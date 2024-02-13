import numpy as np
import moderngl

COMPOSITOR_ALPHA_CLEAR = 0
COMPOSITOR_ALPHA_COPY = 1
COMPOSITOR_ALPHA_SOURCE = 2
COMPOSITOR_ALPHA_DESTINATION = 3
COMPOSITOR_ALPHA_SOURCE_OVER = 4
COMPOSITOR_ALPHA_DESTINATION_OVER = 5
COMPOSITOR_ALPHA_SOURCE_IN = 6
COMPOSITOR_ALPHA_DESTINATION_IN = 7
COMPOSITOR_ALPHA_SOURCE_OUT = 8
COMPOSITOR_ALPHA_DESTINATION_OUT = 9
COMPOSITOR_ALPHA_SOURCE_ATOP = 10
COMPOSITOR_ALPHA_DESTINATION_ATOP = 11
COMPOSITOR_ALPHA_XOR = 12
COMPOSITOR_ALPHA_PLUS_LIGHTER = 13
COMPOSITOR_ALPHA_PLUS_DARKER = 14

modes = {
    "alpha_clear": COMPOSITOR_ALPHA_CLEAR,
    "alpha_copy": COMPOSITOR_ALPHA_COPY,
    "alpha_source": COMPOSITOR_ALPHA_SOURCE,
    "alpha_destination": COMPOSITOR_ALPHA_DESTINATION,
    "alpha_source_over": COMPOSITOR_ALPHA_SOURCE_OVER,
    "alpha_destination_over": COMPOSITOR_ALPHA_DESTINATION_OVER,
    "alpha_source_in": COMPOSITOR_ALPHA_SOURCE_IN,
    "alpha_destination_in": COMPOSITOR_ALPHA_DESTINATION_IN,
    "alpha_source_out": COMPOSITOR_ALPHA_SOURCE_OUT,
    "alpha_destination_out": COMPOSITOR_ALPHA_DESTINATION_OUT,
    "alpha_source_atop": COMPOSITOR_ALPHA_SOURCE_ATOP,
    "alpha_destination_atop": COMPOSITOR_ALPHA_DESTINATION_ATOP,
    "alpha_xor": COMPOSITOR_ALPHA_XOR,
    "alpha_plus_lighter": COMPOSITOR_ALPHA_PLUS_LIGHTER,
    "alpha_plus_darker": COMPOSITOR_ALPHA_PLUS_DARKER,
}


class Compositor:
    def __init__(self, ctx, aspect_ratio=1.0):
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
            uniform int composition_mode;
            in vec2 uv;
            uniform sampler2D Source;
            uniform sampler2D Destination;
            uniform float brightness;
            out vec4 fragColor;
            void main() {
                vec4 srcColor = texture(Source, uv);
                vec4 scaledSourceColor = vec4(srcColor.rgb * brightness, srcColor.a);
                switch (composition_mode) {
                    case -1: {
                        // debugging
                        fragColor = vec4(0.0, 1.0, 1.0, 1.0);
                    }
                    case 0: {
                        // alpha clear
                        fragColor = vec4(0.0, 0.0, 0.0, 0.0);
                        break;
                    }
                    case 1: {
                        // alpha copy
                        fragColor = scaledSourceColor;
                        break;
                    }
                    case 2: {
                        // alpha source
                        fragColor = scaledSourceColor;
                        break;
                    }
                    case 3: {
                        // alpha destination
                        fragColor = texture(Destination, uv);
                        break;
                    }
                    case 4: {
                        // alpha source over
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = srcColor + dstColor * (1.0 - srcColor.a);
                        break;
                    }
                    case 5: {
                        // alpha destination over
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = dstColor + srcColor * (1.0 - dstColor.a);
                        break;
                    }
                    case 6: {
                        // alpha source in
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = srcColor * dstColor.a;
                        break;
                    }
                    case 7: {
                        // alpha destination in
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = dstColor * srcColor.a;
                        break;
                    }
                    case 8: {
                        // alpha source out
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = srcColor * (1.0 - dstColor.a);
                        break;
                    }
                    case 9: {
                        // alpha destination out
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = dstColor * (1.0 - srcColor.a);
                        break;
                    }
                    case 10: {
                        // alpha source atop
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = srcColor * dstColor.a + dstColor * (1.0 - srcColor.a);
                        break;
                    }
                    case 11: {
                        // alpha destination atop
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = dstColor * srcColor.a + srcColor * (1.0 - dstColor.a);
                        break;
                    }
                    case 12: {
                        // alpha xor
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = srcColor * (1.0 - dstColor.a) + dstColor * (1.0 - srcColor.a);
                        break;
                    }
                    case 13: {
                        // alpha plus lighter
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = min(srcColor + dstColor, vec4(1.0));
                        break;
                    }
                    case 14: {
                        // alpha plus darker
                        vec4 srcColor = scaledSourceColor;
                        vec4 dstColor = texture(Destination, uv);
                        fragColor = max(srcColor + dstColor - vec4(1.0), vec4(0.0));
                        break;
                    }
                    default: {
                        fragColor = vec4(0.0, 0.0, 1.0, 1.0);
                        break;
                    }
                }
            }
        """

        self._ctx = ctx
        self._program = self._ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )

        # Compute the vertices of a rectangle with the given aspect ratio
        # (width / height) and a maximum dimension of 2.0 (the rectangle
        # is centered at the origin). Accounting for the aspect ratio here
        # keeps the shader code static.

        # if aspect_ratio > 1.0:
        #     vertices = np.array([
        #         -1.0, -1.0 / aspect_ratio,
        #          1.0, -1.0 / aspect_ratio,
        #         -1.0,  1.0 / aspect_ratio,
        #          1.0,  1.0 / aspect_ratio,
        #     ], dtype='f4')
        # else:
        #     vertices = np.array([
        #         -1.0 * aspect_ratio, -1.0,
        #          1.0 * aspect_ratio, -1.0,
        #         -1.0 * aspect_ratio,  1.0,
        #          1.0 * aspect_ratio,  1.0,
        #     ], dtype='f4')

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

    def render(self, source, destination, mode, brightness):
        self._program["Source"].value = source
        self._program["Destination"].value = destination
        self._program["composition_mode"].value = mode
        self._program["brightness"].value = brightness
        self._vao.render(moderngl.TRIANGLE_STRIP)

        # print(self._program['composition_mode'].value)
        # print(self._program['Source'].value)
        # print(self._program['Destination'].value)
