#!/usr/bin/env python3
"""Which screw lengths and head types fit each joint of the lid mount.

For each joint it sweeps the standard lengths, and reports how far the tip gets past the far
face of its nut and whether it runs into anything on the way, plus the longest screw that
runs into nothing. Then it puts a socket head (ISO 4762), a button head (ISO 7380) and two
Phillips pan heads (ISO 7045, and DIN 7985, whose M3 head is wider) on each screw and checks
them against the parts around them.
It uses the same `Params` and reference models as `lid_mount.py`, so a change there flows
through.

    python fastener_fit.py     # prints a summary, writes ../exports/fastener_fit.json

The nuts are taken at their thickest (ISO 4032 maximum), which is the worst case for reach.
"""
from __future__ import annotations

import json

import cadquery as cq

from hardware import ISO4032, ISO4762, ISO7380, MAJOR
from lid_mount import EXPORTS, Params, build, corners, cyl, make_ring_sweep, overlap, pi_to_screw_heads

LENGTHS = (6, 8, 10, 12, 14, 16, 18, 20, 25)
PITCH = {"M2.5": 0.45, "M3": 0.5, "M4": 0.7}
ISO7045 = {"M2.5": (5.0, 2.1), "M3": (5.6, 2.4), "M4": (8.0, 3.1)}   # Phillips pan head: dk, k
DIN7985 = {"M2.5": (5.0, 2.0), "M3": (6.0, 2.4), "M4": (8.0, 3.1)}   # the older pan head, common in shop bins
HEADS = {
    "socket (ISO 4762)": {s: v[:2] for s, v in ISO4762.items()},
    "button (ISO 7380)": {s: v[:2] for s, v in ISO7380.items()},
    "Phillips pan (ISO 7045)": ISO7045,
    "Phillips pan (DIN 7985)": DIN7985,
}
WASHER_T = 0.8          # the M4 nylon washer under each head, as in hardware.py
PIPETTE_GAP = 9.1       # pipette-head top cover to the window's underside, from Opentrons' STEP
OBSTACLES = ("base", "deck", "camera", "adapter", "lens", "pi5", "pi_spacers", "lid")


def joints(p: Params) -> dict[str, dict]:
    """Each joint: thread size, screw axes, where the underside of the head sits, which way the
    shank points (+1 up, -1 down), and the far face of its nut once it is pulled tight."""
    z_top_deck = p.z_deck + p.deck_t
    m25, m3, m4 = ISO4032["M2.5"][1], ISO4032["M3"][1], ISO4032["M4"][1]
    return {
        "camera -> deck": dict(
            size="M2.5", xy=corners(p.cam_hole_pitch / 2), seat=p.z_pcb_back - p.cam_pcb_t, dir=1,
            # nut pulled down onto the floor of its trap in the deck top
            nut_far=z_top_deck - p.m25_nut_h + m25),
        "Pi 5 -> deck": dict(
            size="M2.5", xy=p.pi_holes(), seat=z_top_deck + p.pi_spacer_h + 1.6, dir=-1,
            # nut pulled up against the roof of its trap in the deck underside
            nut_far=p.z_deck + p.m25_nut_h - m25),
        "deck -> posts": dict(
            size="M3", xy=corners(p.post_c), seat=z_top_deck, dir=-1,
            # nut pulled up against the roof of the side slot
            nut_far=p.z_m3_slot + p.m3_nut_slot_h - m3),
        "base -> lid (phase 2)": dict(
            size="M4", xy=corners(p.bolt_xy), seat=-p.lid_thickness - WASHER_T, dir=1,
            # nut pulled down onto the floor of its trap in the base
            nut_far=p.base_t - p.m4_nut_h + m4),
    }


def shank(j: dict, length: float) -> cq.Workplane:
    """The threads, at about their minor diameter so they don't graze the clearance holes."""
    d = MAJOR[j["size"]] - PITCH[j["size"]]
    z0 = j["seat"] if j["dir"] > 0 else j["seat"] - length
    out = None
    for x, y in j["xy"]:
        c = cyl(d, length, x, y, z0)
        out = c if out is None else out.union(c)
    return out


