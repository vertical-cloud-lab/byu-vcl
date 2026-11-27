# Revision notes for v3

**What this file is:** the changelog from [`manuscript-v2.md`](manuscript-v2.md) to [`manuscript-v3.md`](manuscript-v3.md); what happened to every `[NEEDED]` marker in v2; the evidence gathered on 2026-10-10; and the text to use if the three missing repositories do or do not appear. The per-person asks are in [`sign-off-checklist.md`](sign-off-checklist.md).

**Ownership.** Sterling G. Baird owns the revision and is corresponding author. Seth Leavitt, who directed v2, has left the group and stays an author for that work, subject to Seth's consent (SL-1).

**Text of record.** v1 (`manuscript-v1.md`, verified against the as-submitted arXiv `.docx` that Brenden Pelkie sent). Tonio Buonassisi's 13 December 2024 draft and Brenden's `.docx` both precede v1, so neither was merged. Tonio's reading of the decision letter is the design brief for v3:

> "My read of Joshua Schrier's (the editor's) email, is that he's asking us to present a strong hypothesis in the manuscript, and support the hypothesis with examples throughout the remainder of the manuscript."

---

## 1. What changed from v2

| Area | v2 | v3 |
| --- | --- | --- |
| Abstract | Opened with the cost framing, then disagreed with it | **Opens with the hypothesis** ("We hypothesize that documentation, not hardware, is the rate-limiting step…"), then the test, the result, the exceptions, the conclusion. 247 words; the journal limit is 250 |
| §1 | "We therefore advance five claims" | Hypothesis stated in bold as a three-step argument; each claim now says *how* it is tested; new paragraph on prior open-hardware work (Pearce 2016, Bonvoisin *et al.* 2017) |
| §3 project vignettes | Condensed v1 text | Each ends with an ***Evidence:*** sentence naming the claims it bears on. Before, the vignettes could be deleted without touching the argument; that was the editor's second objection |
| Table 2 | S/C/X marks, criteria implicit | Criteria stated in the caption; **P1, P3, P7 relabelled X → S⁻** (see §3 below); P2 and P4 on C2 → "—" pending replication counts |
| §5 | "Three projects contradict this claim" | "Three projects are negative cases", plus an explicit caveat that non-replication has other explanations (moved into §9 as a new limitation) |
| §6 Table 5 | Five capabilities, provisional scores | **Licence column added**; every cell re-verified against the live resource and tied to evidence in ESI Note S3 |
| §6 obligations | Generic "journals should…" | Built on this journal's own hardware guidelines (Hein & Schrier 2024) and its requirement of a BOM plus construction guide. Those cover 2 of the 5 capabilities; v3 argues for the other three. Commit articles are cited as an existing venue for documentation updates |
| §6 commitment | "every project will have an archival deposit at publication" | Split into what is true at submission (a public repository for every project) and what is promised by publication (an archival deposit). This matches the journal's code policy: GitHub is enough for review, a DOI is needed before publication |
| §9 Limitations | four paragraphs | plus one on what the negative cases cannot show |
| Authors | Pelkie corresponding (as in v1) | **Baird corresponding** (BYU ME; AC); **Leavitt added** (BYU ME); affiliations renumbered by first appearance, with city and country |
| Contributions | v1 statement + `[NEEDED]` | Per-author CRediT; RSC requires a per-author statement for papers with more than 10 authors |
| Back matter | Data availability first | RSC order: contributions → conflicts → **Data availability** → Acknowledgements |
| Generative-AI use | not disclosed | Disclosed in the Acknowledgements and the cover letter, in RSC's recommended wording |
| Figure 8 | Recovered slide with UBC/UofT/AC logos | On 2026-10-10 the logo strip was cropped and a spell-check squiggle removed with an AI tool. **Withdrawn on 2026-11-27**: RSC does not allow AI-assisted tools to alter submitted images, so Figure 8 is the unaltered original again, and the P7 team is asked for a clean export (P7-2) |
| References | 34 | 45 (renumbered in first-citation order by `tools/check_manuscript.py`): ref 6 corrected, ref 13 updated, 11 added (see §7) |

**Factual corrections to v2:**

