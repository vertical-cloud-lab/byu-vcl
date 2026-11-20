"""Safety assets for the vertical lab (#303, PR #318's stacked safety PR): a Class D extinguisher at every station that
handles metal powder, one riding on each MiR250, a wheeled Class D unit where the most powder is, and the signs,
hangers and agent pails that go with them. notes/safety.md has the sources, the placement rules and the checks.

Sterling, PR #318, 2026-11-20: "create a new PR focused on assets for safety. Class D fire extinguishers at each
station, etc. Focused primarily on faithful reconstruction / asset creation. Noting that we might even want to have a
class D fire extinguisher mounted at all times to the MiR250 and available for use, in addition to having these next
to each station that deals with powder."

The assets, each built part by part from the maker's own figures and pictures:

* **Amerex B570** (``b570_parts``): the lab's own Class D unit (DAL #126; Grainger 8C249, P/N 16882): 30 lb of Super D
  (sodium-chloride-based) powder, stored pressure, 195 psig, chrome-plated brass valve, the "soft flow" extension
  applicator. Amerex's datasheet gives 35 x 13 x 8 in overall; everything finer is measured off Amerex's own product
  render (the datasheet's picture, alpha mask and all) scaled to a 7.75 in cylinder, which makes the render 35.7 x
  12.7 in overall against the datasheet's 35 x 13, and checked against the lab's own photos of its unit.
* **Its wall hook** (``hook_parts``): the red J hook that ships with it ("BR VLV W/ WALL BKT" on the lab's box), after
  DAL's mounting study (lab-safety/class-d-extinguisher/model.py at DAL 9cc2f77), seated under the valve.
* **Model 811 heavy-duty vehicle bracket** (``bracket811_parts``): Amerex's box-type bracket, the one Buckeye sells as
  700229 "also identified as Model 811": for 30 lb Class D units, 7.5-8.5 in cylinders, 17.5 in tall, 8.125 in wide
  and deep, 9 lb, powder-coated carbon steel with rubber bushings and a quick-release strap (Buckeye's datasheet).
  It holds the B570 on the back of each MiR250 (``mir_mount``).
* **Amerex 680R** (``w680r_parts``): 150 lb Super D on 36 x 2.5 in steel wheels with non-sparking treads, argon
  cylinder (110 ft3) regulated to 125 psi, 25 ft x 0.75 in hose, extension wand; 52 x 28 x 45 in (Amerex's wheeled
  catalogue, p. 11). At the atomizer and at the EOS, where the most powder is.
* **Signs, a post, a pail** (``sign_parts``, ``post_parts``, ``pail_parts``): a 7 x 10 in CLASS D sign over each
  unit and a double-sided flag sign at 80 in (DAL's flag bracket); a floor-anchored strut post where a station has no
  wall (ours, from catalogue strut); a 50 lb pail of the same Super D agent with a scoop, for a small spill.

    python3 safety.py                    # sizes, the NFPA 10 checks, the MiR payload, the BoM -> out/safety.json
    xvfb-run -a python3 safety.py sheet  # the assets one by one -> out/safety_assets.png
    xvfb-run -a python3 safety.py photo  # the B570 beside Amerex's own render -> out/safety_b570_vs_amerex.png
    python3 safety.py plan               # the floor: every unit, the walk to it -> out/safety_plan.png
    xvfb-run -a python3 safety.py clip   # a short clip -> out/mp4/safety.mp4 (VIZ3D_HD=1: out/hd/safety.mp4)

The B570 rides on each MiR250 by default (``props.mir250``, CLASS_D_ON_MIR); ``VLAB_MIR_CLASS_D=0`` leaves it off.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
IN = 25.4
LB = 0.45359237

# ================================================================================================ what each part is
# Amerex B570, its own frame: the origin at the centre of the cylinder's bottom, z up, the label (its front) to -y, the
# applicator down its right side (+x), the hose's loop over the top in the x-z plane. Heights are from the bottom.
# Measured off Amerex's render (class-d-extinguishers.pdf, image 0, 493 x 1319 px with its alpha mask): the cylinder
# is 272 px across; at 7.75 in that is 35.1 px/in, and the whole thing then spans 35.7 x 12.7 in (datasheet: 35 x 13),
# so the 35 in height includes the hose's loop. A 7.75 in drawn-steel shell is also what the 811 bracket is sold for
# (7.5-8.5 in) and the datasheet's 8 in depth less the gauge.
B570 = dict(
    model="Amerex B570", part_no="16882", grainger="8C249", agent="Super D (sodium chloride based), 30 lb",
    d=7.75 * IN,            # cylinder, 196.9 mm
    z_wall=533.0,           # top of the straight wall (21.0 in)
    z_dome=575.0,           # top of the shell's head (22.65 in in the render)
    neck=(26.0, 575.0, 581.0),          # the yellow neck ring: radius, z0, z1
    collar=(20.0, 581.0, 605.0),        # the threaded collar the valve screws onto
    z_seat=605.0,           # the wall hook's seat, under the valve body
    z_gauge=621.0,          # the gauge's centre (24.4 in)
    z_lever=686.0,          # the squeeze lever's tip, the highest rigid point (27.0 in)
    z_hose=904.0,           # the top of the hose's coil (35.6 in)
    wand_x=119.0,           # the applicator's axis, 20.5 mm outside the shell
    bands=((272.0, 305.0), (466.0, 499.0)),   # the two black lattice bands that hold the applicator
    label=(337.0, 436.0),   # the instruction label (13.3-17.2 in)
    logo=(185.0, 207.0),    # the Amerex diamond (7.3-8.1 in)
    gross_lb=50.0,          # charged (DAL's mounting study: 53 lb shipping weight with the box)
    psig=195, range_ft=(3, 6), discharge_s=24, price_usd=958.01,
    source="Amerex Class D datasheet (amerex-fire.com/upl/downloads/library/class-d-extinguishers.pdf): B570 P/N 16882, "
           "30 lb Super D, 35 H x 13 W x 8 D in, 53 lb shipping, 195 psig, 3-6 ft, 24 s, chrome-plated brass valve, "
           "'soft flow' extension applicator, wall bracket; shapes and heights measured off the datasheet's render; "
           "Grainger 8C249 at $958.01 (DAL #126)")
# The 811 heavy-duty vehicle bracket (Buckeye 700229 = Model 811): its own frame has the back of its web at y = 0, the
# foot plate on z = 0 and the front to -y, so a B570 stands on the foot plate with its axis at y = -(BUSH + r).
B811 = dict(H=17.5 * IN, W=8.125 * IN, D=8.125 * IN, t=3.0, web=110.0, kg=9.0 * LB, z_strap=(311.0, 336.0),
            bush=4.0, price_usd=79.95,
            source="Buckeye datasheet 700229 / Model 811 (qrfs.com): cylinder 7.5-8.5 in, 17.50 x 8.125 x 8.125 in, "
                   "9 lb, powder-coated carbon steel, rubber bushings, UL 299, DOT, USCG; fits 30 lb Class D. Fire "
                   "Supply Depot lists the Amerex 811 at 9.75 W x 8.125 D x 17.5 H in with the strap's latch, "
                   "7/16 in holes, $79.95. Shape from Buckeye's photo; the web and flange split, the strap height and "
                   "the latch are read off it")
# The 680R: its own frame on the floor midway between the wheels, the axle along x, its front (the label) to -y.
W680 = dict(H=52 * IN, W=28 * IN, D=45 * IN, wheel=36 * IN, tread=2.5 * IN, agent_lb=150.0, ship_lb=444.0,
            hose_ft=25.0, hose_in=0.75, argon_ft3=110.0, psi=125, discharge_s=80, range_ft=(4, 8),
            d_agent=305.0, h_agent=880.0, d_argon=178.0, h_argon=960.0, price_usd=11541.0, list_usd=16589.79,
            source="Amerex wheeled catalogue (wheeled-extinguisher-catalog-english.pdf) p. 11: 680R P/N 10897, 150 lb "
                   "Super D, 444 lb shipping, 52 H x 28 W x 45 D in, 36 x 2.5 in steel wheels with non-sparking rubber "
                   "treads, argon cylinder DOT 3AA2015 110 ft3 regulated to 125 psi, 25 ft x 0.75 in hose, 80 s, "
                   "4-8 ft with the applicator, extension wand (nozzle sold separately); the cylinders' sizes are ours, "
                   "from the agent's volume and the catalogue's photo. Price: Tiger Medical's sale price $11,541 (list "
                   "$16,589.79); All Security Equipment $10,931.99; others to $22,573")
PAIL = dict(d=300.0, h=360.0, lb=50.0, price_usd=519.0,
            source="Brooks/Amerex Super D, 50 lb pail (safetyemporium.com 09530; Brooks 50DPAIL, absupply.net, "
                   "about $519); the pail's size and colour aren't published: a 5 gal open-head pail, drawn plain; a "
                   "metal scoop is sold separately (safetyemporium.com 09461)")
SIGN = dict(w=7 * IN, h=10 * IN, t=1.5)      # 7 x 10 in rigid plastic (DAL's parts list)
POST = dict(s=41.3, h=2150.0, base=254.0, base_t=9.5,
            source="ours: a 1-5/8 in 12 ga strut channel (Unistrut P1000 class) on a 10 x 10 x 3/8 in post base, "
                   "anchored with four 1/2 in wedge anchors, painted fire red; the Amerex hook on its face, the signs above")
NFPA10 = dict(top_max=42 * IN, bottom_min=4 * IN, travel_max=75 * 12 * IN, travel_ideal=25 * 12 * IN,
              keep_clear=36 * IN, keep_clear_w=24 * IN,
              source="NFPA 10 6.1.3.8.2-3 (gross weight over 40 lb: top at most 3.5 ft above the floor, bottom at least "
                     "4 in) and 6.5 / OSHA 29 CFR 1910.157(d)(5) (Class D agent within 75 ft of travel); 25 ft is the "
                     "lab's vacuum SOP's 'ideally' (PR 80, vacuum-operating-sop.md gate 0.2)")
# A unit on a wall hook or a post hangs with its bottom here: the hose's loop then tops out at 1047 mm (41.2 in), the
# lever at 826 mm, so either reading of NFPA 10's "top" passes, and the bottom clears the floor by 140 mm (5.5 in)
HANG_BOTTOM = 140.0

# name: (r, g, b, opacity, specular)
MATS = {
    "cd_yellow": (0.93, 0.79, 0.06, 1.0, 0.45),       # Amerex's Class D yellow, glossy enamel
    "chrome": (0.86, 0.87, 0.89, 1.0, 0.95),
    "steel": (0.70, 0.71, 0.73, 1.0, 0.7),
    "rubber": (0.07, 0.07, 0.08, 1.0, 0.15),
    "black_plastic": (0.09, 0.09, 0.10, 1.0, 0.35),
    "handle": (0.17, 0.17, 0.18, 1.0, 0.7),           # the carry handle's black chrome
    "gauge_red": (0.78, 0.09, 0.08, 1.0, 0.4),
    "gauge_green": (0.12, 0.62, 0.27, 1.0, 0.3),
    "label": (0.96, 0.96, 0.94, 1.0, 0.15),
    "print": (0.05, 0.05, 0.05, 1.0, 0.1),
    "picto": (0.55, 0.55, 0.55, 1.0, 0.1),           # the label's pictograms and small print, as grey
    "star": (0.98, 0.83, 0.08, 1.0, 0.2),
    "seal": (0.86, 0.13, 0.12, 1.0, 0.3),            # the red tamper seal on the pin (the lab's photo)
    "hook_red": (0.76, 0.10, 0.09, 1.0, 0.4),
    "bracket": (0.08, 0.08, 0.09, 1.0, 0.45),         # the 811's black powder coat
    "post_red": (0.72, 0.11, 0.10, 1.0, 0.35),
    "sign_red": (0.80, 0.09, 0.09, 1.0, 0.2),
    "sign_white": (0.97, 0.97, 0.95, 1.0, 0.1),
    "alu": (0.80, 0.81, 0.83, 1.0, 0.6),
    "argon_green": (0.20, 0.55, 0.30, 1.0, 0.3),
    "floor_yellow": (0.95, 0.80, 0.10, 1.0, 0.1),
    "floor_black": (0.08, 0.08, 0.08, 1.0, 0.1),
    "pail": (0.90, 0.90, 0.88, 1.0, 0.3),
}


def colour(mat: str) -> tuple:
    return MATS[mat][:3]


# ================================================================================================ geometry helpers
def _pv():
    import pyvista as pv
    return pv


def _mesh(shape, tol=0.25, ang=0.25):
    """A CadQuery shape (or Workplane) -> a pyvista mesh with split normals."""
    import cadquery as cq
    pv = _pv()
    s = shape.val() if hasattr(shape, "val") and not isinstance(shape, cq.Shape) else shape
    if hasattr(shape, "vals") and len(shape.vals()) > 1:
        s = cq.Compound.makeCompound(shape.vals())
    verts, tris = s.tessellate(tol, ang)
    if not tris:
        return pv.PolyData()
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([np.full((len(tris), 1), 3), np.asarray(tris, int)]).ravel()
    m = pv.PolyData(pts, faces).clean()
    return m.compute_normals(split_vertices=True, feature_angle=35.0, auto_orient_normals=False)


def _box(x0, y0, z0, x1, y1, z1):
    import cadquery as cq
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _cyl(r, h, p=(0, 0, 0), d=(0, 0, 1)):
    import cadquery as cq
    return cq.Solid.makeCylinder(r, h, cq.Vector(*p), cq.Vector(*d))


def _prism(pts2d, y0, y1):
    """A polygon in the x-z plane [(x, z)], extruded from y0 to y1."""
    import cadquery as cq
    wp = cq.Workplane("XZ", origin=(0, y1, 0)).polyline(pts2d).close().extrude(y1 - y0)
    return wp.val()


def _revolve(profile):
    """A solid of revolution about z from a closed profile [(r, z)]."""
    import cadquery as cq
    return cq.Workplane("XZ").polyline(profile).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()


def _tube(points, r, n=24, cap=True):
    """A tube along a smooth curve through `points`."""
    pv = _pv()
    pts = np.asarray(points, float)
    spl = pv.Spline(pts, max(60, 12 * len(pts)))
    return spl.tube(radius=r, n_sides=n, capping=cap).triangulate().clean()


def _text(s, h, depth=0.5):
    """pv.Text3D, letters h mm tall, its bottom left at the origin, reading along +x, up +y, depth +z."""
    pv = _pv()
    t = pv.Text3D(s, depth=depth)
    b = t.bounds
    t = t.translate((-b[0], -b[2], -b[4]), inplace=False)
    return t.scale(h / max(b[3] - b[2], 1e-6), inplace=False).triangulate()


def _text_w(s, h):
    t = _text(s, h)
    return t.bounds[1] - t.bounds[0]


def _on_cyl(mesh, r, s0=0.0, z0=0.0):
    """Wrap a flat mesh (x along the surface, y up, z out of it) onto a cylinder of radius r about z, its x = 0 on the
    cylinder's front (-y); s0 shifts it along the surface, z0 up."""
    m = mesh.triangulate().subdivide_adaptive(max_edge_len=2.0).copy()
    p = np.asarray(m.points, float)
    a = (p[:, 0] + s0) / r
    rr = r + p[:, 2]
    m.points = np.c_[rr * np.sin(a), -rr * np.cos(a), p[:, 1] + z0]
    return m


