Question: # Evidence base for slide-design rules an AI agent should follow when generating conference slides

## Context (compressed)

I am an AI coding agent that generated 14 text-heavy "quote" slides for a materials-science
PI's conference talk about AI-agent-driven research workflows ("Agentic Lifestyles in the
Era of AI", CNMS 2026). All 14 were cut; the PI's hand-made slides — minimal text,
sentence-message headlines held constant over changing visual evidence, native screenshots
and videos of GitHub threads and lab hardware, progressive-emphasis builds — were
presented. An adversarial review (iteration 1 of this loop) concluded: the cut is best
explained by (a) the block being an appended prototype/source section, (b) redundancy with
examples already integrated natively, and (c) presentation-blocking rendering defects
(text collisions) — with document-like styling as a contributing factor, not the sole
cause. It also replaced my hard thresholds (≤15 words; 1 slide/min; 8–15 s videos) with
attention-per-second reasoning, rehearsal-based timing, five-second blinded comprehension
tests, and an assertion–evidence audit distinguishing agent self-report from external
verification.

## My revised rule set (v2) — the thing to test against literature

R1. Every slide has one defined communicative job; for analytical claims use a sentence
    assertion headline + legible visual evidence (assertion–evidence structure); demos
    instead get a "what to watch for" cue.
R2. Prefer faithful extraction of native artifacts (crop/enlarge/mask/annotate real
    screenshots) over (a) re-typing content into text slides and (b) raw uncropped
    screenshots.
R3. No fixed word cap; manage required reading time vs. dwell time (reading load ≲50% of
    dwell while the speaker talks), minimum effective text size ≈24 pt equivalent,
    contrast ≥4.5:1 (normal) / 3:1 (large).
R4. One slide, one beat; sequences built by holding a skeleton constant and shifting
    emphasis (dim past, highlight current).
R5. Time budget from rehearsal, not slide count; rank optional beats with cut priority.
R6. Match the host deck's visual system; extend existing motifs rather than introduce a
    new template mid-deck.
R7. Mechanical release gates: no overlap, no placeholder leftovers, margins, media plays;
    then human five-second test (≥80% topic identification).
R8. Distinguish claim-evidence types on evidence slides: direct measurement > independent
    validation > agent self-report > anecdote; show comparators, n, uncertainty when the
    claim is scientific.

## Questions (please answer with citations to the research literature)

1. What does the empirical literature (e.g., Mayer's multimedia-learning principles and
   the cognitive-load tradition; Sweller; signaling/coherence/redundancy effects) say
   that SUPPORTS or REFUTES each rule R1–R8? Note effect sizes and boundary conditions
   where known, and where evidence is from student-learning contexts rather than
   conference audiences (external validity caveat).
2. Assertion–evidence slide research (Michael Alley, Joanna Garner, Melissa Marshall and
   colleagues): what benefits are actually measured (comprehension, recall, speaker
   credibility), and what are the documented failure modes or null results?
3. Jean-luc Doumont's published guidance ("Trees, maps, and theorems"; his IEEE
   Professional Communication papers, e.g. "The Cognitive Style of PowerPoint: Slides Are
   Not All Evil"; "Verbal versus visual: A word is worth a thousand pictures, too"): how
   does his position differ from Alley's assertion–evidence and from Tufte's
   anti-PowerPoint critique, and what would he likely say about (a) slides made of
   screenshots of software UIs, (b) verbatim quotations as slide content, (c) videos as
   evidence in talks?
4. Is there research on AUTHENTICITY of evidence in presentations — e.g., screenshots /
   raw artifacts / photographs vs. stylized re-representations — affecting audience
   trust or persuasion? (Include adjacent literature: photo-evidence "truthiness"
   effects, data-visualization trust studies.)
5. Redundancy: when does on-slide text that duplicates speech help (effective
   redundancy, accessibility, non-native listeners) vs. hurt (redundancy effect)? What
   design resolves the tension for quotation slides specifically — is there evidence on
   presenting verbatim quotes in talks?
6. Given all of the above, produce a final ranked list of the 8 rules: which are
   strongly evidence-backed, which are plausible-but-unverified craft knowledge, and
   which should be modified — with the specific modification the literature suggests.


# Evidence Base for Slide-Design Rules: A Literature Review

## 1. Multimedia Learning Principles Mapped to Rules R1–R8

The cognitive theory of multimedia learning (CTML) and cognitive load theory provide the strongest empirical foundation for several of the proposed rules. Mayer's review reports large median effect sizes for key principles: spatial contiguity (d = 1.10, 22/22 comparisons positive), temporal contiguity (d = 1.22, 9 comparisons), coherence (d = 0.86, 23 comparisons), redundancy (d = 0.86, 16 comparisons), modality (d = 0.76, 53/61 comparisons positive), and segmenting (d = 0.79, 10 comparisons) (mayer2020designingmultimediainstruction pages 6-9, mayer2020designingmultimediainstruction pages 4-6, mayer2020designingmultimediainstruction pages 2-4). The signaling principle shows a smaller but robust effect: d = 0.38 (95% CI [0.30, 0.46]) across 44 effect sizes in one meta-analysis (alpizar2020ametaanalysisof pages 10-11), and r = .17 (95% CI [0.11, 0.22]) across 27 studies in another (richter2016signalingtextpicturerelations pages 9-10).

**Boundary conditions** are critical. The signaling effect is moderated by prior knowledge (low-knowledge learners benefit more, r = .19, vs. high-knowledge r = .08) and pacing (system-paced materials show stronger effects, r = .27, than self-paced, r = .13) (richter2016signalingtextpicturerelations pages 14-15, richter2016signalingtextpicturerelations pages 12-14). For the redundancy principle, adding written text to narrated visuals typically hurts learning when it fully duplicates narration, but short keywords can help, and non-native speakers, older adults, and low-working-memory learners often benefit from redundant text (trypke2023twotypesof pages 13-14, trypke2023twotypesof pages 8-9, trypke2023twotypesof pages 3-4).

**External validity caveat:** Nearly all of this evidence comes from student-learning experiments with instructional multimedia materials, not from conference talks delivered to expert scientific audiences under time pressure. The direction of effects is likely to hold, but exact magnitudes may differ for expert audiences who can suppress irrelevant information more effectively and who bring high prior knowledge—which can trigger expertise reversal effects (trypke2023twotypesof pages 13-14, trypke2023twotypesof pages 12-13).

