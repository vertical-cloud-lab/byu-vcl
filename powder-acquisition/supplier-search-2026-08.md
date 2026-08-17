# Feedstock Supplier Search — August 2026

**Status:** DRAFT (being compiled 2026-08-17; sections below are filled from live web research
plus residential-IP page verification via the lab's Tailscale-connected Raspberry Pi.)

## 0. Why this document exists

The July 2026 plan (see `purchase-quantity-model.md` and
`purity-and-particle-size-recommendations.md`) assumed MSE Supplies and American Elements as
primary sources. Both have failed:

- **MSE Supplies** (after ~1 month of quoting back-and-forth): *cannot supply any of the
  requested elemental powders* — "importation restrictions" and shortages across all of their
  upstream suppliers.
- **American Elements**: unresponsive to a month of emails/calls; anecdotally uninterested in
  small orders.

This document re-sources the entire shopping list with an emphasis on **US-domestic producers
and stockists** and **EU/UK/JP/CA-origin material with US distribution**, because the failure
mode above is almost certainly China-supply-chain exposure (see §2).

## 1. The shopping list being sourced (from issue #161, 2026-08-14)

All items must be **powder/granules ≤300 µm (target 150–300 µm, ≈ −50+100 mesh)** for the
automated auger dosing system; Ar-glovebox storage with brief air exposure during transfers.

| Item | Quantity | Notes |
| --- | --- | --- |
| Al 99.99% | 2 kg | matrix baseline |
| Mn 99.9%, Mg 99.99%, Si 99.9% | 100 g each | Mg 4N powder availability is a known problem (§3) |
| Cr, Cu 99.9% | 100 g each | |
| Zn 99.9% | 100 g | |
| Ni, Fe, Sn 99.9% | 100 g each | |
| Ti 99.99% | 200 g | 4N Ti **powder** is effectively not a stocked product (§3) |
| Al-20Ce master | 250 g | |
| Al-2Sc master | 250 g | |
| Al-10Zr master | 300 g | |
| Al-10Er master | 100 g | |
| Al-10Li master | 100 g | elemental Li ruled out (pyrophoric) |

## 2. The 2025–26 import-restriction backdrop

(to be filled — verified summary with sources)

## 3. Reality checks on the spec

- **Ti "99.99%"**: 4N titanium powder is essentially unobtainable as a stocked product;
  commercial cuts are 99.5 % (HDH) and 99.9 % (spherical/gas-atomized). Verified live prices
  (2026-08-17, Fisher Scientific list, residential-IP fetch):
  - Thermo Scientific Chemicals **Ti powder −60+100 mesh (149–250 µm), 99.5 %**, 100 g,
    cat. AA4310522 — **$80.40** — in the exact target size band.
  - Thermo Scientific Chemicals **Ti powder spherical −150 mesh, 99.9 %**, 100 g,
    cat. AA4154522 — **$113.00** — better flow + purity, finer cut.
  Recommendation: buy the 99.9 % spherical (dissolution chemistry cares about O/Fe, not the
  fourth nine) or the −60+100 mesh 99.5 % if the coarser band matters more than 0.4 %.
- **Mg "99.99%"**: 4N Mg powder in 150–300 µm is not a stocked product from major houses;
  ESPI does list **"Magnesium Granules 4N"** (quote for granule size — must confirm ≤300 µm
  or ask for a custom sieve cut). Fallback remains coarse 99.8–99.9 % atomized Mg
  (−50+100 mesh) per the July recommendation.
- **Al 99.99% powder, 150–300 µm**: not a normal catalog item either — 4N Al is sold as
  shot/granule/ingot; atomized Al powder is typically 99.7–99.9 %. Two routes: (a) accept
  99.7–99.9 % atomized coarse cut off the shelf, (b) toll-atomize 4N ingot into the exact cut
  (Valimet — §5).

## 4. Per-element supplier matrix

(to be filled from the four research sweeps + price verification)

## 5. Valimet (suggested by @sgbaird)

Verified from valimet.com (2026-08-17): spherical aluminum and Al-alloy powders, standard and
**custom particle size distributions**, and **toll atomization of custom alloys** (defense/
aerospace qualified). This makes Valimet a candidate for the single highest-leverage ask:
*toll-atomize 4N Al (or even pre-alloyed compositions) directly into a 150–300 µm cut.*

- Phone: **+1 209 444 1600**
- Email: **sales@valimet.com**
- RFQ form: valimet.com/request-quote
- Address: 431 Sperry Road, Stockton, CA 95206

Questions for the call: minimum lot for toll atomization; can they atomize customer-supplied
4N ingot; standard purity of their H-series spherical Al (typ. 99.7 %); coarsest standard cut
(H-95 / −50+100 mesh availability); price/lead for a 2–5 kg spherical Al order; whether they
can refer a distributor for <10 kg lots.

## 6. Small-lot generalist houses (status as of 2026-08-17)

| House | Location | Pricing | Verified status |
| --- | --- | --- | --- |
| Thermo Scientific Chemicals (former Alfa Aesar) via Fisher Scientific | Ward Hill, MA stock | **listed prices, university punch-out** | product pages live + priced (Pi-verified); search pages bot-gated |
| ESPI Metals | Ashland, OR | now **quote-only** (new Magento shop) | stocks confirmed for: Mg granules 4N, Mn powder −100 mesh 3N, Cr powder −100 mesh 3N+ (also −50 mesh 2N8, −60 5N), Si powder (−150+325 2N5, −325 3N), Sc powder −40 mesh 3N (canned), Er powder −40 mesh 3N (can/ampoule) |
| Atlantic Equipment Engineers / Micron Metals | Upper Saddle River, NJ | quote-only (RFQ per product page) | site live, R&D specialty, custom mesh cuts |
| Sigma-Aldrich / MilliporeSigma | — | listed prices | site unreachable by automation (aggressive bot-blocking even residentially) — check manually in a browser |
| GoodFellow USA | Pittsburgh, PA | listed prices for many items | (to be filled) |
| Belmont Metals | Brooklyn, NY | quote | (to be filled) |
| Reade Advanced Materials | Riverside, RI | quote | (to be filled) |

## 7. RFQ-ready ask (copy-paste for supplier calls/emails)

> We are a university additive-manufacturing lab buying research quantities of elemental
> feedstock for melt atomization. All items must be **powder or granules, 150–300 µm
> (−50+100 mesh preferred; ≤300 µm hard max)**, packed under argon or vacuum, with a
> certificate of analysis reporting **O content plus Fe/Si (metals basis purity)**.
> Quantities: Al 99.99 % — 2 kg; Mn 99.9 %, Mg ≥99.9 % (4N preferred), Si 99.9 % — 100 g ea.;
> Cr, Cu 99.9 % — 100 g ea.; Zn 99.9 % — 100 g; Ni, Fe, Sn 99.9 % — 100 g ea.; Ti ≥99.5 %
> (99.9 % preferred) — 200 g. Master alloys (crushed/granulated to ≤300 µm): Al-10Zr — 300 g;
> Al-2Sc — 250 g; Al-20Ce — 250 g; Al-10Er — 100 g; Al-10Li — 100 g (Ar-sealed).
> Please quote price, lead time, country of origin, and any hazmat shipping fees
> (Ti/Mg powders are DOT class 4.1).

## 8. Verification log

| Check | Route | Result |
| --- | --- | --- |
| Fisher AA4310522 (Ti −60+100 mesh 99.5 %, 100 g) | Pi (residential IP) | live, **$80.40** |
| Fisher AA4154522 (Ti spherical −150 mesh 99.9 %, 100 g) | Pi | live, **$113.00** list |
| ESPI shop catalog (15 element pages) | Pi | live; quote-only; availability as §6 |
| Valimet capabilities/contact | runner fetch | live; toll atomization confirmed |
| Fisher search endpoint | Pi | 403 (bot-gated) — use direct product URLs |
| Sigma-Aldrich | Pi | connection refused — manual browser only |
| micronmetals.com (AEE) | Pi | live; quote-based |
