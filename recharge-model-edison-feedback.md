# Edison Scientific Feedback on the Recharge-Model Dossier

> **Provenance.** Produced by an Edison Scientific (FutureHouse) **ANALYSIS** job,
> task ID `0f848b2d-a949-4cd2-8eb6-c19c887f0abe`, completed 2026-07-04. The uploaded
> collection contained: the four research documents in this repo
> (`recharge-model-exploration.md`, `recharge-model-followup.md`,
> `recharge-model-byu-official-docs.md`, `recharge-model-scenarios-and-operations.md`),
> the official BYU *Recharge Center Policy & Procedures* PDF, the complete `drafts/`
> package (6 files), and the full PR #107 discussion history compiled via the GitHub
> API. The answer below is preserved **verbatim**.
>
> Three earlier ANALYSIS attempts (`46e2ffaf`, `f38bdddc`, `4ba8e3e1`) failed
> server-side; root cause was the upload entry name containing `#`/spaces/parentheses,
> which produced an invalid cloud-storage signed URL at `multipart-upload/initiate`.
> This run used a URL-safe name and the documented `astore_file_content` →
> `data_storage_uris` flow.
>
> **Status: exploratory feedback — not policy, not legal/tax advice.**

---

## (A) CORRECTNESS

1. **Do not describe machine-specific renovation reclassification as presumptively recoverable.**  
   In `drafts/equipment-depreciation-and-reimbursement-package.md` §3, lines 49–55 say dedicated electrical, argon plumbing, ventilation, and rigging are “candidates for capitalization into the equipment asset record.” That is defensible only for costs that BYU Fixed Assets treats as part of the equipment acquisition cost or as modifications/accessories needed to ready the equipment for use. 2 CFR 200.1 defines acquisition cost as net invoice price plus “modifications, attachments, accessories, or auxiliary apparatus necessary to make it usable,” and says taxes, duty, freight, and installation may be included or excluded according to the institution’s regular accounting practices. Dedicated building systems can still be building improvements, not equipment. If these are included in the recharge depreciable base while also included in BYU’s facilities and administrative cost base, that is a double-recovery problem under BYU policy p. 3 and 2 CFR 200.468.

   **Change:** In `equipment-depreciation...` §3 and `rate-proposal-cy2027.md` A1/§4, replace “candidates for capitalization” language with “may be included only if Fixed Assets and Regulatory Accounting determine the item is capitalized to the equipment asset under BYU’s regular accounting practices and is excluded from building/F&A recovery.”

2. **The draft is right on tariff/duty, but only if booked consistently.**  
   `equipment-depreciation...` §2, lines 32–35 correctly cites 2 CFR 200.1 for duty, freight, insurance, and installation. The important condition is regular accounting practice. A tariff/duty cannot be selectively pulled into this one asset if BYU’s normal capitalization policy expenses similar landed-cost charges.

3. **The rate proposal materially understates labor unless a separate subsidy is explicit.**  
   `rate-proposal-cy2027.md` §4 carries only 2 attended student operator hours per 6-hour run at $30/h loaded, or $60/run. The draft itself flags this in §8, but it is still the biggest correctness risk because the proposed $306 internal rate could be seen as not based on actual allowable cost. Northwestern’s CHiMaD Metals Processing Facility publishes an AMAZEMET rePowder “Ultrasonic Atomizer” rate of **$1,075 internal / $1,720 external academic / $2,150 commercial** per run. At 305 runs/year, matching Northwestern’s internal rate would imply $327,875/year of recovered cost. The draft pool is $93,375/year, a gap of **$234,500/year**. Even Scenario B adds only $45,000/year and reaches $454/run, still less than half Northwestern.

   **Change:** Before submitting, do a 2–4 week operator time study and include all staff time: scheduling, quoting, feedstock intake, SDS review, setup, attended monitoring, powder recovery, cleaning, packaging, documentation, failed-run handling, instrument maintenance, training, cloud-lab support, billing support, and safety recordkeeping.

4. **A “zero/near-zero internal rate” should not be presented as the approved rate.**  
   `questions-for-regulatory-accounting.md` item 13 asks whether a blanket zero/near-zero internal rate is acceptable. BYU policy allows centers not to include all costs if a non-federal source covers the gap, and allows non-federal non-recharge funds to pay for specific users. But the defensible structure is: approved cost-based internal rate + documented subsidy/credit. A posted internal rate of $0 while external federally funded users pay cost + F&A could look like non-uniform base pricing or an undocumented subsidy.

   **Change:** In `recharge-center-establishment-proposal.md` §7 and `rate-proposal-cy2027.md` §7, state that the approved internal rate remains the cost-based rate, and any PI-group non-federal use is either charged, subsidized, or credited under §8 with the gross rate and subsidy/credit recorded.

