# Democratizing self-driving labs through user-developed automation infrastructure

Working directory for the revision and resubmission of the Accelerate 2024 "Democratizing
Self-Driving Labs" workshop Perspective. Tracked in
[issue #188](https://github.com/vertical-cloud-lab/byu-vcl/issues/188).

## Contents

| File | What it is |
|---|---|
| [`manuscript-v1.md`](manuscript-v1.md) | Editable markdown recreation of the ChemRxiv v1 text — **the working source**, since the original Google Doc is gone |
| [`chemrxiv-2025-zhkrf.pdf`](chemrxiv-2025-zhkrf.pdf) | The ChemRxiv v1 PDF as posted (18 pp.) |
| [`figures/`](figures/) | The six figures, extracted from the PDF at their embedded resolution |
| [`revision-assessment.md`](revision-assessment.md) | Initial assessment against the editor's rejection points, plus a proposed restructure |

## Provenance

- **DOI:** [10.26434/chemrxiv-2025-zhkrf](https://doi.org/10.26434/chemrxiv-2025-zhkrf)
- **Posted:** 2025-02-12 · **PDF generated:** 2025-02-10 (Microsoft Word for Microsoft 365)
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

`manuscript-v1.md` is a faithful transcription of the v1 text: all section headings, the
full Table 1, all 32 references, author contributions, conflicts, and funding
acknowledgements. Text was un-wrapped and de-hyphenated from the PDF extraction, and
inline citation markers were converted to `<sup>` tags. Two typographic slips in the
original author list (Ethan Rajkumar's stray double comma; Sonya Vasquez's missing
affiliation superscript) were normalised here — both are flagged in the assessment as
things to fix properly.

Figures were extracted at embedded resolution and renamed by figure number. Note that the
v1 PDF presents them out of order (1, 2, **4**, **3**, 5, 6) as a Word float artefact; the
markdown places each figure with its own project section, so the numbering reads out of
order there too. Renumbering is deferred until the restructure settles. The rolling ball
viscometer has no figure in v1.

## Status

Not yet revised. See [`revision-assessment.md`](revision-assessment.md) for the plan; the
blocking item is electronic supporting material (repos or Zenodo deposits) for the powder
dispensing module, the rolling ball viscometer, and the electrochemical workflow.
