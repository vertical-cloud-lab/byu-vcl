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

**Primary — [`img/dept-entry-atomization.jpg`](img/dept-entry-atomization.jpg)** (1226 × 864).
Ultrasonic atomization caught mid-run: a stream of molten aluminium alloy falling onto the
white-hot vibrating sonotrode, which throws a fan of glowing droplets across the chamber — the
droplets that freeze into the powder the rest of the workflow prints with. Requested in
[issue #214](https://github.com/vertical-cloud-lab/byu-vcl/issues/214#issuecomment-5671076211);
it matches the lead bullet in a way no other image we have does.

Suggested caption, if the handout allows one (it mostly does not — most entries run the photo
bare): *Ultrasonic atomization of a molten aluminium alloy — the first step in the lab's
closed-loop alloy discovery workflow.*

**For the email body — [`img/dept-entry-atomization.gif`](img/dept-entry-atomization.gif)**
(400 × 282, 5.4 s, 7.1 MB). The same run as a real-time loop, for anyone who would rather see
the atomization happen than read about it. Slightly heavy for an attachment; linking it is
safer than attaching it.

**Alternative — [`img/dept-entry-collage.jpg`](img/dept-entry-collage.jpg)** (1202 × 1202). A
2 × 2 collage in the style of Anton Bowden's entry, covering more of the lab in one tile:

| | |
|---|---|
| Ultrasonic atomization (as above) | The CubXL tool head carrying an Opentrons P20 GEN2 pipette over the vial deck |
| The OT-2 mid-run with red/yellow/blue stock vials — a frame from our own hardware livestream, 2026-09-08 | The 3D-printed electrochemical cell for nickel-electrode stress testing, from the lab profile |

The vertical-lift-module concept figure was dropped from the collage when the atomization tile
went in: its callout labels ("Back storage", "Operation table") are unreadable at 2 in and were
being clipped by the tile edge, so it was the weakest of the four.

### How the still was made

`am-alloy-2.gif` in [`vertical-cloud-lab/.github`](https://github.com/vertical-cloud-lab/.github)
is a 642-frame, 853 × 480 montage. Frames **4–184** are the atomization segment (~11 s); the rest
are the powder jar, a desktop LPBF machine at a trade show, laser powder-bed fusion, a printed
gear, and a tensile tester. Within the 853 × 480 canvas the footage is pillarboxed into
**x = 240–852**, so the real picture is only 613 × 480 — which is why the crop below is as loose
as it is. At 2 in wide the delivered file is ~300 dpi; crop it much tighter and it stops being
print-safe.

All 181 frames were scored on two things — how unbroken the falling droplet stream is, and how
dense the spray fan is — and **frame 6** won on both. Processing: crop to the footage region,
trim 48 px of dark chamber floor, a brightness-weighted 0.8 px blur that removes GIF dither from
the smooth background while leaving the droplets sharp, 2× Lanczos, light unsharp mask, +6 %
contrast.

### Provenance, since the handout is a department-level document

- **The atomization footage is not ours and its source is not recorded anywhere.** `am-alloy-2.gif`
  was committed to the profile repo as "file" with no attribution, and the README calls the whole
  montage a *"Conceptual demonstration"*. The lab's own atomizer is an **AMAZEMET rePowder**
  (see [issue #126](https://github.com/vertical-cloud-lab/byu-vcl/issues/126), which quotes the
  rePowder facility guide), and what the frames show is exactly that process, so AMAZEMET is the
  likely origin — but that is an inference, not a record. Confirm it before the image goes out
  under the department's name, and add a credit line if it is theirs.
- **Replacing it with our own footage is a small job once the atomizer runs.** One camera on a
  tripod through the chamber window during a training run would make this entry unambiguously
  ours, and would date-stamp it as BYU hardware.
- The CubXL gantry is [Ursa Laboratories](https://www.ursalabs.ai/) hardware (a modified
  Genmitsu PROVerXL 4030 V2 running CubOS) that we instrument and program — worth not implying
  we built the gantry itself. Ursa's own white-background product photos are nicer but are their
  marketing assets; ask @alexc2684 before using them.
- The CubXL photo is by @benwhitney5463,
  [issue #133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5121701796)
  (2026-07-29). The OT-2 frame comes from our livestream archive and is committed in this repo
  under `wireless-color-sensor/ot2/frames/`.
- There is still no good photograph of the complete assembled CubXL: the whole-machine shots in
  issue #133 were uploaded at 250 × 333. Likewise, our atomizer only appears in crate/unboxing
  photos ([issue #124](https://github.com/vertical-cloud-lab/byu-vcl/issues/124)).

See also [`cubxl-media.md`](cubxl-media.md) for the wider CubXL photo/video inventory (currently
on the `claude/issue-200-20260909-1531` branch).
