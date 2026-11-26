# Who funds open-source-minded ventures? (issue #380, round 2, part 3)

Sterling asked for *"a list of investors, firms, philanthropists, and other VC and VC-like sources that have been
involved in funding a venture that falls into the more open-source minded of startups. Be thorough and manual."*
This folder is that list.

- **[`FUNDER_LIST.md`](FUNDER_LIST.md) lists every funder found**, grouped by type, with each venture it backed
  linked to a page that names it.
- **This file** summarises the list, says what it shows and how far to trust it.
- **[`data/`](data/) holds the tables**:
  - every round (`deals.csv`)
  - every funder–venture pair (`investor_links.csv`)
  - every funder (`investors.csv`)
  - every program-level funder (`programs.csv`)

The scope and counting rules were committed before any funding data was gathered ([`PROTOCOL.md`](PROTOCOL.md),
`448c8c2`).

## Bottom line

- **The list is long and flat.** Across the 598 hand-researched ventures in groups U1–U3,
  394 disclosed outside funding.
  - Public sources name 1,447 distinct funders in 964 funding events.
  - 1,089 of those funders appear in only one venture.
  - Only 80 backed five or more, and the ten most frequent account for
    10% of all funder–venture links.
  - There is no small club that funds open source. There is a long tail with a recognisable head.
- **The head is mostly generalist venture firms, an accelerator and chip and cloud companies:**
  - Y Combinator, by count.
  - Accel, Sequoia, Andreessen Horowitz, NEA, Index, Benchmark, Lightspeed and Insight.
  - NVIDIA and Intel Capital, then Alphabet's and Microsoft's investment arms and Salesforce Ventures.
  - The firms that lead open-source rounds most often are Andreessen Horowitz, Accel, Insight, NEA, Sequoia,
    Index and Benchmark.
- **Funds built around open source exist but are small in this count.**
  - OSS Capital, Runa Capital, Open Core Ventures, Heavybit, Uncorrelated Ventures, Boldstart and Crane each back a
    handful of the ventures here.
  - 26 funders in the data state an open-source thesis in their own words. Most of them are large generalists
    (Andreessen Horowitz, Accel, Sequoia, Index, NEA, Redpoint).
- **People are a large share of the funders.** Many of the most frequent angels founded or led open-source
  companies themselves, and now back the next ones:
  - Guillermo Rauch (Vercel), Clem Delangue (Hugging Face) and David Cramer (Sentry)
  - Tom Preston-Werner and Nat Friedman (GitHub), Paul Copplestone (Supabase) and Tristan Handy (dbt Labs)
- **Open hardware, open science and lab ventures draw a different mix**: crowdfunding backers, strategic
  corporates, a few hardware-minded venture firms, grants and, for DeSci, crypto funds.
  - Strategic corporates: Bosch, Renesas, Arm, Qualcomm, Sony, Intel and NVIDIA.
  - Hardware-minded venture firms: True Ventures, Foundry Group, Spark Capital, Khosla, Eclipse and Lux.
  - Grants: SBIR, NSF, NIH, Shuttleworth, CZI and Sloan.
  - Only 11 funders backed three or more of the 97 ventures in this group.
- **Philanthropy and government fund open source mostly at the program level**, and mostly not through companies.
  - Programs: CZI, Sloan, Moore and Schmidt Sciences; DOE's Exascale Computing Project; NSF's POSE and CSSI;
    Germany's Sovereign Tech Agency; the EU's NGI grants through NLnet.
  - Recipients are mostly projects, universities and nonprofits.
- **Nothing here says these funders made money on open source, or that they would fund a given venture.** The list
  records who put money in, as disclosed. Disclosure favours large rounds and survivors.

![Who has backed the most open-source-minded ventures](figures/top_funders.png)

## The funders that backed the most open-source-minded ventures (U1–U3)

One count per venture, however many rounds; "led" counts ventures where the funder led at least one round.
Examples list led ventures first. Full list: [`FUNDER_LIST.md`](FUNDER_LIST.md).

| Funder | Type | Ventures backed | Led a round in | Ventures (led first) |
| --- | --- | --- | --- | --- |
| Y Combinator | accelerator / studio | 59 | 3 | Mattermost, PostHog Inc., SigNoz, Activepieces, Airbyte, Anomaly, Apify, BerriAI … |
| Accel | venture firm | 27 | 15 | Airbyte, Astral, Cloudera, ForgeRock, Heptio, Laravel, Polars B.V., RadixArk … |
| Sequoia Capital | venture firm | 25 | 13 | Deno Land Inc., Docker Inc., FastAPI Labs, GitHub, LangChain, Observable, Inc., Odoo SA, Pydantic Services … |
| Andreessen Horowitz | venture firm | 24 | 12 | Anyscale, Astral, Black Forest Labs, Databricks, GitHub, Inferact, Isovalent, Linera … |
| Intel Capital | corporate / strategic | 22 | 5 | Lightbend, MariaDB, MinIO Inc., Mirantis, Truffle Security, AI21 Labs, Anyscale, Cloudera … |
| New Enterprise Associates | venture firm | 22 | 15 | Acquia, Anyscale, Databricks, Elastic N.V., Metabase, MuleSoft, NGINX, Pentaho … |
| NVIDIA (incl. NVentures) | corporate / strategic | 21 | 1 | AI21 Labs, Black Forest Labs, Cohere, Cumulus Networks, Databricks, EvolutionaryScale, Hugging Face, Lightning AI … |
| Benchmark | venture firm | 20 | 12 | Airbyte, Buoyant, ClickHouse, Cockroach Labs, Docker Inc., Hortonworks, Hyperic, LangChain … |
| Index Ventures | venture firm | 20 | 9 | Chai Discovery, ClickHouse, Dagster Labs, Gatsby, Kong Inc., Lightning AI, Strapi, Temporal Technologies … |
| Coatue | growth, crossover or PE | 17 | 7 | ClickHouse, Databricks, Kubecost, Nomic AI, SiFive, Stability AI, Supabase, Airbyte … |
| Insight Partners | growth, crossover or PE | 16 | 13 | Anaconda, Inc., Appsmith, Astronomer, Automattic, CrewAI, Databricks, Docker Inc., E2B … |
| Lightspeed Venture Partners | venture firm | 16 | 9 | Grafana Labs, Hasura, Inferact, Marqo, Mistral AI, Reflection AI, Serverless, Inc., Stability AI … |
| Kickstarter backers | crowdfunding | 15 | 0 | Augmented Instruments, Backyard Brains, Fonticons, Inc., George Robotics, Great Scott Gadgets, Luxonis, Mycroft AI, OpenBCI … |
| SV Angel | venture firm | 15 | 0 | Airbyte, Anomaly, Buoyant, Civilized Discourse Construction Kit, Expo, Hugging Face, Lightning AI, Mastra … |
| General Catalyst | venture firm | 14 | 7 | Chai Discovery, Gitpod, Ionic, MinIO Inc., Mistral AI, Modular Inc., Together AI, Anaconda, Inc. … |
| Nexus Venture Partners | venture firm | 14 | 8 | Firecrawl, Hasura, MinIO Inc., Nrwl, OpenObserve, Orkes, TileDB, Inc., ToolJet … |
| Redpoint Ventures | venture firm | 14 | 5 | Couchbase, Mattermost, Solo.io, Tiger Data, Zed Industries, ClickHouse, Cockroach Labs, Coder Technologies … |
| CRV | venture firm | 13 | 8 | Gatsby, LanceDB, Meilisearch, ProjectDiscovery, Reflection AI, Strapi, Tailscale, Vercel … |
| GV | corporate / strategic | 13 | 6 | Buoyant, CoreOS, GitLab Inc., Vercel, Warp, deepset, Cockroach Labs, Determined AI … |
| Battery Ventures | venture firm | 12 | 3 | Code Ocean, InfluxData, Orkes, Bitwarden, Chai Discovery, ClickHouse, Cumulus Networks, Cypress.io … |
| Bessemer Venture Partners | venture firm | 12 | 6 | Appwrite, Auterion, Boltz PBC, Coiled, Cypress.io, Netdata Inc., Appsmith, ClickHouse … |
| Guillermo Rauch | person (angel) | 12 | 0 | Chroma, Comfy Org, Dub Technologies, Mastra, Meilisearch, Prisma Data, Inc., ProjectDiscovery, ResearchHub … |
| OSS Capital | venture firm | 12 | 5 | AppFlowy, OpenBB Inc., Plane, Remix Software, Tracel Inc., Appsmith, Cal.com, Inc., Dagster Labs … |
| Salesforce Ventures | corporate / strategic | 12 | 4 | Automattic, Black Forest Labs, MuleSoft, Together AI, Astronomer, Cohere, Databricks, Hugging Face … |
| Tiger Global | growth, crossover or PE | 12 | 7 | Appwrite, Cohere, OctoML, Prefect Technologies, Redis Ltd., Temporal Technologies, Tiger Data, Automattic … |
| Amplify Partners | venture firm | 11 | 3 | OctoML, Prisma Data, Inc., Temporal Technologies, Anyscale, Boltz PBC, Dagster Labs, LangChain, Outerbounds … |
| Sapphire Ventures | venture firm | 11 | 2 | InfluxData, Tetrate, Chai Discovery, Cypress.io, JFrog, Kaltura, Kong Inc., LangChain … |
| True Ventures | venture firm | 11 | 4 | 3D Robotics, Puppet, Solo.io, Vectorize, Inc., Automattic, HashiCorp, Inventables, Iterative … |
| GGV Capital (US arm now Notable Capital) | venture firm | 10 | 5 | Browserbase, HashiCorp, LocalStack, PingCAP, Vercel, Coder Technologies, Jina AI, Kong Inc. … |
| GIC | state or sovereign investor | 10 | 3 | Grafana Labs, Supabase, Vercel, Anaconda, Inc., ClickHouse, Databricks, LangChain, PingCAP … |
| Goldman Sachs | growth, crossover or PE | 10 | 5 | GitLab Inc., Harness, NGINX, Redis Ltd., SugarCRM, Acquia, Databricks, Kong Inc. … |
| Samsung | corporate / strategic | 10 | 3 | AI21 Labs, Mistral AI, Tenstorrent, ClearML, Daytona Platforms, H Company, Liquid AI, MosaicML … |
| Greylock Partners | venture firm | 9 | 4 | Docker Inc., Lightbend, LlamaIndex, Zend Technologies, Anomaly, Civilized Discourse Construction Kit, Cloudera, Modular Inc. … |
| Lux Capital | venture firm | 9 | 7 | Authorea, EvolutionaryScale, Hugging Face, Reflex, Sakana AI, Together AI, tldraw Inc., DeepSeek … |
| David Cramer | person (angel) | 8 | 0 | Earendil Inc., FastAPI Labs, Mastra, Pydantic Services, Strapi, Supermemory, Vercel, VoidZero |
| Dell Technologies Capital | corporate / strategic | 8 | 3 | MinIO Inc., OpenObserve, Tetrate, JFrog, Prime Intellect, Redis Ltd., SpringSource / Pivotal Software, Treeverse |
| Khosla Ventures | venture firm | 8 | 6 | ClickHouse, GitLab Inc., Onyx, Opentrons Labworks, Oven, Sakana AI, Mesosphere, Neon |
| Kleiner Perkins | venture firm | 8 | 4 | Oven, Prisma Data, Inc., Puppet, Together AI, Browserbase, Chai Discovery, CoreOS, XenSource |
| M12 | corporate / strategic | 8 | 2 | Code Ocean, Neon, Isovalent, Mermaid Chart, Nous Research, Pachyderm, ToolJet, Unstructured |
| Tom Preston-Werner | person (angel) | 8 | 1 | Gitpod, AppFlowy, Liquid AI, Nrwl, SigNoz, Spacedrive Technology, Zed Industries, tldraw Inc. |

