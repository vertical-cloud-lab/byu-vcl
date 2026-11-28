"""Maps of the smaller high-bay candidates (#343, 2026-11-28) on OpenStreetMap tiles.

    python3 facility/small_map.py    # -> facility/out/small/map_provo.png, map_uofu.png, map_region.png

Sites and coordinates are in ``out/small/sites.tsv`` (geocoded with the US Census geocoder, or OpenStreetMap Nominatim
where the Census had no match; the ``how`` column says which, and which pins are only to the street). Tiles come from tile.openstreetmap.org at the zoom
given per map, cached in ``out/small/tiles/`` so a redraw doesn't fetch them again (that folder is not committed).
Map data © OpenStreetMap contributors, ODbL; the attribution is printed on every map.
"""
from __future__ import annotations

import csv
import io
import math
import time
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "small"
TILES = OUT / "tiles"
UA = "facility-site-map/1.0 (one-off research figure)"
INK, INK2, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
COL = {"provo": "#2a78d6", "uofu": "#eb6834", "anchor": "#0b0b0b", "earlier": "#8a8984"}


def deg2xy(lat: float, lon: float, z: int) -> tuple[float, float]:
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def tile(z: int, x: int, y: int):
    TILES.mkdir(parents=True, exist_ok=True)
    p = TILES / f"{z}_{x}_{y}.png"
    if not p.exists():
        req = urllib.request.Request(f"https://tile.openstreetmap.org/{z}/{x}/{y}.png", headers={"User-Agent": UA})
        p.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        time.sleep(0.5)
    return plt.imread(io.BytesIO(p.read_bytes()), format="png")


def basemap(ax, south: float, west: float, north: float, east: float, z: int):
    x0, y0 = deg2xy(north, west, z)
    x1, y1 = deg2xy(south, east, z)
    for tx in range(int(x0), int(x1) + 1):
        for ty in range(int(y0), int(y1) + 1):
            ax.imshow(tile(z, tx, ty), extent=(tx, tx + 1, ty + 1, ty), interpolation="lanczos", zorder=0)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.set_aspect("equal")
    ax.axis("off")
    return lambda lat, lon: deg2xy(lat, lon, z)


def sites() -> list[dict]:
    with open(OUT / "sites.tsv", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def draw(name: str, title: str, box: tuple[float, float, float, float], z: int, groups: set[str],
         size=(8.0, 8.0)) -> None:
    fig = plt.figure(figsize=size, dpi=170, facecolor=SURFACE)
    ax = fig.add_axes([0.0, 0.0, 1.0, 0.94])
    xy = basemap(ax, *box, z)
    for s in sites():
        if s["group"] not in groups:
            continue
        lat, lon = float(s["lat"]), float(s["lon"])
        if not (box[0] <= lat <= box[2] and box[1] <= lon <= box[3]):
            continue
        x, y = xy(lat, lon)
        c = COL[s["group"]]
        if s["group"] == "anchor":
            ax.plot(x, y, marker="*", ms=13, mfc=c, mec="white", mew=1.0, zorder=5)
            ax.annotate(s["label"], (x, y), xytext=(8, -3), textcoords="offset points", fontsize=7.5, color=INK,
                        fontweight="bold", zorder=6, bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.8))
            continue
        ax.plot(x, y, marker="o", ms=15, mfc=c, mec="white", mew=1.2, zorder=5)
        ax.text(x, y, s["id"], ha="center", va="center", fontsize=6.6, color="white", fontweight="bold", zorder=6)
        dx, dy = (float(v) for v in (s.get("dx") or 9, s.get("dy") or 0))
        ax.annotate(s["label"], (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=6.4, color=INK,
                    va="center", ha="left" if dx >= 0 else "right", zorder=6,
                    bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.6))
    fig.text(0.01, 0.985, title, fontsize=10, color=INK, ha="left", va="top")
    fig.text(0.01, 0.955, "Blue: closer to Provo. Orange: close to or part of the U of U. Grey: earlier #343 sites. "
             "Stars: BYU, and the U of U's Warnock Engineering Building.", fontsize=6.6, color=INK2, ha="left", va="top")
    ax.add_patch(Rectangle((0.0, 0.0), 1.0, 0.03, transform=ax.transAxes, facecolor="white", alpha=0.75,
                           edgecolor="none", zorder=7))
    ax.text(0.995, 0.012, "Map data © OpenStreetMap contributors (ODbL). Pins: US Census and OpenStreetMap Nominatim "
            "geocodes, some to the street only (out/small/sites.tsv).", transform=ax.transAxes, ha="right", va="bottom", fontsize=5.6, color=INK2, zorder=8)
    fig.savefig(OUT / f"{name}.png", facecolor=SURFACE)
    plt.close(fig)
    from PIL import Image                                  # a 256-colour palette keeps the PNG small
    Image.open(OUT / f"{name}.png").convert("RGB").quantize(colors=256).save(OUT / f"{name}.png", optimize=True)


MAPS = [
    ("map_provo", "Closer to Provo: smaller high-bay candidates", (40.12, -111.83, 40.34, -111.57), 12,
     {"provo", "anchor", "earlier"}, (8.0, 9.2)),
    ("map_uofu", "Close to or part of the University of Utah", (40.69, -111.98, 40.79, -111.80), 13,
     {"uofu", "anchor"}, (9.6, 6.6)),
]

if __name__ == "__main__":
    for args in MAPS:
        draw(*args)
        print("wrote", OUT / f"{args[0]}.png")
