# Recharge Model Exploration — Vertical Cloud Lab (BYU)

> **Issue:** [Explore recharge model for vertical cloud lab](../../issues) (placeholder link to the originating issue).
>
> **Status:** Exploratory background research — not policy. This document collects
> best-practice guidance and prior art to inform the design of a recharge / cost-
> recovery model for the BYU Vertical Cloud Lab (VCL), with particular attention to
> a metal additive-manufacturing (laser powder-bed fusion of AlSi10Mg / aluminum)
> shared facility offered as a service to internal academic and external industrial
> users.
>
> **Provenance:** The technical synthesis below was generated via an automated
> literature search using the Edison Scientific (FutureHouse PaperQA) platform on
> 2026-05-15. All factual claims carry inline citations to the underlying sources
> (numbered references at the end). The wording is preserved verbatim from the
> tool output so that citations remain verifiable; this file should be reviewed
> and adapted by VCL leadership before being treated as authoritative.

---

## Original research question

> What are best practices and common structures for designing a recharge model
> (also called a recharge center or service-center cost-recovery model) for a
> university research laboratory or shared core facility, particularly one
> offering additive manufacturing (e.g., metal 3D printing / laser powder-bed
> fusion of AlSi10Mg and aluminum) as a service to internal academic users and
> external / industry users? Address: federal compliance (Uniform Guidance
> 2 CFR 200, OMB A-21 / A-110), rate-setting methodology, allowable vs.
> unallowable costs, depreciation / equipment recovery, internal vs. external
> user pricing, subsidies, break-even analysis, annual rate review and
> carry-forward of surplus / deficit, and examples from vertically integrated
> lab or "cloud lab" models.

---

### Technical guidance: designing a university recharge/service-center model for an additive manufacturing (metal LPBF) core facility

#### 1. Compliance framework (Uniform Guidance, legacy OMB circulars, CAS/DS-2)
University service/recharge centers exist in a regulated space because internal users frequently pay with federal funds; therefore, core facilities should assume federal dollars are involved unless proven otherwise. (hockberger2013bestpracticesfor pages 4-6)

Legacy OMB Circular A-21 (2 CFR Part 220) and, since 2014, its successor Uniform Guidance provision at 2 CFR 200.468 (Specialized Service Facilities) are the primary federal cost-accounting anchors, but they historically provided limited operational detail for many academic fee-for-service cores (beyond a subset of “specialized service centers” such as animal care and computer centers), creating a documented policy gap that led NIH/ABRF to develop additional community guidance. (hockberger2026abrfcoreadministrators pages 1-2)

For institutions subject to Cost Accounting Standards, CAS disclosure statements (DS-2) document how the institution defines and allocates costs for service centers and specialized service centers; e.g., University of Colorado Boulder defines a “specialized service center” as a complex/specialized facility with ≥$1M operating expenditures and responsibility for its own building, and states that such centers are allocated their full share of F&A costs. (ds2015costaccountingstandardsa pages 37-39)

#### 2. Fundamental structural principle: “rate-at-cost” with non-discrimination
A compliant recharge model is fundamentally a cost allocation mechanism, not a profit center. Institutional recharge policies typically require rates to be set at actual cost and adjusted to achieve break-even over the center’s normal operating cycle, with fund balances (surplus/deficit) carried forward and corrected via future rate changes. (centerUnknownyearno.b01page pages 1-4, centerUnknownyearno.b01page pages 4-7)

Charges to federal awards must be reasonable, based on actual use, not exceed cost, and must not discriminate between federal and nonfederal activities. (centerUnknownyearno.b01page pages 1-4)

Core-facility best-practice literature similarly cautions that setting rates using an unjustifiable utilization estimate can cause underrecovery or creation of a profit, increasing audit risk; the utilization estimate should be “reasonable and justifiable.” (otoole2024aperspectiveinto pages 4-5)

