# The well, simulated with copper's own chemistry

[`sim_well_hf.py`](sim_well_hf.py) → [`sim_well_hf.json`](sim_well_hf.json) (every number below),
[`sim_well_hf.png`](sim_well_hf.png) (the figure) and [`sim_well_hf_fields.npz`](sim_well_hf_fields.npz)
(fields for the animation, same keys as `sim_well_fields.npz` plus `ph` and `film`).
`python sim_well_hf.py` takes about 15 min on 4 cores, `--quick` skips the grid check.

It replaces the placeholder kinetics of [`sim_well.py`](sim_well.py), which set Tafel lines
relative to an assumed bulk-cell i_corr and carried dissolved copper as a tracer. Here each alloy's
bulk cell is calibrated to published measurements, and the copper chemistry feeds back on itself.
It is still a model, not a measurement: it says how big the well's biases should be and where they
come from, so the bench calibration of [`protocol.md` §5](protocol.md#5-calibrate-first) knows what
to look for.

![High-fidelity well simulation](sim_well_hf.png)

## What it adds

| | `sim_well.py` | `sim_well_hf.py` |
| --- | --- | --- |
| Anodic copper | Tafel line, b_a 60 mV/dec, set relative to the bulk cell | Cu + 2Cl⁻ ⇌ CuCl₂⁻ + e⁻, nearly reversible, so the Cu(I) at the metal sits near its Nernst value and copper that piles up in the well throttles more dissolution |
| Film | none | Cu₂O: 30 % of the copper oxidised stays on the metal, more grows where the liquid at the metal is supersaturated in Cu₂O, and its thickness throttles dissolution. One constant per alloy, fitted to the published decay of i_corr with immersion time |
| Dissolved copper | a tracer | Cu(I) (all chloro complexes) and Cu(II); Cu(I) oxidised by dissolved O₂ (t½ 152 s in air-saturated seawater); Cu(II) reduced back at the metal; Cu₂O precipitating in the liquid and redissolving |
| pH | none | alkalinity transported, seawater carbonate and borate buffer (0.94 mM per pH unit at 8.2), closed by the cap |
| Electrolyte | none (a separate Laplace solve for R_u) | potential solved every step from the actual currents (secondary distribution), so iR and any ohmic shielding come out |
| Double layer | none | 30 µF/cm² |
| O-ring | sharp edge at the nominal Ø2.90 mm | the squeezed section, wetted out to r 2.00 mm, with its crevice resolved |
| Alloys | one placeholder metal at five i_corr | C70600, C71500, C95800, each calibrated; NAB has a second anodic path for its Al/Fe-rich phases |
| Grid | uniform 50 µm | 4 µm at the metal, 10 µm across the crevice, 50 µm elsewhere |

## The O-ring makes the spot almost twice as big

An AS568-006 ring squeezed 21 % to 1.40 mm, modelled as a stadium of conserved section area,
touches the metal flat from r = 2.00 to 2.68 mm. Inside that the metal is wet: a 0.1258 cm² disc,
**1.90 times the nominal 0.0661 cm²** (π · 1.45²). Between r = 1.30 mm (the ring's innermost
point) and 2.00 mm the liquid sits in a crevice that narrows to nothing at the contact line. The
model resolves it down to a 4 µm gap, which captures 0.1195 cm² of the 0.1258 (0.1213 at h/2).

That crevice is not dead. At 30 min of open circuit it carries **35 % of the anodic current** on
C71500 (34 % on C70600, 45 % on NAB) from 45 % of the wetted area. During the +50 mV hold its share
falls to 23 % on C71500 because the open spot takes most of the extra current. So:

- **R_p normalised by the nominal area reads 0.60 of the bulk cell's on C71500; normalised by the
  wetted area, 1.08.** The area choice is a larger error than anything the well does to the
  chemistry. Measure the wetted ring after each test (the attack ring the protocol already
  photographs), and report R_p with that area.
- The ohmic drop across the metal is tiny (0.1 µV at OCP, 35 µV in the hold, 0.2 mV for NAB), so
  the crevice is shielded by chemistry, not by resistance: its O₂ falls to 45 % of saturation at
  r = 1.7 mm against 60 % at the centre, and its dissolved copper is the highest in the well.

## Calibration: the bulk cell first

Each bulk cell is a 1 cm² spot under 1D Nernst layers (0.3 mm for O₂, scaled by (D/D_O₂)^⅓ for the
rest), with the same chemistry as the well.

| Alloy | Fitted | Target, source | Model |
| --- | --- | --- | --- |
| C70600, 90/10 Cu–Ni | k_O₂ 6.6 × 10⁻⁵ cm/s; film Γ* 4.6 × 10⁻⁹ mol/cm² | R_p 6.0 kΩ·cm² at 3 h, stagnant (Metikoš-Huković 2011); i_corr decay 12 → 5 µA/cm² in 20–22 h (Kear 2004), τ 4.4 h | R_p 5.99 kΩ·cm²; **E_corr −220 mV SCE, predicted** against −220 to −233 mV measured in ASW (Mantzavinos 2001); i_corr 3.9 µA/cm² at 6 min, 2.8 at τ |
| C71500, 70/30 Cu–Ni | k_O₂ 5.1 × 10⁻⁵ cm/s; Γ* 2.6 × 10⁻⁹ mol/cm² | R_p 8.3 kΩ·cm² at 3 h (Metikoš-Huković 2011); 8.44 → 1.01 µA/cm² in 10 days (Yuan 2007), τ 3.5 h | R_p 8.26 kΩ·cm²; E_corr −217 mV SCE, predicted (no measured value found); i_corr 2.9 → 2.1 µA/cm² |
| C95800, NAB | k_O₂ 1.0 × 10⁻⁴ cm/s; Al-path i₀ 8.6 µA/cm²; its oxide q* 0.34 C/cm² | E_corr −0.260 V SCE, R_f + R_ct 2.08 kΩ·cm², 11.35 → 3.78 µA/cm² in 240 h (Ding 2019), τ 30 h | fitted to all three; i_corr 9.0 µA/cm² at 6 min |

The Cu–Ni alloys have one fitted constant each for the electrochemistry (k_O₂, to R_p), and their
E_corr then comes out within the measured range for 90/10. NAB needs the second path: at −0.26 V SCE
the CuCl₂⁻ route can carry at most about 0.7 µA/cm² (its transport limit in the bulk cell at that
potential), and NAB's published current is about 9. That
second path is the Al- and Fe-rich phases, which is also what Ding 2019 saw attacked first.

## Results: the well against its bulk cell

The protocol's main sequence (OCP 30 min, LPR ±10 mV at 0.167 mV/s, rest 5 min, +50 mV hold
10 min, OCP 5 min), 150 µL of D1141 seawater, cap B (reference tip 3.0 mm up).

