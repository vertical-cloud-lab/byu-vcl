# Reference check: docs/manuscripts/democratizing-sdl/manuscript-v2.md (34 refs)

Checked on 2026-10-10. All 28 DOIs resolve in the Crossref REST API. Where Crossref was incomplete, PubMed, OpenAlex and bioRxiv were used to cross-check. For every DOI reference I compared:
- every author surname and its initials, in order (by a script)
- the title (case-insensitive, with capitals on proper nouns checked by eye)
- journal, year, volume, issue, and pages or article number

## 1. Status of each reference

| # | Status | Details |
|---|---|---|
| 1 | OK | 13/13 authors |
| 2 | OK | |
| 3 | OK | 43/43 authors in order; diacritics correct (Wołos) |
| 4 | OK | |
| 5 | OK | 17/17 authors |
| **6** | **Title mismatch + Author Correction** | Crossref and nature.com now give the title as "An autonomous laboratory for the accelerated synthesis of **inorganic** materials". The manuscript has the original 2023 title, "…of **Novel** Materials", which PubMed still shows. The title was changed by an Author Correction: *Nature* **2026**, *650* (8100), E1, doi:10.1038/s41586-025-09992-y (online 2026-01-19). The correction drops the claim that the materials were novel (now "new to the prediction platform, not necessarily new to science"). It also re-counts the successes as 36 of 40, with 4 inconclusive, and removes Zn2Cr3FeO8. Authors, volume and pages are correct. Ref 6 is cited only once (L47, as an example of commercial automation infrastructure), which does not depend on the novelty claim. Fix: update the title and append the correction (corrected entry below). |
| 7 | OK | |
| 8 | OK | "Ng Wei Tat, L." matches Crossref and the publisher's byline |
| 9 | no DOI | See §4 |
| 10 | no DOI | See §4 |
| 11 | OK | |
| 12 | no DOI | See §4 |
| **13** | **no DOI; edition superseded** | See §4 |
| 14 | OK | |
| 15 | OK | |
| 16 | OK | |
| 17 | OK | Optional: the publisher italicises *via* in the title (RSC house style) |
| 18–20 | OK | |
| 21 | OK (intentional) | Crossref lists the first author as "Vasquez, Joshua". "Vasquez, S." is intentional (the author list has Sonya Vasquez). Leave it. |
| 23 | OK (same intentional name) | The 5th author is "Vasquez, Joshua" in Crossref. The manuscript's "Vasquez, S." is the same person and the same choice as ref 21, so the two are consistent. |
| 22, 24, 25 | OK | |
| 26 | OK (Crossref metadata error) | Crossref and PubMed both split author 13 as surname "Jieh Lim", given name "Zhen". The bioRxiv preprint (10.1101/861856) has "Lim, Zhen Jieh", so the manuscript's "Lim, Z. J." is correct. Crossref gives only the first page (2447); PubMed confirms 2447–2460. |
| 27 | OK; page range unverified | Crossref has no page data, and PubMed, PMC, OpenAlex and Semantic Scholar give only "Unit 14.20". I could not confirm "14.20.1–14.20.17": Wiley returns 403 to automated requests. All other fields are correct, and the µ character is the same as in Crossref. |
| 28–30 | OK | |
| 31 | OK | Diacritic correct (Pablo-García) |
| 32 | OK | 17/17 authors |
| 33, 34 | no DOI | See §4 |

Style notes only, not errors:
- The same person appears with different initials in different refs, each matching its own Crossref record: Prieto "P. L." (ref 4) vs "P." (ref 32), and Kumar "R. E." (ref 6) vs "R." (ref 30).
- Ref 22's "PLOS ONE" is the name Crossref uses; the CASSI abbreviation is "PLoS One". Whichever form you choose, use the same one for candidate (c).

Corrected ref 6, ready to paste:

6. Szymanski, N. J.; Rendy, B.; Fei, Y.; Kumar, R. E.; He, T.; Milsted, D.; McDermott, M. J.; Gallant, M.; Cubuk, E. D.; Merchant, A.; Kim, H.; Jain, A.; Bartel, C. J.; Persson, K.; Zeng, Y.; Ceder, G. An Autonomous Laboratory for the Accelerated Synthesis of Inorganic Materials. *Nature* **2023**, *624* (7990), 86–91. https://doi.org/10.1038/s41586-023-06734-w. Author Correction: *Nature* **2026**, *650* (8100), E1. https://doi.org/10.1038/s41586-025-09992-y.

## 2. Errata, corrections and retractions

I checked four sources for all 28 DOIs:
- Crossref `updated-by`
- the Crossref `filter=updates:<DOI>` query
- a Crossref title search for "Correction / Erratum / Retraction: <title>"
- PubMed's correction links, for the 13 refs indexed there

**Only ref 6 has a notice** (the Author Correction above). There are no retractions or expressions of concern; Crossref includes Retraction Watch data in `updated-by`, and none appears. The `relation` fields hold only preprint and peer-review links.

## 3. Citation order

The body runs from L37 to L352 (Abstract up to References). I excluded the affiliation superscripts in the author block (L15) and the two `<sup>†</sup>` footnote markers (L104, L108).

