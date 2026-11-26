#!/usr/bin/env python3
"""Re-check ventures with no funding found, without a search engine: read each one's own site (home and about pages)
and the README of its most-starred GitHub repositories, and keep every passage that mentions funding or backers.

Writes data/verify/none_found_sweep.csv (venture, page, passage). The passages are read by hand; rounds confirmed
that way are entered as a deal pass. Run from funders/.
"""
import concurrent.futures as cf, csv, re
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
PAT = re.compile(r"(y ?combinator|\byc [swfx]\d{2}\b|\b[swfx]\d{2}\b batch|backed by|funded by|investors?\b|seed round|"
                 r"pre-seed|series [ab]\b|raised \$|raises \$|venture capital|\bvc\b|angel investors?|sponsored by)", re.I)


def get(url):
    try:
        r = requests.get(url, headers=UA, timeout=20)
        return r.text if r.status_code == 200 else None
    except Exception:  # noqa: BLE001
        return None


def text_of(html_, is_md):
    if is_md:
        return re.sub(r"\s+", " ", html_)
    soup = BeautifulSoup(html_, "lxml")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    alts = " ".join(f"[logo: {i.get('alt')}]" for i in soup.find_all("img") if i.get("alt"))
    return re.sub(r"\s+", " ", soup.get_text(" ") + " " + alts)


def pages_for(v, vi, top):
    out = []
    m = re.search(r"site (https?://\S+)", vi.get("hint", ""))
    if m:
        site = m.group(1).rstrip("/;,")
        out += [(site, False), (site + "/about", False), (site + "/company", False)]
    for org in [o for o in vi.get("owners", "").split(";") if o][:2]:
        for repo in top.get(org, [])[:2]:
            out.append((f"https://raw.githubusercontent.com/{org}/{repo}/HEAD/README.md", True))
    return out


def main():
    vin = {r["key"]: r for r in csv.DictReader(open("data/ventures_input.csv"))}
    top = {}
    for r in csv.DictReader(open("../owners/data/finance_passes/input_all.csv")):
        top[r["owner"]] = [x.split(" (")[0].strip() for x in r["top_repos"].split("; ") if x.strip()]
    V = [v for v in csv.DictReader(open("data/ventures.csv"))
         if v["universe"] in ("U1", "U2", "U3") and v["funding_found"] in ("none_found", "bootstrapped_stated")
         and v.get("in_scope", "yes") == "yes"]
    jobs = [(v, url, md) for v in V for url, md in pages_for(v, vin[v["key"]], top)]
    with cf.ThreadPoolExecutor(16) as ex:
        res = list(ex.map(lambda j: get(j[1]), jobs))
    rows = []
    for (v, url, md), h in zip(jobs, res):
        if not h:
            continue
        t = text_of(h, md)
        seen = set()
        for m in PAT.finditer(t):
            a = max(0, m.start() - 200)
            if any(abs(a - s) < 300 for s in seen):
                continue
            seen.add(a)
            rows.append({"key": v["key"], "venture": v["venture"], "page": url, "match": m.group(0),
                         "passage": t[a:m.end() + 220]})
    import os
    os.makedirs("data/verify", exist_ok=True)
    with open("data/verify/none_found_sweep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["key", "venture", "page", "match", "passage"]); w.writeheader(); w.writerows(rows)
    print(len(V), "ventures;", len(jobs), "pages tried;", sum(1 for h in res if h), "read;", len(rows), "passages;",
          len({r["key"] for r in rows}), "ventures with a passage")


if __name__ == "__main__":
    main()
