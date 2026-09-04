# Vacuum Operating SOP — Nilfisk CFM 118EXP (AlSi10Mg / Si Powder Pickup)

> **What this is.** The *operating* SOP: how to set up, continuity-verify, run, shut down,
> clean, and store the Nilfisk CFM 118EXP explosion-proof vacuum when picking up AlSi10Mg or
> elemental Si powder. It is the companion to the *disposal* SOP
> ([`edison/powder-disposal-sop/powder-disposal-sop.md`](edison/powder-disposal-sop/powder-disposal-sop.md)),
> which takes over at the point a sealed liner leaves the bin.

> **Provenance.** Consolidated from §13–§17 of
> [`vacuum-accessories-options.md`](vacuum-accessories-options.md), which are built on three
> Edison Scientific `LITERATURE_HIGH` reviews —
> [`d7ff65b9`](https://platform.edisonscientific.com/trajectories/d7ff65b9-1211-4ced-934e-c3c402eddee0)
> (verification of the first-test-run procedure, 20 refs),
> [`86586e0a`](https://platform.edisonscientific.com/trajectories/86586e0a-afe9-466e-86fe-81590fd46d2a)
> (crevice-tool continuity anomaly, 10 refs), and
> [`56c08a19`](https://platform.edisonscientific.com/trajectories/56c08a19-eebc-477b-a627-bf82808189ec)
> (disposal, 15 refs) — plus the **2026-07-06 BYU Risk Management / Waste Management meeting**
> (Bryant, Steve, Jill, Ed), the **118EXP OEM manual** (UL 1213 par. 22 continuity
> requirement), the **AlSi10Mg and Si SDS** files in this repo, and Nilfisk tech-support
> calls/emails through 2026-09-03. Nothing here is new research; it is the same guidance
> reorganized into the order an operator actually performs it.
>
> **Standards basis:** NFPA 484, NFPA 652, NFPA 654, NFPA 77, OSHA 29 CFR 1910.157, UL 1213
> par. 22 (via the OEM manual).
>
> ⚠️ **AI-synthesized working procedure, not a regulatory ruling.** BYU EHS / Risk Management
> and the faculty PI must review and approve it, and it must be folded into the
> site-specific NFPA 652 Dust Hazard Analysis (DHA), **before** use with live powder.

**Document date**: 2026-09-04 · **Rev**: 1 (first standalone issue) · **Owner**: VCL — Ronnie Guymon

---

# STANDARD OPERATING PROCEDURE: Vacuuming AlSi10Mg / Si Powder with the Nilfisk CFM 118EXP

**Facility**: BYU Vertical Cloud Lab (VCL)
**Equipment**: Nilfisk CFM 118EXP explosion-proof vacuum · antistatic main filter (+ clamp) · upstream HEPA · downstream HEPA · conductive hose 107413543 · cuff 4072000343 · aluminum wand 01768601 · crevice tool 01768900 · dust brush 01719401
**Applicable powders**: AlSi10Mg and elemental Si (aluminum family). **Not** for iron-, copper-, nickel-oxide-bearing, or titanium powders without the alloy-switch procedure in §6.

---

## 0. GATES — DO NOT RUN LIVE POWDER UNTIL THESE ARE CLOSED

| # | Gate | Status as of 2026-09-04 |
|---|---|---|
| 0.1 | **Crevice tool 01768900 reads ≤ 0.1 Ω tool-to-wand.** The last bench measurement (2026-08-19) was **open / MΩ** — an anodized socket bore leaves the tool an *isolated conductor* in the powder stream. The OEM manual's own rule applies: *"if unacceptable results are recorded, DO NOT OPERATE THE CLEANER."* | ❌ **Open.** Tool is out of service. Run the §1.4 remediation ladder, or **run the first test with the dust brush alone** (0.03 Ω, passes). |
| 0.2 | **Class D extinguisher** (Met-L-X / Lith-X / NaCl-based) staged at the station — ≤ 75 ft travel distance per OSHA 1910.157, ideally ≤ 25 ft. **Never** water, CO₂, or ABC on this powder. | ❌ Not confirmed procured. |
| 0.3 | **ESD wrist strap decision.** A strict reading of NFPA 484 §15.3.1.2 calls for the operator to be grounded (sub-micron fines can have MIE < 30 mJ). This was **not** on the 2026-07-06 Risk-Management PPE list, and the epoxy/vinyl floor rules out ESD-footwear grounding. | ⚠️ Reconcile with EHS — then edit §2 accordingly. |
| 0.4 | **Nilfisk clearance in writing.** The 2026-09-03 phone call ("probably anodized, good to use if everything else is low") conflicts with the 2026-08-31 written answer ("the crevice nozzle should be measuring close to 0 Ω, not in MΩ"). Get the resolution by email, referencing UL 1213 par. 22. | ⚠️ Requested. |
| 0.5 | **EHS + PI sign-off on this operating SOP** (not only the disposal SOP) and a documented **NFPA 652 DHA** on file. | ⚠️ Pending. |

---

## 1. PRE-USE CONTINUITY VERIFICATION (REQUIRED BEFORE **EVERY** USE)

The OEM manual is explicit: *"THE OPERATOR SHOULD TEST THE VACUUM MACHINE FOR GROUND
CONTINUITY BEFORE EACH USE,"* checked *"between each connection … tool to wand, wand to hose,
hose to machine,"* and the path **"shall not exceed 0.1 ohm"** (UL 1213 par. 22). This is an
OEM requirement, not merely an NFPA-derived best practice.

### 1.1 Acceptance criteria

| Path | Criterion | Notes |
|---|---|---|
| **Each metal-to-metal connection** — tool → wand, wand → coupler, coupler → hose cuff, hose → machine inlet | **≤ 0.1 Ω** | The governing gate. Any single failing joint blocks the run. |
| **Assembled path** — tool tip → wand → coupler → hose → vacuum inlet | ≤ 0.1 Ω per connection; hose contributes its own resistance | Measure assembled, as the manual intends. |
| **Hose end-to-end** | ~4 Ω typical; spec **R ≤ 10⁴ Ω** | Nilfisk-confirmed normal for their conductive hose. The hose is a **listed component**, not a "connection," so it is judged against its own spec — it passes. |
| **Vacuum body / bin → building ground** | **< 1 Ω** | Body sections measured ~0.2 Ω, lid-to-ground-cable ~1 Ω. |
| **Conductive liner (seated) → bin / ground** | **< 1 kΩ** | Re-check after **every** liner change. There is no bonding clip on this unit — grounding is by liner-to-bare-bin contact. |
| **Dust brush ferrule → wand** | **< 10 Ω** (measured 0.03 Ω ✅) | Also confirm the **bristles** are the conductive EXP variant — a bonded ferrule with nylon bristles is still a floating path at the tips. |
| **Any metal object in the work zone → ground** | **< 10 Ω** | Isolated-conductor sweep, §2.3. |

### 1.2 Meter and technique

- Use a milliohm-capable meter (the EXTECH 380560 used for the baseline resolves 0.01 Ω); a
  general-purpose DMM cannot resolve 0.1 Ω meaningfully. Zero/REL the leads first.
- **Probe the marked points.** Standardized probe points are marked on the vacuum and tools;
  use them every time so readings are comparable run-to-run.
- Press **firmly**, hold **still**, and maximize contact area (side of the probe, not the
  point). Sloppy technique swings readings by orders of magnitude; good technique repeats to
  ~10 mΩ.
- **Record every reading in the session log** (§9) and compare against the previous run — a
  drifting joint is the early warning.

### 1.3 If everything passes

Proceed to §2. If anything fails, **stop** — do not run powder.

### 1.4 If a joint fails — remediation ladder (do them in this order)

Applies to the crevice tool (gate 0.1) and to any joint that goes open. **Do not abrade any
surface you can see** — an anodized skin *over grounded metal* is harmless (it breaks down at
~20–125 V, far below the ~4 kV propagating-brush-discharge threshold). The only problem is a
tool body that **floats**, so the only place bright metal is needed is inside the socket bore.

1. **Probe the anodizing rack marks** — the small bare spots where the part hung during
   anodizing, often inside the bore or at sharp edges. You may get continuity with **zero**
   abrasion.
2. **Seat the tool fully and tightly** on the wand and re-measure — an interference fit can
   scrape through the skin on its own. **No abrasion.**
3. **Plastic-safe contact cleaner** (e.g. CRC QD) on the bore and wand tip, re-seat,
   re-measure. Clears oil/oxide films; will not touch anodize. **No abrasion.**
4. **Only if 1–3 fail:** hand-abrade a **5–10 mm contact band inside the socket bore** and the
   mating band of the wand tip with **gray or maroon Scotch-Brite** (not green). **Hand only —
   no Dremel, no grinder** (power tools generate far more combustible Al fines and gouge the
   seat). Do this **before** the tool has touched powder, away from ignition sources, and
   capture debris with an IPA-dampened wipe.
5. **Re-verify ≤ 0.1 Ω assembled, record the value,** and document the remediation in the DHA
   — the manual treats bore work as an "alteration."
6. **If it still won't reach ≤ 0.1 Ω, stop and replace the tool.** Do not escalate the
   abrasion.

---

## 2. SETUP — BEFORE THE POWDER COMES OUT

### 2.1 PPE (all steps below)

- **N95 or P100 respirator** — the AlSi10Mg SDS lists **H334** (respiratory sensitizer).
- **Nitrile gloves** (non-sparking; no latex).
- **Cotton or antistatic lab coat.** The black VCL coat is 100% cotton ✅; the atomizer coat is
  antistatic ✅; the **80/20 poly-cotton white coat is not acceptable** ❌ — it builds static.
- **Safety glasses.**
- Closed-toe shoes.
- **ESD wrist strap** — pending the gate-0.3 decision with EHS; wear one if available.

### 2.2 Machine and station

- [ ] **§1 continuity check passed** and readings logged.
- [ ] **All three filters installed** — antistatic main filter (with clamp), upstream HEPA,
      downstream HEPA.
- [ ] **Conductive liner seated** in the bin, in contact with bare bin metal, lining the
      interior; liner-to-bin **< 1 kΩ** verified. Black carbon-loaded PE only — never pink
      "antistatic" or silver shield bags.
- [ ] **Class D extinguisher** staged and within reach (gate 0.2).
- [ ] **Grounded steel interim pail** staged with its lid available, labeled per the disposal
      SOP.
- [ ] **Nothing wet, hot, or oxidizing** on the bench; no water, no solvents at the station,
      no compressed air anywhere near this task.

### 2.3 Work zone — isolated-conductor sweep (the most important addition)

The hazard is **ungrounded metal**, not an unbonded floor. An insulating floor (concrete,
epoxy, vinyl) cannot act as the capacitor that produces a spark, and NFPA 484 §15.3.1.1
requires *the equipment* to be grounded and bonded — not the surface being cleaned. Vacuuming
powder off a floor or off the atomizer housing **is the job**, and the bonded
wand → coupler → hose → vacuum chain is the control that makes it safe.

- [ ] Walk the area and **bond or remove every ungrounded conductor** near the powder: metal
      tray, cart, step stool, loose sheet-metal panel, metal trash can, unattached duct stub.
      Anything metal that stays gets a bonding wire to the vacuum body or the same building
      ground point, **verified < 10 Ω**.
- [ ] **Confirm the atomizer housing / frame is bonded to building ground (< 10 Ω).** This is
      the full-scale version of the same rule — a large metal enclosure in direct contact with
      charging powder — and it matters far more than what the powder is sitting on.
- [ ] **Area control:** restrict the immediate area to trained, PPE-equipped personnel; post
      signage — *"COMBUSTIBLE METAL POWDER IN USE — Authorized Personnel Only — NO Water, NO
      Compressed Air."*
- [ ] Second person available (and recording video, for the training record).

### 2.4 For the first test run specifically

- [ ] Use a **few grams** of AlSi10Mg over a **small, defined footprint you can verify clean**
      afterward against the NFPA 654 **1/32-inch layer-depth** criterion — not spread widely
      or where fines can travel under equipment.
- [ ] The floor or housing surface is acceptable and is representative of the real job; a
      **bonded** metal tray at bench height gives better nozzle control if the run allows it
      (ergonomics preference, not a safety gate).
- [ ] Run end-to-end — pickup, suction, sealing, disposal handoff — before scaling up.

---

## 3. VACUUMING

**Goal: keep powder out of the air.** Sub-micron fines can have MIE < 5 mJ; bulk AlSi10Mg is
80–350 mJ.

1. **Equalization touch.** Before the wand tip approaches the powder, briefly touch the
   grounded wand tip to **any grounded metal point** — the vacuum body, a bonded frame, the
   bench ground — *away from the powder*.
2. **Vacuum ON before** you approach the powder.
3. **Move slowly.** Slow, deliberate passes; let the airflow do the work. Fast motion,
   dropping, and piling are what put powder airborne.
4. **Keep the nozzle close to the surface** so capture velocity is highest right at the
   powder.
5. **Never blow powder toward the nozzle**, and never use compressed air anywhere near this
   task (NFPA 484 prohibition; AlSi10Mg SDS §8.2).
6. **Lift the tool away from the powder before switching OFF**, so no loose pile is left at
   the tip.

**Crevice nozzle** (⚠️ gated by 0.1) — corners, seams, gasket grooves, around fittings, small
spills. Its small opening gives the highest tip velocity, which is what dense settled metal
powder needs. Draw it steadily along the crevice; don't stab at piles.

**Dust brush** — adherent fines on flat/contoured surfaces (µm powder clings electrostatically
and won't lift with suction alone). Use **brush-and-capture**: let the bristles just kiss the
surface to release powder while the airflow at the ferrule takes it — **don't sweep powder
across the surface into the air**.

**Watch continuously for:**

- **Visible airborne dust** → slow down, get the nozzle closer.
- **Bin fill** → never exceed ~**25%**.
- **Warmth or odor** → stop. Never vacuum hot or glowing particles; let any powder off a
  laser/furnace/hot plate cool to room temperature first.

---

## 4. SHUTDOWN — IMMEDIATELY AFTER VACUUMING (EVERY SESSION)

1. **Clear the bores:** with the tool in **clean air** (not sitting in powder), run the vacuum
   **15–30 s** to pull residual fines out of the hose/wand bores into the liner.
2. **Power off. Wait ≥ 60 s** for airborne powder to settle **before opening or disassembling
   anything.**
3. **Check liner fill.** If **> ~25%**, seal and remove now (step 4). If below and you are not
   switching powders, it may stay for the next session.
4. **Seal and transfer** (this is the handoff to the disposal SOP):
   - Gently gather the liner above the powder, **gooseneck-twist 2–3 turns**, secure with
     **conductive/ESD tape or two steel zip ties**.
   - Lift the sealed liner into the **grounded steel interim pail**.
   - **Set the lid on — do NOT crimp it.** (Waste Management: crimping raises the explosion
     hazard; the un-crimped lid vents trace H₂.)
   - Install a **fresh conductive liner**, seated against bare bin metal; re-verify
     liner-to-bin **< 1 kΩ**.
5. **Clean the tools** (§5) and **store them** (§6).
6. **Log the session** (§9). Contact BYU Waste Management for pickup when the pail warrants
   it; the pail is on a **1-year clock** from the date EHS tags it.

---

## 5. CLEANING THE TOOLS AFTER USE

### 5.1 Same alloy family (AlSi10Mg ↔ Si ↔ other Al alloys) — routine care

A full IPA cleaning is **not** required every time.

1. **Dry-wipe FIRST.** Remove all visible powder with a dry lint-free wipe (Kimwipes are
   acceptable).
2. **Then a light IPA wipe** — *dampened, not wet*. **Never apply IPA to a visibly
   powder-coated surface:** IPA vapor over combustible metal dust forms a **hybrid mixture**
   with a *lower* ignition energy than either alone. The AlSi10Mg SDS also lists **alcohols**
   among incompatible materials — so: sparing, dry-wipe-first, never a soak.
3. Prefer **70% IPA** (higher flash point than 99%); work with ventilation on and ignition
   sources away.
4. **Let it evaporate fully — ≥ 5 min, until there is no IPA smell** — before reassembly,
   bagging, or any contact with powder.
5. **Dust brush: do not wet the bristles.** Tap them out gently into the sealed liner with the
   vacuum running, then wipe the **ferrule/body only**. Soaked bristles hold both solvent and
   fines and dry slowly.
6. **Re-verify continuity after any cleaning or reassembly** (§1).

**Never:** water, acetone, or chlorinated solvents (the SDS notes a violent reaction with
halogenated hydrocarbons); never blow out, wash, or rinse the filters or attachments.

### 5.2 How to wet the wipe — **do not decant IPA into a spray bottle**

Spraying is routine lab practice elsewhere; it is specifically wrong here. Atomizing a
flammable liquid over combustible metal fines is exactly the hybrid-mixture case (a mist
ignites below the bulk flash point); the plastic bottle and the charged droplets reintroduce
the charged insulator this whole setup exists to eliminate; overspray lands on powder; the jet
disperses powder like the prohibited compressed air; an N95 gives **no** protection against
solvent vapor; and a decanted bottle is a GHS-labeled secondary container that must not live
at the vacuum station.

Approved alternatives, in order:

| Option | Why it fits |
|---|---|
| **Pre-saturated 70% IPA wipes** (best) | Exactly damp-not-wet, no bulk solvent at the bench, no aerosol, no dispensing static. E.g. Berkshire SatPax 1000 (70% IPA, 6×9", 100/canister) or Texwipe TechniSat TX1045. |
| **Steel plunger dispensing can** | Press the wipe on the plunger for a metered wet spot — no aerosol; the can is metal, bondable, and FM/UL-listed with a flame-arrester pan (e.g. Justrite 1-pt/1-qt). |
| **Pour-and-dab, bottle closed** | Free. At a ventilated spot **away from the powder**, tip a small amount onto the wipe, **re-cap immediately**, carry the damp wipe to the tool. |

Keep bulk IPA in the flammables cabinet — **not** at the vacuum station.

### 5.3 Where the used wipes go

A Kimwipe loaded with AlSi10Mg **is** combustible metal dust — it does not go in the regular
trash.

- **Dry wipes** → into the vacuum's conductive liner (or a small conductive bag that goes into
  it) with the collected powder.
- **IPA-damp wipes** → lay flat in a ventilated spot until the IPA has **fully flashed off
  (≥ 5 min, no smell)**, *then* bag them with the dry wipes. **Never** drop a solvent-wet wipe
  into the sealed liner or the interim pail — the un-crimped lid is for trace H₂ venting, not
  solvent vapor.
- Confirm this handling in one line with Jill/Ed at Waste Management, since the pail is on
  their tracking system.

---

## 6. SWITCHING POWDERS

| Situation | What is required |
|---|---|
| **AlSi10Mg ↔ Si ↔ other Al-family** | Compatible. Liner swap + dry wipe + visual check. Same tools, same pail. |
| **Any iron-, copper-, or nickel-oxide-bearing powder, or Ti** | **Incompatible — thermite precursors.** Replace the main filter **and both HEPA filters** (dispose as contaminated waste), full IPA clean of bin/hose/wand/tools, fresh liner, **fresh dedicated interim pail**, and re-verify continuity before use. |

Keep this hose/wand/crevice/brush set **dedicated and labeled** as the aluminum-family set.
The dust brush especially retains powder in its bristles — never share it across families.

---

## 7. STORING THE WAND AND ATTACHMENTS

Powder left inside a wand, crevice nozzle, or brush **is** an accumulation of combustible
metal dust.

- **Clean first, then store** (§5). Don't store visibly powder-coated tools.
- **Store dry** — no moisture near stored tools (damp Al fines can self-heat). Away from
  sinks, eyewash, and water lines.
- **Contain residual dust:** cap/plug the wand and crevice-tool openings, or slip each tool
  into a **black carbon-loaded conductive PE bag** (same liner stock, small). One shared bag
  for same-family tools is fine — label it.
- **Segregate** from oxidizers, metal-oxide powders, and ignition sources — store with/near
  the grounded vacuum station, not in a drawer of random chemicals.
- Keep the **storage area** itself clean to the NFPA 654 **1/32-inch** layer-depth criterion.
- Don't let sealed powder-loaded tools and full liners accumulate — collected powder belongs
  in the liner → pail → EHS stream.

> If a tool truly can't be cleaned before storage (end of a long session), treat it as
> containing combustible dust: cap/bag it, keep it dry and grounded, and clean it before the
> next use.

---

## 8. SPILL RESPONSE

- **NEVER sweep** — sweeping creates the dust cloud.
- Scoop visible piles with a **non-sparking (plastic or brass) scoop** into a conductive bag.
- Re-vacuum only after confirming the ground chain is intact.
- For any visible layer on the floor: restrict access, ventilate, and call EHS.
- Fire: **Class D only.** Never water, CO₂, or ABC.

---

## 9. ABSOLUTE PROHIBITIONS

| Never | Why |
|---|---|
| Water, or wet cleaning of anything powder-contaminated | Al + H₂O → H₂ (SDS **H261**); Class D fire risk |
| Compressed air to blow powder or clean tools/filters | Creates an explosive dust cloud (SDS §8.2; NFPA 484) |
| Acetone or chlorinated solvents | Violent reaction with halogenated hydrocarbons |
| Spraying/atomizing IPA near the powder | Hybrid mixture; mist ignites below bulk flash point (§5.2) |
| IPA on visible powder, in the liner, or on filters | Hybrid mixture; lower MIE than either alone |
| Running with any joint failing the ≤ 0.1 Ω check | OEM: *"DO NOT OPERATE THE CLEANER"* |
| Ungrounded metal objects in the work zone | Isolated conductor: ~5–10 mJ at ~10 kV vs. fines MIE < 5 mJ |
| Crimping the interim-pail lid | Blocks trace H₂ venting; raises explosion hazard |
| Vacuuming hot or glowing particles | Direct ignition source |
| Mineral-oil (or any) passivation of the collected powder | Adds a Class IB flammable liquid; dry sealed grounded containment is sufficient at this scale |
| The 80/20 poly-cotton white lab coat | Builds static |
| Bin above ~25% fill, or pail above ~50% | Accumulation limits set for this SOP |

---

## 10. SESSION LOG (record every run)

Date · operator · powder type · approximate mass vacuumed · **all §1 continuity readings** ·
liner and pail fill after the run · any anomaly (airborne dust, warmth, odor, suction loss) ·
video reference. Drifting continuity readings are the early warning of a failing bond — log
the numbers, don't just check a box.

# OPERATOR QUICK-REFERENCE CARD — 118EXP POWDER PICKUP

**PPE:** N95 · nitrile gloves · cotton/antistatic lab coat (not the white poly one) · safety
glasses · ESD strap if issued.

**Before**

- [ ] Continuity: every joint **≤ 0.1 Ω** · hose ~4 Ω · body-to-ground **< 1 Ω** · liner-to-bin
      **< 1 kΩ** — log the numbers. *Fail = do not run.*
- [ ] Crevice tool cleared (≤ 0.1 Ω) — otherwise **dust brush only**.
- [ ] 3 filters in (main + clamp, upstream HEPA, downstream HEPA).
- [ ] Fresh conductive liner seated against bare bin metal.
- [ ] Class D extinguisher staged · interim pail + lid staged.
- [ ] Bond or remove all loose metal in the zone (**< 10 Ω**), including the atomizer housing.
- [ ] Signage up · second person present/recording · small defined footprint of powder.

**During**

- [ ] Touch wand tip to grounded metal (away from powder) → **vacuum ON** → approach.
- [ ] Slow passes · nozzle close · brush just kisses the surface · never blow powder.
- [ ] Watch: airborne dust · bin ≤ 25% · any warmth/odor → **stop**.
- [ ] Lift tool clear of the powder **before** switching off.

**After**

- [ ] 15–30 s run-on in clean air → **power OFF → wait ≥ 60 s.**
- [ ] Liner > 25%? → gooseneck twist ×2–3, ESD tape / 2 steel ties → into the pail → **lid on,
      NOT crimped** → fresh liner.
- [ ] Dry-wipe tools first, **then** a barely-damp 70% IPA wipe (never spray; brush bristles
      stay dry) → let dry ≥ 5 min / no smell.
- [ ] Dry wipes into the liner; IPA wipes flash off first.
- [ ] Cap/bag tools, store dry with the aluminum-family set.
- [ ] Log the session.

**Emergency:** Class D extinguisher only — **no water, no CO₂, no ABC.** Evacuate, alert
others, call BYU Risk Management. Never sweep a spill.
