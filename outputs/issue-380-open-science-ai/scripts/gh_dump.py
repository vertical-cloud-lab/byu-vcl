#!/usr/bin/env python3
"""Dump every issue, PR, discussion and comment of a GitHub repo with gh api.

REST (paginated, 100/page) for issues+PRs, issue comments and PR review comments;
GraphQL for PR review bodies and for discussions (comments + nested replies),
because the web UI hides both behind "load more".
Usage: python gh_dump.py OWNER/REPO OUTDIR
"""
import json, subprocess, sys, os, time

def gh(args, paginate=False):
    cmd = ["gh", "api"] + (["--paginate"] if paginate else []) + args
    for attempt in range(4):
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0:
            return p.stdout
        sys.stderr.write(f"retry {attempt}: {' '.join(args)[:80]} -> {p.stderr[:200]}\n")
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(p.stderr)

def rest_all(path):
    out = gh([path, "-H", "Accept: application/vnd.github+json"], paginate=True)
    # --paginate concatenates JSON arrays: "[...][...]" -> parse each
    items, dec, i = [], json.JSONDecoder(), 0
    out = out.strip()
    while i < len(out):
        obj, j = dec.raw_decode(out, i)
        items.extend(obj if isinstance(obj, list) else [obj])
        i = j
        while i < len(out) and out[i] in " \n\r\t":
            i += 1
    return items

def graphql(query, **vars):
    args = ["graphql", "-f", f"query={query}"]
    for k, v in vars.items():
        if v is None:
            continue
        args += (["-F", f"{k}={v}"] if isinstance(v, int) else ["-f", f"{k}={v}"])
    return json.loads(gh(args))

DISC_Q = """
query($owner:String!,$name:String!,$cursor:String){
 repository(owner:$owner,name:$name){
  discussions(first:25, after:$cursor){
   pageInfo{hasNextPage endCursor}
   nodes{ number title url createdAt author{login} body category{name}
     comments(first:50){ totalCount pageInfo{hasNextPage endCursor}
       nodes{ id url createdAt author{login} body
         replies(first:50){ totalCount nodes{ url createdAt author{login} body } } } } } } } }"""

DISC_MORE = """
query($id:ID!,$cursor:String){ node(id:$id){ ... on Discussion { comments(first:50, after:$cursor){
 pageInfo{hasNextPage endCursor} nodes{ id url createdAt author{login} body
 replies(first:50){ totalCount nodes{ url createdAt author{login} body } } } } } } }"""

REV_Q = """
query($owner:String!,$name:String!,$cursor:String){
 repository(owner:$owner,name:$name){
  pullRequests(first:50, after:$cursor){
   pageInfo{hasNextPage endCursor}
   nodes{ number reviews(first:50){ totalCount nodes{ url createdAt author{login} body state } } } } } }"""

def main(full, outdir):
    owner, name = full.split("/")
    os.makedirs(outdir, exist_ok=True)
    issues = rest_all(f"repos/{full}/issues?state=all&per_page=100")
    print("issues+PRs:", len(issues))
    icom = rest_all(f"repos/{full}/issues/comments?per_page=100")
    print("issue/PR conversation comments:", len(icom))
    rcom = rest_all(f"repos/{full}/pulls/comments?per_page=100")
    print("PR review (inline) comments:", len(rcom))
    # PR review bodies
    reviews, cursor = [], None
    while True:
        d = graphql(REV_Q, owner=owner, name=name, cursor=cursor)["data"]["repository"]["pullRequests"]
        for pr in d["nodes"]:
            for r in pr["reviews"]["nodes"]:
                if r["body"]:
                    r["pr"] = pr["number"]; reviews.append(r)
        if not d["pageInfo"]["hasNextPage"]:
            break
        cursor = d["pageInfo"]["endCursor"]
    print("PR review bodies (non-empty):", len(reviews))
    # discussions
    discs, cursor = [], None
    try:
        while True:
            d = graphql(DISC_Q, owner=owner, name=name, cursor=cursor)["data"]["repository"]["discussions"]
            for disc in d["nodes"]:
                c = disc["comments"]
                nodes = c["nodes"]
                pc = c["pageInfo"]
                while pc["hasNextPage"]:
                    more = graphql(DISC_MORE, id=disc_id(disc, owner, name), cursor=pc["endCursor"])["data"]["node"]["comments"]
                    nodes += more["nodes"]; pc = more["pageInfo"]
                disc["comments"] = {"totalCount": c["totalCount"], "nodes": nodes}
                discs.append(disc)
            if not d["pageInfo"]["hasNextPage"]:
                break
            cursor = d["pageInfo"]["endCursor"]
    except Exception as e:
        print("discussions error:", str(e)[:200])
    print("discussions:", len(discs), "discussion comments:", sum(len(x["comments"]["nodes"]) for x in discs),
          "replies:", sum(len(c["replies"]["nodes"]) for x in discs for c in x["comments"]["nodes"]))
    for fn, obj in [("issues.json", issues), ("issue_comments.json", icom), ("review_comments.json", rcom),
                    ("review_bodies.json", reviews), ("discussions.json", discs)]:
        json.dump(obj, open(os.path.join(outdir, fn), "w"))

_disc_ids = {}
def disc_id(disc, owner, name):
    q = "query($owner:String!,$name:String!,$n:Int!){repository(owner:$owner,name:$name){discussion(number:$n){id}}}"
    return graphql(q, owner=owner, name=name, n=disc["number"])["data"]["repository"]["discussion"]["id"]

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
