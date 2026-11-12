"""Shared geometry, positions and masses for the Provenance Eyes headset.

Pure Python (no bpy, no numpy), so both the Blender build script and
mass_budget.py import the same numbers.

Frame: metres and grams. The origin is the midpoint between the two ear
canals (the tragion line, "the ear line"). x points forward (out of the
face), y to the wearer's left, z up. The Frankfort plane is roughly z = 0.
"""

import math

# --- Head form ---------------------------------------------------------------
# Cranium as an ellipsoid: 192 mm long, 150 mm wide, 130 mm from the ear line to
# the top of the head. Close to a 50th-percentile adult head (head circumference
# about 570 mm).
HEAD_CENTER = (0.005, 0.0, 0.015)
HEAD_SEMI_AXES = (0.096, 0.075, 0.115)
HEAD_MASS_G = 4500.0  # whole head, for context only; not part of the device

# --- Headband (ratchet suspension, like a face-shield headgear) ----------------
BAND = dict(
    front_z=0.050,    # centre of the band on the forehead, 50 mm above the ear line
    back_z=0.012,     # centre of the band at the back, low on the occiput
    height=0.025,     # 25 mm band
    thickness=0.004,  # 4 mm including the sweatband
    gap=0.003,        # padding between skull model and band
)
CROWN = dict(width=0.022, thickness=0.003, lean_deg=6.0)

# --- Pods ---------------------------------------------------------------------
# "Headlamp" layout: the Pi rides at the front with the camera, the battery at the
# back as the counterweight, the mics at the temples. Same idea as a headlamp with
# a rear battery pack (Petzl NAO RL: 145 g total, 80 g battery at the back).
FRONT_POD = dict(
    base=(0.013, 0.074, 0.036),   # radial depth, width, height: holds the Pi Zero 2 W
    head=(0.016, 0.034, 0.030),   # hinged camera head
    tilt_deg=25.0,                # camera looks 25 degrees below horizontal
)
TEMPLE_POD_THETA_DEG = 70.0          # 0 = forehead, 90 = directly above the ear
TEMPLE_POD = dict(size=(0.009, 0.032, 0.016))      # out, along band, up
TEMPLE_POD_RIGHT = dict(size=(0.011, 0.040, 0.018))  # carries the button and haptic motor
REAR_POD = dict(width=0.072, height=0.040, depth=0.018, r_in=0.062, z=0.056, gap=0.004)

# --- Battery options ------------------------------------------------------------
# Masses of the cells are estimates: PiSugar publishes no weights.
#   pisugar3   - PiSugar 3 board with its own 1200 mAh cell (the default build)
#   lipo3000   - the same board with a larger 1S LiPo pouch (check PiSugar supports it first)
#   beltpack   - no battery on the head: a USB power bank in a pocket, cable down the neck
BATTERY_OPTIONS = {
    "pisugar3": dict(board_g=10.0, cell_g=24.0, cell=(0.006, 0.040, 0.030), label="PiSugar 3, 1200 mAh"),
    "lipo3000": dict(board_g=10.0, cell_g=55.0, cell=(0.008, 0.050, 0.034), label="PiSugar 3 board + 3000 mAh LiPo"),
    "beltpack": dict(board_g=0.0, cell_g=0.0, cell=None, label="belt-pack power bank (off the head)"),
}

# Headgear: about 145 g for a Jackson Safety 370 (reseller figure); 3M does not
# publish the H8A's weight. Split between band, crown strap and ratchet as a guess.
HEADGEAR_G = dict(band=80.0, crown=20.0, ratchet=45.0)


