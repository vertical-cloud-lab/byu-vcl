# Group B — Atomizer training videos 3, 4, 5, 6 (Tue Sep 29 2026)

Source: YouTube auto-captions at `/tmp/work/autosubs/<id>.txt` (no Whisper transcript existed for any of these four IDs). Captions carry no speaker labels; "trainer" = Bartosz Kalicki, inferred from content. Panel/button names are given as heard with the likely intended term, e.g. "graining pressure" → draining/pouring pressure, "ceiling rod" → sealing rod, "turbo pressure" as heard.

Chronology (inferred from content, not from the video numbers): Video 4 (loading the furnace before the first run) → Video 5 (first powder run, carbon-fiber plate, 1:1.5 booster, done by ~11:50) → Video 3 (post-run disassembly, second run with 1:1 booster + molybdenum plate, "that would be all for today") → Video 6 (powder-container fragment; position uncertain).

## txH397FGTAU — Atomizer Training Video 3 (51 min, Sep 29)

Opens with the furnace cool enough to take parts out after the morning run and the stack being rebuilt (the opening line calls it "a deep cleaning"), plus a detour on the missing 18 mm torque-wrench tip. The trainer fits the 1:1 booster and a molybdenum-alloy plate, runs the ultrasonic scan and a liquid pattern test, and explains how a straight vs angled pattern reveals plate cracks. The run documents the purge sequence (one purge cold, then purges at 250 °C and 500 °C, each vacuum + gas wash with the other vessel held at overpressure), heating to a 1000 °C set point to melt the rods, dropping to ~780–790 °C, amplitude theory (50–100 % electrical, 80–90 % best, start ~90), and the pour, during which the Mo plate cracks yet atomizes better after a piece breaks off. It ends with powder inspection, the case for wider Mo plates at low amplitude, and the end-of-day shutdown rule (everything off at ~100 °C, software locks you in until 80 °C, powder can stay overnight). Phases: after (disassembly), before (assembly, scan), during (purge, heat, atomize), after (cooldown/shutdown), theory, troubleshooting, some chatter.

### Timestamp log

