# Initial assessment — revising *Democratizing self-driving labs through user-developed automation infrastructure*

**Prepared:** 2026-08-26 · **For:** [issue #188](https://github.com/vertical-cloud-lab/byu-vcl/issues/188)
**Source assessed:** ChemRxiv v1, [10.26434/chemrxiv-2025-zhkrf](https://doi.org/10.26434/chemrxiv-2025-zhkrf) (posted 2025-02-12; PDF generated 2025-02-10)
**Journal history:** Digital Discovery MS ID DD-PER-12-2024-000410 — rejected 2025-01-09 by Dr. Joshua Schrier, with an explicit invitation to resubmit a substantially revised version.

---

## 1. The editor's three objections, restated

1. It is formally a Perspective, so it must **take a position** and then use the examples to show how the projects **validate that position**.
2. The Introduction gestures at a position, but how each project **supports or undermines** it is never made explicit. The editor wants the projects tied to the identified themes.
3. **Three projects have no electronic supporting material** (repos). Even "work in progress" repos would satisfy the journal's data & code policy.

RSC defines a Perspective as "an authoritative state-of-the-art account… a personal account of research, or **a critical analysis** of a topic of current interest," which "should be timely and add to the existing literature, **rather than duplicate existing articles**." Points 1 and 2 are really one problem — genre — and it is fixable without new experiments. Point 3 is an administrative gate that only the contributors can clear.

## 2. Diagnosis: the manuscript is a catalogue wearing a Perspective's clothes

The paper is well written and the material is genuinely interesting. The problem is architectural, not prose-level.

**The organising principle is a taxonomy of hardware, not a taxonomy of claims.** Sections run *Stand-alone tools → End-to-end automation systems → Control and orchestration software*. That tells a reader what kind of thing each project is. It never tells them what each project *proves*.

**The ten project sections are self-contained vignettes.** They average ~350 words, were written by different contributors (Author Contributions: "All other authors: Contribution of project descriptions"), and **not one of them closes by tying back to a thesis.** They are cleanly excisable: delete any one and the argument is unchanged — which is the diagnostic signature of evidence that is not doing argumentative work.

**The opinions do exist — they are just quarantined in the last three pages.** The Discussion/Outlook contains at least five defensible, contestable positions, and they are good ones:

| # | Position already in the text (p. 14–15) | Status |
|---|---|---|
| A | "The notion that user-developed automation is cheaper is worth critically examining… these costs may negate any savings on capital expenses" | Genuinely counter-intuitive; **strongest thing in the paper** |
| B | "Without documentation, there is no open hardware" | Hard normative claim, quotable, attributed to Peek's keynote |
| C | Skill gap is in the "small stuff" (wire crimping, part design), not the science — with a causal hypothesis (Python-in-curriculum) for why software isn't the bottleneck | Testable, contrarian |
| D | "Automation involving hazardous conditions… should not be built in an ad-hoc manner" | Limit-setting; invites productive disagreement |
| E | User-developed ≠ low-cost; the field's "frugal twin" framing is too narrow | One sentence; deserves a section |

**So the fix is not "add opinions." It is "move the opinions to the front and make the projects earn their place under them."** The paper already contains its own thesis; it buries it on page 14 and never connects it back to the ten examples that were supposed to be the evidence.

**The abstract signals "report" from the first line** — "14 examples… were shared", "ten contributed examples… are highlighted." An editor triaging article types reads this and sees a workshop report. The abstract must lead with the claim, not the count.

## 3. The highest-leverage fix: the paper is sitting on unanalysed quantitative evidence

Table 1 lists **both cost-to-reproduce and time-to-reproduce for all ten projects** — and the manuscript never does anything with the second column. That table is the evidence for position A, and it can be made quantitative.

Assuming a loaded rate for the person doing the build (and treating "3 months" for DiSCO as ~480 h):

| Project | BOM | Build hours | Labour @ $50/h | Labour share of true cost |
|---|---:|---:|---:|---:|
| IvoryOS | $0 | 0.75 | $38 | 100% |
| LEDbyXample photoreactor | $120 | 24 | $1,200 | 91% |
| OpenFlexure public control | $300 | 30 | $1,500 | 83% |
| Science-jubilee | $2,000 | 100 | $5,000 | 71% |
| Powder dispensing module | $300 | 10 | $500 | 63% |
| Rolling ball viscometer | $300 | 10 | $500 | 63% |
| Color mixing bot | $300 | 10 | $500 | 63% |
| Digital pipette Jubilee integration | $100 | 3 | $150 | 60% |
| Electrochemical workflow | $20,000 | 300 | $15,000 | 43% |
| DiSCO platform | $35,000 | 480 | $24,000 | 41% |

**Sensitivity to the rate assumption** (this belongs in the paper, stated openly):

| Loaded rate | Projects where labour > BOM | Median labour share |
|---|---|---|
| $25/h | 4 / 10 | 45% |
| $50/h | 8 / 10 | 62% |
| $75/h | 10 / 10 | 71% |

And note the crucial asymmetry the paper already flags but does not exploit: these are *reproduction* hours. **Original development took "hundreds to thousands of hours"** (the manuscript's own words), so first-build labour share is far higher still — while replication labour is only 3–100 h for eight of the ten projects.

That gives you a sharp, quantitative, falsifiable thesis derived entirely from the authors' own contributed data:

> **User-developed automation is not a cost-reduction strategy at the point of first build — labour dominates BOM for most projects at any realistic rate. It becomes a cost-reduction strategy only on replication, and replication only happens when documentation is good enough to make it happen. Documentation, not hardware, is therefore the rate-limiting step for democratised SDLs.**

This is exactly what Schrier asked for: a position, with the contributed projects as the evidence that validates it. It also differentiates the paper from every other "low-cost SDL" article, because it argues *against* the naive low-cost framing.

## 4. Turn objection 3 from a liability into evidence

The three projects lacking repos are:

| Project | Contributors to chase | Table 1 currently says |
|---|---|---|
| Powder dispensing module | Chang, Gambhir, Ziskason, Nyeland (DTU) | "Manuscript in progress" |
| Rolling ball viscometer | Chang, Gambhir, Ziskason, Nyeland (DTU) | "Manuscript in progress" |
| Electrochemical workflow on science-jubilee | Cao, Rajkumar, Yakavets (AC / UBC) | "Manuscript in progress" |

Two observations.

**First, the bar is low.** Schrier explicitly wrote that he would expect "at least the current 'work in progress' repositories." A stub repo with CAD, a BOM, and an honest README that says "pre-release, documentation incomplete" clears it. Eighteen months on, these are still listed as in progress, so this needs an owner and a deadline, not another round of asking.

**Second — and this is the interesting move — the gap is itself data for thesis B.** The paper argues that documentation is the bottleneck and that documentation work is not rewarded by academic incentives. Then three of its own ten exemplars, from well-resourced groups, arrive with nothing publishable. **Say that out loud.** A short, honest self-audit — score all ten projects against the paper's own five verbs ("procure, build, configure, run, troubleshoot") and report how many pass — converts an embarrassment into the most credible paragraph in the article. Perspectives are allowed to be self-critical; it is close to the only genre that is.

Frame it as a collective self-audit with a commitment attached (every project has an archived deposit by resubmission), not as grading co-authors in public. Get consent from the three teams before publishing any scoring.

**Also worth upgrading:** two Table 1 entries point at `accelerated-discovery.org` Discourse threads. Forum posts are not archival and do not carry persistent identifiers. Minting a **Zenodo DOI for each of the ten projects** would let the cover letter say every contributed project now has a citable, versioned, archived deposit — which answers objection 3 emphatically rather than minimally.

## 5. What has changed in the 18 months since submission

I checked; these all need attention before resubmission.

**Three cited preprints are now published.** Leaving them as preprints in a resubmission reads as inattention:

| Ref | Was | Now |
|---|---|---|
| 14 | Archerfish, ChemRxiv | ***Digital Discovery*** **2025**, [10.1039/d4dd00249k](https://doi.org/10.1039/d4dd00249k) — the target journal |
| 16 | SDCNN, arXiv 2411.09892 | ***Science Advances*** **2025**, [10.1126/sciadv.adw7071](https://doi.org/10.1126/sciadv.adw7071) |
| 29 | IvoryOS, Research Square | ***Nature Communications*** **2025**, [10.1038/s41467-025-60514-w](https://doi.org/10.1038/s41467-025-60514-w) |

**A title-colliding paper now exists in the target journal.** Doloi *et al.*, "**Democratizing self-driving labs: advances in low-cost 3D printing for laboratory automation**," *Digital Discovery* 2025, [10.1039/d4dd00411f](https://doi.org/10.1039/d4dd00411f) — different group, three rounds of review, published. This cuts three ways:

- **Retitle.** "Democratizing self-driving labs…" is now taken in *Digital Discovery*.
- **Differentiate explicitly**, because RSC requires a Perspective to "add to the existing literature, rather than duplicate existing articles" and an editor will make this comparison. Fortunately the differentiation is clean: their framing is cost reduction via low-cost 3D printing; the thesis proposed in §3 is that **the cost framing is wrong**. Cite them, then disagree with them. That is what a Perspective is for.
- **It is a precedent** for what this editor accepted in this space.

**The preprint has already been cited 6×**, including in *Science Robotics*, *Nature Computational Science*, *Materials Horizons*, and *Digital Discovery*. Worth a line in the cover letter: the community is already using this.

**Link rot: none.** All 14 cited project URLs still return HTTP 200 as of 2026-08-26.

## 6. Smaller defects found while reading

- **Reference 7 is double-booked.** It is cited in the Introduction for the Open Source Hardware Association and again in the powder-dispensing section for the OpenTrickler repo. The reference list contains only OpenTrickler — **OSHWA is uncited**. Since the paper leans on OSHWA to define "open hardware," this needs a real citation.
- **Figures are out of order** in the PDF: they appear 1, 2, 4, 3, 5, 6 (Figure 4 on p. 8 precedes Figure 3 on p. 9). A Word float artefact, but sloppy in a resubmission.
- **The rolling ball viscometer has no figure**, while every other hardware project does.
- **Author list**: Sonya Vasquez carries no affiliation superscript; Ethan Rajkumar has a stray double comma ("Ethan Rajkumar2,5,,"). Basita Das is credited as a DiSCO author in Table 1 but is not in the author list — confirm whether that is intended.
- **10 of 14 projects, unexplained.** The paper says 14 were presented and 10 are discussed but never states the selection criterion. A reviewer will ask. Either give the criterion or say the other four declined.
- **The survey is badly underused** — this is precisely Brenden's point about using more survey results. n=58 gets two sentences on page 14, and it is the *only* community-level quantitative evidence in the paper. It should establish the premise up front ("the community wants this and will contribute") before the projects supply the evidence ("here is what happens when they try"). Report the instrument and full results as ESI, and give the response rate — n=58 out of how many attendees?
- **Consider adding a limitations paragraph.** Ten self-selected projects from one workshop, described by their own developers, with self-reported costs and times. Saying so plainly costs nothing and buys credibility.

## 7. Proposed restructure

Roughly the same length; the projects stop being a catalogue and become evidence.

1. **Introduction** — state the thesis in the first 300 words. Cost is the wrong lens; capability, replication and documentation are the right ones.
2. **The community wants this** — survey (n=58) up front, with the instrument in ESI.
3. **Claim 1: user-developed ≠ low-cost.** Table 1 plus the labour analysis in §3. Three orders of magnitude of BOM ($0–$40K) is not one phenomenon. Distinguish the sub-$500 single-function/pedagogical tools from the $20–40K bespoke research platforms; argue that the "frugal twin" framing covers only the first population.
4. **Claim 2: the economics only close on replication.** Digital Pipette (reproduced by several groups; 3 h to replicate) and science-jubilee (documentation, Discord, workshops) are the positive controls. The three repo-less projects are the negative controls. This is the section where the ten projects finally do argumentative work.
5. **Claim 3: without documentation there is no open hardware** — including the self-audit from §4, and the incentives argument.
6. **Claim 4: the skill gap is in the small stuff** — the wire-crimping observation, the Python-curriculum hypothesis, and a concrete prescription (a standard curriculum module; be specific about what is in it).
7. **Claim 5: know the limits** — hazardous automation, validation-critical instruments, and a direct ask to vendors for modular interfaces and documented APIs.
8. **Outlook** — what the community should do next, stated as obligations rather than aspirations.

Under each claim, every project cited must answer *supports / complicates / contradicts*. Projects that support nothing get cut. Projects that **complicate** a claim are the most valuable — DiSCO and the electrochemical workflow both undercut the low-cost narrative, and the paper should say so rather than tuck it into a subordinate clause.

## 8. Open questions and what is needed from the co-authors

- **The Google Doc is gone.** The markdown in this directory is now the working source, recreated from the ChemRxiv PDF. Decide whether to keep editing here (version-controlled, diffable, good for a 27-author paper) or re-import to Docs/Word.
- **Is ChemRxiv v1 identical to the submitted DD version?** The PDF was generated 2025-02-10, a month *after* the 2025-01-09 rejection, so it may already contain post-rejection edits. Brenden would know.
- **Brenden's "manifesto"** is not findable anywhere public. Needed from Brenden/Lilo before it can be folded in.
- **Raw survey data + instrument** (n=58) — needed for §2 and the ESI.
- **Repos or Zenodo deposits** from the DTU team (powder dispenser, viscometer) and the AC/UBC team (electrochemical workflow) — the one true blocker.
- **Retitle.** Needs author-group agreement given the collision with 10.1039/d4dd00411f.
- **Consent** from the three teams before publishing any documentation self-audit.

## 9. Bottom line

The rejection is not about quality; it is about genre, and the editor said as much when he invited resubmission. The manuscript already contains a strong, counter-intuitive thesis and the quantitative evidence to support it — the thesis is on page 14 and the evidence is an unanalysed column of Table 1. Moving the first to the front and analysing the second turns a workshop report into a Perspective without new experiments.

The one thing that cannot be fixed by writing is the three missing repos. That needs an owner and a date.
