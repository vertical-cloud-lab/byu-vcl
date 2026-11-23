"""A day of unit 3's floor passes, and where they wait for the person (#366, #303): one weekday of floor_cleaning.py's
year (upkeep.py's schedule, seed 303) as an animated timeline.

    python3 floor_day.py           # -> out/mp4/floor_day.mp4, out/floor_day.gif, out/floor_day.json (about 1 min)

Everything is the model's (floor_cleaning.own_cleaner on timelapse.simulate with upkeep): the atomizer's runs, the
sieving and the depowdering that make a pass due, the person's shift (08:00-16:00), their crucible hours (each run's
first hour, at the atomizer) and other tasks, units 1 and 2's transfers at the same three docks, and unit 3's passes
(option C: its own line, the stations' vacuums, units_pou's pass times). A pass at the atomizer waits while the person
is at the machine for a crucible hour; a pass at a dock waits while a unit is docked there. The nightly sweep is the
model's 43 min; floor_pass.py's route, with a bond at every spot, takes 89. Notes: notes/floor_cleaning.md.
"""
from __future__ import annotations

import json
import math
import subprocess

import numpy as np

import floor_cleaning as FC

OUT = FC.OUT
NAME = "floor_day"
DAY = 35                                    # a Monday with three atomizer runs (day 0 is a Monday: upkeep's weeks)
FPS, GIF_FPS = 15, 10
W_PX, H_PX = 1280, 720
BASE_S = 34.0                               # video seconds for the 24 h, before the pauses
PAUSE_S = 3.2                               # at each callout
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
UNIT3, PERSON, RUN, SIEVE, MIDI, UNITS = "#6250d6", "#eb6834", "#2a78d6", "#1baf7a", "#eda100", "#8e8f93"
ZONE_NAMES = {"atomizer": "the atomizer's zone", "sieving": "the sieving cell's zone", "midi": "the MIDI's zone",
              "night": "the nightly sweep"}


def day_data(day=DAY) -> dict:
    import timelapse as TL
    import upkeep as U
    d = json.loads((OUT / "floor_cleaning.json").read_text())
    jt = d["jobs"]["units_pou"]
    jobs = {z: v / 60 for z, v in jt["zone_min"].items()}
    night = jt["night_min"] / 60
    sim, up = FC._year_events(FC.SIM["seed"])
    oc = FC.own_cleaner(sim, jobs, night)
    a = U.at(day, 0.0)                      # clock 00:00 of the day, in the schedule's hours
    b = a + 24.0

    def clk(t):
        return t - a

    rows = {"person": [], "crucible": [], "atomize": [], "sieve": [], "depowder": [], "units": [], "unit3": [],
            "wait": []}
    s0, s1 = TL.PARAMS["shift"]["value"]
    shift = (s0, s1) if day % 7 < 5 else None
    for c0, c1 in U.crucible_hours(day):
        rows["crucible"].append((c0, c1))
    for m in sim["maint"]:
        if m["person_h"] > 0 and a <= m["t0"] < b:
            rows["person"].append((clk(m["t0"]), clk(m["t1"]), m["task"]))
    for e in sim["events"]:
        if e["step"] in ("atomize", "sieve", "depowder", "depowder_full") and e["t1"] > a and e["t0"] < b:
            k = "depowder" if e["step"].startswith("depowder") else e["step"]
            rows[k].append((clk(e["t0"]), clk(e["t1"]), e.get("alloy")))
    for t0, t1, u, st in sim["unit_log"]:
        if st in ("repowder", "sieve_cell", "aconity") and t1 > a and t0 < b:
            rows["units"].append((clk(t0), clk(t1), u, st))
    dock_of = {"atomizer": "repowder", "sieving": "sieve_cell", "midi": "aconity"}
    mine = [r for r in oc["log"] if r["t1"] > a and r["t0"] < b]
    for r in mine:
        rows["unit3"].append((clk(r["t0"]), clk(r["t1"]), r["zone"]))
        if r["t0"] - r["ready"] > 0.02:
            t0 = clk(r["t0"])
            if r["zone"] == "atomizer" and any(abs(t0 - c1) < 0.02 for _, c1 in rows["crucible"]):
                why = "person"                       # the person at the machine for a crucible hour
            elif any(abs(t0 - x1) < 0.02 and st == dock_of.get(r["zone"]) for x0, x1, u, st in rows["units"]):
                why = "dock"                         # unit 1 or 2 docked there
            else:
                why = "busy"                         # unit 3 itself, on another pass
            rows["wait"].append((clk(r["ready"]), t0, r["zone"], why))
    return dict(day=day, weekday=day % 7, shift=shift, rows=rows, year=d["year"]["unit3"])


