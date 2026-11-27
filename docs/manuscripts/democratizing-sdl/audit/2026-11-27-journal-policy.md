# Digital Discovery / RSC author requirements, re-checked 2026-11-27 (Perspective resubmission, ex DD-PER-12-2024-000410)

Every live page below was accessed on **2026-11-27**. Quotes are verbatim; "…" marks a cut. Text labelled **Inference** is my reading, not RSC wording. The previous check is [`2026-10-10-journal-policy.md`](2026-10-10-journal-policy.md).

## Bottom line

- **Themed collection: closed.** The AI4X – Accelerate 2026 collection's deadline of 31 October 2026 has passed. I found no extension on the call page, the journal page, the DD blog or the web. No other Digital Discovery call is open. Submit as a regular Perspective. The guidelines require neither a proposal nor an invitation for one.
- **The policies barely changed.** The DD author guidelines read word for word as they did on 28 August and 13 November 2026. RSC-wide there are two additions:
  - retraction grounds now include "undisclosed involvement of artificial intelligence (AI)" and "image irregularities, such as alterations";
  - there is a new "Citation manipulation" section.
- **A rule the 2026-10-10 check missed is now the main blocker.** The rule was already in force: "GenAI or AI-assisted tools must not be used to alter images in submitted manuscripts". v3 says Claude cropped logos and removed a spell-check mark from Figure 8. The figure has to be redone by a person, and the disclosure changed to match.
- **Reference style is not an issue at submission.** RSC asks for "Vancouver style (not Harvard style)" and then says "we will format your content according to our house style before publication". v3's numbered references are fine.
- **Code DOI timing is unchanged.** Referees get GitHub access during review. The Zenodo deposit is due "upon acceptance", and the DOIs for "both the most recent and archived versions" go in the DAS "submitted at acceptance".
- **Editors:** Joshua Schrier is still an Associate Editor (Fordham University), so the cover letter's addressee is right. Alán Aspuru-Guzik is Editor-in-Chief and Anna Rulka is Executive Editor. Co-author Lilo D. Pozzo is listed as a DD Editorial Board Member.

## How this was checked

- I fetched pages with curl using a browser user agent. Every `rsc.org` and `blogs.rsc.org` page cited here returned HTTP 200. `pubs.rsc.org` (collection landing pages, peer-review histories, article pages) and `chemrxiv.org` still return 403.
- **Change detection.** I extracted the text of today's pages and of Wayback Machine snapshots taken either side of 2026-10-10, removed the site navigation, and diffed them:

