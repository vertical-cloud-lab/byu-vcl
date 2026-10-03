"""Narration and segment lists for the tutorial videos (edit here, then run build_tutorials.py).

Every tutorial has the same shape, so that the four hang together: a title, the draw.io outline of its steps, then for each
step the outline again with that step highlighted, the 3D animation of the step under synthetic narration, and the trainer
explaining it in his own words. A closing card points to the next tutorial.

Segment forms:
  ("title", title, subtitle, narration)
  ("outline", diagram, narration)                     diagram = diagrams/<diagram>.png (draw.io export)
  ("anim", name, narration)                           name = ../viz3d/out/mp4/<name>.mp4; narration a string, or a list with
                                                      one sentence per sub-step of the animation (../viz3d/out/<name>.json)
  ("clip", video_id, start_seconds, duration_seconds, speaker)   snapped to sentence boundaries by clip_words.py
  ("card", title, subtitle, narration)

Synthetic narration: Microsoft Edge TTS en-US-AndrewMultilingualNeural at 1x. Human narration: Bartosz Kalicki (AMAZEMET),
in the clips.
"""
VOICE = "en-US-AndrewMultilingualNeural"
# Whisper's mishearings in the clips, corrected in the burned-in subtitles only (the cached words stay as heard)
FIXES = {"newtonometers": "newton meters", "your production": "hearing protection", "the bias": "a vise",
         "transistor": "transducer", "argol": "argon", "ceiling rod": "sealing rod", "or other dramatica.": "or other pneumatics.",
         "in a cruise of 250": "in increments of 250", "fiber powder": "finer powder", "band valve": "vent valve",
         "the clay heats up": "the plate heats up", "pull more": "pour more"}
B = "Bartosz Kalicki, AMAZEMET"

