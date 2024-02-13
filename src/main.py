import pysicgl
import asyncio
import cache
import socket
import hidden_shades
import stack_manager
import framerate
import gpu
import numpy as np
import profiling
import time
import sys
import os
import traceback
import opensimplex

from drivers.artnet import ArtnetDriver
from drivers.udp import UDPDriver

from moderngl_window import Timer, weakref, logger

from microdot_asyncio import Microdot, Request, Response

# DEBUG = True
DEBUG = False

debug = lambda *args, **kwargs: None
if DEBUG:
    debug = print

# get the absolute location of this file
# this is used to add the persistent directory to the system path
SCRIPT_LOCATION = os.path.abspath(sys.path[0])
COVERED_EYES_ROOT = os.path.dirname(SCRIPT_LOCATION)
sys.path.append(COVERED_EYES_ROOT)

RUNTIME_DIR = f"{COVERED_EYES_ROOT}/runtime"
EPHEMERAL_DIR = f"{RUNTIME_DIR}/ephemeral"
PERSISTENT_DIR = f"{RUNTIME_DIR}/persistent"

# ensure that the directories exist
os.makedirs(RUNTIME_DIR, exist_ok=True)
os.makedirs(EPHEMERAL_DIR, exist_ok=True)
os.makedirs(PERSISTENT_DIR, exist_ok=True)

EXAMPLE_SHARDS_DIR = f"{COVERED_EYES_ROOT}/example-shards"
SHARDS_SOURCE = f"{PERSISTENT_DIR}/shards_source"
if not os.path.exists(f"{SHARDS_SOURCE}"):
    print(
        f"Making a symbolic link to the example shards directory ({EXAMPLE_SHARDS_DIR} <-> {SHARDS_SOURCE})"
    )
    os.symlink(f"{EXAMPLE_SHARDS_DIR}", f"{SHARDS_SOURCE}", target_is_directory=True)

print("Adding the persistent dir to the system path")
print(f"persistent dir: {PERSISTENT_DIR}")
sys.path.append(PERSISTENT_DIR)

print("Loading hardware config")
print(PERSISTENT_DIR)

# load hardware config
hw_config = cache.Cache(
    f"{PERSISTENT_DIR}/hw_config",
    {
        "width": 33,
        "height": 32,
    },
)

print("Seeding opensimplex")
opensimplex.seed(int(time.time()))

drivers = [
    # UDPDriver("0.0.0.0", (6969, 6420)),
    # ArtnetDriver("192.168.4.177"),
]

# audio sources
audio_source_root_path = f"{EPHEMERAL_DIR}/audio/sources"
audio_sources = [
    # UDPAudioSourceMic(
    #     audio_source_root_path, "MicStreamUDP", ("0.0.0.0", "42311"), (48000, 1024)
    # ),
    # UDPAudioSource(
    #     audio_source_root_path, "AudioStreamUDP", ("0.0.0.0", "42310"), (44100, 1024)
    # ),
    # MockAudioSource(audio_source_root_path, "MockAudio", 400, (16000, 256)),
]


# create global managers
artnet_provider = hidden_shades.ArtnetProvider(f"{EPHEMERAL_DIR}/artnet")
audio_manager = hidden_shades.AudioManager(f"{EPHEMERAL_DIR}/audio")
globals = hidden_shades.GlobalsManager(f"{EPHEMERAL_DIR}/globals")


# make pysicgl interfaces
def create_interface(screen):
    mem = pysicgl.allocate_pixel_memory(screen.pixels)
    interface = pysicgl.Interface(screen, mem)
    return (interface, mem)


display = pysicgl.Screen((hw_config.get("width"), hw_config.get("height")))
canvas, canvas_memory = create_interface(display)
accumulator, accumulator_memory = create_interface(display)
output, output_memory = create_interface(display)

aspect_ratio = display.width / display.height
window, timer = gpu.create_window(aspect_ratio=aspect_ratio)
compositor = gpu.Compositor(ctx=window.ctx, aspect_ratio=aspect_ratio)
corrector = gpu.Corrector(ctx=window.ctx, aspect_ratio=aspect_ratio)
gpu_environment = gpu.create_environment(window, (display.width, display.height))

