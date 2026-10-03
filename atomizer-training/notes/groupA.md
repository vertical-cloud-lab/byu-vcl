# Group A — atomizer training transcripts (Sep 29 2026)

Source: YouTube auto-captions in `/tmp/work/autosubs/` (the Whisper file for wRc8p2_FnJo exists but is empty, so all three use auto-captions). Trainer: Bartosz Kalicki (AMAZEMET). Trainees: Gage Erickson, Ronnie Guymon, Sterling Baird. Caption mis-hearings normalised: "ceiling/silly rod" = sealing rod, "transucer" = transducer, "automize" = atomize, "Aragon" = argon, "hepailter" = HEPA filter. The HMI button heard as "graining / grading / raining pressure" is written "graining pressure" throughout (see Unclear).

## wRc8p2_FnJo — Video 1 of atomizer training (47 min, Sep 29)

Bartosz powers up the rePowder and gives a full tour of what is inside the integrated control/induction module: compressed-air filters and regulator (transducer cooling), the two argon lines and regulators (sealing rod vs. furnace fill/purge), cooling-water routing, exhaust filters, pneumatics, vacuum valve, oxygen sensor bleed, vent and 8-bar mechanical safety valve, HEPA filter, ultrasonic generator, PLC/fuses and main switch. He then covers back-of-unit utilities and routine maintenance (vacuum pump oil and oil-mist filter, heat exchanger water level, HEPA filter every ~2 months). The second half is an HMI walkthrough: accounts, ultrasonic scan theory (40 kHz, 39–41 kHz scan, +200/−600 Hz offsets), the induction atomization screen (temperature, pressure, oxygen limits, gas wash, pressure control, automatic chamber prep, altitude limitation), furnace controls (green-light confirmation, gas wash x5, melting/graining/turbo pressure, sealing rod), program setup and service mode. From 35:00 he disassembles the furnace (thermocouple, sealing rod, insulation, crucible, nozzle holder, graphite seals, brass filter), explains nozzle sizes and crucible coating, cleans, and reassembles. Phases: before (power-up, hardware orientation, HMI theory, furnace prep/cleaning/reassembly) and maintenance; no run happens in this video.

### Timestamp log

| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:16 | before | Power-up: main breaker was off since yesterday; leave transformer breaker on all the time, shut the other one when people work around the machine |
| 00:54 | theory | Tour inside the module; standard product is cabinet + induction module, here combined into one unit |
| 01:27 | theory | Left side: compressed-air inlet with moisture filters and pressure reducer; ~4 bar in flow, 8 bar supply; air only cools the transducer |
| 01:58 | safety | If air pressure is too low, ultrasonic vibration is disabled with an error |
| 02:12 | parts | Two argon lines: one fills the chamber, one feeds the furnace. Top regulator "sealing rod" drives the rod up/down; lower one supplies fill, purge, pneumatics |
| 03:02 | parts | Cooling water passes an extra pressure reducer, then a flow + temperature sensor; path furnace, cone, chamber, return |
| 03:35 | parts | Furnace exhaust passes a brass pre-filter in the furnace and a finer filter on the back; replace if dirty or pressure will not release |
| 04:06 | maintenance | This side is maintenance-free; look for gas leaks/deteriorated hoses every few weeks or months; keep closed during operation |
| 04:49 | parts | Right side: induction generator control at bottom, do not touch unless it fails |
| 05:14 | parts | Pneumatic block controls all furnace valves (vacuum, purge, fill, gas removal); separate block controls chamber pressure |
| 05:41 | theory | Vacuum valve: running pump always pulls on the furnace; chamber vacuum requires opening the additional valve (manual) |
| 06:06 | theory | Oxygen sensor needs a small continuous bleed flow via a settable valve; valve open only above 50 mbar, closed under vacuum |
| 06:39 | safety | Vent valve removes overpressure; pressure sensor; mechanical safety valve opens automatically above 8 bar even if vent valve fails |
| 07:02 | parts | HEPA filter keeps powder out of sensors and vacuum pump |
| 07:16 | troubleshooting | Argon feed moved to enter chamber directly, in an arc; feeding next to the O2 sensor gives falsely low readings |
| 08:05 | maintenance | HEPA: remove and check about every 2 months; powder collects at bottom; disconnect three points, unbolt cover, filter pops out; spares on hand |
| 08:51 | safety | Put used filter in a metal tray/basket with sand nearby; fine dust (esp. magnesium or overheated evaporate) can spontaneously combust; filter is thin polyester mesh |
| 09:53 | parts | Ultrasonic generator: parameters changeable via app; remote session with AMAZEMET possible for issue sorting |
| 10:27 | troubleshooting | PLC, transformers, fuses for furnace, vacuum pump, generator: first place to check if an electrical part fails |
| 11:20 | parts | Main switch powers whole device; internal connections rewired so everything hooks in here |
| 11:44 | maintenance | Software update: USB port on back of HMI; SD card in PLC; keep old copy |
| 12:58 | maintenance | Back connections: heat exchanger, vacuum pump, compressor, argon, water. Vacuum pump needs the most maintenance |
| 13:14 | maintenance | Vacuum pump oil: sight glass, keep between min and max; standard vacuum pump oil |
| 13:37 | maintenance | Oil-mist filter (foam) collects oil in blue canister; every few weeks remove black screw and pour out; can route to exhaust or a bucket |
| 14:46 | parts | Vacuum pump need not be bolted down; rubber feet damp vibration |
| 14:56 | maintenance | Heat exchanger: check water level; darkish water is fine, it is filtered; low-level sensor shuts everything down |
| 15:40 | troubleshooting | If water valves are closed the internal loop slowly overheats; it is a separate loop cooled through a mechanical heat exchanger; temp shown on HMI |
| 17:17 | troubleshooting | HMI error "cooling water flow low" because heat exchanger is off; do not start it until ready to heat (noise) |
| 17:49 | safety | Compressed air only cools transducer; no air means no vibrations; any displayed error stops heating instantly |
| 18:11 | theory | HMI accounts: admin and others (111, 222, 333...); can restrict who can change settings or press buttons |
| 19:22 | theory | Settings: high and critical oxygen warnings; clock in Polish time; total on-time and ultrasonic-on time |
| 19:58 | before | Advanced ultrasonics page: check transducer + booster stack; scan gives "no air pressure" error until air is on |
| 20:58 | theory | Transducer cooling only needed for the few minutes of atomization |
| 21:07 | theory | Scan sends a weak signal to find best frequency; one single wide peak is good; more parts make the usable range narrower |
| 21:53 | theory | Set amplitude, start vibration; shows frequency and power; amplitude = intensity; cooling runs 1 min after stop |
| 22:32 | parameter | Scan range: 40 kHz system, scan 1 kHz around, 39 to 41 kHz |
| 22:53 | parameter | After scan F-start/F-stop auto-set: peak +200 Hz and −600 Hz; frequency drops as parts heat, generator tracks it |
| 23:48 | theory | Frequency set by Young's modulus, density, part length; shuts down if out of range or power rises |
| 24:29 | theory | Induction atomization program: wait 10 s for communication; reads furnace temperature and pressure (5 mbar shown) |
| 25:03 | parameter | Oxygen display max 1000 ppm; do not work above 100 ppm; best 40–50 ppm; rises when atomizing starts (material, chamber moisture) |
| 25:53 | theory | Middle: basic ultrasonic start/stop/scan; right: chamber control with protective gas, vent valve, transducer cooling, vacuum pump |
| 26:30 | theory | Pump running but vacuum goes to furnace; open the valve to give it to the chamber |
| 26:48 | theory | Gas wash: fill chamber to ~500 mbar, pump out without reaching vacuum; avoids room leak at the vacuum limit |
| 27:20 | theory | Pressure control holds chamber pressure automatically during pour; used to need manual venting when pressure jumped |
| 27:51 | theory | Automatic chamber prep: set target pressure, wait 30 s, fill with argon, repeat or gas wash by oxygen level |
| 28:10 | parameter | At altitude cannot reach −1000 mbar; max about −850 reached yesterday; use ~848 as target (sensor calibration) |
| 28:45 | parameter | Chamber was at 50 mbar so O2 bleed valve kept toggling at its threshold |
| 29:11 | theory | Furnace panel: press button to get green light before any pressure can be applied; legacy confirmation from rotating-chamber model |
| 30:22 | safety | With pressure or vacuum in chamber it locks, cannot open |
| 30:37 | procedure | Furnace gas wash needs vacuum pump running: vacuum furnace, fill argon, repeat; set for 5 repeats |
| 30:57 | theory | After gas wash go straight to melting pressure; graining pressure is higher and pushes material out |
| 31:21 | parameter | Example chamber 150: melting pressure slightly below chamber; graining pressure above chamber |
| 31:36 | parts | Sealing rod button closes/opens furnace; visible moving |
| 31:54 | parameter | Turbo pressure: manual push for poor flow; furnace goes to 1.5 bar while held, drops on release |
| 32:15 | theory | Generator start/stop = heating on/off; vacuum pump button only powers pump, control is from HMI |
| 32:40 | theory | Top physical buttons mirror the screen; temperature set manually, hold to go faster |
| 33:03 | parameter | Program setup: max heating power normally 100; can limit or create heat ramp for ceramics/modified crucibles |
| 33:36 | parameter | Graining pressure has begin and end: raise pressure as crucible empties to keep flow; turbo max 1.5 bar |
| 34:11 | parameter | Hold program setup for service mode; thermocouple type N, up to 1300 C |
| 34:36 | parameter | Service pages show water flow and temperature; must be over 2 L/min to operate |
| 34:59 | before | Preparation = furnace prep + chamber prep; chamber must be opened to prep the furnace |
| 35:49 | before | Remove everything, starting with thermocouple; thin ceramic cover cracks normally, replacements exist; align with the outlet |
| 36:24 | before | Move sealing rod up, pull safety pin, take rod out |
| 36:39 | parts | Top insulation (silica + alumina mix), then side insulation |
| 37:01 | before | Crucible held by a nut; nozzle holder with graphite nozzle may stick; remove bottom insulation, unscrew while holding nut so nothing falls |
| 37:45 | parts | Stack: graphite nut, graphite seal, graphite nozzle holder, second graphite seal |
| 38:06 | troubleshooting | No thermocouple gives "master temperature sensor" error and emergency argon bleed; put it back during maintenance |
| 38:53 | maintenance | Brass preliminary filter catches evaporate and splashes; clean in ultrasonic bath if clogged |
| 39:18 | before | Graphite nozzle is the consumable; look through to check it is clear; keep precise drills or needles to unclog |
| 39:54 | parameter | Nozzle 0.5 mm standard; drill to 0.7, up to 1 mm max for standard operation |
| 40:20 | theory | Al 4047 flows well; copper, tin, brass, bismuth, antimony, silver, gold also done; silver/gold ideal (no oxidation) |
| 41:05 | troubleshooting | Al alloys, magnesium, odd compositions may need larger hole; inconsistent flow or clogging means go bigger |
| 41:30 | parameter | Al-Si-Mg works at 0.5 but more reliable at 0.7; contaminated/oxidized feed flows worse |
| 41:59 | before | Standard graphite crucible; coat with boron nitride spray before use |
| 42:23 | before | Best coating: boron nitride in alcohol with inorganic binders; very thin layer; coat night before, dry; lasts a few processes; spray ~$50 |
| 43:23 | parts | Nozzles in graphite or pure boron nitride; sealing rods graphite or alumina (reactive materials); thick rod coating can block nozzle |
| 44:11 | cleaning | Wipe all parts; most important is the seal; vacuum dust and splashes; else small leak; wipe evaporate off glass |
| 45:36 | cleaning | Graphite always leaves black on wipes, normal |
| 45:54 | before | Nozzle into holder: orientation matters, white side on top |
| 46:08 | before | Thread crucible onto holder; tighten until it feels tight, do not go over |
| 46:33 | before | Rebuild: graphite seal, bottom insulation, crucible, thread into chamber, secure with nut |
| 47:02 | before | Tighten nut a little; before fully tightening make sure the hole ends up where it can be reached |