TUTORIALS = {
    "00-overview": {
        "title": "rePowder atomizer at BYU VCL, tutorial 0: the machine and how it works (draft 2)",
        "segments": [
            ("title", "The rePowder ultrasonic atomizer", "Tutorial 0 · the machine, how it makes powder, and what a run looks like",
             "The rePowder ultrasonic atomizer, at the BYU Vertical Cloud Lab."),
            ("outline", "00-overview",
             "A run on the atomizer has three parts, and each has its own tutorial. Before a run: the utilities, the ultrasonic "
             "stack, the furnace and its charge, and the chamber. During a run: the argon gas wash, the melt, and the pour onto "
             "the vibrating plate. After a run: shutdown, cool-down, collecting the powder, and cleaning. This overview "
             "introduces the machine itself and how it turns a bar of metal into powder."),
            ("anim", "00_machine", [
                "This is the rePowder ultrasonic atomizer at BYU, modeled from the training videos and AMAZEMET's documents.",
                'On top is the induction furnace: a stainless body holding the coil, the crucible and the insulation, under a lid with a window.',
                'The melting control panel and the main switch are on the cabinet, and the touchscreen on its swing arm runs the pressures, the gas and the ultrasonics.',
                'Below the furnace is the fifty-seven liter atomization chamber, with a view port at the front and a door closed by three clamps.',
                'The ultrasonic unit rides in the door: the transducer outside, under its cover, and the sonotrode and plate inside, under the furnace nozzle.',
                'A cone takes the powder down through a valve into the container, which is clamped on by its flange.',
                'Around it are the utilities: argon, the vacuum pump, compressed air for the transducer, and the heat exchanger on the chilled water.',
                'Cut in half, the whole path shows: crucible, sealing rod and nozzle above the plate, and the cone down to the container.',
            ]),
            ("anim", "06_pour", [
                'Here is how it makes powder. An induction coil heats the graphite crucible, and the graphite heats the metal inside it.',
                'Below the furnace, a titanium plate vibrates forty thousand times a second.',
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
        "title": "rePowder atomizer at BYU VCL, tutorial 1: before a run (draft 2)",
        "segments": [
            ("title", "Before a run", "Tutorial 1 · utilities, the ultrasonic stack, the furnace and the chamber",
             "Tutorial one: before a run."),
            ("outline", "00-overview_tutorial1", "Tutorial one covers everything before the furnace heats up."),
            ("outline", "01-before",
             "Before any heating, four things have to be right, in this order. The utilities. The ultrasonic stack, assembled, "
             "torqued and scanned. The furnace: nozzle, crucible, insulation, thermocouple, sealing rod and the charge. "
             "And the chamber, with the powder container clamped and the door closed."),
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
            ("outline", "01-before_step2", "Step two: the ultrasonic stack."),
            ("anim", "02_stack", [
                'The stack goes transducer, booster, sonotrode, plate. The transducer is an air-cooled piezo stack on a cable carrying about a thousand volts. Never drop it or get it wet.',
                'The booster goes onto the transducer at sixty-five newton meters. Mounted in reverse, the one-and-a-half-to-one booster lowers the amplitude, for finer powder.',
                'The sonotrode goes on at sixty newton meters, with isopropanol on the threads.',
                'Fit the splash plate first, because it is hard to fit later, then slide the stack into the door.',
                'The plate goes onto its stud with the stack already in the housing: fifty newton meters, counter-holding the sonotrode with a seventeen millimeter wrench.',
                'Then run a scan. One wide peak a little over forty kilohertz is good.',
                'A drop of water on the plate should atomize over the whole surface. If only half of it atomizes, the plate is cracked.',
                'Finally, bolt the protective cover over the transducer, lock the cable, and connect the cooling air.',
            ]),
            ("clip", "58wJ_Khwgyk", 419.9, 16.0, B),
            ("clip", "58wJ_Khwgyk", 805.1, 37.7, B),
            ("clip", "58wJ_Khwgyk", 1332.2, 28.0, B),
            ("outline", "01-before_step3", "Step three: the furnace."),
            ("anim", "03_furnace_load", [
                "Start cold, with the furnace lid open. For a rebuild, everything comes out: thermocouple, sealing rod, "
                "insulation, and crucible.",
                "The nozzle is the consumable. It goes into its holder white side up. Half a millimeter is the standard bore, "
                "and point seven is more reliable for aluminum alloys. Nozzle and holder screw onto the crucible as a pair, "
                "just tight.",
                "Then the graphite seal and the bottom insulation, and the crucible goes down into the coil, held by the "
                "graphite nut from below.",
                "Side insulation goes around the crucible, with its hole lined up with the thermocouple port, and then the "
                "top insulation.",
                "The thermocouple goes into the hole in the crucible wall, bent to sit close.",
                "The sealing rod needs a clean, smooth tip, or it will not seal. It is lowered onto the nozzle before any "
                "metal goes in.",
                "The charge must be clean and at most twenty millimeters across. Two hundred fifty to three hundred grams is "
                "the recommended load.",
                "Close the lid, and set the latch just tight enough to seal. If it hisses under pressure, adjust the latch.",
            ]),
            ("clip", "wRc8p2_FnJo", 2754.8, 34.6, B),
            ("clip", "1F9_4ccwhss", 100.8, 19.6, B),
            ("outline", "01-before_step4", "Step four: the chamber."),
            ("anim", "03b_chamber", [
                'The powder container goes on with two people: one lifts it into place under the cone while the other closes the flange clamp, finger-tight.',
                'Through the door, the catch bowl goes on the chamber floor and the splash plate above the container. One is enough for aluminum.',
                'Run the frequency check now, before closing, then swing the door shut. The ultrasonic unit rides in it.',
                'Close all three clamps.',
            ]),
            ("clip", "58wJ_Khwgyk", 224.4, 16.4, B),
            ("clip", "58wJ_Khwgyk", 158.3, 25.4, B),
            ("card", "Ready for the gas wash", "Next: tutorial 2, during a run",
             "The machine is ready for the gas wash, which is where tutorial two begins."),
        ],
    },
    "02-during": {
        "title": "rePowder atomizer at BYU VCL, tutorial 2: during a run (draft 2)",
        "segments": [
            ("title", "During a run", "Tutorial 2 · gas wash, heating and melting, the pour, and ending it",
             "Tutorial two: during a run."),
            ("outline", "00-overview_tutorial2", "Tutorial two covers the run itself, from the gas wash to the end of the pour."),
            ("outline", "02-during",
             "A run has four stages: the gas wash, heating and melting the charge, the pour, and ending the pour cleanly."),
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
                'Once the plate is hot, every drop atomizes. Steer with the plate position, so the stream lands high on the plate, but not over the top.',
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
        "title": "rePowder atomizer at BYU VCL, tutorial 3: after a run (draft 2)",
        "segments": [
            ("title", "After a run", "Tutorial 3 · shutdown, cool-down and opening, collecting the powder, cleaning",
             "Tutorial three: after a run."),
            ("outline", "00-overview_tutorial3", "Tutorial three covers everything after the pour."),
            ("outline", "03-after",
             "After the pour come four steps: the shutdown sequence, cooling down and opening the chamber, collecting the powder, "
             "and cleaning for the next run."),
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
                'Open the three clamps and the door. The chamber and cone are water-cooled, but the furnace parts are still hot.',
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
                'Take the plate off its stud. Never grind or clean a plate: keep one plate per alloy, and log which plate saw which material. A stainless scraper handles stuck particles.',
                'Once the furnace can be touched, open the lid and take the sealing rod out. Peel the slag from the crucible floor, scrape aluminum off the shaft, and keep the tip smooth.',
                'Strip the thermocouple, the insulation and the crucible. Look through the nozzle for light; clear it with a needle, or drill it to point seven.',
                'Reassemble in order, wipe the O-rings, and check the HEPA filter about every two months, keeping a used one in a metal tray with sand.',
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
