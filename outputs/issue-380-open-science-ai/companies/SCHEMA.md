# Organization case-study schema (issue #380)

One JSON file per organization: `companies/<group>/<slug>.json`. Missing values are `null`,
never guessed. Every number must trace to an entry in `sources`.

```json
{
  "name": "MongoDB, Inc.",
  "slug": "mongodb",
  "group": "A",
  "category": "software | hardware | ai_lab | big_tech | physical_science | sci_software | foundation | open_infrastructure",
  "subcategory": "database",
  "hq_country": "US",
  "origin": "founder_startup | academic | government | corporate | community | nonprofit",
  "origin_detail": "Founded as 10gen by DoubleClick alumni; MongoDB released 2009",
  "founded_year": 2007,
  "flagship_projects": ["MongoDB"],
  "openness_initial": 3,
  "openness_current": 1,
  "openness_notes": "AGPL until Oct 2018, then SSPL (not OSI-approved)",
  "business_model": "open_core | saas | dual_license | support_services | hardware_sales | proprietary | api | grants | donations | mixed",
  "license_history": [{"year": 2009, "license": "AGPL-3.0 (server)", "note": "", "source": "url"}],
  "relicensing_events": [{"year": 2018, "from": "AGPL-3.0", "to": "SSPL", "direction": "closing | opening",
                          "fork": null, "fork_backer": null, "outcome_note": "", "source": "url"}],
  "funding_total_usd": 311000000,
  "funding_as_of": "2017",
  "ownership_status": "public | private_vc | private_bootstrapped | private_pe | acquired | defunct | nonprofit | government | foundation",
  "exit_events": [{"year": 2017, "type": "IPO | acquisition | take_private | shutdown | merger | bankruptcy",
                   "value_usd": 1200000000, "counterparty": "", "note": "", "source": "url"}],
  "latest_value_usd": 25000000000,
  "latest_value_type": "market_cap | private_valuation | acquisition_price | null",
  "latest_value_date": "2026-11",
  "revenue_latest_usd": 2000000000,
  "revenue_year": 2025,
  "employees_latest": 5000,
  "still_operating": true,
  "end_year": null,
  "us_focus": true,
  "risk_events": ["2018 SSPL relicense; Debian/Fedora dropped MongoDB"],
  "robustness": "Single-vendor control; no foundation; AWS DocumentDB compatible API",
  "physical_science_relevance": "",
  "openness_effect_assessment": "What did openness (or closing) do to growth, community, risk? 2-4 sentences, evidence-based.",
  "key_takeaway": "One customized paragraph.",
  "confidence": "high | medium | low",
  "searches": ["exact query 1", "exact query 2"],
  "sources": [{"url": "https://...", "title": "...", "publisher": "...", "date": "YYYY-MM-DD", "supports": "funding_total_usd, exit_events[0]"}]
}
```

## Openness scale (0–4)

| Level | Software / AI | Hardware |
| --- | --- | --- |
| 0 Closed | Proprietary product, no meaningful public source or weights | Closed designs and firmware |
| 1 Restricted | Source-available or weights under a non-OSI license (SSPL, BSL, ELv2, FSL, Llama licence, non-commercial, RAIL); or only peripheral SDKs/clients open | Only peripheral parts open (e.g. slicer software) |
| 2 Open core | OSI-licensed core, proprietary enterprise features or SaaS are the business | Firmware/software open but hardware designs closed, or older models open and new ones closed |
| 3 Open source | Substantially the whole product OSI-licensed; money from support, hosting, services | Most current design files (CAD, PCB, BOM, firmware) published under an open licence |
| 4 Open + open governance | OSI-licensed **and** neutral foundation / community governance, or fully open data/science infrastructure | Fully open designs (OSHWA-certifiable) plus community governance (e.g. RepRap) |

Record both the initial and the current level; relicensing in either direction goes in
`relicensing_events` with `direction`.
