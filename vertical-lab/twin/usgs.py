"""USGS Mineral Commodity Summaries 2026: prices, net import reliance and the 2025 critical-mineral list.

    python3 -m twin.usgs fetch      # download the data release CSV (3.2 MB) into $TWIN_CACHE (default /tmp/twin_cache)
    python3 -m twin.usgs extract    # -> twin/data/usgs_mcs2026.json, the subset the twin uses (committed)
    python3 -m twin.usgs show       # print the element table

Source: National Minerals Information Center, 2026, U.S. Geological Survey Mineral Commodity Summaries 2026 Data
Release, https://doi.org/10.5066/P1WKQ63T (ScienceBase item 69837e43b66b01367d7ec7c7, file
MCS2026_Commodities_Data.csv). USGS data are in the public domain, so the extracted subset is committed.

What the twin takes from it, per element of either search space:

* **price series 2021-2025** (USD/kg, converted from the unit USGS reports). The twin's market model is calibrated on
  it: its log-returns give each commodity's volatility, and the years with a jump (nickel and silicon metal in 2022,
  aluminium and copper in 2025, lithium in 2022) are the anchors for the sporadic and the persistent shocks
  (twin/supply.py).
* **net import reliance (NIR)**, the share of U.S. apparent consumption that is imported. USGS reports some as a bound
  ("<25", ">50", ">95") or "E" (net exporter); the twin reads a bound as its midpoint within [0, 100] and "E" as 0, and
  keeps the raw string.
* **critical mineral (2025 list)**, as USGS flags it.

FLAIME's mineral-burden metrics (MBS_lin, CMDRI_log; DAL ``genesis-mission-proposal/flaime-genesis-proposal.tex``,
section 3) are defined on NIR and price; ``mineral_burden()`` computes them from this table.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
JSON_PATH = DATA / "usgs_mcs2026.json"
CACHE = Path(os.environ.get("TWIN_CACHE", "/tmp/twin_cache"))
URL = ("https://www.sciencebase.gov/catalog/file/get/69837e43b66b01367d7ec7c7"
       "?f=__disk__d3%2Fac%2F84%2Fd3ac8466552946c5e8caa2c2c6338d9e1aff655d")
SHA256 = "582a0aa231aea53d8a97dc8d1cd3dfa5f885cf3760353e3d029d7f0ae4fbaaf5"
CITATION = ("National Minerals Information Center, 2026, U.S. Geological Survey Mineral Commodity Summaries 2026 "
            "Data Release, https://doi.org/10.5066/P1WKQ63T")
LB = 0.45359237

# element -> (USGS commodity, a substring of the price row's Statistics_detail to use, a substring of the NIR row's
# detail or None for the first NIR row, note). The price row is the one closest to the form a lab or a powder maker
# buys; where USGS only prices an ore or oxide, the note says so and the twin's lab prices (data/feedstock.json) are
# what campaigns pay.
ELEMENTS = {
    "Al": ("Aluminum", "ingot", None, "U.S. market spot ingot"),
    "Cu": ("Copper", "U.S. producer, cathode", None, "U.S. producer cathode (COMEX + premium)"),
    "Ni": ("Nickel", None, None, "LME cash"),
    "Mn": ("Manganese", None, None, "Mn ore, Mn content, CIF China (USD per metric ton unit); a proxy, not metal"),
    "Cr": ("Chromium", "Chromium metal", None, "chromium metal"),
    "Zr": ("Zirconium", "sponge", None, "Zr sponge ex-works China"),
    "Mg": ("Magnesium Metal", "U.S. spot", None, "U.S. spot Western"),
    "Si": ("Silicon", "Silicon metal", "Total", "silicon metal"),
    "Ti": ("Titanium sponge metal", None, None, "Ti sponge"),
    "Fe": ("Iron Ore", None, None, "iron ore unit value (a proxy for iron)"),
    "Ce": ("Cerium", None, None, "cerium oxide 99.5 %"),
    "Sc": ("Scandium", "oxide", None, "scandium oxide 99.99 %"),
    "Li": ("Lithium", None, None, "battery-grade lithium carbonate"),
    "Er": ("Erbium", None, None, "erbium oxide 99.5 %"),
    "Zn": ("Zinc", "North American", "Refined", "North American"),
    "Sn": ("Tin", "New York", None, "New York dealer"),
    "Nb": ("Niobium (Columbium)", None, None, "ferroniobium unit value"),
}
# commodities that are not alloying elements but that the network consumes or depends on
OTHERS = {
    "argon": ("Argon", None, None, "no price in the salient data"),
    "graphite": ("Graphite (Natural)", None, None, "natural graphite imports (crucibles are synthetic graphite)"),
    "rare_earths": ("Rare Earths", "Mischmetal", "Compounds", "mischmetal 65 % Ce"),
}
TO_KG = {"cents per pound": 0.01 / LB, "dollars per pound": 1.0 / LB, "dollars per metric ton": 1e-3,
         "dollars per kilogram": 1.0}


def fetch(dest: Path | None = None) -> Path:
    dest = dest or CACHE / "MCS2026_Commodities_Data.csv"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (twin.usgs)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            dest.write_bytes(r.read())
    h = hashlib.sha256(dest.read_bytes()).hexdigest()
    if h != SHA256:
        raise RuntimeError(f"{dest}: sha256 {h} differs from the release's {SHA256}")
    return dest


def _num(s: str) -> float | None:
    s = (s or "").replace(",", "").replace("–", "-").replace("�", "-").strip()
    if not s or s in ("NA", "W", "XX", "--"):
        return None
    if "-" in s[1:]:                                  # a range such as 660-670: its midpoint
        a, b = s.split("-", 1) if s[0] != "-" else (s, "")
        try:
            return 0.5 * (float(a) + float(b))
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def _nir(s: str) -> float | None:
    """USGS writes NIR as a number, a bound or 'E' (net exporter). A bound is read as the middle of its side."""
    s = (s or "").strip()
    if s == "E":
        return 0.0
    if s.startswith("<"):
        return float(s[1:]) / 2.0
    if s.startswith(">"):
        v = float(s[1:])
        return v + (100.0 - v) / 2.0
    return _num(s)


def extract(csv_path: Path | None = None) -> dict:
    csv_path = csv_path or fetch()
    with open(csv_path, encoding="utf-8-sig", errors="replace") as f:
        rows = list(csv.DictReader(f))
    out = dict(source=CITATION, url=URL, sha256=SHA256, elements={}, others={})
    for table, spec in (("elements", ELEMENTS), ("others", OTHERS)):
        for key, (com, price_key, nir_key, note) in spec.items():
            rs = [r for r in rows if r["Commodity"] == com and r["Country"] == "United States"
                  and r["Section"].startswith("Salient")]
            prices = {}
            for r in rs:
                if r["Statistics"] != "Price" or r["Unit"] not in TO_KG:
                    continue
                if price_key and price_key.lower() not in r["Statistics_detail"].lower():
                    continue
                prices.setdefault(r["Statistics_detail"], {})[r["Year"]] = (r["Value"], r["Unit"])
            series, detail = {}, None
            if prices:
                detail = sorted(prices)[0]
                for yr, (v, unit) in sorted(prices[detail].items()):
                    x = _num(v)
                    if x is not None:
                        k = TO_KG[unit]
                        if com == "Manganese":            # USD per metric ton *unit* of Mn content (10 kg Mn)
                            k = 1.0 / 10.0
                        series[yr] = round(x * k, 4)
            nir = {}
            for r in rs:
                if not r["Statistics"].lower().startswith("net import reliance"):
                    continue
                if nir_key and nir_key.lower() not in r["Statistics_detail"].lower():
                    continue
                if nir:
                    continue
                nir = {r2["Year"]: r2["Value"] for r2 in rs
                       if r2["Statistics_detail"] == r["Statistics_detail"]}
            crit = next((r["Is critical mineral 2025"] for r in rs if r.get("Is critical mineral 2025")), None)
            out[table][key] = dict(commodity=com, price_detail=detail, price_usd_per_kg=series, note=note,
                                   nir_raw=nir, nir_pct={y: _nir(v) for y, v in nir.items()},
                                   critical_2025=crit)
    return out


def write(data: dict | None = None) -> Path:
    data = data or extract()
    DATA.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(data, indent=1) + "\n")
    return JSON_PATH


_CACHE: dict = {}


def load() -> dict:
    if "d" not in _CACHE:
        _CACHE["d"] = json.loads(JSON_PATH.read_text())
    return _CACHE["d"]


RARE_EARTHS = ("Ce", "Er", "La")


def nir(el: str, year: str = "2025") -> float:
    """Net import reliance (0-1). Elements USGS gives none for (Fe: net exporter) read as 0. Cerium and erbium have
    no NIR row of their own; they take the rare-earth compounds' (67 % in 2025)."""
    e = load()["elements"].get(el)
    if not e:
        return 0.0
    if el in RARE_EARTHS and not any(v is not None for v in e["nir_pct"].values()):
        e = load()["others"]["rare_earths"]
    v = e["nir_pct"].get(year)
    if v is None:
        vals = [x for x in e["nir_pct"].values() if x is not None]
        v = vals[-1] if vals else 0.0
    return float(v) / 100.0


