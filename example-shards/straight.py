import pysicgl
from pysicgl_utils import Display
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable, OptionVariable


def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)
    timewarp = TimeWarp(lambda: timebase.seconds())
    field = [0.0] * screen.pixels

    state = {
        "scalar_field": None,
    }

    def compute_scalar_field():
        """
        this function is called to recompute the scalar field.
        it must be re-run when a dependency variable changes.
        there is no automatic mechanism to track these dependencies, so it must
        be added to a reponder callback for any of the dependencies.
        """
        variables = layer.variable_manager.variables

        scale = variables["scale"].value
        side = variables["side"].value

        # determine signs depending on the direction option
        if side == "left":
            sx, sy = (1, 0)
        if side == "right":
            sx, sy = (-1, 0)
        if side == "top":
            sx, sy = (0, 1)
        if side == "bottom":
            sx, sy = (0, -1)

        # use the scale and direction signs to compute a scalar field
        for info in display.pixel_info():
            idx, coordinates, position = info
            x, y = position

            field[idx] = scale * (sx * x + sy * y)

        state["scalar_field"] = pysicgl.ScalarField(field)

    # a callback function to handle changes to declared variables
    def handle_variable_changes(variable):
        name = variable.name

        if name == "speed":
            timewarp.set_frequency(variable.value)
        if name == "scale":
            compute_scalar_field()
        if name == "side":
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
        OptionVariable(
            "side",
            "left",
            ("left", "right", "top", "bottom"),
            responders=[responder],
        )
    )
    layer.variable_manager.initialize_variables()

    # compute the initial scalar field (once variables are all declared)
    compute_scalar_field()

    while True:
        yield None

        # apply the scalar field to the canvas mapping against the selected palette
        offset = timewarp.local()
        pysicgl.functional.scalar_field(
            layer.canvas,
            layer.canvas.screen,
            state["scalar_field"],
            layer.palette,
            offset,
        )
