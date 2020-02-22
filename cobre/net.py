import socket
import cobre.errors

class Socket(object):
    def __init__(self):
        try:
            self._sock = socket.socket(socket.AF_INET)
        except socket.error as e:
            raise cobre.errors.ConnectionError(e)

    def __del__(self):
        self._sock.close()

    def send_bytes(self, buf):
        try:
            self._sock.send(buf)
        except (socket.error, BrokenPipeError) as e:
            raise cobre.errors.SendError(e)

    def recv_bytes(self, buf=4096):
        t = type(buf)
        try:
            if t == bytes or t == bytearray:
                self._sock.recv_into(buf)
            else:
                self._sock.recv(buf)
        except (socket.error, BrokenPipeError) as e:
            raise cobre.errors.RecvError(e)

# TODO: finish these two classes
class Client(Socket):
    def __init__(self, addr):
        super().__init__()
        self.addr = addr

class Server(Socket):
    def __init__(self, addr):
        super().__init__()
        self.addr = addr
