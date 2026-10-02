"""Deflection, sway and natural frequency of each hutch option (#229), from a plywood shell model.

    python fea.py            # fea-results.json, fea-results.md, fea-shapes.npz

Every panel is meshed on its mid-plane with ~25 mm OpenSees ShellMITC4 elements, using an
orthotropic plywood section with the face grain where the cut plan puts it. Joints are glued
and screwed, so panels share nodes along their edges. The panel feet are pinned to the table
top and the table is rigid. The arm's foot is a rigid 100 mm square at the middle of the deck.

The structure is linear, so it is reduced to one 6 x 6 compliance matrix at the arm's foot. Each
load case from loads.py is then turned to every J1 direction, and the fingertip error is the
foot's translation plus its rotation times the lever arm out to the fingertip.
"""

import json
import sys
from pathlib import Path

import numpy as np
import openseespy.opensees as ops

import hutch as H
from loads import ArmLoads

HERE = Path(__file__).parent
MESH = 0.025
DOME_MASS = 7.0          # kg: 13.4 m of pipe at 0.30 kg/m, 8 elbows, 33 clamps and 2.2 kg of canvas


def grid(a, b, keys=(), h=MESH):
    """Points from a to b about h apart, with every key point on the grid."""
    keys = sorted(k for k in set(np.round(list(keys) + [a, b], 6)) if a - 1e-6 <= k <= b + 1e-6)
    out = []
    for k0, k1 in zip(keys[:-1], keys[1:]):
        n = max(1, int(np.ceil((k1 - k0) / h - 1e-9)))
        out += list(np.linspace(k0, k1, n + 1)[:-1])
    return np.array(out + [keys[-1]])