def _on_face(mesh, x0=0.0, z0=0.0, y=0.0, facing=-1):
    """Stand a flat mesh (x along, y up, z out) on a face looking to `facing` y (-1: the front)."""
    m = mesh.copy()
    p = np.asarray(m.points, float)
    if facing < 0:
        m.points = np.c_[p[:, 0] + x0, y - p[:, 2], p[:, 1] + z0]
    else:
        m.points = np.c_[-p[:, 0] + x0, y + p[:, 2], p[:, 1] + z0]
    return m


def _sector(r, a0, a1, z0, z1, t=0.5, n=48):
    """A thin curved panel on a cylinder of radius r, between angles a0..a1 (deg, 0 at -y, + towards +x), z0..z1."""
    pv = _pv()
    a = np.radians(np.linspace(a0, a1, n))
    pts, faces = [], []
    for rr in (r, r + t):
        for zz in (z0, z1):
            for aa in a:
                pts.append((rr * np.sin(aa), -rr * np.cos(aa), zz))
    pts = np.array(pts)
    N = len(a)
    idx = lambda ri, zi, ai: (ri * 2 + zi) * N + ai
    for i in range(N - 1):
        for ri in (0, 1):                                 # inner and outer skins
            q = [idx(ri, 0, i), idx(ri, 0, i + 1), idx(ri, 1, i + 1), idx(ri, 1, i)]
            faces += [3, q[0], q[1], q[2], 3, q[0], q[2], q[3]]
        for zi in (0, 1):                                 # top and bottom edges
            q = [idx(0, zi, i), idx(0, zi, i + 1), idx(1, zi, i + 1), idx(1, zi, i)]
            faces += [3, q[0], q[1], q[2], 3, q[0], q[2], q[3]]
    for ai in (0, N - 1):                                 # the two ends
        q = [idx(0, 0, ai), idx(1, 0, ai), idx(1, 1, ai), idx(0, 1, ai)]
        faces += [3, q[0], q[1], q[2], 3, q[0], q[2], q[3]]
    return pv.PolyData(pts, np.array(faces)).clean().compute_normals(split_vertices=True, feature_angle=35.0)


