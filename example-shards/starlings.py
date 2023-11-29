import pysicgl
from hidden_shades import timebase
from pysicgl_utils import Display
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable
from pysicgl_utils import Display
import opensimplex
import math


def gaussian(x):
    return x * math.sin(2 * x / math.pi) / 3.0


class FloatVec2:
    def __init__(self, name, initial_values):
        self._name = name
        self._x = float(initial_values[0])
        self._y = float(initial_values[1])

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = float(value)

    @property
    def y(self):
        return self._y

    @x.setter
    def y(self, value):
        self._y = float(value)

    @property
    def vector(self):
        return (self._x, self._y)


def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)
    (numx, numy) = display.extent
    (maxx, maxy) = display.shape

    # use the TimeWarp class to make an offset from the base time
    # this begins at unity speed (1.0) but will be updated by the
    # declared speed variable
    timewarp = TimeWarp(lambda: timebase.seconds())

    # a callback function to handle changes to declared variables
    def handle_variable_changes(variable):
        name, value = variable.name, variable.value

        if name == "speed":
            timewarp.set_frequency(value)

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    # these are all of the floating point variety but there are a
    # few different choices (Boolean, Integer, Floating, Option,
    # and ColorSequence)
    # note: only the "speed" variable is assinged the responder
    layer.variable_manager.declare_variable(
        FloatingVariable("speed", 0.3, default_range=[0, 1.0], responders=[responder])
    )
    layer.variable_manager.declare_variable(FloatingVariable("offset", 0.0))
    layer.variable_manager.declare_variable(
        FloatingVariable("scaleX", 0.8, default_range=[0, 3])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scaleY", 0.8, default_range=[0, 3])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("centerX", 0.0, default_range=[-0.5, 0.5])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "centerY",
            0.0,
            default_range=[-0.5, 0.5],
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("gaussian_amplitude", 6, default_range=[0, 10])
    )
    layer.variable_manager.declare_variable(FloatingVariable("noise_amplitude", 0.2))
    layer.variable_manager.initialize_variables()

    # prepare a few static variables
    screen = layer.canvas.screen
    display = Display(screen)
    field = [0.0] * screen.pixels

    state = {
        "scalar_field": None,
    }

    while True:
        yield None

        # get variables
        offset = layer.variable_manager.variables["offset"].value
        gaussian_amplitude = layer.variable_manager.variables[
            "gaussian_amplitude"
        ].value
        noise_amplitude = layer.variable_manager.variables["noise_amplitude"].value

        scaleX = layer.variable_manager.variables["scaleX"].value
        scaleY = layer.variable_manager.variables["scaleY"].value
        centerX, centerY = (
            layer.variable_manager.variables["centerX"].value + 0.5,
            layer.variable_manager.variables["centerY"].value + 0.5,
        )
        offset = layer.variable_manager.variables["offset"].value

        # the timewarp uses its internal speed, as well as the speed
        # of the reference time (in this case timebase.local) to
        # compute its own local time
        z = timewarp.local() + offset

        # fill the scalar field with noise
        for info in display.pixel_info():
            idx, coordinates, position = info
            x, y = position
            x, y = x * scaleX, y * scaleY
            z = timewarp.local() + offset
            field[idx] = opensimplex.noise3(x=x * scaleX, y=y * scaleY, z=z)

        # add a gaussian value to the scalar field
        for pixel in display.pixel_info():
            (idx, (u, v), (x, y)) = pixel
            dx, dy = x - centerX, y - centerY
            gx = gaussian(dx)
            gy = gaussian(dy)
            amount = -(gx + gy) * gaussian_amplitude
            field[idx] = field[idx] * noise_amplitude + amount

        # create the scalar field for pysicgl
        state["scalar_field"] = pysicgl.ScalarField(field)

        # apply the scalar field to the canvas mapping against the
        # layer color palette
        pysicgl.functional.scalar_field(
            layer.canvas, layer.canvas.screen, state["scalar_field"], layer.palette
        )
