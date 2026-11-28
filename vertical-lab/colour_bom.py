"""The colour-coding scheme's bill of materials: merge the priced lines, total them, write the CSV and shopping list.

Sterling, PR #377, 2026-11-22: "Use the raspberry Pi to look up specific codes, items, prices, sellers, lead times, and
any other pertinent information related to the above suggestions and searches. Come up with a full bill of materials
and shopping list for this."

Each group's lines are in out/colour/bom/<group>.json. They were looked up on 2026-11-22 through an SSH SOCKS tunnel
via the CubXL Pi, whose traffic leaves from BYU's own network (AS6510), so the sellers saw a campus visitor rather than
a datacenter. Every price and lead time comes from a page read that way, and its URL is on the line. Prices are per
pack at quantity 1, before shipping and tax (BYU is tax-exempt).

    python3 colour_bom.py      # writes out/colour/bom.csv and bom.md (by group), shopping_list.md (by seller),
                               # bom_totals.json (with the floor tape lengths) and buying_colours.json

The write-up is notes/colour_bom.md; the scheme itself is notes/colour_coding.md.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "out" / "colour" / "bom"
OUT = HERE / "out" / "colour"

GROUPS = {   # in the order the write-up takes them
    "family": "Alloy-family marking, tools and containers",
    "labels": "Labels and markers",
    "floor": "Floor marking",
    "lights": "Stack lights",
    "kit": "A second kit for the Cu family",
}
PRIORITY = ("now", "soon", "optional")
SELLER = {   # one name per seller, so that each table in the shopping list is one order
    "Wolf Automation (Marshall Wolf Automation, Algonquin IL)": "Wolf Automation",
    "Brother USA (brother-usa.com)": "Brother USA", "Primera (primera.com)": "Primera",
    "Nilfisk Direct (nilfiskcfm.com)": "Nilfisk Direct", "STERIS shop / PartsSource": "STERIS shop",
    "Amazon (sold by ANDONT, ships from Amazon)": "Amazon", "Nix Sensor (direct)": "Nix Sensor",
    "Nilfisk dealer (quote)": "Nilfisk dealer (quote)", None: "(quote)"}
COLS = ["group", "priority", "item", "maker", "part_no", "seller", "seller_sku", "pack", "qty_packs",
        "unit_price_usd", "line_usd", "stock_or_lead_time", "qty_basis", "url", "price_date", "notes"]


def floor_lengths() -> dict:
    """Tape lengths from the set-up floor (out/tray_plan.json), drawn as colour_coding.floor_figure draws them: the
    two lane edges; the hazard zones 1 m round each docked MiR250, overlapping zones merged and the tape stopping at a
    machine's face; and a white outline round each docked robot."""
    import numpy as np
    from shapely.geometry import box
    from shapely.ops import unary_union
    from colour_coding import ZONE_MM
    plan = json.loads((HERE / "out" / "tray_plan.json").read_text())["floor"]
    mir = (580.0, 890.0)                                    # MiR250 footprint, as in colour_coding.floor_figure
    zones, white = [], 0.0
    for dk in plan["docks"].values():
        dx, dy = dk["dock"][:2]
        a = dk["dock"][2] if len(dk["dock"]) > 2 else 0
        w, h = (mir[1], mir[0]) if abs(np.sin(np.radians(a))) > 0.7 else mir
        zones.append(box(dx - w / 2 - ZONE_MM, dy - h / 2 - ZONE_MM, dx + w / 2 + ZONE_MM, dy + h / 2 + ZONE_MM))
        white += 2 * (w + h)
    un = unary_union(zones)
    machines = unary_union([box(a, c, b, d) for a, b, c, d in plan["machines"].values()])
    x0, x1, _, _ = plan["aisle_mm"]
    return dict(docks=len(plan["docks"]), hazard_outlines=len(getattr(un, "geoms", [un])),
                lane_edges_m=round(2 * (x1 - x0) / 1000, 1),
                hazard_tape_m=round(un.boundary.difference(machines).length / 1000, 1),
                hazard_perimeter_m=round(un.boundary.length / 1000, 1),
                dock_outlines_m=round(white / 1000, 1))


