"""The vertical cloud lab, start to finish (#303): everything on PR #318 in one long-form video, with chapters.

    python3 longform.py plan       # the parts in order, their sources and lengths; nothing is encoded
    python3 longform.py            # -> out/mp4/vertical_lab_longform.mp4, out/longform.json, out/longform_sheet.png
    python3 longform.py tts        # the narration (narration.json) spoken by Kokoro, cached in /tmp/longform_tts
    python3 longform.py audit      # the checks chapter's table, out/collisions/<LONGFORM_AUDIT_TAG>_table.png
    python3 longform.py upload     # public (LONGFORM_PRIVACY), subscribers notified (LONGFORM_NOTIFY), the chapter
                                   # timestamps in the description; recorded in out/youtube.json

Every part is a clip that renders on its own, from its own script, with its own GIF, MP4 and JSON. This file only
puts them in order, draws a title card before each chapter, draws a caption band on the stills (the figures and the
contact sheets), a REAL FOOTAGE badge on the one piece of real video and a badge on another project's own render, and
writes the chapter list. Every part is re-encoded once to LONGFORM_SIZE at 30 fps before the join, so clips drawn at
8, 10, 12, 15 or 30 fps keep their length. Round 15 (Sterling, 2026-11-23: "re-render everything in a self-consistent
and cohesive way ... render at a higher res (max fps for 720p)"): 1280 x 720, the 3-D drawn at up to 30 fps. A clip is
taken from out/<LONGFORM_HD_DIR>/ (r15, this pass's renders: ``VIZ3D_HD=1 VIZ3D_HD_DIR=r15``) and, if it isn't there or
is still being written, from out/mp4/, flagged in out/longform.json as an earlier render.

Round 12 adds a narration: narration.json, one line per entry, each anchored to a chapter's card, a still, or a clip's
sub-step (its index in the clip's JSON, checked against the label, or a phrase of its caption), or a time into a clip
that has no sub-steps ("at"), spoken by Kokoro (open weights, run on the runner) and mixed into one track, with
out/longform_narration.srt beside it.

Round 15 adds the merged PRs' work: the cups machined (#373) at the start of chapter 1, the base cameras (#374) and the
security cameras considered (#370) in the services chapter, a safety chapter (#379), the CubXL's P300 and its well's
evaporation (#372), names (#376) and colour coding (#377) with the stations, and the floor cleaning (#369) and the waste
(#371) in a chapter of their own; and powder-doser's own render of its newest doser (PR #185, v10) in chapter 1.

Round 16 (Sterling, 2026-11-26: address PR #371's check of what round 15 really rendered "in full and rerender and get
on YouTube"): the clips round 15 kept from earlier renders and the clips this round changes are rendered again into
out/r16/ (render_r16.py); every other clip is round 15's own render, cut back out of round 15's long-form as YouTube
serves it (720p30, frame-exact by round 15's out/longform.json: out/r15/recovered.json), because round 15's renders were
git-ignored and went with its runner. LONGFORM_HD_DIR lists the folders in order (r16,r15), then out/mp4/. A line of
narration over a recovered clip is spoken where round 15 spoke it (r15_offsets), since the frames are the same.

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
# round 15: 1280 x 720 (round 12-14: 1920 x 1080), Sterling: "render at a higher res (max fps for 720p)"
SIZE = tuple(int(v) for v in os.environ.get("LONGFORM_SIZE", "1280x720").split("x"))
FPS = int(os.environ.get("LONGFORM_FPS", "30"))
K = SIZE[1] / 720              # the pixel sizes below were chosen at 1280 x 720
# this pass's renders; a clip not there falls back to out/mp4/. Round 15: LONGFORM_HD_DIR names the folder of the pass
# (VIZ3D_HD_DIR), r15 for the 720p pass drawn at up to 30 fps (round 12's 1080p pass was out/hd/)
# round 16: several folders, the first found wins: r16 (this round's renders), then r15 (round 15's clips recovered
# from its YouTube copy), then out/mp4/
HD_DIRS = [OUT / d.strip() for d in os.environ.get("LONGFORM_HD_DIR", "r16,r15").split(",") if d.strip()]
HD = HD_DIRS[0]
R15 = OUT / "r15"                  # round 15's clips, recovered (out/r15/recovered.json)
R15_COMMIT = os.environ.get("LONGFORM_R15_COMMIT", "4f9ec11e")    # round 15's long-form build: its parts and narration
CARD_S = 6.0
AUDIT_TAG = os.environ.get("LONGFORM_AUDIT_TAG", "round16")   # out/collisions/<tag>_table.png, _summary.json
# every part is encoded with the same settings, so the join is a stream copy
X264 = ["-c:v", "libx264", "-preset", os.environ.get("LONGFORM_PRESET", "veryfast"), "-crf", "18", "-pix_fmt", "yuv420p",
        "-profile:v", "high", "-g", str(2 * FPS), "-video_track_timescale", "15360"]
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
# Round 12: #332 (claude/bottlenecks-10-a-day-20261108), the bottleneck ladder from one fully tested alloy a day to ten
BOTTLENECK = "cc31ddc"

# ===================================================================================================== the chapters
# Each chapter: a key, its title (also the YouTube chapter line), the card's lines, and its parts in order. A part is
#   ("mp4", rel under out/mp4, label or None)                    a rendered clip, whole (out/<LONGFORM_HD_DIR>/ first)
#   ("still", rel under out, seconds, caption, label or None)    a figure, letterboxed, or scrolled if it is tall
#   ("footage", rel under out, caption, label or None)           real video, with a REAL FOOTAGE badge and a credit
#   ("ext", rel under out/mp4, badge, caption, label or None)    another project's own render, framed, badged, credited
# A label starts a YouTube chapter of its own inside the chapter (merged into the next if it would be under 10 s).
CHAPTERS = [
    dict(key="intro", title="A real VLM, then the plan",
         card=["A Kardex vertical lift module (VLM) holds the lab's equipment on electrified trays, each powered tray "
               "with its own UPS. UR12e arms (the UR10e, renamed in 2025) on MiR250 mobile bases, each base with three "
               "cameras and a Class D extinguisher, work at its openings and at the machines too big for a tray.",
               "Everything after the first clip is a 3-D animation, built from the makers' published figures and "
               "photos and checked for collisions. Real footage, photos and data are badged as such."],
         parts=[("footage", "footage/vlm_real_ck8QJhVqPiY.mp4",
                 "A real VLM in operation, from the sample's perspective (Sterling Baird, youtu.be/ck8QJhVqPiY)",
                 None)]),
    # round 15: the safety PR's units come in with the utilities (#379), the waste station with the fume hood (#371),
    # floor-cleaning unit 3 parks on a third charger (#369), and each MiR250 brings its three cameras (#374) and its
    # Class D unit. Round 16 (PR #371's check): the cups' machining cell (#373) gets a spot south of the south row
    # (notes/lab_r16.md) and the powder-waste point stands beside the rePowder (powder_point.py); the ICP-MS station
    # still has no clean spot (notes/lab_r15.md), so its clip shows it on its own
    dict(key="setup", title="The lab set up from scratch",
         card=["An empty warehouse bay: the layout taped out, utilities overhead, two 30 ft (9.15 m) Kardex Shuttle XP "
               "500s going up with a 996 mm opening, the floor machines, the safety equipment, a waste station under "
               "the fume hood, the powder-waste point beside the atomizer and the cups' machining cell behind the south "
               "row, the arms assembled onto their MiR250s (a third, floor-cleaning unit on its own charger), then "
               "every tray "
               "loaded by people: a UPS and stream cameras on each powered one, none on the sample and powder-jar "
               "stores, whose short trays the cameras under each bay's roof inventory."],
         parts=[("mp4", "setup_lab.mp4", None),
                ("still", "tray_plan.png", 14.0, "Every tray from above, each part's own footprint: its UPS with an "
                 "AirGradient, dock plate and cameras where it needs them, nothing closer than 10 mm; and its slot in "
                 "the 30 ft Shuttles", "What goes on which tray")]),
    dict(key="services", title="Services: UPS, automatic hookups, cabling and cameras",
         card=["Each powered tray carries a UPS sized for it: a Vertiv Liebert lithium unit of 800, 1500 or 3000 VA. In "
               "its slot and again in the picking bay, a floating dock in the side wall mates two Stäubli CombiTac "
               "frames with the tray's: mains, Ethernet, air, N2 and chilled water; in transit the tray runs on its UPS.",
               "Then the cabling, the stream camera unit, the cameras under each bay's roof and the three on each "
               "MiR250, and security cameras considered in place of the Pi units (research only)."],
         parts=[("mp4", "vlm_hookups.mp4", "Storage to the bay: the hookups and the UPS"),
                ("mp4", "vlm_coupling.mp4", "The coupling, part by part: Stäubli CombiTac on a floating dock"),
                ("mp4", "vlm_services.mp4", "The docks in every slot"),
                ("still", "ups_lineup.png", 12.0, "Three real UPSs, sized tray by tray from each tray's own loads: Vertiv "
                 "Liebert PSI5-800, GXT5LI-1500 and GXT5LI-3000, lithium (notes/ups.md)", "A real UPS for each tray"),
                ("mp4", "vlm_cabling.mp4", "Cabling"),
                ("mp4", "instruments/stream_cam.mp4", "The stream camera unit: height, pan, tilt"),
                ("mp4", "bay_camera.mp4", "The cameras under the bay's roof, and what each sees"),
                # round 15: PR #374 (Sterling, 2026-11-20: "add two or three cameras to the mobile manipulator")
                ("mp4", "base_cameras.mp4", "Three cameras on each MiR250"),
                # round 15: PR #370, research only (Sterling: security cameras pulled by a Pi, as aurora-cloud-infra does)
                ("still", "security_cameras_bay.png", 12.0, "Considered, research only: security cameras in place of the "
                 "Pi units, hung under the bay's assumed roof (PR #370, notes/security_cameras.md). The video keeps "
                 "the Pi units", "Considered: security cameras instead")]),
    # Round 15: PR #379 (Sterling, 2026-11-20: "Class D fire extinguishers at each station ... mounted at all times to
    # the MiR250"; 2026-11-22, of the building's extinguishers, showers and O2 monitors: "Do these"). Right after the
    # services: every clip from here on has the units on the floor and on the MiR250s
    dict(key="safety", title="Safety: Class D extinguishers, showers and oxygen monitors",
         card=["Burning metal powder needs a Class D agent, not water or CO2. An Amerex B570, 30 lb of Super D, stands "
               "within 4 m of every station that handles powder, one rides on each MiR250, and 150 lb wheeled units "
               "stand at the rePowder and the EOS.",
               "The building's ordinary extinguishers are kept apart and signed differently, a shower and eyewash "
               "stands at each fume hood, and an oxygen monitor wherever argon or nitrogen is used (PR #379)."],
         parts=[("mp4", "safety.mp4", None),
                ("still", "safety_plan.png", 11.0, "Class D on the floor: seven B570s on posts, two 150 lb 680Rs, two "
                 "pails, one B570 on each MiR250. The longest walk from a powder station to a fixed unit is 4.0 m "
                 "(NFPA 10: 75 ft)", "Where the Class D units go"),
                ("still", "safety_other_assets.png", 11.0, "The building's ABC units on the racking, 4.3 m or more from "
                 "any Class D unit and signed differently; a shower and eyewash at each hood; O2 monitors "
                 "(notes/safety.md)", "Ordinary extinguishers, showers and O2 monitors")]),
    dict(key="corrosion", title="Tray A: the corrosion station, OT-2 and CubXL, and an ICP-MS station",
         card=["The OT-2 makes up the CubXL's sulfide stock. The CubXL runs DAL's copper corrosion screen spot by "
               "spot (DAL PR #180) with its P20 and, proposed, a P300 on a lift of its own (PR #372), which also "
               "puts the powder test's 200 µL of seawater in at once. Its magnet holds one cap at a time.",
               "No acid on the OT-2's deck: the CubXL acidifies its own tubes, and an ICP-MS station, its floor spot "
               "still open, dilutes them in its own fume hood."],
         # round 15: the OT-2's clip no longer dilutes the ICP-MS tubes (ot2_corrosion.py: no acid on its deck)
         parts=[("mp4", "instruments/ot2_corrosion_prep.mp4", "The OT-2: the CubXL's sulfide stock"),
                ("mp4", "instruments/cubxl_corrosion.mp4", "The CubXL's corrosion screen"),
                # round 15: PR #372 (Sterling's three CubXL questions, 2026-11-20): evaporation and sulfide loss
                ("still", "cubxl_evap.png", 11.0, "The CubXL's well, first-order estimates: 1-3 % of its water a spot, "
                 "but most of the sulfide escapes as H2S unless the well is mixed or sealed (PR #372, "
                 "notes/cubxl_pipettes.md)", "The well: evaporation and sulfide loss"),
                # round 14 (D): the ICP-MS station on the floor, its acids in a fume hood (icpms.py, notes/icpms.md)
                ("mp4", "icpms.mp4", "An ICP-MS station, its acids in a fume hood"),
                ("mp4", "vlm_workflow.mp4", "Atomized powder dosed for the CubXL")]),
    dict(key="alloy1", title="Alloy route 1/7: the charge cups, machined, dosed, weighed and pressed under vacuum",
         card=["The atomizer melts the lab's own charge cups (#222). A lathe cell behind the south row turns each cup and its "
               "plug from 5N Al or oxygen-free Cu bar, washes them in IPA and dries them under vacuum (PR #373). Each "
               "cup is dosed by weight on the A&D HR-202i under the multi-doser, and its vented plug pressed fully home "
               "under vacuum in a Specac Atlas Autotouch. The die is cleaned between presses, and every cup weighed "
               "again."],
         parts=[("mp4", "dag/route_dag_ch1.mp4", "The route as a function network (DAL's ONR YIP DAG)"),
                ("still", "dal_workflow_table.png", 14.0, "DAL's alloy workflow, step by step (notes/dal_workflow.md): "
                 "the station each step uses here, and what is still missing", "DAL's 17 steps, and where each runs"),
                # round 15: PR #373 (Sterling, 2026-11-20: "automate machining of the high-purity cups and plugs ...
                # a cleaning and drying step (IPA for example)"): the cups are made before they are charged
                ("mp4", "machining_cell.mp4", "Machining the cups and plugs: a lathe, an IPA wash, a vacuum dryer"),
                ("still", "machining_sim.png", 10.0, "The cell simulated part by part (SimPy, 5 seeds x 28 days): about "
                 "114 pairs a day with a pedestal arm against the 67 needed, and a MiR250 unit instead "
                 "(notes/machining.md)",
                 None),
                # round 16 (PR #371's check: "Give the machining cell a place on the floor that doesn't take unit 3's
                # charger"): its place, south of the south row (notes/lab_r16.md)
                ("still", "machining_floor.png", 11.0, "The cell's place (round 16): south of the south row, off unit "
                 "3's charger bay; its MiR250 comes down the row's west end and along a corridor behind it, then "
                 "backs in (notes/lab_r16.md)", "The cell's place on the floor"),
                ("mp4", "alloy_charge.mp4", "The charge cups"),
                # round 14 (D): run B's dose post and draft shield (doser_shield.py) in place of round 10's "can the cup
                # come closer?" section, which the new station answers
                ("still", "doser_shield_section.png", 14.0, "The fall shortened (round 14): a dose post lifts the cup to "
                 "45 mm under the exit, in a clear draft shield (both ours); it was 153 mm, mostly in open air "
                 "(notes/multidoser.md)", "A shorter fall: a dose post and a draft shield"),
                # round 15: powder-doser PR #185's newest design (v10, 2026-11-19) in its own CAD render, fetched as the
                # doser's latest result (out/mp4/ext/credits.json); this lab's clips still use v5 with the dose post
                ("ext", "ext/doser_drop_v10.mp4", "POWDER-DOSER'S OWN CAD RENDER", "of its newest design, v10 (PR "
                 "#185): the beaker 18 mm under the auger's exit. Not yet in this lab's animation, which uses v5 and "
                 "the dose post (a 45 mm fall)", None)]),
                # round 15: the vacuum press's own close-up is out: chapter 1 now shows the press's whole cycle in the
                # shared lab, and the close-up differs from it (plug set at the press, one powder layer, no cleaning)
    dict(key="alloy2", title="Alloy route 2/7: melt and atomize in the rePowder",
         card=["Both MiR250 + UR12e units go to the AMAZEMET rePowder, each with a 131 kg ballast plate low in its base, "
               "and open its furnace together. A loading tool lowers each of the "
               "four Al cups into the crucible. Pump-downs with argon, induction melt, the pour, the ultrasonic spray, powder in the "
               "container. During the pour both arms hold the knobs of a landing stage (ours) and trim the plate under "
               "the stream from the melt-stream cameras. Cut with the lab's own footage, each piece badged with its "
               "alloy, date and source."],
         parts=[("mp4", "dag/route_dag_ch2.mp4", None), ("mp4", "alloy_atomize.mp4", None)]),
    # Round 12: PR #353 (Sterling, 2026-11-19: automate "all aspects of the process"), merged into this branch
    dict(key="atomizer", title="Automating the atomizer's turnaround",
         card=["Between runs the rePowder is taken apart, cleaned and rebuilt, by hand today, following the lab's SOP. "
               "Here two arms do it with tools held by a handle: the latch, the powder container, the chamber vacuumed "
               "with the explosion-proof Nilfisk, the plate swapped, the crucible cleaned and recoated with boron "
               "nitride, and the rebuild, with the viewport cameras watching.",
               "The tools, fixtures and moves are our designs (PR #353)."],
         parts=[("mp4", "atom_cameras.mp4", "The melt and the stream, watched"),
                ("mp4", "atom_latch.mp4", "The furnace latch, unclamped and clamped"),
                ("mp4", "atom_container.mp4", "The powder down and the container off"),
                ("mp4", "atom_vacuum.mp4", "Vacuuming the chamber"),
                ("mp4", "atom_plate.mp4", "Swapping the plate"),
                ("mp4", "atom_crucible_out.mp4", "Taking the furnace apart"),
                ("mp4", "atom_bn.mp4", "Cleaning the crucible and recoating it with boron nitride"),
                ("mp4", "atom_crucible_in.mp4", "The rebuild, and the graphite nut from below"),
                ("still", "atom/turnaround.png", 12.0, "The turnaround between runs, step by step: who does each, and how "
                 "long it takes (a model; notes/atomizer_automation.md)", "The turnaround, timed")]),
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
               "polishing is the hard part, and the chapter says where. Re-planned in round 15 with the MiR250's "
               "cameras and extinguisher aboard: the discs drawn out 340 mm, not 470, the CNC's lid shut before its "
               "tray goes back, the mounts in plain bores; the arm in collision in 0 frames."],
         parts=[("mp4", "dag/route_dag_ch6.mp4", None), ("mp4", "alloy_prep.mp4", None)]),
    dict(key="alloy7", title="Alloy route 7/7: characterizing the build",
         card=["The trays come to the opening in turn: the SEM with the mount clamped in its holder, the VHX, "
               "micro-Vickers, the nanoindenter and PIP on the steel-mounted slice. Each instrument's data is "
               "shown, and labelled real or illustrative."],
         parts=[("mp4", "dag/route_dag_ch7.mp4", None), ("mp4", "alloy_characterize.mp4", None)]),
    # Round 8: the XRD, Mastersizer, XRF and SEM work in chapter 4, the furnace, wire EDM and Instrons in chapter 5, the
    # mounting press, PX500 and Carvera in chapter 6, the SEM, VHX, HM-220, iMicro and PIP in chapter 7, the sieve shaker
    # in chapter 3. Their stand-alone tour clips are left out (Sterling, of the XRD: "why isn't a tray coming and then the
    # robot is putting something in there"); this chapter keeps the stations no chapter uses. Round 15: the names (#376)
    # and the colour code (#377) the whole lab would use, after the gallery
    dict(key="stations", title="The other stations: a tensile tester on its side, gloveboxes, fume hoods, stores, shipping",
         card=["Every instrument model at a glance, a name for each station and a colour for each powder family, then "
               "the stations the alloy route doesn't pass through: a horizontal tensile tester for small bars, a "
               "glovebox on a tray and one on the floor, fume hoods (no HF), the sample store, the powder-jar store, "
               "and a packaging station that labels and seals powder for shipping."],
         parts=[("still", "instruments_gallery.png", 9.0, "Every instrument model: size, and on a tray or beside "
                 "the VLM", "Every instrument model"),
                ("still", "naming/floor_names.png", 11.0, "A call name for each station, a stone whose own property is "
                 "its job (fluorite for the XRF, flint for the wire EDM); the Shuttles are Provo's peaks, timp and nebo "
                 "(PR #376, a proposal)", "A name for everything: stones and peaks"),
                ("still", "colour/bench.png", 11.0, "Colour only where a person decides which tool touches which powder: "
                 "blue for the Al family, orange for Cu, each with a word, checked for colour-blind readers (PR #377)",
                 "Colour coding: blue for Al, orange for Cu"),
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
                ("still", "interference_sheet.png", 11.0, "MuJoCo interference check: what was left over after "
                 "the fixes", "MuJoCo interference check"),
                ("still", "collisions/round11_sheet.png", 12.0, "Round 11's stricter check, clip by clip: frames in "
                 "collision under the old rules and the new, before and after the fixes", "The stricter check, round 11"),
                # round 15: this pass's own table (`python3 longform.py audit` once the renders are in), scrolled
                ("still", f"collisions/{AUDIT_TAG}_table.png", 18.0, "This video's own check: every clip checked "
                 "frame by frame as it was rendered, at the rate it is drawn", "This video, checked frame by frame")]),
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
    # Round 15: PRs #369 (Sterling, 2026-11-20: automatic floor cleaning; 2026-11-22: "show animated visualizations of
    # the processes here, including the human-in-the-loop interactions ... a full pass across the facility") and #371
    # (2026-11-20: "Where does each waste go, how do we get pickups ..."). After the upkeep, the lab's other housekeeping
    dict(key="floor", title="Keeping the floor clean, and the waste",
         card=["Metal powder on the floor is a fire hazard, and no cleaning robot on the market is rated for it. One "
               "option, explored, not decided: unit 3, a third MiR250 + UR12e, squeegees with an explosion-proof "
               "Nilfisk's wand and checks the floor's colour; a visible spill stays a person's job (PR #369).",
               "Then the waste (PR #371): a bottle's trip to the fume hood, its cabinets, and the powder-waste point "
               "by the atomizer."],
         parts=[("mp4", "floor_clean_people.mp4", "Unit 3, and a person for a visible spill"),
                ("mp4", "floor_pass.mp4", "A night's pass across the whole floor, from above"),
                ("still", "waste_streams.png", 14.0, "Every waste stream, a year, at one fully tested alloy a day and at "
                 "ten: modelled, not weighed (PR #371, notes/waste.md)", "The waste, stream by stream"),
                # round 16 (PR #371's check: "Nothing about waste handling is animated"): the clip in place of the
                # station's still
                ("mp4", "waste_clip.mp4", "The waste, handled: a bottle's trip, the cabinets, the powder point")]),
    # Round 12: PR #332 (Sterling, 2026-11-08: "how can we get that up to 10/day?"), a figure at its pinned commit
    dict(key="bottlenecks", title="From one alloy a day to ten: the bottlenecks",
         card=["The year model tests about one alloy a day: a person changes the atomizer's crucible on weekdays, and that "
               "staffing, not a machine, sets the rate. Ten a day takes the crucible changed round the clock (by people, "
               "or by robots as in the atomizer chapter), three rePowders and four MIDIs; or a DED front end that "
               "screens compositions as blocks. PR #332: a model, not a measurement."],
         parts=[("gitstill", BOTTLENECK, "vertical-lab/out/bottleneck_ladder.png", 16.0, "The ladder from about one "
                 "fully tested alloy a day to ten: what each step adds (PR #332, notes/bottleneck.md)", None)]),
    dict(key="finale", title="The whole lab at speed: an hour, a day, a week, a month",
         card=["Everything at once, sped up: the trays cycling, the arm and the atomizer working, the printer "
               "building, then day by day, week by week and month by month, with what the lab has made and "
               "measured so far.",
               "Maintenance runs in the same schedule: the person and visiting vendors where their task is, a beacon "
               "on each machine (amber for upkeep, red while a fault waits), and the upkeep counters beside the rest."],
         parts=[("mp4", "timelapse.mp4", None)]),
]
OUTRO = ["Code, notes and every source: github.com/vertical-cloud-lab/byu-vcl, PR #318 (folder vertical-lab/). "
         "The narration is a synthetic voice (Kokoro, an open text-to-speech model).",
         "Sizes are the makers' published figures where they exist. The docks, fixtures, cells, the press's die and "
         "the camera and extinguisher mounts are our designs at assumed sizes, and each notes file says which numbers "
         "are assumed. The doser's v10 clip is powder-doser's own render.",
         "Vertical Cloud Lab @ BYU, byu-vcl #303"]


# ===================================================================================================== helpers
def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def _under(path: Path, base: Path) -> bool:
    try:
        Path(path).relative_to(base)
        return True
    except ValueError:
        return False


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
                          f"{SIZE[0]}x{SIZE[1]}", "-r", str(FPS), "-i", "-", "-frames:v", str(n), *X264, *THREADS,
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
    d.rectangle((0, 0, SIZE[0], int(10 * K)), fill=BLUE)
    x, w = int(80 * K), SIZE[0] - int(160 * K)
    d.text((x, int(120 * K)), over, font=font(28 * K), fill=GREY)
    ft = font(54 * K, bold=True)
    tl = wrap(d, title, ft, w)
    if len(tl) > 2:
        ft = font(44 * K, bold=True)
        tl = wrap(d, title, ft, w)
    y = int(165 * K)
    for ln in tl:
        d.text((x, y), ln, font=ft, fill=BLUE)
        y += int(ft.size * 1.22)
    y += int(22 * K)
    fb = font(29 * K)
    for para in lines:
        for ln in wrap(d, para, fb, w):
            if y > SIZE[1] - int(110 * K):
                print(f"  card {title[:40]!r}: text cut off at {ln[:40]!r}", flush=True)
                break
            d.text((x, y), ln, font=fb, fill=INK)
            y += int(40 * K)
        y += int(14 * K)
    d.text((x, SIZE[1] - int(70 * K)), foot or "Vertical Cloud Lab @ BYU, byu-vcl #303", font=font(22 * K), fill=GREY)
    return im


def still_frames(src: Path, seconds: float, caption: str):
    """A figure under a caption band: letterboxed if it is wide, scrolled top to bottom if it is tall."""
    band = int(86 * K)
    area = (SIZE[0], SIZE[1] - band)
    im = Image.open(src).convert("RGB")
    n = int(round(seconds * FPS))
    cap = Image.new("RGB", (SIZE[0], band), "white")
    d = ImageDraw.Draw(cap)
    d.line((0, 0, SIZE[0], 0), fill=BLUE, width=max(2, int(3 * K)))
    fb = font(25 * K)
    for k, ln in enumerate(wrap(d, caption, fb, SIZE[0] - int(60 * K))[:2]):
        d.text((int(30 * K), int((12 + 34 * k) * K)), ln, font=fb, fill=INK)
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
    fb = font(26 * K, bold=True)
    tw = d.textlength(text, font=fb)
    d.rounded_rectangle((int(24 * K), int(22 * K), int(24 * K + tw + 32 * K), int(68 * K)), radius=int(8 * K),
                        fill=(200, 30, 30, 235))
    d.text((int(40 * K), int(30 * K)), text, font=fb, fill="white")
    fc = font(25 * K)
    lines = wrap(d, caption, fc, SIZE[0] - int(60 * K))[:2]
    h = int((24 + 34 * len(lines)) * K)
    d.rectangle((0, SIZE[1] - h, SIZE[0], SIZE[1]), fill=(255, 255, 255, 225))
    for k, ln in enumerate(lines):
        d.text((int(30 * K), SIZE[1] - h + int((12 + 34 * k) * K)), ln, font=fc, fill=INK)
    im.save(path)


BAND = 86                      # the caption band under a still or another project's render, px at 720p


def ext_lines(d: ImageDraw.ImageDraw, badge: str, caption: str) -> tuple[int, list[str], list[str]]:
    """The badge's width, and the caption's words on the first line (after the badge) and the rest (full width)."""
    tw = int(d.textlength(badge, font=font(19 * K, bold=True)) + 22 * K)
    fc = font(25 * K)
    first, words = "", caption.split()
    while words and d.textlength(f"{first} {words[0]}".strip(), font=fc) <= SIZE[0] - int(72 * K) - tw:
        first = f"{first} {words.pop(0)}".strip()
    return tw, [first], wrap(d, " ".join(words), fc, SIZE[0] - int(60 * K))


def ext_png(badge: str, caption: str, path: Path):
    """Round 15: another project's own render (powder-doser's CAD of its v10 doser) keeps its own titles and captions,
    so it is framed above a caption band like the stills', whose first words are a blue badge saying whose render it
    is. Transparent above the band."""
    band = int(BAND * K)
    im = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y0 = SIZE[1] - band
    d.rectangle((0, y0, SIZE[0], SIZE[1]), fill=(255, 255, 255, 255))
    d.line((0, y0, SIZE[0], y0), fill=BLUE, width=max(2, int(3 * K)))
    tw, first, rest = ext_lines(d, badge, caption)
    d.rounded_rectangle((int(30 * K), y0 + int(12 * K), int(30 * K) + tw, y0 + int(41 * K)), radius=int(7 * K),
                        fill=BLUE + (255,))
    d.text((int(41 * K), y0 + int(16 * K)), badge, font=font(19 * K, bold=True), fill="white")
    fc = font(25 * K)
    d.text((int(42 * K) + tw, y0 + int(12 * K)), first[0], font=fc, fill=INK)
    for k, ln in enumerate(rest[:1]):
        d.text((int(30 * K), y0 + int(46 * K)), ln, font=fc, fill=INK)
    im.save(path)


def caption_fits(r: dict) -> bool:
    """Whether a part's caption fits its band's two lines (still_frames, badge_png and ext_png cut the rest)."""
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    if r["kind"] == "ext":
        return len(ext_lines(d, r["badge"], r["caption"])[2]) <= 1
    if r["kind"] in ("still", "footage"):
        return len(wrap(d, r["caption"], font(25 * K), SIZE[0] - int(60 * K))) <= 2
    return True


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


def normalise(src: Path, dst: Path, overlay: Path | None = None, band: bool = False):
    """`src` scaled to fit SIZE (or, `band`, the area over a caption band, as a still is), at FPS, with `overlay`."""
    vf = (f"scale={SIZE[0]}:{SIZE[1]}:force_original_aspect_ratio=decrease:flags=lanczos,"
          f"pad={SIZE[0]}:{SIZE[1]}:(ow-iw)/2:(oh-ih)/2:color=white,fps={FPS},setsar=1")
    if band:
        h = SIZE[1] - int(BAND * K)
        vf = (f"scale={SIZE[0]}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,"
              f"pad={SIZE[0]}:{SIZE[1]}:(ow-iw)/2:({h}-ih)/2:color=0xF6F7F9,fps={FPS},setsar=1")
    if overlay is None:
        args = ["-i", src, "-vf", vf]
    else:
        args = ["-i", src, "-i", overlay, "-filter_complex", f"[0:v]{vf}[v];[v][1:v]overlay=0:0[o]", "-map", "[o]"]
    run("ffmpeg", "-y", "-loglevel", "error", *args, "-an", *X264, *THREADS, dst)


def warm(skip=()):
    """Normalise every clip the plan has into the cache, without joining: run while renders are still going, so the
    final build only encodes what changed (each part is keyed on its source's bytes). `skip`: substrings of the
    sources still to be re-rendered."""
    tmp = Path(tempfile.mkdtemp(prefix="longform_warm_"))
    n = 0
    for i, r in enumerate(plan()):
        if r.get("missing") or r["kind"] not in ("mp4", "footage", "ext"):
            continue
        if any(k in str(r.get("git") or r["src"]) for k in skip):
            continue
        out = tmp / f"w{i:03d}.mp4"
        if r["kind"] == "footage":
            ov = tmp / f"badge{i:03d}.png"
            badge_png("REAL FOOTAGE", r["caption"], ov)
            cached([r["src"], ov, SIZE, FPS, "footage"], lambda d, r=r, ov=ov: normalise(r["src"], d, ov), out)
        elif r["kind"] == "ext":
            ov = tmp / f"ext{i:03d}.png"
            ext_png(r["badge"], r["caption"], ov)
            cached([r["src"], ov, SIZE, FPS, "ext"], lambda d, r=r, ov=ov: normalise(r["src"], d, ov, band=True), out)
        else:
            cached([r["src"], SIZE, FPS, "mp4"], lambda d, r=r: normalise(r["src"], d), out)
        out.unlink()
        n += 1
        print(f"  warm: {r.get('git') or r['src']}", flush=True)
    print(f"{n} parts in {CACHE}", flush=True)


# ===================================================================================================== DAL's steps
# Round 14 (run D): per step, what this design does with it. Sterling on round 12's card (PR #318, 2026-11-20): '"most by
# hand" is dissatisfying and misleading', e.g. the BN coating is automated in #353's clips. Status: "auto", automated
# in this design and shown in the video (the chapter says where); "progress", designed or being designed, not in the
# video yet; "none", no station yet; "manual", stays a person's. The last column is what, inside the step, still
# takes a person or is still open. notes/dal_workflow.md has the long form with sources.
DAL_STEPS = [   # (step, station in this design, status, what inside it is still by hand, in progress or open)
    ("Pick a composition", "software: Bayesian optimization over a CALPHAD-screened space", "auto", ""),
    # round 15: the cups and plugs machined, washed and dried in a cell of their own (PR #373, merged)
    ("Weigh the charge", "lathe cell for the cups; multi-doser + balance, vacuum press (ch. 1)", "auto",
     "open: the lathe's trial cuts and quotes (PR #373)"),
    ("Coat the crucible (BN)", "scraped and sprayed by the arm in a fume hood (turnaround)", "auto", ""),
    ("Atomize", "rePowder: loaded, opened, rebuilt by two arms (ch. 2, turnaround)", "auto",
     "by hand: booster swaps, argon cylinders; the arm presses the HMI until AMAZEMET opens an interface"),
    ("Recover and sieve", "explosion-proof vacuum (turnaround); sieving cell with wash (ch. 3)", "auto", ""),
    ("Store", "1,506-jar store on trays N, O, P and Q", "auto", "open: dry storage at about 25 % RH (DAL #131)"),
    ("Characterize the powder", "laser diffraction, XRD with its prep, XRF, SEM (ch. 4)", "auto",
     "in progress: composition by ICP-MS, the new hood station (corrosion chapter)"),
    ("Ship powder out", "packaging station: labels, seal, box", "auto", "by hand: the dangerous-goods call for each powder"),
    ("Print", "Aconity MIDI fed by the arm; depowdering box (ch. 3, 5)", "auto", ""),
    ("Cut parts off the plate", "wire EDM, bars caught in a comb (ch. 5)", "auto", ""),
    ("Heat treat", "Nabertherm furnace, tray F (ch. 5)", "auto", "open: the schedule, DAL's to set"),
    ("Density (Archimedes)", "no station yet", "none", "open: a balance with a density kit"),
    ("Metallography", "EDM sections, hot mounting, PX500 with ready discs (ch. 6)", "auto",
     "by hand: re-papering the discs"),
    ("Mechanical testing", "tensile at 20 and 200 °C (ch. 5); Vickers, nanoindenter, PIP (ch. 7)", "auto",
     "by hand: the nanoindenter's tip change"),
    ("Corrosion", "CubXL and OT-2, tray A", "auto",
     "in progress: impedance (a potentiostat requested); the ICP-MS station"),
    ("Long-term monitoring", "stream cameras only", "none",
     "open: repeat imaging of stored samples (the OpenFlexure array was dropped)"),
    ("Records", "cameras on every powered tray, in each bay and on each MiR250; MongoDB", "auto", ""),
]
TAGS = {"by hand:": (170, 60, 30), "in progress:": (190, 120, 0), "open:": (110, 114, 120)}
STATUS = {"auto": ("AUTOMATED HERE", (30, 120, 60)), "progress": ("IN PROGRESS", (190, 120, 0)),
          "none": ("NO STATION YET", (120, 124, 130)), "manual": ("BY HAND", (170, 60, 30))}


def _cell(d: ImageDraw.ImageDraw, xy, text: str, width: int, size: int, fill, row_h: float, bold=False):
    """`text` at `xy` in one line at `size`, or wrapped to two lines a little smaller if one line won't fit."""
    for sz in range(size, size - 4, -1):                # one line, up to 3 px smaller
        f = font(sz, bold)
        if d.textlength(text, font=f) <= width:
            d.text((xy[0], xy[1] + (size - sz) / 2), text, font=f, fill=fill)
            return
    for sz in range(size - 2, 13, -1):
        f = font(sz, bold)
        lines = wrap(d, text, f, width)
        if len(lines) <= 2:
            gap = min(row_h / 2 - 1, sz * 1.12)
            for k, ln in enumerate(lines):
                d.text((xy[0], xy[1] - 4 + k * gap), ln, font=f, fill=fill)
            return
    d.text(xy, text, font=font(14, bold), fill=fill)


def _tagged(d: ImageDraw.ImageDraw, xy, text: str, width: int, size: int, row_h: float):
    """The last column: its tag ("by hand:", "in progress:", "open:") bold in its colour, then the text in ink; on two
    lines, a little smaller, if one won't hold it."""
    if not text:
        d.text(xy, "-", font=font(size), fill=GREY)
        return
    tag = next((t for t in TAGS if text.startswith(t)), "")
    rest = text[len(tag):].strip()
    for sz in range(size, 13, -1):
        fb, fr = font(sz, True), font(sz)
        tw = d.textlength(tag + " ", font=fb) if tag else 0
        if tw + d.textlength(rest, font=fr) <= width:
            lines = [rest]
        else:
            lines = wrap(d, rest, fr, width - tw)
            if len(lines) > 2 or sz > size - 2:
                continue
        gap = min(row_h / 2 - 1, sz * 1.12)
        y0 = xy[1] - (4 if len(lines) > 1 else 0)
        if tag:
            d.text((xy[0], y0), tag, font=fb, fill=TAGS[tag])
        for k, ln in enumerate(lines):
            d.text((xy[0] + tw, y0 + k * gap), ln, font=fr, fill=INK)
        return
    d.text(xy, text, font=font(14), fill=INK)


def dal_table(path: Path):
    """DAL's 17 steps as one table, 1920 x 951 (the still area at 1080p): the station each runs at in this design,
    whether it is automated here, and what still takes a person or is open."""
    W, H = 1920, 951
    im = Image.new("RGB", (W, H), (246, 247, 249))
    d = ImageDraw.Draw(im)
    fh = font(26, bold=True)
    cols = [(40, "#"), (92, "DAL's step"), (450, "In this design"), (1125, "Status"), (1365, "By hand, in progress, or open")]
    y = 22
    d.text((40, y), "The alloy lab's 17 steps: what this design automates, and what still needs a person",
           font=font(36, True), fill=BLUE)
    y += 58
    for x, h in cols:
        d.text((x, y), h, font=fh, fill=GREY)
    y += 40
    d.line((40, y - 6, W - 40, y - 6), fill=BLUE, width=3)
    foot = 34
    row_h = (H - y - foot - 8) / len(DAL_STEPS)
    for i, (step, where, status, left) in enumerate(DAL_STEPS):
        yy = int(y + i * row_h)
        if i % 2 == 0:
            d.rectangle((30, yy - 3, W - 30, int(yy + row_h) - 3), fill=(235, 238, 244))
        d.text((40, yy + 2), f"{i + 1}", font=font(25, True), fill=BLUE)
        _cell(d, (92, yy + 4), step, 450 - 92 - 14, 25, INK, row_h)
        _cell(d, (450, yy + 5), where, 1125 - 450 - 16, 22, INK, row_h)
        label, colour = STATUS[status]
        fc = font(19, True)
        tw = d.textlength(label, font=fc)
        d.rounded_rectangle((1125, yy + 4, 1125 + tw + 20, yy + 4 + 30), radius=7, fill=colour)
        d.text((1135, yy + 8), label, font=fc, fill="white")
        _tagged(d, (1365, yy + 6), left, W - 40 - 1365, 20, row_h)
    n_auto = sum(s == "auto" for _, _, s, _ in DAL_STEPS)
    d.text((40, H - foot), f"{n_auto} of {len(DAL_STEPS)} steps automated here and shown (the chapter in parentheses). "
           "By hand: still a person's. In progress: being designed. Open: no design yet. A design, not yet built.",
           font=font(19), fill=GREY)
    im.save(path, optimize=True)



# ===================================================================================================== narration
NARRATION = HERE / "narration.json"
TTS_DIR = Path(tempfile.gettempdir()) / "longform_tts"
VOICE = os.environ.get("NARRATION_VOICE", "af_heart")         # Kokoro v1.0's best-rated voice
SPEED = float(os.environ.get("NARRATION_SPEED", "0.96"))
SR = 24000                                                    # Kokoro's rate
KOKORO = (os.environ.get("KOKORO_MODEL", "/tmp/kokoro/kokoro-v1.0.onnx"),
          os.environ.get("KOKORO_VOICES", "/tmp/kokoro/voices-v1.0.bin"))
LINE_RMS_DB = -18.0                                           # each line levelled to this RMS (dBFS), peaks under -1


# How the voice says what the text writes (round 14, run D). The lines are written as they should read in the
# subtitles (OT-2, SEM, MiR); Kokoro's front end (espeak) would say several of these as words ("ups", "sem", "my R")
# or with the wrong stress, so each line is spoken from phonemes: SAY respells a written form as text, then IPA gives
# the phonemes of the words no respelling fixes (Kokoro's phoneme input). Checked by ear and by machine with
# `python3 longform.py narration-check` (faster-whisper back, out/narration/check.json).
SAY = {
    "MiR250": "MiR two-fifty",                                          # MiR itself is in IPA, below
    "OT-2": "O T two", "UPS": "U P S", "SEM": "S E M", "BYU": "B Y U", "EDM": "E D M", "VLM": "V L M",
    "ICP-MS": "I C P M S", "ICP-OES": "I C P O E S", "ICP": "I C P", "CubXL": "Cub X L", "MX-Lab": "M X Lab",
    "UR12e": "U R twelve E", "UR10e": "U R ten E", "HNO3": "nitric acid", "HCl": "hydrochloric acid",
    "PTFE": "P T F E", "AirGradient": "Air Gradient",
    "aluminium": "aluminum",             # the voice is American (af_heart, en-us): the text keeps the repo's spelling
    "PTZ": "P T Z",                      # round 15: pan-tilt-zoom, said as letters
}
IPA = {   # espeak's own reading in the comment
    "MiR": "mˈiːɹ", "MiRs": "mˈiːɹz",    # Sterling: said "meer". espeak's "meer" (mˈɪɹ) came back as "mirror" before
    #                                    a consonant; the long vowel came back as "mere", and "MiR250" as "Mir 250"
    "potentiostat": "pətˌɛnʃiəstˈæt",    # espeak: pətˈɛntɪˌɑːstæt, "puh-TEN-tee-AH-stat"; Sterling: mispronounced
    "doser": "dˈoʊsɚ", "doser's": "dˈoʊsɚz", "dosers": "dˈoʊsɚz",     # espeak: dˈoʊzɚ, heard back as "dozer"
    "Vertiv": "vˈɜːtɪv",                 # espeak: vˈɜːɾɪv, heard back as "verdive"
    "depowdered": "dˌiːpˈaʊdɚd",         # espeak: dᵻpˈaʊdɚd, heard back as "de-powered"
    "Instron": "ˈɪnstɹɑːn",              # espeak: ɪnstɹˈɑːn
    "Stäubli": "ʃtˈɔɪbli",               # espeak: stˈɛʌbli
    # round 15 (the merged PRs' names, ready for any line that says them)
    "CombiTac": "kˈɑːmbitˌæk",           # espeak: kəmbˈaɪ tˈæk, "kum-BYE tack"
    "Haas": "hˈɑːs",                     # espeak: hˈɑːz; Haas Automation says "hahss"
    "IPA": "ˌaɪpˌiːˈeɪ",                 # isopropyl alcohol; espeak says it as a word, and "I P A" ends in the article
}
_TOK = None


def _word(keys):
    return re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, sorted(keys, key=len, reverse=True))) + r")(?![\w-])")