| | C70600 | C71500 | C95800 (NAB) |
| --- | --- | --- | --- |
| E_corr at 30 min, well − bulk | **+4.0 mV** | **+7.9 mV** | **−28.1 mV** |
| i_corr at 30 min, well ÷ bulk (wetted area) | 0.53 | 0.61 | 0.31 |
| R_p, well ÷ bulk, nominal area / wetted area | 0.67 / 1.22 | 0.60 / 1.08 | 1.75 / 3.17 |
| +50 mV hold current, well ÷ bulk | 0.43 | 0.53 | 0.30 |
| O₂ at the centre, 30 min | 52 % | 60 % | 24 % |
| pH at the centre: 30 min / end of hold | 8.30 / 7.19 | 8.29 / 7.31 | 8.29 / 5.80 |
| Cu oxidised in 52 min | 941 ng | 832 ng | 22 ng (plus 220 ng of Al) |
| … left on the metal as film | 456 ng | 409 ng | 9 ng |
| … into the tube (Cu(I) + Cu(II) + suspended Cu₂O) | 485 ng: 1.5 mg/L in 320 µL | 423 ng: 1.3 mg/L | 13 ng: 42 µg/L; Al 220 ng: 0.69 mg/L |
| Charge passed (anodic, both paths) | 1.43 mC | 1.26 mC | 2.39 mC |

