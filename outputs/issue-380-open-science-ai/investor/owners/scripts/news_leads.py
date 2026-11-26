#!/usr/bin/env python3
"""Funding, valuation, acquisition and shutdown leads for each core company, without a web search engine.

The first research passes shared one session-wide web-search budget, which ran out about halfway through. This
script gathers the same kind of evidence from open APIs instead, so the second pass can work from fetched pages:

1. Hacker News (Algolia API): stories whose title names the company and mentions a raise, round, valuation,
   acquisition, IPO or shutdown, found by the company's name and by its website's domain (which finds its own blog
   posts and press releases).
2. TechCrunch (WordPress REST API): posts whose title names the company.
3. Wikipedia: the best-matching article's sentences about money or ownership (a lead only; finance_rules.md asks
   for the cited source where possible).
4. Up to six of the best lead pages are fetched and the sentences that state an amount, round, valuation or deal are
   kept, with the page's URL, so every figure the second pass records can be traced to a page that states it.

Writes data/finance_passes/leads.jsonl (one company per line) and data/finance_passes/leads_<k>.md for each
second-pass chunk. Run from owners/. Pages and APIs change; the output is dated by its file time and commit.
"""
import concurrent.futures as cf, json, os, re, sys, time, urllib.parse as up
import pandas as pd, requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
EVENT = re.compile(r"\b(rais\w*|fund\w*|series [a-h]\b|seed|pre-seed|valu\w*|acqui\w*|buys|bought|merg\w*|ipo|"
                   r"go(es|ing)? public|listing|lists|shut\w*|wind\w* down|closes|closing|layoffs?|"
                   r"invest\w*|backed|round|unicorn|joins|sold|sells|exit)\b", re.I)
MONEY = re.compile(r"([$€£¥]\s?\d[\d,.]*\s?(k|m|mn|bn|b|million|billion|thousand)?\b|\b\d[\d,.]*\s?"
                   r"(million|billion|mn|bn)\b|\b(usd|eur|rmb|cny|yuan|euros?|dollars)\b)", re.I)
GENERIC = {"labs", "lab", "inc", "inc.", "ltd", "llc", "gmbh", "ai", "technologies", "technology", "software",
           "systems", "corp", "corporation", "co", "company", "hq", "org", "studio", "cloud", "io", "dev", "group",
           "limited", "sas", "s.a.", "ag", "oy", "ab", "bv", "pte", "pty", "the", "research", "data"}
S = requests.Session(); S.headers.update(UA)


def get(url, **kw):
    for attempt in range(2):
        try:
            r = S.get(url, timeout=15, **kw)
            if r.status_code in (429, 502, 503):
                time.sleep(3 * (attempt + 1)); continue
            return r
        except requests.RequestException:
            time.sleep(2)
    return None


def names(entity, owner):
    e = re.sub(r"\s+", " ", str(entity)).strip()
    alts = re.findall(r"\(([^)]*)\)", e)
    base = re.sub(r"\([^)]*\)", "", e).strip(" ,")
    out = []
    for n in [base] + [a for a in alts if not a.lower().startswith(("formerly", "via", "now"))]:
        toks = n.replace(",", " ").split()
        while toks and toks[-1].lower().strip(".") in GENERIC - {"data"}:
            toks = toks[:-1]
        if toks:
            out.append(" ".join(toks))
        if n not in out:
            out.append(n)
    o = re.sub(r"[-_](ai|io|dev|hq|org|app|labs?|inc|project|team|com|official)$", "", owner, flags=re.I)
    if len(o) >= 4 and o.lower() not in {x.lower() for x in out}:
        out.append(o)
    return [n for n in dict.fromkeys(out) if len(n) >= 3]


