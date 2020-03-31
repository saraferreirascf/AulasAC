import socket
import threading
import sys
import hashlib
import hmac
import json
import base64

from keyexchange import DiffieHellman
from contextlib import closing
from Crypto.Util import Counter
from Crypto.Cipher import AES

HOST = '127.0.0.1'  #localhost
PORT = 45676 #non-privileged ports are > 1023

class ServerThread(threading.Thread):
    def __init__(self,crypto,c,id):
        super().__init__()
        self.c = c
        self.id = id
        self.crypto = crypto
        self.seq = 0

    def run(self):
        with closing(self.c) as c:
            print(f'[ {self.id} ]i begun key exchange')
            self.crypto.key_exchange(self.id, c)
            print(f'[ {self.id} ]i key exchange successful')
            while True:
                msg = c.recv(1024)
                if msg:
                    try:
                        plaintext = self.crypto.dec(self.id, msg, self.seq)
                        self.seq = (self.seq + 1) & 0xffffffffffffffff
                        sys.stdout.buffer.write(b'[ ')
                        sys.stdout.buffer.write(bytes(str(self.id), encoding='utf8'))
                        sys.stdout.buffer.write(b' ]: ')
                        sys.stdout.buffer.write(plaintext)
                    except ValueError:
                        sys.stdout.buffer.write(b'[ ')
                        sys.stdout.buffer.write(bytes(str(self.id), encoding='utf8'))
                        sys.stdout.buffer.write(b' ]!  invalid mac')
                    finally:
                        sys.stdout.buffer.write(b'\n')
                        sys.stdout.buffer.flush()
                else:
                    print("=[",self.id,"]=", "Disconnected")
                    break

class Server(object):
    def serialize(self, o):
        return json.dumps(o).encode()

    def deserialize(self, x):
        return json.loads(x.decode('utf8'))

    def key_exchange(self, id, c):
        ...

    def dec(self, id, p, seq):
        return self.deserialize(p)

    def unpad(self, p):
        return p

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
                    print("[",order_number,"]i", "connected")
                    thr = ServerThread(self, c, order_number)
                    thr.start()
                    order_number+=1
                except KeyboardInterrupt:
                    print("Shutting down server")
                    s.close()
                    break

class SafeServer(Server):
    def __init__(self):
        self.keys = {}
        self.dh = DiffieHellman()

    def key_exchange(self, id, c):
        msg = c.recv(4096)
        c.sendall(self.serialize(self.dh.get_public()))
        key = self.dh.compute_shared_secret(self.deserialize(msg))
        k1 = hashlib.sha256(key+b'1').digest()[:16]
        k2 = hashlib.sha256(key+b'2').digest()[:16]
        self.keys[id] = (k1, k2) # TODO: synchronize this with a mutex

    def unpad(self, p):
        return p[:-p[-1]]

    def dec(self, id, p, seq):
        k1, k2 = self.keys[id]
        p = self.deserialize(p)
        seq = seq.to_bytes(8, 'big')
        mac = hmac.new(k2, p['cryptogram'].encode()+seq, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(p['mac'], mac):
            raise ValueError('invalid mac')
        ctr_d = Counter.new(64, prefix=base64.decodebytes(p['iv'].encode()))
        ciph = AES.new(k1, AES.MODE_CTR, counter=ctr_d)
        return self.unpad(ciph.decrypt(base64.decodebytes(p['cryptogram'].encode())))
