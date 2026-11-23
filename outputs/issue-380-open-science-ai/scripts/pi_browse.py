#!/usr/bin/env python3
"""Search the web from the lab Pi's network with a headed Chrome and real mouse/keyboard input.

The browser runs on the runner's virtual display (:99) and all of its traffic leaves through an
SSH SOCKS tunnel to the CubXL Pi (rig.sh from byu-vcl PR 234), so search engines, Reddit and
YouTube see BYU's network rather than a datacenter. Every search moves the mouse to the search
box, clicks, types with per-key delays, submits, waits, screenshots and extracts results.

Usage: python pi_browse.py queries.tsv out.jsonl   (tsv: engine<TAB>query)
       python pi_browse.py --fetch urls.txt outdir   (save page text for each URL)
"""
import json, random, re, sys, time, os, hashlib, datetime
from playwright.sync_api import sync_playwright

SHOTS = os.environ.get("SHOTS", "/tmp/pishots")
os.makedirs(SHOTS, exist_ok=True)

def human_move_click(page, locator):
    locator.wait_for(state="visible", timeout=15000)
    try:
        locator.scroll_into_view_if_needed(timeout=5000); time.sleep(random.uniform(0.3, 0.6))
    except Exception:
        pass
    box = locator.bounding_box()
    x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
    y = box["y"] + box["height"] * random.uniform(0.35, 0.65)
    page.mouse.move(random.uniform(200, 900), random.uniform(150, 600), steps=8)
    page.mouse.move(x, y, steps=random.randint(18, 30))
    time.sleep(random.uniform(0.15, 0.4))
    page.mouse.click(x, y)

def type_query(page, q):
    page.keyboard.type(q, delay=random.randint(45, 90))
    time.sleep(random.uniform(0.2, 0.5))
    page.keyboard.press("Enter")

def scroll(page, n=3):
    for _ in range(n):
        page.mouse.wheel(0, random.randint(350, 700)); time.sleep(random.uniform(0.4, 0.9))

JS = {
 "bing": """() => [...document.querySelectorAll('li.b_algo')].map(r => ({title: r.querySelector('h2')?.innerText||'',
          url: r.querySelector('h2 a')?.href||'', cite: r.querySelector('cite')?.innerText||'',
          snippet: (r.querySelector('.b_caption p, .b_lineclamp2, .b_lineclamp3, .b_lineclamp4, .b_paractl')||{}).innerText||''}))""",
 "google": """() => [...document.querySelectorAll('a:has(h3)')].map(a => { const c = a.closest('div.MjjYud, div.g') || a.parentElement;
          return {title: a.querySelector('h3')?.innerText||'', url: a.href, cite: c?.querySelector('cite')?.innerText||'',
          snippet: (c?.querySelector('div.VwiC3b, span.aCOpRe, div[data-sncf]')||{}).innerText||''}})""",
 "ddg": """() => [...document.querySelectorAll("article[data-testid='result']")].map(r => ({title: r.querySelector('h2')?.innerText||'',
          url: r.querySelector("a[data-testid='result-title-a']")?.href||'', cite: '',
          snippet: (r.querySelector("[data-result='snippet']")||{}).innerText||''}))""",
 "youtube": """() => [...document.querySelectorAll('yt-lockup-view-model, ytd-video-renderer')].map(r => ({
          title: (r.querySelector('h3, #video-title, [class*=MetadataViewModelTitle]')||{}).innerText||'',
          url: r.querySelector("a[href^='/watch']")?.href||'', cite: '',
          snippet: (r.querySelector('[class*=ContentMetadataViewModel], #metadata, #channel-info')||{}).innerText||''})).filter(x=>x.url)""",
 "reddit": """() => [...document.querySelectorAll("a[data-testid='post-title']")].map(a => { const c = a.closest('search-telemetry-tracker, div') ;
          return {title: a.innerText||'', url: a.href, cite: '', snippet: (c?.innerText||'').slice(0,300)}})""",
 "hn": """() => [...document.querySelectorAll('article.Story')].map(r => ({title: r.querySelector('.Story_title')?.innerText||'',
          url: r.querySelector('.Story_title a')?.href||'', cite: '', snippet: (r.querySelector('.Story_meta')||{}).innerText||''}))""",
}
ENGINES = {
 "bing":   dict(home="https://www.bing.com/", box="textarea#sb_form_q, input#sb_form_q", res="li.b_algo"),
 "ddg":    dict(home="https://duckduckgo.com/", box="textarea[name='q'] >> visible=true", res="article[data-testid='result']"),
 "google": dict(home="https://www.google.com/?hl=en", box="textarea[name='q'], input[name='q']", res="a:has(h3)"),
 "youtube":dict(home="https://www.youtube.com/", box="input[name='search_query']", res="yt-lockup-view-model, ytd-video-renderer"),
 "reddit": dict(home="https://www.reddit.com/", box="input[name='q']", res="a[data-testid='post-title']",
                direct="https://www.reddit.com/search/?q={q}"),
 "hn":     dict(home="https://hn.algolia.com/", box="input[type='search']", res="article.Story"),
}

