import socket
import sys
import string
import random 
import hmac
import json
import base64

import app

from keyexchange import S2SHelper, SignHelper
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Hash import SHA256
from Crypto import Random

class Client(object):
    def serialize(self, o):
        return json.dumps(o).encode()

    def deserialize(self, x):
        return json.loads(x.decode('utf8'))

    def key_exchange(self, c):
        ...

    def pad(self, p):
        return p

    def unpad(self, p):
        return p

    def enc(self, p, y=None):
        return self.serialize(p)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((app.HOST, app.PORT))
            try:
                print('<begun key exchange>')
                self.key_exchange(s)
                print('<key exchange successful>')
            except Exception:
                print('<key exchange failed>')
                return
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
        self.user = sys.argv[2]
        self.k1 = None
        self.k2 = None
        self.seq = 0

    def key_exchange(self, c):
        s2s = S2SHelper(f'users/{self.user}.pem')
        msg = s2s.get_encoded_symmetric()
        msg['user'] = self.user
        c.sendall(self.serialize(msg))

        msg = self.deserialize(c.recv(4096))
        partner_symmetric = s2s.decode_symmetric(msg)

        key = s2s.compute_shared_secret(partner_symmetric)
        self.k1 = SHA256.new(key+b'1').digest()[:16]
        self.k2 = SHA256.new(key+b'2').digest()[:16]

        challenge = s2s.decode_challenge(self.dec(msg))
        k = SignHelper(f'server.cert')

        if not k.verify(challenge, partner_symmetric, s2s.get_symmetric()):
            raise ValueError('failed to verify signature')

        our_symmetric, challenge = s2s.get_encoded_unencrypted_challenge(partner_symmetric)
        c.sendall(self.enc(challenge, our_symmetric))

    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)

    def unpad(self, p):
        return p[:-p[-1]]

    def dec(self, p):
        p = self.deserialize(p) if type(p) != dict else p
        seq = self.seq.to_bytes(8, 'big')
        self.seq = (self.seq + 1) & 0xffffffffffffffff
        mac = hmac.new(self.k2, p['cryptogram'].encode()+seq, SHA256.new).hexdigest()
        if not hmac.compare_digest(p['mac'], mac):
            raise ValueError('invalid mac')
        ctr_d = Counter.new(64, prefix=base64.decodebytes(p['iv'].encode()))
        ciph = AES.new(self.k1, AES.MODE_CTR, counter=ctr_d)
        return self.unpad(ciph.decrypt(base64.decodebytes(p['cryptogram'].encode())))

    def enc(self, p, y=None):
        iv = Random.new().read(8)
        ctr_e = Counter.new(64, prefix=iv)
        ciph = AES.new(self.k1, AES.MODE_CTR, counter=ctr_e)
        seq = self.seq.to_bytes(8, 'big')
        self.seq = (self.seq + 1) & 0xffffffffffffffff
        cryptogram = str(base64.encodebytes(ciph.encrypt(self.pad(p))), 'utf8')
        mac = hmac.new(self.k2, cryptogram.encode()+seq, SHA256.new).hexdigest()
        msg = {
            'iv': str(base64.encodebytes(iv), 'utf8'),
            'mac': mac,
            'cryptogram': cryptogram,
        }
        if y != None:
            msg['y'] = str(y, 'utf8')
        return self.serialize(msg)
