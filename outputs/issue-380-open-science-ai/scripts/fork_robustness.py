#!/usr/bin/env python3
"""Forks vs originals after closing moves: GitHub stars, forks, and commits in the last 12 months (gh api).
Writes data/fork_vs_original.csv."""
import json, subprocess, csv, datetime
pairs = [("Elasticsearch → OpenSearch (2021)", "elastic/elasticsearch", "opensearch-project/OpenSearch"),
         ("Redis → Valkey (2024)", "redis/redis", "valkey-io/valkey"),
         ("Terraform → OpenTofu (2023)", "hashicorp/terraform", "opentofu/opentofu"),
         ("Akka → Apache Pekko (2022)", "akka/akka", "apache/pekko"),
         ("Puppet → OpenVox (2025)", "puppetlabs/puppet", "OpenVoxProject/openvox"),
         ("MySQL → MariaDB (2009)", "mysql/mysql-server", "MariaDB/server"),
         ("OpenOffice → LibreOffice (2010)", "apache/openoffice", "LibreOffice/core"),
         ("Kibana → OpenSearch Dashboards (2021)", "elastic/kibana", "opensearch-project/OpenSearch-Dashboards")]
since = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
def gh(path, extra=()):
    p = subprocess.run(["gh", "api", path, *extra], capture_output=True, text=True)
    return json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else None
def stats(repo):
    r = gh(f"repos/{repo}") or {}
    # commits in last 12 months on default branch: use search-free approach via pagination header count
    p = subprocess.run(["gh", "api", "-i", f"repos/{repo}/commits?since={since}&per_page=1"], capture_output=True, text=True)
    n = None
    for line in p.stdout.splitlines():
        if line.lower().startswith("link:") and 'rel="last"' in line:
            import re
            m = re.search(r'[&?]page=(\d+)>; rel="last"', line); n = int(m.group(1)) if m else None
    if n is None and p.returncode == 0:
        body = p.stdout.split("\r\n\r\n", 1)[-1] if "\r\n\r\n" in p.stdout else p.stdout.split("\n\n", 1)[-1]
        try: n = len(json.loads(body))
        except Exception: n = None
    return dict(stars=r.get("stargazers_count"), forks=r.get("forks_count"), archived=r.get("archived"), pushed=r.get("pushed_at", "")[:10], license=(r.get("license") or {}).get("spdx_id"), commits_12m=n)
rows = []
for lab, a, b in pairs:
    sa, sb = stats(a), stats(b)
    rows.append(dict(case=lab, original=a, fork=b, **{f"orig_{k}": v for k, v in sa.items()}, **{f"fork_{k}": v for k, v in sb.items()}))
    print(lab, "| orig", sa, "| fork", sb)
with open("data/fork_vs_original.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
