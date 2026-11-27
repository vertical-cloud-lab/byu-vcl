"""The floor-space segment in 3-D: PR 318's lab (setup_lab.build, the scene the campaign video's replay drives), its
instruments, floor machines, Shuttles and MiR250 + UR12e units moved through floorspace_story's three layouts.

    cd vertical-lab
    VIZ3D_SIZE=1920x1080 xvfb-run -a python -m twin.video.floorspace3d test 5 40 58 68 78 84   # stills -> /tmp/fs3d/
    VIZ3D_SIZE=1920x1080 xvfb-run -a python -m twin.video.floorspace3d render I0 I1 OUT        # frames I0..I1-1
    python -m twin.video.floorspace3d all            # every frame on TWIN_VIDEO_WORKERS (3) processes, then joined

Nothing in the scene is rebuilt: each tray instrument's own group is re-hung from its tray onto a carrier of its own,
so it can stand on a bench and fly to its tray; each floor machine's groups onto a carrier that puts it where a layout
has it; both Shuttles' groups (with their trays) onto a carrier that lowers them in. What is added is the conventional
lab's fabric (walls cut at 1.2 m, benches, storage shelving, floors), the people (people.Person: MakeHuman's CC0 body,
skinned), two more units, and the automation's docking targets, fixed arms and sample racks.

Renders are made at RENDER_FPS (15) and held for two frames of the 30 fps cut, as the replay's (lab3d.py).
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[2]            # vertical-lab/
sys.path.insert(0, str(HERE))
OUTD = HERE / "out" / "floorspace"
FRAMES = Path(os.environ.get("FS3D_DIR", "/tmp/fs3d"))
RENDER_FPS = 15

VLM1_GROUPS = ("base", "bay", "belts", "col_front", "col_rear", "console", "drive", "lift", "lift_rails", "posts",
               "shutter", "skin_L", "skin_R", "skin_back", "skin_front", "skin_top", "floor")
HIDE = ("racking", "tape", "docks", "util", "wfloor", "charger0_tape", "charger1_tape", "charger2_tape")
GROUND_C = (0.90, 0.90, 0.89)
CONV_C = (0.79, 0.81, 0.84)
COR_C = (0.72, 0.75, 0.80)
VERT_C = (0.82, 0.86, 0.80)
WALL_C = (0.96, 0.96, 0.95)
CAP_C = (0.30, 0.31, 0.33)
TOP_C = (0.20, 0.21, 0.23)                             # epoxy bench tops
CAB_C = (0.86, 0.87, 0.89)
SHELF_C = (0.66, 0.68, 0.71)
OUTLINE_C = (0.22, 0.24, 0.27)
VOUT_C = (0.10, 0.45, 0.25)
TAPE_Y = (0.96, 0.80, 0.10)


def _box(x0, y0, z0, x1, y1, z1):
    import pyvista as pv
    return pv.Box(bounds=(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))).triangulate()


def _merge(ms):
    ms = [m for m in ms if m is not None and m.n_points]
    if not ms:
        return None
    out = ms[0]
    return out.merge(ms[1:]) if len(ms) > 1 else out


def _outline(env, w=140.0, z=(2.0, 6.0)):
    x0, y0, x1, y1 = env
    return _merge([_box(x0, y0, z[0], x1, y0 + w, z[1]), _box(x0, y1 - w, z[0], x1, y1, z[1]),
                   _box(x0, y0, z[0], x0 + w, y1, z[1]), _box(x1 - w, y0, z[0], x1, y1, z[1])])


class FloorLab:
    """The scene and everything that moves in it, put in a story's state by apply(t)."""

    def __init__(self, story=None):
        from . import floorspace_story as FSS
        os.environ.setdefault("VIZ3D_PEEL", "off")
        self.S = story or FSS.Story()
        t0 = time.time()
        self._build()
        self._hide()
        self._rehang()
        self._fabric()
        self._automation()
        self._agents()
        self.sc.pl.renderer.SetUseDepthPeeling(False)
        self.build_s = time.time() - t0
        self._last_alpha: dict = {}

    # ------------------------------------------------------------------------------------------------ the lab
    def _build(self):
        import animate as A
        import lab
        import setup_lab as SL
        import vlm as V
        import warehouse as W
        self.A, self.SL, self.V, self.W = A, SL, V, W
        data = lab.meshes()
        idata = SL.load_all()
        il = SL.item_label

        def safe_label(inst, il=il):
            try:
                return il(inst)
            except Exception:                           # noqa: BLE001
                return getattr(inst, "model", "")
        SL.item_label = safe_label
        sc, L, F, items, rigs, units, util, _, vp = SL.build(data, idata, mp4=False, name="floorspace", title="")
        L.show_gauges = False
        L.skin(1.0)(1.0)                                # see-through Shuttles, every tray showing, as in the stills
        self.home = {k: [*V.SLOTS[A.HOME[k]]] for k in L.tray}
        for k in L.tray:
            L.tray[k] = list(self.home[k])
            L.where[k] = A.HOME[k]
        for sh in (1, 2):
            L.use(sh)
            L.lift_z = A.LIFT_HOME
            L.shutter = 0.0
        L.use(1)
        L.apply_state()
        self.q_park = np.radians(A.PARK_DEG)
        self.q_ready = np.radians((-90.0, -100.0, 110.0, -100.0, -90.0, 0.0))
        for i, uu in enumerate(units):
            uu.set(W.charger_pose(i))
            uu.robot.set(self.q_park)
        sc.title, sc.caption, sc.label, sc.labels = "", "", "", []
        sc.gauges = []
        self.sc, self.L, self.F, self.items, self.units = sc, L, F, items, units
        self.unit3 = getattr(F, "unit3", None)
        sc.apply()

    def _root(self, g):
        sc = self.sc
        while sc.parent.get(g):
            g = sc.parent[g]
        return g

    def _names_under(self, roots: set) -> list:
        sc = self.sc
        return [n for n, g in sc.group_of.items() if self._root(g) in roots]

    def _hide(self):
        sc = self.sc
        for n, g in sc.group_of.items():
            if g in HIDE or n == "footprints":
                sc.alpha[n] = 0.0

    # ------------------------------------------------------------------------------------------------ carriers
    def _rehang(self):
        from scene import T
        sc, S, L = self.sc, self.S, self.L
        self.base_alpha = dict(sc.alpha)
        # the Shuttles, with their trays (and what rides on them: UPS, cameras, plates, lamps)
        tops = {self._root(g) for g in set(sc.group_of.values())}
        v1 = {g for g in tops if g in VLM1_GROUPS} | {f"tray_{k}" for k in L.tray if L.unit.get(k, 1) == 1}
        v2 = {g for g in tops if g.startswith("u2_")} | {f"tray_{k}" for k in L.tray if L.unit.get(k, 1) == 2}
        for car, gs in (("fs_vlm1", v1), ("fs_vlm2", v2)):
            for g in gs:
                sc.parent[g] = car
            sc.gmat[car] = np.eye(4)
        # every tray instrument (not its UPS, cameras or the tray's own parts) onto a carrier
        self.item = {}
        inv = S.inv
        by_tray = {}
        for key, it in inv.items():
            if it.tray is not None:
                by_tray.setdefault(it.tray, []).append(key)
        for t, lst in self.items.items():
            ours = sorted(by_tray.get(t, []), key=lambda k: inv[k].idx)
            theirs = [e for e in lst if e[0] not in ("ups", "cam")]
            if len(ours) != len(theirs):
                print(f"floorspace3d: tray {t}: {len(theirs)} items in the scene, {len(ours)} in the plan", flush=True)
            for key, (ikey, g, names, label) in zip(ours, theirs):
                groups = {sc.group_of[n] for n in names if n in sc.group_of}
                direct = {gg for gg in groups if sc.parent.get(gg) == f"tray_{t}"}
                if not direct:
                    direct = {self._root(gg) for gg in groups}
                world_t = sc.world(f"tray_{t}")
                car = f"fs_item_{key}"
                for gg in direct:
                    sc.parent[gg] = car
                sc.gmat[car] = world_t.copy()
                # its anchor in the tray's frame, from what is drawn (alpha > 0)
                sc.apply()
                bs = [sc.actors[n].GetBounds() for n in names if n in sc.actors and sc.alpha.get(n, 0) > 0.02]
                if bs:
                    b = np.array(bs)
                    lo, hi = b[:, [0, 2, 4]].min(0), b[:, [1, 3, 5]].max(0)
                    tw = world_t[:3, 3]
                    loc = ((lo[0] + hi[0]) / 2 - tw[0], (lo[1] + hi[1]) / 2 - tw[1], lo[2] - tw[2])
                else:
                    loc = S.item_local(key)
                plan = S.item_local(key)
                if abs(loc[0] - plan[0]) > 60 or abs(loc[1] - plan[1]) > 60:
                    print(f"floorspace3d: {key} ({label}): drawn anchor {np.round(loc)} vs plan {np.round(plan)}",
                          flush=True)
                self.item[key] = dict(car=car, tray=t, local=loc, label=label, names=names)
        # every floor machine onto a carrier: its plan centre and facing in the 3-D lab are the inventory's
        self.mach = {}
        extra = {"repowder": {"stream", "pstream"}}
        for key, it in inv.items():
            if it.tray is not None:
                continue
            names = self.F.groups.get(key, [])
            roots = {self._root(sc.group_of[n]) for n in names if n in sc.group_of} | extra.get(key, set())
            roots &= tops | extra.get(key, set())
            car = f"fs_m_{key}"
            for r in roots:
                sc.parent[r] = car
            sc.gmat[car] = np.eye(4)
            x0, y0, x1, y1 = it.rect0
            self.mach[key] = dict(car=car, c0=((x0 + x1) / 2, (y0 + y1) / 2), th0=S_ang(it.facing0))
        self.vlm_names = self._names_under({"fs_vlm1", "fs_vlm2"})
        sc.apply()

    # ------------------------------------------------------------------------------------------------ fabric
    def _fabric(self):
        import pyvista as pv
        from . import floorspace as FS
        from . import floorspace_story as FSS
        sc, S = self.sc, self.S
        conv, vert = S.conv, S.vert
        sc.add("fs/ground", pv.Plane(center=(2000, -7000, -6), direction=(0, 0, 1), i_size=160000, j_size=130000),
               GROUND_C, "fs_ground", ambient=0.9, diffuse=0.15, specular=0.0, smooth_shading=False)
        x0, y0, x1, y1 = conv.envelope
        sc.add("fs/conv floor", _box(x0, y0, -4, x1, y1, 0), CONV_C, "fs_conv", ambient=0.85, diffuse=0.2,
               specular=0.0)
        c = next(a for a in conv.aisles if a["kind"] == "corridor")["rect"]
        sc.add("fs/corridor", _box(c[0], c[1], 0, c[2], c[3], 0.8), COR_C, "fs_walls", ambient=0.85, diffuse=0.2,
               specular=0.0)
        sc.add("fs/conv outline", _outline(conv.envelope), OUTLINE_C, "fs_conv", specular=0.0, ambient=0.6)
        sc.gmat["fs_conv"] = np.eye(4)
        # walls: a white body and a dark cap where they are cut
        H = FSS.WALL_H
        walls = [_box(w[0], w[1], 0, w[2], w[3], H - 25) for w in conv.walls]
        caps = [_box(w[0], w[1], H - 25, w[2], w[3], H) for w in conv.walls]
        sc.add("fs/walls", _merge(walls), WALL_C, "fs_walls", specular=0.05, ambient=0.35)
        sc.add("fs/wall caps", _merge(caps), CAP_C, "fs_walls", specular=0.0)
        sc.gmat["fs_walls"] = np.eye(4)
        # benches: epoxy top on a base cabinet; shelving: posts and boards, one board under each rack
        tops, cabs, kicks, posts, boards = [], [], [], [], []
        for b in conv.benches:
            bx0, by0, bx1, by1 = b["rect"]
            h = b["h"]
            if b["kind"] == "bench":
                tops.append(_box(bx0, by0, h - 32, bx1, by1, h))
                cabs.append(_box(bx0 + 20, by0 + 25, 100, bx1 - 20, by1 - 25, h - 32))
                kicks.append(_box(bx0 + 70, by0 + 75, 0, bx1 - 70, by1 - 75, 100))
            else:
                for px in (bx0 + 20, bx1 - 50):
                    for py in (by0 + 20, by1 - 50):
                        posts.append(_box(px, py, 0, px + 30, py + 30, h))
                keys = b["keys"]
                for k in keys:
                    z = conv.places[k].z
                    boards.append(_box(bx0, by0, z - 25, bx1, by1, z))
                boards.append(_box(bx0, by0, h - 25, bx1, by1, h))
        sc.add("fs/bench tops", _merge(tops), TOP_C, "fs_benches", specular=0.25)
        sc.add("fs/bench cabinets", _merge(cabs), CAB_C, "fs_benches", specular=0.05)
        sc.add("fs/bench kicks", _merge(kicks), (0.30, 0.31, 0.33), "fs_benches", specular=0.0)
        sc.add("fs/shelf posts", _merge(posts), SHELF_C, "fs_shelves", specular=0.3)
        sc.add("fs/shelf boards", _merge(boards), (0.74, 0.76, 0.79), "fs_shelves", specular=0.15)
        sc.gmat["fs_benches"] = np.eye(4)
        sc.gmat["fs_shelves"] = np.eye(4)
        # the vertical lab's floor, its outline and the MiR aisle's tape: grown out from between the Shuttles
        vx0, vy0, vx1, vy1 = vert.envelope
        sc.add("fs/vert floor", _box(vx0, vy0, 0, vx1, vy1, 3.0), VERT_C, "fs_vfloor", ambient=0.85, diffuse=0.2,
               specular=0.0)
        sc.add("fs/vert outline", _outline(vert.envelope, z=(3.0, 8.0)), VOUT_C, "fs_vfloor", specular=0.0,
               ambient=0.6)
        a = next(a for a in vert.aisles if a["kind"] == "mir")["rect"]
        tape = [_box(a[0], a[1] - 37.5, 3, a[2], a[1] + 37.5, 4.5), _box(a[0], a[3] - 37.5, 3, a[2], a[3] + 37.5, 4.5)]
        yc = (a[1] + a[3]) / 2
        dashes = [_box(x, yc - 25, 3, x + 600, yc + 25, 4.5) for x in np.arange(a[0] + 300, a[2] - 600, 1200)]
        sc.add("fs/vert aisle tape", _merge(tape), TAPE_Y, "fs_vfloor", specular=0.0, ambient=0.5)
        sc.add("fs/vert aisle dashes", _merge(dashes), (0.97, 0.97, 0.97), "fs_vfloor", specular=0.0, ambient=0.5)
        self.vgrow_c = (1815.0, 0.0)
        sc.gmat["fs_vfloor"] = np.eye(4)
        sc.add("fs/old outline", _outline(conv.envelope, w=110.0, z=(0.5, 2.5)), (0.55, 0.36, 0.30), "fs_old",
               specular=0.0, ambient=0.6)
        sc.gmat["fs_old"] = np.eye(4)

    # ------------------------------------------------------------------------------------------------ automation
    def _dock_meshes(self, ident, rel_post):
        """A MiR250 dock's tape (the MiR's 800 x 580 plus 70 mm round), and its target: a post, its foot and an
        AprilTag-style cube (warehouse.tag), at rel_post from the dock's centre."""
        import pyvista as pv
        W = self.W
        tape = W.tape_rect(0.0, 0.0, 940.0, 720.0, t=50.0)
        px, py = rel_post
        post = pv.Cylinder(center=(px, py, W.TARGET_Z / 2), direction=(0, 0, 1), radius=25, height=W.TARGET_Z,
                           resolution=16).triangulate()
        foot = _box(px - 150, py - 150, 0, px + 150, py + 150, 12)
        b, w = W.tag(ident=ident)
        return dict(tape=(tape, (0.97, 0.97, 0.97)), post=(_merge([post, foot]), (0.45, 0.46, 0.48)),
                    black=(b.translate((px, py, W.TARGET_Z), inplace=False), (0.05, 0.05, 0.06)),
                    white=(w.translate((px, py, W.TARGET_Z), inplace=False), (0.98, 0.98, 0.98)))

    def _automation(self):
        import robot as RB
        from scene import T, R
        sc, S, W = self.sc, self.S, self.W
        self.fdocks = []
        for i, d in enumerate(S.flat.docks):
            p = S.conv.places[d["station"]]
            sgn = 1.0 if p.facing == "N" else -1.0
            g = f"fs_fdock{i}"
            for nm, (mesh, col) in self._dock_meshes(i, (520.0, -sgn * 590.0)).items():
                sc.add(f"{g}/{nm}", mesh, col, g, specular=0.0 if nm == "tape" else 0.2,
                       ambient=0.5 if nm in ("tape", "white") else 0.22)
            sc.gmat[g] = T((d["x"], d["y"], 0.0))
            self.fdocks.append(dict(g=g, x=d["x"], y=d["y"], names=sc.members(g)))
        # fixed arms on pedestals beside the benches that have room, each with a sample rack
        self.arms = []
        for i, a in enumerate(S.flat.arms):
            g = f"fs_arm{i}"
            h = 880.0
            sc.add(f"{g}/pedestal", _box(-260, -230, 0, 260, 230, h), (0.55, 0.57, 0.60), g, specular=0.2)
            sc.add(f"{g}/plate", _box(-260, -230, h, 260, 230, h + 20), (0.35, 0.36, 0.38), g, specular=0.3)
            rx = -150.0 * a["side"]            # the arm on the bench side, the rack away from it
            sc.add(f"{g}/rack", _box(-rx - 90, -70, h + 20, -rx + 90, 70, h + 110), (0.30, 0.55, 0.85), g,
                   specular=0.3)
            sc.add(f"{g}/rack caps", _merge([_box(-rx - 75 + j * 37, -55 + k * 37, h + 110, -rx - 50 + j * 37,
                                                  -30 + k * 37, h + 135) for j in range(5) for k in range(4)]),
                   (0.95, 0.45, 0.20), g, specular=0.2)
            sc.gmat[g] = T((a["x"], a["y"], 0.0))
            rb = RB.Robot(sc, self.A.ROBOT, g, T((rx, 0.0, h + 20)), q0=self.A.PARK_DEG, prefix=f"fsarm{i}")
            q0 = math.degrees(math.atan2(a["toward"][1], a["toward"][0])) - 180.0
            self.arms.append(dict(g=g, robot=rb, q0=q0, x=a["x"], y=a["y"], names=sc.members(g) + [
                n for n, gg in sc.group_of.items() if gg.startswith(f"fsarm{i}_")]))
        # the flat lab's chargers: two at the corridor's east end, facing west
        self.fchg = []
        for i, (x, y, hd) in enumerate(S.flat.chargers):
            g = f"fs_fchg{i}"
            for nm, (mesh, col) in W.charger_mesh().items():
                sc.add(f"{g}/{nm}", mesh, col, g, **(dict(ambient=0.8) if "led" in nm else {}))
            sc.gmat[g] = T((x, y, 0.0)) @ R((0, 0, 1), hd)
            self.fchg.append(dict(g=g, M=sc.gmat[g].copy(), names=sc.members(g)))
        # the vertical lab's docks and its three chargers (the scene's own, moved)
        self.vdocks = []
        for i, d in enumerate(S.vert.docks):
            if d["station"] in ("vlm1", "vlm2"):
                continue
            sgn = 1.0 if d["y"] < S.aisle_y else -1.0           # south row: the station is south of the dock
            g = f"fs_vdock{i}"
            for nm, (mesh, col) in self._dock_meshes(40 + i, (520.0, -sgn * 420.0)).items():
                sc.add(f"{g}/{nm}", mesh, col, g, specular=0.0 if nm == "tape" else 0.2,
                       ambient=0.5 if nm in ("tape", "white") else 0.22)
            sc.gmat[g] = T((d["x"], d["y"], 0.0))
            self.vdocks.append(dict(g=g, x=d["x"], y=d["y"], names=sc.members(g)))
        self.vchg = []
        for i, (x, y, hd) in enumerate(S.vert.chargers):
            g = f"charger{i}"
            if g not in sc.gmat:
                continue
            sc.gmat[g] = T((x, y + 243.5, 0.0))
            self.vchg.append(dict(g=g, M=sc.gmat[g].copy(), names=sc.members(g), x=x, y=y))

    # ------------------------------------------------------------------------------------------------ people, units
    def _agents(self):
        import people as PE
        from scene import T
        sc, S = self.sc, self.S
        looks = [dict(), dict(trousers=(0.33, 0.27, 0.22), hair=(0.10, 0.08, 0.07)),
                 dict(skin=(0.55, 0.39, 0.29), hair=(0.06, 0.05, 0.05)), dict(trousers=(0.40, 0.42, 0.45)),
                 dict(skin=(0.93, 0.78, 0.68), hair=(0.62, 0.45, 0.25)), dict(skin=(0.68, 0.50, 0.38)),
                 dict(trousers=(0.25, 0.30, 0.22))]
        self.people = {}
        for i, nm in enumerate(sorted(S.people)):
            p = PE.Person(sc, f"fs_{nm}", **looks[i % len(looks)])
            box = None
            if nm != "p7":                                   # a tote of samples in the right hand
                g = f"fs_{nm}_tote"
                sc.add(f"{g}/tote", _box(-150, -95, -150, 150, 95, 0), (0.95, 0.55, 0.15), g, specular=0.2)
                sc.add(f"{g}/samples", _merge([_box(-120 + j * 60, -60, 0, -80 + j * 60, -20, 45) for j in range(5)] +
                                              [_box(-120 + j * 60, 20, 0, -80 + j * 60, 60, 45) for j in range(5)]),
                       (0.70, 0.72, 0.76), g, specular=0.4)
                p.set(x=0.0, y=0.0, hd=0.0, phase=0.0, amp=0.0, hands={"l": None, "r": None})
                hp = p.hand_point("r")
                sc.gmat[g] = T((hp[0], hp[1], hp[2] - 20.0))
                p.hold("r", g)
                box = g
            self.people[nm] = dict(p=p, box=box, names=p.names() + (sc.members(box) if box else []))
        import setup_lab as SL
        self.robots = {"r1": self.units[0], "r2": self.units[1]}
        for nm in ("r3", "r4"):
            self.robots[nm] = SL.Unit(sc, f"fs_{nm}", (0.0, 0.0, 0.0))
            self.robots[nm].robot.set(self.q_park)
        self.robot_names = {nm: u.all_names() for nm, u in self.robots.items()}
        if self.unit3 is not None:
            self.unit3_names = self.unit3.all_names() + [n for n, g in sc.group_of.items() if g.startswith("unit3")]
        self.base_alpha = dict(sc.alpha)

    # ------------------------------------------------------------------------------------------------ the state
    def _alpha(self, key, names, a):
        """Fade a set of actors to a (times each one's own alpha), only when it changed."""
        a = round(float(a), 3)
        if self._last_alpha.get(key) == a:
            return
        self._last_alpha[key] = a
        sc, base = self.sc, self.base_alpha
        for n in names:
            sc.alpha[n] = base.get(n, 1.0) * a

    def arm_q(self, st: dict, t: float, phase: float = 0.0) -> np.ndarray:
        """A unit's arm: folded while driving; out to its ready pose and working while docked."""
        qp, qr = self.q_park, self.q_ready
        if st.get("moving", 1.0) > 0 or st.get("station") is None:
            return qp
        a = min(1.0, st.get("t_in_dwell", 0.0) / 0.9, st.get("t_left", 0.0) / 0.9)
        a = max(0.0, a)
        w = 0.9 * t + phase
        work = qr + np.radians([18 * math.sin(w), 9 * math.sin(1.3 * w + 1), 12 * math.sin(0.8 * w + 2),
                                10 * math.sin(1.1 * w), 0.0, 40 * math.sin(0.7 * w)])
        f = a * a * (3 - 2 * a)
        return qp + (work - qp) * f

    def apply(self, t: float):
        from scene import T, R, S as Sc
        from . import floorspace_story as FSS
        sc, S, L, A = self.sc, self.S, self.L, self.A
        # the Shuttles and their trays
        dz, va = S.vlm_dz(t)
        sc.gmat["fs_vlm1"] = T((0.0, 0.0, dz))
        sc.gmat["fs_vlm2"] = T((0.0, 0.0, dz))
        self._alpha("vlm", self.vlm_names, va)
        ts = S.tray_state(t)
        for k in L.tray:
            L.tray[k] = list(self.home[k])
            L.where[k] = A.HOME[k]
        for s in (1, 2):
            st = ts[s]
            L.use(s)
            L.lift_z = float(st["lift"])
            L.shutter = float(st["shutter"])
            for k, (y, z) in st["trays"].items():
                L.tray[k] = [float(y), float(z)]
                L.where[k] = "open" if st["out"] == k else None
        L.use(1)
        L.apply_state()
        # the instruments
        for key, d in self.item.items():
            x, y, z, th, where = S.item_pose(key, t, d["local"])
            if where == "tray":
                sc.gmat[d["car"]] = sc.world(f"tray_{d['tray']}")
            else:
                cx, cy, z0 = d["local"]
                sc.gmat[d["car"]] = T((x, y, z)) @ R((0, 0, 1), th) @ T((-cx, -cy, -z0))
        # the floor machines
        for key, d in self.mach.items():
            x, y, th = S.machine_pose(key, t)
            cx, cy = d["c0"]
            sc.gmat[d["car"]] = T((x, y, 0.0)) @ R((0, 0, 1), th - d["th0"]) @ T((-cx, -cy, 0.0))
        # the conventional lab's fabric going down, the vertical floor coming out
        k = S.sink(t)
        sc.gmat["fs_walls"] = T((0.0, 0.0, -(FSS.WALL_H + 60.0) * k))
        sc.gmat["fs_benches"] = T((0.0, 0.0, -(980.0) * k))
        sc.gmat["fs_shelves"] = T((0.0, 0.0, -(1900.0) * k))
        g = S.grow(t)
        cx, cy = self.vgrow_c
        gg = max(g, 1e-3)
        sc.gmat["fs_vfloor"] = T((cx, cy, 0.0)) @ Sc((gg, gg, 1.0)) @ T((-cx, -cy, 0.0))
        self._alpha("vfloor", sc.members("fs_vfloor"), 1.0 if g > 0.002 else 0.0)
        self._alpha("old", sc.members("fs_old"), 1.0 if g > 0.002 else 0.0)
        self._alpha("conv", sc.members("fs_conv"), 1.0)
        # the automation
        n = max(1, len(self.fdocks))
        for i, d in enumerate(self.fdocks):
            s = S.pop(t, i, n)
            sc.gmat[d["g"]] = T((d["x"], d["y"], 0.0)) @ Sc((max(s, 1e-3),) * 3)
            self._alpha(d["g"], d["names"], 1.0 if s > 0.01 else 0.0)
        for i, d in enumerate(self.arms):
            s = S.pop(t, i, max(1, len(self.arms)))
            sc.gmat[d["g"]] = T((d["x"], d["y"], 0.0)) @ Sc((max(s, 1e-3),) * 3)
            self._alpha(d["g"], d["names"], 1.0 if s > 0.01 else 0.0)
            w = 0.8 * t + i
            q = np.radians([d["q0"] + 25 * math.sin(w), -100 + 12 * math.sin(1.3 * w), 110 + 15 * math.sin(0.9 * w),
                            -100 + 12 * math.sin(1.1 * w + 1), -90.0, 50 * math.sin(0.7 * w)])
            qq = self.q_park + (q - self.q_park) * min(1.0, s)
            d["robot"].set(qq)
        for i, d in enumerate(self.fchg):
            s = S.pop(t, i, max(1, len(self.fchg))) if t < FSS.PH["vert"] + 13.0 else max(
                0.0, 1.0 - FSS.win(t, FSS.PH["vert"] + 12.4, FSS.PH["vert"] + 13.6))
            sc.gmat[d["g"]] = d["M"] @ Sc((max(s, 1e-3),) * 3)
            self._alpha(d["g"], d["names"], 1.0 if s > 0.01 else 0.0)
        nv = max(1, len(self.vdocks))
        for i, d in enumerate(self.vdocks):
            s = S.pop(t, i, nv, "vert")
            sc.gmat[d["g"]] = T((d["x"], d["y"], 0.0)) @ Sc((max(s, 1e-3),) * 3)
            self._alpha(d["g"], d["names"], 1.0 if s > 0.01 else 0.0)
        for i, d in enumerate(self.vchg):
            s = S.pop(t, i, len(self.vchg), "vert")
            sc.gmat[d["g"]] = d["M"] @ Sc((max(s, 1e-3),) * 3)
            self._alpha(d["g"], d["names"], 1.0 if s > 0.01 else 0.0)
        if self.unit3 is not None:
            s = S.pop(t, 2, 3, "vert")
            x, y = S.vert.chargers[-1][0], S.vert.chargers[-1][1] + 243.5 + 20.0 + 400.0
            self.unit3.set((x, y, -90.0))
            self._alpha("unit3", self.unit3_names, 1.0 if s > 0.5 else 0.0)
        # people
        for nm, d in self.people.items():
            st = S.people[nm].state(t)
            a = st.get("alpha", 0.0)
            self._alpha(f"p_{nm}", d["names"], a)
            if a <= 0.01:
                continue
            p = d["p"]
            hd = st["hd"] - 90.0
            phase = 2 * math.pi * st["s"] / FSS.STRIDE
            mv = st["moving"]
            tgt = st.get("target")
            hands = {"l": None, "r": None}
            look = None
            if tgt is not None and mv == 0:
                f = min(1.0, st.get("t_in_dwell", 0.0) / 0.7, st.get("t_left", 0.0) / 0.7)
                if f > 0.2:
                    hands["l"] = (tgt[0] + 90 * math.sin(1.7 * t), tgt[1], tgt[2] + 40 * math.sin(2.3 * t))
                look = tgt
            p.set(x=st["x"], y=st["y"], hd=hd, lean=4.0 if (tgt is not None and mv == 0) else 0.0, phase=phase,
                  amp=mv, hands=hands, look=look)
        # units
        for nm, u in self.robots.items():
            ag = S.robots[nm]
            if t < ag.t_in or t > ag.t_out:
                self._alpha(f"r_{nm}", self.robot_names[nm], 0.0)
                continue
            st = ag.state(t)
            self._alpha(f"r_{nm}", self.robot_names[nm], st.get("alpha", 1.0))
            u.set((st["x"], st["y"], st["hd"]))
            u.robot.set(self.arm_q(st, t, hash(nm) % 7))

    def camera(self, t: float):
        c = self.S.camera(t)
        self.sc.cam = [tuple(c["pos"]), tuple(c["foc"]), tuple(c.get("up", (0, 0, 1)))]
        self.sc.view_angle = float(c["va"])

    def render(self, t: float) -> np.ndarray:
        self.apply(t)
        self.camera(t)
        return self.sc.render_base()[:, :, :3]


