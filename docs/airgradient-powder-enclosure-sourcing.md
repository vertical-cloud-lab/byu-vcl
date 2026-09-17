# AirGradient for the powder enclosure — model selection & sourcing

Sourcing notes for putting an [AirGradient](https://www.airgradient.com/) particulate monitor on the
powder enclosure serving the AMAZEMET rePowder ultrasonic atomizer, per
[issue #219](https://github.com/vertical-cloud-lab/byu-vcl/issues/219).

> **Bottom line.** Order **1× Open Air (O-1PST), fully assembled, USD 225** for the enclosure and
> **1× AirGradient ONE (I-9PSL), fully assembled, USD 230** as the room reference — the pair is what
> makes either reading interpretable. Budget a 5 V ≥2 A USB-A supply for the Open Air; the plug is
> **not** in the box. Mount the Open Air at the enclosure's **exhaust or seam line, not inside the
> powder-wetted volume** (see [Combustible dust](#combustible-dust-where-not-to-mount-it)).

## Product line, as of September 2026

| Model | Form | Price (assembled / kit) | PM sensor | Temp/RH sensor | Notes |
|---|---|---:|---|---|---|
| **Open Air `O-1PST`** | Outdoor | **$225 / $125** | 1× Plantower PMS5003T | *inside the PM module* | ASA, UV-resistant, weatherproof; wall/pole mount; USB-C |
| **AirGradient ONE `I-9PSL`** | Indoor | **$230 / $138** | 1× Plantower PMS5003 | **Sensirion SHT40** ±0.2 °C | Display + RGB LED bar; desk/wall |
| Open Air Max `O-M-1PPSTON-CE-S` | Outdoor pro | sub-$1000 | 2× PMS5003 (redundant) | SHT40 | Adds NO₂ + O₃, solar + 10 Ah battery, cellular |

All three carry CO₂ (SenseAir S8/S88, NDIR) and TVOC/NOx (Sensirion SGP41), are open hardware under
CC-BY-SA with [open firmware](https://github.com/airgradienthq/arduino), and speak both MQTT and a
local HTTP API. The **Open Air Max is overkill here** — its differentiators (solar, battery,
cellular, outdoor gas chemistry) are all answers to problems a bench enclosure 3 m from an outlet
does not have.

**Kit vs. assembled.** The kits are genuinely no-solder, 30–60 min builds and AirGradient markets
them as a STEM activity. But the kit price drops CE/FCC/RoHS marking and the 12-month warranty.
For the unit going next to a combustible-metal-dust hazard, pay the $100 for the assembled,
certified unit — the certification is the thing an EHS reviewer will ask for. The indoor one is a
defensible kit build if a student wants it ($138 vs. $230).

## What this sensor can and cannot see

This is the part worth internalizing before the unit arrives, because the obvious expectation —
"it will tell me if powder is escaping" — is only half right.

**The feedstock itself is invisible to it.** Optical PM sensors bin by *aerodynamic* diameter, and
for a sphere `d_ae = d_geo · √ρ`. Our powders are dense:

| Powder | ρ (g/cm³) | √ρ | 15 µm geometric → | Largest geometric size still inside PM10 |
|---|---:|---:|---:|---:|
| Al / AlSi10Mg | 2.70 / 2.67 | 1.64 | **24.7 µm aerodynamic** | **~6.1 µm** |
| Si | 2.33 | 1.53 | 22.9 µm aerodynamic | ~6.6 µm |

The LPBF feedstock cut is **15–45 µm geometric** → roughly **25–74 µm aerodynamic**, entirely above
the PM10 cutoff. A visible spill of feedstock may barely move the needle.

**What it does see is the fraction that actually matters for health**: the sub-~6 µm geometric
fines/satellite tail from atomization and handling, plus any ultrafine condensate. That is the
respirable fraction. So it is the right instrument for *"is anyone breathing this"* and the wrong
instrument for *"did I spill."*

**It saturates below the exposure limits.** The PMS5003T is specified **0–500 µg/m³ effective**,
**≥1000 µg/m³ maximum** (±5 µg/m³ @ 0–100, ±8% @ 100–500). Against the limits for aluminum:

| Limit | Value | vs. sensor |
|---|---:|---|
| PMS5003T effective range top | 500 µg/m³ | — |
| PMS5003T saturation | ~1000 µg/m³ | — |
| **ACGIH TLV-TWA**, Al metal & insoluble cpds, respirable | 1 mg/m³ = **1000 µg/m³** | ≈ exactly at saturation |
| **OSHA PEL**, Al respirable | 5 mg/m³ = **5000 µg/m³** | 10× above the effective range |
| **OSHA PEL**, Al total dust | 15 mg/m³ = **15 000 µg/m³** | 30× above |

A real exposure event pins the sensor and stays pinned. Treat a railed reading as "evacuate and get
a gravimetric cassette on it," not as a number.

**The µg/m³ figures are not accurate for metal dust anyway.** Laser-scattering sensors are factory
calibrated against an ambient aerosol of assumed refractive index and ~1.65 g/cm³ density. Metal
powder is ~2.7 g/cm³ and strongly reflective, so the mass conversion is systematically wrong by an
unknown factor. **Use it as a relative baseline-vs-event trend, not as an absolute concentration.**
This does not diminish its value — a 20× step above a quiet baseline is unambiguous regardless of
what the axis says.

## Combustible dust: where *not* to mount it

Aluminum is a combustible metal under **NFPA 484** (now consolidated into **NFPA 660**), and fine Al
is among the more energetic dusts in that standard. Where a combustible metal dust atmosphere can
exist, NFPA 484 defers to **NFPA 70 Article 500/506** for **Class II** area classification, and
requires dusttight enclosures with a maintenance program to verify dust is not getting inside.

The AirGradient is an unrated ESP32-C3 board with a **fan that deliberately pulls dust-laden air
across a laser diode**. It is not Class II rated and its ASA shell is weatherproof, not dusttight in
the NEC sense. Putting it inside a volume that can develop an explosible Al dust cloud is the one
configuration to avoid.

**Mount it instead at the enclosure exhaust, at a seam/door gap, or in the operator breathing zone
just outside.** This is not a compromise — it is a better experiment. The question worth answering
is "is containment holding," and that is measured at the boundary, not in the middle of the dirty
side where the answer is always "yes, there is powder in here."

Worth confirming with BYU EHS before install; the chemical hygiene plan and hazard checklist already
in this repo are the right starting point, and this ties into the interim fumehood arrangement in
[#195](https://github.com/vertical-cloud-lab/byu-vcl/issues/195).

## Why order the indoor one as well

Because **one monitor produces an uninterpretable number.** PM2.5 in any room swings with outdoor
infiltration, HVAC cycles, foot traffic, and the 3D printers. A single reading at the enclosure
cannot distinguish "the enclosure is leaking" from "someone opened the loading dock."

Two monitors give a **differential**: `enclosure − room` is containment performance, and it rejects
the common-mode room background automatically. That is the measurement that supports a claim in a
paper or an SOP.

The ONE is also the better-instrumented of the two for the room role: the Open Air's temp/RH sensor
sits **inside the PMS5003T module** and AirGradient documents that it "does not show exact ambient
temperatures and RH" and needs dashboard correction. The ONE's **SHT40** is a real ambient sensor
(±0.2 °C, ±2% RH). And its display and LED bar are visible to a student standing in the room, which
the headless Open Air offers nobody.

## Integration with the existing stack

Both paths drop into infrastructure this lab already runs — no new services.

**MQTT (preferred).** Firmware ≥3.7.0 publishes every **60 s** (readings are ~12 s rolling averages)
to:

```
airgradient/readings/{SERIAL}          # e.g. airgradient/readings/34b7daa16674
```

JSON payload with `pm01` / `pm02` / `pm10` (µg/m³), `rco2`, `atmp`, `rhum`, VOC/NOx indices and
Wi-Fi RSSI; invalid readings are omitted rather than sent as nulls, so **consumers must treat every
field as optional.** The broker URL is set in the dashboard under General Settings → Connectivity
and takes credentials inline, TLS included:

```
mqtts://username:password@BROKER_HOST:8883
```

That is exactly the existing HiveMQ Cloud cluster. Follow the per-client credential convention
already in `CLAUDE.md` and mint a separate `airgradient` user, so it can be rotated without
disturbing `picow-color-sensor`, `ot2-robot` or `hf-space`. Note the free HiveMQ tier has **no
per-topic permissions** — the `airgradient/` prefix is a convention, not a boundary.

**Local HTTP (no cloud account).** Each monitor serves its own readings on the LAN:

```
http://airgradient_{SERIAL}.local/measures/current    # GET readings
http://airgradient_{SERIAL}.local/config              # GET/PUT config
```

Setting `"configurationControl": "local"` via PUT cuts the cloud out entirely, and `"httpDomain"`
redirects posts to our own collector. Good fit if we'd rather have a Pi poll it than depend on an
outbound broker.

**Storage.** Readings belong in MongoDB `digital-wetlab` alongside `sensor-data` — an `air-quality`
collection with the same shape. Carry the monitor's own reading time as `timestamp` and the write
time as `stored_at`, which is the convention the color-sensor pipeline settled on after the
insert-time timestamps turned out to be up to three minutes late.

## Check before ordering

- [ ] **Wi-Fi auth is the likely blocker.** These are **2.4 GHz only**, and the stock setup flow is a
      captive portal that takes an SSID and a password — i.e. **WPA2-PSK**. If the install point only
      has BYU's WPA2-Enterprise/eduroam network, the monitors will not join out of the box. The
      ESP32-C3 silicon does support 802.1X and the firmware is open source, so a fork is possible,
      but that is real work. **Confirm a PSK SSID is reachable at the enclosure** (or plan to bridge
      via one of the lab Pis) before spending the money.
- [ ] Ask AirGradient about **education/volume pricing** — they advertise discounts for schools and
      have a research program, and this is two units with more likely later.
- [ ] Confirm the 4 m USB cable actually reaches an outlet, and **order the 5 V ≥2 A USB-A plug
      separately** — not included.
- [ ] Run the enclosure monitor for **at least a week before any powder work** to establish the
      quiet baseline. Without it, the first atomization run produces a number with nothing to
      compare against.

## Cost summary

| Line item | Qty | Unit | Subtotal |
|---|---:|---:|---:|
| AirGradient Open Air `O-1PST`, assembled | 1 | $225 | $225 |
| AirGradient ONE `I-9PSL`, assembled | 1 | $230 | $230 |
| 5 V ≥2 A USB-A power supply | 2 | ~$10 | ~$20 |
| | | **Total** | **~$475** + shipping |

Both-as-kits would be ~$263 + shipping, trading ~2 h of assembly and the CE/warranty coverage.
A reasonable middle: **assembled Open Air + kit ONE ≈ $363**.

## Sources

- [AirGradient Open Air (outdoor) product page](https://www.airgradient.com/outdoor/) — $225 assembled / $125 kit
- [AirGradient ONE (indoor) product page](https://www.airgradient.com/indoor/) — $230 assembled / $138 kit
- [Open Air `O-1PST` spec sheet (PDF)](https://www.airgradient.com/documents/spec-sheets/Spec_Sheet_AirGradient_Open_Air_O-1PST.pdf)
- [Open Air Max product page](https://www.airgradient.com/professional/products/open-air-max/)
- [MQTT configuration KB](https://www.airgradient.com/documentation/kb/kb-airgradient-one-mqtt-configuration-guide)
- [Local server / local API docs](https://github.com/airgradienthq/arduino/blob/master/docs/local-server.md)
- [Plantower PMS5003 data manual v2.3 (PDF)](https://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms5003-manual_v2-3.pdf) — 0–500 µg/m³ effective, ≥1000 µg/m³ max
- [NFPA 484, Standard for Combustible Metals](https://www.nfpa.org/product/nfpa-484-standard/p0484code)
- [Aluminum Association, *Guidelines for Handling Aluminum Fines* (PDF)](https://www.aluminum.org/sites/default/files/2021-11/Safe_Handling-Aluminum_Fine_Particles.pdf)
- [OSHA Annotated PEL Table Z-1](https://www.osha.gov/annotated-pels/table-z-1)
- [ACGIH TLV — Aluminum metal and insoluble compounds](https://www.acgih.org/aluminum-metal-and-insoluble-compounds/)
