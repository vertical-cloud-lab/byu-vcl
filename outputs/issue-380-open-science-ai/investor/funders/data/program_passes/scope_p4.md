# Pass p4: investors with a stated open-source thesis, and their open-source portfolios

One row per investor (`program` = "open-source investment thesis"; `funder_type` = `venture_fund`, `angel`,
`accelerator` or `corporate_program`). Put the investor's own words in `quote` (from its site, a partner's post or
a fund announcement) and its open-source portfolio companies in `examples` (up to 8, from its portfolio page or
announcements). `committed_usd` = fund size if the open-source fund is dedicated (e.g. a fund raised for open
source). Start with these, then add every other investor you find that states such a thesis:

- Dedicated: OSS Capital (Joseph Jacks), Runa Capital (and its ROSS Index), Open Core Ventures (Sid Sijbrandij), Heavybit, Uncorrelated Ventures, Essence VC, Crane Venture Partners, Boldstart Ventures, Amplify Partners, Decibel Partners, Unusual Ventures, Work-Bench, Haystack, Two Sigma Ventures, Notation Capital, 468 Capital, Mango Capital, Basis Set
- Large firms with an open-source practice or public thesis: Andreessen Horowitz (Peter Levine, Martin Casado; open-source AI grants), Index Ventures, Benchmark, Accel, Redpoint (Jason Warner), Lightspeed, Sequoia, Greylock, General Catalyst, Battery Ventures (OpenCloud), Bessemer, Insight Partners, Tiger Global, Coatue, GGV/Notable, IVP, NEA, Khosla, Felicis, Madrona, Point Nine, Seedcamp, Cherry Ventures, Earlybird, Speedinvest, Atomico, Balderton, Northzone, Lux Capital, Radical Ventures, Root Ventures (hardware)
- Corporate venture arms active in open source: GV, CapitalG, M12, Intel Capital, Salesforce Ventures, Dell Technologies Capital, Cisco Investments, IBM Ventures, Red Hat (investments), NVentures (NVIDIA), Samsung NEXT, Databricks Ventures, Snowflake Ventures, MongoDB Ventures, Hugging Face (investments), Mozilla Ventures, GitHub Fund
- Angels known for open-source investing: Nat Friedman, Daniel Gross, Elad Gil, Guillermo Rauch, Solomon Hykes, Mitchell Hashimoto, Thomas Dohmke, Jason Warner, Arash Ferdowsi, Spencer Kimball, Clem Delangue, Thomas Wolf, Ron Conway / SV Angel, Naval Ravikant, Balaji Srinivasan, Lachy Groom, Kevin Mahaffey, Tobi Lütke, Dharmesh Shah, Jeff Dean, Andrej Karpathy (only where a source shows investments in open-source ventures)
- Open hardware and open science investors: Root Ventures, HAX/SOSV, Bolt, Lux, DCVC, Khosla (Opentrons?), SoftBank (Opentrons?), Breakthrough Energy (open?), Spark Capital (Framework?), Eclipse (Oxide?), Foundry Group (MakerBot?) — verify each, keep only what a source supports

Output: about 60-100 rows. Pass id `p4`.
