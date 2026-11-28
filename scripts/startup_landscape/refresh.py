#!/usr/bin/env python3
"""Fold a refresh into the per-company JSON files.

    python scripts/startup_landscape/jobs.py live            # newest live snapshot
    python scripts/startup_landscape/jobs.py build           # data/job_postings.jsonl
    python scripts/startup_landscape/refresh.py --date 2026-11-28
    python scripts/startup_landscape/analyze.py              # figures and summary.md

What it changes in data/<slug>.json:

- ``headcount``: LinkedIn member counts ("View all N employees") and size bands from
  data/linkedin_company_pages.json, which browser.py fills from Wayback captures of the
  company pages and from the one logged-out view LinkedIn served before its sign-in wall.
  Runs of identical readings keep only their first and last capture.
- ``current_openings``: rebuilt from the newest live job-board snapshot (postings with
  ``open_now``). A company with no board of its own gets LinkedIn's public job search
  (data/linkedin_jobs.json) instead. The previous snapshot moves to ``previous``.
- ``postings``: the current quarter's count of newly posted roles, recomputed from
  data/job_postings.jsonl (first seen in that quarter).
"""
import argparse
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "docs", "startup-landscape", "data")
RAW = os.path.join(DATA, "job_postings_raw")
PREVIOUS = "2026-10-10"  # the snapshot the refresh compares against (--previous)


def _ts(url):
    m = re.search(r"/web/(\d{14})", url or "")
    return m.group(1) if m else None


def _band(size):
    m = re.match(r"([\d,]+)(?:-([\d,]+))?(\+)?", (size or "").replace(" employees", ""))
    if not m:
        return None, None
    lo = int(m.group(1).replace(",", ""))
    return lo, int(m.group(2).replace(",", "")) if m.group(2) else None


def linkedin_headcount(d, pages):
    obs = sorted(pages.get("observations") or [], key=lambda o: o["date"])
    have = {_ts(h.get("source")) or h.get("source") for h in d.get("headcount") or []}
    have_dates = {(h.get("date"), h.get("value")) for h in d.get("headcount") or [] if h.get("method") == "linkedin-band"}
    # Collapse runs of the same reading: keep the first and last capture of each run.
    keep, run = [], []
    for o in obs:
        if run and (o.get("members"), o.get("size")) != (run[-1].get("members"), run[-1].get("size")):
            keep += [run[0]] + ([run[-1]] if len(run) > 1 and run[-1]["date"] != run[0]["date"] else [])
            run = []
        run.append(o)
    if run:
        keep += [run[0]] + ([run[-1]] if len(run) > 1 and run[-1]["date"] != run[0]["date"] else [])
    # A band alone is added only for a company with no counted team size at all, and then only the latest.
    counted = [o for o in keep if o.get("members")] or [h for h in d.get("headcount") or [] if h.get("value") is not None]
    from datetime import date as _d
    near = lambda a, b: abs((_d.fromisoformat(a) - _d.fromisoformat(b)).days) <= 7  # noqa: E731
    added = 0
    for o in keep:
        if not o.get("members") and (counted or o is not keep[-1]):
            continue
        if (_ts(o["source"]) or o["source"]) in have or (o["date"], o.get("members")) in have_dates:
            continue
        if any(v == o.get("members") and len(day or "") == 10 and near(day, o["date"]) for day, v in have_dates):
            continue  # the same reading from a capture a few days apart
        lo, hi = _band(o.get("size"))
        how = ("logged-out LinkedIn page, viewed through headed Chrome on a lab Pi"
               if o.get("how") == "live" else "LinkedIn company page as captured by the Wayback Machine")
        note = (f"LinkedIn 'View all {o['members']} employees'; band {o.get('size') or 'n/a'}" if o.get("members")
                else f"LinkedIn size band only ({o.get('size')}); no member count on the page")
        d.setdefault("headcount", []).append({
            "date": o["date"], "value": o.get("members"), "low": lo, "high": hi, "method": "linkedin-band",
            "note": f"{note}; {how}", "source": o["source"], "added": pages.get("refreshed")})
        added += 1
    d["headcount"].sort(key=lambda h: h.get("date") or "") if d.get("headcount") else None
    return added


