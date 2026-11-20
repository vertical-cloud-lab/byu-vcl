"""Ground within reach at the atomizer: bonded floor plates where the MiR250s work, a sprung two-shoe contact on each
MiR250, and the station's ground bar they all go back to (ours, for PR #318 / #303; notes/atom_vacuum.md, "Ground
within reach").

Sterling (PR #318, 2026-11-20): "Nice on having a ground cable and ground bar or similar. I wonder about trying to have
a mobile ground bar of sorts (overhead), or maybe better, just making sure ground is available within close reach
pretty much anywhere nearby machines or where the mobile manipulator would be." A MiR250 on its tyres is an isolated
conductor unless something grounds it (notes/atom_sleeve.md: NFPA 484 (2015, 8.5.2) wants mobile metal equipment bonded
or grounded before use), and the arm and the tools it holds near the powder bond through it. So every spot where a
MiR250 parks to work at the atomizer gets a stainless plate set flush in the floor, bonded to the ground bar; each MiR250
carries two copper-graphite shoes on a bracket at its front end that it lowers once it has parked and lifts before it
drives. Two checks before the arm may reach for powder or a tool:

* the MiR's own meter reads shoe A -> plate -> shoe B (both shoes on metal), and
* the station's monitor reads the plate's two leads to the ground bar (the plate still bonded),

and the MiR's bond lamp turns from amber to green. Nobody has to clip anything on, nothing trails across the floor,
and nothing hangs in the arms' way, which is why this beat the other ways (notes/atom_vacuum.md compares them).

Everything here is in the rePowder model's frame (x right, y back, z up; the furnace axis at x = y = 0) or MiR-local
(x along its length, its heading); importable without building a scene (lab._repowder() uses ``fixture_meshes``).

    import atom_ground as G
    G.add_shoes(sc, mir)                       # on a MiR250 of alloy_atomize.Mir; the shoes start up
    G.add_lamp(sc, mir); G.lamp(sc, mir, "amber")
    for name, (mesh, col) in G.plate_meshes(G.plate_rects(["vacuum", "right"])).items(): ...
    up = G.shoes_anim(sc, mir, 0.0, 1.0)       # update(u): the shoes come down onto the plate
"""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

SS = (0.78, 0.79, 0.81)              # stainless plate
SS_DK = (0.55, 0.57, 0.60)
GRN_YEL = (0.30, 0.65, 0.20)         # bonding leads and the plates' terminals
INSUL = (0.12, 0.12, 0.13)
CU_GRAPHITE = (0.20, 0.17, 0.15)     # the shoes' copper-graphite blocks
OURS = (0.20, 0.42, 0.75)            # our brackets (blue, as in atom_nilfisk)
LAMP = dict(off=(0.35, 0.35, 0.36), amber=(1.00, 0.62, 0.05), green=(0.10, 0.90, 0.25), red=(0.90, 0.10, 0.08))

# ---------------------------------------------------------------------------------------------------- the MiR's shoes
MIR_L, MIR_W, MIR_H = 800.0, 580.0, 300.0          # props.MIR (repeated so that this module imports nothing heavy)
CAB_H = 480.0                                      # props.CAB_H
SHOE_X = MIR_L / 2 + 30.0                          # the shoes' centres: 30 mm in front of the MiR's front face (x 400)
SHOE_Y = 70.0                                      # either side of its centre line
SHOE = (46.0, 38.0, 22.0)                          # copper-graphite block, x, y, z (ours: a crane-rail ground shoe's size)
LIFT = 15.0                                        # mm the shoes are lifted while the MiR drives
PLATE_TOP = 2.0                                    # the plates stand 2 mm proud of the floor (z 0): a chamfered edge
LAMP_AT = (MIR_L / 2 - 40.0 + 2.0, -200.0, MIR_H + CAB_H - 70.0)    # on the cabinet's front face (x = 360)


