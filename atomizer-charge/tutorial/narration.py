"""Narration and segment list for the Al cup and plug tutorial (#248). Edit here, then run build.py.

Every sentence is (caption, spoken). The caption is burned into the video as written; `spoken` is what the voice is
given, spelled out where the TTS would misread it ("6063", "1640T16", "#60"). None means the caption is spoken as is.
Each sentence is synthesized on its own, so the captions are timed exactly.

Numbers are the as-made ones from #222 (Gage's cups, Ronnie's plugs), not the drawing's: the comparison is on the
"table" slide. The press-version section is sgbaird's note on #248 (2026-10-01).

Segment kinds:
  card    title card, narration over it
  image   a still (render, drawing or photo) with optional notes beside it
  clip_vo Gage's lathe Short from `start` (s), Steffan over it, the shop audio kept quietly underneath
  clip    the Short from `start` to `end` with its own audio, captioned with what is said
  gif     a CAD clip from PR #232, one list of sentences per step; each step plays, then holds while the voice finishes
  slide   text slide (bullets or a table)
"""

VOICE = "en-US-SteffanNeural"
SHORT = "z6rwmQW_3Vg"  # "Lathe turning aluminum crucibles for atomizer experiments" (Gage, 1:35)
GAGE = "Gage Erickson · lathe footage, Sept 2026"