# function to load a given shard uuid and return the module
def load_shard(uuid):
    # Import the top-level package
    package_name = "shards_source"
    submodule_name = f"{uuid}"
    package = __import__(package_name, fromlist=[submodule_name])

    # Access the submodule from the package
    shard = getattr(package, submodule_name)

    print(f"Loaded module: {package}")
    print(f"Loaded shard: {shard}")

    # Return the submodule
    return shard


# a function which sets the shard for a given layer after
# initialization
def layer_post_init_hook(layer):
    uuid = layer.info.get("shard_uuid")
    shard = load_shard(uuid)
    layer.set_shard(shard)
    layer.initialize_frame_generator()


# a function called for each layer in the stack upon creation
# this allows the program to keep the details of loading shards
# separate from the job of the Stack class
def stack_initializer(id, path):
    return hidden_shades.Layer(
        id, path, canvas, globals=globals, window=window, gpu_environment=gpu_environment, post_init_hook=layer_post_init_hook
    )

# define stacks
stack_manager = stack_manager.StackManager(f"{EPHEMERAL_DIR}/stacks", stack_initializer)

frate = framerate.FramerateHistory()

async def run_pipeline():
    """
    This is the main render loop.

    Major Players:
    - stack manager: manages layer stacks
    - active layer stack: the active stack of layers (the other stack can be
        modified and then swapped in)
    - layers: layers represent an atomic step in the generation of the output.
        layers have some metadata as well as a program which generates a frame.
    - compositor: a gpu shader which composes the layers together

    Major Resources:
    - window: a moderngl_window window which contains the moderngl context.
    - canvas: working memory for layers. shared between all layers in the stack
        and cleared between each layer.
    - accumulator: memory for accumulating the output of the layers for every
        frame.
    - output: memory for the final output of the pipeline. separation from the
        other buffers ensures that brightness and gamma correction do not leak
        into the environment of the layers.

    - source_texture: texture allocated for the source of the compositor (more
        or less equivalent to the canvas)
    - destination_texture_ping: texture allocated for the destination of the
        compositor (more or less equivalent to the accumulator) uses ping-pong
        buffering to avoid synchronization issues.
    - destination_texture_pong: texture allocated for the destination of the
        compositor (more or less equivalent to the accumulator) uses ping-pong
        buffering to avoid synchronization issues.
    - framebuffer_texture: (implicit) texture allocated for the window framebuffer.
        (more or less equivalent to the output)

    """

    source_texture_id, source_texture, _ = gpu_environment["source"]
    destination_texture_ping_id, destination_texture_ping_texture, destination_fbo_ping = gpu_environment["destination_ping"]
    destination_texture_pong_id, destination_texture_pong_texture, destination_fbo_pong = gpu_environment["destination_pong"]

    # if ping is true then render to ping, else render to pong
    ping = True

    # make a timer for profiling the framerate
    profiler = profiling.ProfileTimer()

    # rate-limit the output
    output_event = asyncio.Event()

    def current_milli_time():
        return round(time.time() * 1000)

    async def rate_limiter(frequency):
        period_ms = 1000 / frequency

        next_frame_ms = current_milli_time() + period_ms
        while True:
            # wait for next time
            while current_milli_time() < next_frame_ms:
                await asyncio.sleep(0)

            # signal
            output_event.set()
            next_frame_ms += period_ms

    # Start a task to control the output rate
    FRAMERATE = 60
    asyncio.create_task(rate_limiter(FRAMERATE))

    timer.start()

    while not window.is_closing:
        current_time, delta = timer.next_frame()

        # start profiling the frame draw time
        profiler.set()

        # Always bind the window framebuffer before calling render
        window.use()

        # clear the destination textures
        window.clear(0.0, 0.0, 0.0, 1.0)
        destination_fbo_ping.clear(0.0, 0.0, 0.0, 0.0)
        destination_fbo_pong.clear(0.0, 0.0, 0.0, 0.0)

        # loop over all layers in the active stack manager
        layer_idx = 0
        debug("Running layer: ", end="")
        for layer in stack_manager.active:
            debug(f"{layer_idx}", end="")
            layer_idx += 1

            # only compute active layers
            if layer.active:
                debug("*", end="")
                # zero the layer interface for each shard
                # (if a layer wants to use persistent memory it can do whacky stuff
                # such as allocating its own local interface and copying out the results)
                pysicgl.functional.interface_fill(
                    canvas, hidden_shades.globals.ALPHA_TRANSPARENCY_FULL | 0x000000
                )

                # run the layer
                try:
                    layer.run()
                except Exception as e:
                    print(f"Exception in layer {layer.id}: {e}")
                    traceback.print_exc()
                    # layer.set_active(False)

                # compose the source texture onto the destination texture
                if ping == True:
                    ping = False
                    destination_fbo_ping.use()
                else:
                    ping = True
                    destination_fbo_pong.use()
                
                compositor.render(
                    source=source_texture_id,
                    destination=(destination_texture_ping_id if ping else destination_texture_pong_id),
                    mode=layer.composition_mode,
                    brightness=layer.brightness,
                )
            debug(", ", end="")
        
        debug("")

        # apply corrections
        window.ctx.screen.use()
        corrector.render(
            destination=(destination_texture_ping_id if not ping else destination_texture_pong_id),
            # brightness=globals.variable_manager.variables["brightness"].value,
            brightness=1.0,
        )

        # output the display data to the window
        if not window.is_closing:
            # texture.write(output_memory)
            window.swap_buffers()

        # output the framebuffer data to the drivers
        data = window.ctx.screen.read(viewport=(0, 0, display.width, display.height))
        for driver in drivers:
            driver.push(data)

        # compute framerate
        profiler.mark()
        frate.record_period_ms(profiler.period_ms)

        # wait for the next output opportunity
        await output_event.wait()
        output_event.clear()

    _, duration = timer.stop()
    window.destroy()
    if duration > 0:
        logger.info(
            "Duration: {0:.2f}s @ {1:.2f} FPS".format(
                duration, window.frames / duration
            )
        )
    
    loop = asyncio.get_running_loop()
    loop.stop()