5. **The embargo-tier surcharge menu is not a federal-cost-principles problem if restricted to non-federal external users, but the agreement overreaches on publication rights.**  
   `rate-proposal-cy2027.md` §5 and `external-user-service-agreement-template.md` §5 restrict premium embargo tiers to non-federal external users. That matches BYU policy p. 5 allowing surcharges only for non-University, non-Federal agency users. The issue is `external-user-service-agreement-template.md` §5.3, lines 76–84: BYU reserves a right to publish “Run Data” after 30 days for all customers by default. For fee-for-service work, this is unusual and may conflict with customer grant terms, patent timing, export-control classification, unpublished student/customer work, or simple customer expectations. DOE user facilities use a clearer binary model: non-proprietary work is tied to open publication, while proprietary work requires full cost recovery. The 6/12/24-month menu is plausible as a surcharge menu, but I did not find published academic recharge-center prior art for this exact timed embargo pricing scheme.

   **Change:** Make the standard tier “BYU may publish only aggregate/anonymized operational data; customer-specific Run Data may be published only with customer written consent or after a separately agreed non-proprietary publication term.” Keep the embargo/proprietary premium as an OGC-approved non-federal external surcharge.

6. **The §8 in-kind reimbursement ledger may overstate the equipment-repayment concept.**  
   `rate-proposal-cy2027.md` §7 values 200 free PI-group runs at 200 × $306 = $61,200/year and says this credits the $250,000 investment in ~4 years. `equipment-depreciation...` §5 similarly values free services at the internal rate. BYU policy §8 allows reimbursement by free services or by equipment charged to the reserve, capped at the investment, with prior approval and documentation. The risk is that the internal rate includes labor, argon, consumables, maintenance, and depreciation, not just equipment value. That may be acceptable as “services received without charge,” but it should be approved explicitly.

   **Change:** Ask Regulatory Accounting whether §8 in-kind credit is valued at (a) full approved internal rate, (b) depreciation component only, or (c) some documented use-allowance. Do not assume full-rate credit.

7. **External federal-user classification is under-specified.**  
   `external-user-service-agreement-template.md` Appendix A asks the customer to certify a federal award number. Good start. But `rate-proposal-cy2027.md` §5 applies “federal external” pricing based on documentation. You need more: certification that the ordered service will be charged directly or indirectly to that award and that the customer institution permits the purchase. If the external user is a nonprofit intermediary or foundation using mixed funds, the surcharge/no-surcharge decision becomes ambiguous.

8. **Card fees cannot be casually assigned to federal users.**  
   `rate-proposal-cy2027.md` §5 notes that card-paid external jobs bear ~2.9% merchant fees and federal-documented externals will be steered to invoice/ACH. That is the right direction. But if a federal-documented external insists on card payment, a card fee embedded only in that transaction could be a surcharge. PCI DSS also means the lab must not handle card data outside BYU-approved eMarkets/Square workflows.

   **Change:** State: “Credit-card acceptance only through BYU Treasury-approved channels; no lab-owned Stripe/PayPal; no separate card convenience fee unless Treasury confirms card-network, state-law, and BYU policy compliance.”

## (B) GAPS

1. **EHS and combustible-metal-powder controls are missing from the approval path.**  
   None of the draft package gives Environmental Health and Safety a formal role. For aluminum alloy and other metal powders, this is not optional. Add review for combustible dust, inert gas/asphyxiation, oxygen sensors, ventilation, PPE, powder storage, spill response, waste, SDS handling, shipping, and emergency procedures. NFPA 484 is the obvious standard to ask EHS about.

2. **Export control is mentioned, but the operational mechanism is thin.**  
   `external-user-service-agreement-template.md` §7 and `questions...` item 23 mention EAR/ITAR screening. Add a workflow: restricted-party screening, country screening, material/alloy and process-parameter review, customer end-use/end-user certification, and escalation rules before accepting non-US users or defense/aerospace alloys. Remote access raises deemed-export issues if non-US persons can observe process parameters.

3. **Cyber/data-security classification is missing.**  
   A cloud-lab model may receive customer CAD files, alloy formulations, process windows, controlled unclassified information, export-controlled technical data, or proprietary manufacturing data. Add data classification, retention, access control, audit logs, remote-session recording policy, and a “no CUI/ITAR data unless approved” clause.

