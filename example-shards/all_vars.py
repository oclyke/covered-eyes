# a shard meant to test all possible variable types
import pysicgl
from hidden_shades.variables.types import (
    BooleanVariable,
    IntegerVariable,
    FloatingVariable,
    OptionVariable,
    ColorSequenceVariable,
    StringVariable,
)


def frames(layer):
    # declare variables
    # these are all of the variable types that are allowed
    layer.variable_manager.declare_variable(BooleanVariable("bool", False))
    layer.variable_manager.declare_variable(
        BooleanVariable("coolBool", True, ("go to school", "do drugs"))
    )
    layer.variable_manager.declare_variable(IntegerVariable("int", 1337, [69, 420]))
    layer.variable_manager.declare_variable(FloatingVariable("float", 0.001))
    layer.variable_manager.declare_variable(
        OptionVariable("option", "option 1", ["option 1", "option 2", "option 3"])
    )
    layer.variable_manager.declare_variable(
        ColorSequenceVariable(
            "color",
            pysicgl.ColorSequence(
                [0xFF0000FF], pysicgl.interpolation.CONTINUOUS_CIRCULAR
            ),
        )
    )
    layer.variable_manager.declare_variable(StringVariable("string", "a frayed knot"))
    layer.variable_manager.initialize_variables()

    while True:
        yield None

        string = layer.variable_manager.variables["string"].value
        color = layer.variable_manager.variables["color"].value
        option = layer.variable_manager.variables["option"].value
        float = layer.variable_manager.variables["float"].value
        integer = layer.variable_manager.variables["int"].value
        boolean = layer.variable_manager.variables["bool"].value
        coolBool = layer.variable_manager.variables["coolBool"].value

        print(
            f"string: {string}, color: {color}, option: {option}, float: {float}, integer: {integer}, boolean: {boolean}, coolBool: {coolBool}"
        )
