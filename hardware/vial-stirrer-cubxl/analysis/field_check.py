"""Field checks for the stirrer's Hall sensor and stir bar (magpylib >= 5).

Geometry from onshape/vial_stirrer.fs, in mm with z = 0 at the deck's top face:
two 1/4 x 1/16 in N52 discs (polarization 1.45 T), opposite poles up, centres 4.9 mm
either side of the axis, faces at z 22.645. US1881 (TO-92UA) flat on the pocket ceiling,
branded face down at z 22.23, package top edge at r 10.3 on -x. Melexis puts the element
1.40-1.58 mm in from the top edge and 0.425-0.46 mm under the face, depending on where
the part was made. Vial on the floor: inner bottom at z 26.63.

The bar's magnet core is not published, so it is swept: a cylinder magnetised along its
length, coupled (its moment along the drive's field, which runs from the N-up magnet to
the S-up one). Run: python field_check.py > field_check_output.txt
"""
import numpy as np
import magpylib as magpy

MM = 1e-3
BR, CC, ZTOP, MAG_D, MAG_T = 1.45, 9.8, 22.645, 6.35, 1.59
FLOOR_IN = 26.63
ANGS = np.arange(0.0, 360.0, 2.0)


def drive(ang, cc=CC):
    c = magpy.Collection()
    for sgn in (+1, -1):  # N up at +x, S up at -x
        c.add(magpy.magnet.Cylinder(polarization=(0, 0, sgn * BR), dimension=(MAG_D * MM, MAG_T * MM),
                                    position=(sgn * cc / 2 * MM, 0, (ZTOP - MAG_T / 2) * MM)))
    c.rotate_from_angax(ang, "z", anchor=0)
    return c


def bar(ang, J, core_d, core_l, zaxis):
    m = magpy.magnet.Cylinder(polarization=(0, 0, -J), dimension=(core_d * MM, core_l * MM), position=(0, 0, zaxis * MM))
    m.rotate_from_angax(90, "y", anchor=(0, 0, zaxis * MM))  # axis along x, moment along -x
    m.rotate_from_angax(ang, "z", anchor=0)
    return m


def hall_peak(x, z, barargs=None):
    """Smaller of the two peaks of Bz at the element over one turn, mT."""
    s = (x * MM, 0, z * MM)
    bz = []
    for a in ANGS:
        b = drive(a).getB(s)[2]
        if barargs:
            b += bar(a, *barargs).getB(s)[2]
        bz.append(b)
    bz = np.array(bz) / MM  # T -> mT
    return min(bz.max(), -bz.min())


def bh(z, cc=CC, half_len=0.0):
    """Horizontal field at height z on the axis, or averaged along a bar of that half-length, mT."""
    xs = np.linspace(-half_len, half_len, 31) if half_len else [0.0]
    return abs(np.mean([drive(0, cc).getB((x * MM, 0, z * MM))[0] for x in xs])) / MM


if __name__ == "__main__":
    print("US1881 worst-case trip points: BOP <= +9.5 mT, BRP >= -9.5 mT\n")
    print("Hall element, drive magnets only:")
    for label, x, z in [("spot 1.40 mm in, 0.425 mm deep", -11.70, 22.655), ("spot 1.58 mm in, 0.46 mm deep", -11.88, 22.69),
                        ("0.5 mm further out", -12.20, 22.655), ("1.0 mm further out", -12.70, 22.655)]:
        print(f"  {label:34s} r {-x:5.2f}: +-{hall_peak(x, z):4.1f} mT")
    print("\nHall element with a coupled bar (bar axis 3 mm above the inner floor, 15 x 6 mm bar):")
    for J, d, l in [(0.5, 3, 10), (0.8, 3, 12), (0.6, 4, 12), (1.0, 4, 12)]:
        a = hall_peak(-11.70, 22.655, (J, d, l, FLOOR_IN + 3.0))
        b = hall_peak(-12.70, 22.655, (J, d, l, FLOOR_IN + 3.0))
        print(f"  core {d} x {l} mm, J {J} T: nominal +-{a:4.1f} mT, 1 mm further out +-{b:4.1f} mT")
    a = hall_peak(-11.70, 22.655, (0.6, 4, 12, FLOOR_IN + 4.0))
    print(f"  core 4 x 12 mm, J 0.6 T, vial on a 1 mm spacer: nominal +-{a:4.1f} mT")
    print("\nHorizontal field at the bar:")
    print(f"  15 x 6 mm bar, centre (z {FLOOR_IN + 3:.2f}): {bh(FLOOR_IN + 3):4.1f} mT; mean over its length {bh(FLOOR_IN + 3, half_len=7.5):4.1f} mT")
    print(f"  3 x 12 mm bar, centre (z {FLOOR_IN + 1.5:.2f}): {bh(FLOOR_IN + 1.5):4.1f} mT; mean over its length {bh(FLOOR_IN + 1.5, half_len=6):4.1f} mT")
    for t in (1, 2, 3):
        print(f"  15 x 6 mm bar on a {t} mm spacer: {bh(FLOOR_IN + 3 + t):4.1f} mT")
