"""The alloy route, chapter 6: sample prep. Chapter 5's AlSi10Mg build is sectioned and two specimens are made for
chapter 7 (#303, PR #318, round 8).

    VIZ3D_FPS=6 xvfb-run --server-num=11 -a python3 alloy_prep.py      # -> out/alloy_prep.{gif,json}, out/mp4/alloy_prep.mp4,
                                                                        #    out/alloy_prep_still.png
    PREVIEW=1 xvfb-run --server-num=11 -a python3 alloy_prep.py         # the last frame of each step -> /tmp
    ARM_AUDIT=1 xvfb-run --server-num=11 -a python3 alloy_prep.py       # every frame collision-checked -> out/collisions/

The lab is the two-Shuttle floor of ``setup_lab.py`` (``animate.lab_scene``'s build: every tray loaded, the floor
machines, the utilities), with the MiR250 + UR10e docked at Shuttle 1. The machines are ``r8_prep.py``'s:

1. **Sectioning, on the wire EDM** (the floor's FANUC, chapter 5's): a coupon (14 x 10 x 6 mm) and a slice
   (10 x 10 x 6 mm). Not the CNC: see the caption and notes/alloy_prep.md.
2. **The slice faced on the Carvera** (tray M, Shuttle 2), both sides, flat and parallel, 6 to 5.6 mm.
3. **The steel mount** (``r8_specimens.steel_mount``): the slice into its pocket, held by an M3 set screw.
4. **The coupon hot-mounted in the LECO MX400** (tray F), the full procedure of the lab's own video.
5. **Ground and polished on the PX500** (tray F): the arm changes whole pre-loaded discs (each with its paper or cloth
   and its retaining ring) between the magazine and the magnetic platen, 320 to 1200 grit SiC, then the cloth with
   1 um alumina, at the SOP's settings.
6. Rinsed and dried, and into the sample store for chapter 7.

The arm's moves are the disc changes (straight lines of the grasp point and planned joint moves, ``robot.py``,
``collide.py``). The specimens' transfers into the CNC's vise, the press's mold and the steel mount are drawn with the
machines' own prop joints (``r8_prep``), as in their tour clips: what is and isn't an arm move here is listed in
notes/alloy_prep.md.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pyvista as pv

import scene
scene.GIF_FPS = 3                      # a ~3-minute GIF under 4.9 MB (the MP4 keeps every frame)
scene.GIF_SIZE = (512, 288)
from scene import FPS, OUT, PREVIEW, Scene, T, R  # noqa: E402

import animate as A                    # noqa: E402
import lab                             # noqa: E402
import r8_prep as RP                   # noqa: E402
import r8_specimens as SP              # noqa: E402
import vlm as V                        # noqa: E402

NAME = "alloy_prep"
TITLE = "Vertical cloud lab, the alloy route 6/7: sample prep"
FAST = 0.30                            # the later disc changes: a time-lapse
CAM_LAB = [(9800, -12500, 6900), (1700, -1800, 1300), (0, 0, 1)]
ST_AT, HOT_AT = (290.0, -170.0), (210.0, -170.0)     # the steel and the hot mount on the MiR's cabinet top (MiR frame),
#                                                      clear of the buffer holder (animate.BUFFER_LOCAL) and the arm


def status(sc, **kv):
    rows = dict(getattr(sc, "_rows", {}))
    rows.update(kv)
    sc._rows = rows
    sc.gauges = [(k, v) for k, v in rows.items() if v]


def build():
    import setup_lab as SL
    import warehouse as W
    data = lab.meshes()
    idata = SL.load_all()
    sc, L, F, items, rigs, units, util, ulabel, vp = SL.build(data, idata, name=NAME, title=TITLE)
    sc.gif = not (PREVIEW or scene.AUDIT)
    SL.add_bay_cams(sc)
    u = units[0]
    u.set(W.dock_pose("vlm"))
    L.robot = u.robot
    L.unit = getattr(L, "unit", {})
    L.skin(1.0)(1.0)
    L.show_gauges = False
    L.apply_state()
    return sc, L, F, rigs, u


def rig_of(rigs, key):
    for k, r in rigs.items():
        if k.split("_", 1)[1] == key:
            return r
    raise KeyError(key)


def show_props(sc, rig, pieces):
    """setup_lab hides an instrument's props; the chapter runs them: put them back under the rig's control."""
    for pc in pieces:
        g = f"{rig.prefix}{pc}"
        names = sc.members(g)
        rig.names[pc] = names
        for n in names:
            sc.alpha[n] = 1.0
    rig.apply()


def hide_props(sc, rig, pieces):
    for pc in pieces:
        for n in rig.names.get(pc, []):
            sc.alpha[n] = 0.0
        rig.names[pc] = []


def mesh_of(solid, tol=0.3):
    return lab.to_mesh(solid.val() if hasattr(solid, "val") else solid, tol, 0.15)


def add_disc(sc, kind):
    g = f"pd_{kind}"
    for nm, (solid, mat) in RP.disc_solids(kind).items():
        r, gg, b, op, spec = RP.MATERIALS.get(mat) or lab.MATS.get(mat) or RP.I.MATERIALS[mat]
        sc.add(f"{g}/{nm}", mesh_of(solid), (r, gg, b), g, opacity=op, specular=spec)
    return g


def cam_at(target, off, look=(0.0, 0.0, 0.0)):
    t = np.asarray(target, float)
    return [tuple(t + np.asarray(off, float)), tuple(t + np.asarray(look, float)), (0, 0, 1)]


def movie():
    sc, L, F, rigs, u = build()
    rb = u.robot
    pol, press, mag, cnc = (rig_of(rigs, k) for k in ("polisher", "mount_press", "disc_magazine", "cnc"))
    show_props(sc, pol, ("holder",))
    show_props(sc, press, ("specimen", "charge", "mount", "stopper", "glow"))
    show_props(sc, cnc, ("carrier", "flip", "part", "stock", "stock2"))
    for pc, v in (("specimen", 0.0), ("charge", 0.0), ("mount", 0.0), ("stopper", 0.0), ("glow", 0.0)):
        press.v[pc] = v
    press.apply()
    for pc, v in (("carrier", 0.0), ("flip", 0.0), ("part", 1.0), ("stock", 1.0), ("stock2", 1.0)):
        cnc.v[pc] = v
    cnc.apply()
    # the discs: our own groups (the arm carries them), at home in the magazine
    discs = {k: add_disc(sc, k) for k in RP.GRITS}
    G = RP.px_geometry()
    m_off = np.array([G["mag"][0], G["mag"][1], 0.0])

    def home(kind):
        i = RP.GRITS.index(kind)
        sc.parent[discs[kind]] = f"{mag.prefix}body"
        sc.gmat[discs[kind]] = T(RP.disc_home(i)[:3, 3] - m_off)
    for k in RP.GRITS:
        home(k)
    # the polisher's water and suspension, ours (the rig's ride on its head)
    show_props(sc, pol, ("water", "powder"))
    pol.v.update(water=0.0, powder=0.0)
    pol.apply()
    sc.apply()

    tray_f = "tray_F"
    # ------------------------------------------------------------------ 0. the lab
    sc.cam = list(CAM_LAB)
    status(sc, Build="AlSi10Mg, chapter 5's", Coupon="to cut", Slice="to cut")
    sc.step("6/7", "Chapter 6, sample prep. Chapter 5's AlSi10Mg build gives chapter 7 two specimens: a coupon "
            "hot-mounted in conductive phenolic (SEM/EDS, micro-Vickers), and a slice set in a steel mount "
            "(nanoindentation and PIP: nothing soft under the sample).", 4.5, hold=1.0)

    # ------------------------------------------------------------------ 1. sectioning on the wire EDM
    edm = F.where.get("wire_edm") if hasattr(F, "where") else None
    ex = 6600.0 if edm is None else float(edm[0])
    ey = -6238.0
    cam_edm = [(ex + 2600, ey + 3300, 2600), (ex, ey - 900, 1100), (0, 0, 1)]
    sc.step("Section", "Sectioning, on the wire EDM on the floor (chapter 5's machine): a 14 x 10 x 6 mm coupon and a "
            "10 x 10 x 6 mm slice, cut from the build's plate with no cutting force and only a thin recast layer.",
            3.5, cam_to=cam_edm, hold=1.6)
    status(sc, Coupon="cut, 14 x 10 x 6 mm", Slice="cut, 10 x 10 x 6 mm")
    sc.step("Section", "Why the EDM and not the CNC: the Carvera's 200 W spindle and ER11 collet take no slitting saw "
            "for parting AlSi10Mg, and a sawn face would need facing anyway. The CNC does what it is good at: facing "
            "the slice.", 1.0, hold=3.4)

    # ------------------------------------------------------------------ 2. the slice faced on the Carvera (tray M)
    cw = sc.world(f"{cnc.prefix}body")
    cpt = (cw @ np.r_[RP.SLICE["x"], RP.SLICE["y"], RP.CV["face_z"], 1.0])[:3]
    cam_cnc = cam_at(cpt, (520, -1250, 760))
    L.fetch("M", "CNC", "Tray M comes to Shuttle 2's opening: the Makera Carvera.", fast=0.45, cam=CAM_LAB, hold=0.2)
    cnc_steps = {i: a for i, a in enumerate(cnc.inst.actions)}
    secs = (1.6, 1.8, 2.0, 3.2, 2.4, 3.6, 2.0)
    caps = ("The Carvera's lid opens.",
            "The slice goes on the parallel in its vise (ours).",
            "Clamped, the lid shut, a 6 mm end mill from the tool changer.",
            "Side 1 faced: 0.2 mm off takes the EDM's recast layer and the cut's waviness.",
            "Turned over for side 2.",
            "Side 2 faced to 5.6 mm: flat, and parallel to side 1, as nanoindentation and PIP need.",
            "Done: out for the steel mount.")
    for i, (cap_, sec) in enumerate(zip(caps, secs)):
        tg = cnc_steps[i][2]
        sc.step("CNC", cap_, sec, cnc.move(tg), cam_to=cam_cnc if i == 0 else None, hold=0.3)
    status(sc, Slice="faced, 10 x 10 x 5.6 mm")
    hide_props(sc, cnc, ("part", "stock", "stock2"))
    L.store("M", "CNC", "Tray M goes back; the arm brings the slice to its steel mount.", fast=0.45, hold=0.1)

    # ------------------------------------------------------------------ 3. the steel mount
    fw = sc.world(tray_f)
    at = np.array([0.0, -180.0, 0.0])           # on the MiR's cabinet top, beside the arm (MiR frame)
    top = A.P.AMR_TOP if hasattr(A.P, "AMR_TOP") else 800.0
    g_st = "p_steel"
    parts = SP.steel_mount("seated")
    for nm, (mesh, col, spec) in parts.items():
        sc.add(f"{g_st}/{nm}", mesh, col, f"{g_st}_{nm}", specular=spec)
        sc.parent[f"{g_st}_{nm}"] = g_st
    sc.parent[g_st] = f"{u.name}_cab"
    sc.gmat[g_st] = T((ST_AT[0], ST_AT[1], A.P.AMR_TOP - 20.0 + 10.0))
    sc.gmat[f"{g_st}_slice"] = T((0, 0, 60.0))
    sc.gmat[f"{g_st}_screw"] = T((40.0, 0, 0))
    pw = sc.world(g_st)[:3, 3]
    cam_st = cam_at(pw + (0, 0, 15), (260, -330, 260))
    sc.step("Steel mount", "The faced slice into the steel mount, on the MiR's cabinet: a 1.5 in puck of 416 stainless "
            "(magnetic, free-machining) with a 10.1 mm pocket.", 2.2, cam_to=cam_st, hold=0.2)
    sc.step("Steel mount", "It seats on the pocket's steel floor, metal on metal, 0.1 mm proud.", 1.4,
            lambda e: sc.gmat.__setitem__(f"{g_st}_slice", T((0, 0, 60.0 * (1 - e)))), hold=0.2)
    sc.step("Steel mount", "An M3 set screw from the side holds it; grinding takes the slice and the puck's top flush "
            "together.", 1.4, lambda e: sc.gmat.__setitem__(f"{g_st}_screw", T((40.0 * (1 - e), 0, 0))), hold=0.6)
    status(sc, Slice="in the steel mount")

    # ------------------------------------------------------------------ 4. the coupon hot-mounted in the MX400
    L.fetch("F", "Mount", "Tray F comes to Shuttle 1's opening: the LECO MX400 press, the PX500 and its disc magazine.",
            fast=0.45, cam=A.CAM_LAB_OPEN if hasattr(A, "CAM_LAB_OPEN") else None, hold=0.3)
    pw_ = sc.world(f"{press.prefix}body")
    g = RP.mx_geometry()
    mold = (pw_ @ np.r_[g["mx"], g["my"], g["top"], 1.0])[:3]
    cam_mx = cam_at(mold, (380, -820, 520), (0, 0, -60))
    pr = press.inst.actions
    seq = [(1, 1.4, "Hot mounting, as in the lab's own MX400 video: the closure swings off the 1.5 in mold."),
           (2, 1.2, "Ram up, its face flush with the top."),
           (3, 1.6, "The coupon goes on the ram face down: the face to be polished."),
           (4, 1.2, "Ram down, into the mold."),
           (5, 1.6, "Conductive phenolic poured in: carbon-filled, the SEM's path to ground."),
           (6, 1.8, "The stopper on top, green end up, as the press's label says; the closure swung back."),
           (7, 3.0, "Heating under pressure at the lab's settings on the screen: 300, 4.2, 100, 10:00 (300 F is "
                    "149 C, 4.2 thousand psi is 29 MPa: our reading of the units)."),
           (8, 1.6, "Cooling, then Complete."),
           (9, 2.2, "Closure off, stopper out: the ram pushes the mount up out of the mold.")]
    for k, (i, sec, cap_) in enumerate(seq):
        sc.step("Mount", cap_, sec, press.move(pr[i][2]), cam_to=cam_mx if k == 0 else None, hold=0.25)
    status(sc, Coupon="hot-mounted, 1.5 in conductive phenolic")

    # ------------------------------------------------------------------ 5. ground and polished on the PX500
    pw2 = sc.world(f"{pol.prefix}body")
    plat = (pw2 @ np.r_[G["bx"], G["by"], G["disc_z"], 1.0])[:3]
    mw = sc.world(f"{mag.prefix}body")
    mpos = mw[:3, 3]
    mid = (plat + mpos) / 2
    cam_pol = cam_at(mid + (0, -200, 300), (300, -2600, 1300))
    sc.step("Polish", "Grinding and polishing on the PX500. Why whole discs: changing a SiC paper means prying off its "
            "retaining ring, peeling the paper, laying a new one flat and pressing the ring back on. No robot has been "
            "shown doing that.", 2.4, cam_to=cam_pol, hold=1.6)
    sc.step("Polish", "The documented automatic route changes whole pre-loaded discs (BAM's RASI cell: a QATM QPOL 250 "
            "Bot with 16). So each steel disc here carries its own paper or cloth and its own ring, the magnetic platen "
            "holds it, and the arm moves it by the handle on the ring.", 1.0, hold=3.4)
    up_ = -RP.LIFT / (pol.inst.joints["head"].vec[2] * -1.0)
    hide_props(sc, press, ("specimen", "mount"))
    for n in [n for n in sc.actors if sc.group_of[n].startswith(g_st)]:
        sc.alpha[n] = 0.0
    sc.step("Polish", "The two mounts go in the PX500's 6-position holder, faces down; the head lifts clear for a disc "
            "change (our extra lift).", 1.2, pol.move({"head": (0.0, up_)}), hold=0.2)
    pre_back = 140.0

    def handle_world(group):
        return sc.world(group) @ RP.handle_tcp()

    def shift(M, d):
        M2 = M.copy()
        M2[:3, 3] = M2[:3, 3] + np.asarray(d, float)
        return M2
    on_platen = f"{pol.prefix}platen"
    out_pol = 470.0                              # pulled out of the PX500 to the front, clear of the furnace
    out_mag = 360.0
    lift_pol = 62.0

    def to_platen(kind, f=1.0, cap_=""):
        g_ = discs[kind]
        Hh = handle_world(g_)
        sc.step("Polish", cap_, 1.6 * f, rb.joint_to(Tw=shift(Hh, (0, -pre_back, 0))), hold=0.0)
        sc.step("Polish", cap_, 0.7 * f, rb.line_to(Hh), hold=0.0)
        sc.step("Polish", cap_, 0.4 * f, rb.grip_to(RP.GRIP_HANDLE), hold=0.0)
        rb.grasp(g_)
        sc.step("Polish", cap_, 0.4 * f, rb.line_to(shift(Hh, (0, 0, 8))), hold=0.0)
        sc.step("Polish", cap_, 1.0 * f, rb.line_to(shift(Hh, (0, -out_mag, 8))), hold=0.0)
        # to the front of the platen, at the lifted height
        Hp = sc.world(on_platen) @ np.linalg.inv(sc.world(on_platen)) @ T(plat) @ RP.handle_tcp()
        a = shift(Hp, (0, -out_pol, lift_pol))
        sc.step("Polish", cap_, 2.0 * f, rb.line_to(a), hold=0.0)
        sc.step("Polish", cap_, 1.2 * f, rb.line_to(shift(Hp, (0, 0, lift_pol))), hold=0.0)
        sc.step("Polish", cap_, 0.6 * f, rb.line_to(Hp), hold=0.0)
        sc.step("Polish", cap_, 0.4 * f, rb.grip_to(0.0), hold=0.0)
        rb.release(on_platen)
        sc.step("Polish", cap_, 0.6 * f, rb.line_to(shift(Hp, (0, -pre_back, 0))), hold=0.0)

    def to_magazine(kind, f=1.0, cap_=""):
        g_ = discs[kind]
        Hh = handle_world(g_)
        i = RP.GRITS.index(kind)
        Hm = mw @ T(RP.disc_home(i)[:3, 3] - m_off) @ RP.handle_tcp()
        sc.step("Polish", cap_, 1.2 * f, rb.joint_to(Tw=shift(Hh, (0, -pre_back, 0))), hold=0.0)
        sc.step("Polish", cap_, 0.6 * f, rb.line_to(Hh), hold=0.0)
        sc.step("Polish", cap_, 0.4 * f, rb.grip_to(RP.GRIP_HANDLE), hold=0.0)
        rb.grasp(g_)
        sc.step("Polish", cap_, 0.6 * f, rb.line_to(shift(Hh, (0, 0, lift_pol))), hold=0.0)
        sc.step("Polish", cap_, 1.2 * f, rb.line_to(shift(Hh, (0, -out_pol, lift_pol))), hold=0.0)
        sc.step("Polish", cap_, 2.0 * f, rb.line_to(shift(Hm, (0, -out_mag, 8))), hold=0.0)
        sc.step("Polish", cap_, 1.0 * f, rb.line_to(shift(Hm, (0, 0, 8))), hold=0.0)
        sc.step("Polish", cap_, 0.4 * f, rb.line_to(Hm), hold=0.0)
        sc.step("Polish", cap_, 0.4 * f, rb.grip_to(0.0), hold=0.0)
        rb.release(f"{mag.prefix}body")
        sc.step("Polish", cap_, 0.6 * f, rb.line_to(shift(Hm, (0, -pre_back, 0))), hold=0.0)

    plat_v = [0.0]

    def grind(cap_, secs_, cloth=False, f=1.0):
        a, b = plat_v[0], plat_v[0] + 1.0
        tg = {"head": (up_, 1.0)}
        sc.step("Polish", cap_, 0.8 * f, pol.move(tg), hold=0.0)
        ws = {"powder": (0.0, 1.0)} if cloth else {"water": (0.0, 1.0)}
        sc.step("Polish", cap_, secs_ * f, pol.move({"platen": (a, b), "holder": (a, b), **ws}), hold=0.0)
        we = {"powder": (1.0, 0.0)} if cloth else {"water": (1.0, 0.0)}
        sc.step("Polish", cap_, 0.8 * f, pol.move({"head": (1.0, up_), **we}), hold=0.1)
        plat_v[0] = b

    to_platen("320", 1.0, "The arm takes the 320-grit disc from the bottom shelf of the magazine and lays it on the "
                          "magnetic platen.")
    status(sc, Disc="320 SiC")
    grind("320 grit, water on: the lab's SOP, head 35 rpm, force 30, platen 150 rpm, 30 s.", 3.2)
    for prev, nxt in (("320", "400"), ("400", "600"), ("600", "800"), ("800", "1200"), ("1200", "cloth")):
        f = 0.75 if prev == "320" else FAST
        cap_ = (f"Change: the {prev} disc back to its shelf, paper, ring and all; the {nxt} out and onto the platen."
                if prev == "320" else f"{prev} back, {nxt} on (a time-lapse).")
        to_magazine(prev, f, cap_)
        to_platen(nxt, f, cap_)
        status(sc, Disc=f"{nxt} SiC" if nxt != "cloth" else "cloth, 1 um alumina")
        if nxt != "cloth":
            grind(f"{nxt} grit, 30 s, the same settings.", 2.0, f=0.8 if nxt == "400" else 0.6)
    grind("The final polish: 1 um alumina from the PX500's dispenser onto the cloth, force 3-5, 150 rpm, 3 min.", 3.6,
          cloth=True)
    status(sc, Coupon="polished, in its hot mount", Slice="polished flush, in the steel mount")
    sc.step("Polish", "Head up. A person re-papers the five SiC discs between batches, off the machine: one fresh "
            "paper per grit per holder load (Buehler: change SiC paper after each holder).", 1.0,
            rb.joint_to(q1=np.radians(A.PARK_DEG)), hold=2.6)

    # ------------------------------------------------------------------ 6. rinse, dry, store; what is hard
    hot = SP.hot_mount("polished")
    stl = SP.steel_mount("polished")
    for nm, (mesh, col, spec) in hot.items():
        sc.add(f"p_hot/{nm}", mesh, col, "p_hot", specular=spec)
    sc.parent["p_hot"] = f"{u.name}_cab"
    sc.gmat["p_hot"] = T((HOT_AT[0], HOT_AT[1], A.P.AMR_TOP - 10.0))
    for nm, (mesh, col, spec) in stl.items():
        sc.add(f"p_stl/{nm}", mesh, col, "p_stl", specular=spec)
    sc.parent["p_stl"] = f"{u.name}_cab"
    sc.gmat["p_stl"] = T((ST_AT[0], ST_AT[1], A.P.AMR_TOP - 10.0))
    hw = sc.world("p_hot")[:3, 3]
    sc.step("Done", "Rinsed, dipped in ethanol and dried (the SOP, part 3), the two mounts ride the MiR's cabinet to "
            "the sample store on tray J, then to chapter 7.", 2.6, cam_to=cam_at(hw + (-30, -30, 20), (330, -420, 300)),
            hold=2.2, still=True)
    sc.step("Done", "Where automating this is hard: re-papering discs, judging the polish (by eye in the SOP), and "
            "loading the holder. Buehler's AutoMet heads automate force, speed and time and its Burst module doses "
            "suspension, but a person changes the papers.", 1.0, hold=4.2)
    sc.step("Done", "UES's Robo-Met.3D (now sold by AV) moves one mounted specimen between polishing, ultrasonic "
            "cleaning and an inverted microscope, for serial sectioning; it does not cut or mount. Sectioning and "
            "mounting are what this chapter adds.", 1.0, cam_to=CAM_LAB, hold=4.2)
    return sc.save()


if __name__ == "__main__":
    print(movie())
