#!/usr/bin/env python3
"""Polite, cached fetchers for the AI-for-materials / self-driving-lab startup survey.

Every source here is a public endpoint meant for this kind of reading: the
Wayback Machine's CDX and playback APIs, public applicant-tracking-system job
boards (the JSON the companies' own careers pages render from), OpenAlex, UK
Companies House pages and the French company registry API. Nothing logs in,
nothing touches LinkedIn directly.

Requests are cached under $SL_CACHE (default /tmp/sl-cache) and rate-limited
per host with a lock file, so several agents on one machine share one budget.

    python scripts/startup_landscape/fetch.py cdx 'example.com/team*' --collapse timestamp:6
    python scripts/startup_landscape/fetch.py cdx-urls 'jobs.ashbyhq.com/example/*'
    python scripts/startup_landscape/fetch.py snap 20240101000000 https://example.com/team
    python scripts/startup_landscape/fetch.py ats example
    python scripts/startup_landscape/fetch.py pay ashby example
    python scripts/startup_landscape/fetch.py openalex-inst "Citrine Informatics"
    python scripts/startup_landscape/fetch.py openalex-authors I4210123456
    python scripts/startup_landscape/fetch.py ch-search "orbital materials"
    python scripts/startup_landscape/fetch.py ch-officers 12345678
    python scripts/startup_landscape/fetch.py ch-filings 12345678
    python scripts/startup_landscape/fetch.py fr entalpic
    python scripts/startup_landscape/fetch.py pdf 'https://find-and-update.company-information.service.gov.uk/company/12345678/filing-history/<id>/document?format=pdf&download=0'
"""
import argparse
import fcntl
import gzip
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict

UA = "Mozilla/5.0 (compatible; byu-vcl-research/0.1; +https://github.com/vertical-cloud-lab/byu-vcl)"
CACHE = os.environ.get("SL_CACHE", "/tmp/sl-cache")
# Seconds between requests to one host, shared across processes.
MIN_INTERVAL = {"web.archive.org": 1.5, "api.openalex.org": 0.2}
DEFAULT_INTERVAL = 0.5


