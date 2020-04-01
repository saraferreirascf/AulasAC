import socket
import sys
import string
import random 
import hmac
import json
import hashlib
import base64

from keyexchange import DiffieHellman
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45676  # The port used by the server

class Client(object):
    def serialize(self, o):
        return json.dumps(o).encode()

    def deserialize(self, x):
        return json.loads(x.decode('utf8'))

    def key_exchange(self, c):
        ...

    def pad(self, p):
        return p

    def enc(self, p):
        return self.serialize(p)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print('<begun key exchange>')
            self.key_exchange(s)
            print('<key exchange successful>')
            while True:
                try:
                    msg=sys.stdin.buffer.readline()[:-1]
                except KeyboardInterrupt:
                    s.close()
                    break
                if msg == b"exit":
                    s.close()
                    break
                else:
                    packet = self.enc(msg)
                    s.sendall(packet)
                    
class SafeClient(Client):
    def __init__(self):
        self.k1 = None
        self.k2 = None
        self.seq = 0

    def key_exchange(self, c):
        dh = DiffieHellman()
        c.sendall(self.serialize(dh.get_public()))
        msg = c.recv(4096)
        key = dh.compute_shared_secret(self.deserialize(msg))
        self.k1 = hashlib.sha256(key+b'1').digest()[:16]
        self.k2 = hashlib.sha256(key+b'2').digest()[:16]

    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)

    def enc(self, p):
        iv = Random.new().read(8)
        ctr_e = Counter.new(64, prefix=iv)
        ciph = AES.new(self.k1, AES.MODE_CTR, counter=ctr_e)
        seq = self.seq.to_bytes(8, 'big')
        self.seq = (self.seq + 1) & 0xffffffffffffffff
        cryptogram = str(base64.encodebytes(ciph.encrypt(self.pad(p))), 'utf8')
        mac = hmac.new(self.k2, cryptogram.encode()+seq, hashlib.sha256).hexdigest()
        return self.serialize({
            'iv': str(base64.encodebytes(iv), 'utf8'),
            'mac': mac,
            'cryptogram': cryptogram,
        })