def bing_decode(u):
    import base64, urllib.parse
    try:
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
        v = qs.get("u", [""])[0]
        if v.startswith("a1"):
            v = v[2:]; v += "=" * (-len(v) % 4)
            return base64.urlsafe_b64decode(v).decode()
    except Exception:
        pass
    return u

def consent(page):
    for sel in ["button:has-text('Accept all')", "button:has-text('Reject all')", "button:has-text('I agree')",
                "button:has-text('Accept')", "#bnp_btn_accept"]:
        try:
            b = page.locator(sel).first
            if b.is_visible(timeout=800):
                human_move_click(page, b); time.sleep(1); return
        except Exception:
            pass

def search(page, engine, q):
    e = ENGINES[engine]
    page.goto(e["home"], wait_until="domcontentloaded", timeout=45000)
    time.sleep(random.uniform(1.5, 2.5)); consent(page)
    try:
        box = page.locator(e["box"]).first
        human_move_click(page, box)
        type_query(page, q)
    except Exception:
        if "direct" not in e:
            raise
        import urllib.parse
        page.goto(e["direct"].format(q=urllib.parse.quote_plus(q)), wait_until="domcontentloaded", timeout=45000)
    try:
        page.wait_for_selector(e["res"], timeout=20000)
    except Exception:
        pass
    time.sleep(random.uniform(1.5, 3.0)); scroll(page, 2)
    body = page.inner_text("body")[:500].lower()
    blocked = any(s in body for s in ["unusual traffic", "captcha", "are you a robot", "verify you are human", "blocked"])
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    slug = re.sub(r"[^a-z0-9]+", "-", q.lower())[:50]
    shot = f"{SHOTS}/{engine}_{slug}_{stamp}.png"
    page.screenshot(path=shot)
    out = page.evaluate(JS[engine])[:12]
    for o in out:
        o["snippet"] = (o.get("snippet") or "")[:400]
        if engine == "bing":
            o["url"] = bing_decode(o["url"])
    return dict(engine=engine, query=q, utc=stamp, final_url=page.url, blocked=blocked, n=len(out), results=out, screenshot=shot)

def fetch(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(random.uniform(2, 4)); consent(page); scroll(page, 3)
    return dict(url=url, final_url=page.url, title=page.title(), text=page.inner_text("body"))

def main():
    with sync_playwright() as p:
        br = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = br.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        if sys.argv[1] == "--fetch":
            outdir = sys.argv[3]; os.makedirs(outdir, exist_ok=True)
            for url in [u.strip() for u in open(sys.argv[2]) if u.strip() and not u.startswith("#")]:
                try:
                    d = fetch(page, url)
                    h = hashlib.sha1(url.encode()).hexdigest()[:10]
                    json.dump(d, open(f"{outdir}/{h}.json", "w"))
                    print("ok", h, len(d["text"]), url[:90], flush=True)
                except Exception as ex:
                    print("fail", url[:90], str(ex)[:120], flush=True)
                time.sleep(random.uniform(4, 8))
            return
        rows = [l.rstrip("\n").split("\t", 1) for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
        with open(sys.argv[2], "a") as f:
            for engine, q in rows:
                try:
                    d = search(page, engine, q)
                except Exception as ex:
                    d = dict(engine=engine, query=q, error=str(ex)[:300])
                f.write(json.dumps(d) + "\n"); f.flush()
                print(engine, "|", q[:60], "|", d.get("n"), "blocked" if d.get("blocked") else "", flush=True)
                time.sleep(random.uniform(6, 12))

if __name__ == "__main__":
    main()
