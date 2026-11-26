# Classifying the GitHub organizations that own popular repositories

Part of a pre-registered study (issue #380): who owns the most-starred open-source repositories, and (later, in a
separate step) what those owners earn and raise. Your job is ONLY the first step: identify and classify each owner.

**Do not look up, record or use any financial outcome** (funding, valuation, revenue, IPO, acquisition price,
shutdown) when deciding a class. The class must not depend on whether the owner succeeded. You may note an
acquisition or shutdown in `status_hint` only if you happen to know it, but never let it change the class.

## Input

A CSV with one row per GitHub organization account: `owner` (the GitHub login), rank by stars, frames (A = among
the 2,000 most-starred repos on GitHub; B = among the most-starred repos in science topics), number of repos,
total stars, the account's name, website (`blog`), e-mail domain, location, creation year, Wikidata item if one
lists this GitHub username, description, and up to three top repositories with stars, language and description.

## Classes (exactly one per owner)

| cls | Rule |
| --- | --- |
| `core` | A company whose main paid product is the project itself in another form: a hosted/cloud service of it, an open-core or enterprise edition, paid licences or support for it, or hardware it sells. Examples: Elastic (`elastic`), Grafana Labs, Supabase, HashiCorp (even though IBM now owns it), Docker Inc. (`docker`, `moby`), Vercel (Next.js; hosting platform marketed to its users), Hugging Face (Hub), Ollama, n8n, LangChain, Opentrons (sells the robots), Prusa Research, Ultralytics (paid licences), DeepSeek (sells API access to its open-weight models) |
| `complement` | A company that publishes the project but earns most of its revenue from other products. Examples: Microsoft, Google/Alphabet (`google`, `tensorflow`, `angular`, `flutter`, `golang`, `google-research`, `puppeteer`), Meta (`facebookresearch`, `meta-llama`), Alibaba (`alibaba`, `ant-design`, `agentscope-ai`), Baidu (`PaddlePaddle`), ByteDance, Tencent, Airbnb, X/Twitter, Cloudflare, OpenAI, Anthropic, xAI, Red Hat/IBM for `ansible`, Broadcom for `spring-projects`, Shopify for `remix-run`, Genymobile for `scrcpy` (sells Genymotion), a consultancy publishing a side tool, a company whose open repo is a list or SDK for a closed product |
| `nonprofit` | A foundation or other nonprofit that owns or stewards the project: Apache Software Foundation, Linux Foundation and its sub-foundations (CNCF for `kubernetes`, OpenJS for `nodejs` and `electron`, PyTorch Foundation for `pytorch` and `vllm-project`, Agentic AI Foundation for `modelcontextprotocol`), Python Software Foundation (`python`, `psf`), Django Software Foundation, Rust Foundation (`rust-lang`), Mozilla, freeCodeCamp, Free Ebook Foundation, Godot Foundation, Open Home Foundation (`home-assistant`), NumFOCUS-sponsored projects ONLY if NumFOCUS or another foundation is the legal home rather than a mere fiscal sponsor (otherwise `community`) |
| `academic` | A university, a university lab or group, or an academic research institute (including state-funded research institutes such as Shanghai AI Laboratory, Max Planck, EMBL, Broad Institute, HHMI Janelia, Allen Institute). Examples: `HKUDS` (HKU), `CompVis` (LMU Munich) |
| `government` | A government agency, national laboratory or government-owned body: `NationalSecurityAgency`, NASA, NIST, NIH/NCBI, DOE national labs (LLNL, ORNL, NREL, Sandia, ...), CERN, UK GDS (`alphagov`) |
| `community` | A project with no owning legal entity, or one that only uses a fiscal host (Open Collective, Open Source Collective, Software Freedom Conservancy, NumFOCUS fiscal sponsorship, Commons Conservancy). Examples: `vuejs`, `twbs` (Bootstrap), `yt-dlp`, `ohmyzsh`, `neovim`, `Homebrew`, `bitcoin`, `TheAlgorithms`, `public-apis`, `d3`, `axios`, `obsproject`, `pallets`, `numpy`, `scipy`, `pandas-dev`, `matplotlib`, scientific-software collaborations without a single owning institution |
| `unknown` | Not identifiable from public sources after a reasonable check |

Tie-breakers:
- Classify the **organization account**, by who owns or controls it today. If a company bought the project's
  company, the class stays `core` and `parent` names the buyer (HashiCorp → `core`, parent IBM).
- Company vs. project org: if a GitHub org is the project's home and a company founded by the maintainers sells a
  hosted or enterprise version (e.g. `mermaid-js` → Mermaid Chart; `storybookjs` → Chromatic), use `core`, set
  `judgment=1` and name the company in `entity`.
- An AI lab that releases open weights and sells API access to those same models → `core` (judgment=1). An AI lab
  whose open repos are tools around closed models → `complement`.
- Academic spin-out companies are companies (`core` or `complement`), not `academic`.
- Crypto/blockchain: classify the developing company or foundation as usual, and set `crypto=1`.
- A one-person "org" that is clearly just an individual's projects → `community` (note "individual's org").
- Content repositories (lists, books, courses) are still classified by owner.
- If you're unsure between two classes, pick the more likely one and set `judgment=1`. Use `unknown` only if you
  can't identify the owner at all.

## How to check

Use your own knowledge first. For any owner you're not sure about (new 2025–26 projects especially), check the
organization's website (the `blog` field) or the repository README with WebFetch (e.g.
`https://github.com/<owner>/<repo>` or the website's about/pricing page) to see whether a company sells something.
A pricing page, "Enterprise", "Cloud" or "Sign up" with paid tiers is evidence of `core` or `complement`. Spend at
most a couple of fetches per owner. Do not use web search for financial information.

## Output

Write a CSV (with a header) to the path given in your task, one row per input owner, in input order, no rows
skipped, with these columns:

`owner,cls,entity,parent,country,basis,judgment,crypto,status_hint,source_url`

- `entity`: the owning organization's common or legal name (e.g. "Grafana Labs", "University of Hong Kong",
  "Python Software Foundation"). For `community`, the project name.
- `parent`: ultimate parent company or institution if different (e.g. "Alphabet", "IBM", "Linux Foundation").
- `country`: ISO-2 country code of the owning entity's headquarters if known (US, CN, DE, ...), else blank.
- `basis`: at most 15 words: what the class rests on (e.g. "sells Grafana Cloud and Enterprise", "HKU data science lab").
- `judgment`: 1 if a judgment call, else 0. `crypto`: 1 or 0.
- `status_hint`: optional, e.g. "acquired by IBM 2025", "subsidiary", "archived".
- `source_url`: the page you checked, or blank if from knowledge.

Quote fields containing commas. When done, reply with: the number of rows written, counts by class, and a list of
the owners you marked `unknown` or `judgment=1` with a few words on why.
