"""Vertical lift module animations: assembly, operation and disassembly of a Kardex Shuttle XP 500
holding the lab's equipment on three electrified trays.

    xvfb-run -a python3 animate.py assembly      # -> out/vlm_assembly.gif, out/mp4/vlm_assembly.mp4
    xvfb-run -a python3 animate.py operation     # -> out/vlm_operation.gif, ...
    xvfb-run -a python3 animate.py disassembly   # -> out/vlm_disassembly.gif, ...
    PREVIEW=1 xvfb-run -a python3 animate.py assembly   # last frame of each sub-step -> /tmp/preview_*.png

``lab.py`` tessellates the models once and caches them in ``.cache/``. Every move is a real one:
parts go on along their assembly paths, trays only ever move on their supports, on the extractor
or through the opening, and equipment goes in and out through the opening.
"""
from __future__ import annotations

import sys

import numpy as np
import pyvista as pv

import lab
import vlm as V
from scene import FPS, Scene, T, R, S, mix

TITLE = "Vertical cloud lab: Kardex Shuttle XP 500 vertical lift module"
LIFT_HOME = V.SLOTS["open"][1]
Z_BELT_TOP = V.Z_TOP_IN + 140
GREEN, OFF = (0.20, 0.85, 0.35), (0.30, 0.32, 0.30)

# what goes on each tray: (equipment key, x, y) in the tray's frame; y = 0 is the tray's centre line
LOADS = {
    "A": [("ot2", -560.0, 0.0), ("cubxl", 560.0, 0.0)],
    "B": [("doser_station", -700.0, 0.0), ("doser_station", 0.0, 0.0), ("doser_station", 700.0, 0.0)],
    "C": [("h2d", -560.0, 0.0), ("a1mini", 360.0, 0.0)],
}
ROLE = {"A": "liquid handling", "B": "powder dosing", "C": "3D printing"}
NAMES = {"ot2": "Opentrons OT-2", "cubxl": "CubXL", "doser_station": "powder doser on an HR-100A",
         "h2d": "Bambu Lab H2D", "a1mini": "Bambu Lab A1 mini"}
HOME = {"A": "R2", "B": "R3", "C": "F1"}       # storage slot of each tray
CAM_WIDE = [(7570, -6720, 4790), (0, -250, 1800), (0, 0, 1)]
CAM_OPEN = [(5200, -7600, 3100), (100, -900, 1450), (0, 0, 1)]
CAM_LOW = [(7600, -8200, 3900), (0, -500, 1500), (0, 0, 1)]

FLOOR_C = (0.965, 0.965, 0.96)


