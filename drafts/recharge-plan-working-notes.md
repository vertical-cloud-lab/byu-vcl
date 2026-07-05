# VCL Recharge Plan — Working Notes (Version 2: Full Detail)

> **Status: DRAFT — exploratory working notes, not policy, not legal/tax advice.**
> This is the detailed edition: every calculation, assumption, note-to-self, and
> the point-by-point disposition of the Edison Scientific review of 2026-07-04
> ([`recharge-model-edison-feedback.md`](../recharge-model-edison-feedback.md)).
> The readable edition with the headline numbers is
> [`recharge-plan-overview.md`](recharge-plan-overview.md) (Version 1).
> Page cites = BYU *Recharge Center Policy & Procedures*
> ([PDF](../byu-recharge-center-policy-and-procedures.pdf), June 2005; currency
> unconfirmed — open question #1 in
> [`questions-for-regulatory-accounting.md`](questions-for-regulatory-accounting.md)).

---

## 1. Edison review — disposition table

Every finding, what we did with it, and where.

### (A) Correctness findings

| # | Finding (condensed) | Disposition |
|---|---|---|
| A1 | Renovation reclassification stated too confidently; dedicated electrical/gas/ventilation may be building systems; double-recovery risk vs. F&A (Policy p. 3; 2 CFR 200.468) | **Adopted.** Language in `equipment-depreciation…` §3 and `rate-proposal-cy2027.md` A1/§4 changed to "may be included only if Fixed Assets and Regulatory Accounting determine the item is capitalized to the equipment asset under BYU's regular accounting practices and is excluded from building/F&A recovery." Decision tree in §6 below. |
| A2 | Tariff/duty fine *only if* consistent with BYU's regular capitalization practice | **Adopted.** Already conditioned in the equipment package §2; consistency requirement noted in §6. |
| A3 | $306/run materially understates labor; Northwestern comparator $1,075 internal; gap ~$234.5k/yr at 305 runs | **Adopted.** Pool rebuilt with staffing scenarios (§3); planning headline moved to ~$836/run; time-study protocol in §10; "freeze quotes" note added everywhere. |
| A4 | Don't present a zero/near-zero internal rate as *the* rate; keep a gross cost-based approved rate + documented subsidy/credit | **Adopted.** Establishment proposal §7 and rate proposal §7 now state the approved internal rate is always the cost-based rate; own-lab usage recorded as gross rate + (§8 credit \| subsidy \| payment). Question 13 reframed. |
| A5 | Embargo menu OK as non-federal surcharge, but §5.3's default "BYU may publish Run Data after 30 days" overreaches; DOE binary model is the precedent; no prior art for a 6/12/24-mo ladder | **Adopted.** Service agreement §5 rewritten: standard tier = aggregate/anonymized only, customer-specific Run Data by written consent; year-one menu = standard + proprietary; timed ladder deferred to after first annual review (§7 below). |
| A6 | §8 in-kind credit may not be worth the full internal rate; get a written valuation ruling | **Adopted.** Valuation options analyzed in §5 below (the answer swings repayment from ~1.5 yr to >useful life); "~4 years" claim withdrawn; question 8 sharpened. |
| A7 | Federal-external classification needs more than an award number: certify the service will be charged to that award and the institution permits it; mixed-fund intermediaries ambiguous | **Adopted.** Service agreement Appendix A strengthened. Mixed-fund/nonprofit-intermediary orders default to non-federal pricing pending documentation. |
| A8 | Card fees can't be casually assigned to federal users; no lab-owned processors; no convenience fee without Treasury confirmation | **Adopted.** Rate proposal §5 note and service agreement §3 now carry the exact recommended language. |

### (B) Gaps → new program elements

