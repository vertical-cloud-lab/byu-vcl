"""Raised deck (hutch) under the spot D dome (#229): lay out the parts, write the cut list, export models.

    python build.py            # cut-list.md, models/*.stl, hutch.glb

The dome is the one in ../dome, with its eight rails cut to 45 1/2 in so that it stands on the
4 x 4 ft deck. Everything here is the recommended option ("ribs + shear panels" in hutch.py);
fea.py compares it with the others.
"""

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh
from trimesh.creation import box

import hutch as H

HERE = Path(__file__).parent
DOME = HERE.parent / "dome"
sys.path[:0] = [str(DOME), str(HERE.parent)]
_spec = importlib.util.spec_from_file_location("dome_build", DOME / "build.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
P = D.P                                     # the dome's part models (pipe, elbow, clamp, canvas, screw)
from piper_fk import Piper  # noqa: E402

IN = H.IN
OPT = H.RECOMMENDED
KERF = 0.0032                               # 1/8 in saw blade
SHEET_4x4 = (48 * IN, 48 * IN)
SHEET_4x8 = (48 * IN, 96 * IN)              # (across the grain, along the grain)
CLEAT = dict(w=0.040, l=1.180)              # foot cleats, from the offcut strip
ACCESS_D = 0.025                            # holes in the spine bottom, to reach the arm's screws
SCREW_L = 0.045                             # M5 x 45 through deck + pad
CBORE_D, CBORE_H = 0.010, 0.006

# The dome stands on the deck: rails shortened so its outside is the deck's 48 in.
D.CUT = {"x": 45.5 * IN, "y": 45.5 * IN, "z": 40.75 * IN}
D.SPAN = {k: v + 2 * P.ELBOW_STOP for k, v in D.CUT.items()}
D.OUTER = {k: v + P.ELBOW_OD for k, v in D.SPAN.items()}

STEPS = [
    "Spot D: two 680 × 1290 mm tables",
    "Side panels, cleated and clamped to the tables",
    "Back panel, glued and screwed between them",
    "Spine: doubler pad and two webs under the deck",
    "Spine bottom, with access holes for the arm screws",
    "Deck: the whole 4 × 4 ft sheet, glued and screwed",
    "PiPER bolted through deck and pad, from below",
    "Dome frame on the deck, rails cut to 45 1/2 in",
    "Canvas top and walls, snap-clamped",
    "Flap up: arm on top, 0.5 m clear underneath",
]
ARM_STEP, DOME_STEP, CLOTH_STEP = 6, 7, 8


def T(R=np.eye(3), t=(0, 0, 0)):
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = t
    return M


@dataclass
class Item:
    name: str
    mesh: trimesh.Trimesh          # world, assembled
    color: str
    step: int
    entry: tuple = (0, 0, 0.4)     # flies in from here, relative to its place
    explode: tuple = (0, 0, 0)     # offset in the exploded view
    tags: set = field(default_factory=set)


# ------------------------------------------------------------------ plywood parts
def _cyl(r, z0, z1, x=0.0, y=0.0):
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=32)
    c.apply_translation((x, y, (z0 + z1) / 2))
    return c


def board_mesh(b):
    m = box(b.size)
    m.apply_translation(b.centre)
    cuts = []
    if b.name in ("deck", "spine-pad"):
        for x, y in H.hole_xy():
            cuts.append(_cyl(0.00275, b.lo[2] - 0.001, b.hi[2] + 0.001, x, y))
            if b.name == "spine-pad":
                cuts.append(_cyl(CBORE_D / 2, b.lo[2] - 0.001, b.lo[2] + CBORE_H, x, y))
    if b.name == "spine-bottom":
        for x, y in H.hole_xy():
            cuts.append(_cyl(ACCESS_D / 2, b.lo[2] - 0.001, b.hi[2] + 0.001, x, y))
    if cuts:
        m = trimesh.boolean.difference([m, *cuts], engine="manifold")
    return m


