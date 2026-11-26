#!/usr/bin/env python3
"""Which repositories in the frames ask for money, and through what: FUNDING.yml links and GitHub Sponsors.

GitHub GraphQL, 40 repositories per query. For each repository: the platforms in its FUNDING.yml (github,
open_collective, patreon, ko_fi, custom, ...). For each owner: whether it has a GitHub Sponsors listing, and its
count of public, active sponsorships. Writes data/repo_funding_links.csv and data/owner_sponsors.csv.
Run from owners/. Reads the token from /tmp/.ghtok if a re-minted one exists, else GH_TOKEN.
"""
import json, os, time
import pandas as pd, requests


def token():
    p = "/tmp/.ghtok"
    return open(p).read().strip() if os.path.exists(p) else os.environ["GH_TOKEN"]


def gql(q):
    for attempt in range(5):
        r = requests.post("https://api.github.com/graphql", json={"query": q}, timeout=90,
                          headers={"Authorization": f"Bearer {token()}"})
        if r.status_code == 200:
            return r.json()
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()


def main():
    a = pd.read_csv("data/repos_frame_a.csv"); b = pd.read_csv("data/repos_frame_b.csv")
    names = list(dict.fromkeys(pd.concat([a.full_name, b.full_name])))
    rows = []
    for i in range(0, len(names), 40):
        chunk = names[i:i + 40]
        body = "\n".join(
            f'r{k}: repository(owner: {json.dumps(n.split("/")[0])}, name: {json.dumps(n.split("/")[1])}) '
            '{ nameWithOwner fundingLinks { platform url } }' for k, n in enumerate(chunk))
        j = gql("query {\n" + body + "\n}")
        for k, n in enumerate(chunk):
            d = (j.get("data") or {}).get(f"r{k}")
            links = (d or {}).get("fundingLinks") or []
            rows.append({"full_name": n, "found": d is not None,
                         "funding_platforms": ";".join(sorted({x["platform"] for x in links})),
                         "funding_urls": " ".join(x["url"] for x in links)})
        print("repos", i + len(chunk), flush=True)
    pd.DataFrame(rows).to_csv("data/repo_funding_links.csv", index=False)

    o = pd.read_csv("data/owners_github.csv")
    orows = []
    pairs = list(zip(o.owner, o.owner_type))
    for i in range(0, len(pairs), 40):
        chunk = pairs[i:i + 40]
        body = "\n".join(
            f'o{k}: {"organization" if t == "Organization" else "user"}(login: {json.dumps(n)}) '
            '{ login hasSponsorsListing sponsorshipsAsMaintainer(activeOnly: true, includePrivate: false) '
            '{ totalCount } }' for k, (n, t) in enumerate(chunk))
        j = gql("query {\n" + body + "\n}")
        for k, (n, t) in enumerate(chunk):
            d = (j.get("data") or {}).get(f"o{k}") or {}
            orows.append({"owner": n, "has_sponsors_listing": d.get("hasSponsorsListing"),
                          "public_active_sponsors": (d.get("sponsorshipsAsMaintainer") or {}).get("totalCount")})
        print("owners", i + len(chunk), flush=True)
    pd.DataFrame(orows).to_csv("data/owner_sponsors.csv", index=False)


if __name__ == "__main__":
    main()