def S_ang(f: str) -> float:
    from . import floorspace as FS
    return FS.FACING[f]


# ============================================================================================ jobs
def n_frames() -> int:
    from . import floorspace_story as FSS
    return int(math.ceil(FSS.T3D_END * RENDER_FPS))


def render_range(i0: int, i1: int, out: Path, lab: FloorLab | None = None):
    lab = lab or FloorLab()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    W_, H_ = (int(v) for v in lab.sc.size)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}",
                            "-framerate", str(RENDER_FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast",
                            "-crf", "12", "-pix_fmt", "yuv444p", "-threads", "1", str(out)], stdin=subprocess.PIPE)
    t0 = time.time()
    lab.sc._clip_n = 0
    for i in range(i0, i1):
        t = i / RENDER_FPS
        img = np.ascontiguousarray(lab.render(t))
        enc.stdin.write(img.tobytes())
        if (i - i0 + 1) % 60 == 0:
            print(f"{out.name}: {i - i0 + 1}/{i1 - i0} frames, {time.time() - t0:.0f} s", flush=True)
    enc.stdin.close()
    enc.wait()
    info = dict(i0=i0, i1=i1, fps=RENDER_FPS, build_s=round(lab.build_s, 1), wall_s=round(time.time() - t0, 1))
    out.with_suffix(".json").write_text(json.dumps(info) + "\n")
    print(json.dumps(info), flush=True)


