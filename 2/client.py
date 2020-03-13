import socket
import sys
from Crypto.Cipher import ARC4
import string
import random 

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45676  # The port used by the server
#KEY = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
KEY="very secret key"

def enc(key,p):
		return ARC4.new(key).encrypt(p)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((HOST, PORT))
	while True:
		#msg=input()
		msg=""
		char=""
		while char != '\n':
			char=sys.stdin.read(1)
			msg=msg+char
		#print("msg=",msg)
			
		
		if msg == "exit":
			s.close()
			break
		else:
			#print("msg=",msg[:-1])
			stream=msg[:-1]
			cipher_stream=enc(KEY,stream) #bytearray
			#print(cipher_stream)
			#for byte in cipher_stream:
				#s.sendall(byte.to_bytes(1, sys.byteorder))
			s.sendall(cipher_stream)
		

