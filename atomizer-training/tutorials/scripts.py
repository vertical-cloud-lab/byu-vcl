"""Narration and segment lists for the tutorial videos (edit here, then run build_tutorials.py).

Every tutorial has the same shape, so that the four hang together: a title, the draw.io outline of its steps built up step
by step, then for each step the outline again with that step highlighted, the 3D animation of the step under synthetic
narration, and the trainer explaining it in his own words. A closing card points to the next tutorial.

Segment forms:
  ("title", title, subtitle, narration)
  ("outline", diagram, narration)                     diagram = diagrams/<diagram>.png (draw.io export)
  ("build", diagram, [sentence0, sentence1, ...])     the outline built up like a PowerPoint slide: sentence 0 over the step
                                                      boxes alone (diagrams/<diagram>_build0.png), then each step's details
                                                      appear (<diagram>_build<k>.png, a hard cut) as sentence k starts, so
                                                      sentence k should name step k. One sentence per build image.
  ("anim", name, narration)                           name = ../viz3d/out/mp4/<name>.mp4; narration a string, or a list with
                                                      one sentence per sub-step of the animation (../viz3d/out/<name>.json)
  ("clip", video_id, start_seconds, duration_seconds, speaker)   snapped to sentence boundaries by clip_words.py
  ("card", title, subtitle, narration)
  ("real", video_id, in_seconds, out_seconds, caption, opts)    the action itself, from real-footage.md: see R() and REAL below

Synthetic narration: Microsoft Edge TTS en-US-AndrewMultilingualNeural at 1x. Human narration: Bartosz Kalicki (AMAZEMET),
in the clips.
"""
VOICE = "en-US-AndrewMultilingualNeural"
# Whisper's mishearings in the clips, corrected in the burned-in subtitles only (the cached words stay as heard)
FIXES = {"newtonometers": "newton meters", "your production": "hearing protection", "the bias": "a vise",
         "transistor": "transducer", "argol": "argon", "ceiling rod": "sealing rod", "or other dramatica.": "or other pneumatics.",
         "in a cruise of 250": "in increments of 250", "fiber powder": "finer powder", "band valve": "vent valve",
         "the clay heats up": "the plate heats up", "pull more": "pour more", "The graph is crucible": "the graphite crucible"}
B = "Bartosz Kalicki, AMAZEMET"