def spoken(text: str) -> str:
    """The line as the voice is to say it (SAY applied)."""
    return _word(SAY).sub(lambda m: SAY[m.group(1)], text)


def phonemes(text: str) -> str:
    """The line's phonemes for Kokoro: espeak's, except IPA's words."""
    global _TOK
    if _TOK is None:
        from kokoro_onnx.tokenizer import Tokenizer
        _TOK = Tokenizer()
    t, out, pos = spoken(text), [], 0
    for m in _word(IPA).finditer(t):
        if t[pos:m.start()].strip():
            out.append(_TOK.phonemize(t[pos:m.start()].strip()))
        out.append(IPA[m.group(1)])
        pos = m.end()
    if t[pos:].strip():
        out.append(_TOK.phonemize(t[pos:].strip()))
    return " ".join(out)


def tts(lines: list[dict]) -> list[Path]:
    """Each line spoken once by Kokoro from its phonemes (cached on voice, speed and phonemes) -> its WAV."""
    import soundfile as sf
    TTS_DIR.mkdir(parents=True, exist_ok=True)
    k, paths = None, []
    for ln in lines:
        ph = phonemes(ln["text"])
        key = hashlib.sha256(f"{VOICE}|{SPEED}|ph|{ph}".encode()).hexdigest()[:16]
        p = TTS_DIR / f"{key}.wav"
        if not p.exists():
            if k is None:
                from kokoro_onnx import Kokoro
                k = Kokoro(*KOKORO)
            y, sr = k.create(ph, voice=VOICE, speed=SPEED, lang="en-us", is_phonemes=True)
            assert sr == SR, sr
            sf.write(str(p), y, sr)
        paths.append(p)
    return paths


