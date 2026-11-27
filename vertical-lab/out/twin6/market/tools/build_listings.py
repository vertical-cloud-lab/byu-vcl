"""Candidates (search cards) + listing pages -> listings.csv, one row per listing.

    python3 build_listings.py <out_dir>
Reads /tmp/market/raw/{candidates.json,details.jsonl}. Detail-page fields override the card's.
"""
import csv, json, math, re, sys
from collections import defaultdict
import stations as STN
import parse as P

RAW = "/tmp/market/raw"
VL = "/home/runner/work/byu-vcl/byu-vcl/vertical-lab"
# ECB euro reference rates of 17 Nov 2026 (Banca d'Italia's republication): value of 1 EUR
EUR = dict(USD=1.0989, GBP=0.83305, CHF=0.9233, SEK=11.11, JPY=175.05, CAD=1.5704, PLN=4.4038, DKK=7.4749,
           CNY=7.3254, HUF=364.93, CZK=24.387, EUR=1.0)
FX_SRC = ("ECB euro reference rates, 17 Nov 2026, as republished by Banca d'Italia "
          "(https://www.bancaditalia.it/compiti/operazioni-cambi/cambio/cambi_rif_20261117)")


def usd(amount, cur):
    if amount is None or not cur:
        return None
    return round(amount * EUR["USD"] / EUR[cur], 2)


def g(pat, t, flags=re.I | re.M, grp=1):
    m = re.search(pat, t or "", flags)
    return m.group(grp).strip() if m else ""


