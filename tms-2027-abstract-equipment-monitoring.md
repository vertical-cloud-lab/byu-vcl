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
| 4 | Kelvin Chow | Acceleration Consortium, University of Toronto | Co-author |
| 5 | Sterling G. Baird | BYU Mechanical Engineering; Acceleration Consortium, University of Toronto | PI |

## Abstract

As laboratories move toward higher levels of autonomy, continuous equipment monitoring
becomes essential for debugging, provenance, safety, and operational analytics — a need
underscored by recent calls for aviation-style "black box" recording in self-driving laboratories
(SDLs). We present a fully open, very low-cost (<$100 per module), many-camera, multi-site
continuous livestreaming infrastructure for SDL operations. Unlike task-specific computer vision
systems for real-time process control, our system provides passive, equipment-level monitoring:
one dedicated camera per equipment module, with tunable frame rate and resolution and
failsafe auto-restart mechanisms for sustained unattended operation. At the Acceleration
Consortium we deployed dozens of modules across many distinct lab spaces, achieving >99%
uptime while collecting tens of thousands of hours of video of SDL workflows; the design has
been replicated at BYU and is being implemented at several other locations. Recorded streams
are linked to timestamps and experiment metadata, providing a visual audit trail that
complements structured experiment records. The same footage yields heuristic, non-invasive
equipment utilization estimates (fraction of non-still frames), and post-processing workflows
remove idle periods to accelerate review. Cameras are positioned so only operators' hands and
forearms are captured, a privacy-by-design choice suited to shared facilities. The approach
applies directly to materials workflows — furnaces, synthesis platforms, and characterization
instruments — and complements ongoing efforts to democratize low-cost SDL infrastructure.
Beyond monitoring, the accumulated footage is a potential source of training data for future
robot-learning models. All hardware designs, firmware, and documentation are openly available
(https://ac-training-lab.readthedocs.io/en/latest/devices/picam.html).

<!-- Source references: byu-vcl issue #9; AC Training Lab picam docs; AccelerationConsortium/streamingLambda -->
<!-- Framing informed by Edison Scientific feedback (PR #146): infrastructure novelty, visual audit trail,
     heuristic utilization, robot-learning as future work, black-box/provenance discourse (Leong et al. 2025),
     democratized SDL literature (Lo et al. 2024; Pelkie et al. 2025), materials-specific examples for TMS. -->
