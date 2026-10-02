"""Pick-up shelf behind the PiPER at spot D (#229): lay out the parts, size them, write the cut list, export.

    python reach.py            # reach-results.json: where picks are comfortable (run first)
    python build.py            # shelf-results.json, cut-list.md, models/*.stl, shelf.glb

Coordinates are the dome model's: x along the wall, y from the room (-y) to the wall (+y), z up
from the table top, metres. The STLs are in the shelf's own frame instead, with the origin on the
arm's J1 axis at the top of the plate the arm stands on, so every number in them is a distance
from the arm.
"""

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh
from scipy.optimize import least_squares
from trimesh.creation import box

HERE = Path(__file__).parent
DOME = HERE.parent / "dome"
sys.path[:0] = [str(DOME), str(HERE.parent)]
_spec = importlib.util.spec_from_file_location("dome_build", DOME / "build.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
P = D.P                                     # the dome's part models
from piper_fk import Piper  # noqa: E402

IN = 0.0254
T = 0.703 * IN                              # 3/4 in plywood, actual (the dome and hutch use the same)
REACH = json.loads((HERE / "reach-results.json").read_text())

# ------------------------------------------------------------------ site
TABLE = D.TABLE                             # spot D, two 680 x 1290 mm tables, top at z = 0
WALL_Y = TABLE["y"] / 2                     # back edge of the tables, against room 158's wall
# The dome (../dome) stands on the table round everything; its back bottom rail runs along the wall.
RAIL_Y = D.SPAN["y"] / 2 - P.PIPE_OD / 2    # inside face of that rail's pipe
RAIL_GAP = 0.005                            # fence to rail
# The arm's base: the 4 x 4 ft half sheet in the photo. 48 in will not drop between the dome's corner
# elbows (1217 mm apart inside), so it is trimmed to 47 1/2 in across.
BASE = dict(x=47.5 * IN, y=48 * IN)
HUTCH_RAIL = (45.5 * IN + 2 * P.ELBOW_STOP) / 2 - P.PIPE_OD / 2   # the same rail on the deck, from its centre

# ------------------------------------------------------------------ shelf, in the arm's frame
# front: J1 axis to the front edge. The parked arm sweeps 317 mm round J1 if it turns while folded,
# so 350 mm leaves 33 mm. depth: front edge to the fence. top: shelf surface above the arm's plate.
SHELF = dict(front=0.350, depth=0.200, length=0.800, top=0.075, lip=0.040)
LEG_H = SHELF["top"] - T                    # 57 mm
PLATE_T = 0.006                             # nest plate, 1/4 in hardboard or acrylic
N_LEGS = 4

# The arm faces -x: its cable, its parked elbow and J1's dead wedge all point along the wall (+x),
# and the shelf is off its side, at J1 = -90 degrees.
ARM_YAW = np.pi
Y_J1 = RAIL_Y - RAIL_GAP - T - SHELF["depth"] - SHELF["front"]
X_J1 = 0.0
PT = T                                      # top of the arm's plate

# Items: 20 mL scintillation vials in front, 50 mL self-standing tubes behind. y is from the front edge.
VIAL = dict(d=0.028, h=0.061, cap=0.013, color="#d5e6ec", cap_color="#2b2d31")
TUBE = dict(d=0.030, h=0.115, cap=0.016, color="#eef1f2", cap_color="#2a78d6")
ROWS = [dict(name="vial", item=VIAL, y=0.040, xs=np.round(np.arange(-0.36, 0.3601, 0.09), 3)),
        dict(name="tube", item=TUBE, y=0.155, xs=np.round(np.arange(-0.20, 0.2001, 0.10), 3))]
POCKET_CLEAR = 0.001                        # pocket = item diameter + 1 mm
CHAMFER = 0.0015                            # 45 degree lead-in on every pocket
PLATE_PINS = [(-0.375, 0.100), (0.375, 0.100)]   # 6 mm pins: round hole on the left, slot on the right
PICK = dict(row=0, x=-0.18, tip_above_plate=0.020, pitch=-45.0)   # the pose in the 3D view

KERF = 0.0032


def T4(R=np.eye(3), t=(0, 0, 0)):
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = t
    return M


SHELF_TO_WORLD = T4(t=(X_J1, Y_J1, PT))


@dataclass
class Part:
    name: str
    mesh: trimesh.Trimesh          # shelf frame
    color: str
    cut: tuple = None              # (length along grain, width, thickness) for the cut list
    tags: set = field(default_factory=set)

    @property
    def world(self):
        return self.mesh.copy().apply_transform(SHELF_TO_WORLD)


def _box(lo, hi):
    m = box(np.subtract(hi, lo))
    m.apply_translation(np.add(lo, hi) / 2)
    return m


def _cyl(r, z0, z1, x=0.0, y=0.0, sections=40):
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=sections)
    c.apply_translation((x, y, (z0 + z1) / 2))
    return c