### Procedural steps

Before
- Leave the transformer breaker on; switch the main breaker off only when people will work around the machine (00:30)
- Confirm compressed air is on (~4 bar regulated from 8 bar supply); ultrasonics refuse to start without it (01:42)
- Keep module doors closed during operation; glance at hoses for leaks every few weeks (04:13)
- Open heat exchanger water valves, start it only when ready to heat; "cooling water flow low" clears once running (16:02, 17:17)
- Log into HMI with an account; restrict trainee accounts if needed (18:11)
- Run ultrasonic scan on transducer + booster in Advanced ultrasonics; expect one peak, 39–41 kHz range (20:38, 22:32)
- Enter induction atomization program and wait 10 s for furnace communication (24:36)
- Press the furnace confirmation button until the green light shows before applying any pressure (29:24)
- Run furnace gas wash with vacuum pump running (5 repeats), then go to melting pressure (30:37, 30:57)
- Set melting pressure slightly below chamber pressure and graining pressure above it (31:21)
- Set max heating power or a heat ramp in program setup when using ceramics (33:09)
- Disassemble furnace: thermocouple, sealing rod (up, safety pin), top insulation, side insulation, nut, crucible + nozzle holder, bottom insulation (35:49)
- Put thermocouple back during maintenance to clear the error and stop emergency argon bleed (38:27)
- Check nozzle bore is clear; unclog with a needle or drill out to 0.7 mm for poorly flowing alloys (39:32, 40:09)
- Coat crucible with boron nitride the night before and let it dry (42:57)
- Insert nozzle in holder white side up; thread crucible on until just tight (46:04, 46:23)
- Rebuild seal, bottom insulation, crucible, nut; align the hole before fully tightening the nut (46:33, 47:06)

