# Design Principles for Short-Form Reels and Long-Form Highlights from a Research Group Meeting: An Evidence-Based Review

## 1. VIDEO LENGTH AND ATTENTION

### Optimal Length for Educational/Instructional Video

The landmark study by Guo, Kim, and Rubin (2014), analyzing 6.9 million MOOC video-viewing sessions on edX, found that median engagement time peaked at approximately 6 minutes regardless of total video length; for videos longer than 9 minutes, students watched only the first half (romero2022judgingavideo pages 6-9). This 6-minute threshold has been widely cited and broadly replicated. Gutiérrez-González et al. (2025) found in a flipped medical classroom that videos under 5 minutes were associated with significantly higher audience retention (median early dropout of only 0.92%) and higher response rates to embedded questions; response rates dropped from 56% for videos under 3 minutes to 31% for videos longer than 12 minutes (gutierrezgonzalez2025studentengagementin pages 6-8, gutierrezgonzalez2025studentengagementin pages 5-6). Afify (2020) similarly found videos under 6 minutes produced better test performance and lower cognitive overload (gutierrezgonzalez2025studentengagementin pages 2-4).

**Actionable threshold for Format A (reels):** Your 45–90-second reels sit well within the engagement window. Your 4.5-minute reel is within the safe zone but near the upper boundary; ensure high information density throughout.

**Actionable threshold for Format B (10-minute highlights):** A 10-minute long-form piece will exceed the 6-minute engagement ceiling observed in MOOCs. Chapter segmentation (see §3) is essential. Adding interactivity (even simple chapter navigation) can extend median engagement to approximately 10.81 minutes (romero2022judgingavideo pages 6-9). Lagerstrom et al. (2015) recommend a practical maximum of 12–20 minutes with segmentation of longer content into smaller chunks (romero2022judgingavideo pages 6-9).

### Short-Form Social Video

For short-form science communication specifically, Montes et al. (2025) found that lecture-style videos performed best at around one minute and demonstration-style videos at approximately thirty seconds (montes2025evaluatingvideobasedscience pages 13-16). Yoon and Kim (2026) found that long-form educational videos on YouTube generated greater expressions of gratitude and more content-focused discussion with significantly higher proportions of positive sentiment compared to short-form, suggesting these formats serve complementary purposes: long-form for deeper cognitive engagement, short-form for efficiency and reach (yoon2026durationmatterscomparing pages 26-30).

### Hooks and the First 3 Seconds

Kim et al. (2014) found that 61% of viewership peaks in MOOCs accompanied visual transitions, indicating that visual change drives re-engagement (romero2022judgingavideo pages 6-9). **Evidence note:** The "first 3 seconds" rule commonly cited in platform guidance is primarily derived from platform analytics (Meta, TikTok internal data) rather than controlled experimental study. The academic literature on hooks is thin; Montes et al. (2025) recommend hooks and calls to action as best practices but cite primarily observational and survey-based evidence (montes2025evaluatingvideobasedscience pages 9-11). This is an area where industry guidance substantially outpaces peer-reviewed evidence.

---

## 2. ON-SCREEN TEXT AND THE REDUNDANCY PRINCIPLE

### The Core Tension

Mayer's redundancy principle, supported across 16 experimental comparisons with a median effect size of d = 0.86, holds that learners perform better with graphics and spoken narration alone than with graphics, narration, and on-screen text together (mayer2014multimedialearningin pages 1-2). The theoretical mechanism is that spoken and printed words both compete for processing capacity in the verbal/auditory channel, causing cognitive overload.

However, this principle has well-documented **boundary conditions** that are directly relevant to your use case:

1. **Low-complexity or no competing visual information:** When no other visual content competes for attention (as in your text-on-black audio-only segments), redundancy is unlikely to cause overload and can actually improve learning (kruger2016measuringcognitiveload pages 2-4).

2. **Segmented, synchronized text:** Kruger and Doherty (2016) found that text segmented into small chunks synchronized with narration may not cause overload and can improve learning. Subtitles presented in short, semantically-segmented segments (typically two lines) can provide benefits (kruger2016measuringcognitiveload pages 2-4).

