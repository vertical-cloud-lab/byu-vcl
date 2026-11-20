# AirGradient air monitors on every powered tray and at every floor station

byu-vcl #303, PR #318. Sterling wants an AirGradient indoor air monitor on every powered tray and at every floor
station. This note picks the model for each place and gives what a 3-D model, the power budget and the data path need.
Sources were read on 2026-11-20. Prices are from airgradient.com on that day.

## Recommendation

| Place | Model | Power | Network |
|---|---|---|---|
| **Powered tray, inside a Shuttle** | AirGradient ONE, model I-9PSL, fully assembled (USD 230). Ask for the no-display build: the spec sheet says "Also available without display", but the site gives no price for it. Otherwise buy the standard one and turn the display and LED bar off (below) | a 5 V, at least 2 A USB-A supply on the tray's UPS-backed 120 V outlet, or a PoE-to-USB-C splitter on the tray's PoE switch | Wi-Fi to a 2.4 GHz hotspot on the tray's own Pi 5, which forwards the readings over the dock's Ethernet |
| **Floor station** | AirGradient ONE I-9PSL with its display, assembled (USD 230) | a 5 V, at least 2 A USB-A supply on the station's 120 V drop | the lab's 2.4 GHz Wi-Fi |

**Why the ONE on the trays as well.**

