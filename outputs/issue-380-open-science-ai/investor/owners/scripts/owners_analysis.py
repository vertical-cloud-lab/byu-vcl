#!/usr/bin/env python3
"""H7-H11 from owners/PREREGISTRATION.md. Run from owners/ after the data steps (see README).

Writes data/h7_stars_by_class.csv, data/h7_sensitivity.csv, data/h10_stars_by_class.csv, data/h8_correlations.csv,
data/h9_outcomes.csv, data/h11_nonprofits.csv and data/results_summary.json.
"""
import json
import numpy as np, pandas as pd
from scipy import stats

RNG = np.random.default_rng(380)
A = pd.read_csv("data/repos_frame_a.csv")
B = pd.read_csv("data/repos_frame_b.csv")
C = pd.read_csv("data/owner_classes.csv", dtype=str)
C["judgment"] = C["judgment"].fillna("0").astype(str).str.strip().isin(["1", "1.0", "True", "true"])
C["crypto"] = C["crypto"].fillna("0").astype(str).str.strip().isin(["1", "1.0", "True", "true"])
CLASSES = ["core", "complement", "nonprofit", "academic", "government", "community", "individual", "unknown"]

# Software repositories that the pre-registered content rule flags only through a substring ("book" in storybook,
# "course" in discourse) or a generic topic. Used in a sensitivity run only; the main results apply the rule as
# written.
CONTENT_FALSE_POSITIVES = {
    "storybookjs/storybook", "discourse/discourse", "HKUDS/DeepTutor", "gammapy/gammapy", "pypose/pypose",
    "materialyzeai/matgl", "SAOImageDS9/SAOImageDS9", "sy2002/QNICE-FPGA", "NMRduino/NMRduino",
    "AFRL-ARES/Educational-ARES"}


def frame(d, content="prereg"):
    d = d.merge(C[["owner", "cls", "judgment", "crypto", "entity", "parent"]], on="owner", how="left")
    d["cls"] = d["cls"].fillna("unknown")
    if content == "prereg":
        d = d[~d.is_content]
    elif content == "corrected":
        d = d[~d.is_content | d.full_name.isin(CONTENT_FALSE_POSITIVES)]
    return d


def by_class(d):
    t = d.groupby("cls").agg(owners=("owner", "nunique"), repos=("stars", "size"), stars=("stars", "sum"))
    t = t.reindex(CLASSES).fillna(0).astype(int)
    t["share_of_stars"] = (t.stars / t.stars.sum()).round(4)
    t["share_of_repos"] = (t.repos / t.repos.sum()).round(4)
    return t


AUDIT = "../edison/inv_owner_class_audit_files/owner_class_audit.csv"


def audit_agreement():
    """Edison's blind re-classification of 120 sampled organizations against mine: agreement, kappa, differences."""
    E = pd.read_csv(AUDIT, dtype=str)
    m = E[["owner", "cls", "judgment", "basis"]].merge(C[["owner", "cls", "judgment", "basis"]], on="owner",
                                                        suffixes=("_edison", "_mine"))
    m["agree"] = m.cls_edison == m.cls_mine
    po = m.agree.mean()
    cl = sorted(set(m.cls_edison) | set(m.cls_mine))
    pe = sum((m.cls_mine == c).mean() * (m.cls_edison == c).mean() for c in cl)
    m.to_csv("data/class_audit_comparison.csv", index=False)
    pd.crosstab(m.cls_mine, m.cls_edison).to_csv("data/class_audit_crosstab.csv")
    dis = m[~m.agree]
    return {"n": int(len(m)), "agree": int(m.agree.sum()), "agreement": round(po, 3),
            "cohen_kappa": round((po - pe) / (1 - pe), 3),
            "disagreements_i_flagged_as_judgment": int(dis.judgment_mine.fillna("0").astype(str).str.strip()
                                                       .isin(["1", "1.0", "True", "true"]).sum()),
            "disagreements": dis[["owner", "cls_mine", "cls_edison"]].to_dict("records")}


def with_audit_classes(d):
    """Replace my class with Edison's for the audited organizations."""
    E = pd.read_csv(AUDIT, dtype=str).set_index("owner").cls
    d = d.copy()
    hit = d.owner.isin(E.index)
    d.loc[hit, "cls"] = d.loc[hit, "owner"].map(E)
    return d