#### 3. Rate-setting methodology (cost pool → unit rate)
**Common structure**
1) Define services and billing units that are auditable (e.g., per hour, per run, per sample, per procedure). (centerUnknownyearno.b01page pages 15-20, otoole2024aperspectiveinto pages 4-4)
2) Build a cost pool composed of allowable and allocable costs (direct costs plus permitted depreciation/use allowances and any approved indirect components). (centerUnknownyearno.b01page pages 4-7, centerUnknownyearno.b01page pages 10-15)
3) Forecast billable units using historical activity, staffing availability, expected efficiency changes, downtime, and documented assumptions; include best/worst-case variance planning. (centerUnknownyearno.b01page pages 10-15, centerUnknownyearno.b01page pages 15-20)
4) Compute the internal base rate as recoverable costs divided by projected billable units, incorporating approved prior-year carryforward adjustments and explicit subsidies where applicable. (centerUnknownyearno.b01page pages 10-15)

**Illustrative institutional “workbook” expectations**
A representative university recharge-center manual requires annual submission of rate proposals that include three-year proforma income statements, schedules of proposed rates/markups, projected income tied to forecasted activity levels, and an explicit description of variance and how excess/deficit will be accommodated. (centerUnknownyearno.b01page pages 10-15)

The same manual provides an explicit hourly-rate method: estimate billable hours from historical data and trends; estimate recoverable costs (wages, benefits/leave, travel, contractual services, equipment allowances); then divide to derive an hourly billing rate. (centerUnknownyearno.b01page pages 15-20)

**Efficient utilization and pricing stability**
Core-facility literature recommends basing rates on efficient usage, potentially using multi-year averages, and maintaining auditable usage records through robust booking/work-order systems. (otoole2024aperspectiveinto pages 4-4)

Pooling or bundling similar instruments to compute a blended hourly rate can stabilize pricing, reduce the risk that older equipment becomes “too expensive,” and allow immediate inclusion of new instruments. (otoole2024aperspectiveinto pages 5-5)

#### 4. Allowable vs. unallowable costs (and how to operationalize them)
Recharge rates should include only allowable/allocable costs under federal cost principles; core-facility external-customer guidance provides concrete examples of unallowable direct costs when charging federal grants, including debt principal/internal interest, advertising, alcoholic beverages, bad debts, contributions, entertainment, fundraising, and public relations. (hockberger2013bestpracticesfor pages 4-6)

Institutional recharge policies typically operationalize this by requiring costs unallowable under OMB A-21 (2 CFR Part 220) to be charged to an unrestricted fund rather than recovered through recharge rates. (centerUnknownyearno.b01page pages 4-7)

At the institution-wide level, DS-2 documents how unallowable costs and “directly associated” unallowable costs are excluded from direct charging and handled in F&A development (e.g., reclassified to unallowable pools and excluded from allocation bases). (ds2015costaccountingstandards pages 11-14)

#### 5. Depreciation and equipment recovery (and replacement reserves)
Institutional policies commonly prohibit recovering lease-purchase payments or principal/interest directly through rates, stating that capital financing is recovered through depreciation. (centerUnknownyearno.b01page pages 1-4)

A representative recharge-center policy specifies straight-line depreciation with a half-year convention and credits depreciation to an equipment replacement reserve that can fund future purchases, explicitly making equipment reserves part of the financial control environment. (centerUnknownyearno.b01page pages 4-7)

The sample rate proposal tables show depreciation allowance and prior-period deficit carryforward treated as explicit line items in the annual rate calculation workbook, reinforcing that depreciation and carryforward are intended to be modeled transparently rather than implicitly. (centerUnknownyearno.b01page media 967a4afa)

Core-facility cost-recovery literature recommends including depreciation as a cost component (e.g., instrument depreciation over an expected life) as part of full cost recovery. (otoole2024aperspectiveinto pages 4-5)

#### 6. Internal vs. external user pricing (academic, nonprofit, commercial)
**Internal users**
Internal users generally must be charged the same internal base rate for the same service; differential internal rates require explicit documentation of user classes, volumes, and bases. (centerUnknownyearno.b01page pages 10-15)

**External users**
A common institutional structure requires external customer rates to include institutional indirect costs and allows a margin/profit for external sales where permitted by policy, while keeping the internal base rate non-profit. (centerUnknownyearno.b01page pages 10-15)

Peer-reviewed core-facility guidance aligns with this structure: federally funded customers should be charged the same base rate whether internal or external, while external commercial users may be charged additional institutional indirect cost on top of the base rate to recover administrative burden; the facility should avoid becoming a profit center even if commercial pricing has no formal upper bound. (hockberger2013bestpracticesfor pages 4-6)

