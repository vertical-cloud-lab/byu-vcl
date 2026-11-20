"""Colour coding for the vertical lab: the scheme as data, a colour-vision check of each palette, and its figures.

Sterling, PR #318, 2026-11-20: "open another PR focused on how we can best leverage color coding (send edison search
related to this in addition to your own searches) for organization and cleanliness of the lab". The write-up is
notes/colour_coding.md; the sources are notes/colour_sources.md and out/edison/colour_*/.

The rule this is built on, from Sterling's own notes on the renders ("technicolor jars", "candy-coloured" powder, the
"rapid flowing of vibrant colors"): colour goes only where a person makes a decision, and each colour means one thing
in one place. Everything else stays neutral: white, greys, black, steel and clear glass.

    python3 colour_coding.py            # the check (out/colour/cvd_check.json) and the figures
    python3 colour_coding.py check      # the check only; exits 1 if a palette fails
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out" / "colour"

# ===================================================================================================== the channels
# A channel is where a colour sits (on a tool, on the floor, on a pipe, in a lamp). The same colour can mean different
# things in different channels, which is unavoidable with only a dozen nameable colours, but never two things in one
# channel, and a channel's colours always come with a word, a letter or a shape (no meaning is carried by colour alone).
# sRGB values are targets for buying (match products to them by eye under the lab's own lights); the safety and
# pipe-marking colours are approximations of the standards' own swatches, used here only for the colour-vision check.

FAMILY = {   # the alloy family a tool or container is dedicated to: its handle, tape band, cap-label stripe, rack edge
    "Al": dict(name="blue", rgb="#0072B2", why="the lab's main family; the most distinct colour from the Cu orange "
               "for every kind of colour vision"),
    "Cu": dict(name="orange", rgb="#E69F00", why="copper-coloured, so it is remembered"),
    # reserved for the next family the lab takes on (Ni-base, Fe-base or Ti, whichever comes first). With blue and
    # orange in use, the search in notes/colour_coding.md finds only brown, black and white still clear of both for
    # every kind of colour vision; black and white are what tools come in anyway, so brown. Green and purple, the
    # obvious picks, fail for tritan vision (11.7 against the blue, 11.0 against the orange). A fourth family can't
    # have a hue of its own: it gets brown with a white band, or its own named, separate tool set.
    "next": dict(name="brown", rgb="#7B4A2A", why="reserved: the only hue left that stays clear of blue and orange",
                 reserved=True),
}
# The neutral is black (or bare steel), not grey: a mid-grey sits 19.7 from the brown for protan vision and 18.8 from
# the blue for tritan vision; black is at least 30 from all three.
NEUTRAL = {"general": dict(name="black or bare steel", rgb="#111111",
                           why="touches no powder, or is cleaned to a validated limit between every use")}

FLOOR = {    # floor tape and paint (OSHA 1910.144 and the usual visual-workplace convention; ISO 3691-4 for the AMRs)
    "aisle edge": dict(name="yellow", rgb="#F2C200", why="traffic: the MiR250s' lane and walkways"),
    "equipment place": dict(name="white", rgb="#FFFFFF", why="where a cart, bin or tool stand goes"),
    "operating hazard zone": dict(name="black/yellow", rgb="#F2C200", rgb2="#1F1F1F",
                                  why="a robot docks within 0.5 m of something fixed, its personnel detection muted: "
                                      "taped 1 m outside it (ISO 3691-4; MiR250 user guide, section 10.7)"),
    "keep clear": dict(name="red/white", rgb="#C8102E", rgb2="#FFFFFF",
                       why="in front of fire extinguishers, electrical panels, eyewash"),
    "safety equipment": dict(name="green", rgb="#00843D", why="eyewash, first aid, spill kit"),
}
# No red "hold" area on the floor: red and the safety green are 6.9 apart for deutan vision (cvd_check.json, first
# version). Anything waiting for a decision goes to the HOLD bin on a passive store tray, with a red tag that says HOLD:
# a place and a word, not a floor colour.

LIGHTS = {   # stack lights and the finale's beacons (IEC 60204-1 indicator colours), in a fixed order, red at the top:
    #          red and green are 12.6 apart for deutan vision, so a lamp's position is its second cue
    "running": dict(name="green", rgb="#00A651", why="normal"),
    "abnormal / upkeep": dict(name="yellow", rgb="#FFD100", why="abnormal condition: warming up, in upkeep"),
    "waiting for a person": dict(name="blue", rgb="#0072CE", why="mandatory action: an operator is needed"),
    "fault": dict(name="red", rgb="#E10600", why="emergency or fault"),
    "idle": dict(name="white", rgb="#F5F5F5", why="neutral: powered, nothing running"),
}

SAFETY = {   # reserved by ANSI Z535.1 / ISO 3864 / OSHA 1910.144: never used for anything else on signs and floors
    "danger, fire equipment, stop": "#C8102E", "warning, dangerous machine parts": "#FF7900",
    "caution, physical hazard": "#F2C200", "safety equipment, first aid": "#00843D",
    "mandatory, information": "#005EB8", "radiation (trefoil, XRD and XRF)": "#B5148A",
}

PALETTES = {"alloy family": {**{k: v["rgb"] for k, v in FAMILY.items()}, "general": NEUTRAL["general"]["rgb"]},
            "alloy family in use": {k: v["rgb"] for k, v in FAMILY.items() if not v.get("reserved")},
            "floor": {k: v["rgb"] for k, v in FLOOR.items() if "rgb2" not in v},
            "lights": {k: v["rgb"] for k, v in LIGHTS.items()},
            "safety (reference)": SAFETY}


# ===================================================================================================== the check
def _rgb1(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0


def simulate(rgb1: np.ndarray, kind: str | None) -> np.ndarray:
    """sRGB (0-1) as a person with full dichromacy of `kind` sees it (Machado et al. 2009, via colorspacious)."""
    from colorspacious import cspace_convert
    if kind is None:
        return rgb1
    cvd = {"name": "sRGB1+CVD", "cvd_type": kind, "severity": 100}
    return np.clip(cspace_convert(rgb1, cvd, "sRGB1"), 0, 1)


def delta(a: np.ndarray, b: np.ndarray) -> float:
    """Colour difference in CAM02-UCS (about 1 = just noticeable side by side)."""
    from colorspacious import deltaE
    return float(deltaE(a, b, input_space="sRGB1", uniform_space="CAM02-UCS"))


VISION = {"normal": None, "protan": "protanomaly", "deutan": "deuteranomaly", "tritan": "tritanomaly"}
# Pass marks: two colours whose job is to be told apart, named, from across a bench, should differ by far more than a
# just-noticeable step. 20 in CAM02-UCS is about the gap between the Okabe-Ito palette's closest pair under deutan
# simulation; under 12 is a fail; 12-20 passes only with a second cue (a word, a letter, a pattern), which this scheme
# always has anyway.
PASS, FLOOR_MARK = 20.0, 12.0


def check() -> dict:
    res = {}
    for pal, cols in PALETTES.items():
        rows = []
        for (ka, ha), (kb, hb) in itertools.combinations(cols.items(), 2):
            d = {v: round(delta(simulate(_rgb1(ha), k), simulate(_rgb1(hb), k)), 1) for v, k in VISION.items()}
            worst = min(d, key=d.get)
            rows.append(dict(a=ka, b=kb, **d, worst=worst, grade="pass" if d[worst] >= PASS else
                             ("needs a second cue" if d[worst] >= FLOOR_MARK else "FAIL")))
        res[pal] = rows
    res["ok"] = all(r["grade"] != "FAIL" for pal in ("alloy family", "alloy family in use", "lights")
                    for r in res[pal])
    return res


# ===================================================================================================== figures
SHORT = {"abnormal / upkeep": "upkeep", "waiting for a person": "needs a\nperson", "equipment place": "equipment",
         "safety equipment": "safety\nequipment", "aisle edge": "aisle edge"}


def palette_figure(res: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    groups = [("Alloy family (tools, containers)", {**{k: v["rgb"] for k, v in FAMILY.items()},
                                                     "general": NEUTRAL["general"]["rgb"]},
               {**{k: v["name"] + (" (reserved)" if v.get("reserved") else "") for k, v in FAMILY.items()},
                "general": "black"}),
              ("Indicator lights (IEC 60204-1)", {k: v["rgb"] for k, v in LIGHTS.items()},
               {k: v["name"] for k, v in LIGHTS.items()}),
              ("Floor (single colours)", {k: v["rgb"] for k, v in FLOOR.items() if "rgb2" not in v},
               {k: v["name"] for k, v in FLOOR.items() if "rgb2" not in v})]
    fig, axs = plt.subplots(len(groups), 1, figsize=(13, 2.05 * len(groups) + 0.7), dpi=110)
    for ax, (title, cols, names) in zip(axs, groups):
        ax.set_xlim(0, 4 * (len(cols) + 0.6))
        ax.set_ylim(-1.35, 1.25)
        ax.axis("off")
        ax.text(0, 1.12, title, fontsize=11.5, weight="bold", color="#1f2328", va="bottom")
        for j, (v, kind) in enumerate(VISION.items()):
            x0 = j * (len(cols) + 0.6)
            ax.text(x0, 0.86, v + (" vision" if v == "normal" else ""), fontsize=9, color="#4b5563")
            for i, (k, h) in enumerate(cols.items()):
                c = simulate(_rgb1(h), kind)
                ax.add_patch(Rectangle((x0 + i, 0), 0.92, 0.75, fc=c, ec="#9aa1ab", lw=0.6))
                if j == 0:
                    ax.text(x0 + i + 0.46, -0.08, SHORT.get(k, k), ha="center", va="top", fontsize=7.4,
                            color="#1f2328", linespacing=0.9)
                    ax.text(x0 + i + 0.46, -0.62, names[k], ha="center", va="top", fontsize=6.8, color="#4b5563")
        rows = [r for pal, rr in res.items() if pal != "ok" for r in rr
                if {r["a"], r["b"]} <= set(cols) and pal != "alloy family in use"]
        if rows:
            w = min(rows, key=lambda r: r[r["worst"]])
            ax.text(len(cols) + 0.6, -0.95, f"closest pair: {w['a']} / {w['b']}, {w[w['worst']]:.0f} in CAM02-UCS "
                    f"({w['worst']} vision) - {w['grade']}", fontsize=8.5, color="#1f2328")
    fig.suptitle("Each palette as seen with normal vision and the three full colour-vision deficiencies "
                 "(Machado 2009 simulation)", fontsize=11, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


ZONE_MM = 1000.0     # the hazard-zone tape, 1 m outside a docked MiR250 (MiR250 User Guide v1.2, section 10.7)


def floor_figure(path: Path) -> None:
    """The floor marking on the set-up floor (out/tray_plan.json): lanes, docks, hazard zones, keep-clear, hold."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Rectangle
    plan = json.loads((HERE / "out" / "tray_plan.json").read_text())
    fig, ax = plt.subplots(figsize=(16, 9.5), dpi=110)
    ax.add_patch(Rectangle((-12000, -13000), 24400, 15500, fc="#e9eaec", ec="none", zorder=0))     # bare floor
    for key, (a, b, c, d) in plan["floor"]["machines"].items():    # over the tape: a zone ends at a machine's face
        ax.add_patch(Rectangle((a, c), b - a, d - c, fc="#c9ccd1", ec="#8a8f98", lw=0.8, zorder=3.5))
    x0, x1, y0, y1 = plan["floor"]["aisle_mm"]
    Y = FLOOR["aisle edge"]["rgb"]
    for yy in (y0, y1):                                                   # 75 mm yellow lane edges
        ax.add_patch(Rectangle((x0, yy - 37), x1 - x0, 75, fc=Y, ec="none", zorder=3))
    mir = (580.0, 890.0)                                                  # MiR250 footprint, props.MIR
    from shapely.geometry import box as sbox
    from shapely.ops import unary_union
    zones, polys = [], []
    for k, dk in plan["floor"]["docks"].items():
        dx, dy = dk["dock"][:2]
        a = dk["dock"][2] if len(dk["dock"]) > 2 else 0
        w, h = (mir[1], mir[0]) if abs(np.sin(np.radians(a))) > 0.7 else (mir[0], mir[1])
        # the dock's operating hazard zone. Docking, the MiR250 drives within 0.5 m of the station with its personnel
        # detection muted; MiR's user guide (v1.2, section 10.7) has such a zone marked with signal tape "at least one
        # meter away from the potentially hazardous area in all directions", and no work station inside it. So the tape
        # runs 1 m outside the docked robot. Overlapping zones are one zone: their union is taped
        z = (dx - w / 2 - ZONE_MM, dy - h / 2 - ZONE_MM, w + 2 * ZONE_MM, h + 2 * ZONE_MM)
        zones.append(z)
        polys.append(sbox(z[0], z[1], z[0] + z[2], z[1] + z[3]))
        ax.add_patch(Rectangle((dx - w / 2, dy - h / 2), w, h, fill=False, ec="white", lw=2.2, zorder=3))
    un = unary_union(polys)
    for g in getattr(un, "geoms", [un]):
        xs, ys = g.exterior.xy
        ax.plot(xs, ys, color=Y, lw=4.5, zorder=3, solid_capstyle="butt")
        ax.plot(xs, ys, color="#1f1f1f", lw=4.5, ls=(0, (2, 2)), zorder=3.1)
    # keep-clear and safety-equipment spots: illustrative, put where nothing else is (free floor next to the rows)
    taken = [(a, c, b - a, d - c) for a, b, c, d in plan["floor"]["machines"].values()] + zones

    def free(cx, cy, half=500):
        return all(cx + half < x or cx - half > x + w or cy + half < y or cy - half > y + h for x, y, w, h in taken)
    spots = []
    for cy, xs in ((-1950.0, (-9300, 9800)), (-5900.0, (-9500, -2700, 9300))):
        for x_want in xs:
            cands = sorted((abs(cx - x_want), cx) for cx in range(-10000, 10001, 100) if free(cx, cy))
            if cands:
                spots.append((cands[0][1], cy))
                taken.append((cands[0][1] - 450, cy - 450, 900, 900))
    for i, (kx, ky) in enumerate(spots):
        green = i == len(spots) - 1
        ax.add_patch(Rectangle((kx - 450, ky - 450), 900, 900, fc=FLOOR["safety equipment"]["rgb"] if green else
                               "white", ec="none" if green else FLOOR["keep clear"]["rgb"], lw=2.5,
                               hatch=None if green else "\\\\", zorder=3))
    handles = [Patch(fc=Y, ec="none", label="yellow: lane edge (the MiR250s' aisle)"),
               Patch(fc="white", ec=Y, lw=3, ls="--", label="black/yellow tape: an operating hazard zone, 1 m round "
                     "each docked MiR250 (ISO 3691-4, MiR's guide)"),
               Patch(fc="white", ec="#8a8f98", label="white: where a robot docks, or a cart, bin or stand goes"),
               Patch(fc="white", ec=FLOOR["keep clear"]["rgb"], hatch="\\\\", label="red/white: keep clear "
                     "(extinguisher, electrical panel, eyewash); spots illustrative"),
               Patch(fc=FLOOR["safety equipment"]["rgb"], ec="none", label="green: safety equipment (eyewash, "
                     "first aid, spill kit); spot illustrative")]
    ax.legend(handles=handles, loc="lower left", fontsize=9, frameon=True, framealpha=1.0, ncol=2,
              bbox_to_anchor=(0.0, -0.02))
    ax.set_title("Floor marking: five meanings, each with its own colour or pattern; everything else is bare floor",
                 fontsize=12.5, loc="left", weight="bold")
    ax.set_xlim(-12000, 12400)
    ax.set_ylim(-13000, 2500)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main(argv) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    res = check()
    (OUT / "cvd_check.json").write_text(json.dumps(dict(
        method="sRGB targets simulated for full protan, deutan and tritan dichromacy (Machado et al. 2009 via "
               "colorspacious, severity 100), colour difference in CAM02-UCS; pass >= 20, needs a second cue 12-20, "
               "fail < 12", palettes=res), indent=1) + "\n")
    for pal, rows in res.items():
        if pal == "ok":
            continue
        worst = min(rows, key=lambda r: r[r["worst"]]) if rows else None
        print(f"{pal:22s} closest: {worst['a']} / {worst['b']} {worst[worst['worst']]} ({worst['worst']}) "
              f"{worst['grade']}" if worst else pal)
    if len(argv) < 2 or argv[1] != "check":
        palette_figure(res, OUT / "palette_cvd.png")
        floor_figure(OUT / "floor_marking.png")
        labels_figure(OUT / "labels.png")
    return 0 if res["ok"] else 1



