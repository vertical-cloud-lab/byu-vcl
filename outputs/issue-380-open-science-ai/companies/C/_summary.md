# Group C (Big Tech and AI labs): partial summary

**Status: 3 of 18 organizations done (2026-11-23).** The shared WebSearch budget for this turn
(200 calls across all agents) ran out after 32 successful searches by this agent. Two more
queries were refused, so nothing was taken from memory to fill the gaps. The other 15 files
still need a follow-up run: Amazon/AWS, IBM, Oracle, NVIDIA, Apple, OpenAI, Anthropic, Google
DeepMind (science), Mistral AI, DeepSeek, xAI, Ai2, EleutherAI, Stability AI and Alibaba Qwen.

Openness is scored on each company's AI and developer-platform strategy (0–4 scale, `../SCHEMA.md`).

| Name | Openness initial→current | Origin | Founded | Latest value (date) | Key open/closed moves |
| --- | --- | --- | --- | --- | --- |
| [Meta](meta.json) | 3→1 | founder_startup | 2004 | $1.43T market cap (2026-11-20) | React BSD+Patents→MIT (2017); PyTorch to the Linux Foundation (2022); Llama 1 non-commercial (Feb 2023), then Llama 2–4 community licences (700M-MAU cap); React Foundation (2025–26); closed Muse Spark with a paid API (Apr 2026) |
| [Alphabet/Google](alphabet-google.json) | 3→2 | founder_startup (Stanford roots) | 1998 | $3.26T market cap (2026-11-20) | Kubernetes to the CNCF and TensorFlow under Apache-2.0 (2015); Gemma under custom terms (2024), then Gemma 4 under Apache-2.0 (Apr 2026); Gemini closed; AOSP developed in-house (2025) with source drops twice a year (2026); Android developer verification (announced Aug 2025) |
| [Microsoft](microsoft.json) | 0→2 | founder_startup | 1975 | $3.60T market cap (2026-11-22) | "Linux is a cancer" (2001); .NET Core under MIT (2014); VS Code under MIT (2015); GitHub bought for $7.5B (2018); Phi-4 weights under MIT (Jan 2025); Copilot Chat extension under MIT (Jun 2025) |

## Observations (from the three completed files)

1. **Commoditize your complement.** Meta earns from ads, so giving away PyTorch, React and
   Llama weights cost it little and undercut rivals that sell model access. Google made the
   mobile OS (Android) and the cloud orchestration layer (Kubernetes) free, which widened the
   market for its paid services. Microsoft opened its developer stack once its revenue moved to
   renting cloud capacity; Azure passed $100B in FY2026.
2. **Governance decides what survives a change of strategy.** Projects handed to foundations
   stayed open through every strategy shift: Kubernetes (CNCF, 2015), .NET (.NET Foundation,
   2014), PyTorch (Linux Foundation, 2022) and React (React Foundation, 2025–26). The lines each
   vendor still controls are the ones that tightened: Meta's frontier models and Android's
   development process.
3. **Open weights were a tactic.** Llama reached 1B downloads by March 2025 and 1.2B by April
   2025. Even so, Meta put its frontier model behind a paid API in April 2026, after reports
   that DeepSeek R1 had built on Llama's architecture fed doubts inside Meta Superintelligence
   Labs.
4. **Small models are converging on OSI licences while frontier models stay closed.** Phi-4
   moved from a research licence to MIT (Jan 2025) and Gemma from custom terms to Apache-2.0
   (Apr 2026). Gemini, Muse Spark and the OpenAI models behind Copilot remain closed.
5. **A licence is not the same as openness.** Android is still Apache-2.0, but in-house
   development, source drops twice a year and mandatory developer verification for sideloaded
   apps (enforced from Sept 2026 in four countries, globally in 2027) hand control back to
   Google.
6. **Value comes from closed services.** All three companies are worth $1.4–3.6T, and their
   profits come from proprietary ads, search and cloud. Openness sits in the layers that do not
   earn money directly but feed users and developers into the layers that do.

Observations on DeepSeek, MCP and AlphaFold will follow with those files.
