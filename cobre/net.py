import socket
import cobre.errors

class Socket(object):
    def __init__(self):
        try:
            self._sock = socket.socket()
        except Exception as e:
            raise cobre.errors.CreationError(e)

    def _close(self):
        s = self._sock
        if s.fileno() != -1:
            s.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self._close()

    def __del__(self):
        self._close()

    def timeout(self, secs):
        self._sock.settimeout(secs)

    def send_bytes(self, buf):
        try:
            self._sock.send(buf)
        except Exception as e:
            raise cobre.errors.SendError(e)

    def recv_bytes(self, buf=4096):
        t = type(buf)
        try:
            if t == bytes or t == bytearray:
                return self._sock.recv_into(buf)
            else:
                return self._sock.recv(buf)
        except Exception as e:
            raise cobre.errors.RecvError(e)

# TODO: finish these two classes
# https://docs.python.org/3/library/socket.html
class Client(Socket):
    def __init__(self, addr=None, sock=None):
        if sock == None:
            super().__init__()
            self.addr = addr
            try:
                host, port = addr.split(':')
                self._sock.connect((host, int(port)))
            except Exception as e:
                raise cobre.errors.ConnectError(e)
        else:
            self._sock = sock

class Server(Socket):
    def __init__(self, addr='127.0.0.1:0', sock=None):
        if sock == None:
            super().__init__()
            self.addr = addr
            try:
                host, port = addr.split(':')
                self._sock.bind((host, int(port)))
            except Exception as e:
                raise cobre.errors.BindError(e)
            try:
                self._sock.listen()
            except Exception as e:
                raise cobre.errors.ListenError(e)
        else:
            self._sock = sock

    def accept(self):
        try:
            s = self._sock.accept()
            return Client(sock=s[0])
        except Exception as e:
            raise cobre.errors.AcceptError(e)
