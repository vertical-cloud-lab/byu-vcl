"""Tables for notes/vertical_lab_worth_it.md from twin/worth_it.py's runs (issue #407).

    python -m twin.worth_it tables         # rewrites out/worth_it/tables.md (and sens.md) from the saved results

Every figure is a median over the event logs (24 in the main grid: 12 seeds of BOFN, 12 of the funnel; 4 in the
sensitivities), with the 10th-90th percentile range where it is shown as "a-b". Pure standard library.
"""
from __future__ import annotations

import statistics
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "out" / "worth_it"
LAYOUT_NAME = {("vlm", 1): "VLM + 1 unit", ("flat", 2): "flat + 2 units", ("vlm", 2): "VLM + 2 units",
               ("flat", 1): "flat + 1 unit"}
ORDER = [("vlm", 1), ("flat", 2), ("vlm", 2), ("flat", 1)]
MODE_NAME = {"none": "the twin's timing (a load and an unload a step)",
             "cells": "PR 332's attended time (the arm stays for its share of each step; the powder line in a cell)",
             "pr332": "PR 332's attended time everywhere"}
TARGETS = (("flaime_al_T1", "Al SOTA"), ("flaime_al_T2", "Al halfway"), ("onr_cu_T1", "Cu SOTA"),
           ("onr_cu_T2", "Cu halfway"))


def _med(v):
    v = [x for x in v if x is not None]
    return statistics.median(v) if v else None


def _pct(v, f):
    v = sorted(x for x in v if x is not None)
    if not v:
        return None
    k = (len(v) - 1) * f
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def _f(x, nd=1, pct=False):
    if x is None:
        return "-"
    if pct:
        return f"{100 * x:.{nd}f} %"
    return f"{x:,.{nd}f}"


def _rng(v, nd=1, pct=False):
    m = _med(v)
    if m is None:
        return "-"
    lo, hi = _pct(v, 0.1), _pct(v, 0.9)
    if pct:
        return f"{100 * m:.{nd}f} % ({100 * lo:.{nd}f}-{100 * hi:.{nd}f})"
    return f"{m:,.{nd}f} ({lo:,.{nd}f}-{hi:,.{nd}f})"


def metrics(r: dict) -> dict:
    """The figures the note reports, from one run's summary."""
    e, i = r["external"], r["internal"]
    ops = r.get("openings") or {}
    trays = r.get("tray_locked") or {}
    busiest = max(trays.items(), key=lambda kv: kv[1]) if trays else (None, None)
    resp_i = (r.get("resp") or {}).get("IN_int") or {}
    resp_e = (r.get("resp") or {}).get("IN_ext") or {}
    out = dict(
        mm_busy=r["mm_busy"],
        opening=max((o["busy"] for o in ops.values()), default=None),
        opening_pres_day=sum(o["presentations_per_day"] for o in ops.values()) if ops else None,
        tray_busiest=busiest[1], tray_busiest_name=busiest[0],
        int_resp_min=resp_i.get("mean_min"), ext_resp_min=resp_e.get("mean_min"),
        int_end_h=i["end_delay_h"], int_end_p95_h=i["end_delay_p95_h"], int_start_min=i["start_delay_min"],
        int_end_p50_h=i.get("end_delay_p50_h"),
        atom_late=r.get("atomizer_late"), atom_runs=r.get("atomizer_runs"),
        ext_done_day=e["done_per_day"] if e["offered"] else None, ext_served=e["served"],
        ext_turn_h=e["turnaround_h"], ext_turn_p95_h=e["turnaround_p95_h"], ext_wait_h=e["start_wait_h"],
        drive_s=statistics.mean(m["drive_s_per_task"] for m in r["mm"]),
        tray_wait_s=(r.get("tray_wait_s") or {}).get("mean"),
        attended_h_day=r.get("attended_h_per_day"),
    )
    for k, _ in TARGETS:
        d, d0 = r["days"].get(k), r["days_twin"].get(k)
        out["shift_" + k] = (d - d0) if (d is not None and d0 is not None) else None
        out["reached_" + k] = d is not None
        out["twin_" + k] = d0
    return out


