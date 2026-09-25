#!/usr/bin/env python3
"""ssh ProxyCommand that caps the download direction (Pi -> runner).

Usage: ProxyCommand="python3 ratelimit_pipe.py %h %p BYTES_PER_S"

Everything the browser loads leaves the Pi as *upload* on its own internet
link, which is also what a livestream uses. A small SO_RCVBUF keeps TCP flow
control tight, so the cap propagates back through the tunnel to the Pi instead
of arriving as a burst.
"""
import os
import socket
import sys
import threading
import time

host, port, rate = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
err = None
for fam, typ, proto, _, addr in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM):
    s = socket.socket(fam, typ, proto)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 64 * 1024)
    try:
        s.connect(addr)
        break
    except OSError as e:
        err = e
        s.close()
else:
    raise SystemExit(f"connect failed: {err}")


def upstream():
    while True:
        data = os.read(0, 65536)
        if not data:
            s.shutdown(socket.SHUT_WR)
            return
        s.sendall(data)


threading.Thread(target=upstream, daemon=True).start()
tokens, last, burst = 0.0, time.monotonic(), rate * 0.25
while True:
    data = s.recv(16384)
    if not data:
        break
    n = len(data)
    while True:
        now = time.monotonic()
        tokens, last = min(burst, tokens + (now - last) * rate), now
        if tokens >= n:
            tokens -= n
            break
        time.sleep((n - tokens) / rate)
    view = memoryview(data)
    while view:
        view = view[os.write(1, view):]