def _box(x0, x1, y0, y1, z0, z1) -> pv.PolyData:
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1)).triangulate()


def _cyl(c, d, r, h, res=24) -> pv.PolyData:
    return pv.Cylinder(center=c, direction=d, radius=r, height=h, resolution=res).triangulate()


def shoe_fixed_meshes() -> dict:
    """MiR-local, the parts that don't move: a bracket down the MiR's front face from the ballast plate (its top flange
    on the plate's front edge, between the cabinet's face, x 360, and the plate's edge, x 380), the actuator's body on
    it. Nothing is drilled into the MiR250 itself: the bracket hangs from the top module's plate. {name: (mesh, colour)}"""
    xb = MIR_L / 2 + 4.0                            # the bracket's inner face, clear of the light band (x 402)
    bracket = _box(xb, xb + 6.0, -110, 110, 90, MIR_H + 46.0).merge(
        _box(MIR_L / 2 - 38.0, xb + 6.0, -110, 110, MIR_H + 40.0, MIR_H + 46.0))
    actuator = _box(xb + 6.0, SHOE_X + 20.0, -40, 40, 110, 200)               # a compact 24 V linear actuator (ours)
    return {"gnd bracket (ours)": (bracket, OURS), "gnd actuator": (actuator, SS_DK)}


def shoe_moving_meshes() -> dict:
    """MiR-local with the shoes DOWN (their faces at PLATE_TOP): the actuator's rod, a crossbar and the two sprung
    shoes. They move together (``set_shoes``)."""
    sx, sy, sz = SHOE
    z0 = PLATE_TOP
    rod = _cyl((SHOE_X, 0.0, z0 + sz + 50.0), (0, 0, 1), 6.0, 100.0, 16)
    bar = _box(SHOE_X - 12.0, SHOE_X + 12.0, -SHOE_Y - 30.0, SHOE_Y + 30.0, z0 + sz + 14.0, z0 + sz + 26.0)
    springs = [_cyl((SHOE_X, s * SHOE_Y, z0 + sz + 7.0), (0, 0, 1), 9.0, 14.0, 16) for s in (-1, 1)]
    shoes = [_box(SHOE_X - sx / 2, SHOE_X + sx / 2, s * SHOE_Y - sy / 2, s * SHOE_Y + sy / 2, z0, z0 + sz)
             for s in (-1, 1)]
    leads = [_cyl((SHOE_X + sx / 2 + 3.0, s * SHOE_Y, z0 + sz + 20.0), (0, 0, 1), 2.5, 26.0, 12) for s in (-1, 1)]
    return {"gnd rod": (rod, SS), "gnd crossbar": (bar, OURS), "gnd springs": (springs[0].merge(springs[1]), SS_DK),
            "gnd shoes (copper-graphite)": (shoes[0].merge(shoes[1]), CU_GRAPHITE),
            "gnd shoe leads": (leads[0].merge(leads[1]), GRN_YEL)}


def shoes_group(mir) -> str:
    return f"{mir.g} gnd shoes"


def add_shoes(sc, mir, down: float = 0.0):
    """The bracket, actuator and the two shoes on a MiR250 (alloy_atomize.Mir): the fixed parts in its own group, the
    shoes in a child group, `down` 0 = lifted (driving), 1 = on the floor plate."""
    for name, (mesh, col) in shoe_fixed_meshes().items():
        sc.add(f"{mir.g}/{name}", mesh, col, mir.g, specular=0.3)
    grp = shoes_group(mir)
    for name, (mesh, col) in shoe_moving_meshes().items():
        sc.add(f"{grp}/{name}", mesh, col, grp, specular=0.2)
    sc.parent[grp] = mir.g
    set_shoes(sc, mir, down)


def set_shoes(sc, mir, down: float):
    from scene import T
    sc.gmat[shoes_group(mir)] = T((0.0, 0.0, LIFT * (1.0 - float(down))))