def _norm(s: str) -> str:
    """For comparing a line with what the recognizer heard: numbers as words, no punctuation, one spelling."""
    from num2words import num2words
    s = s.replace("°", " degrees").replace("%", " percent").replace("µm", " microns")
    s = re.sub(r"(\d),(\d{3})", r"\1\2", s)
    s = re.sub(r"\d+(\.\d+)?", lambda m: " " + num2words(float(m.group()) if "." in m.group() else int(m.group())) + " ",
               s)
    s = re.sub(r"(?<=[A-Z])-(?=[A-Z])", "", s)                    # ICP-MS -> ICPMS
    s = s.lower().replace("-", " ").replace("’", "'")
    for a, b in (("metre", "meter"), ("litre", "liter"), ("modelled", "modeled"), ("catalogue", "catalog"),
                 ("ageing", "aging"), ("colour", "color"), ("aluminium", "aluminum"), ("grey", "gray")):
        s = s.replace(a, b)
    s = re.sub(r"[^a-z' ]", " ", s)
    s = re.sub(r"'s\b|s'", "s", s)
    out, single = [], False
    for w in s.split():                                       # letters said one by one, written as one word: u p s = ups
        one = len(w) == 1 and w != "a"
        if one and single:
            out[-1] += w
        else:
            out.append(w)
        single = one
    return " ".join(out)


