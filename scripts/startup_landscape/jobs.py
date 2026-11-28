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
import hashlib
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
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
    "kebotix": {"pattern": ["hire.withgoogle.com/public/jobs/kebotixcom",
                            "www.kebotix.com/jobs", "www.kebotix.com/careers", "boards.greenhouse.io/kebotix",
                            "boards.greenhouse.io/embed/job_app?for=kebotix", "boards.greenhouse.io/embed/job_board?for=kebotix"]},
    "polymerize": {"pattern": ["polymerize.io/careers", "polymerize.io/company-pages/careers"]},
    "emerald-cloud-lab": {"live": [("bamboohr", "emeraldcloudlab")],
                          "pattern": ["emeraldcloudlab.bamboohr.com", "jobs.lever.co/emeraldcloudlab", "jobs.lever.co/emeraldtherapeutics",
                                      "www.emeraldcloudlab.com/careers", "www.emeraldcloudlab.com/company-culture/careers",
                                      "www.emeraldcloudlab.com/about/careers"]},
    "mattiq": {"pattern": ["mattiq.com/careers"]},
    "atinary": {"pattern": ["atinary.com/careers"]},
    "deep-principle": {"pattern": ["www.deepprinciple.com/join.html", "www.deepprinciple.com/cn/join.html"]},
    # Radical AI moved from Lever to Nodi in 2026. AlleyCorp's portfolio board (Getro) kept its Lever
    # postings after they closed; their ids were found next to the two the board still lists.
    "radical-ai": {"live": [("lever", "RadicalAI"), ("nodi", "radical ai"),
                            ("getro", "jobs.alleycorp.com|" + ",".join(
                                f"radical-ai-2-91959a92-375e-4de8-968f-29c967d9b1ee/jobs/{i}"
                                for i in [*range(73774119, 73774132), *range(81655547, 81655551)]))],
                   "pattern": ["jobs.lever.co/RadicalAI", "www.radical-ai.com/careers",
                               "jobs.alleycorp.com/companies/radical-ai-2-91959a92-375e-4de8-968f-29c967d9b1ee"]},
    "altrove": {"live": [("getro", "portfolio.joinef.com|altrove-2/jobs/94646394")],
                "pattern": ["portfolio.joinef.com/companies/altrove-2", "jobs.cventures.vc/companies/altrove-2",
                            "jobs.alven.co/companies/altrove"]},
    "intrepid-labs": {"pattern": ["jobs.entrepreneurs.utoronto.ca/companies/intrepid-labs-2-e3db58f4-bb86-403c-8430-f8d64448d0fe",
                                  "radical.getro.com/companies/intrepid-labs"]},
    "dp-technology": {"live": [("feishu", "dptechnology.jobs.feishu.cn|index,305722")],
                      "pattern": ["dptechnology.jobs.feishu.cn/index/position", "dptechnology.jobs.feishu.cn/305722/position"]},
    "telescope-innovations": {"live": [("getro", "techjobs.marsdd.com|telescope-innovations/jobs/39623303-mechatronics-engineer-"
                                                 "automated-chemistry-technology,telescope-innovations/jobs/39701379-software-"
                                                 "engineer-automated-chemistry-technology")],
                              "pattern": ["techjobs.marsdd.com/companies/telescope-innovations"]},
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
    if "peoplehr.net" in host:
        return [peoplehr(body)]
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
        # A board page: one <a class="posting-title"> per opening, with its location, team and commitment.
        for pid, name, rest in re.findall(r'(?is)<a class="posting-title" href="[^"]*/([0-9a-f-]{36})"[^>]*>\s*'
                                          r'<h5[^>]*>(.*?)</h5>(.*?)</a>', body):
            c = dict(re.findall(r'(?is)class="sort-by-(location|team|commitment)[^"]*"[^>]*>(.*?)</span>', rest))
            out.append({"posting_id": pid, "title": to_text(name), "location": to_text(c.get("location")) or None,
                        "team": to_text(c.get("team")) or None, "employment_type": to_text(c.get("commitment")) or None,
                        "listing_only": True})
        return out
    if "bamboohr.com" in host:
        # /careers/list is the JSON the careers page renders from; embed2.php is the widget companies
        # put on their own site; a posting page carries its title in og:title (the text loads client-side).
        if re.search(r"/careers/list\b", url):
            try:
                data = json.loads(body)
            except ValueError:
                return []
            for j in data.get("result") or []:
                loc, ats = j.get("location") or {}, j.get("atsLocation") or {}
                out.append({"posting_id": str(j["id"]), "title": (j.get("jobOpeningName") or "").strip(),
                            "team": re.sub(r"^\d+\s+", "", j.get("departmentLabel") or "") or None,
                            "location": ", ".join(filter(None, (loc.get("city") or ats.get("city"),
                                                                loc.get("state") or ats.get("state")))) or None,
                            "employment_type": j.get("employmentStatusLabel"), "listing_only": True})
            return out
        for pid, name in re.findall(r'(?is)<a[^>]+href="[^"]*/careers/(\d+)"[^>]*>(.*?)</a>', body):
            out.append({"posting_id": pid, "title": to_text(name), "listing_only": True})
        t = re.search(r'(?is)<meta[^>]+property="og:title"[^>]+content="([^"]*)"', body)
        if t and re.search(r"/careers/\d+|view\.php\?id=\d+", url):
            out.append({"title": html.unescape(t.group(1)).strip()})
        return out
    if "jobs.feishu.cn" in host:
        # Feishu posting pages render client-side but put the title in <title>: "药化科学家 - 加入DP Technology".
        t = re.search(r"(?is)<title[^>]*>(.*?)</title>", body)
        title = re.sub(r"\s*-\s*加入.*$", "", to_text(t.group(1)) if t else "")
        return [{"title": title, "lang": "zh"}] if title and re.search(r"/position/\d+/detail", url) else []
    if "__NEXT_DATA__" in body and '"currentJob"' in body:
        rec = getro_job(body)
        if rec:
            return [{k: v for k, v in rec.items() if k not in ("status", "last_seen")}]
    if "deepprinciple.com" in host:
        # Deep Principle lists every opening inline on join.html: the title in div.d1, the description in div.d2.
        for name, desc in re.findall(r'(?is)<div class="d1">\s*<p>(.*?)</p>.*?<div class="d2">\s*<div class="html">(.*?)</div>', body):
            out.append({"title": to_text(name), "text": to_text(desc), "lang": "zh" if "/cn/" in url else "en"})
        return out
    # Company's own page (WordPress job post, careers page, PeopleHR opening).
    art = (re.search(r'(?is)<article[^>]*>(.*?)</article>', body) or re.search(r'(?is)<main[^>]*>(.*?)</main>', body))
    text = to_text(art.group(1) if art else body)
    title = page_title(body)
    slug = re.search(r"/(?:careers?|jobs?)/([a-z0-9-]+)/?$", urllib.parse.urlparse(url).path)
    if slug and not any(w in (title or "").lower() for w in slug.group(1).split("-") if len(w) > 3):
        title = slug.group(1).replace("-", " ").title()  # a posting page whose <title> is the site's tagline
    if len(text) < 300 or text.strip() == (title or "").strip():
        text = ""  # a client-rendered page (Polymerize's Gatsby site) leaves only its header and footer
    out.append({"title": title, "text": text, "generic": True})
    out += dated_listings(to_text(body))
    out += linked_listings(body)
    return out


