from .variables.manager import VariableManager
from .variables.types import StringVariable
from .variables.responder import VariableResponder
import socket
import select
import asyncio
from artnet import ArtDMXPacket


class ArtnetProvider:
    def __init__(self, path, rate_limit_hz=30, poll_timeout_ms=5):
        self._root_path = path

        # config the rate limit for updates
        self._rate_limit_period = 1 / rate_limit_hz

        # set up a socket
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._poller = select.poll()
        self._poller.register(self._sock, select.POLLIN)
        self._poll_timeout_ms = poll_timeout_ms

        # set up a structure to track registered endpoints
        # - layers will be able to register their interest in particular universes
        # - if that universe does not exist in the map then it will be added
        # - this provider will be in charge of memory management and will provide read-only
        #   access to the memory for given layers
        self._universes = {}

        # declare private variables
        self._private_variable_responder = VariableResponder(
            lambda variable: self._handle_private_variable_change(variable)
        )
        self._private_variable_manager = VariableManager(
            f"{self._root_path}/private_vars"
        )
        self._private_variable_manager.declare_variable(
            StringVariable(
                "host:port",
                "127.0.0.1:6454",
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.initialize_variables()

    def _handle_private_variable_change(self, variable):
        if variable.name == "host:port":
            host, port = variable.value.split(":")
            self._sender_address = socket.getaddrinfo(host, port)[0][-1]

    def register_universes(self, universes):
        for universe in universes:
            if not universe in self._universes:
                self._universes[universe] = ArtDMXPacket()

    async def run(self):
        # register with server
        self._sock.sendto(b"add", self._sender_address)
        incoming = ArtDMXPacket()

        # process incoming packets
        # - packets are ingested until there would be a substantial block to other tasks
        # - when a block is detected the provider sleeps for the prescribed rate limit period
        # - after awaking from the sleep the provider will attempt to continue processing packets
        while True:
            # check for blocking timeout
            res = self._poller.poll(self._poll_timeout_ms)
            if not res:
                # rate limit the update loop to protect other processes
                # the outer loop will not resume until the next rate-limited opportunity
                await asyncio.sleep(self._rate_limit_period)
                continue

            bytes_recvd = self._sock.readinto(incoming.buffer)
            incoming.update()
            universe = incoming.universe

            if universe in self._universes:
                packet = self._universes[universe]
                packet.ingest(incoming.buffer)
                packet.update()

    @property
    def universes(self):
        return self._universes
