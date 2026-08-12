# CNMS 2026 — curated prompts & outcomes from the lab's GitHub corpus

Source material for the "slideshow of prompts and some of the resulting outcomes" slides
(issue #175). Built 2026-08-12 by fetching **every** issue, PR, and comment across
`byu-vcl`, `powder-doser`, and `tensegrity-optimization` (raw dump + index in
[`data/cnms-2026-corpus/`](../data/cnms-2026-corpus/INDEX.md)), mining each repo for
candidates, and verifying the headline quotes verbatim against the raw JSON.

All quotes are copied exactly, typos included ("weve", "aghh") — recommend keeping them;
they read as authentic. Elisions marked with "…".

## Headline numbers (for the opening / "It's hard to keep up" slide)

- **254 issues + 146 PRs** across the three repos, Jan 6 → Aug 12, 2026
- **3,417 human comments**, 1,181 bot comments, 464 inline review comments, 205 PR reviews
- **616 human `@claude` triggers** — **361 from Sterling** (3 accounts), **255 from students/others**
- Growth curve: **9 triggers in June → 514 in July** (Claude Code workflows landed late June; August is a partial month at 93)
- powder-doser: napkin sketch (Apr 23) → agent-driven glovebox dosing at U. Utah (Jul 24) in **13 weeks**
- byu-vcl PR #60 alone spans Feb→Aug 2026: from Copilot design chat to Claude physically driving the OT-2 — a one-PR embodiment of the talk's timeline
- ⚠️ **FLAIME caveat:** the FLAIME proposal lives in `vertical-cloud-lab/digital-alloy-lab-private`, *not* in these three repos (only one substantive mention here, [byu-vcl#95](https://github.com/vertical-cloud-lab/byu-vcl/pull/95#issuecomment-4566509175)). The "how many sessions / PRs / pings" counts need a separate pass over that repo.

---

## The shortlist — 16 slide-ready prompt → outcome pairs

Ordered to follow the talk narrative. Each works as one slide: the human prompt big, the outcome as the reveal.

### A. Students running the lab's agents (teaching narrative)

**1. Five words, one robot** — sgbaird, 2026-07-11 · [byu-vcl#84](https://github.com/vertical-cloud-lab/byu-vcl/issues/84#issuecomment-4948345446)
> @claude are the lights on?

**Outcome (2m 3s):** "Yes — the lights are on ✅ Captured a fresh full-res still from the OT-2 camera Pi just now (over Tailscale, no one had to touch the hardware)" — with a lux estimate and embedded photo. *Triage-from-anywhere in its purest form.*

**2. A student steers the OT-2 by comment** — timothy-commins (undergrad), 2026-07-28 · [byu-vcl#60](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5108531313)
> @claude the color sensor is in slot 8. I want you to run a test to pick up the wireless color sensor and to use the camera to confirm if it has been picked up or not

**Outcome (39m 46s):** "**Camera confirmation: housing hanging mid-air on the nozzle** ✔" — the agent detected an unannounced P20→P300 pipette swap and corrected coordinates. The arc continues: "it will break the ot-2." ([5108951888](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5108951888)) → "great job… try the same test again but -2mm in the y direction" ([5110062424](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5110062424), which the agent **refused** as unsafe after the pipette swap) → "this test seems perfect" ([5110478883](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5110478883)). *A 4-slide build showing iteration, safety, and convergence.*

**3. An undergrad runs a double-blind experiment on the AI** — me-madsen, 2026-08-03 · [tensegrity#86](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/86#issuecomment-5172717335)
> The second set of drops contains 20 drops. A random arrangement of sets of 5 drops… The order of these will be known to me and not to you. The data will be uploaded to you, and I will check to see if your analysis… matches the actual order of the drops

**Outcome:** Claude pre-registered its decision rule before seeing data, then blind-classified 90 accelerometer drops. Verdict three days later, with a photo of the handwritten key: "By my review, it seems Claude got the true key correct." ([5209909579](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/86#issuecomment-5209909579)) — **18/18 correct**. *A student spontaneously inventing blinded validation is the teaching narrative's peak; one-image slide.*

**4. The learning curve, honestly** — gage-erickson, 2026-06 · [byu-vcl#99](https://github.com/vertical-cloud-lab/byu-vcl/issues/99#issuecomment-4463300181)
> It regularly asks to run specific commands that I also don't really understand.

**Outcome:** Six weeks later the same cohort was steering robots and designing blind tests. Pairs with the onboarding policy comment ([4756431550](https://github.com/vertical-cloud-lab/byu-vcl/issues/99#issuecomment-4756431550)): "We can get you set up with being able to ping @claude on repos…"

### B. Powder doser Part I — generative system design

**5. Napkin sketch → parametric CAD, same day** — sgbaird, 2026-04-23 · [powder-doser#1](https://github.com/vertical-cloud-lab/powder-doser/issues/1)
> We're thinking of using a pure mechanical approach that can be connected to a gantry system… deep ladle/style to drop powder

**Outcome:** Within hours, Copilot opened PR #2 with a CadQuery parametric model plus an Edison literature review framed "roughly as the intro to a *Digital Discovery* manuscript." Follow-up prompt "@copilot+claude-opus-4.7 Include full assembly image from CAD" ([4309852263](https://github.com/vertical-cloud-lab/powder-doser/issues/2#issuecomment-4309852263)) returned an embedded assembly render **one minute later**.

**6. Honest engineering, AI edition** — swcharles (student), 2026-07-01 · [powder-doser#116](https://github.com/vertical-cloud-lab/powder-doser/issues/116#issuecomment-4858202063)
> Note: yes, the threading is terrible. It was AI, we're fixing it in the next few days. It should work for now.

**Outcome:** Posted with photos of 9 freshly printed AI-designed test augers going straight into student hand-tests with powders and a scale ("holding it at different angles, rotating it, tapping it, while recording a video" — [4836316778](https://github.com/vertical-cloud-lab/powder-doser/issues/116#issuecomment-4836316778)). *Real manual tests informing the agent, and a deadpan one-liner for the "challenges" promise.*

### C. Powder doser Part II — the agent as lab operator

**7. Twelve words of delegation** — sgbaird, 2026-07-21 · [powder-doser#131](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5038893181)
> @claude I gave you mongodb credentials. See what you can do with those permissions

**Outcome:** "MongoDB credentials probed: full atlasAdmin access, end-to-end upload verified" — and the agent flagged that admin scope was too broad, prompting scoped credentials the same evening. *The agent talks its operator into better security.*

**8. First fully remote dose** — williamulbz (student), 2026-07-22 · [powder-doser#131](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5048407447)
> @claude the zero is connected to the pico now with tailscale ssh set up. dose 1 g on the powder doser

**Outcome:** "✅ Dosed 1 g — landed at 0.9972 g (within the ±0.005 g tolerance), fully remote over Tailscale SSH." *The first time the agent physically moved powder — from a one-line student prompt.*

**9. The demo demoed itself** — lbwinters (student), 2026-07-23 · [powder-doser#131](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5061919955)
> @claude we have some people visiting for a lab tour, so we want to run a quick demo. Please do so

**Outcome:** "✅ Demo run complete — 1 g three-phase dose landed at **0.9993 g**, the first run ever to finish inside the ±1 mg tolerance" — after Claude noticed and killed a stale serial session holding the port.

**10. Glovebox, go (U. Utah milestone)** — lbwinters, 2026-07-24 · [powder-doser#131](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5072558552)
> @claude weve loaded salt into the auger and we are ready. Go ahead and dose 1 gram of powder

**Outcome:** "✅ Dosed 1 g of salt — cup holds **0.9956 g** (−4.4 mg, inside the ±5 mg tolerance)" — inside an inert-atmosphere glovebox, driven from a GitHub Actions runner over Tailscale. Collaborator verdict ([5074182337](https://github.com/vertical-cloud-lab/powder-doser/issues/117#issuecomment-5074182337)): "Getting the device into and dosing solids within the glovebox wirelessly using Claude as the control agent worked!… The device slowly pulled itself apart while running… the Lessard lab would like to build a few!" *Success, failure, and adoption interest in three bullets.*

**11. The agent as detective** — claude[bot] responding to a debugging prompt, 2026-07-30 · [powder-doser#131](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5134225990)
> the firmware absolutely *sent* tap commands — but with the auger stationary, 50 consecutive taps moved the scale by exactly nothing… That's **~550 commanded taps since 07-24 with essentially zero delivered mass**.

**Outcome:** Pure log forensics proved the solenoid had been electrically dead for a week without anyone noticing; team rewired it, then verified the fix through the agent ("all nuts have been replaced with locknuts! @Claude can you dispense 0.25g of salt?" → **0.2506 g**, [5181688024](https://github.com/vertical-cloud-lab/powder-doser/issues/132#issuecomment-5181688024)).

### D. Tensegrity — analysis, CAD, and optimization

**12. Prose in, printable part out** — sgbaird, 2026-05-08 · [tensegrity#34](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/34)
> Three struts in a triangle. They all rotate at 60 degrees. Top is also a triangle, rotated. From bottom to top is a "string". … Get the STL file too, just in case.

**Outcome:** A fully parametric OpenSCAD T3-prism with sliced Bambu `.gcode.3mf` (PR #35) that grew into the multi-material variants that were printed and drop-tested. Companion one-liner for the BO brain: "use honegumi python package to help with this" ([tensegrity#29](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/29)) → a runnable Ax/BoTorch campaign scaffold. Closing beat months later from a student: "This was excellent. The .3mf file worked great." ([5184282874](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/35#issuecomment-5184282874))

**13. The agent retracts its own finding** — sgbaird, 2026-07-31 · [tensegrity#94](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/94)
> @claude you've been doing a lot of analysis that has more or less been black-box to us… we'd like to better understand the analysis that you're taking with #86.

**Outcome:** The agent commissioned an adversarial Edison review of its own drop-test analysis ("try to break this, not confirm it" — 10 named attack surfaces) — and the review **overturned its recommendation**: "The 20 ms exports contain ~0.39 ms of real pre-trigger data. My script's docstring asserts the opposite… no arrangement attenuates." *Scientific integrity, agent-style — the best "challenges" slide with a happy epistemic ending.*

### E. Manuscripts, proposals, admin

**14. The most relatable academic moment** — sgbaird, 2026-07-01 · [byu-vcl#146](https://github.com/vertical-cloud-lab/byu-vcl/pull/146#issuecomment-4860708087)
> @claude aghh.. abstract limit is 150 words for TMS 2027. Fix this

**Outcome (1m 33s):** "Abstract trimmed to the 150-word TMS limit… **147 words**", itemizing which approved claims survived. Same PR: Edison delivered a referee-style pre-review with real citations ("Camera-based lab monitoring is not new — Edison cites HeinSight2.0…", [4860402760](https://github.com/vertical-cloud-lab/byu-vcl/pull/146#issuecomment-4860402760)).

**15. Admin at conversational speed** — sgbaird, 2026-07-27 · [byu-vcl#156](https://github.com/vertical-cloud-lab/byu-vcl/pull/156#issuecomment-5094167311)
> @claude based on above, what is a max 40-word email I could send to Larry Howell, beginning with 'Hi Larry, Sterling here…'

**Outcome (31 s):** a 38-word draft plus a 40-word alternate, grounded in policy docs the agent had compiled earlier. Same PR, timestamped 3:36 AM: "Compile a list of contacts I could reach out to" → `byu-founder-contacts.md` in 5½ minutes ([5029877173](https://github.com/vertical-cloud-lab/byu-vcl/pull/156#issuecomment-5029877173)). *"Identifying key contacts" theme, verbatim — and the 3:36 AM timestamp shows the lifestyle.*

### F. Multi-agent, multi-tool (timeline node 5)

**16. Agents launching agents** — sgbaird, 2026-07-29 · [powder-doser#131](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5122974511)
> @copilot+mai-code-1-flash-picker open up a new PR that merges into this one

**Outcome:** Copilot opened PR #136 (powder characterization campaign) **stacked onto a Claude branch** — Copilot and Claude handing work to each other. Sibling one-liner from tensegrity ([4713093337](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/33#issuecomment-4713093337)): "@copilot send these results (scripts, data, figures) to edison analysis…, fetch, report back" — one coding agent commissioning, retrieving, and committing a second AI system's scientific review in 24 words.

---

## Failure & guardrails beats (the "challenges" promise)

- **"Kind of scary"** — benwhitney5463, 2026-08-03 ([byu-vcl#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5171373304)): "after the first test failed, claude started doing its own thing… it scraped the 'pipette' (screwdriver) on the right x rail." → Next day: "@claude create a set of custom CLAUDE.md instructions to help avoid this kind of risky behavior" ([5180854707](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-5180854707)) → guardrails PR in 4m 9s: "one human go-ahead buys exactly one hardware run; a failure means stop and report, not retry with a different number." *The strongest failure→recovery pair in the corpus.*
- **Optimism vs. physics** — lbwinters, glovebox session ([5072991855](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5072991855)): "if you don't see powder come out keep running the auger for 30 seconds until you do" → "⚠️ …**no powder after ~150 revolutions**, and then the rig went offline mid-attempt" (fine AIBN clogged the auger). Plus the static-charge video: "the salt stuck to the sides of the auger… we just didn't think to implement [the de-ionizing fan] before beginning" ([5097409563](https://github.com/vertical-cloud-lab/powder-doser/issues/117#issuecomment-5097409563)).
- **Shepherding, not automating** — sgbaird-yolo ([tensegrity 4409363234](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/35#issuecomment-4409363234)): "I guess you started hitting rate limits. Carry on again"; "@claude try again (@gage-erickson, we ran out of fable 5 usage until Saturday, see slack)" ([byu-vcl 5137152673](https://github.com/vertical-cloud-lab/byu-vcl/issues/78#issuecomment-5137152673)) — a lab sharing a model quota like a shared instrument.
- **Sometimes the human wins** — sgbaird, 2026-08-06 ([byu-vcl#169](https://github.com/vertical-cloud-lab/byu-vcl/issues/169#issuecomment-5199599323)): "Nice! Looks like it was best to ditch Claude's efforts, at least on this task. @claude attempt downloading and commit the onshape file Ben linked to" — human does the design, agent does the librarianship, in one sentence.
- **Spaghetti failure** — photo of a failed print dropped into the CAD thread ([tensegrity 4409344661](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/35#issuecomment-4409344661)): "btw, spaghetti failure from the prior print (not entirely unexpected)" — atoms pushing back on bits; kicked off the multi-week supports saga ("@copilot+claude-opus-4.7 you forgot to add supports" → "Fixed in 449adcd", [4461619858](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/35#issuecomment-4461619858)).

## Bench — more verified candidates by theme

**Robotic control / physical loop:** dispense-with-a-diagnosis (salt-bridge jam cleared mid-run by solenoid taps + auger reversals, [powder-doser 5063724411](https://github.com/vertical-cloud-lab/powder-doser/issues/132#issuecomment-5063724411)); PID dose after two failed attempts → "**1.0012 g…, 0 taps, ~11 s** — full 4D telemetry captured, visualized, committed, and logged to MongoDB" ([5122561032](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5122561032)); connectivity check by moving the pipette head −10 cm and back ([byu-vcl 5049615063](https://github.com/vertical-cloud-lab/byu-vcl/issues/60#issuecomment-5049615063)); "Just unplugged it… @claude check it now" → back online in 78 s ([powder-doser 5220074912](https://github.com/vertical-cloud-lab/powder-doser/issues/127#issuecomment-5220074912)); "@claude grab an image" ([byu-vcl 5051310981](https://github.com/vertical-cloud-lab/byu-vcl/issues/84#issuecomment-5051310981)).

**Students & teaching:** "@claude looks like you got stuck… do a quick and easy fix and move on" ([tensegrity 4900737266](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/35#issuecomment-4900737266)); the PI writing students' first prompt template ([tensegrity 4500807271](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/20#issuecomment-4500807271)); "for kicks and giggles, comment on the above issues…" ([tensegrity 5209814854](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/96#issuecomment-5209814854)); RFID "shower thought" — a student redesigning hardware around the agent's perception gap ([powder-doser 5074139529](https://github.com/vertical-cloud-lab/powder-doser/issues/131#issuecomment-5074139529)); precise scope-fencing: "this is not direction for what you should do…, this is a hypothetical question… Do not provide these files now" ([tensegrity 5184162394](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/35#issuecomment-5184162394)); undergrad EE debugging loop closed in 33 min ([byu-vcl 5049210314](https://github.com/vertical-cloud-lab/byu-vcl/issues/147#issuecomment-5049210314)).

**Data & analysis:** "Can you do a video analysis?" → YouTube bot-wall improvisation → full frame-by-frame kinematics with fps hunted from a camera-spec comment ([tensegrity 5036908261](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/86#issuecomment-5036908261)); accelerometer discrepancy → SAE J211 forensics, DAQ software identified from a CSV header path ([tensegrity#71](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/71)); MongoDB time-series streaming designed in an issue body ([powder-doser#126](https://github.com/vertical-cloud-lab/powder-doser/issues/126)); "Claude can probably check the streams" — livestream as provenance ([powder-doser#125](https://github.com/vertical-cloud-lab/powder-doser/issues/125)); "I want to be able to comment 'claude, I've loaded Brown Rice Flour, run the test'" — the prompt *is* the API spec ([powder-doser 5123330037](https://github.com/vertical-cloud-lab/powder-doser/issues/116#issuecomment-5123330037)).

**Design & figures:** "I want to see something cool here from these physics-based simulations" → animated MuJoCo/PolyFEM impact renders ([tensegrity 4427269438](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/33#issuecomment-4427269438)); placeholder manuscript figures driven by a *real* Ax BO loop ([tensegrity 4673509625](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/20#issuecomment-4673509625)); igloo accelerometer mount dictated in prose + caliper readings + phone screenshots ([tensegrity 4794790065](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/35#issuecomment-4794790065)); where AI CAD breaks down — agent asked to diagnose its own spatial-reasoning weakness ([powder-doser 4433787200](https://github.com/vertical-cloud-lab/powder-doser/issues/29#issuecomment-4433787200)); "you were meant to clone bambu slicer repo…" → genuine upstream CLI bug discovered ([tensegrity 4520389873](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/64#issuecomment-4520389873)).

**Admin & literature:** desiccator query → "bulk permeation is *not* the bottleneck" + exact commercial product for $267.50 ([byu-vcl 4482291884](https://github.com/vertical-cloud-lab/byu-vcl/pull/112#issuecomment-4482291884)); pH-meter shopping through the lab Pi's residential IP because vendors 403 the CI runner ([byu-vcl 5139326323](https://github.com/vertical-cloud-lab/byu-vcl/issues/148#issuecomment-5139326323)); "Who would we reach out to at BYU to get permission to drop a scaled up tensegrity structure from the Kimball tower?" ([tensegrity#69](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/69)); egg-drop whimsy routed through Edison ("whether this is a good idea", [tensegrity#46](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/46)); "@claude, wait, what?" → claim verified with citations in 90 s ([byu-vcl 5077808207](https://github.com/vertical-cloud-lab/byu-vcl/issues/164#issuecomment-5077808207)); Al-Ti phase diagram fetched, annotated with the lab's 1500 °C atomizer ceiling, embedded for a student ([byu-vcl 4987607623](https://github.com/vertical-cloud-lab/byu-vcl/issues/161#issuecomment-4987607623)); repo-wide merge triage that generates the next round of prompts ([powder-doser#137](https://github.com/vertical-cloud-lab/powder-doser/issues/137)).

**Meta (this talk):** "@claude attempt editing. You should be able to use your browser tooling I think." → agent joins the live PowerPoint session as Guest Contributor, edits the CNMS deck while it's open, and flags a link-security hole unprompted ([byu-vcl#175](https://github.com/vertical-cloud-lab/byu-vcl/issues/175#issuecomment-5260212969)); "@claude test" → "🏓 Pong!" in 12 s — the moment a second agent joined the lab ([tensegrity#80](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/80)).

---

*Verification note: the 16 shortlist quotes' comment IDs, authors, dates, and text were
checked verbatim against the raw corpus (12 by automated string match, the rest during
mining). Links use the `/issues/<n>#issuecomment-<id>` form, which GitHub auto-redirects
for PRs.*
