# Best practices for the AI-in-the-lab videos — evidence review and self-audit

What the research literature actually supports for the two formats produced in
[PR #184](https://github.com/vertical-cloud-lab/byu-vcl/pull/184) — the seven vertical
[reels](../reels/) and the 9:57 long-form [highlights](../highlights/) cut — and how the
current renders measure up against it.

Two sources feed this:

1. **An Edison Scientific literature review** (`LITERATURE_HIGH` / paperqa3-high, task
   `2f626e42-282b-4c7f-a8a9-61f2974e0e26`, ~28 min, 94 evidence contexts, 51 used,
   50 citations). Full prompt in [`query.txt`](query.txt); the answer in
   [`edison-answer.md`](edison-answer.md) and, with inline citations rendered,
   [`edison-formatted-answer.md`](edison-formatted-answer.md); bibliography in
   [`edison-references.md`](edison-references.md); complete raw trajectory response in
   [`edison-response.json`](edison-response.json).
2. **Measurements of our own artifacts** — the EDLs, the renderer constants, and the
   sidecar caption files in this repo. Every number in the audit below is reproducible
   from committed files; the commands are in [Reproducing the audit](#reproducing-the-audit).

## The evidence, in brief

Effect sizes are Cohen's *d* unless noted. "Strong" means meta-analytic or multi-experiment
support; "gap" means the literature does not answer the question.

| Question | What the evidence says | Strength |
|---|---|---|
| **How long?** | Median engagement with instructional video peaks near **6 min** regardless of total length; past ~9 min viewers watch only the first half (Guo, Kim & Rubin 2014, 6.9 M sessions). Replicated in a flipped medical classroom: embedded-question response rate falls **56 % → 31 %** from <3 min to >12 min. For short-form sci-comm specifically, lecture-style works best at **~1 min**, demonstration-style at **~30 s** | Observational, large-N |
| **Chapters?** | Segmenting is one of the largest effects in multimedia learning, **d = 0.98**. Chapter navigation alone lifts median engagement to ~10.8 min | Strong |
| **Signposting (titles, speaker labels)?** | Signaling: **d = 0.41**, 25/29 tests positive | Strong |
| **Background music?** | Adding music/ambient sound to narrated content *hurts* transfer, **d = 1.11**. Coherence generally **d = 0.86**, 22–23/23 tests | Strong — clearest "don't" in the review |
| **Verbatim text + speech at the same time?** | Mayer's redundancy principle (**d = 0.86**) argues against it — *but its boundary conditions are exactly our case.* With **no competing visual**, with **short segmented chunks synchronized to narration**, and for **L2/HoH viewers**, redundancy does not harm and can help. Subtitle research (AVT) generally finds no added load and better test performance | Strong, with well-mapped exceptions |
| **Word-by-word kinetic reveal?** | Theoretically defensible (sequential presentation mirrors oral flow; motion attracts attention when static text dominates) but **no controlled study compares karaoke-style reveal to static blocks for comprehension of informational video** | **Gap** |
| **How fast can you cut?** | First controlled study of short-form cut rate (Dost & Huang 2026) benchmarks real TikTok at **0.189–0.517 cuts/s**. Visible jump cuts help *completion* via prediction-error attention, but the benefit attenuates at high frequency; **higher transition frequency reduces sustained engagement overall**. Treat **~0.5 cuts/s as a ceiling** | Single controlled study |
| **Cut the "um"s?** | Genuine trade-off. Filled pauses *help* real-time comprehension — listeners recognize the next word faster after "uh" than when it is digitally removed (Fox Tree 2002) — but *hurt* credibility: disfluent speakers are judged less honest, less certain, less ready, and are less often chosen to work with again. **Perceived expertise buffers this** (disfluent experts read as "careful"; disfluent novices don't) | Strong for audio; **gap** for edited video |
| **Does showing a face help?** | Less than people assume. Instructor presence: **d = 0.20** for a static image (only 9/14 positive), **d = 0.36** for dynamic gesture. Meta-analyses find **no significant learning gain**, higher cognitive load, higher motivation and satisfaction. Learners *believe* they learn more when they see a face; they don't measurably | Moderate, consistent |
| **Does audio quality matter?** | The single most actionable finding. Poor audio lowers credibility (**d = 0.32–0.55**), impairs **memory for the stated facts** (**d = 0.44**), and makes evidence count for less. PNAS 2025: simulated bad-microphone "tinny" speech lowered judgments of intelligence, hireability and credibility **even with comprehension held equal**, robust across speaker gender, accent, and synthetic voices. Mechanism is processing fluency — listeners blame the *speaker*, not the mic | Strong, N = 593 + replications |
| **Is unpolished good?** | Only in the persona, never in the signal. Entertainment value predicts sci-comm success better than production quality, and authenticity beats authority markers — but "low-fi production increases credibility" is **unsupported**, and the fluency literature says the opposite. Correct synthesis: **invest in audio, don't over-polish the people** | Mixed; the popular claim is unsupported |
| **Do short-form science videos actually work?** | Engagement, yes. Learning, unknown: **no published controlled study shows a 60-second science reel produces measurable knowledge gain or attitude change.** All the evidence is content analyses, surveys and platform analytics. Whether lab-culture content drives recruitment decisions is unmeasured | **Gap — flagged as a commonly overstated claim** |
| **Captions and accessibility** | WCAG 2.2 AA: 4.5:1 contrast (3:1 for large text); captions must be accurate, synchronous, complete, properly placed, and **identify speakers**. Reading rate ≈ **15 CPS preferred**, 20 CPS max; BBC line limit **37 chars**, Netflix 42. Vertical safe area ≈ central 80 %, with platform UI over roughly the bottom 20 % and top 10 % | Standards, not experiments |
| **Consent** | Consent must be **specific about dissemination** (how, when, to whom), **tiered**, and **ongoing rather than one-time**; participants should be able to **review their clips before publication and withdraw**; with a PI/student power differential, consent is best collected by someone other than the PI, with explicit no-consequences-for-refusal. A recorded "don't film me" must be honored **absolutely** | Consistent across the ethics literature |

Two things the review explicitly could **not** find, which are worth knowing before anyone
cites them: no peer-reviewed study on whether **ML denoisers (RNNoise-style) damage quiet
speech**, and no published guidance on **the ethics of disfluency removal changing how a
person sounds** when republished. Both are areas where this project is ahead of the
literature rather than behind it.

## How the current renders measure up

### Already right, and worth not breaking

| Practice | Evidence | Our state |
|---|---|---|
| No background music | Strongest "don't" in the review (d = 1.11) | **None anywhere.** Both formats are speech-only |
| Chapters on long-form | Segmenting, d = 0.98 | 10 chapters over 9:57; reel 07 carries a chapters sidecar |
| Cut rate under the ceiling | ~0.5 cuts/s ceiling; TikTok band 0.189–0.517 | **0.12–0.24 cuts/s** (7.0–14.1 per min). Inside the band at the calm end — no change needed |
| Speaker labels | Signaling, d = 0.41 | Grayed `Name:`, following the diarized speaker within a bite |
| Text-on-black for audio-only bites | The exact redundancy boundary condition where verbatim text is safe | Black canvas, no competing visual |
| Reel length | ~30–60 s for short-form sci-comm | Five pair reels 0:47–0:53 |
| Reels loudness | ~−14 LUFS streaming target | `I=-14:TP=-1.2:LRA=11`, two-pass, measured −14.3 to −15.4 |
| Honest attribution | — | v2 downgraded inferred names to `In the room:` where diarization couldn't support them |

### Findings

Ordered by expected impact. Every one is measured from a committed file.

**1. The long-form cut is delivered at 16 kHz mono, 96 kbps, undenoised.**
[`highlights/edl.json`](../highlights/edl.json) sets `"audio": {"rate": 16000, "channels": 1}`,
and [`make_highlights.py:183`](../highlights/make_highlights.py) encodes
`-c:a aac -b:a 96k -ar 16000 -ac 1`. A 16 kHz sample rate is an **8 kHz hard ceiling on
audio bandwidth** — telephone-grade, with all sibilance gone — and the noise-reduction chain
built for the reels was never ported. This is the artifact most likely to be watched by an
external or prospective-student audience, and it has the worst audio in the set. It sits
directly on the strongest experimental result in the whole review: degraded audio costs
credibility (d = 0.32–0.55) *and* memory for the facts being stated (d = 0.44), with the
penalty attributed to the speaker rather than the recording. The reels already do this right
(48 kHz, 160 kbps, full denoise chain).

**2. Every reel spends its first 2.4–3.0 s on a silent branded title card.**
`make_reels.py:589` renders `card_title` before item 0, at `dur` 2.4 s (3.0 s for reel 07),
with a 2.6–3.0 s end card after. On a 47-second pair reel that is **~10 % of runtime with no
voice**, and it lands squarely in the window where the retention decision is made. The
evidence for the "first 3 seconds" rule is platform analytics rather than controlled study —
the review says so plainly — but nothing in the literature argues *for* opening on branding,
and Kim et al.'s finding that 61 % of viewership peaks coincide with visual transitions
argues for putting the strongest content where attention is. The material to open on is
already in the EDL: reel 01's "Don't film me", reel 04's *"if you asked me to do it myself,
I couldn't"*.

**3. 53 % of caption cues overlap the preceding cue.**
93 of 177 cues across the seven sidecar `.vtt` files start **before the previous cue ends**,
by up to 0.33 s. Cause: the sidecar writer (`make_reels.py:645`) sets each cue's end to
`last_word_end + 0.3` without clamping to the next phrase's start. Overlapping cues are
ill-defined in WebVTT and are handled inconsistently by players and by YouTube's caption
ingest. One-line fix — clamp the end to `min(next_phrase_start, last_word_end + 0.3)`.

**4. The sidecar captions violate every subtitle standard on line length and rate.**
Cue lines run to **81 characters on a single line** (BBC: 37; Netflix: 42), and **74 of 177
cues exceed 17 CPS**, with reel 02 at a median of 21.0 CPS and a 90th percentile of 29.4 CPS
against the 15 CPS accessibility preference. This does not affect the burned-in text — that
is separately wrapped to a 924 px measure and revealed in sync — but it makes the `.vtt`
files unusable as real caption tracks, which is the form a deaf or hard-of-hearing viewer
would actually consume. Related: **no cue carries a speaker tag**, though WCAG 1.2.2 requires
captions to identify speakers, and the burned-in render already knows who is talking.

**5. The quote block reaches into the platform UI zones.**
The renderer places the quote at `QUOTE_Y = 1158` in a 1920-tall frame, with a measure from
x = 78 to x = 1002, auto-fitting down from 118 px until the phrase fits **four lines**. A
four-line quote at base size therefore ends near **y ≈ 1724**, 196 px off the bottom; at
86 px it ends near y ≈ 1570. Approximate UI overlays are ~1600+ on Shorts, ~1490+ on Reels,
~1440+ on TikTok — so multi-line quotes at the larger sizes sit under the caption/handle
strip on all three. Horizontally, the measure's right edge at x = 1002 is inside the
right-hand action-button column (~860–900 px on Reels/TikTok), so the last ~100–140 px of
every long line sits behind the like/comment/share buttons. Four-line layouts are common
because four lines is exactly what the auto-fit targets. (Platform overlay extents are
industry figures, not measured on device — worth confirming on a phone before re-cutting.)

**6. Reel 03 never shows a person, and reel 07 is 10/14 text cards.**
`reel-03-ben-sterling` is 5/5 `card` items. The instructor-presence literature says faces do
not reliably improve *learning* — so this is not a comprehension problem — but they do raise
satisfaction and perceived learning, and this is recruiting-adjacent content where social
presence is the point. The v3 pass already proved the move: five items were switched to real
footage with no cut changed. Cheap mitigations the review names for audio-only material: a
static photo of the speaker, and high voice quality (which reels already have).

**7. Text-over-footage is where redundancy actually bites.**
The v3 items that put the screen share on screen are the ones where the viewer must read the
screen share, read the verbatim quote, and listen simultaneously. That is the split-attention
and spatial-contiguity case, not the safe boundary condition the black-canvas items enjoy.
The review's specific recommendation: **keep the word-by-word reveal for text-on-black, but
consider short static 1–2 line caption blocks over footage**, in a consistent location.

**8. The 9:57 long-form is past the engagement ceiling.**
Median engagement peaks near 6 min. Chapters (already present) are the documented mitigation
and lift median engagement to ~10.8 min, so this is a known, managed trade rather than a
defect — but a ~6 min variant is what the evidence would pick if only one existed.

**9. Consent has no recorded trail.**
The ethics literature is consistent that consent should be **specific about dissemination**,
**tiered**, **ongoing**, and paired with a **right to review before publication** — and that
a PI/student power differential makes voluntariness the thing to protect, ideally with
consent collected by someone other than the PI. Nothing in this repo records that any of the
people quoted have seen their bite or agreed to its publication. The reels do honor Andrew's
"Don't film me" in the sense that matters most — his clip is audio-only because his phone was
face-down — but the line itself is used as reel 01's cold open, which is a decision worth his
explicit sign-off rather than ours. Concretely: a per-person review link and a recorded
yes/no before anything leaves draft, and a note on how disfluency-removed quotes were edited.

**10. Disfluency removal is the one place where "better" is genuinely contested.**
Cutting the fillers improves perceived competence and polish — which the reels want — but
measurably slows a listener's next-word recognition. The review's own split: keep the
aggressive micro-editing for the reels, and **be more conservative in the long-form**, where
authenticity and social presence carry more of the value. Useful nuance for a lab: perceived
expertise buffers the credibility cost of disfluency, so the case for cutting a student's
"um"s is stronger than for cutting a PI's.

## Reproducing the audit

From this directory, against committed files only (no media needed):

```bash
# 1. caption overlaps, reading rate, line length  (findings 3 and 4)
python3 - <<'PY'
import re, os, statistics as st
os.chdir("../reels")
def parse(p):
    cues, txt, i = [], open(p).read().splitlines(), 0
    while i < len(txt):
        m = re.match(r'(\d+:\d+:\d+\.\d+)\s+-->\s+(\d+:\d+:\d+\.\d+)', txt[i])
        if m:
            f = lambda t: (lambda h, mn, s: int(h)*3600 + int(mn)*60 + float(s))(*t.split(':'))
            body, j = [], i + 1
            while j < len(txt) and txt[j].strip(): body.append(txt[j]); j += 1
            cues.append((f(m.group(1)), f(m.group(2)), body)); i = j
        i += 1
    return cues
ov = n = fast = 0; lines = []
for fn in sorted(f for f in os.listdir('.') if f.endswith('.vtt')):
    c = parse(fn); n += len(c)
    ov += sum(1 for a, b in zip(c, c[1:]) if b[0] < a[1] - 1e-6)
    fast += sum(1 for a, b, t in c if b > a and len(' '.join(t)) / (b - a) > 17)
    lines += [len(L) for _, _, t in c for L in t if L.strip()]
print(f"overlapping cues {ov}/{n} ({100*ov/n:.0f}%)   >17 CPS {fast}/{n}   "
      f"longest line {max(lines)} chars   median {st.median(lines):.0f}")
PY

# 2. silent card time and cut rate  (findings 2 and 6)
python3 - <<'PY'
import json, collections
e = json.load(open("../reels/reels-edl.json"))
for r in e["reels"]:
    dur = sum(b - a for it in r["items"] for a, b in it["segments"])
    cuts = sum(len(it["segments"]) - 1 for it in r["items"]) + len(r["items"]) - 1
    cards = r["title_card"]["dur"] + r["end_card"]["dur"]
    vis = collections.Counter(it.get("visual", "card") for it in r["items"])
    print(f"{r['id']:<26} {cuts/dur:.3f} cuts/s   silent cards {cards:.1f}s "
          f"({100*cards/(dur+cards):.0f}% of runtime)   {dict(vis)}")
PY

# 3. delivery audio settings  (finding 1)
grep -n '"rate"' ../highlights/edl.json ../reels/reels-edl.json
grep -n '\-b:a' ../highlights/make_highlights.py ../reels/make_reels.py | head
```

## Provenance

| File | What it is |
|---|---|
| [`query.txt`](query.txt) | The exact 8-part prompt submitted to Edison |
| [`edison-answer.md`](edison-answer.md) | The review as returned (29.7 kB), with inline citation keys |
| [`edison-formatted-answer.md`](edison-formatted-answer.md) | Same review with the bibliography rendered inline (52 kB) |
| [`edison-references.md`](edison-references.md) | 50 numbered references with DOIs and citation counts |
| [`edison-response.json`](edison-response.json) | Complete raw trajectory response — all 94 evidence contexts, the 51 used, tool history, per-context scores |
| [`edison-run-metadata.json`](edison-run-metadata.json) | Status, timing, context counts |
| [`_task_id.json`](_task_id.json) | Task and build IDs for re-fetching the trajectory |

Re-fetch the trajectory (the API key is `EDISON_PLATFORM_API_KEY`; never echo it):

```python
import json, os
from edison_client import EdisonClient
c = EdisonClient(api_key=os.environ["EDISON_PLATFORM_API_KEY"])
t = c.get_task(task_id=json.load(open("_task_id.json"))["task_id"], verbose=True)
print(t.model_dump()["environment_frame"]["state"]["state"]["response"]["answer"]["answer"])
```

**Caveat on the review itself.** It is an automated literature synthesis. Effect sizes were
taken from the sources it cites and have not been independently verified against the
originals; a handful of cited works are very recent and lightly cited. The parts of it that
should carry the most weight are the ones where it is repeating well-replicated meta-analytic
results (Mayer's principles, the audio-fluency experiments) and, just as usefully, the places
where it says the evidence does not exist.