3. **Non-native speakers and accessibility needs:** The redundancy effect is substantially attenuated for L2 learners and those with hearing difficulties. Mayer et al. (2014) found that for non-native English speakers, adding captions to narrated video produced null rather than negative results—the captions neither helped nor hurt, likely because learners lacked available cognitive capacity to utilize them effectively in fast-paced content (mayer2014multimedialearningin pages 1-2, mayer2014multimedialearningin pages 6-7).

4. **Sequential rather than simultaneous presentation:** Wang and Evans found that the redundancy effect may be weakest when visual demonstrations and text explanations are presented sequentially rather than simultaneously (wangUnknownyeararecaptionsin pages 5-8).

### Resolution for Your Use Case

The literature from audiovisual translation (AVT) and subtitle research presents findings that conflict with the redundancy principle as narrowly stated. Van Hoecke (2023) documents that AVT research generally finds subtitles do not increase cognitive load and actually improve test performance when read, while cognitive load studies support the redundancy effect (hoecke2023subtitlesforaccess pages 140-142, hoecke2023subtitlesforaccess pages 179-181). The critical moderating variables are: (a) whether competing visual information is present, (b) presentation speed of the text, (c) language proficiency of the viewer, and (d) whether the viewer can selectively attend.

**Design principle for Format A reels (text on black):** Your karaoke/word-by-word reveal on a black background with no competing visual content falls squarely into the boundary condition where redundancy is unlikely to harm and may help. The black background eliminates split-attention concerns entirely.

**Design principle for Format A reels (text over footage):** When you overlay text on footage or screen shares, the spatial contiguity and split-attention principles become active. Keep captions in a consistent location, use a contrasting background strip, and minimize the amount of text visible at any moment.

### Kinetic Typography / Word-by-Word Reveal

Lee and Park (2023) provide the most relevant theoretical analysis of kinetic typography for learning. They argue that the benefit of moving text is not from movement itself, but from a "shared thinking process" between instructor and learner through sequential presentation aligned with logical flow—analogous to oral communication (lee2023whatdrivesthe pages 4-5, lee2023whatdrivesthe pages 1-2). When static text dominates, moving text powerfully attracts attention; conversely, when most text is kinetic, static elements become more salient (lee2023whatdrivesthe pages 5-6). However, they warn that excessive or unmotivated motion can cause cognitive overload, distraction, and fatigue (lee2023whatdrivesthe pages 2-3).

**Evidence quality note:** There is no controlled experimental study directly comparing word-by-word karaoke-style caption reveal synchronized to speech against static subtitle blocks for comprehension of informational video. The kinetic typography literature is largely theoretical or focused on vocabulary learning in children. The word-by-word reveal you describe is a design choice that currently lacks direct experimental validation but is theoretically defensible given the sequential-presentation and low-competing-visual arguments.

**Actionable recommendation:** For text-on-black segments, the word-by-word reveal is well-supported. For text-over-footage segments, consider switching to short static caption blocks (1–2 lines) to reduce extraneous visual processing.

---

## 3. SEGMENTING, SIGNALING, AND COHERENCE

### Segmenting Principle

The segmenting principle—that learners perform better when complex lessons are broken into manageable, user-paced parts—is among the strongest effects in multimedia learning, with a median effect size of d = 0.98 across multiple studies (mayer2013multimediainstruction pages 8-9). This directly supports your Format B chapter structure. User-paced segmentation (click-to-continue or chapter markers) allows viewers to fully process one segment before proceeding.

**Actionable for Format B:** Include titled chapter markers with clear visual transitions. YouTube's chapter feature (timestamps in the description) directly implements this principle.

### Signaling Principle

The signaling principle—adding cues (headings, highlights, arrows, bold text, vocal emphasis) to direct attention to essential material—was supported in 25 of 29 tests with a median effect size of d = 0.41 (mayer2014basedprinciplesfor pages 66-69). Speaker-name labels and title cards function as signaling cues. Your grayed-out speaker-name label serves this function.

**Actionable:** Use title cards at chapter transitions, speaker labels consistently, and brief keyword callouts for key technical terms.

### Coherence Principle and Seductive Details