def detail_fields(site, t):
    """Fields read off a listing page's text."""
    f = {}
    if not t:
        return f
    if site == "labx":
        head = t.split("More From")[0]
        f["seller"] = g(r"Sold By:\s*(.+)", head)
        f["location"] = g(r"Location:\s*\n(.+)", head)
        f["cond_label"] = g(r"Condition:\s*\n(.+)", head)
        f["warranty"] = g(r"Warranty:\s*\n(.+)", head)
        f["listed"] = g(r"Date Listed:\s*(.+)", head)
        f["updated"] = g(r"Last Updated:\s*(.+)", head)
        m = re.search(r"\$([\d,]+(?:\.\d\d)?)\s?USD", head)
        f["price"] = (float(m.group(1).replace(",", "")), "USD") if m else None
        f["no_price"] = bool(re.search(r"Please Inquire", head))
        f["desc"] = g(r"About This Listing\n([\s\S]{0,1500}?)(?:\nShipping\n|\nSeller Details)", head)
    elif site == "machinio":
        f["cond_label"] = g(r"^Condition\n(.+)", t)
        f["year"] = g(r"^Year\n(\d{4})", t)
        m = re.search(r"Location\n(?:[\U0001F1E6-\U0001F1FF]{2}\s?)?(.+?)\n·\s?([\d,]+)\s?mi away", t)
        if m:
            f["location"], f["dist_km"] = m.group(1).strip(), float(m.group(2).replace(",", "")) * 1.609
        m = re.search(r"\n(?:\$|US\$)([\d,]+)\s?USD\n|\n€([\d,.]+)\s?EUR\n|\n£([\d,]+)\s?GBP\n", t)
        if m:
            if m.group(1):
                f["price"] = (float(m.group(1).replace(",", "")), "USD")
            elif m.group(2):
                f["price"] = (float(re.sub(r"[.,]", "", m.group(2))), "EUR")
            else:
                f["price"] = (float(m.group(3).replace(",", "")), "GBP")
        f["no_price"] = "Contact Seller for Price" in t or "Request Price" in t
        f["seller"] = g(r"Seller Information\n(.+)", t)
        f["desc"] = g(r"\nDescription\n([\s\S]{0,1800}?)(?:\nShow more|\nClick to Request)", t)
    elif site == "machineseeker":
        m = re.search(r"\n(Starting price|Buy now price|Price|Fixed price plus VAT|Price plus VAT|Negotiable price)?\n?"
                      r"(€[\d.,]+|[\d.,]+\s?€|\$[\d,]+|£[\d,]+|CHF\s?[\d.,']+)\n", t)
        if m:
            amt, cur = P.money(m.group(2))
            f["price"] = (amt, cur) if amt else None
            f["price_kind"] = "starting bid" if (m.group(1) or "").startswith("Starting") else "asking"
        f["no_price"] = "Price info" in t[:1500] and not f.get("price")
        f["year"] = g(r"Year of construction:?\n(\d{4})", t)
        f["cond_label"] = g(r"^Condition:\n(.+)", t)
        f["function"] = g(r"^Functionality:\n(.+)", t)
        m = re.search(r"^Location:\n(.+?)(?:\s*–\s*Distance: about ([\d,.]+)\s?km)?\s*$", t, re.M)
        if m:
            f["location"] = m.group(1).strip()
            if m.group(2):
                f["dist_km"] = float(m.group(2).replace(",", ""))
        f["availability"] = g(r"^Availability:\n(.+)", t)
        f["delivery"] = g(r"^Delivery conditions:\n(.+)", t)
        f["dismantling"] = g(r"^Costs for dismantling & loading:\n(.+)", t)
        f["shipping"] = g(r"^Shipping costs:\n(.+)", t)
        f["desc"] = g(r"\nDescription\n([\s\S]{0,1800}?)(?:\nThe listing was translated|\n Request more information|\nSeller\n)", t)
        f["auction"] = bool(re.search(r"Observe auction|To the auction|Starting price|Ends in", t[:3000]))
    elif site == "exapro":
        f["year"] = g(r"^Year\t(\d{4})", t)
        f["location"] = g(r"^Location\t(.+)", t)
        f["cond_label"] = g(r"^state\t(.+)", t)
        f["availability"] = g(r"^Last availability date\t(.+)", t)
        f["weight_kg"] = g(r"^Weight\t([\d.]+) kg", t)
        m = re.search(r"\n(?:Price:?\s*)?(€\s?[\d.,]+|[\d.,]+\s?€)\s*(?:excl|\n)", t[:3000])
        if m:
            amt, cur = P.money(m.group(1))
            f["price"] = (amt, cur) if amt else None
        f["no_price"] = "Price on request" in t[:3000]
        f["desc"] = g(r"Automatic description \(AI-Generated\)\n([\s\S]{0,1500})", t)
    elif site in ("govdeals", "allsurplus"):
        m = re.search(r"Current Bid\s*\n?\s*(USD|GBP|EUR|CAD)?\s?\$?([\d,]+(?:\.\d\d)?)", t)
        if m:
            f["price"] = (float(m.group(2).replace(",", "")), m.group(1) or "USD")
            f["price_kind"] = "current bid"
        f["location"] = g(r"Location\s*\n(.+)", t)
        f["seller"] = g(r"(?:Seller|Sold by|Agency)\s*\n(.+)", t)
        f["desc"] = g(r"(?:Description|Item Description)\s*\n([\s\S]{0,1500}?)(?:\n(?:Payment|Pickup|Removal|Shipping|Terms))", t)
        f["availability"] = g(r"((?:Pickup|Removal)[^\n]{0,200})", t)
        f["shipping"] = g(r"(Shipping[^\n]{0,200})", t)
        f["ends"] = g(r"(?:Auction (?:ends|close)s?|Closing)\s*:?\s*\n?(.+)", t)
    elif site == "publicsurplus":
        m = re.search(r"Current Price\s*\n?\s*\$([\d,]+(?:\.\d\d)?)", t)
        if m:
            f["price"] = (float(m.group(1).replace(",", "")), "USD")
            f["price_kind"] = "current bid"
        f["seller"] = g(r"(?:Agency|Seller)\s*:?\s*\n?(.+)", t)
        f["location"] = g(r"Location\s*:?\s*\n?(.+)", t)
        f["desc"] = g(r"Description\s*\n([\s\S]{0,1500}?)(?:\n(?:Payment|Pick|Shipping|Terms|Bid History))", t)
        f["availability"] = g(r"((?:Pick ?up|Removal)[^\n]{0,200})", t)
        f["shipping"] = g(r"(Shipping[^\n]{0,200})", t)
    elif site == "marshall":
        m = re.search(r"\$([\d,]+(?:\.\d\d)?)\s*(?:USD)?\n", t[:4000])
        if m:
            f["price"] = (float(m.group(1).replace(",", "")), "USD")
        f["cond_label"] = g(r"Condition:?\s*\n?(Refurbished|Used|New|As[- ]Is[^\n]*)", t)
        f["warranty"] = g(r"((?:\d+[- ](?:day|month|year))[^\n]{0,60}warranty[^\n]{0,60})", t)
        f["location"] = "Cambridge, MA, US (Marshall Scientific)"
    elif site == "dotmed":
        m = re.search(r"Asking Price :\s*\n\s*\$([\d,]+(?:\.\d\d)?)", t)
        if m:
            f["price"] = (float(m.group(1).replace(",", "")), "USD")
        f["cond_label"] = g(r"^Condition :\s*\n(.+)", t)
        f["location"] = g(r"^Location :\s*\n(.+)", t)
        f["seller"] = g(r"^Seller Information\n(.+)", t)
        f["listed"] = g(r"^Date :\s*\n(.+)", t)
        f["availability"] = ("in stock" if re.search(r"^In Stock :\s*\nYes", t, re.M) else "")
        f["desc"] = g(r"Description([\s\S]{0,1200}?)\nReturn Policy", t)
    elif site == "fedequip":
        f["location"] = g(r"Location:?\s*\n?(.+)", t)
        f["desc"] = g(r"(Used [^\n]{0,600})", t)
    f["warranty_txt"] = g(r"([^\n]{0,80}\bwarrant[^\n]{0,120})", t)
    f["ship_txt"] = g(r"([^\n]{0,60}\b(?:ships? (?:in|within)|lead time|in stock|ready to ship|available (?:now|immediately)|"
                      r"immediately available|availability)[^\n]{0,100})", t)
    m = re.search(r"(?:machine weight|net weight|gross weight|total weight|weight)\s*(?:\(?approx\.?\)?)?[:\s]*([\d.,]+)\s?"
                  r"(kg|lbs?|t)\b", t, re.I)
    if m and not f.get("weight_kg"):
        try:
            v = float(m.group(1).replace(",", ""))
            f["weight_kg"] = v * (0.4536 if m.group(2).startswith("lb") else 1000 if m.group(2) == "t" else 1)
        except ValueError:
            pass
    return f


