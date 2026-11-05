# Chapter 4: the powder, checked (`alloy_powder.py`, round 8)

Sterling, on PR #318 (2026-11-05 00:37 UTC), about the round-7 long-form:

> The laser diffractometer demo was really quick and not very informative. [...] you should be showing the
> characteristic data that comes from each of these techniques [...] The rigaku miniflex has kind of a poor angle, or
> you should make the door more transparent from the beginning. The goniometer is already moving by the time the door
> is opening. [...] why isn't this inline with the rest of the animation [...] (i.e., why isn't a tray coming and then
> the robot is putting something in there). Also, for powder XRD, you didn't show anything related to the sample prep
> for it, which is actually kind of an art. [...] For the XRF, it's not clear how the sample is making it somewhere
> else. [...] Instead of the stock AlSi10Mg powder, you should pull SEM images from the Al powder we actually atomized.

This chapter answers those in one run, in the whole two-Shuttle lab as the set-up movie leaves it
(`setup_lab.build`), so every tray is loaded whenever the VLM shows (the 9:09 complaint: "suddenly the VLM only has a
few things on board").

## What happens

| # | Where | What |
|---|---|---|
| 1 | Shuttle 1 | While the plate prints (chapter 3), the MiR250 + UR10e brings a retained sample of the sieved 20-63 µm cut, about 15 g in a vial with a mesh cap, to Shuttle 1's dock. |
| 2 | Tray D, prep station | The arm takes the vial by its side and, turning it over and shaking it, sifts the powder onto a zero-background holder, dusts an SEM stub and fills an XRF cup. A blade strikes the holder's powder off flush with its reference plane, the excess into a trough. Nothing is ground or pressed. |
| 3 | Tray D, Rigaku MiniFlex | The door, drawn see-through from the start, opens to 80 deg; the goniometer stands still. The arm carries the holder in by its fin and sets it on the stage. Door shut and locked, X-ray lamp on, then the goniometer moves: theta 5 deg / 2theta 10 deg to 45 / 90 deg, the holder spinning. The pattern (computed). |
| 4 | Tray D, Hitachi TM4000PlusII | The stub, on a 1.5 in carrier, goes into the SEM's mount cup (r8_char's, with the spring plunger), door in, pump-down; the lab's real images of the same powder, and the particle count. The XRF cup goes onto the MiR. |
| 5 | Tray E, Mastersizer 3000 + Aero S | About 5 g poured into the Aero S. The optical bench in cutaway: the background, the feeder running, large particles scattering narrow onto the focal-plane arcs and small ones wide onto the large-angle detectors; then the size distribution. |
| 6 | Tray M (Shuttle 2), Bruker S2 PUMA | The MiR drives to Shuttle 2 at its 0.3 m/s² (props.ramp_frac, from PR #321). A hatch in the hood's top slides back and the port opens; the arm sets the cup on the chamber's lift ring, which lowers it over the tube and the detector under helium; the spectrum (illustrative). |
| 7 | | The record: size, phases, shape and composition, each tray brought to an opening only when needed. |

## Real, computed, illustrative

- **SEM images: REAL.** The lab's own Al 4047, ultrasonically atomized on the rePowder on 22 Oct 2026, run c3k0n5
  ([DAL #159](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/159)), imaged on BYU's Apreo at 5 kV
  by Ronnie Guymon on 26 Oct 2026 ([DAL #157](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/157)).
  They replace the stock AlSi10Mg image. The caption says they come from a floor SEM, not the TM4000 shown.
- **Particle count: measured from those images** (`r8_powder_data.py`): 972 particles, Dn50 67 µm and Dv50 101 µm as
  imaged, which is the powder before it was sieved.
- **Laser diffraction: COMPUTED.** No Mastersizer result for this powder exists. The curve is the SEM count by volume
  put through a soft-edged 20-63 µm sieve: Dv10 44, Dv50 58, Dv90 72 µm. The panel is badged so.
- **XRD: COMPUTED.** Al-12Si (Al 4047) from Bragg's law, structure factors, Lorentz-polarization and Cu Kα1/Kα2
  (`r8_powder_data.py`). The panel is badged COMPUTED, NOT MEASURED.
- **XRF: ILLUSTRATIVE.** Real line energies and the Aluminum Association's 4047 limits; the heights and the result
  column are made up. Badged ILLUSTRATIVE.

## The XRD prep, and why this way

From Edison's literature answer ([`../out/edison/auto_pxrd_prep/answer.md`](../out/edison/auto_pxrd_prep/answer.md),
summarized in [`edison_r8.md`](edison_r8.md)):

- **Don't grind ductile metal powder.** Milling gas-atomized Al-Cu turned the spheres into larger flakes by cold
  welding, which creates the preferred orientation grinding is meant to cure. So the powder goes on as sieved.
- **Fill evenly with minimal pressure, flush with the holder's reference plane.** Brush or sift fine powder on rather
  than forcing it in. Whitfield, Huq and Kaduk, *Specimen preparation*, International Tables for Crystallography H
  (2019), [doi:10.1107/97809553602060000945](https://doi.org/10.1107/97809553602060000945).
- **Back-loading** fills the inverted holder from behind and helps platy or needle-like powders. These are spheres,
  so sifting on and striking off is enough; the caption doesn't claim back-loading.
- **The automated way:** A-Lab's UR5e pours powder into a vial with a steel-mesh lid and inverts it over the holder
  (Szymanski, *Automating the synthesis and characterization of inorganic materials*, 2024). Our vial's mesh cap is
  that idea; the shaking is ours.
- **Height is the check:** 0.1 mm too high moves Al 111 by -0.072 deg 2theta on the MiniFlex's 150 mm goniometer
  (`r8_powder_data.height_shift`). 0.2 mm of powder is "infinitely thick" to 99 % at 2theta = 90 deg, so the 0.5 mm well
  is enough (`thick_enough`).
- **Spin the holder.** It samples more crystallites; it doesn't remove orientation. Drawn here; whether this MiniFlex
  has a spinner is an assumption.
- **The diffractometer's door by an actuator:** Yotsumoto et al., *Autonomous robotic experimentation system for powder
  X-ray diffraction*, Digital Discovery 3, 2523 (2024),
  [doi:10.1039/d4dd00190g](https://doi.org/10.1039/d4dd00190g), drove theirs with one. Ours is drawn on the hinge.

## Our designs and assumptions (every size an estimate)

- **The prep station** (`r8_powder.pxrd_prep`, on tray D where the OpenFlexure array stood, `TRAY_PLACEMENT`, so the
  set-up movie and `setup_lab.py fit` include it): a 380 × 220 × 100 mm pedestal, the holder's nest at its front edge,
  a 1.5 in stub carrier, an XRF cup, a blade on a small linear axis, a trough.
- **The holder's fin** (14 × 8 × 30 mm, on a tab 30 mm in front of the well): the gripper closes across it, so its
  fingers never reach under the carrier and nothing of the gripper is near the beam's plane.
- **The stub carrier**: a 38.1 mm aluminium disc 25 mm tall with a pin stub, so the SEM's 1.5 in mount cup and its
  spring plunger (r8_char) hold and ground it like a mount; it stands 13 mm proud of the cup's rim for the fingers.
- **The XRF hatch.** At the VLM's opening the S2 PUMA's hood can't open far enough for an arm to reach under it: its
  front corner reaches the 856.5 mm goods height at about 20 deg. Bruker's brochure says the Automation version takes
  samples "into the sample chamber directly or via buffer positions"; drawn here as a hatch in the hood's top that
  slides back over the chamber's port. The real mechanism is a question for Bruker.
- **The XRF seat** used in the tour is now the front-right one (`XRF_SEAT`), nearest the arm.
- **The MiR at Shuttle 2** stops 450 mm left of the dock's centre, in front of the XRF's end of tray M.
- **The XRD door opens to 80 deg, not the tour's 100:** tray D's middle camera post (`services.TRAY_CAMS["D"]`, its
  mast 140 mm in front of the door's hinge) is in the way past about 85 deg.
- **The Aero S cover** lifts off by an actuator (by hand in Malvern's videos), as in round 7.

## Physical sense: what was checked

- Nothing floats: the holder, the stub carrier and both cups are in the arm's gripper, in a nest, or in an
  instrument's own part (the XRD stage, the SEM door's cup, the XRF's lift ring) at every frame.
- The vial's powder moves to the mesh cap when it is upside down and back when it is righted.
- The excess struck off the holder lands in the trough, where it stays.
- The XRF cup stays in the S2 PUMA, and the holder and the stub stay in the MiniFlex and the SEM, until the next
  sample: the trays go back with them inside, doors shut.
- **Left as drawn:** the falling powder is a few dozen points; the dusting on the stub and the fills are simple solids;
  the holder spins on a stage with no spinner drawn.

## Running it

```bash
PREVIEW=1 python3 runner_guard.py bg --quick --mem 6500 --log /tmp/p.log -- xvfb-run -a python3 alloy_powder.py
ARM_AUDIT=1 python3 runner_guard.py bg --mem 6500 --log /tmp/a.log -- xvfb-run -a python3 alloy_powder.py
VIZ3D_FPS=6 python3 runner_guard.py bg --mem 6500 --log /tmp/r.log -- xvfb-run -a python3 alloy_powder.py
```
