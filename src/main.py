import pysicgl
import asyncio
import cache
import socket
import hidden_shades
import stack_manager
import framerate
import logging
import profiling
import time
import sys
import os

from drivers.artnet import ArtnetDriver
from drivers.udp import UDPDriver

from microdot_asyncio import Microdot, Request, Response

ALPHA_TRANSPARENCY_NONE = 0x00000000
ALPHA_TRANSPARENCY_HALF = 0x40000000
ALPHA_TRANSPARENCY_FULL = 0x7F000000

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
  print(f"Making a symbolic link to the example shards directory ({EXAMPLE_SHARDS_DIR} <-> {SHARDS_SOURCE})")
  os.symlink(f"{EXAMPLE_SHARDS_DIR}", f"{SHARDS_SOURCE}", target_is_directory=True)

print("Adding the persistent dir to the system path")
print(f"persistent dir: {PERSISTENT_DIR}")
sys.path.append(PERSISTENT_DIR)

logger = logging.Manager(f"{PERSISTENT_DIR}/logs")

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


drivers = [
    UDPDriver("0.0.0.0", (6969, 6420)),
    ArtnetDriver("192.168.4.177"),
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
visualizer, visualizer_memory = create_interface(display)
corrected, corrected_memory = create_interface(display)
canvas, canvas_memory = create_interface(display)

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
    return hidden_shades.Layer(id, path, canvas, globals=globals, post_init_hook=layer_post_init_hook)


# define stacks
stack_manager = stack_manager.StackManager(f"{EPHEMERAL_DIR}/stacks", stack_initializer)


frate = framerate.FramerateHistory()


async def run_pipeline():
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

    FRAMERATE = 30
    asyncio.create_task(rate_limiter(FRAMERATE))

    # handle layers
    while True:
        profiler.set()

        # zero the visualizer to prevent artifacts from previous render loops
        # from leaking through
        pysicgl.functional.interface_fill(visualizer, ALPHA_TRANSPARENCY_FULL | 0x000000)

        # loop over all layers in the active stack manager
        for layer in stack_manager.active:
            # only compute active layers
            if layer.active:
                # zero the layer interface for each shard
                # (if a layer wants to use persistent memory it can do whacky stuff
                # such as allocating its own local interface and copying out the results)
                pysicgl.functional.interface_fill(canvas, ALPHA_TRANSPARENCY_FULL | 0x000000)

                # run the layer
                try:
                    layer.run()
                except Exception as e:
                    logger.log_exception(e)
                    layer.set_active(False)

                # compose the canvas memory onto the visualizer memory
                pysicgl.functional.compose(visualizer, display, layer.canvas.memory, layer.compositor)

        # gamma correct the canvas
        pysicgl.functional.gamma_correct(visualizer, corrected)

        # apply global brightness
        pysicgl.functional.scale(corrected, globals.variable_manager.variables["brightness"].value)

        # output the display data
        for driver in drivers:
            driver.push(corrected)

        # compute framerate
        profiler.mark()
        frate.record_period_ms(profiler.period_ms)

        # wait for the next output opportunity
        await output_event.wait()
        output_event.clear()

async def serve_api():
    from api import api_app, init_api_app, api_version

    # initialize the api app
    init_api_app(
        stack_manager,
        canvas,
        layer_post_init_hook,
        persistent_dir=PERSISTENT_DIR,
        globals=globals,
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
