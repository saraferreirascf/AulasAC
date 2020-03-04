# Import modules
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter


#key=bytearray(b"very nice key")
key="12345"
pad = '# constant pad for short keys ##'
keye = (key + pad)[:32]

random_generator = Random.new()
IV = random_generator.read(8)

ctr_e = Counter.new(64, prefix=IV)

encryptor = AES.new(keye, AES.MODE_CTR, counter=ctr_e)

fp = open("plaintext.txt", "r")
plaintext = fp.read()

ciphertext = encryptor.encrypt(plaintext)
print(ciphertext)

fc= open("ciphertext.txt","wb+")
fc.write(ciphertext)


###################### DECRYPT ##############################

keyd = (key + pad)[:32]

#restarts from the beginning

ctr_d = Counter.new(64, prefix=IV)

# Create decryptor, then decrypt and print decoded text
decryptor = AES.new(keyd, AES.MODE_CTR, counter=ctr_d)
fp = open("ciphertext.txt", "rb")
ciphertext = fp.read()
decoded_text = decryptor.decrypt(ciphertext)
print(decoded_text)

