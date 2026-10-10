# Digital Discovery / RSC policy research for the Perspective resubmission (ex DD-PER-12-2024-000410)

All pages accessed **2026-10-10**. Quotes are verbatim from pages fetched that day; ellipses mark cuts.

**What I could not open.** `pubs.rsc.org`, `chemrxiv.org` and ResearchGate all returned Cloudflare HTTP 403 to every automated fetch, and the Wayback Machine was offline. So the full texts of the editorials (hardware 2024, Commit 2025) and of the ChemRxiv preprint were **not** read directly. Where I report their content, I say which secondary source it came from: Crossref metadata, the RSC blog, or search-engine snippets.

Main sources:
- DD author guidelines (DDG): https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/digital-discovery
- RSC author responsibilities (RAR): https://www.rsc.org/publishing/journals/processes-and-policies/author-responsibilities
- RSC processes and policies (RPP): https://www.rsc.org/publishing/journals/processes-and-policies
- RSC data-sharing guidance (RDS): https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/data-sharing

---

## 1. Digital Discovery Perspective requirements

**What a Perspective is (DDG):**
> "Reviews and Perspectives must be high-quality, authoritative, state-of-the-art accounts of the selected research field. They should be timely and add to the existing literature, rather than duplicate existing articles, and should be of general interest to the journal's wide readership."
> "All Reviews and Perspectives undergo rigorous peer review, in the same way as regular research papers."
> "All review content should consist of original text and interpretation, avoiding any direct reproduction. If a significant amount of other people's material is to be used, either textual or image-based, permission must be sought by the author in accordance with copyright law and must be made clear in the manuscript."
> "Perspectives present an authoritative state-of-the-art account of a research field. A Perspective may take the form of a personal account of research or a critical analysis of a topic of current interest. In either form, some new unpublished research may be included."

The last sentence is what allows the new Python script and the 10-project self-audit to sit inside a Perspective.

**Length.** DDG sets no length limit for Perspectives. The only length guidance nearby is for other types:
- Full papers: "Although there is no page limit for Full papers, the appropriateness of length to content will be taken into consideration."
- Opinions: "typically three to four pages".
- Templates: "The templates will give you an idea of length and layout … Use of the template is optional … for all other article types (including reviews), use the article template."

**Abstract (DDG):** "The abstract is a single paragraph which should: be around 50 to 250 words … avoid including detailed information on how the research was carried out".

**Table of contents (TOC) entry (DDG):**
> "A table of contents entry (graphical abstract) is required, which should be submitted at the revision stage. This should include an eye-catching graphic and 1-2 sentence(s) of text to summarise the key findings of the article to the reader."

The graphic:
- "Be original, unpublished artwork created by one of the co-authors."
- "If using AI tools to help create the graphic, authors must confirm that the AI tool has been trained using fully licensed datasets and the terms of the licence to use the AI output allow commercial reuse."
- "Not contain logos, trademarks or brands names."

The text:
- "Avoid repeating or paraphrasing the title or abstract."
- "Not be a description or caption of the graphical abstract image."
- "Be provided in an editable format, eg, .docx file."

Specifications:
- "The figure should be a maximum size of 8 cm wide x 4 cm high."
- "Figures should be supplied as TIFF files, with a resolution of 600 dpi or greater."
- "The text supplied should be 1-2 sentences long, using a maximum of 250 characters."

**Keywords.** No keyword list is required for the article. DDG only advises using searchable terms: for the title, "Use keywords and familiar, searchable terms"; for the abstract, "use familiar, searchable terms and keywords". The only "keywords" field DDG mentions is in the ScholarOne account form. Author biographies are not required; DDG only gives photo dimensions in case they are used.

**References (DDG):**
- "It's important you use Vancouver style (not Harvard style)."
- "Use superscript numbers to show the reference source of statements in the text"
- "Journal articles should be cited in the form: A. Name, B. Name and C. Name, Journal Title, year, volume, page/article number(s), DOI [optional]." Article titles are optional for DD; DD is not on the list of journals that require them.
- "The names and initials of all authors should be given in the reference."
- Web pages: "Name of resource, URL, (accessed date)."
- ChemRxiv: "the author(s), the name of the preprint server, the year, the word "preprint" and the DOI (including version number)."

