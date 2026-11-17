# Meetings with outside people that trace back to an agent ping

For point 3 of the [outline](outline.md): "**[N]** meetings came directly from agent-assisted
searches and outreach". Compiled 2026-11-17 for [#350](https://github.com/vertical-cloud-lab/byu-vcl/issues/350).

**Bottom line: about 7 meetings (4 confirmed, 3 likely), from about 27 people and organisations
contacted through agent-built lists or agent-drafted e-mails, so roughly 1 in 4.** This is a
lower bound. Meetings set up over e-mail, Slack, LinkedIn or in private repos leave no public
trace, and only some projects post "met with" notes.

Wording that the evidence supports:

> *"Roughly half a dozen meetings with outside experts came from contact lists and e-mails that
> agents drafted, including professors in Lisbon, Berkeley and Michigan, and BYU's research VP."*

Two caveats belong in the talk:

- **Most of these came through GitHub Copilot's coding agent, not `@claude`.** Copilot was
  running Claude Opus 4.6 or 4.7, often with Edison for the literature. `@claude` alone
  accounts for 1 confirmed meeting and 1 likely one. "Agents" is accurate; "Claude" is not.
- **Nothing from MRS yet.** No public thread holds an MRS list of people to meet, or a meeting
  arranged there. MRS Fall 2026 runs Nov 29 to Dec 4, so any meetings there are still ahead.
  The MRS mentions on GitHub are abstracts ([byu-vcl#158](https://github.com/vertical-cloud-lab/byu-vcl/issues/158),
  [powder-doser#78](https://github.com/vertical-cloud-lab/powder-doser/issues/78)).

## Method

A search agent downloaded every issue, PR and comment from the 13 active public repos in
`vertical-cloud-lab`, about 11,000 records, plus their Discussions. It searched them for meeting,
call, Zoom, met with, reach out, outreach, LinkedIn, e-mail, intro, quote, demo, vendor, expert,
MRS and conference, then read each promising thread in full. It also checked whether the people
met appear in the agent-built contact lists, such as tensegrity-optimization's
[`reviews/target_audience.md`](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/56f58de/reviews/target_audience.md).

A meeting counts only if an agent ping found the person, drafted the outreach, or both. The
thread then has to show the meeting happening (**confirmed**), or a reply and an agreement to
meet (**likely**). Lab members, BYU staff already working with the lab, and contacts found
without an agent are left out. I opened the evidence links for rows 1, 2 and 4 and the ONR call
note in row 6, and they say what the table says.

## Meetings

| # | Confidence | Who | When | Agent | How the agent helped | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | confirmed | Dr. Haris Moazam Sheikh, UC Berkeley (Bayesian optimisation for architected materials) | 2026-07-20 | Copilot agent (Claude Opus 4.7) + Edison | On the agent's [contact list](https://github.com/vertical-cloud-lab/tensegrity-optimization/blob/56f58de/reviews/target_audience.md) from the [ping](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-4411465237). Marcus e-mailed him on 7-16 | [Meeting notes](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-5023444019) |
| 2 | confirmed | Dr. Filipe A. Santos, NOVA Lisbon (tensegrity metamaterials) | 2026-07-23 | Copilot agent (Claude Opus 4.7) + Edison | Same list. E-mailed 7-07, agreed 7-16 | [Meeting notes](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-5060966013) |
| 3 | confirmed | Dr. Liwei Wang, University of Michigan (design optimisation) | 2026-07-28 | Copilot agent (Claude Opus 4.7) + Edison | Same list. E-mailed 7-16 | [Meeting notes](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-5109861072) |
| 4 | confirmed | Larry Howell, BYU research VP (outside the lab) | 2026-07-31 | `@claude` | Claude [ranked him first](https://github.com/vertical-cloud-lab/byu-vcl/pull/156#issuecomment-5029878939) among people to talk to and drafted the e-mail. You sent it on 7-27 | ["Met with Larry"](https://github.com/vertical-cloud-lab/byu-vcl/pull/156#issuecomment-5147164919) |
| 5 | likely | Dr. Andrea Micheletti, University of Rome Tor Vergata (tensegrity additive manufacturing) | after 2026-07-16 | Copilot agent (Claude Opus 4.7) + Edison | Same list as rows 1–3 | [Agreed to meet](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-4994551651), no notes after |
| 6 | likely | Charles Fisher, Office of Naval Research | 2026-10-16 | `@claude` | Claude's ONR YIP package included a drafted e-mail to him. You supplied the name, and the e-mail history is private, so it can't be checked that the sent e-mail was Claude's draft | [Call follow-ups](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/117#issuecomment-6322117066) |
| 7 | likely | Xact Metal (LPBF printers) | 2026-05-21, 2026-07-30 | Copilot agent (Claude Opus 4.6) | Listed in the agent's [printer survey](https://github.com/vertical-cloud-lab/byu-vcl/pull/62#issuecomment-4042277853), with drafted quote requests. Carl requested a quote | [Second meeting's notes](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/133#issuecomment-6353368469). It's a vendor call |

### Outreach with no meeting recorded

About 20 more people and organisations were contacted from agent lists or with agent-drafted
e-mails, with no meeting recorded:

- 10 more researchers from the tensegrity contact list, e-mailed in June and July
  ([PR 41](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-4696267676)).
- The CADSmith authors at CMU, the CadQuery maintainers, and Zoo, who
  [replied with free credits](https://github.com/vertical-cloud-lab/powder-doser/pull/43#issuecomment-5245007983)
  ([powder-doser PR 43](https://github.com/vertical-cloud-lab/powder-doser/pull/43#issuecomment-5223100759)).
- A former BYU engineering dean, from the same Claude list as row 4
  ([byu-vcl PR 156](https://github.com/vertical-cloud-lab/byu-vcl/pull/156#issuecomment-5094556663)).
- Four alternative-funding contacts after the PRF decision, from Claude's drafts
  ([digital-wetlab PR 82](https://github.com/vertical-cloud-lab/digital-wetlab/pull/82#issuecomment-6528871317)).
  The replies are in a private note.
- Two powder-sheet suppliers, Addicoat and IMR, who both replied
  ([byu-vcl#137](https://github.com/vertical-cloud-lab/byu-vcl/issues/137#issuecomment-4811251245)).
- Two workshop speakers from the agent's
  [`SPEAKERS.md`](https://github.com/vertical-cloud-lab/structural-alloy-sdl-workshop/blob/40669a7/SPEAKERS.md).

### Borderline: an agent helped, but didn't find the contact

These would bring the count to about 10–12. Counting every vendor call takes it to about 18.

| Who | Meeting | What the agent did |
| --- | --- | --- |
| Dotov and Gu, University of Nebraska Omaha (tensegrity crutches) | [~2026-08-03](https://github.com/vertical-cloud-lab/tensegrity-optimization/pull/41#issuecomment-5171640386) | A student found them at a conference. The outreach followed the template from the agent thread |
| BYU Risk Management | [2026-07-02](https://github.com/vertical-cloud-lab/tensegrity-optimization/issues/46#issuecomment-4870263148) | Copilot named the office as the one to ask about drop tests |
| Thermo-Calc | [before 2026-10-15](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/4) | Copilot did the licensing research and cleaned up the call transcript. Thermo-Calc is now a letter-of-collaboration partner |
| NSWC Carderock | 2026-10-14 visit | Claude wrote the questions to ask ([digital-alloy-lab PR 117](https://github.com/vertical-cloud-lab/digital-alloy-lab/pull/117)) |
| Mettler-Toledo, Labman, EOS, 2OneLab and other vendors | 2026-05 to 2026-08 | Agents built the comparisons. You picked the vendors |

Left out because no agent was involved in the contact: the Texas Instruments tour, the glovebox,
vertical-lift and cleanroom vendors, the AMAZEMET rePOWDER install, Ursa Labs support calls,
the Utah AI Convergence contacts, and BYU facility staff.
