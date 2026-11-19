"""Cleaning the crucible and touching up its boron-nitride coat, by robot (PR #353, #303). Clip ``atom_bn``.

MiR 1 brings the used crucible (holder and nozzle off, the skull inside: atom_crucible.py takes it out of the furnace
and puts it back) to a cleaning bench beside a fume hood. The arm and a two-axis positioner tip the skull out, brush,
scrape back only what is cracked or lifted, tip out the flakes and vacuum the dust; then, in the running hood, the
crucible stands on a turntable in an open-topped box, a plug masks the nozzle seat, and the arm sprays short bursts
of BN from 15-20 cm, turning the crucible between them, two light passes 5 min apart. The crucible dries overnight
upside down on a rack in the hood and is checked in the morning under a side light with the wrist camera.

The procedure is the lab's own (DAL PR 220, the bronze plan's "Coating and recoating the crucible"; the atomizer SOP
checklist, DAL 253; the SOP's "Cleaning and maintenance", DAL 178; the Nilfisk vacuum SOP, byu-vcl PR 80). What is
ours or assumed is said in notes/atom_bn.md, with the stations and tools in atom_bn_station.py.

    xvfb-run -a python3 atom_bn.py                     # out/atom_bn.gif, out/mp4/atom_bn.mp4, out/atom_bn.json
    PREVIEW=1 xvfb-run -a python3 atom_bn.py           # /tmp/preview_atom_bn.png
    ARM_AUDIT=1 xvfb-run -a python3 atom_bn.py         # out/collisions/atom_bn.json
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import atom_base as AB                 # noqa: E402
import atom_bn_station as S            # noqa: E402
import collide                         # noqa: E402
import ur_arm                          # noqa: E402
from scene import R, T                 # noqa: E402

G_CRU, G_SKULL, G_TRUN, G_TT, G_PLUG = "bn_cru", "bn_skull", "bn_trun", "bn_tt", "bn_plug"
G_BRUSH, G_SCRAPER, G_VAC, G_CAN, G_MIST = "bn_brush", "bn_scraper", "bn_vac", "bn_can", "bn_mist"
CRADLE_LOCAL = (280.0, -100.0)          # the crucible's cradle on MiR 1's cabinet top (ours), MiR-local
CRADLE_H = 40.0
BENCH_SPOT = (2150.0, -850.0, 0.0)      # MiR 1's spots (model frame x, y, yaw): the bench, the hood
HOOD_SPOT = (2850.0, -1130.0, 0.0)
C_CRU = ur_arm.close_for(2 * S.CR_RO + 0.4)
C_TOOL = ur_arm.close_for(S.GRIP_W + 0.4)
DOWN, LEVEL = (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)
SPEED = 0.74                            # every move's time, scaled (the bursts and the free fall are not)


def inv(M):
    Mi = np.eye(4)
    Mi[:3, :3] = M[:3, :3].T
    Mi[:3, 3] = -M[:3, :3].T @ M[:3, 3]
    return Mi


class Clip:
    def __init__(self):
        sc, ma, _ = AB.build("atom_bn", "Vertical cloud lab: cleaning the crucible and recoating it with boron nitride",
                             mirs=1)
        self.sc, self.ma, self.rb = sc, ma, ma.rb
        self.fluids = []
        sc.fluids = self.fluids
        self.coat = {}                    # zone -> coat fraction (0 .. 1)
        self.base_c = {}                  # zone -> its colour after cleaning
        self.wet = 0.0                    # 1: the new coat is wet; 0: dry
        self.vals = dict(flip=0.0, spin=0.0, jaws=1.0, lift=1.0, tt=0.0, knock=0.0, light=0.0)
        self._build()

    # ------------------------------------------------------------------------------------------ the scene
    def add(self, name, mesh, col, grp, parent="rp", **kw):
        self.sc.add(name, mesh, col, grp, **kw)
        if parent is not None:
            self.sc.parent.setdefault(grp, parent)

    def _build(self):
        sc = self.sc
        # the crucible leaves the furnace in atom_crucible.py: the furnace's own crucible, holder and nozzle are hidden
        cru = S.crucible_mesh(sc)
        for grp in ("crucible", "holder", "nozzle"):
            sc.show(sc.members(AB.g(grp)), 0.0)
        self.add("bn crucible", cru, S.GRAPHITE, G_CRU, parent=None, specular=0.15)
        zones = S.coat_zones()
        for z, mesh in zones.items():
            nm = f"bn coat {z[0]} {z[1]}"
            self.add(nm, mesh, S.OLD_COAT, G_CRU, parent=None, specular=0.05, smooth_shading=False)
            self.coat[z] = 0.0
            self.base_c[z] = S.SEAT_C if z[0] == "seat" else (S.DAMAGED if z in S.DAMAGE else S.OLD_COAT)
        self.add("bn skull", S.skull_mesh(), S.SKULL_C, G_SKULL, parent=None, specular=0.5)
        sc.parent[G_SKULL] = G_CRU
        self.paint()
        # MiR 1's cradle for the crucible (ours): a lined ring on the cabinet top
        top = AB.P.MIR["H"] + AB.P.CAB_H
        cx, cy = CRADLE_LOCAL
        ring = S._ring(cx, cy, top, CRADLE_H, S.CR_RO + 8.0, S.CR_RO + 1.0, 48).merge(
            S._cyl((cx, cy, top + 1.5), (0, 0, 1), S.CR_RO + 8.0, 3.0, 48))
        sc.add("amr/bn crucible cradle", ring, (0.30, 0.32, 0.36), self.ma.g)
        sc.parent[G_CRU] = self.ma.g
        sc.gmat[G_CRU] = T((cx, cy, top + 3.0))
        # the bench, the positioner, the tray, the holsters, the light
        for d in (S.bench_meshes(), S.positioner_static(), S.tray_meshes(), S.light_meshes(), S.holster_meshes()):
            for nm, (mesh, col) in d.items():
                self.add("bn " + nm, mesh, col, "bn_station", specular=0.3)
        self.add("bn light beam", S.light_beam(), (1.0, 0.95, 0.75), "bn_station", opacity=0.22, ambient=0.9,
                 diffuse=0.2, specular=0.0)
        self.fluids.append("bn light beam")
        sc.alpha["bn light beam"] = 0.0
        for nm, (mesh, col) in S.trunnion_meshes().items():
            self.add("bn " + nm, mesh, col, G_TRUN, specular=0.4)
        for k in range(3):
            self.add(f"bn jaw {k}", S.jaw_mesh(k), (0.95, 0.95, 0.92), f"bn_jaw{k}", parent=G_TRUN, specular=0.2)
        # the vacuum: atom_nilfisk.py's model if it is there, else a stand-in (and say so)
        self.nilfisk = "stand-in"
        self.inlet = S.NILFISK_INLET
        try:
            import atom_nilfisk as NF                        # another agent's model of the lab's 118EXP (#353)
            nx, ny = S.NILFISK_AT
            for nm, (mesh, col) in NF.vacuum_meshes().items():
                self.add("bn nf " + nm, mesh.translate((nx, ny, 0.0), inplace=False), col, "bn_station", specular=0.3)
            self.inlet = np.asarray(NF.vacuum_local("inlet"), float) + np.array([nx, ny, 0.0])
            self.nilfisk = "atom_nilfisk.vacuum_meshes"
        except Exception as e:                                # noqa: BLE001
            print(f"atom_bn: Nilfisk stand-in ({type(e).__name__}: {e})", flush=True)
            for nm, (mesh, col) in S.nilfisk_standin().items():
                self.add("bn " + nm, mesh, col, "bn_station", specular=0.3)
        # the hood and what is in it
        self.hood = S.add_hood(sc)
        for d in (S.box_meshes(), S.rack_meshes()):
            for nm, (mesh, col) in d.items():
                op = 0.28 if nm == "spray box" else 1.0
                self.add("bn " + nm, mesh, col, "bn_hoodfix", opacity=op, specular=0.3)
        for nm, (mesh, col) in S.lift_meshes().items():
            self.add("bn " + nm, mesh, col, G_TT, specular=0.4)
        for nm, (mesh, col) in S.plug_meshes().items():
            self.add("bn " + nm, mesh, col, G_PLUG, specular=0.3)
        # the tools
        for grp, d in ((G_BRUSH, S.brush_meshes()), (G_SCRAPER, S.scraper_meshes()), (G_VAC, S.vac_meshes()),
                       (G_CAN, S.can_tool_meshes())):
            for nm, (mesh, col) in d.items():
                self.add("bn " + nm, mesh, col, grp, specular=0.4)
        self.add("bn mist", S.mist_mesh(), (0.97, 0.97, 0.95), G_MIST, parent=None, opacity=0.45, ambient=0.7,
                 diffuse=0.4, specular=0.0)
        sc.frame_hooks.insert(0, lambda _sc: _sc.gmat.__setitem__(G_MIST, _sc.world(G_CAN)))
        self.fluids.append("bn mist")
        sc.alpha["bn mist"] = 0.0
        self.add("bn hose", S.hose_mesh(S.NILFISK_INLET, S.NILFISK_INLET + 100), (0.15, 0.15, 0.17), "bn_hose")
        self.fluids.append("bn hose")
        sc.frame_hooks.insert(0, lambda _sc: self.hose())
        self.place_tools()
        self.apply()
        AB.mir_at(self.ma, "front")
        # the can's cradle stand: its top just under the tool's lowest point there (so it carries it)
        self.can_stand()

    def place_tools(self):
        sc = self.sc
        for name, grp, tip in (("brush", G_BRUSH, S.BRUSH_TIP), ("scraper", G_SCRAPER, S.SCRAPER_TIP),
                               ("vac", G_VAC, S.VAC_TIP)):
            x, y = S.HOLSTERS[name]
            if name == "vac":
                y = y + S.VAC_OFF                    # the crevice tool's axis is 75 mm in front of the grip point
            pose = AB.P.tcp_frame((x, y, S.HOLSTER_SEAT[name] + tip + 0.5), DOWN, 0.0)
            sc.parent[grp] = "rp"
            sc.gmat[grp] = pose
        self.home = {g: sc.gmat[g].copy() for g in (G_BRUSH, G_SCRAPER, G_VAC)}
        # the plug, standing in its holster in the hood (its spigot on the holster's floor)
        px, py = S.PLUG_HOLSTER
        zh = S.Z_FLOOR + S.M.floor_z(S.HOLE_R)
        sc.parent[G_PLUG] = "rp"
        sc.gmat[G_PLUG] = T((px, py, S.HOOD_Z0 + 3.0 - (zh - 9.0) + 0.3))
        # the spray tool, in its cradle in the hood: level, its handle just outside the sash
        cx, cy = S.CAN_CRADLE
        sc.parent[G_CAN] = "rp"
        sc.gmat[G_CAN] = AB.P.tcp_frame((cx, -232.0, 1060.0), LEVEL, 0.0)
        self.can_home = sc.gmat[G_CAN].copy()

    def can_stand(self):
        sc = self.sc
        pts = []
        for nm in sc.members(G_CAN):
            m = pv.wrap(sc.actors[nm].GetMapper().GetInput()).transform(sc.gmat[G_CAN], inplace=False)
            pts.append(np.asarray(m.points))
        P = np.vstack(pts)
        sel = P[(P[:, 1] > -150) & (P[:, 1] < -60)]
        zt = float(sel[:, 2].min()) - 0.4
        x = float(P[:, 0].mean())
        stand = S._box(x - 40, x + 40, -150, -60, S.HOOD_Z0, zt)
        self.add("bn can stand", stand, (0.30, 0.31, 0.33), "bn_hoodfix", specular=0.3)

    # ------------------------------------------------------------------------------------------ state
    def apply(self):
        sc, v = self.sc, self.vals
        p = S.POS
        sc.gmat[G_TRUN] = T((p["x"], p["y"], p["axis"])) @ R((1, 0, 0), 180.0 * v["flip"]) @ R((0, 0, 1), v["spin"])
        for k in range(3):
            sc.gmat[f"bn_jaw{k}"] = T(S.jaw_dir(k) * S.JAW_OPEN * v["jaws"])
        cx, cy = S.CRU_IN_BOX
        sc.gmat[G_TT] = T((cx, cy, S.TT_LOW + S.TT["stroke"] * v["lift"])) @ R((0, 0, 1), v["tt"])
        sc.alpha["bn light beam"] = v["light"]

    def setv(self, **kw):
        self.vals.update(kw)
        self.apply()

    def anim(self, also=None, **targets):
        start = {k: self.vals[k] for k in targets}

        def up(u):
            self.setv(**{k: start[k] + (b - start[k]) * u for k, b in targets.items()})
            if also is not None:
                also(u)
        return up

    def paint(self):
        sc = self.sc
        for z, c in self.coat.items():
            new = S.WET if self.wet > 0.5 else S.MATTE
            if self.wet > 0.0 and self.wet < 1.0:
                new = tuple(a + (b - a) * self.wet for a, b in zip(S.MATTE, S.WET))
            base = self.base_c[z]
            col = tuple(a + (b - a) * min(1.0, c) for a, b in zip(base, new))
            sc.color[f"bn coat {z[0]} {z[1]}"] = col

    def hose(self):
        if self.sc.parent.get(G_VAC) == "rp" and np.allclose(self.sc.gmat[G_VAC], self.home[G_VAC]) and \
                getattr(self, "_hose_home", None) is not None:
            return
        Mw = self.sc.world(G_VAC)
        end_w = (Mw @ np.r_[S.VAC_HOSE_AT, 1.0])[:3]
        end = end_w - AB.RP
        mesh = S.hose_mesh(self.inlet, end, sag=120.0)
        self.sc.set_mesh("bn hose", mesh.translate(tuple(AB.RP), inplace=False))
        self._hose_home = True

    # ------------------------------------------------------------------------------------------ moves
    def step(self, label, caption, secs, update=None, cam=None, hold=0.0, **kw):
        self.sc.step(label, caption, max(0.2, secs * SPEED), update, hold=hold, cam_to=cam, **kw)

    def low(self, Tw):
        """A joint move to Tw in the IK branch with the wrist under the tool and the elbow up: the forearm then passes
        under the sash low, the elbow stays outside the hood (planned round anything in the way)."""
        rb, sc = self.rb, self.sc
        Wr = sc.world(rb.root)
        cands = collide.ik_all(rb.model, inv(Wr) @ Tw, rb.q) or []
        best = None
        for q in cands:
            fk = ur_arm.fk(rb.model, q)
            w1 = (Wr @ fk["wrist1"])[2, 3]
            el = (Wr @ fk["forearm"])[2, 3]
            sh = (Wr @ fk["upper_arm"])[2, 3]
            if w1 < Tw[2, 3] - 40.0 and el > sh:
                d = float(np.abs(q - rb.q).sum())
                if best is None or d < best[0]:
                    best = (d, q)
        return rb.joint_to(q1=best[1]) if best is not None else rb.joint_to(Tw=Tw)

    def tcp_m(self, p, approach, spin=0.0):
        return AB.tcp(p, approach, spin)

    def held_tcp(self, Wc_model) -> np.ndarray:
        """The TCP (world) that puts the held group at Wc_model (model frame)."""
        return AB.WT(Wc_model) @ inv(self.rb.held[1])

    def cru_world(self):
        return self.sc.world(G_CRU)

    def cru_model(self):
        return inv(T(AB.RP)) @ self.sc.world(G_CRU)


def cam(eye, at):
    return AB.cam(eye, at)


# ============================================================================================== the clip
def main():
    k = Clip()
    sc, rb, ma = k.sc, k.rb, k.ma
    p = S.POS
    CR_H, RO = S.CR_H, S.CR_RO
    face_z = p["axis"] + p["face"]                         # the chuck's face, upright: the crucible's base

    # the level grasp's TCP for the crucible (at its axis, 20 mm under the rim when upright; rolled 180 deg when it
    # is upside down) and for the plug (at its handle), from where the part's base / rim / frame is to go
    def tcp_up(x, y, zb):
        return AB.P.tcp_frame(tuple(AB.W((x, y, zb + S.CR_H - 20.0))), LEVEL, 0.0)

    def tcp_inv(x, y, zrim):
        return AB.P.tcp_frame(tuple(AB.W((x, y, zrim + 20.0))), LEVEL, 180.0)

    def tcp_plug(x, y, zf):
        return AB.P.tcp_frame(tuple(AB.W((x, y, zf + S.PLUG_GRIP_Z))), LEVEL, 0.0)
    AB.caption_rows(sc, Crucible="used: skull in, holder and nozzle off", Coat="fired; cracked on the floor")

    WIDE = cam((900.0, -3300.0, 2500.0), (2350.0, -250.0, 950.0))
    BENCH = cam((1520.0, -1080.0, 1650.0), (2060.0, -60.0, 1080.0))
    CHUCK = cam((1850.0, -420.0, 1720.0), (2030.0, -60.0, 1140.0))
    HOOD = cam((2420.0, -1250.0, 2250.0), (2840.0, 60.0, 1100.0))
    BOXC = cam((3040.0, -215.0, 1500.0), (2770.0, 118.0, 1080.0))
    RACKC = cam((2560.0, -900.0, 2050.0), (2880.0, 100.0, 1080.0))

    # ---------------------------------------------------------------------------------- 1. arrive
    up, secs = AB.mir_drive(ma, BENCH_SPOT)
    k.step("1/10", "MiR 1 brings the used crucible from the rePowder: the holder and nozzle are off, the skull of "
           "slag and metal is still inside (atom_crucible).", secs, up, cam=WIDE, hold=0.6)

    # ---------------------------------------------------------------------------------- 2. into the chuck
    cru_w = k.cru_world()
    top = cru_w[:3, 3] + np.array([0, 0, CR_H - 20.0])
    T_above = AB.P.tcp_frame(tuple(top + np.array([0, 0, 120.0])), DOWN, 0.0)
    T_at = AB.P.tcp_frame(tuple(top), DOWN, 0.0)
    cap = ("The arm lifts it out of MiR 1's cradle and stands it in the positioner's soft-jawed chuck (ours): "
           "acetal jaws on the outside, never on the bore.")
    k.step("2/10", cap, 2.4, rb.joint_to(Tw=T_above), cam=BENCH)
    k.step("2/10", cap, 1.0, rb.line_to(T_at))
    k.step("2/10", cap, 0.5, rb.grip_to(C_CRU))
    rb.grasp(G_CRU)
    k.step("2/10", cap, 1.0, rb.line_to(T_above))
    chuck_top = AB.W((p["x"], p["y"], face_z + CR_H - 20.0))
    k.step("2/10", cap, 2.6, rb.joint_to(Tw=AB.P.tcp_frame(tuple(chuck_top + [0, 0, 110.0]), DOWN, 0.0)))
    Wc = T((p["x"], p["y"], face_z + 0.2))
    k.step("2/10", cap, 1.2, rb.line_to(k.held_tcp(Wc)))
    k.step("2/10", cap, 0.6, k.anim(jaws=0.0))
    rb.release(G_TRUN)
    k.step("2/10", cap, 0.4, rb.grip_to(0.0))
    k.step("2/10", cap, 1.0, rb.line_to(AB.P.tcp_frame(tuple(chuck_top + [0, 0, 130.0]), DOWN, 0.0)), cam=CHUCK)

    # ---------------------------------------------------------------------------------- 3. skull out
    cap = ("The positioner turns it mouth down over the dark tray, 20 mm above it, and jolts it: a 5 deg flick and a hard "
           "stop. The skull drops out. Un-atomized metal is feedstock, not waste (178 SOP).")
    k.step("3/10", cap, 2.2, k.anim(flip=1.0), hold=0.2)

    def knock(n):
        """The tap: the positioner flicks the crucible 5 deg and stops it hard, n times (ours)."""
        f0 = k.vals["flip"]

        def up(u):
            k.setv(flip=f0 - (5.0 / 180.0) * abs(math.sin(math.pi * n * u)))
        return up
    k.step("3/10", cap, 1.0, knock(3))
    # the skull falls: from where it is to the tray, in free fall (h = g t^2 / 2)
    Ws = sc.world(G_SKULL)
    sc.parent.pop(G_SKULL, None)
    sc.gmat[G_SKULL] = Ws
    zs0 = Ws[2, 3]
    # inverted, the skull's lowest point is its (now downward) top face, ~10 mm out from its frame's origin
    lowest = float(min(pv.wrap(sc.actors["bn skull"].GetMapper().GetInput()).transform(Ws, inplace=False).points[:, 2]))
    drop = lowest - (AB.RP[2] + S.BENCH["top"] + 3.0) - 0.3
    t_fall = math.sqrt(2 * drop / 9810.0)
    Wland = Ws.copy()

    def fall(u):
        t = u * t_fall
        M = Ws.copy()
        M[2, 3] = zs0 - 0.5 * 9810.0 * t * t
        sc.gmat[G_SKULL] = M
    sc.step("3/10", cap, max(t_fall, 1.0 / 15), fall, hold=0.0)
    Wland[2, 3] = zs0 - drop
    sc.gmat[G_SKULL] = Wland
    k.step("3/10", cap, 1.6, k.anim(flip=0.0), hold=0.3,
           labels=[("skull: feedstock", tuple(Wland[:3, 3] + [0, 0, 20]), (0.20, 0.70))])
    AB.caption_rows(sc, Crucible="skull out", Coat="fired; cracked on the floor")

    # ---------------------------------------------------------------------------------- 4. brush
    def tool_out(grp, label, cap):
        home = k.home[grp]
        Wh = AB.WT(home)
        k.step(label, cap, 2.2, rb.joint_to(Tw=Wh @ T((0, 0, -120.0))))
        k.step(label, cap, 0.9, rb.line_to(Wh))
        k.step(label, cap, 0.4, rb.grip_to(C_TOOL))
        rb.grasp(grp)
        k.step(label, cap, 1.2, rb.line_to(Wh @ T((0, 0, -260.0))))

    def tool_back(grp, label, cap):
        home = k.home[grp]
        Wh = AB.WT(home)
        k.step(label, cap, 2.0, rb.joint_to(Tw=Wh @ T((0, 0, -260.0))))
        k.step(label, cap, 1.2, rb.line_to(Wh))
        rb.release("rp")
        k.step(label, cap, 0.4, rb.grip_to(0.0))
        k.step(label, cap, 0.8, rb.line_to(Wh @ T((0, 0, -120.0))))

    axis_top = np.array([p["x"], p["y"], face_z + CR_H])          # the rim's centre, model
    cap = "A soft nylon bore brush (ours) loosens what is left, the chuck turning under it (bronze plan, step 1)."
    tool_out(G_BRUSH, "4/10", cap)
    over = AB.P.tcp_frame(tuple(AB.W(axis_top + [0, 0, 60.0 + S.BRUSH_TIP])), DOWN, 0.0)
    deep = AB.P.tcp_frame(tuple(AB.W(axis_top + [0, 0, -(S.CR_H - S.Z_FLOOR) + 4.0 + S.BRUSH_TIP])), DOWN, 0.0)
    k.step("4/10", cap, 1.6, rb.joint_to(Tw=over), cam=CHUCK)
    k.step("4/10", cap, 1.3, rb.line_to(deep), hold=0.0)
    s0 = k.vals["spin"]
    k.step("4/10", cap, 1.6, k.anim(spin=s0 + 360.0))
    k.step("4/10", cap, 1.1, rb.line_to(over))
    tool_back(G_BRUSH, "4/10", cap)

    # ---------------------------------------------------------------------------------- 5. scrape
    cap = ("An acetal scraper (ours) takes off what is cracked or lifted, and stops at the thin grey layer that won't "
           "come off. It never touches the seat round the hole: the sealing rod seals there.")
    tool_out(G_SCRAPER, "5/10", cap)
    # the blade's edge sits 19 mm out from the stem: the stem 9 mm off the axis puts it 0.5 mm off the wall
    off = -(S.CR_RI - 0.5 - S.SCRAPER_EDGE[1])        # the edge is on the tool's +y: the world's -y, the front wall
    hi = AB.P.tcp_frame(tuple(AB.W(axis_top + [0, off, 40.0 + S.SCRAPER_TIP])), DOWN, 0.0)
    lo = AB.P.tcp_frame(tuple(AB.W(axis_top + [0, off, -(S.CR_H - S.Z_FLOOR) + 6.0 + S.SCRAPER_EDGE[2] - 182.0 + S.SCRAPER_TIP])), DOWN, 0.0)
    k.step("5/10", cap, 1.6, rb.joint_to(Tw=hi), cam=CHUCK)
    seat_lab = [("seat: never scraped", tuple(AB.W(axis_top + [0, 0, -(S.CR_H - S.Z_FLOOR) - 14.0])), (0.70, 0.78)),
                ("blade on the wall", tuple(AB.W(axis_top + [0, -S.CR_RI, -60.0])), (0.75, 0.30))]
    damaged = sorted(z for z in S.DAMAGE)
    for rep in range(3):
        k.step("5/10", cap, 0.9, rb.line_to(lo), labels=seat_lab if rep == 0 else ())
        k.step("5/10", cap, 0.7, rb.line_to(hi))
        a0 = k.vals["spin"]
        part = damaged[rep::3]

        def scraped(u, part=part):
            for z in part:
                k.base_c[z] = tuple(a + (b - a) * u for a, b in zip(S.DAMAGED, S.SCRAPED))
            k.paint()
        k.step("5/10", cap, 0.8, k.anim(spin=a0 + 120.0, also=scraped))
    for z in damaged:
        k.base_c[z] = S.SCRAPED
    k.paint()
    tool_back(G_SCRAPER, "5/10", cap)
    AB.caption_rows(sc, Crucible="scraped: floor and five wall spots back to the grey bonded layer",
                    Coat="old coat kept where it is sound")

    # ---------------------------------------------------------------------------------- 6. tip out, vacuum
    cap = ("Mouth down and tapped again: the flakes fall on the dark tray. Then the dust comes out dry: the "
           "Nilfisk's crevice tool, close to the surface, slow (vacuum SOP). No compressed air, no IPA: nothing oily.")
    k.step("6/10", cap, 1.8, k.anim(flip=1.0), cam=CHUCK)
    k.step("6/10", cap, 0.8, knock(2))
    k.step("6/10", cap, 1.6, k.anim(flip=0.0))
    tool_out(G_VAC, "6/10", cap)
    vo = np.array([0.0, S.VAC_OFF, 0.0])     # the grip point is 75 mm behind the crevice tool's axis (world +y)
    over = AB.P.tcp_frame(tuple(AB.W(axis_top + vo + [0, 0, 25.0 + S.VAC_TIP])), DOWN, 0.0)
    deep = AB.P.tcp_frame(tuple(AB.W(axis_top + vo + [0, 0, -(S.CR_H - S.Z_FLOOR) + 8.0 + S.VAC_TIP])), DOWN, 0.0)
    k.step("6/10", cap, 1.8, rb.joint_to(Tw=over))
    k.step("6/10", cap, 1.4, rb.line_to(deep))
    a0 = k.vals["spin"]
    k.step("6/10", cap, 2.0, k.anim(spin=a0 + 360.0))
    k.step("6/10", cap, 1.2, rb.line_to(over))
    tool_back(G_VAC, "6/10", cap)
    AB.caption_rows(sc, Crucible="clean and dry", Coat="ready for a touch-up")

    # ---------------------------------------------------------------------------------- 7. into the hood
    cap = ("To the hood, its sash at the 18 in (457 mm) working stop. The arm works under the sash, as a person "
           "does; only the gripper and what it holds go in.")
    side = AB.P.tcp_frame(tuple(AB.W((p["x"], p["y"] - 150.0, face_z + CR_H - 20.0))), LEVEL, 0.0)
    grip = AB.P.tcp_frame(tuple(AB.W((p["x"], p["y"], face_z + CR_H - 20.0))), LEVEL, 0.0)
    k.step("7/10", cap, 2.2, rb.joint_to(Tw=side), cam=BENCH)
    k.step("7/10", cap, 1.2, rb.line_to(grip))
    k.step("7/10", cap, 0.5, rb.grip_to(C_CRU))
    k.step("7/10", cap, 0.5, k.anim(jaws=1.0))
    rb.grasp(G_CRU)
    lifted = tcp_up(p["x"], p["y"], face_z + 60.0)
    k.step("7/10", cap, 1.0, rb.line_to(lifted))
    carry = AB.P.tcp_frame(tuple(AB.W((BENCH_SPOT[0], -235.0, 1250.0))), LEVEL, 0.0)
    k.step("7/10", cap, 2.0, rb.joint_to(Tw=carry))
    up, secs = AB.mir_drive(ma, HOOD_SPOT)
    k.step("7/10", cap, secs, up, cam=HOOD)
    cx, cy = S.CRU_IN_BOX
    base_hi = S.TT_HIGH
    over_rim = S.BOX_RIM + 15.0                 # the crucible's base 15 mm over the box's rim on the way in
    OUT_Y = -330.0                              # staging, outside the sash (y -203 .. -185)
    k.step("7/10", cap, 2.2, k.low(tcp_up(cx, OUT_Y, over_rim)))
    k.step("7/10", cap, 2.0, rb.line_to(tcp_up(cx, cy, over_rim)))
    k.step("7/10", cap, 0.9, rb.line_to(tcp_up(cx, cy, base_hi + 0.2)))
    rb.release(G_TT)
    k.step("7/10", cap, 0.4, rb.grip_to(0.0))
    k.step("7/10", cap, 1.6, rb.line_to(tcp_up(cx, OUT_Y, base_hi + 0.2)))

    # the seat plug: the arm holds it over the box, the lift raises the crucible onto it
    cap = ("A PTFE plug (ours) masks the nozzle seat and the hole: the arm holds it still and the lift raises the "
           "crucible onto it. Spray must stay out of the seat and bore (bronze plan).")
    k.step("7/10", cap, 0.8, k.anim(lift=0.0))
    zf_h = S.HOOD_Z0 + 3.0 - (S.Z_FLOOR + S.M.floor_z(S.HOLE_R) - 9.0) + 0.3
    px_, py_ = S.PLUG_HOLSTER
    Z_HI = 1340.0 - S.PLUG_GRIP_Z               # the plug's frame high enough that it clears the box's rim
    k.step("7/10", cap, 1.8, k.low(tcp_plug(px_, OUT_Y, zf_h)), cam=BOXC)
    k.step("7/10", cap, 1.8, rb.line_to(tcp_plug(px_, py_, zf_h)))
    k.step("7/10", cap, 0.4, rb.grip_to(C_TOOL))
    rb.grasp(G_PLUG)
    k.step("7/10", cap, 1.2, rb.line_to(tcp_plug(px_, py_, Z_HI)))
    k.step("7/10", cap, 1.2, rb.line_to(tcp_plug(cx, cy, Z_HI)))
    LP = 0.65                                     # the lift's height for the plug: the gripper stays clear of the box
    base_p = S.TT_LOW + S.TT["stroke"] * LP
    k.step("7/10", cap, 1.0, rb.line_to(tcp_plug(cx, cy, base_p + 0.2)))
    k.step("7/10", cap, 1.6, k.anim(lift=LP))
    rb.release(G_CRU)
    k.step("7/10", cap, 0.4, rb.grip_to(0.0))
    k.step("7/10", cap, 1.4, rb.line_to(tcp_plug(cx, OUT_Y, base_p + 0.2)))
    k.step("7/10", cap, 1.2, k.anim(lift=0.0))
    AB.caption_rows(sc, Crucible="in the box, 70 mm under its rim: still air", Seat="masked")

    # ---------------------------------------------------------------------------------- 8. spray
    Wh = AB.WT(k.can_home)
    cap = ("The spray tool (ours) holds the 13 oz can of Momentive BN Spray II. The arm shakes it for 90 s at about "
           "2.5 Hz, well past the minute after the ball starts to rattle: BN settles fast.")
    k.step("8/10", cap, 2.2, rb.joint_to(Tw=Wh @ T((0, 0, -140.0))), cam=HOOD)
    k.step("8/10", cap, 1.0, rb.line_to(Wh))
    k.step("8/10", cap, 0.4, rb.grip_to(C_TOOL))
    rb.grasp(G_CAN)
    out_ = AB.WT(k.can_home) @ T((0, -60.0, -330.0))
    k.step("8/10", cap, 1.6, rb.line_to(out_))
    # the shake: +-20 mm along the can's axis, solved at the two ends, swung between them
    a_t = S.can_axis_tool()
    qa = rb.solve(out_ @ T(tuple(a_t * 20.0)), rb.q)
    qb = rb.solve(out_ @ T(tuple(-a_t * 20.0)), rb.q)
    q_mid = rb.q.copy()

    def shake(u):
        s = math.sin(2 * math.pi * 7.5 * u)
        rb.set(q_mid + (qa - q_mid) * max(s, 0) + (qb - q_mid) * max(-s, 0))
    sc.step("8/10", cap, 3.0, shake, hold=0.0)
    rb.set(q_mid)
    AB.caption_rows(sc, Shake="90 s (3 s shown)", Crucible="in the box, 70 mm under its rim: still air",
                    Seat="masked")

    # the bursts. Two aims: the upper wall (the beam's centre 28 mm under the rim, the can 175 mm away) and the lower
    # wall (61 mm under, 200 mm away). The box's front wall stops a steeper aim: the floor gets the burst's lower
    # edge and the mist that settles (bronze plan: it builds up fastest).
    sd = S.spray_dir_tool()
    s_w = np.array([0.0, sd[2], -sd[1]])            # tool z = world +y, tool y = world -z
    far_y = cy + S.CR_RI
    rim = S.TT_LOW + CR_H

    def aim_pose(d, L):
        spot = np.array([cx, far_y, rim - d])
        noz = spot - s_w * L
        n_t = S.nozzle_tool()                       # tool frame -> world offset of the orifice from the TCP
        off_w = np.array([n_t[0], n_t[2], -n_t[1]])
        return AB.P.tcp_frame(tuple(AB.W(noz - off_w)), LEVEL, 0.0)
    A_up, A_lo = aim_pose(28.0, 175.0), aim_pose(61.0, 200.0)
    cap = ("Short, quick bursts 15-20 cm from the wall, aimed at the walls, not the floor; the turntable turns the "
           "crucible between them. Only the scraped spots get sprayed: a touch-up, not the whole inside.")
    k.step("8/10", cap, 2.4, rb.joint_to(Tw=A_up), cam=BOXC)

    def sector_at_front():
        # the sector facing the can (the far wall, +y in the world) at the turntable's angle
        ang = (90.0 - k.vals["tt"]) % 360.0
        return int(ang // (360.0 / S.N_SEC)) % S.N_SEC

    def burst(band, amount, label, secs=0.35):
        def up(u):
            sc.alpha["bn mist"] = 1.0 if u < 0.92 else 0.0
            if u >= 0.92 and not getattr(up, "done", False):
                up.done = True
                j = sector_at_front()
                for b, kk, f in ((band, j, 1.0), (band, j - 1, 0.35), (band, j + 1, 0.35)):
                    z = (b, kk % S.N_SEC)
                    if z in S.DAMAGE:
                        k.coat[z] = min(1.0, k.coat[z] + amount * f)
                if band == "low":
                    for kk in (j - 1, j, j + 1):
                        z = ("floor", kk % S.N_SEC)
                        k.coat[z] = min(1.0, k.coat[z] + amount * 0.45)
                k.paint()
        return up

    def turn_to_sector(j):
        target = 90.0 - (j + 0.5) * 360.0 / S.N_SEC
        cur = k.vals["tt"]
        d = (target - cur) % 360.0
        return k.anim(tt=cur + d)

    k.wet = 1.0
    passes = [(0.55, "Pass 1"), (0.5, "Pass 2")]
    for ip, (amt, pname) in enumerate(passes):
        AB.caption_rows(sc, Spray=f"{pname} of 2: light", Crucible="in the box", Seat="masked")
        if ip > 0:
            k.step("8/10", cap, 2.0, rb.joint_to(Tw=A_up))
        for j in sorted({kk for (b, kk) in S.DAMAGE if b == "up"}):
            k.step("8/10", cap, 0.5, turn_to_sector(j))
            sc.step("8/10", cap, 0.35, burst("up", amt, pname), hold=0.0)
        k.step("8/10", cap, 1.2, rb.line_to(A_lo))
        for j in sorted({kk for (b, kk) in S.DAMAGE if b == "low"}):
            k.step("8/10", cap, 0.45, turn_to_sector(j))
            sc.step("8/10", cap, 0.35, burst("low", amt, pname), hold=0.0)
            if ip == 1 and j == 7:              # the still: one burst, its mist in the air
                sc.step("8/10", cap, 0.2, lambda u: sc.alpha.__setitem__("bn mist", 1.0), hold=0.0, still=True)
                sc.alpha["bn mist"] = 0.0
        if ip == 0:
            # the 5 min wait: time-lapse
            k.step("8/10", "About 5 min between passes, longer if the last one still looks wet: the coat dries "
                   "slowly in the box (bronze plan). Time-lapse.", 2.2,
                   lambda u: AB.caption_rows(sc, Spray=f"waiting {int(5 * u)}:{int((300 * u) % 60):02d} of 5:00",
                                             Crucible="in the box", Seat="masked"), hold=0.3)
    cap = ("Then the can upside down for 4 s to clear its valve: upside down it sprays only propellant, aimed at the "
           "hood's back, away from the box.")
    clear_p = AB.P.tcp_frame(tuple(AB.W((cx + 230.0, -250.0, 1150.0))), (0.0, 1.0, 0.0), 180.0)
    k.step("8/10", cap, 2.2, rb.joint_to(Tw=clear_p), cam=HOOD)
    AB.caption_rows(sc, Spray="valve clearing, 4 s", Crucible="in the box", Seat="masked")
    sc.alpha["bn mist"] = 0.0
    sc.step("8/10", cap, 1.6, lambda u: sc.alpha.__setitem__("bn mist", 0.6 if u < 0.95 else 0.0), hold=0.2)
    k.step("8/10", cap, 2.2, rb.joint_to(Tw=Wh @ T((0, 0, -140.0))))
    k.step("8/10", cap, 1.0, rb.line_to(Wh))
    rb.release("rp")
    k.step("8/10", cap, 0.4, rb.grip_to(0.0))
    k.step("8/10", cap, 0.9, rb.line_to(Wh @ T((0, 0, -140.0))))

    # ---------------------------------------------------------------------------------- 9. dry overnight
    cap = ("Plug out, and the crucible goes upside down on the drying rack in the running hood: nothing pools on "
           "the floor and the draft can't reach inside (bronze plan).")
    k.step("9/10", cap, 1.2, k.anim(lift=LP), cam=BOXC)
    k.step("9/10", cap, 2.0, k.low(tcp_plug(cx, OUT_Y, base_p + 0.2)))
    k.step("9/10", cap, 1.4, rb.line_to(tcp_plug(cx, cy, base_p + 0.2)))
    k.step("9/10", cap, 0.4, rb.grip_to(C_TOOL))
    rb.grasp(G_PLUG)
    k.step("9/10", cap, 1.5, k.anim(lift=0.0))
    k.step("9/10", cap, 1.0, rb.line_to(tcp_plug(cx, cy, Z_HI)))
    k.step("9/10", cap, 1.2, rb.line_to(tcp_plug(px_, py_, Z_HI)))
    k.step("9/10", cap, 1.2, rb.line_to(tcp_plug(px_, py_, zf_h + 0.2)))
    rb.release("rp")
    k.step("9/10", cap, 0.4, rb.grip_to(0.0))
    k.step("9/10", cap, 1.4, rb.line_to(tcp_plug(px_, OUT_Y, zf_h + 0.2)))
    k.step("9/10", cap, 1.4, k.anim(lift=1.0))
    k.step("9/10", cap, 1.8, k.low(tcp_up(cx, OUT_Y, base_hi + 0.2)))
    k.step("9/10", cap, 1.4, rb.line_to(tcp_up(cx, cy, base_hi + 0.2)))
    k.step("9/10", cap, 0.4, rb.grip_to(C_CRU))
    rb.grasp(G_CRU)
    k.step("9/10", cap, 0.9, rb.line_to(tcp_up(cx, cy, over_rim)))
    k.step("9/10", cap, 1.6, rb.line_to(tcp_up(cx, OUT_Y, over_rim)))
    # turned over outside the hood (a 180 deg roll of the wrist), then in, onto the rack's three pins
    rx, ry = S.RACK
    zr = S.RACK_TOP + 0.3                       # the inverted crucible's rim on the pins
    k.step("9/10", cap, 1.2, rb.line_to(tcp_up(rx, OUT_Y, over_rim)), cam=RACKC)
    k.step("9/10", cap, 2.0, rb.joint_to(Tw=AB.P.tcp_frame(tuple(AB.W((rx, OUT_Y, over_rim + S.CR_H - 20.0))), LEVEL,
                                                           180.0)))
    k.step("9/10", cap, 1.2, rb.line_to(tcp_inv(rx, OUT_Y, zr + 30.0)))
    k.step("9/10", cap, 1.8, rb.line_to(tcp_inv(rx, ry, zr + 30.0)))
    k.step("9/10", cap, 0.8, rb.line_to(tcp_inv(rx, ry, zr)))
    rb.release("rp")
    k.step("9/10", cap, 0.4, rb.grip_to(0.0))
    k.step("9/10", cap, 1.6, rb.line_to(tcp_inv(rx, OUT_Y, zr)))
    k.step("9/10", cap, 2.0, rb.joint_to(Tw=AB.P.tcp_frame(tuple(AB.W((HOOD_SPOT[0], -430.0, 1250.0))), LEVEL, 0.0)))

    def night(u):
        h = 18.5 + 13.0 * u
        AB.caption_rows(sc, Clock=f"{int(h) % 24:02d}:{int((h % 1) * 60):02d}", Hood="running, sash at 18 in",
                        Coat="drying" if u < 0.9 else "dry")
        k.wet = max(0.0, 1.0 - u * 1.3)
        k.paint()
    k.step("9/10", "Overnight in the running hood, upside down. The vapour leaves the box, so nobody has to check by "
           "smell. Never pour onto a wet coat (bronze plan). Time-lapse.", 4.0, night, cam=RACKC, hold=0.5)
    k.wet = 0.0
    k.paint()

    # ---------------------------------------------------------------------------------- 10. check
    cap = ("In the morning the arm takes it to the bench, upright in the chuck, and looks in with its wrist camera "
           "under a low side light: cracks, lifted edges and bare graphite cast or show dark.")
    k.step("10/10", cap, 2.0, k.low(tcp_inv(rx, OUT_Y, zr)), cam=RACKC)
    k.step("10/10", cap, 1.6, rb.line_to(tcp_inv(rx, ry, zr)))
    k.step("10/10", cap, 0.4, rb.grip_to(C_CRU))
    rb.grasp(G_CRU)
    k.step("10/10", cap, 0.8, rb.line_to(tcp_inv(rx, ry, zr + 30.0)))
    k.step("10/10", cap, 1.6, rb.line_to(tcp_inv(rx, OUT_Y, zr + 30.0)))
    k.step("10/10", cap, 2.0, rb.joint_to(Tw=AB.P.tcp_frame(tuple(AB.W((rx, OUT_Y, zr + 50.0))), LEVEL, 0.0)))
    k.step("10/10", cap, 1.6, rb.joint_to(Tw=AB.P.tcp_frame(tuple(AB.W((HOOD_SPOT[0], -330.0, 1250.0))), LEVEL, 0.0)))
    up, secs = AB.mir_drive(ma, BENCH_SPOT)
    k.step("10/10", cap, secs, up, cam=BENCH)
    Wc = T((p["x"], p["y"], face_z + 0.2))
    k.step("10/10", cap, 2.2, rb.joint_to(Tw=tcp_up(p["x"], p["y"] - 160.0, face_z + 30.0)))
    k.step("10/10", cap, 1.2, rb.line_to(tcp_up(p["x"], p["y"], face_z + 30.0)))
    k.step("10/10", cap, 0.8, rb.line_to(tcp_up(p["x"], p["y"], face_z + 0.2)))
    k.step("10/10", cap, 0.5, k.anim(jaws=0.0))
    rb.release(G_TRUN)
    k.step("10/10", cap, 0.4, rb.grip_to(0.0))
    k.step("10/10", cap, 1.2, rb.line_to(rb.tcp_world() @ T((0, 0, -170.0))))
    look = AB.P.tcp_frame(tuple(AB.W(axis_top + [0, -45.0, 150.0])), DOWN, 0.0)
    k.step("10/10", cap, 2.2, rb.joint_to(Tw=look), cam=CHUCK)
    AB.caption_rows(sc, Light="side light on", Camera="D405, 250 mm from the floor")
    k.step("10/10", cap, 0.6, k.anim(light=1.0))
    a0 = k.vals["spin"]

    def check(u):
        k.setv(spin=a0 + 360.0 * u)
        AB.caption_rows(sc, Light="side light on", Floor="matte white, no black graphite",
                        Cracks="none found" if u > 0.5 else "looking", Lifted="none found" if u > 0.8 else "looking")
    k.step("10/10", "The check (ours, on the D405's colour image): dark pixels on the floor and the floor-wall corner "
           "mean bare graphite; thin dark lines, cracks; a bright edge with a shadow beside it, a lifted flake.", 3.4,
           check, hold=0.6)
    cap = ("Then mouth down over the dark tray and tapped once more: nothing falls, so nothing can reach the 0.5 mm "
           "nozzle. Ready. For copper, it is cured empty under argon in the furnace first: a fresh coat smokes at 500 C.")
    k.step("10/10", cap, 0.5, k.anim(light=0.0))
    k.step("10/10", cap, 1.6, rb.line_to(rb.tcp_world() @ T((0, 0, -120.0))))
    k.step("10/10", cap, 1.8, k.anim(flip=1.0))
    k.step("10/10", cap, 0.8, knock(2))
    k.step("10/10", cap, 1.8, k.anim(flip=0.0))
    AB.caption_rows(sc, Crucible="coated, dry, checked: ready", Next="back into the furnace (atom_crucible)")
    k.step("10/10", cap, 2.0, rb.joint_to(Tw=AB.P.tcp_frame(tuple(AB.W((BENCH_SPOT[0], -200.0, 1330.0))), LEVEL, 0.0)),
           cam=BENCH, hold=1.5)
    return AB.finish(sc)


if __name__ == "__main__":
    main()