# ===================================================================================================== label mock-ups
def labels_figure(path: Path) -> None:
    """Print-size mock-ups (300 dpi): jar labels with the family stripe, tool tags, a waste-can label, the HOLD tag.
    The text is the authority; the stripe or band only makes a mismatch easy to see."""
    from PIL import Image, ImageDraw, ImageFont
    import qrcode
    F, FB, FM = ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    s = 300 / 25.4
    ink, ink2 = (31, 35, 40), (75, 85, 99)

    def rgb(h):
        return tuple(int(255 * v) for v in _rgb1(h))

    def label(w, h, stripe, lines, qr=None, stripe_mm=4.0, border=(150, 150, 150), fill="white"):
        W_, H_ = int(w * s), int(h * s)
        im = Image.new("RGB", (W_, H_), fill)
        d = ImageDraw.Draw(im)
        if stripe:
            d.rectangle((0, 0, W_, int(stripe_mm * s)), fill=rgb(stripe))
        d.rectangle((1, 1, W_ - 2, H_ - 2), outline=border, width=3)
        qx = W_
        if qr:
            q = qrcode.make(qr, border=1).convert("RGB").resize((int((h - stripe_mm - 4) * s),) * 2, 0)
            qx = W_ - q.size[0] - int(1.5 * s)
            im.paste(q, (qx, int((stripe_mm + 2) * s)))
        y = (stripe_mm + 1.8) * s if stripe else 2.0 * s
        for text, mm, font, col in lines:
            f = ImageFont.truetype(font, int(mm * s))
            while d.textlength(text, font=f) > qx - 3.5 * s and f.size > 10:
                f = ImageFont.truetype(font, f.size - 2)
            d.text((2.0 * s, y), text, font=f, fill=col)
            y += mm * s * 1.25
        return im
    al, cu = FAMILY["Al"]["rgb"], FAMILY["Cu"]["rgb"]
    items = [
        ("Jar label (Al lot), 70 x 32 mm", label(70, 32, al, [("c3k0n5", 6.0, FM, ink), ("Al 4047 · 20-63 µm · 250 mL", 3.0, F, ink2),
                                                              ("AL FAMILY · tray O", 2.8, FB, ink2)], qr="lot c3k0n5")),
        ("Jar label (Cu lot)", label(70, 32, cu, [("k7m2q9", 6.0, FM, ink), ("630 bronze (NAB) · 45-105 µm · 250 mL", 3.0, F, ink2),
                                                  ("CU FAMILY · tray O", 2.8, FB, ink2)], qr="lot k7m2q9")),
        ("Tool tag on a sieve tab, 12 mm tape", label(48, 12, al, [("AL · sieve No. 325 · #1", 3.4, FB, ink)], stripe_mm=3.0)),
        ("Funnel band text", label(48, 12, cu, [("CU · Ni powder · funnel", 3.4, FB, ink)], stripe_mm=3.0)),
        ("Powder-waste can, 90 x 40 mm", label(90, 40, al, [("AL FAMILY POWDER WASTE", 5.0, FB, ink),
                                                            ("Al, Si and Mg fines only. Never Cu, Fe or oxides.", 2.9, F, ink2),
                                                            ("Class D extinguisher. Keep lid on.", 2.9, F, ink2)], stripe_mm=6.0)),
        ("HOLD tag (red), 50 x 30 mm", label(50, 30, None, [("HOLD", 9.0, FB, (255, 255, 255)),
                                                            ("do not use: waiting for a decision", 2.6, F, (255, 255, 255))],
                                              border=(120, 10, 25), fill=(200, 16, 46))),
    ]
    pad, cols = 60, 2
    rows_h = []
    for i in range(0, len(items), cols):
        rows_h.append(max(im.height for _, im in items[i:i + cols]) + 70)
    Wt = cols * (max(im.width for _, im in items) + pad) + pad
    sheet = Image.new("RGB", (Wt, sum(rows_h) + 190), "white")
    d = ImageDraw.Draw(sheet)
    d.text((pad, 24), "Label mock-ups at print size (300 dpi): the family stripe along the top; the words underneath "
           "are the authority.\nThe lots and fractions are examples.", font=ImageFont.truetype(FB, 34), fill=ink,
           spacing=8)
    y = 130
    for r, i in enumerate(range(0, len(items), cols)):
        x = pad
        for cap, im in items[i:i + cols]:
            d.text((x, y), cap, font=ImageFont.truetype(F, 30), fill=ink2)
            sheet.paste(im, (x, y + 45))
            x += max(im2.width for _, im2 in items) + pad
        y += rows_h[r]
    sheet.save(path, optimize=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
