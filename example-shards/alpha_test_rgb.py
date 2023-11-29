from pysicgl_utils import Display
import pysicgl
import hidden_shades


def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)
    (numx, numy) = display.extent
    (maxx, maxy) = display.shape

    while True:
        yield None

        for idx in range(int(numx / 3)):
            pysicgl.functional.interface_line(
                layer.canvas,
                hidden_shades.globals.ALPHA_TRANSPARENCY_FULL | 0xFF0000,
                (idx, 0),
                (idx, numy),
            )

        for idx in range(int(numx / 3)):
            pysicgl.functional.interface_line(
                layer.canvas,
                hidden_shades.globals.ALPHA_TRANSPARENCY_HALF | 0x00FF00,
                (idx + int(numx / 3), 0),
                (idx + int(numx / 3), numy),
            )

        for idx in range(int(numx / 3)):
            pysicgl.functional.interface_line(
                layer.canvas,
                hidden_shades.globals.ALPHA_TRANSPARENCY_NONE | 0x0000FF,
                (idx + int(2 * numx / 3), 0),
                (idx + int(2 * numx / 3), numy),
            )
