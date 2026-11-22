# Colour coding: bill of materials and shopping list

Sterling, PR #377, 2026-11-22: "blue and orange as mentioned are fine for now. Use the raspberry Pi to look up specific
codes, items, prices, sellers, lead times, and any other pertinent information related to the above suggestions and
searches. Come up with a full bill of materials and shopping list for this."

**Where everything is:**

- **The lines:** [`out/colour/bom/`](../out/colour/bom/), one JSON file per group. Each line has its maker's part
  number, the seller's SKU, the page its price was read from, the stock or lead time that page showed, and where its
  quantity comes from.
- **The script:** [`colour_bom.py`](../colour_bom.py) totals the lines and writes four files:
  - the full BOM by group, [`out/colour/bom.md`](../out/colour/bom.md), with the notes on every line;
  - the [shopping list by seller](../out/colour/shopping_list.md), one table per order;
  - [`out/colour/bom.csv`](../out/colour/bom.csv), for a purchasing spreadsheet;
  - [`out/colour/bom_totals.json`](../out/colour/bom_totals.json).
- **The scheme itself:** [`colour_coding.md`](colour_coding.md).

## The short version

| Group | Now | Soon | Optional | Lines to quote |
|---|---|---|---|---|
| Alloy-family marking, tools and containers | $684.27 | $126.00 | $248.40 | 3 |
| Labels and markers | $140.92 | $746.06 | $578.00 | 2 |
| Floor marking | $933.30 | $805.00 | $788.78 | 0 |
| Stack lights | $0.00 | $9,988.44 | $0.00 | 0 |
| A second kit for the Cu family | $173.00 | $2,234.45 | $603.00 | 9 |
| **All** | **$1,931.49** | **$13,899.95** | **$2,218.18** | **14** |

- **Now:** what starting the scheme needs.
- **Soon:** wanted when a station or the second family's kit comes on line.
- **Optional:** a convenience or an upgrade.

Prices are per pack at quantity 1 on 2026-11-22, before shipping and tax.

- **Most of the "now" money is floor tape and the family kit.** That covers:
  - the 3 in yellow lane edges and black/yellow hazard zones (Uline, in stock, ships today);
  - 3M 471 band tape and stainless scoops and spatulas (McMaster-Carr);
  - Vikan's blue and orange brushes, dustpans and lidded tubs (WebstaurantStore, ships in 1-6 business days).
- **Stack lights are most of the total: $9,988 for 14.** The pick is a Patlite LA6 PoE tower at $684.90 plus a
  $28.56 bracket, $713.46 a station. The scheduler drives it over HTTP or Modbus/TCP, and one network cable powers it.
  - Wolf Automation shows 3 in stock; the other 11 need a quote.
  - Any machine whose own tower can be set to the lab's order saves a tower.
  - Buy them as stations come on line, not all at once.
- **A second kit for the Cu family is $2,234 "soon", plus quotes.** It holds:
  - the same McMaster 8 in sieve stack the lab has (No. 60, 100, 140, 230, 325, pan and lid, $992.45);
  - the Nilfisk 118EXP's hose and filters.

  AMAZEMET quotes the crucible set, the sealing rod and the plates. This waits on Sterling's open call on dedicating
  sieves and crucibles. `notes/atom_vacuum.md` already plans a whole second 118EXP for Cu. If that is bought, its own
  hose, filters and pail replace this group's vacuum lines. Buy one or the other, not both.

## How it was looked up: through the CubXL Pi

- **A SOCKS tunnel, nothing on the Pi.** Every product page was fetched through an SSH SOCKS tunnel (`ssh -D`) to the
  CubXL Pi. Nothing was installed, written or changed on the Pi; it relayed the traffic. Its load before was 0.09.
- **What the sellers saw:** a visitor from BYU's own network (AS6510, Brigham Young University) instead of the
  runner's Microsoft datacenter (AS8075).