def heads(j: dict, dk: float, k: float) -> cq.Workplane:
    """Heads on the far side of the seat from the shank, lifted 0.01 mm off the seat face."""
    z0 = j["seat"] - k - 0.01 if j["dir"] > 0 else j["seat"] + 0.01
    out = None
    for x, y in j["xy"]:
        c = cyl(dk, k, x, y, z0)
        out = c if out is None else out.union(c)
    return out


def hits(shape: cq.Workplane, parts: dict[str, cq.Workplane], names=OBSTACLES) -> dict[str, float]:
    found = {}
    for name in names:
        v = overlap(shape, parts[name])
        if v > 1e-3:
            found[name] = round(v, 3)
    return found


def longest(j: dict, parts: dict[str, cq.Workplane], names, hi: float = 40.0) -> float | None:
    """Longest screw whose tip runs into nothing, to 0.05 mm; None if nothing is within `hi`."""
    if not hits(shank(j, hi), parts, names):
        return None
    lo = 1.0
    while hi - lo > 0.05:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if hits(shank(j, mid), parts, names) else (mid, hi)
    return round(lo, 2)


def sweep(p: Params, parts: dict[str, cq.Workplane]) -> dict:
    parts = dict(parts, ring_sweep=make_ring_sweep(p))
    names = OBSTACLES + ("ring_sweep",)
    out = {}
    for name, j in joints(p).items():
        rows = []
        for L in LENGTHS:
            tip = j["seat"] + j["dir"] * L
            past = (tip - j["nut_far"]) * j["dir"]
            rows.append({"length": L, "tip_z": round(tip, 2), "past_nut": round(past, 2),
                         "runs_into": hits(shank(j, L), parts, names)})
        head_rows = {}
        for kind, table in HEADS.items():
            dk, k = table[j["size"]]
            row = {"dk": dk, "k": k, "runs_into": hits(heads(j, dk, k), parts, names)}
            if j["size"] == "M3":
                row["plan_gap_to_pi5"] = round(pi_to_screw_heads(p, head_r=dk / 2), 2)
            if j["size"] == "M4":
                drop = WASHER_T + k
                row["below_window"] = round(drop, 2)
                row["left_under_window"] = round(PIPETTE_GAP - drop, 2)
            head_rows[kind] = row
        out[name] = {"size": j["size"], "full_nut_at": round(abs(j["nut_far"] - j["seat"]), 2),
                     "longest": longest(j, parts, names), "lengths": rows, "heads": head_rows}
    # The 2 mm shims lift the deck, and with it the M3 heads, but the nuts stay in the posts.
    j = joints(p)["deck -> posts"]
    j = dict(j, seat=j["seat"] + p.shim_t)
    rows = []
    for L in LENGTHS:
        tip = j["seat"] - L
        rows.append({"length": L, "tip_z": round(tip, 2), "past_nut": round(j["nut_far"] - tip, 2),
                     "runs_into": hits(shank(j, L), parts, ("base",))})
    out["deck -> posts, with the 2 mm shims"] = {
        "size": "M3", "full_nut_at": round(j["seat"] - j["nut_far"], 2),
        "longest": longest(j, parts, ("base",)), "lengths": rows}
    return out


def summary(res: dict) -> None:
    for name, r in res.items():
        top = "nothing within 40 mm" if r["longest"] is None else f"{r['longest']} mm"
        print(f"\n{name} ({r['size']}): reaches through its nut at {r['full_nut_at']} mm, longest {top}")
        for row in r["lengths"]:
            ok = "clear" if not row["runs_into"] else "HITS " + ", ".join(row["runs_into"])
            print(f"  {row['length']:>2} mm: tip {row['past_nut']:+6.2f} mm past the nut, {ok}")
        for kind, h in r.get("heads", {}).items():
            extra = {k: v for k, v in h.items() if k not in ("dk", "k", "runs_into")}
            ok = "fits" if not h["runs_into"] else "HITS " + ", ".join(h["runs_into"])
            print(f"  {kind}: {h['dk']} x {h['k']} mm, {ok} {extra if extra else ''}")


def main() -> None:
    p = Params()
    res = sweep(p, build(p))
    summary(res)
    (EXPORTS / "fastener_fit.json").write_text(json.dumps(res, indent=2) + "\n")


if __name__ == "__main__":
    main()
