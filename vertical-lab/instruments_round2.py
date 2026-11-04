"""Round 2's equipment doing its job, with the insides showing (#303, PR #320): the Opentrons OT-2's gantry and pipette
over its deck, the Bambu Lab H2D and A1 mini printing a part, the CubXL's pipette over its rack, and the multi-doser
dosing into a vial drawn in half section. ``tour.py`` plays each one, like the round-3 and round-4 instruments:

    xvfb-run -a python3 tour.py ot2 h2d a1_mini cubxl_lh multidoser   # -> out/instruments/<key>.gif, .png; out/mp4/...
    python3 tour.py still h2d                                            # the end of every action -> /tmp/still_h2d.png

Each is an ``instruments.Instrument``: named pieces (``body`` stays put), a ``Joint`` per moving piece and an
``actions`` script. What is around each process is drawn see-through while it runs (a piece's ``~`` value in the
actions, as ``alloy_workflow.py`` ghosts the depowdering box and the MIDI's shell), and liquid, powder and printed
parts grow with ``grow()``, a ``follow`` joint that stretches a piece upward from its base. A machine whose motion
isn't rigid pieces (the doser's chain) can name its own clip function in ``TOURS``; tour.py calls it instead of
``tour_one``.

The models are round 2's (``lab_models/equipment.py``, ``lab_models/vendor.py``, ``carousel.py``), split into the
pieces that move; nothing here changes how round 2's scenes draw them. Frame, as in ``instruments.py``: x to the
right and y away from you when you face the front, z up from the bench, origin at the centre of the footprint, mm.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np

from instruments import Instrument, Joint, _piece, _xcyl, _ycyl  # noqa: F401

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))
from common import Model, box, cyl, hose, rbox, tube  # noqa: E402,F401

# files the builds read besides this one and tour.py's common sources: tour.load() re-tessellates when they change
SOURCES = ["lab_models/equipment.py", "lab_models/vendor.py", "lab_models/labware.py", "carousel.py",
           "multidoser/layout.py", "multidoser/parts.py", "multidoser/params.py", "multidoser/kinematics.py"]

# name: (r, g, b, opacity, specular), merged into tour.MATS
MATERIALS = {
    "r2_petg_blue": (0.16, 0.42, 0.80, 1.0, 0.35),      # the part printing on the H2D
    "r2_pla_orange": (0.95, 0.50, 0.12, 1.0, 0.30),     # the part printing on the A1 mini
    "r2_pla_green": (0.20, 0.62, 0.32, 1.0, 0.30),
    "r2_liquid": (0.30, 0.58, 0.92, 0.80, 0.6),         # the liquid in a half-section vial
    "r2_liquid_cut": (0.22, 0.48, 0.85, 1.0, 0.4),
    "r2_powder": (0.66, 0.66, 0.70, 1.0, 0.1),          # a grey metal powder
    "r2_glass_cut": (0.80, 0.90, 0.95, 0.45, 0.9),      # a vial's glass, cut in half
    "r2_tip": (0.90, 0.91, 0.88, 0.70, 0.4),            # a polypropylene pipette tip
    "r2_hot": (1.00, 0.42, 0.08, 1.0, 0.1),             # a hot nozzle tip
}


# ===================================================================================================== helpers
def split(model: Model, inst: Instrument, groups: dict, drop=()) -> None:
    """Hand a lab_models Model's parts to the instrument's pieces: groups = {piece: (part names)}; every other part
    goes to "body", and parts named in `drop` are left out."""
    owner = {n: piece for piece, names in groups.items() for n in names}
    for part in model.parts:
        if part.name in drop:
            continue
        _piece(inst, owner.get(part.name, "body")).parts.append(part)


def grow(z0: float, h0: float, h1: float, parent: str | None = None, v0: float = 0.0) -> Joint:
    """A follow joint that stretches a piece modelled from z0 to z0 + h0 so it reaches z0 + h1 at v = 1: a liquid
    level, a powder heap or a printed part (a prism, so stretching it is the same as adding layers). Below v = 0 it
    shrinks back, to zero height at v = -h0 / (h1 - h0)."""
    k = h1 / h0 - 1.0
    zero = [[0.0] * 4 for _ in range(3)]
    jz = [[0.0] * 4, [0.0] * 4, [0.0, 0.0, k, -k * z0]]
    return Joint("follow", vec=(0.0, 0.0, 1.0), jac=(zero, zero, jz), parent=parent, v0=v0)


def trace(path, axis: int, parent: str | None = None) -> Joint:
    """A follow joint that moves a piece along one axis (0 x, 1 y, 2 z) of a path's offsets, in step with a "path"
    joint on the same waypoints: a CoreXY gantry following its toolhead in y, a bed slinger's bed in y."""
    zero = [[0.0] * 4 for _ in range(3)]
    jac = [list(map(list, zero)) for _ in range(3)]
    jac[axis][axis][3] = 1.0
    return Joint("follow", path=tuple(tuple(p) for p in path), jac=tuple(tuple(map(tuple, j)) for j in jac),
                 parent=parent)