class Lab:
    """The scene plus the state of the machine: where each tray is, the extractor's height, the shutter."""

    def __init__(self, sc: Scene, data: dict):
        self.sc = sc
        self.tray = {k: [*V.SLOTS[HOME[k]]] for k in V.TRAYS}      # [y, z] of each tray
        self.where = dict(HOME)                                     # slot name, or None in transit
        self.lift_z = LIFT_HOME
        self.shutter = 0.0
        self.eq_groups: dict[str, list[str]] = {k: [] for k in V.TRAYS}
        self.show_gauges = True
        self._build(data)

    # ---------------------------------------------------------------------------------- scene
    def _build(self, data):
        sc = self.sc
        floor = pv.Plane(center=(0, -600, -1), direction=(0, 0, 1), i_size=16000, j_size=14000)
        sc.add("floor", floor, FLOOR_C, "floor", ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
        shadow = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=V.UNIT_W + 900, j_size=V.UNIT_D + 900)
        sc.add("floor shadow", shadow, (0.90, 0.90, 0.895), "floor", ambient=1.0, diffuse=0.0, specular=0.0,
               smooth_shading=False)
        for name, e in data["vlm"].items():
            kw = {}
            if e["material"] in ("vlm_skin",):
                kw = dict(specular=0.05, ambient=0.35)
            if e["material"] == "vlm_led":
                kw = dict(ambient=0.9, diffuse=0.2)
            sc.add(name, e["mesh"], e["color"], e["group"], opacity=e["opacity"], **kw)
        eq = data["equipment"]
        for k, loads in LOADS.items():
            for i, (key, x, y) in enumerate(loads):
                g = f"eq_{k}{i}"
                parts = self._station(eq) if key == "doser_station" else [(eq[key], np.eye(4))]
                for (entries, bb), m in parts:
                    cx, cy = (bb[0] + bb[1]) / 2, (bb[2] + bb[3]) / 2
                    for name, e in entries.items():
                        mesh = e["mesh"].copy().transform(T((-cx, -cy, -bb[4])) if key != "doser_station" else m,
                                                         inplace=False)
                        sc.add(f"{g}/{name}", mesh, e["color"], g, opacity=e["opacity"])
                sc.parent[g] = f"tray_{k}"
                sc.gmat[g] = T((x, y, V.T_FLOOR))
                self.eq_groups[k].append(g)
        # the operator: AgileX's PiPER (vendor STEP, as it ships) on a mobile stand against the counter
        pe, pbb = eq["piper"]
        piper = []
        for name, e in pe.items():
            m = e["mesh"]
            if m.n_cells > 150000:      # AgileX's STEP tessellates to ~0.5 M triangles; 85% fewer look the same here
                m = pv.PolyData(m.points, m.faces).decimate(0.85)
            piper.append((name, m, e))
        stand_y = -V.UNIT_D / 2 - V.SKIN - 160 - 190
        self.op_xy = (-700.0, stand_y)
        for name, m, e in piper:
            sc.add(f"op/{name}", m.transform(R((0, 0, 1), 180) if (pbb[2] + pbb[3]) / 2 < 0 else np.eye(4),
                                              inplace=False), e["color"], "op_arm", opacity=e["opacity"])
        stand = pv.Box(bounds=(-110, 110, -110, 110, 120, 880))
        top = pv.Box(bounds=(-160, 160, -160, 160, 880, 900))
        sc.add("op/stand", stand.merge(top), (0.70, 0.71, 0.73), "op")
        base = pv.Box(bounds=(-230, 230, -230, 230, 50, 120))
        sc.add("op/base", base, (0.23, 0.24, 0.26), "op")
        wheels = None
        for sx in (-1, 1):
            for sy in (-1, 1):
                w = pv.Cylinder(center=(sx * 185, sy * 185, 25), direction=(1, 0, 0), radius=25, height=30)
                wheels = w if wheels is None else wheels.merge(w)
        sc.add("op/wheels", wheels, (0.12, 0.12, 0.13), "op")
        sc.gmat["op"] = T((*self.op_xy, 0))
        sc.parent["op_arm"] = "op"
        sc.gmat["op_arm"] = T((0, 0, 900))
        self.apply_state()

    def _station(self, eq):
        """A dosing station: the HR-100A, a bridge over it, and the lab's doser on the bridge."""
        bal, bbb = eq["balance"]
        dos, dbb = eq["doser"]
        h_bal = bbb[5] - bbb[4]
        bridge_h = h_bal + 70.0
        bal_m = T((-(bbb[0] + bbb[1]) / 2, -(bbb[2] + bbb[3]) / 2, -bbb[4]))
        # the doser's outlet end (+y in its frame) over the middle of the balance
        dos_m = T((-(dbb[0] + dbb[1]) / 2, -dbb[3] + 150.0, bridge_h + 12 - dbb[4]))
        legs = None
        for sx in (-1, 1):
            for sy in (-1, 1):
                leg = pv.Box(bounds=(sx * 132.5 - 10, sx * 132.5 + 10, sy * 150 - 10, sy * 150 + 10, 0, bridge_h))
                legs = leg if legs is None else legs.merge(leg)
        plate = pv.Box(bounds=(-150, 150, -170, 170, bridge_h, bridge_h + 12))
        bridge = {"bridge": dict(mesh=legs.merge(plate), color=(0.70, 0.71, 0.73), opacity=1.0)}
        return [((bal, bbb), bal_m), ((dos, dbb), dos_m), ((bridge, (0, 0, 0, 0, 0, 0)), np.eye(4))]

    # ---------------------------------------------------------------------------------- state
    def apply_state(self):
        sc = self.sc
        for k, (y, z) in self.tray.items():
            sc.gmat[f"tray_{k}"] = T((0, y, z))
            on = self.where[k] is not None
            sc.color[f"tray {k} lamp"] = GREEN if on else OFF
            sc.ambient[f"tray {k} lamp"] = 0.9 if on else 0.2
        sc.gmat["lift"] = T((0, 0, self.lift_z))
        L = max(1.0, Z_BELT_TOP - (self.lift_z + 40))
        sc.gmat["belts"] = T((0, 0, self.lift_z + 40)) @ S((1, 1, L))
        sc.gmat["shutter"] = T((0, 0, self.shutter * (V.Z_OPEN_TOP - V.Z_SILL + 10)))
        self.gauges()

    def gauges(self):
        g = []
        if not self.show_gauges:
            self.sc.gauges = []
            return
        for k in V.TRAYS:
            w = self.where[k]
            if w is None:
                state = "moving, unpowered"
            elif w == "open":
                state = "at the opening, powered"
            else:
                state = f"stored ({w}), powered"
            g.append((f"Tray {k}", f"{state}"))
        self.sc.gauges = g

    # ---------------------------------------------------------------------------------- moves
    def lift_to(self, z, carry=None):
        z0 = self.lift_z

        def up(u):
            self.lift_z = z0 + (z - z0) * u
            if carry:
                self.tray[carry][1] = self.lift_z
            self.apply_state()
        return up

    def slide(self, k, y1):
        y0 = self.tray[k][0]

        def up(u):
            self.tray[k][0] = y0 + (y1 - y0) * u
            self.apply_state()
        return up

    def shut(self, f1):
        f0 = self.shutter

        def up(u):
            self.shutter = f0 + (f1 - f0) * u
            self.apply_state()
        return up

    def fetch(self, k, label, caption, to="open", fast=1.0, cam=None, hold=0.4):
        """Extractor goes to tray k's slot, pulls it on, carries it to `to` and pushes it in."""
        sc = self.sc
        ys, zs = V.SLOTS[self.where[k]]
        yt, zt = V.SLOTS[to]
        if abs(self.lift_z - zs) > 1:
            sc.step(label, caption, max(0.6, abs(self.lift_z - zs) / 1333 * fast), self.lift_to(zs), hold=0.1,
                    cam_to=cam)
            cam = None
        self.where[k] = None
        self.apply_state()
        sc.step(label, caption, 2.2 * fast, self.slide(k, 0.0), hold=0.1, cam_to=cam)
        sc.step(label, caption, max(0.6, abs(zs - zt) / 1333 * fast), self.lift_to(zt, carry=k), hold=0.1)
        sc.step(label, caption, 2.2 * fast, self.slide(k, yt), hold=0.0)
        self.where[k] = to
        self.apply_state()
        sc.snap(max(1, int(round(hold * FPS))))

    def store(self, k, label, caption, fast=1.0, cam=None, hold=0.3):
        """Tray k from the opening back to its home slot."""
        self.where[k] = None
        self.apply_state()
        ys, zs = V.SLOTS[HOME[k]]
        self.sc.step(label, caption, 2.2 * fast, self.slide(k, 0.0), hold=0.1, cam_to=cam)
        self.sc.step(label, caption, max(0.6, abs(self.lift_z - zs) / 1333 * fast), self.lift_to(zs, carry=k), hold=0.1)
        self.sc.step(label, caption, 2.2 * fast, self.slide(k, ys), hold=0.0)
        self.where[k] = HOME[k]
        self.apply_state()
        self.sc.snap(max(1, int(round(hold * FPS))))

    # ------------------------------------------------------------------------------- visibility
    def groups(self, *pats):
        out = []
        for n, g in self.sc.group_of.items():
            if any(g == p or (p.endswith("*") and g.startswith(p[:-1])) for p in pats):
                out.append(n)
        return out

    def fade(self, names, a0, a1):
        def up(u):
            for n in names:
                self.sc.alpha[n] = a0 + (a1 - a0) * u
        return up


