# Dated reminders

Comments that should be posted to an issue on a future date. The text lives here
in the repo so it is reviewable in a PR long before it goes out, the same way
`docs/meetings/*/posts/` works — this is that machinery with a date on it.

`queue.json` is the same format `.github/scripts/post_queue.py` already reads,
plus one field:

```json
{
  "id": "2026-10-22-224-valimet-reminder",
  "type": "comment",
  "issue": 224,
  "not_before": "2026-10-22",
  "body_file": "224-valimet-followup.md"
}
```

`not_before` is a UTC date; the post is skipped until it arrives. Since
`post_queue.py` also skips anything whose `<!-- queue:<id> -->` marker is already
on the target issue, running the queue daily is a no-op until something comes due
and then posts it exactly once. Nothing else about the format changes —
`{{TRANSCRIPT}}`-style link placeholders and `<!-- if-trigger -->` blocks behave
as they do for meeting posts.

## Making it fire

Nothing here runs on its own yet. `reminders-workflow.yml` is the daily cron, and
it needs a human to move it into place — the Claude GitHub App has no permission
to write to `.github/workflows/`:

```bash
git mv docs/reminders/reminders-workflow.yml .github/workflows/reminders.yml
```

Until that happens, a reminder only goes out if someone runs **Post queued
comments** manually with `queue` set to `docs/reminders/queue.json`. That still
works — `not_before` just means an early dispatch reports "not due" instead of
posting — but it depends on a person remembering, which is the thing a reminder
is supposed to fix.

## Checking a reminder before it fires

Dry-run it against a pretend date. `REMINDERS_TODAY` overrides the clock:

```bash
GH_REPO=vertical-cloud-lab/byu-vcl QUEUE=docs/reminders/queue.json \
  DRY_RUN=true REMINDERS_TODAY=2026-10-22 \
  python3 .github/scripts/post_queue.py
```

## Adding one

Write the body as a markdown file ending in its `<!-- queue:<id> -->` marker, add
an entry to `queue.json`, and dry-run it. Write the body to be read cold, a month
later, by someone who does not remember the conversation: say what the idea was
and what the next concrete step is, rather than only linking back to it.
