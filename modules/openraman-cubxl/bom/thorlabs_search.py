import json, sys, urllib.request
UA = "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
Q = """query($q: String) { products(storeId: "Thorlabs-Website", userId: "", currencyCode: "USD", cultureName: "en-US", query: $q, first: 15) {
 items { code itemStatusTL price { actual { formattedAmount } } descriptions { reviewType content } } } }"""
for term in sys.argv[1:]:
    req = urllib.request.Request("https://www.thorlabs.com/graphql", data=json.dumps({"query": Q, "variables": {"q": term}}).encode(),
        headers={"User-Agent": UA, "Content-Type": "application/json", "Origin": "https://www.thorlabs.com"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    print("##", term)
    for i in d["data"]["products"]["items"]:
        t = next((x["content"] for x in i["descriptions"] if x["reviewType"] == "Title"), "")
        print("  ", i["code"], i["price"]["actual"]["formattedAmount"], i["itemStatusTL"], "::", (t or "")[:120])
