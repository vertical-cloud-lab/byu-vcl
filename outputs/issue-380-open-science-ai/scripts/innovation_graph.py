#!/usr/bin/env python3
"""US open-source licence mix and developer counts over time, from the GitHub Innovation Graph (CC0).
licenses.csv counts *pushers* (developers who pushed) to public repos by SPDX licence, economy and quarter."""
import sys, pandas as pd, numpy as np
sys.path.insert(0, "scripts")
from viz_style import *
import matplotlib.ticker as mt
L = pd.read_csv("data/innovationgraph/licenses.csv"); Dv = pd.read_csv("data/innovationgraph/developers.csv")
L["t"] = L.year + (L.quarter - 1) / 4; Dv["t"] = Dv.year + (Dv.quarter - 1) / 4
fam = {"MIT": "Permissive", "Apache-2.0": "Permissive", "BSD-3-Clause": "Permissive", "BSD-2-Clause": "Permissive", "ISC": "Permissive", "Unlicense": "Permissive",
       "0BSD": "Permissive", "CC0-1.0": "Permissive", "GPL-3.0": "Copyleft", "GPL-2.0": "Copyleft", "AGPL-3.0": "Copyleft", "LGPL-3.0": "Copyleft",
       "LGPL-2.1": "Copyleft", "MPL-2.0": "Copyleft", "EPL-2.0": "Copyleft", "EUPL-1.2": "Copyleft"}
L["family"] = L.spdx_license.map(fam).fillna("Other / unrecognised")
us = L[L.iso2_code == "US"]
mix = us.groupby(["t", "family"]).num_pushers.sum().unstack().fillna(0)
share = mix.div(mix.sum(axis=1), axis=0)
share.to_csv("data/innovationgraph_us_license_family_share.csv")
top = us.groupby("spdx_license").num_pushers.sum().sort_values(ascending=False).head(8)
print("top US licences by pushers (all quarters):"); print(top)
print(share.iloc[[0, -1]].round(3))
dev = Dv.pivot_table(index="t", columns="iso2_code", values="developers")
w = Dv.groupby("t").developers.sum()
usdev = pd.DataFrame({"us_developers": dev["US"], "world_developers_sum": w, "us_share": dev["US"] / w})
usdev.to_csv("data/innovationgraph_us_developers.csv"); print(usdev.iloc[[0, -1]])
fig = plt.figure(figsize=(W, H), dpi=DPI)
fig.text(0.06, 0.92, "US open-source activity on GitHub: who builds, under which licences", fontsize=32, fontweight="bold", va="center")
fig.text(0.06, 0.865, "GitHub Innovation Graph (CC0): developers in the US, and the licence families of public repos US developers pushed to", fontsize=20, color=TEXT2, va="center")
source_note(fig, "Source: github/innovationgraph data/developers.csv and data/licenses.csv (quarterly, from 2020). Licence counts are pushers per licence; 'Other' includes repos with no recognised licence.")
ax1 = fig.add_axes((0.06, 0.16, 0.40, 0.6)); ax2 = fig.add_axes((0.56, 0.16, 0.36, 0.6))
ax1.plot(usdev.index, usdev.us_developers / 1e6, color=BLUE); ax1.set_title("US developers (millions)", loc="left", fontsize=22, color=TEXT2)
ax1b = ax1.text(usdev.index[-1], usdev.us_developers.iloc[-1] / 1e6, f"  {usdev.us_developers.iloc[-1] / 1e6:.1f}M", fontsize=17, color=TEXT, va="center")
ax1.set_ylim(0, usdev.us_developers.max() / 1e6 * 1.2)
for fam_, c in [("Permissive", BLUE), ("Copyleft", ORANGE), ("Other / unrecognised", "#77766f")]:
    if fam_ in share: 
        ax2.plot(share.index, share[fam_], color=c, label=fam_)
        ax2.text(share.index[-1] + 0.1, share[fam_].iloc[-1], f"{share[fam_].iloc[-1]:.0%}", fontsize=16, color=TEXT, va="center")
ax2.set_ylim(0, 1); ax2.yaxis.set_major_formatter(mt.PercentFormatter(1.0)); ax2.legend(loc="upper left", fontsize=15)
ax2.set_title("Licence family share of US pushers", loc="left", fontsize=22, color=TEXT2)
fig.savefig("figures/innovationgraph_us.png", dpi=DPI); print("saved")