- **How pages were read:** curl where a site serves plain HTML. Elsewhere a real Chrome on a virtual display, with
  images, video and fonts blocked and each page capped at 500 kB/s, so the Pi's Wi-Fi was never loaded.
- **Prices:** as each page showed them on 2026-11-22, per pack at quantity 1, before shipping and tax. BYU is
  tax-exempt. Where a seller gives a quantity break, the line's notes say so.
- **Through BYU's network:**
  - **Worked:** Uline, McMaster-Carr, Mighty Line, WebstaurantStore, Primera, Amazon, AutomationDirect, Wolf Automation, Gilson,
    AMAZEMET, Nix and Brother.
  - **Refused, so nothing is priced from them:** Grainger, Zoro, Mouser, Seton, Newark, Allied (now RS) and Galco's
    product pages, all with bot checks. Digi-Key let in its home page and challenged every search. Brady and Global
    Industrial let one browser in and refused another.
- **Where a figure is weaker:** a few figures came only from a search result, because the page refused. Each is marked
  "(snippet)" in its line's notes and is left out of the totals.

## Codes to buy the colours by

The scheme's colours are sRGB targets: blue `#0072B2`, orange `#E69F00`, and brown `#7B4A2A` reserved for a third
family. Shadow boards, signs, powder coat and custom labels are ordered by a code, so
[`out/colour/buying_colours.json`](../out/colour/buying_colours.json) checks the usual codes the same way
`colour_coding.py` checks the palette: simulated protan, deutan and tritan vision, with differences in CAM02-UCS.

| Family | Order by | Avoid | Why |
|---|---|---|---|
| Al blue | **RAL 5015 sky blue** or **Pantone 300 C** | navy, such as RAL 5005 signal blue | RAL 5005 is 18.4 from the black neutral, under the pass mark of 20 |
| Cu orange | **Pantone 1375 C** or **RAL 1028** (amber); safety orange or RAL 2003 also pass | red-orange: RAL 2004 pure orange, Pantone 021 C | 16.8 and 19.9 from the reserved brown for protan vision |

The red-orange only matters once a third, brown family exists. Today blue and any of these oranges are at least 48.7
apart for every kind of colour vision. Most stock "orange" tools and tape are redder than `#E69F00`. That is fine
for Al against Cu, but it is one more reason the family's name is always printed beside the colour.

## 1. Alloy-family marking, tools and containers

**Bands and tape.**

- **3M 471 vinyl tape in blue and orange,** from McMaster-Carr:
  - 7779A22 at 1/2 in, $18.62 a roll: 2 rolls per colour, for the 12 mm bands.
  - 7779A14 at 1 in, $30.61: 1 roll per colour, for the 25 mm bands on the waste cans.
- **471's limit is heat.** It is rated 40-170 °F (4-77 °C), so it takes washing and isopropanol wipes, but not an
  autoclave or a washer-disinfector's hot stage.
- **Instrument-marking tape** is for anything that goes through a washer-disinfector or autoclave. STERIS/Key
  Surgical make T0202 (blue) and T0207 (orange), 1/4 in x 250 in, so two strips make a 12 mm band. STERIS sells only
  to account holders, so there's no price.
- **Heat-shrink** for round handles and hose cuffs:
  - **Blue:** McMaster 7856K267, 268 and 269 (1/2, 3/4 and 1 in, $5.13-9.86 per 4 ft).
  - **Orange:** McMaster has none in that series. Its orange 6500N302-304 ($10.11-15.02) is the colour of
    high-voltage insulation, so keep it to tool handles, away from wiring.

**Hand tools for each family's spills: Vikan (which now owns Remco), from WebstaurantStore.**

- **The set, blue and orange:**
  - soft hand brush 45873 and 45877 ($13.49 and $13.99);
  - dustpan 56603 and 56607 ($16.49 each);
  - extra-stiff detail brush 44013 and 44017 ($8.49 each).

  They ship in 1-6 business days. remcoproducts.com now redirects to Vikan's site, which shows no prices.
