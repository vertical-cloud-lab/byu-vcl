"""The vertical cloud lab with its characterization instruments, and the backup layout: the alloy equipment in a line
with the VLM, all facing the same way, along a floor rail for the arm (#303).

    xvfb-run -a python3 line.py            # -> out/vlm_line.gif, out/mp4/vlm_line.mp4, out/vlm_line_still.png
    PREVIEW=1 xvfb-run -a python3 line.py  # the last frame of each sub-step -> /tmp/preview_vlm_line.png

What fits through the opening (727.5 mm of product height, Kardex's order sheet) goes on three more trays, D, E and F,
in the three storage slots round 2 left free. What doesn't stands in the line, fronts in line with the VLM's: the
glovebox and the rePowder atomizer on the left; the Aconity MIDI, the two Instrons and the wire EDM on the right. The
rail is the backup to the mobile base: a Vention rack-and-pinion seventh axis along the fronts, with the UR10e on its
carriage at the same 800 mm as on the MiR250, parked at the VLM's opening. No workflow uses it yet.

Builds on ``animate.Lab`` (round 2's scene: the VLM, trays A-C and their equipment, the rePowder) and ``tour.Rig``
(the instruments and their moving pieces).
"""
from __future__ import annotations

import hashlib
import pickle
import sys

import numpy as np

import animate as A
import instruments as I
import lab
import tour
import vlm as V
from scene import FPS, Scene, T, R

TITLE = "Vertical cloud lab: characterization trays and the alloy line"
Y_FACE = -V.UNIT_D / 2 - V.SKIN                 # the VLM's front face; every machine in the line has its front here
EXTRA = {"D": ("R1", "microscopy and diffraction"), "E": ("R4", "mechanical testing and particle size"),
         "F": ("F2", "sample prep and heat treatment")}
# what goes on each new tray, in the tray's frame (centre of its floor, y to the back): (instrument key, x, y)
TRAY_LOADS = {
    "D": [("sem", -760.0, 0.0), ("xrd", 60.0, 0.0), ("openflexure_v7", 560.0, -150.0),
          ("openflexure_delta", 800.0, -150.0)],
    "E": [("pip", -880.0, 0.0), ("nanoindenter", -250.0, 0.0), ("mastersizer", 590.0, 0.0)],
    "F": [("polisher", -500.0, 0.0), ("furnace", 300.0, 0.0)],
}
# the line, left to right: x of each machine's centre; fronts at Y_FACE (the rePowder stays where round 2 put it)
LINE = {"glovebox": -6350.0, "aconity": 3250.0, "instron_floor": 5600.0, "instron_small": 7000.0, "wire_edm": 8700.0}
NAMES = {"glovebox": "inert glovebox, automatic antechamber", "aconity": "Aconity MIDI metal printer",
         "instron_floor": "Instron 68FM-100, 100 kN", "instron_small": "Instron 68SC-2",
         "wire_edm": "FANUC ROBOCUT wire EDM"}
RAIL_Y = A.AMR_XY[1] + A.ARM_LOCAL[1]          # the arm's base over the same spot as on the MiR250
RAIL_X = (-7700.0, 10000.0)
PARK_X = 0.0                                   # the carriage parked at the VLM's opening

CAM_LINE = [(4400, -19800, 8600), (1100, -600, 900), (0, 0, 1)]
CAM_LEFT = [(-7200, -7600, 3300), (-4700, -1300, 1000), (0, 0, 1)]
CAM_VLM = [(3300, -7200, 3900), (0, -300, 1800), (0, 0, 1)]
CAM_RIGHT = [(9800, -7600, 3600), (6200, -1300, 1000), (0, 0, 1)]
CAM_OPEN = [(2600, -5200, 2300), (0, -1100, 1250), (0, 0, 1)]


def aconity_entries() -> dict:
    """The Aconity MIDI from #199's lab-models (lab_models/equipment.py), one mesh per material, cached."""
    import equipment
    src = (lab.HERE / "lab_models" / "equipment.py").read_bytes() + (lab.HERE / "lab.py").read_bytes()
    path = lab.CACHE / f"aconity_{hashlib.sha256(src).hexdigest()[:12]}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    lab.CACHE.mkdir(exist_ok=True)
    print("tessellating the Aconity MIDI", flush=True)
    ents = lab._model_entries(equipment.aconity_midi(), "aconity", 1.0)
    path.write_bytes(pickle.dumps(ents))
    return ents


