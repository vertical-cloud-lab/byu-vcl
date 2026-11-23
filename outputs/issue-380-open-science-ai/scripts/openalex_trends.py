#!/usr/bin/env python3
"""Open-access share of US research by institution type and year, from the OpenAlex API.

Counts works (articles) with at least one US-affiliated author of a given institution type
(education = academia, government = incl. national labs, company = industry, facility,
nonprofit, healthcare), split by open_access.is_oa, for all fields, the Physical Sciences
domain (id 3), Materials Science (field 25), Chemistry (16) and the AI subfield (1702).
"""
import json, time, urllib.request, urllib.parse, sys
BASE = "https://api.openalex.org/works"
TYPES = ["education", "government", "company", "facility", "nonprofit", "healthcare"]
SCOPES = {"all": "", "physical_sciences": ",primary_topic.domain.id:3", "materials": ",primary_topic.field.id:25",
          "chemistry": ",primary_topic.field.id:16", "ai": ",primary_topic.subfield.id:1702"}

def get(filt, group="publication_year"):
    q = urllib.parse.urlencode({"filter": filt, "group_by": group, "per_page": 200})
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(f"{BASE}?{q}", headers={"User-Agent": "openalex-trends-script/1.0"}), timeout=60) as r:
                d = json.load(r)
            return {g["key"]: g["count"] for g in d["group_by"]}
        except Exception as e:
            sys.stderr.write(f"retry {i} {e}\n"); time.sleep(10 * (i + 1))
    raise RuntimeError(filt)

out = {}
for scope, extra in SCOPES.items():
    for t in TYPES + ["any_us"]:
        base = "authorships.institutions.country_code:us,type:article,publication_year:1995-2025" + extra
        if t != "any_us":
            base += f",authorships.institutions.type:{t}"
        tot = get(base); time.sleep(1.2); oa = get(base + ",open_access.is_oa:true")
        out[f"{scope}|{t}"] = {"total": tot, "oa": oa}
        print(scope, t, "2024 total", tot.get("2024"), "oa", oa.get("2024"), flush=True)
        time.sleep(1.5)
# industry share of US AI articles (any company author) over time
json.dump(out, open("data/openalex_us_oa_by_sector.json", "w"), indent=1)
