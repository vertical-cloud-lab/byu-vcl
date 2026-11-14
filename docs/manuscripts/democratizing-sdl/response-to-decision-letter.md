# Response to the editorial decision on DD-PER-12-2024-000410

**Previous manuscript:** DD-PER-12-2024-000410, "Democratizing self-driving labs through user-developed automation infrastructure" (Perspective), rejected at editorial assessment on 9 January 2025 with an invitation to submit a substantially revised version. Preprint: [10.26434/chemrxiv-2025-zhkrf](https://doi.org/10.26434/chemrxiv-2025-zhkrf).
**Revised manuscript:** "Replication, not fabrication: documentation is the rate-limiting step for democratized self-driving labs" ([`manuscript-v3.md`](manuscript-v3.md)).
**Corresponding author:** Sterling G. Baird (Brigham Young University; Acceleration Consortium, University of Toronto).

Section, table and figure numbers below refer to the revised manuscript.

---

Dear Dr Schrier,

Thank you for your assessment of our Perspective and for the invitation to submit a substantially revised version. We agree with all three points in your decision. The manuscript was a workshop catalogue with a position buried near its end, it did not connect the projects to that position, and three of its projects had no supporting materials. We rebuilt it around a single hypothesis, which is now stated in the first sentence of the abstract. Every project is used as evidence for or against it, and in the case of the missing repositories that evidence counts against us. We respond to each point below, quoting your decision letter.

---

### Point 1: take a position and use the examples to validate it

> *"This is formally a "perspective" article, and thus it should take a position/opinion and then use the examples to articulate how these projects validate that hypothesis."*

**Response.** The revised manuscript is organized around one hypothesis: **documentation, not hardware, is the rate-limiting step for democratized self-driving labs.** It argues against the prevailing framing, in which democratization is a matter of lowering the price of hardware, including in recent work in this journal (refs 7 and 8).

**Changes.**

- **Abstract.** The abstract now opens with the hypothesis. It then states how we test it, gives the quantitative result, describes the exceptions, and states what follows. The original abstract began "As self-driving labs become widely deployed…" and described the workshop.
- **Section 1** sets out the hypothesis as a three-step argument: labour dominates first-build cost; savings therefore arise only on replication; and replication requires documentation. It then breaks the hypothesis into five claims, each tested in its own section (Sections 4–8), and says how each will be tested.
- **New quantitative evidence (Section 4, Figure 1, Tables 3 and 4).** The original Table 1 already reported each project's time to reproduce as well as its cost, but the original manuscript never used the time column. From these figures we derive each project's **break-even wage**, the loaded hourly rate at which build labour costs as much as the parts. The median is $30/h and the maximum $73/h, so at any realistic research labour rate labour dominates first-build cost. This statistic needs no assumed wage. Table 4 reports the sensitivity to the wage we do assume elsewhere. No new data were introduced, and the analysis script is in the ESI.
- **Limitations (Section 9)** states what the evidence cannot show and what a stronger test of the central claim would look like.

### Point 2: make explicit how each project supports or undermines the position

> *"The introduction to the current manuscript has some aspects of taking a position, but the way in which the projects support/undermine that position should be more explicitly articulated throughout. We are looking for more explicit information in how these projects fit into the themes that are identified."*

**Response.** We now state, for every project and every claim, whether the project supports, complicates or contradicts the claim. We state this **before** arguing any claim and give the criteria. Every section then returns to the projects by name.

**Changes.**

- **Table 2 (Section 3)** is a matrix of the ten projects against the five claims, marked *supports*, *supports as a negative case*, *complicates*, *contradicts* or *not informative*. Its caption gives the decision criteria, for example that for Claim 1 a project supports the claim if its break-even wage is below $50/h.
- **Every project description in Section 3 now ends with an explicit "Evidence:" sentence** saying which claims that project bears on and how. The original descriptions were self-contained vignettes that could have been deleted without changing the argument.
- **Each claim section (Sections 4–8) names the projects that undermine it and discusses them.** We kept these projects rather than dropping them:
  - **Claim 1 (cost).** P5 (DiSCO) and P7 (electrochemical workflow) are the only projects whose parts outweigh labour at $50/h. We use them to argue that "low-cost SDLs" are really two populations, and that the frugal-twin framing covers only one of them.
  - **Claim 2 (replication).** P5 is valuable for its capability rather than for being replicated.
  - **Claim 3 (documentation).** P8 spread to several groups with only forum threads and direct support from its developers as documentation.
  - **Claim 4 (skills).** P10 (IvoryOS) exists because programming *is* a barrier for some researchers.
- **Documentation self-audit (Section 6, Table 5).** We score all ten projects against the five capabilities a replicator needs (procure, build, configure, run, troubleshoot) and a licence column. Every cell is tied to a public resource in Supplementary Note S3, so the audit can be checked.

### Point 3: electronic supporting materials for three projects

> *"Three projects do not have electronic supporting materials (i.e., github repos) that would support the work. We would generally expect to see at least the current "work in progress" repositories for the current state of the work, in keeping with the journal's broader data & code policies."*

**Response.** We re-checked every project against its live public resources on 10 October 2026 and report the result in Table 1, with the evidence in Supplementary Note S3. The finding was more interesting than a simple gap:

- Two of the three projects the original submission listed as "manuscript in progress" had in fact put their files in public, P1 as a versioned release with a DOI and P7 as tool files in a public fork. But nothing in the manuscript linked to them, so no reader could have found them.
- The third project, P3, has nothing public. Its developers are creating a work-in-progress repository, and the manuscript will not be submitted without it.

In a Perspective arguing that documentation is the binding constraint, this is evidence and not only an omission, and Sections 5 and 6 treat it that way: a design file that cannot be found does not get replicated.

<!-- SIGN-OFF: TV-1. The P3 row below must be filled before submission. -->

| Project | Status in the original submission | Status in this revision |
| --- | --- | --- |
| P1 Powder dispensing module (DTU) | "Manuscript in progress" | Public since 27 January 2025 (release v1.0.0 with a Zenodo DOI), but not linked; now cited in Table 1 |
| P3 Rolling ball viscometer (DTU) | "Manuscript in progress" | Work-in-progress repository: **[TO SUPPLY: URL, DTU team]** |
| P7 Electrochemical workflow (AC/UBC) | "Manuscript in progress" | Electrode tool files public since August 2024 and tool control code since February 2025, but not linked; now cited in Table 1 |
| P8 Digital pipette integration | Two forum threads | Repository folder with the firmware and print files. Forum threads are no longer cited as documentation (Table 1 footnote) |
| P2, P4, P5, P6, P9, P10 | Repository or documentation links | All re-verified. Three renamed repositories updated (P2, P6, P9). Licences and archival deposits reported in Table 5 and Note S3 |
| Analysis in this Perspective | — | Script, derived values and sensitivity sweep provided as ESI and in a public GitHub repository; Zenodo DOI at acceptance, as the journal's code policy requires |

<!-- Checked 2026-10-10. P1's release (2025-01-27) postdates the original submission (December 2024) but predates
     the preprint (2025-02-12), whose Table 1 still said "manuscript in progress"; "not linked" is accurate for both.
     SIGN-OFF: TV-1 / P7-1 (teams confirm these are their files). -->

**Changes.**

- **Table 1** now gives, for every project, the verified location of its design files and documentation.
- **Table 5 and Note S3** report every project's licence and archival deposits alongside its documentation.
- **Section 6** asks builders to deposit designs archivally from the first release and to check that the deposit actually contains the design; one of our own deposits archives empty folders. We hold ourselves to that: every project has a public repository at submission and will have an archival deposit with a persistent identifier by publication.
- **The Data availability statement** covers the analysis code and the evidence for every documentation score.

---

### Other changes

These were not requested in the decision, but the editor and referees will want to know about them.

1. **New title, and a differentiation from Doloi *et al.*** After our submission, this journal published Doloi *et al.*, "Democratizing self-driving labs: advances in low-cost 3D printing for laboratory automation" (*Digital Discovery* 2025, 4, 1685; ref 8). Our original title would now collide with it. We have retitled the manuscript. Section 1 ("Relation to existing work") cites Doloi *et al.* and explains how we differ: they catalogue what can be built cheaply, while we argue that capital cost is close to irrelevant to whether anything is democratized.
2. **Engagement with the open-hardware literature.** Pearce's return-on-investment analysis, Bonvoisin *et al.* on the "source" of open hardware, and the DIN SPEC 3105 documentation standard are now cited and built on (Sections 1, 5 and 6).
3. **References brought up to date.**
   - Four preprints are now cited as their published versions: Archerfish in *Digital Discovery*, the contact-mapping robot in *Science Advances*, IvoryOS in *Nature Communications*, and OpenFlexure in *Biomedical Optics Express*.
   - Reference 6 now carries the 2026 Author Correction to its title.
   - The ASTM viscosity standard is cited in its current edition.
   - The OSHWA definition, previously uncited because of a numbering collision, now has its own reference.
   - All references were checked against Crossref.
4. **Figures.** Figures now appear in citation order (the original printed 1, 2, 4, 3, 5, 6). Two projects that had no figure now have one (Figures 4 and 8). The figures are taken from the source files at higher resolution.
5. **Authorship.**
   - Sterling G. Baird is now corresponding author. Brenden Pelkie, who corresponded on the original submission, remains first author.
   - Seth Leavitt (Brigham Young University) joins the author list for coordinating the revision and for conceptualization of the revised argument.
   - Sterling G. Baird's affiliation now leads with Brigham Young University, his current institution.
   - The Author contributions statement now uses CRediT roles.
   <!-- SIGN-OFF: SGB-5. If Basita Das and/or Ilya Yakavets are added (TB-2, P7-3), say so here with the reason:
        both were credited as project developers in the original Table 1 but omitted from the author list. -->
6. **Use of generative AI.** In line with RSC policy, a statement discloses that the revision was drafted with the assistance of a large language model under the authors' direction, and that the authors verified all such content and take responsibility for it.

We believe the revised manuscript is the Perspective your decision asked for: a contestable position, stated first, and tested project by project against the community's own evidence, including where that evidence goes against us. We would be glad to have it considered for *Digital Discovery*.

Yours sincerely,

Sterling G. Baird, on behalf of all authors
