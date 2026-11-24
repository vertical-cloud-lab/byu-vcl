# Group J: AI-era open-source infrastructure (Nov 2026)

WebFetch only, 2026-11-24. Origin: A academic, F founder startup, C community. (x→y): openness, 0–4. n/d: undisclosed (10 of 17). \*: single report.

| Name | Origin | Founded | Licence → now | Model | Latest value (date) | Outcome |
|---|---|---|---|---|---|---|
| Anyscale (Ray) | A, Berkeley | 2019 | Apache-2.0; PyTorch Fdn 2025 (2→2) | Open core | $1.65B acq.\* (2026-07-30) | Nscale, pending |
| vLLM / Inferact | A, Berkeley | 2023 | Apache-2.0; PyTorch Fdn 2025 (3→4) | Foundation; Inferact | $800M (2026-01) | Inferact spin-out |
| Lightning AI | A, NYU/FAIR | 2019 | Apache-2.0 (2→2) | Open core, GPUs | n/d | Merged with Voltage Park |
| Together AI | F | 2022 | Apache/BSD research code (2→2) | API, GPUs | $3.3B (2025-02-20) | Private |
| LangChain | F | 2023 | MIT; closed LangSmith (3→2) | Open core | $3B (2026-11-13) | Private |
| LlamaIndex | F | 2023 | MIT; closed LlamaParse (3→2) | Open core | n/d | Private |
| Pydantic | C | 2023 | MIT; closed Logfire (3→2) | Open core | n/d | Private |
| Chroma | F | 2022 | Apache-2.0 (3→3) | Hosted | n/d | Replit, pending |
| Ollama | F | 2021 | MIT (3→3) | Hosted | n/d | Private |
| ggml.ai / llama.cpp | C | 2023 | MIT (3→3) | None found | n/d | Hugging Face (2026-02) |
| Unsloth | F | 2023 | Apache-2.0 + Pro, AGPL UI (2→2) | Open core | n/d | Private |
| Nous Research | C | 2023 | Llama-licence weights → MIT/Apache (1→2) | Open core | $1.5B\* (2026-10-07) | Private |
| Replicate | F | 2019 | Apache-2.0 Cog (2→2) | API | n/d | Cloudflare (2025-11) |
| Weights & Biases | F | 2017 | MIT SDK only (1→1) | SaaS | ~$1.7B acq. (2025-03) | CoreWeave (2025-05) |
| Modular | F | 2022 | Closed → Apache Mojo, source-available MAX (0→2) | Open core | $3.9B acq.\* (2026-07) | Qualcomm (2026-07) |
| Qdrant (DE) | F | 2021 | Apache-2.0 (3→3) | Hosted | n/d | Private |
| Weaviate (NL) | F | 2019 | BSD-3 + closed enterprise code (3→2) | Open core | n/d | Private |

## Observations

1. **Permissive licences dominate, and no one relicensed to SSPL or BSL.** Six of the seven licensing or governance events were openings: Ray and vLLM moving to the PyTorch Foundation, three steps at Modular, and one at Chroma. Weaviate's partial 2026 carve-out is the only closing. Mean openness held at 2.29. Group A's database firms logged 18 closings in 21 events and fell from 2.72 to 1.67.

2. **Closing happens by adding products.** LangChain, LlamaIndex and Pydantic kept their frameworks under MIT and built closed services beside them: LangSmith, LlamaParse and Logfire.

3. **Hosting, not licences, is the business.** Every firm with a known model sells a proprietary hosted or enterprise layer. Revenue lags valuation: LangChain's annual recurring revenue (ARR) was reportedly $12–16M (Jul 2025), before its $3B round. Lightning projected $10–20M ARR for 2025 and passed $500M only after merging with a GPU owner.

4. **Compute and chip firms are the buyers.** Seven exits or agreed deals came in 2025–2026, none of them IPOs. Five buyers sell compute or chips: CoreWeave, Nscale, Voltage Park, Qualcomm and Cloudflare. Hugging Face, which took ggml, is itself being bought by NVIDIA (group B). Step-ups were modest: about $1.7B for W&B after $1.25B (2023), and $1.65B for Anyscale after $1.38B (2022).

5. **Foundation first, money after.** vLLM (May 2025) and Ray (Oct 2025) joined the PyTorch Foundation before Inferact raised $150M (Jan 2026) and before Anyscale's sale (Jul 2026). In the database wave, neutral homes appeared only as forks after relicensing (OpenSearch, OpenTofu, Valkey).

6. **Berkeley again.** Ray and vLLM are Berkeley projects co-created by Ion Stoica, in the Spark/Databricks lineage. They are the only projects here under neutral foundation governance.
