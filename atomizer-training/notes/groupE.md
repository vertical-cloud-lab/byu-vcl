# Group E — Whisper-only videos (no YouTube captions): cartridge cleaning, nozzle drilling, the expert cleaning POV and the powder-dosing sessions (Sep 29–30 2026)

Source: faster-whisper large-v3-turbo (int8) transcripts in [`../transcripts/whisper/`](../transcripts/whisper/); none of these six videos has YouTube auto-captions. The first two (cartridge cleaning, drill clip) were transcribed with VAD batching, which merged minutes of silence and scattered talk into single segments (e.g. 00:45–06:53 in the cartridge video, the whole 0:00–4:13 of the drill clip), so a row's mm:ss is the segment start and the words can come well after it. The other four were transcribed on Oct 3 with word timestamps and re-cut at sentence ends, so their times are within a second or two of the words. Two of those four (u-KjR5TENN4, QXSj0j1OqL8) have no speech at all and the third (prj_xgeuQtM) only a few words; their Whisper text is hallucinated filler, reported as such, and their rows are read from frames of the footage taken at the exact second. Speaker attribution is inferred (Bartosz = technical explanations; the trainee "with a class to teach" is probably Sterling). Items marked "(inferred)" are not said on camera; "(keyframe)" means read from the footage (the keyframe sheet, or for the three silent videos frames taken at the exact second), not from speech. Mis-hearings normalised in the text: "octatonics" = ultrasonics, "wider play" = wider plate, "start the forces" = start the process, "ALSI-10MG" = AlSi10Mg.

## f8KL31PN8bA — Cartridge cleaning (18:09, Sep 30)

Post-run clean-up between the morning run and the AlSi10Mg custom-charge run (TFpU4uqVF9c, published 2.5 h later). Bartosz, in a full-face respirator and gloves at the bench (keyframe), cleans a filter cartridge and its valve body: unscrew the plug and take the handle off to open the valve fully for access, or — since the next charge is "aluminum again" — just work paper around inside with tweezers, flush with isopropanol, blow paper lint off the seal with compressed air, and refit it where it sits. Back at the HMI he reads a second peak on the ultrasonic scan as a resonance sign (plate heats more but holds), blames the 1:1 booster + wider plate combination, says the reverse booster removes it, and explains why piezo stacks must not be over-tightened. The last third is lab housekeeping (mask only needed for post-trial cleaning, vacuum/wipe the area, cabinets and a desiccant dry box for consumables) and a look at the AlSi10Mg sample cup — kept upright, plug on top, a small vent hole — with the plan to run it, run another, and then reverse the booster. Phases: after/cleaning, troubleshooting, theory, safety/housekeeping, before (next-run preparation).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:09 | after/cleaning | "It's just cleaning up" — post-run clean-up of the cartridge parts at the bench, respirator and orange gloves on (keyframe). |
| 00:45 | after/cleaning | Something "comes down a little bit and stabilizes" (reading not named; start of a merged 00:45–06:53 segment). |
| 00:45 | after/cleaning | Thorough option: unscrew the plug, take the handle, open the valve fully "to get like a perfect access to the inside of the valve". |
| 00:45 | lesson | If the next material is similar, just clean the inside; even without opening, put paper in and move it around with tweezers. |
| 06:53 | after/cleaning | "Flush it a few times with isopropanol and it will be fine"; then put it back in the same place. |
| 06:53 | after/cleaning | Use compressed air to blow paper-towel dust off the seal; the lint sticks to the seal. |
| 06:53 | tools | Trainee asks about a separate compressed-air gun; Bartosz: put a T on the machine's air line and use this one, "somewhere in the corner". |
| 08:57 | after/cleaning | Refit: "find the spot where it is supposed to sit"; remark that it "definitely got hotter in here". |
| 08:57 | after/cleaning | "Everything is here, so it's just a pit stop and we start the process"; vacuum not needed — wiping suffices, vacuum for a better clean. |
| 12:32 | lesson | Deeper cleaning deferred ("later sounds fine") because "we're just doing aluminum again". |
| 12:59 | troubleshooting | Scan graph at the HMI (keyframe): "something is a little bit off" — a sign of a second peak causing resonance when the plate works. |
| 12:59 | troubleshooting | Plate is more sensitive and "can go up, then it stabilizes"; "fortunately, it's not breaking", it just heats up more. |
| 13:37 | theory | More heat gives faster atomization but is "a rather rough style"; 1:1 booster with the wider plate has a higher chance of resonance. |
| 13:37 | theory | With the reverse booster the resonance will disappear; "the ultrasonics are quite unpredictable". |
| 14:05 | theory | "We will try our best to have some kind of control over them"; recommends a resonator website (heard "pushasonicresonators.org") for reading. |
| 14:31 | theory | Tightening the piezo ceramic stacks raises stability "into infinity" in theory, but past some point they crack — hence the care with the stack. |
| 15:01 | theory | "Theoretically you should compress them as much as you want, but when you're actually doing it, it's not going to work." |
| 15:01 | safety | Trainee: comfortable without the full-face mask once no powder is around? Bartosz: wear it for the cleaning after the trials, then it's fine. |
| 15:01 | housekeeping | All the consumables are best stored in some kind of cabinet. |
| 15:27 | housekeeping | Keep the area clean: from time to time vacuum everything and wipe; small powder residues come from jarring powder out of the container. |
| 15:27 | housekeeping | Trainee: a cabinet dry box with desiccant to keep things drier; "we might pull in that big metal one" (cabinet, inferred). |
| 15:57 | before | Sample cup: keep it upright, plug at the top; filled "pretty much up to the top of this little cap"; furnace lid open (keyframe). |
| 16:50 | before | Filled with AlSi10Mg; a little hole in the top so air can come out — "who knows? We'll just need to test it". |
| 16:50 | before | Plan: another one the same way if time allows; Bartosz will also show how to reverse the booster "to show you the principles". |
| 17:19 | chatter | Trainee has somewhere to be and a class to teach; the run will "probably take about an hour". |
| 17:54 | chatter | "Oh, did I leave it? Oh, no. I thought I left it, didn't I?" — looking for a misplaced item. |

