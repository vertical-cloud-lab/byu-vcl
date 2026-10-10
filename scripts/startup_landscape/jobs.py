#!/usr/bin/env python3
"""Job postings with their full descriptions, current and historical.

Current postings come from each company's public job-board API (the JSON its
careers page renders from). Historical postings come from Wayback Machine
captures of the same boards. Most applicant-tracking systems embed the posting
in the page as JSON (Ashby's ``window.__appData``, Greenhouse's Remix context,
Rippling's ``__NEXT_DATA__``, schema.org ``JobPosting``), so one archived page
gives the title, team, location, pay and the full description even where the
page looks like a JavaScript shell. The archived copies are gzip-encoded as
originally served; ``fetch.get`` decodes them.

    python scripts/startup_landscape/jobs.py live                 # current boards
    python scripts/startup_landscape/jobs.py history periodic-labs  # Wayback, one company
    python scripts/startup_landscape/jobs.py build                # data/job_postings.jsonl + docs

The Wayback Machine firewalls an IP that sends more than about 15 requests a
minute, for an hour or so. Everything here goes through ``fetch.get``, which
spaces requests to web.archive.org by WAYBACK_INTERVAL seconds across
processes, so run one history job at a time.
"""
import argparse
import glob
import html
import json
import os
import re
import sys
import urllib.parse
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch  # noqa: E402

WAYBACK_INTERVAL = 6.0
fetch.MIN_INTERVAL["web.archive.org"] = WAYBACK_INTERVAL

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS = os.path.join(ROOT, "docs", "startup-landscape")
RAW = os.path.join(DOCS, "data", "job_postings_raw")

# Where each company has posted jobs. "pattern" entries are Wayback CDX URL
# prefixes; "live" entries are read from the vendor's public API.
BOARDS = {
    "periodic-labs": {"live": [("ashby", "periodic-labs")], "pattern": ["jobs.ashbyhq.com/periodic-labs"]},
    "cuspai": {"live": [("ashby", "cuspai")], "pattern": ["jobs.ashbyhq.com/cuspai"]},
    "medra": {"live": [("ashby", "medraai")], "pattern": ["jobs.ashbyhq.com/medraai", "www.medra.ai/careers"]},
    "orbital-materials": {"live": [("ashby", "orbitalindustries")],
                          "pattern": ["jobs.ashbyhq.com/orbitalmaterials", "jobs.ashbyhq.com/orbitalindustries"]},
    "tetsuwan-scientific": {"live": [("ashby", "tetsuwan")], "pattern": ["jobs.ashbyhq.com/tetsuwan"]},
    "lila-sciences": {"live": [("greenhouse", "lilasciences")],
                      "pattern": ["job-boards.greenhouse.io/lilasciences", "boards.greenhouse.io/lilasciences"]},
    "citrine-informatics": {"live": [("rippling", "citrine-informatics")],
                            "pattern": ["ats.rippling.com/citrine-informatics", "citrine.io/careers",
                                        "boards.greenhouse.io/citrine", "boards.greenhouse.io/embed/job_app?for=citrine",
                                        "boards.greenhouse.io/embed/job_board?for=citrine"]},
    "dunia-innovations": {"live": [("personio", "dunia")], "pattern": ["dunia.jobs.personio.com"]},
    "chemify": {"live": [("peoplehr", "https://www.chemify.io/careers")],
                "pattern": ["chemifyltd.peoplehr.net/Pages/JobBoard/Opening.aspx", "www.chemify.io/careers"]},
    "aionics": {"live": [("wordpress", "https://aionics.io/wp-json/wp/v2/job?per_page=100")],
                "pattern": ["aionics.io/job/"]},
    "entalpic": {"live": [("notion", "entalpic.notion.site|9f29b9a6-9fb8-4050-8cd3-f9a7c1c0d057")],
                 "pattern": ["entalpic.notion.site"]},
    "matlantis": {"pattern": ["matlantis.com/careers/", "matlantis.com/en/careers"]},
    "mitra-chem": {"live": [("links", r"https://www.mitrachem.com/join-us|https://app\.trinethire\.com/companies/913890-mitra-chem/jobs/[\w-]+")],
                   "pattern": ["mitrachem.com/job/", "www.mitrachem.com/join-us", "jobs.lever.co/mitrachem",
                               "app.trinethire.com/companies/913890-mitra-chem/jobs/"]},
    "materials-nexus": {"pattern": ["www.materialsnexus.com/jobs/", "www.materialsnexus.com/careers"]},
    "kebotix": {"pattern": ["www.kebotix.com/jobs", "www.kebotix.com/careers", "boards.greenhouse.io/kebotix",
                            "boards.greenhouse.io/embed/job_app?for=kebotix", "boards.greenhouse.io/embed/job_board?for=kebotix"]},
    "polymerize": {"pattern": ["polymerize.io/company-pages/careers"]},
    "emerald-cloud-lab": {"pattern": ["www.emeraldcloudlab.com/careers", "www.emeraldcloudlab.com/company-culture/careers",
                                      "www.emeraldcloudlab.com/about/careers"]},
    "mattiq": {"pattern": ["mattiq.com/careers"]},
    "atinary": {"pattern": ["atinary.com/careers"]},
    "deep-principle": {"pattern": ["www.deepprinciple.com/join.html", "www.deepprinciple.com/cn/join.html"]},
}

