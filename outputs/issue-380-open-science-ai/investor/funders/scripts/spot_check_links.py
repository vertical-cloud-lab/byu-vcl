#!/usr/bin/env python3
"""Draw a seeded random sample of funder-venture links and pull, from the first page each link cites, the passages
that name the funder, so a person can judge in context whether the page shows that funder investing in that venture.

Writes data/verify/spot_check_sample.csv (one row per link, with up to two passages). The verdicts are added by hand
in data/verify/spot_check_verdicts.csv. Run from funders/ after build_funders.py.
"""
import concurrent.futures as cf, csv, random, re, sys
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
SEED, N_CORE, N_U4 = 20261126, 30, 10
GENERIC = {"capital", "ventures", "venture", "partners", "fund", "management", "investments", "group", "holdings", "the",
           "and", "llc", "inc", "ltd", "global", "growth", "equity", "labs", "technologies", "incl", "nventures"}


def page_text(url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        soup = BeautifulSoup(r.text, "lxml")
        for t in soup(["script", "style", "noscript"]):
            t.decompose()
        return re.sub(r"\s+", " ", soup.get_text(" ")), ""
    except Exception as e:  # noqa: BLE001
        return None, type(e).__name__


def passages(name, text, n=2, width=260):
    base = re.sub(r"\s*\(.*?\)", "", name).strip()
    toks = [t for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9.'-]+", base) if t.lower() not in GENERIC]
    pats = [re.escape(base)] + ([re.escape(max(toks, key=len))] if toks else [])
    out = []
    for p in pats:
        for m in re.finditer(p, text, re.I):
            out.append(text[max(0, m.start() - width):m.end() + width])
            if len(out) >= n:
                return out, p
        if out:
            return out, p
    return out, ""


def main():
    links = [l for l in csv.DictReader(open("data/investor_links.csv"))]
    rng = random.Random(SEED)
    core = [l for l in links if l["universe"] in ("U1", "U2", "U3")]
    u4 = [l for l in links if l["universe"] == "U4"]
    sample = rng.sample(core, N_CORE) + rng.sample(u4, N_U4)
    urls = [l["sources"].split(" | ")[0] for l in sample]
    with cf.ThreadPoolExecutor(8) as ex:
        pages = list(ex.map(page_text, urls))
    rows = []
    for i, (l, url, (text, err)) in enumerate(zip(sample, urls, pages), 1):
        ps, pat = passages(l["investor"], text) if text else ([], "")
        rows.append({"n": i, "investor": l["investor"], "venture": l["venture"], "universe": l["universe"],
                     "round_types": l["round_types"], "led": l["led"], "source": url,
                     "fetch": "ok" if text else err, "matched_on": pat,
                     "passage_1": ps[0] if ps else "", "passage_2": ps[1] if len(ps) > 1 else ""})
    import os
    os.makedirs("data/verify", exist_ok=True)
    with open("data/verify/spot_check_sample.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(len(rows), "links;", sum(r["fetch"] == "ok" for r in rows), "pages fetched;",
          sum(bool(r["passage_1"]) for r in rows), "with a passage naming the funder")


if __name__ == "__main__":
    main()