TUTORIALS = {
    "00-overview": {
        "title": "Atomizer tutorial 0: the machine and how it works (draft 6)",
        "segments": [
            ("title", "The rePowder ultrasonic atomizer", "Tutorial 0 · the machine, how it makes powder, and what a run looks like",
             "The rePowder ultrasonic atomizer, at the BYU Vertical Cloud Lab."),
            ("build", "00-overview", [
                "A run on the atomizer has three parts, and each has its own tutorial.",
                "Before a run: the utilities, the furnace and its charge, the chamber, and last the ultrasonic stack.",
                "During a run: the argon gas wash, the melt, and the pour onto the vibrating plate.",
                "After a run: shutdown, cool-down, collecting the powder, and cleaning. This overview introduces the machine "
                "itself and how it turns a bar of metal into powder.",
            ]),
            ("anim", "00_machine", [
                "This is the rePowder ultrasonic atomizer at BYU, modeled from the training videos and AMAZEMET's documents.",
                'On top is the induction furnace: a stainless body holding the coil, the crucible and the insulation, under a lid with a window.',
                'The melting control panel and the main switch are on the blue frame, which also houses the induction generator and the electronics, and the touchscreen on its swing arm runs the pressures, the gas and the ultrasonics.',
                'Below the furnace is the fifty-seven liter atomization chamber, with a view port at the front, a door on the left held by three star-knob bolts, and an underside that slopes down to the outlet.',
                'The ultrasonic unit rides in the door: the transducer outside, under its cover, and the sonotrode and plate inside, under the furnace nozzle.',
                'The sloped underside and a short cone take the powder down through a valve into the container, which is clamped on by its flange.',
                'Around it are the utilities: argon, the vacuum pump, compressed air for the transducer, and the heat exchanger on the chilled water.',
                'Cut in half, the whole path shows: crucible, sealing rod and nozzle above the plate, and the cone down to the container.',
            ]),
            ("anim", "06_pour", [
                'Here is how it makes powder. An induction coil heats the graphite crucible, and the graphite heats the metal inside it.',
                'Below the furnace, a plate on the ultrasonic stack vibrates forty thousand times a second.',
                'A little argon overpressure in the furnace pushes on the melt.',
                'When the sealing rod lifts off the nozzle, a thin stream of melt falls onto the plate.',
                'A short extra push of pressure helps the first melt wet the cold plate.',
                'Once the melt wets the plate, the vibration breaks it into droplets, which fly off and freeze into round particles in the argon.',
                'The powder falls down the cone into the container.',
                'A pour takes two or three minutes, with an operator at the window the whole time.',
                'When the crucible is empty, the run is over.',
            ]),
            ("clip", "naePD8o9_Gk", 1445.9, 39.5, B),
            ("clip", "txH397FGTAU", 873.1, 28.0, B),
            ("card", "Safety, every time",
             "Gloves and lab coat · full-face respirator whenever powder is exposed · hearing protection while ultrasonics run · "
             "open the chamber only below 400 °C · the door stays locked until the pressure is vented",
             "A few rules apply to every run. Gloves and a lab coat, because hands go inside the chamber. A full-face respirator "
             "whenever powder is exposed. Hearing protection while the ultrasonics run, even when the noise does not bother you. "
             "Open the chamber only below four hundred degrees, because hot graphite burns in air. And the door stays locked "
             "while the chamber is under pressure or vacuum, so vent it first."),
            ("clip", "naePD8o9_Gk", 2321.3, 10.2, B),
            ("clip", "58wJ_Khwgyk", 2552.7, 14.8, B),
            ("card", "How we got here",
             "Delivered June 2026 · room renovated over the summer: power, chilled water, cabinets · installed Sep 28 · "
             "trained Sep 29–30 by Bartosz Kalicki (AMAZEMET) · first run on our own Oct 2",
             "The machine arrived in June twenty twenty-six, and the room was renovated around it over the summer: power, chilled "
             "water, and cabinets. Bartosz Kalicki from AMAZEMET installed it on September twenty-eighth and trained the "
             "team over the next two days, and the team ran it on its own for the first time on October second. Everything in "
             "these tutorials comes from those recordings."),
            ("card", "Next: tutorial 1, before a run",
             "The written procedure, with a link to the exact moment of video behind every step, is in the byu-vcl repository "
             "under atomizer-training/sop.md",
             "The written procedure, with a link to the exact moment of video behind every step, is in the byu-vcl repository. "
             "Next: tutorial one, before a run."),
        ],
    },
    "01-before": {
        "title": "Atomizer tutorial 1: before a run (draft 6)",
        "segments": [
            ("title", "Before a run", "Tutorial 1 · utilities, the furnace, the chamber and the ultrasonic stack",
             "Tutorial one: before a run."),
            ("outline", "00-overview_tutorial1", "Tutorial one covers everything before the furnace heats up."),
            ("build", "01-before", [
                "Before any heating, four things have to be right, in this order.",
                "The utilities.",
                "The furnace: nozzle, crucible, insulation, thermocouple, sealing rod and the charge.",
                "The chamber, with the splash disc, the powder container and the catch bowl.",
                "And last the ultrasonic stack, assembled, mounted in the door and scanned, before the door closes.",
            ]),
            ("outline", "01-before_step1", "Step one: the utilities."),
            ("anim", "01_utilities", [
                'Switch on the breakers and the main switch. Everything else is still off.',
                'Open the facility chilled-water valve only a little. The campus water is cold enough to trip the water-too-cold fault, and the heat exchanger needs at least two liters per minute.',
                'Switch the heat exchanger on only when you are about to heat.',
                'Compressed air arrives at eight bar and is regulated to about four. It only cools the transducer, but without it the ultrasonics will not start.',
                'Argon, five nines pure, at eight bar on the regulator, feeds the furnace line and the chamber line through a tee. It also drives the pneumatics.',
                "Then the checklist: vacuum pump oil in its sight glass, the exchanger's water level, the HEPA filter, and dry hoses.",
            ]),
            ("clip", "wRc8p2_FnJo", 86.2, 42.5, B),
            ("clip", "wRc8p2_FnJo", 132.5, 38.9, B),
            ("outline", "01-before_step2", "Step two: the furnace."),
            ("anim", "03_furnace_load", [
                "Start cold. Open the furnace lid, and swing the sealing-rod lever up, clear of the opening. For a "
                "rebuild, everything comes out: thermocouple, sealing rod, insulation, and crucible.",
                "On the bench, the nozzle goes into its holder, white side up. Half a millimeter is the standard bore, "
                "and point seven is more reliable for aluminum alloys. The holder screws into the crucible by hand, "
                "several turns, and only just tight.",
                "The graphite seal and the bottom insulation go in first. Then lift the crucible over, and lower it "
                "straight down into the coil. Handle it gently: graphite is brittle.",
                "Open the chamber's left door. Through it, the lower seal and the thin graphite nut go onto the holder "
                "from below, while the crucible is held still at the top, its thermocouple hole turned to the back "
                "right. A second person makes this easier; alone, keep one hand on the crucible. Tighten it snug, but "
                "never force it. Overtightened graphite cracks, and a loose nut will not seal.",
                "Side insulation goes around the crucible, with its hole lined up with the thermocouple port, and then "
                "the top insulation.",
                "The thermocouple goes in at the back right, down into the hole in the crucible wall, bent to sit close.",
                "The sealing rod needs a clean, smooth tip, or it will not seal. It goes straight down onto the nozzle, "
                "before any metal goes in.",
                "Then swing the lever down onto the rod's adapter, push the safety pin in, and press the sealing rod "
                "button to bring it down.",
                "Now the charge, clean and at most twenty millimeters across. Two hundred fifty to three hundred grams "
                "is the recommended load.",
                "Close the lid, and set the latch just tight enough to seal. If it hisses under pressure, adjust the "
                "latch. The chamber door stays open for the next step.",
            ]),
            ("clip", "wRc8p2_FnJo", 2754.8, 34.6, B),
            ("clip", "wRc8p2_FnJo", 2793.2, 44.2, B),    # the thread reaches into the chamber; nut, thermocouple hole
            ("clip", "1F9_4ccwhss", 100.9, 42.5, B),     # rod tip, rod in, lever down, "now we can add the material"
            ("outline", "01-before_step3", "Step three: the chamber."),
            ("anim", "03b_chamber", [
                'First the round splash-protection disc drops into the top flange of the powder container. One is enough for aluminum.',
                'Lift the container under the outlet and close the flange clamp finger-tight. A second person makes this easier, one holding the weight while the other closes the clamp; on your own, keep it supported until the clamp is shut.',
                'Through the open door, the catch bowl goes on the chamber floor, around the outlet. It catches melt that does not atomize, and protects the chamber if a plate breaks.',
            ]),
            ("clip", "58wJ_Khwgyk", 158.3, 25.4, B),
            ("clip", "58wJ_Khwgyk", 224.4, 16.4, B),
            ("outline", "01-before_step4", "Step four: the ultrasonic stack, and closing the door."),
            ("anim", "02_stack", [
                'The ultrasonic stack goes in last. It goes transducer, booster, sonotrode, then the connector, the plate and the upper sonotrode. The transducer is an air-cooled piezo stack on a cable carrying about a thousand volts. Never drop it or get it wet.',
                'The booster goes onto the transducer at sixty-five newton meters. Mounted in reverse, the one-and-a-half-to-one booster lowers the amplitude, for finer powder.',
                'The sonotrode goes on at sixty newton meters, with isopropanol on the threads.',
                'With the door locked open, slide the stack into the door housing, short of its mark for now, and fit both clamps.',
                'With the stack in the housing, follow the training\'s order: the double-threaded connector into the sonotrode, the plate onto it through the hole near its end, then the tungsten upper sonotrode, tightened against the plate to fifty newton meters while a seventeen millimeter wrench holds the sonotrode.',
                'Then run a scan. One wide peak a little over forty kilohertz is good.',
                'A drop of water on the plate should atomize over the whole surface. If only half of it atomizes, the plate is cracked.',
                'Bolt the protective cover over the transducer, lock the cable, and connect the cooling air.',
                'Run the frequency check before closing. Swing the door shut, with the stack pulled back if the upper sonotrode would catch the opening, then slide it to its mark. The stream must land mid-plate, beside the upper sonotrode, and never on it.',
                'Swing the three bolts over, and tighten the star knobs.',
            ]),
            ("clip", "58wJ_Khwgyk", 419.9, 16.0, B),
            ("clip", "58wJ_Khwgyk", 805.1, 37.7, B),
            ("clip", "58wJ_Khwgyk", 1332.2, 28.0, B),
            ("card", "Ready for the gas wash", "Next: tutorial 2, during a run",
             "The machine is ready for the gas wash, which is where tutorial two begins."),
        ],
    },
    "02-during": {
        "title": "Atomizer tutorial 2: during a run (draft 6)",
        "segments": [
            ("title", "During a run", "Tutorial 2 · gas wash, heating and melting, the pour, and ending it",
             "Tutorial two: during a run."),
            ("outline", "00-overview_tutorial2", "Tutorial two covers the run itself, from the gas wash to the end of the pour."),
            ("build", "02-during", [
                "A run has four stages.",
                "The gas wash.",
                "Heating and melting the charge.",
                "The pour.",
                "And ending the pour cleanly.",
            ]),
            ("outline", "02-during_step1", "Step one: the gas wash."),
            ("anim", "04_gas_wash", [
                'Turn pressure control off before any pumping. Wash one vessel while the other keeps its overpressure, so that any leak pulls in argon, not air.',
                'The furnace wash pumps down to the gauge floor, about minus eight hundred fifty millibar at this altitude. That is normal, not a leak.',
                'Then it fills with argon, and repeats.',
                'Read oxygen only after backfilling. Under vacuum the reading means nothing.',
                'Then wash the chamber the same way, while the furnace holds its overpressure.',
                'Start the generator, heat to two hundred fifty degrees, and wash again. The target is moisture in the insulation and the crucible, not the metal.',
                'Then five hundred degrees, and wash again. Stop once oxygen is low and stable: never above one hundred parts per million, ideally forty to fifty.',
                'Turn pressure control back on, with the furnace melting pressure slightly below the chamber. Now it is ready to melt.',
            ]),
            ("clip", "9kn-HhXCr1o", 205.3, 18.6, B),
            ("clip", "9kn-HhXCr1o", 516.3, 26.9, B),
            ("clip", "58wJ_Khwgyk", 2170.4, 15.9, B),
            ("outline", "02-during_step2", "Step two: heat and melt."),
            ("anim", "05_melt", [
                'Set eight hundred fifty to one thousand degrees at first. Long rods heat at the bottom and stay cooler at the top, so overshoot to drop them.',
                'Watch for the melt cues: a small temperature dip as the melt reaches the thermocouple, and faster beeping from the induction.',
                'As soon as the rods slump into a pool, bring the setpoint down to seven hundred eighty to eight hundred degrees, which is kinder to the plate.',
                'Once everything is liquid, wait two minutes, and no longer. The crucible-wall thermocouple lags the melt, and waiting longer only oxidizes it.',
                'Meanwhile, turn the transducer cooling on, rescan the ultrasonics because scans expire, put hearing protection on, and take your place at the window.',
            ]),
            ("clip", "9kn-HhXCr1o", 810.3, 16.7, B),
            ("clip", "1F9_4ccwhss", 282.9, 20.1, B),
            ("clip", "58wJ_Khwgyk", 3442.5, 35.2, B),
            ("outline", "02-during_step3", "Step three: the pour."),
            ("anim", "06_pour", [
                'With the melt at about eight hundred degrees and oxygen low, the pour goes quickly: vibration on, draining pressure, sealing rod up, and turbo as needed.',
                'Vibration on. Amplitude is a percentage of generator current; start near ninety percent and adjust.',
                'Draining pressure, with the furnace above the chamber, pushes the melt out. Only the difference matters.',
                'Sealing rod up, and the stream falls onto the plate. The first drops usually bounce off, because a cold, dry plate does not wet.',
                'A short turbo push heats the plate and clears the nozzle. Pouring more at the start is what makes the plate wet.',
                'Once the plate is hot, every drop atomizes. The stream should land mid-plate, beside the upper sonotrode, and never on it.',
                'A stream that is too thin gathers and drips. Melt shooting past the plate means the pressure is too high, which is what happened on October second.',
                'For two or three minutes, the operator stays at the window with the amplitude slider, the turbo button and the plate position.',
                'When the crucible runs empty, it is time for the end-of-pour sequence.',
            ]),
            ("clip", "58wJ_Khwgyk", 3592.9, 10.0, B),
            ("clip", "naePD8o9_Gk", 1408.8, 20.4, B),
            ("clip", "58wJ_Khwgyk", 3838.7, 13.8, B),
            ("clip", "9kn-HhXCr1o", 1480.2, 18.2, B),
            ("outline", "02-during_step4", "Step four: end the pour."),
            ("anim", "07_end_cooldown", [
                'When the crucible is empty, one turbo push clears the last drops and the nozzle.',
                'Then, within seconds: sealing rod down, melting pressure, generator stop, ultrasonics stop. Vibrating against solidified metal cracks the plate.',
            ], (0, 1)),
            ("clip", "naePD8o9_Gk", 1922.6, 19.9, B),
            ("card", "Next: tutorial 3, after a run", "Shutdown, cool-down, collecting the powder, and cleaning",
             "Tutorial three covers the shutdown, cooling down, collecting the powder, and cleaning."),
        ],
    },
    "03-after": {
        "title": "Atomizer tutorial 3: after a run (draft 6)",
        "segments": [
            ("title", "After a run", "Tutorial 3 · shutdown, cool-down and opening, collecting the powder, cleaning",
             "Tutorial three: after a run."),
            ("outline", "00-overview_tutorial3", "Tutorial three covers everything after the pour."),
            ("build", "03-after", [
                "After the pour come four steps.",
                "The shutdown sequence.",
                "Cooling down and opening the chamber.",
                "Collecting the powder.",
                "And cleaning for the next run.",
            ]),
            ("outline", "03-after_step1", "Step one: the shutdown sequence."),
            ("anim", "07_end_cooldown", [
                'The run ends the moment the crucible is empty: one turbo push to clear the nozzle,',
                'then sealing rod down, melting pressure, generator stop, and ultrasonics stop, all within seconds.',
            ], (0, 1)),
            ("clip", "naePD8o9_Gk", 1891.3, 24.1, B),
            ("outline", "03-after_step2", "Step two: cool down, and open the chamber."),
            ("anim", "07_end_cooldown", [
                'Set two hundred fifty degrees for next time, and let it cool. Open only at or below four hundred degrees, because above five hundred, graphite burns in air.',
                'Turn pressure control off and press vent. The door stays locked while the pressure is off atmospheric. Masks and lab coat on.',
                'Swing the three bolts back and open the door; the plate comes out with it. If the upper sonotrode would catch the edge of the opening, pull the stack back in its housing first. The chamber and cone are water-cooled, but the furnace parts are still hot.',
                'Brush the plate, the bowl, the walls and the view port down into the container, before it comes off.',
            ], (2, 5)),
            ("clip", "naePD8o9_Gk", 2320.3, 11.2, B),
            ("clip", "naePD8o9_Gk", 2339.4, 5.4, B),
            ("outline", "03-after_step3", "Step three: collect the powder."),
            ("anim", "07_end_cooldown", [
                'Close the container valve first, then release the clamp and lift the container off. It is heavier than it looks, and argon stays inside it.',
                'Pour the powder onto paper, pick out the chunks, sieve it, and bag it with a six-character label and a photo on GitHub. At about one hundred degrees, shut the utilities off.',
            ], (6, 7)),
            ("clip", "tfb4fsVNIFI", 0.0, 16.0, B),
            ("clip", "naePD8o9_Gk", 3219, 20, B),
            ("clip", "naePD8o9_Gk", 3051.8, 18.7, B),
            ("outline", "03-after_step4", "Step four: clean and maintain."),
            ("anim", "08_clean", [
                'Cleaning depends on what runs next. For the same alloy: open, brush, and vacuum. A material change takes about an hour: vacuum, then wipe everything, with brushes, paper towels and isopropanol.',
                'Unscrew the upper sonotrode, then slide the plate off the connector. Never grind or clean a plate: keep one plate per alloy, and log which plate saw which material. A stainless scraper handles stuck particles.',
                'Once the furnace can be touched, open the lid, raise the sealing rod, pull the safety pin, swing the lever up, and take the rod out. Scrape aluminum off the shaft, and keep the tip smooth.',
                'Strip it in order: thermocouple, top and side insulation. Then, through the door, hold the graphite nut and unscrew it from below with its seal, so nothing falls. Lift the crucible out, and peel the slag from its floor; the bottom insulation comes out last.',
                'On the bench, unscrew the holder and take the nozzle out. Look through it for light; clear it with a needle, or drill it to point seven.',
                'Reassemble in the same order as before a run. Wipe the O-rings, and check the HEPA filter about every two months, keeping a used one in a metal tray with sand.',
            ]),
            ("clip", "58wJ_Khwgyk", 4057.6, 25.5, B),
            ("clip", "FDRTt68Vfvo", 1071.0, 4.2, B),
            ("clip", "FDRTt68Vfvo", 1096.1, 7.6, B),
            ("clip", "wRc8p2_FnJo", 530.8, 28.6, B),
            ("card", "Lessons from the first run on our own (Oct 2)",
             "Label the plates · fit the transducer cover · keep 17 and 18 mm wrenches and the torque wrench at the machine · "
             "draining pressure was too high and the plate too far · write every reading down",
             "The team's first run without the trainer, on October second, taught a few things. Label the plates, because they "
             "could not be told apart. Fit the transducer cover every time. Keep metric seventeen and eighteen millimeter "
             "wrenches and a torque wrench with the machine. The draining pressure was set too high and the plate was too far "
             "from the nozzle, so much of the charge flew past without atomizing. And write down every reading, because the "
             "machine keeps no log. The full procedure, with links to every moment of the videos, is in the repository."),
        ],
    },
}


