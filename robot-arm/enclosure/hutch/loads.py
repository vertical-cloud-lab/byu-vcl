"""What the PiPER pushes into the deck at full reach with a 1.5 kg payload (#229).

    python loads.py

Masses, centres of mass and link inertias come from AgileX's `piper_description.urdf`
(4.17 kg arm + 0.50 kg gripper, which matches the manual's 4.2 kg + 0.5 kg). The `_v100` URDF
the renders use has placeholder masses (1.4 kg in total), so it is only used for the geometry,
and the two agree on the kinematics to within 2 mm.

Every wrench is what the arm does *to the deck*, at the centre of the base's mounting face, in
the arm's own frame: +x is the way the arm points, z is up. Newtons and newton-metres.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from piper_fk import Piper, _rpy  # noqa: E402

G = 9.81
PAYLOAD = 1.5            # kg, the rated payload, taken at the fingertip point (140 mm past the flange)
OMEGA_J1 = np.pi         # rad/s, J1's rated 180 deg/s (manual)
ALPHA_MAX = 5.0          # rad/s^2, the SDK's ceiling: JointConfig.max_joint_acc is 0-500 in 0.01 rad/s^2


def inertials(piper, urdf):
    """{link: (mass, com in link frame, inertia about com in link frame)} from the URDF."""
    root = ET.parse(piper_desc(urdf)).getroot()
    out = {}
    for link in root.findall("link"):
        i = link.find("inertial")
        if i is None:
            continue
        o = i.find("origin")
        R = _rpy(*map(float, o.get("rpy", "0 0 0").split()))
        c = np.array(list(map(float, o.get("xyz").split())))
        I = i.find("inertia")
        v = {k: float(I.get(k)) for k in ("ixx", "iyy", "izz", "ixy", "ixz", "iyz")}
        In = np.array([[v["ixx"], v["ixy"], v["ixz"]], [v["ixy"], v["iyy"], v["iyz"]], [v["ixz"], v["iyz"], v["izz"]]])
        out[link.get("name")] = (float(i.find("mass").get("value")), c, R @ In @ R.T)
    return out


def piper_desc(urdf):
    from piper_fk import fetch_description
    return fetch_description() / urdf


class ArmLoads:
    URDF = "urdf/piper_description.urdf"

    def __init__(self, payload=PAYLOAD):
        self.piper = Piper(self.URDF)
        self.inert = inertials(self.piper, self.URDF)
        self.payload = payload
        self.q_reach = self.full_reach()

    def full_reach(self):
        """J2, J3, J5 that push the fingertip furthest out horizontally (J1 = J4 = J6 = 0)."""
        lim = self.piper.limits

        def neg_reach(v):
            q = np.array([0, v[0], v[1], 0, v[2], 0])
            return -self.piper.tip(q)[0]

        best = None
        for q2 in np.radians([60, 80, 100]):
            for q3 in np.radians([-20, -60]):
                r = minimize(neg_reach, [q2, q3, 0.0], method="L-BFGS-B",
                             bounds=[lim["joint2"], lim["joint3"], lim["joint5"]])
                if best is None or r.fun < best.fun:
                    best = r
        return np.array([0, best.x[0], best.x[1], 0, best.x[2], 0])

    def bodies(self, q, payload=True):
        """[(mass, com, inertia about com), ...] in the base frame, plus the payload at the tip."""
        poses = self.piper.fk(q, grip=0.0)
        out = []
        for name, (m, c, In) in self.inert.items():
            if name not in poses:
                continue
            T = poses[name]
            R = T[:3, :3]
            out.append((m, T[:3, :3] @ c + T[:3, 3], R @ In @ R.T))
        if payload and self.payload:
            out.append((self.payload, self.piper.tip(q), np.zeros((3, 3))))
        return out

    def wrench(self, q, acc=lambda r: np.zeros(3), spin=(np.zeros(3), np.zeros(3)), payload=True):
        """Force and moment the arm puts on the deck at the base origin.

        acc(r) gives each body's acceleration from its position; spin = (omega, alpha) of the moving
        links about the base, used for the link inertia terms."""
        w, a = spin
        F, M = np.zeros(3), np.zeros(3)
        for m, r, I in self.bodies(q, payload):
            f = m * (acc(r) - np.array([0, 0, -G]))       # what the deck must supply to this body
            F += f
            M += np.cross(r, f) + I @ a + np.cross(w, I @ w)
        return -F, -M

    def cases(self):
        q = self.q_reach
        tip = self.piper.tip(q)
        z = np.array([0, 0, 1.0])
        shoulder = self.piper.fk(q)["link2"][:3, 3]
        out = {}
        out["static"] = self.wrench(q)
        out["static, arm only"] = self.wrench(q, payload=False)
        # J1 braking from full speed: centripetal plus tangential, the worst instant of a swing
        w, a = OMEGA_J1 * z, ALPHA_MAX * z
        out["J1 swing, braking from 180 deg/s"] = self.wrench(
            q, acc=lambda r: np.cross(a, r) + np.cross(w, np.cross(w, r)), spin=(w, a))
        # J2 lifting the stretched arm at the full acceleration (about the shoulder's axis, +y here)
        ax = self.piper.fk(q)["link2"][:3, 2]
        ax = ax * np.sign(np.cross(ax, tip - shoulder)[2] or 1)      # the sense that lifts the tip
        a2 = ALPHA_MAX * ax
        out["J2 lift, full acceleration"] = self.wrench(
            q, acc=lambda r: np.cross(a2, r - shoulder), spin=(np.zeros(3), a2))
        self.tip, self.shoulder = tip, shoulder
        return out


def report():
    L = ArmLoads()
    c = L.cases()
    q = np.degrees(L.q_reach).round(1)
    mass = sum(m for m, _, _ in L.bodies(L.q_reach))
    print(f"full-reach pose (deg): {q}, fingertip at {L.tip.round(3)} m, total moving mass {mass:.2f} kg")
    for k, (F, M) in c.items():
        print(f"{k:34s} F = {F.round(1)} N   M = {M.round(2)} N·m")
    return L, c


if __name__ == "__main__":
    report()
