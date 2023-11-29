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

        pysicgl.functional.interface_circle(
            layer.canvas,
            hidden_shades.globals.ALPHA_TRANSPARENCY_HALF | 0x00AFAFAF,
            (int(numx / 2), int(numy / 2)),
            int(numx / 2),
        )