def loops(x0, x1, y0, y1, n: int, start=(0.0, 0.0), z=0.0) -> tuple:
    """Waypoints from `start` to the corner (x0, y0), n times round the rectangle, and back to `start`."""
    pts = [(start[0], start[1], z)]
    for _ in range(n):
        pts += [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    pts += [(x0, y0, z), (start[0], start[1], z)]
    return tuple(pts)


def half(shape, y: float = 0.0, keep_back: bool = True):
    """The back half (y >= `y`) of a CadQuery shape, so a camera in front sees its section."""
    big = 5000.0
    cutter = box(-big, y - big if keep_back else y, -big, big, y if keep_back else y + big, big)
    return shape.cut(cutter)


# ===================================================================================================== Opentrons OT-2
def ot2() -> Instrument:
    """The OT-2 from Opentrons' reference STEP (lab_models/vendor.py), its gantry and pipette split out by bounding
    box so they move over the deck."""
    raise FileNotFoundError("ot2: not built yet")


# ===================================================================================================== Bambu Lab H2D
def h2d() -> Instrument:
    raise FileNotFoundError("h2d: not built yet")


# ===================================================================================================== Bambu Lab A1 mini
def a1_mini() -> Instrument:
    raise FileNotFoundError("a1_mini: not built yet")


# ===================================================================================================== CubXL, liquid handling
def cubxl_lh() -> Instrument:
    raise FileNotFoundError("cubxl_lh: not built yet")


# ===================================================================================================== the multi-doser
# The chain carousel v2 is powder-doser PR #185's own CAD and kinematics at 1c135e0 (carousel.py, multidoser/): every
# frame of its clip is layout.placements(State(...)), so the chain indexes, the P16 docks, the station tilts and the
# auger turns as the doser's own do. The dose follows powder-doser's protocol (cad/chain-carousel-v2/README.md: dock,
# tilt 30°, dose, hold 0.5 s, tilt back, reverse the auger one revolution at rest, undock), in salt, the rig's test
# powder (TEST-PLAN.md T6c, T8):
# * 105 mg a revolution: the lab rig's salt yield through the auger's Ø3 mm exit, which PR #180's real-size DEM twin
#   matched (cad/paternoster/sim/AUGER-SIM.md). Five revolutions at 60 rpm (T6c doses at 30 and 60 rpm) give 0.525 g.
# * The solenoid taps at 2 Hz while the auger turns (AUGER-SIM.md's taps: 4 N for 10 ms at 2 Hz). layout.py doesn't
#   move the plunger (State.tap is multiplied by 0), so the taps show only as a count.
# * The heap is a cone at salt's angle of repose, 32-35° (AUGER-SIM.md; 34° here), rounded at the top, holding the
#   dose at a poured bulk density of 1.2 g/cm³ (assumed); once it reaches the vial's 25.2 mm bore it rises as a layer.
#   0.525 g makes a heap about 17 mm across and 5 mm high. It is re-meshed (charge.lathe) every frame.
# The rig's vial is carousel.SKIP's; the vial, its cup and the catch funnel are drawn here, whole and cut in half.
MD_MODULE = 5                          # module 6, as round 2's workflow (animate.MODULE)
MD_REVS, MD_RPM = 5.0, 60.0
MD_MG_PER_REV = 105.0
MD_TAP_HZ = 2.0
MD_BULK = 1.2                          # g/cm³ = mg/mm³, poured salt (assumed)
MD_REPOSE = 34.0                       # deg
MD_WALL = 1.4                          # the rig's vial (multidoser/parts.py vial()): 28 x 61 mm, 1.4 mm wall and floor
MD_OWN = frozenset({"vial_cup", "vial_funnel"})      # left out of the Carousel's actors, drawn here
MD_GRAVITY = 9810.0                    # mm/s²


def _md_rest(C) -> tuple:
    """({colour: mesh}, lo, hi) of the rig at rest (chain at home, carriage lowered, level), rig frame, as
    carousel.Carousel draws it: the rig's own vial left out (carousel.SKIP) and its electronics board alongside the
    frame, turned 90° (carousel.board_move). lo, hi: the corners of the frame alone, without the board."""
    import pyvista as pv
    parts = C.part_meshes()
    pl = C.CL.placements(C.CL.State(shift=0.0, ext=0.0))
    board = C.board_move(pl)
    by: dict = {}
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    for p in pl:
        if p.key in C.SKIP:
            continue
        m = board @ p.M if p.group == "elec" else p.M
        mesh = parts[p.key].copy()
        mesh.points = mesh.points @ m[:3, :3].T + m[:3, 3]
        by.setdefault(tuple(round(float(c), 3) for c in p.color), []).append(mesh)
        if p.group != "elec":
            lo, hi = np.minimum(lo, mesh.points.min(0)), np.maximum(hi, mesh.points.max(0))
    return {col: pv.merge(ms, merge_points=False) for col, ms in by.items()}, lo, hi


def _md_frame(lo, hi) -> np.ndarray:
    """Rig frame -> the instrument's: turned 180° about z, so the rig's open +y side, where the station shows, is the
    front and the electronics board stands behind; the footprint centred on the origin."""
    m = np.diag([-1.0, -1.0, 1.0, 1.0])
    m[:3, 3] = m[:3, :3] @ -np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0.0])
    return m


