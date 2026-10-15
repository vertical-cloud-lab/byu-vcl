Question: CONTEXT. We machine powder "cups" as feedstock for a vacuum-induction ultrasonic atomizer
(AMAZEMET rePowder: graphite crucible with a BN wash, chamber pumped down then backfilled with
argon to ~200 mbar, melt at ~800-840 C, pushed through a 0.7 mm nozzle onto a 40 kHz sonotrode),
to make Al-Si powder for laser powder bed fusion (target 15-45 um). Each cup is turned on a
shared university-shop manual lathe from 3/4 in (19.05 mm) 6063 aluminum bar: band-saw cut,
face, center drill, 1/2 in HSS twist drill 2.25 in (57 mm) deep into a blind hole, part off,
2.75 in (70 mm) long. A 6063 plug (12.9 mm dia, 14 mm long, 1 mm vent hole) is turned to a
0.0005-0.0008 in press fit. The cup is filled with 9-14 g of atomized Al-12Si (AA 4047) powder.
About four cups (~200 g total, ~60 cm2 of machined surface per cup incl. the blind bore) are
melted per run. Before filling, cups and plugs are wiped with isopropyl alcohol (IPA) on
Kimwipes and air dried. Lubricant use is not controlled: it may be dry, cutting oil, WD-40,
or a water-soluble coolant, and the lathe is shared with steel and brass work.

QUESTION 2 (how much does an IPA wipe help). How effective is wiping with isopropyl alcohol on
lint-free tissue for removing machining residues from aluminum, compared with acetone, a
hydrocarbon solvent, aqueous alkaline or detergent degreasing, and ultrasonic solvent
cleaning? Use quantitative cleanliness measures where available: residual carbon or
hydrocarbon by gravimetry, XPS, FTIR, optically stimulated electron emission, water-break or
contact angle, particle counts. Specifically:
(a) Solubility of typical cutting oils (mineral oil, esters, EP additives with S/Cl/P),
WD-40, and semi-synthetic coolant residues in IPA versus acetone or heptane; does IPA
redistribute rather than remove oil films? Effect of 70% vs 99% IPA (water content).
(b) Vacuum-component and pre-weld / pre-braze cleaning practice for aluminum (e.g. vacuum
hardware cleaning procedures, AWS D1.2 / brazing guidance, NASA or CERN cleaning
specifications): what do they require, and where does a solvent wipe fall short?
(c) Cleaning blind holes (12.7 mm diameter, 57 mm deep): can a wipe reach the bottom, and
what is recommended (flush, swab, ultrasonic, blow-dry, bake-out)?
(d) Residual IPA or water left in a blind hole before filling with fine Al powder: risks
(hydrogen, hydroxide, powder caking) and recommended drying.
(e) Any data on contamination introduced by handling: fingerprints (Na, Cl, K, lipids),
lint fibers, nitrile glove residue.
Give numbers with citations, and say plainly where the evidence is thin or only indirect.

# Question 2 — How much does an IPA wipe help?

**Bottom line.** An isopropyl-alcohol (IPA) wipe is a useful *preclean* for accessible surfaces and light, soluble contamination. It is not a validated final-cleaning process for these cups: the machining lubricant is uncontrolled, much of the 57-mm blind bore is difficult to wipe reproducibly, and neither dissolved residue nor swarf is reliably carried away without a rinse or flush. Published comparisons show that solvent wiping can improve aluminum wettability, but do **not** establish a percentage of cutting-oil removal for your cups or prove that acetone always outperforms IPA. The strongest relevant process evidence favors controlling machining contamination, flushing the bore, using agitation or an aluminum-compatible detergent where appropriate, rinsing thoroughly, and verifying dryness before adding powder. (dillinghamUnknownyearrapiddevelopmentof pages 3-6, dillinghamUnknownyearrapiddevelopmentof media 40a143a3, liu1994advancedphotonsource pages 53-56, allton2016cleaninggenesissample pages 26-30)

## Comparative evidence and measurement limits