def narration_check(models=("base.en", "small.en"), new_since: str | None = None) -> list[dict]:
    """Every line spoken, then transcribed back by faster-whisper (two model sizes) and compared word by word with
    the spoken form (out/narration/check.json): the word error rate, each difference, and the words the recognizer
    was least sure of. A respelling or a phoneme fix goes in SAY or IPA. Also writes out/narration/lines.ogg, every
    line in order with a second between, to listen to. Round 15: `new_since`, a commit, checks only the lines whose
    text or phonemes differ from narration.json there, into check_new.json and lines_new.ogg."""
    import jiwer
    import soundfile as sf
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly
    lines = json.loads(NARRATION.read_text())
    tag = ""
    if new_since:
        old = json.loads(subprocess.run(["git", "show", f"{new_since}:./narration.json"], capture_output=True,
                                        text=True, cwd=HERE, check=True).stdout)
        before = {phonemes(x["text"]) for x in old}
        lines = [x for x in lines if phonemes(x["text"]) not in before]
        tag = "_new"
    paths = tts(lines)
    threads = int(os.environ.get("OMP_NUM_THREADS", "0") or 0)       # round 15: 1 beside the renders
    asr = {m: WhisperModel(m, device="cpu", compute_type="int8", cpu_threads=threads) for m in models}
    rows, audio = [], []
    for i, (ln, p) in enumerate(zip(lines, paths)):
        y, sr = sf.read(str(p), dtype="float32")
        audio += [y, np.zeros(sr, np.float32)]
        y16 = resample_poly(y, 2, 3).astype(np.float32)                 # 24 kHz -> 16 kHz
        ref = _norm(spoken(ln["text"]))
        row = dict(i=i, chapter=ln["chapter"], part=ln["part"], text=ln["text"], spoken=spoken(ln["text"]),
                   phonemes=phonemes(ln["text"]), seconds=round(len(y) / sr, 2))
        for m, model in asr.items():
            segs, _ = model.transcribe(y16, language="en", word_timestamps=True, beam_size=5)
            words = [w for sg in segs for w in sg.words]
            heard = "".join(w.word for w in words).strip()
            o = jiwer.process_words(ref, _norm(heard))
            diffs = [(a.type, " ".join(o.references[0][a.ref_start_idx:a.ref_end_idx]),
                      " ".join(o.hypotheses[0][a.hyp_start_idx:a.hyp_end_idx]))
                     for a in o.alignments[0] if a.type != "equal"]
            row[m] = dict(heard=heard, wer=round(o.wer, 3), diffs=diffs,
                          unsure=[(w.word.strip(), round(w.probability, 2)) for w in words if w.probability < 0.5])
        rows.append(row)
        print(f"{i:2d} {row['seconds']:5.1f} s  " + "  ".join(f"{m} {row[m]['wer']:.2f}" for m in asr) +
              "".join(f"  [{m}: {d}]" for m in asr for d in row[m]["diffs"][:3]), flush=True)
    dst = OUT / "narration"
    dst.mkdir(parents=True, exist_ok=True)
    (dst / f"check{tag}.json").write_text(json.dumps(dict(
        voice=f"Kokoro v1.0 {VOICE}, speed {SPEED}", recognizers=[f"faster-whisper {m}" for m in models],
        say=SAY, ipa=IPA, lines=rows), indent=1, ensure_ascii=False) + "\n")
    wav = Path(tempfile.gettempdir()) / "narration_lines.wav"
    sf.write(str(wav), np.concatenate(audio), SR)
    run("ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libopus", "-b:a", "32k", dst / f"lines{tag}.ogg")
    return rows


