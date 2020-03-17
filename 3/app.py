import sys

import client
import server

if __name__ == '__main__':
    backends = {
        # RC4 encryption
        'Client_RC4': client.RC4,
        'Server_RC4': server.RC4,
        # AES in CBC mode with no particular padding scheme
        'Client_AES_CBC_NoPadding': client.AES_CBC_NoPadding,
        'Server_AES_CBC_NoPadding': server.AES_CBC_NoPadding,
    }
    backend = backends.get(sys.argv[1]) if len(sys.argv) == 2 else None
    if not backend:
        backends = '|'.join(backends.keys())
        print(f'Usage: python {sys.argv[0]} <{backends}>')
        sys.exit(1)
    instance = backend()
    instance.run()
