import numpy as np
import moderngl

from .window import create_window
from .composition import Compositor


def create_environment(window, size):
    width, height = size

    # Source
    # This texture is generally used by layers to render their content
    source_texture_id = 3
    source_texture = window.ctx.texture((width, height), 4)
    source_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
    source_texture.repeat_x = False
    source_texture.repeat_y = False
    source_texture.use(location=source_texture_id)
    source_fbo = window.ctx.framebuffer(source_texture)

    # Destination
    # Used by the compositor to accumulate the final output
    # (ping and pong are used to avoid feedback loops in openGL)
    destination_texture_ping_id = 2
    destination_texture_ping = window.ctx.texture((width, height), 4)
    destination_texture_ping.filter = (moderngl.NEAREST, moderngl.NEAREST)
    destination_texture_ping.repeat_x = False
    destination_texture_ping.repeat_y = False
    destination_texture_ping.use(location=destination_texture_ping_id)
    destination_fbo_ping = window.ctx.framebuffer(destination_texture_ping)

    destination_texture_pong_id = 1
    destination_texture_pong = window.ctx.texture((width, height), 4)
    destination_texture_pong.filter = (moderngl.NEAREST, moderngl.NEAREST)
    destination_texture_pong.repeat_x = False
    destination_texture_pong.repeat_y = False
    destination_texture_pong.use(location=destination_texture_pong_id)
    destination_fbo_pong = window.ctx.framebuffer(destination_texture_pong)

    # # Framebuffer
    # framebuffer_texture_id = 0
    # framebuffer_texture = window.ctx.texture((width, height), 4)
    # framebuffer_texture.repeat_x = False
    # framebuffer_texture.repeat_y = False
    # framebuffer_texture.use(location=framebuffer_texture_id)

    # The environment
    return {
        "source": (source_texture_id, source_texture, source_fbo),
        "destination_ping": (
            destination_texture_ping_id,
            destination_texture_ping,
            destination_fbo_ping,
        ),
        "destination_pong": (
            destination_texture_pong_id,
            destination_texture_pong,
            destination_fbo_pong,
        ),
        # "framebuffer": (framebuffer_texture_id, framebuffer_texture, None),
    }


class Corrector:
    def __init__(self, ctx, aspect_ratio):
        self.ctx = ctx

        vertex_shader = """
            #version 330 core
            in vec2 in_vert;
            out vec2 uv;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                uv = in_vert * 0.5 + 0.5;
            }
        """
        fragment_shader = """
            #version 330 core
            uniform sampler2D Destination;
            uniform float brightness;
            in vec2 uv;
            out vec4 fragColor;            
            void main() {
                float gamma = 2.2;
                vec4 destinationColor = texture(Destination, uv);

                // Apply brightness adjustment
                destinationColor.rgb *= brightness;

                // Perform gamma correction
                destinationColor.r = pow(destinationColor.r, 1.0 / gamma);
                destinationColor.g = pow(destinationColor.g, 1.0 / gamma);
                destinationColor.b = pow(destinationColor.b, 1.0 / gamma);

                // Output the final color
                fragColor = destinationColor;

                // debugging
                fragColor = texture(Destination, uv);
            }
        """

        self._ctx = ctx
        self._program = self._ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )

        vertices = np.array(
            [
                -1.0,
                -1.0,
                1.0,
                -1.0,
                -1.0,
                1.0,
                1.0,
                1.0,
            ],
            dtype="f4",
        )
        vbo = self._ctx.buffer(vertices)
        self._vao = self._ctx.simple_vertex_array(self._program, vbo, "in_vert")

    def render(self, destination, brightness=1.0):
        self._program["Destination"] = destination
        self._program["brightness"] = brightness
        self._vao.render(moderngl.TRIANGLE_STRIP)
