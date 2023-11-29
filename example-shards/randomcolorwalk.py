# shows how to use a random color from the color palette
import random
import pysicgl
from hidden_shades.variables.types import FloatingVariable


def frames(layer):
    value = 0.5

    layer.variable_manager.declare_variable(
        FloatingVariable("speed", 0.001, default_range=(0.0, 0.02))
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("randomness", 0.01, default_range=(0.0, 0.08))
    )

    while True:
        yield None

        # get variables
        speed = layer.variable_manager.variables["speed"].value
        randomness_strength = layer.variable_manager.variables["randomness"].value

        # increment value
        value += speed + (randomness_strength * (random.random() - 0.5))

        # fill canvas with interpolated color
        color = pysicgl.functional.interpolate_color_sequence(layer.palette, value)
        pysicgl.functional.interface_fill(layer.canvas, color)
