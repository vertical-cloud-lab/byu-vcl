"""An AirGradient ONE on every powered tray and at every floor station (#303, PR #318, round 13).

Sterling, PR #318, 2026-11-20: "Each tray should have an airgradient added to it for environmental monitoring. Each
station should also have one". notes/airgradient.md has the choice, the sources and the data path; in short:

* **The unit:** AirGradient ONE, model I-9PSL (USD 230 assembled): PM1/2.5/10 (Plantower PMS5003), CO2 (SenseAir
  S8), TVOC and NOx indices (Sensirion SGP41), temperature and humidity (Sensirion SHT40), open firmware with a local
  API. 131.2 x 131.2 x 36.2 mm, 230 g (its spec sheet). USB-C 5 V, a supply of at least 2 A; about 1 W typical, under
  4 W at peak with the LEDs off (our estimate from its parts). Wi-Fi 2.4 GHz only: no Ethernet, no PoE.
* **On a tray** (no display: the spec sheet's "also available without display"; or the standard unit with its display
  and LED bar turned off): upright on top of the tray's UPS, between the cradle's two straps, on a printed riser that
  clips across the unit (ours), its front to the middle of the tray, its top and bottom edges open for the convection
  it relies on and its PM intake 450 mm over the tray floor (Plantower asks for 200 mm over the ground). Power: a
  5 V 2.4 A USB supply in one of the UPS's backed outlets. Network: Wi-Fi to a hotspot on the tray's own Pi 5 (the
  stream camera's), which polls its local API and forwards the readings over the dock's Ethernet; Wi-Fi inside a
  steel Shuttle is untested.
* **At a floor station** (the standard unit with its display): on the left end of the grey junction box at the end of
  the station's drop (its screw holes match common US junction boxes), powered from the box's socket, on the lab's
  Wi-Fi.

Not an O2 monitor (argon and N2 users need their own) and not rated for a classified dust area.

    python3 airgradient.py           # the model's size and the trays it goes on
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lab_models"))

AG = dict(w=131.2, h=131.2, d=36.2, r=12.0, edge=3.0, mass_g=230.0, price_usd=230.0, watts_typ=1.0, watts_max=4.0,
          model="AirGradient ONE (I-9PSL)",
          source="AirGradient ONE spec sheet and product page (notes/airgradient.md): 131.2 x 131.2 x 36.2 mm, 230 g, "
                 "USB-C 5 V (>= 2 A supply), Wi-Fi 2.4 GHz; PMS5003, SenseAir S8, SGP41, SHT40")
RISER = dict(t=8.0, l=40.0, lip=10.0)     # the printed riser on the UPS's top (ours): 8 mm thick, 40 mm along it
MATERIALS = {      # (r, g, b, opacity, specular), as instruments.MATERIALS
    "ag_body": (0.94, 0.94, 0.93, 1.0, 0.35),          # white ASA
    "ag_led": (0.97, 0.97, 0.95, 1.0, 0.3),            # the LED bar's dots, off
    "ag_screen": (0.05, 0.06, 0.08, 1.0, 0.8),         # the OLED window
    "ag_logo": (0.45, 0.47, 0.50, 1.0, 0.2),
    "ag_vent": (0.10, 0.10, 0.11, 1.0, 0.1),
    "ag_pm": (0.20, 0.42, 0.80, 1.0, 0.3),             # the blue PMS5003 seen through the bottom vents
    "ag_riser": (0.15, 0.15, 0.16, 1.0, 0.3),          # black PETG
    "ag_cable": (0.12, 0.12, 0.13, 1.0, 0.3),
}


def parts(display: bool = True) -> dict:
    """{name: (shape, material)}, the unit's own frame: x across its front, -y out of the front (the front face at
    y = 0, the back at y = d), z up from its bottom edge. The front from AirGradient's photo (notes/airgradient.md):
    the LED bar's 11 dots along the top, the OLED window lower right, the logo lower left; vent slots along the top
    and bottom edges, the PM sensor's intake and outlet among the bottom ones."""
    import cadquery as cq
    from common import box
    w, h, d, r = AG["w"], AG["h"], AG["d"], AG["r"]
    body = cq.Workplane("XZ").rect(w, h).extrude(-d).translate((0, 0, h / 2)).edges("|Y").fillet(r) \
        .faces("<Y").edges().fillet(AG["edge"])
    p = {}
    vents = None
    for z, n in ((h - 0.8, 13), (0.8, 13)):          # slots cut into the top and bottom edges
        for i in range(n):
            x = -w / 2 + 22.0 + i * (w - 44.0) / (n - 1)
            v = box(x - 2.2, 6.0, z - 1.6, x + 2.2, d - 6.0, z + 1.6)
            vents = v if vents is None else vents.union(v)
    body = body.cut(vents)
    p["AirGradient ONE"] = (body, "ag_body")
    p["vents"] = (box(-w / 2 + 19.0, 7.0, 1.5, w / 2 - 19.0, d - 7.0, 3.0).union(
        box(-w / 2 + 19.0, 7.0, h - 3.0, w / 2 - 19.0, d - 7.0, h - 1.5)), "ag_vent")
    p["PM sensor"] = (box(-26.0, 9.0, 2.6, 26.0, d - 9.0, 3.2), "ag_pm")
    x0, z0 = -w / 2, h                                # photo coordinates: x from the left edge, y down from the top
    if display:
        dots = None
        for i in range(11):
            c = cq.Workplane("XZ").circle(2.5).extrude(0.6).translate((x0 + 20.0 + 9.0 * i, 0.0, z0 - 21.0))
            dots = c if dots is None else dots.union(c)
        p["LED bar"] = (dots, "ag_led")
        p["OLED"] = (box(x0 + 83.0 - 16.0, -0.6, z0 - 99.0 - 8.0, x0 + 83.0 + 16.0, 0.0, z0 - 99.0 + 8.0), "ag_screen")
    p["logo"] = (box(x0 + 15.0, -0.4, z0 - 115.0, x0 + 41.0, 0.0, z0 - 104.0), "ag_logo")
    return p