def company_share(d):
    s = d.groupby("cls").stars.sum()
    return (s.get("core", 0) + s.get("complement", 0)) / s.sum() if s.sum() else np.nan


def core_share(d):
    s = d.groupby("cls").stars.sum()
    core, comp = s.get("core", 0), s.get("complement", 0)
    return core / (core + comp) if core + comp else np.nan


def org_bootstrap(d, n=5000):
    """Resample company-owned organizations with replacement; core share of company stars."""
    co = d[d.cls.isin(["core", "complement"])].groupby(["owner", "cls"]).stars.sum().reset_index()
    vals = co.stars.values; is_core = (co.cls == "core").values
    out = []
    for _ in range(n):
        i = RNG.integers(0, len(co), len(co))
        out.append(vals[i][is_core[i]].sum() / vals[i].sum())
    return np.percentile(out, [2.5, 97.5])


def h7_h10():
    res = {}
    for name, raw in (("A", A), ("B", B)):
        d = frame(raw)
        t = by_class(d)
        t.to_csv(f"data/{'h7' if name == 'A' else 'h10'}_stars_by_class.csv")
        lo, hi = org_bootstrap(d)
        res[name] = {"core_share_of_company_stars": round(core_share(d), 4), "org_bootstrap_95ci": [round(lo, 4),
                     round(hi, 4)], "software_repos": int(len(d)), "software_stars": int(d.stars.sum()),
                     "company_share_of_stars": round(t.loc[["core", "complement"], "stars"].sum() / t.stars.sum(), 4),
                     "by_class": t.share_of_stars.to_dict()}
        sens = []
        for label, dd in [("pre-registered (software repos by rule)", d),
                          ("content rule corrected", frame(raw, "corrected")),
                          ("all repos including content", frame(raw, "all")),
                          ("crypto owners excluded", d[~d.crypto]),
                          ("Edison's audit classes for the 120 audited organizations", with_audit_classes(d))]:
            sens.append({"frame": name, "variant": label, "core_share": core_share(dd),
                         "company_share": company_share(dd)})
        lower = d.copy(); lower.loc[(lower.cls == "core") & lower.judgment, "cls"] = "complement"
        upper = d.copy(); upper.loc[(upper.cls == "complement") & upper.judgment, "cls"] = "core"
        sens.append({"frame": name, "variant": "judgment calls against core", "core_share": core_share(lower),
                     "company_share": company_share(lower)})
        sens.append({"frame": name, "variant": "judgment calls toward core", "core_share": core_share(upper),
                     "company_share": company_share(upper)})
        # judgment calls between a company class and a non-company class, for the company share
        jc = d.judgment & d.cls.isin(["core", "complement"])
        jn = d.judgment & d.cls.isin(["community", "nonprofit", "academic", "government"])
        sens.append({"frame": name, "variant": "judgment-call companies reclassed as community",
                     "core_share": np.nan, "company_share": company_share(d.assign(cls=np.where(jc, "community",
                                                                                                d.cls)))})
        sens.append({"frame": name, "variant": "judgment-call non-companies reclassed as core",
                     "core_share": np.nan, "company_share": company_share(d.assign(cls=np.where(jn, "core",
                                                                                                d.cls)))})
        top = d[d.cls.isin(["core", "complement"])].groupby("owner").stars.sum().sort_values(ascending=False)
        for k in [1, 3, 5]:
            sens.append({"frame": name, "variant": f"largest {k} company owner(s) dropped",
                         "core_share": core_share(d[~d.owner.isin(top.index[:k])]),
                         "company_share": company_share(d[~d.owner.isin(top.index[:k])])})
        res[name]["sensitivity"] = sens
        pd.DataFrame(sens).to_csv(f"data/{'h7' if name == 'A' else 'h10'}_sensitivity.csv", index=False)
    return res


def spearman_ci(x, y, n=5000):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rho = stats.spearmanr(x, y).statistic
    bs = []
    for _ in range(n):
        i = RNG.integers(0, len(x), len(x))
        if len(set(x[i])) > 1 and len(set(y[i])) > 1:
            bs.append(stats.spearmanr(x[i], y[i]).statistic)
    return rho, np.percentile(bs, [2.5, 97.5])


