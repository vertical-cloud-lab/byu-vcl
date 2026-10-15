"""Draw the walking route from the lab (CB 154) to the ME Prototyping Lab (EB 117).

    pip install matplotlib shapely
    python route_map.py            # -> cb154-to-eb117-prototyping-lab.png

Room outlines come from the public floor-plan layer behind BYU's campus map
(map.byu.edu). Only the building number, room number and floor are requested, and
only the rooms on the route are drawn; everything else is reduced to a building
outline. The outdoor part of the route follows OpenStreetMap footways 1102183376,
148219810, 923378521, 1087313174, 1087313175 (a few steps up), 1562010728,
1562010729 and 1562010730.

Floors: CB 154 is on CB floor 1, below street level. CB floor 2 (4656 ft) and EB
floor 2 (4655 ft, the "200B" north door) are at street level. EB 117 is on EB floor 1,
one floor below that; EB's lowest floor, "B", is one floor further down.
"""
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from shapely import transform  # noqa: E402
from shapely.geometry import shape  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

FLOORPLANS = ("https://services.arcgis.com/FvF9MZKp3JWPrSkg/arcgis/rest/services/"
              "Floorplans_V/FeatureServer/0/query")
OUT = Path(__file__).with_name("cb154-to-eb117-prototyping-lab.png")

# Local metres east/north of this point; at this size the error is a few centimetres.
LAT0, LON0 = 40.2466, -111.648
KX = math.cos(math.radians(LAT0)) * 111320
KY = 110950

BLUE, ORANGE = "#2a78d6", "#eb6834"        # floor 1 / street level (validated pair)
SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"

# Route, in local metres. Each leg is (floor, points).
FLOOR1, STREET = "floor 1", "street level"
ROUTE = [
    (FLOOR1, [(-12.7, 27.7), (-17.6, 28.0), (-18.8, 28.0), (-18.8, 19.0), (-15.3, 19.0)]),
    (STREET, [(-15.3, 19.0), (-15.3, 15.0), (-26.5, 15.0), (-28.2, 14.9),   # foyer, SW doors
              (-49.5, 14.9), (-49.3, -3.4), (-49.2, -11.9),                 # sidewalk south
              (-41.8, -11.9), (-40.3, -11.9), (-21.3, -11.9), (-18.7, -12.0),  # between the buildings
              (-18.4, -16.9), (-18.4, -19.5), (-21.2, -19.5)]),             # EB north door 200B
    (FLOOR1, [(-21.2, -19.5), (-21.2, -29.0), (24.0, -29.0), (24.0, -33.5)]),
]


def fetch_rooms():
    query = urllib.parse.urlencode({
        "where": "BLDG_SHORT IN ('CB','EB') AND BLDG_LEVEL IN (1,2)",
        "outFields": "BLDG_SHORT,RoomNumber,BLDG_LEVEL",
        "returnGeometry": "true", "outSR": "4326", "f": "geojson",
    })
    with urllib.request.urlopen(f"{FLOORPLANS}?{query}", timeout=120) as r:
        features = json.load(r)["features"]

    def local(geom):
        return transform(geom, lambda c: [[(x - LON0) * KX, (y - LAT0) * KY] for x, y in c])

    return [((f["properties"]["BLDG_SHORT"], f["properties"]["BLDG_LEVEL"],
              f["properties"]["RoomNumber"]), local(shape(f["geometry"]))) for f in features]


def fill(ax, geom, **kw):
    for poly in getattr(geom, "geoms", [geom]):
        ax.fill(*poly.exterior.xy, **kw)