| mm:ss | phase | what happens / what is said |
|---|---|---|
| 00:01 | after/cleaning | Narration: "this video is a deep cleaning"; post-run disassembly, long silent stretches. |
| 01:33 | before | Trainee asks whether a part's orientation matters; trainer: "Not at all" (part not named). |
| 03:28 | after | Furnace cool enough to take out the parts; parts put back in; "I forgot to put this in". |
| 05:01 | tools | "The 18 mm wrench will be a must"; buy a set at Ace Hardware. |
| 06:37 | tools | Torque wrench should have an "80 mm" (likely 18 mm) tip but it was not shipped; induction-only kits get mis-packed. |
| 07:44 | chatter | Company bureaucracy; AMAZEMET grew from ~10 to 60+ people (11:36). |
| 09:14 | after | "It did go all the way through, so we can reuse it" (melt poured fully; part reusable, inferred crucible). |
| 09:19 | tools | Small tweezers "exceptionally useful": one pair for nuts, one for grabbing anything. |
| 09:40 | lesson | Disassembly went easily "because the oxygen level was much better"; oxide roughens surfaces and makes parts stick. |
| 10:11 | parts | Plate is a molybdenum alloy; best option for Al, but Mo and Al react if the process runs too long. |
| 12:04 | troubleshooting | First scan showed a double peak/interruption; a short burst of vibration seated the parts; micro-friction self-resolves. |
| 12:42 | before | Liquid pattern on plate: straight = plate vibrating well; angled = crack forming, atomization goes around it. |
| 13:06 | theory | Plan: 1:1 booster now; reversed booster can give really small Al particles but needs alloy and pour knowledge. |
| 13:47 | chatter | Gage: powders for LPBF characterization, lower-rare-earth alloys. |
| 14:33 | theory | Low-density metals give bigger particles; Au/Ag much smaller, same technique; spherical, narrow distribution stays usable. |
| 15:21 | theory | Commercial Al powder 15–45 µm; this is larger but uniform and spherical; still good for printing (Northwestern paper). |
| 16:12 | before | "Everything in, vibrations fine, so purging." 1:1 booster is slimmer; amplification depends on mass/diameter difference. |
| 16:44 | during | Purge plan: one purge without heat, then two with heat; each = vacuum pump then gas wash. |
| 17:10 | troubleshooting | Gas "coming out here"; check how far it screws in — if it won't, it did not seat (closure not named). |
| 17:55 | during | One side at overpressure while the other purges, then reverse; two temperatures to drive moisture out of new insulation/crucible. |
| 18:34 | theory | Magnesium gives the largest particles (light); gold and copper alloys much smaller, same plate and booster. |
| 19:21 | theory | First-run powder: narrow distribution, perfect for DED; maybe too big for LPBF. |
| 20:00 | after | Shake the jar: bigger particles rise to the top; grains iridescent. |
| 20:18 | during | Panel: last state melting pressure; now vacuum pump on, "turn off that and then" (sequence garbled). |
| 21:03 | during | Heat up (first heated purge). |
| 21:58 | during | Vacuum at its max but reading still falling; in vacuum the oxygen sensor "is not going to tell you anything". |
| 22:31 | chatter | Software versions differ; trainer reported UI issues; three cabinet generations. |
| 23:28 | during | Press pressure control; get coolant flow; start heating. |
| 30:16 | during | Set point changed to 500 °C; pump stays on gas wash; a leak in between would show as pressure loss. |
| 31:05 | parts | Plate check: edge peeling/cracking OK if loose bits removed; heavy oxide after an oxygen-rich run → clean fully or new plate; scrape with knife. |
| 32:41 | during | "Melt pressure. Turn off pressure control." |
| 32:58 | theory | Automate the 250/500 purge sequence? No: no control over the furnace controller; its software is locked ("a punch card"). |
| 34:15 | during | Repeat purge? "Don't depend on this reading with vacuum inside — fill protective gas, then check; if good, no repeat." |
| 34:48 | theory | The more runs, the better: heat and vacuum clean the system. |
| 35:02 | during | Set max temperature 1000 °C to melt the rods. |
| 37:34 | during | At 1000 °C the Al melts; "when the whistle goes" the Al jumps up in the middle — induction pull, free mixing. |
| 38:38 | during | As soon as it melts, go down; for a metal plate ~780–790 °C is enough; lower temperature = plate durability. |
| 38:55 | theory | Lower amplitude is kinder to the plate but can under-atomize (material flows through); start higher, reduce later. |
| 39:26 | theory | Lower amplitude = smaller particles but slower, more fragile; booster = mechanical control, generator % = electrical. |
| 40:00 | parameter | Amplitude 50–100 % = share of generator max current; 100 high; 80–90 best; start ~90 and adjust. |
| 40:55 | before | Ultrasonic scan test; turn on transducer cooling first. |
| 41:14 | parts | Cooling here is fully manual; newest version stops it 1 min after vibration; plasma runs up to 4 h continuous. |
| 41:48 | during | Start sequence: vibration on, draining pressure, sealing rod, turbo pressure — "do it all as quickly as possible". |
| 42:14 | during | "More amplitude." Pouring a bit too much; use the draining pressure; "too much pressure makes it shoot out too fast". |
| 43:05 | troubleshooting | Some of the plate is broken; pouring higher on the plate might help. |
| 43:48 | troubleshooting | Plate cracked on one side — interrupts atomization. |
| 44:46 | during | Pressure lowered a little; "really good for a moment"; done, stop the vibration (45:07). |
| 45:11 | lesson | After another piece broke, atomization improved: rolled/cut Mo plates hold tension points; "faulty from the factory probably". |
| 46:05 | after | Nice powder in the container; inspect under a light; "could be better". |
| 47:00 | after | Can this be turned off? No — wait for cooling too. |
| 47:28 | parts | Wider/longer Mo plates recommended for Al; larger area helps most at low amplitude. |
| 49:29 | parts | Wider Mo plate shown; use it for the lowest-amplitude reverse-booster run (needs more time to wet). |
| 49:52 | after | Done for today; full cooldown takes a while; come back in ~30 min. |
| 50:06 | after | Shutdown at ~100 °C: heat exchanger off, close water, compressed air, argon, then power; any order. |
| 50:30 | after | Software will not let you leave the program until 80 °C. |
| 50:46 | after | Powder can stay in the chamber overnight; it only cools more slowly; trainer often does this. |

### Procedural steps
Before
- Fit the booster for the run (1:1 here; it is the slimmer one) (16:16).
- Run the ultrasonic scan; on a double peak, give a short burst of vibration and rescan (12:04).
- Wet the plate and check the pattern: straight = good, angled = crack (12:42).
- Inspect the plate; peel or scrape loose flakes with a knife; replace heavily oxidized plates (31:05).
- Turn on transducer air cooling before vibrating (40:55).
During
- Purge once cold, then at 250 °C and 500 °C: vacuum pump then gas wash, other vessel at overpressure (16:44, 17:55, 30:16).
- Fill with protective gas before trusting the oxygen reading (21:58, 34:15).
- Press pressure control, start coolant flow, start heating (23:28).
- Switch to melt pressure and turn off pressure control before melting (32:41).
- Set 1000 °C to melt the rods; drop to ~780–790 °C once molten (35:02, 38:38).
- Set amplitude ~90 %; stay between 80 and 100 (40:00).
- Start the pour: vibration on → draining pressure → sealing rod up → turbo pressure if needed, quickly (41:48).
- If melt shoots out too fast, lower the pour pressure (42:54, 44:46).
- Stop the vibration when the pour ends (45:07).
After
- Keep cooling running; at ~100 °C shut down heat exchanger, water, air, argon, power (47:00, 50:06).
- Exit the program only below 80 °C (50:30).
- Powder may stay in the chamber overnight (50:46).
Cleaning
- Disassemble once the furnace is cool; low-oxygen runs leave parts unstuck (03:28, 09:40).
Troubleshooting
- Angled pattern or half-plate atomization = cracked plate (12:42).
- Gas escaping at a closure: check it screws fully home (17:10).
- Mo plate cracking mid-run may release tension and improve atomization; replace the plate afterwards (45:11).

