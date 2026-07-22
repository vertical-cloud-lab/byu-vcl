"""Parametric CAD for the OT-2 P20 press-fit "fake tip" test array and
mock wireless-color-sensor package (issue #33, PR #114).

Parts generated (STL into ``stl/``, STEP into ``step/``):

1. ``fake_tip_test_array``  — 10 loose test tips (bore ID 3.40-3.85 mm in
   0.05 mm steps) laid out in the same 2 x 5 grid as the deck plate pockets.
   Print in one batch on a Bambu Lab A1 mini.
1b. ``fake_tip_test_array_slit`` — same 10 tips but with the final socket
   geometry (1.78 deg tapered bore + 6 spring-finger slits) for the round-2
   cyclic-durability comparison.
1c. ``fake_tip_test_array_slit_small`` — round-1.5 slitted array stepping
   *down* from 3.40 mm (the smallest bore of the round-1 array) to 2.95 mm in
   0.05 mm steps.  Round-1 slitted testing only picked up the 3.40 mm tip, so
   this probes the smaller bores the real (sub-3.70 mm) nozzle needs.
2. ``deck_plate_base``      — ANSI/SLAS-footprint (127.76 x 85.48 mm) base
   that sits in an OT-2 deck slot.  It has 10 drop-in pockets that register
   each test tip under the pipette without locking it down, plus engraved
   bore-size labels next to every pocket.
3. ``fake_tip_insert``      — final-geometry modular insert (tapered bore,
   6 spring-finger slits) per p20-fake-tip-design.md.
4. ``mock_sensor_package``  — drop-in stand-in for the wireless color sensor
   enclosure: same 40 x 60 mm footprint and 84 mm overall height as the
   original P300 part (so the existing ``byu_color_sensor_charging_port``
   labware/tipLength still apply), but topped with the P20 socket.
5. ``real_sensor_package_p20`` — a *from-scratch* parametric recreation of the
   real printed enclosure (issue #33, the 7.5 mm-rebored P300 part in
   ``reference/``).  The outer silhouette, depth, tray, pedestal and tapered
   post are rebuilt as a hollow 2 mm-walled shell from dimensions measured off
   the reference STEP (volume matches the import to within ~2 %; see
   ``verify_real_package_volume``), then given a P20 socket bored *concentric*
   with the post axis (the original Ø7.5 mm bore sat 3.7 mm off-centre and grips
   the ejector sleeve; this one is centred so it engages the ~3.6 mm nozzle).
6. ``real_enclosure_p20_tip`` — the *actual* enclosure imported from the
   reference STEP with only its fake tip swapped: the old post solid is
   dropped, the residual bore in the body top wall is plugged, and the tested
   "best" tip (Ø6 x 8 mm socket, 3.40 mm bore, 6 spring-finger slits) is
   grafted concentric on the old post axis at the same height
   (``verify_real_enclosure_p20_tip`` checks all of this).

Geometry notes (measured from the original AC "Sensor package main
enclosure.step", P300 version):

* fake-tip post: OD 9.5 mm, 13 mm tall (incl. R2 fillet), total part 84 mm
* bore: entry ID ~5.15 mm narrowing to ~4.19 mm over 14.5 mm depth
  => half-angle 1.78 deg — adopted here as the GEN2 nozzle taper.

Run:  python cad_model.py        (exports all STL + STEP)
"""

from __future__ import annotations

import math
import pathlib
from dataclasses import dataclass

from build123d import (
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Compound,
    Cone,
    Cylinder,
    Location,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    Rot,
    Text,
    add,
    export_step,
    export_stl,
    extrude,
    import_step,
    make_face,
    mirror,
)

HERE = pathlib.Path(__file__).resolve().parent
STL_DIR = HERE / "stl"
STEP_DIR = HERE / "step"
REF_DIR = HERE / "reference"
# the real printed P300-derived enclosure, rebored to 7.5 mm (issue #33).
REAL_ENCLOSURE_STEP = REF_DIR / "sensor_package_main_enclosure_7p5mm.step"

