#!/usr/bin/env python3
"""One search (or page fetch) through the lab Pi's network, in its own headed-Chrome window.

Shares one Chrome (CDP :9222, traffic via the CubXL Pi SOCKS tunnel) between several callers:
each call opens a fresh browser context (its own window), drives the search box with real mouse
moves, clicks and keystrokes, prints compact results, appends them to a shared JSONL log, and
closes the window. A lock file keeps at most 3 searches in flight and spaces queries per engine.

  python pi_search.py --engine bing "query words"        # bing | ddg | google | brave | youtube | reddit | hn
  python pi_search.py --fetch https://example.com/page --max-chars 6000
  python pi_search.py --who groupA --engine ddg "query"   # tag the log entry
"""
import argparse, fcntl, json, os, random, sys, time, datetime, re, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pi_browse as pb
from playwright.sync_api import sync_playwright

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pi-browser", "search_log.jsonl")
STATE = "/tmp/pi_search_state.json"; LOCK = "/tmp/pi_search_state.lock"
SPACING = {"google": 25, "bing": 6, "ddg": 6, "brave": 8, "youtube": 6, "reddit": 10, "hn": 3, "fetch": 2}
MAX_INFLIGHT = 3

pb.ENGINES["brave"] = dict(home="https://search.brave.com/", box="textarea#searchbox, input#searchbox, input[name='q']",
                           res="div.snippet[data-type='web']")
pb.JS["brave"] = """() => [...document.querySelectorAll("div.snippet[data-type='web']")].map(r => ({
    title: (r.querySelector('.title, .snippet-title')||{}).innerText||'',
    url: (r.querySelector("a[href^='http']:not([href*='search.brave.com'])")||r.querySelector('a'))?.href||'',
    cite: (r.querySelector('.netloc, cite, .url, .site-name-content')||{}).innerText||'',
    snippet: (r.querySelector('.snippet-description, .generic-snippet .content, .description')||{}).innerText||''}))"""

def acquire(kind):
    while True:
        with open(LOCK, "a+") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            st = json.load(open(STATE)) if os.path.exists(STATE) else {"inflight": [], "last": {}}
            now = time.time()
            st["inflight"] = [t for t in st["inflight"] if now - t < 180]
            wait = SPACING.get(kind, 5) - (now - st["last"].get(kind, 0))
            if len(st["inflight"]) < MAX_INFLIGHT and wait <= 0:
                st["inflight"].append(now); st["last"][kind] = now
                json.dump(st, open(STATE, "w")); return now
        time.sleep(max(1.0, min(wait if wait > 0 else 2.0, 10)) + random.uniform(0, 1.5))

def release(token):
    with open(LOCK, "a+") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        st = json.load(open(STATE)) if os.path.exists(STATE) else {"inflight": [], "last": {}}
        st["inflight"] = [t for t in st["inflight"] if abs(t - token) > 1e-6]
        json.dump(st, open(STATE, "w"))

def log(rec):
    with open(LOG, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX); f.write(json.dumps(rec) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?")
    ap.add_argument("--engine", default="bing")
    ap.add_argument("--fetch")
    ap.add_argument("--max-chars", type=int, default=6000)
    ap.add_argument("--who", default=os.environ.get("PI_WHO", "main"))
    a = ap.parse_args()
    kind = "fetch" if a.fetch else a.engine
    tok = acquire(kind)
    try:
        with sync_playwright() as p:
            br = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            ctx = br.new_context(viewport={"width": 1500, "height": 950}, locale="en-US")
            page = ctx.new_page()
            try:
                if a.fetch:
                    d = pb.fetch(page, a.fetch)
                    os.makedirs("/tmp/pitext", exist_ok=True)
                    h = hashlib.sha1(a.fetch.encode()).hexdigest()[:10]
                    json.dump(d, open(f"/tmp/pitext/{h}.json", "w"))
                    log(dict(who=a.who, kind="fetch", url=a.fetch, final_url=d["final_url"], title=d["title"], chars=len(d["text"]),
                             utc=datetime.datetime.now(datetime.UTC).isoformat()))
                    print(f"TITLE: {d['title']}\nFINAL_URL: {d['final_url']}\nSAVED: /tmp/pitext/{h}.json ({len(d['text'])} chars)\n")
                    print(d["text"][:a.max_chars])
                else:
                    d = pb.search(page, a.engine, a.query)
                    d["who"] = a.who; log(d)
                    if d.get("blocked"):
                        print("NOTE: page looked like a block/captcha; try another engine")
                    for i, r in enumerate(d["results"], 1):
                        print(f"{i}. {r['title']}\n   {r['url']}\n   {r.get('cite','')} {r['snippet'][:300]}".rstrip())
                    if not d["results"]:
                        print("(no results parsed)")
            finally:
                ctx.close()
    finally:
        release(tok)

if __name__ == "__main__":
    main()
