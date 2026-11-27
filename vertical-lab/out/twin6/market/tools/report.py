"""Fill README.md's tables from summary.csv, listings.csv, new.csv, sources.csv and visits.csv.

    python3 report.py <market dir>
"""
import csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path

USED_OK = {"edm", "instron", "zwick", "chamber", "icpms", "sem", "xrd", "xrf", "mastersizer", "hardness",
           "nanoindenter", "polish", "furnaces", "vhx"}           # round5.py at 4bb91b1
R5 = dict(price_frac=0.45, lead_w=2.0, p_fault=0.25, refurb_w=6.0, refurb_frac=0.15, extra_com_w=1.0)


def rd(p):
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def money(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return ""
    return f"${v/1000:,.0f}k" if v >= 10_000 else f"${v:,.0f}"


def num(x, nd=2):
    try:
        return f"{float(x):.{nd}f}"
    except (TypeError, ValueError):
        return ""


def pct(x):
    try:
        return f"{float(x)*100:.0f} %"
    except (TypeError, ValueError):
        return ""


def main(d):
    d = Path(d)
    S = rd(d / "summary.csv")
    L = rd(d / "listings.csv")
    N = rd(d / "new.csv")
    out = []
    st_rows = [r for r in S if r["component"] in ("", "(station)")]
    comp_rows = defaultdict(list)
    for r in S:
        if r["component"] not in ("", "(station)"):
            comp_rows[r["station"]].append(r)
    out.append("## Results by station\n")
    out.append("Round 5's stand-ins, for comparison: `price_frac` 0.45, `lead_w` 2, `p_fault` 0.25, `refurb_w` 6, "
               "`refurb_frac` 0.15, `extra_com_w` 1. **Market**: *yes* = at least 5 listings that fit, 2 of them in "
               "North America, one priced; *thin* = fewer; *none* = nothing found. Prices are asking prices in USD; "
               "*like-for-like* is the median over the twin's own model and its maker's line only. `price_frac` "
               "is the median used price plus freight and rigging, over the twin's new price.\n")
    out.append("| Key | Lab | In `USED_OK` | Market | Listings (N. America) | Priced | Median used (like-for-like) "
               "| Discount vs new | `price_frac` | `lead_w` | `p_fault` (best) | `extra_com_w` |")
    out.append("| --- | --- | :-: | --- | --: | --: | --: | --: | --: | --: | --: | --: |")
    order = {r["station"]: i for i, r in enumerate(N)}
    for r in sorted(st_rows, key=lambda r: order.get(r["station"], 999)):
        k = r["station"]
        med = money(r["median_used_usd"])
        mef = money(r.get("median_exact_family_usd"))
        medtxt = (med + (f" ({mef})" if mef and mef != med else "")) if med else (f"({mef})" if mef else "")
        out.append(f"| `{k}` | {r['lab']} | {'yes' if k in USED_OK else ''} | {r['market']} | "
                   f"{r['n_listings'] or 0} ({r['n_north_america'] or 0}) | {r['n_priced'] or 0} | {medtxt} | "
                   f"{pct(r['discount_vs_new'])} | {num(r['price_frac'])} | {num(r['lead_w'], 1)} | "
                   f"{num(r['p_fault'])}{(' (' + num(r['p_fault_best']) + ')') if r.get('p_fault_best') else ''} | "
                   f"{num(r['extra_com_w'], 1)} |")
    out.append("")
    if comp_rows:
        out.append("### Stations that are several machines\n")
        out.append("| Key | Component | New (each) | Market | Listings (N. America) | Priced | Median used | `price_frac` |")
        out.append("| --- | --- | --: | --- | --: | --: | --: | --: |")
        for k in sorted(comp_rows, key=lambda k: order.get(k, 999)):
            for r in comp_rows[k]:
                out.append(f"| `{k}` | {r['component']} | {money(r['new_usd_each'])} | {r['market']} | "
                           f"{r['n_listings'] or 0} ({r['n_north_america'] or 0}) | {r['n_priced'] or 0} | "
                           f"{money(r['median_used_usd'])} | {num(r['price_frac'])} |")
        out.append("")
    out.append("## New price and the vendor's stated lead time\n")
    out.append("Most instrument makers quote lead times only on request; the leads below are the ones a vendor or "
               "distributor publishes. The twin's lead (round 4's `BUILD`, including BYU's 2-week purchase order) is "
               "assumed for every item but the room.\n")
    out.append("| Key | Item | New, each | Vendor's stated lead | Twin's lead (weeks) |")
    out.append("| --- | --- | --: | --- | --: |")
    for n in N:
        if n["vendor_lead_text"] and n["vendor_lead_text"] not in ("quote only", "custom", ""):
            src = n["lead_source"]
            txt = n["vendor_lead_text"] + (f" ([source]({src}))" if src.startswith("http") else "")
            out.append(f"| `{n['station']}` | {n['item']} | {money(n['new_usd_each'])} | {txt} | {n['twin_lead_w']} |")
    out.append("")
    out.append("## Sources\n")
    out.append("| Source | Kind | Access | Pages read | Listings kept |")
    out.append("| --- | --- | --- | --: | --: |")
    src = rd(d / "sources.csv")
    kept = Counter(r["source"] for r in L if r.get("keep", "1") == "1")
    for s in src:
        out.append(f"| [{s['source']}]({s['url']}) | {s['kind']} | {s['access']} | {s.get('pages_read', '')} | "
                   f"{kept.get(s.get('key', ''), '') if s.get('key') else ''} |")
    out.append("")
    txt = (d / "README.md").read_text()
    new = re.sub(r"<!-- tables:start -->.*?<!-- tables:end -->",
                 "<!-- tables:start -->\n" + "\n".join(out) + "\n<!-- tables:end -->", txt, flags=re.S)
    (d / "README.md").write_text(new)
    print("README tables:", len(out), "lines")


if __name__ == "__main__":
    main(sys.argv[1])
