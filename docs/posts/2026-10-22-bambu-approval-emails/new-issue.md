Posting for Sterling. Summary of a Claude Code session on 2026-10-22.

## Problem

Every `claude-print` run (e.g. [powder-doser#181](https://github.com/vertical-cloud-lab/powder-doser/pull/181#issuecomment-6352269111)) emails and notifies all 20 members of [`bambu-print-approvers`](https://github.com/orgs/vertical-cloud-lab/teams/bambu-print-approvers).

## Cause

The `bambu-print` environment in byu-vcl, powder-doser, robot-arms, tensegrity-optimization and caliber lists the whole team as its required reviewer. When a run waits for approval, GitHub sends a review request to every member. The workflow's "waiting for approval" comment only links to the team page and doesn't @mention it, so it adds nothing.

## What we tried

- **Disabling the team's notifications** (`notification_setting: notifications_disabled`), then [a test run](https://github.com/vertical-cloud-lab/powder-doser/actions/runs/39863448278) on powder-doser#181. Sterling still got an `approval_requested` notification, so the setting covers @team mentions only, not deployment reviews. Reverted, and the run was cancelled before anyone approved it.

## Research

- [community#14564](https://github.com/orgs/community/discussions/14564), "disable emails for deployment reviews per repository/team": open since April 2022, about 300 upvotes, no reply from GitHub staff and no working fix.
- [community#18598](https://github.com/orgs/community/discussions/18598): the same request, unanswered.
- [The Friday Deploy](https://thefridaydeploy.substack.com/p/approving-deployments-with-github): "for teams, everyone gets an email for every approval request."
- Nothing in GitHub's changelog or on Reddit. There is no per-person or per-team setting for this.

## Options considered

| Option | Why not (for now) |
| --- | --- |
| Small reviewer team (2 to 4 people) | Works, and the gate stays as strong. But only those few could approve. |
| Allowlist users in the workflow / pass the Bambu secrets conditionally | The check lives in the workflow file, and main is unprotected, so anyone with write access (28 in byu-vcl, 30 in powder-doser) could edit it out. Repo secrets are also readable from any branch. |
| Push ruleset protecting `.github/**` (as in our private course repos) | GitHub only allows push rulesets on private and internal repos. These five are public. |
| Branch ruleset requiring PRs to main, with CODEOWNERS on `.github/` | Restricts main for everyone, and people push to main directly. Declined. |
| Custom deployment protection rule (a GitHub App that approves team members automatically) | Would work and send no emails, but needs a hosted webhook receiver (e.g. a Lambda). |
| [trstringer/manual-approval](https://github.com/trstringer/manual-approval) (approve by issue comment) | Runs inside the workflow, so the same "edit it out" problem. |

## Decision

Keep the reviewer gate as it is. Approvers who don't want the emails set up an email filter (instructions below). The custom protection rule App is the option to revisit if the filters aren't enough.

## Muting the approval emails

1. Open one of the emails, which say "requested your review to deploy to an environment".
2. **Gmail:** ⋮ → *Filter messages like these*, or create a filter with the search `from:notifications@github.com "requested your review to deploy to an environment"`. Choose *Skip the Inbox* and add a label such as `bambu-print`.
   **Outlook:** create a rule for messages from `notifications@github.com` that contain that phrase, and move them to a folder.

You'll stay on the team and can still approve. The filter covers email only, so requests still show up in your github.com inbox and in GitHub Mobile. If a print is waiting on you, the person who asked will say so in the thread or message you directly.

<!-- queue:2026-10-22-bambu-approval-emails-issue -->
