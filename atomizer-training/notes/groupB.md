# Group B — Atomizer training videos 3, 4, 5, 6 (Tue Sep 29 2026)

Source: YouTube auto-captions at `/tmp/work/autosubs/<id>.txt`; the Video 3 and Video 5 sections were later re-checked against Whisper transcripts. Captions carry no speaker labels; "trainer" = Bartosz Kalicki, inferred from content. Panel/button names are given as heard with the likely intended term, e.g. "graining pressure" → draining/pouring pressure, "ceiling rod" → sealing rod, "turbo pressure" as heard.

Chronology (inferred from content, not from the video numbers): Video 4 (loading the furnace before the first run) → Video 5 (first powder run, carbon-fiber plate, 1:1.5 booster, done by ~11:50) → Video 3 (post-run disassembly, second run with 1:1 booster + molybdenum plate, "that would be all for today") → Video 6 (powder-container fragment; position uncertain).

## txH397FGTAU — Atomizer Training Video 3 (51 min, Sep 29)

Opens with the furnace cool enough to take parts out after the morning run and the stack being rebuilt (the opening line calls it "a deep cleaning"), plus a detour on the missing 18 mm torque-wrench tip. The trainer fits the 1:1 booster and a molybdenum-alloy plate, runs the ultrasonic scan and a liquid pattern test, and explains how a straight vs angled pattern reveals plate cracks. The run documents the purge sequence (one purge cold, then purges at 250 °C and 500 °C, each vacuum + gas wash with the other vessel held at overpressure), heating to a 1000 °C set point to melt the rods, dropping to ~780–790 °C, amplitude theory (50–100 % electrical, 80–90 % best, start ~90), and the pour, during which the Mo plate cracks yet atomizes better after a piece breaks off. It ends with powder inspection, the case for wider Mo plates at low amplitude, and the end-of-day shutdown rule (everything off at ~100 °C, software locks you in until 80 °C, powder can stay overnight). Phases: after (disassembly), before (assembly, scan), during (purge, heat, atomize), after (cooldown/shutdown), theory, troubleshooting, some chatter. Re-checked against the Whisper large-v3-turbo transcript (`/tmp/work/transcripts/txH397FGTAU.txt`, 48 coarse segments, no word timing) on 2026-10-03; row times still follow the captions. The pour-pressure button is written as heard, "graining" pressure, as in Video 5.

### Timestamp log

