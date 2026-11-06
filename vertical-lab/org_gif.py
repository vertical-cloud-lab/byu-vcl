"""The org page's GIF, remade in the lab as this branch has it: ``vertical-cloud-lab/.github``'s
``profile/vertical-lab.gif`` ("In a vertical lab, equipment is brought to the operator", PR #318).

The org README's figure caption says what it has to show: an "electrified" tray carries its instruments to a storage
position where experiments can run, and comes back to the operator when a sample needs moving. Here that is the 9:09
clip's corrosion test (``animate.workflow``, DAL's powder reactivity test), in the whole two-Shuttle lab as the set-up
leaves it, as one cycle:

1. tray A, the CubXL laid out for DAL's corrosion screen, waits at Shuttle 1's opening; the docked MiR250 + UR10e
   takes a vial of atomized powder off the holder on its own base and stands it in the CubXL's free seat, then parks
   (the 9:09 clip's step 5, the same collision-checked moves);
2. tray A goes back to its slot (R2), where its dock keeps it powered, and the CubXL runs the test there: ten 20 uL
   transfers of seawater onto the powder (``instruments_lab.powder_test``, the 9:09 clip's step 6);
3. tray A comes back to the opening, and the arm takes the vial out to its holder and parks.

The last frame is the first one again (tray A at the opening, the vial on the holder, the arm parked, Shuttle 1's
extractor at the opening), so the GIF loops without a cut. What differs is too small to see: one used 20 uL tip is in
the CubXL's waste, and the vial holds 200 uL, 0.4 mm deep. The GIF plays everything at SPEED x the modelled times and
says so; the CubXL's test, minutes long, is compressed further, and its label says that.

    VIZ3D_FPS=10 xvfb-run -a python3 org_gif.py views    # the candidate views, as stills -> /tmp/org_gif_views.png
    PREVIEW=1 xvfb-run -a python3 org_gif.py             # the last frame of each step -> /tmp/preview_<NAME>.png
    ARM_AUDIT=1 xvfb-run -a python3 org_gif.py           # no render: every frame's arm checked -> out/collisions/
    VIZ3D_FPS=10 xvfb-run -a python3 org_gif.py          # -> out/mp4/<NAME>.mp4, out/<NAME>.json, out/<NAME>_still.png
    python3 org_gif.py gif                               # -> out/<NAME>.gif: SPEED x, for the org README
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np

NAME = "org_vertical_lab"
TITLE = "In a vertical lab, equipment is brought to the operator"
SPEED = 2.0          # the GIF plays the clip at this many times its modelled speed, and says so
GIF_W = 1280         # px; the org README shows it about 830 px wide, so this stays sharp on a 2x display
TEXT = 1.45          # the overlay's text, against the scenes' 720p sizes: the README shows the GIF at about 0.65x

# the views: camera position, focal point, up (mm; Shuttle 1's centre at the origin, its opening facing -y), view angle
CAMS = {
    "lab_vlm": [(7600, -9000, 5200), (1600, -900, 1700), (0, 0, 1)],       # animate.CAM_LAB_VLM
    "lab_open": [(3500, -5900, 2700), (0, -1000, 1300), (0, 0, 1)],        # animate.CAM_LAB_OPEN
    "front34_low": [(3900, -7600, 2300), (600, -800, 1700), (0, 0, 1)],
    "v1": [(3900, -7600, 2300), (600, -800, 1850), (0, 0, 1), 33.0],
    "w1": [(3900, -7600, 2300), (450, -800, 1900), (0, 0, 1), 34.0],
    "w2": [(3700, -7900, 2350), (450, -800, 1900), (0, 0, 1), 33.0],
    "w3": [(4100, -7400, 2300), (500, -800, 1900), (0, 0, 1), 34.0],
    "shuttle1": [(5600, -7400, 3800), (500, -600, 1750), (0, 0, 1)],
    "s1a": [(5600, -7400, 3800), (500, -600, 1850), (0, 0, 1), 31.0],
    "s1b": [(5400, -7600, 3500), (450, -650, 1850), (0, 0, 1), 31.0],
    "s1c": [(6000, -7800, 3900), (700, -600, 1900), (0, 0, 1), 30.0],
}
CAM = "s1a"
# leader-label boxes, as fractions of the frame (the overlay draws a line from each to its point in the lab)
LBL = {"arm": (0.03, 0.86), "cub": (0.02, 0.47), "run": (0.02, 0.47), "vlm": (0.02, 0.10)}
# This view looks down from behind the south row, and the south row's overhead utilities (its cable tray at 3.2 m with
# its network cable, hangers, drops and junction boxes, the DED's argon run, the fume hood's duct; setup_lab.utilities)
# cross the frame's lower left between the camera and Shuttle 1. For this shot they are left out: every utility cell
# south of Y_CUT. The north row's, over the Shuttles, stay.
Y_CUT = -4000.0


def build(data):
    """The whole lab (animate.lab_scene), with the corrosion CubXL that moves (cubxl_rig) on tray A, tray A at Shuttle
    1's opening, the vial on the docked MiR's holder, the arm parked. -> (scene, lab, cub, test)."""
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
    # tray A at Shuttle 1's opening, the extractor there with it: where fetch() leaves them, so the clip ends as it starts
    L.use(1)
    L.tray["A"] = [*V.SLOTS["open"]]
    L.where["A"] = "open"
    L.lift_z = V.SLOTS["open"][1]
    L.shutter = 0.0
    L.apply_state()
    clear_view(sc)
    return sc, L, cub, test


def clear_view(sc):
    """Leave the south row's overhead utilities out of the shot (Y_CUT)."""
    import pyvista as pv
    for nm in [n for n in sc.actors if n.startswith("util/")]:
        mesh = pv.wrap(sc.actors[nm].GetMapper().GetInput())
        if mesh.n_cells == 0:
            continue
        keep = np.flatnonzero(mesh.cell_centers().points[:, 1] > Y_CUT)
        if len(keep) == mesh.n_cells:
            continue
        if len(keep) == 0:
            sc.alpha[nm] = 0.0
            continue
        sc.set_mesh(nm, mesh.extract_cells(keep).extract_surface(algorithm="dataset_surface"))


