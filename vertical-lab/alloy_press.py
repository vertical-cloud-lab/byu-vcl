"""The vacuum press in chapter 1 of the alloy route (#303): ``vacuum_press.py``'s Specac Atlas Autotouch 15T with the
lab's evacuable die round #222's F1 sleeve, standing on tray B and served by the arm. It replaces the assumed electric
press of ``charge.press_parts()``.

Sterling, on PR #318 (2026-11-04): "the plug is supposed to be pushed in all the way such that the powder gets
compressed to a certain tonnage. Also, it would be better if it were a vacuum press." So:

* **The bore is filled up to where the plug is set**, its lead-in in the mouth, 8.03 mm proud of the rim. The
  alloying powder goes in first (Si, Ni), then a top-up of the cup's own metal: AlSi10Mg for the 5N Al cups, Cu for
  the OFE Cu cups. ``charge.RUNS``' doses alone stand 18 mm (Si) and 25 mm (Ni) below the set plug, so pressing the
  plug flush on them compacted nothing (``vacuum_press.runs_vs_set_line``). The doses are solved so that each run keeps
  its 10 wt %: AlSi10Mg is itself 10 % Si, so the Si dose is unchanged; for Cu-10Ni the Ni goes up to make room for Cu.
* **The press works under vacuum.** The die is pumped down below 1 mbar through its port, then the press drives the
  plug the 8.03 mm to flush on a 3.2 t program (load on the powder plus #222's 2 t reserve for the plug's press fit;
  ``vacuum_press.compaction``). Pressed with no air in it, the compact has none to throw molten metal out of the cup
  when it melts (DAL #140).
* **What the arm does.** It sets the cup on the die's ejector pin at the shuttle's out position, its bottom 10 mm in
  the catch ring on F1 (``vacuum_press.CATCH``), so the cup stands in a socket rather than on a bare pin, with its plug
  already in the mouth (set at the rack). The pin lowers the cup into F1: the gripper can't follow it into the die. Then
  it sets the punch, from a rest beside the press, into the die on the plug. The shuttle carries the die in, the guard
  closes, the press runs, the die is vented with dry Ar and comes back out; the arm puts the punch back on its rest,
  the pin pushes the cup back up into the catch ring, and the arm lifts it out.

Press frame (``vacuum_press``): origin on the tray floor at the centre of the press's footprint, z up, front = -y.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pyvista as pv

import charge as C
import vacuum_press as VPm
from scene import T

HERE = Path(__file__).resolve().parent
PRESS_AT = (-620.0, -50.0)              # tray B frame: the press's frame origin. Pump at x = -1180, stand front -411
REST_LOCAL = (150.0, -300.0)            # the punch's rest, press frame: in front of the control tower
REST_TOP = VPm.Z_PISTON                 # the rest's top: the punch stands in a pocket in it, flange up
REST_POCKET = VPm.GUIDE                 # its nose in the pocket, its collar on the rest's top (as on the catch ring)
GRIP_FLANGE = 0.455                     # 2F-85 closure on the punch's 50 mm flange, held level from the front:
#                                         gap = 28 - 90 (c - 0.70)
OPEN_FLANGE = 0.12
TOPUP = {"Al": ("AlSi10Mg", "Al", 0.10), "Cu": ("Cu", "Cu", 0.0)}   # top-up name, charge.POWDERS key, its share of
#                                         the alloying element (AlSi10Mg: Si 9-11 %, EOS; Cu powder: no Ni)
TOPUP_MODULE = {"Al": 0, "Cu": 8}       # carousel modules (0-based) holding the two top-ups
TOPUP_COL = {"AlSi10Mg": (0.70, 0.71, 0.74), "Cu": (0.72, 0.42, 0.26)}
SET_T = None                            # filled from vacuum_press.compaction() at import


# ------------------------------------------------------------------------------------------------ the recipe
def heights(v_cm3: float) -> float:
    """Height above the straight bore's floor of a powder column of volume v (cm3) filled from the drill point."""
    a = VPm.bore_area()
    return (v_cm3 * 1000.0 - a * C.drill_point_h(C.CUP_BORE_D) / 3) / a


