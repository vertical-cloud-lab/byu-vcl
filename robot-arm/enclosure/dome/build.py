"""Spot D enclosure (#229): lay out the parts, write the cut list and export the 3D models.

    python build.py           # cut-list.md, models/*.stl, enclosure.glb

The layout here is also what animate.py renders, so the GIF, the cut list and the exports
cannot drift apart.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh

import parts as P

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from piper_fk import Piper  # noqa: E402

# ------------------------------------------------------------------ site
# Spot D after the second table goes in: two 680 x 1290 mm tables, 1360 x 1290 mm together.
# x runs along the wall, y from the room (-y, front) to the wall (+y, back). Table top at z = 0.
TABLE = dict(x=1.290, y=1.360, t=0.030)

# ------------------------------------------------------------------ frame
# Cut lengths are whole or quarter inches, chosen so the frame sits just inside the table top
# and stands 1.1 m tall. The fitting OD adds half an elbow on every side.
CUT = {"x": 48.0 * P.IN, "y": 50.75 * P.IN, "z": 40.75 * P.IN}
SPAN = {k: v + 2 * P.ELBOW_STOP for k, v in CUT.items()}         # corner-to-corner, on the pipe axes
OUTER = {k: v + P.ELBOW_OD for k, v in SPAN.items()}               # outside of the fittings
Z0 = P.ELBOW_OD / 2                                                # bottom elbows rest on the table
STICK, KERF = 120 * P.IN, 0.003                                    # 10 ft pipe, saw kerf

WRAP = 0.045          # cloth allowance per clamped edge: half the pipe's circumference
CLAMP_AT = (0.15, 0.5, 0.85)

# The arm faces the room: URDF +x (forward) -> world -y.
ARM_YAW = -np.pi / 2
REST = np.zeros(6)
PICK = np.radians([0, 111, -90, 0, 66, 0])

STEPS = [
    "Spot D: two 680 × 1290 mm tables",
    "Plywood base, drilled for the arm",
    "PiPER on, 4 × M5 × 25 screws from below",
    "Base into the middle of the table",
    "Bottom frame: 4 elbows, 4 pipes",
    "Corner posts: 4 × 1035 mm",
    "Top frame: 4 elbows, 4 pipes",
    "Canvas top, snap-clamped to the rails",
    "Back and side walls, clamped",
    "Front flap, clamped at the top only",
    "Roll the flap up to load",
]


def T(R=np.eye(3), t=(0, 0, 0)):
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = t
    return M


def rot_z_to(d, x_hint=None):
    """Right-handed rotation taking +z onto d (and +x onto x_hint, if given)."""
    z = np.asarray(d, float) / np.linalg.norm(d)
    x = np.asarray(x_hint if x_hint is not None else ((1, 0, 0) if abs(z[0]) < 0.9 else (0, 1, 0)), float)
    x = x - z * (x @ z)
    x /= np.linalg.norm(x)
    return np.column_stack([x, np.cross(z, x), z])


@dataclass
class Item:
    part: P.Part
    M: np.ndarray                  # local -> world, assembled position
    step: int                      # step it arrives in
    entry: tuple = (0, 0, 0.4)     # where it flies in from, relative to its place
    window: tuple = (0.0, 1.0)     # part of the step it moves in
    lift: tuple = None             # (offset, step it is lowered in): held off its place until then
    tags: set = field(default_factory=set)

    @property
    def world(self):
        return self.part.mesh.copy().apply_transform(self.M)


# ------------------------------------------------------------------ layout
def corners():
    """Pipe-axis corners: {(sx, sy, sz): xyz}, sz = -1 bottom, +1 top."""
    return {(sx, sy, sz): np.array([sx * SPAN["x"] / 2, sy * SPAN["y"] / 2, Z0 + (sz + 1) / 2 * SPAN["z"]])
            for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)}


def edges():
    """(axis, corner a, corner b) for the 12 frame members; a is the negative end."""
    out = []
    for ax, key in ((0, "x"), (1, "y"), (2, "z")):
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                a, b = [None] * 3, [None] * 3
                o = [i for i in range(3) if i != ax]
                a[o[0]] = b[o[0]] = s1
                a[o[1]] = b[o[1]] = s2
                a[ax], b[ax] = -1, 1
                out.append((key, tuple(a), tuple(b)))
    return out


def elbow_rotation(sx, sy, sz):
    """Legs (+x, +y, +z in the part frame) must point back into the box."""
    D = np.diag([-sx, -sy, -sz]).astype(float)
    if np.linalg.det(D) < 0:          # a reflection: swap two legs instead, the elbow is symmetric
        D = D[:, [1, 0, 2]]
    return D


def layout():
    items = []
    C = corners()
    t = P.PLY["t"]

    # base, arm and screws: bolted up while the base is held off the table, then lowered
    hover = ((0, 0, 0.30), 3)
    items.append(Item(P.plywood_base(), T(t=(0, 0, t)), 1, (0, 0, 0.5), lift=hover, tags={"base"}))
    screw = P.m5_socket_cap()
    for x, y in P.hole_xy():
        items.append(Item(screw, T(t=(x, y, P.CBORE_H)), 2, (0, 0, -0.12), (0.5, 1.0), lift=hover, tags={"screw"}))

    # frame
    elbow = P.formufit_elbow()
    for (sx, sy, sz), c in C.items():
        step = 4 if sz < 0 else 6
        items.append(Item(elbow, T(elbow_rotation(sx, sy, sz), c), step, (0, 0, 0.35), (0, 0.5), tags={"elbow"}))
    pipes = {k: P.pvc_pipe(v) for k, v in CUT.items()}
    for key, a, b in edges():
        pa, pb = C[a], C[b]
        d = (pb - pa) / np.linalg.norm(pb - pa)
        if key == "z":
            step, entry, win = 5, (0, 0, 0.6), (0, 1)
        else:
            step = 4 if a[2] < 0 else 6
            out = np.array([a[0] if key != "x" else 0, a[1] if key != "y" else 0, 0]) * 0.35
            entry, win = tuple(out + (0, 0, 0.25)), (0.4, 1)
        items.append(Item(pipes[key], T(rot_z_to(d), pa + d * P.ELBOW_STOP), step, entry, win,
                          tags={"pipe", key, "top" if a[2] > 0 else "bottom"}))

    # cloth
    r = P.PIPE_OD / 2 + P.CLOTH_T / 2
    X, Y, Z = SPAN["x"] / 2 + r, SPAN["y"] / 2 + r, Z0 + SPAN["z"] + r
    zb = Z0 - P.PIPE_OD / 2
    top = P.canvas_panel(2 * X, 2 * Y, sag=0.012)
    items.append(Item(top, T(t=(0, 0, Z)), 7, (0, 0, 0.5), (0, 0.6), tags={"cloth", "top"}))
    hw = Z - zb
    for side in (-1, 1):
        R = rot_z_to((side, 0, 0), (0, 1, 0))
        items.append(Item(P.canvas_panel(2 * Y, hw), T(R, (side * X, 0, zb + hw / 2)), 8, (side * 0.5, 0, 0), (0, 0.6),
                          tags={"cloth", "wall"}))
    R = rot_z_to((0, 1, 0), (1, 0, 0))
    items.append(Item(P.canvas_panel(2 * X, hw), T(R, (0, Y, zb + hw / 2)), 8, (0, 0.5, 0), (0, 0.6),
                      tags={"cloth", "wall"}))
    R = rot_z_to((0, -1, 0), (1, 0, 0))
    items.append(Item(P.canvas_panel(2 * X, hw), T(R, (0, -Y, zb + hw / 2)), 9, (0, -0.5, 0), (0, 1),
                      tags={"cloth", "flap"}))

    # snap clamps, gap facing into the box
    clamp = P.snap_clamp()
    for key, a, b in edges():
        pa, pb = C[a], C[b]
        is_top, is_front = a[2] > 0 and b[2] > 0, key != "y" and a[1] < 0
        if key == "z":
            step, n = 8, -np.array([a[0], a[1], 0.0])
        elif is_top:
            step = 7 if not is_front else 9
            n = -np.array([a[0] if key != "x" else 0, a[1] if key != "y" else 0, 1.0])
        elif is_front:
            continue                      # the flap is only clamped at the top
        else:
            step, n = 8, -np.array([a[0] if key != "x" else 0, a[1] if key != "y" else 0, 1.0])
        n /= np.linalg.norm(n)
        d = (pb - pa) / np.linalg.norm(pb - pa)
        free = np.linalg.norm(pb - pa) - 2 * P.ELBOW_MOUTH
        for f in CLAMP_AT:
            p = pa + d * (P.ELBOW_MOUTH + f * free)
            win = (0.6, 1) if step != 9 else (0.5, 1)
            items.append(Item(clamp, T(rot_z_to(d, n), p), step, tuple(-n * 0.15), win, tags={"clamp"}))
    return items


def arm_base():
    """URDF arm_base -> world, standing on the plywood."""
    Rz = trimesh.transformations.rotation_matrix(ARM_YAW, (0, 0, 1))
    return T(t=(0, 0, P.PLY["t"])) @ Rz


def arm_meshes(piper, q=REST, grip=0.01, keep=None, world=True):
    """Arm meshes [(link, trimesh, rgb)], in world space or in each link's frame.
    `keep` decimates any sub-mesh over 400 faces to that fraction of its faces."""
    out = []
    poses = piper.fk(q, grip=grip)
    B = arm_base()
    for name, path in piper.meshes.items():
        scene = trimesh.load(path, force="scene")
        for node in scene.graph.nodes_geometry:
            Tn, g = scene.graph[node]
            m = scene.geometry[g]
            if len(m.faces) < 10:
                continue
            try:
                c = np.array(m.visual.material.main_color[:3]) / 255
            except AttributeError:
                c = np.array([0.6, 0.6, 0.6])
            m = trimesh.Trimesh(trimesh.transform_points(m.vertices, Tn), m.faces, process=False)
            if keep and len(m.faces) > 400:
                import pyvista as pv
                pd = pv.wrap(m).decimate(1 - keep)
                m = trimesh.Trimesh(pd.points, pd.faces.reshape(-1, 4)[:, 1:], process=False)
            m.apply_transform(piper.visual_origin[name])
            if world:
                m.apply_transform(B @ poses[name])
            out.append((name, m, c))
    return out


# ------------------------------------------------------------------ cut list
def stick_plan(lengths):
    """First-fit decreasing onto 10 ft sticks."""
    sticks = []
    for L in sorted(lengths, reverse=True):
        for s in sticks:
            if sum(s) + len(s) * KERF + L <= STICK:
                s.append(L)
                break
        else:
            sticks.append([L])
    return sticks


def cloth_plan():
    """Panel sizes (w x h, m) and how they come out of two drop cloths."""
    X, Y, Z = OUTER["x"], OUTER["y"], OUTER["z"]
    panels = {
        "Top": (X + 2 * WRAP, Y + 2 * WRAP),
        "Back": (X + 2 * WRAP, Z + 2 * WRAP),
        "Left side": (Y + 2 * WRAP, Z + 2 * WRAP),
        "Right side": (Y + 2 * WRAP, Z + 2 * WRAP),
        "Front flap": (X + 2 * WRAP, Z + 2 * WRAP),
    }
    W, L = P.CLOTH_SHEET
    # Cloth 1: top and back one after the other down the length; both sides down the offcut strip.
    top, back, side = panels["Top"], panels["Back"], panels["Left side"]
    strip = W - top[0]
    fits = (top[1] + back[1] <= L) and (side[1] <= strip) and (2 * side[0] <= L)
    return panels, fits, strip


def fmt_in(m):
    q = round(m / P.IN * 8) / 8
    whole, frac = int(q), q - int(q)
    fr = {0: "", 0.125: " 1/8", 0.25: " 1/4", 0.375: " 3/8", 0.5: " 1/2", 0.625: " 5/8", 0.75: " 3/4", 0.875: " 7/8"}
    return f"{whole}{fr[round(frac, 3)]} in"


PRICES = [  # checked 2026-09-25 (see ../README.md); qty filled in from the model
    ("Pipe", "Charlotte 3/4 in Sch 40 PVC, 10 ft", 9.31, "https://www.homedepot.com/p/Charlotte-Pipe-3-4-in-x-10-ft-PVC-Schedule-40-Pressure-Plain-End-Pipe-PVC-04007-0600/100348472"),
    ("Corners", "FORMUFIT 3/4 in 3-way elbow, white, 8-pack", 18.99, "https://www.homedepot.com/p/Formufit-3-4-in-Furniture-Grade-PVC-3-Way-Elbow-in-White-8-Pack-F0343WE-WH-8/205749438"),
    ("Cloth", "Everbilt 8 oz canvas drop cloth, 9 × 12 ft", 34.98, "https://www.homedepot.com/p/Everbilt-9-ft-x-12-ft-8-oz-Canvas-Drop-Cloth-BARI-DP8-9-12/308535004"),
    ("Base", "Columbia PureBond 3/4 in birch plywood, 2 × 4 ft", 34.11, "https://www.homedepot.com/p/Columbia-Forest-Products-3-4-in-x-2-ft-x-4-ft-PureBond-Birch-Plywood-Project-Panel-4391/311925836"),
    ("Arm screws", "Everbilt M5 × 25 mm socket cap, 3-pack", 2.75, "https://www.homedepot.com/p/Everbilt-M5-0-8-x-25-mm-Zinc-Plated-Steel-Socket-Cap-Recessed-Hex-Screws-3-per-Pack-803318/204281933"),
    ("Cloth to pipe", "Snap clamps for 3/4 in PVC, 10-pack", 8.80, "https://www.johnnyseeds.com/tools-supplies/greenhouse-and-tunnel-supplies/hardware-accessories/snap-clamps-for-3-4%22-pvc-or-1%22-emt-7036.html"),
]


def write_cut_list(items, path):
    pipes = [it for it in items if "pipe" in it.tags]
    lengths = [float(np.ptp(it.part.mesh.bounds[:, 2])) for it in pipes]
    sticks = stick_plan(lengths)
    n_clamp = sum("clamp" in it.tags for it in items)
    n_elbow = sum("elbow" in it.tags for it in items)
    n_screw = sum("screw" in it.tags for it in items)
    panels, fits, strip = cloth_plan()
    qty = {"Pipe": len(sticks), "Corners": -(-n_elbow // 8), "Cloth": 2, "Base": 1,
           "Arm screws": -(-n_screw // 3), "Cloth to pipe": -(-n_clamp // 10)}

    L = ["# Spot D enclosure: cut list and parts", "",
         "Generated by `build.py` from the same layout the renders use. Lengths are in mm, with the",
         "nearest 1/8 in alongside.", "",
         "## Overall", "",
         "| | Width (x, along the wall) | Depth (y) | Height |", "|---|---|---|---|",
         f"| Table top at D | {TABLE['x'] * 1000:.0f} | {TABLE['y'] * 1000:.0f} | |",
         f"| Frame, outside of the fittings | {OUTER['x'] * 1000:.0f} | {OUTER['y'] * 1000:.0f} | {OUTER['z'] * 1000:.0f} |",
         f"| Frame, pipe centre to pipe centre | {SPAN['x'] * 1000:.0f} | {SPAN['y'] * 1000:.0f} | {SPAN['z'] * 1000:.0f} |",
         "",
         f"Each pipe is cut {2 * P.ELBOW_STOP * 1000:.1f} mm shorter than the centre-to-centre span, because it stops",
         f"{P.ELBOW_STOP * 1000:.1f} mm (0.603 in) short of the corner inside each FORMUFIT elbow.", "",
         "## Pipe (3/4 in Sch 40 PVC)", "",
         "| Member | Qty | Cut length |", "|---|---|---|"]
    for key, name in (("x", "Front and back rails, top and bottom"), ("y", "Side rails, top and bottom"),
                      ("z", "Corner posts")):
        L.append(f"| {name} | 4 | **{CUT[key] * 1000:.0f} mm** ({fmt_in(CUT[key])}) |")
    L += ["", f"Out of {len(sticks)} × 10 ft sticks, allowing {KERF * 1000:.0f} mm per saw cut:", ""]
    for i, s in enumerate(sticks, 1):
        off = STICK - sum(s) - len(s) * KERF
        L.append(f"- Stick {i}: " + " + ".join(f"{x * 1000:.0f}" for x in s) + f" mm, {off * 1000:.0f} mm left over")
    L += ["", "Dry-fit the whole frame before gluing anything. Glued, it will not come apart again. Press-fit",
          "joints hold well enough for a cloth enclosure, and a single screw through each socket makes one",
          "joint solid but still removable.", "",
          "## Canvas", "",
          f"Every panel is the frame face plus {WRAP * 1000:.0f} mm on each clamped edge, which is enough to wrap half",
          "way round the pipe under a snap clamp. The drop cloth is hemmed on its own edges, so keep those",
          "for the free bottom edge of the front flap and fold the cut edges under the clamps.", "",
          "| Panel | Size (w × h) | Clamped to |", "|---|---|---|"]
    where = {"Top": "all four top rails", "Back": "top rail, back posts, bottom rail",
             "Left side": "top rail, posts, bottom rail", "Right side": "top rail, posts, bottom rail",
             "Front flap": "front top rail only, so it rolls up"}
    for k, (w, h) in panels.items():
        L.append(f"| {k} | {w * 1000:.0f} × {h * 1000:.0f} mm | {where[k]} |")
    W, Lc = P.CLOTH_SHEET
    L += ["", f"The \"9 × 12 ft\" drop cloth is {W * 1000:.0f} × {Lc * 1000:.0f} mm (8 ft 9 in × 11 ft 9 in) finished.",
          f"Cloth 1 gives the top and back, one after the other along its length, and both sides out of the "
          f"{strip * 1000:.0f} mm strip left beside them"
          + (". " if fits else " (**does not fit**, check the numbers). ")
          + "Cloth 2 gives the front flap, with enough left over to double the top or the back if the room",
          "light shows through.", "",
          "## Snap clamps", "",
          f"{n_clamp} in total, three per pipe at 15 %, 50 % and 85 % of the exposed length:", "",
          "- 12 on the top rails, which hold the top and the upper edge of every wall",
          "- 12 on the corner posts, which hold where two walls meet",
          "- 9 on the back and side bottom rails. The front bottom rail has none, so the flap hangs free.", "",
          "## Plywood base", "",
          f"- Panel {P.PLY['w'] / P.IN:.0f} × {P.PLY['l'] / P.IN:.0f} in, long side front to back, centred on the table.",
          f"- Four Ø{P.HOLE_D * 1000:.1f} mm through holes on a {P.HOLE_SQ * 1000:.0f} mm square at the panel's centre.",
          f"- Ø{P.CBORE_D * 1000:.0f} mm counterbores {P.CBORE_H * 1000:.0f} mm deep from underneath, so the screw heads sit below the surface.",
          f"- An M5 × 25 then reaches {(0.025 - (P.PLY['t'] - P.CBORE_H)) * 1000:.0f} mm into the arm's base. Check the depth of the arm's",
          "  threaded holes first. If they are shallower, drill the counterbores deeper, not the other way round.",
          "- Mark the holes from the arm itself, not from this drawing. Stand the base on paper, trace it and",
          "  punch through its holes.", "",
          "## Parts to buy", "",
          "| Item | Product | Qty | Each | Total |", "|---|---|---|---|---|"]
    total = 0
    for item, prod, price, url in PRICES:
        n = qty[item]
        total += n * price
        L.append(f"| {item} | [{prod}]({url}) | {n} | ${price:.2f} | ${n * price:.2f} |")
    L += [f"| | | | **Total** | **${total:.2f}** |", "",
          "Prices are from 2026-09-25, before tax. The frame uses", f"{n_elbow} elbows, {len(pipes)} pipes, "
          f"{n_clamp} snap clamps and {n_screw} screws."]
    path.write_text("\n".join(L) + "\n")
    return dict(sticks=len(sticks), clamps=n_clamp, total=total)


# ------------------------------------------------------------------ export
def export(items, piper):
    mdir = HERE / "models"
    mdir.mkdir(exist_ok=True)
    mm = np.diag([1000, 1000, 1000, 1])
    seen = {}
    for it in items:
        if "cloth" not in it.tags and it.part.name not in seen:
            seen[it.part.name] = it.part
    for name, part in seen.items():
        part.mesh.copy().apply_transform(mm).export(mdir / f"{name}.stl")
    hard = [it.world for it in items if "cloth" not in it.tags]
    trimesh.util.concatenate(hard).apply_transform(mm).export(mdir / "enclosure-frame.stl")

    scene = trimesh.Scene()

    def add(mesh, rgb, name):
        m = mesh.copy()
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=[*rgb, 1.0], metallicFactor=0.0, roughnessFactor=0.8, doubleSided=True))
        scene.add_geometry(m, node_name=name)

    hexrgb = lambda h: [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]  # noqa: E731
    for i, it in enumerate(items):
        if "flap" not in it.tags:
            add(it.world, hexrgb(it.part.color), f"{it.part.name}-{i}")
    add(flap_roll(), hexrgb(P.canvas_panel(1, 1).color), "front-flap-rolled")
    for j, (link, m, c) in enumerate(arm_meshes(piper, keep=0.25)):
        add(m, list(c), f"piper-{link}-{j}")
    scene.export(HERE / "enclosure.glb")


def flap_roll():
    """The front flap rolled up under its top rail."""
    r = P.PIPE_OD / 2 + P.CLOTH_T / 2
    y = -(SPAN["y"] / 2 + r) - 0.03
    z = Z0 + SPAN["z"] - 0.035
    roll = trimesh.creation.cylinder(radius=0.03, height=OUTER["x"], sections=32)
    roll.apply_transform(T(rot_z_to((1, 0, 0)), (0, y, z)))
    return roll


if __name__ == "__main__":
    items = layout()
    info = write_cut_list(items, HERE / "cut-list.md")
    print({k: round(v, 3) * 1000 for k, v in OUTER.items()}, info)
    export(items, Piper())
    for f in sorted((HERE / "models").iterdir()) + [HERE / "enclosure.glb"]:
        print(f.name, f.stat().st_size // 1024, "kB")
