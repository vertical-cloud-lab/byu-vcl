"""Scaling up (#303, PR #318, round 8): the alloy that passed the route goes to a large-format printer that builds real
aerospace parts, and to a robot DED cell that repairs real ship parts.

    VIZ3D_FPS=8 xvfb-run --server-num=17 -a python3 scaleup.py          # -> out/scaleup.{gif,json}, out/mp4/scaleup.mp4,
                                                                         #    out/scaleup_still.png
    PREVIEW=1 xvfb-run --server-num=17 -a python3 scaleup.py             # the last frame of each step -> /tmp

The machines are ``r8_scale.py``'s: an EOS M 400-4 (laser powder-bed fusion, 400 x 400 x 400 mm, four 400 W lasers) and
a Meltio Robot Cell with its Blue Laser Engine (wire-laser DED, 1 kW at 450 nm, an ABB robot and a two-axis positioner
rated for 500 kg), with the lab's own InssTek MX-Lab beside them for scale (``instruments_lab.ded``). They stand on a
plain floor here; where they would stand in the lab is ``r8_scale.FLOOR_PLACEMENT``.

The two jobs are real ones with public figures (``r8_scale.SOURCES``): the build of EOS's RUAG Space case study, two
Sentinel-1 antenna brackets and 30 tensile specimens in AlSi10Mg (the brackets' shape is ours: RUAG's isn't public),
and a nickel aluminium bronze propeller after the WAAMpeller of Damen and RAMLAB (1350 mm, about 400 kg; the blade
geometry is a standard-series estimate, the damage and the beads illustrative). The build grows by cutting the parts'
meshes at the layer height every frame; the repair's beads appear segment by segment as the robot lays them, on the
cell's own timeline (``r8_scale.repair_program``).

No UR arm moves here, so there is nothing for ``ARM_AUDIT``; the cell's robot is checked against the blade by
``check_head()`` (the head's least clearance to the propeller over the whole program, printed when the chapter runs).
"""
from __future__ import annotations

import math
import types

import numpy as np
import pyvista as pv
from PIL import ImageDraw

import r8_scale as S8
import tour
from scene import FPS, PREVIEW, Scene, T, R, font, window

TITLE = "Scaling up: large-format printing and ship-part repair"
XC = 5500.0                  # the Meltio cell's centre, right of the EOS
XD = -3400.0                 # the MX-Lab, left of it, for scale
SAW = dict(dx=1250.0, dy=-1800.0, dz=-90.0, table=(900.0, 700.0, 900.0))   # the plate's last offset: onto the saw table

# powder: the lab's figures (alloy_atomize.K7M2Q9, MIDI_BUILDS) and the EOS bed, an estimate
RUN_FINES_G = 187.973        # DAL #219: one rePowder run, < 63 um (1079.886 g charged)
MIDI_BUILD_G = 440.0         # the lab's planning figure for an Aconity MIDI build
BULK = 1.4                   # g/cm3, AlSi10Mg powder bed (an estimate)
EOS_BED_G = 400.0 * 400.0 * S8.EOS["Hb"] / 1000.0 * BULK


def check_head(cell_inst, tl, n=400) -> float:
    """The least distance (mm) from the printhead's box and nozzle to the propeller's points over the program."""
    prop = cell_inst.meshes["prop"][0][0]
    pts = np.asarray(prop.points)
    bx, by, zs, Lt = S8._cell_k()
    worst = 1e9
    T_ = tl.t[-1]
    for v in np.linspace(0.0, 1.0, n):
        q = [float(np.interp(v * T_, tl.t, [s["q"][i] for s in tl.states])) for i in range(4)]
        tilt = float(np.interp(v * T_, tl.t, [s["tilt"] for s in tl.states]))
        M = S8.prop_mount(tilt) @ np.linalg.inv(S8.prop_mount(0.0))
        P = pts @ M[:3, :3].T + M[:3, 3]
        fk = S8.robot_fk(q)
        tip = fk["tip"]
        c = S8.CELL
        # the head box: 262 x 272, from 90 mm over the nozzle's tip to the flange (it stays vertical)
        z0 = tip[2] + c["stand"] + 90.0
        near = P[(np.abs(P[:, 0] - tip[0]) < 400) & (np.abs(P[:, 1] - tip[1]) < 400)]
        if len(near):
            dx = np.maximum(np.abs(near[:, 0] - tip[0]) - 131, 0)
            dy = np.maximum(np.abs(near[:, 1] - tip[1]) - 136, 0)
            dz = np.maximum(z0 - near[:, 2], 0)
            worst = min(worst, float(np.sqrt(dx ** 2 + dy ** 2 + dz ** 2).min()))
    return worst


