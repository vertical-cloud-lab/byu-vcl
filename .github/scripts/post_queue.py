"""Post a queue.json of issue comments / new issues with `gh`.

Queue format (paths in body_file are relative to the queue file):

    {
      "links": {"TRANSCRIPT": "docs/meetings/x/transcript.md"},
      "posts": [
        {"id": "…", "type": "issue", "key": "ISSUE_FOO", "title": "…",
         "assignees": ["…"], "body_file": "new-foo.md"},
        {"id": "…", "type": "comment", "issue": 124, "body_file": "124.md"}
      ]
    }

Placeholders in bodies:
  {{SHA}}        short commit hash of the checked-out ref
  {{<LINK>}}     blob URL at {{SHA}} for each entry in "links"
  {{<KEY>}}      "#N" of a new issue created earlier in the same queue
                 (so create issues first, then comments that reference them)

Every body must end with "<!-- queue:<id> -->". The script looks for that
marker on the target before posting, so a re-run never double-posts.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def gh(*args: str, capture: bool = True) -> str:
    result = subprocess.run(["gh", *args], check=True, text=True,
                            encoding="utf-8", errors="replace",
                            capture_output=capture)
    return result.stdout if capture else ""


def main() -> int:
    # Bodies contain non-ASCII (arrows, degree signs); keep printing them
    # readable on a cp1252 Windows console as well as the Linux runner.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    repo = os.environ["GH_REPO"]
    sha = os.environ.get("GITHUB_SHA", "")[:7]
    dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"
    queue_path = Path(os.environ["QUEUE"])
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    base = queue_path.parent

    subs: dict[str, str] = {"SHA": sha}
    for key, path in queue.get("links", {}).items():
        subs[key] = f"https://github.com/{repo}/blob/{sha}/{path}"

    def render(text: str) -> str:
        for key, value in subs.items():
            text = text.replace("{{" + key + "}}", value)
        leftover = [w for w in text.split("{{")[1:] if "}}" in w]
        if leftover:
            raise SystemExit(f"unresolved placeholder(s): {leftover}")
        return text

    def already_posted(marker: str, issue: int | None) -> bool:
        if issue is not None:
            comments = gh("api", "--paginate",
                          f"repos/{repo}/issues/{issue}/comments",
                          "--jq", ".[].body")
            return marker in comments
        found = gh("issue", "list", "--repo", repo, "--state", "all",
                   "--search", f'"{marker}" in:body', "--json", "number",
                   "--jq", ".[].number").strip()
        return bool(found)

    failures = 0
    for post in queue["posts"]:
        pid = post["id"]
        marker = f"<!-- queue:{pid} -->"
        body = render((base / post["body_file"]).read_text(encoding="utf-8"))
        if marker not in body:
            print(f"[{pid}] body is missing its marker {marker!r}; skipping")
            failures += 1
            continue

        target = post.get("issue")
        if already_posted(marker, target):
            print(f"[{pid}] already posted; skipping")
            if post["type"] == "issue" and "key" in post:
                num = gh("issue", "list", "--repo", repo, "--state", "all",
                         "--search", f'"{marker}" in:body', "--json", "number",
                         "--jq", ".[0].number").strip()
                subs[post["key"]] = f"#{num}"
            continue

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as tmp:
            tmp.write(body)
            body_path = tmp.name

        if post["type"] == "comment":
            desc = f"comment on #{target}"
            cmd = ["issue", "comment", str(target), "--repo", repo,
                   "--body-file", body_path]
        elif post["type"] == "issue":
            desc = f"new issue: {post['title']}"
            cmd = ["issue", "create", "--repo", repo, "--title", post["title"],
                   "--body-file", body_path]
            for who in post.get("assignees", []):
                cmd += ["--assignee", who]
        else:
            print(f"[{pid}] unknown type {post['type']!r}; skipping")
            failures += 1
            continue

        print(f"\n===== [{pid}] {desc} =====\n{body}")
        if dry_run:
            if post["type"] == "issue" and "key" in post:
                subs[post["key"]] = "#<new>"
            continue
        out = gh(*cmd).strip()
        print(f"[{pid}] posted: {out}")
        if post["type"] == "issue" and "key" in post:
            subs[post["key"]] = "#" + out.rstrip("/").rsplit("/", 1)[-1]

    if dry_run:
        print("\nDRY RUN: nothing was posted.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
