"""Stir bar pull, coupling and Hall signal against vial height (magpylib >= 6.1).

Why: on 2026-11-04 the compact stirrer would not start with a vial of water and the
15 x 6 mm bar seated in the cup: 36 full-power kicks at 5 V, no movement. Started with
the vial out, it stirred while Ben lowered the vial in, and stopped when the vial was
about 3 mm from fully down (PR #269, 23:40 UTC;
cubos/results/stirrer_water_20261104/). His options: more fan torque, a weaker bar, or
the vial 3 mm higher.

Model: the drive magnets and the Hall element are field_check.py's (imported, so the
geometry has one source). h is how far the vial sits above its seat (a spacer disc, or
a cup floor that much thicker). With the bar coupled, lying on the vial's floor, for
each h this computes:
  - Fz, the magnets' pull on the bar, down. It is also the bar's pull on the fan's
    rotor, up, which the fan's sleeve bearing carries as thrust;
  - the pull-out torque, the most the coupling can turn the bar (max over lag angle);
  - the Hall element's smaller peak over one turn, with the bar following.
The bars' magnet cores are not published, so each bar gets four cores that bracket it
(the 15 x 6 mm ones are field_check.py's).

What it is used for: turning the bar means dragging it round against friction under
Fz (mu * Fz * r), and the fan carries Fz as thrust in its own bearing. Both scale with
Fz, so Fz(h) / Fz(3 mm) is how much more torque the fan would need at h than it had
where Ben saw it stop. That calibrates the unknown fan torque and friction against
what was seen, instead of guessing them.

Run: python coupling_vs_height.py > coupling_vs_height_output.txt
     (also writes ../img/coupling_vs_height.png)
"""
import sys
from pathlib import Path

import numpy as np
import magpylib as magpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from field_check import FLOOR_IN, MM, bar, drive, hall_peak  # noqa: E402

HALL = (-11.70, 22.655)        # field_check.py's nominal element position (x, z), mm
TRIP = 9.5                      # US1881 worst-case operate/release point, mT
# Orion's datasheet (rev. 6/19/2024) gives the OD4010-05HSS at 5 V and the OD4010-12HSS at 12 V the
# same 8000 rpm, 9.2 CFM and 0.20 in H2O, so the same torque at their rated voltages. A given winding's
# torque at low speed scales with the voltage across it, so today's 12 V fan at 5 V has about 5/12 of it.
FAN_5V_MODEL = 12.0 / 5.0       # OD4010-05HSS at 5 V against today's OD4010-12HSS at 5 V
SEEN = 3.0                      # where Ben saw it stop, mm above the seat
HS = np.round(np.arange(0.0, 8.01, 0.5), 2)
TH = (0.0, 2.0, 3.0, 5.0)  # heights for the pull-out torque

# bar: (axis height above the vial's inner floor, length, cores (J tesla, core diameter, core length))
BARS = {
    "15 x 6 mm (today's)": dict(axis=3.0, L=15.0, color="#2a78d6",
                                cores=[(0.5, 3, 10), (0.8, 3, 12), (0.6, 4, 12), (1.0, 4, 12)]),
    "12 x 3 mm (Pioreactor's)": dict(axis=1.5, L=12.0, color="#eb6834",
                                     cores=[(0.5, 1.5, 9), (0.8, 1.5, 10), (0.6, 2, 10), (1.0, 2, 10)]),
}
MESH = 300


def bar_magnet(lag, core, zaxis):
    J, d, l = core
    return bar(lag, J, d, l, zaxis)


def fz(core, zaxis):
    """Magnets' force on the coupled bar, z component, N (negative = down)."""
    F, _ = magpy.getFT(drive(0), bar_magnet(0.0, core, zaxis), meshing=MESH)
    return float(F[2])


def pullout(core, zaxis):
    """Largest restoring torque on the bar about the vial axis, over lag angle, mN m."""
    lags = np.arange(0.0, 181.0, 7.5)
    tz = [abs(float(magpy.getFT(drive(0), bar_magnet(a, core, zaxis), meshing=MESH)[1][2])) for a in lags]
    i = int(np.argmax(tz))
    fine = np.arange(max(lags[i] - 7.5, 0), lags[i] + 7.6, 1.5)
    tz += [abs(float(magpy.getFT(drive(0), bar_magnet(a, core, zaxis), meshing=MESH)[1][2])) for a in fine]
    return max(tz) * 1e3


def h_where(hs, ys, target):
    """Smallest h at which the decreasing curve ys has fallen to target (linear interpolation)."""
    ys = np.asarray(ys)
    if ys[0] <= target:
        return 0.0
    for k in range(1, len(hs)):
        if ys[k] <= target:
            return hs[k - 1] + (hs[k] - hs[k - 1]) * (ys[k - 1] - target) / (ys[k - 1] - ys[k])
    return float("nan")