| mm:ss | phase | what happens / what is said |
|---|---|---|
| 00:01 | after/cleaning | Narration: "this video is a deep cleaning"; post-run disassembly, long silent stretches. |
| 01:33 | before | Trainee asks whether a part's orientation matters ("orientation doesn't matter, right?"); trainer: "Not at all" (part not named in either transcript). |
| 03:28 | after | Furnace cool enough to take out the parts; parts put back in; "I forgot to put this in". |
| 05:01 | tools | "The 18 mm wrench will be a must"; buy a set at Ace Hardware (captions only; Whisper drops 05:01–06:22). |
| 06:12 | tools | Trainee: the engineering building next door has a tool room that "has all tools", so one can be borrowed meanwhile. |
| 06:37 | tools | Torque wrench should have come with an "80 mm" tip (both transcripts hear 80; 18 mm by context) but it was not shipped: kits are packed by what the control cabinet pulls in, so induction-only orders miss it; the trainer had added it to the induction list himself, then production planning rewrote the lists. |
| 07:44 | chatter | Company bureaucracy; AMAZEMET grew from ~10 to 60+ people (11:36); the trainer used to pack parts from the drawers himself. |
| 09:14 | after | "It did go all the way through, so we can reuse it" (melt poured fully; part reusable, inferred crucible; Whisper names no object either). |
| 09:19 | tools | Small tweezers "exceptionally useful": one pair for nuts, one for grabbing anything; take no space. |
| 09:40 | lesson | Disassembly went easily "because the oxygen level was much better"; oxide roughens surfaces and makes parts stick. |
| 10:11 | parts | Plate is a molybdenum alloy (Whisper "Molybdenium alloy"); best option for Al, but Mo and Al react if the process runs too long. |
| 12:04 | troubleshooting | First scan showed a double peak/interruption; a short burst of vibration seated the parts; micro-friction self-resolves. |
| 12:42 | before | Liquid pattern on plate: straight = plate vibrating well; angled = crack forming, atomization goes around it. |
| 13:06 | theory | Plan: 1:1 booster now; reversed booster can give really small Al particles but needs alloy and pour knowledge; "you will see how different it is with the metal plate". |
| 13:47 | chatter | Gage: powders for LPBF characterization, lower-rare-earth alloys. |
| 14:33 | theory | Low-density metals give bigger particles; Au/Ag much smaller, same technique; spherical, narrow distribution stays usable. |
| 15:21 | theory | Commercial Al powder 15–45 µm; this is larger but uniform and spherical; still good for printing (Northwestern paper); size specs mostly follow how gas-atomized powder behaves, and industry tends to smaller particles (15:54). |
| 16:12 | before | "Everything in, vibrations fine, so purging." 1:1 booster is slimmer than "the previous one" (the 1:1.5); amplification depends on mass/diameter difference. |
| 16:44 | during | Purge plan: one purge without heat, then two with heat; each = vacuum pump then gas wash. |
| 17:10 | troubleshooting | Gas "coming out here"; check how far it screws in — if it won't, it did not seat (closure not named; Whisper equally garbled). |
| 17:55 | during | One side at overpressure while the other purges, then reverse; two temperatures to drive moisture out of new insulation/crucible. |
| 18:34 | theory | Magnesium gives the largest particles (light); gold and copper alloys much smaller, same plate and booster. |
| 19:21 | theory | First-run powder: narrow distribution, perfect for DED; maybe too big for LPBF; DED is cheaper and simpler, good for parameter sweeps. |
| 20:00 | after | Shake the jar: bigger particles rise to the top; grains iridescent. |
| 20:18 | during | Panel: "the last cycle [done], also melting pressure, and now chamber vacuum" — after the furnace's last purge cycle press melting pressure, then vacuum the chamber (same sequence as Video 5 37:35–38:12); "turn off that" (20:33, item unnamed). |
| 21:03 | during | Chamber vacuum pulling down; silent stretch (the captions-only "heat up here" fragments at 21:03–21:29 are not in Whisper, and heating is not started until 23:28). |
| 21:58 | during | Vacuum at its max but reading still falling; in vacuum the oxygen sensor "is not going to tell you anything"; next: protective gas, then redo; running the pump longer is fine but "the effect will not be massive". |
| 22:31 | chatter | Software versions differ; trainer reported UI issues; three cabinet generations. |
| 23:28 | during | Press pressure control; get coolant flow; start heating (first heated purge, 250 °C per 33:03). |
| 30:16 | during | Set point changed to 500 °C; pump stays on gas wash; a leak in between would show as pressure loss. |
| 31:05 | parts | Plate check ("looks good"): edge peeling/cracking OK if loose bits removed; heavy oxide after an oxygen-rich run → clean fully or new plate; scrape with knife. |
| 32:41 | during | "Melt pressure. Turn off pressure control." |
| 32:58 | theory | Automate the "starting at 250 … then redoing it [at] 500" purge sequence? No: no control over the furnace controller; its software is locked ("a punch card"). |
| 34:15 | during | Repeat purge? "Don't depend on this reading with vacuum inside — fill protective gas, then check; if good, no repeat." |
| 34:48 | theory | The more runs, the better: heat and vacuum clean the system. |
| 35:02 | during | "I will just go to the max temperature" — "To 1,000?" — set point 1000 °C to melt the rods ("it's at a thousand", 37:34). |
| 37:34 | during | At 1000 °C the Al melts; "when the whistle goes" the Al jumps up in the middle — induction pull, free mixing. |
| 38:38 | during | As soon as it melts, go down ("I forgot about that part"); for a metal plate ~780–790 °C is enough (Whisper "like 7.9", captions "780, 790"); lower temperature = plate durability. |
| 38:55 | theory | Lower amplitude is kinder to the plate but can under-atomize (material flows through); start higher, reduce later. |
| 39:26 | theory | Lower amplitude = smaller particles but slower, more sensitive, more fragile; booster = mechanical control, generator % = electrical. |
| 40:00 | parameter | Amplitude "from 50 to 100 %?" = share of the generator's max current to the transducer; 100 high; 80–90 best; start ~90 and adjust. |
| 40:55 | before | Ultrasonic scan test; turn on transducer cooling first (the cooling works with or without a scan). |
| 41:14 | parts | Cooling here is fully manual — fine for induction's short runs; newest version stops it 1 min after vibration, which matters for plasma (up to ~4 h continuous atomization). |
| 41:48 | during | Announced to Sterling: a run with the metal plate. Start sequence: vibration on, "graining" pressure, sealing rod, turbo pressure — "do it all as quickly as possible". |
| 42:14 | during | "More amplitude." Pouring a bit too much → "try to remove the graining pressure" (Whisper; captions "use the grain pressure"), i.e. back the pour pressure off; "too much pressure makes it shoot out too fast". |
| 43:05 | troubleshooting | "Some of it is dropping" (un-atomized drops; captions mis-hear "broken"); would pouring higher on the plate help? "Maybe." |
| 43:48 | troubleshooting | Plate cracked on one side — interrupts atomization. |
| 44:16 | lesson | With these parameters (1:1 booster, metal plate) the atomization is generally faster and more efficient; "not too bad". |
| 44:46 | during | Pressure lowered a little; "really good for a moment"; done, stop the vibration (45:07). |
| 45:11 | lesson | After another piece broke, atomization improved: rolled/cut Mo plates hold tension points; "faulty from the factory probably"; first a small piece broke, then at the end another, and the atomization got much faster. |
| 46:05 | after | Nice powder in the container apart from what dropped into the bowl; inspect under a light; "could be better". |
| 47:00 | after | Can this be turned off? No — wait for cooling too. |
| 47:28 | parts | Wider/longer Mo plates recommended for Al (captions: what the trainer "would use the credit for"); larger area helps most at low amplitude — more surface to spread, more time to atomize; he had "expected it generally to be better". |
| 49:29 | parts | Wider Mo plate found on site; use it for the lowest-amplitude reverse-booster run (needs more time to wet). |
| 49:52 | after | Done for today; full cooldown takes a while; come back in ~30 min. |
| 50:06 | after | Shutdown "once it's like about 100 degrees": heat exchanger off, close water, compressed air, argon, then power; "doesn't matter the order". |
| 50:30 | after | Software will not let you leave the program until 80 °C; "it keeps reminding you that you need to keep it all going". |
| 50:46 | after | Powder can stay in the chamber overnight; it does not stick more; "it will have more time to pass[ivate] slowly" (both transcripts hear "pass … slowly"; slow passivation is the likely sense); trainer does this quite often. |