def pressed_recipe() -> dict:
    """Each run's doses with the bore tapped full to the set plug, keeping the run's wt %, and what pressing to flush
    makes of them. Two linear equations per cup: the alloying element's share, and the tapped volumes adding up to the
    cavity under the set plug (#222's tapped densities; mixing is not assumed to pack any closer)."""
    vol = C.volumes()
    v_set = VPm.cavity(VPm.PLUG_SET) / 1000.0
    v_flush = VPm.cavity(C.PLUG_HOME_Z) / 1000.0
    solid = dict(VPm.SOLID, Cu=8.96, Al=2.67)
    runs = {}
    for name, (metal, pw, wt, n) in C.RUNS.items():
        host = (vol["cup"] + vol["plug"]) * C.RHO[metal]
        top, key, f = TOPUP[metal]
        ra, rb = C.POWDERS[pw][1], C.POWDERS[key][1]
        w = wt / 100.0
        A = np.array([[1.0 - w, f - w], [1.0 / ra, 1.0 / rb]])
        m_pw, m_top = np.linalg.solve(A, np.array([w * host, v_set]))
        h1 = heights(m_pw / ra)
        h2 = heights(v_set)
        s_vol = m_pw / solid[pw] + m_top / solid["AlSi10Mg" if top == "AlSi10Mg" else "Cu"]
        el = m_pw + f * m_top
        total = host + m_pw + m_top
        runs[name] = dict(cups=n, cup_metal=metal, alloying=pw, alloying_g=round(float(m_pw), 2), top_up=top,
                          top_up_g=round(float(m_top), 2), column_mm_alloying=round(h1, 1),
                          column_mm_set=round(h2, 1), column_mm_flush=round(heights(v_flush), 1),
                          rel_density_set=round(s_vol / v_set, 3), rel_density_flush=round(s_vol / v_flush, 3),
                          cup_plus_plug_g=round(host, 2), charged_cup_g=round(total, 2),
                          run_g=round(n * total, 1), wt_pct=round(100 * el / total, 2),
                          was_g=round(float(C.recipe()["runs"][name]["cups"][0]["powder_g"]), 2))
    comp = VPm.compaction()
    return dict(set_point_t=comp["set_point_t"], set_point_kN=comp["set_point_kN"],
                plug_travel_mm=round(VPm.TRAVEL, 2), cavity_set_cm3=round(v_set, 3), cavity_flush_cm3=round(v_flush, 3),
                runs=runs,
                note="Bore tapped full to the set plug: the alloying powder, then the cup's own metal on top (AlSi10Mg "
                     "is 10 % Si, so the Al-10Si cups keep the Si dose; the Cu-10Ni cups take more Ni to make room for "
                     "the Cu). The press drives the plug to flush on a 3.2 t program under vacuum; F1 stops it there, "
                     "so the dose sets the green density. The set point comes from vacuum_press.compaction(), a Heckel "
                     "line through #222's E4 estimate for AlSi10Mg; Si and Ni are not calibrated, and a Si layer is "
                     "harder to compact, so check the plug reaches flush on the first cups.")


SET_T = VPm.compaction()["set_point_t"]


