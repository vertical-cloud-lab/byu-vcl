# The two-year cut's script, round 5

Every line as spoken in `twoyears.mp4`, at its time (77 lines). Written by `python -m twin.video.cut5 script` from the templates, filled from the round's tables; edit the templates, not this file. Templates by part:

- Two simulated years of alloy discovery: round 5: `twin/video/narration5.json`
- What is simulated: the lab and two search spaces: `twin/video/narration5.json`
- Round 5: what changed in the twin: `twin/video/narration5_intro.json`
- The function networks: each experiment beside its data: `twin/video/narration_exp5.json`
- The counters, and how to read the replay's plots: `twin/video/narration5_intro.json`
- The atomizer: a design target, next to the lab's record: `twin/video/narration5_intro.json`
- The replay: two years on one seed: `twin/video/narration5.json`
- The lab comparison, like for like: `twin/video/narration5_labs.json`
- Floor space: three labs, capacity matched: `twin/video/narration_floorspace.json`
- The takeaway: `twin/video/narration5_labs.json`
- Notes: real, assumed, simulated: `twin/video/narration5_intro.json`

## 0:00 Two simulated years of alloy discovery: round 5

- **0:01** (open1) This is a simulated benchmark, in round 5: two alloy discovery campaigns, replayed for two years in a digital twin of our planned automated lab, from the day the money arrives.

## 0:13 What is simulated: the lab and two search spaces

- **0:14** (open2) Some of it comes from real sources: the lab's design and its 3-D model, footage from our own atomizer, the search spaces in the two proposals, and published prices. Everything else is simulated: every alloy, every measurement, and every result.

## 0:59 Round 5: what changed in the twin

- **1:00** (chg1) Round five starts the clock on the day the money arrives, and runs for two years. Each campaign has all of its money on day zero. The facility is ready between day 60 and day 100, and the equipment is ordered on day zero: some of it used, chosen by a rule.
- **1:18** (chg2) Experiments also start on day zero, through partners, while the lab is built. Decisions made by people take time. The conventional lab's atomizer runs at most 8 times a week; the automated lab's runs around the clock once its cell is integrated. And the HPC computes candidates continuously. Every lead time, price and decision window here is a stand-in.

## 1:43 The function networks: each experiment beside its data

- **1:43** (dag1) Each campaign is a function network: a chain of steps, where each step's results feed the next. BOFN, Bayesian optimization over function networks, models every step, not just the final score.
- **1:58** (exp1) Here is each step itself, for one alloy from each campaign: the experiment, and the data it makes. Everything is simulated by the twin, unless a label says otherwise.
- **2:11** (comp1) The aluminium alloy is design number 11042: aluminium with three additions, cerium the largest.
- **2:19** (comp2) On this map, it is one of 635 designs in this run's log. The HPC stream's 89.7 million candidates are counted, not drawn.
- **2:31** (comp3) The copper alloy is design number 91: a nickel aluminium bronze, with a little titanium.
- **2:44** (sch1) CALPHAD comes first. As the melt cools, a Scheil model follows how much of it has frozen. This curve is the one the optimizer sees.
- **2:54** (sch2) A full Scheil run on an open database adds the phases as they form. The twin's hidden truth differs again, as a real alloy would.
- **3:04** (sch3) From its curve, the network takes two numbers: the liquidus, and a hot-cracking index.
- **3:10** (sch4) Every run in round five used this open node. The Thermo-Calc stand-in was never bought.
- **3:18** (am1) The twin stands in for the AM module with a moving point source of heat. It gives the melt pool's width and depth, and how fast the metal cools.
- **3:34** (am2) This is not Thermo-Calc output, and no run bought this node. But the same model decides the porosity of every simulated build.
- **3:44** (dag2) For aluminium, the lab makes each alloy's powder itself. Then each alloy is printed, and every build is checked.
- **3:52** (atm1) This footage is real: our own atomizer, running aluminium. The size distribution beside it is the twin's, for this alloy.
- **4:01** (atm2) Here, one of three runs failed, and 13 percent of the charge ended up in the printer's size range.
- **4:09** (prt1) One build is nine cubes, each at its own laser power and speed.
- **4:20** (prt2) Each cube's density and crack reading goes on the map. Too little energy leaves lack of fusion. Too much makes keyhole pores.
- **4:30** (prt3) One build gives the network's print node nine data points.
- **4:35** (sem1) In the SEM, one electron beam scans the sample line by line, and four detectors each catch a different signal.
- **4:43** (sem2) Secondary electrons show the powder's surface. Backscattered electrons show the section's pores and cracks. X-rays give the elements, and diffraction gives each grain's orientation.
- **4:56** (sem3) Every image here is simulated by the twin, for this alloy.
- **5:01** (sem4) The network uses three of them: satellites on the powder, the section's pores and cracks, and the grain size. EDS only checks the composition.
- **5:14** (mec1) Bars are aged straight from the as-built state, then pulled. The furnace profile here is only illustrative: the twin models the strength it leaves.
- **5:23** (mec2) The curve is the twin's simulated record of the test, up to fracture.
- **5:35** (mec3) Yield strength, 244 megapascals, and elongation, 11.8 percent, are the two numbers the network keeps.
- **5:44** (dag3) For copper, a one-hour corrosion screen ranks the DED deposits, and thirty days in seawater come before a utility is known.
- **5:53** (cor1) After an hour at rest, two quick scans give an early corrosion rate and a breakdown potential.
- **6:01** (cor2) In immersion, the coupon is weighed on days 1, 3, 7 and 14. After any reading, the policy may stop it.
- **6:11** (cor3) On day 30 it is cleaned and weighed: 13.2 micrometres a year.
- **6:26** (dag4) Both campaigns share one lab. From here on, each step is an icon that lights up while it runs.