def shoes_anim(sc, mir, d0: float, d1: float):
    def up(u):
        set_shoes(sc, mir, d0 + (d1 - d0) * u)
    return up


def lamp_name(mir) -> str:
    return f"{mir.g}/gnd bond lamp"


def add_lamp(sc, mir, state: str = "amber"):
    """The bond lamp: a dome on a short stalk on the cabinet's front face, amber until the two checks pass."""
    x, y, z = LAMP_AT                               # on the face (x 362): the stalk and the dome stand out along +x
    stalk = _cyl((x + 7.0, y, z), (1, 0, 0), 8.0, 14.0, 16)
    dome = pv.Sphere(radius=22.0, center=(x + 26.0, y, z), theta_resolution=24, phi_resolution=16).triangulate()
    sc.add(f"{mir.g}/gnd lamp stalk", stalk, SS_DK, mir.g)
    sc.add(lamp_name(mir), dome, LAMP[state], mir.g, ambient=0.75, specular=0.2)


def lamp(sc, mir, state: str):
    sc.color[lamp_name(mir)] = LAMP[state]


def shoe_points(spot) -> list[np.ndarray]:
    """The two shoes' centres on the floor for a MiR250 at spot (x, y, yaw deg), model frame."""
    x, y, yaw = spot
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    return [np.array([x + SHOE_X * c - k * SHOE_Y * s, y + SHOE_X * s + k * SHOE_Y * c, 0.0]) for k in (-1, 1)]


# ---------------------------------------------------------------------------------------------------- the floor plates
# Where MiR250s park to work at the atomizer, model frame (x, y, yaw): every clip's and chapter's spot, so the plates
# cover them all. Repeated here, not imported, so that lab.py can use this module without building a scene.
ATOMIZER_SPOTS = {
    "dock": (288.0, -530.0, 0.0),        # setup_lab.DOCK_Y / alloy_atomize.END_POSE / alloy_print.START (world y -2230)
    "front": (150.0, -760.0, 0.0),       # atom_base.PARK (atom_bn, atom_crucible MiR 1, the clips' default)
    "front_left": (-560.0, -620.0, 0.0),
    "left": (-760.0, -40.0, 90.0),       # beside the chamber's door, facing it
    "right": (760.0, -560.0, 0.0),       # atom_plate, atom_sleeve, atom_vacuum's MiR 1
    "latch": (650.0, -560.0, 0.0),       # atom_latch.A_AT
    "lid": (-500.0, -600.0, 0.0),        # atom_latch.B_AT
    "vacuum": (-520.0, -1150.0, 0.0),    # atom_vacuum.MIR_PARK
    "plate_mir2": (-600.0, -1250.0, 0.0),        # atom_plate's MiR 2
    "brush": (-700.0, -350.0, -45.0),    # atom_container.A_LEFT
    "fork": (800.0, -480.0, 90.0),       # atom_container.B_FRONT
    "cams": (1150.0, -950.0, 90.0),      # atom_cameras' MiR 2, parked out of the views
    "crucible_left": (-960.0, -40.0, 90.0),      # atom_crucible.MIR2_AT
    "load": (150.0, -750.0, 0.0),        # alloy_atomize: x_load, y_park
    "wait": (1150.0, -750.0, 0.0),       # alloy_atomize: x_wait
    "container": (-32.0, -950.0, 0.0),   # alloy_atomize: x_cont, y_cont
}
# Spots whose MiR250 stands where the model's own vacuum pump stands (repowder/model.py vacuum_pump: x -880..-420,
# y 120..340, on the floor): the lab's plates leave them out (lab._repowder, fixture_meshes). The clips that use them
# don't check a parked MiR against the machine (collide.py checks movers only while they move), so this is a layout
# fault of those clips, not a plate's. "fork" (atom_container's MiR 2, x 510..1090, y -880..-80 at yaw 90) stands
# where chapter 3 (alloy_print.py) puts the sieve wash module's stand, in front of the utility cabinet: left out too.
NOT_IN_LAB = ("left", "crucible_left", "fork")
# the plate round a spot's two shoes: +-PLATE_ALONG along the MiR's heading, +-PLATE_ACROSS across it. The MiR250 parks
# to +-60-85 mm without a marker (MiR's figure, quoted in PR #318's round 4), the shoes are +-70 mm apart, and a margin
GUARD = 85.0
PLATE_ALONG = SHOE[0] / 2 + GUARD + 40.0           # 148 mm
PLATE_ACROSS = SHOE_Y + SHOE[1] / 2 + GUARD + 40.0  # 214 mm
GROUND_BAR = (-1000.0, 60.0)                         # atom_vacuum.GROUND_BAR: the area's building ground point (assumed)


