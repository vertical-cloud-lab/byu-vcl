# Co-author sign-off checklist: v3 resubmission to *Digital Discovery*

**Manuscript:** [`manuscript-v3.md`](manuscript-v3.md), "Replication, not fabrication: documentation is the rate-limiting step for democratized self-driving labs"
**Owner of the revision and corresponding author:** Sterling G. Baird (SGB)
**Previous submission:** DD-PER-12-2024-000410 (rejected at editorial assessment 2025-01-09, with an invitation to resubmit)

Each item has an ID such as `TV-1`. The same ID appears in the manuscript source as an HTML comment (`<!-- SIGN-OFF: TV-1 -->`) right next to the sentence it governs. Run `grep -n "TV-1" manuscript-v3.md` to see exactly what you are confirming. `python tools/check_manuscript.py manuscript-v3.md` lists every open ID and every `[TO SUPPLY]` placeholder.

**How to sign off:** reply on the thread, or tick your boxes here in a PR, with "confirmed" or a correction for each of your IDs. Corrections to the text are welcome. Please do not soften Table 5, the documentation self-audit. If your team cannot accept its row, ask for the row to be removed, and the caption will say so.

---

## 0. What blocks submission

The paper cannot be submitted until these are done. Everything else is a confirmation.

| # | Item | Owner | IDs |
| --- | --- | --- | --- |
| 1 | Work-in-progress repositories for **P1 Powder dispensing module** and **P3 Rolling ball viscometer** | DTU team (Chang, Gambhir, Ziskason, Nyeland); escalation: Tejs Vegge | TV-1 |
| 2 | Work-in-progress repository for **P7 Electrochemical workflow** | Yang Cao, Ethan Rajkumar, Ilya Yakavets; escalation: SGB / Jason Hein | P7-1 |
| 3 | Agreement to the archival-deposit commitment in §6, from every team | all project teams | TV-6, OM-5, TB-4, BP-9, P7-5, SGB-11, JEH-3 |
| 4 | Consent to publish each team's Table 5 row | all project teams | TV-4, OM-3, TB-3, BP-8, P7-4, SGB-10, JEH-2 |
| 5 | Every author approves the final text and agrees to submission (RSC requires this) | all 28 authors | ALL-1 |

**The bar for items 1–2 is low.** The editor wrote that he would accept "at least the current 'work in progress' repositories". A public repository with the CAD files, a bill of materials, the control code as it stands, a licence, and a README that says "pre-release; documentation incomplete" is enough. It takes an afternoon. If a team cannot do it, that project comes out of Table 1. See [`revision-notes-v3.md`](revision-notes-v3.md) §5 for exactly what changes in that case.

---

## 1. Everyone (all 28 authors)

| ID | Confirm |
| --- | --- |
| ALL-1 | You have read v3, approve it, and agree to its submission to *Digital Discovery* with you as an author. |
| ALL-2 | Your affiliation(s), written out in full: department, institution, city, postcode, country. v3 gives institution, city and country only. |
| ALL-3 | Your CRediT role(s) in the Author contributions statement. If you are under "All other authors", your role is *investigation* (you contributed a project description and cost/time estimates) plus *writing – review and editing*. |
| ALL-4 | You have no conflict of interest to declare, or you send one. Include anything new since 2024, e.g. a company selling kits or instruments described here. |
| ALL-5 | Your funding acknowledgement. The list is v1's and is known to be incomplete (see SGB-6, TB-5, BP-10, NP-3). |
| ALL-6 | The title. v3 uses *"Replication, not fabrication: documentation is the rate-limiting step for democratized self-driving labs"*. Alternatives are ranked in `revision-notes-v2.md` §2. The old title cannot be reused, because Doloi *et al.* (2025) holds it in this journal. |
| ALL-7 | Your ORCID iD. Required for the submitting author; strongly encouraged for everyone. |

### Roster

Tick ALL-1 to ALL-7 per person. Team-specific items are listed in the sections below.