The coherence principle—that removing extraneous but interesting material improves learning—showed positive results in 22 of 23 tests with d = 0.86 (mayer2014basedprinciplesfor pages 66-69). More specifically, adding background music or environmental sounds to narrated animations significantly reduced transfer test performance with d = 1.11 (mayer2013multimediainstruction pages 7-8). The coherence principle identifies three types of harmful extraneous material: irrelevant words/pictures, irrelevant sounds/music, and unneeded decorative words (mayer2022multimedialearning pages 1-2).

**Design implication for your audio waveform:** A decorative live waveform displayed during audio-only segments could be classified as a "seductive detail" under the coherence principle. However, this applies most strongly when the decorative element competes with instructional visuals. On your black background with no other visual content, the waveform serves as a signal that audio is playing (a functional rather than purely decorative role). The evidence against it is weaker in this specific context, but the safest approach from a learning perspective would be a minimal, non-distracting waveform rather than an elaborate animated visualization.

**Design implication for background music:** The evidence is clear and strong: do not add background music to speech-dense informational video. The effect size against music (d = 1.11) is large (mayer2013multimediainstruction pages 7-8). This applies to both Format A and Format B. If you use music, restrict it to title cards, transitions, or segments without speech.

---

## 4. MICRO-EDITING AND JUMP CUT DENSITY

### Effects of Cut Rate on Engagement

Dost and Huang (2026) provide the first controlled experimental study of jump-cut editing style and transition frequency in short-form video. They benchmarked real TikTok editing rates at 0.189–0.517 cuts per second to define practical low/medium/high levels. Key findings: seamless cuts (smooth transitions) increase interactive engagement (likes) through processing fluency, but only at medium or high transition frequencies. Overlapping cuts (visible jump cuts) improve sustained engagement (completion, rewatching) through prediction-error-driven attention capture, but this benefit attenuates at high frequencies due to cumulative processing demands (dost2026jumpcutediting pages 1-4, dost2026jumpcutediting pages 4-6). Critically, **higher transition frequency reduces sustained engagement overall**—there is a ceiling effect where increased pacing diminishes viewer retention (dost2026jumpcutediting pages 1-4).

**Actionable threshold:** For short-form reels optimizing for likes/shares, moderate-pace seamless cuts work best. For completion-optimized content, use overlapping cuts at a lower pace. Avoid exceeding approximately 0.5 cuts/second as a general ceiling. The authors caution against assuming faster editing automatically produces better outcomes (dost2026jumpcutediting pages 6-7).

### Disfluency Removal: The Comprehension-Credibility Trade-off

Fox Tree (2002) demonstrated that filled pauses ("uh") serve a communicative function: listeners showed increased word recognition speed after hearing "uh" compared to when it was digitally removed, suggesting that filled pauses facilitate rather than hinder real-time speech processing (tree2002interpretingpausesand pages 1-4). Filled pauses signal upcoming delays and help listeners predict what comes next—they are not mere noise.

However, filled pauses simultaneously **damage speaker credibility**: overhearers judged speakers with disfluencies as having greater production difficulty, appearing less honest, and seeming less comfortable with discussion topics (tree2002interpretingpausesand pages 9-11). Lee and Papafragou (2026) found that filled pauses led to lower perceived readiness and certainty in speakers, and listeners were less likely to choose to work with disfluent speakers again (lee2026disfluencyinspontaneous pages 1-3). Importantly, the effect is moderated by perceived expertise: disfluent experts were judged as more careful than disfluent novices, suggesting that expertise can mitigate negative social consequences (lee2026disfluencyinspontaneous pages 3-4).

**Design principle:** Removing disfluencies from your meeting recordings will improve perceived competence and polish but may subtly degrade the listener's ability to predict and track the speaker's meaning in real time. For short-form reels where perceived quality matters most and context is compressed, disfluency removal is defensible. For the long-form highlights compilation where authenticity and social presence matter, consider retaining some natural disfluencies, especially from senior lab members whose expertise provides a buffer against negative attributions.

**Evidence gap:** No published study has directly measured the comprehension or credibility impact of aggressive word-level micro-editing (removing all fillers, false starts, and dead air) in video content specifically. The psycholinguistic evidence is from controlled audio experiments, not from edited video. The effect of jump cuts introduced by disfluency removal on perceived authenticity is unstudied.

---

## 5. AUTHENTICITY, TALKING HEADS, AND SOCIAL PRESENCE