ATS_LINK = re.compile(
    r'(?is)<a[^>]+href="([^"]*(?:trinethire\.com/companies/[^"/]+/jobs/(\d+)-([\w-]+)|'
    r'greenhouse\.io/[^"/]+/jobs/(\d+)|[?&]gh_jid=(\d+)|lever\.co/[^"/]+/([0-9a-f-]{36})|'
    r'ashbyhq\.com/[^"/]+/([0-9a-f-]{36})|workable\.com/[^"]*?/j/(\w+)|bamboohr\.com/[^"]*?id=(\d+)|'
    r'applytojob\.com/apply/(\w+)))"[^>]*>(.*?)</a>')


def linked_listings(body):
    """Openings a careers page links to on an applicant-tracking system: the link
    text (or the URL slug) is the title, the ATS id the key. Older careers pages
    often list jobs this way while the posting pages themselves were never archived."""
    out, seen = [], set()
    for m in ATS_LINK.finditer(body):
        ids = [g for g in m.groups()[1:-1] if g]
        pid = ids[0] if ids else None
        title = to_text(m.group(m.lastindex)) if m.lastindex else ""
        if not title or re.match(r"(?i)^(apply|learn more|view|details|read more|see|more)\b", title):
            # "Learn more & apply" under a heading (Emerald's 2015-16 careers page): the heading is the title.
            heads = re.findall(r"(?is)<h[1-6][^>]*>(.*?)</h[1-6]>", body[max(0, m.start() - 3000):m.start()])
            if heads:
                title = to_text(heads[-1])
            elif m.group(3):
                title = m.group(3).replace("-", " ").title()
        if not pid or not title or pid in seen or len(title) > 120:
            continue
        seen.add(pid)
        out.append({"posting_id": pid, "title": title, "listing_only": True, "url": m.group(1)})
    return out


MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"


def dated_listings(text):
    """A careers page that lists each opening as 'Month D, YYYY / Title / blurb / Apply' (Atinary)."""
    from datetime import datetime
    out = []
    for when, title, blurb in re.findall(rf"(?m)^({MONTH} \d{{1,2}}, \d{{4}})\n(.{{4,120}})\n(.+?)\nApply\b", text):
        try:
            d = datetime.strptime(when, "%B %d, %Y").date().isoformat()
        except ValueError:
            continue
        out.append({"posting_id": "title:" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-"),
                    "title": title.strip(), "published": d, "text": clean(blurb)})
    return out


def page_title(body):
    """og:title, else <title>, else the first non-empty <h1>, without a ' | Site' suffix."""
    cands = re.findall(r'(?is)<meta[^>]+property="og:title"[^>]+content="([^"]*)"', body)
    cands += re.findall(r"(?is)<title[^>]*>(.*?)</title>", body)
    cands += re.findall(r"(?is)<h1[^>]*>(.*?)</h1>", body)
    for c in cands:
        t = to_text(c)
        m = re.match(r"(?i)^careers?\s+\|\s+(.+?)\s+\|\s+job description\b", t or "")
        if m:  # Polymerize: "Careers | QA Engineer | Job description | Polymerize"
            return m.group(1)
        t = re.split(r"\s+[|–—]\s+|\s+-\s+(?=[A-Z][\w .&]*$)", t)[0].strip() if t else t
        if t:
            return t
    return None


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


def live_lever(token):
    """Lever's public postings API (the token is case-sensitive: Radical AI's is 'RadicalAI')."""
    import datetime
    out = []
    for j in json.loads(fetch.get(f"https://api.lever.co/v0/postings/{token}?mode=json")):
        c, sal = j.get("categories") or {}, j.get("salaryRange")
        body = (j.get("description") or "") + "".join(f"<h3>{x.get('text')}</h3><ul>{x.get('content')}</ul>"
                                                       for x in j.get("lists") or []) + (j.get("additional") or "")
        out.append({"posting_id": j["id"], "title": j.get("text"), "team": c.get("team") or c.get("department"),
                    "location": c.get("location"), "employment_type": c.get("commitment"),
                    "published": datetime.datetime.fromtimestamp(j["createdAt"] / 1000, datetime.timezone.utc).date().isoformat(),
                    "salary": {"currency": sal.get("currency"), "min": sal.get("min"), "max": sal.get("max"),
                               "interval": "1 YEAR" if "year" in (sal.get("interval") or "") else sal.get("interval")}
                    if sal and sal.get("min") else None,
                    "url": j.get("hostedUrl"), "text": to_text(body)})
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
    """A PeopleHR opening: title, department and city fields, and the description
    between pJobDescription and the location fields."""
    def field(name):
        m = re.search(rf'(?is)id="p{name}"[^>]*>(.*?)</p>', body)
        return to_text(m.group(1)) if m else None
    t = re.search(r'(?is)class="vacancynameforopening"[^>]*>(.*?)</h2>', body)
    i, j = body.find('id="pJobDescription"'), body.find('id="pLocation"')
    desc = body[body.find(">", i) + 1:j if j > i else None] if i >= 0 else body
    return {"title": (to_text(t.group(1)) if t else None) or field("JobTitle"), "team": field("Department"),
            "location": ", ".join(filter(None, (field("City"), field("Country")))) or field("Location"),
            "text": to_text(desc.split("Apply for this job")[0])}


