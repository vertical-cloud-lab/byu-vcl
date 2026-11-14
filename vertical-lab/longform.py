"""The vertical cloud lab, start to finish (#303): everything on PR #318 in one long-form video, with chapters.

    python3 longform.py plan       # the parts in order, their sources and lengths; nothing is encoded
    python3 longform.py            # -> out/mp4/vertical_lab_longform.mp4, out/longform.json, out/longform_sheet.png
    python3 longform.py upload     # unlisted, the chapter timestamps in the description; recorded in out/youtube.json

Every part is a clip that renders on its own, from its own script, with its own GIF, MP4 and JSON. This file only
puts them in order, draws a title card before each chapter, draws a caption band on the stills (the figures and the
contact sheets) and a REAL FOOTAGE badge on the one piece of real video, and writes the chapter list. Every part is
re-encoded once to 1280 x 720 at 15 fps before the join, as in ``alloy_route.py``, so clips rendered at 10 fps keep
their length.

A clip that isn't there is left out with a warning, so the join always runs on whatever is rendered.
"""
from __future__ import annotations

import datetime as dt
import os
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
MP4 = OUT / "mp4"
NAME = "vertical_lab_longform"
SIZE, FPS = (1280, 720), 15
CARD_S = 5.5
THREADS = ["-threads", os.environ["FFMPEG_THREADS"]] if os.environ.get("FFMPEG_THREADS") else []   # runner_guard.py sets 2
GAP = 10.4                     # YouTube drops every chapter if one is under 10 s
BLUE = (30, 60, 140)
GREY = (110, 114, 120)
INK = (40, 42, 46)
REPO = "vertical-cloud-lab/byu-vcl"
PR = f"https://github.com/{REPO}/pull/318"


def font(size, bold=False):
    from PIL import ImageFont
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for d in ("/usr/share/fonts/truetype/dejavu", str(HERE / "fonts")):
        p = Path(d) / name
        if p.exists():
            return ImageFont.truetype(str(p), int(size))
    return ImageFont.load_default()


# Clips taken from the two PRs stacked on this one, at the commit named, without merging them (they are still under
# review): PR #320 (claude/issue-303-r5-cutaways), round 2's equipment in cutaway; PR #321 (claude/issue-303-r5-fixes),
# round 4's review fixes, among them every MiR250 drive at its published 0.3 m/s^2 and the 68SC-2's bar at 3 x 1 mm.
R2 = "5a39245"
FIXES = "a34367a"
# Round 9's two stacked PRs, figures only: #328 (claude/issue-303-edm-orientations), #327 (claude/issue-303-repowder-model)
EDM = "193778b"
REPOWDER = "f9db700"          # #327's second pass (round 10): door, clamps, viewport, a second held-out frame