def cleats():
    """Foot cleats outside each side panel, for clamping to the table ends."""
    out = []
    for s in (-1, 1):
        x0 = s * H.W / 2
        lo = (min(x0, x0 + s * H.T), -CLEAT["l"] / 2, 0)
        hi = (max(x0, x0 + s * H.T), CLEAT["l"] / 2, CLEAT["w"])
        out.append(H.Board(f"cleat-{'left' if s < 0 else 'right'}", lo, hi, 1, (CLEAT["l"], CLEAT["w"]), step=1,
                           tags=("cleat",)))
    return out


PLY_COLORS = {"deck": "#e3d2ad", "side": "#dcc79c", "back": "#d6c08f", "spine": "#cdb27d", "cleat": "#cdb27d"}


def hutch_items():
    items = []
    shift = T(t=(0, H.YC, 0))
    for b in H.boards(OPT) + cleats():
        kind = next((t for t in ("deck", "side", "back", "spine", "cleat") if t in b.tags), "deck")
        m = board_mesh(b).apply_transform(shift)
        c = b.centre
        if kind == "side" or kind == "cleat":
            entry, ex = (np.sign(c[0]) * 0.5, 0, 0.3), (np.sign(c[0]) * 0.55, 0, 0)
        elif kind == "back":
            entry, ex = (0, 0.4, 0.4), (0, 0.45, 0)
        elif kind == "spine":
            ex = {"spine-pad": (0, 0, -0.12), "spine-bottom": (0, 0, -0.42)}.get(b.name, (0, np.sign(c[1]) * 0.12, -0.25))
            entry = (0, -0.6, 0.0)
        else:
            entry, ex = (0, 0, 0.5), (0, 0, 0.32)
        items.append(Item(b.name, m, PLY_COLORS[kind], b.step, entry, ex, {kind, "ply"}))
    return items


# ------------------------------------------------------------------ dome and arm
def dome_items():
    lift = T(t=(0, H.YC, H.deck_top()))
    out = []
    for it in D.layout():
        if it.tags & {"base", "screw"}:
            continue
        step = DOME_STEP if not it.tags & {"cloth", "clamp"} else CLOTH_STEP
        tags = set(it.tags) | {"dome"}
        out.append(Item(it.part.name, it.world.apply_transform(lift), it.part.color, step,
                        (0, 0, 0.5), (0, 0, 0.75), tags))
    return out


def arm_base():
    return T(t=(0, H.YC, H.deck_top())) @ trimesh.transformations.rotation_matrix(D.ARM_YAW, (0, 0, 1))


def arm_meshes(piper, q=D.REST, keep=None, world=True):
    D.arm_base = arm_base                     # the dome's helper, re-pointed at the deck
    return D.arm_meshes(piper, q=q, keep=keep, world=world)


def screws():
    """M5 x 45 socket caps, heads in the pad's counterbores, up into the arm."""
    s = P.m5_socket_cap(SCREW_L)
    out = []
    z = H.CLEAR - H.T + CBORE_H
    for x, y in H.hole_xy():
        out.append(Item("m5x45-socket-cap", s.mesh.copy().apply_transform(T(t=(x, y + H.YC, z))), s.color, ARM_STEP,
                        (0, 0, -0.25), (0, 0, -0.55), {"screw"}))
    return out


def layout():
    return hutch_items() + screws() + dome_items()


# ------------------------------------------------------------------ cut plan
def sheet_plan():
    """Where each board comes out of the two sheets: [(sheet, name, x0, y0, w, l)], x across the
    grain and y along it, metres. Every board has its grain along its length."""
    bs = {b.name: b for b in H.boards(OPT)}
    W, L = SHEET_4x8
    side = bs["side-left"].cut          # (1219, 500): length along the grain
    back, web, bot, pad = bs["back"].cut, bs["spine-web-front"].cut, bs["spine-bottom"].cut, bs["spine-pad"].cut
    plan = [("4 × 4 ft (the sheet you have)", "deck", 0, 0, H.W, H.W)]
    s2 = "4 × 8 ft (second sheet)"
    # row A along the first 1219 mm: two sides and both webs side by side
    x = 0
    for nm, (l, w) in (("side-left", side), ("side-right", side), ("spine-web-front", web), ("spine-web-rear", web)):
        plan.append((s2, nm, x, 0, w, l))
        x += w + KERF
    rowA_left = W - x + KERF
    # row B after a crosscut: back, spine bottom, pad, then cleats from what is left
    y0 = side[0] + KERF
    x = 0
    for nm, (l, w) in (("back", back), ("spine-bottom", bot)):
        plan.append((s2, nm, x, y0, w, l))
        x += w + KERF
    plan.append((s2, "spine-pad", x, y0, pad[1], pad[0]))
    x += pad[1] + KERF
    for nm in ("cleat-left", "cleat-right"):
        plan.append((s2, nm, x, y0, CLEAT["w"], CLEAT["l"]))
        x += CLEAT["w"] + KERF
    left = dict(rowA=(rowA_left, side[0]), rowB=(W - x + KERF, L - y0))
    assert all(p[2] + p[4] <= W + 1e-6 and p[3] + p[5] <= (L if "8" in p[0] else H.W) + 1e-6 for p in plan)
    return plan, left