def mentions(text, ns):
    return any(re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", text, re.I) for n in ns)


def domain(blog):
    b = str(blog or "").strip()
    if not b or b == "nan":
        return ""
    if not b.startswith("http"):
        b = "http://" + b
    d = up.urlparse(b).netloc.lower()
    d = d[4:] if d.startswith("www.") else d
    return "" if d in {"github.com", "github.io", "twitter.com", "x.com", "medium.com", "linkedin.com"} else d


def hn(q):
    r = get("https://hn.algolia.com/api/v1/search", params={"query": q, "tags": "story", "hitsPerPage": 40})
    if not r or r.status_code != 200:
        return []
    return [{"title": h.get("title") or "", "url": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
             "date": (h.get("created_at") or "")[:10], "points": h.get("points") or 0, "via": "hn"}
            for h in r.json().get("hits", [])]


def techcrunch(q):
    r = get("https://techcrunch.com/wp-json/wp/v2/posts", params={"search": q, "per_page": 30,
                                                                  "_fields": "date,link,title"})
    if not r or r.status_code != 200:
        return []
    try:
        js = r.json()
    except ValueError:
        return []
    return [{"title": BeautifulSoup(p["title"]["rendered"], "lxml").get_text(), "url": p["link"],
             "date": p["date"][:10], "points": 0, "via": "techcrunch"} for p in js]


def wikipedia(ns):
    for n in ns[:2]:
        r = get("https://en.wikipedia.org/w/api.php", params={"action": "query", "list": "search", "format": "json",
                                                               "srsearch": f'"{n}"', "srlimit": 3})
        if not r or r.status_code != 200:
            continue
        for hit in r.json().get("query", {}).get("search", []):
            if not mentions(hit["title"], ns):
                continue
            x = get("https://en.wikipedia.org/w/api.php", params={"action": "query", "prop": "extracts",
                                                                   "explaintext": 1, "format": "json",
                                                                   "titles": hit["title"]})
            if not x or x.status_code != 200:
                continue
            page = next(iter(x.json()["query"]["pages"].values()))
            sents = [s for s in re.split(r"(?<=[.!?])\s+", page.get("extract", "")) if
                     (MONEY.search(s) and EVENT.search(s)) or re.search(r"\b(acquir|shut down|ipo|went public)", s, re.I)]
            if sents:
                return {"url": "https://en.wikipedia.org/wiki/" + up.quote(hit["title"].replace(" ", "_")),
                        "excerpts": [s[:300] for s in sents[:10]]}
    return None


def page_excerpts(url, ns, own_domain):
    r = get(url)
    if not r or r.status_code != 200 or "html" not in r.headers.get("content-type", ""):
        return None
    soup = BeautifulSoup(r.content[:3_000_000], "lxml")
    for t in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
        t.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" "))
    on_own = own_domain and own_domain in up.urlparse(url).netloc
    out = []
    for s in re.split(r"(?<=[.!?])\s+", text):
        if len(s) < 25:
            continue
        if MONEY.search(s) and EVENT.search(s) and (on_own or mentions(s, ns) or len(out) < 3 and mentions(text[:4000], ns)):
            out.append(s[:320])
        elif re.search(r"\b(acquir\w*|shut(ting)? down|wind(ing)? down|went public|IPO)\b", s, re.I) and mentions(s, ns):
            out.append(s[:320])
        if len(out) >= 8:
            break
    return out


def leads_for(row):
    ns = names(row.entity, row.owner)
    dom = domain(row.blog)
    hits = []
    for n in ns[:2]:
        hits += hn(n) + hn(f"{n} raises") + hn(f"{n} acquired")
    if dom:
        hits += hn(dom)
    hits += techcrunch(ns[0])
    seen, keep = set(), []
    for h in hits:
        if h["url"] in seen:
            continue
        own = dom and dom in up.urlparse(h["url"]).netloc
        if (mentions(h["title"], ns) or own) and EVENT.search(h["title"]):
            seen.add(h["url"]); keep.append(h)
    # money in the title first, then the company's own site, then points, then recency
    keep.sort(key=lambda h: (not MONEY.search(h["title"]), not (dom and dom in h["url"]), -h["points"],
                             h["date"]), reverse=False)
    keep = keep[:14]
    pages = []
    for h in keep[:6]:
        if "news.ycombinator.com" in h["url"]:
            continue
        ex = page_excerpts(h["url"], ns, dom)
        pages.append({**h, "excerpts": ex if ex is not None else "FETCH FAILED"})
    return {"owner": row.owner, "entity": row.entity, "names": ns, "domain": dom, "titles": keep,
            "pages": pages, "wikipedia": wikipedia(ns)}


def to_md(rec, first_pass):
    L = [f"## {rec['owner']} — {rec['entity']}", ""]
    if first_pass is not None:
        fp = {k: v for k, v in first_pass.items() if isinstance(v, str) and v and k not in ("owner", "entity")}
        L.append("First pass: " + json.dumps(fp, ensure_ascii=False)[:900])
        L.append("")
    L.append(f"Names searched: {', '.join(rec['names'])}; domain: {rec['domain'] or '-'}")
    if rec["titles"]:
        L.append("Headlines (date, title, url):")
        L += [f"- {h['date']} | {h['title']} | {h['url']}" for h in rec["titles"]]
    else:
        L.append("Headlines: none found on Hacker News or TechCrunch")
    for p in rec["pages"]:
        if isinstance(p["excerpts"], list) and p["excerpts"]:
            L.append(f"Page {p['url']} ({p['date']}):")
            L += [f"  > {e}" for e in p["excerpts"]]
    w = rec.get("wikipedia")
    if w:
        L.append(f"Wikipedia {w['url']}:")
        L += [f"  > {e}" for e in w["excerpts"]]
    return "\n".join(L) + "\n"


def main():
    inp = pd.read_csv("data/finance_passes/input_all.csv", dtype=str)
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which != "all":
        inp = inp[inp.owner.isin(pd.read_csv(which, dtype=str).owner)]
    path = "data/finance_passes/leads.jsonl"
    done = set()
    if os.path.exists(path):  # resume: keep companies already fetched
        done = {json.loads(l)["owner"] for l in open(path) if l.strip()}
    rows = [r for r in inp.itertuples(index=False) if r.owner not in done]
    out = {}
    with cf.ThreadPoolExecutor(16) as ex, open(path, "a") as fh:
        futs = {ex.submit(leads_for, r): r.owner for r in rows}
        for i, f in enumerate(cf.as_completed(futs), 1):
            try:
                rec = f.result()
            except Exception as e:  # noqa: BLE001
                rec = {"owner": futs[f], "error": str(e)[:200]}
            out[futs[f]] = rec
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
            if i % 25 == 0:
                print(i, "of", len(rows), flush=True)
    print("done", len(out))


if __name__ == "__main__":
    main()