# ------------------------------------------------------------------------------------------------ the press
class VacPress:
    """The press on tray B, its die, the punch's rest, and their state: guard (0 shut .. 1 up), shuttle y (press
    frame), ram (mm), pin (mm above its seat), the punch (on its rest, held, or in the die), vacuum (mbar), load (t)."""

    def __init__(self, sc, parent="tray_B", at=PRESS_AT, z0=0.0):
        self.sc = sc
        parts = VPm.press_parts()
        cut = VPm.die_parts(cut=True)
        for g in ("fixed", "screen", "vacuum"):
            for k, (m, col) in parts[g].items():
                sc.add(f"vpress/{g}/{k}", m, col, "vpress", specular=0.25 if g != "vacuum" else 0.15)
        sc.parent["vpress"] = parent
        sc.gmat["vpress"] = T((at[0], at[1], z0))
        for k, (m, col) in parts["guard"].items():
            sc.add(f"vpress/guard/{k}", m, col, "vp_guard", opacity=VPm.PETG_ALPHA if k == "panel" else 1.0,
                   specular=0.5)
        sc.add("vpress/ram", parts["ram"]["piston"][0], VPm.BRIGHT, "vp_ram", specular=0.6)
        for k, (m, col) in parts["shuttle"].items():
            sc.add(f"vpress/sh/{k}", m, col, "vp_shuttle", specular=0.5)
        sc.add("vpress/sh/body_cut", cut["body"], C.STEEL, "vp_shuttle", specular=0.5, shown=False)
        sc.add("vpress/sh/f1_cut", cut["f1"], (0.47, 0.48, 0.52), "vp_shuttle", specular=0.5, shown=False)
        sc.add("vpress/sh/catch_cut", cut["catch"], VPm.CATCH_C, "vp_shuttle", specular=0.5, shown=False)
        sc.add("vpress/sh/hole", cut["hole"], VPm.DARK, "vp_shuttle", shown=False)
        sc.add("vpress/pin", parts["pin"]["pin"][0], VPm.BRIGHT, "vp_pin", specular=0.5)
        sc.add("vpress/pin_cut", cut["pin"].translate((0, 0, VPm.CUP_BASE), inplace=False), VPm.BRIGHT, "vp_pin",
               specular=0.5, shown=False)
        sc.add("vpress/ejector", parts["ejector"]["rod"][0], VPm.BRIGHT, "vp_ej", specular=0.5)
        sc.add("vpress/punch", parts["punch"]["punch"][0], VPm.TOOL, "vp_punch", specular=0.5)
        sc.add("vpress/punch_cut", cut["punch"], VPm.TOOL, "vp_punch", specular=0.5, shown=False)
        sc.add("vpress/oring", parts["punch"]["oring"][0], VPm.DARK, "vp_punch")
        sc.add("vpress/oring_cut", cut["oring"], VPm.DARK, "vp_punch", shown=False)
        # the punch's rest: a post with a pocket for the punch's nose; its collar sits on the post's top, flange up
        rx, ry = REST_LOCAL
        rest = C._cylz(20.0, 0.0, REST_TOP, rx, ry).merge(C._box(rx - 45, rx + 45, ry - 45, ry + 45, 0, 10))
        sc.add("vpress/rest", rest, C.PRINT, "vpress", specular=0.2)
        sc.add("vpress/rest_rim", C._ring(VPm.NOSE_R + 3.2, VPm.NOSE_R + 0.5, REST_TOP - 0.3, REST_TOP + 0.6, rx, ry),
               (0.08, 0.40, 0.40), "vpress")
        sc.add("vpress/hose", VPm.hose((0, 0, 300)), VPm.BRIGHT, "vpress", specular=0.4)
        sc.add("vpress/air", pv.PolyData(np.zeros((30, 3))), (0.35, 0.65, 0.95), "vpress", shown=False,
               style="points", point_size=5.0, render_points_as_spheres=True)
        for g in ("vp_guard", "vp_ram", "vp_shuttle", "vp_ej"):
            sc.parent[g] = "vpress"
        sc.parent["vp_pin"] = "vp_shuttle"
        self.st = dict(guard=1.0, y=VPm.Y_OUT, ram=0.0, e=VPm.VP["eject"], x=0.0, mbar=1013.0, load=0.0)
        self.punch_at = "rest"              # "rest", "die" or "held"
        self.cutaway = False
        self._hose_key = None
        self.punch_rest()
        self.apply()

    # ----------------------------------------------------------------------------------------------- state
    def apply(self):
        sc, st = self.sc, self.st
        sc.gmat["vp_guard"] = T((0, 0, st["guard"] * VPm.GUARD_OPEN))
        sc.gmat["vp_ram"] = T((0, 0, st["ram"]))
        sc.gmat["vp_shuttle"] = T((VPm.AXX, st["y"], VPm.Z_PISTON + st["ram"]))
        sc.gmat["vp_pin"] = T((0, 0, st["e"]))
        sc.gmat["vp_ej"] = T((VPm.AXX, VPm.Y_OUT, VPm.Z_PISTON + (st["e"] if st["y"] < VPm.Y_OUT + 5 else 0.0)))
        if self.punch_at == "die":
            sc.gmat["vp_punch"] = T((0, 0, VPm.PUNCH_SET - st["x"]))
        key = (round(st["y"], 2), round(st["ram"], 2))
        if key != self._hose_key:
            self._hose_key = key
            port = (sc.gmat["vp_shuttle"] @ np.r_[VPm.VP["port_local"], 1.0])[:3]
            sc.set_mesh("vpress/hose", VPm.hose(port))
        for whole, half in (("vpress/sh/body", "vpress/sh/body_cut"), ("vpress/sh/f1", "vpress/sh/f1_cut"),
                            ("vpress/sh/catch", "vpress/sh/catch_cut"), ("vpress/pin", "vpress/pin_cut"),
                            ("vpress/punch", "vpress/punch_cut"), ("vpress/oring", "vpress/oring_cut")):
            sc.alpha[whole] = 0.0 if self.cutaway else 1.0
            sc.alpha[half] = 1.0 if self.cutaway else 0.0
        sc.alpha["vpress/sh/hole"] = 1.0 if self.cutaway else 0.0

    def to(self, **kw):
        start = {k: self.st[k] for k in kw}

        def up(u):
            for k, v in kw.items():
                self.st[k] = start[k] + (v - start[k]) * u
            self.apply()
        return up

    def punch_rest(self):
        self.sc.parent["vp_punch"] = "vpress"
        self.sc.gmat["vp_punch"] = T((*REST_LOCAL, REST_TOP - REST_POCKET))
        self.punch_at = "rest"

    def punch_into_die(self):
        """Re-parent the punch to the die (after the arm lets go of it there)."""
        self.sc.parent["vp_punch"] = "vp_shuttle"
        self.punch_at = "die"
        self.apply()

    # ----------------------------------------------------------------------------------------- places (world)
    def world(self, group: str, p) -> np.ndarray:
        return (self.sc.world(group) @ np.r_[np.asarray(p, float), 1.0])[:3]

    def cup_seat(self) -> np.ndarray:
        """Base centre of a cup standing on the pin, as the pin is now (world)."""
        return self.world("vp_pin", (0.0, 0.0, VPm.CUP_BASE))

    def cup_seat_at(self, e: float) -> np.ndarray:
        """... with the shuttle out and the pin at e."""
        return self.world("vpress", (VPm.AXX, VPm.Y_OUT, VPm.Z_PISTON + VPm.CUP_BASE + e))

    def punch_grasp_rest(self) -> np.ndarray:
        """The grasp point on the flange of the punch on its rest (world)."""
        return self.world("vpress", (*REST_LOCAL, REST_TOP - REST_POCKET + VPm.PUNCH_L + VPm.FLANGE_T / 2))

    def punch_grasp_die(self) -> np.ndarray:
        """The same on a punch standing on the set plug in the die, shuttle out (world)."""
        return self.world("vpress", (VPm.AXX, VPm.Y_OUT, VPm.Z_PISTON + VPm.PUNCH_SET + VPm.PUNCH_L + VPm.FLANGE_T / 2))

    def die_top(self) -> np.ndarray:
        return self.world("vp_shuttle", (0.0, 0.0, VPm.BODY_TOP))

    def air(self, cup_group: str, u: float, plug_z: float):
        """Air leaving the cup on pump-down: up the vent, along the plug's channel, out of the port, down the hose."""
        sc = self.sc
        cup = sc.world(cup_group)
        top = plug_z + C.PLUG_L + 0.3
        path = [(0, 0, plug_z - 10), (0, 0, top), (0, C.CUP_BORE_D / 2 - 0.5, top), (-3.0, 7.6, C.SLUG_L + 1.5),
                (-VPm.RING_D / 2 + 0.6, 0, VPm.PORT_Z - VPm.CUP_BASE),
                (-VPm.BODY_R - 18, 0, VPm.PORT_Z - VPm.CUP_BASE)]
        P = [(cup @ np.r_[p, 1.0])[:3] for p in path]
        port = (sc.gmat["vp_shuttle"] @ np.r_[VPm.VP["port_local"], 1.0])[:3]
        W = sc.world("vpress")
        line = VPm.hose_line(port)
        P += [(W @ np.r_[q, 1.0])[:3] for q in line.points[4::8]]
        k = np.arange(30)
        s = (k / 30 + u * 2.5) % 1.0
        seg = np.minimum((s * (len(P) - 1)).astype(int), len(P) - 2)
        f = s * (len(P) - 1) - seg
        pts = np.array([P[i] + (P[i + 1] - P[i]) * t for i, t in zip(seg, f)])
        inv = np.linalg.inv(W)
        sc.set_mesh("vpress/air", pv.PolyData(pts @ inv[:3, :3].T + inv[:3, 3]))

    def gauge(self) -> str:
        st = self.st
        vac = f"{st['mbar']:.0f} mbar" if st["mbar"] >= 10 else f"{st['mbar']:.1f} mbar"
        return f"{st['load']:.1f} t of {SET_T:.1f} t, {vac}, guard {'up' if st['guard'] > 0.5 else 'down'}"


def write_recipe():
    r = pressed_recipe()
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "alloy_recipe_pressed.json").write_text(json.dumps(r, indent=1) + "\n")
    return r


if __name__ == "__main__":
    print(json.dumps(write_recipe(), indent=1))
