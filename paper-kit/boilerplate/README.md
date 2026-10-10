# Boilerplate: to fill, not to invent

Every journal asks for the same handful of statements under different
headings. The words live once, in
[`manuscript/declarations/`](../manuscript/declarations/), and each
`main-<journal>.tex` gives them its publisher's headings and order. Every
blank is a violet `\fillme{...}` that `make submission-check` will not let
through.

The rule for all of them: **copy from the record, never from memory or from
another paper.** Award numbers come from the award letter, roles from the
authors themselves, DOIs from the deposit, interests from each author's own
answer.

## CRediT: who did what

[`declarations/credit.csv`](../manuscript/declarations/credit.csv) holds the
14 roles of the CRediT taxonomy (ANSI/NISO Z39.104-2022,
<https://credit.niso.org/>) as rows, and the authors, in order, as columns.
Mark a cell `x`, or `lead`, `equal` or `supporting` where the degree matters.

| Role | First Author | Second Author | Sterling G. Baird |
|---|---|---|---|
| Conceptualization | | | |
| Data curation | | | |
| Formal analysis | | | |
| Funding acquisition | | | |
| Investigation | | | |
| Methodology | | | |
| Project administration | | | |
| Resources | | | |
| Software | | | |
| Supervision | | | |
| Validation | | | |
| Visualization | | | |
| Writing – original draft | | | |
| Writing – review & editing | | | |

`make credit` turns it into `credit-statement.tex` ("A. Author:
Conceptualization, Methodology. ..."), the form Elsevier, HardwareX,
Springer Nature and RSC print, and `credit-table.tex`, the table above in
LaTeX, for the SI or a cover letter. At G3 each author checks **their own
column** and nobody else's (the sign-off checklist asks).

## Data and code availability

[`declarations/availability.tex`](../manuscript/declarations/availability.tex):
the data behind every figure (the `data/` snapshots with their READMEs), the
figure scripts and the analysis, control or design files, archived on Zenodo
under a stated licence, with the development repository named.

- The DOI placeholder is `https://doi.org/10.5281/zenodo.NNNNNNN`. Zenodo
  reserves a DOI before a record is published (in the upload form: "Do you
  already have a DOI?", answer No, then "Get a DOI now!"), so the submitted
  manuscript can carry the real one. A GitHub release archived through
  Zenodo's GitHub integration also works.
- Licence: CC BY 4.0 for data and MIT for code is the default the
  placeholder suggests. Check it against the repository's own `LICENSE`, and
  for hardware against HardwareX's list of open licences.
- Say what is *not* shared and why, rather than leaving it out.
- Headings: "Data availability" (Elsevier, Springer Nature, RSC), "Data
  Availability Statement" (ASME); Springer Nature also lists "Code
  availability" and "Materials availability" separately.

## Funding

[`declarations/funding.tex`](../manuscript/declarations/funding.tex): one line
per award, funder named as in the Crossref Funder Registry
(<https://www.crossref.org/services/funder-registry/>), award number exactly
as on the award letter. The PI supplies the list at G3. Student fellowships
and mentored-research awards are worded the way their recipient confirms.
ASME prints awards as a "Funding Data" list; Springer Nature under
"Declarations: Funding"; Elsevier and RSC as a "Funding" section or in the
Acknowledgements, as the journal's guide says.

## Conflict of interest

[`declarations/coi.tex`](../manuscript/declarations/coi.tex): "The authors
declare no competing interests," behind a `\fillme{Every author has
confirmed:}` marker that comes off only when every author has answered (the
sign-off checklist's question 6). An author with a relevant patent, company,
consultancy or equity names it instead. Headings: "Declaration of competing
interest" (Elsevier), "Competing interests" or "Conflict of interest"
(Springer Nature: the journal's word), "Conflicts of interest" (RSC, whose
template says to write "There are no conflicts to declare" when there are
none), "Conflict of Interest" (ASME).

## Generative AI

One paragraph that satisfies Elsevier, Springer Nature, RSC and ASME, with
each publisher's current wording quoted, linked and dated:
[`generative-ai.md`](generative-ai.md). The paragraph itself is
[`declarations/genai.tex`](../manuscript/declarations/genai.tex), and research
use of AI (code, analysis) is
[`declarations/genai-methods.tex`](../manuscript/declarations/genai-methods.tex).