def along_ups(k: str) -> bool:
    """Whether tray k's unit stands along its UPS (its width along the UPS's length, between the cradle's straps, its
    front to the opening), which the GXT5 units' 476 and 546 mm leave room for; on the 300 mm PSI5-800 the straps are
    only 130 mm apart, so the unit stands across it, its front to the middle of the tray."""
    import ups as U
    D, _, _ = U.tower_dims(U.unit_of(k))
    return D / 2 - 20.0 >= AG["w"] + 10.0


def riser_parts(ups_t: float, along: bool = False) -> dict:
    """The printed riser (ours), the unit's own frame (centred over the UPS's top): a plate under the unit and two lips
    that hook down the UPS's sides (ups_t apart), 40 mm long; the USB-C lead is in the unit's back recess."""
    from common import box
    w, d = AG["w"], AG["d"]
    rt, rl, lip = RISER["t"], RISER["l"], RISER["lip"]
    plate = box(-w / 2, -2.0, -rt, w / 2, d + 2.0, 0.0)        # the unit's frame: its body from y = 0 to d
    for s in (-1, 1):
        a = s * (ups_t / 2 + 0.5)
        a0, a1 = sorted((a, a + s * 3.0))
        if along:                                   # the UPS's sides run along the unit's x, d/2 off its front
            lipb = box(-rl / 2, d / 2 + a0, -rt - lip, rl / 2, d / 2 + a1, -rt)
        else:                                       # across: the UPS's sides run along the unit's y
            lipb = box(a0, d / 2 - rl / 2, -rt - lip, a1, d / 2 + rl / 2, -rt)
        plate = plate.union(lipb)
    return {"AirGradient riser": (plate, "ag_riser")}