def live_bamboohr(token):
    """BambooHR's careers site renders from /careers/list and /careers/<id>/detail (closed openings 404)."""
    out = []
    for j in json.loads(fetch.get(f"https://{token}.bamboohr.com/careers/list")).get("result") or []:
        url = f"https://{token}.bamboohr.com/careers/{j['id']}"
        jo = json.loads(fetch.get(url + "/detail"))["result"]["jobOpening"]
        loc = jo.get("location") or {}
        out.append({"posting_id": str(j["id"]), "title": jo.get("jobOpeningName"),
                    "team": re.sub(r"^\d+\s+", "", jo.get("departmentLabel") or "") or None,
                    "location": ", ".join(filter(None, (loc.get("city"), loc.get("state")))) or None,
                    "employment_type": jo.get("employmentStatusLabel"), "published": jo.get("datePosted"),
                    "pay_text": jo.get("compensation"), "url": url, "text": to_text(jo.get("description") or "")})
    return out


FEISHU_QUERY = {"keyword": "", "limit": 100, "offset": 0, "job_category_id_list": [], "tag_id_list": [],
                "location_code_list": [], "subject_id_list": [], "recruitment_id_list": [], "portal_type": 6,
                "job_function_id_list": [], "storefront_id_list": [], "portal_entrance": 1}


def live_feishu(spec):
    """A Feishu (Lark) Hire careers site, 'host|board,board' (DP Technology: 'index' for experienced
    hires, '305722' for campus). The site renders from POST /api/v1/search/job/posts, with a CSRF
    token it issues to every visitor; each posting comes back with its full text and publish time.
    Asking without a board name returns a third list that overlaps both, so all three are merged."""
    import datetime
    import http.cookiejar
    import time
    host, boards = spec.split("|")
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def post(path, body, headers=None):
        req = urllib.request.Request(f"https://{host}/api/v1/{path}", data=json.dumps(body).encode(),
                                     headers={"User-Agent": fetch.UA, "Content-Type": "application/json", **(headers or {})})
        with opener.open(req, timeout=60) as resp:
            return json.loads(resp.read())

    token = post("csrf/token", {"portal_entrance": 1})["data"]["token"]
    found = {}
    for board in boards.split(",") + [None]:
        offset = 0
        while True:
            time.sleep(1)
            data = post("search/job/posts", {**FEISHU_QUERY, "offset": offset},
                        {"x-csrf-token": token, **({"website-path": board} if board else {})})["data"]
            for j in data["job_post_list"]:
                found.setdefault(j["id"], (j, board))
            offset += FEISHU_QUERY["limit"]
            if offset >= data["count"]:
                break
    out = []
    for pid, (j, board) in found.items():
        rt = j.get("recruit_type") or {}
        when = datetime.datetime.fromtimestamp(int(j["publish_time"]) / 1000, datetime.timezone(datetime.timedelta(hours=8)))
        out.append({"posting_id": pid, "title": j["title"].strip(), "lang": "zh",
                    "team": ((rt.get("parent") or {}).get("en_name") or None),
                    "location": ", ".join(c.get("en_name") or c.get("name") for c in j.get("city_list") or []) or None,
                    "employment_type": rt.get("en_name"), "published": when.date().isoformat(),
                    "url": f"https://{host}/{board or 'index'}/position/{pid}/detail",
                    "text": clean(f"Job description (职位描述):\n{j.get('description') or ''}\n\n"
                                  f"Requirements (职位要求):\n{j.get('requirement') or ''}")})
    return out


