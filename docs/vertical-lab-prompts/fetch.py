#!/usr/bin/env python3
"""Fetch every comment and prompt Sterling wrote while the vertical-lab
visualizations were built, the replies that answered them, and the related
DAL threads, into data/ and images/ for build.py.

The threads are byu-vcl #303 (the issue, rounds 1-3), PR #318 (rounds 4-15)
and every PR and issue spun off from them. Each of Sterling's comments is kept
whole (markdown and GitHub's own HTML rendering). Each reply is reduced to
links: the reply itself, its job run and how it ended, the videos it uploaded,
the PRs and issues it opened, the commit it pushed up to, and a thumbnail of
its first figure.

Needs `gh` signed in (any token that can read public repos) and network access
to YouTube's oEmbed endpoint, which gives each uploaded video's title and
channel. Run from anywhere:

    python3 docs/vertical-lab-prompts/fetch.py
    python3 docs/vertical-lab-prompts/build.py
"""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
IMAGES = HERE / "images"
THUMBS = HERE / "thumbs"

REPO = "vertical-cloud-lab/byu-vcl"
DAL = "vertical-cloud-lab/digital-alloy-lab"
AUTHOR = "sgbaird"
BOTS = {"claude[bot]"}
HANDOFF_BOT = "vcl-bot[bot]"
ACCEPT = "application/vnd.github.full+json"
LAB_CHANNEL = "https://www.youtube.com/@BYUVerticalCloudLab"

# The issue, the PR the conversation moved to, and every thread spun off from
# them. "visualization" threads change the 3-D lab or its videos; "spin-off"
# threads use the lab as their starting point. `discover()` warns about any
# newer thread that names #303 or #318 in its title.
THREADS = {
    303: "visualization", 318: "visualization",
    320: "visualization", 321: "visualization", 327: "visualization",
    328: "visualization", 329: "visualization", 353: "visualization",
    363: "visualization", 364: "visualization", 365: "visualization",
    366: "visualization", 367: "visualization", 368: "visualization",
    369: "visualization", 370: "visualization", 371: "visualization",
    372: "visualization", 373: "visualization", 374: "visualization",
    376: "visualization", 377: "visualization", 379: "visualization",
    331: "spin-off", 332: "spin-off", 343: "spin-off", 344: "spin-off",
}

# Issue and PR bodies opened under Sterling's name whose text Claude wrote
# (a PR opened from a run's "Create PR" link). Not his words, so left out.
NOT_HIS_TEXT = {318}

# Two prompts 1 s apart on #318 whose replies were posted in the other order.
REPLY_OVERRIDES = {
    7051716604: 7051724090,  # safety assets, retried -> "Opened #379"
    7051717032: 7051723719,  # names + colour coding, retried -> "#376 and #377"
}

YOUTUBE_ID = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})")
MD_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^)\s]+)\)")
RUN_LINK = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/actions/runs/(\d+)")
COMMIT_LINK = re.compile(
    r"\[`?([0-9a-f]{7,40})`?\]\((https://github\.com/[\w.-]+/[\w.-]+/commit/[0-9a-f]{7,40})\)")
BRANCH_LINK = re.compile(r"\[Branch\]\((https://github\.com/[^)\s]+/tree/[^)\s]+)\)")
TRIGGER = re.compile(r"(?<![\w`/])@claude(?:-super|:\w+)?\b", re.I)


# -- GitHub ----------------------------------------------------------------

def gh(path: str, paginate: bool = False, accept: str = ACCEPT):
    """`gh api`; a list for paginated calls, else the decoded object."""
    cmd = ["gh", "api", "-H", f"Accept: {accept}", path]
    if paginate:
        cmd[2:2] = ["--paginate"]
        cmd += ["--jq", ".[]"]
    for attempt in range(4):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            if paginate:
                return [json.loads(x) for x in r.stdout.splitlines() if x.strip()]
            return json.loads(r.stdout) if r.stdout.strip() else None
        if "404" in r.stderr or "Not Found" in r.stderr:
            return [] if paginate else None
        time.sleep(3 * (attempt + 1))
    sys.exit(f"gh api {path} failed: {r.stderr.strip()[:300]}")


