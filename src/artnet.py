class ArtDMXPacket:
    def __init__(self, physical_port=0):
        self._buffer = bytearray(18 + 512)
        self._data = memoryview(self._buffer)

        self.header = bytearray("Art-Net\0", "utf-8")
        self.opcode = 0x5000
        self.protocol_version = 0x00014
        self.physical_port = physical_port

        self._length = 0

    def update(self):
        self._header = self._buffer[0:8]
        self._opcode = int.from_bytes(self._buffer[8:10], "little")
        self._protocol_version = int.from_bytes(self._buffer[10:12], "big")
        self._sequence = int(self._buffer[12])
        self._physical_port = int(self._buffer[13])
        self._universe = int.from_bytes(self._buffer[14:16], "little")
        self._length = int.from_bytes(self._buffer[16:18], "big")

    def ingest(self, buffer):
        self._buffer[:] = buffer

    @property
    def buffer(self):
        return self._buffer

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, val):
        self._header = bytearray(val)
        self._buffer[0:8] = self._header

    @property
    def opcode(self):
        return self._opcode

    @opcode.setter
    def opcode(self, val):
        self._opcode = int(val)
        self._buffer[8:10] = self._opcode.to_bytes(2, "little")

    @property
    def protocol_version(self):
        return self._protocol_version

    @protocol_version.setter
    def protocol_version(self, val):
        self._protocol_version = int(val)
        self._buffer[10:12] = self._protocol_version.to_bytes(2, "big")

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, val):
        self._sequence = int(val)
        self._buffer[12] = self._sequence

    @property
    def physical_port(self):
        return self._physical_port

    @physical_port.setter
    def physical_port(self, val):
        self._physical_port = int(val)
        self._buffer[13] = self._physical_port

    @property
    def universe(self):
        return self._universe

    @universe.setter
    def universe(self, val):
        self._universe = int(val) & 0x7FFF
        self._buffer[14:16] = self._universe.to_bytes(2, "little")

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, val):
        self._length = int(val)
        self._buffer[16:18] = self._length.to_bytes(2, "big")

    @property
    def data(self):
        data_start = 18
        return self._data[data_start : data_start + self._length]

    @data.setter
    def data(self, val):
        for i in range(len(val)):
            self._buffer[18 + i] = val[i]
        self.length = len(val)