| Author | Affiliation in v3 | Team / role | ALL-1 approve | ALL-2 affil. | ALL-3 CRediT | ALL-4 COI | ALL-5 funding | ALL-6 title | ALL-7 ORCID |
| --- | --- | --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Brenden Pelkie | UW | first author; P6 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Sterling G. Baird | BYU; AC | corresponding; P8, P9 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Eunice Aissi | MIT | P5 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Kenzo Aspuru-Takata | AC | P9 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Yang Cao | AC | P7 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Jin Hyun Chang | DTU | P1, P3, P4 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Kshitij Gambhir | DTU | P1, P3, P4 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Wm Salt Hale | UW | P6 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Lucy Hao | UBC | P10 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Chance Hattrick | AC | P8 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Jason E. Hein | AC; UBC; Bergen | P10 PI | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Seth Leavitt | BYU | revision coordination | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Danli Luo | UW | P6 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Owen A. Melville | AC | P2 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Monique Ngan | AC | P2 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Louie Lucas Bisgaard Nyeland | DTU | P1, P3, P4 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Nadya Peek | UW | P6; keynote | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Maria Politi | UBC | P6 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Ethan Rajkumar | AC; UBC | P7 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Alexander E. Siemenn | MIT | P5 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Blair Subbaraman | UW | P6 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Sonya Vasquez | UW (provisional) | P6 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Jeffrey Watchorn | AC | P2 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Wenyu Zhang | UBC | P10 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Rógvi Ziskason | DTU | P1, P3, P4 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Lilo D. Pozzo | UW | senior author | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Tonio Buonassisi | MIT | senior author; P5 PI | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Tejs Vegge | DTU | senior author; DTU PI | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

Two people are named as project developers in Table 1 but are **not** in the author list: Basita Das (P5) and Ilya Yakavets (P7). See TB-2 and P7-3. Neither has been added; only they and their teams can settle it.

---

## 2. Sterling G. Baird (SGB): corresponding author, owner of the revision; P8 and P9 developer

- [ ] **SGB-1.** Corresponding-author line: "Sterling G. Baird, sterling.baird@byu.edu" (the address on your commits to this repository). Also the affiliation order, BYU Mechanical Engineering then Acceleration Consortium, which follows your TMS 2027 abstract.
- [ ] **SGB-2.** Author order. Brenden stays first. Seth is placed alphabetically in the contributor block (between Hein and Luo), the least presumptuous position. Move him if you and Brenden prefer otherwise.
- [ ] **SGB-3.** You accept responsibility for the formal analysis (§4 labour-cost analysis, §6 documentation audit) credited to you in CRediT, and for the **Use of generative AI** statement. That statement discloses that Claude drafted the revision under your and Seth's direction. Check the wording against RSC policy (`revision-notes-v3.md` §6).
- [ ] **SGB-4.** Mint the Zenodo DOI for `analysis/` from the final commit, then paste it into the Data availability statement and Table 1 of the response letter. Metadata is ready in `analysis/.zenodo.json`. I did not create the deposit, because publishing a DOI is irreversible and publicly visible; I can do it on request.
- [ ] **SGB-5.** Authorship of Basita Das and Ilya Yakavets, decided with TB-2 and P7-3. If either is added, the response letter (Other changes, item 5) must say so and why.
- [ ] **SGB-6.** Funding. v1 has no acknowledgement for you, Chance Hattrick, Kenzo Aspuru-Takata or Ethan Rajkumar, although all were at the Acceleration Consortium (plausibly CFREF-2022-00042, as listed for the other AC authors). There is also no line for BYU support of the revision.
- [ ] **SGB-7.** **P8 archival deposit** (with Chance Hattrick). P8 is documented only by two Discourse threads, which the paper itself says do not count. Deposit the CAD, firmware and integration code on Zenodo, or point to an existing repository and mint a DOI from it. Then confirm the P8 row: $100, 3 h, "reproduced by several groups". Who are they? Naming one or two would strengthen §5.
- [ ] **SGB-8.** **P9 link** (with Kenzo Aspuru-Takata). The repository was renamed `ac-training-lab` → `ac-dev-lab`. Confirm which URL is permanent and whether to cite the docs, the repository, or a Zenodo DOI. Then confirm the P9 row: $300, 30 h including the microscope build.
- [ ] **SGB-9.** **Table 2 relabelling.** v2 marked P1, P3 and P7 as *contradicting* Claims 2 and 3. But v2's own §5 argued that they behave exactly as those claims predict, which a referee would spot. v3 marks them *S⁻* (supports, as a negative case), states the criteria in the caption, and moves P2 and P4 on Claim 2 from S to "—" until their teams report replications (OM-2, TV-3). See `revision-notes-v3.md` §3.
- [ ] **SGB-10.** Consent to the P8 and P9 rows of Table 5.
- [ ] **SGB-11.** Agreement to the §6 commitment for P8 and P9.
- [ ] **SGB-12.** At submission: enter the previous manuscript ID (DD-PER-12-2024-000410) and upload the cover letter with the point-by-point response (`cover-letter.md`, `response-to-decision-letter.md`), the ESI (`esi/`), and the TOC graphic and sentence (end of the manuscript).
- [ ] **SGB-13.** Choose the venue route. The Accelerate 2023–2024 themed collection has closed. The **AI4X – Accelerate 2026** collection is open until **31 October 2026** and accepts work "whether specifically presented at the conference or not". For a Perspective or Review it needs a proposal e-mailed to the Editorial Office first, and the collection is selected in the submission system, not mentioned in the cover letter. Otherwise, submit as a regular Perspective (`revision-notes-v3.md` §6).
- [ ] **SGB-14.** The Acknowledgements thank the workshop's other two official co-organizers, Milad Abolhasani and Curtis Berlinguette, who are not authors. §2 now says "several of us co-organized" because the official programme lists them as organizers. Check that they are content to be named.
- [ ] **SGB-15.** At the revision stage, supply the TOC graphic: 8 × 4 cm, ≥ 600 dpi TIFF, original, no logos; a simplified Figure 1(b) is the obvious candidate. The 204-character TOC sentence is at the end of the manuscript.