def _hhmm(h):
    h = max(0.0, h)
    return f"{int(h) % 24:02d}:{int(round((h % 1) * 60)) % 60:02d}" if round((h % 1) * 60) < 60 else \
        f"{(int(h) + 1) % 24:02d}:00"


def callouts(dd) -> list:
    """(clock hour, text) for the moments the timeline stops on."""
    r = dd["rows"]
    out = []
    n0 = [x for x in r["unit3"] if x[2] == "night"]
    if n0:
        out.append((n0[0][0] + 0.15, f"{_hhmm(n0[0][0])}: the nightly sweep, every zone and the aisle "
                                     f"({(n0[0][1] - n0[0][0]) * 60:.0f} min in the model; floor_pass.py's route, "
                                     "bonding at every spot, takes 89). Nobody is in."))
    if dd["shift"]:
        out.append((dd["shift"][0] + 0.02, f"{_hhmm(dd['shift'][0])}: the person's shift starts with run 1's crucible "
                                           "hour at the atomizer (the crucible changed and coated by hand)."))
    first_person = next((w for w in r["wait"] if w[3] == "person"), None)
    if first_person:
        out.append((first_person[0] + 0.05,
                    f"{_hhmm(first_person[0])}: a run ends and the atomizer's floor pass is due, but the person is at "
                    f"the machine for the next run's crucible hour. Unit 3 waits {first_person[1] - first_person[0]:.1f} h"
                    " outside the zone, then cleans as the person leaves."))
    dock = next((w for w in r["wait"] if w[3] == "dock"), None)
    if dock:
        out.append((dock[0] + 0.02, f"{_hhmm(dock[0])}: a pass at {ZONE_NAMES[dock[2]]} waits "
                                    f"{(dock[1] - dock[0]) * 60:.0f} min while unit 1 or 2 is docked there."))
    busy = next((w for w in r["wait"] if w[3] == "busy"), None)
    if busy:
        out.append((busy[0] + 0.02, f"{_hhmm(busy[0])}: run 3's and a depowdering's passes fall due together; "
                                    f"{ZONE_NAMES[busy[2]]} waits {(busy[1] - busy[0]) * 60:.0f} min for unit 3 to "
                                    "finish the atomizer's. No crucible hour follows the last run, so that one goes "
                                    "straight away."))
    sv = next((x for x in r["unit3"] if x[2] == "sieving"), None)
    if sv:
        out.append((sv[0] + 0.03, f"{_hhmm(sv[0])}: the sieving's pass goes straight away: nobody is at that dock."))
    if dd["shift"]:
        out.append((dd["shift"][1] + 0.02, f"{_hhmm(dd['shift'][1])}: the person's shift ends. No pass waits for "
                                           "a person after this; a visible spill would wait for the morning."))
    return sorted(out)


