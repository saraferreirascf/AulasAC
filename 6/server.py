import os
import socket
import threading
import sys
import hmac
import json
import base64

from keyexchange import S2SHelper, SignHelper
from contextlib import closing
from Crypto.Util import Counter
from Crypto.Hash import SHA256
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
            self.crypto.key_exchange(self.id, self.seq, c)
            self.seq = (self.seq + 2) & 0xffffffffffffffff
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

    def key_exchange(self, id, seq, c):
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
        self.session_keys = {}

    # https://en.wikipedia.org/wiki/Station-to-Station_protocol
    def key_exchange(self, id, seq, c):
        msg = self.deserialize(c.recv(4096))

        key = dh.compute_shared_secret(self.deserialize(msg))
        k1 = SHA256.new(key+b'1').digest()[:16]
        k2 = SHA256.new(key+b'2').digest()[:16]

        s2s = S2SHelper('server.pem')
        user = s2s.decode_user(msg)
        partner_symmetric = s2s.decode_symmetric(msg)

        challenge = s2s.get_encoded_unencrypted_challenge(partner_symmetric)
        c.sendall(self.serialize(self.enc(challenge, seq, k1, k2)))

        msg = self.dec(id, c.recv(4096), seq+1)
        partner_symmetric, challenge = s2s.decode_challenge(msg)

        k = SignHelper(os.sep.join(['users', user]))
        # TODO: verify key + finish client side of key exchange

        self.session_keys[id] = (k1, k2) # TODO: synchronize this with a mutex

    def unpad(self, p):
        return p[:-p[-1]]

    def dec(self, id, p, seq):
        k1, k2 = self.session_keys[id]
        p = self.deserialize(p)
        seq = seq.to_bytes(8, 'big')
        mac = hmac.new(k2, p['cryptogram'].encode()+seq, SHA256.new).hexdigest()
        if not hmac.compare_digest(p['mac'], mac):
            raise ValueError('invalid mac')
        ctr_d = Counter.new(64, prefix=base64.decodebytes(p['iv'].encode()))
        ciph = AES.new(k1, AES.MODE_CTR, counter=ctr_d)
        return self.unpad(ciph.decrypt(base64.decodebytes(p['cryptogram'].encode())))

    def enc(self, p, seq, k1, k2):
        iv = Random.new().read(8)
        ctr_e = Counter.new(64, prefix=iv)
        ciph = AES.new(k1, AES.MODE_CTR, counter=ctr_e)
        seq = seq.to_bytes(8, 'big')
        cryptogram = str(base64.encodebytes(ciph.encrypt(self.pad(p))), 'utf8')
        mac = hmac.new(k2, cryptogram.encode()+seq, SHA256.new).hexdigest()
        return self.serialize({
            'iv': str(base64.encodebytes(iv), 'utf8'),
            'mac': mac,
            'cryptogram': cryptogram,
        })
