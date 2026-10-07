# Supplier links by element (consolidated, verified 2026-10-07)

One place for every supplier link the issue-161 threads have turned up, organised by element
and by the *form* the element can arrive in. Every link was fetched on 2026-10-07 from the
lab's Pi 5 stream cam (residential IP) with a rate-limited `curl` run
(`docs/pi-tooling.md`); the status column records what came back. Prices are the latest
figures quoted or read in this issue (August–October 2026) and are planning numbers only.

How to read the **form** column against the campaign plan:

- **Powder** — feeds the auger doser; coarse (150–300 µm) preferred, anything sold as
  "−325 mesh" is all fines (see `quote-review-2026-08.md`).
- **Pieces / chips / ingot** — hand-charged into the aluminium cup
  (`edison-corroboration-2026-09.md` §1); the right form for small, reactive or expensive
  additions.
- **Master alloy** — dilutes the element in Al. Its non-Al fraction *y* decides whether the
  design space stays reachable: see `design-space-and-minimum-feedstock-set-2026-10.md`
  for the per-element floor on *y*. Commercial masters are listed with their *y*.
- **In-house** — arc-melt (#223) or induction-melt a custom master from the pieces above.

Status key: ✅ 200 from the Pi · 🚫 blocked from the Pi (see note) · ❌ unreachable.

## Aluminium base

| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder, 99.7 %, −50+100 mesh | AEE / Micron Metals **AL-111**, 5 lb ≈ $97 | [micronmetals.com](https://micronmetals.com/product/aluminum-powder-coarse/) | ✅ | Only off-the-shelf 150–300 µm Al; quoted 2026-08 at $19.49/lb |
| Pellets, 99.99 % | AEE **AL-130** ¼–½″ | [micronmetals.com](https://micronmetals.com/product/aluminum-metal-powder/) | ✅ | 4N, hand-charge |
| Shot 9.5 mm, 99.99 %, 1 kg | Thermo **045001.A1**, $103 list / $87.65 online | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/045001.A1) | ✅ | 4N base for cups or re-atomization |
| Shot ≤ 15 mm, 99.9 % | Thermo **000632.A3** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/000632.A3) | ✅ | |
| Ingot, 99.999 % | Thermo **010571.22** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/010571.22) | ✅ | 5N |
| Shot / pellets / ingot, 4N–5N | ESPI aluminium page | [shop.espimetals.com](https://shop.espimetals.com/elements/aluminum) | ✅ | By the gram, no minimum |
| Powder, 99.7 %, H-series | Valimet (2 kg 4N quote pending since 2026-08-31) | [datasheet](https://valimet.com/wp-content/uploads/2021/08/Aluminum-H-Series-Data-Sheet-.pdf) · [RFQ](https://valimet.com/request-quote) · [AM powders](https://valimet.com/additive-manufacturing-and-cold-spray-powders/) | ✅ | Toll atomization of custom alloys; signed with APWORKS for Scalmalloy |
| Ingot, 99.8 % P0610, 52 lb $312.56 | Rotometals | [rotometals.com](https://www.rotometals.com/aluminum-ingot-99-8-min-52-pounds-p0610-standard-ingot/) | ✅ | Primary-grade base (industry recipe) |
| Rod, 99.999 %, Ø20/12/10 × 100 mm | Goodfellow via Sigma `GF36586042` / `GF86572042` / `GF98449576` | [goodfellow.com](https://www.goodfellow.com/usa/aluminium-magnesium-alloy-rod-al97-mg3-group) (group page) | ✅ / Sigma 🚫 | For cups (#222); Sigma blocks the Pi, order through the BYU account |
| Rod 4N–6N | High Purity Aluminum (highpurityaluminum.com/products/rod) | — | not checked | From the 2026-09-17 rod search |
| Rod 6063, 3/4″ `1640T16`, 1/2″ `1640T14`, 3/8″ `1640T13` | McMaster-Carr | — | ✅ (McMaster part pages load from the Pi) | Not commercially pure; cups only if 4N is unavailable |
| Powder 99.9 %, 44 µm, 1 lb $73 | McMaster `1402N19` | — | ✅ | Fine; reference only |

## Solutes, one block per element

### Mn
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder −100 mesh, 3N, 100 g **$35** | ESPI **KNC8086** (quoted, no CoA on that lot) | [shop.espimetals.com/elements/manganese](https://shop.espimetals.com/elements/manganese) | ✅ (site) | Ordered 2026-09 plan |
| Master Al-60Mn lumps | Belmont Metals | [belmontmetals.com](https://www.belmontmetals.com/product-category/aluminum-master-alloys/) | ✅ | y = 0.60, brittle |
| Master AlMn | KBM Affilips | [kbmaffilips.com](https://www.kbmaffilips.com/aluminium-based/) | ✅ | EU, via Allied Metals |
| Powder 97 %, $190 | McMaster | — | ✅ | Worse than ESPI on purity and price |

### Cr
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder −325 mesh, 3N+, 100 g **$65** | ESPI (quoted) | [shop.espimetals.com/elements/chromium](https://shop.espimetals.com/elements/chromium) | ✅ (site) | Fines only; hand-weigh into the cup |
| Powder −100+325 mesh, 99.97 %, 50 g $425 | Thermo/Fisher **035668-18** | [thermofisher.com/…/035668.18](https://www.thermofisher.com/order/catalog/product/035668.18) | ✅ (Thermo) / Fisher 🚫 | 13× ESPI per gram |
| Powder, coarse cuts | AEE chromium metal powder | [micronmetals.com](https://micronmetals.com/product/chromium-metal-powder/) | ✅ | Ask for −60+100 |
| Master **Al-Cr33 % pieces 3N** (y = 0.33) | ESPI **Knd1027** | [shop.espimetals.com](https://shop.espimetals.com/knd1027-aluminum-evaporation-materials.html) | ✅ | Brittle intermetallic, crushable |
| Master Al-20Cr | Belmont | [belmontmetals.com store](https://www.belmontmetals.com/store/?product_cat=aluminum-master-alloys) | ✅ | y = 0.20 |

### Zr
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Master **Al-Zr10 % pieces 4N** (y = 0.10) | ESPI **Knd2760** | [shop.espimetals.com](https://shop.espimetals.com/knd2760-aluminum-evaporation-materials.html) | ✅ | Ductile α-Al + Al₃Zr: charge as lumps |
| Master **Al-Zr50 % pieces 4N** (y = 0.50) | ESPI **Knd2756** | [shop.espimetals.com](https://shop.espimetals.com/knd2756-aluminum-evaporation-materials.html) | ✅ | Brittle → crush to 150–300 µm in the glovebox; 4 g delivers 2 wt.% Zr |
| Elemental Zr (pieces, sponge) | ESPI zirconium page | [shop.espimetals.com/elements/zirconium](https://shop.espimetals.com/elements/zirconium) | ✅ | Pieces OK; **never Zr powder** (class 4.2) |
| Master AlZr5/6/10 piglets | KBM Affilips | [kbmaffilips.com](https://www.kbmaffilips.com/aluminium-based/aluminium-zirconium/) | ✅ | EU |
| Master Al-Zr ingots 200–250 g | Stanford Advanced Materials 1653 | [samaterials.com](https://www.samaterials.com/aluminum-master-alloy/1653-aluminum-zirconium-master-alloy.html) | ✅ | Origin unstated |
| Master AlZr datasheet | AMG Aluminum | [amg-al.com PDF](https://amg-al.com/wp-content/uploads/2023/11/AMG_Master_Alloys_Zr_Datasheet.pdf) · [products](https://amg-al.com/products/master-alloys/) | ✅ | US producer; industrial lot sizes |

### Mg
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Pieces ½″ and down, 3N, 100 g $230 | ESPI (quoted) | [shop.espimetals.com](https://shop.espimetals.com/magnesium-pieces-3n.html) | ✅ | Current plan: hand-charge |
| Granules 4N | ESPI **K3141** | [shop.espimetals.com](https://shop.espimetals.com/magnesium-granules-4n.html) | ✅ | Granule size unpublished — ask |
| Ingot 2N8 (by the lb) | ESPI | [shop.espimetals.com](https://shop.espimetals.com/magnesium-ingot-2n8.html) · [Mg page](https://shop.espimetals.com/elements/magnesium) | ✅ | Feed for in-house Al-Mg |
| Sticks 99.8 %, $26.70/lb | Belmont | [belmontmetals.com](https://www.belmontmetals.com/product/99-8-magnesium/) | ✅ | |
| **Master Al-50Mg lumps** (y = 0.50), code 6501B ≈ $25–28/lb, 5 lb min | Belmont | [belmontmetals.com](https://www.belmontmetals.com/product/5050-magnesium-aluminum/) | ✅ | Brittle (β/γ), crushable; first reactive melt if atomizing |
| Atomized Mg powder 20–1000 µm (inert gas) | Luxfer Magtech / Hart Metals, (800) 503-4483 | [luxfermagtech.com](https://luxfermagtech.com/products/magnesium-products/) | ✅ | US mil-spec house; −50+100 mesh possible |
| Atomized Mg powder, flexible PSD; also Ti | Coogee USA (Ottawa IL) | [coogee.com](https://coogee.com/magnesium-powder/) | ✅ | One call covers Mg and Ti |
| Powder −20+100 mesh 99.8 % (no source), granules −12+50, turnings | Thermo/Fisher AA0086930, AA0087036, AA3619318, AA10232A4 | Fisher 🚫 · [Thermo 000869.30](https://www.thermofisher.com/order/catalog/product/000869.30) | Fisher 🚫 | "No source" on the 2026-08 quote |
| Pellets 99.95 %, 25 g $79 | Kurt J. Lesker (evaporation pellets) | [lesker.com](https://www.lesker.com/newweb/deposition_materials/depositionmaterials_evaporationmaterials_1.cfm?pgid=mg1) | ✅ | |
| Pellets | Goodfellow | [goodfellow.com](https://www.goodfellow.com/usa/magnesium-pellets-group) | ✅ | |
| Bars 99.9 %, 100 g £9.88 | Evek (DE) | [evek.one](https://evek.one/rare-metals/716-magnesium-5gr-5kg-999-metal-element-12-pure-bars-for-alloy-material.html) | ✅ | Import |
| Masters AlMg20/25/50/65/75 | KBM Affilips | [kbmaffilips.com](https://www.kbmaffilips.com/aluminium-based/aluminium-magnesium/) | ✅ | 50 and 65 as broken waffle |
| Masters Al-Mg | Heeger · CG Material · American Elements | [heeger](https://heegermaterials.com/aluminum-based-master-alloy/1528-aluminium-magnesium-master-alloy.html) · [cgmaterial](https://cgmaterial.com/products/aluminium-magnesium-master-alloy-al-mg-alloy) · [americanelements](https://www.americanelements.com/aluminum-magnesium-alloy) | ✅ | Resellers, origin unstated |
| Masters Mg-Al 25/50 %, Al-Zr, Al-8Li | Milward (Lockport NY) | [selection chart PDF](http://www.milward.com/pdf/Milward%20Selection%20Chart.pdf) | PDF ✅ · site ❌ (TLS expired) | Phone them |
| Mg sources, search | Rotometals | [rotometals.com](https://www.rotometals.com/search.php?search_query=magnesium) | ✅ | |

### Si
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Already in the lab | McMaster Si (sgbaird, 2026-10-07) | — | — | Check the certificate on the jar |
| Powder −100 mesh 99.9 %, 100 g $106 | Thermo/Fisher **000311-22** | [thermofisher.com/…/000311.22](https://www.thermofisher.com/order/catalog/product/000311.22) | Thermo ✅ / Fisher 🚫 | Quote expired; ETA was 9/18 |
| **Powder −50+100 mesh, 5N, 250 g $405** | Chemsavers | [chemsavers.com](https://chemsavers.com/great-deals/silicon-metal-powder-50-100-mesh-99-999-metals-basis-electronic-grade-certified-250g/) | ✅ | Exact target cut, certified |
| Powder SI-111 (4N, 45–90 µm) · SI-122 (5N, 45–150 µm) · SI-113-F (3N, 15–53 µm, $156/lb) | AEE | [micronmetals.com](https://micronmetals.com/product/silicon-powder-2) | ✅ | Rides the AL-111 order |
| Master Al-Si 1–25 % pieces 4N/5N; **Al-Si11 % 5–10 mm 4N Knc6269** (y = 0.11) | ESPI | [shop.espimetals.com](https://shop.espimetals.com/knc6269-aluminum-evaporation-materials.html) | ✅ | Near-eutectic lump, melts at 577 °C |
| Al-Si slug 4N | Thermo AA4232230 (Fisher) | Fisher 🚫 | 🚫 | |
| Al 4047 benchmark rods (12 % Si) | Bartosz / AMAZEMET | — | — | Si carrier for the Al-Si-Mg-Cu family (`mcmaster-and-stock-alternatives-2026-10.md`) |

### Cu
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder spherical −100+325 mesh, 99.9 %, 100 g $57.80 | Thermo/Fisher **042623-22** | [thermofisher.com/…/042623.22](https://www.thermofisher.com/order/catalog/product/042623.22) | Thermo ✅ | Quote expired; re-quote |
| Powder 99.9 %, 44 µm, 1 lb $90.72 | McMaster **1402N18** | [mcmaster.com/1402N18](https://www.mcmaster.com/1402N18/) | ✅ | No certificate listed |
| Master **Al-Cu10 % pieces 4N** (y = 0.10) · Al-Cu50 % | ESPI **Knd2761** | [shop.espimetals.com](https://shop.espimetals.com/knd2761-aluminum-evaporation-materials.html) | ✅ | |
| Cu wire/rod, certified | McMaster (99 wire, 186 rod products) | — | ✅ | Cut to weight for the cup |

### Ti
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder −325 mesh, 2N7, 200 g $130 | ESPI (quoted; ordered per the 2026-09 plan) | [shop.espimetals.com/elements/titanium](https://shop.espimetals.com/elements/titanium) | ✅ (site) | Class 4.2 fines: glovebox only |
| Powder HDH −100 mesh, 99.7 %, $70/lb (ask for −60+100) | AEE **TI-109** | [micronmetals.com](https://micronmetals.com/product/titanium-metal-powder-2/) | ✅ | |
| Powder −60+100 mesh 99.5 % (no source) · spherical −150 mesh 99.9 % | Thermo/Fisher AA4310522 · AA4154522 | [thermofisher.com/…/043105.22](https://www.thermofisher.com/order/catalog/product/043105.22) | Thermo ✅ | |
| **Master Al-Ti10 % 5 mm pieces 3N** (y = 0.10) | ESPI **Knc6829** | [shop.espimetals.com](https://shop.espimetals.com/knc6829-aluminum-evaporation-materials.html) | ✅ | Replaces Al-5Ti-1B rod |
| Master Al-6Ti pieces | Belmont | [belmontmetals.com](https://www.belmontmetals.com/product-category/aluminum-master-alloys/) | ✅ | y = 0.06 |
| Atomized Ti powder | Coogee USA | [coogee.com](https://coogee.com/magnesium-powder/) | ✅ | Ask with the Mg quote |

### Fe
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder −20 mesh, 99.9 %, 250 g $122 | Thermo/Fisher **047355-30** | [thermofisher.com/…/047355.30](https://www.thermofisher.com/order/catalog/product/047355.30) | Thermo ✅ | Sieve to −50+100; quote expired |
| Powder 99.9 %, 5 µm, 1 lb $85.50 | McMaster **1402N25** | [mcmaster.com/1402N25](https://www.mcmaster.com/1402N25/) | ✅ | Combustible fines; glovebox |
| Master Al-Fe | ESPI (ask) · KBM | [kbmaffilips.com](https://www.kbmaffilips.com/aluminium-based/) | ✅ | Al-5Fe liquidus ≈ 780 °C (COST507) |

### Ni
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder −60+170 mesh, 99.7 %, 100 g $68.90 | Thermo/Fisher **010579-22** | [thermofisher.com/…/010579.22](https://www.thermofisher.com/order/catalog/product/010579.22) | Thermo ✅ | Quote expired |
| Powder 99.9 %, 3 µm, 1 lb $143 | McMaster **1402N24** | [mcmaster.com/1402N24](https://www.mcmaster.com/1402N24/) | ✅ | Respirable; glovebox |
| Nickel 200 rod Ø1/2″ $75.62 · Ø3/4″ $109 | McMaster **9136K23** · **9136K25** | [9136K23](https://www.mcmaster.com/9136K23/) · [9136K25](https://www.mcmaster.com/9136K25/) | ✅ | Slice 0.5–1 mm discs; Fe ≤ 0.40 % |
| Slugs 99.995 %, ~1.8 g, 25 for $230 | Thermo **042331.QK** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/042331.QK) | ✅ | For a 5N base |
| Nickel 270 (99.98 %) bulletin | Special Metals | [PDF](https://www.specialmetals.com/documents/technical-bulletins/nickel-270.pdf) | ✅ | |
| Master Al-20Ni | Belmont | [belmontmetals.com](https://www.belmontmetals.com/product-category/aluminum-master-alloys/) | ✅ | y = 0.20 |

### Ce
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Ingot 99.8 %, 50 g $170 | Thermo **000065.18** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/000065.18) | ✅ | Clean the oxide skin before charging |
| Ingot 99 %, 250 g $162 | Thermo **043977.30** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/043977.30) | ✅ | |
| Ingot / pieces / chips | ESPI cerium page | [shop.espimetals.com/elements/cerium](https://shop.espimetals.com/elements/cerium) | ✅ | By the gram |
| Master AlCe(MM)10 — **mischmetal**, not binary | KBM Affilips | [kbmaffilips.com](https://www.kbmaffilips.com/aluminium-based/aluminium-cerium/) | ✅ | Ask for binary |
| Master Al-Ce (in stock, ~3 weeks) | QS Advanced Materials (Troy MI) | [qsrarematerials.com](https://www.qsrarematerials.com/aluminum-cerium-al-ce-master-alloy-p-665.html) | ✅ | |
| Master Al-10Ce | American Elements | [americanelements.com](https://americanelements.com/aluminum-cerium-alloy) | not checked | Unresponsive to small orders (2026-08) |
| Master AlCe10 ($1.8/kg, tonne lots) | Hebei Shenghua (CN) | — | not checked | Ce is *not* under the 2025 export controls, but tonne lots |
| Master Al-La-Ce AC6642 | Stanford Advanced Materials | [samaterials.com](https://www.samaterials.com/product/ac6642-aluminum-lanthanum-cerium-master-alloy-al-la-ce-alloy.html) | not checked | Contains La |

### Sc
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| **Chips 3N** (dissolve faster than pellets) | ESPI **Knc6313** | [shop.espimetals.com](https://shop.espimetals.com/scandium-chips-3n.html) · [Sc page](https://shop.espimetals.com/elements/scandium) | ✅ | $235/g quoted; no minimum — ask for 4–5 g |
| Pieces 3N (can) | ESPI **Knc9206** | [shop.espimetals.com](https://shop.espimetals.com/scandium-pieces-3n-can.html) | ✅ | |
| Powder −40 mesh 3N (can) | ESPI **Knd1178** | [shop.espimetals.com](https://shop.espimetals.com/scandium-powder-40-msh-3n-can.html) | ✅ | 25 g = $5,875; 3–5 wk |
| Arc-cast pellet ≈ 5 g, $352–458 | Thermo **045118.KF** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/045118.KF) | ✅ (Fisher 🚫) | Slow to dissolve (>1 h at 800 °C) — chips preferred |
| Dendritic pieces 2 g | Thermo **039996.04** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/039996.04) | ✅ | $554–789 |
| "Scandium ingot" 5 g | Thermo 040229.06 | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/040229.06) | ✅ | Sc–Ta crucible alloy — **do not buy** |
| 10 g 99.99 % ampoule ≈ $271 · dendritic | Smart Elements (AT) | [ampoule](https://www.smart-elements.com/shop/10g-scandium-metal-99-99-in-ampoule-under-argon/) · [dendritic](https://www.smart-elements.com/shop/pure-scandium-metal-dendritic-crystalline-9999/) | ✅ | Collector grade, no CoA |
| Sc metal | Nova Elements | [novaelements.com](https://www.novaelements.com/scandium/) | ✅ | Collector grade |
| **Master Al-2Sc** (y = 0.02) datasheet | AMG Aluminum | [PDF](https://amg-al.com/wp-content/uploads/2023/11/AMG_Master_Alloys_Scandium_Datasheet.pdf) | ✅ | ~7.7 kg waffle — industrial |
| Master AlSc2 | KBM Affilips | [kbmaffilips.com](https://www.kbmaffilips.com/aluminium-based/aluminium-scandium/) | ✅ | |
| Master Al-Sc, from ~$200–300, 3 wk | QS Advanced Materials | [qsrarematerials.com](https://www.qsrarematerials.com/aluminum-scandium-al-sc-master-alloy-p-667.html) | ✅ | US stock |
| Master Al-Sc | SAM 1641 · Heeger 1355 · American Elements | [samaterials](https://www.samaterials.com/aluminum-master-alloy/1641-aluminum-scandium-master-alloy.html) · [heeger](https://heegermaterials.com/aluminum-based-master-alloy/1355-aluminum-scandium-master-alloy-al-sc-alloy.html) · [americanelements](https://www.americanelements.com/scandium-aluminum-alloy-113413-85-7) | ✅ | SAM listed discontinued in 2026-09 |
| Sc₂O₃ → Al-Sc (North America) | Rio Tinto Element North 21 | [riotinto.com](https://www.riotinto.com/en/can/news/releases/2022/rio-tinto-becomes-the-first-producer-of-scandium-oxide-in-north-america) | ✅ | Non-China supply |

### Li
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| **Master Al-5Li slabs/ingot** (y = 0.05), code 19515 | Belmont | [belmontmetals.com](https://www.belmontmetals.com/product/5-lithium-aluminum/) | ✅ | Small lots |
| Master AlLi2/5 (Al-10Li on enquiry) | KBM Affilips | [kbmaffilips.com](https://www.kbmaffilips.com/aluminium-based/aluminium-lithium/) | ✅ | |
| Master Al-Li 5/10 | SAM 1630 · CG Material | [samaterials](https://www.samaterials.com/aluminum-master-alloy/1630-aluminum-lithium-master-alloy.html) · [cgmaterial](https://cgmaterial.com/products/aluminium-lithium-master-alloy-al-li-alloy) | ✅ | Origin unstated |
| Master Al-8Li | Milward | [selection chart](http://www.milward.com/pdf/Milward%20Selection%20Chart.pdf) | PDF ✅ | |
| Master AlLi ingot | AMG (Wayne PA) | [amg-al.com](https://amg-al.com/products/master-alloys/) | ✅ | |
| Al-Li1 % pieces (too dilute) | ESPI Knc9021 · Li page | [shop.espimetals.com](https://shop.espimetals.com/knc9021-aluminum-evaporation-materials.html) · [Li page](https://shop.espimetals.com/elements/lithium) | ✅ | **Never elemental Li** |

### Er
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| **Powder −40 mesh 99.9 % (REO), 25 g $770.65**, under Ar | Thermo **044169.14** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/044169.14) | ✅ | Sets the Er ceiling at ~3 wt.% (`erbium-bounds-and-lot-size.md`) |
| Same, 5 g $218.65 | Thermo **044169.06** | [thermofisher.com](https://www.thermofisher.com/order/catalog/product/044169.06) | ✅ | |
| Pieces 99.9 % (REO), 10 g $145 · 50 g $495 | Thermo **000111.09** · **000111.18** | [10 g](https://www.thermofisher.com/order/catalog/product/000111.09) · [50 g](https://www.thermofisher.com/order/catalog/product/000111.18) | ✅ | |
| Pieces 1–3 mm 3N (by the gram) · powder −40 mesh 3N 25 g $800 | ESPI | [pieces](https://shop.espimetals.com/erbium-pieces-1-3mm-3n.html) · [Er page](https://shop.espimetals.com/elements/erbium) | ✅ | 3–5 wk; export-control window closes 2026-11-10 |
| Master AlEr (only non-China producer) | KBM Affilips | [kbmaffilips.com](https://www.kbmaffilips.com/aluminium-based/aluminium-erbium/) | ✅ | |
| Master Al-Er 5/10 | SAM AL5946 | [samaterials.com](https://www.samaterials.com/al5946-aluminum-erbium-alloy.html) | ✅ | |
| Er metal (grams to kg) | Ames Lab Materials Preparation Center | [ameslab.gov](https://www.ameslab.gov/dmse/materials-preparation-center) · [how to work with MPC](https://www.ameslab.gov/dmse/materials-preparation-center/working-materials-preparation-center) | ✅ | Cost recovery; also custom melts |

### Zn
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder −100 mesh, 4N, 100 g **$45** | ESPI (quoted; plan) | [shop.espimetals.com/elements/zinc](https://shop.espimetals.com/elements/zinc) | ✅ (site) | UN 1436 class 4.3 — never wet a spill |
| Powder −140+325 mesh 99.9 %, 100 g $219 | Thermo/Fisher **039694-22** | [thermofisher.com/…/039694.22](https://www.thermofisher.com/order/catalog/product/039694.22) | Thermo ✅ | 46-day lead |
| Granules −30 mesh 3N8 | ESPI | [Zn page](https://shop.espimetals.com/elements/zinc) | ✅ | Screen to −50+100 |
| Master Al-Zn drops | ESPI | [Zn page](https://shop.espimetals.com/elements/zinc) | ✅ | |

### Sn
| Form | Product | Link | Status | Notes |
| --- | --- | --- | --- | --- |
| Powder −325 mesh, 3N, 100 g **$40** | ESPI (quoted; plan) | [shop.espimetals.com/elements/tin](https://shop.espimetals.com/elements/tin) | ✅ (site) | |
| Powder −40 mesh, 5N, 100 g $450 | ESPI | [Sn page](https://shop.espimetals.com/elements/tin) | ✅ | 5N buys nothing at 1 wt.% |
| Powder −100 mesh 99.85 %, 100 g $68 | Thermo/Fisher **000941-22** | [thermofisher.com/…/000941.22](https://www.thermofisher.com/order/catalog/product/000941.22) | Thermo ✅ | |
| Master Al-Sn15 % | ESPI | [Al page](https://shop.espimetals.com/elements/aluminum) | ✅ | y = 0.15 |

### Cs (candidate; see the Edison section of the design-space report)
Cesium melts at 28 °C and boils at 671 °C, 11 °C above the melting point of aluminium, so
an open-crucible Al melt at 700–1000 °C cannot hold it. No link is listed until the Edison
query settles whether any Al-Cs alloying route exists. If one does, the forms are sealed
metal ampoules (Thermo/Alfa, ESPI, Strem, American Elements) or compounds (CsF, Cs₂CO₃).

## Custom and multi-element masters, and services

| Who | What | Link | Status |
| --- | --- | --- | --- |
| Belmont Metals (Brooklyn NY), 1-833-4-ALLOYS | Al master-alloy range, custom alloys from 5–10 lb, feedstock for powder makers, Scalmalloy | [masters](https://www.belmontmetals.com/product-category/aluminum-master-alloys/) · [custom](https://www.belmontmetals.com/custom-alloys/) · [feedstock article](https://www.belmontmetals.com/the-secret-to-perfect-powder-it-starts-with-the-feedstock/) · [Scalmalloy](https://www.belmontmetals.com/product/scalmalloy/) · [contact](https://www.belmontmetals.com/contact-us/) | ✅ |
| ESPI Metals (Ashland OR), sales@espimetals.com | Elements by the gram, cast Al binaries, in-house induction and arc melting, no minimum | [ordering](https://www.espimetals.com/index.php/ordering-information) · [custom quote](https://www.espimetals.com/request-a-custom-quote) · [FAQ](https://www.espimetals.com/index.php/faq) | ✅ |
| Sophisticated Alloys (Butler PA), (724) 789-0158 | Arc/VIM buttons "from a few grams"; **no powders** | [custom](https://www.alloys.com/custom-and-specialty-alloys/index.aspx) · [VIM](https://www.alloys.com/vacuum-melting-services/index.aspx) | ✅ |
| ACI Alloys | Custom Al-Sc, Al-Zr, Al-Li, Al-Mg buttons; rare-earth alloys | [history](https://www.acialloys.com/custom-alloy-history/) · [RE alloys](https://www.acialloys.com/rare-earth-alloys/) | ✅ |
| Ames Lab MPC | Custom melts, high-purity RE metals, cost recovery | [MPC](https://www.ameslab.gov/dmse/materials-preparation-center) | ✅ |
| KBM Affilips (NL; US agent Allied Metals, info@alliedmet.com) | AlSc2, AlZr, AlEr, AlLi, AlMg, AlCe(MM) | [range](https://www.kbmaffilips.com/aluminium-based/) · [forms](https://www.kbmaffilips.com/available-forms/) | ✅ |
| AMG Aluminum (KY/PA) | Al-2Sc, AlZr, Al-Mg, AlLi | [masters](https://amg-al.com/products/master-alloys/) | ✅ |
| Hoesch (DE) | Masters, pure metals 100–300 g pieces | [masters](https://www.hoesch-group.com/en/2022/09/27/master-alloys/) · [pure metals](https://www.hoesch-group.com/en/2022/09/27/pure-metals/) | ✅ |
| Aleastur (ES) | Masters | [aleastur.com](https://www.aleastur.com/en/master-alloys.php) | ✅ |
| Kymera / Reading Alloys | Multi-component masters (Ti-industry hardeners) | [kymerainternational.com](https://kymerainternational.com/product/multi-component-specialty-master-alloys/) | ✅ |
| Milward (Lockport NY) | Mg-Al, Al-Zr, Al-Li, Al-Ti; cut waffle; custom from a few lb | [selection chart PDF](http://www.milward.com/pdf/Milward%20Selection%20Chart.pdf) | PDF ✅, site ❌ |
| Valimet (Stockton CA), (209) 444-1600 | Toll atomization, custom PSD, 4N feed | [RFQ](https://valimet.com/request-quote) | ✅ |
| BAM (DE) | **BAM-M319** certified Scalmalloy powder 100 g €267 — benchmark | [webshop](https://webshop.bam.de/webshop_en/bam-m319.html) · [report](https://webshop.bam.de/media/wysiwyg/Kategorien/Referenzmaterialien/Nichteisenmetalle/Aluminium/Berichte/bam_m319repe.pdf) | ✅ |
| AMAZEMET | rePOWDER (induction 1300 °C; arc option) | [repowder](https://amazemet.com/repowder/) | ✅ |

## Blocked or dead on 2026-10-07

- **fishersci.com** — HTTP 403 to `curl`; an Akamai behavioural challenge to headless Chromium
  and to a *headed* Chromium on the Pi's Xvfb display with xdotool mouse input (the
  press-and-hold widget never renders). All 11 Fisher URLs in the prior docs are affected.
  The matching **thermofisher.com** catalogue pages all return 200, so links above point there;
  the Fisher SKUs are the same numbers with the `AA` prefix and no dot.
- **sigmaaldrich.com** — connection refused/blocked from the Pi (Akamai), as before.
- **milward.com** — TLS certificate expired, site unreachable; the selection-chart PDF over
  plain HTTP still loads. Phone (716) 434-1811 from earlier docs.
- Not re-checked (not in the prior docs' link set): highpurityaluminum.com, americanelements.com
  Al-Ce page, Hebei Shenghua, SAM Al-La-Ce.
