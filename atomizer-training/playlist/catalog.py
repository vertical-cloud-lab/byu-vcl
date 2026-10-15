"""What the atomizer videos on the BYU VCL channel should be called and say, and the playlist's order.

sync.py turns this into titles and descriptions (summary, chapters, then links to this folder on GitHub) and makes the
playlist follow VIDEOS from top to bottom. Edit here, then `python sync.py plan` and `python sync.py apply --ref <sha>`.

Each entry: id, kind (tutorial / stitch / recording / other), title (max 100 characters), was (the title it had before
this catalog), summary, optional status, chapters [(seconds, label)] (YouTube needs the first at 0 and each at least
10 s long), sources [(video id, seconds, label)] for clips a tutorial uses, context (when, who, what it was uploaded
as), and optional tags, category. A recording's title must also be its heading in ../timestamps.md, which
tools/make_timestamps.py builds from ../videos.json, so the two are kept the same.
"""
import os
import sys

TAGS = ["atomizer", "rePowder", "AMAZEMET", "ultrasonic atomization", "metal powder", "BYU Vertical Cloud Lab"]

PLAYLIST = {
    "title": "AMAZEMET rePowder atomizer at BYU VCL: installation, training and tutorials",
    "privacy": "unlisted",
    "description": (
        "The AMAZEMET rePowder ultrasonic atomizer at the BYU Vertical Cloud Lab: its delivery and installation, two days "
        "of training with Bartosz Kalicki of AMAZEMET (Sep 29–30 2026), preparing the charges, and the team's own runs "
        "since Oct 2 2026.\n\n"
        "In order:\n"
        "{tutorials}. Narrated tutorials: the machine and how it works, then before, during and after a run (draft 6, under review)\n"
        "{cups}. Tutorial: making the aluminum cups and plugs that carry powder into the furnace\n"
        "{stitch}. Every recorded step in the order of a run: one raw cut of all the recordings, 6 h 49 min, with chapters\n"
        "{recordings}. The recordings themselves, in the order they were made: delivery and installation (Jun–Sep), "
        "commissioning (Sep 28), training day 1 (Sep 29), training day 2 (Sep 30), dosing the next charge (Sep 30), the "
        "first run on our own (Oct 2) and the run of Oct 6\n\n"
        "Written up on GitHub:\n"
        "Operating procedure (SOP), every step linked to the moment of video it comes from: {sop}\n"
        "Timestamp log, transcripts, notes, 3D animations and the tutorials: {folder}\n"
        "Discussion: {pr}"),
}

B = "Bartosz Kalicki (AMAZEMET) in his own words, cut from the training recordings:"
T = {"wRc8p2_FnJo": "Training video 1", "naePD8o9_Gk": "Training video 2", "txH397FGTAU": "Training video 3",
     "1F9_4ccwhss": "Training video 4", "58wJ_Khwgyk": "Training video 5", "tfb4fsVNIFI": "Training video 6",
     "FDRTt68Vfvo": "Training video 7", "9kn-HhXCr1o": "Training video 9"}


def clips(*pairs):
    return [(vid, t, T[vid]) for vid, t in pairs]


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tutorials"))
from scripts import REAL as _REAL  # noqa: E402  the real-footage picks of the tutorials (drafts 5 and 6)

REAL_INTRO = "The real footage shown after each animation, from the recordings:"


def real(key):
    """[(video id, seconds, label)] of the real-footage picks tutorial `key` shows (drafts 5 and 6), in order (REAL in
    ../tutorials/scripts.py), for its description."""
    return [(REUPLOADED.get(r[1], r[1]), r[2], r[4]) for g in _REAL[key].values() for r in g]


REUPLOADED = {"VFycaxIq0Tc": "2sNAJX89b6s"}     # first upload -> its re-upload (same length), for description links


DRAFT6 = ("Draft 6, for review on GitHub (PR #255). The 3D animations now show the ultrasonic stack as the training "
          "assembles it: the connector, the plate hung by its end, the tungsten upper sonotrode. After each step's "
          "animation, the real action from the recordings (training, Oct 2 and Oct 6), stabilised and labelled, then the "
          "trainer explaining it. Synthetic narration (Microsoft Edge TTS, en-US-AndrewMultilingualNeural) over a "
          "CadQuery/PyVista model and draw.io outlines; clips subtitled with Whisper.")

TUTORIALS = [
    {"id": "t07lNjBmhRg", "kind": "tutorial", "seconds": 437,
     "was": "Atomizer tutorial 0: the machine and how it works (draft 6)",
     "title": "Atomizer tutorial 0: the machine and how it works",
     "summary": "What the rePowder ultrasonic atomizer is and how it turns a bar of metal into powder: a 3D tour of the "
                "machine (induction furnace, control frame, 57 L chamber, the ultrasonic stack in the door, the powder "
                "container and the utilities), how melt poured onto a plate vibrating at 40 kHz becomes round particles, "
                "each followed by the real thing in the lab, Bartosz Kalicki of AMAZEMET on wetting and particle size, the safety rules for every run, and how the "
                "machine got here.",
     "status": DRAFT6,
     "chapters": [(0, "The three parts of a run"),
                  (36, "The machine, in 3D"),
                  (114, "The machine, in the lab"),
                  (156, "How it makes powder"),
                  (214, "Making powder, in the lab"),
                  (266, "Bartosz on wetting and particle size"),
                  (334, "Safety, every run"),
                  (402, "How we got here: June to October 2026")],
     "sources_intro": B,
     "sources": clips(("naePD8o9_Gk", 1445), ("txH397FGTAU", 873), ("naePD8o9_Gk", 2321), ("58wJ_Khwgyk", 2552)),
     "real_intro": REAL_INTRO, "real": real("00-overview")},
    {"id": "R2m-PynLxlE", "kind": "tutorial", "seconds": 1046,
     "was": "Atomizer tutorial 1: before a run (draft 6)",
     "title": "Atomizer tutorial 1: before a run",
     "summary": "Everything before the furnace heats up, in four steps, in the order of a real run: the utilities (power, "
                "chilled water and the heat exchanger, compressed air, argon, the daily checks), the furnace (nozzle and "
                "crucible, the graphite nut threaded on from below through the open chamber door, insulation, "
                "thermocouple, sealing rod and lever, the charge), the chamber (splash disc, powder container, catch bowl) "
                "and last the ultrasonic stack (transducer, booster, sonotrode, connector, the plate hung by its end, upper sonotrode, the torques, the scan), mounted "
                "in the door before it closes. Each step: the outline, a narrated 3D animation, the same step in the "
                "lab, then the trainer explaining it.",
     "status": DRAFT6,
     "chapters": [(0, "Outline: four things before any heating"),
                  (34, "Step 1: the utilities"),
                  (85, "Step 1, in the lab"),
                  (249, "Step 2: the furnace and the charge"),
                  (371, "Step 2, in the lab"),
                  (604, "Step 3: the chamber and the container"),
                  (640, "Step 3, in the lab"),
                  (708, "Step 4: the ultrasonic stack, and closing the door"),
                  (812, "Step 4, in the lab")],
     "sources_intro": B,
     "sources": clips(("wRc8p2_FnJo", 86), ("wRc8p2_FnJo", 132), ("wRc8p2_FnJo", 2754), ("wRc8p2_FnJo", 2793),
                      ("1F9_4ccwhss", 100), ("58wJ_Khwgyk", 158), ("58wJ_Khwgyk", 224), ("58wJ_Khwgyk", 419),
                      ("58wJ_Khwgyk", 805), ("58wJ_Khwgyk", 1332)),
     "real_intro": REAL_INTRO, "real": real("01-before")},
    {"id": "4MyqZakpCtc", "kind": "tutorial", "seconds": 791,
     "was": "Atomizer tutorial 2: during a run (draft 6)",
     "title": "Atomizer tutorial 2: during a run",
     "summary": "The run itself, in four stages: the argon gas wash (vacuum and argon cycles cold, at 250 °C and at 500 °C, "
                "until oxygen is low and stable), heating and melting the charge (overshoot to drop the rods, then about "
                "800 °C, wait two minutes), the pour onto the vibrating plate (vibration, draining pressure, sealing rod "
                "up, turbo), and ending the pour within seconds. Each stage: the outline, a narrated 3D animation, the "
                "same stage in the lab (including three mistakes from Oct 2 and Oct 6), then the trainer explaining it.",
     "status": DRAFT6,
     "chapters": [(0, "Outline: the four stages of a run"),
                  (22, "Step 1: the gas wash"),
                  (89, "Step 1, in the lab"),
                  (264, "Step 2: heat and melt"),
                  (316, "Step 2, in the lab"),
                  (457, "Step 3: the pour"),
                  (533, "Step 3, in the lab"),
                  (715, "Step 4: end the pour"),
                  (735, "Step 4, in the lab")],
     "sources_intro": B,
     "sources": clips(("9kn-HhXCr1o", 205), ("9kn-HhXCr1o", 516), ("58wJ_Khwgyk", 2170), ("9kn-HhXCr1o", 810),
                      ("1F9_4ccwhss", 282), ("58wJ_Khwgyk", 3442), ("58wJ_Khwgyk", 3592), ("naePD8o9_Gk", 1408),
                      ("58wJ_Khwgyk", 3838), ("9kn-HhXCr1o", 1480), ("naePD8o9_Gk", 1922)),
     "real_intro": REAL_INTRO, "real": real("02-during")},
    {"id": "eNdmhnCl16s", "kind": "tutorial", "seconds": 561,
     "was": "Atomizer tutorial 3: after a run (draft 6)",
     "title": "Atomizer tutorial 3: after a run",
     "summary": "Everything after the pour, in four steps: the shutdown sequence, cooling down and opening the chamber "
                "(only below 400 °C, vented, masks on), collecting the powder (container valve, sieving, bagging and "
                "labelling) and cleaning for the next run (brush and vacuum for the same alloy, about an hour for a "
                "material change, one plate per alloy). Each step: the outline, a narrated 3D animation, the same step "
                "in the lab, then the trainer explaining it. It ends with the lessons from the team's first run on its "
                "own, Oct 2.",
     "status": DRAFT6,
     "chapters": [(0, "Outline: four steps after the pour"),
                  (21, "Step 1: the shutdown sequence"),
                  (39, "Step 1, in the lab"),
                  (77, "Step 2: cool down and open the chamber"),
                  (122, "Step 2, in the lab"),
                  (183, "Step 3: collect the powder"),
                  (205, "Step 3, in the lab"),
                  (276, "Step 4: clean and maintain"),
                  (359, "Step 4, in the lab"),
                  (496, "Lessons from the first run on our own")],
     "sources_intro": B,
     "sources": clips(("naePD8o9_Gk", 1891), ("naePD8o9_Gk", 2320), ("naePD8o9_Gk", 2339), ("tfb4fsVNIFI", 0),
                      ("naePD8o9_Gk", 3219), ("naePD8o9_Gk", 3051), ("58wJ_Khwgyk", 4057), ("FDRTt68Vfvo", 1071),
                      ("FDRTt68Vfvo", 1096), ("wRc8p2_FnJo", 530)),
     "real_intro": REAL_INTRO, "real": real("03-after")},
]

