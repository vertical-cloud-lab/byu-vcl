# Electronic Supplementary Information

**for** "Replication, not fabrication: documentation is the rate-limiting step for democratized self-driving labs"

Contents

- Note S1. Project descriptions as contributed by their developers
- Note S2. Workshop survey
- Note S3. Evidence for the documentation self-audit (Table 5)
- Note S4. Labour-cost analysis: method, per-project values and full sensitivity sweep

Files supplied with this ESI: `labor_cost_analysis.py`, `table1-derived.csv`, `sensitivity.csv` (also archived at Zenodo; see the Data availability statement).

---

## Note S1. Project descriptions as contributed by their developers

The main text gives condensed descriptions so that each project can be tied to the argument. The full descriptions below are reproduced as the developers contributed them to the original submission (DD-PER-12-2024-000410; preprint 10.26434/chemrxiv-2025-zhkrf), so that no contributor's account is lost. Only typographical slips have been corrected. Citation markers have been removed; the works they referred to are cited in the main text. Project numbers P1–P10 follow Table 1 of the main text.

### Stand-alone tools

#### P1: Powder dispensing module

Solids handling, in particular powder dispensing, is a ubiquitous task, yet it is also extremely challenging to automate with the necessary precision and reliability. Commercial powder dispensing systems promise high accuracy and precision, but are expensive and lack the flexibility required to integrate with modular automation workflows. Existing open-hardware projects like the Open Trickler did not meet the developers' material compatibility or modularity requirements. In particular, they required a powder dispensing module that integrated the capability to mix powders with an input liquid to produce a mixed substance. The developers decided that high accuracy was not their most important criterion for their use cases, especially given that the powder dispensing system would be used in an iterative optimization format where dispensed amounts can be adjusted and averaged over multiple experiments. To meet their needs, the developers designed their own powder dispensing system. It uses a stepper motor to drive a precision auger and an integrated balance for feedback control over the dispensed powder amount. This feedback ensures precision and repeatability across a range of powder types and quantities. The powder is dispensed into a disposable syringe body, where a peristaltic pump mixes it with a liquid. The modular design includes a low-cost interchangeable dispensing head that can be easily swapped, allowing for the use of dedicated components for each powder used. This tool provides affordable, modular powder-dispensing capability that can be integrated in line with other tools in the researcher's workflow.

#### P2: LEDbyXample modular photoreactor

Using intense light is common during experimental chemistry workflows including crosslinking, photopolymerization, and augmenting reaction pathways. The LEDbyXample photoreactor is an inexpensive and modular photoreactor designed for integration with automated chemistry setups including self-driving labs. It is designed modularly with simple parts and a 3D printed frame. Swappable light-emitting modules containing ~1W LEDs of specific wavelengths mounted to heat sinks are slotted onto the side of the reactor. A fan with mounted magnets is incorporated into the base of the reactor to allow for magnetic stirring of a small stir bar. An active cooling module can be mounted onto the side of the reactor. All modules are controlled using custom PCB boards in tandem with a Raspberry Pi Pico and simple Python code. Clear documentation of the build process and required parts is freely available (see Table 1). Most components are relatively easy to modify or scale for specific experimental requirements.

In designing LEDbyXample, the developers sought to build an automation-friendly system that was more flexible and lower cost than other options available, such as the open-hardware Wisconsin Photoreactor platform and the budget commercial Pioreactor. This project's developers wanted a system that was lower-cost than Pioreactor while providing easy assembly and extensibility so researchers can modify the design and incorporate new capabilities. The relatively simple fabrication can also serve to reinforce builders' skills with prototyping electronics, 3D printing and using a microcontroller.

#### P3: Rolling ball viscometer