def _star(r_out, r_in, n=5):
    """A star polygon [(x, y)], a point up."""
    pts = []
    for i in range(2 * n):
        a = math.pi / 2 + i * math.pi / n
        r = r_out if i % 2 == 0 else r_in
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def _flat_poly(pts2d, depth=0.5):
    """A flat polygon [(x, y)] extruded `depth` along +z, as a mesh (x along, y up, z out)."""
    pv = _pv()
    pts = np.array([(x, y, 0.0) for x, y in pts2d])
    poly = pv.PolyData(pts, np.r_[len(pts), np.arange(len(pts))]).triangulate()
    return poly.extrude((0, 0, depth), capping=True).triangulate().clean()


def _merge(meshes):
    pv = _pv()
    ms = [m for m in meshes if m is not None and m.n_points]
    if not ms:
        return pv.PolyData()
    return ms[0].merge(ms[1:]) if len(ms) > 1 else ms[0]


def _add(parts: dict, name: str, mesh, mat: str):
    if mesh is None or not mesh.n_points:
        return
    if name in parts:
        parts[name] = (_merge([parts[name][0], mesh]), mat)
    else:
        parts[name] = (mesh, mat)


# ================================================================================================ the Amerex B570
def class_d_star(h=22.0, depth=0.6):
    """The Class D symbol as Amerex prints it: a yellow five-pointed star, outlined black, with a black D. Flat, its
    centre at the origin, facing +z. -> [(mesh, mat)]."""
    r = h / 2
    out = [(_flat_poly(_star(r, r * 0.45), depth * 0.5), "print"),
           (_flat_poly(_star(r * 0.86, r * 0.45 * 0.82), depth).translate((0, 0, depth * 0.3), inplace=False), "star")]
    d = _text("D", h * 0.36, depth * 0.4)
    b = d.bounds
    out.append((d.translate((-(b[0] + b[1]) / 2, -(b[2] + b[3]) / 2 - h * 0.03, depth * 1.2), inplace=False),
                "print"))
    return out


