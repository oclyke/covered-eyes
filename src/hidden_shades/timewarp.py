class TimeWarp:
    def __init__(self, reference, frequency=1.0):
        self._reference = reference
        self._frequency = frequency

    def set_frequency(self, freq):
        self._frequency = float(freq)

    def local(self):
        return self._frequency * self._reference()
