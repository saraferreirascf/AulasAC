import socket
import sys


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45678    # The port used by the server


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
    	msg=input()
    	if msg == "exit":
    		s.close()
    		break
    	else:
    		s.sendall(msg.encode('utf-8'))