def fmt(m):
    q = round(m / IN * 8) / 8
    whole, frac = int(q), q - int(q)
    fr = {0: "", 0.125: " 1/8", 0.25: " 1/4", 0.375: " 3/8", 0.5: " 1/2", 0.625: " 5/8", 0.75: " 3/4", 0.875: " 7/8"}
    return f"{m * 1000:.0f} mm ({whole}{fr[round(frac, 3)]} in)"


def write_cut_list(path):
    plan, left = sheet_plan()
    names = {
        "deck": ("Deck", "grain left to right; 4 × Ø5.5 mm at the centre on a 70 mm square"),
        "side-left": ("Side panel", "grain front to back"), "side-right": ("Side panel", ""),
        "back": ("Back panel", "grain left to right"),
        "spine-web-front": ("Spine web", "grain along the length"), "spine-web-rear": ("Spine web", ""),
        "spine-bottom": ("Spine bottom", f"4 × Ø{ACCESS_D * 1000:.0f} mm access holes under the arm's screws"),
        "spine-pad": ("Doubler pad", f"4 × Ø5.5 mm, Ø{CBORE_D * 1000:.0f} mm counterbores {CBORE_H * 1000:.0f} mm deep from below"),
        "cleat-left": ("Foot cleat", "from the offcut"), "cleat-right": ("Foot cleat", ""),
    }
    rows, seen = [], {}
    for sheet, nm, x, y, w, l in plan:
        label, note = names[nm]
        key = (label, round(l, 4), round(w, 4))
        if key in seen:
            rows[seen[key]][3] += 1
            continue
        seen[key] = len(rows)
        rows.append([label, fmt(l), fmt(w), 1, sheet.split(" (")[0], note])
    L = ["# Raised deck (hutch) at spot D: cut list", "",
         "Generated by `build.py` for the recommended build (spine box and back panel). All parts are",
         f"3/4 in plywood, {H.T * 1000:.1f} mm ({H.T / IN:.3f} in) actual. Lengths run along the face grain.", "",
         "## Plywood", "",
         "| Part | Length (along grain) | Width | Qty | From | Notes |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |")
    L += ["", "![Sheet layout](sheet-layout.png)", "",
          "- **Sheet 1** is the 4 × 4 ft sheet you have. It becomes the deck, whole.",
          "- **Sheet 2** is one more 4 × 8 ft sheet of the same 3/4 in plywood, grain along the 8 ft. Crosscut it",
          f"  at 48 in first. The first half gives both sides and both webs, with a {left['rowA'][0] * 1000:.0f} mm strip left over.",
          "  The second half gives the back, the spine bottom, the pad and both cleats, with a",
          f"  {left['rowB'][0] * 1000:.0f} × {left['rowB'][1] * 1000:.0f} mm offcut left over.",
          "- Two 4 × 4 ft halves work just as well as one 4 × 8. If the arm's current base is the other half of the",
          "  sheet you already cut, it is freed when the arm moves up to the deck, and it can supply the second half.",
          "", "## Dome rails", "",
          "The dome frame stands on the deck, so its eight rails are recut. The posts do not change.", "",
          "| Member | Qty | Cut length | Was |", "|---|---|---|---|",
          f"| Front, back and side rails, top and bottom | 8 | **{fmt(D.CUT['x'])}** | 48 in and 50 3/4 in |",
          f"| Corner posts | 4 | {fmt(D.CUT['z'])} | the same |", "",
          f"Outside of the fittings, the frame is now {D.OUTER['x'] * 1000:.0f} × {D.OUTER['y'] * 1000:.0f} × "
          f"{D.OUTER['z'] * 1000:.0f} mm, the same as the deck. If the rails are already cut to the old lengths,",
          "trim them. Every rail is now the same length, so the frame can go together either way round.", "",
          "## Hardware", "",
          "| Item | Qty | Where |", "|---|---|---|",
          "| Wood glue (PVA, e.g. Titebond II) | 1 bottle | every plywood joint |",
          "| #8 × 1 1/2 in wood screws | about 60 | deck into sides, back and webs every 150 mm; through the sides into the web and back ends; spine bottom into the webs |",
          f"| M5 × {SCREW_L * 1000:.0f} mm socket cap screws | 4 | the arm, up through the pad and deck |",
          "| 4 in C-clamps | 4 | the foot cleats to the table ends |", "",
          f"An M5 × {SCREW_L * 1000:.0f} reaches {(SCREW_L - (2 * H.T - CBORE_H)) * 1000:.0f} mm into the arm's base. "
          "Check the depth of its threaded holes first.", ""]
    path.write_text("\n".join(L))
    return plan


