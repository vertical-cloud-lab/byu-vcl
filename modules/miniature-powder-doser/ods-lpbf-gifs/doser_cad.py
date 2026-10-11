"""The lab's powder doser, loaded from its text-to-cad assembly, for the gravity-feed GIF (ods_c_gravity).

Source: vertical-cloud-lab/powder-doser PR 176 (branch claude/issue-172-20261003-2216, commit 509a0bf),
cad/text-to-cad/STEP/assembly_servos_above.step: the current doser rebuilt as code (printed parts in build123d,
vendor NEMA 11, MG996R and Adafruit 412 models, step.parts fasteners, and the POWDER_DOSER_V2 PCB from its Gerbers on
its printed holder), servos-above layout. Point POWDER_DOSER at a checkout's cad/text-to-cad folder.

Every leaf keeps its place in the assembly. The leaves are sorted into the assembly's moving groups, so the GIF can
tilt, turn and tap the doser the way the STEP's kinematics sidecar defines it, and into the material each part would
be made of for the rePowder chamber (README, "The doser in the chamber"). The wooden board is left out: the pod's
steel stand replaces it.

Frame (the assembly's own): z = 0 is the board's top, the auger runs along +y on x = 0 from its outlet (y = 35.4)
to its cap (y = 288), and the hinge is the x axis through (0, 45.4, 38.25).
"""
from __future__ import annotations

import hashlib
import os
import pickle
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
SRC = Path(os.environ.get("POWDER_DOSER", "/tmp/powder-doser/cad/text-to-cad"))
STEP = SRC / "STEP" / "assembly_servos_above.step"
CACHE = HERE / ".cache"

# kinematics, from STEP/assembly_servos_above.step.json
HINGE = np.array([0.0, 45.4, 38.25])                  # tilt: about +x; positive lifts the cap end, outlet down
AUGER_AXIS = np.array([0.0, 35.4, 38.25])             # auger_spin: about +y
OUTLET = AUGER_AXIS.copy()                            # the outlet is on the auger's front face
PINION_AXIS = np.array([-32.0, 113.73, 38.25])        # stepper pinion: about +y, -2.2 x the auger
SERVO_AXES = {"pos": np.array([41.8, 45.4, 65.5]), "neg": np.array([-41.8, 45.4, 65.5])}   # -2 x the tilt
PLUNGER_DIR = np.array([-0.5, 0.0, -0.866025])        # slider, 0 to 7.6 mm
PLUNGER_STROKE = 7.6
# the PCB holder's pose in the doser frame (lib/electronics_place.py: turned -90 deg, origin (50, 240, 0))
HOLDER_ORIGIN = np.array([50.0, 240.0, 0.0])

# materials for the chamber version: colour, and how shiny
MATERIALS = {
    "ss": ((0.74, 0.76, 0.80), 0.55),          # 304 / 316L stainless, machined
    "ss_am": ((0.55, 0.56, 0.59), 0.25),       # 316L printed by LPBF (the auger): matte
    "peek": ((0.80, 0.67, 0.46), 0.15),        # PEEK pinions
    "vac_motor": ((0.19, 0.20, 0.23), 0.30),   # vacuum-rated stepper / gearmotors in the MG996R cradles
    "coil": ((0.78, 0.45, 0.22), 0.40),        # solenoid winding
    "kapton": ((0.86, 0.55, 0.12), 0.20),      # Kapton-insulated leads
    "fastener": ((0.66, 0.68, 0.71), 0.50),    # A4 stainless, vented
    "alu": ((0.83, 0.85, 0.88), 0.35),         # the PCB holder, machined 6061 (outside the pod)
    "fr4": ((0.07, 0.38, 0.20), 0.20),
    "module": ((0.10, 0.30, 0.48), 0.20),      # the plug-in modules (Pico W, Tic, drivers)
    "chip": ((0.09, 0.09, 0.10), 0.20),
    "gold": ((0.86, 0.72, 0.32), 0.60),
    "cap": ((0.14, 0.16, 0.30), 0.30),
}