def set_cam(sc, key):
    cam = CAMS[key]
    sc.cam = [tuple(float(v) for v in c) for c in cam[:3]]
    sc.view_angle = cam[3] if len(cam) > 3 else 30.0


def views():
    """Stills of the candidate views (ORG_VIEWS=a,b,... picks some): tray A at the opening, then in its slot."""
    from PIL import Image, ImageDraw

    import animate as A
    import lab
    import vlm as V
    sc, L, cub, test = build(lab.meshes())
    keys = [k for k in CAMS if not os.environ.get("ORG_VIEWS") or k in os.environ["ORG_VIEWS"].split(",")]
    shots = []
    for state in ("open", "stored"):
        if state == "stored":
            L.tray["A"] = [*V.SLOTS[A.HOME["A"]]]
            L.where["A"] = A.HOME["A"]
            L.lift_z = V.SLOTS[A.HOME["A"]][1]
            L.apply_state()
        for key in keys:
            set_cam(sc, key)
            shots.append((f"{key} / tray A {state}", Image.fromarray(sc.render_base())))
    tw, th = 640, 360
    sheet = Image.new("RGB", (tw * len(keys), th * 2), "white")
    d = ImageDraw.Draw(sheet)
    for i, (lbl, im) in enumerate(shots):
        x, y = (i % len(keys)) * tw, (i // len(keys)) * th
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + 4), lbl, fill=(200, 0, 0))
        im.save(f"/tmp/org_gif_{lbl.replace(' / ', '_').replace(' ', '_')}.png")
    sheet.save("/tmp/org_gif_views.png")
    sc.pl.close()
    print("views -> /tmp/org_gif_views.png", flush=True)