def on_ups(k: str) -> np.ndarray:
    """4x4: the unit's own frame, centred over tray k's UPS (half its depth either side of the UPS's centre line), in
    the tray's frame, standing on its riser on the UPS's top, centred on the UPS's length: along it, its front to the
    opening (-y), on the GXT5 units; across it, its front to the tray's middle (-x), on the PSI5-800 (along_ups)."""
    import ups as U
    from scene import R, T
    m = U.unit_of(k)
    D, Tk, H = U.tower_dims(m)
    bx, yc, z0 = U.placement(k)
    turn = 0.0 if along_ups(k) else -90.0
    return T((bx - D / 2, yc, z0 + H + 1.6 + RISER["t"])) @ R((0, 0, 1), turn) @ T((0, -AG["d"] / 2, 0))


_MESHES: dict = {}


def meshes(key: str, fn) -> dict:
    """{material: PolyData} of a parts dict, tessellated once per key."""
    if key not in _MESHES:
        import lab
        by: dict = {}
        for name, (shape, mat) in fn().items():
            s = shape.val() if hasattr(shape, "val") and len(shape.vals()) == 1 else shape
            if hasattr(s, "vals"):
                import cadquery as cq
                s = cq.Compound.makeCompound(s.vals())
            by.setdefault(mat, []).append(lab.to_mesh(s, 0.4))
        _MESHES[key] = {m: lab._merge(v) for m, v in by.items()}
    return _MESHES[key]


def add_to_tray(sc, k: str, group: str | None = None, parent: str | None = None) -> list:
    """Tray k's AirGradient (no display) on its UPS, as group `group` (default ag_<k>) riding on tray k (or `parent`).
    -> its actor names."""
    import ups as U
    from scene import T
    g = group or f"ag_{k}"
    m = U.unit_of(k)
    if m is None:
        return []
    _, Tk, _ = U.tower_dims(m)
    al = along_ups(k)
    names = []
    for key, fn in ((f"ag_tray", lambda: parts(display=False)),
                    (f"ag_riser_{Tk:.0f}_{int(al)}", lambda: riser_parts(Tk, al))):
        for mat, mesh in meshes(key, fn).items():
            r, gg, b, a, spec = MATERIALS[mat]
            n = f"{g}/{key} {mat}"
            sc.add(n, mesh, (r, gg, b), g, opacity=a, specular=spec)
            names.append(n)
    sc.gmat[g] = on_ups(k)
    sc.parent[g] = parent or f"tray_{k}"
    return names


def at_junction_box(x: float, y: float, z_top: float, face: int) -> dict:
    """{material: PolyData} of a floor station's unit (with its display) on the left end of a junction box at (x, y)
    whose top is z_top (setup_lab.junction_box: 240 x 120 x 180 mm, face -1 looks to -y): the unit's front turned to the
    box's face's side, its back on a printed plate on the box's end, its centre at the box's mid-height."""
    import pyvista as pv
    from scene import R, T
    w = 240.0
    M = T((x - w / 2 - 2.0 - AG["d"] / 2 - 2.0, y, z_top - 90.0 - AG["h"] / 2)) @ \
        R((0, 0, 1), 0.0 if face < 0 else 180.0) @ T((0, -AG["d"] / 2, 0))
    out = {}
    for mat, mesh in meshes("ag_floor", lambda: parts(display=True)).items():
        out[mat] = mesh.transform(M, inplace=False)
    plate = pv.Box(bounds=(x - w / 2 - 4.0, x - w / 2, y - 50.0, y + 50.0, z_top - 160.0, z_top - 20.0)).triangulate()
    out["ag_riser"] = plate if "ag_riser" not in out else pv.merge([out["ag_riser"], plate])
    return out


def colour(mat: str) -> tuple:
    return MATERIALS[mat][:3]


if __name__ == "__main__":
    import ups as U
    print(AG["model"], f"{AG['w']} x {AG['h']} x {AG['d']} mm, {AG['mass_g']:.0f} g")
    for k in U.TRAY_LOADS:
        m = U.unit_of(k)
        D, Tk, H = U.tower_dims(m)
        print(f"tray {k}: on its {m['model']} ({D:.0f} x {Tk:.0f} x {H:.0f} mm); its top at "
              f"{U.T_FLOOR + H + 1.6 + RISER['t'] + AG['h']:.0f} mm over the tray's underside")
