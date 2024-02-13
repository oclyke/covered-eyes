import pysicgl
import numpy as np

from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable, IntegerVariable


def frames(layer):
    # Required for GPU layers - indicate that the source texture is populated
    # directly by the layer
    layer.use_source = True

    # GPU environment
    window = layer.window
    gpu_environment = layer.gpu_environment
    source_texture_id, source_texture, source_fbo = gpu_environment["source"]

    # use a dictionary to store mutable state
    # this state can be modified as a side effect of other
    # functions in the frame generator
    state = {
        "color_bytes": None,
        "color_sample_points": None,
        "color_texture": None,
    }

    # timewarp controller provides local time
    timewarp = TimeWarp(lambda: timebase.seconds())

    # a callback function to handle changes to declared variables
    def handle_variable_changes(variable):
        name = variable.name
        if name == "speed":
            timewarp.set_frequency(variable.value)
        elif name == "palette_resolution":
            num_colors = variable.value
            if num_colors < 1:
                num_colors = 1

            # Create palette texture and bind it to the fragment shader
            colorbytes = bytearray(num_colors * 4)
            color_texture = window.ctx.texture((num_colors, 1), 4, colorbytes)
            color_texture.use(location=5)
            state["color_bytes"] = colorbytes
            state["color_texture"] = color_texture

            # Create color sample points (to be used on a per-frame basis)
            state["color_sample_points"] = list(
                np.linspace(0, 1, num_colors, endpoint=False)
            )

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    layer.variable_manager.declare_variable(
        FloatingVariable("speed", 0.5, default_range=(0, 1), responders=[responder])
    )
    layer.variable_manager.declare_variable(
        IntegerVariable(
            "palette_resolution", 16, default_range=(1, 32), responders=[responder]
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
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "centerZ", 0.0, default_range=(-578.0, 578.0), responders=[responder]
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scaleX", 1, default_range=(0.0, 3), responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scaleY", 1, default_range=(0.0, 3), responders=[responder])
    )
    layer.variable_manager.initialize_variables()

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

            // CC0 license https://creativecommons.org/share-your-work/public-domain/cc0/

            //////////////////// 3D OpenSimplex2S noise with derivatives  ////////////////////
            //////////////////// Output: vec4(dF/dx, dF/dy, dF/dz, value) ////////////////////

            // Permutation polynomial hash credit Stefan Gustavson
            vec4 permute(vec4 t) {
                return t * (t * 34.0 + 133.0);
            }

            // Gradient set is a normalized expanded rhombic dodecahedron
            vec3 grad(float hash) {
                
                // Random vertex of a cube, +/- 1 each
                vec3 cube = mod(floor(hash / vec3(1.0, 2.0, 4.0)), 2.0) * 2.0 - 1.0;
                
                // Random edge of the three edges connected to that vertex
                // Also a cuboctahedral vertex
                // And corresponds to the face of its dual, the rhombic dodecahedron
                vec3 cuboct = cube;
                cuboct[int(hash / 16.0)] = 0.0;
                
                // In a funky way, pick one of the four points on the rhombic face
                float type = mod(floor(hash / 8.0), 2.0);
                vec3 rhomb = (1.0 - type) * cube + type * (cuboct + cross(cube, cuboct));
                
                // Expand it so that the new edges are the same length
                // as the existing ones
                vec3 grad = cuboct * 1.22474487139 + rhomb;
                
                // To make all gradients the same length, we only need to shorten the
                // second type of vector. We also put in the whole noise scale constant.
                // The compiler should reduce it into the existing floats. I think.
                grad *= (1.0 - 0.042942436724648037 * type) * 3.5946317686139184;
                
                return grad;
            }

            // BCC lattice split up into 2 cube lattices
            vec4 os2NoiseWithDerivativesPart(vec3 X) {
                vec3 b = floor(X);
                vec4 i4 = vec4(X - b, 2.5);
                
                // Pick between each pair of oppposite corners in the cube.
                vec3 v1 = b + floor(dot(i4, vec4(.25)));
                vec3 v2 = b + vec3(1, 0, 0) + vec3(-1, 1, 1) * floor(dot(i4, vec4(-.25, .25, .25, .35)));
                vec3 v3 = b + vec3(0, 1, 0) + vec3(1, -1, 1) * floor(dot(i4, vec4(.25, -.25, .25, .35)));
                vec3 v4 = b + vec3(0, 0, 1) + vec3(1, 1, -1) * floor(dot(i4, vec4(.25, .25, -.25, .35)));
                
                // Gradient hashes for the four vertices in this half-lattice.
                vec4 hashes = permute(mod(vec4(v1.x, v2.x, v3.x, v4.x), 289.0));
                hashes = permute(mod(hashes + vec4(v1.y, v2.y, v3.y, v4.y), 289.0));
                hashes = mod(permute(mod(hashes + vec4(v1.z, v2.z, v3.z, v4.z), 289.0)), 48.0);
                
                // Gradient extrapolations & kernel function
                vec3 d1 = X - v1; vec3 d2 = X - v2; vec3 d3 = X - v3; vec3 d4 = X - v4;
                vec4 a = max(0.75 - vec4(dot(d1, d1), dot(d2, d2), dot(d3, d3), dot(d4, d4)), 0.0);
                vec4 aa = a * a; vec4 aaaa = aa * aa;
                vec3 g1 = grad(hashes.x); vec3 g2 = grad(hashes.y);
                vec3 g3 = grad(hashes.z); vec3 g4 = grad(hashes.w);
                vec4 extrapolations = vec4(dot(d1, g1), dot(d2, g2), dot(d3, g3), dot(d4, g4));
                
                // Derivatives of the noise
                vec3 derivative = -8.0 * mat4x3(d1, d2, d3, d4) * (aa * a * extrapolations)
                    + mat4x3(g1, g2, g3, g4) * aaaa;
                
                // Return it all as a vec4
                return vec4(derivative, dot(aaaa, extrapolations));
            }

            // Rotates domain, but preserve shape. Hides grid better in cardinal slices.
            // Good for texturing 3D objects with lots of flat parts along cardinal planes.
            vec4 os2NoiseWithDerivatives_Fallback(vec3 X) {
                X = dot(X, vec3(2.0/3.0)) - X;
                
                vec4 result = os2NoiseWithDerivativesPart(X) + os2NoiseWithDerivativesPart(X + 144.5);
                
                return vec4(dot(result.xyz, vec3(2.0/3.0)) - result.xyz, result.w);
            }

            // Gives X and Y a triangular alignment, and lets Z move up the main diagonal.
            // Might be good for terrain, or a time varying X/Y plane. Z repeats.
            vec4 os2NoiseWithDerivatives_ImproveXY(vec3 X) {
                
                // Not a skew transform.
                mat3 orthonormalMap = mat3(
                    0.788675134594813, -0.211324865405187, -0.577350269189626,
                    -0.211324865405187, 0.788675134594813, -0.577350269189626,
                    0.577350269189626, 0.577350269189626, 0.577350269189626);
                
                X = orthonormalMap * X;
                vec4 result = os2NoiseWithDerivativesPart(X) + os2NoiseWithDerivativesPart(X + 144.5);
                
                return vec4(result.xyz * orthonormalMap, result.w);
            }

            //////////////////////////////// End noise code ////////////////////////////////

            uniform sampler2D palette;
            uniform float zed;
            uniform vec2 scale;
            uniform vec3 center;

            in vec2 uv;

            out vec4 fragColor;

            void main() {
                // Input point
                vec3 X = vec3(scale * vec2(uv.x - center.x, uv.y - center.y), mod(zed - center.z, 578.0));
                
                // Evaluate noise
                vec4 noiseResult = os2NoiseWithDerivatives_ImproveXY(X);
                
                //// Examples of using the result (either the derivates in xyz or the value in w)
                //vec3 col = (noiseResult.xyz / 5.5) * 0.5 + 0.5;
                //vec3 col = (noiseResult.www) * 0.5 + 0.5;
                //fragColor = vec4(col, 1.0);

                // Output to screen
                fragColor = texture(palette, vec2(noiseResult.w, 0.0));
            }
        """,
    )

    # Create a vertex array object as a render target
    vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0])
    vbo = window.ctx.buffer(vertices.astype("f4"))
    vao = window.ctx.simple_vertex_array(prog, vbo, "in_vert")

    # Bind the palette texture to the fragment shader
    # (the other half of this bind is done in the palette_resolution variable handler)
    prog["palette"].value = 5

    while True:
        yield None

        # fill the color texture from the layer palette
        colors = pysicgl.functional.interpolate_color_sequence(
            layer.palette, state["color_sample_points"]
        )
        for i, c in enumerate(colors):
            state["color_bytes"][i * 4] = (c >> 16) & 0xFF
            state["color_bytes"][i * 4 + 1] = (c >> 8) & 0xFF
            state["color_bytes"][i * 4 + 2] = (c >> 0) & 0xFF
            state["color_bytes"][i * 4 + 3] = (c >> 24) & 0xFF
        state["color_texture"].use(location=5)
        state["color_texture"].write(state["color_bytes"])

        # set the uniforms
        prog["zed"].value = (
            timewarp.local() % 578.0
        )  # OpenGL / ModernGL seems to choke on really big floats so do this modulus here
        prog["center"].value = (
            layer.variable_manager.variables["centerX"].value,
            layer.variable_manager.variables["centerY"].value,
            layer.variable_manager.variables["centerZ"].value,
        )
        prog["scale"].value = (
            layer.variable_manager.variables["scaleX"].value,
            layer.variable_manager.variables["scaleY"].value,
        )

        # use the source texture to render
        source_fbo.use()
        vao.render(window.ctx.TRIANGLE_STRIP)