def both(*fs):
    def up(u):
        for f in fs:
            f(u)
    return up


def slide_in(L: Lab, groups, offset, names=None, out=False):
    """Groups slide along `offset` into place (or out of it) while fading in (or out)."""
    sc = L.sc
    base = {g: sc.gmat.get(g, np.eye(4)).copy() for g in groups}
    names = names if names is not None else L.groups(*groups)
    off = np.asarray(offset, float)

    def up(u):
        v = u if out else 1.0 - u
        for g in groups:
            sc.gmat[g] = T(off * v) @ base[g]
        for n in names:
            sc.alpha[n] = 1.0 - min(1.0, v * 1.6) if not out else max(0.0, 1.0 - v * 1.6)
    return up


def equipment_in(L: Lab, k, out=False):
    """Tray k's equipment comes in through the opening (or goes out), lifted 20 mm over the tray floor."""
    sc = L.sc
    gs = L.eq_groups[k]
    base = {g: sc.gmat[g].copy() for g in gs}
    names = L.groups(*gs)
    travel = 1700.0

    def up(u):
        v = u if out else 1.0 - u
        lift = min(1.0, v * 6) * 20.0
        for i, g in enumerate(gs):
            # staggered, the last piece first, so they don't pass through each other
            s = min(1.0, max(0.0, v * 1.3 - (len(gs) - 1 - i) * 0.15)) if not out else \
                min(1.0, max(0.0, v * 1.3 - i * 0.15))
            sc.gmat[g] = T((0, -travel * s, lift)) @ base[g]
            for n in L.groups(g):
                sc.alpha[n] = 1.0 if s < 0.75 else max(0.0, 1 - (s - 0.75) * 4)
    return up