### Parameters and numbers
| value | context | mm:ss |
|---|---|---|
| 18 mm | wrench / torque-wrench tip needed (heard "80 mm") | 05:01, 06:37 |
| 15–45 µm | commercial Al powder size for comparison | 15:21 |
| 1:1, 1:1.5 | booster ratios in use | 16:18, 13:14 |
| 1 cold + 2 heated | purge count | 16:44 |
| 250 °C, 500 °C | heated purge temperatures | 33:03, 30:16 |
| 1000 °C | set point to melt rods | 35:02 |
| 780–790 °C | hold temperature with a metal plate | 38:48 |
| 50–100 % | amplitude range (generator current) | 40:00 |
| 80–90 %, start ~90 | recommended amplitude | 40:17, 40:34 |
| 1 min | newest-version auto cooling after vibration | 41:17 |
| 4 h | plasma continuous atomization | 41:25 |
| ~30 min | come back to shut down | 50:06 |
| ~100 °C | shutdown threshold (heard "100, 114") | 50:19 |
| 80 °C | program exit threshold | 50:36 |

### Quotable moments
- 09:51 "If there is no oxygen, suddenly nothing sticks to other parts. The oxide makes the surface rough and that's what makes it stuck."
- 10:35 "The same reactivity that helps us get good wetting and a good atomization start, at some point may cause the plate to be damaged."
- 12:42 "If the pattern is straight, the plate is going really well. If the pattern is angled, it usually means there is a crack formation."
- 18:05 "You do it at two temperatures to remove all the moisture. New insulation, new crucible may hold moisture; the heat gets it out and the purge removes it."
- 37:39 "When the whistle goes, the aluminum jumps up in the middle. Induction is pulling it. So it also gives us some of the mixing, which is good."
- 38:43 "For the metal plate we don't need to go so high. We will be fine at 780, 790. It's not much, but it has a high impact on the durability of the plate."
- 40:17 "High is 100. 80 to 90 is the best. Lower means there is a chance of no atomization because the vibrations are too weak. Start around 90 and adjust."
- 45:23 "Metal plates, based on how they were rolled and cut, have tension points when heat is applied; when they break, the atomization can actually do better."

### Unclear / needs checking
- "80 mm tip" (06:37) is almost certainly the 18 mm tip; confirm against the torque-wrench kit.
- 01:33 (orientation), 09:14 (what "went all the way through"), 17:10 (which closure "didn't seat"), 20:18 (panel state) are garbled.
- 250 °C for the first heated purge comes only from the trainee's question at 33:03; the trainer's own set points shown are 500 and 1000.
- Shutdown threshold heard as "100, 114" (50:19); treat as ~100 °C.
- Video numbering (3 before 4 and 5) does not match the apparent chronology.

## 1F9_4ccwhss — Atomizer Training Video 4 (10 min, Sep 29)

Loading the induction furnace before the first run: aligning the insulation hole with the thermocouple port, placing the flexible thermocouple close enough, fitting the silica/alumina side insulation, checking the sealing rod tip is clean and undamaged, removing a "sealing block", adding the Al rods, and closing the furnace lid with its adjustable latch. Theory interludes cover indirect induction heating through graphite, the 1600 °C capability and why Fe/Ni are not intended, and why long rods need a higher initial temperature. The second half is a chamber-cleaning walkthrough: brushes, paper and alcohol, a stainless scraper for stuck particles, vacuum first, view-port hook wrench, the swing-out cone, brushing powder down into the container, and a room oxygen-sensor discussion. Phases: before (loading), theory, cleaning/after.

### Timestamp log

| mm:ss | phase | what happens / what is said |
|---|---|---|
| 00:00 | before | Side insulation being placed; Gage invited to feel how tight the assembly gets. |
| 00:31 | before | Hole in insulation must line up with the thermocouple port; thermocouple is flexible, can bend, must get close enough. |
| 00:53 | before | "Maybe a little bit too far" — thermocouple position corrected; then side insulation (01:01). |
| 01:08 | parts | Insulation is a silica and alumina mix; dusty — vacuum the furnace area, especially if something falls in the crucible. |
| 01:41 | parts | "If it falls, it will immediately break"; get it into the hole first (graphite sealing rod, inferred). |
| 01:52 | before | Sealing rod tip must be clean and undamaged: "if it's damaged here, it will just not seal". |
| 02:10 | before | Wipe or vacuum residual dust; "ready to go". |
| 02:18 | before | Remove the "sealing block"; now add the material. |
| 02:39 | theory | Sterling: copper coils, eddy currents; trainer: this is indirect — energy goes into the graphite, graphite heats the charge. |
| 03:35 | theory | Not designed for iron/nickel: melting point too high; plates would not survive; those metals react with graphite. |
| 03:47 | parameter | Generator has enough energy to go up to 1600. |
| 04:05 | theory | Industrial gas atomizers use ceramic crucibles, slow heating, large ceramic nozzles; this unit is built for precious metals. |
| 04:32 | before | "We always need to clean the feedstock. It's really important." |
| 04:37 | before | Rods stand above the furnace; they go down as they melt. |
| 04:43 | lesson | Long rods heat at the bottom and cool at the top: raise temperature first, then decrease; copper sticking out is very hard to melt. |
| 05:08 | theory | The more compressed the material at the bottom, the faster it melts. |
| 05:17 | before | Close and secure the furnace lid; if it hisses, loosen and adjust the latch to tighten. |
| 05:41 | cleaning | Next: the chamber. Cleaning uses brushes, paper and alcohol only (06:01). |
| 06:09 | cleaning | Particles stuck to the wall (with "thinner"/tin-like materials): stainless-steel scraper; cooled particles stick, they do not melt in. |
| 06:34 | cleaning | Copper or softer scraper is fine; a plastic one may get damaged. |
| 06:51 | cleaning | Clean the sealing surface and the seal; wipe the whole chamber; vacuum first (07:12). |
| 07:24 | safety | Trainee: full-face respirators go on for post-run cleaning. |
| 07:33 | theory | Atomization runs also help clean the equipment (heat removes residue; garbled). |
| 07:49 | parts | View port comes out with a hook wrench. |
| 08:08 | cleaning | The cone below swivels out; take it down to remove all powder; clean and vacuum its seal from below (08:38). |
| 08:47 | cleaning | Brush in a circle so powder falls into the container; do this before removing the container (09:17). |
| 09:30 | safety | "You can't operate until you get an oxygen sensor"; trainer: argon flow is small, but agrees one should be fitted. |
| 09:52 | parts | Last item: the powder container, made in-house; a few commercial powders shown. |

