# AlSi10Mg EDS cross-comparison — Edison queries (complete)

> **Status (2026-05-22):** All 6 queries completed; integrated findings + recommendations in **[`eds-cross-comparison-edison-results.md`](./eds-cross-comparison-edison-results.md)**. The original ANALYSIS task (`3beffe7c…`) failed because the data bundle was uploaded as separate files; per the [Edison file-management docs](https://docs.edisonscientific.com/edison-client/file-management), the Analysis crow expects a directory uploaded as a single zipped collection via `store_file_content(file_path=DIR, as_collection=True)`. Re-submitted as task `53f221ff-1bcb-4feb-a48b-e3d3c9cc6b95` and succeeded.

Submitted in response to https://github.com/vertical-cloud-lab/byu-vcl/pull/93#issuecomment-4523029351 to compare three SEM-EDS measurement sets on the same nominal material (AlSi10Mg LPBF print, U of U Aconity MIDI) against ASTM E1078 / E1508 guidance.

## Data analyzed

| # | Source | Sample state | Acquisition | Quant (Mg/Al/Si wt%) | Comment ref |
|---|---|---|---|---|---|
| 1 | issue #48 ([comment 4274431356](https://github.com/vertical-cloud-lab/byu-vcl/issues/48#issuecomment-4274431356)) | loose powder on carbon tape (Mar 2026 training) | 30 s live time, training defaults | low confidence — only CSV/XML/MSA spectra, no quant report | gage-erickson |
| 2 | issue #77 ([comment 4356918457](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-4356918457)) | non-flat as-printed surface (Apr 30, 2026) | 15 kV, 460.8 s, amp 1.92 µs, takeoff 48.7°, res 130.4 eV | O 8.10 / Mg 1.64 / Al 80.79 / Si 9.47 | gage-erickson |
| 3 | issue #77 ([comment 4521289146](https://github.com/vertical-cloud-lab/byu-vcl/issues/77#issuecomment-4521289146)) | polished cross-section, Areas 6 & 7 (May 22, 2026) | 15 kV, 573.4 / 409.6 s, amp 0.96 µs, takeoff 35°, res 135.5 eV | Mg 1.43 / Al 89.16 / Si 9.41 (Area 6); Mg 1.42 / Al 89.45 / Si 9.12 (Area 7); no oxygen | gage-erickson |

Nominal AlSi10Mg: Si 9.0–11.0, Mg 0.20–0.45, Fe < 0.55, Al balance.

## Key observations driving the queries
- Polishing successfully removed the 8 wt% surface O signal (good — confirms native Al₂O₃ surface oxide on the as-printed surface).
- Si recovers to 9.1–9.4 wt% on the polished cross-section — within nominal range (good).
- **Mg is consistently ~1.4–1.6 wt% — about 3–7× higher than nominal — across all three datasets, including the polished cross-section.** This is the central question to resolve.
- Amp time was shortened from 1.92 → 0.96 µs going from non-flat → polished, with resolution worsening 130.4 → 135.5 eV. ASTM E1508 favors longer amp time for trace work.
- Standardless eZAF Smart Quant used throughout — no measured Mg standard.
- "Small spheres" coating the polished surface; fishscale melt-pool pattern visible optically but not in SEM.

## Edison tasks submitted (2026-05-22)

Data bundle uploaded as `data_entry:23c00fbb-a03b-42e3-bcac-d924e5db41cf` (`/tmp/eds-bundle` — see README.md inside).

| Job | Task ID | Status | Purpose |
|---|---|---|---|
| ANALYSIS (with files) | `3beffe7c-1535-44ad-924a-ff4a5b8dfe82` | ❌ fail (bundle as individual files) | Independent expert review — see retry below. |
| ANALYSIS (re-uploaded as collection) | `53f221ff-1bcb-4feb-a48b-e3d3c9cc6b95` | ✅ success | Independent expert review of the three datasets; verdict on whether we are on the right track; cause of high Mg; concrete recommendations; clarifying questions. |
| LITERATURE_HIGH | `1c63284b-2f0a-415c-b51f-8c53fe6a4332` | ✅ success | eZAF / standardless quantification systematic bias for Mg in Al matrices; can it produce 3–7× overestimates? |
| LITERATURE_HIGH | `21ba848f-8c6c-4db1-9830-35062b1d11a2` | ✅ success | Where does Mg actually reside in as-built LPBF AlSi10Mg microstructure? Mg2Si / MgAl2O4 / surface segregation post-polish. |
| LITERATURE_HIGH | `afe8c121-9f8e-4444-abd2-31aa5c42c74e` | ✅ success | Amp-time / pulse-processor effect on SDD energy resolution and Mg Kα / Al Kα peak deconvolution; impact of 1.92 → 0.96 µs change. |
| LITERATURE_HIGH | `53ed54dd-a61c-4074-8858-6c0da3e0d7c9` | ✅ success | "Small spheres" on polished LPBF AlSi10Mg cross-sections: artifact vs real microstructure; why melt-pool pattern is invisible in SEM. |
| LITERATURE_HIGH | `705df51f-975c-48fa-8387-3a7e07389f47` | ✅ success | Concrete EDS acquisition SOP for AlSi10Mg per ASTM E1508 / E1078; kV, current, dead-time, live-time, amp-time, standards, ICP-OES cross-validation. |

Slim bundle (raw MSA/CSV/XML + extracted README, no PDFs) for the successful ANALYSIS retry: `data_entry:0bddb41a-235a-4b1c-ad37-b60d24f22163`.

## Retrieving results

```python
import os, uuid
from edison_client import EdisonClient
client = EdisonClient(api_key=os.environ['EDISON_API_KEY'])
for tid in [
    '3beffe7c-1535-44ad-924a-ff4a5b8dfe82',
    '1c63284b-2f0a-415c-b51f-8c53fe6a4332',
    '21ba848f-8c6c-4db1-9830-35062b1d11a2',
    'afe8c121-9f8e-4444-abd2-31aa5c42c74e',
    '53ed54dd-a61c-4074-8858-6c0da3e0d7c9',
    '705df51f-975c-48fa-8387-3a7e07389f47',
]:
    r = client.get_task(uuid.UUID(tid))
    print(tid, r.status)
    print(r.answer)
```

Results integrated into [`eds-cross-comparison-edison-results.md`](./eds-cross-comparison-edison-results.md).
