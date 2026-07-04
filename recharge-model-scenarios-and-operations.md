# Atomizer Rate Scenarios, Fund Mechanics, Payments, and Work-for-Hire — Q&A

> **Provenance.** This document answers the questions posed by @sgbaird on PR #107
> (2026-07-03/04): rate scenarios for the ~$250k ultrasonic atomizer, the depreciation
> "clock," zero-fee internal pricing, tariffs in the cost base, what recovered funds can
> be used for, break-even under uncertain usage, credit-card friction vs. Stripe, and
> work-for-hire / student-publication interactions. Grounded in the BYU **Recharge Center
> Policy & Procedures** committed in this repo as
> [`byu-recharge-center-policy-and-procedures.pdf`](byu-recharge-center-policy-and-procedures.pdf)
> (page cites refer to that PDF), BYU Financial Services pages, 2 CFR 200.1, and published
> peer-facility rates (Northwestern CHiMaD Metals Processing Facility). Compiled
> 2026-07-04. **Sections 10–11 added 2026-07-04** in response to the follow-up questions
> on research contracts vs. the recharge mechanism (without a center / with a center
> before recovery / after recovery) and on what happens once the equipment is fully
> "cost recovered."
>
> **Status:** Exploratory background research — **not policy or legal/tax advice.**
> Controlling authority is BYU Regulatory Accounting / Financial Services.

---

## 1. When does the depreciation clock start? Is it prorated?

Three separate clocks matter, and only one of them is urgent:

1. **The depreciation schedule itself** runs from the equipment's **in-service date**
   (standard accounting practice; the BYU policy defines the method — "acquisition cost
   of the equipment less residual value divided by its useful life," straight-line only,
   p. 7 — but is silent on start convention). If the atomizer was purchased in ~May 2026
   but commissioned later, the in-service date is what starts the schedule; confirm which
   date the Equipment Inventory Office recorded.
2. **Recoverability** starts only when the center exists with (a) an equipment reserve
   account, (b) a Regulatory Accounting-approved depreciation schedule listing the
   asset number, and (c) approved rates in effect (pp. 6–7). Two clauses make the gap
   costly: "Recharge rates cannot include depreciation from prior years" and equipment
   "cannot be depreciated beyond its useful life … even if the equipment wasn't
   depreciated for each of the five years" (pp. 6–7).
3. **BYU's budget/fiscal year is the calendar year (Jan 1 – Dec 31)** (per the BYU
   Financial Services Budgeting FAQ), so rate years will most naturally align to
   calendar years.

**Practical arithmetic (10-year life, $250k, no residual):** monthly depreciation is
$250{,}000 / 120 \approx \$2{,}083$. It is July 2026 now; if the center's first approved
rates take effect **January 1, 2027**, the forfeited window is only the 2026 stub
(≈ Jun–Dec ≈ **$14.6k** of the $250k). If rates could be made effective within 2026, less
still. On a 5-year life the stub doubles (~$29k). Whether BYU prorates the first year
monthly or uses an annual convention is not stated in the policy — **ask Regulatory
Accounting**, along with the BYU-standard useful life for this equipment class (the policy
allows lives *equal to or longer than* BYU's standard; shorter needs prior approval with
technological-obsolescence justification, p. 7).

**Bottom line:** the loss so far is small, but it accrues monthly. Getting a proposal to
the Chair → Dean → Regulatory Accounting in time for a Jan 1, 2027 rate start caps the
loss at one partial year.

## 2. Illustrative rate scenarios ($250k machine, ~6 h runs)

Assumptions (illustrative only — real numbers come from the rate proposal):

- Depreciation: $25k/yr (10-yr life) or $50k/yr (5-yr life).
- Other fixed pool: maintenance/service contract $10k + allocable admin $5k = $15k/yr.
- Variable cost per run: ≈ $175 (attended operator time at a loaded rate, sonotrode/
  crucible wear, argon, feedstock handling — excludes customer-supplied material).
