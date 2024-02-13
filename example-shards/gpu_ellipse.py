import pysicgl
import numpy as np
from pysicgl_utils import Display
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable, OptionVariable


def frames(layer):
    # Required for GPU layers - indicate that the source texture is populated
    # directly by the layer
    layer.use_source = True

    # Define the size of the color palette texture
    NUM_COLORS = 16

    timewarp = TimeWarp(lambda: timebase.seconds())

    # GPU environment
    window = layer.window
    gpu_environment = layer.gpu_environment
    source_texture_id, source_texture, source_fbo = gpu_environment["source"]

    # Create the shader program
    prog = window.ctx.program(
        vertex_shader="""
            #version 330 core

            in vec2 in_vert;
            out vec2 uv;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_vert * 0.5 + 0.5;
            }
        """,
        fragment_shader="""
            #version 330 core

            in vec2 uv;
            out vec4 f_color;

            uniform sampler2D palette;
            uniform float scale;
            uniform float offset;
            uniform vec2 center;
            uniform float eccentricity;

            void main() {
            
                float one_minus_e_squared = 1 - pow(eccentricity, 2.0);
                float one_minus_e_squared_squared = pow(one_minus_e_squared, 2.0);
                float one_over_one_minus_e_squared_squared = 1.0 / one_minus_e_squared_squared;

                float efx = 1.0;
                float efy = 1.0;
                if (eccentricity < 0.0) {
                    efx = one_over_one_minus_e_squared_squared;
                } else {
                    efy = one_over_one_minus_e_squared_squared;
                }
                float sample_location = scale * sqrt(
                    pow(uv.x - center.x - 0.5, 2.0) * efx + pow(uv.y - center.y - 0.5, 2.0) * efy
                ) + offset;

                f_color = texture(palette, vec2(sample_location, 0.0));
            }
        """,
    )

    # Create palette texture and bind it to the fragment shader
    color_sample_points = list(np.linspace(0, 1, NUM_COLORS, endpoint=False))
    colorbytes = bytearray(NUM_COLORS * 4)
    color_texture = window.ctx.texture((NUM_COLORS, 1), 4, colorbytes)
    color_texture.use(location=5)
    prog["palette"].value = 5

    # Create a vertex array object as a render target
    vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])
    vbo = window.ctx.buffer(vertices.astype("f4"))
    vao = window.ctx.simple_vertex_array(prog, vbo, "in_vert")

    # a callback function to handle changes to declared variables
    def handle_variable_changes(variable):
        name = variable.name
        if name == "speed":
            timewarp.set_frequency(variable.value)

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    layer.variable_manager.declare_variable(
        FloatingVariable("speed", 0.5, default_range=(0, 1), responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scale", 1.0, responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "eccentricity",
            0.0,
            default_range=(-0.99, 0.99),
            allowed_range=(-0.99, 0.99),
            responders=[responder],
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "centerX", 0.0, default_range=(-0.5, 0.5), responders=[responder]
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "centerY", 0.0, default_range=(-0.5, 0.5), responders=[responder]
        )
    )
    layer.variable_manager.initialize_variables()

    while True:
        yield None

        # fill the color texture from the layer palette
        colors = pysicgl.functional.interpolate_color_sequence(
            layer.palette, color_sample_points
        )
        for i, c in enumerate(colors):
            colorbytes[i * 4] = (c >> 16) & 0xFF
            colorbytes[i * 4 + 1] = (c >> 8) & 0xFF
            colorbytes[i * 4 + 2] = (c >> 0) & 0xFF
            colorbytes[i * 4 + 3] = (c >> 24) & 0xFF
        color_texture.use(location=5)
        color_texture.write(colorbytes)

        # set the uniforms
        prog["center"].value = (
            layer.variable_manager.variables["centerX"].value,
            layer.variable_manager.variables["centerY"].value,
        )
        prog["scale"].value = layer.variable_manager.variables["scale"].value
        prog["offset"].value = timewarp.local() % 1.0
        prog["eccentricity"].value = layer.variable_manager.variables[
            "eccentricity"
        ].value

        # use the source texture to render
        source_fbo.use()
        vao.render(window.ctx.TRIANGLE_STRIP)
