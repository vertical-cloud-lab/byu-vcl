# Question

Fourth in a sequential series for a university group building a low-cost, cloud-operated
self-driving laboratory (SDL) around an **AgileX PiPER** 6-DOF arm (~$3k, 1.5 kg payload,
626 mm reach) with self-mounted Raspberry Pi HQ cameras (IMX477, fixed C-mount lenses),
feeding an existing stack: an **Opentrons OT-2**, a **screw-auger powder doser** with an
in-loop analytical balance in a fume hood, a **CubXL gantry**, **Bambu Lab FDM printers**,
a **drop tower** with accelerometers and a high-speed camera, and an **Instron**. Operators
are frequently *physically absent* — that is the group's stated thesis ("Vertical Cloud
Lab"), and undergraduates are the main on-site hands.

Prior queries established: arms in SDLs are a logistics layer; reliability is the binding
constraint and no one publishes MTBI; ISO 9283-on-a-budget and the statistics for a
defensible reliability claim; and (Q3) that perception on specular/transparent/thin labware
should be avoided in favour of tagged fixtures, that stop-and-look is mandatory with a
rolling-shutter sensor, that learned policies plateau at 90–96% where >99% is needed, and
an eight-primitive sandbox ending in a crucible lid press-fit and a powder-atomizer
transfer.

Two things now gate everything else: **whether this can run unattended**, and **what the
control plane should be**. Please treat safety as the harder gate.

# Specifically, please address

1. **Unattended and remotely-supervised operation: what the standards actually require.**
   For a collaborative arm operating without a person present, near a furnace and reactive
   metal powders: what do **ISO 10218-1/-2 (2025 revision)**, **ISO/TS 15066**, **ANSI/RIA
   R15.06**, **ISO 13849-1 / IEC 62061** (performance levels and SIL), and **IEC 61508**
   actually require, and which of them bind a *research* laboratory rather than an
   industrial installation? What is the real regulatory and institutional-EHS position on
   an unattended robot cell in a university lab in the United States — what do IBC/EHS
   committees, OSHA, NFPA (including **NFPA 484** for combustible metals) and insurers
   require, and what have published SDLs actually done? Cover risk assessment
   methodology (ISO 12100, HAZOP, FMEA, STPA/STAMP), and say which is most appropriate
   for an SDL.

2. **The specific hazards here, quantified.** **Reactive/combustible metal powders**
   (aluminium, AlSi10Mg, silicon) — dust-explosion thresholds (MIE, MEC, Kst), the
   grounding and bonding requirements, why static from a printed enclosure or a plastic
   funnel is a real ignition source, and what enclosure and exhaust design is defensible.
   **Furnaces** — thermal runaway, interlocks, what happens if the arm faults mid-insert
   with the door open. **The arm itself** — pinch and crush at 1.5 kg payload, what a
   low-cost arm without certified safety-rated monitored stop can and cannot claim, and
   whether an external safety relay/light curtain/e-stop chain is mandatory or advisable.
   Include the fire-suppression question for metal powders (Class D, why water and CO2 are
   wrong).

3. **Fault detection, containment, and safe-state design.** How do deployed autonomous
   systems detect that something has gone wrong *before* it becomes irreversible? Cover
   watchdogs and heartbeats, current/torque limits, envelope and workspace monitoring,
   vision-based anomaly detection (including whether a VLM supervisor of the LabRobFail
   kind is trustworthy enough to gate an action), mass-balance and consumable accounting
   as an independent check, and the design of **safe states** for each hazard. What does
   the literature say about **recovery** — when should a system retry, when should it halt
   and page a human, and how do you avoid an autonomous retry loop that turns a recoverable
   fault into a catastrophic one? Are there published guard architectures from adjacent
   fields (industrial FDIR, spacecraft safe-mode, autonomous-vehicle minimal risk
   condition) that transfer?

3b. **Remote supervision specifically.** What latency, bandwidth, video quality and UI
   affordances are needed for a remote human to usefully intervene? What does the
   teleoperation and supervisory-control literature say about operator situational
   awareness, handoff, and the "out-of-the-loop" performance problem when the human is
   only summoned on exception? How should an e-stop work when the responsible human is
   1,000 km away and the only people in the room are undergraduates who did not start the
   experiment?

4. **The control plane — and be skeptical of greenfield advice.** Q3 recommended **EOS**
   over AlabOS, Bluesky/Ophyd, ChemOS 2.0 and SiLA 2 for a new SDL. Evaluate that
   recommendation critically against this group's *existing* infrastructure, which is
   already **MQTT (HiveMQ) + MongoDB Atlas + Hugging Face Spaces + GitHub Actions**, with
   devices addressed over Tailscale and an Opentrons HTTP API reachable only from a
   specific Pi. Concretely: what is the migration cost, what would be gained, and is there
   a defensible architecture that keeps MQTT as the device bus and adds an orchestrator
   above it rather than replacing it? Compare on the axes that matter for a *cloud* lab —
   multi-user queuing and fair scheduling, authentication and authorization, provenance and
   audit trail, reproducibility of a campaign, crash recovery and idempotency of a
   partially-executed protocol, and observability. Address **data provenance and
   persistent identifiers** (RO-Crate, PROV-O, Zenodo/DOI minting, ELN integration) and how
   an SDL should record *what physically happened* versus what was requested — Q1 noted our
   sensor records once conflated insert time with measurement time, which is exactly this
   failure.

5. **Human factors and the undergraduate reality.** What does the literature say about
   training, documentation, SOPs, and error rates for student operators of automated
   equipment? What do SDL groups report about the *human* time cost — restocking,
   recalibration, troubleshooting — and how does that compare to the automation savings?
   Is there evidence on how much of an SDL's real throughput is lost to consumable
   restocking and low-utilization windows, and what design choices (magazine capacity,
   batching, scheduled human touchpoints) most improve it?

6. **What to do in the first 90 days**, ordered, given the sandbox in Q3: what safety work
   must precede the first unattended overnight run, what can be done in parallel, what is
   the minimum defensible documentation package for an institutional EHS review, and what
   is the first experiment that can honestly run without a person in the room. Distinguish
   clearly between what is legally required, what is best practice, and what is prudent but
   optional.

Prioritize 2020–2026 sources and named standards clauses. Where an SDL has published its
safety architecture, say so specifically. Flag extrapolation, and say plainly when
something is unknown rather than interpolating.
