"""Parametric CAD for the OT-2 P20 press-fit "fake tip" test array and
mock wireless-color-sensor package (issue #33, PR #114).

Parts generated (STL into ``stl/``, STEP into ``step/``):

1. ``fake_tip_test_array``  — 10 loose test tips (bore ID 3.40-3.85 mm in
   0.05 mm steps) laid out in the same 2 x 5 grid as the deck plate pockets.
   Print in one batch on a Bambu Lab A1 mini.
2. ``deck_plate_base``      — ANSI/SLAS-footprint (127.76 x 85.48 mm) base
   that sits in an OT-2 deck slot.  It has 10 drop-in pockets that register
   each test tip under the pipette without locking it down, plus engraved
   bore-size labels next to every pocket.
3. ``fake_tip_insert``      — final-geometry modular insert (tapered bore,
   3 spring-finger slits) per p20-fake-tip-design.md.
4. ``mock_sensor_package``  — drop-in stand-in for the wireless color sensor
   enclosure: same 40 x 60 mm footprint and 84 mm overall height as the
   original P300 part (so the existing ``byu_color_sensor_charging_port``
   labware/tipLength still apply), but topped with the P20 socket.

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
    BuildPart,
    BuildSketch,
    Compound,
    Cone,
    Cylinder,
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
    Rot,
    Text,
    add,
    export_step,
    export_stl,
    extrude,
    mirror,
)

HERE = pathlib.Path(__file__).resolve().parent
STL_DIR = HERE / "stl"
STEP_DIR = HERE / "step"

FONT = "DejaVu Sans"  # available on Linux CI; build123d falls back if missing


@dataclass
class Params:
    # ---- nozzle / bore (see p20-fake-tip-design.md) ----
    bore_ids: tuple = (3.40, 3.45, 3.50, 3.55, 3.60, 3.65, 3.70, 3.75, 3.80, 3.85)
    nominal_bore_id: float = 3.55          # round-1 best guess (mid-depth ID)
    nozzle_taper_half_angle_deg: float = 1.78  # measured from original P300 STEP
    socket_depth: float = 8.0
    socket_od: float = 6.0                 # top rim must sit under ejector sleeve
    entry_chamfer: float = 0.5
    # ---- spring-finger slits (final geometry only) ----
    n_slits: int = 3
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


def make_test_tip(bore_id: float, p: Params = P) -> Compound:
    """Round-1 test piece: straight bore at ``bore_id``, no slits.

    Stack (bottom -> top): body O8 x 10, flange O10 x 2, socket O6 x 8.
    Bore is blind (socket + 2 mm), leaving a solid base that carries an
    engraved 2-digit size code readable from below (e.g. '55' = 3.55 mm).
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
        # straight blind bore
        bore_depth = p.socket_depth + p.tip_bore_extra
        with Locations((0, 0, z_top)):
            Cylinder(bore_id / 2, bore_depth,
                     align=(Align.CENTER, Align.CENTER, Align.MAX),
                     mode=Mode.SUBTRACT)
        # entry chamfer (45 deg) as a conical cut
        with Locations((0, 0, z_top)):
            Cone(bore_id / 2 + p.entry_chamfer, bore_id / 2, p.entry_chamfer,
                 align=(Align.CENTER, Align.CENTER, Align.MAX),
                 mode=Mode.SUBTRACT)
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
    dr = p.socket_depth / 2 * math.tan(
        math.radians(p.nozzle_taper_half_angle_deg))
    entry_r = bore_mid_id / 2 + dr
    bottom_r = bore_mid_id / 2 - dr
    with Locations((0, 0, z_top)):
        Cone(entry_r, bottom_r, p.socket_depth,
             align=(Align.CENTER, Align.CENTER, Align.MAX),
             mode=Mode.SUBTRACT)
    with Locations((0, 0, z_top)):
        Cone(entry_r + p.entry_chamfer, entry_r, p.entry_chamfer,
             align=(Align.CENTER, Align.CENTER, Align.MAX),
             mode=Mode.SUBTRACT)
    if slits:
        for k in range(p.n_slits):
            ang = 360 / p.n_slits * k
            # radial slot from the top, rounded root (~R0.25 fillet)
            slot = Box(p.socket_od, p.slit_width, p.slit_depth,
                       align=(Align.CENTER, Align.CENTER, Align.MAX),
                       mode=Mode.PRIVATE)
            root = Cylinder(p.slit_width / 2, p.socket_od,
                            rotation=(0, 90, 0), mode=Mode.PRIVATE)
            root = Pos(0, 0, -p.slit_depth) * root
            cutter = slot + root
            cutter = Rot(0, 0, ang) * Pos(0, 0, z_top) * cutter
            add(cutter, mode=Mode.SUBTRACT)


def make_fake_tip_insert(bore_mid_id: float | None = None,
                         p: Params = P) -> Compound:
    """Final-geometry modular insert per the design doc dimension table:
    peg O6 x 5 (press-fits enclosure recess) + flange O8 x 2 + socket
    O6 x 8 with tapered bore and 3 spring-finger slits."""
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


def make_test_array(p: Params = P) -> Compound:
    """All 10 round-1 test tips, laid out in the pocket grid (one print)."""
    tips = []
    for (x, y, _name), bore in zip(grid_centers(p), p.bore_ids):
        tip = make_test_tip(bore, p)
        tips.append(Location((x, y, 0)) * tip)
    return Compound(children=tips)


def export_all(p: Params = P) -> dict[str, Compound]:
    STL_DIR.mkdir(parents=True, exist_ok=True)
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    parts = {
        "fake_tip_test_array": make_test_array(p),
        "deck_plate_base": make_deck_plate(p),
        "fake_tip_insert": make_fake_tip_insert(p=p),
        "mock_sensor_package": make_mock_sensor_package(p=p),
    }
    for name, part in parts.items():
        export_stl(part, str(STL_DIR / f"{name}.stl"))
        export_step(part, str(STEP_DIR / f"{name}.step"))
        bb = part.bounding_box()
        print(f"{name}: bbox {bb.size.X:.1f} x {bb.size.Y:.1f} x "
              f"{bb.size.Z:.1f} mm, volume {part.volume / 1000:.1f} cm^3")
    return parts


if __name__ == "__main__":
    export_all()
