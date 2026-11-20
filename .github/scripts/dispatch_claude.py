#!/usr/bin/env python3
"""Plan, review and post the @claude pings an @claude-super run hands off.

claude-super.yml runs three jobs, and each uses one subcommand:

plan    (the Claude session, job "plan") records a ping in the plan file.
        Nothing is posted, and this job never sees the vcl-bot key.

            python3 .github/scripts/dispatch_claude.py plan --number 353 --body-file t1.md
            python3 .github/scripts/dispatch_claude.py plan --new-issue "Security cameras" --body-file t2.md

review  (job "review": fresh runner, code from main, no secrets, no Claude)
        re-checks the plan, writes every ping verbatim to the run summary,
        and outputs the plan's sha256.

post    (job "dispatch": waits for sgbaird's approval in the claude-super
        environment, then mints the vcl-bot token) refuses a plan whose
        sha256 differs from what review showed, posts each ping as
        vcl-bot[bot], and reports the links on the parent thread.

Each posted ping starts an ordinary @claude run (claude.yml lists vcl-bot in
allowed_bots). --new-issue first opens an issue as vcl-bot, with no @claude in
its title or body, as the thread for a child asked to open a new PR.

Checks, at every stage: vertical-cloud-lab repos only; the target's claude.yml
must list vcl-bot (skipped with a warning if unreadable); the body starts with
@claude and holds no other workflow's tag; titles hold no "@"; at most 10
pings unless the ping that started the run asked for more (--max), never more
than 20. Posting is idempotent per run: re-running the dispatch job skips
pings it already posted.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BLOCKED_TAGS = ("@claude-super", "@claude-print", "@claude-youtube", "@claude-onshape-admin")
DEFAULT_MAX = 10
HARD_MAX = 20
MAX_BODY = 60000
MAX_TITLE = 200
REPO_RE = re.compile(r"vertical-cloud-lab/[A-Za-z0-9._-]+")
BOT = "vcl-bot[bot]"


def default_plan_path():
    if os.environ.get("CLAUDE_SUPER_PLAN"):
        return Path(os.environ["CLAUDE_SUPER_PLAN"])
    return Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "claude-super" / "plan.json"


def gh(args, token, stdin=None):
    env = dict(os.environ, GH_TOKEN=token)
    return subprocess.run(["gh", *args], env=env, input=stdin, capture_output=True, text=True)


_allows = {}


def target_allows_bot(repo):
    """True/False from the target's claude.yml, or None if it can't be read."""
    if repo not in _allows:
        r = gh(["api", f"repos/{repo}/contents/.github/workflows/claude.yml",
                "-H", "Accept: application/vnd.github.raw"], os.environ.get("GH_TOKEN", ""))
        _allows[repo] = None if r.returncode != 0 else ("vcl-bot" in r.stdout)
    return _allows[repo]


def check_entry(e):
    """Problems with one plan entry, as a list of strings (empty if fine)."""
    errs = []
    if not isinstance(e, dict) or set(e) - {"repo", "number", "new_issue", "body"}:
        return ["entry must be an object with only repo, number or new_issue, and body"]
    repo, body = e.get("repo"), e.get("body")
    if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
        errs.append(f"repo {repo!r}: only vertical-cloud-lab repos")
    has_num, has_new = "number" in e, "new_issue" in e
    if has_num == has_new:
        errs.append("give exactly one of number and new_issue")
    if has_num and not (isinstance(e["number"], int) and e["number"] > 0):
        errs.append("number must be a positive integer")
    if has_new:
        t = e["new_issue"]
        if not isinstance(t, str) or not t.strip() or len(t) > MAX_TITLE or "\n" in t:
            errs.append(f"new_issue title must be one line, 1-{MAX_TITLE} characters")
        elif "@" in t:
            errs.append("new_issue title must not contain '@' (an @claude in a title starts a run on its own)")
    if not isinstance(body, str) or not body.startswith("@claude"):
        errs.append("body must start with @claude (optionally @claude+model:effort)")
    elif len(body) > MAX_BODY:
        errs.append(f"body is {len(body)} characters; the limit is {MAX_BODY}")
    else:
        low = body.lower()
        errs += [f"body contains {t}, which would stop claude.yml from running it"
                 for t in BLOCKED_TAGS if t in low]
    if not errs and target_allows_bot(repo) is False:
        errs.append(f"{repo}'s claude.yml doesn't list vcl-bot in allowed_bots, so the ping would start nothing")
    return errs


def load_plan(path):
    if not path.exists():
        return {"max": DEFAULT_MAX, "pings": []}
    plan = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or not isinstance(plan.get("pings"), list):
        sys.exit(f"{path}: not a plan file")
    return plan


def validate_plan(plan):
    errs = []
    cap = plan.get("max", DEFAULT_MAX)
    if not isinstance(cap, int) or not 1 <= cap <= HARD_MAX:
        errs.append(f"max must be 1-{HARD_MAX}, got {cap!r}")
        cap = DEFAULT_MAX
    if len(plan["pings"]) > cap:
        errs.append(f"{len(plan['pings'])} pings planned, cap is {cap}")
    for i, e in enumerate(plan["pings"], 1):
        errs += [f"ping {i}: {m}" for m in check_entry(e)]
    return errs


def target_label(e):
    if "new_issue" in e:
        return f"new issue in {e['repo']}: {e['new_issue']}"
    return f"{e['repo']}#{e['number']}"


# ---------------------------------------------------------------- plan

def cmd_plan(a):
    path = a.plan or default_plan_path()
    body = a.body_file.read_text(encoding="utf-8").strip()
    e = {"repo": a.repo, "body": body}
    if a.number is not None:
        e["number"] = a.number
    else:
        e["new_issue"] = a.new_issue.strip()
    errs = check_entry(e)
    if target_allows_bot(a.repo) is None:
        print(f"warning: couldn't read {a.repo}'s claude.yml; review will try again.", file=sys.stderr)
    if errs:
        sys.exit("Not planned:\n- " + "\n- ".join(errs))
    plan = load_plan(path)
    if a.max is not None:
        if not 1 <= a.max <= HARD_MAX:
            sys.exit(f"--max must be 1-{HARD_MAX}. Use it only if Sterling's ping named a number.")
        plan["max"] = a.max
    if len(plan["pings"]) >= plan["max"]:
        sys.exit(f"Cap reached: {plan['max']} pings planned. Raise --max only if Sterling's ping asked for more.")
    plan["pings"].append(e)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Planned {len(plan['pings'])}/{plan['max']}: {target_label(e)}. "
          "Nothing is posted until your run ends and Sterling approves.")


def cmd_list(a):
    plan = load_plan(a.plan or default_plan_path())
    for i, e in enumerate(plan["pings"], 1):
        print(f"{i}. {target_label(e)}: {e['body'][:100]!r}")
    print(f"{len(plan['pings'])}/{plan['max']} planned")


# ---------------------------------------------------------------- review

def fenced(text):
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    f = "`" * max(3, longest + 1)
    return f"{f}text\n{text}\n{f}"


def inline(text):
    return "`" + text.replace("`", "'").replace("\n", " ") + "`"


def cmd_review(a):
    raw = a.plan.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    plan = json.loads(raw)
    if not isinstance(plan, dict) or not isinstance(plan.get("pings"), list):
        sys.exit("Not a plan file.")
    errs = validate_plan(plan)
    n = len(plan["pings"])
    out = [f"## @claude-super: {n} planned ping{'s' * (n != 1)}", ""]
    if errs:
        out += ["### Failed checks, so the dispatch job will not run", ""] + [f"- {inline(m)}" for m in errs] + [""]
    else:
        out += ["Each block below is posted **verbatim** as `vcl-bot[bot]` once you approve the "
                "**dispatch** job (Review deployments, above). Each starts a plain `@claude` run "
                "with claude.yml's secrets, for up to 6 h. Reject it to post nothing.", ""]
    for i, e in enumerate(plan["pings"], 1):
        if not isinstance(e, dict):
            continue
        where = "?"
        if "number" in e and isinstance(e.get("number"), int):
            r = gh(["api", f"repos/{e.get('repo')}/issues/{e['number']}", "--jq",
                    '(if .pull_request then "PR" else "issue" end) + " " + .title'],
                   os.environ.get("GH_TOKEN", ""))
            kind_title = r.stdout.strip() if r.returncode == 0 else "(couldn't read the title)"
            where = f"{e.get('repo')}#{e['number']}, {inline(kind_title)}"
        elif "new_issue" in e:
            where = f"a **new issue** in {e.get('repo')} titled {inline(str(e['new_issue']))}"
        out += [f"### {i}. To {where}", "", fenced(str(e.get("body", ""))), ""]
    out += [f"Plan sha256: `{sha}`. The dispatch job refuses any other file."]
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    text = "\n".join(out) + "\n"
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"sha256={sha}\ncount={n}\n")
    if errs:
        sys.exit("Plan failed its checks; see the run summary.")


# ---------------------------------------------------------------- post

def existing_marker(repo, number, marker, token):
    r = gh(["api", "--paginate", f"repos/{repo}/issues/{number}/comments", "--jq",
            f'.[] | select(.user.login == "{BOT}") | select(.body | contains("{marker}")) | .html_url'], token)
    return r.stdout.strip().splitlines()[0] if r.returncode == 0 and r.stdout.strip() else None


def existing_issue(repo, marker, token):
    r = gh(["api", "-X", "GET", f"repos/{repo}/issues", "-f", f"creator={BOT}", "-f", "state=all",
            "-f", "per_page=100", "--jq", f'.[] | select(.body // "" | contains("{marker}")) | .number'], token)
    return int(r.stdout.split()[0]) if r.returncode == 0 and r.stdout.strip() else None


def cmd_post(a):
    raw = a.plan.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != a.sha256:
        sys.exit(f"Plan sha256 {sha} differs from the reviewed {a.sha256}; posting nothing.")
    plan = json.loads(raw)
    errs = validate_plan(plan)
    if errs:
        sys.exit("Plan failed its checks; posting nothing:\n- " + "\n- ".join(errs))
    token = os.environ.get("VCL_BOT_TOKEN", "")
    if not token and not a.dry_run:
        sys.exit("VCL_BOT_TOKEN is not set.")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    parent = os.environ.get("PARENT_URL", "")
    run_url = os.environ.get("RUN_URL", "")
    posted = []
    for i, e in enumerate(plan["pings"], 1):
        marker = f"<!-- claude-super run {run_id} ping {i} -->"
        footer = "\n\n---\n<sub>Handed off by a claude-super run"
        footer += f" from [this comment]({parent})" if parent else ""
        footer += f" ([run]({run_url}))" if run_url else ""
        footer += ", approved by sgbaird before posting. Reply in this thread.</sub>\n" + marker
        body = e["body"] + footer
        repo = e["repo"]
        if a.dry_run:
            print(f"[dry run] {target_label(e)}:\n{body}\n")
            continue
        number = e.get("number")
        if "new_issue" in e:
            number = existing_issue(repo, marker, token)
            if number is None:
                intro = "Thread for a task handed off by a claude-super run"
                intro += f" from [this comment]({parent})." if parent else "."
                intro += " The task is in the first comment below.\n\n" + marker
                r = gh(["api", "-X", "POST", f"repos/{repo}/issues", "-f", f"title={e['new_issue']}",
                        "-F", "body=@-", "--jq", ".number"], token, stdin=intro)
                if r.returncode != 0:
                    sys.exit(f"Creating issue {i} failed: {r.stderr.strip()}")
                number = int(r.stdout.strip())
        url = existing_marker(repo, number, marker, token)
        if url:
            print(f"{i}: already posted, {url}")
        else:
            r = gh(["api", "-X", "POST", f"repos/{repo}/issues/{number}/comments",
                    "-F", "body=@-", "--jq", ".html_url"], token, stdin=body)
            if r.returncode != 0:
                sys.exit(f"Posting ping {i} failed: {r.stderr.strip()}")
            url = r.stdout.strip()
            print(f"{i}: posted, {url}")
        posted.append((e, number, url))
    if a.dry_run or not posted:
        return

    # Report on the parent thread: links only, no ping text, so no @claude.
    p_repo, p_num = os.environ.get("PARENT_REPO"), os.environ.get("PARENT_NUMBER")
    lines = [f"Sterling approved the plan, so {len(posted)} ping{'s' * (len(posted) != 1)} went out "
             "as vcl-bot. Each starts a `claude.yml` run and reports in its own thread:", ""]
    for e, number, url in posted:
        label = e["new_issue"].replace("@", "") if "new_issue" in e else f"{e['repo']}#{number}"
        lines.append(f"- [{label}]({url})")
    report_marker = f"<!-- claude-super run {run_id} report -->"
    lines += ["", f"<sub>[run]({run_url})</sub>" if run_url else "", report_marker]
    if p_repo and p_num and not existing_marker(p_repo, int(p_num), report_marker, token):
        gh(["api", "-X", "POST", f"repos/{p_repo}/issues/{p_num}/comments", "-F", "body=@-"],
           token, stdin="\n".join(lines))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("\n".join(lines[:-1]) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("plan", help="record a ping (the Claude session)")
    pl.add_argument("--repo", default="vertical-cloud-lab/byu-vcl")
    g = pl.add_mutually_exclusive_group(required=True)
    g.add_argument("--number", type=int, help="existing PR or issue number")
    g.add_argument("--new-issue", metavar="TITLE", help="open a new issue with this title as the thread")
    pl.add_argument("--body-file", required=True, type=Path)
    pl.add_argument("--max", type=int, help=f"raise the cap (default {DEFAULT_MAX}, at most {HARD_MAX}) "
                    "only if Sterling's ping named a number")
    pl.add_argument("--plan", type=Path, help="plan file (default $CLAUDE_SUPER_PLAN)")
    pl.set_defaults(fn=cmd_plan)

    ls = sub.add_parser("list", help="show the pings planned so far")
    ls.add_argument("--plan", type=Path)
    ls.set_defaults(fn=cmd_list)

    rv = sub.add_parser("review", help="check the plan and write it to the run summary")
    rv.add_argument("--plan", type=Path, required=True)
    rv.set_defaults(fn=cmd_review)

    po = sub.add_parser("post", help="post an approved plan as vcl-bot")
    po.add_argument("--plan", type=Path, required=True)
    po.add_argument("--sha256", required=True, help="sha256 the review job showed")
    po.add_argument("--dry-run", action="store_true")
    po.set_defaults(fn=cmd_post)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
