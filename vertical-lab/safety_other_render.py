"""The figures for safety_other.py's assets (notes/safety.md, "The other safety assets").

    python3 safety_other.py                     # report: NFPA 10 for the ordinary units, ANSI Z358.1 for the showers,
                                                #   the O2 monitors, every spot's clearances, the BoM -> out/safety_other.json
    python3 safety_other.py plan                # out/safety_other_plan.png
    python3 safety_other.py abc-search          # the fewest ordinary units on the racking that pass
    xvfb-run -a python3 safety_other.py sheet   # out/safety_other_assets.png
    VLAB_ONLY_TRAYS= xvfb-run -a python3 safety_other.py lab   # out/safety_other_lab.png
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np

import safety as S
import safety_other as SO
import safety_render as SR

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
INK, INK2, SURF, GRID = SR.INK, SR.INK2, SR.SURF, SR.GRID
RED, GREEN, BLUE, YEL = "#c8201a", "#0f8a4a", "#2f6db5", SR.YEL


# ================================================================================================ the floor plan
def plan() -> str:
    """out/safety_other_plan.png: the floor from above: the walk to the nearest ordinary unit as a field (to NFPA 10's
    75 ft), the ordinary units on the racking, the Class D units they keep away from, the two showers and the walk to
    each from its hood, the O2 monitors with Columbia's 20 ft radius round each, and the ICP-MS station at its
    suggested spot."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    import matplotlib.patheffects as pe
    fl = SR.floor()
    fp = S.mir_footprint()
    rep = json.loads((OUT / "safety_other.json").read_text()) if (OUT / "safety_other.json").exists() else SO.report()
    abc = [SO.take_point(k, x, y, f) for _, k, x, y, f, _, _ in SO.PLACES if k == "abc"]
    dist, x0, y0, block = SO.walk_field(abc)
    fig, ax = plt.subplots(figsize=(19.2, 12.0), dpi=100)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    d = np.where(np.isfinite(dist), dist, np.nan).T / 1000.0
    im = ax.imshow(d, origin="lower", extent=(x0 - 50, x0 + dist.shape[0] * 100 - 50, y0 - 50,
                                              y0 + dist.shape[1] * 100 - 50),
                   cmap="Reds", vmin=0, vmax=22.86, alpha=0.40, interpolation="nearest")
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("walk to the nearest ordinary (ABC) unit, m (the scale ends at 22.9 m, NFPA 10's 75 ft)",
                 fontsize=11, color=INK2)
    names = {"glovebox": "glovebox", "repowder": "rePowder", "sieve_cell": "sieving", "vlm": "Shuttle 1",
             "vlm2": "Shuttle 2", "aconity": "Aconity MIDI", "packaging": "packaging", "instron_floor": "68FM-100",
             "instron_small": "68SC-2", "fumehood": "fume hood", "ded": "MX-Lab DED", "wire_edm": "wire EDM",
             "eos_m400": "EOS M 400-4", "meltio_cell": "Meltio cell"}
    for k, (a, b, c, e) in fl["machines"].items():
        pw = k in SO.POWDER
        ax.add_patch(Rectangle((a, c), b - a, e - c, facecolor="#efe3b0" if pw else "#d9d7d2",
                               edgecolor="#8a6d00" if pw else INK2, lw=1.0))
        if not k.startswith("charger"):
            ax.text((a + b) / 2, (c + e) / 2, names.get(k, k), ha="center", va="center", fontsize=10, color=INK)
    for k, (a, b, c, e) in SR.RACKING.items():
        ax.add_patch(Rectangle((a, c), b - a, e - c, facecolor="#dde3ee", edgecolor="#5a7aa6", lw=0.8))
        ax.text((a + b) / 2, (c + e) / 2, "racking", ha="center", va="center", fontsize=9, color="#5a7aa6",
                rotation=90 if b - a < e - c else 0)
    for k, (a, b, c, e) in SO._icpms_rects().items():
        ax.add_patch(Rectangle((a, c), b - a, e - c, facecolor="none", edgecolor=INK2, lw=1.0, ls="--"))
    ax.text(9700, -7800, "ICP-MS station (suggested, notes/icpms.md;\nnot on the floor yet)", ha="center", va="top", fontsize=9,
            color=INK2)
    a0, a1, b0, b1 = fl["aisle_mm"]
    ax.add_patch(Rectangle((a0, b0), a1 - a0, b1 - b0, facecolor="none", edgecolor="#9bb5d6", lw=1.0, ls="--"))
    ax.text(a0 + 200, (b0 + b1) / 2 + 300, "aisle, 3.0 m", color="#5a7aa6", fontsize=10, va="center")
    for key, d_ in json.loads((OUT / "safety.json").read_text())["docks"].items():
        xd, yd, hd = d_["dock"]
        w = SR._to_world(fp["mir"], xd, yd, hd)
        ax.add_patch(Rectangle((w[0], w[2]), w[1] - w[0], w[3] - w[2], facecolor="none", edgecolor="#2f6db5", lw=0.6,
                               ls=":"))
    # the Class D units, faint: the ordinary units keep 3 m from them
    for st, k, x, y, f, _ in S.PLACES:
        ax.scatter([x], [y], marker="o" if k == "b570" else ("s" if k == "680r" else "h"), s=60, c=YEL,
                   edgecolors="#8a6d00", zorder=5, alpha=0.8)
    ax.scatter([], [], marker="o", s=60, c=YEL, edgecolors="#8a6d00", label="Class D units (safety.py), for reference")
    seen = set()
    for p, pc in zip(SO.PLACES, rep["places"]):
        st, kind, x, y, face, what, ex = p
        sug = ex.get("icpms", False)
        if kind == "abc":
            ax.scatter([x], [y], marker="s", s=200, c=RED, edgecolors=INK, zorder=7,
                       label=None if "abc" in seen else "Amerex B456, 10 lb ABC, on the racking (the building's)")
            ax.add_patch(Circle((x, y), SO.NFPA10_ABC["apart_m"] * 1000.0, facecolor="none", edgecolor=RED, lw=0.8,
                                ls="--", alpha=0.7))
        elif kind == "shower":
            ax.scatter([x], [y], marker="P", s=260, c=GREEN, edgecolors=INK, zorder=7, alpha=0.55 if sug else 1.0,
                       label=None if "shower" in seen else "Guardian G1902 shower and eyewash (its column)")
            cl = SO.place_rects(kind, x, y, face)["clear"]
            ax.add_patch(Circle(((cl[0] + cl[1]) / 2, (cl[2] + cl[3]) / 2), SO.ANSI["spray_clear"], facecolor="#cfead9",
                                edgecolor=GREEN, lw=0.8, zorder=6))
            w = rep["shower"]["check"][st]
            hz = SO.HAZARDS[st]
            ax.plot([hz[0]], [hz[1]], marker="x", color=GREEN, ms=9, mew=2, zorder=7)
            t = ax.text(x - 900 if x > 0 and x > 5000 else x, y + 520 if y > -7000 else y - 600,
                        f"{w['walk_m']:.1f} m from the hood", color=INK, fontsize=10, ha="center", zorder=8,
                        fontweight="bold")
            t.set_path_effects([pe.withStroke(linewidth=3, foreground="white")])
        else:
            gas = ex["gas"]
            ax.scatter([x], [y], marker="^" if kind == "o2" else "v", s=170, c=BLUE if gas == "argon" else "#7a4fbf",
                       edgecolors=INK, zorder=7, alpha=0.55 if sug else 1.0,
                       label=None if f"o2{gas}" in seen else
                       (f"PureAire O2 monitor, argon (sensor {SO.SENSOR_Z['argon']:.0f} mm up)" if gas == "argon" else
                        f"PureAire O2 monitor, nitrogen (at {SO.SENSOR_Z['nitrogen']:.0f} mm, on Shuttle 1's side)"))
            seen.add(f"o2{gas}")
            ax.add_patch(Circle((x, y), SO.O2_RADIUS, facecolor="none", edgecolor=BLUE, lw=0.6, ls=":", alpha=0.35))
        seen.add(kind)
    for k, (x, y) in SO.HAZARDS.items():
        if k in ("fumehood", "icpms"):
            continue
        ax.plot([x], [y], marker="*", color="#1d4f91", ms=12, zorder=6)
    ax.scatter([], [], marker="*", c="#1d4f91", s=110, label="where argon or nitrogen is stored or comes in")
    ax.plot([], [], color=BLUE, lw=0.8, ls=":", label="20 ft round each O2 sensor (Columbia's detection radius)")
    ax.plot([], [], color=RED, lw=0.8, ls="--", label="3 m round each ordinary unit: no Class D unit inside")
    ac = rep["abc"]["check"]
    ax.set_xlim(-13100, 13100)
    ax.set_ylim(-12900, 4100)
    ax.set_aspect("equal")
    ax.set_xticks(np.arange(-12000, 12001, 2000))
    ax.set_yticks(np.arange(-12000, 4001, 2000))
    ax.tick_params(labelsize=9, colors=INK2)
    ax.grid(color=GRID, lw=0.6)
    for s_ in ax.spines.values():
        s_.set_color(GRID)
    ax.set_xlabel("x, mm (along the aisle)", color=INK2)
    ax.set_ylabel("y, mm", color=INK2)
    n_abc = sum(1 for p in SO.PLACES if p[1] == "abc")
    n_o2 = sum(1 for p in SO.PLACES if p[1] in ("o2", "o2wall"))
    ax.set_title(f"The other safety assets: {n_abc} ordinary extinguishers on the racking (farthest walk "
                 f"{ac['worst_walk_m']:.1f} m of NFPA 10's 22.9), 2 showers at the hoods, {n_o2} O2 monitors",
                 fontsize=15, color=INK, loc="left")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.06), ncol=3, fontsize=10.5, frameon=False)
    path = OUT / "safety_other_plan.png"
    fig.savefig(path, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)
    print("->", path.relative_to(HERE))
    return str(path)