def _cone(r0, r1, z0, z1, x, y, sections=40):
    """Frustum from radius r0 at z0 to r1 at z1 (for the pocket chamfers)."""
    t = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    ring = lambda r, z: np.c_[x + r * np.cos(t), y + r * np.sin(t), np.full(sections, z)]  # noqa: E731
    return trimesh.convex.convex_hull(np.vstack([ring(r0, z0), ring(r1, z1)]))


def _minus(a, cutters):
    return trimesh.boolean.difference([a, *cutters], engine="manifold") if cutters else a


# ------------------------------------------------------------------ parts
def leg_x():
    a = SHELF["length"] / 2 - T / 2
    return np.linspace(-a, a, N_LEGS)


def parts():
    L, F, Dp, top = SHELF["length"], SHELF["front"], SHELF["depth"], SHELF["top"]
    out = []
    pin_holes = [_cyl(0.003, top - 0.012, top + 0.001, x, F + y, 24) for x, y in PLATE_PINS]
    out.append(Part("shelf-top", _minus(_box((-L / 2, F, top - T), (L / 2, F + Dp, top)), pin_holes), "#e3d2ad",
                    (L, Dp, T), {"ply"}))
    for i, x in enumerate(leg_x()):
        dowel = [_cyl(IN / 8, -0.001, 0.020, x, F + Dp / 2, 24)] if i in (0, N_LEGS - 1) else []
        out.append(Part(f"leg-{i + 1}", _minus(_box((x - T / 2, F, 0), (x + T / 2, F + Dp, LEG_H)), dowel),
                        "#dcc8a0", (Dp, LEG_H, T), {"ply", "leg"}))
    out.append(Part("fence", _box((-L / 2, F + Dp, 0), (L / 2, F + Dp + T, top + SHELF["lip"])), "#d9c49b",
                    (L, top + SHELF["lip"], T), {"ply"}))
    # nest plate: through pockets with a chamfered lead-in, a round hole and a slot for the pins
    plate = _box((-L / 2 + 0.002, F, top), (L / 2 - 0.002, F + Dp - 0.002, top + PLATE_T))
    cuts = []
    for row in ROWS:
        r = (row["item"]["d"] + POCKET_CLEAR) / 2
        for x in row["xs"]:
            cuts.append(_cyl(r, top - 0.001, top + PLATE_T + 0.001, x, F + row["y"]))
            cuts.append(_cone(r, r + CHAMFER + 0.001, top + PLATE_T - CHAMFER, top + PLATE_T + 0.001, x, F + row["y"]))
    (xa, ya), (xb, yb) = PLATE_PINS
    cuts.append(_cyl(0.003, top - 0.001, top + PLATE_T + 0.001, xa, F + ya, 24))
    slot = trimesh.util.concatenate([_cyl(0.003, top - 0.001, top + PLATE_T + 0.001, xb + dx, F + yb, 24)
                                     for dx in np.linspace(-0.004, 0.004, 9)])
    cuts.append(trimesh.convex.convex_hull(slot.vertices))
    out.append(Part("nest-plate", _minus(plate, cuts), "#f4f1ea", (L - 0.004, Dp - 0.002, PLATE_T), {"plate"}))
    # pins: two 6 mm locating the plate, two 1/4 in dowels through the end legs into the arm's plate
    for x, y in PLATE_PINS:
        out.append(Part("pin-6mm", _cyl(0.003, top - 0.012, top + PLATE_T - 0.001, x, F + y, 24), "#9aa0a6",
                        tags={"pin"}))
    for x in leg_x()[[0, -1]]:
        out.append(Part("dowel-1-4in", _cyl(IN / 8, -0.015, 0.017, x, F + Dp / 2, 24), "#9aa0a6", tags={"pin"}))
    # corner braces: 1 1/2 in steel, inside each end leg, into the arm's plate
    for x, s in ((leg_x()[0], 1), (leg_x()[-1], -1)):
        for y in (F + 0.05, F + Dp - 0.05):
            x0 = x + s * T / 2
            up = _box((min(x0, x0 + s * 0.002), y - 0.008, 0), (max(x0, x0 + s * 0.002), y + 0.008, 0.038))
            flat = _box((min(x0, x0 + s * 0.038), y - 0.008, 0), (max(x0, x0 + s * 0.038), y + 0.008, 0.002))
            out.append(Part("corner-brace", trimesh.util.concatenate([up, flat]), "#8c9196", tags={"brace"}))
    return out