### Procedural steps
Before
- Align the insulation hole with the thermocouple port; bend the thermocouple so it sits close to the crucible (00:31).
- Fit the side insulation; vacuum the dust it sheds (01:01, 01:11).
- Inspect the sealing rod tip for cleanliness and damage before inserting it into the nozzle hole (01:52).
- Remove the sealing block, then load the cleaned feedstock (02:18, 04:32).
- Close and secure the furnace lid; re-adjust the latch if gas hisses out (05:17).
During
- For long rods, overshoot the temperature to melt the bottom first, then reduce (04:43).
Cleaning
- Vacuum the chamber first, then wipe with brushes, paper and alcohol (07:12, 06:01).
- Scrape stuck particles with a stainless-steel scraper; avoid plastic (06:19, 06:34).
- Clean the sealing surface and seal; unscrew the view port with a hook wrench if needed (06:51, 07:55).
- Swing out the cone, clean and vacuum its seal, brush powder down into the container before removing the container (08:08, 08:47, 09:17).
Troubleshooting
- A hissing furnace lid means the latch needs tightening (05:20).

### Parameters and numbers
| value | context | mm:ss |
|---|---|---|
| silica + alumina | side insulation material | 01:08 |
| 1600 | max temperature the generator can reach (°C, inferred) | 03:47 |
| brushes, paper, alcohol | only cleaning consumables needed | 06:01 |
| stainless steel | scraper material | 06:33 |

### Quotable moments
- 01:57 "If it's damaged here, it will just not seal."
- 03:12 "The indirect one is that most of the energy goes into the graphite, and then the graphite is heating the material inside."
- 03:47 "It has enough energy to go up to 1600. The problem is that most of the plates are not going to survive it, and those materials are very reactive to graphite."
- 04:43 "With rods this long, you heat them at the bottom and they tend to cool down here. So we need to increase the temperature first to melt them at the bottom, then decrease."
- 05:08 "The more compressed, especially at the bottom, the material is, the faster it will melt."
- 06:01 "Most of it is just made with brushes, paper, and alcohol. You don't need anything else."
- 06:21 "Because everything is cooled down, they do not melt into the chamber. They just get stuck and you need to scrape them."

### Unclear / needs checking
- "Sealing block" (02:18): a spacer/lock removed before loading; exact part unknown.
- What "immediately breaks if it falls" (01:41); sealing rod is an inference.
- "Thinner or similar materials" (06:14) that stick to the wall — possibly tin.
- 07:33 (atomization helping to clean) is garbled.

## 58wJ_Khwgyk — Atomizer Training Video 5 (79 min, Sep 29)

The complete first powder run, start to finish. Setup: powder container types, splash-protection plates, the gold-melting catch bowl, chamber covers, then the ultrasonic stack (piezo transducer with air cooling and LEMO cable, 1:1.5/reversed/1:1 boosters, titanium connector rod M10/M8, titanium sonotrode, carbon-fiber plate) torqued to 65/60/50 N·m with the plate tightened in the housing, scan at ~40 kHz, wet test and plate positioning. Atmosphere: chamber overpressure with O2-sensor bleed, five automatic furnace purges, chamber vacuum to the altitude-limited floor, protective-gas refill, then repeats at 250 °C and ~500 °C, with a "pressure crucible" warning diagnosed as a chamber-to-furnace leak. Melt: set 1000 °C to drop the rods, hold ~790 °C, wait exactly 2 min, then pour with sealing rod up, draining and turbo pressure, steering the stream by plate position; oxygen rose and bent the stream. After: stop sequence, cool to ~400 °C to open, vent before opening, respirators, brushing, slag, ~1 h cleaning for a material change. Phases: before, during, after, cleaning, theory, troubleshooting, safety, some chatter.

### Timestamp log

