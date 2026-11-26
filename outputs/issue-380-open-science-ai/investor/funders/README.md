# Who funds open-source-minded ventures (issue #380, round 2, part 3)

Sterling asked for a thorough, manual list of the investors, firms, philanthropists and other VC and VC-like
sources that have funded open-source-minded ventures. Read [`FUNDERS.md`](FUNDERS.md) first, then
[`FUNDER_LIST.md`](FUNDER_LIST.md) for every funder. The scope and counting rules were committed before any data
([`PROTOCOL.md`](PROTOCOL.md), `448c8c2`).

## Pipeline

Run from this folder. Python 3 with `requests`, `beautifulsoup4`, `lxml` and `matplotlib`; the Edison steps need the
Python 3.12 venv described in [`../README.md`](../README.md).

| Step | Script | Output |
| --- | --- | --- |
| 1. Ventures: U1 from part 2's core companies, U2 and U3 listed in the script | `scripts/build_inputs.py` | `data/ventures_input.csv`, `data/deal_passes/input_{a,s,c}NN.csv` |
| 2. YC companies tagged or described as open source; ROSS Index; U4 | `scripts/yc_open_source.py`, `scripts/ross_index.py`, `scripts/build_u4.py`, `scripts/build_u4.py --extra` | `data/yc_open_source.csv`, `data/u4/ross_index.csv`, `input_{d,e}NN.csv` |
| 3. Leads from open news APIs, Wikipedia/Wikidata and company sites | `scripts/investor_leads.py [pass ...]` | `data/leads/leads_<pass>.{jsonl,md}` |
| 4. Deal passes: research agents follow [`deal_rules.md`](deal_rules.md), search with `scripts/find_pages.py`, write with `scripts/append_deals.py` | by hand (agents) | `data/deal_passes/{ventures,deals}_<pass>.csv` |
| 5. Deepening passes: pick thin histories, then agents follow [`deepen_rules.md`](deepen_rules.md) | `scripts/deepen_inputs.py`, then by hand | `input_xNN.csv`, `existing_xNN.md`, `{ventures,deals}_xNN.csv` |
| 6. Program passes: agents follow [`program_rules.md`](program_rules.md) and the scopes in `data/program_passes/` | by hand, `scripts/append_programs.py` | `data/program_passes/programs_pN.csv` |
| 7. Investors' own portfolio pages | `scripts/portfolio_sweep.py` | `data/portfolio/` |
| 8. Edison: literature question and blind audit of 40 random ventures | `scripts/edison_funders.py submit`, `... fetch --wait`, `../scripts/edison_files.py fund_deal_audit` | `edison/` |
| 9. Funder types and aliases (hand-made) | `scripts/investor_types_seed.py` | `data/investor_types.csv` (aliases: `data/investor_aliases.csv`) |
| 10. Merge, with the hand-made corrections from Edison's review: ventures entered twice, ventures out of scope, purchases of control, one name that means a different firm in one venture, kinds of thesis statement | `scripts/build_funders.py` (reads `data/venture_aliases.csv`, `out_of_scope.csv`, `round_exclusions.csv`, `contextual_aliases.csv`, `thesis_kinds.csv`) | `data/ventures.csv`, `deals.csv` (with `counted` and `round_id`), `investor_links.csv`, `investors.csv`, `funders_summary.json` |
| 11. Checks: names against cited pages; Edison comparison; then add the audit's rounds and merge again | `scripts/check_sources.py`, `scripts/edison_compare.py`, `scripts/merge_edison_audit.py`, `scripts/build_funders.py` | `data/source_checks_*.csv`, `data/edison_*` |
| 11b. After Edison's review of the write-up (`edison/fund_review_*`): PeerJ added to U2 and its rounds entered by hand (pass `h01`); Moore's grants to Julia Computing and Continuum Analytics entered from Moore's grant pages (pass `xh1`); verified programs added (pass `p7`) | `scripts/late_additions.py`, `scripts/append_deals.py`, `scripts/append_programs.py` | `data/ventures_input.csv`, `data/deal_passes/*_h01.csv`, `*_xh1.csv`, `data/program_passes/programs_p7.csv` |
| 12. Tables, numbers, figures, write-up | `scripts/funders_tables.py`, `scripts/funders_numbers.py`, `scripts/funders_figures.py`, `scripts/funder_list_md.py`, `scripts/render_funders_md.py` | `data/tables/`, `data/funders_numbers.json`, `figures/`, `FUNDER_LIST.md`, `FUNDERS.md` (from `FUNDERS.template.md`) |

Pages, APIs and company sites change; the data is dated 2026-11-26. The session's web-search budget ran out
partway through step 4, which is why steps 3 and 4 lean on open APIs. No searching was done after the review: step
11b used only pages the review cited or that the data already pointed to.