def main():
    rooms = fetch_rooms()
    room = {key: geom for key, geom in rooms}

    fig, ax = plt.subplots(figsize=(12.8, 10.6), dpi=125)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    # Building outlines at street level (floor 2); both end rooms sit inside them.
    for bldg, (lx, ly) in {"CB": (16, 34), "EB": (2, -52)}.items():
        outline = unary_union([g.buffer(0.4) for (b, lvl, _), g in rooms
                               if b == bldg and lvl == 2]).buffer(-0.4)
        fill(ax, outline, fc="#ecebe7", ec="#bdbcb6", lw=1.2, zorder=1)
        name = {"CB": "Clyde Building (CB)", "EB": "Engineering Building (EB)"}[bldg]
        ax.text(lx, ly, name, fontsize=17, color=INK2, ha="center", va="center", zorder=2)

    hall = dict(fc="#f8f7f3", ec="none", zorder=2)
    for key in [("CB", 1, "101"), ("CB", 2, "244"), ("CB", 2, "250"), ("EB", 2, "200B"),
                ("EB", 1, "105")]:
        fill(ax, room[key], **hall)
    for key in [("CB", 1, "148"), ("EB", 2, "203"), ("EB", 2, "201")]:
        fill(ax, room[key], fc="#d6d5cf", ec="#a9a8a2", lw=0.8, zorder=3)
    fill(ax, room[("EB", 1, "107")], fc="#e2e1dc", ec="#a9a8a2", lw=0.8, zorder=3)
    fill(ax, room[("CB", 1, "154")], fc="#cde2fb", ec=BLUE, lw=1.6, zorder=3)
    fill(ax, room[("EB", 1, "117")], fc="#cde2fb", ec=INK, lw=2.2, zorder=3)

    ax.plot(-12.7, 27.7, "o", ms=11, mfc=BLUE, mec=SURFACE, mew=2, zorder=8)
    ax.text(-6.5, 27.7, "CB 154 (start)", fontsize=14, fontweight="bold", color=INK,
            ha="left", va="center", zorder=6)
    ax.text(24.3, -38.4, "EB 117\nPrototyping Lab", fontsize=15, fontweight="bold",
            color=INK, ha="center", va="center", zorder=6)
    ax.text(-11.9, -38.4, "EB 107\nProject Support\nCenter", fontsize=11, color=INK2,
            ha="center", va="center", zorder=6)

    # Route: a surface-colored casing under each leg, then the leg, with arrowheads.
    length = 0.0
    for floor, pts in ROUTE:
        color = BLUE if floor == FLOOR1 else ORANGE
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=SURFACE, lw=9, solid_capstyle="round", zorder=4)
        ax.plot(xs, ys, color=color, lw=4.5, solid_capstyle="round",
                solid_joinstyle="round", zorder=5)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            seg = math.hypot(x1 - x0, y1 - y0)
            length += seg
            if seg > 12:
                mx, my = x0 + 0.55 * (x1 - x0), y0 + 0.55 * (y1 - y0)
                ax.annotate("", xy=(mx + 0.01 * (x1 - x0), my + 0.01 * (y1 - y0)), xytext=(mx, my),
                            arrowprops=dict(arrowstyle="-|>,head_length=0.9,head_width=0.5",
                                            color=color, lw=0), zorder=6)

    def note(x, y, text, tx, ty, **kw):
        ax.annotate(text, xy=(x, y), xytext=(tx, ty), fontsize=12.5, color=INK, ha="center",
                    va="center", zorder=7,
                    bbox=dict(boxstyle="round,pad=0.3", fc=SURFACE, ec="#bdbcb6", lw=0.8),
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.9), **kw)

    for (x, y), arrow in [((-15.3, 19.0), "↑"), ((-21.2, -19.5), "↓")]:
        ax.plot(x, y, "o", ms=17, mfc=SURFACE, mec=INK, mew=1.6, zorder=8)
        ax.text(x, y - 0.15, arrow, fontsize=13, fontweight="bold", color=INK,
                ha="center", va="center", zorder=9)
    note(-15.3, 19.0, "stairs: up 1 floor", 6, 22)
    note(-28.2, 14.9, "southwest doors", -38, 24)
    note(-41.0, -11.9, "a few steps up", -40, -3)
    note(-18.4, -16.9, "EB north door", -2, -10)
    note(-21.2, -19.5, "stairs or elevator:\ndown 1 floor, to floor 1", -43, -25)

    # North arrow and scale bar.
    ax.annotate("N", xy=(-56, 38), xytext=(-56, 30), fontsize=15, fontweight="bold",
                color=INK, ha="center", va="center",
                arrowprops=dict(arrowstyle="-|>,head_length=0.8,head_width=0.45", color=INK, lw=2))
    ax.plot([-60, -40], [-57.5, -57.5], color=INK, lw=3, solid_capstyle="butt")
    ax.text(-50, -55.5, "20 m", fontsize=12, color=INK, ha="center", va="bottom")

    ax.set_xlim(-62, 66)
    ax.set_ylim(-60, 41)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"CB 154 to the Prototyping Lab (EB 117): about {round(length, -1):.0f} m",
                 fontsize=19, color=INK, loc="left", pad=12)

    handles = [Line2D([], [], color=BLUE, lw=4.5, label="Floor 1 (CB 154's floor, and EB 117's)"),
               Line2D([], [], color=ORANGE, lw=4.5, label="Floor 2 and outside (street level)")]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.05, 0.035), ncol=2,
               frameon=False, fontsize=13, labelcolor=INK)
    fig.text(0.95, 0.012, "Floor plans: BYU campus map (map.byu.edu).  Paths: © OpenStreetMap contributors.",
             fontsize=9.5, color=INK2, ha="right")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.94, bottom=0.08)
    fig.savefig(OUT, facecolor=SURFACE)
    print(f"route {length:.0f} m -> {OUT}")


if __name__ == "__main__":
    main()
