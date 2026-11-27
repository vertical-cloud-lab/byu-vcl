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
    # ---- what changes from round 5 (generated)
    def f(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None
    ok = [r for r in st_rows if r.get("used_ok") in ("True", "true", "1")]
    keys_ok = {r["station"] for r in ok}
    lost = sorted(k for k in USED_OK if k not in keys_ok)
    gained = sorted(k for k in keys_ok if k not in USED_OK)
    med = lambda xs: sorted(xs)[len(xs) // 2] if xs else None
    pf = [f(r["price_frac"]) for r in ok if f(r["price_frac"]) is not None]
    lw = [f(r["lead_w"]) for r in ok if f(r["lead_w"]) is not None]
    pfa = [f(r["p_fault"]) for r in ok if f(r["p_fault"]) is not None]
    out.append("## What changes from round 5\n")
    out.append(f"* **Stations with a real used market at a saving** (`used_ok`, {len(ok)}): "
               + ", ".join(f"`{r['station']}`" for r in sorted(ok, key=lambda r: r['station'])) + ".")
    out.append(f"* **In round 5's `USED_OK` but not supported by the market** ({len(lost)}): "
               + (", ".join(f"`{k}`" for k in lost) or "none") + ".")
    out.append(f"* **Not in `USED_OK` but with a real used market** ({len(gained)}): "
               + (", ".join(f"`{k}`" for k in gained) or "none") + " (the conventional lab's keys among them aren't in "
               "round 4's `BUILD`).")
    if pf:
        out.append(f"* Across the `used_ok` stations, the median `price_frac` is {med(pf):.2f} (round 5: 0.45), the "
                   f"median `lead_w` {med(lw):.1f} weeks (round 5: 2) and the median `p_fault` {med(pfa):.2f} "
                   f"(round 5: 0.25).")
    out.append("")
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
    out.append("| Key | Lab | In `USED_OK` | Market | Listings (N. America) | Priced | Median used, all | Priced on "
               "| Discount vs new | `price_frac` | `lead_w` | `p_fault` (best) | `extra_com_w` | Order to working, used / new (weeks) |")
    out.append("| --- | --- | :-: | --- | --: | --: | --: | --- | --: | --: | --: | --: | --: | --: |")
    order = {r["station"]: i for i, r in enumerate(N)}
    for r in sorted(st_rows, key=lambda r: order.get(r["station"], 999)):
        k = r["station"]
        med = money(r["median_used_usd"])
        basis = r.get("price_basis") or ""
        btxt = (f"{basis}: {money(r.get('median_basis_usd'))}" if r.get("median_basis_usd") else
                ("components (below)" if r["component"] == "(station)" and r.get("price_frac") else ""))
        otw = (f"{num(r.get('order_to_working_used_w'), 1)} / {num(r.get('order_to_working_new_w'), 1)}"
               if r.get("order_to_working_used_w") else (f"– / {num(r.get('order_to_working_new_w'), 1)}"
                                                          if r.get("order_to_working_new_w") else ""))
        out.append(f"| `{k}` | {r['lab']} | {'yes' if k in USED_OK else ''} | {r['market']} | "
                   f"{r['n_listings'] or 0} ({r['n_north_america'] or 0}) | {r['n_priced'] or 0} | {med} | {btxt} | "
                   f"{pct(r['discount_vs_new'])} | {num(r['price_frac'])} | {num(r['lead_w'], 1)} | "
                   f"{num(r['p_fault'])}{(' (' + num(r['p_fault_best']) + ')') if r.get('p_fault_best') else ''} | "
                   f"{num(r['extra_com_w'], 1)} | {otw} |")
    out.append("")
    if comp_rows:
        out.append("### Stations that are several machines\n")
        out.append("| Key | Component | New (each) | Market | Listings (N. America) | Priced | Priced on | `price_frac` | `lead_w` |")
        out.append("| --- | --- | --: | --- | --: | --: | --- | --: | --: |")
        for k in sorted(comp_rows, key=lambda k: order.get(k, 999)):
            for r in comp_rows[k]:
                out.append(f"| `{k}` | {r['component']} | {money(r['new_usd_each'])} | {r['market']} | "
                           f"{r['n_listings'] or 0} ({r['n_north_america'] or 0}) | {r['n_priced'] or 0} | "
                           f"{(r.get('price_basis') or '') + (': ' + money(r.get('median_basis_usd')) if r.get('median_basis_usd') else '')} | "
                           f"{num(r['price_frac'])} | {num(r['lead_w'], 1)} |")
        out.append("")
    # ---- examples per station: a few priced listings that went into the statistics, like-for-like and North America first
    out.append("## Examples by station\n")
    out.append("Up to three priced listings per key that count in the statistics, the twin's own model and North "
               "America first (all of them are in `listings.csv`).\n")
    pri = {"exact": 0, "family": 1, "sub": 2}
    by = defaultdict(list)
    for r in L:
        if r.get("in_price_stats") == "1":
            by[r["station"]].append(r)
    seen_keys = [n["station"] for n in N]
    for k in dict.fromkeys(seen_keys):
        xs = by.get(k, [])
        if not xs:
            continue
        xs.sort(key=lambda r: (pri.get(r["match"], 3), r["region"] not in ("US", "CA"), float(r["price_usd"])))
        items = []
        for r in xs[:3]:
            yr = f"{r['year']}, " if r.get("year") else ""
            items.append(f"[{r['title'][:70].strip()}]({r['url']}) ({r['match']}; {money(r['price_usd'])}; "
                         f"{yr}{r['condition'].replace('_', ' ')}; {r['location'][:40] or r['region'] or 'location not given'}; "
                         f"{r['source']})")
        out.append(f"* `{k}`: " + "; ".join(items) + ".")
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
    # ---- the summary bullets: tools/inshort.md filled from the numbers
    try:
        tmpl = (Path(__file__).resolve().parent / "inshort.md").read_text()
    except FileNotFoundError:
        tmpl = ""
    if tmpl:
        okr = [r for r in st_rows if r.get("used_ok") in ("True", "true", "1")]
        pfs = sorted(f(r["price_frac"]) for r in okr if f(r["price_frac"]) is not None)
        leads = sorted(f(r["lead_w"]) for r in okr if f(r["lead_w"]) is not None)
        saved = sorted(f(r["order_to_working_new_w"]) - f(r["order_to_working_used_w"]) for r in okr
                       if f(r.get("order_to_working_new_w")) is not None and f(r.get("order_to_working_used_w")) is not None)
        pfa_ = sorted(f(r["p_fault"]) for r in okr if f(r["p_fault"]) is not None)
        pfb_ = sorted(f(r["p_fault_best"]) for r in okr if f(r.get("p_fault_best")) is not None)
        S_ = {r["station"]: r for r in st_rows}
        C_ = {(r["station"], r["component"]): r for r in S}
        md = lambda xs, nd=2: (f"{xs[len(xs) // 2]:.{nd}f}" if xs else "n/a")
        BUILD = {"services", "hoods", "glovebox", "shuttle", "units", "couplings", "ups", "cameras", "midi", "mxlab", "edm",
                 "instron", "chamber", "zwick", "machining", "icpms", "sieve_cell", "furnaces", "sem", "eds", "ebsd", "xrd",
                 "xrf", "mastersizer", "hardness", "nanoindenter", "pip", "vhx", "polish", "carvera", "doser",
                 "floor_unit", "cubxl"}                              # round4.BUILD: what rounds 4-5 schedule
        g_v = [k for k in gained if k in BUILD]
        g_c = [k for k in gained if k not in BUILD]
        lost_txt = ("The market doesn't support " + ", ".join(f"`{k}`" for k in lost) +
                    " (round 5 allowed them used)." if lost else "Every station in round 5's `USED_OK` has a market.")
        gained_txt = (("It does support " + ", ".join(f"`{k}`" for k in g_v) +
                       ", which round 5 kept new.") if g_v else "") + (
                      (" The conventional lab's own items, which the rounds don't schedule, have used markets too ("
                       + ", ".join(f"`{k}`" for k in g_c) + ").") if g_c else "")
        fill = dict(pf_med=md(pfs), pf_min=f"{pfs[0]:.2f}" if pfs else "n/a", pf_max=f"{pfs[-1]:.2f}" if pfs else "n/a",
                    midi_n=S_.get("midi", {}).get("n_listings", "0"), midi_na=S_.get("midi", {}).get("n_north_america", "0"),
                    arm_n=C_.get(("units", "arm"), {}).get("n_listings", "0"), mir_n=C_.get(("units", "mir"), {}).get("n_listings", "0"),
                    lead_med=md(leads, 1), saved_med=md(saved, 1), pfa_med=md(pfa_), pfb_med=md(pfb_),
                    lost_txt=lost_txt, gained_txt=gained_txt)
        body = tmpl.format(**fill)
        txt0 = (d / "README.md").read_text()
        txt0 = re.sub(r"<!-- inshort:start -->.*?<!-- inshort:end -->",
                      "<!-- inshort:start -->\n" + body.strip() + "\n<!-- inshort:end -->", txt0, flags=re.S)
        (d / "README.md").write_text(txt0)
    txt = (d / "README.md").read_text()
    new = re.sub(r"<!-- tables:start -->.*?<!-- tables:end -->",
                 "<!-- tables:start -->\n" + "\n".join(out) + "\n<!-- tables:end -->", txt, flags=re.S)
    (d / "README.md").write_text(new)
    print("README tables:", len(out), "lines")


if __name__ == "__main__":
    main(sys.argv[1])