def b570_parts(hose: bool = True, lod: str = "full") -> dict:
    """{name: (PolyData, material)}: the Amerex B570, part by part, in its own frame (see B570). lod "lab" leaves out
    the label's small print (for whole-lab scenes, where it is a few pixels)."""
    import cadquery as cq
    pv = _pv()
    b = B570
    R = b["d"] / 2
    zw, zd = b["z_wall"], b["z_dome"]
    p: dict = {}
    # the drawn-steel shell: a rounded foot, the straight wall, a 2:1-ish elliptical head up to the neck
    prof = [(0.0, 0.0), (R - 7.0, 0.0)]
    prof += [(R - 7.0 + 7.0 * math.sin(t), 7.0 - 7.0 * math.cos(t)) for t in np.linspace(0.2, math.pi / 2, 6)]
    prof += [(R, zw)]
    h = zd - zw
    for t in np.linspace(0.08, math.pi / 2, 14):
        x = R * math.cos(t)
        if x < b["neck"][0]:
            break
        prof.append((x, zw + h * math.sin(t)))
    prof += [(b["neck"][0], zd), (0.0, zd)]
    _add(p, "B570 cylinder", _mesh(_revolve(prof), 0.2), "cd_yellow")
    # the neck ring and the threaded collar, yellow, with two grooves
    r0, z0, z1 = b["neck"]
    rc, c0, c1 = b["collar"]
    neck = _cyl(r0, z1 - z0, (0, 0, z0)).fuse(_cyl(rc, c1 - c0, (0, 0, c0)))
    for zg in (c0 + 6.0, c0 + 15.0):
        neck = neck.cut(_cyl(rc + 1, 3.0, (0, 0, zg)).cut(_cyl(rc - 2.0, 3.0, (0, 0, zg))))
    _add(p, "B570 collar", _mesh(neck), "cd_yellow")
    # the valve: a chrome-plated brass body on the collar, the gauge's boss to the front, the outlet to the left
    zv0, zg = c1, b["z_gauge"]
    body = _cyl(17.0, 45.0, (0, 0, zv0)).fuse(_cyl(15.5, 26.0, (0, 2.0, zg), (0, -1, 0)))
    body = body.fuse(_cyl(10.5, 34.0, (-6.0, 0, 626.0), (-1, 0, 0)))          # the outlet boss, to the left
    body = body.fuse(_box(-34.0, -9.0, 640.0, 14.0, 9.0, 654.0))               # the levers' pivot block
    _add(p, "B570 valve", _mesh(body), "chrome")
    _add(p, "B570 ferrule", _mesh(_cyl(12.5, 24.0, (-40.0, 0, 626.0), (-1, 0, 0))), "chrome")
    # the gauge: a chrome bezel, a red face, a green arc at the top (the operable range), a needle in the green
    bezel = _cyl(15.0, 4.0, (0, -24.0, zg), (0, -1, 0)).cut(_cyl(12.0, 5.0, (0, -23.5, zg), (0, -1, 0)))
    _add(p, "B570 gauge bezel", _mesh(bezel), "chrome")
    _add(p, "B570 gauge face", _mesh(_cyl(12.0, 1.0, (0, -24.0, zg), (0, -1, 0))), "gauge_red")
    arc = []
    for a in np.radians(np.linspace(60, 120, 7)):
        arc.append((9.5 * math.cos(a), 9.5 * math.sin(a)))
    for a in np.radians(np.linspace(120, 60, 7)):
        arc.append((6.5 * math.cos(a), 6.5 * math.sin(a)))
    garc = _flat_poly(arc, 0.4)
    _add(p, "B570 gauge arc", _on_face(garc, 0.0, zg, -25.0, -1), "gauge_green")
    needle = _flat_poly([(-0.8, 0.0), (0.8, 0.0), (0.3, 9.0), (-0.3, 9.0)], 0.4)
    _add(p, "B570 gauge needle", _on_face(needle, 0.0, zg, -25.4, -1), "print")
    # the squeeze lever (chrome, on top, rising to its tip) and the carry handle (black chrome, falling to its end),
    # both to the right; Amerex's render, in mm from the axis and the bottom
    lever = [(-34.0, 645.0), (-34.0, 656.0), (-12.0, 664.0), (55.0, 680.0), (99.0, 686.0), (99.0, 681.0),
             (55.0, 673.0), (-6.0, 652.0)]
    _add(p, "B570 lever", _mesh(_prism(lever, -8.0, 8.0)), "chrome")
    handle = [(8.0, 630.0), (20.0, 638.0), (60.0, 627.0), (104.0, 604.0), (104.0, 596.0), (60.0, 615.0),
              (18.0, 623.0)]       # its end stops 5 mm short of the applicator's grip
    _add(p, "B570 handle", _mesh(_prism(handle, -9.0, 9.0)), "handle")
    # the large-loop stainless pull pin through the levers, and the red tamper seal on it (the lab's photo)
    pin = _cyl(2.0, 26.0, (8.0, -13.0, 650.0), (0, 1, 0))
    ring = cq.Solid.makeTorus(12.0, 1.4, cq.Vector(8.0, -14.0, 676.0), cq.Vector(1, 0, 0))
    _add(p, "B570 pin", _mesh(pin.fuse(ring)), "steel")
    _add(p, "B570 seal", _mesh(_box(4.0, -18.0, 656.0, 12.0, -14.0, 668.0)), "seal")
    # the hose: from the outlet to the left, up over the top in a loop, down the right side to the coupling
    if hose:
        # a turn and a half, as Amerex's render shows it (two strands up the left and over the top): out to the left,
        # up and over (the inner turn), down the right, behind the valve's collar, up the left again and over (the
        # outer turn), down to the applicator's coupling; each turn a hose's width behind the last
        path = [(-64.0, 0.0, 626.0), (-88.0, 2.0, 636.0), (-104.0, 4.0, 668.0), (-107.0, 6.0, 720.0),
                (-102.0, 7.0, 785.0), (-72.0, 8.0, 835.0), (-28.0, 9.0, 852.0), (14.0, 10.0, 845.0),
                (48.0, 12.0, 815.0), (73.0, 14.0, 778.0), (82.0, 16.0, 740.0), (78.0, 18.0, 700.0),
                (60.0, 21.0, 664.0), (30.0, 26.0, 642.0), (0.0, 37.0, 624.0), (-42.0, 34.0, 630.0),
                (-95.0, 29.0, 652.0), (-127.0, 25.0, 690.0), (-133.0, 21.0, 727.0), (-125.0, 17.0, 790.0),
                (-103.0, 14.0, 835.0), (-60.0, 11.0, 872.0), (7.0, 8.0, 893.0), (72.0, 5.0, 871.0),
                (103.0, 3.0, 835.0), (116.0, 1.0, 798.0), (119.0, 0.0, 777.0)]
        _add(p, "B570 hose", _tube(path, 11.0), "rubber")
    # the applicator: chrome quick-detach coupling, a black tapered grip, the wand, the soft-flow cup
    wx = b["wand_x"]
    cpl = _cyl(13.0, 77.0, (wx, 0, 700.0)).fuse(_cyl(15.5, 10.0, (wx, 0, 758.0))).fuse(_cyl(15.5, 8.0, (wx, 0, 706.0)))
    _add(p, "B570 coupling", _mesh(cpl), "chrome")           # the quick-detach coupling, 700-777 mm (the render)
    grip = cq.Solid.makeCone(9.5, 13.5, 140.0, cq.Vector(wx, 0, 560.0), cq.Vector(0, 0, 1))
    _add(p, "B570 applicator", _mesh(grip.fuse(_cyl(9.0, 462.0, (wx, 0, 99.0)))), "black_plastic")
    tilt = math.radians(22.0)
    d = (0.0, -math.sin(tilt), -math.cos(tilt))
    top = cq.Vector(wx + 5.0, 0.0, 98.0)
    cup = cq.Solid.makeCylinder(43.0, 86.0, top, cq.Vector(*d))
    cup = cup.cut(cq.Solid.makeCylinder(39.0, 86.0, top + cq.Vector(*d) * 4.0, cq.Vector(*d)))
    cup = cup.fuse(cq.Solid.makeCone(11.0, 43.0, 5.0, top, cq.Vector(*d)))
    _add(p, "B570 nozzle", _mesh(cup), "black_plastic")
    # the two lattice bands (diamond windows) with the applicator's clip on the right
    for i, (zb0, zb1) in enumerate(b["bands"]):
        band = _cyl(R + 3.0, zb1 - zb0, (0, 0, zb0)).cut(_cyl(R + 0.2, zb1 - zb0 + 2, (0, 0, zb0 - 1)))
        zc = (zb0 + zb1) / 2
        for k in range(12):
            a = math.radians(k * 30.0 + 15.0)
            # a diamond prism, radial, through the band at angle a (0 at -y)
            pr = cq.Workplane("XZ", origin=(0, -(R + 8.0), zc)).polyline(
                [(-17.0, 0.0), (0.0, -8.5), (17.0, 0.0), (0.0, 8.5)]).close().extrude(-14.0).val()
            pr = pr.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), math.degrees(a))
            band = band.cut(pr)
        clip = _cyl(13.5, zb1 - zb0, (wx, 0, zb0)).cut(_cyl(9.8, zb1 - zb0 + 2, (wx, 0, zb0 - 1)))
        web = _box(R + 1.0, -6.0, zb0, wx - 12.0, 6.0, zb1)
        _add(p, "B570 bands", _mesh(band.fuse(clip).fuse(web)), "black_plastic")
    # the instruction label: white, a black header, the D star, its two lines; the Amerex diamond lower down
    l0, l1 = b["label"]
    rl = R + 0.25
    _add(p, "B570 label", _sector(rl, -78.0, 78.0, l0, l1, 0.35), "label")
    _add(p, "B570 label header", _sector(rl + 0.3, -78.0, 78.0, l1 - 11.0, l1 - 1.5, 0.2), "print")
    if lod != "full":
        for mesh, mat in class_d_star(22.0, 0.5):
            _add(p, "B570 label star" if mat == "star" else "B570 label print", _on_cyl(mesh, rl + 0.45, 0.0, 372.0),
                 mat)
        return p
    hdr = _text("INSTRUCTIONS", 6.5, 0.25)
    w_ = hdr.bounds[1]
    _add(p, "B570 label print", _on_cyl(hdr, rl + 0.55, -w_ / 2, l1 - 9.6), "label")
    for k in range(4):                                     # the four pictograms, as grey panels with a number disc
        a0 = math.degrees((-62.0 + k * 31.0) / R)
        _add(p, "B570 label pictos", _sector(rl + 0.35, a0, a0 + math.degrees(24.0 / R), l1 - 40.0, l1 - 16.0, 0.15,
                                             8), "picto")
    for a0, a1 in ((-78.0, -46.0), (46.0, 78.0)):          # the two columns of small print either side
        for i in range(9):
            zz = l0 + 12.0 + i * 8.5
            _add(p, "B570 label pictos", _sector(rl + 0.35, a0 + 2, a1 - 2, zz, zz + 2.6, 0.12, 8), "picto")
    for txt, s, z in (("COMBUSTIBLE", -66.0, 375.0), ("METALS", -60.0, 366.0), ("FIRE", 26.0, 375.0),
                      ("EXTINGUISHER", 20.0, 366.0)):
        _add(p, "B570 label print", _on_cyl(_text(txt, 5.0, 0.25), rl + 0.5, s, z), "print")
    for mesh, mat in class_d_star(22.0, 0.5):
        _add(p, "B570 label star" if mat == "star" else "B570 label print", _on_cyl(mesh, rl + 0.45, 0.0, 372.0),
             mat)
    cau = _text("CAUTION: FIRE MAY RE-IGNITE, ALLOW METAL TO COOL BEFORE CLEANUP.", 2.6, 0.2)
    _add(p, "B570 label print", _on_cyl(cau, rl + 0.5, -cau.bounds[1] / 2, l0 + 6.0), "print")
    g0, g1 = b["logo"]
    dia = [(-54.0, 0.0), (0.0, -(g1 - g0) / 2 - 2.0), (54.0, 0.0), (0.0, (g1 - g0) / 2 + 2.0)]
    out = _flat_poly(dia, 0.3)
    inner = _flat_poly([(x * 0.9, y * 0.78) for x, y in dia], 0.5)
    zc = (g0 + g1) / 2
    _add(p, "B570 logo", _on_cyl(out, R + 0.3, 0.0, zc), "print")
    _add(p, "B570 logo white", _on_cyl(inner, R + 0.35, 0.0, zc), "label")
    am = _text("AMEREX", 6.0, 0.25)
    _add(p, "B570 logo", _on_cyl(am, R + 0.95, -am.bounds[1] / 2, zc - 3.0), "print")
    return p


def b570_envelope() -> dict:
    """The B570's extent in its own frame, mm: from the parts (hose included)."""
    pts = np.vstack([m.points for m, _ in b570_parts().values()])
    lo, hi = pts.min(0), pts.max(0)
    return dict(x=(float(lo[0]), float(hi[0])), y=(float(lo[1]), float(hi[1])), z=(float(lo[2]), float(hi[2])))


# ================================================================================================ the hangers
def hook_parts(standoff: float = 10.0) -> dict:
    """The red Amerex wall hook, in the B570's frame as it hangs on it: its back plate on a wall at y = R + standoff
    behind the axis, its arm out under the valve (seat at B570["z_seat"]), a slot for the collar, a short lip.
    2 in wide, 0.09 in steel; the back plate 4.5 in below the seat (DAL's model, from the issue's photos)."""
    t, w = 0.09 * IN, 2.0 * IN
    R = B570["d"] / 2
    yw = R + standoff                      # the wall face
    zs = B570["z_seat"]
    plate = _box(-w / 2, yw - t, zs - 4.5 * IN, w / 2, yw, zs)
    arm = _box(-30.0, -B570["collar"][0] - 14.0, zs - t, 30.0, yw, zs)        # widened round the slot (ours)
    arm = arm.cut(_cyl(B570["collar"][0] + 1.5, 10.0, (0, 0, zs - 5.0)))
    arm = arm.cut(_box(-B570["collar"][0] - 1.5, -60.0, zs - 5.0, B570["collar"][0] + 1.5, 0.0, zs + 5.0))
    lip = _box(-30.0, -B570["collar"][0] - 14.0 - t, zs - t, 30.0, -B570["collar"][0] - 14.0, zs + 14.0)
    lip = lip.cut(_box(-B570["collar"][0] - 1.5, -80.0, zs - 10, B570["collar"][0] + 1.5, -10.0, zs + 20))
    s = plate.fuse(arm).fuse(lip)
    for (x, z, dd) in ((0.0, zs - 2.2 * IN, 0.28 * IN), (-0.6 * IN, zs - 1.0 * IN, 0.2 * IN),
                       (0.6 * IN, zs - 3.6 * IN, 0.2 * IN)):
        s = s.cut(_cyl(dd / 2, 20.0, (x, yw + 5.0, z), (0, -1, 0)))
    p = {"Amerex wall hook": (_mesh(s), "hook_red")}
    screws = None
    for (x, z, dd) in ((0.0, zs - 2.2 * IN, 0.25 * IN), (-0.6 * IN, zs - 1.0 * IN, 0.1875 * IN),
                       (0.6 * IN, zs - 3.6 * IN, 0.1875 * IN)):
        hd = _cyl(dd * 1.1, 4.0, (x, yw - t, z), (0, -1, 0))
        screws = hd if screws is None else screws.fuse(hd)
    p["hook screws"] = (_mesh(screws), "steel")
    return p


