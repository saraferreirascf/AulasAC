import socket
import sys
import string
import random 

from Crypto.Cipher import ARC4, AES
from Crypto import Random
import hmac
import hashlib

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45676  # The port used by the server
KEY = (b"very secret key" + bytes(16))[:16]

class Client(object):
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            self.send_iv(s)
            k1=hashlib.sha256(KEY,'1') #chave para parametrizar cifra 
            k2=hashlib.sha256(KEY,'2')
            while True:
                msg=sys.stdin.buffer.readline()[:-1]
                if msg == b"exit":
                    s.close()
                    break
                else:
                    msg = self.pad(msg)
                    cryptogram = self.enc(self.iv, msg)
                    #s.sendall(hmac.new(k2,cryptogram,seq_number)) #qual e o numero de sequencia?
					#s.sendall(cryptogram)

class AES_CTR_NoPadding(Client):
    def __init__(self):
        self.iv = Random.new().read(16)

    def send_iv(self, s):
        s.sendall(self.iv)

    def pad(self, p):
        return p

    def enc(self, iv, p):
    	ctr_d = Counter.new(64, prefix=iv)
    	ciph = AES.new(KEY, AES.MODE_CTR, counter=ctr_e)
    	return ciph.encrypt(p)

class AES_CTR_PKCS5Padding(AES_CTR_NoPadding):
    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)
