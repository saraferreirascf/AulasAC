import socket
# import thread module 
from _thread import *
import threading 
from Crypto.Cipher import ARC4
import string
import random 
import sys

def threaded(c,addr):
    while True:
        #c.sendall(b"server here")
        msg=c.recv(1024)

        if msg:
            print("[",order_numbers[addr[1]],"]:",end=' ')
            #print(dec(KEY,msg).decode())
            for byte in dec(KEY,msg):
                sys.stdout.write(str(chr(byte)))
                sys.stdout.flush()
            print()
        else:
            print("=[",order_numbers[addr[1]],"]=", "Disconnected")
            break

    c.close()

def dec(key,msg):
		return ARC4.new(key).decrypt(msg)


HOST = '127.0.0.1'  #localhost
PORT = 45676 #non-privileged ports are > 1023
#KEY = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
KEY= "very secret key"

order_number=0
order_numbers={}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print('Server started!')
    print('Waiting for clients...')
    s.listen()
    
    while True:
        try:
            c, addr = s.accept()  # Establish connection with client.
            print("[",order_number,"]", "Connected")
            order_numbers[addr[1]]=order_number
            order_number=order_number+1
            start_new_thread(threaded, (c,addr))

        except KeyboardInterrupt:
            print("Shutting down server")
            s.close()
            break
        
    s.close()
