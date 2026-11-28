# Round 6: why the automated lab buys only the EDM and the Instron frame used

Sterling's question on PR 427 (2026-11-28): why only those two, and why not the furnaces? This note answers it from
the code at twin/ tree `e3d828c`, the market survey (issue 424, `out/twin6/market/`) and
[`twin_round6.md`](twin_round6.md) section 2. It changes nothing under `twin/`. Everything is simulated.

## The short answer

The rule buys used to save time and ignores price, because round 6 tracks money rather than limiting it. A used unit
is bought only if it brings its item online at least 14 expected days sooner than a new one would be. Most stations
already arrive new before the space is expected to be ready (day 80, the middle of the day 60-100 window). For those,
a used unit gains nothing, and its extra checkout makes it later. The EDM (an 18-week new lead) and the Instron frame
(16 weeks) are the only stations that pass all three tests: a lead long enough, a used market the survey counts, and
no slow new parts. The furnaces have a real used market, and a used furnace is cheaper and arrives sooner than a new
one. A new furnace also arrives before the space is ready, though, so used comes out 3.5 days behind.

## The rule

`used_rule6`, [`twin/round6.py`](../twin/round6.py) lines 226-235, applied to each item by `build_schedule6`
(line 279, bought used at line 284). In weeks:

```
new_on  = max(new lead, day 80) + install + commissioning
used_on = max(PO + used lead + p_fault x refurb weeks, day 80) + install + commissioning + extra used commissioning
buy used  if  used_ok  and  new_on - used_on >= 14 days
```

| Input | Value and source |
|---|---|
| Facility window | expected day 80 (`room_expected_d`, `round5.py` L113); each seed draws U(60, 100) (`round5.py` L87, `round6.py` L253) |
| Threshold | 14 days (`rule_days`, `round5.py` L113) |
| New lead | stand-ins in `round4.BUILD` (`round4.py` L97-125) with BYU's 2-week PO (L96), all "assumed" or estimated; the survey found no published lead for these models ("quote only") |
| Used lead | from the listings (`market6.py` `LEAD`, L62): seller handling (1 week from a dealer, 2 from a refurbisher or auction), transit (1 week in North America, 6 from overseas) and rigging (0-1 week), then the 2-week PO on top |
| Condition | `P_FAULT` (`market6.py` L81), weighted over the listings' conditions (0.05 for refurbished with a warranty, up to 0.5 for as-is); if a unit is faulty, `REFURB` weeks by class |
| Shipping and install | freight and rigging are in the delivered price (`FREIGHT`, `market6.py` L47), rigging weeks in the lead; install and commissioning are the same new or used (`BUILD`), plus `EXTRA_COM` for a used unit (`market6.py` L73: 0.5 weeks for a bench tool, 1.5-2 for vacuum and X-ray instruments and machines) |
| Price | a gate only: `used_ok` needs a market of "yes" (at least 5 listings that fit, 2 of them in North America, 1 priced) and a delivered price below new (`market6.py` L242, L314, L318). The rule itself never compares prices |

## The main candidates

Expected days. Price is the delivered used price as a share of the twin's new price. Leads include the PO.

| Station | New: price, lead (weeks) | Used: delivered price, lead (weeks) | Fault risk; refurbishment | Install + commissioning (+ used extra), weeks | Online, new / used (day) | Days saved | Bought |
|---|---|---|---|---|---|---|---|
| EDM | $230k, 18 | $46.7k (20 %), 5 | 0.31; 6 weeks | 2 + 3 (+2) | 161 / 129 | **+32.0** | used |
| Instron frame | $175k, 16 | $21.0k (12 %), 5 | 0.29; 6 weeks | 2 + 2 (+1.5) | 140 / 118.5 | **+21.5** | used |
| Furnaces (2) | $40k, 8 | $8.2k (21 %), 4 | 0.28; 3 weeks | 0 + 1 (+0.5) | 87 / 90.5 | -3.5 | new |
| Prep: polisher, press, saw | $55k, 8 | $12.3k (22 %), 4 | 0.53 (three machines); 3 weeks | 1 + 1 (+0.5) | 94 / 97.5 | -3.5 | new |
| Hardness | $70k, 8 | $8.5k (12 %), 4 | 0.23; 3 weeks | 0 + 1 (+0.5) | 87 / 90.5 | -3.5 | new |
| SEM | $100k, 10 | $19.6k (20 %), 5.5 | 0.12; 6 weeks | 1 + 1 (+1.5) | 94 / 104.5 | -10.5 | new |
| XRD | $105k, 10 | $25.2k (24 %), 4.5 | 0.30; 6 weeks | 1 + 1 (+1.5) | 94 / 104.5 | -10.5 | new |
| Mastersizer | $110k, 10 | $20.4k (19 %), 4.5 | 0.25; 6 weeks | 1 + 1 (+1.5) | 94 / 104.5 | -10.5 | new |
| XRF | $120k, 12 | $15.0k (12.5 %), 4.5 | 0.28; 6 weeks | 1 + 4 (+1.5) | 119 / 125.5 | -6.5 | new |
| Glovebox | $55k, 12 | $17.3k (31 %), 4.5 | 0.28; 4 weeks | 1 + 1 (+1) | 98 / 101 | -3.0 | new |
| ICP-MS (instrument used, the rest new) | $260k, 14 | $156k (60 %), 14 (its new parts) | 0.19; 8 weeks | 1 + 3 (+2) | 126 / 150.5 | -24.5 | new |
| Environmental chamber | $50k, 16 | $4.6k (9 %), 4.5 | 0.18; 3 weeks | 0 + 1 (+0.5) | 119 / 90.5 | +28.5 | new: thin, 4 listings |
| Nanoindenter | $250k, 16 | $25.5k (10 %), 4.5 | 0.37; 6 weeks | 1 + 2 (+1.5) | 133 / 111.5 | +21.5 | new: thin, 3 listings |
| PIP | $130k, 12 | no listings | - | 0 + 1 | 91 / - | - | new: no market |

