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
                          ("crypto owners excluded", d[~d.crypto])]:
            sens.append({"frame": name, "variant": label, "core_share": core_share(dd)})
        lower = d.copy(); lower.loc[(lower.cls == "core") & lower.judgment, "cls"] = "complement"
        upper = d.copy(); upper.loc[(upper.cls == "complement") & upper.judgment, "cls"] = "core"
        sens.append({"frame": name, "variant": "judgment calls against core", "core_share": core_share(lower)})
        sens.append({"frame": name, "variant": "judgment calls toward core", "core_share": core_share(upper)})
        top = d[d.cls.isin(["core", "complement"])].groupby("owner").stars.sum().sort_values(ascending=False)
        for k in [1, 3, 5]:
            sens.append({"frame": name, "variant": f"largest {k} company owner(s) dropped",
                         "core_share": core_share(d[~d.owner.isin(top.index[:k])])})
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


def h8_h9():
    try:
        F = pd.read_csv("data/core_financials.csv")
    except FileNotFoundError:
        return {}
    stars = pd.concat([A, B]).drop_duplicates("full_name").groupby("owner").stars.sum().rename("org_stars")
    F = F.merge(stars, left_on="owner", right_index=True, how="left")
    res, rows = {}, []
    for label, sub in [("latest value (disclosed)", F.dropna(subset=["latest_value_usd"])),
                       ("latest value, shutdowns at zero", F.assign(latest_value_usd=np.where(
                           F.status.eq("shut_down") & F.latest_value_usd.isna(), 0, F.latest_value_usd))
                        .dropna(subset=["latest_value_usd"])),
                       ("peak disclosed value", F.dropna(subset=["peak_value_usd"]).assign(
                           latest_value_usd=lambda x: x.peak_value_usd)),
                       ("total funding", F.dropna(subset=["total_funding_usd"]).assign(
                           latest_value_usd=lambda x: x.total_funding_usd))]:
        if len(sub) < 5:
            continue
        rho, (lo, hi) = spearman_ci(sub.org_stars, sub.latest_value_usd)
        vps = (sub.latest_value_usd / sub.org_stars).replace([np.inf, -np.inf], np.nan).dropna()
        vps = vps[vps > 0]
        rows.append({"measure": label, "n": len(sub), "spearman_rho": round(rho, 3), "ci_low": round(lo, 3),
                     "ci_high": round(hi, 3), "median_usd_per_star": round(vps.median(), 0) if len(vps) else None,
                     "p75_over_p25_usd_per_star": round(vps.quantile(.75) / vps.quantile(.25), 1) if len(vps) > 3
                     else None})
    pd.DataFrame(rows).to_csv("data/h8_correlations.csv", index=False)
    res["H8"] = rows
    fa = F[F.owner.isin(set(frame(A).owner))]
    st = fa.status.value_counts().to_dict()
    ever = fa.ever_1b.value_counts().to_dict()
    acq = fa[fa.status.eq("acquired") & fa.exit_value_usd.notna() & fa.total_funding_usd.notna()]
    res["H9"] = {"n_core_companies_frame_a": int(len(fa)), "status": st, "ever_1b": ever,
                 "share_ever_1b_of_all": round(ever.get("yes", 0) / len(fa), 3) if len(fa) else None,
                 "share_ever_1b_of_known": round(ever.get("yes", 0) / (ever.get("yes", 0) + ever.get("no", 0)), 3)
                 if ever.get("yes", 0) + ever.get("no", 0) else None,
                 "share_shut_down": round(st.get("shut_down", 0) / len(fa), 3) if len(fa) else None,
                 "acquisitions_with_price_and_funding": int(len(acq)),
                 "acquired_above_funding": int((acq.exit_value_usd > acq.total_funding_usd).sum())}
    fa.to_csv("data/h9_outcomes.csv", index=False)
    return res


def h11():
    out = {}
    try:
        N = pd.read_csv("data/form990_summary.csv")
    except FileNotFoundError:
        N = None
    if N is not None and len(N):
        stars = pd.concat([A, B]).drop_duplicates("full_name").groupby("owner").stars.sum().rename("org_stars")
        N = N.merge(stars, left_on="owner", right_index=True, how="left")
        N["revenue_per_1k_stars"] = N.latest_revenue / (N.org_stars / 1000)
        N.to_csv("data/h11_nonprofits.csv", index=False)
        g = N.dropna(subset=["real_growth"])
        out["form990"] = {"n": int(N.ein.nunique()), "median_latest_revenue": float(N.groupby("ein").latest_revenue
                          .first().median()), "n_with_2019_base": int(g.ein.nunique()),
                          "share_real_growth": round(float((g.groupby("ein").real_growth.first() > 0).mean()), 3)
                          if len(g) else None}
    try:
        oc = pd.read_csv("data/opencollective.csv")
        oc = oc.merge(C[["owner", "cls"]], on="owner", how="left")
        out["open_collective"] = {"n": int(len(oc)), "median_yearly_budget": float(oc.oc_yearly_budget.median()),
                                  "by_class": oc.groupby("cls").oc_yearly_budget.median().round(0).to_dict()}
    except FileNotFoundError:
        pass
    return out


if __name__ == "__main__":
    res = {"H7_H10": h7_h10()}
    res.update(h8_h9())
    res["H11"] = h11()
    json.dump(res, open("data/results_summary.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float)[:6000])
