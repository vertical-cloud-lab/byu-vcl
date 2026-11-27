"""Search cards -> candidate listings: the station each fits, price, currency, location, distance, condition hints.

    python3 parse.py            # /tmp/market/raw/search.jsonl -> /tmp/market/raw/candidates.json (+ a printed tally)
"""
import json, re, sys
from collections import Counter, defaultdict
import stations as STN

RAW = "/tmp/market/raw"
MONEY = [
    (r"(?:US[ ]?\$|(?<![A-Za-z])\$)[ ]?([\d]{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?(?![ ]?/[ ]?mo)(?!\d)", "USD"),
    (r"USD[ ]?([\d]{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?", "USD"),
    (r"€[ \u00a0]?([\d]{1,3}(?:[.,]\d{3})+|\d+)(?:,\d{2})?", "EUR"),
    (r"(?<![A-Za-z\d.,-])([\d]{1,3}(?:[.,]\d{3})+|\d+)[ \u00a0]?€", "EUR"),
    (r"EUR[ ]?([\d]{1,3}(?:[.,]\d{3})+|\d+)", "EUR"),
    (r"(?:GBP|£)[ ]?([\d]{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?", "GBP"),
    (r"CAD[ ]?\$?[ ]?([\d]{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?", "CAD"),
    (r"(?:CHF)[ ]?([\d]{1,3}(?:[.,']\d{3})+|\d+)", "CHF"),
    (r"(?:SEK)[ ]?([\d]{1,3}(?:[ .,]\d{3})+|\d+)", "SEK"),
    (r"(?:JPY|¥)[ ]?([\d]{1,3}(?:,\d{3})+|\d+)", "JPY"),
]
NOPRICE = r"please inquire|contact seller for price|request (a )?price|price info|price on request|call for price|" \
          r"request a quote|make (an )?offer|inquire|price upon request|ask for price|on request"


def money(text):
    """The first listed price that isn't a monthly payment. Returns (amount, currency) or (None, None)."""
    clean = re.sub(r"Est\.?\s?\$[\d,]+/mo", "", text)
    clean = re.sub(r"\$[\d,.]+\s?/\s?mo\w*", "", clean)
    best = None
    for pat, cur in MONEY:
        for m in re.finditer(pat, clean):
            raw = m.group(1)
            if cur in ("EUR", "CHF", "SEK"):
                v = float(re.sub(r"[.,' ]", "", raw))
            else:
                v = float(raw.replace(",", ""))
            if v < 1:
                continue
            if best is None or m.start() < best[2]:
                best = (v, cur, m.start())
    return (best[0], best[1]) if best else (None, None)


COND = [
    ("parts", r"for parts|not working|parts only|non-?working|for repair|defective|broken|does not (power|work|turn)|"
              r"won'?t (power|turn)|needs? repair|missing (parts|components)|incomplete"),
    ("refurbished", r"refurbish|reconditioned|rebuilt|remanufactur|certified pre-?owned|\bCPO\b|overhaul"),
    ("warranty", r"warrant(y|ied)|guarantee|\b\d+[- ]day (return|right of return)|money[- ]back"),
    ("tested", r"\btested\b|working condition|in working order|fully functional|ready for operation|"
               r"functionality: fully|operational|functional\b|demo (unit|instrument)|like new|excellent \(used\)|"
               r"calibrated|under power|can be seen running|in production|runs? (well|good|great)|"
               r"was working|working when (removed|taken)|good working"),
    ("as_is", r"\bas[- ]is\b|untested|not tested|where[- ]is|no warranty|unknown condition|condition unknown|"
              r"sold as is|buyer.*inspect"),
    ("new", r"\bnew in (box|crate)|\bunused\b|never used|\bNIB\b|new old stock|new surplus|brand new|"
            r"condition:\s?new\b|^new\n"),
]


def condition(text, site):
    t = text or ""
    hits = [c for c, p in COND if re.search(p, t, re.I | re.M)]
    if "parts" in hits:
        return "parts", hits
    if "refurbished" in hits or "warranty" in hits:
        return ("refurbished_warranty" if ("refurbished" in hits and "warranty" in hits) else
                ("refurbished" if "refurbished" in hits else "warranty")), hits
    if site in ("govdeals", "publicsurplus", "allsurplus"):
        return ("as_is_tested" if "tested" in hits else "as_is"), hits      # these auctions sell as-is, where-is
    if "new" in hits:
        return "new_surplus", hits
    if "tested" in hits:
        return "tested", hits
    if "as_is" in hits:
        return "as_is", hits
    m = re.match(r"\s*(New|Used|Refurbished|Demo|For Parts\w*|Parts)\b", t)
    if m and site == "labx":
        return {"new": "new_surplus", "used": "used", "refurbished": "refurbished", "demo": "tested"}.get(
            m.group(1).lower(), "parts"), hits
    return "used", hits


