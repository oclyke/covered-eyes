from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_COLOR_SEQUENCE
import pysicgl
import json


class ColorSequenceVariable(VariableDeclaration):
    def __init__(self, name, default, **kwargs):
        super().__init__(
            TYPECODE_COLOR_SEQUENCE, pysicgl.ColorSequence, name, default, **kwargs
        )

    def validate(self, value):
        if type(value) is not pysicgl.ColorSequence:
            return False
        if value.interpolator not in pysicgl.interpolation.__dict__.values():
            return False
        return True

    def serialize(self, value):
        colors = []
        interpolator_name = ""
        for color in value:
            colors.append(color)
        for name, interpolator in pysicgl.interpolation.__dict__.items():
            if interpolator == value.interpolator:
                interpolator_name = name

        return json.dumps({"colors": colors, "interpolator": interpolator_name})

    def deserialize(self, ser_value):
        data = json.loads(ser_value)
        interpolator = pysicgl.interpolation.__dict__[data["interpolator"]]
        return pysicgl.ColorSequence(colors=data["colors"], interpolator=interpolator)
