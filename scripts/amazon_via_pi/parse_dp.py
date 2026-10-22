#!/usr/bin/env python3
"""Parse saved Amazon product pages (untrusted HTML, treated as text only).

usage: python3 -I parse_dp.py <dp_*.html.gz> [...]
Prints one JSON object per page: title, price, rating, item weight, dimensions,
the "Customers say" summary, and feature bullets.
"""
import gzip, html, json, re, sys

def load(p):
    raw = open(p, "rb").read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")

def clean(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()

def field(doc, label):
    # table layout: <th ...> Item Weight </th> <td ...> 7.8 ounces </td>
    m = re.search(r"<th[^>]*>\s*" + label + r"\s*</th>\s*<td[^>]*>(.*?)</td>", doc, re.S | re.I)
    if m:
        return clean(m.group(1))
    # bullet layout: <span class="a-text-bold">Item Weight &rlm; : &lrm;</span> <span>7.8 ounces</span>
    m = re.search(label + r"[^<]{0,40}</span>\s*<span[^>]*>(.*?)</span>", doc, re.S | re.I)
    return clean(m.group(1)) if m else ""

for p in sys.argv[1:]:
    doc = load(p)
    out = {"file": p.rsplit("/", 1)[-1]}
    if "captcha" in doc.lower()[:20000] and "productTitle" not in doc:
        out["error"] = "captcha"
        print(json.dumps(out)); continue
    t = re.search(r'id="productTitle"[^>]*>(.*?)</span>', doc, re.S)
    out["title"] = clean(t.group(1)) if t else ""
    # buy-box price only; the first a-price on a page can belong to another item
    pr = re.search(r'id="corePrice(?:Display_desktop)?_feature_div".{0,3000}?<span class="a-offscreen">\s*(\$[\d,.]+)', doc, re.S)
    out["price"] = pr.group(1) if pr else ""
    if 'id="outOfStock' in doc and "Currently unavailable" in doc:
        out["availability"] = "Currently unavailable"
        out["price"] = ""
    else:
        av = re.search(r'id="availability"[^>]*>\s*<span[^>]*>(.*?)</span>', doc, re.S)
        out["availability"] = clean(av.group(1))[:80] if av else ""
    r = re.search(r'id="acrPopover"[^>]*title="([\d.]+) out of 5 stars"', doc)
    out["rating"] = r.group(1) if r else ""
    n = re.search(r'id="acrCustomerReviewText"[^>]*>\s*\(?([\d,]+)\)?\s*(?:ratings?)?', doc)
    out["ratings"] = n.group(1) if n else ""
    for lab in ["Item Weight", "Product Dimensions", "Package Dimensions", "Brand", "Date First Available", "Manufacturer", "Model Number", "Item model number", "Maximum Weight Recommendation"]:
        v = field(doc, lab)
        if v:
            out[lab] = v[:120]
    i = doc.find('data-testid="overall-summary"')
    if i > 0:
        out["customers_say"] = clean("<x " + doc[i:i + 6000])[:900]
    rows = re.findall(r'<th[^>]*prodDetSectionEntry[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>', doc, re.S)
    for k, v in rows:
        k = clean(k)
        if re.search(r"weight|dimension|material|capacity", k, re.I):
            out["tbl:" + k] = clean(v)[:120]
    fb = re.search(r'id="feature-bullets"(.*?)</ul>', doc, re.S)
    if fb:
        out["bullets"] = [clean(x)[:400] for x in re.findall(r"<li[^>]*>(.*?)</li>", fb.group(1), re.S)][:7]
    # any explicit gram / ounce figures anywhere in the description text
    body = clean(doc)
    out["mass_mentions"] = sorted(set([m.group(0) for m in re.finditer(r"(?:[Ww]eigh\w*|[Gg]ram\w*|[Ll]ightweight)[^.]{0,60}?\d{1,4}(?:\.\d+)?\s?(?:g|grams|oz|ounces|lbs?)\b", body)]))[:15]
    out["N_mentions"] = sorted(set(re.findall(r"\b\d{1,3}(?:\.\d+)?\s?N\b(?![a-z0-9])", body)))[:10]
    print(json.dumps(out))
