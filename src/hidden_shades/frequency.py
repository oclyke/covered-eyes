import time
import math


class FreqCounter:
    def __init__(self, frequency):
        self._freq = frequency
        self._basis = 0
        self._total = 0
        self._prev = 0

    def reset(self, ms):
        self._basis = ms
        self._total = 0
        self._prev = 0

    def update(self, ms):
        delta = ms - self._basis
        transitions = math.floor(self._freq * (delta / 1000.0))
        self._prev = self._total
        self._total = transitions

    def transitions(self):
        return self._total

    def outstanding(self):
        return self._total - self._prev
