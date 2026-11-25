#!/usr/bin/env python3
"""Finances of the nonprofits and community projects that own or steward repositories in the frames.

US nonprofits: IRS Form 990 figures from ProPublica's Nonprofit Explorer API, by EIN, given in
data/nonprofit_targets.csv (columns owner, org_name, ein). Every filing year with data is kept; the summary takes
the latest year and FY2019 (or the nearest year before FY2020 if 2019 is missing).

Community projects: Open Collective's public stats, looked up by GitHub handle for every owner in either frame.

Writes data/form990_filings.csv, data/form990_summary.csv and data/opencollective.csv. Run from owners/.
"""
import time
import pandas as pd, requests

import json, collections
_m = collections.defaultdict(list)  # BLS series CUUR0000SA0, saved by hand from the public API to data/cpi_u_bls.json
for _x in [x for f in ("data/cpi_u_bls.json", "data/cpi_u_bls_2009_2017.json")
           for x in json.load(open(f))["Results"]["series"][0]["data"]]:
    if _x["period"].startswith("M") and _x["period"] != "M13" and _x["value"] != "-":
        _m[int(_x["year"])].append(float(_x["value"]))
CPI_U = {y: sum(v) / len(v) for y, v in _m.items()}  # annual averages; 2025 lacks October (shutdown), 2026 is partial


def form990():
    tg = pd.read_csv("data/nonprofit_targets.csv", dtype={"ein": str})
    rows = []
    for _, t in tg.iterrows():
        ein = str(t.ein).replace("-", "")
        r = requests.get(f"https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json", timeout=60)
        time.sleep(0.5)
        if r.status_code != 200:
            rows.append({"owner": t.owner, "ein": ein, "error": r.status_code}); continue
        j = r.json()
        org = j.get("organization", {})
        for f in j.get("filings_with_data", []):
            rows.append({"owner": t.owner, "ein": ein, "name": org.get("name"), "state": org.get("state"),
                         "subsection": org.get("subsection_code"), "tax_year": f.get("tax_prd_yr"),
                         "tax_period": f.get("tax_prd"), "form": f.get("formtype"),
                         "revenue": f.get("totrevenue"), "expenses": f.get("totfuncexpns"),
                         "assets": f.get("totassetsend"), "liabilities": f.get("totliabend"),
                         "contributions": f.get("totcntrbgfts"), "program_revenue": f.get("totprgmrevnue"),
                         "url": f"https://projects.propublica.org/nonprofits/organizations/{ein}"})
        print(t.owner, org.get("name"), len(j.get("filings_with_data", [])), flush=True)
    d = pd.DataFrame(rows)
    d.to_csv("data/form990_filings.csv", index=False)
    out = []
    for (owner, ein), g in d.dropna(subset=["tax_year"]).groupby(["owner", "ein"]):
        g = g.sort_values("tax_year")
        last = g.iloc[-1]
        base = g[g.tax_year <= 2019]
        base = base.iloc[-1] if len(base) else None
        rec = {"owner": owner, "ein": ein, "name": last["name"], "latest_year": int(last.tax_year),
               "latest_revenue": last.revenue, "latest_expenses": last.expenses,
               "latest_net_assets": (last.assets or 0) - (last.liabilities or 0), "url": last.url}
        if base is not None:
            ly, by = int(last.tax_year), int(base.tax_year)
            rec.update({"base_year": by, "base_revenue": base.revenue,
                        "real_growth": (last.revenue / CPI_U[ly]) / (base.revenue / CPI_U[by]) - 1
                        if base.revenue else None})
        out.append(rec)
    pd.DataFrame(out).to_csv("data/form990_summary.csv", index=False)


def opencollective():
    owners = pd.read_csv("data/owners_github.csv")
    q = """query($h: String) { account(githubHandle: $h) { slug name type isHost
      stats { totalAmountReceived { valueInCents currency } yearlyBudget { valueInCents currency }
              balance { valueInCents currency } } } }"""
    rows = []
    for login in owners.owner:
        r = requests.post("https://api.opencollective.com/graphql/v2", json={"query": q, "variables": {"h": login}},
                          timeout=60)
        time.sleep(0.4)
        a = (r.json().get("data") or {}).get("account") if r.status_code == 200 else None
        if a:
            st = a.get("stats") or {}
            c = lambda k: ((st.get(k) or {}).get("valueInCents") or 0) / 100
            rows.append({"owner": login, "oc_slug": a["slug"], "oc_name": a["name"], "oc_type": a["type"],
                         "oc_total_received": c("totalAmountReceived"), "oc_yearly_budget": c("yearlyBudget"),
                         "oc_balance": c("balance"),
                         "oc_currency": (st.get("totalAmountReceived") or {}).get("currency"),
                         "url": f"https://opencollective.com/{a['slug']}"})
    pd.DataFrame(rows).to_csv("data/opencollective.csv", index=False)
    print("open collective matches", len(rows))


if __name__ == "__main__":
    import sys
    if "990" in sys.argv[1:]:
        form990()
    if "oc" in sys.argv[1:]:
        opencollective()
