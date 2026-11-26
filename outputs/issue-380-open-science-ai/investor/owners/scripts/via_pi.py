#!/usr/bin/env python3
"""Fetch a page from the runner, and through a lab Raspberry Pi only when the runner is refused.

Part 2's source check could not fetch 44 cited pages, and its research passes skipped others, because many news and
press-release sites refuse a GitHub runner. Two things get a client refused: a datacenter address (the runner is on
Microsoft's network, AS8075) and a non-browser TLS fingerprint. A lab Pi is on the BYU network (AS6510). With an SSH
SOCKS tunnel to the Pi open on 127.0.0.1:1080,

    ssh -f -N -D 127.0.0.1:1080 -o ExitOnForwardFailure=yes <user>@<pi>

`get(url)` climbs this ladder and stops at the first route that returns the page:

1. `runner`      plain HTTP from the runner
2. `runner-tls`  from the runner with a browser's TLS fingerprint (curl_cffi)
3. `pi`          the same, through the Pi
4. `wayback`     the Internet Archive's closest snapshot, from the runner (or through the Pi if refused)

A real Chrome through the Pi was tried as a fifth route and dropped: it was refused by the two sites that refuse
everything else (Business Wire, Reuters). The Pi only relays: nothing is installed or written on it. Because it shares
its network with live lab work, Pi requests go one at a time across every process (a file lock), at least PI_GAP
seconds apart (default 3), are capped at PI_RATE (1 MB/s) and stop at MAX_BYTES (3 MB). Bing queries are spaced BING_GAP seconds apart
(default 2). Every network fetch is appended to data/pi_fetch_log.csv with its route, status and size. Pages are
cached in PAGE_CACHE (default /tmp/pagecache), never in the repository.

    python scripts/via_pi.py probe <url> ...          # status from every route, without the cache
    python scripts/via_pi.py page <url> [<regex>]      # sentences that state an amount and a deal, or match <regex>
    python scripts/via_pi.py news "<query>"            # Bing News RSS: date | title | url
    python scripts/via_pi.py web "<query>"             # Bing web results: title | url | snippet

Pages are untrusted data: this module returns text and never follows instructions in it.
"""
import base64, csv, datetime as dt, fcntl, hashlib, json, os, re, sys, threading, time, urllib.parse as up
import requests
from bs4 import BeautifulSoup
from curl_cffi import requests as cr

PI_PROXY = os.environ.get("PI_SOCKS", "socks5h://127.0.0.1:1080")
PI_GAP = float(os.environ.get("PI_GAP", "3"))
BING_GAP = float(os.environ.get("BING_GAP", "2"))
PI_RATE = int(os.environ.get("PI_RATE", "1000000"))  # bytes per second, per Pi request
MAX_BYTES = 3_000_000
CACHE = os.environ.get("PAGE_CACHE", "/tmp/pagecache")
LOG = os.environ.get("PI_FETCH_LOG", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                                                   "pi_fetch_log.csv"))
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.9"}
# Words that mark a refusal or a bot check rather than the page. Looked for in the title, or anywhere in the first
# 20 kB of a short page, since a long article can mention "captcha" in passing.
CHALLENGE = re.compile(r"just a moment|attention required|access denied|captcha|are you a robot|unusual traffic|"
                       r"enable javascript and cookies|verify you are (a )?human|pardon our interruption|"
                       r"request unsuccessful|px-captcha|datadome|security check|security checkpoint|"
                       r"bot protection|403 forbidden|page unavailable|blocked", re.I)
_log_lock = threading.Lock()
os.makedirs(CACHE, exist_ok=True)


class _Gap:
    """At most one request at a time, `gap` seconds apart, across every process on this machine."""

    def __init__(self, name, gap):
        self.path, self.gap = f"/tmp/.ratelimit_{name}", gap

    def __enter__(self):
        self.fh = open(self.path, "a+")
        fcntl.flock(self.fh, fcntl.LOCK_EX)
        self.fh.seek(0)
        last = float(self.fh.read().strip() or 0)
        wait = self.gap - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        return self

    def __exit__(self, *a):
        self.fh.seek(0); self.fh.truncate(); self.fh.write(str(time.time())); self.fh.flush()
        fcntl.flock(self.fh, fcntl.LOCK_UN); self.fh.close()


def _key(url):
    return os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest())