- Per the policy, **all** usage goes in the denominator, billed or not (p. 4), and
  available hours must be adjusted for downtime/maintenance to get billable units (p. 5).

**Internal (BYU) rate = variable + fixed pool ÷ runs** (10-yr life ⇒ fixed pool $40k/yr):

| Utilization | Runs/yr (~6 h each) | Internal $/run | External federal academic ×1.515 (F&A)† | Non-federal industry |
|---|---|---|---|---|
| Light | 100 (~600 h) | ~$575 | ~$870 | cost+F&A **+ surcharge** |
| Single-shift | 300 (~1,800 h) | ~$310 | ~$470 | up to market |
| Near-continuous | 800 (~4,800 h) | ~$225 | ~$340 | up to market |

† Using the 51.5% F&A figure surfaced earlier — confirm the current negotiated rate with
SPO. With a 5-year life, add ~$83/run at 300 runs/yr (fixed pool $65k).

**Sanity anchor — published peer rates.** Northwestern's CHiMaD Metals Processing
Facility (which runs an AMAZEMET rePowder) publishes **per-run** ultrasonic-atomizer
rates: **$1,075 internal / $1,720 external academic / $2,150 commercial**
(cmpf.northwestern.edu/fees). Their internal rate being ~3× the illustrative single-shift
number above suggests real cost pools are dominated by **staff effort and facility
support**, not depreciation — expect the honest VCL pool to land closer to Northwestern
than to the table's lower rows. AMAZEMET itself sells atomization-as-a-service from
€1,000 minimum orders, another external price anchor. (A UK published rate page was
searched for but not located from this runner; the Northwestern page is the best public
comparator found.)