def bracket811_parts(closed: float = 1.0) -> dict:
    """The 811 heavy-duty vehicle bracket in its own frame (B811): a black channel (a flat web and two flanges at 45
    deg), a foot plate with chamfered corners, a top lip with two rubber bumpers, bushings on the web, and the strap
    with its over-centre latch at the right front. closed 1: the strap round a B570; 0: the latch thrown, the strap
    swung open about its hinge on the left flange."""
    H, W, D, t, web = B811["H"], B811["W"], B811["D"], B811["t"], B811["web"]
    fl = (W - web) / 2 / math.cos(math.radians(45.0))          # each flange's width
    p: dict = {}
    s = _box(-web / 2, -t, 0.0, web / 2, 0.0, H)
    for sx in (-1, 1):
        f = _box(0.0, -t, 0.0, fl, 0.0, H)
        f = f.rotate(_v(0, 0, 0), _v(0, 0, 1), sx * -45.0 + (180.0 if sx < 0 else 0.0))   # forward and out
        f = f.translate(_v(sx * web / 2, 0.0, 0.0))
        s = s.fuse(f)
    foot = [(-W / 2, 0.0), (W / 2, 0.0), (W / 2, -D + 40.0), (W / 2 - 40.0, -D), (-W / 2 + 40.0, -D), (-W / 2, -D + 40.0)]
    import cadquery as cq
    fp = cq.Workplane("XY").polyline(foot).close().extrude(t).val()
    for hx, hy in ((-60.0, -60.0), (60.0, -60.0), (-60.0, -150.0), (60.0, -150.0), (0.0, -105.0)):
        fp = fp.cut(_cyl(5.6, 10.0, (hx, hy, -2.0)))
    s = s.fuse(fp)
    for hz in (60.0, 200.0, 330.0):                                   # 7/16 in mounting holes up the web
        for hx in (-30.0, 30.0):
            s = s.cut(_cyl(5.6, 10.0, (hx, 2.0, hz), (0, -1, 0)))
    p["811 bracket"] = (_mesh(s), "bracket")
    bush = None
    R = B570["d"] / 2
    for hz in (110.0, 400.0):
        for hx in (-18.0, 18.0):
            bb = _cyl(11.0, B811["bush"], (hx, -t, hz), (0, -1, 0))
            bush = bb if bush is None else bush.fuse(bb)
    p["811 rubber"] = (_mesh(bush), "rubber")
    # the strap: a 25 mm band round the cylinder (axis at y = -(t + bush + R)), from the left flange's tip to the right's
    ya = -(t + B811["bush"] + R)
    z0, z1 = B811["z_strap"]
    a_end = 50.0                                     # deg either side of the back the strap starts from (the flanges)
    sweep = closed * (360.0 - 2 * a_end) + (1 - closed) * 60.0
    rs = R + 1.0
    ring = _cyl(rs + 2.0, z1 - z0, (0, ya, z0)).cut(_cyl(rs, z1 - z0 + 2, (0, ya, z0 - 1)))
    keep = _sector_solid(rs - 1, rs + 3, 180.0 + a_end, 180.0 + a_end + sweep, z0, z1, (0, ya))
    strap = ring.intersect(keep)
    p["811 strap"] = (_mesh(strap), "bracket")
    # the hinge on the left flange, and the over-centre latch at the strap's free end (on the right side when shut)
    ah = math.radians(180.0 + a_end)
    hx, hy = (rs + 4) * math.sin(ah), ya - (rs + 4) * math.cos(ah)
    a_deg = 180.0 + a_end + sweep - 28.0
    a_l = math.radians(a_deg)
    lx, ly = (rs + 9) * math.sin(a_l), ya - (rs + 9) * math.cos(a_l)
    latch = _box(lx - 6.0, ly - 30.0, z0 - 3.0, lx + 6.0, ly + 30.0, z1 + 3.0)
    latch = latch.rotate(_v(lx, ly, 0), _v(lx, ly, 1), -a_deg)
    p["811 latch"] = (_mesh(latch.fuse(_cyl(5.0, z1 - z0 + 10, (hx, hy, z0 - 5)))), "chrome")
    return p


def _v(x, y, z):
    import cadquery as cq
    return cq.Vector(x, y, z)


def _sector_solid(r0, r1, a0, a1, z0, z1, c=(0.0, 0.0)):
    """An annular sector solid about the axis at c, between angles a0..a1 (deg, 0 at -y, + towards +x)."""
    import cadquery as cq
    a = np.radians(np.linspace(a0, a1, max(3, int(abs(a1 - a0) / 6) + 2)))
    outer = [(c[0] + r1 * math.sin(t), c[1] - r1 * math.cos(t)) for t in a]
    inner = [(c[0] + r0 * math.sin(t), c[1] - r0 * math.cos(t)) for t in a[::-1]]
    return cq.Workplane("XY", origin=(0, 0, z0)).polyline(outer + inner).close().extrude(z1 - z0).val()


def b570_in_811() -> np.ndarray:
    """4x4: the B570's frame in the 811's (standing on the foot plate, its back on the bushings)."""
    from scene import T
    R = B570["d"] / 2
    return T((0.0, -(B811["t"] + B811["bush"] + R), B811["t"]))