| # | Gap | Disposition |
|---|---|---|
| B1 | EHS / combustible-metal-powder controls absent (NFPA 484) | **Adopted — biggest gap.** EHS added to kickoff, readiness gate, establishment proposal §8, and questions doc (new EHS section). See §8.1. |
| B2 | Export-control mechanism thin (deemed export via remote access) | Workflow sketched in §8.2; screening appendix already in service agreement; added to kickoff + questions. |
| B3 | Cyber/data-security classification missing | Draft position in §8.3; clause to add to service agreement at OGC review. |
| B4 | No failed-run/rework policy | Draft position in §8.4; placeholder added to service agreement §4. |
| B5 | Per-run billing too coarse | Analysis in §4.3 (unbundling vs. simplicity); year-one decision: keep per-run + overage hours; revisit at first annual review. |
| B6 | No queue-priority policy | Draft posted-priority order in §8.5. |
| B7 | No bad-debt/credit controls (bad debt unallowable in federal pools) | Draft controls in §8.6; PO-required clause already in service agreement §3.4. |
| B8 | Sales-tax characterization needs Tax Office determination | Added to questions (powder = likely tangible personal property). |
| B9 | No insurance/product-liability review | Added to OGC scope + questions. |
| B10 | No segregation-of-duties | Draft matrix in §8.7. |
| B11 | No record-retention schedule | Draft schedule in §8.8. |
| B12 | Policy currency unresolved | Unchanged as open question #1 — gate on it at kickoff. |

### (C) Defensibility rulings — how we now treat the six risky interpretations

1. **Tariff/duty**: include *if* booked to the asset per regular practice — strong. **Renovation**: rigging/vendor-install strong; dedicated electrical/gas/ventilation weak-to-moderate; treat as Fixed Assets' call, not ours.
2. **Zero internal rate**: dead as a framing. Gross approved rate + explicit subsidy/§8 credit only.
3. **Embargo ladder**: legally plausible, operationally risky, zero prior art → deferred; binary standard/proprietary at launch (DOE pattern).
4. **§8 in-kind at full rate**: possible but unproven → written ruling before any projection.
5. **Majority-external *billed* base**: audit-sensitive mismatch with "primarily internal" definition (p. 1) → disclosed up front in establishment proposal §1; scoping guidance requested.
6. **Nonprofit intermediary**: high-risk, **not pursued in year one**; if it ever appears as a customer, priced non-federal/commercial pending ultimate-beneficiary documentation.

### (D) Strategy changes