4. **No failed-run/rework policy.**  
   Ultrasonic atomization yield and PSD are uncertain. The service agreement disclaims yield, but the rate proposal does not define when a run is billable, whether customer-supplied feedstock failure is billable, how operator error is handled, and whether re-runs are free, discounted, or separately charged.

5. **Per-run billing is too coarse for audit and fairness.**  
   `rate-proposal-cy2027.md` uses one run price for ~6-hour runs. That is simple, but atomization may vary by alloy, feedstock form, cleaning burden, crucible/sonotrode wear, argon use, powder handling, and hazardousness. Consider separate charges for base run, staff hours beyond standard, feedstock prep/casting, consumables, customer material pass-through, characterization, and hazardous-material surcharge where allowed.

6. **No queue-priority/capacity policy.**  
   If the facility is “internal-first” but external demand is large, the center needs a posted priority policy: BYU internal research, sponsored commitments, external federal academic, non-federal academic, commercial/proprietary. This matters for UBIT, mission fit, and user expectations.

7. **No bad-debt, collections, and customer credit controls.**  
   Bad debt is unallowable in federal cost pools. For external customers, require PO or signed order, credit review for industry, AR aging rules, suspension for nonpayment, and departmental responsibility for uncollectible amounts.

8. **Sales tax and product characterization need more precision.**  
   The drafts mention Utah sales tax and Avalara. Add a Tax Office determination for whether the transaction is a service, tangible personal property, mixed transaction, resale, shipped out of state, or exempt academic purchase. Powder shipped to customers is likely tangible personal property.

9. **No insurance/product-liability review.**  
   The service agreement caps BYU liability, but OGC/Risk Management should review product liability for powders used in downstream printing, aerospace/medical/defense exclusion language, indemnity, and customer insurance requirements.

10. **No segregation-of-duties control.**  
   Add who approves orders, who logs usage, who bills, who reconciles revenue, who approves rate changes, and who reviews exceptions. This is basic audit hygiene.

11. **No record-retention schedule.**  
   BYU policy says records are subject to federal/internal audit. Specify retention for rate calculations, approvals, usage logs, invoices, subsidy ledgers, §8 ledgers, asset records, SDS, export screening, and service agreements.

12. **BYU policy currency remains unresolved.**  
   The official policy PDF is June 2005 and cites OMB A-21. The drafts ask whether it is current, but the establishment package should not be finalized until Regulatory Accounting confirms current policy, forms, and Uniform Guidance mapping.

## (C) DEFENSIBILITY OF THE SIX RISKIEST INTERPRETATIONS

1. **Tariff/duty and machine-specific renovation in depreciable base: mixed.**  
   - **Tariff/duty:** strong if BYU capitalized it or normally capitalizes it. 2 CFR 200.1 expressly names duty, freight, insurance, and installation as ancillary charges that may be included under regular accounting practice.  
   - **Machine-specific renovation:** moderate to weak unless Fixed Assets reclassifies the items to the equipment asset. Rigging and vendor installation are stronger. Dedicated electrical, gas plumbing, and ventilation are weaker because they may be building systems or F&A-recovered facilities costs.  
   - **Draft files:** `equipment-depreciation...` §2–§3; `rate-proposal-cy2027.md` A1 and §4 exclusions.

2. **Zero/near-zero internal rates subsidized by startup funds: defensible only as documented subsidy, not as hidden repricing.**  
   BYU policy appears to allow under-recovery when non-federal funds cover the gap and usage stays in the denominator. But preserve a gross approved cost-based internal rate. Then show “paid by user,” “paid by startup subsidy,” or “§8 in-kind credit.” This avoids shifting costs to federal users and keeps federal/non-federal internal treatment uniform.  
   - **Draft files:** `questions...` item 13; `recharge-center-establishment-proposal.md` §7; `rate-proposal-cy2027.md` §7.

3. **Embargo-tier surcharge for non-federal external users: legally plausible, operationally risky.**  
   BYU policy permits surcharges for non-University, non-Federal agency users. DOE user-facility practice supports a proprietary/non-proprietary price distinction: non-proprietary users publish; proprietary users pay full cost recovery. But I found no published prior art for a granular 6/12/24-month embargo surcharge menu in academic recharge centers. The main risk is not rate law; it is OGC/IP/export/publication complexity.  
   - **Draft files:** `rate-proposal-cy2027.md` §5; `external-user-service-agreement-template.md` §5.

