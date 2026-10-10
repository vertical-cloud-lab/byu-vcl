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
> "cost recovered." **Sections 12–15 added 2026-07-04** in response to the follow-up
> questions on the meaning of "non-federal external user"/"surcharge if non-federal",
> embargo-tiered pricing in the service agreement (and its interaction with student
> time), reinvesting recovered funds and payment-friction losses, and whether the
> department/college-funded renovation tied to the equipment is recoverable.
> **Section 16 added 2026-07-04** in response to the follow-up question on total
> customer-side revenue required to reach full cost recovery under single-payer-category
> scenarios (internal / federal external / non-federal external / research contracts).
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

## 12. What "surcharge if non-federal" and "non-federal external user" mean

The policy prices a job by **whose money pays for it**, not by who the customer is. Three
tiers (pp. 4–5):

1. **Internal (BYU) users** — any job paid from a BYU account (speedtype). Uniform,
   cost-based rate; no overhead, no surcharge.
2. **External users who document federal funding** — "Rates to external users who
   identify themselves as federally-funded and provide documentation should be set to
   recover cost plus institutional overhead. Appropriate documentation includes a copy of
   the federal award approval or award number that is paying for the services" (p. 5).
   Cost + F&A, **no surcharge**.
3. **Non-federal external users** — the policy's phrase is "non-University, non-Federal
   agency users" (p. 5): anyone outside BYU whose payment is *not* traceable to a federal
   award. This is where the optional **surcharge** lives: "'Surcharges' can be added to
   rates charged to non-University, non-Federal agency users. These surcharges can be
   used to reduce rates charged to users, build a working capital reserve, or to finance
   equipment purchases" (p. 5).

Key clarifications:

- **"Non-federal" describes the funds, not the entity.** A state-university lab paying
  with its NSF award (documented) is a *federal* external → cost + F&A, no surcharge.
  The *same lab* paying from departmental funds, a foundation grant, or an industry
  gift account is a *non-federal* external → surcharge permitted. Companies,
  foundations, individuals, and (if allowed at all — export-control screening first)
  foreign entities are non-federal externals by default.
- **Why the line exists:** the federal cost principles let federal money be charged only
  cost-based prices — the government does not pay a university service center a margin.
  Non-federal payers face no such restriction, so the surcharge is the policy's one
  sanctioned above-cost stream (with UBIT review once externals are charged above cost,
  pp. 5–6).
- **The burden of proof is the user's.** A workable menu is: posted external price =
  cost + F&A + surcharge, with the surcharge *removed* when the user supplies the award
  number/approval. Users who don't document federal funding simply pay the full external
  price.

## 13. Embargo-tiered pricing in the service agreement — and student time

**Short answer: yes, an expiring data-release embargo is a normal contractual object, and
a priced embargo menu is workable — but the *premium* must ride on the surcharge, which
constrains who can buy it.**

### Is an expiring embargo even possible in this kind of agreement?

