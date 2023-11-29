# demonstration of dynamic secondary color palette usage
import pysicgl
from hidden_shades import timebase
from pysicgl_utils import Display
from hidden_shades.frequency import FreqCounter
from hidden_shades.variables.types import ColorSequenceVariable, FloatingVariable
import random
import math


def magnitude(vector):
    squares = map(lambda element: math.pow(element, 2), vector)
    return math.sqrt(sum(squares))


def direction(vector):
    mag = magnitude(vector)
    return tuple(map(lambda element: element / mag, vector))


def vector_add(*vectors):
    dims = len(vectors[0])
    return tuple(map(lambda i: sum(tuple(vec[i] for vec in vectors)), range(dims)))


def vector_scale(vector, scalar):
    return tuple(map(lambda element: element * scalar, vector))


def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)
    (numx, numy) = display.extent
    (maxx, maxy) = display.shape

    diameter = numx // 2
    location = [0.5, 0.5]
    dirvec = [1, 1]

    def add_wobble():
        # adds a little noise into the direction vector
        wobble = layer.variable_manager.variables["wobble"].value
        delta = vector_scale(direction([random.random(), random.random()]), wobble)

        dirvec[0] += delta[0]
        dirvec[1] += delta[1]

    def check_bounds():
        diameter = layer.variable_manager.variables["diameter"].value
        radius = diameter / 2

        bounced = False
        if (location[0] - radius) < 0:
            dirvec[0] = 1
            bounced = True
        if (location[0] + radius) > maxx:
            dirvec[0] = -1
            bounced = True

        if (location[1] - radius) < 0:
            dirvec[1] = 1
            bounced = True
        if (location[1] + radius) > maxy:
            dirvec[1] = -1
            bounced = True

        if bounced:
            add_wobble()

    def advance():
        speed = layer.variable_manager.variables["speed"].value

        new_location = vector_add(location, vector_scale(direction(dirvec), speed))
        location[0] = new_location[0]
        location[1] = new_location[1]

        check_bounds()

    def get_location_coordinates():
        return (int(location[0] * (numx)), int(location[1] * (numy)))

    layer.variable_manager.declare_variable(
        FloatingVariable(
            "speed",
            0.01,
            default_range=(0, 0.05),
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "wobble",
            0.1,
            default_range=(0, 0.5),
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "diameter",
            0.1,
            default_range=(0, 1.0),
        )
    )
    layer.variable_manager.declare_variable(
        ColorSequenceVariable(
            "ball_color",
            pysicgl.ColorSequence(
                [0xFF0000FF], pysicgl.interpolation.CONTINUOUS_CIRCULAR
            ),
        )
    )
    layer.variable_manager.initialize_variables()

    # the advance counter is used to control the number of animation steps performed during each frame
    # the speed of the animation will be controlled the timewarp
    advance_counter = FreqCounter(1.0)

    # reset the advance counter
    advance_counter.reset(timebase.seconds())

    while True:
        yield None

        # run the animation
        advance()

        # fill background color
        pysicgl.functional.interface_fill(layer.canvas, layer.palette[0])

        # draw the ball
        ball_color = layer.variable_manager.variables["ball_color"].value
        diameter = layer.variable_manager.variables["diameter"].value
        pysicgl.functional.interface_circle(
            layer.canvas,
            ball_color[0],
            get_location_coordinates(),
            int(diameter * numx),
        )
