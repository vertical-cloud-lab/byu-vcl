#!/usr/bin/env python3
"""A printable 5 mm C-CS spacer ring for the lid camera, modelled on Amazon B09STVLLVY.

    python c_cs_spacer.py            # writes ../exports/c_cs_spacer_{A..H}.stl, c_cs_spacer.json,
                                     # c_cs_spacer_sizes_C-H.stl (rings C-H laid out as one plate)
                                     # and ../renders/c_cs_spacer.png, c_cs_spacer_sizes.png

The listing (camera/README.md, 2026-10-23 21:20 UTC) gives a ring 30 mm across with a 25 mm
threaded bore and 5 mm of spacing, plus a threaded end of about 4 mm: 9 mm in all. Both threads
are the C-mount's 1"-32 UN, right-handed. The lens screws into the female thread from the
bottom face; the male threaded end screws into the camera's knurled back-focus ring.

It prints lens-face down, so the female thread starts on the bed and the male thread is on
top. The male end is narrower than the female bore under it, so the bore needs a roof: a
0.4 mm disc bridged across it at 4.6-5.0 mm, which leaves 4.6 mm of female thread. **Cut the
disc out after printing** (a hobby knife round the inside of the male end), or the camera sees
plastic. The ring left under the male end is the real roof.

The threads are generated here as a triangle mesh, not in CadQuery: a helical thread is a
radius that depends on the angle and the height, r(theta, z), so each surface is a grid in
(theta, z). The profile is the basic 60-degree UN form, moved out by `clear` (female) or in
(male), radially. The variants differ only in that clearance and are marked by notches on the
rim, one per letter: one notch = A, two = B, and so on to eight = H.

A and B (printed 2026-10-23) both came out too small on both ends at the robot (2026-10-27): the
threaded end was loose in the knurled ring and the lens would not go into either bore. The
slicer was not the cause: the G-code of that print traces both threads within 0.01 mm of this
model (`../slice/c_cs_gcode_check.py`). So C-H (2026-10-28) step both ends bigger:
the threaded end 0.06 mm a side per letter, from 0.06 under basic (C) to 0.24 over (H), and the
bore 0.04 mm a side per letter, from 0.38 over basic (C) to 0.58 (H). Beyond about 0.33 a side
a bore no longer overlaps the lens's thread crests as modelled, so the bigger bores only work
if the printed bore really is that much smaller than drawn, which is what A and B suggest.
"""
from __future__ import annotations

import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
RENDERS = HERE.parent / "renders"

P = 25.4 / 32                 # 1"-32 UN pitch, 0.79375 mm
H = np.sqrt(3) / 2 * P        # height of the sharp 60-degree V
R_MAJ = 25.4 / 2              # basic major radius
R_PITCH = R_MAJ - 3 * H / 8   # basic pitch radius (pitch diameter 24.884 mm)
T30 = np.tan(np.radians(30))
MALE_ROOT = R_MAJ - 17 / 24 * H   # UN external minor radius, 12.213 mm
FEMALE_CREST = R_MAJ - 5 / 8 * H  # UN internal minor radius, 12.270 mm
FEMALE_ROOT = R_MAJ + H / 16      # a little past the basic major, so the crest of a male never bottoms


@dataclass
class Spacer:
    name: str = "A"
    male_clear: float = 0.12      # radial, mm: the printed male thread is this much smaller than basic
    female_clear: float = 0.22    # radial, mm: the printed female thread is this much bigger
    od: float = 30.0              # flange diameter
    spacing: float = 5.0          # flange height: what the ring adds between lens and sensor
    roof: float = 0.4             # bridged disc at the top of the female bore, cut out after printing
    spigot: float = 4.0           # male threaded end
    bore: float = 22.1            # inside diameter of the male end
    relief: float = 0.5           # unthreaded neck at the foot of the male end, so the faces seat
    entry: float = 0.4            # 45-degree lead-in on the female thread, at the lens face
    flutes: int = 30              # grip flutes round the flange
    flute_depth: float = 0.25
    notches: int = 1              # variant mark
    n_theta: int = 360            # mesh resolution
    dz: float = 0.04


def wrap(u):
    return (u + P / 2) % P - P / 2


def tooth(theta, z):
    """Radius of the basic thread surface (no truncation) at angle theta and height z."""
    u = wrap(z - P * theta / (2 * np.pi))       # right-handed helix: u is constant along it
    return R_PITCH - (np.abs(u) - P / 4) / T30


def male_r(s: Spacer, theta, z):
    return np.clip(tooth(theta, z) - s.male_clear, MALE_ROOT - s.male_clear, R_MAJ - s.male_clear)


def female_r(s: Spacer, theta, z):
    return np.clip(tooth(theta, z) + s.female_clear, FEMALE_CREST + s.female_clear,
                   FEMALE_ROOT + s.female_clear)


def rim_r(s: Spacer, theta, z):
    """Flange outside: grip flutes, the variant notches and 45-degree edge chamfers."""
    r = s.od / 2 - s.flute_depth * (1 - np.cos(s.flutes * theta)) / 2
    for k in range(s.notches):
        d = np.abs(np.angle(np.exp(1j * (theta - 0.3 * k))))   # angle from the k-th notch
        r = np.minimum(r, s.od / 2 - 0.8 + d * s.od / 2)
    return r - np.maximum(0.0, 0.3 - z) - np.maximum(0.0, z - (s.spacing - 0.4))


