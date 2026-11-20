#!/usr/bin/env python3
"""Post an "@claude ..." comment as vcl-bot[bot] from an @claude-super run.

claude.yml lets vcl-bot[bot] start runs (``allowed_bots: vcl-bot``), so each
comment posted here starts an ordinary @claude run in the target thread.

    python3 .github/scripts/dispatch_claude.py \
        --repo vertical-cloud-lab/byu-vcl --number 353 --body-file task.md
    python3 .github/scripts/dispatch_claude.py \
        --repo vertical-cloud-lab/byu-vcl --new-issue "Security cameras" --body-file task.md

--new-issue opens a fresh issue as vcl-bot (pointing back to the parent, with
no @claude in it) and posts the task there, so a child asked to open a new PR
has a thread of its own. Both forms count toward the cap.

Checks, before posting:
- the body starts with "@claude" and contains no other workflow's tag
  (@claude-super, @claude-print, @claude-youtube, @claude-onshape-admin),
  any of which would stop claude.yml from running it;
- the target is a vertical-cloud-lab repo whose claude.yml lets vcl-bot in
  (skipped with a warning if that file can't be read);
- this run has dispatched fewer than --max comments (default 10), counted in
  a file under $RUNNER_TEMP.

Appends a footer linking back to the parent comment and run. Reads the token
from VCL_BOT_TOKEN and never prints it.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BLOCKED_TAGS = ("@claude-super", "@claude-print", "@claude-youtube", "@claude-onshape-admin")
LEDGER = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "claude-super-dispatches.json"


def gh(args, token, stdin=None):
    env = dict(os.environ, GH_TOKEN=token)
    return subprocess.run(["gh", *args], env=env, input=stdin, capture_output=True, text=True)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--repo", required=True, help="owner/name, e.g. vertical-cloud-lab/byu-vcl")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--number", type=int, help="existing PR or issue number")
    g.add_argument("--new-issue", metavar="TITLE",
                   help="open a new issue with this title as the child's thread (e.g. for a new PR)")
    p.add_argument("--body-file", required=True, type=Path)
    p.add_argument("--max", type=int, default=10, help="dispatch cap for this run (= children running at once)")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    token = os.environ.get("VCL_BOT_TOKEN", "")
    if not token:
        sys.exit("VCL_BOT_TOKEN is not set: this only works inside an @claude-super run.")
    if not re.fullmatch(r"vertical-cloud-lab/[A-Za-z0-9._-]+", a.repo):
        sys.exit(f"{a.repo}: only vertical-cloud-lab repos (vcl-bot is installed there only).")

    body = a.body_file.read_text(encoding="utf-8").strip()
    if not body.startswith("@claude"):
        sys.exit("The body must start with @claude (optionally @claude+model:effort).")
    low = body.lower()
    for tag in BLOCKED_TAGS:
        if tag in low:
            sys.exit(f"The body contains {tag}; remove it (it would stop claude.yml from running).")

    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else []
    if len(ledger) >= a.max:
        sys.exit(f"Cap reached: {len(ledger)} dispatches already. Raise --max only if Sterling's ping asked for more.")

    # Does the target's claude.yml let vcl-bot in? Read with the job's own
    # token (the App has no contents permission). Public repos always work.
    r = gh(["api", f"repos/{a.repo}/contents/.github/workflows/claude.yml",
            "-H", "Accept: application/vnd.github.raw"], os.environ.get("GH_TOKEN", ""))
    if r.returncode == 0 and "vcl-bot" not in r.stdout:
        sys.exit(f"{a.repo}'s claude.yml doesn't list vcl-bot in allowed_bots, so the comment would start nothing.")
    if r.returncode != 0:
        print(f"warning: couldn't read {a.repo}'s claude.yml; posting anyway.", file=sys.stderr)

    parent = os.environ.get("PARENT_URL", "")
    run = os.environ.get("RUN_URL", "")
    footer = "\n\n---\n<sub>Handed off by a claude-super run"
    footer += f" from [this comment]({parent})" if parent else ""
    footer += f" ([run]({run}))" if run else ""
    footer += ". Reply in this thread; the parent run can't see it.</sub>"
    full = body + footer

    if a.dry_run:
        where = a.number if a.number else f"new issue '{a.new_issue}'"
        print(f"[dry run] {a.repo} {where}:\n{full}")
        return

    if a.new_issue:
        # The issue body has no @claude, so opening it starts nothing; the task
        # comment below is what starts the child.
        intro = "Thread for a task handed off by a claude-super run"
        intro += f" from [this comment]({parent})." if parent else "."
        intro += " The task is in the first comment below."
        r = gh(["api", "-X", "POST", f"repos/{a.repo}/issues", "-f", f"title={a.new_issue}",
                "-F", "body=@-", "--jq", ".number"], token, stdin=intro)
        if r.returncode != 0:
            sys.exit(f"Creating the issue failed: {r.stderr.strip()}")
        a.number = int(r.stdout.strip())

    r = gh(["api", "-X", "POST", f"repos/{a.repo}/issues/{a.number}/comments",
            "-F", "body=@-", "--jq", ".html_url"], token, stdin=full)
    if r.returncode != 0:
        sys.exit(f"Post failed: {r.stderr.strip()}")
    url = r.stdout.strip()
    ledger.append({"repo": a.repo, "number": a.number, "url": url, "new_issue": bool(a.new_issue)})
    LEDGER.write_text(json.dumps(ledger, indent=2))
    print(f"Dispatched {len(ledger)}/{a.max}: {url}")


if __name__ == "__main__":
    main()