For “full cost recovery” examples, external academic users can be charged the same base rate plus additional indirect cost, and commercial users receive an additional commercial uplift. (otoole2024aperspectiveinto pages 4-5)

#### 7. Subsidies and strategic pricing
Surveys and best-practice narratives emphasize that many core facilities are subsidized; one external-customer best-practices paper reports cores frequently receive substantial institutional and grant/private subsidies and recommends incorporating subsidy rules into business planning and capacity management. (hockberger2013bestpracticesfor pages 2-3)

Institutional recharge policies typically require explicit CFO approval for subsidies during the rate-setting process and describe deficits being eliminated through future price changes or general unrestricted fund subsidies. (centerUnknownyearno.b01page pages 4-7)

If indirect costs or margins are recovered from external users, one institutional policy directs that those recoveries (unless controller-approved otherwise) be used to reduce internal charges on a fair and consistent basis. (centerUnknownyearno.b01page pages 7-10)

#### 8. Break-even analysis, carryforward, and annual rate review
A canonical institutional approach is:
- Target break-even over the operating cycle (often the fiscal year). (centerUnknownyearno.b01page pages 4-7)
- Carry forward accumulated surplus/deficit each year. (centerUnknownyearno.b01page pages 7-10)
- Refund surpluses via future rate reductions and eliminate deficits via future rate increases or approved subsidies. (centerUnknownyearno.b01page pages 4-7)

Annual rate review is treated as a control: “Annually, each service center must submit a proposal to establish rates for the following fiscal year,” with CFO review/approval and retention of rate calculations/approvals for long periods (e.g., 10 years). (centerUnknownyearno.b01page pages 10-15)

#### 9. External/industry engagement controls (contracts, IP, risk)
Peer-reviewed best-practices for handling external customers recommends: assess capacity impacts; involve finance and contracting/tech-transfer offices; define terms and conditions; and manage IP, warranty disclaimers, and compliance topics (e.g., UBI, export controls). (hockberger2013bestpracticesfor pages 2-3)

#### 10. Tailoring the recharge structure to metal additive manufacturing (LPBF AlSi10Mg / aluminum)
While the compliance constructs above are generic, LPBF has predictable cost drivers that should be reflected as separate cost pools and billing units to improve allocability and auditability:
- Machine time (build hours) with documented downtime and efficient utilization assumptions. (otoole2024aperspectiveinto pages 4-5, centerUnknownyearno.b01page pages 15-20)
- Technician labor allocated by effort to activities/equipment (design review, build prep, powder handling, depowdering, support removal, stress relief/heat treat coordination, QA reporting). (otoole2024aperspectiveinto pages 4-4)
- Consumables and materials allocated by measured usage (powder consumption and loss, sieve media, filters, inert gas, PPE) using a consistent, documented allocator. (otoole2024aperspectiveinto pages 4-4)
- Service contracts and maintenance allocated to the relevant service line. (otoole2024aperspectiveinto pages 4-5, mcdonald2012feeforserviceasa pages 2-3)
- Depreciation/replacement reserve for high-capital assets (printers, powder management equipment, furnaces, metrology) with an explicit useful life and reserve policy. (centerUnknownyearno.b01page pages 4-7, centerUnknownyearno.b01page media 967a4afa)

Operationally, LPBF centers often benefit from a hybrid unit structure: (i) setup fee per build; (ii) machine-hour rate; (iii) material per kg; and (iv) post-processing and metrology hourly rates. This aligns with the broader best-practice of selecting auditable units (hour/run/sample/procedure) and avoids burying variable costs inside a single blended charge. (centerUnknownyearno.b01page pages 15-20, otoole2024aperspectiveinto pages 4-4)

#### 11. Vertically integrated and “cloud lab” analogs (examples and implications)
Cloud labs provide a relevant “vertical integration” reference model for advanced services because they bundle instrumentation, technicians, data systems, and workflow orchestration into a standardized service.

A review on self-driving labs notes cloud experimentation can enable remote, 24/7 end-to-end workflows but requires substantial capital and specialized operational capabilities; these infrastructure and operational costs “inevitably get passed onto the user,” potentially making access cost-prohibitive for some academic use-cases. It highlights a major academic partnership model: Carnegie Mellon University’s partnership with Emerald Cloud Lab to create a subscription-based facility (~$40M, 200+ instrument types) to broaden academic access. (lo2023reviewoflowcost pages 22-24)

