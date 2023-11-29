class UDPDriver:
    def __init__(self, host="0.0.0.0", ports=(6969, 6420)):
        import socket

        self._host = host
        self._port_control, self._port_data = ports
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._addr = socket.getaddrinfo(self._host, self._port_data)[0][-1]

    def push(self, interface):
        self._sock.sendto(interface.memory, self._addr)
