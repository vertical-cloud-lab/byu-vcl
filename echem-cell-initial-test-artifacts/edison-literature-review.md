Question: I am setting up a first low-hazard test of a 3D-printed Formlabs Clear v5 electrochemical cell with a borrowed potentiostat. The plan is a textbook ferricyanide/ferrocyanide CV in 0.1 M KCl on a 3 mm glassy carbon working electrode, Pt counter, Ag/AgCl reference.

Please critically review the following for any factual errors, safety oversights, or better/cheaper sourcing:

1. Probe chemistry: 1-5 mM K3[Fe(CN)6] in 0.1 M KCl, E0' ~ +0.23 V vs Ag/AgCl (3 M KCl), expected ip ~10-30 uA at 50 mV/s on 3 mm GC. Reversible one-electron outer-sphere couple. Diagnostic for iR drop, contamination, leaky joints.

2. Safety: Main rule is never acidify ferri/ferrocyanide (HCN risk). Otherwise low hazard at mM scale, mL volumes, aqueous cyanide-complex waste stream.

3. Resin choice rationale: Clear v4.1 has documented concentrated KOH tolerance; v5 does not, so defer caustic chemistry. Is this correct as of late 2025 / early 2026?

4. Shopping list (USA, university lab, modest budget, borrowing potentiostat):
   - Fisher AC424125000  K3[Fe(CN)6] 500 g  ~$70
   - Fisher P217-500     KCl ACS 500 g       ~$45
   - BASi MF-2012        3 mm GC working      ~$220
   - BASi MW-1032        Pt wire counter      ~$165
   - BASi MF-2052        Ag/AgCl 3M NaCl RE   ~$165
   - BASi CF-1050        0.05 um alumina      ~$45
   - Optional BASi MF-2060 PK-4 polishing kit ~$260
   Total bare minimum ~$525, recommended ~$785, ex shipping.

Are the prices in the right ballpark for late 2025 / early 2026? Are there meaningfully cheaper or higher-quality alternatives (e.g. CH Instruments, Pine Research, Gamry, ALS) for the electrodes that you would recommend? Any catalog numbers I should double check?

5. Success criteria: E0' ~ +0.23 V, dEp ~ 60-90 mV at 50 mV/s, |ipa/ipc| ~ 1, ip proportional to sqrt(v), no visible resin attack after ~1 h contact. Reasonable?

Please cite sources where you can. Be concise and call out anything that is wrong or risky.

## Critical Review: Ferricyanide CV in a 3D-Printed Formlabs Clear v5 Electrochemical Cell

The following table summarizes the point-by-point review of the proposed experimental plan, identifying errors, caveats, and recommendations:

| Item/Claim | Verdict | Key Comments/Corrections |
|---|---|---|
| 1. Probe chemistry: 1–5 mM K3[Fe(CN)6] in 0.1 M KCl; E0' ~ +0.23 V vs Ag/AgCl (3 M KCl); expected ip ~10–30 µA at 50 mV/s on 3 mm GC; reversible one-electron outer-sphere couple; diagnostic for iR drop, contamination, leaky joints | Caveat | E0' is essentially right: literature examples place ferri/ferrocyanide near +0.215 to +0.23 V vs Ag/AgCl depending on chloride concentration and reference details. Expected current is reasonable for about 1–3 mM, but 5 mM on a 3 mm GC at 50 mV/s is more like about 50–60 µA by Randles–Sevcik, not 10–30 µA. Calling it strictly outer-sphere is now considered too simplistic; a 2023 review argues hexacyanoferrate should be treated as surface-sensitive or multi-sphere because kinetics depend on surface chemistry, adsorbed films, cations, and double-layer effects. Still a good first diagnostic couple. Pt can passivate in ferricyanide experiments, so GC is the right WE choice. (ustundag2009edtamodifiedglassy pages 1-2, petrovic2000cyclicvoltammetryof pages 2-3, cassidy2023useofinnerouter pages 1-3, cassidy2023useofinnerouter pages 10-11, petrovic2000cyclicvoltammetryof pages 3-4) |
| 2. Safety: never acidify ferri/ferrocyanide (HCN risk); otherwise low hazard at mM scale, mL volumes, aqueous cyanide-complex waste stream | Caveat | Main warning is correct: acidified hexacyanoferrate solutions decompose, releasing HCN, slowly at room temperature and faster when heated. Additional oversight: UV light can slowly photodecompose hexacyanoferrate(II) to cyanide; avoid strong UV or sunlight and do not leave waste in clear bottles in sun. At your stated scale the absolute cyanide inventory is small, so low hazard is fair, but keep waste segregated, clearly labeled, and out of acid waste. (gail2011cyanocompoundsinorganic pages 16-18, gail2011cyanocompoundsinorganic pages 18-20, yang2007validationofan pages 2-3) |
| 3. Resin choice rationale: Clear v4.1 has documented concentrated KOH tolerance; v5 does not, so defer caustic chemistry | Caveat | I could not verify this version-specific claim from peer-reviewed sources. As a practical rule, deferring strong caustic work on Clear v5 until you have Formlabs compatibility data is sensible. For this actual test, near-neutral 0.1 M KCl with mM ferri/ferrocyanide for about 1 h, chemical compatibility risk is low and should not be the gating issue. (cassidy2023useofinnerouter pages 3-3) |
| 4. Shopping list and prices/catalogs | Caveat | Ballparks are broadly plausible, but there are cheaper options. Biggest factual issue: BASi MF-2052 is an Ag/AgCl reference with 3 M NaCl, not 3 M KCl; that slightly shifts the reference potential, so your quoted E0' should be adjusted if you use it. BASi WE, CE, and RE pricing is plausible but expensive for a first borrowed-potentiostat test. CH Instruments and ALS usually offer comparable 3 mm GC, Pt wire CE, and Ag/AgCl RE at much lower cost; CHI is often the cheapest mainstream option. Pine is high quality but usually not cheaper. Also, 500 g of K3[Fe(CN)6] is massive overkill for this experiment; even 25–100 g is plenty for years of test CVs. Petrovic specifically used CH Instruments electrodes and standard 0.05 µm alumina polishing supplies in an undergraduate ferricyanide-type CV setup. (petrovic2000cyclicvoltammetryof pages 1-2, petrovic2000cyclicvoltammetryof pages 2-3) |
| 5. Success criteria: E0' ~ +0.23 V, dEp ~ 60–90 mV at 50 mV/s, ipa/ipc ~ 1, ip proportional to sqrt(v), no visible resin attack after about 1 h contact | Correct | Reasonable and appropriately practical. Ideal reversible one-electron behavior is ΔEp about 59 mV at 25 °C, so 60–90 mV is a fair acceptance band for real cells with some uncompensated resistance. ipa/ipc about 1 and ip proportional to v^1/2 are standard checks for reversible diffusion-controlled CV. If ΔEp grows with repeated scans, suspect polishing issues, contamination, poor reference placement, or film formation. No visible resin attack after about 1 h is a good first-pass compatibility screen, though it will not catch subtle swelling or extractables. (petrovic2000cyclicvoltammetryof pages 1-2, petrovic2000cyclicvoltammetryof pages 2-3, petrovic2000cyclicvoltammetryof pages 3-4, cassidy2023useofinnerouter pages 3-4) |


*Table: This table checks each of the user’s five setup points for factual accuracy, safety, and cost-effectiveness. It highlights the main corrections and caveats that matter for a first ferricyanide CV in a 3D-printed cell.*

### 1. Probe Chemistry — Mostly Correct, Two Caveats

The formal potential E0′ ≈ +0.23 V vs Ag/AgCl (3 M KCl) is approximately correct. Literature values for the ferricyanide/ferrocyanide couple range from about +0.215 V vs Ag/AgCl (saturated KCl) to +0.23 V depending on the exact reference electrode filling solution and ionic strength (ustundag2009edtamodifiedglassy pages 1-2). The diffusion coefficient of ferricyanide in 0.1 M KCl is approximately 7.0–7.2 × 10⁻⁶ cm² s⁻¹ (petrovic2000cyclicvoltammetryof pages 2-3).

