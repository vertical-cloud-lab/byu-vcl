"""Narration scripts and segment lists for the tutorial videos (edit here, then run build_tutorials.py).

Segment forms:
  ("card", title, subtitle, narration)
  ("gif", step_name, narration)                       step_name = file in ../viz/out without .gif
  ("clip", video_id, start_seconds, duration_seconds, speaker)   the trainer's own words, from the training videos

Synthetic narration voice: Microsoft Edge TTS en-US-SteffanNeural at 1x. Human narration: Bartosz Kalicki (AMAZEMET)
in the clips. Clip windows are the caption start times from ../timestamps.md with a second or two of lead-in.
"""
VOICE = "en-US-SteffanNeural"
B = "Bartosz Kalicki (AMAZEMET)"
G = "Gage Erickson (BYU VCL)"

TUTORIALS = {
    "00-overview": {
        "title": "rePowder atomizer at BYU VCL, tutorial 0: installation and training overview (draft)",
        "segments": [
            ("card", "rePowder ultrasonic atomizer: installation and training", "Overview of the install (Sep 2026), the AMAZEMET training (Sep 29–30) and the first unsupervised run (Oct 2). Tutorials 1–3 cover before, during and after a run.",
             "This short overview introduces the AMAZEMET rePowder ultrasonic atomizer at the BYU Vertical Cloud Lab. The machine arrived in the summer of twenty twenty-six, the enclosure, power, chilled water and argon were finished in September, and Bartosz Kalicki from AMAZEMET installed it and trained the team on September twenty-ninth and thirtieth. The three tutorials that follow cover what happens before, during, and after a run, using the trainer's own explanations wherever they were recorded."),
            ("clip", "Kv9DT3Vo0GE", 40, 26, G),
            ("clip", "07QOPRHIEvw", 54, 30, G),
            ("card", "How it works", "Induction furnace melts the charge in a graphite crucible. A sealing rod opens a tiny nozzle. The melt stream lands on a plate vibrating at 40 kHz and breaks into droplets that freeze into spherical powder in argon.",
             "An induction coil heats a graphite crucible, and the graphite heats the metal inside it. A graphite sealing rod sits on a nozzle with a hole of half a millimeter or so. Raising the rod, with a little overpressure in the furnace, lets a thin stream of melt fall onto a titanium plate vibrating at forty kilohertz. The melt wets the plate, cavitation throws off droplets, and they freeze into spherical powder in the argon-filled chamber before settling into the container below."),
            ("clip", "z6rwmQW_3Vg", 26, 28, G),
            ("clip", "58wJ_Khwgyk", 3588, 32, B),
            ("clip", "of5-LhkX_VQ", 1788, 14, G),
            ("card", "What is in the repository", "atomizer-training/sop.md (procedure), timestamps.md (every moment linked), keyframes/, viz/ (step animations), transcripts/",
             "Everything shown here is documented in the byu-vcl repository under atomizer-training: the operating procedure, a timestamp log that links every substantive moment of the twenty-six videos, keyframes, the step animations, and the transcripts. Continue with tutorial one, before a run."),
        ],
    },
    "01-before": {
        "title": "rePowder atomizer at BYU VCL, tutorial 1: before a run (draft)",
        "segments": [
            ("card", "Part 1: before a run", "Utilities · ultrasonic stack · furnace preparation · loading the charge. From the AMAZEMET training at BYU, Sep 29–30 2026.",
             "This is part one of three tutorials on the AMAZEMET rePowder atomizer at the BYU Vertical Cloud Lab. It covers everything before heating: the utilities, the ultrasonic stack, preparing the furnace, and loading the charge. Explanations in the trainer's own voice come from the recorded training sessions. The animated steps summarize the standard operating procedure in the repository."),
            ("gif", "01_utilities",
             "Start with the utilities. Open the facility chilled-water valve only a little. The campus water is cold enough to trip the water-too-cold fault, and the heat exchanger needs more than two liters per minute. Switch the heat exchanger on only when you are about to heat. Compressed air arrives at eight bar and is regulated to about four. It does nothing but cool the transducer, and without it the ultrasonics will not start. Argon, five nines purity, at eight bar on the regulator, feeds the furnace line and the chamber line through a tee. Check the vacuum pump oil in the sight glass, the exchanger water level, and look for leaks."),
            ("clip", "58wJ_Khwgyk", 414, 30, B),
            ("gif", "02_stack",
             "The ultrasonic stack is built from the transducer upward: booster, sonotrode, and the plate on its connector stud. Torque matters, because the vibration has to pass through every joint. Sixty-five newton meters at the transducer, sixty at the sonotrode, and fifty at the plate, tightened with the stack already in the housing. A one-and-a-half-to-one booster mounted in reverse lowers the amplitude. That gives finer powder, but it needs a slow and controlled pour. Then run a scan. One wide peak a little above forty kilohertz is good. A drop of water on the plate should atomize over the whole surface. Half the plate means a crack. Bolt the protective cover over the transducer before you close up."),
            ("clip", "FDRTt68Vfvo", 1488, 24, B),
            ("clip", "FDRTt68Vfvo", 1872, 16, B),
            ("clip", "58wJ_Khwgyk", 808, 32, B),
            ("gif", "03_furnace_load_operator",
             "Furnace preparation starts with the nozzle, which is the consumable. Half a millimeter is the standard bore, and point seven is more reliable for aluminum alloys. It goes into the crucible white side up, and the crucible threads onto its holder until it is just tight. The sealing rod goes in before any metal, with a clean and undamaged tip, because a damaged tip will not seal. Then the insulation and the thermocouple, aligned with the port and bent in close. Feedstock must be clean, at most twenty millimeters in diameter, and two hundred fifty to three hundred grams is the recommended charge. Close the lid just tight enough to seal. If it hisses under pressure, adjust the latch."),
            ("clip", "wRc8p2_FnJo", 2744, 40, B),
            ("clip", "1F9_4ccwhss", 108, 18, B),
            ("clip", "1F9_4ccwhss", 280, 26, B),
            ("card", "Chamber ready", "Container clamped by two people, flange finger-tight, splash plate above it, catch bowl in, covers hung, three door clamps closed. Next: part 2, during a run.",
             "Finally the chamber. Mount the powder container with two people, lifting and clamping at the same time, and finger-tighten the flange. Put the splash plate above it and the catch bowl inside, hang the covers over the openings, and close the three door clamps. The machine is now ready for the gas wash, which is where part two begins."),
        ],
    },
    "02-during": {
        "title": "rePowder atomizer at BYU VCL, tutorial 2: during a run (draft)",
        "segments": [
            ("card", "Part 2: during a run", "Gas wash · heating schedule · pressure logic · the pour. From the AMAZEMET training at BYU, Sep 29–30 2026.",
             "Part two covers the run itself: the gas wash, the heating schedule, the pressure logic, and the pour. Most of the explanations are the trainer's own words from the training sessions."),
            ("gif", "04_gas_wash",
             "Turn pressure control off before pumping, and always keep overpressure in the vessel you are not washing, so that any leak pulls in argon instead of air. The furnace gas wash runs five cycles of vacuum and argon on its own. The gauge bottoms out near minus eight hundred fifty millibar at this altitude. That is normal, not a leak. Then wash the chamber the same way. The oxygen reading means nothing under vacuum, so read it only after filling with argon. Start the generator, go to two hundred fifty degrees, and wash again. Then five hundred degrees, and wash again. The target is moisture in the insulation and the crucible, not the melting point of the metal. Stop when oxygen is stable and low: never above one hundred parts per million, ideally forty to fifty. Set the melting pressure slightly below the chamber pressure and turn pressure control back on."),
            ("clip", "9kn-HhXCr1o", 203, 22, B),
            ("clip", "9kn-HhXCr1o", 518, 34, B),
            ("clip", "58wJ_Khwgyk", 2172, 26, B),
            ("gif", "05_melt",
             "Now the melt. Long rods heat at the bottom and stay cool at the top, so overshoot the setpoint to drop them: between eight hundred fifty and one thousand degrees was used in training. Watch for the cues. The temperature dips slightly as the melt touches the thermocouple, and the induction beeps faster. As soon as the charge slumps, bring the setpoint down to about eight hundred degrees, which is kinder to the plate. Once everything is liquid, wait two minutes, and no longer. That is how long the melt needs to catch up with the crucible-wall thermocouple, and waiting longer only oxidizes it. Meanwhile, turn transducer cooling on, rescan the stack because scans expire, put hearing protection on, and take your place at the window."),
            ("clip", "9kn-HhXCr1o", 808, 22, B),
            ("clip", "9kn-HhXCr1o", 962, 22, B),
            ("clip", "58wJ_Khwgyk", 3450, 24, B),
            ("gif", "06_pour",
             "The pour, done quickly and in order: vibration on, then draining pressure, then sealing rod up, and turbo pressure when needed. Amplitude is a percentage of generator current. Eighty to ninety is best; start near ninety and adjust. Draining pressure above the chamber pressure pushes the melt out, and only the pressure difference matters. The first droplet usually bounces, because a dry plate does not wet. Pouring more at the start is what heats the plate, and a short turbo push at one and a half bar helps it wet and clears debris from the nozzle. Once the plate is hot, every drop atomizes. Steer with the plate position so the stream lands high but not over the top. A stream that is too thin gathers and drips; melt shooting past the plate means the pressure was too high. For two or three minutes the operator stays at the window with the amplitude slider, the turbo button and the plate position."),
            ("clip", "txH397FGTAU", 2397, 36, B),
            ("clip", "naePD8o9_Gk", 1150, 36, B),
            ("clip", "naePD8o9_Gk", 1407, 26, B),
            ("clip", "9kn-HhXCr1o", 1476, 26, B),
            ("clip", "9kn-HhXCr1o", 1506, 22, B),
            ("card", "End of pour", "Turbo to clear the nozzle → sealing rod down → melting pressure → generator stop → ultrasonics stop. Within seconds. Next: part 3, after a run.",
             "When the crucible is empty, one turbo push clears the nozzle. Then sealing rod down, melting pressure, generator stop, ultrasonics stop, all within seconds, because vibrating against solidified metal cracks the plate. Part three covers cooldown, powder collection and cleaning."),
        ],
    },
    "03-after": {
        "title": "rePowder atomizer at BYU VCL, tutorial 3: after a run (draft)",
        "segments": [
            ("card", "Part 3: after a run", "Shutdown · cooldown · opening · collecting powder · cleaning and maintenance. From the AMAZEMET training at BYU, Sep 29–30 2026.",
             "Part three covers what happens after the pour: the shutdown sequence, cooling down, opening the chamber, collecting and labelling the powder, and cleaning."),
            ("gif", "07_end_cooldown",
             "After the pour: sealing rod down, melting pressure, generator stop, ultrasonics stop, and transducer cooling off a minute later. Set the furnace to two hundred fifty for next time. Cooling water stays on until about one hundred degrees. Open the chamber at or below four hundred degrees. Above five hundred, graphite burns in air. Turn pressure control off and press vent first; the door locks while the pressure is off atmospheric. Masks and coat on, then the three clamps. The chamber and cone are water-cooled and wet, but the furnace parts are still hot. Brush plate, bowl, walls and view port down into the container with paper under the opening. Close the container valve before taking it off; argon stays inside it. Pour the powder onto paper, pick out the chunks, sieve, and bag it with a six-character label and a photo on GitHub. At about one hundred degrees shut down the utilities in any order; the program lets you leave at eighty."),
            ("clip", "naePD8o9_Gk", 1884, 46, B),
            ("clip", "naePD8o9_Gk", 1994, 22, B),
            ("clip", "naePD8o9_Gk", 2318, 24, B),
            ("clip", "tfb4fsVNIFI", 0, 30, B),
            ("clip", "txH397FGTAU", 3002, 34, B),
            ("gif", "08_clean",
             "Cleaning depends on what comes next. Same alloy: open, brush, vacuum. A material change takes about an hour: vacuum everything, then wipe. Brushes, paper towels and isopropanol are all you need, plus a stainless scraper for stuck particles. Never grind or clean a plate; dedicate one plate to one alloy and log which plate saw which material, because they last one to three runs. When the furnace is cool, take the rod out, peel the slag from the crucible floor, scrape aluminum off the rod shaft and keep the tip smooth. Look through the nozzle for light; unclog it with a needle or drill it to point seven, and swap it if a new charge would not push through. Inspect the HEPA filter every two months and keep the used one in a metal tray with sand, because fine dust can ignite on its own."),
            ("clip", "FDRTt68Vfvo", 1068, 26, B),
            ("clip", "1F9_4ccwhss", 358, 22, B),
            ("clip", "wRc8p2_FnJo", 520, 34, B),
            ("card", "Lessons from the first unsupervised run (Oct 2)", "Label the plates · fit the transducer cover · metric 17/18 mm tools · draining pressure too high, plate too far · write every reading down · tighten the chilled-water fitting",
             "The team's first run without the trainer, on October second, taught a few things. Label the plates, because they could not be told apart. Fit the transducer cover every time. Keep metric seventeen and eighteen millimeter wrenches and a torque wrench with the machine. The draining pressure was set too high and the plate was too far from the nozzle, so most of the charge flew past un-atomized. Write down every reading, since the machine keeps no log. And tighten the chilled-water fitting that leaked all afternoon. The full procedure, with links to every moment of the videos, is in the repository."),
        ],
    },
}
