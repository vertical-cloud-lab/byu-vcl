#!/usr/bin/env python3
"""Voltage at the Pi 5 on the PiPER's wrist for the ways of getting power up the arm.

Copper at 20 C, VBUS and GND of the same gauge, both carrying the load current. A mated USB-C pair
is taken as 20 mOhm (VBUS + GND). The Pi 5 flags under-voltage below 4.63 V, measured after its
input fuse. A USB-C cable is allowed to drop 500 mV on VBUS plus 250 mV on GND at its rated current,
so even a compliant cable can lose 0.75 V.

    python power/voltage_drop.py        # prints a markdown table, writes power/voltage_drop.json
"""
from __future__ import annotations

import json
from pathlib import Path

OHM_PER_M = {17: 0.0167, 18: 0.0210, 20: 0.0333, 22: 0.0530, 24: 0.0842, 26: 0.1339, 28: 0.2129}
R_MATED = 0.020            # ohm per mated USB-C pair, VBUS + GND
UV = 4.63                  # V, Pi 5 under-voltage threshold
LOADS = (1.5, 2.5)         # A: two cameras streaming; plus a busy CPU and the fan at full speed
V_OFFICIAL = 5.1           # V, Raspberry Pi 27 W supply


def usb(v0: float, legs: list[tuple[float, int]], mated: int, amps: float) -> float:
    """Volts at the Pi: supply v0 through cable legs [(metres, AWG)] and `mated` connector pairs
    between the supply's cable and the Pi's socket (the Pi's own socket counts as one)."""
    r = sum(2 * m * OHM_PER_M[g] for m, g in legs) + mated * R_MATED
    return v0 - amps * r


def buck(v0: float, metres: float, awg: int, amps_5v: float, eff: float = 0.9) -> tuple[float, float]:
    """24 V (say) up the arm to a buck converter at the Pi: (volts at the converter, % lost)."""
    i = 5.1 * amps_5v / eff / v0
    drop = i * 2 * metres * OHM_PER_M[awg]
    return v0 - drop, 100 * drop / v0


def main() -> None:
    rows = [
        ("Official 27 W supply alone: its 1.2 m, 17 AWG lead (too short to reach)", [(1.2, 17)], 1),
        ("Official supply + 2 m USB-C extension (22 AWG, one more mated pair)", [(1.2, 17), (2.0, 22)], 2),
        ("Official supply + 2 m extension of a thin 3 A cable (26 AWG)", [(1.2, 17), (2.0, 26)], 2),
        ("5 A PD supply + one 3 m 5 A cable (20 AWG)", [(3.0, 20)], 1),
        ("5 A PD supply + one 3 m 3 A cable (24 AWG)", [(3.0, 24)], 1),
    ]
    out = {"assumptions": __doc__.split("\n\n")[1].replace("\n", " "), "under-voltage (V)": UV, "usb": [], "buck": []}
    print(f"| Route (3 to 3.5 m to the wrist) | at {LOADS[0]} A | at {LOADS[1]} A |\n|---|---|---|")
    for name, legs, mated in rows:
        v = [usb(V_OFFICIAL, legs, mated, a) for a in LOADS]
        out["usb"].append({"route": name, "volts at the Pi": [round(x, 2) for x in v]})
        print(f"| {name} | {v[0]:.2f} V{'' if v[0] > UV else ' (low)'} | {v[1]:.2f} V{'' if v[1] > UV else ' (low)'} |")
    for v0, awg in ((24.0, 22), (12.0, 22), (24.0, 26)):
        vin, pct = buck(v0, 3.5, awg, LOADS[1])
        out["buck"].append({"supply (V)": v0, "AWG": awg, "volts at the converter": round(vin, 2), "lost (%)": round(pct, 2)})
        print(f"| {v0:.0f} V up 3.5 m of {awg} AWG, 5.1 V buck at the Pi | 5.10 V | 5.10 V (converter sees {vin:.2f} V, {pct:.1f} % lost) |")
    (Path(__file__).with_suffix(".json")).write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
