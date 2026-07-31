# The BYU TTO technology catalog

A complete harvest of [`techtransfer.byu.edu/search`](https://techtransfer.byu.edu/search) — BYU's public listing of
technologies available for license — together with the TTO's own process documents and standard
agreement templates.

Companion to [`byu-vc-founder-rules.md`](byu-vc-founder-rules.md) (the policy analysis) and
[`byu-founder-contacts.md`](byu-founder-contacts.md) (who to talk to). This document covers *what BYU
actually has on the shelf* and *how the office transacts*.

Harvested **31 July 2026**. Full machine-readable listing: [`data/byu-tto-technologies.csv`](data/byu-tto-technologies.csv)
(691 rows: ID, title, tags, URL).

## What the catalog contains

**691 technologies**, disclosure IDs spanning **2000–2024**. The page is titled "Technologies
(Archived)", and the ID distribution bears that out — coverage is dense and even through 2024
(21–54 disclosures per year) and then **stops**. There are no 2025 or 2026 entries. Whatever BYU has
disclosed in the last ~18 months is not in this listing, so it is a picture of the back catalog
rather than of current deal flow.

Every item carries at least one tag; items can carry several (the tag counts below sum to more
than 691).

| Tag | Count |
|---|---:|
| Life Sciences | 371 |
| Engineering | 169 |
| Software | 143 |
| Sell Sheet | 82 |
| Mechanical Devices & Processes | 16 |
| Electronics & Instrumentation | 14 |
| Biotech/Medical | 10 |
| Pharmaceuticals / Nutraceuticals | 10 |
| Chemistry | 9 |
| Diagnostics & Drug Delivery | 8 |
| Physics | 6 |
| Engineered Structures & Materials | 4 |
| Food / Agriculture | 3 |
| Energy / Environment / Resources | 3 |
| Microfluidics | 2 |

"Sell Sheet" is a document-type flag rather than a subject: the 82 items so tagged are the ones the
office has prepared marketing material for, i.e. the subset it is actively promoting.

The detail pages add nothing — each is just the ID, title, tags, and "Reach out to us directly to
learn more about this technology." There are no abstracts, patent numbers, inventor names, or
licensing-status fields anywhere in the public listing. **Inventor names appear only in the
*Promising Technologies* document** (below), not in the searchable catalog.

## Technologies closest to VCL's domain

Keyword scan across all 691 titles. The two most on-point:

- **2018-058 — "Matdb: An Automation Framework for Machine Learning to Discover and Optimize
  Materials"** (Software, Sell Sheet). An ML-driven materials-discovery automation framework, already
  packaged for licensing. This is the nearest thing in BYU's portfolio to VCL's own premise, and it
  is worth knowing whether it is licensed, dormant, or available before VCL builds adjacent IP.
- **2005-16 — "Experiment and Optimization Platform and Toolkit Method and Conceptual Design"**
  (Software). Same idea two decades earlier; the oldest item in the catalog.

Other clusters, with counts of title matches:

| Theme | Hits | Representative entries |
|---|---:|---|
| Lab instrumentation | 66 | thin-layer chromatography plates (a long Linford-lineage series), orientation-imaging microscopy, `2016-046` HD-DVD-based fluorescent scanning thermal microscope |
| Materials / synthesis | 65 | carbon-nanotube composites and X-ray windows, ALD-prepared plates, diamond coatings, vapor-phase silane deposition |
| Automation / robotics | 17 | `2018-017` open-source automated aquarium monitoring (hardware + software), `2008-33` gradient chemical separations under automatic feedback control, `2010-060` cellular manipulation devices |
| ML / optimization / DoE | 18 | `2018-022` Design Space Relaxation Optimization Process, `2018-048` neural-network-enabled photonic IC design |
| Additive manufacturing | 13 | `2022-025` melt-detection observation and control of powder-bed fusion, `2022-031` multi-extruder AM, `2021-053` powder-bed geometry boundaries, `2022-040` 3D printing of nanoparticles |

The powder-bed-fusion and multi-extruder entries (`2021-053`, `2022-025`, `2022-031`, `2022-004`) are
the densest cluster of directly adjacent process IP, and several are Sell-Sheet-flagged — meaning
the office is actively looking for licensees.

## How the office transacts

From [`working-with-tto.pdf`](https://brightspotcdn.byu.edu/3b/7c/cfc1c6684a1bb02155a2e326b6f8/working-with-tto.pdf),
the office's own division of labor — the document previously flagged as unreachable:

**TTO's role:** receive disclosures; engage outside counsel and manage the patent process; assess
commercial viability; search for licensees; negotiate, prepare, execute and manage license
agreements; manage legal fees; collect and distribute royalties per the IP Policy; report status to
inventors and colleges.

**The inventor's role:** disclose inventions, sign the disclosure form and assignments, brief TTO on
the fundamentals, **share information about potential licensees**, **share expectations regarding
process, value, and timing**, respond to patent issues promptly, sign the license agreement
acknowledgement form (the "blue sheet"), negotiate and sign the distribution agreement, maintain
confidentiality, and **disclose to TTO any third-party collaborations involving licensed
inventions**.

Two of those inventor duties deserve attention in the founder scenario. "Share information with TTO
about potential licensees" is the sanctioned channel through which a founder-inventor tells TTO
their own company wants the license — it is an *information* duty, which sits comfortably alongside
the Related-Party bar on *negotiating*. And "disclose any third-party collaborations involving
licensed inventions" is a standing obligation that would capture a company↔lab sponsored research
agreement.

### The licensing sequence

From the *Promising Technologies* document, the deal path is explicit and staged:

1. **Option** (optional) — "Before licensing, you may want to enter into an exclusive option to
   permit further research and investigation. The length and other terms of such an option are
   negotiable. During the option period, BYU owns the technology, but you have exclusive rights to
   negotiate a license or assignment."
2. **Term sheet** — "BYU will draft a non-binding, time-sensitive term sheet for your review."
3. **License or assignment** — **License:** "BYU owns the technology, but you have rights to
   commercialize or sublicense." **Assignment:** "You own the technology."

Three things in that document matter for VCL:

- **"We will often take equity in lieu of upfront license fees."** BYU-held equity is not a
  hypothetical the IP Policy merely permits — it is the office's stated normal practice for
  cash-poor licensees. This corroborates the analysis in
  [`byu-vc-founder-rules.md`](byu-vc-founder-rules.md#when-byu-itself-holds-the-equity).
- **Assignment is on the menu, not just licensing.** A full assignment moves title to the company.
  That is a materially different structure from a license, and it is offered as a standard option.
- **"First-time entrepreneurs may be required to include a seasoned entrepreneur on their team."**
  A stated gating condition, and one that points the same direction as the Physical Intelligence
  precedent (hire the experienced full-time CEO at founding) and as BYU's own officer-title rules.

The document also states plainly why the office thinks professors commercialize: public access to
inventions, "access to industry resources through research funding and strategic collaboration," and
"supplementary personal income (inventors receive up to 45% of licensing revenue received by BYU)."

## Standard agreements and forms

All fetched from the TTO's [Resources & Forms](https://techtransfer.byu.edu/resources) page. These
are the office's actual templates — useful as the starting point for any VCL negotiation, since they
show BYU's opening position.

| Document | Link |
|---|---|
| Working with the Technology Transfer Office | [pdf](https://brightspotcdn.byu.edu/3b/7c/cfc1c6684a1bb02155a2e326b6f8/working-with-tto.pdf) |
| Memo about inventorship | [pdf](https://brightspotcdn.byu.edu/26/0e/b1e96a664ad591755e98e2e64375/inventorship-memo.pdf) |
| Preparing a patent application | [pdf](https://brightspotcdn.byu.edu/b7/2d/7f4616ae4d87bf900999ff44791c/preparing-a-patent-application.pdf) |
| Employee and Student Assignment of Ownership and Non-disclosure Agreement | [pdf](https://brightspotcdn.byu.edu/a8/a8/9899af544311a4e9a0b71331950d/employee-and-student-assignment-and-ownership-and-non-disclosure-agreement.pdf) |
| Student Thesis Non-disclosure Agreement | [pdf](https://brightspotcdn.byu.edu/c5/d2/99746d6948039f89de6704c08b46/student-thesis-non-disclosure-agreement.pdf) |
| Request to Secure Dissertation or Thesis (ADV Form 8e) | [pdf](https://brightspotcdn.byu.edu/a3/8d/e8aeae8f471dac6174612e1bfeeb/request-to-secure-dissertation-or-thesis.pdf) |
| Mutual NDA | [pdf](https://brightspotcdn.byu.edu/84/48/328e83ce4c5f98f324462b92a5b0/mutual-nda.pdf) · [doc](https://brightspotcdn.byu.edu/e7/39/64a2670747118342f13049d7dc37/mutual-nda-1.doc) |
| Unilateral NDA — disclosed *to* BYU | [pdf](https://brightspotcdn.byu.edu/3f/1a/f26d41f24468b3564b2ff0d8d51a/unilateral-nda-disclosed-to-byu.pdf) · [doc](https://brightspotcdn.byu.edu/44/33/4797121d487b9452279725c4101a/unilateral-nda-disclosed-to-byu-1.doc) |
| Unilateral NDA — disclosed *by* BYU | [pdf](https://brightspotcdn.byu.edu/70/1d/629bdafe4594b7c387fb0cfecb89/byu-nda-disclosed-by-byu.pdf) · [docx](https://brightspotcdn.byu.edu/ec/61/7ef383e643f98038c78cdc8e6aab/byu-nda-disclosed-by-byu.docx) |
| Invention Disclosure Form | [pdf](https://techtransfer.byu.edu/00000194-bdfe-da60-a1fd-bdfe319e0000/updated-byu-tto-invention-disclosure-form-pdf) · [docx](https://techtransfer.byu.edu/00000194-bdfe-da60-a1fd-bdfe31e90000/updated-tto-invention-disclosure-form-docx) · [online](https://docs.google.com/forms/d/e/1FAIpQLSeRGkL_UMsA4piX-HQwMlGZwTfSGN9P73_2YWxRqxZDzsb9rQ/viewform?usp=sf_link) |
| Selected Promising BYU Technologies (Spring 2023) | [docx](https://techtransfer.byu.edu/promising-technologies) |

Note: the Resources page's own links are malformed (they prefix `techtransfer.byu.edu/` onto the
absolute CDN URL) — the working URLs are the `brightspotcdn.byu.edu` ones above.

### The student/employee assignment agreement is stricter than expected

The [Employee and Student Assignment of Ownership and Non-disclosure
Agreement](https://brightspotcdn.byu.edu/a8/a8/9899af544311a4e9a0b71331950d/employee-and-student-assignment-and-ownership-and-non-disclosure-agreement.pdf)
is signed as a condition of participating in research, and it reaches further than the IP Policy's
ownership triggers alone:

- The signer assigns "all of my rights and ownership interests of any kind or description to the
  intellectual property as described in this document **and to all additions and/or modifications to
  this intellectual property**."
- Consideration is "the opportunity to receive wages or financial support and/or training from
  and/or to participate in research activities" — so it binds **unpaid** lab participants too.
- Anything generated in the research is treated as BYU-owned and confidential, not to be published or
  disclosed "except as authorized in this Agreement," with the standard carve-outs (previously known,
  public knowledge, independently obtained).
- Confidentiality survives departure: the obligation continues "at any time after my association with
  BYU terminates," and on leaving, all notebooks, records, data, programs and models must be returned.

**This is a live constraint on the open-source plan**, and it cuts against the default assumption
that lab output can simply be published. Clause 4's "not to publish or disclose any part of such
information" means open release runs through the same TTO gate identified in
[the open-source analysis](byu-vc-founder-rules.md#does-the-recusal-jeopardize-the-intention-to-open-source-the-work)
— either a standing release of rights or an SRA term. A lab-level "open by default" policy is still
the right instrument, but it operates *downstream* of this agreement rather than around it.

The **inventorship memo** is a plain-language summary of US inventorship law that matters for a
founder scenario: inventorship is **claim-dependent** and can change during prosecution as claims are
amended; contribution to conception (not reduction to practice) is what counts; and a person who
"merely acted under the direction and supervision of the conceivers" is not an inventor. Since the
Developer's 45% share — and the ≥10% forfeiture — key off who is named, this determines the
economics, and it is decided by counsel during prosecution rather than by the lab.

## Current TTO staff (confirmed live, 31 July 2026)

This resolves the caveat from the previous round, where the roster came only from a Wayback capture.
Fetched directly from [About Us](https://techtransfer.byu.edu/about-us):

| Name | Role | Phone |
|---|---|---|
| **Dave Brown** | Director, Software Lead | (801) 422-4866 · dave_brown@byu.edu |
| **Bennett Mortensen** | **Engineering Lead** | (801) 422-9119 · bennett_mortensen@byu.edu |
| Adam Stevens | Life & Physical Sciences Lead | (801) 422-6266 |
| Jennifer Thomas | Relationship Manager | (801) 422-6266 |
| David Campbell | Controller | (801) 422-9240 |

Office: 3760 Harold B. Lee Library, Provo UT 84602 · (801) 422-6266 · byutto@byu.edu

The Spring 2023 *Promising Technologies* document lists the prior lineup — **Mike Alder** (Director,
Life Sciences), Dave Brown (Software), **Spencer Rogers** (Engineering) — which independently
confirms the turnover: Alder has retired, Brown moved up to director, and Mortensen now holds the
engineering portfolio that Rogers had. An ME-originated cloud-lab technology is Mortensen's desk,
consistent with the steer from the AAVP–R meeting.

The office's stated primary functions include one item worth repeating: it reviews **"sponsored
research agreements and faculty consulting agreements that may involve intellectual property"** — so
TTO is a party to the SRA path, not only the licensing path.

## Scale, from the 2020 annual report

The most recent [annual report](https://techtransfer.byu.edu/0000017d-2a24-d39e-af7d-ab2432160001/annual-report-pdf)
published is 2020: **$1,944,029 in royalties** (down from $2,206,183 in 2019), **100 US patent
filings**, 29 international filings, and **7 start-up companies** formed. The office is five people.

That is a small operation by R1 standards, and it is the practical context for the "service to
faculty rather than a profit center" philosophy: roughly $2M of annual royalty income across the
whole university means an individual license is unlikely to be squeezed for maximum extraction, but
also that TTO has limited bandwidth per deal. The office nonetheless cites external rankings —
#1 among universities with under $56M in external funding (Heartland Forward, May 2022).

## Access method

`techtransfer.byu.edu` sits behind CloudFront, which returns **HTTP 403 to datacenter IPs** — the
GitHub Actions runner is blocked regardless of user agent, which is why earlier rounds of this work
fell back to the Wayback Machine. This harvest was taken from a **Tailscale-connected Raspberry Pi on
a residential connection**, which receives HTTP 200. Requests were rate-capped at 1 MB/s with ~1 s
between them; 33 result pages plus 49 facet pages plus 11 documents, ~7 MB total.

Verification: the 33 paginated pages yielded exactly 691 unique URLs with no duplicates, and each of
the 15 tag facets returned exactly the item count the facet UI advertises, so the harvest is complete
against what the site reports.

Not harvested: the per-technology detail pages (691 of them), because sampling both URL styles showed
they contain no information beyond what the listing already carries.

## Open questions for Bennett Mortensen

Arising specifically from this catalog, and complementing the
[existing question list](byu-founder-contacts.md#what-to-ask-them):

1. **Is `2018-058` (Matdb) licensed, and is the powder-bed-fusion cluster available?** These are the
   entries adjacent to VCL's domain; their status affects whether VCL licenses in, builds around, or
   collides with existing commitments.
2. **License vs. assignment for a founder-adjacent spinout** — the *Promising Technologies* document
   offers both. Which does the office prefer for a faculty-founded company, and how does BYU's equity
   position differ between the two?
3. **What does "we will often take equity in lieu of upfront license fees" mean numerically?** Typical
   percentage, share class, and whether anti-dilution or a redemption right is standard.
4. **What triggers the "seasoned entrepreneur on the team" requirement**, and would a faculty founder
   plus a hired CEO satisfy it?
5. **How is the standing "disclose any third-party collaborations involving licensed inventions" duty
   operated** when the third party is the founder's own company?
6. **Does the catalog's stop at 2024 reflect the public listing lagging, or a change in how
   disclosures are published?**