The following table maps each rule to the supporting literature:

| Rule ID | Rule Summary | Supporting Principle(s) | Key Evidence & Effect Sizes | Boundary Conditions/Caveats | External Validity Caveat |
|---|---|---|---|---|---|
| R1 | One communicative job per slide; for analytic claims use sentence-assertion headline + visual evidence; demos get a “what to watch for” cue | Signaling; coherence; assertion–evidence (AE) structure | Signaling improves learning with moderate effects: d = 0.38 in a 29-study meta-analysis and median d = 0.41 in Mayer’s review; coherence median d = 0.86; AE classroom study found retention 94% for AE vs 68% for traditional bullet slides; cited AE studies report fewer misconceptions and better higher-order understanding (alpizar2020ametaanalysisof pages 10-11, mayer2020designingmultimediainstruction pages 2-4, dangelo2018powerpointpresentationsin pages 8-12, alzayed2023assertionevidenceversustraditional pages 2-4) | Strongest evidence is for text-picture signaling and removing extraneous material, not specifically sentence headlines. AE also shows nulls/weaknesses: lower workload but no significant comprehension or motivation gains in one engineering-student creation study (alzayed2023assertionevidenceversustraditional pages 8-9, alzayed2023assertionevidenceversustraditional pages 6-8) | Most AE evidence is from student-learning or student-presentation contexts, not live conference audiences under time pressure (dangelo2018powerpointpresentationsin pages 8-12, alzayed2023assertionevidenceversustraditional pages 8-9) |
| R2 | Prefer faithful extraction of native artifacts (crop/enlarge/mask/annotate real screenshots) over retyping content or showing raw uncropped screenshots | Spatial contiguity; coherence; adjacent trust/clarity findings from data visualization | Spatial contiguity has very large support (median d = 1.10); coherence median d = 0.86; trust literature finds clarity/readability and familiar encodings are primary drivers of trust, and direct labels/annotations reduce working-memory load (mayer2020designingmultimediainstruction pages 4-6, mayer2020designingmultimediainstruction pages 2-4, mckinley2025trustworthybydesign pages 11-12, mckinley2025trustworthybydesign pages 9-10, franconeri2021thescienceof pages 41-42) | No direct empirical comparison of cropped/annotated native screenshots vs retyped slide reconstructions was found. “Authenticity” benefit is therefore inferential, not directly established. Over-ornamented or cluttered screenshots could violate coherence (cavanagh2023usingcommonlyavailabletechnologies pages 4-6, franconeri2021thescienceof pages 41-42) | Evidence comes from multimedia lessons and visualization/trust studies, not specifically scientific talk screenshots of software UIs or lab artifacts (franconeri2021thescienceof pages 41-42, mckinley2025trustworthybydesign pages 2-3) |
| R3 | No fixed word cap; manage reading load vs dwell time, ensure legibility, minimum effective text size, adequate contrast | Modality; redundancy; cognitive-load management; projected-words-per-minute heuristic | Modality median d = 0.76; redundancy median d = 0.86; review of 63 redundancy studies finds short text/keywords can help while full duplicated text often hurts; projected words per minute captures reading burden better than words/slide alone; AE slides in one study averaged 18 projected words/min vs common-practice slides around 35–40 (mayer2020designingmultimediainstruction pages 6-9, mayer2020designingmultimediainstruction pages 4-6, trypke2023twotypesof pages 1-2, trypke2023twotypesof pages 3-4, alley2010projectedwordsper pages 1-3, alley2010projectedwordsper pages 12-14) | The literature does not support a universal word cap. Benefits/harm depend on prior knowledge, complexity, pacing, text length, and whether text is identical or complementary. The 24 pt minimum comes from poster/presentation craft guidance, not direct slide-learning experiments; WCAG contrast ratios are accessibility standards, not CTML findings (trypke2023twotypesof pages 13-14, trypke2023twotypesof pages 8-9, pedwell2017effectivevisualdesign pages 4-5) | Reading-load evidence mostly comes from instructional multimedia and classroom presentations rather than conference talks with expert audiences; contrast guidance comes from accessibility standards outside this evidence base (alley2010projectedwordsper pages 1-3, pedwell2017effectivevisualdesign pages 4-5) |
| R4 | One slide, one beat; keep a constant skeleton and shift emphasis across builds (dim past, highlight current) | Signaling/cueing; organization and integration cueing; segmenting-adjacent pacing logic | Signaling meta-analytic effect d = 0.38; cueing framework shows highlights, color contrast, dimming irrelevant information, and temporal emphasis guide selection/organization/integration and reduce visual search load (alpizar2020ametaanalysisof pages 1-3, koning2009towardsaframework pages 5-7, koning2009towardsaframework pages 3-5, koning2009towardsaframework pages 9-11) | Direct tests of “hold skeleton constant across sequential slides/builds” are scarce. Cueing can backfire if it adds processing burden or is poorly matched to dynamic materials; effects are stronger for novices and complex content (koning2009towardsaframework pages 20-22, koning2009towardsaframework pages 22-24) | Cueing evidence is largely from instructional animations and diagrams, not polished conference decks; nevertheless the mechanism maps closely to progressive emphasis in talks (koning2009towardsaframework pages 5-7, koning2009towardsaframework pages 14-16) |
| R5 | Time budget from rehearsal, not slide count; rank optional beats with cut priority | Segmenting; pacing control; presentation craft knowledge | Segmenting improves learning with median d = 0.79; system pacing vs self-pacing matters in signaling studies, suggesting pacing is a real design variable (mayer2020designingmultimediainstruction pages 6-9, richter2016signalingtextpicturerelations pages 14-15, richter2016signalingtextpicturerelations pages 12-14) | No direct empirical literature was found validating rehearsal-based timing or cut-priority ranking as slide-design rules. This is mainly practice-based craft, though consistent with segmenting and pacing principles (mayer2020designingmultimediainstruction pages 6-9) | Almost entirely extrapolated from instructional pacing research, not from studies of conference talk rehearsal practices |
| R6 | Match the host deck’s visual system; extend existing motifs rather than introducing a new template mid-deck | Coherence; familiarity/consistency from trust literature | Coherence principle supports removing unnecessary variation/noise (median d = 0.86); trust research finds familiarity, professionalism, and clarity matter for trust, implying abrupt template shifts may introduce noise or reduce perceived polish (mayer2020designingmultimediainstruction pages 2-4, mckinley2025trustworthybydesign pages 1-2, mckinley2025trustworthybydesign pages 13-14) | No direct studies were found on mid-deck template changes or host-style matching. Support is indirect: consistency likely helps by preserving coherence and professionalism, but this remains plausible craft knowledge rather than tested law (mckinley2025trustworthybydesign pages 1-2) | Inference is from learning and visualization-trust studies, not from experimental presentation-design studies on deck-level style consistency |
| R7 | Mechanical release gates: no overlap, no leftovers, proper margins/media; then human five-second test | Spatial contiguity; coherence; usability/QA craft knowledge | Spatial contiguity very strongly supported (median d = 1.10); coherence supports eliminating distracting defects/noise. Text collisions or overlap would directly violate both principles (mayer2020designingmultimediainstruction pages 4-6, mayer2020designingmultimediainstruction pages 2-4, cavanagh2023usingcommonlyavailabletechnologies pages 4-6) | The no-overlap/no-placeholder/media-play checks are engineering QA rules rather than studied multimedia principles. The five-second blinded comprehension test appears sensible but no direct empirical validation was found in this literature set (mayer2020designingmultimediainstruction pages 4-6, cavanagh2023usingcommonlyavailabletechnologies pages 4-6) | Strong rationale from perception/learning theory, but the exact gate procedure is craft knowledge, not experimentally established for conference slides |
| R8 | Distinguish evidence types; prioritize direct measurement and independent validation over agent self-report and anecdote; include comparators, n, uncertainty for scientific claims | No direct CTML principle; adjacent support from visualization trust, provenance, and credibility research | Source citation and perceived expertise materially affect trust judgments; clarity/transparency are the most-cited trust factors; provenance information changes trust and accuracy perceptions, though sometimes in counterintuitive ways (mckinley2025trustworthybydesign pages 9-10, mckinley2025trustworthybydesign pages 14-16, feng2023examiningtheimpact pages 5-7, feng2023examiningtheimpact pages 3-5, feng2023examiningtheimpact pages 1-3) | No multimedia-learning experiments directly test an evidence hierarchy for scientific presentation slides. Provenance cues can lower trust even for authentic media if users misread them; source information helps, but trust is multifactorial (feng2023examiningtheimpact pages 27-29, feng2023examiningtheimpact pages 25-27, feng2023examiningtheimpact pages 23-25) | Support comes from HCI, misinformation, and data-visualization trust research rather than conference-presentation studies; still highly relevant for scientific credibility judgments (mckinley2025trustworthybydesign pages 3-4, mckinley2025trustworthybydesign pages 9-10, feng2023examiningtheimpact pages 1-3) |