# ================================================================================================ the 680R
def w680r_parts() -> dict:
    """{name: (PolyData, material)}: the Amerex 680R in its own frame (W680): the agent cylinder in front of the axle,
    the argon cylinder behind it, the handle over the argon, the hose coiled on its rack on the left, the discharge
    valve and the wand clipped up the left front, two spoked wheels with black treads, a toe plate."""
    import cadquery as cq
    w = W680
    p: dict = {}
    rw = w["wheel"] / 2
    zax, yax = rw, 175.0
    xw = w["W"] / 2 - w["tread"] / 2
    for sx in (-1, 1):
        x0 = sx * xw - w["tread"] / 2
        tread = cq.Workplane("YZ", origin=(x0, yax, zax)).circle(rw).circle(rw - 22.0).extrude(w["tread"]).val()
        _add(p, "680R treads", _mesh(tread, 0.6), "rubber")
        rim = cq.Workplane("YZ", origin=(x0 + 8.0, yax, zax)).circle(rw - 21.0).circle(rw - 40.0).extrude(
            w["tread"] - 16.0).val()
        hub = _cyl(45.0, 90.0, (sx * xw - 45.0, yax, zax), (1, 0, 0))
        _add(p, "680R wheels", _mesh(rim.fuse(hub), 0.6), "cd_yellow")
        spokes = []
        for k in range(16):
            a = k * 2 * math.pi / 16
            off = 18.0 if k % 2 else -18.0                   # laced: alternate spokes to either flange
            a_ = np.array([sx * xw + off, yax + 40 * math.cos(a), zax + 40 * math.sin(a)])
            b_ = np.array([sx * xw, yax + (rw - 38.0) * math.cos(a), zax + (rw - 38.0) * math.sin(a)])
            spokes.append(_pv().Cylinder(center=(a_ + b_) / 2, direction=b_ - a_, radius=4.5,
                                         height=float(np.linalg.norm(b_ - a_)), resolution=8).triangulate())
        _add(p, "680R wheels", _merge(spokes), "cd_yellow")
        _add(p, "680R hub caps", _mesh(_cyl(30.0, 12.0, (sx * (xw + 45.0), yax, zax), (sx, 0, 0))), "rubber")
    _add(p, "680R axle", _mesh(_cyl(16.0, 2 * xw, (-xw, yax, zax), (1, 0, 0))), "steel")
    # the agent cylinder: a welded steel shell on the toe plate, its fill cap (chrome, with its two ears) on top
    ra, ha = w["d_agent"] / 2, w["h_agent"]
    z0 = 45.0
    prof = [(0, z0), (ra - 10, z0), (ra, z0 + 10), (ra, z0 + ha - 75)]
    prof += [(ra * math.cos(t), z0 + ha - 75 + 75 * math.sin(t)) for t in np.linspace(0.1, 1.25, 8)]
    prof += [(55.0, z0 + ha), (0, z0 + ha)]
    _add(p, "680R agent cylinder", _mesh(_revolve(prof), 0.5), "cd_yellow")
    cap = _cyl(52.0, 32.0, (0, 0, z0 + ha)).fuse(_box(-48, -6, z0 + ha + 32, -30, 6, z0 + ha + 60)).fuse(
        _box(30, -6, z0 + ha + 32, 48, 6, z0 + ha + 60))
    _add(p, "680R fill cap", _mesh(cap), "chrome")
    for zc in (250.0, 700.0):                           # the stainless collars to the carriage
        col = _cyl(ra + 4, 30.0, (0, 0, zc)).cut(_cyl(ra + 0.5, 32, (0, 0, zc - 1)))
        _add(p, "680R collars", _mesh(col, 0.5), "steel")
    # the argon cylinder behind, its valve and the regulator; green gas label
    rg, hg = w["d_argon"] / 2, w["h_argon"]
    yg = yax + 150.0
    prof = [(0, 120.0), (rg - 8, 120.0), (rg, 128.0), (rg, 120.0 + hg - 60)]
    prof += [(rg * math.cos(t), 120.0 + hg - 60 + 60 * math.sin(t)) for t in np.linspace(0.1, 1.3, 7)]
    prof += [(18.0, 120.0 + hg), (0, 120.0 + hg)]
    _add(p, "680R argon cylinder", _mesh(_revolve(prof).translate(_v(0, yg, 0)), 0.5), "cd_yellow")
    reg = _cyl(16.0, 60.0, (0, yg, 120 + hg)).fuse(_cyl(24.0, 40.0, (0, yg - 30, 120 + hg + 40), (0, -1, 0)))
    _add(p, "680R regulator", _mesh(reg), "chrome")
    gl = _flat_poly([(-30, 0), (0, -30), (30, 0), (0, 30)], 0.4)
    _add(p, "680R gas label", _on_cyl(gl, rg + 0.3, 0.0, 120 + hg - 160).translate((0, yg, 0), inplace=False),
         "argon_green")
    # the carriage: two uprights from the axle up into the handle loop over the argon cylinder, a toe plate
    up = []
    for sx in (-1, 1):
        up.append(_tube([(sx * 150, yax, zax), (sx * 150, yax + 60, zax + 300), (sx * 150, yax + 120, 1100),
                         (sx * 150, yax + 140, 1215)], 16.0, 16))
    up.append(_tube([(-150, yax + 140, 1215), (-100, yax + 145, 1262), (100, yax + 145, 1262),
                     (150, yax + 140, 1215)], 16.0, 16))
    _add(p, "680R handle", _merge(up), "cd_yellow")
    toe = _box(-200.0, -ra - 30.0, 0.0, 200.0, yax + 40.0, 45.0)
    cradle = _box(-110.0, yax + 40.0, 95.0, 110.0, yg + rg + 12.0, 120.0)      # the argon cylinder stands on it
    _add(p, "680R carriage", _mesh(toe.fuse(_box(-170, yax - 20, 45, 170, yax + 20, 700)).fuse(cradle)), "cd_yellow")
    # the hose on its rack (left), coiled in long loops, 25 ft x 3/4 in
    rack = _box(-ra - 70, yax - 10, 940, -ra - 20, yax + 10, 960).fuse(_box(-ra - 70, yax - 10, 520, -ra - 20,
                                                                              yax + 10, 540))
    _add(p, "680R hose rack", _mesh(rack), "cd_yellow")
    loops = []
    xr = -ra - 55.0
    for i in range(6):
        yy = yax - 60.0 + i * 22.0
        pts = [(xr, yy, 950.0)]
        for t in np.linspace(0.0, math.pi, 9)[1:]:
            pts.append((xr - 8.0 * math.sin(t), yy + 30.0 * math.sin(t), 950.0 - (260.0 + 18.0 * i) * (1 - math.cos(t)) / 2))
        pts.append((xr, yy + 4.0, 950.0))
        loops.append(_tube(pts, w["hose_in"] * IN / 2, 14))
    _add(p, "680R hose", _merge(loops), "rubber")
    # the discharge end: the hose up to the valve (chrome, a ring) and the extension wand clipped up the left front
    xv, yv = -ra - 30.0, -ra + 40.0
    _add(p, "680R hose", _tube([(xr, yax - 60, 950), (xr + 10, yax - 140, 1120), (xv, yv + 30, 1280),
                                (xv, yv, 1250)], w["hose_in"] * IN / 2, 14), "rubber")
    valve = _cyl(14.0, 70.0, (xv, yv, 1180)).fuse(cq.Solid.makeTorus(22.0, 3.0, _v(xv - 30, yv, 1215), _v(0, 1, 0)))
    _add(p, "680R valve", _mesh(valve), "chrome")
    _add(p, "680R wand", _mesh(_cyl(12.0, 1000.0, (xv, yv, 180)).fuse(_cyl(32.0, 70.0, (xv, yv, 110)))),
         "black_plastic")
    # the instruction label and the Amerex diamond on the agent cylinder's front
    _add(p, "680R label", _sector(ra + 0.3, -42.0, 42.0, 560.0, 830.0, 0.4), "label")
    _add(p, "680R label header", _sector(ra + 0.75, -42.0, 42.0, 812.0, 828.0, 0.2), "print")
    hdr = _text("INSTRUCTIONS", 10.0, 0.3)
    _add(p, "680R label print", _on_cyl(hdr, ra + 1.0, -hdr.bounds[1] / 2, 814.0), "label")
    for mesh, mat in class_d_star(40.0, 0.6):
        _add(p, "680R label star" if mat == "star" else "680R label print", _on_cyl(mesh, ra + 0.8, 0.0, 600.0),
             mat)
    for i in range(4):
        blk = _flat_poly([(0, 0), (90, 0), (90, 26), (0, 26)], 0.2)
        _add(p, "680R label print", _on_cyl(blk, ra + 0.7, -45.0, 770.0 - i * 34.0), "print")
    dia = [(-55.0, 0.0), (0.0, -17.0), (55.0, 0.0), (0.0, 17.0)]
    _add(p, "680R logo", _on_cyl(_flat_poly(dia, 0.3), ra + 0.3, 0.0, 260.0), "print")
    _add(p, "680R logo white", _on_cyl(_flat_poly([(x * 0.9, y * 0.78) for x, y in dia], 0.5), ra + 0.35, 0.0, 260.0),
         "label")
    am = _text("AMEREX", 7.0, 0.25)
    _add(p, "680R logo", _on_cyl(am, ra + 0.95, -am.bounds[1] / 2, 256.5), "print")
    return p


# ================================================================================================ signs, post, pail
def sign_parts(kind: str = "flat") -> dict:
    """A 7 x 10 in rigid plastic sign, flat (portrait, facing -y, bottom centre at the origin) or the flag (landscape,
    double-sided, in the y-z plane, its wall edge at y = 0 and sticking out to -y... see post_parts). The wording is
    the common one: FIRE EXTINGUISHER / CLASS D / COMBUSTIBLE METALS ONLY."""
    pv = _pv()
    p: dict = {}
    if kind == "flat":
        w, h = SIGN["w"], SIGN["h"]
        plate = pv.Box(bounds=(-w / 2, w / 2, 0.0, SIGN["t"], 0.0, h)).triangulate()
        _add(p, "sign", plate, "sign_white")
        band = pv.Box(bounds=(-w / 2, w / 2, -0.3, 0.0, h - 52.0, h)).triangulate()
        _add(p, "sign red", band, "sign_red")
        for txt, hh, z, mat in (("FIRE", 15.0, h - 25.0, "sign_white"), ("EXTINGUISHER", 12.0, h - 45.0, "sign_white"),
                                ("CLASS D", 26.0, 108.0, "print"), ("COMBUSTIBLE", 10.0, 40.0, "sign_red"),
                                ("METALS ONLY", 10.0, 24.0, "sign_red"), ("NO WATER - NO CO2", 7.0, 8.0, "print")):
            t = _text(txt, hh, 0.4)
            sc = min(1.0, (w - 16.0) / max(t.bounds[1], 1e-6))
            t = t.scale((sc, 1.0, 1.0), inplace=False)
            _add(p, "sign red" if mat == "sign_red" else ("sign print" if mat == "print" else "sign white print"),
                 _on_face(t, -t.bounds[1] / 2, z, -0.3 if mat != "sign_white" else -0.6, -1), mat)
        for mesh, mat in class_d_star(44.0, 0.6):
            _add(p, "sign star" if mat == "star" else "sign print", _on_face(mesh, 0.0, 78.0, -0.3, -1), mat)
        return p
    # the flag: landscape, both faces printed, in the y-z plane (it sticks out from a wall along -y)
    w, h = SIGN["h"], SIGN["w"]
    plate = pv.Box(bounds=(-SIGN["t"] / 2, SIGN["t"] / 2, -w, 0.0, 0.0, h)).triangulate()
    _add(p, "flag sign", plate, "sign_white")
    for sx in (-1, 1):
        t = _text("CLASS D", 30.0, 0.4)
        s_ = _text("FIRE EXTINGUISHER", 11.0, 0.4)
        for mesh, z, mat in ((t, 62.0, "print"), (s_, 140.0, "sign_red")):
            m = mesh.copy()
            q = np.asarray(m.points, float)
            ww = mesh.bounds[1]
            sc = min(1.0, (w - 30.0) / ww)
            q[:, 0] *= sc
            ww *= sc
            # reading along -y on the +x face, along +y on the -x face
            if sx > 0:
                m.points = np.c_[SIGN["t"] / 2 + q[:, 2], -w / 2 - ww / 2 + q[:, 0], q[:, 1] + z]
            else:
                m.points = np.c_[-SIGN["t"] / 2 - q[:, 2], -w / 2 + ww / 2 - q[:, 0], q[:, 1] + z]
            _add(p, "flag sign print" if mat == "print" else "flag sign red", m, mat)
        for mesh, mat in class_d_star(36.0, 0.5):
            m = mesh.copy()
            q = np.asarray(m.points, float)
            if sx > 0:
                m.points = np.c_[SIGN["t"] / 2 + q[:, 2], -w / 2 + q[:, 0], q[:, 1] + 28.0]
            else:
                m.points = np.c_[-SIGN["t"] / 2 - q[:, 2], -w / 2 - q[:, 0], q[:, 1] + 28.0]
            _add(p, "flag sign star" if mat == "star" else "flag sign print", m, mat)
    return p


