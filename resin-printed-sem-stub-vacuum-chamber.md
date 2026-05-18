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

## 1a. Buy vs. print — the commercial baseline

Before committing to a print, note that the unit in the reference image
appears to be a stock catalog product, not a custom build. A direct
commercial equivalent is the **PELCO® SEM Pin Stub Vacuum Desiccator with
Acrylic Cap** (Ted Pella cat. #16179): blue anodized aluminum base, clear
acrylic lid, brass hose-barb valve, holds 12 × Ø12.7 mm pin stubs — the
same construction visible in the issue photo. Currently listed by Systems
for Research (Canada) at **CAD $456.35** (≈ USD $325–340) at
<https://sfr.ca/products/pelco-sbem-pin-stub-vacuum-desiccator>. A
European-built alternative is the **EM-Tec EM-Storr 81P** (vacuum-grade
aluminum, hardened-glass lid, NBR O-ring, all-metal high-vacuum valve;
19 × Ø12.7 mm pin stubs; Ø80 × 15 mm chamber) from Micro to Nano at
**€495** (≈ USD $530+) at
<https://www.microtonano.com/EM-Tec-Em-Storr-vacuum-EM-sample-storage-transport-shipping-container.php>.

For reference, generic 75–100 mm polycarbonate benchtop vacuum desiccators
(Bel-Art / SP Scienceware and similar) run roughly **$50–150** new, but
without the drilled stub-holder plate.

This memo therefore covers two paths in parallel:

1. **Buy the PELCO #16179** (or EM-Storr 81P) and skip fabrication. Lowest
   risk, fastest path to a working chamber. Recommended unless we
   specifically need a non-standard geometry, port placement, or
   stub-hole pattern that the catalog units don't offer.
2. **Print our own** per the remainder of this document. Worth doing only
   if the catalog units don't fit our workflow, or as a learning exercise
   while waiting for a commercial unit to arrive — the parts savings vs.
   PELCO ($30–70 BOM vs. ~$325) are real but modest given the engineering
   effort involved.

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

## 2a. Desiccant pocket

If we also want to use the chamber for short-term *dry* storage of mounted
stubs between pump-downs (not just a one-shot degassing vessel), we should
reserve room for a small charge of desiccant. The simplest, lowest-risk
option is to drop in a loose indicating silica-gel sachet
(e.g. McMaster 2189K-series, 1–5 g packets, color-changing) — no
geometry change required, and the same trick works in the catalog
PELCO #16179.

If we want to commit to it in the printed body, the cleanest integration
is a shallow annular **well** machined into the floor *outside* the stub
hole pattern:

- Depth ~5–8 mm, width ~10–15 mm, capacity ~5–10 g of beads.
- A printed **snap-in cover plate** with through-holes (or a thin
  stainless-mesh disc retained by a step) keeps the beads from migrating
  into the stub holes or being sucked toward the vacuum port when the
  valve is opened.
- Keep the well clear of the gasket land and of the bulkhead-fitting boss
  so it does not compromise either seal.
- Use **bead-form indicating silica gel**, not loose powder, to avoid
  fines being pulled through the port. Regenerable in a 110–120 °C oven,
  which is well within the post-cure temperature the printed body
  already tolerates.

Avoid molecular sieves or strong deliquescent desiccants (CaCl₂) in the
printed chamber — the former generate heat on adsorption and the latter
can release liquid water that would sit against the resin floor.

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
  resin trapped in voids continues to outgas). Keep the bath short
  (~5–10 min); soaking longer than ~10 min can warp parts and roughen
  surfaces (Hassanpour 2024; Riccio 2021).
- Long, hot post-cure per the resin's datasheet — undercured parts are
  measurably more permeable and softer at the gasket land. A pre-service
  bake of 60–80 °C overnight also drives off absorbed atmospheric water
  (the dominant outgassing species from cured photopolymer resins).
- Optionally seal the inner surface with a thin coat of two-part epoxy or
  cyanoacrylate wicked over the gasket land to close any layer-line porosity.

**Sanity check from the literature:** rough vacuum is *not* the hard part
for SLA resins. Published work measures SLA-printed parts well past the
few-torr requirement:

- Radić et al. 2025 — Formlabs Clear (standard methacrylate) reached
  ~**1.9 × 10⁻⁸ mbar** unbaked and ~**1 × 10⁻⁹ mbar** after a 120 °C bake;
  water dominated the residual gas, with no evidence of heavy polymer
  fragments by RGA.
- AL-Hasni & Santori 2020 — SLA epoxy-style vessels were classified as
  "very tight" at ~1 kPa with leak rates on the order of
  **10⁻⁸–10⁻⁹ Pa·m³·s⁻¹**, and SEM confirmed essentially pore-free walls.
- Gulino et al. 2026 — printed KF-25 flanges in stock Anycubic resin
  reached **10⁻⁵ mbar** on an Edwards Auto 306; a thin Al PVD coating
  brought them up to commercial-flange behavior.

So as long as we get the *seal geometry* right (O-ring land flatness,
bulkhead fitting, no threads in resin), bulk gas permeation through the
printed wall is not expected to be the limiting factor for a few-torr
chamber.

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

### 6a. Ad-hoc "brush UV resin around the fitting and re-cure" sealing

A reasonable suggestion is to brush extra liquid UV resin around the
bulkhead fitting / any threaded interface after it's installed, then
re-cure, to close any leftover gap. This is *plausible* but should be
treated as a touch-up, not the primary seal — the literature on coating
SLA prints with extra resin or thermosetting varnish (Tamburrino 2021;
Dizon 2021) shows it can reduce porosity, but several failure modes apply
specifically to brushed-on, ad-hoc applications:

- **Oxygen inhibition** leaves a tacky, undercured surface layer on
  air-exposed photopolymer; in concave corners around a fitting the UV
  light path is poor and patches of resin may never fully cure
  (Hassanpour 2024). Those patches outgas and creep under vacuum.
- **Polymerization shrinkage** of the freshly applied layer can open a
  gap at the interface with the already-cured substrate instead of
  closing one.
- **Resin accumulation in corners** is explicitly flagged as a dimensional
  issue (Tamburrino 2021); a thick fillet around the bulkhead can crack
  on thermal cycling or when the fitting is re-torqued.
- **Brittleness / delamination** of the thin add-on layer on a stiff
  substrate, especially under repeated vent/pump cycles.

**If we do this anyway:** keep the bead thin, cure under a UV lamp with
the part rotated so light reaches every surface (or do it under an inert
purge to defeat oxygen inhibition), and verify by leak test rather than
by inspection. **Preferred alternative for sealing around the fitting:**
a commercial vacuum sealant such as **Vacseal** or Loctite **Torr Seal**
(both well-characterized for HV use), or simply rely on the elastomeric
O-rings on the bulkhead fitting itself — that's why the fitting is
specified as bulkhead-with-O-ring rather than threaded-into-resin in §6
above.

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
| Indicating silica-gel sachet (optional, see §2a)            | 1–2 | McMaster 2189K-series, 1–5 g color-changing     | $1–$3     |
| **Estimated total parts cost**                              |     |                                                 | **~$30–$70** |

For comparison, the catalog equivalent — **PELCO #16179** at
~CAD $456 (≈ USD $325–340) — is roughly 5–10× the parts cost of a
printed unit but ships ready to use. See §1a for the buy-vs-print
trade-off.

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
  One study of an SLA methacrylate resin in 10 vol% acetone reported
  ~4.4% swelling, ~45% tensile-strength loss, and ~46% modulus loss after
  12 weeks (Mahmud 2025). Brief splashes are tolerable if wiped
  immediately, but do not soak the chamber and avoid using it as the
  primary container for acetone-intensive workflows. Ethanol, methanol,
  and IPA in short incidental contact are acceptable; IPA washes during
  post-processing should be kept under ~10 min to avoid warping.
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

0. **Decide buy vs. print first** (see §1a). The default recommendation is
   to buy PELCO #16179 unless we need a non-standard geometry — the
   ~$325 catalog unit is hard to beat for the engineering effort
   involved. The remaining steps apply only if we choose to print.
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
