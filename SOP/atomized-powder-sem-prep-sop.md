# Atomized Powder SEM Sample Preparation

*Draft, 2026-10-15, written from [#264](https://github.com/vertical-cloud-lab/byu-vcl/issues/264) and the issues it links. Nobody has run it yet, so expect changes after the first batch. It makes the samples the [runs plan](https://github.com/vertical-cloud-lab/byu-vcl/blob/cad4e6d/atomizer-runs/plan-adv-mater/measurements.md) asks the SEM for; the plan holds the imaging and EDS settings. Polishing a cross-section is handed over to the polishing SOP in [#258](https://github.com/vertical-cloud-lab/byu-vcl/pull/258). The first use is the plan's G0 shakedown on the u23y78, 4yghtr and kj0461 powders.*

### What each run gets

| Stub | Powder | When | For (runs plan) |
| --- | --- | --- | --- |
| `ID-top`, `ID-mid`, `ID-bot` | the collection jar, at three depths | before the jar is poured out | EDS at 5 kV on 30+ particles each; Mo, W, Ni or Fe pick-up |
| `ID-A-size`, `ID-B-size` | about 0.5 g quartered from each half | after splitting, before sieving | sizing on ≥ 1000 particles: D10, D50, D90 and the share under 15 µm |
| `ID-A-shape`, `ID-B-shape` | each half's fraction through the 45 µm sieve | after sieving | SE images at 100x, 500x and 2000x; circularity and aspect ratio on ≥ 400 particles |
| `ID-A-xs` | half A, through the 45 µm sieve | one run per block and per spread point | cross-section: internal porosity and EDS maps |

`ID` is the run's bag ID, the six-character label from [#249](https://github.com/vertical-cloud-lab/byu-vcl/issues/249). Only the machine and the transducer are restricted to Gage, Ronnie and Sterling; SEM work is open to everyone ([runs plan](https://github.com/vertical-cloud-lab/byu-vcl/blob/cad4e6d/atomizer-runs/plan-adv-mater/README.md#runs-and-what-each-is-meant-to-show)).

### Before you start

* PPE as for any powder handling in the [atomizer SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/sop.md#safety-and-ppe): full-face respirator, ESD coat with the wrist strap, powder-free nitrile gloves.
* Work in the fume hood with the sash down, on a grounded metal tray with its bonding lead clipped on. Never pour or slide powder over paper, plastic or acrylic ([sieve doc](https://github.com/vertical-cloud-lab/byu-vcl/blob/d301844/docs/sieve-order.md)).
* Keep water and alcohol away from loose powder. The SDS lists both as incompatible, and with water the powder gives off hydrogen. No compressed air or air duster on powder either: the SDS says not to, and duster propellant is flammable.
* Clean up with the ATEX vacuum, or brush into the *Solid Material* bucket. Swabs, tabs and anything else with powder on it go in that bucket too, never in the ordinary trash ([lab safety](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/SOP/lab-safety.md#metal-powder-waste-risk-management-pickup)).
* Let a jar that has been somewhere cold warm to room temperature before you open it ([#230](https://github.com/vertical-cloud-lab/byu-vcl/issues/230#issuecomment-5785614623)).
* You need: new 12.7 mm pin stubs (Ted Pella `16111`), 12 mm carbon tabs (`16084-1`), wooden cotton swabs, a stainless micro-spatula, small glass vials, a stub box, and the vacuum stub desiccator (`16179`).

### Step 1: Make a stub

Make every stub the same way. How the powder goes on changes the sizes you measure, so if anything here changes, write it in the run record.

* Handle stubs only with clean tweezers, by the pin or the edge.
* Stick a carbon tab on the stub, press it flat through its top liner with the back of the tweezers, then peel the liner off. Don't touch the adhesive.
* Touch the cotton end of a wooden swab into the powder so that a little sticks. The handle has to be stiff, so the powder flies off in a narrow spray.
* Stand the stub on the bottom of a clean glass beaker, so the hood's airflow can't carry the powder off and whatever misses stays in the beaker.
* Hold the swab about 2 cm above the tab, cotton end over the tab, and flick the handle once with a finger.
* Check under a loupe or the optical microscope. Aim for one layer, with most particles about their own diameter apart. If it's too sparse, flick again. If there are clumps or particles on top of each other, start a new stub.
* Don't spread the powder around or press it into the tape. Particles that sink into carbon tape measure small: PNNL found 20-25% on their powder.
* Hold the stub by its pin over the tray, turn the tab vertical, and tap the edge of the stub on the tray 5 times. Don't blow it off, since blowing takes the big particles first. Whatever falls off now would otherwise fall off inside the SEM.
* Put the stub in the stub box and write its position and name in the run record, with the date.

### Step 2: Which powder, and when

**Top, middle and bottom (EDS).** Take these from the collection jar before it is poured out, after weighing if you like. Pouring, rolling and shaking mix the layers: "shaking a jar brings the biggest particles to the top" ([atomizer SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/8981f5c/atomizer-training/sop.md)).

* **Top:** touch the swab to the middle of the powder surface.
* **Middle and bottom:** push a clean, dry glass tube (about 6 mm bore, open at both ends) straight down to the bottom of the jar. Close the top of the tube with a gloved finger and lift it out over the tray.
* Let the powder slide slowly out of the lower end. The first third out is the bottom of the jar, and the next third is the middle. Make a stub from each, then pour the rest back into the jar.

**Sizing (A-size, B-size).** After the batch is split into halves (runs plan: cone and quarter on a grounded tray) and before the halves are sieved:

* Quarter each half down to about 0.5 g in the same way, on the tray, and put it in a labeled vial.
* Roll the vial gently, then make the stub from it.
* Keep what's left in the vial in case the stub has to be made again.

**Shape (A-shape, B-shape).** After sieving, from each half's fraction that went through the 45 µm sieve (No. 325). Until the lab has that sieve ([PR #262](https://github.com/vertical-cloud-lab/byu-vcl/pull/262) lists it as optional), use the pan under the 63 µm sieve and say so in the run record.

### Step 3: Store the stubs

* Close the stub box and put it in the vacuum stub desiccator, as in Step 11 of the [polishing SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/157ab1e/SOP/sem-eds-polishing-sop.md#step-11). Pump for about 45 s and close the valve before you switch the pump off. Wait a few minutes to see that the seal holds.
* When you open it, let the air back in slowly. A rush of air blows loose powder around.
* Keep desiccant packs out of the stub box ([#230](https://github.com/vertical-cloud-lab/byu-vcl/issues/230#issuecomment-5785614623)).

### Step 4: Cross-section (one run per block and per spread point)

On a loose sphere, the EDS result depends on where the beam lands on the curve. A polished section is flat, so it's the better check of how well the 4047 mixed in ([caliber PR #13](https://github.com/vertical-cloud-lab/caliber/pull/13#issuecomment-6032150138)). It also shows pores inside the particles.

* Mount about 0.5 g of the powder by following the [polishing SOP](https://github.com/vertical-cloud-lab/byu-vcl/blob/157ab1e/SOP/sem-eds-polishing-sop.md) from Step 2 on, with the changes below.
* **Use a conductive mounting powder.** Bakelite doesn't conduct, so particles sitting in it on their own charge up in the SEM.
    * Mix the powder with about 3 g of graphite-filled mounting powder (OnPoint CarbonMount `CBM-2001`, $29 per lb; the lab doesn't have it yet).
    * Spread the mix evenly over the press ram, top it up with the usual black Bakelite, and press as in Step 2.
    * Graphite only adds carbon, which isn't one of the measured elements.
* **Skip the belt sander** (Step 3). It would take the powder layer right off. Start on the polisher at 800 grit with the lightest force, 30 s at a time, checking under the optical microscope.
* **Grind past the tops of the particles.** When particles first show, measure the puck's height with the micrometer. Keep grinding until it is about 0.05 mm shorter, which is about the size of the largest particles. Before that, you are mostly looking at caps of oxide skin.
* Then 1200 grit, 1 µm alumina, 0.1 µm diamond film and the cleaning steps, as in the polishing SOP. Don't use colloidal silica, because it adds Si. Keep each ultrasonic clean to about a minute.
* Particles that pull out leave round holes the size of a particle. Don't count those as porosity: a pore sits inside a particle's outline. Keep EDS away from them too, since they collect polishing residue.
* Run a strip of carbon tape from the edge of the face to the stub or holder, so the face is grounded. Store the puck as in Step 11 of the polishing SOP.

### At the SEM

The settings are in the runs plan. These points depend on how the stubs were made.

* Tap each loose-powder stub once more before loading it.
* Keep the detector, kV, working distance, magnification and image size the same for every run, and write them in the run record. The plan's run-record template has a field for the EDS kV, but none yet for the imaging settings.
* Save TIFFs without the overlay. The settings stay in the file's metadata.
* **Sizing:** BSE images separate aluminum from the carbon tab more cleanly than SE images do. At 500x, the April AlSi10Mg images on the Apreo were about 830 µm wide, so a pixel is about 0.5 µm and a 5 µm particle is about 10 pixels across. Take fields on a fixed grid across the middle of the tab, not the ones that look good, until there are at least 1000 particles.
* **Shape:** circularity reads low on small, pixelated particles, so measure it on the 500x images every run. At 100x a 15 µm particle is only about 5 pixels across, and at 2000x there are too few particles per image.
* **Pick-up:** at 5 kV, a W particle can pass for Si, because W Mα (1.77 keV) sits on Si Kα (1.74 keV). Fe Kα isn't excited at all at 5 kV. So look for pick-up in BSE first, where Mo and W are much brighter than aluminum, and check any bright particle with a spot at 15-20 kV.
* EDS on loose powder doesn't give the powder's oxygen. That comes from inert-gas fusion on the 5 g sample kept back (runs plan).

### Open questions

* **Mike's slurry rule.** Mike Standing's advice was "Under 50 microns: make a slurry. Over 50 microns, use the carbon tape" ([#48](https://github.com/vertical-cloud-lab/byu-vcl/issues/48#issuecomment-4145749018)), and the April AlSi10Mg stubs were made both ways. This SOP stays dry for three reasons. The SDS lists water and alcohols as incompatible with this powder. The slurry went onto Si chips, which add Si to the EDS. And Al and Si look almost the same in BSE, which makes sizing hard. Worth asking Mike whether a dry flick is fine for spherical 15-45 µm powder.
* **Splitting.** The runs plan splits by cone and quarter until a riffler can be bought. In A.A. Khan's sand test at Bradford, coning and quartering was the worst of five methods: 6.8% SD, against 1.0% for a chute riffler and 0.13% for a spinning riffler.
* **The tube for top, middle and bottom** hasn't been tried. If the core won't stay in the tube, a narrower tube or a proper sampling thief is needed.
* **CarbonMount or a carbon coat.** CarbonMount is $29, but it is an order. Without it, the polished face needs a carbon coat at the EMF. Can they do that, and for how much?
* **Holder for 1 1/4" mounts.** Same question as in the polishing SOP. If the SEM has one, the cross-section doesn't need cutting down to a stub.
* **Automated particle analysis.** If the Apreo's software can find and measure particles by itself, the 1000- and 400-particle counts get easy.

### Videos

* [Sample Prep and Viewing Under SEM](https://youtu.be/QC0i_jEU9DM) (Gage, April): slurry and carbon-tape prep of the AlSi10Mg and Si powders ([#48](https://github.com/vertical-cloud-lab/byu-vcl/issues/48#issuecomment-4181057606)).
* [Removing the sample from the puck, final cleaning, mounting to an SEM stub](https://youtu.be/kcyESipwU8Y) (Gage, May; [#77](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-4513166720)).

### Sources

* What to measure, splitting and the 5 g sample: [runs plan, `measurements.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/cad4e6d/atomizer-runs/plan-adv-mater/measurements.md).
* EDS on spheres at 5 kV, cross-sections, colloidal silica: [caliber PR #13](https://github.com/vertical-cloud-lab/caliber/pull/13#issuecomment-6032150138). Fe Kα absent at 5 kV: [caliber EDS voltage plan](https://github.com/vertical-cloud-lab/caliber/blob/e0664b9/docs/eds_voltage_series_plan.md).
* Flick method, monolayer, loose particles: Nanoscience Instruments, [Preparing Powders for Scanning Electron Microscopy](https://www.nanoscience.com/community/blog/preparing-powders-for-scanning-electron-microscopy/).
* Tapping off loose particles, duster propellant, blowing skews particle counts: Thermo Fisher, [Sample preparation e-guide](https://documents.thermofisher.com/TFS-Assets/MSD/Application-Notes/desktop-sem-sample-preparation-guide-BR0098.pdf).
* Particles in carbon tape measure 20-25% small: Lonergan et al., PNNL-34162, [Understanding Biases in Sample Preparation Techniques](https://www.pnnl.gov/publications/understanding-biases-sample-preparation-techniques-coupled-scanning-electron).
* Splitting error by method: Gilson, [Comparison of sample dividing methods](https://www.globalgilson.com/Content/Images/uploaded/pdf/charts-tables/comparison-of-sample-dividing.pdf), from A.A. Khan's test at Bradford.
* Powder hazards: the AlSi10Mg SDS in this repo, `AlSi10Mg-sds-from-heegermaterials [not MSE supplies].pdf`.
* No compressed air, powder-free gloves: Ronnie's ASTM E1078 notes in [#77](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-4400486364).
* Apreo image settings: the April powder TIFFs in [#48](https://github.com/vertical-cloud-lab/byu-vcl/issues/48#issuecomment-4181040112).
* Vacuum stub desiccator: Ted Pella, [16179 tech note](https://www.tedpella.com/technote_html/16179%20TN.pdf); [#111](https://github.com/vertical-cloud-lab/byu-vcl/issues/111); [caliber#16](https://github.com/vertical-cloud-lab/caliber/issues/16).
* Conductive mounting powder: OnPoint, [CarbonMount](https://onpointabrasives.com/products/carbonmount-conductive-compound-1-lb-item-no-cbm-2001).
