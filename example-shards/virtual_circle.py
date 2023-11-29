import pysicgl
from pysicgl_utils import Display
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable
import math
import random


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
    (maxx, maxy) = display.shape
    field = [0.0] * screen.pixels

    state = {
        "scalar_field": None,
    }

    location = [0.5, 0.5]
    dirvec = [1, 1]

    def compute_scalar_field():
        """
        this function is called to recompute the scalar field.
        it must be re-run when a dependency variable changes.
        there is no automatic mechanism to track these dependencies, so it must
        be added to a reponder callback for any of the dependencies.
        """
        variables = layer.variable_manager.variables

        diameter = variables["diameter"].value
        lx, ly = (location[0], location[1])

        # use the scale and direction signs to compute a scalar field
        for info in display.pixel_info():
            idx, coordinates, position = info
            x, y = position

            r = math.sqrt(math.pow(x - lx, 2) + math.pow(y - ly, 2))

            dist = abs(r - diameter)
            if dist < 0.1:
                field[idx] = dist * 10
            elif r < diameter:
                field[idx] = float(1)
            else:
                field[idx] = float(0)

        state["scalar_field"] = pysicgl.ScalarField(field)

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
        compute_scalar_field()

    # a callback function to handle changes to declared variables
    def handle_variable_changes(variable):
        name = variable.name

        if name == "speed":
            timewarp.set_frequency(variable.value)

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "speed", 0.02, default_range=(0, 0.15), responders=[responder]
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
            0.15,
            default_range=(0, 0.5),
            allowed_range=(0, 0.5),
        )
    )
    layer.variable_manager.initialize_variables()

    # compute the initial scalar field (once variables are all declared)
    compute_scalar_field()

    while True:
        yield None

        # run the animation
        advance()

        # apply the scalar field to the canvas by mapping against the layer palette
        offset = timewarp.local()
        pysicgl.functional.scalar_field(
            layer.canvas, layer.canvas.screen, state["scalar_field"], layer.palette
        )