- **They are polypropylene and can charge.** NFPA 484/660 wants conductive, bonded tools round Al dust. The
  static-dissipative option is McMaster 3328N17, with a black handle and a grounding cord ($59.70, banded,
  optional), one per family.

**Powder-contact tools: bare stainless, banded.**

- **Four of each, two sets per family,** all from McMaster:
  - 7075A15 spoon-spatula and 7075A17 spatula ($5.78 each);
  - the 1383N25 flat-bottom spoon set ($11.60).
- **No bronze or beryllium-copper "non-sparking" tools for the Al family.** They are copper alloys, the very
  contaminant the scheme keeps out of Al.

**State is a place: boards, tubs and the HOLD bin.**

- **Shadow boards:** Uline H-7791W pegboard, 48 x 24 in, $63, in stock, with each tool's outline in the family tape.
  Two of them. Vikan's custom colour-coded boards are quote-only; its UK page says about 2 weeks.
- **"To clean" tubs:** Vikan 12 L buckets 56863 (blue) and 56867 (orange), $26.49, with lids 56873 and 56877 ($12.99
  and $13.49).
- **HOLD bin:** Uline S-12676BL, a black lidded tote, sold in threes ($54).
- **HOLD labels:** Uline S-8170, 500 red labels for $27. Uline says they look "more orange than pictured". Hold one
  against the Cu orange before buying: a HOLD label must never read as the Cu family.
- **HOLD tags:** no stock tag is red with white HOLD text. Brady 47102 (red on white, 100 tags) is about $72.99, but
  only from a search result, because Brady refused the page.

**Powder-waste cans.**

- **The pick:** Uline S-7342, unlined 1 gal steel cans with lids, sold only by the carton of 34 ($156), in stock. Two
  go into use and the rest are spares for years.
- **The alternative:** McMaster's 2 gal stainless can with a loose lid, $66.81 each.

## 2. Labels and markers

**Jar labels: the packaging station's Primera LX500c prints the stripe.** No new printer is needed for the jars.

- **Labels:** Primera 075891, white Extreme Matte BOPP, 3 x 2 in (76 x 51 mm), 750 a roll, $64, in stock. Buy 2
  rolls.
  - **Size.** Primera makes no durable label as small as the mock-up's 70 x 32 mm on the LX500c's 2 in core, so the
    label grows to 3 x 2 in. Check it fits the smallest jar.
  - **Orientation.** The AP380 wraps the 2 in side round the jar, so lay the stripe out along the 3 in side.
- **Ink:** the tri-colour cartridge 053374, $68.95, in stock. Buy 2.
  - It is dye ink. Print a swatch of the blue and the orange, hold it against the tape, and wipe it with isopropanol
    before printing labels in bulk. CMY dye may push the blue towards cyan.
  - One review on Primera's listing (a search result) says this BOPP feeds badly in an LX500, so try one roll first.

**Tool tags and small labels: a P-touch.** The lab already labels jars on a P-touch. Brother's networked PT-P950NW
($578, in stock at Brother USA) is the optional upgrade: it takes the 36 mm tapes, prints the heat-shrink wire markers
and can print from the database. The tapes are all from Brother USA and in stock, except the green one:

| Tape | Code | For | Qty | Each |
|---|---|---|---|---|
| black on white, 12 mm | TZe-231 | tool IDs | 4 | $16.49 |
| black on blue, 12 mm | TZe-531 | Al tool tags | 2 | $16.49 |
| black on fluorescent orange, 12 mm (5 m) | TZe-B31 | Cu tool tags | 2 | $20.99 |
| white on blue, 12 mm | TZe-535 | air, nitrogen and argon labels at the docks' couplings | 1 | $17.99 |
| white on green, 12 mm | LM Tapes LMe-735, a compatible (Brother USA has no TZe-735) | chilled water at the couplings | 1 two-pack | $15.44 (Amazon) |
| flexible ID, black on white, 12 mm | TZe-FX231 | cable flags | 4 | $18.49 |
| heat-shrink tube, black on white, 11.2 mm | HSe-231E | wire markers by system and phase | 2 | $45.00 |
| strong adhesive, black on white, 24 mm | TZe-S251 | panel and machine labels, and the VACUUM markers | 3 | $24.99 |