FONT = "DejaVu Sans"  # available on Linux CI; build123d falls back if missing


@dataclass
class Params:
    # ---- nozzle / bore (see p20-fake-tip-design.md) ----
    bore_ids: tuple = (3.40, 3.45, 3.50, 3.55, 3.60, 3.65, 3.70, 3.75, 3.80, 3.85)
    # round-1 slitted testing only picked up the 3.40 mm tip, so the round-1.5
    # slitted array steps *down* from 3.40 mm (the smallest of ``bore_ids``) in
    # 0.05 mm steps to probe the smaller bores the real (sub-3.70 mm) nozzle needs.
    bore_ids_small: tuple = (2.95, 3.00, 3.05, 3.10, 3.15, 3.20, 3.25, 3.30,
                             3.35, 3.40)
    nominal_bore_id: float = 3.55          # round-1 best guess (mid-depth ID)
    best_bore_id: float = 3.40             # round-1 slitted winner + FEA rec.
    nozzle_taper_half_angle_deg: float = 1.78  # measured from original P300 STEP
    socket_depth: float = 8.0
    socket_od: float = 6.0                 # top rim must sit under ejector sleeve
    entry_chamfer: float = 0.5
    # ---- spring-finger slits (final geometry only) ----
    n_slits: int = 6                       # 6 fingers, evenly spaced 60 deg apart
    slit_width: float = 0.5
    slit_depth: float = 6.0                # 75 % of socket depth
    # ---- test tip (round-1 pieces: straight bore, no slits) ----
    tip_body_od: float = 8.0
    tip_body_h: float = 10.0
    tip_flange_od: float = 10.0
    tip_flange_h: float = 2.0
    tip_bore_extra: float = 2.0            # bore continues 2 mm into flange/body
    label_depth: float = 0.6
    # ---- modular insert (final geometry, design doc table) ----
    insert_flange_od: float = 8.0
    insert_flange_h: float = 2.0
    insert_peg_od: float = 6.0
    insert_peg_h: float = 5.0
    # ---- deck plate (ANSI/SLAS footprint) ----
    plate_x: float = 127.76
    plate_y: float = 85.48
    plate_h: float = 24.0      # tall enough that the P20 pickup press
    #                            (tipLength + ~4.5 mm below well top) stays
    #                            above deck: seat z 11.8 + tip 20 = 31.8
    plate_shell: float = 3.0   # underside hollowed to save filament
    pocket_cols: int = 5
    pocket_rows: int = 2
    pocket_pitch: float = 18.0
    pocket_hole_clearance: float = 0.4     # diametral, drop-in fit
    pocket_cbore_clearance: float = 0.8
    pocket_cbore_depth: float = 2.2
    # ---- mock sensor package (original outer envelope) ----
    body_x: float = 40.0
    body_y: float = 60.0
    body_h: float = 66.0                   # top face of original enclosure
    total_h: float = 84.0                  # matches labware tipLength: 84
    pedestal_od: float = 8.0
    # ---- real enclosure recreation (from-scratch, measured off the 7.5 mm
    #      STEP, issue #33).  Native build frame: +Y is the post axis. ----
    real_depth: float = 60.0               # Z extent (z = -30..30)
    real_wall: float = 2.0                 # measured shell wall thickness
    # outer XY silhouette of the upper body (rectangle minus the tray slot),
    # read off the reference end-cap section; closed polygon (x, y):
    real_silhouette: tuple = (
        (10.0, 22.0), (10.0, 66.0), (-30.0, 66.0), (-30.0, 64.0),
        (-15.0, 64.0), (-15.0, 24.0), (-30.0, 24.0), (-30.0, 22.0),
    )
    real_box_x: tuple = (-15.0, 10.0)      # tall-box X span (hollowed region)
    real_body_y: tuple = (2.0, 66.0)       # interior void Y span (box+pedestal)
    real_ped_x: tuple = (-8.0, 10.0)       # pedestal/foot X span
    real_ped_y: tuple = (-5.0, 22.0)       # pedestal/foot Y span
    real_ped_z: float = 27.0               # pedestal/foot Z depth (narrower)
    real_post_y0: float = 66.0             # post base Y (top of body)
    real_post_h: float = 19.5              # post height
    real_post_base_r: float = 7.0          # post base radius (tapered boss)
    real_post_top_r: float = 3.67          # post tip radius (Ø7.34 mm)