| Evidence | Result | What it does—and does not—establish |
|---|---|---|
| Aluminum coupons of **unknown initial contamination**, measured by water contact angle | Approximate readings from the published figure: as received **70°**, IPA-wiped **57°**, acetone-wiped **51°**, and industrial alkaline-parts-washer cleaned **18°**. The authors say wiping reduced angles by at least about 15° across substrates, found no consistent winner between IPA and acetone, and found no added benefit from a post-washer solvent wipe on aluminum. | A useful *relative wetting* comparison, **not** measured residual oil mass or a test of your 6063 bore and cutting fluids. Values read from the graph are approximate. (dillinghamUnknownyearrapiddevelopmentof pages 3-6, dillinghamUnknownyearrapiddevelopmentof media 40a143a3) |
| Machined aluminum in a **5–8% water–oil machining emulsion** | A roughly **5-s solvent immersion** only partly cleaned the surfaces; **5-min ultrasonic cleaning** removed more fine residue; an agitated alkaline-detergent wash best cleared coarse fragments and grooves. Microscopy/SEM–EDS still found localized carbon-rich material after apparently successful cleaning. | This study tested **denatured ethanol**, **not IPA**, in its separate alcohol treatment, and reports no comparative gravimetric oil mass or XPS carbon percentages. Its ultrasonic bath also contained a formulated cleaner, so the improvement cannot be assigned to ultrasound alone. The cropped aluminum micrographs illustrate this ranking. (fragassa2026experimentalinvestigationof pages 6-7, fragassa2026experimentalinvestigationof pages 9-12, fragassa2026experimentalinvestigationof pages 12-14, fragassa2026experimentalinvestigationof media f5c4640b) |
| NASA Genesis aluminum coupons after a **multistep** clean | XPS surface carbon was **55.46 at%** on a cleaned aluminum array frame and **18.71** and **16.01 at%** on cleaned aluminum shields. XPS sampled roughly the outer **4 nm**; finish and surface texture differed substantially. | Demonstrates that visually/particle-clean aluminum can retain measurable surface carbon. **These are not IPA-wipe-only results**, nor are XPS atomic percentages oil mass or directly comparable removal efficiencies. (allton2016cleaninggenesissample pages 30-34) |
| NASA Genesis aluminum shield rinse verification | After repeated IPA-prewipe, detergent, ultrasonic-water and rinse cycles, rinse total organic carbon was **50 ppb above baseline**; particle cleanliness was reported at **MIL-STD-1246B level 25 or less** for the described shields. | A process-verification result, **not** an IPA-versus-detergent controlled experiment or a specification for atomizer feedstock. (allton2016cleaninggenesissample pages 26-30, allton2016cleaninggenesissample pages 30-34) |

Use measurements for different questions: solvent-extracted **nonvolatile residue (NVR), in µg/cm²**, estimates removable mass; FTIR of the extract helps identify hydrocarbons or silicone; XPS compares the near-surface carbon and potential **S, Cl, P, Na or K** signals; rinse-filtrate particle counts identify swarf. A uniform **water-break** or low water-contact angle screens for hydrophobic films on an accessible test surface, but neither proves a particle-free, dry blind bore. Taborelli describes precision cleaning as below **1 µg/cm²** contamination and estimates XPS carbon detection near **10¹⁴ atoms/cm²**, approximately **3 at%** under the stated assumptions; neither number is an established acceptance limit for your process. OSEE can map a surface rapidly but is chemistry-nonspecific and confounded by oxide and finish, so it would need calibration against your 6063 stock and its machining history. (taborelli2020cleaningandsurface pages 1-3, taborelli2020cleaningandsurface pages 10-12, taborelli2020cleaningandsurface pages 12-13, taborelli2020cleaningandsurface pages 13-16, gause1989anoncontactingscanning pages 20-23)

### (a) Solvent versus actual shop soils

