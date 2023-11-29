import asyncio
import math
from hidden_shades.audio.source import ManagedAudioSource


class MockAudioSource(ManagedAudioSource):
    def __init__(self, path, name, freq, fft_config):
        super().__init__(path, name, fft_config)

        self._sample_frequency, self._sample_length = fft_config
        self._freq = freq

    async def run(self):
        def sine_wave(freq, sample_freq):
            # the time period between each step is 1/sample_freq seconds long
            # one full cycle should take 1/freq seconds
            count = 0
            while True:
                phase = count / sample_freq
                yield math.sin(2 * math.pi * freq * phase)
                count += 1
                if count > sample_freq:
                    count = 0

        # make the test signal
        sine_generator = sine_wave(self._freq, self._sample_frequency)

        while True:
            # simulate waiting for a real audio source to fill the buffer
            for idx in range(self._sample_length):
                self._buffer[idx] = next(sine_generator)
            await asyncio.sleep(self._sample_length / self._sample_frequency)

            self.apply_volume()
            self.fft.compute()
            self.fft_postprocess()