CUPS = {
    "id": "osx7moehRnE", "kind": "other",
    "was": "Making the aluminum cups and plugs for the rePowder atomizer (narrated tutorial)",
    "title": "Atomizer tutorial: making the aluminum cups and plugs",
    "category": None,
    # Written for issue #248 and kept as it is: its chapters, numbers and links are that tutorial's own.
    "body": """How to make the aluminum cups and vented plugs that carry powder into the rePowder ultrasonic atomizer at the BYU Vertical Cloud Lab: lathe footage of the first cups, the same steps animated from the CAD, the numbers to use, and what changes for the hydraulic-press versions.

0:00 Intro
0:28 Where the cups go
0:44 The bar
1:06 On the lathe
2:15 The cup, step by step
3:02 The plug, step by step
3:52 Where the #60 drill is
4:04 Why the air hole
4:35 The numbers
5:02 Four rules
5:42 Hydraulic-press versions
6:14 The drawing, and one request

Numbers are from the parts made so far (issue #222). Cups: 2.750 in long, turned from 3/4 in 6063 bar (McMaster 1640T16), with a 1/2 in drill 2.25 in deep. Plugs: each cup's measured hole + .0005 to .0008 in (the first ones were .508 in), .5625 in long, with a #60 air hole. About 8.7 g of powder per cup.

Links
This tutorial (issue #248): https://github.com/vertical-cloud-lab/byu-vcl/issues/248
Charge design (issue #222): https://github.com/vertical-cloud-lab/byu-vcl/issues/222
Drawing, CAD and animations (PR #232): https://github.com/vertical-cloud-lab/byu-vcl/pull/232
Lathe footage, Gage Erickson: https://youtube.com/shorts/z6rwmQW_3Vg
Narration text and build script: https://github.com/vertical-cloud-lab/byu-vcl/tree/edac3cd/atomizer-charge/tutorial

The CAD animations were made before the parts, so their out-of-date callouts have been corrected on screen. The narration is synthetic: Microsoft Edge TTS voice en-US-SteffanNeural.""",
}

STITCH_ABOUT = ("Every logged moment of the 26 atomizer recordings, reorganised into the order of a run and joined end to "
                "end. Nothing is narrated, stabilised or faded: the top bar names the source video, its day and the "
                "running source time; the yellow text is the timestamp log's note for the moment; the subtitles are "
                "Whisper. Stretches where nothing was logged (waiting for purges and melts, idle camera, chatter) are "
                "skipped, which is why the clips cut.")

STITCH = [
    {"id": "LpjXVa_TMXg", "kind": "stitch", "seconds": 12019,
     "was": "rePowder atomizer, every recorded step: Part 1, the machine, and before a run (raw cut, draft 1)",
     "title": "Atomizer, every recorded step (part 1 of 2): the machine, and before a run",
     "summary": "Part 1 of 2: installation, a tour of the machine, the HMI, materials and particle size, safety, and "
                "everything before a run (utilities, the ultrasonic stack, charge preparation, the furnace and the "
                "chamber). " + STITCH_ABOUT,
     "status": "Raw cut, draft 1, for review (PR #255). Part 2, during and after a run: "
               "https://www.youtube.com/watch?v=Nz2Y1O3ekfg",
     "chapters": [(0, "1. Installation and commissioning"), (528, "2. The machine: a tour of the module"),
                  (1432, "3. The HMI: pages, scan, program and pressure logic"),
                  (2388, "4. Materials, boosters and particle size"), (2658, "5. Safety and PPE"),
                  (2776, "6. Before a run: power-up and utilities"), (3504, "7. Before a run: the ultrasonic stack"),
                  (7489, "8. Charge preparation: cups, rods and dosing"),
                  (9325, "9. Before a run: furnace, nozzle, crucible and loading"),
                  (11290, "10. Before a run: chamber, plate guard, bowl and container")]},
    {"id": "Nz2Y1O3ekfg", "kind": "stitch", "seconds": 12557,
     "was": "rePowder atomizer, every recorded step: Part 2, during and after a run (raw cut, draft 1)",
     "title": "Atomizer, every recorded step (part 2 of 2): during and after a run",
     "summary": "Part 2 of 2: the gas wash and heating, the pour, shutdown and powder collection, cleaning, tools and "
                "consumables, and the lessons. " + STITCH_ABOUT,
     "status": "Raw cut, draft 1, for review (PR #255). Part 1, the machine and before a run: "
               "https://www.youtube.com/watch?v=LpjXVa_TMXg",
     "chapters": [(0, "11. During a run: gas wash and heating"), (5104, "12. During a run: the pour"),
                  (7561, "13. After a run: shutdown, cooldown, venting, powder out"),
                  (9632, "14. Cleaning between runs"), (11130, "15. Tools, consumables and spares"),
                  (12093, "16. Lessons, planning and support")]},
]

_TRAINING = ("the rePowder training at BYU, given by Bartosz Kalicki of AMAZEMET to Gage Erickson, Ronnie Guymon and "
             "Sterling Baird.")
DAY1 = "Recorded Tue Sep 29 2026, day 1 of " + _TRAINING
DAY2 = "Recorded Wed Sep 30 2026, day 2 of " + _TRAINING

