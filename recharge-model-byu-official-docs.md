# Official BYU Documents — Recharge Centers, Payments, and Tax: Findings & Assessment

> **Provenance.** This document was compiled in response to a request on PR #107 to *find
> and assess official BYU docs*, with the added context that **all VCL equipment to date
> has been purchased exclusively on startup funds, with no grant money**. Sources are
> official BYU web pages and PDFs located via web search on 2026-07-03. BYU's web
> properties (spo.byu.edu, finserve.byu.edu) are fronted by CloudFront and blocked direct
> retrieval from the CI runner, so full text was retrieved from Internet Archive (Wayback
> Machine) snapshots of the official pages; snapshot dates are given per source. Live
> URLs are listed alongside archived ones — **verify against the live pages before acting**.
>
> **Status:** Exploratory background research — **not policy or legal/tax advice.**
> The controlling authority is BYU Regulatory Accounting / Financial Services, not this
> document.

---

## 1. Documents found

| # | Document | Owner | Format | Retrieved from |
|---|----------|-------|--------|----------------|
| 1 | **Recharge Center Policy & Procedures** (10 pp.) | Sponsored Projects / Research & Regulatory Affairs | PDF | Wayback snapshot 2026-03-07 of [spo.byu.edu policies page](https://spo.byu.edu/policies) → [PDF](https://spo.byu.edu/00000190-3687-d777-a591-37af392d0001/rechargecenterpolicyprocedures-pdf) |
| 2 | **Unallowable Costs – Guidelines** (Apr 1, 2014, 2 pp.) | Grants & Contracts Accounting | PDF | Same policies page → [PDF](https://spo.byu.edu/00000190-368d-d777-a591-37ad68b10000/unallowablecosts-pdf) |
| 3 | **Merchant Services** page | Treasury Services (Financial Services) | Web | [Live](https://finserve.byu.edu/treasury/merchant-services) / Wayback 2025-12-11 |
| 4 | **Transact Payments – eMarkets** page | Treasury Services | Web | [Live](https://finserve.byu.edu/treasury/transact-payments-emarkets) / Wayback 2025-12-11 |
| 5 | **Square Mobile Credit Card Program** page | Treasury Services | Web | [Live](https://finserve.byu.edu/treasury/square-mobile-credit-card) / Wayback 2025-12-11 |
| 6 | **Tax Office** page (UBIT, sales tax, 501(c)(3) letter) | Regulatory Accounting & Reporting | Web | [Live](https://finserve.byu.edu/tax-office) / Wayback 2025-11-17 |
| 7 | **PCI Compliance** page | Treasury Services | Web | [Live](https://finserve.byu.edu/treasury/pci-compliance) (not fetched; listed for completeness) |
| 8 | **Cost Principles Guide** | Grants & Contracts Accounting | Web | [Live](https://finserve.byu.edu/grants-contracts/cost-principles-guide) (surfaced in search; not fetched) |
| 9 | **Asset Management Policy Manual** | Financial Services | PDF | Linked from [spo.byu.edu/policies](https://spo.byu.edu/policies) (not fetched) |

Search results also indicate BYU's federally negotiated **F&A (indirect cost) rate moved
from 50% to 51.5% effective January 1, 2022**, under a DHHS-audited rate agreement
(cognizant agency: DHHS), per BYU Sponsored Projects pages. Confirm the current rate and
agreement with the Sponsored Programs Office (rao@byu.edu, 801-422-3841).

---

## 2. BYU Recharge Center Policy & Procedures — what it actually says

This is the controlling internal document the two earlier research files
(`recharge-model-exploration.md`, `recharge-model-followup.md`) could only approximate
from peer-institution literature. Key provisions, quoted or closely paraphrased:

### Establishment and approval chain (§2)

> "The prospective Recharge Center must submit a proposal to establish a recharge center
> to the Chair of the cognizant Department for approval. … The Chair will forward the
> approved Recharge Center proposal to the Dean's Office for its approval. … The Dean's
> Office will forward the proposal to the Director of Regulatory Accounting … who will
> establish the appropriate account and budget number(s) for the Recharge Center."

The responsibilities table adds that center management "request[s] the establishment of a
recharge center or cost center from the Chair, Dean's **and VP's** office," and that
**Regulatory Accounting** "approve[s] the establishment of recharge centers" and
"review[s] and approve[s] rates." **Financial Accounting** opens/closes the operating,
equipment-reserve, and other accounts; **Internal Audit** periodically reviews records
and practices; records/rates are "subject to audit by Federal and Internal BYU auditors."

So BYU's real chain is **Department Chair → Dean → (VP office) → Regulatory Accounting**
— materially *simpler* than the 16-step, committee-heavy generalization in
`recharge-model-followup.md` §"Who approves". There is no standing rate-review committee
in the policy; Regulatory Accounting is the single rate authority.

### Rate setting (§4)

- Rate proposals go to Regulatory Accounting **at least annually**, and additionally at
  initial establishment, when new services/products are added, or when methodology
  changes significantly. The Chair or Dean reviews and approves rates *before*
  submission.
- **"Annual Rate = Annual Costs / Total Annual Usage."** All usage must be logged and
  factored in **whether billed or not** (i.e., unbilled/subsidized runs still count in
  the denominator).
- Internal rates must be cost-based and designed to **break even over a reasonable
  period — defined as 5 years** (a notably longer window than the 1-year cycle typical
  in the peer policies surveyed earlier).
- All university users get the same rate for the same service under the same
  circumstances; volume discounts must be equally available to all qualifying users.
- A **minimum fee** "based on costs incurred to initiate the service, such as equipment
  set up costs, expendable supply costs" is allowed with Regulatory Accounting approval —
  this directly sanctions the per-build setup fee proposed for LPBF billing in
  `recharge-model-exploration.md`.
- **"Advanced billing for services or products is not allowed."** This is a significant
  constraint for a *cloud lab* model: prepaid credits/deposits (the Emerald Cloud
  Lab-style pattern) would conflict with this clause as written and would need explicit
  negotiation with Regulatory Accounting.

### External users (§4)

- External rates **must add institutional overhead** (F&A) unless Regulatory Accounting
  approves otherwise.
- **"'Surcharges' can be added to rates charged to non-University, non-Federal agency
  users. These surcharges can be used to reduce rates charged to users, build a working
  capital reserve, or to finance equipment purchases."** — i.e., a market uplift on
  commercial users is expressly permitted and can fund the equipment reserve.
- External users who document federal funding (award number/approval) pay **cost +
  institutional overhead only** — no surcharge.
- Revenues from external users must be tracked separately; non-federal external users may
  be billed higher than internal users.

### Costs, equipment, and depreciation (§§3, 7)

- Rates may include only costs directly related to operation; costs must be reasonable,
  allocable, allowable, consistently treated. OMB A-21-unallowable costs (entertainment,
  interest, bad debt, personal goods/services…) are excluded, as is building
  depreciation/rent/O&M not paid by the center, and anything already recovered through
  the F&A rate.
- Equipment capitalization threshold: **$5,000**. The *acquisition cost* of ≥$5,000
  equipment can never go into rates; **straight-line depreciation may be included if
  negotiated with Regulatory Accounting**, and only if the center has an **equipment
  reserve account**, an approved depreciation schedule listing Equipment Inventory Office
  asset numbers, and keeps depreciation journal entries current.
- **"If equipment is purchased with Federal funds or used for cost sharing on Federal
  awards, its depreciation cannot be included in the recharge rates."**
- **"Recharge rates cannot include depreciation from prior years"**, and equipment
  "cannot be depreciated beyond its useful life … even if the equipment wasn't
  depreciated for each of the five years."

### Reimbursement of invested funds (§8)

> "Equipment used by the Recharge Center, which is purchased with general or departmental
> operating (non-Federal) funds, can be depreciated in recharge rates. The department can
> be reimbursed for the cost of this equipment if: prior approval is received by
> Regulatory Accounting [and] adequate documentation is developed, maintained, and
> retained … to verify the equipment's original purchase cost, depreciation/use allowance
> amounts recovered, etc."

Reimbursement to accounts that invested in the center is capped at the amount invested
and takes the form of free services or charging equipment to the center's equipment
reserve account — never cash above the investment.

### Taxes, deficits, closure (§§5, 6, 9)

- Sales of "tangible personal property" to external users may trigger **Utah sales tax**
  (contact Accounting). Charging externals above cost may create **UBIT** exposure under
  the standard three-part test (trade or business, regularly conducted, not substantially
  related to exempt purpose) — contact Regulatory Accounting.
- Surpluses and deficits roll into the following year's rates; deficits that rates can't
  absorb are funded by the department; multi-year deficit recovery needs a Regulatory
  Accounting-approved plan.
- Closing a center: contact Regulatory Accounting and notify the Chair/Dean.

### Currency caveats

The PDF is dated internally to **June 2005** (it names the then-Director of Regulatory
Accounting "currently (June 2005) John N. Gardner") and cites **OMB Circular A-21**
(superseded by Uniform Guidance 2 CFR 200 in 2014) and **PeopleSoft speedtypes** (the
Financial Services site now links to a "Back To Old Site (PeopleSoft Info)" page,
suggesting a system migration). The Unallowable Costs guideline (2014) is likewise still
A-21-based. The *structure* (chair → dean → Regulatory Accounting; annual rates; 5-year
break-even; equipment reserve) is unlikely to have changed drastically, but **the named
offices, forms, and thresholds must be re-verified with Regulatory Accounting before any
rate proposal is drafted**.

---

## 3. What "everything bought on startup funds, no grant money" changes

This is the single most consequential fact for the VCL rate model, and BYU's policy
addresses it directly:

1. **Depreciation is includable.** The federal-funds prohibition on including equipment
   depreciation in rates does *not* apply — startup funds are internal, non-federal
   money, squarely within the policy's "general or departmental operating (non-Federal)
   funds" clause. The LPBF machine, atomizer, and supporting equipment can be depreciated
   into recharge rates (straight-line, over BYU-standard useful lives, with a Regulatory
   Accounting-approved schedule and an equipment reserve account).

2. **The startup investment can be recouped.** §8 provides an explicit, sanctioned
   mechanism to pay back the account that funded the equipment — up to (never beyond) the
   original purchase cost — via the equipment reserve, with prior approval and
   documentation of original cost and amounts recovered. In effect, the recharge center
   can amortize the startup outlay back to the department/PI accounts over the
   equipment's useful life.

3. **No federal-title complications.** Because no grant money bought the equipment, there
   are no federal equipment-title, screening, or cost-sharing entanglements, and no
   double-recovery conflict with a federal award that funded the hardware.

4. **The clock is running.** Two clauses make timing material: rates "cannot include
   depreciation from prior years," and equipment "cannot be depreciated beyond its useful
   life … even if [it] wasn't depreciated for each of the five years." Every year that
   passes between acquisition and establishing the recharge center is a year of
   depreciation that can **never** be recovered through rates. If cost recovery on the
   startup-funded equipment is a goal, establishing the center (or at least negotiating
   the depreciation schedule) sooner preserves more of the recoverable base.

5. **Federal rules still bind the rates themselves.** How the equipment was bought does
   not relax rate discipline: the moment any internal user pays with federal grant funds,
   the uniform-rate, cost-based, break-even, and unallowable-cost rules all apply to the
   rates charged. Startup funding removes constraints on the *cost pool inputs*
   (depreciation), not on *rate conduct*.

6. **Documentation to assemble now:** original purchase costs and funding source for each
   ≥$5,000 item, Equipment Inventory Office asset numbers, in-service dates, and
   BYU-standard useful lives — these are the exact inputs Regulatory Accounting requires
   for an approved depreciation schedule and any reimbursement arrangement.

---

## 4. Credit-card payments — the BYU-specific answer

The generic analysis in `recharge-model-followup.md` §3 is confirmed and sharpened by
BYU's official Treasury Services pages:

- **University units may act as merchants, but Treasury Services approves and coordinates
  all university credit-card merchant services.** All credit-card contracts are reviewed
  by University Legal Counsel under Purchasing's direction; PCI-DSS compliance is managed
  through Treasury Services' PCI program.
- **Each department pays its own merchant fees**, "calculated and allocated monthly and
  booked to the department's corresponding GL code." So card-processing costs land on the
  VCL's operating account — consistent with the earlier finding that recovering them via
  a card surcharge is constrained, while the recharge policy's external-user *surcharge*
  (§4) offers a compliant route to absorb them in external pricing.
- **Online payments:** Transact Payments **eMarkets** (Storefront = fully hosted, least
  PCI burden; Checkout = redirect from a department site, moderate PCI burden, annual PCI
  assessment; Mendix is BYU's recommended PCI-compliant app platform; Brightspot is
  explicitly *not* PCI-compliant for checkout integration). Avalara is integrated for
  automatic sales-tax calculation on external/out-of-state sales.
- **In-person/mobile payments:** the **Square Mobile Credit Card Program** exists for
  departments, with reservation request forms and required PCI-DSS training.
- Contacts published on the official pages: Kim Stringham, Treasury Services
  (kim.stringham@byu.edu, 801-422-1292; merchant services & Square); Connor Brown
  (connor.brown@byu.edu, 801-422-6534; eMarkets); Paul Larsen, Tax Office
  (paul_larsen@byu.edu, 801-422-6630; sales tax).

**Bottom line:** external users paying the VCL by credit card is clearly possible through
established BYU infrastructure (an eMarket storefront is likely the lowest-friction
option), provided the center's rate model accounts for merchant fees and internal users
stay on journal-entry billing.

---

## 5. Tax and nonprofit-intermediary touchpoints

- The **Tax Office** (part of Regulatory Accounting & Reporting) publishes the
  university's **501(c)(3) tax-exempt letter**, Utah sales-tax license and exemption
  forms, and handles **Income Tax (UBIT)** questions — the exact offices the
  nonprofit-intermediary analysis in `recharge-model-followup.md` §4 said would need to
  be engaged. The recharge policy itself flags UBIT whenever externals are charged above
  cost, which an intermediary structure would almost certainly do.
- Utah **sales tax** applies to tangible personal property sold to external users
  (atomized powder or printed parts shipped to an external customer plausibly qualifies);
  Transact's Avalara integration automates destination-based calculation.

---

## 6. Assessment vs. the earlier (generalized) research

| Topic | Followup doc predicted | BYU policy actually says |
|-------|------------------------|--------------------------|
| Approval chain | 16-step chain incl. rate-review committee, budget office | Chair → Dean (→ VP office) → **Regulatory Accounting** (single rate authority) |
| Break-even window | Annual review; surplus limited to ~2–3 months' income | Annual rate updates, but break-even judged **over 5 years**; surpluses/deficits roll into next year's rates |
| Setup fee for LPBF builds | Proposed as hybrid billing unit | Expressly allowed as a "minimum fee" with Regulatory Accounting approval |
| External pricing | Base + F&A; market uplift possible | **Mandatory** institutional overhead on externals (unless waived) + optional surcharge on non-federal externals |
| Prepaid cloud-lab credits | Not flagged | **Advance billing prohibited** — a real obstacle for ECL-style prepaid models |
| Depreciation of startup-funded equipment | General principle only | Explicitly allowed **and** reimbursable to the funding account, with prior approval |
| Credit cards | Possible via central merchant program | Confirmed: Treasury Services program, eMarkets/Square, department pays fees |

One correction of scope: the anonymous "R Center, No.: b-01, page 1 of 23" citations in
`recharge-model-exploration.md` are a 23-page manual and therefore **not** this BYU
policy (10 pages) — they remain unattributed.

---

## 7. Recommended next steps (verification, not policy)

1. Contact **Regulatory Accounting** (via Financial Services, finserve.byu.edu) to
   confirm the current version of the Recharge Center Policy, the current director, and
   whether the 2005 procedures/thresholds still govern post-Uniform-Guidance.
2. Contact the **Sponsored Programs Office** (rao@byu.edu, 801-422-3841) for the current
   DHHS rate agreement (F&A rate for external-user pricing).
3. Begin assembling the **equipment documentation** in §3.6 above — it is needed
   regardless of when a center is proposed, and the unrecoverable-prior-years rule makes
   delay costly.
4. Ask Treasury Services (**kim.stringham@byu.edu**) about an eMarket storefront and
   whether merchant fees may be recovered through the external-user surcharge.
5. Raise the **advance-billing prohibition** early if a prepaid-credit cloud-lab model is
   contemplated.

---

## References (official BYU sources)

1. Brigham Young University, *Recharge Center Policy & Procedures* (PDF, internally dated June 2005). Sponsored Projects Office. Live: https://spo.byu.edu/00000190-3687-d777-a591-37af392d0001/rechargecenterpolicyprocedures-pdf · Archived: https://web.archive.org/web/20260307022648/https://spo.byu.edu/policies
2. Brigham Young University, *Unallowable Costs – Guidelines* (PDF, April 1, 2014). Grants & Contracts Accounting. Live: https://spo.byu.edu/00000190-368d-d777-a591-37ad68b10000/unallowablecosts-pdf
3. BYU Sponsored Projects, *Policies* page. https://spo.byu.edu/policies
4. BYU Financial Services – Treasury, *Merchant Services*. https://finserve.byu.edu/treasury/merchant-services · Archived: https://web.archive.org/web/20251211125107/https://finserve.byu.edu/treasury/merchant-services
5. BYU Financial Services – Treasury, *Transact Payments – eMarkets*. https://finserve.byu.edu/treasury/transact-payments-emarkets · Archived: https://web.archive.org/web/20251211123729/https://finserve.byu.edu/treasury/transact-payments-emarkets
6. BYU Financial Services – Treasury, *Square Mobile Credit Card Program*. https://finserve.byu.edu/treasury/square-mobile-credit-card · Archived: https://web.archive.org/web/20251211123450/https://finserve.byu.edu/treasury/square-mobile-credit-card
7. BYU Financial Services – Treasury, *PCI Compliance*. https://finserve.byu.edu/treasury/pci-compliance
8. BYU Financial Services – Regulatory Accounting & Reporting, *Tax Office*. https://finserve.byu.edu/tax-office · Archived: https://web.archive.org/web/20251117044405/https://finserve.byu.edu/tax-office
9. BYU Financial Services – Grants & Contracts Accounting, *Cost Principles Guide*. https://finserve.byu.edu/grants-contracts/cost-principles-guide
10. BYU Sponsored Projects, F&A rate change 50% → 51.5% effective 2022-01-01 (DHHS-audited rate agreement), per https://spo.byu.edu/faqs and https://spo.byu.edu/reports (surfaced in search; verify with SPO).
