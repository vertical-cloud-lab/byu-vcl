# TMS 2027 Abstract — CubXL Self-Driving Laboratory Platform

## Submission metadata

- **Meeting:** TMS 2027 Annual Meeting & Exhibition, Orlando World Center Marriott, Orlando, FL, March 14–18, 2027
- **Abstract deadline:** July 15, 2026 (per ProgramMaster symposium listings; extended from July 1)
- **Format:** plain text, ≤150-word body, submitted via ProgramMaster
- **Presentation type:** Poster (decision in vertical-cloud-lab/byu-vcl#160 — keep the aqueous SDL framing rather than the electrochemistry reframe)
- **Target symposium:** AI-Enabled Materials Processing: Integrating Accelerated Experimental Workflows and Processing-Aware Machine Learning (Edison SDL rank #1, fit 9.5/10; SDL backups: AI/ML/Data Informatics for Materials Discovery, 8.8; AI-ICME, 8.4 — see `edison-trajectories/tms-symposium-top10/`. An electrochemistry-forward reframe was also analyzed and set aside — see `edison-trajectories/tms-symposium-electrochem/`)
- **Authors:** BYU student authors TBD (Vertical Cloud Lab, BYU Mechanical Engineering — Benjamin Whitney is the primary CubXL contributor per repo activity); Alex Chan as middle author (Founder, Ursa Laboratories, Boston, MA — affiliation per GitHub profile `alexc2684` and the `ursa-laboratories` org, which hosts CubOS/Cubware; confirm preferred affiliation wording with Alex before submission); Sterling G. Baird, PI (last author)
- **Related issue:** vertical-cloud-lab/byu-vcl#159

## Title

A Benchtop Self-Driving Laboratory for Aqueous Chemistry Built on the CubXL Platform

## Abstract (150-word limit)

Useful chemistry workflows chain many unit operations — dispensing, dosing, sensing, sealing — but most low-cost laboratory automation handles only one. Modified CNC platforms, popularized for laboratory automation by Keith Brown's group at Boston University, provide an inexpensive rigid gantry that can carry many tools, and were subsequently commercialized as the CubXL platform with its CubOS control layer. We bring our own tools onto a CubXL base: liquid handling, single-powder dosing from manually swappable cartridges, in-line pH measurement, vial capping and decapping, and camera monitoring of runs. This enables unattended solid-liquid sample preparation in sealed vials with full provenance; capping limits evaporation and keeps the pH probe wet between measurements. Planned closed-loop campaigns pair the platform with Bayesian optimization for solubility and dissolution measurement, pH-controlled precipitation, and leaching. We report integration lessons, cost, and current limitations of bring-your-own-tool automation on a commercial base platform.

## Word count

144 / 150 words (verify with `python3 -c "print(len(open('abstracts/tms-2027-cubxl/abstract.md').read().split('## Abstract (150-word limit)')[1].split('## Word count')[0].split()))"`)