**Structural notes baked into the policy:** a per-run **minimum fee** for setup/
expendables is expressly permitted with Regulatory Accounting approval (p. 4);
higher-than-internal external rates are expected (institutional overhead is *mandatory*
on externals unless waived, p. 5); and the mostly-external user mix described for the
atomizer is unusual for a "recharge center" as defined ("primarily to internal university
operations and secondarily to external users," p. 1) — worth raising in the proposal so
the center is scoped honestly (this affects UBIT and sales-tax review, §5 of the policy).
Non-US external users are not addressed by the policy at all; export-control screening
(EAR/ITAR — metal AM powders and parameters can be sensitive) and payment/sanctions
screening would be handled by the Office of Research / Legal, not Regulatory Accounting.

## 3. Scenarios for *our own lab's* use

Your own lab is an internal user, and there are three compliant ways to structure its
(startup-funded, non-federal) usage — all three require the runs to be **logged and
counted in the denominator** regardless of billing (p. 4):

1. **Pay the uniform internal rate from startup funds.** Cash cycles startup account →
   center operating account; the depreciation component accumulates in the equipment
   reserve, which can then reimburse the startup account (§8, p. 8). Simple, fully
   auditable, partially round-trips the money.
2. **Subsidize to zero** (see §4 below): the center elects to cover your lab's runs from
   "non-Federal, non-recharge center funds" (p. 5). Costs of those runs are then
   *unrecovered costs* — they cannot shift onto paying users (your usage stays in the
   denominator) and must be tracked for exclusion from any F&A proposal (p. 4).
3. **Take usage as in-kind reimbursement of the $250k investment** (§8, pp. 7–8): the
   account that funded the equipment "can only be reimbursed by receiving services
   without charge or by charging equipment to the recharge center's equipment reserve
   account," capped at the dollar amount invested, with prior Regulatory Accounting
   approval and per-run documentation. Example: 200 own-lab runs/yr valued at a ~$310
   internal rate ≈ $62k/yr of in-kind repayment → the $250k is recouped in ~4 years of
   own use alone, faster if paying external volume also feeds the reserve.

Option 3 is likely the most attractive: it converts the startup outlay into a documented
receivable payable in machine time, without any cash moving. Note the interplay: if your
own lab ever runs a job **charged to a federal award**, that job must be billed at the
uniform internal rate — options 2 and 3 only work for non-federally-funded usage.

## 4. Zero / near-zero internal rates — allowed?

**Yes, with structure.** The policy is explicit on both halves:

- "Recharge Centers do not have to include all of their costs in the rates," provided an
  alternative **non-federal** funding source covers the gap, unrecovered costs are not
  transferred to federal budgets, and they are tracked for removal from F&A proposals
  (pp. 3–4).
- "Recharge Centers should charge for all usage … However, Recharge Centers can elect to
  use non-Federal, non-recharge center funds to pay for the services provided to specific
  users (e.g. students)" (p. 5).

A **blanket** zero/nominal internal rate is uniform by construction (everyone internal
gets the same rate for the same service, p. 4), so the uniform-pricing rule is satisfied.
What it does **not** do is lower external rates: internal usage stays in the denominator,
so the internal share of costs is simply eaten by startup/department funds rather than
reallocated to externals.

**And yes — your read on federal money is right.** The federal cost principles (A-21,
now 2 CFR 200.468) bind charges made **to BYU-administered federal awards**, i.e.
internal users paying with grant money. If an *external* university pays with its own
federal grant, that expense sits on *their* award; BYU's policy handles it by requiring
documented federally-funded externals to be charged **cost + institutional overhead, no
surcharge** (p. 5). So zero-rating internal users while externals (including
federally-funded ones) pay cost+F&A removes the internal federal-charging exposure
entirely — the remaining obligations are honoring the no-surcharge rule for documented
federal externals and keeping the cost basis honest, since external federal auditors can
still question a price that isn't cost-based.

## 5. Can a tariff (import duty) be part of cost recovery?

**Yes, almost certainly — via the depreciable base, not as a separate line.** 2 CFR 200.1
(definition of *acquisition cost*): "Ancillary charges such as taxes, **duty**, protective
in transit insurance, freight, and installation may be included in or excluded from the
acquisition cost in accordance with the recipient's … regular accounting practices."
BYU's policy depreciates "acquisition cost … less residual value" (p. 7). So if BYU's
regular capitalization practice booked the landed cost (invoice + tariff + freight +
installation) to the asset record — which is typical — the tariff depreciates into rates
and is recoverable like the rest of the $250k. **Action:** check what acquisition cost
the Equipment Inventory Office recorded for the asset; if the tariff was expensed
separately rather than capitalized, raise it with Regulatory Accounting before the
depreciation schedule is approved.

## 6. What can you do with recovered funds? Cost including or excluding F&A?

Think of three distinct streams with different rules:

1. **Depreciation recovered through rates** flows (by journal entry) into the **equipment
   reserve account**. Uses: purchase/replace equipment ≥$5k (which *must* be charged to
   the reserve, p. 7) and reimburse the account(s) that funded the equipment (§8). The
   reimbursement cap is hard: "Under no circumstances can the non-recharge accounts that
   … invested in the Recharge Center be reimbursed for more than the dollar amount given"
   (p. 7) — and only as free services or equipment charged to the reserve, never cash
   beyond the investment.
2. **The F&A (institutional overhead) component charged to externals** is the
   *university's* recovery of building/administration costs, not the center's — the
   center's own recoverable base **excludes F&A**. So plan on recovering **up to the
   capitalized acquisition cost (including tariff/freight/installation per §5), not
   cost-plus-F&A**. Where the collected overhead lands (central vs. any departmental
   return) is a Regulatory Accounting question worth asking, but don't build a plan that
   assumes the center keeps it.
3. **Surcharges on non-federal external users** are the one stream allowed to exceed
   cost, and the policy names their permitted uses: "reduce rates charged to users, build
   a working capital reserve, or … finance equipment purchases" (p. 5). This — not
   internal rates, which "cannot add charges to accumulate assets" (p. 5) — is the
   sanctioned way to fund the *next* machine. Charging externals above cost triggers the
   UBIT three-part test (p. 5–6), mitigated to the extent the activity is substantially
   related to the educational/research mission (see §9).

## 7. What if anticipated usage is unknown — or break-even arrives early?

The policy's design already absorbs forecast error; you are not locked to a bad guess:

- Rates are estimates updated **at least annually** (`Annual Rate = Annual Costs / Total
  Annual Usage`, p. 4), and a new rate proposal is required whenever methodology or
  services change significantly (p. 2) — so a mid-year correction is available if usage
  explodes.
- **Over-recovery isn't kept**: surpluses "should be included in the recharge rates for
  the following year" (p. 6) — i.e., next year's rates come down. Deficits likewise roll
  forward (or the department funds them; multi-year recovery plans need approval).
- Break-even is judged **over five years** (p. 3), so a first-year forecast miss is
  expected and non-fatal. What auditors look for is a documented, good-faith methodology
  (the rate proposal must explain how usage was estimated, p. 4), honest logs, and the
  annual true-up actually happening.
- If usage runs hot and the equipment investment is repaid **early**: once cumulative
  depreciation reaches the capitalized cost (or the useful life ends), depreciation drops
  out of the pool and internal rates **must fall** — internal rates can't keep collecting
  to accumulate assets (p. 5). Continued accumulation for replacement is only legitimate
  through external non-federal surcharges (§6.3).

For year one, a defensible approach is: forecast conservatively from committed/likely
users, state the method, and let the annual true-up handle the error in either direction.

## 8. Credit cards: BYU eMarkets vs. Stripe — how much friction?

- **Is payment immediate?** Yes, once set up. Transact **eMarkets Storefront** is a
  hosted online store (think a locked-down Shopify run by Treasury Services): external
  customers pay by card in real time, receipts are automatic, Avalara computes
  destination-based sales tax, and settlements post to the center's GL. It is **not** a
  per-transaction manual process. The *setup* is the one-time cost: a request through
  Treasury Services (Connor Brown for eMarkets), contract/legal review, PCI-DSS training,
  and GL configuration — realistically weeks, not days, and far more than Stripe's
  same-day onboarding, but done once.
- **Stripe (or any self-provisioned processor) is not actually an option** for a
  university unit: all merchant accounts must go through Treasury Services' program,
  card contracts go through Legal/Purchasing, and revenue must land in university
  accounts. A lab-owned Stripe account moving university service revenue would bypass
  merchant policy, PCI scoping, and cash-handling controls.
- **Functionally**, eMarkets gives you 80% of what Stripe would here: card-not-present
  payments at invoice/delivery time, hosted checkout, tax handling. What you give up is
  developer-grade API flexibility (metered billing, saved payment methods, subscription
  logic). **Merchant fees are the department's** — booked monthly to the center's GL —
  and per the earlier analysis they're best absorbed in the external-user surcharge
  rather than surcharged at checkout.
- **One recharge-policy interaction to design around:** "Advanced billing for services or
  products is not allowed" (p. 2). Card payment should occur at or after service
  delivery (or at shipment of powder), not as prepaid credits — the ECL-style wallet
  model needs explicit Regulatory Accounting negotiation.

## 9. Work-for-hire and students publishing on the cloud lab itself

Two distinct senses of "work for hire" are in play, and the cloud-lab research angle
threads between them:

**(a) The fee-for-service sense.** Recharge work *is* work-for-hire-like: an external
user buys a defined deliverable (powder, a build, characterization data) at a posted
rate; there is no negotiated IP, no scholarly co-creation, and — critically — the rate
schedule carries **no publication rights** either way. That cuts both directions: the
customer gets their deliverable and data, and the lab has no default right to publish
customer-specific results, **unless the external-user service agreement says so**. This
is where the student-publication tension gets solved contractually, not by policy
exception. The service agreement template should reserve, up front:

- the right to publish **aggregate/anonymized operational data** about the facility
  (throughput, uptime, remote-access architecture, queue behavior, process windows,
  reliability statistics) — exactly what students building and publishing on the
  cloud-lab infrastructure need;
- an **acknowledgment/citation** expectation when facility-produced materials appear in
  the customer's publications (standard user-facility practice);
- an opt-in path for publishing customer-specific results.

The cleanest prior art is the **national user facility two-tier model**: *non-proprietary*
access (results intended for publication — DOE facilities often make publication a
condition of subsidized access) vs. *proprietary* access (confidential, full cost
recovery + surcharge). Offering both tiers lets federally funded academic externals —
the expected majority — self-select into the publication-friendly tier, which directly
feeds the students' infrastructure papers *and* strengthens the "substantially related to
the exempt educational/scientific purpose" prong of the UBIT test (policy pp. 5–6): if the
external usage generates publications and trains students, the case that it's related
income (not unrelated business) is much stronger.

**(b) The BYU IP/copyright sense.** BYU's copyright policy distinguishes **Scholarly
Works** — owned by the creator, with the university expressly disclaiming work-made-
for-hire ownership — from **Commercial Works** created with university resources, which
are treated as works made for hire and university-owned (see BYU copyright policy,
copyright.byu.edu). Applied here:

- Students' **theses and papers about the cloud lab** are Scholarly Works — theirs to
  publish, as usual.
- The **infrastructure itself** — automation software, control systems, scheduling code,
  hardware modifications built as part of paid/assigned work with university resources —
  is university-owned (Commercial Work / inventions under the IP policy, routed through
  BYU Technology Transfer). That's not a publication obstacle (you can publish about
  university-owned systems), but it matters for open-sourcing components or spinning
  anything out — get Tech Transfer's read early if open-source release of the cloud-lab
  stack is intended.
