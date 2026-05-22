# BYU VCL SEM/EDS standard workflow parameters — Edison literature query

Response to https://github.com/vertical-cloud-lab/byu-vcl/pull/93#issuecomment-4523120846 (which references the issue #77 thread on standardizing magnification levels and other SEM/EDS workflow parameters for our powder + printed-part samples).

One Edison `LITERATURE_HIGH` task was submitted on 2026-05-22; it completed successfully (~24 min, ~47 kB answer with ~12 citation tables).

| Field | Value |
|---|---|
| Task ID | `2c752db2-d735-4937-b1b2-dc35eb0cad88` |
| Status | ✅ success |
| Tags | byu-vcl, SOP, SEM, EDS, magnification, pr-93 |

The full answer (with `pages X-Y`-style citations the team can cross-check) is retrievable via:

```python
import uuid, os
from edison_client import EdisonClient
client = EdisonClient(api_key=os.environ["EDISON_API_KEY"])
r = client.get_task(uuid.UUID("2c752db2-d735-4937-b1b2-dc35eb0cad88"))
print(r.answer)
```

This document is a *summary + recommendations* — not a verbatim copy of the answer.

## Scope of the query

We asked Edison for a literature-backed, parameter-by-parameter SOP covering:

1. **Magnification levels** (powder feedstock; polished cross-sections; EDS quant vs. mapping; scout-to-detail ladder).
2. **Imaging parameters** (kV, beam current, WD, lens mode, dwell/frame integration, tilt/TOA).
3. **EDS-specific parameters** (live time, amp time, resolution, background windows, element list, replicate count).
4. **Sample-type deviations** (trace work, light-element work, phase-specific quant, powder vs. polished XS vs. as-printed).
5. **QA/QC and SOP structure** (pre-session, mid-session, calibration cadence, mandatory metadata, ICP-OES/WDS cross-validation).
6. **Existing standards** to cite (ASTM E1508, E1078, E1245, E2109, B214/B243, F3049/F3122/F2792; ISO 13322; Goldstein et al.).

## Recommended scout-to-detail magnification ladder

This is the single most actionable answer to Gage's question. It gives one consistent ladder for *both* powders and printed parts, with the data product at each level:

| Mag | HFW | Sample(s) | What it captures | Detector | Default kV |
|---|---|---|---|---|---|
| **50–100×** | ~3–6 mm | Powder + part | **Scout/overview.** Powder: panorama for apparent particle size distribution + morphology batch screening. Part: whole-cross-section overview, scan strategy, large-scale fishscale pattern, macro-defect context. *Always the first image in a session and archived.* | SE or BSE | 15 kV |
| **250–500×** | ~0.6–1.2 mm | Powder + part | **Morphology / defect-field survey.** Powder: satellite/spatter content, agglomeration, broad shape class. Part: melt-pool fishscale, lack-of-fusion + gas-porosity field survey. ASTM E1245 / E2109 representative fields. | BSE preferred | 15 kV |
| **1 000–2 500×** | ~120–300 µm | Powder + part | **Particle surface / individual melt pools.** Powder: particle surface texture, fine satellites, surface oxide texture. Part: individual melt-pool boundaries, coarse porosity (>10 µm), inter-track bonding. Good bridge between morphology imaging and EDS targeting. | SE + BSE | 15–20 kV |
| **5 000–10 000×** | ~30–60 µm | Polished XS | **Substructure + EDS spots.** Cellular/dendritic structure within melt pools, eutectic Si network in AlSi10Mg, microsegregation context. **Primary range for EDS point-quant on flat polished areas.** | BSE + EDS spot | 15–20 kV |
| **20 000–50 000×** | ~6–15 µm | Polished XS | **Fine precipitates.** Intermetallics (Fe-bearing phases, Mg₂Si), nanoscale cellular boundaries. **Phase-specific EDS spot — only valid when feature ≫ ~1–3 µm interaction volume at 15 kV; otherwise drop to 10 kV or stop reporting phase-pure composition.** | BSE + EDS spot | 15–20 kV (10 kV for sub-µm features) |
| **EDS map mode** | 500–5 000× typical | Both | Compositional mapping for Si/Mg/Fe segregation and contamination screening. Match pixel size to interaction volume; ≥512×384 pixels; record dwell + integration. | EDS map | 15–20 kV |
| **EDS spot quant** | 2 500–10 000× | Both | Routine point analysis. ≥60 s live, target ≥1 M total counts, ≥10 spots/sample for polished XS, ≥20 for powder. | EDS spot | 15–20 kV |

**Key rationale:** SEM-based PSD per ISO 13322-1 needs the 50–500× overview pair (Carlton 2011, ASTM F3049). LPBF AlSi10Mg cellular substructure resolves at 5–10 k× (Qin 2020, Hyer 2020). At >20 k× the interaction volume (~1–3 µm at 15 kV) becomes the resolution-limiting factor for EDS, not the beam (Small 2002, Burgess 2017).