A peer-reviewed cloud-lab perspective describes Emerald Cloud Lab’s vertically integrated features (broad instrumentation access, AWS-hosted data with access controls, potential open-sourcing of a proprietary workflow language) and identifies Strateos’ evolution from predefined workflows toward implementing on-site cloud labs, implying a hybrid model where institutions may host vendor-like automation locally. (arias2024scientificdiscoveryat pages 8-8)

For a university additive manufacturing core, the “cloud lab” analogy suggests design choices such as: workflow standardization (quoting → design review → build execution → QA reports), strong data/traceability systems, and potentially subscription or retainer models for high-volume internal users; but it also underscores that added infrastructure and staffing are likely to increase the cost base that must be recovered through rates or subsidies. (lo2023reviewoflowcost pages 22-24, arias2024scientificdiscoveryat pages 8-8)

#### 12. A practical template/checklist for implementation
| Element | Best-practice structure | Additive manufacturing notes (LPBF) | Key citations (IDs) |
|---|---|---|---|
| Governance/Scope | Define the facility as a university recharge/service center or specialized service facility; establish separate org/fund, central research/finance oversight, faculty advisory input, and annual CFO/controller approval of rates and subsidies. State mission priority order: internal academic users first, then external academic, then industry if capacity allows. | For metal LPBF, governance should explicitly cover EHS, powder handling, inert-gas systems, QA/QC, HIP/heat-treatment/post-processing interfaces, and export-control/IP review for external jobs. | (turpen2016metricsforsuccess pages 1-2, centerUnknownyearno.b01page pages 1-4) |
| Cost pools | Build cost pools from allowable, allocable, supportable costs only: labor + benefits, service contracts, consumables, utilities/space where permitted, equipment depreciation/use allowance, and approved departmental indirect support. Segregate unallowable costs to non-recharge unrestricted funds. | Separate pools are often useful for: machine operation, powder/materials, build prep, post-processing, metrology/CT, design-for-AM consulting, and failed-build/rework risk where institutionally permitted. | (centerUnknownyearno.b01page pages 4-7, centerUnknownyearno.b01page pages 10-15, otoole2024aperspectiveinto pages 4-5, mcdonald2012feeforserviceasa pages 2-3) |
| Billing units | Use auditable units tied to actual service delivery: hour, run, sample, procedure, or hybrid. Keep units simple enough to bill consistently and document usage through booking/work-order systems. | LPBF commonly needs a hybrid unit structure: machine build hour, setup fee per build, powder/material charge per kg used/consumed, post-processing hour, metrology hour, and engineering labor hour for design/support generation. | (centerUnknownyearno.b01page pages 15-20, otoole2024aperspectiveinto pages 4-4) |
| Utilization forecast | Forecast billable units from multi-year historical use, staffing availability, maintenance downtime, and realistic efficient utilization; document key assumptions and best/worst-case scenarios. Rates should be based on reasonable capacity, not aspirational full utilization. | For LPBF, forecast should include scheduled maintenance, calibration, sieve/recycle time, chamber cleanup, powder changeover, inert-gas purge time, failed-build probability, and bottlenecks in heat treatment/CNC/support removal/inspection. | (centerUnknownyearno.b01page pages 10-15, centerUnknownyearno.b01page pages 15-20, otoole2024aperspectiveinto pages 4-5, otoole2024aperspectiveinto pages 4-4) |
| Internal rate formula | Internal rate should recover estimated allowable costs over the operating cycle: `(allowable direct costs + approved depreciation/use allowance + approved indirect support ± prior surplus/deficit carryforward - approved subsidy) / projected billable units`. Internal users should face the same internal base rate for the same service. | For LPBF, consider separate internal rates for machine families or pooled rates for similar printers if that improves stability; avoid burying large one-time prototype engineering effort inside a simple machine-hour rate. | (centerUnknownyearno.b01page pages 10-15, centerUnknownyearno.b01page pages 15-20, otoole2024aperspectiveinto pages 5-5) |
| External pricing add-ons | External users generally pay the same base service cost plus institutional indirect cost/F&A recovery; commercial users may also pay a market-based margin if policy permits. Federally funded customers should not be charged a different base rate than others for the same service. | For LPBF industry users, external pricing often needs contract terms for quoting, expedited service, scrap/rebuild risk, QA documentation, and IP/confidentiality. Consider separate quoting for regulated testing or certifiable documentation packages. | (hockberger2013bestpracticesfor pages 4-6, centerUnknownyearno.b01page pages 4-7, centerUnknownyearno.b01page pages 10-15) |
| Subsidy handling | Subsidies should be explicit, budgeted, approved outside the rate where required, and used to reduce internal user rates rather than hidden in cost pools. Document source, amount, purpose, and any restrictions. | Common LPBF subsidy rationales: strategic campus capability-building, student training, startup faculty access, or subsidized internal pilot builds. Keep sponsored-research subsidies distinct from general institutional support. | (hockberger2013bestpracticesfor pages 2-3, centerUnknownyearno.b01page pages 4-7, centerUnknownyearno.b01page pages 7-10, centerUnknownyearno.b01page pages 1-4) |
| Allowable vs unallowable costs | Include only allowable/allocable costs under federal cost principles. Common unallowables for federal charging include advertising, alcohol, bad debts, entertainment, fundraising, contributions, PR/public relations, and debt principal/internal interest; recover capital through depreciation rather than loan payments. | In LPBF, exclude speculative R&D unrelated to user jobs, marketing/demo events, unfunded exploratory builds, and general lab beautification from recharge rates. Treat unusual failed experiments carefully and consistently under policy. | (hockberger2013bestpracticesfor pages 4-6, centerUnknownyearno.b01page pages 1-4, centerUnknownyearno.b01page pages 4-7, ds2015costaccountingstandards pages 11-14) |
| Depreciation/equipment replacement reserve | Recover equipment cost via depreciation/use allowance over useful life; many institutional models credit depreciation to an equipment replacement reserve and prohibit direct charging of lease principal/interest. Reassess useful lives periodically. | For LPBF, major assets may include printer, powder sieving/recycling equipment, gas handling, depowdering station, furnaces/HIP access, saw/CNC/post-process tools, and metrology equipment. Reserve planning is critical because replacement cycles and service contracts are costly. | (centerUnknownyearno.b01page pages 4-7, centerUnknownyearno.b01page pages 7-10, centerUnknownyearno.b01page pages 15-20, centerUnknownyearno.b01page media 448aef0b) |
| Carryforward/surplus-deficit treatment | Operate at break-even over the normal operating cycle, not at profit. Carry forward prior-year surplus/deficit into the next rate cycle; surpluses are returned through lower future rates and deficits corrected through rate increases or approved subsidy. | Because LPBF demand can be lumpy, define a tolerance band and correction mechanism for over/under-recovery, especially when one or two large projects distort annual volume. Include treatment of prior-period deficit in the annual rate workbook. | (centerUnknownyearno.b01page pages 1-4, centerUnknownyearno.b01page pages 4-7, centerUnknownyearno.b01page pages 10-15, centerUnknownyearno.b01page pages 7-10, centerUnknownyearno.b01page media 448aef0b) |
| Annual rate review & approvals | Require annual rate proposal with pro forma income statements, assumptions, unit forecasts, user classes, depreciation schedules, and variance plans; obtain finance/CFO/controller review and approval before rate changes take effect. | LPBF review should refresh powder pricing, service contracts, gas/electricity assumptions, technician FTE allocation, maintenance downtime, and external demand mix. If new equipment is added, update pooled-rate logic and capacity assumptions. | (centerUnknownyearno.b01page pages 10-15, centerUnknownyearno.b01page pages 15-20) |
| Documentation & retention | Maintain auditable usage records, booking/work-order data, rate calculations, approvals, billing records, inventory records where relevant, and supporting workpapers for long retention periods per policy. | For LPBF, keep job travelers, machine logs, powder lot/recycle logs, build files, QA/inspection results, and invoice-to-job traceability; these records help both financial auditability and technical reproducibility. | (centerUnknownyearno.b01page pages 10-15, centerUnknownyearno.b01page pages 4-7, otoole2024aperspectiveinto pages 4-4) |
| Compliance checks (federal/non-discrimination) | Ensure charges to federal awards are reasonable, based on actual use, do not exceed cost, and do not discriminate between federal and nonfederal internal users. For specialized service facilities, follow institution-specific treatment of F&A allocation and any negotiated indirect-cost rules. | For LPBF, apply the same internal base rate to federal and nonfederal academic users receiving the same service; do not shift industry discounts or strategic subsidies onto federally sponsored internal users without explicit institutional approval. | (centerUnknownyearno.b01page pages 1-4, ds2015costaccountingstandards pages 37-39, ds2015costaccountingstandardsa pages 37-39, hockberger2026abrfcoreadministrators pages 1-2, hockberger2013bestpracticesfor pages 4-6) |
| Cloud-lab/vertical integration considerations | Decide whether the model is pure recharge, recharge + subscription, or vertically integrated end-to-end service. Cloud-lab literature suggests remote access, workflow standardization, and 24/7 orchestration can expand access, but capital, staffing, data systems, and limited competition can increase user cost. | For LPBF, a “cloud manufacturing lab” model could bundle quoting, design review, build prep, printing, post-processing, inspection, and digital traceability. Best fit is usually partial vertical integration on campus rather than full remote automation, because metal AM still needs technician-intensive handling and safety controls. | (lo2023reviewoflowcost pages 22-24, arias2024scientificdiscoveryat pages 8-8, zilgalvis2025yingchiangjeffreylee pages 1-6, arias2024scientificdiscoveryat pages 9-10, arias2024scientificdiscoveryat pages 8-9) |


