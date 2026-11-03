"""Trays G (resin printing), H (PCB assembly) and I (desktop LPBF), and the compact metal printers measured against
the Shuttle's opening (#303).

    xvfb-run -a python3 fab_trays.py           # -> out/vlm_fab_trays.gif, out/mp4/vlm_fab_trays.mp4, out/vlm_fab_trays_still.png
    PREVIEW=1 xvfb-run -a python3 fab_trays.py # the last frame of each sub-step -> /tmp/preview_vlm_fab_trays.png

Each tray is the Kardex tray of ``vlm.tray`` with its equipment from ``fab_resin.py``, ``fab_pcb.py`` and ``fab_metal.py``
(``fab_tour.load``),
fronts to the tray's front edge, where the arm works. Over each tray, a blue box is what goes through the opening: the
tray's inside (2426 x 840 mm) by Kardex's 727.5 mm of product height. Behind them, the next most compact LPBF machines
and the most compact DED found (``fab_metal.py``) stand on boxes of the same height.

The Shuttle's six slots are full (trays A-F), so trays G, H and I need another Shuttle: see the README.
"""
from __future__ import annotations

import cadquery as cq
import numpy as np
import pyvista as pv

import fab_tour
import lab
import tour
import vlm as V
from scene import OUT, PREVIEW, R, Scene, T

TITLE = "Vertical cloud lab: resin printing, PCB assembly and desktop LPBF on trays, and the metal printers that don't fit"
H_MAX = 727.5                                   # Kardex's product height through the opening (order sheet)
IN_W, IN_D = V.TRAY_W - 24.0, V.TRAY_D - 24.0   # inside the tray's rim
TRAYS = {"G": (-2600.0, "resin printing"), "H": (0.0, "PCB assembly"), "I": (2600.0, "desktop LPBF")}
# what goes on each tray, in the tray's frame (centre of its floor, y to the back): (key, x, y, turn about z, degrees)
LOADS = {
    "G": [("form4", -920.0, None, 0.0), ("form4", -470.0, None, 0.0), ("form_wash", -40.0, None, 0.0),
          ("form_cure", 360.0, None, 0.0)],
    "H": [("stencil", -640.0, 0.0, 90.0), ("lumenpnp", 400.0, 0.0, 0.0)],
    "I": [("snowpod", -500.0, None, 0.0), ("snowpod", 300.0, None, 0.0)],
}
METAL = [("metalone", -2200.0), ("meltio_m450", 0.0), ("mprint", 2200.0)]    # (key, x), fronts on METAL_Y
METAL_Y = 1150.0
BLUE = (0.30, 0.55, 0.90)
CAM_ALL = [(-2000, -8200, 4600), (0, 450, 650), (0, 0, 1)]
CAM_G = [(-2100, -4400, 3300), (-2600, -60, 260), (0, 0, 1)]
CAM_H = [(500, -4400, 3300), (0, -60, 260), (0, 0, 1)]
CAM_I = [(3100, -4400, 3300), (2600, -60, 300), (0, 0, 1)]
CAM_METAL = [(2600, -6900, 3100), (0, METAL_Y + 300, 950), (0, 0, 1)]


def add_tray(sc: Scene, k: str, x: float):
    V.TRAYS.setdefault(k, dict(kind="extra", role=TRAYS[k][1]))
    for name, (shape, mat, group) in {**V.tray(k), **V.lamp(k)}.items():
        if hasattr(shape, "vals"):
            shape = shape.val() if len(shape.vals()) == 1 else cq.Compound.makeCompound(shape.vals())
        e = lab._entry(lab.to_mesh(shape, 2.0), mat, group)
        sc.add(name, e["mesh"], e["color"], group, opacity=e["opacity"])
    sc.gmat[f"tray_{k}"] = T((x, 0, 0))


def envelope(sc: Scene, name: str, x0, x1, y0, y1, z0, group="static", color=BLUE, strength=1.0):
    """A see-through box of the opening's product height, and its lid a little stronger."""
    sc.add(f"{name} box", pv.Box(bounds=(x0, x1, y0, y1, z0, z0 + H_MAX)), color, group, opacity=0.07 * strength,
           specular=0.0, ambient=0.6)
    sc.add(f"{name} lid", pv.Box(bounds=(x0, x1, y0, y1, z0 + H_MAX - 3, z0 + H_MAX)), color, group,
           opacity=min(0.35 * strength, 0.8), specular=0.0, ambient=0.6)


def placed(inst, x, y, turn, z) -> np.ndarray:
    """An instrument's own frame -> (x, y) on a surface at z, turned about z; y None: its front 30 mm behind the lip."""
    x0, x1, y0, y1, z0, _ = inst.bbox()
    c = np.array([(x0 + x1) / 2, (y0 + y1) / 2, z0])
    if y is None:
        y = -IN_D / 2 + 30 + (y1 - y0) / 2
    return T((x, y, z)) @ R((0, 0, 1), turn) @ T(-c)


