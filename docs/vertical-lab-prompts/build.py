#!/usr/bin/env python3
"""Build vertical-lab-prompts.pdf from what fetch.py saved in data/.

Writes vertical-lab-prompts.html next to this file (not committed) and prints
it to PDF with the system's Chrome through Playwright, so links stay live and
the PDF gets an outline (bookmarks) by day and entry.

    pip install playwright        # uses the installed Chrome; no browser download
    python3 docs/vertical-lab-prompts/build.py

The last entry is the request for this log; it links to the PR opened from
PROMPT_LOG_BRANCH (default claude/vertical-lab-prompt-log).
"""
from __future__ import annotations

import html
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
LOG = json.loads((HERE / "data" / "log.json").read_text())
OUT_HTML = HERE / "vertical-lab-prompts.html"
OUT_PDF = HERE / "vertical-lab-prompts.pdf"
MT = ZoneInfo("America/Denver")
REPO_URL = f"https://github.com/{LOG['repo']}"
THIS_BRANCH = os.environ.get("PROMPT_LOG_BRANCH", "claude/vertical-lab-prompt-log")
TITLE = "Building the vertical cloud lab, prompt by prompt"
MAX_VIDEOS = 8

# Context the replies themselves don't carry, keyed by reply comment id.
NOTES = {
    6646281962: "GitHub shut the runner down mid-run; the reply of 5 Nov, 15:29 UTC, explains why.",
    6648715991: "GitHub shut the runner down mid-run; the reply of 5 Nov, 15:29 UTC, explains why.",
    7123165202: "Sterling cancelled it to ask for the same work in a new PR (the next entry).",
}

esc = html.escape