### Procedural steps
Before
- Fit the booster for the run (1:1 here; it is the slimmer one) (16:16).
- Run the ultrasonic scan; on a double peak, give a short burst of vibration and rescan (12:04).
- Wet the plate and check the pattern: straight = good, angled = crack (12:42).
- Inspect the plate; peel or scrape loose flakes with a knife; replace heavily oxidized plates (31:05).
- Turn on transducer air cooling before vibrating (40:55).
During
- Purge once cold, then at 250 °C and 500 °C: vacuum pump then gas wash, other vessel at overpressure (16:44, 17:55, 30:16).
- After the furnace's last purge cycle: melting pressure, then vacuum the chamber (20:18).
- Fill with protective gas before trusting the oxygen reading (21:58, 34:15).
- Press pressure control, start coolant flow, start heating (23:28).
- Switch to melt pressure and turn off pressure control before melting (32:41).
- Set 1000 °C to melt the rods; drop to ~780–790 °C once molten (35:02, 38:38).
- Set amplitude ~90 %; stay between 80 and 100 (40:00).
- Start the pour: vibration on → "graining" pressure → sealing rod up → turbo pressure if needed, quickly (41:48).
- If melt shoots out too fast, back off the "graining" (pour) pressure (42:43, 42:54, 44:46).
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
- Un-atomized drops falling off the plate: pouring higher on the plate may help (43:05; cf. Video 5 63:58).
- Mo plate cracking mid-run may release tension and improve atomization; replace the plate afterwards (45:11).