## Default "fixed" parameters for a standard EDS session

These should be **the same** for every routine session unless there is a documented reason to change. Numbers below are the literature defaults; the lab can tighten to the BYU EML reality.

| Item | Standard | Acceptable range | Why |
|---|---|---|---|
| Accelerating voltage | **15 kV** (Al/Ti); **20 kV** (Ni/Fe alloys) | 10–25 kV | Overvoltage rule (E₀ ≥ 1.5–2× highest line of interest). Al overshoots 8× at 15 kV; steels need 20 kV for Cr/Ni/Mo/Fe. |
| Working distance | **10 mm analytical WD** | 10–15 mm fixed | EDS detector solid angle scales as A/r²; mixing WDs within a dataset breaks comparability. |
| Take-off angle | **~35°** (instrument-fixed) | not user-tunable | Treat as geometry constant; same for standards + unknowns. |
| Tilt | **0°** | 0° preferred | Even modest tilt creates large composition errors for low-energy lines. |
| Amp / shaping time | **3.84 µs** | 0.96–7.68 µs | 3.84 µs is the routine-quant compromise. Drop to 0.96–1.92 µs for fast maps; raise to 7.68 µs for trace/minor work. |
| Live time | **60 s minimum, 100 s preferred** for routine quant | 30–300 s | 30 s = scout only. ≥200 s for Mg-in-Al trace work. |
| Target counts | **≥1 M total / ≥10 000 net per peak** | 100 k–5 M | ≥10 k net counts ≈ 1 % relative counting precision. |
| Detector dead time | **~10 %** | 5–15 % for quant; up to 25 % acceptable for mapping | Newbury & Ritchie's modern-SDD recommendation. Above 15 % creates significant Al+Al / Si+Si sum peaks. Don't blindly follow ASTM E1508's older 20–30 % Si(Li) target. |
| Detector FWHM (Mn Kα) | **≤130 eV** | ≤128–130 eV preferred; ≤135 eV acceptable | Health-check threshold; trigger recalibration / service if it drifts. |
| Replicates | **≥10 spots/sample** (polished XS); **≥20** (powder) | scale with heterogeneity | Powder lots vary particle-to-particle; replication is mandatory, not optional. |
| Carbon coat | **~7–10 nm** on polished mounts; uncoated for conductive powders on C-tape | 5–12 nm | Coating consistency matters for low-energy quant. |

## Default "tunable" parameters per sample type

These are the levers we adjust per material/feature; an SOP should specify the decision criteria, not a single value:

| Lever | When to change | What to do |
|---|---|---|
| **Beam current / spot size** | Always tune per session | Set on a high-flux standard (pure Al, Si, or Cu) at analytical WD to hit ~10 % dead time. Typically 0.5–1.5 nA on the Apreo with the 30 mm² Octane Plus. Keep the same current for standards and unknowns. |
| **kV** | Per material class + per feature size | 15 kV for Al/Ti; 20 kV for Ni/Fe; **drop to 5–10 kV** for light-element work (O/N/C, thin oxide layers) or sub-µm features where interaction volume is limiting. |
| **Live time** | Per element abundance | 60 s for major/minor; 200–300 s for trace (Mg in Al, Y in Ni-base, <0.1 wt% impurities). |
| **Map dwell / pixel count** | Per map purpose | 50–200 µs/pixel × 512×384 for routine; up to 200 ms/pixel × 2048×1557 for publication-grade maps. Add drift correction on long maps. |
| **Magnification for quant spot** | Per phase-of-interest size | 5–10 k× for cellular-scale phases; 20–50 k× for sub-µm precipitates (with the caveat above re: interaction volume — reduce kV or report "matrix-averaged" instead of phase-pure). |

## QA / QC that should appear in the written SOP

Edison's answer enumerated a clean structure that matches what we already lean on in `eds-cross-comparison-edison-queries.md` and `eds-quantitative-analysis-alsi10mg.md`:

**Pre-session checklist** (every session):
1. Chamber vacuum < 5×10⁻⁴ Pa, stable for ≥5 min.
2. Gun emission stable; record Schottky-tip hours if approaching service interval.
3. SDD cooled and thermally stable.
4. **Energy calibration** on a Cu standard: confirm Cu Lα ≈ 0.930 keV and Cu Kα ≈ 8.04 keV in a 30 s spectrum.
5. **Resolution check**: Mn Kα FWHM ≤ 130 eV on a Mn standard (or read from the Cu spectrum at Kα). Typical "good" SDD ≈ 127.5–128 eV.
6. **Beam current** measured with Faraday cup, recorded in nA.
7. **Dead-time check**: on pure Al or Si, tune current so meter reads ~10 % at the analytical WD.

