import socket
import sys
from Crypto.Cipher import ARC4
import string
import random 

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45676  # The port used by the server
#KEY = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
KEY=b"very secret key"

class Client(object):
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            while True:
                msg=sys.stdin.buffer.readline()[:-1]
                if msg == b"exit":
                    s.close()
                    break
                else:
                    cryptogram=self.enc(msg)
                    s.sendall(cryptogram)

class RC4(Client):
    def enc(self,p):
        return ARC4.new(KEY).encrypt(p)