The other stations are in [`out/twin6/checks/used_market.md`](../out/twin6/checks/used_market.md).

## Which stations have used listings

The automated lab buys 31 items: `round4.BUILD` without the CubXL, which it owns, and the space's fit-out.

* **A market at a saving (`used_ok`), 20:** EDM (117 listings), ICP-MS (95), Mastersizer (69), furnaces (65),
  Instron (61), Zwick (32), hardness (26), VHX (21), SEM (18), XRF (18), glovebox (14), hoods (13), XRD (8) and
  couplings (6). The prep station is 33 listings: polisher 12, press 9 and saw 12. The partly used ones, whose new
  parts set the lead: machining cell (105), doser (62), floor unit (53), units (46) and sieve cell (43). Only the
  EDM and the Instron are bought used.
* **Thin, 5:** environmental chamber (4), nanoindenter (3), EBSD (2), EDS (1) and Kardex Shuttle (35 listings, but
  only 2 in North America and none like-for-like with a price).
* **None, 4:** PIP (0; made since 2019), Carvera (0), MIDI (82 other LPBF machines, but LPBF must be like-for-like)
  and MX-Lab (4 other DED machines, likewise).
* **Not surveyed, 2:** cameras and UPSs (commodity).
* **Not bought at all:** the atomizer (the AMAZEMET rePowder, owned and used from day 0; the survey found only 2
  overseas listings of other atomizers), the CubXL, and the space's fit-out (building work). The conventional lab
  buys nothing.

## The furnaces

* **Not missing:** 70 listings. 5 were dropped (4 duplicates and 1 new unit advertised on LabX), which leaves 65:
  30 in North America and 23 priced. None is the NAT 15/65 itself. 5 are Nabertherm forced-convection or
  air-circulation furnaces, and 60 are substitutes (Lindberg/Blue M box furnaces, Despatch ovens, other
  Nabertherms). Substitutes count for generic tools (`market6.py` L97-105).
* **Not filtered out:** the verdict is "yes" and `used_ok` is true.
* **Not slower or dearer used:** a used furnace is on site 4 weeks after the order, against 8 new. It costs $4,125
  delivered (a $3,225 median over the 10 priced North American listings, plus $900 LTL freight), against $20,000 new
  each. Fault risk is 0.28 from the mix of conditions (54 % used, 22 % refurbished or with a warranty, 12 % tested,
  11 % as-is). A faulty unit takes 3 weeks and 6.5 % of the new price to repair.
* **A purchasable station:** `furnaces` in `round4.BUILD` (`round4.py` L116), two Nabertherm NAT 15/65s for $40k,
  behind `furnace@vcl` (L137).
* **The reason:** a new furnace is on site on day 56, about 24 days before the expected day 80. A used one would be
  on site on day 34 (28 days plus the expected 0.85 weeks of refurbishment), wait 46 days for the space, then lose
  half a week to its checkout: online on day 90.5 against 87. In the engine's own draws, the new furnaces are on
  site before the space in all 16 grid seeds, and used ones would bring `furnace@vcl` online 3.5 days later in all
  16.
* **What would flip it under today's rule:** a new furnace that takes at least 13.9 weeks, PO included, rather than
  the assumed 8. Neither number is a quote.
* **Two caveats on the price (neither changes the decision, which ignores price):**
  * The 10 priced listings behind it are mostly box furnaces to 1,100-1,200 °C and bench ovens. The only priced
    Nabertherm forced-convection furnace is $9,769, in Germany.
  * The new price is an estimate too: Fisher UK lists the NA 15/65 at about $6.6-7.5k (undated).

## Proposal for after tier 1: buying more used