**Within-session checks**:
- Re-measure a reference standard (e.g., Cu or the in-session Al standard) mid-session if running >2 h.
- After every sample change: re-verify dead time and WD before the first spectrum.

**Calibration cadence**:
- Energy + resolution: per session.
- Faraday-cup beam-current measurement: per session if doing quant.
- Full standard-set re-acquisition: per shift or per major-parameter change.

**Mandatory metadata** (saved alongside every spectrum/image):
- `kV, beam_current_nA, working_distance_mm, magnification, HFW_um, dwell_us, frame_avg, amp_time_us, live_time_s, dead_time_pct, take_off_angle_deg, date, operator, detector_serial, software_version`
- Plus the raw outputs: `.msa` + `.spc` (or vendor equivalent), `.tif` (16-bit), and the vendor-generated PDF if any.

**Cross-validation cadence**:
- ICP-OES on every new powder lot and on each printed-part qualification build (expect ±3–5 % relative on Mg at 0.2–0.45 wt%).
- WDS verification only when EDS-derived composition has to be defensible to ±1 % absolute (e.g., qualification per AMS 7032 / 7034 or aerospace acceptance).

## Standards & references the answer pulled from

ASTM **E1508** (quantitative EDS), **E1078** (specimen prep), **E1245** (inclusion image analysis), **E2109** (phase fraction by image analysis), **B214** / **B243** (powder PSD by sieve), **F3049** (powder characterization for AM), **F3122** / **F2792** (AM terminology). ISO **13322-1** / **-2** (particle size by image analysis). Goldstein, Newbury, Joy *Scanning Electron Microscopy and X-ray Microanalysis* (4th ed.). Newbury & Ritchie 2013/2014/2015/2019. Carlton 2011 (SEM imaging). Burgess 2017 (low-kV EDS). Camus 2007 (acquisition-parameter trade-offs). Guyett 2024 (modern SDD optimization). Garzon 2023 (parameter variations for steels). Hyer 2020 + Qin 2020 + Cauwenbergh 2021 (LPBF AlSi10Mg microstructure). Giunto 2026 (accurate SEM-EDS quant).

## Recommendations (concrete next steps for the lab)

1. **Adopt the scout-to-detail ladder verbatim.** It is one row per data product and matches both the ASTM image-analysis standards and what AlSi10Mg LPBF papers actually publish.
2. **Build a one-page printed quick-reference card** from the table in §"Default fixed parameters" above. Pin it next to the Apreo. The Edison response has a 31-row card-ready table (see `pages 303–335` of the raw answer) that we can lift directly.
3. **Standardize on 15 kV / 10 mm WD / 3.84 µs / ≥60 s live / ~10 % DT** as the universal-default EDS settings. The 0.96 µs amp time used on the May 22 polished sample is a *known deviation* (faster mapping mode) and should be flagged in any SOP.
4. **Make dead-time tuning explicit in the SOP.** Each session must start with "tune current to ~10 % DT on a pure Al/Si/Cu standard at analytical WD." This is the single biggest reproducibility win available — it locks the spectrum quality regardless of detector state or sample geometry.
5. **Mandate `.msa` raw export** for every quant report so we (or Edison Analysis crow) can re-fit later. This is exactly what enabled the corrected Mg ≈ 0.8 wt% re-fit in [`eds-cross-comparison-edison-results.md`](./eds-cross-comparison-edison-results.md).
6. **Replicate count**: enforce ≥10 spots per polished cross-section / ≥20 spots per powder sample as a precondition for reporting a "measured composition" — anything less is a scout, not a measurement.
7. **Add an explicit "deviation log" column** to every saved metadata record so non-default parameters (e.g., 10 kV for light-element work, 7.68 µs for trace-Mg work) are searchable.
8. **Spot-check with Mike Standing's group.** This SOP would benefit from one calibration session against their established procedures before being adopted as the lab default — particularly the dead-time target (we are recommending the modern Newbury & Ritchie ~10 %, which is tighter than ASTM E1508's 20–30 %).
9. **Cross-link** this document into the lab-onboarding README and the Genesis-proposal narrative on QA infrastructure.

## Open questions to bring back to the team

- Does the BYU EML Apreo have a Faraday cup mounted on its stage holder, or do we need to add one? (Required for the beam-current step.)
- What standards does the EML stock? At minimum we need pure Al, pure Si, pure Cu, and ideally MgO + NIST K412 glass for the Mg-in-Al overlap work.
- What is the actual analytical WD recommended by EDAX for the Octane Plus on this Apreo? (We've assumed 10 mm; confirm with the vendor calibration sheet.)
- What is the lab's preferred polished-sample mount geometry (epoxy puck vs. clip-on)? Affects WD reproducibility.
- Is there appetite to formalize this as a numbered SOP in the lab QMS, or keep it as a living markdown doc in this repo?
