#!/bin/sh

rand_port() {
    openssl rand 2 \
    | python3 -c "import sys; print(int.from_bytes(sys.stdin.buffer.read(), 'big'))"
}

port=`rand_port`
python3 -m cobre.tests.basic 127.0.0.1:$port