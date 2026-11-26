#!/usr/bin/env python3
"""Leads on who funded each venture, gathered from open APIs instead of a web search engine.

Every research session shares one web-search budget (part 2's first pass ran out halfway), so the deal passes
start from pages fetched here. For each venture in data/ventures_input.csv:

1. TechCrunch, SiliconANGLE, BetaKit and TechNode (WordPress REST APIs): posts that name the venture; the
   sentences about rounds and investors are kept from the full post text.
2. Hacker News (Algolia API): stories whose title names the venture and a raise, round or backing; the linked
   pages (often the company's own announcement) are fetched and the same sentences kept.
3. Wikipedia: the matching article's sentences about funding and investors, and Wikidata's "investor" (P1951)
   statements for the same entity.
4. The company's own site (U1 rows give it): sentences such as "backed by ...".

Writes data/leads/leads.jsonl (one venture per line) and data/leads/leads_<pass>.md for each deal pass. Leads are
not data: a pass records a funder only from a page that states it. Run from funders/.
"""
import concurrent.futures as cf, csv, glob, html, json, os, re, sys, time, urllib.parse as up
import requests

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
WIKI_UA = {"User-Agent": "open-source-funders-study/1.0 (research script; issue 380)"}
CUE = re.compile(r"\b(led by|co-led|participation (from|by|of)|participat\w+|backed by|backers?|"
                 r"investors? (include|including|such as|are|were)|joined by|funding from|investment from|"
                 r"invested|pre-seed|seed (round|funding|financing)|series [a-h]\b|rais(e|es|ed|ing)\b|grants?\b|"
                 r"awarded|crowdfund\w*|kickstarter|indiegogo|crowd supply|wefunder|republic|seedrs|crowdcube|"
                 r"y combinator|\byc\b|accelerator|angel investors?|angels\b|funded by)\b", re.I)
FUND = re.compile(r"\b(rais\w*|funding|fund\w*|series [a-h]\b|seed|round|backed|invest\w*|valuation|grant|"
                  r"kickstarter|crowdfund\w*|acquir\w*|led by)\b", re.I)
GENERIC = {"labs", "lab", "inc", "inc.", "ltd", "llc", "gmbh", "technologies", "technology", "software", "systems",
           "corp", "corporation", "co", "company", "hq", "org", "studio", "io", "group", "limited", "sas", "s.a.",
           "ag", "oy", "ab", "bv", "b.v.", "pte", "pty", "the", "s.r.o.", "s.r.l.", "a.s.", "pbc", "n.v.", "plc",
           "ltd.", "kft", "oü", "ou", "ug", "sa", "llc."}
S = requests.Session(); S.headers.update(UA)
W = requests.Session(); W.headers.update(WIKI_UA)
WP = [("TechCrunch", "https://techcrunch.com"), ("SiliconANGLE", "https://siliconangle.com"),
      ("BetaKit", "https://betakit.com"), ("TechNode", "https://technode.com")]


def _get_capped(sess, url, **kw):
    """GET with a total deadline (25 s) and a 3 MB cap, so one slow page can't stall a pass."""
    t0 = time.time()
    r = sess.get(url, timeout=15, stream=True, **kw)
    buf = b""
    for chunk in r.iter_content(65536):
        buf += chunk
        if len(buf) > 3_000_000 or time.time() - t0 > 25:
            break
    r._content = buf
    r._content_consumed = True
    return r


def get(sess, url, **kw):
    for attempt in range(3):
        try:
            r = _get_capped(sess, url, **kw)
            if r.status_code == 429 and sess is W:
                return r  # Wikipedia throttles parallel clients; skip rather than wait
            if r.status_code in (429, 502, 503, 504):
                time.sleep(4 * (attempt + 1)); continue
            return r
        except requests.RequestException:
            time.sleep(2)
    return None


def text_of(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg|nav|footer|header)[^>]*>.*?</\1>", " ", h or "")
    h = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</h\d>|</div>", ". ", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    return re.sub(r"\s+", " ", t).strip()


def sentences(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"“(0-9])", t) if 25 < len(s.strip()) < 600]


def names(venture):
    v = re.sub(r"\s+", " ", venture).strip()
    alts = [a for a in re.findall(r"\(([^)]*)\)", v)]
    base = re.sub(r"\([^)]*\)", "", v).strip(" ,/")
    out = []
    for n in [base] + [a.replace("formerly ", "").replace("d/b/a ", "") for a in alts] + base.split(" / "):
        n = n.strip()
        toks = n.replace(",", " ").split()
        while len(toks) > 1 and toks[-1].lower() in GENERIC:
            toks = toks[:-1]
        n2 = " ".join(toks).strip()
        for x in (n2, n):
            if x and len(x) >= 3 and x not in out and x.lower() not in GENERIC:
                out.append(x)
    return out[:4]