def heights(z0, z1, dz):
    n = max(1, int(round((z1 - z0) / dz)))
    return list(np.linspace(z0, z1, n + 1))


def rows(s: Spacer):
    """(z, radius function) rows for the outer and the inner surface, bottom to top."""
    z_roof, z_top = s.spacing - s.roof, s.spacing + s.spigot
    neck = s.spacing + s.relief
    root = MALE_ROOT - s.male_clear

    def male(th, z):
        r = male_r(s, th, z)
        r = np.minimum(r, root + max(0.0, z - neck))     # thread fades in above the neck
        return np.minimum(r, root + max(0.0, z_top - z))  # and is chamfered off at the tip

    outer = [(z, lambda th, z=z: rim_r(s, th, z)) for z in (0.0, 0.3, s.spacing - 0.4, s.spacing)]
    outer += [(z, lambda th, z=z: male(th, z)) for z in heights(s.spacing, z_top, s.dz)]

    def female(th, z):
        return np.maximum(female_r(s, th, z), FEMALE_ROOT + s.female_clear + s.entry - z)

    inner = [(z, lambda th, z=z: female(th, z)) for z in heights(0.0, z_roof, s.dz)]
    inner += [(z_roof, lambda th: 0.02 + 0 * th), (s.spacing, lambda th: 0.02 + 0 * th)]  # the roof disc
    inner += [(s.spacing, lambda th: s.bore / 2 + 0 * th), (z_top - 0.3, lambda th: s.bore / 2 + 0 * th),
              (z_top, lambda th: s.bore / 2 + 0.3 + 0 * th)]
    return outer, inner


def mesh(s: Spacer):
    th = np.linspace(0, 2 * np.pi, s.n_theta, endpoint=False)
    outer, inner = rows(s)
    verts, faces = [], []

    def ring(z, f):
        r = f(th)
        verts.append(np.column_stack([r * np.cos(th), r * np.sin(th), np.full_like(th, z)]))
        return (len(verts) - 1) * s.n_theta

    i = np.arange(s.n_theta)
    j = (i + 1) % s.n_theta

    def band(a, b, flip):   # quads between ring a (lower) and ring b (upper)
        t1 = np.column_stack([a + i, a + j, b + j])
        t2 = np.column_stack([a + i, b + j, b + i])
        t = np.vstack([t1, t2])
        faces.append(t[:, ::-1] if flip else t)

    o = [ring(z, f) for z, f in outer]
    n = [ring(z, f) for z, f in inner]
    for a, b in zip(o, o[1:]):
        band(a, b, False)
    for a, b in zip(n, n[1:]):
        band(a, b, True)
    band(o[0], n[0], True)     # bottom cap, from the outside in, facing down
    band(o[-1], n[-1], False)  # top cap, facing up
    return np.vstack(verts), np.vstack(faces)