| mm:ss | phase | what happens / what is said |
|---|---|---|
| 00:00 | parts | Powder container types: this one shows its contents and has a built-in valve; a stainless tube is simpler, valve added separately. |
| 00:18 | parts | AMAZEMET keeps this type for induction and waste circulation; otherwise plain stainless — easier to make and clean; have both. |
| 00:54 | cleaning | No powder yet, so compressed air may blow out paper-towel dust; never with powder inside (01:32). |
| 01:38 | context | First rod run; AMAZEMET avoids running powder on the production side; long runs were for an automated plasma system. |
| 02:21 | parts | Protective plates: hot metals like copper splash if atomization goes wrong; plates stop splashes entering the container. |
| 02:47 | before | For aluminum one protective plate is enough; splashes stick there, powder falls past. |
| 03:44 | before | Mounting the container is easier with two people: lift and clamp at the same time. |
| 04:08 | before | First process uses the booster already in the housing → "large" powder; easy, good for training, but big particles. |
| 04:48 | before | Finger-tighten the container flange. |
| 05:01 | before | A jewelry gold-melting bowl goes in the chamber for safety; catches un-atomized melt for reuse; graphite would also work. |
| 05:41 | before | Wipe the plate; hang covers over chamber openings/door so powder can be swept from the edge (05:50). |
| 06:40 | parts | Stack base: transducer = stack of piezo discs; compressed-air cooling; LEMO cable brings the generator signal. |
| 07:00 | safety | Transducer care: don't drop, heat, wet or overheat; always air-cool; "one mistake can actually damage it". |
| 07:20 | parts | If the air line were closed the system would still see pressure but give no cooling. |
| 07:38 | cost | Repair ~2,000 (piezo plates swapped); cheap online transducers fail; theirs come from a Polish industrial maker (08:02). |
| 08:21 | parts | Booster: mechanical amplifier; its ring acts like a spring, so it can be held there without affecting vibration. |
| 08:43 | parameter | Boosters: 1:1.5 gives 150 % amplitude; reversed it reduces; 1:1 in the middle (09:22). |
| 08:56 | theory | Reversed booster on Al → smallest particles but needs good wetting and slow pouring; more energy → larger particles, faster, pour more. |
| 09:24 | theory | 1:1 used for copper and magnesium; not every material atomizes at low amplitude. |
| 09:48 | lesson | Amplifying booster "will immediately destroy all the plates"; metal plates crack; reversed gave several Al runs without damage. |
| 10:28 | parts | Connector rod: titanium, prolongs the stack; M10 at the base, M8 at the tip (10:44). |
| 10:59 | cleaning | Clean threads with IPA; if problems start, unscrew everything and clean all threads (cavitation dust). |
| 11:19 | parts | Sonotrode: titanium alloy; M8 at the top means a smaller hole in the plate → more contact surface. |
| 11:53 | parts | For Al a bare carbon-fiber plate works: Al wets and penetrates it; large particles; up to ~10 processes (12:11). |
| 12:39 | theory | Silicon was atomized on CF with induction; unpoured Si expands on cooling and cracks the crucible (13:02). |
| 13:30 | parameter | Torques 65 N·m, 60 N·m, 50 or 55 N·m (50 safer): ultrasound must pass; too tight damages threads, loose = friction. |
| 14:38 | before | Tighten in a vise (best) or on the floor; AMAZEMET uses machined aluminum soft jaws; 18 mm flat wrench needed (15:25). |
| 15:46 | troubleshooting | A damaged sonotrode would show in the scan. |
| 16:59 | before | Torque wrench: pull collar down, rotate so the 60 and 65 marks align → 65 N·m; it clicks when done (17:30). |
| 17:38 | before | "Now it's 60"; the final (plate) torque is done with the stack already in the housing. |
| 18:10 | before | Hold the stack, but don't push the stiff cable/hose back too much; elbow fittings on order (18:47). |
| 19:03 | before | Transducer goes in its cover so nobody hits it; rotate slightly to catch material; clamp only snug (20:18). |
| 21:50 | parameter | Full run with cleaning and prep: ~1 h for Al; longer for higher-melting metals. |
| 22:10 | before | Once connected, run a scan: a little over 40 kHz is right; scan also checks impedance. |
| 22:56 | theory | Holding the vibrating tip heats it instantly; damping shifts frequency; squeaking = loose parts → reassemble (23:18). |
| 24:18 | parameter | All energy passes through the transducer: 300–500 W may trip it; expect ≤100–150 W here, ~50 W on most plates. |
| 24:49 | before | Insert stack into housing; clamp over, not touching the safety cover; add the final clamp. |
| 25:11 | parts | View ports: hardened glass standard, borosilicate optional; furnace window is glass-ceramic; none ever broke. |
| 25:43 | before | Centre the plate; hand-tight then wrench to 50 N·m with counter-hold; arrow shows torque direction (26:02). |
| 26:39 | before | Rescan; power is higher with the plate attached. |
| 27:32 | troubleshooting | Wet test shows spread over the whole surface; a crack makes only half the plate atomize (top yes, bottom no). |
| 28:18 | parts | Plate clearly visible through the view port; a phone holder/camera could go there. |
| 28:46 | before | Plate holder moves up/down/left/right; melt should land as high as possible without going over the top. |
| 29:21 | before | Loosen to turn; up/down needs simultaneous rotation; final adjustment at the first flow (30:32). |
| 30:52 | during | Atmosphere: 5 furnace purges + 2 chamber purges at overpressure, repeated at 250 °C and 500 °C for moisture. |
| 31:17 | theory | Worth it for Mg or Al (low oxygen gives good flow); for bismuth one purge and opening at 300 °C sufficed. |
| 31:57 | before | Argon and compressed air on; cooling not needed until heating starts. |
| 32:05 | during | Chamber overpressure: system auto-adds or vents; the hiss is the oxygen-sensor bleed; valve sets a small flow (32:44). |
| 33:00 | safety | Machine will not block a run on bad O2; you watch the value and set alarms yourself. |
| 33:22 | during | Graphite seals leak between furnace and chamber, so purge one side while the other holds overpressure. |
| 33:49 | during | Vacuum pump on, press gas wash: furnace runs 5 purge cycles automatically; it has no sensor. |
| 34:16 | theory | Hot graphite purifies itself. |
| 34:39 | troubleshooting | "Pressure crucible" warning: furnace not reaching −1 bar; gas leaking chamber→furnace, maybe sealing rod; still workable. |
| 36:14 | troubleshooting | Not reaching −1 = leak; chamber→furnace acceptable, from outside worse; later swap sealing rod/crucible to test (36:27). |
| 37:24 | during | "Cooling water flow low" warning — chiller not on yet. |
| 37:35 | during | After the last cycle (counter shows 1) manually press melting pressure, then overpressure, then vacuum the chamber (38:12). |
| 38:28 | during | Chamber vacuum needs the pump running and the big valve open; furnace valve clicking = argon leaking into chamber (OK). |
| 39:31 | during | Wait until chamber pressure stops changing; −1000 mbar at sea level, less at altitude (reading garbled). |
| 40:10 | during | Fill protective gas; cycle again ("52, heat it up" — garbled); remove all oxygen and moisture. |
| 40:55 | theory | Plasma variant: gas flow all the way through heats the gas in the filters. |
| 41:12 | during | Second cycle: pressure control to 150; read O2 only at pressure, not in vacuum; value drops then stabilizes. |
| 41:51 | during | Start heating: coolant flow, big switch on, no error, set 250 (heard "50"); press generator start (42:22). |
| 42:31 | safety | Hearing protection: use it now; ultrasonic vibration is the worst even if it does not bother you. |
| 42:50 | during | To 250 °C almost instantly, always overshoots; vacuum again — gas wash always needs the vacuum pump (43:05). |
| 43:12 | theory | Heat evaporates moisture; coatings dry off. Smells: pump oil, hot graphite/metal from the vent, filtered (43:44). |
| 44:19 | parts | Door lock engages whenever pressure is off atmospheric. |
| 45:08 | during | Last cycle → overpressure; now the chamber: pump has its own furnace valves, chamber big valve is opened manually (45:22). |
| 46:45 | theory | Frequency is fixed by hardware (generator, transducer, sonotrode matched); a different set costs under 50,000. |
| 47:22 | theory | No 20 kHz for induction; 60 kHz offered but sensitive and hard on parts — explore 40 kHz first. |
| 48:01 | during | Oxygen falling; set point up to ~500 °C to drive out moisture. |
| 49:38 | during | Rods standing up will melt "like a stick of butter". |
| 50:11 | safety | First powder run: full-face respirators for cleaning; ventilation status unknown, call facilities (50:37). |
| 51:08 | during | Melting pressure; O2 rose slightly from heat/evaporation; the filter releases moisture in the first runs. |
| 51:48 | parts | Chamber cooling is very good — condensation can appear inside; water exceptionally cold; one exchanger enough (52:33). |
| 52:50 | during | Al hold ~790–800 (CF plate can go higher); set 1000 to melt the rods, then lower to 790 (53:14). |
| 53:28 | safety | Ventilation checked with a sheet of paper. |
| 54:24 | safety | At 1300 °C it is too bright to watch — use a filter or glasses. |
| 55:06 | theory | Whistling is the induction; it pulses to hold temperature. |
| 55:23 | during | Temperature falls as the rods melt; lower the set point; a packed charge melts easier; a lid shields the crucible (55:45). |
| 57:22 | during | Stabilized; once all liquid wait 2 min — measured lag between crucible-wall thermocouple and melt. |
| 58:43 | during | Do not wait longer than 2 min — more oxidation, more reactivity; then pour. |
| 58:53 | during | Best results need an operator at the window adjusting amplitude, turbo pressure and plate position. |
| 59:51 | during | Start: vibrations on; sealing rod up; draining pressure pushes the melt; turbo pressure when necessary. |
| 60:27 | during | Stream lands too far — move the plate; "too much"; then better, more area covered, pour a bit higher (60:53). |
| 61:07 | during | Once the plate is hot every drop atomizes; initial losses heat the plate; metal plates heat faster (61:34). |
| 62:12 | during | End: turbo pressure to clear the nozzle; sealing rod down; melting pressure; generator stop; ultrasonics stop. |
| 62:24 | lesson | O2 rose a lot; oxide at the nozzle bends the stream — compensate with plate position (62:54). |
| 63:24 | after | Heating stopped; temperature dropping. |
| 63:28 | idea | Laser pointer on the sealing-rod arm or holder to mark plate position — "not very hard". |
| 63:58 | theory | Aim higher on the plate: longer contact, more heating, all atomized instead of droplets. |
| 64:22 | after | Powder in the container plus some in the bowl to brush; repeat, then compare 1:1 booster + metal plate (65:08). |
| 65:22 | lesson | No parameter log exists — record parameters by hand. |
| 65:37 | after | Around 400 °C the furnace/chamber can be opened to speed cooling. |
| 65:41 | troubleshooting | Drips on coolant lines are condensation, more at top temperatures. |
| 66:20 | parts | Chamber water jacket: stainless channels cast in. |
| 66:49 | after | Over ~400 open the chamber; everything inside is cold; "just don't touch the [nozzle]". |
| 67:20 | cleaning | Brushes push powder down; different sizes for different materials. |
| 67:38 | cleaning | Material change in induction mode: vacuum, wipe; ~1 h; scrape anything melted on (68:02). |
| 68:26 | after | Around 100 °C you can shut down. |
| 68:51 | parts | CF plate is reusable if intact; the bowl can be removed and cleaned (69:37). |
| 70:10 | theory | Process is short; prepare the next charge while cooling. |
| 71:41 | theory | Lower amplitude lets plates survive higher temperature; metal plates want the amplitude-reducing booster (72:04). |
| 72:18 | parts | CF rarely destroyed with Al; coated CF for copper wears out; metal plates crack, hole, piece falls off. |
| 73:48 | safety | Full-face respirators labelled; visor sticker replaced instead of the mask (75:02). |
| 76:16 | after | Slag always remains at the crucible bottom; paper or tray under parts catches powder to return (76:24). |
| 77:17 | safety | Always release the pressure — vent the chamber before opening. |
| 77:48 | cleaning | Same material next, so open and brush only; gloves, respirator. |