def main():
    res = {}
    for name, b in BARS.items():
        res[name] = []
        for core in b["cores"]:
            z0 = FLOOR_IN + b["axis"]
            F = np.array([-fz(core, z0 + h) for h in HS])
            T = np.array([pullout(core, z0 + h) for h in TH])
            H = np.array([hall_peak(HALL[0], HALL[1], (core[0], core[1], core[2], z0 + h)) for h in HS])
            res[name].append(dict(core=core, F=F, T=T, H=H))

    big, small = (res[n] for n in BARS)
    print("Stir bar pull, coupling and Hall signal against vial height; geometry from field_check.py")
    print(f"h = vial raised above its seat (mm). Vial inner floor at z {FLOOR_IN} when seated; magnet tops at z 22.645.\n")

    for name, rows in res.items():
        L = BARS[name]["L"]
        print(f"== {name} bar, axis {BARS[name]['axis']} mm above the inner floor ==")
        print("  Fz, the pull down on the bar (= up on the fan's rotor), N:")
        print("   core (J T, d x l mm) " + "".join(f"{h:>6.1f}" for h in HS))
        for r in rows:
            J, d, l = r["core"]
            print(f"   {J:.1f}, {d:g} x {l:g}".ljust(23) + "".join(f"{v:6.3f}" for v in r["F"]))
        print("  relative to h = 3 mm (the torque the fan needs, against what it had where Ben saw it stop):")
        for r in rows:
            J, d, l = r["core"]
            rel = r["F"] / r["F"][list(HS).index(SEEN)]
            print(f"   {J:.1f}, {d:g} x {l:g}".ljust(23) + "".join(f"{v:6.2f}" for v in rel))
        print("  pull-out torque, mN m, at h " + " / ".join(f"{h:g}" for h in TH) + ":  "
              + "   ".join(f"{r['core'][1]:g}x{r['core'][2]:g} J{r['core'][0]:.1f}: "
                         + "/".join(f"{t:.2f}" for t in r["T"]) for r in rows))
        print(f"  friction torque at mu 0.1, r = L/4 = {L / 4:.2f} mm, mN m, at h " + " / ".join(f"{h:g}" for h in TH) + ":  "
              + "   ".join(f"{r['core'][1]:g}x{r['core'][2]:g} J{r['core'][0]:.1f}: "
                         + "/".join(f"{0.1 * r['F'][list(HS).index(h)] * L / 4:.3f}" for h in TH)
                         for r in rows))
        print("  Hall element's smaller peak over a turn, bar following, mT (US1881 needs 9.5 worst case):")
        for r in rows:
            J, d, l = r["core"]
            print(f"   {J:.1f}, {d:g} x {l:g}".ljust(23) + "".join(f"{v:6.1f}" for v in r["H"]))
        print()

    i3 = list(HS).index(SEEN)
    print("== What each option buys, calibrated on Ben's ~3 mm with today's bar ==")
    k = [r["F"][0] / r["F"][i3] for r in big]
    print(f"Torque needed at the seat, against what the fan had at 3 mm: x{min(k):.2f} to x{max(k):.2f} over the four cores")
    hmin = [h_where(HS, r["F"], FAN_5V_MODEL * r["F"][i3]) for r in big]
    print(f"With x{FAN_5V_MODEL:.1f} the torque (OD4010-05HSS, or 12 V on today's fan): runs from h = {min(hmin):.1f} to {max(hmin):.1f} mm up")
    for frac in (0.5, 0.75):
        hs_ = [h_where(HS, r["F"], r["F"][i3] / frac) for r in big]
        print(f"Same bar and fan, if 3 mm was only {frac:.0%} of the fan's best: runs from h = {min(hs_):.1f} to {max(hs_):.1f} mm up")
    worst = max(s["F"][0] / b["F"][i3] for s in small for b in big)
    best = min(s["F"][0] / b["F"][i3] for s in small for b in big)
    print(f"12 x 3 mm bar seated, against today's bar at 3 mm (every pairing of cores): x{best:.2f} to x{worst:.2f}")
    hsm = [h_where(HS, s["F"], b["F"][i3]) for s in small for b in big]
    print(f"12 x 3 mm bar, today's fan: runs from h = {min(hsm):.1f} to {max(hsm):.1f} mm up (every pairing)")
    print("Paired cores (same material, core scaled with the bar; the i-th core of each list):")
    pr = [s["F"][0] / b["F"][i3] for s, b in zip(small, big)]
    print(f"  12 x 3 mm bar seated, against today's bar at 3 mm: x{min(pr):.2f} to x{max(pr):.2f}")
    print("\nOptions, as the pull against what today's fan managed at 3 mm (paired cores, min-max).")
    print("The fan's torque is 1 for today's OD4010-12HSS at 5 V and 2.4 for the OD4010-05HSS at 5 V;")
    print("'share' is the pull over the fan's torque: 1 is the edge Ben saw, under 1 it turns.")
    print(f"  {'fan':<16}{'bar':<10}{'h, mm':>6}{'pull':>14}{'share':>14}")
    for fan, ft in (("OD4010-12HSS", 1.0), ("OD4010-05HSS", FAN_5V_MODEL)):
        for bname, rows in (("15 x 6", big), ("12 x 3", small)):
            for h in (0.0, 1.0, 2.0, 2.5, 3.0, 4.0, 5.0):
                j = list(HS).index(h)
                v = [r["F"][j] / b["F"][i3] for r, b in zip(rows, big)]
                print(f"  {fan:<16}{bname:<10}{h:>6.1f}{min(v):>8.2f}-{max(v):<5.2f}{min(v) / ft:>8.2f}-{max(v) / ft:<5.2f}")
    # water drag at 1200 rpm, an upper bound: rho Cd d w^2 L^4 / 64 with Cd = 1 and no co-rotating fluid
    w = 1200 * 2 * np.pi / 60
    for name, d in (("15 x 6", 6e-3), ("12 x 3", 3e-3)):
        L = BARS[[n for n in BARS if n.startswith(name)][0]]["L"] * 1e-3
        print(f"Water drag on the {name} mm bar at 1200 rpm, upper bound: {1000 * d * w ** 2 * L ** 4 / 64 * 1e3:.3f} mN m")
    plot(res)