Cleaning / maintenance
- Wipe seal, graphite parts and view glass; vacuum dust and splashes before closing (44:11)
- Remove and inspect HEPA filter about every 2 months; store it in a metal basket with sand nearby (08:08, 08:51)
- Check vacuum pump oil between min and max in the sight glass (13:14)
- Drain the oil-mist filter canister every few weeks via the black screw (14:00)
- Check heat exchanger water level (14:56)
- Clean brass pre-filter in an ultrasonic bath when clogged (39:11)
- Replace the finer back exhaust filter if dirty or furnace pressure will not release (03:56)

Troubleshooting
- Any displayed error stops heating instantly; clear the error first (18:02)
- "No air pressure" on scan: turn on compressed air (20:43)
- Electrical failure: check fuses in the PLC compartment first (10:48)
- Water flow must exceed 2 L/min; check in service pages (34:51)
- Chamber locked: there is pressure or vacuum inside, vent first (30:22)
- Generator stops if frequency leaves the range or power climbs; rescan (24:20)
- Low O2 reading with argon fed next to the sensor: feed the chamber directly (07:51)

### Parameters and numbers

| value | context | mm:ss |
| --- | --- | --- |
| ~4 bar | compressed air in flow, transducer cooling | 01:42 |
| 8 bar | compressed air supply pressure | 01:48 |
| 50 mbar | O2 sensor bleed valve opens only above this | 06:29 |
| 8 bar | mechanical safety valve opens | 06:47 |
| ~2 months | HEPA filter inspection interval | 08:08 |
| every few weeks | drain oil-mist filter | 14:00 |
| 1 min | transducer cooling continues after vibration stop | 22:23 |
| 40 kHz; 39–41 kHz | system frequency; scan range (1 kHz around) | 22:38 |
| +200 Hz / −600 Hz | F-start/F-stop offsets from peak | 23:07 |
| 10 s | wait for furnace communication | 24:36 |
| 5 mbar | pressure reading shown on screen | 24:58 |
| 1000 ppm | O2 display max | 25:03 |
| 100 ppm | do not operate above | 25:10 |
| 40–50 ppm | best O2 value | 25:15 |
| ~500 mbar | gas wash fill pressure | 26:59 |
| 30 s | automatic chamber prep dwell | 28:01 |
| −1000 / −850 / 848 | vacuum target unreachable at altitude; max reached; target used | 28:17 |
| 5 | furnace gas wash repeats | 30:53 |
| 150 | example chamber pressure | 31:27 |
| 1.5 bar | turbo pressure (max) | 32:02 |
| 100 | max heating power default | 33:09 |
| type N, 1300 C | thermocouple type and ceiling | 34:27 |
| >2 L/min | required cooling water flow | 34:51 |
| 0.5 / 0.7 / 1 mm | nozzle bore standard / common upsizing / max | 39:59 |
| ~$50 | boron nitride spray bottle | 43:10 |
| few processes | life of crucible coating | 43:02 |

### Quotable moments

- 01:58 "If the pressure will not be enough, you will not be able to use the ultrasonic vibrations. You will get an error and the system will shut down this option for you."
- 06:20 "The sensor, in order to be precise, requires a flow through. So a bit of the gas from the chamber should always escape through that valve."
- 07:51 "If we would have those two next to each other, we would just be putting argon into the sensor, which would show much lower value than it should."
- 18:02 "Any error that is displayed here is always stopping the heating instantly."
- 21:46 "The more things you add, the harder for the system to vibrate. And that's why this perfect range of frequencies is going to be smaller."
- 23:37 "When the system vibrates and heats up, the frequency will be going down. That's why we allow it to go down a little bit more."
- 31:21 "Melting pressure should be slightly lower than the chamber pressure. Graining pressure should be higher than the chamber pressure in order to push material out."
- 44:50 "We just need to make sure that this is clean. Otherwise, we may have a small leakage."

