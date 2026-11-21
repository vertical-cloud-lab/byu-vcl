"""The stir bar's coupling with the fan under the deck, so that the deck is the spacer (magpylib >= 6.1).

Asked by @benwhitney5463 on PR #348 (2026-11-19): the 4.6 mm spacer is not enough for steady
stirring, and a bigger one puts the vial even higher. Could the fan go under the 9 mm deck, with
the vial standing on the deck?

Same model and calibration as ../analysis/coupling_vs_height.py (field_check.py's magnets, Hall
element and bars), but in terms of g, the gap from the drive magnets' top faces to the vial's
outside bottom:

    g =  2.385 mm  today, vial seated on the holder's 1.2 mm floor (z 25.03 - 22.645)
    g =  5.385     vial 3 mm up: where Ben saw the fan stop on 2026-11-04 (the "edge", pull 1.0)
    g =  6.985     on the 4.6 mm spacer (2026-11-05 on; 2026-11-19: "not big enough")
    g = 10.185     under a 9 mm deck: 1.185 from the magnets to the frame's top face, which is
                   against the deck's underside (as from the magnets to the holder floor's
                   underside today), plus the deck
    g = 11.185     under a 10 mm deck (Cubware's PandaDeck.step)

Two drives: today's two 1/4 x 1/16 in N52 discs, and two of the same discs stacked in each pocket
(1/4 x 1/8 in), which the under-deck layout has room for. Pull is relative to today's drive at the
edge with the same core; pull-out torque is the most the coupling can turn the bar.

Run: python coupling_through_deck.py > coupling_through_deck_output.txt
"""
import sys
from pathlib import Path

import numpy as np
import magpylib as magpy

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from field_check import BR, CC, MAG_D, MM, ZTOP, FLOOR_IN, bar, hall_peak  # noqa: E402

SEAT = 25.03                                  # vial's outside bottom when seated today, z
G_TODAY = SEAT - ZTOP                         # 2.385
GAPS = {"seated (today's holder)": G_TODAY, "3 mm up: the edge, 11-04": G_TODAY + 3.0,
        "4.6 mm spacer": G_TODAY + 4.6, "under a 9 mm deck": 1.185 + 9.0, "under a 10 mm deck": 1.185 + 10.0}
GRID = np.round(np.arange(2.0, 14.01, 0.5), 2)
BARS = {"15 x 6 mm (today's)": dict(axis=3.0, L=15.0, d=6.0, cores=[(0.5, 3, 10), (0.8, 3, 12), (0.6, 4, 12), (1.0, 4, 12)]),
        "12 x 3 mm (Pioreactor's)": dict(axis=1.5, L=12.0, d=3.0, cores=[(0.5, 1.5, 9), (0.8, 1.5, 10), (0.6, 2, 10), (1.0, 2, 10)])}
DRIVES = {"1/4 x 1/16 in (today's)": 1.59, "1/4 x 1/8 in (two stacked)": 3.18}
MESH = 300


def drive(t, ang=0.0):
    """Two discs, N up at +x and S up at -x, top faces at ZTOP whatever their thickness."""
    c = magpy.Collection()
    for sgn in (+1, -1):
        c.add(magpy.magnet.Cylinder(polarization=(0, 0, sgn * BR), dimension=(MAG_D * MM, t * MM),
                                    position=(sgn * CC / 2 * MM, 0, (ZTOP - t / 2) * MM)))
    c.rotate_from_angax(ang, "z", anchor=0)
    return c


def zaxis(g, b):
    return FLOOR_IN + b["axis"] + (g - G_TODAY)


def fz(t, core, g, b):
    F, _ = magpy.getFT(drive(t), bar(0.0, *core, zaxis(g, b)), meshing=MESH)
    return -float(F[2])


def pullout(t, core, g, b):
    def tz(a):
        return abs(float(magpy.getFT(drive(t), bar(a, *core, zaxis(g, b)), meshing=MESH)[1][2]))
    lags = np.arange(0.0, 181.0, 7.5)
    v = [tz(a) for a in lags]
    i = int(np.argmax(v))
    v += [tz(a) for a in np.arange(max(lags[i] - 7.5, 0), lags[i] + 7.6, 1.5)]
    return max(v) * 1e3


def drag(b, rpm):
    """Water drag on the bar, upper bound (Cd 1, still water): rho Cd d w^2 L^4 / 64, mN m."""
    w = rpm * 2 * np.pi / 60
    return 1000 * b["d"] * 1e-3 * w ** 2 * (b["L"] * 1e-3) ** 4 / 64 * 1e3


def main():
    edge = GAPS["3 mm up: the edge, 11-04"]
    t0 = DRIVES["1/4 x 1/16 in (today's)"]
    print("Coupling with the fan under the deck; model and calibration as ../analysis/coupling_vs_height.py")
    print("g = gap from the drive magnets' top faces to the vial's outside bottom, mm")
    print("pull = magnets' pull on the bar (= friction under it, = thrust on the fan's bearing),")
    print("       relative to today's drive at the edge (g %.3f) with the same core. Under ~0.7 it started" % edge)
    print("       from rest on 11-05; 0.5 was the aim. Ranges are over the four guessed cores.\n")
    rows = {}
    for bname, b in BARS.items():
        ref = [fz(t0, c, edge, b) for c in b["cores"]]
        for dname, t in DRIVES.items():
            pulls = np.array([[fz(t, c, g, b) / r for g in GRID] for c, r in zip(b["cores"], ref)])
            rows[(bname, dname)] = pulls
            print(f"== {bname} bar, {dname} drive: pull against g ==")
            print("   g    " + "".join(f"{g:>6.1f}" for g in GRID))
            print("   min  " + "".join(f"{v:6.2f}" for v in pulls.min(0)))
            print("   max  " + "".join(f"{v:6.2f}" for v in pulls.max(0)))
            print()
    print("== At the five gaps ==")
    print(f"{'bar':<26}{'drive':<28}{'where':<26}{'g':>7}{'pull':>13}{'pull-out mN m':>18}{'drag 600/1200 rpm':>20}")
    out = []
    for bname, b in BARS.items():
        ref = [fz(t0, c, edge, b) for c in b["cores"]]
        for dname, t in DRIVES.items():
            for where, g in GAPS.items():
                p = [fz(t, c, g, b) / r for c, r in zip(b["cores"], ref)]
                T = [pullout(t, c, g, b) for c in b["cores"]]
                out.append((bname, dname, where, g, min(p), max(p), min(T), max(T)))
                print(f"{bname:<26}{dname:<28}{where:<26}{g:>7.2f}{min(p):>7.2f}-{max(p):<5.2f}"
                      f"{min(T):>11.3f}-{max(T):<6.3f}{drag(b, 600):>9.3f} / {drag(b, 1200):.3f}")
    print()
    print("Hall element's smaller peak over a turn, bar following, mT (US1881 needs 9.5 worst case);")
    print("the element sits beside the magnets exactly as today, so only the bar's distance changes:")
    b = BARS["15 x 6 mm (today's)"]
    for where, g in GAPS.items():
        hs = [hall_peak(-11.70, 22.655, (c[0], c[1], c[2], zaxis(g, b))) for c in b["cores"]]
        print(f"   15 x 6 mm bar, {where:<26} g {g:5.2f}: {min(hs):5.1f} to {max(hs):5.1f}")
    print(f"   drive magnets alone: {hall_peak(-11.70, 22.655):5.1f}")
    return out


if __name__ == "__main__":
    main()
