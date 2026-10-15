"""Currents a small Al corrosion well produces, against what each shortlisted potentiostat resolves.

Reads the well's currents from corrosion_numbers.json (run corrosion_numbers.py first) and
writes current-ranges.png. Needs matplotlib.

Instrument numbers, each from the source named (checked 2026-10-13):
- Rodeostat HC: lowest range +/-10 uA with a 12-bit ADC, so ~4.9 nA per step
  (iorodeo/potentiostat@86e4708 firmware/libraries/potentiostat/ps_analog_subsystem.h#L26-L34,
  ps_constants.cpp#L168-L174); top range +/-10 mA.
- MYSTAT: 12 pA noise (SD) on its +/-2 uA range (Irving et al. 2020, HardwareX, section 7.1);
  top range +/-200 mA.
- EmStat Pico: 5.5 pA resolution on its 100 nA range; +/-3 mA maximum (PalmSens product page).
"""

import json

import matplotlib.pyplot as plt

SURFACE, INK, INK_2 = "#fcfcfb", "#0b0b0b", "#52514e"
NEED, INSTRUMENT = "#eb6834", "#2a78d6"  # categorical slots 2 and 1, validated as a pair

with open("corrosion_numbers.json") as f:
    cur = json.load(f)["currents"]
small, large = cur["3 mm"], cur["4 mm"]

need = [  # (label, low A, high A), from the 3 mm well's low end to the 4 mm well's high end
    ("LPR on a passive surface\n(R$_p$ 10$^4$–10$^6$ Ω·cm², ±10 mV)",
     min(small["lpr_current_nA"].values()) * 1e-9, max(large["lpr_current_nA"].values()) * 1e-9),
    ("Pitting threshold\n(10–100 µA/cm²)",
     min(small["pit_threshold_uA"].values()) * 1e-6, max(large["pit_threshold_uA"].values()) * 1e-6),
    ("Scan reversal\n(1 mA/cm²)", small["reversal_uA"] * 1e-6, large["reversal_uA"] * 1e-6),
]
instruments = [  # (label, smallest resolvable step A, max current A)
    ("Rodeostat HC\n(4.9 nA steps, no autoranging)", 4.9e-9, 10e-3),
    ("MYSTAT\n(12 pA noise; host autoranging)", 12e-12, 200e-3),
    ("EmStat Pico\n(5.5 pA resolution; autoranging)", 5.5e-12, 3e-3),
]

rows = [(lab, lo, hi, NEED) for lab, lo, hi in need] + \
       [(lab, lo, hi, INSTRUMENT) for lab, lo, hi in instruments]

fig, ax = plt.subplots(figsize=(8.2, 3.9), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)
ax.set_xscale("log")
ax.set_xlim(1e-12, 1)
ys = list(range(len(rows)))[::-1]
for y, (lab, lo, hi, color) in zip(ys, rows):
    ax.barh(y, hi - lo, left=lo, height=0.42, color=color, edgecolor=SURFACE, linewidth=2)
for x in (1e-9, 1e-6, 1e-3):
    ax.axvline(x, color="#e4e3df", linewidth=0.8, zorder=0)
ax.set_yticks(ys)
ax.set_yticklabels([r[0] for r in rows], fontsize=7.5, color=INK)
ax.set_xticks([1e-12, 1e-9, 1e-6, 1e-3, 1])
ax.set_xticklabels(["1 pA", "1 nA", "1 µA", "1 mA", "1 A"], fontsize=7.5, color=INK_2)
ax.set_xlabel("Current (A)", fontsize=8, color=INK_2)
ax.tick_params(axis="both", length=0)
for side in ("top", "right", "left"):
    ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color("#c9c8c3")
ax.axhline(2.5, color="#c9c8c3", linewidth=0.8)
ax.bar(0, 0, color=NEED, label="Produced by a 3–4 mm well")
ax.bar(0, 0, color=INSTRUMENT, label="Resolved by the potentiostat (smallest step to max current)")
ax.legend(loc="upper right", fontsize=7, frameon=False, labelcolor=INK)
fig.tight_layout()
fig.savefig("current-ranges.png", facecolor=SURFACE)
print("wrote current-ranges.png")
