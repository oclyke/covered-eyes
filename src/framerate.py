class FramerateHistory:
    def __init__(self, n=10):
        self._n = n
        self._period_history = [0] * self._n
        self._average_period_ms = 0

    def _compute_average(self):
        self._average_period_ms = sum(self._period_history) / len(self._period_history)

    def record_period_ms(self, period):
        self._period_history.append(period)
        if len(self._period_history) > self._n:
            self._period_history.pop(0)

    def average(self):
        self._compute_average()
        if self._average_period_ms == 0:
            return None
        else:
            return 1000 / self._average_period_ms
