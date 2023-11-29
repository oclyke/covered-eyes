from cache import Cache
from .timewarp import TimeWarp


class TimeBase(TimeWarp):
    def __init__(self, path, reference):
        super().__init__(reference)
        self._root_path = path

        # cache mutable values
        initial_info = {
            "frequency": 1.0,
        }
        self._info = Cache(
            f"{self._root_path}/info",
            initial_info,
            lambda key, value: self._handle_info_change(key, value),
        )

    def _handle_info_change(self, key, value):
        if key == "frequency":
            self.set_frequency(value)