def items():
    out = []
    for row in ROWS:
        it = row["item"]
        for x in row["xs"]:
            y, z0 = SHELF["front"] + row["y"], SHELF["top"]
            out.append(Part(row["name"], _cyl(it["d"] / 2, z0, z0 + it["h"] - it["cap"], x, y), it["color"],
                            tags={"item"}))
            out.append(Part(row["name"] + "-cap", _cyl(it["d"] / 2 + 0.0005, z0 + it["h"] - it["cap"], z0 + it["h"], x, y),
                            it["cap_color"], tags={"item"}))
    return out


def base_plate():
    """The arm's plate, back edge flush with the back of the fence, in world coordinates."""
    y1 = RAIL_Y - RAIL_GAP
    m = _box((-BASE["x"] / 2, y1 - BASE["y"], 0), (BASE["x"] / 2, y1, PT))
    return m


# ------------------------------------------------------------------ arm
def arm_base():
    return T4(t=(X_J1, Y_J1, PT)) @ trimesh.transformations.rotation_matrix(ARM_YAW, (0, 0, 1))


def arm_meshes(piper, q, keep=None, grip=0.015):
    D.arm_base = arm_base
    return D.arm_meshes(piper, q=q, grip=grip, keep=keep)


def ik(piper, target_world, pitch_deg):
    """J1, J2, J3, J5 (J4 = J6 = 0) putting the fingertip on target, pointing away from J1 and
    pitched pitch_deg below horizontal. Seeded from the reach grid, refined by least squares."""
    B = arm_base()
    p = np.linalg.inv(B) @ np.r_[target_world, 1]
    az = np.arctan2(p[1], p[0])
    want = np.array([np.cos(az) * np.cos(np.radians(pitch_deg)), np.sin(az) * np.cos(np.radians(pitch_deg)),
                     np.sin(np.radians(pitch_deg))])
    lim = [piper.limits[f"joint{i}"] for i in range(1, 7)]

    def resid(v):
        q = np.array([v[0], v[1], v[2], 0, v[3], 0])
        Tf = piper.fk(q)["link6"]
        tip = Tf[:3, 3] + Tf[:3, 2] * piper.TIP
        return np.r_[tip - p[:3], 0.2 * (Tf[:3, 2][2] - want[2])]

    best = None
    for j2 in np.radians([60, 90, 120, 150]):
        for j3 in np.radians([-30, -60, -90, -120]):
            v0 = np.array([az, j2, j3, 0.0])
            lo = [lim[0][0], lim[1][0], lim[2][0], lim[4][0]]
            hi = [lim[0][1], lim[1][1], lim[2][1], lim[4][1]]
            s = least_squares(resid, np.clip(v0, np.add(lo, 1e-3), np.subtract(hi, 1e-3)), bounds=(lo, hi))
            if s.cost < 1e-9:
                m = min(min(s.x[i] - lo[i], hi[i] - s.x[i]) for i in range(4))
                if best is None or m > best[1]:
                    best = (s.x, m)
    v = best[0]
    return np.array([v[0], v[1], v[2], 0, v[3], 0]), float(np.degrees(best[1]))


