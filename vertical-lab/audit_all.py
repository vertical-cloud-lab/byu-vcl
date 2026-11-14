"""Round 11 (#303, PR #318): run the stricter collision audit (collide.py) over audit-a's clips and gather the results.

Sterling, 2026-11-13, after the round-10 long-form: "There are probably other collisions and interferences that I didn't
catch from this". Each clip runs as ``ARM_AUDIT=1`` (nothing drawn, every frame checked: the arms with the 1.5 mm depth
limit on what may touch, and the movers check) under ``runner_guard.py``, one slot at a time, with
``ARM_AUDIT_SNAP=auto`` so the first frame of each new run of collisions is drawn, aimed at the contact:

    python3 audit_all.py list                       # the jobs: command, memory, where the JSON goes
    python3 audit_all.py run ch1 ch2 ... [--tag T]  # each job in turn through runner_guard (one slot at a time)
    python3 audit_all.py summary [--tag T]          # -> out/collisions/round11_summary.json, and a table on stdout
    xvfb-run -a python3 audit_all.py sheet          # -> out/collisions/round11_sheet.png: the worst frames, drawn

``--tag`` (default ``r11``) is the audit's ARM_AUDIT_TAG: ``out/collisions/<clip>_<tag>.json``, so the round-10 JSONs
(``<clip>.json``, round 10's rules) stay as they were for before/after numbers. ``r11fix`` is used for the re-audit
after a clip's fixes. ``interference`` is interference.py over every model it knows (the MuJoCo check of the
instruments' own moving parts), which writes ``out/interference.json`` instead.
"""
from __future__ import annotations

import json
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
    "ch1": ("chapter 1, charging the crucible (alloy_charge.py, one arm)", ["alloy_charge.py"], {}, 4000,
            ["alloy_charge"]),
    "ch2": ("chapter 2, atomizing (alloy_atomize.py, two arms, the two-Shuttle floor)", ["alloy_atomize.py"], {}, 6500,
            ["alloy_atomize"]),
    "workflow": ("the 8:00 clip (animate.py workflow, the whole lab)", ["animate.py", "workflow"], {}, 6500,
                 ["vlm_workflow"]),
    "baycam": ("the bay camera (services.py baycam; the lab stream's file: hits reported, not fixed)",
               ["services.py", "baycam"], {}, 4000, ["bay_camera"]),
    "scaleup": ("scaling up (scaleup.py: the EOS M 400-4 and the Meltio robot cell; no UR arm, movers only)",
                ["scaleup.py"], {}, 4000, ["scaleup"]),
    "interference": ("interference.py over every model (MuJoCo sweep, exact meshes)", ["interference.py"], {}, 4000,
                     []),
}


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


def _load(name: str, tag: str):
    p = COLL / f"{name}{'_' + tag if tag else ''}.json"
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
                round10_rules=dict(_counts(old) or {}, json=str(p_old.relative_to(HERE))) if old else None,
                round11_rules=dict(_counts(new) or {}, json=str(p_new.relative_to(HERE))) if new else None,
                after_fixes=dict(_counts(fix) or {}, json=str(p_fix.relative_to(HERE))) if fix else None,
                worst=_worst_runs(fix or new) if (fix or new) else [])
    out = dict(round=11, written=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
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


def sheet(n: int = 12, tag: str = "r11"):
    """The worst frames of every clip, from the ARM_AUDIT_SNAP=auto close-ups, ranked by run length x depth."""
    from PIL import Image, ImageDraw
    from scene import font
    picks = []
    for job, (what, args, env, mem, names) in JOBS.items():
        for name in names:
            idx = SNAPS / f"{name}_snaps.json"
            if not idx.exists():
                continue
            rep = _load(name, tag)[0] or {}
            runs = [(r["first_frame"], r["frames"], max([q.get("depth_mm") or 50.0 for q in r["pairs"]]))
                    for r in rep.get("runs", [])]
            runs += [(r["first_frame"], r["frames"], r["depth_mm"]) for r in (rep.get("movers") or {}).get("runs", [])]
            for s in json.loads(idx.read_text()):
                score = max([nf * d for f0, nf, d in runs if abs(f0 - s["frame"]) <= 1] + [0.0])
                if score > 0:
                    picks.append((score, name, s))
    picks.sort(key=lambda x: -x[0])
    picks = picks[:n]
    if not picks:
        print("no snaps to draw")
        return
    tw, th, cap = 480, 270, 46
    cols = 4
    rows = (len(picks) + cols - 1) // cols
    img = Image.new("RGB", (tw * cols, (th + cap) * rows + 40), "white")
    d = ImageDraw.Draw(img)
    d.text((12, 10), "Round 11's stricter audit: the worst frames (collide.py; red = the parts in collision; "
                     "close-ups aimed at the contact)", fill=(20, 20, 24), font=font(18, bold=True))
    for k, (score, name, s) in enumerate(picks):
        x, y = (k % cols) * tw, 40 + (k // cols) * (th + cap)
        im = Image.open(s["file"]).convert("RGB")
        im = im.crop((0, 34, im.width, im.height)).resize((tw, th), Image.LANCZOS)
        img.paste(im, (x, y))
        txt = f"{name} frame {s['frame']} ({s['label']})"
        d.text((x + 6, y + th + 3), txt[:62], fill=(20, 20, 24), font=font(13, bold=True))
        d.text((x + 6, y + th + 22), ("; ".join(s["hits"]))[:70], fill=(170, 20, 20), font=font(12))
    out = COLL / "round11_sheet.png"
    img.quantize(colors=200).save(out, optimize=True)
    print(f"{out.relative_to(HERE)}: {len(picks)} frames")


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
    else:
        sys.exit(__doc__)
