# TMS 2027 symposium fit — electrochemistry-forward reframe

Edison ANALYSIS task `8c66fc3c-78ed-44ee-90c6-fa8196126d89` (submitted 2026-07-14 from
branch `claude/issue-159-20260714-0307`, issue vertical-cloud-lab/byu-vcl#159). Re-swept
all 108 TMS 2027 symposia full-text (same bundle as `../tms-symposium-top10/bundle/`)
with an electrochemistry lens, assuming the potentiostat/electrode module is a roadmap
item, not a demonstrated capability.

## Files

- `tms-symposium-electrochem-8c66fc3c-….md` — the ranked answer (top 10 + risk assessment)
- `tms-symposium-electrochem-8c66fc3c-….json` — full task dump
- `tms-symposium-electrochem-SUBMITTED.json` — task ID + bundle URI
- `../../scripts/edison/submit_tms_symposium_electrochem.py` / `fetch_tms_symposium_electrochem.py`

## Outcome

Top fit under the electrochemistry framing: Next Generation Electrometallurgical
Technologies (9.5/10), then AI-Enabled Materials Processing (9.0), Rare Metal
Extraction & Processing (8.6). Edison's caveat: without at least a minimal potentiostat
integration before the July 15, 2026 deadline, the electrometallurgy venues carry
overclaim risk in front of an electrochemistry audience.

**Decision (PR #160):** keep the aqueous SDL framing and submit as a **poster** to one
of the SDL symposia (AI-Enabled Materials Processing, rank #1 in
`../tms-symposium-top10/`). The electrochemistry reframe is shelved unless a
potentiostat module lands before a future deadline.