### Unclear / needs checking

- "Graining pressure" (30:57, 31:09, 33:33) is heard three ways; likely the HMI label for pour/drain pressure. Confirm the on-screen name.
- 28:19 "maximum is minus 150" then "850 / 8 48": inferred as −850 mbar reached and ~848 entered as target. Verify on the HMI.
- 03:25 colour coding: blue = compressed air; which of "silver" and "clear" is argon vs. water is garbled.
- 18:24 account passwords heard as "one one one ... 222 33 three four five": pattern inferred, not confirmed.
- 22:47 "the head is pipe head estimated a bit" is unintelligible (a scan parameter).
- 46:06 why the nozzle's white side goes on top ("based on how it was treated") is unexplained.
- 08:02 "this can work only if there is no extra sensor in the system" — context lost.

## Pk0K5sBz-sQ — Atomizer training (9.5 min, Sep 29)

A short, mostly silent clip shot immediately after a pour (inferred: the first Al 4047 run), with sparse dialogue. Bartosz has the trainees brush powder from a piece and the plate, says big lumps should be removed but the stream will otherwise take them, and has the tube wiped at the bottom before closing. He explains that slag removal and the nozzle check must wait because the furnace is still ~150 C, and discusses when to stop the cooling water (nominally 100 C, earlier if the crucible is empty; keep it on if a large unpoured charge remains). Phases: after (cooldown, powder handling, cleaning) plus unrelated chatter about class and light switches.

### Timestamp log

| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:49 | chatter | Camera kept recording; lab coat offered and declined |
| 03:56 | cleaning | "With the piece and the powder, we can just brush inside" |
| 04:23 | cleaning | Plate is okay; a big piece should be removed if possible, otherwise the stream takes it by itself |
| 04:50 | cleaning | Powder can be used again without issue; wipe the tube before closing, especially at the bottom; then close it |
| 05:57 | chatter | Keep the solidified piece to show people |
| 06:21 | after | Need to remove slag and check nozzle opening; too hot to touch; a clogged nozzle means taking all pieces out; still 150 C, must wait |
| 06:43 | unclear | Question about ventilation and a better way; answer "no, we still need to wait" |
| 07:36 | chatter | Trainees have to run to class; two light switches three feet apart |
| 08:37 | after | 130 C but crucible is empty; the water is really cold |
| 08:53 | after | Theoretically keep cooling until 100 C; empty and this close it will not boil the water |
| 09:04 | troubleshooting | A big chunk left (e.g. no pour) keeps all the heat in, takes long to cool, keep cooling the whole time |
| 09:18 | after | Leave it to cool; then remove slag, check nozzle, put new material in |

### Procedural steps

After
- Brush loose powder from the piece and plate back inside (03:56)
- Remove any big solidified piece if you can; otherwise the next stream will take it (04:34)
- Wipe the tube, especially the bottom, before closing (04:53)
- Wait until the furnace is cool enough to touch before removing slag and checking the nozzle (06:21)
- Keep cooling water on until ~100 C nominally; with an empty crucible it can stop earlier (08:53)
- If a big unpoured chunk remains, keep the cooling running the whole time (09:04)
- Once cool: remove slag, check nozzle is clear, load new material (09:22)

### Parameters and numbers

| value | context | mm:ss |
| --- | --- | --- |
| 150 C | furnace still too hot to disassemble | 06:37 |
| 130 C | reading when cooling discussed; crucible empty | 08:37 |
| 100 C | nominal temperature to keep cooling until | 08:54 |

### Quotable moments

- 04:53 "Before closing, we need to wipe the tube, especially at the bottom."
- 06:21 "We would need to remove the slag and check if the nozzle is clear... but this is still too hot to touch it."
- 09:04 "If you will have a big chunk of material left in, because for example there is no pouring, it will keep all the heat in. So it will take a long time to cool down."

### Unclear / needs checking

- Minutes 00:00–03:56 and 01:57–02:18 have almost no captions; what is being handled (the "piece", the "plate") is inferred from context.
- 06:43 ventilation question has no usable answer.
- 08:37 "130 degrees" is assumed to be the furnace thermocouple reading (inferred).

## naePD8o9_Gk — Atomizer Training Video 2 (56 min, Sep 29)

