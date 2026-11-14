# Revision notes for v2

**What this file is:** the changelog from [`manuscript-v1.md`](manuscript-v1.md) to [`manuscript-v2.md`](manuscript-v2.md), the title shortlist, and the list of things only the co-authors can resolve. Prepared for [issue #188](https://github.com/vertical-cloud-lab/byu-vcl/issues/188). The diagnosis behind these changes is in [`revision-assessment.md`](revision-assessment.md).

**Target:** resubmission to *Digital Discovery* following the 2025-01-09 rejection of DD-PER-12-2024-000410, which carried an explicit invitation to resubmit a substantially revised version.

---

## 1. The thesis

The editor's objection was one of genre: a Perspective must take a position and use its examples to validate it. v1 had positions, but they were on page 14, and the ten projects were arranged as a taxonomy of hardware rather than as evidence.

v2 is built on a single claim, stated in the first 300 words:

> User-developed automation is not a cost-reduction strategy at the point of first build — labour dominates the bill of materials at any realistic loaded rate. It becomes one only on replication, and replication only happens when documentation is good enough to cause it. **Documentation, not hardware, is the rate-limiting step.**

Five sub-claims follow from it, each with its own section, and Table 2 states in advance which projects support, complicate or contradict each one. That table is the direct answer to the editor's second objection.

## 2. Title shortlist

"Democratizing self-driving labs…" is no longer usable: Doloi *et al.*, "Democratizing self-driving labs: advances in low-cost 3D printing for laboratory automation," *Digital Discovery* **2025**, *4* (7), 1685–1721 ([10.1039/D4DD00411F](https://doi.org/10.1039/D4DD00411F)) occupies it in the target journal.

Ranked, with the trade-off for each:

| | Title | Why / why not |
|---|---|---|
| **1** | **Replication, not fabrication: documentation is the rate-limiting step for democratized self-driving labs** | *Currently in the draft.* States the position and the mechanism; the antithesis is memorable; no collision. Longest of the set. |
| 2 | The parts are the cheap part: rethinking the economics of user-developed laboratory automation | Most quotable, most obviously a Perspective. Slightly informal for RSC; drops "self-driving labs" from the title, which costs discoverability. |
| 3 | User-developed automation for self-driving labs pays off only on the second build | Sharpest single assertion. Narrower — foregrounds Claim 2 and leaves documentation implicit. |
| 4 | Open hardware is not a cost-saving measure: evidence from ten user-developed self-driving lab projects | Signals the counter-intuitive result and the evidence base. "Evidence from ten…" edges back towards report framing. |
| 5 | Documentation as infrastructure: what ten user-developed automation projects reveal about democratizing self-driving labs | Safest and most conventional. Also the least opinionated — which is what got v1 rejected. |

**Recommendation:** #1 or #2. Both differentiate cleanly from Doloi *et al.*, and the differentiation is substantive rather than cosmetic: their framing is cost reduction through cheap 3D printing, and v2 argues the cost framing is the error. §1 "Relation to existing work" cites them and disagrees explicitly — which is what an editor checking for duplication will look for.

## 3. Structural changes

| v1 | v2 |
|---|---|
| Abstract opens "14 examples… were shared" | Abstract opens with the claim and the quantitative result |
| Introduction → position gestured at | §1 states thesis in the first 300 words, with Figure 1 as the evidence, plus a "Relation to existing work" subsection differentiating from refs 7 and 8 |
| Survey: two sentences on p. 14 | §2, up front, establishing the premise the rest of the paper tests |
| Projects grouped by hardware type (stand-alone / end-to-end / software) | §3, same descriptions condensed, but preceded by **Table 2**, which states for every project which claim it supports (S), complicates (C) or contradicts (X) |
| Discussion: five positions, unconnected to the projects | §§4–8, one section per claim, each drawing explicitly on named projects including the ones that undercut it |
| — | §4 **new quantitative analysis**: break-even wage, labour share, rate sensitivity (Tables 3–4, Figure 1) |
| — | §6 **new documentation self-audit** (Table 5) |
| — | §9 **new limitations section** |
| Outlook | §10, rewritten as obligations rather than aspirations |

Full project descriptions as contributed move to Supplementary Note S1, so every contributor's text survives in full while the main text stays argument-led. Condensed versions remain in the main text so no project — and no contributor — becomes invisible.

## 4. The labour analysis

[`analysis/labor_cost_analysis.py`](analysis/labor_cost_analysis.py) is self-contained; run it with `python labor_cost_analysis.py`. It reads nothing but the Table 1 figures already published in v1 — **no new data is introduced** — and writes `table1-derived.csv`, `sensitivity.csv` and `figures/fig1-labour-vs-bom.png`.

Two conversions are stated in the manuscript rather than buried:

- reported ranges enter at their midpoint (P2 `$80–160` → `$120`; P10 `0–1 h` → `0.5 h`);
- P5's "3 months" is read as 12 weeks × 40 h = 480 h at 1 FTE.

The headline statistic is the **break-even wage** — the loaded hourly rate at which labour cost equals the bill of materials. It is worth leading with because it *removes* the arbitrary rate assumption instead of hiding it: median $30/h, maximum $73/h (DiSCO). A reviewer who dislikes the $50/h figure in Table 3 still has to engage with Table 3's final column.

Supporting numbers: median replication time 17 h; 8 of 10 projects reproducible in ≤ 100 h; range 0.5–480 h.

## 5. Reference corrections

**Four cited preprints have been published since submission** — leaving them would read as inattention:

| v1 | v2 |
|---|---|
| 14 Archerfish, ChemRxiv | **17** — *Digital Discovery* **2025**, *4* (4), 896–909, [10.1039/D4DD00249K](https://doi.org/10.1039/D4DD00249K) — *in the target journal* |
| 16 SDCNN, arXiv 2411.09892 | **19** — *Sci. Adv.* **2025**, *11* (27), eadw7071, [10.1126/sciadv.adw7071](https://doi.org/10.1126/sciadv.adw7071). **Title changed on publication** to "A self-supervised robotic system for autonomous contact-based spatial mapping of semiconductor properties" |
| 29 IvoryOS, Research Square | **32** — *Nat. Commun.* **2025**, *16* (1), 5182, [10.1038/s41467-025-60514-w](https://doi.org/10.1038/s41467-025-60514-w). **Author list expanded** from 10 to 17 on publication |
| 23 OpenFlexure, bioRxiv 861856 | **26** — *Biomed. Opt. Express* **2020**, *11* (5), 2447–2460, [10.1364/BOE.385729](https://doi.org/10.1364/BOE.385729). *Was already published five years before v1 was posted.* |

**Other reference fixes:**

- **Ref 7 was double-booked** in v1 — cited in the Introduction for the Open Source Hardware Association and again in the powder-dispensing section for the OpenTrickler repository, while the list contained only OpenTrickler. **OSHWA was therefore uncited** despite the paper leaning on it to define "open hardware." Now split: **9** = OSHWA Definition 1.0, **10** = OpenTrickler.
- **Three bare-URL references given proper citations**: v1 ref 12 → **15** (Ginsburg *et al.*, full author list, pp 2147–2152); v1 ref 22 → **25** (Guevarra *et al.*, *Digit. Discov.* **2023**, *2* (6), 1806–1812); v1 ref 10 → **13** (ASTM D1200-10(2018), formal designation).
- **Missing bibliographic detail added**: v1 ref 20 (Politi *et al.*) had no volume or pages → *Digit. Discov.* **2023**, *2* (4), 1042–1057, [10.1039/D3DD00033H](https://doi.org/10.1039/D3DD00033H). Article numbers added for refs 1 and 20 (ZoMBI).
- **New:** ref **8**, Doloi *et al.*, cited and explicitly differentiated from in §1.
- All 34 references verified against Crossref, and numbering is in strict order of first citation.

## 6. Smaller fixes

- **Figure order.** v1's figures printed 1, 2, **4**, **3**, 5, 6 — a Word float artefact. v2 renumbers into citation order and the files were renamed to match: the new Figure 1 is the labour analysis, and the old DiSCO/colour-bot pair is un-swapped. Figures now run 1–7 with no gaps, verified programmatically.
- **Author list.** Sonya Vasquez's missing affiliation superscript provisionally set to 1 (University of Washington, per ref 21) — **confirm**. Ethan Rajkumar's stray double comma (`2,5,,`) corrected. Basita Das appears as a DiSCO author in Table 1 and on refs 17–19 but is absent from the author list; flagged in an HTML comment in the manuscript rather than resolved, because adding a person to an author list is not a formatting fix.
- **Forum links demoted.** P8's two `accelerated-discovery.org` Discourse threads are no longer cited as documentation. Forum posts carry no persistent identifier and are not archival, and by the paper's own Claim 3 they do not qualify — so Table 1 marks P8 as needing an archival deposit and a footnote says why. Doing otherwise would have the paper violating its own thesis in its own evidence table.

## 7. What only the co-authors can resolve

Every one of these is marked `[NEEDED]` in the manuscript.

**Blocking — the paper cannot be resubmitted without these:**

1. **Repositories for P1, P3 and P7** (powder dispensing module and rolling ball viscometer, DTU; electrochemical workflow, AC/UBC). This was the editor's third objection and it is the only one writing cannot fix. The bar is low — Schrier explicitly accepted "work in progress" repositories. A stub with CAD, a BOM and an honest README saying "pre-release, documentation incomplete" clears it.
2. **Consent for the Table 5 documentation self-audit.** It scores co-authors' own projects, three of them as empty rows. It must be published as a collective self-audit the contributors have agreed to. If a team objects, remove the row and note the omission — do not soften the table.
3. **The commitment sentence in §6** ("every project will have an archival deposit at publication") binds ten teams. Do not publish it until every team agrees and every deposit exists.

**Needed for the sections as drafted:**

4. **Survey material** (n = 58): the instrument verbatim, the full response distribution, the response rate, whether responses were collected before/during/after the showcase, and consent status. §2 is currently thin because only two results from it were ever reported.
5. **Selection criterion for 10 of 14 projects.** A reviewer will ask, and unexplained it reads as selection bias.
6. **A figure for P3**, the rolling ball viscometer — the only hardware project without one.
7. **Zenodo DOIs** for all ten projects, so the cover letter can state that every contributed project is citable, versioned and archived. This answers objection 3 emphatically rather than minimally.
8. **Author-contribution statement** updated for the §4 analysis and §6 audit, which are new to this version.
9. **Brenden's "manifesto"**, referred to in the issue thread but not findable publicly — needed before it can be folded in.
10. **Confirm ChemRxiv v1 is what was submitted.** The posted PDF was generated 2025-02-10, a month *after* the 2025-01-09 rejection, so it may already contain post-rejection edits. If it does, this changelog is measured against the wrong baseline.

## 8. For the cover letter

- The preprint has been **cited 6 times** while under revision — *Science Robotics*, *Nature Computational Science*, *Materials Horizons*, *Digital Discovery*. Evidence the community is already using it.
- Address the Doloi *et al.* overlap **before the editor raises it**. RSC requires a Perspective to "add to the existing literature, rather than duplicate existing articles," and the previous title made the collision unmissable. The differentiation is clean and substantive: they catalogue what can be built cheaply; v2 argues capital cost is close to irrelevant to whether anything is democratized.
- Map the three objections to the three fixes: (1) genre → thesis-first restructure with a new quantitative analysis; (2) projects not tied to themes → Table 2, an explicit per-project supports/complicates/contradicts matrix; (3) missing electronic supporting material → archival deposits with DOIs for all ten.
- Link rot was checked at the previous assessment: all 14 project URLs cited in v1 returned HTTP 200.
