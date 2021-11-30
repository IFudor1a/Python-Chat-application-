import socket


class Socket:
    host = '127.0.0.1'
    port = 9090
    socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
    )

    def broadcast(self, *args):
        raise NotImplementedError

    def handle(self, *args):
        raise NotImplementedError