def write_stl(path: Path, v, f):
    tri = v[f]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    with open(path, "wb") as fh:
        fh.write(b"c_cs_spacer.py".ljust(80, b" "))
        fh.write(struct.pack("<I", len(f)))
        data = np.zeros(len(f), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        data["n"], data["v"] = nrm, tri
        fh.write(data.tobytes())


def section_figure(variants, path: Path, ncols: int | None = None, title: str | None = None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ncols = ncols or len(variants)
    nrows = -(-len(variants) // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.3 * ncols, 6.0 * nrows), dpi=130, squeeze=False)
    for ax, s in zip(axes.flat, variants):
        th = np.pi   # away from the variant notches, on a flute crest
        z_roof, z_top = s.spacing - s.roof, s.spacing + s.spigot
        outer, inner = rows(s)
        zo = [z for z, _ in outer]; ro = [float(f(np.array([th]))[0]) for _, f in outer]
        zi = [z for z, _ in inner]; ri = [float(f(np.array([th]))[0]) for _, f in inner]
        poly_r = ro + ri[::-1]; poly_z = zo + zi[::-1]
        ax.fill(poly_r, poly_z, color="#2b2b2e", label="printed ring (section at 180°)")
        ax.fill([0.02, s.bore / 2, s.bore / 2, 0.02], [z_roof, z_roof, s.spacing, s.spacing],
                color="#ff7800", label="roof disc: cut out after printing")
        zz = np.linspace(0.0, z_roof, 400)
        lens = np.clip(tooth(th, zz), MALE_ROOT, R_MAJ)
        ax.plot(lens, zz, color="#3b82f6", lw=1.6, label="lens thread, basic size")
        zz = np.linspace(s.spacing, z_top, 400)
        ring = np.clip(tooth(th, zz), FEMALE_CREST, R_MAJ + H / 8)
        ax.plot(ring, zz, color="#16a34a", lw=1.6, label="knurled ring's thread, basic size")
        ax.set_xlim(10.4, 15.4); ax.set_ylim(-0.3, z_top + 0.4); ax.set_aspect("equal")
        ax.set_xlabel("radius (mm)"); ax.set_ylabel("height above the lens face (mm)")
        male = f"male {'−' if s.male_clear > 0 else '+'}{abs(s.male_clear):.2f}"
        ax.set_title(f"Variant {s.name} ({s.notches} notch{'es' if s.notches > 1 else ''}): "
                     f"{male}, female +{s.female_clear:.2f} mm", fontsize=10)
        ax.axhline(s.spacing, color="0.6", lw=0.6, ls=":")
        ax.text(15.3, s.spacing + 0.08, "seats on the knurled ring", ha="right", fontsize=8, color="0.35")
        ax.text(15.3, 0.08, "lens rim seats here (on the bed)", ha="right", fontsize=8, color="0.35")
        ax.grid(alpha=0.25)
    axes.flat[0].legend(loc="upper left", fontsize=8, framealpha=0.95)
    fig.suptitle(title or "C–CS spacer ring, 1\"-32 UN both ends: half-section through the axis", fontsize=12)
    fig.tight_layout()
    fig.savefig(path)


VARIANTS = [Spacer("A", 0.12, 0.22, notches=1), Spacer("B", 0.22, 0.32, notches=2)]
# 2026-10-28: both ends bigger than A and B. Male clearance negative = bigger than basic.
SIZES = [Spacer(n, round(0.06 - 0.06 * k, 2), round(0.38 + 0.04 * k, 2), notches=3 + k)
         for k, n in enumerate("CDEFGH")]
PLATE_PITCH = 40.0   # ring centres on the C-H plate: C D E along the front row, F G H behind


def plate_xy(k: int):
    """Centre of ring k (0 = C) in c_cs_spacer_sizes_C-H.stl: +x to the right, +y to the back."""
    return (k % 3 - 1) * PLATE_PITCH, (k // 3 - 0.5) * PLATE_PITCH


def main():
    import trimesh

    EXPORTS.mkdir(exist_ok=True)
    report = {"thread": {"pitch_mm": P, "basic_major_d": 2 * R_MAJ, "basic_pitch_d": 2 * R_PITCH,
                         "male_root_d": 2 * MALE_ROOT, "female_crest_d": 2 * FEMALE_CREST},
              "variants": []}
    plate_v, plate_f = [], []
    for s in VARIANTS + SIZES:
        v, f = mesh(s)
        if s in SIZES:
            k = SIZES.index(s)
            plate_f.append(f + sum(len(x) for x in plate_v))
            plate_v.append(v + np.array([*plate_xy(k), 0.0]))
        path = EXPORTS / f"c_cs_spacer_{s.name}.stl"
        write_stl(path, v, f)
        m = trimesh.load(path)
        lo, hi = m.bounds
        rec = {**asdict(s), "stl": path.name, "triangles": int(len(f)), "watertight": bool(m.is_watertight),
               "winding_consistent": bool(m.is_winding_consistent), "volume_mm3": round(float(m.volume), 2),
               "mass_g_pla": round(float(m.volume) * 1.24e-3, 2),
               "bounds_mm": [[round(x, 3) for x in lo], [round(x, 3) for x in hi]],
               "female_thread_depth_mm": s.spacing - s.roof,
               "male_crest_d": round(2 * (R_MAJ - s.male_clear), 3),
               "male_root_d": round(2 * (MALE_ROOT - s.male_clear), 3),
               "female_crest_d": round(2 * (FEMALE_CREST + s.female_clear), 3),
               "female_root_d": round(2 * (FEMALE_ROOT + s.female_clear), 3),
               "male_wall_at_root_mm": round(MALE_ROOT - s.male_clear - s.bore / 2, 3)}
        report["variants"].append(rec)
        print(f"{s.name}: {len(f)} triangles, watertight {m.is_watertight}, volume {m.volume:.1f} mm3, "
              f"bounds {lo.round(2)} .. {hi.round(2)}")
    path = EXPORTS / "c_cs_spacer_sizes_C-H.stl"
    write_stl(path, np.vstack(plate_v), np.vstack(plate_f))
    m = trimesh.load(path)
    report["plate_C-H"] = {"stl": path.name, "pitch_mm": PLATE_PITCH,
                           "centres_mm": {s.name: plate_xy(k) for k, s in enumerate(SIZES)},
                           "watertight": bool(m.is_watertight), "bodies": len(m.split(only_watertight=False)),
                           "bounds_mm": [[round(x, 3) for x in b] for b in m.bounds]}
    print(f"plate C-H: {len(m.faces)} triangles, watertight {m.is_watertight}, bounds {m.bounds.round(2).tolist()}")
    (EXPORTS / "c_cs_spacer.json").write_text(json.dumps(report, indent=2) + "\n")
    RENDERS.mkdir(exist_ok=True)
    section_figure(VARIANTS, RENDERS / "c_cs_spacer.png")
    section_figure(SIZES, RENDERS / "c_cs_spacer_sizes.png", ncols=3,
                   title="C–CS spacer rings C–H (2026-10-28): both ends bigger than A and B, half-section")


if __name__ == "__main__":
    main()
