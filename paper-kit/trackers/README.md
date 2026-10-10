# Draft tracker issues: TMS 2027 student abstracts

**Drafts for review. None of these has been posted, and no issue exists for
any of them.** One per student-presented abstract: 13 of the lab's 16 TMS 2027
abstracts (the other three are presented by Sterling). Each file is the body
of one issue; its first lines (an HTML comment, invisible once posted) give
the title and the repository it belongs in.

Abstracts, presenters, symposia and slots are from ProgramMaster, read
2026-10-10. Ten are scheduled oral talks; all ten are students' (Sterling's
two talks are separate). Six abstracts are not yet in any published session:
five of these thirteen (Luke, Audrey, Tim, Ben and the camera poster) and one
of Sterling's. Where a symposium has published every oral session, an
unscheduled abstract is probably a poster, but ProgramMaster does not say so.
TMS emails presenters their time and place in early January.

| # | Presenter | Abstract | Slot (ProgramMaster) | Journal | Tracker |
|---|---|---|---|---|---|
| 1 | Gage Erickson | [Optimizing Ultrasonic Atomization Parameters for Supply-Chai...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/8C6E7050A962719685258E270075387D?OpenDocument) | Talk, Thu Mar 18, 10:40 AM, Magnolia 13 | [JOURNAL] | [01-gage-erickson.md](01-gage-erickson.md) |
| 2 | Carl Robison | [An ICME Loop for Composition-Aware LPBF Parameter Qualificat...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/30908CDE388B906E85258E34004DF864?OpenDocument) | Talk, Mon Mar 15, 4:05 PM, San Antonio | [JOURNAL] | [02-carl-robison.md](02-carl-robison.md) |
| 3 | Ronnie Guymon | [CALIBER: A Retrieval-Augmented, Uncertainty-Aware Platform f...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/62FB3D040E8FD6C085258E340053D059?OpenDocument) | Talk, Mon Mar 15, 3:10 PM, Anaheim | [JOURNAL] | [03-ronnie-guymon.md](03-ronnie-guymon.md) |
| 4 | Xavier Zaitzeff | [Implementation of Bayesian Optimization over Function Networ...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/1701C81A5B7A265E85258E27006D39F9?OpenDocument) | Talk (25-minute slot), Wed Mar 17, 10:55 AM, Los Angeles | [JOURNAL] | [04-xavier-zaitzeff.md](04-xavier-zaitzeff.md) |
| 5 | Sam Charles | [A Programmable Powder Doser with 15+ Reservoirs and Automate...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/B6383C9897FAF23585258E280014B8D5?OpenDocument) | Talk, Mon Mar 15, 9:40 AM, Washington | [JOURNAL] | [05-sam-charles.md](05-sam-charles.md) |
| 6 | Will Mulberry | [Auger-Based Powder Dosing as a Mechanistic Probe of Powder F...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/B309C32B4F06F84485258E2800150419?OpenDocument) | Talk, Mon Mar 15, 4:40 PM, Magnolia 18 | Additive Manufacturing | [06-will-mulberry.md](06-will-mulberry.md) |
| 7 | Luke Winters | [Agentic Systems Design of an Open-Source Powder Doser for L-...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/2711856F2A84241585258E2800155BBF?OpenDocument) | Not yet in a published session (probably a poster) | [JOURNAL] | [07-luke-winters.md](07-luke-winters.md) |
| 8 | Marcus Madsen | [Closed-Loop Bayesian Optimization of Multi-Material 3D-Print...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/E59DA70A00DDE30685258E350063E8D5?OpenDocument) | Talk, Tue Mar 16, 4:45 PM, Washington | ASME Journal of Mechanical Design | [08-marcus-madsen.md](08-marcus-madsen.md) |
| 9 | Audrey Christiansen | [Tensegrity-Inspired Lattices for Orientation-Invariant Impac...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/8AA038D180FB1CAE85258E2800132DD4?OpenDocument) | Not yet in a published session (probably a poster) | [JOURNAL] | [09-audrey-christiansen.md](09-audrey-christiansen.md) |
| 10 | Jinkwan Han | [Closed-Loop Bayesian Optimization of Multi-Material 3D-Print...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/4190282C54D62AD685258E270070DE50?OpenDocument) | Talk, Mon Mar 15, 10:50 AM, Crystal Ballroom A | [JOURNAL] | [10-jinkwan-han.md](10-jinkwan-han.md) |
| 11 | Tim Commins | [FeS/PbS Precipitation Boundaries for Impurity Management in ...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/D2B181B3FF2CADCB85258E35005F8A0D?OpenDocument) | Not yet in a published session (probably a poster) | [JOURNAL] | [11-tim-commins.md](11-tim-commins.md) |
| 12 | Ben Whitney | [A Benchtop Self-Driving Laboratory for Aqueous Chemistry Bui...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/8D7F11E04E518CF485258E340076CCDA?OpenDocument) | Not yet in a published session (probably a poster) | [JOURNAL] | [12-ben-whitney.md](12-ben-whitney.md) |
| 13 | Seth Leavitt | [Low-Cost Open-Source Camera Modules for Continuous Monitorin...](https://www.programmaster.org/PM/PM.nsf/ApprovedAbstracts/DF0C2EB3DB75D5C385258E2800046C6E?OpenDocument) | Not yet in a published session; submitted as a student poster | [JOURNAL] | [13-camera-poster.md](13-camera-poster.md) |

## Gates

The same seven for everyone. All four fixed dates are Fridays; the update is
the Thursday before.

| Gate | Date | Done when |
|---|---|---|
| G1 Outline | Fri Oct 23, 2026 | journal chosen (preprint policy and licence checked), title, authors and order, the claim in one sentence, the figure list, a section outline |
| G2 Results freeze | per paper, placeholder | every figure scripted from `data/`, every data file with its README, `make figures check colorblind` clean |
| G3 Draft to co-authors | Fri Jan 29, 2027 | the whole draft, `git tag g3`, sign-off round 1 |
| G4 My review | placeholder, between G3 and G5 | `make rebuild-check` and a fresh-clone build first; then the review PDF and the diff since G3 |
| G5 Preprint and submission | Fri Feb 26, 2027 | every author has approved this version; `make submission-check` passes; preprint posted and paper submitted |
| G6 Slides or poster | Fri Mar 5, 2027 | made from the paper's figures |
| G7 Practice talk | placeholder, before Sun Mar 14 | given to the group, feedback addressed |

TMS facts the gates lean on (tms.org and ProgramMaster, 2026-10-10):
contributed talks are about 20 minutes including questions; rooms have a
Windows laptop without internet, so bring the talk on a USB drive; a poster
board is 4 ft × 4 ft; every presenter, poster presenters included, must
register; student travel grant applications close Nov 15, 2026; the housing
deadline is Feb 16, 2027.

## Thursday update

Four lines, every Thursday, as a comment on the tracker:

```
Figure: [one figure: figures/out/figN_slug.png at commit abc1234, or the image]
Numbers: [the numbers behind it: n, value ± error, data/<file>]
Next week: [one thing]
Blocker: [one blocker, or none]
```

## Posting them, once reviewed

Nothing here runs by itself. After review, each can be opened with, for
example:

```bash
f=trackers/06-will-mulberry.md
gh issue create --repo "$(sed -n 's/^Open in: \([^ ]*\).*/\1/p' "$f")" \
  --title "$(sed -n 's/^Issue title: //p' "$f")" \
  --assignee "$(sed -n 's/.*Assignee: //p' "$f")" --body-file "$f"
```

Fill the `[JOURNAL]`, `[REPO]` and `[DATE]` placeholders first; the issue title
carries the journal.
