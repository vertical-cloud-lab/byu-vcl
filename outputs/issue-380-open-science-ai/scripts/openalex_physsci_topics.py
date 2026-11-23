#!/usr/bin/env python3
"""OpenAlex counts by year for physical-science openness topics: self-driving labs, open-source hardware,
HardwareX papers; plus open-access share for SDL papers and US share. Writes data/openalex_physsci_topics.csv"""
import json, time, urllib.request, urllib.parse, csv
UA = {"User-Agent": "openalex-trends-script/1.0"}
def get(params):
    q = urllib.parse.urlencode(params)
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"https://api.openalex.org/works?{q}", headers=UA), timeout=60) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(5 * (i + 1))
    raise RuntimeError(params)
def by_year(filt):
    d = get({"filter": filt, "group_by": "publication_year", "per_page": 200}); time.sleep(1)
    return {int(g["key"]): g["count"] for g in d["group_by"]}
src = get({"search": "HardwareX", "per_page": 1}) if False else None
s = json.load(urllib.request.urlopen(urllib.request.Request("https://api.openalex.org/sources?search=HardwareX&per_page=3", headers=UA), timeout=60))
hx = s["results"][0]["id"].split("/")[-1]; print("HardwareX source", hx, s["results"][0]["display_name"])
Q = {
 "sdl_all": 'title_and_abstract.search:"self-driving lab" OR "self-driving laboratory" OR "autonomous laboratory" OR "autonomous experimentation"',
 "osh_all": 'title_and_abstract.search:"open-source hardware" OR "open source hardware" OR "open hardware"',
}
out = {}
for k, f in Q.items():
    base = f.replace("title_and_abstract.search:", "title_and_abstract.search:")
    out[k] = by_year(base + ",publication_year:2000-2025")
    out[k + "_oa"] = by_year(base + ",publication_year:2000-2025,open_access.is_oa:true")
    out[k + "_us"] = by_year(base + ",publication_year:2000-2025,authorships.institutions.country_code:us")
out["hardwarex"] = by_year(f"primary_location.source.id:{hx},publication_year:2016-2025")
years = range(2005, 2026)
with open("data/openalex_physsci_topics.csv", "w", newline="") as f:
    w = csv.writer(f); keys = list(out); w.writerow(["year"] + keys)
    for y in years: w.writerow([y] + [out[k].get(y, 0) for k in keys])
for k in out: print(k, {y: out[k].get(y, 0) for y in [2010, 2015, 2020, 2023, 2024, 2025]})