4. **Section-8 in-kind reimbursement via free services: defensible but needs a written valuation ruling.**  
   BYU policy §8 supports free services as a reimbursement mechanism for non-federal accounts that funded equipment, with prior approval and documentation. The unresolved issue is valuation. Full internal-rate credit is generous and may be acceptable, but it includes non-equipment operating costs. Get written approval before relying on the “~4 years to credit $250k” statement.  
   - **Draft files:** `equipment-depreciation...` §5–§6; `rate-proposal-cy2027.md` §7.

5. **Majority-external billed user base in an internal-first recharge center: defensible only if total usage and mission remain internal/research-centered.**  
   BYU policy defines a recharge center as serving internal University operations primarily and external users secondarily. In the forecast, total runs are internal-majority if the PI group’s 200 runs count: 205 internal vs. 100 external. But cash-billed usage is almost all external if PI runs are free/credited. That mismatch is audit-sensitive. It affects UBIT, sales tax, and whether this is really a recharge center versus external sales/auxiliary/commercial service.  
   - **Draft files:** `recharge-center-establishment-proposal.md` §1 and §3; `rate-proposal-cy2027.md` §3 and §7.

6. **Nonprofit intermediary as external user: high-risk and not recommended for year one.**  
   The intermediary does not remove BYU’s need to classify the transaction based on ultimate use, funding source, private benefit, export control, sales tax, and UBIT. If it is a pass-through for industry, BYU should treat it as non-federal external/commercial. If it aggregates federally funded academic work, the no-surcharge rule may still be implicated. Related-party governance, PI conflict of interest, private inurement/private benefit, and double-markup concerns are substantial.  
   - **Draft context:** `pr-107-full-history.md` lines 38–40; `recharge-model-followup.md` nonprofit-intermediary section.

## (D) STRATEGY

The README sequencing is directionally right, but it is too finance-first and pushes legal/EHS/operational controls too late. I would change the 12-month plan as follows.

1. **Immediately: freeze public price promises.**  
   Do not quote $306/run externally or internally except as “illustrative.” The Northwestern comparator makes the current rate look under-costed.

2. **July–August 2026: run a real time-and-cost study.**  
   For every atomizer job, log operator time by task, staff/supervisor time, setup, cleaning, feedstock prep, powder recovery, packaging, documentation, failed runs, maintenance, and remote-access support. This is more important than polishing the proposal text.

3. **July–August 2026: convene one cross-functional kickoff, not serial office visits.**  
   Include Regulatory Accounting, Fixed Assets, department business officer, EHS, OGC, Tax, Treasury, Export Control, and Sponsored Programs. The current `drafts/README.md` Phase 0–3 sequence waits until November–December for OGC/Treasury/Tax/export control. That is too late for January 1 launch.

4. **August 2026: get the asset decision first.**  
   Fixed Assets must decide capitalized cost, in-service date, useful life, and whether any installation/renovation lines belong on the equipment record. Without that, the depreciation pool is provisional.

5. **August–September 2026: choose one clean own-lab structure.**  
   Preferred: approved internal rate + §8 in-kind credit if Regulatory Accounting confirms full-rate valuation. Fallback: approved internal rate + explicit startup subsidy. Avoid describing the rate as “zero.”

6. **September 2026: submit a conservative CY2027 rate with two columns.**  
   Column A: minimum documented cost. Column B: staffed/realistic cost. I would not submit the current $306/run as the main proposal unless the time study supports it. A plausible staffed rate may be $700–$1,100/run, not $306–$454/run.

7. **October 2026: narrow the first-year service menu.**  
   Launch with standard and proprietary/non-public non-federal external options only if OGC approves. Defer 6/12/24-month embargo granularity until after the first annual review.

8. **November–December 2026: operational readiness gate.**  
   Before go-live: approved SOPs, EHS signoff, export screening checklist, service agreement, billing workflow, eMarkets/AR process, customer intake form, usage log, rate schedule, §8 ledger, and reserve-account journal process.

9. **CY2027: quarterly review, not just annual review.**  
   Because usage and labor are uncertain, schedule quarterly actual-vs-forecast checks. Trigger a mid-year rate revision if actual labor per run differs by >20%, utilization differs by >25%, or external mix changes materially.

10. **Treat the Northwestern rate as a warning, not just a comparator.**  
   Northwestern’s $1,075 internal rate for the same class of atomizer suggests the true cost is staff/process dominated. The current VCL model assumes 305 runs/year and only $93,375/year in cost. If the lab needs even 1.0 FTE loaded at $90k, the internal rate becomes roughly $601/run: ($93,375 + $90,000) / 305. If 2.0 FTE are needed, it becomes roughly $896/run. That is the range I would plan around.

## (E) PRIOR ART

Comparable public rate/governance examples found:

1. **Northwestern CHiMaD Metals Processing Facility.**  
   Publishes rates for an AMAZEMET rePowder-class ultrasonic atomizer: **$1,075 NU users / $1,720 external academic / $2,150 commercial** per run. The same facility page describes the AMAZEMET rePowder as atomizing metals/alloys under argon and producing ~100 g powder/day from ~200 g initial material, depending on particle-size target. This is the closest comparator.

2. **Michigan Technological University Advanced Metal 3D Printing Center.**  
   Publishes internal/external use rates for advanced metal 3D printing and notes material-use rates are reviewed annually. Useful as a public university metal AM recharge-rate example, though not atomization-specific.

3. **University of Washington Mechanical Engineering Metal Additive Manufacturing.**  
   Publishes an hourly Arcam EBM A2X rate and separate powder and lab-engineer rates: **Arcam EBM A2X $45 internal / $90 external / $52 outside academic per hour; metal powder $224 internal / $282 external / $259 outside academic per kg; lab engineer $99 internal / $173 external / $115 outside academic per hour.** This supports unbundling machine time, material, and engineer labor rather than using one blended per-run price.

4. **Georgia Tech Advanced Manufacturing Pilot Facility.**  
   Publishes broad equipment rates with internal and external customer columns, including advanced manufacturing categories. Useful for the internal/external differential model.

5. **UMass Amherst ADDFab.**  
   Publishes campus vs external/industry rates, including metal additive systems: EOS M290 daily rates and Optomec LENS 450 daily rates are listed, plus external/industry differentials. Useful as AM core pricing prior art.

6. **LSU Advanced Manufacturing and Machining Facility FY26 rates.**  
   Public PDF lists academic and non-academic rates, including “Metal 3D Printing Mlab Cusing R” at **$36/hour academic / $60/hour non-academic** and separate powder prices. Useful as another unbundled AM rate sheet.

Published guidance on proprietary/data-embargo pricing:

1. **DOE Office of Science user facilities.**  
   DOE states that user fees are not charged for non-proprietary work if the user intends to publish in the open literature, while **full cost recovery is required for proprietary work**. This is strong prior art for a binary non-proprietary/proprietary distinction, not for a 6/12/24-month surcharge ladder.

2. **Advanced Photon Source / Argonne.**  
   APS distinguishes non-proprietary research, where users intend to publish, from proprietary research, where users are charged for machine time and limited support on a full-cost-recovery basis. Again, this supports proprietary-tier pricing in principle.

3. **Hockberger et al., “Best Practices for Core Facilities: Handling External Customers,” Journal of Biomolecular Techniques 24(2):87–97 (2013), DOI: 10.7171/jbt.13-2402-001.**  
   This is the most relevant core-facility guidance. It supports external-customer agreements, appropriate indirect-cost recovery, review by finance/contracts, and care in distinguishing fee-for-service from research collaboration. It does not endorse a timed publication-embargo menu.

**Bottom line:** the dossier is close, but I would not submit the CY2027 rate proposal as written. The rate is probably too low, the renovation capitalization language is too confident, the §8 valuation needs a written ruling, and the embargo menu needs OGC/Regulatory Accounting approval before appearing in a customer-facing agreement.

## Discretionary decisions

- Treated this as a compliance/document review, not a legal opinion or statistical analysis; no statistical tests were applicable.
- Used BYU’s June-2005 Recharge Center Policy PDF as controlling institutional evidence, while flagging its pre-Uniform-Guidance age as a limitation.
- Treated 2 CFR 200.468 as the federal baseline for specialized service facilities and 2 CFR 200.1 as the acquisition-cost definition relevant to tariffs, freight, installation, and ancillary charges.
- Used Northwestern CHiMaD’s published AMAZEMET rePowder rate as the closest cost reasonableness comparator because it is the same instrument class and publicly posts internal/external/commercial rates.
- Interpreted zero/near-zero internal pricing as potentially defensible only when implemented as an explicit non-federal subsidy or §8 credit against a gross approved cost-based rate.
- Treated the embargo pricing menu as a non-federal external surcharge question rather than an internal recharge-rate question, because BYU policy permits surcharges only for non-University, non-Federal agency users.
- Recommended deferring the fine-grained 6/12/24-month embargo menu because I found public prior art for proprietary vs non-proprietary access, but not for timed embargo surcharge ladders in university recharge centers.
- Recommended quarterly CY2027 monitoring thresholds (>20% labor variance, >25% utilization variance, material external-mix change) as practical governance triggers; these thresholds are judgment calls, not requirements found in BYU policy.