# --- Small vector helpers -------------------------------------------------------
def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def mul(a, s):
    return tuple(x * s for x in a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def unit(a):
    n = math.sqrt(dot(a, a))
    return mul(a, 1.0 / n)


def ray_ellipsoid(o, d, c=HEAD_CENTER, r=HEAD_SEMI_AXES):
    """Distance along unit vector d from o (inside the ellipsoid) to its surface."""
    oc = [(o[i] - c[i]) / r[i] for i in range(3)]
    dd = [d[i] / r[i] for i in range(3)]
    A = sum(x * x for x in dd)
    B = 2.0 * sum(oc[i] * dd[i] for i in range(3))
    C = sum(x * x for x in oc) - 1.0
    return (-B + math.sqrt(B * B - 4.0 * A * C)) / (2.0 * A)


# --- Band frame ------------------------------------------------------------------
def band_frame():
    """Return (p0, u, v, w): plane centre, forward axis, left axis, band-normal (up)."""
    t = math.atan2(BAND["front_z"] - BAND["back_z"], 2.0 * HEAD_SEMI_AXES[0])
    u = (math.cos(t), 0.0, math.sin(t))
    v = (0.0, 1.0, 0.0)
    w = (-math.sin(t), 0.0, math.cos(t))
    p0 = (HEAD_CENTER[0], 0.0, 0.5 * (BAND["front_z"] + BAND["back_z"]))
    return p0, u, v, w


def band_dir(theta):
    _, u, v, _ = band_frame()
    return add(mul(u, math.cos(theta)), mul(v, math.sin(theta)))


def band_inner_radius(theta):
    """Radius (from the band centre line) of the band's inner face at angle theta.

    The band is a generalised cylinder along w, so it must clear the head over its
    whole height: take the largest head radius across the band and add the gap.
    """
    p0, _, _, w = band_frame()
    d = band_dir(theta)
    h = BAND["height"]
    best = 0.0
    for k in range(-4, 5):
        o = add(p0, mul(w, 0.5 * h * k / 4.0))
        best = max(best, ray_ellipsoid(o, d))
    return best + BAND["gap"]


def band_point(theta, s=0.0, out=0.0):
    """Point on the band: angle theta, height s along w, `out` metres beyond the inner face."""
    p0, _, _, w = band_frame()
    d = band_dir(theta)
    return add(add(p0, mul(w, s)), mul(d, band_inner_radius(theta) + out))


def band_tangent(theta):
    _, _, _, w = band_frame()
    return unit(cross(w, band_dir(theta)))


# --- Crown strap -----------------------------------------------------------------
def crown_frame():
    p0, _, _, _ = band_frame()
    lean = math.radians(CROWN["lean_deg"])
    k = (math.sin(lean), 0.0, math.cos(lean))   # up, leaning slightly forward
    v = (0.0, 1.0, 0.0)
    n = (math.cos(lean), 0.0, -math.sin(lean))  # strap width direction
    return p0, k, v, n


def crown_point(alpha, out=0.0, s=0.0):
    p0, k, v, n = crown_frame()
    d = add(mul(k, math.cos(alpha)), mul(v, math.sin(alpha)))
    best = 0.0
    for j in range(-2, 3):
        o = add(p0, mul(n, 0.5 * CROWN["width"] * j / 2.0))
        best = max(best, ray_ellipsoid(o, d))
    r = best + BAND["gap"] + out
    return add(add(p0, mul(n, s)), mul(d, r)), d


# --- Rear pod frame ----------------------------------------------------------------
def rear_pod_frame():
    """Inner-face centre of the rear pod and the lean (radians, top tilted forward)."""
    z = REAR_POD["z"]
    o = (HEAD_CENTER[0], 0.0, z)
    t = ray_ellipsoid(o, (-1.0, 0.0, 0.0))
    x_back = HEAD_CENTER[0] - t
    # Slope of the occiput at this height: dx/dz on the ellipsoid's x-z section.
    a, _, c = HEAD_SEMI_AXES
    zr = z - HEAD_CENTER[2]
    xr = x_back - HEAD_CENTER[0]
    slope = -(a * a * zr) / (c * c * xr)  # > 0: surface moves forward as z rises
    lean = math.atan(slope)
    inner = (x_back - REAR_POD["gap"], 0.0, z)
    return inner, lean


# --- Component list for the mass budget -------------------------------------------
def front_pod_centres():
    """Centres of the Pi enclosure (base) and the camera head."""
    t = BAND["thickness"]
    bx = FRONT_POD["base"][0]
    base = band_point(0.0, 0.0, t + bx / 2)
    head = band_point(0.0, -0.004, t + bx + 0.5 * FRONT_POD["head"][0])
    return base, head


def components(battery="pisugar3", with_headgear=True):
    """List of (group, name, mass_g, centroid) for everything the head carries.

    Masses are makers' figures where published (see BOM.md); the rest are
    estimates, printed parts from volume x density (PETG, 1.27 g/cm^3).
    """
    th = math.radians(TEMPLE_POD_THETA_DEG)
    base, cam = front_pod_centres()
    left = band_point(th, 0.0, BAND["thickness"] + 0.5 * TEMPLE_POD["size"][0])
    right = band_point(-th, 0.0, BAND["thickness"] + 0.5 * TEMPLE_POD_RIGHT["size"][0])
    inner, lean = rear_pod_frame()
    back_axis = (-math.cos(lean), 0.0, math.sin(lean))
    rear = add(inner, mul(back_axis, 0.5 * REAR_POD["depth"]))
    band_c = (HEAD_CENTER[0], 0.0, 0.5 * (BAND["front_z"] + BAND["back_z"]))
    ratchet = band_point(math.pi, 0.0, BAND["thickness"] + 0.008)
    crown_top, _ = crown_point(0.0, out=0.002)
    batt = BATTERY_OPTIONS[battery]
    cable_l = band_point(math.radians(95), 0.0, BAND["thickness"] + 0.001)
    items = [
        ("front pod", "Raspberry Pi Zero 2 W (10 g), 14 mm heatsink, microSD", 13.0, base),
        ("front pod", "Printed Pi enclosure, hinge, M2.5 screws", 14.0, base),
        ("front pod", "Camera Module 3 Wide (4 g) + 50 mm cable", 5.0, cam),
        ("front pod", "Printed camera head, red LED", 6.0, cam),
        ("temple pods", "Left: SPH0645 I2S mic (0.4 g) + printed pod", 4.5, left),
        ("temple pods", "Right: SPH0645 mic, 12 mm button, coin vibration motor, printed pod", 8.0, right),
        ("rear pod", "PiSugar 3 board (charger, RTC, programmable button)", batt["board_g"], rear),
        ("rear pod", f"Battery cell ({batt['label']})", batt["cell_g"], rear),
        ("rear pod", "Printed curved battery pod + bracket", 14.0 if batt["cell"] else 0.0, rear),
        ("cables", "Power + I2C cable, front to back (left side)", 4.0, cable_l),
        ("cables", "Mic, button and motor wires, temples to front", 2.0, band_point(0.0, 0.0, BAND["thickness"])),
        ("clips", "Printed cable clips, left", 2.0, band_point(math.radians(80), 0.0, BAND["thickness"])),
        ("clips", "Printed cable clips, right", 2.0, band_point(math.radians(-80), 0.0, BAND["thickness"])),
    ]
    if battery == "beltpack":
        items.append(("cables", "USB-C cable from the band to a pocket (on-head share)", 6.0, ratchet))
    if with_headgear:
        items += [
            ("headgear", "Ratchet headgear: band and sweatband", HEADGEAR_G["band"], band_c),
            ("headgear", "Crown strap", HEADGEAR_G["crown"], crown_top),
            ("headgear", "Ratchet knob and housing", HEADGEAR_G["ratchet"], ratchet),
        ]
    return items


def centre_of_mass(items):
    m = sum(i[2] for i in items)
    c = [sum(i[2] * i[3][k] for i in items) / m for k in range(3)]
    return m, tuple(c)
