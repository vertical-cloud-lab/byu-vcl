#!/usr/bin/env python3
"""Check that the pipette tip never passes over a vial while that vial is capped.

Written 2026-11-05 for PR #269. Ben found that with a tip on, the pipette does
not clear a capped vial on the stir module, so stir_module_trial.yaml must
never carry the tip over vial_1 while vial_1 is capped. This script checks
that for a protocol, move by move, from CubOS's own mock run.

It reuses tip_clearance.record() (which wraps passive_shadow.record_moves) to
mock-run the protocol and capture every commanded gantry pose with the travel
Z CubOS actually computed, and passive_shadow.axis_segments() to expand each
pose into the driver's real X, then Y, then Z moves. It starts from the homed
pose.

State is tracked per protocol step, conservatively:
  * a vial counts as capped from the start of the protocol, through the whole
    of its `decap` step, and again from the moment its `cap` step starts the
    capper down onto it. Before that the cap is still on the capper, so the
    vial is open while the tip lifts out of it and the head moves across;
  * the tip counts as on from the first move of `pick_up_tip` to the end of
    the protocol. That covers a tip that `drop_tip` failed to shed (the
    --tip-stuck case of passive_shadow) as well as the moves before the tip
    is seated.

For every move segment of the pipette's tool point while the tip is on and
the vial is capped, it measures the closest approach, in plan, of the tip's
axis to the vial's axis. The requirement is that this never comes within
--keepout mm (default 14 mm vial radius + 10 mm margin = 24 mm). Vertical
moves count too, so a tip that descends next to a capped vial is caught.

It also lists every place the head goes down while the tip is on: the tip
end's lowest deck Z there and what the deck file has within 30 mm. Those are
the spots to look at on the real deck, since the deck file does not model
holders, the stir module or anything else.

Usage:
  capped_vial_keepout.py GANTRY DECK PROTOCOL [--vial vial_1] [--keepout 24]
                         [--json OUT] [--plot OUT.png]
Exit status 1 if the tip comes within --keepout of the capped vial.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import passive_shadow as ps  # noqa: E402
import tip_clearance as tc  # noqa: E402

TIP_LEN = tc.TIP_LEN
CAPPER = "vial_capper_decapper"


def seg_dist(a, b, cx, cy):
    return ps.horizontal_distance_to_axis((a, b), cx, cy)


def walk(events, obstacles, vial_label):
    vials = {o["label"]: o for o in obstacles if o["kind"] == "vial"}
    capped = {k: True for k in vials}
    tip_on = False
    pose = tc.HOMED
    steps = {}
    prev_step = None
    for ev in events:
        step, cmd = ev["step"], (ev["command"] or "")
        target = tuple(ev["gantry"])
        if step != prev_step:
            # state changes at the start of a step
            if cmd == "pick_up_tip":
                tip_on = True
            # a decap reopens its vial only once the step is over (below)
            if prev_step is not None and steps[prev_step]["command"] == "decap":
                for k in steps[prev_step]["decap_vials"]:
                    capped[k] = False
            prev_step = step
            steps[step] = {"step": step, "command": cmd, "moving": ev["moving_key"],
                           "segments": [], "decap_vials": set(),
                           "tip_on": tip_on, "capped": dict(capped)}
        if cmd == "decap":
            steps[step]["decap_vials"] |= ps._vials_at(obstacles, target)
        ox, oy = ev["offsets"]["pipette"]
        cx, cy = ev["offsets"].get(CAPPER, (0.0, 0.0))
        depth = max(ev["depths"]["pipette"], TIP_LEN if tip_on else 0.0)
        for (ax, ay, az), (bx, by, bz) in ps.axis_segments(pose, target, ev["travel_z_actual"]):
            if cmd == "cap" and (ax, ay) == (bx, by) and bz < az:
                # the capper starts down onto a vial: from here on it counts as capped
                for k in ps._vials_at(obstacles, (ax + cx, ay + cy)):
                    capped[k] = True
            a = (ax + ox, ay + oy, az - depth)
            b = (bx + ox, by + oy, bz - depth)
            cap_g = ((ax, ay, az), (bx, by, bz))
            steps[step]["segments"].append({"tip": [a, b], "gantry": cap_g,
                                             "tip_on": tip_on, "capped": dict(capped)})
        pose = target
    return steps, vials


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("gantry")
    ap.add_argument("deck")
    ap.add_argument("protocol")
    ap.add_argument("--vial", default="vial_1")
    ap.add_argument("--keepout", type=float, default=24.0)
    ap.add_argument("--cap-height", type=float, default=13.0)
    ap.add_argument("--json")
    ap.add_argument("--plot")
    a = ap.parse_args(argv)

    events, _, _ = tc.record(a.gantry, a.deck, a.protocol)
    obstacles = ps.deck_obstacles(a.deck, a.cap_height)
    steps, vials = walk(events, obstacles, a.vial)
    v = vials[a.vial]

    print(f"== {Path(a.protocol).name} | {Path(a.deck).name} | {len(events)} poses | "
          f"keep-out {a.keepout} mm from {a.vial} axis ({v['x']}, {v['y']}) while capped")
    print(f"{'step':>4} {'command':<12} {'moving':<8} {'tip':<4} {a.vial + ' capped':<14}"
          f"{'closest tip-axis to ' + a.vial:>22} {'tip end Z on laterals':>22}")
    worst = None
    report = []
    for s in steps.values():
        lat = [sg for sg in s["segments"] if sg["tip"][0][:2] != sg["tip"][1][:2]]
        dmin = min((seg_dist(sg["tip"][0], sg["tip"][1], v["x"], v["y"]) for sg in s["segments"]),
                   default=None)
        dmin_capped = min((seg_dist(sg["tip"][0], sg["tip"][1], v["x"], v["y"])
                           for sg in s["segments"] if sg["tip_on"] and sg["capped"][a.vial]),
                          default=None)
        zs = sorted({round(sg["tip"][0][2], 3) for sg in lat})
        any_capped = any(sg["capped"][a.vial] for sg in s["segments"])
        all_capped = all(sg["capped"][a.vial] for sg in s["segments"])
        cstate = "yes" if all_capped else ("part" if any_capped else "no")
        tstate = "on" if s["tip_on"] else "off"
        print(f"{s['step']:>4} {s['command']:<12} {(s['moving'] or '')[:8]:<8} {tstate:<4} "
              f"{cstate:<14}{(f'{dmin:.1f}' if dmin is not None else '-'):>22} "
              f"{', '.join(f'{z:g}' for z in zs) or '-':>22}")
        if dmin_capped is not None and (worst is None or dmin_capped < worst[0]):
            worst = (dmin_capped, s["step"], s["command"])
        report.append({"step": s["step"], "command": s["command"], "tip_on": s["tip_on"],
                       "capped": cstate, "closest_mm": dmin, "closest_while_capped_mm": dmin_capped,
                       "lateral_tip_z": zs})

    ok = worst is None or worst[0] >= a.keepout
    print()
    if worst is None:
        print(f"tip never on while {a.vial} is capped")
    else:
        print(f"closest the tip comes to {a.vial}'s axis while it is capped and the tip is on: "
              f"{worst[0]:.1f} mm (step {worst[1]} {worst[2]}); keep-out {a.keepout} mm -> "
              f"{'PASS' if ok else 'FAIL'}")

    # every place the head goes down with the tip on, outside an open vial being pipetted
    print("\nwhere the tip goes down (tip on), with deck-file labware within 30 mm:")
    downs = []
    for s in steps.values():
        for sg in s["segments"]:
            (ax, ay, az), (bx, by, bz) = sg["tip"]
            if not sg["tip_on"] or (ax, ay) != (bx, by) or bz >= az:
                continue
            near = []
            for o in obstacles:
                d = math.hypot(o["x"] - ax, o["y"] - ay)
                if d < 30 and o["kind"] == "vial":
                    near.append(f"{o['label']} {d:.1f} mm")
            near_tips = [o for o in obstacles if o["kind"] == "tip"
                         and math.hypot(o["x"] - ax, o["y"] - ay) < 30]
            if near_tips:
                near.append(f"tip rack ({len(near_tips)} tips within 30 mm)")
            key = (s["step"], s["command"], round(ax, 3), round(ay, 3), round(bz, 3))
            if key in [d[:5] for d in downs]:
                continue
            downs.append(key + (", ".join(near) or "nothing in the deck file",
                                "moving" if s["moving"] == "pipette" else "passive"))
    for st, cmd, x, y, z, near, role in downs:
        print(f"  step {st:>2} {cmd:<12} {role:<8} tip over deck ({x:g}, {y:g}) down to tip-end Z {z:g}: {near}")

    if a.json:
        json.dump({"keepout_mm": a.keepout, "vial": a.vial, "worst": worst, "pass": ok,
                   "steps": report, "descents": downs}, open(a.json, "w"), indent=1)
    if a.plot:
        plot(steps, vials, obstacles, a, downs)
    return 0 if ok else 1


def plot(steps, vials, obstacles, a, downs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    fig, ax = plt.subplots(figsize=(10, 8.4), dpi=130)
    v = vials[a.vial]
    ax.add_patch(Circle((v["x"], v["y"]), a.keepout, fc="#fde2e1", ec="#c0392b", ls="--", lw=1,
                        label=f"keep-out while {a.vial} is capped ({a.keepout:g} mm)"))
    for o in vials.values():
        ax.add_patch(Circle((o["x"], o["y"]), o["r"], fc="#dddddd", ec="#555555", lw=1))
        ax.annotate(o["label"], (o["x"], o["y"]), ha="center", va="center", fontsize=8)
    tips = [o for o in obstacles if o["kind"] == "tip"]
    ax.scatter([t["x"] for t in tips], [t["y"] for t in tips], s=6, c="#999999", label="tip rack")
    styles = {
        ("on", True): dict(c="#c0392b", lw=2.2, label=f"tip on, {a.vial} capped"),
        ("on", False): dict(c="#2f6db5", lw=2.2, label=f"tip on, {a.vial} open"),
        ("off", True): dict(c="#9aa5b1", lw=1.2, ls=":", label="no tip"),
        ("off", False): dict(c="#9aa5b1", lw=1.2, ls=":", label="no tip"),
    }
    seen = set()
    for s in steps.values():
        for sg in s["segments"]:
            (ax0, ay0, _), (bx0, by0, _) = sg["tip"]
            if (ax0, ay0) == (bx0, by0):
                continue
            key = ("on" if sg["tip_on"] else "off", sg["capped"][a.vial])
            st = dict(styles[key])
            lab = st.pop("label")
            if lab in seen:
                lab = None
            seen.add(lab)
            ax.plot([ax0, bx0], [ay0, by0], **st, label=lab, solid_capstyle="round")
    labels = {}
    for i, (st, cmd, x, y, z, near, role) in enumerate(downs):
        ax.plot(x, y, "v", ms=7, mec="k", mfc="#f5b041" if role == "passive" else "#2f6db5")
        labels.setdefault((x, y), []).append(f"{st} {cmd}")
    for (x, y), labs in labels.items():
        labs = list(dict.fromkeys(labs))
        ax.annotate("\n".join(labs), (x, y), xytext=(6, 4), textcoords="offset points", fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
    ax.plot([], [], "v", ms=7, mec="k", mfc="#f5b041", ls="", label="tip goes down beside the capper (passive)")
    ax.plot([], [], "v", ms=7, mec="k", mfc="#2f6db5", ls="", label="tip goes down into a vial or the rack")
    ax.set_aspect("equal")
    ax.set_xlim(90, 330)
    ax.set_ylim(15, 215)
    ax.set_xlabel("deck X (mm)")
    ax.set_ylabel("deck Y (mm)")
    ax.set_title(f"Pipette tip path, {Path(a.protocol).name} on {Path(a.deck).name} (plan view)", fontsize=10)
    ax.legend(loc="upper left", fontsize=7.5, frameon=True)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(a.plot)


if __name__ == "__main__":
    sys.exit(main())
