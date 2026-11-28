#!/usr/bin/env python3
"""What the A1 mini will actually print at the joints: an as-sliced fit check.

    python fit_sim.py            # reads build/lid_mount_A1mini_PLA.3mf (or the committed 3MF)

Two layers of prediction, and the second is only as good as its source:

1. **As sliced.** The G-code inside the 3MF is what the printer runs. Each fit-critical
   layer is rebuilt as the union of its extrusion moves, each buffered by half the
   ;LINE_WIDTH Bambu writes before it (arcs from arc fitting included), and the post tops,
   sockets, M3 nut slots, nut traps and clearance holes are measured on that plastic. This
   catches everything the slicer does to the CAD: layer quantisation, wall placement,
   arc fitting, compensation settings.
2. **As printed.** Bambu's own PLA Basic filament preset for the A1 mini carries the
   dimensional-error model behind its "Auto circle contour-hole compensation": a round
   hole of diameter d prints small by clamp(0.23415 - 0.008 d, 0.088, 0.22) mm per side,
   and a round contour small by clamp(0.008 d - 0.041, -0.035, 0.033) mm per side
   (hole_coef_* / counter_coef_* in "Bambu PLA Basic @BBL A1M", applied radially in
   LayerRegion::auto_circle_compensation). Straight walls take the large-diameter limits,
   tight corner arcs the value for a circle of the same radius. A Monte Carlo then adds
   the things the model leaves out, with spreads that are assumptions, not measurements:
   printer-to-printer spread of that model, nut sizes across their ISO 4032 range, and the
   post-to-socket position error from shrinkage, XY skew and post lean.

Writes fit_sim.json and preview/fit_sim.png.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import zipfile
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
PARAMS = json.loads((HERE.parent / "exports" / "params.json").read_text())

# Where slice_a1mini.py puts each part's STL origin on the bed, and how the part was turned
# for printing (the deck is flipped about X, so y -> -y and z -> deck_top - z).
BASE_AT, DECK_AT = (90.0, 90.0), (90.0, 100.0)
Z_DECK = 99.66                       # deck underside, assembly Z (checks.json)
Z_DECK_TOP = Z_DECK + PARAMS["deck_t"]

# The fits before this check (commit a2a0794), marked on the figure for comparison.
PREVIOUS = {"socket_clear": 0.25, "m3_nut_slot_w": 5.7}

# Bambu PLA Basic @BBL A1M (identical for the A1, P1 and X1 presets).
HOLE = dict(c1=0.0, c2=-0.008, c3=0.23415, lo=0.088, hi=0.22)
CONTOUR = dict(c1=0.0, c2=0.008, c3=-0.041, lo=-0.035, hi=0.033)


def model_undersize(d: float, m: dict) -> float:
    """Per-side amount a round feature of diameter d prints small, per Bambu's model."""
    return min(max(m["c2"] * d + m["c3"], m["lo"]), m["hi"])


# --- G-code -> plastic -----------------------------------------------------------

def arc_points(x0, y0, x1, y1, i, j, cw, step_deg=4.0):
    cx, cy = x0 + i, y0 + j
    a0, a1 = math.atan2(y0 - cy, x0 - cx), math.atan2(y1 - cy, x1 - cx)
    if cw and a1 >= a0:
        a1 -= 2 * math.pi
    if not cw and a1 <= a0:
        a1 += 2 * math.pi
    r = math.hypot(x0 - cx, y0 - cy)
    n = max(2, int(abs(a1 - a0) / math.radians(step_deg)) + 1)
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def layers_of(gcode: str, wanted: list[float]) -> dict[float, Polygon]:
    """Deposited plastic on the layers whose top (; Z_HEIGHT) is closest to each wanted Z."""
    tops = sorted({float(z) for z in re.findall(r"^; Z_HEIGHT: ([\d.]+)", gcode, re.M)})
    pick = {min(tops, key=lambda t: abs(t - w)): w for w in wanted}
    beads: dict[float, list] = {t: [] for t in pick}
    x = y = 0.0
    z = width = None
    for line in gcode.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":")[1])
        elif line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":")[1])
        elif line[:3] in ("G1 ", "G0 ", "G2 ", "G3 "):
            w = dict((m[0], float(m[1:])) for m in line.split(";")[0].split()[1:] if m[0] in "XYEIJ")
            nx, ny = w.get("X", x), w.get("Y", y)
            if z in beads and w.get("E", 0) > 0 and width and (nx, ny) != (x, y):
                pts = ([(x, y), (nx, ny)] if line[1] in "01"
                       else arc_points(x, y, nx, ny, w.get("I", 0), w.get("J", 0), line[1] == "2"))
                beads[z].append(LineString(pts).buffer(width / 2, quad_segs=6))
            x, y = nx, ny
    return {pick[t]: unary_union(b) for t, b in beads.items()}


