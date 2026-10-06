"""Short captions and narration for the slide versions of the 3D animations (edit here, then run build_ppt.py).

Made for a PowerPoint slide: one short caption at a time and one short spoken line per caption. The single-step clips play
the animation at its own speed. The summary (../viz3d/steps.py anim_summary) is one condensed take through the furnace,
the stack, the melt and the pour, with the fasteners sped up. The rules, which build_ppt.py checks:
  - a caption has at most MAX_WORDS words (a number and its unit, "65 N·m", count as two);
  - a caption stays up at least MIN_DWELL seconds;
  - its line is spoken while it is up, starting LEAD s after it appears and done SPARE s before the next one.

Each line is (sub-step, offset, caption, narration): the caption appears `offset` seconds after that sub-step of the
animation starts (../viz3d/out/clean/<name>.json) and stays until the next caption appears, or the video ends. A long
sub-step can carry two captions (2a.4: the door and the nut, then how tight). A clip can set its own "end_hold" (s).
"""
MAX_WORDS = 6
MIN_DWELL = 4.0
LEAD = 0.25
SPARE = 0.3
END_HOLD = 1.0           # s the last frame is held after the animation ends

CLIPS = {
    "03_furnace_load": {
        "title": "Atomizer slide clip: loading the furnace (draft 1)",
        "summary": "The furnace step of tutorial 1, cut for a slide: the lid and lever, the crucible into the coil, "
                   "the graphite nut from below, insulation, thermocouple, sealing rod, the charge and the lid.",
        "lines": [
            ("2a.1", 0.0, "Open the lid, lever up",
             "Start cold. Open the furnace lid, and swing the lever up."),
            ("2a.2", 0.0, "Screw the holder into the crucible",
             "On the bench, screw the nozzle holder into the crucible."),
            ("2a.3", 0.0, "Lower the crucible into the coil",
             "Bottom insulation first, then lower the crucible straight into the coil."),
            ("2a.4", 0.0, "Door open, nut on from below",
             "Open the chamber door, and thread the graphite nut on from below."),
            ("2a.4", 5.3, "Snug, never forced",
             "Snug, but never forced. Overtightened graphite cracks."),
            ("2a.5", 0.0, "Side and top insulation",
             "Then the side and top insulation."),
            ("2a.6", 0.0, "Thermocouple in, back right",
             "The thermocouple goes in at the back right."),
            ("2a.7", 0.0, "Sealing rod in, before metal",
             "The sealing rod goes in before any metal."),
            ("2a.8", 0.0, "Lever down, safety pin in",
             "Swing the lever down, and push the safety pin in."),
            ("2a.9", 0.0, "Charge: 250–300 g of rods",
             "Now the charge: two hundred fifty to three hundred grams."),
            ("2a.10", 0.0, "Close the lid",
             "Close the lid, and latch it just tight enough to seal."),
        ],
    },
    "02_stack": {
        "title": "Atomizer slide clip: the ultrasonic stack and the door (draft 1)",
        "summary": "The ultrasonic-stack step of tutorial 1, cut for a slide: transducer, booster and sonotrode with "
                   "their torques, into the door, the plate, the scan and wet test, the cover, then the door shut and "
                   "bolted.",
        "lines": [
            ("2c.1", 0.0, "The stack: transducer first",
             "The ultrasonic stack goes in last, starting with the transducer."),
            ("2c.2", 0.0, "Booster on: 65 N·m",
             "Then the booster, at sixty-five newton meters."),
            ("2c.3", 0.0, "Sonotrode on: 60 N·m",
             "The sonotrode, at sixty newton meters."),
            ("2c.4", 0.0, "Slide it into the door",
             "Slide the stack into the door housing."),
            ("2c.5", 0.0, "Plate on: 50 N·m",
             "Then the plate, at fifty newton meters."),
            ("2c.6", 0.0, "Scan: one peak near 40 kHz",
             "Scan for one wide peak, near forty kilohertz."),
            ("2c.7", 0.0, "Wet test: whole plate atomizes",
             "A drop of water should atomize over the whole plate."),
            ("2c.8", 0.0, "Cover on, cable, cooling air",
             "Bolt the cover on, then the cable and the air."),
            ("2c.9", 0.0, "Swing the door shut",
             "Swing the door shut, with the plate under the nozzle."),
            ("2c.10", 0.0, "Three bolts, star knobs tight",
             "Swing the three bolts over, and tighten the knobs."),
        ],
    },
    "06_pour": {
        "title": "Atomizer slide clip: the pour (draft 1)",
        "summary": "The pour step of tutorial 2, cut for a slide: the melt held near 800 °C, the vibration on and the "
                   "furnace pressure raised above the chamber's, the sealing rod lifted, a turbo push to heat the plate, "
                   "then every drop atomizing and the powder running down into the container.",
        "tutorials": ("02-during",),
        # 5.2 (3.5 s), 5.3 (3.0 s) and 5.5 (3.5 s) are shorter than MIN_DWELL: 5.2's caption covers 5.3 too, and
        # 5.5's runs 0.5 s into 5.6
        "lines": [
            ("5.1", 0.0, "Melt held near 800 °C",
             "The melt is held near eight hundred degrees, under argon."),
            ("5.2", 0.0, "Vibration on, then furnace pressure up",
             "Switch the vibration on, then raise the furnace pressure above the chamber's."),
            ("5.4", 0.0, "Sealing rod up: melt pours",
             "Lift the sealing rod, and the melt pours."),
            ("5.5", 0.0, "Turbo push heats the plate",
             "A short turbo push heats the plate."),
            ("5.6", 0.5, "Hot plate: every drop atomizes",
             "Once the plate is hot, every drop atomizes."),
            ("5.7", 0.0, "Powder runs into the container",
             "The droplets freeze in the argon, and the powder runs down into the container."),
            ("5.8", 0.0, "The pour lasts 2–3 minutes",
             "The pour lasts two to three minutes, with an operator watching at the window."),
            ("5.9", 0.0, "Crucible empty: the pour ends",
             "When the crucible runs empty, the pour is over."),
        ],
    },
    "summary": {
        "title": "Atomizer slide clip: from loading to powder in 44 seconds (draft 2)",
        "summary": "A whole run in one condensed take, for a slide: the graphite crucible into the induction coil, the "
                   "sealing rod and the charge, the ultrasonic stack into the chamber door, then melting under argon, "
                   "the coil's pulses stirring the melt up the sealing rod, and pouring onto the vibrating plate, which "
                   "atomizes the melt into powder.",
        "note": "Condensed: the fasteners (holder, nut, thermocouple, lever, booster, sonotrode, plate, cover and bolts) "
                "are sped up, and the checks, gas washes and holds are left out. Each move is followed by a short pause, "
                "and the furnace, the stack and the run are a longer pause apart. The parts follow the same paths, in "
                "the same order, as in the full step animations.",
        "tutorials": ("01-before", "02-during"),
        "end_hold": 0.7,
        # also cut into one part per step, at these sub-steps' starts: videos/summary_<suffix>.mp4
        "parts": [("1_furnace", "F.1"), ("2_stack", "S.1"), ("3_run", "R.1")],
        "lines": [
            ("F.1", 0.0, "Graphite crucible into the induction coil",
             "A graphite crucible, with a nozzle, goes into the coil."),
            ("F.4", 0.0, "Fastened below, then insulated",
             "It's fastened from below, then insulated."),
            ("F.7", 0.0, "Sealing rod in, then the metal",
             "A sealing rod plugs the nozzle; then the metal."),
            ("S.1", 0.0, "Ultrasonic stack mounts in the door",
             "The forty kilohertz ultrasonic stack mounts in the door."),
            ("R.1", 0.0, "Argon fill, induction melting and stirring",
             "Under argon, the coil melts and stirs the metal."),
            ("R.2", 0.0, "Melt pours onto the vibrating plate",
             "The rod lifts; melt hits the vibrating plate."),
            ("R.3", 0.0, "Droplets freeze into metal powder",
             "It flies off as droplets that freeze into powder."),
        ],
    },
}