### Procedural steps
Before
- Mount a splash-protection plate above the container (one for Al) (02:38).
- Lift and clamp the powder container with two people; finger-tighten the flange (03:44, 04:48).
- Place the gold-melting bowl in the chamber to catch un-atomized melt (05:01).
- Wipe the plate; hang the covers over the chamber openings (05:41).
- Assemble transducer → booster → titanium connector rod (M10/M8) → sonotrode; IPA on threads (10:28, 10:59).
- Torque in a vise with soft jaws: 65 N·m, 60 N·m; plate 50 (or 55) N·m after mounting in the housing (13:30, 17:38).
- Set the torque wrench: pull the collar down, rotate to the mark, listen for the click (16:59).
- Connect air cooling and LEMO cable; put the transducer in its protective cover (06:46, 19:03).
- Run the ultrasonic scan: expect ~40 kHz and a pass (22:10).
- Insert into the housing; fit both clamps without touching the safety cover (24:49).
- Torque the plate at 50 N·m while counter-holding; follow the arrow (25:43).
- Rescan, then wet-test for atomization over the whole plate (26:39, 27:32).
- Position the plate so melt lands high but not over the top; final adjustment at first flow (28:46, 30:32).
- Confirm argon and compressed air are on (31:57).
During
- Set chamber overpressure; set a small flow through the oxygen sensor (32:05, 32:44).
- Vacuum pump on, press gas wash: furnace runs 5 purges while the chamber holds overpressure (33:49).
- After the last cycle press melting pressure, then overpressure, open the big valve, vacuum the chamber (37:35, 38:12).
- Wait until chamber pressure stops changing, then fill protective gas (39:31, 40:10).
- Use pressure control (150) to read oxygen at pressure (41:12).
- Coolant flow on, big switch on, set 250 °C, press generator start (41:51, 42:22).
- Put on hearing protection (42:31).
- Repeat vacuum/gas wash at 250 °C, then at ~500 °C (43:05, 48:01).
- Switch to melting pressure (51:08).
- Set 1000 °C to melt the rods; lower to ~790 °C as they go down (52:50, 55:23).
- Wait 2 min after everything is liquid, no longer (57:22, 58:43).
- Pour: vibrations on, sealing rod up, draining pressure, turbo pressure as needed; steer with the plate (59:51).
- End: turbo pressure to clear the nozzle, sealing rod down, melting pressure, generator stop, ultrasonics stop (62:12).
- Write down the parameters; there is no log (65:22).
After
- Open the chamber around 400 °C to speed cooling (65:37, 66:49).
- Vent the chamber before opening it (77:17).
- Shut down at ~100 °C (68:26).
- Brush powder from plate, bowl and walls into the container; paper or tray under parts (67:20, 76:24).
Cleaning
- Use compressed air only when no powder is present (01:20).
- Material change: vacuum everything, wipe all surfaces (~1 h); scrape melted-on material (67:38, 68:02).
- Same material next: open and brush only (77:48).
- If the stack squeaks or misbehaves: unscrew, clean all threads, reassemble (23:40).
Troubleshooting
- Furnace not reaching −1 bar = leak; chamber→furnace acceptable; swap sealing rod/crucible if it persists (36:14, 36:27).
- "Cooling water flow low" = chiller not on (37:24).
- Half-plate atomization in the wet test = crack (27:49).
- Stream bending at the nozzle = oxide; adjust the plate (62:24).
- Drips on cold lines are condensation (65:41).