Rheology, in particular viscometry, is a common measurement in formulation applications. Complete rheological characterization of samples requires large, expensive equipment, is time-consuming, and is challenging to automate. Sample loading and equipment cleaning are particularly difficult to automate on traditional rheometers. Low-fidelity proxy methods are commonly used to estimate viscosity in end-use applications, such as the estimation of paint viscosities by timing drainage from a perforated cup. Automated viscometry for Newtonian fluids has also been demonstrated on pipetting robots by comparing set dispense rates to actual liquid dispense rates. The developers of the rolling ball viscometer needed an affordable, repeatable, and automated method to measure the viscosity of Newtonian fluid samples. This project utilizes the rolling ball principle and Stoke's law to measure fluid viscosity. A liquid sample is loaded into a clear tube, then the tube is rotated so that a small ball rolls through the fluid. The motion of the ball is captured with a high-speed camera, allowing the Newtonian viscosity of the fluid to be estimated with Stoke's law. This design allows for automated sample loading and cleaning with peristaltic pumps. The developers decided to build their own tools for this application because they did not find any alternatives that met their requirements for cost, precision, and scalability that would integrate into their workflows.

### End-to-end automation systems

#### P4: Color mixing bot

Implementing a self-driving lab and using it effectively to accelerate research requires a diverse set of skills including hardware engineering, software development, data science and machine learning, background in the scientific application of interest, and system-wide debugging. No conventional degree program teaches the complete combination of prerequisites. Thus, significant opportunities for education and 'on-the-job' training are necessary to advance the adoption of SDLs. Color mixing experiments have become a standard entry point for new users. The objective of a color-matching experiment is to reproduce a target color by learning an appropriate ratio of primary colors to mix. Successful implementation requires automated sample preparation, characterization, machine learning-based experimental design, and workflow orchestration. Progress can be easily monitored visually with a digital camera or spectrometer, and it can be performed with safe chemicals (e.g., food coloring in water) or no chemicals (e.g., mixing LED light intensities). This color mixing bot project increases the complexity by adding a pH matching objective, extending the classic demonstration to a multi-objective context. The system integrates all the necessary components to run the experiment into a compact package. Peristaltic pumps are used to mix stock solutions in a measuring chamber. Stock solutions include colored solutions and clear solutions with acidic or basic pH (achieved with lemon juice or soap). An RGB sensor measures the resulting color, and a pH probe measures pH. A multi-objective Bayesian optimization algorithm learns the optimal ratio of stock solutions to make a solution with target color and pH. This platform is well suited for use in educational settings due to its low cost, portability, and lack of chemical or mechanical hazards.

#### P5: DiSCO materials synthesis and characterization system

To bring a self-driving lab to life, individual automation components must be strung together with sample transfer and control orchestration infrastructure. Many self-driving lab builders turn to robotic arms to shuttle samples between individual workstations in an SDL. While this approach can integrate stand-alone equipment for specific tasks and enables the re-use of human-centric experiment steps, throughput cannot be maximized and challenges arise due to the cost and complexity of reliable robotics. Pursuing a user-developed end-to-end automation hardware approach can provide an opportunity to reconsider and simplify how steps in a sample preparation workflow are physically integrated to maximize reliability and throughput for autonomous campaigns extending several weeks. The DiSCO (Discovery, Synthesis, Characterization, and Optimization) platform takes advantage of this opportunity to simplify the integration of synthesis and characterization for automated experimentation in high-dimensional materials search spaces such as perovskite semiconductor compositions. DiSCO is designed to screen these search spaces and identify regions of high-performing materials with high-throughput but low-fidelity methods. These proportions of these discovered regions can then be further considered with more expensive, higher-fidelity manual experiments. DiSCO integrates several modular components for the synthesis, characterization, and optimization of drop-cast materials. Modules include Archerfish combinatorial printing synthesis technology expanded for 10-dimensional rapid drop-cast synthesis of materials, automated optical and contact-based characterization, and custom machine learning models for experimental control. To integrate the physical synthesis and characterization modules, DiSCO is built around a linear rail that moves samples from module to module. This reduces the sample positioning problem to reliable movement along one axis, improving positional accuracy and decreasing jerk and vibrations. In-house development of the integrated modules allows them to work with this sample positioning system. The modules are all open-source, aside from commercial components like hyperspectral imagers. This flexible platform could easily be modified or expanded to support different synthesis methods of characterization modules and enable use cases in diverse materials problems.

#### P6: Science Jubilee