- **"Three in under 10 hours"** (§5) was wrong. Only two projects (0.5 h, 3 h) are *under* 10 h; five are *at or under* 10 h. v3 says "five in 10 hours or less".
- **"Three orders of magnitude"** of bill of materials overstated it. Excluding software, the range is $100 to $35,000, which v3 now gives as "nearly three orders of magnitude".
- **"Eighteen months on"** was already inaccurate in August 2026: the workshop was on **6 August 2024**. v3 says "more than two years after the workshop".
- **"We organized the workshop"**: the official Accelerate 2024 programme also lists Milad Abolhasani and Curtis Berlinguette as organizers, and neither is an author. v3 says "several of us co-organized" and thanks them by name (SGB-14).
- The workshop's exhibition is called a "hardware exhibition" in the programme. v3 uses that term.

## 2. What happened to every v2 `[NEEDED]` marker

v2 had 18 `[NEEDED]` occurrences covering 12 distinct items, plus 4 author-list queries in an HTML comment. **None remain in v3.** Each was either resolved, or turned into a pre-drafted sentence with a named owner (`SIGN-OFF` ID), or, where the thing does not exist yet, into a `[TO SUPPLY]` placeholder with an owner.

| v2 marker | v3 status | Owner |
| --- | --- | --- |
| §2 selection criterion (10 of 14) | **Drafted**: "those whose developers contributed a written description, with reproduction cost and time estimates" | BP-1 confirms or corrects |
| §2 survey material for ESI | **Note S2 drafted** with what is known: administered *during* the workshop (from v1), n = 58, the two results. Instrument, distribution, response rate and ethics are still owed; a fallback sentence is ready if they were not archived | BP-2, BP-3, LDP-1 |
| Table 1 P1 repository | **Found**: public since 2025-01-27 but never linked; now cited | TV-1 confirms and fixes defects |
| Table 1 P2 Zenodo DOI | No longer needed at submission (journal policy: DOI by publication); covered by the §6 commitment | OM-5 |
| Table 1 P3 repository | `[TO SUPPLY]`, **the one remaining blocker** | TV-1 |
| Table 1 P4 Zenodo DOI | As for P2 | TV-6 |
| Table 1 P7 repository | **Found**: tool files and code public in two forks, never linked; now cited | P7-1 confirms, ideally consolidates |
| Table 1 P8 archival deposit | **Repository folder found and cited**; DOI by publication | SGB-7 |
| Figure 4 confirm | Kept; DTU approves the view | TV-2 |
| Figure 8 confirm | Unaltered original restored 2026-11-27 (the AI-assisted crop was withdrawn); the P7 team exports a clean, logo-free version and confirms the schematic | P7-2 |
| Table 5 verification and consent | **Verification done** 2026-10-10; 18 of the 48 scores changed from v2, every cell tied to evidence in Note S3 (§4 below); consent still per team | TV-4, OM-3, TB-3, BP-8, P7-4, SGB-10, JEH-2 |
| §6 commitment sentence | **Rewritten** to separate "at submission" from "by publication", in line with the journal's code policy; every team still has to agree | per team |
| §9 selection-criterion cross-reference | Resolved by the §2 sentence | BP-1 |
| Data availability: analysis DOI | **Resolved for submission**: the GitHub URL (the repository is public) is enough for review; `.zenodo.json` is ready for the DOI at acceptance | SGB-4 |
| Data availability: archival deposit for all ten | Moved to the §6 commitment (by publication) | per team |
| Data availability: survey | Points to Note S2 | BP-2 |
| Author contributions | **Resolved**: per-author CRediT, reflecting the ownership change | SGB-3, SL-1, ALL-3 |
| Author-list queries: Vasquez affiliation, Das, Yakavets | Carried as owned decisions; **not** resolved, because adding a person to an author list is not an edit an agent should make | NP-2, TB-2, P7-3 |

v2 notes §7 items that were not `[NEEDED]` markers:

