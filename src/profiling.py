import time


def current_micros_time():
    return time.time_ns() // 1000


class ProfileTimer:
    def set(self):
        self._t = current_micros_time()

    def mark(self):
        self._delta = current_micros_time() - self._t

    @property
    def period_us(self):
        return self._delta

    @property
    def period_ms(self):
        return self._delta / 1000


# @timed
def timed(f, *args, **kwargs):
    t = ProfileTimer()
    name = str(f).split(" ")[1]

    def inner(*args, **kwargs):
        t.set()
        result = f(*args, **kwargs)
        t.mark()
        print(f"'{name}' took {t.period_us:9.3f}us")
        return result

    return inner
