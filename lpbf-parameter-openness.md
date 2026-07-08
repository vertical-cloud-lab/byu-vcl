# LPBF printer candidates — openness of process parameters

Research compiled 2026-07-08 from vendor websites, datasheets, and published literature, in support of the printer acquisition (issue #61). Motivating requirement: ability to modify **hatch angle / interlayer hatch rotation** (see PR #95 discussion), and more generally whether exposure parameters (laser power, scan speed, hatch spacing, scan strategy, layer thickness) are user-editable, and whether vendor material parameter sets are viewable or locked.

Everything below is from public sources; items marked **unverified** could not be confirmed publicly and should be asked directly during the quoting process.

## TL;DR comparison

| System | Hatch angle / rotation editable? | Overall parameter access | Factory material sets | Third-party powder | Extra cost for open parameters? |
|---|---|---|---|---|---|
| **Aconity MIDI** | ✅ Confirmed (studies used 0°/45°/67°/90° rotations) | Fully open + Python API, per-part & per-layer control | Open, no locked database | ✅ Confirmed in practice | No — openness is the product |
| **Renishaw AM 250** (used) | ✅ Confirmed (67°/layer is a user-set value) | ~170 user-controllable parameters; editable material files | Editable ("copy and edit materials files") | ✅ Confirmed in literature | No, but machine is end-of-support (see risks) |
| **SLM Solutions SLM 125** | ⚠️ Strongly implied, not line-item verified | >200 editable parameters via Material Development Module | Standard sets provided; run as-is or customize | ✅ Explicit "materials from any supplier" policy | MDM may be an optional module (**unverified**) |
| **EOS M 290** | ✅ Confirmed — but only with paid EOS Build+ tier | Full ParameterEditor (~258 params) with Build+; Basic tier = process settings only, no exposure editing | Editable starting points under Build+; use-only under Basic | Possible via Material Set Configurator; warranty impact **unverified** | **Yes** — annual Build+ subscription |
| **EOS M 100** | ⚠️ Inferred via EOSPRINT 2; not directly documented | Legacy per-material ParameterEditor packages; not covered by current EOS plans | Locked IndustryLine sets at launch; editing sold per material | Same mechanism as M 290 | Yes — per-material packages (legacy licensing) |
| **Farsoon FS191M** | ⚠️ Implied ("scanning path parameters"), not named | "Open for Industry": MakeStar expert mode, 100+ open parameters, Parameter Editor included | Accessible and tunable, not encrypted | ✅ Explicit open-material policy | No (expert mode vs. production mode; confirm it ships enabled) |
| **Xact Metal XM200** | ⚠️ Lives in Materialise build processor, not confirmed | Machine-side live-adjust = power/speed/recoat/bed temp only, **with purchased open-parameters package**; hatching set upstream in Magics | ✅ Published free via web app | ✅ "Use their own powder" (datasheet) | **Yes** — "open parameters package" (price unpublished) |
| **2OneLab 2CREATE** | ⚠️ Implied ("complete control over all parameters e.g. hatching"; per-vector G-code) | Open; G-code export, one command per laser vector; DoE module | Provided free, user-visible/editable | ✅ Explicit "powders from any supplier" | Not indicated (**license model unverified**) |
| **Concept Laser M2** (2017, used) | ❌ Not in free tier (5 params only); requires paid CL WRX Parameter | Free tier: laser power, scan speed, hatch spacing, spot size, contour offset ONLY | Sold per material (1 quality + 1 speed set free with machine) | Only practical with CL WRX Parameter license | **Yes** — CL WRX Parameter license + mandatory training; time-limited license |
| **Mastrex MX100/MX220** | ❓ Nothing published | Nothing published beyond "pre-qualified parameters with open configuration options" (press quote) | **Unverified** | **Unverified**; warranty voids on "unapproved third-party components" | Unknown — must ask vendor |

Legend: ✅ publicly confirmed · ⚠️ likely but not explicitly documented · ❌ confirmed limitation · ❓ no public information

## Per-machine details

### Aconity3D AconityMIDI — most open, purpose-built for parameter research

- Datasheet line item: "FULLY ADAPTABLE PROCESS PARAMETERS"; AconitySTUDIO web software gives "access to all relevant process parameters and machine components" ([datasheet PDF](https://configurator-api.aconity3d.com/storage/documents/configurator-machines/gxPFMisXKEtzchm0/AconityMIDI+_2022.pdf), [CMU equipment page](https://engineering.cmu.edu/mfi/facilities/equipment-details/aconity-midi.html)).
- Hatch angle and interlayer rotation confirmed user-set: published studies configured 0°/90° hatch with and without 67°/90° interlayer rotation ([ResearchGate](https://www.researchgate.net/figure/AconityMIDI-parameters-used-for-the-single-scans-and-3D-parts-on-plates_tbl1_388831884)), and orthogonal / 45°-rotated / parallel strategies ([Springer](https://link.springer.com/article/10.1007/s40964-025-01156-8)).
- Official **Python API**: `change_part_parameter()`, `change_global_parameter()`, start/pause/resume, execution scripts; demonstrated real-time layer-wise closed-loop parameter control ([API docs](https://aconity-control.readthedocs.io/en/latest/aconityapi.html)) — directly relevant to our programmatic-control requirement.
- Per-part parameter sets and mixed layer thicknesses within one job (AconitySTUDIO 3.4 release notes).
- Third-party powder confirmed in practice (e.g., [Equispheres aluminum](https://equispheres.com/aconity3d/)); universities routinely run experimental alloys.
- Quote gathered so far: ~$350k ("Anaconda mini" in the thread = AconityMINI/MIDI).

### Renishaw AM 250 (used) — open parameters, but end-of-life risk

- "User is able to control up to 170 parameters, fully utilizing Renishaw's open source parameter ethos"; material files "freely designed and edited" ([TCT, Materialise Renishaw Build Processor](https://www.tctmagazine.com/materialise-introduces-the-renishaw-build-processor/)).
- Hatch rotation confirmed user-set: AA2024 study on an AM250 varied power 100–200 W, hatch spacing 40–100 µm, and set "fill-hatch angle rotated 67° at each layer" ([Springer](https://link.springer.com/article/10.1007/s00170-020-06346-y)) — also demonstrates third-party (LPW) powder of a non-catalog alloy.
- Note: modulated/pulsed laser — "scan speed" is set indirectly via point distance + exposure time.
- **Risks for a used unit:** Renishaw has ceased AM 250 support (third parties like [Thinklaser](https://thinklaser.com/news/renishaw-am-250-optical-support/) now cover optics); original AutoFab software is effectively abandonware; current QuantAM marketing only mentions RenAM 500 series; dongle/license transfer to a second-hand buyer is **unverified** — must ask Renishaw and the reseller before purchase.

### SLM Solutions (Nikon) SLM 125 — open by design, current product

- Official brochure: "open software architecture… choice of running standard parameters or to customize"; "**Material development module to edit over 200 process parameters**" ([brochure PDF](https://nikon-slm-solutions.com/wp-content/uploads/2024/04/Nikon-SLM-System-Brochure-SLM125-V3.pdf)).
- Explicit open-powder policy: "All machines allow the use of materials from any supplier… flexibility to develop new alloys" (same brochure). Reactive materials (Al, Ti) supported.
- Hatch rotation not line-item verified publicly (build-processor manual is not public) — ask at quote stage.
- **Unverified:** some distributor pages describe the parameter-configuration software as "optional" — confirm the Material Development Module is included in the quote, not an add-on.

### EOS M 290 / M 100 — open only at the paid tier

- Parameter access is governed by software licensing. **EOS Build+** (paid subscription, 1-year minimum on new machines) unlocks the full ParameterEditor: laser power, scan speed, hatch distance for all exposure types, and explicitly "**Hatch Option e.g. Hatch Rotation angle, Hatch offset**", variable layer thickness, all exposure patterns — ~258 parameters ([EOS Plans comparison](https://www.eos.info/eos-plans), [EOSPRINT 2 brochure](https://www.eos.info/04_consulting_service_software/software/pdf_software/brochure_eosprint_en_web.pdf): "vary the start and rotating angle for stripe patterns").
- **EOS Build Basic** (fallback tier): process settings only — no exposure-parameter editing, one frozen material. Hatch angle NOT editable at this tier.
- Also a Toolpath API (2025, via EOS Developer Network) for scan-vector-level access — relevant to programmatic control.
- Third-party powder is supported mechanically (Material Set Configurator, "CustomAr/CustomN2" material declarations); warranty implications not published. This matches the note in this thread that the M 290 is cheaper "if we could seat our own powders."
- **M 100** is discontinued, dental-focused, and absent from current EOS Build plans — a refurb unit would rely on legacy per-material ParameterEditor licenses. At launch it shipped one locked CoCr parameter set ([M 100 technical description](https://images-eu.ssl-images-amazon.com/images/I/919nxYIEJIS.pdf)).

### Farsoon FS191M — genuinely open, newer platform

- The "FS191" in our quotes is the **FS191M** (Formnext 2024; ⌀191 × 199 mm build, optional ⌀78 mm R&D platform, 500 W).
- MakeStar control software is "fully open… laser parameters, scanning path parameters, powder parameters, size compensation, heating parameters" — 100+ open parameters, with an "advanced expert mode [enabling] full access to all parameters" alongside a locked production mode; Parameter Editor included with access to standard material configs plus third-party material tuning ([Farsoon software page](https://www.farsoon-gl.com/software/)).
- Hatch angle not explicitly named ("scanning path parameters" implies it) — confirm at quote stage, along with whether the FS191M ships with expert mode enabled.
- Quote gathered so far: ~$145k — currently the best publicly-documented openness per dollar among the new machines.

### Xact Metal XM200 — "open" is a purchased add-on, split across two programs

- Datasheet: "Open platform provides qualified users the ability to develop their own printing parameters and use their own powder" ([XM200S datasheet](https://3dprinting.co.uk/wp-content/uploads/2019/05/2590-Xact-Metal-XM200S-Product-Sheet-High-Res-20190502.pdf)).
- Caveat 1: machine-side live adjustment (bed temp, melting power, scan speed, recoat speed) requires **purchasing the "open parameters package"** ([Xact software page](https://xactmetal.com/software-2/)).
- Caveat 2: hatching (spacing, pattern, presumably rotation) is defined upstream in the bundled **Materialise Magics Print** build processor, not on the machine — hatch-angle access depends on the Materialise profile editor and is not explicitly confirmed.
- Positive: factory exposure parameters for recommended powders are **published free** via a web app ([XM200G page](https://xactmetal.com/xm200g-%C2%B5hd/)) — no black-box material sets.

### 2OneLab 2CREATE — open, dental-first but not dental-locked

- 2BUILD CAM: "Complete control over all parameters (e.g. hatching, contour)"; exports print data as G-code with one command per laser vector, so toolpath geometry is fully user-determined ([2BUILD page](https://2onelab.com/software/2build/), [Proto3000](https://proto3000.com/product/2onelab-2create/)).
- Explicit open-material system: "powders from any supplier." Parameter sets provided free and user-editable; includes an automated DoE "Parameters Development Module" — attractive for our campaign-style experiments.
- Hatch angle as a named UI field is unverified; license model for 2BUILD unpublished. Quote so far: $175–275k.

### Concept Laser M2 Cusing (2017, used) — most restrictive of the candidates

- Free tier (CL WRX Control): only 5 adjustable parameters — laser power, scan speed, trace (hatch) spacing, spot size, contour offset. **No hatch angle.** Full access requires the paid **CL WRX Parameter** license with mandatory Concept Laser training; the license is time-limited and updates require a maintenance contract ([AM.com](https://additivemanufacturing.com/2016/10/26/the-new-freedom-of-lasercusing-new-software-tool-cl-wrx-parameter-permits-open-processing-of-all-parameter-settings/), [IMD](https://industrialmachinerydigest.com/industrial-news/industry-updates/concept-lasers-new-cl-wrx-parameter-with-open-processing/)).
- Factory material parameter sets are sold per material (one "quality" + one "speed" set free with a new machine).
- Second-hand risk: GE Additive became Colibrium Additive in 2024 and retired the Concept Laser brand; whether CL WRX licenses transfer to a second owner is **unverified** and must be asked of Colibrium and the reseller. The Materialise build processor still lists the M2 as supported.

### Mastrex MX100 / MX220 — no public information on openness

- Product pages publish hardware specs only; software described as "user-friendly software and intuitive controls" with no software name, parameter list, or API documented anywhere ([MX100](https://mastrex.com/product/mx100/), [MX220](https://mastrex.com/product/mx220/)).
- Only openness statement is secondhand press: "pre-qualified material and software parameters with open configuration options for users requiring greater flexibility" ([3Dnatives, May 2026](https://www.3dnatives.com/en/mastrex-affordable-lpbf-systems-19052026/)) — no detail on what "open configuration" includes.
- [Warranty](https://mastrex.com/warranty/) voids on "unapproved third-party components" and firmware alteration; whether powder counts as a component is undefined.
- Company launched at CES 2026; essentially no field-user reports exist yet. Everything about parameter access, hatch angle, material set locking, and powder policy must be asked directly (sales@mastrex.com).

## Questions to ask each vendor during quoting

1. Is **hatch angle and interlayer hatch rotation** a user-editable field? In which software, at which license tier? (Only Aconity, Renishaw AM 250, and EOS-with-Build+ are publicly confirmed.)
2. Which exposure parameters are editable at the tier included in the quote, and what does the full-access tier cost (upfront and annual)?
3. Are the factory material parameter sets **viewable** (actual numbers) or usable only as a black box?
4. Is third-party / self-atomized powder use permitted, and what does it do to the warranty and any process guarantees?
5. Is there an **API or scripting interface** for programmatic control (only Aconity's Python API and EOS's Toolpath API are publicly documented)?
6. For used machines (AM 250, M2): do software licenses/dongles transfer to a second owner, and is a maintenance/support contract available to us?