*Table: This table maps each proposed slide-design rule to the strongest supporting research, effect sizes where available, and the main caveats. It is useful for distinguishing rules that are well-supported by multimedia learning evidence from those that are mainly craft knowledge or supported only by adjacent literatures.*

---

## 2. Assertion–Evidence Slide Research: Measured Benefits and Failure Modes

**Measured benefits.** The assertion–evidence (AE) approach—using a sentence-assertion headline supported by visual evidence rather than topic-phrase headlines with bullet lists—has been studied primarily by Alley, Garner, and colleagues. Garner and Alley (2013, as cited in multiple sources) found that AE presentations produced significantly fewer misconceptions and better comprehension of complex concepts compared to traditional topic-subtopic slides (alzayed2023assertionevidenceversustraditional pages 2-4). D'Angelo (2018) tested three conditions with undergraduates and found retention scores of 94% for AE slides, 87% for phrase-headline slides with added images, and 68% for bullet-point-only slides (dangelo2018powerpointpresentationsin pages 8-12). Alley et al. (2010) demonstrated that AE slides reduce projected text to approximately 18 words per minute, compared to 35–40 for common-practice slides, lowering the reading burden on audiences (alley2010projectedwordsper pages 1-3, alley2010projectedwordsper pages 12-14).

**Null results and failure modes.** Alzayed and Alzamel (2023) found that engineering students creating AE presentations experienced lower perceived cognitive workload than those using traditional PowerPoint, but there were no significant differences in comprehension quiz scores, motivation, self-efficacy, or perceived effort (alzayed2023assertionevidenceversustraditional pages 8-9, alzayed2023assertionevidenceversustraditional pages 6-8). Notably, 40% of AE-group participants did not prefer the structure for future use, with some wanting more detailed text on slides (alzayed2023assertionevidenceversustraditional pages 6-8). Miller and Alley (2017) documented organizational resistance: approximately 60% of industry participants encountered at least some resistance from managers, often because companies wanted slides to serve as standalone reference documents (miller2017theassertionevidenceapproach pages 4-8). Some advisors and managers wanted more data and text on slides and were skeptical of sentence assertions (miller2017theassertionevidenceapproach pages 4-8).

**Speaker credibility** has not been rigorously measured in the AE literature retrieved. The evidence base is strongest for audience comprehension and retention; claims about speaker credibility or persuasion effects remain largely anecdotal within the AE research program.

---

## 3. Doumont's Position vs. Alley and Tufte

Doumont's primary works (*Trees, maps, and theorems*; "The Three Laws of Professional Communication," IEEE TPC 2002) were not available as full text in this search. However, secondary references describe his framework. Pedwell et al. (2017) reference Doumont's three laws, including "maximize the signal-to-noise ratio," where "noise" is defined as "anything that could distract the audience." They note that Doumont's coherence concept aligns with Mayer's coherence principle—both advocate eliminating extraneous information (pedwell2017effectivevisualdesign pages 4-5, pedwell2017effectivevisualdesign pages 5-7).

**Differences from Alley:** Doumont's framework is broader and more structural than AE: it is concerned with overall message architecture (adapt to the audience; maximize signal-to-noise; use effective redundancy) rather than prescribing a specific slide layout. Alley's AE approach operationalizes some of these principles into a concrete template (sentence headline + visual evidence body), which Doumont would likely view as one valid implementation but not the only one.