The most direct solubility result is unfavorable to IPA for *mineral-oil base stock*. In a room-temperature screen using **five parts solvent to one part oil by mass**, 2-propanol produced a single phase with low-viscosity **PAO-2**, but **not** with PAO-5 through PAO-150 or the tested **mineral oil**. This is a binary screening result, not a zero-solubility limit or a measure of wiping efficiency: a fresh wipe can still physically pick up some oil. It does, however, explain why an IPA-wetted wipe may **thin or move** an oil film rather than extract it completely. NASA OSEE scans provide an independent *analogy*, not an IPA test: wiping a fingerprint on 7075 aluminum with methyl chloroform **smeared** contamination; further toluene and MEK wipes reduced but did not fully remove it. (davis2019solubilityofhydrocarbon pages 2-4, davis2019solubilityofhydrocarbon pages 2-2, gause1989anoncontactingscanninga pages 43-49, gause1989anoncontactingscanning pages 49-60)

A compatible **aliphatic hydrocarbon solvent such as heptane** is a more chemically plausible first solvent for paraffinic mineral oil or a WD-40-like oily fraction; **acetone** is often useful for grease and many polar organic or ester-containing residues. Neither is a universal replacement: real cutting oils contain differing base stocks and additives, acetone may leave redistributed residues without a clean rinse, and a hydrocarbon solvent will not reliably remove water-soluble coolant salts. Mattox explicitly recommends solvent selection by soil chemistry and describes acetone for heavy grease followed by a cleaner finishing rinse. The retrieved studies **do not quantify IPA-versus-acetone-versus-heptane solubility for your specific cutting oil, WD-40 formulation, or S/Cl/P extreme-pressure additives**; the proposed solvent choices are chemical reasoning and should be checked against the actual product/SDS and a recovery test. Do not assume an S-, Cl- or P-containing additive has gone simply because its carrier oil or solvent has evaporated. (mattox1998preparationandcleaning pages 17-20, taborelli2020cleaningandsurface pages 1-3, davis2019solubilityofhydrocarbon pages 2-4)

**Semi-synthetic or water-soluble coolant is a different problem.** Its residual mixture can include oil, surfactants and water-soluble components. An IPA wipe is not a demonstrated way of removing all of them; an appropriate aluminum-compatible aqueous cleaner can suspend oily soils, but its own surfactants must then be rinsed away. CERN’s vacuum-cleaning review explicitly warns that trapped rinse water or cleaner residues can produce persistent outgassing or corrosion. **99% reagent-grade IPA** is preferable to **70% IPA** when the purpose is a low-water final solvent rinse: by formulation, the latter brings roughly 30% water into the blind bore. That is a water-loading distinction, **not** evidence that 99% IPA removes mineral oil effectively or that either formulation is residue-free after wiping. No controlled 70%-versus-99% removal or drying result for these cups was found. (taborelli2020cleaningandsurface pages 3-5, taborelli2020cleaningandsurface pages 5-8, davis2019solubilityofhydrocarbon pages 2-4)

### (b) What vacuum-component practice actually requires

The closest material-specific procedure is Argonne’s **6063-aluminum ultrahigh-vacuum** recipe: pre-spray with **2% Almeco 18**, ultrasonically clean in **2% Almeco 18 at 65°C for 10 min**, rinse in **flowing deionized water for 10 min**, then blow dry with **hot, dry nitrogen**. Its broader guidance lists gross contaminant removal, degreasing, ultrasonic non-etch detergent cleaning, DI rinsing and oven drying; it treats an alcohol swab as an *initial* contaminant-removal option, not as equivalent to that sequence. It also requires clean tools/handling and specifies that any blow-off gas be dry, oil-free and filtered. **This is a demonstrated vacuum-component practice, not an automatically validated recipe for powder-filled cups:** aluminum/alloy, detergent, dwell and thorough bore drying must be qualified locally. (liu1994advancedphotonsource pages 53-56, liu1994advancedphotonsource pages 56-60)

