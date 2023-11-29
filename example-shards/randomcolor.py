# shows how to use a random color from the color palette
import random
import pysicgl


def frames(layer):
    while True:
        yield None

        random_number = random.random()
        random_palette_color = pysicgl.functional.interpolate_color_sequence(
            layer.palette, random_number
        )
        pysicgl.functional.interface_fill(layer.canvas, random_palette_color)
