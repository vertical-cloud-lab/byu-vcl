# Verification pass 2: second-source check (2026-11-23)

Every low-confidence case file, plus the medium-confidence files in groups D (hardware) and E
(lab automation and AI for science), had its most consequential facts checked against a page
other than the one already cited. Each checked file now ends with a `verification_pass2` block.
It holds `checked`, `confirmed` (with a short verbatim quote and the URL), `contradicted`
(old value, new value, source, and whether the change was applied), `unconfirmed` (with the
reason and the URLs tried), `confidence_change`, and every URL fetched, including the ones that
failed. Rules, sources and caveats are under [Method](#method) at the end.

## Results

- **38 files checked.** That is 24 of the 25 low-confidence files (`E/strateos.json` was skipped
  because it already lists eight searches) and all 14 medium-confidence D and E files with fewer
  than four searches. Also skipped for having four or more searches: `D/makerbot`,
  `D/prusa-research`, `E/emerald-cloud-lab` and `E/opentrons`. The folder holds 122 case files.
- **161 facts checked, 99 confirmed** on an independent page. Only 7 of those 99 confirmations
  rest on Wikipedia; the rest come from official pages, SEC filings, registries or licence files.
  One confirmation reuses the page already cited for the same field and is flagged
  `"independent": false`.
- **16 values changed:** 10 nulls filled from primary pages, 3 corrected values and 3 corrected
  sentences.
- **2 contradictions recorded but not applied**, both convention or third-party cases.
- **46 facts still unconfirmed.**
- **Confidence raised in 11 files:** 9 from low to medium, 2 from medium to high. No confidence
  was lowered. Files still at low: `D/creality`, `D/lulzbot-aleph-objects`, `D/openbci`,
  `D/pine64`, `D/reprap`, `D/seeed-studio`, `D/sofar-ocean-openrov`, `B/dbt-labs`, `E/atinary`,
  `E/chemify`, `E/evolutionaryscale`, `E/kebotix`, `E/lila-sciences`, `E/orbital-materials` and
  `E/radical-ai` (and `E/strateos`, which was not checked).

### Changed values

Each old value is kept in that file's `verification_pass2.contradicted[]`.

**Corrected values (3)**

| File | Field | Old → new | Source |
| --- | --- | --- | --- |
| `E/chemify.json` | `founded_year` | 2022 → 2019 | [Companies House SC645290](https://find-and-update.company-information.service.gov.uk/company/SC645290): "CHEMIFY LIMITED", incorporated 24 Oct 2019, no previous names, with accounts filed for 2020 and 2021 and shares allotted in 2021. Wikipedia (Leroy Cronin) says "launched in 2019". **Convention call:** Chemify's own timeline says "2022 CHEMIFY FOUNDED", so revert this if the dataset should use public-launch years. |
| `E/atinary.json` | `hq_country` | CH → US | Atinary's own boilerplate in its 11 Aug 2026 [release on ir.bruker.com](https://ir.bruker.com/press-releases/press-release-details/2026/Bruker-Announces-Strategic-Collaboration-with-Atinary-Technologies-to-Advance-Self-Driving-Laboratories/default.aspx), also on atinary.com: "Headquartered in Menlo Park, California, with operations in Boston and Lausanne". The CH value had been an inference. `us_focus` (false) and `origin_detail` were **not** changed and should be revisited. |
| `E/isomorphic-labs.json` | `risk_events[0]` | "Apr 2025: …" → "31 Mar 2025: …" | [Isomorphic Labs' own $600M announcement](https://www.isomorphiclabs.com/articles/isomorphic-labs-announces-600m-external-investment-round), dated March 31, 2025. |

**Nulls filled from primary pages (10)**

| File | Field | Old → new | Source |
| --- | --- | --- | --- |
| `B/prefect.json` | `founded_year` | null → 2018 | [Prefect's Dagster acquisition letter](https://www.prefect.io/blog/prefect-is-acquiring-dagster-labs) (13 Jul 2026): "Prefect and Dagster were both founded in 2018" |
| `E/chemspeed.json` | `founded_year` | null → 1997 | [chemspeed.com/about](https://www.chemspeed.com/about): "Chemspeed was founded 1997." |
| `E/kebotix.json` | `founded_year` | null → 2017 | [Kebotix's SEC Form D](https://www.sec.gov/Archives/edgar/data/1749021/000174902118000001/primary_doc.xml) (2018, repeated in 2020): year of incorporation 2017 |
| `E/cuspai.json` | `latest_value_usd`, `_type`, `_date` | null → 2,600,000,000, private_valuation, 2026-07 | [CuspAI's Series B post](https://cusp.ai/blog/launching-our-ai-materials-foundry-and-450-million-series-b) (20 Jul 2026): "values Cusp at $2.6 billion". Wikipedia (Max Welling) agrees. |
| `E/evolutionaryscale.json` | `relicensing_events[0].year`, `license_history[1].year` | null → 2026 | [Biohub/esm LICENSE.md history](https://github.com/Biohub/esm/commits/main/LICENSE.md): commit c94ed8d, 27 May 2026, swaps the Cambrian licences for MIT |
| `E/isomorphic-labs.json` | `relicensing_events[1].year`, `license_history[3].year` | null → 2026 | [alphafold3 LICENSE history](https://github.com/google-deepmind/alphafold3/commits/main/LICENSE): commit 7b197fe, 9 Jun 2026, "Change the code license from CC BY-NC-SA 4.0 to Apache 2.0" |

**Corrected sentences (3)**

- `B/prefect.json` `origin_detail`: "Founder … and founding year were not confirmed" became "Founded in 2018
  by Jeremiah Lowin, its founder and CEO", from the same Prefect letter.
- `D/raspberry-pi.json` `origin_detail`: the trading subsidiary was incorporated on 10 Sep 2012
  as Newincco 1209 Ltd and renamed Raspberry Pi (Trading) Ltd on 18 Dec 2012
  ([Companies House 08207441](https://find-and-update.company-information.service.gov.uk/company/08207441)).
  The old text, following Wikipedia, gave the renaming date as the incorporation date.
- `E/benchling.json` `risk_events[1]`: "filed Form S-1 with the SEC per Wikipedia" now says that
  Wikipedia's claim rests on a Reuters report citing anonymous sources, and that
  [EDGAR (CIK 1687403)](https://data.sec.gov/submissions/CIK0001687403.json) lists only a 2016
  Form D and no S-1. Any 2021 filing was therefore a confidential draft.

### Contradictions recorded but not applied

- `D/reprap.json` `founded_year`: the file has 2005, Wikipedia's project-start year.
  [reprap.org/wiki/About](https://reprap.org/wiki/About) says RepRap was "first introduced online in
  February 2004", meaning Bowyer's essay. This is a definitional difference, so the file was left
  unchanged.
- `D/pine64.json` `funding_as_of`: the file says $1.7M in "2015-12". The TechCrunch article that
  Wikipedia cites (21 Jan 2016, already in the file's sources) says "so far raised over $1.4
  million", so the campaign was still running in 2016. Not applied, because the source is
  third-party and no close date was found.

### Newer information found (not applied)

- **dbt Labs:** getdbt.com now says "Fivetran + dbt Labs is now Fivetran". Tristan Handy signs
  Fivetran's 11 Nov 2026 founders' letter as its President and Co-Founder. The `name` field and
  the merger date (`exit_events[0].year`, still null) need an update.
- **Sofar Ocean:** SEC Form D filings show $39.1M raised in Oct 2021 and $22.25M in Nov 2024. The
  file's $8.65M is a floor from 2019 and far too low.
- **Citrine Informatics:** Form D filings show further raises in Sep 2023 ($5.0M) and Jan 2025
  ($2.6M), after the file's "no round since Jan 2023".
- **UltiMaker:** 330 employees in May 2022, per Stratasys' 6-K exhibit.

### Important facts still unconfirmed

- **Valuations:**
  - Lila Sciences' $1.3B rests on a Reuters headline that WebFetch cannot open.
  - dbt Labs' $4.2B, its $414M funding total and its 2016 founding year rest on Contrary Research
    alone.
  - The market caps for Raspberry Pi, Recursion and Schrödinger, dated 2026-11-23, come from
    StockAnalysis only. No primary page gives a dated market cap.
  - Recursion's $2.92B IPO value is consistent with the 424B4 share count × $18, but no page states
    it.
- **Funding totals:**
  - Lila $550M, Radical AI $55M and EvolutionaryScale $142M (TechCrunch only) each rest on a single
    page.
  - CuspAI's "over $650M" is $70M more than the ≥ $580M its own round announcements add up to.
  - Pine64's $1.7M is unconfirmed.
  - Formlabs, Oxide, Framework and Citrine totals are researcher sums; each round checked out, but
    no page states a total.
- **Exits and status:**
  - Whether the Qualcomm–Arduino deal has closed (only the headline of Qualcomm's release
    rendered).
  - Creality's HKEX listing year and exchange, which are matched only by the order of a timeline.
  - LulzBot's 2019 sale year (Wikipedia only).
  - The year EvolutionaryScale joined Biohub.
  - Whether Kebotix is still operating: the latest primary evidence is from 2024, and its Form D
    raises in 2023 and 2024 contradict the file's "dormant since 2022".
- **Founding years:**
  - The years for Arduino, System76, OpenBCI, Pine64 and Sofar/OpenROV were not confirmed by any
    second page.
  - Atinary and Orbital Materials stay null. A UK "Orbital Materials Ltd" was incorporated on
    2 Sep 2022, but no page ties it to the US company named in the licence.
- **Openness claims that rest on absence:** Periodic Labs, OpenBCI's Galea (the 2020 "closing"),
  Atinary and Chemify.
- **OCP `license_history[1]`:** the cited legal-documents page returns 404, and the cited policy
  URL now serves a July 2024 revision that names only the OWF CLA 0.9 and OWFa 0.9.

## Per-file table

"Confirmed" lists fields with the domain of the confirming page. The full quote is in the file.
Fields in "Changed" were rewritten. A "conflict, not applied" entry records a contradiction left
in place.

| File | Facts checked | Confirmed (independent page) | Changed (old → new, source) | Still unconfirmed | Confidence |
| --- | --- | --- | --- | --- | --- |
| `A/sentry.json` | relicensing_events[0].year, relicensing_events[0].from, relicensing_events[1].year, openness_current | relicensing_events[0].year (api.github.com); relicensing_events[0].from (api.github.com); relicensing_events[1].year (api.github.com); openness_current (github.com) | none | – | low → **medium** |
| `B/dbt-labs.json` | founded_year, funding_total_usd, latest_value_usd, exit_events[0].counterparty | exit_events[0].counterparty (getdbt.com) | none | founded_year; funding_total_usd; latest_value_usd | low |
| `B/prefect.json` | founded_year, origin_detail, license_history[0].license, flagship_projects[3], funding_total_usd | license_history[0].license (github.com); flagship_projects[3] (prefect.io) | founded_year: null → 2018 ([prefect.io](https://www.prefect.io/blog/prefect-is-acquiring-dagster-labs)); origin_detail: Venture-backed startup behind the Prefect Python workflow framework; remote-first. Founder (commonly reported as Jeremiah Lowin) and founding year were not confirmed in fetched pages → Venture-backed startup behind the Prefect Python workflow framework; remote-first. Founded in 2018 by Jeremiah Lowin, its founder and CEO (per Prefect's own 13 Jul 2026 Dagster acquisition letter) ([prefect.io](https://www.prefect.io/blog/prefect-is-acquiring-dagster-labs)) | funding_total_usd | low → **medium** |
| `D/adafruit.json` | founded_year, funding_total_usd, still_operating, openness_current | founded_year (adafruit.com); still_operating (api.github.com); openness_current (raw.githubusercontent.com) | none | funding_total_usd | medium |
| `D/arduino.json` | funding_total_usd, exit_events[2], ownership_status, founded_year | funding_total_usd (blog.arduino.cc); exit_events[2] (qualcomm.com) | none | ownership_status; founded_year | medium |
| `D/bambu-lab.json` | founded_year, relicensing_events[0].year, still_operating | founded_year (zh.wikipedia.org); relicensing_events[0].year (blog.bambulab.com); still_operating (blog.bambulab.com) | none | – | medium |
| `D/creality.json` | founded_year, exit_events[0].type, exit_events[0].year, exit_events[0].counterparty, still_operating, relicensing_events[0].year | founded_year (zh.wikipedia.org); exit_events[0].type (creality.cn); still_operating (creality.com) | none | exit_events[0].year; exit_events[0].counterparty; relicensing_events[0].year | low |
| `D/formlabs.json` | founded_year, latest_value_usd, latest_value_date, funding_total_usd, still_operating | founded_year (formlabs.com); latest_value_usd (formlabs.com); latest_value_date (formlabs.com); still_operating (formlabs.com) | none | funding_total_usd | medium |
| `D/framework-computer.json` | founded_year, funding_total_usd, relicensing_events[0].year, still_operating | founded_year (frame.work); relicensing_events[0].year (frame.work); still_operating (frame.work) | none | funding_total_usd | medium |
| `D/lulzbot-aleph-objects.json` | founded_year, exit_events[0].year, exit_events[0].counterparty, still_operating, openness_initial, openness_current | founded_year (lulzbot.com); exit_events[0].counterparty (lulzbot.com); still_operating (lulzbot.com); openness_initial (ryf.fsf.org); openness_current (lulzbot.com) | none | exit_events[0].year | low |
| `D/open-compute-project.json` | founded_year, ownership_status, still_operating, license_history[1].license | founded_year (opencompute.org); ownership_status (opencompute.org); still_operating (opencompute.org) | none | license_history[1].license | medium |
| `D/openbci.json` | founded_year, still_operating, openness_current, relicensing_events[0].year | still_operating (docs.openbci.com) | none | founded_year; openness_current; relicensing_events[0].year | low |
| `D/oxide-computer.json` | founded_year, funding_total_usd, still_operating | founded_year (prnewswire.com); still_operating (prnewswire.com) | none | funding_total_usd | medium |
| `D/pine64.json` | founded_year, funding_total_usd, funding_as_of, still_operating, relicensing_events[0].year | still_operating (api.github.com) | none | founded_year; funding_total_usd; relicensing_events[0].year; funding_as_of conflict, not applied: 2015-12 vs 2016-01 or later (campaign still raising on 2016-01-21) (techcrunch.com) | low |
| `D/raspberry-pi.json` | founded_year, origin_detail, exit_events[0].year, exit_events[0].value_usd, latest_value_usd, still_operating | founded_year (find-and-update.company-information.service.gov.uk); exit_events[0].year (investors.raspberrypi.com); still_operating (find-and-update.company-information.service.gov.uk) | origin_detail: The Raspberry Pi Foundation, a UK educational charity, was established in autumn 2008 to promote computer science in schools. It launched the $35 Model B on 29 Feb 2012. Its trading subsidiary, Raspberry Pi (Trading) Ltd, was incorporated on 18 Dec 2012 and renamed Raspberry Pi Ltd in 2021. It became part of Raspberry Pi Holdings plc, which listed on the London Stock Exchange in June 2024. → The Raspberry Pi Foundation, a UK educational charity, was established in autumn 2008 to promote computer science in schools. It launched the $35 Model B on 29 Feb 2012. Its trading subsidiary was incorporated on 10 Sep 2012 as Newincco 1209 Ltd, took the name Raspberry Pi (Trading) Ltd on 18 Dec 2012 and was renamed Raspberry Pi Ltd in Nov 2021 (Companies House 08207441). It became part of Raspberry Pi Holdings plc, which listed on the London Stock Exchange in June 2024. ([find-and-update.company-information.service.gov.uk](https://find-and-update.company-information.service.gov.uk/company/08207441)) | exit_events[0].value_usd; latest_value_usd | medium |
| `D/reprap.json` | founded_year, license_history[0].license, still_operating | license_history[0].license (reprap.org); still_operating (reprap.org) | none | founded_year conflict, not applied: 2005 vs 2004 (reprap.org) | low |
| `D/seeed-studio.json` | founded_year, still_operating, license_history[2].license | founded_year (wiki.seeedstudio.com); still_operating (github.com); license_history[2].license (raw.githubusercontent.com) | none | – | low |
| `D/sofar-ocean-openrov.json` | exit_events[0], funding_total_usd, founded_year, still_operating | exit_events[0] (sec.gov); still_operating (sofarocean.com) | none | funding_total_usd; founded_year | low |
| `D/sparkfun.json` | founded_year, still_operating, openness_current | founded_year (sparkfun.com); still_operating (sparkfun.com); openness_current (raw.githubusercontent.com) | none | – | medium → **high** |
| `D/system76.json` | founded_year, relicensing_events[0].year, relicensing_events[1].year, license_history[3].year, still_operating | relicensing_events[0].year (api.github.com); license_history[3].year (system76.com); still_operating (system76.com) | none | founded_year; relicensing_events[1].year | medium |
| `D/ultimaker.json` | founded_year, funding_total_usd, exit_events[0], license_history[2].license | founded_year (sec.gov); funding_total_usd (sec.gov); exit_events[0] (sec.gov); license_history[2].license (raw.githubusercontent.com) | none | – | low → **medium** |
| `E/atinary.json` | hq_country, still_operating, founded_year, openness_current | still_operating (ir.bruker.com) | hq_country: CH → US ([ir.bruker.com](https://ir.bruker.com/press-releases/press-release-details/2026/Bruker-Announces-Strategic-Collaboration-with-Atinary-Technologies-to-Advance-Self-Driving-Laboratories/default.aspx)) | founded_year; openness_current | low |
| `E/benchling.json` | founded_year, latest_value_usd, latest_value_date, funding_total_usd, risk_events[1] | founded_year (ycombinator.com); latest_value_usd (benchling.com); latest_value_date (benchling.com); funding_total_usd (benchling.com) | risk_events[1]: Nov 2021: filed Form S-1 with the SEC per Wikipedia; no IPO completed as of 2026 → Nov 2021: Wikipedia, citing a Reuters report from anonymous sources, says Benchling filed Form S-1, but SEC EDGAR lists no S-1 or DRS for Benchling, Inc. (CIK 1687403), only a 2016 Form D, so any filing was a confidential draft; no IPO as of 2026 ([data.sec.gov](https://data.sec.gov/submissions/CIK0001687403.json)) | – | low → **medium** |
| `E/chemify.json` | founded_year, funding_total_usd, still_operating, openness_current | still_operating (find-and-update.company-information.service.gov.uk) | founded_year: 2022 → 2019 ([find-and-update.company-information.service.gov.uk](https://find-and-update.company-information.service.gov.uk/company/SC645290)) | funding_total_usd; openness_current | low |
| `E/chemspeed.json` | founded_year, exit_events[0].year, exit_events[0].counterparty, still_operating | exit_events[0].year (sec.gov); exit_events[0].counterparty (chemspeed.com); still_operating (ir.bruker.com) | founded_year: null → 1997 ([chemspeed.com](https://www.chemspeed.com/about)) | – | low → **medium** |
| `E/citrine-informatics.json` | founded_year, funding_total_usd, openness_current | founded_year (sec.gov); openness_current (raw.githubusercontent.com) | none | funding_total_usd | medium |
| `E/cuspai.json` | founded_year, funding_total_usd, latest_value_usd | founded_year (en.wikipedia.org) | latest_value_usd: null → 2,600,000,000 ([cusp.ai](https://cusp.ai/blog/launching-our-ai-materials-foundry-and-450-million-series-b)); latest_value_type: null → private_valuation ([cusp.ai](https://cusp.ai/blog/launching-our-ai-materials-foundry-and-450-million-series-b)); latest_value_date: null → 2026-07 ([cusp.ai](https://cusp.ai/blog/launching-our-ai-materials-foundry-and-450-million-series-b)) | funding_total_usd | low → **medium** |
| `E/evolutionaryscale.json` | openness_initial, openness_current, relicensing_events[0].year, license_history[1].year, exit_events[0].counterparty, exit_events[0].year, funding_total_usd | openness_initial (raw.githubusercontent.com); openness_current (evolutionaryscale.ai); exit_events[0].counterparty (github.com) | relicensing_events[0].year: null → 2026 ([github.com](https://github.com/Biohub/esm/commits/main/LICENSE.md)); license_history[1].year: null → 2026 ([github.com](https://github.com/Biohub/esm/commits/main/LICENSE.md)) | exit_events[0].year; funding_total_usd | low |
| `E/isomorphic-labs.json` | founded_year, funding_total_usd, risk_events[0], risk_events[2], risk_events[3], relicensing_events[1].year, license_history[3].year, openness_current | founded_year (find-and-update.company-information.service.gov.uk); funding_total_usd (isomorphiclabs.com); risk_events[2] (en.wikipedia.org); risk_events[3] (en.wikipedia.org); openness_current (github.com) | risk_events[0]: Apr 2025: first external round, $600M led by Thrive Capital → 31 Mar 2025: first external round, $600M led by Thrive Capital ([isomorphiclabs.com](https://www.isomorphiclabs.com/articles/isomorphic-labs-announces-600m-external-investment-round)); relicensing_events[1].year: null → 2026 ([github.com](https://github.com/google-deepmind/alphafold3/commits/main/LICENSE)); license_history[3].year: null → 2026 ([github.com](https://github.com/google-deepmind/alphafold3/commits/main/LICENSE)) | – | medium → **high** |
| `E/kebotix.json` | founded_year, still_operating, funding_total_usd | – | founded_year: null → 2017 ([sec.gov](https://www.sec.gov/Archives/edgar/data/1749021/000174902118000001/primary_doc.xml)) | still_operating; funding_total_usd | low |
| `E/lila-sciences.json` | founded_year, risk_events[0], funding_total_usd, latest_value_usd | founded_year (generalcatalyst.com); risk_events[0] (generalcatalyst.com) | none | funding_total_usd; latest_value_usd | low |
| `E/orbital-materials.json` | license_history[0].license, license_history[0].year, founded_year, funding_total_usd | license_history[0].license (raw.githubusercontent.com); license_history[0].year (raw.githubusercontent.com) | none | founded_year; funding_total_usd | low |
| `E/periodic-labs.json` | founded_year, funding_total_usd, openness_current | founded_year (en.wikipedia.org); funding_total_usd (en.wikipedia.org) | none | openness_current | low → **medium** |
| `E/radical-ai.json` | funding_total_usd, openness_current, still_operating | openness_current (pypi.org); still_operating (pypi.org) | none | funding_total_usd | low |
| `E/recursion.json` | exit_events[0].year, exit_events[0].value_usd, risk_events[0], revenue_latest_usd, latest_value_usd | exit_events[0].year (sec.gov); risk_events[0] (sec.gov); revenue_latest_usd (sec.gov) | none | exit_events[0].value_usd; latest_value_usd | medium |
| `E/schrodinger.json` | founded_year, exit_events[0].year, revenue_latest_usd, risk_events[1], latest_value_usd | founded_year (schrodinger.com); exit_events[0].year (sec.gov); revenue_latest_usd (sec.gov); risk_events[1] (sec.gov) | none | latest_value_usd | medium |
| `F/enthought.json` | founded_year, hq_country, license_history[0].license, still_operating | founded_year (enthought.com); hq_country (github.com); license_history[0].license (github.com); still_operating (github.com) | none | – | low → **medium** |
| `F/rdkit.json` | founded_year, license_history[0].license, still_operating | founded_year (raw.githubusercontent.com); license_history[0].license (github.com); still_operating (api.github.com) | none | – | low → **medium** |

## Systematic problems

1. **Most facts rest on one page.**
   - 93 of the 122 files ran no WebSearch at all.
   - In 73 files, the only `sources` entry supporting `founded_year` is Wikipedia.
   - For private start-ups, the allowed source types (official pages, filings, registries,
     Wikipedia) often contain no second page at all. Funding figures could then be confirmed only
     against the company's own announcement, or not at all.
2. **`funding_total_usd` mixes three kinds of number:**
   - stated totals;
   - the researcher's sums of announced rounds: Benchling $406M, Isomorphic $7.7B, Formlabs
     $249M, Oxide $834M, Framework, Citrine $51.6M;
   - company lower bounds: CuspAI "over $650M".

   The sums undercount:
   - Formlabs' own releases imply at least $250M.
   - Citrine's Form D filings show $54.7M of equity sold by 2022.
   - Sofar's Form D filings show far more than $8.65M.

   A `funding_basis` field (stated / summed / lower bound) would make the difference visible.
3. **SEC Form D filings are an under-used primary source for US private companies.** In this pass
   they gave:
   - Kebotix's incorporation year;
   - Kebotix's 2023 and 2024 raises;
   - Citrine's later rounds;
   - Sofar's rounds;
   - the absence of a Benchling S-1.

   A Form D sweep would probably correct funding totals across groups A, B and E.
4. **"Latest" values are often stale or can't be checked.**
   - Seven private valuations labelled latest date from the 2021–22 peak: Cockroach Labs, Redis,
     Timescale, Airbyte, Automattic, Formlabs and Benchling.
   - 15 of the 17 market caps are dated November 2026 and come from StockAnalysis, which can't be
     checked against a primary page with WebFetch.
5. **Free text lags the numbers.** Where a value was filled, corrected or overtaken, the
   surrounding prose still says the old thing:
   - Chemify `notes` (2022);
   - Chemspeed `origin_detail` ("around 2001", against 1997);
   - Atinary `us_focus` and `origin_detail` (Swiss base);
   - EvolutionaryScale and Isomorphic `outcome_note` / `note` ("date not confirmed");
   - CuspAI `notes` and `risk_events` ("valuation not stated");
   - dbt Labs `name` (now Fivetran);
   - Kebotix `risk_events` and `robustness` ("dormant since 2022").

   This pass changed only values that a primary page contradicted, so the prose needs an
   editorial sweep.
6. **The same field is defined differently in different files.**
   - `founded_year` can mean the incorporation year, the public launch, when the idea was
     published, or the spin-out year:
     - Chemify: 2019 or 2022;
     - RepRap: 2004 or 2005;
     - Raspberry Pi: Wikipedia's date is when the company was renamed;
     - Formlabs: the company page says the Kickstarter was in 2011, the file says 2012.
   - IPO `value_usd` is the market cap on listing for Recursion, but null for Schrödinger even
     though its 424B4 gives the proceeds.

   Each field needs one convention.
7. **Some sources don't say what `supports` claims:**
   - OCP's licence pages: one returns 404, and the other now serves a 2024 revision that names
     different licences.
   - Benchling's "filed S-1" comes from Wikipedia citing anonymous sources.
   - Pine64's "$1.7M in Dec 2015": the cited article says $1.4M in Jan 2016.
   - Lila's valuation is a headline only.
   - Licence histories skip steps: EvolutionaryScale's Cambrian-licence period is missing, and
     AlphaFold 3's first LICENSE commit is Nov 2024, not the file's Feb 2025.
8. **Access limits shape what could be checked.**
   - reuters.com, openbci.com, kickstarter.com and flagshippioneering.com refuse WebFetch, and
     web.archive.org is blocked.
   - EDGAR's browse pages returned 503; the Archives and `data.sec.gov` routes worked.
   - Several confirmed `still_operating` values rest on recent activity (releases, commits, 2026
     press posts) rather than an explicit statement.

## Method

- **Tools.** WebFetch only. The session's WebSearch budget was exhausted and was not worked
  around: no search engines, browsers, proxies or Pi scripts.
- **Sources fetched:**
  - URLs already in the file;
  - Wikipedia;
  - organizations' own pages, press releases, GitHub repositories and package-registry pages;
  - investors' and acquirers' official announcements;
  - SEC EDGAR;
  - government company registries (UK Companies House, Hong Kong Companies Registry, UKRI
    Gateway to Research).

  The registries' own lookup forms, and EDGAR's company and full-text search, were used as
  registry lookups. No general web search was run.
- **Independence.** A fact counts as confirmed only if the page states the same value and is not
  the page already cited for that field in `sources`. A page cited for a different field was
  accepted. One exception is flagged in its file with `"independent": false`.
- **Changes.** A value was changed only when a primary or clearly authoritative page contradicted
  it; Wikipedia alone was never enough. Nulls were filled only from primary pages, never from
  memory. No fields were reordered or deleted, `sources` and `fetched_urls` were left as they
  were, and new URLs are listed in each block.
- **Confidence.**
  - It was raised one level only when at least two independent pages agree on the checked key
    facts and nothing is left contradicted.
  - The two medium → high raises (`D/sparkfun`, `E/isomorphic-labs`) also rest on primary pages
    and leave no checked fact unconfirmed.
  - No confidence was lowered.
- **Not regenerated.** `companies_master.csv`, `events.csv` and `CASEBOOK.md` were not rebuilt.
  Run `scripts/companies_aggregate.py` and `scripts/casebook.py` to pick up the changed values.