NASA Genesis likewise used an **IPA wipe as precleaning**, followed on aluminum by repeated **20% Brulin 815 GD scrubbing/rinsing**, a **30-min, 30°C** ultrapure-water cascade, final rinse and nitrogen drying. Its investigators also observed hydroxide/oxide formation, pitting and increased trapping area on bare aluminum, especially under more aggressive water conditions: stronger or hotter aqueous cleaning is **not unconditionally better**. A CERN vacuum-surface review similarly describes solvent precleaning for heavy grease, detergent plus ultrasonic agitation, substantial rinsing and controlled drying, while cautioning that pocketed water can make a solvent-based route more appropriate for difficult geometries. I could not verify the text of an **AWS D1.2** clause or an aluminum **vacuum-brazing specification** in the retrieved material; these procedures should **not** be represented as requirements imposed by either standard. Pre-weld cleanliness and the hydrogen mechanism are relevant analogies, not certification of an atomization process. (allton2016cleaninggenesissample pages 20-23, taborelli2020cleaningandsurface pages 5-8, legait2006formationanddistribution pages 21-27)

### (c) The 12.7-mm × 57-mm blind bore

A Kimwipe applied at the mouth cannot be presumed to touch or scrub the **bottom, drill-point recess and full bore circumference**. A deliberately chosen, solvent-compatible **long swab** can reach the bottom, but that changes the present operation: it must be visibly inspected for fibers and followed by a means of *carrying material out*, rather than repeatedly pushing contaminated liquid down the bore. For an appropriate solvent or validated aqueous process, flush or jet **into the bottom and out of the open mouth**, collect the effluent, repeat with fresh fluid, and inspect the base; immersion ultrasound can help dislodge contaminants in blind holes but does not itself guarantee evacuation or drying. CERN explicitly identifies ultrasonic access to blind holes. NASA’s much more demanding blind-hole procedure jetted **each hole**, ultrasonicated in **15-min on/off stages**, rinsed, nitrogen-blew, oven-dried, inserted a **heated filtered-nitrogen probe into each hole**, and **verified each hole with a moisture probe**. Those steps illustrate the failure mode of treating an external wipe or a dry-looking mouth as proof that a hole is clean and dry. (taborelli2020cleaningandsurface pages 5-8, allton2016cleaninggenesissample pages 26-30)

### (d) Liquid left before filling with Al–Si powder

Do **not** put powder onto a bore that might retain liquid IPA, aqueous rinse or coolant. Residual solvent can wet and agglomerate fine feedstock and evolve gas on pump-down or heating; water also promotes aluminum surface hydration. Moisture in aluminum melting is a potential hydrogen source: the reaction **2Al + 3H₂O → Al₂O₃ + 3H₂** expresses the *maximum chemical potential*, not the amount necessarily absorbed into a given melt. Hydrogen uptake and porosity depend on oxide integrity and melt conditions; no hydrogen pickup per microlitre of trapped cup liquid was established here. In an AlSi10Mg powder experiment, exposure at **50°C/80% RH for 72 h** raised measured moisture to about **0.437 wt%** and impaired powder behavior; that deliberately severe exposure is **not** a prediction for a promptly dried 4047 charge. Other AlSi10Mg results found moisture difficult to remove once taken up, reinforcing **dry the empty cup before filling**, not “let the filled cup air-dry.” (legait2006formationanddistribution pages 21-27, cordova2020measuringthespreadability pages 5-6, cordova2020measuringthespreadability pages 10-11)

After the last flush, **invert and drain**, direct **filtered, oil-free dry nitrogen to the bottom**, and, if validated for the part and cleaning chemistry, dry the **empty** cup in a clean warm oven or under controlled vacuum until the bore is dry; cool and store protected from moisture before filling. Confirm drying by a bore-directed check and, where feasible, repeat weighing to constant mass or monitoring the drying exhaust. **No universal temperature, duration, or constant-mass tolerance for this geometry was located.** A bake can remove volatile liquid but must **not** be used as a substitute for removing residual cutting oil or detergent first; indiscriminate heating risks fixing nonvolatile soil in place. (allton2016cleaninggenesissample pages 26-30, liu1994advancedphotonsource pages 56-60, taborelli2020cleaningandsurface pages 5-8)

### (e) What handling can add

Natural latent fingerprints on a nonporous surface were reported at **0.33–29.00 µg per print**, mean **7.40 µg** across **55** marks; the range is large and is **not** an expected deposit for every machinist’s touch. Fingerprints carry lipids plus soluble **Na, Cl and K**; XPS/FTIR/SIMS investigations detect those constituents, but do not provide a defensible universal elemental mass per touch on these cups. An aluminum OSEE experiment shows that solvent wiping a fingerprint can leave a wider, still-detectable residue. (bleay2021theforensicexploitation pages 2-4, bailey2012chemicalcharacterizationof pages 5-6, gause1989anoncontactingscanninga pages 43-49)

