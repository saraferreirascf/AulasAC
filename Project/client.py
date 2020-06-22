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

def splash_screen():
    print()
    print()
    print("  /***************************\\")
    print("  |            ATM            |")
    print("  |           a.k.a.          |")
    print("  |       All The Money       |")
    print("  \\***************************/")
    print()
    print()

def main(port=None):
    # load db
    db = pickle.loads(Path('users.pickle').read_bytes())

    # read user id
    splash_screen()
    print('Assume the role of a card reader, and type the card id, will you?')
    userid = sys.stdin.readline()[:-1].encode()

    # read card pin
    print('\nGood, good... Now punch in the pin:')
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
            print('\nDialing backend...')

            # connect
            c.connect(('localhost', port))

            print('...All good!\n')

            # send user id and pin
            msg = pickle.dumps(dict(userid=userid, pin=pin))
            c.sendall(msg)

            # check if ok
            msg = pickle.loads(c.recv(1024))
            if not msg[ok]:
                print(f'Error: {msg[err]}')
                return

            # read 2fa token
            print('Punch in your 2fa token:')
            token = sys.stdin.readline()[:-1]

            # send token
            msg = pickle.dumps(dict(token=token))
            c.sendall(msg)

            # check if ok
            msg = pickle.loads(c.recv(1024))
            if not msg[ok]:
                print(f'Error: {msg[err]}')
                return

            print(f'\n\nAutheticated as: {str(userid, "utf8")}')
            print('Alright, time to order some Uber Eats(tm)!')
