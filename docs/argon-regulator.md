# Argon regulator for the rePowder atomizer

The regulator on the atomizer's argon cylinder is borrowed. It's a Harris 9296
([#289](https://github.com/vertical-cloud-lab/byu-vcl/issues/289)). This page sets out what a
replacement has to do, what to buy, and where the information came from, so that the next
purchase doesn't repeat the Amazon one.

## Recommendation

Buy a **Harris 9296SS-250-580** (Harris item 3302689), **$553.19 at
[Weldingmart](https://weldingmart.com/products/harris-9296ss-250-580-two-stage-argon-helium-nitrogen-regulator-3302689)**
(listed 2026-10-20). Also buy a **1/4" NPT male × 6 mm push-to-connect** fitting for the outlet.

It's the borrowed model with a stainless-steel diaphragm instead of neoprene: same body, range,
outlet and flow rating. Buying the identical
**9296-250-580** (item 3302609, $516.00 at
[Weldingmart](https://weldingmart.com/products/harris-9296-250-580-general-purpose-two-stage-argon-helium-nitrogen-regulator-3302609))
is also fine. Steer clear of the 125 psi versions (see [below](#what-to-buy)).

## What it has to do

| Requirement | Value | Source |
| --- | --- | --- |
| Gas | Argon, 5N (99.999 %) | [9/17 install call](meetings/2026-09-17-repowder-install/transcript.md) |
| Delivery pressure | **8 bar (116 psi) at the machine, adjustable.** Bartosz asked for a 0–10 bar regulator, not a welding regulator: those are "usually set to three bars and you can only set the flow", and the machine's pneumatics need the higher pressure | 9/17 call, 15:42 and 17:05 |
| Flow | Up to 100 L/min (212 SCFH), only while purging | Bartosz's facility list, [#41](https://github.com/vertical-cloud-lab/byu-vcl/issues/41#issuecomment-4225003786) |
| Inlet | CGA 580, the standard US argon cylinder valve | |
| Outlet | Into the 6/4 mm push-fit line to the T on the back of the machine, whose two 6/4 mm ports feed the furnace and the chamber-fill valve | 9/17 call, 17:40 |
| Cylinders | One regulator per cylinder, no manifold. The booth may hold at most two argon or nitrogen cylinders, not manifolded, each on its own equipment, and no dewar. Under that limit no oxygen detection is needed | Bryant Brown, 8 Oct 2026 ([PR #271](https://github.com/vertical-cloud-lab/byu-vcl/pull/271)) |

In practice that means:

- **Two-stage.** Outlet pressure stays put as the cylinder drains. A single-stage regulator's
  outlet creeps up as the cylinder empties, so it has to be reset.
- **A delivery range that reaches 116 psi with room to spare.** A 0–125 psi model would have to
  run at the very top of its spring.
- **CGA 580 inlet.**
- **Preferably a stainless-steel diaphragm,** for 5N argon. Neoprene lets a little air and
  moisture through into the gas. The plastic line to the machine probably lets in more than the
  diaphragm does, so this matters less than the first three points.

## The borrowed regulator

From the photos on #289:

- **Model:** Harris 9296 "Multi-Stage" (Harris's name for its two-stage design), marked for
  Ar/He/N2 service. "CGA E-4" on the label is the Compressed Gas Association's standard for gas
  pressure regulators, not a fitting.
- **Gauges:** 0–4000 psi on the inlet (USG BU-2581-AM). 0–400 psi on the delivery side (USG
  CU-2581-HF), reading about 800 kPa, i.e. the 8 bar the machine needs.
- **Outlet:** a push-to-connect fitting screwed straight into the low-pressure port.

That matches the **9296-250-580**. It's the only argon version that ships with a 0–400 psi
delivery gauge and a 1/4" NPT outlet. The 125 psi version has a 0–150 psi gauge and a 5/8"-18
outlet. The label says "9296", not "9296SS", so it most likely has the neoprene diaphragm. The
delivery-pressure number cut off at the end of the label should read 250 psig.

## What to buy

Both 250 psi versions share the following, from Weldingmart's spec tables:

- Two-stage, brass body
- CGA 580 inlet, 3000 psig maximum inlet
- 0–250 psig delivery range, with a 0–400 psi delivery gauge
- 1/4" NPT female outlet
- Cv 0.15
- Internal relief valve
- Outlet changes 0.04 psi per 100 psi drop in cylinder pressure
- 7-year warranty

| Model | Harris item | Diaphragm | Weldingmart, 2026-10-20 |
| --- | --- | --- | --- |
| **9296SS-250-580** (recommended) | 3302689 | stainless steel | **$553.19** |
| 9296-250-580 (same as the borrowed one) | 3302609 | neoprene | $516.00 |
| 9296-125-580 / 9296SS-125-580 (not recommended) | 3302608 / 3302688 | neoprene / stainless | $448.36 / $500.75 |

**Why not the 125 psi versions.** 116 psi is 93 % of their range. Their outlet is also a
5/8"-18 RH inert-gas hose thread rather than 1/4" NPT, which needs another adapter before a push
fitting
([125](https://weldingmart.com/products/harris-9296-125-580-general-purpose-two-stage-argon-helium-nitrogen-regulator-3302608),
[125 SS](https://weldingmart.com/products/harris-9296ss-125-580-general-purpose-ss-diaphragm-two-stage-argon-heliumnitrogen-regulator-3302688)).

**Flow.** Cv 0.15 is comfortably enough for the 212 SCFH purge peak. A rough choked-flow estimate
(q ≈ 640 · Cv · P₁ / √(G·T), argon G = 1.38, 530 °R) gives about 900–1,300 SCFH if the second
stage is fed at 250–350 psig, which is 4–6 times the peak. It's also the same flow rating as the
regulator on the cylinder now.

**Other places to get it.**

- **Airgas** lists the plain version as
  [HCL3302609](https://www.airgas.com/product/Gas-Equipment/Regulators/Specialty-Gas-Regulators/p/HCL3302609),
  but doesn't sell it online, and the price is hidden.
- **Locally:** Nick suggested Norco for a Victor two-stage regulator; the contact is in
  [#41](https://github.com/vertical-cloud-lab/byu-vcl/issues/41#issuecomment-4284403253).
  Ask them for the 9296SS-250-580 or an equivalent: a two-stage regulator with a CGA 580 inlet
  that reaches at least 150 psi and has a stainless diaphragm.
- **Nick**, who orders the argon, may be able to add it to a gas order.

## Outlet fitting

- **What to buy:** a straight connector, 1/4" NPT male × **6 mm** push-to-connect, rated for
  at least 150 psi. One example is Tameson's
  [F25TN](https://tameson.com/products/f25tn-6mm-x-1-4inch-npt-plug-in-fitting-with-male-threads-brass-pa-66-nbr-2-pieces),
  which has a brass thread, a PA 66 body and NBR seals.
- **Don't use a 1/4" tube fitting.** The machine's tube is metric 6/4 mm, and a 1/4" (6.35 mm)
  fitting won't grip 6 mm tube reliably.
- **Fitting it:** seal the NPT thread with PTFE tape or paste unless it comes pre-coated. Keep
  tape off the first thread so shreds can't get into the regulator. Leak-check with Snoop at
  8 bar.
- **Before returning the borrowed regulator:** check whose push fitting is in its outlet now.
  On the 9/17 call, Kevin was to supply the push fittings for the compressed air, so this one may
  be ours as well. If it is, move it to the new regulator.

## The Amazon regulator

Nothing in this repo records which regulator was bought on Amazon or what was wrong with it.
The issues, PRs, comments, meeting transcripts and training-video transcripts were all searched
for it. The only trace is a 26 Sept comment on
[PR #232](https://github.com/vertical-cloud-lab/byu-vcl/pull/232#issuecomment-5845793220) asking
whether "that regulator came in yet". Most Amazon "argon regulators" are welding flowmeter
regulators. These are preset to about 50 psi, and only the flow can be adjusted, often to no more
than about 60 SCFH (for example the Flame Tech
[100-FL-AR-60-580](https://store.cyberweld.com/products/flame-tech-argon-flowmeter-regulator-100-fl-ar-60-580)).
That is the kind Bartosz warned against. If anyone still has the order or listing, add the link
and what went wrong here.
