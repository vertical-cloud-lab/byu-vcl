"""Put the vertical-lab videos on the lab's YouTube channel, and keep track of which version of each file is up (#303).

``out/youtube.json`` lists every upload with the sha256 of the file it was made from. A file under ``out/mp4/`` whose
current bytes aren't in that list hasn't been uploaded, or was re-rendered after it was. ``upload`` puts those up,
unlisted, with a title and a description built from the clip's own JSON: what the model is and where its figures
come from, then the clip's steps with timestamps (a joined video gets one timestamp per part). Each description
links the file and the code at the commit the file came from.

    python3 youtube_upload.py plan               # what would go up, and with what title
    python3 youtube_upload.py upload [rel ...]   # upload, recording each one in out/youtube.json as it lands
    python3 youtube_upload.py table              # out/youtube.md: every MP4 and its video

Needs ``YOUTUBE_UPLOAD_TOKEN_PICKLE_B64`` (upload and read only; see ``youtube/README.md``). That token can't delete
or edit a video, so an older render stays up until a ``@claude-youtube`` run removes it; ``out/youtube.json`` marks
those as superseded.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "out"
MP4 = OUT / "mp4"
RECORD = OUT / "youtube.json"
TABLE = OUT / "youtube.md"
REPO = "vertical-cloud-lab/byu-vcl"
PR = f"https://github.com/{REPO}/pull/318"
CHANNEL = "UCKC7WzMu6QEh7O55zZlT2lw"
TAGS = ["vertical cloud lab", "BYU", "self-driving lab", "laboratory automation", "vertical lift module",
        "Kardex Shuttle", "UR10e", "3-D animation", "alloy development"]
DESC_BYTES = 4900            # YouTube's limit is 5000 bytes
TITLE_CHARS = 100

# The joined videos and the clips they are made of, in order. The tours are plain concatenations of their parts'
# MP4s (tour.join, fab_tour.join, animate.py's full join), so each part starts where the previous one ends;
# ``chapters`` checks that the parts add up to the joined file before it writes any timestamp.
ROUND4 = ["vhx", "xrf", "sieve", "openflexure_array", "cubxl_corrosion", "ded", "packaging", "hip", "tray_dock",
          "stream_cam"]
JOINED = {
    "vertical_lab_full.mp4": ["vlm_assembly.mp4", "vlm_loading.mp4", "vlm_workflow.mp4"],
    "vlm_services_all.mp4": ["vlm_services.mp4", "vlm_hookups.mp4", "bay_camera.mp4", "vlm_cabling.mp4"],
    "instruments_round4_tour.mp4": [f"instruments/{k}.mp4" for k in ROUND4],
}

# Titles and a first line for the clips that aren't one instrument each. The steps under the first line come from
# the clip's JSON, so they follow the render; these lines only say what the clip is and where it belongs.
LAB = {
    "vertical_lab_full.mp4": ("Vertical cloud lab: the VLM assembled, loaded and at work (round 1, ends loaded)",
                              "The Kardex Shuttle XP 500 assembled, the lab's equipment loaded onto its trays through "
                              "the opening, and a UR10e on a MiR250 dosing a powder and taking the vial to the CubXL."),
    "vlm_assembly.mp4": ("Vertical cloud lab: the Kardex Shuttle XP 500 VLM going together (3-D animation)",
                         "Chapter 1 of the round-1 animation: the vertical lift module goes together, then the "
                         "cladding goes on."),
    "vlm_loading.mp4": ("Vertical cloud lab: the equipment going onto the VLM's trays (3-D animation)",
                        "Chapter 2 of the round-1 animation: the closed machine turns see-through, and each piece "
                        "of equipment goes onto its tray through the opening, one at a time."),
    "vlm_workflow.mp4": ("Vertical cloud lab: dose a powder, then add liquid in the CubXL (3-D animation)",
                         "Chapter 3 of the round-1 animation: a UR10e on a MiR250 takes a vial to the multi-doser, "
                         "the VLM swaps trays, and the CubXL adds the liquid."),
    "vlm_disassembly.mp4": ("Vertical cloud lab: the VLM unloaded and taken apart (3-D animation)",
                            "The round-1 animation's old last chapter, now a clip of its own: unloaded one piece at "
                            "a time, then taken apart."),
    "vlm_line.mp4": ("Vertical cloud lab: trays D-F and the alloy line along a backup rail (3-D animation)",
                     "Round 3: three more trays, and what doesn't fit through the opening standing in a line with "
                     "the VLM, fronts aligned, along a Vention rail carrying the UR10e."),
    "vlm_fab_trays.mp4": ("Vertical cloud lab: trays G (resin), H (PCB) and I (two SnowPods) on the Kardex Shuttle",
                          "Trays G, H and I, and the metal printers that don't fit through the opening, stood "
                          "against its height."),
    "vlm_services.mp4": ("Vertical cloud lab: one docking coupling per tray, in its slot and at the opening",
                         "Round 4: every service a tray needs (mains, Ethernet, air, N2, chilled water) through one "
                         "automatic coupling, docked in its slot and again at the opening, with a UPS for transit."),
    "vlm_hookups.mp4": ("Vertical cloud lab: one tray's automatic hookups and its UPS, slot to bay (3-D animation)",
                        "One tray followed from its storage slot to the opening: the dock's mains, Ethernet, air, N2 "
                        "and chilled water live in the slot, shut and vented before it lets go, the tray on its own "
                        "UPS in transit, and the bay's dock taking over."),
    "bay_camera.mp4": ("Vertical cloud lab: the overhead camera at the bay, and what it sees (3-D animation)",
                       "The bay's overhead camera from an operator's eye height in front of the opening, then its own "
                       "two pictures, the Camera Module 3 Wide's and the HQ Camera's with the 16 mm lens, while the "
                       "arm works on a presented tray."),
    "vlm_cabling.mp4": ("Vertical cloud lab: the cabling, an overhead ladder tray with drops (3-D animation)",
                        "Round 4: the lab's wired power and network, in one overhead ladder tray behind the line and "
                        "round the VLM, with drops and risers."),
    "vlm_services_all.mp4": ("Vertical cloud lab: tray docking couplings, each tray's UPS, the bay camera, the "
                             "cabling (3-D)",
                             "The tray services, joined: the docking coupling, one tray's hookups and UPS from slot to "
                             "bay, the bay's overhead camera and what it sees, and the cabling."),
    "vlm_tall_opening.mp4": ("Vertical cloud lab: what a taller Kardex opening, about 1000 mm, would put on a tray",
                             "Round 5: the 727.5 mm product height Kardex publishes for the opening, against about "
                             "1000 mm, and which machines a taller opening would let onto a tray."),
    "warehouse.mp4": ("Vertical cloud lab, warehouse version: two MiR250 + UR10e units on an open floor",
                      "The vertical cloud lab laid out on a warehouse floor, with two MiR250 + UR10e units driving "
                      "between the VLM and the floor machines."),
    "setup_lab.mp4": ("Vertical cloud lab, set up from scratch: VLM, floor machines, arms, every tray loaded",
                      "The whole vertical cloud lab set up in an empty warehouse bay, from the tape on the floor to "
                      "every tray loaded and the cameras in place."),
    "alloy_charge_vacuum.mp4": ("Vertical cloud lab, alloy route 1/4: charge cups pressed home in a vacuum press (3-D)",
                                "Chapter 1 of the alloy route with a vacuum press (alloy_charge.py, PR #318 review): each "
                                "cup's bore filled to the plug (Si, then AlSi10Mg; Ni, then Cu), the plug pressed home at "
                                "3.2 t under vacuum in a Specac Atlas Autotouch 15T with the lab's evacuable die round F1, "
                                "and every arm move collision-checked (collide.py)."),
    "alloy_charge.mp4": ("Vertical cloud lab, alloy route 1/4: charge cups dosed, weighed, and pressed under vacuum",
                         "Chapter 1 of the alloy route (alloy_charge.py): four 5N Al and four OFE Cu cups, each dosed "
                         "through its powder's own funnel, weighed on an A&D HR-202i, topped up to the plug line, then "
                         "plugged and pressed home at 3.2 t under vacuum in a Specac Atlas Autotouch 15T, on tray B of "
                         "the VLM. Every frame of the arm's moves collision-checked (collide.py)."),
    "alloy_atomize.mp4": ("Vertical cloud lab, alloy route 2/5: melt and atomize in the rePowder (3-D animation)",
                          "Chapter 2 of the alloy route: the charged cups into the AMAZEMET rePowder's crucible, "
                          "induction melting under argon, ultrasonic atomization."),
    "alloy_print.mp4": ("Vertical cloud lab, alloy route 3/4: the arm runs a sieving cell, then the print (3-D animation)",
                        "Chapter 3 of the alloy route: the arm builds the sieve stack, runs the shaker and tips each "
                        "cut into a labelled jar, and the LPBF cut goes into the Aconity MIDI. Rendered before the "
                        "arm's collision check: in some frames the arm passes through the sieves and the Aconity's "
                        "cabinet (notes/arm_collisions.md)."),
    "alloy_workflow.mp4": ("Vertical cloud lab, alloy route 4/4: depowder, wire EDM, rinse, tensile test (3-D animation)",
                           "Chapter 4 of the alloy route: the build vacuumed with a suction lance and shaken clean in "
                           "a depowdering box, the bars cut off in a FANUC wire EDM, one rinsed, dried and pulled to "
                           "fracture in an Instron 68FM-100. Rendered before the arm's collision check: in some "
                           "frames the arm passes through the lance's hose, the Aconity and the shaker box "
                           "(notes/arm_collisions.md)."),
    "alloy_route.mp4": ("Vertical cloud lab: the alloy route, start to finish (charge cups to tensile bar)",
                        "The alloy route of the Vertical Cloud Lab at BYU, start to finish, in four chapters."),
    "instruments_tour.mp4": ("Vertical cloud lab: every instrument at work, one after another (3-D animation)",
                             "Every instrument model of the vertical cloud lab, each doing its job, one after "
                             "another."),
    "instruments_round4_tour.mp4": ("Vertical cloud lab: VHX + LIBS, XRF, sieving, OpenFlexure array, corrosion, "
                                    "DED, packaging, HIP",
                                    "Round 4's instruments, each doing its job."),
    "fabrication_tour.mp4": ("Vertical cloud lab: compact metal printers, resin printing and PCB assembly "
                             "(3-D animation)",
                             "The fabrication tools, each doing its job."),
    'alloy_characterize.mp4': ('Vertical cloud lab, alloy route 5/5: the trays at work, characterizing the build (3-D)',
        "Chapter 5 of the alloy route (alloy_characterize.py, PR #318 round 7): samples of the printed AlSi10Mg build go through the characterization trays at the VLM's opening. A coupon is ground and polished on the LECO PX500 (tray F), imaged in the Hitachi TM4000PlusII (tray D) and indented in the KLA iMicro (tray E); its powder goes through the Malvern Mastersizer 3000 (tray E). Every arm move collision-checked: 0 frames in collision."),
    'vacuum_press.mp4': ('Vertical cloud lab: the Specac Autotouch vacuum press, with a catch ring in the die (3-D)',
        "The plug press of the alloy route (vacuum_press.py, PR #318 round 7): the cup now stands in a hardened catch ring in the die's mouth when the ejector raises it, so it can't topple while the arm sets it and lifts it off."),
    'vlm_workflow.mp4': ("Vertical cloud lab: atomized powder dosed for the CubXL's powder test (3-D animation)",
        "Round 2's workflow, re-scripted (PR #318 round 7): the multi-doser doses 25 mg of atomized AlSi10Mg for DAL's powder reactivity test, and the CubXL's P20 adds 200 uL of seawater in 10 transfers. No salt is dosed. Every arm move collision-checked."),
    'instruments/cnc.mp4': ('Vertical cloud lab: a Makera Carvera CNC with a tool changer, for a tray (3-D animation)',
        "A compact CNC mill with an automatic tool changer for the vertical cloud lab (instruments_r7.py), with an added lid actuator and pneumatic vise. Sizes from Makera's published figures; the actuator and vise are our design."),
    'instruments/fumehood.mp4': ('Vertical cloud lab: a ducted fume hood, Labconco Protector XStream 4 ft (3-D animation)',
        "A ducted floor fume hood the mobile arm serves through its sash, for etching (Keller's reagent) and wet chemistry (instruments_r7.py)."),
    'instruments/fumehood_tray.mp4': ('Vertical cloud lab: a ductless fume hood on a VLM tray, Sentry Air 24 in (3-D)',
        'A ductless benchtop hood with its blower, sized for a tray of the VLM (instruments_r7.py). Not for HF: its air returns into the VLM.'),
    'instruments/glovebox_tray.mp4': ('Vertical cloud lab: a purge-only N2 glovebox on a VLM tray (3-D animation)',
        "A custom inert glovebox that fits a tray of the VLM with its UPS and dock (instruments_r7.py): glove ports at the front, a 150 mm mini antechamber the arm loads, N2 purge through the tray's dock."),
    'instruments/hardness.mp4': ('Vertical cloud lab: Mitutoyo HM-220 automatic micro-Vickers hardness tester (3-D)',
        'An automatic micro-Vickers hardness tester on a tray (instruments_r7.py): an indent series and its measurement.'),
    'instruments/ot2_corrosion_prep.mp4': ("Vertical cloud lab: the OT-2 making the CubXL's stocks and ICP-MS dilutions (3-D)",
        "The Opentrons OT-2 as tray A's liquid station for the corrosion screen (digital-wetlab PR #83, direction 5): it makes the CubXL's 0.1 mg/L sulfide stock and dilutes the ICP-MS tubes, at real P300 and P20 volumes."),
    'instruments/storage.mp4': ('Vertical cloud lab: the sample store tray, Al and Cu cups and plugs, vials, tubes (3-D)',
        'The sample store on its own tray (instruments_r7.py): racks of machined Al and Cu charge cups and plugs, 20 mL vials, ICP-MS tubes, SEM stubs, mounts, tensile bars and powder jars, every pocket listed for the arm.'),
    'instruments/tensile_h.mp4': ('Vertical cloud lab: a tensile tester on its side on a tray, zwickiLine Z5.0 TN (3-D)',
        "A 5 kN ZwickRoell zwickiLine run horizontally on a tray (instruments_r7.py): a pull to break on a bar faced to 6 x 1.5 mm. The route's 6 x 6 mm bar (14.8 kN) stays on the Instron 68FM-100."),
    'dag/route_dag_ch1.mp4': ('Vertical cloud lab: the alloy route as a function network, stage 1 of 5',
        "DAL's ONR YIP function network (network_dag.py), brought in one stage at a time before chapter 1 of the alloy route (route_dag.py, PR #318)."),
    'dag/route_dag_ch2.mp4': ('Vertical cloud lab: the alloy route as a function network, stage 2 of 5',
        "DAL's ONR YIP function network (network_dag.py), brought in one stage at a time before chapter 2 of the alloy route (route_dag.py, PR #318)."),
    'dag/route_dag_ch3.mp4': ('Vertical cloud lab: the alloy route as a function network, stage 3 of 5',
        "DAL's ONR YIP function network (network_dag.py), brought in one stage at a time before chapter 3 of the alloy route (route_dag.py, PR #318)."),
    'dag/route_dag_ch4.mp4': ('Vertical cloud lab: the alloy route as a function network, stage 4 of 5',
        "DAL's ONR YIP function network (network_dag.py), brought in one stage at a time before chapter 4 of the alloy route (route_dag.py, PR #318)."),
    'dag/route_dag_ch5.mp4': ('Vertical cloud lab: the alloy route as a function network, stage 5 of 5',
        "DAL's ONR YIP function network (network_dag.py), brought in one stage at a time before chapter 5 of the alloy route (route_dag.py, PR #318)."),
}
# Clips added by later rounds get a title from their file name until they have a line here.

WHERE = {
    "on a tray": "It goes on a tray of the Kardex Shuttle XP 500 vertical lift module.",
    "on a VLM tray": "It goes on a tray of the Kardex Shuttle XP 500 vertical lift module.",
    "on a VLM tray, turned 90 deg": "It goes on a tray of the vertical lift module, turned 90 degrees.",
    "beside the VLM": "It is too big for a tray of the vertical lift module, so it stands beside it.",
}
WHERE_KEY = {"rail": "It runs along the front of the line, for the arm.",
             "hip": "It is shown against a tray of the vertical lift module, which it doesn't fit."}
TITLE_KEY = {   # where "<model>, <title>" reads badly or runs over 100 characters
    "rail": "Vention robot 7th axis, a floor rail for the arm",
    "openflexure_array": "six OpenFlexure microscopes (4 x v7, 2 x Delta Stage) on one sub-tray",
    "openflexure_v7": "OpenFlexure Microscope v7, in reflection",
    "openflexure_delta": "OpenFlexure Delta Stage microscope, in reflection",
    "packaging": "automated packaging station for powders, with label printers and a sealer",
    "vhx": "Keyence VHX-7000 + EA-300, digital microscope with laser elemental analysis",
    "cubxl_corrosion": "the CubXL set up for corrosion testing, with an EZstat Pro potentiostat",
    "stream_cam": "Pi 5 stream camera for a tray, HQ Camera + Camera Module 3 Wide",
    "tray_dock": "the tray service dock, a CombiTac-style coupling",
    "xrf": "Bruker S2 PUMA Series 2, benchtop EDXRF for powders and coupons",
    "lumenpnp": "Opulo LumenPnP v4, open-source pick-and-place",
}


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True, cwd=ROOT).stdout


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def duration(path: Path) -> float:
    """Seconds, from ffmpeg's header read (the static one from imageio-ffmpeg if there is no system ffmpeg)."""
    exe = "ffmpeg"
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    err = subprocess.run([exe, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def stamp(t: float) -> str:
    t = int(t + 1e-6)
    return f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def clean(s: str) -> str:
    """YouTube refuses '<' and '>' in titles and descriptions."""
    s = s.replace("->", "→").replace("<-", "←")
    s = re.sub(r"<=\s*", "≤ ", s)
    s = re.sub(r">=\s*", "≥ ", s)
    s = re.sub(r"<\s*(?=[\d.])", "under ", s)
    s = re.sub(r">\s*(?=[\d.])", "over ", s)
    return s.replace("<", "‹").replace(">", "›")


def fit_bytes(s: str, n: int) -> str:
    b = s.encode()
    if len(b) <= n:
        return s
    return b[:n - 3].decode(errors="ignore").rstrip() + "..."


def load_record() -> dict:
    if RECORD.exists():
        return json.loads(RECORD.read_text())
    return {"channel": CHANNEL, "note": "Every upload of a file under out/mp4, oldest first. sha256 is of the file "
            "uploaded; the newest entry whose sha256 matches the file as it is now is its current video.",
            "videos": {}}


def save_record(rec: dict) -> None:
    rec["videos"] = dict(sorted(rec["videos"].items()))
    RECORD.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")


def current(rec: dict, rel: str, digest: str) -> dict | None:
    for up in reversed(rec["videos"].get(rel, [])):
        if up["sha256"] == digest:
            return up
    return None


def files() -> list[str]:
    tracked = sh("git", "ls-files", str(MP4.relative_to(ROOT))).split()
    return sorted(str(Path(p).relative_to(MP4.relative_to(ROOT))) for p in tracked if p.endswith(".mp4"))


def commit_of(rel: str) -> str:
    """The commit the file as it is now came from (7 characters, as the repo's links use)."""
    path = str((MP4 / rel).relative_to(ROOT))
    if sh("git", "status", "--porcelain", "--", path).strip():
        raise SystemExit(f"{rel} has uncommitted changes; commit and push it first, so its links resolve.")
    return sh("git", "log", "-1", "--format=%H", "--", path).strip()[:7]


def clip_json(rel: str) -> dict | None:
    p = OUT / rel.replace(".mp4", ".json")
    return json.loads(p.read_text()) if p.exists() else None


def table_row(rel: str) -> dict | None:
    """The instrument's row in out/instruments.json or out/fabrication.json."""
    kind, _, key = rel.removesuffix(".mp4").partition("/")
    src = {"instruments": "instruments.json", "fabrication": "fabrication.json"}.get(kind)
    if not src or not (OUT / src).exists():
        return None
    return json.loads((OUT / src).read_text()).get(key)


def steps(clip: dict, budget: int) -> list[str]:
    """The clip's captions with their start times: every change of caption if they fit in ``budget`` bytes, else the
    first caption of each step, shortened if need be."""
    fps = clip.get("fps") or 15
    runs: list[tuple[float, str, str]] = []
    for s in clip.get("substeps", []):
        cap = " ".join(s.get("caption", "").split())
        if cap and (not runs or runs[-1][1] != cap):
            runs.append((s["start_frame"] / fps, cap, s.get("label", "")))
    if not runs:
        return []
    lines = [f"{stamp(t)} {clean(c)}" for t, c, _ in runs]
    if len("\n".join(lines).encode()) <= budget:
        return lines
    firsts, seen = [], set()
    for t, c, label in runs:
        if label not in seen:
            seen.add(label)
            firsts.append((t, c))
    each = max(80, budget // max(1, len(firsts)) - 10)
    return [f"{stamp(t)} {fit_bytes(clean(c), each)}" for t, c in firsts]


def part_name(rel: str) -> str:
    row = table_row(rel)
    if row:
        return f"{row['model']}: {lower_first(row['title'])}"
    return LAB.get(rel, (Path(rel).stem.replace("_", " "),))[0].removeprefix("Vertical cloud lab: ").removesuffix(
        " (3-D animation)")


def chapters(rel: str) -> list[str] | None:
    """One timestamp per part of a joined video, if its parts add up to it (within half a second)."""
    if rel == "alloy_route.mp4" and (OUT / "alloy_route.json").exists():
        route = json.loads((OUT / "alloy_route.json").read_text())
        out = []
        for ch in route.get("chapters", []):
            t = ch.get("start_s", ch.get("start"))
            name = ch.get("title") or ch.get("name") or ch.get("chapter")
            if t is None or not name:
                return None
            out.append(f"{stamp(float(t))} {clean(str(name))}")
        return out or None
    parts = JOINED.get(rel)
    if rel == "instruments_tour.mp4":
        parts = [f"instruments/{k}.mp4" for k in json.loads((OUT / "instruments.json").read_text())]
    elif rel == "fabrication_tour.mp4":
        parts = [f"fabrication/{k}.mp4" for k in json.loads((OUT / "fabrication.json").read_text())]
    if not parts:
        return None
    parts = [p for p in parts if (MP4 / p).exists()]
    lens = [duration(MP4 / p) for p in parts]
    if abs(sum(lens) - duration(MP4 / rel)) > 0.5:
        return None
    out, t = [], 0.0
    for p, n in zip(parts, lens):
        out.append(f"{stamp(t)} {clean(part_name(p))}")
        t += n
    return out


def lower_first(s: str) -> str:
    return s[0].lower() + s[1:] if len(s) > 1 and s[1].islower() else s


def title_for(rel: str) -> str:
    if rel in LAB:
        return clean(LAB[rel][0])[:TITLE_CHARS]
    row = table_row(rel)
    key = Path(rel).stem
    if row:
        what = TITLE_KEY.get(key) or f"{row['model']}, {lower_first(row['title'])}"
        for t in (f"Vertical cloud lab: {what} (3-D animation)", f"Vertical cloud lab: {what}",
                  f"Vertical cloud lab: {row['title']} (3-D animation)"):
            if len(clean(t)) <= TITLE_CHARS:
                return clean(t)
        return clean(f"Vertical cloud lab: {row['title']}")[:TITLE_CHARS]
    return clean(f"Vertical cloud lab: {key.replace('_', ' ')} (3-D animation)")[:TITLE_CHARS]


def description(rel: str, commit: str, replaces: list[str]) -> str:
    row = table_row(rel)
    key = Path(rel).stem
    head: list[str] = []
    if replaces:
        olds = ", ".join(f"https://www.youtube.com/watch?v={v}" for v in replaces)
        head.append(f"Replaces {olds}, an earlier render of the same file.")
    if row:
        tour = "fabrication tour" if rel.startswith("fabrication/") else "instrument tour"
        where = WHERE_KEY.get(key) or WHERE.get(row.get("where", ""), "")
        head.append(clean(f"{row['model']}: {lower_first(row['title'])}. {where} One clip of the vertical cloud "
                          f"lab's {tour} ({REPO}#303)."))
    elif rel in LAB:
        head.append(clean(f"{LAB[rel][1]} Part of {REPO}#303."))
    else:
        head.append(f"A clip of the vertical cloud lab animations ({REPO}#303).")
    head.append("Rendered from CAD models, not filmed, unless a frame says it is real footage.")
    tail: list[str] = []
    if row and row.get("source"):
        tail.append(clean(f"Built from: {row['source']}"))
    for n in (row or {}).get("notes", [])[:2]:
        tail.append(clean(f"Note: {n}"))
    tail.append(f"This file: https://github.com/{REPO}/blob/{commit}/vertical-lab/out/mp4/{rel}")
    tail.append(f"Code, sources and caveats: https://github.com/{REPO}/tree/{commit}/vertical-lab (README.md, notes/)")
    tail.append(f"Pull request: {PR}")
    fixed = "\n\n".join(head) + "\n\n" + "\n\n".join(tail)
    budget = DESC_BYTES - len(fixed.encode()) - 40
    if budget < 400:                                  # a long source line: shorten it, keep the steps
        tail[0] = fit_bytes(tail[0], max(200, len(tail[0].encode()) - (400 - budget)))
        fixed = "\n\n".join(head) + "\n\n" + "\n\n".join(tail)
        budget = DESC_BYTES - len(fixed.encode()) - 40
    body = chapters(rel)
    label = "Parts:"
    if body is None:
        clip = clip_json(rel)
        body = steps(clip, budget) if clip else []
        label = "Steps:"
    while body and len("\n".join(body).encode()) > budget:
        body = body[:-1]
    text = "\n\n".join(head) + ("\n\n" + label + "\n" + "\n".join(body) if body else "") + "\n\n" + "\n\n".join(tail)
    return fit_bytes(text, DESC_BYTES)


def pending(rec: dict, only: list[str] | None = None) -> list[dict]:
    order = {"joined": 0, "lab": 1, "instruments": 2, "fabrication": 3}
    rows = []
    for rel in files():
        if only and rel not in only:
            continue
        digest = sha256(MP4 / rel)
        if current(rec, rel, digest):
            continue
        kind = rel.split("/")[0] if "/" in rel else ("joined" if rel in JOINED or rel.endswith("_tour.mp4")
                                                      or rel == "alloy_route.mp4" else "lab")
        # an upload made from another branch (``branch``) is that branch's video, not an older render of this one
        olds = [u["id"] for u in rec["videos"].get(rel, []) if not u.get("superseded_by") and not u.get("branch")]
        rows.append(dict(rel=rel, sha256=digest, bytes=(MP4 / rel).stat().st_size, kind=kind, replaces=olds))
    rows.sort(key=lambda r: (order.get(r["kind"], 9), r["rel"]))
    return rows


def plan(rec: dict, only=None) -> list[dict]:
    rows = pending(rec, only)
    for r in rows:
        r["commit"] = commit_of(r["rel"])
        r["title"] = title_for(r["rel"])
        r["description"] = description(r["rel"], r["commit"], r["replaces"])
    titles = [r["title"] for r in rows]
    dup = {t for t in titles if titles.count(t) > 1}
    if dup:
        raise SystemExit(f"two files would get the same title: {sorted(dup)}")
    return rows


def upload(rec: dict, only=None) -> None:
    sys.path.insert(0, str(ROOT))
    from googleapiclient.errors import HttpError, ResumableUploadError
    from googleapiclient.http import MediaFileUpload
    from youtube.yt_service import get_youtube_service

    yt = get_youtube_service("upload")
    me = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    if me != CHANNEL:
        raise SystemExit(f"the token is for channel {me}, not {CHANNEL}")
    rows = plan(rec, only)
    print(f"{len(rows)} to upload", flush=True)
    for i, r in enumerate(rows, 1):
        body = {"snippet": {"title": r["title"], "description": r["description"], "tags": TAGS, "categoryId": "28",
                            "defaultLanguage": "en"},
                "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False, "embeddable": True}}
        for attempt in range(4):
            try:
                media = MediaFileUpload(str(MP4 / r["rel"]), mimetype="video/mp4", chunksize=8 << 20, resumable=True)
                req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=False)
                resp = None
                while resp is None:
                    _, resp = req.next_chunk()
                break
            except (HttpError, ResumableUploadError) as e:
                reason = str(e)
                if any(k in reason for k in ("quotaExceeded", "uploadLimitExceeded", "rateLimitExceeded",
                                             "dailyLimitExceeded")):
                    save_record(rec)
                    raise SystemExit(f"stopped at {r['rel']} ({i}/{len(rows)}): {reason[:300]}")
                if attempt == 3 or getattr(getattr(e, "resp", None), "status", 500) < 500:
                    save_record(rec)
                    raise SystemExit(f"failed at {r['rel']}: {reason[:300]}")
                time.sleep(10 * (attempt + 1))
        vid = resp["id"]
        now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for old in rec["videos"].get(r["rel"], []):
            if old["id"] in r["replaces"]:
                old["superseded_by"] = vid
        rec["videos"].setdefault(r["rel"], []).append(dict(id=vid, sha256=r["sha256"], bytes=r["bytes"],
                                                           commit=r["commit"], uploaded=now, title=r["title"],
                                                           privacy="unlisted"))
        save_record(rec)
        print(f"{i}/{len(rows)} {r['rel']} -> https://www.youtube.com/watch?v={vid}", flush=True)


def table(rec: dict) -> Path:
    lines = ["# The vertical-lab videos on YouTube", "",
             "Every MP4 under `out/mp4/` and its video on the lab's channel (unlisted). Written by "
             "`python3 youtube_upload.py table` from `out/youtube.json`, which also has the older uploads.", "",
             "| File | Length | Video | Earlier uploads |", "|---|---|---|---|"]
    for rel in files():
        digest = sha256(MP4 / rel)
        up = current(rec, rel, digest)
        ups = rec["videos"].get(rel, [])
        older = [u["id"] for u in ups if not up or u["id"] != up["id"]]
        vid = f"[{up['id']}](https://www.youtube.com/watch?v={up['id']})" if up else "not uploaded"
        old = ", ".join(f"[{v}](https://www.youtube.com/watch?v={v})" for v in older)
        lines.append(f"| [`{rel}`](mp4/{rel}) | {stamp(duration(MP4 / rel))} | {vid} | {old} |")
    TABLE.write_text("\n".join(lines) + "\n")
    return TABLE


if __name__ == "__main__":
    args = sys.argv[1:]
    record = load_record()
    if not args or args[0] == "plan":
        for r in plan(record, args[1:] or None):
            print(f"{r['rel']:40s} {r['commit']} {len(r['title']):3d} {r['title']}"
                  + (f"  [replaces {', '.join(r['replaces'])}]" if r["replaces"] else ""))
    elif args[0] == "show":
        for r in plan(record, args[1:] or None):
            print("=" * 100, "\n", r["title"], "\n", "-" * 100, "\n", r["description"], sep="")
    elif args[0] == "upload":
        upload(record, args[1:] or None)
    elif args[0] == "table":
        print(table(record))
    else:
        raise SystemExit(__doc__)
