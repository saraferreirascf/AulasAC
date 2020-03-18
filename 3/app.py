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
        # AES in CBC mode with PKCS5 padding
        'Client_AES_CBC_PKCS5Padding': client.AES_CBC_PKCS5Padding,
        'Server_AES_CBC_PKCS5Padding': server.AES_CBC_PKCS5Padding,
        # AES in CFB 8 bits mode with no particular padding scheme
        'Client_AES_CFB8_NoPadding': client.AES_CFB8_NoPadding,
        'Server_AES_CFB8_NoPadding': server.AES_CFB8_NoPadding,
        # AES in CFB 8 bits mode with PKCS5 padding
        'Client_AES_CFB8_PKCS5Padding': client.AES_CFB8_PKCS5Padding,
        'Server_AES_CFB8_PKCS5Padding': server.AES_CFB8_PKCS5Padding,
    }
    backend = backends.get(sys.argv[1]) if len(sys.argv) == 2 else None
    if not backend:
        backends = '|'.join(backends.keys())
        print(f'Usage: python {sys.argv[0]} <{backends}>')
        sys.exit(1)
    instance = backend()
    instance.run()
