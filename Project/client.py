import sys
import socket
import pickle

from pathlib import Path
from Crypto.Hash import BLAKE2b
from ssl import SSLContext, PROTOCOL_TLSv1_2

def hash_pin(pin, salt):
    state = BLAKE2b.new()
    state.update(pin)
    state.update(salt)
    return state.digest()

def main():
    # load db
    db = pickle.loads(Path('users.pickle').read_bytes())

    # read user id
    print('Enter the user id:')
    userid = sys.stdin.readline()[:-1].encode()

    # read card pin
    print('Enter the pin:')
    pin = sys.stdin.readline()[:-1].encode()

    # fetch secret
    _, _, _, pin_salt = db[userid]
    pin = hash_pin(pin, pin_salt)

    # start server
    ctx = SSLContext(PROTOCOL_TLSv1_2)
    ctx.load_verify_locations('cert.pem')

    ok = 'ok'
    err = 'err'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        with ctx.wrap_socket(sock, server_hostname='localhost') as c:
            # connect
            c.connect(('localhost', 2500))

            # send user id and pin
            msg = pickle.dumps(dict(userid=userid, pin=pin))
            c.sendall(msg)

            # check if ok
            msg = pickle.loads(c.recv(1024))
            if not msg[ok]:
                print(msg[err])
                return

            # read 2fa token
            print('Enter the 2fa token:')
            token = sys.stdin.readline()[:-1]

            # send token
            msg = pickle.dumps(dict(token=token))
            c.sendall(msg)

            # check if ok
            msg = pickle.loads(c.recv(1024))
            if not msg[ok]:
                print(msg[err])
                return

if __name__ == '__main__':
    main()
