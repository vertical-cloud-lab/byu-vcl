#!/usr/bin/env python3
"""Y Combinator companies that call themselves open source, from the yc-oss mirror of YC's public directory.

Two definitions: tagged `open-source` in the directory (the company chose the tag), or described as open source in
its one-liner or long description (also catches open-weight models). Downloads the mirror's all.json (dated by its
meta.json `last_updated`) and writes data/yc_open_source.csv. Run from funders/.
"""
import csv, json, re, sys, urllib.request

SRC = "https://yc-oss.github.io/api/companies/all.json"
OPEN = re.compile(r"\bopen[- ]?(source|sourced|core|weights?|hardware)\b", re.I)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    data = json.load(open(path)) if path else json.load(urllib.request.urlopen(urllib.request.Request(SRC, headers={"User-Agent": "Mozilla/5.0"})))
    rows = []
    for c in data:
        tags = [t.lower() for t in (c.get("tags") or [])]
        text = " ".join(str(c.get(k) or "") for k in ("one_liner", "long_description"))
        tagged = "open source" in tags or "open-source" in tags
        m = OPEN.search(text)
        if not (tagged or m):
            continue
        rows.append({"name": c.get("name"), "batch": c.get("batch"), "year": (re.findall(r"\d{4}", c.get("batch") or "") or [""])[0],
                     "status": c.get("status"), "tagged_open_source": int(tagged), "described_open": int(bool(m)),
                     "match": (m.group(0) if m else ""), "industry": c.get("industry"), "website": c.get("website"),
                     "one_liner": c.get("one_liner"), "yc_url": c.get("url"), "nonprofit": int(bool(c.get("nonprofit")))})
    rows.sort(key=lambda r: (r["year"], r["name"] or ""))
    with open("data/yc_open_source.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    t = sum(r["tagged_open_source"] for r in rows); d = sum(r["described_open"] for r in rows)
    print(f"{len(data)} YC companies; {len(rows)} tagged or described open ({t} tagged, {d} described, "
          f"{sum(1 for r in rows if r['tagged_open_source'] and r['described_open'])} both)")


if __name__ == "__main__":
    main()
