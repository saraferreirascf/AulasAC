import socket
import threading
import sys
import hashlib
import hmac
import json

from contextlib import closing
from Crypto.Util import Counter
from Crypto.Cipher import AES

HOST = '127.0.0.1'  #localhost
PORT = 45676 #non-privileged ports are > 1023
KEY = b"very secret key"
K1 = hashlib.sha256(KEY+b'1').digest()[:16]
K2 = hashlib.sha256(KEY+b'2').digest()[:16]

class ServerThread(threading.Thread):
    def __init__(self,crypto,c,id):
        super().__init__()
        self.c = c
        self.id = id
        self.crypto = crypto
        self.seq = 0

    def run(self):
        with closing(self.c) as c:
            while True:
                msg = c.recv(1024) #pin
                if msg:
                    try:
                        plaintext = self.crypto.dec(msg, self.seq)
                        self.seq = (self.seq + 1) & 0xffffffffffffffff
                        sys.stdout.buffer.write(b'[ ')
                        sys.stdout.buffer.write(bytes(str(self.id), encoding='utf8'))
                        sys.stdout.buffer.write(b' ]: ')
                        sys.stdout.buffer.write(b' PIN inserted: ')
                        sys.stdout.buffer.write(plaintext) #verificar PIN
                    except ValueError:
                        sys.stdout.buffer.write(b'[ ')
                        sys.stdout.buffer.write(bytes(str(self.id), encoding='utf8'))
                        sys.stdout.buffer.write(b' (error) ]: invalid mac')
                    finally:
                        sys.stdout.buffer.write(b'\n')
                        sys.stdout.buffer.flush()
                else:
                    print("=[",self.id,"]=", "Disconnected")
                    break

class Server(object):
    def deserialize(self, x):
        return json.loads(x.decode('utf8'))

    def run(self):
        order_number=0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            print('ATM started!')
            #print('Waiting for clients...')
            s.listen()
            while True:
                try:
                    c, addr = s.accept()  # Establish connection with client.
                    print("[",order_number,"]", "Connected")
                    thr = ServerThread(self, c, order_number)
                    thr.start()
                    order_number+=1
                except KeyboardInterrupt:
                    print("Shutting down server")
                    s.close()
                    break

class SafeServer(Server):
    def unpad(self, p):
        return p[:-p[-1]]

    def dec(self, p, seq):
        p = self.deserialize(p)
        seq = seq.to_bytes(8, 'big')
        mac = hmac.new(K2, p['cryptogram'].encode()+seq, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(p['mac'], mac):
            raise ValueError('invalid mac')
        ctr_d = Counter.new(64, prefix=bytes.fromhex(p['iv']))
        ciph = AES.new(K1, AES.MODE_CTR, counter=ctr_d)
        return self.unpad(ciph.decrypt(bytes.fromhex(p['cryptogram'])))
