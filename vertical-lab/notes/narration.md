# The narration's pronunciation, checked line by line (round 13, run D)

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
[`out/narration/lines.ogg`](../out/narration/lines.ogg), all 55 lines in order with a second between, to listen to
(9.3 min, 2.3 MB). The comparison writes numbers as words, merges letters said one by one (U P S = UPS), and takes
metre/meter and similar spellings as the same.

**This round's result:** mean word error 1.3 % (small.en) and 2.6 % (base.en); 40 and 34 of the 55 lines word-perfect.
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
- **Written forms** in eight more lines (VLM, UPS, OT-2, CubXL, SEM, wire EDM, MX-Lab).