def mentions(t, nm):
    return any(re.search(r"(?<![A-Za-z0-9])" + re.escape(n) + r"(?![A-Za-z0-9])", t, re.I) for n in nm)


def keep(t, nm, about):
    out = []
    for s in sentences(t):
        if CUE.search(s) and (about or mentions(s, nm)):
            out.append(s[:500])
    return out


def wp_leads(nm):
    """Two steps per site: list matching posts with titles and excerpts only (light), then fetch the full text of at
    most six posts whose title or excerpt names the venture together with a funding word."""
    found = []
    for site, base in WP:
        for q in nm[:2]:
            r = get(S, f"{base}/wp-json/wp/v2/posts", params={"search": q, "per_page": 50,
                                                              "_fields": "id,link,title,date,excerpt"})
            if not r or r.status_code != 200:
                continue
            try:
                posts = r.json()
            except ValueError:
                continue
            pick = []
            for p in posts:
                title = html.unescape(re.sub(r"<[^>]+>", "", (p.get("title") or {}).get("rendered", "")))
                exc = text_of((p.get("excerpt") or {}).get("rendered", ""))
                if mentions(title + " " + exc, nm) and FUND.search(title + " " + exc):
                    pick.append((p, title))
            pick = pick[:6]
            if pick:
                r2 = get(S, f"{base}/wp-json/wp/v2/posts", params={"include": ",".join(str(p["id"]) for p, _ in pick),
                                                                   "per_page": len(pick), "_fields": "id,content"})
                body = {}
                try:
                    body = {x["id"]: text_of((x.get("content") or {}).get("rendered", "")) for x in (r2.json() if r2 is not None and r2.status_code == 200 else [])}
                except (ValueError, TypeError):
                    body = {}
                for p, title in pick:
                    about = mentions(title, nm)
                    ss = keep(body.get(p["id"], ""), nm, about and bool(FUND.search(title)))
                    found.append({"src": site, "date": (p.get("date") or "")[:10], "title": title, "url": p.get("link"),
                                  "about": about, "sentences": ss[:6]})
            if posts:
                break
    return found


def hn_leads(nm):
    urls = []
    for q in nm[:2]:
        r = get(S, "https://hn.algolia.com/api/v1/search", params={"query": q, "tags": "story", "hitsPerPage": 60})
        if not r or r.status_code != 200:
            continue
        for h in r.json().get("hits", []):
            t, u = h.get("title") or "", h.get("url") or ""
            if u and mentions(t, nm) and FUND.search(t):
                urls.append((h.get("created_at", "")[:10], t, u))
        if urls:
            break
    seen, out = set(), []
    for d, t, u in urls:
        if u in seen or len(out) >= 4:
            continue
        seen.add(u)
        r = get(S, u)
        if not r or r.status_code != 200 or "html" not in r.headers.get("content-type", ""):
            out.append({"src": "Hacker News link (not fetched)", "date": d, "title": t, "url": u, "about": True,
                        "sentences": []})
            continue
        ss = keep(text_of(r.text), nm, True)
        out.append({"src": "Hacker News link", "date": d, "title": t, "url": u, "about": True, "sentences": ss[:6]})
    return out