def current_openings(d, rows, li, date):
    slug = d["slug"]
    snaps = sorted(f for f in os.listdir(RAW) if f.startswith(slug + ".live-"))
    prev = d.get("current_openings") or {}
    new = None
    open_vendors = {r.get("vendor") for r in (_snapshot(slug, date) or {}).values()}
    getro_only = snaps and open_vendors <= {"getro"}
    if getro_only and li:
        snaps = []  # an investor's portfolio board keeps closed roles; LinkedIn's search is the better count here
    if snaps and snaps[-1] == f"{slug}.live-{date}.json":
        # Count postings on the board, as the earlier snapshot is counted (not titles merged across postings).
        titles = _open_titles(slug, date)
        src = prev.get("source") or next((s for r in rows if r["open_now"] for s in r["sources"]), None)
        if slug == "atinary":
            src = "https://atinary.com/careers/"
        vendors = {r.get("vendor") for r in (_snapshot(slug, date) or {}).values()}
        basis = "company job board (live snapshot)"
        if vendors == {"linkedin"}:  # no board of its own: the postings come from LinkedIn's public search
            basis, src = "LinkedIn public job search, logged out, by company ID", (li or {}).get("search_url") or src
        new = {"date": date, "count": len(titles), "by_function": _by_function(titles),
               "titles": titles, "source": src, "basis": basis}
    elif li:
        cards = li.get("cards") or []
        new = {"date": date, "count": len(cards), "by_function": {}, "titles": [c["title"] for c in cards],
               "source": li["search_url"],
               "basis": "LinkedIn public job search, logged out, by company ID" if li.get("f_C") else
                        "LinkedIn public job search, logged out, by name"}
        if cards:
            import analyze
            new["by_function"] = dict(Counter(analyze.classify(c["title"]) for c in cards).most_common())
    if new is None:
        return False
    if prev and prev.get("date") != date:
        new["previous"] = {k: prev.get(k) for k in ("date", "count", "by_function", "source") if prev.get(k) is not None}
        if _snapshot(slug, PREVIOUS) is not None:  # recount the earlier snapshot the same way, so the two compare
            titles = _open_titles(slug, PREVIOUS)
            new["previous"].update({"date": PREVIOUS, "count": len(titles), "by_function": _by_function(titles),
                                    "note": f"recounted from the {PREVIOUS} live snapshot"})
    elif prev.get("previous"):
        new["previous"] = prev["previous"]
    d["current_openings"] = new
    return True


def _open_titles(slug, day):
    """Titles of the postings open in one live snapshot, general applications left out, in English."""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from jobs_report import GENERAL, translations
    en = translations()
    snap = _snapshot(slug, day) or {}
    titles = [en.get(r.get("title"), r.get("title")) or "" for r in snap.values()]
    return [re.sub(r"\s+", " ", t).strip() for t in titles if t and not GENERAL.search(t)]


def _by_function(titles):
    import analyze
    return dict(Counter(map(analyze.classify, titles)).most_common())


def quarter(day):
    return f"{day[:4]}Q{(int(day[5:7]) - 1) // 3 + 1}"


