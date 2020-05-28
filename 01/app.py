import sys

if sys.argv[1]=="Client":
	exec(open('client.py').read())
if sys.argv[1]=="Server":
	exec(open('server.py').read())

