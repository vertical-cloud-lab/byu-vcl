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
CARD_S = 4.0
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


# ===================================================================================================== the chapters
# Each chapter: a key, its title (also the YouTube chapter line), the card's lines, and its parts in order. A part is
#   ("mp4", rel under out/mp4, label or None)                    a rendered clip, whole
#   ("still", rel under out, seconds, caption, label or None)    a figure, letterboxed, or scrolled if it is tall
#   ("footage", rel under out, caption, label or None)           real video, with a REAL FOOTAGE badge and a credit
# A label starts a YouTube chapter of its own inside the chapter (merged into the next if it would be under 10 s).
CHAPTERS = [
    dict(key="intro", title="A real VLM, then the plan",
         card=["A Kardex vertical lift module (VLM) holds the lab's equipment on electrified trays. A UR10e on a MiR250 "
               "mobile base works at its opening, and the machines too big for a tray stand beside it.",
               "Everything after the first clip is a 3-D animation, built from the makers' published figures and "
               "photos and checked for collisions. Real footage and photos are badged as such."],
         parts=[("footage", "footage/vlm_real_ck8QJhVqPiY.mp4",
                 "A real VLM in operation, from the sample's perspective (Sterling Baird, youtu.be/ck8QJhVqPiY)",
                 None)]),
    dict(key="setup", title="The lab set up from scratch",
         card=["An empty bay: the layout taped out, utilities and cable trays overhead, the Kardex Shuttle XP 500 "
               "going up, the floor machines, two UR10e arms assembled onto MiR250 bases, then trays A-F loaded by "
               "people and the stream cameras fitted."],
         parts=[("mp4", "setup_lab.mp4", None)]),
    dict(key="trays", title="What the trays carry, and the line beside the VLM",
         card=["Trays D, E and F: microscopy and diffraction (the SEM, the XRD and six OpenFlexures on one sub-tray), "
               "mechanical testing and particle size, sample prep and heat treatment.",
               "What doesn't fit through the 727.5 mm opening stands in a line with the VLM, along a backup rail. "
               "Then trays G, H and I: resin printing, PCB assembly and desktop LPBF."],
         parts=[("mp4", "vlm_line.mp4", "Trays D-F and the line along the rail"),
                ("mp4", "vlm_fab_trays.mp4", "Trays G-I: resin, PCB, desktop LPBF")]),
    dict(key="services", title="Services to every tray: docking, UPS, tether, cabling, cameras",
         card=["One automatic coupling per tray (Staubli CombiTac: mains, Ethernet, air, N2, chilled water), docked "
               "in its slot and again at the opening, with a UPS for the seconds in transit. The alternative is a "
               "retractable tether. Then the cabling, and the stream cameras: a Pi 5 with an HQ Camera and a "
               "Camera Module 3 Wide, two or three per tray and one over the bay."],
         parts=[("mp4", "vlm_services.mp4", "Docking couplings and the UPS"),
                ("mp4", "vlm_tether.mp4", "A retractable tether instead"),
                ("mp4", "vlm_cabling.mp4", "Cabling"),
                ("mp4", "instruments/tray_dock.mp4", "The tray dock, close up"),
                ("mp4", "instruments/stream_cam.mp4", "The stream camera unit: height, pan, tilt")]),
    dict(key="alloy1", title="Alloy route 1/4: the charge cups, dosed, weighed and pressed under vacuum",
         card=["The atomizer melts the lab's own charge cups (#222), turned from 5N Al and oxygen-free Cu bar. Each "
               "is dosed through its powder's own funnel, weighed on an A&D HR-202i, and its vented plug pressed "
               "fully home under vacuum in a Specac Atlas Autotouch, compacting the powder to a set load."],
         parts=[("mp4", "alloy_charge.mp4", None)]),
    dict(key="alloy2", title="Alloy route 2/4: melt and atomize in the rePowder",
         card=["The MiR250 takes the four Al cups to the AMAZEMET rePowder: pump-downs with argon, induction melt, "
               "the pour, the ultrasonic spray, powder in the container. Cut with the lab's own footage of its "
               "bronze and Al runs, each badged with its alloy, date and source."],
         parts=[("mp4", "alloy_atomize.mp4", None)]),
    dict(key="alloy3", title="Alloy route 3/4: sieve and print",
         card=["The arm runs a sieving cell on its own: it stacks the sieves, the Retsch AS 200 shakes them, a tipper "
               "empties each into its labelled jar. The 20-63 um cut goes into the Aconity MIDI, which prints "
               "tensile bars."],
         parts=[("mp4", "alloy_print.mp4", None)]),
    dict(key="alloy4", title="Alloy route 4/4: depowder, cut and test",
         card=["The build vacuumed with a lance, the plate depowdered in a turning, shaking box under argon, the "
               "bars cut off in the FANUC ROBOCUT wire EDM, one rinsed and dried, and pulled in the Instron "
               "68FM-100."],
         parts=[("mp4", "alloy_workflow.mp4", None)]),
    dict(key="charact", title="Characterization instruments, one by one",
         card=["Each modelled from its maker's published figures and photos, with its moving pieces, doing its job. "
               "Ten were refitted against footage of the real machine."],
         parts=[("still", "instruments_gallery.png", 9.0, "Every instrument model: size, and on a tray or beside "
                 "the VLM", None),
                ("mp4", "instruments/xrd.mp4", "XRD (Rigaku MiniFlex) and SEM (Hitachi TM4000PlusII)"),
                ("mp4", "instruments/sem.mp4", None),
                ("mp4", "instruments/vhx.mp4", "Keyence VHX-7000 with the EA-300 LIBS head"),
                ("mp4", "instruments/xrf.mp4", "Benchtop XRF: Bruker S2 PUMA"),
                ("mp4", "instruments/openflexure_v7.mp4", "OpenFlexure v7 and Delta Stage"),
                ("mp4", "instruments/openflexure_delta.mp4", None),
                ("mp4", "instruments/openflexure_array.mp4", "Six OpenFlexures on one sub-tray"),
                ("mp4", "instruments/mastersizer.mp4", "Malvern Mastersizer 3000 + Aero S"),
                ("mp4", "instruments/nanoindenter.mp4", "KLA iMicro nanoindenter"),
                ("mp4", "instruments/pip.mp4", "Plastometrex PLX-Benchtop (PIP)"),
                ("mp4", "instruments/cubxl_corrosion.mp4", "The CubXL set up for corrosion")]),
    dict(key="prep", title="Sample prep, testing, powder handling and shipping",
         card=["The LECO PX500 grinder-polisher, the Nabertherm furnace, two Instrons and the wire EDM; the sieve "
               "shaker, an inert glovebox, and a packaging station that labels and seals powder for shipping."],
         parts=[("mp4", "instruments/polisher.mp4", "LECO PX500 grinder-polisher"),
                ("mp4", "instruments/furnace.mp4", "Nabertherm furnace and the two Instrons"),
                ("mp4", "instruments/instron_small.mp4", None),
                ("mp4", "instruments/instron_floor.mp4", None),
                ("mp4", "instruments/wire_edm.mp4", "FANUC ROBOCUT wire EDM"),
                ("mp4", "instruments/sieve.mp4", "Sieve shaker: Retsch AS 200"),
                ("mp4", "instruments/glovebox.mp4", "Inert glovebox and the packaging station"),
                ("mp4", "instruments/packaging.mp4", None)]),
    dict(key="fab", title="Fabrication: metal printers, DED, resin and PCB assembly",
         card=["Desktop LPBF (the SnowPod fits the opening; the MPRINT and MetalONE don't), the Meltio M450 wire DED "
               "and the InssTek MX-Lab powder DED beside the VLM, Formlabs Form 4 with Wash and Cure, a stencil "
               "printer and the open-source LumenPnP pick-and-place."],
         parts=[("mp4", "fabrication_tour.mp4", "Metal, resin and PCB tools"),
                ("mp4", "instruments/ded.mp4", "InssTek MX-Lab DED")]),
    dict(key="alt", title="The alternatives: a floor rail, or a warehouse with mobile manipulators",
         card=["The backup to the mobile base is a Vention seventh axis along the fronts. The other way is a "
               "warehouse floor: the VLM and the floor machines facing one aisle, served by MiR250 + UR10e units "
               "that dock with a target the arm checks at every station."],
         parts=[("mp4", "instruments/rail.mp4", None),
                ("still", "rail_vs_amr.png", 9.0, "Rail or mobile base: pedestal sway, docking accuracy, tipping",
                 None),
                ("mp4", "warehouse.mp4", "The warehouse version")]),
    dict(key="limits", title="What doesn't fit, and what it would take",
         card=["A hot isostatic press is too tall, too deep and too heavy for a tray. A taller opening, about "
               "1000 mm, would take the MX-Lab and most desktop LPBF machines, but Kardex publishes no figure. And "
               "with the rail in front, a tray comes out for maintenance only through a second opening at the back."],
         parts=[("mp4", "instruments/hip.mp4", "A HIP against a tray"),
                ("mp4", "vlm_tall_opening.mp4", "A taller opening"),
                ("still", "maintenance_access.png", 12.0, "Getting a tray out for maintenance with the rail in front: "
                 "the floor it needs (hatched), and a rear service opening", "Getting a tray out for maintenance")]),
    dict(key="checks", title="How the models were checked",
         card=["Ten models fitted to frames of the real machines, the lab's own SOP videos among them. Every "
               "instrument's motion played through MuJoCo for interferences. Every frame of the arm's moves "
               "checked with FCL against itself, the MiR and everything visible, and planned round obstacles."],
         parts=[("still", "register/before_after.jpg", 16.0, "Each row: a frame of the real machine, the model "
                 "before, the model after refitting", "Fitted to footage of the real machines"),
                ("still", "interference_sheet.png", 11.0, "MuJoCo interference check: what was left over after "
                 "the fixes", "MuJoCo interference check"),
                ("still", "collisions/vlm_workflow_before_after.png", 9.0, "The arm before and after the collision "
                 "check: straight joint moves through the MiR and the holder, then planned round them",
                 "Arm collisions, checked and planned round")]),
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
                          "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-video_track_timescale", "15360",
                          str(path)], stdin=subprocess.PIPE)
    for fr in frames:
        p.stdin.write(np.ascontiguousarray(fr, dtype=np.uint8).tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError(f"ffmpeg failed on {path}")


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


def normalise(src: Path, dst: Path, overlay: Path | None = None):
    vf = (f"scale={SIZE[0]}:{SIZE[1]}:force_original_aspect_ratio=decrease,"
          f"pad={SIZE[0]}:{SIZE[1]}:(ow-iw)/2:(oh-ih)/2:color=white,fps={FPS},setsar=1")
    if overlay is None:
        args = ["-i", src, "-vf", vf]
    else:
        args = ["-i", src, "-i", overlay, "-filter_complex", f"[0:v]{vf}[v];[v][1:v]overlay=0:0[o]", "-map", "[o]"]
    run("ffmpeg", "-y", "-loglevel", "error", *args, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-pix_fmt", "yuv420p", "-video_track_timescale", "15360", dst)


# ===================================================================================================== the plan
def plan() -> list[dict]:
    """[{chapter, kind, src, seconds, label, missing}] for every part, cards included, in order."""
    rows = []
    n = len(CHAPTERS)
    for ci, ch in enumerate(CHAPTERS, 1):
        rows.append(dict(chapter=ch["key"], kind="card", seconds=CARD_S, label=ch["title"], top=True,
                         over=f"Part {ci} of {n}" if ch["key"] != "intro" else "The vertical cloud lab, start to "
                                                                               "finish (3-D, PR #318)"))
        for part in ch["parts"]:
            kind = part[0]
            if kind == "mp4":
                src = MP4 / part[1]
                rows.append(dict(chapter=ch["key"], kind=kind, src=src, seconds=duration(src) if src.exists() else 0,
                                 label=part[2], missing=not src.exists()))
            elif kind == "still":
                src = OUT / part[1]
                rows.append(dict(chapter=ch["key"], kind=kind, src=src, seconds=part[2], caption=part[3],
                                 label=part[4], missing=not src.exists()))
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
        rel = src.relative_to(OUT) if src else ""
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
            print(f"  left out (not rendered): {r['src'].relative_to(OUT)}", flush=True)
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
            normalise(r["src"], out, ov)
        else:
            normalise(r["src"], out)
        d = duration(out)
        record.append(dict(chapter=r["chapter"], kind=r["kind"], start_s=round(t, 2), seconds=round(d, 2),
                           src=str(r["src"].relative_to(HERE)) if r.get("src") else None, label=r.get("label")))
        t += d
        parts.append(out)
        print(f"{stamp(t):>6}  {r['kind']:7s} {r.get('src', '') and r['src'].name}", flush=True)
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
            "route from charge cups to a tensile bar, every instrument doing its job, and the alternatives. 3-D "
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


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "plan":
        show_plan(plan())
    elif args and args[0] == "upload":
        upload(json.loads((OUT / "longform.json").read_text()))
    elif args and args[0] == "cards":                 # the cards alone, to /tmp, to read them
        for i, ch in enumerate(CHAPTERS, 1):
            card_image(f"Part {i} of {len(CHAPTERS)}", ch["title"], ch["card"]).save(f"/tmp/card_{ch['key']}.png")
        print("cards in /tmp/card_*.png")
    else:
        build()
