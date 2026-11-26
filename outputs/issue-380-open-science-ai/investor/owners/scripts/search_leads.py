#!/usr/bin/env python3
"""Search leads for the fourth finance pass: the gaps part 2 left, filled with a search engine and the lab Pi.

Part 2's first pass ran out of web searches halfway, and its second pass worked from Hacker News and TechCrunch
alone, which miss small Chinese companies, very new AI projects and most quiet shutdowns. This script gives every
company a news search (Google News and Bing News RSS, which answer the runner directly) and fetches the best
pages through scripts/via_pi.py, so pages that refuse a datacenter come through the Pi.

Every company gets one Google News query for money and events (raises, funding, valuation, acquired, shut down).
Companies with a thin row (no funding figure, no $1B call, or unknown status) also get one by another name (the most
starred repository's, e.g. RAGFlow for InfiniFlow) and two Bing News queries; Chinese companies get two in Chinese
(融资, financing). Bing's web results were useless to an automated client, so no general web search is used. Hits must name the
company and mention an event. The best pages are fetched and the sentences that state an amount and a deal, or an
acquisition or shutdown, are kept with the page's URL and the route that fetched it.

Writes data/finance_passes/pi_leads.jsonl (one company per line; resumable). Run from owners/ with the SSH SOCKS
tunnel to the Pi open (see via_pi.py). Searches are spaced by via_pi's BING_GAP across all threads.
"""
import concurrent.futures as cf, json, os, re, sys, urllib.parse as up
import pandas as pd

sys.path.insert(0, "scripts")
import via_pi  # noqa: E402
from news_leads import EVENT, MONEY, names, mentions, domain  # noqa: E402

OUT = "data/finance_passes/pi_leads.jsonl"
EVENT_CN = re.compile(r"融资|投资|领投|跟投|估值|收购|并购|上市|关闭|倒闭|停止运营|轮")
MONEY_CN = re.compile(r"\d[\d.,]*\s*(亿|万)\s*(元|美元|人民币|美金|港元)?|数(千万|亿|百万)|(天使|种子|Pre-?A|A\+?|B\+?|C|D)\s*轮")
STATUS = re.compile(r"\b(acqui\w*|bought|buys|merg\w*|shut(s|ting)? down|wind(s|ing)? down|wound down|"
                    r"ceas\w* operations|went public|ipo|sunset\w*|closing (its|the) doors|layoffs?)\b", re.I)
SKIP = ("news.ycombinator.com", "twitter.com", "x.com", "facebook.com", "youtube.com", "linkedin.com/in/",
        "github.com", "reddit.com", "instagram.com", "tiktok.com")


def thin(r):
    return (str(r.ever_1b) == "unknown" or pd.isna(r.total_funding_usd) or str(r.status) == "unknown")


def relevant(h, ns, dom):
    blob = f"{h['title']} {h.get('snippet', '')}"
    own = dom and dom in up.urlparse(h["url"]).netloc
    if any(s in h["url"] for s in SKIP):
        return False
    named = mentions(blob, ns) or own
    return bool(named and (EVENT.search(blob) or EVENT_CN.search(blob) or MONEY.search(blob)))


def excerpts(url, ns, dom):
    res = via_pi.get(url, wayback=False)  # the archive is slow; leads don't need it (the agents' page reads use it)
    if not res["ok"]:
        return None, res.get("tried", "")
    text = via_pi.text_of_html(res["body"])
    on_own = dom and dom in up.urlparse(url).netloc
    named_early = mentions(text[:6000], ns)
    out = []
    for s in re.split(r"(?<=[.!?])\s+|(?<=[。！？])", text):
        if len(s) < 20:
            continue
        money = MONEY.search(s) or MONEY_CN.search(s)
        event = EVENT.search(s) or EVENT_CN.search(s)
        named = mentions(s, ns)
        if money and event and (named or on_own or (named_early and len(out) < 4)):
            out.append(s[:360])
        elif STATUS.search(s) and named:
            out.append(s[:360])
        if len(out) >= 10:
            break
    return out, res["route"]


STOP_REPOS = {"awesome", "docs", "examples", "website", "cookbook", "tutorials", "sdk", "cli", "server", "app", "api",
              "community", "roadmap", "blog", "demo", "templates", "starter", "skills", "agents", "models", "core"}
EVENTS_Q = 'raises OR funding OR valuation OR acquired OR acquisition OR "shut down" OR "shuts down" OR "winding down"'


