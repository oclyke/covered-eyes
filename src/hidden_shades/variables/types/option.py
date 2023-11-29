from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_OPTION


class OptionVariable(VariableDeclaration):
    def __init__(self, name, default, options, **kwargs):
        self._options = tuple(str(val) for val in options)
        super().__init__(TYPECODE_OPTION, str, name, default, **kwargs)

    def validate(self, value):
        return value in self._options

    def get_data(self):
        return {
            "options": self._options,
        }