While the DiSCO project automates experiments by bringing samples to tools, the science-jubilee platform brings the tools to the samples. The science-jubilee project is an experiment automation ecosystem comprising 3 main elements: (1) open-hardware experimental automation tools, (2) software modules which provide flexible control of these tools, and (3) a community of users who contribute to the advancement of the project. It aims to provide flexible, application-agnostic automation infrastructure that researchers can use to explore possibilities for integrating automation into their work. Science-jubilee builds on the success of the Jubilee open-source tool-changing 3D printer by adding tools and capabilities that make it easy to use this motion platform for experimental automation. The Jubilee motion platform is built from a kit that consists of common off the shelf parts and a few commercially available custom components. The tool-changing capability of the platform allows researchers to run multi-step experimental workflows without moving samples to different locations on the same machine or to different machines altogether. A growing library of open-hardware tools enables common tasks like liquid handling, sample imaging, and sonication. A Python library provides a straightforward high-level interface for programming experiments. Documented tool and software interfaces make it possible to develop new tools that extend the platform's capability. Thorough documentation describes in step by step detail the process of building, provisioning, and using the science-jubilee system. The project has a strong focus on building community involvement and adoption. The developers host workshops, engage new users on a Discord server, and travel to showcase the platform. The flexibility of the platform makes it useful in many self-driving lab contexts. The above-mentioned color matching experiment can also be implemented on science-jubilee using a liquid handling tool and a camera tool, making it a useful platform for education and outreach. However, the extensibility and reliability of the motion platform also make it a powerful tool for enabling a wide range of automated scientific workflows, such as for the sonochemical synthesis of quantum dots or automated plant growth monitoring. Science-jubilee fills a large gap in capabilities and cost between truly low-cost automation, such as hacked 3D printers, and commercial automation solutions.

#### P7: Workflow for the development of redox-active compounds

Flexible open automation ecosystems like the science-jubilee platform promise to lower barriers to entry in SDLs by providing baseline infrastructure that can be used by researchers to automate specific tasks in their workflow. In this project, the developers take advantage of the capabilities of the science-jubilee platform to build a novel electrochemical workflow for the development of redox-active compounds. This workflow includes several tasks including the chemical synthesis, isolation and characterization of redox-active compounds. The science-jubilee Opentrons OT2 pipette adapter is used with an Opentrons OT2 P300 pipette to perform liquid handling tasks. The project developers are designing a custom science-jubilee tool to integrate a commercial BluRev rotating disk electrode (RDE). This will allow for the automation of electrochemical characterization steps. In addition, the science-jubilee python control software allows the developers to efficiently program and automate materials synthesis (such as metal-ligand coordination compounds) and characterization (including cyclic voltammetry and kinetic analysis of redox events). The developers chose to build this project on the science-jubilee platform due to its ease of extension to include new tools, programmability, and affordable cost. In particular, the flexibility of the science-jubilee software and friendly graphical user interface facilitated the integration of the rotating disk electrode and ultrasound cleaning tools. Similar workflows could be performed on commercially available automation platforms but at much higher cost.

#### P8: Multi-Platform Liquid Handling Tool

When building SDL platforms from existing equipment, integrating heterogeneous mounting, power supply, and control connections can be complicated. Tool developers can remove complexity from this process by building devices with stand-alone packaging, power supply, and controls. This can allow for easier adoption of their devices on new platforms. Liquid handling in particular is a task that is at the core of many automated experiments. This project modified the existing Digital Pipette tool's design and control system so that it works as a stand-alone device, enabling its easy integration with many SDL platforms. The Digital Pipette is a low-cost and easily adaptable liquid handling device that can be integrated into flexible research setups. The tool provides a liquid handling solution with a price of less than $100 USD, replaceable fluid-contacting components, and easy fluidic integration via luer-lock tip syringes. The design is remarkably simple, involving a self-contained linear servo actuator, a syringe, and 3D printed frame components. This project modified the original Digital Pipette design with a 3D printed attachment that allows the tool to be mounted on motion platforms, such as science-jubilee or robotic arms. Additionally, MQTT communication capabilities were implemented which enable the pipette to work in tandem with other devices. The integration of the Digital Pipette tool has been successfully reproduced by several groups and science-jubilee users, where it is actively used in ongoing research.

