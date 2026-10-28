# Runs on the Pi: fetch archive fragments by sq (2 s each) and save each one's first frame as PNG.
# Refreshes the fragment URL on HTTP 403.
import os, subprocess, sys, time, urllib.request, urllib.error
FF = os.path.expanduser("~/ytframes/bin/ffmpeg"); OUT = os.path.expanduser("~/ytframes/out/issue305/live")
YTDLP = os.path.expanduser("~/.venvs/ytframes/bin/yt-dlp")
UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
def fresh():
    return subprocess.run([YTDLP, "--js-runtimes", "node", "-f", "278", "-g", "https://www.youtube.com/watch?v=sDPzso4-tP0"],
                          capture_output=True, text=True, check=True).stdout.strip().split("\n")[0]
base = fresh(); refreshes = 0
sqs = sorted({int(x) for x in sys.stdin.read().split()})
os.makedirs(os.path.join(OUT, "png"), exist_ok=True); ok = 0
for k, sq in enumerate(sqs):
    seg = os.path.join(OUT, "seg", "%d.webm" % sq); png = os.path.join(OUT, "png", "sq%05d.png" % sq)
    if not os.path.exists(seg):
        d = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(base + "&sq=%d" % sq, headers={"User-Agent": UA}), timeout=30) as r:
                    d = r.read()
                break
            except urllib.error.HTTPError as e:
                if e.code == 403 and refreshes < 20:
                    base = fresh(); refreshes += 1
                else:
                    time.sleep(2)
            except Exception:
                time.sleep(2)
        if d is None:
            continue
        open(seg, "wb").write(d); time.sleep(len(d) / 1.0e6)
    if not os.path.exists(png):
        subprocess.run([FF, "-nostdin", "-loglevel", "error", "-y", "-i", seg, "-frames:v", "1", png])
    ok += os.path.exists(png)
    if k % 50 == 0:
        print("progress", k, len(sqs), "ok", ok, "refreshes", refreshes, file=sys.stderr, flush=True)
print("frames", ok, "of", len(sqs), "refreshes", refreshes, file=sys.stderr, flush=True)
