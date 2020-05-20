import socket
import threading
import sys
import hmac
import json
import base64

import app

from keyexchange import S2SHelper, SignHelper
from contextlib import closing
from Crypto.Util import Counter
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random

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
            #try:
            self.crypto.key_exchange(self.id, self.seq, c)
            #except ValueError:
            #    print(f'[ {self.id} ]! key exchange failed, closing connection')
            #    return
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
                        sys.stdout.buffer.write(b' ]! invalid mac')
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

    def pad(self, p):
        return p

    def unpad(self, p):
        return p

    def run(self):
        order_number=0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((app.HOST, app.PORT))
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

        s2s = S2SHelper('server.pem')
        user = s2s.decode_user(msg)
        partner_symmetric = s2s.decode_symmetric(msg)

        key = s2s.compute_shared_secret(partner_symmetric)
        k1 = SHA256.new(key+b'1').digest()[:16]
        k2 = SHA256.new(key+b'2').digest()[:16]
        self.session_keys[id] = (k1, k2) # TODO: synchronize this with a mutex

        our_symmetric, challenge = s2s.get_encoded_unencrypted_challenge(partner_symmetric)
        c.sendall(self.enc(id, challenge, seq, our_symmetric))

        challenge = s2s.decode_challenge(self.dec(id, c.recv(4096), seq+1))
        k = SignHelper(f'users/{user}.pub')

        if not k.verify(challenge, partner_symmetric, s2s.get_symmetric()):
            raise ValueError('failed to verify signature')

    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)

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

    def enc(self, id, p, seq, y=None):
        k1, k2 = self.session_keys[id]
        iv = Random.new().read(8)
        ctr_e = Counter.new(64, prefix=iv)
        ciph = AES.new(k1, AES.MODE_CTR, counter=ctr_e)
        seq = seq.to_bytes(8, 'big')
        cryptogram = str(base64.encodebytes(ciph.encrypt(self.pad(p))), 'utf8')
        mac = hmac.new(k2, cryptogram.encode()+seq, SHA256.new).hexdigest()
        msg = {
            'iv': str(base64.encodebytes(iv), 'utf8'),
            'mac': mac,
            'cryptogram': cryptogram,
        }
        if y != None:
            msg['y'] = str(y, 'utf8')
        return self.serialize(msg)