def render(dd):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from PIL import Image
    import scene as S

    r = dd["rows"]
    cos = callouts(dd)
    # the clock against video time: BASE_S for the day, with a pause at each callout
    knots = [(0.0, 0.0)]
    vt = 0.0
    last = 0.0
    for h, _ in cos:
        vt += (h - last) / 24.0 * BASE_S
        knots.append((vt, h))
        vt += PAUSE_S
        knots.append((vt, h))
        last = h
    vt += (24.0 - last) / 24.0 * BASE_S
    knots.append((vt, 24.0))
    intro, outro = 1.5, 5.0
    total = intro + vt + outro
    kv = np.array([k[0] for k in knots])
    kh = np.array([k[1] for k in knots])

    fig = plt.figure(figsize=(W_PX / 100, H_PX / 100), dpi=100)
    fig.patch.set_facecolor(SURF)
    ax = fig.add_axes((0.20, 0.30, 0.775, 0.55))
    ax.set_facecolor(SURF)
    ax.set_xlim(0, 24)
    lanes = [("The person (on shift)", "person"), ("rePowder: atomizer runs", "atomize"),
             ("Sieving cell", "sieve"), ("Aconity MIDI: depowdering", "depowder"),
             ("Units 1-2 docked at these three", "units"), ("Unit 3: floor passes", "unit3")]
    ny = len(lanes)
    ax.set_ylim(-0.6, ny - 0.4)
    ax.set_yticks(range(ny), [l for l, _ in lanes][::-1] if False else [l for l, _ in lanes])
    ax.invert_yaxis()
    ax.set_xticks(range(0, 25, 2), [f"{h:02d}:00" for h in range(0, 25, 2)])
    ax.tick_params(colors=INK2, labelsize=9.5)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#9b9a94")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    yl = {k: i for i, (_, k) in enumerate(lanes)}
    blocks = []                                   # (t0, t1, y, h, colour, hatch)

    def add(t0, t1, k, col, h=0.56, hatch=None, alpha=1.0, z=3):
        y = yl[k]
        bg = Rectangle((t0, y - h / 2), max(t1 - t0, 0.04), h, fc=col, ec=SURF, lw=1.2, alpha=0.16, zorder=z)
        fg = Rectangle((t0, y - h / 2), 0.0, h, fc=col if hatch is None else "none", ec=col if hatch else SURF,
                       hatch=hatch, lw=0.0 if hatch else 1.2, alpha=alpha, zorder=z + 1)
        ax.add_patch(bg)
        ax.add_patch(fg)
        blocks.append((t0, max(t1 - t0, 0.04), fg))
    if dd["shift"]:
        ax.add_patch(Rectangle((dd["shift"][0], yl["person"] - 0.36), dd["shift"][1] - dd["shift"][0], 0.72,
                               fc="none", ec=PERSON, lw=1.0, ls=(0, (3, 2)), zorder=2))
        ax.text(dd["shift"][1] + 0.1, yl["person"] - 0.30, "shift", fontsize=8, color=INK2, va="center")
    for c0, c1 in r["crucible"]:
        add(c0, c1, "person", PERSON)
        ax.text((c0 + c1) / 2, yl["person"] + 0.48, "crucible", fontsize=7.5, color=INK2, ha="center", va="center")
    for t0, t1, task in r["person"]:
        add(t0, t1, "person", PERSON, h=0.32, alpha=0.55)
    for t0, t1, al in r["atomize"]:
        add(t0, t1, "atomize", RUN)
    for t0, t1, al in r["sieve"]:
        add(t0, t1, "sieve", SIEVE)
    for t0, t1, al in r["depowder"]:
        add(t0, t1, "depowder", MIDI)
    for t0, t1, u, st in r["units"]:
        add(t0, t1, "units", UNITS, h=0.40)
    last_lbl = -9.0
    for t0, t1, z in sorted(r["unit3"]):
        add(t0, t1, "unit3", UNIT3)
        lbl = {"atomizer": "atomizer", "sieving": "sieving", "midi": "MIDI", "night": "nightly sweep"}[z]
        if t0 - last_lbl >= 0.9:                 # a label only where it has room
            ax.text(t0, yl["unit3"] + 0.47, lbl, fontsize=7.2, color=INK2, ha="left", va="center")
            last_lbl = t0
    for t0, t1, z, why in r["wait"]:
        add(t0, t1, "unit3", {"person": PERSON, "dock": UNITS, "busy": UNIT3}[why], h=0.56, hatch="////", alpha=0.95)
    now = ax.axvline(0, color=INK, lw=1.2, zorder=8)
    clock = fig.text(0.20, 0.905, "", fontsize=24, weight="bold", color=INK, family="DejaVu Sans Mono", va="center")
    fig.text(0.012, 0.955, "A weekday of unit 3's floor passes, and where they wait for the person", fontsize=15,
             weight="bold", color=INK, va="center")
    wd = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][dd["weekday"]]
    fig.text(0.33, 0.905, f"{wd}, day {dd['day'] + 1} of floor_cleaning.py's year (upkeep.py's schedule, seed 303). "
             "All from the model.", fontsize=10, color=INK2, va="center")
    co = fig.text(0.20, 0.185, "", fontsize=12.5, color=INK, va="top", wrap=True, linespacing=1.4)
    y_ = dd["year"]
    fig.text(0.20, 0.065, f"The year (option C): {y_['passes']} passes after runs, sieving and depowdering. "
             f"{y_['waited_for_person']} waited for the person's crucible hour (at most {y_['latency']['max_h']} h), "
             f"{y_['waited_for_dock']} for a unit at the dock.", fontsize=9.5, color=INK2, va="center")
    fig.text(0.20, 0.025, "Hatched: a pass waiting, orange for the person, grey for a unit at the dock, purple for unit "
             "3 itself on another pass. Faint: still to come.", fontsize=8.8, color=INK2, va="center")
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                             f"{W_PX}x{H_PX}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "20", "-pix_fmt", "yuv420p", "-threads", "2", "-movflags", "+faststart",
                             str(OUT / "mp4" / f"{NAME}.mp4")], stdin=subprocess.PIPE)
    gif = []
    n = int(round(total * FPS))
    import textwrap
    for fi in range(n):
        v = fi / FPS - intro
        h = float(np.interp(v, kv, kh)) if v > 0 else 0.0
        now.set_xdata([h, h])
        for t0, w, fg in blocks:
            fg.set_width(min(w, max(0.0, h - t0)))
        clock.set_text(_hhmm(h) if h < 24 else "24:00")
        cur = [t for hh, t in cos if hh <= h + 1e-6]
        txt = cur[-1] if cur else "Unit 3 owns the powder floor; the person owns the crucible, the spills and the liners."
        if v > vt:
            txt = ("Unit 3 cleans as each step ends; the one place it yields to a person is the atomizer during a "
                   "crucible hour, and a visible spill is always the person's.")
        co.set_text("\n".join(textwrap.wrap(txt, 112)))
        fig.canvas.draw()
        fr = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        proc.stdin.write(np.ascontiguousarray(fr).tobytes())
        if math.floor(math.ceil(fi * GIF_FPS / FPS) * FPS / GIF_FPS) == fi:
            gif.append(Image.fromarray(fr).resize((800, 450), Image.LANCZOS))
    proc.stdin.close()
    proc.wait()
    plt.close(fig)
    S.write_gif(gif, OUT / f"{NAME}.gif")
    return dict(frames=n, seconds=round(n / FPS, 1), gif_mb=round((OUT / f"{NAME}.gif").stat().st_size / 1e6, 2))


if __name__ == "__main__":
    (OUT / "mp4").mkdir(parents=True, exist_ok=True)
    dd = day_data()
    info = render(dd)
    rec = dict(what="One weekday of unit 3's floor passes on floor_cleaning.py's year (floor_day.py): clock hours of the "
                    "day; all from the model", day=dd["day"], weekday=dd["weekday"], shift=dd["shift"],
               rows={k: [[round(v, 3) if isinstance(v, float) else v for v in x] if isinstance(x, (list, tuple)) else x
                         for x in vv] for k, vv in dd["rows"].items()},
               callouts=[[round(h, 3), t] for h, t in callouts(dd)], render=info)
    (OUT / f"{NAME}.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps(info), flush=True)