**Differences from Tufte:** Tufte's critique (*The Cognitive Style of PowerPoint*, 2003) indicts the medium itself as inherently low-resolution and hierarchically fragmenting. Doumont, by contrast, argues that slides are not inherently evil—the problem lies in how they are used. His position is pragmatic: slides should serve the message, not replace it, and both verbal and visual channels carry important information ("a word is worth a thousand pictures, too").

**On the specific sub-questions (based on Doumont's known published positions):** (a) *Screenshots of software UIs*: Doumont would likely accept them provided they are cropped and annotated to maximize signal-to-noise ratio; a raw, uncropped UI screenshot would violate his second law by including distracting noise. (b) *Verbatim quotations*: He would caution that large blocks of projected text force the audience to read instead of listen, creating channel conflict; short, carefully selected quotations might be acceptable if they serve a clear communicative purpose. (c) *Videos as evidence*: Consistent with his pragmatic approach, videos would be acceptable when they are the most efficient way to convey dynamic information, provided they are properly cued and the audience knows what to watch for.

*Caveat: These positions on (a)–(c) are inferences from Doumont's published principles rather than direct quotations, as the full texts were not retrievable.*

---

## 4. Authenticity of Evidence in Presentations

**Direct research is sparse.** No controlled experiments were found directly comparing authentic screenshots or raw artifacts against stylized re-representations in scientific conference presentations. The evidence base must be assembled from adjacent literatures.

**Truthiness effect.** Newman et al. (2012) originally demonstrated that non-probative photographs (thematically related images that provide no actual evidence) inflate perceived truthfulness of claims—the "truthiness effect." However, Nadarevic et al. (2020) failed to replicate this effect across four experiments examining statements in social media contexts, finding that non-probative pictures had no significant effect on truth judgments (p = 0.295), while source credibility and repetition were strong predictors (nadarevic2020perceivedtruthof pages 5-6, nadarevic2020perceivedtruthof pages 12-14). This suggests the truthiness effect may be restricted to contexts where pictures are the only available judgment cue, and may not generalize straightforwardly to conference presentations where audience expertise and source information are salient.

**Provenance and trust.** Feng et al. (2023) studied how provenance information (creation, editing, and sharing metadata) affects trust in 595 participants. Provenance information generally lowered trust in deceptive composited media but sometimes paradoxically decreased trust in authentic content, because users confused provenance credibility with content credibility (feng2023examiningtheimpact pages 27-29, feng2023examiningtheimpact pages 25-27, feng2023examiningtheimpact pages 1-3). This suggests that showing "where evidence came from" is not straightforwardly trust-enhancing; interface and explanation matter.

**Data visualization trust.** McKinley et al. (2025) found that clarity (cited by 83.8% of participants), visualization type (48.6%), and source citation (29.7%) are the top factors driving trust in data visualizations. Polished, professional designs increase confidence while cluttered visuals reduce it; aesthetics matter but are secondary to clarity (mckinley2025trustworthybydesign pages 11-12, mckinley2025trustworthybydesign pages 9-10, mckinley2025trustworthybydesign pages 14-16). Franconeri et al. (2021) emphasize that annotation and highlighting direct attention more effectively than raw data, and that the "curse of knowledge" makes presenters overestimate how well audiences read unannotated visualizations (franconeri2021thescienceof pages 18-20, franconeri2021thescienceof pages 41-42).

**Implication for R2:** The literature supports the claim that *annotated, cropped, clearly labeled* artifacts will be more effective than either raw screenshots or fully re-typed text. However, the specific claim that "authentic screenshots" are superior to clean re-representations for trust has not been directly tested.

---

## 5. Redundancy: When On-Slide Text Helps vs. Hurts

Trypke et al. (2023) reviewed 63 studies and distinguished two types of redundancy: *content redundancy* (duplicated information across sources) and *working memory channel redundancy* (overloading a single processing channel). Their key findings (trypke2023twotypesof pages 13-14, trypke2023twotypesof pages 8-9, trypke2023twotypesof pages 12-13, trypke2023twotypesof pages 1-2, trypke2023twotypesof pages 3-4):

**When redundant text hurts:** Adding written text that fully duplicates narration to visuals typically harms learning by creating split attention between the text, the visual, and the spoken narration. The effect is strongest for longer texts with complex visuals. The classic redundancy principle (median d = 0.86) recommends graphics + narration without on-screen text (mayer2020designingmultimediainstruction pages 4-6, cavanagh2023usingcommonlyavailabletechnologies pages 4-6).

**When redundant text helps:** (1) Short keywords or labels accompanying narration improve learning compared to narration alone. (2) Non-native language learners benefit from combined narration + written text—one study found English-as-a-foreign-language learners receiving narration with written keywords outperformed those receiving narration or text alone (trypke2023twotypesof pages 8-9). (3) Older adults benefit from redundant text. (4) Learners with lower working memory capacity benefit. (5) When content is complex and learners are novices, content redundancy aids schema construction. (6) Learner-controlled pacing enhances the benefits of redundant text (trypke2023twotypesof pages 13-14, trypke2023twotypesof pages 11-12, trypke2023twotypesof pages 8-9).

**For quotation slides specifically:** No controlled experiments were found directly testing verbatim quotes as slide content. However, from the redundancy and modality literatures, the following design resolution can be inferred: a verbatim quote presented as projected text while the speaker simultaneously reads it aloud creates a classic redundancy violation. A more effective approach would be to project only the key phrase or sentence from the quote (signaling), let the audience read it silently, and then provide oral commentary that *extends* rather than *duplicates* the projected text—maintaining complementary rather than identical information across channels (trypke2023twotypesof pages 3-4, cavanagh2023usingcommonlyavailabletechnologies pages 4-6).

---

## 6. Final Ranked List of Rules by Evidence Strength

Based on the full body of evidence reviewed above, the eight rules are ranked from strongest to weakest empirical support, with specific modifications suggested by the literature:

| Rank | Rule | Evidence Tier | Suggested Modification (if any) |
|---|---|---|---|
| 1 | R3. Manage reading load vs. dwell time rather than using a fixed word cap | Strongly evidence-backed | Replace the 50% dwell-time threshold with a continuous reading-load metric such as projected words per minute; keep the no-fixed-cap idea, but specify that short keywords or labels are usually preferable to full duplicated text, especially when visuals are present (mayer2020designingmultimediainstruction pages 6-9, mayer2020designingmultimediainstruction pages 4-6, trypke2023twotypesof pages 13-14, trypke2023twotypesof pages 3-4, alley2010projectedwordsper pages 1-3, alley2010projectedwordsper pages 12-14) |
| 2 | R1. One communicative job per slide; for analytic claims use assertion–evidence | Strongly evidence-backed | Narrow the claim: the strongest evidence supports signaling, coherence, and visual evidence for analytic claims; note that AE gains are clearest for comprehension/retention, while motivation and self-efficacy gains are not consistently shown; keep a separate pattern for demo slides with “what to watch for” cues (alpizar2020ametaanalysisof pages 10-11, mayer2020designingmultimediainstruction pages 2-4, dangelo2018powerpointpresentationsin pages 8-12, alzayed2023assertionevidenceversustraditional pages 2-4, alzayed2023assertionevidenceversustraditional pages 8-9, alzayed2023assertionevidenceversustraditional pages 6-8) |
| 3 | R4. One slide, one beat; hold skeleton constant and shift emphasis | Strongly evidence-backed | No major change needed; clarify that the evidence supports cueing/signaling broadly, so dimming past elements and highlighting the current element should be treated as an attention-guidance technique whose benefits depend on not adding clutter or unnecessary motion (alpizar2020ametaanalysisof pages 1-3, koning2009towardsaframework pages 5-7, koning2009towardsaframework pages 3-5, koning2009towardsaframework pages 20-22, koning2009towardsaframework pages 22-24) |
| 4 | R7. Mechanical release gates plus a five-second comprehension test | Strongly evidence-backed for some components; should be modified for others | Keep hard QA gates for overlap, collisions, placeholders, and media failures because they prevent violations of contiguity/coherence; retain the five-second test as useful craft practice, but label it as unvalidated and not empirically calibrated at the ≥80% threshold (mayer2020designingmultimediainstruction pages 4-6, mayer2020designingmultimediainstruction pages 2-4, cavanagh2023usingcommonlyavailabletechnologies pages 4-6) |
| 5 | R2. Prefer faithful extraction of native artifacts over retyping or raw uncropped screenshots | Plausible-but-unverified craft knowledge | Add an explicit annotation rule: native artifacts should be cropped, enlarged, masked, and directly labeled; raw screenshots alone can violate coherence and overload viewers, and the literature supports clarity/annotation more strongly than “authentic screenshot” per se (mayer2020designingmultimediainstruction pages 4-6, mayer2020designingmultimediainstruction pages 2-4, franconeri2021thescienceof pages 41-42, mckinley2025trustworthybydesign pages 11-12, mckinley2025trustworthybydesign pages 9-10) |
| 6 | R8. Distinguish evidence types and rank stronger evidence above weaker evidence | Plausible-but-unverified craft knowledge | Recast the four-level ordering as a transparency heuristic rather than a validated universal hierarchy; keep requirements to show source, comparator, n, and uncertainty for scientific claims, but avoid claiming the exact ranking is empirically established across domains (mckinley2025trustworthybydesign pages 9-10, mckinley2025trustworthybydesign pages 14-16, feng2023examiningtheimpact pages 5-7, feng2023examiningtheimpact pages 27-29, feng2023examiningtheimpact pages 3-5, feng2023examiningtheimpact pages 1-3) |
| 7 | R6. Match the host deck’s visual system rather than introducing a new template mid-deck | Plausible-but-unverified craft knowledge | Keep as a consistency/coherence guideline, but present it as indirect inference from coherence, professionalism, and trust literature rather than a directly tested slide-design rule (mayer2020designingmultimediainstruction pages 2-4, mckinley2025trustworthybydesign pages 1-2, mckinley2025trustworthybydesign pages 13-14) |
| 8 | R5. Time budget from rehearsal, not slide count; rank optional beats for cuts | Plausible-but-unverified craft knowledge | Keep as practical advice, but frame it explicitly as craft knowledge informed by pacing/segmenting logic rather than as a research-backed rule; if desired, tie it to segmenting and optional-beat planning instead of claiming empirical superiority over slide-count heuristics (mayer2020designingmultimediainstruction pages 6-9, richter2016signalingtextpicturerelations pages 14-15, richter2016signalingtextpicturerelations pages 12-14) |


*Table: This table ranks the eight proposed slide-design rules from strongest to weakest empirical support. It also marks where the literature suggests narrowing, reframing, or softening a rule rather than treating it as a hard evidence-based law.*

### Summary of Evidence Tiers

**Strongly evidence-backed (Tier 1):** R3 (reading load management), R1 (assertion–evidence for analytical claims), R4 (progressive emphasis builds), and the core mechanical components of R7 (no overlap/contiguity violations). These rules map directly onto multimedia learning principles with large, replicated effect sizes from meta-analyses (richter2016signalingtextpicturerelations pages 9-10, alpizar2020ametaanalysisof pages 10-11, mayer2020designingmultimediainstruction pages 6-9, mayer2020designingmultimediainstruction pages 4-6, mayer2020designingmultimediainstruction pages 2-4, koning2009towardsaframework pages 5-7, alpizar2020ametaanalysisof pages 1-3).

**Plausible but unverified craft knowledge (Tier 2):** R2 (native artifact extraction), R8 (evidence hierarchy), R6 (visual system matching), and R5 (rehearsal-based timing). These rules are consistent with multimedia learning theory and adjacent trust/credibility research, but have not been directly tested in the form stated. The most important modification is for R2: the literature supports *annotated and cropped* artifacts more strongly than raw "authentic" screenshots per se, because clarity and signal-to-noise ratio are more empirically validated drivers of both comprehension and trust than authenticity alone (mckinley2025trustworthybydesign pages 11-12, mckinley2025trustworthybydesign pages 9-10, franconeri2021thescienceof pages 41-42).

**Key cross-cutting caveat:** The entire evidence base derives predominantly from controlled laboratory experiments with student learners in educational settings. Transfer to live conference presentations with expert audiences is plausible given the underlying cognitive mechanisms, but effect sizes, boundary conditions, and the relative importance of different principles may shift substantially in that context (alzayed2023assertionevidenceversustraditional pages 1-2, alley2010projectedwordsper pages 1-3). In particular, the expertise reversal effect—where design supports helpful for novices become redundant or harmful for experts—is a documented concern that applies to several rules, especially R3 and R4 (trypke2023twotypesof pages 13-14, koning2009towardsaframework pages 20-22).

References

1. (mayer2020designingmultimediainstruction pages 6-9): Richard E. Mayer. Designing multimedia instruction in anatomy: an evidence‐based approach. Clinical Anatomy, 33:2-11, Nov 2020. URL: https://doi.org/10.1002/ca.23265, doi:10.1002/ca.23265. This article has 64 citations and is from a peer-reviewed journal.

2. (mayer2020designingmultimediainstruction pages 4-6): Richard E. Mayer. Designing multimedia instruction in anatomy: an evidence‐based approach. Clinical Anatomy, 33:2-11, Nov 2020. URL: https://doi.org/10.1002/ca.23265, doi:10.1002/ca.23265. This article has 64 citations and is from a peer-reviewed journal.

3. (mayer2020designingmultimediainstruction pages 2-4): Richard E. Mayer. Designing multimedia instruction in anatomy: an evidence‐based approach. Clinical Anatomy, 33:2-11, Nov 2020. URL: https://doi.org/10.1002/ca.23265, doi:10.1002/ca.23265. This article has 64 citations and is from a peer-reviewed journal.

4. (alpizar2020ametaanalysisof pages 10-11): David Alpizar, Olusola O. Adesope, and Rachel M. Wong. A meta-analysis of signaling principle in multimedia learning environments. Educational Technology Research and Development, 68:2095-2119, Feb 2020. URL: https://doi.org/10.1007/s11423-020-09748-7, doi:10.1007/s11423-020-09748-7. This article has 266 citations and is from a domain leading peer-reviewed journal.

5. (richter2016signalingtextpicturerelations pages 9-10): Juliane Richter, Katharina Scheiter, and Alexander Eitel. Signaling text-picture relations in multimedia learning: a comprehensive meta-analysis. Educational Research Review, 17:19-36, Feb 2016. URL: https://doi.org/10.1016/j.edurev.2015.12.003, doi:10.1016/j.edurev.2015.12.003. This article has 351 citations and is from a highest quality peer-reviewed journal.

6. (richter2016signalingtextpicturerelations pages 14-15): Juliane Richter, Katharina Scheiter, and Alexander Eitel. Signaling text-picture relations in multimedia learning: a comprehensive meta-analysis. Educational Research Review, 17:19-36, Feb 2016. URL: https://doi.org/10.1016/j.edurev.2015.12.003, doi:10.1016/j.edurev.2015.12.003. This article has 351 citations and is from a highest quality peer-reviewed journal.

7. (richter2016signalingtextpicturerelations pages 12-14): Juliane Richter, Katharina Scheiter, and Alexander Eitel. Signaling text-picture relations in multimedia learning: a comprehensive meta-analysis. Educational Research Review, 17:19-36, Feb 2016. URL: https://doi.org/10.1016/j.edurev.2015.12.003, doi:10.1016/j.edurev.2015.12.003. This article has 351 citations and is from a highest quality peer-reviewed journal.

8. (trypke2023twotypesof pages 13-14): Melanie Trypke, Ferdinand Stebner, and Joachim Wirth. Two types of redundancy in multimedia learning: a literature review. Frontiers in Psychology, May 2023. URL: https://doi.org/10.3389/fpsyg.2023.1148035, doi:10.3389/fpsyg.2023.1148035. This article has 72 citations and is from a peer-reviewed journal.

9. (trypke2023twotypesof pages 8-9): Melanie Trypke, Ferdinand Stebner, and Joachim Wirth. Two types of redundancy in multimedia learning: a literature review. Frontiers in Psychology, May 2023. URL: https://doi.org/10.3389/fpsyg.2023.1148035, doi:10.3389/fpsyg.2023.1148035. This article has 72 citations and is from a peer-reviewed journal.

10. (trypke2023twotypesof pages 3-4): Melanie Trypke, Ferdinand Stebner, and Joachim Wirth. Two types of redundancy in multimedia learning: a literature review. Frontiers in Psychology, May 2023. URL: https://doi.org/10.3389/fpsyg.2023.1148035, doi:10.3389/fpsyg.2023.1148035. This article has 72 citations and is from a peer-reviewed journal.

11. (trypke2023twotypesof pages 12-13): Melanie Trypke, Ferdinand Stebner, and Joachim Wirth. Two types of redundancy in multimedia learning: a literature review. Frontiers in Psychology, May 2023. URL: https://doi.org/10.3389/fpsyg.2023.1148035, doi:10.3389/fpsyg.2023.1148035. This article has 72 citations and is from a peer-reviewed journal.

12. (dangelo2018powerpointpresentationsin pages 8-12): Larissa D'Angelo. Powerpoint presentations in the classroom: re-evaluating the genre. Language Value, pages 29-44, Dec 2018. URL: https://doi.org/10.6035/languagev.2018.10.3, doi:10.6035/languagev.2018.10.3. This article has 12 citations and is from a peer-reviewed journal.

13. (alzayed2023assertionevidenceversustraditional pages 2-4): Mohammad Alsager Alzayed and Dalal Alzamel. Assertion-evidence versus traditional powerpoint: an investigation of the impact of slide structure on engineering students’ cognitive load, motivation, and performance. Journal of Engineering Research, 11:329-339, Mar 2023. URL: https://doi.org/10.36909/jer.16963, doi:10.36909/jer.16963. This article has 4 citations.

14. (alzayed2023assertionevidenceversustraditional pages 8-9): Mohammad Alsager Alzayed and Dalal Alzamel. Assertion-evidence versus traditional powerpoint: an investigation of the impact of slide structure on engineering students’ cognitive load, motivation, and performance. Journal of Engineering Research, 11:329-339, Mar 2023. URL: https://doi.org/10.36909/jer.16963, doi:10.36909/jer.16963. This article has 4 citations.

15. (alzayed2023assertionevidenceversustraditional pages 6-8): Mohammad Alsager Alzayed and Dalal Alzamel. Assertion-evidence versus traditional powerpoint: an investigation of the impact of slide structure on engineering students’ cognitive load, motivation, and performance. Journal of Engineering Research, 11:329-339, Mar 2023. URL: https://doi.org/10.36909/jer.16963, doi:10.36909/jer.16963. This article has 4 citations.

16. (mckinley2025trustworthybydesign pages 11-12): Trustworthy by Design: The Viewer's Perspective on Trust in Data Visualization This article has 15 citations.

17. (mckinley2025trustworthybydesign pages 9-10): Trustworthy by Design: The Viewer's Perspective on Trust in Data Visualization This article has 15 citations.

18. (franconeri2021thescienceof pages 41-42): Steven L. Franconeri, Lace M. Padilla, Priti Shah, Jeffrey M. Zacks, and Jessica Hullman. The science of visual data communication: what works. Psychological Science in the Public Interest, 22:110-161, Dec 2021. URL: https://doi.org/10.1177/15291006211051956, doi:10.1177/15291006211051956. This article has 619 citations and is from a highest quality peer-reviewed journal.

19. (cavanagh2023usingcommonlyavailabletechnologies pages 4-6): Thomas M. Cavanagh and Christa Kiersch. Using commonly-available technologies to create online multimedia lessons through the application of the cognitive theory of multimedia learning. Educational Technology Research and Development, 71:1-21, Dec 2023. URL: https://doi.org/10.1007/s11423-022-10181-1, doi:10.1007/s11423-022-10181-1. This article has 209 citations and is from a domain leading peer-reviewed journal.

20. (mckinley2025trustworthybydesign pages 2-3): Trustworthy by Design: The Viewer's Perspective on Trust in Data Visualization This article has 15 citations.

21. (trypke2023twotypesof pages 1-2): Melanie Trypke, Ferdinand Stebner, and Joachim Wirth. Two types of redundancy in multimedia learning: a literature review. Frontiers in Psychology, May 2023. URL: https://doi.org/10.3389/fpsyg.2023.1148035, doi:10.3389/fpsyg.2023.1148035. This article has 72 citations and is from a peer-reviewed journal.

22. (alley2010projectedwordsper pages 1-3): Michael Alley, Joanna Garner, and Sarah Zappe. Projected words per minute: a window into the potential effectiveness of presentation slides. ArXiv, pages 15.1000.1-15.1000.14, 2010. URL: https://doi.org/10.18260/1-2--16059, doi:10.18260/1-2--16059. This article has 6 citations.

23. (alley2010projectedwordsper pages 12-14): Michael Alley, Joanna Garner, and Sarah Zappe. Projected words per minute: a window into the potential effectiveness of presentation slides. ArXiv, pages 15.1000.1-15.1000.14, 2010. URL: https://doi.org/10.18260/1-2--16059, doi:10.18260/1-2--16059. This article has 6 citations.

24. (pedwell2017effectivevisualdesign pages 4-5): Rhianna K. Pedwell, James A. Hardy, and Susan L. Rowland. Effective visual design and communication practices for research posters: exemplars based on the theory and practice of multimedia learning and rhetoric. Biochemistry and Molecular Biology Education, 45:249-261, May 2017. URL: https://doi.org/10.1002/bmb.21034, doi:10.1002/bmb.21034. This article has 74 citations and is from a peer-reviewed journal.

25. (alpizar2020ametaanalysisof pages 1-3): David Alpizar, Olusola O. Adesope, and Rachel M. Wong. A meta-analysis of signaling principle in multimedia learning environments. Educational Technology Research and Development, 68:2095-2119, Feb 2020. URL: https://doi.org/10.1007/s11423-020-09748-7, doi:10.1007/s11423-020-09748-7. This article has 266 citations and is from a domain leading peer-reviewed journal.

26. (koning2009towardsaframework pages 5-7): Björn B. de Koning, Huib K. Tabbers, Remy M. J. P. Rikers, and Fred Paas. Towards a framework for attention cueing in instructional animations: guidelines for research and design. Educational Psychology Review, 21:113-140, Apr 2009. URL: https://doi.org/10.1007/s10648-009-9098-7, doi:10.1007/s10648-009-9098-7. This article has 657 citations and is from a domain leading peer-reviewed journal.

27. (koning2009towardsaframework pages 3-5): Björn B. de Koning, Huib K. Tabbers, Remy M. J. P. Rikers, and Fred Paas. Towards a framework for attention cueing in instructional animations: guidelines for research and design. Educational Psychology Review, 21:113-140, Apr 2009. URL: https://doi.org/10.1007/s10648-009-9098-7, doi:10.1007/s10648-009-9098-7. This article has 657 citations and is from a domain leading peer-reviewed journal.

28. (koning2009towardsaframework pages 9-11): Björn B. de Koning, Huib K. Tabbers, Remy M. J. P. Rikers, and Fred Paas. Towards a framework for attention cueing in instructional animations: guidelines for research and design. Educational Psychology Review, 21:113-140, Apr 2009. URL: https://doi.org/10.1007/s10648-009-9098-7, doi:10.1007/s10648-009-9098-7. This article has 657 citations and is from a domain leading peer-reviewed journal.

29. (koning2009towardsaframework pages 20-22): Björn B. de Koning, Huib K. Tabbers, Remy M. J. P. Rikers, and Fred Paas. Towards a framework for attention cueing in instructional animations: guidelines for research and design. Educational Psychology Review, 21:113-140, Apr 2009. URL: https://doi.org/10.1007/s10648-009-9098-7, doi:10.1007/s10648-009-9098-7. This article has 657 citations and is from a domain leading peer-reviewed journal.

30. (koning2009towardsaframework pages 22-24): Björn B. de Koning, Huib K. Tabbers, Remy M. J. P. Rikers, and Fred Paas. Towards a framework for attention cueing in instructional animations: guidelines for research and design. Educational Psychology Review, 21:113-140, Apr 2009. URL: https://doi.org/10.1007/s10648-009-9098-7, doi:10.1007/s10648-009-9098-7. This article has 657 citations and is from a domain leading peer-reviewed journal.

31. (koning2009towardsaframework pages 14-16): Björn B. de Koning, Huib K. Tabbers, Remy M. J. P. Rikers, and Fred Paas. Towards a framework for attention cueing in instructional animations: guidelines for research and design. Educational Psychology Review, 21:113-140, Apr 2009. URL: https://doi.org/10.1007/s10648-009-9098-7, doi:10.1007/s10648-009-9098-7. This article has 657 citations and is from a domain leading peer-reviewed journal.

32. (mckinley2025trustworthybydesign pages 1-2): Trustworthy by Design: The Viewer's Perspective on Trust in Data Visualization This article has 15 citations.

33. (mckinley2025trustworthybydesign pages 13-14): Trustworthy by Design: The Viewer's Perspective on Trust in Data Visualization This article has 15 citations.

34. (mckinley2025trustworthybydesign pages 14-16): Trustworthy by Design: The Viewer's Perspective on Trust in Data Visualization This article has 15 citations.

35. (feng2023examiningtheimpact pages 5-7): K. J. Kevin Feng, Nick Ritchie, Pia Blumenthal, Andy Parsons, and Amy X. Zhang. Examining the impact of provenance-enabled media on trust and accuracy perceptions. Proceedings of the ACM on Human-Computer Interaction, 7:1-42, Sep 2023. URL: https://doi.org/10.1145/3610061, doi:10.1145/3610061. This article has 67 citations and is from a domain leading peer-reviewed journal.

36. (feng2023examiningtheimpact pages 3-5): K. J. Kevin Feng, Nick Ritchie, Pia Blumenthal, Andy Parsons, and Amy X. Zhang. Examining the impact of provenance-enabled media on trust and accuracy perceptions. Proceedings of the ACM on Human-Computer Interaction, 7:1-42, Sep 2023. URL: https://doi.org/10.1145/3610061, doi:10.1145/3610061. This article has 67 citations and is from a domain leading peer-reviewed journal.

37. (feng2023examiningtheimpact pages 1-3): K. J. Kevin Feng, Nick Ritchie, Pia Blumenthal, Andy Parsons, and Amy X. Zhang. Examining the impact of provenance-enabled media on trust and accuracy perceptions. Proceedings of the ACM on Human-Computer Interaction, 7:1-42, Sep 2023. URL: https://doi.org/10.1145/3610061, doi:10.1145/3610061. This article has 67 citations and is from a domain leading peer-reviewed journal.

38. (feng2023examiningtheimpact pages 27-29): K. J. Kevin Feng, Nick Ritchie, Pia Blumenthal, Andy Parsons, and Amy X. Zhang. Examining the impact of provenance-enabled media on trust and accuracy perceptions. Proceedings of the ACM on Human-Computer Interaction, 7:1-42, Sep 2023. URL: https://doi.org/10.1145/3610061, doi:10.1145/3610061. This article has 67 citations and is from a domain leading peer-reviewed journal.

39. (feng2023examiningtheimpact pages 25-27): K. J. Kevin Feng, Nick Ritchie, Pia Blumenthal, Andy Parsons, and Amy X. Zhang. Examining the impact of provenance-enabled media on trust and accuracy perceptions. Proceedings of the ACM on Human-Computer Interaction, 7:1-42, Sep 2023. URL: https://doi.org/10.1145/3610061, doi:10.1145/3610061. This article has 67 citations and is from a domain leading peer-reviewed journal.

40. (feng2023examiningtheimpact pages 23-25): K. J. Kevin Feng, Nick Ritchie, Pia Blumenthal, Andy Parsons, and Amy X. Zhang. Examining the impact of provenance-enabled media on trust and accuracy perceptions. Proceedings of the ACM on Human-Computer Interaction, 7:1-42, Sep 2023. URL: https://doi.org/10.1145/3610061, doi:10.1145/3610061. This article has 67 citations and is from a domain leading peer-reviewed journal.

41. (mckinley2025trustworthybydesign pages 3-4): Trustworthy by Design: The Viewer's Perspective on Trust in Data Visualization This article has 15 citations.

42. (miller2017theassertionevidenceapproach pages 4-8): Elizabeth Miller and Michael Alley. The assertion-evidence approach to technical presentations: overcoming resistance in professional settings. ArXiv, Jun 2017. URL: https://doi.org/10.18260/1-2--28944, doi:10.18260/1-2--28944. This article has 2 citations.

43. (pedwell2017effectivevisualdesign pages 5-7): Rhianna K. Pedwell, James A. Hardy, and Susan L. Rowland. Effective visual design and communication practices for research posters: exemplars based on the theory and practice of multimedia learning and rhetoric. Biochemistry and Molecular Biology Education, 45:249-261, May 2017. URL: https://doi.org/10.1002/bmb.21034, doi:10.1002/bmb.21034. This article has 74 citations and is from a peer-reviewed journal.

44. (nadarevic2020perceivedtruthof pages 5-6): Lena Nadarevic, Rolf Reber, Anne Josephine Helmecke, and Dilara Köse. Perceived truth of statements and simulated social media postings: an experimental investigation of source credibility, repeated exposure, and presentation format. Cognitive Research: Principles and Implications, Nov 2020. URL: https://doi.org/10.1186/s41235-020-00251-4, doi:10.1186/s41235-020-00251-4. This article has 187 citations.

45. (nadarevic2020perceivedtruthof pages 12-14): Lena Nadarevic, Rolf Reber, Anne Josephine Helmecke, and Dilara Köse. Perceived truth of statements and simulated social media postings: an experimental investigation of source credibility, repeated exposure, and presentation format. Cognitive Research: Principles and Implications, Nov 2020. URL: https://doi.org/10.1186/s41235-020-00251-4, doi:10.1186/s41235-020-00251-4. This article has 187 citations.

46. (franconeri2021thescienceof pages 18-20): Steven L. Franconeri, Lace M. Padilla, Priti Shah, Jeffrey M. Zacks, and Jessica Hullman. The science of visual data communication: what works. Psychological Science in the Public Interest, 22:110-161, Dec 2021. URL: https://doi.org/10.1177/15291006211051956, doi:10.1177/15291006211051956. This article has 619 citations and is from a highest quality peer-reviewed journal.

47. (trypke2023twotypesof pages 11-12): Melanie Trypke, Ferdinand Stebner, and Joachim Wirth. Two types of redundancy in multimedia learning: a literature review. Frontiers in Psychology, May 2023. URL: https://doi.org/10.3389/fpsyg.2023.1148035, doi:10.3389/fpsyg.2023.1148035. This article has 72 citations and is from a peer-reviewed journal.

48. (alzayed2023assertionevidenceversustraditional pages 1-2): Mohammad Alsager Alzayed and Dalal Alzamel. Assertion-evidence versus traditional powerpoint: an investigation of the impact of slide structure on engineering students’ cognitive load, motivation, and performance. Journal of Engineering Research, 11:329-339, Mar 2023. URL: https://doi.org/10.36909/jer.16963, doi:10.36909/jer.16963. This article has 4 citations.