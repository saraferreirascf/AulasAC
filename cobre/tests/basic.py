import sys
import time
import threading
import cobre.net
import cobre.errors

def g(kv):
    for k in kv:
        globals()[k] = kv[k]

class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.server = cobre.net.Server(addr=ADDR)

    def run(self):
        s = self.server
        s.timeout(0.2)
        while True:
            with LOCK:
                if DONE:
                    return
            try:
                with s.accept() as c:
                    c.send_bytes(b'ganda jarda')
            except cobre.errors.AcceptError:
                continue

if __name__ == '__main__':
    g({
        'ADDR': sys.argv[1],
        'DONE': False,
        'LOCK': threading.Lock(),
    })

    s = ServerThread()
    s.start()

    with cobre.net.Client(addr=ADDR) as c:
        buf = bytearray(32)
        n = c.recv_bytes(buf)
        print(f'From server: {buf[:n]}')

    with LOCK:
        DONE = True

    s.join()
