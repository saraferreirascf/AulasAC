f= open("keyfile.txt","w+")
key=bytearray(b"very nice key")
f.write(key)
f.close()