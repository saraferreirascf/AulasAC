import sys
import socket
import pickle

from ssl import SSLContext, PROTOCOL_TLSv1_2

def main():
    # read user id
    print('Enter the user id:')
    userid = sys.stdin.readline()[:-1].encode()

    # read card pin
    print('Enter the pin:')
    pin = sys.stdin.readline()[:-1].encode()

    ctx = SSLContext(PROTOCOL_TLSv1_2)
    ctx.load_verify_locations('cert.pem')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        with ctx.wrap_socket(sock, server_hostname='localhost') as c:
            # connect
            c.connect(('localhost', 2500))

            # send user id and pin
            msg = pickle.dumps(dict(userid=userid, pin=pin))
            c.sendall(msg)

            # read 2fa token
            print('Enter the 2fa token:')
            token = sys.stdin.readline()[:-1]

            # send token
            msg = pickle.dumps(dict(token=token))
            c.sendall(msg)

if __name__ == '__main__':
    main()
