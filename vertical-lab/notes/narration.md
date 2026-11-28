# The narration's pronunciation, checked line by line (round 14, run D)

Sterling on round 12's video (PR #318, 2026-11-20): "Potentiostat is mispronounced in the narration. Look for other
hiccups like that in the narration. 'MiR' should be pronounced 'meer' (common pronunciation)."

## How the lines are spoken now

`narration.json` holds each line **as it should read in the subtitles**: OT-2, CubXL, SEM, ICP-MS, MiR250, UPS, VLM,
EDM, BYU. Round 12 had spelled these out for the voice ("the O T two", "a V L M"), so the subtitles read that way too.
`longform.py` now turns each line into what the voice says in two steps:

1. **`SAY`** respells a written form as text: `OT-2` → "O T two", `UPS` → "U P S", `MiR250` → "MiR two-fifty",
   `UR12e` → "U R twelve E", `HNO3` → "nitric acid", `aluminium` → "aluminum" (the voice is American).
2. **`IPA`** gives the phonemes of the words no respelling fixes, through Kokoro's phoneme input (`is_phonemes=True`);
   everything else keeps the phonemes espeak gives it:

| Word | espeak's own reading | Now | Heard back |
|---|---|---|---|
| potentiostat | pətˈɛntɪˌɑːstæt, "puh-TEN-tee-AH-stat" | pətˌɛnʃiəstˈæt, "puh-ten-shee-uh-STAT" | "potentiostat" (small.en) |
| MiR | mˈaɪ ˈɑːɹ, "my R"; respelled "meer", mˈɪɹ, it came back "mirror" before a consonant | mˈiːɹ, "meer" | "MiR 250" / "mere 250" |
| doser | dˈoʊzɚ, heard back as "dozer" | dˈoʊsɚ, "DOH-ser" | "doser" |
| Vertiv | vˈɜːɾɪv (a flapped t), heard back as "verdive" | vˈɜːtɪv | "vertive" |
| Instron | ɪnstɹˈɑːn, "in-STRON" | ˈɪnstɹɑːn, "IN-stron" | (not in a line yet) |
| Stäubli | stˈɛʌbli | ʃtˈɔɪbli, "SHTOY-blee" | (not in a line yet) |

Two lines were reworded rather than respelled, where the recognizer misheard a word said correctly: "depowdered" came
back as "de-powered", so chapter 5's line says "cleared of powder"; "recoating", with an American flapped t, came back
as "recoding", so the BN line says "the recoat happens".

The cache in `/tmp/longform_tts` is keyed on the phonemes, so changing `SAY` or `IPA` re-speaks only the lines it
touches. The subtitles (`out/longform_narration.srt`, written when the long-form is built) take the written text, the
audio the spoken form, from the same line: they can't drift apart.

## The check

```
python3 longform.py narration-check      # every line spoken, then heard back by faster-whisper base.en and small.en
```

It writes [`out/narration/check.json`](../out/narration/check.json) (per line: the text, what is spoken, the phonemes,
what each model heard, the word error rate, each difference, and the words heard with less than 50 % confidence) and
[`out/narration/lines.ogg`](../out/narration/lines.ogg), all 56 lines in order with a second between, to listen to
(9.7 min of speech, 2.4 MB). The comparison writes numbers as words, merges letters said one by one (U P S = UPS), and takes
metre/meter and similar spellings as the same.

