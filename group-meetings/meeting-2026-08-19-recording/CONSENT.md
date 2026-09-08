# Consent and publication ledger — AI in the lab, 2026-08-19

**Status: nothing here has been published, and no one in it has signed off yet.** Every
rendered artifact lives on a *draft* GitHub release, visible only to repository
collaborators. This file exists because the evidence review in
[`best-practices/`](best-practices/) found that the one thing this project had no record of
was consent (finding 9), and a ledger nobody can point at is the same as no ledger.

## Why a written trail, and not just "everyone was in the room"

The ethics literature the review surveyed is consistent on four points, none of which are
satisfied by having recorded the meeting with everyone's knowledge:

1. **Consent must be specific about dissemination** — *this clip*, *this platform*,
   *this audience*, *indefinitely*. Agreeing to be recorded for the lab is not agreeing to
   appear in a public YouTube Short.
2. **It should be tiered.** "Yes to the internal archive, no to social" has to be a
   possible answer, and it has to be a cheap one to give.
3. **It should be ongoing, not one-time.** People may withdraw later, including after
   publication.
4. **Where there is a PI/student power differential, voluntariness is the thing to
   protect.** Consent is best collected by someone other than the PI, and the ask should
   state in as many words that declining carries no consequence.

## What each person is in, and how they appear

Derived from [`reels/reels-edl.json`](reels/reels-edl.json) and
[`highlights/edl.json`](highlights/edl.json); regenerate with the snippet at the bottom.

| Person | Appears in | On screen as | Consent asked | Response |
|---|---|---|---|---|
| Sterling Baird (PI) | reels 03, 06, 07; highlights | footage (room camera + screen share) and text cards | — | — |
| Carl Robison | reels 05, 06, 07; highlights | text cards only (he was camera-off in Teams) | not yet | — |
| Audrey Christiansen | reels 05, 07; highlights | footage (Teams camera) and text cards | not yet | — |
| Xavier Zaitzeff | reel 04, 07; highlights | footage (his clip has real framing) | not yet | — |
| Sam Charles | reel 04, 07; highlights | footage (same clip) | not yet | — |
| Andrew | reels 01, 07; highlights | audio only + the "Don't film me" footage — **see the hold below** | not yet | — |
| Marcus | reels 01, 07; highlights | audio only (phone face-up) | not yet | — |
| Gage Erickson | reels 02, 07; highlights | footage in the Short, audio elsewhere | not yet | — |
| Ronnie | reels 02, 07; highlights | footage in the Short, audio elsewhere | not yet | — |
| Ben Whitney | reels 03, 07; highlights | audio only (phone face-up) | not yet | — |

Rows labelled `In the room:` in the reels are deliberately unattributed: the room shares one
Teams channel and the diarization could not place those lines on a single person. They are
still someone's words — they are covered by the ask, not exempt from it.

## One hold that should block publication on its own

**Reel 01 opens on Andrew saying "Don't film me."** His clip is audio-only precisely because
of that, which honours the request in the sense that matters. But using the line itself as a
cold open is a separate decision, and it is his to make rather than ours. Until he says yes
specifically to that item, reel 01 should not leave draft. Everything else in the set can be
cleared person by person.

## What the ask has to disclose

The clips are edited in ways that change how people sound, and the review found **no
published guidance** on the ethics of that — which is a reason to disclose it plainly rather
than a reason to skip it:

- **Filler words, false starts and pauses are cut** inside a sentence, so a bite is more
  fluent than the person actually was. The keep-intervals are in the EDL, word by word.
- **Background noise is reduced** (`highpass → RNNoise → afftdn → presence → lowpass →
  compression`), which slightly changes voice timbre.
- **Loudness is normalized** to −14 LUFS (reels) / −16 LUFS (long-form).
- **Quotes are burned on screen verbatim**, apart from the display-only spelling fixes
  recorded in the EDL (`"clot" → "Claude"`, `"Bow Torch" → "BoTorch"`).
- Speaker labels come from an automated diarization that is right most of the time and
  says `In the room:` when it isn't sure.

## The process to run before anything leaves draft

1. Someone **other than Sterling** sends each person a link to the specific items they are
   in (the draft-release MP4s plus a timecode), not to the set as a whole.
2. The ask names the destination explicitly: *public YouTube / Shorts / Reels / TikTok on
   the BYU Vertical Cloud Lab channel, indefinitely, worldwide.*
3. The tiers offered are: **public** · **internal/unlisted only** · **audio only, no
   footage** · **no**. Declining any tier is recorded and honoured with no follow-up.
4. Each answer is written into the table above and into
   [`consent-ledger.json`](consent-ledger.json), with the date.
5. Withdrawal stays open afterwards: a request to pull an item removes it from the EDL and
   the set is re-rendered.

Regenerate the "appears in" column from the EDLs:

```bash
python3 - <<'PY'
import json, collections
r = json.load(open("reels/reels-edl.json"))
per = collections.defaultdict(lambda: {"reels": set(), "visual": set()})
for reel in r["reels"]:
    for it in reel["items"]:
        for a, b, lab in (it.get("speaker_spans") or [[0, 0, it.get("speaker", "?")]]):
            nm = (lab or "?").rstrip(":").strip()
            per[nm]["reels"].add(reel["id"][:7])
            per[nm]["visual"].add(it.get("visual", "card"))
for k, v in sorted(per.items()):
    print(f"{k:<24} {sorted(v['reels'])} {sorted(v['visual'])}")
PY
```
