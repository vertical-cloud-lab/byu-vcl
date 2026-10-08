# BO Hackathon manuscript: revised submission files

Digital Discovery manuscript DD-ART-06-2026-000353, *Bayesian Optimization Hackathon for
Chemistry and Materials*. The manuscript work lives in
[AC-BO-Hackathon PR #171](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/pull/171);
the file list was assembled in [#185](https://github.com/vertical-cloud-lab/byu-vcl/issues/185).
Links are pinned to that PR's head, `8321260`.

## Upload set

| File | Suggested designation | Compared with the original submission |
| --- | --- | --- |
| [`RESPONSE_TO_REVIEWERS.pdf`](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/RESPONSE_TO_REVIEWERS.pdf) | Response to Referees | replaces the letter to referees |
| [`copilot-main-fixed.pdf`](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/copilot-main-fixed.pdf) | Main Article | replaces `BO_Hackathon_Manuscript_Final.pdf` |
| [`copilot-main-diff.pdf`](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/copilot-main-diff.pdf) | Revised manuscript with changes marked | new |
| [`BO_Hackathon_Manuscript_Revised_LaTeX_source.zip`](BO_Hackathon_Manuscript_Revised_LaTeX_source.zip) | Source files | new |
| Figures [1](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/latex/figures/intro-bo.png), [2](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/latex/figures/world_map_readable.png), [3](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/latex/figures/preparation_blurred.png), [4](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/latex/figures/gathertown_redacted.png), [5](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/latex/figures/posters_redacted.png) | Figure | new; Digital Discovery asks for separate high-resolution figures at revision |
| Original ESI with [`esi_classification.pdf`](https://github.com/AC-BO-Hackathon/ac-bo-hackathon.github.io/raw/8321260/latex/esi_classification.pdf) appended | Supplementary Information | updated; the Table IV caption points at this page |
| `Author_Contributions_CRediT.pdf` without Jiale Shi and Dandan Tang | Other | updated; its source is not in either repository |
| `Data_Availability_Statement.docx` | Data Availability Statement | unchanged; the manuscript's statement is identical to the submitted one |
| `TOC_entry.pdf` | Table of Contents Entry | unchanged; the graphic has not changed since before submission |

The portal's own author list also still carries the two removed authors, and the change
needs to reach the editor separately from the files.

## How the source zip was built

- `git archive 8321260` of the AC-BO-Hackathon repository.
- The two `\input{|python3 ...}` pipes in `main.tex` (Table III and the project summaries)
  were replaced with the scripts' output, the same flattening `scripts/make_latexdiff.sh`
  does. The zip therefore needs no shell-escape, CSV, or Python.
- Only files the build reads are included: `main.tex`, `main.bbl`,
  `latex/authors-hardcoded.tex`, `latex/glossary.tex`, `latex/references.bib`,
  `latex/summaries-ref.bib`, and the five figures. `latex/authors.tex` (unused; it is the
  2023 LLM hackathon paper's author list) and `edison_output/` are left out.
- Three bibliography entries had `language = {en}`, which `apsrev4-2` turns into
  `\selectlanguage{en}`, a language babel does not know. They read `{english}` in the zip.
  The output is unchanged; the build just no longer exits with an error.

Checked by unpacking the zip into an empty directory and running `pdflatex` without
shell-escape: 0 errors, 0 unresolved references or citations, 24 pages. The text matches
`copilot-main-fixed.pdf` word for word. About 20 line-end hyphenations on pages 9 to 16
differ, and the unmodified `.bib` gives the same result, so that comes from the TeX
installation rather than the source.