def piece_at(plastic, x, y) -> Polygon:
    """The island of plastic around (x, y), or the nearest one."""
    geoms = getattr(plastic, "geoms", [plastic])
    return min(geoms, key=lambda g: Polygon(g.exterior).distance(Point(x, y)))


def void_at(plastic, x, y, r=12.0) -> Polygon:
    """The empty region containing (x, y), within r of it."""
    empty = box(x - r, y - r, x + r, y + r).difference(plastic)
    geoms = getattr(empty, "geoms", [empty])
    return next(g for g in geoms if g.contains(Point(x, y)))


def span(poly, x, y, axis: str, band=0.4) -> float:
    """Width of poly along an axis, through a thin band centred on (x, y)."""
    strip = box(-1e3, y - band, 1e3, y + band) if axis == "x" else box(x - band, -1e3, x + band, 1e3)
    b = poly.intersection(strip).bounds
    return (b[2] - b[0]) if axis == "x" else (b[3] - b[1])


# --- measurements ---------------------------------------------------------------------

def measure(gz: dict[int, str]) -> dict:
    p = PARAMS
    c = p["post_c"]
    z_band = (Z_DECK + 0.6 + (Z_DECK + p["socket_depth"] - p["post_chamfer"])) / 2
    z_slot = Z_DECK + p["socket_depth"] - p["m3_nut_roof"] - p["m3_nut_slot_h"] / 2
    z_scan = [round(z_slot + dz, 2) for dz in np.arange(-2.4, 2.41, 0.2)]
    base = layers_of(gz[1], [z_band, z_slot, 4.0, 1.0] + z_scan)
    deck = layers_of(gz[2], [Z_DECK_TOP - z_band, 1.0, 0.2, 4.0, 8.0])
    out = {"layers": {"post (base, Z)": z_band, "nut slot (base, Z)": z_slot,
                      "socket (deck, print Z)": Z_DECK_TOP - z_band}, "posts": [], "nut_slots": []}
    shapes = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx, by = BASE_AT[0] + sx * c, BASE_AT[1] + sy * c
            dx, dy = DECK_AT[0] + sx * c, DECK_AT[1] - sy * c      # the deck is printed flipped
            post = Polygon(piece_at(base[z_band], bx, by).exterior)
            sock = void_at(deck[Z_DECK_TOP - z_band], dx, dy)
            sock_c = sock.centroid
            post_c = post.centroid
            # Put both in the post's frame: flip the socket back and centre it on the post.
            from shapely import affinity
            sock_a = affinity.translate(affinity.scale(sock, 1, -1, origin=(sock_c.x, sock_c.y)),
                                        post_c.x - sock_c.x, post_c.y - sock_c.y)
            wx, wy = span(post, post_c.x, post_c.y, "x"), span(post, post_c.x, post_c.y, "y")
            sx_, sy_ = span(sock_a, post_c.x, post_c.y, "x"), span(sock_a, post_c.x, post_c.y, "y")
            out["posts"].append({
                "post": [sx * c, sy * c], "post_w_xy": [round(wx, 3), round(wy, 3)],
                "socket_w_xy": [round(sx_, 3), round(sy_, 3)],
                "clear_per_side_xy": [round((sx_ - wx) / 2, 3), round((sy_ - wy) / 2, 3)],
                "corner_clear_min": round(corner_gap(post, sock_a, post_c.x, post_c.y, p["socket_clear"], socket_r()), 3),
                "socket_centre_vs_nominal": [round(sock_c.x - dx, 3), round(sock_c.y - dy, 3)],
            })
            shapes.setdefault("post", post)
            shapes.setdefault("socket", sock_a)
            # M3 nut slot: the gap between the prongs, halfway out along the channel.
            gx = bx + sx * 3.5
            cut = base[z_slot].intersection(LineString([(gx, by - 6), (gx, by + 6)]))
            ys = [b for g in getattr(cut, "geoms", [cut]) for b in (g.bounds[1], g.bounds[3])]
            slot_w = min(y for y in ys if y > by) - max(y for y in ys if y < by)
            out["nut_slots"].append({"post": [sx * c, sy * c], "slot_w": round(slot_w, 3)})
            shapes.setdefault("slot_layer", piece_at(base[z_slot], bx, by))
            shapes.setdefault("slot_at", (bx, by, sx))

    # The slot's floor and roof as sliced: which layers leave the channel open, halfway out.
    bx, by = BASE_AT[0] + c, BASE_AT[1] + c
    open_z = [z for z in z_scan
              if not Polygon(piece_at(base[z], bx, by).exterior).contains(Point(bx + 3.5, by))]
    tops = sorted({float(t) for t in re.findall(r"^; Z_HEIGHT: ([\d.]+)", gz[1], re.M)})
    top_of = lambda z: min(tops, key=lambda t: abs(t - z))
    floor, roof = top_of(min(open_z)) - 0.2, top_of(max(open_z))
    out["nut_slot_z"] = {"floor": round(floor, 2), "roof": round(roof, 2), "height": round(roof - floor, 2),
                         "design": [round(z_slot - p["m3_nut_slot_h"] / 2, 2), round(z_slot + p["m3_nut_slot_h"] / 2, 2)]}

    def hole(plastic, x, y) -> dict:
        v = void_at(plastic, x, y, r=5.0)
        return {"d_equiv": round(2 * math.sqrt(v.area / math.pi), 3),
                "af_y": round(span(v, x, y, "y", band=0.3), 3)}

    h = p["cam_hole_pitch"] / 2
    pi = [(p["pi_cx"] + sx * p["pi_hole_x"] / 2, p["pi_cy"] + sy * p["pi_hole_y"] / 2) for sx in (-1, 1) for sy in (-1, 1)]
    out["holes"] = {
        "M3 clearance, deck (design %.1f)" % p["m3_clear_d"]: hole(deck[1.0], DECK_AT[0] + c, DECK_AT[1] - c),
        "M2.5 clearance, camera boss (design %.1f)" % p["m25_clear_d"]: hole(deck[8.0], DECK_AT[0] + h, DECK_AT[1] - h),
        "M4 clearance, base (design %.1f)" % p["bolt_clear_d"]: hole(base[1.0], BASE_AT[0] + p["bolt_xy"], BASE_AT[1] + p["bolt_xy"]),
    }
    out["nut_traps"] = {
        "M2.5 camera trap, first layer (design AF %.1f)" % p["m25_nut_af"]: hole(deck[0.2], DECK_AT[0] + h, DECK_AT[1] - h),
        "M2.5 camera trap, layer 6 (design AF %.1f)" % p["m25_nut_af"]: hole(deck[1.0], DECK_AT[0] + h, DECK_AT[1] - h),
        "M2.5 Pi trap (design AF %.1f)" % p["m25_nut_af"]: hole(deck[4.0], DECK_AT[0] + pi[0][0], DECK_AT[1] - pi[0][1]),
        "M4 trap (design AF %.1f)" % p["m4_nut_af"]: hole(base[4.0], BASE_AT[0] + p["bolt_xy"], BASE_AT[1] + p["bolt_xy"]),
    }
    return out, shapes


