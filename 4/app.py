import sys

import client
import server

if __name__ == '__main__':
    backends = {
        'Client': client.AES_CTR_NoPadding,
        'Server': server.AES_CTR_NoPadding,
    }
    backend = backends.get(sys.argv[1]) if len(sys.argv) == 2 else None
    if not backend:
        print(f'Usage: python {sys.argv[0]} <backend>')
        print('Backends:')
        for b in backends.keys():
            print(f'\t{b}')
        sys.exit(1)
    instance = backend()
    instance.run()