# ===================================================================================================== the chapters
# Each chapter: a key, its title (also the YouTube chapter line), the card's lines, and its parts in order. A part is
#   ("mp4", rel under out/mp4, label or None)                    a rendered clip, whole
#   ("still", rel under out, seconds, caption, label or None)    a figure, letterboxed, or scrolled if it is tall
#   ("footage", rel under out, caption, label or None)           real video, with a REAL FOOTAGE badge and a credit
# A label starts a YouTube chapter of its own inside the chapter (merged into the next if it would be under 10 s).
CHAPTERS = [
    dict(key="intro", title="A real VLM, then the plan",
         card=["A Kardex vertical lift module (VLM) holds the lab's equipment on electrified trays, each powered tray "
               "with its own UPS. A UR10e arm on a MiR250 mobile base works at its opening and at the machines too big for a tray.",
               "Everything after the first clip is a 3-D animation, built from the makers' published figures and "
               "photos and checked for collisions. Real footage, photos and data are badged as such."],
         parts=[("footage", "footage/vlm_real_ck8QJhVqPiY.mp4",
                 "A real VLM in operation, from the sample's perspective (Sterling Baird, youtu.be/ck8QJhVqPiY)",
                 None)]),
    dict(key="setup", title="The lab set up from scratch",
         card=["An empty bay: the layout taped out, utilities overhead, two Kardex Shuttle XP 500s going up with a "
               "996 mm opening, the floor machines, the arm assembled onto its MiR250, then every tray loaded by "
               "people: a UPS and stream cameras on each powered one, neither on the sample and powder-jar stores, "
               "whose short trays the camera over each bay inventories."],
         parts=[("mp4", "setup_lab.mp4", None),
                ("still", "tray_plan.png", 14.0, "Every tray from above, with its UPS, dock plate and cameras where it "
                 "needs them, and the slot each one takes", "What goes on which tray")]),
    dict(key="services", title="Services: UPS, automatic hookups, cabling and cameras",
         card=["Each powered tray carries a UPS. In its slot and again in the picking bay, a dock in the side wall mates "
               "with the tray's coupling plate: mains, Ethernet, air, N2 and chilled water. In transit the dock "
               "shuts and vents the lines, and the tray runs on its UPS.",
               "Then the cabling, the stream camera unit, and what the camera over the bay sees."],
         parts=[("mp4", "vlm_hookups.mp4", "Storage to the bay: the hookups and the UPS"),
                ("mp4", "vlm_services.mp4", "The docks in every slot"),
                ("still", "dock_lift_clearance.png", 10.0, "Do the docks reach into the lift's path? Clearances, "
                 "docks in and out", "The docks against the lift"),
                ("mp4", "vlm_cabling.mp4", "Cabling"),
                ("mp4", "instruments/stream_cam.mp4", "The stream camera unit: height, pan, tilt"),
                ("mp4", "bay_camera.mp4", "The camera over the bay, and what it sees")]),
    dict(key="corrosion", title="Tray A: the corrosion station, OT-2 and CubXL",
         card=["The OT-2 makes up the CubXL's electrolyte and dilutes the corrosion wells' samples for ICP-MS, which "
               "goes out to the BYU Spectroscopic Facility (digital-wetlab PR #83, direction 5). The CubXL runs DAL's "
               "copper corrosion screen spot by spot (DAL PR #180), with the volumes a real pipette moves; its "
               "capper's magnet holds one cap at a time, so a second cap waits on an empty parking vial. The multi-doser "
               "(chain carousel v5, an A&D HR-202i under its dose point) doses atomized powder for it by weight."],
         parts=[("mp4", "instruments/ot2_corrosion_prep.mp4", "The OT-2: electrolyte and ICP dilutions"),
                ("mp4", "instruments/cubxl_corrosion.mp4", "The CubXL's corrosion screen"),
                ("mp4", "vlm_workflow.mp4", "Atomized powder dosed for the CubXL")]),
    dict(key="alloy1", title="Alloy route 1/7: the charge cups, dosed, weighed and pressed under vacuum",
         card=["The atomizer melts the lab's own charge cups (#222), turned from 5N Al and oxygen-free Cu bar. Each "
               "is dosed by weight on the A&D HR-202i under the multi-doser's dose point (chain carousel v5, no funnel), "
               "and its vented plug pressed "
               "fully home under vacuum in a Specac Atlas Autotouch, compacting the powder to a set load."],
         parts=[("mp4", "dag/route_dag_ch1.mp4", "The route as a function network (DAL's ONR YIP DAG)"),
                ("still", "dal_workflow_table.png", 12.0, "DAL's alloy workflow, step by step (notes/dal_workflow.md): "
                 "the station each step uses here, and what is still missing", "DAL's 17 steps, and where each runs"),
                ("mp4", "alloy_charge.mp4", "The charge cups"),
                ("still", "doser_raise_section.png", 14.0, "Raise the balance on a block to shorten the fall? In v5 the "
                 "parked carriage is 12.6 mm over the HR-202i, so no block fits; the cup stays 153 mm under the exit, "
                 "and the option is each powder's own funnel on our shuttle (round 10)",
                 "Can the cup come closer to the exit?"),
                ("mp4", "vacuum_press.mp4", "The vacuum press with its catch ring")]),
    dict(key="alloy2", title="Alloy route 2/7: melt and atomize in the rePowder",
         card=["Both MiR250 + UR10e units go to the AMAZEMET rePowder, each with a 131 kg ballast plate low in its base: "
               "one holds the furnace's lid down while the other works its latch. A loading tool lowers each of the "
               "four Al cups into the crucible. Pump-downs with argon, induction melt, the pour, the ultrasonic spray, powder in the "
               "container. Cut with the lab's own footage, each piece badged with its alloy, date and source."],
         parts=[("mp4", "dag/route_dag_ch2.mp4", None), ("mp4", "alloy_atomize.mp4", None)]),
    dict(key="alloy3", title="Alloy route 3/7: sieve and print",
         card=["The arm runs a sieving cell on its own: it stacks the sieves, the Retsch AS 200 shakes them, a tipper "
               "empties each into its labelled jar, and a wash module cleans every sieve: shaken out, an ultrasonic IPA "
               "bath, a warm-air knife. The 20-63 um cut goes into the Aconity MIDI, which prints "
               "tensile bars."],
         parts=[("mp4", "dag/route_dag_ch3.mp4", None), ("mp4", "alloy_print.mp4", None)]),
    dict(key="alloy4", title="Alloy route 4/7: the powder, checked",
         card=["While the build prints, a retained sample of the sieved powder goes round the trays: laser "
               "diffraction for its size distribution, powder XRD after a proper sample prep, XRF for composition, "
               "and the SEM. The SEM images are the lab's own atomized Al 4047 (run c3k0n5, DAL #157)."],
         parts=[("mp4", "dag/route_dag_ch4.mp4", None), ("mp4", "alloy_powder.mp4", None)]),
    dict(key="alloy5", title="Alloy route 5/7: depowder, cut, heat treat, tensile at room and elevated temperature",
         card=["The build depowdered with its plate clamped in the box, flat and vertical bars cut off in one pass in the "
               "wire EDM and caught, rinsed in IPA, heat treated as "
               "tensile specimens, then pulled with automatic loading, at room temperature and in a hot chamber, seen in cutaway."],
         parts=[("mp4", "dag/route_dag_ch5.mp4", None), ("mp4", "alloy_workflow.mp4", None),
                ("gitstill", EDM, "vertical-lab/out/edm_orientations.png", 14.0, "Bars printed flat, vertical and at "
                 "45 deg, each cut off with the plate on edge from one fixture, each with its own catch (PR #328)",
                 "Three build orientations through the wire EDM (PR #328)")]),
    dict(key="alloy6", title="Alloy route 6/7: sample prep: section, mount, grind and polish",
         card=["Sections cut from the build, hot-mounted in conductive compound for the SEM, or set in a steel mount "
               "for indentation, then ground and polished with every disc change shown, the mounts standing free in the "
               "PX500's holder while its pistons press them down. Automated "
               "polishing is the hard part, and the chapter says where. Every move re-planned in round 10: the "
               "PX500's column behind the bowl, the gripper turned over the mold, 0 frames in collision."],
         parts=[("mp4", "dag/route_dag_ch6.mp4", None), ("mp4", "alloy_prep.mp4", None)]),
    dict(key="alloy7", title="Alloy route 7/7: characterizing the build",
         card=["The trays come to the opening in turn: the SEM with the mount clamped in its holder, the VHX, "
               "micro-Vickers, the nanoindenter and PIP on the steel-mounted slice. Each instrument's data is "
               "shown, and labelled real or illustrative."],
         parts=[("mp4", "dag/route_dag_ch7.mp4", None), ("mp4", "alloy_characterize.mp4", None)]),
    # Round 8: the XRD, Mastersizer, XRF and SEM work in chapter 4, the furnace, wire EDM and Instrons in chapter 5, the
    # mounting press, PX500 and Carvera in chapter 6, the SEM, VHX, HM-220, iMicro and PIP in chapter 7, the sieve shaker
    # in chapter 3. Their stand-alone tour clips are left out (Sterling, of the XRD: "why isn't a tray coming and then the
    # robot is putting something in there"); this chapter keeps the stations no chapter uses.
    dict(key="stations", title="The other stations: a tensile tester on its side, gloveboxes, fume hoods, stores, shipping",
         card=["Every instrument model at a glance, then the stations the alloy route doesn't pass through: a "
               "horizontal tensile tester for small bars, a glovebox on a tray and one on the floor, fume hoods (no HF), "
               "the sample store, the powder-jar store, and a packaging station that labels and seals powder for "
               "shipping."],
         parts=[("still", "instruments_gallery.png", 9.0, "Every instrument model: size, and on a tray or beside "
                 "the VLM", "Every instrument model"),
                ("mp4", "instruments/tensile_h.mp4", "A tensile tester on its side: zwickiLine Z5.0 TN"),
                ("mp4", "instruments/glovebox_tray.mp4", "A glovebox on a tray"),
                ("mp4", "instruments/glovebox.mp4", "The floor glovebox"),
                ("mp4", "instruments/fumehood.mp4", "Fume hoods: a ducted XStream, a ductless tray hood"),
                ("mp4", "instruments/fumehood_tray.mp4", None),
                ("mp4", "instruments/storage.mp4", "The sample store: cups, plugs, vials"),
                ("mp4", "instruments/powder_store_feed.mp4", "The powder-jar store: feedstock and atomized lots"),
                ("mp4", "instruments/powder_store_lots.mp4", None),
                ("mp4", "instruments/packaging.mp4", "Packaging")]),
    dict(key="fab", title="Fabrication: metal printers, DED, resin and PCB assembly",
         card=["Desktop LPBF, the Meltio M450 wire DED and the InssTek MX-Lab powder DED, Formlabs Form 4 with Wash "
               "and Cure, a stencil printer and the open-source LumenPnP pick-and-place."],
         parts=[("mp4", "fabrication_tour.mp4", "Metal, resin and PCB tools"),
                ("mp4", "instruments/ded.mp4", "InssTek MX-Lab DED")]),
    dict(key="scale", title="Scaling up: large-format printing and ship-part repair",
         card=["An alloy that passes the route goes to a large-format printer for real aerospace parts, and to a DED "
               "cell that rebuilds worn ship parts."],
         parts=[("mp4", "scaleup.mp4", None)]),
    dict(key="limits", title="What doesn't fit, and getting a tray out",
         card=["A hot isostatic press is too tall, too deep and too heavy for a tray. Taller bays would take more: "
               "Kardex's published 727.5 mm, our 996 mm opening, and Modula's 895 and 1,295 mm bays compared. A "
               "tray comes out for maintenance through the front opening, by Kardex's full tray extraction."],
         parts=[("mp4", "instruments/hip.mp4", "A HIP against a tray"),
                ("still", "tall_opening_bays.png", 14.0, "Which machines fit at each bay height, and their weight "
                 "against the tray's rating", "Taller bays: Kardex and Modula"),
                ("still", "maintenance_access.png", 10.0, "Getting a tray out for maintenance: the floor it needs in "
                 "front of the opening", "Getting a tray out for maintenance")]),
    dict(key="checks", title="How the models were checked",
         card=["Ten models fitted to frames of the real machines, the lab's own SOP videos among them. Every "
               "instrument's motion played through MuJoCo for interferences. Every frame of the arm's moves "
               "checked with FCL against itself, the MiR and everything visible, and planned round obstacles.",
               "Since round 11 the check is stricter: a part may touch where it is taken from or set down only up to "
               "1.5 mm deep, and everything else that moves (MiRs, trays, doors, the person, tables) is checked too."],
         parts=[("still", "register/before_after.jpg", 16.0, "Each row: a frame of the real machine, the model "
                 "before, the model after refitting", "Fitted to footage of the real machines"),
                ("gitstill", REPOWDER, "vertical-lab/out/repowder_refine/before_after.jpg", 18.0, "The rePowder "
                 "refitted to the lab's training videos: the lid and the chamber door hinge at the back; the latch, "
                 "bolt and swing-bolt clamps are joints (PR #327; chapter 2 still has the old lid)",
                 "The rePowder, refitted to the lab's videos (PR #327)"),
                ("still", "interference_sheet.png", 11.0, "MuJoCo interference check: what was left over after "
                 "the fixes", "MuJoCo interference check"),
                ("still", "collisions/vlm_workflow_before_after.png", 9.0, "The arm before and after the collision "
                 "check: straight joint moves through the MiR and the holder, then planned round them",
                 "Arm collisions, checked and planned round"),
                ("still", "collisions/round11_sheet.png", 12.0, "Round 11's stricter check, clip by clip: frames in "
                 "collision under the old rules and the new, before and after the fixes", "The stricter check, round 11")]),
    # Round 10: Sterling (2026-11-07), "maintenance over long-term and how that gets handled in workflows".
    dict(key="upkeep", title="Maintenance over the long term, inside the workflow",
         card=["Maintenance is booked into the same schedule as the work: calendar service, consumables by use, "
               "reference checks the arm runs between jobs with control charts, and failures repaired by a person "
               "or a vendor. A person's task holds a Shuttle's opening, so the arm moves to the other Shuttle.",
               "The arm's daily balance check with a reference weight, then a nanoindenter tip changed by a person "
               "with the tray pulled out on Kardex's extraction table, and a year of it booked."],
         parts=[("mp4", "upkeep_clip.mp4", None),
                ("still", "upkeep_year.png", 14.0, "A year of maintenance booked into the lab's schedule: hours by "
                 "who does it, and each station's availability (a model; notes/upkeep.md says what is assumed)",
                 "A year of maintenance, booked")]),
    dict(key="finale", title="The whole lab at speed: an hour, a day, a week, a month",
         card=["Everything at once, sped up: the trays cycling, the arm and the atomizer working, the printer "
               "building, then day by day, week by week and month by month, with what the lab has made and "
               "measured so far.",
               "Maintenance runs in the same schedule: the person and visiting vendors where their task is, a beacon "
               "on each machine (amber for upkeep, red while a fault waits), and the upkeep counters beside the rest."],
         parts=[("mp4", "timelapse.mp4", None)]),
]
OUTRO = ["Code, notes and every source: github.com/vertical-cloud-lab/byu-vcl, PR #318 (folder vertical-lab/).",
         "Sizes are the makers' published figures where they exist. The docks, fixtures, cells, the press's die and "
         "the camera mounts are our designs at assumed sizes, and each notes file says which numbers are assumed.",
         "Vertical Cloud Lab @ BYU, byu-vcl #303"]


