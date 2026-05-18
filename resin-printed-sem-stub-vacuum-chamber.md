# Resin-Printed Vacuum Chamber for SEM Stubs — Feasibility Notes

This document captures a first-pass feasibility analysis for fabricating a small
vacuum chamber for SEM stub preparation by resin (MSLA / SLA) 3D printing
instead of buying a commercial unit. It follows up on the aside in
[#110 (comment)](https://github.com/vertical-cloud-lab/byu-vcl/issues/110#issuecomment-4481621131)
and the parent issue
[#111](https://github.com/vertical-cloud-lab/byu-vcl/issues/111).

> Assume we'd still use a gasket, probably from McMaster-Carr, and that we'd
> probably still use a commercial valve like the one shown in the image above,
> but we could probably get a pretty good airtight connection both between the
> lid and the base as well as the valve and the base.

## 1. Intended use

The reference unit in the issue image is a benchtop "mini" vacuum chamber used
to pull a vacuum over SEM mounting stubs — typically to:

- Degas / impregnate epoxy or Bakelite mounts (pull air out of pores so resin
  fully wets the sample) before polishing.
- Outgas conductive paint (carbon / silver) on mounted samples prior to SEM
  loading.
- Hold a small batch of standard ½" (12.7 mm) aluminum SEM stubs vertically in
  a drilled plate so they can be worked on or stored under reduced pressure.

This is *not* a high-vacuum chamber. The duty cycle is short pumps to a rough
vacuum (a few torr, achievable with a small diaphragm or rotary-vane pump),
held for minutes, then vented to atmosphere. That requirement envelope is what
makes a printed-resin body plausible — we are fighting ~1 atm of crush load and
permeation/leak rates, not UHV outgassing.

## 2. Dimensional targets (from the reference photo)

Approximate, to be confirmed against the actual unit / SEM stub count we
expect to process:

| Feature                       | Target                                  |
| ----------------------------- | --------------------------------------- |
| Internal usable diameter      | ~75–90 mm                               |
| Internal height               | ~20–25 mm (clear stubs + a little head) |
| Stub-holder hole diameter     | 12.8 mm (slip fit on a ½" SEM stub pin) |
| Stub-holder hole count        | 10–14 (matches reference, adjust to need) |
| Wall thickness (printed body) | ≥ 6 mm (see §5)                         |
| Gasket groove (O-ring)        | Sized per Parker O-ring handbook for chosen cord |
| Lid                           | Cast acrylic disc, ~6–10 mm thick, ~10–15 mm larger than seal OD |

The lid in the reference image is a clear cast-acrylic disc that simply sits on
top of the gasketed rim; atmospheric pressure clamps it down once a vacuum is
drawn. We should keep that arrangement — it lets the user see inside and
avoids printing the most sealing-critical surface.

## 3. Resin selection

The printed part is the **base / stub holder**, not the lid. Requirements:

- Low porosity after cure (closed-cell, not microporous).
- Dimensionally stable at room temperature.
- Tolerates incidental contact with ethanol / methanol / acetone wipes used
  during sample prep (acetone is the worst offender; brief contact only).
- Reasonable stiffness so the gasket land does not deform under atmospheric
  load.

Suitable candidates (in rough order of preference for this duty):

1. **Formlabs Rigid 10K** or **Rigid 4000** — glass-filled, very stiff, low
   creep, good dimensional stability. Best chance of holding a flat gasket
   land. More brittle; handle with care around the hose-barb fitting.
2. **Siraya Tech Blu / Sculpt Ultra** or equivalent "tough" engineering resin
   — cheaper, decent stiffness, widely available for desktop MSLA.
3. **Standard / "ABS-like" resin** — acceptable for a proof-of-concept print
   but expect more creep at the gasket land over time.

Avoid flexible / "elastic" resins and resins marketed as "draft" — both will
either leak through deformation or are too porous after cure.

**Post-processing matters more than resin choice for leak-tightness:**

- IPA wash to fully remove uncured resin from internal cavities (uncured
  resin trapped in voids continues to outgas).
- Long, hot post-cure per the resin's datasheet — undercured parts are
  measurably more permeable and softer at the gasket land.
- Optionally seal the inner surface with a thin coat of two-part epoxy or
  cyanoacrylate wicked over the gasket land to close any layer-line porosity.

## 4. Gasket

Use a stock O-ring rather than a flat sheet gasket — O-rings seal far better
on imperfect (printed) surfaces because the elastomer extrudes into surface
defects.

- **Material:** Buna-N (NBR) is the default and cheapest. Viton (FKM) is
  worth the upcharge if we expect repeated solvent contact.
- **Source:** McMaster-Carr O-rings, e.g. the 9452K series (Buna-N) or 9464K
  series (Viton), sized for the chamber rim.
- **Groove:** Design a simple **rectangular groove** per the Parker O-Ring
  Handbook (ORD 5700) recommendations for static face seals — typically
  groove width ≈ 1.30 × cord, groove depth giving ~25% squeeze on the cord.
  A 2.5–3.0 mm cord (e.g. AS568 −1XX series at the appropriate ID) is a
  reasonable starting point for this diameter. (Avoid dovetail/undercut
  grooves here — they retain the O-ring better but are awkward to print
  face-up without supports, which is exactly the orientation we need for a
  clean sealing surface — see §5.)

The gasket groove should be printed *facing up* (see §5) so the sealing
surface comes off the resin tank free of suction-cup marks and supports.

## 5. Print orientation and structural notes

- Orient the part with the **gasket land facing up** (away from the build
  plate) so it prints without support contact. This is the single biggest
  factor for getting a usable sealing surface straight off the printer.
- Keep walls **≥ 6 mm** and add a generous radius (≥ 3 mm) between the wall
  and the floor. Atmospheric load on a ~85 mm ID lid is roughly
  π·(0.0425 m)² · 101 kPa ≈ **575 N** (~130 lbf). The base / rim has to
  carry that without flexing enough to break the seal.
- Add a small (~1° per side) external draft on the OD so the part releases
  cleanly from MSLA suction forces.
- Avoid fully enclosed internal voids (resin traps) — every cavity needs a
  drain hole that can be plugged later with a set screw + O-ring or epoxy.

## 6. Vacuum valve / port

Plan to reuse a commercial valve assembly like the one in the issue photo
(a small ball valve with an integrated hose barb), rather than printing
threaded valve features. Threads in resin are weak and a poor sealing
surface.

Recommended approach:

- Print a **boss** on the base wall with a stepped through-hole sized for a
  bulkhead fitting.
- Use a **brass or stainless bulkhead hose-barb fitting** (e.g. McMaster
  5346K-series brass barbed-tube bulkhead fittings) with O-ring face seals
  on both sides of the printed wall. The seal is then elastomer-to-resin on
  a flat printed face, *not* threads-in-resin.
- The user-operated shutoff valve and any pump tubing live on the *outside*
  of the bulkhead fitting, where loads are taken by metal hardware.

A 1/4" or 3/8" hose barb is sized appropriately for a small diaphragm pump.

## 7. Indicative bill of materials

| Item                                                        | Qty | Notes / source                                  | Est. cost |
| ----------------------------------------------------------- | --- | ----------------------------------------------- | --------- |
| Printed base + stub holder (engineering resin)              | 1   | ~30–60 mL resin per print                        | $2–$6     |
| Cast acrylic lid disc, ~100 mm × 8 mm                       | 1   | McMaster 8560K (cut to size) or local plastics  | $5–$15    |
| O-ring, Buna-N or Viton, sized to rim                       | 1–2 | McMaster 9452K / 9464K series                   | $1–$5     |
| Bulkhead hose-barb fitting + O-rings                        | 1   | McMaster 5346K-series brass barbed bulkhead     | $8–$15    |
| Mini ball valve, hose-barb to hose-barb                     | 1   | Commercial (reuse design in issue photo)        | $10–$25   |
| Vacuum tubing to pump                                       | —   | Existing                                        | —         |
| Vacuum grease (thin film on O-ring during install)          | 1   | Existing / Dow Corning High-Vacuum Grease       | —         |
| **Estimated total parts cost**                              |     |                                                 | **~$30–$70** |

For comparison, a commercial benchtop SEM-stub vacuum chamber typically runs
several hundred dollars, so the printed approach is worth pursuing if a first
prototype seals adequately.

## 8. Risks, limitations, and what could go wrong

- **Resin porosity / permeation** — the leading failure mode. Mitigation:
  pick a stiff engineering resin, long hot post-cure, optional epoxy wash
  coat on internal surfaces. Validate by pumping the assembled chamber down,
  closing the valve, and recording the pressure rise over time before
  putting samples in it.
- **Creep at the gasket land** — resins are viscoelastic; the rim under the
  O-ring can take a permanent set after many cycles. Inspect the gasket
  land periodically for a visible impression deeper than the design
  squeeze, and replace the base if the chamber starts losing vacuum
  faster than baseline. Treat the printed base as a consumable and keep a
  spare print on hand; we do not yet have data to quote a specific cycle
  life.
- **Solvent attack** — acetone in particular softens most photopolymers.
  Wipe spills immediately; do not soak.
- **Brittleness** — Rigid 10K and similar glass-filled resins are stiff but
  shatter on impact. Treat the chamber as glassware.
- **Not for hot work** — do not use this chamber for anything involving
  heating, sputter coating, or volatile solvents under vacuum without a
  separate hazard review.
- **Not for use with hazardous powders without further review** —
  silicon and AlSi10Mg powders kept in the lab (see the SDS files in this
  repo) should not be cycled in a printed chamber until we are confident the
  body will not crack and release material.

## 9. Suggested next steps

1. Measure the existing reference unit (if accessible) or confirm target
   stub count to lock down the OD / ID / hole pattern.
2. Model the base in CAD with the gasket groove sized for a specific stock
   O-ring (commit the source file to this repo when ready).
3. Order the O-ring and bulkhead fitting from McMaster so the printed groove
   and boss can be dimensioned to a real part.
4. Print a first article in a stiff engineering resin, hot post-cure, and
   leak-test (pump down, close valve, time pressure rise).
5. If leak-tight enough for the intended duty, document the final part as an
   SOP-attached drawing using `byu-engineering-sop-template.md`.

This document is intentionally a design memo, not a finalized SOP — once a
working prototype exists, the operating procedure (pump model, pressure
limits, PPE, etc.) should be written up against the standard BYU SOP
template in this repo.
