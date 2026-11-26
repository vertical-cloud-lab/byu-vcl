# DAL and #318: an openness audit

This audit supports section 9 of [`../README.md`](../README.md) for
[#380](https://github.com/vertical-cloud-lab/byu-vcl/issues/380). It was written on 2026-11-23 from local and GitHub
files only.

**How sources are cited**
- `DAL:` means [digital-alloy-lab](https://github.com/vertical-cloud-lab/digital-alloy-lab/tree/e7a01b3) at
  `e7a01b3`, written as `path:line`.
- `#318:` means byu-vcl branch `claude/issue-303-20261103-1736` at
  [`75c0ed0`](https://github.com/vertical-cloud-lab/byu-vcl/tree/75c0ed0/vertical-lab), with paths under `vertical-lab/`.
- `VCL:` means byu-vcl [`main` at `1baa629`](https://github.com/vertical-cloud-lab/byu-vcl/tree/1baa629).
- `FOA` means `DAL:DE-FOA-0003612-000001.pdf`, by printed page (PDF page = printed + 4). `FAQ` means
  `DAL:Genesis-Mission-RFA-FAQs-20260410-v2.pdf`.
- `tex` means `DAL:genesis-mission-proposal/flaime-genesis-proposal.tex`.
- `study:` means this folder.
- "Unknown" means the notes don't say.

## 1. Public vs. private inventory

| Asset | Public | Held back, and why |
|---|---|---|
| Code | DAL under MIT (`DAL:LICENSE`): the BOFN/pKGFN benchmarks and the figure and Edison scripts. #318's 119 Python scripts, under byu-vcl's MIT (`VCL:LICENSE`) | Vendor CAD and meshes are re-fetched at run time, not committed (`#318:.gitignore:1-4`, `#318:openflexure/README.md:12`) |
| Documents | Reviews, the gotchas file, the checklist and the full proposal `.tex` (`DAL:README.md:17-37`); 78 #318 notes | Signed letters, per-person budgets and CVs (`DAL:README.md:14`). PR review history and `private/` proposal files stay private (`:10-11`; `DAL:.gitignore:195-196`). The Thermo-Calc call transcript linked at `DAL:README.md:25` isn't on `main` |
| Literature | DOIs (`DAL:literature/DOIs.md`) | Publisher PDFs, for copyright |
| Edison | About 180 Markdown files | The JSON trajectories, for size (`DAL:.gitignore:44,168`), and a Kosmos run under a U of Utah account (`:112`) |
| Data | Samples from about 20 outside sources (`DAL:database-samples/`) | No lab dataset has a DOI: DAL cites no Zenodo or Figshare record. Sensor and OT-2 records sit in a private MongoDB (`VCL:CLAUDE.md`). The rePowder's process data can't be exported yet ([DAL #151](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/151)) |
| Video | SOP and run videos (`#318:notes/dal_workflow.md:5-26`); #318's long-form, public (`#318:README.md:514-520`) | Nothing |
| Images | The lab's own figures | Vendor images ship in DAL but outside its MIT licence (`DAL:THIRD_PARTY_ASSETS.md:3, 45-81`) |
| Operations | Workflows and runbooks | Credentials and hostnames (`VCL:CLAUDE.md`, "Secret inventory") |

Method and orchestration are open; people's documents and vendor material are closed. Raw experimental data is closed
by default, and that is the gap: the FOA and the proposal both promise deposits that haven't started.

## 2. Software dependencies and their licences

DAL's code has no GPL or AGPL dependency. The copyleft and proprietary pieces sit at the edges. Licences without a DAL
citation come from the upstream LICENSE files on GitHub.

| Component | Where | Licence | Flag |
|---|---|---|---|
| torch, botorch, gpytorch, matplotlib, numpy | `DAL:requirements.txt:1-5` | BSD-style, MIT, MIT, PSF-style, BSD-3 | None |
| `partial_kgfn` port | `DAL:benchmarks/partial_kgfn/*.py:3-4` | MIT, © 2024 frazier-lab | The frazier-lab copyright notice that MIT requires isn't reproduced |
| edison-client | `DAL:benchmarks/bofn_llm_warmstart.py:159` | Apache-2.0 | Calls a paid, closed service |
| google-api-python-client, google-auth | `DAL:youtube/requirements.txt` | Apache-2.0 | Google's API terms apply |
| pycalphad | Demos (`DAL:high-throughput-calphad.md:49-260`) | MIT (`DAL:edison-trajectories/calphad_licensing.md:35`) | None |
| Equilipy | Demos | "CC BY 4.0" (`calphad_licensing.md:43`), but its LICENSE is BSD-3-Clause | Correct DAL's note |
| OpenCalphad | Demo only | GNU GPL (`calphad_licensing.md:39`) | **Copyleft**: run it as a separate program and don't vendor it |
| Thermo-Calc, TC-Python, AM Module, TCAl10/TCMG6 | The proposal's route (`tex:990-991`) | **Proprietary**: by quote; node-locked, FlexLM network or academic site licences; TC-Python capped at 32 logical processors per licence; databases extra (`DAL:high-throughput-calphad.md:453-469, 485`) | Melt-pool maps have "NO open-source equivalent" (`:595`) |
| #318 stack: cadquery, pyvista, trimesh, pycollada, Pillow, scipy, python-fcl, mujoco, coacd, psutil | `#318:README.md:3184` | All permissive (Apache-2.0, MIT, BSD, HPND) | None |
| Kokoro v1.0 voice | `#318:README.md:579` | Apache-2.0 | None |
| OpenFlexure sources | `#318:openflexure/README.md:7-10` | CERN-OHL-S-2.0 and CERN-OHL-1.2 | **Reciprocal** licences inside an MIT repo, and the derived `.scad` files carry no header |

**pycalphad vs. Thermo-Calc, in DAL's words.** pycalphad is free and has no processor limit, but free TDB files
"cannot be combined" for quaternary systems (`DAL:high-throughput-calphad.md:310, 481`). TCAl10 is consistent, but
it is sold separately (:485). DAL's funnel puts pycalphad on the volume (about 1.13M evaluations) and saves TC-Python and the
AM Module for the top 1,000 and the top 50–100 (`:591`; `DAL:genesis-mission-proposal/proposal-population-plan.md:243`).

## 3. Data sources and access terms

References are to `DAL:alloy-databases.md` unless noted.

| Source | Access | Use and caveats | Ref |
|---|---|---|---|
| Materials Project, AFLOW, OQMD, NOMAD, JARVIS | Open. AFLOW is marked "GNU". The Materials Project is CC BY 4.0, apart from a non-commercial GNoME subset (`study:companies/F/materials-project.json`) | Features (`tex:992-994`) | :22-26 |
| pycalphad TDBs, TDBDB, COST507 | Open (each TDB keeps its own terms) | Screening | :202; `DAL:high-throughput-calphad.md:1253-1254` |
| USGS MCS, DOE Critical Materials Assessment | Open (government) | Mineral burden (`tex:997-999`) | :37-38 |
| Helbig, Ferro & Bonollo, ESSENZ, BGS, WGI, UN Comtrade, EU RMIS | Open | Criticality factors | :39-44, 49 |
| Mulukutla SupplyRiskAwareDesign | Open per DAL, but the upstream repo has no licence file | Three files redistributed | :45 |
| FatigueData-CMA2022, Barrionuevo LPBF, Luo AlSi10Mg | Open (CC BY 4.0, Dataverse, Zenodo) | Training data | :230-239 |
| AlloyML | "Open", but partly built from CES EduPack and MatWeb, with no licence file upstream | Templates | :112; `DAL:database-samples/README.md:23` |
| MatWeb | Open per DAL, but only to view: it blocks automated access | Lookup | :20; `database-samples/README.md:42` |
| MatNavi, Materials Commons | Open (MatNavi needs registration) | Not yet used | :21, 31 |
| Knovel, Granta EduPack, SpringerMaterials, CINDAS, ULTERA | **Academic-only** | Knovel through U of Utah (`tex:995`). ULTERA is on request, and its contribution repo is LGPL-3.0 | :15, 18, 30, 32-33, 419-426; `database-samples/README.md:35` |
| Thermo-Calc TCAl10/TCMG6, AM Module | **Proprietary**, about $5–15K a year academic | Core CALPHAD | :27, 82-90, 432 |
| MMPDS, ASM Alloy Center, Total Materia, Aluminum Association, Pandat, JMatPro | **Proprietary** | MMPDS and ASM are the proposal's benchmarks (`tex:995-996`) | :16-17, 19, 28-29, 34, 428-437 |
| SGTE, Alloys-by-Design | **Proprietary** (consortium or industrial partners only) | None | `DAL:company-landscape.md:161`; :225-228 |

DAL found that "no single, centralized, ML-ready criticality dataset exists" (:390). Open FLAIME records would fill
that gap.

## 4. Equipment and vendors

Ratings: API/SDK (yes, partial, none, unknown); firmware (open, closed, unknown); integration docs (good, partial,
poor, unknown).

| Equipment | API/SDK | Firmware | Docs | Evidence |
|---|---|---|---|---|
| AMAZEMET rePowder (atomizer) | **None** on BYU's unit. Newer units' Advanced Control Cabinet has an API. The HMI has Ethernet and serial; the generator has Modbus RTU | Closed | Partial: the protocol and data format are "nowhere public" | DAL #151 and its comments; `#318:notes/atomizer_automation.md:44, 195` |
| Aconity MIDI (LPBF, U of Utah) | Unknown. DAL calls it "open-architecture", unverified | Unknown | Partial: no CAD | `DAL:tms-2027-lpbf-process-parameter-optimization-abstract.md:67`; `DAL:edison-trajectories/pr52-followup/pr52-review-replies.md:465`; `#318:README.md:2306` |
| Kardex Shuttle XP 500 (VLM) | Unknown | Unknown | Partial: the order sheet is hosted by a dealer, and opening options aren't published | `#318:README.md:2876-2914, 3031-3060` |
| Universal Robots UR10e/UR12e | **Yes**: URScript and a BSD-3 ROS 2 driver | Closed | Good | `#318:notes/ur12e.md:17, 26`; `study:companies/G/universal-robots-mir.json` |
| MiR250 | **Yes**: REST API and Modbus | Closed | Partial | `#318:notes/base_cameras.md:239, 277` |
| Rigaku MiniFlex 6G (XRD) | Unknown | Unknown | Partial: no CAD "without a login or a form" | `#318:README.md:2250-2254` |
| Hitachi TM4000PlusII + AZtecOne (SEM/EDS) | Unknown | Unknown | Poor: the EBSD option is undocumented | `#318:README.md:2264-2266` |
| Malvern Mastersizer 3000 (laser diffraction) | Unknown (runs from a PC) | Unknown | Partial | `#318:README.md:2280-2281`; `#318:notes/voltage.md:173-175` |
| Bruker S2 PUMA (XRF) | **Partial**: the only one of six with a published robot link | Unknown | Partial | `#318:notes/instruments_char.md:101-119` |
| Keyence VHX-7000 + EA-300 LIBS | **None documented**, so a PiKVM drives it | Closed | Poor | `#318:notes/instruments_r7.md:137-166` |
| Plastometrex PLX, KLA iMicro, LECO PX500, Instron | Unknown | Unknown | Poor: three of the four makers publish no dimensions | `#318:README.md:2250, 2269, 2279, 2285` |
| NuVant EZstat Pro (potentiostat) | **None**: Windows-only LabVIEW, no ARM driver, reached by Remote Desktop to an offline Windows 7 PC | Closed | Partial | `VCL:potentiostat/ezstat-pro/README.md:17-35` |
| Opentrons OT-2 | **Yes**: Apache-2.0 API | Software open | Good | `study:companies/E/opentrons.json` |
| CubXL (lab-built) | **Yes** | Open (PANDA_Arduino firmware, MIT) | Good | `VCL:cubos/firmware/README.md:8` |
| FANUC EDM, Nabertherm furnace, Retsch sieve, glovebox, ICP-MS | Unknown | Unknown | Unknown | `#318:README.md:2202-2230`; `#318:notes/dal_workflow.md:14`; `#318:notes/icpms.md` |

Only four have a documented interface the lab can program: UR, MiR, the OT-2 and the CubXL. That is the study's
pattern of open orchestration on closed instruments. The workarounds show its cost:
- a camera on the rePowder's HMI to log settings until AMAZEMET answers about data export (DAL #151, 2026-10-07);
- an arm pressing the rePowder's keys (`#318:notes/dal_workflow.md:42`);
- a KVM box on the Keyence;
- Remote Desktop to a Windows 7 PC for the potentiostat.

## 5. What the FOA requires and what the drafts promise

**FOA**
- **Openness.** "Open source" means "any arrangement that furthers the objective of openness", and results must be
  publishable (§III.A, "Open Science", pp. 57–58).
- **Proprietary inputs.** The application should say how it will "protect sensitive aspects of the data while
  maximizing the value of the resulting AI capability" (§IV.C, p. 71).
- **The DMSP** is "NOT required" with a Phase I application but is required "during award negotiation" (App. 4, p. 75;
  FAQ p. 9). It should cover FAIR for "data sets, software, and models", SPDX identifiers "when possible", and a
  "specific justification" for any deviation from the Open Source Definition.
- **Timing.** Data behind a publication must be public "at the time of publication" (§IX.B.12, p. 120). Limits are
  allowed to "avoid negative impact on intellectual property rights" (p. 121). Released data is reported to OSTI with
  DOIs (p. 122).
- **Rights** (§IX.C.34–39, pp. 150–152):
  - DOE gets "Unlimited Rights" in data first produced under the award.
  - Patentable information is protectable "for a reasonable time".
  - "Protected Data" can be held for up to five years.
  - Recipients "elect to retain title", with IP negotiated under the OT agreement.
  - Products embodying subject inventions must be "manufactured substantially in the United States".

**The proposal (`tex`)**
- Data and models will be "shared as a FAIR-compliant digital thread", through Zenodo or Figshare (:285-287).
- "All FLAIME software will be released open-source under a permissive license" (:668-669).
- "Discovered alloy compositions will be published openly rather than licensed" (:678-682).
- The DMSP sketch promises deposits "within 12 months of collection" and says "Data licensed CC-BY-4.0; code licensed
  MIT" (:1520-1530).

**Where the drafts disagree or fall short**
- **Three IP positions on compositions coexist:**
  - open (`tex:678-682`);
  - a "Month-6 review" of "selective IP protection" (`DAL:genesis-mission-proposal/flaime-genesis-proposal.tex.AFTER_MY_EDITS:638-640`,
    `proposal-population-plan.md:226, 234`), which is the version section 9 of the draft report quotes;
  - "proprietary alloy compositions" (`proposal-checklist.md:279`).
- **No data-sharing-limitations paragraph**, although TCAl10 outputs are listed as data to share (`tex:1506-1508`)
  and MMPDS, Knovel and ASM are inputs (`tex:995-996`).
- **"12 months of collection"** is later than "at the time of publication" for any data behind a paper.
- **Licence wording conflicts:** "MIT/Apache-2.0" (:1525) vs. "code licensed MIT" (:1529).
- **Thermo-Calc's role is inconsistent**, and that role sets its IP terms: "funded partner" (`tex:1841-1843`),
  "unfunded partner" (`proposal-checklist.md:215`) and "NOT a funded partner" (`DAL:high-throughput-calphad.md:589`).

## 6. Recommendations

1. **Licences.**
   - **Code: keep MIT,** which matches BoTorch for the promised tutorials (`tex:673-676`).
   - **Hardware: CERN-OHL-P-2.0** for the lab's own designs (cups, plugs, fixtures, #318's stations). SDL-demo pairs
     it with MIT (`study:gh-mining/commercialization_digest.md:104`).
   - **Data: CC BY 4.0, with CC0 metadata,** as Zenodo does (`study:companies/F/zenodo.json`).
   - **Add NOTICE files** to `partial_kgfn/`, `database-samples/` and `#318:openflexure/`, as
     `VCL:modules/electromagnetic-capper/cad/NOTICE.txt` already does.
2. **A home for the data, and a schema.**
   - **Zenodo** for DOI snapshots (`study:companies/CASEBOOK.md:721`).
   - **Materials Data Facility** as the DOE-facing home, which DAL's own review recommends
     (`DAL:edison-trajectories/edison-topic11c-fit-assessment.md:381`).
   - **A NOMAD Oasis** for a self-hosted FAIR server (`DAL:edison-trajectories/self_driving_labs.md:82`).
   - **OSTI registration** for every DOI (FOA p. 122).
   - **Schema.** Publish a JSON Schema for the digital thread (`DAL:edison-trajectories/edison-proposal-plan-review-round15.md:77`)
     with schema.org metadata (`tex:1515-1516`), OPTIMADE-style compositions (`edison-topic11c-fit-assessment.md:381`)
     and PROV-O provenance (`edison-kpi6-digital_thread-review.md:66`). Write one record per composition and stage
     (`DAL:edison-section-drafts/results/appendix4_dmsp_draft.md:22`).
   - **Failed runs, published too:** negative results are the signal Periodic Labs builds its closed data on
     (`study:companies/E/periodic-labs.json`).
3. **Embargo policy for compositions.**
   - **Default:** release at publication or 12 months after collection, whichever comes first (FOA p. 120;
     `tex:1521`).
   - **One exception, decided at the Month-6 gate under a written rule.** A composition that meets its targets
     (`tex:634-640`) and has a named licensee gets a provisional patent and the FOA's "reasonable time" (p. 150), not
     five-year Protected Data.
   - **Why:** AI-for-materials firms close data and compositions, not methods (`study:companies/E/radical-ai.json`).
     FLAIME's edge is its open platform. Patents also trigger the U.S.-manufacturing clause (p. 151).
   - **Reconcile the three IP statements** before award negotiation.
4. **MCP- or MHS-style drivers.**
   - **One small MIT driver per instrument,** exposed as an MCP server. MCP sits under the Linux Foundation, and the
     Model Hardware Standard is due to be open-sourced (`study:language/key_quotes.md:27, 30`).
   - **Start where interfaces exist:** MiR, UR, the OT-2, the CubXL and the S2 PUMA. Add the rePowder's Modbus once
     AMAZEMET agrees.
   - **Precedents:** PyLabRobot (`study:companies/F/pylabrobot.json`) and UR's ROS 2 driver. FOA Topic 11A seeks a
     "cross-cutting software and algorithmic stack" (p. 36).
   - **Keep vendor manuals out of public repos** (ac-dev-lab #532, `study:gh-mining/commercialization_digest.md:104`),
     and host the drivers where they can outlive the lab (`study:README.md`, short answer 3).
5. **Procurement: ask for API rights before buying.** RFQs for the next LPBF (`DAL:alloy-workflow-review.md:75-77`), the
   VLM and every instrument should require:
   - a documented remote interface (REST, OPC UA or Modbus) and the right to publish drivers built on it;
   - process-data export in an open format;
   - permission to publish the interface docs;
   - a retrofit path;
   - offline operation (`#318:notes/security_cameras.md:453`);
   - CAD files or dimensions.

   Add these to the "research partnership terms" DAL already plans (`DAL:alloy-workflow-review.md:302`), and budget
   for driver work (`study:gh-mining/commercialization_digest.md:396`).

## 7. Risks and open questions

- **Licensed outputs.** Can TCAl10 and AM Module results, or values derived from MMPDS, Knovel or ASM, be published
  under CC BY 4.0? DAL's notes don't say. Get the terms in writing before the DMSP is negotiated.
- **IP under the OT agreement.** The terms are set after selection (FOA p. 151; `DAL:genesis-mission-proposal/proposal-checklist.md:414`).
  IP ownership is "a major barrier" (`DAL:genesis-mission-gotchas.md:124`), and funded partners may want rights in
  the compositions.
- **Export control** for AMAZEMET (Poland) and Thermo-Calc (Sweden) is still pending (`proposal-checklist.md:229`).
- **Redistribution gaps:**
  - the `partial_kgfn` notice;
  - samples from unlicensed repos (Mulukutla, AlloyML) or LGPL-3.0 ones (ULTERA);
  - #318's CERN-OHL `.scad` files;
  - vendor manuals, which should be summarized, not reproduced.
- **Vendor lock-in.** Without an AMAZEMET interface, the twin keeps its arm-on-touchscreen design and data capture
  relies on reading the HMI by camera.
- **Hosting.** The American Science Cloud's terms are unknown (`tex:1015-1018`), and the MongoDB records
  (`#318:notes/dal_workflow.md:55`) have no export plan.
- **Open data will feed closed AI,** as the Materials Project fed GNoME (`study:companies/F/materials-project.json`).
  CC BY allows that; the open question is attribution.

## 8. Evidence added after the independent review (2026-11-24)

Later analyses and transcripts bear directly on DAL and #318:

- **Where the lab sits.** Organizations converge toward the middle. Open starters closed 3.3 times per 100
  organization-years, and government, academic and foundation infrastructure almost never closed (1 of 24)
  (`study:data/licence_events_by_start_openness.csv`, `study:data/kinds_corrected.csv`). A university lab that
  publishes under MIT and CERN-OHL-P is in the stable group, so long as its tools don't end up inside a company that
  later needs to close them.
- **The driver layer is the right place to be open.** PyLabRobot's creator describes drivers that "bypass all OEM
  software", mostly reverse-engineered because protocols are undocumented, and says shared drivers have seeded new
  companies. An Uppsala lab left a vendor-installed system because "we also became very dependent on on the vendors to
  solve problems", and built its own on GitHub (`study:voices/voices_digest.md`, Y9 and Y10). Both fit
  recommendation 1 of the playbook (an MCP-style driver per instrument).
- **Plan for the time it costs.** The same Uppsala talk is candid that building takes longer than buying, and suits
  academic labs better than companies. Budget engineering time for the driver layer in the proposal.
- **Licences to avoid.** Adafruit's founder stopped using non-commercial licences because they didn't stop closed
  derivatives (Y13). The Business Source License's own author calls it "not an open source license" (Y8), so it would
  not meet the FOA's open-source expectation. MIT, Apache-2.0 and CERN-OHL-P remain the right defaults.
- **Speed over exclusivity for hardware.** SparkFun's founder reports copies within 12 weeks, and argues that a fast
  release cycle protects a hardware business better than patents (Y7). That supports publishing DAL's fixtures and
  tray stations openly rather than patenting them.
