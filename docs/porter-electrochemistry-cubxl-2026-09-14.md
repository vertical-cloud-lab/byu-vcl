# Conductivity + spectroscopy on the CubXL — conversation with Dr. Jason Porter

Notes from [*Conversation with Dr. Porter concerning Electrochemistry on the CubXL*](https://youtu.be/RKp4XslErJo)
(BYU Vertical Cloud Lab, uploaded 2026-09-14, 14:30). Ben Whitney and Dr. Jason Porter, walking
through Porter's lab. Background for [issue #213](https://github.com/vertical-cloud-lab/byu-vcl/issues/213).

> **Provenance.** YouTube had no captions for this video, so these notes were written from a
> machine transcript of the audio ([`docs/transcripts/RKp4XslErJo-porter-cubxl-electrochemistry.txt`](transcripts/RKp4XslErJo-porter-cubxl-electrochemistry.txt)),
> produced with faster-whisper. Audio only — **anything shown on screen but not spoken is not
> captured here.** Technical terms the recognizer mangled are corrected below, and the key
> passages were re-checked against a larger model; timestamps point back at the video so any
> claim can be verified at the source.

## The ask, and the deadline

Ben framed the visit around a paper on **how versatile the CubXL is** — specifically the limit
of what it can do if a number of instruments are bolted onto it. The contrast he drew: robots
like this usually do *one* thing (liquid mixing, colour matching — VCL already runs one of
those), and the interesting question is what a **multi-purpose** workcell can do. An abstract
and a TMS presentation set the working timeframe (00:00–01:02).

## What Porter proposed measuring

**Conductivity paired with one optical technique** (01:07–02:00):

- His lab has **already built a conductivity sensor**, but it was designed to have electrolyte
  *flow over* it as part of their syringe dosing system, not to be dipped. For a dip-in
  workflow, he said, an off-the-shelf probe probably makes more sense.
- **Easiest optical modality: UV-Vis** — "super modular," easy to drop in, and enough to catch
  an optical/UV absorption change alongside conductivity.
- **What he actually wants: IR, or possibly Raman.** Raman may be the easier of the two here
  because it is straightforward to fibre-couple into a setup like this (02:00–02:13, 04:33–04:39).

## The real point is the closed loop, not the automation

> "We could automate making a bunch of solutions, but the real power in this is integrating the
> sensor network with the data collection — because you want to put that in the loop so you can
> then say, *what's the next mix you want to make?*" (02:13–02:34)

Ben confirmed that closed-loop optimization is exactly the lab's focus. Porter's motivation is
concrete: the test matrix he is trying to run is **~$1,000 of chemicals**, so choosing points
selectively is a direct saving — and the same argument scales to industry (02:42–03:13).

## Funding: Porter offered to write a ~$25k internal BYU proposal

The single largest concrete offer in the conversation. If the dosing + conductivity + **spectroscopy**
combination is of interest, Porter said he could think about what it would look like and
"potentially write an internal proposal at BYU to get like $25k to buy the hardware you would
need" (03:14–03:53). He noted that in-the-loop dosing-plus-prediction work already exists in the
literature; adding spectroscopy is what would make it exciting.

## Picking the proof-of-concept chemistry

Criteria he gave for the first system (04:10–04:39):

1. **Not moisture-sensitive**, so the demo can run in open air.
2. **A conductivity change you can measure** — "that's the easy part."
3. **A spectroscopic signature that correlates with it** — harder, and the crux of the experiment.

Porter took the action to look into candidate systems.

## Environment: glove box vs. open air

Porter's eventual target is a **glove box** (04:53–05:10, 10:17–11:05). The one he showed was
argon-filled at **0 ppm moisture, 0.2 ppm oxygen**, continuously purging and scrubbing. He was
explicit that this is not the same as a fume hood — a hood only keeps chemicals away from your
face, while a glove box conditions the atmosphere. It matters because moisture and oxygen adsorb
onto the powders they work with and **change the conductivity and the chemical stability**, so
open-air results can be misleading. He has a few glove boxes (one for sulfur work, one
non-sulfur, tied to battery research).

Running in open air is acceptable **as a concept demonstration**, with contamination understood
as a caveat; putting the CubXL inside a glove box is "a bigger lift" and a later step.

## How their conductivity measurement actually works

The most directly reusable part of the conversation (07:33–09:26):

- Partners at **CU Boulder 3D-printed a four-electrode sensor** for them.
- Electrolyte flows over the four electrodes through drilled holes in the printed part.
- **Two electrodes apply a fixed current; two measure the potential.** That four-electrode
  arrangement *is* what commercial conductivity probes are doing internally.
- The electrodes are read with a **potentiostat**.
- **Calibration is mandatory**: every cell is different, so you run calibration solutions of
  known concentration, build a calibration curve, and only then can a new liquid's conductivity
  be converted to concentration.

Porter's advice was pragmatic: they did this work and can share the design and protocol, and VCL
could print its own — **but if an off-the-shelf conductivity probe is cheap, just buy one.** They
only built their own because they needed continuous flow-through for the dosing system rather
than a dip probe (09:26–10:05).

## Their integrated flow cell — the template worth copying

What they built is essentially the experiment VCL wants to reproduce on the CubXL (10:05–11:46):

- Two syringes, one **high salt concentration** and one **low**; varying the relative mixing
  sweeps salt concentration across roughly **15 points**, dosed automatically.
- The solution flows continuously **through a gasket, under the electrodes, on top of an ATR
  crystal** — so the **infrared spectrum (ATR-FTIR) and the conductivity are measured at the same
  time, on the same liquid**.
- The cycle is **dose → measure → dose → measure**, fully automated, inside the glove box.

## What Porter wants from the CubXL specifically

- **Powders *and* liquids.** "If you could do powders and liquids, that'd be really helpful for
  us" (12:18–12:22).
- **Stirring** has to be built in (12:22). Ben's response: magnetic stirring is very feasible
  since the lab already has magnet capability; pipette-based mixing (aspirate/dispense) is
  limited but reportedly works well for others; the current pipette is 20 µL but a **300 µL**
  option is available for bigger applications (12:23–13:11). See
  [`docs/pipette-selection-cubxl.md`](pipette-selection-cubxl.md).

## Porter's real driver: a training-data bottleneck

The clearest statement of why he wants automation at all (13:22–14:20):

- This semester he has **three undergraduates manually preparing samples**, purely to generate data.
- He has built a **Python model that predicts all the species present from the spectrum**. It is
  a **highly nonlinear mixing problem**, so traditional regression methods do not work well.
- The model works well, **but he has enough data to train it and not enough to test it** — he
  needs a held-out set to run genuine blind studies against.
- Automation is what unblocks that, and "there's a bunch of cool science I can do once I've got
  the data set." He added there is **no shortage of other chemical systems** he would like to
  explore once something simple exists.

## Action items surfaced in the conversation

| Owner | Item |
|---|---|
| Porter | Look into **Raman vs. IR** for this setup and what hardware the combination needs |
| Porter | Consider writing the **~$25k internal BYU proposal** for spectroscopy hardware |
| Porter | Suggest a **moisture-insensitive model chemistry** where conductivity and spectra correlate |
| Porter | Share the **four-electrode flow-cell design and measurement protocol** |
| Ben / VCL | Open this GitHub issue and send Porter the link so discussion can continue there — Porter's group uses GitHub, mostly for code |
| VCL | Decide **buy vs. build** on the conductivity probe (buy if cheap; a potentiostat is needed either way) |
| VCL | Add **stirring** — magnetic stirrer most likely; evaluate pipette mixing and the 300 µL pipette |
| Both | Decide **open-air proof of concept vs. glove box**, accepting contamination caveats for the first demo |

## Open questions these notes do not answer

- Which potentiostat — does VCL buy one, or borrow Porter's for initial tests? He offered to show
  what they have and said "we can buy one."
- Whether the CubXL-capabilities abstract Ben referenced is the same TMS submission tracked in
  [`tms-2027-abstract-equipment-monitoring.md`](../tms-2027-abstract-equipment-monitoring.md)
  (TMS 2027, Orlando, 14–18 March 2027) or a separate one not yet in this repo.
- Whether flow-through (Porter's geometry) or dip-probe (simpler on a Cartesian gantry) is the
  right first architecture for the CubXL.
