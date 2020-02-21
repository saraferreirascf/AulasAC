import socket
import cobre.errors

class Socket(object):
    # addr:port
    def __init__(self, addr):
        host, port = addr.split(':')
        self._sock = socket.socket(socket.AF_INET)
        try:
            self._sock.connect((host, int(port)))
        except socket.error as e:
            self._sock.close()
            raise cobre.errors.ConnectionError(e)

    def __del__(self):
        self._sock.close()

    def sendmsg(self, msg):
        self._sock