SELLER = {"govdeals": "government or university surplus auction", "publicsurplus": "government or university surplus auction",
          "allsurplus": "commercial surplus auction", "labx": "dealer or lab (LabX)", "machinio": "dealer (Machinio)",
          "machineseeker": "dealer (Machineseeker)", "exapro": "broker (Exapro)", "fedequip": "dealer (Federal Equipment)",
          "marshall": "dealer and refurbisher (Marshall Scientific)", "dotmed": "dealer or auction (DOTmed)"}


def location(text, site):
    lines = [l.strip() for l in (text or "").split("\n") if l.strip()]
    loc, dist_km = "", None
    m = re.search(r"·\s?([\d,]+)\s?mi\b", text or "")
    if m:
        dist_km = float(m.group(1).replace(",", "")) * 1.609
    m = re.search(r"\b([\d,.]+)\s?km\b", text or "")
    if m and dist_km is None:
        try:
            dist_km = float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    if site in ("govdeals", "allsurplus"):
        for l in lines[1:6]:
            if re.match(r"^[^,\d]{2,40}, [^,\d]{2,40}(, [A-Za-z]{3}|, USA)?$", l) and not l.startswith("ONLINE"):
                loc = l
                break
    elif site == "machinio":
        for i, l in enumerate(lines):
            if re.match(r"^[\U0001F1E6-\U0001F1FF]{2}$", l) and i + 1 < len(lines):
                loc = lines[i + 1]
                break
    elif site == "machineseeker":
        for i, l in enumerate(lines):
            if re.search(r"^[\d,.]+\s?km$", l) and i > 0:
                loc = lines[i - 1]
                break
    return loc, dist_km


def main():
    rows = [json.loads(l) for l in open(f"{RAW}/search.jsonl")]
    by = {}
    for r in rows:
        href = r["href"].split("#")[0]
        if r["site"] == "labx":
            href = href.split("?")[0]
        if r["site"] == "marshall":
            href = href.split("?")[0]
        key = href
        title = r["title"] or ""
        if r["site"] == "labx":
            title = re.sub(r"^(New|Used|Refurbished|Demo|For Parts\S*)\s+", "", title)
            title = re.sub(r"\s+(Please Inquire|\$[\d,.]+\s?USD.*)$", "", title)
        model = ""
        m = re.search(r"Manufacturer\n(.+)\nModel\n(.+)", r["text"])
        if m:
            model = f"{m.group(1)} {m.group(2)}"
        st = STN.classify(r["station"], title, model) if r["station"] in STN.S else None
        station = r["station"]
        if not st:
            for k in STN.S:
                if k == r["station"]:
                    continue
                c = STN.classify(k, title, model)
                if c in ("exact", "family"):
                    station, st = k, c
                    break
        if not st:
            continue
        amt, cur = money(r["text"])
        if re.search(NOPRICE, r["text"], re.I) and amt is None:
            amt = None
        cond, hits = condition(r["text"], r["site"])
        loc, dkm = location(r["text"], r["site"])
        auction = bool(re.search(r"ONLINE AUCTION|\bAuction\b|Time Left|Ends in|current bid|\bbid\b", r["text"], re.I)) or \
            r["site"] in ("govdeals", "publicsurplus", "allsurplus")
        rec = dict(station=station, match=st, comp=STN.component(station, title), site=r["site"], title=title,
                   model=model, url=href, amount=amt, currency=cur, price_kind=("current bid" if auction else "asking")
                   if amt else "on request", condition=cond, cond_hits=hits, location=loc, dist_km=dkm,
                   seller_type=SELLER.get(r["site"], ""), seen_utc=r["seen_utc"], query=r["query"],
                   card=r["text"][:900])
        old = by.get(key)
        if old is None or (old["match"] != "exact" and st == "exact"):
            by[key] = rec
    cands = list(by.values())
    json.dump(cands, open(f"{RAW}/candidates.json", "w"), indent=1)
    t = defaultdict(Counter)
    for c in cands:
        t[c["station"]][c["match"]] += 1
    for k in STN.S:
        if k in t:
            print(f"{k:13s} {dict(t[k])}")
    print(len(cands), "candidates from", len(rows), "cards")


if __name__ == "__main__":
    main()
