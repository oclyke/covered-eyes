from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_STRING


class StringVariable(VariableDeclaration):
    def __init__(self, default, name, **kwargs):
        super().__init__(TYPECODE_STRING, str, default, name, **kwargs)
