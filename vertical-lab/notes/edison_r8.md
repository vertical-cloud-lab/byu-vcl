# Edison literature searches for round 8 (2026-11-05)

Sterling asked on PR #318: "send some edison queries related to automated SEM, automated polishing, automated tensile
testing, sample prep, etc." and "look up automated powder XRD sample prep with edison queries". Five Edison
`LITERATURE` tasks ran on 2026-11-05 between 00:42 and 01:00 UTC. Each folder in [`../out/edison/`](../out/edison/)
holds the task id and query (`_task_id.json`), the answer with its references (`answer.md`), and the full trajectory
(`trajectory.json.gz`). The answers are Edison's, not checked line by line; the summaries below quote or paraphrase
them, and the chapter notes say where a choice rests on one.

| Query | Folder | What it changed here |
|---|---|---|
| Automated metallographic prep: disc changes, holders, in-line checks | [`auto_polishing`](../out/edison/auto_polishing/answer.md) | Chapter 6 (`notes/alloy_prep.md`) |
| Robotic SEM loading and the conductive path from a mount | [`auto_sem`](../out/edison/auto_sem/answer.md) | Chapters 6 and 7 |
| Automated tensile testing, with elevated temperature | [`auto_tensile`](../out/edison/auto_tensile/answer.md) | Chapter 5 (`notes/alloy_workflow.md`) |
| Powder-XRD sample prep and its automation | [`auto_pxrd_prep`](../out/edison/auto_pxrd_prep/answer.md) | Chapter 4 (`notes/alloy_powder.md`) |
| Mounting for nanoindentation and PIP | [`mech_test_mounts`](../out/edison/mech_test_mounts/answer.md) | Chapters 6 and 7 |

## Automated polishing

- **Three different ways to step from coarse grinding to fine polishing**, which the answer says should not be
  conflated:
  - **Change the whole prepared disc.** BAM's RASI cell uses a QATM QPOL 250 Bot with a magazine of 16 preloaded
    250 mm discs, picked in a programmed sequence, with six fluid reservoirs. It changes complete discs; how a worn
    SiC sheet or cloth is replaced on a disc isn't described.
  - **Give each grit or cloth its own station** and move the mount between them (a Qness patent, US12263548B2, a
    proposed line rather than a reported trial). Discs are then changed only for wear.
  - **Interchangeable diamond-abrasive films**, as in RoboMet.3D's serial sectioning.
- **RoboMet.3D** moves one mounted specimen between motorized polishing, dual ultrasonic cleaning and an inverted
  microscope; autofocus height closes the loop on the next slice's polishing time. Sectioning and mounting before
  loading are not automated in it.
- No source showed a robot peeling a used paper and laying a new one under a retaining ring. That job is the manual
  pain Sterling describes.

## SEM loading and the conductive path

- **"The most convincing demonstrated workflow carries the polished mount in a rigid, repeatably positioned fixture,
  rather than asking a robot to grip the resin cylinder or place a loose stub."**
- AFRL's **LEROY** bonded a 1.5 in (38.1 mm) conductive PolyFast mount to a stainless RoboMet.3D fixture with silver
  conductive epoxy and exchanged it through the load lock of a Tescan Vega 3. It imaged 1,000 sections (optical,
  BSE, EBSD), about 63 min a section; a vacuum-pump failure stopped it after section 900.
- **The path to ground**: exposed metal or a conductive coating, then a deliberate conductive bridge or a conductive
  mount, then a metal holder, then the grounded stage. Conductive mounts: carbon-filled phenolic (PolyFast),
  copper-filled (Probemet), carbon-filled cold epoxy (CarboCond). The answer calls the conductive mount in a metal
  fixture the strongest demonstrated robotic choice.
- Batch loading on floor SEMs: Hitachi SU3900 with AMICS uses a 28-hole holder for 25 or 30 mm mounts.
- **No verified robotic loading recipe or holder dimensions for a Hitachi TM4000** were found.

## Automated tensile testing

- **The clearest documented routes to unattended specimen exchange**: robotic transfer of single coupons, indexed racks
  of small specimens, and carousels that move pre-assembled holders into a furnace.
- Sandia's research rack-feed system runs about **25 tests an hour** (Heckman 2020), the only quantified rate found.
- ZwickRoell's AllroundLine Z100 + roboTest L ran **148 valid tests** of DIN 50125 A4×20 PBF-LB AlSi10Mg specimens
  from 50 parameter sets; no hourly rate was given.
- **Instron's AT2/AT3/AT6** handling details could not be verified from the literature; their own videos are the
  source for chapter 5.
- **Elevated temperature:** MATRON runs 12 miniature specimens in succession from a carousel, under vacuum or inert
  gas, up to 600 °C. Shimadzu documents a −70 to +280 °C chamber, without robotic exchange inside it. A 2026
  Argonne/APS report has a 1,000 °C split-tube furnace being commissioned and separate UR5 demonstrations of small
  specimen handling. The answer distinguishes an automatically controlled hot test from automated exchange of
  specimens at temperature.

## Powder-XRD sample prep

- **"Present many representative crystallites at a reproducible diffracting height without changing the material."**
- Fill the cavity evenly with minimal pressure, flush with the holder's reference plane. Brush fine powder through a
  sieve rather than forcing a coarse fraction in. Remake mounts with mounds, hollows or gaps.
- **Back-loading** (fill the inverted holder against the surface that will face the beam, close the back, turn it
  upright) and **side-loading** limit the orientation that front pressing causes; neither guarantees a random pattern.
  Height is an independent quality check.
- **For gas-atomized Al or Cu-alloy powder:** start with the as-received powder; sieve gently if needed; spin the
  holder; use a low-background Si holder when the amount is small, not as a cure for coarse grains. **Don't grind
  ductile metal powder**: milling gas-atomized Al-Cu turned spheres into larger flakes by cold welding, which creates
  the orientation problem it was meant to solve.
- Automation: an A-Lab-style UR5e pours powder into a vial with a mesh lid and inverts it over the holder; the arm
  then loads the diffractometer.

## Mounts for nanoindentation and PIP

- **"A Bakelite or epoxy metallographic mount is not automatically disqualifying, but it is not automatically a rigid
  support."** What matters is whether the force under the indent passes through enough metal into a stable platen,
  or through polymer.
- For quantitative nanoindentation, especially modulus, avoid an uncharacterized polymer layer under the metal. NPL's
  Good Practice Guide 92 (ISO 14577 practice): secure the specimen "without significant added compliance or
  flexure"; press it against its stub when bonding with cyanoacrylate; with hot-melt wax, keep it thin and the bonded
  area large.
- ISO 14577 gives **no universal minimum thickness, reverse-face polish, parallelism tolerance or metal-mount
  requirement**. Common practice: indentation depth under 10 % of the thickness, at least about 2 mm from a free edge.
- PIP on the PLX-Benchtop has been published on epoxy-mounted metals (Ma et al., sphere radius 1.006 mm,
  depth/radius about 0.18), without a mounted-versus-unmounted comparison.