def _md_vial_profile() -> list:
    """(r, z) of the rig's 20 mL vial (parts.py vial()), base at z = 0, for charge.lathe."""
    import carousel as C
    r, t, h = C.VIAL_R, MD_WALL, C.VIAL_H
    return [(0.0, 0.0), (r, 0.0), (r, h), (r - t, h), (r - t, t), (0.0, t)]


def _md_heap_shape(s: float) -> float:
    """The heap's height over its sharp cone's (k r), at s = rho / r: the cone's flank, rounded over the top quarter."""
    return 0.875 - 2.0 * s * s if s < 0.25 else 1.0 - s


def _md_heap_flank(mg: float) -> list:
    """(r, z) of the surface of the salt heap holding `mg` milligrams, from its foot to the axis, over the vial's
    floor ([] while it is empty)."""
    import carousel as C
    if mg < 0.5:
        return []
    v = mg / MD_BULK                                      # mm³
    k = math.tan(math.radians(MD_REPOSE))
    big = C.VIAL_R - MD_WALL - 0.05                       # the bore, just clear of the glass
    g = 0.166016                                          # integral of s * _md_heap_shape(s) over 0-1
    r = (v / (2 * math.pi * k * g)) ** (1 / 3)
    layer = 0.0
    if r > big:
        r = big
        layer = (v - 2 * math.pi * k * g * r ** 3) / (math.pi * r * r)
    ss = (1.0, 0.8, 0.6, 0.45, 0.33, 0.25, 0.18, 0.11, 0.05, 0.0)
    return [(s * r, layer + k * r * _md_heap_shape(s)) for s in ss]


def _md_heap_profile(mg: float):
    """The heap's closed (r, z) profile for charge.lathe (None while it is empty)."""
    flank = _md_heap_flank(mg)
    if not flank:
        return None
    return [(0.0, 0.0)] + ([(flank[0][0], 0.0)] if flank[0][1] > 0.01 else []) + flank


