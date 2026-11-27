# Is the vertical lab worth it? Gains, bottlenecks, and VLMs against mobile manipulators

Sterling, on [#407](https://github.com/vertical-cloud-lab/byu-vcl/issues/407) (2026-11-27): "Is the vertical lab worth
it? ... Be willing to conclude that it isn't, or that it is only under conditions we should name. What I want is an
honest answer, not a defence of the design."

"The vertical lab" here means the part of PR 318's design that is vertical: desktop-sized instruments on the trays of
two Kardex Shuttle XP 500 vertical lift modules (VLMs), brought to an opening where a MiR250 + UR12e works at them.
The alternative is the same instruments on benches, served by mobile manipulators that drive to them ("flat"). The
floor machines (atomizer, printers, DED, EDM, frames) stand on the floor in both. Automation against a conventional lab
is a different question, which the twin's rounds 3-5 answer; this note doesn't revisit it.

Everything quantitative here is either sourced (vendor documents, papers, the Acceleration Consortium's own records),
taken from the twin and PR 406's floor plans (simulated and designed, not built), or a stand-in that is marked as one.
The queue model is [`twin/worth_it.py`](../twin/worth_it.py); its tables are
[`out/worth_it/tables.md`](../out/worth_it/tables.md) and [`out/worth_it/sens.md`](../out/worth_it/sens.md).

## The short answer

**For the lab the twin simulates, no. The VLM is worth it only under conditions we don't have now** (the decision table
at the end names them).

- **Transport is not what binds us, so the VLM has nothing to speed up.**
  - In the twin's year the mobile manipulators are 1-2 % busy and the Shuttles' openings about 1 %.
  - Replaying the twin's 24 event logs through either layout moves no target by more than 0.15 days.
  - What binds is money, the shared atomizer, DED capacity, the 30-day immersion and, from round 5, people's decision
    time. The VLM touches none of them, except money, which it spends.
  - In round 5's logs, about 250 results a run wait for a person's decision point, a median of 77 h each. A tray or a
    drive costs minutes.
- **Its one real gain is floor: 29 % less** (281 against 398 m², [PR 406](https://github.com/vertical-cloud-lab/byu-vcl/pull/406)).
  - That floor is only worth something if we pay for space by the square metre: about $51k a year at the twin's rates.
  - It comes with a 9.15 m bay, 31.5 ft to the sprinklers.
  - It is the same work in less floor, not more work in the same floor. The twin's campaigns use about 7 % of the lab's
    capacity (round 3), so more in the same floor isn't something we need.
- **With outside users, the VLM is worse, not better** (simulated, 24 logs):
  - At 60 % outside load, two mobile manipulators on benches serve every request, in 2.1 h on average.
  - The VLM with two units turns away 6 % and takes 7.6 h; with one unit, 19 % and 14.3 h.
  - The limit is the trays, not the robots: instruments that share a tray can't be loaded while any of them is
    running. With two units, tray D (SEM and XRD) is held 89 % of the time. If trays could move while their
    instruments run, the two plans would tie; for a measurement in progress, they can't.
  - One unit is too few on either plan at 60 %: it loses atomizer slots (below). The one case where the VLM does
    better is a single, heavily loaded unit whose battery isn't the limit: its shorter drives then keep the atomizer's
    slots, which one unit on benches loses (section 6, sensitivities).
  - Round 5's two-year logs give the same picture: 99.9 % served in 2.4 h on benches, against 88-94 % in 8-14 h at
    the VLM.
- **If the arm has to stay at the instrument for part of each step,** as PR 332 assumed, the number of units binds
  whatever the layout:
  - one unit can't carry 30 % outside load (about 60 % of requests served, 65-68 h each);
  - two units carry it on either plan (1.9 h on benches, 2.8 h at the VLM);
  - neither plan carries 60 %.

  The remedy is another unit, not a VLM.
- **Cost.** Two 9.15 m Shuttles with their couplings and UPSs are about $0.5M in the twin's own estimates, the price of
  about 3.5 mobile manipulators.
  - Kardex's own maintenance guidance is 10-20 % of the purchase price a year, against the twin's 3 %.
  - Kardex lists no powered tray, and no air or data to a tray (PR 318's search and ours), so PR 318 had to design its
    own couplings and fit a UPS to every powered tray.
- **No precedent.** Neither our searches nor Edison found any lab that runs instruments inside a VLM.
  - The group that got furthest, the Acceleration Consortium, had its Kardex lab's technical requirements met, then
    dropped it in November 2025 "due to perceived risks" ([ac-dev-lab #471](https://github.com/AccelerationConsortium/ac-dev-lab/issues/471)).

**What a VLM is good at, and might still do for us:** storing many passive items densely and handing them to a robot
at one opening. Our powder jars (1,506 in PR 318's racks) and sample stores are that kind of load; running instruments
are not.

![Outside turnaround and share served, three layouts, both timings](../out/worth_it/worth_it.png)

*Simulated (`python -m twin.worth_it_figure`). The twin's year of internal work, 24 event logs, plus outside jobs at
30 % and 60 % of each instrument's clock. Left: request to sample back on the rack, log scale. Right: requests served;
the rest are turned away when 20 wait at one station. "Attended time" is PR 332's share of each step the arm stays.
The tables are below.*

## 1. The gains, one by one

| Gain claimed for VLM trays | What it is for a warehouse | For us | How big |
|---|---|---|---|
| **Floor space** | Dense storage up the height of the room; vendors claim "up to 85-92 %" | **Real, and the only big one.** 281 m² against 398 m² for the same 43 instruments ([PR 406](https://github.com/vertical-cloud-lab/byu-vcl/pull/406), [`twin_floorspace.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/72177f1/vertical-lab/notes/twin_floorspace.md) on its branch). The saving is benches and their aisles: 31 benchtop instruments go into 18 m² of Shuttle footprint | 117 m² less, 29 %. Worth about $51k a year at the twin's space rates ($215/m² a year to run it plus $222/m² a year of building, [`twin/econ.py`](../twin/econ.py) `RATES`), and nothing if the room is already ours. It needs a 9.15 m bay. The vertical lab is not smaller in volume |
| **Throughput** | Goods-to-person: the picker stops walking | **Not a gain.** The replay never finds the VLM faster for internal work, and with outside users it is slower (section 6) | Driving falls from 52-81 s a task on benches to 29-61 s at the VLM. That doesn't matter while the robots are 1-2 % busy |
| **Positioning at a fixed bay** | One pick face, known geometry | **Real but small.** For the benchtop instruments the arm calibrates at 2 openings instead of at every bench. A MiR250 docks to a VL-marker to ±3 mm in up to 14 s (MiR250 spec, 2023), and an arm camera takes that to about 1 mm (Enabled Robotics' ER-VISION). Liverpool's touch-off reached ±0.12 mm (Burger et al. 2020). Kardex doesn't publish the extractor's repeatability at the opening; PR 318's coupling needs 4 mm ([`services.md`](services.md)) | Seconds a visit. Vision calibration takes about 5 s, touch-off about 53 s (Edison, mobile manipulators) |
| **Enclosure** (dust, light, temperature, humidity) | Kardex sells climate-controlled, clean-room and low-humidity units | **Mixed.** It keeps out dust and light, but every watt a stored tray uses stays inside the cladding: 1.3 kW in Shuttle 1 when idle, 3.7 kW with a printer and the furnace running, which needs 1,100-2,200 m³/h of forced air ([`services.md`](services.md)). A room's HVAC does this for benches | Small, and partly a cost |
| **Safety and access control** | Items released only to an authorized user at one opening | **Real but small.** People never reach into a moving machine, and the opening is the only access. The robots still drive the floor in both layouts. A badge-locked room gives most of the access control | Small. It matters more with outside users |
| **Tracking and provenance** | Every pick logged against a slot | **Negligible.** The lab's scheduler logs every step anyway (the twin's event logs do). Provenance that matters, who ran what on which instrument with which calibration, comes from our software, not from the store | None beyond what we'd build anyway |

Two things count against the VLM in the same table:

- **Every visit moves the instrument.** Tray presentations run from 4-6 a day (the twin's own work) to as many as 164
  a day (with outside users).
  - The Acceleration Consortium measured a Kardex tray with a microscope on it ([ac-dev-lab #216](https://github.com/AccelerationConsortium/ac-dev-lab/issues/216)).
    Peaks were 1.0-4.3 m/s², logged once a second, so short peaks are missed. It vibrates "with the most intensity
    when going in and out of the open port, not really when going up or down". A stored tray read about 0, and the
    microscope stayed usable. No VLM vendor publishes acceleration or vibration figures.
  - Moving an instrument can trigger a check before its data count:
    - balances: re-level, warm up, then a check with weights at the new place;
    - Rockwell hardness: ASTM E18 makes a move trigger direct verification;
    - XRD: a reference check (Edison, moving instruments, with its caveats).
    - On a tray, every presentation is a move.
  - Kardex can slow a tray ("slower speeds for fragile items"), at a cost in time (section 4).
- **A single point of failure.** "If a single machine goes down for maintenance, all the inventory it holds becomes
  temporarily unavailable" ([Kardex](https://www.kardex.com/en-us/blog/how-many-vertical-lift-modules)).
  - Here that inventory is 7-8 instruments a Shuttle.
  - A power cut during a lift leaves the machine "with no reference", which needs Kardex's service login
    ([Kardex knowledge base](https://info.kardex-remstar.com/knowledge/recover-from-power-outage)).
  - We found no procedure for getting a stored tray out by hand.
  - On benches, a broken robot leaves every instrument where a person can use it.

## 2. Does any of this touch what binds?

| What binds (the twin) | Where it says so | Does a VLM touch it? |
|---|---|---|
| **Money** | Round 3: "about 80 % of each campaign's spending goes to orders of metal and consumables" and the spending plan holds copper back ([`twin_round3.md`](twin_round3.md)); round 4: "Money binds both plans that start on day 0" ([PR 397](https://github.com/vertical-cloud-lab/byu-vcl/pull/397)) | **Only the wrong way.** It costs about $0.5M of capital (section 5) |
| **The shared atomizer** | Round 4: "about three new aluminium designs a week in every plan"; round 3: it runs 55-71 % of what its start slots allow | **No.** It is a floor machine in both layouts. The replay keeps every atomizer slot in both layouts unless one unit is overloaded (section 6) |
| **DED capacity** | Round 4: "Copper waits for DED capacity" | **No.** The MX-Lab is a floor machine |
| **The 30-day immersion** | 24 vial positions; a coupon holds one for a month | **No.** The vials ride tray A on the CubXL's deck; the VLM changes neither their number nor their month |
| **Decision time** | Round 5 ([PR 405](https://github.com/vertical-cloud-lab/byu-vcl/pull/405)): "A person's decision waits for the next review or weekly meeting." Its summary isn't written yet, but its logs are on its branch. In its automated lab with the cheap policies (16 two-year logs), about 250 results a run are held for a person's decision point (`round5.held`), a median of 77 h each, and 169 h with slow decisions | **No.** A held result waits about three days; the VLM saves or costs minutes. The VLM replay on round 5's logs is in section 6 |
| *(not binding)* the robots | Round 3: "the robots are about 1.5 % busy"; here 1-2 % in every layout | This is the one resource a VLM could relieve, and it isn't short |

The replay confirms it. With no outside work, every layout reproduces the twin's year:

- internal steps end 0.04-0.07 h *earlier* than the twin's (the twin allowed 6 min a step for the transfer);
- no atomizer slot is lost;
- no target moves by more than 0.15 days.

## 3. Why VLMs are popular, and what carries over

VLMs earn their place in warehouses, pharmacies and biobanks by storing **many passive items** densely and bringing
them to a person or robot at one opening. Edison's review of lab, biobank and pharmacy deployments
([answer](../out/edison/worth_it_vlm_lab_storage/answer.md)) puts each claimed benefit against "a small number of
instruments that run in place":

- **Floor-space savings** ("up to 85-92 %"): they come from consolidating many trays. Running instruments "still
  require benches, service clearances, ventilation, power, data, gases, fluids, and stable utility connections".
  Independent figures are smaller than vendors' (a UK hospital dispensary robot saved about 29 % of its area,
  Pharmaceutical Journal 2009).
- **Pick throughput** (100-400 lines an hour): "Instruments that run in place are not repeatedly picked, so this
  metric is largely irrelevant."
- **Ergonomics** (less walking and bending), **pick accuracy** (99.9 %), **traceability**: these help when people
  pick many similar items, and apply weakly or not at all to robots loading a few distinctive instruments.
- **Access control and security**: partly, but "badge-controlled rooms, locked enclosures, software logins, or cages
  usually provide it without a retrieval machine".
- Even for passive stock, the goods-to-person literature finds a VLM uneconomic at low utilization, and some firms
  find them "too slow for efficient order picking" (Edison, [goods-to-person](../out/edison/worth_it_goods_to_person/answer.md);
  Tavira et al., WSC 2024). A case study found one VLM slower than open shelving in most scenarios (Singh et al.,
  WSC 2019).

**What carries over is the store, not the instruments.** Our items are instruments that need power, data, nitrogen,
chilled water or exhaust, and that are busy for hours. Neither we nor Edison
([answer](../out/edison/worth_it_instruments_in_storage/answer.md)) found an installed system that runs instruments
inside a VLM. Edison's precedent search found:

- **Two Vidir patents**: a vertical carousel that powers its shelves while they move (CA3162492C, 2025), and a VLM
  that powers trays once they are stowed (US20240116714A1, 2024). Neither shows a built system or names an
  instrument.
- **Powered trays from two VLM makers**, to keep cold boxes running and to charge batteries:
  - Hänel's trays with a plug-in contact, for cold boxes down to −80 °C;
  - Modula's 240 V socket, on at most 10 trays a machine.
  - Kardex lists neither.

Labs that move instruments do it differently: on docking carts with utilities at the dock (HighRes Biosolutions'
patent US 7,560,071; Ginkgo's carts). Self-driving labs leave instruments where they stand and move the samples
(Liverpool, A-Lab, ASTRAL; the industrial metals labs of FLSmidth, Herzog and Polysius).

**Doing more in the same floor or the same in less?** The vertical lab does the same in 29 % less floor. Doing more
in the same floor would matter if capacity bound us, but the twin's campaigns use about 7 % of the lab's
capex-weighted capacity (round 3). The same work in less floor matters only if the floor costs us something:

- if the lab goes into a building we pay for by the square metre, it saves about $51k a year at the twin's rates;
- if it goes into a room we already have, it saves nothing;
- it needs a room at least 9.17 m tall with 31.5 ft to the sprinkler deflectors (33 ft under ESFR;
  [`kardex_height.md`](kardex_height.md)). PR 344 found no building near BYU over 36 ft, and that PR 318's lab with
  its earlier 3.95 m Shuttles needed only 16-18 ft clear.

## 4. Is there a speed gain from trays over driving?

**Vendor figures.**

- **Kardex Shuttle 500, configured at 6.75 m tall:**
  - 20 s on average (23 s at most) to fetch a tray;
  - 38 s (45 s) to put one away and fetch the next;
  - 94 trays an hour.

  These are at 100 % speed, but units ship with the extractor at 70 %, and an always-closed door adds about 6 s
  ([configuration sheet](https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/VLM-Option-1-96x34-Light-Specification-Sheet.pdf)).
  Kardex publishes no figure for taller units beyond "can increase", and for robot handling "a prior consultation
  with the factory is recommended".
- **Modula:** "Tray delivered to the bay in under 30 seconds", up to 120 trays an hour.
- **The MiR250:**
  - 2.0 m/s at most, accelerating at 0.3 m/s², so it needs 9.5 m to reach that speed;
  - docks to a VL-marker in up to 14 s and undocks in up to 11 s
    ([MiR250 specifications, 2023](https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf)).
  - Nobody publishes how long the arm takes to calibrate at a station. Edison found vision-based calibration at about
    5 s a station and touch-off at about 53 s.

**In the model** (handling table in [`tables.md`](../out/worth_it/tables.md)):

- A task's driving is 29-61 s at the VLM and 52-81 s on PR 406's benches.
- At the VLM the arm waits 10-22 s for its tray after it arrives, even though the Shuttle starts fetching when the unit
  is assigned.
- Either way it is about a minute, against instrument steps of 0.5-8 h. The VLM saves about half a minute of driving a
  visit, and it doesn't matter while the units are 1-2 % busy.

**Slowing the trays for sensitive instruments.**

- Kardex trays "can be programmed ... slower speeds for fragile items", with no figures.
- A dealer told the Acceleration Consortium that speed can be cut at order, and that "many companies, especially in
  research/aerospace tend to do this".
- Nearly every instrument tray in PR 318 holds something sensitive: the SEM, the XRD, the Mastersizer, the
  nanoindenter, the PIP, the microscope, the hardness tester, and the doser's balance. So a slow profile would apply to
  almost every tray.
- The sensitivities run every tray at 2.5× its time ([`sens.md`](../out/worth_it/sens.md), 4 logs). The cost is
  small, because the openings have slack:
  - at 60 % outside load with the twin's timing, two units at the VLM go from 7.5 h to 7.9 h, and the busiest opening
    from 28 % to 33 %. One unit goes from 14.1 h to 16.1 h, with 77 % served instead of 82 %;
  - at 30 % it adds about 0.1 h;
  - with attended time at 30 % and two units, it adds 0.5 h (2.7 to 3.2 h; the opening 60 % to 64 %).

  What costs time is a measurement holding its tray, not the tray's speed.

**How fast can a mobile manipulator go near people?** No standard caps it at walking speed. What they say, and what
people set:

- **ISO 3691-4 (driverless trucks).** With person detection on and more than 0.5 m clear on each side, the truck may run
  at its rated speed. Where detection is muted, as when docking, the limit is 0.3 m/s
  ([TÜV Rheinland's extract](https://tuv-rheinlandprod-media.e-spirit.cloud/f117df9a-386d-4f14-b01c-221f621297b3/example-media/industrial-lifecycle/tuv-rheinland-automatic-guided-vehicles-whitepaper-en_neu.pdf)).
  It covers stationary people only. MiR mutes the fields at every marker but the L-marker, and asks for a marked hazard
  zone at least 1 m around such a dock, with no workstations inside.
- **ANSI/RIA R15.08-1.** A MiR250 with a UR arm is a Type C "mobile manipulator". Presence sensing "may be suspended
  under 300 mm/s", and speed limits must allow for the base and arm moving together (the R15.08 interim chair's 2022
  slides; we didn't read the standard itself).
- **ISO 10218 (2025) and ISO/TS 15066.** 250 mm/s is the arm's reduced speed. ISO/TS 15066 sets contact forces, not
  speeds. For a UR10e, a hand clamped against a surface implies an arm speed under 0.28 m/s (Kirschner et al. 2022).
- **What labs set.** Liverpool's robot chemist capped its base at 0.3 m/s and its arm at 0.4 m/s (0.1 m/s near
  fixtures), and moved the arm only with the base stopped (Burger et al. 2020, SI). A hospital TUG (Aethon T3) tops
  out at 0.76 m/s.
- **People.** They walk at 1.2-1.5 m/s, but about 1.0 m/s beside a moving robot, and comfort falls as the robot's speed
  rises from 0.35 to 1.7 m/s (Neggers et al. 2022). At ≤ 0.4 m/s passing robots were "never perceived as
  intimidating" (Pacchierotti et al. 2006, small samples).

The model drives at 0.8 m/s (a stand-in, between Liverpool's cap and a hospital robot's), with sensitivities at
0.3 m/s and 1.5 m/s:

- At 0.3 m/s, Liverpool's cap, two units on benches go from 2.0 h to 2.2 h at 60 % outside load, and two at the VLM
  from 7.5 h to 7.6 h. A single unit suffers on either plan: 20.3 h on benches, 16.4 h at the VLM.
- At 1.5 m/s nothing changes with two units.

So with two units, a mobile manipulator can drive at a pace people are comfortable with, at or below walking speed,
for almost nothing.

## 5. Cost and implementation

**Capital and running cost of each option.** The twin's prices ([`twin/econ.py`](../twin/econ.py)) unless marked; none
is a quote.

| | Two Shuttles, as PR 318 has them | One more mobile manipulator |
|---|---|---|
| Purchase | 2 × $210k: Kardex's "$6,000-8,000 per vertical foot" × 30 ft is $180-240k ([Kardex](https://www.kardex.com/en-us/blog/how-much-does-a-vertical-lift-module-cost)); a 6.75 m Shuttle 500 lists at $166k, product only ([reseller, 2026](https://storemorestore.com/shelving-and-racks/industrial-shelving/kardex-shuttle-xld-500-vertical-lift-module-96-x-34-light-duty-storage-trays)) | $140k: MiR250 (no list price; the twin uses $59-65k), UR12e $44,636 ([Vention, 2026](https://vention.com/parts/universal-robots-ur12e-collaborative-robot-arm-3443)), gripper $5,240, integration. A MiR250 + FANUC CRX package lists from $159,615 (search snippet only) |
| What only the VLM needs | CombiTac couplings on 12 powered trays and 2 bays, 14 × $4k (estimate); a UPS on every powered tray, $22k; tray cameras; forced ventilation for the heat; a 9.17 m room; a slab for up to 70 t a unit on about 8.5 m² (a 6.75 m unit fully loaded is 39.5 t, Kardex configuration sheet) | Docking targets; benches for the 31 benchtop instruments (not priced here) |
| Capital | **about $0.50M** | **about $0.14-0.16M** |
| Service a year | Twin: 3 %, $12.6k. Kardex's own guidance: **10-20 %** of the purchase price, $42-84k ([Kardex](https://info.kardex-remstar.com/knowledge/how-much-should-i-budget-for-asrs-maintenance)); integrators 5-10 %; two preventive visits a year to keep the warranty | Twin: 5 %, $7k. The MiR250's design life is 5 years or 20,000 h (spec sheet), so a base is replaced within ten years |
| Floor | 117 m² less; about $51k a year at the twin's rates, if the space is paid for | none |
| **Ten years** | $0.62M (the twin's 3 % service) to $1.34M (Kardex's 20 %); **less $0.51M of floor**, if it is paid for at the twin's rates: **$0.11M to $0.83M** | **about $0.2-0.3M** |

So the VLM is close to cost-neutral against another unit only if we would otherwise build or lease about 117 m² at
the twin's high-bay rate and Kardex's service is as cheap as the twin assumed. Even then it buys floor, not
throughput. "A VLM with all the extras may cost about the same as another mobile manipulator" holds per Shuttle only
within a factor of two: about $250k against about $150k. PR 318 has two Shuttles.

**The engineering a VLM needs that a standard one doesn't** (all from PR 318's own design notes):

- **Services to a stored tray.** Kardex powers a tray in its slot and at the opening, but not in transit. It lists
  no powered tray and no air or data, so PR 318 designed a CombiTac coupling for mains, Ethernet, compressed air,
  N₂ and chilled water ([`services.md`](services.md), [`coupling.md`](coupling.md)). A retractable line was tried and
  dropped: while its tray was out it spanned the shaft, so no other tray could be fetched.
- **A UPS on each powered tray** ([`ups.md`](ups.md)).
  - Each tray has a backed branch for whatever loses state, and an unbacked one for heaters, motors and pumps.
  - The schedule "never moves a tray while something on its unbacked branch is working".
  - Tray F's unbacked branch, 5.0 kW, sits at the dock's 5 kVA rating.
- **Heat.** Every stored watt stays in the cladding: forced air at 1,100-2,200 m³/h. Kardex hasn't said what its
  drives tolerate.
- **Load and height.** 555 kg a tray, 70 t a unit, 727.5 mm the tallest item. The N₂ generator (889 mm) doesn't fit a
  tray. A room over 30 ft.
- **Installation and faults.**
  - The Acceleration Consortium's install was planned at "about a week instead of three days" because of tight
    clearances.
  - Its site needed its own disconnect, "since the VLM's built-in emergency shutoff doesn't actually cut transformer
    power" ([ac-dev-lab #471](https://github.com/AccelerationConsortium/ac-dev-lab/issues/471)).
  - Recovering from a power cut mid-lift needs Kardex's service login.
- **Questions only Kardex can answer** (all but the access times are on [`services.md`](services.md)'s list): the
  heat a tray may give off, the interior temperature rating, the extractor's repeatability against the coupling's
  4 mm, whether a slot's power stays on while a tray is stored, and access times for a 9.15 m unit served by a robot.

**What each option fixes.**

| Pain point | VLM | Another mobile manipulator |
|---|---|---|
| Floor or room size | Yes: 29 % less floor, in a tall room | No |
| Robot-hours: outside users, or an arm that attends steps | No; the opening and the trays add their own queues | **Yes**: the binding resource in every case where something binds (section 6) |
| A single point of failure | Adds one: 7-8 instruments behind each Shuttle | **Removes one**: two units back each other up |
| Instruments that must not be moved | Makes it worse: every presentation moves a tray | Nothing moves |
| Dust, light, access | Some help | No |
| Dense passive storage (powder jars, samples) | **Yes**: what VLMs are built for | No |

## 6. Outside users: the queue model

**What it is.** [`twin/worth_it.py`](../twin/worth_it.py) replays the twin's committed event logs through a transport
layer, and adds outside jobs. Eighteen tests are in [`twin/tests/test_worth_it.py`](../twin/tests/test_worth_it.py).

- **The logs.** Round 3b's vertical lab for a year ([`out/twin3b/events/`](../out/twin3b/events)): 12 seeds of
  time-aware BOFN and 12 of the funnel, each campaign's best policy. That is 2,500 or so in-house steps a log.
- **The layouts:**
  - **VLM**: PR 318's tray plan ([`tray_plan.md`](tray_plan.md)). Each Shuttle has one extractor and one opening. A
    running instrument holds its tray, so tray-mates wait for each other: the SEM and XRD on D; the Mastersizer,
    nanoindenter and PIP on E; the furnace, polisher and mounting press on F; the zwickiLine and HM-220 on L.
  - **Flat**: PR 406's "automated, same floor plan", with its docks. One unit in an aisle at a time.
  - Each layout runs with one or two units.
- **Two timings:**
  - **The twin's**: a load and an unload a step. The twin books a 6 min transfer inside each step, and the replay
    credits it back.
  - **PR 332's attended time**: the arm stays at the instrument for a share of each step, from
    [PR 332](https://github.com/vertical-cloud-lab/byu-vcl/pull/332)'s `ATTEND`, "assumed ... from the chapters".
    Examples: XRD 0.5, tensile 0.5, PSD 0.3, SEM 0.2. In the VLM the tray stays at the opening meanwhile. The powder
    line has a cell with its own arm, as PR 332's rung R5 proposes.
- **Outside jobs** arrive at random at the instruments in [`twin/cloud.py`](../twin/cloud.py)'s catalogue: SEM, XRD,
  XRF, PSD, PIP, tensile, hardness, nanoindentation, the corrosion cell, the LPBF and DED machines, the furnace and the
  EDM. Each runs for its catalogue hours, at 0 %, 30 % or 60 % of each instrument's clock.
- **The rules, the same in both layouts:**
  - time-critical work first (the atomizer's start slots, the furnace's cycles and the steps feeding them), then
    internal loads and every unload, then outside loads, which always come last;
  - a free slotted station takes the first queued job whose start window is open, so one campaign's late atomizer
    job doesn't hold up the other campaign's day;
  - outside work takes only the gaps the twin's plan leaves before the next internal step at its station, or anywhere
    on its tray in the VLM;
  - one unit charges at a time, and an idle unit tops up its battery only in gaps long enough to drive to a charger
    and back.
- **Handling (stand-ins unless marked):**
  - driving at 0.8 m/s, accelerating at 0.3 m/s² (vendor);
  - 60 s to dock and localize, and 60 s plus 20 s to load and pick from a rack;
  - a tray takes 26 s each way: Kardex's 20 s plus 3 s for each coupling;
  - 10 s for a camera look at a newly presented tray;
  - a charge lasts 4.5 h of work and takes an hour (MiR's MC250, vendor).

### The results

Medians over 24 logs (full tables, with 10th-90th percentiles: [`tables.md`](../out/worth_it/tables.md)).

**The twin's timing:**

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held | Outside requests served | Outside jobs a day | Request to sample back (h): mean, 95th pct | Atomizer runs off their slot |
|---|---|---|---|---|---|---|---|---|
| 0 % | VLM + 1 | 2 % | 1 % | 6 % (B) | - | - | - | 0 |
| 0 % | flat + 2 | 1 % | - | - | - | - | - | 0 |
| 0 % | VLM + 2 | 1 % | 1 % | 6 % (B) | - | - | - | 0 |
| 30 % | VLM + 1 | 41 % | 20 % | 71 % (E) | 100 % | 127 | 1.7, 5.1 | 0 |
| 30 % | flat + 2 | 21 % | - | - | 100 % | 127 | 1.3, 3.8 | 0 |
| 30 % | VLM + 2 | 20 % | 19 % | 71 % (E) | 100 % | 127 | 1.6, 4.9 | 0 |
| 60 % | VLM + 1 | 62 % | 24 % | 75 % (L) | 80.8 % | 206 | 14.3, 38.2 | **280, in all 24 logs** |
| 60 % | flat + 2 | 39 % | - | - | **100 %** | **255** | **2.1, 5.7** | 0 |
| 60 % | VLM + 2 | 33 % | 28 % | 89 % (D) | 94.2 % | 240 | 7.6, 24.5 | 0 |
| 60 % | flat + 1 | 76 % | - | - | 89.4 % | 228 | 12.3, 19.9 | **396, in all 24 logs** |

**PR 332's attended time:**

| Outside load | Layout | Units busy | Busiest opening busy | Busiest tray held | Outside requests served | Outside jobs a day | Request to sample back (h): mean, 95th pct | Atomizer runs off their slot |
|---|---|---|---|---|---|---|---|---|
| 0 % | all four | 1-2 % | 1 % | 2 % | - | - | - | 0 |
| 30 % | VLM + 1 | 82 % (its ceiling) | 43 % | 45 % (F) | 60.4 % | 77 | 65.2, 74.8 | 5, in 19 of 24 logs |
| 30 % | flat + 2 | 68 % | - | - | **100 %** | **127** | **1.9, 4.8** | 0 (2 logs any) |
| 30 % | VLM + 2 | 67 % | 60 % | 53 % (E) | 100 % | 127 | 2.8, 8.7 | 0 |
| 30 % | flat + 1 | 82 % (its ceiling) | - | - | 58.9 % | 75 | 67.5, 76.9 | 6, in 18 of 24 logs |
| 60 % | VLM + 1 | 82 % | 43 % | 55 % (F) | 30.4 % | 78 | 79.7, 91.4 | 2, in 16 of 24 logs |
| 60 % | flat + 2 | 82 % | - | - | 61.0 % | 155 | 33.4, 39.4 | 0 (1 log any) |
| 60 % | VLM + 2 | 82 % | 67 % | 64 % (F) | 62.2 % | 158 | 32.5, 54.1 | 0 (2 logs any) |
| 60 % | flat + 1 | 82 % | - | - | 29.5 % | 75 | 82.2, 91.7 | 4, in 18 of 24 logs |

"82 %" is a unit's ceiling: 4.5 h of work, then an hour on the charger.

**Days to the twin's targets.**

- With no outside load, no layout moves any target by more than 0.15 days.
- Every layout with two units keeps every target within 0.03 days at the median, and within 0.4 days in the worst
  log, at any outside load and either timing.
- One unit moves targets most where it loses atomizer slots: at 60 % with the twin's timing, up to 0.04 days at the
  median and up to 4.9 days in the worst log, on either plan.
- The replay keeps the twin's order of work. A lost atomizer slot therefore moves every later run, while the twin
  itself would have re-planned. Read those rows as "this many units can't carry this load", not as a forecast of the
  delay.

**What it shows:**

1. **Without outside work, the layout doesn't matter.** Units are 1-2 % busy and openings 1 %. Every target lands
   where the twin put it.
2. **With outside work and the twin's timing, the trays bind, not the robots.**
   - At 60 % outside load with two units, tray D (SEM and XRD) is held by a running measurement 89 % of the time.
     Outside jobs at the VLM then take 7.6 h against 2.1 h on benches, and 6 % are turned away.
   - A second unit at the VLM cuts the turnaround from 14.3 h to 7.6 h, but it stays far above the benches.
   - One unit loses atomizer slots on either plan at 60 %: 280 runs a year at the VLM and 396 on benches, in every
     log. With a 4.5 h battery and that much work, it isn't free when a slot opens.
3. **With attended time, units bind on both plans.** One unit is not enough for 30 % outside load. Two carry 30 %,
   with a little more wait at the VLM: its opening is held 60 % of the time while the arm attends at a presented
   tray. Neither carries 60 %; both serve about 61-62 %. Internal work stays within about 0.2 h of the twin's timing
   on both plans, so neither protects it better.
4. **"A request waits while another tray is in the bay"** is real, but it is not the main queue. The arm waits 10-22 s
   for a tray after arriving, and the opening is 19-28 % busy at most with the twin's timing. Tray locks, a
   measurement holding the tray for hours, are the main queue.

### Round 5's lab says the same

Round 5's logs landed on [PR 405](https://github.com/vertical-cloud-lab/byu-vcl/pull/405)'s branch while this ran.
`python -m twin.worth_it run5 <dir>` replays its 16 two-year logs of the automated lab through the same model:

- the lab built from the day the money arrives, with every route at once;
- nominal decision time and the cheap policies;
- the lab's own instruments only: BYU's existing equipment, core facilities and partners are served by people, so
  they are left out;
- outside jobs from the day its first instrument opens, about day 87.

The tables are in [`tables_r5.md`](../out/worth_it/tables_r5.md). Days to targets are left out, because round 5's
targets are its own.

| Timing, outside load | Layout | Units busy (over two years) | Outside requests served | Request to sample back (h): mean |
|---|---|---|---|---|
| Twin's, 0 % | all four | 1-2 % | - | - |
| Twin's, 60 % | VLM + 1 | 59 % | 87.9 % | 13.8 |
| Twin's, 60 % | flat + 2 | 34 % | **99.9 %** | **2.4** |
| Twin's, 60 % | VLM + 2 | 29 % | 94.3 % | 8.0 |
| Twin's, 60 % | flat + 1 | 68 % | 91.2 % | 14.3 |
| Attended, 30 % | flat + 2 | 60 % | 100 % | 2.4 |
| Attended, 30 % | VLM + 2 | 59 % | 99.7 % | 4.1 |
| Attended, 30 % | either plan with 1 unit | 72 % | 58-59 % | 68-70 |
| Attended, 60 % | flat + 2 / VLM + 2 | 72 % | 60-61 % | 33-34 |

The units are idle for the first three months while the lab is built, which is why their busiest is about 72 % here
against 82 % in round 3b. Round 5's atomizer runs round the clock without start slots, so a late start costs that run
only, with no cascade. Internal steps stay within 0.6 h of round 5's own timing in every layout with two units.

**Sensitivities** (4 logs, 30 % and 60 % outside load; [`sens.md`](../out/worth_it/sens.md)):

- **The tray lock is the VLM's whole disadvantage.** If trays could move while their instruments run, the two plans
  would tie at 60 %: two units at the VLM would match two on benches (2.0 h, everything served), and one unit would
  match one (12.3 h on both). They can't, for a measurement in progress, and [`ups.md`](ups.md) forbids it for
  heaters, printers, polishers and presses.
- **Slowing the trays costs little** (section 4). Neither does turning off the pre-fetch: 7.5 h to 7.7 h with two
  units at 60 %, 14.1 h to 16.3 h with one.
- **Handling time matters more than the layout.**
  - With docking at 150 s and loading at 120 s, one unit fails at 30 % on either plan. Two on benches serve 98 % at
    60 % in 8.1 h; two at the VLM serve 89 % in 11.2 h.
  - At 30 s each, one unit on benches serves 60 % in 3.4 h and the VLM's one unit in 7.3 h. Both still lose
    atomizer slots, the benches more (256 runs, against none at the VLM).
- **With one unit, the battery and the driving decide, and here the VLM does better.**
  - MiR's MC250 runs 4.5 h a charge, and with it one unit loses atomizer slots at 60 % on either plan.
  - With a bare MiR250's 13 h, the VLM's one unit keeps every slot. One on benches still loses 291 runs a year,
    because its longer drives leave it 80 % busy against 69 %.
  - Outside work still takes 10.6 h at the VLM against 5.2 h on benches.
  - So if we could only ever have one unit, the VLM's shorter drives would protect internal work better, at the
    outside users' expense.
- **Carrying every outside sample from packaging** roughly doubles the units' work. At 60 %, two units on benches
  still serve everything (3.4 h); two at the VLM serve 91 % in 9.5 h; one unit serves about two thirds on either plan.
- **Without gaps kept for internal work, outside users cost the campaigns atomizer runs.** At 60 % with two units:
  - with the twin's timing, 23-25 runs a year on either plan;
  - with attended time, 68 at the VLM against 4 on benches.
  - With one unit, hundreds on either plan. A scheduler that puts internal work first matters on any layout.
- **If the units also tend the powder line** (PR 332's shares everywhere), every layout starts hundreds of the
  atomizer's roughly 500 runs a year late (278-505). The powder line needs a cell of its own, as PR 332 concluded.
- Driving speed and shared aisles change almost nothing with two units.

## 7. Is it justified? The decision table

| Condition | The VLM wins | Another mobile manipulator wins | What would change the answer |
|---|---|---|---|
| **The lab as the twin runs it** (two campaigns, no outside users) | No: nothing to speed up, and every target lands on the same day | Neither is needed: two units are 1-2 % busy. The money is better spent where the twin says it binds (metal, the atomizer, DED) | A twin in which transport binds: none of rounds 3-5 has that |
| **Floor** | If we must pay for floor by the m² (new build or lease) at about the twin's rate, **and** a 9.2 m+ bay is available or cheap, **and** Kardex's service comes in near the twin's 3 % rather than its own 10-20 % | If the lab goes into space we already have, or into an ordinary-height room | A site decision (PR 344); Kardex's service quote; the cost of a 31.5 ft room against a 14-18 ft one |
| **Outside users at 30 %** | No: slower (1.6-2.8 h against 1.3-1.9 h) | Yes, if the arm attends steps: one unit can't carry it on either plan, two can | A measured attended share at our instruments (PR 332's are assumptions) |
| **Outside users at 60 %** | No: trays bind; 6-19 % turned away, 7.6-14.3 h | Yes: two units on benches serve everything in 2 h with the twin's timing; with attended time, a third unit or fixed arms at the busiest instruments | Who the outside users are and what they send; one busy instrument a tray (the two plans tie when no tray is shared); measured handling times (at 150 s to dock and 120 s to load, one unit fails at 30 % on either plan) |
| **Only ever one unit, heavily loaded** | Partly: with a long-running battery (a bare MiR250's 13 h), the VLM's shorter drives keep every atomizer slot at 60 % outside load, where one unit on benches loses 291 runs a year | On outside service: benches still turn it around faster (5.2 h against 10.6 h). And a second unit costs about $140k, against about $0.5M for the Shuttles | Whether a second unit is really out of reach; the battery of the unit we buy (with an arm, MiR's MC250 runs 4.5 h, and then one unit loses slots on either plan) |
| **Sensitive instruments** (balances, the SEM, XRD, the nanoindenter, microscopes) | Only if measurements show tray moves harmless and requalification is unnecessary after a presentation | Yes: benches never move them | A vibration and requalification test with our instruments on a Kardex tray (the AC's microscope test is the only one, at 1 Hz) |
| **Passive storage** (1,506 powder jars, sample stores) | **Yes: this is what a VLM is for.** A store VLM can be shorter and needs no services | Not on its own: shelves plus an arm also work for this volume | Our own jar and sample counts and how often the robots fetch them (not modelled here; our count from one log is about 1.2 store visits a day for the twin's prints and lots) |
| **Reliability** | No: a Shuttle down takes 7-8 instruments with it, and recovery needs Kardex | Yes: two units back each other up, and every instrument stays reachable by hand | Kardex's figures for downtime and manual retrieval, which no vendor publishes |
| **Precedent and risk** | No: no lab runs instruments in a VLM; the AC dropped its own | Yes: Liverpool, Argonne, the A-Lab and others all fix instruments and move samples | Someone running instruments in a VLM for a year and publishing it |

**Bottom line.** Keep instruments on benches (or the floor) and add mobile manipulators as outside work grows. If a
VLM stays in the design, make it the store for powder and samples, not the home of the instruments, and size it for
that. What would make the instrument VLM worth it:

- a site where floor is scarce and dear and a tall room is cheap;
- a vibration and requalification test that comes back clean;
- Kardex answers on heat, repeatability, powered slots and service that come in near the twin's assumptions.

## 8. Sources, stand-ins and limits

**Edison** (seven queries submitted 2026-11-27 06:17 UTC; answers and full trajectories committed):

| Query | Job | Answer | Trajectory |
|---|---|---|---|
| Instruments running inside automated storage (precedent) | PRECEDENT | [answer](../out/edison/worth_it_instruments_in_storage/answer.md) | [trajectory](../out/edison/worth_it_instruments_in_storage/trajectory.json.gz) |
| VLMs and AS/RS in labs, biobanks, pharmacies | LITERATURE_HIGH | [answer](../out/edison/worth_it_vlm_lab_storage/answer.md) | [trajectory](../out/edison/worth_it_vlm_lab_storage/trajectory.json.gz) |
| Goods-to-person and VLM economics | LITERATURE | [answer](../out/edison/worth_it_goods_to_person/answer.md) | [trajectory](../out/edison/worth_it_goods_to_person/trajectory.json.gz) |
| Mobile manipulators in labs (speeds, docking, reliability, standards) | LITERATURE_HIGH | [answer](../out/edison/worth_it_mobile_manipulators/answer.md) | [trajectory](../out/edison/worth_it_mobile_manipulators/trajectory.json.gz) |
| Facility-scale automated labs and their layouts | LITERATURE | [answer](../out/edison/worth_it_lab_layouts/answer.md) | [trajectory](../out/edison/worth_it_lab_layouts/trajectory.json.gz) |
| Moving precision instruments routinely | LITERATURE | [answer](../out/edison/worth_it_vibration_moving_instruments/answer.md) | [trajectory](../out/edison/worth_it_vibration_moving_instruments/trajectory.json.gz) |
| Queueing in shared automated labs | LITERATURE | [answer](../out/edison/worth_it_shared_lab_queueing/answer.md) | [trajectory](../out/edison/worth_it_shared_lab_queueing/trajectory.json.gz) |

The script that submits, waits and fetches is [`twin/worth_it_edison.py`](../twin/worth_it_edison.py). Edison's answers
are not checked line by line; where this note leans on one, it says so.

**The research ledgers**, every figure with its URL, a short quote and a reliability tag:
[`out/worth_it/sources/vendors.md`](../out/worth_it/sources/vendors.md) (VLMs, mobile manipulators, the standards on
speed) and [`out/worth_it/sources/cases.md`](../out/worth_it/sources/cases.md) (automated labs, stores in labs,
pharmacies and biobanks, practitioners).

**Vendor documents** (read, not copied; figures and short quotes above):

- **Kardex:**
  - the Shuttle XP brochure ([reseller copy](https://www.supplycore.com/wp-content/uploads/2022/01/Shuttle-XP-Vertical-Lift-Module-1108-1.pdf));
  - two configured Shuttle 500 sheets ([option 1](https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/VLM-Option-1-96x34-Light-Specification-Sheet.pdf),
    [option 6](https://products.storemorestore.com/hubfs/StoreMoreStore/Kardex-Vertical-Lift-Module/VLM-Option-6-120x34Medium-Specification-Sheet.pdf));
  - its price and maintenance pages, power requirements and power-outage recovery.
- **Hänel and Modula:**
  - [Hänel's Lean-Lift drive](https://www.hanel.us/us/products/lean-lift/design-high-speed-drive/) and
    [its electrified containers](https://www.haenel.de/en/products/multi-space/multifunction-containers);
  - [Modula's electrified tray](https://www.modula.eu/options/tray-accessories/electrified-tray/) and
    [Modula with MiR](https://modula.us/wp-content/uploads/2022/07/Modula-and-MIR-Brochure-2022.pdf).
- **Robots:** the [MiR250 specifications](https://www.hartfiel.com/wp-content/uploads/2024/04/MiR250-Specs.pdf) and
  [MiR's MC250 one-pager](https://www.airhydropower.com/media/documents/mir/AHP-MiR-Mobile-Cobot-1-pager[2].pdf),
  UR's datasheets, and the KUKA KMR iiwa and Omron LD-250 guides.

**Practitioners.**

- **Reddit.** We tried it through the CubXL Pi's network (BYU, AS6510) over an SSH SOCKS tunnel, as the issue asked.
  On 2026-11-27, old.reddit.com redirected every search to a login page (`reason=lor2`), www.reddit.com returned 403
  to its JSON search, and the RSS search returned 404. Reddit now needs an account even from a residential or campus
  address, and we have none. Nothing was installed or written on the Pi.
- **Forums.** Eight searches of eng-tips, PLCtalk, Practical Machinist and others found no threads on operating a VLM.
  What we found instead:
  - a 2017 NIOSH investigation of a technician crushed inside a powered vertical storage machine during a repair
    ([NIOSH](https://stacks.cdc.gov/view/cdc/164913));
  - a biobank's account of two automated stores that took about four years from decision to production
    (KU Leuven, Linsen et al. 2020, via Edison);
  - a 2026 Rostock dissertation on lab mobile robots, whose failures clustered at a narrow aisle by a door and rose
    when people were near.

**Case studies.**

- **Emerald Cloud Lab:** about 15,000 sq ft and more than 100 instruments on ordinary benches, served by staff with
  carts. Its users' limit is "only one instrument capable of doing a specific procedure", not transport (Arias and
  Taylor, CMU).
- **Strateos:** moved away from its public robotic lab in 2023. Lilly's lab run with Strateos was sold to Arctoris
  in 2024.
- **The Acceleration Consortium:** its VLM records are in ac-dev-lab
  [#216](https://github.com/AccelerationConsortium/ac-dev-lab/issues/216), [#370](https://github.com/AccelerationConsortium/ac-dev-lab/issues/370),
  [#371](https://github.com/AccelerationConsortium/ac-dev-lab/issues/371), [#374](https://github.com/AccelerationConsortium/ac-dev-lab/issues/374)
  and [#471](https://github.com/AccelerationConsortium/ac-dev-lab/issues/471).
- **Liverpool:** its robot drove about 1 % of the time (our arithmetic: 2.17 km in 8 days at its 0.3 m/s cap) and
  was charged but idle 32 %. GC was the slow step (Burger et
  al. 2020). Its solid-state workflow spent 8 of 9 h on PXRD (Lunt et al. 2024).
- **The A-Lab:** furnaces in batches of eight; failures came from chemistry, not handling (Szymanski et al. 2023).
- **Samsung's ASTRAL:** one arm on a rail.
- **Ginkgo's carts and Automata's LINQ:** stacked tiers, but fixed.
- **Industrial metals labs** (FLSmidth's QCX/RoboLab, over 200 installed): instruments fixed and passive samples
  moved, with every unit operable by hand.
- **Biobanks and pharmacies:** KU Leuven's stores picked 660-1,800 tubes an hour, but 30 % of acceptance tests
  failed. NHS pharmacy robots report "sustained unplanned periods of downtime".

**Stand-ins** (each marked in `Params`):

- the handling times: driving 0.8 m/s, docking and localizing 60 s, loading 60 s, a rack pick 20 s, the camera look
  10 s;
- PR 332's attended shares;
- the outside demand (rates of 0/30/60 % of each instrument's clock, the catalogue's hours and spreads);
- the queue limit of 20, and 30 min of grace at a start slot;
- the 3 s per coupling;
- the twin's prices and space rates;
- that a running instrument holds its tray (the design's rule for unbacked loads, extended here to measurements).

**An independent review of the model** (a separate agent in this session, given the code but not the conclusions)
found five problems, all fixed before the runs reported here:

- one campaign's late atomizer job could block the other campaign's slot;
- results depended on Python's hash seed, through the order of a set of stations;
- idle time anywhere counted as charging;
- outside loads at time-critical stations jumped ahead of internal work;
- for the 26 s a tray took to dock, its instruments didn't yet hold it.

None of them changed the comparison with two units. They did change the rows with one unit:

- the replay's cascades shrank from weeks to days;
- the VLM with one unit had looked able to keep the atomizer's slots at 60 % outside load. Once idle time no longer
  charged it for free, it can't.

It also found four smaller asymmetries, which remain:

- turnaround counts only the requests served, and the VLM turns away more (this favours the VLM);
- on benches the furnace's eight positions take outside jobs independently, while on tray F they share a locked tray
  (about 3 % of outside jobs, about 0.1 h of the gap);
- an outside job can't share a tray trip with an internal job that is loaded but not yet running (slightly
  over-strict for the VLM);
- with attended time, the tray goes back to its slot once the arm's share is done, before the step ends (this bends
  the lock rule in the VLM's favour).

**Limits.**

- **A replay, not a re-plan.** The twin's decisions are fixed, so a lost slot can't be made up by choosing other work.
  The days-to-target shifts are upper bounds where slots are lost and exact where none are.
- **Missing traffic.** Store visits for powder jars and samples aren't modelled: about 1.2 a day for the twin's prints
  and lots (our count from one log), through Shuttle 2's opening. Neither are outside samples' trips from packaging (a sensitivity), failures of
  the robots or the Shuttles, maintenance windows, or the requalification after a tray move.
- **Fixed floor plans.** PR 406's flat plan is the conventional one automated as it stands. A flat plan designed for
  robots might be smaller, which would narrow the floor gap.
- **Round 5's logs** are on PR 405's branch, not this one; `run5` reads them from a directory. Its summary isn't
  written yet, so the decision-hold figures here (`python -m twin.worth_it holds <dir>`) are read straight off its
  logs.

**For a follow-up:**

1. When round 5 is final, rerun on its logs (they are on PR 405's branch):

   ```bash
   cd vertical-lab && mkdir -p /tmp/r5
   for s in $(seq 0 15); do f=r5_vertical_parallel_fast_reorder_s$s.json.xz
     git show origin/claude/twin-round5-20261127:vertical-lab/out/twin5/events/$f > /tmp/r5/$f; done
   python -m twin.worth_it run5 /tmp/r5      # out/worth_it/results_r5.json.xz, tables_r5.md
   python -m twin.worth_it holds /tmp/r5     # the decision holds (add the _dec-slow and _dec-none logs to compare)
   ```

2. Ask Kardex the six questions in [`services.md`](services.md), and for a service quote.
3. Time a MiR250 + UR12e docking, calibrating and loading at one instrument, and a Shuttle tray change with a
   coupling. These replace the biggest stand-ins.
4. Put a balance, and if possible the microscope or XRD, on a Kardex tray at Johnstone (as the AC did), with an
   accelerometer logging faster than 1 Hz. Check them against references after each presentation.
5. Searching Reddit needs a Reddit account or API credentials.

## Rebuilding

```bash
cd vertical-lab
python -m twin.worth_it run            # about 7 min on 4 cores: out/worth_it/results.json.xz and tables.md
python -m twin.worth_it sens           # about 8 min: out/worth_it/sensitivity.json.xz and sens.md
python -m twin.worth_it run5 /tmp/r5   # round 5's 16 logs, fetched as in the follow-up list above
python -m twin.worth_it tables         # the tables again from the saved results
python -m twin.worth_it_figure         # out/worth_it/worth_it.png
python -m pytest -q twin/tests/test_worth_it.py
python twin/worth_it_edison.py fetch   # the Edison answers and trajectories (needs EDISON_PLATFORM_API_KEY)
```

The model is standard-library Python. Only the days to targets (`twin.spaces`) and the figure (matplotlib) need
numpy.