def pick_pose(piper):
    row = ROWS[PICK["row"]]
    tgt = SHELF_TO_WORLD @ np.r_[PICK["x"], SHELF["front"] + row["y"], SHELF["top"] + PLATE_T + PICK["tip_above_plate"], 1]
    return ik(piper, tgt[:3], PICK["pitch"])


# ------------------------------------------------------------------ numbers
def layout_numbers():
    j1lim = REACH["j1_limit_deg"]
    rows = []
    for row in ROWS:
        y = SHELF["front"] + row["y"]
        r = np.hypot(row["xs"], y)
        # this layout: shelf at J1 = -90; the room-facing layout would put it at 180
        j1 = np.degrees(np.arctan2(y, np.abs(row["xs"]))) - 180
        j1_room = 180 - np.degrees(np.arctan2(np.abs(row["xs"]), y))
        rows.append(dict(name=row["name"], y_from_j1=round(y, 3), n=len(row["xs"]), x_span=[float(row["xs"].min()),
                         float(row["xs"].max())], r=[round(float(r.min()), 3), round(float(r.max()), 3)],
                         j1_deg=[round(float(np.abs(j1).min()), 1), round(float(np.abs(j1).max()), 1)],
                         room_facing_j1_deg=[round(float(j1_room.min()), 1), round(float(j1_room.max()), 1)],
                         room_facing_out_of_reach=int((j1_room > j1lim).sum()),
                         room_facing_past_margin=int((j1_room > j1lim - REACH["margin_deg"]).sum())))
    band = REACH["comfortable_band_by_shelf_height_m"][f"{SHELF['top']:.3f}"]
    # along the front row, the stretch the room-facing arm cannot reach at all (J1 past its stop)
    y0 = SHELF["front"] + ROWS[0]["y"]
    dead = y0 * np.tan(np.radians(180 - j1lim))
    dead_m = y0 * np.tan(np.radians(180 - j1lim + REACH["margin_deg"]))
    comfy = item_comfort()
    return dict(j1_to_wall=round(WALL_Y - Y_J1, 4), j1_to_rail=round(RAIL_Y - Y_J1, 4),
                j1_to_fence_back=round(SHELF["front"] + SHELF["depth"] + T, 4),
                hutch_fence_to_rail_with_arm_at_deck_centre=round(HUTCH_RAIL - (SHELF["front"] + SHELF["depth"] + T), 4),
                items_comfortable=comfy, j1_to_front_edge=SHELF["front"],
                j1_to_fence=round(SHELF["front"] + SHELF["depth"], 4), shelf_top_above_plate=SHELF["top"],
                leg_height=round(LEG_H, 4), length=SHELF["length"], depth=SHELF["depth"],
                leg_x=[round(float(x), 4) for x in leg_x()], span_between_legs=round(float(np.diff(leg_x())[0] - T), 4),
                parked_sweep_radius=REACH["rest_pose"]["swept_radius_m"],
                clearance_to_parked_sweep=round(SHELF["front"] - REACH["rest_pose"]["swept_radius_m"], 4),
                comfortable_band=band, rows=rows,
                room_facing_dead_half_width_front_row=round(float(dead), 3),
                room_facing_dead_half_width_front_row_with_margin=round(float(dead_m), 3),
                arm_on_table_y=round(Y_J1, 4), base_centre_y=round(RAIL_Y - RAIL_GAP - BASE["y"] / 2, 4))