| Item | v3 status |
| --- | --- |
| Licences missing on P2 and P4 | **Reported in Table 5's new licence column**, the honest default either way; teams asked to add one (OM-4, TV-5) |
| P9 repository renamed `ac-training-lab` → `ac-dev-lab` | SGB-8 |
| Brenden's manifesto | BP-5, LDP-2 |
| Is v1 what the editor read in Dec 2024? | BP-4 |

## 3. Why Table 2 changed

v2 marked P1, P3 and P7 as **X (contradicts)** on Claims 2 and 3. But v2's §5 then argued that these projects, with no design files and therefore no replication, are exactly what Claims 2 and 3 predict. A project cannot both contradict a claim and be its predicted outcome, and a referee looking for a soft spot in the one table that answers the editor's second objection would find this. v3:

- relabels them **S⁻**, "supports as a negative case", and says in §5 and §9 why negative cases are weaker evidence than positive ones;
- states decision criteria in the caption. C1 is mechanical: S if the break-even wage is below $50/h, C if it is $50–75/h. For C2 and C3, an S requires that replication beyond the developers has been reported;
- moves **P2 and P4 on C2 from S to "—"**, because nothing in the manuscript reports that either has been replicated. If OM-2 or TV-3 report replications, they go back to S, which is better evidence than v2 had.

This leaves Table 2 without a single *X*. That is the honest result: the strongest counter-evidence in the sample (P5 and P7 on cost, P5 on replication, P8 on documentation, P10 on skills) *complicates* rather than refutes, and every one of those is discussed by name.

## 4. Verification of the ten projects, 2026-10-10

Every repository, documentation site, licence and deposit was checked against the live resource. Full reports, with the exact searches behind every negative result, are in [`audit/`](audit/). The per-cell evidence for Table 5 is ESI Note S3. The most consequential findings were re-checked by hand.

**The blocking picture changed.**

| Project | v2 believed | Found |
| --- | --- | --- |
| P1 Powder dispensing | No repository | **Public since 2025-01-27**: `loppe35/PowderDispensing_and_Weighing_Module` (+3 submodules), release v1.0.0, Zenodo 10.5281/zenodo.14746532. It was never linked from the manuscript, even though it predates the preprint by 16 days. Defects, each re-verified: **11 firmware files contain unresolved merge-conflict markers**; **the Zenodo zip contains empty `BuildFiles/`, `FWSW/` and `Data/` folders** (git submodules are not captured); 16 of 22 file names in the build guide do not exist; licences are inconsistent |
| P3 Rolling ball viscometer | No repository | **Still nothing public**, anywhere. **The one remaining blocker** |
| P7 Electrochemical workflow | No repository | **Public but scattered.** RDE adapter STLs in `ethraj2001/jubilee@d5c5969` (2024-08-27), offered upstream as `machineagency/jubilee#204` and never merged. A positioning-only RDE tool class in `cyrilcaoyang/jubilee-sdl2@bc548db` (2025-02-13, archived). No electrochemistry code, no documentation, no deposit |
| P8 Digital pipette | Forum threads only | Firmware and STLs in `AccelerationConsortium/ac-dev-lab/src/ac_training_lab/picow/digital-pipette`; parts list in a Google Doc; no attribution to the CC BY 4.0 original; no release, so no DOI |

**Links that moved:** P2 `owen-melville/photo-reactor` → `AC-SDL4/photo-reactor`; P6 `science_jubilee` → `science-jubilee`; P9 `ac-training-lab` → `ac-dev-lab` (the docs stay at `ac-training-lab.readthedocs.io`, because `ac-dev-lab.readthedocs.io` is 404). All old URLs still redirect.

**Table 5 changes from v2, with the evidence:**