### Parameters and numbers
| value | context | mm:ss |
|---|---|---|
| 18 mm | wrench / torque-wrench tip needed (05:01 captions "18 mm wrench"; at 06:37 both transcripts hear "80 mm" — 18 mm by context and Video 5 15:25) | 05:01, 06:37 |
| 15–45 µm | commercial Al powder size for comparison | 15:21 |
| 1:1 (this run), 1:1.5 ("the previous one", per Video 5), reversed (planned next) | booster ratios | 16:18, 16:21, 13:14, 49:38 |
| 1 cold + 2 heated | purge count | 16:44 |
| 250 °C, 500 °C | heated purge temperatures (250 from the trainee's recap, same in Whisper; the trainer sets 500 himself) | 33:03, 30:16 |
| 1000 °C | set point to melt rods ("To 1,000?"; "it's at a thousand" at 37:34) | 35:02 |
| 780–790 °C | hold temperature with a metal plate (Whisper "like 7.9", captions "780, 790") | 38:48 |
| 50–100 % | amplitude range (generator current) | 40:00 |
| 80–90 %, start ~90 | recommended amplitude | 40:17, 40:34 |
| 1 min | newest-version auto cooling after vibration | 41:17 |
| 4 h | plasma continuous atomization | 41:25 |
| ~30 min | come back to shut down (captions only) | 50:06 |
| ~100 °C | shutdown threshold (Whisper "about 100 degrees"; "100, 114" was a captions-only fragment) | 50:19 |
| 80 °C | program exit threshold | 50:36 |

### Quotable moments
- 09:51 "If there is no oxygen, suddenly nothing sticks to other parts. Oxide seems to make the surface rough, and that's what makes it stuck."
- 10:35 "The same reactivity that helps us get good wetting and a good atomization start, at some point may cause the plate to be damaged."
- 12:42 "If the pattern is straight, the plate is going really well. If the pattern is angled, it usually means there is a crack formation."
- 18:05 "You do it at two temperatures to remove all the moisture. New insulation, new crucible may hold moisture; the heat gets it out and the purge removes it."
- 34:48 "The more we do it, the better it is. The heat from the process cleans it. The vacuum cleans it."
- 37:39 "When the whistle goes, the aluminum jumps up in the middle. Induction is pulling it. So it also gives us some of the mixing, which is good."
- 38:43 "For the metal plate we don't need to go so high. We will be fine at like 780, 790. It's not much, but it has a high impact on the durability of the plate."
- 40:17 "High is 100. 80 to 90 is the best. Lower means there is a chance of no atomization because the vibrations are too weak. Start around 90 and adjust."
- 45:23 "Metal plates, based on how they were rolled and cut, have tension points when heat is applied; when they break, the atomization can actually do better."
- 50:30 "Unless it's 80 degrees, it doesn't allow you to leave the program. It keeps reminding you that you need to keep it all going."

### Unclear / needs checking
- "80 mm tip" (06:37) — not settled by Whisper, which also hears "80mm" (twice, 06:57–07:08); 18 mm rests on the captions-only "The 18 mm wrench will be a must" (05:01) and Video 5 15:25 (18 mm flat wrench). Confirm against the torque-wrench kit.
- 01:33 (orientation) — not resolved: Whisper has the same "orientation doesn't matter, right?" and drops the answer; the part is unnamed. 09:14 — not resolved: Whisper has the same "It did go all the way through. So we can reuse it." with no object named (preceded by "Did you bring this? Yeah. It's cute."). 17:10 — not resolved: Whisper is equally garbled ("you can see how much you can screw it"); the closure is still unnamed. 20:18 — resolved: Whisper has "the last cycle, also melting pressure, and now chamber vacuum", i.e. after the furnace's last purge cycle press melting pressure, then vacuum the chamber (the Video 5 37:35–38:12 sequence); only "turn off that" (20:33) stays unnamed.
- 250 °C for the first heated purge — resolved by corroboration: Whisper hears the trainee's "starting at 250, purging this, purging this, then redoing it [at] 500" the same way, and the trainer's "No, not really" answers the automation question without correcting the temperatures; Video 5 42:50 confirms 250 °C. The trainer still never says 250 himself in this video.
- Shutdown threshold — resolved: Whisper has "once it's like about 100 degrees you can turn off everything, doesn't matter the order"; "100, 114" was a captions-only fragment of the trainee's guess. ~100 °C stands.
- Video numbering (3 before 4 and 5) does not match the apparent chronology.
- Added by the Whisper pass: 21:03 "heat up here" exists only in the captions (Whisper has nothing there, and heating starts at 23:28), so the old "heat up" row was a caption artifact. 42:43 Whisper "remove the grinding pressure" vs captions "use the grain pressure": the direction (back the pour pressure off) is taken from the next line, "too much pressure makes it shoot out too fast". 43:05 Whisper "some of it is dropping" vs captions "some of it is broken": "dropping" is kept because the follow-up is about pouring higher on the plate and the crack is first noticed at 43:48. 50:50 "it will have more time to pass … slowly" (both transcripts): read as "passivate slowly" rather than "cool slowly", unverified. "Graining pressure" (41:48, 42:00) is heard identically by both transcripts, as in Video 5; the panel label still has to be read at the machine.

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

The complete first powder run, start to finish. Setup: powder container types, splash-protection plates, the gold-melting catch bowl, chamber covers, then the ultrasonic stack (piezo transducer with air cooling and LEMO cable, 1:1.5/reversed/1:1 boosters, titanium connector rod M10/M8, tungsten-alloy sonotrode, carbon-fiber plate) torqued to 65/60/50 N·m with the plate tightened in the housing, scan at ~40 kHz, wet test and plate positioning. Atmosphere: chamber overpressure with O2-sensor bleed, five automatic furnace purges, chamber vacuum to the altitude-limited floor, protective-gas refill, then repeats at 250 °C and ~500 °C, with a "pressure crucible" warning diagnosed as a chamber-to-furnace leak. Melt: set 1000 °C to drop the rods, hold ~790 °C, wait exactly 2 min, then pour with sealing rod up, "graining" and turbo pressure, steering the stream by plate position; oxygen rose and bent the stream. After: stop sequence, cool to ~400 °C to open, vent before opening, respirators, brushing, slag, ~1 h cleaning for a material change. Phases: before, during, after, cleaning, theory, troubleshooting, safety, some chatter.

### Timestamp log

| mm:ss | phase | what happens / what is said |
|---|---|---|
| 00:00 | parts | Powder container types: this one shows its contents and has a built-in valve; a stainless tube is simpler, valve added separately. |
| 00:18 | parts | AMAZEMET keeps this type for induction and in the recirculation system for waste management; otherwise plain stainless — easier to make and clean; have both. |
| 00:54 | cleaning | No powder yet, so compressed air may blow out paper-towel dust; never with powder inside (01:32). |
| 01:38 | context | First rod run through this machine — AMAZEMET tests subsystems separately and avoids making powder on the production side; the recent long runs were for an automated, no-operator plasma system. |
| 02:21 | parts | Protective plates: hot metals like copper splash if atomization goes wrong; plates stop splashes entering the container. |
| 02:47 | before | For aluminum one protective plate is enough; splashes stick there, powder falls past. |
| 03:44 | before | Mounting the container is easier with two people: lift and clamp at the same time. |
| 04:08 | before | First process uses the booster already in the housing → "large powder"; easy, good for training, but big particles — "more into DED and LPBF size"; with the parameters set well "you can kind of do both" (04:39). |
| 04:48 | before | Finger-tighten the container flange. |
| 05:01 | before | A jewelry gold-melting bowl goes in the chamber for safety; catches un-atomized melt for reuse; graphite would also work. |
| 05:41 | before | Wipe the plate; hang covers over chamber openings/door so powder can be swept from the edge (05:50). |
| 06:40 | parts | Stack base: transducer = stack of piezo discs; compressed-air cooling; LEMO cable brings the generator signal. |
| 07:00 | safety | Transducer care: don't drop, heat, wet or overheat; always air-cool; "one mistake can actually damage it". |
| 07:20 | parts | If the air line were closed the system would still see pressure but give no cooling. |
| 07:38 | cost | Repair "close to 2,000" (currency unstated; the trainee guessed 5–10k new): only the piezo plates are swapped; cheap Alibaba/AliExpress transducers are cheap for a reason; theirs come from a Polish industrial maker near AMAZEMET (08:02). |
| 08:21 | parts | Booster: mechanical amplifier; its ring acts like a spring, so it can be held there without affecting vibration. |
| 08:43 | parameter | Boosters: 1:1.5 gives 150 % amplitude; reversed it reduces; 1:1 in the middle (09:22). |
| 08:56 | theory | Reversed booster on Al → smallest particles but needs good, slow pouring (not too much material at once); more energy → larger particles, faster atomization, pour more. |
| 09:24 | theory | 1:1 used for copper and magnesium; not every material atomizes at low amplitude. |
| 09:48 | lesson | Amplifying booster "will immediately destroy all the plates"; metal plates crack too quickly; reversed gave several Al runs in a row without damage and significantly better powder — still not very fine, but pretty good (09:55). |
| 10:28 | parts | Connector rod: titanium, prolongs the stack; connectors also titanium; M10 at the base, M8 at the tip (10:44). |
| 10:59 | cleaning | Clean threads with IPA; if problems start, unscrew everything and clean all threads (cavitation dust). |
| 11:19 | parts | Sonotrode (the top piece that carries the plate): "a tungsten alloy, actually" — handles the temperature, not damaged by the conditions; M8 at the top means a smaller hole in the plate → more contact surface. |
| 11:53 | parts | For Al a bare carbon-fiber plate works: Al wets and penetrates it; large particles; up to ~10 processes (12:11). |
| 12:39 | theory | Silicon was atomized on bare CF with induction — the higher-temperature setup with coatings and an "aluminum" (presumably alumina) sealing rod; Si reacts with and wets the CF, atomizing very well; unpoured Si expands on cooling and cracks the crucible (13:02). |
| 13:30 | parameter | Torques 65 N·m, 60 N·m, 50 or 55 N·m ("Newton meters" spoken for the 65; 50 is the safer bet): ultrasound must pass through; too tight damages the thread and connector, loose = friction. |
| 14:38 | before | Tighten in a vise (best) or on the floor; AMAZEMET uses machined aluminum soft jaws; 18 mm flat wrench needed (15:25). |
| 15:46 | troubleshooting | A damaged sonotrode would show in the scan. |
| 16:59 | before | Torque wrench: pull collar down, rotate so the 60 and 65 marks align → 65 N·m; it clicks when done (17:30). |
| 17:38 | before | "Now it's 60"; the final (plate) torque is done with the stack already in the housing. |
| 18:10 | before | Hold the stack, but don't push the stiff cable/hose back too much — Bartosz warned it could damage something (unnamed); elbow fittings on order via Dave (18:47). |
| 19:03 | before | Transducer goes in its cover so nobody hits it; rotate slightly to catch material; clamp only snug (20:18). |
| 21:50 | parameter | Full run with cleaning and prep: ~1 h for Al; longer for higher-melting metals. |
| 22:10 | before | Once connected, run a scan: a little over 40 kHz is right; scan also checks impedance and would not pass if something were wrong; then max amplitude, start vibrations, watch the power (22:29). |
| 22:56 | theory | Holding the vibrating tip heats it instantly (faster at higher frequency); damping shifts frequency; squeaking = loose parts → unscrew, clean, reassemble (23:18). |
| 24:18 | parameter | All energy passes through the transducer: 300–500 W may trip it; expect ≤100–150 W here, ~50 W on most plates. |
| 24:49 | before | Insert stack into housing; clamp over, not touching the safety cover; add the final clamp. |
| 25:11 | parts | View ports: hardened glass standard, borosilicate optional; furnace window is glass-ceramic; none ever broke. |
| 25:43 | before | Centre the plate; hand-tight then wrench to 50 N·m with counter-hold; arrow shows torque direction (26:02). |
| 26:39 | before | Rescan; power is higher with the plate attached. |
| 27:32 | troubleshooting | Wet test shows spread over the whole surface; a crack makes only half the plate atomize (top yes, bottom no). |
| 28:18 | parts | Plate clearly visible through the view port; a phone holder/camera could go there. |
| 28:46 | before | Plate holder moves up/down/left/right; melt should land as high as possible without going over the top. |
| 29:21 | before | Loosen to turn; up/down needs simultaneous rotation; final adjustment at the first flow (30:32). |
| 30:52 | during | Atmosphere: 5 furnace purges + 2 chamber purges at overpressure, done "one, two, three times" — cold, then at 250 °C and 500 °C for moisture. |
| 31:17 | theory | Worth it for Mg or Al (low oxygen gives good flow); for bismuth he just opened the furnace right away at 300 °C to add more, with only a little purging. |
| 31:42 | theory | Bismuth powder made without oxygen does not get the crystal colours; the grains are faceted rather than round because of how it crystallizes. |
| 31:57 | before | Argon and compressed air on; cooling not needed until heating starts. |
| 32:05 | during | Chamber overpressure: system auto-adds or vents; the hiss is the oxygen-sensor bleed; valve sets a small flow (32:44). |
| 33:00 | safety | Machine will not block a run on bad O2; you watch the value and set alarms yourself. |
| 33:22 | during | Graphite seals leak between furnace and chamber, so purge one side while the other holds overpressure. |
| 33:49 | during | Vacuum pump on, press gas wash: furnace runs 5 purge cycles automatically; it has no sensor. |
| 34:16 | theory | Hot graphite purifies itself. |
| 34:39 | troubleshooting | "Pressure crucible" warning: gas coming from chamber to furnace stops it reaching the target; maybe a crack in the sealing rod, but it was inspected and seems tight; still workable because so many purge cycles follow (35:00). |
| 36:14 | troubleshooting | Not reaching −1 = leak; chamber→furnace acceptable, from outside worse; later swap sealing rod/crucible to test (36:27). |
| 36:40 | theory | A new crucible or sealing rod usually aligns better, but the rod is solid graphite seating on solid graphite — not a true seal, so some furnace–chamber leak is inherent. |
| 37:24 | during | "Cooling water flow low" warning — chiller not on yet. |
| 37:35 | during | After the last cycle (counter shows 1) manually press melting pressure, then overpressure, then vacuum the chamber (38:12). |
| 38:28 | during | Chamber vacuum needs the pump running and the big valve open; furnace valve clicking = argon topping up what leaks into the chamber (OK); no clicking would just mean it is well sealed (39:27). |
| 38:53 | theory | Furnace→chamber leaks are acceptable while everything is being flushed with argon; purging the two separately is better than vacuuming both at once, which is also possible. |
| 39:31 | during | Wait until chamber pressure stops changing — not a set point, just the pump's limit: −1000 mbar at sea level, less at altitude; the reading here is inaudible in both transcripts (Video 1 28:10 gives the floor as about −850 mbar). |
| 40:10 | during | Fill protective gas; "this is just the cycle again: 5, 2, heat it up; 5, 2, heat it up; 5, 2" (five furnace purges, two chamber purges, then heat); at the start especially, remove all oxygen and moisture. |
| 40:55 | theory | Plasma variant: start the gas flow all the way through, heating the gas as it passes the filters, and pull it right out. |
| 41:12 | during | Second cycle: pressure control to 150 (no unit spoken); read O2 only at pressure, not in vacuum; value drops then stabilizes. |
| 41:51 | during | Start heating: coolant flow, big switch on, no error, set 250 (captions "50"; Whisper drops the phrase, 250 confirmed at 42:50); press generator start (42:22). |
| 42:31 | safety | Hearing protection: use it now; ultrasonic vibration is the worst even if it does not bother you. |
| 42:50 | during | To 250 °C almost instantly, always overshoots; vacuum again — gas wash always needs the vacuum pump (43:05). |
| 43:12 | theory | Heat evaporates moisture; coatings dry off. Smells: pump oil, hot graphite/metal from the vent, filtered (43:44). |
| 44:19 | parts | Door lock engages whenever pressure is off atmospheric. |
| 45:08 | during | Last cycle → overpressure; now the chamber: pump has its own furnace valves, chamber big valve is opened manually (45:22). |
| 46:45 | theory | Frequency is fixed by hardware (generator, transducer, sonotrode matched); a different set costs under 50,000. |
| 47:22 | theory | No 20 kHz for induction; 60 kHz offered — good for research but very sensitive, damages parts quickly, prone to errors until everything is set perfectly — explore 40 kHz first, then test 60. |
| 48:01 | during | Oxygen falling; set point up to ~500 °C to drive out moisture. |
| 49:38 | during | Rods standing up will melt "like a stick of butter". |
| 50:11 | safety | First powder run: full-face respirators for cleaning; ventilation status unknown, call facilities (50:37). |
| 51:08 | during | Melting pressure; O2 rose slightly from heat/evaporation; the filter releases moisture in the first runs. |
| 51:48 | parts | Chamber cooling is very good — condensation can appear even inside; the water is exceptionally cold; the same supply with another exchanger would serve a plasma system too (52:17). |
| 52:50 | during | Al hold up to 800, maybe 790 (the CF plate can go a bit higher); set much higher — 1000 at 53:38 — just to melt the rods, then lower to ~790 as they go down (53:14). |
| 53:28 | safety | Facilities said the ventilation should be on all the time; checked with a sheet of paper over it. |
| 54:24 | safety | At 1300 °C it is too bright to watch — use a filter or glasses; around 1500–1600 °C it is basically white (54:51). |
| 55:06 | theory | Whistling is the induction; it pulses to hold temperature. |
| 55:23 | during | Temperature falls as the rods melt; lowering the set point just stops applying energy (56:20); a packed charge melts easier; something placed over the crucible shields it so the radiation stays inside (55:45). |
| 57:22 | during | Stabilized; once all liquid wait 2 min — measured lag for the crucible-wall thermocouple to match the melt (reference taken with a thermocouple in the sealing rod). |
| 58:23 | theory | The melt is visibly mixing — the induction pulsing moves it up and down and stirs it. |
| 58:43 | during | Do not wait longer than 2 min — more oxidation, more reactivity; then pour. |
| 58:53 | during | Best results need an operator at the window adjusting amplitude, turbo pressure and plate position. |
| 59:51 | during | Start: vibrations on; sealing rod up; "graining" pressure (HMI label as heard, Whisper "grading" — see Unclear) pushes the melt; turbo pressure when necessary. |
| 60:27 | during | Stream lands too far — move the plate; "too much"; then better, more area covered, pour a bit higher (60:53). |
| 61:07 | during | Once the plate is hot every drop atomizes; initial losses heat the plate; metal plates heat faster (61:34). |
| 62:12 | during | End: turbo pressure to clear the nozzle; sealing rod down; melting pressure; generator stop; ultrasonics stop. |
| 62:24 | lesson | O2 rose a lot; oxide at the nozzle bends the stream, so it wandered forward and back — compensate with plate position; a few initial droplets lost is fine, with a hot plate and a stable stream everything atomizes (62:54). |
| 63:24 | after | Heating stopped; temperature dropping. |
| 63:28 | idea | Laser pointer on the sealing-rod arm or holder to mark plate position — "not very hard". |
| 63:58 | theory | Aim higher on the plate: longer contact, more heating, all atomized instead of droplets. |
| 64:22 | after | Powder in the container plus some in the bowl to brush; repeat, then compare 1:1 booster + metal plate (65:08). |
| 65:22 | lesson | No parameter log exists — record parameters by hand. |
| 65:37 | after | Around 400 °C the furnace/chamber can be opened to speed cooling. |
| 65:41 | troubleshooting | Drips on coolant lines are condensation, more at top temperatures. |
| 66:20 | parts | Chamber water jacket: stainless channels set in the mould, then cast in aluminum — not copper coils. |
| 66:49 | after | Over ~400 open the chamber; everything inside is cold; "just don't touch the nut" — the graphite nut under the furnace that holds the crucible and nozzle holder (see Unclear); clock 11:38 (67:16). |
| 67:20 | cleaning | Brushes push powder down; different sizes for different materials. |
| 67:38 | cleaning | Material change in induction mode: vacuum, wipe all surfaces and the powder container; ~1 h; scrape anything melted on (68:02); much worse with plasma. |
| 68:26 | after | Around 100 °C you can shut down. |
| 68:51 | parts | CF plate is reusable if intact — the IPA wet test checks it for defects (69:12); the bowl can be removed and cleaned (69:37). |
| 70:10 | theory | Process is short; prepare the next charge while cooling. |
| 71:01 | theory | A plate glowing orange in a video is plausible — with copper or brass the carbon-fiber plate glows and can take it; a visible arc means plasma, not induction. |
| 71:41 | theory | Lower amplitude lets plates survive higher temperature; copper alloys, silver and gold all work on CF or metal plates, but metal plates want the amplitude-reducing booster (72:04). |
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
- Assemble transducer → booster → titanium connector rod (M10/M8) → tungsten-alloy sonotrode; IPA on threads (10:28, 10:59).
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
- Pour: vibrations on, sealing rod up, "graining" pressure, turbo pressure as needed; steer with the plate (59:51).
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
| ~2,000 | transducer repair cost, "close to 2,000" (new guessed 5–10k, currency unstated) | 07:38 |
| 1:1.5 (150 %), reversed, 1:1 | booster options | 08:43 |
| M10, M8 | connector rod threads | 10:44 |
| ~10 processes | carbon-fiber plate life with Al | 12:11 |
| 65 / 60 / 50–55 N·m | stack torques; "Newton meters" is spoken once, for the 65 | 13:30 |
| 18 mm | flat wrench size | 15:25 |
| ~1 h | full run incl. prep for Al | 21:50 |
| ~40 kHz | scan frequency, "a little over" | 22:24 |
| 300–500 W | may trip the transducer (captions "watts"; Whisper's "volts" is a mis-hearing) | 24:26 |
| 100–150 W, ~50 W | expected power here / most plates | 24:32 |
| 50 N·m | plate torque in housing | 26:02 |
| 5 + 2 | furnace / chamber purges per cycle | 30:52 |
| 250 °C, 500 °C | heated purge temperatures | 31:01 |
| 300 °C | bismuth: furnace opened right away | 31:37 |
| −1 (bar) | furnace vacuum target | 36:14 |
| −1000 mbar | chamber vacuum floor at sea level; the floor reached here is inaudible (about −850 mbar per Video 1 28:10) | 39:39 |
| "5, 2, heat it up" | purge-cycle shorthand: 5 furnace purges, 2 chamber purges, then heat, repeated | 40:31 |
| 150 | pressure-control target for the O2 reading; no unit spoken (mbar overpressure inferred) | 41:18 |
| 250 (captions "50") | first heating set point; Whisper drops the phrase, 250 confirmed at 42:50 | 42:07 |
| <50,000 | cost of a different frequency set | 47:02 |
| 20 / 40 / 60 kHz | frequency options | 47:22 |
| ~500 °C | second heated purge | 48:06 |
| 790–800 °C | Al hold temperature ("up to 800, maybe 790") | 52:53 |
| 1000 °C | melt set point ("set to a thousand") | 53:38 |
| 1300 °C | too bright to watch unfiltered | 54:26 |
| 1500–1600 °C | glow turns basically white | 54:51 |
| 2 min | hold after full melt (crucible-wall thermocouple lag, measured against a thermocouple in the sealing rod) | 57:29 |
| ~400 °C | open chamber | 65:37 |
| 11:38 | clock time at opening | 67:16 |
| ~1 h | cleaning for a material change | 67:46 |
| ~100 °C | shutdown threshold | 68:26 |

### Quotable moments
- 07:00 "Don't drop it, don't heat it, don't expose it to moisture, don't overheat it. Always have the compressor cooling, because it's pretty expensive."
- 09:48 "The stronger one will immediately destroy all the plates. For metal plates I don't recommend to use this one, because they crack."
- 13:51 "If you go with higher, you can damage the thread, damage the connector. But if you have it loose, then you just have the friction between the parts and the ultrasonic vibration doesn't go through."
- 33:22 "The graphite seals are not perfect. We have leaks between the furnace and the chamber. That's why I'm purging one side, keeping overpressure on the other."
- 36:18 "If it's a leak from the chamber to the furnace, that's acceptable. If it's a leak from the outside, it's worse."
- 36:44 "We have the point where the sealing rod is just like solid graphite going into solid graphite, and it's not really sealed."
- 57:32 "We have measured that 2 minutes is how much it takes for the temperature of the crucible at the wall to be the same as the temperature of the metal, when measured with a thermocouple in the sealing rod."
- 58:43 "We don't want to wait longer than 2 minutes, because it can cause more oxidization, more reactivity. As much as we need, and then we pour."
- 63:58 "If you have the material pointing a little bit higher, it will then pass longer on the plate, heat it more and will have more contact with the plate before falling down. So there is a higher chance that it will be all atomized."

### Unclear / needs checking
- "Lunch powder" (04:17) — resolved: Whisper has "how to make large powder". "NPPF size" (04:39) — resolved: "More into like DED and LPBF size … if you set the parameters well, you can kind of do both" (consistent with Video 3 calling this powder DED-sized).
- "Graining pressure" (59:51, Video 3 41:48): not settled from the audio — Whisper hears "grading pressure" here, and across Videos 1, 3, 5 and 9 both transcripts hear "graining/grading/grainy", never "draining", so the log's "draining" was a guess and "graining" is kept as the heard label; the panel label itself still has to be read at the machine.
- 39:49 "new bars" — the number is inaudible in Whisper as well ("right now it's at negative …" and the segment ends); Whisper adds that it is not a set point but the maximum the pump reaches, shifted by altitude (40:01); Video 1 28:10 gives the floor as about −850 mbar. 40:31 "52, heat it up" — resolved: Whisper has "5-2, heat it up, 5-2, heat it up, 5-2", i.e. five furnace purges, two chamber purges, then heat, repeated — the 30:52 schedule.
- 41:18 "150" — still no unit in Whisper ("It will go to 150"); mbar overpressure remains inferred. 42:07 "50" — resolved as 250 by context: Whisper drops that sentence entirely, but "to 250 it goes almost instantly" (42:50) and the 250/500 plan (31:01) are both confirmed.
- 18:33 — not resolved: Whisper has "Bartosz was saying that if we push this back too much, we might damage the…" and the speaker trails off. 20:48 "Petburg, China" — Whisper has no text between 19:07 and 21:19, so not resolved. 67:05 — resolved: "just don't touch the nut" (Whisper "nut", captions "knot"): the graphite nut under the furnace that holds the crucible and nozzle holder (Video 1 Whisper), the one part still hot when the chamber is opened — not the nozzle as the log guessed.
- 12:25 "the salad" — not resolved: Whisper hears the same words; it answers a question about Al–Mg alloy blends, so an Al–Mg alloy is likely but unnamed. 12:53–12:58 — resolved: "With induction … but it was the higher temperature setup with coatings, aluminum sealing rod" — the Si run used the coated high-temperature set and an "aluminum" (presumably alumina, given the Si melting point) sealing rod.
- 35:00 — resolved by context: both transcripts hear "we can not even work like that", but the next sentence ("it's just that we go through so many of the purging cycles that at the end it's going to be okay") makes the sense "we can even work like that".
- 11:19 sonotrode material — corrected from titanium to tungsten alloy: Whisper has "This is a tungsten alloy, actually. It just handles the temperature well" (captions "ten alloy"), matching Video 8 06:44 ("it's tungsten, I believe, like a tungsten alloy") and Video 7 18:35 ("tungsten nickel iron"); the connector rod and its connectors are titanium (10:28).
- 08:56 "good wetting" was a mis-hearing: Whisper has "you need to have good pouring, because then the pouring has to be slow enough that there is not too much material".
- 52:33 "I think one is enough" — ambiguous: it may be the trainee reading the O2 value ("one at this temperature … oxygen is going to be very low anyway") rather than a heat-exchanger count, so row 51:48 no longer claims "one exchanger enough".
- 24:26 Whisper says "volts" where the captions say "watts"; the scan screen shows power and the captions have "50 W" at 24:42, so watts is kept.

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