# --- the Monte Carlo ------------------------------------------------------------------------

def rounded_square(half: float, r: float, cx=0.0, cy=0.0) -> Polygon:
    return box(cx - half + r, cy - half + r, cx + half - r, cy + half - r).buffer(r, quad_segs=32)


def corner_zones(cx, cy, flat_half: float, reach=9.0):
    """The four regions beyond the ends of the socket's flats, where its corner arcs are."""
    return unary_union([box(min(cx + sx * flat_half, cx + sx * reach), min(cy + sy * flat_half, cy + sy * reach),
                            max(cx + sx * flat_half, cx + sx * reach), max(cy + sy * flat_half, cy + sy * reach))
                        for sx in (-1, 1) for sy in (-1, 1)])


def socket_r(p=PARAMS) -> float:
    return p.get("socket_corner_r") or 1.5 + p["socket_clear"]


def corner_gap(post: Polygon, socket: Polygon, cx, cy, clear: float, r_sock: float) -> float:
    """Smallest gap between the socket's corner arcs and the post."""
    arcs_from = PARAMS["post_w"] / 2 + clear - r_sock
    return socket.exterior.intersection(corner_zones(cx, cy, arcs_from - 0.01)).distance(post)


def designed_corner_gap(clear: float, r_sock: float) -> float:
    half = PARAMS["post_w"] / 2
    return corner_gap(rounded_square(half, 1.5), rounded_square(half + clear, r_sock), 0, 0, clear, r_sock)