# Paint and print codes for ordering custom items (shadow boards, signs, powder coat) by a code rather than "blue".
# sRGB values are the usual published approximations of each swatch, which is all a colour-vision check needs; the
# physical swatch, under the lab's own lights, is what to match.
SWATCHES = {
    "Al": {"RAL 5015 sky blue": "#2271B3", "Pantone 300 C": "#005EB8", "RAL 5017 traffic blue": "#063971",
           "RAL 5005 signal blue": "#1E2460"},
    "Cu": {"Pantone 1375 C": "#FF9E1B", "RAL 1028 melon yellow": "#F4A900", "safety orange (ANSI Z535.1)": "#FF7900",
           "RAL 2003 pastel orange": "#FF7514", "RAL 2000 yellow orange": "#ED760E", "Pantone 021 C": "#FE5000",
           "RAL 2004 pure orange": "#F44611"},
}


def buying_colours() -> dict:
    """Each candidate swatch against the scheme's other colours (the other family, the reserved brown, the black
    neutral), worst case over normal, protan, deutan and tritan vision, graded as colour_coding.check grades."""
    from colour_coding import FAMILY, NEUTRAL, PASS, FLOOR_MARK, VISION, _rgb1, delta, simulate
    ref = {"Al blue": FAMILY["Al"]["rgb"], "Cu orange": FAMILY["Cu"]["rgb"], "reserved brown": FAMILY["next"]["rgb"],
           "black neutral": NEUTRAL["general"]["rgb"]}
    res = {}
    for fam, sw in SWATCHES.items():
        for name, h in sw.items():
            row = {}
            for rn, rh in ref.items():
                if rn.startswith(fam):
                    continue
                d = {v: delta(simulate(_rgb1(h), k), simulate(_rgb1(rh), k)) for v, k in VISION.items()}
                w = min(d, key=d.get)
                row[rn] = dict(worst=round(d[w], 1), vision=w, grade="pass" if d[w] >= PASS else
                               ("needs a second cue" if d[w] >= FLOOR_MARK else "FAIL"))
            res[f"{fam}: {name} ({h})"] = row
    return res


def load() -> list[dict]:
    rows = []
    for g in GROUPS:
        f = SRC / f"{g}.json"
        if not f.exists():
            continue
        for r in json.loads(f.read_text()):
            r = dict(r)
            r["group"] = g
            r["seller"] = SELLER.get(r.get("seller"), r.get("seller"))
            q, p = r.get("qty_packs"), r.get("unit_price_usd")
            r["line_usd"] = round(float(q) * float(p), 2) if isinstance(q, (int, float)) and \
                isinstance(p, (int, float)) else None
            rows.append(r)
    return rows


def money(x) -> str:
    if x is None:
        return "quote"
    try:
        return f"${float(x):,.2f}"
    except (TypeError, ValueError):
        return str(x)


def totals(rows: list[dict]) -> dict:
    t = {g: {p: 0.0 for p in PRIORITY} | {"unpriced": 0} for g in GROUPS}
    for r in rows:
        g, p = r["group"], r.get("priority") or "optional"
        if r["line_usd"] is None:
            t[g]["unpriced"] += 1
        else:
            t[g][p if p in PRIORITY else "optional"] += r["line_usd"]
    t["all"] = {k: round(sum(t[g][k] for g in GROUPS), 2) for k in (*PRIORITY, "unpriced")}
    for g in GROUPS:
        t[g] = {k: round(v, 2) for k, v in t[g].items()}
    return t


def shopping_list(rows: list[dict]) -> str:
    """One table per seller, so each table is one order. Optional lines are listed after the rest of that seller's."""
    by = defaultdict(list)
    for r in rows:
        by[r.get("seller") or "(quote)"].append(r)
    order = sorted(by, key=lambda s: (-sum(r["line_usd"] or 0 for r in by[s] if r.get("priority") != "optional"), s))
    out = ["# Shopping list by seller", "",
           "Generated by `colour_bom.py` from `out/colour/bom/*.json`. Prices are per pack at qty 1 as shown on "
           "2026-11-22, before shipping and tax; each links to the page it was read from.", ""]
    for s in order:
        rr = sorted(by[s], key=lambda r: (PRIORITY.index(r.get("priority")) if r.get("priority") in PRIORITY else 3,
                                          r["group"], r.get("item", "")))
        sub = sum(r["line_usd"] or 0 for r in rr if r.get("priority") != "optional")
        out += [f"## {s}", "", f"Subtotal without the optional lines: {money(sub)}", "",
                "| Priority | Item | Maker part no. | Seller SKU | Pack | Qty | Unit | Line | Stock or lead time |",
                "|---|---|---|---|---|---|---|---|---|"]
        for r in rr:
            sku = r.get("seller_sku") or ""
            if r.get("url"):
                sku = f"[{sku or 'page'}]({r['url']})"
            out.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                r.get("priority") or "", r.get("item") or "", r.get("part_no") or "", sku, r.get("pack") or "",
                r.get("qty_packs") if r.get("qty_packs") is not None else "", money(r.get("unit_price_usd")),
                money(r["line_usd"]), (r.get("stock_or_lead_time") or "not shown").replace("|", "/")))
        out.append("")
    return "\n".join(out)


