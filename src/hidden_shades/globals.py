import pysicgl
from cache import Cache
from .variables.manager import VariableManager
from .variables.types import FloatingVariable, ColorSequenceVariable

ALPHA_TRANSPARENCY_HALF = 0x40000000

DEFAULT_PALETTE = pysicgl.ColorSequence(
    colors=list(
        map(
            lambda color: ALPHA_TRANSPARENCY_HALF | color,
            
            [
                0xFF0000,
                0xFF5F00,
                0xFFBF00,
                0xDFFF00,
                0x7FFF00,
                0x1FFF00,
                0x00FF3F,
                0x00FF9F,
                0x00FFFF,
                0x009FFF,
                0x003FFF,
                0x1F00FF,
                0x7F00FF,
                0xDF00FF,
                0xFF00BF,
                0xFF005F,
            ],
        )
    ),
)


class GlobalsManager:
    def __init__(self, path):
        # create root path
        self._root_path = path

        # a variable manager to expose variables
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

        # these global variables are accessible in user space
        self._variable_manager.declare_variable(FloatingVariable("brightness", 1.0))
        self._variable_manager.declare_variable(
            ColorSequenceVariable("palette", DEFAULT_PALETTE)
        )
        self._variable_manager.initialize_variables()

    @property
    def variable_manager(self):
        return self._variable_manager
