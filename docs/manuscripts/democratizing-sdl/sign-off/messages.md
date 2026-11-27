# Draft notes to co-authors

Ready-to-paste drafts for Sterling. **None of these has been sent.** Each note links to the package rather than attaching it, so everyone reads the same copy. Replace `<deadline>` with a date about two weeks after sending. Attach the PDFs from [`review-copies/`](review-copies/) if a link is not enough.

Package links (on the PR branch until #193 is merged):

- one-page summary: `docs/manuscripts/democratizing-sdl/sign-off/summary-of-changes.pdf`
- per-author checklist: `docs/manuscripts/democratizing-sdl/sign-off/per-author-checklist.md`
- manuscript: `docs/manuscripts/democratizing-sdl/sign-off/review-copies/manuscript-v3.pdf` (Word copy with line numbers: `manuscript-v3-for-review.docx`)

---

## 1. Everyone (28 authors)

**Subject:** Democratizing SDLs Perspective: revised version for your approval by `<deadline>`

Dear all,

The revision of our Accelerate 2024 Perspective (*Digital Discovery* DD-PER-12-2024-000410, rejected in January 2025 with an invitation to resubmit) is ready for your approval. It is rebuilt around one hypothesis, as the editor asked: documentation, not hardware, is the rate-limiting step for democratized self-driving labs. Each project is used as evidence for or against it.

The one-page summary says what changed, and your section of the per-author checklist lists your contribution as worded, the files behind it, and what you need to confirm. For everyone, that is:

1. approval of the text and of submission with you as an author;
2. your full affiliation, CRediT role, funding line, conflicts of interest and ORCID;
3. the title.

Project teams also confirm what is said about their project, their row of the documentation audit (Table 5), and the commitment in §6 to an archival deposit by publication.

Please reply by `<deadline>`, with "confirmed" or a correction against each ID in your section. Tracked changes in the Word copy are welcome. RSC requires every author's explicit agreement, so silence cannot count as consent.

Thank you,
Sterling

---

## 2. DTU team (P1, P3, P4): Jin Hyun Chang, Kshitij Gambhir, Rógvi Ziskason, Louie Lucas Bisgaard Nyeland; cc Tejs Vegge

**Subject:** Perspective resubmission: one repository we can't submit without (P3), and three confirmations

Dear Jin, Kshitij, Rógvi and Louie (cc Tejs),

One item blocks the resubmission, and only you can do it. **The editor's third objection was that three projects had no repository, and the rolling ball viscometer (P3) is now the only one with nothing public.** The decision letter says a "work in progress" repository is enough. Even an afternoon's version clears it:

- the CAD files;
- a bill of materials;
- the control code as it stands;
- a licence;
- a README saying "pre-release; documentation incomplete".

Please send the URL by `<deadline>`. If it can't be done, we will take P3 out of the paper. The replacement text is already drafted.

Three confirmations:

1. **P1:** is `github.com/loppe35/PowderDispensing_and_Weighing_Module` (release v1.0.0, Zenodo 10.5281/zenodo.14746532) the P1 release? It credits only Louie. While you are there, three small fixes would help any reader:
   - 11 firmware files contain unresolved merge-conflict markers;
   - the Zenodo deposit has empty submodule folders;
   - 16 of 22 file names in the build guide don't match the files.
2. **Figure 4** (viscometer) comes from slide 4 of your showcase deck. Is that view OK for publication? If so, please send the original photograph. At revision the journal needs 600 dpi, and the slide copy is too small.
3. **Your rows:** Tables 1 and 5 for P1, P3 and P4, and whether anyone outside the team has built any of the three. P4 (`gitlab.com/auto_lab/47332-student-excercises`) also has no licence file.

The items are TV-1 to TV-7 in the checklist, and each of you also has the general items in your own section.

Thank you,
Sterling

---

## 3. P7 team: Yang Cao, Ethan Rajkumar; cc Jason Hein

**Subject:** Perspective resubmission: are these your electrochemistry files?

Dear Yang and Ethan (cc Jason),

The editor objected that P7 had no repository. Searching for this revision, we found that your files have been public all along. The manuscript never linked them, and it now cites them:

- `github.com/ethraj2001/jubilee`, commit d5c5969 (2024-08-27): the RDE adapter STLs, offered upstream as machineagency/jubilee#204;
- `github.com/cyrilcaoyang/jubilee-sdl2`, commit bc548db (2025-02-13, archived): the RDE tool class and configuration.

**Please confirm by `<deadline>` that these are P7's files.** Better still, gather them into one work-in-progress repository with a README, a parts list, the source CAD and whatever CV workflow code exists, and send the URL. The documentation audit (Table 5) would then be re-scored.

Also:

1. **Figure 8 (needed before submission).** The journal does not accept logos in figures, and RSC does not allow AI tools to edit submitted images, so we can't crop it ourselves. Could you export a clean version from your own slide, with ordinary software? It needs no logo strip, no red proofing underline, and a width of at least 1960 px. "Pipette" in place of "Opentrons" in the image avoids a brand-name query; the caption can keep the name. Please also confirm the schematic is still current.
2. Is the P7 row ($20 K, 300 h) right?
3. **Ilya Yakavets** is named as a P7 developer in Table 1 but is not in the author list. Was that intended? Please ask Ilya before we change anything.

The items are P7-1 to P7-5.

Thank you,
Sterling

---

## 4. Brenden Pelkie and Lilo Pozzo

**Subject:** Perspective resubmission: survey, selection criterion and handover

Dear Brenden and Lilo,

Thank you for the as-submitted files. The revision takes up your suggestion: it is now organized around a single, contestable position. A few things only you can settle:

1. **Selection criterion (BP-1).** §2 says the ten projects analysed are those "whose developers contributed a written description, with reproduction cost and time estimates". Is that right?
2. **Survey (BP-2, BP-3, LDP-1).** Do you have the instrument and the per-item responses? What was the response rate (58 of how many attendees)? RSC also asks for the ethics committee and a consent statement for human-subjects data. If there was no review, we can say so plainly and publish aggregates only. A fallback sentence is ready if the instrument wasn't archived.
3. **BP-4.** Is the ChemRxiv text what the editor assessed in December 2024?
4. **The manifesto (BP-5, LDP-2).** Could you send it, or confirm that the §6 obligations cover it?
5. **P6 (BP-7 to BP-9).** The science-jubilee rows of Tables 1 and 5, and a Zenodo DOI by publication (no release since v0.3.2).
6. **Handover (BP-6).** Brenden stays first author, and I take over as corresponding author.

Thank you,
Sterling

---

## 5. Tonio Buonassisi, with Alexander Siemenn and Eunice Aissi (P5)

**Subject:** Perspective resubmission: DiSCO row and Basita Das

Dear Tonio, Alex and Eunice,

The revision follows Tonio's reading of the decision letter: a strong hypothesis, supported by examples throughout. DiSCO plays an important part in it, as the strongest *complication* (§§4–5). Please check:

1. **TB-2: Basita Das** is named as a P5 developer and co-authored three of the cited module papers, but has never been in the author list. Was that intended? Please ask Basita before we change anything.
2. The P5 rows of Tables 1 and 5. `PV-Lab/DiSCO` is an empty placeholder, so the paper does not cite it. Populating it, even as a work in progress, would raise the score.
3. Archival deposits for the module repositories by publication (TB-4), and MIT funding lines (TB-5).

Thank you,
Sterling

---

## 6. P2 team: Owen Melville, Monique Ngan, Jeffrey Watchorn

**Subject:** Perspective resubmission: LEDbyXample row, and a licence

Dear Owen, Monique and Jeffrey,

Please confirm the P2 rows of Tables 1 and 5 (OM-1, OM-3), and let us know whether anyone outside the team has built LEDbyXample (OM-2). Each of the following takes minutes and improves both the repository and the paper:

- **Licence (OM-4):** `AC-SDL4/photo-reactor` has no licence file, so strictly no one may build from it. A licence also changes the paper's count of unlicensed projects.
- **README:** it names `turn_on_led` and `set_led_brightness`, but the code defines `turn_on_LED` and `set_brightness`.
- **DOI (OM-5):** a GitHub release with the Zenodo integration gives a DOI by publication.

Thank you,
Sterling

---

## 7. P10 team: Wenyu Zhang, Lucy Hao, Jason Hein

**Subject:** Perspective resubmission: IvoryOS rows

Dear Wenyu, Lucy and Jason,

Please confirm the P10 rows of Tables 1 and 5 (JEH-1, JEH-2) and §7's reading of IvoryOS as complicating our skills claim. The Zenodo deposit (10.5281/zenodo.15272617) meets our deposit commitment. However, it is a single snapshot from April 2025 under CC BY 4.0, while the repository is MIT. Turning on automatic release archiving and correcting the deposit's licence would fix both (JEH-3).

Thank you,
Sterling

---

## 8. Nadya Peek, with Blair Subbaraman, Danli Luo, Sonya Vasquez, Wm Salt Hale and Maria Politi (P6)

**Subject:** Perspective resubmission: keynote paraphrase and affiliations

Dear all,

1. **NP-1.** §6 paraphrases Nadya's closing keynote at Accelerate 2024: documentation is mandatory for open-source hardware, documentation *is* the source, and "without documentation there is no open hardware". Is that a fair paraphrase?
2. **NP-2.** v1 gave Sonya no affiliation, and the revision uses University of Washington. Sonya, please confirm or correct it.
3. **NP-3.** UW funding lines.

The science-jubilee rows (Tables 1 and 5) are with Brenden (BP-7 to BP-9).

Thank you,
Sterling

---

## 9. Seth Leavitt

**Subject:** Democratizing SDLs Perspective: may we keep you as an author?

Hi Seth,

The revision you started is ready to resubmit, and it is built on your argument: replication makes user-developed automation pay, and documentation makes replication possible. We'd like to keep you as an author. Your contribution reads "conceptualization (revised argument), project administration (coordination of the revision, August–September 2026), writing – review and editing", with BYU Mechanical Engineering as the affiliation. Could you confirm that you agree, check the wording, and send a current e-mail address for the submission system (SL-1)?

Thanks,
Sterling

---

## 10. Workshop co-organizers who are not authors: Milad Abolhasani, Curtis Berlinguette

**Subject:** Acknowledgement in the Accelerate 2024 Democratizing SDLs Perspective

Dear Milad and Curtis,

The official Accelerate 2024 programme lists you as co-organizers of the Democratizing Self-Driving Labs workshop. Our Perspective on the workshop, now being resubmitted to *Digital Discovery*, thanks you by name in the Acknowledgements. Are you content to be named (SGB-14)?

Best regards,
Sterling