def clip_meta(src: str) -> dict | None:
    """The sub-steps of a clip as built: out/clean/<rel>.json beside a render in this pass's folder (out/<HD_DIR>/, or
    round 12's out/hd/: a VIZ3D_HD=1 scene writes its JSON to out/clean/), else out/<rel>.json; the first of them that
    has sub-steps (round 15: out/safety.json is the safety PR's report, its clip's sub-steps are in out/clean/)."""
    p = Path(src) if Path(src).is_absolute() else HERE / src
    rel, hd = Path(p.name), False
    for base, is_hd in [(d, True) for d in HD_DIRS] + [(OUT / "hd", True), (MP4, False)]:
        try:
            rel, hd = p.relative_to(base), is_hd
            break
        except ValueError:
            continue
    stem = str(rel.with_suffix(""))
    clean, plain = OUT / "clean" / f"{stem}.json", OUT / f"{stem}.json"
    for c in ((clean, plain) if hd else (plain, clean)):
        if c.exists():
            m = json.loads(c.read_text())
            if isinstance(m, dict) and m.get("substeps"):
                return m
    return None


_PROBE: dict = {}


def probe(path: Path) -> tuple[int, int, float]:
    """A video's width, height and frame rate as encoded (the rate a clip was drawn at: scene.py encodes every frame)."""
    key = str(path)
    if key not in _PROBE:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,r_frame_rate", "-of", "csv=p=0", str(path)], capture_output=True,
                           text=True)
        try:
            w, h, rate = r.stdout.strip().splitlines()[0].split(",")[:3]
            num, den = (rate.split("/") + ["1"])[:2]
            _PROBE[key] = (int(w), int(h), float(num) / float(den or 1))
        except (ValueError, IndexError, ZeroDivisionError):
            _PROBE[key] = (0, 0, 0.0)
    return _PROBE[key]


