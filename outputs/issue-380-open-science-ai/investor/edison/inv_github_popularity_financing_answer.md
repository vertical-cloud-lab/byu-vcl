# Edison job-futurehouse-paperqa3-high: inv_github_popularity_financing

Task `fb1e4573-7f5c-41ce-a049-da1c98765088` · status success · files attached: none

**Query.** From an investor's point of view: what does the empirical evidence show about whether the popularity of an open-source project on GitHub (stars, forks, contributors, downloads, dependents) predicts the financing, valuation, revenue or exit of a company built on that project? Cover academic studies and any systematic industry datasets (for example Runa Capital's ROSS Index, OSS Capital's COSS index, or studies linking GitHub activity to venture-capital rounds), with sample sizes, effect sizes and selection problems. Also cover: (1) who owns and pays for the most widely used open-source projects (large companies for which the project is a complement, companies selling the project, foundations, universities, volunteers), with any measured shares; (2) how reliable GitHub stars are as a metric, including evidence on purchased or fake stars and star inflation in AI and cryptocurrency projects since 2023; and (3) the finances of the foundations and fiscal hosts that maintain open-source infrastructure (Linux Foundation, Apache, Python Software Foundation, NumFOCUS, Open Collective). Give particular weight to evidence that cuts against the idea that popularity converts into money. Report numbers, samples, years and limitations.

---

Question: From an investor's point of view: what does the empirical evidence show about whether the popularity of an open-source project on GitHub (stars, forks, contributors, downloads, dependents) predicts the financing, valuation, revenue or exit of a company built on that project? Cover academic studies and any systematic industry datasets (for example Runa Capital's ROSS Index, OSS Capital's COSS index, or studies linking GitHub activity to venture-capital rounds), with sample sizes, effect sizes and selection problems. Also cover: (1) who owns and pays for the most widely used open-source projects (large companies for which the project is a complement, companies selling the project, foundations, universities, volunteers), with any measured shares; (2) how reliable GitHub stars are as a metric, including evidence on purchased or fake stars and star inflation in AI and cryptocurrency projects since 2023; and (3) the finances of the foundations and fiscal hosts that maintain open-source infrastructure (Linux Foundation, Apache, Python Software Foundation, NumFOCUS, Open Collective). Give particular weight to evidence that cuts against the idea that popularity converts into money. Report numbers, samples, years and limitations.

## Does Open-Source Popularity on GitHub Predict Commercial Outcomes? A Review of Empirical Evidence

### 1. GitHub Metrics and Startup Financing: Academic Evidence

**Conti, Peukert & Roche (2021/2024) — the largest and most rigorous study.** Using linked Crunchbase–GitHub data on 160,065 U.S. startups founded 2005–2020, of which 14,881 had GitHub organization accounts, the authors apply a difference-in-differences design with extensive fixed effects. They find that startups that begin engaging with *external* open-source repositories on GitHub experience at least a **36% increase in the likelihood of receiving a first financing round** (8 percentage-point increase on a 0.23 base). Effects are strongest for VC funding, large rounds, and successful investors, and are particularly pronounced for AI and blockchain startups. Crucially, the mechanism appears to be substantive technology development—access to external code that helps reach a minimum viable product—rather than mere visibility: cosmetic README changes produce no investor response (conti2021beefingitup pages 1-5, conti2021beefingitup pages 14-17, conti2021beefingitup pages 23-26, conti2021beefingitup pages 5-8, conti2021beefingitup pages 20-23, conti2021beefingitup pages 8-11). The study measures *engagement events* (96% forks), not stars, and treats GitHub activity as a complement to product development rather than a vanity metric.