**Error in peak current range.** Applying the Randles–Ševčík equation, ip = (2.69 × 10⁵) n³/² A D¹/² C v¹/² (petrovic2000cyclicvoltammetryof pages 2-3), for a 3 mm GC electrode (A = 0.0707 cm²), D = 7.2 × 10⁻⁶ cm² s⁻¹, and v = 0.050 V s⁻¹: at 1 mM, ip ≈ 11 µA; at 5 mM, ip ≈ 57 µA. The stated range of 10–30 µA is correct only for the lower end of the 1–5 mM concentration range (roughly 1–3 mM). At 5 mM, expect approximately 55–60 µA, not 30 µA.

**Caveat on "outer-sphere" designation.** While the ferricyanide/ferrocyanide couple is widely used as a textbook outer-sphere probe, a comprehensive 2023 review argues that it should be classified as a "surface-sensitive" or "multi-sphere" electron transfer species, because its kinetics depend strongly on electrode surface chemistry, cation identity, adsorbed films, and double-layer structure. Nonetheless, this does not diminish its utility as a diagnostic probe; rather, it makes it even more sensitive to surface condition and cell quality, which is what you want for cell validation. Petrovic (2000) demonstrated that ferricyanide causes passivating Prussian blue film formation on Pt electrodes, leading to progressively increasing ΔEp with repeated scans — your choice of GC as the working electrode is therefore the right one (petrovic2000cyclicvoltammetryof pages 3-4, petrovic2000cyclicvoltammetryof pages 1-2).

### 2. Safety — Correct, with One Addition

The warning about never acidifying ferricyanide/ferrocyanide is confirmed. According to Ullmann's Encyclopedia: "When acidified with mineral acids, solutions of hexacyanoferrates decompose slowly at room temperature and more rapidly when heated, releasing HCN" (gail2011cyanocompoundsinorganic pages 16-18, gail2011cyanocompoundsinorganic pages 18-20). The hexacyanoferrate complexes themselves are described as "practically nontoxic because of the strong bonding between iron and cyanide" (gail2011cyanocompoundsinorganic pages 18-20).

**Additional hazard not mentioned: UV photodecomposition.** Hexacyanoferrate(II) decomposes slowly under UV light at normal temperature to release free cyanide ions (gail2011cyanocompoundsinorganic pages 18-20). This means: (a) store stock solutions in amber bottles or in the dark; (b) do not leave ferrocyanide-containing waste in clear containers in sunlight; (c) ferricyanide solutions also have limited shelf life in ambient light. This is a minor point at your scale (mM concentrations, mL volumes yields <1 mg total CN⁻), but worth knowing.

At your stated scale, the overall hazard assessment of "low" is fair. Keep waste segregated from acid waste streams and clearly labeled.

### 3. Resin Choice — Prudent but Unverifiable from Peer-Reviewed Literature

No peer-reviewed publications were identified that specifically compare chemical resistance of Formlabs Clear v4.1 vs v5. The user's caution in deferring caustic chemistry on v5 until Formlabs provides compatibility data is sound practice. For the proposed experiment — near-neutral 0.1 M KCl with mM-level ferricyanide for ~1 h — chemical compatibility with methacrylate-based SLA resins should not be a concern regardless of version. The real test will come when you move to more aggressive electrolytes.

### 4. Shopping List — Broadly Correct, but Key Errors and Savings Available

**Reference electrode error.** The BASi MF-2052 is an Ag/AgCl reference electrode with **3 M NaCl**, not 3 M KCl filling solution. This matters: the Ag/AgCl potential in 3 M NaCl is slightly different from 3 M KCl (~5 mV offset), and your stated E0′ of +0.23 V applies to the 3 M KCl reference. If you use the BASi MF-2052 with 3 M NaCl, your measured E0′ will be shifted accordingly. Either account for this or purchase a 3 M KCl-filled reference.

**500 g of K₃[Fe(CN)₆] is massive overkill.** At 5 mM in 20 mL per experiment, you use ~33 mg per run. Even 25 g would last for hundreds of experiments. Consider purchasing a smaller quantity unless you anticipate large-scale use, which also reduces cyanide-complex waste inventory.