def _log(url, route, status, n, challenge, final):
    with _log_lock:
        new = not os.path.exists(LOG)
        with open(LOG, "a", newline="") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            w = csv.writer(f)
            if new:
                w.writerow(["utc", "url", "route", "status", "bytes", "challenge", "final_url"])
            w.writerow([dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), url, route, status, n,
                        int(challenge), final])
            fcntl.flock(f, fcntl.LOCK_UN)


def is_challenge(status, body):
    if status in (401, 403, 405, 406, 429, 451, 503):
        return True
    head = body[:20000].decode("utf-8", "replace")
    title = re.search(r"<title[^>]*>(.*?)</title>", head, re.S | re.I)
    title = title.group(1) if title else ""
    return bool(CHALLENGE.search(title)) or (len(body) < 15000 and bool(CHALLENGE.search(head)))


def _result(url, route, status, body, final):
    ch = isinstance(status, int) and is_challenge(status, body)
    _log(url, route, status, len(body), ch, final)
    return {"status": status, "final_url": final, "challenge": ch, "route": route,
            "ok": status == 200 and not ch and len(body) > 200, "body": body}


def _plain(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, stream=True, allow_redirects=True)
        body = r.raw.read(MAX_BYTES, decode_content=True) or b""
        r.close()
        return _result(url, "runner", r.status_code, body, r.url)
    except Exception as e:
        return _result(url, "runner", "ERR " + type(e).__name__, b"", "")


def _tls(url, via_pi, route, params=None):
    def go():
        try:
            r = cr.get(url, params=params, impersonate="chrome", timeout=40 if via_pi else 25, allow_redirects=True,
                       proxies={"http": PI_PROXY, "https": PI_PROXY} if via_pi else None,
                       max_recv_speed=PI_RATE if via_pi else 0)
            return _result(url, route, r.status_code, (r.content or b"")[:MAX_BYTES], str(r.url))
        except Exception as e:
            return _result(url, route, "ERR " + type(e).__name__, b"", "")
    if via_pi:
        with _Gap("pi", PI_GAP):
            return go()
    return go()


def _wayback(url):
    for via_pi in (False, True):
        try:
            if via_pi:
                with _Gap("pi", PI_GAP):
                    r = cr.get("https://archive.org/wayback/available", params={"url": url}, impersonate="chrome",
                               timeout=40, proxies={"https": PI_PROXY})
            else:
                r = cr.get("https://archive.org/wayback/available", params={"url": url}, impersonate="chrome",
                           timeout=30)
            snap = ((r.json() or {}).get("archived_snapshots") or {}).get("closest") or {}
        except Exception:
            continue
        if not snap.get("url") or str(snap.get("status")) != "200":
            return None
        res = _tls(snap["url"].replace("http://", "https://", 1), via_pi, "wayback")
        if res["ok"]:
            res["snapshot"] = snap.get("timestamp")
            return res
    return None


def get(url, use_cache=True, wayback=True):
    """{'ok', 'status', 'route', 'final_url', 'challenge', 'body'} from the first route on the ladder that works."""
    k = _key(url)
    if use_cache and os.path.exists(k + ".json"):
        meta = json.load(open(k + ".json"))
        meta["body"] = open(k + ".body", "rb").read() if os.path.exists(k + ".body") else b""
        return meta
    tried = []
    res = None
    for step in ("runner", "runner-tls", "pi", "wayback"):
        if step == "runner":
            r = _plain(url)
        elif step == "runner-tls":
            r = _tls(url, False, "runner-tls")
        elif step == "pi":
            r = _tls(url, True, "pi")
        else:
            if not wayback:
                break
            r = _wayback(url)
            if r is None:
                tried.append("wayback:none")
                break
        tried.append(f"{step}:{r['status']}")
        if r["ok"]:
            res = r
            break
        if r["status"] == 404 and step == "runner":  # a dead link: only the archive can help
            r2 = _wayback(url) if wayback else None
            tried.append(f"wayback:{r2['status'] if r2 else 'none'}")
            res = r2 if r2 and r2["ok"] else r
            break
        res = res or r
    res = dict(res)
    res["tried"] = " ".join(tried)
    meta = {k2: v for k2, v in res.items() if k2 != "body"}
    json.dump(meta, open(k + ".json", "w"))
    open(k + ".body", "wb").write(res["body"] if res["ok"] else b"")
    return res


def text_of_html(body):
    soup = BeautifulSoup(body[:MAX_BYTES], "lxml")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" "))


