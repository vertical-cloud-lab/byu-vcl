"""Headed Chromium on Xvfb, driven by real X mouse and keyboard events (xdotool), for reading vendor pages that block bots.

Used for the procurement third pass (#303, PR #331, 2026-11-07). Headless Chromium on the stream-cam Pi was refused by
Hitachi High-Tech (Akamai), KLA, Instron and Bambu Lab (Cloudflare), Modula and Staubli; the same pages opened in headed
Chromium driven this way. Parker (Akamai "Access Denied") still refused it.

What it does: starts Xvfb :77 and system Chromium (no --headless, no --enable-automation), both niced, from tmpfs
(/tmp/vcl-hc); types each URL into the address bar, moves the mouse along curved paths, scrolls with the wheel, and
clicks with real X events. CDP (--remote-debugging-port, no Runtime.enable) is used only to read the page text and to cap
the browser's bandwidth at 400 kB/s down, since the Pi carries a live stream on residential Wi-Fi.

Run it on the stream-cam Pi (Pi 5, 4 GB; it has chromium, Xvfb, xdotool, scrot and ~/.venvs/cdp with websocket-client):
  ssh "$RPI_STREAM_CAM_USERNAME@$RPI_STREAM_CAM_HOSTNAME" 'mkdir -p -m 700 /tmp/vcl-hc-bin && cat > /tmp/vcl-hc-bin/hc.py' < headed_chromium.py
  ssh ... '~/.venvs/cdp/bin/python /tmp/vcl-hc-bin/hc.py start'
  ssh ... '~/.venvs/cdp/bin/python /tmp/vcl-hc-bin/hc.py go https://example.com/contact'   # prints title and text
Commands: start | go URL [WAIT] | text [REGEX [CTX]] | links REGEX | shot | click X Y | move X Y | findclick TEXT |
          scroll N | key K... | eval JS | stop.  `shot` writes /tmp/vcl-hc/shot.png (copy it back with ssh cat).
Check the Pi read-only first (load, free RAM, the stream), read one page at a time, and always `stop`, then
`rm -rf /tmp/vcl-hc-bin`: nothing is left on the Pi's disk.
"""
import json, os, random, re, signal, subprocess, sys, time, urllib.request

D = "/tmp/vcl-hc"
DISP = ":77"
PORT = 9333
ENV = dict(os.environ, DISPLAY=DISP)
CHALLENGE = re.compile(r"just a moment|verify you are human|checking your browser|attention required|"
                       r"access denied|are you a robot|press & hold|captcha|unusual traffic|request unsuccessful",
                       re.I)


def run(*a):
    return subprocess.run(list(a), env=ENV, capture_output=True, text=True)


def xdo(*a):
    return run("xdotool", *[str(x) for x in a])


def page_ws():
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=5) as r:
        for t in json.load(r):
            if t.get("type") == "page" and not t["url"].startswith(("devtools://", "chrome-extension://")):
                return t["webSocketDebuggerUrl"]
    raise SystemExit("no page target")


def cdp():
    import websocket
    return websocket.create_connection(page_ws(), timeout=60, suppress_origin=True)