The first full run on Al 4047 rods from heating through powder removal. It opens with the HMI (generator start/stop) and the altitude limitation on the vacuum gauge, then a mistake: the setpoint was left at 800 C so the charge began melting before the 250 C purge, so Bartosz purges immediately (furnace once, chamber twice) and recaps the normal 250/500/final purge sequence. He reduces to 800 C once the rods slump, rescans the ultrasonic stack (needs just over 40 kHz), waits 2 min for the melt, then pours: sealing rod up, graining pressure, turbo pressure to push and to heat the sonotrode plate, with coaching on when a thin stream gathers rather than atomizes, wetting theory, and the quick shutdown (melting pressure, sealing rod, generator stop, ultrasonic stop). After cooling to ~400 C the chamber is vented, opened with masks and lab coats, powder is brushed down into the container, the plate removed, cooling shut off and the container valve closed. Phases: during (heating, purging, scanning, atomizing), after (shutdown, cooldown, venting, powder collection), cleaning, troubleshooting, with long stretches of chatter (stocks, mining, nuclear).

### Timestamp log

| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:26 | during | Warning gone; generator start = start heating, generator stop = stop heating |
| 01:07 | theory | Purge did not reach −1 bar: at altitude the gauge compares to ambient and can only show about −0.8 bar; real vacuum is the same |
| 01:44 | unclear | Can the sensor be recalibrated for altitude? Bartosz: no idea, probably hard; ~15% difference, same in Denver |
| 02:40 | parts | Crucible size question; a plug as big as one rod down the middle leaves ~20 mm from rod edge to crucible wall (custom cup, inferred) |
| 03:23 | mistake | Material already melting: setpoint went straight to 800 C; the setpoint stays at the last value entered |
| 03:32 | procedure | Skip the 250 C step; purge now: once the furnace, twice the chamber; vacuum pump + gas wash, safe as long as material has not melted |
| 04:56 | procedure | Chamber: gas wash, go to overpressure, purge chamber, overpressure, then atomize; go directly to melting pressure after the final gas wash |
| 05:48 | parameter | Normal sequence: 250 C and purge, 500 C and purge, then final temperature |
| 06:14 | procedure | Disable pressure control first, then start vacuum pump |
| 08:17 | procedure | Recap: set 250 C, purge chamber then furnace; 500 C, same; then final temperature and melt |
| 09:02 | parameter | Confirmed: brought to about 1000 C to melt aluminum; copper will need much higher |
| 10:35 | procedure | Chamber purge: go to the minimum value, protective gas, repeat; if it stops going further, move on |
| 11:07 | procedure | Pressure control back on; oxygen level pretty good |
| 12:40 | during | Oxygen low; raise the temperature |
| 14:15 | theory | Graphite can go to 2000 C with no oxygen; with oxygen degradation is very fast |
| 14:41 | during | Material slumping; reduce temperature to 800; one more ultrasonic scan; after 800 wait 2 min, then pour |
| 17:45 | during | Fully melted; sit 2 min to mix |
| 18:08 | theory | A scan is valid only for a limited time; rescan otherwise; frequency should read a bit over 40 kHz, may drop slightly |
| 18:53 | troubleshooting | If not above 40 kHz: impossible with these parts; worst case unscrew and re-screw the stack, a loose joint shifts frequency |
| 19:12 | during | Ultrasonic start; it vibrates; then sealing rod up and graining pressure; turbo pressure if the push is not enough, especially at start |
| 19:44 | theory | Turbo at the start heats the plate; also stabilizes a wandering stream and unclogs small debris |
| 20:29 | troubleshooting | Stream too thin: it gathers, does not atomize, plate cannot heat up; more volume needed |
| 20:42 | troubleshooting | Earlier Bartosz poured more to heat the plate and wash off solidified leftovers |
| 21:10 | during | Stream stable; give a small turbo push now and then to prevent clogging; if too much gathers, stop |
| 22:04 | theory | Plate position: best to pour exactly in the middle; stream never 100% straight |
| 22:29 | after | Done: sealing rod; check crucible is empty; turbo to push the last; then melting pressure, sealing rod, generator stop, ultrasonic stop |
| 22:58 | theory | Very little material may not pour; turbo helps and clears the nozzle; mostly practice and feel |
| 23:29 | theory | Counterintuitive: pouring more helps; lose a droplet but plate heats, wets, rest atomizes quickly |
| 23:49 | theory | Pour straight on the plate from the start; metal plates are thin and heat in one spot |
| 24:16 | theory | Wetting lets vibration into the melt; a dry droplet bounces; cavitation releases droplets; there is a paper on it |
| 24:49 | after | No need to lower setpoint: generator stop means no heating; set 250 for next time anyway |
| 25:52 | before | For tomorrow drill one or two nozzles to ~0.7 mm (Dremel/Proxxon); a 0.6 drill by hand works; graphite machines easily |
| 26:53 | chatter | Hikes; other installs (Denver, California, Nevada, Oregon); Utah dryness |
| 30:15 | theory | Turbo recap: warm up to atomize, correct stream direction; more pressure usually helps |
| 30:37 | troubleshooting | Turbo during cooldown will not keep the nozzle clear: "if it gets clogged, it gets clogged" |
| 31:27 | after | Shutdown list: melting pressure, sealing rod down, generator stop, ultrasonic stop; order irrelevant, do it quickly |
| 32:09 | safety | Prolonged vibration with solidified metal on the plate can break the plate |
| 32:26 | after | Next: take out powder, clean, remove plate, change booster to 1:1, use a metal plate for next test |
| 32:49 | theory | Transducer cooling button; vibrations cannot start without it on |
| 33:16 | after | Turn temperature down; wait to open furnace; chamber can open at 400 C, over 500 C graphite degrades in oxygen |
| 37:27 | after | To open, remove overpressure first; the system blocks you otherwise |
| 38:13 | after | Furnace 350 C still too hot; chamber and cone are water-cooled and ice cold, so wet right after the process |
| 38:41 | safety | Overpressure inside; three clamps; opening one just leaks; with powder inside wear a mask |
| 39:00 | procedure | Remove pressure control, press vent valve; masks on |
| 40:02 | chatter | A customer will plasma-atomize uranium in Europe |
| 41:12 | safety | Lab coat recommended: hands go in to clean everything |
| 42:19 | safety | Aluminum on skin not bad; magnesium completely neutral |
| 42:46 | cleaning | Paper under the opening to catch falling particles; throw them back in |
| 43:37 | cleaning | Cool argon still coming out; brush powder back into the chamber |
| 44:04 | cleaning | Vacuum later for leftovers; everything pushed down to the container |
| 44:34 | cleaning | If the ceramic bowl is cool, remove larger pieces and throw powder back in; powder also in the view port |
| 45:09 | cleaning | Remove the plate; slide everything out |
| 50:32 | after | Dust settled; open; push everything into the container and remove it |
| 50:51 | after | Pour powder onto paper, remove larger pieces, slide into a container |
| 52:25 | after | Shut down cooling; nominal 100 C, earlier is fine when empty and cold, furnace open |
| 53:39 | after | Close the container valve first (pull down and move); it is heavier than it looks |
| 54:14 | after | Secure contents, brush powder off the top, open valve, small brush |
| 55:12 | after | Store elsewhere; remove remaining pieces by hand or through a mesh |
| 55:52 | chatter | Bartosz left the lab partly to avoid PPE; recently atomized Nitinol |

