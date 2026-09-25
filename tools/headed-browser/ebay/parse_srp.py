#!/usr/bin/env python3
"""Summarise a saved eBay search-results page: one line per listing.

  parse_srp.py save-NAME.html [LIMIT]

Prints `ITEMID | title | condition | price | ... | seller`. Listings eBay adds
under "Results matching fewer words" are marked [fewer-words].
"""
import html
import re
import sys

s = open(sys.argv[1], encoding="utf-8", errors="replace").read()
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 60
cut = s.find("Results matching fewer words")
parts = re.split(r'<li class="s-card', s)
seen = set()
pos = len(parts[0])
for b in parts[1:]:
    start = pos
    pos += len('<li class="s-card') + len(b)
    m = re.search(r'data-listingid="?(\d+)', b)
    if not m or m.group(1) in seen:
        continue
    seen.add(m.group(1))
    b = b[b.find(">") + 1:]  # drop the <li ...> attributes
    b = re.sub(r"<(script|style|svg)[\s\S]*?</\1>", " ", b)
    b = re.sub(r'<span aria-hidden=true style="color: transparent !important">[^<]*</span>', "", b)
    txt = html.unescape(re.sub(r"<[^>]+>", "\n", b))
    toks = [t.strip() for t in txt.split("\n") if len(t.strip()) > 1]
    toks = [t for t in toks if not t.startswith(("{", "[", "Opens in a new", "watch "))
            and t not in ("Find more like this", "See all similar items on eBay.", "Shop on eBay",
                          "Results matching fewer words")]
    if not toks:
        continue
    flag = " [fewer-words]" if 0 <= cut < start else ""
    print(f"{m.group(1)}{flag} | " + " | ".join(toks[:12]))
    limit -= 1
    if not limit:
        break