### Procedural steps
After / cleaning
- Unscrew the plug and take the handle off, then open the valve fully for access to its inside (00:45).
- If the next run is the same material, only clean the inside: push paper in and work it around with tweezers, even without opening the valve (00:45).
- Flush the part a few times with isopropanol (06:53).
- Put it back in the same place and blow paper-towel lint off the seal with compressed air (06:53).
- Refit the part by finding the spot where it is supposed to sit (08:57).
- Wipe the surfaces; reach for the vacuum cleaner only when a better clean is wanted (08:57).
- Wear the full-face mask for the post-trial cleaning; once no powder is around it can come off (15:01).
- Vacuum and wipe the whole area from time to time; expect small spills when jarring powder from the container (15:27).
- Store consumables in a cabinet, ideally a desiccant dry box (15:01, 15:27).
Before (next run)
- Read the ultrasonic scan for a second peak; if resonance shows with the 1:1 booster and wider plate, switch to the reverse booster (12:59, 13:37).
- Keep the AlSi10Mg sample cup upright with the plug on top; check in a test run whether the vent hole works (15:57, 16:50).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| isopropanol, "a few times" | flush of the cleaned cartridge/valve part | 06:53 |
| T fitting on the machine's compressed-air line | second air gun for cleaning | 06:53 |
| "aluminum again" | same material next, so deep cleaning can wait | 12:32 |
| second peak on the scan | resonance sign; plate heats more but is not breaking | 12:59 |
| 1:1 booster + wider plate | combination with a higher chance of resonance | 13:37 |
| reverse booster | makes the resonance disappear | 13:37 |
| AlSi10Mg | powder filling the sample cup; small vent hole in the top | 16:50 |
| ~1 hour | expected duration of the next run | 17:19 |

### Quotable moments
- "Sometimes even without opening it you can try to put some paper in, use the tweezers to like move it around." (00:45)
- "Flush it a few times with isopropanol and it will be fine." (06:53)
- "Everything is here, so it's just a pit stop and we start the [process]." (08:57)
- "The ultrasonics are quite unpredictable. We will try our best to have some kind of control over them." (13:37–14:05)
- "The more you tighten the piezo ceramic stacks, the stability of the whole system is going into infinity. But then if you go to some point … it will just crack." (14:31)