- **The fluorescent orange** can't be simulated like an ordinary colour. Hold it beside the 471 orange and the HOLD
  labels.
- **The compatible green** may have a weaker laminate and adhesive. Try it first on the chilled-water fittings, which
  sweat.

**Pipe markers (ASME A13.1).**

- **McMaster's made-to-order markers:** 2094N11 (white on blue) and 2094N12 (white on green), printed with the
  message you give. Each is 1 x 8 in, wraparound, for 3/4-2-1/4 in OD pipe, $27.16 per 10. Buy 3 packs for COMPRESSED
  AIR, NITROGEN and ARGON, and 2 for CHILLED WATER SUPPLY and RETURN.
- **Arrows:** these markers carry none, so add Uline's blue (S-23500-1) and green (S-23506-1) arrow markers, $24 per
  24.
- **VACUUM:** nobody stocks it in black on white, so print it on the P-touch's 24 mm TZe-S251. For 1-1/2 to 2 in pipe,
  where A13.1 wants 3/4 in letters, use the 36 mm TZe-S261.

**Wiring (NEC 210.5(C)(1)).**

- **The panel label is custom.** The pre-printed "wire colour code" labels cover the US pair, 208Y/120 and 480Y/277,
  not IEC 400/230. Print one per panel on the LX500c, from the jar-label rolls, with each system's colours as swatches
  and words:
  - 208Y/120: L1 black, L2 red, L3 blue, N white, PE green;
  - 400/230: L1 brown, L2 black, L3 grey, N blue, PE green-yellow.
- **At the terminations:** HSe-231E heat-shrink markers, by system and phase.
- **Inside the European machines' supply enclosures and on the trays' UPS outlets:** TZe-S251 labels ("IEC colours:
  blue = neutral", "UPS").

**Network (TIA-606).** Cable flags on TZe-FX231 carry both names, for example `tray-d-sw/3` and `lonsdale-pc`. About
120 cables come from the naming PR's counts (31 computers, 31 camera units, 12 switches and the instruments). Each
needs two flags of about 80 mm, so the 240 flags take 19.2 m, inside the 4 cassettes.

**Gas cylinders.** Brady 103669 status tags (FULL / IN USE / EMPTY), 25 a pack, are optional and not priced, since
Brady refused the page. The contents label stays the cylinder's identity (CGA C-7).

**The legend sign.** Three 18 x 24 in posters go up: one at the entrance and one by each family's shadow board.
- **Printing:** a large-format printer (BYU's print services), with the target swatches and the family names. Laminate
  them, and check the printed blue and orange against the tape.
- **Not priced.**

## 3. Floor marking

**The quantities come from the floor plan,** computed by `colour_bom.floor_lengths()` from `out/tray_plan.json` as
`colour_coding.floor_figure` draws it. Each has about 10 % added and is rounded up to whole 100 ft rolls.

| Marking | Length | Bought |
|---|---|---|
| Yellow lane edges, 3 in | 40.8 m (134 ft) | 2 rolls |
| Black/yellow hazard zones, 1 m round each docked MiR250 | 83.1 m (273 ft) | 4 rolls (3 if the offcuts are used) |
| White dock outlines, 2 in, 12 docks | 35.3 m (116 ft) | 2 rolls |
| White corners, about 10 cart, bin and stand places | 40 corners | 2 boxes of 24 |
| Red/white keep-clear, 3 in, 12 areas | about 46 m (150 ft) | 2 rolls |
| Green safety-equipment spots, 3 in | about 11 m | 1 roll, the smallest sold |

- **The hazard zones** are 8 taped outlines once overlapping zones are merged: 104.5 m of perimeter, 83.1 m of it clear
  of machines.
- **The 12 keep-clear areas** are:
  - the safety-assets PR's 7 Class D fire points (glovebox, rePowder, the Shuttles' gap, the Aconity's gap, packaging,
    DED, EOS M 400);
  - about 2 of the building's own extinguishers;
  - about 3 electrical panels.

  NEC 110.26 gives the panels' working space: 30 in wide by 36 in deep.
- **One seller.** Uline stocks the whole tape order, every line showing "In stock, ships today". Its tape is 60 mil
  PVC with bevelled edges. Uline gives no maker code; the roll weight matches Mighty Line's.
- **The alternative:** Mighty Line direct sells the same lines as 3RY, 3RYCHV, 2RW, 3RWCHVRED and 3RG, and its
  cleaner and floor signs too. Its total is 11 % more.
- **Check before ordering:** the Uline yellow/black and red/white pages don't say "diagonal". Check the photos, since
  the hazard pattern is diagonal stripes.
- **AMR traffic.** No maker claims its tape for AMRs. Mighty Line markets its tape for AGV paths. Uline claims
  forklift and floor-scrubber resistance.

## 4. Stack lights

- **The pick: Patlite LA6-5DTNWB-POE.** It is $684.90 at Wolf Automation. Automation Distribution has it at
  $761.00, "factory stock, lead time by quote". Add a Patlite SZK-003W wall bracket, $28.56. That makes $713.46 a
  station and $9,988.44 for 14.
- **Why this one:**
  - **The scheduler talks to it directly,** over HTTP, Modbus/TCP or Patlite's socket commands (from Patlite's spec
    sheet).
  - **One cable:** PoE (802.3af, 8.6 W typical, 12.5 W at most) carries power and data. No 24 V supply, PLC or PC.
  - **Built in:** steady or flashing for each lamp (30, 60 or 120 a minute) and a buzzer. Its 8 wired inputs let a
    machine's own PLC drive it too.
