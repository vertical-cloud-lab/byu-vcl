# Reference check: docs/manuscripts/democratizing-sdl/manuscript-v3.md (45 refs)

Checked on 2026-11-27. The list has 39 DOI references and 6 web references. All 40 DOIs (the 39, plus the Author Correction appended to ref 6) resolve in the Crossref REST API and are registered at doi.org. Where Crossref was incomplete I cross-checked against PubMed, Europe PMC, OpenAlex and the publisher's own page. For every DOI reference I compared:
- every author surname and its initials, in order (by a script)
- the title (case-insensitive by script, with capitals on proper nouns and acronyms checked by eye)
- journal, year, volume, issue, and pages or article number

Numbers are v3's throughout. The 2026-10-10 check used v2's 34-reference numbering.

## What changed since 2026-10-10

- **New update notice: ref 10** (Pearce 2020, *HardwareX*) has a registered Erratum (2021). It is procedural and leaves the content unchanged. It was not recorded when the reference was added to v3. Details in §1 and §3.
- **Resolved: ref 31's page range** (µManager), "unverified" on 2026-10-10, is now confirmed as 14.20.1–14.20.17 from Wiley's own article metadata.
- **Confirmed: ref 6's Author Correction is cited correctly** (vol 650, issue 8100, p E1, 2026, 10.1038/s41586-025-09992-y).
- **No new corrections, retractions or expressions of concern** for any reference, and no Retraction Watch entries.
- **Both standards are still current.** ASTM D1200-23 is "Standard Active", and DIN SPEC 3105-1:2020-07 is "[CURRENT]". Neither has a newer edition, draft or successor.
- **All six web URLs return HTTP 200 with no redirects.**
- **The preprint's citation count is out of date in the cover letter.** It now has 10 verified citations, not six. All four venues the letter names are correct (§5).
- **No factual errors in the reference list, so no required edits to it.** The one required edit is the cover letter's count.

## 1. Status of each reference

