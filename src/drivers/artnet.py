from artnet import ArtDMXPacket
import socket

MAX_BYTES_PER_UNIVERSE = 512


class ArtnetDriver:
    def __init__(self, host, port=6454, start_universe=0, physical_port=0):
        self._packet = ArtDMXPacket(physical_port)

        self._disabled = False

        # configure socket
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._addr = socket.getaddrinfo(self._host, self._port)[0][-1]

        # configure output
        self._start_universe = start_universe
        self._sequence = 0
        self.advance_sequence()

    def advance_sequence(self):
        self._sequence += 1
        if self._sequence > 255:
            self._sequence = 1
        self._packet.sequence = self._sequence

    def push(self, interface):
        if not self._disabled:
            bytes_remaining = len(interface.memory)
            offset = 0
            universes = (bytes_remaining // MAX_BYTES_PER_UNIVERSE) + 1

            for universe in range(universes):
                length = min(MAX_BYTES_PER_UNIVERSE, bytes_remaining)
                self._packet.universe = universe
                self._packet.data = interface.memory[offset : offset + length]

                try:
                    self._sock.sendto(self._packet.buffer, self._addr)
                except:
                    print("ERROR sending ArtNet packet")
                    self._disabled = True

                self.advance_sequence()
                offset += length
                bytes_remaining -= length