### Control and orchestration software

#### P9: Public control of an Open Flexure microscope

Automated experimentation opens up new possibilities for how researchers use equipment and perform experiments. For example, distributed experiments have combined resources located around the world. Future SDLs that operate as user facilities will also likely require distributed access to equipment. This project explored use cases for remote equipment access systems by building a remote interface to the Open Flexure microscope. The Open Flexure microscope platform has gained popularity as a low-cost, programmable, open-source option. The programmable nature of the microscope is essential in automation, making tasks such as taking scans of larger areas much faster and more efficient. This project developed a software interface that enables public remote access to a programmable Open Flexure microscope. The interface uses the MQTT protocol to allow users to position the stage, focus, and capture images remotely via a python interface. The requesting credential system of this project allows unrelated individuals to take turns using the microscope. The Open Flexure microscope was chosen as the equipment to build this system due to its wide adoption and open source status. The microscope's code is also open source, and the hardware is relatively inexpensive compared to other options. This project expands on existing open source microscope control software such as Micro Manager by allowing remote, public control to the tools. This system has the potential to enable cloud experimentation tasks for education or research, broadening access to research equipment to anyone with an internet connection. While this project focused specifically on enabling microscope access, similar implementations could be developed to extend the accessibility of many tools in automated experimentation, including several other examples from this workshop.

#### P10: IvoryOS

The projects described so far have focused on enabling autonomous experimentation through the advancement of hardware capabilities. While these advancements are important, they are not enough to realize democratized access to SDLs. Reliable and efficient orchestration and control software is a critical part of SDL infrastructure. Currently, it is common for SDL developers to create their own control software by stringing together scripts and notebooks. While this can get an effort off the ground, controlling SDLs programmatically requires a steep learning curve that turns away many researchers without coding experience. This status quo also leads to challenges in maintainability, extensibility, and reproducibility of automation systems. Many initiatives have sought to provide software frameworks for SDL control and orchestration including ChemIDE and 𝜒DL, AlabOS, and ChemOS 2.0. However, easy integration with existing software is challenging due to the heterogeneity of SDL components. SDL research objectives are also fluid, making rigidly configured control software difficult to maintain. The ivoryOS project aims to provide adaptable, easily integrated GUI interfaces to SDL platforms that will make programming and controlling SDLs easier for researchers. To achieve configuration-free GUI integration, the ivoryOS works as an extension to existing Python scripts to dynamically manage module states. During setup, the backend will capture the SDL features by iterating through instances and inspecting their available methods and parameter requirements (serialization). This captured snapshot summarizes the platform's functionalities and updates the web GUI fields accordingly, where users can visualize the method and interact with SDLs. This permits flexibility in SDL developments, where there is no constraint in frameworks or layouts, meeting the continuous development requirement of SDLs. Additionally, the GUI also provides low-code programming for quick workflow design using available methods, allowing flexibility in building various experiments. The experiment execution has a self-driving centered design, featuring built-in iteration options including simple repeat, high-throughput or adaptive experimentations. When configuring optimization parameters, the GUI provides a code-free interface for users to configure parameters and objectives for their optimization campaign. This adaptability simplifies the initial setup and enhances the flexibility to incorporate a variety of devices, providing a ready-to-use GUI option when sharing SDLs to the broader audience.

---

## Note S2. Workshop survey

A survey of attendees was administered during the Democratizing Self-Driving Labs workshop at the 2024 Accelerate Conference (Vancouver, BC) to assess community needs for democratized SDL adoption. There were 58 respondents. The main text reports two results:

- Respondents ranked "Developing low-cost SDL equipment and shared blueprints" as a top priority for advancing democratized SDLs.
- Over 70% of respondents said they were willing to publish hardware designs and related software.

**[TO SUPPLY: survey instrument verbatim; per-item response distributions; number of attendees, for the response rate; whether responses were collected before or after the showcase; consent and ethics statement. Owner: Brenden Pelkie and Lilo D. Pozzo (sign-off BP-2, BP-3, LDP-1). If the instrument and distributions were not archived, replace this paragraph with: "The survey instrument and per-item response distributions were not archived; the two aggregate results above are those recorded at the time."]**