## 3. Seth Leavitt (SL): revision coordination

Seth has left the group. Authorship still requires his consent: RSC requires every author to approve the submission.

- [ ] **SL-1.** Consent to being listed as an author. Affiliation at the time of the work: "Department of Mechanical Engineering, Brigham Young University", as in the TMS 2027 abstract. Your contribution as worded: "conceptualization (revised argument), project administration (coordination of the revision, August–September 2026), writing – review and editing". Also a current e-mail address for the submission system.
- [ ] **ALL-1 to ALL-7** as for everyone.

## 4. Brenden Pelkie (BP): first author, original corresponding author; P6 developer

- [ ] **BP-1.** The **10-of-14 selection criterion** (§2). v3 says the ten are "those whose developers contributed a written description, with reproduction cost and time estimates". Confirm this, or give the real criterion. A referee will ask.
- [ ] **BP-2.** **Survey material for Supplementary Note S2:** the instrument verbatim, the full response distribution, the response rate (58 of how many attendees?), and whether responses were collected before or after the showcase. *Fallback, only if true:* "The survey instrument and per-item response distributions were not archived; we report the two aggregate results recorded at the time." In that case Note S2 becomes that sentence, and §9 already treats the survey as a convenience sample.
- [ ] **BP-3.** Ethics and consent for publishing aggregate survey results (with LDP-1). RSC policy: for studies involving human subjects, the paper must "name the institutional/local ethics committee that has approved the study, and where possible the approval or case number", and "a statement regarding informed consent is required". RSC gives no exemption for anonymous surveys. Best: an IRB exemption or approval number plus a one-line consent and anonymity statement in Note S2. If there was no ethics review, either obtain an exemption determination now, or describe the survey plainly as anonymous workshop feedback, publish aggregates only, and let the editor decide.
- [ ] **BP-4.** Confirm that the ChemRxiv/arXiv text (`submitted/democratizing-sdl-arxiv-submission.docx`, created 2025-02-04) is the text the editor assessed in December 2024. The response letter quotes its abstract.
- [ ] **BP-5.** The "manifesto" you and Lilo mentioned. Send it, or confirm that the v3 thesis and the §6 obligations cover it.
- [ ] **BP-6.** Handover of corresponding authorship to SGB, and the author order (you remain first).
- [ ] **BP-7.** P6 science-jubilee row of Table 1: $2,000, 100 h, docs link.
- [ ] **BP-8.** Consent to the P6 row of Table 5. Under the stated rubric, Troubleshoot is ◐ unless written troubleshooting/FAQ pages exist; if they do, send the URL and it becomes ●.
- [ ] **BP-9.** §6 commitment: a Zenodo DOI for science-jubilee (if none exists, mint one from a GitHub release).
- [ ] **BP-10.** UW funding lines for the P6 authors.

