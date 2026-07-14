# TMS 2027 Abstract — CubXL Self-Driving Laboratory Platform

## Submission metadata

- **Meeting:** TMS 2027 Annual Meeting & Exhibition, Orlando World Center Marriott, Orlando, FL, March 14–18, 2027
- **Abstract deadline:** July 15, 2026 (per ProgramMaster symposium listings; extended from July 1)
- **Format:** plain text, ≤150-word body, submitted via ProgramMaster
- **Presentation type:** Poster (decision in vertical-cloud-lab/byu-vcl#160 — keep the aqueous SDL framing rather than the electrochemistry reframe)
- **Target symposium:** AI-Enabled Materials Processing: Integrating Accelerated Experimental Workflows and Processing-Aware Machine Learning (Edison SDL rank #1, fit 9.5/10; SDL backups: AI/ML/Data Informatics for Materials Discovery, 8.8; AI-ICME, 8.4 — see `edison-trajectories/tms-symposium-top10/`. An electrochemistry-forward reframe was also analyzed and set aside — see `edison-trajectories/tms-symposium-electrochem/`)
- **Authors:** TBD (Vertical Cloud Lab, BYU Mechanical Engineering; Sterling G. Baird, PI)
- **Related issue:** vertical-cloud-lab/byu-vcl#159

## Title

Modular Benchtop Self-Driving Laboratory for Closed-Loop Aqueous Materials Chemistry Using Interchangeable Powder, Liquid, and Sensing Modules

## Abstract (150-word limit)

Self-driving laboratories are usually bespoke builds: expensive, tied to one site, and hard for other groups to reproduce. We built a benchtop alternative on CubXL, a modular gantry platform running the open-source CubOS control layer with version-controlled YAML protocols, offline motion validation, and a local experiment database. Interchangeable deck modules handle liquids, dose a single powder from manually swappable cartridges, measure pH in-line, cap and decap vials, and monitor runs by camera. The platform prepares solid-liquid samples in sealed vials unattended and records full provenance; capping also limits evaporation and keeps the pH probe wet between measurements. Planned closed-loop campaigns pair the platform with Bayesian optimization for solubility and dissolution measurements, pH-controlled precipitation, and leaching. We report integration lessons, cost, and current limitations, and discuss how standardized swappable modules let individual research groups run replicable autonomous workflows.

## Word count

137 / 150 words (verify with `python3 -c "print(len(open('abstracts/tms-2027-cubxl/abstract.md').read().split('## Abstract (150-word limit)')[1].split('## Word count')[0].split()))"`)