*Table: This table provides a practical template for structuring a compliant university recharge/service center model for a shared metal additive manufacturing core. It summarizes governance, costing, pricing, compliance, and operational design choices, with evidence-linked citations from the conversation.*

#### Evidence limitations
The present corpus did not include the full regulatory text of 2 CFR 200.468 itself; therefore, the discussion of Uniform Guidance is grounded in peer-reviewed and institutional implementation literature that explicitly references 2 CFR 200.468 as the successor to OMB A-21 specialized service facility guidance. (hockberger2026abrfcoreadministrators pages 1-2)



References

1. (hockberger2013bestpracticesfor pages 4-6): Philip Hockberger, Susan Meyn, Connie Nicklin, Diane Tabarini, Paula Turpen, and Julie Auger. Best practices for core facilities: handling external customers. Journal of biomolecular techniques : JBT, 24 2:87-97, Jul 2013. URL: https://doi.org/10.7171/jbt.13-2402-001, doi:10.7171/jbt.13-2402-001. This article has 42 citations.

2. (hockberger2026abrfcoreadministrators pages 1-2): Philip Hockberger, Julie Auger, Paula Turpen, and Susan Meyn. Abrf core administrators network: the early years. Journal of Biomolecular Techniques, 37:27-34, Mar 2026. URL: https://doi.org/10.7171/001c.158405, doi:10.7171/001c.158405. This article has 0 citations and is from a peer-reviewed journal.