def add_tray(sc: Scene, L: A.Lab, k: str):
    slot, role = EXTRA[k]
    V.TRAYS[k] = dict(kind="extra", role=role)
    A.HOME[k] = slot
    A.ROLE[k] = role
    for name, (shape, mat, group) in {**V.tray(k), **V.lamp(k)}.items():
        if hasattr(shape, "vals"):
            shape = shape.val() if len(shape.vals()) == 1 else I.cq.Compound.makeCompound(shape.vals())
        e = lab._entry(lab.to_mesh(shape, 2.0), mat, group)
        sc.add(name, e["mesh"], e["color"], group, opacity=e["opacity"])
    L.tray[k] = [*V.SLOTS[slot]]
    L.where[k] = slot
    L.eq_groups[k] = []


def place_floor(inst_bbox, x: float) -> np.ndarray:
    """A machine's own frame -> the line: centred on x, its front face on Y_FACE, standing on the floor."""
    x0, x1, y0, _, z0, _ = inst_bbox
    return T((x - (x0 + x1) / 2, Y_FACE - y0, -z0))


def build(name: str, data: dict, idata: dict):
    sc = Scene(name, TITLE, gif=False)          # the GIF is made from the MP4 (mp4_to_gif)
    sc.cam = list(CAM_LINE)
    L = A.Lab(sc, data, robot=False)
    import pyvista as pv
    sc.add("line floor", pv.Plane(center=(1200, -900, -1.5), direction=(0, 0, 1), i_size=34000, j_size=18000),
           A.FLOOR_C, "floor", ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
    rigs = {}
    for k, loads in TRAY_LOADS.items():
        add_tray(sc, L, k)
        for key, x, y in loads:
            inst, ents = idata[key]
            x0, x1, y0, y1, z0, _ = inst.bbox()
            at = T((x - (x0 + x1) / 2, y - (y0 + y1) / 2, V.T_FLOOR - z0))
            rigs[key] = tour.Rig(sc, inst, ents, f"{k}_{key}:", at=at, parent=f"tray_{k}")
            L.eq_groups[k].append(f"{k}_{key}:body")
    for key, x in LINE.items():
        if key == "aconity":
            ents = aconity_entries()
            pts = np.vstack([e["mesh"].points for e in ents.values() if e["mesh"].n_points])
            lo, hi = pts.min(0), pts.max(0)
            for n, e in ents.items():
                sc.add(n, e["mesh"], e["color"], "aconity", opacity=e["opacity"])
            sc.gmat["aconity"] = place_floor((lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]), x)
            continue
        inst, ents = idata[key]
        rigs[key] = tour.Rig(sc, inst, ents, f"line_{key}:", at=place_floor(inst.bbox(), x))
    rail = I.rail(length=RAIL_X[1] - RAIL_X[0], travel=1.0)
    rents = tour.piece_entries(rail)
    rc = (RAIL_X[0] + RAIL_X[1]) / 2
    rigs["rail"] = tour.Rig(sc, rail, rents, "rail:", at=T((rc, RAIL_Y, 0)))
    rigs["rail"].v["carriage"] = PARK_X - rc            # the carriage's joint is in mm along x (travel = 1 mm)
    rigs["rail"].apply()
    import robot
    L.robot = robot.Robot(sc, A.ROBOT, "rail:carriage", T((0, 0, I.RAIL["top"])), q0=A.PARK_DEG, prefix="ur")
    L.apply_state()
    return sc, L, rigs


def line_labels(xs=None):
    out = []
    for key, x in LINE.items():
        if xs is not None and not (xs[0] <= x <= xs[1]):
            continue
        z = {"glovebox": 1900, "aconity": 2400, "instron_floor": 2300, "instron_small": 1450, "wire_edm": 2000}[key]
        out.append((NAMES[key], (x, Y_FACE + 300, z), None))
    return out


def lab_at(lbls, fy=0.10):
    """Spread leader labels across the top of the frame, right of the tray table, left to right in x order."""
    lbls = sorted(lbls, key=lambda l: l[1][0])
    n = len(lbls)
    return [(t, xyz, (0.27 + 0.70 * i / max(n - 1, 1) if n > 1 else 0.6, fy + 0.065 * (i % 3)))
            for i, (t, xyz, _) in enumerate(lbls)]


