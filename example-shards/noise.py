import pysicgl
import numpy
import opensimplex
from pysicgl_utils import Display
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable


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
    # prepare a few static variables
    screen = layer.canvas.screen
    display = Display(screen)
    field = [0.0] * screen.pixels
    print(len(field))

    # use the TimeWarp class to make an offset from the base time
    # this begins at unity speed (1.0) but will be updated by the
    # declared speed variable
    timewarp = TimeWarp(lambda: timebase.seconds())

    # declare some 2-element floating point vectors.
    # the values here are used as the default values for declared variables
    # but will be reset by the stored value when the
    # layer_manager.initialize_variables() method is called.
    offset = 0.0

    state = {
        "scalar_field": None,
        "xs": None,
        "ys": None,
        "zs": None,
    }

    def update_sample_arrays():
        scaleX = layer.variable_manager.variables["scaleX"].value
        scaleY = layer.variable_manager.variables["scaleY"].value

        (nx, ny) = display.extent

        xs = numpy.linspace(0, scaleX, num=nx)
        ys = numpy.linspace(0, scaleY, num=ny)

        state["xs"] = xs
        state["ys"] = ys

    def fill_scalar_field():
        offset = layer.variable_manager.variables["offset"].value
        z = timewarp.local() + offset
        zs = numpy.linspace(z, z, num=1)
        out = opensimplex.noise3array(state["xs"], state["ys"], zs)

        # print(out.size)

        # This loop is evidence of the need for pysicgl to support
        # numpy arrays in the constructor for ScalarField objects
        (nx, ny) = display.extent
        for idx in range(nx):
            for idy in range(ny):
                field[idx + idy * nx] = float(out[0][idy][idx])

        state["scalar_field"] = pysicgl.ScalarField(field)

    # a callback function to handle changes to declared variables
    def handle_variable_changes(variable):
        name, value = variable.name, variable.value

        if name == "speed":
            timewarp.set_frequency(value)
        if (
            name == "scaleX"
            or name == "scaleY"
            or name == "centerX"
            or name == "centerY"
        ):
            update_sample_arrays()
            fill_scalar_field()

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    # these are all of the floating point variety but there are a
    # few different choices (Boolean, Integer, Floating, Option,
    # and ColorSequence)
    # note: only the "speed" variable is assinged the responder
    layer.variable_manager.declare_variable(
        FloatingVariable("speed", 0.5, default_range=(0.0, 1), responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("offset", offset, responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scaleX", 1, default_range=(0.0, 3), responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scaleY", 1, default_range=(0.0, 3), responders=[responder])
    )
    layer.variable_manager.initialize_variables()

    while True:
        yield None
        # fill the scalar field with noise
        fill_scalar_field()

        # apply the scalar field to the canvas mapping against the
        # layer color palette
        pysicgl.functional.scalar_field(
            layer.canvas, layer.canvas.screen, state["scalar_field"], layer.palette
        )
