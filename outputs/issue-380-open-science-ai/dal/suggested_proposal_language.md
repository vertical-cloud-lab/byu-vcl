# Suggested proposal language for FLAIME / DAL: openness, data and IP

This is draft text for the Genesis Mission (DE-FOA-0003612, Topic 3B) application and its later Data Management
and Sharing Plan. It turns the [openness audit](dal_openness_audit.md) and the evidence in this study into
paragraphs that resolve the inconsistencies the audit found:
- three positions on compositions;
- "12 months" vs. "at the time of publication";
- MIT vs. MIT/Apache-2.0;
- Thermo-Calc's role.

It is a suggestion for the DAL team to edit. It is not a commitment, and it does not change the DAL repository.
FOA page references are as quoted in the audit (§III.A pp. 57–58; §IV.C p. 71; App. 4 p. 75; §IX.B.12 pp. 120–122;
§IX.C.34–39 pp. 150–152).

## Open science and software sharing

> FLAIME's software is released under the MIT licence, with SPDX identifiers in every file. That includes the
> function-network optimization engine (BOFN/pKGFN), the instrument drivers and the orchestration code for the
> vertical cloud lab. Tutorials and benchmarks follow the Honegumi model. Each instrument is exposed through a
> small, documented driver following the Model Context Protocol, an open standard now hosted by the Linux
> Foundation's Agentic AI Foundation, so other DOE and university laboratories can reuse the interface with their
> own AI agents. Where a vendor's SDK or documentation can't be published, the driver keeps the vendor-specific part
> behind a thin, documented adapter. Lab-designed hardware (charge cups, plugs, fixtures, tray stations) is
> released under CERN-OHL-P-2.0. Any deviation from the Open Source Definition is justified component by component,
> as the FOA requires.

*Evidence:*
- Foundation-hosted projects stayed open through changes of owner (README §2).
- Drivers and shared interfaces are what other labs reuse (PyLabRobot, OpenFlexure; README §5).
- Missing APIs, not licence fees, are the real cost of closed equipment (`ac-dev-lab` digest).

## Data management and sharing

> Every experiment and simulation writes one record per composition and process stage to a FAIR digital thread.
> The thread is defined by a published JSON Schema with schema.org metadata, OPTIMADE-style composition fields and
> PROV-O provenance. Data underlying a publication are deposited at the time of publication. All other data are
> deposited within 12 months of collection, whichever comes first. Data go to Zenodo for DOI snapshots and to the
> Materials Data Facility as the DOE-facing home, with DOIs reported to OSTI. Data are licensed CC BY 4.0 with CC0
> metadata. Negative and failed runs are released on the same schedule, because they are the most valuable and
> least available signal for machine-learning materials discovery.

*Evidence:*
- Open materials databases (Materials Project, OQMD, AFLOW, NOMAD, Alexandria, OMat24) became the training base
  for ML materials discovery (Edison round 2).
- Closed AI-for-materials startups protect data, not methods (group E).
- 92% of foundation models adopted in science papers are open-weight (Edison: open-weight AI).

## Data sharing limitations

> Some inputs carry third-party terms and are not redistributed: CALPHAD databases licensed from Thermo-Calc
> (TCAL), and handbook data from MMPDS, Knovel and ASM. For these we publish derived results, the identifiers and
> versions of the inputs, and the code needed to reproduce the derivation with a licensed copy. Open-source
> screening (pycalphad, OpenCalphad) is published in full. Vendor-confidential instrument documentation is not
> published; the open drivers document only the interfaces we implement.

*Evidence:* the audit's finding that the drafts list TCAL outputs as shared data without a limitations paragraph.

## Intellectual property in alloy compositions

> By default, alloy compositions discovered with FLAIME are published openly. At the Month-6 gate, a composition
> that meets the project's performance targets *and* has a named prospective licensee may instead be held as
> Protected Data for a reasonable time while a provisional patent is filed, as the award terms allow. Any
> resulting product is manufactured substantially in the United States. No other outputs are withheld.

*Evidence:*
- Value in open ecosystems is captured by services and data, not by closing methods (README §2).
- University licensing income rarely covers technology-transfer costs, and the largest returns come through
  inventor-founded startups (Edison round 3).
- A single written rule replaces three conflicting statements.

## Partner roles (to make consistent)

> Thermo-Calc Software AB is a [funded / unfunded] partner that provides [licences / technical support / database
> development]. Its IP terms are set out in [the OT agreement / a letter].

Choose one wording and use it everywhere: `tex` currently says "funded partner", the checklist says "unfunded
partner", and `high-throughput-calphad.md` says "NOT a funded partner".

## Why this positioning is competitive

- The FOA defines open source broadly ("any arrangement that furthers the objective of openness") and asks how
  applicants will protect sensitive data while "maximizing the value of the resulting AI capability".
- DOE's own national labs release about 94% of their inventoried software as open source, mostly BSD-3 or MIT.
- The Genesis Mission's AI partners, Anthropic and OpenAI, are building agentic access to national-lab science,
  and Anthropic plans to open-source a hardware standard for AI-operated instruments.
- An open, standards-based driver and data layer is what lets those agents use this lab.
