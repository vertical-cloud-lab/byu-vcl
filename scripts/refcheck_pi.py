#!/usr/bin/env python3
"""Fetch reference metadata and open-access full text from the Pi's residential IP.

Runs ON THE PI with stdlib only (no venv, nothing installed system-wide). The runner
copies this over, feeds it DOIs on stdin, and rsyncs the results back rate-capped.

Why the Pi: several publishers refuse Actions-runner IPs outright. Measured from the
Pi on 2026-09-15, Crossref / OpenAlex / Unpaywall / Europe PMC / arXiv / nature.com
all answer 200, while RSC, Wiley, ACS, ScienceDirect and ChemRxiv return 403 even
here -- their block is bot fingerprinting, not datacentre IP, so for those the only
route to full text is an open-access mirror (Europe PMC, arXiv, a repository copy).
"""
import gzip
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OUT = pathlib.Path.home() / "refcheck"
OUT.mkdir(exist_ok=True)
MAILTO = "vcl@byu.edu"
UA = ("Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/140.0.0.0 Safari/537.36")


def get(url, accept="application/json", timeout=45, binary=False):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA if not accept.startswith("application/json") else
                      f"vcl-refcheck/1.0 (mailto:{MAILTO})",
        "Accept": accept,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return r.getcode(), raw, r.geturl()


def try_get(url, **kw):
    try:
        return get(url, **kw)
    except urllib.error.HTTPError as e:
        return e.code, b"", url
    except Exception as e:  # noqa: BLE001 - network flakiness on residential wifi
        return None, str(e).encode(), url


def slug(doi):
    return re.sub(r"[^a-zA-Z0-9]+", "-", doi).strip("-").lower()


def crossref(doi):
    code, raw, _ = try_get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    if code != 200:
        return {"found": False, "http": code}
    m = json.loads(raw)["message"]
    authors = [f"{a.get('given','')} {a.get('family','')}".strip()
               for a in m.get("author", [])[:12]]
    date = (m.get("issued", {}).get("date-parts") or [[None]])[0]
    return {
        "found": True,
        "title": (m.get("title") or [""])[0],
        "authors": authors,
        "n_authors": len(m.get("author", [])),
        "year": date[0] if date else None,
        "container": (m.get("container-title") or [""])[0],
        "type": m.get("type"),
        "publisher": m.get("publisher"),
        "is_referenced_by_count": m.get("is-referenced-by-count"),
        "url": m.get("URL"),
    }