## 6:35 The counters, and how to read the replay's plots

- **6:36** (cnt1) Three counters run through the replay. Designed means computed candidates: a stream on the HPC evaluates 122,880 a day, at full capacity and outside the experiments' cost. The policy sees 64 new ones a day.
- **6:54** (cnt2) Made means powder lots, or alloys made. Tested means alloys through the full chain: in the replayed run, 104 aluminium alloys and 6 copper alloys.
- **7:06** (cnt3) Early stopping means only promising alloys finish every step.
- **7:12** (cnt4) In the replay's plots, the solid curve is the best new alloy tested so far in the automated lab, and the dashed curve is the conventional lab, on the same seed and policy. The dotted lines are the two targets.
- **7:26** (cnt5) Money is shown as cumulative spend in each lab, not as a budget bar. And when best so far goes flat, the replay says why.

## 7:36 The atomizer: a design target, next to the lab's record

- **7:37** (atm1) Once its cell is integrated, the automated lab's atomizer runs around the clock at a derived cycle: about 2.2 hours per aluminium composition, or 76 a week. That is a design target, not a demonstrated rate.
- **7:52** (atm2) It needs 6 to 8 pre-coated crucibles per alloy family in rotation, and the lab has one. The lab's record so far is 10 runs in 43 days, about 1.6 a week. Before the cell, and in the conventional lab, the twin assumes 8 a week.

## 8:11 The replay: two years on one seed

- **8:12** (rep1) The replay starts on the day the money arrives. All of it is there, for both campaigns, and every station is ordered. There is no lab yet.
- **8:21** (rep2) This is seed 1 of 16, with time-aware BOFN in the stocked automated lab: the median seed for both campaigns together. It stays the same seed to the end.
- **8:37** (rep3) Day 67. The space is ready, and equipment comes in. A station is see-through until it is online, and until the cell is integrated, people run each of them.
- **8:49** (rep3b) Meanwhile the first alloys are made on the existing atomizer and printed at the partners: the panel on the left lists what runs outside the new lab. Under each plot, a line says why its curve is not moving yet.
- **9:15** (rep4) Day 161. The Shuttles and the mobile units are integrated. From here, the run's own bookings move the 3-D model: trays to the openings and units to the docks, round the clock.
- **9:28** (rep5) Day 176: aluminium's best new alloy passes the best existing alloy on this synthetic benchmark, and on day 182, the halfway target. In the conventional lab, the same seed gets there on days 196 and 378.
- **10:57** (rep6) Day 291: copper's best new alloy passes both targets at once. In the conventional lab, this seed's copper reaches neither within two years.
- **11:33** (rep7) Now both curves are flat. With all of its money there from the start, this lab has spent 90 percent of its two years of money by day 337, and from here it mostly waits: the line under each plot says why. The conventional lab is still spending.
- **13:18** (rep8) In this seed, the automated lab's best new alloys end at 0.79 for aluminium and 0.70 for copper, and the conventional lab's at 0.77 and 0.53. One seed is an example, not a result. The comparison over all 16 seeds comes next.

## 13:41 The lab comparison, like for like

