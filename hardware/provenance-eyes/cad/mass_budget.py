"""Mass budget and centre of mass for the Provenance Eyes headset.

    python mass_budget.py            # markdown tables for every battery option

Reads the same layout.py as the Blender build, so the numbers match the renders.
x is measured forward from the ear line (tragion), z up from it; both in cm.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L  # noqa: E402


def table(battery):
    items = L.components(battery, with_headgear=True)
    rows = ["| Group | Part | Mass (g) | x (cm) | z (cm) |", "| --- | --- | ---: | ---: | ---: |"]
    for group, name, m, c in items:
        if m:
            rows.append(f"| {group} | {name} | {m:.1f} | {100 * c[0]:+.1f} | {100 * c[2]:+.1f} |")
    m_dev, c_dev = L.centre_of_mass(L.components(battery, with_headgear=False))
    m_tot, c_tot = L.centre_of_mass(items)
    lines = [f"### {L.BATTERY_OPTIONS[battery]['label']}", "", *rows, ""]
    lines.append(f"- Add-on parts: **{m_dev:.0f} g**, centre of mass **{100 * c_dev[0]:+.1f} cm** "
                 f"fore-aft of the ear line, {100 * c_dev[1]:+.1f} cm left-right, {100 * c_dev[2]:+.1f} cm up.")
    lines.append(f"- With the headgear: **{m_tot:.0f} g**, centre of mass **{100 * c_tot[0]:+.1f} cm** "
                 f"fore-aft, {100 * c_tot[1]:+.1f} cm left-right, {100 * c_tot[2]:+.1f} cm up.")
    shift = 100 * (m_tot * c_tot[0]) / (m_tot + L.HEAD_MASS_G)
    lines.append(f"- Shift of the head-plus-device centre of mass (head {L.HEAD_MASS_G / 1000:.1f} kg): "
                 f"{shift:+.2f} cm fore-aft.")
    return "\n".join(lines)


if __name__ == "__main__":
    print("Positive x is in front of the ear line, negative behind it.\n")
    for b in L.BATTERY_OPTIONS:
        print(table(b))
        print()
