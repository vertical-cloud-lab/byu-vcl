#!/usr/bin/env python3
"""Link GitHub owners and repositories to Wikidata entities, and pull what Wikidata records about them.

Two bridges: entities whose GitHub username (P2037) matches an owner login, and software entities whose source
code repository (P1324) is a repository in either frame, with their developer (P178). For every entity reached,
the script records its types (P31), country, inception, dissolution, stock exchange and ticker, owner, parent
organization, website, employees and latest total revenue.

Writes data/wikidata_github_usernames.csv, data/wikidata_repo_links.csv and data/wikidata_entities.csv.
Run from owners/ after harvest_github.py.
"""
import re, time
import pandas as pd, requests

UA = {"User-Agent": "open-source-owner-study/0.1 (research script)", "Accept": "text/csv"}


def sparql(q):
    for attempt in range(5):
        r = requests.get("https://query.wikidata.org/sparql", params={"query": q}, headers=UA, timeout=120)
        if r.status_code == 200:
            from io import StringIO
            return pd.read_csv(StringIO(r.text), dtype=str)
        print("wikidata HTTP", r.status_code, r.text[:120].replace("\n", " "), flush=True)
        time.sleep(10 * (attempt + 1))
    r.raise_for_status()


def qid(s):
    return s.str.replace("http://www.wikidata.org/entity/", "", regex=False)


import os, sys
if "--reuse" in sys.argv and os.path.exists("data/wikidata_repo_links.csv"):
    usernames = pd.read_csv("data/wikidata_github_usernames.csv", dtype=str)
    repos = pd.read_csv("data/wikidata_repo_links.csv", dtype=str).fillna({"dev": ""})
else:
    usernames = sparql("SELECT ?item ?gh WHERE { ?item wdt:P2037 ?gh . }")
    usernames["item"] = qid(usernames["item"])
    usernames.to_csv("data/wikidata_github_usernames.csv", index=False)

    repos = sparql("""SELECT ?item ?repo ?dev WHERE { ?item wdt:P1324 ?repo .
      FILTER(STRSTARTS(STR(?repo), "https://github.com/")) OPTIONAL { ?item wdt:P178 ?dev } }""")
    repos["item"] = qid(repos["item"]); repos["dev"] = qid(repos["dev"].fillna(""))
    repos["full_name"] = (repos["repo"].str.replace("https://github.com/", "", regex=False)
                          .str.replace(r"\.git$", "", regex=True).str.strip("/").str.split("/").str[:2].str.join("/"))
    repos.to_csv("data/wikidata_repo_links.csv", index=False)

a = pd.read_csv("data/repos_frame_a.csv"); b = pd.read_csv("data/repos_frame_b.csv")
o = pd.read_csv("data/owners_github.csv")
logins = set(o.owner.str.lower())
names = set(pd.concat([a.full_name, b.full_name]).str.lower())
u = usernames[usernames.gh.str.lower().isin(logins)]
r = repos[repos.full_name.str.lower().isin(names)]
ents = sorted(x for x in set(u.item) | set(r.dev) if re.fullmatch(r"Q\d+", str(x)))  # owners and developers of linked software; drops 'unknown value' blank nodes
print("matched usernames", len(u), "repo links", len(r), "entities", len(ents))

# One small query per property, then aggregate here: a single query with every OPTIONAL multiplies rows and times out.
PROPS = {"types": "wdt:P31", "country": "wdt:P17", "inception": "wdt:P571", "dissolved": "wdt:P576",
         "exchanges": "wdt:P414", "owned_by": "wdt:P127", "parent": "wdt:P749", "website": "wdt:P856",
         "employees": "wdt:P1128", "developer": "wdt:P178"}
LITERAL = {"inception", "dissolved", "website", "employees"}
ent = pd.DataFrame({"item": ents})
for col, prop in PROPS.items():
    parts = []
    for i in range(0, len(ents), 200):
        vals = " ".join(f"wd:{e}" for e in ents[i:i + 200])
        if col in LITERAL:
            q = f"SELECT ?e ?v WHERE {{ VALUES ?e {{ {vals} }} ?e {prop} ?v . }}"
        else:
            q = f"""SELECT ?e ?v WHERE {{ VALUES ?e {{ {vals} }} ?e {prop} ?x .
              ?x rdfs:label ?v . FILTER(LANG(?v) = "en") }}"""
        parts.append(sparql(q)); time.sleep(0.5)
    d = pd.concat(parts)
    if len(d):
        d["e"] = qid(d["e"])
        ent = ent.merge(d.groupby("e")["v"].apply(lambda s: "|".join(sorted(set(map(str, s))))).rename(col),
                        left_on="item", right_index=True, how="left")
    print(col, len(d), flush=True)
tick = []
for i in range(0, len(ents), 200):
    vals = " ".join(f"wd:{e}" for e in ents[i:i + 200])
    tick.append(sparql(f"SELECT ?e ?t WHERE {{ VALUES ?e {{ {vals} }} ?e p:P414 ?st . ?st pq:P249 ?t . }}"))
tick = pd.concat(tick)
if len(tick):
    tick["e"] = qid(tick["e"])
    ent = ent.merge(tick.groupby("e")["t"].apply(lambda s: "|".join(sorted(set(s)))).rename("tickers"),
                    left_on="item", right_index=True, how="left")
lab = []
for i in range(0, len(ents), 200):
    vals = " ".join(f"wd:{e}" for e in ents[i:i + 200])
    lab.append(sparql(f'SELECT ?e ?l WHERE {{ VALUES ?e {{ {vals} }} ?e rdfs:label ?l . FILTER(LANG(?l) = "en") }}'))
lab = pd.concat(lab); lab["e"] = qid(lab["e"])
ent = ent.merge(lab.drop_duplicates("e").rename(columns={"e": "item", "l": "label"}), on="item", how="left")

# latest total revenue (P2139) with its point in time and unit
rev = []
for i in range(0, len(ents), 200):
    vals = " ".join(f"wd:{e}" for e in ents[i:i + 200])
    d = sparql(f"""SELECT ?e ?amount ?unitLabel ?when WHERE {{ VALUES ?e {{ {vals} }}
      ?e p:P2139 ?st . ?st psv:P2139 ?v . ?v wikibase:quantityAmount ?amount ; wikibase:quantityUnit ?unit .
      OPTIONAL {{ ?st pq:P585 ?when . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". ?unit rdfs:label ?unitLabel . }} }}""")
    rev.append(d)
    time.sleep(1)
rev = pd.concat(rev)
if len(rev):
    rev["e"] = qid(rev["e"])
    rev = rev.sort_values("when").groupby("e").tail(1).rename(
        columns={"amount": "revenue", "unitLabel": "revenue_unit", "when": "revenue_date"})
    ent = ent.merge(rev.rename(columns={"e": "item"}), on="item", how="left")
ent.to_csv("data/wikidata_entities.csv", index=False)
print("done", len(ent))