First citation of each reference, by line:

| Line | First cited |
|---|---|
| L47 | 1–3, 4, 5, 6 |
| L49 | 7, 8 |
| L61 | 9 |
| L129 | 10 |
| L135 | 11, 12 |
| L141 | 13, 14 |
| L151 | 15, 16 |
| L157 | 17, 18, 19, 20 |
| L163 | 21, 22, 23 |
| L177 | 24 |
| L181 | 25, 26, 27 (in "3,25", ref 3 is a re-citation) |
| L183 | 28, 29, 30, 31, 32 |
| L323 | 33, 34 |

- **Numbering is strictly sequential from 1 to 34.** Every reference is cited, nothing points beyond 34, every citation group parses, and no citations sit inside tables or captions.
- Re-citations: ref 3 (L181), ref 7 (L75, L224), ref 8 (L75), ref 9 (L246).
- One thing to decide: the Table 1 footnote (L108) names the "accelerated-discovery.org Discourse forum" without citing ref 34. If you add a citation there, ref 34 becomes about #10 and every later reference has to be renumbered.

## 4. Non-DOI URLs (GET requests, redirects followed, 2026-10-10)

| Ref | URL as cited | HTTP | Final URL | Notes |
|---|---|---|---|---|
| 9 | https://www.oshwa.org/definition/ | 301 → 200 | https://oshwa.org/definition/ | Page still shows "Open Source Hardware (OSHW) Definition 1.0". The site now drops "www"; updating is optional. |
| 10 | https://github.com/eamars/OpenTrickler | 200 | same | Owner is Ran Bao, so "Bao, R." is correct. Not archived; GPL-3.0. The latest release at the 2024-12-14 access date was v1.4 (2024-05-10), so "2024" holds. It is now at v2.0.2 (2025-07-18). |
| 12 | https://pioreactor.com/ | 200 | same | Page title: "Pioreactor \| Accessible, open-source bioreactors" |
| 13 | https://www.astm.org/d1200-10r18.html | 307 → 200 (a HEAD request gets 403, which is bot-blocking) | https://store.astm.org/d1200-10r18.html | The page marks this edition **"Standard Historical"** |
| 33 | https://labautomation.io/ | 200 | same | Page title: "Lab Automation Forums" (matches) |
| 34 | https://accelerated-discovery.org/ | 200 | same | Page title: "Accelerated Discovery - AI and automation to accelerate materials discovery" (matches) |

**ASTM D1200-10(2018) has been superseded.** The active edition is **ASTM D1200-23**:
- approved 2023-06-01, record created 2023-06-15
- DOI 10.1520/D1200-23, 4 pages, ASTM marks it "Standard Active"

There is no -24 or -25 edition. ASTM's version list is -94(1999), -94(2005), -10, -10(2014), -10(2018), -23. The 2018 edition was therefore already historical on the cited access date (2024-12-11). Ref 13 is cited generically (L141, "timing drainage from a perforated cup"), so citing the current edition is the right fix:

13. ASTM International. *Standard Test Method for Viscosity by Ford Viscosity Cup*; ASTM D1200-23; ASTM International: West Conshohocken, PA, 2023. https://doi.org/10.1520/D1200-23.

## 5. Candidate new references (checked in Crossref)

(a) Pearce, J. M. Return on Investment for Open Source Scientific Hardware Development. *Sci. Public Policy* **2016**, *43* (2), 192–195. https://doi.org/10.1093/scipol/scv034.

- Crossref: published online 2015-06-20, in the April 2016 issue; volume 43, issue 2, pp 192–195.
- 2016 is the volume year, which is the ACS convention.
- No updates or corrections. The DOI resolves to academic.oup.com (the 403 there is OUP's bot-blocking).

(b) Bonvoisin, J.; Mies, R.; Boujut, J.-F.; Stark, R. What Is the "Source" of Open Source Hardware? *J. Open Hardw.* **2017**, *1* (1), 5. https://doi.org/10.5334/joh.7.

- DOI 10.5334/joh.7 is correct.
- Crossref authors: Jérémy Bonvoisin, Robert Mies, Jean-François Boujut, Rainer Stark. Published 2017-09-05; volume 1, issue 1, article number 5 (no page range).
- The published title has a lowercase "is"; "Is" above follows the list's title case.
- The journal has moved from Ubiquity Press to Western Libraries; the DOI resolves (200) to ojs.lib.uwo.ca.
- No updates or corrections.

(c) Maia Chagas, A. Haves and Have Nots Must Find a Better Way: The Case for Open Scientific Hardware. *PLOS Biol.* **2018**, *16* (9), e3000014. https://doi.org/10.1371/journal.pbio.3000014.

- Crossref: André Maia Chagas (surname "Maia Chagas"); published 2018-09-27; volume 16, issue 9, e3000014.
- `updated-by` shows only a "new version" entry (2018-10-09) pointing back to the article itself. That is PLOS's own versioning, not a correction, and the article page shows no correction notice.
- Write "PLoS Biol." instead if ref 22 is changed to "PLoS One".
