# Group C (Big Tech and AI labs): summary

Sources: WebSearch for Meta, Alphabet, Microsoft (32 searches); WebFetch for the rest (105 reads).
Openness covers AI and developer platforms, 0–4 (`../SCHEMA.md`).

| Name | Openness | Origin | Founded | Latest value (date) | Key open/closed moves |
| --- | --- | --- | --- | --- | --- |
| [Meta](meta.json) | 3→1 | startup | 2004 | $1.43T (2026-11-20) | PyTorch to LF '22; Llama licences; closed Muse Spark '26 |
| [Alphabet](alphabet-google.json) | 3→2 | startup | 1998 | $3.26T (2026-11-20) | Kubernetes to CNCF; Gemma Apache '26; AOSP tightened |
| [Microsoft](microsoft.json) | 0→2 | startup | 1975 | $3.60T (2026-11-22) | .NET MIT '14; GitHub '18; Phi-4 MIT '25 |
| [Amazon](amazon-aws.json) | 1→2 | startup | 1994 | $2.76T (2026-11-23) | OpenSearch, Valkey forks to LF |
| [IBM](ibm.json) | 0→2 | corporate | 1911 | $220B (2026-11-23) | Bought Red Hat, HashiCorp, Confluent |
| [Oracle](oracle.json) | 0→1 | startup | 1977 | $354B (2026-11-23) | Closed OpenSolaris '10; forks followed |
| [NVIDIA](nvidia.json) | 0→1 | startup | 1993 | $3.99T (2026-11-23) | CUDA closed; Nemotron open |
| [Apple](apple.json) | 0→1 | startup | 1976 | $5.07T (2026-11-23) | Swift Apache '15; OpenELM non-OSI '24 |
| [OpenAI](openai.json) | 3→1 | nonprofit | 2015 | $852B private (2026-04) | GPT-2 withheld '19; gpt-oss Apache '25 |
| [Anthropic](anthropic.json) | 0→1 | startup | 2021 | $1.17T (2026-11-23) | Claude closed; MCP to LF '25; IPO '26 |
| [DeepMind science](google-deepmind-science.json) | 4→2 | startup | 2010 | in Alphabet | AlphaFold 2 open '21; AF3 restricted '24 |
| [Mistral](mistral-ai.json) | 3→2 | startup | 2023 | €21–25B (2026-09) | Apache, partly closed '24, reopened '25 |
| [DeepSeek](deepseek.json) | 1→3 | corporate | 2023 | $70B pre-money (2026-10) | MIT from R1 '25 |
| [xAI](xai.json) | 1→1 | startup | 2023 | $250B (2026-02) | Grok-1 Apache '24; restrictive Grok 2 '25 |
| [Ai2](ai2.json) | 3→4 | nonprofit | 2014 | n/a | Fully open OLMo '24; Olmo 3 '25 |
| [EleutherAI](eleutherai.json) | 4→4 | community | 2020 | n/a | The Pile '20; Common Pile '25 |
| [Stability AI](stability-ai.json) | 1→1 | startup | 2019 | undisclosed | OpenRAIL '22; paid above $1M revenue |
| [Alibaba Qwen](alibaba-qwen.json) | 1→2 | startup | 1999 | $214B (2026-11-23) | Apache Qwen3 '25; Max closed |

## Observations

1. **Commoditize the complement.** Meta's ads pay for free PyTorch and Llama, Google gave away
   Android and Kubernetes, and NVIDIA opens models that run on its GPUs while CUDA stays closed.
2. **Open weights moved markets.** DeepSeek's MIT-licensed R1 preceded Nvidia losing ~$600B in a
   day (2025-01-27). OpenAI then released Apache-2.0 gpt-oss.
3. **Meta changed course.** Llama reached 1.2B downloads, but Meta's frontier model went closed
   (Muse Spark, April 2026). Qwen added a revenue cap to its largest open model.
4. **Mid-sized models converged on OSI licences** (Phi-4, Qwen3, Mistral 3, DeepSeek, Gemma 4).
5. **Closed labs open standards.** Anthropic gave MCP to a Linux Foundation fund; Claude
   stayed closed.
6. **Governance decides durability.** Projects held by foundations (Kubernetes, PyTorch, OpenSearch,
   Valkey, MCP) survived strategy shifts, while Llama and AOSP were tightened.
7. **AI for science.** The fully open AlphaFold 2 won a Nobel. The restricted AlphaFold 3 spawned
   open clones, with value moving to Isomorphic Labs. Ai2's fully open OLMo drew $152M from NSF
   and NVIDIA.
8. **Value comes from closed cores** (Apple, NVIDIA, Microsoft). Stability AI, built on open
   weights, nearly failed.