def _md_heap_top(mg: float, rho: float = 0.0) -> float:
    """Height of the heap's surface over the vial's floor, rho from the axis."""
    flank = _md_heap_flank(mg)
    if not flank:
        return 0.0
    return float(np.interp(rho, [p[0] for p in flank[::-1]], [p[1] for p in flank[::-1]]))


def _md_cut(CL, key: str, m: np.ndarray):
    """A station part (the vial's cup, the catch funnel) where the rig places it, cut in half: the rig's -y half kept,
    so the camera on its +y side sees the section."""
    import lab
    w = half(cq.Workplane("XY").add(CL.moved(key, m)), y=CL.STATION_Y, keep_back=False)
    vals = w.vals()
    return lab.to_mesh(vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals), 0.1, 0.2)


def _md_stream(t: float, t0: float, t1: float, top_mg: float) -> np.ndarray:
    """The dose in flight at time t, rig frame: grains leave the auger's outlet from t0 to t1, fall onto the catch
    funnel's cone by its D-cut flat, slide down it to the spout and fall from there onto the heap in the vial."""
    import carousel as C
    CL = C.CL
    ex = np.asarray(CL.exit_point(C.TILT), float)
    seat = C.vial_seat()
    f = CL.FUNNEL
    rs, rt = f["spout_d"] / 2, f["top_d"] / 2
    r_hit = math.hypot(ex[0] - seat[0], ex[1] - seat[1])
    z_hit = CL.FUNNEL_SPOUT_Z + (r_hit - rs) / (rt - rs) * f["h"] + 0.6
    d1 = math.sqrt(2 * (ex[2] - z_hit) / MD_GRAVITY)                       # the free fall onto the cone
    lip = np.array([seat[0] + rs - 0.8, seat[1], CL.FUNNEL_SPOUT_Z + 0.5])
    hit = np.array([ex[0], ex[1], z_hit])
    v_slide = 160.0                                                         # mm/s down the cone (assumed)
    d2 = float(np.linalg.norm(lip - hit)) / v_slide
    floor = seat[2] + MD_WALL
    land = np.array([seat[0] + 1.5, seat[1], floor + _md_heap_top(top_mg, 1.5) + 0.4])
    v0 = v_slide * (lip[2] - hit[2]) / max(float(np.linalg.norm(lip - hit)), 1e-6)   # downward, negative
    dz = lip[2] - land[2]
    d3 = (v0 + math.sqrt(v0 * v0 + 2 * MD_GRAVITY * dz)) / MD_GRAVITY
    rng = np.random.default_rng(7)
    dtau = 0.0025
    n = int((t1 - t0) / dtau)
    tau = t0 + (np.arange(n) + rng.random(n)) * dtau
    jit = rng.normal(0.0, 0.45, (n, 2))
    a = t - tau
    pts = []
    for i in np.nonzero((a >= 0) & (a <= d1 + d2 + d3))[0]:
        ai = a[i]
        if ai < d1:
            p = np.array([ex[0], ex[1], ex[2] - 0.5 * MD_GRAVITY * ai * ai])
        elif ai < d1 + d2:
            p = hit + (lip - hit) * (ai - d1) / d2
        else:
            s = ai - d1 - d2
            p = np.array([lip[0] + (land[0] - lip[0]) * min(s / d3, 1.0), lip[1],
                          lip[2] + v0 * s - 0.5 * MD_GRAVITY * s * s])
            p[2] = max(p[2], land[2])
        pts.append(p + (jit[i, 0], jit[i, 1], 0.0))
    return np.array(pts) if pts else np.zeros((0, 3))


