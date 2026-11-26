# Owner classification audit

Primary-source checks: 2026-11-25.

I classified all 120 accounts in the original input order, using the seven columns requested in the task. I checked at least one organization website or repository for every account and attached a checked primary URL to every row. I used account identity, governance, and the relationship between open projects and paid products or services. I did not query or use financial outcomes to choose classes.

## Counts

| Class | Accounts |
|---|---:|
| `core` | 36 |
| `complement` | 19 |
| `nonprofit` | 9 |
| `academic` | 10 |
| `government` | 1 |
| `community` | 45 |
| `unknown` | 0 |
| **Total** | **120** |

**Judgment calls: 36. Unknown accounts: 0.** These are unweighted sample counts, not estimates of the distribution across all popular GitHub organizations. The sample contains 60 accounts from the top 300 and 60 from the remainder.

## Hardest classifications

- **`Spooky-Manufacturing` → `core`:** The input identifies a quantum-computing manufacturer and the repository contains designs for its own computer. I infer a product-focused hardware developer and core, but could not verify the company website, legal registration, or a paid offering; community remains plausible. [Checked source](https://github.com/Spooky-Manufacturing/8Q).
- **`OpenMontageInc` → `core`:** The repository links to a Studio desktop product and the account presents itself as OpenMontageInc. I infer a product-focused company and core, but the sources do not establish a paid tier or corporate registration. [Checked source](https://openmontage.video).
- **`labmlai` → `community`:** The two checked pages describe open tutorials and a self-hosted monitoring app, but do not establish a commercial legal entity or paid offering. I choose community, with company-versus-project identity unresolved. [Checked source](https://labml.ai/app).
- **`micro` → `core`:** The account combines an open services framework with a hosted assistant and related developer ecosystem. I lean core for this product-focused developer, but the exact paid-service/open-framework linkage and legal entity remain insufficiently explicit. [Checked source](https://micro.mu).
- **`K-Dense-AI` → `complement`:** The company distinguishes paid hosted/enterprise agents from free skills and the local BYOK assistant. I choose complement because the checked sources do not establish the paid service as a hosted edition of the open implementation; core is a plausible alternative. [Checked source](https://www.k-dense.ai).
- **`Textualize` → `complement`:** The current company homepage presents separate writing applications alongside the open Textual framework. I choose complement because I did not establish a current paid hosted or enterprise edition of the framework itself. [Checked source](https://www.textualize.io).
- **`php` → `community`:** I distinguish the PHP Group and contributor governance from the supporting PHP Foundation. The checked credits and foundation structure do not establish that the foundation owns or controls the php GitHub account. [Checked source](https://www.php.net/credits.php).
- **`spacetelescope` → `academic`:** STScI is an AURA-operated scientific research institute. NASA mission operations do not make it a government agency or a DOE-style national laboratory; the research-institute rule favors academic over nonprofit or government. [Checked source](https://www.stsci.edu/who-we-are).
- **`mixOmics-org` → `academic`:** The site states that the team is led by the Lê Cao lab at the University of Melbourne, with worldwide contributors. I choose a lab-led academic account rather than an autonomous multi-institution community; legal title is not documented. [Checked source](https://mixomics.org).

## Every account marked `judgment=1`

The table includes all judgment calls, in input order. A flag marks a discretionary boundary or incomplete ownership evidence; it does not imply that the owner is wholly unidentified.

| Owner | Class | Reason | Checked sources |
|---|---|---|---|
| `NousResearch` | `core` | I apply the open-model/API tie-breaker: Nous offers model access and Hermes Cloud. This is a direct product relationship, not merely tooling for another company’s closed models. | [Source 1](https://nousresearch.com); [Source 2](https://portal.nousresearch.com/) |
| `FuelLabs` | `core` | Fuel Labs is the identifiable developer, not a generic Ethereum community or automatically a foundation. I map its own blockchain infrastructure to core; conventional paid-product evidence is less explicit. | [Source 1](https://fuel.network); [Source 2](https://github.com/FuelLabs) |
| `ultraworkers` | `community` | The repository explicitly disclaims Anthropic affiliation. I treat Ultraworkers as an independent developer collective; I could not establish a separate owning legal entity. | [Source 1](https://github.com/ultraworkers/claw-code) |
| `OpenCut-app` | `community` | The README describes a maintainer-led MIT editor and distinguishes sponsors from the project. I found no owning company or paid edition; community is the more likely interpretation. | [Source 1](https://github.com/OpenCut-app/OpenCut) |
| `oven-sh` | `core` | I keep the product-focused Bun developer company in core and put Anthropic in parent, following the acquired-project-company tie-breaker rather than reclassifying it as a parent-company side tool. | [Source 1](https://bun.com/) |
| `odysseus-dev` | `community` | The README identifies an open, self-hosted workspace and a contributor-maintained project. A commercial or institutional owner is not established, so I choose community rather than inferring a startup from the product presentation. | [Source 1](https://github.com/odysseus-dev/odysseus) |
| `Textualize` | `complement` | The current company homepage presents separate writing applications alongside the open Textual framework. I choose complement because I did not establish a current paid hosted or enterprise edition of the framework itself. | [Source 1](https://www.textualize.io); [Source 2](https://textual.textualize.io) |
| `ByteByteGoHq` | `complement` | The owner is an educational publisher. I treat its free system-design repository as supporting separate paid courses, rather than a paid edition of that repository; the content-product boundary is debatable. | [Source 1](https://bytebytego.com) |
| `mermaid-js` | `core` | I apply the explicit project-home/maintainer-company tie-breaker: Mermaid Chart sells a hosted Mermaid product. The community appearance of the GitHub account does not override that rule. | [Source 1](https://www.mermaidchart.com) |
| `sveltejs` | `community` | I distinguish a framework team from the companies employing its maintainers. Vercel employment and sponsorship alone do not establish ownership or satisfy the maintainer-founded-company tie-breaker. | [Source 1](https://svelte.dev/docs/svelte/faq) |
| `ChatGPTNextWeb` | `core` | The README advertises an Enterprise Edition and a business contact alongside the hosted NextChat offering. I apply the project-home/commercial-provider tie-breaker despite incomplete legal-entity detail. | [Source 1](https://nextchat.club); [Source 2](https://github.com/ChatGPTNextWeb/NextChat) |
| `rtk-ai` | `core` | RTK AI Labs identifies founders and advertises RTK Pro. I apply the project-home/maintainer-company tie-breaker; I use the public team name rather than inventing a registered legal name. | [Source 1](https://www.rtk-ai.app); [Source 2](https://www.rtk-ai.app/team/) |
| `OpenMontageInc` | `core` | The repository links to a Studio desktop product and the account presents itself as OpenMontageInc. I infer a product-focused company and core, but the sources do not establish a paid tier or corporate registration. | [Source 1](https://github.com/OpenMontageInc/OpenMontage); [Source 2](https://openmontage.video) |
| `pingdotgg` | `complement` | The T3 Code README identifies T3 Tools, Inc. and explicitly presents T3 Code as free. Ping Labs separately markets a subscription chat app and creator tools, so I choose complement. | [Source 1](https://ping.gg/); [Source 2](https://github.com/pingdotgg/t3code) |
| `scikit-learn` | `community` | Its governance document explicitly calls it a meritocratic, consensus-based community project. Institutional employment and support do not establish a single university or foundation as owner. | [Source 1](https://scikit-learn.org/stable/about.html); [Source 2](https://scikit-learn.org/stable/governance.html) |
| `labmlai` | `community` | The two checked pages describe open tutorials and a self-hosted monitoring app, but do not establish a commercial legal entity or paid offering. I choose community, with company-versus-project identity unresolved. | [Source 1](https://labml.ai); [Source 2](https://labml.ai/app) |
| `tabler` | `core` | The Tabler site sells Pro templates and component packages and credits Codecalm. I apply the project-home/maintainer-business tie-breaker rather than treating it as only an individual’s free projects. | [Source 1](https://tabler.io) |
| `K-Dense-AI` | `complement` | The company distinguishes paid hosted/enterprise agents from free skills and the local BYOK assistant. I choose complement because the checked sources do not establish the paid service as a hosted edition of the open implementation; core is a plausible alternative. | [Source 1](https://www.k-dense.ai); [Source 2](https://github.com/K-Dense-AI/k-dense-byok) |
| `mastodon` | `nonprofit` | The organization explicitly describes itself as nonprofit, but its about page describes multiple legal entities and a governance transition. I retain the common name Mastodon rather than asserting one entity controls every asset. | [Source 1](https://joinmastodon.org/about) |
| `php` | `community` | I distinguish the PHP Group and contributor governance from the supporting PHP Foundation. The checked credits and foundation structure do not establish that the foundation owns or controls the php GitHub account. | [Source 1](https://www.php.net/credits.php); [Source 2](https://thephp.foundation/structure/) |
| `2noise` | `community` | The organization and README identify a speech-model developer collective. Research-only model terms do not prove university ownership, and I found no owning company or paid API; I choose community. | [Source 1](https://github.com/2noise); [Source 2](https://github.com/2noise/ChatTTS) |
| `reworkd` | `complement` | The current company site markets web-data extraction, while the sampled repository is the distinct general-purpose AgentGPT project. I choose complement; the relationship between the two products is not fully documented. | [Source 1](https://reworkd.ai); [Source 2](https://github.com/reworkd/AgentGPT) |
| `jj-vcs` | `community` | I classify the independent Jujutsu organization, not Google simply because Google employees contributed or historical copyrights reference Google. Current maintainer control is more consistent with community. | [Source 1](https://github.com/jj-vcs/jj) |
| `openssl` | `nonprofit` | The official site lists both OpenSSL Software Foundation Inc and a separate commercial services corporation. I choose nonprofit foundation stewardship, while flagging the split legal and commercial structure. | [Source 1](https://openssl.org/about/) |
| `composer` | `core` | Composer’s creators operate Packagist Conductors GmbH, which sells managed Composer repositories and extended Composer support. I apply the maintainer-founded-company tie-breaker although the core client remains community-developed. | [Source 1](https://getcomposer.org/); [Source 2](https://packagist.com/about/) |
| `readest` | `core` | The site credits Bilingify LLC and sells Plus/Pro subscriptions for the reader’s cloud features. I apply the project-home/company tie-breaker and identify the legal company, rather than only the project name. | [Source 1](https://readest.com); [Source 2](https://readest.com/en/pricing) |
| `pypa` | `community` | PEP 609 describes PyPA as a collaborative community and separates it from the PSF Packaging Working Group. PSF association and shared policies are not, on their own, evidence that PSF owns this organization account. | [Source 1](https://www.pypa.io/en/latest/); [Source 2](https://peps.python.org/pep-0609/) |
| `livewire` | `core` | The framework site integrates the creator’s free and paid Flux components into the Livewire ecosystem. I apply the project-home/commercial-edition tie-breaker; paid components are adjacent to, rather than a hosted copy of, the framework. | [Source 1](https://livewire.laravel.com); [Source 2](https://fluxui.dev) |
| `micro` | `core` | The account combines an open services framework with a hosted assistant and related developer ecosystem. I lean core for this product-focused developer, but the exact paid-service/open-framework linkage and legal entity remain insufficiently explicit. | [Source 1](https://micro.mu); [Source 2](https://github.com/micro/go-micro) |
| `PrimeIntellect-ai` | `core` | The paid model-training platform directly integrates its open Prime-RL and Verifiers ecosystem. I choose core at account level rather than treating all open tools as complements to generic rented compute. | [Source 1](https://primeintellect.ai/) |
| `scipipe` | `community` | The project has academic origins, but the checked website and repository present a standalone software project rather than one institution’s lab account. I choose community rather than academic. | [Source 1](https://scipipe.org); [Source 2](https://github.com/scipipe/scipipe) |
| `spacetelescope` | `academic` | STScI is an AURA-operated scientific research institute. NASA mission operations do not make it a government agency or a DOE-style national laboratory; the research-institute rule favors academic over nonprofit or government. | [Source 1](https://www.stsci.edu/who-we-are); [Source 2](https://www.stsci.edu/what-we-do) |
| `pathsim` | `community` | The site credits Milan Rother personally and offers an MIT framework, alongside a consulting link. That does not establish a company owning the account; I use the individual-organization rule and choose community. | [Source 1](https://pathsim.org) |
| `mixOmics-org` | `academic` | The site states that the team is led by the Lê Cao lab at the University of Melbourne, with worldwide contributors. I choose a lab-led academic account rather than an autonomous multi-institution community; legal title is not documented. | [Source 1](https://mixomics.org) |
| `Spooky-Manufacturing` | `core` | The input identifies a quantum-computing manufacturer and the repository contains designs for its own computer. I infer a product-focused hardware developer and core, but could not verify the company website, legal registration, or a paid offering; community remains plausible. | [Source 1](https://github.com/Spooky-Manufacturing/8Q) |
| `brainlife` | `academic` | The checked platform explicitly identifies the University of Texas at Austin and the university-based research team. I choose academic rather than community despite contributions and use across many institutions. | [Source 1](https://brainlife.io/about); [Source 2](https://brainlife.io/docs/) |

## Decisions and limitations

- I classify the organization account, not a repository’s topic, its contributors’ employers, or its sponsors. I do not treat institutional affiliations alone as ownership.
- I distinguish a foundation’s legal stewardship from fiscal hosting or other support. I apply the supplied community examples even when a project has an organizational sponsor.
- I apply the explicit project-home/maintainer-company tie-breaker where a commercial provider offers the project’s hosted, enterprise, licensed, or support variant. I flag borderline applications.
- I use current ownership statements. React’s official announcement explicitly places React and React Native under the React Foundation, hosted by the Linux Foundation; the lysine-dev account identifies itself as a Commonhaus member. I do not preserve their historical corporate associations as their current class.
- I leave `parent` blank when no different ultimate parent is established. A corporate entity can remain core or complement even where its ultimate parent is a nonprofit foundation.
- I use `unknown` only when the owner cannot be identified at all. For named but legally informal project groups, I choose the more likely class and flag uncertainty when appropriate. Zero unknowns should not be read as proof that every organization’s legal title was verified.
- Public pages establish product and governance relationships more reliably than legal title or organization-account administration. Some named legal entities and paid-product links remain unverified; the judgment notes identify these gaps. A failed website fetch is a verification limitation, not evidence about an owner’s business status.
- This is one independent rules-based audit, not a legal due-diligence review or an inter-rater reliability study. No comparison labels were provided, so I do not report agreement or accuracy.
- I use product descriptions and commercial offerings to distinguish core from complement without measuring financial outcomes. For product-boundary cases, the chosen class is explicitly a judgment, not a measured commercial mix.

## Validation

- Exactly 120 output rows, with one row for every input owner and no duplicates.
- Owner order exactly matches `audit_sample.csv`.
- Exact columns: `owner,cls,entity,parent,basis,judgment,source_url`.
- Every `basis` has at most 15 whitespace-delimited words; every judgment flag is 0 or 1.
- Every output source URL was successfully fetched in this audit.
