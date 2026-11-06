"""The org page's GIF, remade in the lab as this branch has it: ``vertical-cloud-lab/.github``'s
``profile/vertical-lab.gif`` ("In a vertical lab, equipment is brought to the operator", PR #318).

The org README's figure caption says what it has to show: an electrified tray carries its instruments to a storage
position where experiments can run, and comes back to the operator when a sample needs moving. Here that is round 2's
example run, as the 9:09 clip (``animate.workflow``) stages it in the whole two-Shuttle lab, cut to one visit:

1. tray A, the CubXL laid out for DAL's corrosion screen, comes from its slot (R2) to Shuttle 1's opening;
2. the docked MiR250 + UR10e takes the vial of atomized powder off the holder on its own base and stands it in the
   CubXL's free seat, then parks: the same collision-checked moves as the 9:09 clip's step 5;
3. tray A goes back to its slot, docked to power, and the CubXL runs DAL's powder test there: ten 20 uL transfers of
   seawater onto the powder (``instruments_lab.powder_test``, the 9:09 clip's step 6).

The clip starts and ends with every tray in its slot and the arm parked. Only the vial is somewhere else (on the MiR,
then in the CubXL): the GIF dissolves back to the first frame over LOOP_FADE s, so it loops. Everything plays at
SPEED x the modelled times, and the GIF says so.

    VIZ3D_FPS=10 xvfb-run -a python3 org_gif.py views    # the candidate views, as stills -> /tmp/org_gif_views.png
    PREVIEW=1 xvfb-run -a python3 org_gif.py             # the last frame of each step -> /tmp/preview_<NAME>.png
    VIZ3D_FPS=10 xvfb-run -a python3 org_gif.py          # -> out/mp4/<NAME>.mp4, out/<NAME>.json
    python3 org_gif.py gif                               # -> out/<NAME>.gif: SPEED x, looped, for the org README
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

NAME = "org_vertical_lab"
TITLE = "In a vertical lab, equipment is brought to the operator"
SPEED = 2.0          # the GIF plays the clip at this many times its modelled speed, and says so
LOOP_FADE = 0.6      # s (at playback): the dissolve from the last frame back to the first
GIF_W = 1280         # px; the org README shows it about 830 px wide, so this stays sharp on a 2x display
TEXT = 1.45          # the overlay's text, against the scenes' 720p sizes: the README shows the GIF at about 0.65x

# the views (camera position, focal point, up), mm, Shuttle 1's centre at the origin, its opening facing -y
CAMS = {
    "lab_vlm": [(7600, -9000, 5200), (1600, -900, 1700), (0, 0, 1)],       # animate.CAM_LAB_VLM
    "lab_open": [(3500, -5900, 2700), (0, -1000, 1300), (0, 0, 1)],        # animate.CAM_LAB_OPEN
    "front34": [(4300, -8300, 3300), (700, -700, 1650), (0, 0, 1)],
    "front34_low": [(3900, -7600, 2300), (600, -800, 1700), (0, 0, 1)],
    "shuttle1": [(5600, -7400, 3800), (500, -600, 1750), (0, 0, 1)],
}


def build(data):
    """The whole lab (animate.lab_scene), with the corrosion CubXL that moves (cubxl_rig) on tray A, the vial on the
    docked MiR's holder, Shuttle 1's extractor at tray A's slot. -> (scene, lab, cub, test)."""
    import pyvista as pv

    import animate as A
    import cubxl_rig
    import instruments_lab as IL
    import props as P
    import vlm as V
    from scene import S, T
    sc, L = A.lab_scene(data, name=NAME, title=TITLE)
    sc.text_scale = TEXT
    L.show_gauges = False
    L.extra_gauges = []
    cub = cubxl_rig.CubRig(L)
    for key, g, names, _ in L.items.get("A", []):      # as animate.workflow: CubRig draws the set-up's CubXL, moving
        if key == "cubxl_corrosion":
            for nm in names:
                sc.alpha[nm] = 0.0
                sc.base_alpha[nm] = 0.0
    test = IL.powder_test()
    cub.pose(cubxl_rig.state_at(test, 0.0))
    # the vial, dosed with 25 mg of atomized powder on tray B (the 9:09 clip's steps 2-4), waits in the holder on the
    # docked MiR's cabinet: a heap on its floor at its angle of repose, to scale (animate.workflow)
    q = IL.POWDER_TEST
    rep = math.radians(34.0)
    r_heap = (3 * (q["mg"] / 1.4) / (math.pi * math.tan(rep))) ** (1 / 3)
    heap = pv.Cone(center=(0, 0, 0.5), direction=(0, 0, -1), height=1.0, radius=1.0, resolution=40).triangulate()
    sc.add("vial/heap", heap, P.POWDER, "vial_heap")
    sc.parent["vial_heap"] = "vial"
    sc.gmat["vial_heap"] = T((0, 0, P.VIAL_FLOOR)) @ S((r_heap, r_heap, r_heap * math.tan(rep)))
    sc.parent["vial"] = L.amr_group
    sc.gmat["vial"] = T(L.buffer_seat)
    L.powder_h = L.liquid_h = 0.0
    L.set_fill()
    # Shuttle 1's extractor waits at tray A's slot: where store() leaves it, so the clip ends as it starts
    L.lift_z = V.SLOTS[A.HOME["A"]][1]
    L.apply_state()
    return sc, L, cub, test