Adopted wholesale: quote freeze; July–Aug time study; single cross-functional kickoff; asset decision first; one clean own-lab structure; two-column conservative rate submission; narrowed year-one menu; Nov–Dec readiness gate; **quarterly** CY2027 reviews with revision triggers (>20% labor variance, >25% utilization variance, material mix change — Edison's suggested thresholds, which are judgment calls, not policy). `README.md` resequenced to match.

---

## 2. Assumptions register (revised)

| # | Assumption | Value | Status / verify with |
|---|---|---|---|
| A1 | Capitalized acquisition cost (invoice + tariff + freight + installation; renovation items **only if Fixed Assets capitalizes them to the equipment asset and they are excluded from building/F&A recovery**) | **$250,000** placeholder | Fixed Assets / Equipment Inventory |
| A2 | Useful life, straight-line, no residual | **10 yr** | Regulatory Accounting (BYU class standard) |
| A3 | In-service date | ~June 2026 | Equipment Inventory |
| A4 | First-year proration | monthly | Regulatory Accounting (policy silent) |
| A5 | External overhead | **51.5%**, base unconfirmed | SPO — *single most sensitive external assumption* |
| A6 | Run duration | ~6 machine-h | instrument log |
| A7 | CY2027 usage | **305 runs** (200 own-lab / 5 other internal / 70 federal-ext / 30 non-federal-ext) | usage log + letters of interest |
| A8 | Maintenance/service | $10,000/yr | vendor quote |
| A9 | Center-specific admin/supplies | $5,000/yr | department |
| A10 | **Staffing** | **scenario variable — see §3** (was: 2 h × $30/h buried in variable cost) | time study |
| A11 | Non-labor variable cost/run | **$115** (argon 45, sonotrode/crucible wear 55, packaging/consumables 15) | operating experience |
| A12 | Loaded FTE cost | $90,000/yr | department HR |
| A13 | Card fees | ~2.9% of card-paid external revenue | Treasury |

Note-to-self: A10 restructure means the old "$175 variable" is retired — don't
mix the two pools when comparing against the superseded
[`rate-proposal-cy2027.md`](rate-proposal-cy2027.md) numbers.

## 3. Cost pool and rate scenarios

**Fixed, non-staff:** depreciation $25,000 + maintenance $10,000 + admin $5,000 = **$40,000/yr**
**Variable, non-labor:** $115/run × 305 = **$35,075/yr**
**Staff:** scenario S FTE × $90,000

Internal rate = ($40,000 + S×$90,000 + $35,075) / 305:

| Scenario | Staff $/yr | Pool $/yr | **Internal $/run** | Federal ext ×1.515 | Note |
|---|---|---|---|---|---|
| Floor (old draft: 2 h student labor only, no staff) | ~$18k in variable | $93,375 | **$306** | $464 | **Document as floor; never quote** |
| 1.0 FTE | 90,000 | 165,075 | **$541** | $820 | Edison's low anchor |
| 1.5 FTE | 135,000 | 210,075 | **$689** | $1,044 | |
| **2.0 FTE (planning basis)** | 180,000 | 255,075 | **$836** | $1,267 | Northwestern-consistent; headline in Version 1 |

Depreciation component: $25,000 / 305 = **$82/run** → equipment reserve, billed runs only.

**Volume sensitivity at 2.0 FTE** (rate = $220,000/N + $115):

| Runs/yr N | Internal | Federal ext |
|---|---|---|
| 150 | $1,582 | $2,397 |
| **305** | **$836** | **$1,267** |
| 500 | $555 | $841 |
| 800 | $390 | $591 |

Note-to-self: the staffed model is *much* more volume-sensitive than the old
draft ($40k fixed → $220k quasi-fixed). If external demand disappoints, the
year-one deficit is real money; that's the argument for the quarterly reviews
and for a conservative denominator at submission.

**5-year-life variant** (if approved with obsolescence justification, p. 7):
fixed non-staff $65,000 → 2.0 FTE internal = **$918/run**; doubles capital
recovery to $50k/yr.

**Two-column submission format** (Edison D6): Column A = floor ($306, minimum
documented cost); Column B = time-study-supported staffed rate (planning: $836).
Submit B as the proposed rate; A exists to show the pool floor transparently.

### 3.1 Suggested posted schedule (planning; final = exact pool ÷ usage)

| Tier | Planning $/run | Construction |
|---|---|---|
| Internal (uniform, p. 4) | **$836** | pool ÷ 305 |
| External, documented federal | **$1,267** | $836 × 1.515; **no surcharge** (p. 5) |
| External, non-federal — standard | **$1,500** | $1,267 + ~$233 surcharge (~18%) |
| External, non-federal — proprietary | **$1,900** | $1,267 + ~$633 surcharge |
| Minimum fee / initiated job | **$150** | initiation costs (p. 4) |

Sanity anchors: Northwestern $1,075 / $1,720 / $2,150 per run (same instrument
class); UW ME unbundled (Arcam $45–90/h + powder $224–282/kg + engineer
$99–173/h); LSU Mlab $36–60/h; UMass ADDFab daily rates. We sit below
Northwestern at each tier — defensible for a newer, lower-overhead operation,
but the time study decides.

Surcharge income accounting note-to-self: track separately (p. 5 uses: reduce
rates / working capital / equipment purchases); it is the **only** above-cost
stream; net surcharge income is the UBIT-relevant quantum (~21% federal rate on
net unrelated income if the related-purpose position fails) — Tax Office review.

### 3.2 CY2027 cash walk at planning rates (note-to-self)

Billed runs = 105 (5 int + 70 fed-ext + 30 nonfed-ext):

- Cash in: 5×$836 + 70×$1,267 + 30×$1,500 = $4,180 + $88,690 + $45,000 = **$137,870**
- Of which central's F&A: 100 ext runs × $431 = **$43,100** (not the center's)
- Center keeps: 105×$836 cost recovery = $87,780 + 30×$233 surcharge = $6,990 → **$94,770**
- Pool = $255,075 → **unrecovered ≈ $167,295** = exactly the 200 own-lab runs'
  share (200 × $836). This is the documented subsidy / §8 in-kind quantum —
  someone (startup/department) must be shown covering it (pp. 3–5), tracked and
  excluded from F&A proposals (p. 4).
- Reserve deposits: 105 billed × $82 = **$8,610/yr** (thin — see §5 tension).
- Card-fee leak: if all 30 non-federal jobs pay by card, ~2.9% × $45,000 ≈
  **$1,305** — absorbed by the surcharge. Federal externals steered to
  invoice/ACH; if one insists on card, fee is center operating cost (recycled
  through the pool), never a per-transaction add-on (Edison A8).

