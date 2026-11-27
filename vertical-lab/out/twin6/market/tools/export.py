"""visits.jsonl -> visits.csv, and the page counts per source into sources.csv.

    python3 export.py <market dir>
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

HOST = {"labx.com": "labx", "machinio.com": "machinio", "govdeals.com": "govdeals", "allsurplus.com": "allsurplus",
        "publicsurplus.com": "publicsurplus", "fedequip.com": "fedequip", "machineseeker.com": "machineseeker",
        "exapro.com": "exapro", "dotmed.com": "dotmed", "marshallscientific.com": "marshall", "ebay.com": "ebay",
        "bidspotter.com": "bidspotter", "equipnet.com": "equipnet", "surplusrecord.com": "surplusrecord",
        "biosurplus.com": "biosurplus", "gsaadvantage.gov": "gsa", "haascnc.com": "haas", "makera.com": "makera",
        "equipt.com": "equipt", "caeonline.com": "cae", "robotsdoneright.com": "rdr", "ipinfo.io": "ipinfo",
        "conquerscientific.com": "conquer", "gmi-inc.com": "gmi", "semtechsolutions.com": "semtech"}


def site_of(url):
    for h, k in HOST.items():
        if h in (url or ""):
            return k
    return ""


def main(d):
    d = Path(d)
    rows = []
    for l in open("/tmp/market/raw/visits.jsonl"):
        v = json.loads(l)
        lab = v.get("label", "")
        kind = "search" if lab.startswith("search|") else "listing" if lab.startswith("detail|") else \
            "excluded (two crawlers on one tab)" if lab.startswith("contaminated") else "probe or vendor page"
        rows.append(dict(t_utc=v["t_utc"], kind=kind, site=site_of(v["url"]), url=v["url"], status=v.get("status"),
                         blocked=v.get("blocked") or "", error=(v.get("error") or "")[:80], title=(v.get("title") or "")[:90]))
    with open(d / "visits.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    n = Counter(r["site"] for r in rows)
    src = list(csv.DictReader(open(d / "sources.csv")))
    for s in src:
        k = site_of(s["url"])
        s["key"] = k
        s["pages_read"] = n.get(k, 0)
    keys = ["source", "key", "url", "kind", "access", "checked_utc", "pages_read", "note"]
    with open(d / "sources.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(src)
    print(len(rows), "visits;", dict(n))


if __name__ == "__main__":
    main(sys.argv[1])