- **The boundary to watch:** when an external "job" requires real student intellectual
  contribution and contemplates co-authorship or shared invention, it has stopped being
  recharge work and should be papered as a **collaboration / sponsored-research
  agreement** instead (different F&A treatment, negotiated IP and publication terms).
  Routing genuine research through the recharge rate schedule both under-prices it and
  leaves everyone's IP/publication rights undefined.

**Net:** the recharge model and the students' publication agenda are compatible, but only
if (1) the external-user agreement template reserves aggregate-data publication rights
and offers a non-proprietary tier, and (2) research-shaped engagements get routed to
collaboration agreements rather than the rate sheet. Both are worth raising in the same
conversation with Regulatory Accounting / Office of Research that establishes the center.

## 10. Research contracts vs. the recharge mechanism

"Research contract" here means a sponsored agreement negotiated through the Sponsored
Programs Office (SPO) — a statement of work, a budget of direct costs plus F&A at the
negotiated rate, deliverables/reporting, and negotiated IP/publication terms, with funds
landing in a restricted BYU project account. The comparison splits into the three
configurations asked about.

### (a) Without a recharge center (the current state)

A research contract is essentially the **only compliant channel** for external money tied
to atomizer work today (short of gifts, which carry no deliverables, or personal outside
consulting, which doesn't use university equipment). But it has two structural limits as
a cost-recovery vehicle:

1. **No auditable rate exists, so machine time cannot be priced.** The contract budget
   can carry the *inputs* — operator effort, consumables, argon, feedstock — as direct
   costs, but there is no approved per-run or per-hour figure to charge for the atomizer
   itself. The machine effectively rides along at $0.
2. **No capital recovery flows to the lab.** Depreciation on university-owned equipment
   is recoverable on sponsored awards **only through the university's F&A rate** — it is
   expressly barred from recharge-style direct billing *and* from ad hoc direct charges
   (the policy: costs "already reimbursed through the Facilities and Administrative
   (indirect) cost rate" can't be in rates, p. 3; the same consistency principle blocks
   direct-charging it on awards). F&A recovery goes to central university administration,
   not to the startup account. **Without a center there is no mechanism at all by which
   contract dollars repay the $250k.**

Also, using contracts as a *substitute* for a rate structure — repeatedly "contracting"
what is really routine fee-for-service — is a compliance smell: the policy allows direct
sale of goods/services only when "directly and substantially related to the mission"
(p. 1), recurring sales without approved rates invite audit and sales-tax questions, and
each engagement costs weeks of SPO negotiation that a posted rate would avoid.

### (b) With the center, before the cost is recovered

The two mechanisms **compose rather than compete** — and the center makes the contracts
better:

- **Inside a research contract, the BYU project account is an *internal* user.** Machine
  time enters the contract budget as a priced line at the posted internal rate (the
  uniform-rate rule makes this mandatory if the award is federal, and it is the
  consistent treatment for any sponsored account). The sponsor also pays F&A on the
  contract — recharge/service charges sit inside the MTDC base (2 CFR 200.1) — so the
  sponsor's all-in cost per run ≈ internal rate × ~1.5.
- **Contract-funded runs recover capital exactly like external sales.** The internal rate
  carries the depreciation component, which flows into the equipment reserve and, via §8,
  repays the startup account. So during the recovery period, *both* channels amortize the
  $250k; they differ in who pays what on top.
- **Choosing between them for a given external party:**

| Dimension | Research contract (via SPO) | Direct external recharge sale |
|---|---|---|
| Scope | Open-ended research, intellectual contribution, unknowns | Defined deliverable (powder, runs, data) at posted rate |
| Setup time | Weeks–months of negotiation | Immediate (rate sheet + service agreement) |
| Price basis | Budgeted direct costs (incl. machine time at *internal* rate) + negotiated F&A (~51.5%) on MTDC | Cost + institutional overhead; **+ surcharge** if non-federal (pp. 2, 5) |
| Above-cost margin | Fixed-price residuals *may* revert to the department after project close-out (confirm BYU practice with SPO); cost-reimbursable contracts have none | Surcharge on non-federal externals only — the center's one above-cost stream |
| IP / publication | Negotiated per agreement | None by default; governed by the service-agreement template (§9) |
| UBIT | Research income of a university is excluded under IRC §512(b)(8) — a genuine tax advantage for industry-funded *research* | Above-cost external sales must pass the three-part test (policy pp. 5–6) |
| Student involvement | Expected — co-authorship, thesis work | Should be operational only; research-shaped work must be re-papered as a contract (§9b) |

- **The routing rule (restating §9b):** if the engagement needs student intellectual
  contribution, co-authorship, or negotiated IP, it is a contract; if it is a defined
  service at a posted price, it is recharge. The center doesn't replace contracts — it
  gives contracts an auditable machine-time price and gives routine work a channel that
  doesn't burn SPO cycles.

### (c) With the center, after the cost is recovered

Contracts keep working identically, but the machine-time line **gets cheaper** — once
depreciation exits the cost pool (§11), the internal rate drops toward
operating-cost-only, which makes proposals more competitive. The flip side: contract
volume **no longer repays capital**; it only covers operating costs. Whether that's good
(cheaper science) or a problem (no replacement fund) depends on the §11 choices below.

## 11. What happens once the equipment is "cost recovered"?

"Cost recovered" needs one disambiguation first, because two ledgers run in parallel:
(i) **depreciation charged into rates** accumulating in the equipment reserve, and
(ii) **reimbursement of the startup account** under §8 drawing that reserve down (as free
services or equipment purchases, capped at the amount invested, p. 7). Full recovery on
ledger (i) does not automatically mean the startup account has been made whole on (ii).

**The end of recovery is triggered by whichever comes first** (pp. 6–7):

- cumulative depreciation charged into rates reaches the capitalized acquisition cost
  (straight-line, cost less residual over useful life); or
- **the useful life ends** — and there is no catch-up: "Equipment cannot be depreciated
  beyond its useful life … even if the equipment wasn't depreciated for each of the five
  years," and "Recharge rates cannot include depreciation from prior years." If billing
  ran thin, the machine ages out with part of the $250k permanently unrecovered.

Once triggered, five things follow:

1. **The machine keeps running; nothing physical changes.** A fully depreciated atomizer
   can stay in service indefinitely. Its usage is still logged and still sits in the
   rate denominator — it just contributes $0 of capital cost to the numerator.
2. **Rates must come down.** Internal rates are cost-based and break-even over 5 years
   (pp. 3, 5); with depreciation out of the pool, continuing to charge the old rate
   over-recovers, and surpluses are forced into the following year's rates (p. 6). There
   is no "keep charging and pocket the difference" option on internal users — internal
   rates "cannot add charges to accumulate assets" (p. 5). External rates fall too
   (cost + overhead on a smaller cost base); only the **surcharge** on non-federal
   externals may lawfully stay above cost.
3. **§8 reimbursement hits its hard cap.** "Under no circumstances can the non-recharge
   accounts that gave money to/invested in the Recharge Center be reimbursed for more
   than the dollar amount given" (p. 7). Once the startup account has received $250k of
   free services/equipment value, that channel closes permanently.
4. **Replacement funding must come from outside internal rates.** The sanctioned sources:
   whatever balance remains in the equipment reserve; **surcharges on non-federal
   externals** (expressly usable "to finance equipment purchases," p. 5); proceeds from
   selling the old machine (all sale proceeds and gain/loss are booked to the equipment
   reserve, p. 7); or a fresh departmental/startup investment — which restarts the §8
   cycle on the new asset. Note the strategic tension: **the reserve cannot both fully
   repay the startup account and pre-fund the successor machine** unless external
   surcharge volume covers the difference — and with the expected user mix (mostly
   federally-funded academic externals, who pay cost + overhead with *no* surcharge),
   the surcharge base is thin. That argues for deliberately leaving part of the reserve
   unreimbursed, or courting some non-federal industry volume, if a successor machine is
   the goal.
5. **Buying the replacement restarts the cycle.** Equipment ≥$5k must be charged to the
   equipment reserve (p. 7), a new Regulatory Accounting-approved depreciation schedule
   is set up for the new asset number, depreciation re-enters the cost pool, and rates
   step back up for the next recovery period.

**Net:** "cost recovered" is not an end state where the center banks profit — it's a
regime change where rates drop to operating cost, the capital-repayment channel closes,
and the only lawful accumulation for the future runs through the equipment reserve and
non-federal external surcharges. Planning the reserve-vs-reimbursement split *before*
that point is the main strategic decision the policy leaves to the center.

---

## References

1. BYU, *Recharge Center Policy & Procedures* — committed as [`byu-recharge-center-policy-and-procedures.pdf`](byu-recharge-center-policy-and-procedures.pdf); page cites above refer to this PDF.
2. BYU Financial Services, *Budgeting FAQ* (budget year = Jan 1 – Dec 31). https://finserve.byu.edu/2024/budgeting-faq
3. 2 CFR § 200.1, definitions of "acquisition cost" (ancillary charges incl. taxes, duty, freight, installation) and "modified total direct costs" (MTDC — services are in the F&A base; equipment/capital expenditures are excluded). https://www.law.cornell.edu/cfr/text/2/200.1
4. Northwestern CHiMaD Metals Processing Facility, fee schedule (ultrasonic atomizer per-run rates: $1,075 NU / $1,720 external academic / $2,150 commercial). https://cmpf.northwestern.edu/fees/ and equipment page https://cmpf.northwestern.edu/equipment/amazemet-repowder-ultrasonic-atomizer-2/
5. AMAZEMET, atomization-as-a-service (from €1,000 minimum). https://www.amazemet.com/amazemet-new-business-line-atomization-service/
6. BYU Copyright Policy (Scholarly vs. Commercial Works; work-made-for-hire treatment). https://copyright.byu.edu/00000172-140d-dbd3-a3f3-5d9d9ed50000/exhibit-b-current-copyright-policy
7. Georgia Tech Advanced Manufacturing Pilot Facility, AMAZEMET rePowder listing. https://ampf.research.gatech.edu/amazemet-repowder
8. IRC § 512(b)(8) — exclusion from unrelated business taxable income of research income of a college, university, or hospital "performed for any person." https://www.law.cornell.edu/uscode/text/26/512
9. Companion documents in this repo: `recharge-model-byu-official-docs.md` (policy assessment), `recharge-model-followup.md` (approvals, admin, credit cards, nonprofit intermediary), `recharge-model-exploration.md` (compliance framework and rate-setting literature).
