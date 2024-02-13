import pysicgl
import numpy as np


def frames(layer):
    # Required for GPU layers - indicate that the source texture is populated
    # directly by the layer
    layer.use_source = True

    # GPU environment
    window = layer.window
    gpu_environment = layer.gpu_environment
    source_texture_id, source_texture, source_fbo = gpu_environment["source"]

    # Create the shader program
    prog = window.ctx.program(
        vertex_shader="""
            #version 330 core

            in vec2 in_vert;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        """,
        fragment_shader="""
            #version 330 core

            out vec4 f_color;
            void main() {
                f_color = color;
            }
        """,
    )

    # Create a vertex array object as a render target
    vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])
    vbo = window.ctx.buffer(vertices.astype("f4"))
    vao = window.ctx.simple_vertex_array(prog, vbo, "in_vert")

    while True:
        yield None

        # fill the color texture from the layer palette
        color = pysicgl.functional.interpolate_color_sequence(layer.palette, 0)

        # set the uniforms
        prog["color"].value = (
            (color >> 16) & 0xFF,
            (color >> 8) & 0xFF,
            (color >> 0) & 0xFF,
            (color >> 24) & 0xFF,
        )

        # use the source texture to render
        source_fbo.use()
        vao.render(window.ctx.TRIANGLE_STRIP)
