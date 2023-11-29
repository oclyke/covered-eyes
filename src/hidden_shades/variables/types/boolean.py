from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_BOOLEAN


class BooleanVariable(VariableDeclaration):
    def __init__(self, name, default, tags=("False", "True"), **kwargs):
        super().__init__(TYPECODE_BOOLEAN, bool, name, default, **kwargs)
        self._tags = tuple(str(tag) for tag in tags)

    def deserialize(self, ser_value):
        """
        given a serialized value (str) returns the expected type
        this is used to load values
        """
        return ser_value == "True"

    def serialize(self, value):
        """
        given a valid value for this variable return the serialized
        form which may be used to recover the value via the deserialize
        method
        """
        return str(value)

    def get_data(self):
        return {
            "tags": self._tags,
        }
