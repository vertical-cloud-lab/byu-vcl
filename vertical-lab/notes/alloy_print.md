## The alloy route, chapter 3: sieve and print (`alloy_print.py`)

The atomized powder goes through the sieve shaker, into the Aconity MIDI's powder supply, and the MIDI prints the
plate that chapter 4 ([`alloy_workflow.py`](../alloy_workflow.py)) takes out.
[GIF](../out/alloy_print.gif), [MP4](../out/mp4/alloy_print.mp4), [still](../out/alloy_print_still.png),
[steps](../out/alloy_print.json). 101 s at 1280 × 720, 15 fps; the GIF is 640 × 360 at 5 fps, 4.2 MB.

```bash
xvfb-run -a python3 alloy_print.py            # about 18 min on a 4-core runner
PREVIEW=1 xvfb-run -a python3 alloy_print.py  # last frame of each sub-step -> /tmp/preview_alloy_print.png
```

| Step | What happens | Who does it |
|---|---|---|
| 1 | MiR250 drives from the rePowder to the sieve bench; the arm takes the rePowder's container by its handle | arm |
| 2 | Container tipped into the No. 60; set down on the bench; lid over the rods and down; both knobs turned; the stack shakes, see-through; the fractions panel | arm, then the AS 200 |
| 3 | Stack taken apart, No. 325 + pan into a jar | **a person** (below) |
| 3 | Jar into a cup on the MiR's cabinet | arm |
| 4 | MiR to the Aconity; door opens; supply piston drops; the arm carries the jar in, level, and pours by turning its wrist; jar back on the MiR; door shuts | arm |
| 5 | The print as a time-lapse, cut open: recoater sweeps, laser scans the bars and the lug, platform drops; MiR back to x = 1400 | the MIDI |

**Hand-offs.**
- **Start:** the MiR at x = −3487 (the rePowder's container axis, `REPOWDER_AT` + 288), y = −2230, arm parked, the
  container on a cup on its cabinet. The MiR is 148 mm further from the line than `alloy_workflow.MIR_Y`, because
  the rePowder's front stands up to 337 mm proud of the line's (−1899 against `line.Y_FACE` −1562): at `MIR_Y` the
  MiR would sit 107 mm inside it. The atomizer chapter should end there, or this chapter's `START` should move to
  wherever it ends.
- **End:** the MiR at x = 1400, `MIR_Y`, arm parked; the Aconity closed and opaque; the plate at the bottom of a
  30 mm powder cake; chapter 4's first camera (`CAM_LINE`) and status rows. Two differences remain: the cup holder
  and the empty jar are still on the MiR's cabinet, and chapter 4's MiR has neither.

**Where the shaker stands.** On a bench (1000 × 600 × 700 mm, assumed) between the rePowder (right edge
x = −2615) and the VLM (left edge −1417), front on `line.Y_FACE`, centre x = −2015. It is beside the rePowder, as
[`instruments_char.md`](instruments_char.md) recommends (dust, route), and the gap to the glovebox (541 mm) is too
narrow for a bench. `setup_lab.py` puts the shaker on tray F instead; the two layouts disagree.

### Sources and assumptions

| Item | Value | Status |
|---|---|---|
| Shaker, stack, lid, knobs, fractions | `instruments_char.sieve()`: Retsch AS 200 control, 8 in stack of DAL PR #175 | published / DAL; amounts per fraction an example |
| LPBF cut | No. 325 + pan, 20–63 µm; under 20 µm about 0.05 % (DAL) | from `instruments_char.md` |
| Container | `instruments_char`'s rePowder container (Ø128 × 228, "DAL, assumed size"), with its handle bar | assumed |
| Jar | 250 mL wide-mouth, Ø70 × 124, open | assumed |
| Supply and build cylinders, recoater | `alloy_models.py`: 170 mm each (DAL PR #169); the layout inside is a choice there | DAL / layout choice |
| Build | `alloy_models`' plate, bars and lug; 30 mm (`M.LUG[5]`), the cake chapter 4 starts in | chapter 4 |
| Layer | 50 µm, the layer of AddUp's AlSi10Mg sheet that chapter 4 cites; 600 layers | assumed for the MIDI |
| Recoat and scan | a time-lapse: 6 drawn cycles for 600 layers; hatch drawn on the bars below 6 mm, on the lug above | schematic |
| Gripper closures | 12 mm handle 0.876, 36 mm crossbar 0.59, 54 mm knob 0.36, 70 mm jar 0.18 (linear from chapter 4's 0.88 for 12 mm) | approximate |

### Open questions and simplifications

- **How much powder.** One run charges 78 g (`out/alloy_charge.json`). Its 20–63 µm cut is some fraction of that,
  tens of grams. A 30 mm build in the 170 mm cylinder needs about 1 kg in the bed (π/4 · 170² · 30 mm ≈ 680 cm³ at
  about 1.5 g/cm³), plus the supply's excess. So one jar stands for many runs, or a smaller build cylinder. The
  caption says so. Whether Aconity offers a reduced build volume for the MIDI hasn't been checked.
- **A person takes the stack apart.** Sieves come off one at a time and the fine fractions are tipped out. That is
  the dustiest step of the run (Al under 63 µm; DAL's sieve note asks for bonding, grounding and extraction, or a
  glovebox). The `instruments_char` stack is one mesh per material, so the sieves can't be lifted separately here.
  An arm doing it would need its own sieve meshes, and a place for five sieves on the bench.
- **The jar is drawn open.** A capped jar would need a decapper at the printer, or a person.
- **The arm pours into the supply through the door.** The TCP reaches 540 mm in past the door plane at the
  floor + 95 mm, gripper level. The UR10e's IK solves it from the MiR at chapter 4's spot (`aco_x`). With the shell
  drawn see-through, how close the forearm comes to the 280 mm tall chamber's door frame hasn't been checked. In
  practice the MIDI's supply is filled by hand.
- **The lid moves back to the bench by itself** after sieving. That is the person of the step above.
- **The door's handle is hidden during the print** so it doesn't cover the plate in the close-up.
- **No argon purge is shown**, only said; the MIDI's own gas loop isn't modelled.
