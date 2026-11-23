# Group A: commercial open-source data infrastructure

Method: MongoDB through Cockroach Labs were researched with 46 WebSearch queries. After the shared search budget ran out, the other twelve were researched with WebFetch on 42 known URLs (see `search_tool` and `fetched_urls`). Unconfirmed values are null. Sentry is low confidence.

| Organization | Openness | Origin | Founded | Outcome | Latest value (date) |
|---|---|---|---|---|---|
| MongoDB | 3→1 | founders | 2007 | IPO 2017; public | $23.0B mkt cap (2026-11-20) |
| Elastic | 3→2 | founders (NL) | 2012 | IPO 2018; public | $10.2B mkt cap (2026-10-30) |
| Redis | 2→2 | founders (Israel) | 2011 | private | $2.0B (2021-04) |
| HashiCorp | 2→1 | founders | 2012 | IPO 2021; IBM 2025 | $6.4B (2025-02-27) |
| Confluent | 3→2 | LinkedIn spin-out | 2014 | IPO 2021; IBM 2026 | $11B (2026-03-17) |
| Cockroach Labs | 3→1 | founders | 2015 | private | $5B (2021-12) |
| Couchbase | 2→1 | startup merger | 2011 | IPO 2021; Haveli 2025 | $1.5B (2025-09-24) |
| Grafana Labs | 3→2 | founders | 2014 | private | $6B (2024-08) |
| Sentry | 3→1 | side project | 2008 (project) | private | not found |
| Tiger Data (Timescale) | 3→2 | founders | 2015 | private | >$1B (2022-02) |
| InfluxData | 3→2 | founders (YC) | 2012 | private | not found |
| Neo4j | 3→2 | founders (Sweden) | 2007 | private | $2.2B (2024-11) |
| MariaDB | 3→2 | MySQL founder's fork | 2009 | SPAC 2022; K1 2024 | ~$37M (2024-09) |
| Cloudera + Hortonworks | 2→2 | founders; Yahoo spin-out | 2008 | IPOs; merged 2019; PE 2021 | $5.3B (2021-10) |
| Docker | 3→2 | founders (Paris) | 2008 | enterprise unit sold 2019 | not found |
| Kong | 2→2 | founders (Milan) | 2009 | private | $2B (2023) |
| Lightbend (Akka) | 3→1 | founders | 2011 | private | not found |
| MySQL AB / Sun | 3→2 | founders (Sweden) | 1995 | Sun 2008; Oracle 2010 | ~$1B (2008-02) |

## Observations

1. **Relicense, fork, partial reversal.** Elastic closed in 2021; AWS forked OpenSearch, which moved to the Linux Foundation; Elastic re-added AGPL in 2024. Redis closed in March 2024; Valkey followed eight days later, backed by AWS, Google and Oracle; Redis added AGPL in 2025. The reversals restored OSI status but not the cloud channel: AWS now recommends Valkey.
2. **Forks need a motivated backer:** hyperscalers (OpenSearch, Valkey), ecosystem vendors (OpenTofu) or ASF volunteers (Pekko). Where nobody resold the product, closing drew no fork (CockroachDB, Couchbase, Sentry). Neo4j stopped a redistribution in court.
3. **Closing did not stop growth when the company owned the cloud service.** MongoDB, on SSPL since 2018, reached $2.46B revenue and about 19x its IPO valuation. MongoDB, HashiCorp and Elastic relicensed 1 to 2.3 years after listing; Couchbase did so four months before.
4. **Listed open-core firms mostly ended up owned by someone else.** Of eight that listed, only MongoDB and Elastic remain independent. IBM bought HashiCorp (under half its IPO value) and Confluent (near its IPO valuation). Private equity bought Cloudera, MariaDB (~$37M after a SPAC) and Couchbase (at about its IPO share price).
5. **OSI copyleft looks like the stable middle.** Grafana chose AGPL in 2021, drew no fork, and doubled its valuation to over $6B. Elastic and Redis later converged on AGPL. Sentry's FSL, open after two years, is another middle path.
6. **The technology outlives the company in foundations.** Kafka at the ASF meant Confluent restricted only add-ons. OpenSearch, Valkey, OpenTofu, Pekko, DocumentDB and the MariaDB Foundation keep code available whatever vendors do, so code robustness and company robustness diverge.
7. **Private valuations froze for closers without an exit:** Redis ($2B in 2021, about $1.3B on secondaries) and Cockroach Labs ($5B in 2021). Grafana, which stayed OSI-licensed, re-priced upward in 2024.
8. **Ownership change is itself a risk.** Oracle inheriting MySQL triggered an EU review and the MariaDB fork. MariaDB then wrote the BSL later adopted by CockroachDB, Couchbase, Lightbend and HashiCorp.
9. **Origins.** Most are founder startups led by the project's creators. Both corporate spin-outs (Confluent from LinkedIn, Hortonworks from Yahoo) built on ASF projects and never relicensed their cores.
