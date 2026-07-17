# Canopy Hood and Soft-Wall Partition Options

Research for ventilation / powder-containment at the BYU Vertical Cloud Lab, revisiting the **"portable cleanroom" / soft-wall partition** vs **canopy hood** comparison requested on [Issue #2 (Fumehood)](https://github.com/vertical-cloud-lab/byu-vcl/issues/2). See also [Issue #75 (Glovebox)](https://github.com/vertical-cloud-lab/byu-vcl/issues/75), [Issue #30 (Glovebox)](https://github.com/vertical-cloud-lab/byu-vcl/issues/30), and [Issue #53 (VLM venting)](https://github.com/vertical-cloud-lab/byu-vcl/issues/53).

## Context and Decision History

The original plan was to either (a) relocate the existing Hamilton SafeAire fume hood from the old welding lab or (b) purchase a new one. After follow-up with BYU Engineering Facilities (Barry Holman, Dave Laws):

- **Moving the existing fume hood**: ~$75,000 and ≥3 months (reroute ducting, phoenix valve, rebalance).
- **New fume hood**: ~$40,000–$45,000 for the phoenix valve + commissioning + install (plus the hood itself, ~$15K new or ~$3K used), also ≥3 months.
- **Final guidance (meeting with Barry Holman)**: **Installing a fume hood — even tied to general exhaust — is not possible due to university liability concerns about future use.** The recommended alternative is a **canopy hood tied to general exhaust**, which is much cheaper and avoids chemical-exhaust loading (which is already at maximum capacity).
- Chemicals in the lab will be non-corrosive and limited to what general exhaust can safely handle. Equipment hookups for the glovebox + atomizer + sink/drain were estimated by Dave at **~$25K total (excluding any hood)**.

This document compares the canopy-hood route with soft-wall / portable-cleanroom and other source-capture alternatives so the team can decide on the containment strategy for the ultrasonic atomizer, powder handling, and related equipment.

## Use Case and Requirements

- Handle fine metal powders (Al, Si, Mg, AlSi10Mg, etc.) during weighing, transfer, and ultrasonic atomization without breathing them in.
- Avoid corrosive chemicals (per facilities guidance) — the containment is primarily for **particulate** control, not solvent vapor.
- Keep powders from migrating across the lab (goal expressed in the original issue: *"airflow in from the top and airflow out in the bottom of the partition… to keep powder towards the ground"*).
- Tie into the existing lab layout: adjacent to glovebox, VLM ([#53](https://github.com/vertical-cloud-lab/byu-vcl/issues/53)), and atomizer.
- Be compatible with NFPA 484 (combustible metals) practices: grounding, Class D extinguisher, no water-based suppression, explosion-proof vacuum already procured (see [`vacuum-accessories-options.md`](./vacuum-accessories-options.md)).

| Requirement | Target |
|---|---|
| Primary hazard | Airborne metal powders (combustible dust) |
| Chemicals | Non-corrosive only; general exhaust, not chemical exhaust |
| Containment mode | Source capture + general room air management |
| Footprint | Wall-mounted bench area (approx. where whiteboards are today) |
| Compatibility | Glovebox, VLM, atomizer hookups in the same work order |
| Codes | NFPA 484, NFPA 652, BYU Chemical Hygiene Plan |

### Lab Layout / Floorplan Reference

Room **CB154** floorplans are checked into the repo at [`cb154.pdf`](./cb154.pdf) and [`cb154-annotated.pdf`](./cb154-annotated.pdf) (obtained via [pf.byu.edu/space](https://pf.byu.edu/space); see [issue #31 comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/31#issuecomment-4292025463) and the earlier dimensions Gage captured in [issue #7 comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/7#issuecomment-3787027938)). Anyone sizing a canopy hood or softwall partition should cross-check the candidate footprint (6'×8', 8'×8', 10'×10', etc.) against the annotated plan before placing a quote, including:

- Clearance for entry (≥3 ft on at least one open face of a softwall).
- Aisle / egress paths that cannot be blocked by curtains.
- Proximity to the glovebox ([#30](https://github.com/vertical-cloud-lab/byu-vcl/issues/30) / [#75](https://github.com/vertical-cloud-lab/byu-vcl/issues/75)), VLM ([#53](https://github.com/vertical-cloud-lab/byu-vcl/issues/53)), atomizer, and the OT-2 so the high-emission bench sits inside the containment envelope.
- Ceiling height for FFU / canopy-hood + duct (softwall frames are 8 ft; room ceiling must accommodate plus the FFU plenum on top).

## Option A — Canopy Hood (Recommended by Facilities)

A canopy hood is an open exhaust hood suspended above the work surface. It is **not** a fume hood — it has no sash or enclosure — but it pulls air from the room and from above the workstation below, carrying fine particulates up through a duct to general exhaust.

Barry Holman and Dave Laws indicated BYU can **custom-build** a canopy hood sized to our bench (see the example photo from the neighboring lab, attached in the issue). This is the path Facilities prefers for our lab.

### Pros / Cons

| Pros | Cons |
|---|---|
| Allowed by BYU liability policy (general exhaust, non-corrosive) | Open system — containment depends on face velocity & geometry; not suitable for toxic vapors |
| Much cheaper than a fume hood install | Dave warned earlier that a *large* canopy hood would overload building capacity; must stay small (~2'×2' to ~3'×3') |
| Custom-sized to fit bench, glovebox antechamber area, and atomizer exit | Still requires duct + Phoenix valve / balance damper integration with general exhaust (cost bundled in the ~$25K equipment-hookups estimate per Dave) |
| Can be combined with soft-wall partition or snorkel arms for better capture | Not a cleanroom; particles can drift sideways at low face velocity |

### Sizing Guidance

- Dave's earlier note (see [issue #2 comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/2)): building cannot handle a *large* canopy hood; a **~2' × 2'** unit is likely the maximum. A larger 3' × 3' or 4' × 4' should only be pursued if Facilities confirms airflow capacity.
- ASHRAE / ACGIH Industrial Ventilation guidance for canopy hoods: exhaust volume Q ≈ 1.4 × P × H × v, where P is the hood perimeter, H the height above the source, v the desired capture velocity (typically 75–125 fpm for nuisance dust). For a 2'×2' hood 2 ft above bench at v = 100 fpm, that's ≈ 1,120 cfm — non-trivial but within general-exhaust range.
- Mount close to the source (≤18–24") to improve capture and reduce required flow.

### Vendor / Fabrication Options

| Option | Vendor | Typical Price (hood only) | Notes |
|---|---|---|---|
| **BYU shop-built** (recommended) | BYU Engineering Facilities | Bundled in ~$25K equipment-hookups estimate from Dave | Sized to our bench; matches neighboring-lab precedent |
| Fisherbrand Stainless Steel Canopy Hood | [Fisher Scientific](https://www.fishersci.com/) | ~$1,500–$4,000 for 36–48" units | Standard sizes start at 36" wide; 2'×2' is usually custom |
| HEMCO Canopy Hoods | [hemcocorp.com/canopy.html](https://hemcocorp.com/canopy.html) | ~$2,000–$5,000+ | Fiberglass and stainless versions; common in academic labs |
| Genie Scientific custom | [geniescientific.com](https://www.geniescientific.com/custom-fume-hoods/) | Quote | Custom sizes available |
| Scientifix canopy fume hoods | [scientifix.net](https://www.scientifix.net/products/fume-hoods/canopy-fume-hood/) | Quote | Custom and standard sizes |
| Spencer-Virnoche canopy | [spencervirnoche.com](https://spencervirnoche.com/products/canopy-fume-hoods/) | Quote | |

> **Recommendation**: Stick with the BYU shop-built approach for the hood itself to keep it inside Facilities' design envelope and avoid separate procurement/compliance review. If a store-bought unit is ever needed, budget **~$1,500–$5,000** for the hood plus **$3,000–$10,000** for blower, ductwork, and a balance damper, in addition to whatever Phoenix-valve / commissioning charges Facilities adds.

## Option B — Soft-Wall Partition / Portable Cleanroom

Inspired by the agent instruction: *"partitioned off this area with soft walls, airflow in from the top and airflow out in the bottom of the partition, to keep powder towards the ground"*. A soft-wall cleanroom is a steel frame with antistatic vinyl strip curtains, ceiling-mounted Fan Filter Units (FFUs) that push HEPA-filtered air **downward** through the volume, and an air return near the floor. Operated at **negative pressure** with respect to the rest of the lab, it forms a "downflow" containment around the bench without building-level ducting.

This is not a direct substitute for the canopy hood; it is complementary. It addresses powder migration within the lab, protecting the rest of the room from the bench area, while the canopy hood (or snorkel, below) removes captured particulate from the bench itself.

### Pros / Cons

| Pros | Cons |
|---|---|
| No building ducting required (HEPA-recirculated FFUs); fast to deploy | Recirculated HEPA is OK for particulate but not for vapors |
| Downflow pattern naturally drives powders toward floor (matches agent-instruction concept) | Combustible-metal-dust handling in a recirculated FFU needs an **explosion-proof motor** and grounding; standard ValuLine FFUs are not ATEX-rated |
| Modular / relocatable; does not trigger a capital build-out | Takes up floor space (need ≥8'×8' footprint with clearance) |
| Can be operated at negative pressure by balancing FFU supply vs. room exhaust (canopy hood) | Curtains are not a substitute for a fume hood; won't contain vapors |
| Matches lab-wide dehumidification plan — keeps the bench volume dry (Barry/Dave thought the whole room would stay dry enough without sealing, but this buys insurance) | Not an OSHA-rated "enclosure" for regulated chemicals |

### Vendor Pricing Snapshot

| Vendor | Model / Size | Price (room only; no FFU) | FFU Add-On | Notes |
|---|---|---|---|---|
| **Terra Universal ValuLine** | 6'×8'×8' (P/N 6600-66A-VL-0608) | ~$4,723 | WhisperFlow 2'×4' FFU ~$744 each | [ValuLine Softwall](https://www.terrauniversal.com/valuline-softwall-cleanrooms.html); ships in 4–6 days |
| Terra Universal ValuLine | 8'×8'×8' | ~$5,500 | Same | |
| Terra Universal ValuLine | 10'×10'×8' | ~$6,500–$7,000 | Same; typically 2–4 FFUs | |
| **Cleatech Softwall** | 8'×8'×8' | ~$6,260 | +FFUs/filters | [8'×8' listing](https://www.cleatech.com/product/softwall-cleanroom-8-x-8%E2%80%B2/) — excludes filters/accessories |
| Cleatech Softwall | 10'×10'×8' | ~$7,060 | +FFUs/filters | [10'×10' listing](https://www.cleatech.com/product/softwall-cleanroom-10-x-10/) |
| AirClean Systems | Custom | Quote | | Ductless / recirculating lines available |
| Plas-Labs, Inc. | Curtained enclosures | Quote | | Budget builder-kit style |

> **Typical all-in cost for a working 8'×8' downflow softwall (frame + curtains + 1–2 HEPA FFUs + LED lights):** **~$6,500–$10,000**.
>
> Budget additional **~$1,000–$3,000** for antistatic / ESD curtain upgrade and grounding kit if used with combustible metal powders.

### Key Design Notes for Combustible Metal Powders

- Use **antistatic / ESD-dissipative vinyl** curtain strips, not standard PVC, to reduce static discharge risk.
- All frame members and FFUs must be **bonded and grounded** per NFPA 484.
- Standard FFU motors are not explosion-proof. For fine Al / Mg dust handling **inside** the partition, pair with a HEPA-filtered explosion-proof vacuum (already procured — see [`vacuum-accessories-options.md`](./vacuum-accessories-options.md)) and do powder transfers in small quantities.
- Run the partition at slight **negative pressure** (exhaust > supply) so leaks are inward. Easiest way: tie the canopy hood (Option A) or a snorkel (Option D) into the partition footprint so exhaust > FFU supply.

## Option C — Ductless / Recirculating Fume Hood (Backup)

Self-contained hood with internal HEPA + (optional) carbon filtration. No building ducting. Useful as an interim containment solution for weighing and small powder transfers.

| Vendor / Model | Price Range | Notes |
|---|---|---|
| Sentry Air Systems benchtop (e.g., SS-340 series) | ~$1,000–$4,000 new; ~$1,250 used | HEPA / ULPA options; see used listings on LabX |
| Air Science Purair FLOW / BASIC | $3,000–$8,000+ | Common in academic labs |
| Erlab Captair ductless | $5,000–$12,000+ | High-end filter monitoring |

> **Limitation**: Internal motors in most ductless hoods are **not** explosion-proof. Use only for non-ignitable quantities of metal powder, or pair with an explosion-proof vacuum for cleanup. Confirm filter compatibility before buying.

## Option D — Point-Source Capture (Snorkel / Elephant Trunk)

A **snorkel arm** (aka extraction arm, elephant-trunk) is an articulated flex duct with a hood at the end, positioned directly over a specific source such as the ultrasonic atomizer outlet, the glovebox antechamber, or a bench-top weigh station. Often the cheapest and most effective way to grab particulate right at the emission point; can be combined with Option A or B.

| Option | Vendor | Price | Notes |
|---|---|---|---|
| Fume Dog Economy Extraction Arm / Snorkel, 6"×10' | [fumedog.com](https://fumedog.com/products/fume-dog-economy-extraction-arm-snorkel-hanging-6-x-10) | ~$855 | Metal construction, hanging mount |
| Cole-Parmer ICI Quick-Ship Exhaust Snorkel, 3"×57" | [coleparmer.com/p/81840](https://www.coleparmer.com/p/ici-quick-ship-exhaust-snorkels/81840) | ~$1,675–$2,135 | Anodized aluminum; ships quickly |
| Labs-USA exhaust snorkel | [labs-usa.com/laboratory-fume-hoods/exhaust-snorkel/](https://labs-usa.com/laboratory-fume-hoods/exhaust-snorkel/) | Quote | Referenced in [issue #2](https://github.com/vertical-cloud-lab/byu-vcl/issues/2) comment |
| Nederman Original Extractor | [nederman.com](https://www.nederman.com/) | ~$1,500–$3,500 | Industry standard; polypropylene / stainless variants |

> **Ideal pairing**: One snorkel at the atomizer outlet, one near the VLM door (addresses [issue #53](https://github.com/vertical-cloud-lab/byu-vcl/issues/53)), both teed into the same general-exhaust duct as the canopy hood. Facilities can bundle this duct work with the canopy-hood install.

## Option E — Two Paths Forward (Choose or Combine)

The softwall-partition and canopy-hood paths are substantially different in both cost and what they deliver. It's worth treating them as **two separate candidate plans** rather than assuming both are needed up front.

### Plan 1 — Softwall partition only (cheapest, no Facilities work)

- **Total estimated cost: ~$7.5K–$13K** (one-time, no institutional work order).
- 8'×8' Terra Universal ValuLine or Cleatech softwall + 1–2 HEPA FFUs + LED + antistatic curtains and grounding.
- Pair with the existing explosion-proof vacuum ([`vacuum-accessories-options.md`](./vacuum-accessories-options.md)) and a Class D extinguisher for combustible-metal-dust handling.
- No building ducting, no Phoenix valve, no general-exhaust rebalance — so it avoids the 3-month Facilities lead time altogether.
- **Integrate the dehumidifier *as* one of the softwall panels** (per @sgbaird-yolo's refinement in [this comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/96#issuecomment-4292305653) — i.e., the dehumidifier replaces one wall panel rather than sitting as a free-standing appliance inside). The already-procured **Quest 155** (see [PR #43 / issue #42](https://github.com/vertical-cloud-lab/byu-vcl/pull/43)) ships with a **MERV-13 filter** on the intake (spec'd in that doc as *"laboratory-grade filtration, removes particles and microorganisms"*) and an internal blower (~435 CFM at 0" w.c., dropping at higher external static). Mounting it as a panel:
  - Concentrates humidity control on the ~500 ft³ envelope (8'×8'×8') vs. the full ~2,000+ ft³ room — much easier to drive to 10–15% RH for hygroscopic Al/Mg powders.
  - Reduces energy cost and recovers condensate faster than treating the whole lab.
  - Uses the Quest's blower + MERV-13 for air circulation, which tempts the question of whether the dehumidifier could **replace the FFU** entirely.
- **Spot-check of "dehumidifier in place of the FFU":**
  1. **Filter class** — MERV-13 is ~90% efficient on 1–3 µm particles but is **not** HEPA (≥99.97% @ 0.3 µm). For fine Al / Mg dust in the 1–10 µm respirable range MERV-13 gives partial protection; true HEPA (as used in WhisperFlow-style FFUs) is significantly better. **MERV-13 alone is not equivalent to a HEPA FFU for combustible-dust containment.**
  2. **Duty cycle** — a dehumidifier's fan typically runs **only when the compressor cycles on** (i.e., when RH is above setpoint). Once the envelope is dry, the unit idles and airflow stops, so the envelope would lose active filtration, air turnover, and any inward-leak (negative-pressure) protection it was providing. A HEPA FFU runs continuously. **This is the biggest argument against using the dehumidifier as the sole air mover.** Many Quest units can be forced to continuous-fan mode — confirm the Quest 155 has this setting before relying on it; even so, continuous fan without compressor re-evaporates moisture sitting on the cold coil, partially undoing dehumidification.
  3. **Airflow direction & particulates** — a dehumidifier pulls air across a cold coil and can re-entrain collected particulate when cycling, and the coil is not designed to be cleaned to combustible-dust standards. If mounted as a panel, orient the **intake to the outside** of the softwall (room air) and the **exhaust to the inside** so the envelope is supplied with dried, MERV-13-filtered air, and any powder that escapes is *not* pulled through the coil.
  4. **Codes / safety** — Quest 155 uses **R-454B** (mildly flammable A2L refrigerant). For a combustible-metal-dust envelope, confirm the motor/compressor enclosure with the manufacturer before placing it on a curtain wall that could see airborne Al/Mg dust. Bond and ground the chassis per NFPA 484.
- **Recommended configuration:** use the dehumidifier **as a panel for humidity control + room-to-envelope pre-filtration**, and **keep at least one HEPA FFU** for continuous airflow, true HEPA filtration, and to maintain slight negative pressure in the envelope. The FFU runs 24/7; the Quest 155 cycles on demand to hold RH setpoint. This preserves the cost advantage of Plan 1 while addressing the duty-cycle and filter-class gaps.
- If FFU cost is the concern, one sensitivity worth checking with Terra Universal / Cleatech is whether a **lower-flow HEPA FFU** (~$500) plus the Quest 155 as the primary circulation path is acceptable — the Quest already provides much of the air turnover while running, and the FFU only needs to cover the idle period and final HEPA polish.
- **Footprint check** (per lab floorplan [`cb154-annotated.pdf`](./cb154-annotated.pdf) / [`cb154.pdf`](./cb154.pdf), referenced in [issue #31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31#issuecomment-4292025463)): confirm an 8'×8' softwall fits the intended bench area with the required ≥3 ft clearance on at least one open side for entry. If the available footprint is tight, the Terra Universal 6'×8' (~$4,723) is a fallback; if there's more room, 10'×10' (~$7,060 Cleatech) gives space for the dehumidifier + a staging cart + the OT-2 without crowding.
- **Trade-off**: recirculated HEPA contains particulate but not vapors; not a substitute for point-source capture at the atomizer. If the atomizer outlet produces strong local plumes, add a single ductless snorkel (Option C/D) *inside* the partition.
- Strong candidate if room-level powder sampling is acceptable, or as a **near-term / interim** solution before any permanent buildout. This is also the direction currently favored by @sgbaird per the PR discussion.

### Plan 2 — Canopy hood + snorkels (Facilities-integrated)

- **Total estimated cost: ~$25K–$30K Facilities hookups + ~$2K–$4K snorkels** (bundled with glovebox + atomizer + sink hookups, so a lot of the $25K is shared infrastructure).
- Shop-built 2'×2' canopy hood tied to general exhaust + 1–2 snorkel arms over the atomizer and VLM door.
- Requires a Facilities work order and ≥3-month lead time; tied to BYU exhaust budget.
- Delivers active source capture at emission points and continuous room-air turnover — a permanent solution.
- **Can later be augmented** with a softwall partition if sampling still shows drift (adds ~$7K–$10K on top).

### Recommendation

1. If the priority is **lowest cost and fastest deployment**, start with **Plan 1 (softwall partition)** — ~$7.5K–$13K — and defer the canopy hood. Re-evaluate with air sampling after a few months of operation.
2. If a permanent canopy + glovebox + atomizer hookup is already being done anyway, **Plan 2** is the natural scope since the marginal cost of adding the canopy to the same work order is small, and a softwall can still be layered on later.
3. Either way, **keep using existing departmental fume hoods** for any rare, one-off chemistry work (per Scott's note in the issue).

## Cost Summary

| Item | Estimated Cost | Notes |
|---|---|---|
| **Softwall cleanroom 8'×8'** (Terra Universal ValuLine + 1–2 FFUs, LEDs, antistatic curtains, grounding) | **~$7.5K–$13K** | Standalone; no Facilities work |
| Ductless fume hood (Sentry / Air Science / Erlab) | ~$1,000–$8,000 | Backup / interim; optional inside softwall |
| Snorkel arm (each) | ~$850–$2,200 | Pair with canopy or partition |
| Shop-built 2'×2' canopy hood (BYU Facilities) | Included in ~$25K equipment-hookups estimate per Dave | Plus any Phoenix-valve / commissioning |
| Vendor-supplied canopy hood (if needed) | ~$1,500–$5,000 hood + $3,000–$10,000 blower/ducting | Fallback if Facilities can't shop-build |
| Installation / duct runs / balance damper (Facilities) | Folded into ~$25K estimate | Ask Dave to itemize |
| **Plan 1 — Softwall only (cheapest)** | **~$7.5K–$13K** | No Facilities work; fastest to deploy |
| **Plan 2 — Canopy + 2× snorkels (Facilities-integrated)** | **~$25K–$30K Facilities + ~$2K–$4K snorkels** | Shared with glovebox / atomizer hookups |
| **Plan 1 + 2 layered (canopy + snorkels + softwall)** | **~$32K–$43K total** | Only if air sampling shows it's needed |

For comparison, the prior fume-hood route was **~$55K–$90K** depending on whether we moved the old hood or bought a new one, and was ultimately ruled out by BYU liability policy. **Even the fully-layered Plan 1 + 2 comes in well under the cheapest fume-hood option, and softwall alone is roughly an order of magnitude cheaper.**

## Safety Considerations (NFPA 484 / 652 and BYU CHP)

- **Class D extinguisher** within reach of any metal-powder handling (see the [BYU Chemical Hygiene Plan](./byu-engineering-lab-safety-plan-chemical-hygiene-plan-2024.pdf) and [SOP template](./byu-engineering-sop-template.md)).
- Bond and ground canopy hood, duct, snorkel arms, softwall frame, FFU, and the explosion-proof vacuum.
- Do not use water sprinklers in the containment zone for metal fires; confirm with Facilities that the area is on a dry-pipe / exempt zone or has a risk assessment.
- Use antistatic curtain material and antistatic clothing (no synthetic lab coats) for powder transfers.
- Keep the ultrasonic atomizer's exhaust hooked directly to a snorkel or to inside the canopy hood envelope — do not vent particulate into room air.
- Maintain a written SOP (use [`byu-engineering-sop-template.md`](./byu-engineering-sop-template.md)) for each powder handling operation.
- Cross-reference the [BYU Engineering Safety & Health Hazard Checklist](./byu-engineering-safety-and-health-hazard-checklist.pdf) and [Risk Assessment Matrix](./byu-engineering-safety-and-health-risk-assessment-matrix-v2.pdf) when finalizing the install.

## Open Questions for Facilities (Barry Holman / Dave Laws)

- Exact cfm budget available on general exhaust for the canopy hood — confirms whether 2'×2', 3'×3', or 4'×4' is achievable.
- Is a dedicated Phoenix valve required for the canopy hood, or can it share with the glovebox / atomizer hookups?
- Can snorkel arms be added to the same duct run without a separate balance damper?
- Is the canopy hood motor/blower on an explosion-proof circuit, or can it be made so? (NFPA 484 question for fine Al / Mg dust.)
- Can Facilities support grounding taps for softwall frame, FFU, and vacuum in the bench area?
- Would running the room with the existing dehumidifier + canopy-hood makeup air still meet humidity targets, or does a softwall partition help?

## Next Steps

- [ ] Share this document with Dave Laws and Barry Holman ahead of the next Facilities meeting.
- [ ] **Decide between Plan 1 (softwall only, ~$7.5K–$13K, no Facilities work) and Plan 2 (canopy + snorkels, ~$25K–$30K Facilities + snorkels)** — or start with Plan 1 and layer in Plan 2 later. Per the PR discussion, Plan 1 with the Quest 155 dehumidifier mounted *as one of the softwall panels* (not free-standing inside) is currently the favored direction.
- [ ] Overlay the chosen footprint (6'×8' / 8'×8' / 10'×10') on [`cb154-annotated.pdf`](./cb154-annotated.pdf) before buying, using Gage's dimensions from [issue #7 comment](https://github.com/vertical-cloud-lab/byu-vcl/issues/7#issuecomment-3787027938) and the layout discussion on [issue #31](https://github.com/vertical-cloud-lab/byu-vcl/issues/31#issuecomment-4292025463).
- [ ] Confirm Quest 155 panel-mount details: (a) dimensions vs. softwall frame rail opening; (b) whether Quest 155 supports **continuous-fan** mode so the envelope sees airflow when the compressor is idle; (c) intake-out / exhaust-in orientation so the envelope receives dried, MERV-13-filtered air; (d) refrigerant (R-454B, A2L) clearance / NFPA 484 bonding with BYU Facilities.
- [ ] Decide whether the Quest 155's MERV-13 filter + cycling blower is acceptable on its own, or whether to retain at least one HEPA FFU for continuous airflow + true HEPA filtration + negative-pressure maintenance. Default recommendation in this doc: **keep one FFU**; revisit only if a cost-driven reason emerges.
- [ ] Get written quotes from **Terra Universal** (ValuLine 8'×8' with antistatic curtains + 1–2 WhisperFlow FFUs + LED + grounding kit, and ask about panel cut-outs or a door/service panel that can host the Quest 155) and **Cleatech** (8'×8' softwall) to firm up Plan 1 pricing.
- [ ] Ask Dave to itemize the ~$25K equipment-hookups estimate to isolate the canopy-hood + Phoenix-valve portion from the glovebox / atomizer / sink portions (needed to price Plan 2 accurately).
- [ ] Get a written quote for the shop-built canopy hood (sized 2'×2' minimum, 3'×3' ideal) from Facilities, plus duct and blower.
- [ ] Get a quote for a **Nederman / Fume Dog / Cole-Parmer snorkel arm** × 2 (atomizer + weighing bench) for either plan.
- [ ] Loop in Dave L. and Bryant B. on NFPA 484 compliance before committing to a design (static, grounding, extinguishing).
- [ ] Verify scope overlap with [Issue #30 / #75 (glovebox)](https://github.com/vertical-cloud-lab/byu-vcl/issues/75) and [Issue #53 (VLM venting)](https://github.com/vertical-cloud-lab/byu-vcl/issues/53) so all hookups can be bundled in one work order to minimize commissioning / rebalance cost.
- [ ] Confirm with PI whether the softwall partition alone is sufficient for now, or whether a permanent canopy hood is worth funding up front.
