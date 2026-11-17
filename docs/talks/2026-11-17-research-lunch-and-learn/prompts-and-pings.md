# Prompt pairs and atomizer pings

Real examples for slides 5 and 6 of the [outline](outline.md), found by searching the lab's public
threads for [#350](https://github.com/vertical-cloud-lab/byu-vcl/issues/350). Quotes are verbatim and every link was opened
through the GitHub API; "…" marks a cut. Prompts are Sterling's unless noted.

**Recommended:** Pair B for slide 5, a 16-word prompt that adds a tool and a check, and Ping 1
for slide 6, where a meeting became an assigned issue and then "Email sent."

## 1. Prompt pairs: "The same agent succeeds or fails on context and tools"

The two prompts in each pair are on the same task, in the same thread.

### Pair A: context (name the thing). Grabbing a frame from the OT-2 lid camera

**Not so good:** byu-vcl PR #234, 2026-09-29. [comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5896714246)
> @claude grab a single image from the overhead ot2 camera. Max one sentence and just the embedded image

What happened: two cameras fit "overhead ot2 camera", and the agent used the easy one, the OT-2's own built-in camera through `/camera/picture` ([reply](https://github.com/vertical-cloud-lab/byu-vcl/pull/234#issuecomment-5896725922)). Two days later Sterling had to ask again (below).

**Good:** byu-vcl PR #84, 2026-10-01. [comment](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-5924735383)
> @claude when I asked for a snapshot image, I meant from the raspberry Pi and corresponding camera that is sitting literally on top of the ot2 right now. Not the embedded camera. If you don't have access to that for some reason, let me know. Max four sentences and the embedded image in your reply

What happened: "Sorry for the mix-up". This time the frame came from the Pi 5 and HQ Camera on the lid, in four sentences as asked, with a useful read of the optics: about 65 px per well now, and about 180 px if the camera were squared to the deck ([reply](https://github.com/vertical-cloud-lab/byu-vcl/pull/84#issuecomment-5924738921)).

*What changed:* the prompt names the device, rules out the wrong one, and says what to do if access fails.

### Pair B: tools (give it a checker). Atomizer charge-cup design, DAL #152

**Not so good:** 2026-09-24. [comment](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/152#issuecomment-6353386494)
> @claude+opus-5-5 comment on above. Make a 3D visualization based on the actual docs for the atomizer we have available. Use proper CAD. Let me know what info you need … but I thought we had sufficient info in this repository scattered throughout issue and PR comments. … provide a table of experiments with the dimensions (i.e., the bill of materials …)

What happened: a 41-minute run produced CAD, a BOM and a PDF ([reply](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/152#issuecomment-6353386571)). Sterling's verdict was "You're overly verbose, using too much jargon, the PDF is kind of confusing" ([comment](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/152#issuecomment-6353386742)). The press fit had also been sized by comparing hoop stress (~100 MPa) with yield (≥110 MPa), a mistake that went unnoticed until the Edison check.

**Good:** 2026-09-25. [comment](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/152#issuecomment-6353387199)
> @claude double check this with Edison, and also make sure that the sizes are something standard.

What happened: "Edison caught four real errors, and three sizes weren't stock". The agent corrected its own number: "I checked hoop stress against yield, which is wrong. … 1.12× yield — not the 0.91 I claimed". It also swapped a 1 mm vent for 1/16" and changed the sleeve fit ([reply](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/152#issuecomment-6353387308)).

*What changed:* the prompt is only 16 words long, but it names a tool (Edison) and a check (stock sizes). A good prompt doesn't have to be long.

### Pair C: definition of done (state the limits). TMS 2027 abstract, tensegrity-optimization #78

**Not so good:** 2026-07-01. [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/78#issuecomment-4860721863)
> @claude implement based on feedback; i.e., the framework and methodology for creating these improved structures is a key focus, that other things are down the road (e.g., use of different materials than just FDM)

What happened: a "~245 words" abstract full of fill-in slots ("Preliminary results from [N] BO-selected designs … show [an X% reduction …]"), on the day the abstract was due ([reply](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/78#issuecomment-4860723505)).

**Good:** 2026-07-02, about an hour later. [comment](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/78#issuecomment-4861047658)
> @claude [facepalm emoji] pretty sure it's a 150 word limit, and we definitely can't get results today, when it is due, so stop mentioning placeholders. We can talk about targeted results over baselines where the baseline has numbers. … (target of 25 batches of 4 per batch for 100 experiments)

What happened: 140 words with every placeholder gone. It now has a target against a published baseline (0.34 J/cm³, Bates et al. 2016) and "25 batches of four designs (100 experiments)" ([reply](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/78#issuecomment-4861048830)).

*What changed:* the prompt gives the word limit, the deadline, a ban on placeholders, and the numbers to use.

### byu-vcl #197: does a prompt there fit? Partly. The guesses weren't from Sterling's prompts

- **The guessed firmware facts came from runs Timothy Commins started,** with short prompts asking the agent to move the sensor and measure, e.g. "…this time in well 7, and also 5mm higher" ([5594316664](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5594316664)). The reply told him to "set `--rgb`" to light the sample ([5594323820](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5594323820)). The next run concluded that the LEDs were "inert" ([5594524982](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5594524982)). The root cause was missing context: the firmware is on the board, not in the repo, and the agent said so ("I'm inferring the mechanism rather than reading it", [5610320804](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5610320804)). The fix came when a prompt sent it to the upstream repos: "Three things this issue got wrong, now read from the firmware source instead of guessed: `R`/`Y`/`B` are paint volumes in µL, not LED colours" ([5637989650](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5637989650)).
- **Sterling's own good #197 prompt** ([5604864980](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5604864980)):
  > @claude get the youtube livestream links (timestamped links) for each of the exact moments where color measurements were taken, along with a screenshot … (… probably 300 px width) … based on https://huggingface.co/…/basic_plotting.py … This is in part assuming that the color sensor measurements are timestamped (which if they're not, we need to correct).

  Result: all 114 readings were indexed, and the agent replied "Your caveat was right — they were not timestamped". It fixed that in code, checked the links by OCR against the clock burned into the stream (27/27 within 1 s), and found a person in shot in 11 of the 27 frames ([reply](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5604868918)).
- **Sterling's weaker #197 prompt** ([5630125440](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5630125440)):
  > …I'm guessing it might be easier to use the Opentrons UI to do some calibration along with using the well plate JSON representation … I think the file is on main branch in a nested directory). Provide some links and documentation to @timothy-commins for this process. Keep your response brief.

  Result: the reply pointed to a JSON for "the 3×2 paint-vial rack" and covered importing labware ([reply](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5630127237)). Timothy wrote back: "I'm not sure what that refers to, but we are going to use a 96 slot well… I need instructions on how to calibrate it" ([5638357384](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5638357384)). The agent agreed the phrase "was too vague" ([5638364283](https://github.com/vertical-cloud-lab/byu-vcl/issues/197#issuecomment-5638364283)).
- **Verdict:** #197 makes a mild Sterling-only pair (the two prompts above). The firmware story is better told as "missing context makes the agent guess", with the caveat that the prompts were Timothy's.

### Alternates

- **D. Context beats tools (atomizer, DAL #219).** The issue body said "70% copper, 30% nickel". The prompt "@claude:medium suggest the melt temperature to run at" ([comment](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/219#issuecomment-6454377957)) got "Aim for 1300 °C … about 60 °C of superheat" ([reply](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/219#issuecomment-6454386230)). Then Sterling named the real alloy, its composition and a source: "nickel aluminum bronze (NAB), also called 630 Bronze … 82% copper, 10% aluminum, 5% nickel, and 3% iron according to https://www.nationalbronze.com/…" ([comment](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/219#issuecomment-6460235121)). The answer became "most of my earlier warnings were too pessimistic … about 250 °C of superheat, not ≤ 60 °C" ([reply](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/219#issuecomment-6460239409)). Edison had also been run on the wrong alloy, so a tool can't make up for wrong context. Sterling owned the mix-up in the thread.
- **E. A wish list vs. a spec (atomizer animations).** The everything-at-once prompt ([DAL #142](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/142#issuecomment-6353376613)) led to "that animation … is hilariously bad. I don't think the users of the atomizer will have Elastigirl / Mr. Fantastic powers" and "you got lazy, you were meant to at least start with whisper" ([byu-vcl #255](https://github.com/vertical-cloud-lab/byu-vcl/pull/255#issuecomment-5966425543)). The stack-fix spec named `atomizer-training/viz3d/model.py` and `stack_parts()`, cited timestamped training videos, listed five numbered fixes, and gave a number to check ("about 29 mm … check yours") ([spec](https://github.com/vertical-cloud-lab/byu-vcl/pull/255#issuecomment-6032439000), [re-sent](https://github.com/vertical-cloud-lab/byu-vcl/pull/255#issuecomment-6032838369)). The result "clears the upper sonotrode by 28.6 mm, against the 29 mm you got" ([reply](https://github.com/vertical-cloud-lab/byu-vcl/pull/255#issuecomment-6032844455)). Caveats: the spec is marked "drafted by claude, approved by sgbaird". Its first copy also went to the wrong workflow because it mentioned `@claude-youtube`.

---

## 2. Atomizer pings: "Working in the open"

### Ping 1: a meeting transcript turned into an issue, then "Email sent." (DAL #153)

- **Links:** [bot-posted issue](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/153) (`github-actions[bot]`, 2026-09-17, assigned to Gage) and [Gage's reply](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/153#issuecomment-6353386531)
- **Quote:** "@gage-erickson could you email Taylor Sparks (cc me) about using his arc melter? Ask whether it's feasible before ~Sep 28–29 so we can atomize the result while Bartosz is here". Gage, five days later: "Email sent."
- **Why it's a good slide:** the whole loop fits on one screen. A meeting became a task for the right person, and he closed it without anyone having to remember.
- **Context for the slide:** this is one of 12 posts queued from the 9/17 AMAZEMET call ([queue](https://github.com/vertical-cloud-lab/byu-vcl/blob/4b2f547/docs/meetings/2026-09-17-repowder-install/posts/queue.json)). The [corrected transcript](https://github.com/vertical-cloud-lab/byu-vcl/blob/4b2f547/docs/meetings/2026-09-17-repowder-install/transcript.md) has a funny corrections table: Tactiq's "30 mm hose" is really 13 mm, and "death certificate" was "desiccant".

### Ping 2: a 26-word question from the machine (DAL #164)

- **Links:** [question](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/164#issuecomment-6353398049), [answer](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/164#issuecomment-6353398132), [Gage's follow-up with a photo](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/164#issuecomment-6353398411)
- **Quote:** Gage: "@claude there is already some sharpie writing on a piece on the inside of the chamber. If I drew a line would that be an issue?" Claude: "No, a marker line won't hurt the sonotrode or the run."
- **Why it's a good slide:** a student at the machine gets an answer with numbers in it (~0.2 mg of ink, ~3 ppm O₂ against a 100 ppm limit). About 40 minutes later he posted photos and "…goldilocks zone. Hallelujah."

### Ping 3: an SOP draft that corrects the notes from the run record (DAL #251)

- **Links:** [Gage's request](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/251), [agent's SOP reply](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/251#issuecomment-6782394032), [PR #253](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/253) (still open)
- **Quote:** "Set the amplitude to 90 before Ultrasonic Start. On Oct 6 it ran at 50 by mistake. … close the argon cylinder after every run (one was found empty on Oct 20)."
- **Why it's a good slide:** each SOP fix cites a real past run. The agent also asked Gage to "check these at the machine" instead of overruling him. Caveat: PR #253 isn't merged.

### Runners-up

- **Install checklist** (bot post, 9/17, [DAL #142](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/142#issuecomment-6353376509)): "@gage-erickson things to have ready before the 28th: … Argon: 5N (99.999%). … Needs 8 bar at the machine, so an adjustable 0–10 bar regulator, not a welding regulator". This is the right person getting a concrete list straight from the call.
- **A safety ruling into the SOP in 2 minutes** (DAL #143): "@claude:high Record the safety office's oxygen-detection ruling in the atomizer SOP and the lab safety page, and open a PR." ([prompt](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/143#issuecomment-6353378713)). The reply: "I recorded the oxygen-detection ruling and opened PR vertical-cloud-lab/byu-vcl#271" ([reply](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/143#issuecomment-6353378782)). That PR was later moved to DAL #190, which is open.
- **The public record as the lab's memory** (DAL #159): "@claude:medium max one sentence, have we ordered sieves geared towards LPBF (and/or DED) yet?" ([prompt](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/159#issuecomment-6353395043)). The reply took 24 s: "Not as far as GitHub shows." ([reply](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/159#issuecomment-6353395132))
- **An honest one:** the Oct 6 run cross-check ([byu-vcl #255](https://github.com/vertical-cloud-lab/byu-vcl/pull/255#issuecomment-6027045992)) lined up Gage's collar-camera videos with the room stream. Gage then corrected two of its points in public and suggested a thumbs-up signal to sync the clocks ([Sterling quoting him](https://github.com/vertical-cloud-lab/byu-vcl/pull/255#issuecomment-6030587512)). This works for "corrections happen in the open", not for "the agent was right".
