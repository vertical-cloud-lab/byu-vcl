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
