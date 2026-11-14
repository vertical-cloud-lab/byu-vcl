# Revision notes for v3

**What this file is:** the changelog from [`manuscript-v2.md`](manuscript-v2.md) to [`manuscript-v3.md`](manuscript-v3.md); what happened to every `[NEEDED]` marker in v2; the evidence gathered on 2026-10-10; and the text to use if the three missing repositories do or do not appear. The per-person asks are in [`sign-off-checklist.md`](sign-off-checklist.md).

**Ownership.** Sterling G. Baird owns the revision and is corresponding author. Seth Leavitt, who directed v2, has left the group and stays an author for that work, subject to his consent (SL-1).

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
| Figure 8 | Recovered slide with UBC/UofT/AC logos | Logo strip cropped, PowerPoint spell-check squiggle under "Opentrons" removed (the "p" descender it overlapped was restored); original kept in `figures/source/` |
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
| Figure 8 confirm | **Logos removed** (the journal would strip them); P7 team confirms the schematic is current | P7-2 |
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

**(b) P3's team cannot publish a repository.**

- Remove P3 from Tables 1, 2, 3 and 5 and from Figure 1.
- Delete the P3 row from `PROJECTS` in `analysis/labor_cost_analysis.py` and re-run it.
- Update every number in the abstract and §§1, 4 and 5 from the output. P3 sits at the median break-even wage, so the median is almost unchanged; recheck the median rebuild time and the counts.
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
| Submitting author ORCID required | ALL-7, SGB |
| Human subjects: name the ethics committee and approval number, and give a consent statement | Owed (BP-3/LDP-1); RSC gives no anonymous-survey exemption |
| TOC: required at the revision stage; graphic 8 × 4 cm, ≥ 600 dpi TIFF, original, no logos; text 1–2 sentences, ≤ 250 characters, not paraphrasing the title or abstract | Text drafted (204 characters); graphic is SGB-15 |
| Cover letter "will be sent to reviewers" | Written accordingly |
| Resubmission | No RSC rule found that requires citing the previous ID, but the cover letter and response do so throughout. "If you submit a revised version of a previously considered manuscript this will be treated as a resubmission and not an appeal." |

**Themed collections.** The Accelerate 2023–2024 collection is published and closed. The **AI4X – Accelerate 2026** collection is open until **31 October 2026**. It takes work "whether specifically presented at the conference or not", but a Perspective needs a proposal to the Editorial Office first (SGB-13).

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