SEGMENTS = [
    ("card", {
        "title": "Making the aluminum cups and plugs",
        "sub": "The 6063 cups that carry powder into the rePowder atomizer, and their vented plugs",
        "footer": "BYU Vertical Cloud Lab · issues #222 and #248",
        "chapter": "Intro",
    }, [
        ("This tutorial shows how to make the aluminum cups and plugs that carry powder into the rePowder atomizer.",
         "This tutorial shows how to make the aluminum cups and plugs that carry powder into the re Powder atomizer."),
        ("Each cup is turned from 3/4 inch 6063 aluminum bar, filled with alloy powder, and closed with a plug that "
         "has a small air hole through it.",
         "Each cup is turned from three-quarter-inch, sixty sixty-three aluminum bar, filled with alloy powder, and "
         "closed with a plug that has a small air hole through it."),
        ("You'll see the first cups being made on the lathe, the same steps from the CAD, the numbers to use, and "
         "what changes for the hydraulic-press versions.", None),
    ]),
    ("image", {
        "title": "Where the cups go",
        "path": "cad/renders/crucible_cutaway.png",
        "bg": "light",
        "notes": ["Cups stand plug-up around the sealing rod", "Powder drops into metal that's already liquid",
                  "The air hole points up"],
        "chapter": "Where the cups go",
    }, [
        ("First, where they end up.", None),
        ("The cups stand plug-up in the graphite crucible, around the sealing rod.", None),
        ("Standing plug-up means the powder drops into metal that's already liquid, and the air hole points up.", None),
    ]),
    ("image", {
        "title": "The bar: 3/4 in 6063 aluminum",
        "path": "tutorial/assets/bar_1640T16.jpg",
        "bg": "dark",
        "notes": ["McMaster-Carr 1640T16", "Ø3/4 in, 2 ft long", "Cup + plug: about 3.5 in of bar",
                  "Reorder: $21.65 for 2 ft, $36.08 for 4 ft (prices from 9/17)"],
        "chapter": "The bar",
    }, [
        ("Everything is turned from this bar: 3/4 inch 6063 aluminum rod, McMaster part 1640T16, sold in "
         "2 foot lengths.",
         "Everything is turned from this bar: three-quarter-inch, sixty sixty-three aluminum rod, McMaster part "
         "sixteen forty T sixteen, sold in two-foot lengths."),
        ("A cup and its plug together use about 3.5 inches of bar.",
         "A cup and its plug together use about three and a half inches of bar."),
        ("Check what's left before you start, and reorder if it's running short.", None),
    ]),
    ("clip_vo", {
        "title": "Mark and saw the blanks",
        "start": 0.0,
        "notes": ["Mark about 3 in per cup", "Finished length: 2.750 in", "The extra 1/4 in is for facing"],
        "credit": GAGE,
        "chapter": "On the lathe",
    }, [
        ("Here's how the first cups were made.", None),
        ("Gage marked the bar at about 3 inches per cup: a quarter inch over the finished length, so both ends can "
         "be faced.",
         "Gage marked the bar at about three inches per cup: a quarter inch over the finished length, so both ends "
         "can be faced."),
    ]),
    ("clip", {
        "title": "The plan, in Gage's words",
        "start": 27.7, "end": 42.0,
        "captions": [
            (28.8, 33.5, "We're going to cut this on the band saw [into] pieces, and then we're going to need to "
                         "drill out on the lathe the interior hole."),
            (33.5, 42.0, "And then we'll also turn out on the lathe the... plugs."),
        ],
        "notes": ["Band saw: blanks", "Lathe: drill the hole", "Lathe: turn the plugs"],
        "credit": GAGE,
    }, []),
    ("clip_vo", {
        "title": "Mark and saw the blanks",
        "start": 43.0,
        "notes": ["Three 3 in blanks", "Plus about 1 3/8 in for plugs"],
        "credit": GAGE,
    }, [
        ("The blanks were cut on the band saw: three pieces 3 inches long, plus a piece about 1 3/8 inches long for "
         "the plugs.",
         "The blanks were cut on the band saw: three pieces, three inches long, plus a piece about one and "
         "three-eighths inches long, for the plugs."),
    ]),
    ("clip", {
        "title": "Center drill, then the 1/2 in drill",
        "start": 62.2, "end": 71.9,
        "captions": [
            (62.2, 65.8, "Poke it just a little bit, that's all you need, huh? / You just need a guide hole."),
            (65.8, 71.9, "So we just use the center drill, poke out your hole, and we'll put our 1/2-inch drill in."),
        ],
        "notes": ["Center drill: a guide hole only", "Then the 1/2 in drill", "from the tailstock"],
        "credit": GAGE,
    }, []),
    ("clip", {
        "title": "Face both ends to 2.750 in",
        "start": 74.1, "end": 81.4,
        "captions": [
            (74.1, 81.4, "This is the first one: we cut the ends so they're flat on both sides, and now this is "
                         "perfectly at 2.75 inches."),
        ],
        "notes": ["Face both ends flat", "Length 2.750 in"],
        "credit": GAGE,
    }, []),
    ("clip_vo", {
        "title": "Drill 1/2 in, 2.25 in deep",
        "start": 86.6,
        "notes": ["1/2 in drill, 2.25 in deep", "The drill point leaves a pointed bottom: fine",
                  "Each cup in its own bag"],
        "credit": GAGE,
    }, [
        ("The half-inch drill then went in 2.25 inches deep. The drill tip leaves a pointed bottom, and that's fine.",
         "The half-inch drill then went in two and a quarter inches deep. The drill tip leaves a pointed bottom, "
         "and that's fine."),
        ("Each finished cup went into its own bag.", None),
    ]),
    ("gif", {
        "title": "The cup, step by step (CAD)",
        "gif": "machining_cup",
        "chapter": "The cup, step by step",
        # frame index where each step starts; steps follow the clip's own titles
        "steps": [0, 13, 25, 26, 43],
    }, [
        [("Here are the same steps from the CAD. One: face the end of the bar.", None)],
        [("Two: center drill, then drill the pocket. The first cups used a 1/2 inch drill, 2.25 inches deep.",
          "Two: center drill, then drill the pocket. The first cups used a half-inch drill, two and a quarter "
          "inches deep."),
         ("Drilling is shown cut in half, so you can see inside.", None)],
        [("The drawing follows a 31/64 drill with a reamer or a boring bar, for a smooth, round hole on size.",
          "The drawing follows a thirty-one sixty-fourths drill with a reamer or a boring bar, for a smooth, round "
          "hole on size."),
         ("The first cups skipped that step, but the press versions will want it.", None)],
        [("Three: part it off. The cups so far are 2.75 inches long.",
          "Three: part it off. The cups so far are two point seven five inches long.")],
        [("That's the cup: a 1/2 inch hole, 2.25 inches deep, a 1/8 inch wall, and a solid bottom.",
          "That's the cup: a half-inch hole, two and a quarter inches deep, an eighth-inch wall, and a solid "
          "bottom.")],
    ]),
    ("gif", {
        "title": "The plug, step by step (CAD)",
        "gif": "machining_plug",
        "chapter": "The plug, step by step",
        "steps": [0, 15, 21, 30, 37, 53],
    }, [
        [("Now the plug. The CAD calls it the lid.", None),
         ("Make the cup first, then its plug. Measure that cup's hole, and turn the plug 0.0005 to 0.0008 inches "
          "bigger, so it presses in.",
          "Make the cup first, then its plug. Measure that cup's hole, and turn the plug five to eight "
          "ten-thousandths of an inch bigger, so it presses in.")],
        [("Taper the nose slightly. That's the end that goes in, and the taper starts it in straight.", None)],
        [("Drill the air hole straight through the middle, with a #60 drill.",
          "Drill the air hole straight through the middle, with a number sixty drill.")],
        [("Break the top edge. It's a deburr only, and plays no part in the fit.", None)],
        [("Part it off. The plugs so far are 9/16 inch long.",
          "Part it off. The plugs so far are nine-sixteenths of an inch long.")],
        [("One plug per cup, turned to that cup's measured hole. The first plugs came out at 0.508 inch diameter.",
          "One plug per cup, turned to that cup's measured hole. The first plugs came out at point five oh eight "
          "inches in diameter."),
         ("Measure every hole, rather than reusing that number.", None)],
    ]),
    ("image", {
        "title": "Where the #60 drill is",
        "path": "tutorial/assets/wire_gauge_drawer.jpg",
        "bg": "dark",
        "notes": ["Wire-gauge drill drawer", "#60 (0.040 in): the plug's air hole",
                  "#70: the graphite nozzle", "Ask a lab assistant to open it"],
        "chapter": "Where the #60 drill is",
    }, [
        ("The #60 drill for the air hole is in the wire-gauge drill drawer, next to the #70 used on the graphite "
         "nozzle.",
         "The number sixty drill for the air hole is in the wire-gauge drill drawer, next to the number seventy "
         "used on the graphite nozzle."),
        ("Ask a lab assistant to open it.", None),
    ]),
    ("gif", {
        "title": "Why the plug has an air hole",
        "gif": "fill_and_vent",
        "chapter": "Why the air hole",
        "steps": [0, 15, 27],
    }, [
        [("Filling comes later, but it explains the hole.", None),
         ("Tap the powder down to the line where the plug will sit, and weigh what goes in: about 8.7 grams per cup.",
          "Tap the powder down to the line where the plug will sit, and weigh what goes in: about eight point seven "
          "grams per cup."),
         ("A caliper depth rod set to 9/16 inch marks the line.",
          "A caliper depth rod set to nine-sixteenths of an inch marks the line.")],
        [("Then the plug goes in flush.", None)],
        [("The chamber is pumped down before melting.", None),
         ("With the hole, the air under the plug has somewhere to go. Without it, the air has to come out through "
          "the powder.", None)],
    ]),
    ("slide", {
        "title": "Made so far vs. the drawing",
        "chapter": "The numbers",
        "table": {
            "head": ["", "Made so far (keep doing this)", "Drawing (for reference)"],
            "rows": [
                ["Bar", "3/4 in 6063, McMaster 1640T16", "same"],
                ["Cup length", "2.750 in", "2.500 in"],
                ["Cup hole", "1/2 in drill, 2.25 in deep (pointed bottom)",
                 "31/64 drill, then bore or ream to .500, 1.875 in deep"],
                ["Plug diameter", "that cup's measured hole + .0005 to .0008 in (first ones: .508)", "same rule"],
                ["Plug length", ".5625 in (9/16)", ".375 in"],
                ["Air hole", "#60 (.040 in)", "1/16 in"],
                ["Dose", "about 8.7 g per cup", ""],
            ],
        },
    }, [
        ("Here are the numbers in one place.", None),
        ("Keep making cups the way the first ones were made, so the runs stay comparable.", None),
        ("Cups 2.75 inches long, with a 1/2 inch hole 2.25 inches deep. Plugs 9/16 inch long, with a #60 air hole, "
         "sized to each cup.",
         "Cups two point seven five inches long, with a half-inch hole two and a quarter inches deep. Plugs "
         "nine-sixteenths of an inch long, with a number sixty air hole, sized to each cup."),
        ("The drawing's numbers are the original design, shown for reference.", None),
    ]),
    ("slide", {
        "title": "Four rules",
        "chapter": "Four rules",
        "bullets": [
            "1. Cup first, then its plug: that cup's hole + .0005 to .0008 in, never more",
            "2. Every plug gets an air hole, straight through the middle",
            "3. Taper the plug's leading end so it starts in straight",
            "4. Keep each plug bagged with its own cup: they aren't interchangeable",
            "No marker, scribing or stamps. Wipe with IPA, dry, weigh to 0.01 g, label the bag",
        ],
    }, [
        ("Four rules.", None),
        ("One: make the cup first, then its plug, sized to that cup. Never more than 0.0008 inches over: tighter "
         "than that permanently stretches the cup wall.",
         "One: make the cup first, then its plug, sized to that cup. Never more than eight ten-thousandths over: "
         "tighter than that permanently stretches the cup wall."),
        ("Two: every plug gets an air hole, straight through the middle.", None),
        ("Three: taper the plug's leading end, so it starts in straight.", None),
        ("Four: keep each plug bagged with its own cup. They aren't interchangeable.", None),
        ("Don't mark, scribe or stamp the parts. Wipe them with isopropyl alcohol, let them dry, weigh each one to "
         "0.01 gram, and label the bag.",
         "Don't mark, scribe or stamp the parts. Wipe them with isopropyl alcohol, let them dry, weigh each one to "
         "a hundredth of a gram, and label the bag."),
    ]),
    ("slide", {
        "title": "Hydraulic-press versions",
        "chapter": "Hydraulic-press versions",
        "bullets": [
            "Some cups will be compacted in the hydraulic press. For those (Sterling's note on #248):",
            "1. The plug slides in and out of the cup, rather than pressing in",
            "2. A fairly clean, smooth bore (doesn't have to be perfect): drill 31/64, then ream or bore to .500",
            "3. The plug has to reach the powder and compact it: a straight bore, the same size all the way down",
        ],
    }, [
        ("Some cups will be compacted in the hydraulic press, and those change in three ways.", None),
        ("First, the plug has to slide in and out of the cup, rather than press in.", None),
        ("Second, the inside of the cup should be fairly clean and smooth. It doesn't have to be perfect: drill "
         "undersize, then ream or bore to size.", None),
        ("Third, the plug has to be able to travel down to the powder and compact it, so the hole must be straight, "
         "and the same size all the way down.", None),
    ]),
    ("image", {
        "title": "The drawing",
        "path": "cad/drawings/charge_parts.png",
        "bg": "light",
        "notes": [],
        "chapter": "The drawing, and one request",
    }, [
        ("The full drawing, the CAD and these animations are in pull request 232, linked from issue 222.", None),
        ("The lengths on the drawing are design values. For the standard cups, go by the numbers in this video.",
         None),
        ("One request: nobody has filmed the plugs being turned yet. Please record that step this time, with the "
         "chest camera.", None),
    ]),
    ("card", {
        "title": "Links",
        "sub": "github.com/vertical-cloud-lab/byu-vcl · issues #248 and #222 · PR #232 (drawing, CAD, animations)",
        "lines": ["Lathe footage: Gage Erickson, youtube.com/shorts/z6rwmQW_3Vg",
                  "Animations: atomizer-charge/cad/machining.py (PR #232), numbers corrected on screen",
                  "Narration: Microsoft Edge TTS voice en-US-SteffanNeural"],
        "footer": "BYU Vertical Cloud Lab",
        "chapter": "Links",
    }, [
        ("Links to everything are in the description.", None),
    ]),
]