def live_getro(spec):
    """Postings a company published on a Getro job board (VC-portfolio and university boards), read
    from the posting page's __NEXT_DATA__: 'board-host|job-id-slug,job-id-slug'. Getro keeps
    expired and deactivated postings at their URLs, so these are records of closed roles too."""
    host, slugs = spec.split("|")
    out = []
    for slug in slugs.split(","):
        url = f"https://{host}/companies/{slug}"
        rec = getro_job(fetch.get(url))
        if not rec:
            print("no job at", url, file=sys.stderr)
            continue
        ats = posting_key(rec.get("original_url") or "")
        out.append({**rec, "posting_id": ats or rec["posting_id"], "getro_id": rec["posting_id"], "url": url,
                    "closed": rec["status"] != "active"})
    return out


def getro_job(body):
    """The posting on a Getro job page, from its __NEXT_DATA__ (live or archived)."""
    data = json_after(body, '<script id="__NEXT_DATA__" type="application/json">')
    j = (((data or {}).get("props") or {}).get("pageProps") or {}).get("initialState", {}).get("jobs", {}).get("currentJob")
    if not j:
        return None
    sal = None
    if j.get("compensationPublic") and j.get("compensationAmountMinCents"):
        sal = {"currency": j.get("compensationCurrency"), "min": j["compensationAmountMinCents"] / 100,
               "max": (j.get("compensationAmountMaxCents") or j["compensationAmountMinCents"]) / 100,
               "interval": {"year": "1 YEAR"}.get(j.get("compensationPeriod"), j.get("compensationPeriod"))}
    closed = j.get("closedAt") or j.get("deactivatedAt") or j.get("expiresAt")
    return {"posting_id": str(j["id"]), "title": j.get("title"),
            "location": "; ".join(x.get("name") or "" for x in j.get("locations") or []) or None,
            "employment_type": ", ".join(j.get("employmentTypes") or []) or None,
            "published": j.get("postedAt"), "salary": sal, "original_url": j.get("url"),
            "getro_source": j.get("source"), "status": j.get("status"),
            "last_seen": closed if j.get("status") != "active" else None, "text": to_text(j.get("description") or "")}


def live_nodi(company):
    """Nodi, an AI-screening ATS: its careers widget renders from this public endpoint. Only the
    posting itself is kept (not the recruiter id or the screening rubric the endpoint also returns)."""
    out = []
    for j in json.loads(fetch.get(f"https://api.nodi.global/job-offers/active/company/{urllib.parse.quote(company)}")):
        sal = None
        if j.get("min_salary") and (j.get("frequency") or "").lower().startswith("annual"):
            sal = {"currency": j.get("currency") or "USD", "min": j["min_salary"], "max": j.get("max_salary") or j["min_salary"],
                   "interval": "1 YEAR"}
        out.append({"posting_id": j["id"], "title": j.get("title"), "team": j.get("department"),
                    "location": j.get("location"), "employment_type": j.get("type"), "published": j.get("created_at"),
                    "salary": sal, "url": f"https://app.nodi.global/jobs/public/{j['id']}",
                    "text": to_text(j.get("description") or "")})
    return out


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