- **It reads tray temperature properly.** Its Sensirion SHT40 sits in an isolated pocket: AirGradient says it "is
  isolated to avoid impact from internal heat" ([enclosure figure](https://www.airgradient.com/_img/blog-poc/images/pages/indoor/ag1_enclosure-w800.webp)).
  - Tray heat is the open question. PR #344 estimates a 23 K rise for trays A-F unventilated, and gives no heat
    budget for trays G-M.
  - The Open Air measures temperature and humidity inside its PMS5003T, which reads warm. AirGradient says
    "corrections must be applied ... These may not be entirely accurate"
    ([spec sheet](https://www.airgradient.com/documents/spec-sheets/Spec_Sheet_AirGradient_Open_Air_O-1PST.pdf)).
  - The Open Air is built for outdoors and has no display.
- **There is no smaller indoor AirGradient for sale.** The site sells only the ONE and the Open Air, each assembled or
  as a kit of the same hardware.
  - The DIY Basic and DIY Pro guides are marked "Replaced by newer instructions"
    ([instructions](https://www.airgradient.com/open-airgradient/instructions/)).
  - No PCB-only product was found.
  - The Open Air is smaller in plan, 91.5 × 86.7 mm against 131.2 × 131.2 mm, but it is 85 mm deep.

## Specifications

| | AirGradient ONE (I-9PSL) | AirGradient Open Air (O-1PST) |
|---|---|---|
| Size and weight (spec sheets) | 131.2 × 131.2 × 36.2 mm, 230 g without cable ([ONE spec sheet](https://www.airgradient.com/documents/spec-sheets/Spec_Sheet_AirGradient_ONE_I-9PSL.pdf), dated 2025-04-25). The [product page](https://www.airgradient.com/indoor/) says 130 × 130 × 35 mm, 350 g | 91.5 × 86.7 × 85 mm, 180 g without cable ([spec sheet](https://www.airgradient.com/documents/spec-sheets/Spec_Sheet_AirGradient_Open_Air_O-1PST.pdf), dated 2026-06-22) |
| Price, assembled / kit | USD 230 / 138 ([indoor](https://www.airgradient.com/indoor/)) | USD 225 / 125 ([outdoor](https://www.airgradient.com/outdoor/)). The O-1PPT is no longer on the page. A [review](https://breathesafeair.com/airgradient-open-air-review/) describes it as having two PM sensors (*search snippet only*) |
| PM | Plantower PMS5003: PM1, PM2.5 and PM10. Assembled: PM2.5 ±4 µg/m³ from 0 to 100 µg/m³, ±8 % from 100 to 500. Kit: ±10 µg/m³ / ±10 %. The [datasheet](https://cdn-shop.adafruit.com/product-files/3686/plantower-pms5003-manual_v2-3.pdf) gives an effective range of 0-500 µg/m³ and particles of 0.3-10 µm | PMS5003T: ±5 µg/m³ from 0 to 100, ±8 % from 100 to 500 |
| CO₂ | Senseair S8, NDIR, 400-10,000 ppm, ±40 ppm ±3 % of reading at 5-30 °C and 20-70 % RH. The S88 alternative covers 0-10,000 ppm | the same |
| TVOC / NOx | Sensirion SGP41: VOC Index 0-500 (<±15) and NOx Index 0-500 (<±50). Both are relative indices | the same |
| Temperature / RH | Sensirion SHT40: ±0.2 °C over -40 to 125 °C, ±2 % RH over 0-100 % | inside the PMS5003T: ±0.5 °C, ±2 % RH, reads warm |
| Display and controls | 1.3 in OLED (128 × 64), 11 RGB LEDs, push button, reset button | none: a status LED and a push button |
| Controller and network | ESP32-C3-MINI, Wi-Fi 2.4 GHz 802.11 b/g/n, Bluetooth LE 5. A cellular model, I-9PSL-CE, exists. **No Ethernet or PoE** | the same. The cellular model is O-1PST-CE (LTE Cat 1) |
| Power input | USB-C. ">2A 5V USB A Power Plug is Required", not included; a 2 m USB-A to USB-C cable is supplied | the same, with a 4 m cable |
| Mounting | wall screws "compatible with common European or US junction boxes", clip-on stands, or wall or pole (spec sheet). No magnets mentioned | wall (two screws) or pole (two stainless zip ties) |
| Enclosure | ASA, "UV Resistant and Weather Proof". White in AirGradient's photos; no colour is specified | white ASA with a blue base |
| Certification and licence | CE, RoHS, REACH, FCC, RESET Air. Code and hardware under CC BY-SA 4.0 ([firmware](https://github.com/airgradienthq/arduino)) | CE, RoHS, REACH, FCC |

**Operating temperature.** AirGradient publishes none, so the parts set it:

- Senseair S8: "<50 °C", "<85 % RH" ([Senseair](https://senseair.com/products/size-counts/s8-lp/)).
- PMS5003: -10 to +60 °C and 0-99 % RH (datasheet).
- SGP41: -10 to 50 °C (Mouser and DigiKey listings, *search snippet only*).
- ESP32-C3-MINI-1: -40 to 85 °C ([datasheet v2.2](https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf)).

That puts the limit at about 50 °C. The CO₂ accuracy is specified only from 5 to 30 °C, which a warm tray can exceed.

## The 3-D model

**AirGradient ONE.**

- **Body.** A rounded-square slab 131.2 mm wide, 131.2 mm high and 36.2 mm deep.
  - Corner radius in plan about 12 mm, measured off the front photo. Edges rounded about 3 mm.
  - White ASA: about RGB (0.94, 0.94, 0.93) with a slight sheen.
- **Front.** Flat, with no grille. These positions are measured off AirGradient's
  [front photo](https://www.airgradient.com/_img/blog-poc/images/pages/indoor/v9_shop_assembled-w1200.webp) and
  [render](https://www.airgradient.com/_img/blog-poc/images/pages/indoor/ag1_features-w800.webp), scaled to the
  131.2 mm width, ±3 mm. x runs from the left edge and y down from the top edge.
  - **LED bar:** 11 round dots about 5 mm across at a 9 mm pitch, from x = 20 to 110 mm at y = 21 mm. They glow
    through the plastic and read white when off.
  - **OLED window:** black, about 32 × 16 mm, centred at x = 83 mm, y = 99 mm, in the lower right. It shows small
    white text in four fields (CO2, PM2.5, VOC, NOx).
  - **Logo:** a grey "airgradient" wordmark with a circle-swoosh mark, about 26 × 11 mm, at x = 15-41 mm,
    y = 104-115 mm.
- **Top and bottom edges.** A row of small rectangular vent slots along each. Along the bottom are the PM sensor's
  separate intake and outlet, where the blue PMS5003 shows through, and the T/RH sensor's own vented pocket
  ([enclosure figure](https://www.airgradient.com/_img/blog-poc/images/pages/indoor/ag1_enclosure-w800.webp)). AirGradient:
  - "The vents on the top and bottom of the enclosure create a natural convection";
  - "Separation of intake and outlet of PM sensor avoids air loops".
- **Back** ([figure](https://www.airgradient.com/_img/blog-poc/images/pages/indoor/ag1_mounting-w1600.webp)):
  - four keyhole slots in a diamond, at top, left, right and bottom;
  - a square recess in the middle, about 35 × 35 mm, holding the USB-C socket;
  - a cable channel from the recess to the top or the bottom edge;
  - two clip-on feet under the bottom edge for a desk.
- **On a tray:** draw it upright on the side of the tray's hub box, with its top and bottom edges clear. On a
  floor station: on the station's junction box.

**Open Air,** if it is ever wanted. A 91.5 × 86.7 × 85 mm rounded-square column
([photo](https://www.airgradient.com/_img/blog-poc/images/pages/outdoor/oa_assembled-w1200.webp)):

- a white cover with rounded top edges and the logo on the front;
- a blue base about 12 mm deep, where the air enters;
- a mount at the back.

## Power

- **Supply.** AirGradient asks for a 5 V supply of at least 2 A. Its assembly guide says a weaker adapter can distort
  the screen and drop sensors out ([guide](https://www.airgradient.com/documentation/one-v9/)).
- **What it draws: about 1 W typical, our estimate from the parts' datasheets.** AirGradient publishes no figure.
  - ESP32-C3-MINI-1: 82-84 mA receiving, up to 350 mA peak transmitting, 16-28 mA in modem-sleep.
  - PMS5003: up to 100 mA active.
  - S8: 18 mA average, 300 mA peak.
  - SGP41: about 3 mA (Sensirion's [catalog](https://sensirion.com/products/catalog/SGP41), *search snippet only*).
  - That sums to about 0.14-0.21 A, or 0.7-1.0 W at 5 V, before the display and LED bar. This counts the 3.3 V
    parts' current at 5 V, as through a linear regulator.
  - The simultaneous peak is about 0.75 A (3.8 W) with the LEDs off. The 10 W supply rating is the safe budget.
  - Next to a tray's Pi 5 cameras (4 W each) and its switch (8 W) ([`ups.md`](ups.md)), it is negligible.
- **On a tray, two ways in.**
  - A small 5 V, 2 A USB-A supply on the tray's UPS-backed 120 V branch, through the supplied cable, whose 90° plug
    hides behind the case.
  - A PoE splitter on a free port of the tray's PoE switch, for example
    [Adafruit 4552](https://www.adafruit.com/product/4552): IEEE 802.3af in, isolated 5 V 2 A out on USB-C, USD 14.95,
    82 × 28.5 × 23.2 mm. Its Ethernet output goes unused, because the ONE has no Ethernet port.
  - Both ride the tray's UPS through transit. No AirGradient-specific report of a PoE splitter was found.

## Network and the data path

- **Wi-Fi inside a steel Shuttle will probably be poor.** This is untested; [`three_each.md`](three_each.md) raises
  the same doubt for the Bambu A1 mini. The fix is a hotspot on the tray itself:
  - Every powered tray already has a Pi 5 with Ethernet through the dock ([`services.md`](services.md)). Its own Wi-Fi
    can serve a 2.4 GHz hotspot that the ONE joins.
  - The Pi then polls the monitor, tags each reading with the tray, and buffers while the tray rides the extractor
    and has no Ethernet.
  - Floor stations use the lab's Wi-Fi, which needs a 2.4 GHz SSID.
- **The monitor's own interfaces**, from firmware 3.0.10 ([docs](https://github.com/airgradienthq/arduino/blob/1a2bed8/docs/local-server.md)):
  - `http://airgradient_<serial>.local/measures/current` returns JSON: `rco2`, `pm01`, `pm02`, `pm10`, `pm003Count`,
    `atmp`, `rhum`, `tvocIndex`, `noxIndex`, `wifi`, `firmware`, `model` and more.
  - `/metrics` serves OpenMetrics for Prometheus ([source](https://github.com/airgradienthq/arduino/blob/1a2bed8/examples/OneOpenAir/OpenMetrics.cpp#L21)).
  - `/config` is read with GET and changed with PUT, with no authentication.
  - Home Assistant discovers the monitor natively from 2024.6.
- **Its own MQTT client.**
  - Set `mqttBrokerUrl` to `mqtt://<user>:<password>@<host>:<port>`. The monitor then publishes the same JSON every
    60 s to `airgradient/readings/<serial>`
    ([topic](https://github.com/airgradienthq/arduino/blob/1a2bed8/examples/OneOpenAir/OneOpenAir.ino#L621),
    [interval](https://github.com/airgradienthq/arduino/blob/1a2bed8/examples/OneOpenAir/OneOpenAir.ino#L79)).
  - GET `/config` returns the whole stored configuration, so it hands that URL, password included, to anyone on the
    network ([source](https://github.com/airgradienthq/arduino/blob/1a2bed8/examples/OneOpenAir/LocalServer.cpp#L41-L47)).
    Give it a credential of its own, following the per-client split in CLAUDE.md, or keep it on the tray hotspot.
  - The firmware hands ESP-IDF's MQTT client the URI and nothing else: no CA certificate
    ([source](https://github.com/airgradienthq/arduino/blob/1a2bed8/src/MqttClient.cpp#L35-L37)). A verified TLS
    session to the lab's HiveMQ Cloud, which is TLS-only on 8883, is therefore doubtful. This is untested.
- **Data path.**
  - The monitor's JSON goes to the tray Pi, by polling `/measures/current` or through a broker on the Pi.
  - The Pi publishes over TLS to the lab's HiveMQ broker with the lab's existing client code.
  - A subscriber, like the OT-2 Space's, writes it to MongoDB in a `sensor-data`-style collection keyed by monitor
    serial and tray.
  - Floor monitors use the same path through one LAN broker or poller.
- **Settings to PUT on each unit.**
  - `configurationControl: "local"` and `postDataToAirGradient: false`. `disableCloudConnection`, set on the Wi-Fi
    setup page, also stops automatic firmware updates.
  - Inside a Shuttle: `ledBarMode: "off"` and `displayBrightness: 0`.
  - `abcDays`: the default is 8 and the maximum 200.
    - Senseair's ABC treats the lowest reading over the period as the "expected fresh air value of 400 ppm".
    - It is unsuitable where CO₂ never falls to background ([Senseair](https://senseair.com/the-senseair-abc-algorithm/)).
    - A Shuttle breathes lab air, so keep ABC only if the lab returns to outdoor CO₂ overnight. Otherwise turn it off
      and calibrate against a reference.

## Inside a Shuttle tray: dust, airflow and what it does not cover

- **Airflow.** The PMS5003 has its own fan, so the tray's still air doesn't stop it. The other sensors rely on the
  case's convection, so keep the top and bottom edges open.
- **Dust.** The PMS5003 [datasheet](https://cdn-shop.adafruit.com/product-files/3686/plantower-pms5003-manual_v2-3.pdf)
  sets these limits:
  - mount it "at least 20cm higher than the grand", against floc dust;
  - not "in the air flow way of the air cleaner";
  - add protection if the concentration is at or above 300 µg/m³ for more than half the year, or at or above
    500 µg/m³ for more than a fifth of it;
  - MTTF ≥ 3 years.
- **On trays that handle powder,** mount the monitor outside the downdraft, glovebox or sieve enclosure. Read its PM
  channel as an alarm for powder escaping, not as an exposure measurement.
- **No oxygen sensor.** It doesn't replace the O₂-depletion monitors needed near argon and nitrogen (PR #344, #31).
- **Not rated for hazardous locations.** Its certifications are CE, RoHS, REACH, FCC and RESET Air only, so keep it
  out of any area classified for combustible metal dust.
- **Floor stations.** Mount it where the EPA puts the "breathing zone height (3 – 6 ft)", with "free air flow", and
  away from sources such as the fume hood's exhaust
  ([EPA](https://19january2025snapshot.epa.gov/air-sensor-toolbox/guide-siting-and-installing-air-sensors)). Its
  screw holes match common US junction boxes, so it can go on the box at the end of the station's drop.

## Machine-readable specs

```json
{
  "airgradient_one": {
    "model": "I-9PSL",
    "use": {"tray": "no-display build if AirGradient sells it, else the standard unit with ledBarMode off and displayBrightness 0",
            "floor_station": "standard unit with display"},
    "dims_mm": [131.2, 131.2, 36.2],
    "dims_order": "W x H x D",
    "dims_mm_product_page": [130, 130, 35],
    "mass_g": 230,
    "mass_g_product_page": 350,
    "power_w_typ": 1.0,
    "power_w_max": 10.0,
    "power_note": "typ: estimate from component datasheets with the LED bar off; max: AirGradient's required 5 V >2 A supply; estimated simultaneous peak without LEDs about 3.8 W",
    "input": "USB-C, 5 V; >2 A 5 V USB-A supply required (not included); 2 m USB-A to USB-C cable",
    "network": ["Wi-Fi 2.4 GHz 802.11 b/g/n", "Bluetooth LE 5"],
    "ethernet": false,
    "poe": false,
    "local_api": ["/measures/current", "/metrics", "/config"],
    "mqtt_topic": "airgradient/readings/<serial>",
    "mqtt_interval_s": 60,
    "price_usd": {"assembled": 230, "kit": 138},
    "display": "1.3 in OLED 128 x 64 (also available without display, unpriced)",
    "leds": 11,
    "mounting": ["wall screws on US/EU junction-box spacing", "clip-on stands"],
    "colour_rgb": [0.94, 0.94, 0.93],
    "sensors": {
      "pm": {"part": "Plantower PMS5003", "outputs": ["PM1", "PM2.5", "PM10", "particle counts 0.3-10 um"], "pm25_effective_range_ugm3": [0, 500], "pm25_accuracy": "+-4 ug/m3 (0-100), +-8 % (100-500), assembled"},
      "co2": {"part": "Senseair S8 (or S88)", "range_ppm": [400, 10000], "accuracy": "+-40 ppm +-3 % of reading at 5-30 C"},
      "voc_nox": {"part": "Sensirion SGP41", "voc_index": [0, 500], "nox_index": [0, 500]},
      "temp_rh": {"part": "Sensirion SHT40", "temp_accuracy_c": 0.2, "rh_accuracy_pct": 2}
    },
    "operating_temp_c_from_parts": [-10, 50],
    "sources": ["https://www.airgradient.com/indoor/",
                "https://www.airgradient.com/documents/spec-sheets/Spec_Sheet_AirGradient_ONE_I-9PSL.pdf"]
  },
  "airgradient_open_air": {
    "model": "O-1PST",
    "use": "not recommended for the trays or floor stations",
    "dims_mm": [91.5, 86.7, 85.0],
    "mass_g": 180,
    "power_w_typ": 1.0,
    "power_w_max": 10.0,
    "power_note": "same estimate and supply requirement as the ONE, without display or LED bar",
    "input": "USB-C, 5 V; >2 A 5 V USB-A supply required (not included); 4 m cable",
    "network": ["Wi-Fi 2.4 GHz 802.11 b/g/n", "Bluetooth LE 5"],
    "ethernet": false,
    "poe": false,
    "price_usd": {"assembled": 225, "kit": 125},
    "display": null,
    "sensors": {
      "pm": {"part": "Plantower PMS5003T", "pm25_accuracy": "+-5 ug/m3 (0-100), +-8 % (100-500)"},
      "co2": {"part": "Senseair S8 (or S88)", "range_ppm": [400, 10000]},
      "voc_nox": {"part": "Sensirion SGP41"},
      "temp_rh": {"part": "inside the PMS5003T", "temp_accuracy_c": 0.5, "rh_accuracy_pct": 2, "note": "reads warm; needs correction"}
    },
    "sources": ["https://www.airgradient.com/outdoor/",
                "https://www.airgradient.com/documents/spec-sheets/Spec_Sheet_AirGradient_Open_Air_O-1PST.pdf"]
  }
}
```