def price(el: str, year: str = "2024") -> float | None:
    e = load()["elements"].get(el)
    if not e or not e["price_usd_per_kg"]:
        return None
    s = e["price_usd_per_kg"]
    return s.get(year, list(s.values())[-1])


def critical(el: str) -> bool:
    e = load()["elements"].get(el)
    return bool(e and (e.get("critical_2025") or "").lower().startswith("y"))


def log_returns(el: str) -> list[float]:
    e = load()["elements"].get(el) or load()["others"].get(el)
    s = [v for _, v in sorted((e or {}).get("price_usd_per_kg", {}).items()) if v]
    return [math.log(b / a) for a, b in zip(s, s[1:])]


def mineral_burden(wt: dict[str, float], base: str = "Al", year_nir: str = "2025",
                   price_year: str = "2024") -> dict:
    """FLAIME's two mineral-burden scalars (DAL flaime-genesis-proposal.tex, Activity 1):

        MBS_lin   = sum_{i != base} NIR_i * (c_i / c_base) * x_i
        CMDRI_log = sum_{i != base} NIR_i * log10(1 + c_i / c_base) * x_i

    with x_i the mass fraction, c_i the commodity price and NIR_i the net import reliance (0-1). FLAIME freezes the
    prices at month 1 (2022-2024 averages); this uses one year, `price_year`. Elements with no USGS price are skipped
    and listed under 'missing'."""
    cb = price(base, price_year)
    mbs = cmd = 0.0
    missing = []
    for el, w in wt.items():
        if el == base or w <= 0:
            continue
        c = price(el, price_year)
        if c is None or cb is None:
            missing.append(el)
            continue
        x = w / 100.0
        mbs += nir(el, year_nir) * (c / cb) * x
        cmd += nir(el, year_nir) * math.log10(1.0 + c / cb) * x
    return dict(mbs_lin=mbs, cmdri_log=cmd, missing=missing)


def show():
    d = load()
    print(f"{'el':3} {'commodity':24} {'2021':>9} {'2022':>9} {'2023':>9} {'2024':>9} {'2025':>9}  NIR25  crit")
    for el, e in d["elements"].items():
        p = e["price_usd_per_kg"]
        print(f"{el:3} {e['commodity'][:24]:24} " + " ".join(f"{p.get(y, float('nan')):9.2f}"
                                                         for y in ("2021", "2022", "2023", "2024", "2025"))
              + f"  {e['nir_raw'].get('2025', '-'):>5}  {e['critical_2025']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "fetch":
        print(fetch())
    elif cmd == "extract":
        print(write())
    else:
        show()