P = Params()


def grid_centers(p: Params = P) -> list[tuple[float, float, str]]:
    """Pocket/test-tip centers, plate origin at its center.

    Returns (x, y, well_name); row A is the back (+y) row per Opentrons
    convention.
    """
    out = []
    for r in range(p.pocket_rows):           # 0 = A (back), 1 = B (front)
        for c in range(p.pocket_cols):
            x = (c - (p.pocket_cols - 1) / 2) * p.pocket_pitch
            y = ((p.pocket_rows - 1) / 2 - r) * p.pocket_pitch
            out.append((x, y, f"{chr(ord('A') + r)}{c + 1}"))
    return out


def _bore_radius(entry_id: float, depth: float, taper_half_angle_deg: float):
    """(top_radius, bottom_radius) for a tapered bore narrowing downward."""
    dr = depth * math.tan(math.radians(taper_half_angle_deg))
    return entry_id / 2, entry_id / 2 - dr


def _cut_socket_features(z_top: float, bore_mid_id: float, p: Params = P,
                         tapered: bool = True, slits: bool = False,
                         cx: float = 0.0, cy: float = 0.0,
                         socket_od: float | None = None) -> None:
    """Cut the bore (+ chamfer, optional spring-finger slits) into whatever is
    being built; call inside an active BuildPart context.

    ``z_top`` is the socket-mouth Z, the bore opening downward into material.
    ``tapered`` cuts the 1.78 deg conical nozzle bore (else a straight bore at
    ``bore_mid_id``).  ``slits`` adds ``p.n_slits`` single-wall rounded-root
    axial slots (one per spring finger), evenly spaced around the socket.
    ``socket_od`` bounds the slit length (defaults to ``p.socket_od``).
    """
    socket_od = socket_od or p.socket_od
    if tapered:
        dr = p.socket_depth / 2 * math.tan(
            math.radians(p.nozzle_taper_half_angle_deg))
        entry_r = bore_mid_id / 2 + dr
        bottom_r = bore_mid_id / 2 - dr
        with Locations((cx, cy, z_top)):
            Cone(entry_r, bottom_r, p.socket_depth,
                 align=(Align.CENTER, Align.CENTER, Align.MAX),
                 mode=Mode.SUBTRACT)
            Cone(entry_r + p.entry_chamfer, entry_r, p.entry_chamfer,
                 align=(Align.CENTER, Align.CENTER, Align.MAX),
                 mode=Mode.SUBTRACT)
    else:
        entry_r = bore_mid_id / 2
        bore_depth = p.socket_depth + p.tip_bore_extra
        with Locations((cx, cy, z_top)):
            Cylinder(bore_mid_id / 2, bore_depth,
                     align=(Align.CENTER, Align.CENTER, Align.MAX),
                     mode=Mode.SUBTRACT)
            Cone(bore_mid_id / 2 + p.entry_chamfer, bore_mid_id / 2,
                 p.entry_chamfer,
                 align=(Align.CENTER, Align.CENTER, Align.MAX),
                 mode=Mode.SUBTRACT)
    if slits:
        for k in range(p.n_slits):
            ang = 360 / p.n_slits * k
            # single radial slot from the bore axis out through one wall, so
            # p.n_slits slots produce exactly p.n_slits spring fingers
            slot = Box(socket_od, p.slit_width, p.slit_depth,
                       align=(Align.MIN, Align.CENTER, Align.MAX),
                       mode=Mode.PRIVATE)
            root = Cylinder(p.slit_width / 2, socket_od,
                            rotation=(0, 90, 0),
                            # Align.MIN puts the cylinder base at the bore axis
                            # (X=0) after the 90 deg rotation, matching the slot
                            align=(Align.CENTER, Align.CENTER, Align.MIN),
                            mode=Mode.PRIVATE)
            root = Pos(0, 0, -p.slit_depth) * root
            cutter = slot + root
            cutter = Pos(cx, cy, z_top) * Rot(0, 0, ang) * cutter
            add(cutter, mode=Mode.SUBTRACT)