| Project | v2 | v3 | Why |
| --- | --- | --- | --- |
| P1 | ○○○○○ | ◐◐◐●● | The public release found above |
| P2 | ●●◐◐○ | ●●◐◐◐ | Scattered troubleshooting notes plus an issue tracker with a maintainer reply = ◐ under the rubric |
| P4 | ◐◐◐●○ | ○○◐●◐ | No BOM, no CAD and no assembly instructions in any branch or mirror; scattered tips = ◐ |
| P5 | ○○◐●○ | ◐◐◐◐○ | Scored for the platform from module-level material; Run drops because there is no Archerfish operating procedure and no orchestration code; `PV-Lab/DiSCO` is an empty placeholder |
| P6 | ●●●●● | ●●●●● | Unchanged, but Troubleshoot now rests on the written "first-line troubleshooting" section, not on Discord |
| P7 | ○○○○○ | ◐◐○○○ | The print files found above |
| P8 | ◐◐◐◐○ | ◐◐◐◐◐ | Forum thread with maintainer replies = ◐, the same basis as P9 |
| P9 | ◐◐●●◐ | ◐◐◐◐◐ | The microscope-side code is missing (issue #37) and the public Spaces were down |
| P10 | n/a n/a ●●◐ | n/a n/a ●●● | Written "Workflow step warnings" and "Human intervention and errors" pages |

**A claim that did not survive.** v2 said troubleshooting was "the weakest column by a wide margin". With every cell tied to evidence it is not: Troubleshoot has three ●, four ◐ and three ○, about the same as the other columns. v3 drops the claim from the abstract and §6 and reports what the audit does show:

1. Only one of nine hardware projects is completely documented.
2. Half of the applicable cells (24 of 48) are partial.
3. Projects document *operating* better than *obtaining and building*: Run is ● for four projects, while Procure and Build are ● for two of nine.
4. Existing documentation often fails on contact with a stranger: merge-conflict markers, wrong file names, an empty deposit, function names that don't match the code, a down interface, an empty placeholder repository.
5. Licensing and archiving are unattended. Two projects have no licence file, two declare different licences in different places, and none of the three deposits archives the complete, current design.

This is a stronger result for the paper, and it came from checking rather than assuming.

**Archival deposits:** P1 (empty), P5 (SDCNN module only, via a fork), P10 (one 2025-04-24 snapshot; declares CC BY 4.0 against the repository's MIT). None for P2, P3, P4, P6, P7, P8, P9.

**Publications since 2024** describing any of the ten projects: none, beyond those already cited for P5 and P10.

## 5. P3, and the text for each outcome

v3's text already reflects the verified state: P1 and P7 have public files that were not linked, and P3 has none. Three outcomes remain.

**(a) P3's team publishes a work-in-progress repository (the expected path).**

- Put the URL in Table 1 and in the response letter.
- Re-score the P3 row of Table 5 from the repository's contents. A pre-release repository with CAD and a BOM typically scores Procure ◐, Build ◐ and ○ for the rest.
- In §5, change "P3 has released no files at all." to "P3's developers released a work-in-progress repository only during this revision, more than two years after the workshop."
- The abstract's "the third has released none" becomes "the third released files only during this revision".
- Also change, so that nothing still says P3 has no files (list from the 2026-11-27 pre-submission read):
  - §3, P3's *Evidence:* sentence ("with no public design files at all");
  - §6, "one is still an empty row";
  - Table 5's caption date and the P3 row, and ESI Note S3's P3 section;
  - the response letter's P3 sentence (a `[TO SUPPLY]` holds both versions) and its Point 3 table;
  - the cover letter's point 3 (its SIGN-OFF note has the wording);
  - Table 2 stays S⁻ for P3, because its legend now says "not linked … before this revision".

**(b) P3's team cannot publish a repository.**

- Remove P3 from Tables 1, 2, 3 and 5 and from Figure 1.
- Delete the P3 row from `PROJECTS` in `analysis/labor_cost_analysis.py` and re-run it.
- Update every number in the abstract and §§1, 4 and 5 from the output. Computed on 2026-11-27 for nine projects:
  - unchanged: median break-even wage $30/h, maximum $73/h (DiSCO), the two projects above $50/h (P5, P7), the bill-of-materials range $100–35,000;
  - **median rebuild time 17 h → 24 h** (abstract, §1, §5);
  - "eight of the ten in 100 hours or less" → **seven of the nine**; "five in 10 hours or less" → **four**;
  - Table 4: labour exceeds parts for 4/9 at $25/h (median share 45%), 7/9 at $50/h (62%) and 9/9 at $75/h (71%);
  - "ten projects" → "nine projects" throughout, including the title of Table 1 and the TOC text.
- Add to §2: "An eleventh project was presented but is not included because its design files could not be released."
- Change "Three projects…" in the abstract and §5 to "Two projects…".
- Do **not** keep P3 while weakening the §6 commitment.

**(c) A team declines to have its Table 5 row published.** Remove the row and add to the caption: "One team declined to have its row published."

**If the P1 or P7 teams fix the defects listed in §4 before submission**, which is the better outcome, keep §6's "we found…" sentences in the past tense and record the fixes in Note S3. A co-author audit catching defects that the authors then fix is itself evidence for the paper's prescription that someone other than the author should check documentation.

## 6. Journal requirements checked on 2026-10-10

Sources, all accessed 2026-10-10: the *Digital Discovery* author guidelines (https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/digital-discovery) and RSC author responsibilities (https://www.rsc.org/publishing/journals/processes-and-policies/author-responsibilities). Quotations are verbatim.

| Requirement | Where v3 meets it |
| --- | --- |
| Perspective: "a personal account of research or a critical analysis of a topic of current interest… some new unpublished research may be included" | The §4 analysis and §6 audit are the "new unpublished research"; the position is the critical analysis |
| Abstract "around 50 to 250 words" | 247 words |
| Data availability statement mandatory; "at the end of the article… after the conflicts of interest statement and before any acknowledgements"; full URLs, never "available on request" | Done, in that order |
| Code: GitHub access for referees during review; "Authors must also obtain a DOIs for the code and/or data and submit it before publication" | GitHub URL now, Zenodo at acceptance (SGB-4); the §6 commitment is phrased to match |
| A data reviewer "verifies that the code is functional and reproduces the reported findings" | `analysis/README.md`, pinned `requirements.txt`, one-command reproduction; re-verified byte for byte |
| GenAI: "must be declared at submission within the cover letter"; tool and model in Acknowledgements; if there is no Methods section, all details go in the Acknowledgements; AI cannot be an author | Cover letter paragraph; Acknowledgements paragraph in RSC's recommended wording; prompts are the public issue and PR threads; Claude is in neither the author list nor CRediT |
| ">10 co-authors: the corresponding author must provide… the contribution of each co-author" | Per-author CRediT |
| "the corresponding author attests… that those named as co-authors have agreed to its submission" | ALL-1 for all 28 authors |
| Submitting author ORCID required "when submitting a revised manuscript" (re-checked 2026-11-27); link it at submission anyway | ALL-7, SGB-12 |
| Human subjects: name the ethics committee and approval number, and give a consent statement | Owed (BP-3/LDP-1); RSC gives no anonymous-survey exemption |
| TOC: required at the revision stage; graphic 8 × 4 cm, ≥ 600 dpi TIFF, original, no logos; text 1–2 sentences, ≤ 250 characters, not paraphrasing the title or abstract | Text drafted (212 characters). Graphic due at revision, as original artwork by a co-author that preferably does not reuse a figure (SGB-15); `figures/source/toc-layout-sketch.png` is a layout sketch only |
| Cover letter "will be sent to reviewers" | Written accordingly |
| Resubmission | No RSC rule found that requires citing the previous ID, but the cover letter and response do so throughout. "If you submit a revised version of a previously considered manuscript this will be treated as a resubmission and not an appeal." |

**Themed collections.** The Accelerate 2023–2024 collection is published and closed. The **AI4X – Accelerate 2026** collection closed on **31 October 2026**; on 2026-11-27 there was no extension and no other *Digital Discovery* call was open. The paper therefore goes in as a regular Perspective, which needs no proposal or invitation (SGB-13).

**The editor's own guidelines.** Hein and Schrier, "Guidelines for hardware-focused articles", *Digit. Discov.* 2024, 3, 447–448. Together with the journal's requirement of "a comprehensive bill of materials and a construction guide" for hardware papers, this is cited in §6. It is the natural anchor for the paper's recommendation: the journal already demands procure and build, and v3 argues for configure, run and troubleshoot.

## 7. References

All 34 v2 references were re-checked against Crossref on 2026-10-10.

- **Ref 6 (A-Lab).** The title was changed by an Author Correction, *Nature* 2026, 650, E1 (10.1038/s41586-025-09992-y): "…Synthesis of **Inorganic** Materials" (was "Novel"). v3 cites the corrected title and the correction notice. The paper is cited only as an example of commercial automation infrastructure, so nothing else changes.
- **Ref 13 (ASTM D1200).** The 2018 reapproval is marked "Standard Historical", superseded by **D1200-23**, which v3 now cites.
- **Ref 9 (OSHWA).** The canonical URL has dropped `www.`.
- **Ref 21 and ref 23.** "Vasquez, S." is cited deliberately and matches the author list. Leave it.
- **Ref 27 (µManager).** Crossref and PubMed give only "Unit 14.20"; the 14.20.1–14.20.17 page range could not be independently confirmed (Wiley blocks automated access).
- **No retractions or expressions of concern** in any reference.

**Eleven added, all verified in Crossref:**

| Ref | Where | Why |
| --- | --- | --- |
| Pearce 2016, *Sci. Public Policy* | §1, §5 | ROI of open hardware comes from replication by others: Claim 2's antecedent |
| Bonvoisin *et al.* 2017, *J. Open Hardw.* | §1, §6 | The "source" of OSH is its documentation, and projects share it unevenly: Claim 3's antecedent |
| Yoshikawa *et al.* 2026, *Digit. Discov.* (Commit) | §6 | A Commit article used for a hardware update (disposable tips for the Digital Pipette); also P8's base device |
| DIN SPEC 3105-1:2020-07 | §6 | Existing documentation standard on which shared templates can build |
| Maia Chagas 2018, *PLoS Biol.* | §1 | The access-and-cost case for open scientific hardware |
| Pearce 2020, *HardwareX* | §1 | The canonical "open hardware saves 87%" result: the cost framing, quantified |
| Antoniou *et al.* 2021, *Proc. Des. Soc.* | §6 | BOM plus assembly instructions are not enough for replicability |
| Saubke *et al.* 2025, *Procedia CIRP* | §6 | Documentation deficits against DIN SPEC 3105 block reproduction: the closest analogue to Table 5 |
| Hein & Schrier 2024, *Digit. Discov.* | §6 | The journal's hardware guidelines |
| *Digital Discovery* author guidelines (web) | §6 | Source for the BOM + construction-guide requirement |
| Aspuru-Guzik, Hein & Schrier 2025, *Digit. Discov.* | §6 | Defines the Commit format |

## 8. What v3 deliberately does not do

- **Does not create repositories or deposits for anyone's project.** The designs belong to their teams, and a stub made by someone else would be exactly the kind of documentation the paper argues against.
- **Does not mint the Zenodo DOI for the analysis.** Publishing a DOI is irreversible and public. Everything is staged (`analysis/.zenodo.json`), and it can be done on request.
- **Does not add Basita Das or Ilya Yakavets** to the author list, or move anyone in it beyond inserting Seth alphabetically.
- **Does not soften Table 5.** Where the evidence changed a score, it changed in whichever direction the evidence pointed, and each change is listed in §4.
- **Does not choose the title for the group.** v2's first choice is kept; the alternatives are in `revision-notes-v2.md` §2.

## 9. Re-check and changes of 2026-11-27

Sterling asked for every blocker to be re-checked against the live repositories and this thread, for the manuscript and response letter to be brought up to date, and for a sign-off package. Reports: [`audit/2026-11-27-projects-p1-p5.md`](audit/2026-11-27-projects-p1-p5.md), [`audit/2026-11-27-projects-p6-p10.md`](audit/2026-11-27-projects-p6-p10.md), [`audit/2026-11-27-references.md`](audit/2026-11-27-references.md), [`audit/2026-11-27-journal-policy.md`](audit/2026-11-27-journal-policy.md) and [`audit/llm-provenance.md`](audit/llm-provenance.md).

**The thread.** No co-author has commented on PR #193, #190 or #188 since 2026-10-10. No confirmation of any sign-off ID is on record.

### 9.1 What the journal-policy re-check changed

| Finding | Change |
| --- | --- |
| RSC: "GenAI or AI-assisted tools must not be used to alter images in submitted manuscripts. This includes adding, removing, moving, or obscuring features." In force before 2026-10-10 but missed then | **Figure 8 restored to the unaltered original**; the AI-assisted crop is withdrawn. P7-2 now asks the team for a clean export, which is needed before submission. The AI disclosure in the Acknowledgements and cover letter no longer mentions image editing and states that no figure was edited with an AI tool |
| AI4X – Accelerate 2026 closed on 31 October with no extension; no other DD call open | Submit as a regular Perspective (SGB-13) |
| Lilo D. Pozzo is on the DD Editorial Board; Milad Abolhasani, thanked as a workshop co-organizer, is an Associate Editor | Cover letter says so, for routing under RSC's editor-as-author rule. Abolhasani is not to be proposed as a reviewer (SGB-12) |
| "Adding authors from new institutions … will not be considered unless fully justified to the editor" | Cover letter now explains why BYU is new |
| TOC graphic: "original, unpublished artwork created by one of the co-authors", preferably not reused from the article; due at revision | The draft made on the same day was demoted to a layout sketch (`figures/source/toc-layout-sketch.png`); SGB-15 moved to the revision stage |
| DD's code template: "The version of the code employed for this study is …"; DOIs for "both the most recent and archived versions" at acceptance | Data availability gains the version sentence (a tag to fill at submission) and promises both DOIs |
| Human-subjects ethics statement belongs "in the 'methods/experimental' section" | §2 gains a `[TO SUPPLY]` for it (BP-3, LDP-1) |
| LLM results: "Specify the model identifier and generation date" | ESI Note S3 names the models and dates behind the Table 5 scores; `audit/llm-provenance.md` lists every session |
| Affiliation is where the work was done; a later address is a footnote | ALL-2 says so; flagged for Maria Politi (v3 lists UBC for P6 work) |
| Reference style: RSC reformats; "Vancouver style (not Harvard style)" | No change needed (the October note overstated this) |
| Figures at revision: separate TIFFs at 600 dpi or more | Figure 4 (1532 px) and Figure 8 (1842 px) are below 600 dpi even at single-column width; TV-2 and P7-2 ask for originals |

### 9.2 Other corrections made today

- **ESI Note S4 rounding.** Note S4 gave 46% for P1, P3 and P4 at $25/h and for the $25/h median. The exact value is 45.45%, as Table 4 already says; the ESI had rounded the three-decimal CSV a second time. Note S4 now states the rounding rule (half to even, so the 62.5% at $50/h is reported as 62%).
- **"Ten teams" → eight.** §10 and the TOC text said ten teams built the ten projects; the DTU team built three. The Outlook's "eleventh team … twelfth copy" sentence relied on the wrong count and was rewritten.
- **AI disclosure, model list.** The Actions logs' `modelUsage` records show that Claude Code also used Claude Haiku 4.5 (September) and Haiku 5.5 (October) for auxiliary steps. The Acknowledgements and cover letter now name them, and the period runs to November 2026.
- **Timing of the P1 and P7 files** (response letter, Point 3). P7's files were public before the original submission; P1's release came after it, before the preprint. "Had in fact put files in public" did not say when.
- **P3 in the response letter.** "Its developers are creating a work-in-progress repository" asserted something nobody has confirmed. It is now a placeholder with the two sentences to choose from at submission.
- **No-P3 fallback numbers** computed and written into §5(b) above: the median rebuild time would move from 17 h to 24 h; the break-even median and maximum would not change.
- **Pronouns.** Several notes and one sentence of §6 used pronouns inferred from names. They now use names or neutral wording.
- **Review copies.** Table column widths are set in the markdown separators so that the Word and PDF copies are readable; GitHub ignores them.

### 9.3 The projects and references, re-checked

**The three blockers of 10 October are unchanged.**

| Blocker | 2026-10-10 | 2026-11-27 |
| --- | --- | --- |
| P3 repository | Nothing public anywhere | **Still nothing public**, on GitHub, GitLab, Zenodo, Figshare/DTU Data, DataCite, OSF, arXiv, Crossref or OpenAlex. Two leads to ask DTU about, neither linked to P3 by evidence: the GitHub organisation `DTU-Energy-Instruments` (created 2026-10-14, no public repositories), and `auto_lab/sdl-next-generation-batteries`, which stopped being public |
| P1 files confirmed by the team | Found, not confirmed | **Unchanged.** Same heads, the same single release, all 11 conflict-marker files and the empty Zenodo folders still there; no confirmation on record |
| P7 files confirmed by the team | Found, not confirmed | **Unchanged.** The STL blobs are byte-identical; machineagency/jubilee#204 has had no activity since it was opened; nothing consolidates the work; no confirmation on record |
| Approval by all 28 authors | Not started | **None received** |

**No Table 5 score changes.** Every resource behind a score is live and unchanged. Small facts updated:
- IvoryOS has shipped six releases since October (latest v1.8.3, 2026-11-24), none of them archived on Zenodo;
- P9's two Hugging Face Spaces are still down;
- a fork of P2 (`kelvinchow23/photo-reactor`, November 2026) holds a "Rev B" redesign by an AC engineer, added to OM-2 as a possible replication for the team to judge;
- Ethan Rajkumar's GitHub profile now gives McMaster University, so ALL-2 asks about a present-address footnote.

**References.** All 45 re-checked against Crossref: no factual errors, retractions or expressions of concern, and both standards are still current. Ref 31's page range, unconfirmed in October, is now confirmed. Optional edits applied: ref 14 names OpenTrickler v1.4, ref 26 reads "PLoS One", and the web references carry the 2026-11-27 access date. The preprint has ten verified citations, not the six the cover letter claimed, and six of them share no author with the paper; the cover letter now says so.

**URLs.** Every link in Table 1 and every web reference returned HTTP 200 on 2026-11-27. The exception was the P4 GitLab page, which rate-limited the runner (HTTP 429) after its API had confirmed the project public.

### 9.4 Changes after an independent pre-submission read

A separate session read the package as a referee and handling editor would and raised 25 items; [`audit/2026-11-27-presubmission-review.md`](audit/2026-11-27-presubmission-review.md) lists each one and what was done. It confirmed every number in Tables 3–5, Note S4 and Figure 1. The changes that touch the argument, all flagged for approval (SGB-9, SGB-16):

- **Claim 1** no longer says "at any realistic loaded rate". At $25/h, the bottom of the paper's own band, labour exceeds parts for only four of the ten, so it now says "at the loaded rates of most people who build these systems".
- **Table 2 follows its own caption.** An S on C2 or C3 needs reported replication, so:
  - P2 C3 S → — (documented, no reported build);
  - P4 C2 — → S⁻ and C3 S → S⁻ (no bill of materials or build files, no reported build);
  - P9 C2 and C3 S → — (the replication was the microscope's, not the control layer's).

  After this, C2 is S for P6, P8 and P10 (three of ten, the "minority" Claim 2 predicts) and C3 is S for P6 and P10.
- **§6's pattern** is restated from the counts. Among the nine hardware projects, Run is complete for three and Procure and Build for two each, and Configure, complete only for science-jubilee, is the weakest. "Document how to operate better than how to build" overstated a one-project difference.
- **§1, step three:** "its documentation, and the support behind it". The positive cases (P6, P8) replicated with support around the documentation.
- **New text:** a §6 paragraph on the two C3 complications the caption promised (P5, P8); a §5 sentence on P4; four Limitations sentences (the identical DTU figures, the cash constraint, self-reported replication, no second rater); and the disclosure that two of us co-wrote Lo *et al.*

Precision and consistency fixes, applied without changing the argument:
- the impossible "labour share … higher by an order of magnitude";
- the Outlook's "cheaper than the hardware";
- "nearly three" → "more than two" orders of magnitude;
- P5's modules "most", not all, open source;
- P8's licence footnote;
- the letters' four statements the manuscript did not support;
- typos in Note S1 and the abstract.

Left open for Sterling (SGB-16): criteria for X in Table 2, the hardware-only median rebuild time (24 h), DOIs in Table 1, and the script's file name. New team item ALL-8 asks each team for the records that would turn three assertions into evidence: its reported difficulties (§7), a rough estimate of its development hours (§5), and any builds by outsiders (Table 2, C2).
