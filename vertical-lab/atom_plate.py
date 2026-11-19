"""The atomizing plate swapped by the arm, every substep (PR #353 for #303): notes/atom_plate.md.

DAL's checklist (digital-alloy-lab PR 253, "Configuring the Ultrasonic Tower" steps 8-18 and "Powder Collection and
Cleaning" step 6) and the detailed SOP (PR 178, "Ultrasonic stack" steps 8-11, the plate table, "Cleaning and
maintenance") give the order. MiR 2's UR10e + 2F-85 (+ D405) does every step at the door; MiR 1 waits at the right.

    xvfb-run -a python3 atom_plate.py                 # out/atom_plate.gif, out/mp4/atom_plate.mp4, .json, _still.png
    ARM_AUDIT=1 xvfb-run -a python3 atom_plate.py     # out/collisions/atom_plate.json
    PREVIEW=1 xvfb-run -a python3 atom_plate.py       # /tmp/preview_atom_plate.png
"""
from __future__ import annotations

import math
import os

import numpy as np
import pyvista as pv
from PIL import ImageDraw

import atom_base as AB
import atom_plate_tools as PT
import ur_arm
from scene import R, T, font

M = AB.M
g = AB.g
NAME = "atom_plate"
UPTO = int(os.environ.get("PLATE_UPTO", "99"))      # development: stop after this many chapters
SPEED = 0.74                                         # every sub-step's seconds scaled by this (Clip.step)
RNG = np.random.default_rng(353)

OLD = dict(id="CF-AL-03", alloy="Al-10Si", mat="CF, bare", uses=4, cond="intact; Al film, lifts off", slot=1)
NEW = dict(id="WCF-CU-07", alloy="NAB (Cu)", mat="CF, W-coated", uses=0, slot=2)
# booster 1:1.5 with CF (DAL 253 table), so the scan reads ~40.1 kHz


def inv(Mx):
    Mi = np.eye(4)
    Mi[:3, :3] = Mx[:3, :3].T
    Mi[:3, 3] = -Mx[:3, :3].T @ Mx[:3, 3]
    return Mi


def frame(p, z, x) -> np.ndarray:
    """A 4x4 at p with the given z, and x made square to it."""
    z = np.asarray(z, float)
    z = z / np.linalg.norm(z)
    x = np.asarray(x, float)
    x = x - z * (x @ z)
    x = x / np.linalg.norm(x)
    F = np.eye(4)
    F[:3, 0], F[:3, 1], F[:3, 2], F[:3, 3] = x, np.cross(z, x), z, p
    return F


def local_tcp(p, z, x) -> np.ndarray:
    return frame(np.asarray(p, float), z, x)


def Dm(v):
    return M.joint_matrix("door", v)


def track(rb, pose_fn, n=48, also=None, max_jump=18.0):
    """The TCP through pose_fn(u), u 0..1, IK solved now (nearest the last solution); also(u) runs alongside."""
    q, path = rb.q.copy(), []
    for u in np.linspace(0.0, 1.0, n + 1):
        if also is not None:
            also(u)
        q = rb.solve(pose_fn(u), q)
        path.append(q)
    if also is not None:
        also(0.0)
    path = np.array(path)
    jump = np.degrees(np.abs(np.diff(path, axis=0)).max())
    if jump > max_jump:
        raise ValueError(f"track: {jump:.0f} deg in one step at {rb.sc.label}")

    def up(u):
        if also is not None:
            also(u)
        f = u * n
        i = min(int(f), n - 1)
        rb.set(path[i] + (path[i + 1] - path[i]) * (f - i))
    up.path = path
    return up


def replay(rb, path, also=None):
    """update(u): the arm through a stored joint path (e.g. a track's, reversed)."""
    path = np.asarray(path, float)
    n = len(path) - 1

    def up(u):
        if also is not None:
            also(u)
        f = u * n
        i = min(int(f), n - 1)
        rb.set(path[i] + (path[i + 1] - path[i]) * (f - i))
    return up


def spin(rb, base_fn, deg_fn, n=48, also=None):
    """A grasp turned about the tool's own axis: the TCP through base_fn(u) @ Rz(deg_fn(u)). Wrist 3 turns about the
    flange's z, which is the tool's axis, so the turn goes on q6 alone (an IK branch can't flip under it) and the rest
    of the arm follows base_fn(u) (the thread's advance) by IK."""
    q, path = rb.q.copy(), []
    q6_0 = q[5]
    for u in np.linspace(0.0, 1.0, n + 1):
        Tb = base_fn(u) @ R((0, 0, 1), deg_fn(0.0))
        q = rb.solve(Tb, q)
        qq = q.copy()
        qq[5] = q[5] + math.radians(deg_fn(u) - deg_fn(0.0))
        path.append(qq)
    path = np.array(path)
    # check: the last pose is where it should be
    Wr = rb.sc.world(rb.root)
    Tend = Wr @ ur_arm.fk(rb.model, path[-1])["tool0"] @ T((0, 0, ur_arm.TCP_MM))
    want = base_fn(1.0) @ R((0, 0, 1), deg_fn(1.0))
    if np.abs(Tend - want).max() > 0.5:
        raise ValueError(f"spin: end pose off by {np.abs(Tend - want).max():.2f} at {rb.sc.label}")

    def up(u):
        if also is not None:
            also(u)
        f = u * n
        i = min(int(f), n - 1)
        rb.set(path[i] + (path[i + 1] - path[i]) * (f - i))
    return up


def branch_for(rb, pre, grasp, path_fn, close, also=None, n=10, skip=(), back=None, pre_close=0.0):
    """The IK solution at `grasp` from which the arm can follow path_fn(u) (u 0..1; also(u) moves the scene with it)
    touching nothing but actors whose names contain a string in `skip`, and whose approach pose `pre` is clear too:
    (q at the grasp, q at pre), nearest first; (None, None) if none. After alloy_atomize.arc_branch."""
    import collide
    if collide is None:
        return None, None
    chk = rb.checker()
    Tb = inv(rb.sc.world(rb.root)) @ grasp
    cands = collide.ik_all(rb.model, Tb, rb.q) or []

    def bad(q, c):
        return any(not any(k in h[2] for k in skip) for h in chk.collisions(q, c, chk.snapshot()))
    best = (1e9, None, None)
    for q in cands:
        ok, qq, nbad = True, q.copy(), 0
        for u in np.linspace(0.0, 1.0, n):
            if also is not None:
                also(u)
            try:
                q_new = rb.solve(path_fn(u), qq)
            except ValueError:
                ok = False
                break
            if np.abs(q_new - qq).max() > math.radians(25):
                ok = False
                break
            qq = q_new
            if bad(qq, close):
                nbad += 1
        if also is not None:
            also(0.0)
        if not ok:
            continue
        try:
            q_pre = rb.solve(pre, q)
        except ValueError:
            continue
        if bad(q_pre, pre_close):
            nbad += 3
        if nbad:
            if nbad < best[0]:
                best = (nbad, q, q_pre)
            continue
        if back is not None:
            try:
                q_back = rb.solve(back, qq)
            except ValueError:
                continue
            if bad(q_back, 0.0):
                continue
        return q, q_pre
    print(f"warning: {rb.sc.name} {rb.sc.label}: no clear IK branch for the move (best: {best[0]} bad samples)",
          flush=True)
    return best[1], best[2]


def approach(c, rb, label, caption, pre, grasp, path_fn, close, also=None, skip=(), secs=(1.6, 0.6), back=None,
             pre_close=None, **kw):
    """Joint move to the pre-grasp in a branch that suits the move that follows, then the straight approach. The
    fingers open only pre_close's width on the way (default: 12 mm over the part)."""
    pc = max(0.0, close - 0.16) if pre_close is None else pre_close
    rb.set(close=rb.close)
    q, q_pre = branch_for(rb, pre, grasp, path_fn, close, also=also, skip=skip, back=back, pre_close=pc)
    c.step(label, caption, secs[0], both(rb.grip_to(pc), rb.joint_to(q1=q_pre) if q_pre is not None else
                                         rb.joint_to(Tw=pre)), hold=0.0, **kw)
    c.step(label, caption, secs[1], rb.line_to(grasp), hold=0.0)


def seq(*parts):
    """update(u) running parts [(weight, update)] one after another."""
    w = np.array([p[0] for p in parts], float)
    edges = np.r_[0.0, np.cumsum(w) / w.sum()]

    def up(u):
        for k, (_, f) in enumerate(parts):
            a, b = edges[k], edges[k + 1]
            if u >= a or k == 0:
                v = min(max((u - a) / max(b - a, 1e-9), 0.0), 1.0)
                if f is not None and (u >= a):
                    f(v)
    return up


