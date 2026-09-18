# SEM/EDS Polishing SOP — Vertical Cloud Lab

Standard operating procedure for sectioning, mounting, grinding, and polishing
metallographic samples (primarily **aluminum / AlSi10Mg**) to an SEM/EDS-ready
finish.

> **Status: draft — working document.** Transcribed from
> [byu-vcl #110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110) and
> not yet verified line-by-line against the equipment. Items marked
> **VERIFY** are known gaps — confirm on the machine and edit this file.
> This is **not** a substitute for the
> [BYU Engineering SOP template](../byu-engineering-sop-template.md) paperwork
> or for in-person training on each machine.

- **Lab location:** polishing lab, _[room # / building]_
- **Primary contacts:** Gage Erickson, Ronnie Guymon
- **Equipment owner / trainer:** Project Support Center (PSC); Dr. Fullwood's group
- **Related:** [#110](https://github.com/vertical-cloud-lab/byu-vcl/issues/110),
  [#77](https://github.com/vertical-cloud-lab/byu-vcl/issues/77),
  [caliber #16](https://github.com/vertical-cloud-lab/caliber/issues/16) (vacuum chamber)

---

## 1. Safety and prerequisites

**Emergency contacts** (from the BYU SOP template):

- University Police: 801-422-2222
- Risk Management: 801-422-4468
- College Health & Safety Officer: 801-422-6589

**Before you start**

- Get trained in person on the saw, mounting press, and polisher before running
  any of them unsupervised.
- **Reserve the polisher.** There is a QR code on the machine that links to the
  reservation site. _**VERIFY:** record the reservation URL here._
- Read the SDSs for ethanol, methanol, and acetone. Methanol is **toxic by skin
  absorption and ingestion**; all three are **flammable**.

**PPE and controls**

| Hazard | Control |
| --- | --- |
| Flying debris, saw | Safety glasses at all times; keep the blade cover down |
| Solvents (ethanol, methanol, acetone) | Work **in the fume hood**; nitrile gloves; no ignition sources |
| Hot mounting press | Do not touch the mold assembly until it has cooled |
| Sample contamination | Gloves whenever handling the puck after grinding starts |
| Rotating platen / belt | No loose sleeves, gloves clear of the belt, hair tied back |

**Waste:** solvent rinses go to the labeled chemical waste container in the fume
hood — never down the drain.

---

## 2. Consumables and materials

| Item | Detail |
| --- | --- |
| Mounting compound | Bakelite (phenolic) — epoxy is the alternative for delicate samples |
| SiC grinding paper | 320, 400, 600, 800, 1200 grit — **VERIFY:** the exact sequence stocked |
| Polishing pads | Adhesive-backed cloth, e.g. Imperial adhesive-back disc, 12 in / 300 mm |
| 1 µm suspension | Allied High Tech Products, **1 µm alumina suspension, de-agglomerated** |
| 0.05 µm suspension | Allied High Tech Products #180-20000, **0.05 µm colloidal silica, non-crystallizing** (vibratory polisher) |
| Solvents | Ethanol, methanol, acetone — in labeled squirt bottles |
| Parafilm | Bemis Parafilm M laboratory film — covers the solvent container in the ultrasonic cleaner |
| Kapton (polyimide) tape | For breaking the sample out of the Bakelite without damaging the surface |
| Silver conductive paint | SEM conductivity between sample and stub |
| Glassware | Deep glass containers (bowls / dishes) kept under the fume hood |

> **Naming note:** the 1 µm **alumina** and the 0.05 µm **colloidal silica** are
> different products used at different stages. Do not use the words
> interchangeably — see [§9 Open questions](#9-open-questions-and-confusing-parts).

---

## 3. Sectioning — diamond saw

1. **Check out a blade.** Go to the Project Support Center and check out a
    diamond-edged saw blade. They give you a bag containing a couple of blades in
    a cardboard container, two wrenches, and some metal pieces (the flanges and
    nut). Take it to the saw in the polishing lab.
2. **Mount the blade.** Lift the platform to reach the arbor. Locate the bolt
    directly under and to the right of the slit in the platform where the blade
    passes through. Stack, in order, then tighten with the two wrenches:
    1. the wider flange ring, flat side toward the blade,
    2. the blade,
    3. the second wide flange ring, flat side toward the blade,
    4. the piece that fits into the recess of the flange ring,
    5. the nut.
3. **Water.** Confirm the water valve at the back is **closed** (handle parallel
    to the back of the machine). Fill the bucket from the fume hood and fill the
    machine until about **¼–½ in** of the blade sits in the water. Lower the
    platform back down.
4. **Clamp the sample** against the two stabilizing rods, then clamp it in place.
    _**VERIFY:** describe / photograph the stabilizing rods._
5. **Check before starting:** blade cover down, saw not touching the sample.
6. **Start the saw.** Switch on the right side toward the back → green button on
    the side → green button on the front. Bring the speed to about **1400 rpm**.
7. **Cut.** Slowly rotate the handle to feed the blade into the sample, keeping
    the speed around **1000–1100 rpm** under load. Listen for unusual noise. A
    little water should be spraying up; **if no water is coming up, stop** — a dry
    blade will overheat and be ruined. Reposition as needed.
    - **Target size:** roughly **1 cm³** — small enough to sit on an SEM stub
      without overhanging the edges.
8. **Clean up.** Disassemble the saw, open the water valve to drain, dry the
    machine and all saw hardware, and return the bag to the PSC.

---

## 4. Mounting — Bakelite press

> The machine is a hot **compression mounting press** (it heats *and* presses).
> It is referred to in the lab as the "Bakelite press", "Bakelite oven", and
> "Bakelite compressor" — all the same machine.

1. Turn the press on with the switch at the back and open the water valve to the
    left of the machine (cooling water).
2. Press **Operate**, then set the parameters from the laminated sheet hanging
    above the machine. _**VERIFY:** copy those settings into this SOP so they
    survive the sheet going missing._
3. Place the sample in the mold with the **face you want to polish pointing
    down**.
4. Lower the ram with the arrows on the screen.
5. Add **¾ of a scoop** of Bakelite powder. _**VERIFY:** which scoop — the one
    stored with the machine?_
6. Fit the cap piece on top, **metal side down, green marble side up**, flush
    with the top of the machine. It has to be an airtight fit, so expect to wiggle
    it in.
7. Swing the lock bar over the chamber and press **Play**.
8. When the cycle finishes, remove the lock bar, press the **up arrow** to eject
    the puck, and pull it off the cap. It should release easily.
9. Turn the press off.

---

## 5. Rough grinding — belt sander

1. Turn on the belt sander and open the water valve on top so water runs down the
    belt.
2. Sand the puck by moving it **side to side** across the belt until the sample
    face is fully exposed and all Bakelite has been removed from the surface of
    interest.
3. Turn the sander off, then close **both** valves: the one on top of the sander
    and the large yellow-handled valve to the left of the machine.

_**VERIFY:** belt grit, and how much pressure to use._

---

## 6. Grinding and polishing — automatic polisher

### 6.1 Machine check (before mounting the sample)

1. Turn the machine on and open its water valve.
2. Set the gentle values — **35, 30, 150** reading from the top of the screen
    down. _**VERIFY:** units. Presumably force (N/lbf), head speed (rpm), and
    platen speed (rpm) — label them._
3. Set the timer to **30 seconds**.
4. Press **Link + H₂O** together to turn the water on, then **Link + Play**
    together to start it spinning.
5. If nothing is wrong, press **Stop**.

> The **Link** button is in the top-right of the panel and acts as a modifier —
> hold it together with another key. _**VERIFY:** the machine make/model and the
> real name of this button._

### 6.2 SiC grinding sequence

**Cleanliness rule:** rinse the puck, the metal puck holder, the sandpaper
retaining ring, and the platen thoroughly **between every grit change**. A
single carried-over coarse particle puts a scratch through everything you have
done so far. Wear gloves and do not touch the sample face.

1. Press **Link + ↑** together to raise the puck holder.
2. Remove the splash-guard ring and the metal paper-retaining ring, lay down
    **320 grit** paper, and replace both rings.
3. Seat the puck in the metal holder with the sample face on the paper.
4. Turn on the water and start the platen as in §6.1. Position the water stream
    so it washes the removed particles **away from** the sample — if it washes
    them across the sample they will scratch it.
5. Grind while checking the surface frequently. **Move to the next grit only
    when every scratch on the face is the same size** (i.e. all the scratches from
    the previous grit are gone).
6. Rinse everything (see the cleanliness rule) and repeat for each grit:

    | Step | Grit | Notes |
    | --- | --- | --- |
    | 1 | 320 | Until the face is flat and uniform |
    | 2 | 400 | |
    | 3 | 600 | |
    | 4 | 800 | |
    | 5 | 1200 | See the 1200-plain vs 1200-fine question in §9 |

    _**VERIFY:** this sequence — the grits stocked may differ._

**All SiC papers are single use.** If a paper starts to tear mid-run, stop and
replace it.

### 6.3 1 µm alumina polish

1. **Pad.** Polishing pads may be reused **only on the exact same alloy** —
    reusing a pad across alloys cross-contaminates the surface.
    1. Peel the backing off to expose the adhesive side.
    2. Cut a small square of electroplating tape and stick it to the back of the
      pad, wrapping it around the edge to the top, to make a pull tab for
      removing the pad later. _**VERIFY:** the tape type — electroplating tape,
      electrical tape, or the Kapton tape we bought?_
    3. Stick the pad down on the platen.
2. **Prepare the puck and the landing zone before the machine is running:**
    - Blow the puck completely dry with compressed air from the fume hood and wipe
      the water off the **sides and bottom** with a paper towel.
    - **DO NOT WIPE THE SAMPLE FACE WITH THE PAPER TOWEL.**
    - Set out a clean paper towel to receive the puck after polishing, a deep
      glass container, and a squirt bottle of deionized water.
    - From this point on the puck may touch **only cleaned surfaces**, and the
      polished face is **never** set down.
3. **Charge the pad.** Apply **6–7 generous circles of 1 µm alumina suspension**,
    concentrated toward the center — the suspension migrates outward as the platen
    spins.
4. Swing the puck holder over the pad and press **Link + ↓** to lower it.
5. Set the timer to **3 minutes** and press start. **Do not run the machine's
    water during this step** — the alumina suspension is the lubricant and the
    abrasive; water would wash it away.
6. **Keep the pad wet with alumina** throughout; you will see it moving toward the
    edge of the pad. Re-apply as needed.
7. **Between runs**, rinse the face with deionized water over the deep glass
    container and inspect for scratches. Repeat 3-minute runs until no scratches
    are visible. _**VERIFY:** how many runs is typical, and at what magnification
    are we judging "no visible scratches"?_
8. **Clean up.** Wash the alumina off the pad and off the whole machine in the
    fume hood. Blow the pad dry with compressed air, put the adhesive cover back
    on its sticky side, and bag it **labeled with both the abrasive (e.g. "1 µm
    alumina") and the alloy it was used on**.

---

## 7. Cleaning after polishing

> The polished face must not sit in air while it is wet with suspension — silica
> starts to crystallize on the surface immediately.

### 7.1 After the alumina polish

1. Carry the puck to the fume hood **polished side up, in the deep glass
    container**.
2. Spray the face with ethanol and blow dry with compressed air.
3. **If a haze remains**, continue:
    1. Rinse the glass container twice with ethanol, emptying it into the chemical
      waste. The container and the puck are now both "clean".
    2. Place the puck face-up in the glass container and **submerge it completely
      in methanol** so the polished face is never exposed to air.
    3. Rinse the ultrasonic cleaner with deionized water, then fill it with
      **¼–½ in** of deionized water.
    4. Cover the glass container with a lid (or Parafilm) so no bath water can get
      in, and set it in the ultrasonic cleaner. Put the ultrasonic cleaner's own
      lid on and run it. _**VERIFY:** run time._
    5. Take the container back to the fume hood. Remove the lid carefully so no
      bath water drips into the **methanol**.
    6. Blow dry with compressed air. Repeat the ultrasonication if the haze is
      still there.

### 7.2 After the vibratory polisher (colloidal silica)

This is the aggressive, recommended process. **Speed matters** — the sample must
not sit in air between coming out of the colloidal silica and hitting the
ethanol.

1. Prepare **3 glass bowls** (under the fume hood): rinse with water, dry with a
    paper towel.
2. Fill one with **acetone**, one with **ethanol**, one with **methanol** — just
    enough to cover the whole puck. Label or mark each bowl.
3. Take the ethanol squirt bottle and the ethanol bowl to the vibratory polisher
    and get ready to lift the puck and Vibromet holder out of the colloidal silica.
4. Lift the sample out of the silica and **immediately start spraying it with
    ethanol**. While still spraying, free the puck from the holder and drop it
    into the ethanol bowl, **specimen side up**. Go to the ultrasonic cleaner.
5. Move the puck from the ethanol to the **acetone**, cover the bowl with
    Parafilm, and ultrasonicate **10 minutes**.
6. Move it back to the **ethanol**, Parafilm, ultrasonicate **8 minutes**.
7. Move it to the **methanol**, Parafilm, ultrasonicate **5 minutes**.
8. Remove from the methanol and dry **vigorously** with compressed air.
9. Inspect the finish and repeat steps as needed.

---

## 8. Vibratory polishing (colloidal silica)

_Not yet written._ The 0.05 µm colloidal silica step on the Vibromet comes
between §6.3 and §7.2. Cleaning afterwards is §7.2, which is already documented.

---

## 9. Open questions and confusing parts

Points where this procedure is ambiguous, self-inconsistent, or incomplete.
Resolve on the machine and edit this file.

1. **Alumina vs. silica in §6.3.** The original text says to use "1 µm alumina
    suspension" and then, one sentence later, to "apply 6–7 generous circles of
    silica". Those are two different products — the 1 µm alumina is the pad
    polish; the 0.05 µm colloidal silica is the vibratory-polisher medium. Written
    here as **alumina** throughout §6.3, on the assumption "silica" was a slip.
2. **§6.3 step order.** The original told you to lower the head onto the pad and
    *then* dry the puck and set out the clean towel / glass container / DI bottle.
    Reordered here so all preparation happens before the puck goes down.
3. **"3 minutes" vs. "every couple of minutes".** The original says to set 3
    minutes, and also to rinse and inspect "every couple of minutes". Written here
    as repeated 3-minute runs with an inspection between each. Confirm.
4. **"DO NOT USE WATER" vs. the DI rinse.** These refer to different water: the
    machine's water jet stays off during polishing; the DI squirt bottle is used
    off the machine between runs. Stated explicitly here.
5. **Machine settings "35, 30, 150" have no units or labels.** Almost certainly
    force, head speed, and platen speed, but that needs confirming — and the
    machine make/model should be recorded so the next person can find the manual.
6. **The "Link" button.** Its real name and location should be confirmed; every
    control in §6 is a two-key combination with it.
7. **1200 plain vs. 1200 fine — is the fine one needed?**
    Check the labels first. If one reads **P1200** (FEPA grading) and the other
    **1200** with no P (CAMI/ANSI grading), they are *not* the same paper with a
    different texture — **P1200 ≈ 15 µm** abrasive while **CAMI 1200 ≈ 3 µm**, a
    5× difference. Practical answer: jumping from ~15 µm straight to the 1 µm
    alumina works but costs a lot of polishing time; the ~3 µm paper bridges that
    gap cheaply. If both are the same grading standard and genuinely differ only
    in backing/texture, the plain one is sufficient — which matches what the PSC
    staff told us. **Action: read the two labels and record what they actually
    say.**
8. **Rotating the sample between grits.** Standard metallographic practice is to
    turn the sample 90° at each grit change so the new scratch direction is
    perpendicular — that is what makes "all scratches the same size" easy to judge.
    The original SOP does not mention it. Confirm whether the automatic head makes
    this moot (it rotates the sample continuously) or whether we should add it.
9. **Tape type in §6.3.** "Electroplating tape" may be a slip for electrical
    tape, or for the Kapton tape bought for this workflow
    ([order 12789](https://meorders.byu.edu/order/12789)).
10. **§7.1 said "no water drips into ethanol"** at the point where the container
    holds **methanol**. Corrected here to methanol; confirm which solvent that
    final ultrasonication actually uses.
11. **Ultrasonication time in §7.1 is unspecified.** §7.2 uses 10 / 8 / 5 minutes
    for acetone / ethanol / methanol — pick a number for §7.1 and write it down.
12. **Kapton tape is bought but not in the procedure.** The plan was to use it to
    break the sample out of the Bakelite while preserving the surface. Add that
    step once the technique is settled.
13. **Bakelite press parameters live only on a laminated sheet** above the
    machine. Copy them into §4.
14. **Machine naming.** "Bakelite compressor", "Bakelite oven", and "the machine"
    are the same compression mounting press. Standardized here.
15. **Typo in the original:** "Return bad to PSC" → "return the **bag** to the
    PSC".
16. **Metal pucks instead of Bakelite.** Noted in #110 as a likely improvement —
    superglue the sample to a metal puck. If we switch, §4 is replaced entirely.
17. **Missing from this SOP:** PPE was not in the original (added in §1), and
    there is no mounting / stub-prep section covering the silver conductive paint
    and getting the sample into the SEM.

---

## 10. Revision history

| Date | Change | By |
| --- | --- | --- |
| 2026-09-18 | First draft, transcribed from #110 | @ronnie-guymon (text), formatted by Claude |