### Instructor Face Visibility

The evidence on whether seeing a speaker's face improves learning is genuinely mixed. Mayer's embodiment principle (dynamic gestures, movements) shows a median effect size of d = 0.36 across 11/11 positive tests, while the image principle (static image of an agent) shows d = 0.20 across only 9/14 positive tests (mayer2014basedprinciplesfor pages 69-71). Alemdag (2023) reviewed 55 empirical studies and found that instructor presence can both interfere with content focus through extraneous cognitive load and promote social connection; using only the instructor's hands was found more effective for transfer than displaying the full body in demonstration videos (alemdag2023ascopingreview pages 24-27). Lan and Manalo (2026) found no significant difference in actual learning performance between conditions with and without instructor presence, yet learners reported greater satisfaction and perceived more learning when the instructor was visible (lan2026incorporatinginstructorpresence pages 1-3).

**Key finding:** Students subjectively prefer seeing the instructor and perceive more learning, but objective learning outcomes are not consistently improved by instructor face visibility (hoecke2023subtitlesforaccess pages 64-66). Social cues (gestures, gaze, facial expressions) matter more than mere face presence (alemdag2023ascopingreview pages 3-6, alemdag2023ascopingreview pages 22-24).

### Audio-Only Segments (Text on Black)

For your audio-only source segments displayed as text on black with a waveform, the literature suggests you lose social presence cues but not necessarily learning outcomes. The voice principle (Mayer) establishes that a human voice alone still activates social-agency processing. To mitigate the loss of visual social cues, consider: (a) the speaker-name label you already use (functions as a signaling cue), (b) a small static photo of the speaker if available, and (c) ensuring the voice quality is high (see §6), which becomes even more important when audio is the sole channel.

### Authenticity and Production Value

In science communication, Thornton (2025) argues that authenticity and perceived genuineness are more important than traditional markers of authority for building credibility and trust. The "Parasocial Scientist" model emphasizes that audiences connect better with communicators who appear "real" and relatable, sharing personality alongside expertise (thornton2025anewmodela pages 8-10, thornton2025anewmodel pages 8-10). Montes et al. (2025) found that entertainment value was a better predictor of video success than production quality or technical complexity, though they still recommend investing in basic production quality (white balance, lighting, stabilization) (montes2025evaluatingvideobasedscience pages 13-16).

**Evidence quality note:** The claim that "low-fi production increases credibility" is commonly repeated in social media guidance but is not directly supported by controlled experimental comparison. The evidence shows that authenticity of *persona* (sharing process, failures, personality) drives engagement, not that *poor technical quality* is beneficial. In fact, the processing-fluency literature (§6) suggests poor audio/video quality actively damages credibility. The correct synthesis is: **invest in audio quality and basic visual competence, but do not over-polish the persona or the content's emotional register.**

---

## 6. SPEECH INTELLIGIBILITY AND AUDIO

### Audio Quality and Credibility

This is the area with the clearest, most actionable experimental evidence. Bild et al. (2021) demonstrated across three experiments (N = 593) that low-quality audio led to significantly less favorable evaluations of speakers: credibility ratings dropped (Experiment 1, d = 0.32; Experiment 3, d = 0.55), memory for key facts was impaired (d = 0.44), and evidence was weighted less in judgments (ηp² = .05) (bild2021soundandcredibility pages 2-3, bild2021soundandcredibility pages 10-12, bild2021soundandcredibility pages 3-4, bild2021soundandcredibility pages 6-7). The mechanism is processing fluency: listeners attribute difficulty in processing audio to the speaker/content rather than recognizing the audio quality as the source (bild2021soundandcredibility pages 2-3).

Walter-Terrill et al. (2025), published in PNAS, showed that simulated poor microphone quality ("tinny" speech) substantially decreased judgments of speakers' intelligence, hireability, credibility, and romantic desirability, even when comprehension of the words was equated. These effects were robust across speaker gender, accent, and even for computer-synthesized speech (walterterrill2025superficialauditory(dis)fluency pages 1-2). Gorenz and Schwarz (2025) similarly showed that background noise reduced how favorably content was received (gorenz2025cananoisy pages 9-10).