# ------------------------------------------------------------------------------------------------ the scene
class Clip:
    def __init__(self):
        sc, ma, mb = AB.build(NAME, "Vertical cloud lab: swapping the atomizing plate (rePowder, DAL SOP)")
        self.sc, self.ma, self.mb, self.rb = sc, ma, mb, mb.rb
        AB.mir_at(ma, "right")
        AB.mir_at(mb, (-600.0, -1250.0, 0.0))
        ms = AA_meshes()
        # --- my upper sonotrode (flats, Sharpie lines) instead of the model's round one
        sc.show(sc.members(g("upper")), 0.0)
        sc.add("plate upper", PT.put(PT.upper_local(), PT.FS), M.W_ALLOY, g("upper"), specular=0.6)
        sc.add("plate upper lines", PT.put(PT.sharpie_local(), PT.FS), PT.SHARPIE, g("upper"))
        # --- the old plate gets its tag
        sc.add("plate old tag", PT.put(PT.plate_tag(), PT.FS), PT.LABEL, g("plate"))
        # --- my door bolts and lugs instead of the model's clamps
        for k in range(2):
            sc.show(sc.members(g(f"clamp{k}")), 0.0)
            sc.show([n for n in (f"clamp_body{k}",) if n in sc.actors], 0.0)     # the model's bracket: ours replaces it
            rod, knob, bracket, _ = PT.bolt_meshes(k)
            sc.add(f"plate bolt bracket {k}", bracket, M.STEEL_DK, "rp")
            sc.add(f"plate bolt rod {k}", rod, (0.70, 0.71, 0.73), f"bolt{k}", specular=0.5)
            sc.add(f"plate bolt knob {k}", knob, PT.BLACK, f"knob{k}")
            sc.parent[f"bolt{k}"] = "rp"
            sc.parent[f"knob{k}"] = f"bolt{k}"
            sc.gmat[f"bolt{k}"] = np.eye(4)
            sc.gmat[f"knob{k}"] = np.eye(4)
        sc.add("plate door lugs", PT.lug_meshes(), M.STEEL, g("door"))
        # --- fixtures on MiR 2's cabinet top (ours)
        mg = mb.g
        for name, (mesh, col) in PT.rack_meshes().items():
            sc.add(f"{mg}/{name}", mesh, col, mg)
        for name, (mesh, col) in PT.tray_meshes().items():
            sc.add(f"{mg}/{name}", mesh, col, mg)
        sc.add(f"{mg}/tool shelf", PT.shelf_meshes(), (0.72, 0.74, 0.77), mg)
        sc.add(f"{mg}/wrench holder", PT.wrench_holder(), (0.30, 0.32, 0.36), mg)
        sc.add(f"{mg}/gauge holder", PT.gauge_holder(), (0.30, 0.32, 0.36), mg)
        sc.add(f"{mg}/dropper holder", PT.dropper_holder(), (0.30, 0.32, 0.36), mg)
        sc.add(f"{mg}/wipe holder", PT.wipe_holder(), (0.30, 0.32, 0.36), mg)
        # plates standing in the rack: the slots' own plates (the old one's slot is empty, the new one waits)
        pl = PT.plate_local(ms)
        self.pl_local = pl
        for i in range(PT.RACK_SLOTS):
            if i == OLD["slot"] or i == 4:
                continue
            grp = "newplate" if i == NEW["slot"] else f"rackplate{i}"
            col = PT.W_COAT if i in (2, 3) else PT.CF
            sc.add(f"plate rack plate {i}", pl, col, grp, specular=0.3 if i in (2, 3) else 0.1)
            sc.add(f"plate rack tag {i}", PT.plate_tag(), PT.LABEL, grp)
            sc.parent[grp] = mg
            sc.gmat[grp] = PT.plate_in_slot(i)
        # the spare upper sonotrode socket stays empty; the wrench, gauge, dropper and wipe in their holders
        for name, (mesh, col) in PT.wrench_meshes().items():
            sc.add(f"plate wrench {name}", mesh, col, "wrench", specular=0.4)
        for name, (mesh, col) in PT.socket_meshes().items():
            sc.add(f"plate wrench {name}", mesh, col, "socket", specular=0.5)
        sc.parent["wrench"] = mg
        sc.gmat["wrench"] = PT.wrench_in_holder()
        sc.parent["socket"] = "wrench"
        sc.gmat["socket"] = np.eye(4)
        for name, (mesh, col) in PT.gauge_meshes().items():
            sc.add(f"plate {name}", mesh, col, "gauge", specular=0.5)
        sc.parent["gauge"] = mg
        sc.gmat["gauge"] = PT.gauge_in_holder()
        for name, (mesh, col) in PT.dropper_meshes().items():
            sc.add(f"plate {name}", mesh, col, "dropper", specular=0.3)
        sc.parent["dropper"] = mg
        sc.gmat["dropper"] = T((PT.DROP_AT[0], PT.DROP_AT[1], PT.TOP + 4.0))
        for name, (mesh, col) in PT.wipe_meshes().items():
            sc.add(f"plate {name}", mesh, col, "wipe")
        sc.parent["wipe"] = mg
        sc.gmat["wipe"] = T((PT.WIPE_AT[0], PT.WIPE_AT[1], PT.TOP + 4.0))
        # the laser line (the module sits in the sealing rod's place; DAL #164) and the mist
        beam = pv.Cylinder(center=(0, 0, (M.NOZZLE_EXIT_Z + M.IMPACT[2]) / 2), direction=(0, 0, 1), radius=0.6,
                           height=M.NOZZLE_EXIT_Z - M.IMPACT[2], resolution=12).triangulate()
        sc.add("plate laser", beam, (1.0, 0.05, 0.05), "laser", ambient=1.0, diffuse=0.0)
        sc.add("plate laser dot", pv.Sphere(radius=2.2, center=tuple(M.IMPACT)), (1.0, 0.1, 0.1), "laser",
               ambient=1.0, diffuse=0.0)
        sc.parent["laser"] = "rp"
        sc.show(sc.members("laser"), 0.0)
        self.mist_n = 260
        sc.add("plate mist", pv.PolyData(np.zeros((self.mist_n, 3))), (0.30, 0.62, 1.0), "mist", point_size=6,
               render_points_as_spheres=True, ambient=0.7)
        sc.add("plate drop", pv.Sphere(radius=1.6), (0.55, 0.75, 0.98), "drop", specular=0.8)
        sc.parent["mist"] = "rp"
        sc.parent["drop"] = "rp"
        sc.show(["plate mist", "plate drop"], 0.0)
        self.inset = None
        orig = sc.overlay

        def overlay(img, scale, anchors, _orig=orig):
            img = _orig(img, scale, anchors)
            if self.inset is not None:
                self.draw_inset(img, scale)
            return img
        sc.overlay = overlay
        self.door = 0.0
        self.swing = [0.0, 0.0]
        self.turn = [0.0, 0.0]
        self.upper_rot = 0.0       # deg about the axis, + = tightening
        self.upper_out = 0.0       # mm along the axis, out
        self.rows = {}

    # -------------------------------------------------------------------------------- state
    def set_bolt(self, k, swing=None, turn=None):
        if swing is not None:
            self.swing[k] = swing
        if turn is not None:
            self.turn[k] = turn
        Mr, Mk = PT.bolt_matrix(k, self.swing[k], self.turn[k])
        self.sc.gmat[f"bolt{k}"] = Mr
        self.sc.gmat[f"knob{k}"] = Mk

    def set_door(self, v):
        self.door = v
        AB.set_joints(self.sc, door=v)
        # the compressed-air hose to the transducer's cover is flexible: its last two points ride on the door (ours;
        # the model draws it as a fixed line)
        if "rp pipe air" in self.sc.actors:
            r = M.pipe_routes()["air"]
            pts = np.array(r["pts"], float)
            Dv = Dm(v)
            for i in (3, 4):
                pts[i] = (Dv @ np.r_[pts[i], 1.0])[:3]
            pts[2] = pts[2] + (pts[3] - np.array(r["pts"][3], float)) * 0.35
            self.sc.set_mesh("rp pipe air", pv.Spline(pts, 120).tube(radius=r["r"], n_sides=14))

    def upper_local_M(self, rot=None, out=None) -> np.ndarray:
        rot = self.upper_rot if rot is None else rot
        out = self.upper_out if out is None else out
        return T((0, 0, out)) @ R((0, 0, 1), -rot)

    def set_upper(self, rot=None, out=None):
        if rot is not None:
            self.upper_rot = rot
        if out is not None:
            self.upper_out = out
        self.sc.gmat[g("upper")] = PT.FS @ self.upper_local_M() @ PT.FS_INV

    def stack_world(self, v=None) -> np.ndarray:
        """World 4x4 of the stack frame with the door at v (default: as it is)."""
        return AB.WT(Dm(self.door if v is None else v) @ PT.FS)

    def status(self, **kv):
        self.rows.update(kv)
        AB.caption_rows(self.sc, **self.rows)

    # -------------------------------------------------------------------------------- the inset (HMI scan)
    def draw_inset(self, img, scale):
        kind, a = self.inset
        if a <= 0.02:
            return
        W, H = img.size
        s = max(scale, 0.8)
        d = ImageDraw.Draw(img, "RGBA")
        w, h = 330 * s, 190 * s
        x0, y0 = W - w - 14 * s, 50 * s
        al = int(235 * a)
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 8 * s, fill=(12, 16, 24, al), outline=(90, 100, 120, al))
        d.text((x0 + 10 * s, y0 + 6 * s), "HMI: frequency scan, plate on", font=font(14 * s, bold=True),
               fill=(230, 235, 240, al))
        px0, px1 = x0 + 34 * s, x0 + w - 12 * s
        py0, py1 = y0 + 32 * s, y0 + h - 30 * s
        d.line([(px0, py1), (px1, py1)], fill=(150, 160, 175, al), width=max(1, int(s)))
        d.line([(px0, py0), (px0, py1)], fill=(150, 160, 175, al), width=max(1, int(s)))
        f = np.linspace(39.0, 41.0, 160)
        prog = min(1.0, a * 1.0) if kind == "scan" else 1.0
        amp = np.exp(-0.5 * ((f - 40.10) / 0.09) ** 2) * 0.92 + 0.04 + 0.01 * np.sin(f * 37.0)
        n = max(2, int(len(f) * self.scan_u))
        pts = [(px0 + (fi - 39.0) / 2.0 * (px1 - px0), py1 - ai * (py1 - py0)) for fi, ai in zip(f[:n], amp[:n])]
        d.line(pts, fill=(90, 200, 255, al), width=max(2, int(2 * s)))
        for k, fk in enumerate((39.0, 39.5, 40.0, 40.5, 41.0)):
            xk = px0 + (fk - 39.0) / 2.0 * (px1 - px0)
            d.text((xk - 12 * s, py1 + 4 * s), f"{fk:.1f}", font=font(11 * s), fill=(170, 178, 190, al))
        d.text((px1 - 34 * s, py1 + 14 * s), "kHz", font=font(11 * s), fill=(170, 178, 190, al))
        for fk in (39.5, 40.5):                                   # the SOP's band
            xk = px0 + (fk - 39.0) / 2.0 * (px1 - px0)
            d.line([(xk, py0), (xk, py1)], fill=(120, 220, 120, int(al * 0.6)), width=max(1, int(s)))
        if self.scan_u > 0.98:
            xk = px0 + (40.10 - 39.0) / 2.0 * (px1 - px0)
            d.text((px0 + 6 * s, py0 + 2 * s), "one peak, 40.10 kHz", font=font(12 * s, bold=True),
                   fill=(120, 230, 140, al))

    # -------------------------------------------------------------------------------- steps
    def step(self, label, caption, seconds, update=None, hold=1.2, **k):
        """A sub-step at SPEED: the arm's transfers run at about 1.3x the first cut (still under UR's 1 m/s TCP
        default for these distances); holds shorten likewise but keep at least 0.4 s where one was asked for."""
        s = max(0.2, seconds * SPEED)
        h = 0.0 if hold <= 0 else max(0.4, hold * SPEED)
        if os.environ.get("PLATE_TRACE"):
            print(f"TRACE frame {self.sc.n} {label} {caption[:70]}", flush=True)
        self.sc.step(label, caption, s, update, hold=h, **k)


