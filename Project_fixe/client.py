import socket
import sys
import string
import random 
import hmac
import json
import time
import hashlib

from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 45676  # The port used by the server
KEY = b"very secret key"
K1 = hashlib.sha256(KEY+b'1').digest()[:16]
K2 = hashlib.sha256(KEY+b'2').digest()[:16]
correct=False

class Client(object):
   


    def serialize(self, o):
        return json.dumps(o).encode()

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            while True:
                try:
                    card_number=input("Enter your card number please: ")

                    with open("accounts.txt", "r") as file:
                        for line in file:
                            if card_number in line:
                                correct=True
                                pin_txt=line.split(" ")[1]
                                print("Pin found in file: "+pin_txt)

                    if correct==True:
                        time.sleep(5) #inserir animacao de estar à espera com 3 pontinhos?
                        print("Card inserted!")
                        print()
                        print()

                        print("*******************************")
                        print("|              ATM            |")
                        print("*******************************")
                        print()
                        print()
                        print("Insert your pin please: ")
                        msg=sys.stdin.buffer.readline()[:-1] #aparecer * em vez dos numeros?
                        pin=msg.decode("utf-8")
                        print("Pin inserted= "+pin)
                        print()
                        print("checking pin...") #Fazer verificacao melhor né
                        time.sleep(5)
                        print(pin)
                        print(pin_txt)
                        print(pin==pin_txt) #Porque que isto da falso broooo
                        if pin==pin_txt :
                            print("Pin correct! Welcome :)")
                        else:
                            print("Pin wrong!")
                            s.close()





                    else:
                        print("This card number does not exists")
                        s.close()

                except KeyboardInterrupt:
                    s.close()
                    break
                if msg == b"exit":
                    s.close()
                    break
                else:
                    packet = self.enc(msg)
                    s.sendall(packet)
                    
class SafeClient(Client):
    def __init__(self):
        self.seq = 0

    def pad(self, p):
        n = 16 - len(p)%16
        return p + bytes([n] * n)

    def enc(self, p):
        iv = Random.new().read(8)
        ctr_e = Counter.new(64, prefix=iv)
        ciph = AES.new(K1, AES.MODE_CTR, counter=ctr_e)
        seq = self.seq.to_bytes(8, 'big')
        self.seq = (self.seq + 1) & 0xffffffffffffffff
        cryptogram = ciph.encrypt(self.pad(p)).hex()
        mac = hmac.new(K2, cryptogram.encode()+seq, hashlib.sha256).hexdigest()
        return self.serialize({
            'iv': iv.hex(),
            'mac': mac,
            'cryptogram': cryptogram,
        })
        