---

## Note S3. Evidence for the documentation self-audit (Table 5)

**Method.** On 2026-10-10 we checked every project against its live public resources: repositories via the GitHub and GitLab APIs, documentation sites, Zenodo, Software Heritage, Crossref and OpenAlex. Scores use one rubric for all projects:

- **Procure:** a bill of materials with parts, quantities and sources (print files count for printed parts).
- **Build:** assembly or fabrication instructions together with CAD or fabrication files.
- **Configure:** installation, wiring and calibration.
- **Run:** operating instructions with an example.
- **Troubleshoot:** written troubleshooting, FAQ or known-issues content scores ● (complete); a support channel only (an issue tracker with maintainer replies, a forum or a chat server), or scattered notes, scores ◐ (partial); nothing scores ○ (absent).

Software-only projects are n/a (not applicable) for Procure and Build. The scores were proposed with the assistance of a large language model working from the resources listed here (see Acknowledgements), and each project team reviewed its own row. Negative results (nothing found) are recorded, with the exact searches that produced them, in the audit files (`audit/`) of the repository named in the Data availability statement.

<!-- SIGN-OFF: every team (TV-4, OM-3, TB-3, BP-8, P7-4, SGB-10, JEH-2). "Each project team reviewed its own row" becomes true only when they have. -->

### P1 Powder dispensing module

- **Repository:** github.com/loppe35/PowderDispensing_and_Weighing_Module, with submodules PowderDispenser_BuildFiles, PowderDispenser_FWSW and PowderDispenser_Data. Created 2024-12-12; release v1.0.0 on 2025-01-27.
- **Deposit:** Zenodo 10.5281/zenodo.14746532 (concept DOI 10.5281/zenodo.14746531). The archive holds the README, the licence texts and **empty submodule folders**, because Zenodo's GitHub integration does not capture git submodules. The README still says a DOI "will be added once available".
- **Not linked:** the original submission listed this project as "manuscript in progress".

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | ◐ | BuildFiles README, "Additional Hardware Components": main electronics are linked to vendors, but there are no quantities or costs, and fasteners, fan, auger, bearings, tubing and power supply are missing |
| Build | ◐ | STEP and STL files for 18 parts, renders, `Circuit.png`, print settings. The 7-step assembly text is skeletal, and 16 of the 22 file names it cites are not in the repository |
| Configure | ◐ | PlatformIO build, pip install and `config.json` calibration are documented. However, 11 FWSW files (including `platformio.ini`, all five firmware headers and `requirements.txt`) contain unresolved merge-conflict markers on `main` and in the v1.0.0 commit, so these steps fail as written |
| Run | ● | `Use_Example.ipynb` (73 cells: checks, demo, calibration, sensitivity/accuracy/stability tests) |
| Troubleshoot | ● | Dedicated "Troubleshooting / Common Issues" section (three items) |
| Licence | inconsistent | Hardware CERN-OHL-W-2.0 (BuildFiles); software MIT intended, but `LICENSE.md` contains merge-conflict markers; no licence at the repository root; Zenodo metadata says CC BY 4.0 |

### P2 LEDbyXample modular photoreactor

