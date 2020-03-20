
#TODO
# Parametrizar a cifra com k1



import socket
import sys
import string
import random 
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45676  # The port used by the server
KEY = (b"very secret key" + bytes(16))[:16]

class Client(object):
    
    def run(self):
        num_seq=0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            self.send_iv(s)
            k1=hashlib.sha256(KEY+b'1').digest()   
            k2=hashlib.sha256(KEY+b'2').digest()
            while True:
                msg=sys.stdin.buffer.readline()[:-1]
                if msg == b"exit":
                    s.close()
                    break
                else:
                    msg = self.pad(msg)
                    cryptogram = self.enc(self.iv, msg, k1)
                    s.sendall(cryptogram)
                    num_seq=num_seq+1
                    s.sendall(hmac.new(k2,cryptogram+bytes(num_seq),hashlib.sha256).hexdigest().encode()) 
                    


class AES_CTR_NoPadding(Client):
    def __init__(self):
        self.iv = Random.new().read(8)

    def send_iv(self, s):
        s.sendall(self.iv)

    def pad(self, p):
        return p

    def enc(self, iv, p, k):
        ctr_e = Counter.new(64, prefix=iv)
        ciph = AES.new(KEY, AES.MODE_CTR, counter=ctr_e)
        return ciph.encrypt(p)

class AES_CTR_PKCS5Padding(AES_CTR_NoPadding):
    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)
