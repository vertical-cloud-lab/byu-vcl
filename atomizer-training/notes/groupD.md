# Group D — atomizer video transcript index

Source: YouTube auto-captions (`/tmp/work/autosubs/<id>.txt`); no Whisper transcript existed for any of these nine IDs when they were indexed.
All nine have since been re-checked against Whisper large-v3-turbo ([`../transcripts/whisper/`](../transcripts/whisper/)): the six short clips have
word-timed sentence segments, the three run videos coarse 30 s–4 min ones, so caption start times are kept. Lines still disputed after that were
re-decoded word by word from the audio ([`recheck-clips.json`](../transcripts/whisper/recheck-clips.json), "clip re-run"). Corrections are marked in the
rows and listed in each Unclear section. Captions are sparse and noisy, so long silent stretches are real gaps, not omissions. Speaker names are given only
where the transcript makes them clear; "narrator" = the person holding the camera. Items marked "(inferred)" are not
stated verbatim in the captions.

## TFpU4uqVF9c — nzyjn0 atomization AlSi10Mg-Al6063 (20:56, Sep 30)

Bartosz narrates the first custom-charge run (AlSi10Mg powder in an Al 6063 cup, per the title) from the end of the gas-wash stage through the pour.
The furnace is at ~270 °C when the clip starts; he explains the five vacuum/argon gas washes, that "melting pressure" is used at the end of a cycle to
put overpressure in the furnace, and he alternates vacuum, backfill and temperature steps until the oxygen reading is low and stable. He then raises
the temperature above normal to homogenize the mixed charge, watches an un-homogenized spot with a thicker oxide layer on one side, decides to pour
anyway at ~800 °C, and drains using the low draining-pressure settings from the day before under manual pressure control. The pour is over within
about a minute ("It was fast. It was everything"), then melting pressure, sealing rod down, generator stop. Phases: during (pump-down / gas wash, heating, homogenization, atomizing) and the first shutdown
steps. The video description adds a remark not in the captions: irregular particles are better for compaction and larger particles for (resisting)
oxidation. Re-checked against the Whisper transcript (five segments, one spanning 04:02–15:56, so the caption times are kept).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:05 | pump-down | Furnace "at around 270" (°C, inferred); "making five gas washes, so vacuum and filling with protective gas". |
| 00:16 | pump-down | "At the end of the cycle we need to use the melting pressure to create the overpressure in the furnace." |
| 01:37 | pump-down | Presses "melting pressure". |
| 01:40 | pump-down | "Now let's vacuum the chamber." |
| 02:45 | pump-down | Pump down "as much as we are able to", then backfill with protective gas (argon) (inferred). |
| 02:58 | pump-down | "And again" — next wash cycle. |
| 04:03 | heating | "After filling the chamber with protective gas again, let's go to higher temperature." |
| 04:53 | pump-down | "And now, again" — another wash at the higher temperature. |
| 09:48 | pump-down | "Okay, final one." — last wash cycle (clip re-run of 09:35–10:15; the captions' "10" was "Okay", and the batched Whisper has nothing there). |
| 10:06 | heating | "Oxygen level is low. Everything stable. Now we can raise the temperature." |
| 10:26 | heating | "Start with slightly higher temperature to help homogenize the material" (mixed powder/cup charge). |
| 14:51 | heating | "Mostly homogenized, but I still see something on one side, some leftover. Let's give it a moment." |
| 15:55 | heating | Slight lack of homogenization on one side; "visibly thicker layer of oxide". |
| 16:24 | heating | Raises temperature "just a little bit more" to help. |
| 16:35 | heating | "Seems much better. But there is still something left." |
| 17:17 | heating | Decision: "try to pour it and see what will stay"; lower the temperature "to around 800°". |
| 19:14 | atomizing | Uses "the parameters of low graining pressure that I have used yesterday" (Whisper "graining", captions "draining": the pour pressure); controls mostly via pressure control. |
| 19:27 | atomizing | "Just barely anything. There's also little material. That's why manual control would be better." |
| 19:40 | atomizing | "Vibrations on" (ultrasonic generator started). |
| 20:28 | after | "It was fast. It was everything." — pour complete in under a minute. |
| 20:36 | after | "So melting pressure, sealing rod down. Generator stopped." (Whisper; the captions' "signal down" is the sealing rod). |

### Procedural steps
Before
- (none captured; clip starts at the gas-wash stage)

During
- Run five gas washes: vacuum the chamber, backfill with protective gas, repeat (00:10).
- At the end of each wash cycle press "melting pressure" to put overpressure in the furnace (00:16, 01:37).
- Interleave washes with temperature steps; only raise temperature after backfilling with argon (04:03, 04:53).
- Proceed to melt temperature only when the oxygen reading is low and stable (10:06).
- For a mixed charge, overshoot slightly to homogenize, then watch the melt surface for leftover material/oxide (10:26, 14:51).
- If a spot persists, nudge the temperature up a little; if it still persists, pour anyway and see what stays (16:24, 17:17).
- Lower to ~800 °C before draining (17:31).
- Use low draining pressure and manual pressure control when there is little material (19:14, 19:27).
- Switch vibrations on just before opening the pour (19:40).

After
- When the pour is finished: melting pressure, sealing rod down, generator stop (20:36).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| ~270 (°C, inferred) | furnace temperature at start of clip | 00:07 |
| 5 | gas washes (vacuum + argon backfill) | 00:10 |
| ~800 °C | temperature lowered to before pouring | 17:31 |
| "low graining pressure" | pour pressure, same setting as the previous day (value not stated; Whisper "graining", captions "draining") | 19:14 |

### Quotable moments
- "At the end of the cycle, we need to use the melting pressure to create the overpressure in the furnace." (00:16)
- "Oxygen level is low. Everything stable. Now we can raise the temperature." (10:06)
- "Let's start with slightly higher temperature to help homogenize the material." (10:26)
- "There's also little material. That's why manual control would be better." (19:29)
- "We'll just have to try to pour it and see what will stay." (17:17)

### Unclear / needs checking
- "around 270" at 00:07 is assumed to be °C (consistent with the 250 °C wash stage in the Oct 2 run).
- "10. Final one." (09:48) — resolved: the clip re-run hears "Okay, final one."; there is no number, so nothing to reconcile with the 5-cycle gas wash.
- The homogenization temperature and the actual draining-pressure value are never spoken.
- Whether "melting pressure" and "draining pressure" are the same control — no: they are two furnace pressure settings (melting pressure holds the furnace just below the chamber, the pour pressure pushes the melt out, Video 1 31:21). Here melting pressure ends each wash cycle and the pour (00:16, 20:36), and the pour uses the "low graining pressure" (19:14, the label Whisper hears in the training videos too).
- Re-checked against Whisper: no number changes (270, five washes, ~800 confirmed). Whisper adds "sealing rod down" to the end-of-pour sequence (20:36).

## qYyT39D5Yzo — Atomizer Fri Oct 2 pt1 (21:39, Oct 2)

The team's first run without the trainer, part 1: startup and loading. The narrator turns on utilities (air, compressed air), notices a chilled-water
fitting is still leaking, and reads a startup checklist from a phone (oil, water level, argon at 8 bar, chilled water, air valve). Much of the clip is
spent identifying the unlabeled sonotrode/atomization plates (Mo, Nb, carbon-fibre, stainless, "aluminum") and deciding on a molybdenum plate because
"those are the gold standard" for smaller particles, then scrounging metric 17/18 mm wrenches and a torque wrench to mount the upper sonotrode. The
nozzle (new, 0.5 mm) is checked for light through the hole, the HMI is password-protected, the transducer housing is skipped "this time", and after
closing the chamber they reopen it to run the ultrasonic frequency check ("only one valley, one peak"). Phases: before (setup/prep/loading), with
several lessons learned. Re-checked against the Whisper transcript (segments of 30 s to 4 min, so the caption times are kept).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:09 | setup | Narrator starts the atomizer run; turns on "this guy" and the air. |
| 00:41 | setup / problem | "The water's still leaking from... this guy here. I forgot to tighten that a little more." |
| 00:53 | setup | Turn on the compressed air. |
| 01:26 | setup | Startup checklist: check oil, check water level, argon set to 8 bar, open chilled water lines (~20°), press air valve. |
| 01:46 | prep | Plan: use a molybdenum plate this run; nothing currently installed ("nothing's on here"). |
| 02:24 | prep / lesson | Cannot identify plates; "have to go back and find the video"; "I'm going to mark these so we don't forget." |
| 03:01 | chatter | Ronnie arrives: "You ready to do some science?" |
| 03:36 | prep | Plate ID: "probably molybdenum-dipped carbon fibre... feel how light they are"; "MO is molybdenum"; others "just the Mo". |
| 04:16 | prep | Another plate material "right next to molybdenum on the periodic table... NB" — niobium, said as "Molybdenum and Neobium" (Whisper, 04:42). |
| 05:06 | prep | "So these ones are just carbon fibre, right? I don't know what makes these different." |
| 05:20 | prep | Set includes big carbon fibre, stainless steel, big molybdenum; choose Mo: "gold standard. We get smaller particles." |
| 05:52 | tools | Borrowed tools from the PSC — "these are the project support centers, I think" (Whisper; captions "project sports centers"); must return later; "we need to order some tools." |
| 06:21 | cleaning | Need something to clean "this thing" after the run. |
| 06:33 | cleaning / lesson | Aluminum residue not coming off a part; "didn't know how dingable this is"; "it's tungsten... a tungsten alloy." |
| 06:49 | cleaning | "The shape of this is very important" — Bartosz "told me it's not a big deal" (Whisper), but the deposit "grew from the last run to the one we just did"; remove carefully, maybe with a file. |
| 07:24 | setup | Power on by pressing the button; "that green light just came on." |
| 07:38 | loading | Attach "the upper sonotrode... he called it like protruding sono[trode]... the extending sonotrode." |
| 07:56 | tools | Small wrenches were returned; toolbox Allen keys are imperial only; need metric 17 and 18. |
| 09:17 | tools | Ronnie sent to fetch wrenches 18 and 17 from the PSC. |
| 09:49 | prep | "That shouldn't be empty relatively... going to suck having to clean that out" (container? unclear). |
| 10:08 | loading | "Check the nozzle. Pretty sure I put a new one in there. Yep, there's light coming through." |
| 10:44 | loading | "Make sure it's set back in good." |
| 10:54 | setup | HMI is password protected; "Heat" selected (11:11). |
| 12:01 | setup | "That's not a nice noise... Don't want to press that." (unidentified alarm/button). |
| 14:15 | setup | Narrator reviews "the system SOP that I wrote down cuz it's kind of a little bit funky... making sure it's linear." |
| 14:42 | loading | Torque wrench "the 50 torque" already set; 17 mm wrench used. |
| 15:09 | loading | "This will go on this part here"; "this whole thing turns" (16:00). |
| 16:08 | loading / lesson | "We should also put the housing over this too" — four screws; skipped: "let's not worry about it this time." |
| 17:02 | lesson | "But we should, to protect this expensive... transducer." |
| 17:21 | loading | "Shut those three things on there" (chamber latches, inferred). |
| 17:29 | pump-down | Reading SOP: "After purging at 500... press protective gas... that'll allow air into the chamber. Start by pressing purging." |
| 18:44 | loading | "Are you ready for the .5 mm?" (captions; the clip re-run hears "Did you already feel a .5mm?", the batched Whisper drops it) — 0.5 mm nozzle (inferred); "we'll just be doing that crucible." |
| 20:00 | check / lesson | "We need to test this... Can we open this back up?" — chamber reopened for the test. |
| 20:50 | check | Frequency scan: "He said there should only be one valley, one peak. So I think that's good." |
| 21:09 | check | "Power zero watts." |
| 21:13 | record | Takes a video inside the chamber: "Oh yeah, look at that." |

### Procedural steps
Before
- Turn on the air, then the compressed air; confirm water lines are not leaking (00:24, 00:41, 00:53).
- Run the startup checklist: check oil, check water level, argon regulator at 8 bar, open chilled water lines, press air valve (01:26).
- Select the atomization plate material for the run; label plates so they can be identified later (01:46, 02:56).
- Power the unit on with the button and confirm the green light (07:24).
- Mount the upper sonotrode with 17/18 mm wrenches and the torque wrench set to "50" (07:38, 14:42).
- Fit the protective housing over the transducer with its four screws (16:08, 17:02).
- Install a new nozzle and confirm the orifice is open by seeing light through it (10:08).
- Seat the nozzle/crucible assembly fully ("set back in good") (10:44).
- Log in to the password-protected HMI (10:54).
- Close the chamber ("shut those three things") (17:21).
- Run the ultrasonic frequency test before closing up; expect one valley and one peak, power 0 W (20:50, 21:09).

Cleaning
- Remove aluminum build-up from the tungsten-alloy part after each run, without damaging its shape; a file may work (06:33, 07:08).
- Return borrowed tools and order a dedicated metric tool set (06:08, 06:28).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| 8 bar | argon regulator setting on the checklist | 01:29 |
| ~20° | chilled water lines "about 20°" (°C setpoint? unclear) | 01:31 |
| 17, 18 (mm) | wrench sizes needed for the sonotrode | 09:21 |
| 50 | torque wrench setting ("the 50 torque"; units unstated, N·m inferred) | 14:42 |
| 4 | screws holding the transducer housing | 16:33 |
| 500 (°C) | SOP: "after purging at 500" | 17:33 |
| 0.5 mm | nozzle size ("the .5 mm") | 18:44 |
| 1 valley, 1 peak | expected frequency-scan shape | 20:53 |
| 0 W | ultrasonic power at idle | 21:09 |

### Quotable moments
- "I'm thinking for today we do a molybdenum one since he says those are the gold standard. We get smaller particles with those." (05:27)
- "It's tungsten, I believe, like a tungsten alloy. However, the shape of this is very important." (06:44)
- "It grew from the last run to the one we just did. So I think we should get it off. We should be careful not to damage it." (06:58)
- "Let's not worry about it this time. But we should, to protect this expensive transducer." (16:59)
- "He said there should only be one valley, one peak. So I think that's good." (20:53)

### Unclear / needs checking
- Which part is the "upper / extending sonotrode" (booster? sonotrode extension?) — the trainer's term was not caught.
- Which tungsten-alloy part carries the aluminum deposit (sealing-rod tip? sonotrode plate?).
- "Aluminum plates" at 02:43 — plates made of aluminum, or plates intended for aluminum charges?
- "Open chilled water lines about 20°" — valve angle or 20 °C.
- "Press protective gas... that'll allow air into the chamber" (18:12) — probably means argon fill/vent; wording garbled.
- "PSC" — resolved: Whisper hears "these are the project support centers, I think", the shop the tools came from. Who the narrator is (not Ronnie) is still open; Whisper's "once Ryan gets back" (10:08 segment) is presumably Ronnie fetching the wrenches.
- Re-checked against Whisper: 8 bar, "about 20 degrees", wrenches 18 and 17, one valley/one peak and zero watts are all confirmed as spoken. The ".5 mm" (18:44) and "the 50 torque" (14:42) lines are missing from the batched Whisper but present in the clip re-run ("this one is the 50 torque, right? Yep, and I already set it"; "17 or 18. 17").

## of5-LhkX_VQ — Atomizer run Oct 2 part 2 (30:18, Oct 2)

Part 2 of the unsupervised run: purge, heat, pour and cooldown. A small graphite part is dropped while loading with tweezers, the sealing rod is
lowered, 250 °C is set, pressure control is turned on and the wash sequence is explained (one wash at room temperature, one at 250 °C, one or two at
500 °C, stopping when the oxygen reading is in the "low 20s"); a "gas wash" is five vacuum/argon cycles and pressure control (which holds 150 mbar)
must be turned off before pumping. The generator is started, the chilled water alarm waited out, and after the 500 °C wash the oxygen reads low 20s so
the fourth wash is skipped. They set 830 °C (the trainer had used 850 then 800), set amplitude to "about 90" on an unmarked knob, the pour pressure to
".17 bar" (Whisper; captions "17.17"), check the plate ("pure molybdenum"), and open the sealing rod: material flies out and most of the charge is not atomized — the pressure "was definitely too high" and the plate
should have been closer. Shutdown follows (sealing rod closed, generator stop, ultrasonic off, furnace to 250 °C, open above... only below 400 °C
because graphite oxidizes). Phases: during (pump-down, heating, atomizing) and after (cooldown), plus troubleshooting. Re-checked against the
Whisper transcript (segments of 30 s to 3 min, so the caption times are kept) and a word-level re-run of the disputed clips
([`../transcripts/whisper/recheck-clips.json`](../transcripts/whisper/recheck-clips.json)): the pressure was 0.17 bar and the plate pure molybdenum.

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 01:14 | setup | "Oh, good. It's working." |
| 01:25 | prep | Surface "already been wiped down... we can wipe it down again. I don't think that would hurt." |
| 01:55 | chatter | It is ~2:11 pm; a 2:30 meeting with Dr. Barrett is pushed to 3–3:15. |
| 02:25 | status | "Just figured out some kinks and are about to start purging period." |
| 03:00 | loading | "You locked it down"; charge orientation: "Just this way." |
| 03:15 | loading / lesson | Tweezers for a graphite part: "I really don't know how fragile graphite is... Bartosz made it sound like if you dropped it..." |
| 03:45 | loading / mistake | "I dropped it." (apparently survived; continues). |
| 03:58 | loading | "Sealing [rod] is down." |
| 04:03 | heating | "Set 250°." Green light on; "turn on pressure control" (04:16). |
| 04:23 | pump-down | "Now we're going to put some vacuum pump and gas wash." |
| 04:42 | pump-down | Sequence: vacuum here first, then at 250, then at 500; doing the first one "before we go temperature at all" — chamber at 30°. |
| 04:59 | pump-down | "One wash of the whole system at room temperature, then one at 250, then two washes at 500 if needed" — "it's like four washes total" (Whisper). |
| 05:22 | pump-down | How to know if needed: oxygen reading; "if it's like low 20s, he says that's good." |
| 05:54 | heating | "Heat." |
| 06:31 | pump-down | "Melting pressure." |
| 06:54 | panel | Two separate panel sections: one for the chamber, one for the furnace. |
| 07:19 | record | "We just put a date on that." |
| 08:01 | pump-down | "Now let's come back up with argon"; turn on "this guy"; "open these a little bit" (08:09). |
| 08:20 | setup | "Wait for cooling water flow [warning] to go off." |
| 08:46 | setup | "80 PSI. Dang, that's high." (gauge unidentified). |
| 09:05 | setup | "Generator start." |
| 09:24 | pump-down | "Once that gets up to 250°, then press vacuum pump and gas wash again." |
| 10:35 | pump-down | Button difference: "this does five cycles... five cycles per wash and only one cycle per [the other]." |
| 11:13 | pump-down | To wash: "just press gas wash. So vacuum pump, gas wash." |
| 11:50 | pump-down | "Melting pressure then press. Pressure control keeps this at 150 m[bar]. Going to turn that off so we can suck it out." |
| 12:11 | pump-down | Watch gauge go "all the way" down; then "turn off that" (12:50). |
| 13:06 | heating | Change temperature setpoint up to 500. |
| 13:18 | design | No keypad for exact setpoints; furnace is from a different company that "won't let them interface", so controls are separate. |
| 13:42 | design | "It should be really easy to do a single button that does this entire cycle" — but "I don't know what the real situation is" (Whisper): the interface reason is second-hand. |
| 14:20 | pump-down | At 500: "press vacuum pump gas again." |
| 14:32 | plumbing | Identifying lines: chilled water lines ("really cold"); white hose is the argon into the tank (15:02). |
| 15:42 | chatter | "He said we could atomize gold and silver in this" — wedding-ring joke. |
| 16:31 | pump-down | "All right, I'm going to turn off pressure control" (Whisper, both the batched transcript and the clip re-run; the captions heard "turn on"), ready to pump the chamber at 500 °C; "this is going up … it's going down" (16:59). |
| 17:50 | check | Oxygen "in low 20s. So I think we're good. We don't have to do another purge cycle." |
| 18:21 | record | "So just write down the mbar" (Whisper); "with the mbar check" (19:15). |
| 19:25 | heating | "We can bring this up to 800." |
| 19:33 | heating / deviation | "He went to 850 and then brought it down to 800?" — can't remember why: "I think you just like felt like that was a good amount, so I guess we'll just have to play with it" (Whisper); "I'm going to set to 830." |
| 19:56 | heating | "Hoping this is going to mix well. Starting to glow." |
| 20:12 | chatter | Meta glasses livestream idea. |
| 21:56 | heating | "Is it getting orange? Oh, yeah. I don't think it's melting just yet." |
| 22:15 | charge | Plug ("cap") length: "I think it was like .3 something" per the GitHub issue (captions and the clip re-run; the batched Whisper drops it); "didn't go hardly in at all" — maybe shorter is fine. |
| 23:04 | charge | Purpose of the plugs: "apparently what we're doing could explode" (loose powder; inferred). |
| 23:17 | atomizing | Pour pressure set: "I guess we'll see if .17 bar is high enough. He kept turning it down" (every Whisper decode: 0.17 bar, as #249 records). The label just before is "printing pressure" (captions) or "spinning pressure" (clip re-run), i.e. the pour pressure heard elsewhere as "graining", not melting pressure; the captions' "17.17 bar" doubled the number. |
| 23:37 | heating | "Hey, it's melting. Oh, it's gone. Definitely not a lot in there." |
| 23:54 | heating | Powder "might be clumped up again... No, I think it's mixing" — induction stirs the melt. |
| 24:18 | safety | Heat felt through the viewing window. |
| 24:27 | heating | "Let that go for about 2 minutes" before atomizing. |
| 24:54 | atomizing | Amplitude: 100 "might be too much... bring it to about 90"; knob reads "88 to 100... around 90". |
| 25:23 | lesson | "We're going to have to create digital readouts" for the amplitude knob. |
| 25:38 | heating | "830°." |
| 25:53 | atomizing | "Check the plate. What plate is this? The M[o]? … Not the coated carbon, it's pure molybdenum. Yeah, pure molybdenum." (word-level clip re-run of 25:50–26:15; the captions' "aluminum … pure aluminum" was a mis-hearing, and the batched Whisper drops the answer). |
| 26:25 | atomizing | "Sealing rod, graining pressure" (both transcripts "grinning": the pour pressure), on. |
| 26:45 | atomizing / problem | "Uh-oh. Can you turn off the frequency? Holy dang, [they] are flying out of there." (captions and the clip re-run; the batched Whisper drops the second sentence). |
| 27:00 | atomizing | "It's totally working... Is that all of it? Yep." "Most of it did not get atomized, unfortunately." |
| 27:26 | lesson | "That was definitely too high. It should have been a lot lower." |
| 27:33 | lesson | "The plate needed to be a lot closer so [it] had more time to run down it." |
| 27:41 | after | Shutdown: once sealing rod [closed], generator stop, ultrasonic stop, cooler. |
| 27:59 | after | Temperature "down to 250". |
| 28:07 | after | "We got some... you can see a pile. A good amount." |
| 28:37 | after | Wait until "400° up here", then open — "it'll cool a lot faster." |
| 28:52 | theory | Graphite exposed to oxygen above 400–500° reacts; below 400° it is safe to expose. |
| 29:26 | problem | Water dripping on a cord — not condensation: "this is leaking. We need to tighten that more." |
| 29:53 | after | "Our first atomizer run by ourselves. Woo!" |

### Procedural steps
Before
- Wipe down the chamber/sonotrode surfaces before loading (01:25).
- Load the graphite part with tweezers and do not drop it (03:15).
- Lower the sealing rod before heating (03:58).

During
- Set 250 °C, confirm green light, turn on pressure control (04:03, 04:16).
- Gas-wash once at room temperature, once at 250 °C, then once or twice at 500 °C (04:42, 04:59).
- Before pumping, turn pressure control off (it holds 150 mbar); press melting pressure, then vacuum pump + gas wash (11:50).
- "Gas wash" runs five vacuum/argon cycles; the other button runs one (10:35).
- Backfill with argon, start the generator, wait for the cooling-water-flow warning to clear (08:01, 08:20, 09:05).
- After the 500 °C wash check oxygen; low 20s means no further wash (05:22, 17:50).
- Write down the readings (18:21).
- Raise to melt temperature (trainer: 850 then 800; team used 830) and hold ~2 minutes to mix (19:25, 19:51, 24:27).
- Set amplitude (~90) and check which plate is installed (24:54, 25:53).
- Open the sealing rod with the pour ("graining") pressure on; watch the pour (26:25).

After
- Close the sealing rod, stop the generator, stop the ultrasonic, cooler on (27:41).
- Set the furnace to 250 °C (27:59).
- Open the chamber only once the upper temperature is below 400 °C, then it cools faster (28:37).

Troubleshooting
- If most of the charge pours un-atomized: lower the draining pressure and move the plate closer to the nozzle (27:26, 27:33).
- Tighten the leaking chilled-water fitting (29:26).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| 250 °C | first heated wash setpoint | 04:03 |
| 30° | chamber temperature at first (room-temp) wash | 04:57 |
| 500 °C | second heated wash setpoint; washes "if needed" | 05:17, 13:09 |
| low 20s | oxygen reading considered good (unit not stated) | 05:29, 18:10 |
| 80 PSI | a gauge, "that's high" (unidentified) | 08:46 |
| 4 washes | total: room temperature, 250, two at 500 if needed ("it's like four washes total", Whisper) | 05:05 |
| 5 cycles | per "gas wash"; 1 cycle for the other button | 10:44 |
| 150 mbar | pressure held by pressure control | 11:59 |
| 800 / 850 °C | trainer's melt setpoints (850 then 800) | 19:28, 19:36 |
| 830 °C | team's melt setpoint | 19:51, 25:38 |
| ~0.3 (in, inferred) | plug length from the GitHub issue (".3 something": captions and clip re-run) | 22:49 |
| 0.17 bar | pour pressure: Whisper ".17 bar", as #249 records; captions "printing pressure 17 … 17.17 bar" | 23:26 |
| ~2 min | hold after melting before atomizing | 24:27 |
| pure Mo | plate on Oct 2: "pure molybdenum" (clip re-run; captions "pure aluminum") | 26:07 |
| ~90 (88–100) | amplitude knob setting | 25:06, 25:30 |
| 400 °C (500 °C) | graphite oxidation threshold; open chamber below 400 | 28:38, 28:56 |

### Quotable moments
- "One wash of the whole system at room temperature, then one wash at 250, then two washes at 500 if needed." (05:08)
- "Pressure control keeps this at 150 m[bar]. Going to turn that off so we can suck it out." (11:59)
- "The furnace system is like a different company and they won't let them interface with each other. That's why these are separate." (13:33)
- "That was definitely too high. It should have been a lot lower... The plate needed to be a lot closer." (27:26)
- "The graphite when exposed to oxygen above 400° or above 500° reacts with the oxygen." (28:52)

### Unclear / needs checking
- Pressure at 23:17 — resolved as spoken: every Whisper decode (batched transcript, clip re-run at beam 5 and beam 1) has "I guess we'll see if .17 bar is high enough. He kept turning it down", i.e. 0.17 bar, matching #249. The label before it is "printing pressure" (captions) or "spinning pressure" (clip re-run, beam 1): the pour pressure (heard "grinning" at 26:25, "graining" in the training videos), not melting pressure. Still open: why 0.17 bar was "definitely too high" when the chamber holds 150 mbar (+20 mbar), unless the HMI value is a differential above the chamber (inferred).
- Which graphite part was dropped (03:45) and whether it was inspected afterward.
- Plate identity at 25:59 — resolved: a word-level re-run of 25:50–26:15 hears "What plate is this? The MW? Yeah. And not the coated carpet, it's pure molybdenum. Yeah, pure molybdenum." (beam 5; beam 1 also ends "just pure molybdenum"; a longer 25:40–26:35 window trails off as "…not as a coated carpet, just yeah"). The captions' "The ML … aluminum … pure aluminum" was a mis-hearing of the same words; the batched Whisper segment kept only the question. Pure Mo matches the pt1 choice (05:27) and #249.
- "80 PSI" gauge (08:46): compressed air? Not the 8 bar argon.
- "Could explode" (23:15) — the trainer's actual reason for plugging the powder cup is not in the captions.
- Oxygen unit ("low 20s") — ppm presumed.
- Whether "cooler" at 27:50 is a separate shutdown action (Whisper: "Cooler, yeah").
- Re-checked against Whisper: 250, 30°, 150 mbar, 80 psi, five cycles, low 20s, 830, ~90 (88–100), 2 min and 400/500 are all confirmed as spoken. Missing from the batched Whisper but confirmed by the clip re-run: ".3 something" (22:49), "Holy dang … flying out of there" (26:53), "pure molybdenum" (26:07). Whisper-only: "four washes total" (05:05), the 850/800 answer (19:48), the hedge on the furnace interface (13:41). 16:31: Whisper hears "turn off pressure control" in both decodes, the captions "turn on"; "off" is kept, as the chamber is pumped next.

## BxA7Z9Fliss — Claude ping for dosing Al 4047 (10:48, Oct 1)

A screen-and-camera clip of the narrator on GitHub, scrolling to a pull request where Claude can be pinged, copying a prompt to request another
powder-dosing run of Al 4047 (the powder doser, not the atomizer). Almost all of the clip is silent apart from throat-clearing; the only commentary is
about seeing reflections in the camera when daytime turns to nighttime. Phase: before (powder preparation via the dosing workflow), effectively
unrelated to atomizer operation.

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:01 | prep (dosing) | On GitHub, "one of these pull requests I have where I can ping Claude... before I'd run another dosing." |
| 00:12 | prep (dosing) | "Just copy that prompt down here." |
| 02:54 | chatter | Waves to self in the reflection; camera workflows show reflections "or daytime goes to nighttime". |
| 05:42 | chatter | "Oh, almost forgot." (unspecified). |

### Procedural steps
Before
- To run another Al 4047 dosing, reuse the saved prompt by pasting it into a comment on the Claude-enabled PR (00:01, 00:12).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| Al 4047 | powder being dosed (title only; not spoken) | — |

### Quotable moments
- "You start doing camera workflows and you get reflections or daytime goes to nighttime and suddenly you can see things that normally you wouldn't." (03:00)

### Unclear / needs checking
- The PR number, the prompt text and the dosing parameters are on screen, not in the captions.
- What was "almost forgot[ten]" at 05:42.
- Re-checked against Whisper (word-timed sentence segments): the same words; voice-activity detection finds speech only at 00:00–00:17, 02:53–03:07 and 05:46, so the rest of the 10:48 is silent screen and camera time.

## Kv9DT3Vo0GE — Exciting Vertical Cloud Lab Construction Update!! Atomizer Will Be Installed Soon! (02:30, Sep 1)

A walk-through of the lab enclosure under construction, before the atomizer arrived. The narrator climbs a ladder to show the dehumidifier (filter
removed), a pump beside it, venting being installed, a large pipe and chilled-water lines, then the very large transformer that powers the atomizer
(too big for its planned spot), the new slats, vents, lights (switches not yet wired), cabinets, a big sink, a second sink (presumably emergency
eyewash), whiteboard space and large breaker boxes. Phase: installation / facility prep; no run content.

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:00 | installation | Dehumidifier up top "with the filter gone"; pump next to it; venting going in. |
| 00:16 | installation | Climbs ladder; big pipe hooked up; lights still hanging. |
| 00:31 | installation | Lines overhead "are cold water or chilled water". |
| 00:43 | installation | "Look how big this transformer is. This is the device that powers our atomizer." |
| 00:49 | installation | Transformer too big for the planned spot "above there"; placed here instead; could put a tall table over it if heat allows (01:00). |
| 01:13 | installation | Slats, vents, lights; electrical "should be done"; light switches not working yet (01:28). |
| 01:35 | installation | Cabinets; big sink — "they'll have to drill the holes, put in the finished plumbing" (01:44, batched Whisper; captions "I'll"; the clip re-run's "so that the drill the holes" settles neither). |
| 01:48 | installation | Second sink, probably the emergency [eyewash]; narrator wonders why not combined. |
| 02:05 | installation | Whiteboard space; "massive" breaker boxes — "look how big these breakers are" (02:18). |

### Procedural steps
Before (installation)
- Finish sink plumbing: drill holes and install fixtures (01:44; who does it is unclear, "they'll" or "I'll").
- Keep the transformer area clear until its heat output is known before covering it with a table (01:00).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| (none) | no numeric values spoken | — |

### Quotable moments
- "Look how big this transformer is. This is the device that powers our atomizer. Holy cow, it's massive." (00:43)
- "We were going to try to put it above there on this other side, but then it was too big, so we had to put it here." (00:49)

### Unclear / needs checking
- "Emergency irons" (01:52) — presumably emergency eyewash/shower.
- Which pump is "next to" the dehumidifier (condensate pump? exhaust?).
- Re-checked against Whisper (word-timed sentence segments): the wording agrees with the captions, "emergency irons" included; the one difference is who finishes the sink plumbing (Whisper "they'll", captions "I'll").

## 07QOPRHIEvw — Placing the Atomizer!!! (01:26, Sep 3)

The atomizer and the other crate contents have been moved into the enclosure and cleaned up (the description says the containment chamber was cleaned
out and the crate unboxed). The narrator describes what remains: chilled water to be brought down from the top, the argon line run along the wall by
the orange tape with the tanks, then commissioning in about two weeks. Phase: installation. The first 55 s have no captions.

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:55 | installation | Atomizer and crate contents are in the enclosure; "cleaned up a little bit"; ready to be installed the rest of the way. |
| 01:08 | installation | Chilled water comes down from the top; argon runs "by that orange tape on the wall" with the tanks. |
| 01:18 | installation | "That should be it for installing this. Commission it in about 2 weeks." |

### Procedural steps
Before (installation)
- Route chilled water from the ceiling drop and argon from the tanks along the wall marked with orange tape (01:08).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| ~2 weeks | expected time to commissioning | 01:22 |

### Quotable moments
- "They'll bring in the chilled water down from the top and run the argon there by that orange tape on the wall." (01:08)

### Unclear / needs checking
- No captions for 00:00–00:55; whatever is shown there is undocumented. Whisper's voice-activity filter also finds no speech before 00:54, and its text after that matches the captions.

## cKwQbKdE22Q — Vacuum test (02:37, Sep 8)

This is not the atomizer. Someone adds a small amount of powder, connects a hose, switches a vacuum on, lets it run 15–30 s "to get all of the powder
out", then pours/inspects to see how much powder was captured — and finds "no visible powder in there" (the captions add "I mean, you can see it", which Whisper hears as "We should use tape"). It
reads as a test of a small vacuum for picking up (metal) powder, with an ambiguous result. Phase: prep / equipment test (powder-handling, inferred).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:00 | test | "Add just a little bit of this powder... like this here." |
| 00:15 | test | Connect the hose/fitting; "we'll turn this on" (00:24). |
| 01:08 | test | "Let it run for 15 to 30 seconds to get all of the powder out of here." |
| 01:16 | test | "Now we just leave it like that" (captions; Whisper "we'll just move it back … move forward", 01:24). |
| 01:24 | test | Pour out / inspect: "I want to see how much powder." |
| 01:37 | result | "There's no visible powder in there" (both); then "I mean, you can see it" (captions) or "We should use tape" (Whisper, 01:44) — a tape check for residue (inferred). |
| 01:59 | test | "Move everything back over here" (Whisper; captions "everything talked about too … all the way", 02:09); ends. |

### Procedural steps
Before (equipment test)
- Add a small quantity of powder, connect the vacuum, run it 15–30 s, then inspect the collection side for powder (00:00, 01:08, 01:31).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| 15–30 s | vacuum run time to clear the powder | 01:08 |

### Quotable moments
- "You just let it run for 15 to 30 seconds to get all of the powder out of here." (01:08)

### Unclear / needs checking
- What vacuum and what powder; whether this is the powder-doser vacuum, a cleanup vacuum, or a leak test of something else.
- Whether "no visible powder" means the vacuum failed to capture it or captured all of it.
- Re-checked against Whisper (word-timed sentence segments): 15–30 s and "no visible powder" confirmed; 01:44 and 01:59 differ (see rows). The frame at 01:00 shows the operator in a half-face respirator, VCL ESD coat and gloves, holding a vacuum wand; at 00:00 a gloved hand holds the powder bottle (keyframe).

## w02MRlZhpNk — Dehumidifier troubleshooting (02:58, Sep 29)

The narrator is up at the enclosure dehumidifier trying to work out why it is not running. The 24 V control terminals are "shorted to each other"
(jumpered to call for dehumidification, inferred), a relay click is heard, the condensate pump appears to have nothing attached and the drain seems
"connected directly", and the eventual suspicion is a tripped breaker; turning the humidistat knob produces clicks but the direction for "dryer" is
uncertain. Phase: facility troubleshooting (enclosure humidity control, relevant to powder handling), no run content.

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:02 | troubleshooting | "Bajillion pipes... lots of power going all over the place." |
| 00:10 | troubleshooting | Dehumidifier: "the 24 volts shorted to each other. So that should be working." |
| 00:40 | troubleshooting | "I heard a click. That's good, I guess." |
| 00:46 | troubleshooting | The pump "doesn't look like anything's actually attached to it"; its point is to move water in and out. |
| 01:17 | troubleshooting | "Is the pump just not being used at all? Maybe." Two bare wires (Whisper; captions "two pair of wires"); "looks like it's just connected directly." |
| 01:43 | troubleshooting | "Why is it not on?" — "I don't think, I don't think the breaker got tripped" (Whisper, batched and clip re-run); the captions dropped the second "don't" and heard "I think the breaker got tripped" (01:57). |
| 02:08 | troubleshooting | Clicks heard when turning the control; "I would have assumed that's the right way to turn it for dryer." |
| 02:43 | troubleshooting | Notes a line "going into the side"; goes back down (02:55). |

### Procedural steps
Troubleshooting
- Confirm the 24 V control terminals are jumpered/shorted and listen for the relay click (00:10, 00:40).
- Check whether the condensate pump is actually plumbed or bypassed (00:46, 01:17).
- If the unit is dead despite the control signal, check the breaker (01:57); here the narrator did not think it had tripped.
- Verify which direction of the humidistat knob means "dryer" (02:32).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| 24 V | control terminals shorted together | 00:18 |

### Quotable moments
- "The 24 volts [are] shorted to each other. So that should be working." (00:18)
- "Then the question is why is it not on? I don't think the breaker got tripped." (01:43, Whisper)

### Unclear / needs checking
- Outcome unknown — the clip ends without the dehumidifier confirmed running.
- Which breaker and whether the pump is intentionally bypassed.
- Re-checked against Whisper (word-timed sentence segments): 24 V confirmed ("the 24 volts shorted to each other"); the breaker line (01:43) is a negative in both Whisper decodes, and "bare" vs "pair of" wires (01:17) differ.

## z6rwmQW_3Vg — Lathe turning aluminum crucibles for atomizer experiments (01:35, Sep 26)

Machine-shop clip of making the aluminum powder cups ("crucibles") and plugs for the custom-charge runs. Rod stock is cut on the band saw to 3 in
(2.75 in target plus 1/4 in extra for facing), giving three 3 in pieces plus one ~1 3/8 in piece for plugs; on the lathe the ends are faced to exactly
2.75 in, a centre drill makes a guide hole and a 1/2 in drill bores the interior; the plugs are also turned on the lathe. Phase: before (charge
preparation).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:01 | prep | "Over our 2.75, should we cut this like 1/4 in more?" |
| 00:14 | prep | "1/4 in should be fine if you're confident in your turning abilities" — cut at 3 in (00:21). |
| 00:27 | prep | Plan: band-saw the pieces, drill the interior hole on the lathe, turn the plugs on the lathe (00:33). |
| 00:42 | prep | Cut done: three 3 in pieces plus one piece "about 1 and 3/8"; extra left to face the ends flat and exact. |
| 01:02 | prep | Centre drill "just a guide hole", then the 1/2 in drill (01:05). |
| 01:14 | prep | First piece faced both ends, "perfectly at 2.75 in"; two more to go. |
| 01:25 | prep | Putting in the 1/2 in drill bit. |

### Procedural steps
Before
- Cut rod stock 1/4 in over the finished length (3 in for a 2.75 in cup) to allow facing (00:01, 00:21).
- Face both ends on the lathe to the exact 2.75 in length (01:14).
- Centre-drill a guide hole, then bore with a 1/2 in drill (01:04, 01:25).
- Turn the press-fit plugs from the shorter piece (00:36, 00:47).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| 2.75 in | finished cup length | 00:01, 01:17 |
| +1/4 in → 3 in | band-saw cut length | 00:05, 00:21 |
| 3 | number of 3 in pieces | 00:45 |
| ~1 3/8 in | extra piece (plug stock, inferred) | 00:47 |
| 1/2 in | bore drill diameter | 01:07, 01:25 |

### Quotable moments
- "1/4 in should be fine if you're confident in your turning abilities." (00:14)
- "We just left some extra on them so we can turn off the edges, make them flatter and more exact." (00:50)

### Unclear / needs checking
- Rod outer diameter and bore depth are not spoken (repo notes say 20 mm OD, ~3 in deep bore; the 2.75 in cup here is shorter).
- Which alloy this stock is (Al 6063 per the later runs; not stated here).
- Re-checked against Whisper (word-timed sentence segments): 2.75 in, "a quarter inch more", "three three-inch pieces" and "about one and three-eighths" are confirmed. Whisper's voice-activity filter drops the 00:14 answer ("1/4 in should be fine if you're confident…") and both 1/2 in drill lines (01:05, 01:25), which rest on the captions.
