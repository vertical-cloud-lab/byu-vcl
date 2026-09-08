# Question

This is a follow-up to a prior high-effort literature query on low-cost 6-DOF arms with
eye-in-hand cameras in self-driving laboratories (SDLs). That query concluded that the
least-crowded, highest-need contributions for a small academic lab are, in rank order:
(1) publishing a real **mean-time-between-intervention (MTBI)** and failure taxonomy for
an arm-based SDL — no deployed SDL paper reports MTBI for the arm specifically;
(2) the **first quantitative metrological characterization of a sub-$5k 6-DOF arm**
(AgileX PiPER class) under lab-relevant conditions; and (3) **vision-corrected
manipulation primitives** that close the repeatability gap between a $2.5k arm and the
sub-millimetre tolerances of real lab tasks.

I now want a deep, methods-focused treatment of how to actually execute (1) and (2)
rigorously enough to be publishable and to become the reference other groups cite.

# Specifically, please address

1. **How to measure robot-arm accuracy and repeatability properly, on a budget.**
   What do the relevant standards actually specify — **ISO 9283** (manipulating
   industrial robots, performance criteria and test methods), **ISO/TS 15066** for
   collaborative operation, **ASME B89.4.22** and **ISO 10360** for articulated
   measurement systems, and **VDI/VDE 2617-9**? Give the concrete test procedure: pose
   set, number of cycles, load conditions, warm-up, and the exact definitions of pose
   accuracy `AP`, pose repeatability `RP`, multi-directional pose accuracy variation
   `vAP`, distance accuracy `AD`, and drift `dAP`. Then: which parts of ISO 9283 can a
   university lab realistically execute **without** a $100k laser tracker? Critically
   evaluate the low-cost ground-truth options — photogrammetry / stereo camera rigs,
   ChArUco-board bundle adjustment, dial-indicator ballbar-style fixtures, LVDT nests,
   3D-printed kinematic reference artifacts, a used CMM, laser interferometry, and
   commodity motion capture (OptiTrack/Vicon vs. cheaper alternatives) — with achievable
   uncertainty for each, and state what uncertainty you need to credibly certify a
   claim of "0.1 mm repeatability" or to refute it.

2. **Thermal drift and duty-cycle effects.** How is thermal drift of robot arms
   characterized and reported in the literature? What magnitudes are observed for
   harmonic-drive and cycloidal-drive arms during warm-up and sustained duty, and over
   what time constants? What is known specifically about drift in low-cost arms using
   integrated modular joint actuators with brushless motors and planetary or harmonic
   reducers? How should a warm-up protocol and ambient-temperature logging be designed
   so results are reproducible?

3. **Reliability engineering for autonomous laboratories.** Beyond MTBI: what metrics,
   failure taxonomies, and reporting conventions exist or are being proposed for
   autonomous experimentation (e.g. per-operation success rate, mean time between
   failures, campaign completion probability, overall equipment effectiveness, autonomy
   level scales for SDLs)? Are there published failure taxonomies for laboratory
   robotics, and what do adjacent fields — semiconductor fab, industrial robotics,
   spacecraft autonomy, warehouse automation — use that the SDL community should adopt?
   What sample sizes and confidence intervals are needed to make a defensible MTBI claim
   (e.g. how many cycles to distinguish 97.5% from 99.8% per-operation reliability)?
   What is the right statistical model — binomial per-operation, Weibull time-to-failure,
   or a renewal process — and how should censored data and mixed failure modes be
   handled?

4. **Existing benchmarks and datasets to build on rather than reinvent.** What robot
   manipulation and lab-automation benchmarks exist that a small lab could adopt or
   extend (e.g. NIST assembly task boards, YCB object set, RoboCup@Work, FMB, Ranking
   the Real, and any lab-automation-specific benchmark)? Is there a standard labware
   task board? If not, what would one need to contain to be adopted by the SDL
   community, and who would need to endorse it?

5. **Publication and venue strategy.** Which venues actually publish robot-arm
   metrology and reliability characterization (HardwareX, Digital Discovery, JOSS,
   Measurement, Precision Engineering, IEEE T-ASE, RA-L, Journal of Laboratory
   Automation / SLAS Technology)? What have their recent accepted papers of this type
   looked like in scope, and what does each require in the way of open data, open
   hardware files, and reproducibility artifacts? What are the realistic review-cycle
   times?

6. **The minimum credible paper.** Concretely specify the smallest experimental campaign
   that would support a defensible paper combining (1) and (2): the exact pose set, cycle
   counts, payload and reach conditions, thermal protocol, measurement instrument and its
   calibration, statistical analysis plan, and the data/code artifacts to release. State
   what reviewers of the venues in part 5 would most likely attack, and how to preempt it.

Cite specific standards clauses and numbers wherever possible, prioritize 2020-2026
sources for the reliability and benchmark material, and clearly flag extrapolation.