# ======================================================================================= chapters
def new_scene(name, data) -> tuple[Scene, Lab]:
    sc = Scene(name, TITLE)
    sc.cam = list(CAM_WIDE)
    L = Lab(sc, data)
    return sc, L


def assembly(data):
    sc, L = new_scene("vlm_assembly", data)
    eq = [n for k in V.TRAYS for n in L.groups(*L.eq_groups[k])]
    vlm_groups = ["base", "posts", "col_front", "col_rear", "lift_rails", "drive", "lift", "belts", "bay", "console",
                  "shutter", "skin_L", "skin_R", "skin_back", "skin_front", "skin_top", "tray_A", "tray_B", "tray_C"]
    for n in L.groups(*vlm_groups, "op", "op_arm") + eq:
        sc.alpha[n] = 0.0
    L.show_gauges = False
    L.apply_state()
    n = 9
    sc.step(f"1/{n}", "The Kardex Shuttle XP 500 quoted in #53: 2450 × 864 mm trays in a 2780 × 3074 mm module, 3950 mm "
            "tall to stay under 13 ft. The base frame goes down first, on levelling feet.",
            2.0, slide_in(L, ["base"], (0, 0, 900)), hold=1.2,
            labels=[("base frame, 2780 × 3074 mm", (V.UNIT_W / 2, -V.UNIT_D / 2, 100), (0.80, 0.80))])
    sc.step(f"2/{n}", "Posts and roof rails. The posts at the middle of each side mark off the three bays: front "
            "storage, the extractor's shaft and rear storage.",
            2.0, slide_in(L, ["posts"], (0, 0, 1800)), hold=1.0,
            labels=[("front storage", (V.UNIT_W / 2, V.Y_FRONT, V.UNIT_H), (0.83, 0.20)),
                    ("extractor shaft", (V.UNIT_W / 2, 0, V.UNIT_H), (0.86, 0.28)),
                    ("rear storage", (V.UNIT_W / 2, V.Y_REAR, V.UNIT_H), (0.88, 0.36))])
    sc.step(f"3/{n}", "Storage columns. Trays rest on supports on a 25 mm pitch (drawn every 100 mm here), so a tray "
            "takes only the height its equipment needs. The front column leaves a gap for the access opening.",
            2.4, slide_in(L, ["col_front", "col_rear"], (2600, 0, 0)), hold=1.4,
            labels=[("rear column: tray supports", (V.TRAY_W / 2, V.Y_REAR, 2600), (0.86, 0.30)),
                    ("front column", (V.TRAY_W / 2, V.Y_FRONT, 2600), (0.84, 0.48)),
                    ("gap for the opening", (V.TRAY_W / 2, V.Y_FRONT, 1300), (0.84, 0.66))])
    sc.step(f"4/{n}", "The extractor: guide rails in the shaft, the drive on the roof frame (motor, cross shaft, two "
            "belt pulleys), then the platform on its belts. It carries one tray at a time.",
            2.6, both(slide_in(L, ["lift_rails"], (0, 0, 2500)), slide_in(L, ["drive"], (0, 0, 1400)),
                      slide_in(L, ["lift", "belts"], (0, 0, 2400))), hold=1.4,
            labels=[("drive on the roof frame", (V.UNIT_W / 2 - 700, 0, V.Z_TOP_IN + 150), (0.80, 0.16)),
                    ("extractor platform", (V.TRAY_W / 2, 0, LIFT_HOME - 60), (0.86, 0.62))])
    trays_lbl = [(f"tray {k}: {V.TRAYS[k]['kind']}, {V.TRAYS[k]['capacity_lb']} lb", (V.TRAY_W / 2, *V.SLOTS[HOME[k]]),
                  (0.86, 0.30 + 0.12 * i)) for i, k in enumerate(V.TRAYS)]
    sc.step(f"5/{n}", "Three electrified trays (#53): strong (1080 lb), medium (794 lb) and light (502 lb). Each has a "
            "power strip and a socket; it has power in its slot and at the opening, not while it moves.",
            2.4, slide_in(L, ["tray_A", "tray_B", "tray_C"], (3200, 0, 0)), hold=1.6, labels=trays_lbl)
    sc.step(f"6/{n}", "Cladding, the access opening with its light curtains and LED bar, the operator console, and the "
            "powered safety shutter behind the front panel. The panels are drawn see-through.",
            2.6, both(slide_in(L, ["skin_L"], (-900, 0, 0)), slide_in(L, ["skin_R"], (900, 0, 0)),
                      slide_in(L, ["skin_back"], (0, 900, 0)), slide_in(L, ["skin_top"], (0, 0, 900)),
                      slide_in(L, ["skin_front", "bay", "console", "shutter"], (0, -900, 0))), hold=1.4,
            labels=[("access opening", (0, -V.UNIT_D / 2, 1300), (0.20, 0.62)),
                    ("operator console", (V.TRAY_W / 2 + 390, -V.UNIT_D / 2 - 120, 1330), (0.84, 0.70)),
                    ("operation counter", (-900, -V.UNIT_D / 2 - 100, V.Z_SILL), (0.18, 0.80))])
    # loading: each tray comes to the opening, its equipment goes in through it, and it goes home
    L.show_gauges = True
    for i, k in enumerate(("A", "B", "C")):
        items = ", ".join(sorted({NAMES[key] for key, _, _ in LOADS[k]}, key=lambda s: s))
        step = f"{7 + i}/{n}"
        cap = f"Loading tray {k} ({ROLE[k]}): the extractor brings it to the opening and the equipment goes in through " \
              f"it: {items}."
        L.fetch(k, step, cap, fast=0.8 if i else 1.0, cam=CAM_OPEN if i == 0 else None)
        sc.step(step, cap, 1.0, L.shut(1.0), hold=0.1)
        sc.step(step, cap, 2.4, equipment_in(L, k), hold=0.8,
                labels=[(f"{NAMES[key]}", (x, V.Y_OPEN + y, V.Z_OPEN + 700), (0.10 + 0.27 * j, 0.20))
                        for j, (key, x, y) in enumerate(LOADS[k]) if key != "doser_station" or j == 1])
        sc.step(step, cap, 1.0, L.shut(0.0), hold=0.1)
        L.store(k, step, cap, fast=0.8, cam=CAM_WIDE if i == 2 else None)
    sc.step(f"{n}/{n}", "The operator rolls up: an AgileX PiPER arm (AgileX's own STEP) on a mobile stand, its base "
            "level with the counter. A person can work the opening the same way.",
            1.8, slide_in(L, ["op", "op_arm"], (0, -1500, 0)), hold=1.2,
            labels=[("AgileX PiPER", (L.op_xy[0], L.op_xy[1], 1200), (0.14, 0.40))])
    sc.step(f"{n}/{n}", "Assembled and loaded: liquid handling on tray A, powder dosing on tray B, 3D printing on tray C. "
            "Each tray is powered in its slot, so the equipment on it can keep running while it is stored.",
            1.5, None, hold=3.0, cam_to=CAM_WIDE, still=True,
            labels=[(f"tray {k}: {ROLE[k]}", (V.TRAY_W / 2 - 300, *V.SLOTS[HOME[k]]), (0.86, 0.30 + 0.12 * i))
                    for i, k in enumerate(V.TRAYS)])
    return sc.save()


