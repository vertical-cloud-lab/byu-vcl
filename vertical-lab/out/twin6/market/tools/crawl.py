"""Run a plan of searches through the tunnelled Chrome, round-robin across sites, at a person's pace.

    python3 crawl.py plan.json [--skip-done]
Writes one line per listing card to /tmp/market/raw/search.jsonl and one line per page to visits.jsonl.
A site that answers with a challenge or block twice is dropped for the rest of the run (recorded, not retried).
"""
import json, random, sys, time
from collections import defaultdict, deque
from urllib.parse import quote_plus
import browse as B

SITES = {
    "labx": ("https://www.labx.com/search-a?sw={q}", 'a[href*="/item/"]'),
    "machinio": ("https://www.machinio.com/listings?search={q}", 'a[href*="/listings/"]'),
    "govdeals": ("https://www.govdeals.com/en/search?kWord={q}", 'a[href*="/asset/"]'),
    "allsurplus": ("https://www.allsurplus.com/en/search?kWord={q}", 'a[href*="/asset/"]'),
    "publicsurplus": ("https://www.publicsurplus.com/sms/browse/search?posting=y&keyWord={q}", 'a[href*="auction/view"]'),
    "fedequip": ("https://fedequip.com/ssearch?search={q}", 'a[href*="/inventory/"]'),
    "machineseeker": ("https://www.machineseeker.com/main/search/index?search-word={q}", 'a[href*="/i-"]'),
    "exapro": ("https://www.exapro.com/product-search/?text={q}", 'a[href*="-p"][href*="exapro.com/"]'),
    "dotmed": ("https://www.dotmed.com/listings/search_equipment.html?key={q}", 'a[href*="/listing/"]'),
    "marshall": ("https://www.marshallscientific.com/search?q={q}", 'a[href*="/products/"]'),
    "conquer": ("https://conquerscientific.com/?s={q}&post_type=product", 'a[href*="/product/"]'),
    "gmi": ("{url}", 'a[href*="gmi-inc.com/product/"]'),
    "rdr": ("{url}", 'a[href*="/inventory/universal-robots/"]'),
    "semtech": ("{url}", 'a[href*="semtechsolutions.com/"][href*="/sem"], a[href*="semtechsolutions.com/"][href*="refurbished"]'),
}

def main():
    plan = json.load(open(sys.argv[1]))
    done = set()
    if "--skip-done" in sys.argv:
        try:
            for l in open(B.RAW / "visits.jsonl"):
                v = json.loads(l)
                if v.get("label", "").startswith("search|") and not v.get("blocked") and not v.get("error"):
                    done.add(v["label"])
        except FileNotFoundError:
            pass
    queues = defaultdict(deque)
    for st, q, sites in plan:
        for s in sites:
            lab = f"search|{s}|{st}|{q}"
            if lab not in done:
                queues[s].append((st, q, lab))
    strikes = defaultdict(int)
    only = None
    for a in sys.argv:
        if a.startswith("--sites="):
            only = set(a.split("=", 1)[1].split(","))
    if only:
        queues = defaultdict(deque, {s: q for s, q in queues.items() if s in only})
    for a in sys.argv:
        if a.startswith('--cdp='):
            B.CDP = 'http://127.0.0.1:' + a.split('=', 1)[1]
    pw, br, ctx, page = B.connect()
    if "--newtab" in sys.argv:
        page = ctx.new_page()
    n = 0
    order = list(queues)
    while any(queues[s] for s in order):
        random.shuffle(order)
        for s in order:
            if not queues[s] or strikes[s] >= 2:
                continue
            st, q, lab = queues[s].popleft()
            tmpl, sel = SITES[s]
            url = q if tmpl == "{url}" else tmpl.format(q=quote_plus(q))
            r = B.visit(page, url, label=lab, gap=(4.0, 9.0))
            if r["blocked"] or (r["status"] and r["status"] >= 400):
                strikes[s] += 1
                print(f"BLOCK {s} {r['status']} {r['blocked']} {q}", flush=True)
                continue
            cs = B.cards(page, sel)
            t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with open(B.RAW / "search.jsonl", "a") as f:
                for c in cs:
                    f.write(json.dumps(dict(station=st, site=s, query=q, search_url=url, seen_utc=t, **c)) + "\n")
            n += 1
            print(f"{n} {s:13s} {st:12s} {q[:40]:40s} cards={len(cs)}", flush=True)
    for s in order:
        if strikes[s] >= 2:
            print(f"DROPPED {s}: left {len(queues[s])} searches", flush=True)
    pw.stop()

if __name__ == "__main__":
    main()