# ===================================================================================================== helpers
def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def wrap(d: ImageDraw.ImageDraw, text: str, f, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if d.textlength(trial, font=f) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def stamp(t: float) -> str:
    t = int(t)
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def encode_frames(frames, path: Path, n: int):
    """Raw RGB frames (an iterator of HxWx3 uint8) to an H.264 MP4 at FPS."""
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                          f"{SIZE[0]}x{SIZE[1]}", "-r", str(FPS), "-i", "-", "-frames:v", str(n), "-c:v", "libx264",
                          *THREADS, "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-video_track_timescale", "15360",
                          str(path)], stdin=subprocess.PIPE)
    for fr in frames:
        p.stdin.write(np.ascontiguousarray(fr, dtype=np.uint8).tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError(f"ffmpeg failed on {path}")


def from_git(commit: str, path: str) -> Path | None:
    """A file as it is at `commit` (another branch's render), copied to /tmp; None if that commit isn't here."""
    dst = Path(tempfile.gettempdir()) / "longform_git" / f"{commit}_{path.replace('/', '_')}"
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True, cwd=HERE)
        if r.returncode:
            print(f"  not available: {commit}:{path} (git fetch origin first)", flush=True)
            return None
        dst.write_bytes(r.stdout)
    return dst


# ===================================================================================================== cards
def card_image(over: str, title: str, lines: list[str], foot: str | None = None) -> Image.Image:
    im = Image.new("RGB", SIZE, (246, 247, 249))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, SIZE[0], 10), fill=BLUE)
    x, w = 80, SIZE[0] - 160
    d.text((x, 120), over, font=font(28), fill=GREY)
    ft = font(54, bold=True)
    tl = wrap(d, title, ft, w)
    if len(tl) > 2:
        ft = font(44, bold=True)
        tl = wrap(d, title, ft, w)
    y = 165
    for ln in tl:
        d.text((x, y), ln, font=ft, fill=BLUE)
        y += int(ft.size * 1.22)
    y += 22
    fb = font(29)
    for para in lines:
        for ln in wrap(d, para, fb, w):
            if y > SIZE[1] - 110:
                break
            d.text((x, y), ln, font=fb, fill=INK)
            y += 40
        y += 14
    d.text((x, SIZE[1] - 70), foot or "Vertical Cloud Lab @ BYU, byu-vcl #303", font=font(22), fill=GREY)
    return im


