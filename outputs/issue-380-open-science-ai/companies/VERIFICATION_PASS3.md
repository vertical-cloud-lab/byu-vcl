# Verification pass 3: the 46 facts pass 2 left unconfirmed (2026-11-24)

## Method

Pass 2 ([`VERIFICATION_PASS2.md`](VERIFICATION_PASS2.md)) left 46 facts unconfirmed, listed in the `verification_pass2.unconfirmed` blocks of the case files. This pass tried each one again with WebFetch only. No web search was run: the session's search budget was spent, and it was not worked around with search engines, browsers, proxies or the repo's Pi scripts. Pages fetched were organizations' own sites and GitHub orgs, investor and acquirer posts, a government registry (UK Companies House), Wikipedia in several languages, and news pages whose URLs were known or linked from a fetched page. The independence rule is the same as in pass 2. A fact counts as confirmed only if a page states the same value and is not the page already cited for that field. Funding totals count if they are within about 10%, or if one page states the rounds that make up the total. A fact counts as contradicted only if a primary or clearly authoritative page states a different value. Wikipedia can confirm but cannot alone contradict. For `openness_current` the licence facts were checked, not the score. No case file, CSV or other Markdown file was changed. The results are in [`../data/verification_pass3.csv`](../data/verification_pass3.csv), with a quote or a note of what was tried for each fact.

## Results

| Status | Facts |
| --- | ---: |
| confirmed | 14 |
| contradicted | 2 |
| still unconfirmed | 30 |
| not attempted | 0 |
| total | 46 |

### Confirmed