COUNTRY_US = r"\b(USA|US|United States|[A-Z]{2}, USA|Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|" \
             r"Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|" \
             r"Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|" \
             r"New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|" \
             r"South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|" \
             r"Wyoming|, (AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|" \
             r"NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b)"


def region(loc, dist_km):
    if re.search(COUNTRY_US, loc or ""):
        return "US"
    if re.search(r"Canada|, (ON|QC|BC|AB|MB|SK|NS|NB)\b", loc or ""):
        return "CA"
    if dist_km is not None and dist_km < 3500:
        return "US"
    if loc:
        return "overseas"
    return ""


def main(out_dir):
    cands = json.load(open(f"{RAW}/candidates.json"))
    det = {}
    try:
        for l in open(f"{RAW}/details.jsonl"):
            d = json.loads(l)
            if d.get("status") == 200 and not d.get("blocked"):
                det[d["url"]] = d
    except FileNotFoundError:
        pass
    rows = []
    for c in cands:
        d = det.get(c["url"])
        f = detail_fields(c["site"], d["text"]) if d else {}
        amt, cur = (f["price"] if f.get("price") else (c["amount"], c["currency"]))
        kind = f.get("price_kind") or (c["price_kind"] if amt else "on request")
        if c["site"] in ("govdeals", "allsurplus", "publicsurplus") and amt:
            kind = "current bid"
        if c["site"] == "machineseeker" and f.get("auction") and amt:
            kind = "starting bid" if kind != "current bid" else kind
        text_for_cond = "\n".join([c["card"], f.get("cond_label", ""), f.get("function", ""), f.get("warranty", ""),
                                   f.get("desc", ""), f.get("warranty_txt", "")])
        cond, hits = P.condition(text_for_cond, c["site"])
        lab = (f.get("cond_label") or "").lower()
        if c["site"] == "labx" and lab:
            cond = {"refurbished": "refurbished", "used": "used", "new": "new_surplus", "demo": "tested"}.get(lab, cond)
            if (f.get("warranty") or "").lower().startswith("yes"):
                cond = "refurbished_warranty" if cond == "refurbished" else "warranty"
            if "parts" in lab or "not working" in lab:
                cond = "parts"
        loc = f.get("location") or c["location"]
        dkm = f.get("dist_km") or c["dist_km"]
        rows.append(dict(
            station=c["station"], component=c.get("comp", ""), match=c["match"], title=c["title"][:200],
            source=c["site"], url=c["url"], price=amt, currency=cur or "", price_usd=usd(amt, cur), price_kind=kind,
            condition=cond, condition_evidence="; ".join(sorted(set(h for h in hits)))[:120],
            cond_label=(f.get("cond_label") or "")[:60], warranty=(f.get("warranty") or "")[:60],
            year=f.get("year", ""), location=(loc or "")[:80], region=region(loc, dkm),
            dist_km=round(dkm) if dkm else "", seller_type=c["seller_type"], seller=(f.get("seller") or "")[:60],
            availability=(f.get("availability") or f.get("ship_txt") or "")[:160],
            delivery_terms="; ".join(x for x in [f.get("delivery", ""), ("dismantling & loading: " + f["dismantling"])
                                                  if f.get("dismantling") else "", ("shipping: " + f["shipping"])
                                                  if f.get("shipping") else ""] if x)[:160],
            weight_kg=round(f["weight_kg"]) if f.get("weight_kg") else "",
            date_seen=(d["t_utc"] if d else c["seen_utc"])[:10], detail_read=bool(d),
            shot=(d or {}).get("shot", "")))
    # the same unit listed twice (two sites, or two searches that reached it by different URLs): same station, same
    # price within 1 %, and the same model tokens; or, unpriced, the same title and place. Later copies get keep=0.
    def toks(t):
        t = STN.norm(t).lower()
        t = re.sub(r"\b([a-z]{1,4})[\s-]+(\d)", r"\1\2", t)            # 'st-10', 'tm 3030' -> 'st10', 'tm3030'
        words = set(re.findall(r"[a-z0-9]*\d[a-z0-9]*|[a-z]{3,}", t))
        return " ".join(sorted(words - {"used", "for", "sale", "with", "and", "the", "cnc", "machine", "industrial",
                                        "robot", "cobot", "robots"}))
    seen = {}
    for r in rows:
        r["keep"] = 1
        r["dup_of"] = ""
        p = r["price_usd"]
        if p:
            k = (r["station"], r["component"], round(math.log(p) / math.log(1.01)), toks(r["title"]))
        elif r["location"] and r["year"]:
            k = (r["station"], r["component"], None, toks(r["title"]), r["location"], r["year"])
        else:
            k = None
        if k is not None and k in seen:
            r["keep"], r["dup_of"] = 0, seen[k]
        elif k is not None:
            seen[k] = r["url"]
    for r in rows:
        r.setdefault("reason", "")
        if r["source"] == "labx" and r["condition"] == "new_surplus":
            r["keep"], r["reason"] = 0, "new equipment advertised on LabX, not a used unit"
        elif r["keep"] == 0 and r["dup_of"]:
            r["reason"] = "the same unit as dup_of"
    ov = {}
    try:
        for o in csv.DictReader(open(f"{out_dir}/overrides.csv")):
            ov[o["url"]] = o
    except FileNotFoundError:
        pass
    for r in rows:
        o = ov.get(r["url"])
        if not o:
            continue
        for k in ("station", "component", "match", "condition"):
            if o.get(k):
                r[k] = o[k]
        if o.get("keep", "") != "":
            r["keep"] = int(o["keep"])
        if o.get("reason"):
            r["reason"] = o["reason"]
    # freight and rigging, and the lead to site, per listing: the same tables the summary uses (twin/market6.py)
    sys.path.insert(0, VL)
    from twin import market6 as M
    wt_of = {}
    for n in csv.DictReader(open(f"{VL}/out/twin6/market/new.csv")):
        wt_of[(n["station"], n["component"])] = n["wt"]
        wt_of.setdefault((n["station"], ""), n["wt"])
    for r in rows:
        wt = wt_of.get((r["station"], r["component"])) or wt_of.get((r["station"], "")) or STN.S.get(
            r["station"], {}).get("wt", "bench")
        r["ship_class"] = wt
        r["freight_rigging_usd"] = M.freight(wt, r["region"], r["dist_km"] or None)
        r["lead_w_est"] = M.lead_of(r, wt)
    keys = list(rows[0].keys()) if rows else []
    with open(f"{out_dir}/listings_raw.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "rows ->", f"{out_dir}/listings_raw.csv")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/market")
