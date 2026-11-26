# Instrument simulators, round 2: microscopy, diffraction and chemistry

Part of PR 318's second round of the twin (`twin/instruments/`, contract in `twin/instruments/__init__.py`). Each
module here turns an artifact's hidden state into the raw data a real instrument records (a pattern, a micrograph, a
spectrum, an orientation map), then runs on that raw data the analysis a lab would run. The numbers it reports carry
the detection limits, overlaps, sampling biases and correlations of that chain. They are not the truth plus Gaussian
noise. Every number we chose ourselves is marked *assumed*.

| instrument key | module.function | outputs | station (SPEC) |
|---|---|---|---|
| `xrd_powder` | `xrd.measure_powder` | phases, a_fcc_A, solute_ss_wt, crystallite_nm | `xrd` (Rigaku MiniFlex; not yet a station in `facility.py`) |
| `xrd_part` | `xrd.measure_part` | phases, a_fcc_A, beta_prime_frac (Cu), microstrain | `xrd` + `prep` |
| `sem_powder` | `sem.measure_powder` | sphericity, satellite_frac, d50_img_um, n_particles | `byu_sem` |
| `sem_section` | `sem.measure_section` | porosity, pore_dmax_um, crack_density, lof_frac | `byu_sem` + `prep` |
| `eds` | `eds.measure` | comp (wt%, balance element excluded), lod | `byu_sem` |
| `ebsd` | `ebsd.measure` | grain_um, equiaxed_frac, texture_mrd, indexed_frac, kam_deg, beta_prime_frac (Cu) | `byu_sem` + `prep` |
| `xrf` | `xrf.measure` | comp | `psd` (Mastersizer + XRF station; Bruker S2 PUMA) |
| `icpms` | `icpms.measure` | comp | `byu_icpms` |

There are three fidelities, all deterministic given `rng`:

* **`full`**: publication-size raw data (0.01 deg XRD steps, 1024 px micrographs, 10 eV EDS channels, maps of
  ~400x300 points), the real analysis, and `raw` in the result for figures.
* **`lite`**: small raw data (0.04 deg, 128-256 px, 20 eV, ~64x64-100x80 points) and the same analysis, under 30 ms a
  call.
* **`fast`**: under 1 ms. It samples the analysis errors from distributions fitted to the lite chain, as functions
  of the sample's state.

The fitted parameters are in `twin/instruments/calib_micro.json`.

`raw` carries only what the instrument recorded and what the analysis derived from it. The latent state used to make
it stays out of the result unless the caller passes `with_truth=True`, which the gallery figures do for their
annotations. The latent state means the true phases, the drawn pores, cracks and particles, noise-free spectra,
digest recoveries, and the sample displacement. A test checks this.

## Run it

```bash
cd vertical-lab
export OPENBLAS_NUM_THREADS=1      # these fits are small; multi-threaded OpenBLAS costs more than it saves
nice -n 10 /tmp/venv/bin/python -m pytest -q twin/tests/test_instruments_micro.py      # 52 checks, 15-40 s (< 60 s on a loaded runner)
nice -n 10 /tmp/venv/bin/python -m twin.instruments.calibrate_micro                    # refit every fast mode (~2-4 min)
nice -n 10 /tmp/venv/bin/python -m twin.instruments.calibrate_micro xrd                # or one module
nice -n 10 /tmp/venv/bin/python -m twin.instruments.calibrate_micro --table 40         # fast vs lite, gallery alloys
nice -n 10 /tmp/venv/bin/python -m twin.instruments.gallery_micro                      # figures and DAG icons
```

`gallery_micro` writes the following. The samples are AlSi10Mg, Scalmalloy and an uninoculated 7075 for FLAIME, and
70-30 Cu-Ni and NAB for ONR. Each lot and part is made through the truth the way `reference_table()` makes them
(`micro.gallery_samples`).

* One PNG per instrument in `out/twin2/instruments/`: `xrd.png`, `sem_powder.png`, `sem_section.png`, `eds.png`,
  `ebsd.png`, `kikuchi.png`, `xrf.png`, `icpms.png`.
* 512x512 transparent icons in `out/twin2/thumbs/`: `sem_powder`, `sem_section`, `eds`, `ebsd`, `kikuchi`, `xrd`,
  `xrf`. They read at 120 px on both light and dark backgrounds.

Use from code: `from twin.instruments import measure; measure("xrd_part", part, "onr_cu", rng, fidelity="lite")`.
`micro.make_samples(campaign, design, proc)` builds a (lot, part) pair through the truth, and
`micro.random_samples(campaign, n)` builds representative ones across each space and process window.

## The shared latent microstructure (`twin/instruments/micro.py`)

`phase_model(sample, campaign, kind)` turns a lot (`kind="powder"`) or a part (`"part"`) into the following:

* **Phases**: weight and volume fractions, composition, structure (space group and atom positions, or a cell for
  complex phases), lattice parameters, crystallite size, microstrain, morphology, mean Z, the backscatter
  coefficient and density.
* **The FCC matrix**: the solute it holds in solution and its Vegard lattice parameter.
* **Parts only**: pore populations by type, cracks and grains.
* **Lots only**: the sieved powder's size populations, per atomizer run.

Every instrument reads this state and nothing else from the truth. The state is a deterministic function of the
truth's own variables:

* composition and `thermo` (`eutectic_by`, `primary`, `nucleant_wt`, `beta_900`, `kappa_700`)
* the part's `cell_um`, `grain_um`, `equiaxed`, `beta_prime`, `temper`, `cooling_K_s` / `melt_pool`, `pores`,
  `crack_density`
* the lot's atomizer runs (`d50_um`, `gsd`, `true_superheat_K`, `undissolved`)

**Aluminium.** Phases are placed in this order:

1. **Primary intermetallics** form above the invariant composition (`thermo.AL_PRIMARY`). LPBF keeps 70 % of the
   excess in solution, as `truth_al.strength` does. A droplet keeps 70 % times its retention fraction (*assumed*).
   When both Sc and Zr are present this gives Al3(Sc,Zr), L1_2.
2. **The matrix** keeps what the cooling rate retains: `truth_al.RETAIN` for LPBF. For an atomized droplet it is
   interpolated in log cooling rate between equilibrium solubilities and RETAIN (*assumed*). The droplet cooling rate
   is Newtonian cooling in argon, `6 h dT / (rho c d)` with Nu ~ 4 (*assumed*; 3e4-1e5 K/s for 40-90 um droplets).
3. **The eutectic / cell network** takes the rest, element by element. The phases are Si, Al2Cu, Mg2Si (when Mg
   and Si are both present), MgZn2, Al6(Mn,Fe), Al13Fe4, Al3Ni, Al11Ce3, Al3Sc, Al3Er, AlLi and Sn.
4. **Parts** are characterized in the condition `truth_al.strength` describes. The L1_2 precipitates hold 80 % of
   the Sc/Zr/Er in solution, about 5 nm. Ageing precipitates (Mg2Si, Al2Cu, MgZn2, Al3Li) take what `strength()`
   puts into `f_age`, at 6-40 nm.
5. **Powders only**: a melt set below the true liquidus entrains 10 % of the undissolved Zr/Ti/Sc/Cr/Er as coarse
   D0_23 Al3Zr, D0_22 Al3Ti and so on (*assumed*). These are in `pm["extra"]`, and the chemistry modules add them
   back.

AlSi10Mg comes out with 8 % eutectic Si, 2.1 wt% Si in solution and a = 4.0467 A, against the 4.045-4.047 A
reported for as-built LPBF AlSi10Mg (Li et al., Acta Mater. 105, 2016, 25,
https://doi.org/10.1016/j.actamat.2015.10.044). Scalmalloy comes out at 4.061 A, its Mg expanding the lattice.

**Copper.**

* **beta'** is the truth's `beta_prime` for parts. For powders it is `beta_900 x truth_cu._retain(droplet cooling
  rate)`, which makes atomized NAB about 60 % martensite, as gas-atomized NAB powders are.
* **kappa** for parts is `kappa_700 x (0.5 + temper)`, as in `truth_cu.strength`. A droplet gets 10 % of
  `kappa_700` (*assumed*).
* **The kappa split** is by Fe:Ni (*assumed*): Fe-rich kappa_II (DO3 Fe3Al-type rosettes) and kappa_IV (fine BCC),
  and Ni-rich lamellar kappa_III (B2 NiAl). Each is capped at 85 % of what is left of its formers. The phase
  identities follow Hasan, Lorimer & Ridley, J. Phys. IV 43 (1982) C4-653 and Culpan & Rose, J. Mater. Sci. 13 (1978)
  1647.
* **Cu-Ni family**: delta-Ni2Si, delta-Ni3Nb, eta-Ni3Ti, BCC Cr and BCC Fe precipitate above solubility limits that
  are *assumed* (Si 0.05, Nb 0.1, Ti 0.15 + 0.01 Ni, Cr 0.15, Fe 2.3 + 0.3 Al wt%), 70 % of the excess in a
  tempered deposit and 30 % in a droplet.
* **The alpha matrix** gets the remainder, by mass balance. 70-30 Cu-Ni comes out at a = 3.5884 A, against C71500's
  handbook 3.586-3.590 A. NAB's alpha comes out at 3.647 A.

**Vegard coefficients** (A per at.% in solution, `micro.VEGARD`). For Al these are Mg +0.0045, Cu -0.0051,
Si -0.0017, Zn -0.0007, Li -0.0010 and Mn -0.0090. The sources are the lattice-parameter compilations in Hatch (ed.),
*Aluminum: Properties and Physical Metallurgy* (ASM 1984), ch. 1, and King, J. Mater. Sci. 1 (1966) 79
(https://doi.org/10.1007/BF00549722). Cr, Fe, Ni, Ti, Zr, Sc, Er, Ce and Sn are *assumed*: the sign and size are
from King's size factors, and their solubility is small, so they matter little. For Cu, Cu-Ni follows Vegard
between 3.6149 and 3.5240 A, and Al +0.0022, Mn +0.0029 and Fe +0.0009 are from Pearson's *Handbook of Lattice
Spacings*. Cr, Si, Nb and Ti are *assumed*.

**Structures** (`micro.STRUCTURES`). Atom positions are carried for these:

* FCC A1
* diamond Si
* the L1_2 phases: Al3Sc, Al3Zr (metastable), Al3Er, Al3Li, Al3(Sc,Zr)
* D0_23 Al3Zr and D0_22 Al3Ti
* Mg2Si (C1)
* theta-Al2Cu (C16, x = 0.1581)
* MgZn2 (C14)
* AlLi (B32) and beta-Sn
* beta' (on its DO3 beta1 parent, a = 5.84 A, with martensitic broadening; *assumed*, since the real 9R/3R cells
  split these lines)
* kappa_II (DO3), kappa_III (B2), kappa_IV, Cr and Fe (A2)

These complex cells carry their true cells and centring: Al6(Mn,Fe), Al13Fe4, Al45Cr7, Al11Ce3, Al3Ni, Al3Mg2,
delta-Ni2Si, delta-Ni3Nb and eta-Ni3Ti. Their intensities are drawn once per phase (seeded by name) from Wilson
statistics, <|F|^2> = sum f_j^2 (Wilson, Acta Cryst. 2, 1949, 318). This is *assumed*. Their line positions, number
of lines and intensity fall-off are right; the individual intensities are not.

**Pores, cracks, grains.**

* **Pore types** follow the truth's `pores` {lof, keyhole, gas} volume fractions, each with a lognormal size (the
  equivalent sphere diameter, Cunningham et al., Science 363 (2019) 849, https://doi.org/10.1126/science.aav4687;
  Snell et al., JOM 72 (2020) 101):
  * lack of fusion: median 70 um, scaled up by the truth's LoF index (50-300 um), GSD 1.55, aspect 2.6, irregular
  * keyhole: 0.35 of the melt-pool depth (20-100 um), GSD 1.35, near-spherical
  * gas: 12 um (Al) or 18 um (Cu), GSD 1.45
  * all medians, GSDs and shapes are *assumed*