3. (ds2015costaccountingstandardsa pages 37-39): C DS. Cost accounting standards board disclosure statement for educational institutions. Unknown journal, 2015.

4. (centerUnknownyearno.b01page pages 1-4): R Center. No.: b-01 page: 1 of 23. Unknown journal, Unknown year.

5. (centerUnknownyearno.b01page pages 4-7): R Center. No.: b-01 page: 1 of 23. Unknown journal, Unknown year.

6. (otoole2024aperspectiveinto pages 4-5): Peter J. O'Toole and Joanne L. Marrison. A perspective into full cost recovery within a core facility/shared resource lab. Journal of Microscopy, 294:372-379, Nov 2024. URL: https://doi.org/10.1111/jmi.13246, doi:10.1111/jmi.13246. This article has 13 citations.

7. (centerUnknownyearno.b01page pages 15-20): R Center. No.: b-01 page: 1 of 23. Unknown journal, Unknown year.

8. (otoole2024aperspectiveinto pages 4-4): Peter J. O'Toole and Joanne L. Marrison. A perspective into full cost recovery within a core facility/shared resource lab. Journal of Microscopy, 294:372-379, Nov 2024. URL: https://doi.org/10.1111/jmi.13246, doi:10.1111/jmi.13246. This article has 13 citations.

9. (centerUnknownyearno.b01page pages 10-15): R Center. No.: b-01 page: 1 of 23. Unknown journal, Unknown year.

