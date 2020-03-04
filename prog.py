import sys

if sys.argv[1]=="-keygen":
	exec(open('keygen.py').read())
if sys.argv[1]=="-enc":
	exec(open('enc.py').read())
if sys.argv[1]=="-dec":
	exec(open('dec.py').read())