* **Number densities** come from the volume fraction and the lognormal third moment.
* **Hot cracks** have the truth's `crack_density` (mm/mm2). Their length is 60 + 4 x grain_um (median, GSD 1.6) and
  their opening 1.5 um. They run along columnar grain boundaries, parallel to the build direction (Martin et al.,
  Nature 549 (2017) 365, https://doi.org/10.1038/nature23894). Lengths and opening are *assumed*.
* **Grains**:
  * Al: `grain_um`, equiaxed share = the truth's `equiaxed`, columnar aspect 4, <100> fiber spread 14 deg.
  * Cu: equiaxed share = 0.08 + 0.55 temper + 0.12 Fe/4, aspect 5, spread 18 deg.
  * Baseline KAM: 0.55-0.7 deg for Al; 0.45 + 1.2 beta' deg for Cu.
  * All of these are *assumed*.

The phase model conserves mass to within its rounding (`test_phase_model_balances`). It runs in 0.2-0.4 ms and is
cached per sample.

## XRD (`twin/instruments/xrd.py`)

**What it models.** A Rigaku MiniFlex 600 with a D/teX Ultra detector, Bragg-Brentano geometry and a 150 mm
goniometer, scanning Cu K-alpha1/alpha2 over 2theta 10-100 deg. Full scans are 0.01 deg steps at 2 deg/min (0.3 s per
step); lite scans are 0.04 deg at 10 deg/min. Every phase of the latent microstructure contributes reflections.

* **Structure factors** are kinematic: F = sum_j f_j(s) exp(2 pi i h.r_j). Site occupancies come from the phase
  composition (the FCC site is the matrix's own solid solution).
  * Form factors: Cromer-Mann (International Tables for Crystallography Vol. C, Table 6.1.1.4). The coefficient
    table covers Li, C, O, Mg, Al, Si, Sc, Ti, Cr, Mn, Fe, Ni, Cu, Zn, Zr, Nb, Sn and Ce. Er is Gd's coefficients
    scaled to Z = 68 (*assumed*).
  * Anomalous terms f', f'' at Cu K-alpha: Sasaki 1989 / Henke et al. 1993 (https://henke.lbl.gov/optical_constants/),
    approximate.
  * Isotropic Debye-Waller factor, with B per phase (*assumed*, 0.3-1.5 A^2).
  * Reflections are grouped by d-spacing through Gram matrices of the sites' geometric factors, so the same cached
    list serves any occupancy.
* **Intensity**: (w_p / rho_p) m |F|^2 / V^2 x LP with LP = (1 + cos^2 2theta) / (sin^2 theta cos theta). This is
  the mass-absorption form of the Rietveld scale, as in Hill & Howard, J. Appl. Cryst. 20 (1987) 467. The absolute
  scale goes through the mixture's mass attenuation coefficient. Pure Al powder's (111) peak is 2e4 counts/s
  (*assumed*).
* **Profiles**: pseudo-Voigt with Thompson-Cox-Hastings mixing (J. Appl. Cryst. 20, 1987, 79).
  * Instrument width from Caglioti H^2 = U tan^2 + V tan + W (Nucl. Instrum. 3, 1958, 223), with U, V, W =
    0.010, -0.003, 0.004 deg^2 (*assumed*; FWHM 0.065 deg at 40 deg, 0.105 deg at 90 deg).
  * Scherrer size broadening (K = 0.9, Lorentzian) and microstrain broadening (4 eps tan theta, Gaussian).
  * K-alpha2 at half of K-alpha1, wavelengths 1.540593 / 1.544414 A (Hoelzer et al., Phys. Rev. A 56, 1997, 4554).
* **Preferred orientation** of parts: March-Dollase about <100> normal to the measured build plane (Dollase,
  J. Appl. Cryst. 19, 1986, 267), with r = 1 - 0.35 x the columnar share (*assumed*).
* **Peak shifts**:
  * sample displacement, d2theta = -2 s cos theta / R, with s ~ N(0, 50 um) for a packed powder holder and
    N(0, 25 um) for a mounted part (*assumed*)
  * a zero error ~ N(0, 0.005 deg) (*assumed*)
  * each intermetallic's cell differs from the handbook's by ±0.1 % (*assumed*), fixed per sample
* **Background**: a Chebyshev polynomial (air scatter falling with angle, a flat Compton term) plus Fe/Mn/Cr
  fluorescence under Cu radiation. Powders add an amorphous hump at 21.5 deg from the holder. Magnitudes are
  *assumed*, set for a peak-to-background of about 100 on Al(111).
* **Counts**: Poisson for the dwell time per step.

**Analysis.**

1. **Background**: a Chebyshev polynomial (plus the hump term for powders), fitted by iteratively clipped least
   squares.
2. **FCC peak positions**:
   * The analyst predicts the positions from the design (Vegard, all solute in solution).
   * The nearest significant peak (prominence > 5 sigma) within 0.6 deg is indexed, lowest angle first, and the
     estimate is updated after each fit. This matters for NAB powder, where beta'(220) sits 0.8 deg from alpha(111).
   * Each indexed peak gets a pseudo-Voigt + K-alpha2 + linear-background fit (Levenberg-Marquardt).
3. **a_fcc** comes from least squares of a_hkl on cos^2 theta / sin theta, which corrects for the displacement.
4. **Williamson-Hall** (beta cos theta = K lambda / L + 4 eps sin theta) runs on the fitted widths, with the
   instrument removed in quadrature. A non-positive intercept reports 1000 nm, the method's ceiling.
5. **"Rietveld-lite"**: bounded least squares of the whole pattern against reference patterns of the candidate
   phases plus the Chebyshev background (normal equations, then BVLS on the Cholesky factor).
   * Candidates are the phases the design's chemistry allows.
   * The references use handbook cells. The matrix uses the refined a and the W-H broadening, and a March-Dollase r
     refined on a grid (0.55-1.15) for parts.
   * Weight fractions come from the scales, since the references are per unit weight fraction (the ZMV relation).
   * A phase is reported only if its scale exceeds 3 standard errors (the covariance scaled by the reduced
     chi-square).
6. **`solute_ss_wt`**: inverse Vegard, assuming the solutes sit in the matrix in the design's proportions.
   * For a single dominant solute (Cu-Ni, Al-Mg, Al-Cu) this is fair.
   * It is ambiguous for multi-solute alloys, because Mg expands Al while Si, Cu and Mn contract it. AlSi10Mg powder
     with 1.85 % Si and 0.34 % Mg in solution reads 0.95 % "design-proportioned solute".
   * It is None when the solutes' effects cancel (|da/dc| < 4e-4 A per wt%).
   * Where the sample has no `design`, a rounded composition stands in for it (*assumed*).

**What emerges.**

* **Lattice parameter**: within 1-3e-4 A of the true matrix value (lite) at these displacements.
* **Detection limits**: the weight fraction at which a phase is detected in half the draws, fitted from the lite
  chain over the calibration set (`calib_micro.json`, `xrd_part`):
  * 0.5-1.5 wt% for phases with strong, separate lines: Al2Cu 0.8, Mg2Si 1.4, eutectic Si 1.1, Al6(Mn,Fe) 0.8,
    primary L1_2 Al3Zr 0.45. The 0.22 wt% Mg2Si in AlSi10Mg is not detected.
  * 2-3.5 wt% for complex low-symmetry cells, whose intensity is spread over many weak lines: Al45Cr7 3.5, Al3Ni 2.8.
  * 2.5 wt% for kappa_III in NAB, which sits under alpha and kappa_II.
  * 2.2 wt% for nanometre L1_2 Al3Sc precipitates.
* **L1_2 Al3(Sc,Zr)**: its fundamental lines coincide with Al's, so only the weak superlattice lines identify it.
  Scalmalloy's 1.3 % of 5 nm Al3Sc precipitates is invisible, while 0.5 % of coarse primary Al3(Sc,Zr) is detected
  at about 1 % (over-estimated).
* **Nano-precipitates** (MgZn2 at 6 nm) read low because their lines are broader than the reference's.
* **Texture**: shows up as a strong (200).
* **Displacement**: shifts every line, and is removed by the cos^2/sin fit.

**Known limits.**

* The intermetallic cells are not refined, and there is no microabsorption (Brindley) correction.
* Wilson intensities stand in for complex phases (see above).
* beta' is its cubic parent, so the 9R splitting is absent.
* There is a single measured face, perpendicular to the build direction.
* The fast mode treats per-phase detection as independent of the other phases present. Overlap-driven misses
  appear only on average.
* A beta'-dominated NAB powder reads a crystallite size at the 1000 nm cap. The fast mode reproduces this (94 % of
  draws).

## Calibration of the fast modes: fast vs lite on the gallery alloys

**Method.** Each module's `calibrate()` runs its lite chain over the same set of samples:

* random feasible designs from `twin.spaces` (24-60 per campaign, depending on the module), with process settings
  drawn from the design;
* a quarter of the atomizer melts set 60 K below the true liquidus, so undissolved additions are entrained;
* the three DED modes for Cu;
* the gallery alloys.

It then fits its error model and writes it to `calib_micro.json`. The error models are:

* **XRD**:
  * a_fcc bias: constant plus a beta' term
  * a_fcc spread: robust
  * per phase, a logistic detection curve in log10(wt), with the log-ratio bias and spread of detected fractions
  * a false-positive rate
  * crystallite: log-ratio regression, plus the probability of reading the cap (by beta' share)
  * microstrain ratio
  * beta' line: linear in the true beta' with a kappa interaction, its residual split into a persistent
    per-sample part and a per-measurement part
* **SEM, EBSD, EDS, XRF, ICP-MS**: see their sections below.

**Results.** The [calibration table](#calibration-table-fast-vs-lite-40-draws-each-gallery-alloys) near the end shows each output over 40 draws of each fidelity, from
`python -m twin.instruments.calibrate_micro --table 40`. The full table, with every output and element, is in
`out/twin2/instruments/calib_micro_table.md`. z is (fast - lite) / standard error.

* **Agreement**: of the 127 rows in the table at the end, 97 are within 2 standard errors and 111 within 3.
* **Large z with tiny absolute differences**: the largest z are all XRF, whose spread is a few hundredths of a
  percent of the value. The relative differences are at most 1.8 %, except Fe in 70-30 Cu-Ni powder: -5.6 %
  (lite -3 % from the truth, fast -8.5 %).
* **XRD beta'**: the fast model splits its error into a persistent per-sample offset (overlap with kappa, texture;
  seeded by the sample) and a per-measurement part, so a sample's repeat measurements scatter as in lite. For NAB,
  lite reads 0.294 ± 0.004 and fast 0.293 ± 0.004.
* **Other remaining gaps**:
  * EDS Zr in Scalmalloy, near its LOD: detected in about 50 % of lite draws and 38 % of fast.
  * EBSD Scalmalloy texture_mrd: skewed near random.
  * XRD microstrain in NAB: fast 13 % lower.

The fast models fit across the whole space, not per alloy, so a sample's own quirks average out.

## SEM (`twin/instruments/sem.py`): powder (SE) and polished sections (BSE)

**What it models.** A Hitachi TM4000-class desktop SEM at 15 kV.

*Powder* (`measure_powder` -> `sphericity`, `satellite_frac`, `d50_img_um`, `n_particles`). The lot's sieved cut
(`micro.powder_population`: one lognormal per good atomizer run, volume median `d50_um`, geometric SD `gsd`, cut
20-63 um Al / 45-150 um Cu, 4 % by mass leaking through the sieves) is dispersed on carbon tape as a monolayer at
35 % area coverage (assumed) by random sequential placement that lets neighbours touch but not overlap by more than
6 % of the radius sum (assumed). Particles are spheres; the share of the melt that ran cold (`irregular`, logistic in
the run's `true_superheat_K`, from micro) are elongated, lumpy ligaments (aspect lognormal about 1.9, assumed); a
share `satellite_frac` of particles carries 1 + Poisson(0.6) satellites of 0.05-0.35 of the host radius at random
elevations -10..60 deg (assumed). A height map gives the surface tilt; the SE yield follows the secant of the tilt
(edge effect, capped at 8; Goldstein et al., *Scanning Electron Microscopy and X-Ray Microanalysis*, 4th ed. 2018,
ch. 3, https://doi.org/10.1007/978-1-4939-6676-9), the Everhart-Thornley detector side is brighter, the tape behind a
particle is shadowed (collector field shortens shadows: 45 deg, assumed), tape SE yield 0.06 vs Al 0.16 / Cu 0.20
(effective yield x collection, assumed), 600 primary electrons per pixel (e.g. 50 pA x 2 us, assumed), Poisson shot
noise. Analysis: Gaussian smoothing (1 px), a threshold 5 sigma above the tape's histogram peak (half-width at half
maximum; Otsu's method, https://doi.org/10.1109/TSMC.1979.4310076, splits particle faces from their bright edges on
SE images, so it is not used), hole filling, Euclidean distance transform and marker-controlled watershed
(Beucher & Meyer 1993; scikit-image, https://scikit-image.org/docs/stable/api/skimage.segmentation.html#watershed)
to split touching particles, border-touching particles excluded (the classic size bias against large particles),
equivalent circle diameters weighted by volume (d^3) for the d50, circularity 4 pi A / P^2 with the perimeter from
crack-edge counts x pi/4 (unbiased for random boundary orientation), satellites as the residue of a disk opening
(radius 0.22 of the median particle radius) still attached to exactly one particle (necks between two touching
particles belong to two labels and are rejected).

*Section* (`measure_section` -> `porosity`, `pore_dmax_um`, `crack_density` (mm/mm2, 0.0 when none found),
`lof_frac`). A vertical section (build direction up) through the part's pore and crack populations
(`micro.phase_model(..., 'part')`). Pores are sampled in 3-D and cut by the plane: per type, the expected number
crossing the field is n_V x area x mean caliper (DeHoff & Rhines, *Quantitative Microscopy*, 1968; Underwood,
*Quantitative Stereology*, 1970), sizes are size-biased by the caliper, the cut height is uniform, so the section
circle is smaller than the pore's diameter; lack-of-fusion pores are irregular oblate spheroids lying in the layers
(aspect 2.6 from micro, six random Fourier modes of the outline with amplitude ~0.45 x irregularity, assumed),
keyhole and gas pores are spheres (Cunningham et al., Science 363 (2019) 849,
https://doi.org/10.1126/science.aav4687; Snell et al., JOM 72 (2020) 101, https://doi.org/10.1007/s11837-019-03761-9).
Hot cracks are tortuous traces up the build direction (steps of 0.8 grain width, 0.25 rad wander, assumed) with
lognormal lengths and openings about `open_um` = 1.5 um from micro (Martin et al., Nature 549 (2017) 365,
https://doi.org/10.1038/nature23894); a crack narrower than a pixel darkens it by the share it covers (partial
volume). Phases contribute by their backscatter coefficient (Reuter's fit via `micro.bse_eta`): resolved by a
thresholded random field when larger than 1.5 px (beta' colonies at the grain size, assumed), averaged into the
pixel otherwise; pore interiors 12 % of the matrix signal (assumed); 2 polishing scratches per mm2, 2-5 % darker
(assumed); 1000 primary electrons per pixel and 60 % BSE collection (assumed), Poisson noise. Analysis: pores
below half the matrix level after 0.8 px smoothing; thin dark features by a black top-hat (1 x 5 px closing) across
the build direction after smoothing along it, against the Poisson noise of the matrix level (4.5 sigma); connected
components of the union with elongation >= 4, width <= 3.5 px and length >= 6 px are cracks (skeleton length,
orthogonal links 1, diagonal sqrt 2, + 1 px per trace); the remaining threshold mask gives pores (>= 2 px), called
lack of fusion when >= 12 px with circularity < 0.55 or elongation > 2.2 (assumed cut-offs, after the shape-factor
practice in Snell 2020); porosity = (pore + crack area) / field.

**Field of view vs pixel (part of the physics).** Powder: full 1024 px at 1 (Al) / 2 (Cu) um/px (1.0 / 2.0 mm
fields, 200-470 particles); lite 192 px at twice the pixel (0.38 / 0.77 mm, 20-50 particles). Section: full
1024 px at 2 um/px (2.0 mm, 4.2 mm2, a 2 x 2 mosaic of 512 px frames); lite 256 px at 4 um/px (1.0 mm, 1.05 mm2).
What emerges: gas pores under ~2.5 px (10 um at lite) vanish and small detected pores lose half their area to the
blur (detection 16 % at 2-2.5 px, 90 % at 2.5-3 px; area ratio 0.43-0.65 below 4 px, 0.9-1.0 above 7.5 px); the
largest pore in a 2-D field underestimates the largest pore in 3-D; one field's porosity scatters with the handful of
large lack-of-fusion pores it happens to hold (sd/mean 0.6-0.8 for the Cu deposits, lite); 1.5 um cracks at 4 um
pixels are found in pieces (recovered share of a trace is logistic in opening/pixel with midpoint
0.27), so lite reads 7075's 1.88 mm/mm2 as about 1.3 while full (2 um pixels) reads about 1.9;
outline-based satellite counting misses most satellites at these magnifications (true 0.07, lite 0.005-0.014,
full 0.01-0.06), more so for Cu at 4 um/px; the volume-weighted d50 of a few dozen particles reads 7-12 % above the
cut's true volume median (touching pairs the watershed leaves merged, leaked oversize particles), with a heavy upper
tail.

**Fast mode.** Powder: per campaign, linear regressions of the lite chain's log(d50_img / cut dv50), sphericity,
satellite share and log(n) on (1, irregular share, satellite share, ln(dv50/50)), with residual spread (satellite
spread binomial in the particle count x 0.99). Al coefficients: d50 [0.0819, -0.101, -0.0884, 0.351], sd
0.070; sphericity [0.987, -0.142, -0.0141, 0.00697], sd 0.015; satellites
[-0.00295, 0.0724, 0.15, 0.0311]. Cu: d50 [0.24, -0.0639, 0.028, -0.325], sd 0.089; sphericity
[0.972, -0.0952, -0.0105, 0.0192], sd 0.011; satellites [0.0262, 0.0724, 0.0191, -0.0397]. Section: the same
stereological sampler as the image (so the field-to-field scatter and the cut's size bias are exact, not fitted),
then transfer tables measured on 10526 pores and 1675 cracks matched object by object between the
truth and the lite analysis: detection probability, median measured/true area and its log-sd, and the probability of
being called lack of fusion, by true class (round / LoF) and section diameter in pixels (bins
[0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.5, 7.5, 10.0, 14.0, 20.0, 30.0, 50.0]); crack recovery logistic in opening/pixel (midpoint 0.274, width 0.276),
skeleton/trace length ratio 1.030 (log-sd 0.089), 5.36 um2 of crack area per um of
length, and false cracks (scratches, pore chains) in 21 % of crack-free lite fields, ~40 um
each (so a crack-free part reads 0.02-0.04 mm/mm2 on average, under the 0.05 crack-free cut). Detection table
(round): 0.0381, 0.0413, 0.0564, 0.162, 0.904, 0.99, 0.992, 0.996, 0.997, 1, 1, 1, 1, 1; area ratio (round): 0.429, 0.429, 0.429, 0.429, 0.455, 0.644, 0.766, 0.847, 0.898, 0.933, 0.956, 0.972, 0.982, 1.01; P(LoF | LoF): 0, 0, 0, 0, 0, 0, 0.2, 0.714, 0.773, 0.936, 0.85, 0.827, 0.819, 0.678.
Calibrated with `python -m twin.instruments.sem 40 8` (40 random designs per campaign through the truth with random
process settings, a quarter of the melts set 60 K cold, plus the gallery alloys, 8 lite repeats each; ~20 s).

**Fast vs lite on the gallery alloys (60 draws each, same seed).**

| alloy | output | truth | lite mean ± sd | fast mean ± sd |
|---|---|---|---|---|
| AlSi10Mg | d50_img_um | 50.34 | 55.27 ± 9.7 | 54.36 ± 3.2 |
| AlSi10Mg | sphericity |  | 0.9827 ± 0.0088 | 0.9795 ± 0.014 |
| AlSi10Mg | satellite_frac | 0.07 | 0.01038 ± 0.023 | 0.01658 ± 0.016 |
| AlSi10Mg | n_particles |  | 20.93 ± 4.7 | 22.13 ± 5.2 |
| Scalmalloy | d50_img_um | 50.71 | 53.89 ± 4.1 | 54.58 ± 3.1 |
| Scalmalloy | sphericity |  | 0.9845 ± 0.011 | 0.9785 ± 0.013 |
| Scalmalloy | satellite_frac | 0.07 | 0.004844 ± 0.016 | 0.01821 ± 0.017 |
| Scalmalloy | n_particles |  | 21.07 ± 4.2 | 20.87 ± 5.3 |
| 7075 | d50_img_um | 50.41 | 54.8 ± 7.3 | 54.48 ± 3.2 |
| 7075 | sphericity |  | 0.983 ± 0.011 | 0.9794 ± 0.014 |
| 7075 | satellite_frac | 0.07 | 0.007836 ± 0.018 | 0.01465 ± 0.015 |
| 7075 | n_particles |  | 22.78 ± 5.2 | 21.87 ± 5 |
| 70-30 Cu-Ni | d50_img_um | 73.5 | 81.93 ± 7 | 81.91 ± 6.3 |
| 70-30 Cu-Ni | sphericity |  | 0.9741 ± 0.0095 | 0.9752 ± 0.01 |
| 70-30 Cu-Ni | satellite_frac | 0.07 | 0.01365 ± 0.017 | 0.01804 ± 0.015 |
| 70-30 Cu-Ni | n_particles |  | 51.52 ± 6.4 | 50.92 ± 6.6 |
| NAB | d50_img_um | 74.91 | 83.98 ± 6.2 | 83.75 ± 6.2 |
| NAB | sphericity |  | 0.9737 ± 0.01 | 0.9743 ± 0.01 |
| NAB | satellite_frac | 0.07 | 0.007826 ± 0.012 | 0.01796 ± 0.015 |
| NAB | n_particles |  | 50.23 ± 5.9 | 50.03 ± 7.7 |
| AlSi10Mg | porosity | 0.004363 | 0.00375 ± 0.0027 | 0.003335 ± 0.0022 |
| AlSi10Mg | pore_dmax_um |  | 45.25 ± 20 | 41.94 ± 16 |
| AlSi10Mg | crack_density | 0.02572 | 0.02284 ± 0.044 | 0.0402 ± 0.069 |
| AlSi10Mg | lof_frac | 0.0961 | 0.05759 ± 0.16 | 0.04498 ± 0.16 |
| Scalmalloy | porosity | 0.005477 | 0.004426 ± 0.0025 | 0.005111 ± 0.004 |
| Scalmalloy | pore_dmax_um |  | 48.64 ± 18 | 49.83 ± 25 |
| Scalmalloy | crack_density | 0.03332 | 0.03026 ± 0.037 | 0.03297 ± 0.046 |
| Scalmalloy | lof_frac | 0.1491 | 0.08618 ± 0.21 | 0.1043 ± 0.22 |
| 7075 | porosity | 0.01748 | 0.01596 ± 0.0048 | 0.01607 ± 0.0049 |
| 7075 | pore_dmax_um |  | 59.25 ± 21 | 57.44 ± 20 |
| 7075 | crack_density | 1.878 | 1.336 ± 0.41 | 1.373 ± 0.4 |
| 7075 | lof_frac | 0.06204 | 0.0495 ± 0.14 | 0.0679 ± 0.17 |
| 70-30 Cu-Ni | porosity | 0.0561 | 0.05271 ± 0.034 | 0.05868 ± 0.037 |
| 70-30 Cu-Ni | pore_dmax_um |  | 164.1 ± 61 | 164.2 ± 55 |
| 70-30 Cu-Ni | crack_density | 0.02901 | 0.03178 ± 0.059 | 0.03195 ± 0.055 |
| 70-30 Cu-Ni | lof_frac | 0.9468 | 0.7255 ± 0.29 | 0.7254 ± 0.23 |
| NAB | porosity | 0.02941 | 0.03007 ± 0.025 | 0.02814 ± 0.022 |
| NAB | pore_dmax_um |  | 138.6 ± 66 | 122.4 ± 55 |
| NAB | crack_density | 0.01307 | 0.02101 ± 0.046 | 0.02152 ± 0.059 |
| NAB | lof_frac | 0.9002 | 0.6502 ± 0.34 | 0.6788 ± 0.24 |

Porosity, LoF share and the largest pore are heavy-tailed (a few large lack-of-fusion pores per field), so a test
of fast vs lite should allow ~3 standard errors (sd x sqrt(2/n)) rather than a fixed relative tolerance; 150-draw
checks on 70-30 and NAB agree to within 1 SE for porosity, dmax and LoF share.

**Timings** (CPU per call on the shared runner, single thread): fast powder 0.05-0.07 ms, fast section 0.15-0.8 ms;
lite powder 12.6 ms (max 13.7), lite section 12.6 ms (max 15.7) (wall time was up to 2-3x higher at load average
10); full powder 0.46 s, full section 0.24 s.

**Known limits.** Particles are spheres or smooth ligaments, not the splats, flakes and hollow particles of a real
ultrasonic-atomized lot; satellites are only counted from outlines (a satellite on top of its host is invisible to
the analysis, as with a threshold-only method in practice); no charging, contamination or tilt; the section's phase
contrast is coarse (sub-pixel phases are averaged, colony-scale beta' is a thresholded random field) and grain
channelling contrast is omitted; LoF pores are smooth-edged and contain no unmelted particles; cracks are only
along the build direction (no solidification cracks across a layer, no delamination); the crack-vs-pore split is by
shape alone, so a crack touching a pore can be absorbed into the pore. Fast mode reproduces the lite chain (2 um/px
powder, 4 um/px sections), not full: full resolves more satellites, small pores and thin cracks.

## Chemistry: EDS, XRF, ICP-MS (`twin/instruments/eds.py`, `xrf.py`, `icpms.py`)

All three read the latent state from `micro.phase_model` (the lot's or part's composition, plus the coarse
intermetallic a cold melt entrains into a powder; the phases each element sits in; the lot's oxygen), simulate the
raw data, and run the analysis a lab would run on it. Nothing from the truth enters a result except through that
chain. `fast` draws from error models fitted to the `lite` chain (`calibrate()` in each module; parameters in
`twin/instruments/calib_micro.json` under `eds`, `xrf`, `icpms`; rerun with
`python -m twin.instruments.eds` etc.).

### EDS (desktop SEM, 15 kV, 30 mm2 SDD, 60 s live, about 1 nA)

**Forward model.** Characteristic generation from Bethe's ionization cross-section integrated over the electron's
slowing down (Bethe stopping power with Joy & Luo's low-energy correction, Scanning 11 (1989) 176), times the
fluorescence yield (Krause, J. Phys. Chem. Ref. Data 8 (1979) 307) and the line's in-family share, times the
backscatter loss (Myklebust's fit). Kramers continuum, N(E) = k Z (E0 - E)/E with k about 2e-9 photons per electron
per eV into 4 pi (Kramers, Phil. Mag. 46 (1923) 836; Goldstein et al., *Scanning Electron Microscopy and X-Ray
Microanalysis*, 4th ed., 2018). Absorption on the way out through a Packwood-Brown Gaussian phi(rho z) integrated
numerically (Packwood & Brown, X-Ray Spectrom. 10 (1981) 138) with Anderson-Hasler X-ray ranges, 35 deg take-off.
Reed's K-K secondary fluorescence (Br. J. Appl. Phys. 16 (1965) 913). A carbon contamination film and the native
oxide (for powder, the shell the lot's oxygen implies for its particle size, half of the O assumed at the surface)
emit O and C and absorb soft X-rays. Powder: take-off angles spread over the particles' curvature (+-14 deg) and
5-20 % of soft X-rays shadowed by neighbours (both assumed), and the analysed field mixes the lot's atomizer runs with
Dirichlet weights (about 120 particles' worth, assumed). Detector: polymer window on a 77 %-open Si grid, 30 nm dead
layer, 450 um Si (Moxtek AP3.3-like, assumed); FWHM^2 = noise^2 + 2.355^2 F eps E with F = 0.115, eps = 3.71 eV and
noise set for 129 eV at Mn K-alpha (C K-alpha comes out at 58 eV); Si escape peaks (Reed & Ware, J. Phys. E 5 (1972)
582); a 0.5 % incomplete-charge shelf (assumed); pile-up by self-convolution with 0.4 us pulse-pair resolution;
paralyzable dead time 4 us (real time from live time); gain/offset drift; Poisson counts. Line energies:
Bearden, Rev. Mod. Phys. 39 (1967) 78 and NIST SRD 128 (https://physics.nist.gov/PhysRefData/XrayTrans/Html/search.html);
edges from the same. In-family weights (K-beta/K-alpha about 0.13 for Sc-Zn) approximate (assumed). Mass absorption
coefficients: 38.5 Z^3.66 / A E^-2.8 with K (125/Z + 3.5), L (3) and M (2) jump ratios (assumed form; within about 10 %
of NIST XCOM, https://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html, for the metals at 1.5-9 keV: Al, Fe, Ni, Cu,
Zn, Si, Mg at Cu K-alpha reproduce to 2-12 %); the forward model multiplies each (line, absorber) pair by a fixed
error (5 % above 2 keV, 8 % 1-2 keV, 12 % below 1 keV, assumed) that the quantification does not know, standing for
the tables' own uncertainty.

**Analysis.** Weighted linear least squares of the 0.33-14.7 keV spectrum against one column per element and shell
(fixed in-family weights, escape peaks, detector efficiency), a six-term background (Kramers shape through the window
and the specimen's absorption, times a cubic and a 1/E term), and a pile-up column; normal equations (see the note
on LAPACK below). Net intensities of the principal families (K for Z <= 30; L for Zr, Nb, Sn, Ce, Er; Er M and Ce M,
the 3d metals' L lines, O and C are fitted as nuisance columns). Standardless: emitted intensities per unit mass
fraction predicted by a ZAF-lite (same Z and F, Philibert-Duncumb-Heinrich absorption instead of phi(rho z)),
iterated, metals normalized to 100 % (O and C excluded); 3-sigma LODs from the fit covariance (scaled by the reduced
chi-square). The spectral overlaps are the real ones: Er M / Al K, Mg K / Al K, Mn K-beta / Fe K-alpha, Cr K-beta /
Mn K-alpha, Ni K-beta / Cu K-alpha, Cu K-beta / Zn K-alpha, Sc K-beta / Ti K-alpha, Ti K-beta / Ce L-alpha, Zr L / Nb L,
O K / Cr L; plus the Al K + O K pile-up under Zr L. Li is invisible (window, yield 3e-4) and its mass goes into the
other elements on normalization.

**What emerges.** LODs of 0.06 wt% (Mg) to 0.4 (Zn, Zr L) and 0.8 (Ce L, Er L at overvoltage 1.8) in Al; 0.07-0.3 in
Cu. Light elements read low in powder (Al in NAB powder -27 %, Si in Cu powders -17 %, Si in AlSi10Mg powder -5 %)
and a little off in polished parts (Al in NAB -6 %); Ti reads 15-20 % low in Al alloys (Sc K-beta / Ce L overlaps and
low overvoltage); Zr near its LOD is detected in about half the Scalmalloy spectra and biased high (pile-up).
Input count rate 15-35 kcps, dead time 6-13 %, pile-up 0.7-1.4 %.

### XRF (Bruker S2 PUMA, Pd tube, SDD, He)

**Forward model.** Three conditions, 100 s each (assumed method): light 12 kV/4 mA no filter (Mg, Al, Si), mid
30 kV/1.6 mA 100 um Al (Sc-Zn K, Ce and Er L), heavy 50 kV/1 mA 250 um Cu (Zr, Nb, Sn K). Pd-anode Kramers
continuum through 75 um Be plus Pd L and K lines (assumed strengths). Primary fluorescence by the fundamental-
parameter integral (Sherman, Spectrochim. Acta 7 (1955) 283) with eds.py's MACs, edges, yields and line energies
(K lines of Zr, Nb, Sn and their K yields from Bearden 1967 and Krause 1979 added), 45 deg geometry; secondary
fluorescence in a simplified Shiraiwa-Fujino form (assumed). Residual air in the He path, 0.3-2 % per run, and a
4 um prolene film under loose powder (assumed). Loose powder: a roughness loss of 10-18 % for lines whose information
depth is small against d50 (particle-size effect) and a heterogeneity factor (1 - e^-D)/D for elements held in coarse
second phases (Claisse & Samson, Adv. X-Ray Anal. 5 (1962) 335; Bertin 1975). The MAC table carries the same kind
of fixed per-pair error as in EDS. Peaks are integrated in +-1 FWHM windows that also catch the overlapping lines;
background = Compton/Rayleigh scatter of the tube spectrum (sigma_s about 0.2 (Z/13)^0.5 cm2/g against the specimen's
absorption, scale assumed) plus the incomplete-charge shelf of every stronger line above (1.2 %/keV, assumed);
Poisson counts. Instrument constant: pure Cu K-alpha = 150 kcps at the mid condition (assumed). Li has no line.

**Analysis.** Background from side windows; overlap correction with the software's line ratios (3 % off, assumed);
FP iteration with nominal MACs, pure He, no roughness or heterogeneity correction; normalized to 100 % with the base
element measured; LOD from 3 sqrt(background) (at least one count).

**What emerges.** LODs 10-50 ppm for transition metals and Zr/Nb in Al, 20-80 ppm for Mg, about 100-150 ppm for Si;
in Cu, 10-20 ppm for the 3d metals but about 200-300 ppm for Al and Si. The light base line of Al alloys is read
low in loose powder (roughness, residual air), so after normalization every other element reads high: Si +21 % in
AlSi10Mg powder (+11 % on a flat part), Zr +25 %, Zn +12 %; in Cu alloys Ni and Fe read 5-9 % low (matrix effects
through the MAC errors and fluorescence). Precision is far better than accuracy (within-sample SD 0.1-2 %).

### ICP-MS (Agilent 8900, HF-free digest)

Aqua regia + H2O2 closed-vessel microwave (assumed 200 degC), 100 mg in 50 mL, 1000x dilution. Recovery by phase
(assumed values, `RECOVERY`): solid solution dissolves (Zr 0.85, Ti 0.9, Nb 0.65 in solution, which hydrolyse without
fluoride); eutectic Si 0.03 (elemental Si is inert to HCl/HNO3), Mg2Si's Si 0.3, Al3Zr 0.35-0.45, Al3Ti 0.5,
Al3(Sc,Zr) 0.45-0.75, Al45Cr7 0.7, Ni3Nb 0.35, Ni3Ti 0.6, Cr particles 0.6; dissolved Si above 60 mg/L in the digest
polymerizes (30 % of the excess kept). Recovery varies digest to digest by 15 % of the missing share. Measurement:
sensitivity and BEC per element (typical 8900 He/H2-mode figures, assumed), Poisson counts, 0.8 % flicker per
replicate, 0.3 % residual drift after internal standard, three replicates; five-point calibration (each standard
+-0.5 %), weighted linear fit; 3-sigma LOD from ten blank replicates. Results are absolute (not normalized), so what
the digest misses reads low: Si in AlSi10Mg -90 %, Zr in Scalmalloy -35 to -50 %, Sc -9 to -14 %; dissolved metals
within 1 % (SD 0.5-1 %). Li is measured (7Li). Sources for the chemistry: EPA Method 3052 (microwave digestion,
https://www.epa.gov/hw-sw846/sw-846-test-method-3052) and its caution that silicate/refractory phases need HF.

### Calibration (fast vs lite), timings

Fitted on 60 (EDS), 50 (XRF), 40 (ICP-MS) random designs per campaign through the truth (a quarter with the melt set
60 K cold), each as a lot and a part, plus the reference alloys, 3-4 repeats each. Model, per element, campaign and
sample kind: log(measured/true) bias regressed on log10 concentration, overlap load (EDS) and two matrix descriptors
(Al: heavy and light solute; Cu: Ni/30, Al/9.5) over sample means; within-sample log-spread regressed on the
repeats' SDs; a logistic detection curve within 3x LOD and the measured/true ratio when detected; false-positive
rate and size for absent elements; LOD median and spread. ICP-MS: lognormal around the expected recovery, spread a
function of the missing share and concentration.

Gallery alloys, 50 draws each (bias and SD relative to the truth, %; detection rate):

| instrument | alloy | sample | element | true wt% | lite bias | lite sd | fast bias | fast sd | detected lite/fast |
|---|---|---|---|---|---|---|---|---|---|
| eds | AlSi10Mg | powder | Si | 10.00 | -5.7 % | 2.8 % | -4.6 % | 2.7 % | 100/100 % |
| eds | AlSi10Mg | powder | Mg | 0.31 | -5.3 % | 9.6 % | +1.8 % | 7.3 % | 100/100 % |
| eds | AlSi10Mg | part | Si | 10.00 | +3.6 % | 1.7 % | +4.0 % | 1.6 % | 100/100 % |
| eds | AlSi10Mg | part | Mg | 0.23 | -2.1 % | 13.7 % | -1.9 % | 3.2 % | 98/100 % |
| eds | Scalmalloy | powder | Mg | 2.93 | -0.5 % | 1.4 % | +0.1 % | 1.3 % | 100/100 % |
| eds | Scalmalloy | powder | Sc | 0.70 | -3.4 % | 3.1 % | -3.3 % | 2.6 % | 100/100 % |
| eds | Scalmalloy | powder | Zr | 0.30 | +20.6 % | 29.8 % | +16.3 % | 22.3 % | 56/34 % |
| eds | Scalmalloy | part | Mg | 2.17 | +1.0 % | 2.1 % | +0.8 % | 1.4 % | 100/100 % |
| eds | Scalmalloy | part | Sc | 0.70 | -5.1 % | 3.0 % | -5.4 % | 2.2 % | 100/100 % |
| eds | Scalmalloy | part | Zr | 0.30 | +32.2 % | 36.7 % | +14.5 % | 19.5 % | 50/42 % |
| eds | 7075 | powder | Zn | 4.01 | -1.3 % | 3.3 % | -1.7 % | 1.8 % | 100/100 % |
| eds | 7075 | powder | Mg | 2.20 | -1.7 % | 2.1 % | -1.3 % | 2.6 % | 100/100 % |
| eds | 7075 | powder | Cu | 1.60 | -2.4 % | 4.1 % | -3.2 % | 7.4 % | 100/100 % |
| eds | 7075 | powder | Cr | 0.23 | +1.8 % | 11.3 % | +3.9 % | 11.9 % | 82/92 % |
| eds | 7075 | part | Zn | 2.19 | -5.3 % | 3.8 % | -6.4 % | 2.8 % | 100/100 % |
| eds | 7075 | part | Mg | 1.63 | +0.9 % | 2.8 % | +1.8 % | 3.3 % | 100/100 % |
| eds | 7075 | part | Cu | 1.60 | -6.6 % | 4.2 % | -7.4 % | 4.3 % | 100/100 % |
| eds | 7075 | part | Cr | 0.23 | -2.4 % | 8.3 % | -2.2 % | 9.3 % | 76/54 % |
| eds | 70-30 Cu-Ni | powder | Ni | 30.00 | -0.2 % | 0.5 % | -0.4 % | 0.4 % | 100/100 % |
| eds | 70-30 Cu-Ni | powder | Fe | 0.60 | -0.8 % | 5.8 % | -1.6 % | 4.0 % | 100/100 % |
| eds | 70-30 Cu-Ni | powder | Mn | 0.53 | -4.4 % | 5.9 % | -3.7 % | 5.9 % | 100/100 % |
| eds | 70-30 Cu-Ni | part | Ni | 30.00 | -0.3 % | 0.6 % | -0.3 % | 0.3 % | 100/100 % |
| eds | 70-30 Cu-Ni | part | Fe | 0.60 | -0.0 % | 5.2 % | -0.5 % | 4.7 % | 100/100 % |
| eds | 70-30 Cu-Ni | part | Mn | 0.52 | -3.8 % | 6.3 % | -1.0 % | 5.3 % | 100/100 % |
| eds | NAB | powder | Al | 9.20 | -27.2 % | 3.8 % | -26.0 % | 3.1 % | 100/100 % |
| eds | NAB | powder | Ni | 4.50 | +2.7 % | 1.9 % | +1.9 % | 2.1 % | 100/100 % |
| eds | NAB | powder | Fe | 4.00 | +2.4 % | 1.4 % | +2.8 % | 1.6 % | 100/100 % |
| eds | NAB | powder | Mn | 1.05 | -0.1 % | 3.7 % | -0.2 % | 2.8 % | 100/100 % |
| eds | NAB | part | Al | 9.16 | -6.3 % | 0.7 % | -6.6 % | 0.6 % | 100/100 % |
| eds | NAB | part | Ni | 4.50 | +0.4 % | 1.8 % | +0.1 % | 1.2 % | 100/100 % |
| eds | NAB | part | Fe | 4.00 | +1.1 % | 1.3 % | +0.7 % | 0.7 % | 100/100 % |
| eds | NAB | part | Mn | 1.02 | -1.5 % | 3.6 % | -0.7 % | 3.4 % | 100/100 % |
| xrf | AlSi10Mg | powder | Si | 10.00 | +21.4 % | 0.7 % | +22.4 % | 0.6 % | 100/100 % |
| xrf | AlSi10Mg | powder | Mg | 0.31 | -3.3 % | 1.2 % | -0.1 % | 2.1 % | 100/100 % |
| xrf | AlSi10Mg | part | Si | 10.00 | +10.9 % | 0.7 % | +11.5 % | 0.7 % | 100/100 % |
| xrf | AlSi10Mg | part | Mg | 0.23 | -3.6 % | 1.2 % | -1.1 % | 1.4 % | 100/100 % |
| xrf | Scalmalloy | powder | Mg | 2.93 | +1.0 % | 1.3 % | -0.3 % | 1.0 % | 100/100 % |
| xrf | Scalmalloy | powder | Sc | 0.70 | +6.9 % | 1.8 % | +6.4 % | 2.0 % | 100/100 % |
| xrf | Scalmalloy | powder | Zr | 0.30 | +25.6 % | 3.7 % | +25.0 % | 3.3 % | 100/100 % |
| xrf | Scalmalloy | part | Mg | 2.17 | -0.9 % | 1.2 % | -1.6 % | 0.8 % | 100/100 % |
| xrf | Scalmalloy | part | Sc | 0.70 | +8.4 % | 1.8 % | +7.6 % | 1.4 % | 100/100 % |
| xrf | Scalmalloy | part | Zr | 0.30 | +12.1 % | 2.3 % | +13.0 % | 2.0 % | 100/100 % |
| xrf | 7075 | powder | Zn | 4.01 | +11.7 % | 1.8 % | +10.3 % | 1.5 % | 100/100 % |
| xrf | 7075 | powder | Mg | 2.20 | +4.0 % | 0.8 % | +3.8 % | 0.7 % | 100/100 % |
| xrf | 7075 | powder | Cu | 1.60 | +4.7 % | 1.5 % | +4.0 % | 1.4 % | 100/100 % |
| xrf | 7075 | powder | Cr | 0.23 | +0.1 % | 1.3 % | -3.0 % | 1.1 % | 100/100 % |
| xrf | 7075 | part | Zn | 2.19 | +9.0 % | 1.8 % | +7.3 % | 1.2 % | 100/100 % |
| xrf | 7075 | part | Mg | 1.63 | +1.1 % | 0.8 % | +1.6 % | 0.8 % | 100/100 % |
| xrf | 7075 | part | Cu | 1.60 | +3.5 % | 1.6 % | +2.6 % | 1.9 % | 100/100 % |
| xrf | 7075 | part | Cr | 0.23 | +3.1 % | 1.5 % | +1.6 % | 1.6 % | 100/100 % |
| xrf | 70-30 Cu-Ni | powder | Ni | 30.00 | -6.1 % | 0.0 % | -6.7 % | 0.0 % | 100/100 % |
| xrf | 70-30 Cu-Ni | powder | Fe | 0.60 | -3.2 % | 0.3 % | -8.4 % | 0.5 % | 100/100 % |
| xrf | 70-30 Cu-Ni | powder | Mn | 0.53 | +3.7 % | 0.3 % | +3.7 % | 0.3 % | 100/100 % |
| xrf | 70-30 Cu-Ni | part | Ni | 30.00 | -6.1 % | 0.0 % | -6.6 % | 0.1 % | 100/100 % |
| xrf | 70-30 Cu-Ni | part | Fe | 0.60 | -1.8 % | 0.2 % | -2.4 % | 0.2 % | 100/100 % |
| xrf | 70-30 Cu-Ni | part | Mn | 0.52 | +3.7 % | 0.3 % | +3.8 % | 0.2 % | 100/100 % |
| xrf | NAB | powder | Al | 9.20 | +6.5 % | 1.7 % | +5.2 % | 1.8 % | 100/100 % |
| xrf | NAB | powder | Ni | 4.50 | -5.1 % | 0.1 % | -6.0 % | 0.2 % | 100/100 % |
| xrf | NAB | powder | Fe | 4.00 | -8.4 % | 0.1 % | -9.1 % | 0.2 % | 100/100 % |
| xrf | NAB | powder | Mn | 1.05 | -1.9 % | 0.2 % | -2.2 % | 0.1 % | 100/100 % |
| xrf | NAB | part | Al | 9.16 | +10.2 % | 1.7 % | +8.4 % | 1.7 % | 100/100 % |
| xrf | NAB | part | Ni | 4.50 | -6.1 % | 0.1 % | -6.7 % | 0.1 % | 100/100 % |
| xrf | NAB | part | Fe | 4.00 | -7.3 % | 0.1 % | -7.8 % | 0.1 % | 100/100 % |
| xrf | NAB | part | Mn | 1.02 | -1.8 % | 0.2 % | -2.2 % | 0.1 % | 100/100 % |
| icpms | AlSi10Mg | powder | Si | 10.00 | -90.9 % | 1.1 % | -91.1 % | 0.9 % | 100/100 % |
| icpms | AlSi10Mg | powder | Mg | 0.31 | -0.4 % | 0.8 % | -0.3 % | 0.5 % | 100/100 % |
| icpms | AlSi10Mg | part | Si | 10.00 | -89.8 % | 1.2 % | -90.0 % | 1.0 % | 100/100 % |
| icpms | AlSi10Mg | part | Mg | 0.23 | -0.8 % | 0.9 % | -1.0 % | 0.7 % | 100/100 % |
| icpms | Scalmalloy | powder | Mg | 2.93 | -0.4 % | 0.8 % | -0.3 % | 0.4 % | 100/100 % |
| icpms | Scalmalloy | powder | Sc | 0.70 | -9.3 % | 1.6 % | -9.3 % | 1.3 % | 100/100 % |
| icpms | Scalmalloy | powder | Zr | 0.30 | -33.7 % | 3.5 % | -35.7 % | 2.4 % | 100/100 % |
| icpms | Scalmalloy | part | Mg | 2.17 | -0.4 % | 0.8 % | -0.3 % | 0.4 % | 100/100 % |
| icpms | Scalmalloy | part | Sc | 0.70 | -14.0 % | 2.0 % | -13.9 % | 1.7 % | 100/100 % |
| icpms | Scalmalloy | part | Zr | 0.30 | -48.6 % | 3.7 % | -50.3 % | 2.5 % | 100/100 % |
| icpms | 7075 | powder | Zn | 4.01 | -0.2 % | 0.7 % | -0.0 % | 0.4 % | 100/100 % |
| icpms | 7075 | powder | Mg | 2.20 | -0.2 % | 0.6 % | -0.2 % | 0.4 % | 100/100 % |
| icpms | 7075 | powder | Cu | 1.60 | -0.1 % | 0.7 % | -0.1 % | 0.5 % | 100/100 % |
| icpms | 7075 | powder | Cr | 0.23 | -1.1 % | 1.0 % | -1.4 % | 0.7 % | 100/100 % |
| icpms | 7075 | part | Zn | 2.19 | -0.8 % | 0.9 % | -0.7 % | 0.6 % | 100/100 % |
| icpms | 7075 | part | Mg | 1.63 | -0.3 % | 0.7 % | -0.4 % | 0.5 % | 100/100 % |
| icpms | 7075 | part | Cu | 1.60 | -0.6 % | 0.8 % | -0.7 % | 0.5 % | 100/100 % |
| icpms | 7075 | part | Cr | 0.23 | -1.1 % | 1.0 % | -1.4 % | 0.7 % | 100/100 % |
| icpms | 70-30 Cu-Ni | powder | Ni | 30.00 | -0.2 % | 0.7 % | -0.3 % | 0.5 % | 100/100 % |
| icpms | 70-30 Cu-Ni | powder | Fe | 0.60 | -0.3 % | 0.9 % | -0.1 % | 0.5 % | 100/100 % |
| icpms | 70-30 Cu-Ni | powder | Mn | 0.53 | -0.1 % | 0.7 % | -0.3 % | 0.5 % | 100/100 % |
| icpms | 70-30 Cu-Ni | part | Ni | 30.00 | -0.2 % | 0.7 % | -0.3 % | 0.5 % | 100/100 % |
| icpms | 70-30 Cu-Ni | part | Fe | 0.60 | -0.3 % | 0.9 % | -0.1 % | 0.5 % | 100/100 % |
| icpms | 70-30 Cu-Ni | part | Mn | 0.52 | -0.1 % | 0.7 % | -0.3 % | 0.5 % | 100/100 % |
| icpms | NAB | powder | Al | 9.20 | -0.4 % | 0.8 % | -0.4 % | 0.5 % | 100/100 % |
| icpms | NAB | powder | Ni | 4.50 | -0.4 % | 0.8 % | -0.1 % | 0.5 % | 100/100 % |
| icpms | NAB | powder | Fe | 4.00 | -0.2 % | 0.8 % | -0.3 % | 0.6 % | 100/100 % |
| icpms | NAB | powder | Mn | 1.05 | -0.3 % | 0.7 % | -0.3 % | 0.5 % | 100/100 % |
| icpms | NAB | part | Al | 9.16 | -0.4 % | 0.9 % | -0.5 % | 0.6 % | 100/100 % |
| icpms | NAB | part | Ni | 4.50 | -0.6 % | 0.8 % | -0.3 % | 0.7 % | 100/100 % |
| icpms | NAB | part | Fe | 4.00 | -0.8 % | 0.9 % | -1.0 % | 0.6 % | 100/100 % |
| icpms | NAB | part | Mn | 1.02 | -0.3 % | 0.7 % | -0.3 % | 0.5 % | 100/100 % |

Timings on the shared runner (load average about 10 on 4 cores), per call over the gallery samples:

* eds: lite median 13.8 ms (max 17.6), fast median 0.125 ms (max 0.248), full median 17 ms (max 38)
* xrf: lite median 19.9 ms (max 28.2), fast median 0.113 ms (max 0.199), full median 19 ms (max 35)
* icpms: lite median 1.9 ms (max 2.7), fast median 0.102 ms (max 0.172), full median 9 ms (max 16)

Known gaps between fast and lite: an element within about 2x its LOD whose detection depends on a sample-specific
artifact (EDS Zr L under the Al K + O K pile-up in Scalmalloy: lite detects 50-56 %, fast 34-42 %); XRF Fe in 70-30
powder (-3 % lite, -8 % fast). Everything else agrees to about 2 % in bias and comparable spread.

### Known limits

* MACs are a power law with jump ratios, not tabulated values; L and M family weights and the Pd tube lines are
  approximate; Er form factors etc. are not used here. Continuum absorption uses a line's phi(rho z) with E_c = E.
* EDS: no peak-shape asymmetry beyond the shelf, no Si internal fluorescence peak, no coincidence of three events,
  no Duane-Hunt fitting; the analysed area is assumed homogeneous (coarse intermetallics are averaged, not imaged).
* XRF: no full-spectrum fitting (window integration with overlap correction instead), no escape/sum peaks, no
  Compton/Rayleigh tube-line peaks in the analysis; finite-thickness effects ignored (loose powder cups are thick).
* ICP-MS recoveries are assumed numbers, not measured on these alloys; no polyatomic interference model beyond
  BECs; no matrix suppression (2 mg/L after dilution).
* `np.linalg.lstsq`/QR take about 100 ms on this runner (OpenBLAS threads under contention); the EDS fit uses
  column-scaled normal equations (0.1 ms).

## EBSD (`twin/instruments/ebsd.py`)

**What it models.** An orientation map of a polished section of a part that contains the build direction (BD up),
taken on the lab's SEM at 20 kV and 70 deg tilt, then analysed the way a lab would analyse it. Powder lots are not
mapped (`measure` returns `{}` for them).

*The map (`_simulate`)* reads only `micro.phase_model(part)`: `grains` (grain size, equiaxed share, columnar aspect,
<100> fiber spread, KAM), the phase volume fractions (beta' and kappa for Cu, the fine second phases for both), the
pore populations and the hot-crack density.

- **Grains.** There are two Poisson-Voronoi tessellations. Equiaxed grains get uniformly random orientations
  (Shoemake 1992). Columnar grains have their seeds in a space compressed along BD by the aspect ratio (4 for Al,
  5 for Cu), and their orientations are a <100> fiber along BD: a Rayleigh-distributed tilt of `fiber_spread_deg`
  and a random spin.
  - Seed densities give an infinite ideal section an area-weighted equivalent-circle diameter (ECD) equal to the
    truth's `grain_um`. For 2-D Poisson-Voronoi cells, area-weighted ECD = 1.241/sqrt(seed density), from the
    gamma(3.6) distribution of cell areas (Ferenc & Neda, Physica A 385 (2007) 518,
    https://doi.org/10.1016/j.physa.2007.07.063).
  - Equiaxed grains are 1.5 um in Al, the truth's own constant. In Cu they are 0.6 x grain_um (*assumed*). Columnar
    grains take the rest of the truth's mixture, so the area-weighted mixture equals `grain_um`.
  - Which population a point belongs to follows melt-pool bands. The period is the melt-pool depth (Al) or 400 um
    (Cu), and at least 2.5 columnar lengths. The arcs are a hatch wide, and the bottom `equiaxed_frac` of each band
    is the fine-grain zone (*assumed geometry*; Spierings et al., Mater. Des. 115 (2017) 52,
    https://doi.org/10.1016/j.matdes.2016.11.040).
- **Orientation inside grains.** A Gaussian random rotation field with a correlation length of 0.6 um (*assumed*).
  Its amplitude gives the truth's `kam_deg` at a 0.5 um reference step (*assumed*), so KAM grows with step size and
  saturates at about 1.6 x the reference.
- **Indexing noise.** About 0.35 deg mean neighbour misorientation on good patterns, and worse as band contrast falls
  (Humphreys, J. Mater. Sci. 36 (2001) 3833, https://doi.org/10.1023/A:1017973432592; Wright, Nowell & Field,
  Microsc. Microanal. 17 (2011) 316, https://doi.org/10.1017/S1431927611000055).
- **Band contrast (pattern quality)** per point, then indexing:
  - Base values are FCC 0.92 (Al) or 0.88 (Cu), beta' 0.75 and kappa 0.70 (*assumed*).
  - It is multiplied by exp(-local KAM/4 deg), by (1 - 1.5 x the volume share of unresolved second phases: the Si
    network, L1_2, kappa_III/IV), by 0.75 next to grain boundaries (overlapping patterns), and by 0.5 along polishing
    scratches (Poisson, about one per map).
  - It is 0.02 in pores and cracks.
  - Pattern-to-pattern scatter is lognormal with sigma 0.25. A point indexes above 0.35 (*all assumed*; the Hough
    indexing logic is in Wright & Nowell, Microsc. Microanal. 12 (2006) 72,
    https://doi.org/10.1017/S1431927606060117).
  - Low-quality points are misindexed at p = 0.03 exp(-(BC-0.35)/0.15): half random, half the 60 deg <111>
    pseudo-symmetric FCC solution.
- **Pores.** Sections of the truth's pore spheres: N_A = N_V E[D] (DeHoff), with the size-biased lognormal
  (mu + sigma^2) and the section radius sqrt(R^2 - z^2). Lack-of-fusion sections are ellipses (aspect 2.6, long axis
  in the layer plane).
- **Hot cracks.** Lines along BD with the truth's length per area (mm/mm^2), lognormal lengths, a 1.5 um opening and
  a random walk in x. A pixel is hit with probability min(1, opening/step).
- **Cu phases.**
  - Retained beta' sits in blobs: a thresholded Gaussian field at the truth's volume fraction (Delesse), with
    correlation of about grain/2. The blobs hold their own random martensite packets (grain/3), with extra lath noise
    of 1 deg per component and KAM 1.5 deg. They index poorly, so EBSD under-counts beta' relative to XRD.
  - Coarse kappa_II appears as BCC points at its volume fraction.
  - beta' and kappa are confused 10 % of the time (both are BCC-derived), and 0.5 % of FCC points are read as BCC
    (*assumed*).
- **Re-mapping.** A map with less than 30 % of its points indexed (it landed in a lack-of-fusion pore) is re-taken
  at another spot, at most twice (*assumed operator policy*).
- **Step and field of view.** The step is grain/5 for lite and grain/10 for full, clipped to 0.1-5 um. The point
  budget is fixed: 80 x 64 for lite, 400 x 300 for full. So the field of view, and with it the number of grains and
  bands sampled, depends on the grain size, and the resolution and FOV biases emerge rather than being imposed.

*The analysis (`_analyse`)* uses only the measured map (quaternions, phase IDs, band contrast):

1. Grain reconstruction: connected components over 4-neighbours of the same phase misoriented by less than 15 deg,
   with cubic symmetry (24 operators, disorientation by the max |w| of q1^-1 q2 S_i).
2. Grains with fewer than 4 points are removed.
3. Grain size is the area-weighted mean ECD over FCC grains, excluding edge grains (ASTM E2627 practice) unless fewer
   than 5 interior grains remain.
4. Equiaxed share is the area share of grains with aspect ratio < 2. The aspect ratio comes from the second moments,
   with the pixel's 1/12 added to each.
5. `texture_mrd` is the density of the <100> pole along BD, from a Gaussian kernel (5 deg half-width) on the angle
   between BD and the nearest <100>. It is normalised by the kernel's expectation for a random texture (computed
   once by Monte Carlo), so a random map reads about 1.
   - The ideal value for an infinite map is (1 - eq)(w^2/(w^2+s^2))/E_rand + eq, with the Rayleigh tilt width s.
     That gives 4.95 for a 14 deg fiber.
6. KAM is the mean over first neighbours below 5 deg (Wright et al. 2011).
7. `indexed_frac` is the share of indexed points.
8. `beta_prime_frac` (Cu) is the share of indexed points in beta'.

**Full mode** adds `raw`: quaternion map, IPF-BD colours, phase map, grain labels, boundary mask, KAM and
band-contrast maps, step, and Kikuchi patterns; the ideal values only with `with_truth=True` (figure annotation).

- The Kikuchi pattern is a gnomonic projection with PC (0.5, 0.40) and DD 0.65 (*assumed geometry*). It has one band
  per reflector with kinematic |F|^2 above 3 % of the strongest, computed from the structure's atom sites in
  `micro.STRUCTURES` with an electron scattering amplitude Z^0.75 exp(-1.5 s^2) (*assumed shape*) and a Debye-Waller
  factor. FCC Al and Cu are shown, plus beta' as its DO3 parent.
- Band half-width is the Bragg angle at the relativistic wavelength, lambda = 12.2643/sqrt(V(1+0.97848e-6 V)) A
  = 0.0859 A at 20 kV (e.g. Williams & Carter, *Transmission Electron Microscopy*, Table 1.1).
- Bands have soft edges and bright edge lines. The background falls off from below the PC; Poisson counts; static
  background division; round phosphor screen. Cu bands come out wider than Al's (smaller d), as they should.

**Fast mode.** It samples the lite chain's error from `calib_micro.json["ebsd"]`, written by `python -m
twin.instruments.ebsd 60` (`calibrate()`). Per campaign and output it fits:

1. A ridge-regularised linear model of the error mean on 14 state features: 1, eq, eq(1-eq), ln d, the step-clip
   term, sqrt(porosity), beta', beta'^2, the true KAM, the unresolved-phase share, crack density, eq ln d, (ln d)^2,
   and sqrt(por) ln d.
2. A per-sample table of mean residuals and within-sample (map-to-map) spreads. The fast mode reads it by
   inverse-distance-weighted 5-nearest neighbours in standardised feature space, shrunk toward the linear model when
   far away.

The errors are modelled in ln(meas/true) for grain size and MRD, ln(meas) for KAM, logit for the indexed share, and
meas - true for the equiaxed and beta' shares. The calibration set is 60 random designs per campaign through the
truth (random process settings, a quarter of the melts set 60 K cold, all three DED modes) with 3 maps each, plus the
gallery alloys with 24 maps each. That is 252 (Al) and 228 (Cu) lite maps, about 15 s in all.

**Calibration (lite chain, ln or difference units).** Mean error over all samples, residual sd after the mean model,
and the pooled within-sample sd:

| campaign | output | mean y | resid sd | within-part sd |
|---|---|---|---|---|
| Al | grain_um ln(meas/true) | +0.030 | 0.178 | 0.195 |
| Al | equiaxed_frac (meas - true) | -0.043 | 0.075 | 0.078 |
| Al | texture_mrd ln(meas/ideal) | -0.033 | 0.256 | 0.276 |
| Al | indexed_frac logit | +2.84 (94.5 %) | 0.685 | 0.688 |
| Al | kam_deg ln | +0.032 | 0.035 | 0.019 |
| Cu | grain_um | -0.066 | 0.147 | 0.149 |
| Cu | equiaxed_frac | -0.005 | 0.136 | 0.145 |
| Cu | texture_mrd | -0.042 | 0.254 | 0.258 |
| Cu | indexed_frac logit | +2.79 (94.2 %) | 0.630 | 0.563 |
| Cu | kam_deg ln | +0.046 | 0.019 | 0.009 |
| Cu | beta_prime_frac (meas - true) | -0.020 | 0.014 | 0.011 |

**Fast vs lite on the gallery parts** (30 draws each, mean +- sd; "true" is the truth or the ideal MRD):

| part | output | true | lite | fast |
|---|---|---|---|---|
| AlSi10Mg | grain_um | 8.39 | 8.89 +- 0.39 | 9.02 +- 0.41 |
| AlSi10Mg | texture_mrd | 4.95 | 4.95 +- 0.66 | 5.03 +- 0.50 |
| AlSi10Mg | kam_deg | 0.55 | 1.104 +- 0.007 | 1.103 +- 0.009 |
| Scalmalloy | grain_um | 2.31 | 1.70 +- 0.24 | 1.74 +- 0.21 |
| Scalmalloy | equiaxed_frac | 0.95 | 0.80 +- 0.04 | 0.78 +- 0.04 |
| Scalmalloy | texture_mrd | 1.18 | 1.07 +- 0.33 | 1.31 +- 0.46 |
| 7075 | grain_um | 17.7 | 19.2 +- 0.9 | 19.7 +- 0.9 |
| 7075 | indexed_frac | - | 0.959 +- 0.020 | 0.956 +- 0.022 |
| 70-30 Cu-Ni | grain_um | 23.7 | 22.2 +- 3.1 | 23.1 +- 2.9 |
| 70-30 Cu-Ni | equiaxed_frac | 0.37 | 0.35 +- 0.10 | 0.32 +- 0.10 |
| NAB | grain_um | 26.2 | 19.6 +- 2.1 | 20.2 +- 2.3 |
| NAB | equiaxed_frac | 0.48 | 0.50 +- 0.09 | 0.46 +- 0.08 |
| NAB | indexed_frac | - | 0.760 +- 0.061 | 0.768 +- 0.039 |
| NAB | beta_prime_frac | 0.323 | 0.211 +- 0.026 | 0.203 +- 0.028 |

**What emerges rather than being imposed:**
- Grain size is biased a few percent high for columnar maps, because low-angle neighbours in the fiber merge.
- It is biased low (-25 %) where 1.5 um equiaxed grains are only about 3 points across (Scalmalloy) or where beta'
  blobs and pores cut the grains (NAB).
- Voronoi cells and pixelation take about 0.08 off the equiaxed share of a perfectly equiaxed map and add about 0.08
  to a fully columnar one.
- The texture MRD has about 25 % map-to-map scatter, because a lite map holds only 100-300 grains.
- KAM at the lite step is about 2x the truth's 0.5 um-step value.
- EBSD reads 0.21 for NAB's beta' against 0.32 true (about 0.65x, the under-count against XRD).
- About 1-5 % of points are lost to pores and cracks, and about 23 % in NAB.

Calibration noise: the per-part means rest on 24 maps, so a fast-vs-lite comparison at 50 draws can differ by up to
about 0.05 in a share and 5-10 % in grain size. MRD near random (Scalmalloy) differs most in relative terms, because
the lite distribution is skewed.

**Timings** (one core, runner shared with other jobs): fast 0.1-0.5 ms (phase_model is cached), lite 8-13 ms
(80 x 64 points; up to about 30 ms when the runner is loaded), full 0.3-0.7 s (400 x 300 points plus a 240 px
Kikuchi pattern). The gallery takes about 8 s.

**Known limits.**
- Orientations are uncorrelated between neighbouring grains: no variant selection and no K-S/N-W relation for beta',
  and no twins (FCC Cu alloys anneal-twin, so a real map of a tempered deposit would show Sigma3 boundaries this one
  lacks).
- There is no 3-D grain shape and no tilt-corrected aspect ratio.
- Second phases finer than the step only lower band contrast; they are never indexed as their own phase. Kappa_II is
  per-point, not drawn as particles.
- The Kikuchi intensities are kinematic with a schematic electron form factor, not dynamical.
- beta' is indexed as its DO3 parent, not the 9R/3R martensite.
- The electron scattering amplitude for band intensities is not the Doyle-Turner table.


## Timings

Measured on the shared 4-core runner with `OPENBLAS_NUM_THREADS=1`, so with BLAS on one thread. With OpenBLAS's
default 4 threads, spin-up costs more than these small fits take: process CPU time doubles, and wall time spikes
under load.

* **Lite and fast**: CPU time per call from `calibrate_micro --table 40`, median over the five gallery alloys and
  their range. The tests check medians against 1 ms (fast) and 30 ms (lite).

| instrument | lite ms/call: median over the 5 gallery alloys (range) | fast ms/call |
|---|---|---|
| sem_powder | 18.9 (18.7-21.6) | 0.096 (0.092-0.098) |
| eds | 7.0 (6.6-7.3) | 0.052 (0.047-0.065) |
| xrf | 11.8 (7.6-12.9) | 0.048 (0.032-0.059) |
| icpms | 0.7 (0.4-0.9) | 0.022 (0.022-0.026) |
| xrd_powder | 12.3 (10.2-12.8) | 0.362 (0.317-0.369) |
| sem_section | 16.6 (14.8-22.3) | 0.283 (0.241-0.393) |
| ebsd | 9.6 (8.8-11.8) | 0.169 (0.156-0.180) |
| xrd_part | 15.9 (13.4-16.3) | 0.032 (0.024-0.072) |

* **Full**, per call, ms (AlSi10Mg / NAB):

| instrument | AlSi10Mg | NAB |
|---|---|---|
| sem_powder | 746 | 601 |
| eds | 22 | 14 |
| xrf | 14 | 10 |
| icpms | 4 | 5 |
| xrd_powder | 450 (first call computes the full-grid patterns; later calls ~30-60) | 32 |
| sem_section | 260 | 332 |
| ebsd (with Kikuchi patterns) | 370 | 366 |
| xrd_part | 27 | 34 |

**Robustness.** A sweep of 3630 fast and lite calls raised no exceptions and gave no non-finite outputs. It covered
120 random lots and parts across both campaigns, including:

* lots whose runs all failed;
* gas-atomized lots with no runs;
* NaN oxygen and satellite share;
* parts with empty `pores`, or without `strength`.

## Calibration table (fast vs lite, 40 draws each, gallery alloys)

| instrument | alloy | output | true | lite mean ± sd | fast mean ± sd | z |
|---|---|---|---|---|---|---|
| sem_powder | AlSi10Mg | d50_img_um | – | 54.4 ± 5.05 | 52.5 ± 3.0592 | -2.1 |
| sem_powder | AlSi10Mg | satellite_frac | 0.07 | 0.0179 ± 0.0339 | 0.017 ± 0.0179 | -0.1 |
| sem_powder | AlSi10Mg | sphericity | – | 0.981 ± 0.00896 | 0.984 ± 0.0128 | +0.9 |
| sem_powder | Scalmalloy | d50_img_um | – | 53.9 ± 3.9387 | 54.5 ± 3.6684 | +0.7 |
| sem_powder | Scalmalloy | satellite_frac | 0.07 | 0.0132 ± 0.0231 | 0.0128 ± 0.0151 | -0.1 |
| sem_powder | Scalmalloy | sphericity | – | 0.984 ± 0.00962 | 0.982 ± 0.0134 | -0.6 |
| sem_powder | 7075 | d50_img_um | – | 54.6 ± 3.7870 | 53.1 ± 3.5640 | -1.9 |
| sem_powder | 7075 | satellite_frac | 0.07 | 0.0155 ± 0.0321 | 0.0143 ± 0.0164 | -0.2 |
| sem_powder | 7075 | sphericity | – | 0.983 ± 0.00952 | 0.982 ± 0.0139 | -0.1 |
| sem_powder | 70-30 Cu-Ni | d50_img_um | – | 81.8 ± 7.68 | 79.6 ± 6.84 | -1.3 |
| sem_powder | 70-30 Cu-Ni | satellite_frac | 0.07 | 0.0116 ± 0.0157 | 0.0195 ± 0.0173 | +2.2 |
| sem_powder | 70-30 Cu-Ni | sphericity | – | 0.974 ± 0.00966 | 0.975 ± 0.00927 | +0.2 |
| sem_powder | NAB | d50_img_um | – | 82.7 ± 6.24 | 83.2 ± 5.82 | +0.3 |
| sem_powder | NAB | satellite_frac | 0.07 | 0.00844 ± 0.0142 | 0.0155 ± 0.0126 | +2.3 |
| sem_powder | NAB | sphericity | – | 0.976 ± 0.00934 | 0.975 ± 0.0106 | -0.4 |
| eds | AlSi10Mg | comp.Mg | 0.308 | 0.301 ± 0.0292 | 0.305 ± 0.0225 | +0.6 |
| eds | AlSi10Mg | comp.Si | 10.0 | 9.50 ± 0.239 | 9.49 ± 0.227 | -0.2 |
| eds | Scalmalloy | comp.Mg | 2.9326 | 2.9393 ± 0.0485 | 2.9317 ± 0.0319 | -0.8 |
| eds | Scalmalloy | comp.Sc | 0.7 | 0.678 ± 0.0207 | 0.676 ± 0.0209 | -0.3 |
| eds | Scalmalloy | comp.Zr (n 15/19) | 0.3 | 0.38 ± 0.0873 | 0.361 ± 0.0931 | -0.6 |
| eds | 7075 | comp.Cu | 1.6000 | 1.5833 ± 0.0687 | 1.5242 ± 0.0985 | -3.1 |
| eds | 7075 | comp.Mg | 2.2006 | 2.1808 ± 0.0499 | 2.1616 ± 0.052 | -1.7 |
| eds | 7075 | comp.Zn | 4.0146 | 4.0093 ± 0.113 | 3.9311 ± 0.0932 | -3.4 |
| eds | 70-30 Cu-Ni | comp.Fe | 0.6 | 0.589 ± 0.0279 | 0.589 ± 0.0191 | +0.1 |
| eds | 70-30 Cu-Ni | comp.Mn | 0.525 | 0.498 ± 0.0299 | 0.49 ± 0.0283 | -1.3 |
| eds | 70-30 Cu-Ni | comp.Ni | 30.0 | 29.9 ± 0.164 | 29.9 ± 0.0955 | -2.0 |
| eds | NAB | comp.Al | 9.20 | 6.72 ± 0.322 | 6.75 ± 0.279 | +0.4 |
| eds | NAB | comp.Fe | 4.0000 | 4.0856 ± 0.047 | 4.0847 ± 0.0756 | -0.1 |
| eds | NAB | comp.Mn | 1.0502 | 1.0564 ± 0.0433 | 1.0442 ± 0.0256 | -1.5 |
| eds | NAB | comp.Ni | 4.5000 | 4.6079 ± 0.0902 | 4.5978 ± 0.0847 | -0.5 |
| xrf | AlSi10Mg | comp.Mg | 0.308 | 0.3 ± 0.0042 | 0.304 ± 0.00543 | +4.1 |
| xrf | AlSi10Mg | comp.Si | 10.0 | 12.1 ± 0.0737 | 12.2 ± 0.0532 | +7.3 |
| xrf | Scalmalloy | comp.Mg | 2.9326 | 2.9615 ± 0.0419 | 2.9080 ± 0.0235 | -7.0 |
| xrf | 7075 | comp.Mg | 2.2006 | 2.2874 ± 0.0181 | 2.2757 ± 0.0143 | -3.2 |
| xrf | 7075 | comp.Zn | 4.0146 | 4.4807 ± 0.0793 | 4.4132 ± 0.0601 | -4.3 |
| xrf | 70-30 Cu-Ni | comp.Fe | 0.6 | 0.582 ± 0.0021 | 0.549 ± 0.00272 | -60.1 |
| xrf | 70-30 Cu-Ni | comp.Ni | 30.0 | 28.2 ± 0.0166 | 28.0 ± 0.0134 | -56.3 |
| xrf | NAB | comp.Al | 9.20 | 9.81 ± 0.179 | 9.72 ± 0.129 | -2.6 |
| xrf | NAB | comp.Fe | 4.0000 | 3.6656 ± 0.00621 | 3.6358 ± 0.00572 | -22.3 |
| xrf | NAB | comp.Ni | 4.5000 | 4.2684 ± 0.00745 | 4.2280 ± 0.00845 | -22.7 |
| icpms | AlSi10Mg | comp.Si | 10.0 | 0.898 ± 0.138 | 0.896 ± 0.0788 | -0.1 |
| icpms | Scalmalloy | comp.Zr | 0.3 | 0.2 ± 0.00944 | 0.192 ± 0.00616 | -4.3 |
| icpms | 7075 | comp.Zn | 4.0146 | 4.0015 ± 0.0328 | 4.0054 ± 0.0114 | +0.7 |
| icpms | 70-30 Cu-Ni | comp.Fe | 0.6 | 0.599 ± 0.00475 | 0.599 ± 0.00227 | +0.2 |
| icpms | 70-30 Cu-Ni | comp.Ni | 30.0 | 30.0 ± 0.248 | 29.9 ± 0.109 | -1.0 |
| icpms | NAB | comp.Al | 9.20 | 9.17 ± 0.0551 | 9.17 ± 0.0475 | -0.1 |
| icpms | NAB | comp.Fe | 4.0000 | 3.9971 ± 0.0258 | 3.9801 ± 0.0177 | -3.4 |
| icpms | NAB | comp.Ni | 4.5000 | 4.4860 ± 0.0348 | 4.4837 ± 0.0147 | -0.4 |
| xrd_powder | AlSi10Mg | a_fcc_A | 4.0483 | 4.0482 ± 1.20e-04 | 4.0482 ± 1.17e-04 | -2.8 |
| xrd_powder | AlSi10Mg | crystallite_nm | – | 634 ± 292 | 753 ± 254 | +1.9 |
| xrd_powder | AlSi10Mg | phase.Si | – | 0.0841 ± 0.00284 | 0.0851 ± 0.00633 | +0.9 |
| xrd_powder | AlSi10Mg | solute_ss_wt | – | 0.96 ± 0.0848 | 1.0128 ± 0.0831 | +2.8 |
| xrd_powder | Scalmalloy | a_fcc_A | 4.0655 | 4.0655 ± 1.11e-04 | 4.0655 ± 1.03e-04 | -0.3 |
| xrd_powder | Scalmalloy | crystallite_nm | – | 749 ± 273 | 752 ± 267 | +0.0 |
| xrd_powder | Scalmalloy | solute_ss_wt | – | 3.6146 ± 0.0252 | 3.6131 ± 0.0235 | -0.3 |
| xrd_powder | 7075 | a_fcc_A | 4.0554 | 4.0554 ± 1.18e-04 | 4.0554 ± 1.19e-04 | -0.5 |
| xrd_powder | 7075 | crystallite_nm | – | 592 ± 300 | 705 ± 290 | +1.7 |
| xrd_powder | 7075 | solute_ss_wt | – | 8.37 ± 0.163 | 8.35 ± 0.165 | -0.5 |
| xrd_powder | 70-30 Cu-Ni | a_fcc_A | 3.5884 | 3.5884 ± 7.32e-05 | 3.5884 ± 5.39e-05 | -1.9 |
| xrd_powder | 70-30 Cu-Ni | crystallite_nm | – | 374 ± 90.7 | 354 ± 97.5 | -1.0 |
| xrd_powder | 70-30 Cu-Ni | solute_ss_wt | – | 31.5 ± 0.0894 | 31.5 ± 0.0658 | +1.9 |
| xrd_powder | NAB | a_fcc_A | 3.6384 | 3.6382 ± 2.52e-04 | 3.6382 ± 7.49e-05 | +0.4 |
| xrd_powder | NAB | crystallite_nm | – | 1000 ± 0 | 988 ± 74.3 | -1.0 |
| xrd_powder | NAB | phase.beta' | – | 0.641 ± 0.00346 | 0.624 ± 0.0271 | -4.0 |
| xrd_powder | NAB | solute_ss_wt | – | 9.13 ± 0.105 | 9.14 ± 0.0313 | +0.4 |
| sem_section | AlSi10Mg | crack_density | 0.0257 | 0.0181 ± 0.0507 | 0.0437 ± 0.0681 | +1.9 |
| sem_section | AlSi10Mg | lof_frac | 0.0961 | 0.0324 ± 0.151 | 0.0656 ± 0.197 | +0.8 |
| sem_section | AlSi10Mg | pore_dmax_um | – | 46.0 ± 20.3 | 49.1 ± 25.3 | +0.6 |
| sem_section | AlSi10Mg | porosity | 0.00436 | 0.00375 ± 0.00273 | 0.00433 ± 0.00392 | +0.8 |
| sem_section | Scalmalloy | crack_density | 0.0333 | 0.0294 ± 0.0485 | 0.0253 ± 0.0321 | -0.4 |
| sem_section | Scalmalloy | lof_frac | 0.149 | 0.0708 ± 0.159 | 0.0706 ± 0.193 | -0.0 |
| sem_section | Scalmalloy | pore_dmax_um | – | 42.9 ± 12.5 | 47.5 ± 15.6 | +1.4 |
| sem_section | Scalmalloy | porosity | 0.00548 | 0.00367 ± 0.00185 | 0.00488 ± 0.00258 | +2.4 |
| sem_section | 7075 | crack_density | 1.8781 | 1.2643 ± 0.373 | 1.3716 ± 0.386 | +1.3 |
| sem_section | 7075 | lof_frac | 0.062 | 0.0495 ± 0.135 | 0.0566 ± 0.108 | +0.3 |
| sem_section | 7075 | pore_dmax_um | – | 57.6 ± 22.3 | 53.5 ± 12.9 | -1.0 |
| sem_section | 7075 | porosity | 0.0175 | 0.0155 ± 0.00549 | 0.016 ± 0.00551 | +0.5 |
| sem_section | 70-30 Cu-Ni | crack_density | 0.029 | 0.0379 ± 0.0656 | 0.0231 ± 0.0484 | -1.2 |
| sem_section | 70-30 Cu-Ni | lof_frac | 0.947 | 0.719 ± 0.242 | 0.779 ± 0.156 | +1.3 |
| sem_section | 70-30 Cu-Ni | pore_dmax_um | – | 163 ± 58.1 | 164 ± 50.1 | +0.1 |
| sem_section | 70-30 Cu-Ni | porosity | 0.0561 | 0.0458 ± 0.0289 | 0.0512 ± 0.0271 | +0.9 |
| sem_section | NAB | crack_density | 0.0131 | 0.0151 ± 0.046 | 0.014 ± 0.0281 | -0.1 |
| sem_section | NAB | lof_frac | 0.9 | 0.615 ± 0.322 | 0.628 ± 0.312 | +0.2 |
| sem_section | NAB | pore_dmax_um | – | 141 ± 60.4 | 116 ± 46.5 | -2.1 |
| sem_section | NAB | porosity | 0.0294 | 0.0296 ± 0.0225 | 0.0234 ± 0.0171 | -1.4 |
| ebsd | AlSi10Mg | equiaxed_frac | 0 | 0.0942 ± 0.0248 | 0.103 ± 0.0246 | +1.6 |
| ebsd | AlSi10Mg | grain_um | 8.39 | 9.07 ± 0.543 | 8.78 ± 0.362 | -2.8 |
| ebsd | AlSi10Mg | indexed_frac | – | 0.933 ± 0.0118 | 0.93 ± 0.0164 | -0.9 |
| ebsd | AlSi10Mg | kam_deg | – | 1.1040 ± 0.00707 | 1.1040 ± 0.00976 | +0.0 |
| ebsd | AlSi10Mg | texture_mrd | – | 4.7530 ± 0.65 | 4.9615 ± 0.367 | +1.8 |
| ebsd | Scalmalloy | equiaxed_frac | 0.954 | 0.792 ± 0.0388 | 0.778 ± 0.0417 | -1.6 |
| ebsd | Scalmalloy | grain_um | 2.3147 | 1.7360 ± 0.256 | 1.6188 ± 0.18 | -2.4 |
| ebsd | Scalmalloy | indexed_frac | – | 0.96 ± 0.0128 | 0.956 ± 0.0229 | -1.0 |
| ebsd | Scalmalloy | kam_deg | – | 0.776 ± 0.00479 | 0.778 ± 0.00467 | +1.3 |
| ebsd | Scalmalloy | texture_mrd | – | 1.1250 ± 0.506 | 1.2214 ± 0.326 | +1.0 |
| ebsd | 7075 | equiaxed_frac | 0 | 0.0851 ± 0.0209 | 0.082 ± 0.0227 | -0.6 |
| ebsd | 7075 | grain_um | 17.7 | 19.6 ± 0.948 | 19.2 ± 0.833 | -2.3 |
| ebsd | 7075 | indexed_frac | – | 0.962 ± 0.017 | 0.956 ± 0.0188 | -1.6 |
| ebsd | 7075 | kam_deg | – | 1.0942 ± 0.00632 | 1.0938 ± 0.00749 | -0.3 |
| ebsd | 7075 | texture_mrd | – | 4.8412 ± 0.499 | 4.8070 ± 0.348 | -0.4 |
| ebsd | 70-30 Cu-Ni | beta_prime_frac | 1.39e-04 | 0.00507 ± 9.67e-04 | 0.00423 ± 0.00111 | -3.6 |
| ebsd | 70-30 Cu-Ni | equiaxed_frac | 0.373 | 0.305 ± 0.11 | 0.339 ± 0.118 | +1.3 |
| ebsd | 70-30 Cu-Ni | grain_um | 23.7 | 23.6 ± 3.3730 | 22.6 ± 2.8535 | -1.4 |
| ebsd | 70-30 Cu-Ni | indexed_frac | – | 0.947 ± 0.048 | 0.914 ± 0.0638 | -2.6 |
| ebsd | 70-30 Cu-Ni | kam_deg | – | 0.925 ± 0.00709 | 0.929 ± 0.0054 | +2.8 |
| ebsd | 70-30 Cu-Ni | texture_mrd | – | 2.3269 ± 0.499 | 2.3193 ± 0.64 | -0.1 |
| ebsd | NAB | beta_prime_frac | 0.306 | 0.205 ± 0.0247 | 0.199 ± 0.02 | -1.3 |
| ebsd | NAB | equiaxed_frac | 0.475 | 0.485 ± 0.0811 | 0.468 ± 0.0943 | -0.9 |
| ebsd | NAB | grain_um | 26.2 | 19.9 ± 2.4150 | 19.8 ± 2.2817 | -0.2 |
| ebsd | NAB | indexed_frac | – | 0.766 ± 0.0393 | 0.758 ± 0.036 | -0.9 |
| ebsd | NAB | kam_deg | – | 1.6781 ± 0.0246 | 1.6723 ± 0.0214 | -1.1 |
| ebsd | NAB | texture_mrd | – | 2.0697 ± 0.543 | 2.0750 ± 0.536 | +0.0 |
| xrd_part | AlSi10Mg | a_fcc_A | 4.0467 | 4.0467 ± 2.10e-04 | 4.0466 ± 1.93e-04 | -0.6 |
| xrd_part | AlSi10Mg | microstrain | – | 6.19e-04 ± 1.38e-04 | 5.66e-04 ± 1.62e-04 | -1.6 |
| xrd_part | AlSi10Mg | phase.Si | – | 0.0725 ± 0.00216 | 0.0741 ± 0.00251 | +3.0 |
| xrd_part | Scalmalloy | a_fcc_A | 4.0610 | 4.0609 ± 2.10e-04 | 4.0609 ± 1.66e-04 | +0.8 |
| xrd_part | Scalmalloy | microstrain | – | 5.16e-04 ± 1.25e-04 | 5.46e-04 ± 1.42e-04 | +1.0 |
| xrd_part | 7075 | a_fcc_A | 4.0542 | 4.0543 ± 1.81e-04 | 4.0542 ± 1.86e-04 | -1.3 |
| xrd_part | 7075 | microstrain | – | 5.61e-04 ± 1.11e-04 | 5.51e-04 ± 1.32e-04 | -0.4 |
| xrd_part | 7075 | phase.Al2Cu | – | 0.0131 ± 0.00177 | 0.0135 ± 0.0016 | +0.9 |
| xrd_part | 7075 | phase.MgZn2 (n 35/40) | – | 0.00628 ± 0.00117 | 0.00609 ± 9.14e-04 | -0.8 |
| xrd_part | 70-30 Cu-Ni | a_fcc_A | 3.5884 | 3.5884 ± 8.43e-05 | 3.5884 ± 1.63e-04 | +0.7 |
| xrd_part | 70-30 Cu-Ni | beta_prime_frac | 1.39e-04 | 0 ± 0 | 0 ± 0 | +nan |
| xrd_part | 70-30 Cu-Ni | microstrain | – | 5.55e-04 ± 5.79e-05 | 5.67e-04 ± 6.86e-05 | +0.8 |
| xrd_part | NAB | a_fcc_A | 3.6472 | 3.6471 ± 2.88e-04 | 3.6472 ± 1.59e-04 | +1.1 |
| xrd_part | NAB | beta_prime_frac | 0.306 | 0.294 ± 0.00456 | 0.293 ± 0.00454 | -0.8 |
| xrd_part | NAB | microstrain | – | 0.00114 ± 1.65e-04 | 9.90e-04 ± 1.33e-04 | -4.4 |

## Known limits (all modules)

* **The latent microstructure is a model of a model.** Its phases and fractions follow the truth's own closed forms
  (Scheil `eutectic_by`, the strength model's precipitate fractions), not a CALPHAD equilibrium or a precipitation
  kinetics code. Pore and crack geometries, grain shapes and textures are *assumed* families anchored on the papers
  cited.
* **Al parts are characterized in the condition the strength model describes** (the alloy family's standard
  treatment), with nothing in between. XRD, SEM and EBSD cannot see an as-built versus aged difference unless the
  campaign builds both.
* **Fast modes reproduce lite, not full.** The lite chain has coarser pixels, steps and channels and smaller fields,
  so its own biases (resolution-limited small pores, EBSD step size against grain size, XRD counting statistics)
  are what the fast mode samples.
* **Fast models are fitted across the whole space.** Per-alloy quirks of the lite chain average out:
  * the beta' share XRD reads for NAB
  * EBSD texture near random
  * XRF Fe in 70-30 Cu-Ni
  * EDS Zr near its LOD
  The table above shows where.
* **Rebuild the calibration if micro.py changes.** Each module's fast mode assumes the `micro.py` it was calibrated
  on: rerun `python -m twin.instruments.calibrate_micro` after editing the phase, pore or grain models.
* **No instrument drift or operator variation** between sessions, beyond what each module describes (EDS gain drift,
  XRD displacement, SEM field choice). There is no cross-instrument correlation through a shared mount or polish,
  except the one sample state they all read.
