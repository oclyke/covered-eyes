import pysicgl
import numpy as np
import opensimplex
from pysicgl_utils import Display
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable, IntegerVariable

def frames(layer):
    NUM_COLORS = 16

    window = layer.window
    gpu_environment = layer.gpu_environment
    prog = window.ctx.program(
        vertex_shader='''
            #version 330

            in vec2 in_vert;
            out vec2 v_text;

            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                v_text = in_vert;
            }
        ''',
        fragment_shader='''
            #version 330

            in vec2 v_text;
            out vec4 f_color;

            uniform sampler2D Texture;
            uniform vec2 Seed;
            uniform int Iter;
            uniform float Zoom;
            uniform float Aspect;
            uniform vec2 Center;

            void main() {
                vec2 c = Seed;
                int i;

                vec2 z = vec2((v_text.x - Center.x) / (Zoom * Aspect), (v_text.y - Center.y) / Zoom);

                for (i = 0; i < Iter; i++) {
                    float x = (z.x * z.x - z.y * z.y) + c.x;
                    float y = (z.y * z.x + z.x * z.y) + c.y;

                    if ((x * x + y * y) > 4.0) {
                        break;
                    }

                    z.x = x;
                    z.y = y;
                }

                f_color = texture(Texture, vec2((i == Iter ? 0.0 : float(i)) / float(Iter), 0.0));
            }
        ''',
    )

    source_texture_id, source_texture, source_fbo = gpu_environment["source"]

    # Create texture and bind it to the fragment shader
    color_sample_points = list(np.linspace(0, 1, NUM_COLORS, endpoint=False))
    colorbytes = bytearray(NUM_COLORS * 4)
    color_texture = window.ctx.texture((NUM_COLORS, 1), 4, colorbytes)
    color_texture.use(location=5)
    prog['Texture'].value = 5

    vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])
    vbo = window.ctx.buffer(vertices.astype('f4'))
    vao = window.ctx.simple_vertex_array(prog, vbo, 'in_vert')

    # declare variables
    # these are all of the floating point variety but there are a
    # few different choices (Boolean, Integer, Floating, Option,
    # and ColorSequence)
    # note: only the "speed" variable is assinged the responder
    layer.variable_manager.declare_variable(
        FloatingVariable("seed_real", -0.8, default_range=(-0.99, -0.01))
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("seed_imaginary", 0.156, default_range=(-0.5, 0.5))
    )
    layer.variable_manager.declare_variable(
        IntegerVariable("iterations", 100, default_range=(50, 200))
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("center_x", 0.0, default_range=(-1, 1))
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("center_y", 0.0, default_range=(-1, 1))
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("zoom", 0.30, default_range=(0.1, 10))
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("aspect_ratio", 1.5, default_range=(0.1, 10))
    )
    layer.variable_manager.initialize_variables()

    # indicate that the source texture should be used
    layer.use_source = True

    while True:
        yield None

        # fill the color texture from the layer palette
        colors = pysicgl.functional.interpolate_color_sequence(layer.palette, color_sample_points)
        for i, c in enumerate(colors):
            colorbytes[i * 4] = (c >> 16) & 0xFF
            colorbytes[i * 4 + 1] =  (c >> 8) & 0xFF
            colorbytes[i * 4 + 2] = (c >> 0) & 0xFF
            colorbytes[i * 4 + 3] = (c >> 24) & 0xFF
        color_texture.use(location=5)
        color_texture.write(colorbytes)

        # get the variable values
        seed_real = layer.variable_manager.variables["seed_real"].value
        seed_imaginary = layer.variable_manager.variables["seed_imaginary"].value
        iterations = layer.variable_manager.variables["iterations"].value
        center_x = layer.variable_manager.variables["center_x"].value
        center_y = layer.variable_manager.variables["center_y"].value
        zoom = layer.variable_manager.variables["zoom"].value
        aspect_ratio = layer.variable_manager.variables["aspect_ratio"].value

        # set the uniforms
        prog['Seed'].value = (seed_real, seed_imaginary)
        prog['Iter'].value = iterations
        prog['Center'].value = (center_x, center_y)
        prog['Zoom'].value = zoom
        prog['Aspect'].value = aspect_ratio

        # use the source texture to render
        source_fbo.clear(1.0, 1.0, 1.0, 1.0)
        source_fbo.use()
        vao.render(window.ctx.TRIANGLE_STRIP)