## By kind of funder

![Who funds which kind of open venture](figures/funder_mix.png)

| Universe | Investor-venture links | venture firm | corporate / strategic | person (angel) | accelerator / studio | growth, crossover or PE | state or sovereign investor | philanthropy | government grant | crowdfunding | crypto fund or DAO | bank or lender | other | unclassified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | 1427 | 51% | 8% | 24% | 5% | 5% | 1% | 0% | 1% | 0% | 2% | 0% | 0% | 3% |
| U2 | 347 | 50% | 14% | 9% | 2% | 5% | 3% | 1% | 4% | 6% | 3% | 0% |  | 4% |
| U3 | 833 | 54% | 18% | 9% | 1% | 11% | 3% |  | 1% |  | 1% | 0% |  | 3% |
| U4 | 914 | 40% | 4% | 22% | 27% | 1% | 0% | 1% | 0% | 0% | 1% |  | 0% | 4% |

### Investors that say they invest in open source

Quoted from the firm's own page or from a public interview. The count is ventures in this data, U1–U4.

| Investor | In their words | Ventures here (U1–U4) |
| --- | --- | --- |
| Accel | “Open source is upending major enterprise and IT categories.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-1-of-2)) | 33 |
| Andreessen Horowitz | “a thriving open source ecosystem is essential to building this future.” ([source](https://a16z.com/supporting-the-open-source-ai-community/)) | 33 |
| Sequoia Capital | “the developer is now at the center of decision-making for the adoption of any product.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-1-of-2)) | 27 |
| New Enterprise Associates | “Open source/open core have become the essential model to get distribution and adoption quickly.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-2-of-2/)) | 23 |
| Index Ventures | “At Index, we believe in the power of the open source movement. Adopting its spirit, this is a forum for sharing learnings and experiences” ([source](https://www.indexventures.com/opensource)) | 22 |
| Insight Partners | “Many of these ScaleUps are built around open source or have a major open-source component.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-2-of-2/)) | 18 |
| CRV | “I still think it's an under-heated market.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-1-of-2)) | 17 |
| Lightspeed Venture Partners | “most open-source startups need to really be hyper-focused on adoption in the beginning.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-2-of-2/)) | 17 |
| Redpoint Ventures | “We believe in the rise of open source at the application tier.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-1-of-2)) | 16 |
| Bessemer Venture Partners | “this is one of the most essential ingredients for building a successful open-source project and commercial entity.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-2-of-2/)) | 15 |
| OSS Capital | “Open source is eating software faster than software is eating the world.” ([source](https://oss.capital)) | 13 |
| Lux Capital | “establish open-source as the default way to incorporate AI.” ([source](https://www.luxcapital.com/companies)) | 11 |
| SignalFire | “open source being preferred and in many cases mandated from the top.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-1-of-2)) | 11 |
| M12 | “there is good appetite for the acquirers as well as the public markets, depending on the value proposition” ([source](https://www.linuxfoundation.org/blog/blog/perspectives-open-source-startups)) | 11 |
| Sapphire Ventures | “Open source is a GTM strategy for DevOps tools and infrastructure software.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-2-of-2/)) | 11 |
| Uncorrelated Ventures | “the phenomenon of innovative companies moving away from open source will weaken that brand.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-2-of-2/)) | 10 |
| Dell Technologies Capital | “The valley of death is between marketshare and money share.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-1-of-2)) | 8 |
| Madrona Venture Group | “open source as table stakes for dev tools.” ([source](https://techcrunch.com/2020/02/05/where-top-vcs-are-investing-in-open-source-and-dev-tools-part-1-of-2)) | 7 |
| Databricks Ventures | “Projects and entrepreneurs that share Databricks' commitment to building on open platforms” ([source](https://www.databricks.com/databricks-ventures)) | 6 |
| Runa Capital | “considers an active developer community instrumental for software businesses” ([source](https://runacap.com/ross-index/)) | 5 |
| Boldstart Ventures | “When your open-source project is popular with a large audience of developers, that's great.” ([source](https://www.boldstart.vc/portfolio)) | 4 |
| Mozilla Ventures | “Mozilla Ventures is about fueling companies and products that put people before profits.” ([source](https://blog.mozilla.org/en/mozilla/mozilla-launches-first-of-its-kind-venture-fund-to-fuel-responsible-tech-companies-products/)) | 4 |
| Open Core Ventures | “We turn open source projects into durable, venture-scale opportunities.” ([source](https://opencoreventures.com)) | 3 |
| Zetta Venture Partners | “The beauty of open source from an investor's perspective is distribution, not innovation” ([source](https://www.linuxfoundation.org/blog/blog/perspectives-open-source-startups)) | 2 |
| Serena | “The best performing startups in infrastructure are not hiding their source code—they're sharing it.” ([source](https://www.linuxfoundation.org/press/linux-foundation-cossa-and-serena-report-shows-venture-investment-in-open-source-outperforms-proprietary-counterparts-and-benefits-communities)) | 1 |
| Zerodha | “A significant portion of our success and growth is owed to FOSS.” ([source](https://techcrunch.com/2024/11/10/open-source-projects-draw-equity-free-funding-from-corporates-startups-and-even-vcs)) | 1 |

### Corporate and strategic investors

Investment arms rolled up to their parent:

| Group | Arms found | Ventures | Examples |
| --- | --- | --- | --- |
| Alphabet | CapitalG, GV, Google, Gradient Ventures | 34 | AI21 Labs, Buoyant, CTGT, Charm, Cockroach Labs, CoreOS, Databricks, Determined AI, GitLab Inc., Grafana Labs |
| Intel | Intel Capital | 23 | AI21 Labs, Anyscale, Cloudera, CollabNet, Hugging Face, JBoss, Kaltura, Lightbend, MariaDB, MinIO Inc. |
| NVIDIA | NVIDIA (incl. NVentures) | 22 | AI21 Labs, Black Forest Labs, Cohere, Cumulus Networks, Databricks, EvolutionaryScale, Hugging Face, Lightning AI, MindsDB, Mistral AI |
| Microsoft | GitHub, M12, Microsoft | 17 | Code Ocean, Databricks, Embedchain, Isovalent, Ivy, Mem0, Mermaid Chart, Mesosphere, Neon, Nous Research |
| Samsung | Samsung | 16 | AI21 Labs, Activeloop, ClearML, Daytona Platforms, Enso, H Company, Ivy, Liquid AI, Mistral AI, MosaicML |
| Salesforce | Salesforce Ventures | 15 | Astronomer, Automattic, Black Forest Labs, Cohere, Databricks, Flotype, Hugging Face, LiveKit, Mistral AI, MuleSoft |
| Goldman Sachs | Goldman Sachs | 10 | Acquia, Databricks, GitLab Inc., Harness, Kong Inc., Mirantis, NGINX, Redis Ltd., SugarCRM, Temporal Technologies |
| Dell | Dell Technologies Capital, VMware | 9 | JFrog, MinIO Inc., OpenObserve, Prime Intellect, Puppet, Redis Ltd., SpringSource / Pivotal Software, Tetrate, Treeverse |
| Alibaba | Alibaba, Ant Group | 8 | 01.AI, Anyscale, Baichuan Intelligence, MariaDB, MiniMax, Moonshot AI, Sealos, Z.ai |
| Amazon | Amazon | 6 | Acquia, Databricks, EvolutionaryScale, H Company, Hugging Face, Mentra |
| Tencent | Tencent | 6 | Baichuan Intelligence, DeepSeek, MiniMax, Moonshot AI, StepFun, Z.ai |
| Saudi Aramco | Aramco Ventures (incl. Prosperity7) | 5 | Cohere, Rescale, SiFive, Together AI, Zilliz |

Individually:

| Funder | Type | Ventures backed | Led a round in | Ventures (led first) |
| --- | --- | --- | --- | --- |
| Intel Capital | corporate / strategic | 23 | 6 | Lightbend, MariaDB, MinIO Inc., Mirantis, TrueFoundry, Truffle Security, AI21 Labs, Anyscale … |
| NVIDIA (incl. NVentures) | corporate / strategic | 22 | 1 | AI21 Labs, Black Forest Labs, Cohere, Cumulus Networks, Databricks, EvolutionaryScale, Hugging Face, Lightning AI … |
| Samsung | corporate / strategic | 16 | 3 | AI21 Labs, Mistral AI, Tenstorrent, Activeloop, ClearML, Daytona Platforms, Enso, H Company … |
| GV | corporate / strategic | 15 | 8 | Buoyant, CoreOS, GitLab Inc., Roboflow, Vercel, Warp, deepset, sync. … |
| Salesforce Ventures | corporate / strategic | 15 | 4 | Automattic, Black Forest Labs, MuleSoft, Together AI, Astronomer, Cohere, Databricks, Flotype … |
| Gradient Ventures | corporate / strategic | 11 | 6 | Charm, Infisical, LastMile AI, Mage, Orchest, Payload, CTGT, Mastra … |
| M12 | corporate / strategic | 11 | 3 | Code Ocean, Neon, Webiny, Isovalent, Ivy, Mermaid Chart, Nous Research, Pachyderm … |
| Dell Technologies Capital | corporate / strategic | 8 | 3 | MinIO Inc., OpenObserve, Tetrate, JFrog, Prime Intellect, Redis Ltd., SpringSource / Pivotal Software, Treeverse |
| Alibaba | corporate / strategic | 7 | 5 | 01.AI, Baichuan Intelligence, MariaDB, MiniMax, Moonshot AI, Sealos, Z.ai |
| Cisco Investments | corporate / strategic | 7 | 1 | Puppet, Cohere, Isovalent, LangChain, Lightning AI, Mistral AI, MuleSoft |
| Amazon | corporate / strategic | 6 | 0 | Acquia, Databricks, EvolutionaryScale, H Company, Hugging Face, Mentra |
| Databricks Ventures | corporate / strategic | 6 | 0 | LanceDB, LangChain, Neon, Pynecone, RadixArk, Reflex |
| Red Hat | corporate / strategic | 6 | 1 | Jaspersoft, CoreOS, Gluster, Mirantis, MongoDB Inc., MySQL AB |
| Tencent | corporate / strategic | 6 | 2 | Baichuan Intelligence, Moonshot AI, DeepSeek, MiniMax, StepFun, Z.ai |
| Aramco Ventures (incl. Prosperity7) | corporate / strategic | 5 | 2 | Together AI, Zilliz, Cohere, Rescale, SiFive |
| Qualcomm Ventures | corporate / strategic | 5 | 2 | 3D Robotics, Particle, Daytona Platforms, Hugging Face, SiFive |
| SAP Ventures | corporate / strategic | 5 | 1 | Jaspersoft, Alfresco Software, Mirantis, MySQL AB, Zend Technologies |
| Automattic | corporate / strategic | 4 | 0 | Deno Land Inc., Liquid AI, Riot IM, Twenty |
| CapitalG | corporate / strategic | 4 | 2 | LangChain, Odoo SA, Databricks, Grafana Labs |
| GitHub | corporate / strategic | 4 | 0 | Embedchain, Mem0, ToolJet, formbricks |
| Google | corporate / strategic | 4 | 2 | AI21 Labs, Isovalent, Hugging Face, Sakana AI |
| Mozilla Ventures | corporate / strategic | 4 | 0 | Adap, Deno Land Inc., Flower, Probabl |
| AMD | corporate / strategic | 3 | 1 | Liquid AI, Hugging Face, RadixArk |
| Digital Science | corporate / strategic | 3 | 0 | Authorea, Figshare, Overleaf |
| IBM | corporate / strategic | 3 | 1 | Lightbend, Hugging Face, Mistral AI |

### Accelerators

- **Y Combinator** is the largest single source of early money for open-source startups in this data.
  - YC's own directory lists **183 companies tagged open source**, and **289 tagged or described as open source**
    ([`data/yc_open_source.csv`](data/yc_open_source.csv), from the yc-oss mirror of the directory, 2026-11-25).
  - Most of them are from 2020 on.
- **Other accelerators** appear far less often: HAX/SOSV for hardware (Opentrons, Particle, Crowd Supply), Neo,
  Antler, 500 Global, AI Grant, South Park Commons and Techstars.
- **Open Core Ventures** is a studio that builds companies around existing open-source projects.

| Funder | Type | Ventures backed | Led a round in | Ventures (led first) |
| --- | --- | --- | --- | --- |
| Y Combinator | accelerator / studio | 297 | 4 | Imgix, Mattermost, PostHog Inc., SigNoz, /dev/fast, 0.security, 280 North, ARC Prize Foundation … |
| Neo | accelerator / studio | 4 | 1 | Bluesky, Dagster Labs, Mage, Warp |
| Open Core Ventures | accelerator / studio | 3 | 0 | Mermaid Chart, Phaser Studio Inc., Stirling PDF |
| SOSV | accelerator / studio | 3 | 0 | Crowd Supply, Opentrons Labworks, Particle |
| Techstars | accelerator / studio | 3 | 0 | Comet ML, Ionic, Qovery |
| 500 Global | accelerator / studio | 2 | 0 | Mycroft AI, Sakana AI |
| AI Grant | accelerator / studio | 2 | 0 | Reworkd, Rowan |
| Antler | accelerator / studio | 2 | 0 | NetBird, Nhost |
| Expa | accelerator / studio | 2 | 0 | Metabase, OpenReplay |
| South Park Commons | accelerator / studio | 2 | 0 | Deep Cogito, Expo |
| Alchemist Accelerator | accelerator / studio | 1 | 0 | Mat3ra |
| HF0 | accelerator / studio | 1 | 0 | Fish Audio |

### People (angels)

| Funder | Type | Ventures backed | Led a round in | Ventures (led first) |
| --- | --- | --- | --- | --- |
| Guillermo Rauch | person (angel) | 18 | 0 | Chroma, Comfy Org, ComfyUI, Dub Technologies, LastMile AI, LiveKit, Mastra, Meilisearch … |
| Tom Preston-Werner | person (angel) | 10 | 1 | Gitpod, AppFlowy, Liquid AI, Nhost, Nrwl, OpenPipe, SigNoz, Spacedrive Technology … |
| Clem Delangue | person (angel) | 9 | 0 | Adap, FastAPI Labs, Flower, Kestra Technologies, Letta, NanoCo, Prime Intellect, Together AI … |
| Nat Friedman | person (angel) | 9 | 2 | EvolutionaryScale, Logseq Inc., Chroma, Dagger, Daily, Deno Land Inc., Strapi, Vercel … |
| Paul Copplestone | person (angel) | 9 | 0 | Embedchain, Infracost, Mem0, Pynecone, Reflex, Resend, SigNoz, Trigger.dev … |
| Paul Graham | person (angel) | 9 | 0 | Browser Use, Mastra, Mentra, Paradev, Rescale, Reworkd, Sim, Tinfoil … |
| David Cramer | person (angel) | 8 | 0 | Earendil Inc., FastAPI Labs, Mastra, Pydantic Services, Strapi, Supermemory, Vercel, VoidZero |
| Balaji Srinivasan | person (angel) | 6 | 0 | Dub Technologies, LabDAO, Mastra, Molecule, Nous Research, VitaDAO |
| Nicolas Dessaigne | person (angel) | 6 | 0 | Kestra Technologies, Medusa, Paradev, Prisma Data, Inc., Strapi, ToolJet |
| Olivier Pomel | person (angel) | 6 | 0 | Daytona Platforms, Embedchain, Fig, Hugging Face, Kestra Technologies, Mem0 |
| Amjad Masad | person (angel) | 5 | 0 | Chroma, LiveKit, Mastra, ResearchHub, Roboflow |
| Bob Young | person (angel) | 5 | 0 | AppFlowy, Liquid AI, NocoDB, OpenBB Inc., ResearchHub |
| Dharmesh Shah | person (angel) | 5 | 0 | Composio, CrewAI, Embedchain, Mem0, Twenty |
| Jeff Dean | person (angel) | 5 | 0 | Letta, LiveKit, Roboflow, Supermemory, marimo |
| Naval Ravikant | person (angel) | 5 | 0 | Chroma, OpenBB Inc., Spacedrive Technology, TrueFoundry, Vercel |
| Scott Belsky | person (angel) | 5 | 0 | Embedchain, Gatsby, Mage, Mem0, Roboflow |
| Tristan Handy | person (angel) | 5 | 0 | Evidence, Kestra Technologies, Letta, Mastra, Pydantic Services |
| Calvin French-Owen | person (angel) | 4 | 0 | Raycast, Resend, Roboflow, Shuttle |
| Dylan Field | person (angel) | 4 | 1 | Warp, Deno Land Inc., Resend, Zed Industries |
| Eric Schmidt | person (angel) | 4 | 0 | H Company, Reflection AI, Sendmail, Inc., Stability AI |
| Gokul Rajaram | person (angel) | 4 | 0 | Danswer, Onyx, Orkes, TrueFoundry |
| Jack Altman | person (angel) | 4 | 0 | Chroma, PostgresML, Pynecone, Reflex |
| Jason Warner | person (angel) | 4 | 0 | Fig, PostHog Inc., Raycast, Svix |
| Logan Kilpatrick | person (angel) | 4 | 0 | Cline Bot Inc., LiveKit, OpenPipe, Supermemory |
| Paul Buchheit | person (angel) | 4 | 0 | Pachyderm, PipelineDB, RethinkDB, Sim |
| Thomas Dohmke | person (angel) | 4 | 0 | Embedchain, Mem0, Raycast, Shuttle |
| Anthony Casalena | person (angel) | 3 | 0 | Medusa, Tailscale, Vercel |
| Anthony Goldbloom | person (angel) | 3 | 1 | marimo, Coiled, TrueFoundry |
| Aravind Srinivas | person (angel) | 3 | 0 | Daytona Platforms, LiveKit, Prime Intellect |
| Augusto Marietti | person (angel) | 3 | 0 | Gatsby, Prisma Data, Inc., Strapi |

### Growth, crossover and state investors

These join later and larger rounds, mostly of AI and infrastructure companies:

| Funder | Type | Ventures backed | Led a round in | Ventures (led first) |
| --- | --- | --- | --- | --- |
| Coatue | growth, crossover or PE | 18 | 8 | ClickHouse, Databricks, Kubecost, Nomic AI, Raycast, SiFive, Stability AI, Supabase … |
| Insight Partners | growth, crossover or PE | 18 | 15 | Anaconda, Inc., Apollo, Appsmith, Astronomer, Automattic, Bitrise, CrewAI, Databricks … |
| Tiger Global | growth, crossover or PE | 15 | 9 | Appwrite, CloudQuery, Cohere, Daily, OctoML, Prefect Technologies, Redis Ltd., Temporal Technologies … |
| GIC | state or sovereign investor | 10 | 3 | Grafana Labs, Supabase, Vercel, Anaconda, Inc., ClickHouse, Databricks, LangChain, PingCAP … |
| Goldman Sachs | growth, crossover or PE | 10 | 5 | GitLab Inc., Harness, NGINX, Redis Ltd., SugarCRM, Acquia, Databricks, Kong Inc. … |
| Altimeter Capital | growth, crossover or PE | 8 | 7 | Airbyte, ClickHouse, Cockroach Labs, LiveKit, Prisma Data, Inc., Solo.io, dbt Labs, GitLab Inc. |
| Bpifrance | state or sovereign investor | 8 | 0 | Genymobile, H Company, HARFANG 3D, Mistral AI, Pollen Robotics, Probabl, Strapi, Talend |
| Alkeon Capital | growth, crossover or PE | 4 | 0 | Databricks, GitLab Inc., Harness, Odoo SA |
| In-Q-Tel | state or sovereign investor | 4 | 0 | Cloudera, Docker Inc., MongoDB Inc., Sakana AI |
| J.P. Morgan | growth, crossover or PE | 4 | 0 | Astronomer, Cockroach Labs, Grafana Labs, Lightning AI |
| Shenzhen Capital Group | state or sovereign investor | 4 | 2 | Layabox, ModelBest, Baichuan Intelligence, Seeed Studio |
| SoftBank (Vision Fund) | growth, crossover or PE | 4 | 2 | Mapbox, Opentrons Labworks, MinIO Inc., Redis Ltd. |
| T. Rowe Price | growth, crossover or PE | 4 | 1 | Mesosphere, Cloudera, Databricks, SiFive |
| BOND | growth, crossover or PE | 3 | 1 | Sentry, ClickHouse, Cockroach Labs |
| Baillie Gifford | growth, crossover or PE | 3 | 0 | Chai Discovery, Databricks, Tenstorrent |
| Beijing AI Industry Investment Fund | state or sovereign investor | 3 | 0 | Baichuan Intelligence, Chaitin Tech, ModelBest |
| BlackRock | growth, crossover or PE | 3 | 0 | Databricks, Mistral AI, Odoo SA |
| DFJ Growth | growth, crossover or PE | 3 | 0 | LangChain, Mapbox, Modular Inc. |
| DST Global | growth, crossover or PE | 3 | 0 | Databricks, Mistral AI, Reflection AI |
| Eurazeo | growth, crossover or PE | 3 | 1 | Neo4j, H Company, Mistral AI |

### Who joins early rounds (pre-seed, seed, angel, accelerator, Series A; U1–U4)

| Funder | Type | Early rounds joined | Of which led | Ventures |
| --- | --- | --- | --- | --- |
| Y Combinator | accelerator / studio | 345 | 2 | /dev/fast, 0.security, 280 North, ARC Prize Foundation, Activeloop, Activepieces, Acyclic Labs, Adap |
| Accel | venture firm | 26 | 20 | Airbyte, Appsmith, Astral, Cloudera, Couchbase, ForgeRock, H Company, Heptio |
| Andreessen Horowitz | venture firm | 20 | 12 | Anyscale, Black Forest Labs, Boltz PBC, Civit, Databricks, Flotype, GitButler, Inferact |
| SV Angel | venture firm | 19 | 1 | Airbyte, Anomaly, Buoyant, Composio, Imgix, KERNEL, Mastra, Modular Inc. |
| Guillermo Rauch | person (angel) | 16 | 0 | Chroma, Comfy Org, ComfyUI, LastMile AI, LiveKit, Mastra, Meilisearch, Prisma Data, Inc. |
| Sequoia Capital | venture firm | 15 | 9 | Cockroach Labs, Dagster Labs, Deno Land Inc., FastAPI Labs, Infracost, LangChain, Mermaid Chart, Observable, Inc. |
| New Enterprise Associates | venture firm | 15 | 7 | Anyscale, Metabase, Neural Magic, Pentaho, Rocket.Chat, Sakana AI, Sentry, Tiger Data |
| CRV | venture firm | 14 | 9 | Gatsby, LanceDB, Lepton AI, LocalStack, Meilisearch, ProjectDiscovery, Reflection AI, RethinkDB |
| Nexus Venture Partners | venture firm | 14 | 9 | Browser Use, Deep Cogito, Firecrawl, Hasura, MinIO Inc., Nrwl, OpenObserve, Orkes |
| Lux Capital | venture firm | 14 | 8 | Airweave, DeepSeek, EvolutionaryScale, Hugging Face, Pynecone, Reflex, Sakana AI, Together AI |
| General Catalyst | venture firm | 13 | 6 | Anaconda, Inc., CTGT, Gitpod, Ionic, JuliaHub, Kilo Code, MinIO Inc., Modular Inc. |
| Amplify Partners | venture firm | 13 | 4 | Anyscale, Boltz PBC, Dagster Labs, OctoML, PostgresML, Prisma Data, Inc., ReadySet, Temporal Technologies |
| Benchmark | venture firm | 11 | 10 | Airbyte, Buoyant, ClickHouse, Cockroach Labs, Deep Cogito, Docker Inc., Hortonworks, Hyperic |
| Bessemer Venture Partners | venture firm | 11 | 8 | Appsmith, Appwrite, Boltz PBC, Coiled, Cypress.io, Fern, Herdr, Portainer.io |
| Intel Capital | corporate / strategic | 11 | 2 | Anyscale, MinIO Inc., Mirantis, Oxide Computer Company, Prime Intellect, Tetrate, TileDB, Inc., TrueFoundry |
| Seedcamp | venture firm | 10 | 1 | Appwrite, Liveblocks, Medusa, Meilisearch, Orchest, QuestDB |
| Mango Capital | venture firm | 10 | 0 | CloudQuery, Gatsby, Infracost, Jina AI, Meilisearch, ProjectDiscovery, Unstructured, Upstash |
| Lightspeed Venture Partners | venture firm | 9 | 6 | Composio, Grafana Labs, Inferact, Langfuse, Marqo, Mistral AI, ProjectDiscovery, Reflection AI |
| Gradient Ventures | corporate / strategic | 9 | 5 | CTGT, Infisical, LastMile AI, Mage, Mastra, Orchest, Payload, Streamlit |
| Index Ventures | venture firm | 9 | 5 | ClickHouse, Dagster Labs, Lightning AI, MinIO Inc., Mistral AI, Pentaho, ReadySet, Strapi |
| OSS Capital | venture firm | 9 | 5 | AppFlowy, Dagster Labs, Liquid AI, NocoDB, OpenBB Inc., Plane, Remix Software, formbricks |
| True Ventures | venture firm | 9 | 3 | 3D Robotics, Iterative, MakerBot Industries, Puppet, Sofar Ocean Technologies, Solo.io, Vectorize, Inc. |
| Tom Preston-Werner | person (angel) | 9 | 1 | AppFlowy, Gitpod, Liquid AI, Nhost, Nrwl, OpenPipe, SigNoz, Zed Industries |
| Clem Delangue | person (angel) | 9 | 0 | Adap, FastAPI Labs, Kestra Technologies, Letta, NanoCo, Prime Intellect, Together AI, marimo |
| Pioneer Fund | venture firm | 9 | 0 | Adap, Airweave, BerriAI, LiteLLM, Mastra, Netmaker, Paradev, Trigger.dev |
| Redpoint Ventures | venture firm | 8 | 6 | Couchbase, Dagger, LiveKit, Mattermost, Mistral AI, Solo.io, Zed Industries |
| SignalFire | venture firm | 8 | 4 | Budibase, CopilotKit, Invoke, Jitsu, Lago, ProjectDiscovery, SigNoz |
| Paul Copplestone | person (angel) | 8 | 0 | Embedchain, Infracost, Mem0, Pynecone, Resend, SigNoz, Trigger.dev, VoidZero |
| Madrona Venture Group | venture firm | 7 | 6 | All Hands AI, Heptio, OctoML, Pulumi, Tigera, Unstructured |
| Coatue | growth, crossover or PE | 7 | 4 | Dagster Labs, HTTPie, Kubecost, Nomic AI, Raycast, Supabase, Together AI |

## Open hardware, open science, lab and science-software ventures

Group U2 plus the U1 companies that part 2 found through GitHub's 22 science topics. These are the comparables for
DAL and the SDL kit. Every venture with its funders is in
[`data/tables/science_hardware_ventures.md`](data/tables/science_hardware_ventures.md).

| Funder | Type | Ventures backed | Led a round in | Ventures (led first) |
| --- | --- | --- | --- | --- |
| Kickstarter backers | crowdfunding | 14 | 0 | Augmented Instruments, Backyard Brains, George Robotics, Great Scott Gadgets, Luxonis, Mycroft AI, OpenBCI, OpenMV … |
| NVIDIA (incl. NVentures) | corporate / strategic | 5 | 0 | EvolutionaryScale, Hugging Face, Orbital Materials, Radical AI, SiFive |
| Intel Capital | corporate / strategic | 4 | 0 | Hugging Face, Oxide Computer Company, SiFive, TileDB, Inc. |
| Qualcomm Ventures | corporate / strategic | 4 | 2 | 3D Robotics, Particle, Hugging Face, SiFive |
| True Ventures | venture firm | 4 | 1 | 3D Robotics, Inventables, MakerBot Industries, Sofar Ocean Technologies |
| Balaji Srinivasan | person (angel) | 3 | 0 | LabDAO, Molecule, VitaDAO |
| Bessemer Venture Partners | venture firm | 3 | 3 | Auterion, Boltz PBC, Coiled |
| Bpifrance | state or sovereign investor | 3 | 0 | HARFANG 3D, Pollen Robotics, Probabl |
| Costanoa Ventures | venture firm | 3 | 1 | Coiled, Auterion, prefix.dev |
| Crowd Supply backers | crowdfunding | 3 | 0 | Lime Microsystems, MNT Research, Yunnan BinaryStars Technologies |
| Digital Science | corporate / strategic | 3 | 0 | Authorea, Figshare, Overleaf |
| Foundry Group | venture firm | 3 | 3 | 3D Robotics, MakerBot Industries, Sofar Ocean Technologies |
| General Catalyst | venture firm | 3 | 1 | Chai Discovery, Anaconda, Inc., JuliaHub |
| Lux Capital | venture firm | 3 | 3 | Authorea, EvolutionaryScale, Hugging Face |
| SOSV | accelerator / studio | 3 | 0 | Crowd Supply, Opentrons Labworks, Particle |
| Sequoia Capital | venture firm | 3 | 1 | Observable, Inc., Chai Discovery, Hugging Face |
| Spark Capital | venture firm | 3 | 3 | Framework Computer, Particle, SiFive |
| Y Combinator | accelerator / studio | 3 | 0 | Curvenote, K-Scale Labs, Opentrons Labworks |
| Addition | venture firm | 2 | 2 | Hugging Face, Seqera |
| Amazon | corporate / strategic | 2 | 0 | EvolutionaryScale, Hugging Face |
| Amino Collective | venture firm | 2 | 0 | Molecule, Seqera |
| Anzu Partners | venture firm | 2 | 1 | Arduino, Framework Computer |
| Arm | corporate / strategic | 2 | 0 | Arduino, Raspberry Pi Holdings / Raspberry Pi Ltd |
| Baillie Gifford | growth, crossover or PE | 2 | 0 | Chai Discovery, Tenstorrent |
| Battery Ventures | venture firm | 2 | 1 | Code Ocean, Chai Discovery |
| Bezos Expeditions | person (angel) | 2 | 0 | MakerBot Industries, Tenstorrent |
| Coatue | growth, crossover or PE | 2 | 1 | SiFive, Hugging Face |
| Counterpart Ventures | venture firm | 2 | 0 | Oxide Computer Company, Particle |
| Eclipse Ventures | venture firm | 2 | 1 | Oxide Computer Company, Tenstorrent |
| Gaingels | venture firm | 2 | 0 | Molecule, Trilobio |
| Greycroft | venture firm | 2 | 0 | Boltz PBC, Inventables |
| IDTheory | venture firm | 2 | 0 | LabDAO, Molecule |
| L1 Digital | crypto fund or DAO | 2 | 0 | Molecule, VitaDAO |
| Menlo Ventures | venture firm | 2 | 1 | Chai Discovery, JuliaHub |
| National Science Foundation (SBIR) | government grant | 2 | 0 | Kitware, re:3D |

SCIENCE_NOTES

## Philanthropists and foundations

Most of this money goes to projects, universities and nonprofits, not to companies. Sizes are as each source
states them, committed unless marked; "→ firms" says whether for-profit companies can receive it. Full rows:
[`data/programs.csv`](data/programs.csv) (passes p1–p3, with notes on how firm each figure is).

| Funder (people behind it) | Program | Years | Size reported | → firms | Recipients, for example |
| --- | --- | --- | --- | --- | --- |
| Chan Zuckerberg Initiative (Priscilla Chan, Mark Zuckerberg); Kavli Foundation and Wellcome joined in 2024 | [Essential Open Source Software for Science](https://chanzuckerberg.com/eoss/) | 2019– | about $47M over six cycles (sum of the program page) | no | napari, scikit-image |
| Chan Zuckerberg Initiative | [Open science grants](https://chanzuckerberg.com/science/programs-resources/open-science/grants) | 2019– | n/a | no | bioRxiv, medRxiv, protocols.io, 2i2c, The Carpentries |
| Gordon and Betty Moore Foundation | [Data-Driven Discovery](https://news.berkeley.edu/2014/10/02/funding-for-big-data-projects-in-ecology-astronomy-microscopy-and-more/) | 2013–18 | $60M | no | 14 Moore Investigators |
| Moore, Sloan and Helmsley foundations | [Project Jupyter](https://www.moore.org/newsroom/press-releases/2015/07/07/$6m-for-uc-berkeley-and-cal-poly-to-expand-and-enhance-open-source-software-for-scientific-computing-and-data-science) | 2015– | $6M | no | Jupyter (UC Berkeley, Cal Poly) |
| Alfred P. Sloan Foundation | [Open source in science](https://sloan.org/programs/digital-technology/open-source-in-science); [university OSPOs](https://sloan.org/programs/digital-technology/ospo-loi) | 2015– | n/a | no | NumFOCUS, JOSS, OSPOs at CMU, Johns Hopkins, RIT, UC Santa Cruz |
| Alfred P. Sloan Foundation with the Open Source Hardware Association | [Open Hardware Trailblazers fellowships](https://opensource.com/article/22/3/trailblazer-funding-open-hardware-academia) | 2022– | n/a | no | academic open-hardware leads |
| Schmidt Sciences (Eric and Wendy Schmidt) | [Virtual Institute for Scientific Software](https://engineering.jhu.edu/news/virtual-institute-scientific-software-johns-hopkins-schmidt-futures/) | 2022–27 | $40M | no | Johns Hopkins, UW, Georgia Tech, Cambridge |
| Schmidt Futures and Ken Griffin | [Convergent Research (focused research organisations)](https://www.schmidtfutures.org/schmidt-futures-and-ken-griffin-commit-50-million-to-support-the-launch-of-a-new-model-for-scientific-research/) | 2021– | $50M | no | Forest Neurotech |
| Arnold Ventures (Laura and John Arnold) | [Center for Open Science](https://www.cos.io/about/news/center-open-science-receives-75-million-additional-funding-laura-and-john-arnold-foundation) | 2013–19 | $12.75M | no | COS, OSF |
| Arcadia Fund (Lisbet Rausing, Peter Baldwin) | OurResearch: [2021](https://blog.openalex.org/arcadia-2021-grant/), [2024](https://blog.openalex.org/?p=2066) | 2021–29 | $4.5M, then $7.5M | no | OpenAlex, Unpaywall |
| The Navigation Fund and Astera Institute (Jed McCaleb) | [open-science grants](https://blog.openalex.org/arcadia-2021-grant/); [Astera residency](https://astera.org/residency) | 2022– | n/a | sometimes | OpenAlex, 2i2c, Open Science Hardware Foundation |
| Shuttleworth Foundation (Mark Shuttleworth) | [fellowships](https://en.wikipedia.org/wiki/Shuttleworth_Foundation) | 2007–24 | n/a | no | Open Source Ecology, FarmBot (seed grant) |
| Kyutai founders: Xavier Niel (Iliad), Rodolphe Saadé (CMA CGM), Eric Schmidt | [Kyutai open-science AI lab](https://techcrunch.com/2023/11/17/kyutai-is-an-french-ai-research-lab-with-a-330-million-budget-that-will-make-everything-open-source/) | 2023– | about €300M | no | Kyutai |
| Paul G. Allen | [Allen Institute for AI](https://en.wikipedia.org/wiki/Allen_Institute_for_AI) | 2014– | n/a | no | OLMo, Semantic Scholar |
| Gil Elbaz | [Common Crawl](https://en.wikipedia.org/wiki/Common_Crawl) | 2007– | n/a | no | Common Crawl |
| Brian Armstrong | [ResearchHub](https://www.researchhub.com/about) | 2021– | $1.5M+ paid out | no | open peer review and bounties |
| Patrick Collison, Tyler Cowen and co-donors | [Fast Grants](https://en.wikipedia.org/wiki/Fast_Grants) | 2020–22 | $50M+ (about 250 grants) | no | COVID-19 research |
| Mozilla Foundation | [Mozilla Open Source Support](https://www.mozilla.org/moss) | 2015–20 | $3.5M+ | sometimes | open-source projects Mozilla relies on |
| Gates Foundation | [digital public infrastructure](https://www.biometricupdate.com/202209/gates-foundation-commits-200m-to-digital-id-and-other-public-infrastructure) | 2022– | $200M | sometimes | MOSIP, Mojaloop |
| Mellon Foundation | [open scholarly infrastructure](https://www.mellon.org/grant-details/code-for-science-and-society-inc.-20453350) | 2005– | n/a | no | Coko, Invest in Open Infrastructure, Code for Science & Society |
| Craig Newmark Philanthropies | [open-source security](https://www.memorysafety.org/blog/2026-craig-newmark/) | 2019– | n/a | no | ISRG Prossimo, Wikimedia |
| Renaissance Philanthropy with Biohub, Wellcome and Kavli | [Open Source for Science Fund](https://www.renaissancephilanthropy.org/insights/open-source-for-science-fund-launches) | 2026– | $20M | not stated | research software |
| Ford and Sloan foundations | [Digital Infrastructure Insights Fund](https://www.fordfoundation.org/the-latest/news/major-philanthropies-tackle-inequality-by-strengthening-digital-infrastructure/) | 2018– | $1.3M (2020 round) | no | research on open infrastructure |
| Stability AI, Hugging Face, Canva, CoreWeave and others | [EleutherAI Institute](https://techcrunch.com/2023/03/02/stability-ai-hugging-face-and-canva-back-new-ai-research-nonprofit/) | 2023– | n/a | no | GPT-NeoX, The Pile |
| Thiel Foundation; Mercatus Center | [Thiel Fellowship](https://en.wikipedia.org/wiki/Thiel_Fellowship); [Emergent Ventures](https://en.wikipedia.org/wiki/Emergent_Ventures) | 2010–; 2018– | $250k per fellow; $1M launch grant | sometimes | individuals |

Philanthropy also reaches open-source companies directly, in the deal data:
- CZI granted to Seqera (Nextflow).
- Sloan granted to Julia Computing.
- The Shuttleworth Foundation granted FarmBot its seed money.
- Knight Foundation co-led Authorea's 2016 round with Lux Capital.
- Jed McCaleb and Sam Altman fund Arcadia Science.

## Governments and public programs

Grants unless marked as investment. "→ firms" says whether companies can receive it.

| Government or public body | Program | Years | Size reported | → firms | Recipients, for example |
| --- | --- | --- | --- | --- | --- |
| US Department of Energy | [Exascale Computing Project](https://science.osti.gov/-/media/ascr/ascac/pdf/meetings/2024/ECP-OverviewASCACMay2024pptx.pdf) | 2016–24 | $1.8B (whole project, mostly open-source software) | no | E4S, Spack, about 70 software products |
| US National Science Foundation | [POSE (Pathways to Enable Open-Source Ecosystems)](https://www.nsf.gov/funding/opportunities/pose-pathways-enable-open-source-ecosystems) | 2022– | about $100M obligated across 146 awards (NSF awards API; approximate) | sometimes | ecosystem organisations around university projects |
| US National Science Foundation | [CSSI](https://simpler.grants.gov/opportunity/358751) (successor to SI2) | 2010– | $34M (one solicitation) | no | research software at universities |
| US National Science Foundation and NVIDIA | [Open Multimodal AI Infrastructure, led by Ai2](https://blogs.nvidia.com/blog/national-science-foundation-ai2-open-ai-models/) | 2025–30 | $152M ($75M NSF, $77M NVIDIA in kind) | no | Ai2's open models |
| NIH Office of Data Science Strategy | [Sustainable software tools for open science](https://grants.nih.gov/grants/guide/rfa-files/rfa-od-24-010.html) | 2020– | n/a | no | biomedical research software |
| NASA Science Mission Directorate | [open-source tools, frameworks and libraries; TOPS](https://science.nasa.gov/researchers/open-science/nasa-open-science-funding-opportunities) | 2020s– | $6.5M (one TOPS round) | no | open-science software |
| DARPA | [POSH open-source hardware](https://linux.com/?p=471279) and IDEA | 2018– | $35M+ (POSH) | sometimes | open-source chip-design tools |
| DARPA and ARPA-H | [AI Cyber Challenge](https://www.darpa.mil/news/2025/ai-cyber-challenge-winners-def-con-33) | 2023–25 | $8.5M in final prizes | yes | open-source cyber-reasoning systems |
| Open Technology Fund (US) | [FOSS Sustainability Fund](https://docs.opentech.fund/otf-application-guidebook/our-funds-and-fellowships/free-and-open-source-software-sustainability-fund) | 2012– | n/a | sometimes | Tor, Signal |
| In-Q-Tel (US intelligence community), investment | [stakes in open-source companies](https://techcrunch.com/2012/09/18/mongodb-maker-10gen-closes-undisclosed-round-from-u-s-intelligence-agency/) | 2009– | n/a | yes | 10gen (MongoDB), Lucidworks, Cloudant, D2iQ |
| US SBIR/STTR (NSF, NIH, DOE), in the deal data | small-business grants | | | yes | Kitware, Enthought, re:3D, Backyard Brains |
| Germany: Sovereign Tech Agency | [Fund, Resilience, Fellowship, Challenges](https://www.sovereign.tech/tech) | 2022– | €11.5M in its first year (Osborne et al. 2024, via Edison) | sometimes | curl, OpenSSH, systemd, PHP, conda-forge |
| Germany: Prototype Fund (research ministry) | [grants to individuals](https://prototypefund.de/en/faq) | 2016– | n/a | no | civic and open-source prototypes |
| EU: Next Generation Internet, via NLnet | [NGI Zero Entrust, Core, Commons Fund](https://nlnet.nl/NGI0/) | 2020s– | n/a | sometimes | F-Droid, Pixelfed, open-hardware projects |
| EU: European Innovation Council | [EIC Accelerator](https://eic.ec.europa.eu/news/38-start-ups-and-smes-secure-eic-support-latest-round-eic-accelerator_en) (grant plus equity) | 2021– | n/a | yes | deep-tech start-ups |
| France: national AI strategy | scikit-learn and open data-science tools (Osborne et al. 2024, via Edison) | 2021– | €32M announced | not stated | scikit-learn (later Probabl) |
| France: Bpifrance, investment | [AI plan](https://www.bpifrance.com/2025/03/27/bpifrance-deploys-e10-billion-to-develop-the-ai-ecosystem-by-2029/), stakes | 2023– | €10B plan to 2029 | yes | Mistral AI, AMI Labs, Pollen Robotics, Probabl |
| UK: UKRI and the Software Sustainability Institute | [Research Software Maintenance Fund](https://www.software.ac.uk/research-software-maintenance-fund/round-2) | 2022– | n/a | no | research software |
| Netherlands, Australia, Canada | [eScience Center](https://www.esciencecenter.nl/about-us/), [ARDC](https://www.ardc.edu.au/about/), [CANARIE](https://www.canarie.ca/software/) | | n/a | no | research software and data |
| China: state and municipal funds, investment | [Zhipu AI and others](https://www.caixinglobal.com/2025-07-03/chinas-zhipu-ai-secures-140-million-investment-from-shanghai-state-backed-funds-102338133.html) | 2024– | n/a | yes | Zhipu AI, MiniMax, DeepSeek |
| Singapore: GIC and Temasek, investment | [open-weight AI and open-source companies](https://techcrunch.com/2025/10/09/reflection-raises-2b-to-be-americas-open-frontier-ai-lab-challenging-deepseek/) | 2025– | n/a | yes | Reflection AI, AMI Labs, Supabase, ClickHouse |

## Corporate open-source funds, platforms, crypto public goods and crowdfunding

| Funder | Program | Years | Size reported | → firms | Notes |
| --- | --- | --- | --- | --- | --- |
| GitHub (Microsoft) | [GitHub Sponsors](https://github.blog/open-source/maintainers/100-million-for-open-source-a-milestone-built-by-the-community/) | 2019– | $100M paid out cumulatively | sometimes | maintainers and projects |
| GitHub with M12 | [GitHub Fund and GitHub Accelerator](https://github.com/open-source/accelerator) | 2023– | GitHub reports "$130MM+ invested in open source" | yes | ToolJet, Unsloth |
| GitHub with partners | [Secure Open Source Fund](https://techcrunch.com/2024/11/19/github-launches-1-25m-open-source-fund-with-a-focus-on-security/) | 2024– | $1.25M | no | security of critical projects |
| Microsoft, Google, Amazon, Citi and others | [OpenSSF Alpha-Omega](https://openssf.org/community/alpha-omega/) | 2022– | $12.5M (2026 round) | no | security of critical projects |
| Sentry and member companies | [Open Source Pledge](https://opensourcepledge.com/) | 2024– | $9.8M pledged | no | $2,000 per developer a year to maintainers |
| Zerodha | [FLOSS/fund](https://zerodha.com/open-source/2025-report/) | 2024– | $1M a year | no | Krita, OpenSSL, FFmpeg, Blender |
| Bloomberg, Indeed, Spotify, Microsoft | FOSS contributor funds ([Bloomberg](https://www.bloomberg.com/company/stories/bloomberg-ospo-launches-foss-contributor-fund/), [Indeed](https://github.com/indeedeng/FOSS-Contributor-Fund), [Spotify](https://engineering.atspotify.com/2022/4/announcing-the-spotify-foss-fund), [Microsoft](https://github.com/microsoft/foss-fund)) | 2019– | about $10,000 per award | no | projects the sponsor depends on |
| Google | [Summer of Code](https://opensource.googleblog.com/2025/08/google-summer-of-code-2025-contributor-statistics.html); [Open Source Peer Bonus](https://opensource.googleblog.com/2024/06/google-open-source-peer-bonus-program-first-group-2024-recipients.html) | 2005– | n/a | no | 1,280 contributors in 2025 |
| Meta | [Llama Impact Grants](https://ai.meta.com/blog/llama-3-1-impact-grants-call-for-applications/) | 2023–25 | $0.5M, then $2M | yes | CognitiveLab |
| Sequoia; Andreessen Horowitz | [Open Source Fellowship; Open Source AI Grant](https://techcrunch.com/2024/11/10/open-source-projects-draw-equity-free-funding-from-corporates-startups-and-even-the-u-s-government/) | 2023– | n/a | no (equity-free) | FastAPI's author, vLLM, LMSYS |
| Mozilla | [Mozilla Ventures](https://techcrunch.com/2022/11/02/mozilla-launches-35m-venture-capital-fund-for-early-stage-responsible-tech-startups/) (investment); [Builders Accelerator](https://blog.mozilla.org/en/mozilla/14-ai-projects-to-watch-mozillas-first-builders-accelerator-cohort/) | 2022– | $35M fund; up to $100k a project | yes | Flower, Nous Research |
| Cloudflare; Fastly; Vercel | [Vite Ecosystem Fund](https://blog.cloudflare.com/launching-vite-ecosystem-fund); [Fast Forward](https://itsfoss.com/news/fastly-open-source-initiative/); [open-source program](https://vercel.com/open-source-program) | 2022– | $1M; $50M in free services; credits | no | infrastructure for projects |
| Tidelift (now Sonar) | [paying maintainers](https://prnewswire.com/news-releases/tidelift-reaches-milestone-of-one-million-dollars-committed-to-paying-open-source-maintainers-300754389.html) | 2018– | $1M+ committed by 2018 | no | maintainers of packages |
| Open Collective | [Open Source Collective](https://opencollective.com/opensource) (fiscal host for 2,735 collectives); [Open Collective Foundation](https://opencollective.com/foundation/updates/announcement-we-are-dissolving-open-collective-foundation) (dissolved 2024) | 2017– | n/a | no | fiscal hosting for projects |
| Gitcoin | [Gitcoin Grants](https://www.gitcoin.co/impact) | 2019– | $60M+ distributed | sometimes | quadratic funding for open source and web3 |
| Optimism Collective | [Retro Funding](https://optimism.io/blog/850m-op-dedicated-to-the-evolution-of-retro-funding) | 2022– | paid in OP tokens | sometimes | retroactive public-goods funding |
| Ethereum Foundation | [Ecosystem Support Program](https://blog.ethereum.org/category/ecosystem-support-program) | 2019– | about $32.6M in Q1 2025 alone | sometimes | client teams, tooling, research |
| Filecoin Foundation for the Decentralized Web; Protocol Labs | [grants](https://www.businesswire.com/news/home/20210928005396/en/Filecoin-Foundation-for-the-Decentralized-Web-Launches-to-Preserve-Humanity%E2%80%99s-Most-Important-Information) | 2020– | n/a | sometimes | Internet Archive, Freedom of the Press Foundation |
| VitaDAO; Molecule | [longevity research funding](https://www.lifespan.io/?p=118091); [IP-NFTs](https://molecule.xyz/blog/we-have-raised-12-7-million-in-seed-funding-to-build-the-future-of-decentralized-science/) | 2021– | $3M+ funded; $12.7M seed for Molecule | sometimes | DeSci research projects |
| Kickstarter, Crowd Supply, Indiegogo backers | reward crowdfunding | 2009– | e.g. Pine64's PINE A64, [$1.7M](https://silicon.co.uk/workspace/first-15-supercomputer-kickstarter-184595) | yes | Opentrons, OpenBCI, Bela, OpenMV, Luxonis, MNT Reform, LimeSDR |
| StartEngine, Wefunder, Crowdcube investors | equity crowdfunding | | e.g. Purism [$0.2M](https://www.linux-magazine.com/Online/News/Purism-Crowdfunding-Launched) | yes | Purism, Mycroft AI, Framework |

On crowdfunding, the strongest evidence Edison found is about open source itself. Across about 28,000
Kickstarter projects, open-source projects raised about 39% more relative to their goals than comparable projects,
and patent-based ones about 33% less (Bort et al. 2024; [Edison answer](edison/fund_who_funds_open_source_answer.md)).

## How good is the list?

CHECKS

## How the list was made

1. **Scope first.** [`PROTOCOL.md`](PROTOCOL.md) fixed what counts as an open-source-minded venture and as a
   funder, and the counting rules, before any funding data was gathered (`448c8c2`).
2. **Four groups of ventures**, kept apart in every table:
   - **U1**: all 387 companies behind the most-starred open-source projects on GitHub, from part 2. Nobody picked
     them for their funding.
   - **U2**: 97 open hardware, open science, lab and science-software ventures, picked by hand for relevance to DAL
     and the SDL kit.
   - **U3**: 156 well-known commercial open-source and open-weight AI ventures since 1998. This group
     over-represents successes.
   - **U4**: 402 young open-source startups from two third-party lists, Runa Capital's ROSS Index (2020–26) and Y
     Combinator's directory. They were added after the first passes had started, because there was time, and
     researched more lightly.
3. **Leads without a search engine.** Every research session shares one web-search budget, which ran out in part 2
   and again here after about 15 passes. So `scripts/investor_leads.py` first collected funding sentences for every
   venture from:
   - TechCrunch, SiliconANGLE, BetaKit and TechNode (their public WordPress APIs)
   - Hacker News links, which are often the company's own announcement
   - Wikipedia and Wikidata
   - the company's own site
4. **Deal passes.** Research agents (Claude Sonnet, 46 passes of 13–25 ventures) read the leads and the pages they
   point to. For each round they recorded the lead and the other named investors, with a source URL. Where nothing
   was disclosed they recorded "none found". Once the search budget was spent, they searched with
   `scripts/find_pages.py`, the same open APIs.
5. **Deepening passes.** Then 21 deepening passes went back to the 198 well-funded ventures whose history came
   back thin. They added rounds from company newsrooms, Wikipedia's cited articles, SEC prospectuses and archived
   press releases.
6. **Program passes.** Four passes listed the programs that fund open source and open science outside equity
   rounds: foundations, governments and public investors, corporate funds, crypto, accelerators and crowdfunding.
   They also recorded investors that state an open-source thesis, in their own words.
7. **Merge.** `scripts/build_funders.py` normalises names with a hand-made alias table
   ([`data/investor_aliases.csv`](data/investor_aliases.csv)) and types each funder from a hand-made table
   ([`data/investor_types.csv`](data/investor_types.csv), by the firm's own description; people count as angels).
   - A round that a source reports only as talks, a rumour or a raise in progress is kept, but its names are not
     counted (`counted` column in `deals.csv`).
   - Claude Opus planned the passes, wrote the scripts, reviewed the rows and wrote this file.

## Limits

- **Disclosure is selective.** Big rounds, well-known investors and companies that survived are reported more.
  Seed angels, small funds, failures and private companies outside the US and Europe are reported less. Counts
  therefore favour large, visible firms.
- **Coverage is uneven.** The search budget ran out early, so many ventures were researched only from news APIs,
  Wikipedia and company pages.
  - The first passes for U1, U2 and part of U3 had web search; the rest did not.
  - Chinese-language sources were read for a handful of companies only.
  - U4 (young startups) was researched lightly by design: for most of it, YC's own page and a quick look at the
    company site.
- **"None found" means none found.** Of the companies behind the most-starred projects, 159 have no
  disclosed outside funding in this data. Some will have raised money that was never announced or that these
  sources don't reach.
- **U2, U3 and U4 are not random.** U2 was picked for relevance and U3 for fame. U4 comes from lists kept by an
  accelerator (YC) and an investor (Runa), which both have an interest in the companies on them.
- **A count is not a return.** Nothing here measures whether these funders made money on open source. Edison found
  no study that does. Being on the list doesn't mean a funder would back a new open venture.
- **Names are normalised by hand.** Fund vehicles roll up to the firm, and corporate arms stay separate but roll up
  to their parent in one table. Some aliases will be missed, and a few distinct firms share a name.
- **Rounds are as sources describe them.** Labels (seed, Series A) and amounts follow the source, and sources
  sometimes disagree; the rows say so in `note`.

## Files

| Path | What it is |
| --- | --- |
| [`FUNDER_LIST.md`](FUNDER_LIST.md) | Every funder found, by type, with each venture linked to a page naming it |
| [`PROTOCOL.md`](PROTOCOL.md) | Scope and counting rules, committed before any data |
| [`deal_rules.md`](deal_rules.md), [`deepen_rules.md`](deepen_rules.md), [`program_rules.md`](program_rules.md) | The instructions each research pass followed |
| `data/ventures_input.csv` | The 1,042 ventures, their group (U1–U4) and the list each came from |
| `data/ventures.csv` | One row per venture: what is open, status, whether funding was found, part 2's funding total for U1 |
| `data/deals.csv` | One row per funding event: type, date, amount, lead and other investors (as written and normalised), source URL and kind |
| `data/investor_links.csv` | One row per funder–venture pair, with rounds, leads, first year and sources |
| `data/investors.csv` | One row per funder: type, ventures by group, leads, years, examples, stated open-source thesis |
| `data/programs.csv` | Program-level funders: foundations, governments, corporate funds, crypto, accelerators, crowdfunding |
| `data/investor_aliases.csv`, `data/investor_types.csv` | Hand-made name normalisation and funder types |
| `data/yc_open_source.csv`, `data/u4/ross_index.csv` | YC companies tagged or described as open source; every ROSS Index entry read |
| `data/portfolio/` | Investors' own portfolio pages, and the ventures matched on them |
| `data/source_checks_deals.csv`, `data/source_checks_programs.csv` | Whether each name or amount appears on the page it cites |
| `data/leads/` | The leads each pass started from |
| `data/deal_passes/`, `data/program_passes/` | Raw pass outputs, as written |
| `data/tables/` | The tables in this file, and the full open hardware, science and lab venture table |
| `edison/` | Edison's literature answer and blind audit, with full trajectories |
| `scripts/` | Everything that produced the above; run order in [`README.md`](README.md) |
| `figures/` | The two charts |
