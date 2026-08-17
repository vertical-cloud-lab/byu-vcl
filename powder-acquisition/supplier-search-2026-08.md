# Feedstock Supplier Search — August 2026

**Compiled 2026-08-17** from four parallel live-web research sweeps plus direct product-page
verification routed through the lab's Tailscale-connected Raspberry Pi (residential IP —
Fisher/Thermo product pages price-verified this way; datacenter IPs get 403s).
Suppliers were **not** contacted; everything below is desk research to make the calls/POs fast.

## 0. Why this document exists

The July 2026 plan (see `purchase-quantity-model.md` and
`purity-and-particle-size-recommendations.md`) assumed MSE Supplies and American Elements as
primary sources. Both have failed:

- **MSE Supplies** (~1 month of quoting): *cannot supply any of the requested elemental
  powders* — "importation restrictions" and shortages across all upstream suppliers.
- **American Elements**: unresponsive to a month of emails/calls.

Both are storefronts over largely China-origin material. §2 explains why that channel broke in
2025–26 and which of our elements are exposed. This document re-sources the entire list around
**US-domestic producers/stockists** and **EU/CA-origin material**, with verified prices where
they exist and RFQ contacts where they don't.

## 1. The shopping list being sourced (issue #161 chart, 2026-08-14)

All items must be **powder/granules ≤300 µm (target 150–300 µm ≈ −50+100 mesh)** for automated
auger dosing; Ar-glovebox storage with brief air exposure during transfers.

| Item | Quantity | Item | Quantity |
| --- | --- | --- | --- |
| Al 99.99% | 2 kg | Ti 99.99% | 200 g |
| Mn 99.9% | 100 g | Al-20Ce | 250 g |
| Mg 99.99% | 100 g | Al-2Sc | 250 g |
| Si 99.9% | 100 g | Al-10Zr | 300 g |
| Cr 99.9% | 100 g | Al-10Er | 100 g |
| Cu 99.9% | 100 g | Al-10Li | 100 g |
| Zn 99.9% | 100 g | | |
| Ni, Fe, Sn 99.9% | 100 g each | | |

**Mesh ↔ µm quick reference:** −50 = ≤297 µm · −50+100 = 149–297 · −60+100 = 149–250 ·
−100 = ≤149 · −100+325 = 44–149 · −140+325 = 44–105 · −150 = ≤104 · −325 = ≤44 (violates the
no-fines rule).

## 2. The 2025–26 import-restriction backdrop (why MSE went dark)

Verified as of 2026-08-17; this is the stack that killed small-parcel Chinese powder resale:

1. **China MOFCOM rare-earth export controls.** April 4 2025: Sm, Gd, Tb, Dy, Lu, **Sc**, Y
   put under dual-use export licensing ([CSET translation of MOFCOM 2025 No. 61](https://cset.georgetown.edu/publication/mofcom-notice-2025-61/)) —
   **never suspended, still in force**. October 9 2025: expansion added Ho, **Er**, Tm, Eu, Yb
   plus extraterritorial rules ([Squire Patton Boggs](https://www.squirepattonboggs.com/), [Al Jazeera 2025-10-10](https://www.aljazeera.com/));
   after the Trump–Xi truce these October measures are **suspended only until 2026-11-10**
   ([Pillsbury](https://www.pillsburylaw.com/en/news-and-insights/china-suspends-export-controls-certain-critical-minerals-related-items.html)).
2. **Other Chinese metal controls:** W, Te, Bi, Mo, In licensing since Feb 2025
   ([Xinhua](http://english.news.cn/20250204/cb07a7cd42a94ba3b4ed44cbcdecd9e4/c.html)); Ga/Ge/Sb US-export
   ban Dec 2024, suspended Nov 2025 → **until 2026-11-27** ([CNBC](https://www.cnbc.com/2025/11/09/china-suspends-ban-on-exports-of-gallium-germanium-antimony-to-us.html)).
   None of these five are on our list, but they signal how fast this regime moves.
3. **US Section 232 aluminum tariff at 50%** since 2025-06-04 ([White & Case](https://www.whitecase.com/insight-alert/trump-administration-increases-steel-and-aluminum-section-232-tariffs-50-and-narrows)) —
   applies to the aluminum content of imported unwrought Al (incl. master-alloy waffle/ingot).
4. **China tariff stack** as of Aug 2026 ≈ 30–33% blended (MFN + §301 + IEEPA 10% + reciprocal
   10%; higher reciprocal rate suspended until **2026-11-10**).
5. **De minimis eliminated for all countries** since 2025-08-29 ([EO 14324 / White & Case](https://www.whitecase.com/insight-alert/united-states-suspend-customs-de-minimis-entry-most-shipments-august-29-2025)) —
   every small parcel now needs formal customs entry. This alone breaks the $100–500 powder
   parcel model MSE-style resellers ran on.

**Exposure ranking for our elements:**

- **Sc — highest.** License-controlled by China since Apr 2025 (~85%+ of refined supply);
  2026 global deficit. Route: AMG (US), Rio Tinto Element North 21 (Quebec), KBM/Treibacher (EU).
- **Er — high, with a deadline.** Oct-2025 controls suspended only to **2026-11-10**; Al-Er
  masters are essentially 100% China-origin today. Route: KBM custom AlEr (EU), Ames Lab MPC Er
  metal (US), or — if Chinese material is used at all — take delivery well before Nov 2026.
- **Moderate (concentration/tariff, no licensing):** Ce (China dominates RE refining; but not
  controlled), Mg (China ~85% of primary; US Magnesium in Rowley UT is permanently gone —
  Chapter 11 Sept 2025, site bought by the State of Utah Jan 2026 for Great Salt Lake
  restoration), electrolytic Mn (~90%+ China; US stocks are screened imports — buy early).
- **Low:** Zr, Li (as Al-masters from US/EU), Cr (France/Germany aluminothermic — DCX/GfE),
  Ti (US HDH + Canadian spherical exist), Cu, Zn, Sn, Fe, Ni, Si, Al (domestic chains intact).

## 3. Reality checks on the spec (please amend the chart)

1. **Ti 99.99% → amend to 99.5–99.9%.** 4N Ti *powder* is not a stocked product anywhere
   (4N Ti exists as crystal bar; powdering it would degrade it via O pickup). Stocked reality:
   99.5% HDH angular and 99.9% spherical. Verified prices in §5.
2. **Mg 99.99% → amend to 99.8–99.9% powder** (or chase ESPI's quote-only "Magnesium Granules
   4N", stock K3141 — granule size unpublished and probably mm-scale evaporation granules, not
   a mesh powder — verify on quote). 4N Mg powder is otherwise nonexistent; Edison literature
   only supports ≥99.9% anyway.
3. **Al 99.99% powder in 150–300 µm → does not exist off the shelf.** 4N Al is sold as
   shot/granules/ingot; atomized Al powder tops out at 99.7–99.8% in coarse cuts
   (Toyal's U-series hits 99.996% but only D50 ≤ 60 µm, i.e., fines). Options: (a) accept
   99.7% in the exact cut (AEE AL-111), (b) Valimet H-95 (99.7%, 75–177 µm, zero fines),
   (c) **toll-atomize purchased 4N ingot** (Valimet Special Alloys Group / Toyal RFQ), or
   (d) Toyal U-series 99.996% accepting the fines tradeoff.
4. **Al-10Li → consider re-speccing to Al-5Li, 200 g.** Western standard grades are 2–5% Li
   (KBM: AlLi2/AlLi5; Belmont: Al-5% Li). 200 g of Al-5Li delivers the same 10 g Li and is
   quotable from stock US/EU producers; "Al-10Li" is a rare bird.
5. **Al-20Ce caveat:** KBM's standard product is **AlCe(MM)10 — mischmetal**-based (Ce-rich
   with La/Nd/Pr). If the chemistry needs *binary* Al-Ce, say so explicitly on RFQs (custom US
   melt from Ce metal is the clean route).
6. **Master alloys do not exist as ≤300 µm granules off the shelf** — standard forms are
   waffle/ingot/rod. They are brittle intermetallic-rich alloys and crush well; "cast + crush +
   screen to 150–300 µm" is a routine custom ask. Kymera/Reading Alloys (alloy + granulation
   in-house) and Belmont Metals (stocks "30–60 mesh granular" ≈ 250–600 µm and shot "for
   continuous feeding systems") are the two US doors for that.

## 4. TL;DR buy plan

Prices **verified 2026-08-17 via residential-IP fetch of Fisher/Thermo product pages** unless
marked (q) = quote-only. Fisher list prices; university punch-out usually beats list.

| Item | Primary buy | Verified price | Backup |
| --- | --- | --- | --- |
| Al 2 kg | AEE/Micron Metals **AL-111** atomized Al, 99.7%, **−50+100 mesh (exact cut)**, $25/lb (1–2 lb), $18.75/lb (3–10 lb) → ~5 lb ≈ **$94** + hazmat freight | listed on site | Valimet H-95 (q) · Fisher AA0001022 −40+325 99.8% 100 g **$29.35** (bridge qty) · toll-atomized 4N (q) |
| Mg 100 g | Fisher **AA0086930** Mg −20+100 mesh 99.8%, 250 g, **$101.40** → sieve at 300 µm | ✔ | Fisher Chemical M7100 40–80 mesh 100 g ~$122.75 (Cole-Parmer) · Luxfer Magtech custom −50+100 atomized (q) · ESPI 4N granules (q) |
| Si 100 g | Fisher **AA0031122** Si −100 mesh 99.9%, 100 g, **$119.00** → +325 sieve to strip fines | ✔ | Chemsavers 5N **−50+100 mesh (exact cut)** 250 g **$405** free ship · Alfa 5N −100+325 250 g $578.65 · AEE SI-111 45–90 µm 4N (q, 100 g min) |
| Mn 100 g | Sigma **266140** Mn −50 mesh 99.9% (manual price check — Sigma blocks automation) | (manual) | ESPI Mn powder −100 mesh 3N (q) · F.W. Winter custom cut (q) · Fisher AA4134314 −140+325 99.6% 25 g $49.25 |
| Cr 100 g | ESPI **Cr powder −50 mesh 2N8** or **−100 mesh 3N+** (q) — Fisher's stocked 99.97% is $10/g | (q) | Fisher AA3566818 −100+325 99.97% 50 g **$497.00** (×2 = $994 — pricey stopgap) · Exotech FL custom certified cut (q) · Belmont 99% (q) |
| Ti 200 g | Fisher **AA4310522** Ti −60+100 mesh (149–250 µm) 99.5%, 100 g, **$80.40** × 2 = **$160.80** | ✔ | Fisher AA4154522 spherical −150 mesh 99.9% 100 g **$113.00** (sieve 45 µm fines) · ESPI −100 mesh 3N (q) |
| Fe 100 g | Fisher **AA4735530** Fe −20 mesh 99.9%, 250 g, **$142.00** → sieve to ≤300 µm | ✔ | GFS Chemicals (OH) electrolytic Fe Item 226, 100 g (q — verify size) · Acros AC197815000 −70 mesh 99% 500 g (purity short) |
| Ni 100 g | Thermo **010579.22** (= AA1057922) Ni −60+170 mesh 99.7%, 100 g, **$68.90** | ✔ | Sigma 203904 ≤150 µm 99.99% (manual) — Thermo spherical −100+325 (042733.30) is discontinued |
| Cu 100 g | Thermo/Fisher **AA4262322** Cu spherical −100+325 mesh 99.9%, 100 g, **$57.80–69.10** | ✔ | Thermo 000908.36 −40+100 mesh 99.5% 500 g **$64.30** (exact band, sieve 300 µm top) · ACuPowder custom (q) |
| Zn 100 g | ESPI RFQ: **Zn granules −30 mesh 3N8 screened to −50+100**, or Zn −100 mesh 5N (q) | (q) | Fisher AA3969422 −140+325 99.9% 100 g **$301.00** (live but expensive; line shows EU discontinuation signals) · Acros −100+200 5N 2×50 g (manual) |
| Sn 100 g | Thermo/Fisher **AA0094122** Sn −100 mesh 99.85%, 100 g, **$68.00–81.00** → +325 sieve | ✔ | ESPI Sn −100 mesh 5N (q) · AEE SN-102 line, custom cut (q, 100 g min) |
| Al-10Zr 300 g | **AMG Aluminum NA** (q) — ask cut piece + crush; or **Kymera/Reading** custom alloy+granulate (q) | (q) | Beck Aluminum (Aleastur US stock, 440-684-4848) · KBM AlZr10 via Allied Metals · Milward (site TLS broken — phone) |
| Al-2Sc 250 g | **AMG Aluminum NA** Al-Sc 2% (q) — the proven US producer | (q) | Rio Tinto Element North 21 (salesinfo@riotinto.com) · KBM AlSc2 · Treibacher (lab-scale friendly) · Bayville Chemical NY (q) |
| Al-20Ce 250 g | **Kymera/Reading or Sophisticated Alloys custom binary Al-Ce melt + crush** (q) | (q) | Eck Industries WI (holds ORNL Al-Ce license — worth one email) · KBM AlCe(MM)10 (mischmetal — flag) |
| Al-10Er 100 g | **KBM Affilips custom AlEr** (EU, dodges China controls) via Allied Metals (q) | (q) | Ames Lab MPC Er metal + custom melt at Sophisticated Alloys (q) · ESPI Er powder −40 mesh 3N canned (q) · China routing only if delivered ≪ 2026-11-10 |
| Al-(5)Li 200 g | **Belmont Metals Al-5% Li** (q, small lots, Brooklyn NY) | (q) | KBM AlLi5 waffle (q, Ar-pack ask) · Milward (phone) |

**Planning envelope:** priced items above ≈ **$1,000–1,400** (with the ESPI Cr/Zn/Mn quotes
replacing the two overpriced Fisher lines) + hazmat/DG fees **$150–400** across shipments +
master alloys **$800–3,000** (quote-driven: melt-lot minimums and custom crushing dominate,
not metal content). **Total first-round estimate: ~$2,000–4,800.** July's $1.3–3.4K envelope
still brackets the middle of this; the master-alloy crush premium is the new unknown.

## 5. Fisher/Thermo verified-price snapshot (2026-08-17)

One basket on the existing university punch-out covers seven primaries. All pages showed live
Add-to-Cart; "discontinued" banners on Fisher pages are template boilerplate — only
042733.30 (Ni spherical 250 g) is actually dead (no price offered).

| SKU | Item | Pack | List |
| --- | --- | --- | --- |
| AA0001022 | Al powder −40+325 mesh 99.8% | 100 g | $29.35 |
| AA0086930 | Mg powder −20+100 mesh 99.8% | 250 g | $101.40 |
| AA0031122 | Si powder −100 mesh 99.9% | 100 g | $119.00 |
| AA4134314 | Mn powder −140+325 mesh 99.6% | 25 g | $49.25 |
| AA3566818 | Cr powder −100+325 mesh 99.97% | 50 g | $497.00 |
| AA4310522 | Ti powder −60+100 mesh 99.5% | 100 g | $80.40 |
| AA4154522 | Ti powder spherical −150 mesh 99.9% | 100 g | $113.00 |
| AA4735530 | Fe powder −20 mesh 99.9% | 250 g | $142.00 |
| 010579.22 | Ni powder −60+170 mesh 99.7% | 100 g | $68.90 |
| AA4262322 | Cu powder spherical −100+325 mesh 99.9% | 100 g | $57.80 (Thermo) / $69.10 (Fisher) |
| 000908.36 | Cu powder −40+100 mesh 99.5% | 500 g | $64.30 |
| AA3969422 | Zn powder −140+325 mesh 99.9% | 100 g | $301.00 |
| AA0094122 | Sn powder −100 mesh 99.85% | 100 g | $68.00 (Thermo) / $81.00 (Fisher) |

## 6. Element-by-element notes (condensed from the research sweeps)

### Aluminum (2 kg)
- **AEE/Micron Metals AL-111** ([micronmetals.com](https://micronmetals.com/product/aluminum-powder-coarse/)):
  atomized nodular Al, 99.7%, **−50+100 mesh — the only found off-the-shelf product in exactly
  the target cut**. $25/lb (1–2 lb) → $18.75/lb (3–10 lb); 2 lb min. Hazmat UN1396 class 4.3 —
  LTL/FedEx ground only, no UPS. Combine with their Si (SI-111) on one PO/shipment.
- **Valimet** (§8): H-95 spherical, 99.7%, d10 73/d50 108/d90 160 µm, ≤10% −200 mesh —
  effectively 75–177 µm with ~zero fines. Just under the 150–300 target but arguably better
  auger feed; custom −50+100 screens and 4N toll atomization are the RFQ items.
- **AMPAL / US Metal Powders** (Palmerton PA; new powder line mid-2025), **Toyal America**
  (Lockport IL; N/H/U purity tiers 99.7/99.96/**99.996%**, D50 ≤60 µm), **Kymera** (ECKA
  granules): industrial-scale backstops for the full campaign.
- ProChem (Rockford IL) Al −100 mesh 99.9% listed $80/500 g — right price, has fines; de-dust
  if used.

### Magnesium (100 g)
- Primary: Fisher **AA0086930** (−20+100 mesh = 149–841 µm, 99.8%, 250 g, $101.40): bottom cut
  already at 149 µm; one 300 µm sieve pass yields the exact target band with zero fines.
- **Luxfer Magtech / Hart Metals** (Tamaqua PA — it's Luxfer, not Kymera): *the* US mil-spec
  atomized-Mg house, cuts 20–1000 µm; smallest lot unknown — ask: (800) 503-4483,
  lmd-info@luxfer.com. The strategic source for the 20-run campaign.
- US Magnesium (Rowley UT) is gone for good (§2) — don't chase it.
- Ship as UN1869 class 4.1 (coarse, ground) or UN1418 4.3+4.2 (finer/air) — DG fee either way.

### Silicon (100 g)
- Cheap path: Fisher **AA0031122** ($119/100 g, 99.9%, −100 mesh) + a +325 de-fines sieve.
- Exact-cut path: **Chemsavers** (Bluefield VA) Si −50+100 mesh **99.999%** 250 g **$405**
  free shipping ([listing](https://chemsavers.com/great-deals/silicon-metal-powder-50-100-mesh-99-999-metals-basis-electronic-grade-certified-250g/)) — confirm stock/PO terms.
- AEE SI-111 (45–90 µm 4N, 100 g min, quote) consolidates with the Al order. Coarse Si is
  non-hazmat.

### Manganese (100 g)
- US EMM context: essentially all imported (China-dominant); domestic capacity (Electric
  Metals USA, MN) still ramping; EMD antidumping order continued Feb 2026. Buy stocked US
  inventory early; consider a second 100 g as shelf insurance.
- Primary: **Sigma 266140** Mn −50 mesh 99.9% trace-metals (≤297 µm — exact top cut; screen
  +100 in glovebox). Sigma blocks all automation — price via punch-out.
- **ESPI** "Manganese Powder −100 Mesh 3N" (stock KNC8086, quote, same-day response).
- **F.W. Winter** (Camden NJ, the US electrolytic-Mn specialist): custom −50+100 mesh ask —
  info@fwwinter.com, (856) 963-7490.
- AEE MN-101 ships UN3089 class 4.1.

### Chromium (100 g)
- No China exposure: aluminothermic Cr is French (DCX Chrome/Delachaux — US warehouse:
  Delachaux Metal Inc., Napoleon OH) or German (GfE).
- Fisher's only ≥99.9% stocked item (AA3566818, 99.97%, 44–149 µm) is **$497/50 g** — works
  but is the most expensive line in the basket. Get ESPI's quote first (−50 mesh 2N8 = 99.8%,
  ≤297 µm — best size match; or −100 mesh 3N+), and **Exotech** (Pompano Beach FL — US
  manufacturer from recycled targets, 99.7–99.99%, custom −3 to −325 mesh cuts, ICP/LECO
  certified) for a certified 100–500 g custom lot.

### Titanium (200 g)
- Buy 2× Fisher **AA4310522** (−60+100 mesh, 149–250 µm, 99.5%, $80.40) — dead center of the
  target band; note on the PO that the 99.99% chart spec was amended (4N Ti powder doesn't
  exist). If purity must exceed 99.5%: AA4154522 spherical 99.9% ($113/100 g, sieve off
  <45 µm) or ESPI −100 mesh 3N (quote).
- Industrial scale-up doors: Kymera/Reading "AmeriTi" HDH (custom PSD), AP&C/Colibrium
  (Quebec, spherical CpTi), 6K Additive (PA).
- Hazmat: UN2546 class 4.2 (spherical) / UN2878 4.1 (coarse) — ground only, DG fee, end-use
  statement common.

### Iron (100 g)
- Fisher **AA4735530** (−20 mesh ≤841 µm, 99.9%, 250 g, $142) + in-lab sieve to ≤300 µm
  (reject stays useful as non-auger melt stock).
- **GFS Chemicals** (Powell OH — US electrolytic-Fe manufacturer): Item 226 "Iron,
  Electrolytic, Primary Standard" 100 g — call to confirm particle form ≤300 µm or a custom
  screen; if yes this becomes the best answer (99.95%+, US-made, PO-friendly).
- Avoid <45 µm and carbonyl Fe (pyrophoric-adjacent). AEE FE-101 is 1–9 µm — ruled out.

### Nickel (100 g)
- Thermo **010579.22** −60+170 mesh 99.7% 100 g $68.90 — one pack, right cut. (Alfa retitled
  the legacy "−50+100" item; same product. Also on VWR as 7484717.)
- 99.9% floor rigid? Sigma **203904** ≤150 µm 99.99% (punch-out price) + 45 µm de-fines sieve.
- Thermo spherical −100+325 (042733.30) is discontinued. Novamet lines are all too fine.
  ACuPowder (Union NJ) is the US producer RFQ for custom cuts — (908) 851-4500 (their web TLS
  cert is expired; phone).

### Copper (100 g)
- **AA4262322** spherical −100+325 mesh 99.9% 100 g $57.80 (Thermo) — meets both hard
  constraints, best flow. For the literal 150–300 µm band: 000908.36 (−40+100, 99.5%, 500 g,
  $64.30) + 300 µm top sieve, accepting 99.5%.
- ACuPowder custom −50+100 99.9% cut = long-term route.

### Zinc (100 g)
- The constrained one. Ideal stocked cut (AA3969422 −140+325 99.9%) is **live at $301/100 g**
  but shows line-erosion signals (delisted Fisher UK). Better: **ESPI RFQ** — Zn granules
  −30 mesh 3N8 screened to −50+100, or Zn −100 mesh 5N (Knc8394). Fallback: Acros −100+200
  mesh 99.999% 2×50 g via Fisher (punch-out check). Zinc powder ships UN1436 class 4.3(+4.2).
- Skip zinc dust (fine), shot (coarse), and pyro-grade material.

### Tin (100 g)
- **AA0094122** −100 mesh 99.85% $68 (Thermo) + +325 sieve. Purity floor rigid → ESPI Sn
  −100 mesh **5N** quote. AEE SN-102 line has custom cuts (100 g min). Non-hazmat.

## 7. Master alloys (all quote-only — see §3 for form/crush reality)

Single best consolidation play: **one RFQ to Kymera/Reading Alloys** (they cast master alloys
AND crush/classify brittle alloys to controlled PSD in-house — the only single-vendor
"alloy + 150–300 µm granules" door found), plus **Sophisticated Alloys** (Butler PA,
(724) 789-0158, VIM melts "from a few grams") as the universal small-lot backstop.

| Alloy | Ranked suppliers | Notes |
| --- | --- | --- |
| Al-10Zr (300 g) | 1. AMG Aluminum NA (info@amg-al.com, 800-523-8457) · 2. Kymera/Reading (RFQ) · 3. Beck Aluminum/Aleastur US stock (440-684-4848) · 4. KBM AlZr10 via Allied Metals · 5. Milward Alloys, Lockport NY (site TLS broken — phone) | US-made routine item; no export-control exposure. Standard form waffle (~7.7 kg) — ask for cut piece + crush |
| Al-2Sc (250 g) | 1. **AMG Aluminum NA** — Sc 2.0±0.3%, Fe ≤0.05, aerospace grade · 2. **Rio Tinto Element North 21**, Sorel-Tracy QC (salesinfo@riotinto.com) — only N.American Sc producer, sells "standard Al-Sc alloy"; small-qty policy unknown · 3. KBM AlSc2 · 4. Treibacher (Austria — explicitly lab-batch friendly) · 5. Bayville Chemical, Smithtown NY (631-586-4309) | **China routing is structurally unreliable (licensed since Apr 2025).** Sc metal ≈ $3.3–5.3k/kg benchmarks → 250 g of Al-2Sc contains ~5 g Sc; quotes will be melt-lot-minimum-driven, likely low-$100s–$1k |
| Al-20Ce (250 g) | 1. Kymera/Reading or Sophisticated Alloys **custom binary melt** · 2. Eck Industries, Manitowoc WI (ORNL Al-Ce licensee — one email worth sending) · 3. KBM AlCe(MM)10 via Allied (mischmetal — La/Nd/Pr present) · 4. Belmont/Milward custom | Ce not export-controlled; Ce metal feed is cheap and available — custom melt is low-risk |
| Al-10Er (100 g) | 1. **KBM Affilips custom AlEr** (only non-China producer advertising AlEr; info@kbmaffilips.com, +31 412 681311; US agent **Allied Metals**, alliedmet.com) · 2. Ames National Lab **Materials Preparation Center** (Ames IA) Er metal → custom melt at Sophisticated/Kymera · 3. ESPI Er powder −40 mesh 3N (canned) as elemental fallback · 4. China storefronts (Heeger AlEr10 waffle/rod/shot; SAM) — **only with delivery ≪ 2026-11-10** | Er controls resume 2026-11-10 unless the truce is extended — this is the schedule-critical item |
| Al-5Li (200 g, re-spec from Al-10Li) | 1. **Belmont Metals** Al-5% Li (833-4-ALLOYS, small lots, granular/shot culture) · 2. KBM AlLi2/AlLi5 waffle via Allied — ask Ar-sealed packaging · 3. Milward (phone) | Spec coarse granules (250–300 µm), Ar-backfilled packaging, dry-box storage — crushed Al-Li fines pick up moisture |
| (Optional) Al-5Ti-1B rod | AMG "TiBAl" · Beck/Aleastur rod, US stock | Only if TiB₂ grain refinement is later wanted; the plan's Ti is now elemental powder |

## 8. Valimet (per @sgbaird's suggestion)

Family-owned US manufacturer of gas-atomized **spherical Al and Al-alloy powders**, Stockton
CA; mil-spec pedigree (MIL-PRF-23950 types); "standard and custom particle size
distributions"; **toll atomization of custom alloys** (Special Alloys Group).

- **Phone (209) 444-1600** · fax (209) 444-1636 · **sales@valimet.com** / valimet@valimet.com
- RFQ/sample form: [valimet.com/request-quote](https://valimet.com/request-quote) ("contact us
  for a quote or a sample") · 431 Sperry Rd, Stockton CA 95206
- People: Luigi Alzati (VP Sales & Marketing), Chris Adam (President)
- All H-grades 99.7% Al min (Fe ≤0.2%); coarsest standards **H-95** (d50 108, d90 160 µm,
  ≤10% −200 mesh) and H-60; "many other sizes from stock, custom sizing offered"
  ([H-series datasheet](https://valimet.com/wp-content/uploads/2021/08/Aluminum-H-Series-Data-Sheet-.pdf))

**Call script:** (1) smallest saleable lot / sample of H-95 or a custom −50+100 screen;
(2) feasibility + minimum for toll-atomizing customer-supplied 4N ingot (and whether they'd
atomize our *alloyed* compositions later — that could eventually replace in-house blending for
production runs); (3) if they can't do 2–5 kg lots, who they'd refer (they know every US Al
powder distributor); (4) price/lead.

## 9. Contact directory (RFQ channels)

| Supplier | Role | Contact |
| --- | --- | --- |
| Valimet (Stockton CA) | Al spherical + toll atomization | (209) 444-1600, sales@valimet.com |
| AEE / Micron Metals (Upper Saddle River NJ) | coarse Al/Si + custom mesh cuts everything | (201) 828-9400 / (800) 486-2436 |
| ESPI Metals (Ashland OR) | quote-house: Mn/Cr/Zn/Sn/Mg-4N/Sc/Er | sales@espimetals.com, (541) 488-8311 / (800) 638-2581 — same-day quotes, no minimum, institutional POs only |
| Luxfer Magtech / Hart Metals (Tamaqua PA) | mil-spec atomized Mg granules | (800) 503-4483, lmd-info@luxfer.com |
| F.W. Winter (Camden NJ) | electrolytic Mn | info@fwwinter.com, (856) 963-7490 |
| Exotech (Pompano Beach FL) | US Cr powder, certified custom cuts | exotech.com RFQ |
| GFS Chemicals (Powell OH) | US electrolytic Fe | gfschemicals.com, phone on site |
| ACuPowder (Union NJ) | Cu/Sn/Zn/Ni producer, custom cuts | (908) 851-4500, info@acupowder.com — **site TLS expired, call** |
| Kymera International / Reading Alloys (Raleigh NC / Robesonia PA) | master alloys + crush/classify to PSD; Ti HDH | info@kymerainternational.com, (984) 900-2749, web RFQ |
| Sophisticated Alloys (Butler PA) | custom VIM melts "from a few grams" | (724) 789-0158 |
| AMG Aluminum NA (Wayne PA) | Al-Sc/Al-Zr/TiBAl producer | info@amg-al.com, (800) 523-8457 |
| Belmont Metals (Brooklyn NY) | small-lot masters, granular/shot forms | (833) 4-ALLOYS, web RFQ |
| Beck Aluminum (Chagrin Falls OH) | Aleastur (Spain) master alloys, US stock | (440) 684-4848 |
| KBM Affilips (Oss NL) | full master-alloy range incl. AlEr/AlLi | info@kbmaffilips.com, +31 412 681311; US agent Allied Metals (alliedmet.com) |
| Rio Tinto Element North 21 (Sorel-Tracy QC) | N.American Al-Sc | salesinfo@riotinto.com |
| Treibacher (Althofen AT) | custom AlSc, lab-scale friendly | treibacher.com portal |
| Ames National Lab MPC (Ames IA) | research-grade Sc/Er metal to universities | ameslab.gov/dmse/materials-preparation-center → "Request a quote" |
| Eck Industries (Manitowoc WI) | Al-Ce know-how (ORNL licensee) | eckindustries.com contact |
| Chemsavers (Bluefield VA) | 5N Si −50+100 mesh, priced | chemsavers.com |

## 10. RFQ-ready ask (copy-paste for calls/emails)

> We are a university additive-manufacturing lab buying research quantities of elemental
> feedstock for melt atomization. All items must be **powder or granules, 150–300 µm
> (−50+100 mesh preferred; ≤300 µm hard max, ≥45 µm bottom screen where possible)**, packed
> under argon or vacuum, with a certificate of analysis reporting **metals-basis purity plus O
> content and Fe/Si**. Quantities: Al ≥99.7% (99.99% if available) — 2 kg; Mn 99.9 %, Mg
> ≥99.8 %, Si 99.9 % — 100 g ea.; Cr ≥99.8 %, Cu 99.9 % — 100 g ea.; Zn 99.9 % — 100 g; Ni,
> Fe, Sn 99.9 % — 100 g ea.; Ti ≥99.5 % — 200 g. Master alloys (cast, then crushed/screened to
> 150–300 µm; Ar-packed): Al-10Zr — 300 g; Al-2Sc — 250 g; Al-20Ce (binary, not mischmetal) —
> 250 g; Al-10Er (or Al-5Er × 2) — 100 g; Al-5Li — 200 g. Please quote price, lead time,
> country of origin, and hazmat shipping fees (Al/Mg/Ti/Zn/Mn powders are DOT class 4.1/4.2/4.3
> as applicable). Small-lot substitutions and nearest-stock granulations are welcome.

## 11. Action list (suggested order)

1. **Fisher punch-out basket today** (verify punch-out pricing ≤ list): AA0086930 (Mg),
   AA0031122 (Si), AA4310522 ×2 (Ti), AA4735530 (Fe), 010579.22 (Ni), AA4262322 (Cu),
   AA0094122 (Sn). ≈ **$750** list. Optionally AA0001022 (Al 100 g, $29.35) as an
   auger-commissioning bridge while the 2 kg order is quoted.
2. **One ESPI email** (same-day quotes): Mn −100 mesh 3N · Cr −50 mesh 2N8 and −100 mesh 3N+ ·
   Zn 3N8 screened −50+100 (or −100 mesh 5N) · Sn 5N (purity insurance) · Mg granules 4N
   (ask granule size!) · Sc powder −40 mesh 3N canned · Er powder −40 mesh 3N canned (prices
   for reference vs. masters).
3. **AEE order/RFQ**: AL-111 Al 5 lb + SI-111 Si 100 g on one hazmat shipment.
4. **Two calls**: Valimet (§8 script) and Luxfer Magtech (smallest lot of −50+100 atomized Mg).
5. **Master-alloy RFQs (one email each)**: Kymera/Reading (all five alloys + crush — ask for
   single-PO pricing), AMG (Al-2Sc + Al-10Zr, cut + crush), Belmont (Al-5Li + granular forms),
   KBM/Allied (AlEr custom + AlLi5 backup), Sophisticated Alloys (quote the full five as
   custom melts — the comparison quote). Copy §10 text.
6. **Before 2026-11-10:** lock the Er route (KBM or Ames-fed custom melt; any China-origin
   fallback must deliver before controls resume). Sc: US/CA route only.
7. Sigma manual check (Mn 266140, Ni 203904) from a campus browser.

## 12. Verification log

| Check | Route | Result |
| --- | --- | --- |
| Fisher/Thermo 13 SKUs (§5) | Pi (residential IP), 2026-08-17 | all live with listed prices except 042733.30 (discontinued); "discontinued" banners elsewhere = template boilerplate |
| ESPI shop (15 element pages + 4 detail pages) | Pi | live; quote-only (no prices online); availability as §6; −40 mesh Sc/Er cans confirmed as titles |
| Valimet site + H-series datasheet | runner + agent | capabilities/contacts as §8 |
| Fisher search endpoint | Pi | 403 even residentially — use direct product URLs |
| Sigma-Aldrich | Pi + agents | blocks all automation — manual browser only |
| micronmetals.com (AEE) | Pi + agent | live; prices listed on some SKUs (AL-111 tiers), quote on others |
| samaterials.com (Stanford Adv. Mat.) | agent | 403 — manual verification; China-sourced flag stands |
| milward.com | agent | TLS certificate expired — phone them |
| acupowder.com | agent | TLS certificate expired — phone them |
| Policy sources (§2) | agent (multi-source) | dates/status as cited; re-verify near 2026-11-10 |

*Research assembled by Claude (issue #161); four parallel web sweeps, 2026-08-17. Prices are
snapshots — re-verify at order time.*