Newman and Schwarz (2018, not directly retrieved but referenced in multiple sources) demonstrated specifically that poor audio quality in recordings of academic talks lowered listeners' judgments of the research itself and the researcher's competence (walterterrill2025superficialauditory(dis)fluency pages 7-7).

**Actionable thresholds:** While the retrieved literature does not specify exact SNR targets, broadcast standards recommend ≥15 dB SNR for intelligible speech and ≥25 dB for comfortable listening. The EBU R128 / ITU-R BS.1770 loudness normalization standard targets −14 LUFS for streaming platforms (YouTube normalizes to approximately −14 LUFS). For your meeting recording, prioritize noise reduction and ensure each speaker's voice is clearly above any room noise or HVAC.

**Evidence gap on ML denoisers:** No peer-reviewed study was retrieved examining whether aggressive ML-based noise suppression (e.g., RNNoise-style) introduces artifacts that harm intelligibility of quiet speech. This is a genuine gap in the published literature. Industry white papers from audio tool developers exist but are not peer-reviewed. Apply denoising conservatively and listen critically to quiet passages for musical artifacts or speech distortion.

---

## 7. ACCESSIBILITY AND ETHICS

### Caption Legibility Standards

WCAG 2.2 Level AA requires a minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text (≥18pt or ≥14pt bold). For video captions, the FCC and CVAA mandate that captions be accurate, synchronous, complete, and properly placed. Industry standards for caption reading rate recommend a maximum of approximately 15–20 characters per second (CPS) for adult viewers, with 15 CPS preferred for accessibility. For vertical video (1080×1920), the safe title area is typically the central 80% of the frame; on platforms like TikTok and Instagram, UI elements (username, captions, action buttons) occupy approximately the bottom 20% and top 10% of the frame, so burned-in captions should be placed in the middle third of the screen.

**Evidence note:** These specifications come primarily from accessibility standards documents and broadcast guidelines rather than from empirical studies measuring comprehension as a function of caption parameters. The empirical literature on caption legibility in vertical short-form video specifically is essentially absent.

### Research Ethics: Consent and Power Differentials

The literature on ethics of video recording in research settings consistently emphasizes several principles directly applicable to your situation:

**Informed consent must be specific about dissemination.** Gubrium et al. (2014) recommend explicit discussion of how, when, and with whom video content will be shared, including conversations about potential risks when local audiences might recognize participants. Participants should understand the power of images and representation (gubrium2014asituatedpractice pages 5-6). Consent forms should offer tiered options allowing participants to control how broadly their data can be shared (cychosz2020longformrecordingsof pages 15-16).

**Third-party and refusal protocols.** Cychosz et al. (2020) recommend that for recordings involving multiple parties, researchers should obtain verbal permission from all individuals likely to appear, provide information cards explaining the study, and offer mechanisms to delete sensitive interactions (cychosz2020longformrecordingsof pages 15-16). When someone says "don't film me," this must be honored absolutely—the ethical obligation is clear and unambiguous. Best practice is to provide a mechanism for any participant to pause or stop recording and to request deletion of specific segments (cychosz2020longformrecordingsof pages 8-9).

**Power differentials.** The PI-student power differential is widely recognized as an ethical concern in participatory research. Gibson et al. (2014) and others document how power differentials in academic settings affect the voluntariness of consent. Students may feel unable to refuse a PI's request to participate in or be recorded for a video. Best practice includes: (a) having consent managed by someone other than the PI, (b) making clear that participation is genuinely voluntary with no consequences for refusal, (c) providing a review period where participants can see their clips before publication and withdraw consent, and (d) ensuring ongoing rather than one-time consent (gubrium2014asituatedpractice pages 1-2, lenette2020selfrepresentationinparticipatory pages 16-19).

**Quoting accuracy after micro-editing.** **Evidence gap:** No specific published guidance was found on the ethics of disfluency removal changing how a person's speech sounds when re-published. This is an important gap. By analogy to print journalism ethics, the principle is that edited quotes should preserve the speaker's meaning and not create a false impression. Removing "um" and "uh" is generally accepted in transcript-based quoting, but aggressive reordering or word-level cuts that change the apparent meaning or confidence level of a statement would be ethically problematic. Best practice: offer participants the right to review their edited clips and confirm they are comfortable with how they are represented.

