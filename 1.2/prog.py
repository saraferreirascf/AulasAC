# Import modules
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter
import sys

RAND = Random.new()

def keygen(keyfile):
    #key=bytearray(b"very nice key")
    KEY = RAND.read(32)
    #key="12345"
    #pad = '# constant pad for short keys ##'
    #keye = (key + pad)[:32]
    with open(keyfile, "wb") as f:
        f.write(KEY)


###################### ENCRYPT ##############################

def enc(keyfile,infile,outfile):
    #print("Entrei na funcao de enc ehehe")
    IV = RAND.read(8)
    #print("IV=",IV)
    with open("IV.txt", "wb") as fi:
        fi.write(IV)

    with open(keyfile, "rb") as f:
        keye=f.read()

    ctr_e = Counter.new(64, prefix=IV)
    encryptor = AES.new(keye, AES.MODE_CTR, counter=ctr_e)

    with open(infile, "rb") as fp:
        plaintext = fp.read()

    ciphertext = encryptor.encrypt(plaintext)

    with open(outfile,"wb") as fc:
        fc.write(ciphertext)

###################### DECRYPT ##############################


def dec(keyfile,infile,outfile):
    #print("Entrei na funcao de dec ehehe")
    
    with open(keyfile,"rb") as f:
        keyd=f.read()
    #keyd = (key + pad)[:32]
    with open("IV.txt","rb") as fi:
        IV=fi.read()
    #print("IV=",IV)
    #restarts from the beginning

    ctr_d = Counter.new(64, prefix=IV)

    # Create decryptor, then decrypt and print decoded text
    decryptor = AES.new(keyd, AES.MODE_CTR, counter=ctr_d)
    with open(infile, "rb") as fp:
        ciphertext = fp.read()
    #print("Ciphertext do ficheiro:",ciphertext)
    decoded_text = decryptor.decrypt(ciphertext)
    #print(decoded_text.decode("utf-8"))
    with open(outfile,"wb") as fc:
        fc.write(decoded_text)

def usage():
    print('Usage: python3 prog.py -genkey <outfile>')
    print('                       -enc <keyfile> <infile> <outfile>')
    print('                       -dec <keyfile> <infile> <outfile>')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    elif sys.argv[1]=="-genkey":
        keygen(sys.argv[2])
    elif sys.argv[1]=="-enc":
        enc(sys.argv[2],sys.argv[3],sys.argv[4])
    elif sys.argv[1]=="-dec":
        dec(sys.argv[2],sys.argv[3],sys.argv[4])
    else:
        usage()