- **13:42** (lab1) Now the two labs, like for like: the same policy and the same stock rule in both, over 16 seeds each. All of it is simulated.
- **13:51** (lab2) Aluminium's first target, the best existing alloy, is a tie with the heuristic. With BOFN or pKGFN in both labs it comes 1.2 times sooner, and every interval includes one.
- **14:05** (lab3) Aluminium's halfway target comes 1.3 to 1.4 times sooner with an optimizer in both labs. With the heuristic, about half the seeds get there in either lab.
- **14:17** (lab4) Copper is where the automated lab leads: 1.5 to 2.1 times sooner with the funnel, and at least 2.0 to 2.5 times with BOFN or pKGFN.
- **14:32** (nw1) Where the automated lab does not win. Aluminium's first target is a tie: with the heuristic, the automated lab prints most of its first alloys at the same partners, before its own printer comes online around day 180.
- **14:47** (nw2) The optimizers reach that first target later than the heuristic: in the stocked automated lab, on day 176 with BOFN, against day 81.
- **14:58** (nw3) A stocked conventional lab keeps up with an automated lab that orders its metal as it goes: 0.7 to 0.9 times on aluminium's first target.
- **15:10** (nw4) And reaching a target costs the campaigns no less: about the same money with both labs stocked, and more with an optimizer when both order as they go.
- **15:21** (lab5) Where it does win: copper, with every policy and in every pairing, mostly through its own DED machine, in house from around day 228. And aluminium's halfway target, when both labs run an optimizer.
- **15:37** (mon1) Money, as spending over time. With all of it available on day zero, the automated lab has spent 90 percent of aluminium's two-year money by day 402, and of copper's by day 371. Then it idles.
- **15:52** (mon2) The conventional lab, with the same policy, spreads its spending over both years: by the end it has spent 75 percent of aluminium's money and 78 percent of copper's.
- **16:04** (mon3) Counting fixed costs, an aluminium alloy costs about 25 thousand dollars with BOFN in the automated lab, against 10 thousand in the conventional lab.

## 16:17 Floor space: three labs, capacity matched

- **16:18** (f1) Forty-three instruments, laid out three ways. These are design layouts, not built labs.
- **16:24** (f2) First, a conventional materials lab, grouped by workflow: rooms for powder, the metal printers, the machine shop, the furnace and the SEM, and open benches for the rest.
- **16:36** (f3) Benches are thirty inches deep and aisles five feet wide, with service space behind every floor machine. Measured to its walls, it comes to 4,280 square feet.
- **16:49** (f4) Next, the same floor plan, automated. Mobile robots drive the routes people walked, with fixed arms, docking targets and sample racks at the stations.
- **17:01** (f5) The floor area stays the same. And a robot docked in a five-foot aisle leaves too little room for another to pass.
- **17:09** (f6) The vertical lab. Two Kardex Shuttles come in, and every benchtop instrument moves onto a tray.
- **17:23** (f7) The floor machines rearrange along one robot aisle, and the floor area falls to 3,029 square feet.
- **17:42** (f8) Side by side. For today's 43 instruments, a flat lab laid out so robots can dock and pass needs 4,128 square feet, about what the conventional lab does.
- **17:54** (f10) For scale, Emerald Cloud Lab in South San Francisco held more than a hundred items of equipment in about 15,000 square feet.
- **18:03** (f11) But today's equipment uses only 18 of the Shuttles' 45 trays. Laid out flat, as bench positions robots can serve, all 45 need 6,192 square feet.
- **18:17** (f12) The vertical lab holds them in 3,029: 51 percent less floor, at 14.9 tray positions per thousand square feet, against 7.3.
- **18:28** (f9) In the vertical lab, most of the floor goes to the floor machines, their clearances and the robot aisle, the same as in the flat layouts for robots. And the Shuttles stand 9.15 meters tall, so it needs a high bay.

## 18:44 The takeaway

- **18:44** (take1) So, in this simulated benchmark, like for like. Copper comes sooner in the automated lab with every policy: 1.5 to 2.1 times with the funnel, and at least 2.0 times with an optimizer.
- **18:59** (take2) Aluminium's first target is a tie. Its halfway target comes 1.3 to 1.4 times sooner, and only with an optimizer in both labs. There, the policy does more than the lab.
- **19:12** (take3) And the automated lab is not cheaper. Its two-year money is spent in about 12 to 13 months, and with fixed costs each aluminium alloy costs about twice as much.

## 19:25 Notes: real, assumed, simulated

- **19:26** (note1) Everything here is simulated: the alloys, the results, and every measurement, with modelled noise not yet calibrated on the lab's instruments. The facility window, every lead time, the used-equipment prices, the decision windows, the HPC allocation, and the atomizer's design cycle are assumptions and stand-ins. It shows how two lab designs and their policies interact in a model, not what the real lab will find.