def movie():
    """The cycle, rendered real-time. The scene draws only the leader labels: the title, the step captions and the
    speed badge go in the GIF's header band (gif()), from the phases written into out/<NAME>.json."""
    import animate as A
    import instruments_lab as IL
    import lab
    from scene import OUT
    sc, L, cub, test = build(lab.meshes())
    sc.title = ""
    rb, amr = L.robot, L.amr_group
    q = IL.POWDER_TEST
    set_cam(sc, os.environ.get("ORG_CAM", CAM))
    sc.intro = 0.6
    area = math.pi * (A.P.VIAL_R - A.P.VIAL_WALL) ** 2
    grasp_z = 50.0
    buf = np.array(L.buffer_seat)
    p_buf = (sc.world(amr) @ np.r_[buf + (0, 0, grasp_z), 1.0])[:3]
    p_slot = cub.deck_world(*q["seat"], 0.0) + (0, 0, grasp_z)
    arm_at = sc.world(rb.root)[:3, 3]
    lbl_arm = ("the operator: a MiR250 + UR10e", tuple(arm_at + (0.0, -200.0, -150.0)), LBL["arm"])
    lbl_cub = ("tray A at the opening:\nthe CubXL, a corrosion test", tuple(cub.deck_world(200.0, 150.0, 260.0)),
               LBL["cub"])
    at_opening = [lbl_arm, lbl_cub]
    phases = []

    def phase(text):
        phases.append(dict(start_frame=sc.n, text=text))

    def on_state(s):
        L.liquid_h = s["vial"] / area
        L.set_fill()
    # ---------------------------------------------------------------- 1. the vial into the CubXL, at the opening
    # each phase's labels stay up through all its sub-steps (Scene.sticky_labels), and the last phase's are the
    # first's, so the labels match where the GIF loops
    lbl_vlm = ("Kardex Shuttle XP 500:\nevery tray docked to power", (-700.0, -1540.0, 3000.0), LBL["vlm"])
    phase("The operator, here a mobile robot arm, loads the next sample onto the tray.")
    sc.sticky_labels = at_opening
    A.pick(L, rb, "", "", A.down(p_buf), A.down(p_buf + (0, 0, 120)), "vial")
    A.place(L, rb, "", "", A.down(p_slot, spin=0.0), A.down(p_slot + (0, 0, 130), spin=0.0), cub.body)
    sc.step("", "", 1.4, rb.joint_to(A.PARK_RAD), hold=0.1)
    # ---------------------------------------------------------------- 2. back to its slot; the test runs there
    phase("The tray goes back into storage, still powered, and the experiment runs there.")
    sc.sticky_labels = [lbl_vlm]
    L.store("A", "", "")
    lbl_run = ("tray A in its slot: the test runs\nthere (time-lapse)", tuple(cub.deck_world(200.0, 150.0, 200.0)),
               LBL["run"])
    sc.sticky_labels = [lbl_vlm, lbl_run]
    sc.step("", "", 0.6, None, hold=0.0)
    sc.step("", "", 5.0, cub.play(test, "start", "end", on_state), hold=0.6)
    # ---------------------------------------------------------------- 3. back to the opening; the vial out
    phase("When the sample needs moving, the tray comes back to the operator.")
    sc.sticky_labels = [lbl_vlm]
    L.fetch("A", "", "")
    phase("The arm takes the tested sample out, and the tray is free for the next one.")
    sc.sticky_labels = at_opening
    A.pick(L, rb, "", "", A.down(p_slot, spin=0.0), A.down(p_slot + (0, 0, 130), spin=0.0), "vial")
    A.place(L, rb, "", "", A.down(p_buf), A.down(p_buf + (0, 0, 120)), amr)
    sc.step("", "", 1.4, rb.joint_to(A.PARK_RAD), hold=0.4, still=True)
    out = sc.save()
    print(f"highest forearm/wrist point {rb.max_z_world:.0f} mm", flush=True)
    meta_path = OUT / f"{NAME}.json"
    if meta_path.exists() and not os.environ.get("ARM_AUDIT") and not os.environ.get("PREVIEW"):
        meta = json.loads(meta_path.read_text())
        meta.update(title=TITLE, speed=SPEED, camera=os.environ.get("ORG_CAM", CAM), phases=phases)
        meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    return out