def multidoser() -> Instrument:
    """The chain carousel v2 (carousel.py): its own layout.placements(State(...)), the dose in half section. The
    pieces are meshes, the rig at rest as carousel.Carousel draws it, so bbox() is the rig's; multidoser_tour plays
    it from the doser's own kinematics."""
    import carousel as C
    import charge
    rest, rig_lo, rig_hi = _md_rest(C)
    lo = np.min([m.bounds[::2] for m in rest.values()], axis=0)
    hi = np.max([m.bounds[1::2] for m in rest.values()], axis=0)
    frame = _md_frame(lo, hi)
    w, d, h = (float(v) for v in hi - lo)
    inst = Instrument(
        "multidoser", "Multi-doser, 13 powder modules", "the lab's chain carousel v2 (powder-doser PR #185)",
        (round(w), round(d), round(h)),
        f"powder-doser {C.SHA[:7]} (PR #185's head), cad/chain-carousel-v2: its own CAD, layout and kinematics, "
        "verbatim in multidoser/, and its three reference STEPs, hash-checked (carousel.py)")
    body = [(m.transform(frame, inplace=False), col, 1.0) for col, m in rest.items()]
    glass = MATERIALS["r2_md_glass"]
    vial = charge.lathe(_md_vial_profile()).translate(C.vial_seat(), inplace=False).transform(frame, inplace=False)
    body.append((vial, glass[:3], glass[3]))
    inst.meshes["body"] = body
    inst.md_frame = frame                    # rig frame -> this one: multidoser_tour draws the Carousel through it
    corners = np.array([[x, y, z, 1.0] for x in (rig_lo[0], rig_hi[0]) for y in (rig_lo[1], rig_hi[1])
                        for z in (rig_lo[2], rig_hi[2])]) @ frame.T
    inst.md_rig_bb = tuple(float(v) for pair in zip(corners.min(0)[:3], corners.max(0)[:3]) for v in pair)
    inst.notes = [
        f"{w:.0f} x {d:.0f} x {h:.0f} mm from its own placements: the frame on its levelling feet and the electronics "
        "board alongside it, turned 90°, as on tray B. 731 mm is 3.5 mm over Kardex's 727.5 mm product height.",
        f"The dose: {MD_REVS:.0f} auger revolutions at {MD_RPM:.0f} rpm of salt at {MD_MG_PER_REV:.0f} mg a "
        f"revolution (the rig's salt yield, powder-doser AUGER-SIM.md), {MD_REVS * MD_MG_PER_REV / 1000:.3f} g; "
        "hold 0.5 s, tilt back, one reverse revolution at rest (powder-doser's dose protocol).",
    ]
    return inst