def company_table():
    """One row per company (several GitHub orgs can belong to one company), with its stars in the two frames.

    Stars: every software repo of the company's orgs in Frame A or B, counted once. `stars_pre2025` drops repos
    created in 2025-26 (an exploratory check on recent AI-era star inflation, not pre-registered).
    `raised_usd` is the larger of disclosed equity funding and the SEC Form D total sold, both understatements.
    """
    F = pd.read_csv("data/core_financials.csv")
    allr = pd.concat([frame(A), frame(B)]).drop_duplicates("full_name")
    allr["year"] = allr.created_at.astype(str).str[:4]
    F["org_stars"] = F.owner.map(allr.groupby("owner").stars.sum()).fillna(0)
    F["org_stars_pre2025"] = F.owner.map(allr[allr.year < "2025"].groupby("owner").stars.sum()).fillna(0)
    F["key"] = F.entity.fillna(F.owner).str.strip().str.lower()
    agg = {c: "first" for c in F.columns if c not in ("key", "owner", "org_stars", "org_stars_pre2025", "frames",
                                                         "in_frame_a")}
    agg.update({"owner": lambda x: "|".join(x), "org_stars": "sum", "org_stars_pre2025": "sum",
                "frames": lambda x: "".join(sorted(set("".join(x.fillna(""))))), "in_frame_a": "max"})
    Co = F.groupby("key", sort=False).agg(agg).reset_index(drop=True)
    fd = Co.get("form_d_total_sold", pd.Series(np.nan, index=Co.index))
    Co["raised_usd"] = np.fmax(Co.total_funding_usd, fd)
    return Co


