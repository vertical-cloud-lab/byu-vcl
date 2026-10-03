# Atomizer videos: timestamp log

_735 timestamped rows across 22 of 26 videos._

Every substantive moment in the BYU VCL atomizer videos (install, AMAZEMET rePowder training Sep 29–30 2026, and the team's own runs), indexed from the transcripts in [`transcripts/`](transcripts/). Rows were extracted from the caption text by reading agents and the `mm:ss` is the caption start time, so a link lands at most a few seconds before the moment.

**Links do not autoplay.** The `mm:ss` link opens YouTube's embed player paused at that second (`youtube.com/embed/<id>?start=<s>`; embeds only autoplay when `autoplay=1` is passed). The ▶ link is the normal watch page at the same time, which does autoplay. Unlisted videos open with either link; private ones need the channel login.

Phases: *before* (utilities, stack, furnace prep, loading), *during* (pump-down/gas wash, heating, atomizing), *after* (shutdown, cooldown, venting, powder collection), *cleaning/maintenance*, *theory*, *troubleshooting*, *installation*, *chatter*.

Transcript source per video is listed in the heading: **whisper** = faster-whisper large-v3-turbo on the runner, **auto** = YouTube auto-captions. Whisper is more accurate; the auto-caption rows will be re-checked as Whisper transcripts land.

## Video 1 of atomizer training
`wRc8p2_FnJo` · 2026-09-29 · 47:20 · unlisted · transcript: whisper · [open paused](https://www.youtube.com/embed/wRc8p2_FnJo?start=0) · [▶ watch](https://www.youtube.com/watch?v=wRc8p2_FnJo)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:16](https://www.youtube.com/embed/wRc8p2_FnJo?start=16) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=16s) | before | Power-up: main breaker was off since yesterday; leave transformer breaker on all the time, shut the other one when people work around the machine |
| [00:54](https://www.youtube.com/embed/wRc8p2_FnJo?start=54) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=54s) | theory | Tour inside the module; standard product is cabinet + induction module, here combined into one unit |
| [01:27](https://www.youtube.com/embed/wRc8p2_FnJo?start=87) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=87s) | theory | Left side: compressed-air inlet with moisture filters and pressure reducer; ~4 bar in flow, 8 bar supply; air only cools the transducer |
| [01:58](https://www.youtube.com/embed/wRc8p2_FnJo?start=118) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=118s) | safety | If air pressure is too low, ultrasonic vibration is disabled with an error |
| [02:12](https://www.youtube.com/embed/wRc8p2_FnJo?start=132) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=132s) | parts | Two argon lines: one fills the chamber, one feeds the furnace. Top regulator "sealing rod" drives the rod up/down; lower one supplies fill, purge, pneumatics |
| [03:02](https://www.youtube.com/embed/wRc8p2_FnJo?start=182) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=182s) | parts | Cooling water passes an extra pressure reducer, then a flow + temperature sensor; path furnace, cone, chamber, return |
| [03:25](https://www.youtube.com/embed/wRc8p2_FnJo?start=205) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=205s) | parts | Colour coding of the lines: blue = compressed air; trainee reads silver as argon and Bartosz accepts, which leaves clear = water |
| [03:35](https://www.youtube.com/embed/wRc8p2_FnJo?start=215) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=215s) | parts | Furnace exhaust passes a brass pre-filter in the furnace and a finer filter on the back; replace if dirty or pressure will not release |
| [04:06](https://www.youtube.com/embed/wRc8p2_FnJo?start=246) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=246s) | maintenance | This side is maintenance-free; look for gas leaks/deteriorated hoses every few weeks or months; keep closed during operation |
| [04:49](https://www.youtube.com/embed/wRc8p2_FnJo?start=289) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=289s) | parts | Other side (more cramped): induction generator control at bottom, do not touch unless it fails |
| [05:14](https://www.youtube.com/embed/wRc8p2_FnJo?start=314) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=314s) | parts | Pneumatic block controls all furnace valves (vacuum, purge, fill, gas removal); separate block controls chamber pressure |
| [05:41](https://www.youtube.com/embed/wRc8p2_FnJo?start=341) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=341s) | theory | Vacuum valve: running pump always pulls on the furnace; chamber vacuum requires opening the additional valve (manual) |
| [06:06](https://www.youtube.com/embed/wRc8p2_FnJo?start=366) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=366s) | theory | Oxygen sensor needs a small continuous bleed flow via a settable valve; valve open only above 50 mbar, closed under vacuum |
| [06:39](https://www.youtube.com/embed/wRc8p2_FnJo?start=399) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=399s) | safety | Vent valve removes overpressure; pressure sensor; mechanical safety valve opens automatically if chamber pressure exceeds 0.8 bar, even if the vent valve fails (Whisper: "0.8 bars"; captions heard 8 bar) |
| [07:02](https://www.youtube.com/embed/wRc8p2_FnJo?start=422) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=422s) | parts | HEPA filter keeps powder out of sensors and vacuum pump |
| [07:16](https://www.youtube.com/embed/wRc8p2_FnJo?start=436) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=436s) | troubleshooting | Argon feed moved to enter chamber directly, in an arc; feeding next to the O2 sensor gives falsely low readings |
| [08:05](https://www.youtube.com/embed/wRc8p2_FnJo?start=485) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=485s) | maintenance | HEPA: remove and check about every 2 months; powder collects at bottom; disconnect at two points, pull the whole unit out, unbolt the cover, filter pops out; spares on hand |
| [08:51](https://www.youtube.com/embed/wRc8p2_FnJo?start=531) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=531s) | safety | Put used filter in a metal tray/basket with sand nearby; very fine evaporate dust is prone to spontaneous combustion (mainly a plasma-unit problem; here only with magnesium or overheated, evaporating material); it is a rapid oxidation rather than a real fire; filter is thin polyester mesh |
| [09:53](https://www.youtube.com/embed/wRc8p2_FnJo?start=593) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=593s) | parts | Ultrasonic generator: parameters changeable via app; remote session with AMAZEMET possible for issue sorting |
| [10:27](https://www.youtube.com/embed/wRc8p2_FnJo?start=627) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=627s) | troubleshooting | PLC, transformers, fuses for furnace, vacuum pump, generator: first place to check if an electrical part fails |
| [11:20](https://www.youtube.com/embed/wRc8p2_FnJo?start=680) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=680s) | parts | Main switch powers whole device; internal connections rewired so everything hooks in here |
| [11:44](https://www.youtube.com/embed/wRc8p2_FnJo?start=704) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=704s) | maintenance | Software update: USB port on back of HMI; SD card in PLC; keep old copy |
| [12:58](https://www.youtube.com/embed/wRc8p2_FnJo?start=778) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=778s) | maintenance | Back connections: heat exchanger, vacuum pump, compressor, argon, water. Vacuum pump needs the most maintenance |
| [13:14](https://www.youtube.com/embed/wRc8p2_FnJo?start=794) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=794s) | maintenance | Vacuum pump oil: sight glass, keep between min and max; standard vacuum pump oil |
| [13:37](https://www.youtube.com/embed/wRc8p2_FnJo?start=817) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=817s) | maintenance | Oil-mist filter (foam) collects oil in blue canister; every few weeks remove black screw and pour out; can route to exhaust or a bucket |
| [14:46](https://www.youtube.com/embed/wRc8p2_FnJo?start=886) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=886s) | parts | Vacuum pump need not be bolted down; rubber feet damp vibration |
| [14:56](https://www.youtube.com/embed/wRc8p2_FnJo?start=896) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=896s) | maintenance | Heat exchanger: check water level; darkish water is fine, it is filtered; low-level sensor shuts everything down |
| [15:40](https://www.youtube.com/embed/wRc8p2_FnJo?start=940) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=940s) | troubleshooting | If water valves are closed the internal loop slowly overheats; it is a separate loop cooled through a mechanical heat exchanger; temp shown on HMI |
| [15:53](https://www.youtube.com/embed/wRc8p2_FnJo?start=953) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=953s) | before | Heat exchanger: just switch it on, nothing else to do; have the water valves open first (slightly open is enough); it runs even with them closed but the internal loop temperature creeps up |
| [17:17](https://www.youtube.com/embed/wRc8p2_FnJo?start=1037) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1037s) | troubleshooting | HMI error "cooling water flow low" because heat exchanger is off; do not start it until ready to heat (noise) |
| [17:49](https://www.youtube.com/embed/wRc8p2_FnJo?start=1069) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1069s) | safety | Compressed air only cools transducer; no air means no vibrations; any displayed error stops heating instantly |
| [18:11](https://www.youtube.com/embed/wRc8p2_FnJo?start=1091) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1091s) | theory | HMI accounts: admin and others (111, 222, 333...); can restrict who can change settings or press buttons |
| [19:22](https://www.youtube.com/embed/wRc8p2_FnJo?start=1162) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1162s) | theory | Settings: high and critical oxygen warnings; clock in Polish time; total on-time and ultrasonic-on time |
| [19:58](https://www.youtube.com/embed/wRc8p2_FnJo?start=1198) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1198s) | before | Advanced ultrasonics page: check transducer + booster stack; scan gives "no air pressure" error until air is on |
| [20:58](https://www.youtube.com/embed/wRc8p2_FnJo?start=1258) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1258s) | theory | Transducer cooling only needed for the few minutes of atomization |
| [21:07](https://www.youtube.com/embed/wRc8p2_FnJo?start=1267) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1267s) | theory | Scan sends a weak signal to find best frequency; one single wide peak is good; more parts make the usable range narrower |
| [21:53](https://www.youtube.com/embed/wRc8p2_FnJo?start=1313) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1313s) | theory | Set amplitude, start vibration; shows frequency and power; amplitude = intensity; cooling runs 1 min after stop |
| [22:32](https://www.youtube.com/embed/wRc8p2_FnJo?start=1352) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1352s) | parameter | Scan range: 40 kHz system, scan 1 kHz around, 39 to 41 kHz |
| [22:53](https://www.youtube.com/embed/wRc8p2_FnJo?start=1373) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1373s) | parameter | After scan F-start/F-stop auto-set: peak +200 Hz and −600 Hz; frequency drops as parts heat, generator tracks it |
| [23:48](https://www.youtube.com/embed/wRc8p2_FnJo?start=1428) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1428s) | theory | Frequency set by Young's modulus, density, part length; shuts down if out of range or power rises |
| [24:29](https://www.youtube.com/embed/wRc8p2_FnJo?start=1469) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1469s) | theory | Induction atomization program: wait 10 s for communication; reads furnace temperature and pressure (5 mbar shown) |
| [25:03](https://www.youtube.com/embed/wRc8p2_FnJo?start=1503) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1503s) | parameter | Oxygen display max 1000 ppm; do not work above 100 ppm; best 40–50 ppm; rises when atomizing starts (material, chamber moisture) |
| [25:53](https://www.youtube.com/embed/wRc8p2_FnJo?start=1553) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1553s) | theory | Middle: basic ultrasonic start/stop/scan; right: chamber control with protective gas, vent valve, transducer cooling, vacuum pump |
| [26:30](https://www.youtube.com/embed/wRc8p2_FnJo?start=1590) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1590s) | theory | Pump running but vacuum goes to furnace; open the valve to give it to the chamber |
| [26:48](https://www.youtube.com/embed/wRc8p2_FnJo?start=1608) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1608s) | theory | Gas wash: fill chamber to ~500 mbar, pump out without reaching vacuum; avoids room leak at the vacuum limit |
| [27:20](https://www.youtube.com/embed/wRc8p2_FnJo?start=1640) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1640s) | theory | Pressure control holds chamber pressure automatically during pour; used to need manual venting when pressure jumped |
| [27:51](https://www.youtube.com/embed/wRc8p2_FnJo?start=1671) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1671s) | theory | Automatic chamber prep: set target pressure, wait 30 s, fill with argon, repeat or gas wash by oxygen level |
| [28:10](https://www.youtube.com/embed/wRc8p2_FnJo?start=1690) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1690s) | parameter | At altitude cannot reach −1000 mbar; max about −850 reached yesterday; use ~848 as target (sensor calibration) |
| [28:45](https://www.youtube.com/embed/wRc8p2_FnJo?start=1725) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1725s) | parameter | Chamber was at 50 mbar so O2 bleed valve kept toggling at its threshold |
| [29:11](https://www.youtube.com/embed/wRc8p2_FnJo?start=1751) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1751s) | theory | Furnace panel: press button to get green light before any pressure can be applied; legacy confirmation from rotating-chamber model |
| [30:22](https://www.youtube.com/embed/wRc8p2_FnJo?start=1822) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1822s) | safety | With pressure or vacuum in chamber it locks, cannot open |
| [30:37](https://www.youtube.com/embed/wRc8p2_FnJo?start=1837) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1837s) | procedure | Furnace gas wash needs vacuum pump running: vacuum furnace, fill argon, repeat; set for 5 repeats |
| [30:57](https://www.youtube.com/embed/wRc8p2_FnJo?start=1857) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1857s) | theory | After gas wash go straight to melting pressure; graining pressure is higher and pushes material out |
| [31:21](https://www.youtube.com/embed/wRc8p2_FnJo?start=1881) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1881s) | parameter | Example chamber 150: melting pressure slightly below chamber; graining pressure above chamber |
| [31:36](https://www.youtube.com/embed/wRc8p2_FnJo?start=1896) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1896s) | parts | Sealing rod button closes/opens furnace; visible moving |
| [31:54](https://www.youtube.com/embed/wRc8p2_FnJo?start=1914) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1914s) | parameter | Turbo pressure: manual push for poor flow; furnace goes to 1.5 bar while held, drops back to the melting or graining pressure setting on release |
| [32:15](https://www.youtube.com/embed/wRc8p2_FnJo?start=1935) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1935s) | theory | Generator start/stop = heating on/off; vacuum pump button only powers pump, control is from HMI |
| [32:40](https://www.youtube.com/embed/wRc8p2_FnJo?start=1960) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1960s) | theory | Top physical buttons mirror the screen; temperature set manually, hold to go faster |
| [33:03](https://www.youtube.com/embed/wRc8p2_FnJo?start=1983) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=1983s) | parameter | Program setup: max heating power normally 100; can limit or create heat ramp for ceramics/modified crucibles |
| [33:36](https://www.youtube.com/embed/wRc8p2_FnJo?start=2016) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2016s) | parameter | Graining pressure has begin and end: raise pressure as crucible empties to keep flow; turbo max 1.5 bar |
| [34:11](https://www.youtube.com/embed/wRc8p2_FnJo?start=2051) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2051s) | parameter | Hold program setup for service mode; thermocouple type N (Whisper hears "M type"), up to 1300 C, which is what it is designed to reach |
| [34:36](https://www.youtube.com/embed/wRc8p2_FnJo?start=2076) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2076s) | parameter | Service pages show water flow and temperature; must be over 2 L/min to operate |
| [34:59](https://www.youtube.com/embed/wRc8p2_FnJo?start=2099) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2099s) | before | Preparation = furnace prep + chamber prep; chamber must be opened to prep the furnace; AMAZEMET also has videos of this on their site |
| [35:49](https://www.youtube.com/embed/wRc8p2_FnJo?start=2149) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2149s) | before | Remove everything, starting with thermocouple; thin ceramic cover cracks normally, replacements exist; to insert it just align it with the hole; unless the cover is completely destroyed it still works |
| [36:24](https://www.youtube.com/embed/wRc8p2_FnJo?start=2184) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2184s) | before | Move sealing rod up, pull safety pin, take rod out |
| [36:39](https://www.youtube.com/embed/wRc8p2_FnJo?start=2199) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2199s) | parts | Top insulation (silica + alumina mix), then side insulation |
| [37:01](https://www.youtube.com/embed/wRc8p2_FnJo?start=2221) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2221s) | before | Crucible held by a nut; nozzle holder with graphite nozzle may stick; remove bottom insulation, unscrew while holding nut so nothing falls |
| [37:45](https://www.youtube.com/embed/wRc8p2_FnJo?start=2265) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2265s) | parts | Stack: graphite nut, graphite seal, graphite nozzle holder, second graphite seal |
| [38:06](https://www.youtube.com/embed/wRc8p2_FnJo?start=2286) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2286s) | troubleshooting | No thermocouple gives "master temperature sensor" error and an emergency argon bleed (from the bottom, to keep the atmosphere and cool faster); put it back during maintenance |
| [38:53](https://www.youtube.com/embed/wRc8p2_FnJo?start=2333) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2333s) | maintenance | Brass preliminary filter catches evaporate and splashes; clean in ultrasonic bath if clogged |
| [39:18](https://www.youtube.com/embed/wRc8p2_FnJo?start=2358) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2358s) | before | Graphite nozzle is the consumable; look through to check it is clear; keep precise drills or needles to unclog |
| [39:54](https://www.youtube.com/embed/wRc8p2_FnJo?start=2394) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2394s) | parameter | Nozzle 0.5 mm standard; drill to 0.7, up to 1 mm max for standard operation |
| [40:20](https://www.youtube.com/embed/wRc8p2_FnJo?start=2420) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2420s) | theory | Al 4047 flows well; copper, tin, brass, bismuth, antimony, silver, gold also done; silver/gold ideal (no oxidation) |
| [41:05](https://www.youtube.com/embed/wRc8p2_FnJo?start=2465) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2465s) | troubleshooting | Al alloys, magnesium, odd compositions may need larger hole; inconsistent flow or clogging means go bigger |
| [41:30](https://www.youtube.com/embed/wRc8p2_FnJo?start=2490) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2490s) | parameter | Al-Si-Mg works at 0.5 but more reliable at 0.7; contaminated/oxidized feed flows worse |
| [41:59](https://www.youtube.com/embed/wRc8p2_FnJo?start=2519) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2519s) | before | Standard graphite crucible; coat with boron nitride (or yttria) spray before use; crucibles are not sold pre-coated |
| [42:23](https://www.youtube.com/embed/wRc8p2_FnJo?start=2543) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2543s) | before | Best coating: boron nitride in alcohol solution with inorganic binders; very thin layer; coat the night before and let dry (can warm it slightly); lasts a few processes; a spray bottle ~$50 |
| [43:23](https://www.youtube.com/embed/wRc8p2_FnJo?start=2603) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2603s) | parts | Nozzles in graphite or pure boron nitride; sealing rods graphite or alumina (reactive materials); coating the sealing rod is worse, not better: too thick a coating can block the nozzle |
| [44:11](https://www.youtube.com/embed/wRc8p2_FnJo?start=2651) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2651s) | cleaning | Wipe all parts; most important is the seal; vacuum dust and splashes; else small leak; wipe evaporate off glass |
| [45:36](https://www.youtube.com/embed/wRc8p2_FnJo?start=2736) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2736s) | cleaning | Graphite always leaves black on wipes, normal |
| [45:54](https://www.youtube.com/embed/wRc8p2_FnJo?start=2754) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2754s) | before | Nozzle into holder: orientation matters, white side on top |
| [46:08](https://www.youtube.com/embed/wRc8p2_FnJo?start=2768) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2768s) | before | Thread crucible onto holder; tighten until it feels tight, do not go over |
| [46:33](https://www.youtube.com/embed/wRc8p2_FnJo?start=2793) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2793s) | before | Rebuild: graphite seal, bottom insulation, crucible, thread into chamber, secure with nut |
| [47:02](https://www.youtube.com/embed/wRc8p2_FnJo?start=2822) | [▶](https://www.youtube.com/watch?v=wRc8p2_FnJo&t=2822s) | before | Tighten nut a little; before fully tightening make sure the hole ends up where it can be reached |

## Atomizer Training Video 2
`naePD8o9_Gk` · 2026-09-29 · 56:35 · unlisted · transcript: whisper · [open paused](https://www.youtube.com/embed/naePD8o9_Gk?start=0) · [▶ watch](https://www.youtube.com/watch?v=naePD8o9_Gk)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:26](https://www.youtube.com/embed/naePD8o9_Gk?start=26) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=26s) | during | Warning gone; generator start = start heating, generator stop = stop heating |
| [01:07](https://www.youtube.com/embed/naePD8o9_Gk?start=67) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=67s) | theory | Purge did not reach −1 bar: at altitude the gauge compares to ambient and can only show about −0.8 bar; real vacuum is the same (and powder quality is not affected) |
| [01:44](https://www.youtube.com/embed/naePD8o9_Gk?start=104) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=104s) | unclear | Can the sensors be recalibrated for altitude? Bartosz: no idea; one maybe, the other probably impossible; ~15% difference (captions heard a Denver comparison here; Whisper hears "for both") |
| [02:40](https://www.youtube.com/embed/naePD8o9_Gk?start=160) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=160s) | parts | Crucible size question; a plug as big as one rod down the middle leaves ~20 mm from rod edge to crucible wall (custom cup, inferred) |
| [03:23](https://www.youtube.com/embed/naePD8o9_Gk?start=203) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=203s) | mistake | Material already melting: the setpoint had gone straight to ~1000 C (Whisper: "we just go straight to a tunnel" = "a thousand"; captions heard 800); was it left that high? It stays at the last value entered |
| [03:32](https://www.youtube.com/embed/naePD8o9_Gk?start=212) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=212s) | procedure | Skip the 250 C step; purge now: once the furnace, twice the chamber; vacuum pump + gas wash, safe as long as material has not melted |
| [04:56](https://www.youtube.com/embed/naePD8o9_Gk?start=296) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=296s) | procedure | Furnace: gas wash, then go to overpressure; chamber: vacuum pump + vacuum valve purge, then overpressure; then atomize right away; go directly to melting pressure once the final gas wash finishes |
| [05:48](https://www.youtube.com/embed/naePD8o9_Gk?start=348) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=348s) | parameter | Normal sequence: 250 C and purge, 500 C and purge, then final temperature |
| [06:14](https://www.youtube.com/embed/naePD8o9_Gk?start=374) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=374s) | procedure | Disable pressure control first, then start vacuum pump |
| [08:17](https://www.youtube.com/embed/naePD8o9_Gk?start=497) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=497s) | procedure | Recap (trainee): set 250 C, purge the furnace and the chamber; 500 C, same; then final temperature and melt everything (Whisper places this recap at the start of its 06:09–09:04 segment) |
| [09:02](https://www.youtube.com/embed/naePD8o9_Gk?start=542) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=542s) | parameter | Confirmed: brought to about 1000 C to melt aluminum; copper will need much higher |
| [10:35](https://www.youtube.com/embed/naePD8o9_Gk?start=635) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=635s) | procedure | Chamber purge: go to the minimum value, protective gas, repeat; if it stops going further, move on |
| [11:07](https://www.youtube.com/embed/naePD8o9_Gk?start=667) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=667s) | procedure | Pressure control back on; it was only purged once or twice, so it can simply be repeated; oxygen level pretty good, then low |
| [12:40](https://www.youtube.com/embed/naePD8o9_Gk?start=760) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=760s) | during | Oxygen low; raise the temperature |
| [14:15](https://www.youtube.com/embed/naePD8o9_Gk?start=855) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=855s) | theory | Graphite can go to 2000 C with no oxygen; with oxygen degradation is very fast |
| [14:41](https://www.youtube.com/embed/naePD8o9_Gk?start=881) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=881s) | during | Material slumping; reduce temperature to 800; one more ultrasonic scan; after 800 wait 2 min, then pour |
| [17:45](https://www.youtube.com/embed/naePD8o9_Gk?start=1065) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1065s) | during | Fully melted; sit 2 min to mix |
| [18:08](https://www.youtube.com/embed/naePD8o9_Gk?start=1088) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1088s) | theory | A scan is valid only for a limited time; rescan otherwise; frequency should read a bit over 40 kHz, may drop slightly |
| [18:53](https://www.youtube.com/embed/naePD8o9_Gk?start=1133) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1133s) | troubleshooting | If not above 40 kHz: with the parts here that should be impossible; worst case screw the stack together again, a loose joint shifts the frequency |
| [19:12](https://www.youtube.com/embed/naePD8o9_Gk?start=1152) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1152s) | during | Ultrasonic start; it vibrates; then sealing rod up and graining pressure; turbo pressure if the push is not enough, especially at start |
| [19:44](https://www.youtube.com/embed/naePD8o9_Gk?start=1184) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1184s) | theory | Turbo at the start heats the plate; also stabilizes a wandering stream and unclogs small debris |
| [20:12](https://www.youtube.com/embed/naePD8o9_Gk?start=1212) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1212s) | during | Trainee takes the pour: presses sealing rod, then graining pressure (Whisper hears "draining pressure"), then watch what happens and use turbo pressure to control it |
| [20:29](https://www.youtube.com/embed/naePD8o9_Gk?start=1229) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1229s) | troubleshooting | Stream too thin: it gathers, does not atomize, plate cannot heat up; more volume needed |
| [20:42](https://www.youtube.com/embed/naePD8o9_Gk?start=1242) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1242s) | troubleshooting | Earlier Bartosz poured more to heat the plate and wash off solidified leftovers |
| [21:10](https://www.youtube.com/embed/naePD8o9_Gk?start=1270) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1270s) | during | Stream stable; give a small turbo push now and then (press for just a moment) to prevent clogging; if too much gathers, stop |
| [22:04](https://www.youtube.com/embed/naePD8o9_Gk?start=1324) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1324s) | theory | Plate position: best to pour exactly in the middle; stream never 100% straight |
| [22:29](https://www.youtube.com/embed/naePD8o9_Gk?start=1349) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1349s) | after | Done: with the sealing rod still up, look into the crucible to check it is all out; turbo still brings a little, then nothing more even with turbo; then melting pressure, sealing rod, generator stop, ultrasonic stop |
| [22:58](https://www.youtube.com/embed/naePD8o9_Gk?start=1378) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1378s) | theory | Very little material may not pour; turbo helps and clears the nozzle; mostly practice and feel |
| [23:29](https://www.youtube.com/embed/naePD8o9_Gk?start=1409) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1409s) | theory | Counterintuitive: pouring more helps; lose a droplet but plate heats, wets, rest atomizes quickly |
| [23:49](https://www.youtube.com/embed/naePD8o9_Gk?start=1429) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1429s) | theory | Asked whether to keep the plate out of the way at first: no, pour straight on the plate from the start, maybe with a bit more stream at the beginning; metal plates are thin, heat faster and in one spot |
| [24:16](https://www.youtube.com/embed/naePD8o9_Gk?start=1456) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1456s) | theory | Plate heats from the aluminum's temperature, not from damped vibration; wetting (melt in contact with the plate) lets vibration into the melt; a dry droplet bounces; internal cavitation releases droplets; there are papers on it |
| [24:49](https://www.youtube.com/embed/naePD8o9_Gk?start=1489) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1489s) | after | No need to lower setpoint: generator stop means no heating; set 250 for next time anyway |
| [25:52](https://www.youtube.com/embed/naePD8o9_Gk?start=1552) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1552s) | before | For tomorrow drill one or two nozzles to ~0.7 mm (Dremel/Proxxon); a 0.6 drill by hand works; graphite machines easily |
| [26:53](https://www.youtube.com/embed/naePD8o9_Gk?start=1613) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1613s) | chatter | Hikes; other installs (Denver, California, Nevada, Oregon); Utah dryness |
| [30:15](https://www.youtube.com/embed/naePD8o9_Gk?start=1815) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1815s) | theory | Turbo recap: warm up to atomize, correct stream direction; more pressure usually helps |
| [30:37](https://www.youtube.com/embed/naePD8o9_Gk?start=1837) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1837s) | troubleshooting | Turbo during cooldown will not keep the nozzle clear: "if it gets clogged, it gets clogged" |
| [31:27](https://www.youtube.com/embed/naePD8o9_Gk?start=1887) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1887s) | after | Shutdown list: melting pressure, sealing rod down, generator stop, ultrasonic stop; order irrelevant, do it quickly |
| [32:09](https://www.youtube.com/embed/naePD8o9_Gk?start=1929) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1929s) | safety | Prolonged vibration with solidified metal on the plate can break the plate |
| [32:26](https://www.youtube.com/embed/naePD8o9_Gk?start=1946) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1946s) | after | Next: take out powder, take out the ultrasonic system, remove the plate, change booster to 1:1; metal plate for next test |
| [32:49](https://www.youtube.com/embed/naePD8o9_Gk?start=1969) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1969s) | theory | Transducer cooling button (turned off now); vibrations cannot start without it on; pressure control stayed on throughout |
| [33:16](https://www.youtube.com/embed/naePD8o9_Gk?start=1996) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=1996s) | after | Turn temperature down; wait until the furnace can be opened so it cools faster; chamber can open at 400 C, over 500 C graphite degrades faster in oxygen |
| [37:27](https://www.youtube.com/embed/naePD8o9_Gk?start=2247) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2247s) | after | To open, remove overpressure first; the system blocks you otherwise |
| [38:13](https://www.youtube.com/embed/naePD8o9_Gk?start=2293) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2293s) | after | Furnace 350 C still too hot to touch (cools much faster once open); chamber and cones are water-cooled and ice cold, so chamber cleaning can start right after the process |
| [38:41](https://www.youtube.com/embed/naePD8o9_Gk?start=2321) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2321s) | safety | Overpressure inside; three clamps; opening one just leaks; with powder inside wear a mask |
| [39:00](https://www.youtube.com/embed/naePD8o9_Gk?start=2340) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2340s) | procedure | Remove pressure control, press vent valve; masks on |
| [40:02](https://www.youtube.com/embed/naePD8o9_Gk?start=2402) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2402s) | chatter | Someone in Europe asked about plasma-atomizing uranium (an inquiry, not a confirmed job); lots of interest, from the US as well |
| [41:12](https://www.youtube.com/embed/naePD8o9_Gk?start=2472) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2472s) | safety | Lab coat recommended: hands go in to clean everything |
| [42:19](https://www.youtube.com/embed/naePD8o9_Gk?start=2539) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2539s) | safety | Aluminum on skin not that bad; magnesium completely harmless, the body dissolves it |
| [42:46](https://www.youtube.com/embed/naePD8o9_Gk?start=2566) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2566s) | cleaning | Paper under the opening to catch falling particles; throw them back in |
| [43:37](https://www.youtube.com/embed/naePD8o9_Gk?start=2617) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2617s) | cleaning | Cool argon still coming out; brush powder back into the chamber |
| [44:04](https://www.youtube.com/embed/naePD8o9_Gk?start=2644) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2644s) | cleaning | Vacuum later for leftovers; everything pushed down to the container |
| [44:34](https://www.youtube.com/embed/naePD8o9_Gk?start=2674) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2674s) | cleaning | If the ceramic bowl is cool, remove larger pieces and throw powder back in; powder also in the view port |
| [45:09](https://www.youtube.com/embed/naePD8o9_Gk?start=2709) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=2709s) | cleaning | Remove the plate; slide everything out |
| [50:32](https://www.youtube.com/embed/naePD8o9_Gk?start=3032) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=3032s) | after | Dust settled; open; push everything into the container and remove it |
| [50:51](https://www.youtube.com/embed/naePD8o9_Gk?start=3051) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=3051s) | after | Pour powder onto paper, remove larger pieces, slide into a container; still need to find a container/jar for the powder |
| [52:25](https://www.youtube.com/embed/naePD8o9_Gk?start=3145) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=3145s) | after | Shut down cooling (it will not boil the water any more); nominal 100 C, earlier is fine when the crucible is empty and everything is ice cold, so the coil is safe |
| [53:39](https://www.youtube.com/embed/naePD8o9_Gk?start=3219) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=3219s) | after | Close the container valve first (pull down and move); it is heavier than it looks |
| [54:14](https://www.youtube.com/embed/naePD8o9_Gk?start=3254) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=3254s) | after | Secure contents, brush powder off the top, open valve, small brush |
| [55:12](https://www.youtube.com/embed/naePD8o9_Gk?start=3312) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=3312s) | after | Store elsewhere; remove remaining pieces by hand or through a mesh |
| [55:52](https://www.youtube.com/embed/naePD8o9_Gk?start=3352) | [▶](https://www.youtube.com/watch?v=naePD8o9_Gk&t=3352s) | chatter | Bartosz left the lab partly to avoid PPE; recently atomized Nitinol |

## Atomizer Training Video 3
`txH397FGTAU` · 2026-09-29 · 51:05 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/txH397FGTAU?start=0) · [▶ watch](https://www.youtube.com/watch?v=txH397FGTAU)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:01](https://www.youtube.com/embed/txH397FGTAU?start=1) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1s) | after/cleaning | Narration: "this video is a deep cleaning"; post-run disassembly, long silent stretches. |
| [01:33](https://www.youtube.com/embed/txH397FGTAU?start=93) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=93s) | before | Trainee asks whether a part's orientation matters; trainer: "Not at all" (part not named). |
| [03:28](https://www.youtube.com/embed/txH397FGTAU?start=208) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=208s) | after | Furnace cool enough to take out the parts; parts put back in; "I forgot to put this in". |
| [05:01](https://www.youtube.com/embed/txH397FGTAU?start=301) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=301s) | tools | "The 18 mm wrench will be a must"; buy a set at Ace Hardware. |
| [06:37](https://www.youtube.com/embed/txH397FGTAU?start=397) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=397s) | tools | Torque wrench should have an "80 mm" (likely 18 mm) tip but it was not shipped; induction-only kits get mis-packed. |
| [07:44](https://www.youtube.com/embed/txH397FGTAU?start=464) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=464s) | chatter | Company bureaucracy; AMAZEMET grew from ~10 to 60+ people (11:36). |
| [09:14](https://www.youtube.com/embed/txH397FGTAU?start=554) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=554s) | after | "It did go all the way through, so we can reuse it" (melt poured fully; part reusable, inferred crucible). |
| [09:19](https://www.youtube.com/embed/txH397FGTAU?start=559) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=559s) | tools | Small tweezers "exceptionally useful": one pair for nuts, one for grabbing anything. |
| [09:40](https://www.youtube.com/embed/txH397FGTAU?start=580) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=580s) | lesson | Disassembly went easily "because the oxygen level was much better"; oxide roughens surfaces and makes parts stick. |
| [10:11](https://www.youtube.com/embed/txH397FGTAU?start=611) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=611s) | parts | Plate is a molybdenum alloy; best option for Al, but Mo and Al react if the process runs too long. |
| [12:04](https://www.youtube.com/embed/txH397FGTAU?start=724) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=724s) | troubleshooting | First scan showed a double peak/interruption; a short burst of vibration seated the parts; micro-friction self-resolves. |
| [12:42](https://www.youtube.com/embed/txH397FGTAU?start=762) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=762s) | before | Liquid pattern on plate: straight = plate vibrating well; angled = crack forming, atomization goes around it. |
| [13:06](https://www.youtube.com/embed/txH397FGTAU?start=786) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=786s) | theory | Plan: 1:1 booster now; reversed booster can give really small Al particles but needs alloy and pour knowledge. |
| [13:47](https://www.youtube.com/embed/txH397FGTAU?start=827) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=827s) | chatter | Gage: powders for LPBF characterization, lower-rare-earth alloys. |
| [14:33](https://www.youtube.com/embed/txH397FGTAU?start=873) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=873s) | theory | Low-density metals give bigger particles; Au/Ag much smaller, same technique; spherical, narrow distribution stays usable. |
| [15:21](https://www.youtube.com/embed/txH397FGTAU?start=921) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=921s) | theory | Commercial Al powder 15–45 µm; this is larger but uniform and spherical; still good for printing (Northwestern paper). |
| [16:12](https://www.youtube.com/embed/txH397FGTAU?start=972) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=972s) | before | "Everything in, vibrations fine, so purging." 1:1 booster is slimmer; amplification depends on mass/diameter difference. |
| [16:44](https://www.youtube.com/embed/txH397FGTAU?start=1004) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1004s) | during | Purge plan: one purge without heat, then two with heat; each = vacuum pump then gas wash. |
| [17:10](https://www.youtube.com/embed/txH397FGTAU?start=1030) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1030s) | troubleshooting | Gas "coming out here"; check how far it screws in — if it won't, it did not seat (closure not named). |
| [17:55](https://www.youtube.com/embed/txH397FGTAU?start=1075) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1075s) | during | One side at overpressure while the other purges, then reverse; two temperatures to drive moisture out of new insulation/crucible. |
| [18:34](https://www.youtube.com/embed/txH397FGTAU?start=1114) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1114s) | theory | Magnesium gives the largest particles (light); gold and copper alloys much smaller, same plate and booster. |
| [19:21](https://www.youtube.com/embed/txH397FGTAU?start=1161) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1161s) | theory | First-run powder: narrow distribution, perfect for DED; maybe too big for LPBF. |
| [20:00](https://www.youtube.com/embed/txH397FGTAU?start=1200) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1200s) | after | Shake the jar: bigger particles rise to the top; grains iridescent. |
| [20:18](https://www.youtube.com/embed/txH397FGTAU?start=1218) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1218s) | during | Panel: last state melting pressure; now vacuum pump on, "turn off that and then" (sequence garbled). |
| [21:03](https://www.youtube.com/embed/txH397FGTAU?start=1263) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1263s) | during | Heat up (first heated purge). |
| [21:58](https://www.youtube.com/embed/txH397FGTAU?start=1318) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1318s) | during | Vacuum at its max but reading still falling; in vacuum the oxygen sensor "is not going to tell you anything". |
| [22:31](https://www.youtube.com/embed/txH397FGTAU?start=1351) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1351s) | chatter | Software versions differ; trainer reported UI issues; three cabinet generations. |
| [23:28](https://www.youtube.com/embed/txH397FGTAU?start=1408) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1408s) | during | Press pressure control; get coolant flow; start heating. |
| [30:16](https://www.youtube.com/embed/txH397FGTAU?start=1816) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1816s) | during | Set point changed to 500 °C; pump stays on gas wash; a leak in between would show as pressure loss. |
| [31:05](https://www.youtube.com/embed/txH397FGTAU?start=1865) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1865s) | parts | Plate check: edge peeling/cracking OK if loose bits removed; heavy oxide after an oxygen-rich run → clean fully or new plate; scrape with knife. |
| [32:41](https://www.youtube.com/embed/txH397FGTAU?start=1961) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1961s) | during | "Melt pressure. Turn off pressure control." |
| [32:58](https://www.youtube.com/embed/txH397FGTAU?start=1978) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=1978s) | theory | Automate the 250/500 purge sequence? No: no control over the furnace controller; its software is locked ("a punch card"). |
| [34:15](https://www.youtube.com/embed/txH397FGTAU?start=2055) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2055s) | during | Repeat purge? "Don't depend on this reading with vacuum inside — fill protective gas, then check; if good, no repeat." |
| [34:48](https://www.youtube.com/embed/txH397FGTAU?start=2088) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2088s) | theory | The more runs, the better: heat and vacuum clean the system. |
| [35:02](https://www.youtube.com/embed/txH397FGTAU?start=2102) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2102s) | during | Set max temperature 1000 °C to melt the rods. |
| [37:34](https://www.youtube.com/embed/txH397FGTAU?start=2254) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2254s) | during | At 1000 °C the Al melts; "when the whistle goes" the Al jumps up in the middle — induction pull, free mixing. |
| [38:38](https://www.youtube.com/embed/txH397FGTAU?start=2318) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2318s) | during | As soon as it melts, go down; for a metal plate ~780–790 °C is enough; lower temperature = plate durability. |
| [38:55](https://www.youtube.com/embed/txH397FGTAU?start=2335) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2335s) | theory | Lower amplitude is kinder to the plate but can under-atomize (material flows through); start higher, reduce later. |
| [39:26](https://www.youtube.com/embed/txH397FGTAU?start=2366) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2366s) | theory | Lower amplitude = smaller particles but slower, more fragile; booster = mechanical control, generator % = electrical. |
| [40:00](https://www.youtube.com/embed/txH397FGTAU?start=2400) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2400s) | parameter | Amplitude 50–100 % = share of generator max current; 100 high; 80–90 best; start ~90 and adjust. |
| [40:55](https://www.youtube.com/embed/txH397FGTAU?start=2455) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2455s) | before | Ultrasonic scan test; turn on transducer cooling first. |
| [41:14](https://www.youtube.com/embed/txH397FGTAU?start=2474) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2474s) | parts | Cooling here is fully manual; newest version stops it 1 min after vibration; plasma runs up to 4 h continuous. |
| [41:48](https://www.youtube.com/embed/txH397FGTAU?start=2508) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2508s) | during | Start sequence: vibration on, draining pressure, sealing rod, turbo pressure — "do it all as quickly as possible". |
| [42:14](https://www.youtube.com/embed/txH397FGTAU?start=2534) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2534s) | during | "More amplitude." Pouring a bit too much; use the draining pressure; "too much pressure makes it shoot out too fast". |
| [43:05](https://www.youtube.com/embed/txH397FGTAU?start=2585) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2585s) | troubleshooting | Some of the plate is broken; pouring higher on the plate might help. |
| [43:48](https://www.youtube.com/embed/txH397FGTAU?start=2628) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2628s) | troubleshooting | Plate cracked on one side — interrupts atomization. |
| [44:46](https://www.youtube.com/embed/txH397FGTAU?start=2686) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2686s) | during | Pressure lowered a little; "really good for a moment"; done, stop the vibration (45:07). |
| [45:11](https://www.youtube.com/embed/txH397FGTAU?start=2711) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2711s) | lesson | After another piece broke, atomization improved: rolled/cut Mo plates hold tension points; "faulty from the factory probably". |
| [46:05](https://www.youtube.com/embed/txH397FGTAU?start=2765) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2765s) | after | Nice powder in the container; inspect under a light; "could be better". |
| [47:00](https://www.youtube.com/embed/txH397FGTAU?start=2820) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2820s) | after | Can this be turned off? No — wait for cooling too. |
| [47:28](https://www.youtube.com/embed/txH397FGTAU?start=2848) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2848s) | parts | Wider/longer Mo plates recommended for Al; larger area helps most at low amplitude. |
| [49:29](https://www.youtube.com/embed/txH397FGTAU?start=2969) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2969s) | parts | Wider Mo plate shown; use it for the lowest-amplitude reverse-booster run (needs more time to wet). |
| [49:52](https://www.youtube.com/embed/txH397FGTAU?start=2992) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=2992s) | after | Done for today; full cooldown takes a while; come back in ~30 min. |
| [50:06](https://www.youtube.com/embed/txH397FGTAU?start=3006) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=3006s) | after | Shutdown at ~100 °C: heat exchanger off, close water, compressed air, argon, then power; any order. |
| [50:30](https://www.youtube.com/embed/txH397FGTAU?start=3030) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=3030s) | after | Software will not let you leave the program until 80 °C. |
| [50:46](https://www.youtube.com/embed/txH397FGTAU?start=3046) | [▶](https://www.youtube.com/watch?v=txH397FGTAU&t=3046s) | after | Powder can stay in the chamber overnight; it only cools more slowly; trainer often does this. |

## Atomizer Training Video 4
`1F9_4ccwhss` · 2026-09-29 · 10:08 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/1F9_4ccwhss?start=0) · [▶ watch](https://www.youtube.com/watch?v=1F9_4ccwhss)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:00](https://www.youtube.com/embed/1F9_4ccwhss?start=0) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=0s) | before | Side insulation being placed; Gage invited to feel how tight the assembly gets. |
| [00:31](https://www.youtube.com/embed/1F9_4ccwhss?start=31) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=31s) | before | Hole in insulation must line up with the thermocouple port; thermocouple is flexible, can bend, must get close enough. |
| [00:53](https://www.youtube.com/embed/1F9_4ccwhss?start=53) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=53s) | before | "Maybe a little bit too far" — thermocouple position corrected; then side insulation (01:01). |
| [01:08](https://www.youtube.com/embed/1F9_4ccwhss?start=68) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=68s) | parts | Insulation is a silica and alumina mix; dusty — vacuum the furnace area, especially if something falls in the crucible. |
| [01:41](https://www.youtube.com/embed/1F9_4ccwhss?start=101) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=101s) | parts | "If it falls, it will immediately break"; get it into the hole first (graphite sealing rod, inferred). |
| [01:52](https://www.youtube.com/embed/1F9_4ccwhss?start=112) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=112s) | before | Sealing rod tip must be clean and undamaged: "if it's damaged here, it will just not seal". |
| [02:10](https://www.youtube.com/embed/1F9_4ccwhss?start=130) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=130s) | before | Wipe or vacuum residual dust; "ready to go". |
| [02:18](https://www.youtube.com/embed/1F9_4ccwhss?start=138) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=138s) | before | Remove the "sealing block"; now add the material. |
| [02:39](https://www.youtube.com/embed/1F9_4ccwhss?start=159) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=159s) | theory | Sterling: copper coils, eddy currents; trainer: this is indirect — energy goes into the graphite, graphite heats the charge. |
| [03:35](https://www.youtube.com/embed/1F9_4ccwhss?start=215) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=215s) | theory | Not designed for iron/nickel: melting point too high; plates would not survive; those metals react with graphite. |
| [03:47](https://www.youtube.com/embed/1F9_4ccwhss?start=227) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=227s) | parameter | Generator has enough energy to go up to 1600. |
| [04:05](https://www.youtube.com/embed/1F9_4ccwhss?start=245) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=245s) | theory | Industrial gas atomizers use ceramic crucibles, slow heating, large ceramic nozzles; this unit is built for precious metals. |
| [04:32](https://www.youtube.com/embed/1F9_4ccwhss?start=272) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=272s) | before | "We always need to clean the feedstock. It's really important." |
| [04:37](https://www.youtube.com/embed/1F9_4ccwhss?start=277) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=277s) | before | Rods stand above the furnace; they go down as they melt. |
| [04:43](https://www.youtube.com/embed/1F9_4ccwhss?start=283) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=283s) | lesson | Long rods heat at the bottom and cool at the top: raise temperature first, then decrease; copper sticking out is very hard to melt. |
| [05:08](https://www.youtube.com/embed/1F9_4ccwhss?start=308) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=308s) | theory | The more compressed the material at the bottom, the faster it melts. |
| [05:17](https://www.youtube.com/embed/1F9_4ccwhss?start=317) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=317s) | before | Close and secure the furnace lid; if it hisses, loosen and adjust the latch to tighten. |
| [05:41](https://www.youtube.com/embed/1F9_4ccwhss?start=341) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=341s) | cleaning | Next: the chamber. Cleaning uses brushes, paper and alcohol only (06:01). |
| [06:09](https://www.youtube.com/embed/1F9_4ccwhss?start=369) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=369s) | cleaning | Particles stuck to the wall (with "thinner"/tin-like materials): stainless-steel scraper; cooled particles stick, they do not melt in. |
| [06:34](https://www.youtube.com/embed/1F9_4ccwhss?start=394) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=394s) | cleaning | Copper or softer scraper is fine; a plastic one may get damaged. |
| [06:51](https://www.youtube.com/embed/1F9_4ccwhss?start=411) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=411s) | cleaning | Clean the sealing surface and the seal; wipe the whole chamber; vacuum first (07:12). |
| [07:24](https://www.youtube.com/embed/1F9_4ccwhss?start=444) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=444s) | safety | Trainee: full-face respirators go on for post-run cleaning. |
| [07:33](https://www.youtube.com/embed/1F9_4ccwhss?start=453) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=453s) | theory | Atomization runs also help clean the equipment (heat removes residue; garbled). |
| [07:49](https://www.youtube.com/embed/1F9_4ccwhss?start=469) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=469s) | parts | View port comes out with a hook wrench. |
| [08:08](https://www.youtube.com/embed/1F9_4ccwhss?start=488) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=488s) | cleaning | The cone below swivels out; take it down to remove all powder; clean and vacuum its seal from below (08:38). |
| [08:47](https://www.youtube.com/embed/1F9_4ccwhss?start=527) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=527s) | cleaning | Brush in a circle so powder falls into the container; do this before removing the container (09:17). |
| [09:30](https://www.youtube.com/embed/1F9_4ccwhss?start=570) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=570s) | safety | "You can't operate until you get an oxygen sensor"; trainer: argon flow is small, but agrees one should be fitted. |
| [09:52](https://www.youtube.com/embed/1F9_4ccwhss?start=592) | [▶](https://www.youtube.com/watch?v=1F9_4ccwhss&t=592s) | parts | Last item: the powder container, made in-house; a few commercial powders shown. |

## Atomizer Training Video 5
`58wJ_Khwgyk` · 2026-09-29 · 1:18:49 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/58wJ_Khwgyk?start=0) · [▶ watch](https://www.youtube.com/watch?v=58wJ_Khwgyk)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:00](https://www.youtube.com/embed/58wJ_Khwgyk?start=0) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=0s) | parts | Powder container types: this one shows its contents and has a built-in valve; a stainless tube is simpler, valve added separately. |
| [00:18](https://www.youtube.com/embed/58wJ_Khwgyk?start=18) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=18s) | parts | AMAZEMET keeps this type for induction and waste circulation; otherwise plain stainless — easier to make and clean; have both. |
| [00:54](https://www.youtube.com/embed/58wJ_Khwgyk?start=54) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=54s) | cleaning | No powder yet, so compressed air may blow out paper-towel dust; never with powder inside (01:32). |
| [01:38](https://www.youtube.com/embed/58wJ_Khwgyk?start=98) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=98s) | context | First rod run; AMAZEMET avoids running powder on the production side; long runs were for an automated plasma system. |
| [02:21](https://www.youtube.com/embed/58wJ_Khwgyk?start=141) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=141s) | parts | Protective plates: hot metals like copper splash if atomization goes wrong; plates stop splashes entering the container. |
| [02:47](https://www.youtube.com/embed/58wJ_Khwgyk?start=167) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=167s) | before | For aluminum one protective plate is enough; splashes stick there, powder falls past. |
| [03:44](https://www.youtube.com/embed/58wJ_Khwgyk?start=224) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=224s) | before | Mounting the container is easier with two people: lift and clamp at the same time. |
| [04:08](https://www.youtube.com/embed/58wJ_Khwgyk?start=248) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=248s) | before | First process uses the booster already in the housing → "large" powder; easy, good for training, but big particles. |
| [04:48](https://www.youtube.com/embed/58wJ_Khwgyk?start=288) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=288s) | before | Finger-tighten the container flange. |
| [05:01](https://www.youtube.com/embed/58wJ_Khwgyk?start=301) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=301s) | before | A jewelry gold-melting bowl goes in the chamber for safety; catches un-atomized melt for reuse; graphite would also work. |
| [05:41](https://www.youtube.com/embed/58wJ_Khwgyk?start=341) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=341s) | before | Wipe the plate; hang covers over chamber openings/door so powder can be swept from the edge (05:50). |
| [06:40](https://www.youtube.com/embed/58wJ_Khwgyk?start=400) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=400s) | parts | Stack base: transducer = stack of piezo discs; compressed-air cooling; LEMO cable brings the generator signal. |
| [07:00](https://www.youtube.com/embed/58wJ_Khwgyk?start=420) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=420s) | safety | Transducer care: don't drop, heat, wet or overheat; always air-cool; "one mistake can actually damage it". |
| [07:20](https://www.youtube.com/embed/58wJ_Khwgyk?start=440) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=440s) | parts | If the air line were closed the system would still see pressure but give no cooling. |
| [07:38](https://www.youtube.com/embed/58wJ_Khwgyk?start=458) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=458s) | cost | Repair ~2,000 (piezo plates swapped); cheap online transducers fail; theirs come from a Polish industrial maker (08:02). |
| [08:21](https://www.youtube.com/embed/58wJ_Khwgyk?start=501) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=501s) | parts | Booster: mechanical amplifier; its ring acts like a spring, so it can be held there without affecting vibration. |
| [08:43](https://www.youtube.com/embed/58wJ_Khwgyk?start=523) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=523s) | parameter | Boosters: 1:1.5 gives 150 % amplitude; reversed it reduces; 1:1 in the middle (09:22). |
| [08:56](https://www.youtube.com/embed/58wJ_Khwgyk?start=536) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=536s) | theory | Reversed booster on Al → smallest particles but needs good wetting and slow pouring; more energy → larger particles, faster, pour more. |
| [09:24](https://www.youtube.com/embed/58wJ_Khwgyk?start=564) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=564s) | theory | 1:1 used for copper and magnesium; not every material atomizes at low amplitude. |
| [09:48](https://www.youtube.com/embed/58wJ_Khwgyk?start=588) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=588s) | lesson | Amplifying booster "will immediately destroy all the plates"; metal plates crack; reversed gave several Al runs without damage. |
| [10:28](https://www.youtube.com/embed/58wJ_Khwgyk?start=628) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=628s) | parts | Connector rod: titanium, prolongs the stack; M10 at the base, M8 at the tip (10:44). |
| [10:59](https://www.youtube.com/embed/58wJ_Khwgyk?start=659) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=659s) | cleaning | Clean threads with IPA; if problems start, unscrew everything and clean all threads (cavitation dust). |
| [11:19](https://www.youtube.com/embed/58wJ_Khwgyk?start=679) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=679s) | parts | Sonotrode: titanium alloy; M8 at the top means a smaller hole in the plate → more contact surface. |
| [11:53](https://www.youtube.com/embed/58wJ_Khwgyk?start=713) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=713s) | parts | For Al a bare carbon-fiber plate works: Al wets and penetrates it; large particles; up to ~10 processes (12:11). |
| [12:39](https://www.youtube.com/embed/58wJ_Khwgyk?start=759) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=759s) | theory | Silicon was atomized on CF with induction; unpoured Si expands on cooling and cracks the crucible (13:02). |
| [13:30](https://www.youtube.com/embed/58wJ_Khwgyk?start=810) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=810s) | parameter | Torques 65 N·m, 60 N·m, 50 or 55 N·m (50 safer): ultrasound must pass; too tight damages threads, loose = friction. |
| [14:38](https://www.youtube.com/embed/58wJ_Khwgyk?start=878) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=878s) | before | Tighten in a vise (best) or on the floor; AMAZEMET uses machined aluminum soft jaws; 18 mm flat wrench needed (15:25). |
| [15:46](https://www.youtube.com/embed/58wJ_Khwgyk?start=946) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=946s) | troubleshooting | A damaged sonotrode would show in the scan. |
| [16:59](https://www.youtube.com/embed/58wJ_Khwgyk?start=1019) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1019s) | before | Torque wrench: pull collar down, rotate so the 60 and 65 marks align → 65 N·m; it clicks when done (17:30). |
| [17:38](https://www.youtube.com/embed/58wJ_Khwgyk?start=1058) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1058s) | before | "Now it's 60"; the final (plate) torque is done with the stack already in the housing. |
| [18:10](https://www.youtube.com/embed/58wJ_Khwgyk?start=1090) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1090s) | before | Hold the stack, but don't push the stiff cable/hose back too much; elbow fittings on order (18:47). |
| [19:03](https://www.youtube.com/embed/58wJ_Khwgyk?start=1143) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1143s) | before | Transducer goes in its cover so nobody hits it; rotate slightly to catch material; clamp only snug (20:18). |
| [21:50](https://www.youtube.com/embed/58wJ_Khwgyk?start=1310) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1310s) | parameter | Full run with cleaning and prep: ~1 h for Al; longer for higher-melting metals. |
| [22:10](https://www.youtube.com/embed/58wJ_Khwgyk?start=1330) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1330s) | before | Once connected, run a scan: a little over 40 kHz is right; scan also checks impedance. |
| [22:56](https://www.youtube.com/embed/58wJ_Khwgyk?start=1376) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1376s) | theory | Holding the vibrating tip heats it instantly; damping shifts frequency; squeaking = loose parts → reassemble (23:18). |
| [24:18](https://www.youtube.com/embed/58wJ_Khwgyk?start=1458) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1458s) | parameter | All energy passes through the transducer: 300–500 W may trip it; expect ≤100–150 W here, ~50 W on most plates. |
| [24:49](https://www.youtube.com/embed/58wJ_Khwgyk?start=1489) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1489s) | before | Insert stack into housing; clamp over, not touching the safety cover; add the final clamp. |
| [25:11](https://www.youtube.com/embed/58wJ_Khwgyk?start=1511) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1511s) | parts | View ports: hardened glass standard, borosilicate optional; furnace window is glass-ceramic; none ever broke. |
| [25:43](https://www.youtube.com/embed/58wJ_Khwgyk?start=1543) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1543s) | before | Centre the plate; hand-tight then wrench to 50 N·m with counter-hold; arrow shows torque direction (26:02). |
| [26:39](https://www.youtube.com/embed/58wJ_Khwgyk?start=1599) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1599s) | before | Rescan; power is higher with the plate attached. |
| [27:32](https://www.youtube.com/embed/58wJ_Khwgyk?start=1652) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1652s) | troubleshooting | Wet test shows spread over the whole surface; a crack makes only half the plate atomize (top yes, bottom no). |
| [28:18](https://www.youtube.com/embed/58wJ_Khwgyk?start=1698) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1698s) | parts | Plate clearly visible through the view port; a phone holder/camera could go there. |
| [28:46](https://www.youtube.com/embed/58wJ_Khwgyk?start=1726) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1726s) | before | Plate holder moves up/down/left/right; melt should land as high as possible without going over the top. |
| [29:21](https://www.youtube.com/embed/58wJ_Khwgyk?start=1761) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1761s) | before | Loosen to turn; up/down needs simultaneous rotation; final adjustment at the first flow (30:32). |
| [30:52](https://www.youtube.com/embed/58wJ_Khwgyk?start=1852) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1852s) | during | Atmosphere: 5 furnace purges + 2 chamber purges at overpressure, repeated at 250 °C and 500 °C for moisture. |
| [31:17](https://www.youtube.com/embed/58wJ_Khwgyk?start=1877) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1877s) | theory | Worth it for Mg or Al (low oxygen gives good flow); for bismuth one purge and opening at 300 °C sufficed. |
| [31:57](https://www.youtube.com/embed/58wJ_Khwgyk?start=1917) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1917s) | before | Argon and compressed air on; cooling not needed until heating starts. |
| [32:05](https://www.youtube.com/embed/58wJ_Khwgyk?start=1925) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1925s) | during | Chamber overpressure: system auto-adds or vents; the hiss is the oxygen-sensor bleed; valve sets a small flow (32:44). |
| [33:00](https://www.youtube.com/embed/58wJ_Khwgyk?start=1980) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=1980s) | safety | Machine will not block a run on bad O2; you watch the value and set alarms yourself. |
| [33:22](https://www.youtube.com/embed/58wJ_Khwgyk?start=2002) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2002s) | during | Graphite seals leak between furnace and chamber, so purge one side while the other holds overpressure. |
| [33:49](https://www.youtube.com/embed/58wJ_Khwgyk?start=2029) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2029s) | during | Vacuum pump on, press gas wash: furnace runs 5 purge cycles automatically; it has no sensor. |
| [34:16](https://www.youtube.com/embed/58wJ_Khwgyk?start=2056) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2056s) | theory | Hot graphite purifies itself. |
| [34:39](https://www.youtube.com/embed/58wJ_Khwgyk?start=2079) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2079s) | troubleshooting | "Pressure crucible" warning: furnace not reaching −1 bar; gas leaking chamber→furnace, maybe sealing rod; still workable. |
| [36:14](https://www.youtube.com/embed/58wJ_Khwgyk?start=2174) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2174s) | troubleshooting | Not reaching −1 = leak; chamber→furnace acceptable, from outside worse; later swap sealing rod/crucible to test (36:27). |
| [37:24](https://www.youtube.com/embed/58wJ_Khwgyk?start=2244) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2244s) | during | "Cooling water flow low" warning — chiller not on yet. |
| [37:35](https://www.youtube.com/embed/58wJ_Khwgyk?start=2255) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2255s) | during | After the last cycle (counter shows 1) manually press melting pressure, then overpressure, then vacuum the chamber (38:12). |
| [38:28](https://www.youtube.com/embed/58wJ_Khwgyk?start=2308) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2308s) | during | Chamber vacuum needs the pump running and the big valve open; furnace valve clicking = argon leaking into chamber (OK). |
| [39:31](https://www.youtube.com/embed/58wJ_Khwgyk?start=2371) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2371s) | during | Wait until chamber pressure stops changing; −1000 mbar at sea level, less at altitude (reading garbled). |
| [40:10](https://www.youtube.com/embed/58wJ_Khwgyk?start=2410) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2410s) | during | Fill protective gas; cycle again ("52, heat it up" — garbled); remove all oxygen and moisture. |
| [40:55](https://www.youtube.com/embed/58wJ_Khwgyk?start=2455) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2455s) | theory | Plasma variant: gas flow all the way through heats the gas in the filters. |
| [41:12](https://www.youtube.com/embed/58wJ_Khwgyk?start=2472) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2472s) | during | Second cycle: pressure control to 150; read O2 only at pressure, not in vacuum; value drops then stabilizes. |
| [41:51](https://www.youtube.com/embed/58wJ_Khwgyk?start=2511) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2511s) | during | Start heating: coolant flow, big switch on, no error, set 250 (heard "50"); press generator start (42:22). |
| [42:31](https://www.youtube.com/embed/58wJ_Khwgyk?start=2551) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2551s) | safety | Hearing protection: use it now; ultrasonic vibration is the worst even if it does not bother you. |
| [42:50](https://www.youtube.com/embed/58wJ_Khwgyk?start=2570) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2570s) | during | To 250 °C almost instantly, always overshoots; vacuum again — gas wash always needs the vacuum pump (43:05). |
| [43:12](https://www.youtube.com/embed/58wJ_Khwgyk?start=2592) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2592s) | theory | Heat evaporates moisture; coatings dry off. Smells: pump oil, hot graphite/metal from the vent, filtered (43:44). |
| [44:19](https://www.youtube.com/embed/58wJ_Khwgyk?start=2659) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2659s) | parts | Door lock engages whenever pressure is off atmospheric. |
| [45:08](https://www.youtube.com/embed/58wJ_Khwgyk?start=2708) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2708s) | during | Last cycle → overpressure; now the chamber: pump has its own furnace valves, chamber big valve is opened manually (45:22). |
| [46:45](https://www.youtube.com/embed/58wJ_Khwgyk?start=2805) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2805s) | theory | Frequency is fixed by hardware (generator, transducer, sonotrode matched); a different set costs under 50,000. |
| [47:22](https://www.youtube.com/embed/58wJ_Khwgyk?start=2842) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2842s) | theory | No 20 kHz for induction; 60 kHz offered but sensitive and hard on parts — explore 40 kHz first. |
| [48:01](https://www.youtube.com/embed/58wJ_Khwgyk?start=2881) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2881s) | during | Oxygen falling; set point up to ~500 °C to drive out moisture. |
| [49:38](https://www.youtube.com/embed/58wJ_Khwgyk?start=2978) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=2978s) | during | Rods standing up will melt "like a stick of butter". |
| [50:11](https://www.youtube.com/embed/58wJ_Khwgyk?start=3011) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3011s) | safety | First powder run: full-face respirators for cleaning; ventilation status unknown, call facilities (50:37). |
| [51:08](https://www.youtube.com/embed/58wJ_Khwgyk?start=3068) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3068s) | during | Melting pressure; O2 rose slightly from heat/evaporation; the filter releases moisture in the first runs. |
| [51:48](https://www.youtube.com/embed/58wJ_Khwgyk?start=3108) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3108s) | parts | Chamber cooling is very good — condensation can appear inside; water exceptionally cold; one exchanger enough (52:33). |
| [52:50](https://www.youtube.com/embed/58wJ_Khwgyk?start=3170) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3170s) | during | Al hold ~790–800 (CF plate can go higher); set 1000 to melt the rods, then lower to 790 (53:14). |
| [53:28](https://www.youtube.com/embed/58wJ_Khwgyk?start=3208) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3208s) | safety | Ventilation checked with a sheet of paper. |
| [54:24](https://www.youtube.com/embed/58wJ_Khwgyk?start=3264) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3264s) | safety | At 1300 °C it is too bright to watch — use a filter or glasses. |
| [55:06](https://www.youtube.com/embed/58wJ_Khwgyk?start=3306) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3306s) | theory | Whistling is the induction; it pulses to hold temperature. |
| [55:23](https://www.youtube.com/embed/58wJ_Khwgyk?start=3323) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3323s) | during | Temperature falls as the rods melt; lower the set point; a packed charge melts easier; a lid shields the crucible (55:45). |
| [57:22](https://www.youtube.com/embed/58wJ_Khwgyk?start=3442) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3442s) | during | Stabilized; once all liquid wait 2 min — measured lag between crucible-wall thermocouple and melt. |
| [58:43](https://www.youtube.com/embed/58wJ_Khwgyk?start=3523) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3523s) | during | Do not wait longer than 2 min — more oxidation, more reactivity; then pour. |
| [58:53](https://www.youtube.com/embed/58wJ_Khwgyk?start=3533) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3533s) | during | Best results need an operator at the window adjusting amplitude, turbo pressure and plate position. |
| [59:51](https://www.youtube.com/embed/58wJ_Khwgyk?start=3591) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3591s) | during | Start: vibrations on; sealing rod up; draining pressure pushes the melt; turbo pressure when necessary. |
| [60:27](https://www.youtube.com/embed/58wJ_Khwgyk?start=3627) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3627s) | during | Stream lands too far — move the plate; "too much"; then better, more area covered, pour a bit higher (60:53). |
| [61:07](https://www.youtube.com/embed/58wJ_Khwgyk?start=3667) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3667s) | during | Once the plate is hot every drop atomizes; initial losses heat the plate; metal plates heat faster (61:34). |
| [62:12](https://www.youtube.com/embed/58wJ_Khwgyk?start=3732) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3732s) | during | End: turbo pressure to clear the nozzle; sealing rod down; melting pressure; generator stop; ultrasonics stop. |
| [62:24](https://www.youtube.com/embed/58wJ_Khwgyk?start=3744) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3744s) | lesson | O2 rose a lot; oxide at the nozzle bends the stream — compensate with plate position (62:54). |
| [63:24](https://www.youtube.com/embed/58wJ_Khwgyk?start=3804) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3804s) | after | Heating stopped; temperature dropping. |
| [63:28](https://www.youtube.com/embed/58wJ_Khwgyk?start=3808) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3808s) | idea | Laser pointer on the sealing-rod arm or holder to mark plate position — "not very hard". |
| [63:58](https://www.youtube.com/embed/58wJ_Khwgyk?start=3838) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3838s) | theory | Aim higher on the plate: longer contact, more heating, all atomized instead of droplets. |
| [64:22](https://www.youtube.com/embed/58wJ_Khwgyk?start=3862) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3862s) | after | Powder in the container plus some in the bowl to brush; repeat, then compare 1:1 booster + metal plate (65:08). |
| [65:22](https://www.youtube.com/embed/58wJ_Khwgyk?start=3922) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3922s) | lesson | No parameter log exists — record parameters by hand. |
| [65:37](https://www.youtube.com/embed/58wJ_Khwgyk?start=3937) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3937s) | after | Around 400 °C the furnace/chamber can be opened to speed cooling. |
| [65:41](https://www.youtube.com/embed/58wJ_Khwgyk?start=3941) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3941s) | troubleshooting | Drips on coolant lines are condensation, more at top temperatures. |
| [66:20](https://www.youtube.com/embed/58wJ_Khwgyk?start=3980) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=3980s) | parts | Chamber water jacket: stainless channels cast in. |
| [66:49](https://www.youtube.com/embed/58wJ_Khwgyk?start=4009) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4009s) | after | Over ~400 open the chamber; everything inside is cold; "just don't touch the [nozzle]". |
| [67:20](https://www.youtube.com/embed/58wJ_Khwgyk?start=4040) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4040s) | cleaning | Brushes push powder down; different sizes for different materials. |
| [67:38](https://www.youtube.com/embed/58wJ_Khwgyk?start=4058) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4058s) | cleaning | Material change in induction mode: vacuum, wipe; ~1 h; scrape anything melted on (68:02). |
| [68:26](https://www.youtube.com/embed/58wJ_Khwgyk?start=4106) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4106s) | after | Around 100 °C you can shut down. |
| [68:51](https://www.youtube.com/embed/58wJ_Khwgyk?start=4131) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4131s) | parts | CF plate is reusable if intact; the bowl can be removed and cleaned (69:37). |
| [70:10](https://www.youtube.com/embed/58wJ_Khwgyk?start=4210) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4210s) | theory | Process is short; prepare the next charge while cooling. |
| [71:41](https://www.youtube.com/embed/58wJ_Khwgyk?start=4301) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4301s) | theory | Lower amplitude lets plates survive higher temperature; metal plates want the amplitude-reducing booster (72:04). |
| [72:18](https://www.youtube.com/embed/58wJ_Khwgyk?start=4338) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4338s) | parts | CF rarely destroyed with Al; coated CF for copper wears out; metal plates crack, hole, piece falls off. |
| [73:48](https://www.youtube.com/embed/58wJ_Khwgyk?start=4428) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4428s) | safety | Full-face respirators labelled; visor sticker replaced instead of the mask (75:02). |
| [76:16](https://www.youtube.com/embed/58wJ_Khwgyk?start=4576) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4576s) | after | Slag always remains at the crucible bottom; paper or tray under parts catches powder to return (76:24). |
| [77:17](https://www.youtube.com/embed/58wJ_Khwgyk?start=4637) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4637s) | safety | Always release the pressure — vent the chamber before opening. |
| [77:48](https://www.youtube.com/embed/58wJ_Khwgyk?start=4668) | [▶](https://www.youtube.com/watch?v=58wJ_Khwgyk&t=4668s) | cleaning | Same material next, so open and brush only; gloves, respirator. |

## Atomizer Training Video 6
`tfb4fsVNIFI` · 2026-09-29 · 0:49 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/tfb4fsVNIFI?start=0) · [▶ watch](https://www.youtube.com/watch?v=tfb4fsVNIFI)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:00](https://www.youtube.com/embed/tfb4fsVNIFI?start=0) | [▶](https://www.youtube.com/watch?v=tfb4fsVNIFI&t=0s) | after | After moving all the powder in, close the container. |
| [00:03](https://www.youtube.com/embed/tfb4fsVNIFI?start=3) | [▶](https://www.youtube.com/watch?v=tfb4fsVNIFI&t=3s) | theory | Argon is heavy and sinks, so after a run the container still holds a semi-protective atmosphere even opened cold. |
| [00:37](https://www.youtube.com/embed/tfb4fsVNIFI?start=37) | [▶](https://www.youtube.com/watch?v=tfb4fsVNIFI&t=37s) | cleaning | Best way to clean after an atomization: open it fully by removing the four nuts (00:42, 00:45). |

## Atomizer training
`Pk0K5sBz-sQ` · 2026-09-29 · 9:32 · public · transcript: auto · [open paused](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=0) · [▶ watch](https://www.youtube.com/watch?v=Pk0K5sBz-sQ)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:49](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=49) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=49s) | chatter | Camera kept recording; lab coat offered and declined |
| [03:56](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=236) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=236s) | cleaning | "With the piece and the powder, we can just brush inside" |
| [04:23](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=263) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=263s) | cleaning | Plate is okay; a big piece should be removed if possible, otherwise the stream takes it by itself |
| [04:50](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=290) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=290s) | cleaning | Powder can be used again without issue; wipe the tube before closing, especially at the bottom; then close it |
| [05:57](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=357) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=357s) | chatter | Keep the solidified piece to show people |
| [06:21](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=381) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=381s) | after | Need to remove slag and check nozzle opening; too hot to touch; a clogged nozzle means taking all pieces out; still 150 C, must wait |
| [06:43](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=403) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=403s) | unclear | Question about ventilation and a better way; answer "no, we still need to wait" |
| [07:36](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=456) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=456s) | chatter | Trainees have to run to class; two light switches three feet apart |
| [08:37](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=517) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=517s) | after | 130 C but crucible is empty; the water is really cold |
| [08:53](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=533) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=533s) | after | Theoretically keep cooling until 100 C; empty and this close it will not boil the water |
| [09:04](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=544) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=544s) | troubleshooting | A big chunk left (e.g. no pour) keeps all the heat in, takes long to cool, keep cooling the whole time |
| [09:18](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=558) | [▶](https://www.youtube.com/watch?v=Pk0K5sBz-sQ&t=558s) | after | Leave it to cool; then remove slag, check nozzle, put new material in |

## Atomizer Training Video 7
`FDRTt68Vfvo` · 2026-09-30 · 52:48 · public · transcript: auto · [open paused](https://www.youtube.com/embed/FDRTt68Vfvo?start=0) · [▶ watch](https://www.youtube.com/watch?v=FDRTt68Vfvo)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:01](https://www.youtube.com/embed/FDRTt68Vfvo?start=1) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1s) | after/cleaning | Asks whether Gage has cleaned the chamber inside before; cleaning is next. |
| [00:09](https://www.youtube.com/embed/FDRTt68Vfvo?start=9) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=9s) | after/cleaning | Between runs: remove the crucible, wipe it, check and probably clean the nozzle, put everything back. |
| [00:19](https://www.youtube.com/embed/FDRTt68Vfvo?start=19) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=19s) | before/setup | Decide atomization setup; use the reverse booster as part of training; first remove the plate, then unscrew everything. |
| [00:41](https://www.youtube.com/embed/FDRTt68Vfvo?start=41) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=41s) | before/setup | Stack is fully mechanical; disassembly order doesn't matter; finally remove housing from booster — four hex screws. |
| [00:59](https://www.youtube.com/embed/FDRTt68Vfvo?start=59) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=59s) | after/cleaning | Ronnie (most vacuum experience) to demonstrate vacuuming inside the chamber. |
| [01:14](https://www.youtube.com/embed/FDRTt68Vfvo?start=74) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=74s) | after/cleaning | Chamber has almost no crevices: only the port to the vacuum pump and the view port; vacuum those, then the surfaces. |
| [02:22](https://www.youtube.com/embed/FDRTt68Vfvo?start=142) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=142s) | chatter | Lab reorganisation: moving a storage cabinet, table placement, longer hoses could move the unit (to ~14:20). |
| [06:35](https://www.youtube.com/embed/FDRTt68Vfvo?start=395) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=395s) | chatter | Idea: robot arm on wheels with spray nozzle and paper-towel gripper to wipe the chamber automatically. |
| [07:08](https://www.youtube.com/embed/FDRTt68Vfvo?start=428) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=428s) | admin | A training attendance list will go round for everyone taking part. |
| [10:30](https://www.youtube.com/embed/FDRTt68Vfvo?start=630) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=630s) | before/storage | Cabinet becomes a dry box with desiccants for powders, graphite consumables, anything to keep dry. |
| [11:24](https://www.youtube.com/embed/FDRTt68Vfvo?start=684) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=684s) | chatter | Head-mounted camera is recording; ideas for a 360 tracking camera or camera glasses. |
| [14:20](https://www.youtube.com/embed/FDRTt68Vfvo?start=860) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=860s) | before/setup | Start taking the stack out; loosen the first fastener; "that is a 17" (mm wrench). |
| [16:48](https://www.youtube.com/embed/FDRTt68Vfvo?start=1008) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1008s) | troubleshooting | Earlier resonance explained: part was slightly off when fully in, tolerance near zero, so it pushed on the separating ring. |
| [17:10](https://www.youtube.com/embed/FDRTt68Vfvo?start=1030) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1030s) | chatter | Where is the atomized 4047 powder that could be used as a sample? |
| [17:51](https://www.youtube.com/embed/FDRTt68Vfvo?start=1071) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1071s) | after/cleaning | How do you clean the plate? "You don't" — careful grinding would probably just destroy it. |
| [18:16](https://www.youtube.com/embed/FDRTt68Vfvo?start=1096) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1096s) | lesson | Keep the same plate for the same material (only a few rounds anyway); need a log of which plate saw which material. |
| [18:35](https://www.youtube.com/embed/FDRTt68Vfvo?start=1115) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1115s) | part | Current plate material stated as tungsten–nickel–iron. |
| [18:55](https://www.youtube.com/embed/FDRTt68Vfvo?start=1135) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1135s) | before/setup | To remove the stack: disconnect everything, then remove the clamp. |
| [19:20](https://www.youtube.com/embed/FDRTt68Vfvo?start=1160) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1160s) | before/setup | The ultrasonic cable connector has a small locking nut; if screwed in, unscrew it or the cable won't come out. |
| [19:45](https://www.youtube.com/embed/FDRTt68Vfvo?start=1185) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1185s) | safety | Keep the cable secured so nobody stands on it; ~1,000 V goes through it. |
| [20:04](https://www.youtube.com/embed/FDRTt68Vfvo?start=1204) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1204s) | safety | Hold the transducer while freeing the stack — if it drops, it's bad; several thousand dollars; converts electrical signal to movement. |
| [20:49](https://www.youtube.com/embed/FDRTt68Vfvo?start=1249) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1249s) | before/setup | Wrench sizes on the stack: 17 and 18 mm. |
| [21:52](https://www.youtube.com/embed/FDRTt68Vfvo?start=1312) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1312s) | before/setup | Option: leave the sonotrode on, unscrew the housing, swap the booster; booster and connector can stay together. |
| [22:11](https://www.youtube.com/embed/FDRTt68Vfvo?start=1331) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1331s) | theory | Which part is the booster: the piece inside the housing; remove it from the sonotrode and connect it the other way round. |
| [22:41](https://www.youtube.com/embed/FDRTt68Vfvo?start=1361) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1361s) | theory | Booster changes amplitude: 1:1 is normal, the other is 1:1.5; reversed it's 1.5:1, giving "75% of normal amplitude" (as said). |
| [23:36](https://www.youtube.com/embed/FDRTt68Vfvo?start=1416) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1416s) | theory | Amplitude 0–100 on screen is % of set generator power — how much current goes to the transducer, not a physical value. |
| [24:01](https://www.youtube.com/embed/FDRTt68Vfvo?start=1441) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1441s) | theory | Could stack three boosters, but power would be very high; mechanical and electrical changes act differently — combine both. |
| [24:50](https://www.youtube.com/embed/FDRTt68Vfvo?start=1490) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1490s) | theory | Amplification comes from going bigger-to-smaller: the difference of mass at the two ends. |
| [25:59](https://www.youtube.com/embed/FDRTt68Vfvo?start=1559) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1559s) | chatter | Camera handover ("Tell me it's recording"). |
| [27:43](https://www.youtube.com/embed/FDRTt68Vfvo?start=1663) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1663s) | chatter | Gloves; Bartosz's magnesium medical-lab work needed a full protective suit. |
| [29:31](https://www.youtube.com/embed/FDRTt68Vfvo?start=1771) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1771s) | before/setup | Threads are M10 everywhere except the transducer, which is M10 fine. |
| [30:16](https://www.youtube.com/embed/FDRTt68Vfvo?start=1816) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1816s) | troubleshooting | Stud seized in the booster; trick: jam two M10 nuts together on it, then unscrew with the nuts. |
| [31:16](https://www.youtube.com/embed/FDRTt68Vfvo?start=1876) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1876s) | theory | Going 1.5:1 reduction: "the lower the amplitude we can achieve, the finer the powder" — so we want the reduction. |
| [32:40](https://www.youtube.com/embed/FDRTt68Vfvo?start=1960) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1960s) | troubleshooting | Studs sometimes seize from vibration, sometimes stay loose; the double-nut trick is basically the only thing that works. |
| [33:03](https://www.youtube.com/embed/FDRTt68Vfvo?start=1983) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1983s) | before/setup | Fit the smaller housing now — it will not pass over the transducer later. |
| [33:17](https://www.youtube.com/embed/FDRTt68Vfvo?start=1997) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=1997s) | before/setup | The KF50 connection is always the top, connecting to the chamber; 1.5:1 end goes up into the chamber. |
| [34:58](https://www.youtube.com/embed/FDRTt68Vfvo?start=2098) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2098s) | before/setup | Housing screws: just tight enough to compress the rubber seals; don't overtighten. |
| [35:18](https://www.youtube.com/embed/FDRTt68Vfvo?start=2118) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2118s) | before/setup | Fit connector stud: the end with the M8 thread and wrench flats must face up so the plate can be tightened. |
| [35:50](https://www.youtube.com/embed/FDRTt68Vfvo?start=2150) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2150s) | before/setup | Use a torque wrench — right torque is very important: transducer–booster 65, booster–sonotrode 60, plate connector 50. |
| [37:18](https://www.youtube.com/embed/FDRTt68Vfvo?start=2238) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2238s) | part | Prolonger sonotrode currently the 80 mm tip; a 70 mm exists; may need combinations. |
| [37:56](https://www.youtube.com/embed/FDRTt68Vfvo?start=2276) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2276s) | before/setup | 17 mm on the transducer; check the arrow on the torque wrench; reverse the ratchet; hold with a second wrench. |
| [38:33](https://www.youtube.com/embed/FDRTt68Vfvo?start=2313) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2313s) | before/setup | Set the torque wrench: pull the collar and rotate; reading = lowest visible number plus vernier (60 + 5 = 65). |
| [40:21](https://www.youtube.com/embed/FDRTt68Vfvo?start=2421) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2421s) | before/setup | Tighten until you hear the click — that's how you know the torque is reached. |
| [40:26](https://www.youtube.com/embed/FDRTt68Vfvo?start=2426) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2426s) | before/setup | After any change, test: connect compressed air and cable, scan, run, confirm normal operation and no snapped connector. |
| [40:55](https://www.youtube.com/embed/FDRTt68Vfvo?start=2455) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2455s) | before/setup | Push the cable connector in and lock it; remember to unlock before removing. |
| [41:03](https://www.youtube.com/embed/FDRTt68Vfvo?start=2463) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2463s) | safety | Carry by the housing; don't touch the transducer — it heats where touched; booster ring is the safe grip (acts like a spring). |
| [41:40](https://www.youtube.com/embed/FDRTt68Vfvo?start=2500) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2500s) | troubleshooting | Frequency reads lower than usual (under 40,000 Hz) with reverse booster; adding the top sonotrode raises it; OK for short processes. |
| [42:16](https://www.youtube.com/embed/FDRTt68Vfvo?start=2536) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2536s) | theory | At maximum amplitude the stack vibrates at a slightly higher frequency. |
| [43:09](https://www.youtube.com/embed/FDRTt68Vfvo?start=2589) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2589s) | before/setup | Install: put the protective plate on first (hard to do afterwards) and make sure the seal is in; lock the door open. |
| [43:32](https://www.youtube.com/embed/FDRTt68Vfvo?start=2612) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2612s) | safety | Normal use: bolt the protective cover over the transducer — someone opening the chamber could hit or wet it; 2–3 min saves thousands. |
| [44:15](https://www.youtube.com/embed/FDRTt68Vfvo?start=2655) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2655s) | theory | Terminology: transducer, housing, booster, prolonger sonotrode, top sonotrode (short bar whose only task is holding the plate). |
| [44:35](https://www.youtube.com/embed/FDRTt68Vfvo?start=2675) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2675s) | theory | Sonotrode length fixed by frequency and material: a multiple of half-wavelength (~70 mm → 70, 140). |
| [44:56](https://www.youtube.com/embed/FDRTt68Vfvo?start=2696) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2696s) | before/setup | Put in the seal (O-ring). |
| [45:40](https://www.youtube.com/embed/FDRTt68Vfvo?start=2740) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2740s) | before/setup | Mount plate: connector (small double-threaded stud) first, then plate, then hold with the top sonotrode. |
| [46:29](https://www.youtube.com/embed/FDRTt68Vfvo?start=2789) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2789s) | lesson | Thread the connector fully in first so the plate isn't forced through the 8 mm ring; the ring snapped at the edge before. |
| [47:37](https://www.youtube.com/embed/FDRTt68Vfvo?start=2857) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2857s) | before/setup | Check nothing snags, surfaces are flat, no gaps; push the top sonotrode fully onto the plate — better than before. |
| [48:12](https://www.youtube.com/embed/FDRTt68Vfvo?start=2892) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2892s) | before/setup | Two 17 mm wrenches; plate joint to 50 torque. |
| [49:30](https://www.youtube.com/embed/FDRTt68Vfvo?start=2970) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=2970s) | before/setup | Final test: menu, scan, vibration/power; put some water on the plate to see it vibrate. |
| [50:21](https://www.youtube.com/embed/FDRTt68Vfvo?start=3021) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=3021s) | troubleshooting | Small crack with dark spot at the plate edge = heating from tension; it will crack there; poor placement → resonance → defects. |
| [51:23](https://www.youtube.com/embed/FDRTt68Vfvo?start=3083) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=3083s) | lesson | Metal plates generally last 1–3 runs; with reverse booster and a low-temperature alloy maybe 4–6. |
| [51:42](https://www.youtube.com/embed/FDRTt68Vfvo?start=3102) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=3102s) | before/setup | Next: connect the container, put the plate inside the protection plate, take care of the frames. |
| [51:55](https://www.youtube.com/embed/FDRTt68Vfvo?start=3115) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=3115s) | lesson | Seen a plate snap after one process and after five of the same kind — not something you can fully rely on. |
| [52:23](https://www.youtube.com/embed/FDRTt68Vfvo?start=3143) | [▶](https://www.youtube.com/watch?v=FDRTt68Vfvo&t=3143s) | cleaning | Clean the O-ring seal; "a lot of isopropyl, a lot of paper towels — that's the base for everything"; get a dispenser. |

## Atomizer Training Video 8
`HTlUrAr5HVU` · 2026-09-30 · 11:52 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/HTlUrAr5HVU?start=0) · [▶ watch](https://www.youtube.com/watch?v=HTlUrAr5HVU)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:07](https://www.youtube.com/embed/HTlUrAr5HVU?start=7) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=7s) | troubleshooting | Something "is getting off... this usually doesn't happen" (object not identifiable from audio). |
| [00:37](https://www.youtube.com/embed/HTlUrAr5HVU?start=37) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=37s) | before/loading | Gage asked the shop for a ~0.5 mm drill bit to make a nozzle; "that is so tiny". |
| [00:57](https://www.youtube.com/embed/HTlUrAr5HVU?start=57) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=57s) | part | The machined nozzle is 0.5 mm; this one is 0.7 mm, fresh; all graphite. |
| [01:28](https://www.youtube.com/embed/HTlUrAr5HVU?start=88) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=88s) | before/loading | Bartosz: screw the nozzle into the crucible first, then put the holder/nut on — easier. |
| [01:41](https://www.youtube.com/embed/HTlUrAr5HVU?start=101) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=101s) | lesson | Producer's order (nozzle holder with nut first) is worse: you must grab the thread or use an awkward special tool. |
| [02:26](https://www.youtube.com/embed/HTlUrAr5HVU?start=146) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=146s) | before/loading | Very little thread engagement — "you just barely have to get it on". |
| [02:52](https://www.youtube.com/embed/HTlUrAr5HVU?start=172) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=172s) | before/loading | Orient the hole on the part "about here", angled, so the other part can travel from here to there. |
| [03:37](https://www.youtube.com/embed/HTlUrAr5HVU?start=217) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=217s) | mistake | Didn't centre it in the hole enough, so the part wasn't fitting. |
| [03:45](https://www.youtube.com/embed/HTlUrAr5HVU?start=225) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=225s) | part | Aluminium–silicon(-ate) insulation; "it just turns into powder"; standard for furnaces. |
| [04:09](https://www.youtube.com/embed/HTlUrAr5HVU?start=249) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=249s) | lesson | It breaks if dropped; already chipped at the top; many fragile consumables. |
| [04:23](https://www.youtube.com/embed/HTlUrAr5HVU?start=263) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=263s) | before/loading | Insulation goes in first; the thermocouple sits there and measures temperature. |
| [04:44](https://www.youtube.com/embed/HTlUrAr5HVU?start=284) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=284s) | cleaning | Clean the sealing rod; centre piece is graphite and really brittle; aluminium didn't stick much. |
| [05:29](https://www.youtube.com/embed/HTlUrAr5HVU?start=329) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=329s) | cleaning | Need scrapers/specific tools; for now squeeze and rub across the aluminium. |
| [06:13](https://www.youtube.com/embed/HTlUrAr5HVU?start=373) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=373s) | lesson | Damaging the rod shaft isn't a big deal, but the tip must be good, or you need a new tip/shaft. |
| [06:25](https://www.youtube.com/embed/HTlUrAr5HVU?start=385) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=385s) | part | This (rod) is what goes into the chamber (furnace). |
| [07:30](https://www.youtube.com/embed/HTlUrAr5HVU?start=450) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=450s) | lesson | Contamination: keep "our aluminium one" and "our copper one" sets; doesn't need to be 100%. |
| [08:43](https://www.youtube.com/embed/HTlUrAr5HVU?start=523) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=523s) | before/loading | Close the furnace. |
| [09:09](https://www.youtube.com/embed/HTlUrAr5HVU?start=549) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=549s) | before/loading | How tight? Enough to get a seal — if not tight enough, air gets in. |
| [09:53](https://www.youtube.com/embed/HTlUrAr5HVU?start=593) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=593s) | idea | Laser pointer through the pour path to show where metal will land on the plate before heating; wastes less. |
| [10:59](https://www.youtube.com/embed/HTlUrAr5HVU?start=659) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=659s) | before/loading | Ready; waiting for material; clean the lid (smaller lid is easier). |
| [11:26](https://www.youtube.com/embed/HTlUrAr5HVU?start=686) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=686s) | cleaning | Residue flakes off the lid; rub it clean for a good seal. |
| [11:41](https://www.youtube.com/embed/HTlUrAr5HVU?start=701) | [▶](https://www.youtube.com/watch?v=HTlUrAr5HVU&t=701s) | before/loading | Last part before loading more material. |

## Atomizer Training Video 9
`9kn-HhXCr1o` · 2026-09-30 · 50:08 · public · transcript: whisper · [open paused](https://www.youtube.com/embed/9kn-HhXCr1o?start=0) · [▶ watch](https://www.youtube.com/watch?v=9kn-HhXCr1o)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:00](https://www.youtube.com/embed/9kn-HhXCr1o?start=0) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=0s) | during/pump-down | Gas wash running: furnace (crucible chamber) purged first, now the atomizing chamber at −848 mbar; argon backfill next. |
| [00:30](https://www.youtube.com/embed/9kn-HhXCr1o?start=30) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=30s) | during/pump-down | Vacuum pump switches off; cycle = pump air out, fill with argon, pump out again. |
| [01:07](https://www.youtube.com/embed/9kn-HhXCr1o?start=67) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=67s) | theory | Oxygen reading becomes inaccurate under vacuum — don't trust it until backfilled. |
| [01:41](https://www.youtube.com/embed/9kn-HhXCr1o?start=101) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=101s) | during/pump-down | Press pressure control → chamber brought up to 150 mbar. |
| [01:58](https://www.youtube.com/embed/9kn-HhXCr1o?start=118) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=118s) | during/prep | Turn on the heat exchanger (big red switch on the back); wait for the "water flow too low" alarm to clear. |
| [02:17](https://www.youtube.com/embed/9kn-HhXCr1o?start=137) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=137s) | during/heating | Must press generator start first; setpoint was 800, bring it down to 250 (°C). |
| [03:02](https://www.youtube.com/embed/9kn-HhXCr1o?start=182) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=182s) | during/pump-down | Once at setpoint: pressure control off, then vacuum pump on; gas wash just stays on. |
| [03:25](https://www.youtube.com/embed/9kn-HhXCr1o?start=205) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=205s) | theory | While pumping one volume keep overpressure in the other, so a leak pulls argon rather than air. |
| [03:43](https://www.youtube.com/embed/9kn-HhXCr1o?start=223) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=223s) | theory | Pressure control is chamber only; furnace has its own melting pressure and "graining" (pouring) pressure. |
| [04:16](https://www.youtube.com/embed/9kn-HhXCr1o?start=256) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=256s) | during/pump-down | Gas wash = five purges down to −0.85 bar, backfill, cleanse again. |
| [04:40](https://www.youtube.com/embed/9kn-HhXCr1o?start=280) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=280s) | lesson | Argon cylinder read 2,000 on Monday; just over half used after 5–6 runs. |
| [04:58](https://www.youtube.com/embed/9kn-HhXCr1o?start=298) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=298s) | during/pump-down | Counter shows how many purges are left; done at 05:37; pressure control off (05:48). |
| [06:13](https://www.youtube.com/embed/9kn-HhXCr1o?start=373) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=373s) | during/heating | Purging again at 250 °C; next raise to 500 °C after this purge (or via pressure control later). |
| [06:41](https://www.youtube.com/embed/9kn-HhXCr1o?start=401) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=401s) | theory | Change pressure only while far from melting; once fully liquid, don't change pressure. |
| [07:10](https://www.youtube.com/embed/9kn-HhXCr1o?start=430) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=430s) | during/heating | 500 °C set; aluminium won't melt yet. |
| [08:15](https://www.youtube.com/embed/9kn-HhXCr1o?start=495) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=495s) | theory | Cycle: purge, 250 °C (drives out oxygen/moisture), purge, 500 °C, purge → ready to melt. |
| [08:41](https://www.youtube.com/embed/9kn-HhXCr1o?start=521) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=521s) | theory | No purge every 250 ° beyond that: the target is leftover moisture, not the melting point; after 500 °C go to working temp. |
| [10:43](https://www.youtube.com/embed/9kn-HhXCr1o?start=643) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=643s) | during | Furnace pressure barely different from the chamber but was enough last run; can control manually if needed. |
| [12:37](https://www.youtube.com/embed/9kn-HhXCr1o?start=757) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=757s) | during/heating | Pressure control on, raise temperature: 850 °C was enough last time (vs 800 or 1,000). |
| [12:59](https://www.youtube.com/embed/9kn-HhXCr1o?start=779) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=779s) | during | Oxygen content stabilises slowly. |
| [13:30](https://www.youtube.com/embed/9kn-HhXCr1o?start=810) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=810s) | theory | Melting cue: the temperature dips a bit as the metal liquefies and contacts the thermocouple. |
| [14:03](https://www.youtube.com/embed/9kn-HhXCr1o?start=843) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=843s) | theory | Second cue: faster beeping — induction draws more power as the melt pulls heat from the crucible. |
| [14:16](https://www.youtube.com/embed/9kn-HhXCr1o?start=856) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=856s) | theory | Melt doesn't fall until the sealing rod is opened; usually raise furnace pressure a little to give it a push. |
| [15:18](https://www.youtube.com/embed/9kn-HhXCr1o?start=918) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=918s) | during | Give it a small pressure push; can see it inside. |
| [15:42](https://www.youtube.com/embed/9kn-HhXCr1o?start=942) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=942s) | during/heating | Sealing rod is going down as the charge melts; reduce temperature back to 800 °C. |
| [15:57](https://www.youtube.com/embed/9kn-HhXCr1o?start=957) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=957s) | during/heating | Melt keeps going, temperature drops; once all liquid wait ~2 min to overheat to the reading and to mix. |
| [16:25](https://www.youtube.com/embed/9kn-HhXCr1o?start=985) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=985s) | theory | Beeps are induction pulses; the magnetic field makes the melt jump in the middle. |
| [16:43](https://www.youtube.com/embed/9kn-HhXCr1o?start=1003) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1003s) | theory | More material mixes better; a tiny pool at the bottom doesn't really mix. |
| [17:05](https://www.youtube.com/embed/9kn-HhXCr1o?start=1025) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1025s) | during | The bar is gone; melt jumping; wait 2 minutes before opening the nozzle. |
| [17:50](https://www.youtube.com/embed/9kn-HhXCr1o?start=1070) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1070s) | during | Everything melted, no leftovers. |
| [18:03](https://www.youtube.com/embed/9kn-HhXCr1o?start=1083) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1083s) | theory | On-screen time = timer of the current status (melting vs pouring pressure). |
| [18:47](https://www.youtube.com/embed/9kn-HhXCr1o?start=1127) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1127s) | during | Water still 23 °C, fine; need only a tiny flow or everything overcools and condenses. |
| [19:34](https://www.youtube.com/embed/9kn-HhXCr1o?start=1174) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1174s) | during/atomizing | Start transducer cooling; parameters kept from last scan (rescan if not); start vibration. |
| [20:14](https://www.youtube.com/embed/9kn-HhXCr1o?start=1214) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1214s) | during/atomizing | Switch to pouring ("graining") pressure and open the sealing rod; recording. |
| [20:24](https://www.youtube.com/embed/9kn-HhXCr1o?start=1224) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1224s) | during/atomizing | Initial droplet usually lost; flow too high for this low amplitude; atomization very slow. |
| [20:51](https://www.youtube.com/embed/9kn-HhXCr1o?start=1251) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1251s) | lesson | A very thin stream or single droplets would atomize stably; "should go with 0.5 (nozzle) without any issue". |
| [21:07](https://www.youtube.com/embed/9kn-HhXCr1o?start=1267) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1267s) | troubleshooting | Good atomization on the top of the plate, but material gathers at the bottom and drips un-atomized. |
| [21:24](https://www.youtube.com/embed/9kn-HhXCr1o?start=1284) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1284s) | lesson | With the reverse booster you must know the material's parameters to have full control of the pour. |
| [21:39](https://www.youtube.com/embed/9kn-HhXCr1o?start=1299) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1299s) | after | Pour over: stop vibrations, sealing rod down, back to melting pressure, stop heating — as soon as done. |
| [22:05](https://www.youtube.com/embed/9kn-HhXCr1o?start=1325) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1325s) | theory | Light inside is a flow sensor, not arcing. |
| [22:23](https://www.youtube.com/embed/9kn-HhXCr1o?start=1343) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1343s) | troubleshooting | Had almost no overpressure yet the melt fell too quickly → go back to the smaller nozzle. |
| [22:59](https://www.youtube.com/embed/9kn-HhXCr1o?start=1379) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1379s) | theory | Reference: best well-controlled reverse-booster run ≈ 90% conversion of material to powder. |
| [23:59](https://www.youtube.com/embed/9kn-HhXCr1o?start=1439) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1439s) | theory | Reference video: very slow, just droplets, everything atomized, nothing wasted. |
| [24:12](https://www.youtube.com/embed/9kn-HhXCr1o?start=1452) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1452s) | theory | Ideal = slow drip or slow stream; a slow flow can be improved with turbo pressure; smaller-nozzle risk: nothing pours. |
| [24:39](https://www.youtube.com/embed/9kn-HhXCr1o?start=1479) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1479s) | theory | Fine powder recipe: very small nozzle + very low amplitude (reverse booster) + slow, controlled pouring. |
| [25:08](https://www.youtube.com/embed/9kn-HhXCr1o?start=1508) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1508s) | theory | Only differential pressure matters; too little furnace pressure → splatter instead of a stream. |
| [25:42](https://www.youtube.com/embed/9kn-HhXCr1o?start=1542) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1542s) | theory | Process is short anyway; 2 vs 5 minutes changes little. |
| [26:45](https://www.youtube.com/embed/9kn-HhXCr1o?start=1605) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1605s) | theory | High amplitude = faster process, larger particles. |
| [27:16](https://www.youtube.com/embed/9kn-HhXCr1o?start=1636) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1636s) | material | The rod just run is aluminium 6063 (BYU's own rod, inferred). |
| [27:39](https://www.youtube.com/embed/9kn-HhXCr1o?start=1659) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1659s) | lesson | For smaller particles swap to the 0.5 nozzle; most Al alloys don't like 0.5, but here the flow was too good. |
| [28:05](https://www.youtube.com/embed/9kn-HhXCr1o?start=1685) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1685s) | result | Some material wasted but samples exist for max, min and smallest-particle options. |
| [29:05](https://www.youtube.com/embed/9kn-HhXCr1o?start=1745) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1745s) | lesson | Recommended charge 250–300 g: small samples are gone before you tune; a full crucible may kill the plate. |
| [29:56](https://www.youtube.com/embed/9kn-HhXCr1o?start=1796) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1796s) | after/cleaning | Light clean only: open, brush, take the powder out. |
| [30:20](https://www.youtube.com/embed/9kn-HhXCr1o?start=1820) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1820s) | troubleshooting | Nozzle likely has solidified metal to remove by hand after cooling; new charge may not re-melt it → disassemble. |
| [32:33](https://www.youtube.com/embed/9kn-HhXCr1o?start=1953) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1953s) | theory | Consumables tour begins ("definitely record this"). |
| [33:04](https://www.youtube.com/embed/9kn-HhXCr1o?start=1984) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=1984s) | part | Insulation: plenty of spares; blue type rated higher temp, denser, less dust — for silver/gold or high purity. |
| [33:45](https://www.youtube.com/embed/9kn-HhXCr1o?start=2025) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2025s) | part | Nozzle holders break if dropped; overtightening cracks the thread; many spares. |
| [33:58](https://www.youtube.com/embed/9kn-HhXCr1o?start=2038) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2038s) | part | Sealing rods: normal, plus ones with a hole for a thermocouple reading the furnace centre; alumina cylinders for reactive materials. |
| [34:26](https://www.youtube.com/embed/9kn-HhXCr1o?start=2066) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2066s) | part | Graphite nuts (costly, only break if dropped); graphite seals wear and crack; graphite and boron-nitride nozzles. |
| [34:56](https://www.youtube.com/embed/9kn-HhXCr1o?start=2096) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2096s) | part | BN nozzles for more reactive melts (e.g. Al with calcium) — flows more smoothly. |
| [35:18](https://www.youtube.com/embed/9kn-HhXCr1o?start=2118) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2118s) | part | Thermocouple covers: standard and long (for the sealing-rod thermocouple); two spare thermocouples; extra plug, dual measurement possible. |
| [36:21](https://www.youtube.com/embed/9kn-HhXCr1o?start=2181) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2181s) | part | Furnace seals wear; back filters — replace if overpressure is hard to release; ultrasonic-bath cleaning. |
| [36:58](https://www.youtube.com/embed/9kn-HhXCr1o?start=2218) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2218s) | part | Spare viewport glass and its seal — droplets can hit the glass during maintenance. |
| [37:25](https://www.youtube.com/embed/9kn-HhXCr1o?start=2245) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2245s) | part | Spare prolonger, top sonotrodes, connectors; crucibles and side insulation (second layer underneath). |
| [37:40](https://www.youtube.com/embed/9kn-HhXCr1o?start=2260) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2260s) | part | Filters inside the blue cabinet, right side, between chamber and vacuum pump; check every 1–2 months. |
| [38:35](https://www.youtube.com/embed/9kn-HhXCr1o?start=2315) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2315s) | part | Plates: carbon fibre uncoated (aluminium), large CF (unstable stream), CF with Mo tip (copper wetting), CF plasma-coated W (Cu alloys, survives anything). |
| [39:48](https://www.youtube.com/embed/9kn-HhXCr1o?start=2388) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2388s) | part | Ti64 plates vibrate well but break above ~800 °C (phase change); niobium for higher temp but cracks at high amplitude. |
| [40:48](https://www.youtube.com/embed/9kn-HhXCr1o?start=2448) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2448s) | part | Molybdenum ("MLS" alloy) plates small/large: golden standard; may react with ~0.5 kg Al in long runs. |
| [41:28](https://www.youtube.com/embed/9kn-HhXCr1o?start=2488) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2488s) | part | Stainless plates: cheap, break in one process; for magnesium use Mo or Nb; medical → Nb (bio-approved). |
| [43:00](https://www.youtube.com/embed/9kn-HhXCr1o?start=2580) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2580s) | cleaning | Chamber brushes: get bigger anti-static ones. |
| [43:47](https://www.youtube.com/embed/9kn-HhXCr1o?start=2627) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2627s) | admin | Training certificate signed, one copy each. |
| [44:16](https://www.youtube.com/embed/9kn-HhXCr1o?start=2656) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2656s) | lesson | Keep practising right after Bartosz leaves; his 10.5 mm rod pours well. |
| [44:53](https://www.youtube.com/embed/9kn-HhXCr1o?start=2693) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2693s) | lesson | Parameters and equipment choice are the main factor; once established it's easy to repeat. |
| [45:12](https://www.youtube.com/embed/9kn-HhXCr1o?start=2712) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2712s) | lesson | Operator focus for 2–3 min of pouring: aim low amplitude, raise via slider if not atomizing; pulse turbo pressure to stabilise. |
| [46:11](https://www.youtube.com/embed/9kn-HhXCr1o?start=2771) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2771s) | after/cooldown | Below 100 °C shut down the cooling; vent the chamber before opening (inferred). |
| [46:33](https://www.youtube.com/embed/9kn-HhXCr1o?start=2793) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2793s) | part | Supplied tool for unscrewing the sealing rod. |
| [47:07](https://www.youtube.com/embed/9kn-HhXCr1o?start=2827) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2827s) | troubleshooting | Water on the floor is condensation — facility supply too cold; could shut it down now. |
| [47:40](https://www.youtube.com/embed/9kn-HhXCr1o?start=2860) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2860s) | theory | It's a heat exchanger, not a chiller; chilled water comes from the facility. |
| [48:00](https://www.youtube.com/embed/9kn-HhXCr1o?start=2880) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2880s) | future | Viewport argon upgrade for magnesium; extended consumables last months. |
| [48:36](https://www.youtube.com/embed/9kn-HhXCr1o?start=2916) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2916s) | future | Pure copper is tough (Cu–Sn easier, evaporation, no visibility); semester plan: aluminium, maybe magnesium. |
| [49:25](https://www.youtube.com/embed/9kn-HhXCr1o?start=2965) | [▶](https://www.youtube.com/watch?v=9kn-HhXCr1o&t=2965s) | admin | Support via WhatsApp with photos; everyone added to the database system. |

## The expert cleaning the atomizer, pov
`u-KjR5TENN4` · 2026-09-30 · 18:45 · public · transcript: auto · [open paused](https://www.youtube.com/embed/u-KjR5TENN4?start=0) · [▶ watch](https://www.youtube.com/watch?v=u-KjR5TENN4)

_No caption-derived rows yet (no YouTube auto-captions for this video; waiting on the Whisper transcript)._

## Cartridge cleaning
`f8KL31PN8bA` · 2026-09-30 · 18:09 · public · transcript: whisper · [open paused](https://www.youtube.com/embed/f8KL31PN8bA?start=0) · [▶ watch](https://www.youtube.com/watch?v=f8KL31PN8bA)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:09](https://www.youtube.com/embed/f8KL31PN8bA?start=9) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=9s) | after/cleaning | "It's just cleaning up" — post-run clean-up of the cartridge parts at the bench, respirator and orange gloves on (keyframe). |
| [00:45](https://www.youtube.com/embed/f8KL31PN8bA?start=45) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=45s) | after/cleaning | Something "comes down a little bit and stabilizes" (reading not named; start of a merged 00:45–06:53 segment). |
| [00:45](https://www.youtube.com/embed/f8KL31PN8bA?start=45) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=45s) | after/cleaning | Thorough option: unscrew the plug, take the handle, open the valve fully "to get like a perfect access to the inside of the valve". |
| [00:45](https://www.youtube.com/embed/f8KL31PN8bA?start=45) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=45s) | lesson | If the next material is similar, just clean the inside; even without opening, put paper in and move it around with tweezers. |
| [06:53](https://www.youtube.com/embed/f8KL31PN8bA?start=413) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=413s) | after/cleaning | "Flush it a few times with isopropanol and it will be fine"; then put it back in the same place. |
| [06:53](https://www.youtube.com/embed/f8KL31PN8bA?start=413) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=413s) | after/cleaning | Use compressed air to blow paper-towel dust off the seal; the lint sticks to the seal. |
| [06:53](https://www.youtube.com/embed/f8KL31PN8bA?start=413) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=413s) | tools | Trainee asks about a separate compressed-air gun; Bartosz: put a T on the machine's air line and use this one, "somewhere in the corner". |
| [08:57](https://www.youtube.com/embed/f8KL31PN8bA?start=537) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=537s) | after/cleaning | Refit: "find the spot where it is supposed to sit"; remark that it "definitely got hotter in here". |
| [08:57](https://www.youtube.com/embed/f8KL31PN8bA?start=537) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=537s) | after/cleaning | "Everything is here, so it's just a pit stop and we start the process"; vacuum not needed — wiping suffices, vacuum for a better clean. |
| [12:32](https://www.youtube.com/embed/f8KL31PN8bA?start=752) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=752s) | lesson | Deeper cleaning deferred ("later sounds fine") because "we're just doing aluminum again". |
| [12:59](https://www.youtube.com/embed/f8KL31PN8bA?start=779) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=779s) | troubleshooting | Scan graph at the HMI (keyframe): "something is a little bit off" — a sign of a second peak causing resonance when the plate works. |
| [12:59](https://www.youtube.com/embed/f8KL31PN8bA?start=779) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=779s) | troubleshooting | Plate is more sensitive and "can go up, then it stabilizes"; "fortunately, it's not breaking", it just heats up more. |
| [13:37](https://www.youtube.com/embed/f8KL31PN8bA?start=817) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=817s) | theory | More heat gives faster atomization but is "a rather rough style"; 1:1 booster with the wider plate has a higher chance of resonance. |
| [13:37](https://www.youtube.com/embed/f8KL31PN8bA?start=817) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=817s) | theory | With the reverse booster the resonance will disappear; "the ultrasonics are quite unpredictable". |
| [14:05](https://www.youtube.com/embed/f8KL31PN8bA?start=845) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=845s) | theory | "We will try our best to have some kind of control over them"; recommends a resonator website (heard "pushasonicresonators.org") for reading. |
| [14:31](https://www.youtube.com/embed/f8KL31PN8bA?start=871) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=871s) | theory | Tightening the piezo ceramic stacks raises stability "into infinity" in theory, but past some point they crack — hence the care with the stack. |
| [15:01](https://www.youtube.com/embed/f8KL31PN8bA?start=901) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=901s) | theory | "Theoretically you should compress them as much as you want, but when you're actually doing it, it's not going to work." |
| [15:01](https://www.youtube.com/embed/f8KL31PN8bA?start=901) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=901s) | safety | Trainee: comfortable without the full-face mask once no powder is around? Bartosz: wear it for the cleaning after the trials, then it's fine. |
| [15:01](https://www.youtube.com/embed/f8KL31PN8bA?start=901) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=901s) | housekeeping | All the consumables are best stored in some kind of cabinet. |
| [15:27](https://www.youtube.com/embed/f8KL31PN8bA?start=927) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=927s) | housekeeping | Keep the area clean: from time to time vacuum everything and wipe; small powder residues come from jarring powder out of the container. |
| [15:27](https://www.youtube.com/embed/f8KL31PN8bA?start=927) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=927s) | housekeeping | Trainee: a cabinet dry box with desiccant to keep things drier; "we might pull in that big metal one" (cabinet, inferred). |
| [15:57](https://www.youtube.com/embed/f8KL31PN8bA?start=957) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=957s) | before | Sample cup: keep it upright, plug at the top; filled "pretty much up to the top of this little cap"; furnace lid open (keyframe). |
| [16:50](https://www.youtube.com/embed/f8KL31PN8bA?start=1010) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=1010s) | before | Filled with AlSi10Mg; a little hole in the top so air can come out — "who knows? We'll just need to test it". |
| [16:50](https://www.youtube.com/embed/f8KL31PN8bA?start=1010) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=1010s) | before | Plan: another one the same way if time allows; Bartosz will also show how to reverse the booster "to show you the principles". |
| [17:19](https://www.youtube.com/embed/f8KL31PN8bA?start=1039) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=1039s) | chatter | Trainee has somewhere to be and a class to teach; the run will "probably take about an hour". |
| [17:54](https://www.youtube.com/embed/f8KL31PN8bA?start=1074) | [▶](https://www.youtube.com/watch?v=f8KL31PN8bA&t=1074s) | chatter | "Oh, did I leave it? Oh, no. I thought I left it, didn't I?" — looking for a misplaced item. |

## Atomizer training (sterling's phone)
`2wMgeI-E7zw` · 2026-09-30 · 15:58 · public · transcript: auto · [open paused](https://www.youtube.com/embed/2wMgeI-E7zw?start=0) · [▶ watch](https://www.youtube.com/watch?v=2wMgeI-E7zw)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:05](https://www.youtube.com/embed/2wMgeI-E7zw?start=5) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=5s) | before/setup | Rear connections: main power plug; vacuum pump socket; lower port feeds the heat exchanger on the other side. |
| [00:23](https://www.youtube.com/embed/2wMgeI-E7zw?start=23) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=23s) | before/setup | Argon arrives via a T into two lines; one blue line is compressed air; two cooling hoses (supply/return) to the heat exchanger. |
| [00:46](https://www.youtube.com/embed/2wMgeI-E7zw?start=46) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=46s) | before/setup | Heat exchanger fed from the facility pipe; facility water is really cold; lines to be insulated against condensation. |
| [01:04](https://www.youtube.com/embed/2wMgeI-E7zw?start=64) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=64s) | troubleshooting | Open the facility valve only a very little; cold water tripped "water too cold" — threshold 10 °C, reading 9.3, lowered to 7 °C. |
| [01:28](https://www.youtube.com/embed/2wMgeI-E7zw?start=88) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=88s) | before/setup | Keep the valve barely open, watch the exchanger water temperature rise under load, adjust. |
| [01:45](https://www.youtube.com/embed/2wMgeI-E7zw?start=105) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=105s) | theory | Heat exchanger: coolant tank with level sensor; stops on low level or high temperature; main switch starts inverter and pump; pressure gauge. |
| [02:29](https://www.youtube.com/embed/2wMgeI-E7zw?start=149) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=149s) | before/setup | "Cooling water too low" error on the main screen clears after a short delay; check in service mode (~10 flowing). |
| [02:55](https://www.youtube.com/embed/2wMgeI-E7zw?start=175) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=175s) | lesson | Exchanger panel is loud; the side panel can come off to add insulation inside. |
| [03:27](https://www.youtube.com/embed/2wMgeI-E7zw?start=207) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=207s) | theory | Main switch; one panel controls the furnace (pressure and temperature); the other controls the ultrasonic system and chamber. |
| [03:45](https://www.youtube.com/embed/2wMgeI-E7zw?start=225) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=225s) | theory | Software has user accounts (account manager, simple default passwords); one program tests vibrations, another runs the system. |
| [04:29](https://www.youtube.com/embed/2wMgeI-E7zw?start=269) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=269s) | admin | Mixed schedules; mornings cover more; keep notes on consumables and modifications. |
| [04:53](https://www.youtube.com/embed/2wMgeI-E7zw?start=293) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=293s) | future | For Al–Mg alloys with more magnesium there is an upgrade: viewport with argon purge to keep visibility. |
| [05:21](https://www.youtube.com/embed/2wMgeI-E7zw?start=321) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=321s) | admin | Order was priced with a chiller rather than a heat exchanger → credit for extra consumables/parts; lots of crucibles. |
| [06:02](https://www.youtube.com/embed/2wMgeI-E7zw?start=362) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=362s) | before/loading | Bartosz brought aluminium 4047 rods for basic training; will show how to control particle size. |
| [06:16](https://www.youtube.com/embed/2wMgeI-E7zw?start=376) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=376s) | theory | Changing parts drastically changes the PSD; not every combination suits every alloy; tricks for Al large vs small. |
| [06:49](https://www.youtube.com/embed/2wMgeI-E7zw?start=409) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=409s) | theory | Lower density → larger particles; you cannot resist that. |
| [06:57](https://www.youtube.com/embed/2wMgeI-E7zw?start=417) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=417s) | troubleshooting | Water on the floor is from setup; unit can't be moved back — hoses too stiff; longer hoses/angle fitting. |
| [07:29](https://www.youtube.com/embed/2wMgeI-E7zw?start=449) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=449s) | part | The transducer is the core; compressed-air cooling connects here; thread mismatch solved with Teflon tape/hardware store fitting. |
| [08:03](https://www.youtube.com/embed/2wMgeI-E7zw?start=483) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=483s) | theory | Maximise compressed-air flow to keep the transducer cold; plasma runs for hours, atomizing only a couple of minutes. |
| [08:28](https://www.youtube.com/embed/2wMgeI-E7zw?start=508) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=508s) | safety | Don't drop the transducer; keep it away from moisture. |
| [08:41](https://www.youtube.com/embed/2wMgeI-E7zw?start=521) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=521s) | before/setup | Stack: one rod (sonotrode), then the plate, then the final rod that holds the plate in position. |
| [08:51](https://www.youtube.com/embed/2wMgeI-E7zw?start=531) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=531s) | lesson | Plate is a consumable: one process or a few; if it breaks, open the chamber and change it; a cracked plate may not run twice. |
| [09:17](https://www.youtube.com/embed/2wMgeI-E7zw?start=557) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=557s) | safety | If a plate breaks, the ceramic crucible under it catches molten metal. |
| [09:33](https://www.youtube.com/embed/2wMgeI-E7zw?start=573) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=573s) | cost | Plates cost $10–12 up to $70–80 (tungsten plasma-coated carbon fibre from Korea). |
| [10:07](https://www.youtube.com/embed/2wMgeI-E7zw?start=607) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=607s) | theory | Aiming for smaller particles means lower amplitude, so plates last longer. |
| [10:34](https://www.youtube.com/embed/2wMgeI-E7zw?start=634) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=634s) | lesson | Coat crucibles with boron-nitride spray for reactive materials; yttria also possible; BN most flexible; US suppliers exist. |
| [11:37](https://www.youtube.com/embed/2wMgeI-E7zw?start=697) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=697s) | cleaning | Switching alloys: after a run peel the slag off the crucible bottom; micro leftovers on walls don't matter. |
| [12:09](https://www.youtube.com/embed/2wMgeI-E7zw?start=729) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=729s) | cleaning | Sealing rods: peel slag, polish; as long as the tip is smooth it works. |
| [12:25](https://www.youtube.com/embed/2wMgeI-E7zw?start=745) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=745s) | part | Extended pack extras: splash cover for spitting materials; denser high-temperature insulation for purity. |
| [13:02](https://www.youtube.com/embed/2wMgeI-E7zw?start=782) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=782s) | safety | Two full masks, ear protection (ultrasonic), filters; the induction coil is also noisy. |
| [13:48](https://www.youtube.com/embed/2wMgeI-E7zw?start=828) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=828s) | before/loading | BYU test rods: bored hole, powder loaded, capped — to try Wednesday; arc melting as fallback. |
| [14:27](https://www.youtube.com/embed/2wMgeI-E7zw?start=867) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=867s) | lesson | Any consolidation helps; pure powder has a higher chance of just getting lost. |
| [14:53](https://www.youtube.com/embed/2wMgeI-E7zw?start=893) | [▶](https://www.youtube.com/watch?v=2wMgeI-E7zw&t=893s) | admin | 8:30 a.m. start tomorrow; use the vacuum during runs; parking (to end). |

## nzyjn0 atomization AlSi10Mg-Al6063
`TFpU4uqVF9c` · 2026-09-30 · 20:56 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/TFpU4uqVF9c?start=0) · [▶ watch](https://www.youtube.com/watch?v=TFpU4uqVF9c)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:05](https://www.youtube.com/embed/TFpU4uqVF9c?start=5) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=5s) | pump-down | Furnace "at around 270" (°C, inferred); "making five gas washes, so vacuum and filling with protective gas". |
| [00:16](https://www.youtube.com/embed/TFpU4uqVF9c?start=16) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=16s) | pump-down | "At the end of the cycle we need to use the melting pressure to create the overpressure in the furnace." |
| [01:37](https://www.youtube.com/embed/TFpU4uqVF9c?start=97) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=97s) | pump-down | Presses "melting pressure". |
| [01:40](https://www.youtube.com/embed/TFpU4uqVF9c?start=100) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=100s) | pump-down | "Now let's vacuum the chamber." |
| [02:45](https://www.youtube.com/embed/TFpU4uqVF9c?start=165) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=165s) | pump-down | Pump down "as much as we are able to", then backfill with protective gas (argon) (inferred). |
| [02:58](https://www.youtube.com/embed/TFpU4uqVF9c?start=178) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=178s) | pump-down | "And again" — next wash cycle. |
| [04:03](https://www.youtube.com/embed/TFpU4uqVF9c?start=243) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=243s) | heating | "After filling the chamber with protective gas again, let's go to higher temperature." |
| [04:53](https://www.youtube.com/embed/TFpU4uqVF9c?start=293) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=293s) | pump-down | "And now, again" — another wash at the higher temperature. |
| [09:48](https://www.youtube.com/embed/TFpU4uqVF9c?start=588) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=588s) | pump-down | "10. Final one." — last wash cycle (the "10" may be a cycle count; unclear). |
| [10:06](https://www.youtube.com/embed/TFpU4uqVF9c?start=606) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=606s) | heating | "Oxygen level is low. Everything stable. Now we can raise the temperature." |
| [10:26](https://www.youtube.com/embed/TFpU4uqVF9c?start=626) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=626s) | heating | "Start with slightly higher temperature to help homogenize the material" (mixed powder/cup charge). |
| [14:51](https://www.youtube.com/embed/TFpU4uqVF9c?start=891) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=891s) | heating | "Mostly homogenized, but I still see something on one side, some leftover. Let's give it a moment." |
| [15:55](https://www.youtube.com/embed/TFpU4uqVF9c?start=955) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=955s) | heating | Slight lack of homogenization on one side; "visibly thicker layer of oxide". |
| [16:24](https://www.youtube.com/embed/TFpU4uqVF9c?start=984) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=984s) | heating | Raises temperature "just a little bit more" to help. |
| [16:35](https://www.youtube.com/embed/TFpU4uqVF9c?start=995) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=995s) | heating | "Seems much better. But there is still something left." |
| [17:17](https://www.youtube.com/embed/TFpU4uqVF9c?start=1037) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=1037s) | heating | Decision: "try to pour it and see what will stay"; lower the temperature "to around 800°". |
| [19:14](https://www.youtube.com/embed/TFpU4uqVF9c?start=1154) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=1154s) | atomizing | Uses "parameters of low draining pressure that I have used yesterday"; controls mostly via pressure control. |
| [19:27](https://www.youtube.com/embed/TFpU4uqVF9c?start=1167) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=1167s) | atomizing | "Just barely anything. There's also little material. That's why manual control would be better." |
| [19:40](https://www.youtube.com/embed/TFpU4uqVF9c?start=1180) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=1180s) | atomizing | "Vibrations on" (ultrasonic generator started). |
| [20:28](https://www.youtube.com/embed/TFpU4uqVF9c?start=1228) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=1228s) | after | "It was fast. It was everything." — pour complete in under a minute. |
| [20:36](https://www.youtube.com/embed/TFpU4uqVF9c?start=1236) | [▶](https://www.youtube.com/watch?v=TFpU4uqVF9c&t=1236s) | after | "Melting pressure signal down and generator stop." |

## nzyjn0 AlSi10Mg-Al6063 dosing session
`prj_xgeuQtM` · 2026-09-29 · 1:08:45 · public · transcript: auto · [open paused](https://www.youtube.com/embed/prj_xgeuQtM?start=0) · [▶ watch](https://www.youtube.com/watch?v=prj_xgeuQtM)

_No caption-derived rows yet (no YouTube auto-captions for this video; waiting on the Whisper transcript)._

## Dosing Al 4047 powder
`QXSj0j1OqL8` · 2026-10-01 · 22:15 · public · transcript: auto · [open paused](https://www.youtube.com/embed/QXSj0j1OqL8?start=0) · [▶ watch](https://www.youtube.com/watch?v=QXSj0j1OqL8)

_No caption-derived rows yet (no YouTube auto-captions for this video; waiting on the Whisper transcript)._

## Atomizer Fri Oct 2 pt1
`qYyT39D5Yzo` · 2026-10-02 · 21:39 · public · transcript: auto · [open paused](https://www.youtube.com/embed/qYyT39D5Yzo?start=0) · [▶ watch](https://www.youtube.com/watch?v=qYyT39D5Yzo)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:09](https://www.youtube.com/embed/qYyT39D5Yzo?start=9) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=9s) | setup | Narrator starts the atomizer run; turns on "this guy" and the air. |
| [00:41](https://www.youtube.com/embed/qYyT39D5Yzo?start=41) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=41s) | setup / problem | "The water's still leaking from... this guy here. I forgot to tighten that a little more." |
| [00:53](https://www.youtube.com/embed/qYyT39D5Yzo?start=53) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=53s) | setup | Turn on the compressed air. |
| [01:26](https://www.youtube.com/embed/qYyT39D5Yzo?start=86) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=86s) | setup | Startup checklist: check oil, check water level, argon set to 8 bar, open chilled water lines (~20°), press air valve. |
| [01:46](https://www.youtube.com/embed/qYyT39D5Yzo?start=106) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=106s) | prep | Plan: use a molybdenum plate this run; nothing currently installed ("nothing's on here"). |
| [02:24](https://www.youtube.com/embed/qYyT39D5Yzo?start=144) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=144s) | prep / lesson | Cannot identify plates; "have to go back and find the video"; "I'm going to mark these so we don't forget." |
| [03:01](https://www.youtube.com/embed/qYyT39D5Yzo?start=181) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=181s) | chatter | Ronnie arrives: "You ready to do some science?" |
| [03:36](https://www.youtube.com/embed/qYyT39D5Yzo?start=216) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=216s) | prep | Plate ID: "probably molybdenum-dipped carbon fibre... feel how light they are"; "MO is molybdenum"; others "just the Mo". |
| [04:16](https://www.youtube.com/embed/qYyT39D5Yzo?start=256) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=256s) | prep | Another plate material "right next to molybdenum on the periodic table... NB" — niobium (inferred). |
| [05:06](https://www.youtube.com/embed/qYyT39D5Yzo?start=306) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=306s) | prep | "So these ones are just carbon fibre, right? I don't know what makes these different." |
| [05:20](https://www.youtube.com/embed/qYyT39D5Yzo?start=320) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=320s) | prep | Set includes big carbon fibre, stainless steel, big molybdenum; choose Mo: "gold standard. We get smaller particles." |
| [05:52](https://www.youtube.com/embed/qYyT39D5Yzo?start=352) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=352s) | tools | Borrowed tools from the "PSC" (project support centre?); must return later; "we need to order some tools." |
| [06:21](https://www.youtube.com/embed/qYyT39D5Yzo?start=381) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=381s) | cleaning | Need something to clean "this thing" after the run. |
| [06:33](https://www.youtube.com/embed/qYyT39D5Yzo?start=393) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=393s) | cleaning / lesson | Aluminum residue not coming off a part; "didn't know how dingable this is"; "it's tungsten... a tungsten alloy." |
| [06:49](https://www.youtube.com/embed/qYyT39D5Yzo?start=409) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=409s) | cleaning | "The shape of this is very important" — the deposit "grew from the last run to the one we just did"; remove carefully, maybe with a file. |
| [07:24](https://www.youtube.com/embed/qYyT39D5Yzo?start=444) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=444s) | setup | Power on by pressing the button; "that green light just came on." |
| [07:38](https://www.youtube.com/embed/qYyT39D5Yzo?start=458) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=458s) | loading | Attach "the upper sonotrode... he called it like protruding sono[trode]... the extending sonotrode." |
| [07:56](https://www.youtube.com/embed/qYyT39D5Yzo?start=476) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=476s) | tools | Small wrenches were returned; toolbox Allen keys are imperial only; need metric 17 and 18. |
| [09:17](https://www.youtube.com/embed/qYyT39D5Yzo?start=557) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=557s) | tools | Ronnie sent to fetch wrenches 18 and 17 from the PSC. |
| [09:49](https://www.youtube.com/embed/qYyT39D5Yzo?start=589) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=589s) | prep | "That shouldn't be empty relatively... going to suck having to clean that out" (container? unclear). |
| [10:08](https://www.youtube.com/embed/qYyT39D5Yzo?start=608) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=608s) | loading | "Check the nozzle. Pretty sure I put a new one in there. Yep, there's light coming through." |
| [10:44](https://www.youtube.com/embed/qYyT39D5Yzo?start=644) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=644s) | loading | "Make sure it's set back in good." |
| [10:54](https://www.youtube.com/embed/qYyT39D5Yzo?start=654) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=654s) | setup | HMI is password protected; "Heat" selected (11:11). |
| [12:01](https://www.youtube.com/embed/qYyT39D5Yzo?start=721) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=721s) | setup | "That's not a nice noise... Don't want to press that." (unidentified alarm/button). |
| [14:15](https://www.youtube.com/embed/qYyT39D5Yzo?start=855) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=855s) | setup | Narrator reviews "the system SOP that I wrote down cuz it's kind of a little bit funky... making sure it's linear." |
| [14:42](https://www.youtube.com/embed/qYyT39D5Yzo?start=882) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=882s) | loading | Torque wrench "the 50 torque" already set; 17 mm wrench used. |
| [15:09](https://www.youtube.com/embed/qYyT39D5Yzo?start=909) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=909s) | loading | "This will go on this part here"; "this whole thing turns" (16:00). |
| [16:08](https://www.youtube.com/embed/qYyT39D5Yzo?start=968) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=968s) | loading / lesson | "We should also put the housing over this too" — four screws; skipped: "let's not worry about it this time." |
| [17:02](https://www.youtube.com/embed/qYyT39D5Yzo?start=1022) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=1022s) | lesson | "But we should, to protect this expensive... transducer." |
| [17:21](https://www.youtube.com/embed/qYyT39D5Yzo?start=1041) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=1041s) | loading | "Shut those three things on there" (chamber latches, inferred). |
| [17:29](https://www.youtube.com/embed/qYyT39D5Yzo?start=1049) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=1049s) | pump-down | Reading SOP: "After purging at 500... press protective gas... that'll allow air into the chamber. Start by pressing purging." |
| [18:44](https://www.youtube.com/embed/qYyT39D5Yzo?start=1124) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=1124s) | loading | "Are you ready for the .5 mm?" — 0.5 mm nozzle (inferred); "we'll just be doing that crucible." |
| [20:00](https://www.youtube.com/embed/qYyT39D5Yzo?start=1200) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=1200s) | check / lesson | "We need to test this... Can we open this back up?" — chamber reopened for the test. |
| [20:50](https://www.youtube.com/embed/qYyT39D5Yzo?start=1250) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=1250s) | check | Frequency scan: "He said there should only be one valley, one peak. So I think that's good." |
| [21:09](https://www.youtube.com/embed/qYyT39D5Yzo?start=1269) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=1269s) | check | "Power zero watts." |
| [21:13](https://www.youtube.com/embed/qYyT39D5Yzo?start=1273) | [▶](https://www.youtube.com/watch?v=qYyT39D5Yzo&t=1273s) | record | Takes a video inside the chamber: "Oh yeah, look at that." |

## Atomizer run Oct 2 part 2
`of5-LhkX_VQ` · 2026-10-02 · 30:18 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/of5-LhkX_VQ?start=0) · [▶ watch](https://www.youtube.com/watch?v=of5-LhkX_VQ)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [01:14](https://www.youtube.com/embed/of5-LhkX_VQ?start=74) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=74s) | setup | "Oh, good. It's working." |
| [01:25](https://www.youtube.com/embed/of5-LhkX_VQ?start=85) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=85s) | prep | Surface "already been wiped down... we can wipe it down again. I don't think that would hurt." |
| [01:55](https://www.youtube.com/embed/of5-LhkX_VQ?start=115) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=115s) | chatter | It is ~2:11 pm; a 2:30 meeting with Dr. Barrett is pushed to 3–3:15. |
| [02:25](https://www.youtube.com/embed/of5-LhkX_VQ?start=145) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=145s) | status | "Just figured out some kinks and are about to start purging period." |
| [03:00](https://www.youtube.com/embed/of5-LhkX_VQ?start=180) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=180s) | loading | "You locked it down"; charge orientation: "Just this way." |
| [03:15](https://www.youtube.com/embed/of5-LhkX_VQ?start=195) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=195s) | loading / lesson | Tweezers for a graphite part: "I really don't know how fragile graphite is... Bartosz made it sound like if you dropped it..." |
| [03:45](https://www.youtube.com/embed/of5-LhkX_VQ?start=225) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=225s) | loading / mistake | "I dropped it." (apparently survived; continues). |
| [03:58](https://www.youtube.com/embed/of5-LhkX_VQ?start=238) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=238s) | loading | "Sealing [rod] is down." |
| [04:03](https://www.youtube.com/embed/of5-LhkX_VQ?start=243) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=243s) | heating | "Set 250°." Green light on; "turn on pressure control" (04:16). |
| [04:23](https://www.youtube.com/embed/of5-LhkX_VQ?start=263) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=263s) | pump-down | "Now we're going to put some vacuum pump and gas wash." |
| [04:42](https://www.youtube.com/embed/of5-LhkX_VQ?start=282) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=282s) | pump-down | Sequence: vacuum here first, then at 250, then at 500; doing the first one "before we go temperature at all" — chamber at 30°. |
| [04:59](https://www.youtube.com/embed/of5-LhkX_VQ?start=299) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=299s) | pump-down | "One wash of the whole system at room temperature, then one at 250, then two washes at 500 if needed." |
| [05:22](https://www.youtube.com/embed/of5-LhkX_VQ?start=322) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=322s) | pump-down | How to know if needed: oxygen reading; "if it's like low 20s, he says that's good." |
| [05:54](https://www.youtube.com/embed/of5-LhkX_VQ?start=354) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=354s) | heating | "Heat." |
| [06:31](https://www.youtube.com/embed/of5-LhkX_VQ?start=391) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=391s) | pump-down | "Melting pressure." |
| [06:54](https://www.youtube.com/embed/of5-LhkX_VQ?start=414) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=414s) | panel | Two separate panel sections: one for the chamber, one for the furnace. |
| [07:19](https://www.youtube.com/embed/of5-LhkX_VQ?start=439) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=439s) | record | "We just put a date on that." |
| [08:01](https://www.youtube.com/embed/of5-LhkX_VQ?start=481) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=481s) | pump-down | "Now let's come back up with argon"; turn on "this guy"; "open these a little bit" (08:09). |
| [08:20](https://www.youtube.com/embed/of5-LhkX_VQ?start=500) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=500s) | setup | "Wait for cooling water flow [warning] to go off." |
| [08:46](https://www.youtube.com/embed/of5-LhkX_VQ?start=526) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=526s) | setup | "80 PSI. Dang, that's high." (gauge unidentified). |
| [09:05](https://www.youtube.com/embed/of5-LhkX_VQ?start=545) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=545s) | setup | "Generator start." |
| [09:24](https://www.youtube.com/embed/of5-LhkX_VQ?start=564) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=564s) | pump-down | "Once that gets up to 250°, then press vacuum pump and gas wash again." |
| [10:35](https://www.youtube.com/embed/of5-LhkX_VQ?start=635) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=635s) | pump-down | Button difference: "this does five cycles... five cycles per wash and only one cycle per [the other]." |
| [11:13](https://www.youtube.com/embed/of5-LhkX_VQ?start=673) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=673s) | pump-down | To wash: "just press gas wash. So vacuum pump, gas wash." |
| [11:50](https://www.youtube.com/embed/of5-LhkX_VQ?start=710) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=710s) | pump-down | "Melting pressure then press. Pressure control keeps this at 150 m[bar]. Going to turn that off so we can suck it out." |
| [12:11](https://www.youtube.com/embed/of5-LhkX_VQ?start=731) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=731s) | pump-down | Watch gauge go "all the way" down; then "turn off that" (12:50). |
| [13:06](https://www.youtube.com/embed/of5-LhkX_VQ?start=786) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=786s) | heating | Change temperature setpoint up to 500. |
| [13:18](https://www.youtube.com/embed/of5-LhkX_VQ?start=798) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=798s) | design | No keypad for exact setpoints; furnace is from a different company that "won't let them interface", so controls are separate. |
| [13:42](https://www.youtube.com/embed/of5-LhkX_VQ?start=822) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=822s) | design | "It should be really easy to do a single button that does this entire cycle." |
| [14:20](https://www.youtube.com/embed/of5-LhkX_VQ?start=860) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=860s) | pump-down | At 500: "press vacuum pump gas again." |
| [14:32](https://www.youtube.com/embed/of5-LhkX_VQ?start=872) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=872s) | plumbing | Identifying lines: chilled water lines ("really cold"); white hose is the argon into the tank (15:02). |
| [15:42](https://www.youtube.com/embed/of5-LhkX_VQ?start=942) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=942s) | chatter | "He said we could atomize gold and silver in this" — wedding-ring joke. |
| [16:31](https://www.youtube.com/embed/of5-LhkX_VQ?start=991) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=991s) | pump-down | "Turn on pressure control"; "this is going up" (16:59). |
| [17:50](https://www.youtube.com/embed/of5-LhkX_VQ?start=1070) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1070s) | check | Oxygen "in low 20s. So I think we're good. We don't have to do another purge cycle." |
| [18:21](https://www.youtube.com/embed/of5-LhkX_VQ?start=1101) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1101s) | record | "Just write down" readings; "with the mbar check" (19:15). |
| [19:25](https://www.youtube.com/embed/of5-LhkX_VQ?start=1165) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1165s) | heating | "We can bring this up to 800." |
| [19:33](https://www.youtube.com/embed/of5-LhkX_VQ?start=1173) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1173s) | heating / deviation | "He went to 850 and then brought it down to 800?" — can't remember why; "I'm going to set to 830." |
| [19:56](https://www.youtube.com/embed/of5-LhkX_VQ?start=1196) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1196s) | heating | "Hoping this is going to mix well. Starting to glow." |
| [20:12](https://www.youtube.com/embed/of5-LhkX_VQ?start=1212) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1212s) | chatter | Meta glasses livestream idea. |
| [21:56](https://www.youtube.com/embed/of5-LhkX_VQ?start=1316) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1316s) | heating | "Is it getting orange? Oh, yeah. I don't think it's melting just yet." |
| [22:15](https://www.youtube.com/embed/of5-LhkX_VQ?start=1335) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1335s) | charge | Plug ("cap") length: "point three something" per the GitHub issue; "didn't go hardly in at all" — maybe shorter is fine. |
| [23:04](https://www.youtube.com/embed/of5-LhkX_VQ?start=1384) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1384s) | charge | Purpose of the plugs: "apparently what we're doing could explode" (loose powder; inferred). |
| [23:17](https://www.youtube.com/embed/of5-LhkX_VQ?start=1397) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1397s) | atomizing | "Melting pressure 17. Guess we'll see if 17.17 bar is high enough. He kept turning it down." |
| [23:37](https://www.youtube.com/embed/of5-LhkX_VQ?start=1417) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1417s) | heating | "Hey, it's melting. Oh, it's gone. Definitely not a lot in there." |
| [23:54](https://www.youtube.com/embed/of5-LhkX_VQ?start=1434) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1434s) | heating | Powder "might be clumped up again... No, I think it's mixing" — induction stirs the melt. |
| [24:18](https://www.youtube.com/embed/of5-LhkX_VQ?start=1458) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1458s) | safety | Heat felt through the viewing window. |
| [24:27](https://www.youtube.com/embed/of5-LhkX_VQ?start=1467) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1467s) | heating | "Let that go for about 2 minutes" before atomizing. |
| [24:54](https://www.youtube.com/embed/of5-LhkX_VQ?start=1494) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1494s) | atomizing | Amplitude: 100 "might be too much... bring it to about 90"; knob reads "88 to 100... around 90". |
| [25:23](https://www.youtube.com/embed/of5-LhkX_VQ?start=1523) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1523s) | lesson | "We're going to have to create digital readouts" for the amplitude knob. |
| [25:38](https://www.youtube.com/embed/of5-LhkX_VQ?start=1538) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1538s) | heating | "830°." |
| [25:53](https://www.youtube.com/embed/of5-LhkX_VQ?start=1553) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1553s) | atomizing | "Check the plate. What plate is this?... aluminum. Not a coated carbon, just pure." |
| [26:25](https://www.youtube.com/embed/of5-LhkX_VQ?start=1585) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1585s) | atomizing | "Sealing rod, [draining] pressure, on." |
| [26:45](https://www.youtube.com/embed/of5-LhkX_VQ?start=1605) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1605s) | atomizing / problem | "Uh-oh. Please turn off the frequency. Holy dang, [they] are flying out of there." |
| [27:00](https://www.youtube.com/embed/of5-LhkX_VQ?start=1620) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1620s) | atomizing | "It's totally working... Is that all of it? Yep." "Most of it did not get atomized, unfortunately." |
| [27:26](https://www.youtube.com/embed/of5-LhkX_VQ?start=1646) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1646s) | lesson | "That was definitely too high. It should have been a lot lower." |
| [27:33](https://www.youtube.com/embed/of5-LhkX_VQ?start=1653) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1653s) | lesson | "The plate needed to be a lot closer so [it] had more time to run down it." |
| [27:41](https://www.youtube.com/embed/of5-LhkX_VQ?start=1661) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1661s) | after | Shutdown: once sealing rod [closed], generator stop, ultrasonic stop, cooler. |
| [27:59](https://www.youtube.com/embed/of5-LhkX_VQ?start=1679) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1679s) | after | Temperature "down to 250". |
| [28:07](https://www.youtube.com/embed/of5-LhkX_VQ?start=1687) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1687s) | after | "We got some... you can see a pile. A good amount." |
| [28:37](https://www.youtube.com/embed/of5-LhkX_VQ?start=1717) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1717s) | after | Wait until "400° up here", then open — "it'll cool a lot faster." |
| [28:52](https://www.youtube.com/embed/of5-LhkX_VQ?start=1732) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1732s) | theory | Graphite exposed to oxygen above 400–500° reacts; below 400° it is safe to expose. |
| [29:26](https://www.youtube.com/embed/of5-LhkX_VQ?start=1766) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1766s) | problem | Water dripping on a cord — not condensation: "this is leaking. We need to tighten that more." |
| [29:53](https://www.youtube.com/embed/of5-LhkX_VQ?start=1793) | [▶](https://www.youtube.com/watch?v=of5-LhkX_VQ&t=1793s) | after | "Our first atomizer run by ourselves. Woo!" |

## Claude ping for dosing Al 4047
`BxA7Z9Fliss` · 2026-10-01 · 10:48 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/BxA7Z9Fliss?start=0) · [▶ watch](https://www.youtube.com/watch?v=BxA7Z9Fliss)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:01](https://www.youtube.com/embed/BxA7Z9Fliss?start=1) | [▶](https://www.youtube.com/watch?v=BxA7Z9Fliss&t=1s) | prep (dosing) | On GitHub, "one of these pull requests I have where I can ping Claude... before I'd run another dosing." |
| [00:12](https://www.youtube.com/embed/BxA7Z9Fliss?start=12) | [▶](https://www.youtube.com/watch?v=BxA7Z9Fliss&t=12s) | prep (dosing) | "Just copy that prompt down here." |
| [02:54](https://www.youtube.com/embed/BxA7Z9Fliss?start=174) | [▶](https://www.youtube.com/watch?v=BxA7Z9Fliss&t=174s) | chatter | Waves to self in the reflection; camera workflows show reflections "or daytime goes to nighttime". |
| [05:42](https://www.youtube.com/embed/BxA7Z9Fliss?start=342) | [▶](https://www.youtube.com/watch?v=BxA7Z9Fliss&t=342s) | chatter | "Oh, almost forgot." (unspecified). |

## Claude ping and troubleshooting for dosing Al 4047
`dXRB7c6GeDw` · 2026-10-01 · 59:37 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/dXRB7c6GeDw?start=0) · [▶ watch](https://www.youtube.com/watch?v=dXRB7c6GeDw)

_No caption-derived rows yet (no YouTube auto-captions for this video; waiting on the Whisper transcript)._

## Drill press, number 70 bit, graphite nozzle
`LSQmxwmlTkQ` · 2026-09-30 · 4:14 · public · transcript: whisper · [open paused](https://www.youtube.com/embed/LSQmxwmlTkQ?start=0) · [▶ watch](https://www.youtube.com/watch?v=LSQmxwmlTkQ)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:00](https://www.youtube.com/embed/LSQmxwmlTkQ?start=0) | [▶](https://www.youtube.com/watch?v=LSQmxwmlTkQ&t=0s) | preparation | Only speech in the clip (single 0:00–4:13 segment): "Going still? Got another one." — a second nozzle to drill (inferred). |
| [00:00](https://www.youtube.com/embed/LSQmxwmlTkQ?start=0) | [▶](https://www.youtube.com/watch?v=LSQmxwmlTkQ&t=0s) | chatter | "Yeah, that's hard to…"; "I might have to run to class in a couple seconds, sorry." "Perfect. Okay, thank you." |

## Lathe turning aluminum crucibles for atomizer experiments
`z6rwmQW_3Vg` · 2026-09-26 · 1:35 · public · transcript: auto · [open paused](https://www.youtube.com/embed/z6rwmQW_3Vg?start=0) · [▶ watch](https://www.youtube.com/watch?v=z6rwmQW_3Vg)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:01](https://www.youtube.com/embed/z6rwmQW_3Vg?start=1) | [▶](https://www.youtube.com/watch?v=z6rwmQW_3Vg&t=1s) | prep | "Over our 2.75, should we cut this like 1/4 in more?" |
| [00:14](https://www.youtube.com/embed/z6rwmQW_3Vg?start=14) | [▶](https://www.youtube.com/watch?v=z6rwmQW_3Vg&t=14s) | prep | "1/4 in should be fine if you're confident in your turning abilities" — cut at 3 in (00:21). |
| [00:27](https://www.youtube.com/embed/z6rwmQW_3Vg?start=27) | [▶](https://www.youtube.com/watch?v=z6rwmQW_3Vg&t=27s) | prep | Plan: band-saw the pieces, drill the interior hole on the lathe, turn the plugs on the lathe (00:33). |
| [00:42](https://www.youtube.com/embed/z6rwmQW_3Vg?start=42) | [▶](https://www.youtube.com/watch?v=z6rwmQW_3Vg&t=42s) | prep | Cut done: three 3 in pieces plus one piece "about 1 and 3/8"; extra left to face the ends flat and exact. |
| [01:02](https://www.youtube.com/embed/z6rwmQW_3Vg?start=62) | [▶](https://www.youtube.com/watch?v=z6rwmQW_3Vg&t=62s) | prep | Centre drill "just a guide hole", then the 1/2 in drill (01:05). |
| [01:14](https://www.youtube.com/embed/z6rwmQW_3Vg?start=74) | [▶](https://www.youtube.com/watch?v=z6rwmQW_3Vg&t=74s) | prep | First piece faced both ends, "perfectly at 2.75 in"; two more to go. |
| [01:25](https://www.youtube.com/embed/z6rwmQW_3Vg?start=85) | [▶](https://www.youtube.com/watch?v=z6rwmQW_3Vg&t=85s) | prep | Putting in the 1/2 in drill bit. |

## Placing the Atomizer!!!
`07QOPRHIEvw` · 2026-09-03 · 1:26 · public · transcript: auto · [open paused](https://www.youtube.com/embed/07QOPRHIEvw?start=0) · [▶ watch](https://www.youtube.com/watch?v=07QOPRHIEvw)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:55](https://www.youtube.com/embed/07QOPRHIEvw?start=55) | [▶](https://www.youtube.com/watch?v=07QOPRHIEvw&t=55s) | installation | Atomizer and crate contents are in the enclosure; "cleaned up a little bit"; ready to be installed the rest of the way. |
| [01:08](https://www.youtube.com/embed/07QOPRHIEvw?start=68) | [▶](https://www.youtube.com/watch?v=07QOPRHIEvw&t=68s) | installation | Chilled water comes down from the top; argon runs "by that orange tape on the wall" with the tanks. |
| [01:18](https://www.youtube.com/embed/07QOPRHIEvw?start=78) | [▶](https://www.youtube.com/watch?v=07QOPRHIEvw&t=78s) | installation | "That should be it for installing this. Commission it in about 2 weeks." |

## Exciting Vertical Cloud Lab Construction Update!! Atomizer Will Be Installed Soon!
`Kv9DT3Vo0GE` · 2026-09-01 · 2:30 · public · transcript: auto · [open paused](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=0) · [▶ watch](https://www.youtube.com/watch?v=Kv9DT3Vo0GE)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:00](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=0) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=0s) | installation | Dehumidifier up top "with the filter gone"; pump next to it; venting going in. |
| [00:16](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=16) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=16s) | installation | Climbs ladder; big pipe hooked up; lights still hanging. |
| [00:31](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=31) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=31s) | installation | Lines overhead "are cold water or chilled water". |
| [00:43](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=43) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=43s) | installation | "Look how big this transformer is. This is the device that powers our atomizer." |
| [00:49](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=49) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=49s) | installation | Transformer too big for the planned spot "above there"; placed here instead; could put a tall table over it if heat allows (01:00). |
| [01:13](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=73) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=73s) | installation | Slats, vents, lights; electrical "should be done"; light switches not working yet (01:28). |
| [01:35](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=95) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=95s) | installation | Cabinets; big sink — narrator will drill holes and finish plumbing (01:44). |
| [01:48](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=108) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=108s) | installation | Second sink, probably the emergency [eyewash]; narrator wonders why not combined. |
| [02:05](https://www.youtube.com/embed/Kv9DT3Vo0GE?start=125) | [▶](https://www.youtube.com/watch?v=Kv9DT3Vo0GE&t=125s) | installation | Whiteboard space; "massive" breaker boxes — "look how big these breakers are" (02:18). |

## Vacuum test
`cKwQbKdE22Q` · 2026-09-08 · 2:37 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/cKwQbKdE22Q?start=0) · [▶ watch](https://www.youtube.com/watch?v=cKwQbKdE22Q)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:00](https://www.youtube.com/embed/cKwQbKdE22Q?start=0) | [▶](https://www.youtube.com/watch?v=cKwQbKdE22Q&t=0s) | test | "Add just a little bit of this powder... like this here." |
| [00:15](https://www.youtube.com/embed/cKwQbKdE22Q?start=15) | [▶](https://www.youtube.com/watch?v=cKwQbKdE22Q&t=15s) | test | Connect the hose/fitting; "we'll turn this on" (00:24). |
| [01:08](https://www.youtube.com/embed/cKwQbKdE22Q?start=68) | [▶](https://www.youtube.com/watch?v=cKwQbKdE22Q&t=68s) | test | "Let it run for 15 to 30 seconds to get all of the powder out of here." |
| [01:16](https://www.youtube.com/embed/cKwQbKdE22Q?start=76) | [▶](https://www.youtube.com/watch?v=cKwQbKdE22Q&t=76s) | test | "Now we just leave it like that." |
| [01:24](https://www.youtube.com/embed/cKwQbKdE22Q?start=84) | [▶](https://www.youtube.com/watch?v=cKwQbKdE22Q&t=84s) | test | Pour out / inspect: "I want to see how much powder." |
| [01:37](https://www.youtube.com/embed/cKwQbKdE22Q?start=97) | [▶](https://www.youtube.com/watch?v=cKwQbKdE22Q&t=97s) | result | "There's no visible powder in there... I mean, you can see it." |
| [02:09](https://www.youtube.com/embed/cKwQbKdE22Q?start=129) | [▶](https://www.youtube.com/watch?v=cKwQbKdE22Q&t=129s) | test | "All the way." (unclear); ends. |

## Dehumidifier troubleshooting
`w02MRlZhpNk` · 2026-09-29 · 2:58 · unlisted · transcript: auto · [open paused](https://www.youtube.com/embed/w02MRlZhpNk?start=0) · [▶ watch](https://www.youtube.com/watch?v=w02MRlZhpNk)

| mm:ss | ▶ | phase | what happens / what is said |
| --- | --- | --- | --- |
| [00:02](https://www.youtube.com/embed/w02MRlZhpNk?start=2) | [▶](https://www.youtube.com/watch?v=w02MRlZhpNk&t=2s) | troubleshooting | "Bajillion pipes... lots of power going all over the place." |
| [00:10](https://www.youtube.com/embed/w02MRlZhpNk?start=10) | [▶](https://www.youtube.com/watch?v=w02MRlZhpNk&t=10s) | troubleshooting | Dehumidifier: "the 24 volts shorted to each other. So that should be working." |
| [00:40](https://www.youtube.com/embed/w02MRlZhpNk?start=40) | [▶](https://www.youtube.com/watch?v=w02MRlZhpNk&t=40s) | troubleshooting | "I heard a click. That's good, I guess." |
| [00:46](https://www.youtube.com/embed/w02MRlZhpNk?start=46) | [▶](https://www.youtube.com/watch?v=w02MRlZhpNk&t=46s) | troubleshooting | The pump "doesn't look like anything's actually attached to it"; its point is to move water in and out. |
| [01:17](https://www.youtube.com/embed/w02MRlZhpNk?start=77) | [▶](https://www.youtube.com/watch?v=w02MRlZhpNk&t=77s) | troubleshooting | "Is the pump just not being used at all? Maybe." Two pairs of wires; "looks like it's just connected directly." |
| [01:43](https://www.youtube.com/embed/w02MRlZhpNk?start=103) | [▶](https://www.youtube.com/watch?v=w02MRlZhpNk&t=103s) | troubleshooting | "Why is it not on? ... I think the breaker got tripped." |
| [02:08](https://www.youtube.com/embed/w02MRlZhpNk?start=128) | [▶](https://www.youtube.com/watch?v=w02MRlZhpNk&t=128s) | troubleshooting | Clicks heard when turning the control; "I would have assumed that's the right way to turn it for dryer." |
| [02:43](https://www.youtube.com/embed/w02MRlZhpNk?start=163) | [▶](https://www.youtube.com/watch?v=w02MRlZhpNk&t=163s) | troubleshooting | Notes a line "going into the side"; goes back down (02:55). |
