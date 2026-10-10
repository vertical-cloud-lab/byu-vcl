import urllib.parse
import re, sys, time, urllib.request, gzip, json
UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
for q in sys.argv[1:]:
    url = "https://www.amazon.com/s?k=" + urllib.parse.quote_plus(q)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html", "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            b = r.read(); b = gzip.decompress(b) if r.headers.get("Content-Encoding") == "gzip" else b
            s = b.decode("utf-8", "replace")
    except Exception as e:
        print(json.dumps({"q": q, "error": repr(e)[:200]})); continue
    out = []
    for blk in re.split(r'data-component-type="s-search-result"', s)[1:9]:
        asin = re.search(r'data-asin="([A-Z0-9]{10})"', blk) or re.search(r'/dp/([A-Z0-9]{10})', blk)
        title = re.search(r'<h2[^>]*>.*?<span[^>]*>(.*?)</span>', blk, re.S)
        price = re.search(r'a-offscreen">(\$[0-9.,]+)', blk)
        out.append({"asin": asin.group(1) if asin else None, "price": price.group(1) if price else None,
                    "title": re.sub(r"<[^>]+>", "", title.group(1))[:150] if title else None})
    print(json.dumps({"q": q, "url": url, "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "results": out}))
    sys.stdout.flush(); time.sleep(3)
