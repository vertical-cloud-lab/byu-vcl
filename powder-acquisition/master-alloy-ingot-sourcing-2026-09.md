# Master Alloys in Ingot / Chunk Form for In-House Atomization, and Small-Lot Rare Earths (2026-09-03)

**Context:** [Issue #161 — Atomizer Powder Acquisition](https://github.com/vertical-cloud-lab/byu-vcl/issues/161).
This document answers @sgbaird's 2026-09-03 questions:

1. Are there **master alloys sold in block / ingot / chunk form** (Al-Mg first, then Al-Sc, Al-Zr, Al-Er,
   Al-Ce, Al-Li, Al-Ti) that the lab could remelt and atomize itself on the rePowder — looking at
   Thermo Fisher and ESPI first, then others?
2. **Is 25 g the minimum lot for scandium?** The lab wants to cap spend at **~$1,000 per individual
   rare-earth material** for now.

It builds on [quote-review-2026-08.md](quote-review-2026-08.md) (the ESPI / Fisher / AEE quotes),
[supplier-search-2026-08.md](supplier-search-2026-08.md) (the wider supplier map) and
[purchase-quantity-model.md](purchase-quantity-model.md) (campaign consumption: **Sc 4 g, Er 5 g,
Ce 37.5 g, Mg 36 g, Zr 27.5 g, Li 2.9 g, Ti 7.5 g** for the 20-run first round).

> **Verification note.** The Raspberry Pi route could not be used this run: the `claude.yml`
> workflow does not contain a Tailscale connect step, the OAuth client in the runner's environment
> only permits an unknown device tag (25 plausible tags were rejected), and the client's API scopes
> do not allow reading the ACL to find it. All fetches below were made from the GitHub runner on
> 2026-09-03; Fisher/Thermo product pages happened to serve list prices to the datacenter IP
> today. See §9 for the fix.

---

## 0. Bottom line

| Question | Answer |
| --- | --- |
| **Al-Mg master alloy in ingot form?** | **Neither Thermo Fisher nor ESPI stocks one** (§2–3). The off-the-shelf answer is **Belmont Metals' 50/50 Magnesium-Aluminum lumps (code 6501B)** — brittle Al-50Mg, 2″ to ¼″, US stock, on their web store at ≈ $25–28/lb with a 5-lb minimum (≈ $130) — crushable in the glovebox, no atomizer run needed (§4–5). ESPI stocks 2N8 Mg ingot, 3N pieces, 3N–4N pellets and 4N granules and has in-house induction / vacuum-arc melting, so a **custom Al-35Mg button is a one-line ask on the same ESPI RFQ**; Sophisticated Alloys ("few grams to ~500 g", no minimum) and ACI Alloys do the same. |
| **Other masters as chunks at ESPI?** | **Yes — ESPI sells Al-based binary alloys as 3–12 mm pieces, by the gram, no minimum:** Al-10Zr 4N, Al-50Zr 4N, Al-10Ti 3N, Al-33Cr 3N, Al-1Li, Al-10Cu 4N, Al-Si 1–25 % 4N/5N, Al-15Sn 4N, Al-Zn drops, Al-Ni. These are catalogued as "evaporation materials" but are simply cast binary alloys — exactly what a 100 g remelt needs. **No Al-Sc, Al-Er, Al-Ce or Al-Mn at ESPI.** |
| **Is 25 g the Sc minimum?** | **No.** ESPI's ordering page states *"There is no minimum order size, quantity, or charge"*, and every ESPI Sc item (chips, pieces, −40 mesh powder) is listed with **Unit of Measure: Gm** — the 25 g on the quote is the can size ESPI reached for, not a floor (at $235/g, 4 g = $940, 5 g = $1,175). Better: **Thermo Fisher sells a ≈ 5 g Sc arc-cast pellet, 045118.KF, for $352–458** (REO impurities ≤ 0.001 %) — one pellet is the whole campaign's scandium at a third of ESPI's per-gram rate. Al-2Sc master alloy in a 250 g lot (QS Advanced Materials, US, from ~$200–300) is the other sub-$1k route (§7). |
| **≤ $1k per rare earth** | Sc: Thermo pellet ($352–458) or 250 g Al-2Sc — both fit. Er: the quoted 25 g / $800 fits but is 5× the campaign need; **Thermo 000111.09 Er pieces, 10 g, $145 list** is the right buy. Ce: **Thermo 000065.18 Ce ingot 99.8 %, 50 g, $170** or 250 g of 99 % for $162. All three certified: **≈ $670–770 total** (§7). |

---

## 1. Engineering framing — what "atomize the master ourselves" actually buys

**What the rePowder produces.** Amazemet's own specification for the rePowder is a d50 of
**80–100 µm at 20 kHz, 45–60 µm at 40 kHz and 35–45 µm at 60 kHz**, with a narrow distribution
("up to 80 % of the manufactured powder" inside the target window), induction or plasma melting
from 200 °C to 3500 °C, and feed forms of "chips, failed AM prints, damaged samples, rods, wire,
powder" ([amazemet.com/repowder](https://amazemet.com/repowder/)). Two consequences:

1. **In-house atomized master alloy will be ~100 µm powder at coarsest, not 150–300 µm.** That is
   below the sand-sized dosing target, but it is *spherical* and *narrow-PSD*, which is what
   actually governs auger flow: the cohesion index used in
   [quote-review-2026-08.md §3.1](quote-review-2026-08.md) for a 100 µm sphere is ≈ 6×, in the same
   "fine but feeds" class as the Fisher spherical Cu that was rated acceptable. It should be
   trialled in the auger before it is relied on.
2. **Every master you atomize costs an atomizer run.** With 20 alloy runs planned, each master
   atomization is a 5 % tax on the campaign plus one crucible clean-out. It is worth it for
   the two or three elements where powder is unobtainable or unsafe (Mg, Li), not for elements
   that arrive as usable powder already (Zr, Cr, Ti, Cu, Si — all now available as ESPI pieces
   *and* as powder from the August quotes).

**Crush-and-screen is the cheaper route for brittle masters.** High-solute masters are
intermetallic-dominated and brittle — Al-50Mg (β-Al₃Mg₂ / γ-Al₁₂Mg₁₇), Al-33Cr, Al-50Zr, Al-Ni,
Al-25Si — and can be crushed in the glovebox and screened to −50+100 mesh with no atomizer time.
Dilute masters (Al-2Sc, Al-10Zr, Al-1Li, Al-5Li, Al-10Er) are ductile α-Al with a few percent of
particles and will *not* crush; those are the ones where atomizing (or simply hand-charging a
weighed lump) is the only route to a dosable form.

**Al-Mg specifics.**

- **Which Mg level.** The Al-rich eutectic sits at ~450 °C and ~35 wt % Mg, so an **Al-35Mg**
  master is fully liquid barely above 450 °C — the easiest melt in the whole programme and the one
  with the least Mg loss (low temperature, Mg activity diluted by Al). Commercial "magnalium" is
  Al-50Mg (liquidus ~460 °C); it works too but is more Mg-reactive and its atomized powder *is*
  pyrotechnic-grade magnalium at ~100 µm. Prefer **Al-25 to Al-35Mg** for a custom melt; accept
  Al-50Mg if that is what is on the shelf.
- **Dose mass.** For the Al-Ce-Mg family (6 wt % Mg) an Al-35Mg master means 17 g of master per
  100 g batch, Al-50Mg means 12 g; both are trivial for the auger and both stay inside the 100 g
  crucible budget once the Al base is reduced accordingly.
- **Safety relative to pure Mg.** Diluting Mg into Al cuts its vapour pressure and gives the melt an
  Al₂O₃ / MgAl₂O₄ skin instead of a burning MgO one, so an Al-Mg remelt is the appropriate
  *first* reactive melt on the machine — pure Mg is not (see
  [quote-review-2026-08.md §4](quote-review-2026-08.md)). The atomized Al-Mg powder is still a
  combustible metal dust: argon storage, Class D extinguisher, coarse screen, same rules as the
  rest of the inventory.
- **Charge losses.** Keep the 15 % Mg over-charge from the purchase model; the master route does
  not remove evaporation, it just moves it to a cooler melt.

---

## 2. ESPI Metals — what is actually on the shelf (verified 2026-09-03)

ESPI's new shop is quote-only (product pages carry no price and no pack size), but the catalogue
is complete and the ordering rules are explicit:

- *"We specialize in supplying small quantities of materials for research."* —
  [espimetals.com/index.php/faq](https://www.espimetals.com/index.php/faq)
- *"There is no minimum order size, quantity, or charge. Please inquire about items or quantities
  not found on this online catalog."* —
  [espimetals.com/index.php/ordering-information](https://www.espimetals.com/index.php/ordering-information)
- In-house capability: *"Located within our fabrication facility is the melting department …
  Induction melting … Vacuum arc melting"* — [espimetals.com](https://www.espimetals.com/) home
  page. ESPI's catalogue already contains dozens of custom binary alloys (Er-Ni, Fe-Al, Ti-Sn,
  Zr-Ti, the Al-X pieces below), i.e. custom binary melts are routine for them.
- Contact: **sales@espimetals.com**, 1-800-638-2581, or the
  [custom quote form](https://www.espimetals.com/request-a-custom-quote) (quote "within the next
  business day").

### 2.1 Al-based binary alloys in piece form (all "Unit of Measure: Gm")

| ESPI item | Stock no. | Solute delivered | Use in the plan |
| --- | --- | --- | --- |
| [Aluminum-Zr10 % Pieces 4N](https://shop.espimetals.com/knd2760-aluminum-evaporation-materials.html) | Knd2760 | 10 wt % Zr on a 4N basis | **Direct hit for the Al-10Zr line (300 g)** — hand-charge as lumps, or atomize once into ~100 µm powder. Replaces the Kymera custom-crush request. |
| [Aluminum-Zr50 % Pieces 4N](https://shop.espimetals.com/knd2756-aluminum-evaporation-materials.html) | Knd2756 | 50 wt % Zr | Brittle — **crushable in the glovebox** to a −50+100 mesh granule; 55 g covers the whole campaign's 27.5 g Zr. |
| [Aluminum-Ti10 % 5 mm Pcs 3N](https://shop.espimetals.com/knc6829-aluminum-evaporation-materials.html) | Knc6829 | 10 wt % Ti | Replaces both the Al-5Ti-1B rod and the −325 mesh Ti powder: no TiB₂, no Class 4.2 dust, 75 g covers the campaign's 7.5 g Ti. |
| [Aluminum-Cr33wt % Pieces 3N](https://shop.espimetals.com/knd1027-aluminum-evaporation-materials.html) | Knd1027 | 33 wt % Cr | Brittle intermetallic — crushable; 60 g covers the 20 g Cr need without any −325 mesh Cr powder. |
| [Aluminum-Li1 % 3–7 mm Pieces](https://shop.espimetals.com/knc9021-aluminum-evaporation-materials.html) | Knc9021 | 1 wt % Li | Too dilute for the Al-Li-Cu run (2 wt % Li target needs Al-5Li or richer) — listed for completeness; also Al-Li 0.1 % (Knc9391). |
| [Aluminum-Cu10 % Pieces 4N](https://shop.espimetals.com/knd2761-aluminum-evaporation-materials.html) | Knd2761 | 10 wt % Cu | Optional: cleaner Cu carrier than powder for the Si-Mg-Cu / Zn-Mg-Cu families; also Al-Cu50 % 4N (Knd2757). |
| Aluminum-Si 1 / 1.5 / 2 / 5 / 10 / 11 / 25 % pieces, 4N–5N | Knc6733, Knc9293, Knc9931, Knc6811, Knc6833, Knc6269, Knc6830 | Si | Al-Si11 % 5–10 mm 4N (Knc6269) is a near-eutectic lump that melts at 577 °C — the easiest way to bring 12 wt % Si into a 100 g melt. |
| Aluminum-Sn15 % Pcs 5–12 mm 4N (Knc7919) · Aluminum-Zn alloy drops (Knd5066) · Aluminum-Ni pieces (Al₃Ni, Al₃Ni₂, AlNi, Al21Ni79) | — | Sn, Zn, Ni | Available if the powder lines fall through; not needed today. |

**Not found at ESPI (searched "Aluminum-Mg/-Sc/-Ce/-Er/-Mn", "AlMg", "master alloy"):** Al-Mg
(the research agent saw only an Al-1.5 % Mg *wire*), Al-Sc, Al-Er, Al-Ce, Al-Mn. The full shop
search returned only the items above.

### 2.2 Magnesium, aluminium base, and rare-earth solid forms at ESPI

| Element | Solid forms listed | Stock no. (where read) | Note |
| --- | --- | --- | --- |
| **Mg** | Ingot 2N8 (sold by the **lb**) · Pieces 3N, 3N35, 1″+ 3N35 · Pellets ⅛″ in 3N35 / 3N5 / **4N** · Pellets ¼″ in 3N / 3N35 / 4N · **Granules 4N** · Chips 3N35 · rod | Ingot Knd1952 · Pieces 3N K3143x · Granules 4N K3141 | The ½″ pieces on the August quote ($2.30/g) are the 3N "Pieces". **4N ⅛″ pellets** are the clean feed for an in-house Al-Mg melt; 2N8 ingot by the pound is the cheap feed. Granule size for K3141 is still unpublished — ask. |
| **Al** | Shot 3N / **4N** / 5N / 6N (1–3, 4–12, 5–8 mm) · Pellets ⅛″, ¼″, 3–8 mesh (4N, 5N) · Ingot 3N7+, **4N**, 5N, 5N5 · **Powder −50+100 mesh 2N7** | — | 4N Al shot is the Valimet-quote fallback for a 4N base: buy shot, atomize in-house. The −50+100 mesh 2N7 powder is a second source for the AEE AL-111 cut. |
| **Sc** | Chips 3N · Pieces 3N (can) · Powder −40 mesh 3N (amp / can) · Rod ¼″, ½″ 3N | Chips Knc6313 · Pieces Knc9206 · Powder Knd1178 | All "Unit of Measure: Gm" → **ask for 4–5 g of chips or pieces**, not the 25 g can. |
| **Er** | Pieces 1–3 mm, 3–6 mm, 6–12 mm 3N · Chips 1–3 mm 3N · Powder −24 mesh, −40 mesh 3N | Pieces 1–3 mm Knd2551 | 10 g of 1–3 mm pieces is the right lot for a 5 g need; no can minimum. |
| **Ce** | Ingot 3N · Pieces 3N (amp / can / oil) · Chips 3N (argon) · **Powder −24+40 mesh 3N** (425–710 µm) · Rod | — | Ce metal is cheap; 40–50 g of pieces (argon-packed) makes a binary Al-Ce master in one in-house melt, avoiding the mischmetal problem entirely. |
| **Zr** | Chips −1 mm, 1–3 mm 3N · Pellets ⅛″, ¼″ · Pieces 6–12 mm 3N · Sponge · **Powder −60+100 mesh 2N7** | — | Only relevant if Al-10Zr pieces are refused; the powder is Class 4.2. |
| **Li** | Rod ½″ × 2½″ · Wire ⅛″ (oil) | — | No Al-Li master richer than 1 % — Al-5Li still has to come from Belmont / KBM (§4). |

---

## 3. Thermo Fisher / Alfa Aesar — no master alloys, but the right rare-earth pieces

The Thermo Scientific Chemicals (ex-Alfa Aesar) catalogue was searched for aluminium-based alloys
and master alloys and for magnesium / scandium solid forms. Product pages served list prices to
the runner on 2026-09-03 (the "discontinued" banner on every page is template boilerplate, as in
August).

| Need | Thermo Fisher answer | Cat. no. | Pack / price (list, 2026-09-03) |
| --- | --- | --- | --- |
| Al-Mg or any Al master alloy | **None.** No Al-Mg, Al-Sc, Al-Zr, Al-Er, Al-Ce, Al-Li or Al-Ti master alloy is catalogued. The only Al-Mg items are wrought shapes — 5052 plate (discontinued), 5056 gauze, 6061 foil/rod, and Sigma-resold Goodfellow Al97Mg3 / Al95Mg5 pieces (form not shown, ≈ $600+ each) — plus 99:1 and 96.5:3.5 Al-Si evaporation slugs (042322, 038492) and −325 mesh AlSi12 powder (088322). | — | — |
| Mg solid forms | **Turnings, granules, rods, slugs, cube, foil — no ingot, no pieces/lumps, no chips of its own brand.** Turnings 99.8 % (010232: AA1023222 100 g; 2.5 kg $469) · turnings 99+ % (L08120: AAL0812022 100 g **$44.65**, list $57.80) · turnings −4 mesh 99.98 % (036193: AA3619318 50 g **$47.65**, list $63.00) · Acros 99.9+ % turnings (AC191085000 500 g $98.65) · **granules −4+30 mesh 99.8 % (000870: AA0087036 500 g $168.70)** · rod 7.9 mm × 25 mm 99.9 % (043355.KF, $46.50/pc) · rod 3.3 cm × 30 cm 99.8 % (010231, ≈ 450 g/pc) · 19 mm cube (045119.KF, $93.50) · 99.95 % slugs (043296–043299, $185/10 g and up) · AZ31B plate/rod (Mg-3Al-1Zn, not a master). Prices as read on fishersci.com by the research agent, 2026-09-03. | see left | see left |
| Sc metal | *Scandium pieces, distilled dendritic, 99.9 % (REO)*, under Ar | [039996.04](https://www.thermofisher.com/order/catalog/product/039996.04) | **2 g, $615.00 list / $553.65 online** (Fisher list $788.65) ≈ $277–394/g |
| | **Scandium arc-cast pellet, 15.9 mm dia, ≈ 5 g, total REO impurities ≤ 0.001 %** — the best certified $/g Sc found anywhere | [045118.KF](https://www.thermofisher.com/order/catalog/product/045118.KF) (Fisher AA45118KF) | **1 pc ≈ 5 g, $414.00 list / $351.65 online** (Fisher list $458.00) ≈ $70–92/g |
| | *Scandium ingot* — actually a Sc–Ta (8–12 % Ta) crucible ingot, not orderable | 040229.06 | 5 g, unusable here |
| | Sc powder −40 mesh | — | not in the current catalogue |
| Er metal | *Erbium pieces, 99.9 % (REO)*, under Ar | [000111.09](https://www.thermofisher.com/order/catalog/product/000111.09) · 000111.18 | **10 g $145.00** ($123.65 online) · 50 g $495.00 |
| | *Erbium powder, −40 mesh, 99.9 % (REO)* | 044169.06 · 044169.14 | 5 g $243.00 · 25 g $906.00 |
| Ce metal | *Cerium ingot, 99 % (REO)*, under oil | [043977.30](https://www.thermofisher.com/order/catalog/product/043977.30) · 043977.A1 | **250 g $162.00** · 1 kg $644.00 |
| | *Cerium ingot, 99.8 % min (REO)* | [000065.18](https://www.thermofisher.com/order/catalog/product/000065.18) · 000065.30 | **50 g $170.00** · 250 g $623.00 |
| 4N / 5N Al for remelting | Al shot 99.99 %, 9.5 mm ([045001.A1](https://www.thermofisher.com/order/catalog/product/045001.A1)) · Al shot 99.9 %, ≤ 15 mm (000632.A3) · Al ingot 99.999 % (010571.22) · Al shot 99.999 % 4–8 mm (010573.A1) | see left | **4N shot 1 kg $103.00 list / $87.65 online** · 99.9 % shot 2 kg $122.00 / $103.65 · 5N ingot 100 g $95.40 list · 5N shot 1 kg: price not read |
| Mg powder (from the August quote) | AA0086930 / 000869.30, −20+100 mesh 99.8 % — still priced on the web page ($101.40) but quoted **"No source"** by the Fisher quote desk on #M6449 | — | — |

**Read-across:** Thermo Fisher is the right place for **a 5 g Sc arc-cast pellet, 10 g of Er pieces and
50–250 g of Ce ingot**, and it stocks **4N Al shot at ~$90–103/kg** — a ready alternative to the Valimet
4N powder quote if the base is to be atomized in-house. It sells no master alloy to atomize; its Mg
turnings and −4+30 mesh granules are the feed for an in-house Al-Mg melt.

---

## 4. Everyone else — who sells solid master alloys in lots a lab can buy

Solid forms only (waffle / piglet / ingot / slab / lumps / pieces / rod). "Quote" = no price
published. US sources first. Verified directly from the runner unless marked *(agent)*, which
means read by a research agent from the vendor page on 2026-09-03; *(snippet)* = search-engine
text only, site blocked.

### 4.1 US producers and small-lot houses

| Vendor | Al-Mg | Al-Sc | Al-Zr | Al-Er | Al-Ce | Al-Li | Al-Ti / TiB | Smallest lot / price | Contact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Belmont Metals**, Brooklyn NY | **50/50 Mg-Al lumps (2″–¼″), code 6501B** — "brittle master alloy … for the safe and precise addition of magnesium"; liquidus 465 °C. Also 520.2 (Al-10Mg casting ingot, quote) | Scalmalloy ingot/waffle (Al-4Mg-0.7Sc-0.5Mn) only | — | — | — | **5 % Li-Al, code 19515**: 1″×6″×12″ slabs, 2-2 ingot (quote) | 6 % Ti-Al sheared pieces (quote) | **Online store: $25.40–27.66 per lb, 5-lb cart minimum ≈ $127–138** (only Al master alloy with a shown price). Custom alloys: "minimum order quantities ranging from five to ten pounds", 4-lb standard sample. Also 99.8 % Mg sticks/ingot $26.70/lb, 5-lb min. | 1-833-4-ALLOYS, [RFQ](https://www.belmontmetals.com/contact-us/), [store](https://www.belmontmetals.com/store/?product_cat=aluminum-master-alloys) |
| **ESPI Metals**, Ashland OR | — (custom melt possible, §2) | — | **Al-10Zr 4N and Al-50Zr 4N pieces, by the gram** | — | — | Al-1Li pieces (too dilute) | **Al-10Ti 3N 5 mm pieces** | No minimum; quote same day | sales@espimetals.com |
| **Milward Alloys**, Lockport NY *(agent; legacy site, expired TLS — phone)* | Mg-Al 25 % and 50 % | custom only ("curiosity elements, e.g. scandium") | 5 / 6 / 10 / 15 % | — | — | 8 % Li | Ti 6/10; TiB 3/1, 5/1, 5/0.2, 10/1 (rod) | Forms include **cut waffle 1 lb** and rod pieces 30 g / 200 g; custom alloys "from a few pounds to 1-½ tons"; quote | 1-800-833-6600, milward@milward.com |
| **AMG Aluminum NA**, Robards KY / Wayne PA *(agent)* | Al-50Mg broken slab; Al-68Mg buttons/waffle | **Al-2Sc waffle, Sc 2.0 ± 0.3 %, Fe/Si ≤ 0.05 %, ≈ 7.7 kg per waffle** | 5 / 10 / 15 % waffle | — | — | — | Ti 6/10; TiBAl waffle, sheared ingot, button, rod | Quote; smallest units "button", "broken slab" — ask for one broken piece | (800) 523-8457, info@amg-al.com |
| **QS Advanced Materials**, Troy MI | — | **Al-Sc master alloy — page shows InStock, low price $200 ("start from $300" in text), 3-week lead** | — | — | **Al-Ce master alloy, "from $300"** | — | — | Form and Sc / Ce % not stated — ask; also Al-La/Nd/Y/Gd | 866-279-7170, Sales@QSAdvancedMaterials.com |
| **Sophisticated Alloys**, Butler PA *(agent; site alloys.com)* | custom | custom | custom | custom | custom | custom | custom | **Arc melter "few grams to ~500 g", VIM to 12 lb; "usually with no minimum order quantity"; "Aluminum Base", "Rare Earths", "Reactive Alloys"** — solid buttons/ingots (this is why they said "no powder") | (724) 789-0158 |
| **ACI Alloys**, San Jose CA *(agent)* | past melts Al/Mg 95/5, 70/30 | Al-Sc named | Al/Zr 90/10 | — | — | Al/Li 0.26–50 % | Al/Ti | Custom arc/VIM buttons; quote | (408) 259-7337, sales@acialloys.com |
| **Ames National Lab MPC**, Ames IA *(agent)* | — | RE expertise | — | RE expertise | RE expertise | — | — | "Special alloy ingots … from several grams to 25 kg"; cost-recovery, not a catalogue vendor | mpc@ameslab.gov |
| **CG Material**, Ontario CA *(agent)* | Al-Mg 5–50 % lump / ingot / waffle | — | — | — | — | Al-Li 2–10 % lump / ingot / waffle | — | "Most products are kept in stock"; quote; origin not stated | (888) 818-7916, sales@cgmaterial.com |
| **Kymera / Reading Alloys**, Robesonia PA *(agent)* | — | — | 40Al-60Zr only | — | — | — | — | Ti-industry hardeners only; **not** the one-stop master-alloy shop assumed in August | — |

### 4.2 US resellers of (mostly China-origin) waffle and ingot — all quote-only, origin unstated

| Vendor | Coverage | Notes |
| --- | --- | --- |
| **Stanford Advanced Materials**, Santa Ana CA *(snippet; site 403)* | AL1631 Al-Mg 5–50 %; AL1641 Al-Sc (2 % waffle per description, "5–70 %" in the spec table — confirm); **AL1653 Al-Zr 5/10/15 % as 200–250 g ingots**; AL5946 Al-Er 5/10 % ingot; AL1624 Al-Ce (pure Ce per SDS); AL1630 Al-Li 5/10 % wire/ingot/waffle; Al-Ti, TiB | The only reseller quoting per-ingot masses (200–250 g Al-Zr); ask for sub-carton lots and country of origin. sales@samaterials.com, (949) 407-8904 |
| **Heeger Materials**, Denver CO *(snippet; site 403)* | Al-Mg 20/25/50/65/75 waffle/bar/shot; Al-Sc2 waffle ("currently unavailable"); Al-Zr 5/10/15; Al-Er; Al-Ce (pure) and Al-La-Ce; Al-Li 2/5; Al-Ti, TiB | Every page says "MOQ 1" (unit undefined) and "price within 24 h"; contradictory stock banners. sales@heegermaterials.com |
| **American Elements**, Santa Monica CA *(snippet; site 403)* | Al-Mg 4/25/50/68; Sc-Al ingot (Sc % unstated); Al-Zr 6/10/15; Al-Er custom; Al-Ce 90/10; Li-Al; TiB | Full coverage on paper; @gage-erickson's experience — no response to any contact — stands. |
| **ALB Materials**, Reno NV *(agent)* | Sputtering targets only; custom-alloy page mentions Al-Li/Mg/Sc/Zr | $300 order minimum; no master-alloy stock. |
| **Reade**, RI *(agent)* | Mg-Al 50/50 and 65/35 — powder page says ingot/pieces also available | RFQ. |

### 4.3 European producers (quote; no US office)

| Vendor | Coverage | Forms / small-lot note |
| --- | --- | --- |
| **KBM Affilips**, Oss NL | **AlMg20 / 25 / 50 / 65 / 75** (50 and 65 "available in the form of broken waffle ingots"); **AlSc2**; AlZr5 / 6 / 10 piglets and waffle; **AlEr on enquiry**; **AlCe(MM)10 — mischmetal**; AlLi2 / AlLi5; AlTi5/6/10, TiBAl rod 100 g / 200 g "Contiform" pieces | Piglet / waffle / 100–200 g rod pieces; custom heats min 200 kg; **no US distributor for Al masters** (Allied Metals handles only their Ni masters). info@kbmaffilips.com, +31 412 681311 |
| **Aleastur**, Avilés ES *(agent)* | AlMg20/50, AlSc2, AlZr5/6/10/15, AlCe10, AlTi, TiB — no AlLi / AlEr | Waffle, coil, sticks; quote. Beck Aluminum (Chagrin Falls OH, 440-684-4848) stocks Aleastur in the US (August finding). |
| **Hoesch Metallurgie**, Düren DE *(agent)* | AlMg25/50/68, AlSc1, AlZr5/10/15, AlCe10, AlLi2, AlTi — no AlEr | Bars, waffle, ingots; **pure Mg 99.9 % pieces 100–300 g and cut pieces 0.5–2 kg**; quote |

### 4.4 Wrought Al-Mg and pure Mg in small solid lots (for an in-house Al-Mg melt)

| Vendor | Item | Lot / price |
| --- | --- | --- |
| Goodfellow USA *(agent)* | Al97/Mg3 rod (5754-type, wrought — carries ~0.5 % Mn/Fe/Si); Mg pellets (rod offcuts); Mg rod | rod from $164–204; Mg pellets from $174; Mg rod from $281; no minimum |
| Kurt J. Lesker *(agent)* | Mg evaporation pellets 99.95 % | 25 g $79 · 100 g $179 · 1 lb $704 |
| Belmont Metals | 99.8 % Mg sticks 1.3″ × 12″ / ingot | $26.70 per lb, 5-lb minimum |
| ESPI Metals | Mg pellets ⅛″ / ¼″ 3N–4N; pieces 3N; ingot 2N8; granules 4N | by the gram (ingot by the lb); quote |
| Hoesch *(agent)* | Mg 99.9 % pieces 100–300 g | quote |
| Evek GmbH, DE *(agent)* | Mg 99.9 % bars | 100 g £9.88 · 1 kg £49.41 |
| Rotometals | **no Mg ingot** — anodes and 25 g ribbon only | — |

---

## 5. Al-Mg — the ranked options

| Rank | Route | What you get | Cost / lot | Why this rank |
| --- | --- | --- | --- | --- |
| 1 | **Belmont Metals 50/50 Mg-Al lumps (6501B)** — order from the web store | Brittle Al-50Mg lumps, 2″ to ¼″, liquidus 465 °C, US stock | **≈ $127–138 for the 5-lb minimum** (≈ 2.3 kg; the campaign needs ≈ 72 g) | The only Al-Mg master in the country with a price and a cart button. Brittle enough to crush and screen in the glovebox — **no atomizer run needed** — and the same lumps can be hand-charged as-is. Excess is cheap insurance. |
| 2 | **Custom Al-35Mg (near-eutectic) button, 250 g** from Sophisticated Alloys (arc melter, "few grams to ~500 g", no minimum), ACI Alloys, or ESPI's own melt shop | Exactly the Mg level you want, in a lump you can atomize or crush; near-eutectic melts at ~450 °C | Quote (expect a few hundred dollars — melt-labour dominated) | Best metallurgical fit for in-house atomization; slower (custom melt lead time). |
| 3 | **AMG Al-50Mg broken slab / Milward Mg-Al 25–50 % cut waffle** | Producer-grade US masters | Quote; Milward sells 1-lb cut waffle | Same material as Belmont from the primary producers; worth one phone call each if Belmont is out of stock. |
| 4 | **KBM AlMg20 / AlMg25 waffle** or Hoesch AlMg25 (EU) | Ductile low-Mg masters — atomize, don't crush | Quote; no US office; §232 tariff applies | Only if a low-Mg (non-brittle) master is specifically wanted. |
| 5 | **Make it from pure Mg + 4N Al in-house** — Mg from ESPI ⅛″ 4N pellets, Lesker 99.95 % pellets (25 g $79), Belmont 99.8 % sticks, or Hoesch 100–300 g pieces | Whatever composition you cast | Cheapest metal cost; one reactive melt | Only after the machine has Al-alloy runs behind it; pure Mg is the wrong first reactive melt (see [quote-review-2026-08.md §4](quote-review-2026-08.md)). |
| — | Resellers (CG Material, Heeger, SAM, American Elements) | Al-Mg 5–75 % waffle / lump | Quote; origin unstated | Fine as backups; ask country of origin and lead time first. |

**Dosing check for the plan:** the Al-Ce-Mg family's 6 wt % Mg needs **12 g of Al-50Mg** (or 17 g of
Al-35Mg) per 100 g batch; the 7xxx-like family's 3 wt % Mg needs 6 g. With a 15 % over-charge the
20-run campaign consumes ≈ 72 g of Al-50Mg in total — one Belmont lump.

---

## 6. The other masters — where each one is actually purchasable in a lab lot

| Master | Best solid source now | Backup | Note |
| --- | --- | --- | --- |
| **Al-10Zr** (300 g) | **ESPI Al-Zr10 % Pieces 4N (Knd2760), by the gram** | Milward / AMG AlZr10 cut waffle; SAM AL1653 200–250 g ingots; KBM AlZr10 piglets; ESPI Al-Zr50 % 4N (crushable) | Solved without a custom crush order. |
| **Al-2Sc** (250 g) | **QS Advanced Materials (Troy MI)** — in stock, "from $200–300", 3-week lead; confirm 2 wt % Sc, form and CoA | AMG Al-2Sc waffle (7.7 kg — ask for a broken piece); KBM / Aleastur AlSc2 (EU); or **make it**: ESPI Sc chips 5 g + 245 g 4N Al | SAM AL1641 and Heeger AlSc2 show discontinued / unavailable flags; Sigma 755672 discontinued. |
| **Al-10Er** (100 g) | **Make it**: Thermo 000111.09 Er pieces 10 g ($145) + 90 g 4N Al, one melt | KBM AlEr (on enquiry, EU); SAM AL5946 Al-Er 5/10 % ingot; Heeger; Amazon/China listings (export-control suspension ends 2026-11-10) | No US stock of Al-Er exists; the in-house melt is faster than any RFQ. |
| **Al-20Ce binary** (250 g) | **Make it**: Thermo 000065.18 Ce ingot 99.8 % 50 g ($170) or ESPI Ce pieces 3N (argon) + 200 g 4N Al | QS Advanced Materials Al-Ce ("from $300"); Aleastur / Hoesch AlCe10 (ask whether MM); SAM AL1624 | KBM's AlCe(MM)10 is mischmetal — avoid. |
| **Al-5Li** (200 g) | **Belmont 5 % Li-Al (19515)** — slabs / 2-2 ingot; ask for the smallest cut | KBM AlLi5 waffle; CG Material Al-Li 2–10 % lump; Milward Al-8Li | ESPI's Al-Li1 % is too dilute for a 2 wt % Li alloy. Ar-pack and dry-box store either way. |
| **Al-10Ti** (75–100 g) | **ESPI Al-Ti10 % 5 mm Pcs 3N (Knc6829), by the gram** | Belmont 6 % Ti-Al sheared pieces; Milward / AMG / KBM AlTi10 | Replaces the −325 mesh Ti powder rejected in August. |
| **Al-Mn / Al-Cr** (not needed) | Belmont 60 % Mn-Al broken slab, 20 % Cr-Al; ESPI Al-Cr33 % pieces | — | Elemental Mn / Cr powder from the August quotes is adequate; listed only for completeness. |

**Consolidation:** with ESPI (Al-Zr, Al-Ti, Sc, Er, Ce, Mg, 4N Al, custom Al-Mg) + Belmont (Al-Mg,
Al-Li) + Thermo (Er, Ce) + QS (Al-Sc, Al-Ce), every master in the plan is covered by four vendors
that all sell small lots to universities — and the Kymera "cast + crush all five" package that was
the August critical path is no longer needed.

---

## 7. Rare earths under a ~$1,000-per-element cap — Sc, Er, Ce

Campaign consumption from [purchase-quantity-model.md](purchase-quantity-model.md), after over-charge
and contingency: **Sc 4.0 g · Er 5.0 g · Ce 37.5 g.**

### 7.1 Scandium — 25 g is a can size, not a minimum

- **ESPI:** every Sc line (Chips 3N Knc6313, Pieces 3N Knc9206, Powder −40 mesh 3N Knd1178) is
  listed "Unit of Measure: Gm" and the ordering page says *no minimum order size, quantity, or
  charge*. Ask for **5 g of chips or pieces** (chips/pieces, not powder — the melt does not care,
  and pieces carry less surface oxide). At the quoted $235/g that is ≈ **$1,175 for 5 g, $940 for
  4 g** — at the cap, but 5× less than the 25 g can.
- **Thermo Fisher — the certified answer:** *Scandium arc-cast pellet, 15.9 mm dia, ≈ 5 g, total
  REO impurities ≤ 0.001 %*, **045118.KF, $414.00 list / $351.65 online** (Fisher AA45118KF, $458.00)
  — [thermofisher.com](https://www.thermofisher.com/order/catalog/product/045118.KF). One pellet is
  the whole campaign's Sc at ≈ $70–92/g, a third of the ESPI rate. The alternative *Scandium pieces,
  distilled dendritic, 99.9 % (REO)*, 039996.04, is 2 g at $615.00 list / $553.65 online ($788.65 on
  Fisher), i.e. $277–394/g. The 5 g "Scandium ingot" 040229.06 is a Sc–Ta (8–12 % Ta) crucible-grade
  ingot — unusable here — and no Sc powder is listed.
- **Collector-market metal (cheap, but no formal CoA):** Metallium (USA) 5 g dendritic 99.5 %
  ≈ $120; Smart Elements (Austria) 10 g > 99.99 % under Ar ≈ $271, 50 g ≈ $625; Nova Elements EU
  5 g 99.95 % ≈ €250. These are one-tenth of ESPI's per-gram price. They are reasonable for the
  *exploratory* Sc runs if the lab is willing to run its own ICP check; they are not what to cite
  in a paper's methods without that check. (Luciteria, PEGuys and Apex Magnets were all sold out.)
- **Al-2Sc master alloy — the route the metallurgy prefers** (oxide already dissolved, see
  [purity-and-particle-size-recommendations.md §5](purity-and-particle-size-recommendations.md)):
  250 g contains 5 g Sc. Small-lot sources found: **QS Advanced Materials (Troy, MI)** Al-Sc master
  alloy — page structured data shows "InStock", low price $200; agent-read text "start from $300", 3-week lead; US stock; KBM Affilips AlSc2 waffle (industrial size, quote);
  an Amazon marketplace "ProMetals" 1 kg AlSc2 ingot listing at ≈ $24 (unverified, no CoA — assay
  before use); Sigma-Aldrich 755672 (≈ 35 g ingot) and Stanford Advanced Materials AL1641 are
  both marked discontinued; Heeger's Al-Sc is "currently unavailable". Chinese direct sales of
  Al-Sc alloys need a MOFCOM licence (Sc has been controlled since April 2025 and was *not* part
  of the November 2025 suspension), so the US-stocked QS route is the practical one.

**Under-$1k Sc options, ranked:**

| Route | Buy | Sc delivered | Cost | Certification |
| --- | --- | ---: | ---: | --- |
| **Thermo 045118.KF arc-cast pellet** | 1 pc | ≈ 5 g | **$352–458** | REO impurities ≤ 0.001 %, CoA |
| QS Advanced Materials Al-Sc master (US) | ~250 g | 5 g | ~$200–600 (quote) | CoA supplied |
| ESPI Sc chips/pieces 3N, re-quoted at 4–5 g | 4–5 g | 4–5 g | ~$940–1,175 | full 3N CoA, US stock |
| Thermo 039996.04 × 2 | 4 g | 4 g | $1,107–1,230 | 99.9 % REO CoA |
| Smart Elements 10 g 99.99 % | 10 g | 10 g | ~$271 + shipping | vendor purity claim, ask for CoA |
| Metallium 5 g 99.5 % | 5 g | 5 g | ~$120 | none |

### 7.2 Erbium — buy 10 g of pieces, not 25 g of powder

- **Thermo Fisher 000111.09, Erbium pieces 99.9 % (REO), 10 g, list $145.00** (online $123.65),
  in stock — [thermofisher.com](https://www.thermofisher.com/order/catalog/product/000111.09);
  50 g is 000111.18 at $495. Thermo's Er *powder* (044169.06, 5 g, $243) is the same money for
  half the metal — pieces are the right form for a melt anyway.
- **ESPI:** Er pieces 1–3 mm (Knd2551), 3–6 mm, 6–12 mm, chips, all by the gram; re-quote **10 g**
  against the $32/g powder line (≈ $320).
- Collector-grade: Metallium Er 35 g ingot ≈ $40, 5 g chunk ≈ $12.
- **Al-Er master:** no US stock found. KBM Affilips (EU) lists AlEr (quote); SAM AL5946 "from
  $100" and Hunan High Broad AlEr20 (MOQ 1 kg) are China-origin — deliverable only while the Er
  export-control suspension lasts (**expires 2026-11-10**). With 10 g of Er pieces in hand, the
  cleaner move is an **in-house Al-10Er melt** (100 g: 10 g Er + 90 g 4N Al) — one atomizer run or
  one hand-charged lump.

### 7.3 Cerium — cheap in every form

- **Thermo Fisher:** Cerium ingot 99 % (REO) 250 g **043977.30, $162** (under mineral oil); Cerium
  ingot 99.8 % (REO) 50 g **000065.18, $170**; 250 g **000065.30, $623** —
  [043977.30](https://www.thermofisher.com/order/catalog/product/043977.30),
  [000065.18](https://www.thermofisher.com/order/catalog/product/000065.18).
- **ESPI:** Cerium Ingot 3N, Pieces 3N (argon can), Chips 3N (argon), Powder −24+40 mesh 3N — by the
  gram; 50 g of argon-packed pieces is the right ask.
- **Binary Al-Ce master:** QS Advanced Materials Al-Ce master "from $300" (US); Epoch / Xinglu /
  Hunan High Broad AlCe20–30 (China, MOQ 1 kg, not export-controlled); KBM's AlCe is mischmetal.
  Or, again, **make it**: 250 g of Al-20Ce = 50 g Ce pieces + 200 g Al in one melt — the surest way
  to get a *binary* master with no La/Nd/Pr.

### 7.4 What the cap buys

| Element | Need | Cheapest certified route | Cost | Cheapest route of any kind |
| --- | ---: | --- | ---: | --- |
| Sc | 4 g | **Thermo 045118.KF arc-cast pellet, ≈ 5 g** | $352–458 | Metallium 5 g ≈ $120 |
| Er | 5 g | Thermo 000111.09, 10 g pieces | $145 list | Metallium 35 g ≈ $40 |
| Ce | 37.5 g | Thermo 000065.18, 50 g 99.8 % ingot | $170 | Thermo 043977.30, 250 g 99 % $162 |

All three fit comfortably under $1k each. Sc + Er + Ce together via the certified Thermo routes lands
at **≈ $670–770** (pellet + 10 g Er pieces + 50 g Ce ingot), versus $6,675 on the August ESPI quote
for Sc + Er alone.

---

## 8. What to add to the next RFQ round (copy-paste)

**ESPI Metals** (sales@espimetals.com) — add to the open quote:

```
Please add to our quote (BYU, research quantities; you note no minimum order):
1. Aluminum-Zr10% Pieces 4N, stock Knd2760 — 300 g
2. Aluminum-Ti10% 5 mm Pieces 3N, stock Knc6829 — 100 g
3. Magnesium Pellets 1/8" 4N — 100 g  (and please state the granule size of Magnesium Granules 4N, K3141)
4. Aluminum Shot 4N (or Pellets 3-8 mesh 4N) — 500 g
5. Scandium Chips 3N, stock Knc6313 — 5 g  (in place of the 25 g -40 mesh powder can)
6. Erbium Pieces 1-3 mm 3N, stock Knd2551 — 10 g  (in place of the 25 g powder)
7. Cerium Pieces 3N, argon-packed — 50 g
8. Custom melt: aluminium-magnesium binary alloy, 35 wt% Mg (Al-35Mg) or 50 wt% Mg,
   cast button/ingot, ~250 g, from 4N Al and 3N+ Mg — feasibility, price and lead time.
Please include a certificate of analysis (Fe, Si, O where measured) with each line.
```

**Belmont Metals** — web store: `50/50 Magnesium Aluminum`, code 6501B, 5 lb (minimum) ≈ $127–138.
RFQ (1-833-4-ALLOYS / contact form): `5% Lithium Aluminum, code 19515 — smallest cut piece
available (target 200–500 g), argon-bagged`.

**Thermo Fisher** — add to the punch-out cart: `000111.09 Erbium pieces 99.9% (REO) 10 g` and
`000065.18 Cerium ingot 99.8% (REO) 50 g` (or `043977.30` 250 g 99 % if 99 % is acceptable).
Only add `039996.04 Scandium pieces 2 g` if ESPI's 5 g Sc price comes back above ~$1,200.

**QS Advanced Materials** (Sales@QSAdvancedMaterials.com, 866-279-7170):
`RFQ: Al-Sc master alloy, 2 wt% Sc, ~250 g, and Al-Ce master alloy (binary, no La/Nd/Pr),
~20 wt% Ce, ~250 g — please state form (ingot/pieces), country of origin, CoA (Sc/Ce, Fe, Si, O),
price and lead time.`

**Sophisticated Alloys** ((724) 789-0158, alloys.com) — re-open the conversation on *solid* buttons,
which is what they do: `Custom arc-melted buttons, ~250 g each: Al-35Mg, Al-20Ce (binary), Al-10Er
(we can supply the Er); 4N Al base; no powder required.`

---

## 9. Verification log and the Pi route

| Source | How verified | Result |
| --- | --- | --- |
| ESPI shop (`shop.espimetals.com`) — element pages, alloy search, 14 product pages | runner, 2026-09-03 | Live; quote-only (no prices, no pack sizes); "Unit of Measure" and stock numbers read from product pages |
| ESPI FAQ + ordering-information pages | runner | "no minimum order size, quantity, or charge"; "small quantities of materials for research" |
| Thermo Fisher product pages (039996.04, 000111.09, 000111.18, 043977.30, 000065.18, 044169.06) | runner (list prices served to the datacenter IP today) | Prices as quoted above; "discontinued" banners on these pages are template boilerplate (same finding as August) |
| Metallium price list (`elementsales.com`) | runner | Sc 5 g $120 · Ce 25 g $44 · Er 35 g $40 |
| QS Advanced Materials Al-Sc page | runner | Structured data: InStock, low price $200 |
| Amazemet rePowder page | runner | d50 80–100 / 45–60 / 35–45 µm at 20 / 40 / 60 kHz |
| Rotometals | runner | Mg sold only as anodes and ribbon — no casting ingot |
| Tailscale → Pi | **not reached** | `tailscale` not installed on the runner; workflow has no connect step; OAuth client rejects 25 candidate tags; API scopes exclude ACL read |

**Making the Pi route work next time.** The CLAUDE.md procedure assumes `claude.yml` joins the
runner to the tailnet before the agent starts. The workflow currently only exports
`TS_OAUTH_CLIENT_ID` / `TS_OAUTH_SECRET` / `TAILNET_ID` into the environment; it needs the official
step, with the tag the OAuth client is allowed to use:

```yaml
- name: Connect to tailnet
  uses: tailscale/github-action@v3
  with:
    oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
    oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
    tags: tag:<the tag granted to this OAuth client>
```

(`.github/workflows` edits are outside what this bot may commit, so this is left as a note.)
Nothing on the Pi was touched this run.

---

## Sources

*Verified from the runner, 2026-09-03:*
ESPI — [home (melting capability)](https://www.espimetals.com/) · [FAQ](https://www.espimetals.com/index.php/faq) · [ordering information (no minimum)](https://www.espimetals.com/index.php/ordering-information) · [custom quote form](https://www.espimetals.com/request-a-custom-quote) · [Al-Zr10 % pieces 4N](https://shop.espimetals.com/knd2760-aluminum-evaporation-materials.html) · [Al-Zr50 % pieces 4N](https://shop.espimetals.com/knd2756-aluminum-evaporation-materials.html) · [Al-Ti10 % pieces](https://shop.espimetals.com/knc6829-aluminum-evaporation-materials.html) · [Al-Cr33 % pieces](https://shop.espimetals.com/knd1027-aluminum-evaporation-materials.html) · [Al-Li1 % pieces](https://shop.espimetals.com/knc9021-aluminum-evaporation-materials.html) · [Al-Cu10 % pieces](https://shop.espimetals.com/knd2761-aluminum-evaporation-materials.html) · [Al-Si11 % pieces](https://shop.espimetals.com/knc6269-aluminum-evaporation-materials.html) · [Mg ingot 2N8](https://shop.espimetals.com/magnesium-ingot-2n8.html) · [Mg pieces 3N](https://shop.espimetals.com/magnesium-pieces-3n.html) · [Mg granules 4N](https://shop.espimetals.com/magnesium-granules-4n.html) · [Sc chips 3N](https://shop.espimetals.com/scandium-chips-3n.html) · [Sc pieces 3N](https://shop.espimetals.com/scandium-pieces-3n-can.html) · [Sc powder −40 mesh](https://shop.espimetals.com/scandium-powder-40-msh-3n-can.html) · [Er pieces 1–3 mm](https://shop.espimetals.com/erbium-pieces-1-3mm-3n.html) · element listings for [Mg](https://shop.espimetals.com/elements/magnesium), [Sc](https://shop.espimetals.com/elements/scandium), [Er](https://shop.espimetals.com/elements/erbium), [Ce](https://shop.espimetals.com/elements/cerium), [Al](https://shop.espimetals.com/elements/aluminum), [Zr](https://shop.espimetals.com/elements/zirconium), [Li](https://shop.espimetals.com/elements/lithium)
Thermo Fisher — [039996.04 Sc pieces](https://www.thermofisher.com/order/catalog/product/039996.04) · [045118.KF Sc arc-cast pellet](https://www.thermofisher.com/order/catalog/product/045118.KF) · [040229.06 Sc–Ta ingot](https://www.thermofisher.com/order/catalog/product/040229.06) · [000111.09 Er pieces](https://www.thermofisher.com/order/catalog/product/000111.09) · [000111.18](https://www.thermofisher.com/order/catalog/product/000111.18) · [044169.06 Er powder](https://www.thermofisher.com/order/catalog/product/044169.06) · [043977.30 Ce ingot 99 %](https://www.thermofisher.com/order/catalog/product/043977.30) · [000065.18 Ce ingot 99.8 %](https://www.thermofisher.com/order/catalog/product/000065.18) · [045001.A1 Al shot 4N](https://www.thermofisher.com/order/catalog/product/045001.A1) · [000632.A3 Al shot 99.9 %](https://www.thermofisher.com/order/catalog/product/000632.A3) · [010571.22 Al ingot 5N](https://www.thermofisher.com/order/catalog/product/010571.22) · [AA0086930 Mg powder (Fisher)](https://www.fishersci.com/shop/products/magnesium-powder-20-100-mesh-99-8-metals-basis-thermo-scientific/AA0086930)
Belmont Metals — [50/50 Magnesium Aluminum (6501B)](https://www.belmontmetals.com/product/5050-magnesium-aluminum/) · [5 % Lithium Aluminum (19515)](https://www.belmontmetals.com/product/5-lithium-aluminum/) · [Aluminum master alloys category](https://www.belmontmetals.com/product-category/aluminum-master-alloys/) · [store](https://www.belmontmetals.com/store/)
KBM Affilips — [aluminium-based range](https://www.kbmaffilips.com/aluminium-based/) · [AlMg](https://www.kbmaffilips.com/aluminium-based/aluminium-magnesium/) · [AlSc](https://www.kbmaffilips.com/aluminium-based/aluminium-scandium/) · [AlLi](https://www.kbmaffilips.com/aluminium-based/aluminium-lithium/) · [AlZr](https://www.kbmaffilips.com/aluminium-based/aluminium-zirconium/) · [AlEr](https://www.kbmaffilips.com/aluminium-based/aluminium-erbium/) · [AlCe(MM)](https://www.kbmaffilips.com/aluminium-based/aluminium-cerium/)
Milward Alloys — [products](https://www.milward.com/products.htm) · [custom alloys](https://www.milward.com/custom.htm) · [contact](https://www.milward.com/contact.htm) (expired TLS certificate)
Others — [Metallium price list](http://www.elementsales.com/pl_element.htm) · [Smart Elements 10 g Sc](https://www.smart-elements.com/shop/10g-scandium-metal-99-99-in-ampoule-under-argon/) · [QS Advanced Materials Al-Sc](https://www.qsrarematerials.com/aluminum-scandium-al-sc-master-alloy-p-667.html) · [Amazemet rePowder](https://amazemet.com/repowder/) · [Rotometals Mg search](https://www.rotometals.com/search.php?search_query=magnesium)

*Read by the research agents, 2026-09-03 (vendor pages unless marked snippet):*
[Belmont 99.8 % Mg](https://www.belmontmetals.com/product/99-8-magnesium/) · [Belmont custom-alloy policy](https://www.belmontmetals.com/custom-alloys/) · [Belmont 520.2](https://www.belmontmetals.com/product/520-2-aluminum-alloy/) · [Belmont Scalmalloy](https://www.belmontmetals.com/product/scalmalloy/) · [AMG master alloys](https://amg-al.com/products/master-alloys/) · [AMG Al-Sc datasheet](https://amg-al.com/wp-content/uploads/2023/11/AMG_Master_Alloys_Scandium_Datasheet.pdf) · [AMG Al-Zr datasheet](https://amg-al.com/wp-content/uploads/2023/11/AMG_Master_Alloys_Zr_Datasheet.pdf) · [Milward selection chart (PDF)](http://www.milward.com/pdf/Milward%20Selection%20Chart.pdf) · [Kymera specialty master alloys](https://kymerainternational.com/product/multi-component-specialty-master-alloys/) · [QS Al-Ce](https://www.qsrarematerials.com/aluminum-cerium-al-ce-master-alloy-p-665.html) · [CG Material Al-Mg](https://cgmaterial.com/products/aluminium-magnesium-master-alloy-al-mg-alloy) · [CG Material Al-Li](https://cgmaterial.com/products/aluminium-lithium-master-alloy-al-li-alloy) · [Sophisticated Alloys vacuum melting](https://www.alloys.com/vacuum-melting-services/index.aspx) · [Sophisticated Alloys custom alloys](https://www.alloys.com/custom-and-specialty-alloys/index.aspx) · [ACI Alloys custom alloy history](https://www.acialloys.com/custom-alloy-history/) · [ACI rare-earth alloys](https://www.acialloys.com/rare-earth-alloys/) · [Ames MPC](https://www.ameslab.gov/dmse/materials-preparation-center) · [Ames MPC — working with the MPC](https://www.ameslab.gov/dmse/materials-preparation-center/working-materials-preparation-center) · [Aleastur master alloys](https://www.aleastur.com/en/master-alloys.php) · [Hoesch master alloys](https://www.hoesch-group.com/en/2022/09/27/master-alloys/) · [Hoesch pure metals](https://www.hoesch-group.com/en/2022/09/27/pure-metals/) · [KBM available forms](https://www.kbmaffilips.com/available-forms/) · [Goodfellow Al97/Mg3 rod](https://www.goodfellow.com/usa/aluminium-magnesium-alloy-rod-al97-mg3-group) · [Goodfellow Mg pellets](https://www.goodfellow.com/usa/magnesium-pellets-group) · [Kurt J. Lesker Mg pellets](https://www.lesker.com/newweb/deposition_materials/depositionmaterials_evaporationmaterials_1.cfm?pgid=mg1) · [Evek Mg bars](https://evek.one/rare-metals/716-magnesium-5gr-5kg-999-metal-element-12-pure-bars-for-alloy-material.html) · [Smart Elements 50 g Sc](https://www.smart-elements.com/shop/pure-scandium-metal-dendritic-crystalline-9999/) · [Nova Elements Sc](https://www.novaelements.com/scandium/) · [Fisher Mg turnings 99+ %](https://www.fishersci.com/shop/products/magnesium-turnings-99-thermo-scientific/AAL0812022) · [Fisher Mg turnings −4 mesh 99.98 %](https://www.fishersci.com/shop/products/magnesium-turnings-4-mesh-99-98-metals-basis-thermo-scientific/AA3619318) · [Fisher Mg granules −4+30 mesh](https://www.fishersci.com/shop/products/magnesium-granules-12-50-mesh-99-8-metals-basis-thermo-scientific/AA0087036) · [Fisher Mg turnings 99.8 %](https://www.fishersci.com/shop/products/magnesium-turnings-99-8-metals-basis-thermo-scientific/AA10232A4) · [Fisher Mg rod 3.3 cm × 30 cm](https://www.fishersci.com/shop/products/magnesium-rod-3-3cm-1-3in-dia-x-30cm-12in-long-99-8-metals-basis-thermo-scientific/AA10231KM) · [Fisher Sc arc-cast pellet](https://www.fishersci.com/shop/products/scandium-arc-cast-pellet-15-9mm-0-63in-dia-thermo-scientific/AA45118KF) · [Fisher Al-Si slug 99:1](https://www.fishersci.com/shop/products/aluminum-silicon-slug-6-35mm-0-25-in-dia-x-6-35mm-0-25-in-length-99-99-metals-basis-thermo-scientific/AA4232230) · [Fisher Al category "alloy" filter](https://www.fishersci.com/us/en/browse/90347107/aluminum-(al)?keyword=alloy) · [Fisher Sc category](https://www.fishersci.com/us/en/browse/90347172/scandium-(sc))
Snippet-only (site blocked bots): [SAM Al-Zr 200–250 g ingots](https://www.samaterials.com/aluminum-master-alloy/1653-aluminum-zirconium-master-alloy.html) · [SAM Al-Sc AL1641](https://www.samaterials.com/aluminum-master-alloy/1641-aluminum-scandium-master-alloy.html) · [SAM Al-Er](https://www.samaterials.com/al5946-aluminum-erbium-alloy.html) · [SAM Al-Li](https://www.samaterials.com/aluminum-master-alloy/1630-aluminum-lithium-master-alloy.html) · [Heeger Al-Mg](https://heegermaterials.com/aluminum-based-master-alloy/1528-aluminium-magnesium-master-alloy.html) · [Heeger Al-Sc](https://heegermaterials.com/aluminum-based-master-alloy/1355-aluminum-scandium-master-alloy-al-sc-alloy.html) · [American Elements Al-Mg](https://www.americanelements.com/aluminum-magnesium-alloy) · [American Elements Sc-Al](https://www.americanelements.com/scandium-aluminum-alloy-113413-85-7) · [Sigma-Aldrich 755672 Al-2Sc](https://www.sigmaaldrich.com/US/en/product/aldrich/755672) · Amazon "ProMetals" AlSc2 / AlMg50 / Al-Ce listings (HTTP 500, unverified)
Export-control background — [Holland & Knight (Apr 2025 Sc controls)](https://www.hklaw.com/en/insights/publications/2025/04/china-imposes-export-controls-on-medium-and-heavy-rare-earth-materials) · [Pillsbury (Nov 2025 suspension, Er)](https://www.pillsburylaw.com/en/news-and-insights/china-suspends-export-controls-certain-critical-minerals-related-items.html) · [The Register, 2026-08-28 (suspension expiry 2026-11-10)](https://www.theregister.com/systems/2026/08/28/datacenters-face-direct-hit-from-china-rare-earth-curbs-as-clock-runs-out-on-escalated-licensing-chokeoff/5293257)

*Caveats:* no supplier was contacted; ESPI, KBM, Milward, AMG, SAM, Heeger and the custom melters are quote-only, so every "quote" line is a catalogue finding, not a price. Belmont's store showed two per-lb figures ($25.40 and $27.66) for 6501B — confirm at checkout. Collector-market Sc/Er/Ce (Metallium, Smart Elements, Nova) carries no formal CoA. Thermo/Fisher web prices are list or online-exclusive prices before the BYU punch-out discount.