def draws(n=200_000, seed=1) -> dict:
    """Random draws shared by every design evaluated, so the comparisons are paired."""
    rng = np.random.default_rng(seed)
    c = PARAMS["post_c"]
    # One printer-to-printer offset on Bambu's model per sample, for holes and for contours.
    d = {"dh": rng.normal(0, 0.03, n), "dc": rng.normal(0, 0.03, n),
         "nut": rng.uniform(5.32, 5.50, n)}                   # ISO 4032 M3: s = 5.32 ... 5.50
    # Post-to-socket position error at each of the 4 posts, per axis: differential shrinkage
    # between base and deck (0.1 % sigma), XY skew (0.05 deg sigma; printing the deck flipped
    # doubles it, and turning the deck takes back half) and post lean at 96 mm (0.05 mm
    # sigma). The deck floats to the mean, so only the residual counts.
    sx, sy = np.array([-1, -1, 1, 1]), np.array([-1, 1, -1, 1])
    eps = rng.normal(0, 0.001, (n, 1))
    t = np.tan(np.radians(rng.normal(0, 0.05, (n, 1))))
    ex = c * (sx * eps + sy * t) + rng.normal(0, 0.05, (n, 4))
    ey = c * (sy * eps - sx * t) + rng.normal(0, 0.05, (n, 4))
    ex -= ex.mean(axis=1, keepdims=True)
    ey -= ey.mean(axis=1, keepdims=True)
    d["pos"] = np.maximum(np.abs(ex), np.abs(ey)).max(axis=1)
    return d


def socket_odds(flat_sliced: float, corner_sliced: float, r_sock: float, d: dict) -> dict:
    """Straight walls take the model's large-diameter limits; a corner arc of radius r, a circle of 2r.

    Only a post top that is bigger than its socket can jam. The posts are 96 mm cantilevers,
    about 6.5 N/mm at the tip (3EI/L^3, walls only, E = 3 GPa), so a post top that is merely
    out of place by a tenth of a millimetre bends into line under well under a newton."""
    flat = flat_sliced - (HOLE["lo"] + d["dh"]) + (CONTOUR["hi"] + d["dc"])
    corner = (corner_sliced - (model_undersize(2 * r_sock, HOLE) + d["dh"])
              + (model_undersize(2 * 1.5, CONTOUR) + d["dc"]))
    size = np.minimum(flat, corner)
    return {
        "flats, per side (predicted median)": round(float(np.median(flat)), 3),
        "flats, per side (5th-95th percentile)": [round(float(q), 3) for q in np.percentile(flat, [5, 95])],
        "corners (predicted median)": round(float(np.median(corner)), 3),
        "P(post top fits its socket)": round(float(np.mean(size >= 0)), 3),
        "P(fits, and all four drop in without flexing a post)": round(float(np.mean(size - d["pos"] >= 0)), 3),
        "P(tight: pushes in with up to 0.05 mm interference)": round(float(np.mean((size < 0) & (size >= -0.05))), 3),
        "P(needs trimming: over 0.05 mm interference)": round(float(np.mean(size < -0.05)), 3),
    }