### Procedural steps

Before
- Check the temperature setpoint before heating; it stays at whatever was entered last (03:42)
- Normal heat-and-purge: 250 C, gas wash furnace and chamber; 500 C, repeat; then final temperature (05:48, 08:17)
- Disable pressure control before starting the vacuum pump (06:14)
- Purge chamber: vacuum to the minimum, protective gas fill, repeat; then re-enable pressure control (10:40, 11:07)
- Go directly to melting pressure after the final gas wash (05:17)
- Drill one or two spare nozzles to ~0.7 mm for tomorrow's powder-packed cups (25:52)

During
- Melt at ~1000 C; once the charge slumps reduce to 800 C and wait 2 min for full melt and mixing (09:02, 14:45)
- Rescan the ultrasonic stack just before pouring; scans expire (14:49, 18:08)
- Confirm frequency a bit over 40 kHz; if off, re-tighten the stack (18:32, 19:03)
- Ultrasonic start, then sealing rod up and graining pressure (19:12, 19:20)
- Use turbo pressure to push at the beginning until the stream is stable (19:24)
- If the stream gathers instead of atomizing, pour more to heat the plate (20:34, 21:00)
- Give short turbo pushes to stabilize and prevent clogging; stop if too much gathers (21:12)
- Aim to pour in the middle of the plate (22:10)

