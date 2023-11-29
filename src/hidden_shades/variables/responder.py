class VariableResponder:
    def __init__(self, handler):
        self._handler = handler

    def handle(self, variable):
        self._handler(variable)