def bom_by_group(rows: list[dict], t: dict) -> str:
    """The full BOM, by what each line is for, with the quantity's basis and the notes on each line."""
    out = ["# Bill of materials by group", "",
           "Generated by `colour_bom.py` from `out/colour/bom/*.json`; the write-up is `notes/colour_bom.md`. Prices "
           "are per pack at qty 1 as shown on 2026-11-22, before shipping and tax.", ""]
    for g, name in GROUPS.items():
        rr = [r for r in rows if r["group"] == g]
        if not rr:
            continue
        tg = t[g]
        out += [f"## {name}", "", f"Now {money(tg['now'])}; soon {money(tg['soon'])}; optional {money(tg['optional'])}"
                f"; {tg['unpriced']} line(s) to quote.", "",
                "| # | Priority | Item | Maker, part no. | Seller (SKU) | Qty | Unit | Line | Stock or lead time |",
                "|---|---|---|---|---|---|---|---|---|"]
        rr = sorted(rr, key=lambda r: PRIORITY.index(r.get("priority")) if r.get("priority") in PRIORITY else 3)
        for i, r in enumerate(rr, 1):
            seller = f"{r.get('seller') or 'quote'}" + (f" ({r['seller_sku']})" if r.get("seller_sku") else "")
            if r.get("url"):
                seller = f"[{seller}]({r['url']})"
            out.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                i, r.get("priority") or "", r.get("item") or "", f"{r.get('maker') or ''} {r.get('part_no') or ''}",
                seller, r.get("qty_packs") if r.get("qty_packs") is not None else "", money(r.get("unit_price_usd")),
                money(r["line_usd"]), (r.get("stock_or_lead_time") or "not shown").replace("|", "/")))
        out += ["", "<details><summary>Quantity basis and notes, line by line</summary>", ""]
        for i, r in enumerate(rr, 1):
            alt = r.get("alt")
            alt_s = ""
            if isinstance(alt, dict) and alt.get("seller"):
                alt_s = (f" **Alternative:** {alt.get('maker') or ''} {alt.get('part_no') or ''} at "
                         f"{alt.get('seller')}, {money(alt.get('unit_price_usd'))}"
                         + (f", {alt['stock_or_lead_time']}" if alt.get("stock_or_lead_time") else "") + ".")
            out.append(f"{i}. **{r.get('item')}.** {r.get('qty_basis') or ''} {r.get('notes') or ''}{alt_s}".strip())
        out += ["", "</details>", ""]
    return "\n".join(out)


def main() -> int:
    rows = load()
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "bom.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in COLS})
    t = totals(rows)
    fl = floor_lengths()
    (OUT / "bom_totals.json").write_text(json.dumps(dict(
        note="USD, per pack at qty 1 x qty_packs, before shipping and tax; prices read 2026-11-22 through the CubXL "
             "Pi's SOCKS tunnel (BYU network). 'unpriced' counts lines that need a quote.", totals=t,
        floor_lengths=fl), indent=1) + "\n")
    print("floor:", fl)
    bc = buying_colours()
    (OUT / "buying_colours.json").write_text(json.dumps(dict(
        method="each swatch's approximate sRGB simulated for full protan, deutan and tritan dichromacy (as "
               "colour_coding.check), CAM02-UCS difference to the scheme's other colours, worst case; pass >= 20, "
               "needs a second cue 12-20, fail < 12", swatches=bc), indent=1) + "\n")
    for k, row in bc.items():
        print(f"{k:42s}", "  ".join(f"{rn} {v['worst']} ({v['vision']}, {v['grade']})" for rn, v in row.items()))
    (OUT / "shopping_list.md").write_text(shopping_list(rows) + "\n")
    (OUT / "bom.md").write_text(bom_by_group(rows, t) + "\n")
    print(f"{len(rows)} lines")
    for g, name in GROUPS.items():
        print(f"{name:45s} now {money(t[g]['now']):>12s}  soon {money(t[g]['soon']):>12s}  "
              f"optional {money(t[g]['optional']):>11s}  unpriced {t[g]['unpriced']}")
    a = t["all"]
    print(f"{'all':45s} now {money(a['now']):>12s}  soon {money(a['soon']):>12s}  optional {money(a['optional']):>11s}"
          f"  unpriced {a['unpriced']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