### Parameters and numbers
| value | context | mm:ss |
|---|---|---|
| ~2,000 | transducer repair cost (new guessed 5–10k, currency unstated) | 07:38 |
| 1:1.5 (150 %), reversed, 1:1 | booster options | 08:43 |
| M10, M8 | connector rod threads | 10:44 |
| ~10 processes | carbon-fiber plate life with Al | 12:11 |
| 65 / 60 / 50–55 N·m | stack torques | 13:30 |
| 18 mm | flat wrench size | 15:25 |
| ~1 h | full run incl. prep for Al | 21:50 |
| ~40 kHz | scan frequency, "a little over" | 22:24 |
| 300–500 W | may trip the transducer | 24:26 |
| 100–150 W, ~50 W | expected power here / most plates | 24:32 |
| 50 N·m | plate torque in housing | 26:02 |
| 5 + 2 | furnace / chamber purges per cycle | 30:52 |
| 250 °C, 500 °C | heated purge temperatures | 31:01 |
| 300 °C | bismuth: furnace opened right away | 31:37 |
| −1 (bar) | furnace vacuum target | 36:14 |
| −1000 mbar | chamber vacuum at sea level | 39:39 |
| 150 | pressure-control target for the O2 reading | 41:18 |
| 250 (heard "50") | first heating set point | 42:07 |
| <50,000 | cost of a different frequency set | 47:02 |
| 20 / 40 / 60 kHz | frequency options | 47:22 |
| ~500 °C | second heated purge | 48:06 |
| 790–800 °C | Al hold temperature | 52:53 |
| 1000 °C | melt set point | 53:38 |
| 1300 °C | too bright to watch unfiltered | 54:26 |
| 2 min | hold after full melt | 57:29 |
| ~400 °C | open chamber | 65:37 |
| 11:38 | clock time at opening | 67:16 |
| ~1 h | cleaning for a material change | 67:46 |
| ~100 °C | shutdown threshold | 68:26 |

