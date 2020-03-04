Para correr o Servidor:
$ python3 app.py Server

Para correr o Cliente:
$ python3 app.py Client

Para gerar as chaves para o AES-CTR:
$python3 prog.py -genkey <keyfile>

Para cifrar um texto com o AES-CTR:
$python3 prog.py -enc <keyfile> <infile> <outfile>

Para decifrar um texto cifrado com AES-CTR:
$python3 prog.py -dec <keyfile> <infile> <outfile>
