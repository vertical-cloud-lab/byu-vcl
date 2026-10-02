# 2026-10-02 — What the manufacturers and the standards say would make the colour readings more accurate

Asked on [PR #202](https://github.com/vertical-cloud-lab/byu-vcl/pull/202) by @timothy-commins:

> please pull from manufacturer pages and acredited pages about what can get done to make the
> sensor more accurate. double check your info to make sure it is correct. Also look at what we
> have already done. Some things we have done have increased accuracy but maybe there is more we
> can do with those specific factors

No hardware moved. **How the sources were checked:** every quotation below was copied from a
downloaded copy of the source, and then searched for again, word for word, in a copy downloaded
separately (or, for web pages, in the saved page text) by [`check_quotes.py`](#how-the-quotes-were-checked).
Standards that are sold rather than published (ASTM, ISO, CIE) could only be read as their official
scope or preview pages; those rows say **scope only**, and nothing is claimed about the parts behind
the paywall.

## The number that says how far there is to go: black ÷ white

A zero reference should read close to zero. Published dried Mars black reflects **0.02** of what
titanium white does at 440–670 nm (the same reference spectra as every score since 09-30). Ours,
board lamp subtracted ([`analyse_source_checks.py`](analyse_source_checks.py) →
[`source-checks-2026-10-02.json`](source-checks-2026-10-02.json)):

| run | black ÷ white, 440–670 nm | white well's reading that isn't the white paint |
| --- | --- | --- |
| 09-30 15:47, white and black next to the colours, on the plate | 0.68–0.89 | 62–89% |
| **09-30 19:15, empty wells between the paints, on the plate** | **0.52–0.73** | **42–73%** |
| 10-01, z 125 (foot ~37 mm up) | 0.81–0.91 | 78–91% |
| 10-01, z 100 (foot ~12 mm up; best accuracy score of ten heights) | 0.66–0.83 | 59–83% |
| 10-01, z 92 (foot ~4.5 mm up) | 0.62–0.80 | 54–80% |
| 10-01, z 86.5 (pressed ~1 mm)¹ | 0.72–0.82 | 67–81% |

¹ The white was read before the H10 landing moved the enclosure on the nozzle, the black after it
([`landing_shift.py`](landing_shift.py)), so this row mixes two states.

The last column assumes every well reads `s + k·R`: `s` is light that doesn't depend on the paint
(through and across the plate, the deck, reflections inside the enclosure), `R` is the paint's
reflectance. Then black ÷ white = (s + k·R_black) / (s + k·R_white). The range covers R_black from
the published 0.02 up to 0.15, for a watered-down black that looks grey.

**So between about half and nine-tenths of what the sensor sees over the white well is not the white
paint.** The white/black correction cancels `s` only where it is the same in every well. It isn't:
it changes with the neighbours (09-30), with the height (10-01), with how the enclosure sits on the
nozzle (10-02), and with how much light a semi-opaque paint lets through from below. That is the
floor of 0.24–0.36 left after the correction. Every recommendation below either makes `s` smaller
or makes it the same in every well, and **black ÷ white measures the first in one run, with no
colours needed.** For comparison, the colour-measurement standard ISO 18314-1 describes the zero
reference as having "low to no reflectance (for example a black light trap)".

## Things we did that helped, and what the sources say is left in each

### 1. White and black reference wells — took out about half of the error

- **What we did and got:** with empty wells between the paints, the two-point correction halved the
  miss (0.29 → 0.14), the floor (0.55 → 0.27) and the squeeze (2.6× → 1.3×)
  ([`results-white-black-correction-2026-10-01.md`](results-white-black-correction-2026-10-01.md)).
- **The manufacturer calls this the simplest of its calibrations.** ams OSRAM's calibration note
  (AN000633 §2.4) names it the "Black/White Scale", `(X − Xmin)/(Xmax − Xmin)`, and goes on:
  > "The results in the diagram(s) are good for such a primitive correction method but can be better
  > using matrices. The difference between scale and matric methods is the number of used targets. A
  > higher number of reference targets can increase accuracy for calibration dramatically."
- **And it wants the references in the same conditions as the samples** (AN000633 §2.5):
  > "It is important to make all measurements with the Sensor and reference device under identical
  > conditions closed to the application. Each deviation from calibration and application decreases
  > the accuracy."
- **More along the same line:**
  1. **A black that is really black.** Ours reads 0.52–0.91 of the white where Mars black should read
     0.02. Liquitex itself describes Mars Black as "A dense opaque single pigment, with a brown
     undertone", so even undiluted it is a warm black, not a neutral one. Use it undiluted, or use a
     light trap (see the standards section).
  2. **A white that is really white and opaque.** Liquitex calls Titanium White "the strongest, most
     opaque of all whites"; watered down it lets the deck's light through. Use it undiluted, or an
     opaque white standard of known reflectance.
  3. **More references than two.** A matrix calibration needs at least as many targets as channels:
     "Be attended to the number of linearly independent targets, which must be greater than or equal
     to the number of filters used in the sensor to obtain a stable matrix" (AN000633, PDF p. 29), so
     8 or more. Mixtures of our own three paints, each measured once on a reference instrument, are
     what ams calls a "local correction" (§2.5); in its example, narrowing a 24-colour chart to the 12
     colours nearest one target cut that colour's error from ΔE 1.7 to 1.4. The reference "should be
     at least ten times more accurate or higher than the sensor requires" (§1.4). For scale, ams's own
     per-device calibration on a 24-patch colour chart reached "Average DeltaE 0,98487" and "Max
     DeltaE 2,30337" (AN000633, PDF p. 24).
  4. **A per-well empty reading before the paint goes in.** For liquids ams subtracts the empty
     container first: "The influences of the cuvette and the optical path should be eliminated using
     differential measurement. To do this, first measure the empty cuvette in the setup." (miniLiquid
     guide QG000121 §1). It is also what the AC's March 2026 recovery did, per well. It captures each
     position's own light; it cannot capture light that a paint lets through from below.
  5. **Read white and black in the same pick-up, at the same height, within ~10 min of the colours**
     (already the rule since 10-01; drift is −0.06%/min).

### 2. Empty wells between the paints — the black became the darkest well

- **What we did and got:** on 09-30, putting black paint in A5 took 7–13% off the empty well next to
  it, and white in A4 took 2–5% off the blue next to it
  ([`results-white-black-2026-09-30.md`](results-white-black-2026-09-30.md)). With empty wells
  between the paints the black became the darkest well in every channel, and the miss went from 0.20
  (references next to the colours) to 0.14
  ([`results-spaced-wells-2026-09-30.md`](results-spaced-wells-2026-09-30.md)).
- **The plate makers say clear plates leak the most light between wells.** Revvity's microplate
  guide (p. 9):
  > "Cross-talk occurs when light from one well travels through the well walls into adjacent wells and
  > is then detected, adding non-specific counts to that well."
  >
  > "Clear plates can have the highest cross talk, with black plates having the lowest. White plates
  > give medium cross-talk, with the magnitude of the cross-talk being dependent on the concentration
  > of titanium dioxide used as whitener."

  Corning, whose plate definition the protocols load (`corning_96_wellplate_360ul_flat`), says clear
  polystyrene plates "are used for cell culture and colorimetric (absorbance) assays", and of its
  black- and white-walled clear-bottom plates: "Opaque walls prevent well-to-well crosstalk".
- **More along the same line:** an opaque-walled plate. Solid black has the least cross-talk and
  lets nothing up from below; black walls with a clear bottom keep the option of a transmission
  reading later (the AC's 2026 run read through the plate with a light panel under it). Spacing
  should then matter much less; that is untested.

### 3. Blacking out the OT-2 — less stray light, steadier readings

- **What we did and got:** 28–35% less light at fixed spots over the base, and no pair of readings
  more than 0.24% apart on 10-01; no measurable colour gain on its own
  ([`results-blackout-2026-10-02.md`](results-blackout-2026-10-02.md)).
- **The manufacturer lists the light that's left as accuracy errors to remove.** AN000633 §1.3,
  "Disturbances", includes "Ambient Light" and "Reflections inside the Sensor System", and says "a
  verification and optimization process must correct or eliminate all these negative effects".
- **More along the same line:**
  1. **A defined backing under the plate.** Today the deck is the backing. Black paper (planned)
     stops deck light coming up through semi-opaque paint; ISO 13655 accepts black or white and asks
     for white when the sample is see-through (standards section below). Try both.
  2. **Black inside the enclosure's lower opening.** The enclosure is printed in white, so its inner
     walls bounce light towards the sensor: the "Reflections inside the Sensor System" item.
     (Upstream once printed a black enclosure. The only result on record is with the board's own LED
     switched on as well, which made similar colours harder to tell apart, so it says nothing about a
     black interior under the rail lights;
     [ac-dev-lab#152](https://github.com/AccelerationConsortium/ac-dev-lab/issues/152).)
  3. **Black paper instead of the brown cardboard**, then re-read the white and black.

### 4. Read height — z 100 scored best of ten heights; pressing onto the plate scored worst

- **What we did and got:** miss 0.12 at z 100 against 0.44 (corrected) pressed onto the plate; one
  hard landing moved the enclosure 0.7 mm on the nozzle and changed a reading by 12%
  ([`results-height-series-2026-10-01.md`](results-height-series-2026-10-01.md)).
- **The manufacturer explains why position and tilt change the colour.** The AS7341 package has a
  pinhole aperture, not a diffuser, and each colour channel is a different photodiode in a 4×4 array
  under that one pinhole. ams's optomechanical design note (AN001054 §5) says the angular response
  "is limited to ±40° over all the channels", and:
  > "Due to the structured detector (4 x 4 array), the field of view is individual for each
  > photodiode; almost symmetrical for the centered photodiodes and more asymmetrical for those in
  > distance to the center. To avoid a blurred imaging of a light source or its position onto the
  > sensors array the diffuser is also used"

  and, of a diffuser that is not perfectly Lambertian: "In the case of a tilted light incidence, the
  response may shift to an asymmetrical shape. This causes different color measurements in relation
  to the positioning light source and sensor and decreases the accuracy." Its Figure 10 shows a light
  source that is "partly shadowed blue channel; detected as yellowish light". The datasheet lists a
  half-cone angle of 40° "on the sensor".
- **More along the same line:**
  1. **A diffuser over the sensor** (next section). It is the manufacturer's fix for exactly this.
  2. **A fixed gap, never a press.** Read lifted (z 95–100 scored best) so nothing pushes the
     enclosure up the nozzle.
  3. **Limit what the sensor can see to one well.** If nothing in the enclosure narrows it, a 40°
     half-cone 12 mm up takes in a circle about 20 mm across, enough to include the neighbouring wells
     9 mm away (an estimate: how deep the sensor sits inside the enclosure isn't recorded). That fits z 100 still squeezing colours
     2.7×. A short matte-black tube under the sensor, as wide as a well, would narrow it.

### 5. Rail lights on — 5.6× the signal

- **What we did and got:** the rail lights are now the only light (10-01, lights off = board lamp
  only).
- **The manufacturer lists the light source's drift as an error.** AN000633 §1.3: "Temperature and
  ageing effects from Sensor and luminary (e.g. LEDs)"; §1.4: "The test setup should be stable and free
  of any disturbances and drifts."
- **More along the same line:** warm the rail lights up before the first reading. For its own liquid
  kit ams says "Switch them on and wait 30 minutes to get the working temperature." (QG000121 §7.6).
  Keep re-reading white and black within ~10 min of the colours, and record the rail light's spectrum
  once: it has little light at 410 nm, which is why that channel is unreliable. ams's balancing guide
  prefers broadband sources ("Width-banded light sources (e.g. D65, A, or high CRI LED)",
  QG000139, PDF p. 9).

### 6. Repeated readings — one landing repeats to 0.04–0.12%

- **Enough.** ams: "The higher the Gain and TINT, the better the ratio between signal and noise"
  (AN000633 §2.1), but the noise is already 100× smaller than the landing error. Average over
  separate landings instead, if contact readings are kept.
- **A free check that comes with every reading.** Each reading is two integrations (`F1F4CN`, then
  `F5F8CN`), and both measure the Clear and NIR channels, as in ams's own two-pass example (SMUX note
  AN000666). The firmware throws them away; comparing them between the two halves would flag light
  that changed mid-reading.

## New things the sources recommend that we haven't tried

1. **A diffuser over the sensor — the manufacturer's first requirement, and probably missing.**
   - Datasheet §11.3: "For optimal performance, an achromatic diffuser shall be placed above the
     device aperture. The recommended solution is a bulk diffuser that meets the minimum recommended
     scattering characteristic shown below."
   - AN001054 §3: "It is also important to note that the technical parameters listed in the datasheet
     [1] apply to a diffuser in front of the sensor. Different diffusers, and the use without a
     diffuser, lead to different sensor parameters." Every channel's figures in the datasheet carry
     the footnote "The following diffuser is used in final test on top of AS7341: ED1-C50". The kit's
     user guide puts it plainly: "Customers should add a diffuser in front of the sensor in the case
     of a nondiffusible application." (UG000400, PDF p. 5).
   - **Which kind.** For light whose direction changes, as ours does with height: "a volume diffuser
     with nearly Lambertian and achromatic characteristics is the best choice" (AN001054 §4), with
     "a smooth angular response (no spikes in the angular response curves) exceeding ±45° (FHWM)"
     (§3). The note's examples are "Lexan 8B28" opaque white film, 250 µm, and the Kimoto 100 PBU film
     on ams's own evaluation kit (125 µm, 66% transmission, 89.5% haze, 35.5° half-angle, Fig. 9).
   - **Costs:** a volume diffuser passes less light ("the transmission efficiency of cosine volume
     diffusers is smaller than 50%"), which is a reason to raise the gain (item 2), and fitting one
     "typically changes the calibration parameters and requires recalibration", so re-read white and
     black after.
   - The upstream build docs never mention one, and no photo on file shows the sensor side. **Check
     by looking up into the enclosure's opening:** a white film over the sensor means there is one; a
     small dark chip with a pinhole means there isn't.
2. **More counts, at one fixed gain, once [`../pico/`](../pico/) is flashed.**
   - ams: "The higher the counts (before saturation), the better the accuracy." (UG000400, PDF
     p. 40); its liquid guide aims "to achieve stable values for the sensor result to be greater than
     10,000 digits or more" (QG000121 §7.6). **Our brightest channel is 1,464–2,402 counts, 2–4% of
     full scale.** 512x instead of 256x roughly doubles that (typical ratio 7.75 ÷ 3.95); more needs a
     longer integration, e.g. `astep` 2999 with `atime` 255 is about 2.1 s per half-reading. Expect
     it to help the weak 410 nm channel, not the stray-light floor: gain scales both alike.
   - ams normalises every reading to "Basic_Counts" = raw counts ÷ (gain × integration time) and says
     "For all corrections and calibrations, always use Basic_Counts or other calculated values
     without dependence on the setup and parameters, especially for dynamic gain and the like."
   - **Pick one gain and keep it for references and samples alike.** The gains are not exact powers of
     two (Fig. 17: 256x is 3.75–4.25× the 64x response, 512x 7.25–8.25×), and ams's own published
     gain-correction tables disagree with each other in direction at 256x and 512x; its user guide
     says "Customers should verify them and make an individual gain correction in the case of the
     highest accuracy requirements." (UG000400, PDF p. 27). The chip's automatic gain control changes
     the gain between readings ("The gain from this status read is required to calculate spectral
     results if AGC is enabled"), so leave it off.
   - Check the saturation bit (`ASAT_STATUS`) in every reply; the firmware change already reports it.
3. **Auto-zero every cycle.** The datasheet's dark-count figures assume "auto zero done before every
   integration cycle" (`AZ_CONFIG` = 1), which resets the offsets "to compensate for changes of the
   device temperature". The upstream driver never writes that register, so it stays at its default,
   255: "Only before first measurement cycle". A one-line firmware change; cost ~15 ms per cycle.
4. **Paint that hides what is under it.** Liquitex rates all three colours **Semi-Opaque** (Primary
   Yellow PY74, Cadmium Red Medium Hue PR170 + PR9, Primary Blue PB15:3) and only the white and the
   black **Opaque**. Watered down, the colours let light through from below and the black doesn't,
   which is the floor. Less water, a defined backing (see the standards section), or both.
5. **Calibrate against a reference instrument and more targets** (item 3 of §1). ams calls a
   per-device calibration "the most complex but has the highest accuracy" (AN000633 §2.5).

## What the standards add

Standards bodies sell their standards, so only the official free preview pages were read (they
include the clauses quoted). The NIH guide is free in full.

- **The black and white references** (ISO 18314-1:2015, *Analytical colorimetry — Practical colour
  measurement*, §5.3–5.5):
  - "A black calibration standard is a standard which has low to no reflectance (for example a black
    light trap). Black calibration is used to establish a known zero point for the instrument."
    Watered-down Mars black is not that: it reads 0.52–0.91 of our white.
  - The white "is made of a durable material, like ceramic, glass, or enamel" and "has reflectance
    values that are traceable to a national standard". Watered-down paint in a clear well has no
    known reflectance, so our calibrated values can only be relative.
  - "When performing extended measurement series and/or under strongly varying environmental
    conditions (for example temperature) the white calibration shall be repeated in regular
    intervals."
  - "After certain time intervals it is recommended to verify the accuracy of the measurements
    through the use of coloured control standards." and "The white calibration standard may not be
    used for control measurements." We have never had a control: a few stable coloured samples read
    every run, separate from the white and black, would show whether a change helped.
- **The plate** (NIH/NCATS *Assay Guidance Manual*, "Microplate Selection and Recommended Practices",
  2020): "Clear microplates are typically used for absorbance (colorimetric)-based readouts." White
  plates "can reduce well-to-well crosstalk, while enhancing the luminescence signal by better
  reflecting the light"; black plates likewise reduce it. And: "Suboptimal choice of microplate
  color will often manifest as [1] lower signal-to-background ratios compared to the optimal
  microplate color, and/or [2] well-to-well crosstalk when highly active and inactive samples are
  adjacent to one another." That is the 09-30 neighbour effect, in a government guide. If a white
  plate is tried, note that "the color of white is not standardized in opaque microplates".
- **The backing under the plate** (ISO 13655:2017 §4.2.3): "The specimen shall be backed by either a
  black or a white material that conforms to A.2 or A.3", and "Where samples being measured by
  reflection are transparent, the backing used shall be white". So the standard asks for a *defined*
  backing, and for see-through samples a white one. Watered-down paint is partly see-through, so it
  is worth one run on black paper and one on white paper, judged by black ÷ white and the miss.
- **The geometry** (ISO 13655:2017 §4.2.4): "The measurement geometry shall be (45°:0°) or (0°:45°),
  annular or circumferential". Ours is neither: light from the rail lights overhead and from the deck
  below, with the sensor looking straight down. A ring of light at 45° around the sensor's view, with
  the rail lights off, would be the standard geometry. That is a bigger change than the others.
- **The liquid surface** (NIH guide): in top-read assays, "centrifugation will increase variability
  by creating uneven menisci across the microplate". Our sensor reads from the top, so keep every
  well's volume the same (200 µL) and free of bubbles.

## Our own check: the channel tolerance is not what limits the score

The datasheet guarantees each visible channel's centre wavelength only to **typ ± 10 nm** (Figs. 8–15:
e.g. F1 405/415/425 nm), "measured on a production ongoing sample bases on glass using diffused
light". Every score since 09-30 used the typical centres. Re-scoring with the passbands moved within
those limits ([`analyse_source_checks.py`](analyse_source_checks.py)):

| run | miss at typical centres | all channels −10 … +10 nm | each channel independently ±10 nm (5th–95th pct) |
| --- | --- | --- | --- |
| 09-30 19:15, spaced, on the plate | 0.142 | 0.155 … 0.127 | 0.135–0.149 |
| 10-01, z 100 | 0.118 | 0.118 … 0.126 | 0.114–0.125 |
| 10-01, z 125 | 0.154 | 0.162 … 0.147 | 0.148–0.159 |

A single published value moves by up to 0.10 (yellow at 510 nm, red at 620 nm, on the steep edges),
but the run's miss moves by at most ±0.015. **The error we see is the setup's, not the datasheet
tolerance's.** Measuring our unit's channel centres would matter only once the rest is fixed.

## Earlier claims on PR #202, re-checked against the sources

| claim (where) | verdict |
| --- | --- |
| gain ratios: 256x is 3.75–4.25× and 512x 7.25–8.25× the 64x response (10-01) | **right** (DS000504 Fig. 17; typical 3.95 and 7.75) |
| the chip's power-on gain is code 9 = 256x, and `set_again(128)` is ignored (10-01) | **right** (CFG1 0xAA default 9; upstream `set_again` only writes codes 0–10) |
| every channel's figures are measured with an ED1-C50 diffuser on top (10-01) | **right** (footnote to Figs. 8–15) |
| "nano-optic deposited interference" filters behind a built-in aperture; 40° half-cone (10-01) | **right** (§1 and p. 15) |
| dark counts 0–3 (ADC 0–4) and 0–5 (ADC 5) at 512x and 98 ms, auto-zero before every integration (10-01) | **right about the datasheet, but it doesn't describe our board**: the spec assumes `AZ_CONFIG` = 1, and our firmware leaves it at 255 |
| the chip is "rated −30 to 85 °C" (10-01) | **imprecise**: 85 °C is the absolute maximum; the operating range is −30 to 70 °C, with "functionality will vary with temperature". The datasheet gives no temperature coefficient |
| the AS7341's own LED was "rejected for saturating the enclosure walls" (09-12, `accuracy-provenance.md`) | **overstated**: upstream it raised most channels to 10k–20k counts (410 nm to ~2k; of 65,535, so not saturated) "possibly due to reflection from the enclosure walls", and the colours stopped being distinguishable ([ac-dev-lab#87](https://github.com/AccelerationConsortium/ac-dev-lab/issues/87)) |
| the green power LED is a fixed offset that the white/black correction cancels (10-02) | **right**; and Adafruit's newer boards have "a cuttable jumper to disable the onboard ON power LED" if it is ever wanted gone |

## How the quotes were checked

1. Each source was downloaded and converted to text twice, with `pdftotext -layout` and with plain
   `pdftotext` (web pages: their saved text).
2. The ams documents were downloaded a second time, separately, from ams's own site, and the two
   copies compared byte for byte; they were identical.
3. Every quotation in this file was then searched for in those texts, with only whitespace,
   line-break hyphens, quote marks and ligatures normalised:
   [`check_quotes.py`](check_quotes.py) with the list in
   [`accuracy-sources-quotes-2026-10-02.json`](accuracy-sources-quotes-2026-10-02.json). All were
   found. One (Revvity's "medium cross-talk") matches only with the line-break hyphen ignored, which is
   how that PDF breaks the word.
4. Numbers read from figures (gain ratios, centre wavelengths, dark counts) were also checked against
   the table's column positions, since `pdftotext` can shift a value into the wrong column.

The sources are not copied into the repository. To re-run the check, download them from the links
below into one folder and run `python3 check_quotes.py accuracy-sources-quotes-2026-10-02.json --dir
<folder>`.

## Sources

**Manufacturer: ams OSRAM (the AS7341)**, all from ams-osram.com:

| short name | document | used for |
| --- | --- | --- |
| DS000504 | [AS7341 datasheet](https://look.ams-osram.com/m/24266a3e584de4db/original/AS7341-DS000504.pdf), v3-00, 2020-06-25 (current) | gain ratios, centre-wavelength limits, dark counts, half-cone angle, auto-zero, AGC, saturation, §11.3 diffuser |
| AN001054 | [AS7341 Details for Optomechanical Design](https://look.ams-osram.com/m/436a32f63ba06bad/original/AS7341-Details-for-Optomechanical-Design.pdf), v1-00, 2022-09-21 | diffuser requirement, angle of incidence, per-photodiode field of view |
| AN000633 | [Spectral Sensor Calibration Methods](https://look.ams-osram.com/m/269928fe0dba7511/original/Spectral-Sensor-Calibration-Methods.pdf), v2-00, 2021-05-20 | disturbances, Basic_Counts, black/white scale, matrix calibration, reference instrument |
| UG000400 | [AS7341 Evaluation Kit user guide](https://look.ams-osram.com/m/2a3e700eb3b0a0cf/original/AS7341_UG000400_6-00.pdf), v6-00, 2022-09-08 | counts vs accuracy, diffuser, gain correction |
| QG000121 | [miniLiquid – Measurement in Liquids](https://look.ams-osram.com/m/dfeb820072a6e472/original/SpectralSensing_QG000121_2-00.pdf), v2-00, 2021-01-11 | empty-container subtraction, warm-up, count level |
| AN000660 | [AS7341 Demo for Fast Measurement Using Unicom Board](https://look.ams-osram.com/m/7dd996b7759236a3/original/AS7341-Demo-for-Fast-Measurement-Using-Unicom-Board.pdf), v1-00, 2019-12-09 | one of ams's gain-correction tables |
| QG000139, AN000666, ChipLib docs | inside the evaluation-software downloads on the [AS7341 product page](https://ams-osram.com/products/sensor-solutions/ambient-light-color-spectral-proximity-sensors/ams-as7341-11-channel-spectral-color-sensor) (ALS bundle v1-26-3) | broadband light for balancing; the two-pass SMUX example; the other gain-correction table |

**Other manufacturers**

| maker | page | used for |
| --- | --- | --- |
| Adafruit (the breakout board) | [product 4698](https://www.adafruit.com/product/4698) | the power-LED jumper |
| Revvity (microplates) | [Guide to selecting a microplate](https://resources.revvity.com/pdfs/gde-selecting-a-mircoplate.pdf), p. 9 | well-to-well cross-talk by plate colour |
| Corning (microplates) | [Microplate Selection Guide](https://www.fishersci.com/content/dam/fssite/north-america/us/documents/brands/c/corning/corning-microplate-selection-guide.pdf), CLS-MP-014 REV7, ©2011, pp. 6, 10 (via Fisher Scientific; corning.com refused the download) | clear plates for absorbance; opaque walls prevent cross-talk; solid black/white plates of the same standard 360 µL flat-well format (e.g. 3915 black, 3912 white) |
| Liquitex (the paints) | product pages for BASICS [Primary Yellow](https://www.liquitex.com/products/basics-acrylic-color-primary-yellow), [Cadmium Red Medium Hue](https://www.liquitex.com/products/basics-acrylic-color-cadmium-red-medium-hue), [Primary Blue](https://www.liquitex.com/products/basics-acrylic-color-primary-blue), [Titanium White](https://www.liquitex.com/products/basics-acrylic-color-titanium-white), [Mars Black](https://www.liquitex.com/products/basics-acrylic-color-mars-black) | opacity ratings, pigments |

**Standards and metrology**

| source | read | used for |
| --- | --- | --- |
| ISO 13655:2017, *Graphic technology — Spectral measurement and colorimetric computation for graphic arts images*, §4.2.3–4.2.4 | the official free preview pages ([iTeh](https://standards.iteh.ai/catalog/standards/sist/960e390f-2252-4af2-bbd1-167266af6cc0/iso-13655-2017)) | defined black or white backing; 45°:0° geometry |
| ISO 18314-1:2015, *Analytical colorimetry — Part 1: Practical colour measurement*, §5.3–5.5 | the official free preview pages ([iTeh](https://standards.iteh.ai/catalog/standards/sist/0f146362-4c3a-4d22-9ac1-584728b0d5ee/iso-18314-1-2015)) | white standard, black light trap, recalibration interval, coloured control standards |
| Auld DS *et al.*, "Microplate Selection and Recommended Practices in High-throughput Screening and Quantitative Biology", *Assay Guidance Manual*, NIH/NCATS, 2020 | [full text](https://www.ncbi.nlm.nih.gov/books/NBK558077/) | plate colour and cross-talk; menisci in top-read assays |

**Upstream and this repository**

- [ac-dev-lab#87](https://github.com/AccelerationConsortium/ac-dev-lab/issues/87) and
  [#152](https://github.com/AccelerationConsortium/ac-dev-lab/issues/152): the board-LED and
  black-enclosure tests.
- [`wireless-color-sensor@07efedd`](https://github.com/AccelerationConsortium/wireless-color-sensor/tree/07efedd7302bd1def93ef81ceadba38e1ae96853/sensor_file):
  `lib/as7341.py` (never writes `AZ_CONFIG`; `set_again` takes codes 0–10).