def _srt_s(stamp_: str) -> float:
    h, m, rest = stamp_.strip().split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


_R15OFF: dict | None = None


def r15_offsets() -> dict:
    """Round 16: {(clip under out/r15/, line text): seconds into that clip} where round 15's long-form spoke each line
    (its out/longform.json and out/longform_narration.srt at R15_COMMIT). A recovered clip is round 15's frames, so a
    line over it keeps round 15's timing exactly, whatever the clip's out/clean/ JSON says."""
    global _R15OFF
    if _R15OFF is not None:
        return _R15OFF
    _R15OFF = {}
    try:
        m15 = json.loads(subprocess.run(["git", "show", f"{R15_COMMIT}:./out/longform.json"], capture_output=True,
                                        text=True, cwd=HERE, check=True).stdout)
        srt = subprocess.run(["git", "show", f"{R15_COMMIT}:./out/longform_narration.srt"], capture_output=True,
                             text=True, cwd=HERE, check=True).stdout
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"  narration: round 15's placement not available ({e!r})", flush=True)
        return _R15OFF
    clips = [q for q in m15["parts"] if q["kind"] == "mp4"]
    for block in srt.strip().split("\n\n"):
        ls = block.splitlines()
        if len(ls) < 3 or " --> " not in ls[1]:
            continue
        t0, text = _srt_s(ls[1].split(" --> ")[0]), " ".join(ls[2:]).strip()
        for q in clips:
            if q["start_s"] <= t0 < q["start_s"] + q["seconds"]:
                src = q["src"]
                rel = src.split("out/r15/", 1)[1] if "out/r15/" in src else src.split("out/mp4/", 1)[-1]
                _R15OFF[(rel, text)] = t0 - q["start_s"]
                break
    return _R15OFF


def narration_times(meta: dict) -> list[dict]:
    """narration.json with each line's time in the video ("t"), from the parts as encoded. A clip line's sub-step is
    found by its index and checked against its label (by the label if the index moved)."""
    lines = json.loads(NARRATION.read_text())
    parts = meta["parts"]
    out = []
    for ln in lines:
        ch, part = ln["chapter"], ln["part"]
        if part == "card":
            r = next((r for r in parts if r["chapter"] == ch and r["kind"] == "card"), None)
            t = None if r is None else r["start_s"]
        elif part.endswith((".png", ".jpg")):
            r = next((r for r in parts if r["chapter"] == ch and r["kind"] == "still"
                      and (r.get("src") or "").endswith(part)), None)
            t = None if r is None else r["start_s"]
        elif part.endswith(".mp4"):                     # round 15: footage or another project's render, by its file
            r = next((r for r in parts if r["chapter"] == ch and r["kind"] in ("footage", "ext")
                      and (r.get("src") or "").endswith(part)), None)
            t = None if r is None else r["start_s"] + min(float(ln.get("at", 0.0)), max(0.0, r["seconds"] - 2.0))
        else:
            r = next((r for r in parts if r["chapter"] == ch and r["kind"] == "mp4"
                      and (r.get("src") or "").endswith(f"/{part}.mp4")), None)
            t = None
            # round 16: over a clip recovered from round 15's video, where round 15 spoke it (its offset included)
            src_r = (r or {}).get("src") or ""
            if r is not None and "out/r15/" in src_r:
                off = r15_offsets().get((src_r.split("out/r15/", 1)[1], ln["text"]))
                if off is not None:
                    out.append(dict(ln, t=round(r["start_s"] + off, 2)))
                    continue
            if r is not None:
                cm = clip_meta(r["src"])
                subs = (cm or {}).get("substeps", [])
                i = ln.get("substep")
                # round 14 (D): a line may anchor on a phrase of the sub-step's caption ("match"), which survives a
                # clip that gains or loses steps (chapter 2 was being reworked while its narration was rewritten)
                found = [j for j, sb in enumerate(subs) if ln.get("match") and ln["match"] in (sb.get("caption") or "")]
                if found:
                    i = found[0]
                elif ln.get("match"):
                    print(f"  narration: {part} has no caption with {ln['match']!r}; by sub-step index", flush=True)
                if not found and i is not None and i < len(subs) and subs[i]["label"] != ln.get("label"):
                    hit = [j for j, sb in enumerate(subs) if sb["label"] == ln.get("label")]
                    print(f"  narration: {part} sub-step {i} is now {subs[i]['label']!r}; "
                          f"{'using ' + str(hit[0]) if hit else 'kept'}", flush=True)
                    i = hit[0] if hit else i
                if cm and i is not None and i < len(subs):
                    t = r["start_s"] + subs[i]["start_frame"] / float(cm.get("fps", FPS))
                    t = min(t, r["start_s"] + r["seconds"] - 2.0)
                # round 15: "at", seconds into the clip, for a clip with no sub-steps (the 2-D floor_pass and floor_day,
                # base_cameras joined from two renders) or as the fallback when its sub-step can't be found
                if t is None and ln.get("at") is not None:
                    t = r["start_s"] + min(float(ln["at"]), max(0.0, r["seconds"] - 2.0))
        if t is None:
            print(f"  narration: no anchor for {ch}/{part}, line left out: {ln['text'][:60]}", flush=True)
            continue
        out.append(dict(ln, t=round(t + float(ln.get("offset", 0.0)), 2)))
    return sorted(out, key=lambda x: x["t"])