def slot_odds(slot_sliced: float, d: dict) -> dict:
    gap = slot_sliced - 2 * (HOLE["lo"] + d["dh"]) - d["nut"]
    return {"slot width (predicted median)": round(float(np.median(gap + d["nut"])), 3),
            "P(nut slides in)": round(float(np.mean(gap >= 0)), 3),
            "P(nut pressed in: up to 0.1 mm interference)": round(float(np.mean((gap < 0) & (gap >= -0.1))), 3),
            "P(nut won't go)": round(float(np.mean(gap < -0.1)), 3),
            "P(loose: gap over 0.3)": round(float(np.mean(gap > 0.3)), 3)}


def monte_carlo(meas: dict) -> dict:
    p, d = PARAMS, draws()
    r_sock = socket_r()
    flat = float(np.mean([np.mean(q["clear_per_side_xy"]) for q in meas["posts"]]))
    corner = float(min(q["corner_clear_min"] for q in meas["posts"]))
    slot = float(np.mean([s["slot_w"] for s in meas["nut_slots"]]))
    return {"post_in_socket": {"flats, per side (as sliced)": round(flat, 3),
                               "corners (as sliced)": round(corner, 3), **socket_odds(flat, corner, r_sock, d)},
            "m3_nut_in_slot": {"slot width (as sliced)": round(slot, 3), **slot_odds(slot, d)}}


def sweep(meas: dict) -> dict:
    """The same odds over a range of designs, using the as-sliced offsets measured here."""
    p, d = PARAMS, draws(n=50_000)
    flat_off = float(np.mean([np.mean(q["clear_per_side_xy"]) for q in meas["posts"]])) - p["socket_clear"]
    clears = np.round(np.arange(0.05, 0.401, 0.025), 3)
    out = {"socket_clear": clears.tolist(), "P_fits": {}, "flats_median": {}}
    for label, r_of in (("corners concentric (r = 1.5 + clear)", lambda c: 1.5 + c),
                        ("corners relieved (r = 1.0)", lambda c: 1.0)):
        odds = [socket_odds(c + flat_off, designed_corner_gap(c, r_of(c)), r_of(c), d) for c in clears]
        out["P_fits"][label] = [o["P(post top fits its socket)"] for o in odds]
        out["flats_median"][label] = [o["flats, per side (predicted median)"] for o in odds]
    slot_off = float(np.mean([s["slot_w"] for s in meas["nut_slots"]])) - p["m3_nut_slot_w"]
    widths = np.round(np.arange(5.5, 6.01, 0.05), 3)
    odds = [slot_odds(w + slot_off, d) for w in widths]
    out.update({"m3_nut_slot_w": widths.tolist(),
                "P_nut_slides": [o["P(nut slides in)"] for o in odds],
                "P_nut_loose": [o["P(loose: gap over 0.3)"] for o in odds]})
    return out


def predicted_holes(meas: dict) -> dict:
    out = {}
    for name, h in meas["holes"].items():
        d = h["d_equiv"]
        out[name] = {"as_sliced": d, "predicted": round(d - 2 * model_undersize(d, HOLE), 3)}
    for name, h in meas["nut_traps"].items():
        out[name] = {"as_sliced_af": h["af_y"], "predicted_af": round(h["af_y"] - 2 * HOLE["lo"], 3)}
    return out