def still_frames(src: Path, seconds: float, caption: str):
    """A figure under a caption band: letterboxed if it is wide, scrolled top to bottom if it is tall."""
    band = 86
    area = (SIZE[0], SIZE[1] - band)
    im = Image.open(src).convert("RGB")
    n = int(round(seconds * FPS))
    cap = Image.new("RGB", (SIZE[0], band), "white")
    d = ImageDraw.Draw(cap)
    d.line((0, 0, SIZE[0], 0), fill=BLUE, width=3)
    fb = font(25)
    for k, ln in enumerate(wrap(d, caption, fb, SIZE[0] - 60)[:2]):
        d.text((30, 12 + 34 * k), ln, font=fb, fill=INK)
    scale_fit = min(area[0] / im.width, area[1] / im.height)
    tall = im.height * (area[0] / im.width) > area[1] * 1.6
    if not tall:
        fit = im.resize((max(1, int(im.width * scale_fit)), max(1, int(im.height * scale_fit))), Image.LANCZOS)
        base = Image.new("RGB", SIZE, (246, 247, 249))
        base.paste(fit, ((area[0] - fit.width) // 2, (area[1] - fit.height) // 2))
        base.paste(cap, (0, area[1]))
        arr = np.asarray(base)
        for _ in range(n):
            yield arr
        return
    # tall: full width, scrolled, with a second's hold at each end
    wide = im.resize((area[0], int(im.height * area[0] / im.width)), Image.LANCZOS)
    travel = wide.height - area[1]
    hold = FPS
    for i in range(n):
        u = min(1.0, max(0.0, (i - hold) / max(1, n - 2 * hold)))
        u = u * u * (3 - 2 * u)
        y0 = int(round(u * travel))
        base = Image.new("RGB", SIZE, (246, 247, 249))
        base.paste(wide.crop((0, y0, area[0], y0 + area[1])), (0, 0))
        base.paste(cap, (0, area[1]))
        yield np.asarray(base)


def badge_png(text: str, caption: str, path: Path):
    """A transparent overlay: a red REAL FOOTAGE badge top left and a caption band at the bottom."""
    im = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fb = font(26, bold=True)
    tw = d.textlength(text, font=fb)
    d.rounded_rectangle((24, 22, 24 + tw + 32, 22 + 46), radius=8, fill=(200, 30, 30, 235))
    d.text((40, 30), text, font=fb, fill="white")
    fc = font(25)
    lines = wrap(d, caption, fc, SIZE[0] - 60)[:2]
    h = 24 + 34 * len(lines)
    d.rectangle((0, SIZE[1] - h, SIZE[0], SIZE[1]), fill=(255, 255, 255, 225))
    for k, ln in enumerate(lines):
        d.text((30, SIZE[1] - h + 12 + 34 * k), ln, font=fc, fill=INK)
    im.save(path)


CACHE = Path(tempfile.gettempdir()) / "longform_parts"     # normalised parts, keyed by their source's bytes


def cached(key_parts: list, make, dst: Path):
    """Run make(tmp) once per distinct input (sha256 of the source bytes and the settings), then copy to dst."""
    h = hashlib.sha256()
    for k in key_parts:
        if isinstance(k, Path):
            with open(k, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
        else:
            h.update(str(k).encode())
    CACHE.mkdir(parents=True, exist_ok=True)
    hit = CACHE / f"{h.hexdigest()[:20]}.mp4"
    if not hit.exists():
        tmp = hit.with_suffix(".part.mp4")
        make(tmp)
        tmp.rename(hit)
    dst.write_bytes(hit.read_bytes())


def normalise(src: Path, dst: Path, overlay: Path | None = None):
    vf = (f"scale={SIZE[0]}:{SIZE[1]}:force_original_aspect_ratio=decrease,"
          f"pad={SIZE[0]}:{SIZE[1]}:(ow-iw)/2:(oh-ih)/2:color=white,fps={FPS},setsar=1")
    if overlay is None:
        args = ["-i", src, "-vf", vf]
    else:
        args = ["-i", src, "-i", overlay, "-filter_complex", f"[0:v]{vf}[v];[v][1:v]overlay=0:0[o]", "-map", "[o]"]
    run("ffmpeg", "-y", "-loglevel", "error", *args, "-an", "-c:v", "libx264", *THREADS, "-preset", "medium",
        "-crf", "21", "-pix_fmt", "yuv420p", "-video_track_timescale", "15360", dst)


def warm(skip=()):
    """Normalise every clip the plan has into the cache, without joining: run while renders are still going, so the
    final build only encodes what changed (each part is keyed on its source's bytes). `skip`: substrings of the
    sources still to be re-rendered."""
    tmp = Path(tempfile.mkdtemp(prefix="longform_warm_"))
    n = 0
    for i, r in enumerate(plan()):
        if r.get("missing") or r["kind"] not in ("mp4", "footage"):
            continue
        if any(k in str(r.get("git") or r["src"]) for k in skip):
            continue
        out = tmp / f"w{i:03d}.mp4"
        if r["kind"] == "footage":
            ov = tmp / f"badge{i:03d}.png"
            badge_png("REAL FOOTAGE", r["caption"], ov)
            cached([r["src"], ov, SIZE, FPS, "footage"], lambda d, r=r, ov=ov: normalise(r["src"], d, ov), out)
        else:
            cached([r["src"], SIZE, FPS, "mp4"], lambda d, r=r: normalise(r["src"], d), out)
        out.unlink()
        n += 1
        print(f"  warm: {r.get('git') or r['src']}", flush=True)
    print(f"{n} parts in {CACHE}", flush=True)


# ===================================================================================================== DAL's steps
DAL_STEPS = [   # notes/dal_workflow.md, condensed: (step, station in the vertical lab, still missing)
    ("Pick a composition", "software: BO over a CALPHAD-screened space", ""),
    ("Weigh the charge", "multi-doser + A&D HR-202i on tray B; vacuum press", "cutting rod or wire to mass"),
    ("Coat the crucible (BN)", "by hand, under extraction", "stays manual: an aerosol job"),
    ("Atomize", "AMAZEMET rePowder, beside the VLM", "computer control of the rePowder"),
    ("Recover and sieve", "sieving cell beside the rePowder (Retsch AS 200)", ""),
    ("Store", "jars in the glovebox", "a dry cabinet on a tray"),
    ("Characterize the powder", "SEM, Mastersizer, XRF, VHX with LIBS", "SEM stub prep"),
    ("Ship powder out", "packaging station", "a dangerous-goods check per powder"),
    ("Print", "Aconity MIDI, DED, beside the VLM; depowdering box", ""),
    ("Cut parts off the plate", "FANUC ROBOCUT wire EDM", ""),
    ("Heat treat", "Nabertherm NAT 15/65, tray F", ""),
    ("Density (Archimedes)", "not modelled", "a balance with a density kit"),
    ("Metallography", "LECO PX500 on tray F; OpenFlexure array, VHX", "a mounting press"),
    ("Mechanical testing", "Instrons; PIP and iMicro on tray E", "a hardness tester"),
    ("Corrosion", "the CubXL set up for corrosion, tray A", ""),
    ("Long-term monitoring", "OpenFlexure array, stream cameras", ""),
    ("Records", "Pi 5 stream cameras on every tray; MongoDB", ""),
]


def dal_table(path: Path):
    """notes/dal_workflow.md's 17 steps as one table, 1920 x 951 (the still area at 1080p)."""
    W, H = 1920, 951
    im = Image.new("RGB", (W, H), (246, 247, 249))
    d = ImageDraw.Draw(im)
    fh, fb, fn = font(30, bold=True), font(27), font(27, bold=True)
    cols = [(40, "#"), (100, "Step (DAL, by hand today)"), (600, "Station in the vertical lab"),
            (1360, "Still missing")]
    y = 26
    d.text((40, y), "The alloy workflow, step by step: what DAL does by hand, and where it goes", font=font(36, True),
           fill=BLUE)
    y += 62
    for x, h in cols:
        d.text((x, y), h, font=fh, fill=GREY)
    y += 44
    d.line((40, y - 6, W - 40, y - 6), fill=BLUE, width=3)
    row_h = (H - y - 10) / len(DAL_STEPS)
    for i, (step, where, gap) in enumerate(DAL_STEPS):
        yy = int(y + i * row_h)
        if i % 2 == 0:
            d.rectangle((30, yy - 3, W - 30, int(yy + row_h) - 3), fill=(235, 238, 244))
        d.text((40, yy), f"{i + 1}", font=fn, fill=BLUE)
        d.text((100, yy), step, font=fb, fill=INK)
        d.text((600, yy), where, font=fb, fill=INK)
        d.text((1360, yy), gap or "-", font=fb, fill=(170, 60, 30) if gap else GREY)
    im.save(path, optimize=True)


# ===================================================================================================== the plan
def plan() -> list[dict]:
    """[{chapter, kind, src, seconds, label, missing}] for every part, cards included, in order."""
    if not (OUT / "dal_workflow_table.png").exists():
        dal_table(OUT / "dal_workflow_table.png")
    rows = []
    n = len(CHAPTERS)
    for ci, ch in enumerate(CHAPTERS, 1):
        rows.append(dict(chapter=ch["key"], kind="card", seconds=CARD_S, label=ch["title"], top=True,
                         over=f"Part {ci} of {n}" if ch["key"] != "intro" else "The vertical cloud lab, start to "
                                                                               "finish (3-D, PR #318)"))
        for part in ch["parts"]:
            kind = part[0]
            if kind == "mp4":
                # LONGFORM_SRC="a.mp4=/path/x.mp4,...": build from another copy of a clip (e.g. the committed one while
                # its re-render is still writing out/mp4/a.mp4)
                ovr = dict(kv.split("=", 1) for kv in os.environ.get("LONGFORM_SRC", "").split(",") if "=" in kv)
                src = Path(ovr[part[1]]) if part[1] in ovr else MP4 / part[1]
                rows.append(dict(chapter=ch["key"], kind=kind, src=src, seconds=duration(src) if src.exists() else 0,
                                 label=part[2], missing=not src.exists()))
            elif kind == "still":
                src = OUT / part[1]
                rows.append(dict(chapter=ch["key"], kind=kind, src=src, seconds=part[2], caption=part[3],
                                 label=part[4], missing=not src.exists()))
            elif kind == "gitmp4":
                src = from_git(part[1], part[2])
                rows.append(dict(chapter=ch["key"], kind="mp4", src=src, seconds=duration(src) if src else 0,
                                 label=part[3], missing=src is None, git=f"{part[1]}:{part[2]}"))
            elif kind == "gitstill":                    # a figure from a stacked PR's branch, at a pinned commit
                src = from_git(part[1], part[2])
                rows.append(dict(chapter=ch["key"], kind="still", src=src, seconds=part[3], caption=part[4],
                                 label=part[5], missing=src is None, git=f"{part[1]}:{part[2]}"))
            elif kind == "footage":
                src = OUT / part[1]
                rows.append(dict(chapter=ch["key"], kind=kind, src=src, seconds=duration(src) if src.exists() else 0,
                                 caption=part[2], label=part[3], missing=not src.exists()))
    rows.append(dict(chapter="outro", kind="outro", seconds=8.0, label=None))
    return rows


def chapters_from(rows: list[dict]) -> list[tuple[float, str]]:
    """The YouTube chapter lines the plan would give, from the parts' lengths before encoding."""
    marks, t = [], 0.0
    for r in rows:
        if r.get("missing"):
            continue
        if r["kind"] == "card":
            marks.append(dict(start_s=t, title=next(c for c in CHAPTERS if c["key"] == r["chapter"])["title"]))
        elif r.get("label"):
            marks.append(dict(start_s=t, title=r["label"]))
        t += r["seconds"]
    return youtube_chapters(marks, t)


def show_plan(rows):
    t = 0.0
    for r in rows:
        src = r.get("src")
        rel = r.get("git") or (src.relative_to(OUT) if src else "")
        flag = "  MISSING" if r.get("missing") else ""
        print(f"{stamp(t):>6} {r['seconds']:6.1f} s  {r['kind']:7s} {r['chapter']:9s} {rel}{flag}")
        if not r.get("missing"):
            t += r["seconds"]
    print(f"total {stamp(t)} ({t:.0f} s)")
    for t0, name in chapters_from(rows):
        print(f"  {stamp(t0)} {name}")


# ===================================================================================================== the join
def build():
    rows = plan()
    tmp = Path(tempfile.mkdtemp(prefix="longform_"))
    parts, t, record = [], 0.0, []
    n = len(CHAPTERS)
    for i, r in enumerate(rows):
        if r.get("missing"):
            print(f"  left out (not rendered): {r.get('git') or r['src']}", flush=True)
            continue
        out = tmp / f"p{i:03d}.mp4"
        if r["kind"] == "card":
            ch = next(c for c in CHAPTERS if c["key"] == r["chapter"])
            im = card_image(r["over"], ch["title"], ch["card"])
            arr = np.asarray(im)
            encode_frames((arr for _ in range(int(CARD_S * FPS))), out, int(CARD_S * FPS))
            im.save(tmp / f"card_{ch['key']}.png")
        elif r["kind"] == "outro":
            im = card_image("Thanks for watching", "The vertical cloud lab, start to finish", OUTRO[:2], OUTRO[2])
            arr = np.asarray(im)
            encode_frames((arr for _ in range(int(r["seconds"] * FPS))), out, int(r["seconds"] * FPS))
        elif r["kind"] == "still":
            nfr = int(round(r["seconds"] * FPS))
            encode_frames(still_frames(r["src"], r["seconds"], r["caption"]), out, nfr)
        elif r["kind"] == "footage":
            ov = tmp / f"badge{i:03d}.png"
            badge_png("REAL FOOTAGE", r["caption"], ov)
            cached([r["src"], ov, SIZE, FPS, "footage"], lambda d, r=r, ov=ov: normalise(r["src"], d, ov), out)
        else:
            cached([r["src"], SIZE, FPS, "mp4"], lambda d, r=r: normalise(r["src"], d), out)
        d = duration(out)
        src = r.get("git") or (str(r["src"].relative_to(HERE)) if r.get("src") else None)
        record.append(dict(chapter=r["chapter"], kind=r["kind"], start_s=round(t, 2), seconds=round(d, 2),
                           src=src, label=r.get("label")))
        t += d
        parts.append(out)
        print(f"{stamp(t):>6}  {r['kind']:7s} {src or ''}", flush=True)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    dst = MP4 / f"{NAME}.mp4"
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
        "-movflags", "+faststart", dst)
    total = duration(dst)
    # the chapter list from what was actually encoded
    marks = []
    for rr in record:
        if rr["kind"] == "card":
            ch = next(c for c in CHAPTERS if c["key"] == rr["chapter"])
            marks.append(dict(start_s=rr["start_s"], title=ch["title"]))
        elif rr.get("label"):
            marks.append(dict(start_s=rr["start_s"], title=rr["label"]))
    yt = youtube_chapters(marks, total)
    meta = dict(name=NAME, seconds=round(total, 1), fps=FPS, size=list(SIZE), card_seconds=CARD_S,
                built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), parts=record,
                youtube_chapters=[dict(start_s=s, stamp=stamp(s), title=nm) for s, nm in yt])
    (OUT / "longform.json").write_text(json.dumps(meta, indent=1) + "\n")
    sheet(record, dst, tmp)
    print(f"{NAME}: {stamp(total)} ({total:.1f} s), {dst.stat().st_size / 1e6:.1f} MB, {len(parts)} parts, "
          f"{len(yt)} chapters", flush=True)
    return meta


def youtube_chapters(marks: list[dict], total: float) -> list[tuple[float, str]]:
    """First at 0:00, each at least 10 s long (GAP keeps a margin): a mark too close after the one before it is
    dropped, so a chapter's card and its first labelled part share the card's line."""
    tops = {c["title"] for c in CHAPTERS}
    out: list[list] = []
    for m in marks:
        s, nm = m["start_s"], m["title"]
        if out and s - out[-1][0] < GAP:
            if nm in tops and out[-1][1] not in tops:
                out[-1][1] = nm                       # a chapter's own name outranks a part's
            elif nm in tops and len(out) == 1:
                out[-1][1] = nm                       # the opening is too short to be a chapter of its own
            continue
        out.append([s, nm])
    if out:
        out[0][0] = 0.0
    while len(out) > 1 and total - out[-1][0] < GAP:
        out.pop()
    return [(round(s, 1), nm) for s, nm in out]


def sheet(record, dst: Path, tmp: Path):
    """One frame from the middle of each chapter's first clip, 4 across, for the README and the PR."""
    picks = []
    seen = set()
    for rr in record:
        if rr["kind"] in ("mp4", "footage") and rr["chapter"] not in seen:
            seen.add(rr["chapter"])
            picks.append((rr["chapter"], rr["start_s"] + rr["seconds"] * 0.55))
    w, h, cols = 480, 270, 4
    rows_n = (len(picks) + cols - 1) // cols
    sh = Image.new("RGB", (w * cols, (h + 30) * rows_n), "white")
    d = ImageDraw.Draw(sh)
    for i, (key, t) in enumerate(picks):
        p = tmp / f"sheet_{key}.png"
        run("ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", dst, "-vframes", "1", p)
        x, y = (i % cols) * w, (i // cols) * (h + 30)
        sh.paste(Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS), (x, y))
        ch = next(c for c in CHAPTERS if c["key"] == key)
        d.text((x + 8, y + h + 5), f"{i + 1}. {ch['title']}"[:58], font=font(15, bold=True), fill=INK)
    sh.save(OUT / "longform_sheet.png", optimize=True)


# ===================================================================================================== YouTube
TITLE = "The vertical cloud lab, start to finish: a Kardex VLM, its instruments and the alloy route (3-D)"


def description(meta: dict, commit: str) -> str:
    head = ("Everything on PR #318 of the BYU Vertical Cloud Lab, in one video: a Kardex Shuttle XP 500 vertical lift "
            "module holding the lab's equipment on electrified trays, a UR10e on a MiR250 at its opening, the alloy "
            "route from charge cups to a tensile bar, every instrument doing its job, maintenance booked into the "
            "workflow, and the alternatives. 3-D "
            "animation built from makers' published figures and photos; real footage is badged as such.\n\n"
            f"Code, notes and sources: https://github.com/{REPO}/tree/{commit}/vertical-lab\n"
            f"PR: {PR}\n\n")
    chap = "Chapters\n" + "".join(f"{c['stamp']} {c['title']}\n" for c in meta["youtube_chapters"])
    tail = ("\nThe real VLM at the start: Sterling Baird, \"Vertical Lift Module in operation - from the sample's "
            "perspective\", https://www.youtube.com/watch?v=ck8QJhVqPiY . The atomizer footage in chapter 2 is the "
            "lab's own (DAL #159, #219).\n\nAssumed, not published: the docks, the fixtures and cells, the press's "
            "die, the camera mounts and several electrical ratings; each notes file in vertical-lab/notes says "
            "which numbers are which.")
    s = head + chap + tail
    while len(s.encode()) > 4900:
        tail = tail[: max(0, len(tail) - 200)]
        s = head + chap + tail
    return s


def upload(meta: dict) -> str:
    sys.path.insert(0, str(HERE.parent))
    import youtube_upload as Y
    from googleapiclient.http import MediaFileUpload
    from youtube.yt_service import get_youtube_service

    dst = MP4 / f"{NAME}.mp4"
    rec = Y.load_record()
    digest = Y.sha256(dst)
    for v in rec["videos"].get(f"{NAME}.mp4", []):
        if v["sha256"] == digest:
            print(f"already up: https://www.youtube.com/watch?v={v['id']}")
            return v["id"]
    commit = subprocess.run(["git", "log", "-1", "--format=%h", "--", str(dst)], capture_output=True, text=True,
                            cwd=HERE).stdout.strip() or subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                                                                       capture_output=True, text=True,
                                                                       cwd=HERE).stdout.strip()
    yt = get_youtube_service("upload")
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    if me != Y.CHANNEL:
        raise SystemExit(f"the token is for channel {me}, not {Y.CHANNEL}")
    body = {"snippet": {"title": TITLE[:100], "description": description(meta, commit), "tags": Y.TAGS,
                        "categoryId": "28", "defaultLanguage": "en"},
            "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False, "embeddable": True}}
    media = MediaFileUpload(str(dst), mimetype="video/mp4", chunksize=16 << 20, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=False)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploaded {status.progress():.0%}", flush=True)
    vid = resp["id"]
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec["videos"].setdefault(f"{NAME}.mp4", []).append(dict(id=vid, sha256=digest, bytes=dst.stat().st_size,
                                                             commit=commit, uploaded=now, title=TITLE[:100],
                                                             privacy="unlisted"))
    Y.save_record(rec)
    (OUT / "longform_youtube.txt").write_text(description(meta, commit) + "\n")
    print(f"https://www.youtube.com/watch?v={vid}")
    return vid


def readme_table(meta: dict) -> str:
    """The chapters as a markdown table: number, title, start, and the parts with links (a part from another branch
    named with its commit)."""
    rows = ["| # | Starts | Chapter | Parts |", "|---|---|---|---|"]
    n = 0
    for ch in CHAPTERS:
        parts = [r for r in meta["parts"] if r["chapter"] == ch["key"]]
        if not parts:
            continue
        n += 1
        start = parts[0]["start_s"]
        links = []
        for r in parts:
            src = r.get("src")
            if not src or r["kind"] == "card":
                continue
            if ":" in src:
                commit, path = src.split(":", 1)
                links.append(f"[`{Path(path).name}`](https://github.com/{REPO}/blob/{commit}/{path}) ({commit})")
            else:
                links.append(f"[`{Path(src).name}`]({src})")
        rows.append(f"| {n} | {stamp(start)} | {ch['title']} | {', '.join(links)} |")
    return "\n".join(rows)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "plan":
        show_plan(plan())
    elif args and args[0] == "readme":
        print(readme_table(json.loads((OUT / "longform.json").read_text())))
    elif args and args[0] == "upload":
        upload(json.loads((OUT / "longform.json").read_text()))
    elif args and args[0] == "warm":                  # normalise the clips into the cache ahead of the build
        warm(args[1:])
    elif args and args[0] == "cards":                 # the cards alone, to /tmp, to read them
        for i, ch in enumerate(CHAPTERS, 1):
            card_image(f"Part {i} of {len(CHAPTERS)}", ch["title"], ch["card"]).save(f"/tmp/card_{ch['key']}.png")
        print("cards in /tmp/card_*.png")
    else:
        build()
