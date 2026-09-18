# Vertical Lift Module (VLM) Procurement

Research document for the BYU Vertical Cloud Lab VLM acquisition. This covers used options, new Kardex quote specifications, competing vendor quotes, and programmatic control capabilities.

## Table of Contents

- [Target Specifications](#target-specifications)
- [Used VLM Options (Vertical Storage USA)](#used-vlm-options-vertical-storage-usa)
- [New Kardex Quote Specifications](#new-kardex-quote-specifications)
- [Competing Vendors](#competing-vendors)
  - [Modula](#modula)
  - [Vidir](#vidir)
  - [EFFIMAT](#effimat)
- [Vendor Comparison](#vendor-comparison)
- [Programmatic Control](#programmatic-control)
- [Vendor Contact Information](#vendor-contact-information)
- [Draft Outreach Emails](#draft-outreach-emails)
- [Used Equipment Marketplaces](#used-equipment-marketplaces)
- [Action Items](#action-items)

---

## Target Specifications

The following specifications were identified for the BYU VCL VLM:

| Parameter | Target Value |
|---|---|
| Model baseline | Kardex Remstar Shuttle XP-500 |
| Tray size | 96.46" W × 34.00" D |
| Machine height | < 13' (156") |
| Power | 208V, 3-phase |
| Doors | Powered safety shutter doors |
| Tray types (3 total) | (1) Light: 502 lbs/tray (22.3 lbs/ft²) |
| | (1) Medium: 794 lbs/tray (34.9 lbs/ft²) |
| | (1) Strong: 1,080 lbs/tray (47.4 lbs/ft²) |
| Programmatic control | Required (API/software, not just touchscreen/GUI) |

---

## Used VLM Options (Vertical Storage USA)

The following pre-owned units are available from [Vertical Storage USA](https://verticalstorageusa.com). Contact them at **(888) 340-3851** or via their [contact form](https://verticalstorageusa.com/contact-us/) to request quotes. All units include a **60-day parts & labor warranty** and are crated/installed by factory-trained certified technicians.

### Used Options Comparison

| Spec | Option 1: XP-500 (2021) | Option 2: XP-500 | Option 3: 250NT-1250 | Option 4: 250NT-1850 |
|---|---|---|---|---|
| **Model** | XP-500-2450×864 | XP-500-2450×864 | 250NT-1250×864 | 250NT-1850×864 |
| **Year** | 2021 | Not listed | Not listed | Not listed |
| **Condition** | Excellent | Pre-owned | Pre-owned | Pre-owned, fully refurbished |
| **Footprint** | 16' H × 110" W × 120" D | 16' H × 110" W × 120" D | 9'-2" H × 62" W × 105" D | 16' H × 85" W × 123" D |
| **Height** | 16' (192") | 16' (192") | 9'-2" (110") | 16' (192") |
| **Tray size** | 96.5" L × 24" W | 96.5" W × 34" D | 49.2" × 32.5" | 73" L × 34" W |
| **Tray count** | 42 | 28 | 10 | 31 |
| **Tray capacity** | 650 lbs/tray | 550 lbs/tray | 550 lbs/tray | 550 lbs/tray |
| **Controls** | 3000 Operator Console | 3000 Operator Console | C2000 w/ swing arm keypad | C2000 Operator Console |
| **Power** | 480VAC / 15A / 10.0 kVA | 480VAC / 15A / 10.0 kVA | Not listed | Not listed |
| **Doors** | Bi-parting steel shutter | Bi-parting steel shutter | Not listed | Not listed |
| **Qty available** | 1 | 1 | 1 | 3 |
| **Price** | Request quote | Request quote | Request quote | Request quote |
| **Link** | [Listing](https://verticalstorageusa.com/used-warehouse-storage-equipment/pre-owned-2021-kardex-remstar-vlm-for-sale-excellent-condition/) | [Listing](https://verticalstorageusa.com/used-warehouse-storage-equipment/pre-owned-kardex-remstar-vertical-lift-module-shuttle-model-xp-500-2450x864-2/) | [Listing](https://verticalstorageusa.com/used-warehouse-storage-equipment/pre-owned-remstar-vertical-lift-module-shuttle-model-250nt-1250x864/) | [Listing](https://verticalstorageusa.com/used-warehouse-storage-equipment/pre-owned-remstar-vertical-lift-modules-shuttle-model-250nt-1850x864/) |

### Notes on Used Options

- **Options 1 & 2** are both XP-500 models (same as the target specification baseline) and match the 96.5" tray width. Option 2's 34" tray depth matches the target spec exactly.
- **Option 1** has shallower trays (24" D vs. 34" D target) but more trays (42 vs. 28) and higher per-tray capacity (650 lbs).
- **Option 3** is the smallest unit (9'-2" H, 49.2" trays) — significantly smaller than the target spec and likely too small.
- **Option 4** has 73" trays (narrower than the 96.46" target) but offers 3 units available, making it suitable if multiple smaller units are acceptable.
- **Power mismatch**: Options 1 & 2 are 480VAC (target is 208V 3-phase). Verify whether a step-up transformer is needed or if 208V variants are available.
- **Height mismatch**: Options 1, 2, and 4 are 16' tall (target is < 13'). Confirm ceiling height at the BYU VCL lab.
- **Controls**: The C3000 console (Options 1 & 2) is newer than the C2000 (Options 3 & 4). Ask about programmatic control compatibility for each console generation.

> **Estimated used VLM pricing**: $35,000–$75,000 per unit depending on size, age, and condition. Pre-owned XP-500 units from recent years typically fall toward the upper end.

---

## New Kardex Quote Specifications

The following specifications should be submitted to Kardex for an official quote:

```
KARDEX REMSTAR SHUTTLE XP-500
Tray Size:            96.46" W × 34.00" D
Height of machine:    Less than 13' (156")
Power:                208V 3 Phase

Total of three trays:
  (1) Light capacity tray:    502 lbs/tray  (22.3 lbs/ft²)
  (1) Medium capacity tray:   794 lbs/tray  (34.9 lbs/ft²)
  (1) Strong capacity tray: 1,080 lbs/tray  (47.4 lbs/ft²)

Options:
  - Powered safety shutter doors
  - Programmatic control capability (API/software integration,
    not just touchscreen/GUI)

Additional questions:
  1. What programmatic control options are available?
     (Power Pick Global API, JMIF, OPC-UA, PLC I/O, REST/SOAP?)
  2. Can the unit be controlled via external software without
     the operator console / touchscreen?
  3. Is the Power Pick Global software included, or is it an
     additional cost?
  4. What is the lead time for a new unit?
  5. What warranty options are available?
  6. Is installation included in the quote?
```

> **Estimated new price**: ~$150,000 for a standard Kardex Shuttle XP-500 configuration. Actual price will vary with options, tray configuration, and installation.

---

## Competing Vendors

### Modula

[Modula](https://modula.us/) is a major VLM manufacturer headquartered in Italy with a strong US presence (70+ dealers). Their **Modula Lift** is the closest competitor to the Kardex Shuttle XP-500.

| Spec | Modula Lift |
|---|---|
| Tray widths | 74.80" (1,900 mm) to 161.41" (4,100 mm) |
| Tray depths | 25.75" (654 mm) and 33.74" (857 mm) |
| Max product height/tray | Up to 27.36" (695 mm) |
| Tray payload | 551 lbs (250 kg) to 2,200 lbs (990 kg) |
| Gross unit capacity | Up to 154,000 lbs (70,000 kg) |
| Unit height | Up to ~69' (21 m) |
| Throughput | Up to 130 trays/hour |
| Operator interface | 10.4" Copilot touchscreen running Lift OS |
| Software | Modula WMS (Basic, Premium packages) |
| Programmatic control | REST API, ODBC, XML, ASCII; Modula Link / Modula Driver for ERP integration |
| ERP integration | SAP, Oracle, Microsoft Dynamics, Epicor, and others |
| New price range | Starts in low six figures (~$100,000+) |

**Modula model variants**:
- **Modula Lift** — Standard heavy-duty, large-scale VLM (closest to Kardex XP-500)
- **Modula Slim** — Compact footprint for limited floor space
- **Modula Next** — Advanced security and picking controls
- **FlexiBox** — Custom solution for nonstandard items

**Key advantages**: Wide tray size range, strong US dealer network (70+), Copilot interface with REST API, well-documented WMS integration.

### Vidir

[Vidir Solutions](https://vidirsolutions.com/) is a Canadian manufacturer known for innovative servo-driven VLMs with high throughput.

| Spec | Vidir VLM |
|---|---|
| Heights | 9'-10" to 29'-8" |
| Widths | 9'-9" to 13'-9" |
| Depths | 7'-10" to 9'-7" |
| Storage capacity | 188 ft³ to 1,649 ft³ |
| Tray capacity | Up to 1,500 lbs/tray |
| Drive | Industry-first servo motors, chain drive |
| Tray height detection | Automatic |
| Software | Integrated inventory control, ERP connectivity |
| Power | 208V/230V, 60Hz, 15A, 3-phase |
| New price range | ~$75,000–$140,000 |
| Used price range | ~$35,000–$75,000 |

**Key advantages**: Servo-driven (high speed and precision), 208V/230V power (matches BYU target spec), competitive pricing, front-facing maintenance, Schneider Electric parts for reliability.

### EFFIMAT

[EFFIMAT](https://effimat.com/) is a Danish manufacturer with a unique **tote-based** (box-based) VLM design, optimized for high-throughput small-parts picking rather than full-tray retrieval.

| Spec | EFFIMAT |
|---|---|
| Storage unit | Tote/box (not full tray) |
| Box size | 400 × 600 mm (15.74" × 23.62"), heights 50–400 mm |
| Max weight per box | 25 kg (55 lbs) |
| Vertical height | Up to 36 m (~118') |
| Throughput | Up to 400 boxes/hour (5 presented per cycle) |
| Footprint (W × D) | 2,874 mm × 2,365 mm (~113" × 93") |
| Software | EffiSoft™ WMS |
| Programmatic control | API/connectors for ERP/WMS integration |
| New price range | ~$100,000+ (premium for high throughput) |

> **Note on EFFIMAT**: This is a fundamentally different architecture (tote-based vs. tray-based). The 55 lbs/box max capacity is far below the target spec's 502–1,080 lbs/tray. EFFIMAT is best suited for high-throughput small-parts storage and may not be appropriate if heavy tray loads are required. However, it is worth getting a quote for comparison and to understand its applicability for lighter-weight inventory items.

---

## Vendor Comparison

| Feature | Kardex XP-500 | Modula Lift | Vidir VLM | EFFIMAT |
|---|---|---|---|---|
| **Architecture** | Tray-based | Tray-based | Tray-based | Tote/box-based |
| **Max tray/box capacity** | ~1,000 lbs/tray | Up to 2,200 lbs/tray | Up to 1,500 lbs/tray | 55 lbs/box |
| **Tray width range** | Up to ~144" | 74.80"–161.41" | 9'-9"–13'-9" (unit) | 15.74" (box) |
| **Min machine height** | ~8.4' (101") | Configurable | 9'-10" | Configurable |
| **Power (US)** | 208V/480V 3-phase | Configurable | 208V/230V 3-phase | Configurable |
| **Programmatic control** | Power Pick Global, JMIF, Web Services | REST API, ODBC, Modula Link/Driver | ERP connectivity, inventory SW | EffiSoft API, ERP connectors |
| **Software** | Power Pick Global / FastPic5 | Modula WMS (Lift OS) | Integrated inventory control | EffiSoft™ |
| **New price (est.)** | ~$150,000 | ~$100,000+ | ~$75,000–$140,000 | ~$100,000+ |
| **Used availability** | Good (established market) | Moderate | Limited | Rare |
| **US presence** | Strong (Westbrook, ME HQ) | Strong (70+ dealers) | Canadian (US via dealers) | Danish (US via distributors) |
| **Best for** | General-purpose, heavy loads | Flexible tray sizes, ERP integration | Budget-conscious, 208V power | High-throughput small parts |

---

## Programmatic Control

A key requirement is the ability to control the VLM programmatically (via API/software) rather than solely through a touchscreen or GUI. Below is a summary of programmatic control options by vendor.

### Kardex — Power Pick Global & JMIF

| Interface | Description |
|---|---|
| **Power Pick Global (PPG)** | Kardex's WMS software. Supports inventory management, automated retrieval, pick optimization. Integrates with ERP systems (SAP, Oracle, etc.). |
| **JMIF (Java Machine Interface)** | Java-based middleware for external programmatic control. Acts as a bridge between external systems and the Kardex unit. |
| **Web Services** | REST/SOAP API endpoints for sending/receiving inventory transactions, status, and orders programmatically. |
| **OPC-UA** | Not natively documented, but achievable via middleware (JMIF or third-party bridge) for PLC-level control. |
| **User I/O Peripherals** | Hardware interface for direct PLC I/O and fieldbus integration. |
| **Barcode/RFID** | Integrated scanning for automated order processing and inventory control. |

**Key question for Kardex**: Can the VLM be fully controlled via JMIF or Web Services API without any operator interaction at the console? What are the licensing costs for Power Pick Global?

### Modula — WMS API & Modula Link

| Interface | Description |
|---|---|
| **REST API** | RESTful web service endpoints for picking, storage, and inventory queries. |
| **ODBC / XML / ASCII** | Multiple data interchange protocols for ERP integration. |
| **Modula Link** | Real-time bidirectional control from ERP — send commands and monitor status directly. |
| **Modula Driver** | Mediates order exchanges between ERP and Copilot console. |
| **Copilot API** | Programmatic access to core warehouse operations (retrieve, store, inventory). |

**Key question for Modula**: Is the REST API documentation publicly available, or does it require a formal integration request? Can the VLM be fully controlled via API without operator interaction?

### Vidir — Integrated Software

| Interface | Description |
|---|---|
| **Integrated inventory control** | Built-in software with pick/stock lists, reporting. |
| **ERP connectivity** | Integration with external ERP/WMS systems. |
| **Remote service access** | Remote diagnostics and monitoring. |

**Key question for Vidir**: What specific APIs or protocols are supported for programmatic control? Can the VLM be operated headlessly via software commands?

### EFFIMAT — EffiSoft

| Interface | Description |
|---|---|
| **EffiSoft™** | EFFIMAT's WMS software with API/connectors for ERP/WMS integration. |
| **External automation** | Integration with robot arms, conveyors, and industrial control systems via standard interfaces. |

**Key question for EFFIMAT**: What specific API protocols are supported (REST, SOAP, OPC-UA)? Can the system be operated fully via API?

---

## Vendor Contact Information

| Vendor | Contact Method | Details |
|---|---|---|
| **Kardex (US HQ)** | Phone | (800) 639-5805 |
| | Email | info@kardexremstar.com |
| | Web form | [kardex.com/get-in-touch](https://www.kardex.com/en-us/company_people/about-kardex/get-in-touch) |
| | Address | 41 Eisenhower Dr, Westbrook, ME 04092 |
| **Kardex Storage Systems** (distributor) | Phone | (844) 577-2255 |
| | Email | info@kardexstoragesystems.com |
| **Modula USA** | Phone | (800) 361-0785 |
| | Email | info@modula.us |
| | Web form | [modula.us/contact](https://modula.us/contact/) |
| **Vidir Solutions** | Phone | (800) 210-0141 |
| | Web form | [vidirsolutions.com/contact](https://vidirsolutions.com/contact) |
| **EFFIMAT** | Phone | +45 7199 4800 |
| | Email | info@effimat.com |
| | Sales (Johnny Rasmussen) | jor@effimat.com, +45 8177 3187 |
| | Web form | [effimat.com/contact](https://effimat.com/contact/) |
| **Vertical Storage USA** (used equipment) | Phone | (888) 340-3851 |
| | Web form | [verticalstorageusa.com/contact-us](https://verticalstorageusa.com/contact-us/) |

---

## Draft Outreach Emails

### Email to Vertical Storage USA (Used Equipment Quotes)

> **Subject:** Quote Request — Pre-Owned Kardex Remstar VLMs for University Lab
>
> Hello,
>
> I am a researcher at Brigham Young University exploring storage solutions for our Vertical Cloud Lab. We are interested in receiving quotes for the following pre-owned Kardex Remstar units listed on your website:
>
> 1. Pre-Owned 2021 Kardex Remstar VLM — Model XP-500-2450×864 (Excellent Condition)
> 2. Pre-Owned Kardex Remstar VLM — Model XP-500-2450×864
> 3. Pre-Owned Remstar VLM — Model 250NT-1250×864
> 4. Pre-Owned Remstar VLM — Model 250NT-1850×864
>
> For each unit, could you provide:
> - Pricing (including delivery and installation to Provo, UT 84602)
> - Availability of 208V 3-phase power configuration (vs. 480VAC)
> - Programmatic control options (API or software control, not just the operator console)
> - Any additional information on machine condition or history
>
> Thank you for your time.
>
> Best regards,
> [Name]
> Brigham Young University — Vertical Cloud Lab

### Email to Kardex (New Unit Quote)

> **Subject:** Quote Request — Kardex Shuttle XP-500 for University Research Lab
>
> Hello,
>
> I am a researcher at Brigham Young University and would like to request a formal quote for a new Kardex Remstar Shuttle XP-500 with the following specifications:
>
> - **Tray Size:** 96.46" W × 34.00" D
> - **Machine Height:** Less than 13'
> - **Power:** 208V, 3-phase
> - **Doors:** Powered safety shutter doors
> - **Trays (3 total):**
>   - (1) Light capacity tray — 502 lbs/tray (22.3 lbs/ft²)
>   - (1) Medium capacity tray — 794 lbs/tray (34.9 lbs/ft²)
>   - (1) Strong capacity tray — 1,080 lbs/tray (47.4 lbs/ft²)
>
> We also have the following questions:
> 1. What programmatic control options are available? We need the ability to control the VLM via external software (API, SDK, or middleware) rather than exclusively through the touchscreen/GUI. Specifically, can you provide details on Power Pick Global API access, JMIF (Java Machine Interface), and/or Web Services integration?
> 2. Can the unit be operated entirely via API without operator interaction at the console?
> 3. Is Power Pick Global included in the quote, or is it an additional cost?
> 4. What is the current lead time for a new unit?
> 5. What warranty and service contract options are available?
> 6. Is installation included, and do you service the Provo, UT 84602 area?
>
> Thank you for your time.
>
> Best regards,
> [Name]
> Brigham Young University — Vertical Cloud Lab

### Email to Modula (Competing Quote)

> **Subject:** Quote Request — Modula Lift VLM for University Research Lab
>
> Hello,
>
> I am a researcher at Brigham Young University exploring vertical lift module options for our Vertical Cloud Lab. We are seeking a competing quote for a Modula Lift with specifications comparable to the Kardex Shuttle XP-500:
>
> - **Tray Size:** Approximately 96" W × 34" D (closest available configuration)
> - **Machine Height:** Less than 13'
> - **Power:** 208V, 3-phase
> - **Tray Capacities:** Range from ~500 lbs to ~1,100 lbs per tray
> - **Doors:** Powered safety shutter doors (or equivalent)
>
> We specifically require programmatic control capability:
> 1. Can the Modula Lift be controlled entirely via API (REST, ODBC, or other protocol) without operator interaction at the Copilot console?
> 2. Is the Modula WMS REST API documentation available for review prior to purchase?
> 3. What ERP/WMS integration options are included vs. additional cost (Modula Link, Modula Driver)?
>
> Could you also provide information on lead time, warranty, installation services for Provo, UT 84602, and any educational/university pricing programs?
>
> Thank you for your time.
>
> Best regards,
> [Name]
> Brigham Young University — Vertical Cloud Lab

### Email to Vidir (Competing Quote)

> **Subject:** Quote Request — Vidir VLM for University Research Lab
>
> Hello,
>
> I am a researcher at Brigham Young University exploring vertical lift module options for our Vertical Cloud Lab. We are seeking a competing quote for a Vidir VLM with specifications comparable to the Kardex Shuttle XP-500:
>
> - **Tray Size:** Approximately 96" W × 34" D (closest available configuration)
> - **Machine Height:** Less than 13'
> - **Power:** 208V, 3-phase
> - **Tray Capacities:** Range from ~500 lbs to ~1,100 lbs per tray
> - **Doors:** Powered safety shutter doors (or equivalent)
>
> We specifically require programmatic control capability:
> 1. What APIs or software protocols does the Vidir VLM support for external programmatic control?
> 2. Can the unit be operated entirely via software commands without operator interaction?
> 3. What ERP/WMS integration options are available?
>
> Could you also provide information on lead time, warranty, installation services for Provo, UT 84602, and any educational/university pricing programs?
>
> Thank you for your time.
>
> Best regards,
> [Name]
> Brigham Young University — Vertical Cloud Lab

### Email to EFFIMAT (Competing Quote)

> **Subject:** Quote Request — EFFIMAT VLM for University Research Lab
>
> Hello,
>
> I am a researcher at Brigham Young University exploring automated storage solutions for our Vertical Cloud Lab. We are evaluating the EFFIMAT system alongside tray-based VLMs (Kardex, Modula, Vidir).
>
> Our target specifications (based on a Kardex Shuttle XP-500 baseline):
> - **Storage area:** Approximately 96" W × 34" D equivalent
> - **Machine Height:** Less than 13'
> - **Power:** 208V, 3-phase
> - **Load capacity:** Items ranging from ~500 lbs to ~1,100 lbs (we understand the EFFIMAT tote system has a 55 lbs/box limit — please advise on whether multi-box configurations or alternative solutions can accommodate heavier items)
>
> We specifically require programmatic control capability:
> 1. What APIs or software protocols does EffiSoft support for external programmatic control?
> 2. Can the system be operated entirely via API without operator interaction?
> 3. What ERP/WMS integration options are available?
>
> Could you provide a formal quote, lead time, warranty details, and availability of installation/service in Provo, UT 84602?
>
> Thank you for your time.
>
> Best regards,
> [Name]
> Brigham Young University — Vertical Cloud Lab

---

## Used Equipment Marketplaces

In addition to Vertical Storage USA, the following marketplaces may have used VLMs:

| Marketplace | URL | Notes |
|---|---|---|
| Vertical Storage USA | [verticalstorageusa.com](https://verticalstorageusa.com/used-equip-type/used-vertical-lift-modules/) | Specialized VLM dealer, factory-certified refurbishment |
| ECS Eco | [ecseco.com](https://ecseco.com/used-equipment/carousels/vertical-lift-modules/) | Used VLMs from multiple manufacturers |
| Machineseeker | [machineseeker.com](https://www.machineseeker.com/mss/kardex) | European marketplace with international shipping |
| eBay | [ebay.com](https://www.ebay.com) | Search "Kardex VLM" or "vertical lift module" |
| Exapro | [exapro.com](https://www.exapro.com) | Used industrial machinery marketplace |
| Machinio | [machinio.com](https://www.machinio.com) | Industrial equipment search engine |
| Surplus Record | [surplusrecord.com](https://www.surplusrecord.com) | Industrial surplus equipment |

### Search Keywords

- `Kardex Remstar Shuttle XP-500 used`
- `Kardex VLM vertical lift module used`
- `vertical lift module 96" tray used`
- `Modula Lift VLM used`
- `Vidir VLM used`
- `vertical lift module 208V 3-phase`
- `automated storage retrieval system ASRS used`

---

## Action Items

- [ ] Request quotes from Vertical Storage USA for all four used VLM listings
- [ ] Submit formal quote request to Kardex for new Shuttle XP-500 (per specs above)
- [ ] Ask Kardex about Power Pick Global / JMIF / Web Services for programmatic control
- [ ] Request competing quote from Modula for a similarly spec'd Modula Lift
- [ ] Request competing quote from Vidir for a similarly spec'd VLM
- [ ] Request competing quote from EFFIMAT (note tote-based architecture limitations)
- [ ] Verify BYU VCL lab ceiling height (target spec requires < 13'; used options are 16')
- [ ] Verify BYU VCL lab power availability (208V vs. 480V 3-phase)
- [ ] Compare delivered quotes side-by-side (price, specs, programmatic control, lead time, warranty)
- [ ] Evaluate programmatic control options from each vendor for lab automation compatibility
- [ ] Set up alerts on used equipment marketplaces for VLM listings

---

## References

1. [Kardex Shuttle XP-500 Brochure (PDF)](https://www.raymond-central.com/-/media/dealers/heubelshaw/kardexremstar/literature/product-brochures/vlm-literature/featured-literature/vertical-lift-module-brochure--shuttlexp.pdf)
2. [Kardex Power Pick Global Software (PDF)](https://info.kardex-remstar.com/hubfs/US-EN-Download-Center-Assets/Software%20Information/power-pick-global.pdf)
3. [Kardex JMIF Interface](https://www.kardex.com/en-gb/products/interface/kardex-jmif)
4. [Kardex Operating Manuals Portal](https://info.kardex-remstar.com/knowledge/kardex-remstar-operating-manuals)
5. [Modula Lift Specifications (PDF)](https://www.werres.com/-/media/dealers/werres/literature/modula/modula-lift.pdf)
6. [Modula WMS Integration (PDF)](https://www.modula.eu/wp-content/uploads/2024/12/Modula-WMS-ENG.pdf)
7. [Modula Software Integrations](https://modula.us/solutions/modula-software-integrations/)
8. [Vidir VLM Brochure (PDF)](https://vidirsolutions.com/wp-content/uploads/2024/11/VLM-Brochure-2025R00.pdf)
9. [EFFIMAT Brochure (PDF)](https://dilarce.com/wp-content/uploads/2024/05/Brochure-EffiMat-.pdf)
10. [VLM Pricing Guide — Vertical Storage USA](https://verticalstorageusa.com/vertical-lift-module-price/)
11. [VLM Cost Guide — White Systems](https://whitesystems.com/how-much-does-a-vertical-lift-module-cost/)
12. [ASRS Cost Factors — Kardex](https://www.kardex.com/en-us/blog/asrs-cost-factors)
