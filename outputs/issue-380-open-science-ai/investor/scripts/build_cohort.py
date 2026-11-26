#!/usr/bin/env python3
"""Turn the verified listing and deal terms (data/cohort_listings_verified.csv) into the H1 analysis table
(data/cohort_listings.csv). Every judgment call is here, in code, so it can be checked:

- Value at exit is what a holder of one share bought at the offer received, on the date the money was paid:
  cash deal prices; for stock deals the value on the closing date (MuleSoft $44.73, Hortonworks $13.53); plus
  special dividends and spin-offs (SolarWinds: $9.25 buyout per original share after its 1-for-2 reverse
  split, $1.25 of special dividends, and half an N-able share valued at its first regular-way day's high-low
  average, $14.05).
- Exit dates are when tendering holders were paid or the shares stopped trading (Talend 2021-07-30, SUSE
  2023-10-06, MariaDB 2024-07-25), not the later legal completion.
- Domo sold its business in 2026 and trades as a cash shell (HUCK); it is valued at the market price.
- Cohorts: "open_source" and "closed" are the pre-registered lists (JFrog is in the open-source list but is
  analysed both ways). Companies found after pre-registration are marked *_sensitivity: Instructure (both
  listings), ForgeRock and Tenable (open-source origin), and UiPath, C3.ai and Amplitude (closed, borderline
  categories). The sensitivity offer prices for Tenable, UiPath, C3.ai and Amplitude are from memory and were
  not verified against a filing (the session's web-search budget ran out).
"""
import pandas as pd
v = pd.read_csv("data/cohort_listings_verified.csv")
SHORT = {"Domo (now Huckleberry.ai)": "Domo", "Instructure (first listing)": "Instructure (2015 listing)",
         "Instructure Holdings (second listing)": "Instructure (2021 listing)", "MariaDB plc": "MariaDB",
         "Pivotal Software": "Pivotal"}
YAHOO = {"MongoDB": "MDB", "Elastic": "ESTC", "JFrog": "FROG", "Kaltura": "KLTR", "GitLab": "GTLB",
         "Atlassian": "TEAM", "Nutanix": "NTNX", "Appian": "APPN", "Domo": "DOMO_HUCK", "PagerDuty": "PD",
         "Fastly": "FSLY", "Dynatrace": "DT", "Cloudflare": "NET", "Datadog": "DDOG", "Snowflake": "SNOW",
         "Unity Software": "U", "Palantir": "PLTR", "DigitalOcean": "DOCN", "AvePoint": "AVPT", "Backblaze": "BLZE"}
PAID = {"Talend": "2021-07-30", "SUSE": "2023-10-06", "MariaDB": "2024-07-25"}
rows = []
for _, r in v.iterrows():
    name = SHORT.get(r.company, r.company)
    coh = "open_source" if r.cohort == "open-source" else "closed"
    if name in ("Instructure (2015 listing)", "Instructure (2021 listing)", "ForgeRock"):
        coh = "open_source_sensitivity"
    listed = name in YAHOO
    exitp = None; dist = 0.0; exd = None
    if not listed:
        exitp = float(r.exit_price_per_share); exd = PAID.get(name, r.exit_close_date)
        if name == "SolarWinds":
            exitp = 9.25; dist = 1.25 + 0.5 * 14.05
    rows.append({"cohort": coh, "company": name, "listing_type": r.listing_type.split(" (")[0], "currency": r.currency,
                 "status": "listed" if listed else "exited", "listing_date": r.listing_date, "offer_price": r.offer_price,
                 "exit_price_per_share": exitp, "distributions_per_share": dist if not listed else None,
                 "exit_close_date": exd, "first_day_close": r.first_day_close, "yahoo_ticker": YAHOO.get(name),
                 "source_listing": r.source_listing, "source_exit": r.source_exit})
extra = [  # found after pre-registration; offer prices from memory, unverified
    ("open_source_sensitivity", "Tenable", "IPO", "2018-07-26", 23.0, "TENB"),
    ("closed_sensitivity", "UiPath", "IPO", "2021-04-21", 56.0, "PATH"),
    ("closed_sensitivity", "C3.ai", "IPO", "2020-12-09", 42.0, "AI"),
    ("closed_sensitivity", "Amplitude", "direct listing", "2021-09-28", 35.0, "AMPL")]
for coh, name, lt, d, p, t in extra:
    rows.append({"cohort": coh, "company": name, "listing_type": lt, "currency": "USD", "status": "listed",
                 "listing_date": d, "offer_price": p, "exit_price_per_share": None, "distributions_per_share": None,
                 "exit_close_date": None, "first_day_close": None, "yahoo_ticker": t,
                 "source_listing": "from memory; unverified (web-search budget exhausted)", "source_exit": ""})
out = pd.DataFrame(rows); out.to_csv("data/cohort_listings.csv", index=False)
print(out.groupby("cohort").size()); print(out[["cohort", "company", "status", "offer_price", "exit_price_per_share", "distributions_per_share", "exit_close_date"]].to_string())
