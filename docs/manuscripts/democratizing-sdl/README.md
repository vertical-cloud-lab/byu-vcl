# Democratizing self-driving labs through user-developed automation infrastructure

Working directory for the revision and resubmission of the Accelerate 2024 "Democratizing
Self-Driving Labs" workshop Perspective. Tracked in
[issue #188](https://github.com/vertical-cloud-lab/byu-vcl/issues/188).

## Contents

| File | What it is |
|---|---|
| [`manuscript-v3.md`](manuscript-v3.md) | **The submission text.** Hypothesis-first, Sterling G. Baird as corresponding author. Every statement a co-author must still confirm carries a `<!-- SIGN-OFF: ID -->` comment; the few values that do not exist yet are marked `[TO SUPPLY: …]` |
| [`sign-off-checklist.md`](sign-off-checklist.md) | **What each co-author has to confirm**, by person and team, with the blocking items first |
| [`response-to-decision-letter.md`](response-to-decision-letter.md) | Point-by-point response to the DD-PER-12-2024-000410 decision |
| [`cover-letter.md`](cover-letter.md) | Cover letter for the resubmission |
| [`esi/supplementary-information.md`](esi/supplementary-information.md) | ESI: Note S1 (project descriptions as contributed), S2 (survey), S3 (evidence for every Table 5 cell), S4 (labour analysis) |
| [`revision-notes-v3.md`](revision-notes-v3.md) | Changelog v2 → v3, what happened to every v2 `[NEEDED]` marker, and the 2026-10-10 verification of all ten projects |
| [`tools/check_manuscript.py`](tools/check_manuscript.py) | Renumbers citations into first-appearance order and lists open sign-off IDs and placeholders. Run it after any edit that adds a reference |
| [`manuscript-v2.md`](manuscript-v2.md) | v2: the first restructure around the thesis. Superseded by v3 |
| [`revision-notes-v2.md`](revision-notes-v2.md) | Changelog v1 → v2 and the title shortlist (§2) |
| [`analysis/`](analysis/) | Self-contained script deriving the break-even wage and labour shares from Table 1, plus its CSV outputs |
| [`manuscript-v1.md`](manuscript-v1.md) | Editable markdown recreation of the v1 text — kept as the baseline to diff against |
| [`submitted/`](submitted/) | **The as-submitted Word source**, contributed by Brenden Pelkie. The authoritative v1 record |
| [`chemrxiv-2025-zhkrf.pdf`](chemrxiv-2025-zhkrf.pdf) | The ChemRxiv v1 PDF as posted (18 pp.) |
| [`figures/`](figures/) | Nine figures in citation order, extracted from the Word source at full embedded resolution |
| [`figures/source/`](figures/source/) | Unused originals and alternates, kept so the co-authors can choose |
| [`revision-assessment.md`](revision-assessment.md) | Initial assessment against the editor's rejection points, plus the proposed restructure that v2 implements |

## Provenance

- **DOI:** [10.26434/chemrxiv-2025-zhkrf](https://doi.org/10.26434/chemrxiv-2025-zhkrf)
- **Posted:** 2025-02-12 · **PDF generated:** 2025-02-10 (Microsoft Word for Microsoft 365)
- **Word source:** created 2025-02-04, last modified 2025-02-11 by Brenden Pelkie; 18 pp., 8 819 words
- **License:** CC BY-NC 4.0
- **Journal history:** submitted to *Digital Discovery* as MS ID DD-PER-12-2024-000410;
  rejected 2025-01-09 by Dr. Joshua Schrier with an explicit invitation to resubmit a
  substantially revised version.

**How the PDF was retrieved.** ChemRxiv sits behind a Cloudflare managed challenge that
returns HTTP 403 to datacenter IPs — this affects `chemrxiv.org/doi/pdf/...`, the public
API (`/engage/chemrxiv/public-api/v1/items/doi/...`), and the asset gateway alike, with or
without a browser user-agent. The route that worked:

1. Resolve metadata through [Crossref](https://api.crossref.org/works/10.26434/chemrxiv-2025-zhkrf)
   (title, 27 authors, abstract, posted date) — not blocked.
2. Get the ChemRxiv item ID and asset URL from
   [OpenAlex](https://api.openalex.org/works/doi:10.26434/chemrxiv-2025-zhkrf)
   (`best_oa_location.pdf_url`) — item `67a4ffb6fa469535b94a3ad9`.
3. Pull the PDF from the Wayback Machine snapshot of that asset URL
   (`https://web.archive.org/web/20250308000104id_/…`), which was captured 2025-03-08.

If you need the PDF again from a normal residential connection, the direct link works fine
in a browser: <https://chemrxiv.org/doi/10.26434/chemrxiv-2025-zhkrf>.

## Fidelity of the markdown recreation

`manuscript-v1.md` was transcribed from the PDF and has since been **verified against the
Word source** in [`submitted/`](submitted/): 97.8 % word-level agreement over the body
text, with every residual difference accounted for below. All section headings, the full
Table 1, all 32 references, author contributions, conflicts and funding acknowledgements
are present.

Deviations from the submitted source, all deliberate and all trivial:

| In the submitted source | In `manuscript-v1.md` |
|---|---|
| `Ethan Rajkumar2,5,,` | stray double comma removed |
| `Sonya Vasquez` (no affiliation superscript) | left unnumbered, flagged in the assessment |
| `enabling it's easy integration` | `its` |
| `automated experiments.This project` | space restored after the full stop |
| `less than $100USD` | `$100 USD` |
| `3d printing` | `3D printing` |
| Table 1: `Rolling Ball viscometer`, `Manuscript In progress`, `$30-$40K` | sentence case, en dash |

Text was additionally un-wrapped and de-hyphenated from the PDF extraction, and inline
citation markers were converted to `<sup>` tags.

One caveat the Word source does **not** settle: it was created 2025-02-04, nearly a month
after the 2025-01-09 rejection, so it establishes that the ChemRxiv PDF and the arXiv
submission carry the same text, not that either matches the December 2024 manuscript the
*Digital Discovery* editor read.

The v1 PDF presented the figures out of order (1, 2, **4**, **3**, 5, 6) as a Word float
artefact — confirmed in the Word source, where the Figure 4 caption precedes Figure 3.
**v2 renumbers them into citation order and the files were renamed to match**, so
`figures/` no longer corresponds to v1's numbering — read `manuscript-v1.md` for the
original placement.

## Figures

Figures 2–7 and 9 were re-extracted from the Word source at roughly twice the linear
resolution of the earlier PDF extractions. Figures 4 and 8 are new: neither project had a
figure in v1, and both were recovered from material the contributors had already
submitted. Both are marked `[NEEDED — confirm figure]` in the manuscript, because neither
was approved for publication.

| Figure | File | Source |
|---|---|---|
| 1 | `fig1-labour-vs-bom.png` | generated by `analysis/labor_cost_analysis.py` |
| 2 | `fig2-powder-dispensing-module.png` | Word source, 2048 × 1455 |
| 3 | `fig3-ledbyxample-photoreactor.png` | Word source, 2048 × 1203 |
| **4** | `fig4-rolling-ball-viscometer.jpg` | **new** — DTU slide deck, slide 4, 1532 × 2048 |
| 5 | `fig5-color-mixing-bot.jpg` | DTU slide deck, 3302 × 2476 (beats the Word copy's 2500 × 1874) |
| 6 | `fig6-disco.png` | Word source, 2048 × 579 |
| 7 | `fig7-science-jubilee.png` | Word source, 2048 × 1012 |
| **8** | `fig8-electrochemical-workflow.png` | **new** — original Google Form figure set; logo strip cropped and a spell-check underline removed for v3 (1842 × 652). Original in `figures/source/` |
| 9 | `fig9-ivoryos.png` | downscaled from the 16039 × 6235 TIFF in `figures/source/` |

`figures/source/` holds what is not used: the IvoryOS TIFF at full size, the DTU slide
deck, an unannotated photograph of the LEDbyXample photoreactor, and CAD renders of the
viscometer and powder dispensing module. A 26 MB file in the shared Drive folder was not
committed.

## Reproducing the analysis

```
cd analysis && python labor_cost_analysis.py
```

Requires `matplotlib`. Reads nothing but the figures already published in v1's Table 1 —
no new data — and rewrites `table1-derived.csv`, `sensitivity.csv` and
`../figures/fig1-labour-vs-bom.png`.

## Status

**v3 is the submission text (2026-10-10).** Sterling G. Baird owns the revision and is
corresponding author; Seth Leavitt, who coordinated v2, is kept as an author. Everything an
agent can resolve has been resolved. What remains is in
[`sign-off-checklist.md`](sign-off-checklist.md), led by the one item writing cannot fix:
work-in-progress repositories for the powder dispensing module and rolling ball viscometer
(DTU) and the electrochemical workflow (P7 team). The editor said he would accept
"work in progress" repositories, so the bar is low.

Check the manuscript after any edit:

```
python tools/check_manuscript.py manuscript-v3.md             # lint and report open items
python tools/check_manuscript.py manuscript-v3.md --renumber  # after adding a reference
```
