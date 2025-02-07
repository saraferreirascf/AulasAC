# yet another crypto lib, but it's necessary, because
# pycrypto can't handle certificates too well
from OpenSSL import crypto

from Crypto.Util.asn1 import DerSequence
from Crypto.PublicKey import RSA
from binascii import a2b_base64
from pathlib import Path

class Certificate(object):
    def __init__(self, path='', pem='', parse=True):
        if path:
            pem = Path(path).read_bytes()
        i = pem.find(b'-----BEGIN CERTIFICATE-----')
        assert i != -1
        pem = pem[i:]
        self.pem = pem
        self.cert = None
        if parse:
            self._parse_cert()

    def _parse_cert(self):
        lines = self.pem.replace(b' ',b'').split()
        der = a2b_base64(b''.join(lines[1:-1]))
        self.cert = DerSequence()
        self.cert.decode(der)

    def public_key(self):
        if not self.cert:
            self._parse_cert()
        subject = DerSequence()
        subject.decode(self.cert[0])
        return RSA.import_key(subject[6])

def load_chain(path='', parse=True):
    chain = []
    pem = Path(path).read_bytes()

    begin = b'-----BEGIN CERTIFICATE-----'
    end = b'-----END CERTIFICATE-----'

    while True:
        a = pem.find(begin)
        if a == -1:
            return chain
        b = pem[a:].find(end)
        cert_pem = pem[a:][:b+len(end)+1]
        chain.append(Certificate(pem=cert_pem, parse=parse))
        pem = pem[a:][b+len(end)+1:]

# http://www.yothenberg.com/validate-x509-certificate-in-python/
def verify_chain_of_trust(cert, trusted_certs):
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cert.pem)

    # Create and fill a X509Sore with trusted certs
    store = crypto.X509Store()
    for trusted_cert in trusted_certs:
        trusted_cert = crypto.load_certificate(crypto.FILETYPE_PEM, trusted_cert.pem)
        store.add_cert(trusted_cert)

    # Create a X590StoreContext with the cert and trusted certs
    # and verify the the chain of trust
    store_ctx = crypto.X509StoreContext(store, certificate)
    # Returns None if certificate can be validated
    result = store_ctx.verify_certificate()

    return result == None