Gloves and wipes are not automatically clean. In a NASA glove-screening study, all tested glove types transferred **under 3 µg/cm²** under an *extreme* standardized dry-contact test; several were below **0.5 µg/cm²**. Solvent extraction could release much more: one tested nitrile glove yielded **234 µg/cm² in acetone**, versus **180–210 µg/cm²** for the compared latex gloves. Extraction is **not** the amount transferred by ordinary gloved handling, but shows why solvent-soaked gloves should not contact clean bores. Select and qualify clean, powder-free gloves, change them after touching the lathe or other dirty surfaces, and verify the blank NVR/particles from the chosen low-lint wipe or swab. I found **no reliable fiber count or nitrile-additive mass transferred to these particular cups**; “lint-free” does not demonstrate zero fibers. (sovinski2004contaminationofcritical pages 8-9, sovinski2004contaminationofcritical pages 11-17, liu1994advancedphotonsource pages 56-60)

## Proportionate shop decision

**Keep the IPA wipe, but downgrade its claim:** it removes some accessible light contamination and can improve contact angle; it does **not** demonstrate removal of mineral cutting oil, coolant additives, embedded mixed-metal debris or residue at the bottom of the bore. The highest-value change is to **standardize the machining lubricant and isolate/clean the tooling**, then qualify a **bore-flush → appropriate solvent or aluminum-compatible detergent/ultrasonic clean → fresh rinse → verified dry** process on sacrificial cups. Compare that process against current practice with **blank-corrected solvent-extracted NVR and FTIR**, bore-effluent particle counts, and—if important for powder chemistry—XPS on representative cut-open bores. A water-break/contact-angle result on the accessible face is a useful supplementary screen, not a release test for the blind hole. None of the cited studies measures final atomized **15–45 µm powder yield, composition or hydrogen** under your rePowder settings, so any asserted numeric improvement in those outcomes would be speculative. (davis2019solubilityofhydrocarbon pages 2-4, liu1994advancedphotonsource pages 53-56, allton2016cleaninggenesissample pages 26-30, dillinghamUnknownyearrapiddevelopmentof pages 3-6, taborelli2020cleaningandsurface pages 10-12)

References

1. (dillinghamUnknownyearrapiddevelopmentof pages 3-6): RG Dillingham. Rapid development of surface treatment processes for bonding dissimilar materials. Unknown journal, Unknown year.

2. (dillinghamUnknownyearrapiddevelopmentof media 40a143a3): RG Dillingham. Rapid development of surface treatment processes for bonding dissimilar materials. Unknown journal, Unknown year.

3. (liu1994advancedphotonsource pages 53-56): C Liu and J Noonan. Advanced Photon Source accelerator ultrahigh vacuum guide. Office of Scientific and Technical Information (OSTI), Mar 1994. URL: https://doi.org/10.2172/10150835, doi:10.2172/10150835.

4. (allton2016cleaninggenesissample pages 26-30): JH Allton, JD Hittle, ET Mickelson, and EK Stansbery. Cleaning genesis sample return canister for flight: lessons for planetary sample return. Unknown journal, 2016.

5. (fragassa2026experimentalinvestigationof pages 6-7): Cristiano Fragassa, Jacopo Vetricini, Mattia Latini, Mattia Merlin, and Carlo Santulli. Experimental investigation of surface contamination removal in machined metals using multi-technique characterization. Metals, 16:485, Apr 2026. URL: https://doi.org/10.3390/met16050485, doi:10.3390/met16050485. This article has 2 citations.

6. (fragassa2026experimentalinvestigationof pages 9-12): Cristiano Fragassa, Jacopo Vetricini, Mattia Latini, Mattia Merlin, and Carlo Santulli. Experimental investigation of surface contamination removal in machined metals using multi-technique characterization. Metals, 16:485, Apr 2026. URL: https://doi.org/10.3390/met16050485, doi:10.3390/met16050485. This article has 2 citations.