def plot(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, ink2, grid, surf = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": ink2, "axes.labelcolor": ink, "xtick.color": ink2,
                         "ytick.color": ink2, "axes.titlesize": 11, "axes.titleweight": "bold"})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), facecolor=surf)
    i3 = list(HS).index(SEEN)
    big = list(res.values())[0]
    for name, rows in res.items():
        c = BARS[name]["color"]
        F = np.array([r["F"] / b["F"][i3] for r, b in zip(rows, big)])
        Hh = np.array([r["H"] for r in rows])
        for ax, Y in ((a1, F), (a2, Hh)):
            ax.fill_between(HS, Y.min(0), Y.max(0), color=c, alpha=0.18, lw=0)
            ax.plot(HS, np.median(Y, 0), color=c, lw=2, label=name)
    a1.set_yscale("log")
    a1.axhline(1.0, color=ink2, lw=1, ls="--")
    a1.text(7.9, 1.06, "today's fan at 5 V: Ben saw it stop at 3 mm", ha="right", va="bottom", color=ink2, fontsize=8.5)
    a1.axhline(FAN_5V_MODEL, color=ink2, lw=1, ls=":")
    a1.text(7.9, FAN_5V_MODEL * 1.06, "x2.4 the torque: OD4010-05HSS at 5 V", ha="right", va="bottom",
            color=ink2, fontsize=8.5)
    a1.axvline(SEEN, color=grid, lw=6, zorder=0)
    a1.set_xlabel("vial raised above its seat, mm")
    a1.set_ylabel("pull on the bar (and up on the rotor),\nrelative to today's bar at 3 mm")
    a1.set_title("Pull on the bar: a fan turns below its line")
    a2.axhline(TRIP, color=ink2, lw=1, ls="--")
    a2.text(7.9, TRIP - 0.3, "US1881 worst-case trip, 9.5 mT", ha="right", va="top", color=ink2, fontsize=8.5)
    a2.set_ylim(0, 22)
    a2.set_xlabel("vial raised above its seat, mm")
    a2.set_ylabel("Hall element's smaller peak over a turn, mT")
    a2.set_title("Hall signal with the bar following")
    for ax in (a1, a2):
        ax.set_facecolor(surf)
        ax.grid(True, color=grid, lw=0.8, which="major")
        ax.set_xlim(0, 8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.legend(frameon=False, loc=(0.52, 0.22) if ax is a2 else "lower left", fontsize=9)
    fig.text(0.01, 0.01, "Bands: four guessed magnet cores per bar (not published); lines: their median. Left: each core over "
             "today's bar's same-material core at 3 mm. Geometry from field_check.py / vial_stirrer.fs.",
             color=ink2, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = Path(__file__).resolve().parent.parent / "img" / "coupling_vs_height.png"
    fig.savefig(out, dpi=150, facecolor=surf)


if __name__ == "__main__":
    main()
