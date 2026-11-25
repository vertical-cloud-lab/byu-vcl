#!/usr/bin/env python3
"""Who the complement companies are: stars by ultimate parent, with the parent's listing (if any).

The parent names come from the classification (parent if given, else entity), normalised below. Tickers are
assigned by hand for listed parents; private ones are marked private. Writes data/complement_parents.csv and
appends the listed parents to data/listed_targets.csv. Run from owners/.
"""
import pandas as pd

exec(open("scripts/owners_analysis.py").read().split("if __name__")[0])

NORMALISE = {"Alibaba": "Alibaba Group", "Alibaba Group (affiliate)": "Ant Group", "Google": "Alphabet",
             "Meta": "Meta Platforms", "Amazon Web Services": "Amazon", "SpaceX": "SpaceX (xAI)",
             "xAI": "SpaceX (xAI)", "Red Hat": "IBM", "IBM Research": "IBM", "GitHub": "Microsoft",
             "Tencent ARC Lab": "Tencent", "Tencent Cloud": "Tencent", "Volcano Engine": "ByteDance",
             "Google DeepMind": "Alphabet", "Google Quantum AI": "Alphabet", "Baidu Apollo": "Baidu",
             "Alibaba Cloud": "Alibaba Group", "Ele.me": "Alibaba Group", "Alibaba Token Hub": "Alibaba Group",
             "VMware Tanzu": "Broadcom", "X Corp.": "SpaceX (xAI)", "ZeroSSL (apilayer)": "Idera",
             "ZeroSSL": "Idera", "Carl Zeiss Microscopy": "Carl Zeiss AG", "Carl Zeiss AG": "Carl Zeiss AG",
             "Sea Limited (Sea AI Lab)": "Sea Limited", "OMRON SINIC X": "OMRON", "Qunar": "Trip.com Group",
             "Fujitsu Research of Europe": "Fujitsu", "Valence Labs": "Recursion Pharmaceuticals",
             "Merck KGaA (EMD Group)": "Merck KGaA"}
TICKERS = {"Microsoft": "MSFT", "Alphabet": "GOOGL", "Meta Platforms": "META", "Alibaba Group": "BABA",
           "Apple": "AAPL", "Amazon": "AMZN", "NVIDIA": "NVDA", "IBM": "IBM", "Broadcom": "AVGO", "Baidu": "BIDU",
           "Tencent": "0700.HK", "Bilibili": "BILI", "Cloudflare": "NET", "Airbnb": "ABNB", "Shopify": "SHOP",
           "Block, Inc.": "XYZ", "Coinbase": "COIN", "Atlassian": "TEAM", "Adobe": "ADBE", "Rapid7": "RPD",
           "JD.com": "JD", "Netflix": "NFLX", "Uber": "UBER", "Oracle": "ORCL", "Intel": "INTC",
           "Datadog": "DDOG", "DigitalOcean": "DOCN", "CoStar Group": "CSGP", "Illumina": "ILMN",
           "Schrödinger, Inc.": "SDGR", "AstraZeneca": "AZN", "BASF": "BAS.DE", "Merck KGaA": "MRK.DE",
           "Dassault Systemes": "DSY.PA", "Fujitsu": "6702.T", "OMRON": "6645.T", "Sea Limited": "SE",
           "Trip.com Group": "TCOM", "Hancom": "030520.KQ", "Recursion Pharmaceuticals": "RXRX",
           "BioNTech": "BNTX", "Oxford Nanopore Technologies": "ONT.L", "EPAM Systems": "EPAM",
           "Rigetti Computing": "RGTI", "Kuaishou": "1024.HK", "ZOZO": "3092.T", "Novonesis": "NSIS-B.CO",
           "Deezer": "DEEZR.PA", "Nexon": "3659.T", "Workday": "WDAY", "Snowflake": "SNOW", "F5": "FFIV",
           "SUSE": None, "8x8": "EGHT", "Netlify": None, "Figma": "FIG", "OutSystems": None}


def main():
    d = pd.concat([frame(A).assign(fr="A"), frame(B).assign(fr="B")]).drop_duplicates("full_name")
    co = d[d.cls == "complement"].reset_index(drop=True)
    co["ultimate"] = co.parent.fillna(co.entity).replace(NORMALISE)
    co["stars_a"] = co.stars.where(co.fr == "A", 0)
    g = co.groupby("ultimate").agg(stars=("stars", "sum"), stars_frame_a=("stars_a", "sum"), repos=("stars", "size"),
                                   orgs=("owner", lambda s: ";".join(sorted(set(s))))).sort_values("stars",
                                                                                                   ascending=False)
    g["ticker"] = g.index.map(TICKERS)
    g.to_csv("data/complement_parents.csv")
    t = g.dropna(subset=["ticker"]).reset_index()[["ultimate", "ticker"]].rename(columns={"ultimate": "entity"})
    t["role"] = "complement parent"
    t.to_csv("data/listed_targets.csv", index=False)
    print(len(g), "parents;", len(t), "listed; share of complement stars with a listed parent:",
          round(g.dropna(subset=["ticker"]).stars.sum() / g.stars.sum(), 3))


if __name__ == "__main__":
    main()
