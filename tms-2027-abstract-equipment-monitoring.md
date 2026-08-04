# TMS 2027 Abstract — Livestreaming Cameras for Equipment Monitoring

- **Meeting:** TMS 2027 Annual Meeting & Exhibition, Orlando, FL, March 14–18, 2027
- **Presentation type:** Poster
- **Target symposium:** *AI-Enabled Materials Processing: Integrating Accelerated Experimental Workflows and Processing-Aware Machine Learning* (Data-Driven and Computational Materials Design track; [flyer 021](https://www.tms.org/tms2027/downloads/flyers/TMS2027-CFA-Flyer-021.pdf))
  - The flyer explicitly welcomes "real-time process monitoring," "high throughput and data-aware experimental design," and "closed-loop experimental workflows that integrate synthesis, processing, characterization, testing, and iterative model-guided refinement" — the enabling-technology angle for accelerated/self-driving experimental workflows.
  - Alternate: *AI/ML/Data Informatics for Materials Discovery: Bridging Experiment, Theory, and Modeling* ([flyer 022](https://www.tms.org/tms2027/downloads/flyers/TMS2027-CFA-Flyer-022.pdf)) — lists "FAIR data principles, metadata frameworks, provenance, and interoperable infrastructure" as a topic of interest.
- **Abstract deadline:** July 1, 2026 (per flyer key dates)
- **Presenter:** Seth Leavitt

## Title

**Low-Cost Open-Source Camera Modules for Continuous Monitoring of Self-Driving Laboratories**

## Authors and Affiliations

| # | Author | Affiliation(s) | Role |
|---|--------|----------------|------|
| 1 | Seth Leavitt | BYU Mechanical Engineering | Presenter |
| 2 | Yanghuang Liu | Acceleration Consortium, University of Toronto | Co-author |
| 3 | Jonathan Woo | Acceleration Consortium, University of Toronto | Co-author |
| 4 | Sterling G. Baird | BYU Mechanical Engineering; Acceleration Consortium, University of Toronto | PI |

## Abstract

*(Word limit: 150; current version: 147 words)*

As laboratories move toward higher autonomy, continuous equipment monitoring becomes
essential for debugging, provenance, and safety — echoing recent calls for aviation-style
"black box" recording in self-driving laboratories (SDLs). We present a fully open, low-cost
(<$100/module), many-camera, multi-site livestreaming infrastructure for SDL operations.
Unlike task-specific computer vision for real-time process control, each equipment module
receives a dedicated passive camera with tunable frame rate and resolution and failsafe
auto-restart for unattended operation. Dozens of modules deployed across multiple
institutions have achieved >99% uptime while collecting tens of thousands of hours of video.
Streams linked to timestamps and experiment metadata provide a visual audit trail
complementing structured records; the footage also yields heuristic utilization estimates
and, prospectively, robot-learning training data. Cameras capture only operators' hands and
forearms, a privacy-by-design choice for shared facilities housing furnaces, synthesis
platforms, and characterization instruments. All hardware, firmware, and documentation are
openly available (https://ac-training-lab.readthedocs.io/en/latest/devices/picam.html).

<!-- Source references: byu-vcl issue #9; AC Training Lab picam docs; AccelerationConsortium/streamingLambda -->
<!-- Framing informed by Edison Scientific feedback (PR #146): infrastructure novelty, visual audit trail,
     heuristic utilization, robot-learning as future work, black-box/provenance discourse (Leong et al. 2025),
     democratized SDL literature (Lo et al. 2024; Pelkie et al. 2025), materials-specific examples for TMS. -->
