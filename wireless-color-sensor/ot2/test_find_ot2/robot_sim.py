"""Stand-in OT-2 for run.sh: GET /health on 31950 and an mDNS responder, both on IPv4 and IPv6.

Usage (inside the netns run.sh creates): python3 robot_sim.py <interface> <its IPv4 address>
"""
import http.server, json, socket, socketserver, struct, sys, threading

NAME, IFNAME, V4 = "OT2CEP20210722R13", sys.argv[1], sys.argv[2]

class Health(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"name": NAME, "api_version": "8.8.1", "robot_model": "OT-2 Standard"}).encode()
        self.send_response(200 if self.path == "/health" else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a):
        print("http", self.client_address[0], self.path, flush=True)

class DualStack(socketserver.ThreadingMixIn, http.server.HTTPServer):
    address_family, daemon_threads = socket.AF_INET6, True
    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()

def name(n):
    return b"".join(bytes([len(p)]) + p.encode() for p in n.split(".")) + b"\0"

def answer(qid):
    rdata = name(f"{NAME}._http._tcp.local")
    return (struct.pack("!6H", qid, 0x8400, 0, 1, 0, 0) + name("_http._tcp.local")
            + struct.pack("!HHIH", 12, 1, 120, len(rdata)) + rdata)

def serve(sock, tag):
    while True:
        data, addr = sock.recvfrom(9000)
        if len(data) >= 12 and b"_http" in data and not data[2] & 0x80:
            print("mdns", tag, addr[0], flush=True)
            sock.sendto(answer(struct.unpack("!H", data[:2])[0]), addr)

s4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s4.bind(("0.0.0.0", 5353))
s4.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
              socket.inet_aton("224.0.0.251") + socket.inet_aton(V4))
s6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
s6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
s6.bind(("::", 5353))
s6.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP,
              socket.inet_pton(socket.AF_INET6, "ff02::fb") + struct.pack("@I", socket.if_nametoindex(IFNAME)))
threading.Thread(target=serve, args=(s4, "v4"), daemon=True).start()
threading.Thread(target=serve, args=(s6, "v6"), daemon=True).start()
print("ready", flush=True)
DualStack(("::", 31950), Health).serve_forever()