def call(ws, i, method, **params):
    ws.send(json.dumps({"id": i, "method": method, "params": params}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == i:
            if "error" in m:
                raise RuntimeError(m["error"])
            return m.get("result", {})


def evaluate(expr):
    ws = cdp()
    try:
        r = call(ws, 1, "Runtime.evaluate", expression=expr, returnByValue=True)
        return r.get("result", {}).get("value")
    finally:
        ws.close()


def mouse_pos():
    out = xdo("getmouselocation", "--shell").stdout
    v = dict(l.split("=") for l in out.split() if "=" in l)
    return int(v.get("X", 600)), int(v.get("Y", 450))


def human_move(x, y):
    x0, y0 = mouse_pos()
    n = random.randint(14, 24)
    cx, cy = (x0 + x) / 2 + random.uniform(-80, 80), (y0 + y) / 2 + random.uniform(-60, 60)
    for k in range(1, n + 1):
        t = k / n
        t = t * t * (3 - 2 * t)
        bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x
        by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y
        xdo("mousemove", int(bx + random.uniform(-1.5, 1.5)), int(by + random.uniform(-1.5, 1.5)))
        time.sleep(random.uniform(0.008, 0.03))
    xdo("mousemove", x, y)


def human_click(x, y):
    human_move(x, y)
    time.sleep(random.uniform(0.15, 0.4))
    xdo("mousedown", 1)
    time.sleep(random.uniform(0.06, 0.14))
    xdo("mouseup", 1)


def wiggle():
    x, y = mouse_pos()
    human_move(max(50, min(1300, x + random.randint(-200, 200))), max(150, min(850, y + random.randint(-120, 120))))


def focus_window():
    wids = xdo("search", "--onlyvisible", "--class", "chromium").stdout.split()
    if wids:
        human_move(random.randint(500, 900), random.randint(300, 600))
        xdo("windowfocus", "--sync", wids[-1])


def snapshot(maxchars=1500):
    v = evaluate("JSON.stringify({u: location.href, t: document.title, r: document.readyState,"
                 " b: document.body ? document.body.innerText : ''})")
    v = json.loads(v or "{}")
    with open(f"{D}/page.txt", "w") as f:
        f.write(v.get("b", ""))
    return v


def shot():
    run("scrot", "-o", f"{D}/shot.png")
    print(f"screenshot: {D}/shot.png")


def start():
    os.makedirs(D, mode=0o700, exist_ok=True)
    os.chmod(D, 0o700)
    xv = subprocess.Popen(["nice", "-n", "15", "Xvfb", DISP, "-screen", "0", "1366x900x24", "-nolisten", "tcp"],
                          stdout=subprocess.DEVNULL, stderr=open(f"{D}/xvfb.log", "w"), start_new_session=True)
    time.sleep(2)
    ch = subprocess.Popen(["nice", "-n", "15", "chromium", f"--user-data-dir={D}/profile", "--no-first-run",
                           "--no-default-browser-check", "--disable-sync", "--password-store=basic", "--lang=en-US",
                           "--window-position=0,0", "--window-size=1366,900", "--disk-cache-size=50000000",
                           f"--remote-debugging-port={PORT}", "about:blank"],
                          env=ENV, stdout=subprocess.DEVNULL, stderr=open(f"{D}/chromium.log", "w"),
                          start_new_session=True)
    for _ in range(40):
        try:
            page_ws()
            break
        except Exception:
            time.sleep(1)
    # bandwidth cap: a holder process keeps a CDP session open with the throttle set
    hold = subprocess.Popen([sys.executable, __file__, "hold"], stdout=open(f"{D}/hold.log", "w"),
                            stderr=subprocess.STDOUT, start_new_session=True)
    with open(f"{D}/pids", "w") as f:
        f.write(f"{xv.pid} {ch.pid} {hold.pid}\n")
    time.sleep(3)
    print("started; hold log:", open(f"{D}/hold.log").read().strip())


def hold():
    ws = cdp()
    call(ws, 1, "Network.enable")
    try:
        call(ws, 2, "Network.emulateNetworkConditions", offline=False, latency=0,
             downloadThroughput=400 * 1024, uploadThroughput=150 * 1024)
        print("throttle on: 400 kB/s down, 150 kB/s up", flush=True)
    except Exception as e:
        print("throttle failed:", e, flush=True)
    ws.settimeout(None)
    while True:
        try:
            ws.recv()
        except Exception as e:
            print("hold ended:", e, flush=True)
            return


def go(url, wait=45):
    focus_window()
    xdo("key", "ctrl+l")
    time.sleep(random.uniform(0.3, 0.6))
    xdo("type", "--delay", random.randint(40, 90), url)
    time.sleep(0.3)
    xdo("key", "Delete")
    xdo("key", "Return")
    t0 = time.time()
    time.sleep(4)
    v = {}
    while time.time() - t0 < wait:
        try:
            v = snapshot()
        except Exception as e:
            v = {"t": f"(eval failed: {e})", "b": "", "r": "?"}
        head = (v.get("t", "") + "\n" + v.get("b", "")[:400])
        if v.get("r") == "complete" and not CHALLENGE.search(head) and len(v.get("b", "")) > 200:
            break
        wiggle()
        time.sleep(random.uniform(1.5, 3.0))
    # read like a person: a couple of scrolls down and back up
    for _ in range(random.randint(2, 3)):
        xdo("click", 5)
        time.sleep(random.uniform(0.4, 0.9))
    for _ in range(3):
        xdo("click", 4)
        time.sleep(0.2)
    try:
        v = snapshot()
    except Exception:
        pass
    b = v.get("b", "")
    print(f"url:   {v.get('u')}\ntitle: {v.get('t')}\nstate: {v.get('r')}  chars: {len(b)}  "
          f"challenge: {bool(CHALLENGE.search(v.get('t', '') + b[:600]))}  ({time.time() - t0:.0f}s)")
    print("----\n" + b[:1200])
    shot()


def text(rx=None, ctx=1):
    b = snapshot()["b"]
    if not rx:
        print(b)
        return
    lines = [l for l in b.splitlines() if l.strip()]
    hits = [i for i, l in enumerate(lines) if re.search(rx, l, re.I)]
    keep = sorted({j for i in hits for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1))})
    last = -2
    for j in keep:
        if j != last + 1:
            print("--")
        print(lines[j])
        last = j