# Not one of the 26 indexed videos (no transcript or notes yet), so its description comes from YouTube's auto-captions.
DELIVERY = {
    "id": "hbaD2ii6f3c", "kind": "delivery", "category": "28", "seconds": 301,
    "was": "Unboxing of smaller crate w/ Atomizer pieces",
    "title": "Atomizer delivery (Jun 15): unboxing the crate of accessories and spares",
    "summary": "Unpacking the smaller crate of atomizer parts, box by box: respirators and cartridges, ear protection, lab "
               "coats and gloves, fire-extinguishing powder, brushes, 17 and 18 mm wrench heads and the large torque "
               "wrench; crucibles, many insulating pieces, metal filters and graphite parts; rods, plates and small "
               "parts; the vacuum pump; boxes the narrator takes for powder collection containers; an oil filter, "
               "anti-static mats, fittings and tubes, and the heat exchanger. Everything looks intact.",
    "chapters": [(0, "PPE, tools and the torque wrench"), (91, "Crucibles, insulation, filters and graphite"),
                 (170, "Rods, plates and small parts"), (201, "Vacuum pump, containers, oil filter, mats"),
                 (246, "Fittings, tubes and the heat exchanger")],
    "context": "Uploaded Mon Jun 15 2026. It is not in the indexed set yet (no transcript or timestamp log), so this "
               "summary comes from YouTube's auto-captions.",
}

# Gage's videos of the Oct 6 run, titled as his daily run SOP asks ("Month/Day/Year Atomizer Run Video #", ../daily-sop.md)
# with a description after the colon. "docs" are extra links into this folder, checked by sync.py like the others.
RUN_OCT6 = [("The run, checked against the daily SOP and the room stream; what to check before the next run",
             "runs/2026-10-06.md"),
            ("Daily run SOP (Gage Erickson)", "daily-sop.md")]
PARAMS_261 = [("Run parameters (issue #261)", "https://github.com/vertical-cloud-lab/byu-vcl/issues/261")]
OCT6 = [
    # Re-uploaded on 2026-10-07 as 2sNAJX89b6s (same length, title and description); the first upload, VFycaxIq0Tc, was
    # made private and taken out of both playlists. The notes, transcript and timestamp log still cite VFycaxIq0Tc.
    {"id": "2sNAJX89b6s", "source_id": "VFycaxIq0Tc", "kind": "recording", "cite": "OCT6a",
     "was": "Oct 6 atomizer run, video 1",
     "title": "10/6/2026 Atomizer Run Video 1: onboarding Paul (orders, run log, SEM stubs)",
     "summary": "Gage Erickson introduces Paul, who is joining the team, to the lab and to his part of the daily run SOP. "
                "Only Gage and Ronnie operate the machine. Paul's list: order a clip for the T-piece and some tools "
                "(bigger brushes for the container, a stainless scraper, a tape measure) through ME orders, checked with "
                "Gage or Ronnie first; keep an Excel sheet of every run's parameters (plate type, amplitude, melt "
                "temperature, alloy); and make SEM stubs from each powder. No machine operation.",
     "context": "Recorded Tue Oct 6 2026, 13:07–13:27 MDT (placed on the room stream's clock), on Gage's collar phone.",
     "docs": RUN_OCT6, "links": PARAMS_261,
     "chapters": [(0, "Meeting Paul; who may operate the machine"), (195, "The list of things to help with"),
                  (296, "Charges, alloys and a jar of powder"), (402, "IPA on anything with powder on it"),
                  (463, "Ordering: a clip for the T-piece"), (531, "How to place an ME order"),
                  (896, "Tools: brushes, a scraper, a tape measure"), (1044, "The run sheet; organizing powders"),
                  (1077, "Making SEM stubs"), (1173, "Logging every run's parameters")]},
    {"id": "dnPs56DPt6I", "kind": "recording", "cite": "OCT6b",
     "was": "Oct 6th atomizer run, video 2",
     "title": "10/6/2026 Atomizer Run Video 2: furnace, ultrasonic scan, carbon-fibre plate, door closed",
     "summary": "Gage rebuilds the furnace and sets up the ultrasonic stack on his own: crucible and insulation into the "
                "coil, the thermocouple and the sealing rod, a scan at 40,000 Hz, a plate torqued to 50 N·m and tested "
                "(40,200 Hz, 20 W), then swapped for a carbon-fibre plate, “the cheapest”. A spray test through the "
                "open door, then the door is bolted shut. The stack's height under the nozzle is not checked here; in "
                "video 3 it turns out to be too high.",
     "context": "Recorded Tue Oct 6 2026, 14:06–14:24 MDT, on Gage Erickson's collar phone.",
     "docs": RUN_OCT6, "links": PARAMS_261,
     "chapters": [(0, "Crucible and insulation into the furnace"), (220, "Thermocouple and sealing rod"),
                  (338, "Ultrasonic scan: 40,000 Hz"), (392, "A plate on, torqued to 50"),
                  (582, "Test: 40,200 Hz, 20 W"), (786, "Swapping to a carbon-fibre plate"),
                  (985, "Spray test; the door bolted shut")]},
    {"id": "DWH1CEygsTI", "kind": "recording", "cite": "OCT6c",
     "was": "Oct 6 atomizer run, video 3",
     "title": "10/6/2026 Atomizer Run Video 3: gas wash, melt, pour (stack too high, vibration off)",
     "summary": "180 g of aluminium rods (#261 says Al 6067, probably 6063), wiped with IPA, go in beside the sealing "
                "rod. One gas wash takes the oxygen to 19 ppm; then 900 °C, 840 °C for two minutes, and 0.2 bar of pour pressure. The pour starts with the "
                "ultrasonic vibration off and the stack too high, so the stream hits the upper sonotrode and blobs off "
                "it. Pulled back three quarters of the way through, some melt atomizes: a small jar of powder, enough "
                "for SEM, and a bag of splats. Oxygen reads 121 ppm afterwards. Gage explains what went wrong, then the "
                "cooldown to 400 °C. A run to learn from: the run report below lists what to check before the next one.",
     "context": "Recorded Tue Oct 6 2026, 14:37–15:12 MDT, on Gage Erickson's collar phone. Powder code 4yghtr.",
     "docs": RUN_OCT6, "links": PARAMS_261,
     "chapters": [(0, "Charge wiped with IPA and loaded"), (317, "Gas wash"),
                  (1175, "Out in the lab: SEM samples, a sieve"), (1243, "Argon fill; oxygen 19 ppm"),
                  (1275, "Heating to 900 °C"), (1466, "Pour pressure 0.2 bar; oxygen 27 ppm"),
                  (1602, "Melted; 840 °C for two minutes"), (1700, "Scan, draining pressure, the checklist"),
                  (1775, "The pour"), (1955, "What went wrong: stack too high, vibration off"),
                  (2023, "Cooldown to 400 °C")]},
]

# The daily run SOP's own playlist: the team's runs, oldest first. The team adds each day's videos themselves; sync.py
# puts these first and leaves anything else where it is.
RUNS = {
    "title": "Atomizer Runs",
    "privacy": "unlisted",
    "ids": ["qYyT39D5Yzo", "of5-LhkX_VQ", "2sNAJX89b6s", "dnPs56DPt6I", "DWH1CEygsTI"],
    "description": (
        "The BYU Vertical Cloud Lab team's own runs of the AMAZEMET rePowder ultrasonic atomizer, oldest first, from the "
        "first one without the trainer (Oct 2 2026). Run videos are titled \"Month/Day/Year Atomizer Run Video #\", as the "
        "daily run SOP asks.\n\n"
        "Each run's parameters: https://github.com/vertical-cloud-lab/byu-vcl/issues/261\n"
        "Daily run SOP: {daily}\n"
        "Run reports, checked against the videos: {runs}\n"
        "Operating procedure (SOP), every step linked to the training video it comes from: {sop}\n"
        "Installation, training and tutorials, all in order: https://www.youtube.com/playlist?list={main}"),
}