**Significant cost savings with CH Instruments.** The BASi electrode set totals ~$550+ for WE, CE, and RE alone. CH Instruments (Austin, TX) is widely used in academic electrochemistry labs and offers comparable products at substantially lower prices. Petrovic (2000) used CH Instruments electrodes for an analogous undergraduate voltammetry experiment (petrovic2000cyclicvoltammetryof pages 1-2). A representative CH Instruments setup might include: 3 mm GC disk WE (~$75–100), Pt wire CE (~$40–60), Ag/AgCl (3 M KCl) RE (~$60–80), plus alumina polish (~$20–30), totaling roughly $200–270 — approximately half the BASi cost. ALS Co. (Japan, with US distribution) offers similar pricing. Pine Research Instrumentation is another high-quality option but tends to be priced between CHI and BASi.

**Price ballparks are otherwise reasonable** for late 2025 / early 2026, consistent with inflation from the ~$40/500 g ferricyanide prices noted in Petrovic (2000) (petrovic2000cyclicvoltammetryof pages 3-4).

### 5. Success Criteria — Correct and Practical

All stated diagnostic criteria are well-founded:

- **E0′ ≈ +0.23 V** — confirmed (see §1), provided you are using an Ag/AgCl (3 M KCl) reference.
- **ΔEp ≈ 60–90 mV at 50 mV/s** — the theoretical value for a reversible one-electron process is 59.2/n = 59 mV at 25 °C (petrovic2000cyclicvoltammetryof pages 1-2). Real macroelectrode cells typically show 60–80 mV due to uncompensated resistance; 80–90 mV is tolerable for a first test but warrants investigation. Values >100 mV should prompt checking reference electrode placement, cell resistance, and electrode polishing quality (petrovic2000cyclicvoltammetryof pages 3-4, cassidy2023useofinnerouter pages 6-8).
- **|ipa/ipc| ≈ 1** — standard criterion for a reversible process (petrovic2000cyclicvoltammetryof pages 3-4).
- **ip ∝ √v** — predicted by the Randles–Ševčík equation and confirms diffusion-controlled behavior (petrovic2000cyclicvoltammetryof pages 2-3).
- **No visible resin attack after ~1 h** — reasonable first-pass screen, though note that it will not detect subtle swelling, surface hazing on the interior, or extractable leachates that might contaminate electrochemical measurements. Consider also running a blank CV (KCl only, no ferricyanide) in the 3D-printed cell to check for any resin-derived redox peaks.

### Summary of Actionable Corrections

1. Recalculate expected ip: at 5 mM you should see ~55 µA, not ≤30 µA.
2. Add UV photodecomposition to your safety notes; store solutions and waste in the dark.
3. Verify your reference electrode fill solution: BASi MF-2052 uses 3 M NaCl, not 3 M KCl. Adjust your expected E0′ or buy a 3 M KCl reference.
4. Consider CH Instruments electrodes to save ~$300.
5. Buy 25–100 g of K₃[Fe(CN)₆] instead of 500 g.
6. Run a blank CV (KCl only) in the printed cell before adding ferricyanide to detect any resin-derived electroactive contaminants.
7. Note that ferricyanide is more accurately described as "surface-sensitive" rather than "outer-sphere," which actually makes it a better diagnostic for your cell.


References

1. (ustundag2009edtamodifiedglassy pages 1-2): Zafer Üstündağ and Ali Osman Solak. Edta modified glassy carbon electrode: preparation and characterization. Electrochimica Acta, 54:6426-6432, Nov 2009. URL: https://doi.org/10.1016/j.electacta.2009.06.015, doi:10.1016/j.electacta.2009.06.015. This article has 94 citations and is from a domain leading peer-reviewed journal.

2. (petrovic2000cyclicvoltammetryof pages 2-3): Steven C. Petrovic. Cyclic voltammetry of hexachloroiridate(iv): an alternative to the electrochemical study of the ferricyanide ion. The Chemical Educator, 5:231-235, Oct 2000. URL: https://doi.org/10.1007/s00897000416a, doi:10.1007/s00897000416a. This article has 100 citations.

