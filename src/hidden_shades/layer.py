import pysicgl
from cache import Cache
from .variables.manager import VariableManager
from .variables.types import OptionVariable, FloatingVariable, ColorSequenceVariable
from .variables.responder import VariableResponder
from pathutils import rmdirr


class Layer:
    DEFAULT_COMPOSITION_MODE = "ALPHA_SOURCE_OVER"
    DEFAULT_COLOR_SEQUENCE_INTERPOLATOR = "CONTINUOUS_CIRCULAR"

    def __init__(self, id, path, interface, globals, init_info={}, post_init_hook=None):
        self.id = id

        # reference to hidden shades globals
        self._globals = globals

        # the root path for this layer will not change during its lifetime
        self._root_path = path
        self._vars_path = f"{self._root_path}/vars"
        self._info_path = f"{self._root_path}/info"

        # a pysicgl interface will be provided
        self.canvas = interface

        # the shard related items are left uninitialized
        # it is possible to set these in the post-init hook
        self._shard = None
        self._frame_generator_obj = None
        self._active = False

        # static info does not change
        self._static_info = {
            "id": self.id,
        }

        # variables which may be dynamically registered for external control
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

        # declare private variables
        self._private_variable_manager = VariableManager(
            f"{self._root_path}/private_vars"
        )
        self._private_variable_responder = VariableResponder(
            lambda variable: self._handle_private_variable_change(variable)
        )
        self._private_variable_manager.declare_variable(
            OptionVariable(
                "composition_mode",
                Layer.DEFAULT_COMPOSITION_MODE,
                pysicgl.composition.__dict__.keys(),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.declare_variable(
            ColorSequenceVariable(
                "palette",
                pysicgl.ColorSequence(
                    [0x000000, 0xFFFFFF],
                    pysicgl.interpolation.__dict__[
                        Layer.DEFAULT_COLOR_SEQUENCE_INTERPOLATOR
                    ],
                ),
            )
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                "brightness",
                1.0,
            )
        )
        self._private_variable_manager.initialize_variables()

        # mutable info recorded in a cache
        # (this must be done after default values are set because it
        # will automatically enable the module if possible)
        initial_info = {
            "shard_uuid": None,
            "index": None,
            "active": True,
            "use_local_palette": False,
        }
        self._info = Cache(
            f"{self._root_path}/info",
            {**initial_info, **init_info},
            lambda key, value: self._handle_info_change(key, value),
        )

        # allow for post-init
        if post_init_hook is not None:
            post_init_hook(self)

    def _handle_private_variable_change(self, variable):
        if variable.name == "composition_mode":
            key = self.private_variable_manager.variables["composition_mode"].value
            self._compositor = pysicgl.composition.__dict__[key]

    def _handle_info_change(self, key, value):
        self.reset_canvas()
        if key == "active":
            active = bool(value)
            self._active = active
            return active
        if key == "palette":
            if value is None:
                self._palette = None
            else:
                l = list(int(element) for element in value)
                self._palette = pysicgl.ColorSequence(l)
                return l

    def destroy_storage(self):
        """
        Removes the layer information from storage
        """
        rmdirr(self._root_path)

    def initialize_frame_generator(self):
        self._frame_generator_obj = self._shard.frames(self)
        next(self._frame_generator_obj)

    def set_shard(self, shard):
        self._shard = shard

    def run(self):
        """
        Gets the next frame from the frame generator object, only if the layer is ready and active
        """
        if self._active:
            next(self._frame_generator_obj)
            pysicgl.functional.scale(
                self.canvas,
                self._private_variable_manager.variables["brightness"].value,
            )

    def reset_canvas(self):
        pysicgl.functional.interface_fill(self.canvas, 0x000000)

    def set_index(self, idx):
        self._info.set("index", idx)

    def set_active(self, active):
        self._info.set("active", bool(active))

    def merge_info(self, info):
        self._info.merge(info)

    def use_local_palette(self, use_local):
        self._info.set("use_local_palette", bool(use_local))

    @property
    def info(self):
        return dict(**self._info.cache, **self._static_info)

    @property
    def variable_manager(self):
        return self._variable_manager

    @property
    def private_variable_manager(self):
        return self._private_variable_manager

    @property
    def palette(self):
        if self._info.get("use_local_palette"):
            return self._private_variable_manager.variables["palette"].value
        else:
            return self._globals.variable_manager.variables["palette"].value

    @property
    def compositor(self):
        return self._compositor

    @property
    def active(self):
        return self._active