- **Repository:** github.com/AC-SDL4/photo-reactor. The URL in the original submission, github.com/owen-melville/photo-reactor, now redirects there.
- **Activity:** last commit 2025-01-28; no releases.
- **Deposit:** none.

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | ● | README "Step 1" tables: supplier, part number, quantity, cost, link (stir bar, vials and fasteners not listed) |
| Build | ● | Steps 3a–3g with photographs and circuit diagrams; STL and Fusion 360 sources |
| Configure | ◐ | MicroPython flashing, upload and wiring are covered. There is no LED, temperature or stirring calibration, and host-side control is only in the undocumented `serial_test.py` |
| Run | ◐ | The README documents `turn_on_led` and `set_led_brightness`, but the code defines `turn_on_LED` and `set_brightness`; `reactor_test.py` defines functions only |
| Troubleshoot | ◐ | Scattered notes ("Tricky step" alerts, fan initialization caveat); issue tracker with one maintainer reply (#1); issue #2 (2026-09-10) unanswered |
| Licence | none | No licence file |

### P3 Rolling ball viscometer

**Nothing public was found:** no repository on GitHub or GitLab (including every project in the `auto_lab` group), no deposit on Zenodo, Figshare or OSF, and no publication. Every cell is ○.

### P4 Color mixing bot

- **Repository:** gitlab.com/auto_lab/47332-student-excercises, with branches `main`, `student_excercises` and `ph`. Last commit 2024-07-30; no releases. Mirrors: github.com/dtu-energy/color_mixing_pumpbot and github.com/gambhirkshitij/47332-2024.
- **Deposit:** none.

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | ○ | No bill of materials in any branch or mirror; parts can only be inferred from firmware `#include`s |
| Build | ○ | No CAD, assembly instructions or wiring diagram |
| Configure | ◐ | Calibration notebook 01, Excel and configuration templates, pip install; no flashing instructions; wiring given as pin numbers only |
| Run | ● | Eight notebooks (00–07). They sit on the non-default `student_excercises` branch, and the pH (multi-objective) extension described in the main text exists as code on the `ph` branch with no example |
| Troubleshoot | ◐ | Scattered tips (Arduino reset, serial-port fallback, a "may contain bugs" banner) |
| Licence | none | No licence file; `setup.py` declares MPL-2.0 |

### P5 DiSCO platform

- **Repositories:** github.com/PV-Lab/Archerfish (Apache-2.0), github.com/PV-Lab/SDCNN (MIT) and github.com/PV-Lab/Autocharacterization-Bandgap (MIT). github.com/PV-Lab/DiSCO exists but has been an empty placeholder since 2024-02-01.
- **Deposits:** SDCNN only, Zenodo 10.5281/zenodo.15556275, which archives a fork.
- **Description:** the integrated platform is described only in a 2025 MIT doctoral thesis (hdl.handle.net/1721.1/165609). The platform uses Archerfish 4.0 (ten precursors), whose files have not been released; the repository holds Archerfish 1.0.

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | ◐ | `Archefish BOM.xlsx` covers Archerfish 1.0 only (about USD 507); nothing for the rest of the platform |
| Build | ◐ | Archerfish 1.0 CAD; assembly steps only in the paper's SI and the thesis; nothing for platform integration |
| Configure | ◐ | Software installation documented; wiring and PWM settings only in the thesis |
| Run | ◐ | SDCNN and Bandgap example notebooks; no Archerfish operating procedure and no platform orchestration code |
| Troubleshoot | ○ | Nothing in any repository; no issues filed |
| Licence | Apache-2.0, MIT | Per module repository |

### P6 Science-jubilee

- **Repository:** github.com/machineagency/science-jubilee, renamed from `science_jubilee`, which redirects. Last release v0.3.2 on 2024-05-29.
- **Documentation:** science-jubilee.readthedocs.io.
- **Deposit:** none. Software Heritage holds only a 2024-08-17 snapshot under the old URL.

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | ● | `building/building_a_jubilee` (kit sources, tool list with vendor links); jubilee3d.com Getting_Parts; parts tables with quantity, vendor and cost in the tool build pages; STL, STEP and F3D files in `tool_library/` |
| Build | ● | Step-by-step frame, axis, toolchanger, wiring and per-tool build pages; assembly PDFs |
| Configure | ● | `getting_started/installation`, `tool_offsets`, `wiring`; Duet configuration files |
| Run | ● | `new_user_guide`, `pipette_guide`, `color_mixing_setup`; nine notebooks |
| Troubleshoot | ● | `new_user_guide#first-line-troubleshooting` (no power, axis not moving, endstop crash, probing); "If it doesn't:" checklist in the syringe tool page; plus two Discord servers and the issue tracker |
| Licence | MIT, CC BY 4.0 | Software MIT; Jubilee hardware CC BY 4.0 |

### P7 Electrochemical workflow

- **Tool files:** github.com/ethraj2001/jubilee, commit d5c5969 (2024-08-27), "added a new RDE tool for Jubilee 2.2". It adds three STL files for the rotating-disk-electrode adapter. They were offered upstream as machineagency/jubilee pull request #204, which is still open and unmerged.
- **Control code:** github.com/cyrilcaoyang/jubilee-sdl2 (archived, MIT), commit bc548db (2025-02-13). It contains an RDE tool class adapted from the science-jubilee pipette tool, a configuration file and a deck definition.
- **Deposit:** none. Not linked from the original submission.

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | ◐ | Print files only; no parts list for the electrode, potentiostat, fasteners or cell |
| Build | ◐ | Print files only (no source CAD, no assembly steps) |
| Configure | ○ | Configuration stubs without instructions |
| Run | ○ | `demo.py` only picks up and parks the tool; no electrochemistry workflow is public |
| Troubleshoot | ○ | None |
| Licence | MIT, CC BY 4.0 | Code MIT; the print files inherit CC BY 4.0 from the Jubilee repository |

### P8 Digital pipette integration

- **Code and print files:** github.com/AccelerationConsortium/ac-dev-lab, folder `src/ac_training_lab/picow/digital-pipette`. It contains Pico W MQTT firmware, a secrets template, time-synchronization and web-app scripts, and `designs/Science_Jubille_Adapter v0.stl` and `designs/pipettecase1 v2.stl`.
- **Documentation:** a docs page at ac-training-lab.readthedocs.io/en/latest/devices/picow-digital-pipette.html, and a parts list (12 items, quantities, no suppliers) in a Google Doc linked from forum thread accelerated-discovery.org/t/236.
- **Deposit:** none; the repository has no releases.
- **Attribution:** the folder carries no attribution to the CC BY 4.0 Digital Pipette design it modifies.

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | ◐ | Parts list with quantities but no suppliers, outside the repository; print files |
| Build | ◐ | Print files and videos; no written assembly steps |
| Configure | ◐ | Firmware and configuration template; no written setup |
| Run | ◐ | Example scripts; no operating instructions |
| Troubleshoot | ◐ | Forum thread /t/236 with maintainer and original-author replies; open issues #138 and #146 |
| Licence | MIT | Repository licence |

### P9 OpenFlexure public control

- **Repository:** github.com/AccelerationConsortium/ac-dev-lab, renamed from `ac-training-lab`, which redirects. The canonical documentation remains ac-training-lab.readthedocs.io; ac-dev-lab.readthedocs.io returns 404.
- **Missing:** the code that runs on the microscope itself is not in the repository (issue #37, open since 2024-09-16).
- **Public interface:** on 2026-10-10, the two Hugging Face Spaces that host it were sleeping and in a runtime error.
- **Deposit:** none.

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | ◐ | Delegated to the commercial kit and the upstream OpenFlexure parts list, reachable via forum thread /t/231 |
| Build | ◐ | Upstream build documentation via /t/231 and /t/254 |
| Configure | ◐ | Network setup notes only; microscope-side MQTT service and broker setup missing |
| Run | ◐ | `use.py` example and MQTT client in the code; the docs page has no operating instructions, and the public interface was not running |
| Troubleshoot | ◐ | Issues #58 and #81 with maintainer replies; forum thread /t/254 |
| Licence | MIT | Repository licence |

### P10 IvoryOS

- **Repository:** gitlab.com/heingroup/ivoryos (canonical), mirrored at github.com/ivoryos-ai/IvoryOS. Release v1.7.0 on 2026-10-07.
- **Deposit:** Zenodo concept DOI 10.5281/zenodo.15272617 resolves to a single version (10.5281/zenodo.15272618, 2025-04-24). No later release is archived, and the deposit declares CC BY 4.0 while the repository is MIT.

| Capability | Score | Evidence |
|---|:-:|---|
| Procure | n/a | Software |
| Build | n/a | Software |
| Configure | ● | README installation; integrator quick-start; contributor setup |
| Run | ● | UI guide, run-behaviour page, examples, video tutorials |
| Troubleshoot | ● | "Workflow step warnings" in the deck-compatibility page; "Human intervention and errors" in the run-behaviour page; plus Discord, Slack and the issue tracker |
| Licence | MIT | Repository licence (deposit declares CC BY 4.0) |

---

## Note S4. Labour-cost analysis

**Inputs.** The only inputs are the cost-to-reproduce and time-to-reproduce figures in Table 1, which the developers of each project reported themselves. No other data are used.

**Conversions.** Reported ranges are taken at their midpoints: P2 "$80–160" is $120, P5 "$30–40 K" is $35,000, and P10 "0–1 h" is 0.5 h. P5's "3 months" is read as 12 weeks × 40 h = 480 h at one full-time equivalent.

**Quantities.** For a project with bill of materials *B* (USD) and reproduction time *h* (hours), at a fully loaded labour rate *w* (USD/h):

- labour cost *L* = *w h*;
- labour share of first-build cost = *L* / (*B* + *L*);
- break-even wage *w*\* = *B* / *h*, the rate at which *L* = *B*. It does not depend on any assumed *w*. Labour exceeds parts whenever *w* > *w*\*.

**Per-project values** (from `table1-derived.csv`):

| Project | BOM (USD) | Hours | Break-even wage (USD/h) | Labour @ $25 | @ $50 | @ $75 | Labour share @ $25 | @ $50 | @ $75 | Note |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|
| IvoryOS GUI control software | 0 | 0.5 | 0.00 | 12 | 25 | 38 | 100% | 100% | 100% | reported 0-1 h per new hardware integration; midpoint used |
| LEDbyXample modular photoreactor | 120 | 24 | 5.00 | 600 | 1,200 | 1,800 | 83% | 91% | 94% | BOM range midpoint used |
| Public control of OpenFlexure microscope | 300 | 30 | 10.00 | 750 | 1,500 | 2,250 | 71% | 83% | 88% | time includes the microscope build itself |
| Science-jubilee flexible automation platform | 2,000 | 100 | 20.00 | 2,500 | 5,000 | 7,500 | 56% | 71% | 79% |  |
| Powder dispensing module | 300 | 10 | 30.00 | 250 | 500 | 750 | 46% | 62% | 71% |  |
| Rolling ball viscometer | 300 | 10 | 30.00 | 250 | 500 | 750 | 46% | 62% | 71% |  |
| Color mixing bot | 300 | 10 | 30.00 | 250 | 500 | 750 | 46% | 62% | 71% |  |
| Digital pipette Jubilee integration | 100 | 3 | 33.33 | 75 | 150 | 225 | 43% | 60% | 69% |  |
| Electrochemical workflow on science-jubilee | 20,000 | 300 | 66.67 | 7,500 | 15,000 | 22,500 | 27% | 43% | 53% |  |
| DiSCO photovoltaics platform | 35,000 | 480 | 72.92 | 12,000 | 24,000 | 36,000 | 26% | 41% | 51% | '3 months' read as 12 weeks x 40 h = 480 h at 1 FTE |

**Sensitivity of the conclusion to the assumed rate** (from `sensitivity.csv`):

| Loaded rate (USD/h) | Projects where labour > BOM | Median labour share | Mean labour share |
|--:|--:|--:|--:|
| 10 | 2 / 10 | 25% | 37% |
| 15 | 3 / 10 | 33% | 44% |
| 20 | 3 / 10 | 40% | 50% |
| 25 | 4 / 10 | 46% | 54% |
| 30 | 4 / 10 | 50% | 58% |
| 40 | 8 / 10 | 57% | 63% |
| 50 | 8 / 10 | 62% | 68% |
| 60 | 8 / 10 | 67% | 71% |
| 75 | 10 / 10 | 71% | 75% |
| 100 | 10 / 10 | 77% | 79% |
| 125 | 10 / 10 | 81% | 82% |
| 150 | 10 / 10 | 83% | 85% |

**Reproducing.** `python labor_cost_analysis.py` (Python ≥ 3.9 with matplotlib) rewrites both CSV files and Figure 1. Re-running it on 2026-10-10 reproduced both CSV files byte-for-byte.