def post_parts(with_unit: bool = True, lod: str = "full") -> dict:
    """A floor-anchored post (ours, POST) with the Amerex hook and a B570 on its front (-y) face, the flat CLASS D sign
    above it at 60-70 in, the flag sign at 80 in sticking out to the side (+x), and a 36 x 36 in keep-clear square taped
    on the floor in front. Frame: the post's axis at the origin on the floor, its front face to -y."""
    pv = _pv()
    from scene import T
    s, H = POST["s"], POST["h"]
    p: dict = {}
    bp = pv.Box(bounds=(-POST["base"] / 2, POST["base"] / 2, -POST["base"] / 2, POST["base"] / 2, 0.0,
                        POST["base_t"])).triangulate()
    ch = pv.Box(bounds=(-s / 2, s / 2, -s / 2, s / 2, POST["base_t"], H)).triangulate()
    slot = pv.Box(bounds=(-11.0, 11.0, -s / 2 - 0.4, -s / 2 + 0.2, POST["base_t"] + 30.0, H - 30.0)).triangulate()
    _add(p, "post", _merge([bp, ch]), "post_red")
    _add(p, "post slot", slot, "floor_black")
    bolts = [pv.Cylinder(center=(x, y, POST["base_t"] + 6.0), direction=(0, 0, 1), radius=9.5, height=12.0,
                         resolution=6).triangulate() for x in (-95.0, 95.0) for y in (-95.0, 95.0)]
    _add(p, "post anchors", _merge(bolts), "steel")
    R = B570["d"] / 2
    zb = HANG_BOTTOM
    M = T((0.0, -s / 2 - R - 10.0, zb))           # the B570's frame: its axis 10 mm off the post's face
    for name, (mesh, mat) in hook_parts(10.0).items():
        _add(p, name, mesh.transform(M, inplace=False), mat)
    if with_unit:
        for name, (mesh, mat) in b570_parts(lod=lod).items():
            _add(p, name, mesh.transform(M, inplace=False), mat)
    for name, (mesh, mat) in sign_parts("flat").items():
        _add(p, name, mesh.translate((0.0, -s / 2 - SIGN["t"], 60 * IN - 0.0), inplace=False), mat)
    # the flag bracket (DAL's: 1/8 x 1-1/2 in aluminium, a 3.5 in leg on the post, an 11 in flag leg) and its sign
    fz = 80 * IN
    leg = pv.Box(bounds=(s / 2, s / 2 + 3.2, -s / 2, s / 2, fz, fz + 38.0)).triangulate()
    flag = pv.Box(bounds=(s / 2, s / 2 + 11 * IN, -1.6, 1.6, fz, fz + 38.0)).triangulate()
    _add(p, "flag bracket", _merge([leg, flag]), "alu")
    for name, (mesh, mat) in sign_parts("flag").items():
        m = mesh.copy()
        q = np.asarray(m.points, float)
        m.points = np.c_[-q[:, 1] + s / 2 + 40.0, q[:, 0], q[:, 2] + fz - SIGN["w"]]       # out to +x, under the leg
        _add(p, name, m, mat)
    # the keep-clear area taped on the floor in front: 24 in wide, 36 in out (DAL suggested 36 x 36 in; on this floor a
    # 36 in square in front of a unit between two machines runs into the docked MiR250s)
    k, kw = NFPA10["keep_clear"], NFPA10["keep_clear_w"]
    y0, y1 = -s / 2 - k, -s / 2
    tape = []
    for (xa, xb, ya, yb) in ((-kw / 2, kw / 2, y0, y0 + 50), (-kw / 2, kw / 2, y1 - 50, y1),
                             (-kw / 2, -kw / 2 + 50, y0, y1), (kw / 2 - 50, kw / 2, y0, y1)):
        tape.append(pv.Box(bounds=(xa, xb, ya, yb, 0.0, 1.2)).triangulate())
    _add(p, "keep clear", _merge(tape), "floor_yellow")
    return p


def pail_parts() -> dict:
    """A 50 lb pail of Super D with its lid, bail handle, label band and a metal scoop clipped to its side. Frame: the
    pail's axis on the floor."""
    pv = _pv()
    r, h = PAIL["d"] / 2, PAIL["h"]
    p: dict = {}
    body = pv.Cylinder(center=(0, 0, h / 2), direction=(0, 0, 1), radius=r - 8.0, height=h, resolution=48)
    rims = [pv.Cylinder(center=(0, 0, z), direction=(0, 0, 1), radius=r - 4.0, height=8.0, resolution=48)
            for z in (h * 0.55, h * 0.75)]
    lid = pv.Cylinder(center=(0, 0, h + 9.0), direction=(0, 0, 1), radius=r, height=18.0, resolution=48)
    _add(p, "pail", _merge([body.triangulate(), lid.triangulate()] + [x.triangulate() for x in rims]), "pail")
    band = _sector(r - 7.5, -70.0, 70.0, 80.0, 180.0, 0.5)
    _add(p, "pail label", band, "cd_yellow")
    t = _text("SUPER D", 22.0, 0.4)
    _add(p, "pail print", _on_cyl(t, r - 6.5, -t.bounds[1] / 2, 140.0), "print")
    t = _text("CLASS D POWDER 50 LB", 9.0, 0.3)
    _add(p, "pail print", _on_cyl(t, r - 6.5, -t.bounds[1] / 2, 100.0), "print")
    for mesh, mat in class_d_star(26.0, 0.5):
        _add(p, "pail star" if mat == "star" else "pail print", _on_cyl(mesh, r - 6.6, -95.0, 130.0), mat)
    bail = _tube([(-r + 2, 0, h * 0.8), (-r + 8, 0, h + 70), (0, 0, h + 115), (r - 8, 0, h + 70), (r - 2, 0, h * 0.8)],
                 3.0, 10)
    _add(p, "pail bail", bail, "steel")
    scoop = pv.Box(bounds=(r - 4, r + 8, -45.0, 45.0, 120.0, 230.0)).triangulate()
    handle = pv.Cylinder(center=(r + 4.0, 0.0, 280.0), direction=(0, 0, 1), radius=11.0, height=100.0).triangulate()
    _add(p, "scoop", _merge([scoop, handle]), "alu")
    return p


# ================================================================================================ the MiR250's unit
# The B570 rides on the aisle side of each MiR250 (its -y side, the side away from the arm: at every dock the arm's side
# faces the machine, so this side faces the aisle), centred along it, in an 811 bracket bolted through a 6 mm aluminium
# adapter plate (ours) to the cabinet's side panel. It hangs over the MiR's own deck edge, under the arm's base, its
# label out. There it stays inside the circle the MiR250 already sweeps turning on the spot (494 mm): mounted on the
# back end instead, it made that circle 619 mm and six docks lost their pivot spot (notes/safety.md). The cabinet's door
# (the UR control box's) moves from that side to the front end (props.mir250).
MIR_MOUNT = dict(x=0.0, z_foot=310.0, plate_t=6.0, plate=(470.0, 250.0), plate_kg=1.9)
CLASS_D_ON_MIR = os.environ.get("VLAB_MIR_CLASS_D", "1") != "0"


