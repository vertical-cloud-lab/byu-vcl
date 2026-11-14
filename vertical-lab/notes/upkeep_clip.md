# Maintenance in the workflow: the clip (`upkeep_clip.py`)

Sterling, on PR #318 (2026-11-07): "Something that's been on my mind is maintenance over long-term and how that gets
handled in workflows." `notes/upkeep.md` answers that in words and numbers. This clip shows three of the answers
happening, in the lab as the set-up movie leaves it.

```bash
PREVIEW=1 xvfb-run -a python3 upkeep_clip.py       # the last frame of each sub-step -> /tmp/preview_upkeep_clip.png
ARM_AUDIT=1 xvfb-run -a python3 upkeep_clip.py     # every frame collision-checked -> out/collisions/
VIZ3D_FPS=6 xvfb-run -a python3 upkeep_clip.py     # -> out/mp4/upkeep_clip.mp4, out/upkeep_clip.gif, .json, still
```

`VLAB_ONLY_TRAYS=BE` is the default: only trays B and E, the two the clip presents, are populated. The Shuttles are
clad, so the empty trays aren't seen.

## Round 11: a real person, and everything that moves checked

Sterling on round 10's clip (PR #318, 2026-11-13):
- "Yikes.. That's kind of a cringy looking human, although I don't totally dislike the idea of showing an actual person
  with movement."
- "Also, maintenance step shows a collision. There are probably other collisions and interferences that I didn't catch
  from this."

### The person (`people.py`)

Round 10's figure was drawn here: capsule limbs on a box of a coat with gaps at the shoulders, an egg of a head with a
cap and a black band for glasses, mittens, tubes and blobs. It is replaced by **MakeHuman's base mesh** (hm08: one
smooth body of 13,380 vertices with a face, ears and five fingers a hand) on **MakeHuman's default skeleton and skin
weights**, posed every frame by linear-blend skinning in numpy.