# --- figure ----------------------------------------------------------------------------------

def figure(shapes: dict, meas: dict, mc: dict, sw: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly

    blue, orange, ink, muted, grid = "#2a78d6", "#eb6834", "#52514e", "#898781", "#e1e0d9"
    plt.rcParams.update({"font.size": 9, "text.color": ink, "axes.labelcolor": ink, "axes.edgecolor": muted,
                         "xtick.color": muted, "ytick.color": muted, "axes.titlesize": 10})

    def draw(ax, geom, **kw):
        for g in getattr(geom, "geoms", [geom]):
            ax.add_patch(MPoly(np.asarray(g.exterior.coords), closed=True, **kw))
            for r in g.interiors:
                ax.add_patch(MPoly(np.asarray(r.coords), closed=True, fc="white", ec=kw.get("ec", ink), lw=0.5))

    fig, axs = plt.subplots(2, 2, figsize=(10, 9.2))
    ax = axs[0, 0]
    post, sock = shapes["post"], shapes["socket"]
    cx, cy = post.centroid.x, post.centroid.y
    draw(ax, box(cx - 7, cy - 7, cx + 7, cy + 7).difference(sock), fc=blue, ec="white", lw=0.6, alpha=0.55)
    draw(ax, post, fc=orange, ec="white", lw=0.6, alpha=0.85)
    ps = mc["post_in_socket"]
    ax.set_title(f"(a) Post top (orange) in its deck socket (blue), as sliced\n"
                 f"gap {ps['flats, per side (as sliced)']:.2f} mm on the flats, {ps['corners (as sliced)']:.2f} mm in the corners",
                 loc="left")
    ax.set_xlim(cx - 7, cx + 7), ax.set_ylim(cy - 7, cy + 7), ax.set_aspect("equal")
    ax.set_xticks([]), ax.set_yticks([])

    ax = axs[0, 1]
    bx, by, sx = shapes["slot_at"]
    draw(ax, shapes["slot_layer"], fc=orange, ec="white", lw=0.6, alpha=0.85)
    af = 5.5
    hexagon = Polygon([(bx + af / math.sqrt(3) * math.cos(math.radians(a)), by + af / math.sqrt(3) * math.sin(math.radians(a)))
                       for a in range(0, 360, 60)])
    draw(ax, hexagon, fc="none", ec="#0b0b0b", lw=1.2, ls="--")
    ns = mc["m3_nut_in_slot"]
    ax.set_title(f"(b) M3 nut slot through a post at Z {meas['layers']['nut slot (base, Z)']:.1f}, as sliced\n"
                 f"{ns['slot width (as sliced)']:.2f} mm wide; dashed: the largest M3 nut, 5.50 mm", loc="left")
    ax.set_xlim(bx - 7, bx + 7), ax.set_ylim(by - 7, by + 7), ax.set_aspect("equal")
    ax.set_xticks([]), ax.set_yticks([])

    p = PARAMS
    ax = axs[1, 0]
    relieved = socket_r() < 1.5 + p["socket_clear"] - 1e-9
    (lab_c, conc), (lab_r, reli) = sw["P_fits"].items()
    ax.plot(sw["socket_clear"], conc, color=orange, lw=2)
    ax.plot(sw["socket_clear"], reli, color=blue, lw=2)
    ax.annotate(lab_r, (0.148, 0.86), ha="right", fontsize=8.5, color=ink)
    ax.annotate(lab_c, (0.262, 0.40), ha="left", fontsize=8.5, color=ink)
    x0, x1 = p["socket_clear"], PREVIOUS["socket_clear"]
    this = reli if relieved else conc
    y0, y1 = np.interp(x0, sw["socket_clear"], this), np.interp(x1, sw["socket_clear"], conc)
    ax.plot([x1], [y1], "o", ms=8, mfc="white", mec=orange, mew=2)
    ax.annotate(f"before: {y1:.0%}", (x1, y1), xytext=(8, -4), textcoords="offset points", fontsize=8.5, color=ink)
    ax.plot([x0], [y0], "o", ms=8, color=blue if relieved else orange, mec="white", mew=2)
    ax.annotate(f"now: {y0:.0%}", (x0, y0), xytext=(-8, -16), textcoords="offset points", ha="right",
                fontsize=8.5, color=ink)
    ax.set_title("(c) Chance every post top fits its socket without trimming", loc="left")
    ax.set_xlabel("socket clearance in the CAD, mm per side"), ax.set_ylabel("probability")
    ax.set_ylim(-0.02, 1.02), ax.grid(color=grid, lw=0.6), ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    ax = axs[1, 1]
    ax.plot(sw["m3_nut_slot_w"], sw["P_nut_slides"], color=blue, lw=2)
    ax.plot(sw["m3_nut_slot_w"], sw["P_nut_loose"], color=orange, lw=2)
    ax.annotate("nut slides in", (sw["m3_nut_slot_w"][2], sw["P_nut_slides"][2]), xytext=(8, -2),
                textcoords="offset points", fontsize=8.5, color=ink)
    ax.annotate("more than 0.3 mm play", (sw["m3_nut_slot_w"][-3], sw["P_nut_loose"][-3]), xytext=(-40, 10),
                textcoords="offset points", fontsize=8.5, color=ink)
    w0, w1 = p["m3_nut_slot_w"], PREVIOUS["m3_nut_slot_w"]
    y0, y1 = (np.interp(w, sw["m3_nut_slot_w"], sw["P_nut_slides"]) for w in (w0, w1))
    ax.plot([w1], [y1], "o", ms=8, mfc="white", mec=blue, mew=2)
    ax.annotate(f"before: {y1:.0%}", (w1, y1), xytext=(-8, 6), textcoords="offset points", ha="right",
                fontsize=8.5, color=ink)
    ax.plot([w0], [y0], "o", ms=8, color=blue, mec="white", mew=2)
    ax.annotate(f"now: {y0:.0%}", (w0, y0), xytext=(4, -16), textcoords="offset points", fontsize=8.5, color=ink)
    ax.set_title("(d) M3 nut in its side slot", loc="left")
    ax.set_xlabel("nut slot width in the CAD, mm"), ax.set_ylabel("probability")
    ax.set_ylim(-0.02, 1.02), ax.grid(color=grid, lw=0.6), ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.text(0.01, 0.005, "(a), (b): rebuilt from the G-code in lid_mount_A1mini_PLA.3mf. (c), (d): that geometry, plus Bambu's own "
             "PLA Basic error model for the A1 mini\nand assumed spreads for printer-to-printer variation, nut size, "
             "shrinkage, skew and post lean (fit_sim.py). Estimates, not measurements.",
             fontsize=7.5, color=muted)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(path, dpi=130)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--3mf", dest="tmf", type=Path, default=HERE / "lid_mount_A1mini_PLA.3mf")
    ap.add_argument("--out", type=Path, default=HERE / "fit_sim.json")
    args = ap.parse_args()
    with zipfile.ZipFile(args.tmf) as z:
        gz = {n: z.read(f"Metadata/plate_{n}.gcode").decode() for n in (1, 2)}
    meas, shapes = measure(gz)
    mc = monte_carlo(meas)
    sw = sweep(meas)
    result = {"source": args.tmf.name, "design": {k: PARAMS.get(k) for k in (
                  "socket_clear", "socket_corner_r", "m3_nut_slot_w", "m3_nut_slot_h", "m25_nut_af", "m4_nut_af",
                  "m3_clear_d", "m25_clear_d", "bolt_clear_d")},
              "bambu_model": {"hole": HOLE, "contour": CONTOUR},
              "as_sliced": meas, "predicted": predicted_holes(meas), "monte_carlo": mc, "sweep": sw}
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "preview").mkdir(exist_ok=True)
    figure(shapes, meas, mc, sw, HERE / "preview" / "fit_sim.png")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