def AA_meshes():
    return M.meshes()


# ------------------------------------------------------------------------------------------------ grasps
def grasp_plate_local() -> np.ndarray:
    """TCP in a plate's own frame: 18 mm in from its free end, the pads on its faces, approaching along +across."""
    return local_tcp((PT.PLATE_L - PT.HOLE_E - 18.0, 0.0, PT.PLATE_T / 2), (0, 1, 0), (0, 0, 1))


def grasp_upper_local(z=25.0) -> np.ndarray:
    """TCP in the upper sonotrode's frame (its plate face at z = PLATE_T): on the axis z mm up, coaxial."""
    return local_tcp((0.0, 0.0, z), (0, 0, -1), (0, 1, 0))


def grasp_wrench_local() -> np.ndarray:
    """The handle, from behind the spine; the fingers close across it, the wrist camera on the far side from the
    arm's forearm when the wrench is on the stack."""
    return local_tcp(PT.WR_GRASP, (0, 1, 0), (-1, 0, 0))


def knob_turn(c, rb, k, loosen, caption_cam, close, L):
    """A door bolt's star knob turned one full turn on its axis, from the left, in two grasps of 180 deg, the wrist kept
    within 90 deg either side of where the wrist camera faces the chamber (away from the arm's own forearm)."""
    sc = c.sc
    sgn = -1.0 if loosen else 1.0
    t0 = 0.0 if loosen else 1.0
    adv = PT.KNOB_PITCH * PT.KNOB_TURNS / 2           # mm along the rod per half turn (out when loosening)
    # the pads on the lobes' outer part: the 2F-85's fingertips reach 18 mm past the grasp point, so 13 mm further
    # out they stop 2 mm short of the lug and of the door's front edge as the wrist turns
    G0 = AB.WT(local_tcp(PT.knob_centre(k, c.swing[k], t0), (1, 0, 0), (0, 0, 1))) @ T((0, 0, -13.0))
    Gs = G0 @ R((0, 0, 1), -90.0 * sgn)               # the first grasp's turn: 90 deg back from centre
    cap1 = ("The arm takes a door bolt's star knob from the left, on its axis ..." if loosen else
            "... and each knob tightened, one turn back on.")
    approach(c, rb, L, cap1, Gs @ T((0, 0, -70)), Gs,
             lambda u: Gs @ T((0, 0, sgn * adv * u)) @ R((0, 0, 1), 180.0 * sgn * u), close,
             skip=("plate bolt",), secs=(1.4, 0.6), cam_to=caption_cam if loosen else None)
    cap2 = (f"One turn loosens it, {PT.KNOB_PITCH * PT.KNOB_TURNS:.2f} mm back off the door's lug (M12 assumed), in "
            "two grasps." if loosen else cap1)
    G = Gs
    for half in range(2):
        c.step(L, cap2, 0.3, rb.grip_to(close), hold=0.0)
        rb.grasp(f"knob{k}")
        c.step(L, cap2, 0.7, spin(rb, lambda u, G=G: G @ T((0, 0, sgn * adv * u)), lambda u: 180.0 * sgn * u, n=24),
               hold=0.0)
        rb.release(f"bolt{k}")
        c.turn[k] = 0.5 * (half + 1) if loosen else 1.0 - 0.5 * (half + 1)
        sc.gmat[f"knob{k}"] = PT.bolt_matrix(k, c.swing[k], c.turn[k])[1]
        Gend = G @ T((0, 0, sgn * adv)) @ R((0, 0, 1), 180.0 * sgn)
        if half == 0:
            c.step(L, cap2, 0.45, both(rb.grip_to(ur_arm.close_for(46.0)),
                                       spin(rb, lambda u, Ge=Gend: Ge, lambda u: -180.0 * sgn * u, n=24)), hold=0.0)
            G = Gend @ R((0, 0, 1), -180.0 * sgn)
        else:
            c.step(L, "Let go, back off.", 0.5, both(rb.grip_to(0.0), rb.line_to(Gend @ T((0, 0, -60)))), hold=0.0)


