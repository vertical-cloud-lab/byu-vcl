"""Round 15 (#303, PR #318): the final pass, every 3-D clip of the long-form rendered again at 1280 x 720, drawn at up
to 30 fps, each checking its own frames as it renders (collide.py's strict rules), into out/r15/ (git-ignored).

Sterling, 2026-11-23: "re-render everything in a self-consistent and cohesive way. Fix collisions, nonsensical parts,
etc. ... In a final pass, render at a higher res (max fps for 720p) and upload to YouTube". On the 4-core runner a
whole-lab frame at 720p costs about as much as round 13's 1080p frame did at 10-15 fps, so the clips are drawn at the
highest rate the six hours allowed: FPS below, per job. Each job runs through runner_guard.py (memory-gated slots).

    python3 render_r15.py list                 # the jobs, their fps, memory and whether their output exists
    python3 render_r15.py queue JOB ...        # start each job detached through runner_guard (bg); logs /tmp/rl/
    python3 render_r15.py check [JOB ...]      # outputs: frames, fps, and the inline audit's frames in collision
    python3 render_r15.py fabjoin              # the nine fabrication clips -> out/r15/fabrication_tour.mp4

The long-form then builds from out/r15/ with LONGFORM_HD_DIR=r15 LONGFORM_SIZE=1280x720 LONGFORM_FPS=30.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
R15 = OUT / "r15"
LOGS = Path("/tmp/rl")
COMMON = dict(VIZ3D_HD="1", VIZ3D_HD_DIR="r15", VIZ3D_SIZE="1280x720", VIZ3D_HD_CLEAN="0", VIZ3D_AUDIT="1",
              VIZ3D_PROGRESS="1")

TOUR = ["stream_cam", "tensile_h", "glovebox_tray", "glovebox", "fumehood", "fumehood_tray", "storage",
        "powder_store_feed", "powder_store_lots", "packaging", "ded", "hip", "cubxl_corrosion"]
ATOM = ["atom_cameras", "atom_latch", "atom_container", "atom_vacuum", "atom_plate", "atom_crucible_out", "atom_bn",
        "atom_crucible_in"]

# name: (argv after python3, extra env, --mem MB, fps, outputs under out/r15/)
JOBS: dict[str, tuple[list[str], dict, int, int, list[str]]] = {}
for k in TOUR:
    JOBS[f"t_{k}"] = (["tour.py", k], {}, 2000, 30, [f"instruments/{k}.mp4"])
JOBS["ot2"] = (["ot2_corrosion.py"], {}, 2500, 30, ["instruments/ot2_corrosion_prep.mp4"])
JOBS["coupling"] = (["coupling.py", "movie"], {}, 3000, 30, ["vlm_coupling.mp4"])
JOBS["vacuum_press"] = (["vacuum_press.py"], {}, 2500, 30, ["vacuum_press.mp4"])
JOBS["dag"] = (["route_dag.py"], {}, 1500, 30, [f"dag/route_dag_ch{i}.mp4" for i in range(1, 8)])
for k in ATOM:   # atom_crucible.py renders both crucible clips: `out` (taking the furnace apart) and `in` (the rebuild)
    argv = ["atom_crucible.py", k.rsplit("_", 1)[1]] if k.startswith("atom_crucible_") else [f"{k}.py"]
    JOBS[k] = (argv, {}, 4500 if k == "atom_cameras" else 3500, int(os.environ.get("R15_FPS_ATOM", "15")), [f"{k}.mp4"])
FAB = ["metalone", "snowpod", "mprint", "meltio_m450", "form4", "form_wash", "form_cure", "stencil", "lumenpnp"]
for k in FAB:
    JOBS[f"f_{k}"] = (["fab_tour.py", k], {}, 2000, 30, [f"fabrication/{k}.mp4"])
# whole-lab and chapter clips (fps set when the final floor is in: see FPS_HEAVY)
FPS_HEAVY = int(os.environ.get("R15_FPS_HEAVY", "15"))
JOBS.update({
    "setup": (["setup_lab.py"], {}, 6500, FPS_HEAVY, ["setup_lab.mp4"]),
    "svc_services": (["services.py", "services"], {}, 6000, FPS_HEAVY, ["vlm_services.mp4"]),
    "svc_hookups": (["services.py", "hookups"], {}, 6000, FPS_HEAVY, ["vlm_hookups.mp4"]),
    "svc_baycam": (["services.py", "baycam"], {}, 6000, FPS_HEAVY, ["bay_camera.mp4"]),
    "svc_cabling": (["services.py", "cabling"], {}, 6000, FPS_HEAVY, ["vlm_cabling.mp4"]),
    "workflow": (["animate.py", "workflow"], {}, 6500, FPS_HEAVY, ["vlm_workflow.mp4"]),
    "icpms": (["icpms.py"], {}, 5500, FPS_HEAVY, ["icpms.mp4"]),
    "ch1": (["alloy_charge.py"], {"VLAB_ONLY_TRAYS": "B"}, 4500, FPS_HEAVY, ["alloy_charge.mp4"]),
    # chapter 2 splices the lab's footage into its render and writes out/mp4/alloy_atomize.mp4 at the render's size;
    # `collect` copies the MP4 to out/r15/. Chapters 1, 2 and 6 were re-planned this round and audited by their
    # helpers on the final code (strict rules, 10-12 fps: out/collisions/*_r15fix_*), so their renders skip the
    # inline audit, which costs about as much CPU as the drawing (AUDITED below)
    "ch2": (["alloy_atomize.py"], {}, 5000, FPS_HEAVY, ["alloy_atomize.mp4"]),
    "ch3": (["alloy_print.py"], {}, 5500, FPS_HEAVY, ["alloy_print.mp4"]),
    "ch4": (["alloy_powder.py"], {"VLAB_ONLY_TRAYS": "DEM"}, 4500, FPS_HEAVY, ["alloy_powder.mp4"]),
    "ch5": (["alloy_workflow.py"], {"VLAB_ONLY_TRAYS": "F"}, 4500, FPS_HEAVY, ["alloy_workflow.mp4"]),
    "ch6": (["alloy_prep.py"], {"VLAB_ONLY_TRAYS": "FM"}, 4500, FPS_HEAVY, ["alloy_prep.mp4"]),
    "ch7": (["alloy_characterize.py"], {"VLAB_ONLY_TRAYS": "DEKL"}, 4500, FPS_HEAVY, ["alloy_characterize.mp4"]),
    "upkeep": (["upkeep_clip.py"], {}, 5500, FPS_HEAVY, ["upkeep_clip.mp4"]),
    "scaleup": (["scaleup.py"], {}, 6000, FPS_HEAVY, ["scaleup.mp4"]),
    "finale": (["timelapse.py"], {"VIZ3D_HD_CLEAN": "1"}, 6500, FPS_HEAVY, ["timelapse.mp4"]),
    "safety": (["safety.py", "clip"], {}, 6000, FPS_HEAVY, ["safety.mp4"]),
    "machining": (["machining_cell.py"], {}, 5000, FPS_HEAVY, ["machining_cell.mp4"]),
    "floorclean": (["floor_clean_people.py"], {}, 5000, FPS_HEAVY, ["floor_clean_people.mp4"]),
    "basecams_vlm": (["base_cameras.py", "vlm"], {}, 5000, FPS_HEAVY, ["base_cameras_vlm.mp4"]),
    "basecams_atom": (["base_cameras.py", "atomizer"], {}, 4500, FPS_HEAVY, ["base_cameras_atomizer.mp4"]),
})


# round 15: clips whose helper audited the final code at 10-15 fps; their final render draws without auditing again
# (chapter 2 was, but chapter 1's carrier re-spacing moved its cups afterwards, so it audits itself again; chapter 1's
# last fix had no audit yet, so it does too)
AUDITED = {"ch6", "atom_crucible_out", "atom_crucible_in", "atom_container", "icpms"}


def fps_of(name: str) -> int:
    return int(os.environ.get(f"R15_FPS_{name.upper()}", JOBS[name][3]))


def queue(names: list[str]) -> None:
    LOGS.mkdir(exist_ok=True)
    # --normal: queue at runner_guard's normal priority, ahead of the --low bulk; for light clips that fit in the
    # memory a whole-lab render leaves, so a core doesn't sit idle while the big ones wait for memory
    prio = [] if "--normal" in names else ["--low"]
    names = [n for n in names if n != "--normal"]
    for n in names:
        argv, env, mem, _, _ = JOBS[n]
        e = dict(COMMON, **env, VIZ3D_FPS=str(fps_of(n)))
        if n in AUDITED:
            e["VIZ3D_AUDIT"] = ""
        cmd = ["python3", "runner_guard.py", "bg", "--log", str(LOGS / f"{n}.log"), "--mem", str(mem), "--label", n, *prio,
               "--", "env"] + [f"{k}={v}" for k, v in e.items()] + ["xvfb-run", "-a", "python3"] + argv
        pid = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True).stdout.strip()
        print(f"{n}: pid {pid}, {fps_of(n)} fps, --mem {mem}")


def probe(p: Path) -> str:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,nb_frames", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return r.stdout.strip() or "unreadable"


def audit_of(rel: str) -> str:
    a = OUT / "collisions" / (rel[:-4] + ".json")
    if not a.exists():
        return "no audit"
    d = json.loads(a.read_text())
    return (f"audit {d.get('fps')} fps: {d.get('frames_with_collisions')} arm / "
            f"{d.get('frames_with_collisions_all', d.get('frames_with_collisions'))} all of {d.get('frames_checked')}")


def check(names: list[str]) -> None:
    for n in names or list(JOBS):
        for rel in JOBS[n][4]:
            p = R15 / rel
            print(f"{n:16s} {rel:40s} {probe(p) if p.exists() else 'missing':24s} {audit_of(rel)}")


def fabjoin() -> None:
    """The fabrication tour from this pass's clips where they exist (30 fps), else the committed 720p ones (15 fps:
    round 15 re-rendered only the clips whose captions changed), re-encoded to one 30 fps file."""
    parts = []
    for k in FAB:
        p = R15 / "fabrication" / f"{k}.mp4"
        parts.append(p if p.exists() else OUT / "mp4" / "fabrication" / f"{k}.mp4")
    lst = Path("/tmp/r15_fab_concat.txt")
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-threads", "2", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-vf", "fps=30,setsar=1", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt",
                    "yuv420p", "-movflags", "+faststart", str(R15 / "fabrication_tour.mp4")], check=True)
    print("fabrication_tour:", ", ".join(f"{p.parent.parent.name}/{p.name}" for p in parts))


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("list", [])
    if cmd == "queue":
        queue(args)
    elif cmd == "check":
        check(args)
    elif cmd == "fabjoin":
        fabjoin()
    elif cmd == "collect":                       # chapter 2's spliced MP4 into out/r15/
        import shutil
        shutil.copy2(OUT / "mp4" / "alloy_atomize.mp4", R15 / "alloy_atomize.mp4")
        # the splice's JSON has the footage in its sub-steps; longform.clip_meta reads out/clean/ first for out/r15/
        shutil.copy2(OUT / "alloy_atomize.json", OUT / "clean" / "alloy_atomize.json")
        print("alloy_atomize.mp4 and its spliced JSON ->", R15, "and out/clean/")
    else:
        for n, (argv, env, mem, fps, outs) in JOBS.items():
            print(f"{n:16s} {' '.join(argv):32s} {fps_of(n):3d} fps {mem:5d} MB {env} -> {outs}")