# ------------------------------------------------------------------ export
def export(items, piper):
    mdir = HERE / "models"
    mdir.mkdir(exist_ok=True)
    mm = np.diag([1000, 1000, 1000, 1])
    back = T(t=(0, -H.YC, 0))
    done = set()
    for it in items:
        if "ply" in it.tags and it.name.rstrip("-leftright") not in done:
            base = it.name.replace("-left", "").replace("-right", "").replace("-front", "").replace("-rear", "")
            if base in done:
                continue
            done.add(base)
            it.mesh.copy().apply_transform(back).apply_transform(mm).export(mdir / f"{base}.stl")
    hard = [it.mesh for it in items if "ply" in it.tags or "screw" in it.tags]
    trimesh.util.concatenate(hard).apply_transform(mm).export(mdir / "hutch.stl")

    scene = trimesh.Scene()

    def add(mesh, rgb, name):
        m = mesh.copy()
        m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=[*rgb, 1.0], metallicFactor=0.0, roughnessFactor=0.8, doubleSided=True))
        scene.add_geometry(m, node_name=name)

    hexrgb = lambda h: [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]  # noqa: E731
    for y0, y1 in ((-D.TABLE["y"] / 2, -0.0015), (0.0015, D.TABLE["y"] / 2)):
        t = box((D.TABLE["x"], y1 - y0, 0.03))
        t.apply_translation((0, (y0 + y1) / 2, -0.015))
        add(t, hexrgb("#26272a"), f"table-{y0:.2f}")
    for i, it in enumerate(items):
        if "flap" not in it.tags:
            add(it.mesh, hexrgb(it.color), f"{it.name}-{i}")
    add(flap_roll(), hexrgb("#e8dfcb"), "front-flap-rolled")
    for j, (link, m, c) in enumerate(arm_meshes(piper, keep=0.25)):
        add(m, list(c), f"piper-{link}-{j}")
    scene.export(HERE / "hutch.glb")


def flap_roll():
    return D.flap_roll().apply_transform(T(t=(0, H.YC, H.deck_top())))


def heights():
    top = H.deck_top() + D.OUTER["z"]
    return dict(deck_top=H.deck_top(), under_spine=H.CLEAR - H.SPINE_H - H.T, dome_top=top,
                floor_top=H.TABLE["h"] + top, floor_deck=H.TABLE["h"] + H.deck_top())


if __name__ == "__main__":
    items = layout()
    write_cut_list(HERE / "cut-list.md")
    export(items, Piper())
    print({k: round(v, 3) for k, v in heights().items()})
    for f in sorted((HERE / "models").iterdir()) + [HERE / "hutch.glb"]:
        print(f.name, f.stat().st_size // 1024, "kB")