**This round's result:** mean word error 1.4 % (small.en) and 2.8 % (base.en); 38 and 33 of the 56 lines word-perfect.
Every remaining difference is a number written another way ("a hundred" as "one hundred", "250" as "two hundred and
fifty"), a homophone ("Kardex" as "Cardex", "missed" as "mist"), or "round" heard as "around". The machine check
catches a wrong word, not a wrong stress: "potentiostat" was transcribed correctly in round 12 too, so the stressed and
unusual words were also read off espeak's phonemes one by one (all 690 distinct words in the narration).

## What changed in the lines

- **11:43, the 17-step card:** "This is the alloy lab's workflow today, seventeen steps, mostly by hand" is now "The
  alloy lab's seventeen steps, and what this design does with each: fifteen are automated and shown in this video, two
  have no station yet, and the last column lists what still takes a person." The card itself was redrawn the same way
  (`notes/dal_workflow.md`).
- **The ICP-MS:** the OT-2's dilution line now says the step moves to the ICP-MS station on the floor, with its own fume
  hood, so no acid rides on a tray; a line was added for the station's clip (`notes/icpms.md`).
- **The atomizer:** the card's line no longer says one arm holds the lid while the other works the latch (run C is
  deciding whether the lid hold stays); the latch line no longer begins "The arm no longer swings the loop", which only
  made sense next to the round before; the BN line no longer quotes the old card's "stayed manual".
- **Run B's dose post:** the line over chapter 1's figure said the cup can't come closer to the outlet. Run B's
  dose post and draft shield bring it to 45 mm (from 153), so the line and the figure (`out/doser_shield_section.png`,
  in place of `doser_raise_section.png`) now say that.
- **Run C's chapter 2:** the stack line now says the two arms build the stack between runs. That line and the
  container, latch and powder lines anchor on a phrase of their sub-step's caption (`"match"` in `narration.json`), not
  only an index, so they follow the chapter as it changes.
- **Written forms** in eight more lines (VLM, UPS, OT-2, CubXL, SEM, wire EDM, MX-Lab).

## Round 15: the merged PRs' lines (PR #318, 2026-11-23)

Sterling: "pull in the latest results from all the other relevant PRs ... and re-render everything in a self-consistent
and cohesive way". The long-form gained two chapters (safety; the floor and the waste) and parts in four others
(services, corrosion, chapter 1, the stations), and `narration.json` 19 lines (75 in all), each tied to its notes file
in its `source`. Three parts without a line were left out to hold the length (about 90 min): the docks-against-the-lift
still, round 6's collision before-and-after, and `floor_day.mp4`.