| Page | Snapshots compared with today | Result |
| --- | --- | --- |
| DD author guidelines | [2026-08-28](https://web.archive.org/web/20260828081742/https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/digital-discovery), [2026-11-13](https://web.archive.org/web/20261113024555/https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/digital-discovery) | Body text and template links identical |
| RSC author responsibilities | [2026-09-09](https://web.archive.org/web/20260909120248/https://www.rsc.org/publishing/journals/processes-and-policies/author-responsibilities), [2026-10-13](https://web.archive.org/web/20261013084246/https://www.rsc.org/publishing/journals/processes-and-policies/author-responsibilities) | Identical, except a new "Citation manipulation" section and one new editor-duty bullet, both added after 2026-10-13 |
| RSC processes and policies | [2026-10-05](https://web.archive.org/web/20261005133157/https://www.rsc.org/publishing/journals/processes-and-policies), [2026-10-24](https://web.archive.org/web/20261024062843/https://www.rsc.org/publishing/journals/processes-and-policies), [2026-11-08](https://web.archive.org/web/20261108210929/https://www.rsc.org/publishing/journals/processes-and-policies) | Expression-of-concern and retraction criteria rewritten between 2026-10-24 and 2026-11-08; nothing else changed |
| RSC data-sharing guidance | [2026-09-14](https://web.archive.org/web/20260914121418/https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/data-sharing) | Identical |
| DD boards and teams | [2026-09-14](https://web.archive.org/web/20260914121500/https://www.rsc.org/publishing/journals/boards-and-teams/digital-discovery) | Shi Xuan Leong added as Associate Editor (announced 16 Nov 2026); Vanda Glezakou added to the Advisory Board (announced 18 Sep 2026); one affiliation edited |
| DD journal page | [2026-09-10](https://web.archive.org/web/20260910012021/https://www.rsc.org/publishing/journals/digital-discovery) | The closed LLM call was removed from the calls list; nothing else changed |
| AI4X call page | [2026-08-28](https://web.archive.org/web/20260828081747/https://www.rsc.org/publishing/journals/calls-for-papers/digital-discovery-2026-ai4x-accelerate-conference-themed-collection) | Identical: still "Submissions now open", deadline 31 October 2026 |

- **Not read:**
  - ScholarOne's submission form, which needs a login.
  - RSC's Journal Finder result for a given institution. It sets the institution with a POST request, which I skipped under the read-only rule.
  - The 2025-01-09 decision letter in full, which is not in the repository.

## What changed since 2026-10-10

1. **The AI4X collection deadline has passed** (31 October 2026), and no extension was found. The only open RSC call on self-driving labs is a joint MSDE / *Reaction Chemistry & Engineering* collection, which is not Digital Discovery (row 10.3).
2. **Retraction and expression-of-concern criteria were rewritten** (RSC processes and policies, between 2026-10-24 and 2026-11-08). Retraction grounds now name "undisclosed involvement of artificial intelligence (AI)" and "image irregularities, such as alterations and duplications" (row 4.7).
3. **New "Citation manipulation" section** (RSC author responsibilities, added after 2026-10-13) (row 5.8).
4. **Board:** Shi Xuan Leong joined as an Associate Editor on 16 November 2026. Nothing that affects this submission changed.

Everything else asked about is unchanged.

**In force on 2026-10-10 but not recorded by that check.** None of these is new; all bear on the submission:

- (a) The ban on AI-altered images (row 4.5). It conflicts with v3's Figure 8.
- (b) RSC reformats references to its house style (row 2.1). The 2026-10-10 recommendation to use "Vancouver numbered superscript references in RSC form" overstated what is required at submission.
- (c) The TOC graphic should "preferably" not reuse a figure from the article (row 8.2). v3 plans a simplified Figure 1(b).
- (d) "Adding authors from new institutions and/or countries that differ to the original author list will not be considered unless fully justified to the editor" (row 5.4). BYU was not in the original author list.
- (e) An editor who is an author gets another editor (row 5.7), and Pozzo is on the board (row 11.1).
- (f) Authors who have moved list their current address as a footnote, not an affiliation (row 5.5).
- (g) AI4X contributions went through an e-mailed request for a submission link. Proposals were asked for only for a "Review article" (row 10.1).
- (h) Preferred reviewers and the transparent-peer-review choice are entered in ScholarOne (row 7.5).
- (i) Open-access agreements are matched on the primary corresponding author's institutional e-mail and on the acceptance date (row 9.2).

## Requirements, with sources

Source links are defined at the end of the file. Access date is 2026-11-27 unless a snapshot date is given.

| # | Requirement | Verbatim quote | Source | Accessed | Changed since 2026-10-10? |
| --- | --- | --- | --- | --- | --- |
| **1.1** | Perspective: definition | "Perspectives present an authoritative state-of-the-art account of a research field. A Perspective may take the form of a personal account of research or a critical analysis of a topic of current interest. In either form, some new unpublished research may be included." | [DDG][ddg] | 2026-11-27 | No |
| 1.2 | Reviews and Perspectives in general | "Reviews and Perspectives must be high-quality, authoritative, state-of-the-art accounts of the selected research field. They should be timely and add to the existing literature, rather than duplicate existing articles…" / "All Reviews and Perspectives undergo rigorous peer review, in the same way as regular research papers." | [DDG][ddg] | 2026-11-27 | No |
| 1.3 | Length, figure or reference limits | No limit is stated for Perspectives. The only length statements on the page are for other types: "Although there is no page limit for Full papers, the appropriateness of length to content will be taken into consideration." / "Communications will not normally exceed the length of four printed journal pages." / "Opinions are typically three to four pages in length…" | [DDG][ddg] | 2026-11-27 | No |
| 1.4 | Abstract | "The abstract is a single paragraph which should: - be around 50 to 250 words" | [DDG][ddg] | 2026-11-27 | No |
| 1.5 | Invitation or proposal | Only Opinions are by invitation: "Opinions … are published by invitation of the Digital Discovery Editorial Board or Editorial Office." The page says nothing comparable for Perspectives. | [DDG][ddg] | 2026-11-27 | No |
| **2.1** | Reference style at submission | "It’s important you use Vancouver style (not Harvard style). However, we will format your content according to our house style before publication." | [DDG][ddg] | 2026-11-27 | No. The second sentence was there on 2026-08-28; the 2026-10-10 check quoted only the first |
| 2.2 | House style applied by RSC | "All articles accepted for publication in our journals are edited and typeset to our house style by professional editors: the manuscript will be formatted for you." | [DDG][ddg] | 2026-11-27 | No |
| 2.3 | Templates | "Use of the template is optional for our journals. For communications, use the communication template; for all other article types (including reviews), use the article template." | [DDG][ddg] | 2026-11-27 | No |
| 2.4 | Files at submission; embedded figures | "Article text as a Word, PDF or LaTeX file (if you use LaTeX, please also include a PDF version)" / "Numbered figures are either included within or at the end of the text…" / "The submission system allows for up to five files to be uploaded at once. Alternatively, a ZIP file containing up to 20 files can be uploaded." | [DDG][ddg] | 2026-11-27 | No |
| 2.5 | Figure specifications | "Figures, Schemes and Charts should be supplied as TIFF files, with a resolution of 600 dpi or greater. You can supply EPS or PDF files instead, but we will need to convert these to TIFF files in the final article." / "Images should fit within either single column (8.3 cm) or double column (17.1 cm) width, and must be no longer than 23.3 cm." / "Figures including logos, trademarks or brands names (for example Lego® or Rubik’s Cube®) should not be used." | [DDG][ddg] | 2026-11-27 | No |
| 2.6 | What is due at revision | "As well as your revised manuscript, you will be asked to provide a response to the referees, your figures as separate high-resolution files and a table of contents entry." | [DDG][ddg] | 2026-11-27 | No |
| **3.1** | Code and data during review | "Authors are expected to submit both their code and data to community-recognized data repositories… Referees must have access to the code and data during the peer-review process." / RSC-wide: "For all submissions to our journals, any data required to understand and verify the research in an article must be made available on submission." | [DDG][ddg] | 2026-11-27 | No |
| **3.2** | When a DOI is needed | "…any custom code referenced in the manuscript must be deposited in a persistent repository, such as Zenodo, Code Ocean, or Mendeley, upon acceptance. Authors must also obtain a DOIs for the code and/or data and submit it before publication." / "DOIs for both the most recent and archived versions of the software or code referenced in the manuscript must be included in the DAS submitted at acceptance." | [DDG][ddg] | 2026-11-27 | No |
| 3.3 | Data that goes with code | "Custom code must be accompanied by the complete dataset used for training and testing. … Similarly to a custom code, data must also be deposited in a persistent repository, with a DOI provided before publication." | [DDG][ddg] | 2026-11-27 | No |
| 3.4 | Data availability statement | "A data availability statement must be included at the end of the article under the heading “Data availability”, after the conflicts of interest statement and before any acknowledgements." / "The full URL link to data sets should be provided (not embedded behind text)." / Template: "The code for [description of software] can be found at [URL to code location] with [DOI – see guidelines below for citing software and code]. The version of the code employed for this study is version [XXX]." / "The following statement is generally not acceptable “Data are available upon request from the authors"." | [DDG][ddg] | 2026-11-27 | No |
| 3.5 | Data reviewer | "On Digital Discovery we invite a data reviewer (in addition to the regular two reviewers) who verifies that the code is functional and reproduces the reported findings. They also check if the data and/or code are appropriately presented and documented." / "Phase 2: … A third data reviewer may also be consulted to assess and comment on the code and/or data provided." | [DDG][ddg] | 2026-11-27 | No |
| 3.6 | Results produced with an LLM | "Provide log files that include the inputs and outputs used in their study." / "Specify the model identifier and generation date when using commercial LLMs." | [DDG][ddg] | 2026-11-27 | No |
| 3.7 | Citing code | "Authors are asked to provide the names of all code creators in the reference, the name of the repository, and a DOI, although a URL can be provided if a DOI is not available." / "…in the instance where code has been deposited in GitHub and Zenodo, as per the guidelines above, the Zenodo DOI is preferred for bibliographic references" | [RDS][rds] | 2026-11-27 | No (identical to 2026-09-14) |
| 4.1 | AI cannot be an author | "Artificial intelligence (AI) tools, such as ChatGPT or other Large Language Models, cannot be listed as an author on a submitted work." | [RAR][rar] | 2026-11-27 | No |
| **4.2** | What to declare, and where | "If GenAI tools have been used when generating any part of the manuscript (for example when drafting text, translating content, formatting data, creating or editing figures, visualising results, refining code, or compiling references) this must be declared at submission within the cover letter. Authors should also include a statement within the Experimental/Materials and Methods section outlining how the tool was used, including prompts. Details of the AI tool such as the name and specific model or version (e.g., GPT-4 or Claude 3.5 Sonnet) should be included in the Acknowledgements section. If there is no Experimental/Materials and Methods section, all details must be included in the Acknowledgements section. The use of an LLM (or other AI-tool) for “AI assisted copy editing” purposes does not need to be declared." | [RAR][rar] | 2026-11-27 | No (identical on 2026-09-09 and 2026-10-13) |
| 4.3 | Recommended wording | "“During the preparation of this manuscript/study, the author(s) used [tool name, version information] for the purposes of [description of use]. The authors have reviewed and edited the output and take full responsibility for the content of this publication.”" | [RAR][rar] | 2026-11-27 | No |
| 4.4 | DD: Acknowledgements | "You should also declare all sources of funding and any use of artificial intelligence (AI) tools at this point." | [DDG][ddg] | 2026-11-27 | No |
| **4.5** | Editing images with AI | "GenAI or AI-assisted tools must not be used to alter images in submitted manuscripts. This includes adding, removing, moving, or obscuring features within an image or figure. Basic adjustments such as brightness, contrast or colour balance are acceptable, provided they do not hide or remove original information. We may use image forensics or specialist software to check for irregularities." | [RAR][rar] | 2026-11-27 | No. In force on 2026-09-09; **not recorded by the 2026-10-10 check** |
| 4.6 | Figures or graphics made with AI | DDG: "If using AI tools to help create figures, authors must confirm that the AI tool has been trained using fully licensed datasets and the terms of the licence to use the AI output allow commercial reuse." / RAR: "Any AI tool used during image creation should be trained on licensed datasets and the output must be cleared for commercial reuse." | [DDG][ddg], [RAR][rar] | 2026-11-27 | No |
| **4.7** | Consequences of undisclosed AI use | RAR (unchanged): "If AI usage is suspected and not disclosed, the RSC reserves the right to contact the author for further information. If concerns are not addressed satisfactorily, the manuscript may be withdrawn, rejected or retracted." / RPP (**new**): "Editors can decide to retract a publication if they no longer have confidence in the results and conclusions reported in the paper. Reasons for this loss of confidence can be, but are not limited to: … image irregularities, such as alterations and duplications; … Any form of misrepresentation, for example: … undisclosed involvement of artificial intelligence (AI)." | [RAR][rar], [RPP][rpp] | 2026-11-27 | **Yes** (the RPP text; added between 2026-10-24 and 2026-11-08) |
| 5.1 | Authorship criteria (ICMJE) | "Final approval of the version to be published, AND - Agreement to be accountable for all aspects of the work…" | [RAR][rar] | 2026-11-27 | No |
| 5.2 | Corresponding author's attestation | "On submission of the manuscript, the corresponding author attests to the fact that those named as co-authors have agreed to its submission for publication and accept the responsibility for having properly included all (and only) co-authors." | [RAR][rar] | 2026-11-27 | No |
| 5.3 | CRediT; more than 10 authors | RAR: "We strongly recommend you use CRediT (the Contributor Roles Taxonomy) for standardised contribution descriptions. All authors should have agreed to their individual contributions ahead of submission… Please note that for any manuscript with more than 10 co-authors the corresponding author must provide the editor with a statement to specify the contribution of each co-author." / DDG: "If there are more than 10 co-authors on the manuscript, the corresponding author should provide a statement to specify the contribution of each co-author." | [RAR][rar], [DDG][ddg] | 2026-11-27 | No |
| 5.4 | Changing authors | "Authors must notify the editorial office of any changes in authorship after initial submission… Authorship changes post-submission will only be considered in exceptional circumstances and are subject to editorial approval. Authorship changes post-acceptance will generally not be considered. In general, adding authors from new institutions and/or countries that differ to the original author list will not be considered unless fully justified to the editor. All authors, including those being added or removed, must agree to any changes." | [RAR][rar] | 2026-11-27 | No. The new-institution sentence was present; the 2026-10-10 quote cut it |
| 5.5 | Affiliations | "The author affiliation(s) listed should be the institution(s) where the majority of the research was conducted. If an author has multiple affiliations all the relevant institutions should be listed. If the present address of an author is different from that at which the work was conducted, that address should be stated in a footnote and not as an affiliation." | [DDG][ddg] (same text in [RAR][rar]) | 2026-11-27 | No |
| 5.6 | ORCID | "We require the submitting author to provide an ORCID iD when submitting a revised manuscript, and we also encourage all co-authors to link their ORCID iD to their account on our submission system." | [RPP][rpp] | 2026-11-27 | No |
| 5.7 | An editor among the authors | "Specifically, in cases where an editor is an author of a submitted manuscript, the manuscript must be passed to another editor for independent peer review." / "The relevant Royal Society of Chemistry journal concerned should be informed of any significant conflicts of interest that editors, authors or reviewers may have…" | [RAR][rar] | 2026-11-27 | No |
| 5.8 | Citation manipulation | "Authors should not engage in excessive or inappropriate self-citation of their own work." / "Authors should avoid excessive citations to support a single statement in their article." / "Suspected citation manipulation by the authors may result in rejection of the submission or retraction of the article if published…" | [RAR][rar] | 2026-11-27 | **Yes** (added after 2026-10-13) |
| **6.1** | Human subjects | "When a study involves the use of human subjects, authors should adhere to the general principles set out in the Declaration of Helsinki. Authors must include in the 'methods/experimental' section of the manuscript a statement that all experiments were performed in compliance with the relevant guidelines. The statement must name the institutional/local ethics committee that has approved the study, and where possible the approval or case number should be provided. Details of all guidelines followed should be provided. A statement regarding informed consent is required for all studies involving human subjects." | [RAR][rar] (same text in [EXP][exp]) | 2026-11-27 | No |
| 6.2 | DD's softer wording | "For studies that involve the use of live animals or human subjects an ethical statement may be required." | [DDG][ddg] | 2026-11-27 | No |
| 6.3 | Exemption for anonymous surveys | None found in the DD guidelines, author responsibilities or experimental-reporting pages. | [DDG][ddg], [RAR][rar], [EXP][exp] | 2026-11-27 | No |
| 6.4 | DD precedent (not policy) | Hung *et al.*, "Autonomous laboratories for accelerated materials discovery: a community survey and practical insights", *Digital Discovery*, 2024 (102 survey responses). Its sections run Abstract, 1–5, Data availability, Author contributions, Conflicts of interest, Acknowledgements, with no ethics or consent statement anywhere in the main text. DAS: "De-identified responses to the survey, additional details on survey design and deployment, and figures summarizing selected responses are provided in the ESI." The ESI was not read. | [HUNG][hung] (Wayback copy of the RSC HTML, captured 2026-05-24) | 2026-11-27 | n/a |
| **7.1** | Resubmission or appeal | "Appeals will only be considered on manuscripts that have not been revised. If you submit a revised version of a previously considered manuscript this will be treated as a resubmission and not an appeal." | [DDG][ddg] | 2026-11-27 | No |
| 7.2 | Citing the previous ID; time limit | **No RSC text found.** I checked the DD guidelines, processes and policies, author responsibilities, revise-or-transfer and assessment-and-review pages. Search-engine summaries of DD's published peer-review histories say a resubmission gets a new submission date; `pubs.rsc.org` returns 403, so this is unverified. | [DDG][ddg], [RPP][rpp], [REV][rev] | 2026-11-27 | Unknown |
| 7.3 | Response document | For transfers that already have reports: "These files should include a summary of any new work added and a point by point response to the reviewers’ comments." / For revisions: "Make sure that you address all reviewer comments, and if you have decided not to make a change, explain why." | [DDG][ddg], [REV][rev] | 2026-11-27 | No |
| 7.4 | Cover letter | "Your cover letter will be sent to reviewers." / "Address your letter to the relevant Associate Editor or Executive Editor." / "Avoid repeating information that is already in your abstract or introduction." / "Don’t include preferred/non-preferred reviewers in your letter as these should be entered in the manuscript submission system only." / "Don’t refer to themed issue invitations or invited articles as these should be entered in the manuscript submission system only." | [DDG][ddg] | 2026-11-27 | No |
| 7.5 | Entered in ScholarOne, not in files | "A list of preferred reviewers; should be entered in the manuscript submission system" / "You will also be asked to supply the names and contact details of all co-authors." / transparent peer review: "You can opt in during the submission and peer review process and can change your mind about transparent peer review at any point prior to acceptance." | [DDG][ddg] | 2026-11-27 | No |
| **8.1** | When the TOC entry is due | "A table of contents entry (graphical abstract) is required, which should be submitted at the revision stage." | [DDG][ddg] | 2026-11-27 | No |
| 8.2 | TOC graphic | "Be original, unpublished artwork created by one of the co-authors. Preferably, the graphic should not be reused and appear again within the article. If using AI tools to help create the graphic, authors must confirm that the AI tool has been trained using fully licensed datasets and the terms of the licence to use the AI output allow commercial reuse." / "Not contain logos, trademarks or brands names." | [DDG][ddg] | 2026-11-27 | No (the "not reused" sentence was present but not recorded on 2026-10-10) |
| 8.3 | TOC size and text | "The figure should be a maximum size of 8 cm wide x 4 cm high. It is recommended that authors make use of the full space available." / "Figures should be supplied as TIFF files, with a resolution of 600 dpi or greater." / "The text supplied should be 1-2 sentences long, using a maximum of 250 characters." / "Avoid repeating or paraphrasing the title or abstract." | [DDG][ddg] | 2026-11-27 | No |
| **9.1** | APC | "APC (Applicable for submissions from 1 January 2026)" / "Full price \| £2,200 (+ local taxes if applicable)*" / "Corresponding authors from India, Indonesia and Philippines \| £1,100 (+ local taxes if applicable)" / "Corresponding authors from Research4Life Group A & Group B \| Full APC waiver" / "*15% RSC member and institutional discounts available. Applicable to full price only." / "APCs apply to accepted articles only, there are no submission charges." | [DDG][ddg], [PAY][pay] | 2026-11-27 | No. The payments page shows no 2027 price yet, so the price for submissions from 1 January 2027 is unknown |
| 9.2 | Who an agreement covers | "We identify eligible articles using the email address of the primary corresponding author as assigned in our submission system." / "Article eligibility is based on editorial acceptance date (‘latest decision date’ in the report)." / "If your institution has an agreement with us that covers APCs, you will be notified of this at article acceptance." | [OAA][oaa], [DDG][ddg] | 2026-11-27 | No (not checked on 2026-10-10) |
| 9.3 | Agreements for the authors' institutions | RSC's own tool is the [Journal Finder][jf]; not queried (see "How this was checked"). The self-reported [OA Forward registry][reg] lists RSC agreements with **CRKN (Canada), 2025-01-01 to 2027-12-31** and **Lyrasis (US consortium), 2024-01-01 to 2026-12-31**. It lists none for BYU, U Washington, MIT, DTU (or any Danish consortium) or Bergen. CRKN: "authors affiliated with participating CRKN member institutions can now publish open access in both hybrid and gold RSC journals at no cost to the author." / "The term of this agreement is January 1, 2025, to December 31, 2027." | [JF][jf], [REG][reg], [CRKN][crkn] | 2026-11-27 | Unknown |
| **10.1** | AI4X – Accelerate 2026 collection | Call page: "Submissions now open" / "Deadline:" / "31 October 2026" … "whether specifically presented at the conference or not". Blog: "The deadline for submissions is 31 October 2026." / "If you would like to contribute to this collection, please let us know by email at digitaldiscovery-rsc@rsc.org, and we will set up a submission link for you to contribute your article." / "Authors are welcome to submit original research in the form of a Communication or Full Paper. Authors who would like to contribute a Review article should contact the Editorial office with their proposal." Newsletter, 29 Sep 2026: "…before the deadline of 31 October 2026." | [AI4X][ai4x], [AI4XB][ai4xb], [NEWS][news] | 2026-11-27 | **Yes: the deadline has passed.** No extension found: the call page body is identical to 2026-08-28, and no blog post or other web page announces one |
| 10.2 | Other Digital Discovery calls | The journal page lists only AI4X. "General purpose models: Large language models and beyond": "The deadline for submissions is 31 August 2026." It was removed from the journal page after 2026-09-10. The blog's "Open calls" category has nothing newer. **No DD collection is open.** | [DDJ][ddj], [LLMC][llmc], [OPEN][open], [CALLS][calls] | 2026-11-27 | Yes (the LLM call was already closed before 2026-10-10, but was still listed then) |
| 10.3 | Not DD: joint MSDE / RCE collection | "This joint themed collection from Molecular Systems Design & Engineering (MSDE) and Reaction Chemistry & Engineering…" / "Deadline: 31 May 2027" / themes include "benchmarking and reproducibility, including community challenges that can be used to test novel platforms" / "please contact the Editorial Office at MSDE or Editorial Office at Reaction Chemistry & Engineering with your proposed topic." | [MSDE][msde] | 2026-11-27 | n/a |
| **11.1** | Editors | Board page: "Alán Aspuru-Guzik / Editor-in-Chief / University of Toronto, Canada"; "Anna Rulka / Executive Editor / Royal Society of Chemistry, UK"; "Joshua Schrier / Associate Editor / Fordham University, USA"; "Milad Abolhasani / Associate Editor"; "Lilo D Pozzo / Editorial Board Member / University of Washington, USA"; "Alexander Whiteside / Deputy Editor". Jason E. Hein is not listed, and was not on 2026-09-14 either. | [BOARD][board] | 2026-11-27 | No for Schrier, the Editor-in-Chief and Pozzo |
| 11.2 | New Associate Editor | "We’re pleased to welcome Prof. Shi Xuan Leong, of Nanyang Technological University, Singapore, to the Editorial Board of Digital Discovery as an Associate Editor." (16 Nov 2026) | [LEONG][leong] | 2026-11-27 | Yes (no bearing on this submission) |
| 11.3 | Schrier's title | "The program of speakers includes our Associate Editors Prof. Joshua Schrier and Prof. Yousung Jung." | [NEWS][news] | 2026-11-27 | No |
| **12.1** | Disclosing the preprint | "Previous publication of an abstract or preprint of the proceedings of meetings does not preclude subsequent submission for publication, but full disclosure should be made at the time of submission…" | [RAR][rar] | 2026-11-27 | No |
| 12.2 | Posting a revised preprint | "We allow preprints deposited in ChemRxiv (only) to be the revised version, but must still be a pre-acceptance version" | [RPP][rpp] | 2026-11-27 | No |
| 12.3 | Citing a ChemRxiv preprint | "ChemRxiv & bioRxiv: The citation should include the author(s), the name of the preprint server, the year, the word “preprint” and the DOI (including version number)." | [DDG][ddg] | 2026-11-27 | No |

### Notes on the table (inference marked)

- **1.3, 1.5. Inference:** a Perspective has no word, figure or reference cap, and needs no pre-submission enquiry. This one was explicitly invited to resubmit in any case. The office can still decline it at initial assessment.
- **2.1. Inference:** "Vancouver (not Harvard)" contrasts numbered with author–date citation. v3's numbered superscripts with an ordered list qualify, even though the entries are in ACS rather than RSC format. RSC copy-editing reformats them.
- **2.4:** a single Word or PDF file with the figures embedded is acceptable at submission. Separate high-resolution figure files are due at revision (2.6).
- **3.2:** no DOI is needed at submission. The DAS submitted at acceptance needs two Zenodo DOIs: the concept DOI ("most recent") and the version DOI ("archived").
- **3.6. Inference:** v3's Table 5 scores were "proposed with the assistance of a large language model" (ESI Note S3). That is close enough to "LLM use for inference" that supplying logs, model identifiers and dates is the safe reading.
- **6.4:** DD published a survey-based article with no ethics statement in the main text. That suggests the editor might accept a plain "anonymous workshop feedback" statement, but the policy text (6.1) still says "must".
- **7.2:** with no RSC rule, the decision letter governs. Cite the ID in the cover letter (v3 already does) and in any ScholarOne field that asks for it.
- **9.2–9.3. Inference:** since Sterling G. Baird (sterling.baird@byu.edu) is the primary corresponding author, BYU's agreement status decides the APC. Agreements held by U Washington, Toronto or UBC do not apply. Eligibility is judged at acceptance, so an agreement ending on 2026-12-31 (such as Lyrasis's, if BYU were in it) would not cover a 2027 acceptance unless renewed.
- **12.2:** no arXiv copy of the original exists (arXiv API and OpenAlex searched 2026-11-27), only ChemRxiv v1. So a revised preprint, posted as a new version of 10.26434/chemrxiv-2025-zhkrf before acceptance, is within the rule.

## Edits the manuscript, cover letter or response letter now need

Text is quoted rather than given by line number, because these files were being edited during this check. Edits are in priority order.

**Must do before submission**

1. **Replace the AI-edited Figure 8** (rows 4.5, 4.7).
   - **Files:** `figures/fig8-electrochemical-workflow.png`; `manuscript-v3.md` (Figure 8, Acknowledgements); `cover-letter.md`.
   - **What:** v3's figure was cropped and retouched by Claude (logo strip removed, spell-check underline removed, a letter descender restored). That is "removing … features" and "adding" with an AI-assisted tool. A person should remake it from the original in `figures/source/` with ordinary image software. Better still, the P7 team could export a clean version from their own slide, with the logos removed and proofing marks turned off at source.
   - **Then:** in the Acknowledgements, delete "; and to crop institutional logos and a spell-check mark from Figure 8". In the cover letter's **Use of generative AI** paragraph, delete ", and clean one contributed figure".
   - **Do not** delete the disclosure while keeping the AI-edited file. Undisclosed AI involvement and image alteration are now named retraction grounds.
   - **Optional, while remaking it:** DD's figure rule (2.5) discourages brand names inside figures. If the image itself carries the "Opentrons" label, a generic label ("pipette") avoids a production query; the caption can keep the name.

2. **Venue** (rows 10.1–10.2).
   - The cover letter needs nothing; it rightly says nothing about collections.
   - `sign-off-checklist.md` SGB-13 and the "Themed collections" paragraph of `revision-notes-v3.md` §6 still say AI4X "is open until 31 October 2026". Both should say it closed with no extension, and that the paper goes in as a regular Perspective.
   - Joining AI4X late would need an e-mail to digitaldiscovery-rsc@rsc.org. That is a decision for Sterling, not taken here.

3. **Cover letter: mention the board member** (rows 5.7, 11.1).
   - **File:** `cover-letter.md`, in the authorship paragraph.
   - **What:** add "Co-author Lilo D. Pozzo is a member of the *Digital Discovery* Editorial Board." That lets the office route the manuscript under RSC's editor-as-author rule.
   - **In ScholarOne:** do not propose Milad Abolhasani (Associate Editor, thanked in the Acknowledgements) or any co-author as a reviewer.

4. **Cover letter: explain the new institution** (rows 5.4, 5.5).
   - **File:** `cover-letter.md`, after "Since the original submission, Sterling G. Baird has become corresponding author…".
   - **What:** BYU was not in the original author list. Add one sentence, for example: "Brigham Young University appears for the first time because Sterling G. Baird carried out the revision there, keeping the Acceleration Consortium affiliation from the original work, and Seth Leavitt contributed from BYU." The response letter's "Other changes" item 5 already says this; the cover letter does not.
   - **Also (`manuscript-v3.md` author block, via ALL-2):** any author whose present address differs from where the work was done keeps the original institution, with the current address in a footnote.

5. **Table-of-contents entry** (rows 8.1, 8.2, 4.6).
   - **File:** `cover-letter.md`. Remove "table-of-contents graphic" from **Enclosures**, unless it exists by submission. It is due "at the revision stage"; the text can stay.
   - **File:** `manuscript-v3.md`, Table of contents entry, "Graphic:" line (and SGB-15). Replace "A simplified Figure 1(b) is the natural candidate" with: an original graphic drawn by a co-author, not a reuse of Figure 1 ("Preferably, the graphic should not be reused and appear again within the article").
   - Make it without AI image tools. **Inference:** otherwise RSC requires a confirmation about the tool's training data that the authors are not in a position to give.

6. **Logs and model identifiers for the LLM-proposed scores** (rows 3.6, 4.2).
   - **File:** `esi/supplementary-information.md`, Note S3 **Method**.
   - **What:** after "The scores were proposed with the assistance of a large language model…", add the model identifiers and dates of the runs that proposed and re-checked the scores, and say that the session record is archived with the analysis code. The SIGN-OFF comment under the Acknowledgements lists runs and models: `claude-opus-5` in the September runs, and `claude-opus-5-5` with `claude-haiku-5-5` in run 38081233692 on 2026-10-10, the day every cell was re-checked. It does not say which runs produced the scores, so match them first.
   - **Why:** those identifiers are now only in an HTML comment, which will not render.
   - **Time-sensitive:** the comment notes that the August run logs have already expired. Save whatever record of the scoring session exists now and put it in the Zenodo deposit: the run logs and the issue/PR threads.

7. **Data availability statement** (rows 3.2, 3.4).
   - **File:** `manuscript-v3.md`, Data availability.
   - **(a)** Replace `/tree/main/` in the GitHub URL with the tag or commit used for submission. Add DD's template sentence: "The version of the code employed for this study is [tag/commit]." This finishes SGB-4.
   - **(b)** Change "a Zenodo DOI for the archived version will be added at acceptance" to "Zenodo DOIs for this version and for the latest version (concept DOI) will be added at acceptance".
   - **File:** `response-to-decision-letter.md`, Point 3 table, last row. Change "Zenodo DOI at acceptance" to "Zenodo DOIs (version and concept) at acceptance".

8. **Survey ethics statement in the main text** (rows 6.1–6.4).
   - **File:** `manuscript-v3.md` §2. Put the ethics and consent sentence in §2 itself, not only in Supplementary Note S2. RSC requires it "in the 'methods/experimental' section of the manuscript", and §2 is that section for the survey. At present §2 says only that "the survey's ethics and consent information are given in Supplementary Note S2".
   - **Content:** unchanged from BP-3/LDP-1: committee name, approval or exemption number, and a consent statement; or, failing those, a plain statement that there was none.
   - The Hung *et al.* precedent lowers the risk of the plain-statement fallback but does not remove it.

**No change needed, or optional**

9. **References** (rows 2.1, 5.8, 12.3).
   - No conversion to RSC format is needed before submission.
   - Optionally update ref. 40's access date to 2026-11-27; the guidelines text it relies on was re-checked today and is unchanged.
   - Under the new citation-manipulation section: 14 of the 45 references include a co-author. Almost all are the source for a project's own description, and P5's refs 21–24 each support a different component. No change needed.

10. **Cover letter polish** (rows 7.4, 11.3).
    - Schrier is still the right addressee. The journal's own newsletter writes "Prof. Joshua Schrier", so "Dear Professor Schrier" is an option in both letters; "Dr" is not wrong.
    - DD asks cover letters to "Avoid repeating information that is already in your abstract or introduction". The three bullets under "we show the following" repeat the abstract's numbers and could shrink to one sentence.

11. **Entered in ScholarOne, not in the files** (rows 5.6, 7.2, 7.5, 12.1):
    - article type Perspective;
    - DD-PER-12-2024-000410 in any resubmission or previous-manuscript field and in the comments to the editor. No RSC page describes that field, so check the form;
    - the ChemRxiv DOI in any preprint field;
    - preferred reviewers, with no co-authors, close collaborators or Abolhasani;
    - funders and grant numbers in the funding fields;
    - an opt-in decision on transparent peer review;
    - the submitting author's ORCID, linked now (it is required by the revised-manuscript stage).

12. **Cost** (rows 9.1–9.3); no file changes.
    - The APC is £2,200 plus tax, 15% less for an RSC member.
    - **Inference:** the price follows the submission date, and no 2027 price is published. Submitting before 1 January 2027 fixes the 2026 price.
    - BYU is not in the OA Forward registry. Check it in the [Journal Finder][jf]: search for "Brigham Young University (US)". This takes a minute in a browser.

**At revision (not needed now)** (rows 2.5, 2.6)

13. **Figure resolution.** Separate TIFFs at 600 dpi or more, fitting 8.3 cm or 17.1 cm width. Several figures fall short at their likely width, so ask the teams for originals now:

| Figure | Pixel width | dpi at 8.3 cm | dpi at 17.1 cm | Action |
| --- | --- | --- | --- | --- |
| Fig. 4 | 1532 | 469 | 228 | Below 600 dpi even at single column; ask the team for the original |
| Fig. 8 | 1842 | 564 | 274 | Below 600 dpi even at single column; ask the team for the original |
| Figs 2, 3, 6, 7 | 2048 | 627 | 304 | Pass only at single-column width |
| Fig. 5 | 3302 | 1010 | 490 | Single column only, unless an original exists |
| Fig. 9 | 3200 | 979 | 475 | Use the 16039-px TIFF in `figures/source/` |
| Fig. 1 | 2880 | 881 | 428 | Re-render from the script at 600 dpi |

**Housekeeping (outside the three files):**

- `revision-notes-v3.md` §6, row "Submitting author ORCID required": the rule is "when submitting a revised manuscript".
- [`2026-10-10-journal-policy.md`](2026-10-10-journal-policy.md), Implications item 9: "Vancouver numbered superscript references in RSC form" overstates what is needed at submission (row 2.1).

[ddg]: https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/digital-discovery
[rar]: https://www.rsc.org/publishing/journals/processes-and-policies/author-responsibilities
[rpp]: https://www.rsc.org/publishing/journals/processes-and-policies
[rds]: https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/data-sharing
[exp]: https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/experimental-reporting
[rev]: https://www.rsc.org/publishing/publish-with-us/publish-a-journal-article/revise-or-transfer-your-article
[ddj]: https://www.rsc.org/publishing/journals/digital-discovery
[board]: https://www.rsc.org/publishing/journals/boards-and-teams/digital-discovery
[ai4x]: https://www.rsc.org/publishing/journals/calls-for-papers/digital-discovery-2026-ai4x-accelerate-conference-themed-collection
[ai4xb]: https://blogs.rsc.org/dd/2026/08/04/open-call-for-papers-ai4x-accelerate-conference-2026-themed-collection/
[news]: https://blogs.rsc.org/dd/2026/09/29/digital-discovery-october-2026-newsletter/
[llmc]: https://blogs.rsc.org/dd/2026/05/08/call-for-papers-general-purpose-models-large-language-models-and-beyond-themed-collection/
[open]: https://blogs.rsc.org/dd/category/open-calls/
[calls]: https://www.rsc.org/publishing/journals/calls-for-papers
[leong]: https://blogs.rsc.org/dd/2026/11/16/leong/
[msde]: https://www.rsc.org/publishing/journals/calls-for-papers/self-driving-laboratories-for-chemical-discovery-and-engineering-msde
[pay]: https://www.rsc.org/publishing/open-access/payments-and-funding
[oaa]: https://www.rsc.org/publishing/open-access/open-access-agreements
[jf]: https://rsc.chronoshub.io/
[reg]: https://oaforward.org/portfolio/registry-of-open-publishing-agreements/
[crkn]: https://crkn-rcdr.ca/en/crkn-signs-read-and-publish-agreement-royal-society-chemistry
[hung]: https://web.archive.org/web/20260524232101/https://pubs.rsc.org/en/content/articlehtml/2024/dd/d4dd00059e