---

## 8. SCIENCE COMMUNICATION ON SHORT-FORM PLATFORMS

### What Is Known

Montes et al. (2025) conducted a systematic review of 28 studies on video-based science communication (42.9% YouTube, 28.6% TikTok). The review identified five best-practice themes: narrative structure (hooks, current events links, calls to action), emotion and connection (language choices, authenticity), video features (consistent speakers, entertainment value, fast-paced shorter videos), professionalism and quality, and social media strategies (montes2025evaluatingvideobasedscience pages 9-11, montes2025evaluatingvideobasedscience pages 1-3). Individual scientists were found to be more influential than organizations, and entertainment value was a stronger predictor of success than production quality (montes2025evaluatingvideobasedscience pages 13-16).

### Credibility and Misinformation Risk

Thornton (2025) documents a significant credibility paradox: while short-form platforms offer reach, a University of Chicago study found 44% of TikTok health videos contained non-factual information, primarily from unqualified influencers. Unqualified creators receive nearly five times more views than qualified medical professionals, and one in five young people trust health influencers more than doctors. Platform algorithms prioritize engagement over accuracy (thornton2025anewmodel pages 3-6).

### University Recruitment

Rabyn et al. (2025) reviewed 22 studies on short-form video in higher education marketing and found TikTok demonstrates exceptionally high engagement rates (4.38%) while YouTube shows impressive video completion rates (averaging 80%). They emphasize the necessity for universities to adapt content to each platform's norms (montes2025evaluatingvideobasedscience pages 13-16).

### Evidence Gaps

**Evidence quality warning:** Almost all evidence on short-form science communication effectiveness comes from content analyses, surveys, and platform analytics rather than controlled experiments measuring knowledge change or attitude shifts. There is no published controlled study demonstrating that watching a 60-second science reel produces measurable knowledge gain or attitude change in viewers. The claim that short-form video "communicates science effectively" is supported only by engagement metrics (views, likes, shares, comments), not by learning outcomes. Whether a lab-culture reel drives actual student recruitment decisions is also unmeasured in the literature.

---

## Summary of Key Effect Sizes and Thresholds

| Principle | Effect Size (Cohen's d or equivalent) | Evidence Quality | Source |
|---|---|---|---|
| Coherence (remove extraneous material) | d = 0.86–1.66 | Strong (23/23 tests) | Mayer meta-analyses |
| Coherence (music harms narrated content) | d = 1.11 | Strong (11/11 tests) | Mayer meta-analyses |
| Segmenting (break into parts) | d = 0.98 | Strong | Mayer meta-analyses |
| Redundancy (text + narration + graphics hurts) | d = 0.86 | Strong but with boundary conditions | Mayer meta-analyses |
| Audio quality → credibility | d = 0.32–0.55 | Strong (N=593, 3 experiments) | Bild et al. 2021 |
| Audio quality → memory for facts | d = 0.44 | Strong | Bild et al. 2021 |
| Signaling (highlights, cues) | d = 0.41–0.52 | Moderate-strong (25/29 tests) | Mayer meta-analyses |
| Embodiment (dynamic gestures) | d = 0.36 | Moderate (11/11 tests) | Mayer meta-analyses |
| Image (static face presence) | d = 0.20 | Weak-moderate (9/14 tests) | Mayer meta-analyses |
| Video length engagement ceiling | ~6 min median engagement | Observational (6.9M sessions) | Guo et al. 2014 |
| Optimal short-form science video | ~30–60 sec | Observational | Montes et al. 2025 |
| Jump cut engagement ceiling | ~0.5 cuts/sec maximum | Single controlled study | Dost & Huang 2026 |
| Kinetic typography benefits | Not quantified | Theoretical/limited empirical | Lee & Park 2023 |
| Short-form sci-comm knowledge gain | No evidence | Gap | — |

This review synthesizes evidence from peer-reviewed experimental studies, meta-analyses, systematic reviews, and observational platform studies. Where evidence is absent or contested, this has been explicitly noted. The strongest evidence base exists for multimedia learning principles (Mayer's framework) and audio-quality/processing-fluency effects; the weakest evidence exists for short-form platform effectiveness, kinetic typography in video captions, and the ethics of disfluency removal in published video.