def wiki_leads(nm, category):
    out = []
    for q in nm[:2]:
        r = get(W, "https://en.wikipedia.org/w/api.php", params={"action": "query", "list": "search", "srsearch": q,
                                                                 "srlimit": 3, "format": "json"})
        if not r or r.status_code != 200:
            continue
        hits = r.json().get("query", {}).get("search", [])
        hit = next((h for h in hits if mentions(h["title"], nm)), None)
        if not hit:
            continue
        r = get(W, "https://en.wikipedia.org/w/api.php", params={"action": "query", "prop": "extracts|pageprops",
                "explaintext": 1, "titles": hit["title"], "format": "json", "redirects": 1})
        if not r or r.status_code != 200:
            continue
        page = next(iter(r.json().get("query", {}).get("pages", {}).values()), {})
        ext = page.get("extract") or ""
        url = "https://en.wikipedia.org/wiki/" + up.quote(page.get("title", hit["title"]).replace(" ", "_"))
        ss = keep(ext, nm, True)
        ss = [s for s in ss if re.search(r"(fund|invest|rais|series|seed|led by|backed|grant|capital|ventures?)", s, re.I)]
        if ss:
            out.append({"src": "Wikipedia", "date": "", "title": page.get("title"), "url": url, "about": True,
                        "sentences": ss[:8]})
        qid = (page.get("pageprops") or {}).get("wikibase_item")
        if qid:
            r = get(W, f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json")
            if r and r.status_code == 200:
                ent = r.json().get("entities", {}).get(qid, {})
                inv = [c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") for c in
                       ent.get("claims", {}).get("P1951", [])]
                inv = [i for i in inv if i]
                if inv:
                    r2 = get(W, "https://www.wikidata.org/w/api.php", params={"action": "wbgetentities",
                             "ids": "|".join(inv[:40]), "props": "labels", "languages": "en", "format": "json"})
                    labels = []
                    if r2 and r2.status_code == 200:
                        labels = [e.get("labels", {}).get("en", {}).get("value", i)
                                  for i, e in r2.json().get("entities", {}).items()]
                    out.append({"src": "Wikidata P1951 (investor)", "date": "", "title": qid,
                                "url": f"https://www.wikidata.org/wiki/{qid}", "about": True,
                                "sentences": ["Investors listed on Wikidata: " + "; ".join(labels)]})
        break
    return out


def site_leads(nm, hint):
    m = re.search(r"site (\S+)", hint or "")
    if not m or m.group(1) in {"", "nan"}:
        return []
    u = m.group(1).rstrip(";,")
    if not u.startswith("http"):
        u = "https://" + u
    out = []
    for path in ("", "/about", "/company", "/about-us"):
        r = get(S, up.urljoin(u if u.endswith("/") else u + "/", path.lstrip("/")))
        if not r or r.status_code != 200 or "html" not in r.headers.get("content-type", ""):
            continue
        h = r.text
        alts = re.findall(r'(?is)(backed by|investors|our investors|supported by|funded by)(.{0,2500})', h)
        logo = []
        for _, chunk in alts[:2]:
            logo += [html.unescape(a) for a in re.findall(r'alt="([^"]{2,60})"', chunk)]
        ss = [s for s in sentences(text_of(h)) if re.search(r"(backed by|investors|funded by|raised|series [a-h]|"
                                                             r"seed round|y combinator)", s, re.I)]
        if ss or logo:
            out.append({"src": "company site", "date": "", "title": path or "/", "url": r.url, "about": True,
                        "sentences": [s[:400] for s in ss[:5]] + (["Logo alt texts near 'backed by/investors': " +
                                                                   "; ".join(dict.fromkeys(logo))[:400]] if logo else [])})
    return out[:2]


def one(v):
    nm = names(v["venture"])
    leads = []
    for f in (lambda: wp_leads(nm), lambda: hn_leads(nm), lambda: wiki_leads(nm, v["category"]),
              lambda: site_leads(nm, v["hint"])):
        try:
            leads += f()
        except Exception as e:  # noqa: BLE001
            leads.append({"src": "error", "date": "", "title": repr(e)[:200], "url": "", "about": False,
                          "sentences": []})
    leads = [l for l in leads if l["sentences"] or l["src"].startswith("Hacker News")]
    leads.sort(key=lambda x: (not (x["about"] and bool(FUND.search(x["title"] or ""))), not x["about"],
                              x["date"] or "9999"))
    return {"key": v["key"], "venture": v["venture"], "names": nm, "leads": leads[:16]}


def main():
    """Args: pass ids to process (default: all, in the order U2, U3, U1). Each pass writes leads_<pass>.jsonl."""
    vs = list(csv.DictReader(open("data/ventures_input.csv")))
    os.makedirs("data/leads", exist_ok=True)
    out = {}
    for path in glob.glob("data/leads/*.jsonl"):
        for line in open(path):
            try:
                d = json.loads(line); out[d["key"]] = d
            except ValueError:
                pass
    t0 = time.time()
    order = sorted(glob.glob("data/deal_passes/input_*.csv"), key=lambda p: ("scadex".find(os.path.basename(p)[6]) % 9, p))
    if sys.argv[1:]:
        order = [p for p in order if re.search(r"input_(\w+)\.csv", p).group(1) in sys.argv[1:]]
    for inp in order:
        pid = re.search(r"input_(\w+)\.csv", inp).group(1)
        keys = [v["key"] for v in csv.DictReader(open(inp))]
        todo = [v for v in vs if v["key"] in keys and v["key"] not in out]
        with cf.ThreadPoolExecutor(16) as ex:
            for d in ex.map(one, todo):
                out[d["key"]] = d
                with open(f"data/leads/leads_{pid}.jsonl", "a") as f:
                    f.write(json.dumps(d) + "\n")
        write_md(inp, out)
        print(f"{pid}: {len(todo)} done, {time.time() - t0:.0f}s", flush=True)


def write_md(inp, out):
    if True:
        pid = re.search(r"input_(\w+)\.csv", inp).group(1)
        lines = [f"# Leads for deal pass {pid}\n", "Gathered by `scripts/investor_leads.py` from open APIs. Leads, "
                 "not data: record a funder only from a page that states it.\n"]
        for v in csv.DictReader(open(inp)):
            d = out.get(v["key"], {"leads": []})
            lines.append(f"\n## {v['venture']} (`{v['key']}`, {v['universe']})\n")
            if not d["leads"]:
                lines.append("_No leads found._\n")
            for l in d["leads"]:
                lines.append(f"- **{l['src']}** {l['date']} · {l['title']} · {l['url']}")
                for s in l["sentences"]:
                    lines.append(f"  > {s}")
        open(f"data/leads/leads_{pid}.md", "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