def _group(rows):
    g = defaultdict(list)
    for r in rows:
        mode = (r.get("params") or {}).get("attend", "none")
        g[(mode, r["ext_load"], r["layout"], r["n_mm"])].append(metrics(r))
    return g


def main_table(rows, mode: str) -> str:
    g = _group(rows)
    loads = sorted({k[1] for k in g if k[0] == mode})
    head = ("| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held by a run | "
            "Internal steps end later than the twin's, mean (h) | Atomizer runs off their slot | "
            "Outside jobs served | Outside jobs a day | Outside turnaround (h) | Outside turnaround, 95th pct (h) |")
    lines = [head, "|" + "---|" * 11]
    for ext in loads:
        for lay in ORDER:
            ms = g.get((mode, ext, *lay))
            if not ms:
                continue
            names = [m["tray_busiest_name"] for m in ms if m["tray_busiest_name"]]
            tray_name = max(set(names), key=names.count) if names else None
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                f"{100 * ext:.0f} %", LAYOUT_NAME[lay], _rng([m["mm_busy"] for m in ms], 0, pct=True),
                _rng([m["opening"] for m in ms], 0, pct=True) if lay[0] == "vlm" else "-",
                (_rng([m["tray_busiest"] for m in ms], 0, pct=True) + f" ({tray_name})") if lay[0] == "vlm" else "-",
                _rng([m["int_end_h"] for m in ms], 2),
                "%s; %d of %d logs" % (_f(_med([m["atom_late"] for m in ms]), 0),
                                      sum(1 for m in ms if (m["atom_late"] or 0) > 0), len(ms)),
                _f(_med([m["ext_served"] for m in ms]), 1, pct=True) if ext else "-",
                _f(_med([m["ext_done_day"] for m in ms]), 0) if ext else "-",
                _rng([m["ext_turn_h"] for m in ms], 1) if ext else "-",
                _f(_med([m["ext_turn_p95_h"] for m in ms]), 1) if ext else "-"))
    return "\n".join(lines)


def targets_table(rows, mode: str) -> str:
    g = _group(rows)
    loads = sorted({k[1] for k in g if k[0] == mode})
    lines = ["| Outside load | Layout | " + " | ".join(f"{n}: days later (median, max)" for _, n in TARGETS) + " |",
             "|" + "---|" * (2 + len(TARGETS))]
    for ext in loads:
        for lay in ORDER:
            ms = g.get((mode, ext, *lay))
            if not ms:
                continue
            cells = []
            for k, _ in TARGETS:
                v = [m["shift_" + k] for m in ms if m["shift_" + k] is not None]
                lost = sum(1 for m in ms if m["twin_" + k] is not None and not m["reached_" + k])
                c = f"{_med(v):.2f} ({max(v):.2f}; n={len(v)})" if v else "-"
                if lost:
                    c += f"; {lost} not reached"
                cells.append(c)
            lines.append(f"| {100 * ext:.0f} % | {LAYOUT_NAME[lay]} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def twin_days(rows) -> str:
    """The twin's own days to each target over the logs (the replay's reference)."""
    seen = {}
    for r in rows:
        seen.setdefault(r["log"], r["days_twin"])
    out = []
    for k, n in TARGETS:
        v = [d.get(k) for d in seen.values()]
        reached = [x for x in v if x is not None]
        out.append(f"{n}: reached in {len(reached)} of {len(v)} logs, median day "
                   f"{_med(reached):.0f}" if reached else f"{n}: not reached in any of {len(v)} logs")
    return "; ".join(out)


def handling_table(rows, mode: str) -> str:
    g = _group(rows)
    lines = ["| Outside load | Layout | Driving a task (s) | Waiting for the tray after arriving (s) | "
             "Request to the arm at the instrument, internal (min) | the same, outside jobs (min) | "
             "Tray presentations a day (both Shuttles) | Attended arm-hours a day |",
             "|" + "---|" * 8]
    for ext in sorted({k[1] for k in g if k[0] == mode}):
        for lay in ORDER:
            ms = g.get((mode, ext, *lay))
            if not ms:
                continue
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                f"{100 * ext:.0f} %", LAYOUT_NAME[lay], _f(_med([m["drive_s"] for m in ms]), 0),
                _f(_med([m["tray_wait_s"] for m in ms]), 0) if lay[0] == "vlm" else "-",
                _f(_med([m["int_resp_min"] for m in ms]), 1), _f(_med([m["ext_resp_min"] for m in ms]), 1),
                _f(_med([m["opening_pres_day"] for m in ms]), 0) if lay[0] == "vlm" else "-",
                _f(_med([m["attended_h_day"] for m in ms]), 1)))
    return "\n".join(lines)