## 4. Rate-design notes

### 4.1 Why not unbundle (yet)

Edison B5 + UW prior art favor unbundling (machine-h + powder + engineer-h +
consumables + hazard surcharge). Counterweights: year-one audit simplicity, the
minimum-fee mechanism already covers setup asymmetry, and our jobs are
homogeneous (6-h aluminum runs) until the alloy menu grows. **Year-one
decision: single per-run rate + posted overage rate for staff hours beyond
[2 h] of customer-caused extra handling + pass-through for customer-supplied
feedstock prep.** Revisit at first annual review with time-study task data —
if inter-job labor variance >~30%, unbundle.

### 4.2 Failed runs (draft billing rule — see §8.4 for the policy text)

Billable = run reaching [atomization start]; Facility-fault failures re-run at
no charge (cost stays in pool as rework — allowable, ordinary); customer-fault
failures (out-of-spec feedstock, wrong SDS) billable at minimum fee + hours
consumed. Yield/PSD never guaranteed (already §4.3 of the service agreement).

### 4.3 Minimum fee

$150 per initiated job (p. 4 expressly contemplates a "minimum fee" from
initiation costs). Keep — it protects against small-job losses and is
policy-sanctioned.

## 5. Own-lab usage and §8 valuation (the money question)

Structure (per Edison A4): the **approved internal rate is always the gross,
cost-based rate**. Own-lab (~200 runs/yr, non-federal) is then settled one of
three ways, each logged run-by-run:

| Option | Mechanics | Cash effect |
|---|---|---|
| **§8 in-kind (preferred)** | run delivered without charge; credited against the $250k investment (pp. 7–8); prior written approval + ledger | no cash; pool share absorbed as documented under-recovery |
| Pay from startup | journal entry at $836 | cash circulates; $82/run reaches reserve |
| Documented subsidy | center covers from non-federal, non-recharge funds (p. 5) | no cash; same under-recovery tracking |

**The valuation swing (why the written ruling matters):**

| §8 credit valued at… | Credit/yr (200 runs) | Time to credit $250k |
|---|---|---|
| Full internal rate ($836) | $167,200 | **~1.5 yr** |
| Depreciation component only ($82) | $16,400 | **~15 yr → exceeds 10-yr life; max ~$164k ever credited** |
| Use-allowance (unknown %) | between | between |

Note-to-self: full-rate credit now looks *generous to us* precisely because the
staffed rate tripled — expect Regulatory Accounting to balk (the rate is mostly
labor/argon/maintenance, not "equipment value"). A middle position to propose:
credit at **depreciation + maintenance share** (~$115/run → ~$23k/yr → ~10.9 yr,
matching useful life almost exactly). Do **not** publish any repayment timeline
until the ruling exists. The old "~4 years to credit $250k" figure is
**withdrawn** (it was an artifact of the under-costed $306 rate).

**Reserve-vs-repayment tension, quantified:** billed-only deposits ≈ $8.6k/yr →
~$86k reserve over the life if own-lab stays unbilled. Full §8 repayment and a
pre-funded successor machine cannot both happen from this volume mix (scenarios
doc §11.4). Levers: bill own-lab in cash for some years (fills reserve), court
non-federal volume (surcharge → reserve), or accept partial repayment.

## 6. Depreciable base: tariff, freight, installation, renovation

