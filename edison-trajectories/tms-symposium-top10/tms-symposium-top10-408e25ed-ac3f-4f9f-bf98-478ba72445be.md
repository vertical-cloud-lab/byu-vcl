I swept all 108 symposium records in `tms2027-symposia.json`/`tms2027-symposia-full-text.md`, using the full scope text rather than titles only. I scored every scope for SDL-relevant terms (closed-loop, Bayesian optimization, autonomous/robotic/high-throughput workflows, open instrumentation, provenance, aqueous chemistry, pH, leaching, precipitation, hydrometallurgy, in situ monitoring), then manually inspected the high-scoring and hidden-gem cases. Organizer notes are based on public web pages/search results available during this run, so treat them as evidence of likely receptiveness, not a guarantee of programming decisions.

## Ranked top 10

### 1. AI-Enabled Materials Processing: Integrating Accelerated Experimental Workflows and Processing-Aware Machine Learning

- **Sponsorship:** TMS Materials Processing and Manufacturing Division; Additive Manufacturing Committee; Computational Materials Science and Engineering Committee; Process Technology and Modeling Committee
- **Fit score as written:** **9.5/10**
- **Hidden gem?** **No.** This is the most obvious SDL home.
- **Why it fits:** This scope almost names the abstract. It calls for AI and ML “directly with experimental materials processing,” “high-throughput manufacturing,” “real-time process monitoring,” “experimental processing workflows,” “Bayesian optimization for process tuning,” and “closed-loop experimental workflows that integrate synthesis, processing, characterization, testing, and iterative model-guided refinement.” CubXL is a systems/platform talk, but the scope explicitly welcomes experimental and hybrid work at the interface of processing and data-driven optimization.
- **Organizer-background notes:** Strong receptiveness signal. Maitreyee Sharma Priyadarshini’s public profile lists “Bayesian Optimization” and “automated materials and chemistry workflows”; a public RSC result identifies her as an author on PAL 2.0, a physics-driven Bayesian optimization framework. Sreenivas Raguraman and Timothy Weihs are connected to Johns Hopkins materials processing; public search also surfaced the Johns Hopkins AIMD-L automated laboratory paper/result in the same organizer ecosystem. Thomas Voisin, Allison Beese, and Samantha Webster reinforce the processing/manufacturing angle.
- **Reframing/edit:** Keep the abstract mostly intact, but replace one sentence with a processing-centric hook: “The platform targets closed-loop optimization of aqueous processing variables, including reagent addition, powder-to-liquid ratio, pH, dissolution time, and precipitation conditions.” This fits within 150 words if you trim the pH-probe storage detail.

### 2. AI/ML/Data Informatics for Materials Discovery: Bridging Experiment, Theory, and Modeling

- **Sponsorship:** TMS Materials Processing and Manufacturing Division; TMS Structural Materials Division; Computational Materials Science and Engineering Committee; Mechanical Behavior of Materials Committee
- **Fit score as written:** **8.8/10**
- **Hidden gem?** **No.** Obvious from title, but still stronger than many title-only AI sessions because the scope emphasizes data infrastructure and experimental workflows.
- **Why it fits:** The scope emphasizes “connecting experiment, theory, and modeling in the modern materials research workflow,” “generation, extraction, curation, management, and effective use of high-quality materials data,” “FAIR data principles, metadata frameworks, provenance, and interoperable infrastructure,” and “case studies that connect laboratory practice, computational experimentation, and AI-assisted materials development.” CubOS provenance, YAML protocols, offline validation, and a local experiment database are unusually aligned with this data-infrastructure framing.
- **Organizer-background notes:** Strong-to-very-strong receptiveness. James Saal is at Citrine Informatics; Taylor Sparks is widely associated with materials informatics; Kamal Choudhary and Daniel Wines are NIST/JHU data-oriented materials researchers; public JHU APL material-discovery coverage quotes Christopher Stiles on AI-driven materials discovery. This committee is likely to value the software/provenance part of CubOS, not just the gantry hardware.
- **Reframing/edit:** Emphasize data provenance and reproducible automation: “CubOS records machine-readable protocols, validation results, sensor streams, and experiment outcomes for AI-ready materials datasets.” This can fit within 150 words by shortening the module list.

### 3. Artificial Intelligence Applications in Integrated Computational Materials Engineering (AI-ICME)

