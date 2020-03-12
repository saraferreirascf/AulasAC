import socket
# import thread module 
from _thread import *
import threading 


def threaded(c,addr):
    while True:
        msg=c.recv(1024)
        if msg:
            print("[",order_numbers[addr[1]],"]:",msg.decode('utf-8'))
        else:
            print("=[",order_numbers[addr[1]],"]=", "Disconnected")
            break

    c.close()


HOST = '127.0.0.1'  #localhost
PORT = 45678      #non-privileged ports are > 1023

order_number=0
order_numbers={}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print('Server started!')
    print('Waiting for clients...')
    s.listen()
 
    while True:
        c, addr = s.accept()  # Establish connection with client.
        
        print("[",order_number,"]", "Connected")
        order_numbers[addr[1]]=order_number
        order_number=order_number+1
        start_new_thread(threaded, (c,addr))

        
    s.close()

    