# --- text helpers --------------------------------------------------------------

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+?\d[\d ()-]{8,}\d")


def clean(text):
    """Plain text with contact details removed (the survey records no contact data)."""
    text = EMAIL.sub("[email removed]", text or "")
    text = PHONE.sub("[phone removed]", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def to_text(fragment):
    if not fragment:
        return ""
    if "&lt;" in fragment and "<" not in fragment.replace("&lt;", ""):
        fragment = html.unescape(fragment)
    fragment = re.sub(r"(?i)<li[^>]*>", "\n- ", fragment)
    return clean(fetch.html_to_text(fragment))


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def json_after(body, marker):
    """Parse the JSON object that follows `marker` in a page (balanced braces)."""
    i = body.find(marker)
    if i < 0:
        return None
    i = body.find("{", i)
    depth, j, in_str, esc = 0, i, False, False
    while j < len(body):
        c = body[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(body[i:j + 1])
                except ValueError:
                    return None
        j += 1
    return None


def ld_postings(body):
    out = []
    for blob in re.findall(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', body):
        try:
            data = json.loads(blob.strip())
        except ValueError:
            continue
        for d in walk(data):
            if d.get("@type") == "JobPosting":
                out.append(d)
    return out


def _loc(v):
    if isinstance(v, list):
        return "; ".join(filter(None, (_loc(x) for x in v)))
    if isinstance(v, dict):
        a = v.get("address") or v
        if isinstance(a, dict):
            return ", ".join(filter(None, (a.get("addressLocality"), a.get("addressRegion"), a.get("addressCountry")
                                           if isinstance(a.get("addressCountry"), str) else None)))
        return v.get("name") or ""
    return v or ""


def _salary(v):
    if not isinstance(v, dict):
        return None
    val = v.get("value") or {}
    if isinstance(val, dict) and (val.get("minValue") or val.get("value")):
        return {"currency": v.get("currency"), "min": val.get("minValue") or val.get("value"),
                "max": val.get("maxValue") or val.get("value"), "interval": val.get("unitText")}
    return None


# --- parsers for one page (live or archived) -----------------------------------------

def parse_page(url, body):
    """Return a list of posting dicts found in one page (a posting page gives one,
    a board page gives the list of titles without descriptions)."""
    host = urllib.parse.urlparse(url).hostname or ""
    out = []
    if "ashbyhq.com" in host:
        data = json_after(body, "window.__appData")
        if data:
            p = data.get("posting")
            if p:
                comp = p.get("scrapeableCompensationSalarySummary") or p.get("compensationTierSummary")
                out.append({"posting_id": p.get("id"), "title": p.get("title"),
                            "team": p.get("departmentName") or p.get("teamName"),
                            "location": p.get("locationName"), "employment_type": p.get("employmentType"),
                            "published": p.get("publishedDate"), "pay_text": comp,
                            "text": to_text(p.get("descriptionHtml") or p.get("descriptionPlainText") or "")})
            for j in ((data.get("jobBoard") or {}).get("jobPostings") or []):
                out.append({"posting_id": j.get("id") or j.get("jobId"), "title": j.get("title"),
                            "team": j.get("departmentName") or j.get("teamName"), "location": j.get("locationName"),
                            "employment_type": j.get("employmentType"), "published": j.get("publishedDate"),
                            "pay_text": j.get("compensationTierSummary"), "listing_only": True})
        return out
    if "rippling.com" in host:
        data = json_after(body, '__NEXT_DATA__" type="application/json">') or json_after(body, "__NEXT_DATA__")
        best = None
        for d in walk(data or {}):
            desc = d.get("description")
            if (d.get("name") or d.get("title")) and isinstance(desc, (dict, str)) and desc:
                if isinstance(desc, dict):
                    desc = "\n".join(str(v) for v in desc.values() if isinstance(v, str))
                if not best or len(desc) > len(best[1]):
                    best = (d, desc)
        if best:
            d, desc = best
            locs = d.get("workLocations") or d.get("locations") or []
            pay = d.get("payRangeDetails") or []
            out.append({"posting_id": d.get("uuid") or d.get("id"), "title": d.get("name") or d.get("title"),
                        "team": (d.get("department") or {}).get("name") if isinstance(d.get("department"), dict) else d.get("department"),
                        "location": "; ".join(x if isinstance(x, str) else (x.get("name") or "") for x in locs),
                        "employment_type": (d.get("employmentType") or {}).get("label") if isinstance(d.get("employmentType"), dict) else d.get("employmentType"),
                        "published": d.get("createdOn") or d.get("created_at"),
                        "pay_text": json.dumps(pay) if pay else None, "text": to_text(desc)})
        for d in walk(data or {}):
            if d.get("uuid") and d.get("name") and "url" in d and not d.get("description"):
                out.append({"posting_id": d["uuid"], "title": d["name"], "listing_only": True})
        return out
    if "greenhouse.io" in host:
        data = json_after(body, "window.__remixContext")
        jp = None
        for d in walk(data or {}):
            if isinstance(d.get("jobPost"), dict):
                jp = d["jobPost"]
                break
        if jp:
            pay = jp.get("pay_ranges") or []
            out.append({"posting_id": str(jp.get("id") or jp.get("job_post_id") or ""), "title": jp.get("title"),
                        "team": jp.get("department_name"), "location": jp.get("job_post_location"),
                        "published": jp.get("published_at"),
                        "pay_text": "; ".join(f'{p.get("min")}–{p.get("max")} {p.get("currency_type", "")}'.strip()
                                              for p in pay if isinstance(p, dict)) or None,
                        "text": to_text(jp.get("content") or "")})
            return out
        m = re.search(r'(?is)<h1[^>]*class="app-title"[^>]*>(.*?)</h1>', body)
        c = re.search(r'(?is)<div id="content"[^>]*>(.*)</div>\s*(?:<div id="application"|<form)', body)
        if m:
            loc = re.search(r'(?is)<div class="location"[^>]*>(.*?)</div>', body)
            out.append({"title": to_text(m.group(1)), "location": to_text(loc.group(1)) if loc else None,
                        "text": to_text(c.group(1)) if c else to_text(body)})
            return out
    if "personio." in host:
        t = re.search(r'(?is)<h1[^>]*>(.*?)</h1>', body)
        return [{"title": to_text(t.group(1)) if t else None, "text": personio_text(body)}]
    for d in ld_postings(body):
        org = d.get("hiringOrganization") or {}
        out.append({"title": html.unescape(d.get("title") or ""), "location": _loc(d.get("jobLocation")),
                    "employment_type": d.get("employmentType") if isinstance(d.get("employmentType"), str) else
                    ", ".join(d.get("employmentType") or []),
                    "published": d.get("datePosted"), "valid_through": d.get("validThrough"),
                    "salary": _salary(d.get("baseSalary")), "org": org.get("name") if isinstance(org, dict) else None,
                    "text": to_text(d.get("description") or "")})
    if out:
        return out
    if "lever.co" in host:
        t = re.search(r'(?is)<div class="posting-headline">\s*<h2>(.*?)</h2>', body)
        cats = re.findall(r'(?is)<div class="[^"]*(location|department|commitment|workplaceTypes)[^"]*">(.*?)</div>', body)
        main = re.search(r'(?is)<div class="content">(.*?)<div class="section page-centered last-section-apply"', body)
        if t:
            c = {k: to_text(v) for k, v in cats}
            out.append({"title": to_text(t.group(1)), "location": c.get("location"), "team": c.get("department"),
                        "employment_type": c.get("commitment"), "text": to_text(main.group(1) if main else body)})
        return out
    # Company's own page (WordPress job post, careers page, PeopleHR opening).
    t = re.search(r'(?is)<h1[^>]*>(.*?)</h1>', body) or re.search(r'(?is)<title>(.*?)</title>', body)
    art = (re.search(r'(?is)<article[^>]*>(.*?)</article>', body) or re.search(r'(?is)<main[^>]*>(.*?)</main>', body))
    out.append({"title": to_text(t.group(1)) if t else None, "text": to_text(art.group(1) if art else body),
                "generic": True})
    return out


# --- live boards -------------------------------------------------------------------

def live_ashby(token):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true"
    out = []
    for j in json.loads(fetch.get(url)).get("jobs", []):
        sal = None
        for tier in (j.get("compensation") or {}).get("compensationTiers") or []:
            for c in tier.get("components") or []:
                if c.get("compensationType") == "Salary" and c.get("minValue") and not sal:
                    sal = {"currency": c.get("currencyCode"), "min": c.get("minValue"), "max": c.get("maxValue"),
                           "interval": c.get("interval")}
        out.append({"posting_id": j.get("id") or j.get("jobUrl", "").rstrip("/").rsplit("/", 1)[-1],
                    "title": j.get("title"), "team": j.get("department") or j.get("team"),
                    "location": j.get("location"), "employment_type": j.get("employmentType"),
                    "published": j.get("publishedAt"), "salary": sal,
                    "pay_text": (j.get("compensation") or {}).get("scrapeableCompensationSalarySummary"),
                    "url": j.get("jobUrl"), "text": to_text(j.get("descriptionHtml") or "")})
    return out


def live_greenhouse(token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    out = []
    for j in json.loads(fetch.get(url)).get("jobs", []):
        out.append({"posting_id": str(j.get("id")), "title": j.get("title"),
                    "team": "; ".join(d.get("name") for d in j.get("departments") or []),
                    "location": (j.get("location") or {}).get("name"), "published": j.get("first_published"),
                    "updated": j.get("updated_at"), "url": j.get("absolute_url"),
                    "text": to_text(html.unescape(j.get("content") or ""))})
    return out


def live_rippling(token):
    board = f"https://ats.rippling.com/{token}/jobs"
    ids = set(re.findall(rf"/{re.escape(token)}/jobs/([0-9a-f-]{{36}})", fetch.get(board)))
    out = []
    for i in sorted(ids):
        url = f"{board}/{i}"
        for p in parse_page(url, fetch.get(url)):
            if not p.get("listing_only"):
                out.append({**p, "posting_id": i, "url": url})
    return out


def live_personio(token):
    xml = fetch.get(f"https://{token}.jobs.personio.com/xml")
    out = []
    for pos in re.findall(r"(?s)<position>(.*?)</position>", xml):
        def f(tag):
            m = re.search(rf"(?s)<{tag}>(.*?)</{tag}>", pos)
            return html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", m.group(1))).strip() if m else None
        parts = []
        for name, value in re.findall(r"(?s)<jobDescription>\s*<name>(.*?)</name>\s*<value>(.*?)</value>", pos):
            parts.append(f"## {html.unescape(re.sub(r'<!\[CDATA\[|\]\]>', '', name)).strip()}\n"
                         + to_text(html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", value))))
        pid = f("id")
        url = f"https://{token}.jobs.personio.com/job/{pid}?language=en"
        text = clean("\n\n".join(parts)) or personio_text(fetch.get(url))
        out.append({"posting_id": pid, "title": f("name"), "team": f("department"), "location": f("office"),
                    "employment_type": f("employmentType"), "seniority": f("seniority"),
                    "years_experience": f("yearsOfExperience"), "keywords": f("keywords"),
                    "published": f("createdAt"), "url": url, "text": text})
    return out


def personio_text(body):
    """The description blocks of a Personio job page (its XML feed often leaves them empty)."""
    i = body.find("jb-description-item")
    if i < 0:
        return ""
    j = min([k for k in (body.find("<form", i), body.find("</main>", i)) if k > 0] or [len(body)])
    return to_text(body[body.rfind("<div", 0, i):j])


def live_peoplehr(careers_url):
    """Chemify's careers page lists each PeopleHR opening with its title and post date."""
    from datetime import datetime
    page = fetch.get(careers_url)
    listed = {}
    for guid, card in re.findall(r'(?s)Opening\.aspx\?v=([0-9a-f-]{36})"(.*?)</a>', page):
        t = re.search(r'(?s)text-size-large">(.*?)</div>', card)
        d = re.search(r'(?s)eyebrow-large">(.*?)</div>', card)
        try:
            when = datetime.strptime(d.group(1).strip(), "%B %d, %Y").date().isoformat() if d else None
        except ValueError:
            when = None
        listed[guid] = (to_text(t.group(1)) if t else None, when)
    out = []
    for guid in sorted(set(re.findall(r"Opening\.aspx\?v=([0-9a-f-]{36})", page))):
        url = f"https://chemifyltd.peoplehr.net/Pages/JobBoard/Opening.aspx?v={guid}"
        try:
            body = fetch.get(url)
        except Exception as err:  # noqa: BLE001
            print("skip", url, err, file=sys.stderr)
            continue
        rec = {**peoplehr(body), "posting_id": guid, "url": url}
        title, when = listed.get(guid, (None, None))
        if title:
            rec["title"] = title
        rec["published"] = when
        out.append(rec)
    return out


def peoplehr(body):
    t = re.search(r'(?is)id="[^"]*(?:lblVacancyTitle|VacancyName|JobTitle)[^"]*"[^>]*>(.*?)<', body) \
        or re.search(r"(?is)<title>(.*?)</title>", body)
    loc = re.search(r'(?is)id="[^"]*(?:Location)[^"]*"[^>]*>(.*?)<', body)
    desc = re.search(r'(?is)id="[^"]*(?:VacancyDescription|JobDescription|Description)[^"]*"[^>]*>(.*?)</div>\s*</div>', body)
    return {"title": to_text(t.group(1)) if t else None, "location": to_text(loc.group(1)) if loc else None,
            "text": to_text(desc.group(1) if desc else body)}


def live_wordpress(url):
    out = []
    for p in json.loads(fetch.get(url)):
        out.append({"posting_id": str(p.get("id")), "title": html.unescape(p["title"]["rendered"]),
                    "published": p.get("date"), "updated": p.get("modified"), "url": p.get("link"),
                    "text": to_text(p["content"]["rendered"])})
    return out


def live_links(spec):
    """'careers-page-url|link-regex': every linked posting page on a careers page, parsed generically."""
    careers_url, rx = spec.split("|", 1)
    out = []
    for url in sorted(set(re.findall(rx, fetch.get(careers_url)))):
        for p in parse_page(url, fetch.get(url)):
            out.append({**p, "posting_id": url.rstrip("/").rsplit("/", 1)[-1], "url": url})
    return out


def _notion(site, path, payload):
    return json.loads(fetch.get(f"https://{site}/api/v3/{path}", data=json.dumps(payload),
                                headers={"Content-Type": "application/json"}))


def _notion_blocks(site, page_id):
    rm = _notion(site, "loadCachedPageChunk", {"page": {"id": page_id}, "limit": 300, "cursor": {"stack": []},
                                                "chunkNumber": 0, "verticalColumns": False})["recordMap"]["block"]
    return {k: (v.get("value") or {}).get("value", v.get("value") or {}) for k, v in rm.items()}


def _notion_title(block):
    return "".join(x[0] for x in (block.get("properties") or {}).get("title") or [])


def live_notion(spec):
    """A public Notion hiring page whose roles sit in a database: 'site|page-uuid'.
    Notion's page API serves the same JSON the page renders from, no browser needed."""
    import datetime
    site, page_id = spec.split("|")
    blocks = _notion_blocks(site, page_id)
    out = []
    for b in blocks.values():
        if b.get("type") != "collection_view" or not b.get("collection_id"):
            continue
        space = b.get("space_id") or blocks[page_id].get("space_id")
        res = _notion(site, "queryCollection?src=initial_load", {
            "source": {"type": "collection", "id": b["collection_id"], "spaceId": space},
            "collectionView": {"id": b["view_ids"][0], "spaceId": space},
            "loader": {"type": "reducer", "reducers": {"collection_group_results": {"type": "results", "limit": 100}},
                       "searchQuery": "", "userTimeZone": "UTC"}})
        rm = res["recordMap"]["block"]
        for rid in res["result"]["reducerResults"]["collection_group_results"]["blockIds"]:
            row = (rm.get(rid, {}).get("value") or {})
            row = row.get("value", row)
            title = _notion_title(row)
            if not title:
                continue
            page = _notion_blocks(site, rid)
            lines = []
            for cid in (page.get(rid) or {}).get("content") or []:
                c = page.get(cid) or {}
                t = _notion_title(c)
                if t:
                    lines.append(("- " if "list" in (c.get("type") or "") else "") + t)
            ts = row.get("created_time")
            out.append({"posting_id": rid, "title": title,
                        "published": datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc).date().isoformat() if ts else None,
                        "url": f"https://{site}/{rid.replace('-', '')}", "text": clean("\n".join(lines))})
    return out


LIVE = {"notion": live_notion, "links": live_links, "ashby": live_ashby, "greenhouse": live_greenhouse, "rippling": live_rippling,
        "personio": live_personio, "peoplehr": live_peoplehr, "wordpress": live_wordpress}


def cmd_live(slugs, date):
    os.makedirs(RAW, exist_ok=True)
    for slug in slugs:
        rows = []
        for vendor, token in BOARDS.get(slug, {}).get("live", []):
            try:
                for p in LIVE[vendor](token):
                    rows.append({"company": slug, "vendor": vendor, "basis": "live", "seen": date, **p})
            except Exception as err:  # noqa: BLE001
                print(f"{slug} {vendor}: {err}", file=sys.stderr)
        if rows:
            with open(os.path.join(RAW, f"{slug}.live.json"), "w", encoding="utf-8") as fh:
                json.dump(rows, fh, indent=1, ensure_ascii=False)
        print(slug, len(rows), "live postings")


# --- Wayback history ---------------------------------------------------------------

ID_RX = [
    re.compile(r"ashbyhq\.com/[^/]+/([0-9a-f-]{36})"),
    re.compile(r"greenhouse\.io/[^/]+/jobs/(\d+)"),
    re.compile(r"[?&](?:gh_jid|token)=(\d+)"),
    re.compile(r"rippling\.com/[^/]+/jobs/([0-9a-f-]{36})"),
    re.compile(r"lever\.co/[^/]+/([0-9a-f-]{36})"),
    re.compile(r"personio\.\w+/job/(\d+)"),
    re.compile(r"Opening\.aspx\?v=([0-9a-f-]{36})", re.I),
]


def posting_key(url):
    for rx in ID_RX:
        m = rx.search(url)
        if m:
            return m.group(1).lower()
    return None


def _root(url):
    u = re.sub(r"^https?://(www\.)?", "", url.split("?")[0].split("#")[0]).rstrip("/")
    return u.replace(":80", "")


def cmd_history(slug, max_pages):
    """Wayback: every posting URL under the company's board prefixes with its first
    and last capture, the parsed posting from its earliest capture, and the board
    page itself once a quarter (which lists titles never captured on their own)."""
    os.makedirs(RAW, exist_ok=True)
    out_path = os.path.join(RAW, f"{slug}.wayback.json")
    done = (json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path)
            else {"captures": {}, "board_captures": {}, "postings": []})
    caps, board_caps = done["captures"], done.setdefault("board_captures", {})

    def save():
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(done, fh, indent=1, ensure_ascii=False)

    for pattern in BOARDS[slug]["pattern"]:
        if pattern in caps:
            continue
        try:
            caps[pattern] = fetch.cdx_urls(pattern + "*")
        except Exception as err:  # noqa: BLE001
            print(f"cdx {pattern}: {err}", file=sys.stderr)
            continue
        save()
        print(pattern, len(caps[pattern]), "urls", flush=True)
    live_ids = set()
    lp = os.path.join(RAW, f"{slug}.live.json")
    if os.path.exists(lp):
        live_ids = {str(r.get("posting_id") or "").lower() for r in json.load(open(lp, encoding="utf-8"))}
    by_key, roots = defaultdict(list), set()
    for pattern, rows in caps.items():
        for r in rows:
            url = r["original"]
            if re.search(r"\.(js|css|png|jpe?g|svg|ico|woff2?|pdf|xml)(\?|$)", url, re.I) or "/application" in url:
                continue
            k = posting_key(url)
            if not k and _root(url).startswith(_root(pattern).rstrip("/") + "/") and _root(url) != _root(pattern):
                k = _root(url)  # a company's own page per job (WordPress etc.)
            if k:
                by_key[k].append(r)
            elif _root(url) == _root(pattern):
                roots.add(_root(url))
    todo = []
    for k, rows in by_key.items():
        rows.sort(key=lambda r: r["first"])
        first, last = rows[0]["first"], max(r["last"] for r in rows)
        n = sum(r["n"] for r in rows)
        done.setdefault("spans", {})[k] = {"first": first, "last": last, "n": n, "url": rows[0]["original"]}
        todo.append((k in live_ids, first, k, rows[0]["original"], first, last, n))
    # Board pages, one capture per quarter.
    for root in sorted(roots):
        if root not in board_caps:
            try:
                rows = fetch.cdx(root, filters=("statuscode:200",), collapse="timestamp:6")
            except Exception as err:  # noqa: BLE001
                print(f"cdx {root}: {err}", file=sys.stderr)
                continue
            quarters = {}
            for r in rows:
                q = r["timestamp"][:4] + str((int(r["timestamp"][4:6]) - 1) // 3)
                quarters.setdefault(q, r)
            board_caps[root] = [(r["timestamp"], r["original"]) for r in quarters.values()]
            save()
        for ts, orig in board_caps[root]:
            todo.append((False, ts, None, orig, ts, ts, 1))
    save()
    todo.sort(key=lambda t: (t[0], t[1]))
    seen = {(p.get("posting_id") or "") + "|" + p["capture"] for p in done["postings"]}
    fetched = 0
    for is_live, ts, k, url, first, last, n in todo:
        cap = f"https://web.archive.org/web/{ts}/{url}"
        if f"{k or ''}|{cap}" in seen or is_live:
            continue  # a posting still live has its text from the API; its span is in done["spans"]
        if fetched >= max_pages:
            break
        try:
            body = fetch.get(f"https://web.archive.org/web/{ts}id_/{url}", timeout=120)
        except Exception as err:  # noqa: BLE001
            print("skip", cap, err, file=sys.stderr)
            continue
        fetched += 1
        for p in parse_page(url, body):
            rec = {"company": slug, "basis": "wayback", "capture": cap, "url": url,
                   "first_seen": first, "last_seen": last, "n_captures": n, **p}
            if k:
                rec["posting_id"] = k
            elif p.get("posting_id"):
                rec["posting_id"] = str(p["posting_id"]).lower()
                rec["board_capture"] = True
            done["postings"].append(rec)
        seen.add(f"{k or ''}|{cap}")
        save()
        print(ts, (k or "board")[:12], url[:90], flush=True)
    print(slug, "fetched", fetched, flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    lv = sub.add_parser("live")
    lv.add_argument("slugs", nargs="*")
    lv.add_argument("--date", default="2026-10-10")
    hi = sub.add_parser("history")
    hi.add_argument("slug")
    hi.add_argument("--max-pages", type=int, default=400)
    sub.add_parser("build")
    a = ap.parse_args()
    if a.cmd == "live":
        cmd_live(a.slugs or [s for s, b in BOARDS.items() if b.get("live")], a.date)
    elif a.cmd == "history":
        cmd_history(a.slug, a.max_pages)
    elif a.cmd == "build":
        import jobs_report
        jobs_report.build()


if __name__ == "__main__":
    sys.exit(main())