| Where | The line says (what the picture doesn't) | Source |
|---|---|---|
| services, `base_cameras` | three cameras per base, after robot-arms' cell; they check the docking and watch the arm; none is a safety device | notes/base_cameras.md |
| services, `security_cameras_bay.png` | security cameras costed, about $9-19k for the lab; most PTZs don't fit under the bay's roof | notes/security_cameras.md |
| safety, card | a metal fire needs Class D, not water or CO2; one within 4 m of every powder station, one on each base | notes/safety.md |
| safety, `safety` (On every MiR250) | the turning circle grows 5 mm; 3 kg of payload left with the arm at full load | out/safety.json |
| safety, `safety_other_assets.png` | the ordinary units 4 m or more from Class D, signed differently; BYU EHS still to confirm | notes/safety.md |
| corrosion, `cubxl_corrosion` (the P300) | the P300 on its lift is a proposal: 33 transfers become 6; DAL's protocol unchanged | notes/cubxl_pipettes.md |
| corrosion, `cubxl_evap.png` | 1-3 % of the water a spot, but the metal sees about a tenth of the sulfide unless mixed or sealed | notes/cubxl_pipettes.md |
| chapter 1, `machining_cell` (twice) | nothing else here can turn a cup, so the cell is new; IPA in closed vessels in the baths' water, alcohol the only lubricant, Al and Cu on separate days | notes/machining.md |
| chapter 1, `machining_sim.png` | about 114 pairs a day against 67; the dryer and baskets set the pace; stoppage rates estimated | out/machining_sim.json |
| chapter 1, `ext/doser_drop_v10.mp4` | powder-doser's own render of v10, the beaker 18 mm under the exit; this lab's animation still has v5 and the dose post | out/mp4/ext/credits.json |
| stations, `naming/floor_names.png` | a proposal: stones whose property is their job, the Shuttles Timp and Nebo | notes/naming.md |
| stations, `colour/bench.png` | colour only where a person decides; blue Al, orange Cu, always with a word, checked for colour-blind readers | notes/colour_coding.md |
| floor, card | no cleaning robot is rated for metal dust; an option explored, for the dust hazard analysis to decide | notes/floor_cleaning.md |
| floor, `floor_clean_people` (the spill) | a visible spill is a person's job: the robot stops and messages them; broom for the bulk, the robot for the residue | notes/floor_cleaning.md |
| floor, `floor_pass` (twice) | 53 spots, 45 studs, bonding at each doubles the model's 43 min; its two spills are illustrations | out/floor_pass.json |
| floor, `waste_streams.png` | the largest hazardous stream is the unused coarse powder, three quarters of a run; undecided; modelled, not weighed | notes/waste.md |
| floor, `waste_station_still.png` | hazardous waste leaves through BYU Risk Management's pickups, monthly at one a day, every week or two at ten | notes/waste.md |

**Changed:** this round's OT-2 clip no longer dilutes the ICP-MS tubes (`ot2_corrosion.py`: no acid on its deck; the
CubXL acidifies its own tubes and the capped tubes go to the ICP-MS station). The OT-2's line over the dilution ("One
part sample to nine of dilute nitric acid ...") is now on the clip's last step, "No acid on this deck": the OT-2's maker
says to keep corrosive materials away from it, so its deck holds only seawater and sulfide, and the tenfold dilution is
made at the station, in its own hood. The corrosion card's line says "the OT-2 makes up the sulfide stock" (it said
"solutions and dilutions"). Chapter 1's card line now starts the charge from "cups turned from bar". The checks
chapter's last line anchors on `collisions/round15_table.png` (`python3 longform.py audit` draws it once the pass is
rendered; until then that one line is left out). Four of round 14's lines (setup_lab's loading, the OT-2's dilution,
the CubXL's potentiostat, the atomizer's keys) now also anchor on a phrase of their sub-step's caption (`"match"`), as
the new lines on clips with sub-steps do, since those clips were being re-rendered with new steps.

**Anchors:** `base_cameras` (joined from two renders) and the 2-D `floor_pass` have no sub-steps, so their lines give
`"at"`, seconds into the clip; a line on another project's render or on footage names the file (`ext/...mp4`).

**Pronunciation:** `IPA` (isopropyl alcohol) is said from phonemes, `ˌaɪpˌiːˈeɪ`: respelled "I P A", espeak read the last
letter as the article "uh". `PTZ` is respelled "P T Z". "powder-doser" is written "powder doser" in its line, so the
`doser` fix (`dˈoʊsɚ`) reaches it; with the hyphen espeak said "dozer". Ready for later lines, not yet spoken:
`CombiTac` `kˈɑːmbitˌæk` (espeak: "kum-BYE tack") and `Haas` `hˈɑːs` (espeak: "hahz"). Amerex, Nilfisk, Provo, Timp
and Nebo are read right by espeak as they are.

**The check** (`python3 longform.py narration-check --new ea5d9d5`: only the lines whose phonemes differ from round
14's, into [`out/narration/check_new.json`](../out/narration/check_new.json) and
[`lines_new.ogg`](../out/narration/lines_new.ogg)): 22 lines, 4.5 min; mean word error 2.6 % (small.en) and 2.5 %
(base.en), 14 and 12 of 22 word-perfect. What remains is numbers written another way ("nine to nineteen thousand
dollars" as "$9,000 to $19,000"), homophones ("MiR" as "mere", "too coarse" as "two course"), "fluorite" as "Fleurite"
(base.en only), "planned" as "plant" (base.en only) and "pickups" as "pick-ups". "BYU's" before "Risk Management"
came back as "BY use", so that line says "BYU Risk Management's". "Timp" was heard right in this sentence;
notes/naming.md found it heard as "temp" after "to".
