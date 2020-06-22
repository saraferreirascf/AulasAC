import sys
import pyotp
import qrcode
import socket
import pickle

from pathlib import Path
from baseconv import base56
from threading import Thread, Lock
from ssl import SSLContext, PROTOCOL_TLSv1_2

from Crypto.Hash import BLAKE2b
from Crypto.Random import get_random_bytes

class SharedState(object):
    def __init__(self, load):
        self.path = Path(load)
        self.lock = Lock()
        try:
            self.data = pickle.loads(self.path.read_bytes())
        except FileNotFoundError:
            self.data = {}

    def save(self):
        with self.lock:
            data = pickle.dumps(self.data)
        self.path.write_bytes(data)

    def new(self, user, pin):
        salt = generate_pin_salt()
        userid = generate_user_id(user, salt)
        pinhash = hash_pin(pin, salt)
        shared_secret = pyotp.random_base32()
        totp = pyotp.TOTP(shared_secret)
        url = totp.provisioning_uri('banco@xp.to', issuer_name='Banco XPTO')
        qrcode.make(url).show()
        with self.lock:
            self.data[userid] = (salt, pinhash, shared_secret)
        return userid

    def check_pin(self, userid, pin):
        with self.lock:
            salt, pinhash, _ = self.data[userid]
        return hash_equal(pinhash, hash_pin(pin, salt))

    def check_2fa(self, userid, token):
        with self.lock:
            _, _, shared_secret = self.data[userid]
        return pyotp.TOTP(shared_secret).verify(token)

class SockHandler(Thread):
    def __init__(self, s, addr, state):
        super().__init__()
        self.s = s
        self.addr = addr
        self.state = state

    def run(self):
        with self.s as c:
            # initial payload contains user id
            # and the user's pin code
            msg = pickle.loads(c.recv(1024))

            # retrieve user id
            userid = msg.get('userid')
            if not userid:
                print(f'{self.addr} : no user id')
                print(f'{self.addr} : disconnected')
                return

            # retrieve pin
            pin = msg.get('pin')
            if not pin:
                print(f'{self.addr} : no pin')
                print(f'{self.addr} : disconnected')
                return

            # validate pin
            if not self.state.check_pin(userid, pin):
                print(f'{self.addr} : invalid pin: {pin}: for user: {userid}')
                print(f'{self.addr} : disconnected')
                return

            # receive token
            msg = pickle.loads(c.recv(1024))
            token = msg.get('token')
            if not token:
                print(f'{self.addr} : no token')
                print(f'{self.addr} : disconnected')
                return

            # verify token
            if not self.state.check_2fa(userid, token):
                print(f'{self.addr} : token expired')
                print(f'{self.addr} : disconnected')
                return

            # we're good to go!
            print(f'{self.addr} : authenticated')
            print(f'{self.addr} : disconnected')

def hash_equal(h1, h2):
    result = 0
    for i in range(len(h1)):
        result |= h1[i] ^ h2[i]
    return result == 0

def hash_pin(pin, salt):
    state = BLAKE2b.new()
    state.update(pin)
    state.update(salt)
    return state.digest()

def generate_pin_salt():
    return get_random_bytes(512)

def generate_user_id(name, salt):
    state = BLAKE2b.new()
    state.update(name)
    state.update(salt)
    digest = state.digest()
    num = int.from_bytes(digest, 'little')
    return base56.encode(num).encode()

def main_new_user():
    db = SharedState('users.pickle')
    print('Enter the username:')
    name = sys.stdin.readline()[:-1].encode()
    print('Enter the pin:')
    pin = sys.stdin.readline()[:-1].encode()
    userid = db.new(name, pin)
    print(f'Generated user id: {str(userid, "utf8")}')
    db.save()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'gen':
        main_new_user()
        return

    ctx = SSLContext(PROTOCOL_TLSv1_2)
    ctx.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    listener.bind(('', 1500))
    listener.listen(8)

    db = SharedState('users.pickle')

    while True:
        try:
            s, addr = listener.accept()
            print(f'{addr} : connected')
            s = ctx.wrap_socket(s, server_side=True)
            SockHandler(s, addr, db).start()
        except OSError:
            continue
        except KeyboardInterrupt:
            print('*Windows shutdown jingle*')
            break
        finally:
            listener.close()

if __name__ == '__main__':
    main()