After
- Crucible empty: sealing rod, check crucible, turbo for the last drops; melting pressure, sealing rod, generator stop, ultrasonic stop, quickly (22:29, 31:34)
- Set the temperature to 250 C for next time (25:01)
- Turn off transducer cooling (32:49)
- Wait to ~400 C before opening the chamber (33:29)
- Disable pressure control, press vent valve to release overpressure (39:00)
- Masks and lab coat on before opening with powder inside (38:52, 41:12)
- Shut down the cooling water around 100 C, or earlier if the crucible is empty (52:25)

Cleaning
- Hold paper under the opening to catch particles; return them (42:46)
- Brush powder from cone, plate and view port down into the chamber and container (43:41, 44:25)
- Remove larger pieces from the ceramic bowl once cool (44:34)
- Remove the plate (45:09)
- Let dust settle, open, push everything into the container (50:32)
- Pour onto paper, pick out large pieces, slide into the storage container (50:51)
- Close the container valve before removing it; it is heavy (53:39)
- Brush powder off the container top and secure it; sieve by hand or mesh (54:14, 55:24)
- Change booster to 1:1 and fit a metal plate for the next test (32:33)

Troubleshooting
- Gauge cannot reach −1 bar at altitude; ~−0.85 bar is the display max (01:11)
- Setpoint overshoot: skip the 250 step and purge immediately as long as nothing has melted (03:32, 04:00)
- Stream too thin, gathering: pour more (20:29)
- Little material left will not pour: turbo (22:58)
- Turbo during cooling does not prevent clogging (30:47)
- Frequency off: loose joint in the stack, re-screw (19:03)

### Parameters and numbers

| value | context | mm:ss |
| --- | --- | --- |
| −1 bar / −0.8x bar | true vacuum vs. display max at altitude | 01:07 |
| ~15% | gauge difference at altitude | 02:05 |
| ~20 mm | rod edge to crucible inner wall | 03:01 |
| 800 C | setpoint it jumped to | 03:26 |
| 250 C, 500 C | purge hold temperatures | 05:50 |
| 1 furnace, 2 chamber | purges done this run | 03:49 |
| ~1000 C | melt temperature for aluminum | 09:02 |
| 2000 C | graphite safe with no oxygen | 14:26 |
| 800 C | reduced setpoint for pouring | 14:45 |
| 2 min | wait after full melt | 14:58 |
| >40 kHz | required scan frequency | 18:32 |
| 0.7 mm; 0.6 mm | nozzle drill target; hand-drill size | 26:10 |
| 1:1 | booster for next test | 32:37 |
| 400 C; 500 C | safe to open chamber; graphite degrades above | 33:31 |
| 350 C | furnace still too hot | 38:16 |
| 3 | chamber clamps | 38:48 |
| 100 C | nominal cooling shut-off | 52:42 |

### Quotable moments

- 01:25 "In reality it's minus one, but it can only display minus 80 something, because it's checking the pressure of the air."
- 14:22 "You can easily heat it up to 2,000, nothing will happen if there is no oxygen. It's just if there is oxygen the degradation can happen very quickly."
- 19:03 "In the worst case scenario, screw everything again. Maybe the connection is loose. That may cause the frequency to be off."
- 19:54 "If the stream starts to move a lot, using turbo pressure can help to push it and unclog the nozzle from any small debris."
- 23:29 "It may be counterintuitive to pour more... but you lose a droplet, the plate heats up, the material wets it and everything else is atomizing very quickly."
- 24:28 "If it's just a droplet sitting on it, it will bounce. If it's wetting, the vibrations will go through."
- 32:09 "There is no need to keep vibrations. It may cause the plate to get damaged because there will be solidified material on it."
- 33:29 "We can also open the chamber if it's 400. It's just safe for the graphite. Over 500 there is a faster degradation of graphite because of the oxygen."

### Unclear / needs checking

- 03:26 "we did go straight to 800" vs. 09:02 "about a thousand Celsius for melting aluminum, yes": which setpoint was actually used before reducing to 800 at 14:45.
- 02:44 "225. That's where the power kit" — unresolved (crucible dimension, ID, or mass).
- 09:20 "if it's not sticking out so much, it's going to be fine" — referent unclear (rod height above coil?).
- 20:23 "remove the ultrasonic system and use turbo pressure" — probably a mis-hearing; order of actions at the pour is unclear.
- 44:34 "ceramic bowl" — probably the cone/funnel below the sonotrode (inferred).
- 40:46 "Did you set this one up already? both accounts" — unrelated to the run, context lost.
- Long caption gaps (15:01–17:28, 46:21–50:32) cover the melt wait and the chamber cleaning; nothing was said that the captions caught.
