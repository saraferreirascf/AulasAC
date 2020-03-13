# Import modules
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter
import sys
import random
import string


def keygen(keyfile):
    #key=bytearray(b"very nice key")
    KEY = "".join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    #key="12345"
    #pad = '# constant pad for short keys ##'
    #keye = (key + pad)[:32]
    f= open(keyfile,"w+")
    f.write(key)
    f.close()


###################### ENCRYPT ##############################

def enc(keyfile,infile,outfile):
    #print("Entrei na funcao de enc ehehe")
    random_generator = Random.new()
    IV = random_generator.read(8)
    #print("IV=",IV)
    fi= open("IV.txt","wb")
    fi.write(IV)
    fi.close()

    f= open(keyfile,"r")
    keye=f.read()
    f.close()

    ctr_e = Counter.new(64, prefix=IV)
    encryptor = AES.new(keye, AES.MODE_CTR, counter=ctr_e)

    fp = open(infile, "r")
    plaintext = fp.read()
    #print(plaintext)
    fp.close()

    ciphertext = encryptor.encrypt(plaintext)


    fc= open(outfile,"wb")
    fc.write(ciphertext)
    fc.close()

###################### DECRYPT ##############################


def dec(keyfile,infile,outfile):
    print("Entrei na funcao de dec ehehe")
    
    f= open(keyfile,"r")
    keyd=f.read()
    f.close()
    #keyd = (key + pad)[:32]
    fi= open("IV.txt","rb")
    IV=fi.read()
    fi.close()
    #print("IV=",IV)
    #restarts from the beginning

    ctr_d = Counter.new(64, prefix=IV)

    # Create decryptor, then decrypt and print decoded text
    decryptor = AES.new(keyd, AES.MODE_CTR, counter=ctr_d)
    fp = open(infile, "rb")
    ciphertext = fp.read()
    fp.close()
    #print("Ciphertext do ficheiro:",ciphertext)
    decoded_text = decryptor.decrypt(ciphertext)
    #print(decoded_text.decode("utf-8"))
    fc= open(outfile,"w")
    fc.write(decoded_text.decode("utf-8"))
    fc.close()


if sys.argv[1]=="-genkey":
	keygen(sys.argv[2])
if sys.argv[1]=="-enc":
	enc(sys.argv[2],sys.argv[3],sys.argv[4])
if sys.argv[1]=="-dec":
	dec(sys.argv[2],sys.argv[3],sys.argv[4])