def operation(data):
    sc, L = new_scene("vlm_operation", data)
    L.apply_state()
    n = 4
    cap1 = "In a vertical lab the equipment comes to the operator. The PiPER asks for tray B: the extractor pulls it " \
           "off its supports, carries it down and pushes it into the opening."
    sc.step(f"1/{n}", cap1, 1.2, None, hold=0.6,
            labels=[("rear storage", (V.TRAY_W / 2, V.Y_REAR, 3300), (0.86, 0.22)),
                    ("extractor", (V.TRAY_W / 2, 0, LIFT_HOME - 40), (0.88, 0.50)),
                    ("front storage", (V.TRAY_W / 2, V.Y_FRONT, 2700), (0.84, 0.36)),
                    ("access opening", (0, -V.UNIT_D / 2, 1300), (0.20, 0.62))])
    L.fetch("B", f"1/{n}", cap1, cam=CAM_OPEN)
    cap2 = "The shutter opens and the PiPER tends the dosers at the front of the tray. Its 626 mm reach covers the " \
           "front of the tray, so what it handles goes there."
    sc.step(f"2/{n}", cap2, 1.0, L.shut(1.0), hold=0.2)
    arm = L.sc.gmat["op_arm"].copy()

    def turn(a0, a1):
        def up(u):
            sc.gmat["op_arm"] = arm @ R((0, 0, 1), a0 + (a1 - a0) * u)
        return up
    sc.step(f"2/{n}", cap2, 1.4, turn(0, -25), hold=0.4)
    sc.step(f"2/{n}", cap2, 1.6, turn(-25, 20), hold=0.4)
    sc.step(f"2/{n}", cap2, 1.0, turn(20, 0), hold=0.3)
    sc.step(f"2/{n}", cap2, 1.0, L.shut(0.0), hold=0.2)
    cap3 = "Tray B goes back to its slot and power, and the extractor brings tray C (the printers) instead. Trays " \
           "are unpowered only while they move."
    L.store("B", f"3/{n}", cap3, cam=CAM_WIDE)
    L.fetch("C", f"3/{n}", cap3)
    sc.step(f"3/{n}", cap3, 1.0, L.shut(1.0), hold=1.0)
    cap4 = "Tray C waits at the opening, powered, until the PiPER is done; then it goes back up and the next tray " \
           "comes down. Experiments run in storage in between."
    sc.step(f"4/{n}", cap4, 1.0, L.shut(0.0), hold=0.3)
    L.store("C", f"4/{n}", cap4)
    sc.step(f"4/{n}", cap4, 0.8, L.lift_to(LIFT_HOME), hold=1.5, still=True)
    return sc.save()


