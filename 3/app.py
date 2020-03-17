import sys

import client
import server

if sys.argv[1]=="Client_RC4":
    client.RC4().run()
elif sys.argv[1]=="Server_RC4":
    server.RC4().run()
