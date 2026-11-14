"""Round 11 (#303, PR #318): run the stricter collision audit (collide.py) over audit-a's clips and gather the results.

Sterling, 2026-11-13, after the round-10 long-form: "There are probably other collisions and interferences that I didn't
catch from this". Each clip runs as ``ARM_AUDIT=1`` (nothing drawn, every frame checked: the arms with the 1.5 mm depth
limit on what may touch, and the movers check) under ``runner_guard.py``, one slot at a time, with
``ARM_AUDIT_SNAP=auto`` so the first frame of each new run of collisions is drawn, aimed at the contact:

    python3 audit_all.py list                       # the jobs: command, memory, where the JSON goes
    python3 audit_all.py run ch1 ch2 ... [--tag T]  # each job in turn through runner_guard (one slot at a time)
    python3 audit_all.py summary [--tag T]          # -> out/collisions/round11_summary.json, and a table on stdout
    xvfb-run -a python3 audit_all.py sheet          # -> out/collisions/round11_sheet.png: the worst frames, drawn
    python3 audit_all.py selftest                   # collide.depth() on known cases, then two scenes with known
                                                    # answers under ARM_AUDIT=1 (needs xvfb-run and a runner_guard slot)

``--tag`` (default ``r11``) is the audit's ARM_AUDIT_TAG: ``out/collisions/<clip>_<tag>.json``, so the round-10 JSONs
(``<clip>.json``, round 10's rules) stay as they were for before/after numbers. ``r11fix`` is used for the re-audit
after a clip's fixes. ``interference`` is interference.py over every model it knows (the MuJoCo check of the
instruments' own moving parts), which writes ``out/interference.json`` instead.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLL = HERE / "out" / "collisions"
SNAPS = Path(os.environ.get("ARM_AUDIT_SNAP_DIR", "/tmp/r11_snaps"))
DISPLAY = os.environ.get("AUDIT_DISPLAY", "43")

# name: (what, script and args, extra env, --mem MB, the scene names whose JSONs it writes)
JOBS = {
    "ch1": ("chapter 1, charging the crucible (alloy_charge.py, one arm)", ["alloy_charge.py"], {}, 3000,
            ["alloy_charge"]),
    "ch2": ("chapter 2, atomizing (alloy_atomize.py, two arms, the two-Shuttle floor)", ["alloy_atomize.py"], {}, 4500,
            ["alloy_atomize"]),
    # VLAB_ONLY_TRAYS=ABC: the trays it fetches (the others stay in their slots, which no arm or tray in this clip
    # reaches; setup_lab.build's comment); not for its render, whose Shuttles are open frames
    "workflow": ("the 8:00 clip (animate.py workflow, the whole lab)", ["animate.py", "workflow"],
                 {"VLAB_ONLY_TRAYS": "ABC"}, 4500, ["vlm_workflow"]),
    "baycam": ("the bay camera (services.py baycam; the lab stream's file: hits reported, not fixed)",
               ["services.py", "baycam"], {}, 3000, ["bay_camera"]),
    "scaleup": ("scaling up (scaleup.py: the EOS M 400-4 and the Meltio robot cell; no UR arm, movers only)",
                ["scaleup.py"], {}, 3000, ["scaleup"]),
    "interference": ("interference.py over every model (MuJoCo sweep, exact meshes)", ["interference.py"], {}, 3000,
                     []),
}


# what the stricter rules found outside audit-a's clips, and who fixed it (notes/arm_collisions.md)
FOUND_ELSEWHERE = [
    dict(what="stored trays, with their plates and service lines, into the drawn column supports as they are stored "
              "(tray F 50 mm in chapter 5's validation; audit-b's chapters)", check="movers",
         fixed="vlm.py, 063b014 (orchestrator): supports drawn only where a tray rests inside a slot, per Shuttle"),
    dict(what="the safety shutter 12 mm into the bay's side walls as it moves", check="movers",
         fixed="vlm.py, 063b014 (orchestrator): the walls stop 1 mm short of the shutter's path"),
    dict(what="the MiR's body 3 mm into the floor tape on every drive (props.mir250's skirt is drawn down to z = 0)",
         check="movers", fixed="collide.py (audit-a): the floor and its markings, anything within 6 mm of z = 0, "
                               "are not solid to the movers check"),
]
VALIDATION = dict(
    known_case="round 10's alloy_workflow.py, section 6 (CH5_FROM=6, VLAB_ONLY_TRAYS=F), camera F1 where round 10 had "
               "it: the tongs through F1's post, 25 mm, frames 333-370 (28 frames), caught; the tongs 6 mm into the "
               "MiR's cabinet (548-551), allowed by round 10's rules, caught",
    files=["out/collisions/round11_validation/ch5_section6_round10_camera_F1.json",
           "out/collisions/round11_validation/ch5_section6_round10_camera_F1_frame333.jpg",
           "out/collisions/round11_validation/ch5_section6_camera_F1_moved.json"],
    selftest="python3 audit_all.py selftest: depth() on known cases; a movers scene (cart into a wall 25 mm, door "
             "through a post 50 mm, scaled belt into a ceiling 25 mm caught; floor, 0.8 mm plate, own subtree not); "
             "an arm pushing a held cube 10 mm into its fixture (4 frames at 12 mm; 0 under round 10's rules)")


def command(job: str, tag: str) -> list[str]:
    what, args, env, mem, _ = JOBS[job]
    if job == "interference":
        return ["python3", *args]
    e = {"ARM_AUDIT": "1", "ARM_AUDIT_TAG": tag, "ARM_AUDIT_SNAP": "auto:24", "VIZ3D_FPS": "6", **env}
    return ["env", *[f"{k}={v}" for k, v in e.items()], "xvfb-run", f"--server-num={DISPLAY}", "-a", "python3", *args]


def run(jobs: list[str], tag: str):
    """Each job in turn, through runner_guard.py slot (so this stream holds one slot at a time)."""
    for job in jobs:
        what, args, env, mem, _ = JOBS[job]
        log = Path(f"/tmp/audita_{job}_{tag}.log")
        cmd = [sys.executable, str(HERE / "runner_guard.py"), "slot", "--mem", str(mem), "--label",
               f"audita-{job}-{tag}", "--", *command(job, tag)]
        t0 = time.time()
        print(f"{time.strftime('%H:%M:%S', time.gmtime())} {job}: {' '.join(cmd[2:])} -> {log}", flush=True)
        with open(log, "w") as fh:
            rc = subprocess.call(cmd, cwd=HERE, stdout=fh, stderr=subprocess.STDOUT)
        print(f"{time.strftime('%H:%M:%S', time.gmtime())} {job}: rc={rc} after {(time.time() - t0) / 60:.1f} min",
              flush=True)


ROUND10 = "d6eeeb7"          # the branch as round 11 started: round 10's JSONs, under round 10's rules


def _load(name: str, tag: str):
    p = COLL / f"{name}{'_' + tag if tag else ''}.json"
    if not tag:                # round 10's, from git (a re-render's own audit overwrites the file in the tree)
        r = subprocess.run(["git", "show", f"{ROUND10}:vertical-lab/{p.relative_to(HERE)}"], cwd=HERE,
                           capture_output=True, text=True)
        return (json.loads(r.stdout), p) if r.returncode == 0 else (None, p)
    return (json.loads(p.read_text()), p) if p.exists() else (None, p)


def _counts(rep: dict | None) -> dict | None:
    if rep is None:
        return None
    mv = rep.get("movers") or {}
    return dict(frames_checked=rep.get("frames_checked"), arm_frames=rep.get("frames_with_collisions"),
                arm_runs=len(rep.get("runs", [])), mover_frames=mv.get("frames_with_collisions"),
                mover_runs=len(mv.get("runs", [])) if mv else None,
                all_frames=rep.get("frames_with_collisions_all", rep.get("frames_with_collisions")),
                allowed_before_but_too_deep=rep.get("hits_allowed_before_but_too_deep"),
                rules=rep.get("rules_version", "round 10 (old)"))


def _worst_runs(rep: dict, n: int = 5) -> list[dict]:
    out = []
    for r in rep.get("runs", []):
        d = max([q.get("depth_mm") or 0 for q in r["pairs"]] + [0])
        out.append(dict(kind="arm", label=r["label"], frames=f"{r['first_frame']}-{r['last_frame']}",
                        n=r["frames"], depth_mm=d or None,
                        what="; ".join(f"{q['part']} in {q['other']}" for q in r["pairs"][:3])))
    for r in (rep.get("movers") or {}).get("runs", []):
        out.append(dict(kind="mover", label=r["label"], frames=f"{r['first_frame']}-{r['last_frame']}",
                        n=r["frames"], depth_mm=r["depth_mm"],
                        what="; ".join(f"{q['body']} into {q['other']}" for q in r["pairs"][:3])))
    out.sort(key=lambda r: -(r["n"] * (r["depth_mm"] or 50.0)))
    return out[:n]


def summary(tag: str, fixtag: str = "r11fix") -> dict:
    clips = {}
    for job, (what, args, env, mem, names) in JOBS.items():
        if job == "interference":
            p = HERE / "out" / "interference.json"
            if p.exists():
                d = json.loads(p.read_text())
                clips[job] = dict(what=what, summary=d.get("summary"), json=str(p.relative_to(HERE)))
            continue
        for name in names:
            old, p_old = _load(name, "")
            new, p_new = _load(name, tag)
            fix, p_fix = _load(name, fixtag)
            clips[name] = dict(
                what=what, job=job,
                round10_rules=dict(_counts(old) or {}, json=f"{ROUND10}:{p_old.relative_to(HERE)}") if old else None,
                round11_rules=dict(_counts(new) or {}, json=str(p_new.relative_to(HERE))) if new else None,
                after_fixes=dict(_counts(fix) or {}, json=str(p_fix.relative_to(HERE))) if fix else None,
                worst=_worst_runs(fix or new) if (fix or new) else [])
    sheet_rows = []
    for label, r10, before, after, who in SHEET_CLIPS:
        old_ = _load(r10, "")[0]

        def src(x):
            if isinstance(x, tuple):
                return x[2]
            if x and isinstance(x[0], (list, tuple)):
                for alt in x:
                    if isinstance(alt, tuple):
                        return alt[2]
                    if alt and all(_strict(n) for n in alt):
                        return [f"out/collisions/{n}.json" for n in alt]
                return None
            return [f"out/collisions/{n}.json" for n in x] if x else None
        b, a = _frames(before), _frames(after)
        sheet_rows.append(dict(
            clip=label, fixes_by=who,
            round10_rules=dict(frames=old_.get("frames_with_collisions"), of=old_.get("frames_checked"),
                               json=f"{ROUND10}:vertical-lab/out/collisions/{r10}.json") if old_ else None,
            round11_before_fixes=dict(frames=b[0], of=b[1], source=src(before)) if b else None,
            round11_after_fixes=dict(frames=a[0], of=a[1], source=src(after)) if a else "not re-audited"))
    out = dict(round=11, written=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
               every_clip=sheet_rows,
               found_by_the_movers_check_fixed_elsewhere=FOUND_ELSEWHERE, validation=VALIDATION,
               rules=("collide.py, round 11: what may touch only up to 1.5 mm deep (collide.depth, a 26-direction "
                      "translational depth), and the movers check (everything that moves and isn't an arm, new "
                      "contacts deeper than 1.5 mm); round 10's numbers are the same clips' JSONs under round 10's "
                      "rules (no depth limit, arms only), as committed"),
               clips=clips)
    COLL.mkdir(parents=True, exist_ok=True)
    (COLL / "round11_summary.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{'clip':16s} {'round 10 rules':>16s} {'round 11 rules (arm/movers/all)':>32s} {'after fixes':>20s}")
    for name, c in clips.items():
        if "summary" in c:
            print(f"{name:16s} {json.dumps(c['summary'])[:100]}")
            continue

        def f(x, full=True):
            if not x:
                return "-"
            if not full:
                return f"{x['arm_frames']} of {x['frames_checked']}"
            return f"{x['arm_frames']}/{x['mover_frames']}/{x['all_frames']} of {x['frames_checked']}"
        print(f"{name:16s} {f(c['round10_rules'], False):>16s} {f(c['round11_rules']):>32s} {f(c['after_fixes']):>20s}")
    return out


# The long-form's "How the models were checked" still: each clip's frames in collision under round 10's rules, under
# round 11's before the fixes and after them, and two of the frames found. (label, scene name of round 10's JSON at
# ROUND10, [JSONs before the fixes], [JSONs after], whose fixes). Several JSONs are summed (a chapter audited in parts).
SHEET_CLIPS = [
    # (label, round 10's JSON at ROUND10, before, after, whose). before/after: [names] summed, a list of such lists
    # (the first whose files all exist under round 11's rules is used: a final audit, then the partial ones), or
    # (frames, checked, source) for a run whose JSON was overwritten (the source is given in the streams' messages)
    ("Chapter 1: the charge", "alloy_charge", ["alloy_charge_r11"], ["alloy_charge"], "audit-a"),
    ("Chapter 2: atomizing", "alloy_atomize", ["alloy_atomize_r11"], [["alloy_atomize"], ["alloy_atomize_r11fix"]],
     "audit-a"),
    # audit-b: before is round 10's code under the strict rules, recovered from its printed report (138 of 1371); the
    # final is the render's own audit, the pre-render audit (8095c46) until then
    ("Chapter 3: sieve and print", "alloy_print", [["alloy_print_r11s0"], (138, 1371, "audit-b's report")],
     [["alloy_print"], ["alloy_print_r11_prerender"]], "audit-b"),                  # final: the render's own (a72df46)
    ("Chapter 4: powder checks", "alloy_powder", [], [["alloy_powder"]], "audit-b"),
    # ch5: before = its sections 1-5 and 6-7 on round 10's code (F1 already moved), 00:04-00:29, 209 + 214 of 962 +
    # 1003 frames; 148 of those were only the MiR's skirt in the floor tape, left out since (FLOOR_MM), so 275 here.
    # After = ch5-audit-final, the whole chapter as rendered (86ff959). The other alloy_workflow_s* are intermediate
    ("Chapter 5: cut, heat-treat, test", "alloy_workflow",
     (275, 1965, "ch5's alloy_workflow_s15 + _s67, less 148 frames of floor tape"), [["alloy_workflow"]], "ch5"),
    ("Chapter 6: sample prep", "alloy_prep", [], [["alloy_prep"]], "audit-b"),
    ("Chapter 7: characterize", "alloy_characterize", ["alloy_characterize_r11s0"], [["alloy_characterize"]],
     "audit-b"),
    ("The 8:00 clip: a vial dosed for the CubXL", "vlm_workflow", ["vlm_workflow_r11"], [["vlm_workflow_r11fix"]],
     "audit-a"),
    # upkeep's first full-clip strict run (01:19 UTC; its JSON since overwritten; numbers from upkeep's log): the arm
    # 0 of 1460, the movers check 120 of 1460
    ("Maintenance", "upkeep_clip", (120, 1460, "upkeep's log, 01:19"), [["upkeep_clip"]], "upkeep"),  # final: 443a7a4
    ("The bay camera", "bay_camera", ["bay_camera_r11"], [], "lab"),
    ("Scaling up: the EOS and the Meltio cell", "scaleup", ["scaleup_r11"], [["scaleup_r11fix"], ["scaleup_r11"]],
     "audit-a"),
]
SHEET_PICS = [
    ("out/collisions/round11_validation/ch5_section6_round10_camera_F1_frame333.jpg",
     "Chapter 5 as round 10 rendered it: the tongs through camera F1's post (25 mm, 28 frames). "
     "Sterling's own catch; the new audit finds it, and F1 has moved."),
    ("out/collisions/round11_validation/vlm_workflow_frame109_vial_in_solid_rack.jpg",
     "A fixture drawn solid: the vial lifted out of a rack whose pockets were only drawn as rims (25 mm). "
     "Round 10's rules let a held part touch its fixtures however deep; now only 1.5 mm."),
]


def _strict(n: str) -> bool:
    p = COLL / f"{n}.json"
    return p.exists() and str(json.loads(p.read_text()).get("rules_version", "")).startswith("round 11")


def _frames(names):
    """(frames in collision, frames checked) summed over JSONs (arms and movers), or None if any is missing. `names`
    may be (frames, checked, "source") for a run whose JSON was overwritten, or a list of alternatives (the first
    that is there, under round 11's rules, wins)."""
    if isinstance(names, tuple):
        return names[:2]
    if names and isinstance(names[0], (list, tuple)):
        for alt in names:
            if isinstance(alt, tuple):
                return alt[:2]
            if alt and all(_strict(n) for n in alt):
                return _frames(alt)
        return None
    bad = chk = 0
    for n in names:
        rep = _load(n, "x")[0] if False else (json.loads((COLL / f"{n}.json").read_text())
                                                if (COLL / f"{n}.json").exists() else None)
        if rep is None:
            return None
        bad += rep.get("frames_with_collisions_all", rep.get("frames_with_collisions", 0)) or 0
        chk += rep.get("frames_checked", 0) or 0
    return (bad, chk) if names else None


def sheet(n: int = 2, tag: str = "r11", out_name: str = "round11_sheet.png"):
    """out/collisions/round11_sheet.png, 1920 x 1080: SHEET_CLIPS' frames in collision (share of frames checked) under
    round 10's rules, round 11's before the fixes and after, and SHEET_PICS. Colours: one blue, two steps (the dataviz
    skill's ramp, validated as an ordinal pair: 2.44:1 for the light end on the surface)."""
    from PIL import Image, ImageDraw
    from scene import font
    W, H = 1920, 1080
    SURF, INK, INK2, MUTED, GRID = (252, 252, 251), (11, 11, 11), (82, 81, 78), (137, 135, 129), (226, 225, 221)
    DARK, LIGHT = (28, 92, 171), (109, 167, 236)              # blue 550 (before the fixes), blue 300 (after)
    img = Image.new("RGB", (W, H), SURF)
    d = ImageDraw.Draw(img)
    d.text((60, 34), "How the models were checked: round 11's stricter collision audit", fill=INK,
           font=font(44, bold=True))
    sub = ("Every frame, on the meshes as drawn (FCL). New in round 11: what an arm picks up or sets down may touch its "
           "fixtures only 1.5 mm deep, and everything else that moves (MiRs, trays, doors, people) is checked too.")
    words, line, ly = sub.split(), "", 98
    for w_ in words:                                             # wrap at word boundaries
        t = (line + " " + w_).strip()
        if d.textlength(t, font=font(24)) > W - 120 and line:
            d.text((60, ly), line, fill=INK2, font=font(24))
            ly, line = ly + 32, w_
        else:
            line = t
    d.text((60, ly), line, fill=INK2, font=font(24))
    # legend
    y = 174
    d.rounded_rectangle((60, y + 4, 92, y + 24), 4, fill=DARK)
    d.text((102, y), "Round 11's rules, before the fixes", fill=INK, font=font(22))
    d.rounded_rectangle((520, y + 4, 552, y + 24), 4, fill=LIGHT)
    d.text((562, y), "After the fixes", fill=INK, font=font(22))
    d.text((800, y), "Round 10's rules: the figure in grey", fill=MUTED, font=font(22))
    # rows
    rows = []
    for label, r10, before, after, who in SHEET_CLIPS:
        old = _load(r10, "")[0]
        o = (old.get("frames_with_collisions", 0), old.get("frames_checked", 0)) if old else None
        rows.append((label, o, _frames(before), _frames(after), who))
    vmax = max([100.0 * b[0] / b[1] for _, _, b, _, _ in rows if b and b[1]] +
               [100.0 * a[0] / a[1] for _, _, _, a, _ in rows if a and a[1]] + [5.0])
    vmax = 5.0 * math.ceil(vmax / 5.0)
    x0, x1 = 660, 1060                                          # the bars' baseline and full scale
    top, rh = 240, 70
    for k in range(int(vmax / 5) + 1):                          # recessive grid, every 5 %
        gx = x0 + (x1 - x0) * (5.0 * k / vmax)
        d.line((gx, top - 2, gx, top + rh * len(rows) - 3), fill=GRID, width=1)
        d.text((gx - 14, top + rh * len(rows) + 2), f"{5 * k} %", fill=MUTED, font=font(18))
    d.text((x0, top - 22), "share of the frames checked that have a collision", fill=MUTED, font=font(17))
    for r, (label, o, b, a, who) in enumerate(rows):
        y = top + r * rh
        d.text((60, y + 2), label, fill=INK, font=font(24, bold=True))
        old_txt = f"round 10: {o[0]} of {o[1]}" if o else "round 10: not audited"
        d.text((60, y + 34), old_txt, fill=MUTED, font=font(20))
        for k, (val, col) in enumerate(((b, DARK), (a, LIGHT))):
            by = y + 4 + k * 32
            if val is None:
                d.text((x0, by - 2), "before the fixes: not on record" if k == 0 else
                       "after: not re-audited", fill=MUTED, font=font(19))
                continue
            frac = val[0] / val[1] if val[1] else 0.0
            bw = (x1 - x0) * (100.0 * frac / vmax)
            if val[0] > 0:
                d.rounded_rectangle((x0, by, x0 + max(bw, 6), by + 24), 4, fill=col)
            pct = 100 * frac
            pct_txt = (f" ({pct:.1f} %)" if pct >= 0.05 else " (under 0.1 %)") if val[0] else ""
            d.text((x0 + max(bw, 0) + 12, by - 1), f"{val[0]} of {val[1]} frames" + pct_txt,
                   fill=INK if k == 0 else INK2, font=font(21, bold=(k == 1 and val[0] == 0)))
        d.line((60, y + rh - 3, x1 + 200, y + rh - 3), fill=GRID, width=1)
    # two frames found
    px, pw = 1400, 470
    ph = int(pw * 9 / 16)
    py = 240
    for path, cap in SHEET_PICS[:n]:
        p_ = HERE / path
        if not p_.exists():
            continue
        im = Image.open(p_).convert("RGB")
        im = im.crop((0, 34, im.width, im.height)) if im.height == 720 else im
        img.paste(im.resize((pw, ph), Image.LANCZOS), (px, py))
        d.rectangle((px, py, px + pw - 1, py + ph - 1), outline=GRID, width=1)
        words, line, ly = cap.split(), "", py + ph + 8
        for w_ in words:                                         # wrap the caption to the picture's width
            t = (line + " " + w_).strip()
            if d.textlength(t, font=font(19)) > pw and line:
                d.text((px, ly), line, fill=INK2, font=font(19))
                ly, line = ly + 24, w_
            else:
                line = t
        d.text((px, ly), line, fill=INK2, font=font(19))
        py = ly + 44
    d.text((60, H - 30), "red in a picture: the parts in collision.  Data: out/collisions/round11_summary.json;  "
           "checker: collide.py;  notes: notes/arm_collisions.md", fill=MUTED, font=font(18))
    out = COLL / out_name
    img.save(out, optimize=True)
    print(f"{out.relative_to(HERE)}: {len(rows)} clips, {min(n, len(SHEET_PICS))} frames")
    return out


# ------------------------------------------------------------------------------------------- self-tests
def selftest_depth():
    """collide.depth() against known penetrations, coarse and fine meshes (notes/arm_collisions.md's table)."""
    import numpy as np
    import pyvista as pv
    import collide as CL

    def body(mesh, name):
        t = CL._tris(mesh.triangulate().clean())
        b = CL.Body(name, name, *t)
        b.src = t                                  # so depth() measures it shrunk by TOUCH_MM, as in the audits
        b.place(np.eye(4))
        return b
    block = {"coarse": pv.Box((-50, 50, -50, 50, -50, 0)), "fine": pv.Box((-50, 50, -50, 50, -50, 0), level=20)}
    want = {0.3: 1.5, 1.0: 1.5, 2.0: 3.0, 3.0: 3.0, 10.0: 12.0, 25.0: 25.0}
    ok = True
    for d, w in want.items():
        got = [CL.depth(body(pv.Box((-10, 10, -10, 10, -d, 40 - d), level=lv), "f"), body(block[bn], "b"))
               for bn in block for lv in (0, 8)]
        ok &= all(g == w for g in got)
        print(f"finger sunk {d:4.1f} mm: {got} (expected {w:g})")
    for d, w in {0.5: 1.5, 8.0: 12.0}.items():
        s_ = pv.Sphere(radius=15, center=(0, 0, 15 - d), theta_resolution=40, phi_resolution=40)
        got = [CL.depth(body(s_, "s"), body(block[bn], "b")) for bn in block]
        ok &= all(g == w for g in got)
        print(f"sphere sunk {d} mm: {got} (expected {w:g})")
    clear = CL.depth(body(pv.Box((-10, 10, -10, 10, 0.2, 40)), "f"), body(block["fine"], "b"))
    ok &= clear == 0.0
    print(f"0.2 mm clear: {clear} (expected 0)")
    # fits (charge.lathe parts, both windings): a 20 mm peg 20 mm into a bore of its own size reads as touching
    # (TOUCH_MM), 0.3 mm clearance as clear, 0.3 mm interference as deep (the shortest move that frees it is out)
    import charge as C
    for wind in (1, -1):
        for r_bore, w in ((10.0, CL.TOUCH_MM), (10.3, 0.0), (9.7, 25.0)):
            peg = C.lathe([(0, -20), (10, -20), (10, 20), (0, 20)][::wind], res=64)
            ring = C.lathe([(r_bore, -20), (20, -20), (20, 0), (r_bore, 0)][::wind], res=64)
            got = CL.depth(body(peg, "p"), body(ring, "r"))
            ok &= got == w
            print(f"peg in a bore of radius {r_bore} (winding {wind:+d}): {got} (expected {w:g})")
    print("DEPTH SELFTEST", "OK" if ok else "FAILED")
    return ok


def _selftest_movers():
    """A scene whose movers are known: run under ARM_AUDIT=1."""
    import numpy as np
    import pyvista as pv
    import scene as SC
    from scene import T, R
    sc = SC.Scene("r11_movers_selftest", "movers self-test")
    sc.add("floor", pv.Box((-2000, 2000, -2000, 2000, -20, 0)), "grey", "static")
    sc.add("pad", pv.Box((300, 500, -400, 400, 0, 0.8)), "orange", "pad")          # a 0.8 mm floor plate: shallow
    sc.add("wall", pv.Box((1220, 1400, -600, 600, 0, 800)), "white", "wall")       # the cart ends 20 mm into it
    sc.add("cart/body", pv.Box((-200, 200, -300, 300, -0.5, 400), level=4), "blue", "cart")   # 0.5 mm into the floor
    sc.add("cart/lift", pv.Box((-150, 150, -250, 250, 380, 420)), "green", "cart_lift")       # its own subtree
    sc.parent["cart_lift"] = "cart"
    sc.add("machine", pv.Box((-1500, -1000, 500, 1000, 0, 900)), "white", "machine")
    sc.add("door", pv.Box((-1000, -995, 500, 1000, 0, 900)), "red", "door")       # hinged at (-1000, 500)
    sc.parent["door"] = "machine"
    sc.add("post", pv.Cylinder(center=(-753, 747, 450), direction=(0, 0, 1), radius=40, height=900), "black", "post")
    sc.add("pulley", pv.Box((1700, 1800, -50, 50, -100, 0)), "grey", "pulley")     # the belt stands on it
    sc.add("belt", pv.Box((1730, 1770, -20, 20, 0, 1)), "black", "belt")          # 1 mm tall, drawn scaled
    sc.gmat["belt"] = np.diag([1.0, 1.0, 50.0, 1.0])
    sc.add("ceiling", pv.Box((1600, 1900, -100, 100, 380, 420)), "grey", "ceiling")

    def drive(u):
        sc.gmat["cart"] = T((1040.0 * u, 0, 0))              # front 200 + 1040 = 1240: 20 mm into the wall
    def lift(u):
        sc.gmat["cart_lift"] = T((0, 0, -30.0 * u))          # down into its own cart
    def swing(u):
        sc.gmat["door"] = R((0, 0, 1), -75.0 * u, pivot=(-1000, 500, 0))   # through the post
    def stretch(u):
        sc.gmat["belt"] = np.diag([1.0, 1.0, 50.0 + 350.0 * u, 1.0])         # 400 mm tall: 20 mm into the ceiling
    sc.step("drive", "cart over the plate into the wall", 4.0, drive, hold=0.2)
    sc.step("lift", "the lift sinks into its own cart", 1.0, lift, hold=0.2)
    sc.step("door", "the door swings into the post", 2.0, swing, hold=0.2)
    sc.step("belt", "a scaled belt grows into the ceiling", 1.0, stretch, hold=0.2)
    rep = sc.save()
    got = {(q["body"], q["other"]) for r in rep["movers"]["runs"] for q in r["pairs"]}
    ok = {("cart/body", "wall"), ("door", "post"), ("belt", "ceiling")} <= got and \
        not any(o in ("floor", "pad") or b == "cart/lift" for b, o in got)
    print("MOVERS SELFTEST", "OK" if ok else f"FAILED: {sorted(got)}")
    sys.exit(0 if ok else 1)


def _selftest_arm():
    """An arm holding a 30 mm cube pushes it 10 mm into the fixture it puts it down on: run under ARM_AUDIT=1."""
    import pyvista as pv
    import robot
    import scene as SC
    from scene import T
    sc = SC.Scene(os.environ.get("TEST_NAME", "r11_arm_selftest"), "arm depth self-test")
    sc.add("floor", pv.Box((-2000, 2000, -2000, 2000, -20, 0)), "grey", "static")
    rb = robot.Robot(sc, "ur10e", "static", T((0, 0, 0)), q0=[0, -90, 90, -90, -90, 0])
    Tt = rb.tcp_world()
    p = Tt[:3, 3]
    sc.add("part", pv.Box((-15, 15, -15, 15, -15, 15)), "orange", "part")
    sc.gmat["part"] = T(p)
    sc.add("fixture", pv.Box((p[0] - 60, p[0] + 60, p[1] - 60, p[1] + 60, 0, p[2] - 45.0)), "white", "fixture")
    rb.grasp("part")
    down = Tt.copy()
    down[2, 3] -= 40.0                                       # the cube's bottom ends 10 mm into the fixture
    sc.step("down", "into the fixture", 2.0, rb.line_to(down), hold=0.2)
    rb.release("fixture")
    sc.step("away", "up", 1.0, rb.line_to(Tt), hold=0.2)
    rep = sc.save()
    strict = rep["rules_version"].startswith("round 11")
    ok = (rep["frames_with_collisions"] > 0 and rep["runs"][0]["pairs"][0].get("depth_mm") == 12.0) if strict else \
        rep["frames_with_collisions"] == 0
    print("ARM SELFTEST", rep["rules_version"], "OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


def selftest() -> bool:
    ok = selftest_depth()
    base = ["xvfb-run", f"--server-num={DISPLAY}", "-a", sys.executable, str(Path(__file__).resolve())]
    for env, arg in (({}, "_selftest_movers"), ({}, "_selftest_arm"),
                     ({"ARM_AUDIT_RULES": "old", "TEST_NAME": "r11_arm_selftest_old"}, "_selftest_arm")):
        e = dict(os.environ, ARM_AUDIT="1", VIZ3D_FPS="6", **env)
        ok &= subprocess.call(base + [arg], cwd=HERE, env=e) == 0
    for n in ("r11_movers_selftest", "r11_arm_selftest", "r11_arm_selftest_old"):
        (COLL / f"{n}.json").unlink(missing_ok=True)
    print("SELFTEST", "OK" if ok else "FAILED")
    return ok


if __name__ == "__main__":
    a = sys.argv[1:]
    tag = "r11"
    if "--tag" in a:
        i = a.index("--tag")
        tag = a[i + 1]
        a = a[:i] + a[i + 2:]
    if not a or a[0] == "list":
        for job, (what, args, env, mem, names) in JOBS.items():
            print(f"{job:12s} --mem {mem}  {' '.join(command(job, tag))}\n             {what}")
    elif a[0] == "run":
        run(a[1:] or [j for j in JOBS], tag)
    elif a[0] == "summary":
        summary(tag)
    elif a[0] == "sheet":
        sheet(tag=tag)
    elif a[0] == "selftest":
        sys.exit(0 if selftest() else 1)
    elif a[0] in ("_selftest_movers", "_selftest_arm"):
        globals()[a[0]]()
    else:
        sys.exit(__doc__)