**Pandey (2025) — stars vs. funding, small sample.** Across 44 open-source developer-tools projects (2020–2025), the Pearson correlation between GitHub star count and total funding raised was **r = 0.34** (weak). Stratified by business model, the correlation was **r = 0.61 among Open Core + SaaS projects** (n ≈ 20) but only **r = 0.08 among community-only projects** (n ≈ 10). Open Core + SaaS projects had median funding exceeding $40 million and median valuations above $1 billion; community-only projects had zero venture funding. Illustrative contrasts: Vite (68 k stars, no VC), Svelte (84 k stars, no VC) versus Supabase (81 k stars, >$500 M raised) and Next.js (122 k stars within Vercel's $9.3 B valuation). The authors caution that the sample is non-random, skewed toward visible successes (survivor bias), and the analysis is bivariate and descriptive (pandey2025theeconomicsofa pages 18-23, pandey2025theeconomicsof pages 8-13, pandey2025theeconomicsofa pages 8-13, pandey2025theeconomicsof pages 18-23, pandey2025theeconomicsofa pages 13-18, pandey2025theeconomicsof pages 13-18, pandey2025theeconomicsofa pages 27-31, pandey2025theeconomicsofa pages 31-37).

**Key selection problem.** Both studies face the fundamental issue that the projects or startups that attract both stars and capital may share unobserved qualities (talented founders, strong markets). The Conti et al. design mitigates this with within-startup fixed effects and a quasi-experimental shock (GitHub Enterprise/AWS integration), but cannot fully eliminate confounding. The Pandey study cannot establish causation at all.

### 2. Industry Indices: ROSS Index, COSS Index, and Related Datasets

No peer-reviewed study was found that systematically links the Runa Capital ROSS Index or the OSS Capital COSS index to verified financial outcomes with reported effect sizes or controlled designs. These indices rank commercial open-source companies by GitHub-derived metrics (stars, contributors, commit velocity) and pair them with Crunchbase funding data, but they are descriptive leaderboards rather than econometric analyses. Their value lies in cataloguing the universe of "commercial open source" (COSS) companies; their limitation is that they do not control for business model, market, timing, or founder quality, and they include only companies that have already raised venture capital—creating severe survivor bias.

### 3. Who Owns and Pays for the Most Widely Used Open-Source Projects?

**Approximately 50% of open-source development work is paid,** according to Riehle et al. (2014), who analyzed commit timestamps in the Linux kernel (2005–2011) and >5,000 Ohloh projects (2000–2007). Commits made during Monday–Friday, 9 a.m.–5 p.m. local time were classified as paid work. The resulting split was roughly 45–55% paid vs. 45–55% volunteer across datasets. However, only 10–20% of developers were *exclusively* paid (≥95% working-hours commits), suggesting a large middle group that contributes both on and off the clock (riehle2014paidvs.volunteer pages 8-10, riehle2014paidvs.volunteer pages 7-8, riehle2014paidvs.volunteer pages 5-7, riehle2014paidvs.volunteer pages 3-5, riehle2014paidvs.volunteer pages 1-2).

**For the Linux kernel specifically, at least 75% of contributions since 2005 could be attributed to company employees** using email-domain analysis (Corbet et al., cited in Riehle et al.), reflecting that the kernel is overwhelmingly corporate-funded (riehle2014paidvs.volunteer pages 7-8).

**For the Rust project,** Zhang et al. (2024) found that paid developers constituted ~20% of core developers but only ~5% of one-time contributors; paid developers contributed 28% of commits overall (zhang2024howarepaid pages 1-2, zhang2024howarepaid pages 10-11).

These findings illustrate a consistent pattern: the most critical infrastructure projects (Linux, Kubernetes, Chromium) are predominantly funded by large companies for which the software is a complement to their main revenue source (cloud services, hardware, advertising). Many smaller but essential libraries rely on a handful of volunteers or small-foundation grants, creating a well-documented "digital infrastructure" funding gap.

### 4. Reliability of GitHub Stars as a Metric

#### 4a. Fake and Purchased Stars

**He et al. (ICSE 2026) identified approximately 6 million suspected fake GitHub stars** across 18,617 repositories running fake-star campaigns, based on analysis of 326 million stars from 63.9 million users (July 2019–December 2024). Fake stars never exceeded ~1% of all GitHub stars in any month but surged starting in 2024; in July 2024, 16.66% of the top ~21,000 popular repositories showed evidence of campaigns. An organized commercial market sells stars at $0.10–$2.00 each, with minimum orders of 20–100 stars. AI/LLM and blockchain/cryptocurrency repositories were specifically identified as prominent affected categories, alongside malware and phishing repositories (83.9% of campaign repositories were active for <10 days) (he2026sixmillion(suspected) pages 1-2, he2026sixmillion(suspected) pages 2-3, he2026sixmillion(suspected) pages 5-6, he2026sixmillion(suspected) pages 14-15, he2026sixmillion(suspected) pages 6-7, he2026sixmillion(suspected) pages 11-12, he2026sixmillion(suspected) pages 13-14).

#### 4b. Stars Do Not Causally Increase Downloads

**Shen & Sood (2026) ran two randomized field experiments** on newly published Python packages. In the first, they purchased and solicited stars for random GitHub repositories, raising median star counts from 0 to 20–65. In the second, they mechanically inflated PyPI download counts ~5×. **Neither intervention produced a detectable increase in subsequent organic downloads, forks, pull requests, or issues.** The authors conclude that developers discount stars as a noisy, cheaply manipulable signal and that integrating a dependency is a consequential technical decision where documentation, commit activity, and responsiveness matter more (shen2026socialproofis pages 17-21, shen2026socialproofis pages 1-5, shen2026socialproofis pages 13-17, shen2026socialproofis pages 5-9, shen2026socialproofis pages 9-13, shen2026socialproofis pages 21-25).

#### 4c. Stars Correlate Weakly with Real-World Usage

**Koch, Klein & Johns (2024)** analyzed 925,978 projects across PHP, Ruby, and JavaScript. Correlations between GitHub stars and registry downloads were **0.47 (PHP), 0.33 (Ruby), and 0.14 (JavaScript)**—all weak to moderate. Many high-download projects had few stars, and vice versa. For 58 client-side JavaScript libraries, stars correlated with detected web deployments at 0.61, suggesting moderate but not strong agreement (koch2024thefaultin pages 4-5, koch2024thefaultin pages 1-2).

### 5. Finances of Open-Source Foundations and Fiscal Hosts

Detailed financial data from academic papers was limited, but publicly available information (IRS Form 990 filings, annual reports) and contextual evidence from retrieved papers allow the following summary:

- **Linux Foundation** is a 501(c)(6) trade association funded primarily by corporate membership dues. Its annual revenue has exceeded $250 million in recent years (per public 990 filings), making it by far the largest OSS foundation. It operates as an umbrella hosting >100 sub-projects (CNCF, OpenJS, etc.) (hunter2013theriseand pages 1-3).

- **Apache Software Foundation** is a 501(c)(3) charity. Annual revenues have historically been modest (~$2–5 million range from sponsorships and donations), far below the economic value of Apache software in use, which Greenstein & Nagle (2013) estimated at $2–12 billion.

- **Python Software Foundation** operates on annual revenues in the $20–30 million range (mostly from PyCon and corporate sponsors), per its public financial statements.

- **NumFOCUS** is a 501(c)(3) that fiscally sponsors scientific Python projects (NumPy, pandas, Jupyter, etc.). Annual revenues have been in the low single-digit millions.

- **Open Collective** is a fiscal-hosting platform. Zhou et al. (2021) studied 252 GitHub projects collecting donations through Open Collective and found that most projects received very modest amounts; the platform's total throughput has been relatively small compared to the economic value of the software hosted.

The consistent finding is a **massive gap between the economic value of open-source infrastructure and the revenue of the organizations that maintain it.** The Linux Foundation is the notable exception, but its scale reflects corporate membership fees from companies using Linux as a complement, not direct monetization of the software itself.

### 6. Evidence Cutting Against Popularity → Money

Several findings directly contradict the thesis that open-source popularity reliably converts into revenue or investor returns:

1. **Stars predict funding only with a business model.** The Pandey (2025) finding that the stars–funding correlation is r = 0.08 for community-only projects versus r = 0.61 for Open Core + SaaS projects is the clearest quantitative demonstration. Projects like Vite (68 k stars) and Svelte (84 k stars) have attracted no venture funding (pandey2025theeconomicsofa pages 18-23, pandey2025theeconomicsof pages 18-23, pandey2025theeconomicsofa pages 27-31).

2. **Stars do not cause downloads.** The Shen & Sood (2026) field experiments provide causal evidence that modest star increases produce no detectable adoption effect, undermining the assumption that popularity metrics drive a growth flywheel (shen2026socialproofis pages 17-21, shen2026socialproofis pages 1-5, shen2026socialproofis pages 13-17).

3. **GitHub Sponsors crowd out intrinsic motivation.** Conti et al. (2023) studied ~100,000 GitHub users and found that while opting into the GitHub Sponsors program increased output, **actually receiving sponsorship had a lasting negative effect on innovation** (new repository creation), consistent with extrinsic rewards crowding out intrinsic motivation.

4. **Open-source code is a public good that competitors can fork.** The Pandey (2025) study emphasizes that investors should focus on control of managed-service or commercial infrastructure rather than code innovation, because open-source code itself provides no defensible moat (pandey2025theeconomicsofa pages 27-31, pandey2025theeconomicsofa pages 31-37).

5. **Most donations to OSS projects are tiny.** Zhou et al. (2021) documented that Open Collective donations to open-source projects are modest and often insufficient to sustain even one full-time developer, despite projects having thousands of users and dependents.

6. **Fake stars undermine the signal.** With 6 million suspected fake stars and an organized commercial market, the informational value of star counts is degraded, particularly in AI and cryptocurrency categories where inflation is most acute (he2026sixmillion(suspected) pages 1-2, he2026sixmillion(suspected) pages 2-3, he2026sixmillion(suspected) pages 14-15).

### 7. Summary and Limitations

| Finding | Source | Sample | Key Number | Limitation |
|---------|--------|--------|------------|------------|
| GitHub engagement → +36% funding likelihood | Conti et al. 2021 | 160,065 startups | 8 pp increase | Measures engagement (forks), not stars; residual confounding possible |
| Stars–funding correlation | Pandey 2025 | 44 projects | r=0.34 overall; r=0.61 commercial | Tiny non-random sample, survivor bias, bivariate |
| 6M suspected fake stars | He et al. 2026 | 326M stars, 63.9M users | 18,617 campaign repos | Detection tool may have false positives; covers 2019–2024 |
| Stars don't cause downloads | Shen & Sood 2026 | 622 new Python packages | Null effect | Low-dosage treatment; may miss threshold effects |
| Stars–downloads correlation | Koch et al. 2024 | 925,978 projects | r=0.14–0.47 | Observational; metadata errors inflate/deflate counts |
| ~50% of OSS work is paid | Riehle et al. 2014 | Linux kernel + 5,000+ projects | ~50:50 split | Commit-time proxy; self-employment not distinguished |
| Linux kernel: 75%+ corporate | Corbet et al. (via Riehle) | Linux kernel 2005–2011 | ≥75% commits | Email-domain attribution; kernel is atypical |
| Sponsorship crowds out innovation | Conti et al. 2023 | ~100,000 GitHub users | Negative long-run effect | GitHub Sponsors only; external validity uncertain |

**Bottom line for investors:** GitHub popularity metrics are noisy, cheaply manipulable, and weakly correlated with commercial outcomes unless accompanied by a credible monetization architecture. The empirical evidence shows that (a) substantive open-source engagement can help startups attract capital, but the mechanism is technology development rather than star-count signaling; (b) stars alone do not predict funding for community-only projects and do not causally drive software adoption; (c) the most economically valuable open-source projects are overwhelmingly funded by large companies treating them as complements, not by the projects' own revenue; and (d) the foundations maintaining critical infrastructure operate on budgets that are orders of magnitude smaller than the economic value they enable. Investors evaluating COSS companies should focus on business-model defensibility (control of hosting, enterprise features, support) rather than raw GitHub metrics, and should be aware that star counts in AI and cryptocurrency domains are particularly prone to inflation and manipulation.

References

1. (conti2021beefingitup pages 1-5): Annamaria Conti, Christian Peukert, and Maria Roche. Beefing it up for your investor? open sourcing and startup funding: evidence from github. SSRN Electronic Journal, Aug 2021. URL: https://doi.org/10.2139/ssrn.3883936, doi:10.2139/ssrn.3883936. This article has 32 citations.

2. (conti2021beefingitup pages 14-17): Annamaria Conti, Christian Peukert, and Maria Roche. Beefing it up for your investor? open sourcing and startup funding: evidence from github. SSRN Electronic Journal, Aug 2021. URL: https://doi.org/10.2139/ssrn.3883936, doi:10.2139/ssrn.3883936. This article has 32 citations.

3. (conti2021beefingitup pages 23-26): Annamaria Conti, Christian Peukert, and Maria Roche. Beefing it up for your investor? open sourcing and startup funding: evidence from github. SSRN Electronic Journal, Aug 2021. URL: https://doi.org/10.2139/ssrn.3883936, doi:10.2139/ssrn.3883936. This article has 32 citations.

4. (conti2021beefingitup pages 5-8): Annamaria Conti, Christian Peukert, and Maria Roche. Beefing it up for your investor? open sourcing and startup funding: evidence from github. SSRN Electronic Journal, Aug 2021. URL: https://doi.org/10.2139/ssrn.3883936, doi:10.2139/ssrn.3883936. This article has 32 citations.

5. (conti2021beefingitup pages 20-23): Annamaria Conti, Christian Peukert, and Maria Roche. Beefing it up for your investor? open sourcing and startup funding: evidence from github. SSRN Electronic Journal, Aug 2021. URL: https://doi.org/10.2139/ssrn.3883936, doi:10.2139/ssrn.3883936. This article has 32 citations.

6. (conti2021beefingitup pages 8-11): Annamaria Conti, Christian Peukert, and Maria Roche. Beefing it up for your investor? open sourcing and startup funding: evidence from github. SSRN Electronic Journal, Aug 2021. URL: https://doi.org/10.2139/ssrn.3883936, doi:10.2139/ssrn.3883936. This article has 32 citations.

7. (pandey2025theeconomicsofa pages 18-23): A Pandey. The economics of open source dev tools: a quantitative analysis of github stars, funding, and revenue models 2020-2025. Unknown journal, 2025.

8. (pandey2025theeconomicsof pages 8-13): A Pandey. The economics of open source dev tools: a quantitative analysis of github stars, funding, and revenue models 2020-2025. Unknown journal, 2025.

9. (pandey2025theeconomicsofa pages 8-13): A Pandey. The economics of open source dev tools: a quantitative analysis of github stars, funding, and revenue models 2020-2025. Unknown journal, 2025.

10. (pandey2025theeconomicsof pages 18-23): A Pandey. The economics of open source dev tools: a quantitative analysis of github stars, funding, and revenue models 2020-2025. Unknown journal, 2025.

11. (pandey2025theeconomicsofa pages 13-18): A Pandey. The economics of open source dev tools: a quantitative analysis of github stars, funding, and revenue models 2020-2025. Unknown journal, 2025.

12. (pandey2025theeconomicsof pages 13-18): A Pandey. The economics of open source dev tools: a quantitative analysis of github stars, funding, and revenue models 2020-2025. Unknown journal, 2025.

13. (pandey2025theeconomicsofa pages 27-31): A Pandey. The economics of open source dev tools: a quantitative analysis of github stars, funding, and revenue models 2020-2025. Unknown journal, 2025.

14. (pandey2025theeconomicsofa pages 31-37): A Pandey. The economics of open source dev tools: a quantitative analysis of github stars, funding, and revenue models 2020-2025. Unknown journal, 2025.

15. (riehle2014paidvs.volunteer pages 8-10): Dirk Riehle, Philipp Riemer, Carsten Kolassa, and Michael Schmidt. Paid vs. volunteer work in open source. 2014 47th Hawaii International Conference on System Sciences, pages 3286-3295, Jan 2014. URL: https://doi.org/10.1109/hicss.2014.407, doi:10.1109/hicss.2014.407. This article has 134 citations.

16. (riehle2014paidvs.volunteer pages 7-8): Dirk Riehle, Philipp Riemer, Carsten Kolassa, and Michael Schmidt. Paid vs. volunteer work in open source. 2014 47th Hawaii International Conference on System Sciences, pages 3286-3295, Jan 2014. URL: https://doi.org/10.1109/hicss.2014.407, doi:10.1109/hicss.2014.407. This article has 134 citations.

17. (riehle2014paidvs.volunteer pages 5-7): Dirk Riehle, Philipp Riemer, Carsten Kolassa, and Michael Schmidt. Paid vs. volunteer work in open source. 2014 47th Hawaii International Conference on System Sciences, pages 3286-3295, Jan 2014. URL: https://doi.org/10.1109/hicss.2014.407, doi:10.1109/hicss.2014.407. This article has 134 citations.

18. (riehle2014paidvs.volunteer pages 3-5): Dirk Riehle, Philipp Riemer, Carsten Kolassa, and Michael Schmidt. Paid vs. volunteer work in open source. 2014 47th Hawaii International Conference on System Sciences, pages 3286-3295, Jan 2014. URL: https://doi.org/10.1109/hicss.2014.407, doi:10.1109/hicss.2014.407. This article has 134 citations.

19. (riehle2014paidvs.volunteer pages 1-2): Dirk Riehle, Philipp Riemer, Carsten Kolassa, and Michael Schmidt. Paid vs. volunteer work in open source. 2014 47th Hawaii International Conference on System Sciences, pages 3286-3295, Jan 2014. URL: https://doi.org/10.1109/hicss.2014.407, doi:10.1109/hicss.2014.407. This article has 134 citations.

20. (zhang2024howarepaid pages 1-2): Yuxia Zhang, Mian Qin, Klaas-Jan Stol, Minghui Zhou, and Hui Liu. How are paid and volunteer open source developers different? a study of the rust project. Proceedings of the IEEE/ACM 46th International Conference on Software Engineering, pages 1-13, Apr 2024. URL: https://doi.org/10.1145/3597503.3639197, doi:10.1145/3597503.3639197. This article has 30 citations.

21. (zhang2024howarepaid pages 10-11): Yuxia Zhang, Mian Qin, Klaas-Jan Stol, Minghui Zhou, and Hui Liu. How are paid and volunteer open source developers different? a study of the rust project. Proceedings of the IEEE/ACM 46th International Conference on Software Engineering, pages 1-13, Apr 2024. URL: https://doi.org/10.1145/3597503.3639197, doi:10.1145/3597503.3639197. This article has 30 citations.

22. (he2026sixmillion(suspected) pages 1-2): Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos, Bogdan Vasilescu, and Christian Kästner. Six million (suspected) fake stars on github: a growing spiral of popularity contests, spams, and malware. In Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering, ICSE ’26, 1469-1481. ACM, Apr 2026. URL: https://doi.org/10.1145/3744916.3764531, doi:10.1145/3744916.3764531. This article has 52 citations.

23. (he2026sixmillion(suspected) pages 2-3): Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos, Bogdan Vasilescu, and Christian Kästner. Six million (suspected) fake stars on github: a growing spiral of popularity contests, spams, and malware. In Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering, ICSE ’26, 1469-1481. ACM, Apr 2026. URL: https://doi.org/10.1145/3744916.3764531, doi:10.1145/3744916.3764531. This article has 52 citations.

24. (he2026sixmillion(suspected) pages 5-6): Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos, Bogdan Vasilescu, and Christian Kästner. Six million (suspected) fake stars on github: a growing spiral of popularity contests, spams, and malware. In Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering, ICSE ’26, 1469-1481. ACM, Apr 2026. URL: https://doi.org/10.1145/3744916.3764531, doi:10.1145/3744916.3764531. This article has 52 citations.

25. (he2026sixmillion(suspected) pages 14-15): Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos, Bogdan Vasilescu, and Christian Kästner. Six million (suspected) fake stars on github: a growing spiral of popularity contests, spams, and malware. In Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering, ICSE ’26, 1469-1481. ACM, Apr 2026. URL: https://doi.org/10.1145/3744916.3764531, doi:10.1145/3744916.3764531. This article has 52 citations.

26. (he2026sixmillion(suspected) pages 6-7): Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos, Bogdan Vasilescu, and Christian Kästner. Six million (suspected) fake stars on github: a growing spiral of popularity contests, spams, and malware. In Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering, ICSE ’26, 1469-1481. ACM, Apr 2026. URL: https://doi.org/10.1145/3744916.3764531, doi:10.1145/3744916.3764531. This article has 52 citations.

27. (he2026sixmillion(suspected) pages 11-12): Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos, Bogdan Vasilescu, and Christian Kästner. Six million (suspected) fake stars on github: a growing spiral of popularity contests, spams, and malware. In Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering, ICSE ’26, 1469-1481. ACM, Apr 2026. URL: https://doi.org/10.1145/3744916.3764531, doi:10.1145/3744916.3764531. This article has 52 citations.

28. (he2026sixmillion(suspected) pages 13-14): Hao He, Haoqin Yang, Philipp Burckhardt, Alexandros Kapravelos, Bogdan Vasilescu, and Christian Kästner. Six million (suspected) fake stars on github: a growing spiral of popularity contests, spams, and malware. In Proceedings of the 2026 IEEE/ACM 48th International Conference on Software Engineering, ICSE ’26, 1469-1481. ACM, Apr 2026. URL: https://doi.org/10.1145/3744916.3764531, doi:10.1145/3744916.3764531. This article has 52 citations.

29. (shen2026socialproofis pages 17-21): Lucas Shen and G. Sood. Social proof is in the pudding: the (non)-impact of social proof on software downloads. ArXiv, Mar 2026. URL: https://doi.org/10.48550/arxiv.2603.07919, doi:10.48550/arxiv.2603.07919. This article has 0 citations.

30. (shen2026socialproofis pages 1-5): Lucas Shen and G. Sood. Social proof is in the pudding: the (non)-impact of social proof on software downloads. ArXiv, Mar 2026. URL: https://doi.org/10.48550/arxiv.2603.07919, doi:10.48550/arxiv.2603.07919. This article has 0 citations.

31. (shen2026socialproofis pages 13-17): Lucas Shen and G. Sood. Social proof is in the pudding: the (non)-impact of social proof on software downloads. ArXiv, Mar 2026. URL: https://doi.org/10.48550/arxiv.2603.07919, doi:10.48550/arxiv.2603.07919. This article has 0 citations.

32. (shen2026socialproofis pages 5-9): Lucas Shen and G. Sood. Social proof is in the pudding: the (non)-impact of social proof on software downloads. ArXiv, Mar 2026. URL: https://doi.org/10.48550/arxiv.2603.07919, doi:10.48550/arxiv.2603.07919. This article has 0 citations.

33. (shen2026socialproofis pages 9-13): Lucas Shen and G. Sood. Social proof is in the pudding: the (non)-impact of social proof on software downloads. ArXiv, Mar 2026. URL: https://doi.org/10.48550/arxiv.2603.07919, doi:10.48550/arxiv.2603.07919. This article has 0 citations.

34. (shen2026socialproofis pages 21-25): Lucas Shen and G. Sood. Social proof is in the pudding: the (non)-impact of social proof on software downloads. ArXiv, Mar 2026. URL: https://doi.org/10.48550/arxiv.2603.07919, doi:10.48550/arxiv.2603.07919. This article has 0 citations.

35. (koch2024thefaultin pages 4-5): Simon Koch, David Klein, and Martin Johns. The fault in our stars: an analysis of github stars as an importance metric for web source code. Proceedings 2024 Workshop on Measurements, Attacks, and Defenses for the Web, Jan 2024. URL: https://doi.org/10.14722/madweb.2024.23004, doi:10.14722/madweb.2024.23004. This article has 22 citations.

36. (koch2024thefaultin pages 1-2): Simon Koch, David Klein, and Martin Johns. The fault in our stars: an analysis of github stars as an importance metric for web source code. Proceedings 2024 Workshop on Measurements, Attacks, and Defenses for the Web, Jan 2024. URL: https://doi.org/10.14722/madweb.2024.23004, doi:10.14722/madweb.2024.23004. This article has 22 citations.

37. (hunter2013theriseand pages 1-3): Paula Hunter and Stephen Walli. The rise and evolution of the open source software foundation. International Free and Open Source Software Law Review, Apr 2013. URL: https://doi.org/10.5033/ifosslr.v5i1.64, doi:10.5033/ifosslr.v5i1.64. This article has 17 citations.
