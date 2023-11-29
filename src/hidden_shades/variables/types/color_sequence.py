from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_COLOR_SEQUENCE
import pysicgl
import json


class ColorSequenceVariable(VariableDeclaration):
    def __init__(self, name, default, **kwargs):
        super().__init__(
            TYPECODE_COLOR_SEQUENCE, pysicgl.ColorSequence, name, default, **kwargs
        )

    def serialize(self, value):
        colors = []
        for color in value:
            colors.append(color)
        return json.dumps({"colors": colors})

    def deserialize(self, ser_value):
        data = json.loads(ser_value)
        return pysicgl.ColorSequence(data["colors"])