Yes — it's standard practice, not exotic. Sponsored-research agreements routinely carry
publication-delay clauses (30–120 days for patent review, sometimes longer); DOE national
user facilities run exactly a two-tier system (non-proprietary access with expected
publication vs. proprietary access with confidentiality at full cost recovery); and
journal/repository data embargoes of 6–24 months are commonplace. Nothing in the BYU
recharge policy addresses data terms at all — that's the service agreement's job, and an
"facility may publish run data after N months; customer may purchase a longer N" clause
is well within it. A customer *lessening or waiving* their own embargo is trivially fine
(unilateral relaxation in the facility's favor).

### Can the price vary with embargo length?

Split by user tier, because the pricing rules differ:

- **Non-federal externals: yes, cleanly.** The embargo premium is exactly what a
  surcharge is — an above-cost charge on non-University, non-federal users — and its
  permitted uses (reduce rates, working capital, equipment purchases, p. 5) fit. A
  posted menu (e.g., release at 30 days = base; +6 mo / +12 mo / +24 mo / indefinite at
  increasing premiums) applied consistently to all non-federal externals is defensible.
  The policy imposes uniformity on *University* users (p. 4), not on externals, but a
  published, consistently applied menu is the right practice anyway (and keeps UBIT
  accounting clean — embargo premiums are above-cost income, and an *indefinite*
  embargo/proprietary tier is the hardest to defend as "substantially related" to the
  educational mission, pp. 5–6).
- **Documented-federal externals: only cost-based differences.** They pay cost + F&A
  with no surcharge, so a non-cost embargo premium can't be charged to them. Two clean
  designs: (a) give the federal tier one standard embargo term at no premium, sized to
  cover normal patent/publication needs; or (b) adopt the DOE pattern — the
  indefinite/proprietary tier simply *is* the full-cost-plus-surcharge product,
  effectively unavailable to federal money (which typically shouldn't be buying
  proprietary confidentiality anyway). A genuinely cost-based confidentiality charge
  (secure storage, restricted-access handling labor) may be charged to anyone if it's in
  the approved rate as a distinct service — but such costs are usually small.
- **Internal users: fixed, cost-based, uniform.** Internal rates can't carry a non-cost
  premium at all ("cannot add charges to accumulate assets," p. 5), so there is no
  internal embargo *menu*. That matters less than it sounds: internal researchers' data
  is their own research output — the embargo menu is really about the *facility's*
  reserved right to publish operational/run data from external jobs (§9a).

So: **not** a single fixed price with one immutable embargo for everyone — a tiered menu
is fine — but the paid tiers live on the non-federal external side, and internal +
federal-external tiers get standard terms.

### Does this allow student time?

Two senses, both favorable:

1. **Student labor in the rate: yes, regardless of embargo.** Student operator/technician
   wages are ordinary allowable costs of operating the center and belong in the cost pool
   like any staff effort — embargoed jobs don't change that.
2. **Student research/publication: an *expiring* embargo largely dissolves the §9
   tension.** Every finite-embargo job eventually joins the publishable corpus, so the
   students' infrastructure papers (throughput, reliability, remote-access architecture)
   can draw on aggregate operational data immediately (reserve that right in the
   template, §9a) and on run-level data as embargoes lapse. Publication is delayed, not
   excluded. Design cautions: match embargo lengths to student timelines (a 24-month
   embargo can outlive a Master's student — thesis chapters may need the
   aggregate/anonymized layer instead; BYU's ETD process allows time-limited delayed
   release, confirm current terms with Graduate Studies); keep the **indefinite** tier
   operator-only (no student intellectual contribution — that work belongs in a
   sponsored-research agreement per §9b, and standing confidential work can also erode
   the fundamental-research posture relevant to export control); and note that heavy
   proprietary volume weakens the UBIT "related to educational purpose" defense that
   student involvement otherwise strengthens.

## 14. Reinvesting recovered funds — and how much actually leaks

### Can recovered funds buy new/upgraded equipment, long-term?

**Yes — that's what the equipment reserve is for, and it's self-renewing.** Equipment
purchases ≥ $5,000 *must* be charged to the reserve (p. 7); a ≥ $5,000 capital upgrade to
an existing machine belongs there the same way. Each new/upgraded asset then gets its own
Regulatory Accounting-approved depreciation schedule and depreciates into rates in turn
(no double recovery — the reserve spent previously *recovered* depreciation; the new
asset's cost was never itself in rates). That loop can run indefinitely: recover
depreciation → reserve → replace/upgrade → depreciate the replacement → …

Two structural limits on using it as a *growth* engine:

- **Internal rates only return capital, they don't grow it.** Depreciation recovers
  historical cost, and internal rates "cannot add charges to accumulate assets" (p. 5).
  So internal volume can sustain the *existing* capital base (in nominal dollars), not
  expand it.
- **Expansion money comes from three places only:** the surcharge on non-federal
  externals (expressly usable "to finance equipment purchases," p. 5), proceeds from
  selling old equipment (booked to the reserve, p. 7), and fresh
  departmental/startup investment (which opens a new §8 repayment claim). And the
  reserve can't simultaneously repay the startup account in full *and* fund the next
  machine (§11.4) — the reimbursement-vs-reinvestment split is a real allocation choice.

### What's the net deficit to the base amount? Is it ~3% for credit cards?

**No — card fees are not 3% of the invested base, and with sane design they net to ~0.**
Where the money can actually leak:

1. **Card/merchant fees: ~2–3% of card-paid revenue only, and recoverable.** Internal
   users settle by journal entry (zero friction). Only external revenue collected by card
   bears the fee, and the fee is an ordinary operating cost of the center: absorb it in
   the non-federal surcharge (net leakage ≈ 0) or include it in the cost pool (recovered
   through rates; spread across users). Large external jobs can be invoiced/ACH through
   Accounts Receivable and skip card fees entirely. Worst case — the center chooses to
   eat unrecovered fees — the loss is 3% × (card-collected revenue), which becomes a
   deficit rolled into next year's rates (p. 6), not a haircut on the $250k claim.
2. **The stub-year loss (§1): the one true haircut so far.** Depreciation before rates
   are effective is permanently unrecoverable (~$2,083/month on a 10-year life until
   rates start).
3. **Under-utilization risk:** if billed volume runs thin over the useful life, the
   machine ages out with the shortfall permanently unrecovered (§11) — recovery is
   volume-dependent, not guaranteed.
4. **Nominal-dollar recovery:** the §8 cap is "the dollar amount given" (p. 7) — no
   interest or inflation adjustment, so a $250k recovered over ~10 years comes back
   lighter in real terms, and straight-line on historical cost under-funds a
   more-expensive successor machine.
5. **F&A goes to central:** the institutional-overhead component collected from
   externals is the university's, not the center's (§6.2) — it was never part of the
   recoverable base, but don't count it as center revenue.

**Net:** payment friction is a rounding error if priced in; the real erosion risks are
timing (item 2), volume (item 3), and inflation (item 4).

## 15. Is the department/college-funded renovation recoverable?

**Default answer: not through recharge rates — with one genuine carve-out worth pursuing.**

- **The policy excludes building costs from rates.** Unallowable: "Building depreciation,
  rent, and operations and maintenance not paid by recharge center. (Only costs incurred
  by the recharge center can be included in rates.)" (p. 3). A renovation is normally
  capitalized as a building improvement, and the center didn't pay for it — doubly
  excluded. The policy's lone exception (animal care facilities, p. 3) underlines that
  facility costs are includable only by explicit exception.
- **The F&A double-recovery bar is the deeper reason.** Capitalized building improvements
  typically enter the university's building-depreciation pool inside the negotiated F&A
  rate, and "any costs already reimbursed through the Facilities and Administrative
  (indirect) cost rate" cannot also be in recharge rates (p. 3). So the university *does*
  recover the renovation — through the ~51.5% overhead charged on federal awards and
  external users — it just flows to central administration, not back to the department or
  college. (Whether BYU has any F&A return/distribution that shares it with colleges is a
  question for the Controller/Regulatory Accounting.)
- **The carve-out: equipment installation costs.** 2 CFR 200.1 lets "ancillary charges
  such as taxes, duty, protective in transit insurance, freight, and **installation**" be
  capitalized into the *equipment's* acquisition cost per the institution's regular
  practice — and BYU depreciates "acquisition cost … less residual value" (p. 7). Parts
  of the renovation that exist only to install and operate this specific machine —
  rigging, dedicated electrical service, inert-gas plumbing, equipment-specific
  ventilation/exhaust — are candidates for capitalization into the atomizer's asset
  record rather than the building's. Whatever lands on the equipment asset record
  depreciates into rates like the rest of the $250k and becomes §8-reimbursable to the
  accounts that paid. **The decisive fact is how Fixed Assets / the Equipment Inventory
  Office booked the renovation** — if the equipment-specific portion sits on a building
  asset today, raise reclassification with Regulatory Accounting *before* the
  depreciation schedule is approved; after approval it's much harder.
- **The §8 route doesn't rescue the rest.** Reimbursement is capped at "the dollar amount
  given to the Recharge Center" (p. 7), and money spent on the *building* before any
  center existed is not obviously an "investment in the Recharge Center." Even if
  Regulatory Accounting entertained counting it, reimbursement value has to be generated
  by costs that lawfully flow through rates — which circles back to the building-cost
  exclusion. Treat general renovation spend (walls, general HVAC, finishes, code
  upgrades) as sunk departmental investment recovered, if at all, via central F&A.

**Action items:** get the renovation's accounting treatment (building asset vs. equipment
asset vs. expensed) from Fixed Assets; inventory which line items are genuinely
machine-specific installation; and put the capitalization question to Regulatory
Accounting in the same conversation as the depreciation schedule (§1).

## 16. Total revenue required for full cost recovery, by payer category

The question: if 100% of usage were paid by a single payer category X, how much money
must *customers* put in (gross, their side) for the center to reach full cost recovery?
The categories price differently, and — critically — **not everything the customer pays
counts toward recovery**: F&A goes to central administration (§6.2), card fees go to the
processor (§14.1), and surcharge is above-cost extra. The center's recovery requirement
is the same in every scenario — the cost pool — so the differences are pure gross-up.

### (a) The per-dollar gross-up table

Customer-side payment required per **$1.00 the center must keep** (using 51.5%
institutional overhead† and ~2.9% card fees):

| Payer category X | Customer pays | Center keeps | Central (F&A) | Processor |
|---|---|---|---|---|
| Internal BYU (journal entry) | **$1.00** | $1.00 | — | — |
| Federal external, invoice/ACH | **~$1.52** | $1.00 | $0.515 | — |
| Federal external, credit card‡ | **~$1.58** | $1.00 | ~$0.53 | ~$0.05 |
| Non-federal external, invoice, no surcharge | **~$1.52** | $1.00 | $0.515 | — |
| Non-federal external, card, fee-covering surcharge | **~$1.56** | $1.00 | $0.515 | ~$0.05 |
| Non-federal external + 20% growth surcharge (invoice) | **~$1.72** | $1.20 | $0.515 | — |
| Research contract, federal cost-reimbursable (per $1 of machine time) | **~$1.52** | $1.00 | $0.515 | — |
| Research contract, industry fixed-price | negotiated ≥ ~$1.52 | $1.00 (+ possible residual) | $0.515 | — |

† 51.5% is the negotiated research F&A figure surfaced earlier; whether external *sales*
carry that exact rate (and on what base) is a Regulatory Accounting question — it is the
single most sensitive number in this table. ‡ Federal externals can't be surcharged
(p. 5), so their card fees must be absorbed as an ordinary cost of the center and
recovered through everyone's rates — hence the gross-up: cost portion ×
1/(1 − 0.029 × 1.515) ≈ ×1.046, i.e. customer-side ≈ 1.046 × 1.515 ≈ 1.58.

Two structural takeaways: (1) internal dollars are ~34% more "efficient" at recovery than
external dollars from the customer's perspective — external users pay ~$1.52–1.58 for
every $1 that reaches the center; (2) research contracts behave *identically* to federal
external sales for the machine-time line (internal rate + F&A on MTDC, §10b) — the
contract just wraps other budget lines (student salaries, materials, each also bearing
F&A) around it.

### (b) Whole-life worked example (illustrative §2 assumptions)

$250k machine, 10-year life, 300 runs/yr (single-shift), $15k/yr other fixed, $175/run
variable → **lifetime cost pool ≈ $925k** ($250k capital + $150k fixed + $525k variable),
3,000 runs, internal rate ≈ $308/run. Total customer-side revenue for full recovery if
all usage were category X:

| All usage paid by… | Lifetime gross revenue | Per run | Of which reaches the center |
|---|---|---|---|
| Internal BYU users | **$925k** | ~$308 | $925k |
| Federal externals (invoice) | **~$1.40M** | ~$467 | $925k |
| Federal externals (all card) | **~$1.47M** | ~$489 | $925k (≈$64k recycled fees) |
| Non-federal externals (card + fee surcharge) | **~$1.44M** | ~$481 | $925k |
| Non-federal externals (+20% surcharge, invoice) | **~$1.59M** | ~$529 | $1.11M ($185k growth funds) |
| Federal research contracts (machine-time share) | **~$1.40M** | ~$467 | $925k |

If you only care about the **$250k machine** (the depreciation slice of revenue): $250k
of internal billings / ~$379k of federal-external gross (~$396k if all card) /
~$379k+ of non-federal gross / ~$379k of contract machine-time gross — central keeps
~$129k of F&A in every external case.

**Scale caution (§2's Northwestern anchor):** if the honest cost pool lands near
Northwestern's $1,075/run internal rate, multiply everything ≈3×: lifetime pool ≈$3.2M
internal / ≈$4.9M federal-external gross — and the $250k machine is then only ~8% of
lifetime revenue. "Full cost recovery" is mostly about recovering *operating* costs
year-by-year; the capital piece is the small, slow slice.

### (c) The timing constraint — volume can't accelerate the $250k

Recovery of capital is **paced by the depreciation schedule, not by revenue**: $25k/yr
enters rates on a 10-year life ($50k/yr on an approved 5-year life), and if volume runs
hot the surplus rolls back into next year's rates (p. 6) rather than accelerating
repayment (§7, §11). So under *any* payer mix, plan on the full useful life to recover
the full $250k through rates. The only levers that move faster: a justified shorter
useful life (prior approval, p. 7), the non-federal surcharge (above-cost by design), and
§8 in-kind repayment via free services to the funding account (§3.3) — which trades
billable revenue for repayment credit.

### (d) Assumptions and variables to nail down

1. **The external overhead rate and base** — is it the negotiated 51.5% research F&A,
   applied to the full cost-based price? This swings external gross by hundreds of $k.
2. **Exclusivity** — "all costs from X" assumes X is 100% of the *denominator*. Every
   unbilled own-lab run (subsidized or §8 in-kind) removes its share of the pool from
   what X's revenue can recover; the shortfall stays with you (§4).
3. **True staffing costs** — the dominant unknown (Northwestern anchor, §2).
4. **Card-fee rate and payment mix** — 2.5–3.5% depending on card type/eMarkets
   schedule; large jobs invoiced via ACH eliminate the leak (§14.1).
5. **Utah sales tax** on tangible product (powder) sold to industry — collected on top
   via Avalara; a sticker-price increase, not revenue (Tax Office question).
6. **UBIT** — ~21% federal tax on *net* surcharge income if the activity is unrelated
   (§6.3, §13); shave the growth-surcharge stream accordingly unless the related-purpose
   defense holds.
7. **Bad debt is unallowable** in rates — a defaulting external is a straight loss the
   pool can't absorb; require POs/prepay-at-delivery discipline (but no *advance*
   billing, p. 2).
8. **The stub-year loss** (~$14.6k, §1) and **nominal-dollar recovery** (§14.4) are
   haircuts on the $250k that no payer category fixes.
9. **Non-US users** — wire/currency costs plus export-control screening (§2); treat as
   non-federal externals and price the friction into the surcharge.

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
9. DOE Office of Science, user facility user agreements — non-proprietary (publication expected) vs. proprietary (confidential, full cost recovery) access tiers. https://science.osti.gov/User-Facilities/Policies-and-Processes/Agreements
10. Companion documents in this repo: `recharge-model-byu-official-docs.md` (policy assessment), `recharge-model-followup.md` (approvals, admin, credit cards, nonprofit intermediary), `recharge-model-exploration.md` (compliance framework and rate-setting literature).
