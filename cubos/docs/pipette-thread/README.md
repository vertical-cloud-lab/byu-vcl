# The pipette thread, migrated from PR #171

GitHub cannot move a comment between issues — a comment is bound to the thread it
was posted on and no API relocates it. So the pipette discussion was **copied**
here verbatim, and the originals stay on
[PR #171](https://github.com/vertical-cloud-lab/byu-vcl/pull/171) as the untouched
record. Every entry below links back to its original.

**78 of 113 comments** on #171 are pipette work. What stayed
behind, and why, is at the bottom.

## Files

- [`01-tip-handling.md`](./01-tip-handling.md) — Tip handling arrives: tip racks, `pick_up_tip`, and why `mix` wanted gantry 149 · *2026-08-06 → 2026-08-26* · 21 comments
- [`02-tipped-hardware-runs.md`](./02-tipped-hardware-runs.md) — Tipped runs on hardware: the first live aspirate, and a plunger that only turned one way · *2026-08-27 → 2026-09-01* · 22 comments
- [`03-wiring-and-prior-art.md`](./03-wiring-and-prior-art.md) — The wiring hunt: the Cubware pin shift, the raw-step probe, and the science-jubilee prior art · *2026-09-08 → 2026-09-09* · 7 comments
- [`04-firmware-and-p20-gen2.md`](./04-firmware-and-p20-gen2.md) — Firmware, P20 GEN2 constants, and the TMC2209 that answers nothing · *2026-09-15 → 2026-09-18* · 22 comments
- [`05-narrowing-the-driver.md`](./05-narrowing-the-driver.md) — Narrowing to the driver: the LEDs, `DIAG`/`INDEX`, and two separate stepper systems · *2026-09-21* · 6 comments

## Chronological index

| # | when (UTC) | who | subject | |
|---|---|---|---|---|
| 1 | 2026-08-06 21:08 | @​benwhitney5463 | @claude write a protocol given these deck and gantry files. Note the first step should be moving to a park position so the pipette does not risk hitti | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5209135743) |
| 2 | 2026-08-07 00:13 | @​benwhitney5463 | @claude address the above comment | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5210219073) |
| 3 | 2026-08-07 00:13 | @​claude[bot] | Protocol written — but as measured, the pipette cannot reach any of the six vials | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5210223219) |
| 4 | 2026-08-08 00:53 | @​jarrettshupe | @claude I want to make the same protocol as the one above, but with a few changes. Here are the new files: j_config_1.yaml cub_xl_ben_pipette_capper.y | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5223680699) |
| 5 | 2026-08-08 00:54 | @​claude[bot] | Protocol written — `capper_decapper_tip_test_j1.yaml`, validated offline, 28/28 mock | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5223682486) |
| 6 | 2026-08-24 23:58 | @​benwhitney5463 | @claude add a vial rack to this deck file. take the dimensions and tip locations from the specs on CubXL docs. the position of the bottom-right tip is | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5403089570) |
| 7 | 2026-08-24 23:59 | @​claude[bot] | Tip rack added to `sterling_6vials_tiprack.yaml` from the CubXL docs spec — validated offline, committed | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5403092518) |
| 8 | 2026-08-25 00:40 | @​benwhitney5463 | @claude using that deck and gantry file, write a protocol based on this file capper_decapper_test.yaml name is pipette_test. You will need to change t | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5403396903) |
| 9 | 2026-08-25 00:40 | @​claude[bot] | `pipette_test.yaml` written — validate_setup PASS, 27/27 mock. And the `drop_z` answer is: leave it alone — no deck change needed | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5403401043) |
| 10 | 2026-08-25 23:39 | @​benwhitney5463 | @claude visibly, the gantry can move freely above all obstacles on the deck with a pipette tip attached (according to the gantry this is at z = 122).  | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418480213) |
| 11 | 2026-08-25 23:40 | @​claude[bot] | The answer is a formula, not a fixed number: `mix` always asks for gantry Z = safe_z + 35, because safe_z is a promise about the **tip end**, not the carriage | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418484459) |
| 12 | 2026-08-26 00:06 | @​benwhitney5463 | @claude run a protocol with these files: sterling_6vials_tiprack.yaml cub_xl_ben_pipette_capper.yaml pipette_test.yaml | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418717095) |
| 13 | 2026-08-26 00:07 | @​claude[bot] | **Claude encountered an error after 7m 41s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32913702719) | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418720200) |
| 14 | 2026-08-26 00:18 | @​benwhitney5463 | @claude try again, and if node.js is outdated, download the necessary updates. | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418807749) |
| 15 | 2026-08-26 00:19 | @​claude[bot] | **Claude encountered an error after 1s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32914558002) | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418810397) |
| 16 | 2026-08-26 00:27 | @​benwhitney5463 | @claude what is stopping you from connecting to the RPi5 | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418866769) |
| 17 | 2026-08-26 00:27 | @​claude[bot] | **Claude encountered an error after 1s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32915136461) | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5418869142) |
| 18 | 2026-08-26 17:48 | @​benwhitney5463 | @claude run a protocol with these files: sterling_6vials_tiprack.yaml cub_xl_ben_pipette_capper.yaml pipette_test.yaml | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5428960518) |
| 19 | 2026-08-26 17:48 | @​claude[bot] | **Claude encountered an error after 1s** —— [View job](https://github.com/vertical-cloud-lab/byu-vcl/actions/runs/32996181849) | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5428964937) |
| 20 | 2026-08-26 17:55 | @​benwhitney5463 | @claude run a protocol with these files: sterling_6vials_tiprack.yaml cub_xl_ben_pipette_capper.yaml pipette_test.yaml | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5429050592) |
| 21 | 2026-08-26 17:55 | @​claude[bot] | I couldn't run it — the runner has no route to the Pi since the Tailscale step was removed from `main` 2 h ago. Audited the trio offline instead, and it has two collision paths | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5429055892) |
| 22 | 2026-08-27 23:37 | @​benwhitney5463 | @claude run the following protocol: pipette_test.yaml cub_xl_ben_pipette_capper.yaml sterling_6vials_tiprack.yaml I changed the protocol so the pipett | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5446491357) |
| 23 | 2026-08-27 23:37 | @​claude[bot] | Ran it — steps 0–5 on hardware, **6/6 complete**. Your `height: -15.0` works: the tip goes 15 mm into vial_1. I stopped before `drop_tip` | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5446494084) |
| 24 | 2026-08-28 00:44 | @​benwhitney5463 | @claude here are the updated files I want you to run: ben_6vials_tiprack.yaml cub_xl_ben_pipette_capper.yaml pipette_test.yaml I recalibrated the mach | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5446958159) |
| 25 | 2026-08-28 00:45 | @​claude[bot] | I reached the Pi but did not run it — the controller's frame moved in the recalibration, and the deck file only followed on one axis | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5446959869) |
| 26 | 2026-08-28 01:05 | @​benwhitney5463 | @claude try again with the same deck and gantry file, but with this new protocol. The Pi should be online. pipette_test.yaml | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5447092637) |
| 27 | 2026-08-28 01:05 | @​claude[bot] | The file can't load — `instrumet:` — and with that typo fixed, the retract move you added *is* the shear. Corrected + verified, but the Pi is still offline | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5447094354) |
| 28 | 2026-08-31 17:24 | @​benwhitney5463 | @claude I implemented a few of your suggestions, and I updated the position of the tiprack on the deck (The coordinates I found were done with the pip | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5481959806) |
| 29 | 2026-08-31 17:24 | @​claude[bot] | Ran it — **18/18 steps, 4m 39s**. Your `aspirate`, `blowout` and `drop_tip` all executed on hardware for the first time | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5481964468) |
| 30 | 2026-08-31 17:59 | @​benwhitney5463 | @claude I will post a video of what happened shortly. In brief, it looked like the machine descended below the safe z when traveling by about 10mm. Wh | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5482357822) |
| 31 | 2026-08-31 17:59 | @​claude[bot] | Both symptoms and the plunger have concrete answers — and the two config changes you made push the wrong way | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5482360876) |
| 32 | 2026-08-31 18:41 | @​benwhitney5463 | @claude, here are the changes I made to the protocol files: ben_6vials_tiprack.yaml cub_xl_ben_pipette_capper.yaml pipette_test.yaml Please do commit  | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5482842278) |
| 33 | 2026-08-31 18:41 | @​claude[bot] | Patch applied, and the plunger is answered: **the stepper only turns one way** | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5482845374) |
| 34 | 2026-09-01 18:05 | @​benwhitney5463 | @claude I fixed the tip rack location, and I made the suggested edits on the protocol. Here's the trio I want you to run. I redid the wiring on the pi | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5498247245) |
| 35 | 2026-09-01 18:06 | @​claude[bot] | Ran it — **18/18 steps, 5m 50s, clean**. The plunger moved exactly twice, and I can tell you which twice | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5498250321) |
| 36 | 2026-09-01 18:33 | @​benwhitney5463 | @claude try it again with this shortened protocol: pipette_test.yaml | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5498574547) |
| 37 | 2026-09-01 18:33 | @​claude[bot] | Your rewiring **fixed the direction fault** — but `HOME` inverted with it, and that blocks the run at connect. No motion was commanded | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5498578842) |
| 38 | 2026-09-01 18:55 | @​benwhitney5463 | @claude I changed the wired to hopefully fix it. Try that protocol again. | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5498856358) |
| 39 | 2026-09-01 18:56 | @​claude[bot] | Ran it — **12/12 steps, 5m 16s**. Your rewiring kept the direction fix, and for the first time **every plunger command actuated**. But the limit switch still never asserts | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5498859855) |
| 40 | 2026-09-01 19:13 | @​benwhitney5463 | @claude I rewired it again, so try the protocol again. analyze this pin diagram:https://github.com/Ursa-Laboratories/Cubware/blob/main/documentation/o | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5499080008) |
| 41 | 2026-09-01 19:13 | @​claude[bot] | Ran it — **12/12, campaign 73**. And the diagram is wrong: every Arduino→TMC2209 signal wire is shifted one pin, and the firmware's ENABLE pin isn't connected to anything | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5499082972) |
| 42 | 2026-09-01 19:45 | @​benwhitney5463 | @claude I changed a few values in the protocol: pipette_test.yaml I also fixed the wired as you suggested. Try the run again. | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5499474060) |
| 43 | 2026-09-01 19:45 | @​claude[bot] | Ran it — **12/12, campaign 77**. And I owe you a correction: there is no plunger "direction fault". Both symptoms are one input pin, and I found the firmware line that proves it | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5499477489) |
| 44 | 2026-09-08 18:30 | @​benwhitney5463 | @claude, the pipette still isn't actuating anything, and I am wondering if it is a hardware or a software issue, or maybe it's both. The Arduino pins  | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5589942249) |
| 45 | 2026-09-08 18:30 | @​claude[bot] | Both — and the software half is new: correcting the UART pin opened a path that leaves the driver switched **off** | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5589945967) |
| 46 | 2026-09-08 21:17 | @​benwhitney5463 | @claude the Pi is plugged back in. Try running that trio again, and I will let you know if anything is actuated on the pipette. Note that some of the  | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5591994630) |
| 47 | 2026-09-08 21:17 | @​claude[bot] | Ran it — **12/12, campaign 83**. And the probe I built underneath the position counter says the switch loop is **open** while the Arduino's STEP output is **perfect** | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5591997774) |
| 48 | 2026-09-08 21:35 | @​benwhitney5463 | New Trio (shorter test, different park positions) pipette_test.yaml cub_xl_ben_pipette_capper.yaml ben_6vials_tiprack.yaml | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5592188010) |
| 49 | 2026-09-09 21:12 | @​sgbaird | @claude have a look at https://science-jubilee.readthedocs.io/en/latest/building/pipette_tool.html and the GitHub repository attached with that, since | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5608815876) |
| 50 | 2026-09-09 21:12 | @​claude[bot] | Read it properly this time — and it turns up the p20 constants, an independent check on the P300 calibration, a 2.5× current error, and one resistor that would make the driver say what's wrong | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5608819470) |
| 51 | 2026-09-15 21:45 | @​benwhitney5463 | @claude I connected a 10 kilo-ohm resistor between A0 and A1. Run the trio, then report back. Feel free to delete the pipette_park_position. link the  | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5688524600) |
| 52 | 2026-09-15 21:46 | @​claude[bot] | Ran it — **12/12, campaign 26**. Then taught the firmware to use your resistor, and got the first straight answer out of the TMC2209: **it isn't communicating at all** | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5688528247) |
| 53 | 2026-09-16 22:16 | @​benwhitney5463 | @claude run the trio again this time with the current percent at 17 | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5705358341) |
| 54 | 2026-09-16 22:17 | @​claude[bot] | Ran it — **11 of 12 steps, campaign 36**. Then the closing `home` failed, and the machine is parked in `Alarm`. Separately: `RUN_CURRENT_PERCENT 17` is in the flashed image but never reaches the chip | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5705362338) |
| 55 | 2026-09-17 14:47 | @​benwhitney5463 | @claude summarize the troubleshooting we've already done on the pipette (be brief) an give potential next steps. | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5716350545) |
| 56 | 2026-09-17 14:48 | @​claude[bot] | Pipette: where we are, and what I'd do next | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5716356734) |
| 57 | 2026-09-17 21:55 | @​benwhitney5463 | @claude Try the trio again. I fixed the error from the last run, so the machine should be able to home. When I pull the plunger manually, it moves fre | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5721762440) |
| 58 | 2026-09-17 21:56 | @​claude[bot] | I couldn't run it — the Arduino's serial link is corrupting data, so `run_protocol` aborts at instrument connect. The P20 GEN2 alignment is done, and your hand test plus Alex's review pin the driver fault on one measurement | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5721765761) |
| 59 | 2026-09-17 22:43 | @​benwhitney5463 | @claude the driver current pot is turned completely clockwise to allow 2A. Should I change that? What is the best way to measure 12V at the screw term | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722205565) |
| 60 | 2026-09-17 22:44 | @​claude[bot] | `F` is *Forward*, not *Fault* — and your two facts together make `VM` the answer | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722210120) |
| 61 | 2026-09-17 23:06 | @​benwhitney5463 | @claude try running the trio again | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722394735) |
| 62 | 2026-09-17 23:06 | @​claude[bot] | It didn't run — `home` (step 0) failed, **0 steps executed**. The cause is `ALARM:9` on **Z**, and there's a second, separate fault on **X** | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722398630) |
| 63 | 2026-09-17 23:28 | @​benwhitney5463 | @claude, the gantry wasn't on... that is my bad. It is on now. Try the trio again. | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722607151) |
| 64 | 2026-09-17 23:28 | @​claude[bot] | Ran it — **the gantry homed on the first attempt, 18.1 s.** Then `decap vial_1` didn't confirm, and the interlock stopped it at step 2. Separately: I owe you a retraction — there was never a limit-switch fault | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722611202) |
| 65 | 2026-09-18 00:00 | @​benwhitney5463 | @claude run the trio again. That time, the capper/decapper never actually went down in the z-direction. Any ideas why? | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722877699) |
| 66 | 2026-09-18 00:00 | @​claude[bot] | Running the trio, and instrumenting Z specifically | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722881065) |
| 67 | 2026-09-18 00:10 | @​benwhitney5463 | @claude I measured the voltage on the screw heads of the Stepper motor driver, and it read at 13V. I stopped the run because you tried to push past th | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722983477) |
| 68 | 2026-09-18 00:11 | @​claude[bot] | The Y overrun was mine — a relative jog computed against a counter that was 282 mm wrong. And 13 V at `VM` retires the hypothesis I'd put at the top of the list | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5722987717) |
| 69 | 2026-09-18 00:34 | @​benwhitney5463 | @claude try the trio again. The machine is homed right now. | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5723187035) |
| 70 | 2026-09-18 00:34 | @​claude[bot] | Ran it — **12/12 steps, campaign 54**. And for the first time the plunger **retracts**: every command emitted steps, in both directions | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5723190142) |
| 71 | 2026-09-18 00:45 | @​benwhitney5463 | @claude still no physical actuation on the P20. The LEDs on the Motor Driver were as such: B red for the majority while the Pipette was running comman | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5723280806) |
| 72 | 2026-09-18 00:45 | @​claude[bot] | Your LED reading matches the trace command-for-command — which means everything upstream of the driver chip is now proven good, and the fault is inside one short segment | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5723283674) |
| 73 | 2026-09-21 17:20 | @​jarrettshupe | @claude summarize everything that ben has done since you listed the "next steps" for troubleshooting. | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5764603386) |
| 74 | 2026-09-21 17:20 | @​claude[bot] | What Ben has done since the 2026-09-17 next-steps list | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5764608218) |
| 75 | 2026-09-21 17:36 | @​jarrettshupe | Could the stepper driver have anything to do with the issues above? @claude | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5764821653) |
| 76 | 2026-09-21 17:37 | @​claude[bot] | Short answer: not for the gantry, and yes for the plunger — where it's now one of only two things left | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5764827888) |
| 77 | 2026-09-21 21:50 | @​benwhitney5463 | @claude check https://github.com/Ursa-Laboratories/Cubware/blob/main/documentation/opentrons-pipette-setup.md is everything in the "before running pip | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5768010367) |
| 78 | 2026-09-21 21:50 | @​claude[bot] | Checked all four — **1–4 are good to go**, with one caveat on #1 that's worth fixing before the next run: the flashed image isn't the P20 GEN2 one | [·](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5768014434) |

