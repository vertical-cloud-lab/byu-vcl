#!/usr/bin/env python3
"""Frames A and B from the pre-registration: the most-starred repositories and their owners' profiles.

Frame A: the 2,000 most-starred public non-fork repositories, paged through star ranges (the search API returns at
most 1,000 rows per query). Frame B: for each of 22 science topics, the 100 most-starred repositories with >= 10
stars. Then every owner's profile (/orgs/<login> or /users/<login>).

Writes data/repos_frame_a.csv, data/repos_frame_b.csv, data/owners_github.csv and data/harvest_log.json.
Run from owners/. Reads the token from /tmp/.ghtok if a re-minted one exists, else GH_TOKEN.
"""
import datetime as dt, json, os, re, sys, time
import pandas as pd, requests

TOPICS = ["chemistry", "computational-chemistry", "cheminformatics", "materials-science", "materials-informatics",
          "bioinformatics", "genomics", "drug-discovery", "molecular-dynamics", "quantum-chemistry",
          "protein-structure", "lab-automation", "laboratory-automation", "self-driving-lab",
          "autonomous-experimentation", "open-hardware", "open-source-hardware", "scientific-computing", "physics",
          "astronomy", "neuroscience", "microscopy"]
CONTENT_TOPICS = {"awesome", "awesome-list", "list", "lists", "resources", "tutorial", "tutorials", "book", "books",
                  "interview", "interview-questions", "roadmap", "cheatsheet", "learning", "education", "course",
                  "courses"}
CONTENT_NAME = re.compile(r"awesome|interview|roadmap|cheatsheet|tutorial|book|course", re.I)


def token():
    p = "/tmp/.ghtok"
    return open(p).read().strip() if os.path.exists(p) else os.environ["GH_TOKEN"]


S = requests.Session()


def get(url, params=None, search=False):
    for attempt in range(6):
        r = S.get(url, params=params, timeout=60, headers={
            "Authorization": f"Bearer {token()}", "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"})
        if r.status_code in (403, 429) and ("rate limit" in r.text.lower() or "secondary" in r.text.lower()):
            reset = int(r.headers.get("x-ratelimit-reset", time.time() + 60))
            wait = max(5, min(120, reset - time.time() + 2))
            print(f"rate limited, sleeping {wait:.0f}s", flush=True)
            time.sleep(wait)
            continue
        if r.status_code >= 500:
            time.sleep(5 * (attempt + 1))
            continue
        if search:
            time.sleep(2.2)  # 30 search requests a minute
        return r
    r.raise_for_status()


def row(it, frame, topic=None):
    lang = it.get("language")
    topics = it.get("topics") or []
    content = (lang is None) or bool(CONTENT_TOPICS & set(topics)) or bool(CONTENT_NAME.search(it["name"]))
    return {"frame": frame, "topic_query": topic, "full_name": it["full_name"], "owner": it["owner"]["login"],
            "owner_type": it["owner"]["type"], "stars": it["stargazers_count"], "forks": it["forks_count"],
            "open_issues": it["open_issues_count"], "language": lang,
            "license": (it.get("license") or {}).get("spdx_id"), "topics": ";".join(topics),
            "created_at": it["created_at"], "pushed_at": it["pushed_at"], "archived": it["archived"],
            "is_content": content, "homepage": it.get("homepage"), "description": (it.get("description") or "")[:300]}


def search(q, pages, frame, topic=None):
    out, log = [], []
    for page in range(1, pages + 1):
        r = get("https://api.github.com/search/repositories",
                {"q": q, "sort": "stars", "order": "desc", "per_page": 100, "page": page}, search=True)
        if r.status_code != 200:
            log.append({"q": q, "page": page, "status": r.status_code, "msg": r.text[:200]})
            break
        j = r.json()
        log.append({"q": q, "page": page, "status": 200, "total_count": j["total_count"],
                    "incomplete_results": j["incomplete_results"], "n": len(j["items"])})
        out += [row(it, frame, topic) for it in j["items"]]
        if len(j["items"]) < 100:
            break
    return out, log


def frame_a(n=2000):
    rows, log, upper = {}, [], None
    while len(rows) < n:
        q = f"stars:1000..{upper}" if upper else "stars:>=1000"  # two stars: qualifiers are OR-ed, so use a range
        got, lg = search(q, 10, "A")
        log += lg
        before = len(rows)
        for g in got:
            rows.setdefault(g["full_name"], g)
        print(f"frame A: {q!r} -> {len(got)} rows, {len(rows)} unique", flush=True)
        if not got or len(rows) == before:
            break
        upper = min(g["stars"] for g in got)
    df = pd.DataFrame(rows.values()).sort_values("stars", ascending=False).head(n).reset_index(drop=True)
    df.insert(1, "rank", range(1, len(df) + 1))
    return df, log


def frame_b():
    rows, log = [], []
    for t in TOPICS:
        got, lg = search(f"topic:{t} stars:>=10", 1, "B", t)
        log += lg
        rows += got
        print(f"frame B: {t} -> {len(got)}", flush=True)
    df = pd.DataFrame(rows)
    topics = df.groupby("full_name")["topic_query"].apply(lambda s: ";".join(sorted(set(s))))
    df = df.drop_duplicates("full_name").drop(columns="topic_query").merge(
        topics.rename("topic_queries"), left_on="full_name", right_index=True)
    return df.sort_values("stars", ascending=False).reset_index(drop=True), log


def owner(lt):
    login, typ = lt
    url = f"https://api.github.com/{'orgs' if typ == 'Organization' else 'users'}/{login}"
    r = get(url)
    j = r.json() if r.status_code == 200 else {}
    return {"owner": login, "owner_type": typ, "status": r.status_code, "name": j.get("name"),
                "blog": j.get("blog"), "email": j.get("email"), "location": j.get("location"),
                "description": (j.get("description") or j.get("bio") or "")[:300],
                "company": j.get("company"), "twitter": j.get("twitter_username"),
                "is_verified": j.get("is_verified"), "created_at": j.get("created_at"),
                "public_repos": j.get("public_repos"), "followers": j.get("followers")}


def owners(logins_types):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as ex:
        out = list(ex.map(owner, sorted(logins_types)))
    return pd.DataFrame(out)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    a, la = frame_a()
    a.to_csv("data/repos_frame_a.csv", index=False)
    b, lb = frame_b()
    b.to_csv("data/repos_frame_b.csv", index=False)
    lt = set(zip(a.owner, a.owner_type)) | set(zip(b.owner, b.owner_type))
    o = owners(lt)
    o.to_csv("data/owners_github.csv", index=False)
    json.dump({"started_utc": started, "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "frame_a_rows": len(a), "frame_b_rows": len(b), "owners": len(o), "search_log": la + lb},
              open("data/harvest_log.json", "w"), indent=1)
    print("done", len(a), len(b), len(o))
