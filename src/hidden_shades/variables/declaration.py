class VariableDeclaration:
    def __init__(
        self, typecode, type, name, default, description=None, responders=None
    ):
        self._name = name
        self._type = type
        self._typecode = int(typecode)
        self._description = description

        # validate the default value
        if not self.validate(default):
            raise ValueError(
                f'invalid default value "{default}" for {self} with type "{self._type}"'
            )

        # set the default and initial values
        self._default = default
        self._value = default

        # using a new empty list is important to avoid a leak which
        # causes responders from any instance of a VariableDeclaration
        # to all be called for any change to any instance... this note
        # exists mostly to serve as a clue in case this behaviour is
        # observed again
        self._responders = []
        if responders is not None:
            for responder in responders:
                self.add_responder(responder)

    def add_responder(self, responder):
        self._responders.append(responder)

    def notify(self):
        for responder in self._responders:
            responder.handle(self)

    def validate(self, value):
        """
        validates the given value
        may raise one of:
        - ValueError
        - TypeError
        returns True if provided value is valid, else False
        when this function returns false it may raise a default error
        """
        return type(value) is self._type

    def deserialize(self, ser_value):
        """
        given a serialized value (str) returns the expected type
        this is used to load values
        """
        return self._type(ser_value)

    def serialize(self, value):
        """
        given a valid value for this variable return the serialized
        form which may be used to recover the value via the deserialize
        method
        """
        return str(value)

    def get_data(self):
        """
        returns additional data for derived classes
        """
        return {}

    def get_dict(self):
        serialized_default = self.serialize(self._default)
        serialized_value = self.serialize(self._value)
        return {
            "typecode": self._typecode,
            "id": self._name,
            "description": self._description,
            "default": serialized_default,
            "value": serialized_value,
            "data": self.get_data(),
        }

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def default(self):
        return self._default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if not self.validate(val):
            raise ValueError
        self._value = val
        self.notify()