Ruleset: 2 CFR 200.1 (acquisition cost may include "taxes, duty, protective in
transit insurance, freight, and installation" **per the institution's regular
accounting practices**; equipment includes "modifications, attachments,
accessories, or auxiliary apparatus necessary to make it usable"); Policy p. 7
(depreciate "acquisition cost … less residual value"); Policy p. 3 (no building
costs; nothing already in F&A).

Decision tree per line item (the decision belongs to **Fixed Assets /
Regulatory Accounting**, not us — Edison A1):

1. On the equipment asset record already? → in the base.
2. Not booked, but it's duty/freight/insurance/vendor-install **and** BYU's
   regular practice capitalizes such charges? → request addition before
   schedule approval.
3. Renovation line item: needed *solely* to make the machine usable
   (rigging, vendor commissioning)? → strongest candidates. Dedicated
   electrical/argon plumbing/exhaust? → **plausible but weak-to-moderate**;
   often building systems; if it's in the building-depreciation pool feeding
   F&A, it **cannot** also sit in our base (double recovery, p. 3 / 2 CFR
   200.468).
4. General renovation (walls, HVAC, finishes)? → out; recovered, if at all,
   through central F&A.

Note-to-self: get the renovation project ledger itemized **now**; the ask dies
once the depreciation schedule is approved. Sterling's "retroactive quote on
non-atomizer-specific items" idea = exactly the itemization exercise in the
equipment package §3 table.

## 7. Publication, embargo, and data rights (redesigned)

Year-one menu (DOE user-facility pattern — non-proprietary vs. proprietary is
the only precedented split; no published prior art anywhere for a timed
embargo-surcharge ladder):

- **Standard:** customer owns Run Data. Facility publishes **only aggregate /
  anonymized operational data** (throughput, uptime, queue behavior,
  architecture performance). Customer-specific Run Data published **only with
  written consent** or under a separately agreed non-proprietary term. This
  still feeds the students' infrastructure papers — that corpus is operational
  data, not customer results.
- **Proprietary (non-federal only):** no publication of anything job-specific;
  full cost + top surcharge tier.

Deferred: 6/12/24-month embargo ladder. Revisit at first annual review with
OGC + Regulatory Accounting if customers actually ask for intermediate terms.
Note-to-self: the ladder was *our* invention; nobody has validated demand.
Keep §5.3 of the service agreement carrying the two-tier table with the ladder
bracketed as a future option.

Federal-documented customers: standard tier only at cost+F&A (no premium
products — premiums are surcharges, p. 5). Cleanest DOE-consistent line:
federal money doesn't buy confidentiality.

## 8. Compliance program (new, from Edison gaps)

### 8.1 EHS (do first — gate on it)
Aluminum powder = combustible dust: **NFPA 484** review, housekeeping/dust
control, grounding/bonding, no-spark tools, PPE; argon = asphyxiant → oxygen
monitor in the room; powder storage limits; spill/waste procedures; DOT/IATA
shipping classification for outbound powder (likely Class 4.1 for fine Al —
EHS/shipping to confirm); emergency procedures. Repo already has the college
safety plan + SOP template — draft the atomizer SOP against them, then EHS
sign-off **before external work**. Added to establishment proposal §8 and the
readiness gate.

### 8.2 Export control workflow (before any non-US touchpoint)
Restricted/denied-party screening (customer + institution) → country screening
→ alloy/parameter sensitivity check (aluminum AM powder is generally EAR99-ish,
but defense-relevant alloys/parameters escalate) → end-use/end-user
certification (service agreement §7) → **deemed-export check for remote access**
(non-US person observing live process parameters = potential export even with
no shipment) → escalation to Office of Research for anything non-obvious.
Year one requests no non-US sales (establishment proposal §3).

### 8.3 Customer data handling (cloud-lab specific)
Classify at intake: public / customer-confidential / export-controlled / CUI.
**Refuse CUI/ITAR data absent an approved plan.** Retention: [3 yr] then
delete on request; access limited to named operators; remote sessions logged;
recording policy disclosed. Add as a clause at OGC review.

### 8.4 Failed-run policy (posted text, draft)
"A run is billable when atomization begins. Runs that fail due to Facility
equipment or operator error are repeated without additional charge. Runs that
fail due to customer-supplied feedstock or inaccurate customer declarations are
billable for hours consumed plus the minimum fee. Yield and particle-size
distribution are not guaranteed."

### 8.5 Queue priority (posted, draft)
1. Safety/maintenance; 2. BYU internal research commitments; 3. sponsored-award
deadlines (any tier); 4. external federal academic; 5. external non-federal
academic; 6. commercial/proprietary. Note: a posted policy that visibly serves
internal research first also supports the "primarily internal" scoping (p. 1)
and the UBIT related-purpose position.

### 8.6 Credit & collections
New industrial customers: PO or signed order + [credit check over $5k].
Net-30; suspension of new orders at 60 days past due; department eats
uncollectibles (**bad debt is unallowable in the pool** — cannot be recycled
into rates). Prefer ACH/invoice for anything over [$5k]; card via eMarkets
below that.

### 8.7 Segregation of duties (draft matrix)
Order acceptance: facility manager. Usage log: operator (per run), reviewed
monthly by manager. Billing/journal entries: department finance (not the
operator). Reconciliation: department finance monthly vs. usage log. Rate
changes: PI + Chair/Dean → Regulatory Accounting. Exception review (comped
runs, failed runs, write-offs): PI + department finance quarterly.

### 8.8 Record retention (draft)
Rate calcs, approvals, usage logs, invoices, subsidy & §8 ledgers, asset
records, export screenings, service agreements, EHS/SOP records: retain
[audit horizon — ask Regulatory Accounting; federal awards imply ≥3 yr from
final expenditure report, longer under BYU schedule]. Everything auditable by
federal and internal auditors (p. 3).

## 9. Revised timeline with triggers

| When | What | Gate/trigger |
|---|---|---|
| Now | Quote freeze; usage log starts | — |
| Jul–Aug 2026 | **Time study** (see §10); **cross-functional kickoff** (Reg. Acctg, Fixed Assets, dept finance, EHS, OGC, Tax, Treasury, Export Control, SPO) | kickoff scheduled = Phase 1 open |
| Aug 2026 | **Asset decision** (capitalized cost, in-service date, life, renovation items) | depreciation pool final |
| Aug–Sep 2026 | Own-lab structure + **written §8 valuation ruling** | no repayment projections before this |
| Sep 2026 | Establishment + **two-column rate proposal** (floor / staffed) via Chair→Dean→Reg. Acctg (p. 2 requires Chair/Dean rate review) | time study complete |
| Oct–Nov 2026 | Approvals; accounts opened; eMarkets application; OGC agreement review | |
| Nov–Dec 2026 | **Readiness gate:** EHS sign-off, SOPs, export checklist, billing workflow, intake form, rate schedule posted, §8 ledger live, reserve journal process | all items or no-go |
| Jan 1 2027 | Go live | |
| CY2027 | **Quarterly** actual-vs-forecast | mid-year revision if labor/run > ±20%, utilization > ±25%, or external mix shifts materially |

## 10. Time-study protocol (2–4 weeks, July–August)

Log per run, in minutes, by task: scheduling/customer comms; quoting; feedstock
intake + SDS review; setup; attended monitoring; powder recovery; cleaning;
packaging/shipping prep; documentation/data delivery; failed-run handling;
maintenance (allocated); training; cloud-lab/remote-session support; billing
support; safety recordkeeping. Also log: material, feedstock form, argon
consumed, sonotrode/crucible wear events, machine-hours, calendar span.
Output: loaded labor $/run distribution (mean, P80) + task-level variance →
feeds §3 staffing scenario choice and the §4.1 unbundling decision.
Note-to-self: run it on *real* jobs including at least [2] external-style dry
runs with full paperwork, or the admin overhead lines will read as zero.

## 11. Superseded numbers (do not reuse)

- ~~$306/run internal as a proposable rate~~ → floor only (Column A).
- ~~$464 federal external~~ → $1,267 planning.
- ~~"$61,200/yr §8 credit → ~4 years to repay $250k"~~ → withdrawn pending
  valuation ruling (§5).
- ~~6/12/24-month embargo price ladder ($775/$925/$1,225/$1,525)~~ → deferred;
  two-tier launch.
- ~~30-day default publication right over customer Run Data~~ → consent-based.

## 12. Prior-art rate shelf (for the submission appendix)

| Facility | Instrument | Published rates |
|---|---|---|
| Northwestern CHiMaD MPF | AMAZEMET rePowder (same class) | **$1,075 int / $1,720 ext-acad / $2,150 comm per run** |
| UW ME Metal AM | Arcam EBM A2X | $45/$90/$52 per h + powder $224/$282/$259 per kg + engineer $99/$173/$115 per h |
| LSU AMMF (FY26) | Mlab Cusing R | $36 acad / $60 non-acad per h + powder |
| UMass ADDFab | EOS M290, Optomec LENS 450 | daily rates, campus vs. external/industry |
| Michigan Tech; Georgia Tech AMPF | metal AM suites | internal/external columns, annual review |
| DOE user facilities / APS | — | binary non-proprietary (publish, no fee) vs. proprietary (full cost recovery) — the embargo-precedent anchor |
