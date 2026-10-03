# Question

**Experimental design for a physically closed generative end-effector design loop — how to make "an LLM designed a better gripper" a defensible measurement rather than a demo.**

Fourth in a sequential series for a university materials self-driving lab. Prior scans established, and should not be re-derived: (Q1) every deployed arm-based SDL uses an expensive industrial arm with a custom or heavily modified end-effector, the arm is a transfer layer, and reliability is unreported; (Q2) the metrology options below a laser tracker, and that a 95% one-sided reliability claim needs ~118 operations for p ≥ 0.975 and ~1,497 for p ≥ 0.998 with zero failures; (Q3) that **no published system autonomously closes the loop from laboratory-object requirements through editable manufacturable gripper CAD, FDM fabrication, and measured manipulation performance on a real SDL arm** — Fit2Form (Ha, Agrawal & Song 2020) closes geometry→print→test without editable parametric CAD or lab objects; Yi et al. 2025 close stiffness–pose co-design on a predefined flexure family; IterCAD / Text2CAD-Bench / CADIR / CME-CAD optimize digital similarity with no fabrication; Omaisan 2026's robot-aware passive-gripper design is simulation-only with physical tests explicitly pending; MATTERIX simulates workflows but generates no grippers. Q3 ranked closing that loop as the highest-value opportunity, ahead of a compliance-vs-precision map, an end-effector reliability benchmark, a printed kinematic tool changer, a robotic DSC press-fit station, fixed-focus wrist servoing, and an open powder scoop.

Our assets: **CADSmith** (multi-agent text-to-CadQuery with exact OpenCASCADE validation and a three-view VLM judge; 100% execution, 38× mean-Chamfer reduction vs. zero-shot on a private 100-prompt benchmark), an AgileX **PiPER** (6-DOF, ~1.5 kg payload, unverified 0.1 mm claim), Bambu **A1 mini / H2D** FDM printers including validated **printed-in-place rigid + TPU-85A mechanical-interlock joints** (no reliance on PETG–TPU bond chemistry; pull-through ratio 1.71× anchor-bulb, 2.5× captive core; Bruceton n ≥ 20 reuse protocol), an A&D HR-100A balance with closed-loop logging, and lab objects: SEM stubs, empty and filled vials, SBS well plates, aluminium DSC crucibles and press-fit lids, printed tensile/impact coupons, and cohesive AlSi10Mg and Si powders.

We do not want another survey. We want the **protocol**.

## 1. The measurement, done properly

- **What is the right dependent variable** for "this finger is better"? Interrogate the candidates — binary grasp success, retention force to failure, wrest/pull-off force, capture envelope (success vs. imposed lateral/axial/angular offset), seating success, cycle life, time-to-complete — and say which ones published gripper work actually uses, how it defines them operationally, and which are confounded by arm pose error rather than finger geometry.
- **How do you separate the finger's contribution from the arm's?** Give concrete designs: fixed-fixture testing off the arm, deliberately perturbed poses, paired designs on the same trajectories, blocking on time-of-day for thermal drift. What is the standard practice, and what does it miss?
- **Statistical design.** For comparing k generated designs against a human-expert control on n objects: power analysis for binary success at realistically high baseline rates, the right paired/blocked structure, multiplicity correction across designs and objects, and how to report capture envelopes (logistic regression on offset? ED50-style thresholds?). What sample sizes make a referee believe a difference of 5 percentage points at a 90% baseline?
- **Fatigue and cycle life for printed compliant fingers.** Standards or established protocols for cyclic testing of FDM flexures (loading rate, environmental control, failure criterion, run-out definition), and the published fatigue data that exists for PLA/Tough PLA/PETG/TPU/PA-CF at flexure-relevant strain amplitudes. How many cycles constitute a credible claim, and how do you accelerate honestly?
- **Print-to-print and printer-to-printer variability** as a nuisance factor: what is documented for FDM dimensional reproducibility, and how many replicate prints per design does a comparison need?

## 2. The generative loop itself

- **What is the right feedback signal to return to the generator?** Rank the options on information content and practicality: pass/fail, scalar reward, force–displacement curves, failure-mode labels, a VLM's reading of failure video, human code-level edits. Note that Sadik & Bujny 2025 found code-level human edits achieve zero Hausdorff distance vs. image-only correction — what is the analogous result, if any, for *functional* rather than geometric feedback?
- **How many physical iterations is realistic**, and what does the literature on design-of-experiments under expensive evaluations (Bayesian optimization over parametric geometry, multi-fidelity with simulation as the cheap tier) say about allocating a budget of, say, 30–60 printed-and-tested designs?
- **Ablations a referee will demand**: which components of the pipeline (kernel checks, VLM judge, physical feedback, parametric priors) must be individually removed, and what is the minimum set that still supports the headline claim?
- **The human-expert control arm.** How have published human-vs-AI design comparisons been run credibly — expert selection, time budgets, blinding, whether the expert sees the same spec, how to avoid a strawman baseline? Cite specific studies. What does a fair control look like when the expert is a student in the same lab?
- **Pre-registration and reporting.** Is there precedent for pre-registering a hardware-design comparison? What reporting standards (CONSORT-like checklists, HardwareX's requirements, ASME/RA-L expectations for hardware claims) would strengthen it?

## 3. Reusing what we have

- Our tensegrity work uses **mechanical interlock instead of interfacial adhesion** for rigid+TPU printed-in-place joints. Does the compliant-gripper literature use the same trick, and is there published data on multi-material FDM finger durability that we should be designing against?
- Is there any published use of **balance/force feedback as the reward signal** in a design loop (as opposed to a control loop)?
- What existing **open datasets, object sets, or task boards** could make our results comparable to others — YCB, the peg-in-hole benchmarks, ATLA/lab-specific sets — and what are their documented limitations for laboratory objects?

## 4. Deliverable

A concrete, criticizable experimental protocol we could pre-register: objects, designs, replicates, cycles, instruments, statistical model, ablations, controls, and the specific numbers that would constitute success or failure. Plus the three most likely reasons a referee rejects it, and what to measure now to forestall each. Flag extrapolation, and name what is simply absent from the literature.
