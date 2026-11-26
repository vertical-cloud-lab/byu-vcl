#!/usr/bin/env python3
"""Form 990 figures that ProPublica's API lacks, read from its organization pages instead.

nonprofit_finances.py uses ProPublica's Nonprofit Explorer API, whose `filings_with_data` stops at 2017 for the
OpenJS Foundation and is empty for the Rust Foundation, Ladybird and DigitalPlat. ProPublica's web page for each
organization lists the IRS's extracted figures for later years too. For every target with no API data, or whose
latest API year is before 2021, this reads that page (through scripts/via_pi.py) and parses each "Fiscal Year
Ending" block: revenue, expenses, total assets and total liabilities.

Writes data/form990_html_filings.csv and updates data/form990_summary.csv for those organizations with the same rules
as nonprofit_finances.py (latest year; FY2019 base, or the nearest year before FY2020; real growth on CPI-U), with
`source` = propublica-html. Run from owners/ after nonprofit_finances.py.
"""
import re, sys
import pandas as pd

sys.path.insert(0, "scripts")
import via_pi  # noqa: E402
from nonprofit_finances import CPI_U  # noqa: E402

MONTHS = "Jan|Feb|March|April|May|June|July|Aug|Sept|Oct|Nov|Dec"


def money(label, block):
    m = re.search(label + r" \$(-?[\d,]+)", block)
    return float(m.group(1).replace(",", "")) if m else None


def parse(text):
    out = []
    parts = re.split(r"Fiscal Year Ending ", text)[1:]
    for p in parts:
        m = re.match(rf"({MONTHS})\.? (\d{{4}})", p)
        if not m or "Extracted Financial Data" not in p[:200]:
            continue
        block = p[:4000]
        out.append({"tax_year": int(m.group(2)), "fy_end_month": m.group(1),
                    "revenue": money("Revenue", block), "expenses": money("Expenses", block),
                    "assets": money("Total Assets", block), "liabilities": money("Total Liabilities", block)})
    return out


def main():
    tg = pd.read_csv("data/nonprofit_targets.csv", dtype={"ein": str})
    tg["ein9"] = tg.ein.str.replace("-", "")
    S = pd.read_csv("data/form990_summary.csv", dtype={"ein": str})
    S["ein9"] = S.ein.str.zfill(9)
    have = S.groupby("ein9").latest_year.max()
    todo = tg[~tg.ein9.isin(have.index) | tg.ein9.map(have).lt(2021)]
    rows = []
    for ein, g in todo.groupby("ein9"):
        url = f"https://projects.propublica.org/nonprofits/organizations/{ein}"
        res = via_pi.get(url)
        text = via_pi.text_of_html(res["body"]) if res["ok"] else ""
        name = g.org_name.iloc[0]
        yrs = parse(text)
        print(name, ein, "route", res["route"], "years", [y["tax_year"] for y in yrs])
        for owner in g.owner:
            for y in yrs:
                rows.append({"owner": owner, "ein": ein, "name": name, **y, "url": url, "route": res["route"]})
    H = pd.DataFrame(rows)
    H.to_csv("data/form990_html_filings.csv", index=False)
    if not len(H):
        return
    new = []
    for (owner, ein), g in H.dropna(subset=["revenue"]).groupby(["owner", "ein"]):
        g = g.sort_values("tax_year").drop_duplicates("tax_year", keep="first")
        last = g.iloc[-1]
        base = g[g.tax_year <= 2019]
        base = base.iloc[-1] if len(base) else None
        rec = {"owner": owner, "ein": ein, "name": last["name"], "latest_year": int(last.tax_year),
               "latest_revenue": last.revenue, "latest_expenses": last.expenses,
               "latest_net_assets": (last.assets or 0) - (last.liabilities or 0), "url": last.url,
               "source": "propublica-html"}
        if base is not None:
            ly, by = int(last.tax_year), int(base.tax_year)
            rec.update({"base_year": by, "base_revenue": base.revenue,
                        "real_growth": (last.revenue / CPI_U[ly]) / (base.revenue / CPI_U[by]) - 1
                        if base.revenue else None})
        new.append(rec)
    N = pd.DataFrame(new)
    S = S[~S.ein9.isin(set(N.ein))].drop(columns="ein9")
    if "source" not in S.columns:
        S["source"] = "propublica-api"
    out = pd.concat([S, N], ignore_index=True)
    out.to_csv("data/form990_summary.csv", index=False)
    print(N[["owner", "name", "latest_year", "latest_revenue", "base_year", "real_growth"]].to_string())


if __name__ == "__main__":
    main()
