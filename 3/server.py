import socket
import threading
import string
import random 
import sys

from contextlib import closing
from Crypto.Cipher import ARC4

HOST = '127.0.0.1'  #localhost
PORT = 45676 #non-privileged ports are > 1023
#KEY = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
KEY= b"very secret key"

class ServerThread(threading.Thread):
    def __init__(self,crypto,c,id):
        super().__init__()
        self.c = c
        self.id = id
        self.crypto = crypto

    def run(self):
        with closing(self.c) as c:
            iv = self.crypto.recv_iv(c)
            while True:
                #c.sendall(b"server here")
                msg=c.recv(1024)
                if msg:
                    plaintext = self.crypto.dec(iv, msg)
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
    def recv_iv(s):
        ...