def item_comfort():
    """For every pocket: is a 45 +/- 15 degree pick comfortable at every fingertip height from 10 to
    60 mm above the nest plate? Read straight off reach.py's map."""
    d = np.load(HERE / "reach-map.npz")
    feas, R, Z, Pd = d["feas"], d["r_bins"], d["z_bins"], d["pitches"]
    sel = (Pd >= REACH["approach_pitch_deg"][0]) & (Pd <= REACH["approach_pitch_deg"][1])
    comf = feas[sel].all(axis=0)
    zc = (Z[:-1] + Z[1:]) / 2
    lo, hi = REACH["grip_above_shelf_m"]
    base = SHELF["top"] + PLATE_T
    zs = (zc >= base + lo - 0.005) & (zc <= base + hi + 0.005)
    out = {}
    for row in ROWS:
        r = np.hypot(row["xs"], SHELF["front"] + row["y"])
        i = np.digitize(r, R) - 1
        ok = comf[i][:, zs].all(axis=1)
        out[row["name"]] = f"{int(ok.sum())}/{len(ok)}"
    return out


def stiffness():
    """Beam estimates: sag between legs under the items plus a press from the arm, and the shove
    it takes to slide an unfixed shelf. Same plywood values as the hutch (E along the grain)."""
    E = 7.0e9
    b, t = SHELF["depth"], T
    EI = E * b * t ** 3 / 12
    load_kg, press = 3.0, 20.0                   # items on the shelf; the arm pushing an item into a pocket
    w = load_kg * 9.81 / SHELF["length"]

    def sag(span):
        return 5 * w * span ** 4 / (384 * EI) + press * span ** 3 / (48 * EI)

    span4 = float(np.diff(leg_x())[0])
    span2 = float(leg_x()[-1] - leg_x()[0])
    shelf_kg = 600 * T * (SHELF["length"] * SHELF["depth"] + N_LEGS * SHELF["depth"] * LEG_H
                          + SHELF["length"] * (SHELF["top"] + SHELF["lip"]))
    mu = 0.3
    # humidity: in-plane plywood movement ~0.01-0.02 % per 1 % moisture content; 3 % MC swing season to season
    hyg = 0.00015 * 3 * (SHELF["front"] + SHELF["depth"])
    return dict(E_Pa=E, EI_Nm2=round(EI, 1), items_kg=load_kg, press_N=press,
                span_4_legs_m=round(span4, 3), sag_4_legs_mm=round(sag(span4) * 1000, 3),
                stiffness_4_legs_N_per_mm=round(press / (press * span4 ** 3 / (48 * EI)) / 1000, 0),
                span_2_legs_m=round(span2, 3), sag_2_legs_mm=round(sag(span2) * 1000, 3),
                stiffness_2_legs_N_per_mm=round(press / (press * span2 ** 3 / (48 * EI)) / 1000, 0),
                creep_factor=2.0, sag_4_legs_long_term_mm=round((sag(span4) + 5 * w * span4 ** 4 / (384 * EI)) * 1000, 3),
                shelf_kg=round(shelf_kg, 2), friction_mu=mu,
                slide_force_unfixed_N=round(mu * (shelf_kg + load_kg) * 9.81, 1),
                humidity_shift_mm=round(hyg * 1000, 2), target_mm=0.1)


# ------------------------------------------------------------------ cut list
def fmt(m):
    q = round(m / IN * 8) / 8
    w, f = int(q), q - int(q)
    frac = {0: "", 0.125: " 1/8", 0.25: " 1/4", 0.375: " 3/8", 0.5: " 1/2", 0.625: " 5/8", 0.75: " 3/4", 0.875: " 7/8"}[f]
    return f"{m * 1000:.0f} mm ({w}{frac} in)"