def main():
    data = tour.load(["eos_m400", "meltio_cell", "ded"])
    eos_i, eos_e = data["eos_m400"]
    cell_i, cell_e = data["meltio_cell"]
    sc = Scene("scaleup", TITLE)
    sc.intro = 1.0
    tour.studio(sc, size=40000.0, at=(1500.0, -2000.0))
    E = tour.Rig(sc, eos_i, eos_e, "eos:")
    C = tour.Rig(sc, cell_i, cell_e, "cell:", at=T((XC, 0, 0)))
    tour.contact_shadow(sc, eos_i.bbox(), name="shadow eos")
    bb = cell_i.bbox()
    tour.contact_shadow(sc, (bb[0] + XC, bb[1] + XC, bb[2], bb[3]), name="shadow cell")
    if "ded" in data:
        di, de = data["ded"]
        Dm = tour.Rig(sc, di, de, "mx:", at=T((XD, 0, 0)))
        bb = di.bbox()
        tour.contact_shadow(sc, (bb[0] + XD, bb[1] + XD, bb[2], bb[3]), name="shadow mx")
        for piece in [p for p in Dm.names if p in di.props]:       # the MX-Lab's substrate and beads: not here
            for nm in Dm.names[piece]:
                sc.alpha[nm] = 0.0
    g = S8.eos_geometry()
    cx, cy, P, Hb = g["cx"], g["cy"], g["P"], g["Hb"]

    # ---- the build, drawn by cutting the parts at the layer height (in the plate's frame), the powder cake, beams
    parts = S8.eos_build_parts(g)
    full = {k: m for k, (m, _) in parts.items()}
    sc.add("build/bars", full["bars"], S8.ALSI_C, "eos:load", specular=0.55)
    sc.add("build/brackets", full["brackets"], S8.ALSI_C, "eos:lift", specular=0.55)
    sc.parent["eos:lift"] = "eos:load"
    sc.add("build/cake", pv.Box(bounds=(cx - 196, cx + 196, cy - 196, cy + 196, P, P + 1)), (0.55, 0.56, 0.58),
           "eos:load", opacity=0.32, specular=0.05)
    verts = np.vstack([np.asarray(m.points) for m in full.values()])
    for k in range(4):
        sc.add(f"beam{k}", pv.Line((0, 0, 0), (0, 0, 1)).tube(radius=2.5), (0.95, 0.10, 0.08), "beams",
               opacity=0.85, ambient=0.9, diffuse=0.25)
        sc.add(f"pool{k}", pv.Sphere(radius=7, center=(0, 0, 0)), (1.0, 0.62, 0.15), "pools", ambient=0.95,
               diffuse=0.2)
    blade_w = pv.Box(bounds=(-12, 12, cy - 240, cy + 240, P + 1, P + 3))
    sc.add("saw/band", blade_w, (0.55, 0.57, 0.62), "saw", specular=0.8)
    sc.parent["saw"] = "eos:load"
    tw, td, th = SAW["table"]
    tx, ty = cx + SAW["dx"], cy + SAW["dy"]
    table = [pv.Box(bounds=(tx - tw / 2, tx + tw / 2, ty - td / 2, ty + td / 2, th - 40, th))]
    table += [pv.Box(bounds=(x - 25, x + 25, y - 25, y + 25, 0, th - 40)) for x in (tx - tw / 2 + 40, tx + tw / 2 - 40)
              for y in (ty - td / 2 + 40, ty + td / 2 - 40)]
    sc.add("saw table", table[0].merge(table[1:]), (0.32, 0.33, 0.36), "static", specular=0.3)
    rng = np.random.default_rng(7)
    state = dict(f=0.0, beams=0.0, lift=0.0, saw=-1.0, out=0.0, plate=0.0)
    plate_names = E.names["load"] + ["build/bars", "build/brackets"]

    def eos_apply():
        f = state["f"]
        E.apply()
        o = state["out"]
        if o > 0:                     # past the load path's start: on to the saw table
            sc.gmat["eos:load"] = E.inst.joints["load"].matrix(0.0) @ T((SAW["dx"] * o, (SAW["dy"] + 1300) * o,
                                                                        (SAW["dz"] - 160) * o))
        h = P + f * Hb
        if f < 1.0:
            for k, m in full.items():
                name = "build/" + k
                cut = m.clip(normal=(0, 0, 1), origin=(0, 0, h), invert=True) if f > 0 else pv.PolyData()
                sc.set_mesh(name, cut if cut.n_points else pv.Sphere(radius=0.01, center=(cx, cy, P - 5)))
        else:
            for k, m in full.items():
                sc.set_mesh("build/" + k, m)
        top = P + max(f, 0.004) * Hb
        sc.set_mesh("build/cake", pv.Box(bounds=(cx - 196, cx + 196, cy - 196, cy + 196, P, top)))
        sc.show(["build/cake"], state.get("cake", 1.0))
        L = state["lift"]
        sc.gmat["eos:lift"] = T((0, -120 * L, 260 * L)) @ R((0, 0, 1), 20 * L, (cx, cy, P)) @ R((1, 0, 0), -22 * L,
                                                                                                (cx, cy, P + 50))
        s = state["saw"]
        sc.show(["saw/band"], 1.0 if s >= 0 else 0.0)
        sc.gmat["saw"] = T((cx - 280 + 560 * max(s, 0.0), 0, 0))
        sc.show(plate_names, state["plate"])
        # the beams: each scanner to a point of the layer being melted
        on = state["beams"]
        Wl = sc.world("eos:load")
        hl = h
        near = verts[np.abs(verts[:, 2] - hl) < 3.0]
        for k, (sx, sy, sz) in enumerate(g["scanners"]):
            if on > 0.5 and len(near):
                p = near[rng.integers(len(near))]
                pw = (Wl @ np.append(p, 1.0))[:3]
                a = np.array([sx, sy, sz - 4])
                sc.set_mesh(f"beam{k}", pv.Line(a, pw).tube(radius=2.5, n_sides=8))
                sc.gmat["pools"] = np.eye(4)
                sc.set_mesh(f"pool{k}", pv.Sphere(radius=7, center=pw, theta_resolution=10, phi_resolution=10))
                sc.show([f"beam{k}", f"pool{k}"], 1.0)
            else:
                sc.show([f"beam{k}", f"pool{k}"], 0.0)

    # ---- the repair program
    tl, beads, tilt = S8.repair_program()
    Tt = tl.t[-1]
    mk = {k: tl.t[i] / Tt for k, i in tl.marks.items()}
    prog = [k for k in cell_i.joints if k in ("tilt", "j1", "j2", "j3", "j5", "glow", "patch") or k.startswith("bead")]
    clear = check_head(cell_i, tl)
    print(f"the printhead's least clearance to the propeller over the program: {clear:.0f} mm", flush=True)

    def cell_prog(v):
        for k in prog:
            C.v[k] = v
        C.apply()

    # the repair zone, in the world: the beads' centre with the edge turned up
    allp = np.vstack([s for segs, _ in beads for s in segs])
    zone = (S8.prop_mount(tilt) @ np.append(allp.mean(0), 1.0))[:3] + (XC, 0, 0)
    zone0 = (S8.prop_mount(0.0) @ np.append(allp.mean(0), 1.0))[:3] + (XC, 0, 0)

    # ---- overlay: a panel of numbers, top right
    sc.panel = []
    base_overlay = sc.overlay

    def overlay(self, img, scale, anchors):
        img = base_overlay(img, scale, anchors)
        if not self.panel:
            return img
        s = max(scale, 0.80)
        d = ImageDraw.Draw(img, "RGBA")
        W_ = img.size[0]
        f1, f2 = font(14 * s, bold=True), font(13 * s)
        head, rows = self.panel[0], self.panel[1:]
        wmax = max([d.textlength(head, font=f1)] + [d.textlength(r, font=f2) for r in rows])
        x0, y0 = W_ - wmax - 34 * s, 46 * s
        h = 26 * s + 19 * s * len(rows)
        d.rounded_rectangle((x0, y0, W_ - 10 * s, y0 + h), 6 * s, fill=(255, 255, 255, 232), outline=(150, 156, 164))
        d.text((x0 + 12 * s, y0 + 6 * s), head, font=f1, fill=(20, 20, 24))
        for i, r in enumerate(rows):
            col = (150, 40, 30) if r.startswith("*") else (40, 42, 48)
            d.text((x0 + 12 * s, y0 + 26 * s + 19 * s * i), r.lstrip("*"), font=f2, fill=col)
        return img
    sc.overlay = types.MethodType(overlay, sc)

    # ---- cameras
    CAM_WIDE = [(2600, -15200, 5600), (1900, -300, 1000), (0, 0, 1)]
    CAM_EOS = [(1400, -5600, 2500), (-700, -500, 1200), (0, 0, 1)]
    CAM_CH = [(-150, -2350, 1750), (cx, cy, P + 40), (0, 0, 1)]
    CAM_CH2 = [(-1750, -2150, 1850), (cx, cy, P + 30), (0, 0, 1)]
    CAM_OUT = [(600, -3900, 2300), (cx, cy - 1300, 1050), (0, 0, 1)]
    CAM_SAW = [(-150, -3350, 1700), (tx, ty, th + 60), (0, 0, 1)]
    CAM_CELL = [(XC + 1500, -7400, 3200), (XC, 0, 1250), (0, 0, 1)]
    CAM_ZONE = [tuple(zone + (-80, -880, 330)), tuple(zone + (0, 0, 10)), (0, 0, 1)]
    CAM_ZONE2 = [tuple(zone + (420, -760, 420)), tuple(zone + (0, 0, 0)), (0, 0, 1)]
    CAM_ROBOT = [(XC - 300, -3900, 2300), (XC + 150, 200, 1350), (0, 0, 1)]
    sc.cam = CAM_WIDE
    n = 9
    E.v.update({"load": 0.0, "door": 0.0, "platform": 0.0, "recoater": 0.0})
    eos_apply()
    cell_prog(0.0)

    # 1. both machines
    sc.step(f"1/{n}", "Scaling up. The route proved an alloy gram by gram; parts that fly and sail need machines this "
            "size. An EOS M 400-4 prints by laser powder-bed fusion: 4.2 m long, 4.8 t, a 400 mm cube of build "
            "volume, four 400 W lasers. A Meltio Robot Cell repairs by wire-laser DED: 4.05 x 2.35 x 3.0 m. The "
            "lab's InssTek MX-Lab stands on the left for scale.", 6.5, None, hold=1.6, cam_to=CAM_WIDE,
            labels=[("EOS M 400-4", (-900, -806, 2355), (0.36, 0.16)),
                    ("Meltio Robot Cell", (XC, -1175, 3000), (0.80, 0.16)),
                    ("InssTek MX-Lab (in the lab)", (XD, -380, 1835), (0.10, 0.30))])

    # 2. the powder
    sc.panel = ["Powder, AlSi10Mg",
                f"one rePowder run, < 63 um      {RUN_FINES_G:7.0f} g   (DAL #219)",
                f"one Aconity MIDI build          {MIDI_BUILD_G:7.0f} g   (lab's figure)",
                f"EOS bed, 400 x 400 x {S8.EOS['Hb']:.0f} mm     {EOS_BED_G / 1000:7.1f} kg",
                f"*  = {EOS_BED_G / RUN_FINES_G:.0f} rePowder runs (bulk {BULK} g/cm3: an estimate)"]
    sc.step(f"2/{n}", "Powder first. The rePowder made 188 g under 63 um in one run; the Aconity MIDI builds on "
            "about 440 g. A 100 mm build in the EOS's 400 x 400 mm bed takes about 22 kg. So at this scale the "
            "recipe is what the route hands on, and the powder is bought by the 100 kg: EOS sells AlSi10Mg.", 5.5,
            None, hold=2.4, cam_to=CAM_EOS)

    # 3. the plate in
    sc.panel = []
    sc.step(f"3/{n}", "The chamber door opens, and a 400 mm build plate goes onto the platform.", 3.5,
            lambda u: (E.v.update(door=window(u, 0, 0.4), load=window(u, 0.45, 1.0)),
                       state.update(plate=1.0 if u > 0.42 else 0.0), eos_apply()), hold=0.4,
            cam_to=CAM_CH)
    sc.step(f"3/{n}", "Door shut; argon in. Drawn see-through from here.", 2.0,
            lambda u: (E.v.update({"door": 1 - u, "~body": 0.85 * u, "~door": 0.85 * u}), eos_apply()), hold=0.3)

    # 4. the build
    nsweep = 9

    def build(u):
        state["f"] = u
        k = u * nsweep
        ph = k - math.floor(k)
        state["beams"] = 1.0 if ph > 0.3 else 0.0
        rec = min(ph / 0.3, 1.0) if ph <= 0.3 else 1.0
        E.v["recoater"] = rec if int(k) % 2 == 0 else 1.0 - rec
        E.v["platform"] = u
        sc.gauges = [("layer", f"{int(u * 1667):5d} of 1667 at 60 um"), ("height", f"{u * Hb:5.1f} of {Hb:.0f} mm"),
                     ("lasers", "4 x 400 W, one field")]
        eos_apply()
    sc.step(f"4/{n}", "The build of EOS's RUAG Space case study: two Sentinel-1 antenna brackets (40 cm, AlSi10Mg, "
            "flight-qualified; this shape is ours, RUAG's isn't public) and 30 tensile bars. On the one-laser M 400 it "
            "took about 80 h at 60 um layers; here each recoat stands for about 185 layers.", 11.0,
            lambda u: build(0.5 * u), hold=0.0, cam_to=CAM_CH2)
    sc.step(f"4/{n}", "All four lasers reach the whole 400 x 400 mm field, so they can work on the same part at "
            "once: the M 400-4's case for speed. The powder around the parts (drawn see-through) holds them up.", 11.0,
            lambda u: build(0.5 + 0.5 * u), hold=0.0, cam_to=CAM_CH)
    state["f"] = 1.0
    state["beams"] = 0.0
    sc.gauges = []

    # 5. out of the powder, out of the door
    def unpack(u):
        E.v["platform"] = 1.0 - window(u, 0.0, 0.45)
        state["cake"] = 1.0 - window(u, 0.25, 0.55)
        E.v.update({"~body": 0.85 * (1 - window(u, 0.45, 0.65)), "~door": 0.85 * (1 - window(u, 0.45, 0.65)),
                    "door": window(u, 0.55, 0.8)})
        eos_apply()
    sc.step(f"5/{n}", "Done. The platform lifts the plate out of the powder, which is unpacked and sieved for reuse "
            "under argon in the setup station; the door opens.", 5.0, unpack, hold=0.3, cam_to=CAM_CH)

    def carry(u):
        E.v["load"] = 1.0 - window(u, 0.0, 0.6)
        state["out"] = window(u, 0.6, 1.0)
        eos_apply()
    sc.step(f"5/{n}", "The plate comes out to the saw. (AlSi10Mg builds are usually stress-relieved on the plate "
            "first.)", 4.0, carry, hold=0.3, cam_to=CAM_SAW)

    # 6. off the plate
    def cut(u):
        state["saw"] = window(u, 0.0, 0.55)
        state["lift"] = window(u, 0.6, 1.0)
        eos_apply()
    sc.step(f"6/{n}", "A band saw (drawn as its blade) parts the brackets from the plate, and they lift off: "
            "antenna brackets after RUAG Space's, 380 x 110 x 100 mm as drawn. The tensile bars stay for testing.",
            6.0, cut, hold=1.2,
            still=True,
            labels=[("antenna bracket, after RUAG Space\n(shape schematic)", (tx, ty, th + 330), (0.18, 0.28)),
                    ("30 tensile bars", (tx + 150, ty - 170, th + 60), (0.80, 0.62))])
    state["saw"] = -1.0
    eos_apply()

    # 7. the cell, the propeller, the damage
    def doors(u):
        C.v.update(door0=u, door1=u)
        C.apply()
    sc.step(f"7/{n}", "Ship parts. On the cell's positioner, a nickel aluminium bronze propeller after the "
            "WAAMpeller of Damen and RAMLAB: three blades, 1350 mm, about 400 kg, inside the positioner's 500 kg. "
            "One blade's leading edge is eroded, 30 mm deep (illustrative).", 5.0, doors, hold=0.6, cam_to=CAM_CELL,
            labels=[("NAB propeller, 1350 mm, ~400 kg", (XC + 780, -400, 1330), (0.80, 0.22)),
                    ("two-axis positioner", (XC + 1640, 120, 900), (0.84, 0.55)),
                    ("ABB robot, blue-laser head", (XC - 280, 120, 1700), (0.16, 0.24))])

    def tilt_up(u):
        cell_prog(window(u, 0.0, 1.0) * mk["tilted"])
        C.v.update(door0=1 - window(u, 0.0, 0.4), door1=1 - window(u, 0.0, 0.4))
        C.v.update({"~body": 0.85 * window(u, 0.2, 0.6), "~door0": 0.85 * window(u, 0.2, 0.6),
                    "~door1": 0.85 * window(u, 0.2, 0.6)})
        C.apply()
    sc.step(f"7/{n}", "Doors shut. The positioner tilts the propeller until the damaged edge faces up. Drawn "
            "see-through.", 4.0, tilt_up, hold=0.2, cam_to=CAM_ROBOT)
    sc.step(f"7/{n}", "Before: the notch, cut back to clean metal, about 120 mm along the edge.", 3.0, None,
            hold=1.0, cam_to=CAM_ZONE, labels=[("eroded leading edge", tuple(zone + (0, 0, 15)), (0.22, 0.30))])

    # 8. the repair
    def depo(u):
        cell_prog(mk["tilted"] + (mk["deposited"] - mk["tilted"]) * u)
    sc.step(f"8/{n}", "The robot brings the head down. 1 kW of blue light from nine 450 nm diodes melts the wire into "
            "the edge, pass on pass, each layer on the last (beads drawn about 2x). Copper alloys take blue light far "
            "better than infrared; Meltio lists copper alloys, and NAB filler wire is our assumption.", 20.0, depo,
            hold=0.4, cam_to=CAM_ZONE2)

    def home(u):
        cell_prog(mk["deposited"] + (mk["home"] - mk["deposited"]) * u)
    sc.step(f"8/{n}", "Head up, robot home. As deposited, the edge stands proud of the blade's profile.", 3.0, home,
            hold=0.6, cam_to=CAM_ZONE)

    # 9. machined back; what each machine takes
    sc.step(f"9/{n}", "After: machined back to the profile (on a mill or by hand, not in the cell), the edge whole "
            "again. US Navy suppliers already print NAB and copper-nickel parts by wire-arc DED (AML3D).", 3.0,
            lambda u: cell_prog(mk["home"] + (mk["machined"] - mk["home"]) * u), hold=1.6,
            labels=[("restored leading edge", tuple(zone + (0, 0, 15)), (0.22, 0.30))])
    sc.panel = ["What size of part each takes"] + [f"{k}: {v}" for k, v in S8.ENVELOPES.items()]
    sc.step(f"9/{n}", "From coupons to flight brackets and propellers: the lab's MX-Lab and Aconity MIDI qualify the "
            "alloy; the EOS builds parts up to a 400 mm cube; the cell repairs or builds metre-scale parts up to "
            "500 kg.", 6.0, lambda u: (cell_prog(mk["machined"] + (1.0 - mk["machined"]) * u),
                                       C.v.update({"~body": 0.85 * (1 - u), "~door0": 0.85 * (1 - u),
                                                   "~door1": 0.85 * (1 - u)}), C.apply()),
            hold=2.6, cam_to=CAM_WIDE, labels=[])
    print(sc.save())


if __name__ == "__main__":
    main()
