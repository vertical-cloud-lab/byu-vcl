# Sign-off package for the resubmission

Everything a co-author needs in order to approve the revised Perspective, plus the list of what still stands between it and submission. Prepared on 27 November 2026. Nothing here has been sent to anyone.

## What to send

| File | For whom | What it is |
| --- | --- | --- |
| [`summary-of-changes.md`](summary-of-changes.md) ([.docx](summary-of-changes.docx), [.pdf](summary-of-changes.pdf)) | everyone | One page: what changed since the decision letter of 9 January 2025 |
| [`per-author-checklist.md`](per-author-checklist.md) ([.docx](per-author-checklist.docx), [.pdf](per-author-checklist.pdf)) | everyone, each reading their own section | Each author's contribution as worded in the manuscript, the files and public records that back it, and the items they confirm |
| [`review-copies/manuscript-v3.pdf`](review-copies/manuscript-v3.pdf) | everyone | The manuscript as it would be submitted |
| [`review-copies/manuscript-v3-for-review.docx`](review-copies/manuscript-v3-for-review.docx) | anyone who wants to edit | The same text in Word, with line numbers and every sign-off anchor shown inline as **[[ID]]**, so each person can search for their own IDs |
| [`review-copies/esi.pdf`](review-copies/esi.pdf) | project teams | Supplementary information: Note S1 has each project as contributed, and Note S3 has the evidence for each team's Table 5 row |
| [`review-copies/response-to-decision-letter.pdf`](review-copies/response-to-decision-letter.pdf), [`review-copies/cover-letter.pdf`](review-copies/cover-letter.pdf) | senior authors | The point-by-point response and the cover letter |
| [`messages.md`](messages.md) | Sterling | Draft notes to each team, ready to paste, each with that team's specific asks |

The markdown files one level up are the source of truth. The Word and PDF copies are generated from them by [`../tools/build_review_copies.py`](../tools/build_review_copies.py) and should be regenerated after any edit.

## How people sign off

Reply to the e-mail or on [PR #193](https://github.com/vertical-cloud-lab/byu-vcl/pull/193) with "confirmed", or a correction, for each ID in your section. Corrections to the text are welcome as tracked changes in the Word review copy. Please do not soften Table 5. If a team cannot accept its row, it can ask for the row to be removed, and the caption will say so.

Silence is not consent: RSC requires the corresponding author to attest that every author agreed to the submission.

## Status and what still blocks submission

See [Who still has to do what](#who-still-has-to-do-what) below. It is kept in step with [`../sign-off-checklist.md`](../sign-off-checklist.md), the master list of IDs.
