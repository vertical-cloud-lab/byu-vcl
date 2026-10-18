# TMS 2027 top-10 symposium ranking for the CubXL abstract (Edison ANALYSIS)

Asks Edison to rank the **top 10 TMS 2027 symposia** for the CubXL
self-driving-laboratory abstract (`abstracts/tms-2027-cubxl/abstract.md`),
sweeping the **full call-for-abstracts text of all 108 symposia** (not just
titles, to surface hidden gems) and weighing the **research backgrounds of each
symposium's organizers** (receptiveness to self-driving labs / lab automation /
open hardware).

- `bundle/` — files uploaded to Edison:
  - `abstract.md` — the draft CubXL abstract (143/150 words).
  - `tms2027-symposia-full-text.md` / `tms2027-symposia.json` — full CFA text
    of all 108 TMS 2027 symposia (title, sponsorship, organizers with
    affiliations, complete scope, deadline), scraped from ProgramMaster with
    `scripts/edison/scrape_tms2027_symposia.py`. This is the same content TMS
    renders into the per-symposium flyer PDFs (tms.org serves those behind
    Cloudflare; ProgramMaster serves the identical source text).
- `tms-symposium-top10-SUBMITTED.json` — task id + uploaded-bundle URI (resumable).
- `tms-symposium-top10-<task_id>.md` / `.json` — fetched answer + full task dump.

Driver scripts: `scripts/edison/submit_tms_symposium_top10.py` (submit) and
`scripts/edison/fetch_tms_symposium_top10.py` (poll + fetch).

Related issue: vertical-cloud-lab/byu-vcl#159.
