import socket
import sys
from Crypto.Cipher import ARC4

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45676   # The port used by the server
KEY = "super secret key"

def enc(key,p):
		return ARC4.new(key).encrypt(p)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((HOST, PORT))
	while True:
		msg=input()
		if msg == "exit":
			s.close()
			break
		else:
			s.sendall(enc(KEY,msg))
		