LIVE = {"lever": live_lever, "notion": live_notion, "links": live_links, "ashby": live_ashby, "greenhouse": live_greenhouse, "rippling": live_rippling,
        "personio": live_personio, "peoplehr": live_peoplehr, "wordpress": live_wordpress, "bamboohr": live_bamboohr,
        "feishu": live_feishu, "getro": live_getro, "nodi": live_nodi}


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
    re.compile(r"hire\.withgoogle\.com/public/jobs/[^/]+/(?:view/|confirmation\?jobPosition=)(P_\w+)"),
    re.compile(r"bamboohr\.com/(?:careers/|jobs/view\.php\?id=)(\d+)"),
    re.compile(r"jobs\.feishu\.cn/[^/]+/position/(\d+)"),
    re.compile(r"/companies/[^/]+/jobs/(\d+)(?:[-/?#]|$)"),  # Getro boards
]


def posting_key(url):
    for rx in ID_RX:
        m = rx.search(url)
        if m:
            return m.group(1).lower()
    return None


def _root(url):
    u = re.sub(r"^(https?://)?(www\.)?", "", url.split("?")[0].split("#")[0]).rstrip("/")
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
            if k and not p.get("listing_only"):
                rec["posting_id"] = k
            elif p.get("posting_id"):
                rec["posting_id"] = str(p["posting_id"]).lower()
                rec["board_capture"] = True
            done["postings"].append(rec)
        seen.add(f"{k or ''}|{cap}")
        save()
        print(ts, (k or "board")[:12], url[:90], flush=True)
    print(slug, "fetched", fetched, flush=True)


def cmd_reparse(slug):
    """Re-run the parsers over the captures already fetched (from the cache), so a
    parser fix needs no new requests to the archive."""
    out_path = os.path.join(RAW, f"{slug}.wayback.json")
    done = json.load(open(out_path, encoding="utf-8"))
    by_cap = {}
    for r in done["postings"]:
        k = r.get("posting_id") if not r.get("board_capture") and not r.get("listing_only") else None
        by_cap.setdefault(r["capture"], (k, r["url"], r["first_seen"], r["last_seen"], r["n_captures"]))
    rebuilt, missing = [], 0
    for cap, (k, url, first, last, n) in by_cap.items():
        ts = re.search(r"/web/(\d{14})/", cap).group(1)
        key = hashlib.sha256(f"https://web.archive.org/web/{ts}id_/{url}".encode()).hexdigest()
        if not os.path.exists(os.path.join(fetch.CACHE, key)):
            missing += 1
            rebuilt += [r for r in done["postings"] if r["capture"] == cap]
            continue
        body = fetch.get(f"https://web.archive.org/web/{ts}id_/{url}")
        for p in parse_page(url, body):
            rec = {"company": slug, "basis": "wayback", "capture": cap, "url": url,
                   "first_seen": first, "last_seen": last, "n_captures": n, **p}
            if k and not p.get("listing_only"):
                rec["posting_id"] = k
            elif p.get("posting_id"):
                rec["posting_id"] = str(p["posting_id"]).lower()
                rec["board_capture"] = True
            rebuilt.append(rec)
    done["postings"] = rebuilt
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(done, fh, indent=1, ensure_ascii=False)
    print(slug, len(by_cap), "captures reparsed;", missing, "not in cache")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    lv = sub.add_parser("live")
    lv.add_argument("slugs", nargs="*")
    lv.add_argument("--date", default="2026-10-10")
    hi = sub.add_parser("history")
    hi.add_argument("slug")
    hi.add_argument("--max-pages", type=int, default=400)
    rp = sub.add_parser("reparse", help="re-run the parsers over cached captures")
    rp.add_argument("slugs", nargs="+")
    sub.add_parser("build")
    a = ap.parse_args()
    if a.cmd == "live":
        cmd_live(a.slugs or [s for s, b in BOARDS.items() if b.get("live")], a.date)
    elif a.cmd == "history":
        cmd_history(a.slug, a.max_pages)
    elif a.cmd == "reparse":
        for slug in a.slugs:
            cmd_reparse(slug)
    elif a.cmd == "build":
        import jobs_report
        jobs_report.build()


if __name__ == "__main__":
    sys.exit(main())
