# Weekly lab safety review

Every Monday at 13:00 UTC (06:00 MST), [`safety-review.yml`](../../.github/workflows/safety-review.yml)
reviews the past week across every public `vertical-cloud-lab` repo and files the report as a
byu-vcl issue labelled [`safety-review`](https://github.com/vertical-cloud-lab/byu-vcl/issues?q=label%3Asafety-review),
assigned to `sgbaird`. Each new report closes the previous one and carries its open items forward.

## Reading and answering a report

Reply on the report issue: "resolved: E-stop installed", "accepted risk, not raising again",
"wrong, that powder isn't in use". The next run reads the last three reports and every reply, and
treats your replies as decisions. Findings have stable IDs (`atomizer-class-d-extinguisher`), so
you can refer to them across weeks.

The report is an AI review that read a lot of text. Check a finding before acting on it.

## What it reads

Collected before Claude starts by
[`safety_review_collect.py`](../../.github/scripts/safety_review_collect.py), so coverage doesn't
depend on what the session thinks to look for:

- every issue, PR, comment, review comment, review, default-branch commit and Actions run updated
  in the window, in every public, unarchived org repo. The window is the last 8 days, stretched back
  to the previous report (at most 35 days) if a week was missed
- open org issues matching safety terms, whatever their age (the standing backlog)
- text-only shallow clones of recently active repos, for SOPs, hazard analyses, control code and
  workflow files, plus full file listings for spotting SDS PDFs
- the last three reports and their replies
- AirGradient air-quality data for the window (`AIRGRADIENT_API_KEY`)

Then Claude follows [`PROMPT.md`](PROMPT.md): it reads all of it, using subagents in parallel on big
weeks, checks the automation that moves hardware, compares what people do with the SOPs and SDSs on
file, rates findings with the College risk-assessment matrix, and verifies each one before
writing it up.

## What it can't do, by design

The session reads public comments, so anyone with a GitHub account can put text in front of it.
It therefore gets nothing worth hijacking:

- Its GitHub token is the job's own `GITHUB_TOKEN`, read-only (`contents`, `issues`,
  `pull-requests`, `actions`: read), not the Claude app's write token.
- Its only secret is the Claude OAuth token. The AirGradient key is passed only to the collect
  step. No tailnet, Pis, MQTT, printers or cameras.
- It writes a file, nothing more. A separate `post` job, on a fresh runner with no Claude,
  defuses every `@mention` in the report and files it with `issues: write`, the workflow's only
  write permission.

So it doesn't see private repos (`digital-wetlab-private`, `digital-alloy-lab-private`) and can't
inspect the lab's devices. Reports say when a thread points somewhere they couldn't follow.

**Reports are public.** PROMPT.md tells the session to name no people, give only a link for
anything that looks like an incident involving a person, and leave out secrets, addresses and
storage locations. One side effect: a report links the threads it cites, so those threads show
"mentioned this issue" in their timelines.

## Running and changing it

- **On demand:** Actions → *Weekly lab safety review* → *Run workflow*. Untick *File the report as an
  issue* for a dry run: the report then appears only in the run summary and the `safety-review`
  artifact (still public, as this repo is).
- **What it looks for, and how the report reads:** edit [`PROMPT.md`](PROMPT.md). `@claude` runs can
  do this in a PR.
- **Cadence, model, effort, assignee, permissions:** edit the workflow (`cron`, and the `env:` block
  at the top). The Claude app can't edit `.github/workflows/`, so that is a human commit. For every
  two weeks, keep the weekly cron and add a step that exits early on odd ISO weeks.
- **Cost:** one Opus session at max effort a week, reading 100+ threads on a busy week. Lower
  `SAFETY_EFFORT` to `high` if that is too much.
