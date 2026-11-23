#!/usr/bin/env python3
"""What the AI labs actually open-source: public repos per GitHub org (count, stars, licences, created per year)."""
import json, subprocess, collections, csv
ORGS = {"Anthropic": ["anthropics"], "OpenAI": ["openai"], "Google DeepMind": ["google-deepmind"], "Meta FAIR": ["facebookresearch"],
        "DeepSeek": ["deepseek-ai"], "Ai2": ["allenai"], "Mistral AI": ["mistralai"]}
rows, summ = [], []
for lab, orgs in ORGS.items():
    repos = []
    for o in orgs:
        for kind in ("orgs", "users"):
            p = subprocess.run(["gh", "api", "--paginate", f"{kind}/{o}/repos?per_page=100"], capture_output=True, text=True)
            txt = p.stdout.strip(); dec = json.JSONDecoder(); i = 0; got = []
            while i < len(txt):
                obj, j = dec.raw_decode(txt, i); i = j
                if isinstance(obj, list): got += obj
                while i < len(txt) and txt[i] in " \n\r\t": i += 1
            if got:
                repos += got; break
    src = [r for r in repos if not r.get("fork")]
    lic = collections.Counter(((r.get("license") or {}).get("spdx_id") or "none") for r in src)
    years = collections.Counter(r["created_at"][:4] for r in src)
    stars = sum(r["stargazers_count"] for r in src)
    top = sorted(src, key=lambda r: -r["stargazers_count"])[:3]
    summ.append(dict(lab=lab, public_source_repos=len(src), stars=stars, permissive=sum(v for k, v in lic.items() if k in ("MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause")),
                     no_license=lic.get("none", 0) + lic.get("NOASSERTION", 0), created_2024=years.get("2024", 0), created_2025=years.get("2025", 0), created_2026=years.get("2026", 0),
                     top_repos="; ".join(f"{r['name']} ({r['stargazers_count']:,})" for r in top)))
    for y, n in sorted(years.items()): rows.append(dict(lab=lab, year=y, repos_created=n))
with open("data/ai_lab_github_orgs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(summ[0].keys())); w.writeheader(); w.writerows(summ)
with open("data/ai_lab_github_repos_by_year.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["lab", "year", "repos_created"]); w.writeheader(); w.writerows(rows)
for s in summ: print(s)
