# a simple layer for a solid color
import pysicgl


def frames(layer):
    while True:
        yield None

        pysicgl.functional.interface_fill(layer.canvas, layer.palette[0])
