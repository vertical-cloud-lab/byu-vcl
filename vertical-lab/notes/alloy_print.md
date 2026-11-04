## The alloy route, chapter 3: sieve and print (`alloy_print.py`, `sieve_station.py`)

The atomized powder goes through a sieving cell, into the Aconity MIDI's powder supply, and the MIDI prints the
plate that chapter 4 ([`alloy_workflow.py`](../alloy_workflow.py)) takes out.
[GIF](../out/alloy_print.gif), [MP4](../out/mp4/alloy_print.mp4), [still](../out/alloy_print_still.png),
[steps](../out/alloy_print.json), stills of the [cell](../out/alloy_print_cell.png) and the
[tipper](../out/alloy_print_tipper.png). 198 s at 1280 × 720 and 15 fps (re-rendered in round 5's fixes, with the MiR250 at its
0.3 m/s² and off the rePowder on an S-curve); the GIF is 640 × 360 at 5 fps.

**Round 5 (PR #318): no person.** Sterling, on "a person still takes the sieve stack apart": "The idea would be to
have the robot take care of this, or to use something more automated. ... some kind of clamping mechanism or clever
hardware-centric design." The arm now builds the stack, takes it apart, tips each sieve into its own jar and puts
the set back, with no second arm. What it takes is in [`sieve_station.py`](../sieve_station.py).

```bash
xvfb-run -a python3 alloy_print.py            # 40+ min on the 4-core runner when other renders share it
PREVIEW=1 xvfb-run -a python3 alloy_print.py  # last frame of each sub-step -> /tmp/preview_alloy_print.png
```

| Step | What happens | Who does it |
|---|---|---|
| 1 | MiR250 from the rePowder to the sieving cell | MiR |
| 2 | The stack built on the AS 200 from the Al set's stand, pan first (the pan in full, the rest sped up); the container from the MiR, tipped into the No. 60, back on the MiR; the lid from the tipper's roof, over the rods; both knobs turned; the stack shakes, see-through; the fractions panel | arm, then the AS 200 |
| 3 | Knobs back, lid back on the tipper's roof; each sieve, top down, into the tipper's cradle, which clamps it, turns it over the funnel and knocks the frame; the turntable puts the right jar under the funnel; the sieve back on the stand; the LPBF jar into a cup on the MiR | arm, tipper |
| 4 | MiR to the Aconity; door opens; supply piston drops; the arm carries the jar in, level, and pours; jar back on the MiR; door shuts | arm |
| 5 | The print as a time-lapse, cut open; MiR back to x = 1400 | the MIDI |

### The cell

| Part | What it is | Why |
|---|---|---|
| **Handling tab** on each sieve and the pan | 12 mm stainless tab at the front of the frame, 40 mm out, gripped like the plate's 12 mm lug (2F-85 at 0.88), fingers closing vertically | The 2F-85 opens 85 mm and a sieve is 207 mm across. Nested sieves leave only the top one's rim free, and a tab 50.8 mm above the next one leaves room for the fingers |
| **The Al set's stand** | A plate with a lip that takes a skirt, right of the shaker. The set waits nested in reverse: No. 60 at the bottom, pan on top (the pan sits on the No. 325's rim) | Off the stand top first, the pieces go onto the shaker pan first. Off the shaker top first, they go back in storage order, ready for the next run. No rack, no second arm |
| **Tipper** | A C-shaped cradle on a horizontal shaft (pneumatic rotary actuator), open at the front for the tab and the fingers; three pads clamp the frame; a pneumatic knocker taps the frame | The lab tips each sieve over a funnel by hand (below) |
| **Funnel and jars** | A Ø252 funnel over a turntable with five 250 mL jars, labelled: > 250, 150–250, 106–150, 63–106 and < 63 µm (LPBF). The No. 325 and the pan share the LPBF jar | Each fraction in its own jar |
| **Lid park** | The AS 200's clamping lid rests on the tipper's roof | The arm turns the two knobs, as before |
| **Enclosure** | Downdraft enclosure on the bench, open at the front, extraction through the roof; a ground bar on the back panel and green-yellow straps to the shaker, tipper, stand | Al under 63 µm is among the most ignitable metal dusts (DAL's sieve note); Sterling asked for the grounding to be shown on DAL #175 |

**Cleaning between alloys, from DAL #234's Edison answer** (Nov 3): use a separate sieve set per alloy family
("cleaning lowers carryover but can't prove there is none"), so the Cu-alloy set lives on its own stand. Recover
powder dry by tapping the frame, not the mesh; brush only No. 100 and coarser, lightly, from the underside; never a
wire brush or an air jet on the cloth; sonicate finer meshes 3–5 min in water with a mild detergent, then rinse and
dry upright. The tipper's knocker does the first. The clip doesn't show a brush or a bath: Retsch's UR 1 bath takes
one 200 × 50 mm sieve at a time (5.7 L, 35 kHz, timer 0–15 min, Retsch data sheet), so a bath step would be one
more station on the bench.

**Passes.** DIN 66165 allows at most 26 cm³ on a 200 mm, 63 µm sieve, about 35–40 g of powder at 1.3–1.5 g/cm³
(Retsch's table, via DAL PR #175). Four cups charge 157 g, so a run is about four passes; one is shown.

**What the lab does now** (Gage Erickson's videos "10/29/2026 Atomizer 630 Bronze cleaning and sieving", Videos
1–3, unlisted on the lab's channel, fetched at 144p by the parent session): the 8 in sieve shaken by hand over its
pan, the retained powder tipped out over a white plastic funnel into glass jars, the jars labelled on a P-touch and
weighed, the sieves brushed and wiped with Kimwipes. The NAB result is three jars (< 63 µm, 64–250 µm and
> 251 µm: 188 g, 827 g and 182 g of 1,938 g melted over two runs, DAL #219).

**Hand-offs.**
- **Start:** the MiR at x = −3487, y = −2230, arm parked, the container in its cup (as before).
- **End:** as before: the MiR at x = 1400, `MIR_Y`, arm parked; the Aconity closed and opaque; the plate under a
  30 mm powder cake; chapter 4's first camera. The MiR now has two cups: the empty container's and the empty jar's.
- **Where the cell stands:** the bench is 1065 × 600 × 700 mm (assumed), x from −2515 to −1450, between the
  rePowder's heat exchanger and the VLM. Tipper at x = −2350, AS 200 at −1971, stand at −1623. `setup_lab.py` puts
  the AS 200 on tray F; this chapter keeps it beside the rePowder, as the round-4 note on Al dust suggests. The
  two layouts still disagree.

### Sources and assumptions

| Item | Value | Status |
|---|---|---|
| Shaker, lid, knobs, the fractions' colours | `instruments_char.sieve()`: Retsch AS 200 control | published |
| Sieves | DAL's 8 in, 2 in deep, 304 stainless McMaster stack (DAL PR #175), profiles from DAL's sieving model; here each its own group with a tab | DAL; the tab is ours |
| Stand, tipper, funnel, turntable, jars, enclosure, straps | `sieve_station.py` | **assumed, our design** |
| LPBF cut | No. 325 + pan, 20–63 µm; under 20 µm about 0.05 % (DAL) | from `instruments_char.md` |
| Powder in each jar | drawn heights, an example | **not data** |
| Supply fill caption | full MIDI cylinder about 440 g, its 55 mm reduction kit about 30 g (DAL #138); 1,080 g of 630 bronze in one run of the 225 cm³ crucible (DAL #219) | DAL |
| Gripper closures | 12 mm tab and handle 0.88, 36 mm crossbar 0.59, 54 mm knob 0.36, 70 mm jar 0.18 | approximate |

### Open questions and simplifications

- **Can the 2F-85 hold a loaded sieve by one tab?** About 0.7 kg 100 mm from the tab is about 0.7 N·m on the
  fingers. That is well inside the gripper's rating, but the tab has to be stiff and the pads must not slip.
- **The cradle's pads clamp a 0.6 mm wall.** A real cradle might clamp the rim lip instead, or take the sieve in a
  collet. Not checked against a real sieve.
- **Knocking the frame isn't brushing.** Fines left in the 45 µm cloth stay there until the set is cleaned; DAL
  #234 says that is the reason for a set per alloy family.
- **The jars are open.** A capped jar would need a decapper, or the jar goes to the MIDI open, as here.
- **The bench's sieving takes about 2 min on screen.** A real run is four passes of minutes each.
- **The lid is put back by the arm**; Fritsch's ANALYSETTE 3 PRO, with motor-tensioned clamping, would take the
  knobs out of the job.
- **The arm pours into the MIDI's supply through the door**, as before; in practice the MIDI's supply is filled by
  hand.