3. (cassidy2023useofinnerouter pages 1-3): John F. Cassidy, Rafaela C. de Carvalho, and Anthony J. Betts. Use of inner/outer sphere terminology in electrochemistry—a hexacyanoferrate ii/iii case study. Electrochem, 4:313-349, Jul 2023. URL: https://doi.org/10.3390/electrochem4030022, doi:10.3390/electrochem4030022. This article has 47 citations.

4. (cassidy2023useofinnerouter pages 10-11): John F. Cassidy, Rafaela C. de Carvalho, and Anthony J. Betts. Use of inner/outer sphere terminology in electrochemistry—a hexacyanoferrate ii/iii case study. Electrochem, 4:313-349, Jul 2023. URL: https://doi.org/10.3390/electrochem4030022, doi:10.3390/electrochem4030022. This article has 47 citations.

5. (petrovic2000cyclicvoltammetryof pages 3-4): Steven C. Petrovic. Cyclic voltammetry of hexachloroiridate(iv): an alternative to the electrochemical study of the ferricyanide ion. The Chemical Educator, 5:231-235, Oct 2000. URL: https://doi.org/10.1007/s00897000416a, doi:10.1007/s00897000416a. This article has 100 citations.

6. (gail2011cyanocompoundsinorganic pages 16-18): Ernst Gail, Stephen Gos, Rupprecht Kulzer, Jürgen Lorösch, Andreas Rubo, and Manfred Sauer. Cyano compounds, inorganic. ArXiv, Oct 2011. URL: https://doi.org/10.1002/14356007.a08\_159.pub3, doi:10.1002/14356007.a08\_159.pub3. This article has 114 citations.

7. (gail2011cyanocompoundsinorganic pages 18-20): Ernst Gail, Stephen Gos, Rupprecht Kulzer, Jürgen Lorösch, Andreas Rubo, and Manfred Sauer. Cyano compounds, inorganic. ArXiv, Oct 2011. URL: https://doi.org/10.1002/14356007.a08\_159.pub3, doi:10.1002/14356007.a08\_159.pub3. This article has 114 citations.

8. (yang2007validationofan pages 2-3): Yongsheng Yang, Charles R. Brownell, Nakissa Sadrieh, Joan C. May, Alfred V. Del Grosso, Robbe C. Lyon, and Patrick J. Faustino. Validation of an in vitro method for the determination of cyanide release from ferric-hexacyanoferrate: prussian blue. Journal of pharmaceutical and biomedical analysis, 43 4:1358-63, Mar 2007. URL: https://doi.org/10.1016/j.jpba.2006.11.010, doi:10.1016/j.jpba.2006.11.010. This article has 13 citations and is from a peer-reviewed journal.

9. (cassidy2023useofinnerouter pages 3-3): John F. Cassidy, Rafaela C. de Carvalho, and Anthony J. Betts. Use of inner/outer sphere terminology in electrochemistry—a hexacyanoferrate ii/iii case study. Electrochem, 4:313-349, Jul 2023. URL: https://doi.org/10.3390/electrochem4030022, doi:10.3390/electrochem4030022. This article has 47 citations.

10. (petrovic2000cyclicvoltammetryof pages 1-2): Steven C. Petrovic. Cyclic voltammetry of hexachloroiridate(iv): an alternative to the electrochemical study of the ferricyanide ion. The Chemical Educator, 5:231-235, Oct 2000. URL: https://doi.org/10.1007/s00897000416a, doi:10.1007/s00897000416a. This article has 100 citations.

11. (cassidy2023useofinnerouter pages 3-4): John F. Cassidy, Rafaela C. de Carvalho, and Anthony J. Betts. Use of inner/outer sphere terminology in electrochemistry—a hexacyanoferrate ii/iii case study. Electrochem, 4:313-349, Jul 2023. URL: https://doi.org/10.3390/electrochem4030022, doi:10.3390/electrochem4030022. This article has 47 citations.

12. (cassidy2023useofinnerouter pages 6-8): John F. Cassidy, Rafaela C. de Carvalho, and Anthony J. Betts. Use of inner/outer sphere terminology in electrochemistry—a hexacyanoferrate ii/iii case study. Electrochem, 4:313-349, Jul 2023. URL: https://doi.org/10.3390/electrochem4030022, doi:10.3390/electrochem4030022. This article has 47 citations.