- `B/dbt-labs.json` `founded_year` = 2016: [https://www.sequoiacap.com/companies/dbt-labs/](https://www.sequoiacap.com/companies/dbt-labs/), "Founded 2016"
- `B/dbt-labs.json` `latest_value_usd` = 4200000000: [https://www.getdbt.com/blog/next-layer-of-the-modern-data-stack/](https://www.getdbt.com/blog/next-layer-of-the-modern-data-stack/), "dbt Labs raised another round of funding– $222m at $4.2b valuation."
- `D/arduino.json` `ownership_status` = acquired: [https://www.arduino.cc/qualcomm/](https://www.arduino.cc/qualcomm/), "We are excited to announce that we are now part of the Qualcomm family!"
- `D/arduino.json` `founded_year` = 2005: [https://it.wikipedia.org/wiki/Arduino_(hardware)](https://it.wikipedia.org/wiki/Arduino_(hardware)), "Il progetto prese avvio nel 2005 presso l'Interaction Design Institute di Ivrea"
- `D/lulzbot-aleph-objects.json` `exit_events[0].year` = 2019: [https://www.tctmagazine.com/aleph-objects-finds-buyer-3d-printing-lulzbot/](https://www.tctmagazine.com/aleph-objects-finds-buyer-3d-printing-lulzbot/), "Aleph Objects, the manufacturer behind the open source LulzBot 3D printer brand, has been acquired by Fargo Additive Manufacturing Equipment (FAME 3D). [November 11, 2019]"
- `D/open-compute-project.json` `license_history[1].license` = OCP IP policy: contributions under OCP CLA or OWF CLA; Specification License = OCP Hardware License (permissive or reciprocal) or OWFa 1.0: [https://www.opencompute.org/contributions/templates-agreements](https://www.opencompute.org/contributions/templates-agreements), "OCP-CLA"; "Hardware License OCPHL-R Option"; "Hardware License OCPHL-P Option"; "Modified OWF-CLA-1.0"; "Modified OWFa1.0 Final Specification Agreement (FSA)" (listed as archived)
- `D/pine64.json` `founded_year` = 2015: [https://fr.wikipedia.org/wiki/Pine64](https://fr.wikipedia.org/wiki/Pine64), "Entreprise fondée en 2015"
- `D/pine64.json` `funding_total_usd` = 1700000: [https://de.wikipedia.org/wiki/Pine64](https://de.wikipedia.org/wiki/Pine64), "bei der über 1,7 Millionen US-Dollar gesammelt wurden"
- `D/raspberry-pi.json` `latest_value_usd` = 1186000000: [https://companiesmarketcap.com/raspberry-pi/marketcap/](https://companiesmarketcap.com/raspberry-pi/marketcap/), "As of November 2026 Raspberry Pi has a market cap of $1.18 Billion USD."
- `D/system76.json` `founded_year` = 2005: [https://fr.wikipedia.org/wiki/System76](https://fr.wikipedia.org/wiki/System76), "Création: 7 novembre 2005"
- `D/system76.json` `relicensing_events[1].year` = 2021: [https://www.gamingonlinux.com/2021/05/system76-releases-the-open-source-launch-configurable-keyboard/](https://www.gamingonlinux.com/2021/05/system76-releases-the-open-source-launch-configurable-keyboard/), "Sticking to their ethos, they've launched the Launch as a fully open source unit. [...] This includes the hardware [13 May 2021]"
- `E/chemify.json` `funding_total_usd` = 93000000: [https://european-biotechnology.com/latest-news/zeon-invests-in-chemify-to-cut-compound-synthesis-time-using-ai-and-robotics/](https://european-biotechnology.com/latest-news/zeon-invests-in-chemify-to-cut-compound-synthesis-time-using-ai-and-robotics/), "The startup raised a $50 million Series B round in October, adding to the $43 million Series A round it closed in 2023."
- `E/recursion.json` `latest_value_usd` = 1660000000: [https://companiesmarketcap.com/recursion-pharmaceuticals/marketcap/](https://companiesmarketcap.com/recursion-pharmaceuticals/marketcap/), "As of November 2026 Recursion Pharmaceuticals has a market cap of $1.66 Billion USD."
- `E/schrodinger.json` `latest_value_usd` = 1830000000: [https://companiesmarketcap.com/schrodinger/marketcap/](https://companiesmarketcap.com/schrodinger/marketcap/), "As of November 2026 Schrödinger has a market cap of $1.83 Billion USD."

Notes on the confirmations:

- The three `latest_value_usd` market caps (Raspberry Pi, Recursion, Schrödinger) are confirmed by companiesmarketcap.com, a second aggregator independent of the cited StockAnalysis. For Recursion it also shows Nasdaq's figure of $1.65B for 2026-11-23. No primary page gives a dated market cap.
- Arduino: the arduino.cc home page banner also reads "Arduino is now a Qualcomm company." Neither page gives a closing date, so the acquisition's completion date is still unknown.
- Arduino `founded_year`, Pine64 `funding_total_usd` and `founded_year`, and System76 `founded_year` rest on Italian, German and French Wikipedia. These are secondary sources, but they are different pages from the cited English articles. The Pine64 founding year is the weakest of them: French Wikipedia states it only as a category label ("Entreprise fondée en 2015"), and its infobox gives no date. Like the English infobox, it may share an upstream source rather than add an independent one.
- Open Compute Project: OCP's templates and agreements page lists the OCP-CLA, the OCPHL-R and OCPHL-P hardware licence options, the Modified OWF-CLA-1.0 and the Modified OWFa 1.0 agreement. It marks all of them as archived or deprecated. The archived OCP-CLA is dated 2019-03-01 and the OWF versions 2021-08-16. The current agreement for specifications and designs is "OWF CLA 0.9". This confirms the licence terms in `license_history[1]` but not its 2015 date. The file has no entry yet for the move to OWF CLA 0.9.
- Chemify: the page gives the $43M Series A and the $50M Series B in one sentence. It adds that Zeon's 2026 investment was undisclosed, so $93M is still a lower bound.
- dbt Labs `latest_value_usd`: dbt Labs' own Series D post (2022-02-24) gives "$222m at $4.2b valuation". The cited Contrary page links to it, but it is a separate, primary page. The $414M total still has no page: Contrary sources it to Crunchbase, which returned 403.
- LulzBot: TCT Magazine's article of 11 November 2019 is one of the cited Wikipedia article's references. 3D Printing Industry's article of the same day says the same: "all of its assets have been acquired by Fargo Additive Manufacturing Equipment 3D (FAME 3D)".
- System76 Launch: GamingOnLinux (13 May 2021) says the keyboard launched "as a fully open source unit", hardware included, with an "Open Source PCB design" and "Open Source milled chassis design". Pass 2 found the system76/launch repository was created on 2019-12-05, so some files may have been visible earlier. 2021 is the year of the open release.

## Contradicted facts

| File | Field | Value in file → proposed | Source |
| --- | --- | --- | --- |
| `E/atinary.json` | `openness_current` | 0 → 1 | [https://github.com/Atinary-technologies](https://github.com/Atinary-technologies) ; [https://api.github.com/orgs/atinary-technologies/repos?per_page=100](https://api.github.com/orgs/atinary-technologies/repos?per_page=100) |
| `E/orbital-materials.json` | `founded_year` | null → 2022 | [https://find-and-update.company-information.service.gov.uk/company/14332843](https://find-and-update.company-information.service.gov.uk/company/14332843) ; [https://www.orbitalindustries.com/privacy-policy](https://www.orbitalindustries.com/privacy-policy) |

- **Atinary `openness_current`: 0 → 1.** Pass 2 found no GitHub org at `github.com/atinary`. The org is `github.com/Atinary-technologies`, named "Atinary Technologies" and linking to www.atinary.com. It is described as "AI/ML platform to digitize R&D operations and enable self-driving labs". It has seven public repositories, none of them forks. `sdlabs_wrapper` (MIT, 2023) is a wrapper "used for quick usage of SDLabs for optimization purposes". `chem-MFBO` (MIT, 2024) and `monorepo_template` (MIT, 2026) are also there. `phoenics` (2019), `experiment_planning_plugins` (2020) and `gryffin` (2021) are under Apache-2.0. `nexus_sdk` has a non-standard licence. The file's note says that Phoenics and Gryffin are "not mentioned or claimed by the company". But the company hosts them itself. SDLabs remains proprietary SaaS. On the rubric, "only peripheral SDKs/clients open" is level 1.
- **Orbital Materials `founded_year`: null → 2022.** Pass 2 found ORBITAL MATERIALS LTD (14332843, incorporated 2 September 2022), but no company page tied that entity to Orbital. Orbital's own privacy policy now does. It names "Orbital Materials Ltd", "Company Number 14332843", at the same 10 John Street address. It also names "Orbital Materials, Inc." at El Segundo, California, whose incorporation date is still unknown. If the US entity is older, the founding year could be earlier. This fills a null rather than correcting a wrong value.

## Still unconfirmed

- `B/dbt-labs.json` `funding_total_usd` (414000000). Tried: dbt's Series D post (2022-02-24; $222m round, no total); Sequoia company page and getdbt.com/about-us (no amounts); Crunchbase and Forbes pages linked from Contrary (both 403); en.wikipedia Dbt_Labs and variants (404).
- `B/prefect.json` `funding_total_usd` (null). Tried: en.wikipedia Prefect_(software) (404). No new official page found; pass 2 found no funding post in prefect.io's sitemap.
- `D/adafruit.json` `funding_total_usd` (0). Tried: en.wikipedia Limor_Fried and Phillip_Torrone (silent on funding); the Business Insider article Wikipedia cites ('...without a dime of funding', 2015) could not be fetched.
- `D/creality.json` `exit_events[0].year` (2026). Tried: creality.com/investor-relations (no exchange, stock code or date); HKEX Newly Listed Securities page (covers 9-25 Nov 2026 only; Creality absent).
- `D/creality.json` `exit_events[0].counterparty` (Hong Kong Stock Exchange (HKEX)). Tried: creality.com/investor-relations shows only 'Global Offering' and 'Announcements & Circulars' menu labels, no exchange name or stock code.
- `D/creality.json` `relicensing_events[0].year` (2018). Tried: creality.com Ender-3 product page; no text about open-sourcing or a year.
- `D/formlabs.json` `funding_total_usd` (249000000). Tried: formlabs.com/company gives only 'achieved a $2 billion dollar valuation' and investor logos, no amount; de.wikipedia Formlabs (404).
- `D/framework-computer.json` `funding_total_usd` (45225000). Tried: fr.wikipedia Framework_Computer gives the $9M round (H1 2021), the $18M Series A and Linus Sebastian's 224 998,37 USD, but no Series A-1 and no total; de and es.wikipedia (404).
- `D/openbci.json` `founded_year` (2013). Tried: Kickstarter campaign page (403); openbci.com/about (403); en.wikipedia Conor_Russomanno (no year); de.wikipedia OpenBCI (404).
- `D/openbci.json` `openness_current` (2). Tried: galea.co (403); OpenBCI's 'Introducing: Galea' post (403); en.wikipedia Conor_Russomanno (does not mention Galea). No page states Galea's licence.
- `D/openbci.json` `relicensing_events[0].year` (2020). Tried: same pages as openness_current; nothing dates a licence change.
- `D/oxide-computer.json` `funding_total_usd` (834000000). Tried: oxide.computer/press, Counterpart and Eclipse Series D posts, The Next Web (no total stated); Forbes (403); en.wikipedia Oxide_Computer_Company (404).
- `D/pine64.json` `relicensing_events[0].year` (2026). Tried: pine64.org/blog/ only repeats the cited post's excerpt (Jul 25, 2026); no independent page found.
- `D/raspberry-pi.json` `exit_events[0].value_usd` (689000000). Tried: en.wikipedia Raspberry_Pi_Foundation ('The sale raised £136 million to fund the endowment', no valuation) and Raspberry_Pi (no price); raspberrypi.com IPO post (404); Elektor IPO article (403).
- `D/sofar-ocean-openrov.json` `funding_total_usd` (8650000). Tried: en.wikipedia Sofar_Ocean (404); ted.com/speakers/david_lang (no funding).
- `D/sofar-ocean-openrov.json` `founded_year` (2011). Tried: TED speaker page (2010 search for lost gold, then 'Soon OpenROV was born', undated); fr.wikipedia OpenROV (prototype 'présenté en 2011' at World Maker Faire, no founding year); en.wikipedia Eric_Stackpole (404).
- `E/atinary.json` `founded_year` (null). Tried: Atinary's GitHub org (oldest repo, phoenics, created 2019-10-31; no founding year).
- `E/chemify.json` `openness_current` (0). Tried: European Biotechnology (no licensing statement); tech.eu (403); cen.acs.org (406); endpoints.news (403); en.wikipedia Chemify (404).
- `E/citrine-informatics.json` `funding_total_usd` (51600000). Tried: en.wikipedia Citrine_Informatics (404). No page states a total.
- `E/cuspai.json` `funding_total_usd` (650000000). Tried: cusp.ai/blog lists $30M, '$100M+ Series A' and '$450 million Series B' (at least $580M) but no total; cusp.ai/news and en.wikipedia CuspAI (404).
- `E/evolutionaryscale.json` `exit_events[0].year` (null). Tried: repo now under Biohub/esm, README says 'our API migrated from forge.evolutionaryscale.ai to biohub.ai' (undated); biohub.ai, en.wikipedia Chan_Zuckerberg_Biohub (silent); biohub.org/about, evolutionaryscale.ai/blog, en.wikipedia EvolutionaryScale (404).
- `E/evolutionaryscale.json` `funding_total_usd` (142000000). Tried: en.wikipedia EvolutionaryScale (404); no investor or company page with the amount found.
- `E/kebotix.json` `still_operating` (null). Tried: kebotix.com/news (latest dated item 2022; only 2026 sign is the footer '© 2026 Kebotix, Inc.').
- `E/kebotix.json` `funding_total_usd` (null). Tried: kebotix.com/news (SIT Capital and ArcTern investment items, no amounts). No page states a total.
- `E/lila-sciences.json` `funding_total_usd` (550000000). Tried: lila.ai/news (the cited page) only; its own post says 'bringing total funding to $550M'. No independent page reachable (Reuters blocked).
- `E/lila-sciences.json` `latest_value_usd` (1300000000). Tried: lila.ai/news lists only the Reuters headline 'tops $1.3 billion valuation'; Reuters cannot be fetched.
- `E/orbital-materials.json` `funding_total_usd` (null). Tried: orbitalindustries.com/news (no funding items) and privacy policy (no amounts).
- `E/periodic-labs.json` `openness_current` (0). Tried: github.com/periodiclabs, huggingface.co/periodic-labs, en.wikipedia Periodic_Labs (all 404). Absence fits 0 but no page states it.
- `E/radical-ai.json` `funding_total_usd` (55000000). Tried: radical-ai.com/news repeats the cited post's headline 'Radical AI announces $55M in new funding' (not independent); no investors named.
- `E/recursion.json` `exit_events[0].value_usd` (2920000000). Tried: en.wikipedia Recursion_Pharmaceuticals (404). No page states a market cap at the IPO.