| # | DOI | Status | Details / exact fix |
|---|---|---|---|
| 1 | 10.1016/j.xcrp.2023.101411 | OK | 13/13 authors. Crossref stores two given names unspaced ("Fraser G.L.", "Chris E.B."), so "F. G. L." and "C. E. B." are right. |
| 2 | 10.1038/s44286-024-00033-5 | OK | 6/6 |
| 3 | 10.1126/science.adk9227 | OK | 43/43 authors in order; diacritics correct (Wołos) |
| 4 | 10.1039/D1SC04588A | OK | 8/8 |
| 5 | 10.1039/D3DD00142C | OK | 17/17 |
| 6 | 10.1038/s41586-023-06734-w | OK; update notice already cited | 16/16 authors, and the title is the corrected one. The appended correction matches Crossref exactly: title "Author Correction: An autonomous laboratory for the accelerated synthesis of inorganic materials", *Nature* volume "650", issue "8100", page "E1-E1", online 2026-01-19, print issue 2026-02-05, `update-to` type "correction". PubMed agrees: ErratumIn "Nature. 2026 Feb;650(8100):E1. doi: 10.1038/s41586-025-09992-y." No further notices since. Nothing to change. |
| 7 | 10.1039/D3DD00223C | OK | 13/13 |
| 8 | 10.1039/D4DD00411F | OK | 8/8; "Ng Wei Tat, L." matches Crossref |
| 9 | 10.1371/journal.pbio.3000014 | OK | 1/1. `updated-by` holds only a PLOS "new_version" entry (2018-10-09) that points back to the article itself, not a correction (as on 2026-10-10). A new `is-reply-to` relation links it to an Access 2 Perspectives interview (10.21428/51e64700.b528ba98). That is a third-party link, not a notice. |
| **10** | 10.1016/j.ohx.2020.e00139 | **Update notice (new)** | Crossref `updated-by` type "erratum" (2021-10-01) → 10.1016/j.ohx.2021.e00235, "Erratum regarding previously published articles", *HardwareX* volume "10", e00235. PubMed: ErratumIn "HardwareX. 2021 Sep 22;10:e00235". It covers 12 *HardwareX* articles at once and only adds a footnote that had been left out: "given his role as Co-Editor in Chief, Prof Joshua Pearce had no involvement in the peer-review process … Full responsibility for the editorial process for these articles was delegated to Prof Todd Duncombe." The text, data and savings figures are unchanged, and every bibliographic field of ref 10 is correct. **No change required**; appending the erratum is optional (text in §2). |
| 11 | — (web) | OK | §4 |
| 12 | 10.1093/scipol/scv034 | OK | Online 2015-06-20, April 2016 issue; 2016 is the volume year |
| 13 | 10.5334/joh.7 | OK | 4/4; volume 1, issue 1, article number 5, 2017 |
| 14 | — (web) | OK; optional version pin | §4, and option (b) in §2 |
| 15 | 10.1021/acs.orglett.1c01910 | OK | 3/3; title identical to Crossref |
| 16 | — (web) | OK | §4 |
| 17 | 10.1520/D1200-23 | OK; current edition | Crossref: title "Test Method for Viscosity by Ford Viscosity Cup" (ASTM's DOI records drop "Standard"), author "D01 Committee", publisher-location "West Conshohocken, PA". See §3. |
| 18 | 10.1039/D2DD00126H | OK | 6/6 |
| 19 | 10.1145/3624062.3624615 | OK | 10/10 authors. The container title, "ACM", "New York, NY, USA" and pages "2147-2152" all match. |
| 20 | 10.1016/j.xpro.2023.102329 | OK | 2/2 |
| 21 | 10.1039/D4DD00249K | OK | 9/9. Optional: the publisher italicises *via* (RSC house style), as on 2026-10-10. |
| 22–24 | see list | OK | 7/7, 5/5, 4/4 |
| 25 | 10.1145/3313831.3376425 | OK (intentional) | 4/4; pages "1-13". Crossref still lists the first author as "Vasquez, Joshua". "Vasquez, S." is intentional, as decided on 2026-10-10. Leave it. |
| 26 | 10.1371/journal.pone.0296717 | OK | 4/4 (abbreviation style note below) |
| 27 | 10.1039/D3DD00033H | OK (intentional) | 9/9. Author 5 is "Vasquez, Joshua" in Crossref. Same intentional choice as ref 25. |
| 28, 29 | see list | OK | 5/5, 9/9 |
| 30 | 10.1364/BOE.385729 | OK (Crossref metadata error) | 18/18. Crossref still splits author 13 as family "Jieh Lim", given "Zhen", but the bioRxiv preprint (10.1101/861856) has "Lim, Zhen Jieh". Crossref gives only "2447"; PubMed's MedlinePgn "2447-2460" confirms the range. |
| 31 | 10.1002/0471142727.mb1420s92 | OK; **page range now confirmed** | 5/5. Crossref has no pages, and PubMed, Europe PMC and OpenAlex give only "Unit14.20". Wiley's own article page (Wayback snapshot of 2025-07-11) carries `citation_firstpage` "14.20.1", `citation_lastpage` "14.20.17", volume "92", issue "1". The µ is U+00B5 in the manuscript, Crossref and Wiley alike. |
| 32–36 | see list | OK | 5/5, 4/4, 13/13, 8/8 (Pablo-García correct), 17/17 |
| 37 | 10.1017/pds.2021.443 | OK | 5/5. Crossref's title is in capitals ("IDENTIFYING THE FACTORS AFFECTING THE REPLICABILITY OF OPEN SOURCE HARDWARE DESIGNS"); the manuscript's title case is right. |
| 38 | 10.1016/j.procir.2025.08.035 | OK | 3/3. Crossref and OpenAlex give the title as "Howling for a New Standard -Deficits in Open Source Hardware Documentation", with a stray hyphen. The manuscript's spaced en dash only changes punctuation, not wording. ScienceDirect returns 403 to automated requests, so I could not see how the title is printed. |
| 39 | 10.1039/D4DD90009J | OK; not superseded | 2/2. *Digital Discovery* has published no newer hardware-guidelines editorial (Crossref search, June 2024 onward). |
| 40 | — (web) | OK | §4 |
| 41 | 10.1039/D4DD90053G | OK | 3/3 |
| 42 | 10.1039/D5DD00336A | OK | 8/8. This article itself cites the preprint (§5). |
| 43 | 10.31030/3173063 | OK; current edition | Crossref title "DIN SPEC 3105-1:2020-07, Open Source Hardware_- Teil_1: Anforderungen an die technische Dokumentation; Text Englisch", publisher "DIN Media GmbH", Berlin, which the manuscript matches. DIN Media's English title: "Open Source Hardware - Teil 1: Requirements for technical documentation; Text in English". See §3. |
| 44, 45 | — (web) | OK | §4 |

Style notes only, not errors:
- The *PLoS* abbreviations are still mixed: "PLoS Biol." (ref 9) but "PLOS ONE" (ref 26). The CASSI forms are "PLoS Biol." and "PLoS One". This was flagged on 2026-10-10 and v3 kept both; an optional fix is in §2.
- The same person appears with different initials, each matching its own Crossref record: Prieto "P. L." (ref 4) vs "P." (ref 36), and Kumar "R. E." (ref 6) vs "R." (ref 34).

## 2. Edits

**Required in the reference list: none.** Every field of every reference agrees with Crossref or, where Crossref is incomplete, with PubMed or the publisher's page. The only differences from Crossref are its three known metadata quirks (refs 25/27, 30 and 31), and the manuscript already handles each of them correctly.

**Required outside the reference list: one.** In `cover-letter.md` line 25 (line 31 before the letter was edited earlier today), "six times" is out of date. Replacement text is in §5.

**Optional, ready to paste:**

(a) Ref 10 with its erratum appended, parallel to ref 6. The erratum is procedural, so this is a judgement call:

10. Pearce, J. M. Economic Savings for Scientific Free and Open Source Technology: A Review. *HardwareX* **2020**, *8*, e00139. https://doi.org/10.1016/j.ohx.2020.e00139. Erratum: *HardwareX* **2021**, *10*, e00235. https://doi.org/10.1016/j.ohx.2021.e00235.

(b) Ref 14, naming the release that was current in 2024. The sentence (L153) describes OpenTrickler as the P1 developers found it, so "2024" is right. But the cited access date now postdates the v2.0 releases (v2.0, 2025-07-12, through v2.0.2, 2025-07-18), so naming the release removes the ambiguity:

14. Bao, R. eamars/OpenTrickler, v1.4, 2024. https://github.com/eamars/OpenTrickler/releases/tag/v1.4 (accessed 2026-11-27).

(c) Ref 26 in the same abbreviation style as ref 9:

26. Subbaraman, B.; de Lange, O.; Ferguson, S.; Peek, N. The Duckbot: A System for Automated Imaging and Manipulation of Duckweed. *PLoS One* **2024**, *19* (1), e0296717. https://doi.org/10.1371/journal.pone.0296717.

(d) Access dates. All six web references were re-checked today and are unchanged, so "(accessed 2026-10-10)" can become "(accessed 2026-11-27)" in refs 11, 14, 16, 40, 44 and 45.

## 3. Errata, corrections, retractions and superseded works

I checked six sources for all 40 DOIs:
- Crossref `updated-by`, `update-to` and `relation`
- the Crossref `filter=updates:<DOI>` query
- Crossref Labs `cr-labs-updates`, which carries Retraction Watch data. Crossref's own `updated-by` would also show Retraction Watch entries, as `source: retraction-watch`.
- a Crossref search for "correction / erratum / retraction <title>" (117 queries)
- PubMed CommentsCorrections, for the 16 DOIs indexed there
- OpenAlex `is_retracted`

**Two notices, and no others.**
- **Ref 6:** the Author Correction, already cited.
- **Ref 10:** the procedural *HardwareX* erratum (new to this check).

There are no retractions, expressions of concern, withdrawals or Retraction Watch entries, and `is_retracted` is false for all 40 DOIs. The title searches turned up only two false positives, both different articles with similar titles:
- "Correction: Towards a Modular Architecture for Intelligent Aerial Manipulator Systems" (10.2514/6.2018-1631.c1), against ref 5
- "Correction: Open Source Hardware and Healthcare Collaborative Platforms: Common Legal Challenges" (10.5334/joh.37), against ref 13

Otherwise the `relation` fields hold only has-preprint, has-review and has-part links (refs 3, 7, 8, 20–22, 26–30, 35, 36), plus the ref 9 link above.

**Superseded works: none.**
- **Ref 17, ASTM D1200-23: current.**
  - The ASTM store page says "Standard Active", "Last Updated: Jun 15, 2023", and `store.astm.org/d1200.html` redirects to `d1200-23.html`.
  - Crossref lists the editions -94r99, -94r05, an undated record, -10, -10r14, -10r18 and -23. Lookups for -24, -25, -26, -23R24 and -23R25 all return 404.
  - ASTM reviews standards every five years, so the next action on D1200 is due around 2028.
- **Ref 43, DIN SPEC 3105-1:2020-07: current.**
  - DIN Media's page reads "Technical rule [CURRENT]" (German page: "[AKTUELL]"), publication date 2020-07, 13 pages, procedure PAS.
  - Crossref holds only the 2020-07 DOIs, for Part 1 (10.31030/3173063) and Part 2 (10.31030/3173062).
  - DIN Media, Crossref prefix 10.31030 and two web searches show no draft, successor or newer edition. An older din.de record (313396436), which search engines still list, now returns 404.
  - OSEG's GitLab working copy could not be checked (GitLab returned HTTP 429).
- **Ref 39:** no newer *Digital Discovery* guidelines for hardware articles.
- **Preprints:** the list cites none (no arXiv, ChemRxiv, bioRxiv or Research Square DOIs), so none can have been published since. The four formerly-preprint references (refs 21, 23, 30, 36) are already cited as their published versions.

## 4. Non-DOI URLs (GET and HEAD requests, redirects followed, 2026-11-27)

| Ref | URL as cited | HTTP | Final URL | Notes |
|---|---|---|---|---|
| 11 | https://oshwa.org/definition/ | 200 | same | Page title "Definition \| OSHWA". It still shows "Open Source Hardware (OSHW) Definition 1.0". |
| 14 | https://github.com/eamars/OpenTrickler | 200 | same | Owner is Ran Bao, so "Bao, R." is correct. Not archived, GPL-3.0, last push 2026-11-19. Latest release is still v2.0.2 (2025-07-18), so nothing new since 2026-10-10. v1.4 dates from 2024-05-10. |
| 16 | https://pioreactor.com/ | 200 | same | Page title "Pioreactor \| Accessible, open-source bioreactors" |
| 40 | https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/digital-discovery | 200 | same | Page title "Author guidelines for Digital Discovery". It still says "Papers that describe hardware must include detailed supporting information, including a comprehensive bill of materials and a construction guide", which is what §6 relies on. |
| 44 | https://labautomation.io/ | 200 | same | Page title "Lab Automation Forums" (matches) |
| 45 | https://accelerated-discovery.org/ | 200 | same | Page title "Accelerated Discovery - AI and automation to accelerate materials discovery" (matches) |

All six give the same result with a tool User-Agent and with a browser User-Agent. Because OSHWA is now cited without `www.`, its earlier 301 is gone.

## 5. Citations of the preprint (10.26434/chemrxiv-2025-zhkrf, posted 2025-02-12)

| Source | Count | Notes |
|---|---|---|
| OpenAlex (W4407556581) `cited_by_count` | 12 | 4 in 2025, 8 in 2026. Two of the 12 do not hold up; see below the table. |
| Crossref `is-referenced-by-count` | 7 | Counts only references deposited with this DOI. Rows 1–4, 6, 8 and 10 below. |
| OpenCitations (index v2) | 4 | Lags; rows 1–4 only |
| Semantic Scholar | — | The preprint is not indexed: DOI lookup 404, title match 404. The search endpoint returned 429 on 8 attempts. |
| **Verified here** | **10** | The citing work's own reference list, as deposited in Crossref, contains the preprint |

Verified citing works:

| # | Citing work | Venue, year, vol (issue), pages | DOI | How verified | Shares an author with this paper? |
|---|---|---|---|---|---|
| 1 | Pelkie, B. *et al.* Accelerated sol–gel synthesis of nanoporous silica via integrated small angle X-ray scattering with an open-source automation platform | *Digit. Discov.* 2025, 4 (10), 3018–3030 | 10.1039/D5DD00274E | ref cit31, DOI | Yes: Pelkie, Pozzo |
| 2 | Cooper, A. I. *et al.* (23 authors). Accelerating discovery in natural science laboratories with AI and robotics: Perspectives and challenges | *Sci. Robot.* 2025, 10 (106), eadv7932 | 10.1126/scirobotics.adv7932 | ref e_1_3_1_15_2, DOI (matched by Crossref) | Yes: Hein (1 of 23) |
| 3 | Darvish, K. *et al.* (23). MATTERIX: toward a digital twin for robotics-assisted chemistry laboratory automation | *Nat. Comput. Sci.* 2026 (online 2025-12-31), 6 (1), 67–82 | 10.1038/s43588-025-00924-4 | ref 924_CR10, DOI | No |
| 4 | Yoshikawa, N. *et al.* (8). Commit: Digital pipette: open hardware for liquid transfer in self-driving laboratories (this is ref 42) | *Digit. Discov.* 2026, 5 (1), 93–97 | 10.1039/D5DD00336A | ref cit9, DOI | No. Ilya Yakavets is an author, so it becomes a self-citation if P7-3 adds him. |
| 5 | Benstead, C.; Politi, M.; Bergsman, D. S.; Pozzo, L. D. An automated sampling workflow for parallel long-term membrane diffusion cell testing | *Digit. Discov.* 2026, 5 (3), 1312–1324 | 10.1039/D5DD00523J | ref cit10, citation text (no DOI) | Yes: Politi, Pozzo |
| 6 | Pokhrel, P.; Kordijazi, A. Self-driving manufacturing labs: A conceptual framework and implementation case studies | *Proc. Inst. Mech. Eng., Part B* 2026, online first 2026-05-04 (no volume yet) | 10.1177/09544054261444844 | Crossref matched the DOI. The printed reference wrongly reads "Dig Discov 2025; 2(6): 1980–1998". | No |
| 7 | Maroulis, A. P. *et al.* (8). A user's guide to your first self-driving liquid handling lab | *Digit. Discov.* 2026, 5 (5), 2028–2041 | 10.1039/D5DD00525F | ref cit24, ChemRxiv URL | No |
| 8 | Lee, H. *et al.* (6). Toward self-driving laboratory 2.0 for chemistry and materials discovery | *Mater. Horiz.* 2026, 13 (10), 4712–4739 | 10.1039/D5MH01984B | ref cit202, DOI | No |
| 9 | Soni, A.; Jia, S.; Chao, C.; Abate, I. I. Accelerated development of energy materials through automation and artificial intelligence | *The Innovation* 2026 (July), 101509 | 10.1016/j.xinn.2026.101509 | ref bib182, title | No |
| 10 | Subbaraman, B. Building Automation for Insight | Adjunct Proc. 39th ACM UIST, 2026, pp 1–5 | 10.1145/3830397.3841702 | DOI | Yes: Subbaraman |

Listed by OpenAlex but not counted:
- **Anker, A. S. *et al.*** Autonomous Synthesis of Nanoparticles with Target Scattering Patterns. *ACS Nano* 2026, 20 (8), 6767–6782, 10.1021/acsnano.5c15488.
  - The published article does not cite the preprint. None of its 92 references does, in the Crossref deposit or in PMC12961950. It cites row 1 (Pelkie *et al.* 2025) instead.
  - The citation appears only in its arXiv v1 (2505.13571, 2025-05-19, "Autonomous nanoparticle synthesis by design", ref. 64), which OpenAlex merged into the journal record. That version shares an author with this paper (Vegge).
- **Böser, A.; Bräse, S.** BrickSDLab: A low-cost self-driving lab platform made from LEGO® bricks for rapid prototyping and education. ChemRxiv, posted 2025-10-21, 10.26434/chemrxiv-2025-lb8jt.
  - Unverifiable: ChemRxiv deposits no references in Crossref and returns 403 to automated requests, and there is no Wayback copy (the Wayback CDX API was offline).
  - Plausible, given the topic. If real, it is an independent citation from a preprint, not a journal.

**Verdict on the cover letter** ("cited six times while under revision, including in *Science Robotics*, *Nature Computational Science*, *Materials Horizons* and this journal"):
- **Venues: correct.** Each is verified, and *Digital Discovery* accounts for four of the citing articles (rows 1, 4, 5, 7).
- **Count: out of date.** There are now ten verified citations: nine journal articles and one ACM conference paper, all after the preprint was posted. Four share at least one author with this paper (rows 1, 2, 5, 10). Six are fully independent, including *Nature Computational Science*, *Materials Horizons* and two of the four *Digital Discovery* papers.

Replacement for the first sentence at `cover-letter.md` line 25:

> The preprint of the original version has been cited ten times while under revision, including in *Science Robotics*, *Nature Computational Science*, *Materials Horizons* and, four times, this journal.

Or, to pre-empt a question about self-citation:

> The preprint of the original version has been cited ten times while under revision, in venues including *Science Robotics*, *Nature Computational Science*, *Materials Horizons* and this journal; six of the citing papers share no author with this one.

Re-count just before sending: OpenAlex already has eight 2026 citations.

## 6. Related 2025–2026 papers in *Digital Discovery* (for awareness only)

Found by Crossref searches of *Digital Discovery* (ISSN 2635-098X) from 2025-01-01 on. None of these is cited in v3, and I did not check them against the text:

1. Maroulis, A. P.; Waynor, D. M.; Gallagher, Q. M.; Patel, R. A.; Tamasi, M.; Radford, D. C.; Webb, M. A.; Gormley, A. J. A User's Guide to Your First Self-Driving Liquid Handling Lab. *Digit. Discov.* **2026**, *5* (5), 2028–2041. https://doi.org/10.1039/D5DD00525F.
   - Why it matters: a foundation-level guide to building and running low-cost open-source liquid handlers, framed as democratization and citing the preprint. It is the closest published example of the configure/run documentation §6 calls for.
2. Baas, S.; Carson, N.; Saggiomo, V. Hacking 3D Printers as Laboratory Robots. *Digit. Discov.* **2026**, *5* (4), 1460–1469. https://doi.org/10.1039/D5DD00451A.
   - Why it matters: a review of 3D printers repurposed as laboratory robots, the low-cost-hardware strand that refs 8 and 21 belong to.
3. Quijano Velasco, P.; Leong, C. J.; Koay, E. H. H.; Hippalgaonkar, K.; Cheng, J. J. W. Qubots: Open-Source Modular Laboratory Robots as Building Blocks for Flexible Assembly of Self-Driving Labs. *Digit. Discov.* **2026**, *5* (10), 4315–4328. https://doi.org/10.1039/D6DD00280C.
   - Why it matters: open-source modular robots that claim reduced cost and engineering effort, a comparator for science-jubilee (P6) and DiSCO (P5).
4. Greenwood, R.; Lai, V.; Zhang, W.; Lindenberg, E.; Hein, J. E. An In Silico Tool for Rapid and Accessible Training in Self-Driving Laboratory Development. *Digit. Discov.* **2026**, *5* (11), 5013–5018. https://doi.org/10.1039/D6DD00557H.
   - Why it matters: training for SDL skills, which is Claim 4's territory. Two of its authors (W. Zhang, J. E. Hein) are on this paper.
5. Zhang, T.; Lin, H.; Chen, Y.; Viswanathan, V. SALSA: A Low-Cost Self-Driving Lab Modular Add-On for Salt Solubility Assessment for Battery Electrolytes. *Digit. Discov.* **2026**, *5* (4), 1881–1887. https://doi.org/10.1039/D5DD00516G.
   - Why it matters: a low-cost SDL module built around a 3D-printed Archimedes-screw solid doser, a direct comparator for P1 (powder dispensing).

## 7. Audit trail

Queried 2026-11-27, roughly 19:00–19:30 UTC. API calls used the User-Agent `ref-check/1.0 (mailto:noreply@example.org)`. A browser User-Agent was used only for the ASTM and DIN pages and for the second pass of URL checks.

- **Crossref REST API**
  - `/works/{doi}` for all 40 DOIs, plus the *HardwareX* erratum, the Access 2 Perspectives record, the preprint, the 12 OpenAlex citing works and the §6 papers.
  - `/works?filter=updates:{doi}` for all 40 DOIs (several retried after HTTP 429).
  - `/works?query.bibliographic=` correction / erratum / retraction + title (117 queries).
  - `/prefixes/10.1520/works` and `/prefixes/10.31030/works` searches, and lookups of ASTM D1200 edition DOIs.
  - `/works?filter=issn:2635-098X,from-pub-date:…` searches for §3 and §6.
- **Crossref Labs:** `/works/{doi}` for all 40 DOIs (`cr-labs-updates`).
- **doi.org Handle API:** `/api/handles/{doi}` for all 40 DOIs; every one returned responseCode 1.
- **NCBI E-utilities:** `esearch` by `[AID]` for all 40 DOIs, and one `efetch` for the 16 PMIDs found (CommentsCorrections, MedlinePgn).
- **Europe PMC**
  - search: the erratum, PMID 20890901, and both preprints (neither indexed)
  - full text: PMC9123478 (the erratum's text) and PMC12961950 (*ACS Nano* references)
- **OpenAlex**
  - the preprint record and `filter=cites:W4407556581`
  - `filter=doi:` for all 40 DOIs (`is_retracted`)
  - records for the *ACS Nano* paper, BrickSDLab, µManager and ref 38
- **OpenCitations index v2:** `/citations` and `/citation-count` for the preprint.
- **Semantic Scholar Graph API:** DOI lookup (404), `search/match` (404), `search` (429).
- **arXiv:** export API for 2505.13571 (one version only), and the v1 PDF, text extracted with `pdftotext`.
- **Internet Archive:** availability API; snapshot `20250711150815` of the Wiley µManager page; CDX API (offline at the time).
- **Publisher and standards pages**
  - `store.astm.org/d1200-23.html`, `store.astm.org/d1200.html`, and `doi.org/10.1520/D1200-23`
  - `dinmedia.de` record 324805763 (English and German), `din.de` record 313396436 (404), and `doi.org/10.31030/3173063`
- **GitHub REST API:** `repos/eamars/OpenTrickler`, its releases, and `users/eamars`.
- **Web search:** two queries for DIN SPEC 3105 revisions or successors.
- **Not reachable or not used:**
  - ChemRxiv, ScienceDirect and live Wiley pages (403)
  - GitLab API (429)
  - Google Scholar (not queried)

`manuscript-v3.md` was edited elsewhere during this check, at 19:27 UTC. Re-parsing the reference list afterwards showed all 45 entries unchanged, and `tools/check_manuscript.py`, in report-only mode, reports 45 references, all 45 cited.