BAND = 86            # px at 1280 wide: the white header band over the render that holds the GIF's text


def header(img, caption: str):
    """The frame under a white band: the org page's title, the step's caption and the speed badge."""
    from PIL import Image, ImageDraw

    import scene as SC
    w = img.width
    k = w / 1280
    H = int(round(BAND * k))
    out = Image.new("RGB", (w, img.height + H), "white")
    out.paste(img, (0, H))
    d = ImageDraw.Draw(out)
    d.text((18 * k, 9 * k), TITLE, font=SC.font(29 * k, bold=True), fill=(20, 20, 24))
    d.text((18 * k, 50 * k), caption, font=SC.font(21 * k), fill=(55, 58, 66))
    fb = SC.font(20 * k, bold=True)
    badge = f"{SPEED:g}× speed"
    x1 = w - 18 * k
    x0 = x1 - d.textlength(badge, font=fb) - 26 * k
    d.rounded_rectangle((x0, 12 * k, x1, 46 * k), 6 * k, fill=(30, 60, 140))
    d.text((x0 + 13 * k, 17 * k), badge, font=fb, fill=(255, 255, 255))
    d.line([(0, H - 1), (w, H - 1)], fill=(30, 60, 140), width=max(1, int(round(2 * k))))
    return out


def gif(width=GIF_W, lossy=40, colors=192):
    """out/mp4/<NAME>.mp4 -> out/<NAME>.gif, every frame at SPEED x the MP4's rate, each under the header band; and the
    same frames as out/mp4/<NAME>_readme.mp4 (SPEED x, h264), for anyone who would rather embed a video. One palette
    for the whole clip (the camera holds still), no dithering, then gifsicle -O3 --lossy."""
    from PIL import Image

    from scene import OUT
    mp4, out = OUT / "mp4" / f"{NAME}.mp4", OUT / f"{NAME}.gif"
    meta = json.loads((OUT / f"{NAME}.json").read_text())
    phases = meta["phases"]
    fps = meta["fps"] * SPEED
    sw, sh = meta["size"]
    w, h = width, int(round(sh * width / sw / 2)) * 2
    with tempfile.TemporaryDirectory() as tmp:
        dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf",
                                f"scale={w}:{h}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                               stdout=subprocess.PIPE)
        n = 0
        while True:
            buf = dec.stdout.read(w * h * 3)
            if len(buf) < w * h * 3:
                break
            cap = [p["text"] for p in phases if p["start_frame"] <= n][-1]
            header(Image.frombytes("RGB", (w, h), buf), cap).save(f"{tmp}/{n:05d}.png", compress_level=1)
            n += 1
        dec.wait()
        seq = ["-framerate", f"{fps:g}", "-i", f"{tmp}/%05d.png"]
        pal = f"{tmp}/pal.png"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq, "-vf",
                        f"palettegen=max_colors={colors}:stats_mode=full", pal], check=True)
        raw = f"{tmp}/raw.gif"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq, "-i", pal, "-lavfi",
                        "[0:v][1:v]paletteuse=dither=none:diff_mode=rectangle", "-loop", "0", raw], check=True)
        subprocess.run(["gifsicle", "-O3", f"--lossy={lossy}", "-o", str(out), raw], check=True)
        vid = OUT / "mp4" / f"{NAME}_readme.mp4"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *seq, "-c:v", "libx264", "-crf", "20", "-preset", "slow",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(vid)], check=True)
        Image.open(f"{tmp}/00000.png").save(OUT / f"{NAME}_first.png", optimize=True)
    msg = (f"{out.name}: {out.stat().st_size / 1e6:.2f} MB, {w} x {h + int(round(BAND * w / 1280))}, {n} frames at "
           f"{fps:g} fps ({n / fps:.1f} s); {vid.name}: {vid.stat().st_size / 1e6:.2f} MB")
    print(msg, flush=True)
    return msg


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "movie"
    {"views": views, "movie": movie, "gif": gif}[arg]()