- **Sponsorship:** TMS Materials Processing and Manufacturing Division; Computational Materials Science and Engineering Committee; Integrated Computational Materials Engineering Committee; Process Technology and Modeling Committee
- **Fit score as written:** **8.4/10**
- **Hidden gem?** **No.** Title clearly suggests AI/ML, but the scope has unusually good SDL language.
- **Why it fits:** The scope explicitly lists “active learning and Bayesian optimization,” “autonomous/closed-loop experimentation for accelerated discovery and processing optimization,” “data curation, standards, provenance/traceability,” and “reproducible machine learning operations pipelines.” CubXL’s local experiment database and version-controlled protocols map directly onto provenance/traceability and reproducible closed-loop experimentation.
- **Organizer-background notes:** Strong receptiveness to AI infrastructure. Brandon Bocklund is publicly associated with `pycalphad`, described as a free/open-source CALPHAD Python library, and ESPEI. Ghanshyam Pilania’s public profile lists “machine learning & high throughput screening of functional materials.” Wenwu Xu’s SDSU lab page lists materials informatics and machine learning. This is a good audience if the abstract is framed as infrastructure enabling ICME-compatible experimental data.
- **Reframing/edit:** Add an ICME phrase: “The platform produces traceable, machine-readable processing histories for closed-loop ICME workflows.” Fits within 150 words if you compress “current capabilities and limitations.”

### 4. Functional Nanomaterials 2027

- **Sponsorship:** TMS Functional Materials Division; Nanomaterials Committee
- **Fit score as written:** **8.0/10**
- **Hidden gem?** **Yes.** The title sounds like nanomaterial property talks, but the scope explicitly invites autonomy.
- **Why it fits:** The scope says the symposium focuses on nanomaterial design “advanced by the use of AI and autonomy,” with focused sessions on “design/manufacturing/characterization strategies of nanomaterials aided by AI and autonomous experiments” and a topic area of “Data-Driven and Autonomous Discovery in Nanomaterials.” CubXL’s aqueous precipitation, dissolution, and pH-control workflows could be framed as modular wet-chemistry routes to nanomaterial synthesis and screening.
- **Organizer-background notes:** Moderate-to-strong receptiveness. Mostafa Bedewy’s public research presence is linked to nanomanufacturing and data/automation-adjacent work; Keerti Kappagantula and Aditya Nittala at PNNL give a national-lab advanced-manufacturing flavor. The catch: the abstract as written does not say “nanomaterials,” so organizer enthusiasm will depend on reframing toward nanoparticle/precipitation synthesis rather than platform generality alone.
- **Reframing/edit:** Highest-value edit: change examples to “pH-controlled precipitation and dissolution studies relevant to nanomaterial synthesis and stability.” This fits within 150 words. Do not overclaim nanomaterial results if you do not have them.

### 5. Novel Strategies for Rapid Acquisition and Processing of Large Datasets From Advanced Characterization Techniques

- **Sponsorship:** TMS Structural Materials Division; Advanced Characterization, Testing, and Simulation Committee
- **Fit score as written:** **7.8/10**
- **Hidden gem?** **Yes.** The title looks like microscopy/data processing, but the full scope explicitly invites autonomous experiments and feedback workflows.
- **Why it fits:** The scope says “recent developments in high-throughput and autonomous experimental approaches combined with advances in instrumentation” create data-curation challenges, and it calls for “machine learning and AI guided real-time or post facto reduction,” “FAIR data principles,” and “workflows for on-the-fly data extraction and feedback.” CubXL’s camera monitoring, pH measurements, and experiment database are less advanced-characterization-heavy than the listed OM/SEM/TEM/APT/XCT examples, but the systems/data-acquisition angle fits.
- **Organizer-background notes:** Moderate receptiveness. Public pages show Sriram Vijayan works in materials characterization; Rakesh Kamath is associated publicly with advanced manufacturing and synchrotron/neutron characterization; Fan Zhang at NIST specializes in multiscale materials characterization. They may like real-time instrumentation and metadata handling, but will expect the talk to foreground sensing/data acquisition rather than hardware modularity alone.
- **Reframing/edit:** Emphasize “inline sensing streams and image-derived observations as FAIR, feedback-ready datasets.” Fits within 150 words if the module list is shortened.

### 6. From Mine to Refinery: An EPD Symposium Honoring Shijie Wang