def mir_mount() -> np.ndarray:
    """4x4: the 811 bracket's frame on a MiR250 (MiR-local: the floor at its centre, x along it, the arm's side +y):
    its web's back on the adapter plate on the cabinet's -y side, its front (-y in its frame) to the MiR's -y."""
    import props as P
    from scene import T
    y_cab = -P.MIR["W"] / 2 + 30.0                         # the cabinet's side (props.mir250)
    return T((MIR_MOUNT["x"], y_cab - MIR_MOUNT["plate_t"], MIR_MOUNT["z_foot"]))


def mir_parts() -> dict:
    """{name: (PolyData, material)}, MiR-local: the adapter plate, the 811 bracket and the B570 in it."""
    pv = _pv()
    import props as P
    M = mir_mount()
    p: dict = {}
    y_cab = -P.MIR["W"] / 2 + 30.0
    pw, ph = MIR_MOUNT["plate"]
    plate = pv.Box(bounds=(MIR_MOUNT["x"] - ph / 2, MIR_MOUNT["x"] + ph / 2, y_cab - MIR_MOUNT["plate_t"], y_cab,
                           MIR_MOUNT["z_foot"] - 5.0, MIR_MOUNT["z_foot"] - 5.0 + pw)).triangulate()
    _add(p, "class D adapter plate", plate, "alu")
    for name, (mesh, mat) in bracket811_parts().items():
        _add(p, name, mesh.transform(M, inplace=False), mat)
    Mb = M @ b570_in_811()
    for name, (mesh, mat) in b570_parts().items():
        _add(p, name, mesh.transform(Mb, inplace=False), mat)
    return p


_MIR_CACHE: dict = {}


def mir_meshes() -> dict:
    """{name: (PolyData, rgb)} for props.mir250(): the parts merged by material, cached (tessellated once a process)."""
    if "m" not in _MIR_CACHE:
        cache = HERE / ".cache"
        cache.mkdir(exist_ok=True)
        import hashlib
        import pickle
        h = hashlib.sha256((HERE / "safety.py").read_bytes() + (HERE / "props.py").read_bytes()).hexdigest()[:16]
        path = cache / f"safety_mir_{h}.pkl"
        if path.exists():
            _MIR_CACHE["m"] = pickle.loads(path.read_bytes())
        else:
            by: dict = {}
            for name, (mesh, mat) in mir_parts().items():
                by.setdefault(mat, []).append(mesh)
            out = {f"class D {mat}": (_merge(ms).clean(), colour(mat)) for mat, ms in by.items()}
            path.write_bytes(pickle.dumps(out))
            _MIR_CACHE["m"] = out
    return {k: (m.copy(), c) for k, (m, c) in _MIR_CACHE["m"].items()}


def mir_footprint() -> dict:
    """The MiR250's plan outline with the unit on it, MiR-local: its own 800 x 580 mm, and what the unit adds behind it;
    the radius it sweeps turning on the spot (about its centre: the MiR250's drive wheels are at its middle)."""
    import props as P
    pts = np.vstack([m.points for m, _ in mir_parts().values()])
    xs, ys = pts[:, 0], pts[:, 1]
    L, W = P.MIR["L"], P.MIR["W"]
    r = float(np.max(np.hypot(xs, ys)))
    return dict(mir=(-L / 2, L / 2, -W / 2, W / 2),
                unit=(float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max())),
                beside_mm=float(-W / 2 - ys.min()), along=(float(xs.min()), float(xs.max())),
                top_mm=float(pts[:, 2].max()), bottom_mm=float(pts[:, 2].min()), r_unit=r,
                r_turn=max(r, float(math.hypot(L / 2, W / 2))), r_turn_mir=float(math.hypot(L / 2, W / 2)))


# ================================================================================================ where they go
# The fixed units, world (setup_lab's floor; x along the aisle, the north row's fronts at y -1562, the south row's at
# -6238). Each sits in a gap between machines, behind the row's front line, so no MiR250 dock, approach lane or pivot
# spot reaches it (``plan_check``), it hangs outside the station's own powder area, and it is seen from the aisle.
# kind: "b570" (on a post, its front to `face`), "680r" (the wheeled unit), "pail".
PLACES = [
    # station, kind, x, y, face (the direction its front looks: -1 to -y, +1 to +y), what it covers. Each is the
    # nearest spot to its station that clears everything (safety_render.place_search, 50 mm grid, then rounded)
    ("glovebox", "b570", -8050.0, -1150.0, -1, "the floor glovebox (west of it)"),
    ("repowder", "b570", -5150.0, -1450.0, -1, "the rePowder atomizer (its fire point, west of it)"),
    ("repowder", "680r", -6300.0, -1000.0, -1, "the rePowder atomizer (its fire point)"),
    ("repowder", "pail", -5650.0, -1475.0, -1, "the rePowder atomizer (its fire point)"),
    ("vlm", "b570", 1750.0, -1150.0, -1, "both Shuttles' openings (in the gap between them)"),
    ("aconity", "b570", 8495.0, -1150.0, -1, "the Aconity MIDI and its depowdering (east of it)"),
    ("aconity", "pail", 8485.0, -800.0, -1, "the Aconity MIDI"),
    ("packaging", "b570", 10786.0, -2050.0, -1, "the packaging station (east of its dock)"),
    ("ded", "b570", 4900.0, -6650.0, 1, "the MX-Lab DED (east of it)"),
    ("eos_m400", "b570", -9450.0, -9550.0, 1, "the EOS M 400-4 (in front of it)"),
    ("eos_m400", "680r", -10200.0, -9050.0, 1, "the EOS M 400-4"),
]
# The sieving cell has no spot of its own: its bench stands 85 mm from the rePowder and 20 mm from Shuttle 1, and its
# front is its MiR250's dock and target post. It is covered by the docked MiR's own unit while a MiR works there, and
# by the rePowder's fire point and the unit between the Shuttles (out/safety.json, "walks").
# where each hazard is, for the walk: the point a person would fight a fire from, at the station's working face
HAZARDS = {
    "glovebox": (-7300.0, -1250.0), "repowder": (-3500.0, -1950.0), "sieve_cell": (-1982.0, -1650.0),
    "vlm": (0.0, -1650.0), "vlm2": (3630.0, -1650.0), "aconity": (6950.0, -1650.0), "packaging": (10050.0, -1700.0),
    "ded": (3900.0, -6150.0), "eos_m400": (-9450.0, -9650.0),
}


def floor_parts(lod: str = "lab") -> dict:
    """{name: (PolyData, material)}, world: every fixed unit of PLACES where it stands (a post with its B570, signs and
    keep-clear area; a 680R; a pail), turned to face the way PLACES says."""
    from scene import T, R
    out: dict = {}
    built = {"b570": post_parts(True, lod), "680r": w680r_parts(), "pail": pail_parts()}
    for station, kind, x, y, face, _ in PLACES:
        M = T((x, y, 0.0)) @ R((0, 0, 1), 0.0 if face < 0 else 180.0)
        for name, (mesh, mat) in built[kind].items():
            _add(out, f"{kind} {name}", mesh.transform(M, inplace=False), mat)
    return out


def floor_meshes() -> dict:
    """{name: (PolyData, rgb, specular)} for setup_lab.build: floor_parts merged by material, cached on safety.py."""
    import hashlib
    import pickle
    cache = HERE / ".cache"
    cache.mkdir(exist_ok=True)
    h = hashlib.sha256((HERE / "safety.py").read_bytes()).hexdigest()[:16]
    path = cache / f"safety_floor_{h}.pkl"
    if path.exists():
        return pickle.loads(path.read_bytes())
    by: dict = {}
    for name, (mesh, mat) in floor_parts().items():
        by.setdefault(mat, []).append(mesh)
    out = {}
    for mat, ms in by.items():
        m = _merge(ms).clean().triangulate()
        if m.n_cells > 20000:                  # at lab scale: a quarter of the triangles (quadric decimation)
            m = m.decimate(0.75).compute_normals(split_vertices=True, feature_angle=35.0)
        out[f"class D {mat}"] = (m, colour(mat), MATS[mat][4])
    path.write_bytes(pickle.dumps(out))
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("what", nargs="?", default="report")
    a = ap.parse_args()
    import safety_render as SR
    SR.main(a.what)