async def serve_api():
    from api import api_app, init_api_app, api_version

    # initialize the api app
    init_api_app(
        stack_manager,
        canvas,
        layer_post_init_hook,
        shards_source_dir=SHARDS_SOURCE,
        globals=globals,
        window=window,
        gpu_environment=gpu_environment,
    )

    # set up server
    PORT = 1337

    # configure maximum request size
    Request.max_content_length = 128 * 1024  # 128 KB
    Response.default_content_type = "application/json"

    # create application structure
    app = Microdot()
    app.mount(api_app, url_prefix="/api/v0")

    @app.get("/alive")
    async def get_alive(request):
        return None

    @app.get("/index")
    async def get_index(request):
        return {
            "hw_version": hardware.hw_version.to_string(),
            "api_version": api_version.to_string(),
            "api": {
                "latest": "v0",
                "versions": {
                    "v0": "/api/v0",
                },
            },
        }

    # serve the api
    asyncio.create_task(app.start_server(debug=True, port=PORT))


async def control_visualizer():
    # information about visualizer control server
    CONTROL_HOST = "0.0.0.0"
    CONTROL_PORT = 6969

    # format the control message which indicates the screen resolution
    config_message = f"{display.width} {display.height}\n"

    while True:
        try:
            # open a connection to the control server in the visualizer
            control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            control.connect(socket.getaddrinfo(CONTROL_HOST, CONTROL_PORT)[0][-1])
            control.send(config_message.encode("utf-8"))
            control.close()
        except:
            pass
        await asyncio.sleep(5.0)


async def blink():
    while True:
        await asyncio.sleep(5)
        print(f"{frate.average()} fps, ({len(stack_manager.active)} layers)")


async def main():
    # create async tasks
    asyncio.create_task(run_pipeline())
    asyncio.create_task(control_visualizer())
    asyncio.create_task(serve_api())
    asyncio.create_task(blink())
    asyncio.create_task(artnet_provider.run())

    # start audio sources
    for source in audio_sources:
        print("Initializing audio source: ", source)
        audio_manager.add_source(source)
        asyncio.create_task(source.run())

    # initialize the audio manager once all audio sources have been registered
    audio_manager.initialize()

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
