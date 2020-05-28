from Crypto.Util.asn1 import DerSequence
from Crypto.PublicKey import RSA
from binascii import a2b_base64

class Certificate(object):
    def __init__(self, path=''):
        with open(path, 'rb') as f:
            pem = f.read()
            lines = pem.replace(b' ',b'').split()
            der = a2b_base64(b''.join(lines[1:-1]))
            self.cert = DerSequence()
            self.cert.decode(der)

    def public_key(self):
        subject = DerSequence()
        subject.decode(self.cert[0])
        return RSA.import_key(subject[6])
