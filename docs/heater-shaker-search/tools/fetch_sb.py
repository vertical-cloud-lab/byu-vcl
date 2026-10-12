"""Download sb0 storyboard sheets listed in a JSONL file into OUTDIR/<id>/NNN.webp."""
import json, os, sys, urllib.request, concurrent.futures as cf
src, outdir = sys.argv[1], sys.argv[2]
ids = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
jobs = []
for l in open(src):
    r = json.loads(l)
    if not r.get("ok") or (ids and r["id"] not in ids):
        continue
    sb = r["sb"].get("sb0")
    if not sb:
        continue
    os.makedirs(os.path.join(outdir, r["id"]), exist_ok=True)
    for i, (u, dur) in enumerate(sb["fragments"]):
        p = os.path.join(outdir, r["id"], "%03d.img" % i)
        if not os.path.exists(p):
            jobs.append((u, p))
def get(job):
    u, p = job
    for _ in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
            open(p, "wb").write(data)
            return len(data)
        except Exception:
            pass
    return -1
with cf.ThreadPoolExecutor(16) as ex:
    sizes = list(ex.map(get, jobs))
print("fetched", sum(1 for s in sizes if s > 0), "of", len(jobs), "bytes", sum(s for s in sizes if s > 0), "failed", sum(1 for s in sizes if s < 0))