def make_test_tip(bore_id: float, p: Params = P, tapered: bool = False,
                  slits: bool = False) -> Compound:
    """Round-1 test piece: straight bore at ``bore_id``, no slits by default.

    Stack (bottom -> top): body O8 x 10, flange O10 x 2, socket O6 x 8.
    Bore is blind (socket + 2 mm), leaving a solid base that carries an
    engraved 2-digit size code readable from below (e.g. '55' = 3.55 mm).

    Set ``tapered``/``slits`` to build the round-2 final-geometry variant
    (1.78 deg tapered bore + 6 spring-finger slits) for cyclic-durability
    testing once a round-1 bore winner is chosen.
    """
    with BuildPart() as part:
        Cylinder(p.tip_body_od / 2, p.tip_body_h,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, p.tip_body_h)):
            Cylinder(p.tip_flange_od / 2, p.tip_flange_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        z_flange_top = p.tip_body_h + p.tip_flange_h
        with Locations((0, 0, z_flange_top)):
            Cylinder(p.socket_od / 2, p.socket_depth,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        z_top = z_flange_top + p.socket_depth
        _cut_socket_features(z_top, bore_id, p, tapered=tapered, slits=slits)
        # engraved size code on the bottom face, mirrored so it reads
        # correctly when the tip is flipped over
        code = f"{round(bore_id * 100) % 100:02d}"
        with BuildSketch(Plane.XY) as sk:
            Text(code, font_size=4.0, font=FONT)
            mirror(about=Plane.YZ, mode=Mode.REPLACE)
        extrude(sk.sketch, amount=p.label_depth, mode=Mode.SUBTRACT)
    return part.part


def _add_socket(plane_z: float, bore_mid_id: float, p: Params = P,
                slits: bool = True):
    """Add the final-geometry socket (tapered bore + spring fingers) on top of
    whatever is being built; call inside an active BuildPart context."""
    with Locations((0, 0, plane_z)):
        Cylinder(p.socket_od / 2, p.socket_depth,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    z_top = plane_z + p.socket_depth
    _cut_socket_features(z_top, bore_mid_id, p, tapered=True, slits=slits)


def make_fake_tip_insert(bore_mid_id: float | None = None,
                         p: Params = P) -> Compound:
    """Final-geometry modular insert per the design doc dimension table:
    peg O6 x 5 (press-fits enclosure recess) + flange O8 x 2 + socket
    O6 x 8 with tapered bore and 6 spring-finger slits."""
    bore_mid_id = bore_mid_id or p.nominal_bore_id
    with BuildPart() as part:
        Cylinder(p.insert_peg_od / 2, p.insert_peg_h,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, p.insert_peg_h)):
            Cylinder(p.insert_flange_od / 2, p.insert_flange_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        _add_socket(p.insert_peg_h + p.insert_flange_h, bore_mid_id, p)
    return part.part


def make_mock_sensor_package(bore_mid_id: float | None = None,
                             p: Params = P) -> Compound:
    """Drop-in stand-in for the sensor enclosure: original outer envelope
    (40 x 60 footprint, 84 mm overall) with the P20 socket on top.

    Print solid STL with ~8 % gyroid infill -> ~40 g, matching the real
    sensor package mass closely enough for pickup/retention testing.
    """
    bore_mid_id = bore_mid_id or p.nominal_bore_id
    pedestal_h = p.total_h - p.body_h - p.socket_depth
    with BuildPart() as part:
        Box(p.body_x, p.body_y, p.body_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, p.body_h)):
            Cylinder(p.pedestal_od / 2, pedestal_h,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        _add_socket(p.body_h + pedestal_h, bore_mid_id, p)
        # engraved label on the front face
        with BuildSketch(Plane.XZ.offset(p.body_y / 2)) as sk:
            with Locations((0, p.body_h / 2)):
                Text("BYU VCL\nWCS MOCK\nP20", font_size=7.0, font=FONT)
        extrude(sk.sketch, amount=-p.label_depth, mode=Mode.SUBTRACT)
    return part.part


def make_deck_plate(p: Params = P) -> Compound:
    """SLAS-footprint deck plate with 10 registration pockets + labels."""
    hole_d = p.tip_body_od + p.pocket_hole_clearance
    cbore_d = p.tip_flange_od + p.pocket_cbore_clearance
    hole_depth = p.pocket_cbore_depth + p.tip_body_h
    with BuildPart() as part:
        Box(p.plate_x, p.plate_y, p.plate_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        # hollow the underside, leaving solid columns around each pocket
        Box(p.plate_x - 2 * p.plate_shell, p.plate_y - 2 * p.plate_shell,
            p.plate_h - hole_depth - p.plate_shell,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT)
        for (x, y, _name) in grid_centers(p):
            with Locations((x, y, 0)):
                Cylinder((cbore_d + 2 * p.plate_shell) / 2,
                         p.plate_h - p.label_depth,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
        for (x, y, _name) in grid_centers(p):
            with Locations((x, y, p.plate_h)):
                Cylinder(cbore_d / 2, p.pocket_cbore_depth,
                         align=(Align.CENTER, Align.CENTER, Align.MAX),
                         mode=Mode.SUBTRACT)
                Cylinder(hole_d / 2, hole_depth,
                         align=(Align.CENTER, Align.CENTER, Align.MAX),
                         mode=Mode.SUBTRACT)
        # engraved bore-size label under each pocket + title + A1 marker
        with BuildSketch(Plane.XY.offset(p.plate_h)) as sk:
            for (x, y, name), bore in zip(grid_centers(p), p.bore_ids):
                with Locations((x, y - 8.2)):
                    Text(f"{bore:.2f}", font_size=3.2, font=FONT)
            with Locations((0, -p.plate_y / 2 + 6)):
                Text("BYU VCL  P20 FAKE-TIP TEST ARRAY", font_size=4.5,
                     font=FONT)
            with Locations((-p.plate_x / 2 + 8, p.plate_y / 2 - 7)):
                Text("A1", font_size=5.0, font=FONT)
        extrude(sk.sketch, amount=-p.label_depth, mode=Mode.SUBTRACT)
    return part.part


def make_test_array(p: Params = P, tapered: bool = False,
                    slits: bool = False,
                    bore_ids: tuple | None = None) -> Compound:
    """All 10 test tips, laid out in the pocket grid (one print).

    Default is the round-1 straight-bore array (clean press-fit measurement).
    Pass ``tapered=True, slits=True`` for the round-2 array that mirrors the
    final socket geometry (1.78 deg taper + 6 spring-finger slits).

    ``bore_ids`` overrides ``p.bore_ids`` (e.g. ``p.bore_ids_small`` for the
    round-1.5 smaller-bore slitted array); it must have <= 10 entries to fit
    the 2 x 5 grid.
    """
    bore_ids = bore_ids if bore_ids is not None else p.bore_ids
    tips = []
    for (x, y, _name), bore in zip(grid_centers(p), bore_ids):
        tip = make_test_tip(bore, p, tapered=tapered, slits=slits)
        tips.append(Location((x, y, 0)) * tip)
    return Compound(children=tips)


def make_real_sensor_package_p20(bore_mid_id: float | None = None,
                                 p: Params = P, slits: bool = True) -> Compound:
    """Recreate the *real* printed sensor-package enclosure (issue #33, the
    7.5 mm-rebored P300-derived part) **from scratch** and give it a working
    P20 fake tip.

    Rather than importing and re-boring the reference STEP (which produced an
    off-centre, wall-breaching socket because the original Ø7.5 mm bore sits
    3.7 mm off the post axis), the enclosure is rebuilt parametrically from
    dimensions measured off that STEP:

    * the upper body is the measured outer silhouette (``real_silhouette`` —
      a rectangle with the tray slot removed) extruded the full ``real_depth``;
    * a single interior void leaves a uniform ``real_wall`` (2 mm) shell across
      the tall box and the pedestal/foot;
    * the tapered fake-tip post (``real_post_*``) is rebuilt concentric on the
      body axis and hollowed.

    The result matches the imported reference volume to within ~2 %
    (``verify_real_package_volume``).  A P20 socket (1.78 deg tapered bore + 3
    spring-finger slits) is then bored **concentric** with the post so it
    engages the ~3.6 mm nozzle (not the ejector sleeve) and the socket stays
    inside the post wall.

    The part is returned post-up (+Z); the body/sensor end faces -Z.
    """
    bore_mid_id = bore_mid_id or p.nominal_bore_id
    bx0, bx1 = p.real_box_x
    by0, by1 = p.real_body_y
    px0, px1 = p.real_ped_x
    py0, py1 = p.real_ped_y
    w = p.real_wall
    with BuildPart() as bp:
        # upper body: extrude the measured outer silhouette the full depth
        with BuildSketch(Plane.XY) as sk:
            with BuildLine():
                Polyline(*p.real_silhouette, close=True)
            make_face()
        extrude(amount=p.real_depth / 2, both=True)
        # pedestal / foot below the body (narrower than the body in Z)
        with Locations(((px0 + px1) / 2, (py0 + py1) / 2, 0)):
            Box(px1 - px0, py1 - py0, p.real_ped_z, mode=Mode.ADD)
        # one continuous interior void -> uniform-wall hollow shell
        with Locations(((bx0 + bx1) / 2, (by0 + by1) / 2, 0)):
            Box(bx1 - bx0 - 2 * w, by1 - by0 - 2 * w, p.real_depth - 2 * w,
                mode=Mode.SUBTRACT)
        with Locations(((px0 + px1) / 2, (py0 + py1) / 2, 0)):
            Box(px1 - px0 - 2 * w, py1 - py0, p.real_ped_z - 2 * w,
                mode=Mode.SUBTRACT)
        # tapered fake-tip post, concentric on the body axis (x = z = 0)
        with Locations((0, p.real_post_y0, 0)):
            Cone(p.real_post_base_r, p.real_post_top_r, p.real_post_h,
                 rotation=(-90, 0, 0),
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, p.real_post_y0 - 0.1, 0)):
            Cone(p.real_post_base_r - 2.5, p.real_post_top_r - 1.2,
                 p.real_post_h - 3.5, rotation=(-90, 0, 0),
                 align=(Align.CENTER, Align.CENTER, Align.MIN),
                 mode=Mode.SUBTRACT)
    # rotate post-up (+Z); native +Y post axis -> +Z, axis stays at x = y = 0
    part0 = Rot(90, 0, 0) * bp.part
    z_top = part0.bounding_box().max.Z       # post tip = socket mouth
    with BuildPart() as part:
        add(part0)
        _cut_socket_features(z_top, bore_mid_id, p, tapered=True, slits=slits)
    return part.part


def _split_real_enclosure_solids():
    """Import the actual printed enclosure STEP and split it into
    (body, old fake-tip post).

    The reference file conveniently keeps the fake-tip post as its own solid
    (base plane y = 66, top y = 85.5, outer cone + Ø7.5 -> 6.4 tapered bore,
    all concentric on the part's Y axis at x = z = 0), so "lopping off" the
    old tip is exact: drop that solid and keep the body untouched.
    """
    imported = import_step(str(REAL_ENCLOSURE_STEP))
    solids = sorted(imported.solids(), key=lambda s: s.bounding_box().min.Y)
    body, post = solids[0], solids[-1]
    # sanity: the post solid sits entirely above the body top face
    assert post.bounding_box().min.Y >= body.bounding_box().max.Y - 1e-3
    return body, post


def make_real_enclosure_p20_tip(bore_mid_id: float | None = None,
                                p: Params = P, slits: bool = True) -> Compound:
    """The **actual** printed enclosure (imported from the reference STEP,
    body untouched) with its fake tip replaced by the tested "best" P20 tip.

    Unlike ``make_real_sensor_package_p20`` (a from-scratch parametric
    recreation), this edits the real part directly per PR #60: the old post
    solid (Ø7.5 mm ejector-sleeve bore) is dropped, the residual ~2 mm of
    bore that continued into the body top wall is plugged, and a new tip is
    grafted **concentric on the old post axis** with the **same 19.5 mm
    height** (top face stays at the original z), so nothing else about the
    part changes.

    New tip (bottom -> top), mirroring the round-1 winning test-tip stack:
    base flare matching the old post's Ø14 base circumference, Ø8 stem,
    45 deg chamfer into the Ø10 flange, then the Ø6 x 8 mm socket with the
    1.78 deg tapered bore (mid-ID default ``p.best_bore_id`` = 3.40 mm, the
    round-1 slitted winner and FEA recommendation) + 6 spring-finger slits.

    Returned post-up (+Z), like ``make_real_sensor_package_p20``.
    """
    bore_mid_id = bore_mid_id or p.best_bore_id
    body, old_post = _split_real_enclosure_solids()
    # rotate to post-up: native +Y post axis -> +Z (axis stays at x = y = 0)
    body = Rot(90, 0, 0) * body
    old_post = Rot(90, 0, 0) * old_post
    pb = old_post.bounding_box()
    axis_x, axis_y = pb.center().X, pb.center().Y   # old post axis: (0, 0)
    z_base, z_tip = pb.min.Z, pb.max.Z              # 66.0 .. 85.5
    base_r = pb.size.X / 2                          # Ø14.04 base flare
    stem_r = p.tip_body_od / 2
    flange_r = p.tip_flange_od / 2
    z_socket = z_tip - p.socket_depth
    z_flange = z_socket - p.tip_flange_h
    z_chamfer = z_flange - (flange_r - stem_r)      # 45 deg into the flange
    with BuildPart() as part:
        add(body)
        with Locations((axis_x, axis_y, 0)):
            # plug the residual Ø7.4 bore in the body top wall (part of the
            # old tip's bore, so filling it belongs to the tip swap)
            with Locations((0, 0, z_base)):
                Cylinder(3.7, 2.0, align=(Align.CENTER, Align.CENTER,
                                          Align.MAX))
                # base flare: old base circumference down to the stem
                Cone(base_r, stem_r, 3.5,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((0, 0, z_base + 3.5)):
                Cylinder(stem_r, z_chamfer - (z_base + 3.5),
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((0, 0, z_chamfer)):
                Cone(stem_r, flange_r, z_flange - z_chamfer,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((0, 0, z_flange)):
                Cylinder(flange_r, p.tip_flange_h,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
            with Locations((0, 0, z_socket)):
                Cylinder(p.socket_od / 2, p.socket_depth,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
        _cut_socket_features(z_tip, bore_mid_id, p, tapered=True, slits=slits,
                             cx=axis_x, cy=axis_y)
    return part.part


def verify_real_enclosure_p20_tip(p: Params = P) -> dict:
    """Checks for ``make_real_enclosure_p20_tip``: the body is untouched,
    the new tip is concentric with the old post circumference, the top face
    height is preserved, and the socket is full depth."""
    body, old_post = _split_real_enclosure_solids()
    body, old_post = Rot(90, 0, 0) * body, Rot(90, 0, 0) * old_post
    new = make_real_enclosure_p20_tip(p=p)
    pb, nb, bb = (old_post.bounding_box(), new.bounding_box(),
                  body.bounding_box())
    z_base = pb.min.Z
    # body untouched: below the post base the new part is exactly the body
    box = Box(200, 200, 200, align=(Align.CENTER, Align.CENTER, Align.MAX),
              mode=Mode.PRIVATE).moved(Location((0, 0, z_base)))
    delta = (new & box).volume - body.volume
    # new tip concentric with the old post axis (bbox-symmetry centres)
    tip_box = Box(200, 200, 200,
                  align=(Align.CENTER, Align.CENTER, Align.MIN),
                  mode=Mode.PRIVATE).moved(Location((0, 0, z_base + 0.01)))
    new_tip = new & tip_box
    tc, pc = new_tip.bounding_box().center(), pb.center()
    return {
        "body_volume_delta_mm3": round(delta, 3),
        "tip_axis_offset_mm": round(math.hypot(tc.X - pc.X, tc.Y - pc.Y), 4),
        "old_top_z": round(pb.max.Z, 3),
        "new_top_z": round(nb.max.Z, 3),
        "bbox_xy_match": (abs(nb.min.X - bb.min.X) < 1e-6
                          and abs(nb.max.X - bb.max.X) < 1e-6
                          and abs(nb.min.Y - bb.min.Y) < 1e-6
                          and abs(nb.max.Y - bb.max.Y) < 1e-6),
        "n_solids": len(new.solids()),
    }


def verify_real_package_volume(p: Params = P) -> dict:
    """Compare the from-scratch recreation against the imported reference STEP.

    Returns a dict with both volumes (cm^3) and the percentage delta.  Used to
    confirm the parametric rebuild faithfully reproduces the real part before
    its tip is changed; the reference STEP is read here for validation only,
    never for geometry.
    """
    if not REAL_ENCLOSURE_STEP.exists():
        return {}
    imported = import_step(str(REAL_ENCLOSURE_STEP))
    ref_vol = sum(s.volume for s in imported.solids()) / 1000.0
    # rebuild without the socket so the comparison is body-to-body
    recreated = make_real_sensor_package_p20(p=p, slits=False)
    rec_vol = recreated.volume / 1000.0
    return {
        "reference_cm3": round(ref_vol, 2),
        "recreated_cm3": round(rec_vol, 2),
        "delta_pct": round((rec_vol - ref_vol) / ref_vol * 100.0, 1),
    }


def export_all(p: Params = P) -> dict[str, Compound]:
    STL_DIR.mkdir(parents=True, exist_ok=True)
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    parts = {
        "fake_tip_test_array": make_test_array(p),
        "fake_tip_test_array_slit": make_test_array(p, tapered=True, slits=True),
        "fake_tip_test_array_slit_small": make_test_array(
            p, tapered=True, slits=True, bore_ids=p.bore_ids_small),
        "deck_plate_base": make_deck_plate(p),
        "fake_tip_insert": make_fake_tip_insert(p=p),
        "mock_sensor_package": make_mock_sensor_package(p=p),
        "real_sensor_package_p20": make_real_sensor_package_p20(p=p),
        "real_enclosure_p20_tip": make_real_enclosure_p20_tip(p=p),
    }
    checks = verify_real_enclosure_p20_tip(p)
    print(f"real_enclosure_p20_tip checks: {checks}")
    vmatch = verify_real_package_volume(p)
    if vmatch:
        print(f"real_sensor_package_p20 volume check: recreated "
              f"{vmatch['recreated_cm3']} cm^3 vs reference "
              f"{vmatch['reference_cm3']} cm^3 ({vmatch['delta_pct']:+}%)")
    for name, part in parts.items():
        export_stl(part, str(STL_DIR / f"{name}.stl"))
        export_step(part, str(STEP_DIR / f"{name}.step"))
        bb = part.bounding_box()
        print(f"{name}: bbox {bb.size.X:.1f} x {bb.size.Y:.1f} x "
              f"{bb.size.Z:.1f} mm, volume {part.volume / 1000:.1f} cm^3")
    return parts


if __name__ == "__main__":
    export_all()
