#!/usr/bin/env python3
"""H1: what public investors earned from every 2014-2022 listing of an open-source-origin company, against a
rule-chosen cohort of closed-source infrastructure-software listings from the same years.

Inputs: data/cohort_listings.csv (listing and exit terms, with sources) and the Yahoo price files written by
scripts/fetch_prices.py. For companies still listed, the value of one share bought at the offer price is the
latest adjusted close times (first-day raw close / first-day adjusted close), so dividends and splits count.
For companies that left the market, it is the deal value per share plus any distributions. Benchmarks (QQQ,
IGV) are total-return over exactly the same holding window. Writes data/h1_returns.csv and
data/h1_summary.csv. Run from investor/."""
import numpy as np, pandas as pd
rng = np.random.default_rng(1)
END = pd.Timestamp("2026-11-24")
c = pd.read_csv("data/cohort_listings.csv", parse_dates=["listing_date", "exit_close_date"])
adj = pd.read_csv("data/prices_daily_adjclose.csv", index_col=0, parse_dates=True)
raw = pd.read_csv("data/prices_daily_close.csv", index_col=0, parse_dates=True)
for extra in ["data/prices_extra_adjclose.csv"]:
    try:
        e = pd.read_csv(extra, index_col=0, parse_dates=True); adj = adj.join(e, how="outer")
    except FileNotFoundError:
        pass
try:
    raw = raw.join(pd.read_csv("data/prices_extra_close.csv", index_col=0, parse_dates=True), how="outer")
except FileNotFoundError:
    pass

def px(frame, t, date, side="after"):
    s = frame[t].dropna()
    s = s[s.index >= date] if side == "after" else s[s.index <= date]
    return (s.iloc[0], s.index[0]) if side == "after" else (s.iloc[-1], s.index[-1])

def bench(t, a, b):
    pa, _ = px(adj, t, a); pb, _ = px(adj, t, b, "before")
    return pb / pa

rows = []
for _, r in c.iterrows():
    a = r.listing_date
    if r.status == "listed":
        t = r.yahoo_ticker
        p1_adj, d1 = px(adj, t, a); p1_raw, _ = px(raw, t, a)
        pend, dend = px(adj, t, END, "before")
        value = pend * (p1_raw / p1_adj)          # value now of one share bought on day 1 at the day-1 close
        b = dend
        first_close = p1_raw if pd.isna(r.first_day_close) else r.first_day_close
    else:
        value = r.exit_price_per_share + (0 if pd.isna(r.distributions_per_share) else r.distributions_per_share)
        b = r.exit_close_date
        first_close = r.first_day_close
    yrs = (b - a).days / 365.25
    m_offer = value / r.offer_price
    m_first = value / first_close if pd.notna(first_close) else np.nan
    q = bench("QQQ", a, b); g = bench("IGV", a, b)
    rows.append({**{k: r[k] for k in ["cohort", "company", "listing_type", "status"]},
                 "listing_date": a.date(), "end_date": pd.Timestamp(b).date(), "years": yrs,
                 "offer_price": r.offer_price, "first_day_close": first_close, "end_value_per_share": value,
                 "multiple_from_offer": m_offer, "multiple_from_first_close": m_first,
                 "cagr_from_offer": m_offer ** (1 / yrs) - 1,
                 "cagr_from_first_close": m_first ** (1 / yrs) - 1 if pd.notna(m_first) else np.nan,
                 "qqq_multiple": q, "qqq_cagr": q ** (1 / yrs) - 1, "igv_multiple": g, "igv_cagr": g ** (1 / yrs) - 1})
R = pd.DataFrame(rows)
R["excess_vs_qqq_offer"] = R.cagr_from_offer - R.qqq_cagr
R["excess_vs_qqq_first"] = R.cagr_from_first_close - R.qqq_cagr
R["excess_vs_igv_offer"] = R.cagr_from_offer - R.igv_cagr
R["beat_qqq_offer"] = R.multiple_from_offer > R.qqq_multiple
R["lost_money_offer"] = R.multiple_from_offer < 1
R.to_csv("data/h1_returns.csv", index=False)

def boot_diff(x, y, n=10000):
    x, y = np.asarray(x), np.asarray(y)
    d = [np.median(rng.choice(x, len(x))) - np.median(rng.choice(y, len(y))) for _ in range(n)]
    return np.percentile(d, [2.5, 97.5])

def perm_p(x, y, n=20000):
    x, y = np.asarray(x), np.asarray(y); obs = np.median(x) - np.median(y); z = np.concatenate([x, y]); k = 0
    for _ in range(n):
        rng.shuffle(z); k += abs(np.median(z[:len(x)]) - np.median(z[len(x):])) >= abs(obs)
    return k / n