def text(url):
    """Visible text of the page, or None if no route could fetch it."""
    res = get(url)
    return text_of_html(res["body"]) if res["ok"] else None


# --- search: Bing answers the runner, so searching does not go through the Pi unless Bing refuses the runner ---
def _bing(path, params):
    for via_pi in (False, True):
        with _Gap("bing", BING_GAP):
            try:
                r = cr.get("https://www.bing.com" + path, params=params, impersonate="chrome", timeout=30,
                           proxies={"https": PI_PROXY} if via_pi else None)
            except Exception:
                continue
        if r.status_code == 200 and not is_challenge(200, r.content):
            return r.content
    return b""


def news(q):
    """Bing News RSS for a query: [{'date', 'title', 'url', 'source', 'snippet'}]."""
    body = _bing("/news/search", {"q": q, "format": "rss", "setlang": "en", "cc": "US"})
    out = []
    for it in BeautifulSoup(body, "xml").find_all("item"):
        link = it.link.get_text() if it.link else ""
        real = up.parse_qs(up.urlparse(link).query).get("url", [link])[0]
        d = it.pubDate.get_text() if it.pubDate else ""
        try:
            d = dt.datetime.strptime(d[:25].strip(), "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
        except ValueError:
            d = d[:16]
        src = it.find("News:Source") or it.find("Source")
        out.append({"date": d, "title": it.title.get_text() if it.title else "", "url": real,
                    "source": src.get_text() if src else "", "via": "bing-news",
                    "snippet": BeautifulSoup(it.description.get_text(), "lxml").get_text(" ")[:300]
                    if it.description else ""})
    return out


def _unwrap(href):
    if "bing.com/ck/a" in href:
        u = up.parse_qs(up.urlparse(href).query).get("u", [""])[0]
        if u.startswith("a1"):
            s = u[2:] + "=" * (-len(u[2:]) % 4)
            try:
                return base64.urlsafe_b64decode(s).decode()
            except Exception:
                return href
    return href


def web(q):
    """Bing web results for a query: [{'title', 'url', 'snippet'}]."""
    body = _bing("/search", {"q": q, "setlang": "en", "cc": "US"})
    out = []
    for li in BeautifulSoup(body, "lxml").select("li.b_algo"):
        a = li.select_one("h2 a")
        if not a:
            continue
        cap = li.select_one(".b_caption p") or li.select_one("p")
        out.append({"title": a.get_text(" ", strip=True), "url": _unwrap(a.get("href", "")), "via": "bing-web",
                    "date": "", "snippet": cap.get_text(" ", strip=True)[:300] if cap else ""})
    return out


def _probe(urls):
    for u in urls:
        for name, fn in (("runner", lambda: _plain(u)), ("runner-tls", lambda: _tls(u, False, "runner-tls")),
                         ("pi", lambda: _tls(u, True, "pi"))):
            r = fn()
            print(f"{name:10} {r['status']!s:>6} {len(r['body']):8d} {'CHALLENGE' if r['challenge'] else '':9} "
                  f"{u[:100]}")


def _page(url, pattern=None):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from news_leads import EVENT, MONEY
    res = get(url)
    print("HTTP", res["status"], "via", res["route"], res.get("snapshot") or "", res["final_url"])
    if not res["ok"]:
        print("tried:", res.get("tried"))
        return
    soup = BeautifulSoup(res["body"], "lxml")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    meta = (soup.find("meta", attrs={"property": "article:published_time"}) or
            soup.find("meta", attrs={"name": "date"}) or soup.find("meta", attrs={"itemprop": "datePublished"}))
    print("TITLE", title[:200], "| DATE", meta.get("content") if meta else "-")
    t = text_of_html(res["body"])
    rx = re.compile(pattern, re.I) if pattern else None
    n = 0
    for s in re.split(r"(?<=[.!?])\s+", t):
        if (rx and rx.search(s)) or (not rx and MONEY.search(s) and EVENT.search(s)):
            print("-", s[:400]); n += 1
            if n >= 25:
                break
    if n == 0:
        print("(no matching sentences)")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "probe":
        _probe(sys.argv[2:])
    elif cmd == "page":
        _page(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif cmd == "news":
        for h in news(sys.argv[2]):
            print(f"{h['date']} | {h['title']} | {h['url']}")
    elif cmd == "web":
        for h in web(sys.argv[2]):
            print(f"{h['title'][:90]} | {h['url']} | {h['snippet'][:160]}")