def write_cut_list(path, nums, stiff):
    L, Dp = SHELF["length"], SHELF["depth"]
    fence_h = SHELF["top"] + SHELF["lip"]
    strip = (Dp + fence_h + KERF, L + KERF + Dp)      # (width, length) of the plywood the shelf needs
    assert N_LEGS * (LEG_H + KERF) <= strip[0]
    n_vial, n_tube = len(ROWS[0]["xs"]), len(ROWS[1]["xs"])
    lines = [
        "# Pick-up shelf: cut list", "",
        "Generated by `build.py`. Plywood is 3/4 in, 17.9 mm (0.703 in) actual. Lengths run along the face grain.",
        "Every distance in the notes is from the arm's J1 axis (the centre of its base), measured square to the wall.",
        "", "## Plywood", "",
        "| Part | Length (along grain) | Width | Qty | Notes |", "|---|---|---|---|---|",
        f"| Shelf top | {fmt(L)} | {fmt(Dp)} | 1 | 2 × Ø6 mm holes 12 mm deep for the plate pins, {PLATE_PINS[1][0] * 1000:.0f} mm "
        f"either side of centre, {PLATE_PINS[0][1] * 1000:.0f} mm from the front edge |",
        f"| Leg | {fmt(Dp)} | {fmt(LEG_H)} | {N_LEGS} | stood on edge, square to the wall, centres at "
        f"{', '.join(f'{x * 1000:+.0f}' for x in leg_x())} mm along the shelf; the two end legs get a Ø1/4 in hole "
        "20 mm deep up into the bottom edge, on centre |",
        f"| Fence | {fmt(L)} | {fmt(fence_h)} | 1 | behind the top and legs, standing on the arm's plate; stands "
        f"{SHELF['lip'] * 1000:.0f} mm proud of the shelf |",
        "", f"All six parts come out of one {strip[0] * 1000:.0f} × {strip[1] * 1000:.0f} mm strip: the top and the fence "
        "side by side along it, and the four legs crosscut from the end. Any offcut that size works.", "",
        "## Nest plate", "",
        "| Part | Size | Qty | Notes |", "|---|---|---|---|",
        f"| Nest plate | {fmt(L - 0.004)} × {fmt(Dp - 0.002)}, 1/4 in (6 mm) | 1 | hardboard, MDF or acrylic; laser-cut or "
        "drilled with Forstner bits |",
        f"| — vial pockets | Ø{(VIAL['d'] + POCKET_CLEAR) * 1000:.0f} mm through | {n_vial} | "
        f"{ROWS[0]['y'] * 1000:.0f} mm from the front edge ({nums['rows'][0]['y_from_j1'] * 1000:.0f} mm from J1), "
        f"every {np.diff(ROWS[0]['xs'])[0] * 1000:.0f} mm from {ROWS[0]['xs'][0] * 1000:+.0f} to {ROWS[0]['xs'][-1] * 1000:+.0f} mm |",
        f"| — tube pockets | Ø{(TUBE['d'] + POCKET_CLEAR) * 1000:.0f} mm through | {n_tube} | "
        f"{ROWS[1]['y'] * 1000:.0f} mm from the front edge ({nums['rows'][1]['y_from_j1'] * 1000:.0f} mm from J1), "
        f"every {np.diff(ROWS[1]['xs'])[0] * 1000:.0f} mm from {ROWS[1]['xs'][0] * 1000:+.0f} to {ROWS[1]['xs'][-1] * 1000:+.0f} mm |",
        f"| — lead-in | {CHAMFER * 1000:.1f} mm × 45° | every pocket | a countersink bit, by hand |",
        "| — pin holes | Ø6 mm round on the left, 6 × 14 mm slot on the right | 1 + 1 | the slot runs along the shelf |",
        "", "## Hardware", "",
        "| Item | Qty | Where |", "|---|---|---|",
        "| Wood glue (PVA) | a little | legs to the top, fence to the legs and top |",
        "| #8 × 1 1/4 in wood screws | 16 | 2 down through the top into each leg; 2 through the fence into each leg |",
        "| 6 mm × 20 mm steel dowel pins | 2 | press-fit in the shelf top; locate the nest plate |",
        "| 1/4 in × 1 1/4 in steel dowel pins | 2 | up into the end legs, down into the arm's plate; locate the shelf |",
        "| 1 1/2 in steel corner braces, with #8 × 5/8 in screws | 4 | inside the end legs, into the arm's plate; hold the shelf down |",
        "| AprilTag or ArUco markers, printed | 2 | optional, one at each end of the plate, for the wrist camera |",
        "",
        "## Drilling the arm's plate",
        "",
        f"Two Ø1/4 in holes 15 mm deep for the dowels (the plate is 18 mm, so not through), at {leg_x()[0] * 1000:+.0f} and {leg_x()[-1] * 1000:+.0f} mm "
        f"along the shelf and {(SHELF['front'] + Dp / 2) * 1000:.0f} mm from J1 toward the wall. Rather than measuring "
        "them out, mark them from the legs: drill the legs first, drop a 1/4 in dowel centre into each hole and press the "
        "shelf down where it goes. The two sets then line up whatever the error in marking out.",
        "",
    ]
    path.write_text("\n".join(lines))