def multidoser_tour(inst: Instrument, entries: dict) -> str:
    """The multi-doser's clip, which tour.tour_one can't play (the chain moves by its own kinematics, not as rigid
    pieces): the chain indexes module 6 to the station, the P16 docks it, the station tilts it 30° and the auger doses
    0.525 g of salt into the 20 mL vial, drawn cut in half with its cup and funnel so the heap shows; the hold, the tilt
    back, one reverse turn at rest and the undock. The other modules fade while the docked one works.
    -> out/instruments/multidoser.gif, .png, .json; out/mp4/instruments/multidoser.mp4."""
    import carousel as C
    import charge
    import pyvista as pv
    import tour
    from PIL import Image
    from scene import OUT, R, Scene, T, window

    CL = C.CL
    out = OUT / "instruments"
    out.mkdir(parents=True, exist_ok=True)
    (OUT / "mp4" / "instruments").mkdir(parents=True, exist_ok=True)
    sc = Scene(f"instruments/{inst.key}", f"{inst.title}: {inst.model}")
    sc.intro = 0.6
    bb = inst.bbox()
    tour.studio(sc, shadow_of=bb)
    frame = np.asarray(inst.md_frame, float)

    def at(p) -> tuple:                      # rig frame -> the scene's
        return tuple((frame @ np.r_[np.asarray(p, float), 1.0])[:3])

    # ------------------------------------------------------------------ the rig, its vial, cup, funnel, heap, stream
    parts = C.part_meshes()                  # cached with carousel's own SKIP before it is widened below
    skip = C.SKIP
    C.SKIP = skip | MD_OWN
    try:
        car = C.Carousel(sc, "md", prefix="md", highlight=MD_MODULE, shift=0.0, ext=0.0)
    finally:
        C.SKIP = skip
    sc.gmat["md"] = frame
    pl = {p.key: p for p in CL.placements(CL.State(shift=0.0, ext=0.0))}
    for key in sorted(MD_OWN):
        p = pl[key]
        whole = parts[key].copy()
        whole.points = whole.points @ p.M[:3, :3].T + p.M[:3, 3]
        sc.add(f"md_own/{key}", whole, p.color, "md", specular=0.3)
        sc.add(f"md_own/{key}_cut", _md_cut(CL, key, p.M), p.color, "md", specular=0.3, shown=False)
    seat = C.vial_seat()
    # turned 180°: lathe(cut=True) keeps +y, and the camera is on the rig's +y side; 0.1 mm up, clear of the cup's floor
    sc.gmat["md_vial"] = T(seat + (0, 0, 0.1)) @ R((0, 0, 1), 180.0)
    sc.parent["md_vial"] = "md"
    glass = MATERIALS["r2_md_glass"]
    for name, cut in (("whole", False), ("cut", True)):
        sc.add(f"md_vial/{name}", charge.lathe(_md_vial_profile(), cut=cut), glass[:3], "md_vial", opacity=glass[3],
               specular=glass[4], shown=not cut)
    sc.gmat["md_heap"] = T((0, 0, MD_WALL + 0.05))
    sc.parent["md_heap"] = "md_vial"
    salt = MATERIALS["r2_salt"]
    sc.add("md_heap/salt", charge.lathe([(0, 0), (1, 0), (0, 1)], cut=True), salt[:3], "md_heap", specular=salt[4],
           shown=False)
    grain = MATERIALS["r2_salt_grain"]
    sc.add("md_stream/salt", pv.PolyData(np.zeros((1, 3))), grain[:3], "md", shown=False, style="points",
           point_size=5.0, render_points_as_spheres=True, specular=grain[4])

    st = dict(cut=0.0, mg=0.0, turns="at rest", taps=0)

    def heap():
        prof = _md_heap_profile(st["mg"])
        sc.alpha["md_heap/salt"] = 0.0 if prof is None else 1.0
        if prof is not None:
            sc.set_mesh("md_heap/salt", charge.lathe(prof, cut=st["cut"] >= 0.5, res=64))

    def gauges():
        sc.gauges = [("Tilt", f"{car.state['tilt']:.0f}°"), ("Auger", st["turns"]),
                     ("Solenoid", f"{st['taps']} taps at {MD_TAP_HZ:.0f} Hz" if st["taps"] else "off"),
                     ("Load cell", f"{st['mg'] / 1000:.3f} g")]

    def cutaway(f1: float):
        """An update(u): the vial, its cup and the funnel from whole to cut in half (f1 = 1) or back."""
        f0 = st["cut"]

        def up(u):
            f = f0 + (f1 - f0) * window(u, 0.0, 0.35)
            st["cut"] = f
            for a, b in (("md_vial/whole", "md_vial/cut"), *((f"md_own/{k}", f"md_own/{k}_cut") for k in MD_OWN)):
                sc.alpha[a], sc.alpha[b] = 1.0 - f, f
            heap()
        return up

    def both(*fs):
        def up(u):
            for f_ in fs:
                if f_ is not None:
                    f_(u)
            gauges()
        return up

    def unease(e: float) -> float:          # u for e = ease(u): the dose runs at a constant rate in time
        return 0.5 - math.sin(math.asin(1.0 - 2.0 * min(max(e, 0.0), 1.0)) / 3.0)

    # ------------------------------------------------------------------ cameras and labels (the scene's frame)
    ex = np.array(at(car.exit_point()))
    vs = np.array(at(seat))
    # the whole rig framed on its frame (the board stands behind it), the station's side square to the camera
    whole_cam = tour.frame_cam(inst.md_rig_bb, inst.cam, pad=0.92, look_z=0.46)
    mid_cam = tour.close_cam(at((50.0, CL.STATION_Y, 325.0)), 480.0, (0.18, -1.0, 0.28))
    dose_cam = tour.close_cam(np.r_[0.3 * ex[:2] + 0.7 * vs[:2], 291.0], 215.0, (-0.12, -1.0, 0.26))
    heap_cam = tour.close_cam(np.r_[0.15 * ex[:2] + 0.85 * vs[:2], 280.0], 150.0, (-0.12, -1.0, 0.26))
    nema = pl["nema34"].M[:3, 3]
    estop = (car.board @ np.r_[pl["estop"].M[:3, 3], 1.0])[:3]
    act = CL.actuator_pins(0.0, C.DOCK_EXT)
    carriage = CL.to_world(CL.electronics_frame(0.0, C.DOCK_EXT), (40.0, 0.0, -45.0))
    L_station = ("dosing station", at(CL.HINGE_STATION + np.array([0.0, 0.0, -60.0])), (0.80, 0.62))
    L_drive = ("NEMA 34: drives both chains", at(nema), (0.16, 0.66))
    L_loop = ("13 modules on two #35 chains", at((CL.CHAIN_L / 2, CL.STATION_Y, 560.0)), (0.80, 0.22))
    L_board = ("electronics board, behind", at(estop + np.array([0.0, 0.0, 25.0])), (0.80, 0.80))
    L_act = ("Actuonix P16 actuator", at((act[0] + act[1]) / 2), (0.18, 0.74))
    L_carr = ("electronics carriage:\nNEMA 11, pinion, solenoid,\ndock magnet", at(carriage), (0.84, 0.30))
    L_mod = (f"module {MD_MODULE + 1}: auger in its plate", at(CL.to_world(CL.sam_frame(CL.station_frame(), C.TILT),
                                                                         (70.0, 0.0, 0.0))), (0.20, 0.18))
    L_vial = ("20 mL vial, cut in half", at(seat + np.array([0.0, 0.0, 40.0])), (0.84, 0.62))
    L_funnel = ("catch funnel (D-cut), cut in half", at((seat[0], seat[1], CL.FUNNEL_TOP - 8.0)), (0.84, 0.46))
    below_spout = (seat[0] + 6.5, seat[1], CL.FUNNEL_SPOUT_Z - 9.0)          # in the stream, under the spout
    L_fall = ("salt from the Ø3 mm outlet,\nthrough the funnel", at(below_spout), (0.84, 0.24))
    L_heap = ("salt heap, cut in half", at(seat + np.array([0.0, 0.0, MD_WALL + 2.0])), (0.84, 0.66))
    L_lc = ("vial cup on the 100 g load cell", at((seat[0], seat[1] - 15.5, CL.CUP_Z + 17.0)), (0.16, 0.56))

    # ------------------------------------------------------------------ the clip
    n = 6
    sc.cam = whole_cam
    gauges()
    mod = MD_MODULE + 1
    cap = (f"Thirteen powder modules ride two #35 roller chains. The chain indexes module {mod} (green) to the dosing "
           f"station on the bottom run, 8 links (76.2 mm) per module.")
    sc.step(f"1/{n}", cap, 3.2, both(car.to(shift=car.index_to(MD_MODULE))), hold=0.5,
            labels=[L_loop, L_station, L_drive, L_board])
    cap = (f"An Actuonix P16 lifts the electronics carriage up to module {mod}'s plate, and the dock magnet holds the "
           "auger's 44T gear in mesh with the steel 20T pinion. The other modules fade out.")
    sc.step(f"2/{n}", cap, 2.4, both(car.to(ext=C.DOCK_EXT, magnet_on=True), car.ghost(0.16), cutaway(1.0)), hold=0.5,
            labels=[L_act, L_carr], cam_to=mid_cam)
    cap = ("The station tilts the module 30°, cap end up, about a hinge through the auger's outlet. The vial, its cup "
           "and the catch funnel are drawn cut in half.")
    sc.step(f"3/{n}", cap, 2.0, both(car.to(tilt=C.TILT)), hold=0.5, labels=[L_mod, L_funnel, L_vial])
    # the dose, in real time: 5 turns at 60 rpm, taps at 2 Hz, then powder-doser's 0.5 s hold for the tail. The camera
    # moves in to the funnel and the vial over its first 1.2 s, and down to the heap from 2.4 s to 4.4 s.
    t_on, t_run = 0.25, MD_REVS * 60.0 / MD_RPM
    secs = t_on + t_run + 0.75
    transit = 0.27                                            # outlet to heap, s (the stream's own timing)
    spin0 = car.state["spin"]
    dose_mg = MD_REVS * MD_MG_PER_REV
    cam0 = [np.array(v, float) for v in sc.cam]

    def lerp(c0, c1, k):
        return [np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * k for a, b in zip(c0, c1)]

    def dose(e):
        t = unease(e) * secs
        cam = lerp(lerp(cam0, dose_cam, window(t / 1.2, 0.0, 1.0)), heap_cam, window((t - 2.4) / 2.0, 0.0, 1.0))
        sc.cam = [tuple(v) for v in cam]
        a = min(max((t - t_on) / t_run, 0.0), 1.0)
        on = 0.0 < a < 1.0
        tap = 2.0 if on and (t - t_on) * MD_TAP_HZ % 1.0 < 0.15 else 0.0
        car.set(spin=spin0 + 2 * math.pi * MD_REVS * a, tap=tap)
        st["turns"] = f"{MD_REVS * a:.1f} turns at {MD_RPM:.0f} rpm" if a < 1.0 else f"{MD_REVS:.0f} turns, stopped"
        st["taps"] = int(min(max(t - t_on, 0.0), t_run) * MD_TAP_HZ + (1 if t > t_on else 0))
        st["mg"] = dose_mg * min(max((t - t_on - transit) / t_run, 0.0), 1.0)
        pts = _md_stream(t, t_on, t_on + t_run, st["mg"])
        sc.alpha["md_stream/salt"] = 1.0 if len(pts) else 0.0
        if len(pts):
            sc.set_mesh("md_stream/salt", pv.PolyData(pts))
        heap()

    cap = (f"The NEMA 11 turns the auger {MD_REVS:.0f} times through the pinion while the solenoid taps the tube. Salt "
           f"leaves the outlet at {MD_MG_PER_REV:.0f} mg a turn and falls through the funnel into the vial, on its "
           f"100 g load cell: {dose_mg / 1000:.3f} g.")
    sc.step(f"4/{n}", cap, secs, both(dose), hold=0.5, labels=[L_fall, L_heap, L_lc])
    sc.alpha["md_stream/salt"] = 0.0
    spin1, tilt1 = car.state["spin"], car.state["tilt"]

    def settle(u):                          # tilt back, then one reverse turn at rest
        back = window(u, 0.62, 1.0)
        car.set(tilt=tilt1 * (1.0 - window(u, 0.0, 0.55)), spin=spin1 - 2 * math.pi * back)
        st["turns"] = f"{back:.1f} turn back" if back > 0.005 else f"{MD_REVS:.0f} turns, stopped"
        st["taps"] = 0

    cap = ("After a 0.5 s hold for the tail of the dose, the module tilts back and the auger turns back once at rest, "
           "which draws the powder back from the outlet.")
    sc.step(f"5/{n}", cap, 2.8, both(settle), hold=0.5, labels=[L_mod, L_vial], cam_to=mid_cam)
    st["turns"] = "at rest"
    cap = (f"The carriage drops away and the magnet lets go, so module {mod} rides on with the chain. The vial holds "
           f"{dose_mg / 1000:.3f} g of salt.")
    sc.step(f"6/{n}", cap, 2.6, both(car.to(ext=0.0, magnet_on=False), car.ghost(1.0), cutaway(0.0)), hold=0.5,
            labels=[L_station, L_drive], cam_to=whole_cam)
    # the hero still for the gallery: at rest, every module solid, the vial whole with its dose; no text
    img = sc.render_base()
    Image.fromarray(img).save(out / f"{inst.key}.png", optimize=True)
    return sc.save()


MATERIALS.update({
    "r2_md_glass": (0.75, 0.88, 0.95, 0.28, 0.9),     # the multi-doser's vial (layout.GLASS), thin so the dose shows
    "r2_salt": (0.93, 0.93, 0.90, 1.0, 0.1),          # the salt heap in the multi-doser's vial
    "r2_salt_grain": (0.58, 0.58, 0.56, 1.0, 0.1),    # salt in flight: darker, so single grains show on white
})


# {key: name of a function here, (inst, entries) -> str}: a clip tour.tour_one can't play; tour.py calls it instead
TOURS: dict[str, str] = {"multidoser": "multidoser_tour"}

REGISTRY = {"ot2": ot2, "h2d": h2d, "a1_mini": a1_mini, "cubxl_lh": cubxl_lh, "multidoser": multidoser}