def build(name="vlm_fab_trays"):
    keys = {k for loads in LOADS.values() for k, *_ in loads} | {k for k, _ in METAL}
    data = fab_tour.load(keys)
    sc = Scene(name, TITLE, gif=False)
    sc.cam = list(CAM_ALL)
    tour.studio(sc, size=16000, at=(0, 600))
    rigs = {}
    for k, (tx, role) in TRAYS.items():
        add_tray(sc, k, tx)
        envelope(sc, f"tray {k}", -IN_W / 2, IN_W / 2, -IN_D / 2, IN_D / 2, V.T_FLOOR, group=f"tray_{k}")
        for i, (key, x, y, turn) in enumerate(LOADS[k]):
            if key not in data:
                print("  missing", key)
                continue
            inst, ents = data[key]
            rigs[f"{k}{i}"] = tour.Rig(sc, inst, ents, f"{k}{i}_{key}:", at=placed(inst, x, y, turn, V.T_FLOOR),
                                       parent=f"tray_{k}")
    for key, x in METAL:
        if key not in data:
            print("  missing", key)
            continue
        inst, ents = data[key]
        x0, x1, y0, y1, _, _ = inst.bbox()
        at = placed(inst, x, METAL_Y + (y1 - y0) / 2, 0.0, 0.0)
        rigs[key] = tour.Rig(sc, inst, ents, f"metal_{key}:", at=at)
        w, d = x1 - x0, y1 - y0
        envelope(sc, f"metal {key}", x - w / 2 - 20, x + w / 2 + 20, METAL_Y - 20, METAL_Y + d + 20, 0.0,
                 color=(0.88, 0.30, 0.25), strength=1.8)
    return sc, data, rigs


def first_action(rig) -> dict:
    """The targets of an instrument's first captioned action: the cover opening, the board going on, and so on."""
    for cap, _, targets in rig.inst.actions:
        if cap:
            return targets
    return {}


def movie():
    sc, data, rigs = build()

    def both(*names):
        ups = [rigs[n].move(first_action(rigs[n])) for n in names if n in rigs]
        return lambda u: [f(u) for f in ups]

    def model(key):
        return data[key][0].model if key in data else key

    n = 6
    sc.step(f"1/{n}", "Three more trays. The blue boxes are what fits through the Shuttle's opening: the tray's inside, "
            "2426 x 840 mm, by 727.5 mm of product height. The metal printers behind stand on red boxes of the same "
            "height.", 3.4, None, hold=1.6,
            labels=[("tray G: resin printing", (TRAYS["G"][0] - 900, -IN_D / 2, H_MAX + 40), (0.16, 0.20)),
                    ("tray H: PCB assembly", (TRAYS["H"][0], -IN_D / 2, H_MAX + 40), (0.48, 0.14)),
                    ("tray I: desktop LPBF", (TRAYS["I"][0] + 900, -IN_D / 2, H_MAX + 40), (0.80, 0.20)),
                    ("727.5 mm", (TRAYS["I"][0] + IN_W / 2, -IN_D / 2, H_MAX), (0.92, 0.50))])
    sc.step(f"2/{n}", "Tray G: two Formlabs Form 4s, a Form Wash and a Form Cure, in the order a print goes. Every one "
            "fits closed. The Form 4's cover opens to 844 mm and the Form Cure's door swings out, so they open only at "
            "the opening, where there is about 845 mm under the header.", 4.2, both("G0", "G2", "G3"), hold=1.2,
            cam_to=CAM_G,
            labels=[(model("form4"), (TRAYS["G"][0] - 920, -150, 600), (0.16, 0.22)),
                    (model("form_wash"), (TRAYS["G"][0] - 40, -150, 420), (0.52, 0.16)),
                    (model("form_cure"), (TRAYS["G"][0] + 360, -150, 420), (0.84, 0.24))])
    sc.step(f"3/{n}", "Tray H: the DDM Novastar SPR-45VA stencil printer, turned 90 degrees because it is 889 mm deep "
            "against the tray's 840, and the open-source Opulo LumenPnP v4. The right end is free for a reflow oven.",
            4.2, both("H0", "H1"), hold=1.2, cam_to=CAM_H,
            labels=[(model("stencil"), (TRAYS["H"][0] - 640, 0, 450), (0.20, 0.22)),
                    (model("lumenpnp"), (TRAYS["H"][0] + 400, 0, 470), (0.74, 0.22))])
    sc.step(f"4/{n}", "Tray I: two SnowX SnowPods, desktop LPBF, 660 mm tall: the only powder-bed printer found that "
            "goes through the opening, with 67.5 mm to spare. Each makes its own nitrogen from air with a NitroPod, so "
            "the tray needs only power. A Kickstarter kit: not shipping yet.", 4.4, both("I0", "I1"), hold=1.4,
            cam_to=CAM_I,
            labels=[(model("snowpod"), (TRAYS["I"][0] - 500, -150, 700), (0.30, 0.20)),
                    (model("snowpod"), (TRAYS["I"][0] + 300, -150, 700), (0.62, 0.20))])
    metal = [(f"{model(k)}, {data[k][0].size[2]:.0f} mm tall", (x, METAL_Y, data[k][0].size[2]),
              (0.18 + 0.32 * i, 0.16 + 0.06 * (i % 2))) for i, (k, x) in enumerate(METAL) if k in data]
    sc.step(f"5/{n}", "The other metal printers: Sharebot's MetalONE and One Click Metal's MPRINT (LPBF), and Meltio's "
            "M450, wire and laser, the most compact DED found. Each stands well above its red box, so none goes "
            "through the opening; they stand in the line with the Aconity MIDI.", 4.4, None,
            hold=1.6, cam_to=CAM_METAL, labels=metal)
    sc.step(f"6/{n}", "The Shuttle's six slots already hold trays A-F, so trays G, H and I need a second Shuttle.", 2.8,
            None, hold=2.2, cam_to=CAM_ALL, still=True,
            labels=[(f"tray {k}", (TRAYS[k][0], -IN_D / 2, H_MAX + 40), (0.20 + 0.30 * i, 0.22))
                    for i, k in enumerate(TRAYS)])
    return sc.save()


if __name__ == "__main__":
    import line
    print(movie(), flush=True)
    if not PREVIEW:
        print(line.mp4_to_gif(OUT / "mp4" / "vlm_fab_trays.mp4", OUT / "vlm_fab_trays.gif"), flush=True)
