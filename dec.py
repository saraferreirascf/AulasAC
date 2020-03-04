# Import modules
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter


key="12345"
pad = '# constant pad for short keys ##'
keyd = (key + pad)[:32]

# Create counter for decryptor: it is equal to the encryptor, but restarts from the beginning

ctr_d = Counter.new(64, prefix=IV)

# Create decryptor, then decrypt and print decoded text
decryptor = AES.new(keyd, AES.MODE_CTR, counter=ctr_d)

fp = open("ciphertext.txt", "rb")
ciphertext=fp.read()
decoded_text = decryptor.decrypt(ciphertext)


print(decoded_text)