def plate_rect(spot) -> tuple:
    """The plate under a spot's shoes, axis-aligned: (x0, x1, y0, y1). A spot at a slant (atom_container's brushing
    spot, -45 deg) gets the square round its turned plate."""
    a, b = shoe_points(spot)
    c = (a + b) / 2
    t = math.radians(spot[2])
    ex = PLATE_ALONG * abs(math.cos(t)) + PLATE_ACROSS * abs(math.sin(t))
    ey = PLATE_ALONG * abs(math.sin(t)) + PLATE_ACROSS * abs(math.cos(t))
    return (c[0] - ex, c[0] + ex, c[1] - ey, c[1] + ey)


STEP = 10.0                                         # mm: the grid the plates' outline is worked out on


def plate_rects(spots=None) -> list[tuple]:
    """The plates for the named spots (or (x, y, yaw) tuples; default every ATOMIZER_SPOT): the union of each spot's
    rectangle, cut into non-overlapping rectangles (plates laid side by side, no two drawn in the same place), each
    (x0, x1, y0, y1, group) where `group` numbers the joined areas (one bonding lead pair each)."""
    from scipy import ndimage
    spots = list(ATOMIZER_SPOTS) if spots is None else list(spots)
    rects = [plate_rect(ATOMIZER_SPOTS[s] if isinstance(s, str) else s) for s in spots]
    x0 = math.floor(min(r[0] for r in rects) / STEP) * STEP
    y0 = math.floor(min(r[2] for r in rects) / STEP) * STEP
    nx = int(math.ceil((max(r[1] for r in rects) - x0) / STEP))
    ny = int(math.ceil((max(r[3] for r in rects) - y0) / STEP))
    grid = np.zeros((ny, nx), bool)
    for r in rects:
        i0, i1 = int(round((r[2] - y0) / STEP)), int(round((r[3] - y0) / STEP))
        j0, j1 = int(round((r[0] - x0) / STEP)), int(round((r[1] - x0) / STEP))
        grid[i0:i1, j0:j1] = True
    labels, _ = ndimage.label(grid)
    out, used = [], np.zeros_like(grid)
    for i in range(ny):                           # greedy: the longest run in a row, grown down while it stays full
        j = 0
        while j < nx:
            if not grid[i, j] or used[i, j]:
                j += 1
                continue
            j1 = j
            while j1 < nx and grid[i, j1] and not used[i, j1]:
                j1 += 1
            i1 = i + 1
            while i1 < ny and grid[i1, j:j1].all() and not used[i1, j:j1].any():
                i1 += 1
            used[i:i1, j:j1] = True
            out.append((x0 + j * STEP, x0 + j1 * STEP, y0 + i * STEP, y0 + i1 * STEP, int(labels[i, j])))
            j = j1
    return out


def _terminal_at(rects, group, bar) -> np.ndarray:
    """Where a joined area's bonding terminal sits: the corner of its pieces nearest the ground bar, 30 mm in."""
    gb = np.asarray(bar, float)
    best = None
    for x0, x1, y0, y1, gr in rects:
        if gr != group:
            continue
        for cx, cy in ((x0, y0), (x0, y1), (x1, y0), (x1, y1)):
            d = float(np.hypot(cx - gb[0], cy - gb[1]))
            if best is None or d < best[0]:
                best = (d, np.array([cx + (30.0 if cx == x0 else -30.0), cy + (30.0 if cy == y0 else -30.0)]))
    return best[1]


