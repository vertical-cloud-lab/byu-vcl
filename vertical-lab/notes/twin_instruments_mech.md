# Twin round 2: mechanical, powder and corrosion instrument simulators

The twin's instruments (PR 318, `twin/instruments/`, contract in `twin/instruments/__init__.py`) make the raw data a
real instrument makes from the artifact's hidden state, then run the analysis a lab runs on that data. This note
covers the mechanical, powder and corrosion set: `mech.py` (shared constitutive and fracture model), `tensile.py`,
`pip.py`, `hardness.py`, `density.py`, `psd.py`, `atomize_yield.py`, `reuse.py` and `corrosion.py`, with
`calibrate_mech.py` / `calib_mech.json` (the fast modes), `gallery_mech.py` (figures) and
`twin/tests/test_instruments_mech.py`.

```bash
cd vertical-lab
nice -n 10 /tmp/venv/bin/python -m twin.instruments.calibrate_mech --n 80     # ~25 s CPU; writes calib_mech.json
nice -n 10 /tmp/venv/bin/python -m pytest -q twin/tests/test_instruments_mech.py   # 62 tests, ~10 s CPU
nice -n 10 /tmp/venv/bin/python -m twin.instruments.gallery_mech              # out/twin2/instruments, out/twin2/thumbs
```

Values marked *assumed* are ours, not a source's. Every module's docstring holds its full model; this note
summarises it.

## Shared hidden state (mech.py)

Tensile, PIP and hardness all read the same part through `mech.py`, so their results are correlated the way a real
lab's are. For example, PIP and Vickers agree with each other and disagree with tensile on a porous part.