## What stayed on #171

Not everything on that thread is pipette work. These stayed, and the reason is
recorded so the split is auditable rather than a judgement call taken on trust:

| comments | when | subject |
|---|---|---|
| [1 comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5137258252) | 2026-07-30 | thread bootstrap |
| [17 comments](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5148514023) | 2026-08-01 → 2026-08-03 | capper/decapper engage depth, cap capture, park position, X-rail drag |
| [2 comments](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5361568302) | 2026-08-20 | Ursa's simulation-only panda/mock configs |
| [1 comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5429493288) | 2026-08-26 | Tailscale workflow step removed from main (CI infrastructure) |
| [2 comments](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5642454946) | 2026-09-12 | new CubXL Pi + cameras; answer is the tailnet ACL |
| [3 comments](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5642530631) | 2026-09-12 → 2026-09-14 | tailnet ACL escalation |
| [2 comments](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5668131902) | 2026-09-14 | CubOS install on rpi-5-des4 (provisioning) |
| [1 comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5676760183) | 2026-09-15 | tailnet ACL follow-up |
| [2 comments](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5676809636) | 2026-09-15 | CubOS main update audit |
| [2 comments](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5688376684) | 2026-09-15 | CubOS main migration |
| [1 comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5768117054) | 2026-09-21 | the request that created this split |
| [1 comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/171#issuecomment-5768121409) | 2026-09-21 | progress comment for it |