def unpaywall(doi):
    code, raw, _ = try_get(
        f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={MAILTO}")
    if code != 200:
        return {}
    d = json.loads(raw)
    best = d.get("best_oa_location") or {}
    return {
        "is_oa": d.get("is_oa"),
        "oa_status": d.get("oa_status"),
        "pdf": best.get("url_for_pdf"),
        "landing": best.get("url_for_landing_page"),
        "host": best.get("host_type"),
        "all_pdfs": [loc.get("url_for_pdf") for loc in d.get("oa_locations", [])
                     if loc.get("url_for_pdf")],
    }


def europepmc(doi):
    q = urllib.parse.quote(f'DOI:"{doi}"')
    code, raw, _ = try_get(
        f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&resultType=core")
    if code != 200:
        return {}
    res = json.loads(raw).get("resultList", {}).get("result", [])
    if not res:
        return {}
    r = res[0]
    return {"pmcid": r.get("pmcid"), "pmid": r.get("pmid"),
            "isOpenAccess": r.get("isOpenAccess"), "title": r.get("title")}


def openalex(doi):
    code, raw, _ = try_get(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}")
    if code != 200:
        return {}
    d = json.loads(raw)
    locs = []
    for loc in (d.get("locations") or []):
        src = (loc.get("source") or {}).get("display_name")
        if loc.get("pdf_url"):
            locs.append({"pdf": loc["pdf_url"], "source": src,
                         "version": loc.get("version")})
        elif loc.get("landing_page_url") and loc.get("is_oa"):
            locs.append({"landing": loc["landing_page_url"], "source": src,
                         "version": loc.get("version")})
    return {"title": d.get("title"), "year": d.get("publication_year"),
            "cited_by_count": d.get("cited_by_count"),
            "type": d.get("type"), "locations": locs}


def semanticscholar(doi):
    code, raw, _ = try_get(
        f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}"
        "?fields=title,year,venue,citationCount,openAccessPdf,externalIds")
    if code != 200:
        return {}
    return json.loads(raw)


def fetch_fulltext(doi, meta, uw, epmc, oa=None, s2=None):
    """Try OA routes in order of text quality: EuropePMC XML > OA PDF > arXiv > landing."""
    s = slug(doi)
    attempts = []

    if epmc.get("pmcid"):
        url = (f"https://www.ebi.ac.uk/europepmc/webservices/rest/"
               f"{epmc['pmcid']}/fullTextXML")
        code, raw, _ = try_get(url, accept="application/xml", timeout=90)
        attempts.append(("europepmc_xml", url, code, len(raw)))
        if code == 200 and len(raw) > 5000:
            p = OUT / f"{s}.xml"
            p.write_bytes(raw)
            return str(p), attempts

    for label, url in [("unpaywall_pdf", uw.get("pdf"))] + \
                      [("unpaywall_alt_pdf", u) for u in (uw.get("all_pdfs") or [])[:3]]:
        if not url:
            continue
        code, raw, _ = try_get(url, accept="application/pdf,text/html", timeout=120)
        attempts.append((label, url, code, len(raw)))
        if code == 200 and raw[:4] == b"%PDF" and len(raw) > 20000:
            p = OUT / f"{s}.pdf"
            p.write_bytes(raw)
            return str(p), attempts
        if code == 200 and b"<html" in raw[:2000].lower() and len(raw) > 30000:
            p = OUT / f"{s}.html"
            p.write_bytes(raw)
            return str(p), attempts

    # Repository copies: RSC / Wiley / ACS / Elsevier 403 even from a residential IP,
    # so for those a mirror (arXiv, ChemRxiv, a university repository) is the only route.
    extra = [("openalex_" + re.sub(r"\W+", "_", str(l.get("source")))[:30], l.get("pdf"))
             for l in (oa or {}).get("locations", []) if l.get("pdf")]
    if (s2 or {}).get("openAccessPdf", {}) and s2["openAccessPdf"].get("url"):
        extra.append(("semanticscholar_pdf", s2["openAccessPdf"]["url"]))
    seen = {u for _, u, _, _ in attempts}
    for label, url in extra:
        if not url or url in seen:
            continue
        seen.add(url)
        code, raw, _ = try_get(url, accept="application/pdf,text/html", timeout=120)
        attempts.append((label, url, code, len(raw)))
        if code == 200 and raw[:4] == b"%PDF" and len(raw) > 20000:
            p = OUT / f"{s}.pdf"
            p.write_bytes(raw)
            return str(p), attempts
        if code == 200 and b"<html" in raw[:2000].lower() and len(raw) > 30000:
            p = OUT / f"{s}.html"
            p.write_bytes(raw)
            return str(p), attempts

    for label, url in [("openalex_landing_" + re.sub(r"\W+", "_", str(l.get("source")))[:30],
                        l.get("landing")) for l in (oa or {}).get("locations", [])
                       if l.get("landing")]:
        if not url or url in seen:
            continue
        seen.add(url)
        code, raw, _ = try_get(url, accept="text/html", timeout=90)
        attempts.append((label, url, code, len(raw)))
        if code == 200 and len(raw) > 30000 and b"<html" in raw[:2000].lower():
            p = OUT / f"{s}.html"
            p.write_bytes(raw)
            return str(p), attempts

    if uw.get("landing"):
        code, raw, _ = try_get(uw["landing"], accept="text/html", timeout=90)
        attempts.append(("unpaywall_landing", uw["landing"], code, len(raw)))
        if code == 200 and len(raw) > 30000:
            p = OUT / f"{s}.html"
            p.write_bytes(raw)
            return str(p), attempts

    return None, attempts


def main():
    dois = [ln.strip() for ln in sys.stdin if ln.strip() and not ln.startswith("#")]
    results = {}
    for i, doi in enumerate(dois, 1):
        doi = doi.lower().replace("https://doi.org/", "").strip()
        print(f"[{i}/{len(dois)}] {doi}", flush=True)
        meta = crossref(doi)
        uw = unpaywall(doi) if meta.get("found") else {}
        ep = europepmc(doi) if meta.get("found") else {}
        oa = openalex(doi) if meta.get("found") else {}
        s2 = semanticscholar(doi) if meta.get("found") else {}
        path, attempts = (fetch_fulltext(doi, meta, uw, ep, oa, s2)
                          if meta.get("found") else (None, []))
        results[doi] = {"crossref": meta, "unpaywall": uw, "europepmc": ep,
                        "openalex": oa, "semanticscholar": s2,
                        "fulltext_path": path, "attempts": attempts}
        print(f"    exists={meta.get('found')} oa={uw.get('oa_status')} "
              f"fulltext={'yes' if path else 'NO'}", flush=True)
        time.sleep(1)
    (OUT / "index.json").write_text(json.dumps(results, indent=2))
    print("wrote", OUT / "index.json")


if __name__ == "__main__":
    main()
