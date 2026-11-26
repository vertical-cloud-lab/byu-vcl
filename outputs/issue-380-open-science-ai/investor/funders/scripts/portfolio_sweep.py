#!/usr/bin/env python3
"""Investor-side check: fetch investors' own portfolio pages and find the study's ventures on them.

A deal pass looks for each venture's funders; this looks the other way, so it catches investors the passes missed
and confirms others from the investor's own page. For each portfolio page in data/portfolio/pages.csv (investor,
url), the page's links are matched to ventures' websites (domain match, strong) and its text to distinctive venture
names (name match, weaker: only names of two or more words or of 7+ letters that aren't common words). Pages built
by JavaScript return little and are reported as such.

Writes data/portfolio/fetch_log.csv and data/portfolio/matches.csv (investor, key, venture, universe, match,
evidence, url). Run from funders/.
"""
import concurrent.futures as cf, csv, glob, html, re, sys
from urllib.parse import urlparse
import requests

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
SKIP = ("github", "medium.com", "substack", "linkedin", "twitter", "x.com", "prnewswire", "businesswire",
        "globenewswire", "wikipedia", "web.archive", "youtube", "facebook", "instagram", "crunchbase", "google.com",
        "apple.com", "notion.site", "vercel.app", "netlify.app", "github.io")
COMMON = set("""zero plane void monica cube open refine agno onyx sim dub fig lens reflex locust apify payload medusa
novu warp chroma letta mastra tiny datalab notable author union strix sealos explosion symbolica motion gitea portainer
better cline continue comet budibase infisical temporal harness redash docker grafana sentry supabase vercel kong expo
ionic prisma neon turso pulumi linera fuel strapi ghost""".split())


def dom(u):
    u = (u or "").strip().rstrip(";,")
    if not u or u == "nan":
        return ""
    if not u.startswith("http"):
        u = "https://" + u
    h = urlparse(u).netloc.lower().split(":")[0]
    return h[4:] if h.startswith("www.") else h


def ventures():
    vin = list(csv.DictReader(open("data/ventures_input.csv")))
    doms = {}
    for v in vin:
        for m in re.finditer(r"site (\S+)", v["hint"] or ""):
            d = dom(m.group(1))
            if d and not any(s in d for s in SKIP):
                doms.setdefault(d, v["key"])
    for p in glob.glob("data/deal_passes/deals_*.csv"):
        for r in csv.DictReader(open(p)):
            if r["source_kind"] == "company":
                d = dom(r["source"])
                if d and not any(s in d for s in SKIP):
                    doms.setdefault(d, r["key"])
    names = {}
    for v in vin:
        base = re.sub(r"\([^)]*\)", "", v["venture"]).strip(" ,")
        base = re.sub(r",? (Inc\.?|Ltd\.?|LLC|GmbH|S\.A\.|SAS|B\.V\.|N\.V\.|plc|AG|Corp\.?|Corporation|PBC|s\.r\.o\.|Kft|OÜ|UG)$", "", base).strip()
        n = base.lower()
        if (len(n.split()) >= 2 or len(n) >= 7) and n not in COMMON and n.split()[0] not in COMMON:
            names[n] = v["key"]
    return {v["key"]: v for v in vin}, doms, names


def fetch(row):
    try:
        r = requests.get(row["url"], headers=UA, timeout=30)
        return row, r.status_code, r.text if r.status_code == 200 else ""
    except requests.RequestException as e:
        return row, repr(e)[:80], ""


def main():
    V, doms, names = ventures()
    pages = list(csv.DictReader(open("data/portfolio/pages.csv")))
    log, matches = [], {}
    with cf.ThreadPoolExecutor(12) as ex:
        for row, status, h in ex.map(fetch, pages):
            links = {dom(u) for u in re.findall(r'href="(https?://[^"#?]+)', h)}
            text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)))).lower()
            n_dom = n_name = 0
            for d in links:
                k = doms.get(d)
                if k:
                    matches[(row["investor"], k)] = ("domain", d, row["url"]); n_dom += 1
            for n, k in names.items():
                if (row["investor"], k) in matches:
                    continue
                if re.search(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", text):
                    matches[(row["investor"], k)] = ("name", n, row["url"]); n_name += 1
            log.append({"investor": row["investor"], "url": row["url"], "status": status, "bytes": len(h),
                        "external_links": len(links), "domain_matches": n_dom, "name_matches": n_name})
    with open("data/portfolio/fetch_log.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
    rows = [{"investor": i, "key": k, "venture": V[k]["venture"], "universe": V[k]["universe"], "match": m,
             "evidence": e, "url": u} for (i, k), (m, e, u) in sorted(matches.items())]
    with open("data/portfolio/matches.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["investor", "key", "venture", "universe", "match", "evidence", "url"])
        w.writeheader(); w.writerows(rows)
    ok = [l for l in log if l["bytes"] > 2000]
    print(f"{len(pages)} pages, {len(ok)} returned content; {sum(r['match'] == 'domain' for r in rows)} domain matches, "
          f"{sum(r['match'] == 'name' for r in rows)} name matches")


if __name__ == "__main__":
    main()
