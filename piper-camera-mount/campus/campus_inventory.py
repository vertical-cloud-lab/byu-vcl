#!/usr/bin/env python3
"""What the ECEn shop (ELC) and the ME Project Support Center (PSC) sell that this mount needs.

ELC: https://elcparts.byu.edu is a React app over a JSON API, and /api/items/ answers without a
login, from a CI runner as well as from campus. Each item has a name, price, count, shelf and
description. Screws, nuts and washers are sold by length band ("<= 1 in", "> 1 in"), not by size,
so the catalogue can't say whether a given size is in the drawer. A negative count means the shop's
tally isn't kept up for that item (zip ties are at -476), not that it's out.

PSC: https://psc.byu.edu/available%20for%20purchase is a CMS page of cards. It answers 403 to a
datacenter address, so fetch it through a campus Pi and hand the saved HTML to `psc`.

    python campus/campus_inventory.py elc                      # fetch, save the snapshot, print matches
    python campus/campus_inventory.py elc --from campus/elc_items_2026-10-09.json
    ssh "$CUBXL_PI_USERNAME@$CUBXL_PI_HOSTNAME" 'curl -sL "https://psc.byu.edu/available%20for%20purchase"' > psc.html
    python campus/campus_inventory.py psc psc.html             # writes campus/psc_items_<date>.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
ELC_API = "https://elcparts.byu.edu/api/items/"

# What the mount still needs (BOM.md), and the ELC catalogue names that could supply it.
NEEDS = [
    ("Pi 5, 8 GB", r"^Pi 5 \("),
    ("Pi 5 Active Cooler", r"Active Cooler"),
    ("microSD card", r"^SD-MICRO-(32|64)GB|Micro SD card \*NEW\*"),
    ("Camera cable, Standard-Mini, 300 mm", r"RASPI-CAM-CABLE"),
    ("HQ Camera (the ELC has only the v2.1)", r"^U-MCU-RASPI-CAM$"),
    ("USB-C extension", r"USB-C-EXTEN"),
    ("USB-C right-angle cable", r"USB C Right angle"),
    ("27 W USB-C supply", r"SPPLY-5V-RASPI"),
    ("M3, M2.5, M2 screws", r"^H-SCREW-<=1in$|^M-screw$"),
    ("M3, M2.5, M2 nuts", r"^H-NUT$"),
    ("Washers", r"^H-WASHER$"),
    ("Zip ties", r"^H-ZIPTIE$"),
    ("Hook-and-loop ties", r"^Velcro"),
    ("24 V route: lead up the arm", r"^WIRE-HOOK-(16-18|20-30)AWG$"),
    ("24 V route: barrel plug and socket", r"^CABLE-DC-BARREL-(PLUG|SOCKET)$"),
    ("24 V route: 5 V buck converters (none is rated 5 A)", r"^VR-BUCK"),
]


def fetch_elc() -> dict:
    req = urllib.request.Request(ELC_API, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        items = json.load(r)
    return {"url": ELC_API, "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "items": items}


def elc(args: argparse.Namespace) -> None:
    if args.src:
        snap = json.loads(Path(args.src).read_text())
        snap = snap if isinstance(snap, dict) else {"url": ELC_API, "fetched_utc": "?", "items": snap}
    else:
        snap = fetch_elc()
        out = HERE / f"elc_items_{snap['fetched_utc'][:10]}.json"
        out.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + "\n")
    items = snap["items"]
    print(f"{len(items)} items, fetched {snap['fetched_utc']}\n")
    print("| Need | ELC item | Price | Count | Shelf | Description |\n|---|---|---|---|---|---|")
    for need, pat in NEEDS:
        for it in sorted((i for i in items if re.search(pat, i["name"])), key=lambda i: i["name"]):
            desc = (it.get("description") or "").replace("|", "/")[:80]
            print(f"| {need} | {it['name']} | ${it['price']:.2f} | {it['quantity']} | {it['location']} | {desc} |")


def psc(args: argparse.Namespace) -> None:
    text = Path(args.html).read_text(encoding="utf-8", errors="replace")
    # Each card is an <img alt="..."> followed by the item name and its price text.
    body = re.sub(r"<(script|style)\b.*?</\1>", "", text, flags=re.S)
    body = html.unescape(re.sub(r"<[^>]+>", "\n", body))
    lines = [s.strip() for s in body.splitlines() if s.strip() and "=" not in s]
    start = next(i for i, s in enumerate(lines) if s.startswith("(Prices are approximate"))
    items, free = [], ""
    for name, price in zip(lines[start + 1:], lines[start + 2:]):
        if "$" in price or price == "Free":
            items.append({"name": name, "price": price})
    free = next((s for s in lines if s.startswith("We provide consumables")), "")
    date = dt.date.today().isoformat() if not args.date else args.date
    out = HERE / f"psc_items_{date}.json"
    out.write_text(json.dumps({"url": "https://psc.byu.edu/available%20for%20purchase", "date": date,
                               "terms": lines[start - 1], "free": free, "items": items}, indent=1) + "\n")
    print(f"{len(items)} items -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("elc")
    e.add_argument("--from", dest="src", help="read a saved snapshot instead of fetching")
    e.set_defaults(fn=elc)
    p = sub.add_parser("psc")
    p.add_argument("html", help="the PSC 'Our Inventory' page, saved from a campus address")
    p.add_argument("--date", help="date of the fetch, for the file name (default today)")
    p.set_defaults(fn=psc)
    a = ap.parse_args()
    a.fn(a)