## 5. Lilo D. Pozzo (LDP): senior author

- [ ] **LDP-1.** Survey ethics/consent and the instrument (with BP-2 and BP-3).
- [ ] **LDP-2.** The manifesto (with BP-5).
- [ ] **LDP-3.** Your funding line (unchanged from v1: NSF POSE TIP-2229018, NSF PREM DMR-2424949).

## 6. Tejs Vegge (TV) and the DTU team: P1, P3, P4

Jin Hyun Chang, Kshitij Gambhir, Rógvi Ziskason, Louie Lucas Bisgaard Nyeland; Tejs Vegge as PI.

- [ ] **TV-1. BLOCKING.** Public work-in-progress repositories for **P1 Powder dispensing module** and **P3 Rolling ball viscometer**, with URLs for Table 1. Also confirm the P1, P3 and P4 rows ($300, 10 h each) and the developer lists.
- [ ] **TV-2.** **Figure 4** (viscometer) was recovered from slide 4 of your showcase deck and has never been approved for publication. Approve it, or send a better view; CAD renders are in `figures/source/`. Figures 2 and 5 are unchanged from v1.
- [ ] **TV-3.** Has the color mixing bot (P4) been built by anyone outside the four developers, e.g. multiple units for course 47332? If yes, Table 2 C2 becomes S. The same question applies to P1 and P3.
- [ ] **TV-4.** Consent to the P1, P3 and P4 rows of Table 5. P1 and P3 are currently empty rows; once the repositories exist they will be re-scored from what is in them.
- [ ] **TV-5.** Add a licence to `gitlab.com/auto_lab/47332-student-excercises` (P4). It has none, so under default copyright no one may legally build from it, and the paper's own licence column reports this. CERN-OHL-S or CC BY-SA 4.0 for hardware and MIT or Apache-2.0 for code takes minutes.
- [ ] **TV-6.** §6 commitment: Zenodo deposits for P1, P3 and P4 by publication.
- [ ] **TV-7.** DTU funding lines (CAPeX DNRF P3; BIG-MAP 957189), unchanged from v1. Should anyone else on the team be added?

## 7. Owen A. Melville (OM) and team: P2 LEDbyXample

Owen A. Melville, Monique Ngan, Jeffrey Watchorn.

- [ ] **OM-1.** P2 row of Table 1: $80–160, 24 h, repository link.
- [ ] **OM-2.** Has LEDbyXample been built outside your team? If yes, by whom? Table 2 C2 becomes S.
- [ ] **OM-3.** Consent to the P2 row of Table 5.
- [ ] **OM-4.** Add a licence to `github.com/owen-melville/photo-reactor` (none found). This is the better outcome; the Licence column will then read ● and the sentence about unlicensed repositories in §6 can be cut or narrowed.
- [ ] **OM-5.** §6 commitment: a Zenodo DOI (GitHub release → Zenodo integration).

## 8. Tonio Buonassisi (TB) and MIT team: P5 DiSCO

Alexander E. Siemenn, Eunice Aissi, Basita Das; Tonio Buonassisi as PI.