### Quotable moments
- 07:00 "Don't drop it, don't heat it, don't expose it to moisture, don't overheat it. Always have the compressor cooling, because it's pretty expensive."
- 09:48 "The stronger one will immediately destroy all the plates. For metal plates I don't recommend to use this one, because they crack."
- 13:51 "If you go higher, you can damage the thread. If you have it loose, you just have friction between the parts and the ultrasonic vibration doesn't go through."
- 33:22 "The graphite seals are not perfect. We have leaks between the furnace and the chamber. That's why I'm purging one side, keeping overpressure on the other."
- 36:18 "If it's a leak from the chamber to the furnace, that's acceptable. If it's a leak from the outside, it's worse."
- 57:32 "We have measured that 2 minutes is how much it takes for the temperature of the crucible at the wall to be the same as the temperature of the metal."
- 58:43 "We don't want to wait longer than 2 minutes, because it can cause more oxidization, more reactivity. As much as we need, and then we pour."
- 63:58 "If the material points a little higher, it passes longer on the plate, heats it more, has more contact before falling, so there is a higher chance it will all be atomized."

### Unclear / needs checking
- "Lunch powder" (04:17) = large powder; "NPPF size" (04:39) possibly "LPBF" (but Video 3 calls this powder DED-sized).
- "Graining pressure" (59:51, Video 3 41:48): draining or pouring pressure — confirm the panel label.
- 39:49 "new bars" (chamber vacuum floor at Provo altitude) and 40:31 "52, heat it up" are garbled.
- 41:18 "150" has no unit (mbar overpressure, inferred); 42:07 "50" is read as 250 from 42:50.
- 18:33 what gets damaged by pushing the stack back; 20:48 "Petburg, China" label; 67:05 "don't touch the knot".
- 12:25 "the salad" — a customer's Al alloy, unidentified; 12:53–12:58 silicon setup garbled.
- 35:00 "we cannot even work like that" likely means "we can still work like that".

## tfb4fsVNIFI — Atomizer Training Video 6 (49 s, Sep 29)

A short fragment at the powder container: after brushing all the powder in, close it; argon is heavy and stays in the bottom, so the container keeps a semi-protective atmosphere even if opened cold after a run; the best way to clean it after an atomization is to open it fully by removing four nuts. Phase: after (powder collection), cleaning. Most of the clip is silent.

### Timestamp log

| mm:ss | phase | what happens / what is said |
|---|---|---|
| 00:00 | after | After moving all the powder in, close the container. |
| 00:03 | theory | Argon is heavy and sinks, so after a run the container still holds a semi-protective atmosphere even opened cold. |
| 00:37 | cleaning | Best way to clean after an atomization: open it fully by removing the four nuts (00:42, 00:45). |

### Procedural steps
After
- Brush all powder into the container, then close it (00:00).
Cleaning
- To clean the container fully, remove the four nuts and open it completely (00:40).

### Parameters and numbers
| value | context | mm:ss |
|---|---|---|
| 4 | nuts to remove to open the container | 00:42 |

### Quotable moments
- 00:03 "It should be in at least a semi-protective atmosphere. Argon is heavy, so it goes to the bottom. After the run, even if you open it cold, you should still have [argon]."

### Unclear / needs checking
- The 00:14–00:37 gap and the trailing "if you like, as" are cut; which container (glass with valve vs stainless tube) is unknown.