def postings_quarter(d, rows, date):
    q = quarter(date)
    n = sum(1 for r in rows if r.get("first_seen") and quarter(r["first_seen"]) == q
            and r["function"] != "general-application")
    if not rows:
        return False
    src = (d.get("current_openings") or {}).get("source")
    d["postings"] = [p for p in d.get("postings") or [] if p.get("period") != q] + [
        {"period": q, "new_postings": n, "method": "job_postings.jsonl",
         "note": f"postings first seen {q[:4]}-{int(q[-1]) * 3 - 2:02d}-01 to {date} (live boards and Wayback)",
         "source": src}]
    d["postings"].sort(key=lambda p: p.get("period") or "")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", required=True)
    ap.add_argument("--previous", default="2026-10-10", help="date of the snapshot the profiles compare against")
    ap.add_argument("--profiles-only", action="store_true")
    a = ap.parse_args()
    global PREVIOUS
    PREVIOUS = a.previous
    if a.profiles_only:
        return write_profiles(a.date, a.previous)
    pages = json.load(open(os.path.join(DATA, "linkedin_company_pages.json"), encoding="utf-8"))
    jobs = json.load(open(os.path.join(DATA, "linkedin_jobs.json"), encoding="utf-8"))
    rows = defaultdict(list)
    with open(os.path.join(DATA, "job_postings.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            rows[r["company"]].append(r)
    for name in sorted(os.listdir(DATA)):
        path = os.path.join(DATA, name)
        if not name.endswith(".json") or name.startswith("linkedin_") or "_titles_" in name:
            continue
        text = open(path, encoding="utf-8").read()
        d = json.loads(text)
        if not isinstance(d, dict) or not d.get("slug"):
            continue
        # Write back in the file's own layout so the diff shows only what changed.
        indent = next((i for i in (2, 1) if json.dumps(d, indent=i, ensure_ascii=False) == text.rstrip("\n")), 2)
        newline = "\n" if text.endswith("\n") else ""
        slug = d["slug"]
        n_hc = linkedin_headcount(d, {**(pages.get("companies", {}).get(slug) or {}), "refreshed": a.date})
        op = current_openings(d, rows.get(slug, []), (jobs.get("companies") or {}).get(slug), a.date)
        pq = postings_quarter(d, rows.get(slug, []), a.date)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(d, indent=indent, ensure_ascii=False) + newline)
        print(f"{slug}: +{n_hc} LinkedIn points; openings {'updated' if op else 'unchanged'}; "
              f"{'quarter recount' if pq else 'no postings'}")
    write_profiles(a.date, a.previous)



# --- profile pages: a generated "Update" block near the top of each companies/<slug>.md ---------------

PROFILES = os.path.join(ROOT, "docs", "startup-landscape", "companies")


def _snapshot(slug, date):
    path = os.path.join(RAW, f"{slug}.live-{date}.json")
    if not os.path.exists(path):
        return None
    key = lambda r: str(r.get("posting_id") or r.get("url")).lower()  # noqa: E731
    rows = [r for r in json.load(open(path, encoding="utf-8")) if not r.get("closed") and r.get("vendor") != "wordpress"]
    return {key(r): r for r in rows}


def _clean_title(t):
    return re.sub(r"\s+", " ", t or "").strip()


def profile_block(d, pages, li, news, date, prev_date):
    slug = d["slug"]
    lines = []
    obs = [o for o in (pages.get("observations") or []) if o.get("members")]
    new_pts = [h for h in d.get("headcount") or [] if h.get("added") == date]
    if new_pts:
        lines += ["**Team size on LinkedIn.** People listing the company, read from the company page (LinkedIn's "
                  "'View all N employees'); this counts alumni who never updated their profile and misses staff "
                  "without one.", "", "| Date | Members | Band | Source |", "| --- | --- | --- | --- |"]
        for h in sorted(new_pts, key=lambda h: h["date"]):
            band = f'{h["low"]}-{h["high"]}' if h.get("high") else (f'{h["low"]}+' if h.get("low") else "")
            src = "LinkedIn, logged out" if "web.archive.org" not in h["source"] else "Wayback"
            lines.append(f'| {h["date"]} | {h["value"] if h.get("value") is not None else "band only"} | {band} | [{src}]({h["source"]}) |')
        lines.append("")
    now, before = _snapshot(slug, date), _snapshot(slug, prev_date)
    op = d.get("current_openings") or {}
    if now is not None:
        real = lambda rs: {k: r for k, r in rs.items() if not re.search(  # noqa: E731
            r"(?i)don'?t see|general (interest|application)|open application|spontaneous|talent (pool|community)|stay up to date",
            r.get("title") or "")}
        now_r, before_r = real(now), real(before or {})
        added = [_clean_title(now_r[k]["title"]) for k in now_r if k not in before_r]
        gone = [_clean_title(before_r[k]["title"]) for k in before_r if k not in now_r]
        where = "LinkedIn's public job search" if "LinkedIn" in (op.get("basis") or "") else "its job board"
        txt = (f"**Openings.** {len(now_r)} open on {date} on [{where}]({op.get('source')}), against "
               f"{len(before_r)} on {prev_date}." if before is not None else
               f"**Openings.** {len(now_r)} open on {date} on [{where}]({op.get('source')}).")
        lines.append(txt + (f" {len(added)} new, {len(gone)} closed." if before is not None else ""))
        if before is not None and len(added) + len(gone) <= 60:
            if added:
                lines.append(f"- New since {prev_date}: " + "; ".join(sorted(set(added))) + ".")
            if gone:
                lines.append(f"- Closed since {prev_date}: " + "; ".join(sorted(set(gone))) + ".")
        lines.append("")
    if li:
        cards = li.get("cards") or []
        how = "by company ID" if li.get("f_C") else "by name"
        m = re.match(r"([\d,]+) Jobs? in", li.get("header") or "")
        total = int(m.group(1).replace(",", "")) if m else len(cards)
        if cards and total > len(cards):
            where = Counter(c.get("location") for c in cards).most_common(4)
            lines.append(f"**LinkedIn job search** ([logged out, {how}]({li['search_url']}), {li['fetched_utc'][:10]}): "
                         f"{total} postings, the same roles as its own board, listed in "
                         + ", ".join(f"{loc} ({n})" for loc, n in where) + f" among the first {len(cards)}.")
        elif cards and len(cards) > 12 and slug not in ("matlantis", "telescope-innovations"):
            where = Counter(c.get("location") for c in cards).most_common(4)
            lines.append(f"**LinkedIn job search** ([logged out, {how}]({li['search_url']}), {li['fetched_utc'][:10]}): "
                         f"{len(cards)} postings across " + ", ".join(f"{loc} ({n})" for loc, n in where) + ".")
        elif cards:
            items = "; ".join(f'{_clean_title(c["title"])} ({c.get("location") or "location n/a"}, posted {c.get("posted") or "n/a"}'
                              + (f', {c["applicants"]}' if c.get("applicants") else "") + ")" for c in cards[:12])
            more = f" and {len(cards) - 12} more" if len(cards) > 12 else ""
            lines.append(f"**LinkedIn job search** ([logged out, {how}]({li['search_url']}), {li['fetched_utc'][:10]}): "
                         f"{len(cards)} posting{'s' if len(cards) != 1 else ''}: {items}{more}.")
        else:
            lines.append(f"**LinkedIn job search** ([logged out, {how}]({li['search_url']}), {li['fetched_utc'][:10]}): "
                         "no postings.")
        lines.append("")
    for n in news:
        lines.append(f"- {n['summary']} ([source]({n['source']}))")
    if news:
        lines.append("")
    if not lines:
        return None
    head = [f"<!-- refresh:{date} -->", f"## Update, {date}", "",
            f"What changed between the first snapshot ({prev_date}) and {date}. The method is in the "
            f"[survey README](../README.md#update-{date}).", ""]
    return "\n".join(head + lines).rstrip() + f"\n<!-- /refresh:{date} -->\n"


def write_profiles(date, prev_date):
    pages = json.load(open(os.path.join(DATA, "linkedin_company_pages.json"), encoding="utf-8"))["companies"]
    jobs = json.load(open(os.path.join(DATA, "linkedin_jobs.json"), encoding="utf-8"))["companies"]
    news_path = os.path.join(DATA, f"news_{date}.json")
    news = json.load(open(news_path, encoding="utf-8")) if os.path.exists(news_path) else []
    for name in sorted(os.listdir(PROFILES)):
        slug = name[:-3]
        path = os.path.join(DATA, f"{slug}.json")
        if not os.path.exists(path):
            continue
        d = json.load(open(path, encoding="utf-8"))
        block = profile_block(d, pages.get(slug) or {}, jobs.get(slug), [n for n in news if n["slug"] == slug],
                              date, prev_date)
        md_path = os.path.join(PROFILES, name)
        md = open(md_path, encoding="utf-8").read()
        md = re.sub(rf"<!-- refresh:{date} -->.*?<!-- /refresh:{date} -->\n\n?", "", md, flags=re.S)
        if block:
            # after the title and the one-line company summary
            m = re.search(r"\A# .*?\n\n.*?\n\n", md, re.S)
            md = md[:m.end()] + block + "\n" + md[m.end():] if m else block + "\n" + md
        open(md_path, "w", encoding="utf-8").write(md)


if __name__ == "__main__":
    main()
