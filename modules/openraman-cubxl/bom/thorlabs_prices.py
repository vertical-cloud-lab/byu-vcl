"""Query Thorlabs' public storefront GraphQL (Virto xAPI) for US list prices.

Runs on the Pi (stdlib only). Prints one JSON object per part number.
"""
import json, sys, time, urllib.request

UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
URL = "https://www.thorlabs.com/graphql"
Q = """query($q: String) {
  products(storeId: "Thorlabs-Website", userId: "", currencyCode: "USD", cultureName: "en-US",
           query: $q, first: 60) {
    totalCount
    items { code name slug itemStatusTL altItemIdTL descriptions { reviewType content }
      price { actual { amount formattedAmount } list { amount formattedAmount }
              tierPrices { quantity price { amount } } }
      availabilityData { isActive isBuyable isInStock availableQuantity }
    }
  }
}"""

def query(term):
    body = json.dumps({"query": Q, "variables": {"q": term}}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json",
        "Origin": "https://www.thorlabs.com", "Referer": "https://www.thorlabs.com/"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

for term in sys.argv[1:]:
    try:
        d = query(term)
        if not d.get("data"):
            print(json.dumps({"term": term, "error": d.get("errors")})); continue
        items = d["data"]["products"]["items"]
        exact = [i for i in items if i["code"].upper() == term.upper()]
        print(json.dumps({"term": term, "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                          "exact": [dict({k: v for k, v in i.items() if k != "descriptions"}, title=next((x["content"] for x in (i.get("descriptions") or []) if x["reviewType"] == "Title"), None), url="https://www.thorlabs.com" + (next((x["content"] for x in (i.get("descriptions") or []) if x["reviewType"] == "ItemUrl"), None) or "")) for i in exact], "candidates": [i["code"] for i in items][:60]}))
    except Exception as e:
        print(json.dumps({"term": term, "error": repr(e)}))
    sys.stdout.flush()
    time.sleep(1.0)