7. (fragassa2026experimentalinvestigationof pages 12-14): Cristiano Fragassa, Jacopo Vetricini, Mattia Latini, Mattia Merlin, and Carlo Santulli. Experimental investigation of surface contamination removal in machined metals using multi-technique characterization. Metals, 16:485, Apr 2026. URL: https://doi.org/10.3390/met16050485, doi:10.3390/met16050485. This article has 2 citations.

8. (fragassa2026experimentalinvestigationof media f5c4640b): Cristiano Fragassa, Jacopo Vetricini, Mattia Latini, Mattia Merlin, and Carlo Santulli. Experimental investigation of surface contamination removal in machined metals using multi-technique characterization. Metals, 16:485, Apr 2026. URL: https://doi.org/10.3390/met16050485, doi:10.3390/met16050485. This article has 2 citations.

9. (allton2016cleaninggenesissample pages 30-34): JH Allton, JD Hittle, ET Mickelson, and EK Stansbery. Cleaning genesis sample return canister for flight: lessons for planetary sample return. Unknown journal, 2016.

10. (taborelli2020cleaningandsurface pages 1-3): Mauro Taborelli. Cleaning and surface properties. Preprint, Jan 2020. URL: https://doi.org/10.48550/arxiv.2006.01585, doi:10.48550/arxiv.2006.01585. This article has 48 citations.

11. (taborelli2020cleaningandsurface pages 10-12): Mauro Taborelli. Cleaning and surface properties. Preprint, Jan 2020. URL: https://doi.org/10.48550/arxiv.2006.01585, doi:10.48550/arxiv.2006.01585. This article has 48 citations.

12. (taborelli2020cleaningandsurface pages 12-13): Mauro Taborelli. Cleaning and surface properties. Preprint, Jan 2020. URL: https://doi.org/10.48550/arxiv.2006.01585, doi:10.48550/arxiv.2006.01585. This article has 48 citations.

13. (taborelli2020cleaningandsurface pages 13-16): Mauro Taborelli. Cleaning and surface properties. Preprint, Jan 2020. URL: https://doi.org/10.48550/arxiv.2006.01585, doi:10.48550/arxiv.2006.01585. This article has 48 citations.

14. (gause1989anoncontactingscanning pages 20-23): RL Gause. A noncontacting scanning photoelectron emission technique for bonding surface cleanliness inspection. Unknown journal, 1989.

15. (davis2019solubilityofhydrocarbon pages 2-4): Matthew C. Davis, Patrick W. Fedick, David V. Lupton, Gregory S. Ostrom, Roxanne Quintana, and Josanne-Dee Woodroffe. Solubility of hydrocarbon oils in alcohols (≤c6) and synthesis of difusel carbonate for degreasing. RSC Advances, 9:22891-22899, Jul 2019. URL: https://doi.org/10.1039/c9ra04220b, doi:10.1039/c9ra04220b. This article has 12 citations and is from a peer-reviewed journal.

16. (davis2019solubilityofhydrocarbon pages 2-2): Matthew C. Davis, Patrick W. Fedick, David V. Lupton, Gregory S. Ostrom, Roxanne Quintana, and Josanne-Dee Woodroffe. Solubility of hydrocarbon oils in alcohols (≤c6) and synthesis of difusel carbonate for degreasing. RSC Advances, 9:22891-22899, Jul 2019. URL: https://doi.org/10.1039/c9ra04220b, doi:10.1039/c9ra04220b. This article has 12 citations and is from a peer-reviewed journal.

17. (gause1989anoncontactingscanninga pages 43-49): RL Gause. A noncontacting scanning photoelectron emission technique for bonding surface cleanliness inspection. Unknown journal, 1989.

18. (gause1989anoncontactingscanning pages 49-60): RL Gause. A noncontacting scanning photoelectron emission technique for bonding surface cleanliness inspection. Unknown journal, 1989.

