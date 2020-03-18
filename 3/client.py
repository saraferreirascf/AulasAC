import socket
import sys
import string
import random 

from Crypto.Cipher import ARC4, AES
from Crypto import Random

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45676  # The port used by the server
#KEY = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
KEY = (b"very secret key" + bytes(16))[:16]

class Client(object):
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            self.send_iv(s)
            while True:
                msg=sys.stdin.buffer.readline()[:-1]
                if msg == b"exit":
                    s.close()
                    break
                else:
                    msg = self.pad(msg)
                    cryptogram = self.enc(self.iv, msg)
                    s.sendall(cryptogram)

class RC4(Client):
    def __init__(self):
        self.iv = None

    def send_iv(self, s):
        ...

    def pad(self, p):
        return p

    def enc(self, iv, p):
        return ARC4.new(KEY).encrypt(p)

class AES_CBC_NoPadding(Client):
    def __init__(self):
        self.iv = Random.new().read(16)

    def send_iv(self, s):
        s.sendall(self.iv)

    def pad(self, p):
        return p

    def enc(self, iv, p):
        ciph = AES.new(KEY, AES.MODE_CBC, iv)
        return ciph.encrypt(p)

class AES_CBC_PKCS5Padding(AES_CBC_NoPadding):
    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)

class AES_CFB8_NoPadding(Client):
    def __init__(self):
        self.iv = Random.new().read(16)

    def send_iv(self, s):
        s.sendall(self.iv)

    def pad(self, p):
        return p

    def enc(self, iv, p):
        ciph = AES.new(KEY, AES.MODE_CFB, iv=iv, segment_size=8)
        return ciph.encrypt(p)

class AES_CFB8_PKCS5Padding(AES_CFB8_NoPadding):
    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)

class AES_CFB_NoPadding(Client):
    def __init__(self):
        self.iv = Random.new().read(16)

    def send_iv(self, s):
        s.sendall(self.iv)

    def pad(self, p):
        return p

    def enc(self, iv, p):
        ciph = AES.new(KEY, AES.MODE_CFB, iv)
        return ciph.encrypt(p)

class AES_CFB_PKCS5Padding(AES_CFB_NoPadding):
    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)
