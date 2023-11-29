import json
from pathutils import ensure_parent_dirs


class Cache:
    """
    Cache storage backed by filesystem.
    Nested dictionaries not allowed.
    """

    def __init__(self, path, initial_values={}, on_change=None):
        self._path = path
        self._on_change = on_change
        self._cache = initial_values

        # try to load existing file
        # if failed then make sure dirs exist for initial storage
        try:
            self.load()
        except FileNotFoundError:
            ensure_parent_dirs(path)
            self.notify()

        # store initial values
        self.store()

    def set_change_handler(self, on_change):
        """
        Used to set the change handler after object construction.
        """
        self._on_change = on_change

    def notify(self, key=None):
        """
        Notify the registered change handler, if any, of the value of one or all keys in the cache.
        """
        if self._on_change is not None:
            if key is not None:
                corrected = self._on_change(key, self._cache[key])
                if corrected is not None:
                    self._cache[key] = corrected
            else:
                for key in self._cache.keys():
                    corrected = self._on_change(key, self._cache[key])
                    if corrected is not None:
                        self._cache[key] = corrected

    def load(self):
        with open(self._path, "r") as f:
            self._cache = json.load(f)
        self.notify()

    def store(self):
        with open(self._path, "w") as f:
            json.dump(self._cache, f)

    def get(self, name):
        return self._cache[name]

    def set(self, key, value):
        self._cache[key] = value
        self.notify(key)
        self.store()

    def merge(self, map):
        for key, value in map.items():
            self._cache[key] = value
        self.notify()
        self.store()

    @property
    def cache(self):
        return self._cache