- **The order is a setting.** Each tier is a multi-colour LED, so set red, yellow, green, blue and white from the top
  at each tower as it goes in, and check it.
- **Stock:** 3 at Wolf; the other 11 by quote. Allied's "about 4 weeks" for a sibling model is from a search result
  only.
- **Network:** 14 PoE ports (about 216 W of PoE budget at 15.4 W a port) and 14 Cat5e cables. The cables aren't priced
  here; they belong to the network PR.
- **Priced, and not chosen:**

  | Option | Parts | Per station | For 14 |
  |---|---|---|---|
  | (b) plain 24 VDC tower | Patlite LS7-502DWC-RYGBC $301, M12 cable $35.50, CLICK Ethernet PLC C0-10DD1E-D $201, 24 V supply C0-01AC $73 (AutomationDirect, all in stock) | $610.50 | $8,547 |
  | (c) USB, Patlite | LR6-USBW base and 5 LED units (Wolf) | $391.00 | $5,474 |
  | (c) USB, budget | ANDONT 5-tier USB tower (Amazon, maker unknown, IP40) | $160.54 | $2,248 |

  - **Option (b)** also needs an enclosure, DIN rail, outlet and PLC program at each station. Its tower can't flash
    on its own.
  - **Option (c)** goes dark whenever its PC does, and several stations have no PC of their own.
  - **Not priced:** Banner's and Werma's towers.

## 5. A second kit for the Cu family

Sterling hasn't decided "whether to dedicate sieve sets and crucibles per family now", so those lines are
"soon".

- **Sieves.** The lab's own stack is McMaster's 8 x 2 in 304 stainless series (`instruments_char.py`,
  `notes/alloy_print.md`). The second stack totals $992.45:
  - No. 60 (7969T38), No. 100 (7969T42) and No. 140 (7969T43) at $144.77 each;
  - No. 230 (7969T46) and No. 325 (7969T48) at $186.72 each;
  - the pan (7969T21) at $91.76 and the lid (7969T19) at $92.94.

  Gilson's V8SF set is $557.80. But it stacks at 2-1/8 in, and the lab's tab, tipper and wash fixtures are drawn to
  McMaster's 2 in frame.
