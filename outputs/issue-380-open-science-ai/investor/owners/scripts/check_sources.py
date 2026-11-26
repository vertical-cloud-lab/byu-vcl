#!/usr/bin/env python3
"""Check that each sourced figure in data/core_financials.csv appears on the page it cites.

For every number column with a URL (exit, funding, valuation, peak value), the cited page (or each page, when a
cell lists several separated by '|') is fetched and its text searched for the amount written the usual ways:
"$4.6 million", "$4.6M", "4.6 million", "$4,600,000", "€150m", "$1.2 billion", "1.2B" and so on, within 1%
rounding. A total that is a sum of rounds will often not appear as such; those are reported as `not on page`,
which flags them for reading rather than marking them wrong.

Pages are fetched through scripts/via_pi.py: from the runner first, then with a browser's TLS fingerprint, then
through a lab Pi's SSH SOCKS tunnel, then from the Internet Archive. The route that worked is recorded per figure
(`route`). Without the tunnel the Pi step simply fails and the rest of the ladder still runs.

Writes data/source_checks.csv (one row per figure) and prints the share confirmed. Run from owners/.
"""
import concurrent.futures as cf, re, sys
import numpy as np, pandas as pd

sys.path.insert(0, "scripts")
import via_pi  # noqa: E402

PAIRS = [("exit_value_usd", "exit_source"), ("total_funding_usd", "funding_source"),
         ("last_valuation_usd", "valuation_source"), ("peak_value_usd", "peak_source")]
_cache = {}
NUM = re.compile(r"(?:[$€£¥]|usd|us\$|eur|rmb|cny|hk\$)?\s?(\d{1,3}(?:[,.]\d{3})+|\d+(?:\.\d+)?)\s?"
                 r"(billion|million|thousand|bn|mn|b|m|k)?\b", re.I)
SCALE = {"billion": 1e9, "bn": 1e9, "b": 1e9, "million": 1e6, "mn": 1e6, "m": 1e6, "thousand": 1e3, "k": 1e3}


def text_of(url):
    if url not in _cache:
        res = via_pi.get(url)
        _cache[url] = (via_pi.text_of_html(res["body"]) if res["ok"] else None, res["route"] if res["ok"] else "")
    return _cache[url]


def amounts(text):
    out = []
    for m in NUM.finditer(text):
        raw, unit = m.group(1), (m.group(2) or "").lower()
        if re.fullmatch(r"\d{1,3}(?:,\d{3})+", raw):
            v = float(raw.replace(",", ""))
        elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", raw) and not unit:
            v = float(raw.replace(".", ""))
        else:
            try:
                v = float(raw.replace(",", ""))
            except ValueError:
                continue
        out.append(v * SCALE.get(unit, 1))
    return np.array(out)


def check(value, urls):
    res, route, first = "fetch failed", "", None
    for u in urls:
        t, rt = text_of(u)
        if t is None:
            continue
        a = amounts(t)
        if len(a) and np.any(np.abs(a - value) <= 0.01 * value + 1):
            return "confirmed", u, rt
        res, route, first = "not on page", route or rt, first or u
    return res, first or (urls[0] if urls else ""), route


def main():
    F = pd.read_csv("data/core_financials.csv")
    jobs = []
    for r in F.itertuples(index=False):
        for col, src in PAIRS:
            v, s = getattr(r, col), str(getattr(r, src) or "")
            if pd.notna(v) and v > 0 and s.startswith("http"):
                urls = [u.strip() for u in re.split(r"\s*\|\s*|\s+", s) if u.strip().startswith("http")]
                jobs.append((r.owner, r.entity, col, float(v), urls))
    rows = []
    with cf.ThreadPoolExecutor(12) as ex:
        futs = {ex.submit(check, v, urls): (o, e, c, v, urls) for o, e, c, v, urls in jobs}
        for f in cf.as_completed(futs):
            o, e, c, v, urls = futs[f]
            res, u, rt = f.result()
            rows.append({"owner": o, "entity": e, "field": c, "value_usd": v, "result": res, "url": u, "route": rt})
    d = pd.DataFrame(rows).sort_values(["owner", "field"])
    d.to_csv("data/source_checks.csv", index=False)
    print(d.result.value_counts().to_string())
    ok = d[d.result != "fetch failed"]
    print("confirmed share of fetched:", round((ok.result == "confirmed").mean(), 3), "n", len(ok))
    print(d.groupby("field").result.value_counts().unstack(fill_value=0).to_string())
    print(d[d.result != "fetch failed"].groupby("route").result.value_counts().unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main()