def h8_h9():
    try:
        Co = company_table()
    except FileNotFoundError:
        return {}
    res, rows = {}, []
    Co = Co[Co.org_stars > 0]  # a company whose only frame repos are content (e.g. archived, no language) has no stars
    zero = Co.assign(latest_value_usd=np.where(Co.status.eq("shut_down") & Co.latest_value_usd.isna(), 0,
                                               Co.latest_value_usd))
    for label, sub, xcol in [
            ("latest value (disclosed)", Co.dropna(subset=["latest_value_usd"]), "org_stars"),
            ("latest value, shutdowns at zero", zero.dropna(subset=["latest_value_usd"]), "org_stars"),
            ("peak disclosed value", Co.dropna(subset=["peak_value_usd"]).assign(latest_value_usd=lambda x:
                                                                                 x.peak_value_usd), "org_stars"),
            ("disclosed equity funding", Co.dropna(subset=["total_funding_usd"]).assign(
                latest_value_usd=lambda x: x.total_funding_usd), "org_stars"),
            ("capital raised, larger of disclosed and Form D", Co.dropna(subset=["raised_usd"]).assign(
                latest_value_usd=lambda x: x.raised_usd), "org_stars"),
            ("exploratory: latest value, stars on repos created before 2025",
             Co.dropna(subset=["latest_value_usd"]).query("org_stars_pre2025 > 0"), "org_stars_pre2025")]:
        if len(sub) < 5:
            continue
        rho, (lo, hi) = spearman_ci(sub[xcol], sub.latest_value_usd)
        vps = (sub.latest_value_usd / sub[xcol]).replace([np.inf, -np.inf], np.nan).dropna()
        vps = vps[vps > 0]
        rows.append({"measure": label, "n": len(sub), "spearman_rho": round(rho, 3), "ci_low": round(lo, 3),
                     "ci_high": round(hi, 3), "median_usd_per_star": round(vps.median(), 0) if len(vps) else None,
                     "p75_over_p25_usd_per_star": round(vps.quantile(.75) / vps.quantile(.25), 1) if len(vps) > 3
                     else None})
    pd.DataFrame(rows).to_csv("data/h8_correlations.csv", index=False)
    res["H8"] = rows
    Co = company_table()
    fa = Co[Co.in_frame_a == 1].copy()
    st = fa.status.value_counts().to_dict()
    ever = fa.ever_1b.value_counts().to_dict()
    acq = fa[fa.status.eq("acquired") & fa.exit_value_usd.notna() & fa.raised_usd.notna()]
    n = len(fa)
    res["H9"] = {"n_core_companies_frame_a": int(n), "status": st, "ever_1b": ever,
                 "share_ever_1b_of_all": round(ever.get("yes", 0) / n, 3) if n else None,
                 "share_ever_1b_of_known": round(ever.get("yes", 0) / (ever.get("yes", 0) + ever.get("no", 0)), 3)
                 if ever.get("yes", 0) + ever.get("no", 0) else None,
                 "share_shut_down": round(st.get("shut_down", 0) / n, 3) if n else None,
                 "handed_to_foundation": int(fa.h9_addition.sum()),
                 "acquisitions": int(st.get("acquired", 0)),
                 "acquisitions_with_disclosed_price": int(fa[fa.status.eq("acquired")].exit_value_usd.notna().sum()),
                 "acquisitions_with_price_and_funding": int(len(acq)),
                 "acquired_above_capital_raised": int((acq.exit_value_usd > acq.raised_usd).sum()),
                 "with_disclosed_funding": int(fa.total_funding_usd.notna().sum()),
                 "with_form_d": int(fa.get("form_d_total_sold", pd.Series(dtype=float)).notna().sum()),
                 "capital_raised_sum_usd": float(fa.raised_usd.sum()),
                 "median_raised_usd_where_disclosed": float(fa.raised_usd.median())}
    # Exploratory (not pre-registered): by the year the company's first repo in the frames was created, since
    # younger companies have had less time to reach $1B or to fail; and the subset with disclosed capital
    allr = pd.concat([frame(A, "all"), frame(B, "all")]).drop_duplicates("full_name")
    first = allr.groupby("owner").created_at.min().astype(str).str[:4].astype(int)
    fa["first_repo_year"] = fa.owner.map(lambda s: min(first.get(o, 9999) for o in s.split("|")))
    fa["cohort"] = pd.cut(fa.first_repo_year, [0, 2014, 2019, 2022, 2024, 2030],
                          labels=["2014 or earlier", "2015-19", "2020-22", "2023-24", "2025-26"])
    g = fa.groupby("cohort", observed=True).agg(
        companies=("owner", "size"), ever_1b=("ever_1b", lambda x: int((x == "yes").sum())),
        ever_1b_unknown=("ever_1b", lambda x: int((x == "unknown").sum())),
        acquired=("status", lambda x: int((x == "acquired").sum())),
        shut_down=("status", lambda x: int((x == "shut_down").sum())),
        with_disclosed_capital=("raised_usd", lambda x: int(x.notna().sum())))
    g["share_ever_1b"] = (g.ever_1b / g.companies).round(3)
    sub = [("all", fa), ("disclosed capital raised", fa[fa.raised_usd.notna()]),
           ("raised $10M or more", fa[fa.raised_usd >= 1e7])]
    extra = pd.DataFrame([{"cohort": f"subset: {k}", "companies": len(d), "ever_1b": int((d.ever_1b == "yes").sum()),
                           "ever_1b_unknown": int((d.ever_1b == "unknown").sum()),
                           "acquired": int((d.status == "acquired").sum()),
                           "shut_down": int((d.status == "shut_down").sum()),
                           "with_disclosed_capital": int(d.raised_usd.notna().sum()),
                           "share_ever_1b": round((d.ever_1b == "yes").mean(), 3)} for k, d in sub])
    pd.concat([g.reset_index(), extra], ignore_index=True).to_csv("data/h9_by_cohort.csv", index=False)
    res["H9_exploratory"] = pd.concat([g.reset_index(), extra], ignore_index=True).astype(str).to_dict("records")
    fa.to_csv("data/h9_outcomes.csv", index=False)
    # H10: company owners in the science frame
    fb = Co[Co.frames.fillna("").str.contains("B")]
    big = fb[fb.raised_usd >= 1e7]
    res["H10_companies"] = {"core_companies_in_frame_b": int(len(fb)), "raised_10m_or_more": int(len(big)),
                            "names_raised_10m_or_more": big.entity.tolist(),
                            "ever_1b": fb.ever_1b.value_counts().to_dict(), "status": fb.status.value_counts()
                            .to_dict()}
    fb.to_csv("data/h10_core_companies.csv", index=False)
    return res