# ================================================================================================ the asset sheet
def sheet() -> str:
    """out/safety_other_assets.png: the B456 alone and on its rack upright, its signs beside the Class D one, the
    G1902 whole and its eyewash close up, its mixing valve, and the O2 monitor on its post and close up."""
    from PIL import Image, ImageDraw
    from scene import font, T
    import tour
    tiles = []
    abc = SO.abc_parts()
    tiles.append((SR.shot(abc, (-0.55, -1.6, 0.35), pad=0.9), "Amerex B456, 10 lb ABC",
                  ["the building's ordinary unit, 4-A:80-B:C", "20 x 7.75 x 5 in, 195 psig, 15-21 ft",
                   "red: never taken for the yellow Class D"]))
    rk = dict(SO.rack_parts())
    rk.update(SO.upright_stub(2400.0))
    tiles.append((SR.shot(rk, (-0.9, -1.6, 0.45), pad=1.0, look_z=0.55), "On a rack upright, at the aisle's ends",
                  ["where a warehouse keeps its extinguishers", f"top at {SO.ABC_TOP_Z:.0f} mm (NFPA 10: at most 60 in)",
                   "3 m or more from every Class D unit"]))
    signs = {}
    for name, (m, mat) in S.sign_parts("flat").items():
        signs[f"cd {name}"] = (m.translate((-150.0, 0.0, 130.0), inplace=False), mat)
    for name, (m, mat) in SO.abc_sign_parts().items():
        signs[f"abc {name}"] = (m.translate((150.0, 0.0, 0.0), inplace=False), mat)
    sc = SR._studio("so_signs", (1000, 1000))
    SR.add_parts(sc, signs, "asset")
    sc.cam = [(0.0, -1500.0, 210.0), (0.0, 0.0, 210.0), (0, 0, 1)]
    sc.view_angle = 22.0
    tiles.append((Image.fromarray(sc.render_base()), "Signed differently",
                  ["Class D: white, a yellow star (left)", "ordinary: red, an arrow down, and A B C",
                   "in their own shapes: NOT FOR METAL FIRES"]))
    sc.pl.close()
    sh = dict(SO.shower_parts())
    sh.update(SO.mixer_parts())
    tiles.append((SR.shot(sh, (-1.1, -1.5, 0.45), pad=0.98, look_z=0.5), "Guardian G1902 shower and eyewash",
                  ["at the fume hood and the ICP-MS hood", "head 84 in up, 24 in out; 20 gpm",
                   "tempered water from a mixing valve"]))
    sc = SR._studio("so_eyewash", (1000, 1000))
    SR.add_parts(sc, SO.shower_parts(), "asset")
    b = SO.SHOWER
    sc.cam = [(-420.0, b["bowl_y"] - 700.0, b["eye_z"] + 420.0), (40.0, b["bowl_y"], b["eye_z"] - 40.0), (0, 0, 1)]
    sc.view_angle = 30.0
    tiles.append((Image.fromarray(sc.render_base()), "Its eyewash, close up",
                  ["two heads in a stainless bowl, 37.5 in up", "flip-top covers, a flag handle beside it",
                   "stay-open valves: on in under a second"]))
    sc.pl.close()
    sc = SR._studio("so_shower_top", (1000, 1000))
    SR.add_parts(sc, sh, "asset")
    sc.cam = [(-900.0, -1500.0, 2900.0), (0.0, -300.0, 2350.0), (0, 0, 1)]
    sc.view_angle = 32.0
    tiles.append((Image.fromarray(sc.render_base()), "Its head, pull rod and mixing valve",
                  ["the triangle handle 65.5 in up (ANSI: 69)", "thermostatic valve: 60-100 F, 85 F set",
                   "hot and cold down from the roof"]))
    sc.pl.close()
    o2 = SO.o2_post_parts("argon", True)
    tiles.append((SR.shot(o2, (-0.9, -1.6, 0.4), pad=1.0, look_z=0.5), "PureAire O2 monitor, for argon",
                  [f"alarms at {SO.O2['alarm_low']} and {SO.O2['alarm_high']} % O2; horn and strobe",
                   f"its sensor {SO.SENSOR_Z['argon']:.0f} mm up: argon sinks (1.38 x air)",
                   "at every argon user and store"]))
    sc = SR._studio("so_o2", (1000, 1000))
    SR.add_parts(sc, o2, "asset")
    zb = SO.O2_BOX_Z
    sc.cam = [(-380.0, -1150.0, zb + 420.0), (0.0, -40.0, zb + 285.0), (0, 0, 1)]
    sc.view_angle = 34.0
    tiles.append((Image.fromarray(sc.render_base()), "Its monitor, close up",
                  ["zirconia sensor, 0-25 %, 10+ years", "6.5 x 4.5 x 3.25 in, a 90 dB horn inside",
                   "nitrogen's at 5 ft: no remote sensor"]))
    sc.pl.close()
    W, H = 3600, 2280
    cols = 4
    tw, th = W // cols, 880
    img = Image.new("RGB", (W, H), SURF)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "The other safety assets: the building's ABC units, a shower and eyewash at each hood, O2 monitors",
           font=font(52, bold=True), fill=INK)
    for i, (im, title, lines) in enumerate(tiles):
        r, c = divmod(i, cols)
        x, y = c * tw, 110 + r * (th + 190)
        im = im.copy()
        im.thumbnail((tw - 20, th - 20))
        img.paste(im, (x + (tw - im.size[0]) // 2, y))
        d.text((x + 30, y + th + 4), title, font=font(36, bold=True), fill=INK)
        for j, t in enumerate(lines):
            d.text((x + 30, y + th + 52 + j * 34), t, font=font(28), fill=INK2)
    path = OUT / "safety_other_assets.png"
    img.save(path, optimize=True)
    print("->", path.relative_to(HERE))
    return str(path)


# ================================================================================================ in the lab
LAB_VIEWS = [
    ((-8200.0, -5600.0, 2300.0), (-11833.0, -3714.0, 1100.0), "Rack W, the aisle's west end: the building's ABC unit"),
    ((450.0, -3700.0, 2300.0), (450.0, -7000.0, 1150.0), "West of the fume hood: its shower and eyewash"),
    ((-2150.0, 1700.0, 2300.0), (-3440.0, -350.0, 1050.0), "Behind the rePowder: its argon monitor, sensor low"),
    ((2150.0, -950.0, 1750.0), (1450.0, -250.0, 1450.0), "Between the Shuttles: the N2 generator's monitor"),
]


def lab_stills() -> str:
    """out/safety_other_lab.png: setup_lab.build with every safety asset (the trays' instruments left out), four views."""
    from PIL import Image, ImageDraw
    from scene import font
    os.environ.setdefault("VLAB_ONLY_TRAYS", "")
    import lab
    import setup_lab as SL
    data = lab.meshes()
    idata = SL.load_all()
    sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, mp4=False, name="safety_other_lab")
    sc.apply()
    shots = []
    for cam, look, title in LAB_VIEWS:
        sc.cam = [cam, look, (0, 0, 1)]
        sc.view_angle = 40.0
        shots.append((Image.fromarray(sc.render_base()), title))
    sc.pl.close()
    w, h = shots[0][0].size
    tw, th = w // 2, h // 2
    img = Image.new("RGB", (2 * tw, 2 * th + 140), SURF)
    d = ImageDraw.Draw(img)
    d.text((24, 16), "In the lab: the building's ABC units, the showers at the hoods, the O2 monitors",
           font=font(int(30 * w / 1920 + 4), bold=True), fill=INK)
    for i, (im, title) in enumerate(shots):
        r, c = divmod(i, 2)
        img.paste(im.resize((tw, th)), (c * tw, 70 + r * (th + 34)))
        d.text((c * tw + 14, 70 + r * (th + 34) + th + 2), title, font=font(22, bold=True), fill=INK)
    path = OUT / "safety_other_lab.png"
    img.save(path, optimize=True)
    print("->", path.relative_to(HERE))
    return str(path)


def main(what: str):
    if what == "report":
        SO.report()
    elif what == "plan":
        plan()
    elif what == "sheet":
        sheet()
    elif what == "lab":
        lab_stills()
    elif what == "abc-search":
        r = SO.abc_search()
        print(json.dumps(dict(candidates=r["candidates"], fewest=r["choice"], runners_up=r["runners_up"]), default=float,
                         indent=1))
    elif what == "all":
        SO.report()
        plan()
        sheet()
    else:
        raise SystemExit(f"unknown: {what}")
