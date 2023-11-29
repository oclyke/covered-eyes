class TimeWarp:
    def __init__(self, reference, frequency=1.0):
        self._reference = reference
        self._prev = self._reference()
        self._local = 0
        self._frequency = frequency

    def _update(self):
        now = self._reference()
        delta = now - self._prev
        self._local += self._frequency * delta
        self._prev = now

    def set_frequency(self, freq):
        self._frequency = float(freq)

    def local(self):
        self._update()
        return self._local
