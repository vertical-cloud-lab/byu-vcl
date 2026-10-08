"""Parse saved Amazon pages into JSON on stdout.

    python parse_amazon.py search "q1.html::magnetic cable holder" ... > amazon_search_<date>.json
    python parse_amazon.py product p_B09M8L4GQV.html ...              > amazon_products_<date>.json

Search pages are given as `path::query`. Product pages must be named `p_<ASIN>.html`. The
pages were fetched with curl from the CubXL Pi (see README.md); this runs anywhere with
beautifulsoup4 and lxml.
"""

import json
import re
import sys

from bs4 import BeautifulSoup


def text(el):
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""


def soup(path):
    return BeautifulSoup(open(path, encoding="utf-8", errors="replace").read(), "lxml")


def search(path, query):
    rows = []
    cards = soup(path).select('div[data-component-type="s-search-result"]')
    for rank, card in enumerate(cards, 1):
        asin = card.get("data-asin", "")
        if not asin:
            continue
        h2s = [text(h) for h in card.select("h2")]
        title = max(h2s, key=len) if h2s else ""
        stars = re.match(r"([\d.]+) out of 5", text(card.select_one("span.a-icon-alt")))
        ratings = None
        for el in card.select("a[href*='customerReviews'], span[aria-label$='ratings'], "
                              "span[aria-label$='rating']"):
            label = (el.get("aria-label") or text(el)).replace("(", "").replace(")", "")
            m = re.search(r"([\d,.]+)\s*([Kk])?", label)
            if m:
                n = float(m.group(1).replace(",", ""))
                ratings = int(n * 1000) if m.group(2) else int(n)
                break
        bought = card.find(string=re.compile(r"bought in past month"))
        rows.append(dict(
            query=query, rank=rank, asin=asin,
            brand=h2s[0] if len(h2s) > 1 and h2s[0] != title else "",
            title=title,
            price=text(card.select_one("span.a-price:not(.a-text-price) span.a-offscreen")),
            list_price=text(card.select_one("span.a-price.a-text-price span.a-offscreen")),
            stars=float(stars.group(1)) if stars else None,
            ratings=ratings,
            bought_past_month=text(bought.parent) if bought else "",
            sponsored=bool(card.find(string=re.compile(r"^\s*Sponsored\s*$"))),
            url=f"https://www.amazon.com/dp/{asin}",
        ))
    return rows


def product(path):
    s = soup(path)
    specs = {}
    for row in s.select("#productOverview_feature_div tr, #productDetails_techSpec_section_1 tr, "
                        "#productDetails_detailBullets_sections1 tr, "
                        "#technicalSpecifications_section_1 tr"):
        key, vals = row.select_one("th, td"), row.select("td")
        if key is not None and vals:
            specs[text(key)] = text(vals[-1])
    for li in s.select("#detailBullets_feature_div li"):
        if ":" in text(li):
            k, v = text(li).split(":", 1)
            specs[k.strip(" ‎‏")] = v.strip(" ‎‏")
    for k in ("Customer Reviews", "Best Sellers Rank"):
        specs.pop(k, None)
    variants = [v for v in (text(li) for li in s.select("[id^=inline-twister] li, #twister li"))
                if v and v not in "←→" and not v.isdigit()]
    asin = re.search(r"p_(B\w+)\.html", path).group(1)
    return dict(
        asin=asin,
        title=text(s.select_one("#productTitle")),
        price=text(s.select_one("#corePrice_feature_div span.a-offscreen"))
        or text(s.select_one("#corePriceDisplay_desktop_feature_div span.a-offscreen"))
        or text(s.select_one("span.a-price span.a-offscreen")),
        rating=text(s.select_one("#acrPopover span.a-icon-alt")),
        ratings=text(s.select_one("#acrCustomerReviewText")),
        variants=variants,
        bullets=[b for b in (text(li) for li in s.select("#feature-bullets li")) if b],
        description=text(s.select_one("#productDescription")),
        specs=specs,
        url=f"https://www.amazon.com/dp/{asin}",
    )


if __name__ == "__main__":
    mode, args = sys.argv[1], sys.argv[2:]
    if mode == "search":
        out = [row for a in args for row in search(*a.split("::", 1))]
    else:
        out = [product(a) for a in args]
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
    print()
