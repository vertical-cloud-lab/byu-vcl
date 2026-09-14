# BYU VCL entry for the ME department research-projects handout

The department circulates a handout titled **"Research Projects by Professorial Faculty (A–Z)"**
(BYU Mechanical Engineering / Ira A. Fulton College of Engineering; the 2025-10-08 revision is
11 pages). This file holds our entry so it can be pasted into an email or a Word document
without re-deriving it each time it is requested. Requested in
[issue #214](https://github.com/vertical-cloud-lab/byu-vcl/issues/214).

## The format, as used by the other entries

```
<Name, bold + underlined>, <email, hyperlinked>
<optional group name or "Research focus: ..." line>
   • bullet
   • bullet
```

- Bullets sit in a text column occupying roughly the left 60 % of the page; **one photo (or a
  small collage) floats at the right margin**, vertically aligned with the first bullets.
  Images run about 2 in wide.
- Three to six bullets per person. Length varies from three words (Chris Mattson) to three
  lines (Brian Iverson); most are one sentence naming a project.
- Several entries lead a bullet with a topic phrase and a colon — "Wetting behavior and heat
  transfer:", "Superhydrophobic surfaces:", "Agricultural Robotics:". That pattern is used below.
- A group-name line under the name has precedent (Larry Howell, "Compliant Mechanisms Research
  Group"); so does a "Research focus:" line (Tim McLain).
- Entries are alphabetical by last name, so **Baird falls on page 1, between Matt Allen and
  Jon Blotter**.

## The entry

> **Sterling Baird**, sterling.baird@byu.edu
> Vertical Cloud Lab
>
> - Autonomous alloy discovery: closing the loop between powder dosing, ultrasonic atomization,
>   metal 3D printing, and mechanical testing so that new additively manufactured aerospace
>   alloys are proposed, produced, and tested with minimal human intervention.
> - Cloud labs: remotely operated experiments that students and collaborators anywhere can queue
>   from a web browser or a Python script and watch on a livestream — used for coursework,
>   outreach, and remote collaboration.
> - Frugal twins: low-cost, modular benchtop counterparts to expensive instruments, enabling
>   low-risk prototyping, lower barriers to lab automation, and multi-fidelity optimization.
> - Vertical automation: vertical lift modules that bring equipment to the operator rather than
>   the operator to the equipment, reclaiming the unused vertical space in a laboratory.
> - Bayesian optimization for materials: open-source scaffolding (Honegumi), realistic
>   benchmarks, and algorithms that handle competing objectives, noisy measurements, and prior
>   knowledge, to find better materials in fewer experiments.

Optional sixth bullet, if the layout allows it:

> - Autonomous electrochemistry: 3D-printed electrochemical cells and automated sample exchange
>   for next-generation batteries and electrolyzers.

The wording tracks the three core thrusts and the three framing concepts on the
[lab's public profile](https://github.com/vertical-cloud-lab) (vertical automation, cloud
experimentation, frugal twins; autonomous alloy discovery, autonomous electrochemistry,
advanced Bayesian optimization).

## The image

**Primary — [`img/dept-entry-cubxl.jpg`](img/dept-entry-cubxl.jpg)** (1200 × 1420). The CubXL
tool head carrying an Opentrons P20 GEN2 pipette over the vial deck, with the Arduino/TMC2209
stack that drives it. Our own photo, by @benwhitney5463 in
[issue #133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5121701796)
(2026-07-29), cropped to remove empty wall above the head. It is the sharpest photograph of lab
hardware we have and it reads unambiguously as automated experimentation at 2 in wide.

**Alternative — [`img/dept-entry-collage.jpg`](img/dept-entry-collage.jpg)** (1202 × 1202). A
2 × 2 collage in the style of Anton Bowden's entry, covering more of the lab in one tile:

| | |
|---|---|
| CubXL tool head (as above) | The OT-2 mid-run with red/yellow/blue stock vials — a frame from our own hardware livestream, 2026-09-08 |
| The vertical-lift-module concept figure from the lab profile | The 3D-printed electrochemical cell for nickel-electrode stress testing, from the lab profile |

Provenance notes, since the handout is a department-level document:

- The CubXL gantry is [Ursa Laboratories](https://www.ursalabs.ai/) hardware (a modified
  Genmitsu PROVerXL 4030 V2 running CubOS) that we instrument and program — worth not implying
  we built the gantry itself. Ursa's own white-background product photos are nicer but are their
  marketing assets; ask @alexc2684 before using them.
- The OT-2 frame comes from our livestream archive and is committed in this repo under
  `wireless-color-sensor/ot2/frames/`.
- The molten-metal frames in the profile's `am-alloy-2.gif` are a *conceptual* montage whose
  source footage is not documented in the repo, so they are deliberately **not** used here.
- There is still no good photograph of the complete assembled CubXL: the whole-machine shots in
  issue #133 were uploaded at 250 × 333, and the only wide frame available is 896 × 720 from a
  video. Likewise, the ultrasonic atomizer only appears in crate/unboxing photos
  ([issue #124](https://github.com/vertical-cloud-lab/byu-vcl/issues/124)). One good wide photo
  of each, once installed, would make this entry noticeably stronger — and the atomizer photo
  would let the image match the lead bullet.

See also [`cubxl-media.md`](cubxl-media.md) for the wider CubXL photo/video inventory (currently
on the `claude/issue-200-20260909-1531` branch).
