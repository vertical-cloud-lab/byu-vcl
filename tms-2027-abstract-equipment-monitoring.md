# TMS 2027 Abstract — Livestreaming Cameras for Equipment Monitoring

- **Meeting:** TMS 2027 Annual Meeting & Exhibition, Orlando, FL, March 14–18, 2027
- **Target symposium:** *AI-Enabled Materials Processing: Integrating Accelerated Experimental Workflows and Processing-Aware Machine Learning*
  - Alternate: *AI/ML/Data Informatics for Materials Discovery: Bridging Experiment, Theory, and Modeling*
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

Equipment monitoring is a common need across laboratories, growing as they move to higher
levels of autonomy. We present a low-cost (<$100 per module), fully open-source camera system
for continuous livestreaming and recording of laboratory equipment. At the Acceleration
Consortium we deployed dozens of these modules, collecting tens of thousands of hours of video
of self-driving lab workflows across many distinct lab spaces; the design has been replicated at
BYU and is being implemented at several other locations. One camera is dedicated per equipment
module, so only operators' hands and forearms are captured. Benefits include real-time
debugging, full provenance, review of unattended operation, and potential for real-time decision
making and training data for robot-learning models. The same footage enables non-invasive
utilization estimates (non-still frames divided by total frames). Post-processing workflows remove
still frames and speed up the remainder. Hardware, firmware, and documentation are openly
available (https://ac-training-lab.readthedocs.io/en/latest/devices/picam.html).

<!-- Source references: byu-vcl issue #9; AC Training Lab picam docs; AccelerationConsortium/streamingLambda -->