# ------------------------------------------------------------------ export
def export(piper, q):
    mdir = HERE / "models"
    mdir.mkdir(exist_ok=True)
    mm = np.diag([1000, 1000, 1000, 1])
    ps = parts()
    done = set()
    for p in ps:
        name = "leg" if p.name.startswith("leg-") else p.name
        if name in done or "brace" in p.tags or "pin" in p.tags:
            continue
        done.add(name)
        p.mesh.copy().apply_transform(mm).export(mdir / f"{name}.stl")
    trimesh.util.concatenate([p.mesh for p in ps]).apply_transform(mm).export(mdir / "shelf.stl")

    scene = trimesh.Scene()

    def add(mesh, rgb, name):
        m = mesh.copy()
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=[*rgb, 1.0], metallicFactor=0.0, roughnessFactor=0.8, doubleSided=True))
        scene.add_geometry(m, node_name=name)

    hexrgb = lambda h: [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]  # noqa: E731
    for y0, y1 in ((-TABLE["y"] / 2, -0.0015), (0.0015, TABLE["y"] / 2)):
        t = box((TABLE["x"], y1 - y0, 0.03))
        t.apply_translation((0, (y0 + y1) / 2, -0.015))
        add(t, hexrgb("#26272a"), f"table-{y0:.2f}")
    add(base_plate(), hexrgb("#e9dcc0"), "arm-plate")
    for i, p in enumerate(ps + items()):
        add(p.world, hexrgb(p.color), f"{p.name}-{i}")
    for i, it in enumerate(dome_frame()):
        add(it.world, hexrgb(it.part.color), f"dome-{it.part.name}-{i}")
    for j, (link, m, c) in enumerate(arm_meshes(piper, q, keep=0.25)):
        add(m, list(c), f"piper-{link}-{j}")
    scene.export(HERE / "shelf.glb")


def dome_frame():
    """The dome's PVC frame from ../dome, without its cloth, base or screws."""
    return [it for it in D.layout() if it.tags & {"pipe", "elbow"}]


if __name__ == "__main__":
    piper = Piper()
    q, margin = pick_pose(piper)
    nums, stiff = layout_numbers(), stiffness()
    res = dict(layout_m=nums, stiffness=stiff, pick_pose_deg=[round(float(v), 1) for v in np.degrees(q)],
               pick_pose_min_margin_deg=round(margin, 1), pick=PICK)
    (HERE / "shelf-results.json").write_text(json.dumps(res, indent=1) + "\n")
    write_cut_list(HERE / "cut-list.md", nums, stiff)
    export(piper, q)
    print(json.dumps(res, indent=1))
    for f in sorted((HERE / "models").iterdir()) + [HERE / "shelf.glb"]:
        print(f.name, f.stat().st_size // 1024, "kB")
