"""The rePowder's ultrasonic stack (induction module) as BYU's machine is assembled, with the sizes measured on the
machine on 2026-10-08 (vertical-cloud-lab/byu-vcl issue 261, comment 6069616664):

    upper sonotrode (W-Ni-Fe)   0.785 in across, 2.23 in long        -> 19.94 x 56.64 mm
    CF and Mo plates            4.71 x 0.82 in                        -> 119.63 x 20.83 mm
    the plate's hole            "the back of the plate is lined up with the edge of the sonotrodes ... no overhang",
                                so the hole's centre sits one sonotrode radius (9.97 mm) from the plate's back end
    set-up                      "comes off perpendicular to the stack ... at a 45 degree angle": the plate is square
                                to the axis, and the stack rises at 45 deg (40 in the earlier models). The plate hangs
                                straight down the stack's slope, so it also sits at 45 deg. This reading of the 45 is
                                ours; the Oct 6 viewport photo in issue 261 fits it (see README.md)
    stack position              "adjustable": it slides along its axis in the housing on the door

Everything else is an estimate carried over from byu-vcl's viz3d model (atomizer-training/viz3d/model.py on PR 255,
88eeace), which read its sizes off the training videos: the plates' thickness (2.5 mm for CF; the Mo plate's is
unknown), the 8 mm hole, the M8 connector, the Ti sonotrode below its tip, the booster, transducer and cover. The Ti
sonotrode is taken to be as wide as the upper one, since the plate's back end lines up with "the sonotrodes".

Frame: the stack's own, the same as viz3d's stack_parts(): z along the axis, out of the door into the chamber, z = 0
at the Ti sonotrode's tip face (the plate's back face); x along the plate from its hole towards its free end; y = z
cross x. Millimetres. In the chamber (viz3d's frame: x right, into the chamber from the door; y back; z up; the
melt stream falls down the line x = y = 0) the axis is (cos 45, 0, sin 45) and the plate's x runs straight down the
slope, (sin 45, 0, -cos 45).

    python stack_model.py            # exports/ (STEP, STL, GLB), dims.json, and prints the landing window
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
IN = 25.4
STREAM_R = 1.4            # the melt stream's radius, as in viz3d

CARBON = (0.13, 0.13, 0.15)
MOLY = (0.60, 0.61, 0.64)
W_ALLOY = (0.47, 0.48, 0.51)
TITANIUM = (0.66, 0.64, 0.60)
BOOSTER = (0.72, 0.73, 0.76)
TRANSDUCER = (0.25, 0.27, 0.30)
STEEL = (0.78, 0.79, 0.81)


@dataclass(frozen=True)
class Dims:
    """Sizes in mm. The first five are measured (issue 261); the rest are estimates."""
    upper_d: float = 0.785 * IN       # W-Ni-Fe upper sonotrode
    upper_l: float = 2.23 * IN
    plate_l: float = 4.71 * IN        # CF and Mo plates are the same size
    plate_w: float = 0.82 * IN
    stack_angle: float = 45.0         # deg above horizontal; the plate is square to the axis
    sono_d: float = 0.785 * IN        # Ti sonotrode, taken equal to the upper one
    plate_t: float = 2.5              # CF plate; the Mo plate's thickness is not known
    hole_d: float = 8.0               # passes the M8 connector
    plate_corner_r: float = 1.0
    sono_flats: float = 17.0          # wrench flats near the Ti sonotrode's tip
    conn_r: float = 4.0               # M8 connector: each threaded half, and the 8 mm ring between them
    conn_half: float = 12.0
    conn_ring: float = 3.0
    upper_chamfer: float = 1.2

    @property
    def hole_e(self) -> float:
        """The hole's centre to the plate's back end: the back end is flush with the sonotrodes' edge."""
        return self.sono_d / 2


MEASURED = Dims()
# the sizes the models used before the measurements (byu-vcl viz3d at 88eeace, and this repo's repowder_stack.py)
ESTIMATED_2026_10_07 = Dims(upper_d=20.0, upper_l=55.0, plate_l=100.0, plate_w=20.0, stack_angle=40.0, sono_d=20.0)

SOURCES = {
    "upper_d": "measured, 0.785 in (issue 261, 2026-10-08)",
    "upper_l": "measured, 2.23 in (issue 261, 2026-10-08)",
    "plate_l": "measured, 4.71 in, CF and Mo plates (issue 261, 2026-10-08)",
    "plate_w": "measured, 0.82 in, CF and Mo plates (issue 261, 2026-10-08)",
    "stack_angle": "measured: the plate 'comes off at a 45 degree angle', square to the stack (issue 261); read as "
                   "the stack rising at 45 deg with the plate straight down its slope",
    "hole_e": "from the measurement: the plate's back end is flush with the sonotrodes' edge, so one sonotrode radius",
    "sono_d": "assumed equal to the upper sonotrode ('the edge of the sonotrodes')",
    "plate_t": "estimate (CF, video frames); the Mo plate's thickness is not known",
    "hole_d": "estimate: the M8 connector passes it",
    "plate_corner_r": "estimate",
    "sono_flats": "estimate (viz3d)",
    "conn_r": "M8", "conn_half": "estimate (viz3d)", "conn_ring": "estimate (viz3d)",
    "upper_chamfer": "estimate",
}