def classify(path: str) -> tuple[str, str] | None:
    """(moving group, material) for a leaf of the assembly, or None to leave it out."""
    leaf = path.split("/")[-1]
    if leaf == "board":
        return None
    if path.startswith("electronics"):
        if leaf.startswith(("electronics_pads", "electronics_copper", "electronics_silk")):
            return None                         # coplanar with the FR-4; they would z-fight
        if leaf == "electronics_pcb_holder":
            return "pcb", "alu"
        if leaf == "electronics_fr4":
            return "pcb", "fr4"
        if leaf == "electronics_pcb":
            return "pcb", "module"
        if "pin" in leaf.split("_")[-1] or "tail" in leaf:
            return "pcb", "gold"
        if leaf.startswith("electronics_C_"):
            return "pcb", "cap"
        if "screw" in leaf or "standoff" in leaf:
            return "pcb", "fastener"
        return "pcb", "chip"
    parts = path.split("/")
    if parts[0].startswith("servo_pinion"):
        side = "pos" if parts[0].endswith("pos_group") else "neg"
        return f"servo_{side}", ("fastener" if "screw" in leaf else "peek")
    if parts[0].startswith("servo_"):
        return "base", ("vac_motor" if leaf.endswith("_case") else "ss")
    if parts[0] in ("baseplate", "baseplate_hw"):
        return "base", ("ss" if leaf == "baseplate" else "fastener")
    if parts[0] == "tilt_group":
        if "auger_group" in parts:
            return "auger", ("ss_am" if leaf == "auger" else "ss")
        if leaf == "stepper_pinion":
            return "pinion", "peek"
        if leaf in ("solenoid_plunger", "solenoid_spring"):
            return "plunger", "ss"
        if leaf == "stepper_motor":
            return "tilt", "vac_motor"
        if leaf == "stepper_leads":
            return "tilt", "kapton"
        if leaf == "solenoid_coil":
            return "tilt", "coil"
        if "screw" in leaf or "nut" in leaf or "nylon" in leaf:
            return "tilt", "fastener"
        return "tilt", "ss"
    return "base", "ss"