def R(vid, t_in, t_out, caption, **opts):
    """A real-footage pick from real-footage.md: the recording from t_in to t_out (its middle 14 s if it runs longer than
    17), under a bar reading `caption`. opts: light (the camera rests on one view, so less stabilisation zoom), mute (only
    chatter on the sound), wrong (shown as the mistake, not the method), exact (keep the points as given), section (the
    bar's step label, where no step outline comes before it), at="end" (a long pick plays its last 14 s, not its middle,
    where the words that matter come at the end)."""
    return ("real", vid, t_in, t_out, caption, opts)


# Draft 5: after each step's animation, the real action for each of its sub-steps (the first picks of real-footage.md, in
# the animation's order), then the explanation clips draft 4 already had. A key names the segment the group follows:
# "anim <name>" (plus " <first>-<last>" for a part of one), "card <title>", or "before card <title>" for a group that
# comes just before that card.
REAL = {
    "00-overview": {
        "anim 00_machine": [
            R("VFycaxIq0Tc", 150, 170, "The machine, from the front", light=True, mute=True, section="The machine"),
            R("2wMgeI-E7zw", 215, 238, "Furnace panel and touchscreen", section="The machine"),
            R("2wMgeI-E7zw", 12, 34, "The utilities, at the back", section="The machine"),
        ],
        "anim 06_pour": [
            R("TFpU4uqVF9c", 957, 980, "The melt, through the lid window", section="How it makes powder"),
            R("dnPs56DPt6I", 980, 995, "Water atomizing on the plate", section="How it makes powder"),
            R("9kn-HhXCr1o", 1212, 1232, "Rod up: the stream hits the plate", light=True, section="How it makes powder"),
            R("9kn-HhXCr1o", 1262, 1271, "Atomizing high on the plate", light=True, section="How it makes powder"),
        ],
        "card Safety, every time": [
            R("58wJ_Khwgyk", 4427, 4442, "Full-face respirators, one each", section="Safety"),
        ],
    },
    "01-before": {
        "anim 01_utilities": [
            R("2wMgeI-E7zw", 203, 215, "The main switch, on the frame"),
            R("2wMgeI-E7zw", 64, 78, "Chilled water: open it a little"),
            R("2wMgeI-E7zw", 126, 148, "Heat exchanger on"),
            R("qYyT39D5Yzo", 44, 58, "Compressed air on"),
            R("DWH1CEygsTI", 355, 370, "The argon regulator"),
            R("qYyT39D5Yzo", 86, 98, "The startup checklist"),
        ],
        "anim 03_furnace_load": [
            R("wRc8p2_FnJo", 2150, 2172, "Teardown: thermocouple out first"),
            R("dnPs56DPt6I", 168, 190, "Crucible lowered into the coil"),
            R("HTlUrAr5HVU", 178, 190, "Graphite nut on, from below"),     # draft 6: the alt pick (2:26 showed arms)
            R("1F9_4ccwhss", 31, 55, "Insulation lined up with the port", light=True),
            R("HTlUrAr5HVU", 260, 280, "Thermocouple into its hole"),
            R("dnPs56DPt6I", 240, 265, "Sealing rod in, under the lever"),
            R("DWH1CEygsTI", 40, 60, "The charge, wiped with IPA"),
            R("1F9_4ccwhss", 317, 335, "Lid closed and latched", light=True),
        ],
        "anim 03b_chamber": [
            R("58wJ_Khwgyk", 286, 298, "Container on, clamp finger-tight"),
            R("58wJ_Khwgyk", 329, 343, "The catch bowl, in the chamber", exact=True),
        ],
        "anim 02_stack": [
            R("58wJ_Khwgyk", 397, 418, "The transducer, at the door"),
            R("FDRTt68Vfvo", 2276, 2300, "Booster on, counter-held: 65 N·m"),
            R("FDRTt68Vfvo", 2123, 2145, "The sonotrode, threaded on"),
            R("58wJ_Khwgyk", 1486, 1503, "The stack, into the door housing"),
            R("58wJ_Khwgyk", 1555, 1575, "The plate on: 50 N·m"),
            R("dnPs56DPt6I", 338, 363, "The scan, on the touchscreen", at="end"),
            R("dnPs56DPt6I", 980, 995, "Water test: the whole plate atomizes"),
            R("FDRTt68Vfvo", 2455, 2470, "The cable connector, locked"),
            R("dnPs56DPt6I", 602, 615, "Frequency check: 40,200 Hz"),
            R("dnPs56DPt6I", 1030, 1044, "The star knobs, tightened"),      # draft 6: before the phone turns to the floor
        ],
    },
    "02-during": {
        "anim 04_gas_wash": [
            R("9kn-HhXCr1o", 184, 205, "Pressure control off, pump on"),
            R("58wJ_Khwgyk", 2030, 2052, "The furnace gas wash, started"),
            R("58wJ_Khwgyk", 2255, 2273, "The last cycle, at −0.76 bar", light=True),
            R("DWH1CEygsTI", 1255, 1268, "Oxygen after the fill: 19 ppm"),
            R("58wJ_Khwgyk", 2293, 2312, "Chamber wash: pump on, valve open"),
            R("9kn-HhXCr1o", 149, 170, "Generator on, setpoint 250 °C"),
            R("9kn-HhXCr1o", 373, 393, "The next wash, at 500 °C"),
            R("9kn-HhXCr1o", 94, 108, "Pressure control back on"),
        ],
        "anim 05_melt": [
            R("58wJ_Khwgyk", 3170, 3186, "Overshoot, to drop the rods"),
            R("DWH1CEygsTI", 1417, 1430, "The charge, glowing"),
            R("txH397FGTAU", 2313, 2332, "Setpoint down as it melts"),
            R("DWH1CEygsTI", 1628, 1652, "The pool: wait two minutes", at="end"),
            R("DWH1CEygsTI", 1710, 1722, "Rescan: 40,185 Hz", exact=True),  # draft 6: only while the touchscreen is in frame
        ],
        "anim 06_pour": [
            R("naePD8o9_Gk", 1152, 1171, "The pour sequence, on the touchscreen"),
            R("of5-LhkX_VQ", 1500, 1522, "Amplitude set to about 90"),
            R("9kn-HhXCr1o", 1212, 1232, "Rod up: the stream hits the plate", light=True),
            R("9kn-HhXCr1o", 1262, 1271, "Hot plate: atomizing high on it", light=True),
            R("DWH1CEygsTI", 1833, 1848, "Stack too high: stream on the sonotrode", wrong=True),
            R("DWH1CEygsTI", 1955, 1978, "The same mistake, explained", wrong=True),
            R("9kn-HhXCr1o", 1271, 1280, "Melt gathers at the bottom, drips", light=True),
            R("of5-LhkX_VQ", 1608, 1633, "Pressure too high: little atomized", wrong=True, at="end"),
            R("txH397FGTAU", 2686, 2708, "At the window as the pour ends"),
        ],
        "anim 07_end_cooldown 0-1": [
            R("58wJ_Khwgyk", 3732, 3744, "Turbo, then the stop sequence"),
            R("9kn-HhXCr1o", 1299, 1316, "It's over: stop the vibration", light=True),
        ],
    },
    "03-after": {
        "anim 07_end_cooldown 0-1": [
            R("TFpU4uqVF9c", 1228, 1242, "Pour over: rod down, generator off"),
        ],
        "anim 07_end_cooldown 2-5": [
            R("of5-LhkX_VQ", 1679, 1699, "Setpoint down to 250 °C"),
            R("Pk0K5sBz-sQ", 260, 284, "Door open, the plate on it"),
            R("naePD8o9_Gk", 2620, 2645, "Powder brushed into the chamber"),
        ],
        "anim 07_end_cooldown 6-7": [
            R("naePD8o9_Gk", 3305, 3330, "Powder brushed out onto paper"),
        ],
        "anim 08_clean": [
            R("1F9_4ccwhss", 412, 436, "Seal and chamber, wiped with alcohol", at="end"),
            R("wRc8p2_FnJo", 2184, 2207, "Sealing rod out, insulation lifted"),
            R("wRc8p2_FnJo", 2247, 2272, "The nut, unscrewed from below"),
            R("LSQmxwmlTkQ", 0, 20, "Drilling a nozzle: #70 bit", mute=True),
            R("FDRTt68Vfvo", 3142, 3155, "The O-ring seal, wiped with isopropanol"),
        ],
        "before card Lessons from the first run on our own (Oct 2)": [
            R("qYyT39D5Yzo", 146, 170, "Oct 2: which plate is which?", section="Lessons from Oct 2"),
            R("of5-LhkX_VQ", 1644, 1660, "Oct 2: pressure too high, plate far", section="Lessons from Oct 2"),
        ],
    },
}


def _anchor(seg):
    if seg[0] == "anim":
        return f"anim {seg[1]}" + (f" {seg[3][0]}-{seg[3][1]}" if len(seg) > 3 else "")
    return f"card {seg[1]}" if seg[0] == "card" else None


for _key, _groups in REAL.items():
    _new, _used = [], set()
    for _seg in TUTORIALS[_key]["segments"]:
        _a = _anchor(_seg)
        _new += _groups.get(f"before {_a}", []) + [_seg] + _groups.get(_a, [])
        _used |= {_a, f"before {_a}"}
    assert set(_groups) <= _used, f"{_key}: no segment for {set(_groups) - _used}"
    TUTORIALS[_key]["segments"] = _new
