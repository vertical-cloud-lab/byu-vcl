#!/usr/bin/env python3
"""Parse saved Amazon search pages (untrusted HTML, treated as text only).

usage: python3 -I parse_search.py <file.html[.gz]> [...]
Prints one JSON line per organic or sponsored result.
"""
import gzip, html, json, re, sys

def load(p):
    raw = open(p, "rb").read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")

def clean(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

for p in sys.argv[1:]:
    doc = load(p)
    blocks = re.split(r'(?=<div[^>]*data-component-type="s-search-result")', doc)[1:]
    for b in blocks:
        b = b[:60000]
        asin = re.search(r'data-asin="([A-Z0-9]{10})"', b)
        if not asin:
            continue
        title = re.search(r'<h2[^>]*aria-label="([^"]+)"', b) or re.search(r'<h2[^>]*>(.*?)</h2>', b, re.S)
        price = re.search(r'<span class="a-offscreen">\s*(\$[\d,.]+)\s*</span>', b)
        rating = re.search(r'(\d\.\d) out of 5 stars', b)
        nrev = re.search(r'aria-label="([\d,.]+K?\+?) ratings?"', b) or re.search(r'<span[^>]*class="a-size-(?:base|small|mini)[^"]*s-underline-text[^"]*"[^>]*>\(?([\d,.]+K?)\)?</span>', b)
        bought = re.search(r'([\d,.]+K?\+) bought in past month', b)
        print(json.dumps({
            "file": p.rsplit("/", 1)[-1],
            "asin": asin.group(1),
            "sponsored": ("AdHolder" in b[:1500]) or ("Sponsored" in b and "sp_atf" in b),
            "title": clean(title.group(1))[:200] if title else "",
            "price": price.group(1) if price else "",
            "rating": rating.group(1) if rating else "",
            "ratings": nrev.group(1) if nrev else "",
            "bought_month": bought.group(1) if bought else "",
        }))