def views():
    """Stills of the candidate views: the lab at the start, then tray A at the opening."""
    from PIL import Image

    import animate as A
    import lab
    import vlm as V
    sc, L, cub, test = build(lab.meshes())
    shots = []
    for state in ("stored", "open"):
        if state == "open":
            L.tray["A"] = [*V.SLOTS["open"]]
            L.where["A"] = "open"
            L.lift_z = V.SLOTS["open"][1]
            L.apply_state()
        for key, cam in CAMS.items():
            sc.cam = [tuple(c) for c in cam]
            img = Image.fromarray(sc.render_base())
            shots.append((f"{key} / tray A {state}", img))
    tw, th = 640, 360
    sheet = Image.new("RGB", (tw * len(CAMS), th * 2), "white")
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, (lbl, im) in enumerate(shots):
        x, y = (i % len(CAMS)) * tw, (i // len(CAMS)) * th
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + 4), lbl, fill=(200, 0, 0))
    sheet.save("/tmp/org_gif_views.png")
    for lbl, im in shots:
        im.save(f"/tmp/org_gif_{lbl.replace(' / ', '_').replace(' ', '_')}.png")
    sc.pl.close()
    print("views -> /tmp/org_gif_views.png", flush=True)


def movie():
    import animate as A
    import cubxl_rig
    import instruments_lab as IL
    import lab
    from scene import FPS
    sc, L, cub, test = build(lab.meshes())
    rb, amr = L.robot, L.amr_group
    q = IL.POWDER_TEST
    cam0 = [tuple(c) for c in CAMS[os.environ.get("ORG_CAM", "front34")]]
    sc.cam = list(cam0)
    badge = f"{SPEED:g}x speed"
    area = math.pi * (A.P.VIAL_R - A.P.VIAL_WALL) ** 2
    grasp_z = 50.0
    # ---------------------------------------------------------------- 1. tray A comes to the opening
    cap = "A tray of instruments comes out of storage to the opening, where the operator is."
    sc.step(badge, cap, 0.6, None, hold=0.4)
    L.fetch("A", badge, cap)
    # ---------------------------------------------------------------- 2. the vial into the CubXL
    cap = "The operator, a mobile robot arm here, loads a sample: a vial of atomized powder for a corrosion test."
    buf = np.array(L.buffer_seat)
    p_buf = (sc.world(amr) @ np.r_[buf + (0, 0, grasp_z), 1.0])[:3]
    p_slot = cub.deck_world(*q["seat"], 0.0) + (0, 0, grasp_z)
    A.pick(L, rb, badge, cap, A.down(p_buf), A.down(p_buf + (0, 0, 120)), "vial")
    A.place(L, rb, badge, cap, A.down(p_slot, spin=0.0), A.down(p_slot + (0, 0, 130), spin=0.0), cub.body)
    sc.step(badge, cap, 1.4, rb.joint_to(A.PARK_RAD), hold=0.1)
    # ---------------------------------------------------------------- 3. back to its slot; the test runs there
    cap = "The tray goes back into storage, still powered, and the test runs there."
    L.store("A", badge, cap)

    def on_state(s):
        L.liquid_h = s["vial"] / area
        L.set_fill()
    sc.step(badge, cap, 5.0, cub.play(test, "start", "end", on_state), hold=0.6)
    out = sc.save()
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    return out


def gif():
    """out/mp4/<NAME>.mp4 -> out/<NAME>.gif: SPEED x, GIF_W wide, the last frame dissolving into the first."""
    from scene import OUT
    mp4, out = OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif"
    meta = json.loads((OUT / f"{NAME}.json").read_text())
    fps_in = meta["fps"]
    fps_out = fps_in * SPEED
    n_fade = max(1, int(round(LOOP_FADE * fps_out)))
    with tempfile.TemporaryDirectory() as tmp:
        # the clip, then n_fade frames dissolving from its last frame to its first: [0:v] is the clip; [1:v] its last
        # frame and [2:v] its first, each held n_fade frames, blended with a ramp
        dur = n_fade / fps_in
        fade = f"{tmp}/fade.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-sseof", f"-{1.5 / fps_in}", "-i", str(mp4), "-i",
                        str(mp4), "-filter_complex",
                        f"[0:v]select='eq(n,0)',loop={n_fade - 1}:1:0,setpts=N/{fps_in}/TB,format=rgb24[a];"
                        f"[1:v]select='eq(n,0)',loop={n_fade - 1}:1:0,setpts=N/{fps_in}/TB,format=rgb24[b];"
                        f"[a][b]blend=all_expr='A*(1-(N+1)/{n_fade + 1})+B*((N+1)/{n_fade + 1})',"
                        f"trim=duration={dur:.4f}",
                        "-r", str(fps_in), "-pix_fmt", "yuv444p", "-c:v", "libx264", "-crf", "12", fade], check=True)
        lst = f"{tmp}/list.txt"
        Path(lst).write_text(f"file '{mp4}'\nfile '{fade}'\n")
        joined = f"{tmp}/joined.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf",
                        f"setpts=PTS/{SPEED},fps={fps_out}", "-pix_fmt", "yuv444p", "-c:v", "libx264", "-crf", "12",
                        joined], check=True)
        pal = f"{tmp}/pal.png"
        vf = f"scale={GIF_W}:-1:flags=lanczos"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", joined, "-vf",
                        f"{vf},palettegen=max_colors=192:stats_mode=full", pal], check=True)
        raw = f"{tmp}/raw.gif"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", joined, "-i", pal, "-lavfi",
                        f"{vf}[x];[x][1:v]paletteuse=dither=none:diff_mode=rectangle", "-loop", "0", raw],
                       check=True)
        subprocess.run(["gifsicle", "-O3", "--lossy=40", "-o", str(out), raw], check=True)
    n = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of",
                            "csv=p=0", str(out)], capture_output=True, text=True).stdout.strip() or 0)
    print(f"{out}: {out.stat().st_size / 1e6:.2f} MB, {n} frames at {fps_out:g} fps ({n / fps_out:.1f} s)", flush=True)
    return out


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "movie"
    {"views": views, "movie": movie, "gif": gif}[arg]()