What it means:

1. **For Cu–Ni the well reads E_corr a few mV *more positive* than the bulk cell, not 9 mV more
   negative as `sim_well.py` had it.** Two effects pull against each other. The still well supplies
   less O₂, which pulls E_corr down. But the Cu(I) that piles up near the metal (75–80 µM after 30 min, above the 42 µM at
   which Cu₂O saturates) pushes the dissolution back toward equilibrium, which pulls it up, and the
   Cu(II) that Cu(I) oxidation makes is a second oxidant at the metal. For Cu–Ni the copper feedback
   wins, by 4–11 mV through the first 30 min.
2. **For NAB the O₂ effect wins, by 28 mV.** Its anodic current is mostly the Al/Fe-phase path,
   which has no back-reaction, and its higher current starves the well of O₂ faster (24 % of
   saturation at the centre, 9 % in the crevice). Its R_p reads 1.75 times the bulk cell's even on
   the nominal area. A well comparison of NAB against Cu–Ni is therefore biased toward NAB.
3. **Corrosion rates read low in the well, by a factor of 2–3**, and the +50 mV hold passes
   0.30–0.53 of the bulk cell's current. The old model had 0.71 and 0.69 at 5 µA/cm².
4. **About half of the copper oxidised reaches the tube** (0.51–0.52 for Cu–Ni). The rest is film.
   That split rests on the assumed 30 % solid-state share (`BETA_FILM`): at 10 % the tube gets 0.62
   of it, at 60 %, 0.32 (sensitivity below). The ICP-MS number is a lower bound on what dissolved,
   and the charge-to-copper balance the protocol asks for (§6) is a measurement of this split.
5. **The well acidifies under anodic polarisation**: pH 7.2–7.3 at the spot after the +50 mV hold
   for Cu–Ni, from Cu₂O formation (2Cu + H₂O → Cu₂O + 2H⁺ + 2e⁻) and precipitation, and 5.8 at the
   centre and 2.8 in the crevice for NAB, from Al hydrolysis (a lower bound: the model keeps
   hydrolysing Al³⁺ below pH ~4.5, where it really stops). At open circuit it stays near 8.3. So the hold changes
   the chemistry of the companion measurement after it; the protocol's companion OCP-only well
   (§4) is the right control.
6. **A cathodic step replates much less than the old model said**: 18.5 % of the dissolved copper in
   10 min at −300 mV on C71500, against 51 %. Most of the copper is by then Cu(II) or suspended Cu₂O,
   away from the metal, and only Cu(I) at the metal replates. It is still enough that cathodic holds
   belong on separate spots.
7. **Ohmic effects and double-layer charging are negligible**: under 0.04 mV of non-uniformity on
   Cu–Ni, 0.2 mV on NAB, and the double layer is under 1 % of the LPR charge. Natural convection is
   subcritical (below).

## Checks

| Check | Result |
| --- | --- |
| Cottrell (O₂-limited flat spot as wide as the bore, 1 cm deep) | model ÷ analytic 1.013 at 30 s, 1.004 at 120 s, 1.0015 at 300 s, 1.0008 at 600 s |
| Copper mass balance (oxidised = liquid + suspended + film) | error below 0.001 % for all three alloys |
| Grid, C71500, h against h/2 (40,986 cells) | E_corr −221.5 / −221.5 mV; R_p 3223 / 3205 Ω·cm² (nominal area); hold 7.73 / 7.64 µA/cm²; Cu oxidised 832 / 836 ng; to the tube 423 / 424 ng; crevice share 0.350 / 0.355; resolved wetted area 0.1195 / 0.1213 cm² |
| Bulk calibration | R_p within 0.5 % of each target; NAB E_corr −262.0 mV for −262 mV; i_corr decay at τ 0.714 / 0.716 / 0.708 for targets 0.714 / 0.716 / 0.708 |
| E_corr of C70600, not fitted | −220 mV SCE at 3 h against −220 to −233 mV measured |

## Sensitivity (C71500)