### Unclear / needs checking
- Which "cartridge": never named. The frame at 09:00 shows a flanged stainless body with a wire filter cage, a lever-handle valve, threaded studs and a wash bottle — a filter cartridge in a valve body (powder-container valve or exhaust filter?), not the main HEPA, whose removal T1 08:05 describes differently. Confirm from footage.
- Timing is coarse: the 00:45–06:53 and 08:57–12:32 segments each hold a few sentences, so the words may come minutes after the row's mm:ss.
- Mis-hearings: "pushasonicresonators.org" (an ultrasonic-resonator site; exact URL unknown), "upload paper" (read a paper?), "put it back in the same room" (same place), "auto consumables" (all the consumables).
- "The glass is sealed and then we have enough force to actually give up" (08:57) is garbled — possibly a gasket seating under clamp force.
- What "comes down a little bit and stabilizes" at 00:45 (pressure? scan frequency?) is unknown.
- Which trainee presents the sample cup (15:57) and who has the class to teach (17:19; probably Sterling, cf. LSQmxwmlTkQ).

## LSQmxwmlTkQ — Drill press, number 70 bit, graphite nozzle (4:14, Sep 30)

Four-minute machine-shop clip, published 10:05 MDT, three minutes after sgbaird's issue #222 comment that the description links to (photos of two drilled nozzles: "one of them I botched just a bit, the other one looks pretty nice"). Whisper returned a single VAD-merged segment spanning the whole 0:00–4:13 with only a few words of chatter — no spoken procedure, numbers or part names — so the drilling itself must be read from the footage. The keyframes show black-gloved hands holding a small part on the drill-press table (00:00), held under the chuck at 01:00–02:00, and bench work over a tray at 03:00 (keyframe; times from frames taken at the exact second). Phase: before/preparation — consumable prep, opening the graphite nozzle bore with a #70 wire-gauge bit (nominally 0.028 in ≈ 0.71 mm, a drill-gauge fact not spoken) from the as-shipped 0.5 mm toward ~0.7 mm (inferred from title and repo context).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:00 | preparation | Only speech in the clip (single 0:00–4:13 segment): "Going still? Got another one." — a second nozzle to drill (inferred). |
| 00:00 | chatter | "Yeah, that's hard to…"; "I might have to run to class in a couple seconds, sorry." "Perfect. Okay, thank you." |

### Procedural steps
- None spoken. (inferred from title and 00:00 keyframe) Hold the graphite nozzle on the drill-press table and open its bore with a #70 bit (00:00).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| #70 wire-gauge bit | per the title; nominal 0.028 in ≈ 0.71 mm (not spoken) | 00:00 |
| 2 nozzles | "Got another one"; issue #222 comment: one slightly botched, one nice | 00:00 |
| 0.5 → ~0.7 mm | nozzle bore before/after, from repo context, not this clip (inferred) | — |

### Quotable moments
- "Got another one." (00:00)
- "I might have to run to class in a couple seconds, sorry." (00:00)

### Unclear / needs checking
- Whisper merged the whole clip into one segment, so the mm:ss of these words is unknown (anywhere in 0:00–4:13); re-run with word timestamps or without VAD batching to place them.
- Nothing is said about speed, feed, backing material, depth stop or which side of the nozzle plate is drilled; only the footage and the issue #222 photos ("same side in each picture") can answer that.
- Who drills: the issue comment is by sgbaird ("one of them I botched"), so probably Sterling (inferred); the blue-shirted person at 03:00 is unidentified.
- The 0.5 mm → ~0.7 mm bore sizes come from repo context, not from this clip.

## u-KjR5TENN4 — The expert cleaning the atomizer, pov (18:45, Sep 30)

