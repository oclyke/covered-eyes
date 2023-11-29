import asyncio
from hidden_shades.audio.source import ManagedAudioSource
import socket
from collections import deque


class UDPAudioSourceMic(ManagedAudioSource):
    def __init__(self, path, name, network_config, audio_config):
        super().__init__(path, name, audio_config)

        # break out network config
        self._host, self._port = network_config

        # create a buffer to receive data from the socket connection
        self._BYTES_PER_SAMPLE = 2
        self._udp_buffer = bytearray(self._BYTES_PER_SAMPLE * self._sample_length)

        # create a deque to streamline operations
        self._queue = deque((), self._sample_length)

    async def run(self):
        sock = None
        read_fail_count = 0

        while True:
            # wait for some amount of time
            # (to allow other tasks to operate)
            # ((this is ugly, and it's because I don't know
            # how to make a proper asynchronous UDP client in
            # micropython))
            await asyncio.sleep(0.01)

            if sock is None:
                # create and connect a socket to the audio server
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sockaddr = socket.getaddrinfo(self._host, self._port)[0][-1]
                try:
                    sock.connect(sockaddr)
                except OSError as error:
                    sock = None
                    timeout_secs = 3
                    if error.args[0] == 61:
                        print(
                            f"FAILED: connect to UDP audio source. retrying in {timeout_secs} seconds..."
                        )
                        await asyncio.sleep(timeout_secs)
                        continue
                    else:
                        raise error

            # read data into the buffer
            bytes_read = sock.readinto(self._udp_buffer)

            # check for broken connection
            if bytes_read == 0:
                read_fail_count += 1
                if read_fail_count > 5:
                    print("ERROR: UDP audio connection broken, resetting...")
                    sock.close()
                    sock = None
                    continue

            # convert data into samples in deque
            samples_read = int(bytes_read / self._BYTES_PER_SAMPLE)
            for idx in range(samples_read):
                sample = int.from_bytes(
                    self._udp_buffer[
                        self._BYTES_PER_SAMPLE
                        * (idx) : self._BYTES_PER_SAMPLE
                        * (idx + 1)
                    ],
                    "little",
                )
                self._queue.append(sample)

            # check available data length
            available_samples = len(self._queue)
            if available_samples < self._sample_length:
                # if we don't have a full sample set then continue
                print(
                    f"waiting for {self._sample_length - available_samples} more samples"
                )
                continue

            # consume the samples
            for idx in range(self._sample_length):
                self._buffer[idx] = self._queue.popleft()

            self.apply_volume()
            self.fft.compute()
            self.fft_postprocess()