- **Sponsorship:** TMS Extraction and Processing Division; Hydrometallurgy and Electrometallurgy Committee; Pyrometallurgy Committee
- **Fit score as written:** **7.6/10**
- **Hidden gem?** **Yes.** The title would not surface an SDL platform, but the full scope is very compatible with the leaching/pH side of CubXL.
- **Why it fits:** The scope welcomes “hydrometallurgical, electrochemical, and chemical processes,” and specifically “leaching behavior, solution chemistry, reagent optimization, kinetic and thermodynamic modeling,” including “the potential use of AI.” Your abstract already names leaching, pH, powder dosing into liquids, sealed vials, and Bayesian optimization, which are directly relevant to small-scale hydrometallurgical screening.
- **Organizer-background notes:** Strong hydrometallurgy receptiveness, weaker SDL-specific signal. Michael Free’s University of Utah research page explicitly mentions column leaching tests where recovery is tracked and flow rates/parameters “such as pH are monitored and controlled by automated equipment.” Michael Moats is publicly listed with hydrometallurgy/electrorefining/electrowinning interests. Corby Anderson and Ramana Reddy are extraction/metallurgy leaders. This audience will value the leaching workflow if you make it concrete.
- **Reframing/edit:** For highest acceptance likelihood here, make the abstract hydrometallurgy-forward: “We target closed-loop leaching and solution-chemistry campaigns for critical-material extraction, using automated powder addition, liquid handling, sealed-vial aging, and inline pH tracking.” This fits within 150 words by dropping the solubility/precipitation examples or moving them after leaching.

### 7. Rare Metal Extraction & Processing

- **Sponsorship:** TMS Extraction and Processing Division; Hydrometallurgy and Electrometallurgy Committee
- **Fit score as written:** **7.2/10**
- **Hidden gem?** **Yes.** The title suggests extraction metallurgy, not autonomous labs, but the scope fits the aqueous leaching module set.
- **Why it fits:** The scope covers “extraction of critical minerals,” “processing and refining studies… spanning laboratory, pilot-scale, and industrial applications,” “unconventional feedstocks,” “recycling of critical elements,” and “novel processes such as biomimicking leaching and separation.” CubXL is well suited to small-scale, replicated, pH-tracked leaching and separation-reagent screening, but the current abstract should say “rare/critical metals” more directly.
- **Organizer-background notes:** Strong domain receptiveness. Public pages identify Gisele Azimi as working in electrochemistry, thermodynamics, hydrometallurgy, advanced recycling, and urban mining; Kerstin Forsberg’s KTH profile highlights crystallization and resource recovery; Shafiq Alam is publicly associated with hydrometallurgy/leaching; Michael Dziekan, Jaeheon Lee, and others are in critical-material extraction ecosystems. They may not prioritize open hardware unless tied to better extraction datasets.
- **Reframing/edit:** Replace generic “leaching studies” with “rare/critical-metal leaching and reagent-optimization studies from powders, residues, or recycled feedstocks.” Fits within 150 words with minor trimming.

### 8. Next Generation Electrometallurgical Technologies for Metal Extraction, Refining, and Recycling

- **Sponsorship:** TMS Extraction and Processing Division; Hydrometallurgy and Electrometallurgy Committee
- **Fit score as written:** **6.8/10**
- **Hidden gem?** **Yes.** The title is electrochemical/extraction-focused, but the scope has relevant platform language.
- **Why it fits:** The scope encourages “closed-loop system design,” “process control,” “modularization,” and scaling “from laboratory experiments to pilot facilities,” with emphasis on extraction, refining, recycling, electrolyte stability, and recovery from e-waste, batteries, and magnet scrap. CubXL is not an electrometallurgical reactor as written, but it can prepare, age, monitor, and screen electrolyte/leachate chemistries feeding such workflows.
- **Organizer-background notes:** Moderate domain fit. Public results associate Samira Sokhanvaran with Hatch and electrometallurgy/sustainable metal production; Takanari Ouchi’s public profile lists resource recycling, nonferrous metallurgy, and electrochemistry. Receptiveness likely depends on whether you frame CubXL as upstream electrolyte/leachate screening or as modular sample preparation for electrochemical extraction campaigns.
- **Reframing/edit:** Add “electrolyte and leachate screening” rather than only “aqueous materials chemistry.” This can fit within 150 words if you remove one implementation detail.

### 9. Circular Metallurgy: Design, Technology, Application

- **Sponsorship:** TMS Functional Materials Division; TMS Structural Materials Division; Alloy Phases Committee
- **Fit score as written:** **6.7/10**
- **Hidden gem?** **Yes.** The full scope, not the title, reveals a direct automation opening.
- **Why it fits:** The scope includes “AI-enhanced recovery networks,” “AI and machine learning approaches for sustainable materials discovery and process optimization,” and, most directly, “Scale up circularity through lab automation, robotics, process optimization and AI/ML.” CubXL’s sealed-vial leaching, pH tracking, and powder/liquid handling can be positioned as a low-cost robotic screening platform for recycling and recovery chemistry.
- **Organizer-background notes:** Good AI/materials-design signal. Bin Ouyang appears in public searches around closed-loop materials synthesis/design and data-driven materials; Song-Mao Liang, Alan Luo, John Perepezko, Pascal Gauthier, and Wei Xiong give the symposium strong alloy/circularity/process credibility. The mismatch is that CubXL is not yet a circular-metallurgy result unless the abstract foregrounds recycling/leaching use cases.
- **Reframing/edit:** “We demonstrate a replicable benchtop route for robotic screening of circular-metallurgy solution chemistries, including leaching, pH adjustment, and precipitation.” Fits within 150 words if the pH-probe storage sentence is removed.