- [ ] **TB-1.** P5 row of Table 1: $30–40 K, 3 months (analysed as 480 h at 1 FTE), three repositories. Does a DiSCO-level repository or paper now exist?
- [ ] **TB-2.** **Basita Das** is a P5 developer in Table 1 and a co-author on all three cited DiSCO module papers, but was never in the author list. Intended or an omission? Ask Basita directly; do not add or leave out without asking.
- [ ] **TB-3.** Consent to the P5 row of Table 5 and to the characterization in §§4–5: DiSCO's parts outweigh labour at $50/h, it is "designed to be learned from" rather than replicated, and the modules are published while the integrated platform has no build guide.
- [ ] **TB-4.** §6 commitment: Zenodo DOIs for the DiSCO repositories (some may already exist through the papers' code-availability statements).
- [ ] **TB-5.** MIT funding lines (none in v1).

Tonio's own read of the decision letter, which v3 is built on: *"present a strong hypothesis in the manuscript, and support the hypothesis with examples throughout the remainder of the manuscript."* Please check that the abstract and §1 now do that.

## 9. Jason E. Hein (JEH) and UBC team: P10 IvoryOS

Wenyu Zhang, Lucy Hao, Jason E. Hein. Jason is also the likely escalation point for P7.

- [ ] **JEH-1.** P10 row of Table 1: $0, 0–1 h per integration, GitLab link plus Zenodo concept DOI 10.5281/zenodo.15272617.
- [ ] **JEH-2.** Consent to the P10 row of Table 5 and to §7's reading of IvoryOS as *complicating* Claim 4.
- [ ] **JEH-3.** §6 commitment: already met by the existing Zenodo deposit.
- [ ] Your three affiliations (AC; UBC; University of Bergen), as in v1.

## 10. P7 team: electrochemical workflow

Yang Cao, Ethan Rajkumar, Ilya Yakavets. Escalation: SGB / Jason Hein.

- [ ] **P7-1. BLOCKING.** A public work-in-progress repository for the workflow (science-jubilee configuration, the rotating-disk-electrode tool CAD as it stands, control scripts, README), with its URL for Table 1. Also confirm the P7 row: $20 K, 300 h.
- [ ] **P7-2.** **Figure 8** comes from the original showcase-form figure set. For v3 the UBC/UofT/AC logo strip was cropped and a spell-check underline under "Opentrons" removed; the original is in `figures/source/`. Confirm the schematic is current.
- [ ] **P7-3.** **Ilya Yakavets** is a P7 developer in Table 1 but is not in the author list. Intended or an omission?
- [ ] **P7-4.** Consent to the P7 row of Table 5. It is currently empty and will be re-scored from the repository.
- [ ] **P7-5.** §6 commitment: a Zenodo deposit by publication.

## 11. Nadya Peek (NP) and UW science-jubilee team: P6

Blair Subbaraman, Danli Luo, Sonya Vasquez, Wm Salt Hale; Maria Politi is now at UBC. P6 row items are under BP-7 to BP-9.

- [ ] **NP-1.** §6 paraphrases your Accelerate 2024 closing keynote: documentation is mandatory for open-source hardware, documentation *is* the source, and "without documentation there is no open hardware". Confirm the attribution and wording.
- [ ] **NP-2.** Sonya Vasquez's affiliation. v1 gave none; v3 provisionally uses University of Washington. Sonya confirms or corrects it.
- [ ] **NP-3.** UW funding lines.

## 12. Contributors acknowledged with SGB

- **Chance Hattrick (P8):** SGB-7 (deposit, row, who replicated it), plus the ALL items.
- **Kenzo Aspuru-Takata (P9):** SGB-8 (canonical link, row), plus the ALL items.

---

## Status at the time of writing (2026-10-10)

| Category | Count |
| --- | --- |
| v2 `[NEEDED]` markers | 18 occurrences, 12 distinct items; all resolved or turned into an owned ID above (`revision-notes-v3.md` §2) |
| `[TO SUPPLY]` placeholders left in v3 | 5: three repositories, one deposit, one DOI |
| Sign-off IDs | listed by `tools/check_manuscript.py` |
| Blocking items | 2 repositories (DTU ×2 in one ask; P7) plus consents |