**Supplementary information (ESI) (DDG):**
- "Supplementary data is peer-reviewed and should therefore be included with the original submission"
- "Supplementary Information files are published 'as is'"
- "Use common, widely known and machine-readable file formats where possible"
- "References cited in the Supplementary Information (SI) may be listed at the bottom of the reference section of the main manuscript. Please include a note in the data availability statement to explain that references cited in the SI have been listed in the article's reference list."

**Data availability statement (DAS): mandatory (DDG).**
> "a data availability statement (DAS) is required to be submitted alongside all articles."
> "These should include, where applicable, links to datasets … This section should list the database, accession number, DOI, URL or any other relevant details. The full URL link to data sets should be provided (not embedded behind text)."
> "A data availability statement must be included at the end of the article under the heading "Data availability", after the conflicts of interest statement and before any acknowledgements."

Template wording offered:
- "The code for [description of software] can be found at [URL to code location] with [DOI …]. The version of the code employed for this study is version [XXX]."
- "Data collected from human participants, described in [Fig. X], are not available for confidentiality reasons."

DDG also warns: "The following statement is generally not acceptable "Data are available upon request from the authors"."

**Cover letter (DDG):**
> "This is a chance for you to explain the importance of the work submitted and why it is most suitable for the journal. **Your cover letter will be sent to reviewers.**"

Its instructions include "Address your letter to the relevant Associate Editor or Executive Editor" and "Don't refer to themed issue invitations or invited articles as these should be entered in the manuscript submission system only."

**Article processing charge (APC) (DDG):** "Full price £2,200 (+ local taxes if applicable)", applicable for submissions from 1 January 2026. The journal is gold open access.

## 2. Data and code policy (DDG, verbatim)

> **Data requirements for submission.** "Authors are expected to submit both their code and data to community-recognized data repositories, or to a general repository if no community-specific option is available. Referees must have access to the code and data during the peer-review process. Furthermore, to ensure long-term availability, any custom code referenced in the manuscript must be deposited in a persistent repository, such as Zenodo, Code Ocean, or Mendeley, upon acceptance. Authors must also obtain a DOIs for the code and/or data and submit it before publication."
> "DOIs for both the most recent and archived versions of the software or code referenced in the manuscript must be included in the DAS submitted at acceptance. We recommend using Zenodo for referencing and citation for code and data deposited on GitHub."
> **Data sharing.** "Custom code must be accompanied by the complete dataset used for training and testing. … Similarly to a custom code, data must also be deposited in a persistent repository, with a DOI provided before publication."
> **Hardware papers.** "Papers that describe hardware must include detailed supporting information, including a comprehensive bill of materials and a construction guide. All design files and software code should be hosted in a public, persistent repository … Authors should provide relevant files in an editable format."
> **Peer review.** "On Digital Discovery we invite a data reviewer (in addition to the regular two reviewers) who verifies that the code is functional and reproduces the reported findings. They also check if the data and/or code are appropriately presented and documented."
> **LLM use for inference.** "authors are required to: Provide log files that include the inputs and outputs used in their study … Specify the model identifier and generation date when using commercial LLMs."

Two RSC-wide rules also apply. From RPP: "For all submissions to Royal Society of Chemistry journals, any data required to understand and verify the research in an article must be made available on submission." From RDS, the GitHub row of the repository table reads "Please also consider archiving code in combination with a repository that can issue a DOI", and on citing code:
> "Authors are asked to provide the names of all code creators in the reference, the name of the repository, and a DOI, although a URL can be provided if a DOI is not available." "Please cite the specific release where possible" … "in the instance where code has been deposited in GitHub and Zenodo … the Zenodo DOI is preferred for bibliographic references".