def repo_name(top_repos, ns):
    """The org's most-starred repo name, as an extra search name, if it is distinctive (e.g. RAGFlow, Sealos)."""
    m = re.match(r"\s*([\w.-]+) \(", str(top_repos or ""))
    if not m:
        return None
    n = m.group(1)
    if len(n) < 5 or n.lower() in STOP_REPOS or any(n.lower() == x.lower().replace(" ", "") for x in ns):
        return None
    return n


def leads_for(r):
    ns = names(r.entity, r.owner)
    n0 = ns[0]
    rn = repo_name(r.top_repos, ns)
    if rn:
        ns = ns + [rn]
    dom = domain(r.blog)
    is_thin, is_cn = thin(r), str(r.country) == "CN"
    hits = via_pi.gnews(f'"{n0}" ({EVENTS_Q})')
    if is_thin:
        alt = rn or next((x for x in ns[1:] if x.lower() != n0.lower() and len(x) >= 5), None)
        if alt:
            hits += via_pi.gnews(f'"{alt}" (raises OR funding OR valuation OR acquired OR "shut down")')
        hits += via_pi.news(f'"{n0}" raises') + via_pi.news(f'"{n0}" funding')
    if is_cn:
        hits += via_pi.gnews(f'"{n0}" 融资', "zh")
        if rn:
            hits += via_pi.gnews(f'"{rn}" 融资', "zh")
    seen, keep = set(), []
    for h in hits:
        key = h.get("url") or h.get("gn_link") or ""
        h.setdefault("url", "")
        tkey = re.sub(r"\W+", " ", h["title"].lower()).strip()[:80]
        if not key or key in seen or tkey in seen or not relevant({**h, "url": h["url"] or h.get("source_url", "")},
                                                                  ns, dom):
            continue
        seen.add(key); seen.add(tkey); keep.append(h)
    # money in the title first, then status events, then the company's own site, then recency (newest first)
    keep.sort(key=lambda h: (not (MONEY.search(h["title"]) or MONEY_CN.search(h["title"])),
                             not STATUS.search(h["title"]), not (dom and dom in (h["url"] or h.get("source_url", ""))),
                             "".join(chr(255 - ord(c)) for c in (h.get("date") or ""))))
    keep = keep[:20]
    pages = []
    for h in keep[:4 if is_thin else 2]:
        if not h["url"] and h.get("gn_link"):
            h["url"] = via_pi.gdecode(h["gn_link"])
        if not h["url"]:
            continue
        ex, route = excerpts(h["url"], ns, dom)
        pages.append({"url": h["url"], "date": h.get("date", ""), "title": h["title"], "route": route,
                      "excerpts": ex if ex is not None else "FETCH FAILED"})
    for h in keep:
        h.pop("snippet", None)
    return {"owner": r.owner, "entity": r.entity, "names": ns, "domain": dom, "thin": int(is_thin),
            "country": None if pd.isna(r.country) else r.country, "hits": keep, "pages": pages}


def main():
    F = pd.read_csv("data/core_financials.csv")
    inp = pd.read_csv("data/finance_passes/input_all.csv", dtype=str)[["owner", "blog", "top_repos"]]
    F = F.merge(inp, on="owner", how="left")
    C = F.drop_duplicates("entity").copy()
    C["is_thin"] = C.apply(thin, axis=1)
    # the companies with no $1B call first, then the other thin rows, then the rest; by stars within each
    C["prio"] = (C.ever_1b != "unknown").astype(int) + (~C.is_thin).astype(int)
    C = C.sort_values(["prio", "stars"], ascending=[True, False])
    if len(sys.argv) > 1:
        C = C[C.owner.isin(sys.argv[1:])]
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["owner"] for l in open(OUT) if l.strip()}
    todo = [r for r in C.itertuples(index=False) if r.owner not in done]
    print(f"companies {len(C)}, thin {int(C.is_thin.sum())}, to do {len(todo)}", flush=True)
    with cf.ThreadPoolExecutor(12) as ex, open(OUT, "a") as fh:
        futs = {ex.submit(leads_for, r): r.owner for r in todo}
        for i, f in enumerate(cf.as_completed(futs), 1):
            try:
                rec = f.result()
            except Exception as e:  # noqa: BLE001
                rec = {"owner": futs[f], "error": f"{type(e).__name__}: {str(e)[:200]}"}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
            if i % 20 == 0:
                print(i, "of", len(todo), flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