def _throttle(host):
    os.makedirs(CACHE, exist_ok=True)
    gap = MIN_INTERVAL.get(host, DEFAULT_INTERVAL)
    with open(os.path.join(CACHE, f".rate-{host}"), "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        last = float(fh.read() or 0)
        wait = last + gap - time.time()
        if wait > 0:
            time.sleep(wait)
        fh.seek(0)
        fh.truncate()
        fh.write(str(time.time()))


def _read_capped(resp):
    """Read a response, holding the average under $SL_MAX_BPS bytes/s if set
    (for fetching from a Pi on shared Wi-Fi)."""
    cap = float(os.environ.get("SL_MAX_BPS") or 0)
    if not cap:
        return resp.read()
    chunks, got, t0 = [], 0, time.time()
    while True:
        chunk = resp.read(16384)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        got += len(chunk)
        ahead = got / cap - (time.time() - t0)
        if ahead > 0:
            time.sleep(ahead)


def get(url, *, data=None, headers=None, tries=4, timeout=60):
    """GET (or POST if data) with cache, per-host throttle and backoff on 429/5xx."""
    key = hashlib.sha256((url + (data or "")).encode()).hexdigest()
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    host = urllib.parse.urlparse(url).hostname
    for attempt in range(tries):
        _throttle(host)
        req = urllib.request.Request(
            url,
            data=data.encode() if data else None,
            headers={"User-Agent": UA, **(headers or {})},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                blob = _read_capped(resp)
            # Wayback's id_ playback can return the original gzip body undecoded.
            if blob[:2] == b"\x1f\x8b":
                blob = gzip.decompress(blob)
            body = blob.decode("utf-8", errors="replace")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(body)
            return body
        except urllib.error.HTTPError as err:
            if err.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(20 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < tries - 1:
                time.sleep(10 * (attempt + 1))
                continue
            raise


def html_to_text(body):
    body = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", body)
    body = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr|section|article)>", "\n", body)
    body = html.unescape(re.sub(r"<[^>]+>", " ", body))
    lines = (re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in body.splitlines())
    return "\n".join(ln for ln in lines if ln)


# --- Wayback Machine -------------------------------------------------------

def cdx(pattern, frm=None, to=None, collapse=None, filters=(), limit=None,
        fields="timestamp,original,statuscode,digest"):
    q = {"url": pattern, "output": "json", "fl": fields}
    if frm:
        q["from"] = frm
    if to:
        q["to"] = to
    if limit:
        q["limit"] = limit
    params = list(q.items())
    if collapse:
        params.append(("collapse", collapse))
    params += [("filter", f) for f in filters]
    url = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(params)
    rows = json.loads(get(url, timeout=180) or "[]")
    return [dict(zip(rows[0], r)) for r in rows[1:]] if rows else []


def cdx_urls(pattern, frm=None, to=None, limit=50000):
    """Distinct captured URLs under a prefix, with first/last capture and count.

    For a job board this is the posting history: each posting URL first and
    last seen by the crawler, a lower bound on how long it was open.
    """
    rows = cdx(pattern, frm, to, filters=("statuscode:200",), limit=limit,
               fields="urlkey,timestamp,original")
    agg = defaultdict(lambda: {"first": "99999999", "last": "0", "n": 0, "original": ""})
    for r in rows:
        a = agg[r["urlkey"]]
        a["n"] += 1
        if r["timestamp"] < a["first"]:
            a["first"], a["original"] = r["timestamp"], r["original"]
        a["last"] = max(a["last"], r["timestamp"])
    return sorted(({"urlkey": k, **v} for k, v in agg.items()), key=lambda d: d["first"])


def snap(timestamp, url, raw=False):
    """Archived copy as originally served (id_ = no Wayback toolbar or rewriting)."""
    body = get(f"https://web.archive.org/web/{timestamp}id_/{url}")
    return body if raw else html_to_text(body)


# --- Public job boards -----------------------------------------------------

def ats(token):
    """Try the public job-board APIs of the common ATS vendors for one board token."""
    out = {}
    tries = {
        "ashby": f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true",
        "greenhouse": f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=false",
        "lever": f"https://api.lever.co/v0/postings/{token}?mode=json",
        "lever-eu": f"https://api.eu.lever.co/v0/postings/{token}?mode=json",
        "recruitee": f"https://{token}.recruitee.com/api/offers/",
        "workable": f"https://apply.workable.com/api/v1/widget/accounts/{token}",
    }
    for vendor, url in tries.items():
        try:
            data = json.loads(get(url))
        except Exception:
            continue
        jobs = []
        if vendor == "ashby":
            for j in data.get("jobs", []):
                jobs.append({"title": j.get("title"), "team": j.get("department") or j.get("team"),
                             "location": j.get("location"), "published": j.get("publishedAt"),
                             "url": j.get("jobUrl")})
        elif vendor == "greenhouse":
            for j in data.get("jobs", []):
                jobs.append({"title": j.get("title"), "location": (j.get("location") or {}).get("name"),
                             "updated": j.get("updated_at"), "first_published": j.get("first_published"),
                             "url": j.get("absolute_url")})
        elif vendor.startswith("lever") and isinstance(data, list):
            for j in data:
                jobs.append({"title": j.get("text"), "team": (j.get("categories") or {}).get("team"),
                             "location": (j.get("categories") or {}).get("location"),
                             "created": time.strftime("%Y-%m-%d", time.gmtime(j.get("createdAt", 0) / 1000)),
                             "url": j.get("hostedUrl")})
        elif vendor == "recruitee":
            for j in data.get("offers", []):
                jobs.append({"title": j.get("title"), "team": j.get("department"),
                             "location": j.get("location"), "published": j.get("published_at"),
                             "url": j.get("careers_url")})
        elif vendor == "workable":
            for j in data.get("jobs", []):
                jobs.append({"title": j.get("title"), "team": j.get("department"),
                             "location": j.get("city") or j.get("country"),
                             "published": j.get("published_on") or j.get("created_at"),
                             "url": j.get("url") or j.get("shortlink")})
        else:
            continue
        out[vendor] = {"source": url, "jobs": jobs}
    return out


PAY_RE = re.compile(
    r"([$€£])\s?(\d{2,3}(?:,\d{3})+|\d{2,3}(?:\.\d)?\s?[kK])\s*(?:-|–|—|to)\s*[$€£]?\s?(\d{2,3}(?:,\d{3})+|\d{2,3}(?:\.\d)?\s?[kK])")


def _money(tok):
    tok = tok.replace(",", "").replace(" ", "")
    return int(float(tok[:-1]) * 1000) if tok[-1] in "kK" else int(tok)


def pay(vendor, token):
    """Posted pay ranges (US pay-transparency laws make many boards publish them).

    vendor is ashby or greenhouse. Ashby returns structured salary components;
    for Greenhouse the range is pulled out of the posting text.
    """
    out = []
    if vendor == "ashby":
        data = json.loads(get(f"https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true"))
        for j in data.get("jobs", []):
            found = False
            for tier in (j.get("compensation") or {}).get("compensationTiers") or []:
                for c in tier.get("components") or []:
                    if c.get("compensationType") == "Salary" and c.get("minValue") and not found:
                        found = True
                        out.append({"title": j.get("title"), "team": j.get("department") or j.get("team"),
                                    "location": j.get("location"), "currency": c.get("currencyCode"),
                                    "min": c.get("minValue"), "max": c.get("maxValue"),
                                    "interval": c.get("interval"), "url": j.get("jobUrl")})
            m = None if found else PAY_RE.search(j.get("descriptionPlain") or "")
            if m:
                out.append({"title": j.get("title"), "team": j.get("department") or j.get("team"),
                            "location": j.get("location"),
                            "currency": {"$": "USD", "€": "EUR", "£": "GBP"}[m.group(1)],
                            "min": _money(m.group(2)), "max": _money(m.group(3)),
                            "interval": "1 YEAR", "url": j.get("jobUrl")})
    elif vendor == "greenhouse":
        data = json.loads(get(f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"))
        for j in data.get("jobs", []):
            text = html_to_text(html.unescape(j.get("content") or ""))
            m = PAY_RE.search(text)
            if m:
                out.append({"title": j.get("title"), "location": (j.get("location") or {}).get("name"),
                            "currency": {"$": "USD", "€": "EUR", "£": "GBP"}[m.group(1)],
                            "min": _money(m.group(2)), "max": _money(m.group(3)),
                            "interval": "1 YEAR", "url": j.get("absolute_url")})
    return out


# --- OpenAlex ----------------------------------------------------------------

def openalex_inst(query):
    url = "https://api.openalex.org/institutions?" + urllib.parse.urlencode({"search": query})
    res = json.loads(get(url))["results"]
    return [{"id": r["id"].rsplit("/", 1)[-1], "name": r["display_name"], "ror": r.get("ror"),
             "country": r.get("country_code"), "works": r.get("works_count")} for r in res]


def openalex_authors(inst_id):
    """Authors who have published with this institution, with the years of that
    affiliation and their other affiliations (a proxy for background)."""
    out, cursor = [], "*"
    while cursor:
        url = "https://api.openalex.org/authors?" + urllib.parse.urlencode(
            {"filter": f"affiliations.institution.id:{inst_id}", "per-page": 200, "cursor": cursor})
        page = json.loads(get(url))
        for a in page["results"]:
            here, other = [], []
            for aff in a.get("affiliations", []):
                inst = aff["institution"]
                rec = {"name": inst.get("display_name"), "years": sorted(aff.get("years", []))}
                (here if inst.get("id", "").endswith(inst_id) else other).append(rec)
            out.append({"id": a["id"].rsplit("/", 1)[-1], "name": a["display_name"],
                        "works": a.get("works_count"),
                        "years_here": here[0]["years"] if here else [],
                        "other_affiliations": other})
        cursor = page["meta"].get("next_cursor")
    return out


# --- Company registries -------------------------------------------------------

CH = "https://find-and-update.company-information.service.gov.uk"


def ch_search(query):
    body = get(f"{CH}/search/companies?" + urllib.parse.urlencode({"q": query}))
    hits = re.findall(r'href="/company/([A-Z0-9]{8})"[^>]*>\s*(.*?)\s*</a>', body, flags=re.S)
    return [{"number": n, "name": html.unescape(re.sub(r"<[^>]+>", "", t)).strip()} for n, t in hits]


def ch_officers(number):
    return html_to_text(get(f"{CH}/company/{number}/officers"))


def ch_filings(number, pages=3):
    text = []
    for p in range(1, pages + 1):
        text.append(html_to_text(get(f"{CH}/company/{number}/filing-history?page={p}")))
    return "\n".join(text)


def pdf_text(url):
    """Text of a PDF (e.g. Companies House accounts, which state average headcount)."""
    import io
    from pypdf import PdfReader  # pip install pypdf
    key = hashlib.sha256(("pdf:" + url).encode()).hexdigest()
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    _throttle(urllib.parse.urlparse(url).hostname)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp:
        blob = resp.read()
    text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(blob)).pages)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return text


def fr(query):
    url = "https://recherche-entreprises.api.gouv.fr/search?" + urllib.parse.urlencode({"q": query})
    return json.loads(get(url))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cdx")
    c.add_argument("pattern")
    c.add_argument("--from", dest="frm")
    c.add_argument("--to")
    c.add_argument("--collapse", help="e.g. digest, or timestamp:6 for one capture per month")
    c.add_argument("--filter", action="append", default=[], help="e.g. statuscode:200")
    c.add_argument("--limit", type=int)
    u = sub.add_parser("cdx-urls")
    u.add_argument("pattern")
    u.add_argument("--from", dest="frm")
    u.add_argument("--to")
    s = sub.add_parser("snap")
    s.add_argument("timestamp")
    s.add_argument("url")
    s.add_argument("--raw", action="store_true")
    for name in ("ats", "openalex-inst", "openalex-authors", "ch-search", "ch-officers", "ch-filings", "fr", "pdf"):
        sub.add_parser(name).add_argument("arg")
    y = sub.add_parser("pay", help="posted pay ranges from an ashby or greenhouse board")
    y.add_argument("vendor", choices=["ashby", "greenhouse"])
    y.add_argument("token")
    g = sub.add_parser("get", help="cached, throttled GET of any URL, printed as text")
    g.add_argument("url")
    g.add_argument("--raw", action="store_true")
    a = p.parse_args()

    if a.cmd == "cdx":
        for r in cdx(a.pattern, a.frm, a.to, a.collapse, a.filter, a.limit):
            print("\t".join(r.values()))
    elif a.cmd == "cdx-urls":
        for r in cdx_urls(a.pattern, a.frm, a.to):
            print(f'{r["first"]}\t{r["last"]}\t{r["n"]}\t{r["original"]}')
    elif a.cmd == "snap":
        print(snap(a.timestamp, a.url, a.raw))
    elif a.cmd == "get":
        body = get(a.url)
        print(body if a.raw else html_to_text(body))
    elif a.cmd == "pay":
        print(json.dumps(pay(a.vendor, a.token), indent=1, ensure_ascii=False))
    elif a.cmd in ("ch-officers", "ch-filings", "pdf"):
        print({"ch-officers": ch_officers, "ch-filings": ch_filings, "pdf": pdf_text}[a.cmd](a.arg))
    else:
        fn = {"ats": ats, "openalex-inst": openalex_inst, "openalex-authors": openalex_authors,
              "ch-search": ch_search, "fr": fr}[a.cmd]
        print(json.dumps(fn(a.arg), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