class Model:
    def __init__(self, opt):
        self.opt = opt
        self.o = H.OPTIONS[opt]
        self.nodes, self.coords, self.elems = {}, [], []
        self.fixed = set()
        self.build()

    # -------------------------------------------------------------- mesh
    def node(self, x, y, z):
        k = (round(x, 5), round(y, 5), round(z, 5))
        if k not in self.nodes:
            self.nodes[k] = len(self.nodes) + 1
            self.coords.append(k)
            ops.node(self.nodes[k], *k)
        return self.nodes[k]

    def panel(self, axis, c, u, v, sec, order, t):
        """Quads on the plane coord[axis] = c over grids u, v (the other two axes, in order).
        `order` = True puts element local x along u (the grain), else along v."""
        ax = [i for i in range(3) if i != axis]
        for i in range(len(u) - 1):
            for j in range(len(v) - 1):
                pts = []
                for a, b in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)) if order else \
                        ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j)):
                    p = [0.0, 0.0, 0.0]
                    p[axis], p[ax[0]], p[ax[1]] = c, u[a], v[b]
                    pts.append(self.node(*p))
                s = sec(u[i:i + 2].mean(), v[j:j + 2].mean()) if callable(sec) else sec
                tag = len(self.elems) + 1
                ops.element("ShellMITC4", tag, *pts, s)
                area = (u[i + 1] - u[i]) * (v[j + 1] - v[j])
                self.elems.append((pts, area * t[s] * H.RHO))

    def build(self):
        o = self.o
        ops.wipe()
        ops.model("basic", "-ndm", 3, "-ndf", 6)
        # material x = face grain; plane stress through PlateFiber, integrated through the thickness
        ops.nDMaterial("ElasticOrthotropic", 1, H.E_PAR, H.E_PERP, H.E_PERP, H.NU, 0.3, 0.3,
                       H.G_INPLANE, H.G_TRANSVERSE, H.G_TRANSVERSE, 0.0)
        ops.nDMaterial("PlateFiber", 2, 1)
        ops.section("PlateFiber", 1, 2, H.T)
        ops.section("PlateFiber", 2, 2, 2 * H.T)          # deck + doubler pad
        t = {1: H.T, 2: 2 * H.T}

        XS = H.W / 2 - H.T / 2                  # side panel mid-planes
        YF, YB = -H.W / 2, H.W / 2 - H.T / 2    # deck front edge, back panel mid-plane
        ZD = H.CLEAR + H.T / 2                  # deck mid-plane
        ZB = H.CLEAR - H.SPINE_H - H.T / 2      # spine bottom mid-plane
        b = H.BASE_PATCH / 2
        kx = [0, -b, b, -H.PAD_X / 2, H.PAD_X / 2]
        ky = [0, -b, b, -H.SPINE_Y, H.SPINE_Y]
        xs = grid(-XS, XS, kx)
        ys = grid(YF, YB, ky)
        zs = grid(0, ZD, [ZB])
        self.geom = dict(XS=XS, YF=YF, YB=YB, ZD=ZD, ZB=ZB)

        def deck_sec(x, y):
            return 2 if (o["spine"] and abs(x) < H.PAD_X / 2 and abs(y) < H.SPINE_Y) else 1

        self.panel(2, ZD, xs, ys, deck_sec, True, t)                    # deck, grain along x
        for s in (-1, 1):
            self.panel(0, s * XS, ys, zs, 1, True, t)                   # sides, grain front to back
        if o["back"]:
            self.panel(1, YB, xs, zs, 1, True, t)                       # back, grain left to right
        if o["spine"]:
            zw = zs[zs >= ZB - 1e-9]
            for s in (-1, 1):
                self.panel(1, s * H.SPINE_Y, xs, zw, 1, True, t)       # webs, grain along x
            yb = ys[(ys >= -H.SPINE_Y - 1e-9) & (ys <= H.SPINE_Y + 1e-9)]
            self.panel(2, ZB, xs, yb, 1, True, t)                      # box bottom, grain along x

        for k, n in self.nodes.items():
            if abs(k[2]) < 1e-9:
                ops.fix(n, 1, 1, 1, 0, 0, 0)                            # feet pinned to the table
                self.fixed.add(n)
            elif o["wall"] and abs(k[2] - ZD) < 1e-4 and abs(k[1] - YB) < 1e-4:
                ops.fix(n, 1, 1, 1, 0, 0, 0)                            # deck back edge on the wall ledger
                self.fixed.add(n)

        # the arm's foot: a rigid square tied to a master node at the deck centre
        self.master = 10 ** 6
        ops.node(self.master, 0.0, 0.0, ZD)
        for k, n in self.nodes.items():
            if abs(k[2] - ZD) < 1e-4 and abs(k[0]) <= b + 1e-4 and abs(k[1]) <= b + 1e-4:
                ops.rigidLink("beam", self.master, n)
        self.ZD = ZD

    # -------------------------------------------------------------- analysis
    def _static(self, load):
        ops.timeSeries("Constant", 1)
        ops.pattern("Plain", 1, 1)
        for n, v in load:
            ops.load(n, *v)
        ops.constraints("Transformation")
        ops.numberer("RCM")
        ops.system("UmfPack")
        ops.test("NormDispIncr", 1e-12, 6)
        ops.algorithm("Linear")
        ops.integrator("LoadControl", 1.0)
        ops.analysis("Static")
        ops.analyze(1)

    def _clear(self):
        ops.remove("loadPattern", 1)
        ops.remove("timeSeries", 1)
        ops.wipeAnalysis()
        ops.reset()

    def compliance(self):
        """6 x 6: foot translation and rotation per unit force and moment at the foot."""
        C = np.zeros((6, 6))
        for k in range(6):
            v = [0.0] * 6
            v[k] = 1.0
            self._static([(self.master, v)])
            C[:, k] = ops.nodeDisp(self.master)
            self._clear()
        self.C = C
        return C

    def shape(self, wrench):
        """Nodal displacements (n x 3) under a wrench at the foot, for the deformed-shape render."""
        self._static([(self.master, list(wrench))])
        U = np.array([ops.nodeDisp(n)[:3] for n in range(1, len(self.coords) + 1)])
        self._clear()
        return U

    def modes(self, arm):
        """Natural frequencies of the deck as a rigid body on the hutch's stiffness at the foot.

        A full eigen solve of the 40 000-DOF shell model is slow in OpenSees' band solver, so the
        stiffness is condensed to the foot (K = C^-1) and the masses that ride on the deck are
        lumped onto it: the arm at full reach pointing at the room, the deck, the spine, the dome
        on the rim and a third of each panel. This slightly underestimates the local rocking
        frequency, since the whole deck is made to rock with the foot."""
        K = np.linalg.inv((self.C + self.C.T) / 2)
        bodies = []
        Rz = rot_z(-np.pi / 2)
        zc = np.array([0, 0, H.T / 2])
        for m, r, I in arm.bodies(arm.q_reach):
            bodies.append((m, Rz @ r + zc, Rz @ I @ Rz.T))
        for b in H.boards(self.opt):
            m = float(np.prod(b.size)) * H.RHO
            c = b.centre - np.array([0, 0, self.ZD])
            if "side" in b.tags or "back" in b.tags:
                bodies.append((m / 3, np.array([c[0], c[1], 0.0]), np.zeros((3, 3))))
            else:
                s = b.size
                I = m / 12 * np.diag([s[1] ** 2 + s[2] ** 2, s[0] ** 2 + s[2] ** 2, s[0] ** 2 + s[1] ** 2])
                bodies.append((m, c, I))
        h = H.W / 2
        for x, y in ((-h, 0), (h, 0), (0, -h), (0, h)):
            bodies.append((DOME_MASS / 4, np.array([x, y, 0.0]), np.zeros((3, 3))))
        M = np.zeros((6, 6))
        for m, r, I in bodies:
            S = np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])
            M[:3, :3] += m * np.eye(3)
            M[:3, 3:] += -m * S
            M[3:, :3] += m * S
            M[3:, 3:] += I - m * S @ S
        from scipy.linalg import eigh
        lam, vec = eigh(K, M)
        return np.sqrt(lam) / (2 * np.pi), vec.T, float(sum(b[0] for b in bodies))


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def tip_error(C, F, M, tip, phi):
    """Fingertip displacement (m) for the arm pointing at angle phi (0 = +x, the arm's own frame
    turned about z), from the foot compliance C. Wrench and tip are in the arm's frame at the
    mounting face; the foot node is T/2 lower, on the deck mid-plane."""
    R = rot_z(phi)
    F, M, r = R @ F, R @ M, R @ tip + np.array([0, 0, H.T / 2])
    M = M + np.cross(np.array([0, 0, H.T / 2]), F)
    d = C @ np.r_[F, M]
    return d[:3] + np.cross(d[3:], r)