**What this means for the resubmission:**
- **A DOI is not required at submission.** A GitHub link that referees can open is acceptable. Zenodo or equivalent DOIs become mandatory "upon acceptance" and "before publication".
- **Work-in-progress repositories.** No policy text addresses them. However, the "most recent **and** archived versions" wording fits a living GitHub repository plus a frozen Zenodo release (a concept DOI plus a version DOI) that matches the manuscript.
- **Checklist.** I found no Digital Discovery-specific data/code checklist. The guidelines, the 2021 data-reviewer blog (https://blogs.rsc.org/dd/2021/12/16/data-reviewer/) and searches turned up none. The nearest thing is RSC's generic submission checker (https://submission-checker.rsc.org), which can "verify the presence of important compliance statements". The 2021 blog says a data reviewer assesses "the data and code provided" for "all manuscripts which include original research", along with "the submitted Data Availability Statements".
- **Hardware editorial.** Hein & Schrier, "Guidelines for hardware-focused articles", *Digital Discovery*, 2024, 3, 447–448, DOI 10.1039/D4DD90009J (bibliographic details from Crossref). According to search-indexed text of the editorial (not read directly), it sets four criteria: "(1) relevance to the digitalization of chemical research (broadly defined); (2) comparative analysis of the hardware to existing alternatives; (3) replicability and modification of the design; (4) instructions for operation and safety."

## 3. RSC policy on generative AI (RAR, verbatim)

> **Authorship.** "Artificial intelligence (AI) tools, such as ChatGPT or other Large Language Models, cannot be listed as an author on a submitted work. AI tools do not meet the criteria to qualify for authorship, as they are unable to take responsibility for the work, cannot consent to publication nor manage copyright, licence or other legal obligations, and are unable to understand issues around conflicts of interest."
> "Authors are fully responsible and accountable for the content of their article, including any parts produced by an AI tool."
> "We do not permit the presentation of any kind of content generated by AI tools as though it were original research data/results from nonmachine sources."
> **Disclosure.** "If GenAI tools have been used when generating any part of the manuscript (for example when drafting text, translating content, formatting data, creating or editing figures, visualising results, refining code, or compiling references) this must be declared at submission within the cover letter. Authors should also include a statement within the Experimental/Materials and Methods section outlining how the tool was used, including prompts. Details of the AI tool such as the name and specific model or version (e.g., GPT-4 or Claude 3.5 Sonnet) should be included in the Acknowledgements section. If there is no Experimental/Materials and Methods section, all details must be included in the Acknowledgements section. The use of an LLM (or other AI-tool) for "AI assisted copy editing" purposes does not need to be declared."
> **Recommended statement in Acknowledgements.** "During the preparation of this manuscript/study, the author(s) used [tool name, version information] for the purposes of [description of use]. The authors have reviewed and edited the output and take full responsibility for the content of this publication."
> "If AI usage is suspected and not disclosed, … the manuscript may be withdrawn, rejected or retracted."
> **Images.** "Where graphics have been created using AI for illustrative or aesthetic purposes only, a brief description of AI use should be included in the figure caption … Details of the AI tool … should be included in the Acknowledgements section."

DDG adds to the Acknowledgements section: "You should also declare all sources of funding and any use of artificial intelligence (AI) tools at this point."

**Credit for the AI.** Claude cannot be an author. No RSC text provides for crediting AI in CRediT or the author-contributions statement; tool details go in Acknowledgements. So disclosure goes in three places:
1. The cover letter.
2. A Methods-type section (how the tool was used, **including prompts**), or Acknowledgements only if the paper has no such section.
3. Acknowledgements (tool name and specific model/version).

## 4. Resubmitting a previously rejected manuscript

The only explicit RSC text on resubmission is in DDG (identical in RPP and other RSC journals):
> "Appeals will only be considered on manuscripts that have not been revised. If you submit a revised version of a previously considered manuscript this will be treated as a resubmission and not an appeal."

Related RSC text:
- One RPP ground for returning a manuscript without review (stated for rejections by a *different* RSC journal): "the manuscript has already been reviewed and rejected by a different Royal Society of Chemistry journal, and the author(s) have made little or no attempt to address the advice that the editor and/or reviewers have provided already".
- For transferred manuscripts that already have reports, the revised files "should include a summary of any new work added and a point by point response to the reviewers' comments" (DDG and https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/revise-or-transfer-your-article).
- Revision advice (DDG): "Make sure that you address all reviewer comments, and if you have decided not to make a change, explain why."
- Preprints (RAR): "Previous publication of an abstract or preprint … does not preclude subsequent submission for publication, but full disclosure should be made at the time of submission". RPP: "We allow preprints deposited in ChemRxiv (only) to be the revised version, but must still be a pre-acceptance version".

**Not found:** any RSC page requiring the previous manuscript ID to be quoted, or a published description of ScholarOne's resubmission field. The 2025-01-09 decision letter's own instructions take precedence. In practice it goes in as a new ScholarOne submission that cites DD-PER-12-2024-000410, with a point-by-point reply to the editor's comments. The preprint to disclose is ChemRxiv 10.26434/chemrxiv-2025-zhkrf (posted 2025-02-12, CC BY-NC 4.0, 27 authors per Crossref).

## 5. Authorship requirements

**Criteria (RAR).** RSC recommends the ICMJE criteria, including "Final approval of the version to be published, AND Agreement to be accountable for all aspects of the work".

**All authors approve submission (RAR):**
> "On submission of the manuscript, the corresponding author attests to the fact that those named as co-authors have agreed to its submission for publication and accept the responsibility for having properly included all (and only) co-authors."

**CRediT.** RAR: "we strongly encourage … an 'Author Contributions' section … We strongly recommend you use CRediT … All authors should have agreed to their individual contributions ahead of submission … for any manuscript with more than 10 co-authors the corresponding author must provide the editor with a statement to specify the contribution of each co-author." DDG adds: "If there are more than 10 co-authors on the manuscript, the corresponding author should provide a statement to specify the contribution of each co-author."

**So with 27 authors, a per-author contribution statement is effectively mandatory.**

**ORCID (RPP):** "We require the submitting author to provide an ORCID iD when submitting a revised manuscript, and we also encourage all co-authors to link their ORCID iD to their account on our submission system."

**Conflicts of interest.** RAR: "a Conflicts of interest statement is required for all submitted manuscripts. If no conflicts exist, please state that 'There are no conflicts to declare' under a Conflicts of interest heading as the last section before your Acknowledgements." Per DDG, the DAS goes between the COI statement and the Acknowledgements.

**Adding authors (RAR):**
> "Authors must notify the editorial office of any changes in authorship after initial submission … Authorship changes post-submission will only be considered in exceptional circumstances and are subject to editorial approval. … All authors, including those being added or removed, must agree to any changes. Authors must also provide a reason for the change, explain why authors are being added/deleted after submission and demonstrate that any authors being added made a significant intellectual contribution to the paper. We reserve the right to request evidence supporting authorship contribution."

A resubmission is a new submission, so strictly these are not post-submission changes. Even so, the safe course is to explain the two additions in the cover letter, using these criteria.

## 6. Ethics for an anonymous attendee survey

RSC has **no explicit exemption** for anonymous surveys. The applicable text:
- DDG: "For studies that involve the use of live animals or human subjects an ethical statement may be required. For full details, please refer to our Human & Animal Welfare policy."
- RAR / experimental-reporting page (https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/experimental-reporting):
  > "When a study involves the use of human subjects, authors should adhere to the general principles set out in the Declaration of Helsinki. Authors must include in the 'methods/experimental' section of the manuscript a statement that all experiments were performed in compliance with the relevant guidelines. The statement must name the institutional/local ethics committee that has approved the study, and where possible the approval or case number should be provided. Details of all guidelines followed should be provided. A statement regarding informed consent is required for all studies involving human subjects."

**DD precedent.** Hung et al., "Autonomous laboratories for accelerated materials discovery: a community survey and practical insights", *Digital Discovery*, 2024, 3, 1273–1279, DOI 10.1039/D4DD00059E. It is a DD Opinion built on a 102-response survey. I could not open its text or SI to see how it handled ethics. Worth checking before deciding on wording.

## 7. Accelerate 2024 and the "Democratizing Self-Driving Labs" workshop

**Dates and venue.** "Vancouver • Aug 6 — 9, 2024" (https://www.accelerate24.ca/program). "This year's conference will be held primarily at two venues located at the University of British Columbia in Vancouver, Canada. The Nest … The Robert H. Lee Alumni Centre" (https://www.accelerate24.ca/about). It was co-hosted by the Acceleration Consortium and UBC.

**The workshop is on the official programme.** Official PDF: https://cdn.prod.website-files.com/6595b07837c97657e3cd5cb4/66ab7f56721acdeddc63a3ae_AC24-Digital-Program-V6.pdf, Tuesday 6 August 2024:
- "12:45—2:45 PM ROBERT H. LEE ALUMNI CENTRE, JACK POOLE HALL Workshop: Democratizing self-driving labs (Part I)"
- "2:55—4:55 PM … Workshop: Democratizing self-driving labs (Part II)"

Organizers: Tejs Vegge, Sterling Baird, Tonio Buonassisi, Lilo Pozzo, Brenden Pelkie, Jason Hein, Milad Abolhasani, Curtis Berlinguette. The web description ends: "This workshop will involve talks, discussion, and a hardware exhibition."

Note that the programme calls it a "hardware exhibition", not a "demo session". Also, Abolhasani and Berlinguette are listed as organizers but are **not** in the preprint's Crossref author list. That matters if the text says "we organized".

**The 14 projects: not publicly verifiable from what I could reach.**
- The preprint abstract (from Crossref) confirms: "14 examples of custom built hardware, software, and workflows were shared … ten contributed examples … are highlighted."
- The list itself is only in the ChemRxiv full text (blocked).
- The forum topic (https://accelerated-discovery.org/t/272, "Democratizing Self-driving Labs Workshop: 'So you want to build a self-driving lab'", 2024-08-06) holds only a slide deck.
- No AC Substack, LinkedIn or programme page lists the projects. Use the manuscript source as the authority.

## 8. Accelerate themed collections in Digital Discovery

**There is no standalone "AC2024" collection.** The 2024 conference shares a combined **"Accelerate Conference 2023–2024"** collection.
- It is **published and closed**: announced 19 Feb 2026, "has now been published online" (https://blogs.rsc.org/dd/2026/02/19/new-themed-collection-in-collaboration-with-accelerate-conference-2023-2024/).
- Collection URL: https://pubs.rsc.org/en/journals/articlecollectionlanding?sercode=dd&themeid=4d92f48e-5474-4e4d-afb4-7dde5e725c15
- Guest editors: J. George, C. Ouellet-Plamondon, K. Reyes. Editorial DOI: 10.1039/D5DD90057C.
- It contains papers a reviewer will expect this Perspective to engage with: Lo et al. "frugal twin" Tutorial Review (10.1039/D3DD00223C), Doloi et al. "Democratizing self-driving labs: advances in low-cost 3D printing…" (10.1039/D4DD00411F), the Hung et al. survey Opinion, Archerfish (10.1039/D4DD00249K) and Opentrons viscometry (10.1039/D4DD00368C).

**Accelerate 2025 collection:** "currently underway" as of Feb 2026: https://pubs.rsc.org/en/journals/articlecollectionlanding?sercode=dd&themeid=d417bcf8-8458-4280-9a00-99fdcd42e07e

**Open now: AI4X – Accelerate Conference 2026 themed collection** (https://blogs.rsc.org/dd/2026/08/04/open-call-for-papers-ai4x-accelerate-conference-2026-themed-collection/):
> "whether specifically presented at the conference or not" … "The deadline for submissions is 31 October 2026." … "Authors are welcome to submit original research in the form of a Communication or Full Paper. Authors who would like to contribute a Review article should contact the Editorial office with their proposal."

## 9. Open-hardware literature (all checked against Crossref; summaries from abstracts unless noted)

**The four candidates:**
- **(a)** J. M. Pearce, "Return on investment for open source scientific hardware development", *Sci. Public Policy*, 2016, **43**(2), 192–195, DOI 10.1093/scipol/scv034 (online 20 Jun 2015; issue Apr 2016). It gives a method for calculating funders' return on investment from the savings when others replicate a released open design. Its syringe-pump case study reaches returns of hundreds to thousands of percent within months. (The abstract was not retrievable; this summary is from Semantic Scholar's TLDR.)
- **(b)** J. Bonvoisin, R. Mies, J.-F. Boujut and R. Stark, "What is the "Source" of Open Source Hardware?", *J. Open Hardw.*, 2017, **1**(1), 5, DOI 10.5334/joh.7. It argues that whether hardware counts as open source is "not only a question of licence but a question of documentation". Its analysis of 132 products finds widely varying interpretations, and some misuse, of what has to be shared.
- **(c)** A. Maia Chagas, "Haves and have nots must find a better way: The case for open scientific hardware", *PLoS Biol.*, 2018, **16**(9), e3000014, DOI 10.1371/journal.pbio.3000014. It argues that open-science initiatives ignore access to equipment, which is unevenly distributed mainly for cost reasons. It makes the case for open hardware in research and education, including at well-funded institutions.
- **(d)** DIN SPEC 3105-1:2020-07, *Open Source Hardware – Part 1: Requirements for technical documentation* (Text in English), DIN Media (formerly Beuth), Berlin, July 2020, DOI 10.31030/3173063. Free download: https://www.dinmedia.de/en/technical-rule/din-spec-3105-1/324805763. Working repository: https://gitlab.com/OSEGermany/OHS-3105. Note the date is **2020-07**, not -09. The companion Part 2 (community-based assessment) is DOI 10.31030/3173062.

**Three additional references (one per theme):**
- **Cost.** J. M. Pearce, "Economic savings for scientific free and open source technology: A review", *HardwareX*, 2020, **8**, e00139, DOI 10.1016/j.ohx.2020.e00139. Open tools save on average 87% against proprietary equivalents: 89% with Arduino, 92% with RepRap-class 3D printing, 94% with both.
- **Replication.** R. Antoniou, R. Pinquié, J.-F. Boujut, A. Ezoji and E. Dekoninck, "Identifying the factors affecting the replicability of open source hardware designs", *Proc. Des. Soc.*, 2021, **1**, 1817–1826, DOI 10.1017/pds.2021.443. From a survey and interviews, it finds a bill of materials plus assembly instructions are not enough. Replicability depends on the documentation, the design and the replicator's context.
- **Documentation quality.** D. Saubke, P. Krenz and T. Redlich, "Howling for a New Standard – Deficits in Open Source Hardware Documentation", *Procedia CIRP*, 2025, **136**, 195–200, DOI 10.1016/j.procir.2025.08.035. It analyses existing open hardware against DIN SPEC 3105 and identifies documentation deficits that prevent reproduction in industrial settings. This is the closest analogue to the self-audit.

## 10. The "Commit" article type

**Official definition (DDG):**
> "Commit reports an incremental improvement to the work previously published in Digital Discovery and should clearly outline the limitations of the prior work that have been addressed. Authors may optionally include a brief summary of relevant recent developments to support the rationale for their improvements. The title must indicate that it is a Commit and include the title of the original article being improved, formatted as: 'Commit: [Title of the original article].' Please note that at this time Commits are submitted as Technical Notes for technical reasons." "While Commit reports are generally shorter than full articles, there is no strict page limit."

**Launch.** RSC blog, 23 Jan 2025 (https://blogs.rsc.org/dd/2025/01/23/introducing-commit-a-mini-article-for-dynamic-reporting-of-incremental-improvements-to-previous-scholarly-work/):
> "This new type of article allows the community to share changes to work published in Digital Discovery articles, whether this is one's own work or another's. We see Commits as citable articles describing the changes made to a project, which could be a full manuscript, or an open hardware or software project published in the journal."

The blog lists three examples:
- "Hardware articles: a device which has the same motivation and use but has an improvement in capabilities or construction."
- "Software articles: addition of features or improvement of capabilities."
- "Data: incorporating additional data while keeping the underlying schema the same".

It adds: "We expect that most of the improvements will be present in associated code/data repositories or supporting information".

The editorial is Aspuru-Guzik, Hein & Schrier, "Commit: Mini article for dynamic reporting of incremental improvements to previous scholarly work", *Digital Discovery*, 2025, 4, 301–302, DOI 10.1039/D4DD90053G. Crossref abstract: "a new article type at Digital Discovery intended for reporting incremental improvements on work previously published in the journal".

**Peer review is not confirmed.** Neither DDG nor the blog says how Commits are reviewed; the editorial full text was blocked. A search-engine summary claims the editorial specifies 2–3 reviewers, one of them an author of the original article plus a data reviewer. That claim is **unverified**. They are handled as Technical Notes.

**Yoshikawa Commit vs the 2023 paper:**
- Yoshikawa et al., *Digital Discovery*, 2026, **5**(1), 93–97, DOI 10.1039/D5DD00336A (Crossref): "We present an updated version of the digital pipette … The new version supports disposable tip replacement to reduce contamination while maintaining high accuracy."
- The 2023 original is Yoshikawa et al., *Digital Discovery*, 2023, **2**, 1745–1751, DOI 10.1039/D3DD00115F: "an economical 3D-printed pipette … to overcome the limitations of two-finger robot grippers".

In short, the Commit adds disposable-tip replacement.

**Relevance here.** Commit only applies to work previously *published* in DD, so the Perspective itself cannot be a Commit. It is, however, a ready-made mechanism for the documentation-update argument.

---

## Implications for the resubmission

1. **Cover letter, which reviewers will see.**
   - Address it to the handling Associate Editor.
   - Identify the paper as a resubmission of DD-PER-12-2024-000410, rejected at editorial assessment on 2025-01-09 with an invitation to resubmit.
   - Give a point-by-point account of how each editorial concern was addressed.
   - Disclose ChemRxiv 10.26434/chemrxiv-2025-zhkrf and how this version differs from it.
   - Follow any instructions in the decision letter, which take precedence.
2. **GenAI disclosure in three places.**
   - Cover letter: a declaration.
   - A Methods/"Approach" section: how Claude was used, including prompts. Depositing the prompt/session logs in the archive is the practical way to satisfy "including prompts".
   - Acknowledgements: the exact model name/version, using RSC's recommended sentence.
   - Claude must not appear in the author list or the CRediT statement.
   - If an LLM was used for any *analysis* (for example, scoring the audit), also supply input/output logs, the model identifier and the generation date.
3. **Code and data.**
   - A public GitHub URL is enough for review. Mint Zenodo DOIs (version plus concept) before publication, and ideally now, since a data reviewer will run the script and judge its documentation.
   - Ship a README, a pinned environment, the audit rubric and raw per-project scores, and a one-command reproduction.
   - Cite the code in the references using the Zenodo DOI.
4. **"Data availability" section.** Place it after Conflicts of interest and before Acknowledgements, with full URLs and DOIs and no "available on request". Add the SI-references note if SI cites references.
5. **Author contributions.** With 27 (or more) authors, a per-author contribution statement is mandatory; use CRediT. All authors must agree to their contributions, and to submission, beforehand.
6. **Author-list change from the 2024 submission.** Name the two added contributors in the cover letter, give the reason they were omitted, describe their significant intellectual contribution, and confirm all authors agree. Also reconcile "we organized the workshop" with the programme's organizer list (Abolhasani and Berlinguette are not authors).
7. **ORCID and COI.** The submitting author needs a linked ORCID iD; encourage co-authors to link theirs. Include a "Conflicts of interest" statement. Consider whether authors maintaining or selling any of the audited projects should declare.
8. **Survey ethics.**
   - Preferred: in the Methods, name the ethics committee and give the approval or exemption/"not human subjects research" determination number, plus an informed-consent or anonymity statement.
   - If no determination exists, obtain one or reframe the survey as anonymous workshop feedback. In that case state that explicitly and let the editor decide.
   - Publish aggregate data only.
9. **Format.**
   - Single-paragraph abstract of 250 words or fewer.
   - TOC graphic: 8 × 4 cm TIFF at 600 dpi, no logos.
   - TOC text: 1–2 sentences, 250 characters or fewer, not repeating the title.
   - Vancouver numbered superscript references in RSC form.
   - Figure permissions for reused project images.
   - If AI helped make a figure or the TOC graphic, the licensing confirmation and a caption note.
10. **Positioning.**
    - Explicitly differentiate from DD's frugal-twin Tutorial Review, the Doloi et al. 3D-printing review and the Hein & Schrier hardware guidelines, because Perspectives must "add to … rather than duplicate".
    - Engage Pearce 2016 and 2020, Bonvoisin 2017, Maia Chagas 2018, DIN SPEC 3105-1, Antoniou 2021 and Saubke 2025.
    - Optionally target the open AI4X–Accelerate 2026 collection (deadline **31 Oct 2026**). A Perspective needs a prior email to the Editorial Office, and the collection is selected in ScholarOne, not mentioned in the cover letter.