def write(rows) -> str:
    parts = ["# Is the vertical lab worth it? The queue model's tables (issue #407)", "",
             "Written by `python -m twin.worth_it tables` from `out/worth_it/results.json.xz`. Simulated: the "
             "twin's round-3 event logs (24: 12 seeds of time-aware BOFN, 12 of the funnel, the vertical lab, one "
             "year) replayed through a transport layer with stand-in handling times (`twin/worth_it.py`, "
             "`Params`). Medians over the logs, 10th-90th percentile in brackets. An internal step's delay is "
             "against the twin's own end; the twin's 6 min transfer is credited back, so it can be negative. "
             "'Atomizer runs off their slot': runs that started more than 30 min after their slot in the twin "
             "(median over logs; how many logs had any). A replay keeps the twin's order, so one lost slot "
             "moves every later run: those rows are the cases to read as 'this many units can't carry it'.", "",
             "The twin's own days to its targets in these logs: " + twin_days(rows) + ".", ""]
    for mode in ("none", "cells"):
        if not any((r.get("params") or {}).get("attend", "none") == mode for r in rows):
            continue
        parts += [f"## Timing: {MODE_NAME[mode]}", "", main_table(rows, mode), "",
                  "Days to the twin's targets, later than the twin's own day:", "", targets_table(rows, mode), "",
                  "Handling:", "", handling_table(rows, mode), ""]
    text = "\n".join(parts)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables.md").write_text(text)
    return text


def write_sens(sens: dict) -> str:
    parts = ["# Sensitivities (issue #407)", "",
             "Written by `python -m twin.worth_it tables` from `out/worth_it/sensitivity.json.xz`: 4 logs (BOFN and "
             "the funnel, seeds 0-1), every layout, 30 % and 60 % outside load. Medians over the logs.", ""]
    for ext in (0.3, 0.6):
        parts += [f"## {100 * ext:.0f} % outside load", "",
                  "| Case | " + " | ".join(f"{LAYOUT_NAME[l]}: turnaround h; served; step delay h; atomizer runs "
                                         f"off slot; units busy; opening busy" for l in ORDER) + " |", "|" + "---|" * 5]
        for name, rows in sens.items():
            g = defaultdict(list)
            for r in rows:
                if abs(r["ext_load"] - ext) < 1e-9:
                    g[(r["layout"], r["n_mm"])].append(metrics(r))
            cells = []
            for lay in ORDER:
                ms = g.get(lay)
                if not ms:
                    cells.append("-")
                    continue
                cells.append("%s; %s; %s; %s; %s; %s" % (
                    _f(_med([m["ext_turn_h"] for m in ms]), 1), _f(_med([m["ext_served"] for m in ms]), 0, pct=True),
                    _f(_med([m["int_end_h"] for m in ms]), 1), _f(_med([m["atom_late"] for m in ms]), 0),
                    _f(_med([m["mm_busy"] for m in ms]), 0, pct=True),
                    _f(_med([m["opening"] for m in ms]), 0, pct=True) if lay[0] == "vlm" else "-"))
            parts.append(f"| {name} | " + " | ".join(cells) + " |")
        parts.append("")
    text = "\n".join(parts)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sens.md").write_text(text)
    return text