A body-worn POV recording, uploaded at 10:19 MDT on Sep 30, an hour before the cartridge-cleaning clip (f8KL31PN8bA), of the trainer cleaning the rePowder after a run. The orange gloves are the ones Bartosz wears in the cartridge clip, so "the expert" is presumably him (inferred). **There is no usable speech.** Whisper's voice-activity filter found none in the first pass. Re-run on Oct 3 without the filter (fixed 30 s windows, word timestamps), it returns 39 segments that are all stock hallucinations: "So, let's go." at exactly the same position near the end of several 30 s windows (00:57, 01:27, 02:27), "Thank you." six times, "Okay."/"so" fillers, and "I'm going to put it in the oven", "I love you", "I'm going to go ahead and cook". The transcript is kept in [`../transcripts/whisper/`](../transcripts/whisper/) as the record of that check, but nothing in it is indexed. The rows below are read from frames taken at the exact second: a printed sheet consulted under the machine, hands in orange gloves under and inside the chamber, the view port, a bench of tools, a wash bottle at the door seal, used paper into the bin. That is consistent with the brush/paper/IPA cleaning described in Video 4 05:41–09:17 and Video 2 41:12–55:12, which remain the spoken source for the procedure. Phases: after/cleaning (keyframe).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:00 | cleaning | (keyframe) Wide view of the rePowder before the clean: blue housing, the chamber with its round view port, the HMI on its arm, a grey bin. No speech anywhere in the video; the Whisper text is hallucination (see Unclear). |
| 00:30 | cleaning | (keyframe) POV under the machine: orange gloves holding a printed sheet by a black star knob; the sheet is consulted again at 01:00–01:30 and 04:00 (not readable at 360p). |
| 03:00 | cleaning | (keyframe) Both hands up under the chamber, working on a stainless flange with a tool. |
| 05:00 | cleaning | (keyframe) A long hand tool inside the stainless chamber and cone; hands inside it again at 06:00, wiping (inferred). |
| 07:00 | cleaning | (keyframe) View across the machine front: HMI on its arm, the grey bin. |
| 07:30 | cleaning | (keyframe) Holding a round stainless dome-shaped part over the container stand (the splash plate or the cone, unidentified). |
| 09:00 | cleaning | (keyframe) At a bench laid out with wrenches, pliers, polished stainless parts, paper towels and a wash bottle. |
| 10:30 | cleaning | (keyframe) Close-up of the view-port window (cleaning it, inferred from Video 1 44:11). |
| 11:00 | cleaning | (keyframe) Holding a round black spoked part over boxes (unidentified: a lid or hand-wheel). |
| 13:30 | cleaning | (keyframe) A blue-capped wash bottle at the chamber door's opening and seal (IPA on the seal, inferred from Video 4 06:51). |
| 15:00 | cleaning | (keyframe) Used paper into the bin; argon cylinders chained to the wall behind. |
| 15:30 | cleaning | (keyframe) Hands with paper at the top of the stainless powder container under the chamber. |
| 17:30 | cleaning | (keyframe) In front of the HMI with a long-handled tool; pliers on the shelf. |

### Procedural steps
- None spoken. The footage shows the post-run clean of the chamber underside, cone, view port, door seal and container top with paper, hand tools and a wash bottle (03:00–06:00, 10:30, 13:30, 15:30, keyframe); follow Video 4 05:41–09:17 and the SOP's cleaning section for the actual steps.

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| (none) | no speech, so nothing spoken to record | — |

### Quotable moments
- None: the only Whisper text is hallucination.

### Unclear / needs checking
- Hallucination check: with VAD, Whisper finds no speech; without it, every segment is filler ("So, let's go.", "Thank you.", "Okay.", "so") or a stock phrase unrelated to the scene. The repeated "So, let's go." sits at the same offset (27.18–29.98 s) in several 30 s windows, the signature of window-end hallucination. The opening "Let's do it." (00:02) could be real but says nothing: VAD at a low threshold (0.2) finds a single 1 s blip there (00:02.9–00:03.9) and nothing else in 18:45, and word-level re-runs of 00:00–00:06 return low-confidence filler that changes from run to run ("… … … Thank you." in the committed [`recheck-clips.json`](../transcripts/whisper/recheck-clips.json); an earlier run gave "Let's go. … How have you been?"), the signature of Whisper sampling on noise.
- What is being cleaned in each frame, and in what order, has to be read from the footage; the rows come from frames every 30 s, and many are blurred by head movement. The printed sheet (00:30–04:00) is presumably a cleaning checklist, not legible at 360p.
- Which run this follows (the Sep 29 last run or an early Sep 30 run) is not stated; the upload time puts it before the cartridge-cleaning clip and Video 7.

## prj_xgeuQtM — nzyjn0 AlSi10Mg-Al6063 dosing session (1:08:45, Sep 29)

