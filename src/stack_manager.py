import stack


class StackManager:
    def __init__(self, path, layer_initializer):
        from cache import Cache

        self._stackA = stack.Stack(f"{path}/", "A", layer_initializer)
        self._stackB = stack.Stack(f"{path}/", "B", layer_initializer)

        self._stacks = {
            "A": self._stackA,
            "B": self._stackB,
        }

        self._active = None
        self._inactive = None

        initial_info = {"active": "A", "stacks": list(self._stacks.keys())}
        self._info = Cache(
            f"{path}/info",
            initial_info,
            lambda key, value: self._handle_info_change(key, value),
        )

    # expression selection information
    def _handle_info_change(self, key, value):
        if key == "active":
            self._handle_active_change(value)

    def _handle_active_change(self, name):
        if name == "A":
            self._active = self._stackA
            self._inactive = self._stackB
        elif name == "B":
            self._active = self._stackB
            self._inactive = self._stackA
        else:
            raise ValueError

    # a tool to activate an expression while simultaneously deactivating the other
    def activate(self, name):
        if name in ["A", "B"]:
            self._info.set("active", name)
        else:
            raise ValueError

    def get(self, name):
        if name == "active":
            return self._active
        if name == "inactive":
            return self._inactive
        else:
            raise ValueError

    def switch(self):
        active = self._info.get("active")
        if active == "A":
            self.activate("B")
        else:
            self.activate("A")

    @property
    def active(self):
        return self._active

    @property
    def inactive(self):
        return self._inactive

    @property
    def info(self):
        return self._info.cache

    @property
    def stacks(self):
        return self._stacks
