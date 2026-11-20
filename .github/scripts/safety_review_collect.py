#!/usr/bin/env python3
"""Collect everything the weekly lab safety review reads, before Claude starts.

Run by .github/workflows/safety-review.yml. Collecting up front, without a
model in the loop, makes coverage deterministic: every issue, PR, comment,
review and default-branch commit in the window, across every public
vertical-cloud-lab repo, lands in the bundle whether or not the session thinks
to look for it. The session then reads the bundle and digs further.

Bundle layout (under --out):

    MANIFEST.md / manifest.json  window, repos, counts, coverage gaps
    index.md                     one row per active thread, keyword hits first
    activity/<repo>/<n>.md       thread header, body, comments/reviews in window
    commits/<repo>.md            default-branch commits in the window
    actions/<repo>.md            workflow runs in the window, per workflow
    backlog.md                   open org issues matching safety search terms
    previous/<n>.md              the last few safety-review reports + replies
    repos/<repo>/                shallow, text-only clones (md, py, yml, ...)
    repos/<repo>.files.txt       full file listing, including PDFs and CAD
    airgradient.md / .json       air-quality summary for the window, if keyed

Stdlib only, so it runs as `python3 -I` with nothing installed. Needs GH_TOKEN
(the job's read-only GITHUB_TOKEN is enough: everything read here is public).
AIRGRADIENT_API_KEY is optional; it is sent as a query parameter and never
printed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.github.com"
ORG = "vertical-cloud-lab"
HOME = os.environ.get("GITHUB_REPOSITORY", f"{ORG}/byu-vcl")
LABEL = "safety-review"
MAX_LOOKBACK_DAYS = 35
CLONE_IF_PUSHED_WITHIN_DAYS = 180
MAX_BODY_CHARS = 20_000
MAX_COMMENT_CHARS = 15_000

# Sparse-checkout patterns for the text-only clones (gitignore syntax, any depth).
TEXT_PATTERNS = [
    "*.md", "*.txt", "*.rst", "*.yml", "*.yaml", "*.toml", "*.cfg",
    "*.ini", "*.py", "*.ino", "*.sh", "*.c", "*.cpp", "*.h",
]  # no *.json: in these repos it is mostly bulky data and Edison task dumps

# Open-issue searches for the standing safety backlog. One query per term,
# because issue search caps boolean operators and these are cheap.
BACKLOG_TERMS = [
    "safety", "hazard", "SOP", "PPE", "\"risk assessment\"", "extinguisher",
    "respirator", "e-stop", "interlock", "fume hood", "glovebox", "SDS",
]

# A hint for ordering the index, not a filter: Claude is told to read
# everything regardless of hits.
SAFETY_RE = re.compile(
    r"\b(safe(ty)?|hazard\w*|injur\w*|burn(s|ed|ing)?|fires?|flamm\w*|explo\w*|"
    r"dust|powders?|respirat\w*|PPE|gloves?|goggles?|fume\w*|ventilat\w*|toxic\w*|"
    r"S?DS|SOPs?|e-?stops?|emergency|interlock\w*|pinch\w*|lasers?|"
    r"high[- ]?voltage|shock\w*|extension cords?|lithium|argon|nitrogen|"
    r"cylinders?|pressur\w*|inert|glove ?box\w*|molten|melt\w*|furnace\w*|"
    r"induction|overheat\w*|smoke|spill\w*|waste|chemicals?|acids?|solvents?|"
    r"unattended|overnight|ESD|static|humidity|hydrogen|class d|extinguish\w*|"
    r"incident\w*|near[- ]miss\w*|accident\w*|risk\w*)\b",
    re.I,
)

coverage_gaps: list[str] = []
api_calls = 0


def log(msg: str) -> None:
    print(msg, flush=True)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def request(url: str, headers: dict | None = None, tries: int = 4):
    """GET a URL; return (parsed JSON, response headers). Retries 5xx/rate limits."""
    global api_calls
    for attempt in range(tries):
        req = urllib.request.Request(url, headers=headers or {})
        try:
            api_calls += 1
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                return (json.loads(data) if data else None), resp.headers
        except urllib.error.HTTPError as exc:
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            remaining = exc.headers.get("X-RateLimit-Remaining") if exc.headers else None
            transient = exc.code >= 500 or exc.code == 429 or (
                exc.code == 403 and (retry_after or remaining == "0")
            )
            if transient and attempt < tries - 1:
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 20 * (attempt + 1)
                if remaining == "0" and exc.headers.get("X-RateLimit-Reset"):
                    wait = max(5, int(exc.headers["X-RateLimit-Reset"]) - int(time.time()) + 5)
                    wait = min(wait, 900)
                log(f"  HTTP {exc.code}, retrying in {wait}s")
                time.sleep(wait)
                continue
            raise
        except urllib.error.URLError:
            if attempt < tries - 1:
                time.sleep(10 * (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


def gh(path: str, params: dict | None = None):
    url = path if path.startswith("http") else API + path
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "vcl-safety-review",
    }
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return request(url, headers)


def paged(path: str, params: dict | None = None, max_pages: int = 20, note_truncation: bool = True) -> list:
    params = dict(params or {})
    params.setdefault("per_page", 100)
    out: list = []
    url: str | None = API + path + "?" + urllib.parse.urlencode(params)
    pages = 0
    while url and pages < max_pages:
        data, headers = gh(url)
        pages += 1
        if isinstance(data, dict) and "items" in data:
            data = data["items"]
        if isinstance(data, dict):  # e.g. actions runs
            data = next((v for v in data.values() if isinstance(v, list)), [])
        out.extend(data or [])
        url = None
        for part in (headers.get("Link") or "").split(","):
            if 'rel="next"' in part:
                url = part[part.find("<") + 1 : part.find(">")]
    if url and note_truncation:
        coverage_gaps.append(f"{path}: stopped after {max_pages} pages; more exist")
    return out


def safe(repo: str, what: str, fn, default):
    try:
        return fn()
    except urllib.error.HTTPError as exc:
        # 404/410: issues disabled, Actions disabled, or the like.
        if exc.code not in (404, 410):
            coverage_gaps.append(f"{repo}: {what} failed (HTTP {exc.code})")
        return default
    except Exception as exc:  # noqa: BLE001 - record and keep going
        coverage_gaps.append(f"{repo}: {what} failed ({type(exc).__name__})")
        return default


def clip(text: str | None, limit: int) -> str:
    text = (text or "").replace("\r\n", "\n").strip()
    if len(text) > limit:
        return text[:limit] + f"\n\n[... clipped at {limit} of {len(text)} characters; read the full text with gh api]"
    return text


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------
# Previous reports, and the window they imply
# --------------------------------------------------------------------------

def previous_reports(out: Path) -> list[dict]:
    issues = safe(HOME, "previous reports", lambda: paged(
        f"/repos/{HOME}/issues",
        {"labels": LABEL, "state": "all", "sort": "created", "direction": "desc", "per_page": 5},
        max_pages=1, note_truncation=False,
    ), [])
    issues = [i for i in issues if "pull_request" not in i][:3]
    for issue in issues:
        comments = safe(HOME, f"comments on #{issue['number']}", lambda: paged(
            f"/repos/{HOME}/issues/{issue['number']}/comments"), [])
        parts = [
            f"# #{issue['number']} {issue['title']}",
            f"{issue['html_url']} | state: {issue['state']} | created {issue['created_at']}",
            "",
            issue.get("body") or "",
        ]
        for c in comments:
            parts += ["", f"---\n### Reply by {c['user']['login']} at {c['created_at']}", "", c.get("body") or ""]
        write(out / "previous" / f"{issue['number']}.md", "\n".join(parts))
    return issues


# --------------------------------------------------------------------------
# Per-repo activity
# --------------------------------------------------------------------------

def issue_number(url: str | None) -> int | None:
    m = re.search(r"/(?:issues|pulls)/(\d+)$", url or "")
    return int(m.group(1)) if m else None


def collect_repo(repo: dict, since: datetime, out: Path, report_numbers: set[int]) -> dict:
    full = repo["full_name"]
    name = repo["name"]
    s = iso(since)
    log(f"- {full}")

    threads: dict[int, dict] = {}
    issues = safe(full, "issues", lambda: paged(
        f"/repos/{full}/issues",
        {"state": "all", "since": s, "sort": "updated", "direction": "desc"}), [])
    for it in issues:
        if full == HOME and it["number"] in report_numbers:
            continue
        threads[it["number"]] = {"item": it, "comments": [], "review_comments": [], "reviews": [], "files": []}

    comments = safe(full, "issue comments", lambda: paged(
        f"/repos/{full}/issues/comments", {"since": s, "sort": "updated", "direction": "asc"}), [])
    review_comments = safe(full, "review comments", lambda: paged(
        f"/repos/{full}/pulls/comments", {"since": s, "sort": "updated", "direction": "asc"}), [])

    def thread_for(n: int) -> dict | None:
        if full == HOME and n in report_numbers:
            return None
        if n not in threads:
            it = safe(full, f"issue {n}", lambda: gh(f"/repos/{full}/issues/{n}")[0], None)
            if not it:
                return None
            threads[n] = {"item": it, "comments": [], "review_comments": [], "reviews": [], "files": []}
        return threads[n]

    for c in comments:
        n = issue_number(c.get("issue_url"))
        t = thread_for(n) if n else None
        if t is not None:
            t["comments"].append(c)
    for c in review_comments:
        n = issue_number(c.get("pull_request_url"))
        t = thread_for(n) if n else None
        if t is not None:
            t["review_comments"].append(c)

    for n, t in threads.items():
        if "pull_request" not in t["item"]:
            continue
        reviews = safe(full, f"reviews on PR {n}", lambda: paged(f"/repos/{full}/pulls/{n}/reviews", max_pages=3), [])
        t["reviews"] = [r for r in reviews if (parse(r.get("submitted_at")) or since) >= since]
        t["files"] = safe(full, f"files on PR {n}", lambda: paged(f"/repos/{full}/pulls/{n}/files", max_pages=3, note_truncation=False), [])

    rows = []
    for n, t in sorted(threads.items(), key=lambda kv: kv[1]["item"]["updated_at"], reverse=True):
        rows.append(write_thread(full, name, n, t, since, out))

    commits = safe(full, "commits", lambda: paged(f"/repos/{full}/commits", {"since": s}, max_pages=3), [])
    if commits:
        lines = [f"# Default-branch commits in {full} since {s}", ""]
        for c in commits:
            msg = (c["commit"]["message"] or "").split("\n", 1)[0]
            who = (c.get("author") or {}).get("login") or c["commit"]["author"]["name"]
            lines.append(f"- {c['commit']['author']['date']} [{c['sha'][:7]}]({c['html_url']}) {who}: {msg}")
        write(out / "commits" / f"{name}.md", "\n".join(lines))

    runs = safe(full, "workflow runs", lambda: paged(
        f"/repos/{full}/actions/runs", {"created": f">={since:%Y-%m-%d}"}, max_pages=10), [])
    if runs:
        by_wf: dict[str, list] = defaultdict(list)
        for r in runs:
            by_wf[r.get("name") or r.get("path") or "?"].append(r)
        lines = [f"# Workflow runs in {full} since {since:%Y-%m-%d}", ""]
        for wf, rs in sorted(by_wf.items(), key=lambda kv: -len(kv[1])):
            concl = Counter((r.get("conclusion") or r.get("status") or "?") for r in rs)
            events = Counter(r.get("event") for r in rs)
            lines += [f"## {wf}: {len(rs)} runs", f"conclusions {dict(concl)}; events {dict(events)}", ""]
            for r in rs[:15]:
                actor = (r.get("triggering_actor") or r.get("actor") or {}).get("login")
                lines.append(f"- {r['created_at']} {r.get('event')} by {actor}: {r.get('conclusion') or r.get('status')} {r['html_url']}")
            lines.append("")
        write(out / "actions" / f"{name}.md", "\n".join(lines))

    return {
        "repo": full,
        "threads": len(threads),
        "comments": len(comments),
        "review_comments": len(review_comments),
        "commits": len(commits),
        "workflow_runs": len(runs),
        "rows": rows,
    }


def write_thread(full: str, name: str, n: int, t: dict, since: datetime, out: Path) -> dict:
    it = t["item"]
    is_pr = "pull_request" in it
    kind = "PR" if is_pr else "Issue"
    labels = ", ".join(l["name"] for l in it.get("labels", [])) or "none"
    new_thread = (parse(it["created_at"]) or since) >= since
    in_window = len(t["comments"]) + len(t["review_comments"]) + len(t["reviews"])
    older = max(0, (it.get("comments") or 0) - len(t["comments"]))

    parts = [
        f"# {full}#{n} ({kind}): {it['title']}",
        "",
        f"- URL: {it['html_url']}",
        f"- State: {it['state']}"
        + (f" ({it.get('state_reason')})" if it.get("state_reason") else "")
        + (" | merged" if is_pr and (it.get("pull_request") or {}).get("merged_at") else ""),
        f"- Author: {it['user']['login']} | created {it['created_at']} | updated {it['updated_at']}"
        + (" | **opened in this window**" if new_thread else ""),
        f"- Labels: {labels} | assignees: {', '.join(a['login'] for a in it.get('assignees', [])) or 'none'}",
        f"- Comments in window: {in_window}; older issue comments not included: {older}"
        + (f" (read with `gh api repos/{full}/issues/{n}/comments`)" if older else ""),
        "",
        "## Body",
        "",
        clip(it.get("body"), MAX_BODY_CHARS) or "_(empty)_",
    ]
    if t["files"]:
        parts += ["", "## Files changed in this PR", ""]
        parts += [f"- {f['status']} `{f['filename']}` (+{f.get('additions', 0)}/-{f.get('deletions', 0)})" for f in t["files"]]

    events = []
    for c in t["comments"]:
        events.append((c["created_at"], f"Comment by {c['user']['login']}", c["html_url"], c.get("body"), c.get("updated_at")))
    for c in t["review_comments"]:
        where = f"`{c.get('path')}`" + (f" line {c.get('line') or c.get('original_line')}" if c.get("line") or c.get("original_line") else "")
        events.append((c["created_at"], f"Review comment by {c['user']['login']} on {where}", c["html_url"], c.get("body"), c.get("updated_at")))
    for r in t["reviews"]:
        if r.get("body") or r.get("state") in ("APPROVED", "CHANGES_REQUESTED"):
            events.append((r["submitted_at"], f"Review ({r.get('state')}) by {(r.get('user') or {}).get('login')}", r.get("html_url"), r.get("body"), None))
    events.sort(key=lambda e: e[0] or "")
    if events:
        parts += ["", "## Activity in the window", ""]
        for created, who, url, body, updated in events:
            edited = f" (edited {updated})" if updated and updated != created else ""
            parts += [f"### {created} {who}{edited}", url or "", "", clip(body, MAX_COMMENT_CHARS) or "_(no text)_", ""]

    text = "\n".join(parts)
    rel = Path("activity") / name / f"{n}.md"
    write(out / rel, text)
    hits = Counter(m.group(0).lower() for m in SAFETY_RE.finditer(text))
    return {
        "ref": f"{name}#{n}",
        "kind": kind,
        "state": it["state"],
        "title": it["title"],
        "new": new_thread,
        "events": in_window,
        "hits": sum(hits.values()),
        "top_terms": ", ".join(k for k, _ in hits.most_common(5)),
        "file": str(rel).replace("\\", "/"),
        "url": it["html_url"],
    }


# --------------------------------------------------------------------------
# Standing backlog, clones, AirGradient
# --------------------------------------------------------------------------

def backlog(out: Path) -> int:
    seen: dict[str, dict] = {}
    for term in BACKLOG_TERMS:
        q = f"org:{ORG} is:open {term}"
        items = safe(ORG, f"search {term}", lambda: paged("/search/issues", {"q": q, "per_page": 100}, max_pages=1, note_truncation=False), [])
        for it in items:
            entry = seen.setdefault(it["html_url"], {"item": it, "terms": []})
            entry["terms"].append(term.strip('"'))
        time.sleep(2.5)  # search API: 30 requests/minute
    lines = [
        f"# Open issues and PRs in {ORG} matching safety search terms",
        "",
        "Matched regardless of recent activity: this is the standing backlog. Stale ones matter too.",
        "",
        "| Thread | Kind | Updated | Matched | Title |",
        "| --- | --- | --- | --- | --- |",
    ]
    for url, e in sorted(seen.items(), key=lambda kv: kv[1]["item"]["updated_at"], reverse=True):
        it = e["item"]
        repo = it["repository_url"].rsplit("/", 1)[-1]
        kind = "PR" if "pull_request" in it else "Issue"
        title = it["title"].replace("|", "\\|")
        lines.append(f"| [{repo}#{it['number']}]({url}) | {kind} | {it['updated_at'][:10]} | {', '.join(e['terms'])} | {title} |")
    write(out / "backlog.md", "\n".join(lines))
    return len(seen)


def clone(repo: dict, out: Path) -> bool:
    dest = out / "repos" / repo["name"]
    url = f"https://github.com/{repo['full_name']}.git"
    try:
        subprocess.run(["git", "clone", "--quiet", "--depth", "1", "--filter=blob:none", "--sparse", url, str(dest)],
                       check=True, timeout=300, capture_output=True)
        subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", "--no-cone", *TEXT_PATTERNS],
                       check=True, timeout=600, capture_output=True)
        listing = subprocess.run(["git", "-C", str(dest), "ls-tree", "-r", "--name-only", "HEAD"],
                                 check=True, timeout=120, capture_output=True, text=True).stdout
        write(out / "repos" / f"{repo['name']}.files.txt", listing)
        return True
    except Exception as exc:  # noqa: BLE001
        coverage_gaps.append(f"{repo['full_name']}: text-only clone failed ({type(exc).__name__})")
        return False


AG_API = "https://api.airgradient.com/public/api/v1"
AG_FIELDS = [
    ("pm02", "PM2.5 µg/m³"), ("pm10", "PM10 µg/m³"), ("pm01", "PM1 µg/m³"),
    ("pm003Count", "0.3 µm count/dL"), ("rco2", "CO₂ ppm"), ("tvoc_index", "TVOC index"),
    ("nox_index", "NOx index"), ("atmp", "Temp °C"), ("rhum", "RH %"),
]


def airgradient(since: datetime, now: datetime, out: Path) -> str:
    key = os.environ.get("AIRGRADIENT_API_KEY")
    if not key:
        coverage_gaps.append("AirGradient: AIRGRADIENT_API_KEY not set, so no air-quality data")
        return "skipped"

    def ag(path: str, **params):
        params["token"] = key
        url = f"{AG_API}{path}?{urllib.parse.urlencode(params)}"
        return request(url, {"Accept": "application/json", "User-Agent": "vcl-safety-review"})[0]

    try:
        current = ag("/locations/measures/current")
    except Exception as exc:  # noqa: BLE001 - never echo the URL, it carries the key
        coverage_gaps.append(f"AirGradient: current measures failed ({type(exc).__name__}"
                             + (f" {exc.code}" if isinstance(exc, urllib.error.HTTPError) else "") + ")")
        return "failed"
    current = current if isinstance(current, list) else [current]

    raw: dict = {"current": current, "past": {}}
    lines = [
        f"# AirGradient, {since:%Y-%m-%d %H:%M} to {now:%Y-%m-%d %H:%M} UTC",
        "",
        "Per location: the latest reading, then the window's distribution. Stale `latest` means the monitor",
        "is offline, which is itself a finding if it guards a powder or enclosure area. Raw rows are in",
        "airgradient.json.",
        "",
    ]
    for loc in current:
        loc_id = loc.get("locationId")
        name = loc.get("locationName") or f"location {loc_id}"
        rows: list = []
        start = since
        while start < now and loc_id is not None:
            end = min(start + timedelta(days=7), now)
            try:
                chunk = ag(f"/locations/{loc_id}/measures/past",
                           **{"from": start.strftime("%Y%m%dT%H%M%SZ"), "to": end.strftime("%Y%m%dT%H%M%SZ")})
                rows.extend(chunk if isinstance(chunk, list) else [])
            except Exception as exc:  # noqa: BLE001
                coverage_gaps.append(f"AirGradient {name}: past measures {start:%m-%d}..{end:%m-%d} failed ({type(exc).__name__})")
            start = end
        raw["past"][str(loc_id)] = rows
        lines += [f"## {name} (id {loc_id})", "", f"Latest: {loc.get('timestamp')}"]
        lines.append("; ".join(f"{label} {loc.get(k)}" for k, label in AG_FIELDS if loc.get(k) is not None) or "(no fields)")
        lines += ["", f"{len(rows)} readings in the window.", ""]
        if rows:
            lines += ["| Measure | min | median | p95 | max |", "| --- | --- | --- | --- | --- |"]
            for k, label in AG_FIELDS:
                vals = sorted(float(r[k]) for r in rows if isinstance(r.get(k), (int, float)))
                if vals:
                    p95 = vals[min(len(vals) - 1, int(0.95 * len(vals)))]
                    lines.append(f"| {label} | {vals[0]:.1f} | {statistics.median(vals):.1f} | {p95:.1f} | {vals[-1]:.1f} |")
            peak = max((r for r in rows if isinstance(r.get("pm02"), (int, float))), key=lambda r: r["pm02"], default=None)
            if peak:
                lines.append(f"\nPM2.5 peak {peak['pm02']} at {peak.get('timestamp')}.")
        lines.append("")
    write(out / "airgradient.md", "\n".join(lines))
    write(out / "airgradient.json", json.dumps(raw, indent=1))
    return f"{len(current)} locations"


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--lookback-days", type=float, default=8)
    ap.add_argument("--no-clone", action="store_true", help="skip the text-only clones")
    args = ap.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    reports = previous_reports(out)
    since = now - timedelta(days=args.lookback_days)
    if reports:
        # Reach back to the last report (with a day of overlap) if runs were missed.
        since = min(since, parse(reports[0]["created_at"]) - timedelta(days=1))
    since = max(since, now - timedelta(days=MAX_LOOKBACK_DAYS))
    log(f"Window: {iso(since)} .. {iso(now)}")

    repos = paged(f"/orgs/{ORG}/repos", {"type": "public", "sort": "pushed"})
    repos = [r for r in repos if not r.get("archived") and not r.get("disabled")]
    log(f"{len(repos)} public, unarchived repos")

    report_numbers = {r["number"] for r in reports}
    # Every labelled report, not only the last three, is excluded from activity.
    for it in safe(HOME, "all reports", lambda: paged(f"/repos/{HOME}/issues", {"labels": LABEL, "state": "all"}, max_pages=5), []):
        report_numbers.add(it["number"])

    stats = [collect_repo(r, since, out, report_numbers) for r in repos]
    n_backlog = backlog(out)

    cloned = []
    if not args.no_clone:
        recent = now - timedelta(days=CLONE_IF_PUSHED_WITHIN_DAYS)
        active = {s["repo"] for s in stats if s["threads"] or s["commits"]}
        for r in repos:
            # Forks are upstream mirrors (opentrons, BambuStudio): their docs are not the lab's.
            if r.get("fork") or r["full_name"] == HOME:
                continue
            if (parse(r.get("pushed_at")) or now) >= recent or r["full_name"] in active:
                log(f"clone {r['full_name']}")
                if clone(r, out):
                    cloned.append(r["name"])

    ag_status = airgradient(since, now, out)

    rows = [row for s in stats for row in s["rows"]]
    rows.sort(key=lambda r: (-r["hits"], -r["events"]))
    index = [
        f"# Active threads, {since:%Y-%m-%d} to {now:%Y-%m-%d}",
        "",
        "Sorted by safety-keyword hits, which are only a reading-order hint. Read every thread:",
        "the hazards that matter most are often in threads that never use the word.",
        "",
        "| Thread | Kind | State | New | Events | Hits | Top terms | Title | File |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        title = r["title"].replace("|", "\\|")
        index.append(f"| [{r['ref']}]({r['url']}) | {r['kind']} | {r['state']} | {'yes' if r['new'] else ''} | "
                     f"{r['events']} | {r['hits']} | {r['top_terms']} | {title} | `{r['file']}` |")
    write(out / "index.md", "\n".join(index))

    manifest = {
        "home": HOME,
        "since": iso(since),
        "until": iso(now),
        "previous_reports": [r["html_url"] for r in reports],
        "repos": [{k: v for k, v in s.items() if k != "rows"} for s in stats],
        "threads": len(rows),
        "backlog_matches": n_backlog,
        "cloned": cloned,
        "airgradient": ag_status,
        "api_calls": api_calls,
        "coverage_gaps": coverage_gaps,
    }
    write(out / "manifest.json", json.dumps(manifest, indent=2))
    active_stats = [s for s in stats if s["threads"] or s["commits"] or s["workflow_runs"]]
    md = [
        "# Safety review bundle",
        "",
        f"- Window: **{iso(since)}** to **{iso(now)}**",
        f"- Previous reports: {', '.join(manifest['previous_reports']) or 'none (this is the first)'}",
        f"- Repos scanned: {len(stats)} public, unarchived; {len(active_stats)} with activity",
        f"- Active threads: {len(rows)} (see index.md); standing backlog matches: {n_backlog} (backlog.md)",
        f"- Text-only clones: {', '.join(cloned) or 'none'} (repos/; full listings in repos/*.files.txt)",
        f"- AirGradient: {ag_status}",
        f"- GitHub API calls: {api_calls}",
        "",
        "| Repo | Threads | Comments | Review comments | Commits | Workflow runs |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for s in active_stats:
        md.append(f"| {s['repo']} | {s['threads']} | {s['comments']} | {s['review_comments']} | {s['commits']} | {s['workflow_runs']} |")
    md += ["", "## Coverage gaps", ""] + ([f"- {g}" for g in coverage_gaps] or ["- none"])
    write(out / "MANIFEST.md", "\n".join(md))
    log(f"Done: {len(rows)} threads, {api_calls} API calls, {len(coverage_gaps)} coverage gaps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
