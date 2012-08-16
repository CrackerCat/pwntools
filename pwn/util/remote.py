import pwn, socket, time, sys
from threading import Thread

class remote:
    def __init__(self, host, port, fam = None, typ = socket.SOCK_STREAM, proto = 0):
        self.target = (host, port)
        if fam is None:
            if host.find(':') <> -1:
                self.family = socket.AF_INET6
            else:
                self.family = socket.AF_INET
        self.type = typ
        self.proto = proto
        self.sock = None
        self.debug = pwn.DEBUG
        self.connect()

    def connect(self):
        self.close()
        self.sock = socket.socket(self.family, self.type, self.proto)
        self.sock.connect(self.target)

    def settimeout(self, n):
        self.sock.settimeout(n)

    def setblocking(self, b):
        self.sock.setblocking(b)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def send(self, dat):
        return self.sock.send(dat)

    def recv(self, numb = 1024):
        res = self.sock.recv(numb)
        if self.debug:
            sys.stdout.write(res)
            sys.stdout.flush()
        return res

    def recvn(self, numb):
        res = []
        n = 0
        while n < numb:
            c = self.recv(1)
            if not c:
                break
            res.append(c)
            n += 1
        return ''.join(res)

    def recvuntil(self, delim):
        d = list(delim)
        res = []
        while d:
            c = self.recv(1)
            if not c:
                break
            res.append(c)
            if c == d[0]:
                d.pop(0)
            else:
                d = list(delim)
        return ''.join(res)

    def recvline(self, lines = 1):
        res = []
        for _ in range(lines):
            res.append(self.recvuntil('\n'))
        return ''.join(res)

    def interactive(self, prompt = '> '):
        self.debug = True
        def loop():
            while True:
                self.recv()
        t = Thread(target = loop)
        t.daemon = True
        t.start()
        while True:
            try:
                time.sleep(0.1)
                self.send(raw_input(prompt) + '\n')
            except KeyboardInterrupt:
                break
