import pysicgl
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
    screen = layer.canvas.screen
    display = Display(screen)
    timewarp = TimeWarp(lambda: timebase.seconds())
    field = [0.0] * screen.pixels

    # use a dictionary to store mutable state
    # this state can be modified as a side effect of other
    # functions in the frame generator
    state = {
        "scalar_field": None,
    }

    # some simple 2-element float vectors
    # values specified here are used as defaults

    center = FloatVec2("center", (0.0, 0.0))

    def compute_scalar_field():
        """
        this function is called to recompute the scalar field.
        it must be re-run when a dependency variable changes.
        there is no automatic mechanism to track these dependencies, so it must
        be added to a reponder callback for any of the dependencies.
        """
        variables = layer.variable_manager.variables

        (cx, cy) = display.center
        scale = variables["scale"].value
        eccentricity = variables["eccentricity"].value
        (ox, oy) = (variables["centerX"].value, variables["centerY"].value)

        # we use a signed eccentricity to indicate the direction of the major axis
        # when eccentricity > 0 the major axis is x
        # when eccentricity < 0 the major axis is y
        # in either case the absolute value of the supplied variable is used to scale
        # the major axis (for symmetry... )
        one_over_one_minus_e = 1 / (1 - abs(eccentricity))
        efx, efy = (1, 1)
        if eccentricity < 0:
            efx = one_over_one_minus_e
        if eccentricity > 0:
            efy = one_over_one_minus_e

        # use the scale and direction signs to compute a scalar field
        for info in display.pixel_info():
            idx, coordinates, position = info
            x, y = position

            field[idx] = scale * (efx * abs(x - cx - ox) + efy * abs(y - cy - oy))

        state["scalar_field"] = pysicgl.ScalarField(field)  # return the scalar field

    # a callback function to handle changes to declared variables
    def handle_variable_changes(variable):
        name = variable.name

        if name == "speed":
            timewarp.set_frequency(variable.value)
        if name == "scale":
            compute_scalar_field()
        if name == "eccentricity":
            compute_scalar_field()
        if name == "centerX":
            compute_scalar_field()
        if name == "centerY":
            compute_scalar_field()

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    layer.variable_manager.declare_variable(
        FloatingVariable("speed", 0.5, default_range=(0, 1), responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scale", 1.0, responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "eccentricity",
            0.0,
            default_range=(-0.99, 0.99),
            allowed_range=(-0.99, 0.99),
            responders=[responder],
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "centerX", center.x, default_range=(-0.5, 0.5), responders=[responder]
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "centerY", center.y, default_range=(-0.5, 0.5), responders=[responder]
        )
    )
    layer.variable_manager.initialize_variables()

    # compute the initial scalar field (once variables are all declared)
    compute_scalar_field()

    while True:
        yield None

        # apply the scalar field to the canvas by mapping against the layer palette
        offset = timewarp.local()
        pysicgl.functional.scalar_field(
            layer.canvas,
            layer.canvas.screen,
            state["scalar_field"],
            layer.palette,
            offset,
        )