def mp4_to_gif(mp4, gif, fps=6, width=720, lossy=80):
    """The GIF from the MP4: 720 px wide at 6 fps, one palette, gifsicle --lossy. A 70 s movie at the scenes' own GIF
    settings comes out near 15 MB."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        pal = f"{tmp}/pal.png"
        vf = f"fps={fps},scale={width}:-1:flags=lanczos"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4), "-vf",
                        f"{vf},palettegen=max_colors=128:stats_mode=diff", pal], check=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4), "-i", pal, "-lavfi",
                        f"{vf}[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle", f"{tmp}/raw.gif"], check=True)
        subprocess.run(["gifsicle", "-O3", f"--lossy={lossy}", "-o", str(gif), f"{tmp}/raw.gif"], check=True)
    return f"{gif}: {gif.stat().st_size / 1e6:.1f} MB"


def movie(data, idata):
    sc, L, rigs = build("vlm_line", data, idata)
    rail = rigs["rail"]
    rc = (RAIL_X[0] + RAIL_X[1]) / 2
    L.skin(0.0)(1.0)
    L.apply_state()
    n = 7
    sc.step(f"1/{n}", "The backup layout: the alloy equipment in a line with the VLM, every front facing the same way, "
            "along a floor rail. The VLM now holds six trays: round 2's three and three for characterization.", 3.2,
            None, hold=1.4,
            labels=lab_at(line_labels() + [A.REPOWDER_LBL[:2] + (None,),
                                           ("Kardex Shuttle XP 500, six trays", (0, Y_FACE, 3950), None)]))
    sc.step(f"2/{n}", "The cladding drawn see-through: trays D, E and F take the instruments that fit through the "
            "727.5 mm opening.", 2.4, L.skin(1.0), hold=0.6, cam_to=CAM_VLM,
            labels=[(f"tray {k}: {EXTRA[k][1]}", (V.TRAY_W / 2 - 200, *V.SLOTS[EXTRA[k][0]]), (0.84, 0.18 + 0.14 * i))
                    for i, k in enumerate(("F", "E", "D"))])
    steps = {"D": "Tray D: the Hitachi TM4000PlusII SEM (EDS; EBSD proposed), the Rigaku MiniFlex XRD and the two "
                  "OpenFlexure microscopes, in reflection.",
             "E": "Tray E: the Plastometrex PLX-Benchtop (PIP), the KLA iMicro nanoindenter and the Malvern Mastersizer "
                  "3000 with its Aero S.",
             "F": "Tray F: the Buehler EcoMet 30 polisher and the Nabertherm NAT 15/65 furnace."}
    cam = CAM_OPEN
    for i, k in enumerate(("D", "E", "F")):
        L.fetch(k, f"3/{n}", f"Tray {k} comes to the opening.", fast=0.6, cam=cam, hold=0.2)
        cam = None
        lbl = []
        for key, x, y in TRAY_LOADS[k]:
            inst, _ = idata[key]
            lbl.append((inst.model, A.tray_world(k, (x, y, inst.bbox()[5] + 20)), None))
        sc.step(f"3/{n}", steps[k], 2.4, None, hold=1.0, labels=lab_at(lbl, fy=0.14))
        L.store(k, f"3/{n}", f"Tray {k} goes back to its slot ({A.HOME[k]}), where it has power.", fast=0.6, hold=0.1)
    sc.step(f"4/{n}", "Left of the VLM: the inert glovebox, its automatic antechamber facing along the line, and the "
            "rePowder ultrasonic atomizer.", 3.0, None, hold=1.2, cam_to=CAM_LEFT,
            labels=lab_at(line_labels((-9000, -3000)) + [A.REPOWDER_LBL[:2] + (None,)]))
    sc.step(f"5/{n}", "Right of it: the Aconity MIDI, the floor and tabletop Instrons (neither fits a tray: the "
            "shortest Instron frame is 1020 mm tall) and the wire EDM that cuts parts off their build plates.", 3.4,
            None, hold=1.2, cam_to=CAM_RIGHT, labels=lab_at(line_labels((2000, 11000))))
    sc.step(f"6/{n}", "The backup to the mobile base: a Vention rack-and-pinion seventh axis along the fronts, the "
            "UR10e on its carriage at 800 mm, as on the MiR250. It can carry the arm from machine to machine.", 3.4,
            rail.move({"carriage": (None, LINE["instron_floor"] - rc)}), hold=0.6,
            labels=[("Vention 7th axis", (6500, RAIL_Y, 700), (0.70, 0.75))])
    sc.step(f"6/{n}", "Not used by any workflow yet: it parks at the VLM's opening, where the MiR250 parks.", 3.2,
            rail.move({"carriage": (None, PARK_X - rc)}), hold=0.4, cam_to=CAM_VLM)
    sc.step(f"7/{n}", "The whole line, about 17 m along the rail.", 2.4, None, hold=2.4, cam_to=CAM_LINE, still=True,
            labels=lab_at(line_labels() + [A.REPOWDER_LBL[:2] + (None,),
                                           ("VLM: trays A-F", (0, Y_FACE, 3950), None)]))
    return sc.save()


if __name__ == "__main__":
    from scene import OUT, PREVIEW
    data = lab.meshes()
    idata = tour.load()
    print(movie(data, idata), flush=True)
    if not PREVIEW:
        print(mp4_to_gif(OUT / "mp4" / "vlm_line.mp4", OUT / "vlm_line.gif"), flush=True)