A fixed vertical phone view of the powder-doser bench, uploaded at 17:59 MDT on Sep 29: the blue 3D-printed doser, a balance under a glass draft shield, tissues and paper. Per the title, this is the AlSi10Mg powder being dosed into the Al 6063 cup that became the nzyjn0 charge of the Sep 30 custom-charge run (TFpU4uqVF9c, issue #249). Not atomizer operation, but the charge preparation for it. **Almost no speech:** Whisper's voice-activity filter finds 5 s in 68 minutes, all in the first 19 s, and even at a much lower threshold (0.2) only 7 s, in the same place. The batched transcript has one line, "Let's see how this looks" (00:17); word-level re-runs of 00:00–00:25 come back with low-confidence fragments that change from run to run ("I … see how this" in the committed [`recheck-clips.json`](../transcripts/whisper/recheck-clips.json)), so nothing more can be read there. Everything else below is read from frames taken at the exact second, one per minute through the active stretches. Phases: before (charge preparation, keyframe).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:00 | dosing | (keyframe) Doser bench: blue 3D-printed doser with a tube mounted horizontally, balance under a glass draft shield. "Let's see how this looks" (00:17) is the only clear line in the video. |
| 07:00 | dosing | (keyframe) Paper and blue tools laid out at the back of the bench; a tube stands upright on it from 08:00. |
| 11:00 | dosing | (keyframe) Gloved hands at the back work on the upright tube (filling it, inferred), a white bottle beside it at 12:00–13:00 (the powder, inferred). |
| 14:00 | dosing | (keyframe) A gloved arm reaches across to the doser; at 15:00 a red-topped tube stands in the draft shield on the balance, and hands are at the doser again at 16:00. |
| 24:00 | dosing | (keyframe) A red-marked item in the draft shield; from here to 52:00 the frames do not change (dosing or waiting; the frames cannot tell). |
| 53:00 | after | (keyframe) Hands back at the doser; a red-marked part set down on the paper at 54:00. |
| 55:00 | after | (keyframe) The glass draft shield lifted off and set down in front; the balance pan bare. |
| 58:00 | after | (keyframe) An arm at the doser once more; the bench is still from there to the end. |

### Procedural steps
- None spoken. The footage shows the bench laid out, a tube filled and fitted, a part set in the draft shield on the balance, a long unchanged stretch, and the shield lifted off (07:00–55:00, keyframe). The spoken account of the same kind of dose is dXRB7c6GeDw below.

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| AlSi10Mg into Al 6063 | charge material and cup, from the title only | — |
| nzyjn0 | the charge ID in the title, the same as the Sep 30 run (TFpU4uqVF9c) | — |

### Quotable moments
- "Let's see how this looks." (00:17), the only clear line.

### Unclear / needs checking
- Speech check: VAD at the default threshold 0.5 finds 3 regions, 5.2 s in total; at 0.2, the same 3 regions, 7.1 s (00:09.5–00:18.9). Nothing after 00:19 is speech, so a run without VAD would only add hallucinated filler of the kind seen in u-KjR5TENN4 and QXSj0j1OqL8.
- How much powder went into the cup, and with what doser settings: neither is said or legible on the 360p frames; check the dosing logs for the nzyjn0 run.
- What the red-marked items are (a cap? tape on the cup?).

## dXRB7c6GeDw — Claude ping and troubleshooting for dosing Al 4047 (59:37, Oct 1)

A phone screen recording (uploaded 20:30 MDT on Sep 30, at the same time as BxA7Z9Fliss) of the GitHub pull request where Claude drives the powder doser, narrated while the dose runs. Sterling (the PR author, inferred from the "sgbaird commented" header on screen) is dosing the team's own atomized Al 4047 powder. Claude's comment headings on screen are "Dispensing 8 g of Al 4047", "Investigating the stalled Al 4047 dose", "Fixing the telemetry MemoryError, then re-running the 8 g Al 4047 dose" and "Finishing the Al 4047 dose at bulk tilt only (clog-tolerant)" (keyframes 00:59–38:59). The dose stalls at about 3 g; a MemoryError on the doser's Pico is fixed; larger particles in the atomized powder clog the auger nozzle, which "a larger auger inner channel" or sieving the powder first would avoid; the last tilt-back is too jarring and the tapping solenoid flexes on its one-sided 3D-printed mount. It ends with about 8 g dosed, a small amount of which is loaded into "the 6063 one end closed tube", the powder cup for the Oct 2 charge (inferred). Not atomizer operation, but the charge preparation for it. Whisper with word timestamps, so the times are within a second or two of the words. Phases: before (charge preparation), troubleshooting (doser), chatter.

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:59 | dosing | (keyframe) Phone screen: the PR thread, Claude's checklist "Dispensing 8 g of Al 4047". |
| 00:23 | dosing | "It looks like it's dosing now. Close to three grams at the moment. Looks like it's flowing pretty well … getting into the funnel." |
| 01:31 | troubleshooting | "I'm a little surprised that it stopped. Unless I didn't load enough in"; goes back through the doser's livestream to the last point it was pouring (01:49–02:02). |
| 02:06 | troubleshooting | On the replay: "going, going, going … still see it trickling … looks like it's tapping … and it stopped, even though it was still flowing powder." |
| 03:24 | dosing | Reads Claude's reply ("the new protocol it wrote"); "I'm screen recording my session here" (03:48). |
| 04:23 | chatter | A visitor asks what is being dosed: "the atomized" powder; "it was going great, and then it just stopped." |
| 04:55 | chatter | Stock delivered: "That's a solid 6063" — "what you ordered" (05:08). |
| 05:33 | chatter | "Just clean it with IPA is the only thing. You can throw both in if you want" (object not named). |
| 05:47 | dosing | Picks "medium … just for a faster response here" (the Claude effort setting, inferred; the sentence ends at 07:20). |
| 08:46 | troubleshooting | "Oh, memory error" — the telemetry MemoryError on the doser's Pico (keyframe 14:59 heading); "maybe I should get a Pico 2 … save my RAM. This should be quite solvable" (09:39). |
| 18:21 | chatter | Waiting without a laptop; card access has failed, so leaving means calling the engineering lab supervisor to get back in (19:32–19:45). |
| 23:14 | troubleshooting | Dose backed up: "some pieces maybe kind of stuck … in the nozzle area, some of those larger pieces." |
| 23:39 | lesson | "A larger auger inner channel would help with that, or me just sitting [sifting, inferred] it … like I probably should have"; "but it's still coming out" (24:02). |
| 25:24 | troubleshooting | Still getting powder, "just some bigger pieces in the middle there"; the cartridge "might just not be mated properly"; the back clamp could support it better (26:21–26:45). |
| 27:21 | lesson | "Those bigger chunks really gummed up the nozzle." |
| 29:48 | dosing | "Trying to get to 4.5, so it's actually kind of a ways away." |
| 38:59 | dosing | (keyframe) Claude's new plan: "Finishing the Al 4047 dose at bulk tilt only (clog-tolerant)". |
| 51:46 | dosing | Back on the livestream: "still got that skipping or whatever's going on with the meter"; the flow slows as it nears the target (52:05–52:26). |
| 52:40 | dosing | "Three, two, zero … pretty much spot on"; "that's the drift, which was just from the fume hood", which is not perfectly sealed; "overall, I'd say that's pretty good" (52:46). |
| 53:27 | lesson | A small extra amount came with "that last tilt back", which "could probably be a lot slower, less jarring." |
| 53:47 | lesson | "The solenoid actually bends a little bit when it hits, just because it's only fixtured on one side … to the 3D print, so actually cantilevers just a little bit." |
| 55:05 | before | "So I've got 8 grams. Take a small amount … load it into the 6063 one end closed tube" — the powder cup; "and I gotta go." |
| 58:56 | dosing | "Okay, we're finished"; the balance reading arrives, the auger rpm "came back up a little bit" (59:15); (keyframe 58:59) Claude's report with a plot. |

### Procedural steps
Before (charge preparation, powder doser)
- Watch the dose on the doser's livestream; if it stops, scrub back to the last point it poured (01:49).
- Sieve the atomized powder before dosing, or the larger particles clog the auger nozzle (23:39, inferred reading of "sitting").
- Check the cartridge is mated properly and supported by the back clamp (26:21, 26:32).
- Load the dosed powder into the Al 6063 one-end-closed tube (55:23).
Troubleshooting (doser)
- A MemoryError on the Pico stops the telemetry; the fix was made in firmware (08:46, keyframe 14:59).
- The last tilt-back should be slower; the tapping solenoid needs fixturing on both sides (53:36, 53:47).

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| ~3 g | dosed when the flow stalled ("close to three grams") | 00:27 |
| 4.5 (g, inferred) | interim target, "kind of a ways away" | 29:48 |
| 8 g | total dosed ("I've got 8 grams"; Claude's heading "Dispensing 8 g of Al 4047") | 55:09 |
| Al 6063, one end closed | the tube the powder goes into | 55:23 |

### Quotable moments
- "OK, and it stopped, even though it was still flowing powder." (02:25)
- "A larger auger inner channel would help with that, or me just sitting it with light amount, like I probably should have." (23:39)
- "Those bigger chunks really gummed up the nozzle." (27:21)
- "I noticed the solenoid actually bends a little bit when it hits, just because it's only fixtured on one side." (53:47)

### Unclear / needs checking
- "Sitting it with light amount" (23:52): read as sifting/sieving the powder (inferred); it could also mean loading a lighter amount.
- "Three, two, zero" (52:40): a balance reading or a countdown; the target was 8 g by Claude's heading, 4.5 at 29:48.
- Garbled: "Bioheap transfer" and "currently it's the drain" (03:39–03:45), "That's what Salmon will know about that" (29:07), "Load it into the 4047 aluminum" (55:15, presumably "load the 4047 aluminum into …").
- That the "small amount" loaded at 55:13 is the Oct 2 charge is inferred from the Oct 2 run (OCT2b 23:37: "definitely not a lot in there").
- The PR text on screen is legible only in outline at 360p; the PR itself (vertical-cloud-lab, "Optimization campaign: firmware tap …") is the record of the protocol and the fixes.

## QXSj0j1OqL8 — Dosing Al 4047 powder (22:15, Oct 1)

A fixed vertical phone view of the same powder-doser bench as prj_xgeuQtM, uploaded at 20:56 MDT on Sep 30, during or right after the Al 4047 dose narrated in dXRB7c6GeDw (inferred from the upload times). **No speech at all.** Whisper's voice-activity filter finds none, even at a threshold of 0.2. The Oct 3 run without the filter (30 s windows) returns 46 segments that are all hallucination: "so" in nearly every window, "Thank you." ×6, "We'll be back."/"We'll be right back." ×5, "I'm sorry." ×2, and the phrase "It's time to get to the end of the day" at 00:01. The transcript is kept as the record of that check; the rows below come from frames taken at the exact second, one per minute. Phases: before (charge preparation, keyframe).

### Timestamp log
| mm:ss | phase | what happens / what is said |
| --- | --- | --- |
| 00:00 | dosing | (keyframe) The camera settles on the doser bench: blue 3D-printed doser, balance with a glass draft shield, paper with blue tools, jars, a wash bottle. No speech in the video; the Whisper text is hallucination (see Unclear). |
| 02:00 | dosing | (keyframe) A gloved hand works at the back of the bench; an empty tube stands upright on the paper. |
| 04:00 | dosing | (keyframe) Gloved hands place something in the draft shield on the balance. |
| 12:00 | dosing | (keyframe) Gloved hands at the back hold a small tube upright, through 15:00 (filling it, inferred). |
| 17:00 | dosing | (keyframe) A blue-and-white tube (the powder cartridge, inferred) fitted to the doser by hand. |
| 18:00 | dosing | (keyframe) The cartridge sits in the doser above the balance; the scene stays still to 20:00. |
| 21:00 | dosing | (keyframe) A gloved hand at the balance; a clear cover lifted at the back. |
| 22:00 | dosing | (keyframe) Last frame: the cartridge in place over the balance. |

### Procedural steps
- None spoken; see dXRB7c6GeDw for the narrated dose.

### Parameters and numbers
| value | context | mm:ss |
| --- | --- | --- |
| Al 4047 | powder being dosed, from the title only | — |

### Quotable moments
- None: the only Whisper text is hallucination.

### Unclear / needs checking
- Hallucination check: VAD finds no speech at either threshold (0.5 or 0.2). The no-VAD transcript's stock phrases fall at the starts and ends of 30 s windows, as in u-KjR5TENN4.
- Whether this is the camera side of the dXRB7c6GeDw session or a separate later dose: the uploads are 26 minutes apart, and nothing on screen dates the frames.