19. (mattox1998preparationandcleaning pages 17-20): Donald M. Mattox. Preparation and cleaning of vacuum surfaces. ArXiv, pages 553-606, Jan 1998. URL: https://doi.org/10.1016/b978-012352065-4/50070-5, doi:10.1016/b978-012352065-4/50070-5. This article has 2 citations.

20. (taborelli2020cleaningandsurface pages 3-5): Mauro Taborelli. Cleaning and surface properties. Preprint, Jan 2020. URL: https://doi.org/10.48550/arxiv.2006.01585, doi:10.48550/arxiv.2006.01585. This article has 48 citations.

21. (taborelli2020cleaningandsurface pages 5-8): Mauro Taborelli. Cleaning and surface properties. Preprint, Jan 2020. URL: https://doi.org/10.48550/arxiv.2006.01585, doi:10.48550/arxiv.2006.01585. This article has 48 citations.

22. (liu1994advancedphotonsource pages 56-60): C Liu and J Noonan. Advanced Photon Source accelerator ultrahigh vacuum guide. Office of Scientific and Technical Information (OSTI), Mar 1994. URL: https://doi.org/10.2172/10150835, doi:10.2172/10150835.

23. (allton2016cleaninggenesissample pages 20-23): JH Allton, JD Hittle, ET Mickelson, and EK Stansbery. Cleaning genesis sample return canister for flight: lessons for planetary sample return. Unknown journal, 2016.

24. (legait2006formationanddistribution pages 21-27): PA Legait. Formation and distribution of porosity in al-si welds. Unknown journal, 2006.

25. (cordova2020measuringthespreadability pages 5-6): Laura Cordova, Ton Bor, Marc de Smit, Mónica Campos, and Tiedo Tinga. Measuring the spreadability of pre-treated and moisturized powders for laser powder bed fusion. Additive Manufacturing, 32:101082, Mar 2020. URL: https://doi.org/10.1016/j.addma.2020.101082, doi:10.1016/j.addma.2020.101082. This article has 175 citations and is from a highest quality peer-reviewed journal.

26. (cordova2020measuringthespreadability pages 10-11): Laura Cordova, Ton Bor, Marc de Smit, Mónica Campos, and Tiedo Tinga. Measuring the spreadability of pre-treated and moisturized powders for laser powder bed fusion. Additive Manufacturing, 32:101082, Mar 2020. URL: https://doi.org/10.1016/j.addma.2020.101082, doi:10.1016/j.addma.2020.101082. This article has 175 citations and is from a highest quality peer-reviewed journal.

27. (bleay2021theforensicexploitation pages 2-4): Stephen M. Bleay, Melanie J. Bailey, Ruth S. Croxton, and Simona Francese. The forensic exploitation of fingermark chemistry: a review. ArXiv, Oct 2021. URL: https://doi.org/10.1002/wfs2.1403, doi:10.1002/wfs2.1403. This article has 77 citations.

28. (bailey2012chemicalcharacterizationof pages 5-6): Melanie. J. Bailey, Nicholas J. Bright, Ruth S. Croxton, Simona Francese, Leesa S. Ferguson, Stephen Hinder, Sue Jickells, Benjamin J. Jones, Brian N. Jones, Sergei G. Kazarian, Jesus J. Ojeda, Roger P. Webb, Rosalind Wolstenholme, and Stephen Bleay. Chemical characterization of latent fingerprints by matrix-assisted laser desorption ionization, time-of-flight secondary ion mass spectrometry, mega electron volt secondary mass spectrometry, gas chromatography/mass spectrometry, x-ray photoelectron spectroscopy, and attenuated total reflection fou. Analytical chemistry, 84 20:8514-23, Sep 2012. URL: https://doi.org/10.1021/ac302441y, doi:10.1021/ac302441y. This article has 137 citations and is from a highest quality peer-reviewed journal.

29. (sovinski2004contaminationofcritical pages 8-9): MF Sovinski. Contamination of critical surfaces from nvr glove residues via dry handling and solvent cleaning. Unknown journal, 2004.

30. (sovinski2004contaminationofcritical pages 11-17): MF Sovinski. Contamination of critical surfaces from nvr glove residues via dry handling and solvent cleaning. Unknown journal, 2004.