| Change | E_corr 30 min | R_p, nominal area | Hold | Cu to the tube | Share of Cu oxidised reaching the tube |
| --- | --- | --- | --- | --- | --- |
| Baseline | −221.5 mV | 3223 Ω·cm² | 7.73 µA/cm² | 423 ng | 0.51 |
| Cu(I) oxidation 10× slower | −224.7 | 3377 | 7.33 | 369 | 0.53 |
| Film share 10 % (Γ* refitted) | −213.6 | 3940 | 7.41 | 512 | 0.62 |
| Film share 60 % (Γ* refitted) | −230.2 | 2610 | 7.30 | 254 | 0.32 |

The well-vs-bulk E_corr shift stays +8 to +11 mV across the film-share range (bulk −221.6 and
−241.4 mV respectively), so its sign is robust; the copper split is not, which is why the protocol
measures it.

## Parameters and where they come from

"Via Edison" means the number is from the Edison answers in [`../copper-ded-edison/batch1/`](../copper-ded-edison/batch1/),
whose agent read the paper; I did not re-read it. "Assumed" means no source was read for the value.

| Parameter | Value | Source | Read |
| --- | --- | --- | --- |
| Dissolution mechanism, nearly reversible and largely transport-limited | Cu → Cu⁺ + e⁻, Cu⁺ + 2Cl⁻ → CuCl₂⁻ | Hauser and Newman, LBL report 1988 (copper RDE in chloride) | full text |
| Product in neutral aerated NaCl | mostly CuCl₂⁻; a CuCl layer at less cathodic potentials | Deslouis, Tribollet, Mengoli, Musiani 1988, J. Appl. Electrochem. 18 | abstract |
| Film-free exchange conductance K₀ | 0.01 cm/s (28 × the bulk cell's transport conductance) | value assumed, consistent with "nearly reversible" | — |
| E°(CuCl₂⁻/Cu); Cu₂O solubility | 0.2317 V SHE; 41.7 µM Cu(I) at pH 8.2 (16.4 µM as CuCl₂⁻) | NBS ΔfG° (CuCl₂⁻ −240.1, Cl⁻ −131.228, Cu₂O −146.0, H₂O −237.129 kJ/mol), as `sim_well.py` | tables, not re-read |
| Cu(I) speciation | log β 2.7, 5.5, 5.7 at I = 0, Davies to I 0.7: CuCl₂⁻ 39 %, CuCl₃²⁻ 61 % | assumed (typical compilation values) | — |
| Cu(I) oxidation | Cu⁺ 14.1 s⁻¹, CuCl⁰ 3.9 s⁻¹ → 4.6 × 10⁻³ s⁻¹ for total Cu(I) in air-saturated seawater | Sharma and Millero 1988, J. Solution Chem., as restated in a later paper's search snippet | snippet only |
| D(O₂) | 1.9 × 10⁻⁵ cm²/s | Southampton RDE case study, 1.9 ± 0.2 × 10⁻⁵ in chloride at 25 °C; Kear, Albarran, Walsh RDE ~1.5 × 10⁻⁵ in seawater | abstracts |
| D of Cu(I), Cu(II), alkalinity, Al | 8.0, 7.0, 11, 5.0 × 10⁻⁶ cm²/s | assumed | — |
| O₂ saturation, κ | 0.21 mM, 0.053 S/cm | as `sim_well.py` | — |
| Carbonate and borate | DIC 2.39 mM, B 0.437 mM (D1141's NaHCO₃ and H₃BO₃); pK₁* 5.847, pK₂* 8.966, pK_B 8.597, pK_W 13.217 | D1141 recipe; Lueker 2000, Dickson 1990, Millero 1995 | standard values, not re-read |
| O₂ reduction | α 0.5 (b_c 118 mV/dec); k_O₂ fitted | α assumed | — |
| R_p targets, Cu–Ni | 6.0, 8.3 kΩ·cm², 3 h stagnant, 3.5 % NaCl pH 7.9 (binary Cu–10Ni, Cu–30Ni at.%) | Metikoš-Huković et al. 2011, Desalination 276 | via Edison c1-05 |
| Film decay times | τ 4.4 h (90/10), 3.5 h (70/30), 30 h (NAB) | Kear et al. 2004 review; Yuan and Pehkonen 2007; Ding et al. 2019 | via Edison c1-02 |
| NAB E_corr and R | −0.260 V SCE; R_f + R_ct 1761 + 318 Ω·cm² | Ding et al. 2019, cast C95800, 3.5 % NaCl | via Edison c1-02 |
| C70600 E_corr (check only) | −220 to −233 mV | Mantzavinos 2001, ASW 20 °C | via Edison c1-03 |
| Film share of Cu oxidised | 30 % | assumed; 10 % and 60 % in the sensitivity | — |
| Cu₂O precipitation | 0.01 s⁻¹ in the liquid, 10⁻⁴ cm/s onto the film | assumed | — |
| Cu(II) reduction at the metal | 10⁻³ cm/s | assumed | — |
| NAB Al/Fe-phase path | b 60 mV/dec; i₀ and its oxide's q* fitted | b assumed | — |
| C_dl | 30 µF/cm² | assumed (Hauser and Newman used 10) | — |
| Cu activity in the alloy | mole fraction: 0.877, 0.666, 0.713 | ideal solution, assumed | — |

## Natural convection

Rayleigh numbers for the 4.4 mm column, against 1101 for a layer with a rigid bottom and a free top
(side walls raise the threshold further):

- **Thermal:** 157 for a 0.1 K bottom-heated difference, 1567 for 1 K. A sealed cap at room
  temperature is far below 0.1 K, but a deck warmed from below by the steppers could approach 1 K.
  Log the deck temperature under the tray.
- **Solutal:** dissolved copper makes the bottom denser, which is stable (−12,900 at 100 µM).
  O₂ depletion is between −76 and 313 depending on its partial molar volume (28–32 cm³/mol), so
  subcritical either way.

Neglecting convection is justified for a thermally quiet deck.

## What it changes in the protocol

- **Report R_p and current densities on the measured wetted area**, from the attack ring, not on the
  O-ring's nominal ID. On the nominal area the well reads R_p 0.6–0.7 of the bulk cell's for Cu–Ni;
  on the wetted area, 1.1–1.2. Or change the seal so the contact line sits at the ID (a flat FKM
  gasket punched to Ø2.90 mm, or a sharper lip), which also removes the crevice.
- **Do not compare NAB with Cu–Ni in the well without the bulk-cell calibration.** The model puts
  NAB's E_corr 28 mV low and its R_p 1.75 times high in the well, against small biases for Cu–Ni.
- **Expect the ICP-MS copper to be about half of the charge**, with the rest as film, and treat the
  measured split as a result. Strip the film from a few spots afterwards (the coulometric reduction
  of [`protocol.md` §8](protocol.md#8-later-modules)) to close the balance.
- **The anodic hold acidifies the spot to pH 7.2–7.3 on Cu–Ni and below 6 on NAB.** Keep the
  companion OCP-only well, and read the OCP after the hold as a disturbed surface.
- **The 30 min OCP is still the right length.** In the model the well's E_corr on C71500 moves
  0.5 mV over the last 15 min.

## What it still leaves out

Ni, Fe and Mn dissolution and their films; CuCl and Cu₂(OH)₃Cl solids; reduction of the Cu₂O film at
cathodic potentials (so the cathodic case overstates what the film keeps); the counter's chlorine and
hypochlorite, which would oxidise Cu(I); Al³⁺ hydrolysis that stops below pH ~4.5 (so NAB's crevice
pH of 2.8 is a lower bound); migration (0.7 M supporting electrolyte); natural convection; roughness and
fluid at the O-ring's contact line; and any effect of sulfide. The Cu(I) oxidation constants were
seen only as restated in a search snippet, and the speciation constants are assumed; the 10 × slower
case shows that this moves E_corr by 3 mV. Calibration targets come from bulk cells in 3.5 % NaCl
for two of the three alloys, not D1141.
