import pysicgl
import hidden_shades
from pysicgl_utils import Display
from hidden_shades import artnet_provider


def frames(layer):
    print("audio source: ", hidden_shades.audio_manager.audio_source.name)

    screen = layer.canvas.screen
    display = Display(screen)
    (numx, numy) = display.extent
    (maxx, maxy) = display.shape

    # create a coordinator that simplifies access to the underlying universe data
    # - the total number of required channels is provided
    # - the coordinator assumes that the data is contiguous
    # - the coordinator assumes that the data begins at an offset byte of 0
    total_channels = screen.pixels * 3
    coordinator = UniverseCoordinator(artnet_provider, total_channels)

    # register universes against the provider
    # (note: this does not prevent other layers from registering the same universes)
    artnet_provider.register_universes(coordinator.universes)

    while True:
        yield None

        # plot universes directly to output
        for info in display.pixel_info():
            idx, coordinates, position = info

            # get the color of this pixel from the coordinated artnet sources
            color = int.from_bytes(
                bytearray(
                    [
                        coordinator[3 * idx + 0],
                        coordinator[3 * idx + 1],
                        coordinator[3 * idx + 2],
                        0xFF,
                    ]
                ),
                "little",
            )

            # plot the pixel
            pysicgl.functional.interface_pixel(layer.canvas, color, coordinates)


class UniverseCoordinator:
    UNIVERSE_MAX_CHANNELS = 512

    def __init__(
        self, provider, total_channels, start_universe=0, universes=None, start_offset=0
    ):
        self._provider = provider
        self._start_offset = start_offset
        self._total_channels = int(total_channels)
        self._universes = universes
        if self._universes is None:
            total_universes = len(self) // UniverseCoordinator.UNIVERSE_MAX_CHANNELS
            if len(self) % UniverseCoordinator.UNIVERSE_MAX_CHANNELS:
                total_universes += 1
            self._universes = tuple(
                range(start_universe, start_universe + total_universes)
            )

        print("total channels: ", total_channels)
        print("universes: ", self._universes)

    def __len__(self):
        return self._total_channels

    def __getitem__(self, idx):
        # compute the index into the universes using the start offset
        index = idx + self._start_offset

        # using the index into contiguous data region determine how many universes and bytes into the data this index would exist
        universe_idx = index // UniverseCoordinator.UNIVERSE_MAX_CHANNELS
        byte_idx = index % UniverseCoordinator.UNIVERSE_MAX_CHANNELS

        # get the universe id from the map of universes
        universe_id = self._universes[universe_idx]

        # print("idx, index, (uni, byte)", idx, index, (universe_id, byte_idx))

        # print(self._provider.universes)

        # get the packet from the provider
        packet = self._provider.universes[universe_id]

        # return the correct byte from the packet
        return packet.data[byte_idx]

    @property
    def universes(self):
        return self._universes
