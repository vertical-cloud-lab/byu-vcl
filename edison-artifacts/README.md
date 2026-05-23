# Edison Scientific (FutureHouse PaperQA / Finch) artifacts — PR #93

Raw answers, queries, metadata, and (for the ANALYSIS task) the full Jupyter
notebook for every Edison task submitted from this PR. Fetched via
`EdisonClient.get_task(uuid.UUID(<task_id>))`; `formatted_answer` is the
citation-formatted markdown returned by PaperQA, `answer` is the plain-text
summary, and `notebook.ipynb` is the executed analysis notebook returned by the
Finch `job-futurehouse-data-analysis-crow-high` agent.

| Folder | Task ID | Kind | Topic |
|---|---|---|---|
| `lit-quant-analysis-alsi10mg-powder__cd669bc0` | `cd669bc0-0b4b-4b1f-8e32-7b5ec8aa474e` | LITERATURE_HIGH | Quantitative compositional analysis of AlSi10Mg AM powder (initial broad search) |
| `analysis-eds-cross-comparison__53f221ff` | `53f221ff-1bcb-4feb-a48b-e3d3c9cc6b95` | ANALYSIS (Finch) | Cross-comparison of the three EDS datasets with the data bundle attached as a zipped collection |
| `lit-ezaf-standardless-mg-bias__1c63284b` | `1c63284b-2f0a-415c-b51f-8c53fe6a4332` | LITERATURE_HIGH | Standardless eZAF systematic bias for trace Mg in an Al matrix |
| `lit-mg-microstructural-location__21ba848f` | `21ba848f-8c6c-4db1-9830-35062b1d11a2` | LITERATURE_HIGH | Where Mg actually resides in as-built LPBF AlSi10Mg (Mg₂Si / MgAl₂O₄ / surface segregation) |
| `lit-amp-time-mg-al-deconvolution__afe8c121` | `afe8c121-9f8e-4444-abd2-31aa5c42c74e` | LITERATURE_HIGH | Amp-time / pulse-processor effect on SDD energy resolution and Mg Kα / Al Kα deconvolution |
| `lit-small-spheres-fishscale__53ed54dd` | `53ed54dd-a61c-4074-8858-6c0da3e0d7c9` | LITERATURE_HIGH | "Small spheres" on polished LPBF AlSi10Mg cross-sections; missing melt-pool/fishscale pattern |
| `lit-eds-sop-astm-e1508__705df51f` | `705df51f-975c-48fa-8387-3a7e07389f47` | LITERATURE_HIGH | Concrete EDS acquisition SOP for AlSi10Mg per ASTM E1508 / E1078 |
| `lit-sem-eds-workflow-parameters__2c752db2` | `2c752db2-d735-4937-b1b2-dc35eb0cad88` | LITERATURE_HIGH | Standard SEM/EDS workflow parameters (magnification ladder, fixed vs tunable settings) for powders + printed parts |

The integrated, human-curated summaries of these artifacts live in:

- `../eds-quantitative-analysis-alsi10mg.md` (uses `cd669bc0`)
- `../eds-cross-comparison-edison-results.md` (uses `53f221ff` + the five LITERATURE_HIGH tasks above)
- `../sem-eds-workflow-parameters-sop.md` (uses `2c752db2`)

To re-fetch any task:

```python
import os, uuid
from edison_client import EdisonClient
c = EdisonClient(api_key=os.environ['EDISON_API_KEY'])
r = c.get_task(uuid.UUID('<task_id>'))
print(r.formatted_answer or r.answer)
```

Failed tasks (no useful output, not archived here):

- `3beffe7c-1535-44ad-924a-ff4a5b8dfe82` — first ANALYSIS attempt; bundle uploaded as separate files
- `eb5e59c7-96c8-4c34-864f-8842d5c774d4` — second attempt; oversized bundle (PDFs still included)

The successful retry (`53f221ff`) used `client.store_file_content(file_path=DIR, as_collection=True)` per the [Edison file-management docs](https://docs.edisonscientific.com/edison-client/file-management).
