import pysicgl
import seasnake


class SimpleSnakeArrangement:
    def __init__(self, screen, reverse_first=False):
        # the screen is used to inform the width of snake rows
        self._screen = screen

        # a simple snake arrangement assumes that the screen memory is
        # fully utilized and that every other screen row is reversed.
        self._memory = pysicgl.allocate_pixel_memory(self._screen.pixels)
        self._interface = pysicgl.Interface(screen, self._memory)

        self._reverse_first = reverse_first

    def map(self, interface):
        """
        Map a standard pysicgl interface into the memory according to snake rules.
        """
        seasnake.map_simple(
            interface.memory, self._memory, self._screen.width, self._reverse_first
        )


class SnakeDriver(SimpleSnakeArrangement):
    def __init__(self, screen, output, reverse_first=False):
        # init the simple snake arrangement which is used
        # to remap display memory
        super().__init__(screen, reverse_first)

        # an output supports ingest and push methods to respectively
        # prepare and transmit buffer information
        self._output = output

    def ingest(self, interface):
        """ """
        # first, remap the interface according to the hardware output arrangement
        self.map(interface)

        # then ingest the mapped memory into the output driver
        self._output.ingest(self._interface)

    def push(self, interface):
        self._output.push(interface)
