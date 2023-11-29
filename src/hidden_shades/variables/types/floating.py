from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_FLOATING


class FloatingVariable(VariableDeclaration):
    def __init__(
        self, name, default, default_range=(0, 1), allowed_range=None, **kwargs
    ):
        self._default_range = tuple(float(val) for val in default_range)
        self._allowed_range = (
            tuple(float(val) for val in allowed_range)
            if allowed_range is not None
            else None
        )
        super().__init__(TYPECODE_FLOATING, float, name, default, **kwargs)

    def validate(self, value):
        v = self._type(value)
        if self._allowed_range is not None:
            if v < min(self._allowed_range):
                raise ValueError
            if v > max(self._allowed_range):
                raise ValueError
        return True

    def get_data(self):
        return {
            "default_range": self._default_range,
            "allowed_range": self._allowed_range,
        }