def srt_stamp(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


def narration_track(meta: dict, total: float, wav: Path) -> list[dict]:
    """Every line spoken and placed at its time (pushed later, with a warning, if the line before is still going),
    levelled to LINE_RMS_DB, into one mono WAV of the video's length; out/longform_narration.srt beside it."""
    import soundfile as sf
    rows = narration_times(meta)
    paths = tts(rows)
    track = np.zeros(int((total + 1.0) * SR), np.float32)
    free, placed = 0.0, []
    for r, p in zip(rows, paths):
        y, sr = sf.read(str(p), dtype="float32")
        rms, peak = float(np.sqrt(np.mean(y ** 2))) + 1e-9, float(np.abs(y).max()) + 1e-9
        y = y * min(10 ** (LINE_RMS_DB / 20) / rms, 0.89 / peak)        # never clipped: a spiky line gets less gain
        t = max(r["t"], free + 0.6)
        if t - r["t"] > 0.5:
            print(f"  narration: pushed {t - r['t']:.1f} s later: {r['text'][:60]}", flush=True)
        i0 = int(t * SR)
        n = max(0, min(len(y), len(track) - i0))
        track[i0:i0 + n] += y[:n]
        free = t + len(y) / SR
        placed.append(dict(r, t=round(t, 2), end=round(free, 2)))
    sf.write(str(wav), track, SR)
    (OUT / "longform_narration.srt").write_text("".join(
        f"{k + 1}\n{srt_stamp(r['t'])} --> {srt_stamp(r['end'])}\n{r['text']}\n\n" for k, r in enumerate(placed)))
    spoken = sum(r["end"] - r["t"] for r in placed)
    print(f"narration: {len(placed)} lines, {spoken / 60:.1f} min spoken of {total / 60:.1f} "
          f"({100 * spoken / total:.0f} %)", flush=True)
    return placed


# ===================================================================================================== the audit table


# round 15: a clip joined from separately audited renders is checked as the sum of their audits
AUDIT_PARTS = {"base_cameras": ["base_cameras_vlm", "base_cameras_atomizer"],
               # round 16: the fabrication tour is joined from its nine clips, each audited as it rendered
               "fabrication_tour": [f"fabrication/{k}" for k in ("metalone", "snowpod", "mprint", "meltio_m450",
                                                                  "form4", "form_wash", "form_cure", "stencil",
                                                                  "lumenpnp")]}
TWO_D = {"floor_pass", "floor_day"}        # 2-D animations (floor_pass.py, floor_day.py): no scene to check


def audit_rows() -> list[dict]:
    """Every 3-D clip in the plan with its collision audit (out/collisions/<clip>.json): frames checked, frames with
    an arm in collision, frames with anything moving in collision, the clip's size and the rate it was drawn at, and
    whether the clip and its audit are this pass's render or an earlier render reused."""
    # this round's audits: the reports that differ from the last commit before this round's renders (ROUND_BASE), or
    # didn't exist then (file times can't tell: merges and checkouts touch them). Round 15 started its renders on
    # ea5d9d5, after merging PRs #369-#379
    base = os.environ.get("ROUND_BASE", os.environ.get("ROUND12_BASE", "859d7678"))     # round 16 started on 859d7678
    st = subprocess.run(["git", "diff", "--name-only", base, "--", "out/collisions"], capture_output=True, text=True,
                        cwd=HERE).stdout.split()
    st += subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "out/collisions"], capture_output=True,
                         text=True, cwd=HERE).stdout.split()
    changed = {str(Path(x).relative_to("out/collisions")) if x.startswith("out/collisions/") else
               str(Path(x).relative_to("vertical-lab/out/collisions")) if x.startswith("vertical-lab/out/collisions/")
               else Path(x).name for x in st}
    rows, seen = [], set()
    for r in plan(quiet=True):
        if r["kind"] != "mp4" or r.get("missing") or "/dag/" in str(r["src"]):
            continue
        srcp = Path(str(r["src"]))
        for base in (HD, MP4):
            try:
                rel = srcp.relative_to(base).with_suffix("")
                break
            except ValueError:
                rel = Path(srcp.stem)
        name = srcp.stem
        if name in seen or name in TWO_D:
            continue
        seen.add(name)
        reps, fresh = [], True
        for part in AUDIT_PARTS.get(name, [str(rel)]):
            a = OUT / "collisions" / f"{part}.json"
            reps.append(json.loads(a.read_text()) if a.exists() else None)
            fresh = fresh and a.exists() and f"{part}.json" in changed
        have = [x for x in reps if x]

        def total(key, alt=None):
            vals = [x.get(key, x.get(alt) if alt else None) for x in have]
            return None if not have or any(v is None for v in vals) else sum(vals)
        w, h, rate = probe(srcp)
        cm = clip_meta(str(r["src"])) or {}
        rows.append(dict(clip=name, chapter=r["chapter"], this_pass=not r.get("earlier"), round15=bool(r.get("round15")),
                         seconds=round(r["seconds"], 1),
                         height=h, drawn_fps=round(rate) if rate else cm.get("fps"),
                         audit_this_round=bool(have) and fresh, fps=have[0].get("fps") if have else None,
                         frames_checked=total("frames_checked"), arm_frames=total("frames_with_collisions"),
                         all_frames=total("frames_with_collisions_all", "frames_with_collisions")))
    return rows


AUDIT_NOTES = {   # what the frames that remain are, where it is known (round 13: README, notes/arm_collisions.md, the notes files)
    "hip": "by design: the press drawn through a tray's outline, to show it doesn't fit",
    "setup_lab": "floor machines set down over their utility drops; the control box into its cabinet as it is built",
    "vlm_services": "the dock heads meeting the trays' plates as they mate",
    "alloy_prep": "the work itself: the holder lowered into the alumina on the cloth",
    "alloy_workflow": "the plate 6 mm into the depowdering box's rotor for one frame",
    "vlm_workflow": "by design: the holder grips its vial (round 11)",
    "cubxl_corrosion": "the work itself: the pipette tip into its well",
    "ded": "the work itself: the melt pool's glow on the part",
    # round 15 (the orchestrator): the tour clips' remaining "movers" frames are drawn effects, not contacts
    "fumehood": "by design: the drawn airflow's arrows overlapping each other",
    "fumehood_tray": "by design: the drawn airflow's arrows overlapping each other",
    "glovebox_tray": "by design: the powder stream drawn inside the jar as it pours",
    "safety": "by design: each B570 slid down into its 811 bracket as it is strapped in (a studio, no arm)",
    "atom_vacuum": "the crevice tool 1.5 mm into its station for one frame (8/10)",
    "alloy_print": "a fingertip on the sieving cell's frame by the funnel",
    "vlm_hookups": "the bay's dock head coming out through the bay's side wall, drawn without its opening",
    "bay_camera": "the vial 3 mm into its rack as it is set down",
    "atom_plate": "a fingertip 1.5 mm into the furnace for one frame",
    "scaleup": "the work itself: the saw through the brackets, the deposition's glow on the beads",
    "packaging": "the labeller's arm on the bag as it labels it",
    "upkeep_clip": "one frame of a moving part touching, under 3 mm",
    "atom_vacuum": "the crevice tool 3 mm into its station, the brush 0.3 mm, one frame each",
    # round 15
    "alloy_charge": "a fingertip 12 mm into the left base camera's case, setting a cup in the carrier",
    "alloy_atomize": "checker artifact: the held cup's cutaway half against its own whole copy, as the tong lowers it",
    "ot2_corrosion_prep": "the nozzle seated in its tip at pick-up (the tips are drawn solid)",
    "cubxl_corrosion": "the nozzle seated in its tip at pick-up (the tips are drawn solid)",
    "alloy_workflow": "the plate 3 mm into the depowdering box's rotor; a bar 6 mm into its trough",
    "setup_lab": "rigging: machines set down over their drops; the MiR250 onto its charger; tray B's racks sliding in",
    "meltio_m450": "the work itself: the deposition on the wall",
    # round 16
    "fabrication_tour": "the work itself: parts in the IPA and the UV glow, the laser in the bed, the wall's glow",
    "base_cameras": "",
}


def audit_table(path: Path):
    """audit_rows() as one table, 1920 wide (scrolled if tall), and <AUDIT_TAG>_summary.json beside it."""
    rows = audit_rows()
    for r in rows:
        # round 15: a note only where frames remain (the notes of fixed clips were stale)
        r["note"] = AUDIT_NOTES.get(r["clip"], "") if (r.get("all_frames") or r.get("arm_frames")) else ""
    path.with_name(f"{AUDIT_TAG}_summary.json").write_text(json.dumps(rows, indent=1) + "\n")
    W, row_h = 1920, 36
    H = 150 + row_h * len(rows) + 70
    im = Image.new("RGB", (W, H), (246, 247, 249))
    d = ImageDraw.Draw(im)
    d.text((40, 22), "Every clip in this video, checked frame by frame for collisions (FCL, round 11's strict rules)",
           font=font(34, True), fill=BLUE)
    cols = [(40, "Clip"), (440, "Rendered"), (760, "Frames checked"), (980, "Arm in collision"),
            (1200, "Anything moving"), (1420, "What the frames are")]
    y = 84
    fh = font(22, bold=True)
    for x, h in cols:
        d.text((x, y), h, font=fh, fill=GREY)
    y += 40
    d.line((30, y - 6, W - 30, y - 6), fill=BLUE, width=3)
    fb, fn = font(23), font(19)
    for i, r in enumerate(rows):
        yy = y + i * row_h
        if i % 2 == 0:
            d.rectangle((30, yy - 3, W - 30, yy + row_h - 3), fill=(235, 238, 244))
        d.text((40, yy), r["clip"], font=fb, fill=INK)
        # round 15: the clip's own height and the rate it was drawn at (720p30, 720p15), as the file has them
        size = f"{r['height']}p{r['drawn_fps'] or ''}" if r.get("height") else "-"
        # round 16: a clip recovered from round 15's video says so, with round 15's own audit
        d.text((440, yy), size + ("" if r["this_pass"] else ", round 15" if r.get("round15") else ", earlier"),
               font=fb, fill=INK if r["this_pass"] or r.get("round15") else GREY)
        fc = r["frames_checked"]
        d.text((760, yy), "-" if fc is None else f"{fc}" + ("" if r["audit_this_round"] else " (round 15)" if
                                                            r.get("round15") else " (earlier)"), font=fb,
               fill=INK if r["audit_this_round"] or r.get("round15") else GREY)
        for x, key in ((980, "arm_frames"), (1200, "all_frames")):
            v = r[key]
            d.text((x, yy), "-" if v is None else f"{v}", font=fb, fill=(20, 120, 50) if v == 0 else
                   (170, 60, 30) if v else GREY)
        note = r["note"] or ("" if not (r["all_frames"] or r["arm_frames"]) else f"out/collisions/{r['clip']}.json")
        while note and d.textlength(note, font=fn) > W - 1420 - 40:
            note = note[:-2].rstrip() + "…"
        d.text((1420, yy + 2), note, font=fn, fill=INK)
    d.text((40, H - 50), "Rendered: height and frames a second as drawn; round 15: that pass's render, cut from its "
           "video; earlier: a render from before it. "
           "Frames checked: every frame as shown, once however many parts touch. \"Anything moving\" adds trays, "
           "doors, MiRs, tables and people.", font=font(20), fill=GREY)
    im.save(path, optimize=True)
    return rows