RECORDINGS = [
    {"id": "Kv9DT3Vo0GE", "kind": "recording",
     "was": "Exciting Vertical Cloud Lab Construction Update!! Atomizer Will Be Installed Soon!",
     "title": "Atomizer installation (Sep 1): the lab enclosure under construction",
     "summary": "A walk-through of the lab enclosure under construction, before the atomizer arrived: the "
                "dehumidifier with a pump beside it, venting, chilled-water lines, and the transformer that powers "
                "the atomizer, too big for its planned spot. The narrator also shows the new slats, vents and "
                "lights (switches not yet working), cabinets, a big sink and a second sink, whiteboard space and "
                "large breaker boxes.",
     "context": "Uploaded Tue Sep 1 2026."},
    {"id": "07QOPRHIEvw", "kind": "recording",
     "was": "Placing the Atomizer!!!",
     "title": "Atomizer installation (Sep 3): the machine in its enclosure",
     "summary": "Installation update: the atomizer and the rest of the crate's contents are in the cleaned-up "
                "enclosure. The narrator explains what is still to come: chilled water down from the ceiling, "
                "argon from the tanks along the orange-taped wall, and commissioning in about two weeks.",
     "context": "Uploaded Thu Sep 3 2026, with the note “Spent some time cleaning the containment chamber out and "
                "unboxing the atomizer and crate to prepare for installation!”"},
    {"id": "cKwQbKdE22Q", "kind": "recording",
     "was": "Vacuum test",
     "title": "Vacuum test (Sep 8): clearing a small amount of powder",
     "summary": "Not the atomizer itself: in a half-face respirator and gloves, someone adds a little powder, "
                "connects a hose and runs a vacuum for 15 to 30 s “to get all of the powder out”, then checks and "
                "finds “no visible powder in there”. Which vacuum and which powder, and whether that counts as a "
                "pass, are not said.",
     "context": "Uploaded Tue Sep 8 2026."},
    {"id": "z6rwmQW_3Vg", "kind": "recording", "cite": "LATHE",
     "was": "Lathe turning aluminum crucibles for atomizer experiments",
     "title": "Atomizer charge prep (Sep 26): turning aluminum cups on the lathe",
     "summary": "Machine-shop clip of making the aluminum cups and plugs that hold powder for the custom-charge "
                "runs. Rod stock is band-sawn into three 3 in pieces (2.75 in plus 1/4 in for facing) and one of "
                "about 1 3/8 in for plugs; on the lathe the first cup is faced to exactly 2.75 in, centre-drilled "
                "and bored with a 1/2 in drill.",
     "context": "Gage Erickson's lathe footage, uploaded Sat Sep 26 2026. The narrated tutorial built on it: "
                "https://www.youtube.com/watch?v=osx7moehRnE"},
    {"id": "2wMgeI-E7zw", "kind": "recording", "cite": "SP",
     "was": "Atomizer training (sterling's phone)",
     "title": "Atomizer commissioning (Sep 28): walk-around of the utilities and consumables",
     "summary": "Bartosz Kalicki of AMAZEMET walks the team round the newly installed machine: the rear utility "
                "connections and the heat exchanger's first start-up, where cold facility water trips a "
                "water-too-cold fault (limit lowered from 10 to 7 °C) and coolant flow reads about 3 L/min against "
                "the 2 needed; then the control panels and accounts, transducer air cooling, plate life and cost, "
                "crucible coating, cleaning between alloys, and PPE.",
     "context": "Filmed on Sterling Baird's phone on the commissioning day, Mon Sep 28 2026 (inferred from “8:30 "
                "a.m. start tomorrow” and rods “to test on Wednesday”), and uploaded Sep 30.",
     "chapters": [(0, "Rear utilities and heat-exchanger start-up"),
                  (206, "Control panels and accounts; particle size"),
                  (448, "Transducer air cooling; plate life and cost"),
                  (632, "Crucible coating; cleaning between alloys"),
                  (781, "PPE, capped powder rods; next-day logistics")]},
    {"id": "wRc8p2_FnJo", "kind": "recording", "cite": "T1",
     "was": "Video 1 of atomizer training",
     "title": "Atomizer training video 1 (Sep 29): tour of the module, the HMI, furnace teardown",
     "summary": "Bartosz Kalicki (AMAZEMET) powers up the rePowder and shows the trainees the inside of the "
                "module: compressed air at about 4 bar (transducer cooling only), the two argon lines, cooling "
                "water, valves, the O2 sensor and the HEPA filter (check every 2 months), then vacuum pump and "
                "heat exchanger upkeep. On the HMI he covers the 40 kHz ultrasonic scan, O2 limits (best 40–50 "
                "ppm, not above 100), gas wash and the furnace pressures. He then strips the furnace, explains "
                "nozzle bores (0.5 mm standard, 0.7 mm for poor flow) and boron nitride coating, cleans and "
                "rebuilds it. No run happens.",
     "context": DAY1,
     "chapters": [(0, "Power-up: leave the transformer breaker on"),
                  (53, "Module tour: compressed air, argon and water"),
                  (285, "Pneumatics, valves, O2 sensor and HEPA filter"),
                  (592, "Ultrasonic generator, PLC, fuses and updates"),
                  (778, "Vacuum pump oil, heat exchanger water level"), (1091, "HMI accounts and settings"),
                  (1198, "Ultrasonic scan: 39–41 kHz, one wide peak"),
                  (1469, "Atomization screen: keep O2 under 100 ppm"),
                  (1553, "Chamber controls: gas wash, pressure control"),
                  (1748, "Furnace panel: green light, gas wash x5, turbo"),
                  (1983, "Program setup, heat ramp and service mode"),
                  (2099, "Furnace teardown: thermocouple to brass filter"),
                  (2357, "Nozzle bore: 0.5 mm standard, drill to 0.7 mm"),
                  (2519, "Crucible coating: boron nitride, night before"),
                  (2651, "Clean the seal, glass and graphite parts"),
                  (2754, "Reassemble: nozzle white side up, crucible, nut")]},
    {"id": "1F9_4ccwhss", "kind": "recording", "cite": "T4",
     "was": "Atomizer Training Video 4",
     "title": "Atomizer training video 4 (Sep 29): loading the furnace, cleaning the chamber",
     "summary": "Before the first run, Bartosz Kalicki loads the induction furnace with the trainees: insulation "
                "lined up with the thermocouple port, the sealing rod tip checked and the rod lowered, the rods "
                "added and the lid latched. He explains that the coil heats the graphite, which heats the charge, "
                "and why iron and nickel are not intended: the plates would not survive and those metals react "
                "with graphite. Then chamber cleaning: vacuum first, then brushes, paper and alcohol, a "
                "stainless-steel scraper, and the swing-out cone.",
     "context": DAY1,
     "chapters": [(0, "Insulation, thermocouple and sealing rod"),
                  (158, "Induction heating; why not iron or nickel"),
                  (271, "Load the rods and close the furnace lid"),
                  (340, "Cleaning the chamber: brushes, scraper, cone")]},
    {"id": "58wJ_Khwgyk", "kind": "recording", "cite": "T5",
     "was": "Atomizer Training Video 5",
     "title": "Atomizer training video 5 (Sep 29): the first run, start to finish",
     "summary": "The first rod run through the machine, start to finish, with Bartosz Kalicki explaining each "
                "step. He fits the powder container, splash guard and catch bowl, builds the stack (1:1.5 booster, "
                "titanium connector rod, tungsten-alloy sonotrode, carbon-fiber plate) at 65/60/50 N·m and scans "
                "it at just over 40 kHz. Furnace and chamber purges run cold, at 250 °C and at 500 °C; a 1000 °C "
                "set point melts the aluminum rods, held at about 790 °C for 2 min, then poured. Rising oxygen "
                "bends the stream; the chamber is opened at about 400 °C.",
     "context": DAY1,
     "chapters": [(0, "Powder container, splash guard, catch bowl"), (397, "Transducer care and booster choice"),
                  (627, "Connector rod, sonotrode, carbon-fiber plate"),
                  (805, "Torque the stack: 65 and 60 N·m in a vise"),
                  (1143, "Transducer cover; bench scan at 40 kHz"),
                  (1486, "Stack in housing; plate 50 N·m; wet test; aim"),
                  (1843, "Purge plan; chamber overpressure; O2 sensor"),
                  (2027, "Furnace gas wash (5 purges); leak warning"),
                  (2254, "Chamber vacuum, protective gas, O2 reading"), (2510, "Heat to 250 °C and purge"),
                  (2880, "Purge at 500 °C, then melting pressure"),
                  (3169, "Set 1000 °C to melt, hold 790 °C, wait 2 min"),
                  (3590, "The pour onto the carbon-fiber plate"), (3731, "Stop sequence; why the stream wandered"),
                  (3861, "Cooldown: open at 400 °C, off at 100 °C"),
                  (4131, "Q&A: plate reuse, glowing plates, plate wear"),
                  (4427, "Off topic: respirator storage, lab layout"),
                  (4576, "Slag, vent the chamber, brush the powder")]},
    {"id": "tfb4fsVNIFI", "kind": "recording", "cite": "T6",
     "was": "Atomizer Training Video 6",
     "title": "Atomizer training video 6 (Sep 29): closing the powder container",
     "summary": "A 49-second clip at the powder container after a run. Bartosz Kalicki says to close the container "
                "once all the powder is brushed in: argon is heavy and stays at the bottom, so it keeps a "
                "semi-protective atmosphere even when opened cold. To clean it properly after a run, open it "
                "fully. Most of the clip is silent.",
     "context": DAY1},
    {"id": "Pk0K5sBz-sQ", "kind": "recording", "cite": "TA",
     "was": "Atomizer training",
     "title": "Atomizer training (Sep 29): right after a pour, brushing powder and cooling down",
     "summary": "Recorded right after a pour; the first four minutes have almost no speech. Bartosz Kalicki "
                "(AMAZEMET) has the trainees brush the powder back inside for reuse, remove any big solidified "
                "piece, and wipe the tube, especially at the bottom, before closing. Removing slag and checking "
                "the nozzle must wait because the furnace is still at 150 °C. He adds that the cooling water stays "
                "on until about 100 °C, can stop earlier when the crucible is empty, and must stay on if a big "
                "unpoured chunk is left.",
     "context": DAY1,
     "chapters": [(0, "Mostly silent footage after the pour"), (236, "Brush powder back in, wipe the tube"),
                  (379, "Still 150 °C: slag and nozzle check must wait"),
                  (517, "When to stop the cooling water (100 °C)")]},
    {"id": "naePD8o9_Gk", "kind": "recording", "cite": "T2",
     "was": "Atomizer Training Video 2",
     "title": "Atomizer training video 2 (Sep 29): a run, from heating to powder out",
     "summary": "Bartosz Kalicki (AMAZEMET) coaches the trainees through an Al 4047 run, from heating to powder "
                "out. The setpoint is still at about 1000 °C from before, so the rods melt before the usual 250 °C "
                "and 500 °C purges; they purge at once, drop to 800 °C, wait 2 min and rescan the stack (just over "
                "40 kHz). A trainee pours with the sealing rod up and turbo pressure, Bartosz explains wetting and "
                "the quick shutdown, then the chamber is vented, opened in masks and lab coats, and the powder "
                "brushed into the container. Long stretches are off-topic chat.",
     "context": DAY1,
     "chapters": [(0, "Start heating; why the gauge stops at −0.8 bar"),
                  (202, "Setpoint left at 1000 °C: purge right away"),
                  (348, "Normal routine: purge at 250 °C, then 500 °C"),
                  (635, "Chamber purge, then heat once O2 is low"),
                  (880, "Rods slump: reduce to 800 °C, wait 2 min"),
                  (1088, "Rescan the ultrasonic stack: just over 40 kHz"),
                  (1152, "Pour: ultrasonic start, sealing rod up, turbo"),
                  (1348, "Crucible empty: shutdown, then wetting theory"),
                  (1489, "Set 250 °C for next time; drill 0.7 mm nozzles"),
                  (1613, "Off topic: other installs, minerals, stocks"),
                  (1815, "Recap: turbo, shutdown order, plate damage"),
                  (1996, "Wait for 400 °C; off topic: mining, nuclear"),
                  (2247, "Vent the chamber, masks and lab coats on"),
                  (2564, "Brush the powder down into the container"),
                  (2709, "Remove the plate; chamber cleaning, no speech"),
                  (3032, "Powder into the container; cooling water off"),
                  (3219, "Close the container valve and take it out")]},
    {"id": "txH397FGTAU", "kind": "recording", "cite": "T3",
     "was": "Atomizer Training Video 3",
     "title": "Atomizer training video 3 (Sep 29): 1:1 booster and a Mo plate, the last run of the day",
     "summary": "Bartosz Kalicki and the trainees clean up after the previous run, reassemble the furnace and fit "
                "the 1:1 booster with a molybdenum-alloy plate, checked by a scan and a liquid pattern test. After "
                "purges cold, at 250 °C and at 500 °C, a 1000 °C set point melts the rods and 780–790 °C is held; "
                "he advises starting near 90 % amplitude. The Mo plate cracks during the pour, yet atomizes better "
                "once a piece breaks off. The day ends with the powder, the case for wider Mo plates, and "
                "shutdown: everything off at about 100 °C.",
     "context": DAY1,
     "chapters": [(0, "Cleaning up after the previous run"), (300, "Off topic: the missing torque-wrench tip"),
                  (552, "Reassembly, low-oxygen lesson, Mo-alloy plate"),
                  (723, "Scan double peak; liquid pattern test"), (786, "Booster plan; particle size for printing"),
                  (972, "1:1 booster in; cold furnace purge"), (1113, "Theory: particle size by metal; DED vs LPBF"),
                  (1217, "Chamber vacuum and protective gas"), (1407, "Heat to 250 °C and purge"),
                  (1815, "Purge at 500 °C; plate wear check"), (1960, "Melting pressure; can purging be automated?"),
                  (2101, "Set 1000 °C to melt the rods"), (2313, "Lower to 780–790 °C; amplitude 80–90 %; scan"),
                  (2498, "The pour: Mo plate cracks, then works better"),
                  (2764, "Powder check; the case for wider Mo plates"),
                  (2991, "Shutdown at 100 °C; program locked above 80 °C")]},
    {"id": "w02MRlZhpNk", "kind": "recording",
     "was": "Dehumidifier troubleshooting",
     "title": "Atomizer room (Sep 29): dehumidifier troubleshooting",
     "summary": "Facility troubleshooting, not atomizer operation: up at the enclosure dehumidifier, the narrator "
                "finds the 24 V control terminals shorted together and hears a click, sees that the pump next to "
                "it seems unconnected, and does not think the breaker has tripped. Turning the humidistat knob "
                "gives more clicks, but the clip ends without the unit confirmed running.",
     "context": "Recorded Tue Sep 29 2026, during the training."},
    {"id": "prj_xgeuQtM", "kind": "recording", "cite": "DOSE1",
     "was": "nzyjn0 AlSi10Mg-Al6063 dosing session",
     "title": "Atomizer charge prep (Sep 29): dosing AlSi10Mg for charge nzyjn0 (no narration)",
     "summary": "A fixed phone view of the lab's powder doser and balance, preparing charge nzyjn0: AlSi10Mg "
                "powder dosed into an Al 6063 cup for the Sep 30 custom-charge atomizer run. There is almost no "
                "speech (“Let's see how this looks” at 0:17). Gloved hands lay out tools, work on a tube and set a "
                "tube on the balance; the view then stays unchanged from about 24:00 to 52:00, after which the "
                "draft shield is lifted off.",
     "context": "Recorded Tue Sep 29 2026. The cup became the charge of the Sep 30 custom-charge run; the powders "
                "are logged in issue #249: https://github.com/vertical-cloud-lab/byu-vcl/issues/249",
     "chapters": [(0, "Powder doser and balance on the bench"), (420, "Paper and tools laid out at the back"),
                  (660, "Gloved hands work on an upright tube"), (840, "At the powder doser; a tube on the balance"),
                  (1440, "Long unchanged view: dosing or waiting"),
                  (3180, "Back at the doser; draft shield lifted off"),
                  (3480, "An arm at the powder doser once more")]},
    {"id": "u-KjR5TENN4", "kind": "recording",
     "was": "The expert cleaning the atomizer, pov",
     "title": "Atomizer training (Sep 30): the expert cleaning the atomizer, first-person view",
     "summary": "A body-worn, first-person recording of the trainer cleaning the atomizer after a run (the "
                "uploader calls him “the expert”; Bartosz Kalicki, inferred from his orange gloves). There is no "
                "narration and no usable speech, so the chapters name what the frames show. In orange gloves he "
                "works under the chamber with a printed sheet, inside the chamber and cone with a long tool, at a "
                "bench of tools, at the view port, at the door seal with a wash bottle, and with paper at the top "
                "of the powder container. Training videos 2 and 4 narrate the same kind of cleaning.",
     "context": "Uploaded Wed Sep 30 2026, mid-morning on day 2 of the training.",
     "chapters": [(0, "Under the chamber with a printed sheet"),
                  (300, "Inside the chamber and cone with a long tool"),
                  (450, "A domed stainless part, then the tool bench"),
                  (630, "View port, then a wash bottle at the door seal"),
                  (900, "Paper to the bin; powder container top; HMI")]},
    {"id": "LSQmxwmlTkQ", "kind": "recording",
     "was": "Drill press, number 70 bit, graphite nozzle",
     "title": "Atomizer nozzle prep (Sep 30): drilling a graphite nozzle with a #70 bit",
     "summary": "Machine-shop clip: a graphite nozzle is held on the drill-press table and under the chuck to open "
                "its bore with a #70 wire-gauge bit (nominally 0.028 in, about 0.71 mm). There is no narration, "
                "only a few words of chatter. Per the issue comment linked below, two nozzles were drilled: one "
                "“botched just a bit”, one that “looks pretty nice”.",
     "context": "Uploaded Wed Sep 30 2026.",
     "links": [("Photos of the two drilled nozzles (issue #222)",
                "https://github.com/vertical-cloud-lab/byu-vcl/issues/222#issuecomment-5914976661")]},
    {"id": "f8KL31PN8bA", "kind": "recording",
     "was": "Cartridge cleaning",
     "title": "Atomizer training (Sep 30): cleaning a filter cartridge; a second scan peak",
     "summary": "Bartosz Kalicki, in a respirator and gloves, cleans a filter cartridge and its valve body at the "
                "bench after a run, mostly without words for the first six minutes, then flushes it with "
                "isopropanol and blows paper lint off the seal with compressed air; deeper cleaning waits, as the "
                "next charge is aluminum again. At the HMI he reads a second peak on the ultrasonic scan as "
                "resonance from the 1:1 booster with the wider plate, and explains why piezo stacks must not be "
                "over-tightened. It ends with housekeeping and the AlSi10Mg sample cup for the next run.",
     "context": DAY2,
     "chapters": [(0, "Cleaning the cartridge valve at the bench"),
                  (413, "IPA flush, then compressed air on the seal"),
                  (534, "Refitting the cartridge; deep clean deferred"),
                  (777, "Second scan peak, booster choice, piezo stacks"),
                  (901, "Masks, housekeeping and consumables storage"),
                  (957, "The AlSi10Mg sample cup and next steps")]},
    {"id": "TFpU4uqVF9c", "kind": "recording", "cite": "RUN1",
     "was": "nzyjn0 atomization AlSi10Mg-Al6063",
     "title": "Atomizer training (Sep 30): first custom charge, AlSi10Mg in an Al 6063 cup",
     "summary": "Bartosz Kalicki narrates the first custom-charge run: charge nzyjn0, AlSi10Mg powder in an Al "
                "6063 cup. Vacuum and argon gas washes alternate with temperature steps until the oxygen reading "
                "is low and stable. He overshoots the temperature to homogenize the mixed charge, still sees a "
                "leftover spot with a thicker oxide layer, lowers to about 800 °C and pours at the previous day's "
                "low pour pressure under manual pressure control. The pour is over in under a minute, then melting "
                "pressure, sealing rod down, generator stop.",
     "context": DAY2 + " Probably the same run as Training video 9, filmed from another camera (the SOP infers this "
                       "from "
                "matching times): https://www.youtube.com/watch?v=9kn-HhXCr1o. The uploader's note: “also was "
                "mentioned that irregular and larger particles are better for compaction and oxidation, "
                "respectively”.",
     "chapters": [(0, "Gas wash (purge): vacuum, then argon backfill"), (243, "Higher temperature, more gas washes"),
                  (606, "Oxygen low and stable: heat to homogenize"),
                  (891, "Leftover spot with a thicker oxide layer"), (1037, "Decide to pour; lower to about 800 °C"),
                  (1154, "Pour at low pressure, then sealing rod down")]},
    {"id": "FDRTt68Vfvo", "kind": "recording", "cite": "T7",
     "was": "Atomizer Training Video 7",
     "title": "Atomizer training video 7 (Sep 30): reversing the booster, rebuilding the stack",
     "summary": "Between two runs, Bartosz Kalicki talks the trainees through taking the ultrasonic stack apart "
                "and flipping the 1:1.5 booster to 1.5:1, which lowers the amplitude for finer powder. He frees a "
                "seized stud with two jammed M10 nuts, gives torques of 65, 60 and 50 for the three joints and "
                "shows how to set the torque wrench. The rebuilt stack scans just under 40 kHz, goes back in with "
                "the plate and is scanned with water on the plate; plates last about 1–3 runs. From 2:20 to 14:20 "
                "the talk is mostly lab layout.",
     "context": DAY2,
     "chapters": [(0, "Plan between runs; vacuuming the chamber"), (140, "Off topic: lab layout, moving a cabinet"),
                  (630, "Cabinet to become a desiccant dry box"), (683, "Off topic: camera ideas, shelving"),
                  (859, "Teardown starts: taking the plate off"),
                  (1007, "Why it resonated; keep one plate per alloy"),
                  (1134, "Removing the stack: cable, clamp, transducer"),
                  (1312, "Booster theory: 1:1.5 vs reversed 1.5:1"),
                  (1556, "Off topic: camera, paper towels, gloves"),
                  (1768, "Flipping the booster; freeing a seized stud"),
                  (1982, "Housing on; 1.5:1 end up toward the chamber"),
                  (2148, "Torque 65/60/50 and setting the torque wrench"),
                  (2425, "Bench test: scan; frequency under 40 kHz"),
                  (2587, "Installing the stack; naming its parts"),
                  (2739, "Mounting the plate: connector first, torque 50"),
                  (2969, "Final scan with water; why plates crack")]},
    {"id": "HTlUrAr5HVU", "kind": "recording", "cite": "T8",
     "was": "Atomizer Training Video 8",
     "title": "Atomizer training video 8 (Sep 30): nozzles, and reassembling the furnace",
     "summary": "Gage Erickson reassembles the furnace between runs while Bartosz Kalicki advises. Gage shows a "
                "fresh 0.7 mm graphite nozzle and a smaller one he machined (said as “0.05”; 0.5 mm inferred), and "
                "Bartosz recommends screwing the nozzle into the crucible before fitting the holder nut. They seat "
                "the insulation and thermocouple, scrape aluminium off the graphite sealing rod while protecting "
                "its tip, keep one consumable set per alloy, close the furnace just tight enough to seal and clean "
                "the lid before loading.",
     "context": DAY2,
     "chapters": [(0, "Nozzle sizes; nozzle into the crucible first"),
                  (224, "Insulation in; cleaning the sealing rod"),
                  (520, "Closing the furnace; laser-pointer aiming idea"), (658, "Cleaning the lid before loading")]},
    {"id": "9kn-HhXCr1o", "kind": "recording", "cite": "T9",
     "was": "Atomizer Training Video 9",
     "title": "Atomizer training video 9 (Sep 30): a full run, then consumables and plates",
     "summary": "Gage Erickson runs the machine while Bartosz Kalicki explains each step: gas wash, heat exchanger "
                "and generator on, purges at 250 °C and 500 °C, then 850 °C to melt the charge, back to 800 °C and "
                "a 2-minute wait to mix. With the reverse booster the melt pours too fast for the low amplitude "
                "and part of it drips through un-atomized, so Bartosz recommends a 0.5 mm nozzle and a slow, "
                "controlled pour for fine powder. He then tours the consumables and plate materials, the training "
                "certificate is signed, and he gives closing advice.",
     "context": DAY2 + " Probably the same run as the nzyjn0 custom-charge video, filmed from another camera (the SOP "
                "infers this from matching times): https://www.youtube.com/watch?v=TFpU4uqVF9c",
     "chapters": [(0, "Gas wash: furnace, then chamber; 150 mbar"),
                  (117, "Heat exchanger on; heat to 250 °C and purge"),
                  (372, "Purge again, then 500 °C; why two stages"), (641, "Low pour pressure; heat to 850 °C"),
                  (809, "Melting cues: temperature dip, faster beeping"),
                  (941, "Back to 800 °C; wait 2 min to overheat and mix"),
                  (1174, "The pour: vibration on, open the sealing rod"),
                  (1299, "Stop the pour; next time a smaller nozzle"),
                  (1378, "Fine powder: small nozzle, low amplitude"),
                  (1708, "Powder out, nozzle check; charge size"),
                  (1951, "Consumables: insulation, sealing rods, nozzles"),
                  (2118, "Consumables: thermocouples, seals, filters"),
                  (2315, "Plates: carbon fibre, Ti64, Nb, Mo, steel"),
                  (2625, "Certificate; advice on practice and the pour"),
                  (2770, "Cooldown below 100 °C; condensation; plans")]},
    {"id": "BxA7Z9Fliss", "kind": "recording",
     "was": "Claude ping for dosing Al 4047",
     "title": "Atomizer charge prep (Sep 30): asking Claude on GitHub to dose Al 4047",
     "summary": "Not atomizer operation: a mostly silent screen recording in which the narrator opens a GitHub "
                "pull request where Claude can be pinged and copies a saved prompt asking for another powder-doser "
                "run of Al 4047. The rest of the clip stays on the pull request without commentary.",
     "context": "Recorded Wed Sep 30 2026."},
    {"id": "QXSj0j1OqL8", "kind": "recording",
     "was": "Dosing Al 4047 powder",
     "title": "Atomizer charge prep (Sep 30): preparing an Al 4047 dose (no narration)",
     "summary": "A fixed phone view of the lab's powder doser bench, with no narration and no speech: per the "
                "upload's title, Al 4047 powder is being dosed, as charge preparation for the atomizer. Gloved "
                "hands set out an empty tube, place an item in the draft shield on the balance, hold a small tube "
                "upright at the back of the bench, and fit a tube (the powder cartridge, inferred) to the doser "
                "above the balance, where it then sits still.",
     "context": "Recorded Wed Sep 30 2026.",
     "chapters": [(0, "Doser bench; an empty tube set out"), (240, "An item placed in the draft shield"),
                  (720, "A small tube held upright at the back"),
                  (1020, "A tube fitted to the powder doser by hand"),
                  (1260, "Hand at the balance; a clear cover lifted")]},
    {"id": "dXRB7c6GeDw", "kind": "recording", "cite": "DOSE2",
     "was": "Claude ping and troubleshooting for dosing Al 4047",
     "title": "Atomizer charge prep (Sep 30): dosing Al 4047 with Claude; a stall and a clog",
     "summary": "A narrated phone screen recording of the GitHub pull request in which Claude runs the lab's "
                "powder doser, dosing 8 g of the team's own atomized Al 4047 powder. The dose stalls near 3 g, "
                "Claude fixes a telemetry MemoryError on the doser's Pico, and larger particles then clog the "
                "auger nozzle, so Claude finishes at bulk tilt only. It ends at about 8 g, with notes on a larger "
                "auger channel, a slower final tilt-back and the one-sided solenoid mount. Charge preparation for "
                "the atomizer, not atomizer operation.",
     "context": "Recorded Wed Sep 30 2026. The dose became the charge of the Oct 2 run (inferred).",
     "chapters": [(0, "Dose stalls near 3 g; replaying the livestream"),
                  (201, "Claude's reply, with side talk from a visitor"),
                  (523, "MemoryError on the doser's Pico; Claude's fix"),
                  (1098, "Waiting on Claude, with off-topic chat"), (1391, "Larger particles clog the auger nozzle"),
                  (1785, "Still a ways from 4.5 with the clog"),
                  (2339, "Claude's plan: bulk tilt only (clog-tolerant)"),
                  (3103, "Reaching the target, pretty much spot on"),
                  (3204, "Lessons: slower tilt-back, solenoid mount flex"),
                  (3302, "8 g dosed; a small amount for the 6063 tube"),
                  (3533, "Finished: balance reading and Claude's report")]},
    {"id": "qYyT39D5Yzo", "kind": "recording", "cite": "OCT2a",
     "was": "Atomizer Fri Oct 2 pt1",
     "title": "Atomizer, first run on our own (Oct 2), part 1: startup, plates and loading",
     "summary": "Startup and loading, narrated by a team member with Ronnie Guymon helping. Utilities go on while "
                "a chilled-water fitting still leaks, and a phone checklist is read: oil, water level, argon at 8 "
                "bar, chilled water, air valve. They identify the unlabeled plates and choose molybdenum for "
                "smaller particles, fetch metric 17 and 18 mm wrenches to mount the upper sonotrode, see light "
                "through the new nozzle and skip the transducer housing this time. The chamber is then reopened "
                "for the frequency scan: one valley, one peak.",
     "context": "Recorded Fri Oct 2 2026: the team's first run without the trainer.",
     "chapters": [(0, "Utilities on and the startup checklist"),
                  (106, "Identifying the plates; choosing molybdenum"),
                  (391, "Aluminum build-up on the tungsten-alloy part"),
                  (444, "Power on; upper sonotrode; metric wrenches"),
                  (608, "Nozzle check, HMI login, wait for wrenches"),
                  (855, "Sonotrode torqued; transducer housing skipped"),
                  (1041, "Chamber closed; reading the SOP purge steps"),
                  (1200, "Reopen the chamber for the frequency scan")]},
    {"id": "of5-LhkX_VQ", "kind": "recording", "cite": "OCT2b",
     "was": "Atomizer run Oct 2 part 2",
     "title": "Atomizer, first run on our own (Oct 2), part 2: gas wash, pour and cooldown",
     "summary": "Purge, heat, pour and cooldown. After loading and lowering the sealing rod, the team gas-washes "
                "at room temperature, 250 °C and 500 °C; with oxygen in the low 20s they skip a fourth wash. They "
                "heat to 830 °C (the trainer used 850, then 800), set amplitude to about 90 and pour pressure to "
                "0.17 bar, and confirm a pure molybdenum plate. When the sealing rod opens, most of the charge "
                "pours un-atomized: the pressure was too high and the plate too far from the nozzle. Then "
                "shutdown, opening only below 400 °C.",
     "context": "Recorded Fri Oct 2 2026: the team's first run without the trainer.",
     "chapters": [(0, "Setup and wipe-down before loading"), (180, "Loading with tweezers; sealing rod down"),
                  (243, "Set 250 °C; gas wash at room temperature"), (545, "Generator start; gas wash at 250 °C"),
                  (786, "Heat to 500 °C; gas wash at 500 °C"), (1070, "Oxygen in the low 20s; heat to 830 °C"),
                  (1212, "Off topic: livestreaming with Meta glasses"),
                  (1316, "Melting; plug length; pour pressure 0.17 bar"),
                  (1494, "Amplitude about 90; pure molybdenum plate"),
                  (1585, "Pour: most of the charge is not atomized"),
                  (1661, "Shutdown; open the chamber below 400 °C")]},
] + OCT6

