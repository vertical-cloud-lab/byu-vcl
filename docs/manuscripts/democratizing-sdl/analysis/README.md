# Labour-cost analysis

Reproduces Figure 1 and Tables 3–4 of the Perspective, plus the values in ESI Note S4.

```
python -m pip install -r requirements.txt
python labor_cost_analysis.py
```

| Output | What it is |
|---|---|
| `table1-derived.csv` | Per project: bill of materials, build hours, break-even wage, and labour cost and labour share at $25, $50 and $75 per hour |
| `sensitivity.csv` | Number of projects where labour exceeds parts, and median and mean labour share, at 12 loaded rates from $10 to $150 per hour |
| `../figures/fig1-labour-vs-bom.png` | Figure 1 |

The only inputs are the self-reported cost-to-reproduce and time-to-reproduce figures in the paper's Table 1, which are hard-coded in `PROJECTS`. Ranges enter at their midpoint, and DiSCO's "3 months" is read as 480 h at 1 FTE. The break-even wage is `bom / hours` and does not depend on any assumed rate.

On 2026-10-10, a run from a clean copy reproduced both CSVs byte for byte.

`.zenodo.json` holds the metadata for archiving this folder on Zenodo at acceptance. Digital Discovery requires a DOI for custom code before publication; a GitHub link is enough while the paper is in review.