def when(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def local(s: str) -> datetime:
    return when(s).astimezone(MT)


def stamp(s: str) -> str:
    t = local(s)
    return f"{t:%-d %b %Y}, {t:%H:%M} {t.tzname()} ({when(s):%H:%M} UTC)"


def day_title(t: datetime) -> str:
    return f"{t:%A} {t:%-d %B %Y}"


def duration(minutes: int | None) -> str:
    if minutes is None:
        return ""
    h, m = divmod(int(minutes), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def words(md: str) -> int:
    text = re.sub(r"<[^>]+>|https?://\S+", " ", md or "")
    return len(re.findall(r"[A-Za-z0-9][\w'’.-]*", text))


def opening(md: str, n: int = 16) -> str:
    text = re.sub(r"<[^>]+>", " ", md or "")
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\(\s*https?://[^)\s]+\s*\)", " (link)", text)
    text = re.sub(r"https?://\S+", "(link)", text)
    text = re.sub(r"^\s*>.*$", "", text, flags=re.M)          # quoted lines
    text = re.sub(r"(?<![\w`])@claude(?:-super|:\w+)?\b,?", "", text)
    text = re.sub(r"^\s*#{1,6}\s+", "", text, flags=re.M)    # heading marks
    text = re.sub(r"[*_`>|]", " ", text)
    ws = text.split()
    return " ".join(ws[:n]) + (" …" if len(ws) > n else "")


def tidy_body(body_html: str, md: str) -> str:
    """GitHub's HTML for a comment, made to print: headings demoted so they
    stay out of the PDF outline, <details> opened, heading anchors dropped."""
    h = body_html
    if not h.strip():
        from markdown_it import MarkdownIt
        h = MarkdownIt("commonmark").enable("table").render(md or "")
    h = re.sub(r'<a id="user-content-[^"]*" class="anchor"[^>]*>.*?</a>', "", h, flags=re.S)
    h = re.sub(r"<h([1-6])\b[^>]*>", r'<div class="ch ch\1">', h)
    h = re.sub(r"</h[1-6]>", "</div>", h)
    h = re.sub(r"<details(?![^>]*\bopen\b)", "<details open", h)
    return h


def link(url: str, text: str, cls: str = "") -> str:
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{esc(url, quote=True)}"{c}>{text}</a>'


def thread_ref(n: int) -> str:
    t = LOG["threads"][str(n)]
    return link(t["url"], f"#{n}", "thread")


FIRST_LINKED: dict[int, list] = {}   # reply id -> the lab videos it is the first to link


def first_links(replies: list[dict]) -> None:
    """A video is credited to the first reply that links it, which is the run
    that announced the upload; later replies only refer back to it."""
    seen = set()
    for r in sorted(replies, key=lambda r: (r["created_at"], r["id"])):
        FIRST_LINKED[r["id"]] = [v for v in r.get("videos", []) if v["id"] not in seen]
        seen.update(v["id"] for v in r.get("videos", []))


def reply_html(r: dict, extra: str = "") -> str:
    run = r.get("run") or {}
    is_this_run = r["ended"].startswith("running")
    status = "this run, which made this PDF" if is_this_run else r["ended"]
    if run.get("minutes") is not None and not is_this_run and "in " not in status and "after" not in status:
        status += f" ({duration(run['minutes'])})"
    bits = [link(r["url"], esc(r["title"] or "the reply"), "reply-title"),
            f'<span class="meta">{esc(status)}'
            + (f' · {link(run["url"], "job run")}' if run.get("url") else "")
            + (f' · {link(r["branch"], "branch")}' if r.get("branch") else "")
            + "</span>"]
    if NOTES.get(r["id"]):
        bits.append(f'<div class="note">{esc(NOTES[r["id"]])}</div>')
    rows = []
    vids = FIRST_LINKED.get(r["id"], [])
    if vids:
        shown = "; ".join(link(v["url"], esc(v["title"])) for v in vids[:MAX_VIDEOS])
        more = f"; and {len(vids) - MAX_VIDEOS} more, listed in the reply" if len(vids) > MAX_VIDEOS else ""
        rows.append(("New video" + ("s" if len(vids) > 1 else ""), shown + esc(more)))
    opened = list(r.get("opened") or [])
    if opened:
        rows.append(("Opened", "; ".join(
            link(p["url"], f"{p['kind']} #{p['number']}") + f" {esc(p['title'])}" for p in opened)))
    if r.get("commit"):
        rows.append(("Pushed up to", link(r["commit"]["url"], f"<code>{esc(r['commit']['sha'])}</code>")))
    if is_this_run and THIS_BRANCH:
        rows.append(("Opened", link(f"{REPO_URL}/pulls?q=" + quote(f"is:pr head:{THIS_BRANCH}"), "the PR")
                     + f" from <code>{esc(THIS_BRANCH)}</code>, with this PDF, its data and the scripts ("
                     + link(f"{REPO_URL}/tree/{THIS_BRANCH}/docs/vertical-lab-prompts", "files") + ")"))
    if rows:
        bits.append('<table class="outs">' + "".join(
            f"<tr><th>{esc(k)}</th><td>{v}</td></tr>" for k, v in rows) + "</table>")
    thumb = ""
    if r.get("thumb"):
        thumb = (f'<a class="thumb" href="{esc(r["figure"], quote=True)}">'
                 f'<img src="{esc(r["thumb"], quote=True)}" alt="first figure of the reply"></a>')
    return f'<div class="reply">{thumb}{"".join(bits)}{extra}</div>'


def entry_html(i: int, e: dict) -> str:
    n = e["thread"]
    trig = e.get("trigger")
    kind = e["kind"]
    t = local(e["created_at"])
    head = (f'<h3 id="e{i}" class="entry-h"><span class="num">{i}</span><span class="sep"> · </span>'
            f'<span class="when">{t:%-d %b}, {t:%H:%M}</span><span class="sep"> · </span>'
            f'<span class="peek">{esc(opening(e["body_md"], 9))}</span></h3>'
            f'<div class="entry-meta">{esc(stamp(e["created_at"]))} · {thread_ref(n)} '
            f'<span class="ttl">{esc(LOG["threads"][str(n)]["title"])}</span> · {esc(kind)}'
            + (f' · <code>{esc(trig)}</code>' if trig else "")
            + (f' · edited {esc(stamp(e["updated_at"]))}' if e.get("edited") else "")
            + f' · {link(e["url"], "original comment ↗" if kind == "comment" else "original ↗")}</div>')
    body = f'<div class="body markdown-body">{tidy_body(e["body_html"], e["body_md"])}</div>'
    if e.get("reply"):
        hand = ""
        if e.get("handoffs"):
            items = []
            for h in e["handoffs"]:
                inner = reply_html(h["reply"]) if h.get("reply") else '<div class="meta">no reply found</div>'
                items.append(f'<li><div class="ho-h">{thread_ref(h["thread"])} {link(h["url"], esc(h["label"]))}</div>{inner}</li>')
            hand = ('<div class="handoffs"><div class="lbl">Handed off: Sterling approved the plan, then '
                    f'vcl-bot posted {len(e["handoffs"])} pings, each starting its own run</div>'
                    f'<ol>{"".join(items)}</ol></div>')
        out = f'<div class="outputs"><div class="lbl">What it produced</div>{reply_html(e["reply"], hand)}</div>'
    elif trig:
        out = '<div class="outputs none">No reply from a run was found for this one.</div>'
    else:
        out = '<div class="outputs none">A note, with no <code>@claude</code> in it, so no run started; later runs read the whole thread.</div>'
    return f'<section class="entry">{head}{body}{out}</section>'


def dal_html() -> str:
    parts = []
    for group in dict.fromkeys(d["group"] for d in LOG["dal"]):
        items = []
        for d in (x for x in LOG["dal"] if x["group"] == group):
            if d["what"] == "branch":
                where = "DAL branch <code>consolidation-2</code>"
            else:
                where = f"DAL {d['kind']} #{d['number']}" + (" comment" if d["what"] == "comment" else "")
            who = "Sterling" if d.get("author") == "sgbaird" else (d.get("author") or "")
            date = f"{local(d['date']):%-d %b %Y}" if d.get("date") else ""
            ctx = f' <span class="ctx">({esc(d["thread_title"])})</span>' if d.get("thread_title") and d["what"] == "comment" else ""
            items.append(f'<li>{link(d["url"], esc(d["label"]), "dal-label")} '
                         f'<span class="meta">{where} · {esc(who)} · {esc(date)}</span>{ctx}</li>')
        parts.append(f'<h3 class="dal-group">{esc(group)}</h3><ul class="dal">{"".join(items)}</ul>')
    return "".join(parts)


def main() -> None:
    entries = LOG["entries"]
    threads = LOG["threads"]
    by_thread = Counter(e["thread"] for e in entries)
    runs = [e for e in entries if e.get("reply")]
    replies = [e["reply"] for e in runs] + [h["reply"] for e in runs for h in e.get("handoffs", []) if h.get("reply")]
    first_links(replies)
    videos = {v["id"] for r in replies for v in r.get("videos", [])}
    opened = {p["number"] for r in replies for p in r.get("opened", [])}
    stopped = sum(1 for r in replies if r["ended"].startswith(("stopped", "cancelled", "run ended")))
    minutes = sum((r.get("run") or {}).get("minutes") or 0 for r in replies)
    n_words = sum(words(e["body_md"]) for e in entries)
    first, last = local(entries[0]["created_at"]), local(entries[-1]["created_at"])
    fetched = when(LOG["fetched_at"])

    # Contents
    toc_rows = []
    for i, e in enumerate(entries, 1):
        t = local(e["created_at"])
        toc_rows.append(
            f'<tr><td class="n">{link(f"#e{i}", str(i))}</td><td class="d">{t:%-d %b %H:%M}</td>'
            f'<td class="t">#{e["thread"]}</td><td>{link(f"#e{i}", esc(opening(e["body_md"])))}</td>'
            f'<td class="r">{"run" if e.get("reply") else "note"}</td></tr>')

    thread_rows = []
    for n, t in sorted(threads.items(), key=lambda kv: kv[1]["created_at"]):
        c = by_thread.get(int(n), 0)
        thread_rows.append(
            f'<tr><td>{link(t["url"], "#" + n)}</td><td>{esc(t["kind"])}, {esc(t["state"])}</td>'
            f'<td>{esc(t["title"])}</td><td class="r">{c or "–"}</td><td>{esc(t["group"])}</td></tr>')

    # Entries, by day (Mountain time)
    body, day = [], None
    for i, e in enumerate(entries, 1):
        d = local(e["created_at"]).date()
        if d != day:
            day = d
            body.append(f'<h2 class="day">{esc(day_title(local(e["created_at"])))}</h2>')
        body.append(entry_html(i, e))

    latest = None   # the newest whole-lab long-form
    for r in sorted(replies, key=lambda r: r["created_at"], reverse=True):
        longs = [v for v in r.get("videos", []) if "start to finish" in v["title"].lower()]
        if longs:
            latest = longs[0]
            break

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{esc(TITLE)}</title>
<style>{CSS}</style></head><body>
<section class="cover">
  <div class="kicker">vertical-cloud-lab/byu-vcl · issue #303 and PR #318</div>
  <div class="title">{esc(TITLE)}</div>
  <p class="sub">Every comment and prompt Sterling Baird wrote while the vertical-lab visualizations were built,
  from the first request on {first:%-d %B} to {last:%-d %B %Y}: issue {thread_ref(303)}, PR {thread_ref(318)} and the
  threads they spun off. Each is given whole, linked to the original on GitHub, and followed by what it produced:
  the reply, its job run, the videos uploaded, the PRs and issues opened and the commit pushed.
  The last part links related prompts and comments in the digital-alloy-lab repository (DAL).</p>
  <table class="stats">
    <tr><td>{len(entries)}</td><th>comments and prompts, in {len(by_thread)} threads, about {n_words:,} words</th></tr>
    <tr><td>{len(runs)}</td><th>started a run; one more prompt handed off {sum(len(e.get('handoffs', [])) for e in entries)} runs to other threads</th></tr>
    <tr><td>{stopped}</td><th>runs stopped early: out of model credits, runner shut down or cancelled</th></tr>
    <tr><td>{duration(minutes)}</td><th>of run time in all, by the job runs' own clocks</th></tr>
    <tr><td>{len(videos)}</td><th>videos on the lab's YouTube channel, each listed under the reply that first links it</th></tr>
    <tr><td>{len(opened)}</td><th>PRs and issues opened by the runs</th></tr>
    <tr><td>{len(LOG['dal'])}</td><th>related DAL prompts, comments and threads, each with a short label</th></tr>
  </table>
  {"<p class='sub'>The latest long-form: " + link(latest['url'], esc(latest['title'])) + ".</p>" if latest else ""}
  <p class="fine">Read from the GitHub API on {fetched:%-d %B %Y at %H:%M} UTC by <code>docs/vertical-lab-prompts/fetch.py</code>;
  this PDF is built by <code>build.py</code> beside it. Comments show their latest text; an edited one says when.
  Times are Mountain (the lab's), with UTC in brackets. Every link opens the original.</p>
</section>

<section class="front">
<h2>Contents</h2>
<p class="fine">Each row is one comment, in the order written. "Run" means it started a @claude run; "note" means it didn't.</p>
<table class="toc"><thead><tr><th>№</th><th>When (MT)</th><th>Thread</th><th>Opening words</th><th></th></tr></thead>
<tbody>{"".join(toc_rows)}</tbody></table>

<h2>The threads</h2>
<p class="fine">Where the comments are. "visualization" threads change the 3-D lab or its videos; "spin-off" threads start from it.
The last column but one counts Sterling's comments in each.</p>
<table class="threads"><thead><tr><th>Thread</th><th>Kind</th><th>Title</th><th>His</th><th></th></tr></thead>
<tbody>{"".join(thread_rows)}</tbody></table>
</section>

<section class="log">
<h2 class="part">The comments and prompts, in order</h2>
{"".join(body)}
</section>

<section class="dalsec">
<h2 class="part">Related prompts and comments in DAL</h2>
<p class="fine">From <a href="https://github.com/vertical-cloud-lab/digital-alloy-lab">vertical-cloud-lab/digital-alloy-lab</a>, picked by hand:
Sterling's DAL prompts that fed the vertical lab or asked for the same kind of 3-D work, then the DAL threads its models,
footage and numbers came from. Each label is 5–7 words; the line after it says where the link goes and who wrote it.</p>
{dal_html()}
</section>

<section class="howto">
<h2 class="part">How this was made</h2>
<ul>
<li><b>Which comments.</b> Every issue body, comment, review and review comment by <code>sgbaird</code> in the
{len(threads)} threads listed above. The PR body of #318 is left out: it was opened under Sterling's name from a run's link,
and Claude wrote its text. <code>fetch.py</code> warns about any newer thread that names #303 or #318 in its title.</li>
<li><b>Which reply.</b> A run posts its tracking comment within seconds of the prompt, so the reply is the next
comment by <code>claude[bot]</code> in the same thread, within five minutes. Two prompts written one second apart on 20 Nov
(entries for the retried safety and naming runs) got their replies in the other order; those two are paired by hand.
For the <code>@claude-super</code> prompt, the hand-offs are the pings <code>vcl-bot</code> posted, each paired with its own reply.</li>
<li><b>What it produced.</b> Taken from each reply: its first heading, how it ended (with the job run's own
start and end), the videos it links that are on the lab's channel (checked with YouTube's oEmbed), the PRs and
issues it names that a bot opened during the run, the commit it says it pushed up to, and a thumbnail of its first figure.</li>
<li><b>Rebuild.</b> <code>python3 docs/vertical-lab-prompts/fetch.py</code>, then <code>build.py</code>. The DAL labels
are in <code>dal_links.json</code>.</li>
</ul>
</section>
</body></html>"""
    OUT_HTML.write_text(page)
    print(f"wrote {OUT_HTML.name}: {len(entries)} entries")
    to_pdf()


def to_pdf() -> None:
    from playwright.sync_api import sync_playwright
    footer = ('<div style="font-family: Lato, sans-serif; font-size: 7.5px; color: #777; width: 100%; '
              'padding: 0 14mm; display: flex; justify-content: space-between;">'
              f'<span>{esc(TITLE)}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(OUT_HTML.as_uri(), wait_until="load")
        page.wait_for_timeout(500)
        page.pdf(path=str(OUT_PDF), format="Letter", print_background=True,
                 margin={"top": "14mm", "bottom": "15mm", "left": "14mm", "right": "14mm"},
                 display_header_footer=True, header_template="<div></div>", footer_template=footer,
                 outline=True, tagged=True)
        browser.close()
    print(f"wrote {OUT_PDF.name}: {OUT_PDF.stat().st_size / 1e6:.1f} MB")


CSS = r"""
@page { size: Letter; }
html { font-family: Lato, "DejaVu Sans", sans-serif; font-size: 9.6pt; color: #1d2330; line-height: 1.42; }
a { color: #1a56a8; text-decoration: none; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 0.86em; }
code { background: #f1f3f6; padding: 0 2px; border-radius: 2px; }
h1, h2, h3 { line-height: 1.2; }
.cover { page-break-after: always; padding-top: 30mm; }
.cover .kicker { color: #6a7385; letter-spacing: .04em; text-transform: uppercase; font-size: 8.5pt; }
.cover .title { font-size: 27pt; line-height: 1.15; margin: 6px 0 14px; font-weight: 800; color: #12213f; }
.cover .sub { font-size: 11pt; max-width: 165mm; }
.stats { margin: 16px 0 14px; border-collapse: collapse; }
.stats td { font-size: 17pt; font-weight: 800; color: #1a56a8; text-align: right; padding: 2px 12px 2px 0; white-space: nowrap; }
.stats th { text-align: left; font-weight: 400; font-size: 10.5pt; }
.fine { color: #5b6475; font-size: 8.6pt; }
.front { page-break-after: always; }
.front h2, .part { font-size: 16pt; color: #12213f; border-bottom: 2px solid #12213f; padding-bottom: 3px; }
.part { page-break-before: always; }
.log .part { page-break-before: avoid; }
table.toc, table.threads { width: 100%; border-collapse: collapse; font-size: 8.3pt; }
table.toc td, table.toc th, table.threads td, table.threads th { padding: 1.5px 5px; border-bottom: 1px solid #e4e7ec; vertical-align: top; text-align: left; }
table.toc td.n { text-align: right; width: 7mm; } table.toc td.d { white-space: nowrap; width: 22mm; }
table.toc td.t { width: 11mm; } td.r { color: #6a7385; text-align: right; white-space: nowrap; }
table.toc a { color: #1d2330; } table.toc td.n a { color: #1a56a8; }
h2.day { font-size: 12.5pt; color: #fff; background: #12213f; padding: 3px 8px; margin: 18px 0 8px; break-after: avoid; }
.entry { margin: 0 0 12px; padding-bottom: 6px; border-bottom: 1px dashed #cfd5df; }
h3.entry-h { font-size: 10.5pt; margin: 8px 0 1px; break-after: avoid; }
h3.entry-h .sep { color: #9aa3b2; font-weight: 400; }
h3.entry-h .peek { color: #4c5566; font-weight: 400; font-style: italic; }
h3.entry-h .num { display: inline-block; min-width: 20px; background: #1a56a8; color: #fff; border-radius: 3px; text-align: center; padding: 0 4px; margin-right: 4px; }
.entry-meta { color: #5b6475; font-size: 8.4pt; margin-bottom: 4px; break-after: avoid; }
.entry-meta .ttl { color: #3c4556; }
.body { border-left: 3px solid #1a56a8; padding: 1px 0 1px 9px; margin: 4px 0 6px; }
.body > :first-child { margin-top: 0; } .body > :last-child { margin-bottom: 0; }
.body p { margin: 0 0 5px; }
.body ul, .body ol { margin: 2px 0 6px; padding-left: 18px; }
.body li { margin: 1px 0; }
.body blockquote { margin: 3px 0 6px; padding: 0 0 0 8px; border-left: 3px solid #c9ced8; color: #4c5566; }
.body img { max-width: 100%; max-height: 95mm; border: 1px solid #ddd; }
.body pre { white-space: pre-wrap; word-break: break-word; background: #f4f6f8; padding: 5px; border-radius: 3px; }
.body table { border-collapse: collapse; margin: 4px 0; font-size: 8.6pt; }
.body td, .body th { border: 1px solid #d5dae2; padding: 2px 5px; }
.body .ch { font-weight: 800; margin: 6px 0 3px; } .body .ch1, .body .ch2 { font-size: 11pt; } .body .ch3 { font-size: 10.2pt; }
.body input[type=checkbox] { margin: 0 4px 0 0; } .body .contains-task-list { list-style: none; padding-left: 4px; }
markdown-accessiblity-table { display: block; }
.outputs { background: #f5f7fa; border: 1px solid #e1e5eb; border-radius: 4px; padding: 5px 8px; font-size: 8.7pt; break-inside: auto; }
.outputs.none { background: none; border: none; color: #6a7385; padding: 0 0 0 12px; font-style: italic; }
.outputs .lbl, .handoffs .lbl { font-size: 7.6pt; text-transform: uppercase; letter-spacing: .05em; color: #6a7385; margin-bottom: 2px; }
.reply { overflow: hidden; }
.reply-title { font-weight: 700; display: block; }
.meta { color: #5b6475; }
.note { color: #7a4b00; font-style: italic; }
.thumb { float: right; margin: 0 0 4px 8px; }
.thumb img { width: 52mm; max-height: 33mm; object-fit: cover; border: 1px solid #ccd2db; border-radius: 2px; }
table.outs { border-collapse: collapse; margin-top: 3px; }
table.outs th { text-align: left; vertical-align: top; color: #5b6475; font-weight: 400; padding: 1px 8px 1px 0; white-space: nowrap; }
table.outs td { padding: 1px 0; }
.handoffs { margin-top: 6px; clear: both; }
.handoffs ol { margin: 2px 0 0; padding-left: 18px; }
.handoffs li { margin: 0 0 5px; break-inside: avoid; }
.handoffs .reply { border-left: 2px solid #c9ced8; padding-left: 6px; margin-top: 1px; }
.handoffs .thumb img { width: 40mm; max-height: 24mm; }
.dal-group { font-size: 11pt; color: #12213f; margin: 12px 0 4px; break-after: avoid; }
ul.dal { margin: 0; padding-left: 16px; } ul.dal li { margin: 2px 0; break-inside: avoid; }
.dal-label { font-weight: 700; }
.ctx { color: #8a92a3; font-size: 8.2pt; }
.howto li { margin: 0 0 6px; }
"""

if __name__ == "__main__":
    main()