### 10. Mechanistic and Experimental Thermodynamics & Kinetics of Alloys

- **Sponsorship:** TMS Functional Materials Division; TMS Structural Materials Division; Alloy Phases Committee
- **Fit score as written:** **6.4/10**
- **Hidden gem?** **Yes.** The title sounds like traditional alloy thermodynamics, but the scope explicitly calls for automated and closed-loop workflows.
- **Why it fits:** The scope includes “high-quality experimental measurements,” “advanced experimental techniques,” “high-throughput experimental techniques,” and a specific topic of “Data-driven strategies for rapid alloy discovery and optimization, including high-throughput experimentation, automated synthesis and characterization, and AI/ML-assisted workflows,” plus “adaptive and closed-loop frameworks.” The problem is domain mismatch: CubXL is aqueous/materials-chemistry-focused, not alloy synthesis or thermodynamics.
- **Organizer-background notes:** Mixed but credible. Ji-Cheng Zhao is publicly associated with high-throughput experimental tools for the Materials Genome Initiative; Chuan Zhang/CompuTherm and Bin Ouyang/Vanderbilt indicate strong CALPHAD/data-driven alloy design interest. They may welcome automation methodology, but only if you connect it to quantitative thermodynamic/kinetic measurements or alloy-relevant solution processing.
- **Reframing/edit:** This would require the most reframing: emphasize “automated measurement of dissolution/precipitation kinetics and solution equilibria as high-quality inputs to thermodynamic models.” It can fit within 150 words, but acceptance risk remains higher than ranks 1 to 9.

## Important near-miss

**Hume-Rothery Symposium: Data-Driven Materials Discovery and Phase Stability** has excellent scope language, including “Autonomous and closed-loop materials discovery frameworks,” plus organizers such as James Saal and Bin Ouyang. However, the provided scope says: **“This symposium only accepts invited abstracts.”** I would not use it as a contributed-abstract target unless you have an invitation.

## Bottom line

Submit first to **AI-Enabled Materials Processing: Integrating Accelerated Experimental Workflows and Processing-Aware Machine Learning**. It has the best combination of exact scope language, organizer receptiveness to Bayesian optimization/automated workflows, and tolerance for a systems-focused SDL talk.

Use these as backups:

1. **AI/ML/Data Informatics for Materials Discovery: Bridging Experiment, Theory, and Modeling** if you want to emphasize CubOS, provenance, protocol validation, FAIR-ish data capture, and reproducible experimental infrastructure.
2. **From Mine to Refinery: An EPD Symposium Honoring Shijie Wang** if you want the highest acceptance likelihood from an application-driven reframing: hydrometallurgical leaching, pH-controlled solution chemistry, reagent optimization, and powder/liquid screening.

If you are willing to reframe, the strongest acceptance-oriented edit for a systems-focused SDL talk is **hydrometallurgy/leaching-forward but still platform-centered**: present CubXL as a low-cost, open-source robotic platform for closed-loop screening of aqueous leaching, pH adjustment, dissolution, and precipitation workflows. That keeps the system emphasis while making the application concrete for TMS.

## Discretionary decisions

- Used a weighted full-text keyword screen across all 108 symposia to avoid title-only shortlisting, then manually reviewed high-scoring and hidden-gem candidates.
- Weighted autonomous experimentation, Bayesian optimization, closed-loop workflows, high-throughput workflows, aqueous chemistry, pH, leaching, hydrometallurgy, provenance, and instrumentation terms more heavily than broad “AI” or generic “processing” terms.
- Ranked by combined scope fit and organizer receptiveness, not by keyword score alone.
- Treated “fit score” as an expert judgment for the abstract as written, on a 0 to 10 scale, rather than a statistical estimate.
- Marked “hidden gem” when the title alone would probably not lead a reasonable submitter to shortlist the symposium for an SDL/open-hardware platform talk.
- Excluded the Hume-Rothery symposium from the ranked top 10 despite good topical fit because the scope states that it accepts invited abstracts only.
- Recommended reframing within the 150-word limit by trimming implementation details, especially the pH-probe wet-storage sentence, rather than expanding the abstract.