- **Elastic modulus.** The Hill average of the Voigt and Reuss bounds over the elements' Young's moduli, weighted by
  volume fraction ([Kaye & Laby](https://www.kayelaby.npl.co.uk/general_physics/2_2/2_2_2.html); Si 162 GPa from
  [Hopcroft 2010](https://doi.org/10.1109/JMEMS.2009.2039697)). Porosity is corrected with Mackenzie's
  E0 (1 - 1.9 p + 0.9 p²) ([1950](https://doi.org/10.1088/0370-1301/63/1/302)). Temperature enters linearly at
  -4.8e-4 /K for Al and -3.8e-4 /K for Cu (*assumed linear*). Results: AlSi10Mg 77 GPa, 70-30 Cu-Ni 150, NAB 109–116.
- **Voce law** σ = s_y + (s_s − s_y)(1 − exp(−θ0 ε/(s_s − s_y))). It is fixed by the 0.2 % proof stress, the
  engineering UTS at Considère's point and the uniform strain there.
  - The bar law matches the truth's `ys_MPa` and `uts_MPa` exactly. Its uniform elongation is
    e_u = (0.62 + 0.38 exp(−el/4)) el (*assumed*).
  - The matrix law is the sound metal: `ys_sound_MPa`, with the truth's UTS/YS ratio at the sound ductility (the
    truth's porosity and crack knock-downs undone).
  - A bar too brittle to neck gets its neck moved out, so that it breaks first instead.
- **Texture.** The truth's strength is taken as the horizontal (XY) bar's. Columnar share is 1 − `equiaxed` for Al
  and 0.7 for DED Cu. Along Z, flow stress is 9 % × columnar lower and elongation 25 % × columnar lower (*assumed*,
  after [Tang et al. 2021](https://doi.org/10.1016/j.mtla.2021.101017)).
- **Fracture (weakest link).** Each pore population in the truth's `pores` (gas, keyhole, lack of fusion) has a
  lognormal size distribution (*assumed* medians: Al 15/55/110 µm, Cu 30/90/220 µm). Cracks come from
  S_V = 4 L_A / π, with linking across a band one crack size thick (*assumed*).
  - The largest defect in the gauge volume is a Poisson extreme-value draw.
  - The bar is then an imperfect bar (the Marciniak–Kuczyński / Hutchinson–Neale argument): the defect section
    carries (1 − a)/(1 − ā) of the law's load and breaks at a local strain ε_loc.
  - ε_loc is solved per part so that the mean elongation over specimens equals the truth's `el_pct`.
  - Scatter and early breaks therefore grow with defects. A crack-dominated part sometimes breaks before its 0.2 %
    offset, so its `ys_MPa` is absent for that bar.

## Instruments

| module | what it simulates | raw data (full) | analysis |
|---|---|---|---|
| `tensile.measure` / `measure_hot` | 3 sub-size bars, L0 = 5.65 √A0 (Al 3×2 mm, Cu 6×3 mm). ISO 6892-1 A1 strain rates. 50 Hz (full) or 5 Hz (lite). Extensometer noise 1.5e-5 and 1e-5 resolution; load cell 0.1 % + 0.3 N; machine compliance 3e-5 mm/N; seating toe; micrometer ±5 µm. Bar-to-bar strength 1.2 % + 0.3 × porosity. Hot test: 250 °C ±2 K. `orientation='z'` cuts the bars along the build direction (columnar parts: AlSi10Mg YS −9 %, EL −25 %; runs the lite chain). (*All instrument numbers assumed.*) | stress–strain records, crosshead, true curves | ASTM E8/E111: modulus over 15–40 % of max force, toe compensation, 0.2 % offset, UTS, plastic elongation at fracture; returns means, `n_bars` and per-bar `bars` |
| `pip.measure` | Plastometrex PLX: 1 mm WC-Co ball, load aimed at a/R = 0.6 from a ±20 % strength guess. Analytical forward model: Tabor representative strain; Johnson expanding cavity C ≤ 3; Hill–Storåkers–Zdunek pile-up c² = 2.5(2−m)/(4+m) ([1989](https://doi.org/10.1098/rspa.1989.0056)); Hertzian recovery. Stylus noise 0.15 µm, roughness 0.2 µm, tilt, off-centre trace. Friction 0.1–0.4 against the model's 0.2; software E 71/125 GPa. | 3 indents, each a 3001-point stylus trace; the fitted profile; the true and fitted Voce laws | Least-squares Voce fit to the levelled, centred profile with the same forward model (the PIP iteration) → 0.2 % proof, engineering UTS, uniform elongation |
| `hardness.measure_vickers` | HV0.5, 5 indents. Tabor HV = 3 σ(8 %); Nix–Gao ISE (h* 0.6/1.0 µm, *assumed*). Pores in the indent zone as a Poisson draw (2 × their share, *assumed*); indents > 30 % on a void rejected per ISO 6507. Diagonals ±0.4 µm + 0.4 %. | HV per indent, diagonals | HV = 1.8544 F/d² |
| `hardness.measure_nanoindent` | Berkovich, 50/80 mN, 16 indents (9 in lite); Tabor at 7.2 %; Nix–Gao; grain-orientation scatter (H 6 %, E 2 % Al / 8 % Cu, divided by √grains); β′ hits; pile-up area error ([Bolshakov & Pharr 1998](https://doi.org/10.1557/JMR.1998.0146)); drift; tip-area C1 ±5 %. | load–depth curves | [Oliver–Pharr](https://doi.org/10.1557/JMR.1992.1564): quadratic fit to the top 60 % of unloading, h_c = h_max − 0.75 P/S, E from E_r |
| `density.measure` | Archimedes in water: 0.1 mg balance, water density from [Tanaka 2001](https://doi.org/10.1088/0026-1394/38/4/3) at 21 ± 1.5 °C, meniscus ±0.3 mg, bubbles (exponential, 0.4/0.8 mm³). Open porosity is flooded unless `sealed=True` (lack of fusion 0.3 + 10 × share connected, cracks 80 %: *assumed*). | masses, T, bubble, open and closed porosity | ρ = m_a ρ_L / (m_a − m_w) against the **designed** composition's rule-of-mixtures density, so Mg, Zn or Li loss reads high (Scalmalloy 1.009) |
| `psd`, `atomize_yield`, `reuse` | see "Powder" below | | |
| `corrosion.measure_screen` / `measure_immersion` | see "Corrosion" below | | |

### Physics that emerges, checked by the tests and the gallery

- Tensile on sound AlSi10Mg is within 1 % of the truth's YS, within 3 % of its UTS and within 5 % of its EL.
- Porous and cracked bars scatter more. A crack-dominated 7075 breaks before 0.2 % in about a quarter of its bars.
- PIP over-reads porous and cracked parts. In `pip_vs_tensile.png`, 128 designs, PIP sits +18 % above tensile on
  defective parts (sd 29 %).
- On sound parts, PIP is within published accuracy against tensile: UTS −3.2 % (sd 2.6 %), YS −3.9 % (sd 5.3 %).
  Published figures are about 5 % on UTS and about 10 % on YS
  ([Campbell et al. 2019](https://doi.org/10.1016/j.actamat.2019.02.017),
  [Clyne et al. 2021](https://doi.org/10.1002/adem.202100437),
  [Tang et al. 2021](https://doi.org/10.1016/j.mtla.2021.101017)).
- PIP's UTS is pinned better than its YS because indentation strains bracket the neck. Its ductility is uniform
  elongation, below tensile EL on ductile Cu-Ni.
- Columnar texture biases PIP and Vickers low by half the Z/XY difference.

## Powder: PSD, flowability, atomizer yield, reuse (psd.py, atomize_yield.py, reuse.py)

- **PSD (Mastersizer 3000 + Aero S).**
  - The true lot volume distribution is a mixture of the runs' lognormals, weighted by charge_g × usable_frac.
  - Satellites: a share min(0.5, sat/2) of the volume below d50/4 sits on hosts, which grow +12 %.
  - Cohesive fines agglomerate (d_coh 15 µm Al, 8 µm Cu); reuse adds spatter.
  - Aero S pressure breaks agglomerates (P_agg 1.0/0.7 bar) and frees satellites (8 bar).
  - Poisson sampling of a 2 g / 5 g aliquot.
  - Forward model: Fraunhofer diffraction plus Schlick–Fresnel reflection (Al 1.37+7.62i, Cu 0.27+3.41i,
    [refractiveindex.info](https://refractiveindex.info)), specular share 0.9(1−0.3 sat)exp(−O/20000).
  - Inversion: NNLS + Tikhonov against the chosen optical model
    ([ISO 13320:2020](https://www.iso.org/standard/69111.html);
    [Mastersizer 3000](https://www.malvernpanalytical.com/en/products/product-range/mastersizer-range/mastersizer-3000)).
  - The Fraunhofer setting reads −7 % d50 with spurious fines. *All coefficients assumed.*
- **Flow** (`psd.flow`).
  - Beverloo (Chem. Eng. Sci. 15, 1961) through the Hall funnel (ASTM B213, 2.54 mm) or the Carney funnel
    (ASTM B964, 5.08 mm), × 1.3 hopper factor.
  - Cohesion through a Bond number on d32 (A 6.5e-20 J, asperity 12 nm, z0 0.4 nm) and ffc = 3.7 Bo^-0.27 (Capece et
    al., Powder Technol. 286, 2015, *as recalled*).
  - `lof_factor` is the knob the campaign can multiply LPBF lack-of-fusion porosity by for a poorly flowing powder
    (Spierings et al., Prog. Addit. Manuf. 1, 2016). *Assumed.*
- **Yield** (`atomize_yield.measure`).
  - Per-run mass balance: 0.01 g balance; heel 2.5/3.5 cm³ plus 1 %/0.5 % dross.
  - The rest of the loss splits 30/35/10/25 % into oversize, splat, filter and unaccounted; a failed run leaves 70 %
    as skull.
  - Sieving: Gaudin passage ((a−d)/(a+w))² with ISO 3310-1 aperture spread, 200 presentations/min, bed-depth and
    blinding terms (ASTM B214, ISO 2591-1).
  - `cut_g` is what the sieve actually gives: about 15 % below the ideal lognormal cut for coarse Al lots (near-mesh
    particles held back by the 63 µm sieve) and about 5 % below for Cu.
  - Anchors: DAL #219 (1,080 g NAB, 91 % usable) and notes/alloy_charge.md (4 cups ≈ 59 cm³).
- **Crucibles** (`crucible_options()`, `charge_plan(campaign, crucible_cm3, fill=None)`). Every plan returns
  `charge_g`, `run_h`, `consumables` (supply keys `argon`, `cc_plate`, `graphite_crucible`, `bn_spray`, plus
  `bn_nozzle` for Cu), `p_fail_add` and `note`, along with meltdown time, heel share and superheat non-uniformity.
  Per-run charge:

  | campaign | crucible | cups | rod pieces |
  |---|---|---|---|
  | Al | 225 cm³ | 158 g | 382 g |
  | Al | 400 cm³ | 237 g | 679 g |
  | Cu | 225 cm³ | — | 1,240 g (NAB about 1,080 g with `comp`) |
  | Cu | 400 cm³ | — | 2,204 g |

  The 400 cm³ crucible is charged as 1.56 × `graphite_crucible` (*assumed* $700 against $450). Its geometry is also
  *assumed*.
- **Reuse** (`after_build(lot, grams_spread, grams_fused, process, rng)`,
  `after_ded(lot, grams_fed, catchment, process, rng)`). Both return `(grams_back, state of the returned powder)` and
  never mutate the input.
  - LPBF: the oxide grows 0.5 nm per build, plus oxidised spatter; recovery is clipped to 85–95 %
    ([Raza et al., Mater. Des. 198, 2021](https://research.chalmers.se/publication/521110/file/521110_Fulltext.pdf);
    [Fiegl et al., Mater. Des. 212, 2021](https://research.chalmers.se/en/publication/526911);
    [Cordova et al., JOM 71, 2019](https://link.springer.com/article/10.1007/s11837-018-3305-2);
    Del Re et al., IJAMT 97, 2018). AlSi10Mg oxygen goes 900 → 1,364 → 1,793 ppm at 0, 10 and 20 builds.
  - DED overspray: 65 % is swept up, and a heated share of 10 % × P/600 W comes back with an oxide shell
    ([Terrassa et al., Powder Technol. 338, 2018](https://www.osti.gov/pages/biblio/1693671)).

## Corrosion (corrosion.py, ONR only)

- **Screen** (CubXL, 0.071 cm² O-ring well, artificial seawater).
  - OCP for 60 min: Cu2O ennoblement, E_inf from the galvanic series
    ([ASTM G82](https://www.astm.org/g0082-98r21.html); drift and tau *assumed*).
  - EIS from 100 kHz to 10 mHz: Randles + CPE + finite Warburg ([Brug 1984](https://doi.org/10.1016/S0022-0728(84)80225-5)),
    CNLS fit for Rct.
  - LPR ±10 mV at 0.167 mV/s ([ASTM G59](https://www.astm.org/g0059-97r20.html)) on a mixed-potential curve: anodic
    ~60 mV/dec ([Kear 2004](https://doi.org/10.1016/S0010-938X(02)00257-3)), O2 limiting current 25 µA/cm² (*assumed*),
    R_u 60 Ω, charging current, drift.
  - Cyclic polarization at 1 mV/s, reversed at 1 mA/cm² ([ASTM G61](https://www.astm.org/g0061-86r18.html); both
    *assumed*).
  - Analysis: a Butler–Volmer fit over −100..+30 mV gives B ([Stern & Geary 1957](https://doi.org/10.1149/1.2428496));
    Eb at 100 µA/cm²; Erp at loop closure; then Faraday's law with the design's equivalent weight
    ([ASTM G102](https://www.astm.org/g0102-89r15e01.html)).
  - Nuisances (*assumed*): T 22 ± 1 °C (20 kJ/mol), dissolved O2 ±8 %, area ±4 % and × (1 + 1.5 porosity), 18 % spot
    scatter, 8 % chance of an O-ring crevice (−100 mV).
  - The screen reads 1.5–1.75× the truth's early rate. The Tafel fit inflates B by about 30 %, and porous parts wet
    more area.
- **Immersion.**
  - Coupon and solution: 20×10×3 mm in 200 mL ASW ([ASTM G31](https://www.astm.org/g0031-21.html), D1141).
  - Rate: r(t) = r_inf + (r_1h − r_inf) exp(−t/film_days). This runs above the old stub, e.g. NAB 21.3 against
    16.3 µm/yr.
  - Mass loss: 45 % of the product is retained (× 1.4 mass); G1 cleaning over 6 cycles, extrapolated
    ([ASTM G1](https://www.astm.org/g0001-03r17e01.html)); 0.1 mg balance.
  - SEM: 10 fields × 250 µm of exponential site depths whose expected maximum over 10 mm is `attack_um` (Gumbel;
    [Shibata 1996](https://doi.org/10.5006/1.3292074); ASTM G46). LOD 0.5 µm. A porous part's lack-of-fusion pores
    are mistaken for attack with p = 0.05–0.10.
  - ICP-MS on day 30: Cu/Ni retention 0.45/0.65, 10 % wall loss, 50× dilution, blank-subtracted, LOD 1.7/1.0 ppb
    (all *assumed*).

## Fast mode and its calibration

`calibrate_mech.py` builds lots and parts through the truths the way `campaign.py` does: 80 designs per campaign
from `spaces.sample`, with each design's own atomizer, LPBF and DED settings, plus the reference alloys. That is
168 parts covering porosity 0.3–13 %, crack density 0–2 mm/mm² and EL 0.2–37 %. It runs every lite chain 3–6 times
per sample and fits what `fast` samples.

- **Tensile, PIP, hardness, density and yield use a two-level model** (`fit_two_level`, evaluated by
  `mech.two_level`). For the log ratio of measured to the truth's (or sound) value:
  - the between-sample mean is a ridge-linear model in state features, plus a kernel-smoothed table of each
    calibration sample's own residual (k = 6 nearest, h = 0.2);
  - the within-sample spread is a log-linear model plus a smoothed table, bias-corrected for small repeats.
  - Features: porosity, lack of fusion, cracks, gas, columnar share, β′. Tensile adds its ductility and the
    largest-defect share's mean and spread. PIP adds the modulus mismatch, the hardening and the indent geometry's
    response to it. Hardness adds hardening, strength and grain size.
  - Tensile also has a logistic model for a break before 0.2 % offset.
- **PSD and corrosion** use linear models with a correlated (Cholesky / MVN) residual.

| fast model | between-sample rmse (log) | median within-sample sd | mean bias |
|---|---|---|---|
| tensile YS / UTS / EL / E (per bar) | 0.011 / 0.029 / 0.093 / 0.019 | 0.021 / 0.049 / 0.195 / 0.016 | −0.3 % / −3 % / −2 % / −1 % |
| tensile at 250 °C YS / UTS / EL | 0.012 / 0.035 / 0.087 | 0.028 / 0.061 / 0.249 | −0.6 % / −4 % / −4 % |
| PIP YS / UTS / UE (vs the sound metal) | 0.024 / 0.012 / 0.115 | 0.018 / 0.008 / 0.061 | −4 % / −6 % / +3 % |
| Vickers HV (vs Tabor) | 0.011 | 0.014 | +2 % (ISE) |
| nano H / E | 0.016 / 0.012 | 0.017 / 0.019 | +32 % (ISE + pile-up) / +3 % |
| density (rel., after open porosity and bubble) | 0.0003 | 0.0005 | +0.0009 |
| PSD d10 / d50 / d90 (vs the lot lognormal) | — | 1.2–1.4 % | −1.8 % / +3.6 % / +10.6 % |
| yield collected / cut | — | — | −0.3 % / −15 % Al, −4.6 % Cu |
| screen ln Rp / ln B / ln Rct; OCP; Eb; Erp | 0.16 / 0.11 / 0.17; 9 mV; 27 mV; 32 mV | | early rate ×1.5–1.75 |
| immersion ln rate30 / ln Cu / ln Ni | 0.075 / 0.09 / 0.08 | | |

The tests check fast against lite on sound, porous and cracked samples for 16 outputs: means within 4 SE + 4 %, and
spreads within ×3.

## Timings

CPU time per call on the runner (`time.process_time`, so the other jobs' load does not count). The test asserts
fast < 1 ms and lite < 30 ms.

| instrument | fast (ms) | lite (ms) | full (ms) |
|---|---|---|---|
| yield | 0.28 | 0.7 | 5 |
| psd | 0.06 | 0.6 | 3 |
| density | 0.03 | 0.02 | 0.02 |
| pip | 0.16 | 9.4 | 16 |
| vickers | 0.06 | 0.1 | 0.2 |
| nanoindent | 0.08 | 1.0 | 2 |
| tensile | 0.25 | 0.8 | 1 |
| tensile_hot | 0.24 | 0.8 | 1 |
| corrosion_screen | 0.11 | 3.9 | 5 |
| immersion | 0.04 | 0.2 | 0.3 |

## Gallery

`gallery_mech.py` writes:
- `out/twin2/instruments/`: `psd.png`, `yield.png`, `pip.png` (profile, fit and Voce curves), `tensile.png` (RT and
  250 °C), `hardness.png`, `corrosion_screen.png` (OCP, LPR, Nyquist, CP), `immersion.png`, `reuse.png` and
  `pip_vs_tensile.png`.
- `out/twin2/thumbs/{psd,tensile,pip,hardness,corrosion,yield}.png`: 512×512 on a transparent background, checked
  for legibility at 120 px on light and dark backgrounds.

## Limits

- PIP's forward model is analytical (Tabor, Johnson, Hill), not FEM. It sees no anisotropic, non-axisymmetric
  profiles, only their mean effect.
- The fracture model has one weakest section per bar and no fatigue or strain-rate effects. Pore size distributions
  are assumed, not taken from the truth.
- The hot test reuses the RT fracture model with the truth's 250 °C elongation.
- PSD has no true Mie series and uses one wavelength.
- Sieve, flow, crucible and reuse constants are untested against the lab's data. Reuse does not change composition.
- Corrosion uses seawater kinetics in every electrolyte, with no galvanic coupling, flow or sulfide. The film is a
  single time constant.
- The fast modes interpolate the calibration table. A state far outside the 168 calibration parts falls back to
  the linear part.
- `SPEC` layouts differ by module (hardness and corrosion hold one entry per method). `facility.py` and `econ.py`
  should read them per instrument.
- `campaign.py` (another agent's file) calls these through `instruments.measure` at the spec's `fidelity`, plus
  `atomize_yield.charge_plan` and `reuse`. Short campaigns ran clean at lite and fast with both crucibles (120 days,
  seed 1), and test_twin's budget and reproducibility tests pass.
