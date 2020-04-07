import sys

import client
import server

HOST = '127.0.0.1'  #localhost
PORT = 45678 #non-privileged ports are > 1023

if __name__ == '__main__':
    backends = {
        'Client': client.SafeClient,
        'Server': server.SafeServer,
    }
    backend = backends.get(sys.argv[1]) if len(sys.argv) >= 2 else None
    if not backend:
        print(f'Usage: python {sys.argv[0]} <backend> [<user>]')
        print('Backends:')
        for b in backends.keys():
            print(f'\t{b}')
        sys.exit(1)
    try:
        instance = backend()
        instance.run()
    except IndexError:
        print(f'Error: missing user argument')
        sys.exit(1)