- **Crucibles, the sealing rod and the plates:** AMAZEMET, by quote (sales@amazemet.com).
  - The plates are already in `out/atom/plate_bom.json`, so count them once.
  - The spare graphite set in `out/atom/crucible_bom.json` could become the Cu set.
- **The vacuum (Nilfisk 118EXP).** A set of filters per family pays for itself. `notes/atom_vacuum.md` replaces the
  main filter and both HEPAs at every family switch, about $1,200 a time, and the lab has switched three times. With
  a set per family, the filters are swapped, not thrown away. The parts:
  - hose 01769218, $646;
  - main filter 40000460, $353;
  - upstream HEPA 1408678500, $243;
  - crevice tool 01768900, $53;
  - optional: the downstream HEPA kit 5-60103, $603.

  These prices are the repo's own (`out/atom/vacuum_bom.json`), not re-fetched today.
- **The collection vessel:** Uline S-7344, a 5 gal steel pail. It is $24 each but sold only in cartons of 5 ($120),
  in stock.
- **The funnel.** Al is the only powder both families use: it is the Al family's base, and about 9-10 % of NAB and 630
  bronze. So one more funnel is needed. `notes/lab_r8.md` says plastics are the worst choice for static with Al
  powder, so print it in a static-dissipative filament rather than plain PP.
- **The press punch and catch ring** are the lab's own design: a machine-shop quote from the STEP. They are optional,
  as run B's fallback.
- **Jars and cap liners** aren't priced: the repo names no jar product.

## The order of buying

1. **Order this week; it is in stock:**
   - **Uline:** floor tape and corners, the HOLD bin and labels, the pegboards, the waste cans and the Cu collection
     pail.
   - **McMaster-Carr:** band tape, heat-shrink and stainless tools, and the sieves once they're decided.
   - **WebstaurantStore:** Vikan's tools and tubs.
   - **Mighty Line:** the cleaner and the signs.

   Most of it ships the same day or within a week.
2. **Ask for quotes now, since they set the long lead times:**
   - Wolf Automation or Automation Distribution, for 11 more LA6 towers;
   - AMAZEMET, for the crucible set, the rod and the plates;
   - a Nilfisk dealer, for the 118EXP's bin and conductive brush;
   - a machine shop, for the punch and ring if run B's fallback is wanted.
3. **Check the colours before buying in bulk.** Hold a sample of the tape, a tool and a label against the codes above
   under the lab's lights. Also check that Uline's two striped tapes are diagonal.

## Not priced, and why

- **Quote only:**
  - AMAZEMET's crucible set, sealing rod and plates (sales@amazemet.com);
  - the 118EXP's own collection bin and its conductive dust brush, from a Nilfisk dealer;
  - the press punch and catch ring, from a machine shop (the STEP is in `vacuum_press.py`).
- **Account only:** STERIS/Key Surgical's instrument-marking tape (T0202 blue, T0207 orange).
- **Refused:** Brady's red HOLD tags (47102), whose page returned 403 through the tunnel. The $72.99 per 100 comes
  only from a search result.
- **Made here:** the Cu family's Al-powder funnel, printed in-house.
- **Not specified:** the powder jars and cap liners, since the repo names no product.
- **Not fetched:** the three legend posters, from a large-format printer, and Brady's cylinder status tags
  (103669), whose page was refused.

## Open

- **Sterling's calls:**
  - whether to dedicate sieve sets and crucibles per family now (section 5);
  - a second 118EXP, or a second hose and filter set for the one vacuum;
  - how many stations get a tower now.
- **Physical colours.** No colour was measured; the photos were blocked to spare the Pi. Check every bought item
  against the codes above under the lab's own LED lighting. The optional Nix Mini 3 ($129) reads real values back
  into the check.
- **Shipping** isn't in the totals: Uline, McMaster-Carr and Mighty Line quote it at checkout.