def main():
    arm = ArmLoads()
    cases = arm.cases()
    tip = arm.tip
    phis = np.radians(np.arange(0, 360, 15))
    F0, M0 = cases["static"]
    Fa, Ma = cases["static, arm only"]
    payload = (F0 - Fa, M0 - Ma)
    results, shapes = {}, {}
    for opt in H.OPTIONS:
        mdl = Model(opt)
        C = mdl.compliance()
        r = dict(label=H.OPTIONS[opt]["label"], note=H.OPTIONS[opt]["note"], nodes=len(mdl.coords),
                 elements=len(mdl.elems))

        def worst(F, M, part=None):
            errs = []
            for p in phis:
                e = tip_error(C, F, M, tip, p)
                errs.append(np.linalg.norm(e[:2]) if part == "h" else abs(e[2]) if part == "v" else np.linalg.norm(e))
            i = int(np.argmax(errs))
            return errs[i] * 1000, float(np.degrees(phis[i]))

        r["payload_mm"], r["payload_dir"] = worst(*payload)
        r["static_mm"], r["static_dir"] = worst(F0, M0)
        r["lift_mm"], _ = worst(*cases["J2 lift, full acceleration"])
        Fs, Ms = cases["J1 swing, braking from 180 deg/s"]
        Fd, Md = Fs - F0, Ms - M0             # the inertial part of the swing, on top of gravity
        r["sway_mm"], r["sway_dir"] = worst(Fd, Md, part="h")
        # the foot on its own, for the arm pointing at the room (-y)
        d = C @ np.r_[rot_z(-np.pi / 2) @ Fd, rot_z(-np.pi / 2) @ Md]
        r["sway_foot_mm"] = float(np.linalg.norm(d[:2]) * 1000)
        d = C @ np.r_[rot_z(-np.pi / 2) @ F0, rot_z(-np.pi / 2) @ M0]
        r["sag_mm"] = float(-d[2] * 1000)
        r["tilt_mrad"] = float(np.linalg.norm(d[3:5]) * 1000)
        f, vec, mass = mdl.modes(arm)
        r["f_hz"] = [float(x) for x in f[:3]]
        r["mode1"] = vec[0].tolist()
        r["moving_mass_kg"] = mass
        r["C"] = C.tolist()
        results[opt] = r
        print(f"{opt:12s} payload {r['payload_mm']:.3f} mm  static {r['static_mm']:.3f}  lift {r['lift_mm']:.3f}  "
              f"sway {r['sway_mm']:.3f} (foot {r['sway_foot_mm']:.3f})  sag {r['sag_mm']:.3f}  "
              f"f = {np.round(f[:3], 1)} Hz  [{r['nodes']} nodes]", flush=True)

        # deformed shape under the worst static case, for the renders
        mdl2 = Model(opt)
        phi = np.radians(r["static_dir"])
        R = rot_z(phi)
        W6 = np.r_[R @ F0, R @ M0 + np.cross([0, 0, H.T / 2], R @ F0)]
        shapes[opt] = dict(xyz=np.array(mdl2.coords), u=mdl2.shape(W6),
                           quads=np.array([p for p, _ in mdl2.elems]) - 1, phi=phi)
    out = dict(pose_deg=np.degrees(arm.q_reach).round(2).tolist(), tip=arm.tip.tolist(),
               cases={k: dict(F=v[0].round(3).tolist(), M=v[1].round(3).tolist()) for k, v in cases.items()},
               options=results)
    (HERE / "fea-results.json").write_text(json.dumps(out, indent=1))
    np.savez_compressed(HERE / "fea-shapes.npz", **{f"{k}__{kk}": vv for k, v in shapes.items()
                                                    for kk, vv in v.items()})
    return out


def variants():
    """Option 3 with a deeper spine, or a stiff adapter plate under the arm (README, "What is left")."""
    arm = ArmLoads()
    c = arm.cases()
    (F0, M0), (Fa, Ma) = c["static"], c["static, arm only"]
    phis = np.radians(np.arange(0, 360, 15))
    for label, kw in (("as built", {}), ("spine 150 mm deep", dict(SPINE_H=0.15)),
                      ("rigid 200 mm adapter plate", dict(BASE_PATCH=0.2))):
        old = {k: getattr(H, k) for k in kw}
        for k, v in kw.items():
            setattr(H, k, v)
        C = Model(H.RECOMMENDED).compliance()
        e = max(np.linalg.norm(tip_error(C, F0 - Fa, M0 - Ma, arm.tip, p)) for p in phis)
        print(f"{label:28s} payload deflection {e * 1000:.3f} mm", flush=True)
        for k, v in old.items():
            setattr(H, k, v)


if __name__ == "__main__":
    variants() if sys.argv[1:] == ["variants"] else main()
    sys.exit(0)