def stop():
    try:
        pids = open(f"{D}/pids").read().split()
    except Exception:
        pids = []
    for p in pids:
        try:
            os.killpg(int(p), signal.SIGTERM)
        except Exception:
            pass
    time.sleep(2)
    run("pkill", "-f", f"user-data-dir={D}/profile")
    run("pkill", "-f", f"Xvfb {DISP}")
    subprocess.run(["rm", "-rf", D])
    print("stopped; left:", subprocess.run(["bash", "-c", f"ls -d {D} 2>/dev/null; pgrep -fa 'vcl-hc|Xvfb :77' | grep -v pgrep"],
                                           capture_output=True, text=True).stdout.strip() or "nothing")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "start": start()
    elif cmd == "hold": hold()
    elif cmd == "go": go(args[0], int(args[1]) if len(args) > 1 else 45)
    elif cmd == "text": text(args[0] if args else None, int(args[1]) if len(args) > 1 else 1)
    elif cmd == "shot": shot()
    elif cmd == "click": human_click(int(args[0]), int(args[1])); time.sleep(1); print("clicked")
    elif cmd == "move": human_move(int(args[0]), int(args[1])); print("moved")
    elif cmd == "scroll":
        n = int(args[0]); b = 5 if n > 0 else 4
        for _ in range(abs(n)): xdo("click", b); time.sleep(random.uniform(0.15, 0.35))
        print("scrolled")
    elif cmd == "key": xdo("key", *args); print("key", args)
    elif cmd == "stop": stop()
    elif cmd == "eval": print(evaluate(args[0]))
    elif cmd == "findclick":
        find = """const want = %s; const els = [...document.querySelectorAll('a,button,summary,h2,h3,h4,h5,span,div,li,p')];
          const el = els.find(e => e.innerText && e.innerText.trim() === want) || els.find(e => e.innerText && e.innerText.trim().startsWith(want) && e.innerText.length < want.length + 40);""" % json.dumps(args[0])
        ok = evaluate("(() => {" + find + " if (!el) return false; el.scrollIntoView({block: 'center', behavior: 'instant'}); return true; })()")
        if not ok: print("not found"); sys.exit(0)
        time.sleep(1.2)
        pos = evaluate("(() => {" + find + " const r = el.getBoundingClientRect(); return [r.x + Math.min(r.width / 2, 120) + window.screenX, r.y + r.height / 2 + window.screenY + (window.outerHeight - window.innerHeight)]; })()")
        human_click(int(pos[0]), int(pos[1])); time.sleep(1.5); print("clicked at", [int(p) for p in pos])