10. (otoole2024aperspectiveinto pages 5-5): Peter J. O'Toole and Joanne L. Marrison. A perspective into full cost recovery within a core facility/shared resource lab. Journal of Microscopy, 294:372-379, Nov 2024. URL: https://doi.org/10.1111/jmi.13246, doi:10.1111/jmi.13246. This article has 13 citations.

11. (ds2015costaccountingstandards pages 11-14): C DS. Cost accounting standards board disclosure statement for educational institutions. Unknown journal, 2015.

12. (centerUnknownyearno.b01page media 967a4afa): R Center. No.: b-01 page: 1 of 23. Unknown journal, Unknown year.

13. (hockberger2013bestpracticesfor pages 2-3): Philip Hockberger, Susan Meyn, Connie Nicklin, Diane Tabarini, Paula Turpen, and Julie Auger. Best practices for core facilities: handling external customers. Journal of biomolecular techniques : JBT, 24 2:87-97, Jul 2013. URL: https://doi.org/10.7171/jbt.13-2402-001, doi:10.7171/jbt.13-2402-001. This article has 42 citations.

14. (centerUnknownyearno.b01page pages 7-10): R Center. No.: b-01 page: 1 of 23. Unknown journal, Unknown year.

15. (mcdonald2012feeforserviceasa pages 2-3): Sandra A. McDonald, Kara Sommerkamp, Maureen Egan-Palmer, Karen Kharasch, and Victoria Holtschlag. Fee-for-service as a business model of growing importance: the academic biobank experience. Biopreservation and biobanking, 10 5:421-5, Oct 2012. URL: https://doi.org/10.1089/bio.2012.0017, doi:10.1089/bio.2012.0017. This article has 16 citations and is from a peer-reviewed journal.

16. (lo2023reviewoflowcost pages 22-24): Stanley Lo, Sterling Baird, Joshua Schrier, Ben Blaiszik, Sergei Kalinin, Helen Tran, Taylor Sparks, and Alán Aspuru-Guzik. Review of low-cost self-driving laboratories: the "frugal twin" concept. ChemRxiv, Sep 2023. URL: https://doi.org/10.26434/chemrxiv-2023-6z9mq, doi:10.26434/chemrxiv-2023-6z9mq. This article has 4 citations.

17. (arias2024scientificdiscoveryat pages 8-8): D. Sebastian Arias and Rebecca E. Taylor. Scientific discovery at the press of a button: navigating emerging cloud laboratory technology. Advanced Materials Technologies, May 2024. URL: https://doi.org/10.1002/admt.202400084, doi:10.1002/admt.202400084. This article has 7 citations and is from a peer-reviewed journal.

18. (turpen2016metricsforsuccess pages 1-2): Paula B. Turpen, Philip E. Hockberger, Susan M. Meyn, Connie Nicklin, Diane Tabarini, and Julie A. Auger. Metrics for success: strategies for enabling core facility performance and assessing outcomes. Journal of Biomolecular Techniques : JBT, 27:25-39, Apr 2016. URL: https://doi.org/10.7171/jbt.16-2701-001, doi:10.7171/jbt.16-2701-001. This article has 45 citations.

19. (centerUnknownyearno.b01page media 448aef0b): R Center. No.: b-01 page: 1 of 23. Unknown journal, Unknown year.

20. (ds2015costaccountingstandards pages 37-39): C DS. Cost accounting standards board disclosure statement for educational institutions. Unknown journal, 2015.

21. (zilgalvis2025yingchiangjeffreylee pages 1-6): G ZILGALVIS. Ying-chiang jeffrey lee, bria persaud, barbara del castello, allison berke. Unknown journal, 2025.

22. (arias2024scientificdiscoveryat pages 9-10): D. Sebastian Arias and Rebecca E. Taylor. Scientific discovery at the press of a button: navigating emerging cloud laboratory technology. Advanced Materials Technologies, May 2024. URL: https://doi.org/10.1002/admt.202400084, doi:10.1002/admt.202400084. This article has 7 citations and is from a peer-reviewed journal.

23. (arias2024scientificdiscoveryat pages 8-9): D. Sebastian Arias and Rebecca E. Taylor. Scientific discovery at the press of a button: navigating emerging cloud laboratory technology. Advanced Materials Technologies, May 2024. URL: https://doi.org/10.1002/admt.202400084, doi:10.1002/admt.202400084. This article has 7 citations and is from a peer-reviewed journal.