# ===================================================================================================== the plan
def plan(quiet: bool = False) -> list[dict]:
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
                # round 15: a render of this pass that ffprobe can't read yet (still being written, or killed) is
                # passed over for the earlier one. Round 16: the first readable one of HD_DIRS (r16, then round 15's
                # recovered clips in r15), then out/mp4/
                hd, hd_s = HD / part[1], 0.0
                if part[1] not in ovr:
                    for dd in HD_DIRS:
                        cand = dd / part[1]
                        cs = duration(cand) if cand.exists() else 0.0
                        if cs:
                            hd, hd_s = cand, cs
                            break
                        if cand.exists() and not quiet:
                            print(f"  {cand.relative_to(OUT)}: not readable yet (still rendering?)", flush=True)
                src = Path(ovr[part[1]]) if part[1] in ovr else hd if hd_s else MP4 / part[1]
                secs = hd_s if src == hd else duration(src) if src.exists() else 0
                earlier = src.exists() and src.parent != (HD / part[1]).parent and part[1] not in ovr
                rows.append(dict(chapter=ch["key"], kind=kind, src=src, seconds=secs, label=part[2],
                                 missing=not src.exists() or not secs, earlier=earlier,
                                 round15=src.exists() and _under(src, R15),
                                 upscaled=src.exists() and 0 < probe(src)[1] < SIZE[1],
                                 was_s=duration(MP4 / part[1]) if src == hd and (MP4 / part[1]).exists() else None))
            elif kind == "ext":                         # round 15: another project's own render, out/mp4/ext/
                src = MP4 / part[1]
                rows.append(dict(chapter=ch["key"], kind=kind, src=src, seconds=duration(src) if src.exists() else 0,
                                 badge=part[2], caption=part[3], label=part[4], missing=not src.exists()))
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
        if r["kind"] == "mp4" and not r.get("missing"):    # round 15: the clip's own size and rate, and whose pass
            w, h, rate = probe(src)
            flag += f"  {h}p{rate:.0f}" + ("  round 15's, recovered" if r.get("round15") else
                                           "  earlier render" if r.get("earlier") else "")
            if r.get("was_s") and r["seconds"] < 0.5 * r["was_s"]:     # a render still writing reads as a short clip
                flag += f"  SHORT: out/mp4/'s is {r['was_s']:.1f} s; still rendering?"
        if r.get("caption") and not caption_fits(r):
            flag += "  CAPTION CUT (over two lines)"
        print(f"{stamp(t):>6} {r['seconds']:6.1f} s  {r['kind']:7s} {r['chapter']:11s} {rel}{flag}")
        if not r.get("missing"):
            t += r["seconds"]
    print(f"total {stamp(t)} ({t:.0f} s)")
    miss = [str(r.get("git") or r["src"].relative_to(OUT)) for r in rows if r.get("missing")]
    if miss:
        print(f"missing ({len(miss)}): " + ", ".join(miss))
    early = [str(r["src"].relative_to(OUT)) for r in rows if r["kind"] == "mp4" and r.get("earlier")]
    print(f"not in out/{HD.name}/ ({len(early)}, from round 15's video or out/mp4/): " + ", ".join(early))
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
        elif r["kind"] == "ext":
            ov = tmp / f"ext{i:03d}.png"
            ext_png(r["badge"], r["caption"], ov)
            cached([r["src"], ov, SIZE, FPS, "ext"], lambda d, r=r, ov=ov: normalise(r["src"], d, ov, band=True), out)
        else:
            cached([r["src"], SIZE, FPS, "mp4"], lambda d, r=r: normalise(r["src"], d), out)
        d = duration(out)
        src = r.get("git") or (str(r["src"].relative_to(HERE)) if r.get("src") else None)
        # round 15: an earlier render (out/mp4/, not this pass's out/<HD_DIR>/) and one smaller than the video, flagged
        record.append(dict(chapter=r["chapter"], kind=r["kind"], start_s=round(t, 2), seconds=round(d, 2),
                           src=src, label=r.get("label"), **({"earlier_render": True} if r.get("earlier") else {}),
                           **({"round15_recovered": True} if r.get("round15") else {}),
                           **({"upscaled": True} if r.get("upscaled") else {})))
        t += d
        parts.append(out)
        print(f"{stamp(t):>6}  {r['kind']:7s} {src or ''}", flush=True)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    dst = MP4 / f"{NAME}.mp4"
    silent = tmp / f"{NAME}_silent.mp4"
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
        "-movflags", "+faststart", silent)
    total = duration(silent)
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
    if NARRATION.exists() and os.environ.get("LONGFORM_NARRATION", "1") != "0":
        wav = tmp / "narration.wav"
        placed = narration_track(meta, total, wav)
        # EBU R128 to -16 LUFS (speech-gated, so the long silences don't count), true peak -1.5 dB
        run("ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-t", f"{total:.3f}",
            "-movflags", "+faststart", dst)
        meta["narration"] = dict(voice=f"Kokoro v1.0 {VOICE}, speed {SPEED}", lines=len(placed),
                                 spoken_s=round(sum(r["end"] - r["t"] for r in placed), 1),
                                 srt="out/longform_narration.srt")
    else:
        run("ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-c", "copy", "-movflags", "+faststart", dst)
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
# round 15: the round in the title, as round 13's upload had it, so it is told apart from the earlier uploads
TITLE = os.environ.get("LONGFORM_TITLE",
                       "The vertical cloud lab, start to finish: a Kardex VLM and the alloy route (3-D, round 16)")
# round 16: Sterling, 2026-11-26: "rerender and get on YouTube", no visibility named, so unlisted as this PR's uploads are
# unless asked (round 12 and 15 were asked for public); subscribers aren't notified of an unlisted video
PRIVACY = os.environ.get("LONGFORM_PRIVACY", "unlisted")
NOTIFY = os.environ.get("LONGFORM_NOTIFY", "0") not in ("0", "", "false", "no")


def description(meta: dict, commit: str) -> str:
    """The YouTube description: what the video is, what is new, the sources, and every chapter's timestamp. Round 15:
    shorter text, since 66 chapter lines take 3.1 kB of YouTube's 5,000 bytes; the budget leaves room only for the
    "Requested in" link (about 100 bytes) that youtube/yt_service.py appends."""
    early = [p for p in meta["parts"] if p.get("earlier_render")]
    head = ("A design study of an automated alloy lab at BYU's Vertical Cloud Lab: two Kardex vertical lift modules hold "
            "the instruments on powered trays, and UR12e arms (the UR10e, renamed in 2025) on MiR250 mobile bases work "
            "at their openings and at the floor machines. The alloy route runs from machining the charge cups through "
            "atomizing, printing, testing and characterization; then safety, upkeep, the floor and the waste, and the "
            "way from one alloy a day to ten.\n\n"
            "New in this version (round 16): the waste handled on screen, a bottle's trip to the fume hood and the "
            "powder-waste point at the atomizer with its vacuums; the machining cell on the floor; the CubXL's P300 in "
            "the powder test; the clips round 15 kept from earlier renders drawn again on the current lab; the set-up "
            "movie fixed and redrawn. Round 15's other clips are its own renders.\n\n"
            "A 3-D animation, not footage of a working lab: makers' published sizes and photos, our own designs where "
            "nothing exists yet, every arm move checked for collisions. Real footage, photos and data are badged; the "
            "voice is synthetic (Kokoro).\n\n"
            f"Code, notes and sources: https://github.com/{REPO}/tree/{commit}/vertical-lab\n"
            f"PR: {PR}\n\n")
    rates = sorted({round(probe(HERE / p["src"])[2]) for p in meta["parts"] if p["kind"] == "mp4"
                    and "/dag/" not in str(p["src"]) and Path(HERE / p["src"]).exists()} - {0})
    if rates:
        # round 15: say which clips were drawn when; the services and safety clips were copied into out/r15/ from
        # their round-14 and #379 renders, so the count of "earlier" parts alone undercounts them
        head += (f"{meta['size'][0]} x {meta['size'][1]} at 30 fps, the 3-D drawn at {rates[0]}" +
                 (f"-{rates[-1]}" if rates[-1] != rates[0] else "") + " frames a second: the chapters, the "
                 "turnaround and the whole-lab clips at 15, the instrument and fabrication clips at 30.\n\n")
    chap = "Chapters\n" + "".join(f"{c['stamp']} {c['title']}\n" for c in meta["youtube_chapters"])
    tail = ("\nThe real VLM: Sterling Baird, https://youtu.be/ck8QJhVqPiY . The atomizer footage is the lab's own (DAL "
            "#159, #219); the doser drop is powder-doser's own CAD render (PR #185, v10). Each notes file says which "
            "numbers are assumed.")
    budget = 4850                                     # 5000 is YouTube's limit; the triggering link is appended
    s = head + chap + tail
    while len(s.encode()) > budget and tail:
        tail = tail[: max(0, len(tail) - 200)]
        s = head + chap + tail
    cut = 70
    while len(s.encode()) > budget and cut > 24:      # still long: shorten the chapter titles, keep every timestamp
        chap = "Chapters\n" + "".join(f"{c['stamp']} {c['title'][:cut]}\n" for c in meta["youtube_chapters"])
        s = head + chap + tail
        cut -= 6
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
    from youtube.yt_service import with_triggering_link
    desc = with_triggering_link(description(meta, commit))
    body = {"snippet": {"title": TITLE[:100], "description": desc, "tags": Y.TAGS,
                        "categoryId": "28", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": PRIVACY, "selfDeclaredMadeForKids": False, "embeddable": True}}
    media = MediaFileUpload(str(dst), mimetype="video/mp4", chunksize=16 << 20, resumable=True)
    print(f"uploading {dst.name}: {PRIVACY}, subscribers {'notified' if NOTIFY else 'not notified'}", flush=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=NOTIFY)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploaded {status.progress():.0%}", flush=True)
    vid = resp["id"]
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rec["videos"].setdefault(f"{NAME}.mp4", []).append(dict(id=vid, sha256=digest, bytes=dst.stat().st_size,
                                                             commit=commit, uploaded=now, title=TITLE[:100],
                                                             privacy=PRIVACY, notified_subscribers=NOTIFY))
    Y.save_record(rec)
    (OUT / "longform_youtube.txt").write_text(desc + "\n")
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
    elif args and args[0] == "audit":                 # the audit table for the checks chapter
        for r in audit_table(OUT / "collisions" / f"{AUDIT_TAG}_table.png"):
            print(r)
    elif args and args[0] == "narration-check":       # speak every line and hear it back (faster-whisper)
        # round 15: narration-check [--models base.en,small.en] [--new <commit>]: only the lines changed since <commit>
        opt = dict(zip(args[1::2], args[2::2]))
        narration_check(tuple(opt.get("--models", "base.en,small.en").split(",")), opt.get("--new"))
    elif args and args[0] == "tts":                   # speak the narration into the cache ahead of the build
        print(len(tts(json.loads(NARRATION.read_text()))), "lines in", TTS_DIR)
    elif args and args[0] == "warm":                  # normalise the clips into the cache ahead of the build
        warm(args[1:])
    elif args and args[0] == "cards":                 # the cards alone, to /tmp, to read them
        for i, ch in enumerate(CHAPTERS, 1):
            card_image(f"Part {i} of {len(CHAPTERS)}", ch["title"], ch["card"]).save(f"/tmp/card_{ch['key']}.png")
        print("cards in /tmp/card_*.png")
    else:
        build()