def zc(r, z0, z1) -> cq.Solid:
    """A cylinder of radius r on the stack's axis, from z0 to z1."""
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


def tube(ro, ri, z0, z1) -> cq.Shape:
    return zc(ro, z0, z1).cut(zc(ri, z0 - 1, z1 + 1))


def box(x0, x1, y0, y1, z0, z1) -> cq.Solid:
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def fuse(*shapes) -> cq.Shape:
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.clean()


def plate(d: Dims = MEASURED, thickness: float | None = None) -> cq.Shape:
    """The plate: its back face on the Ti sonotrode's tip (z = 0), hung by its hole on the axis, its free end along +x."""
    t = d.plate_t if thickness is None else thickness
    body = (cq.Workplane("XY").box(d.plate_l, d.plate_w, t, centered=(True, True, False))
            .edges("|Z").fillet(d.plate_corner_r).val())
    return body.translate(cq.Vector(d.plate_l / 2 - d.hole_e, 0, 0)).cut(zc(d.hole_d / 2, -1, t + 1))


def upper_sonotrode(d: Dims = MEASURED) -> cq.Shape:
    """The W-Ni-Fe upper sonotrode, screwed onto the connector's outer half, its face against the plate."""
    up = cq.Workplane("XY").circle(d.upper_d / 2).extrude(d.upper_l).faces(">Z").edges().chamfer(d.upper_chamfer).val()
    return up.translate(cq.Vector(0, 0, d.plate_t)).cut(zc(d.conn_r + 0.4, d.plate_t - 1, d.conn_half + 0.6))


def connector(d: Dims = MEASURED) -> cq.Shape:
    """The double-threaded M8 connector: half in each sonotrode, its 8 mm ring hidden in the Ti sonotrode's tip."""
    h, g, r = d.conn_half, d.conn_ring, d.conn_r
    return fuse(zc(r - 0.2, -h - g, -g), zc(r, -g, 0.0), zc(r - 0.2, 0.0, h))


def ti_sonotrode(d: Dims = MEASURED) -> cq.Shape:
    """Ti sonotrode: M8 bore and wrench flats at the tip, a collar and the KF50 flange at the booster end (estimates)."""
    r = d.sono_d / 2
    sono = fuse(zc(r, -128, 0), zc(17, -122, -114), zc(37, -116, -108))
    sono = sono.cut(zc(d.conn_r + 0.4, -d.conn_half - d.conn_ring - 1.0, 1.0))
    for x0, x1 in ((d.sono_flats / 2, r + 2), (-r - 2, -d.sono_flats / 2)):
        sono = sono.cut(box(x0, x1, -r - 2, r + 2, -14, -2))
    return sono.clean()


def back_end() -> dict[str, cq.Shape]:
    """Booster (1.5:1), transducer and cover, measured back from the Ti sonotrode's tip: viz3d's estimates."""
    return {
        "booster": fuse(zc(20, -250, -130), zc(34, -195, -185)),
        "transducer": fuse(zc(36, -350, -250), zc(30, -360, -350), zc(9, -385, -360)),
        "stack_cover": fuse(tube(50, 46, -402, -232), zc(50, -407, -402).cut(zc(12, -412, -400)),
                            tube(62, 46, -240, -232)),
    }


def parts(d: Dims = MEASURED, plate_material: str = "cf", full: bool = False) -> dict[str, tuple[cq.Shape, tuple]]:
    """name -> (shape, rgb), in the stack's frame. full adds the booster, transducer and cover."""
    P = {
        f"plate_{plate_material}": (plate(d), CARBON if plate_material == "cf" else MOLY),
        "upper_sonotrode": (upper_sonotrode(d), W_ALLOY),
        "connector_m8": (connector(d), TITANIUM),
        "ti_sonotrode": (ti_sonotrode(d), TITANIUM),
    }
    if full:
        colours = {"booster": BOOSTER, "transducer": TRANSDUCER, "stack_cover": STEEL}
        P.update({k: (s, colours[k]) for k, s in back_end().items()})
    return P


def assembly(d: Dims = MEASURED, plate_material: str = "cf", full: bool = False, name: str = "repowder_stack"):
    assy = cq.Assembly(name=name)
    for k, (shape, rgb) in parts(d, plate_material, full).items():
        assy.add(shape, name=k, color=cq.Color(*rgb))
    return assy