def disassembly(data):
    sc, L = new_scene("vlm_disassembly", data)
    L.apply_state()
    n = 8
    sc.step(f"1/{n}", "Taking it down is the assembly in reverse. The operator's stand rolls away first.", 1.8,
            slide_in(L, ["op", "op_arm"], (0, -1500, 0), out=True), hold=0.6)
    # unloading: equipment out through the opening, tray by tray
    for i, k in enumerate(("C", "B", "A")):
        step = f"{2 + i}/{n}"
        cap = f"Unloading tray {k} ({ROLE[k]}): it comes to the opening and the equipment goes out through it."
        L.fetch(k, step, cap, fast=0.7, cam=CAM_OPEN if i == 0 else None)
        sc.step(step, cap, 0.8, L.shut(1.0), hold=0.1)
        sc.step(step, cap, 2.0, equipment_in(L, k, out=True), hold=0.3)
        sc.step(step, cap, 0.8, L.shut(0.0), hold=0.1)
        L.store(k, step, cap, fast=0.7)
    L.show_gauges = False
    L.apply_state()
    sc.step(f"5/{n}", "The cladding, the opening's frame and counter, the console and the shutter come off.",
            2.4, both(slide_in(L, ["skin_L"], (-900, 0, 0), out=True), slide_in(L, ["skin_R"], (900, 0, 0), out=True),
                      slide_in(L, ["skin_back"], (0, 900, 0), out=True), slide_in(L, ["skin_top"], (0, 0, 900), out=True),
                      slide_in(L, ["skin_front", "bay", "console", "shutter"], (0, -900, 0), out=True)),
            hold=0.8, cam_to=CAM_WIDE)
    sc.step(f"6/{n}", "The trays slide out of their slots.", 2.0,
            slide_in(L, ["tray_A", "tray_B", "tray_C"], (3200, 0, 0), out=True), hold=0.6)
    sc.step(f"7/{n}", "The extractor platform, its drive and its guide rails come out.", 2.4,
            both(slide_in(L, ["lift_rails"], (0, 0, 2500), out=True), slide_in(L, ["drive"], (0, 0, 1400), out=True),
                 slide_in(L, ["lift", "belts"], (0, 0, 2400), out=True)), hold=0.6)
    sc.step(f"8/{n}", "The storage columns, the posts and roof rails, and last the base frame.", 2.0,
            slide_in(L, ["col_front", "col_rear"], (2600, 0, 0), out=True), hold=0.3)
    sc.step(f"8/{n}", "The storage columns, the posts and roof rails, and last the base frame.", 2.4,
            both(slide_in(L, ["posts"], (0, 0, 1800), out=True), slide_in(L, ["base"], (0, 0, 900), out=True)),
            hold=1.5)
    return sc.save()


CHAPTERS = {"assembly": assembly, "operation": operation, "disassembly": disassembly}

if __name__ == "__main__":
    data = lab.meshes()
    for name in sys.argv[1:] or list(CHAPTERS):
        print(CHAPTERS[name](data), flush=True)
