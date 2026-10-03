# Group E — Whisper transcripts: cartridge cleaning and #70 drill bit on a graphite nozzle (Sep 30 2026)

Source: faster-whisper large-v3-turbo (int8, batched, VAD) transcripts at `/tmp/work/transcripts/<id>.txt`; neither video has YouTube auto-captions. Both are speech-sparse: the VAD batching merged minutes of silence and scattered talk into single segments (e.g. 00:45–06:53 in the cartridge video, the whole 0:00–4:13 of the drill clip), so a row's mm:ss is the segment start and the words can come well after it. Speaker attribution is inferred (Bartosz = technical explanations; the trainee "with a class to teach" is probably Sterling). Items marked "(inferred)" are not said on camera; "(keyframe)" means read from the keyframe sheet, not from speech. Mis-hearings normalised in the text: "octatonics" = ultrasonics, "wider play" = wider plate, "start the forces" = start the process, "ALSI-10MG" = AlSi10Mg.

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
- Which "cartridge": never named. The 08:00 keyframe shows a flanged stainless body with a wire filter cage, a lever-handle valve, threaded studs and a wash bottle — a filter cartridge in a valve body (powder-container valve or exhaust filter?), not the main HEPA, whose removal T1 08:05 describes differently. Confirm from footage.
- Timing is coarse: the 00:45–06:53 and 08:57–12:32 segments each hold a few sentences, so the words may come minutes after the row's mm:ss.
- Mis-hearings: "pushasonicresonators.org" (an ultrasonic-resonator site; exact URL unknown), "upload paper" (read a paper?), "put it back in the same room" (same place), "auto consumables" (all the consumables).
- "The glass is sealed and then we have enough force to actually give up" (08:57) is garbled — possibly a gasket seating under clamp force.
- What "comes down a little bit and stabilizes" at 00:45 (pressure? scan frequency?) is unknown.
- Which trainee presents the sample cup (15:57) and who has the class to teach (17:19; probably Sterling, cf. LSQmxwmlTkQ).

## LSQmxwmlTkQ — Drill press, number 70 bit, graphite nozzle (4:14, Sep 30)

Four-minute machine-shop clip, published 10:05 MDT, three minutes after sgbaird's issue #222 comment that the description links to (photos of two drilled nozzles: "one of them I botched just a bit, the other one looks pretty nice"). Whisper returned a single VAD-merged segment spanning the whole 0:00–4:13 with only a few words of chatter — no spoken procedure, numbers or part names — so the drilling itself must be read from the footage. The keyframes show a black-gloved hand holding a small part on the drill-press table under the chuck (00:00) and bench work over a tray (02:00) (keyframe). Phase: before/preparation — consumable prep, opening the graphite nozzle bore with a #70 wire-gauge bit (nominally 0.028 in ≈ 0.71 mm, a drill-gauge fact not spoken) from the as-shipped 0.5 mm toward ~0.7 mm (inferred from title and repo context).

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
- Who drills: the issue comment is by sgbaird ("one of them I botched"), so probably Sterling (inferred); the blue-shirted person at 02:00 is unidentified.
- The 0.5 mm → ~0.7 mm bore sizes come from repo context, not from this clip.