def ts(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def fetch_thread(n: int) -> dict:
    issue = gh(f"repos/{REPO}/issues/{n}")
    comments = gh(f"repos/{REPO}/issues/{n}/comments?per_page=100", paginate=True)
    review_comments, reviews = [], []
    if issue.get("pull_request"):
        review_comments = gh(f"repos/{REPO}/pulls/{n}/comments?per_page=100", paginate=True)
        reviews = gh(f"repos/{REPO}/pulls/{n}/reviews?per_page=100", paginate=True)
    return {"issue": issue, "comments": comments,
            "review_comments": review_comments, "reviews": reviews}


def discover(all_items: list[dict]) -> None:
    for it in all_items:
        n, title = it["number"], it["title"]
        if n not in THREADS and re.search(r"#30[3]\b|#318\b", title):
            print(f"  note: #{n} names #303/#318 in its title but isn't in THREADS: {title[:80]}")


# -- Images ----------------------------------------------------------------

def download(url: str, limit: int = 40_000_000, auth: bool = False) -> bytes | None:
    headers = {"User-Agent": "vcl-prompt-log"}
    if auth:
        tok = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
        if tok:
            headers["Authorization"] = f"token {tok}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
            data = r.read(limit + 1)
    except Exception as e:  # noqa: BLE001 - a missing figure is not fatal
        print(f"  could not fetch {url[:90]}: {e}")
        return None
    return None if len(data) > limit else data


def save_images(cid: int, html: str) -> str:
    """Download each image in a comment's HTML; point the HTML at the copies."""
    srcs = []
    for m in re.finditer(r'<img[^>]+?src="([^"]+)"', html):
        if m.group(1) not in srcs:
            srcs.append(m.group(1))
    for k, src in enumerate(srcs):
        data = download(src.replace("&amp;", "&"))
        if not data:
            continue
        ext = ".png"
        if data[:3] == b"GIF":
            ext = ".gif"
        elif data[:2] == b"\xff\xd8":
            ext = ".jpg"
        name = f"{cid}-{k}{ext}"
        (IMAGES / name).write_bytes(data)
        html = html.replace(src, f"images/{name}")
    return html


def first_figure(body: str) -> str | None:
    """The first committed figure a reply shows, as a raw.githubusercontent URL."""
    for m in re.finditer(r'(?:!\[[^\]]*\]\(|<img[^>]+?src=")(https://github\.com/([\w.-]+/[\w.-]+)/blob/([^/]+)/([^)"?\s]+)(?:\?raw=true)?)', body):
        path = m.group(4)
        if path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            return f"https://raw.githubusercontent.com/{m.group(2)}/{m.group(3)}/{path}"
    return None


def thumbnail(reply_id: int, url: str) -> str | None:
    out = THUMBS / f"{reply_id}.jpg"
    if out.exists():
        return f"thumbs/{out.name}"
    data = download(url, limit=60_000_000)
    if not data:
        return None
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        im.seek(0)
        im = im.convert("RGB")
        im.thumbnail((640, 400))
        im.save(out, "JPEG", quality=82, optimize=True)
    except Exception as e:  # noqa: BLE001
        print(f"  no thumbnail for {url[:90]}: {e}")
        return None
    return f"thumbs/{out.name}"


# -- YouTube ---------------------------------------------------------------

def youtube_info(ids: set[str]) -> dict:
    cache_file = DATA / "youtube.json"
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    for vid in sorted(ids - set(cache)):
        url = ("https://www.youtube.com/oembed?format=json&url="
               + urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}", safe=""))
        data = download(url)
        try:
            d = json.loads(data) if data else {}
        except json.JSONDecodeError:
            d = {}
        cache[vid] = {"title": d.get("title"), "channel": d.get("author_name"),
                      "channel_url": d.get("author_url")}
        time.sleep(0.2)
    cache_file.write_text(json.dumps(cache, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    return cache


def is_lab_upload(info: dict) -> bool:
    """A video one of these runs uploaded: on the lab's channel and titled as
    the vertical lab (the channel's own run footage is dated, e.g. 10/27/2026)."""
    return (info.get("channel_url") == LAB_CHANNEL
            and bool(re.search(r"vertical[ -]?(?:cloud )?lab|vertical lift", info.get("title") or "", re.I)))


# -- Replies ---------------------------------------------------------------

def clean_md(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = MD_LINK.sub(r"\1", s)
    s = re.sub(r"[`*_]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def reply_title(body: str) -> str:
    for line in body.splitlines():
        if line.startswith("### "):
            return clean_md(line[4:])
    text = body.split("\n---\n", 1)[-1] if "\n---\n" in body else body
    for line in text.splitlines():
        line = clean_md(line)
        if line and not line.startswith("Claude "):
            return line if len(line) <= 220 else line[:217].rsplit(" ", 1)[0] + " …"
    return ""


def how_it_ended(body: str, run: dict | None) -> str:
    head = body.split("\n", 1)[0]
    m = re.search(r"Claude (finished|encountered an error) .*?(?:in|after) ([\dhms ]+)\*\*", head)
    if "Out of usage credits" in body:
        return f"stopped: the account ran out of model credits{' after ' + m.group(2).strip() if m else ''}"
    if m and m.group(1).startswith("encountered"):
        return f"stopped with an error after {m.group(2).strip()}"
    if run and run.get("conclusion") == "cancelled":
        return "cancelled"
    if run and run.get("conclusion") in ("failure", "timed_out"):
        return f"run ended: {run['conclusion']}"
    if run and run.get("status") != "completed":
        return "running when this was fetched"
    if m:
        return f"finished in {m.group(2).strip()}"
    return "finished"


def run_info(run_id: str | None) -> dict | None:
    if not run_id:
        return None
    r = gh(f"repos/{REPO}/actions/runs/{run_id}", accept="application/vnd.github+json")
    if not r:
        return {"id": run_id, "url": f"https://github.com/{REPO}/actions/runs/{run_id}"}
    out = {k: r.get(k) for k in ("status", "conclusion", "run_started_at", "updated_at", "name")}
    out.update(id=run_id, url=r.get("html_url"))
    if r.get("run_started_at") and r.get("updated_at"):
        out["minutes"] = round((ts(r["updated_at"]) - ts(r["run_started_at"])).total_seconds() / 60)
    return out


def describe_reply(c: dict, start: datetime, issues: dict, yt: dict) -> dict:
    body = c.get("body") or ""
    run_ids = RUN_LINK.findall(body)
    run = run_info(run_ids[0] if run_ids else None)
    end = ts(c["updated_at"])
    # PRs and issues it opened: mentioned in the reply and created during the run.
    opened = []
    for num in dict.fromkeys(int(x) for x in re.findall(r"(?:byu-vcl/(?:pull|issues)/|(?<![\w/#])#)(\d{3})\b", body)):
        it = issues.get(num)
        if it and it["user"]["login"] in BOTS | {HANDOFF_BOT} and start <= ts(it["created_at"]) <= end:
            opened.append({"number": num, "title": it["title"], "url": it["html_url"],
                           "kind": "PR" if it.get("pull_request") else "issue"})
    videos = []
    for vid in dict.fromkeys(YOUTUBE_ID.findall(body)):
        info = yt.get(vid, {})
        if is_lab_upload(info):
            videos.append({"id": vid, "title": info["title"], "url": f"https://www.youtube.com/watch?v={vid}"})
    commit = None
    m = re.search(r"(?:up to|pushed|Pushed)[^\n]{0,80}?" + COMMIT_LINK.pattern, body)
    if m:
        commit = {"sha": m.group(1)[:7], "url": m.group(2)}
    branch = BRANCH_LINK.search(body)
    fig = first_figure(body)
    return {
        "id": c["id"], "url": c["html_url"], "created_at": c["created_at"],
        "updated_at": c["updated_at"], "title": reply_title(body),
        "ended": how_it_ended(body, run), "run": run, "opened": opened,
        "videos": videos, "commit": commit,
        "branch": branch.group(1) if branch else None,
        "thumb": thumbnail(c["id"], fig) if fig else None, "figure": fig,
    }


def pair_replies(comments: list[dict]) -> dict[int, dict]:
    """Map each of Sterling's @claude comments to the tracking comment its run
    posted: the next unclaimed bot comment in the thread, within 5 minutes."""
    by_id = {c["id"]: c for c in comments}
    taken, out = set(REPLY_OVERRIDES.values()), {}
    for c in comments:
        if c["user"]["login"] != AUTHOR:
            continue
        if c["id"] in REPLY_OVERRIDES:
            out[c["id"]] = by_id[REPLY_OVERRIDES[c["id"]]]
            continue
        if not TRIGGER.search(c.get("body") or ""):
            continue
        t = ts(c["created_at"])
        for r in comments:
            if (r["user"]["login"] in BOTS and r["id"] not in taken
                    and 0 <= (ts(r["created_at"]) - t).total_seconds() <= 300):
                out[c["id"]] = r
                taken.add(r["id"])
                break
    return out


def trigger_of(body: str) -> str | None:
    m = TRIGGER.search(body or "")
    return m.group(0) if m else None


# -- DAL -------------------------------------------------------------------

def dal_links(dal_issues: dict) -> list[dict]:
    spec = json.loads((HERE / "dal_links.json").read_text())
    out = []
    for group in spec["groups"]:
        for item in group["links"]:
            url = item["url"]
            m = re.match(rf"https://github\.com/{DAL}/(?:issues|pull)/(\d+)(?:#issuecomment-(\d+))?$", url)
            rec = {"group": group["title"], "label": item["label"], "url": url}
            if m:
                num = int(m.group(1))
                it = dal_issues.get(num)
                rec.update(number=num, thread_title=it["title"] if it else None,
                           kind="PR" if it and it.get("pull_request") else "issue")
                if m.group(2):
                    c = gh(f"repos/{DAL}/issues/comments/{m.group(2)}", accept="application/vnd.github+json")
                    if not c:
                        sys.exit(f"DAL comment not found: {url}")
                    rec.update(author=c["user"]["login"], date=c["created_at"], what="comment")
                elif it:
                    rec.update(author=it["user"]["login"], date=it["created_at"], what=rec["kind"])
                else:
                    sys.exit(f"DAL thread not found: {url}")
            else:
                rec.update(what="branch", author=item.get("author"), date=item.get("date"))
            n_words = len(item["label"].split())
            if not 5 <= n_words <= 7:
                print(f"  note: label has {n_words} words: {item['label']}")
            out.append(rec)
    return out


# -- Main ------------------------------------------------------------------

def main() -> None:
    for d in (DATA, IMAGES, THUMBS):
        d.mkdir(exist_ok=True)
    print("listing byu-vcl issues and PRs")
    all_items = gh(f"repos/{REPO}/issues?state=all&per_page=100", paginate=True)
    issues = {it["number"]: it for it in all_items}
    discover(all_items)

    threads, raw = {}, {}
    for n in THREADS:
        print(f"fetching #{n}")
        raw[n] = fetch_thread(n)
        it = raw[n]["issue"]
        threads[n] = {"number": n, "title": it["title"], "url": it["html_url"],
                      "kind": "PR" if it.get("pull_request") else "issue",
                      "state": "merged" if (it.get("pull_request") or {}).get("merged_at") else it["state"],
                      "author": it["user"]["login"], "created_at": it["created_at"],
                      "group": THREADS[n]}

    # Every YouTube link in the replies, so each can be checked against the channel.
    ids = set()
    for d in raw.values():
        for c in d["comments"]:
            if c["user"]["login"] in BOTS:
                ids.update(YOUTUBE_ID.findall(c.get("body") or ""))
    print(f"looking up {len(ids)} YouTube ids")
    yt = youtube_info(ids)

    entries = []
    for n, d in raw.items():
        it = d["issue"]
        items = []
        if it["user"]["login"] == AUTHOR and n not in NOT_HIS_TEXT and (it.get("body") or "").strip():
            items.append(("issue body" if threads[n]["kind"] == "issue" else "PR body", it))
        comments = d["comments"]
        replies = pair_replies(([it] if items else []) + comments)
        items += [("comment", c) for c in comments if c["user"]["login"] == AUTHOR]
        items += [("review comment", c) for c in d["review_comments"] if c["user"]["login"] == AUTHOR]
        items += [("review", c) for c in d["reviews"] if c["user"]["login"] == AUTHOR and (c.get("body") or "").strip()]
        for kind, c in items:
            body = c.get("body") or ""
            created = c.get("created_at") or c.get("submitted_at")
            updated = c.get("updated_at") or created
            html = save_images(c["id"], c.get("body_html") or "")
            rep = replies.get(c["id"])
            entry = {
                "id": c["id"], "thread": n, "kind": kind, "url": c["html_url"],
                "created_at": created, "updated_at": updated,
                # An issue's updated_at moves with any activity, so only comments can say "edited".
                "edited": kind != "issue body" and (ts(updated) - ts(created)).total_seconds() > 120,
                "trigger": trigger_of(body), "body_md": body, "body_html": html,
                "reply": describe_reply(rep, ts(created), issues, yt) if rep else None,
                "handoffs": [],
            }
            entries.append(entry)
            print(f"  #{n} {created} {kind}: {'reply ' + str(rep['id']) if rep else 'no run'}")

    # Hand-offs: pings vcl-bot posted for a @claude-super prompt, and their replies.
    for e in entries:
        if not (e["trigger"] or "").lower().startswith("@claude-super"):
            continue
        marker = f"issuecomment-{e['id']}"
        for n, d in raw.items():
            comments = d["comments"]
            for i, c in enumerate(comments):
                body = c.get("body") or ""
                if c["user"]["login"] != HANDOFF_BOT or marker not in body or not body.startswith("@claude"):
                    continue
                letter = re.match(r"@claude \*\*\(([A-Z])\)", body)
                bold = re.match(r"@claude \*\*(.+?)\*\*", body)
                label = clean_md(bold.group(1)) if bold else threads[n]["title"]
                t = ts(c["created_at"])
                rep = None
                for r in comments[i + 1:]:
                    if r["user"]["login"] not in BOTS or (ts(r["created_at"]) - t).total_seconds() > 300:
                        continue
                    if letter and f"({letter.group(1)})" not in (r.get("body") or "")[:300]:
                        continue
                    rep = r
                    break
                e["handoffs"].append({
                    "thread": n, "url": c["html_url"], "created_at": c["created_at"],
                    "label": label[:200],
                    "reply": describe_reply(rep, t, issues, yt) if rep else None,
                })
        e["handoffs"].sort(key=lambda h: (h["thread"] != e["thread"], h["created_at"], h["thread"]))

    entries.sort(key=lambda e: (e["created_at"], e["id"]))

    print("fetching the DAL links")
    dal_items = gh(f"repos/{DAL}/issues?state=all&per_page=100", paginate=True)
    dal = dal_links({it["number"]: it for it in dal_items})

    log = {"fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "repo": REPO, "author": AUTHOR, "threads": {str(k): v for k, v in threads.items()},
           "entries": entries, "dal": dal}
    (DATA / "log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n")
    n_runs = sum(1 for e in entries if e["reply"])
    print(f"{len(entries)} entries by {AUTHOR} in {len({e['thread'] for e in entries})} threads, "
          f"{n_runs} with a run; {len(dal)} DAL links -> {DATA / 'log.json'}")


if __name__ == "__main__":
    main()
