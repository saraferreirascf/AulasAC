import socket
import threading
import string
import random 
import sys

from contextlib import closing
from Crypto.Cipher import ARC4, AES

HOST = '127.0.0.1'  #localhost
PORT = 45676 #non-privileged ports are > 1023
#KEY = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
KEY = (b"very secret key" + bytes(16))[:16]

class ServerThread(threading.Thread):
    def __init__(self,crypto,c,id):
        super().__init__()
        self.c = c
        self.id = id
        self.crypto = crypto

    def run(self):
        with closing(self.c) as c:
            iv = self.crypto.recv_iv(c)
            #if iv:
                #print("iv received=",iv)
            while True:
                #c.sendall(b"server here")
                msg=c.recv(1024)
                if msg:
                    plaintext_padded = self.crypto.dec(iv, msg)
                    plaintext = self.crypto.unpad(plaintext_padded)
                    sys.stdout.buffer.write(b'[ ')
                    sys.stdout.buffer.write(bytes(str(self.id), encoding='utf8'))
                    sys.stdout.buffer.write(b' ]: ')
                    sys.stdout.buffer.write(plaintext)
                    sys.stdout.buffer.write(b'\n')
                    sys.stdout.buffer.flush()
                else:
                    print("=[",self.id,"]=", "Disconnected")
                    break

class Server(object):
    def run(self):
        order_number=0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            print('Server started!')
            print('Waiting for clients...')
            s.listen()
            while True:
                try:
                    c, addr = s.accept()  # Establish connection with client.
                    print("[",order_number,"]", "Connected")
                    thr = ServerThread(type(self), c, order_number)
                    thr.start()
                    order_number=order_number+1
                except KeyboardInterrupt:
                    print("Shutting down server")
                    s.close()
                    break

class RC4(Server):
    @staticmethod
    def dec(iv,p):
        return ARC4.new(KEY).decrypt(p)

    @staticmethod
    def unpad(p):
        return p

    @staticmethod
    def recv_iv(s):
        ...

class AES_CBC_NoPadding(Server):
    @staticmethod
    def recv_iv(s):
        return s.recv(16)

    @staticmethod
    def unpad(p):
        return p

    @staticmethod
    def dec(iv, p):
        ciph = AES.new(KEY, AES.MODE_CBC, iv)
        return ciph.decrypt(p)

class AES_CBC_PKCS5Padding(AES_CBC_NoPadding):
    @staticmethod
    def unpad(p):
        return p[:-p[-1]]

class AES_CFB8_NoPadding(Server):
    @staticmethod
    def recv_iv(s):
        return s.recv(16)

    @staticmethod
    def unpad(p):
        return p

    @staticmethod
    def dec(iv, p):
        ciph = AES.new(KEY, AES.MODE_CFB, iv=iv, segment_size=8)
        return ciph.decrypt(p)

class AES_CFB8_PKCS5Padding(AES_CFB8_NoPadding):
    @staticmethod
    def unpad(p):
        return p[:-p[-1]]

class AES_CFB_NoPadding(Server):
    @staticmethod
    def recv_iv(s):
        return s.recv(16)

    @staticmethod
    def unpad(p):
        return p

    @staticmethod
    def dec(iv, p):
        ciph = AES.new(KEY, AES.MODE_CFB, iv, segment_size=128)
        return ciph.decrypt(p)

class AES_CFB_PKCS5Padding(AES_CFB_NoPadding):
    @staticmethod
    def unpad(p):
        return p[:-p[-1]]