def main():
    c = Clip()
    sc, rb, mb = c.sc, c.rb, c.mb
    close_upper = ur_arm.close_for(2 * PT.UPPER_R + 0.2)
    close_plate = ur_arm.close_for(PT.PLATE_T + 0.2)
    close_knob = ur_arm.close_for(34.0)
    close_lug = ur_arm.close_for(22.2)
    close_bar = ur_arm.close_for(16.2)
    close_gauge = ur_arm.close_for(PT.GAUGE_T + 0.2)
    close_bottle = ur_arm.close_for(32.2)
    close_stem = ur_arm.close_for(12.2)
    OPEN = ur_arm.close_for(46.0)      # let go by opening to 46 mm, not the full 85: the neighbours stay clear
    n_ch = [0]

    def chapter():
        n_ch[0] += 1
        return n_ch[0] <= UPTO

    def L(i):
        return f"{i}/12"

    cam_far = AB.cam((-150, -2500, 1850), (-380, -450, 900))
    cam_bolts = AB.cam((330, -1180, 1260), (-190, -190, 935))
    cam_open = AB.cam((120, -1450, 1550), (-320, -20, 930))
    cam_stack = AB.cam((-120, -760, 1170), (-290, 25, 905))
    cam_deck = AB.cam((-120, -1750, 1500), (-600, -860, 820))
    sc.cam = list(cam_far)

    def mirw(p):
        return mb.world(np.asarray(p, float))

    def at_mir(Mloc):
        return mb.sc.world(mb.g) @ Mloc

    c.status(Plate=f"{OLD['id']} ({OLD['alloy']})", Uses=str(OLD["uses"]), Door="shut, 2 bolts",
             Torque="-", Scan="-")
    c.set_upper(0.0, 0.0)
    for k in range(2):
        c.set_bolt(k, 0.0, 0.0)

    # ------------------------------------------------------------------ 1: MiR 2 to the door
    if chapter():
        up, secs = AB.mir_drive(mb, (-600.0, -720.0, 0.0))
        c.step(L(1), "MiR 2 drives to the chamber's door. The chamber is vented to the room and cold (DAL 253: "
               "never open above atmosphere; the cone and chamber are water-cooled).", max(secs, 3.0), up, hold=0.6,
               cam_to=cam_far)

    # ------------------------------------------------------------------ 2: the bolts
    if chapter():
        for k in (1, 0):
            knob_turn(c, rb, k, loosen=True, caption_cam=cam_bolts, close=close_knob, L=L(2))
            # swing: grip the knob from the front, the pads on its top and bottom lobes
            kc1 = PT.knob_centre(k, 0.0, 1.0) + np.array([0.0, 0.0, 1.25])
            G1 = AB.WT(local_tcp(kc1, (0, 1, 0), (0, 0, 1)))
            pin = AB.W(PT.bolt_geom(k)[0])
            deg = PT.SWING_DEG[k]
            approach(c, rb, L(2), "From the front, it swings the bolt up out of the lug's slot ...",
                     G1 @ T((0, 0, -60)), G1, lambda u, G1=G1, pin=pin, deg=deg: R((0, 1, 0), deg * u, pin) @ G1,
                     close_knob, skip=("plate bolt", "plate door lugs"), secs=(1.2, 0.6),
                     back=R((0, 1, 0), deg, pin) @ G1 @ T((0, 0, -60)))
            c.step(L(2), "From the front, it swings the bolt up out of the lug's slot ...", 0.3,
                   rb.grip_to(close_knob), hold=0.0)
            rb.grasp(f"bolt{k}")
            c.step(L(2), ("... and over the top, along the face (T5 27:16)." if k == 1 else
                          "... the top one only 90 deg up: the viewport hood is in the way of 180 (ours)."),
                   1.6 if k == 1 else 1.2,
                   track(rb, lambda u, G1=G1, pin=pin, deg=deg: R((0, 1, 0), deg * u, pin) @ G1, n=60), hold=0.0)
            rb.release("rp")
            c.swing[k] = 1.0
            c.set_bolt(k)
            c.step(L(2), "Bolt clear.", 0.5, both(rb.grip_to(OPEN),
                                                    rb.line_to(R((0, 1, 0), deg, pin) @ G1 @ T((0, 0, -60)))),
                   hold=0.0)
        c.status(Door="unbolted")

    # ------------------------------------------------------------------ 3: open the door
    if chapter():
        # the lower lug's web, model frame (door shut): the pads on its top and bottom faces (22 mm apart), 21 mm in
        # front of the door so the fingertips (18 mm past the grasp point) stay clear of its edge, and clear of the
        # lower bolt's bracket to the right
        lug = np.array([PT.LUG_X[0] + 4.0, -139.0, PT.BOLT_Z[1]])
        Gl = AB.WT(local_tcp(lug, (0, 1, 0), (0, 0, 1)))

        def door_pose(u, Gl=Gl):
            return AB.WT(Dm(u)) @ inv(AB.WT(np.eye(4))) @ Gl
        approach(c, rb, L(3), "The arm takes the door's lower lug ...", Gl @ T((0, 0, -70)), Gl, door_pose, close_lug,
                 also=c.set_door, skip=("door",), secs=(1.4, 0.6), back=door_pose(1.0) @ T((0, 0, -70)),
                 cam_to=cam_open)
        c.step(L(3), "The arm takes the door's lower lug ...", 0.3, rb.grip_to(close_lug), hold=0.0)
        opening = track(rb, door_pose, n=80, also=c.set_door)
        c.door_path = opening.path
        c.step(L(3), "... and swings it open 100 deg on its back hinge. The stack rides on the door, so the plate comes "
               "out with it (DAL 178 step 8).", 3.2, opening, hold=0.2)
        c.step(L(3), "Open.", 0.6, both(rb.grip_to(OPEN), rb.line_to(door_pose(1.0) @ T((0, 0, -70)))), hold=0.0)
        c.status(Door="open 100 deg")

    # ------------------------------------------------------------------ 4: the plate's condition
    if chapter():
        Fs = c.stack_world()
        mid = (Fs @ np.r_[55.0, 0.0, PT.PLATE_T, 1.0])[:3]
        eye = (Fs @ np.r_[55.0, -110.0, 170.0, 1.0])[:3]
        look = frame(eye, mid - eye, Fs[:3, 0])
        c.step(L(4), "The wrist camera (D405, 7-50 cm) looks at the plate: no crack, no dark spot at an edge, metal "
               "that lifts off. A plate that fails comes off (DAL 253 Cleaning step 6).", 2.0,
               rb.joint_to(Tw=look), hold=1.2, cam_to=cam_stack,
               labels=[(f"plate {OLD['id']}\n{OLD['alloy']}, {OLD['mat']}", tuple((Fs @ np.r_[60, 0, 2.5, 1])[:3]),
                        (0.78, 0.30))])
        c.status(Plate=f"{OLD['id']}: {OLD['cond']}")

    # ------------------------------------------------------------------ 5: break the upper sonotrode loose
    if chapter():
        Gw = grasp_wrench_local()
        Wh = at_mir(PT.wrench_in_holder())
        c.step(L(5), "It takes the stack wrench from its holder (ours: two 17 mm heads; the reaction closes inside "
               "the tool).", 1.6, rb.joint_to(Tw=Wh @ Gw @ T((0, 0, -80))), hold=0.0, cam_to=cam_deck)
        c.step(L(5), "It takes the stack wrench from its holder (ours: two 17 mm heads; the reaction closes inside "
               "the tool).", 0.6, rb.line_to(Wh @ Gw), hold=0.0)
        c.step(L(5), "It takes the stack wrench from its holder.", 0.3, rb.grip_to(close_bar), hold=0.0)
        rb.grasp("wrench")
        c.step(L(5), "Lift.", 0.6, rb.line_to(T((0, 0, 60)) @ Wh @ Gw), hold=0.0)
        Fs = c.stack_world()
        eng = Fs @ Gw
        pre = Fs @ T((0, -60, 0)) @ Gw
        c.step(L(5), "To the stack: the fixed head goes onto the lower sonotrode's flats, behind the plate ...", 2.2,
               rb.joint_to(Tw=pre), hold=0.0, cam_to=cam_stack)
        c.step(L(5), "To the stack: the fixed head goes onto the lower sonotrode's flats, behind the plate ...", 1.0,
               rb.line_to(eng), hold=0.0)

        def sock(u, turn=0.0):
            sc.gmat["socket"] = T((0, 0, -PT.SOCKET_STROKE * u)) @ R((0, 0, 1), turn)
        c.step(L(5), "... and the drive's slotted socket slides 15 mm down the axis onto the upper sonotrode's end "
               "flats.", 0.9, lambda u: sock(u), hold=0.0)

        def loosen(u):
            a = 32.0 * u
            sock(1.0, a)
            c.set_upper(rot=-a)
            tq = 58.0 * math.sin(math.pi * min(u / 0.35, 1.0) / 2) if u < 0.35 else 58.0 * max(0.0, 1 - (u - 0.35) * 4) + 0.6
            c.status(Torque=f"{tq:5.1f} N m (loosening)")
        c.step(L(5), "It breaks the joint loose (about 58 N m, ours: a little over the 50 it was set to). The arm "
               "feels only the tool's weight.", 1.6, loosen, hold=0.3)
        c.status(Torque="loose")
        c.step(L(5), "Socket up ...", 0.6, lambda u: sock(1 - u, 32.0), hold=0.0)
        c.step(L(5), "... and the wrench slides off.", 0.8, rb.line_to(pre), hold=0.0)
        Wh = at_mir(PT.wrench_in_holder())
        c.step(L(5), "Back to its holder.", 2.0, rb.joint_to(Tw=T((0, 0, 60)) @ Wh @ Gw), hold=0.0, cam_to=cam_deck)
        c.step(L(5), "Back to its holder.", 0.6, both(rb.line_to(Wh @ Gw), lambda u: sock(0.0, 32.0 * (1 - u))),
               hold=0.0)
        rb.release(mb.g)
        c.step(L(5), "Back to its holder.", 0.5, both(rb.grip_to(OPEN), rb.line_to(Wh @ Gw @ T((0, 0, -60)))),
               hold=0.0)

    # ------------------------------------------------------------------ 6: unscrew it by hand
    if chapter():
        def upper_world():
            return c.stack_world() @ c.upper_local_M()
        Gu = grasp_upper_local(25.0)
        turns_left = PT.THREAD_TURNS - 32.0 / 360.0
        per = 180.0                  # a grasp turns it half a turn; the wrist stays within 90 deg of centre
        n_grasp = int(math.ceil(turns_left * 360.0 / per))
        rot0 = c.upper_rot
        done = 0.0
        Gs = c.stack_world() @ T((0, 0, c.upper_out)) @ Gu @ R((0, 0, 1), 90.0)
        adv = per / 360.0 * PT.M8_PITCH
        approach(c, rb, L(6), "The 2F-85 takes the upper sonotrode on its axis, below the Sharpie lines ...",
                 Gs @ T((0, 0, -80)), Gs, lambda u: Gs @ T((0, 0, -adv * u)) @ R((0, 0, 1), -per * u), close_upper,
                 skip=("plate upper",), secs=(2.2, 0.7), back=Gs @ T((0, 0, -adv)) @ R((0, 0, 1), -per) @
                 T((0, 0, -80)), cam_to=cam_stack)
        Gc = Gs
        cap = (f"... and unscrews it by hand: {PT.THREAD_TURNS:.1f} turns of M8 on the connector, half a turn a "
               f"grasp (the grip's friction, about 1.4 N m at 235 N, ours, turns a free thread).")
        for i in range(n_grasp):
            d = min(per, turns_left * 360.0 - done)
            c.step(L(6), cap, 0.2, rb.grip_to(close_upper), hold=0.0)
            rb.grasp(g("upper"))

            def turn(u, G=Gc, d=d):
                return G @ T((0, 0, -d * u / 360.0 * PT.M8_PITCH)) @ R((0, 0, 1), -d * u)
            c.step(L(6), cap, 0.45, spin(rb, lambda u, G=Gc, d=d: G @ T((0, 0, -d * u / 360.0 * PT.M8_PITCH)),
                                         lambda u, d=d: -d * u, n=24), hold=0.0)
            done += d
            rb.release(g("connector"))
            c.set_upper(rot=rot0 - done, out=(done + 32.0) / 360.0 * PT.M8_PITCH)
            c.status(Upper=f"{(done + 32.0) / 360.0:.1f} / {PT.THREAD_TURNS:.1f} turns off")
            Gt_ = turn(1.0)
            if i < n_grasp - 1:
                c.step(L(6), cap, 0.35, both(rb.grip_to(ur_arm.close_for(2 * PT.UPPER_R + 8.0)),
                                             spin(rb, lambda u, G0=Gt_: G0, lambda u, d=d: d * u, n=24)),
                       hold=0.0)
                Gc = Gt_ @ R((0, 0, 1), d)
        rb.grasp(g("upper"))
        c.status(Upper="off the connector")
        c.step(L(6), "Off the stud. It goes to its tray on MiR 2.", 0.6, rb.line_to(rb.tcp_world() @ T((0, 0, -40))),
               hold=0.0)
        Ut = at_mir(PT.upper_in_tray(-1))
        Gt = Ut @ Gu          # the coaxial grip leaves the sonotrode free to stand at any turn in its square socket
        c.step(L(6), "Off the stud. It goes to its tray on MiR 2.", 2.2, rb.joint_to(Tw=Gt @ T((0, 0, -50))), hold=0.0,
               cam_to=cam_deck)
        c.step(L(6), "Off the stud. It goes to its tray on MiR 2.", 0.7, rb.line_to(Gt), hold=0.0)
        rb.release(mb.g)
        c.step(L(6), "Off the stud. It goes to its tray on MiR 2.", 0.5,
               both(rb.grip_to(OPEN), rb.line_to(Gt @ T((0, 0, -60)))), hold=0.0)

    # ------------------------------------------------------------------ 7: old plate off, into its slot
    if chapter():
        Gp = grasp_plate_local()
        Fs = c.stack_world()
        G = Fs @ Gp
        c.step(L(7), "It takes the old plate near its free end, the pads on its faces ...", 2.2,
               both(rb.grip_to(ur_arm.close_for(18.0)), rb.joint_to(Tw=G @ T((0, 0, -70)))), hold=0.0, cam_to=cam_stack)
        c.step(L(7), "It takes the old plate near its free end, the pads on its faces ...", 0.7, rb.line_to(G),
               hold=0.0)
        c.step(L(7), "It takes the old plate near its free end, the pads on its faces ...", 0.3,
               rb.grip_to(close_plate), hold=0.0)
        rb.grasp(g("plate"))
        off = Fs @ T((0, 0, M.CONN_HALF + 2.0)) @ Gp
        c.step(L(7), "... and slides it straight off the M8 stud, along the axis (14 mm), never forcing it "
               "(DAL 178 step 9: a plate snapped at its hole's edge once).", 1.2, rb.line_to(off), hold=0.0)
        slot = at_mir(PT.plate_in_slot(OLD["slot"]))
        Gs = slot @ Gp
        c.step(L(7), f"Into its own labelled slot: plates stay with one alloy (DAL 178, OCT2a 02:24).", 2.4,
               rb.joint_to(Tw=T((0, 0, 70)) @ Gs), hold=0.0, cam_to=cam_deck)
        c.step(L(7), f"Into its own labelled slot: plates stay with one alloy (DAL 178, OCT2a 02:24).", 0.9,
               rb.line_to(Gs), hold=0.0)
        rb.release(mb.g)
        c.step(L(7), "Logged.", 0.5, both(rb.grip_to(OPEN), rb.line_to(Gs @ T((0, 0, -60)))), hold=0.8,
               labels=[(f"{OLD['id']}  {OLD['alloy']}  {OLD['mat']}\nruns {OLD['uses']}  {OLD['cond']}",
                        tuple(mirw((PT.slot_x(OLD['slot']), PT.RACK_AT[1], PT.TOP + 110))), (0.70, 0.22))])
        c.status(Plate=f"{OLD['id']} -> slot {OLD['slot'] + 1} (log: {OLD['alloy']}, {OLD['uses']} runs)")

    # ------------------------------------------------------------------ 8: the new plate on
    if chapter():
        Gp = grasp_plate_local()
        slot = at_mir(PT.plate_in_slot(NEW["slot"]))
        Gs = slot @ Gp
        c.step(L(8), f"The next run is copper, so a new W-coated plate ({NEW['id']}; DAL 253 Copper step 2).", 1.4,
               both(rb.grip_to(ur_arm.close_for(18.0)), rb.joint_to(Tw=Gs @ T((0, 0, -60)))), hold=0.0)
        c.step(L(8), f"The next run is copper, so a new W-coated plate ({NEW['id']}; DAL 253 Copper step 2).", 0.6,
               rb.line_to(Gs), hold=0.0)
        c.step(L(8), "It grips the plate ...", 0.3, rb.grip_to(close_plate), hold=0.0)
        rb.grasp("newplate")
        c.step(L(8), "... lifts it out ...", 0.9, rb.line_to(T((0, 0, 125)) @ Gs), hold=0.0)
        Fs = c.stack_world()
        off = Fs @ T((0, 0, M.CONN_HALF + 2.0)) @ Gp
        c.step(L(8), "... and slides it onto the stud, square to the axis, onto the lower sonotrode's face (the "
               "connector was threaded fully in first, step 10).", 2.4, rb.joint_to(Tw=off @ T((0, 0, -40))),
               hold=0.0, cam_to=cam_stack)
        c.step(L(8), "... and slides it onto the stud ...", 0.5, rb.line_to(off), hold=0.0)
        c.step(L(8), "... and slides it onto the stud ...", 1.0, rb.line_to(Fs @ T((0, 0, 0.05)) @ Gp), hold=0.0)
        rb.release(g("connector"))
        c.step(L(8), "Let go.", 0.4, both(rb.grip_to(OPEN), rb.line_to(Fs @ Gp @ T((0, 0, -60)))), hold=0.0)
        c.step(L(8), "The camera looks along the joint, edge on: the plate lies flat on the face with no gap "
               "(step 11).", 1.6, rb.joint_to(Tw=c.stack_world() @ local_tcp((40.0, -150.0, 1.25), (0, 1, 0), (0, 0, 1))),
               hold=0.8)
        c.status(Plate=f"{NEW['id']} ({NEW['alloy']}, {NEW['mat']}), flat", Uses="0")

    # ------------------------------------------------------------------ 9: upper sonotrode on by hand
    if chapter():
        Gu = grasp_upper_local(25.0)
        Ut = at_mir(PT.upper_in_tray(-1))
        Gt = Ut @ Gu                     # coaxial: taken at the wrist's own turn, whatever the sonotrode's
        c.step(L(9), "The upper sonotrode from its tray ...", 2.0, rb.joint_to(Tw=Gt @ T((0, 0, -60))), hold=0.0,
               cam_to=cam_deck)
        c.step(L(9), "The upper sonotrode from its tray ...", 0.6, rb.line_to(Gt), hold=0.0)
        c.step(L(9), "The upper sonotrode from its tray ...", 0.25, rb.grip_to(close_upper), hold=0.0)
        rb.grasp(g("upper"))
        c.step(L(9), "The upper sonotrode from its tray ...", 0.6, rb.line_to(Gt @ T((0, 0, -60))), hold=0.0)
        # onto the stud at the thread's start, the wrist 90 deg back from centre, then half a turn a grasp
        per = 180.0
        total = PT.THREAD_TURNS * 360.0
        n_grasp = int(math.ceil(total / per))
        out0 = PT.THREAD_TURNS * PT.M8_PITCH
        adv = per / 360.0 * PT.M8_PITCH
        Fs = c.stack_world()
        Gs = Fs @ T((0, 0, out0)) @ Gu @ R((0, 0, 1), -90.0)
        Grel = inv(sc.world(g("upper")) @ PT.FS) @ rb.tcp_world()        # the grip as taken in the tray
        Pf = inv(Fs @ T((0, 0, out0))) @ Gs @ inv(Grel)                  # the sonotrode's frame at the start, stack-relative
        rot0 = -math.degrees(math.atan2(Pf[1, 0], Pf[0, 0]))
        approach(c, rb, L(9), "... onto the stud, by hand (step 12).", Gs @ T((0, 0, -30)), Gs,
                 lambda u: Gs @ T((0, 0, adv * u)) @ R((0, 0, 1), per * u), close_upper, skip=("plate upper",),
                 secs=(2.2, 0.5), pre_close=close_upper, cam_to=cam_stack)
        rb.release(g("connector"))
        c.set_upper(rot=rot0, out=out0)
        done = 0.0
        Gc = Gs
        cap = f"Threaded down by hand, half a turn a grasp ({n_grasp} grasps), until it sits on the plate."
        for i in range(n_grasp):
            d = min(per, total - done)
            c.step(L(9), cap, 0.2 if i else 0.1, rb.grip_to(close_upper), hold=0.0)
            rb.grasp(g("upper"))

            def turn(u, G=Gc, d=d):
                return G @ T((0, 0, d * u / 360.0 * PT.M8_PITCH)) @ R((0, 0, 1), d * u)
            c.step(L(9), cap, 0.45, spin(rb, lambda u, G=Gc, d=d: G @ T((0, 0, d * u / 360.0 * PT.M8_PITCH)),
                                         lambda u, d=d: d * u, n=24), hold=0.0)
            done += d
            rb.release(g("connector"))
            c.set_upper(rot=rot0 + done, out=(total - done) / 360.0 * PT.M8_PITCH)
            c.status(Upper=f"{done / 360.0:.1f} / {PT.THREAD_TURNS:.1f} turns on")
            Gt_ = turn(1.0)
            if i < n_grasp - 1:
                c.step(L(9), cap, 0.35, both(rb.grip_to(ur_arm.close_for(2 * PT.UPPER_R + 8.0)),
                                             spin(rb, lambda u, G0=Gt_: G0, lambda u, d=d: -d * u, n=24)),
                       hold=0.0)
                Gc = Gt_ @ R((0, 0, 1), -d)
        c.set_upper(rot=rot0 + total, out=0.0)
        c.rot_hand = rot0 + total
        c.status(Upper="snug, by hand")
        c.step(L(9), "Snug against the plate.", 0.5, both(rb.grip_to(OPEN), rb.line_to(rb.tcp_world() @ T((0, 0, -70)))),
               hold=0.0)

    # ------------------------------------------------------------------ 10: torque 50 N m
    if chapter():
        Gw = grasp_wrench_local()
        Wh = at_mir(PT.wrench_in_holder())
        c.step(L(10), "The stack wrench again.", 2.0, rb.joint_to(Tw=Wh @ Gw @ T((0, 0, -80))), hold=0.0,
               cam_to=cam_deck)
        c.step(L(10), "The stack wrench again.", 0.6, rb.line_to(Wh @ Gw), hold=0.0)
        c.step(L(10), "The stack wrench again.", 0.3, rb.grip_to(close_bar), hold=0.0)
        rb.grasp("wrench")
        c.step(L(10), "The stack wrench again.", 0.6, rb.line_to(T((0, 0, 60)) @ Wh @ Gw), hold=0.0)
        Fs = c.stack_world()
        eng = Fs @ Gw
        pre = Fs @ T((0, -60, 0)) @ Gw
        c.step(L(10), "Counter-hold on the lower sonotrode's flats; the socket onto the upper's.", 2.2,
               rb.joint_to(Tw=pre), hold=0.0, cam_to=cam_stack)
        c.step(L(10), "Counter-hold on the lower sonotrode's flats; the socket onto the upper's.", 1.0,
               rb.line_to(eng), hold=0.0)

        def sock(u, turn=0.0):
            sc.gmat["socket"] = T((0, 0, -PT.SOCKET_STROKE * u)) @ R((0, 0, 1), turn)
        rh = getattr(c, "rot_hand", 0.0)
        t0 = (-rh + 90.0) % 180.0 - 90.0                 # the socket's slot to the flats' angle (they repeat every 180)
        c.step(L(10), "The drive turns its slot to the flats' angle, which the camera reads ...", 0.6,
               lambda u: sock(0.0, t0 * u), hold=0.0)
        c.step(L(10), "... and the socket slides onto them.", 0.8, lambda u: sock(u, t0), hold=0.0)

        def tighten(u):
            a = 20.0 * u
            sock(1.0, t0 - a)
            c.set_upper(rot=rh + a)
            tq = 50.0 * (u ** 1.6)
            c.status(Torque=f"{tq:5.1f} N m (clutch at 50.0)", Reaction=f"{tq:5.1f} N m inside the tool")
        c.step(L(10), "The last 20 deg (ours) to 50 N m, where the clutch slips (DAL 253 step 13). The counter-hold "
               "takes the same 50 N m, so the stack and the arm see none of it.", 2.4, tighten, hold=0.6)
        c.status(Torque="50.0 N m", Reaction="-")
        c.step(L(10), "Socket up, wrench off.", 0.6, lambda u: sock(1 - u, t0 - 20.0), hold=0.0)
        c.step(L(10), "Socket up, wrench off.", 0.8, rb.line_to(pre), hold=0.0)
        Wh = at_mir(PT.wrench_in_holder())
        c.step(L(10), "Back to its holder.", 2.0, rb.joint_to(Tw=T((0, 0, 60)) @ Wh @ Gw), hold=0.0, cam_to=cam_deck)
        c.step(L(10), "Back to its holder.", 0.6, both(rb.line_to(Wh @ Gw), lambda u: sock(0.0, (t0 - 20.0) * (1 - u))),
               hold=0.0)
        rb.release(mb.g)
        c.step(L(10), "Back to its holder.", 0.5, both(rb.grip_to(OPEN), rb.line_to(Wh @ Gw @ T((0, 0, -60)))),
               hold=0.0)

    # ------------------------------------------------------------------ 11: orient, height, rescan, wet test
    if chapter():
        Fs = c.stack_world()
        mid = (Fs @ np.r_[55.0, 0.0, PT.PLATE_T, 1.0])[:3]
        eye = (Fs @ np.r_[55.0, -110.0, 170.0, 1.0])[:3]
        look = frame(eye, mid - eye, Fs[:3, 0])
        c.step(L(11), "The camera checks the plate is square to the hatch (step 14; within 2 deg, ours) ...", 2.0,
               rb.joint_to(Tw=look), hold=0.6, cam_to=cam_stack)
        # the gauge plate: from its holder, its end laid against the upper sonotrode between the lines
        Gg = local_tcp((PT.GAUGE_L - 12.0, PT.GAUGE_W / 2 - 4.0, PT.GAUGE_T / 2), (0, -1, 0), (0, 0, 1))
        Gh = at_mir(PT.gauge_in_holder()) @ Gg
        c.step(L(11), "... and the height: the Mo gauge plate (a retired plate cut short, DAL #164).", 2.0,
               rb.joint_to(Tw=Gh @ T((0, 0, -60))), hold=0.0, cam_to=cam_deck)
        c.step(L(11), "... and the height: the Mo gauge plate (a retired plate cut short, DAL #164).", 0.6,
               rb.line_to(Gh), hold=0.0)
        c.step(L(11), "... and the height: the Mo gauge plate (a retired plate cut short, DAL #164).", 0.25,
               rb.grip_to(close_gauge), hold=0.0)
        rb.grasp("gauge")
        c.step(L(11), "... and the height: the Mo gauge plate (a retired plate cut short, DAL #164).", 0.6,
               rb.line_to(T((0, 0, 60)) @ Gh), hold=0.0)
        zl = (PT.SHARPIE_Z[0] + PT.SHARPIE_Z[1]) / 2
        # the gauge held level and on edge, its end 0.5 mm off the upper sonotrode, its top edge at the lines' middle
        Fs = c.stack_world()
        p_touch = (Fs @ np.r_[0.0, 0.0, zl, 1.0])[:3]
        side = Fs[:3, :3] @ np.array([0.0, -1.0, 0.0])
        side[2] = 0.0
        side /= np.linalg.norm(side)
        tip = p_touch + side * (PT.UPPER_R + 0.5)
        Gf = np.eye(4)
        Gf[:3, 0], Gf[:3, 1] = side, (0, 0, 1)
        Gf[:3, 2] = np.cross(Gf[:3, 0], Gf[:3, 1])
        Gf[:3, 3] = tip - Gf[:3, 1] * (PT.GAUGE_W / 2) - Gf[:3, 2] * (PT.GAUGE_T / 2)
        Gg2 = local_tcp((PT.GAUGE_L - 12.0, PT.GAUGE_W / 2 - 4.0, PT.GAUGE_T / 2), (0, -1, 0), (0, 0, 1))
        Gtcp = Gf @ Gg2
        c.step(L(11), "Laid level against the upper sonotrode: its edge falls between the Sharpie lines, so the plate "
               "is at the logged height (step 15).", 2.2, rb.joint_to(Tw=Gtcp @ T((0, 0, -30))), hold=0.0,
               cam_to=cam_stack)
        c.step(L(11), "Laid level against the upper sonotrode: its edge falls between the Sharpie lines.", 0.6,
               rb.line_to(Gtcp), hold=0.8,
               labels=[("Sharpie lines (DAL #164)", tuple((Fs @ np.r_[0, 0, zl, 1])[:3]), (0.80, 0.34))])
        c.status(Height=f"between the lines ({zl - M.PLATE_T:.0f} mm), logged")
        Gh = at_mir(PT.gauge_in_holder()) @ Gg
        c.step(L(11), "The gauge back.", 2.0, rb.joint_to(Tw=T((0, 0, 60)) @ Gh), hold=0.0, cam_to=cam_deck)
        c.step(L(11), "The gauge back.", 0.6, rb.line_to(Gh), hold=0.0)
        rb.release(mb.g)
        c.step(L(11), "The gauge back.", 0.4, both(rb.grip_to(OPEN), rb.line_to(Gh @ T((0, 0, -60)))), hold=0.0)
        # rescan on the HMI
        c.scan_u = 0.0
        c.inset = ("scan", 1.0)

        def scan(u):
            c.scan_u = u
        c.step(L(11), "Rescan with the plate on (step 16): one peak in 39.5-40.5 kHz; the power reads higher with "
               "the plate on (DAL 178 step 10).", 2.6, scan, hold=1.0)
        c.status(Scan="40.10 kHz, one peak")
        c.inset = None
        # wet test: the dropper, taken from the side, then turned nozzle-down by the wrist over the plate
        Gd = local_tcp((0.0, 0.0, 40.0), (0, -1, 0), (1, 0, 0))
        Dh = at_mir(T((PT.DROP_AT[0], PT.DROP_AT[1], PT.TOP + 4.0))) @ Gd
        c.step(L(11), "Wet test: the IPA dropper ...", 1.8, rb.joint_to(Tw=Dh @ T((0, 0, -60))), hold=0.0,
               cam_to=cam_deck)
        c.step(L(11), "Wet test: the IPA dropper ...", 0.6, rb.line_to(Dh), hold=0.0)
        c.step(L(11), "Wet test: the IPA dropper ...", 0.25, rb.grip_to(close_bottle), hold=0.0)
        rb.grasp("dropper")
        c.step(L(11), "Wet test: the IPA dropper ...", 0.6, rb.line_to(T((0, 0, 80)) @ Dh), hold=0.0)
        Fs = c.stack_world()
        spot = (Fs @ np.r_[95.0, 0.0, PT.PLATE_T, 1.0])[:3]
        Bm = np.eye(4)                                  # the bottle upside down, its nozzle 52 mm over the spot
        Bm[:3, 0], Bm[:3, 1], Bm[:3, 2] = (1, 0, 0), (0, -1, 0), (0, 0, -1)
        Bm[:3, 3] = spot + np.array([0, 0, 52.0 + 90.0])
        Gdrop = Bm @ Gd
        c.step(L(11), "... over the plate, turned nozzle-down.", 2.4, rb.joint_to(Tw=Gdrop), hold=0.0,
               cam_to=cam_stack)
        drop_from = spot + np.array([0, 0, 52.0])
        fall = math.sqrt(2 * 0.052 / 9.81)                 # s: a drop falls 52 mm in 0.10 s
        mist0 = np.array([(Fs @ np.r_[RNG.uniform(-8, 105), RNG.uniform(-9, 9), PT.PLATE_T, 1.0])[:3]
                          for _ in range(c.mist_n)])
        vel = np.array([Fs[:3, :3] @ np.r_[RNG.normal(0, 0.15), RNG.normal(0, 0.15), 1.0] for _ in range(c.mist_n)])
        vel *= RNG.uniform(20, 70, (c.mist_n, 1))         # mm/s: a slow mist off the face (ours)
        T_STEP = 3.6
        t_drop = (0.3, 0.9, 1.5)                           # s into the step: three drops
        born = np.array([t_drop[int(RNG.integers(0, 3))] + fall + RNG.uniform(0.0, 1.4) for _ in range(c.mist_n)])

        def wet(u):
            t = u * T_STEP
            p = None
            for t0 in t_drop:
                if t0 - 0.25 <= t < t0:                       # it swells at the nozzle
                    p = drop_from
                elif t0 <= t < t0 + fall:
                    tt = t - t0
                    p = drop_from + np.array([0, 0, -0.5 * 9810.0 * tt * tt])
            sc.show(["plate drop"], 1.0 if p is not None else 0.0)
            if p is not None:
                sc.gmat["drop"] = T(p - AB.RP)
            age = t - born
            on = age > 0
            sc.show(["plate mist"], 1.0 if on.any() else 0.0)
            pts = mist0 + vel * np.clip(age, 0, None)[:, None]
            pts[~on] = mist0[~on] - Fs[:3, 2] * 0.5            # not yet: on the face, hidden in the plate's skin
            sc.set_mesh("plate mist", pv.PolyData(pts - AB.RP))
        c.step(L(11), "Three drops of IPA with the vibration on: the whole plate atomizes them, straight off its "
               "face, so it is not cracked (step 16; DAL 178 step 10).", T_STEP, wet, hold=0.0)
        sc.show(["plate mist"], 0.0)
        c.status(Wet="whole plate atomizes")
        Dh = at_mir(T((PT.DROP_AT[0], PT.DROP_AT[1], PT.TOP + 4.0))) @ Gd
        c.step(L(11), "The dropper back.", 2.2, rb.joint_to(Tw=T((0, 0, 80)) @ Dh), hold=0.0, cam_to=cam_deck)
        c.step(L(11), "The dropper back.", 0.6, rb.line_to(Dh), hold=0.0)
        rb.release(mb.g)
        c.step(L(11), "The dropper back.", 0.4, both(rb.grip_to(OPEN), rb.line_to(Dh @ T((0, 0, -60)))), hold=0.0)

    # ------------------------------------------------------------------ 12: seals, door shut, landing, bolts
    if chapter():
        Gwp = local_tcp((0.0, 0.0, 55.0), (0, -1, 0), (1, 0, 0))     # the wipe's stem, from the side
        W0 = T((PT.WIPE_AT[0], PT.WIPE_AT[1], PT.TOP + 4.0))
        Wp = at_mir(W0) @ Gwp
        c.step(L(12), "The wipe pad, wet with IPA (ours) ...", 1.8, rb.joint_to(Tw=Wp @ T((0, 0, -60))), hold=0.0,
               cam_to=cam_deck)
        c.step(L(12), "The wipe pad, wet with IPA (ours) ...", 0.6, rb.line_to(Wp), hold=0.0)
        c.step(L(12), "The wipe pad, wet with IPA (ours) ...", 0.25, rb.grip_to(close_stem), hold=0.0)
        rb.grasp("wipe")
        c.step(L(12), "The wipe pad, wet with IPA (ours) ...", 0.6, rb.line_to(T((0, 0, 80)) @ Wp), hold=0.0)
        D = AB.WT(Dm(c.door))
        pts = [(-114.5, 10.0, 1080.0), (-114.5, -95.0, 1080.0), (-114.5, -95.0, 860.0)]

        def pad_pose(p):
            Pm = np.eye(4)                                  # the pad's face on the door's seal face, 0.5 mm off
            Pm[:3, 0], Pm[:3, 1], Pm[:3, 2] = (0, 1, 0), (0, 0, 1), (1, 0, 0)
            Pm[:3, 3] = p
            return D @ Pm @ Gwp

        def loop(u):
            f = u * (len(pts) - 1)
            i = min(int(f), len(pts) - 2)
            p = np.array(pts[i], float) + (np.array(pts[i + 1], float) - np.array(pts[i], float)) * (f - i)
            return pad_pose(p)
        c.step(L(12), "... along the door's seal face (step 18; here the top and the front side, the rest the same "
               "way).", 2.4, rb.joint_to(Tw=loop(0.0) @ T((0, 0, -40))), hold=0.0, cam_to=cam_open)
        c.step(L(12), "... along the door's seal face (step 18) ...", 0.5, rb.line_to(loop(0.0)), hold=0.0)
        c.step(L(12), "... along the door's seal face (step 18) ...", 2.6, track(rb, loop, n=70), hold=0.0)
        c.step(L(12), "Wipe back.", 0.5, rb.line_to(loop(1.0) @ T((0, 0, -50))), hold=0.0)
        Wp = at_mir(W0) @ Gwp
        c.step(L(12), "Wipe back.", 2.2, rb.joint_to(Tw=T((0, 0, 80)) @ Wp), hold=0.0, cam_to=cam_deck)
        c.step(L(12), "Wipe back.", 0.6, rb.line_to(Wp), hold=0.0)
        rb.release(mb.g)
        c.step(L(12), "Wipe back.", 0.4, both(rb.grip_to(OPEN), rb.line_to(Wp @ T((0, 0, -60)))), hold=0.0)
        # door shut
        lug = np.array([PT.LUG_X[0] + 4.0, -139.0, PT.BOLT_Z[1]])
        Gl0 = AB.WT(local_tcp(lug, (0, 1, 0), (0, 0, 1)))

        def door_pose(u):
            return AB.WT(Dm(u)) @ inv(AB.WT(np.eye(4))) @ Gl0
        q_pre = rb.solve(door_pose(1.0) @ T((0, 0, -70)), c.door_path[-1])
        c.step(L(12), "The door shut on the wiped seal ...", 2.0, rb.joint_to(q1=q_pre), hold=0.0, cam_to=cam_open)
        c.step(L(12), "The door shut on the wiped seal ...", 0.6, rb.joint_to(q1=c.door_path[-1]), hold=0.0)
        c.step(L(12), "The door shut on the wiped seal ...", 0.3, rb.grip_to(close_lug), hold=0.0)
        c.step(L(12), "The door shut on the wiped seal ...", 3.0,
               replay(rb, np.r_[[rb.q], c.door_path[::-1]], also=lambda u: c.set_door(1.0 - u)), hold=0.0)
        c.step(L(12), "The door shut on the wiped seal ...", 0.5,
               both(rb.grip_to(OPEN), rb.line_to(door_pose(0.0) @ T((0, 0, -70)))), hold=0.0)
        c.status(Door="shut")
        # landing check: the laser down the empty nozzle
        cam_land = AB.cam((-260, -820, 1060), (-25, 0, 930))

        ours = [n for n in sc.actors if n.startswith("plate bolt") or n == "plate door lugs"]

        def cut(f):
            AB.AA.set_cut(sc, f, AB.AA.CH_G)
            sc.show(ours, 1.0 - f)                      # our bolts and lugs go with the cut-away front half
        c.step(L(12), "Landing check, the chamber cut open here to show it: a laser in the sealing rod's place shines "
               "down the empty nozzle (DAL #164, T5 63:28) ...", 1.6, cut, hold=0.0, cam_to=cam_land)
        sc.show(sc.members("laser"), 1.0)
        c.step(L(12), "... its dot lands high on the plate and centred, 7 mm clear of the upper sonotrode (step 17; "
               "the left camera sees it through the door's sight glass, DAL PR 189).", 1.2, None, hold=1.6,
               labels=[("laser dot: 75 mm down the plate\nfrom its hole, 7 mm clear", tuple(AB.W(M.IMPACT)),
                        (0.70, 0.28))])
        sc.show(sc.members("laser"), 0.0)
        c.step(L(12), "The laser comes out before heating (#164).", 1.2, lambda u: cut(1.0 - u), hold=0.0)
        # bolts back
        for k in (0, 1):
            pin = AB.W(PT.bolt_geom(k)[0])
            deg = PT.SWING_DEG[k]
            kc1 = PT.knob_centre(k, 0.0, 1.0) + np.array([0.0, 0.0, 1.25])
            G1 = AB.WT(local_tcp(kc1, (0, 1, 0), (0, 0, 1)))
            G1o = R((0, 1, 0), deg, pin) @ G1
            c.step(L(12), "Both bolts back into their lugs ...", 1.6, rb.joint_to(Tw=G1o @ T((0, 0, -60))), hold=0.0,
                   cam_to=cam_bolts)
            c.step(L(12), "Both bolts back into their lugs ...", 0.5, rb.line_to(G1o), hold=0.0)
            c.step(L(12), "Both bolts back into their lugs ...", 0.3, rb.grip_to(close_knob), hold=0.0)
            rb.grasp(f"bolt{k}")
            c.step(L(12), "Both bolts back into their lugs ...", 1.3,
                   track(rb, lambda u, G1=G1, pin=pin, deg=deg: R((0, 1, 0), deg * (1 - u), pin) @ G1, n=60), hold=0.0)
            rb.release("rp")
            c.swing[k] = 0.0
            c.set_bolt(k)
            c.step(L(12), "Both bolts back into their lugs ...", 0.4, both(rb.grip_to(OPEN),
                                                                            rb.line_to(G1 @ T((0, 0, -60)))), hold=0.0)
            knob_turn(c, rb, k, loosen=False, caption_cam=None, close=close_knob, L=L(12))
        c.status(Door="shut, 2 bolts tight")
        c.step(L(12), f"Done: {NEW['id']} on at 50 N m, square, at the logged height, scan 40.10 kHz, wet test good. "
               "Logged for the run (DAL 253 Run Log item 3).", 1.8, rb.joint_to(q1=np.radians(AB.AA.A.PARK_DEG)),
               hold=1.6, cam_to=cam_far, still=True)
    AB.finish(sc)


both = AB.both

if __name__ == "__main__":
    main()
