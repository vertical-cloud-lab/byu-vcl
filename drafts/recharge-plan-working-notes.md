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

## 12. Feasibility check: proposed low-rate structure (Sterling, 2026-07-05)

Proposal under evaluation: internal **$100/run**, federal external **$500/run**,
non-federal surcharge **$500–1,500**, embargo pricing (possibly any users)
**$500 / 6 mo, $1,000 / 1 yr, $4,000 / 2 yr**. Verdict: buildable, with three
corrections forced by the policy. This section records the conditions; it does
**not** replace the §3 planning basis until the time study and Regulatory
Accounting say so.

### 12.1 The numbers are coupled — you only get to pick one of them

Federal externals must pay cost + institutional overhead ("External rates must
add institutional overhead (F&A) unless Regulatory Accounting approves
otherwise," p. 5). So **$500 federal external ⟹ approved cost-based internal
rate ≈ $330** ($500 / 1.515). You cannot post internal $836 and federal
external $500 — the external price is built *from* the internal rate, and
below-cost external pricing is not a thing the policy offers (the subsidy
mechanism on p. 5 covers internal usage; BYU subsidizing outsiders would be a
hard sell everywhere from Regulatory Accounting to UBIT posture). One lever:
the "unless Regulatory Accounting approves otherwise" waiver on F&A — worth a
kickoff question, but don't plan on it.

### 12.2 What it takes for a ~$330 cost rate to be honest

$100 can never be the approved rate — the non-labor variable cost alone is
$115/run (A11), so `pool ÷ usage` can't reach $100 at any volume. But $330 is
arithmetically reachable; solve `(40,000 + S×90,000)/N + 115 = 330`:

| Staffing S | Runs/yr N needed | Machine-hours (6 h/run) | % of 8,760 h |
|---|---|---|---|
| 1.0 FTE | ~605 | ~3,630 | ~41% |
| 1.5 FTE | ~814 | ~4,884 | ~56% |
| 2.0 FTE | ~1,023 | ~6,138 | ~70% |

I.e., **$500 federal external is precisely the "near-continuous" scenario**
Sterling described — it is not achievable at the 305-run CY2027 forecast (A7).
To propose it: the denominator needs documentary support (letters of interest,
queue projections, own-lab commitment), because a padded forecast that doesn't
materialize becomes a real deficit the department funds (p. 6), and the
quarterly triggers (§9) would force a mid-year rate *increase* on customers —
the worst commercial look. Note-to-self: Northwestern charges $1,075 internal
on the same instrument; if $330 is proposable at all it's because of an
unusually hot denominator, not a cheaper pool. Also sanity-check that S FTE can
physically execute N runs (1,023 runs × even 2 h direct labor ≈ 2,046 h ≈ 1.2
FTE of direct time alone before any admin/quoting/EHS overhead).

### 12.3 Internal $100 — compliant, but as a *price*, not a *rate*

Mechanism (p. 5, and Edison A4): approved internal rate stays cost-based;
internal users are *charged* $100 and the gap (rate − $100; $230/run at the
$330 scenario, $736/run at the $836 planning basis) is a documented subsidy
from non-federal, non-recharge funds, tracked and excluded from F&A proposals
(p. 4). "Startup money can legitimately subsidize early internal usage below
cost — what it cannot do is buy anyone a different rate." Blanket $100 for all
internal users preserves uniformity (p. 4). Internal users paying the $100 from
federal grants is fine (under-charging federal money is allowed; over-charging
is not) as long as the subsidy source is non-federal. Own-lab runs stay on the
§5 structure (§8 in-kind credit preferred) — don't route them through the $100
price without deciding what that does to the reimbursement claim.

### 12.4 Non-federal surcharge $500–1,500 — cleanly allowed

Expressly permitted, size discretionary (p. 5). At the $330-cost scenario the
posted non-federal price is $1,000–$2,000/run, bracketing under Northwestern's
$2,150 commercial — defensible. Net surcharge income remains the UBIT quantum.

### 12.5 The embargo ladder — cannot be "for any users"

- **Non-federal externals: yes.** An embargo premium is a surcharge; $500/6 mo,
  $1,000/1 yr, $4,000/2 yr is a lawful posted menu for them.
- **Federal externals: no.** No surcharge (p. 5) means no purchasable premium.
  Give them one standard term at no charge (or the DOE binary), not the menu.
- **Internal: no, and no need.** Internal rates carry only costs (p. 5), and
  under the consent-based §7 design the facility asserts no publication right
  over internal runs — there is nothing to sell them an embargo against.
- **Design consequence:** a paid embargo presupposes the *standard* tier
  defaults to "job-specific data becomes publishable after the term" —
  re-flipping the consent-based default Edison A5 made us adopt. That's a
  legitimate choice (DOE non-proprietary = publication expected), but make it
  deliberately, and remember the ladder still has **zero prior art** (§7).
- **Menu coherence:** price the proprietary/indefinite tier *above* the 2-yr
  premium, or everyone rational buys proprietary at $633 and the ladder is
  dead letter — at $4,000/2 yr the proprietary surcharge must exceed $4,000.
  And decide whether the ladder **stacks** on the $500–1,500 base surcharge
  (2 yr + top base = $6,000/run ≈ 3× Northwestern commercial — market check)
  or replaces it.

### 12.6 Capital-recovery consequence

At N ≈ 1,000 runs the depreciation slice is only ~$25/run, but billed volume is
huge, so the reserve fills at the same $25k/yr — capital recovery is unchanged
in total (it's paced by the schedule, scenarios doc §16c). The real exposure is
12.2's: if volume disappoints, the low rates under-recover *operating* cost and
the deficit is the department's.

**Bottom line:** the structure survives contact with the policy if (a) $100 is
framed as subsidized price against a cost-based approved rate, (b) $500 federal
external is supported by a documented ~600–1,000-run/yr forecast (or an F&A
waiver), and (c) the embargo menu is sold to non-federal externals only. The
quote freeze (§9) still applies to all of these numbers.

## 13. Own-lab funding, the leverage question, open-data default, upgrades (Sterling, 2026-07-05)

Questions under analysis: (a) "I wouldn't have funds to pay for our own lab's
usage → full subsidy → less leverage on costs recovered from non-lab sources";
(b) what is the DOE binary (link wanted); (c) open-by-default data with a
permissive license + short grace period, embargo only for non-federal externals
at ~$5k/2 yr or ~$10k/4 yr; (d) can upgrades be capitalized on the non-federal
surcharge, or "relax and set a normal internal price and look for alternatives."
Analysis only — no draft numbers or agreement text changed yet (see 13.6).

### 13.1 Own-lab usage does not require cash — or new money

Three layers, in order of preference:

1. **§8 in-kind credit is the no-cash channel.** Own-lab runs are delivered
   without charge and credited against the $250k investment (pp. 7–8). That is
   not a subsidy funded by new money; it is the center repaying a debt it
   already owes the startup account. No invoice ever arrives. (Valuation ruling
   still pending — §5.)
2. **The "full subsidy" is mostly money already being spent.** The center's
   cash costs are staff + consumables + maintenance. If startup-funded students
   already operate the machine and startup funds already buy the argon and
   sonotrodes, establishing the center creates **no new bill** — it converts
   existing spending into a *documented* subsidy (tracked, excluded from F&A
   proposals, pp. 3–5). The subsidy requirement is bookkeeping, not a second
   outlay of the same dollars.
3. **The real cash question is staffing, not the own-lab charge.** At 2.0 FTE
   the pool's cash portion is ~$230k/yr against ~$95k of external cash in
   (§3.2). If those FTEs are the people startup/department already pays, the
   gap is absorbed; if they are new hires, *that* is the funding decision — and
   it exists at any posted internal price whatsoever.

### 13.2 Leverage runs the other way: a low *rate* cuts external recovery; a subsidized *price* doesn't

Because federal externals pay internal rate × 1.515 with no surcharge (p. 5),
the approved rate is the lever that sets what non-lab sources contribute:

| World | Approved rate | Federal ext pays / center keeps (per run) | Own-lab cash cost |
|---|---|---|---|
| Honest staffed rate | $836 | $1,267 / **$836** | $0 (§8 credit or documented subsidy) |
| Low-rate structure (§12) | ~$330 | $500 / **$330** | $0 (same) |

Own-lab cash cost is identical in both worlds — under §8/subsidy you never pay
cash either way. So the low-rate structure surrenders ~$500/run × 70 federal
external runs ≈ **$35k/yr of external recovery in exchange for nothing**. The
leverage-maximizing construction is exactly the compliant one: **highest
defensible cost-based rate + §8 credit / documented subsidy for own-lab +
surcharge on non-federal externals**. Two refinements:

- **Uniformity does not require buying everyone else a cheap price.** The rate
  must be uniform (p. 4); the *subsidy* may be scoped — the policy permits
  paying for "specific users'" services from non-federal, non-recharge funds
  (p. 5). Own-lab can ride §8/subsidy while other internal users pay the full
  rate from their own accounts. "Consistent for myself and for others" lives at
  the rate level, where it is automatic.
- **Surcharge income may lawfully "reduce rates charged to users" (p. 5)** —
  the one mechanism by which external money can, in effect, cover part of the
  internal share of the pool.

Confirmed: internal and federal-external differ only by F&A (p. 5), with the
single escape hatch "unless Regulatory Accounting approves otherwise" — the F&A
waiver stays on the kickoff agenda but is not planning-assumption material.

### 13.3 The DOE binary, with links

Two contract types chosen at intake, nothing more:

- **Non-proprietary:** user intends to publish; results become public. At DOE,
  "user fees are not charged for non-proprietary work if the user intends to
  publish the research results in the open literature"
  ([DOE Office of Science FAQ](https://science.osti.gov/User-Facilities/Frequently-Asked-Questions)) —
  DOE can charge $0 because Congress funds the facilities; our analog is the
  *standard tier at posted cost-based prices*, not free.
- **Proprietary:** user keeps results confidential; "full cost recovery is
  required for proprietary work" (same FAQ). Our analog: full cost + top
  surcharge, non-federal only.

Primary sources: [DOE Office of Science user agreements](https://science.osti.gov/User-Facilities/User-Resources/User-Agreements)
(both IP class waivers); [APS explainer — "Differences between non-proprietary
and proprietary research"](https://www.aps.anl.gov/Users-Information/Legal-Financial/Differences-between-non-proprietary-and-proprietary)
(clearest side-by-side; note aps.anl.gov blocked this CI runner — verify in a
browser); [ORNL user agreements](https://www.ornl.gov/content/user-agreements).
The point of citing it as precedent: **open is the default; secrecy is the
priced exception** — which is exactly the instinct behind the open-data design
below.

### 13.4 Open-by-default with permissive license + grace period (proposed redesign of §7 / agreement §5)

Sterling's default (data goes public under a permissive license, facility
claims no rights beyond the license, ~3-month grace period, customer may
shorten/waive) is *cleaner* than both prior designs — closer to DOE than the
consent-based Edison A5 version, and it dissolves several standing problems:

- **Structure:** Run Data is deposited in [repository] under [license] upon
  expiry of a [3-month] grace period running from data delivery; the customer
  may shorten or waive. Facility asserts no ownership; everyone (including the
  facility and its students) uses the data under the license like anyone else.
  Contract mechanics: since the customer owns Run Data (agreement §5.1), the
  clause is the customer *agreeing to the release* — one paragraph, all tiers.
- **License note-to-self:** raw run data is largely facts (thin copyright), so
  the license is mostly signaling + certainty. **CC0** = cleanest for data,
  avoids attribution stacking; **CC BY 4.0** = citation credit for students.
  Either defensible; OGC gets the final word. Repository choice (Zenodo /
  Materials Data Facility / institutional) is a kickoff add-on.
- **The free grace period is uniform and costs nothing** → no surcharge issue,
  so federal externals get it too (p. 5 problem never arises).
- **Paid embargo = surcharge = non-federal externals only** (p. 5) — agreed,
  and now the *standard* tier already defaults to "publishable after the term,"
  so the §12.5 design contradiction (consent-based default vs. paid embargo)
  disappears.
- **Ladder pricing ($5k/2 yr … $10k/4 yr):** compliance-wise free — surcharge
  size is discretionary (p. 5) — so this is a *market* question with zero prior
  art (§7). A late-program **business-school student** doing a
  willingness-to-pay / pricing study is a genuinely good fit (capstone-sized,
  also useful on the §12.2 demand-forecast problem). Cautions at 4 years:
  outlives most student timelines (mitigated — the aggregate/anonymized
  operational-data carve-out stays publishable immediately in **all** tiers,
  and that is the corpus the infrastructure papers need); standing
  confidentiality erodes the fundamental-research/export posture and the UBIT
  related-purpose story if it becomes the norm rather than the exception.
- **Kill the indefinite tier.** With a 4-yr rung available, drop "proprietary
  /indefinite" entirely: every embargo expires. This solves the §12.5 menu-
  coherence problem (nothing has to be priced above the top rung), strengthens
  the open-facility posture, and anyone needing true perpetual secrecy is
  routed to a sponsored-research agreement or declined.
- **Federal externals get the grace period only** (can't buy extensions). If a
  federal customer legitimately needs longer, the uniform no-cost standard term
  can be set at whatever length policy chooses — or route to SPO. DOE-
  consistent line unchanged: federal money doesn't buy confidentiality.

### 13.5 Upgrades: the surcharge channel is real, and "relax to a normal internal price" costs you nothing you actually had

- **Direct answer: yes.** Surcharge income may be used "to finance equipment
  purchases" (p. 5); purchases/upgrades ≥$5k are charged to the equipment
  reserve (p. 7), each capitalized upgrade gets its own depreciation schedule
  and re-enters rates. Expressly permitted — no relaxation needed on this goal.
- **The two decisions are decoupled.** Internal rates can *never* fund upgrades
  at any price level ("cannot add charges to accumulate assets," p. 5). So
  setting a normal (honest) internal rate sacrifices zero upgrade capacity —
  upgrade money was only ever coming from: (1) the non-federal surcharge,
  (2) gifts/philanthropy (opens a new §8 basis), (3) department/college/startup
  investment (ditto), (4) sale proceeds of old equipment (p. 7), (5) residuals
  on industry *fixed-price* contracts (confirm disposition with SPO). Per
  §13.2, the honest rate actually *helps*: a higher rate base means a higher
  surcharge-eligible price before market limits bite.
- **The binding constraint is the thin non-federal base, not policy.** 30
  non-federal runs × $233 surcharge ≈ $7k/yr; even × $1,500 ≈ $45k/yr gross
  (UBIT on net). Embargo premiums stack on top for those customers only. Every
  federal-academic customer contributes $0 to upgrades *by design* — courting
  industry/non-federal volume is the only demand-side lever.
- **And the §5 tension governs:** every dollar of §8 in-kind credit competes
  with reserve accumulation. If upgrades matter more than repaying the startup
  account, deliberately take less §8 credit (or bill own-lab in cash for some
  years so the $82/run depreciation actually reaches the reserve).

### 13.6 Decisions this queues (not yet made)

1. Adopt open-by-default + grace period as the standard tier (flips Edison A5
   consent-based design — deliberate, DOE-precedented). → rewrite agreement §5
   and §7 above once confirmed.
2. License (CC0 vs CC BY 4.0) and repository. → OGC + kickoff.
3. Drop the indefinite/proprietary tier in favor of a capped ladder (top rung
   2 or 4 yr). → with OGC; year-one menu could still launch binary (grace-only
   vs. one paid rung) if the ladder feels premature.
4. Ladder price points ($5k/2 yr, $10k/4 yr) → market study (business-school
   student project).
5. Own-lab settlement stays §8-in-kind-preferred; no blanket internal price cut
   needed for "consistency" (§13.2).

## 14. How the three flows interact: free own-lab use × federal externals × non-federal externals (Sterling, 2026-07-05)

Question under analysis: if own-lab uses the machine extensively "for free"
(§8 in-kind) *at the same time as* heavy federal-external and non-federal-
external billing, how do the streams interact for equipment-buying capacity?
Does the surcharge-for-equipment ability change before vs. after cost recovery?
Can the federal-external price cover depreciation, and what limits how that
recovered depreciation is used?

### 14.1 The four streams never mix — each run feeds fixed buckets

Every run generates money (or credit) into at most four buckets, and the
buckets have different rules. Per-run contributions at the §3 planning basis
(305 total runs, $82/run depreciation slice, $836 internal rate):

| Run settled as… | Depreciation → equipment reserve | Surcharge → growth funds | §8 credit → startup account | F&A → central |
|---|---|---|---|---|
| Own-lab, §8 in-kind (unbilled) | $0 — forfeited this year | $0 | **yes** (valuation ruling pending, §5) | $0 |
| Internal, billed in cash | $82 | $0 | $0 | $0 |
| **Federal external** | **$82** | $0 (no surcharge, p. 5) | $0 | ~$431 |
| **Non-federal external** | **$82** | ~$233 std (embargo ladder stacks) | $0 | ~$431 |

Interaction rules that fall out of the table:

- **The streams are additive, not interfering.** Free own-lab runs do not
  raise or lower what an external run deposits into the surcharge bucket;
  federal-external runs feed the reserve but never the growth bucket;
  non-federal runs feed both. "Both things happening at once" simply sums
  the columns.
- **The one true coupling is through the denominator.** The depreciation
  slice is $25,000 ÷ total usage, and all usage counts billed or not (p. 4).
  So the reserve's annual depreciation intake collapses to one formula:

  > **Reserve intake = $25,000 × (billed runs ÷ total runs)**

  Free own-lab runs don't just forfeit "their own" $82 — by enlarging the
  denominator they shrink the slice collected on *every* billed run. At 105
  billed / 305 total: 105 × $82 ≈ **$8.6k/yr**. Double own-lab to 400 free
  runs (505 total): the slice drops to ~$50 and the same 105 billed runs
  deposit only ~$5.2k. The forfeited remainder — $25,000 × (unbilled ÷ total)
  — is gone for that year (no prior-year catch-up, p. 6–7), offset only by
  the §8 credit accruing on those same runs. This is §5's reserve-vs-repayment
  tension restated as a formula: **billed-fraction fills the reserve;
  unbilled-fraction earns §8 credit; every run is one or the other.**

### 14.2 The two thought experiments, and the mixed case

- **"Only ever used it myself at zero fee → as if nothing happened."** Cash-
  wise, essentially yes: no revenue, no reserve, no surcharge. But not quite
  *nothing* — every run accrues §8 in-kind credit, so the center is steadily
  repaying the startup account's $250k in machine time (at whatever valuation
  the ruling sets), and the usage log + documented under-recovery still have
  to be kept (pp. 3–5). It's a repayment engine with no accumulation engine.
- **"Never used it myself, everything from non-federal externals → accumulate
  a lot."** Correct, and it's the maximum-accumulation corner: reserve intake
  = the full $25k/yr (billed fraction = 1) *plus* surcharge income on every
  run, both usable for equipment (p. 5, p. 7). Two bounds: the depreciation
  part is capped at the $250k capitalized cost over the useful life — it is
  return *of* capital, not income — while the surcharge part is uncapped but
  UBIT-relevant and market-limited. (An all-external center also stresses the
  "primarily internal" recharge-center framing — standing kickoff question.)
- **Both at once (the real plan):** sum the columns. At the CY2027 forecast
  (200 own-lab free / 5 internal billed / 70 federal / 30 non-federal):
  reserve ≈ $8.6k/yr + surcharge ≈ $7k/yr ≈ **$15.6k/yr of equipment-buying
  capacity**, plus ~$16.4k/yr of §8 credit accruing on the free runs
  (valuation pending). Versus: billing own-lab in cash would push the reserve
  to $25k/yr but cost real cash; going all-external would add surcharge
  breadth. The mix doesn't create any new constraint — it just splits the
  $25k depreciation stream between "collected into reserve" and "converted
  to §8 credit" in proportion to billing.

### 14.3 Before vs. after "cost recovered" — which streams change

- **Surcharge → equipment: does not change. Ever.** It is above-cost income
  whose permitted uses ("reduce rates …, build a working capital reserve, or
  … finance equipment purchases," p. 5) are independent of the depreciation
  schedule's state. Before recovery, after recovery, on the current machine
  or the next — the channel is permanent. Sterling's intuition is right.
- **Depreciation → reserve: temporary and capped by construction.** It runs
  only while (a) cumulative depreciation < capitalized cost and (b) the
  useful life hasn't expired — whichever ends first ends the stream, with no
  catch-up (pp. 6–7). Then depreciation exits the pool, rates step down, and
  the reserve stops filling from this asset. The stream gives back the $250k
  at most once.
- **The loop restarts on new assets.** Anything ≥$5k bought from the reserve
  or surcharge funds gets its own approved schedule and re-enters rates
  (p. 7) — so "accumulate → buy → depreciate → accumulate" is the sanctioned
  long-term engine. But note the asymmetry: *sustained* growth capacity comes
  only from the surcharge (and new gifts/investment, each opening a fresh §8
  basis); the depreciation stream on any one asset is a closed loop returning
  its own cost.

### 14.4 Federal externals and depreciation: yes, they pay it — and the limits on using it

The federal-external price is cost × 1.515, and "cost" is the full approved
rate including the $82 depreciation component — so **every federal-external
run pushes $82 into the equipment reserve, identical to any other billed
run**. What federal externals never contribute is the surcharge (p. 5). The
F&A increment (~$431) is the university's recovery, not the center's.

Limits on recovered depreciation (all from pp. 6–7 + §8):

1. It must be deposited to the **equipment reserve account** — it can't
   subsidize operations or sit in the operating account.
2. Spendable only on **equipment ≥$5k** (purchase/replacement/upgrade — which
   *must* be charged to the reserve) or **§8 reimbursement** of the accounts
   that funded the center's equipment (prior Regulatory Accounting approval,
   documented, hard-capped at the amount invested, cash never beyond it).
3. Total collection is capped at the **capitalized acquisition cost**; the
   collection window is capped at the **approved useful life**; skipped years
   are unrecoverable.
4. Each reserve-funded purchase starts a **new depreciation schedule** — no
   double recovery on the same dollars.

### 14.5 Net answer

Funds available to buy the next piece of equipment at any moment =
**equipment-reserve balance** (fed by $25k × billed-fraction per year, capped
at $250k lifetime, competing with §8 draws) **+ accumulated surcharge income**
(non-federal externals only, uncapped, permanent, UBIT-relevant). Free own-lab
use slows only the first term — dollar-for-dollar, $82 per free run at current
volume, while earning §8 credit instead — and touches the second term not at
all. Federal externals feed only the first term; non-federal externals feed
both; and after full recovery the first term ends while the second keeps
running unchanged.

## 15. Prior-art rate shelf (for the submission appendix)

| Facility | Instrument | Published rates |
|---|---|---|
| Northwestern CHiMaD MPF | AMAZEMET rePowder (same class) | **$1,075 int / $1,720 ext-acad / $2,150 comm per run** |
| UW ME Metal AM | Arcam EBM A2X | $45/$90/$52 per h + powder $224/$282/$259 per kg + engineer $99/$173/$115 per h |
| LSU AMMF (FY26) | Mlab Cusing R | $36 acad / $60 non-acad per h + powder |
| UMass ADDFab | EOS M290, Optomec LENS 450 | daily rates, campus vs. external/industry |
| Michigan Tech; Georgia Tech AMPF | metal AM suites | internal/external columns, annual review |
| DOE user facilities / APS | — | binary non-proprietary (publish, no fee) vs. proprietary (full cost recovery) — the embargo-precedent anchor |
