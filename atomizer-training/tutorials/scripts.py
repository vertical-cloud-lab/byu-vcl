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
            ("anim", "00_machine",
             "The atomizer is a single module. On top is the induction furnace, under a stainless bell with a small window. "
             "Beside it, the blue cabinet carries the melting control panel and the touchscreen that runs the machine. "
             "Below the furnace is the atomization chamber. Its door holds the ultrasonic unit and a view port. "
             "A cone under the chamber leads down to the powder container, which closes with its own valve. "
             "At the back are the utilities: chilled water, compressed air, argon, and the vacuum pump."),
            ("anim", "06_pour",
             "Here is how it makes powder. An induction coil heats a graphite crucible, and the graphite heats the metal inside it. "
             "A graphite sealing rod closes a small nozzle in the floor of the crucible. When the rod lifts, a little argon "
             "overpressure pushes a thin stream of melt through the nozzle, onto a plate vibrating forty thousand times a second. "
             "The melt wets the plate, the vibration breaks it into droplets, and they freeze into round particles as they fall "
             "through the argon into the container."),
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
            ("anim", "01_utilities",
             "Open the facility chilled-water valve only a little. The campus water is cold enough to trip the water-too-cold "
             "fault, and the heat exchanger needs more than two liters per minute. Switch the heat exchanger on only when you "
             "are about to heat. Compressed air arrives at eight bar and is regulated to about four. It only cools the "
             "transducer, and without it the ultrasonics will not start. Argon, five nines pure, at eight bar on the regulator, "
             "feeds the furnace line and the chamber line through a tee. Check the vacuum pump oil in its sight glass, the "
             "exchanger's water level, and look for leaks."),
            ("clip", "wRc8p2_FnJo", 86.2, 42.5, B),
            ("clip", "wRc8p2_FnJo", 132.5, 38.9, B),
            ("outline", "01-before_step2", "Step two: the ultrasonic stack."),
            ("anim", "02_stack",
             "The stack is built from the transducer outward: booster, sonotrode, and the plate on its connector stud. Torque "
             "matters, because the vibration has to pass through every joint: sixty-five newton meters at the transducer, sixty "
             "at the sonotrode, and fifty at the plate. A one-and-a-half-to-one booster mounted in reverse lowers the amplitude, "
             "which gives finer powder but needs a slow, controlled pour. Then run a scan. One wide peak a little above forty "
             "kilohertz is good. A drop of water on the plate should atomize over the whole surface; atomizing on only half of "
             "it means a crack. Bolt the protective cover over the transducer before you close up."),
            ("clip", "58wJ_Khwgyk", 419.9, 16.0, B),
            ("clip", "58wJ_Khwgyk", 805.1, 37.7, B),
            ("clip", "58wJ_Khwgyk", 1332.2, 28.0, B),
            ("outline", "01-before_step3", "Step three: the furnace."),
            ("anim", "03_furnace_load",
             "The nozzle is the consumable. Half a millimeter is the standard bore, and point seven is more reliable for aluminum "
             "alloys. It goes into its holder white side up, and the crucible threads on until it is just tight. Then the "
             "insulation, and the thermocouple, lined up with its port and bent in close to the crucible. The sealing rod needs "
             "a clean, undamaged tip, because a damaged tip will not seal, and it is lowered before any metal goes in. The charge "
             "must be clean and at most twenty millimeters across; two hundred fifty to three hundred grams is the recommended "
             "load. Close the lid just tight enough to seal. If it hisses under pressure, adjust the latch."),
            ("clip", "wRc8p2_FnJo", 2754.8, 34.6, B),
            ("clip", "1F9_4ccwhss", 100.8, 19.6, B),
            ("outline", "01-before_step4", "Step four: the chamber."),
            ("anim", "03b_chamber",
             "Mount the powder container with two people, one lifting and one clamping, and tighten the flange by hand. Put the "
             "splash plate above it and the catch bowl inside, hang the covers over the openings, and close the door with all "
             "three clamps."),
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
            ("anim", "04_gas_wash",
             "Turn pressure control off before pumping, and always keep overpressure in the vessel you are not washing, so that "
             "any leak pulls in argon instead of air. The furnace wash runs five cycles of vacuum and argon on its own. The gauge "
             "bottoms out near minus eight hundred fifty millibar at this altitude; that is normal, not a leak. Then wash the "
             "chamber the same way. The oxygen reading means nothing under vacuum, so read it only after filling with argon. "
             "Heat to two hundred fifty degrees and wash again, then to five hundred and wash again; the target is moisture in "
             "the insulation and the crucible. Stop when oxygen is stable and low: never above one hundred parts per million, "
             "ideally forty to fifty. Set the melting pressure slightly below the chamber pressure, and turn pressure control "
             "back on."),
            ("clip", "9kn-HhXCr1o", 205.3, 18.6, B),
            ("clip", "9kn-HhXCr1o", 516.3, 26.9, B),
            ("clip", "58wJ_Khwgyk", 2170.4, 15.9, B),
            ("outline", "02-during_step2", "Step two: heat and melt."),
            ("anim", "05_melt",
             "Long rods heat at the bottom and stay cool at the top, so overshoot the setpoint to drop them: between eight hundred "
             "fifty and one thousand degrees was used in training. Watch for the cues. The temperature dips slightly as the melt "
             "touches the thermocouple, and the induction beeps faster. As soon as the charge slumps, bring the setpoint down to "
             "seven hundred eighty to eight hundred degrees, which is kinder to the plate. Once everything is liquid, wait two minutes and no "
             "longer: that is how long the melt takes to catch up with the crucible-wall thermocouple, and waiting longer only "
             "oxidizes it. Meanwhile turn transducer cooling on, rescan the stack, because scans expire, put hearing protection "
             "on, and take your place at the window."),
            ("clip", "9kn-HhXCr1o", 810.3, 16.7, B),
            ("clip", "1F9_4ccwhss", 282.9, 20.1, B),
            ("clip", "58wJ_Khwgyk", 3442.5, 35.2, B),
            ("outline", "02-during_step3", "Step three: the pour."),
            ("anim", "06_pour",
             "The pour is quick: vibration on, then draining pressure and sealing rod up within a second or two of each other, "
             "and turbo pressure when needed. Amplitude is a percentage of generator current; start near ninety. Draining pressure "
             "above the chamber pressure pushes the melt out, and only the difference matters. The first droplet usually "
             "bounces, because a dry plate does not wet. Pouring more at the start heats the plate, and once it is hot every drop "
             "atomizes. Steer with the plate position, so the stream lands high on the plate but not over the top."),
            ("clip", "58wJ_Khwgyk", 3592.9, 10.0, B),
            ("clip", "naePD8o9_Gk", 1408.8, 20.4, B),
            ("clip", "58wJ_Khwgyk", 3838.7, 13.8, B),
            ("clip", "9kn-HhXCr1o", 1480.2, 18.2, B),
            ("outline", "02-during_step4", "Step four: end the pour."),
            ("card", "End of pour, within seconds",
             "Turbo to clear the nozzle → sealing rod down → melting pressure → generator stop → ultrasonics stop",
             "When the crucible is empty, one turbo push clears the nozzle. Then sealing rod down, melting pressure, generator "
             "stop, and ultrasonics stop, all within seconds, because vibrating against solidified metal cracks the plate."),
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
            ("outline", "03-after_step1", "Step one: shut down, and step two, cool down and open."),
            ("anim", "07_end_cooldown",
             "After the pour: sealing rod down, melting pressure, generator stop, ultrasonics stop, and transducer cooling off "
             "once the plate has cooled. Set the furnace to two hundred fifty for next time. Cooling water stays on until about one hundred "
             "degrees. Open the chamber at or below four hundred degrees; above five hundred, graphite burns in air. Turn "
             "pressure control off and press vent first, because the door stays locked while the pressure is off atmospheric. "
             "Masks and coat on, then open the three clamps. Brush the plate, the bowl, the walls and the view port down into the "
             "container. Close the container valve before taking it off; argon stays inside it."),
            ("clip", "naePD8o9_Gk", 1891.3, 24.1, B),
            ("clip", "naePD8o9_Gk", 2320.3, 11.2, B),
            ("clip", "naePD8o9_Gk", 2339.4, 5.4, B),
            ("clip", "tfb4fsVNIFI", 0.0, 16.0, B),
            ("outline", "03-after_step3", "Step three: collect the powder."),
            ("card", "Collecting the powder",
             "Close the container valve first · pour onto paper · pick out the chunks · sieve · bag with a six-character label · "
             "photo on GitHub",
             "Close the container valve before you take the container off; it is heavier than it looks. Pour the powder onto "
             "paper, pick out the chunks, sieve it, and bag it with a six-character label and a photo on GitHub."),
            ("clip", "naePD8o9_Gk", 3051.8, 18.7, B),
            ("clip", "naePD8o9_Gk", 3219, 20, B),
            ("outline", "03-after_step4", "Step four: clean and maintain."),
            ("anim", "08_clean",
             "Cleaning depends on what runs next. For the same alloy: open, brush, and vacuum. A material change takes about an "
             "hour: vacuum everything, then wipe. Brushes, paper towels and isopropanol are all you need, plus a stainless scraper "
             "for stuck particles. Never grind or clean a plate; dedicate one plate to one alloy, and log which plate saw which "
             "material, because they last one to three runs. When the furnace is cool, take the rod out, peel the slag from the "
             "crucible floor, and keep the rod tip smooth. Look through the nozzle for light, and clear it with a needle or drill "
             "it to point seven. Inspect the HEPA filter every two months, and keep a used one in a metal tray with sand."),
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
