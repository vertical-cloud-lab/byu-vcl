"""Read listing pages for the candidates (condition, location, seller, price, availability, shipping).

    MARKET_CDP=http://127.0.0.1:9225 python3 detail.py [--cap N] [--stations a,b] [--sites x,y]
Writes /tmp/market/raw/details.jsonl (the page's text, first 15,000 characters) and a JPEG of each page.
"""
import json, os, random, sys, time
import browse as B

RAW = "/tmp/market/raw"
SHOTS = "/tmp/market/shots/detail"
ORDER = {"exact": 0, "family": 1, "sub": 2}


def main():
    cap = 30
    stations = sites = None
    for a in sys.argv[1:]:
        if a.startswith("--cap="):
            cap = int(a.split("=")[1])
        if a.startswith("--stations="):
            stations = set(a.split("=")[1].split(","))
        if a.startswith("--sites="):
            sites = set(a.split("=")[1].split(","))
    os.makedirs(SHOTS, exist_ok=True)
    done = set()
    if os.path.exists(f"{RAW}/details.jsonl"):
        for l in open(f"{RAW}/details.jsonl"):
            d = json.loads(l)
            if not d.get("error"):
                done.add(d["url"])
    cands = json.load(open(f"{RAW}/candidates.json"))
    cands = [c for c in cands if c["url"] not in done and c["site"] != "fedequip" or
             (c["site"] == "fedequip" and "/inventory/" in c["url"] and c["url"] not in done)]
    if stations:
        cands = [c for c in cands if c["station"] in stations]
    if sites:
        cands = [c for c in cands if c["site"] in sites]
    cands.sort(key=lambda c: (ORDER[c["match"]], c["station"]))
    per = {}
    todo = []
    for c in cands:
        k = (c["station"], c.get("comp", ""))
        if per.get(k, 0) >= cap:
            continue
        per[k] = per.get(k, 0) + 1
        todo.append(c)
    random.shuffle(todo)          # interleave sites
    todo.sort(key=lambda c: ORDER[c["match"]])
    print(len(todo), "pages to read", flush=True)
    pw, br, ctx, page = B.connect()
    blocked = {}
    for i, c in enumerate(todo):
        if blocked.get(c["site"], 0) >= 2:
            continue
        r = B.visit(page, c["url"], gap=(6.0, 12.0), scrolls=(2, 4), label=f"detail|{c['site']}|{c['station']}")
        if r["blocked"] or (r["status"] and r["status"] >= 400 and r["status"] != 404):
            blocked[c["site"]] = blocked.get(c["site"], 0) + 1
        try:
            txt = page.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception:
            txt = ""
        shot = ""
        if not r["blocked"] and r["status"] == 200:
            shot = f"{SHOTS}/{c['site']}_{abs(hash(c['url'])) % 10**9}.jpg"
            try:
                page.evaluate("() => window.scrollTo(0, 0)")
                page.wait_for_timeout(600)
                page.screenshot(path=shot, type="jpeg", quality=55)
            except Exception:
                shot = ""
        rec = dict(url=c["url"], site=c["site"], station=c["station"], match=c["match"], status=r["status"],
                   blocked=r["blocked"], error=r["error"], title=r["title"], final_url=r["final_url"],
                   text=txt[:15000], shot=shot, t_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        with open(f"{RAW}/details.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(i + 1, c["site"], c["station"], c["match"], r["status"], r["blocked"], c["title"][:60], flush=True)
    pw.stop()


if __name__ == "__main__":
    main()
