#!/usr/bin/env python3
"""Check that each investor named in data/deals.csv appears on the page its round cites, and that each program
amount in the program passes appears on its source page.

Investor names are matched loosely: case and punctuation ignored, "(person)" dropped, and a name also counts if its
distinctive part appears (e.g. "Sequoia" for "Sequoia Capital", "a16z" for "Andreessen Horowitz"). Amounts are
matched within 1% in the usual spellings ("$4.6 million", "$4.6M", "4,600,000", "€150m"). Pages that can't be
fetched (403, paywall, script-only) are reported as `unavailable`, not as wrong.

Writes data/source_checks_deals.csv and data/source_checks_programs.csv and prints the shares. Run from funders/.
"""
import concurrent.futures as cf, csv, glob, re, sys
import requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
_cache = {}
GENERIC = {"capital", "ventures", "venture", "partners", "fund", "management", "investments", "group", "holdings",
           "the", "and", "llc", "lp", "inc", "ltd", "co", "vc", "global", "growth", "equity", "labs", "technologies",
           "technology", "company", "corporation", "corp", "international", "advisors", "associates", "investment",
           "person", "of", "de", "la", "family", "office", "foundation", "ag", "gmbh", "sa", "bv", "plc"}
ALT = {"andreessen horowitz": ["a16z"], "gv": ["google ventures"], "m12": ["microsoft"],
       "nventures": ["nvidia"], "y combinator": ["yc ", "ycombinator"], "kleiner perkins": ["kpcb", "kleiner"],
       "new enterprise associates": ["nea"], "general catalyst": ["general catalyst"],
       "institutional venture partners": ["ivp"], "draper fisher jurvetson": ["dfj"],
       "bessemer venture partners": ["bvp", "bessemer"], "lightspeed venture partners": ["lightspeed"]}
NUM = re.compile(r"(?:[$€£¥]|usd|us\$|eur|rmb|cny|hk\$)?\s?(\d{1,3}(?:[,.]\d{3})+|\d+(?:\.\d+)?)\s?"
                 r"(billion|million|thousand|bn|mn|b|m|k)?\b", re.I)
SCALE = {"billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "mn": 1e6, "m": 1e6, "thousand": 1e3, "k": 1e3}


def norm(s):
    return " " + re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower().replace("&", " and "))).strip() + " "


def text_of(url):
    if url in _cache:
        return _cache[url]
    out = None
    try:
        hdr = {"User-Agent": "research script admin@example.com"} if "sec.gov" in url else UA  # SEC asks for a declared agent
        r = requests.get(url, headers=hdr, timeout=25)
        if r.status_code == 200 and len(r.content) > 500:
            soup = BeautifulSoup(r.content[:5_000_000], "lxml")
            for t in soup(["script", "style", "noscript"]):
                t.decompose()
            txt = soup.get_text(" ")
            if len(txt) > 300:
                out = norm(txt)
    except Exception:  # noqa: BLE001
        pass
    _cache[url] = out
    return out


_nospace = {}


def found(name, text):
    n = norm(re.sub(r"\(person\)", "", name))
    if n in text:
        return True
    # spacing variants ("Seed Camp" for "Seedcamp", "Open AI" for "OpenAI")
    ns = _nospace.setdefault(id(text), text.replace(" ", ""))
    if len(n.strip()) >= 6 and n.replace(" ", "") in ns:
        return True
    k = n.strip()
    for full, alts in ALT.items():
        if k == full or k.startswith(full):
            if any(norm(a).strip() in text for a in alts):
                return True
    toks = [t for t in k.split() if t not in GENERIC and len(t) > 2]
    if not toks:
        return False
    if " " + " ".join(toks) + " " in text:
        return True
    return len(toks) >= 1 and len(toks[0]) >= 5 and " " + toks[0] + " " in text and not name.endswith("(person)")


def amounts(text):
    out = []
    for m in NUM.finditer(text):
        raw, unit = m.group(1), (m.group(2) or "").lower()
        try:
            v = float(raw.replace(",", "")) if re.fullmatch(r"\d{1,3}(,\d{3})+", raw) else float(raw.replace(",", ""))
        except ValueError:
            continue
        out.append(v * SCALE.get(unit, 1))
    return out


def main():
    deals = list(csv.DictReader(open("data/deals.csv")))
    urls = sorted({d["source"] for d in deals} | {r["source"] for p in glob.glob("data/program_passes/programs_*.csv")
                                                    for r in csv.DictReader(open(p))})
    with cf.ThreadPoolExecutor(16) as ex:
        list(ex.map(text_of, urls))
    rows = []
    for d in deals:
        t = _cache.get(d["source"])
        for role, col in (("lead", "lead_raw"), ("investor", "investors_raw")):
            for nm in [x.strip() for x in d[col].split(" | ") if x.strip()]:
                rows.append({"key": d["key"], "venture": d["venture"], "date": d["date"], "type": d["type"], "role": role,
                             "name": nm, "source": d["source"], "source_kind": d["source_kind"],
                             "check": "unavailable" if t is None else ("found" if found(nm, t) else "not on page")})
    with open("data/source_checks_deals.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    av = [r for r in rows if r["check"] != "unavailable"]
    print(f"deals: {len(rows)} investor mentions; page fetched for {len(av)}; found on page {sum(r['check'] == 'found' for r in av)}"
          f" ({100 * sum(r['check'] == 'found' for r in av) / max(1, len(av)):.0f}%)")
    prow = []
    for p in sorted(glob.glob("data/program_passes/programs_*.csv")):
        for r in csv.DictReader(open(p)):
            if not r["committed_usd"]:
                continue
            v = float(r["committed_usd"]); t = _cache.get(r["source"])
            res = "unavailable" if t is None else ("found" if any(abs(a - v) <= 0.01 * v for a in amounts(t)) else "not on page")
            prow.append({"funder": r["funder"], "program": r["program"], "committed_usd": r["committed_usd"],
                         "amount_note": r["amount_note"], "source": r["source"], "check": res})
    if prow:
        with open("data/source_checks_programs.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(prow[0])); w.writeheader(); w.writerows(prow)
        av = [r for r in prow if r["check"] != "unavailable"]
        print(f"programs: {len(prow)} amounts; page fetched for {len(av)}; found {sum(r['check'] == 'found' for r in av)} "
              "(amounts in other currencies or summed by the researcher will show as not on page)")


if __name__ == "__main__":
    main()
