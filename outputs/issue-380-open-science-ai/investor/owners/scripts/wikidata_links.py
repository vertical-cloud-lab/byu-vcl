#!/usr/bin/env python3
"""Link GitHub owners and repositories to Wikidata entities, and pull what Wikidata records about them.

Two bridges: entities whose GitHub username (P2037) matches an owner login, and software entities whose source
code repository (P1324) is a repository in either frame, with their developer (P178). For every entity reached,
the script records its types (P31), country, inception, dissolution, stock exchange and ticker, owner, parent
organization, website, employees and latest total revenue.

Writes data/wikidata_github_usernames.csv, data/wikidata_repo_links.csv and data/wikidata_entities.csv.
Run from owners/ after harvest_github.py.
"""
import time
import pandas as pd, requests

UA = {"User-Agent": "open-source-owner-study/0.1 (research script)", "Accept": "text/csv"}


def sparql(q):
    for attempt in range(5):
        r = requests.get("https://query.wikidata.org/sparql", params={"query": q}, headers=UA, timeout=120)
        if r.status_code == 200:
            from io import StringIO
            return pd.read_csv(StringIO(r.text), dtype=str)
        time.sleep(10 * (attempt + 1))
    r.raise_for_status()


def qid(s):
    return s.str.replace("http://www.wikidata.org/entity/", "", regex=False)


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
ents = sorted(set(u.item) | set(r.item) | set(x for x in r.dev if x))
print("matched usernames", len(u), "repo links", len(r), "entities", len(ents))

rows = []
for i in range(0, len(ents), 150):
    vals = " ".join(f"wd:{e}" for e in ents[i:i + 150])
    q = f"""SELECT ?e ?eLabel
      (GROUP_CONCAT(DISTINCT ?typeLabel; separator="|") AS ?types)
      (SAMPLE(?countryLabel) AS ?country) (MIN(?inception) AS ?inception) (MIN(?dissolved) AS ?dissolved)
      (GROUP_CONCAT(DISTINCT ?exLabel; separator="|") AS ?exchanges) (GROUP_CONCAT(DISTINCT ?ticker; separator="|") AS ?tickers)
      (GROUP_CONCAT(DISTINCT ?ownerLabel; separator="|") AS ?owned_by) (GROUP_CONCAT(DISTINCT ?parentLabel; separator="|") AS ?parent)
      (GROUP_CONCAT(DISTINCT ?devLabel; separator="|") AS ?developer)
      (SAMPLE(?site) AS ?website) (MAX(?emp) AS ?employees)
    WHERE {{ VALUES ?e {{ {vals} }}
      OPTIONAL {{ ?e wdt:P31 ?type . }} OPTIONAL {{ ?e wdt:P17 ?country . }}
      OPTIONAL {{ ?e wdt:P571 ?inception . }} OPTIONAL {{ ?e wdt:P576 ?dissolved . }}
      OPTIONAL {{ ?e p:P414 ?st . ?st ps:P414 ?ex . OPTIONAL {{ ?st pq:P249 ?ticker . }} }}
      OPTIONAL {{ ?e wdt:P127 ?owner . }} OPTIONAL {{ ?e wdt:P749 ?parent . }} OPTIONAL {{ ?e wdt:P178 ?dev . }}
      OPTIONAL {{ ?e wdt:P856 ?site . }} OPTIONAL {{ ?e wdt:P1128 ?emp . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en".
        ?e rdfs:label ?eLabel . ?type rdfs:label ?typeLabel . ?country rdfs:label ?countryLabel .
        ?ex rdfs:label ?exLabel . ?owner rdfs:label ?ownerLabel . ?parent rdfs:label ?parentLabel .
        ?dev rdfs:label ?devLabel . }} }}
    GROUP BY ?e ?eLabel"""
    d = sparql(q)
    rows.append(d)
    time.sleep(1)
    print("entities", i + len(d), flush=True)
ent = pd.concat(rows)
ent["e"] = qid(ent["e"])

# latest total revenue (P2139) with its point in time and unit
rev = []
for i in range(0, len(ents), 150):
    vals = " ".join(f"wd:{e}" for e in ents[i:i + 150])
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
    ent = ent.merge(rev, on="e", how="left")
ent.rename(columns={"e": "item", "eLabel": "label"}).to_csv("data/wikidata_entities.csv", index=False)
print("done", len(ent))