def plate_meshes(rects, prefix: str = "gnd plate", bar=GROUND_BAR) -> dict:
    """The plates: 304 stainless, 2 mm proud of the floor with a stepped (chamfered) edge, laid side by side; one
    recessed green-yellow terminal per joined area, at its corner nearest the ground bar. {name: (mesh, colour)},
    model frame. Everything stays under 6 mm, so collide.py's movers check counts it as a floor marking (a MiR rolls
    onto it)."""
    tops, rims = [], []
    for x0, x1, y0, y1, _ in rects:
        tops.append(_box(x0 + 2.0, x1 - 2.0, y0 + 2.0, y1 - 2.0, -1.0, PLATE_TOP))
        rims.append(_box(x0, x1, y0, y1, -1.0, PLATE_TOP - 1.0))
    out = {prefix: (tops[0].merge(tops[1:] + rims) if len(tops) > 1 else tops[0].merge(rims[0]), SS)}
    terms = []
    for gr in sorted({r[4] for r in rects}):
        c = _terminal_at(rects, gr, bar)
        terms.append(_box(c[0] - 14.0, c[0] + 14.0, c[1] - 9.0, c[1] + 9.0, PLATE_TOP - 0.5, PLATE_TOP + 1.5))
    out[f"{prefix} terminals"] = (terms[0].merge(terms[1:]) if len(terms) > 1 else terms[0], GRN_YEL)
    return out


def channel_meshes(rects, bar=GROUND_BAR, prefix: str = "gnd channel") -> dict:
    """Each joined area's bonding leads, in a flush floor channel (a 40 mm cover strip, 3 mm proud) run square from its
    terminal to the ground bar: {name: (mesh, colour)}, model frame. Two leads in each channel, so the station's monitor
    reads the plate 4-wire."""
    out = {}
    gb = np.array(bar, float)
    parts = []
    for gr in sorted({r[4] for r in rects}):
        p = _terminal_at(rects, gr, bar)
        for a, b in ((p, np.array([p[0], gb[1]])), (np.array([p[0], gb[1]]), gb)):
            if np.linalg.norm(b - a) < 1.0:
                continue
            xa, xb_ = sorted((a[0], b[0]))
            ya, yb = sorted((a[1], b[1]))
            parts.append(_box(xa - 20.0, xb_ + 20.0, ya - 20.0, yb + 20.0, -1.0, 3.0))
    if parts:
        out[prefix] = (parts[0].merge(parts[1:]) if len(parts) > 1 else parts[0], GRN_YEL)
    return out


def bar_meshes(bar=GROUND_BAR) -> dict:
    """The area's ground bar (as atom_vacuum draws it: a copper bar on two standoffs, 120 x 30 mm, 40 mm tall)."""
    x, y = bar
    return {"gnd bar": (_box(x - 60, x + 60, y - 15, y + 15, 0, 40), (0.55, 0.45, 0.25))}


def lab_spots() -> list[str]:
    return [k for k in ATOMIZER_SPOTS if k not in NOT_IN_LAB]


def fixture_meshes() -> dict:
    """For lab._repowder(): the plates of every ATOMIZER_SPOT but NOT_IN_LAB's (joined where they overlap), their
    channels, the ground bar. Model frame; flat except the bar."""
    rects = plate_rects(lab_spots())
    out = {}
    out.update(plate_meshes(rects))
    out.update(channel_meshes(rects))
    out.update(bar_meshes())
    return out


if __name__ == "__main__":
    for r in plate_rects():
        print("plate", [round(v) for v in r[:4]], "group", r[4], f"{(r[1] - r[0]):.0f} x {(r[3] - r[2]):.0f} mm")