The question the rule asks is what limits used buying, not the market. 18 stations with a real used market are
bought new. Buying all 18 used would save about $875k of the $4.68M capital in expectation, but it would delay most of
their stations. The partly used ones would be 1-6 weeks later, the cell's mobile units among them.

1. **Value money as well as time.** Keep "used if it saves at least 14 days", and add "used if it is cheaper and
   costs no more than its checkout (about 4 days) on a station other than the cell's."
   * That adds the furnaces, hardness, prep, VHX, Zwick, glovebox and couplings: about $283k of capital saved in
     expectation.
   * `furnace@vcl`, `hardness@vcl`, `prep@vcl` and `density@vcl` come online 3.5 days later. Tensile (gated by the
     Instron) and the cell don't move.
   * Or put a price on a day, λ: buy used when the expected saving is at least λ times the expected days lost.
     * The break-even λ is $5.5-17k a day for the six of those seven that lose days (couplings loses none), $7-16k
       for the SEM, XRD, Mastersizer and XRF, and $4.2k for the ICP-MS. For the doser, sieve cell and machining cell
       it is under $250.
     * For scale, the lab's staff and its equipment's service contracts, utilities and space cost about $1.4k a day.
     * A day of the cell is worth far more than a day of one station, so keep the cell's items out of the trade or
       give them their own λ.
2. **Fix two things in the arithmetic that count against used.**
   * **Partly used stations:** the used parts' refurbishment is added after the new parts' lead (`round6.py` L232
     and L285), although it would happen while the lab waits for those parts. Doing the two in parallel changes the
     days saved for:
     * the ICP-MS from -24.5 to -14;
     * the machining cell from -39.2 to -14;
     * the units from -16.2 to -7;
     * the floor unit from -21.8 to -7;
     * the doser and the sieve cell to -3.5.
   * **Checking a bench tool before the space is ready:** a bench tool that arrives 6 weeks early could be checked
     out in an existing BYU lab while the room is fitted out.
     * That puts the furnaces, prep, hardness, Zwick, VHX, hoods, SEM, XRD and Mastersizer at 0 days, and the
       glovebox and XRF at +4.
     * This is optimistic for vacuum and X-ray instruments, whose 1.5 extra weeks are partly done in place.
3. **Better inputs, which also move today's rule.**
   * **New-lead quotes** (PR 331's drafts): every new lead in `BUILD` is assumed.
     * The rule would buy used if new took at least 13.9 weeks, PO included, for the furnaces, hardness, prep and
       Zwick; 14.4 for the glovebox; and 14.9 for the SEM, XRD, Mastersizer and XRF.
     * The two used purchases rest on the same stand-ins: the Instron stays used only above 14.9 weeks (16 assumed)
       and the EDM above 15.4 (18 assumed).
   * **The marketplaces the survey couldn't read** (eBay, BidSpotter, EquipNet and Surplus Record): with enough
     listings, the thin 16-week stations would pass on time.
     * The chamber needs 1 more listing, the nanoindenter 2 and the EBSD 3.
     * Only the nanoindenter would bring a station forward: `nanoindent@vcl`, by about 3 weeks. Hot tensile waits
       for the Instron, and the EBSD gates no station (it isn't in `STATION_ITEMS`).
   * **Like-for-like for stations the robots serve:** most of the low prices are substitutes. That is 60 of 65
     listings for the furnaces, 25 of 26 for hardness, 18 of 18 for the XRF and all of the prep machines'. If the
     robots need the exact model (tray geometry, automation, software), these markets shrink and the prices rise.
     Decide which stations need it before buying more used.
   * **Reliability in service:** `p_fault` covers a unit's arrival only. Over two years a used unit has a new
     one's downtime and service contract, so buying more used would look free. Add a downtime factor for used
     units first.
4. **Running it.** Add a build-out option (for example `used_rule="value"`) with today's rule as the default, so
   tier 1's rows stay valid. It changes the `twin/` tree, so it needs a new pin and a GP check after tier 1. It
   touches no optimizer.
   * All 16 seeds' build-outs take milliseconds and show which station dates move.
   * Where nothing moves, only the money columns should change, since capital payments feed only the spend report
     (`round6.py` L1005). Those rows can be re-priced after one seed confirms it.
   * Where dates move, rerun the automated lab's three reorder arms over 16 seeds: about 221 CPU-hours, which is
     55 runner-hours on EPYC 9V45s and about twice that on 7763s. The conventional lab buys nothing.

## Reproducing the numbers

Read-only, with numpy in any environment, from `vertical-lab/`:

```python
from twin import round6 as R6, round4 as R4
m = R6.load_market()
for k in sorted(R4.BUILD):
    p = R6.used_params(k, m)
    print(k, p["ok"], p["lead_w"], p["p_fault"], p["price_frac"], R6.used_rule6(k, p))
```
