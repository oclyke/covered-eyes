from pathutils import ensure_dirs
from .responder import VariableResponder


class VariableManager(VariableResponder):
    def __init__(self, path):
        super().__init__(lambda variable: self._handle_variable_change(variable))
        self._path = path
        self._variables = {}

        # ensure filesystem storage exists
        ensure_dirs(self._path)

    def _handle_variable_change(self, variable):
        self._store_variable(variable)

    def _store_variable(self, variable):
        serialized = variable.serialize(variable.value)
        with open(f"{self._path}/{variable.name}", "w") as f:
            f.write(serialized)

    def declare_variable(self, variable):
        """
        This method allows automatic association of a declared variable
        to this object so that it may be properly cached.
        """
        self._variables[variable.name] = variable  # register it into the list
        variable.add_responder(self)  # register self as a responder

        return variable

    def initialize_variables(self):
        """
        This method should be called once all variables have been declared.
        It is used to load the initial values, if any, from the filesystem and notify
        responders as needed.
        """
        for name, variable in self._variables.items():
            # try to read the serialized value from memory allowing for it not to exist
            serialized = None
            try:
                with open(f"{self._path}/{variable.name}", "r") as f:
                    serialized = str(f.read())
            except OSError:
                pass

            # if a serialized value was found use it to set the value of the variable
            if serialized is not None:
                variable.value = variable.deserialize(serialized)

            # finally store the current value and notify any responders
            self._store_variable(variable)
            variable.notify()

    @property
    def variables(self):
        return self._variables

    @property
    def info(self):
        ids = list(self._variables.keys())
        return {
            "total": len(ids),
            "ids": ids,
        }