# ----------------------------------------------------------------------------------------- the stack in the chamber
def axes(d: Dims = MEASURED, clock: float = 0.0):
    """(axis, along, across) in the chamber's frame. clock: the plate's angle about the axis, 0 = straight down the
    slope (as measured), 90 = level, towards the chamber's front (-y)."""
    a = math.radians(d.stack_angle)
    n = np.array([math.cos(a), 0.0, math.sin(a)])
    down = np.array([math.sin(a), 0.0, -math.cos(a)])
    front = np.array([0.0, -1.0, 0.0])
    al = math.cos(math.radians(clock)) * down + math.sin(math.radians(clock)) * front
    return n, al, np.cross(n, al)


def landing_window(d: Dims = MEASURED, offset: float = 0.0, stream_r: float = STREAM_R) -> tuple[float, float]:
    """With the plate straight down the slope: the range of distances from the hole, along the plate, where a vertical
    stream can land on the plate without touching the upper sonotrode first. offset: the stream's sideways distance
    from the axis's vertical plane (it must be under 0.5 * plate_w - stream_r to land on the plate at all).

    Going up from a landing point t, the stream moves back along the plate by cot(angle) per mm it rises along the axis,
    so over the upper sonotrode's length it comes back to t - upper_l * cot(angle), which must stay outside the
    sonotrode's radius (plus the stream's)."""
    cot = 1.0 / math.tan(math.radians(d.stack_angle))
    reach = math.sqrt(max((d.upper_d / 2 + stream_r) ** 2 - offset ** 2, 0.0))
    return d.upper_l * cot + reach, d.plate_l - d.hole_e - stream_r


def landing_drop(t: float, d: Dims = MEASURED) -> float:
    """How far below the point where the axis passes under the stream the stream lands, for a landing t mm from the
    hole (plate straight down the slope, the axis in the stream's vertical plane, the stack slid along its fixed
    axis): t / cos(angle). The hole's centre on the plate's face is on the axis, so the plate's thickness doesn't
    enter."""
    return t / math.cos(math.radians(d.stack_angle))


def dims_json(d: Dims = MEASURED) -> dict:
    lo, hi = landing_window(d)
    out = {k: round(getattr(d, k), 3) for k in d.__dataclass_fields__}
    out["hole_e"] = round(d.hole_e, 3)
    return {
        "units": "mm, degrees",
        "frame": "stack frame: z along the axis into the chamber, z = 0 at the Ti sonotrode's tip face (the plate's "
                 "back face); x along the plate from its hole to its free end; y = z cross x",
        "dims": out,
        "sources": SOURCES,
        "measured_in_inches": {"upper_d": 0.785, "upper_l": 2.23, "plate_l": 4.71, "plate_w": 0.82},
        "set_up": {"stack_angle_deg": d.stack_angle, "plate_clock": "straight down the stack's slope",
                   "stack_position": "adjustable: slides along its axis in the housing on the door"},
        "landing_window_mm_from_hole": [round(lo, 1), round(hi, 1)],
        "landing_window_note": f"with the plate straight down the slope and the stream (radius {STREAM_R} mm) in the "
                               "axis's vertical plane: nearer the hole, the upper sonotrode is in the stream's way",
        "previous_estimates_2026_10_07": {k: getattr(ESTIMATED_2026_10_07, k) for k in
                                          ("upper_d", "upper_l", "plate_l", "plate_w", "stack_angle", "sono_d")},
    }


def export_all(out: Path = HERE / "exports") -> list[Path]:
    """STEP assemblies (named, coloured parts), a STEP and an STL per part, and a GLB, all in the stack's frame."""
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for name, kw in (("repowder_stack_tip_cf", dict(plate_material="cf")),
                     ("repowder_stack_full_cf", dict(plate_material="cf", full=True))):
        assy = assembly(**kw, name=name)
        p = out / f"{name}.step"
        assy.export(str(p))
        written.append(p)
    assy = assembly(full=True, name="repowder_stack_full_cf")
    p = out / "repowder_stack_full_cf.glb"
    assy.export(str(p), tolerance=0.05, angularTolerance=0.1)
    written.append(p)
    single = {"plate_cf": plate(), "upper_sonotrode": upper_sonotrode(), "connector_m8": connector(),
              "ti_sonotrode": ti_sonotrode()}
    for k, s in single.items():
        for ext in ("step", "stl"):
            p = out / f"{k}.{ext}"
            if ext == "stl":
                cq.exporters.export(s, str(p), tolerance=0.02, angularTolerance=0.1)
            else:
                cq.exporters.export(s, str(p))
            written.append(p)
    return written


if __name__ == "__main__":
    (HERE / "dims.json").write_text(json.dumps(dims_json(), indent=2) + "\n")
    for p in export_all():
        print(f"{p.relative_to(HERE)}  {p.stat().st_size / 1e3:.0f} kB")
    for label, d in (("measured", MEASURED), ("estimated 2026-10-07", ESTIMATED_2026_10_07)):
        lo, hi = landing_window(d)
        print(f"{label}: the stream can land {lo:.1f} to {hi:.1f} mm from the hole ({hi - lo:.1f} mm of plate)")