- **Sources.** All three files are CC0 1.0 (section C of MakeHuman's LICENSE.md, "The license for the bundled assets").
  They are fetched at run time into `.cache/makehuman/` and never committed, pinned to commit `a8bc2d5` of
  [makehumancommunity/makehuman](https://github.com/makehumancommunity/makehuman) with their sha256 checked:
  `makehuman/data/3dobjs/base.obj`, `makehuman/data/rigs/default.mhskel` and `default_weights.mhw`. The helper and
  `joint-*` groups are dropped, except the skirt helper (the coat's skirt) and the eyes.
- **Posing.** A walk cycle (hips, knees and ankles, the arms swinging against the legs), the shoes grounded every frame,
  a lean taken 60 % at the hips and 40 % along the lower spine, both arms solved to their hand targets (two-bone IK,
  elbows out and down, the forearm turned to the hand's work), the head turned to what the person looks at, and the
  fingers together and curled. 74 of the skeleton's 163 bones are posed; the face's are folded into the head.
- **Dress.** Cut by region along smooth lines, with the skin weights carried onto each cut:
  - a lab coat over the torso and arms to the wrists, pushed out 12 mm, smoothed, and hung. Each front and back
    profile is bridged over its hollows top to bottom and side to side, so it runs straight from the chest and the
    shoulder blades and doesn't follow the waist or the seat;
  - its skirt to mid-thigh (MakeHuman's skirt helper), tied more to the pelvis than to each thigh, and a collar with
    lapels;
  - a scrub top with its own V-neck; trousers that hang straight from the knee; shoes;
  - blue nitrile gloves 55 mm up the forearm;
  - skin on the face and neck; short hair thinning to its line; brows; eyes; wrap-around safety glasses.
- **Size.** 1.75 m in shoes.
- **The figure's sheet:** [out/upkeep_clip_person.png](../out/upkeep_clip_person.png) (standing, side, back, face,
  walking, pushing, reaching).

### What the arm audit couldn't see, now checked

`collide.Auditor` checks the arms. audit-a's movers check (`collide.Movers`, the default since round 11) checks every
group whose world matrix changes. A body that bends in place, a lean or a reach, doesn't change it. So this clip adds
`PeopleCheck` (`ARM_AUDIT=1`): the person as posed, every part, against everything visible near them; the extraction
table; and tray E with all on it while it is off its dock. It writes `out/collisions/upkeep_clip_movers.json`. A contact
counts if `collide.depth` puts it over 1.5 mm. The shoes on the floor and the castors are allowed 12 mm, and the tray
on the table's rollers 3 mm.

Found and fixed:

| What | Where (round 10's clip) | Fix |
|---|---|---|
| The person walked into unit 2 on its charger | the walk-in, 25 mm | the table starts 200 mm nearer the Shuttles (y -4400): the person behind it starts clear of the MiR's front at -5418 |
| The shoes 25 mm into the floor | every walking frame | the shoes grounded every frame: their lowest point 2 mm over the floor (its tape is 1.5 mm) |
| The gloves in the table's push bar | pushing it in and out | each palm's target settled every frame so the fingers rest on the bar's top, 0.5 mm over it; the person 215 mm back, a 24 deg stoop (the bar is under the hips) |
| The coat in the push bar | pushing | the new coat hangs 190 mm in front of the body's centre; the person stands 215 mm back from the edge |
| The table's frame in the LED-Navigator strip | docked, 266 frames | docked 4 mm off the cover (the strip stands 2 mm proud of it) |
| The table's latch hooks inside the cover's lip | docked | they rest on the lip's top |
| The castors in the floor's tape | rolling | the wheels 2 mm over the floor |
| The iMicro's hood through its own cabinet and through tray E's cameras E0 and E1 | the hood lifting | audit-b (180c0f4): only the lid lifts; the front panel is the cabinet's |
| The person's coat and gloves through camera post E0 and into the iMicro | the tip change | below |

### The tip change, and why it needed a removable panel

The tip sits 260 mm inside the cabinet, 235 mm under the top edge of the iMicro's front panel, which is now fixed. To
reach over that edge and down to the tip, the shoulder would have to be about 1.55 m high and within 0.35 m of the
panel. The 1.75 m figure's shoulder is at 1.40 m upright. The camera masts of E0 and E1 also stand 80 mm in front of the
iMicro, and the table and the tray's margin put the tip 523 mm from where the person stands. So no pose reaches it, and
none would without a step and a closer table.

The clip therefore takes the front panel off as a step of its own: **a removable service panel (assumed: KLA publishes
no service drawing), lifted straight up its guides** (r8_char's `panel` piece, audit-b's 80c752c).
- **The masts.** The person lifts the panel from between the masts, 455 mm in front of them, and keeps their body in
  front of them; only the arms go through. Camera E1 has since moved behind the iMicro (the lab stream's 47219fc,
  because the lid alone swept through it), so only E0's mast stands in front now. The clip reads the masts from the
  scene.
- **How high the panel goes.** The panel goes up 650 mm, 1.55 times its guides' 420 mm. At 420 mm its lower edge hung
  at the height the person's head reaches when they bend in, and the check caught the head in it.
- **Lifting and lowering.** The hands rest on its top edge and lift it 120 mm, settled so they touch without sinking
  in. They come back out of its plane, and it slides on up by itself (assumed: gas-sprung, ours). Lowering is the
  reverse, the hands under its lower edge. The movers check caught the rising panel catching the fingers when it all
  happened at once.
- **The reach.** People.py's skeleton was solved off-line for the reach. The body's centre is 51 mm to the left of the
  tip and 411 mm in front of the masts, bent 42 deg. The head goes past the masts' line and the chest stays 20 mm short
  of it.
- **The stage and the hand.** Before the reach only the x stage moves aside, 100 mm. The carriage stays home, since
  run out to its load position it stands in the hand's way in. Under the head that leaves 120 mm between the
  carriage's rails (1025 mm) and the head (1132 mm). The hand comes in level at that height, a fist round the shaft,
  its top 2 mm under the head and its bottom 5 mm over the rails.
- **The tip.** It is turned out and the new one turned in, in place. Drawn out, its 60 mm shaft would take the hand
  into the rails, so the clip doesn't show that; the caption says the tip is unscrewed and the new one screwed in. A
  real change would want the head raised or the stage lowered: the iMicro's own service procedure isn't modelled
  (assumed).

## The render

Round 11's render (`86bb4d3`), with the new person and every fix above:

- **[MP4](../out/mp4/upkeep_clip.mp4):** 772 frames at 6 fps, 1280 × 720, 128.7 s, 6.4 MB.
  - Part 1, the week: frames 0-78.
  - Part 2, the check: frames 79-399.
  - Part 3, the tip change: frames 401-771. The panel step and the tip change add 12 s.
- **[GIF](../out/upkeep_clip.gif):** 512 px at 3 fps, 4.1 MB. **[Still](../out/upkeep_clip_still.png).**
- **The control chart, both versions:** [today's check](../out/upkeep_clip_chart.png) and
  [the what-if](../out/upkeep_clip_chart_whatif.png).
- **Audits** (`ARM_AUDIT=1`, the stricter rules, the default since round 11): see "Collisions, before and after" below.
- **Cost:** 19.7 min in one slot (02:58-03:18 UTC), `VLAB_ONLY_TRAYS=BE`. The part-3 checks (`UPKEEP_FROM=3`, a preview
  and an audit in one slot) took 12-14 min each, and there were five of them.

Round 10's render, for the record: 701 frames, 116.8 s; its arm audit was 534 frames, 0 in collision, with nothing
else checked.

- **Fixed after the preview (round 10's continuation):**
  - **The reading's camera.** It had the weight behind the doser's vertical extrusion. It now looks along the
    close-up's clear line of sight, nearer, with the weight a third of the way across, clear of the chart.
  - **The tip change's camera.** It sat behind the person's shoulder. It now looks along the extraction view's line,
    closer, with the person to the left of the iMicro.
  - **The captions.** They no longer say the HR-202i calibrates itself, and they say the check weighs ten times.
  - **The fused-silica check** is the arm's next job on tray E. The clip had claimed it ran while the tray went back
    up.

## What it shows

### 1/3 The week

`out/upkeep_week.png`, full frame: one steady-state week of the model with every station's bookings. Process steps
are grey; upkeep is coloured by who does it:
- the arm's checks at night;
- the person's tasks on the weekday shift, round the crucible hours;
- vendors;
- faults waiting for the next shift.

### 2/3 A check between jobs

`upkeep.py` task `bal_weights`: daily, the arm, 0.2 h, at night.
- **The weight.** The A&D HR-202i under the multi-doser's dose point is checked with a 100 g OIML class E2 weight.
  The weight lives in tray J's store and rides on the MiR's deck in a low seat of its own (ours).
- **Into the balance.** The arm takes the weight by its body, as weight tongs would, and stands it on our vessel
  shuttle's fork outside the doser. The shuttle carries it through the balance's side door onto the pedestal on the
  pan and backs out, as round 9's 8:37 clip sets a vial.
- **The reading.** It settles to 100.0001 g. The shuttle lifts the weight off and back ten times, for USP <41>'s
  repeatability (one is shown). The mean goes on a control chart against the lab's limits.
- **The what-if.** A reading outside the limits is repeated once. Still out, the doser is flagged, no doses are booked
  on it, and a person's task is booked for the next shift.
- **Back.** The weight goes back to its seat on the deck and tray B goes back up.

**No internal mass.** A&D's [HR-i manual](https://www.aandd.jp/products/manual/balances/hr-i.pdf) calibrates the
HR-202i "using a weight that you have". So this weight is its daily check and, once a month, its calibration
(`bal_cal`). The first version of the clip said the balance calibrated itself with a built-in mass, which is wrong for
the HR-i series.

### 3/3 A person's task, with the tray pulled out

`upkeep.py` task `nano_tip`: every 600 indentation runs, a person, the tray pulled out, 2 h.
1. Tray E comes to Shuttle 1's opening.
2. The MiR250 + UR10e drives off to Shuttle 2, which carries on working. Only Shuttle 1's opening is taken.
3. A person rolls an extraction table to the opening and docks it against the cover's lip.
4. The tray comes out onto the table's rails. Kardex's Shuttle XP brochure, p. 6: "With the full tray extraction
   device, a tray is placed in front of the access opening" (notes/maintenance.md). Off its dock the tray has no
   power, so the iMicro is shut down first.
5. The iMicro's hood lifts. The person, in gloves and safety glasses, unscrews the Berkovich tip and fits the new one.
6. The hood comes down, the tray rolls back onto its dock and the table goes away.
7. The MiR docks at Shuttle 1 again. The new tip's area function on fused silica is the arm's next job on tray E
   (`nano_fs`), before any sample, and the run count starts from zero.

At 304 alloys a year the tip falls due about every two years. So the model's first year has no planned extraction,
only one repair: a broken tip, with a 72 h wait for the part.

## What it assumes

| What | Value | Basis |
|---|---|---|
| Check weight | 100 g OIML E2, Ø24 mm, 37.5 mm tall, knob form | OIML R 111-1's shape, sized from the mass at 8.0 g/cm³ (estimated); E2's ±0.16 mg tolerance from its Table 1 |
| Limits | action ±0.3 mg, warning ±0.2 mg | ours: the HR-202i's ±0.2 mg linearity plus the E2 tolerance |
| Readings on the chart | 30 working days | illustrative, seeded |
| The weight's seat on the deck | 64 mm block, 3 mm pocket | ours |
| Extraction table | 2,360 × 900 mm, rails at the opening's 854 mm | assumed: Kardex publishes no size for its extraction device or its cart (notes/maintenance.md has the questions to ask) |
| The person | 1.75 m: lab coat, nitrile gloves, safety glasses | drawn here (`Person`): no figure existed in the codebase. The finale (`timelapse.py`) uses the same figure |
| The tip change | 2 h, every 600 runs | assumed (`upkeep.py nano_tip`) |

The person's arms are a two-link solve to each hand target, and their walk is a simple gait. Neither is checked for
contact with the tray or the table, so their hands are illustrative. `ARM_AUDIT` checks only the UR10e.
