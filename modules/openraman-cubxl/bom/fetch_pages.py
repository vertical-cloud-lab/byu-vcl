"""Fetch a list of URLs politely (stdlib only) and print status + price-like strings."""
import re, sys, time, urllib.request, gzip, json
UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
for url in sys.argv[1:]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                                               "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            b = r.read()
            if r.headers.get("Content-Encoding") == "gzip": b = gzip.decompress(b)
            s = b.decode("utf-8", "replace"); code = r.status; final = r.geturl()
    except Exception as e:
        print(json.dumps({"url": url, "error": repr(e)[:300]})); continue
    prices = re.findall(r'(?:US\$|\$|USD\s?)\s?[0-9][0-9,]*\.?[0-9]{0,2}', s)
    ld = re.findall(r'"price"\s*:\s*"?([0-9.,]+)"?', s)
    title = re.search(r'<title[^>]*>(.*?)</title>', s, re.S)
    print(json.dumps({"url": url, "final": final, "status": code, "len": len(s), "title": (title.group(1).strip()[:150] if title else None),
                      "prices": prices[:15], "jsonld_price": ld[:10], "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))
    sys.stdout.flush(); time.sleep(1.5)
