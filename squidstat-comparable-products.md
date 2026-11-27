# Comparable Products for Squidstat Instruments

This document provides comparable product information for accounting and procurement purposes. It covers alternatives to both the **Squidstat Cycler** (multi-channel battery cycler, ~$10k new) and the **Squidstat Plus** (single-channel potentiostat/galvanostat/FRA, ~$6k new / ~$4k refurbished).

> **Note:** Prices listed are approximate and based on publicly available information. Request formal quotes from each vendor for exact pricing. Universities typically require 2–3 competing quotes for procurement.

---

## Squidstat Plus (Single-Channel with EIS) — Comparables

The Squidstat Plus Complete Setup (PL-25-M2-CS) is a single-channel potentiostat/galvanostat with FRA (EIS) capability.

| Specification | Admiral Instruments Squidstat Plus | PalmSens PalmSens4 | Gamry Interface 1010E |
|---|---|---|---|
| **Estimated Price** | ~$6,000 (new) / ~$4,000 (refurb) | ~$5,000–$8,000 | ~$6,000–$10,000 |
| **Channels** | 1 | 1 | 1 |
| **Operating Modes** | Pot / Gal / ZRA / FRA | Pot / Gal / FRA (optional) | Pot / Gal / ZRA |
| **Voltage Range** | ±10 V | ±5 V or ±10 V | ±12 V |
| **Max Current** | ±1 A | ±30 mA | ±1 A |
| **EIS Frequency** | 10 µHz – 2 MHz | 10 µHz – 1 MHz | 10 µHz – 2 MHz |
| **ADC/DAC Resolution** | 16-bit | 18-bit | 16-bit |
| **Current Ranges** | 8 (100 nA to 1 A) | 9 (100 pA to 10 mA) | Multiple (to 1 A) |
| **Input Impedance** | 10 TΩ | > 1 TΩ | > 10 TΩ |
| **Data Backup** | 16 GB onboard | 8 GB onboard | None (PC-based) |
| **Software** | Squidstat UI + API | PSTrace (Windows) + PStouch (Android) | Gamry Framework + Echem Analyst |
| **SDK / API** | Python API | .NET, Python, LabVIEW, MATLAB | Python, LabVIEW |
| **Connectivity** | USB | USB + Bluetooth | USB |
| **Weight** | 1 kg | 0.5 kg | ~2 kg |
| **Warranty** | 2 years (new) / 90 days (refurb) | Standard | Standard |
| **OS Support** | Windows, macOS, Ubuntu | Windows, Android | Windows |
| **Website** | [admiralinstruments.com](https://www.admiralinstruments.com/potentiostats/squidstat-plus) | [palmsens.com](https://www.palmsens.com/product/palmsens4/) | [gamry.com](https://www.gamry.com/potentiostats/interface/interface-1010e-potentiostat/) |

### Key Differences

- **PalmSens PalmSens4** has lower max current (30 mA vs 1 A) but offers Bluetooth connectivity and battery power. Better for low-current analytical electrochemistry and field work. Lower EIS max frequency (1 MHz vs 2 MHz on the Plus).
- **Gamry Interface 1010E** is a close match in current (1 A) and EIS frequency (2 MHz). Well-established in the research community with extensive application support. Windows-only software.
- **Squidstat Plus** offers the best value at ~$6k with cross-platform support (Windows/macOS/Ubuntu), Python API, and competitive specs.

---

## Squidstat Cycler / Multi-Channel Systems — Comparables

The Squidstat Cycler (~$10k new) is a multi-channel battery cycling system. For four-channel potentiostat alternatives, the following products are comparable.

| Specification | Admiral Instruments Squidstat Prime | PalmSens MultiPalmSens4 | Gamry Multichannel (4× Interface 1010E) | BioLogic VSP-3e |
|---|---|---|---|---|
| **Estimated Price** | ~$5,000–$7,000 | ~$10,000–$20,000 (config-dependent) | ~$25,000–$35,000 | ~$25,000–$40,000 |
| **Channels** | 4 | 2–10 (configurable) | 4 (independent units) | Up to 8 |
| **Operating Modes** | Pot / Gal / ZRA | Pot / Gal / FRA (optional per channel) | Pot / Gal / ZRA | Pot / Gal / FRA (optional) |
| **Voltage Range** | ±10 V | ±5 V or ±10 V per channel | ±12 V per channel | ±10 V (customizable up to 20 V) |
| **Max Current** | ±250 mA | ±30 mA per channel | ±1 A per channel | ±1 A (expandable to 800 A with boosters) |
| **EIS** | No (DC only) | Optional (10 µHz – 1 MHz) | Yes (10 µHz – 2 MHz) | Optional (10 µHz – 1 MHz) |
| **ADC/DAC Resolution** | 16-bit | 18-bit | 16-bit | 16-bit |
| **Data Backup** | 16 GB onboard | 8 GB per channel | None (PC-based) | None (PC-based) |
| **Software** | Squidstat UI + API | MultiTrace (Windows) | Gamry Framework | EC-Lab |
| **SDK / API** | Python API | .NET, Python, LabVIEW, MATLAB | Python, LabVIEW | EC-Lab developer package |
| **OS Support** | Windows, macOS, Ubuntu | Windows | Windows | Windows |
| **Warranty** | 2 years | Standard | Standard | Standard |
| **Website** | [admiralinstruments.com](https://www.admiralinstruments.com/potentiostats/squidstat-prime) | [palmsens.com](https://www.palmsens.com/product/multipalmsens4/) | [gamry.com](https://www.gamry.com/potentiostats/multichannel-potentiostat/) | [biologic.net](https://www.biologic.net/products/vsp-3e/) |

### Key Differences

- **Squidstat Prime** is the most affordable 4-channel option but is DC-only (no EIS) and has lower max current (250 mA). Best value for battery cycling applications that don't require impedance spectroscopy.
- **PalmSens MultiPalmSens4** is highly configurable (2–10 channels, optional EIS per channel) but has significantly lower max current (30 mA per channel). Best for analytical electrochemistry with multiple samples.
- **Gamry Multichannel** provides research-grade performance with full EIS per channel and 1 A current, but at a much higher price point. Each channel is a fully independent potentiostat.
- **BioLogic VSP-3e** is a premium research instrument with up to 8 channels, booster compatibility (up to 800 A), and advanced features. Highest cost but most expandable.

---

## Vendor Contact Information

| Vendor | Website | Contact |
|---|---|---|
| Admiral Instruments | [admiralinstruments.com](https://www.admiralinstruments.com) | Request quote via website |
| PalmSens | [palmsens.com](https://www.palmsens.com) | Request quote via website |
| Gamry Instruments | [gamry.com](https://www.gamry.com) | Request quote via website or sales@gamry.com |
| BioLogic | [biologic.net](https://www.biologic.net) | Request quote via website |

---

## Action Items

- [ ] Request formal quote from PalmSens for a 4-channel MultiPalmSens4 with EIS (±10 V configuration)
- [ ] Request formal quote from Gamry for a 4-channel Interface 1010E multichannel system
- [ ] Set up alerts on eBay and BidSpotter for "squidstat" for auction opportunities
- [ ] Monitor the XALT Energy auction (March 31, 2026) for Squidstat Cycler availability

---

## References

- Admiral Instruments product page: https://www.admiralinstruments.com/potentiostats
- PalmSens PalmSens4: https://www.palmsens.com/product/palmsens4/
- PalmSens MultiPalmSens4: https://www.palmsens.com/product/multipalmsens4/
- Gamry potentiostats: https://www.gamry.com/potentiostats/browse-all-potentiostats/
- Gamry multichannel: https://www.gamry.com/potentiostats/multichannel-potentiostat/
- BioLogic VSP-3e: https://www.biologic.net/products/vsp-3e/
- XALT Energy auction (BidSpotter): https://www.bidspotter.com/en-us/auction-catalogues/bscbiditup/catalogue-id-bscbiditup10039/lot-a132a1ab-1944-4122-87c5-b3ea01214276