def h11():
    """Form 990 finances of US nonprofits that own repos (fiscal hosts reported separately), and Open Collective."""
    out = {}
    stars_by_owner = pd.concat([frame(A), frame(B)]).drop_duplicates("full_name").groupby("owner").stars.sum()
    try:
        N = pd.read_csv("data/form990_summary.csv", dtype={"ein": str})
    except FileNotFoundError:
        N = None
    if N is not None and len(N):
        N["fiscal_host"] = N.owner.str.startswith("(fiscal host)")
        N["org_stars"] = N.owner.map(stars_by_owner).fillna(0)
        E = N.groupby("ein").agg(name=("name", "first"), owners=("owner", lambda x: "|".join(x)),
                                 fiscal_host=("fiscal_host", "max"), latest_year=("latest_year", "first"),
                                 latest_revenue=("latest_revenue", "first"), latest_expenses=("latest_expenses",
                                 "first"), latest_net_assets=("latest_net_assets", "first"),
                                 base_year=("base_year", "first"), base_revenue=("base_revenue", "first"),
                                 real_growth=("real_growth", "first"), org_stars=("org_stars", "sum"),
                                 url=("url", "first")).reset_index()
        E["revenue_per_1k_stars"] = (E.latest_revenue / (E.org_stars / 1000)).replace([np.inf, -np.inf], np.nan)
        E["stale"] = E.latest_year < 2021
        E.to_csv("data/h11_nonprofits.csv", index=False)
        own = E[~E.fiscal_host & ~E.stale]
        g = own.dropna(subset=["real_growth"])
        out["form990_owners"] = {"n": int(len(own)), "excluded_stale_latest_before_2021": E[E.stale].name.tolist(),
                                 "median_latest_revenue": float(own.latest_revenue.median()),
                                 "median_latest_revenue_excl_linux_foundation": float(
                                     own[~own.name.str.contains("Linux Foundation")].latest_revenue.median()),
                                 "n_at_least_10m": int((own.latest_revenue >= 1e7).sum()),
                                 "n_with_2019_base": int(len(g)),
                                 "n_real_growth": int((g.real_growth > 0).sum()),
                                 "share_real_growth": round(float((g.real_growth > 0).mean()), 3) if len(g) else None,
                                 "sum_latest_revenue": float(own.latest_revenue.sum())}
        fh = E[E.fiscal_host]
        out["form990_fiscal_hosts"] = fh[["name", "latest_year", "latest_revenue", "base_revenue", "real_growth"]] \
            .to_dict("records")
    try:
        oc = pd.read_csv("data/opencollective.csv")
        oc = oc.merge(C[["owner", "cls"]], on="owner", how="left")
        oc["cls"] = oc.cls.fillna("individual")
        # matches whose names differ but which were checked by hand and are the project's own collective
        manual = {"twbs": "Bootstrap's collective", "yjs": "Y-Collective funds Yjs", "mne-tools": "MNE-Python"}
        good = oc[((oc.name_match == 1) | oc.owner.isin(manual)) & (oc.oc_total_received > 0)].copy()
        good["org_stars"] = good.owner.map(stars_by_owner)
        good.to_csv("data/h11_opencollective.csv", index=False)
        com = good[good.cls == "community"]
        out["open_collective"] = {"matched_with_money": int(len(good)), "by_class_n": good.cls.value_counts().to_dict(),
                                  "by_class_median_yearly_budget": good.groupby("cls").oc_yearly_budget.median()
                                  .round(0).to_dict(),
                                  "community_n": int(len(com)),
                                  "community_median_yearly_budget": float(com.oc_yearly_budget.median()) if len(com)
                                  else None,
                                  "community_n_budget_over_100k": int((com.oc_yearly_budget >= 1e5).sum()),
                                  "community_total_yearly_budget": float(com.oc_yearly_budget.sum()),
                                  "community_owners_in_frames": int(C[C.cls == "community"].shape[0]),
                                  "currencies": good.oc_currency.value_counts().to_dict(),
                                  "note": "budgets are in each collective's own currency (mostly USD), not converted"}
    except FileNotFoundError:
        pass
    return out


if __name__ == "__main__":
    res = {"class_audit": audit_agreement(), "H7_H10": h7_h10()}
    res.update(h8_h9())
    res["H11"] = h11()
    json.dump(res, open("data/results_summary.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float)[:6000])