def _leaves(step: Path):
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TDF import TDF_Label, TDF_LabelSequence
    from OCP.TDocStd import TDocStd_Document
    from OCP.TopLoc import TopLoc_Location
    from OCP.XCAFDoc import XCAFDoc_DocumentTool

    doc = TDocStd_Document(TCollection_ExtendedString("doser"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    reader.ReadFile(str(step))
    reader.Transfer(doc)
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

    def name(label):
        a = TDataStd_Name()
        return a.Get().ToExtString() if label.FindAttribute(TDataStd_Name.GetID_s(), a) else "?"

    out = []

    def walk(label, loc, path):
        lab = label
        if tool.IsReference_s(label):
            ref = TDF_Label()
            tool.GetReferredShape_s(label, ref)
            lab = ref
            loc = loc.Multiplied(tool.GetLocation_s(label))
        if tool.IsAssembly_s(lab):
            comps = TDF_LabelSequence()
            tool.GetComponents_s(lab, comps)
            for i in range(1, comps.Length() + 1):
                walk(comps.Value(i), loc, path + [name(label)])
        else:
            out.append(("/".join(path[1:] + [name(label)]), tool.GetShape_s(lab).Moved(loc)))

    roots = TDF_LabelSequence()
    tool.GetFreeShapes(roots)
    walk(roots.Value(1), TopLoc_Location(), [])
    return out


def _tess(shape, tol=0.12):
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    BRepMesh_IncrementalMesh(shape, tol, False, 0.35, True)
    pts, tris, off = [], [], 0
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        face = TopoDS.Face_s(ex.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            p = [tri.Node(i).Transformed(trsf) for i in range(1, tri.NbNodes() + 1)]
            pts.append(np.array([[q.X(), q.Y(), q.Z()] for q in p]))
            t = np.array([tri.Triangle(i).Get() for i in range(1, tri.NbTriangles() + 1)]) - 1
            if face.Orientation() == TopAbs_REVERSED:
                t = t[:, [0, 2, 1]]
            tris.append(t + off)
            off += len(p)
        ex.Next()
    if not pts:
        return None
    return np.vstack(pts), np.vstack(tris)


def meshes() -> dict[tuple[str, str], pv.PolyData]:
    """{(group, material): merged mesh in the doser frame}, cached in .cache/ against the STEP's hash."""
    digest = hashlib.sha1(STEP.read_bytes()).hexdigest()[:12]
    cache = CACHE / f"doser_{digest}.pkl"
    if cache.exists():
        raw = pickle.loads(cache.read_bytes())
    else:
        acc: dict[tuple[str, str], list] = {}
        for path, shape in _leaves(STEP):
            key = classify(path)
            if key is None:
                continue
            m = _tess(shape)
            if m is not None:
                acc.setdefault(key, []).append(m)
        raw = {}
        for key, ms in acc.items():
            off, P, F = 0, [], []
            for p, t in ms:
                P.append(p)
                F.append(t + off)
                off += len(p)
            raw[key] = (np.vstack(P), np.vstack(F))
        CACHE.mkdir(exist_ok=True)
        cache.write_bytes(pickle.dumps(raw))
    out = {}
    for key, (p, t) in raw.items():
        faces = np.hstack([np.full((len(t), 1), 3), t]).astype(np.int64).ravel()
        out[key] = pv.PolyData(p, faces).compute_normals(split_vertices=True, feature_angle=35.0)
    return out


def _leaf_cache() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """{assembly path: (points, triangles)} for every leaf, in the doser frame, cached against the STEP's hash."""
    digest = hashlib.sha1(STEP.read_bytes()).hexdigest()[:12]
    cache = CACHE / f"leaves_{digest}.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    out = {}
    for path, shape in _leaves(STEP):
        m = _tess(shape)
        if m is not None:
            out[path] = m
    CACHE.mkdir(exist_ok=True)
    cache.write_bytes(pickle.dumps(out))
    return out


def _poly(p, t) -> pv.PolyData:
    faces = np.hstack([np.full((len(t), 1), 3), t]).astype(np.int64).ravel()
    return pv.PolyData(np.asarray(p, float), faces)


# ------------------------------------------------------------------------------------------------- in-chamber module
# The doser as built does not fit beside the stream (README, "Inside the chamber"), so the in-chamber module keeps PR
# 176's drive parts and folds them up: the tube keeps its outlet end, its 44T gear and its cap thread but loses most of
# the reservoir, so the gear sits 20 mm from the outlet and the NEMA 11 (still behind the gear, on its upright) reaches
# past the cap. The tilt servos, baseplate, mounting plate, tap collar and solenoid stay behind; a machined cradle plate
# carries the two brackets and the stepper's upright, at a fixed tilt. Outlet face to cap end: 85.4 mm (PR 176: 252).
COMPACT_TUBE = [(35.4, 45.0), (103.7, 133.7), (180.0, 193.0), (255.4, 288.2)]   # pieces of PR 176's tube, end to end


def _tube_shifts():
    out, y = [], COMPACT_TUBE[0][0]
    for a, b in COMPACT_TUBE:
        out.append((a, b, y - a))
        y += b - a
    return out


SHIFT_GEAR = _tube_shifts()[1][2]                       # -58.7: the gear, pinion, stepper and its upright move this far
SHIFT_CAP = _tube_shifts()[3][2]                        # -167.4
SHIFT_FRONT = 40.0 - 81.7                               # front bracket: just behind the outlet, on plain tube
SHIFT_REAR = 76.5 - 163.4                               # rear bracket: beside the stepper, as in PR 176, before the cap
COMPACT_PINION_AXIS = PINION_AXIS + np.array([0.0, SHIFT_GEAR, 0.0])
CRADLE = (-48.0, 32.0, 38.0, 90.0, 3.0, 9.0)            # x0, x1, y0, y1, z0, z1 (machined 304, under the brackets)

# The nose (Sterling, 2026-10-07): no separate funnel or spout, and (his later note) no taper either, since a taper is
# where powder clogs. The tube keeps PR 176's storage-auger inside as tested: open 21 mm bore at the cap end, the flight in
# the outlet third, and the v4 outlet (a short funnel to a 3 mm annular exit round the core's tip). The only addition is a
# screw-on 316L capillary that keeps the exit's own 3 mm bore, smooth, as the storage augers keep their bore and drop the
# flight (along the axis, forward of the outlet face):
#   collar     0-3 mm    threads onto the outlet end, 25 mm OD
#   capillary  3-38 mm   3 mm bore (v4's exit), 5 mm OD, smooth: carries the granules to the stream; vibrated, it sets
#                        the rate between the flight's pulses
# It turns with the tube. A vibration motor on the front bracket's foot shakes the tube, and with it the capillary.
NOSE_OUT = [(0.0, 12.5), (3.0, 12.5), (3.0, 2.5), (38.0, 2.5)]       # (s, outer radius)
NOSE_IN = [(0.0, 1.5), (38.0, 1.5)]                                   # (s, bore radius)
NOSE_L = NOSE_OUT[-1][0]
NOSE_TIP = OUTLET - np.array([0.0, NOSE_L, 0.0])        # where the granules leave, in the doser frame
VIBRATOR = (np.array([23.5, 46.0, 24.5]), 6.5, 22.0)    # centre, radius, length: on the front bracket's foot


def nose_mesh(res=48) -> pv.PolyData:
    """The nose as a closed surface of revolution about the auger axis, from the outlet face forwards (-y)."""
    prof = [(r, s) for s, r in NOSE_OUT] + [(r, s) for s, r in reversed(NOSE_IN)]   # out along the outside, back
    a = np.linspace(0.0, 2 * np.pi, res, endpoint=False)
    pts = np.array([(r * np.cos(t), OUTLET[1] - s, OUTLET[2] + r * np.sin(t)) for r, s in prof for t in a])
    n, faces = len(prof), []
    for i in range(n):
        j = (i + 1) % n
        for k in range(res):
            k2 = (k + 1) % res
            faces += [4, i * res + k, i * res + k2, j * res + k2, j * res + k]
    return pv.PolyData(pts, faces).triangulate()


def _mirror_x(mesh: pv.PolyData) -> pv.PolyData:
    """Mirror image across the doser's x = 0 plane, with the faces re-wound so they still face out."""
    out = mesh.copy()
    out.points[:, 0] *= -1.0
    f = out.faces.reshape(-1, 4)
    out.faces = f[:, [0, 1, 3, 2]].ravel()
    return out


def compact_meshes(nose: bool = False, mirror: bool = False) -> dict[tuple[str, str], pv.PolyData]:
    """{(group, material): mesh} of the in-chamber module, in the doser frame (groups: base, auger, pinion).
    nose: add the screw-on nose (auger group) and the vibration motor on the front bracket (base group).
    mirror: the mirror-image build, with the stepper on the doser's +x side."""
    leaves = _leaf_cache()
    acc: dict[tuple[str, str], list[pv.PolyData]] = {}

    def put(key, mesh, dy=0.0):
        if mesh.n_points:
            acc.setdefault(key, []).append(mesh.translate((0.0, dy, 0.0), inplace=False))

    def leaf(name):
        return next(_poly(*m) for p, m in leaves.items() if p.split("/")[-1] == name)

    tube = leaf("auger")
    for a, b, dy in _tube_shifts():
        put(("auger", "ss_am"), tube.clip_box((-40, 40, a, b, -10, 90), invert=False), dy)
    put(("auger", "ss"), leaf("auger_cap"), SHIFT_CAP)
    put(("base", "ss"), leaf("bracket_front"), SHIFT_FRONT)
    put(("base", "ss"), leaf("bracket_rear"), SHIFT_REAR)
    put(("base", "ss"), leaf("mounting_plate_plate").clip_box((-47.0, -17.0, 127.5, 136.0, 8.5, 63.0), invert=False),
        SHIFT_GEAR)                                     # only the stepper's upright
    put(("base", "vac_motor"), leaf("stepper_motor"), SHIFT_GEAR)
    put(("base", "kapton"), leaf("stepper_leads"), SHIFT_GEAR)
    put(("pinion", "peek"), leaf("stepper_pinion"), SHIFT_GEAR)
    x0, x1, y0, y1, z0, z1 = CRADLE
    put(("base", "ss"), pv.Box((x0, x1, y0, y1, z0, z1)))
    # the screws that go with the brackets and the stepper
    for path, (p, t) in leaves.items():
        if not path.startswith("tilt_group") or not any(k in path.split("/")[-1] for k in ("screw", "nut")):
            continue
        c = p.mean(axis=0)
        for (xa, xb, ya, yb), dy in (((-31, 31, 80.0, 95.5), SHIFT_FRONT), ((-31, 31, 162.0, 177.0), SHIFT_REAR),
                                     ((-47, -17, 125.0, 140.0), SHIFT_GEAR)):
            if xa < c[0] < xb and ya < c[1] < yb:
                put(("base", "fastener"), _poly(p, t), dy)
                break
    if nose:
        put(("auger", "ss_am"), nose_mesh())
        c, r, L = VIBRATOR
        put(("base", "vac_motor"), pv.Cylinder(center=c, direction=(0, 1, 0), radius=r, height=L, resolution=32))
        put(("base", "ss"), pv.Box((c[0] - r - 0.5, c[0] + r + 0.5, c[1] - 5, c[1] + 5, 17.0, c[2])))   # its strap
    out = {k: pv.merge(v) for k, v in acc.items()}
    if mirror:
        out = {k: _mirror_x(m.triangulate()) for k, m in out.items()}
    return {k: m.compute_normals(split_vertices=True, feature_angle=35.0) for k, m in out.items()}


def holder_to_doser() -> np.ndarray:
    """4x4: the PCB holder's own frame (pcb_holder_assembly: x across, y back from its front face, z up from the board)
    to the doser frame."""
    m = np.eye(4)
    m[:3, :3] = [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]     # turned -90 deg about z
    m[:3, 3] = HOLDER_ORIGIN
    return m