def summarize(df, label):
    out = []
    for coh, g in df.groupby("cohort"):
        out.append({"set": label, "cohort": coh, "n": len(g),
                    "median_multiple_offer": g.multiple_from_offer.median(),
                    "median_cagr_offer": g.cagr_from_offer.median(),
                    "median_excess_qqq_offer": g.excess_vs_qqq_offer.median(),
                    "median_excess_qqq_first": g.excess_vs_qqq_first.median(),
                    "median_excess_igv_offer": g.excess_vs_igv_offer.median(),
                    "share_beat_qqq": g.beat_qqq_offer.mean(), "share_lost_money": g.lost_money_offer.mean(),
                    "share_still_listed": (g.status == "listed").mean(), "median_years": g.years.median()})
    o = pd.DataFrame(out)
    oss = df[df.cohort == "open_source"]; cl = df[df.cohort == "closed"]
    for col in ["excess_vs_qqq_offer", "excess_vs_qqq_first", "excess_vs_igv_offer"]:
        x, y = oss[col].dropna(), cl[col].dropna()
        lo, hi = boot_diff(x, y)
        o.loc[len(o)] = {"set": label, "cohort": f"difference ({col}), open minus closed",
                         "n": f"{len(x)} vs {len(y)}", "median_excess_qqq_offer": np.median(x) - np.median(y),
                         "median_multiple_offer": lo, "median_cagr_offer": hi, "share_beat_qqq": perm_p(x, y)}
    o = o.astype(object)
    o.loc[o.cohort.astype(str).str.startswith("difference"), ["median_multiple_offer", "median_cagr_offer", "share_beat_qqq"]] = \
        o.loc[o.cohort.astype(str).str.startswith("difference"), ["median_multiple_offer", "median_cagr_offer", "share_beat_qqq"]].values
    return o.rename(columns={})

def relabel(df, jfrog=None, extras=False):
    d = df.copy()
    if extras:
        d["cohort"] = d.cohort.replace({"open_source_sensitivity": "open_source", "closed_sensitivity": "closed"})
    d = d[d.cohort.isin(["open_source", "closed"])]
    if jfrog is None:
        d = d[d.company != "JFrog"]
    else:
        d.loc[d.company == "JFrog", "cohort"] = jfrog
    return d

S = [summarize(relabel(R), "pre-registered: 14 open-source vs 25 closed (JFrog excluded)"),
     summarize(relabel(R, jfrog="open_source"), "JFrog counted as open source"),
     summarize(relabel(R, jfrog="closed"), "JFrog counted as closed"),
     summarize(relabel(R, extras=True), "plus companies found after pre-registration (Instructure x2, ForgeRock, Tenable; UiPath, C3.ai, Amplitude)")]
# Hortonworks held through Cloudera's $16 buyout (1.305 x $16 = $20.88 on 2021-10-08) instead of valued at the merger close
H = R.copy(); i = H.company == "Hortonworks"
yrs = (pd.Timestamp("2021-10-08") - pd.Timestamp("2014-12-12")).days / 365.25
q = bench("QQQ", pd.Timestamp("2014-12-12"), pd.Timestamp("2021-10-08")); g = bench("IGV", pd.Timestamp("2014-12-12"), pd.Timestamp("2021-10-08"))
m = 20.88 / 16; mf = 20.88 / 26.38
H.loc[i, ["years", "multiple_from_offer", "cagr_from_offer", "cagr_from_first_close", "qqq_multiple", "qqq_cagr", "igv_cagr"]] = [yrs, m, m ** (1 / yrs) - 1, mf ** (1 / yrs) - 1, q, q ** (1 / yrs) - 1, g ** (1 / yrs) - 1]
H["excess_vs_qqq_offer"] = H.cagr_from_offer - H.qqq_cagr; H["excess_vs_qqq_first"] = H.cagr_from_first_close - H.qqq_cagr
H["excess_vs_igv_offer"] = H.cagr_from_offer - H.igv_cagr; H["beat_qqq_offer"] = H.multiple_from_offer > H.qqq_multiple; H["lost_money_offer"] = H.multiple_from_offer < 1
S.append(summarize(relabel(H), "Hortonworks held through Cloudera's 2021 buyout"))
pd.concat(S).to_csv("data/h1_summary.csv", index=False)
pd.set_option("display.width", 250)
print(R[["cohort", "company", "status", "years", "multiple_from_offer", "cagr_from_offer", "qqq_cagr", "excess_vs_qqq_offer", "excess_vs_qqq_first"]].round(3).sort_values(["cohort", "excess_vs_qqq_offer"]).to_string())
print(pd.concat(S).round(3).to_string())