def render_all(workers: int | None = None):
    """Every frame, split into contiguous ranges over `workers` processes (each builds the scene), then joined into
    FRAMES/lab3d.mp4."""
    workers = workers or int(os.environ.get("TWIN_VIDEO_WORKERS", "3"))
    n = n_frames()
    FRAMES.mkdir(parents=True, exist_ok=True)
    cuts = [round(n * i / workers) for i in range(workers + 1)]
    procs = []
    for w in range(workers):
        out = FRAMES / f"part{w}.mp4"
        log = open(FRAMES / f"part{w}.log", "w")
        cmd = ["xvfb-run", "-a", sys.executable, "-m", "twin.video.floorspace3d", "render", str(cuts[w]),
               str(cuts[w + 1]), str(out)]
        procs.append(subprocess.Popen(cmd, cwd=str(HERE), stdout=log, stderr=subprocess.STDOUT,
                                      env=dict(os.environ, VIZ3D_SIZE="1920x1080")))
    for p in procs:
        p.wait()
    lst = FRAMES / "parts.txt"
    lst.write_text("".join(f"file '{FRAMES / f'part{w}.mp4'}'\n" for w in range(workers)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    str(FRAMES / "lab3d.mp4")], check=True)
    print("joined", FRAMES / "lab3d.mp4", flush=True)


def test_main(ts):
    from PIL import Image
    FRAMES.mkdir(parents=True, exist_ok=True)
    lab = FloorLab()
    print(f"built in {lab.build_s:.0f} s", flush=True)
    for t in ts:
        t1 = time.time()
        img = lab.render(t)
        print(f"t={t}: {time.time() - t1:.2f} s", flush=True)
        Image.fromarray(img).save(FRAMES / f"test_{t:05.1f}.png")


if __name__ == "__main__":
    cmd = sys.argv[1] if sys.argv[1:] else "test"
    if cmd == "test":
        test_main([float(v) for v in sys.argv[2:]] or [5.0, 40.0, 58.0, 68.0, 78.0])
    elif cmd == "render":
        render_range(int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4]))
    elif cmd == "all":
        render_all()
    else:
        raise SystemExit(__doc__)