VIDEOS = TUTORIALS + [CUPS] + STITCH + [DELIVERY] + RECORDINGS

_DRAFT = ("This is draft {n} of tutorial {t}; draft 6, linked above, replaced it after review on "
          "https://github.com/vertical-cloud-lab/byu-vcl/pull/255.")
SUPERSEDED = [
    {"id": "p6jlgTJEOw4", "by": "t07lNjBmhRg", "why": _DRAFT.format(n=1, t=0),
     "was": "rePowder atomizer at BYU VCL, tutorial 0: installation and training overview (draft)",
     "title": "[superseded] Atomizer tutorial 0, draft 1 (installation and training overview)"},
    {"id": "eKH7y4JgJD8", "by": "R2m-PynLxlE", "why": _DRAFT.format(n=1, t=1),
     "was": "rePowder atomizer at BYU VCL, tutorial 1: before a run (draft)",
     "title": "[superseded] Atomizer tutorial 1, draft 1 (before a run)"},
    {"id": "cGxBFZyFmCY", "by": "4MyqZakpCtc", "why": _DRAFT.format(n=1, t=2),
     "was": "rePowder atomizer at BYU VCL, tutorial 2: during a run (draft)",
     "title": "[superseded] Atomizer tutorial 2, draft 1 (during a run)"},
    {"id": "wPzP6I3jT5w", "by": "eNdmhnCl16s", "why": _DRAFT.format(n=1, t=3),
     "was": "rePowder atomizer at BYU VCL, tutorial 3: after a run (draft)",
     "title": "[superseded] Atomizer tutorial 3, draft 1 (after a run)"},
    {"id": "uVVeTokW3Us", "by": "t07lNjBmhRg", "why": _DRAFT.format(n=2, t=0),
     "was": "rePowder atomizer at BYU VCL, tutorial 0: the machine and how it works (draft 2)",
     "title": "[superseded] Atomizer tutorial 0, draft 2 (the machine and how it works)"},
    {"id": "qiBB0lIXUDM", "by": "R2m-PynLxlE", "why": _DRAFT.format(n=2, t=1),
     "was": "rePowder atomizer at BYU VCL, tutorial 1: before a run (draft 2)",
     "title": "[superseded] Atomizer tutorial 1, draft 2 (before a run)"},
    {"id": "sagBBb78pVQ", "by": "4MyqZakpCtc", "why": _DRAFT.format(n=2, t=2),
     "was": "rePowder atomizer at BYU VCL, tutorial 2: during a run (draft 2)",
     "title": "[superseded] Atomizer tutorial 2, draft 2 (during a run)"},
    {"id": "50j8N8YyDxU", "by": "eNdmhnCl16s", "why": _DRAFT.format(n=2, t=3),
     "was": "rePowder atomizer at BYU VCL, tutorial 3: after a run (draft 2)",
     "title": "[superseded] Atomizer tutorial 3, draft 2 (after a run)"},
    {"id": "raIcdus1lI0", "by": "t07lNjBmhRg", "why": _DRAFT.format(n=3, t=0),
     "was": "rePowder atomizer at BYU VCL, tutorial 0: the machine and how it works (draft 3)",
     "title": "[superseded] Atomizer tutorial 0, draft 3 (the machine and how it works)"},
    {"id": "KwY4KTY1UdI", "by": "R2m-PynLxlE", "why": _DRAFT.format(n=3, t=1),
     "was": "rePowder atomizer at BYU VCL, tutorial 1: before a run (draft 3)",
     "title": "[superseded] Atomizer tutorial 1, draft 3 (before a run)"},
    {"id": "79QQtmIm0JM", "by": "4MyqZakpCtc", "why": _DRAFT.format(n=3, t=2),
     "was": "rePowder atomizer at BYU VCL, tutorial 2: during a run (draft 3)",
     "title": "[superseded] Atomizer tutorial 2, draft 3 (during a run)"},
    {"id": "TvaFwSyqaog", "by": "eNdmhnCl16s", "why": _DRAFT.format(n=3, t=3),
     "was": "rePowder atomizer at BYU VCL, tutorial 3: after a run (draft 3)",
     "title": "[superseded] Atomizer tutorial 3, draft 3 (after a run)"},
    {"id": "-yxOIJfhs80", "by": "t07lNjBmhRg", "why": _DRAFT.format(n=4, t=0),
     "was": "Atomizer tutorial 0: the machine and how it works",
     "title": "[superseded] Atomizer tutorial 0, draft 4 (the machine and how it works)"},
    {"id": "xpkbazHT_7M", "by": "R2m-PynLxlE", "why": _DRAFT.format(n=4, t=1),
     "was": "Atomizer tutorial 1: before a run",
     "title": "[superseded] Atomizer tutorial 1, draft 4 (before a run)"},
    {"id": "Jex6lDcERUM", "by": "4MyqZakpCtc", "why": _DRAFT.format(n=4, t=2),
     "was": "Atomizer tutorial 2: during a run",
     "title": "[superseded] Atomizer tutorial 2, draft 4 (during a run)"},
    {"id": "VWa33SEvFJw", "by": "eNdmhnCl16s", "why": _DRAFT.format(n=4, t=3),
     "was": "Atomizer tutorial 3: after a run",
     "title": "[superseded] Atomizer tutorial 3, draft 4 (after a run)"},
    {"id": "nPIPvVh38Dw", "by": "osx7moehRnE",
     "why": "This first upload's narration said each cup went into its own bag, over footage showing them in one bag, and "
            "gave .508 in as a measured diameter rather than the target.",
     "was": "Making the aluminum cups and plugs for the rePowder atomizer (narrated tutorial)",
     "title": "[superseded] Atomizer tutorial: making the aluminum cups and plugs (first upload)"},
    {"id": "qwopusVSwf4", "by": "UaMVgjwOtrU",
     "why": "This is draft 1 (33 s) of the slide clip of a whole run; draft 3 (45 s), linked above, is slower, shows the "
            "melt being stirred, keeps the powder inside the chamber and shows the rebuilt ultrasonic stack, after review on "
            "https://github.com/vertical-cloud-lab/byu-vcl/pull/255.",
     "was": "Atomizer slide clip: from loading to powder in 33 seconds (draft 1)",
     "title": "[superseded] Atomizer slide clip: from loading to powder in 33 seconds (draft 1)"},
    {"id": "Pnwe5B1YUnM", "by": "t07lNjBmhRg", "why": "This is draft 5 of tutorial 0. It showed the ultrasonic stack wrongly assembled, with the plate's centre on a stud at the end of the stack; draft 6, linked above, shows it as the training does: the connector, the plate hung by its hole near one end, and the tungsten upper sonotrode. Review: https://github.com/vertical-cloud-lab/byu-vcl/pull/255.", "was": "Atomizer tutorial 0: the machine and how it works", "title": "[superseded] Atomizer tutorial 0, draft 5 (the machine and how it works)"},
    {"id": "sWx-k8CyCsk", "by": "R2m-PynLxlE", "why": "This is draft 5 of tutorial 1. It showed the ultrasonic stack wrongly assembled, with the plate's centre on a stud at the end of the stack; draft 6, linked above, shows it as the training does: the connector, the plate hung by its hole near one end, and the tungsten upper sonotrode. Review: https://github.com/vertical-cloud-lab/byu-vcl/pull/255.", "was": "Atomizer tutorial 1: before a run", "title": "[superseded] Atomizer tutorial 1, draft 5 (before a run)"},
    {"id": "1rqkZO2DOhc", "by": "4MyqZakpCtc", "why": "This is draft 5 of tutorial 2. It showed the ultrasonic stack wrongly assembled, with the plate's centre on a stud at the end of the stack; draft 6, linked above, shows it as the training does: the connector, the plate hung by its hole near one end, and the tungsten upper sonotrode. Review: https://github.com/vertical-cloud-lab/byu-vcl/pull/255.", "was": "Atomizer tutorial 2: during a run", "title": "[superseded] Atomizer tutorial 2, draft 5 (during a run)"},
    {"id": "UqYrbrsJSsU", "by": "eNdmhnCl16s", "why": "This is draft 5 of tutorial 3. It showed the ultrasonic stack wrongly assembled, with the plate's centre on a stud at the end of the stack; draft 6, linked above, shows it as the training does: the connector, the plate hung by its hole near one end, and the tungsten upper sonotrode. Review: https://github.com/vertical-cloud-lab/byu-vcl/pull/255.", "was": "Atomizer tutorial 3: after a run", "title": "[superseded] Atomizer tutorial 3, draft 5 (after a run)"},
    {"id": "j9QcpcG8EVI", "by": "UaMVgjwOtrU", "why": "This is draft 2 of the slide clip of a whole run (44 s). It showed the ultrasonic stack wrongly assembled, with the plate's centre on a stud at the end of the stack; draft 3 (45 s), linked above, shows it as the training does: the connector, the plate hung by its hole near one end, and the tungsten upper sonotrode. Review: https://github.com/vertical-cloud-lab/byu-vcl/pull/255.", "was": "Atomizer slide clip: from loading to powder in 44 seconds (draft 2)", "title": "[superseded] Atomizer slide clip: from loading to powder in 44 seconds (draft 2)"},
    {"id": "8lBR11fgznI", "by": "6LTmL_qm2Eo", "why": "This is draft 1 of the slide clip of the ultrasonic stack. It showed the ultrasonic stack wrongly assembled, with the plate's centre on a stud at the end of the stack; draft 2, linked above, shows it as the training does: the connector, the plate hung by its hole near one end, and the tungsten upper sonotrode. Review: https://github.com/vertical-cloud-lab/byu-vcl/pull/255.", "was": "Atomizer slide clip: the ultrasonic stack and the door (draft 1)", "title": "[superseded] Atomizer slide clip: the ultrasonic stack and the door (draft 1)"},
    {"id": "21oFnNmzd3E", "by": "JAXKQTDq2zg", "why": "This is draft 1 of the slide clip of the pour. It showed the ultrasonic stack wrongly assembled, with the plate's centre on a stud at the end of the stack; draft 2, linked above, shows it as the training does: the connector, the plate hung by its hole near one end, and the tungsten upper sonotrode. Review: https://github.com/vertical-cloud-lab/byu-vcl/pull/255.", "was": "Atomizer slide clip: the pour (draft 1)", "title": "[superseded] Atomizer slide clip: the pour (draft 1)"},
    {"id": "86K-EHhtPp8", "by": "u4MORr_PZbI", "why": "This is draft 1 of the slide clip of loading the furnace. Draft 2, linked above, puts the stack's housing in the chamber door where the rebuilt ultrasonic stack needs it. Review: https://github.com/vertical-cloud-lab/byu-vcl/pull/255.", "was": "Atomizer slide clip: loading the furnace (draft 1)", "title": "[superseded] Atomizer slide clip: loading the furnace (draft 1)"},
    {"id": "VFycaxIq0Tc", "by": "2sNAJX89b6s", "why": "This is the first upload of Oct 6 video 1. On 2026-10-07 it was made private and re-uploaded as the video linked above, at the same length; the notes, transcript and timestamp log on GitHub still cite this id, at the same times.", "was": "10/6/2026 Atomizer Run Video 1: onboarding Paul (orders, run log, SEM stubs)", "title": "[superseded] 10/6/2026 Atomizer Run Video 1 (first upload)"},
]
