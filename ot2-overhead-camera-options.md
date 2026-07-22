# OT-2 Overhead Camera — Camera Options & Integration Guide

**Robot:** Opentrons OT-2 Liquid Handling Robot
**Use Case:** Overhead well plate imaging (96-well and 384-well plates)
**Mounting Approach:** "Fake pipette" — camera mounted in the second pipette slot on the OT-2 gantry
**Compute:** Raspberry Pi Zero 2W (or RPi 4B) running RPi OS Lite (bookworm)
**Software Stack:** `picamera2` / `libcamera` → Python capture → S3 upload → MQTT URI notification

> **Related Issues & References:**
> - [byu-vcl#34](https://github.com/vertical-cloud-lab/byu-vcl/issues/34) — This issue (overhead camera for OT-2)
> - [byu-vcl#9](https://github.com/vertical-cloud-lab/byu-vcl/issues/9) — Set up picam (existing RPi camera experience)
> - [a1_cam docs](https://ac-training-lab.readthedocs.io/en/latest/devices/a1_cam.html) — Reference implementation (MQTT + S3 + picamera2)
> - [RAISE press-fit camera (arXiv:2510.06546)](https://arxiv.org/abs/2510.06546) — Press-fit camera tool for OT-2 from University of Toronto
> - [RSC Digital Discovery camera tool](https://pubs.rsc.org/en/content/articlehtml/2025/dd/d4dd00334a) — Another OT-2 camera integration

---

## 1. OT-2 Internal Dimensions & Working Distance

Understanding the geometry is critical for lens/camera selection.

| Parameter | Value | Source |
|-----------|-------|--------|
| External dimensions (W × D × H) | 660 × 570 × 630 mm | [Opentrons specs](https://docs.opentrons.com/ot-2/system-description/specs/) — "66 cm × 57 cm × 63 cm (≈ 26" × 22.5" × 25")" |
| Deck slots | 11 ANSI/SLAS-compliant slots | Opentrons docs |
| Internal height (deck to lid) | **~400 mm** (~16 in) | Estimated from external height (630 mm) minus ~230 mm base/electronics; [Opentrons GitHub hardware files](https://github.com/Opentrons/ot2). **Verify by physical measurement.** |
| 96-well plate height | ~14 mm | SBS standard |
| 384-well plate height | ~14 mm | SBS standard |
| Well plate footprint | 127.76 × 85.48 mm | ANSI/SLAS 1-2004 |
| **Working distance (lid to plate surface)** | **~386 mm** (~15 in) | ~400 mm lid height − 14 mm plate height |
| **Working distance (gantry-mounted camera to plate)** | **~150–180 mm** (estimate) | Depends on gantry z-position and camera mount depth; gantry z-travel is ~218 mm |
| **Working distance (fixed mount on lid or above OT-2)** | **~386–610 mm** (~15–24 in) | Flush on lid: ~386 mm; on arm/bracket ~9" above lid: ~610 mm (~24 in) |

> **Note:** The gantry will be moved out of the way (to a home/park position) before capturing images. The "fake pipette" approach uses the second pipette slot, which has its own linear actuator for z-axis movement, giving some control over working distance.

### Well Dimensions

| Plate Type | Wells | Well Diameter | Well Spacing (center-to-center) | Well Depth |
|------------|-------|---------------|--------------------------------|------------|
| 96-well | 96 (12 × 8) | 6.86 mm | 9.0 mm | ~10–11 mm |
| 384-well | 384 (24 × 16) | 3.7 mm | 4.5 mm | ~11 mm |

---

## 2. Camera Options Comparison

### 2a. Raspberry Pi Camera Module 3 (Standard) ⭐ Recommended Baseline

| Specification | Value |
|---------------|-------|
| Sensor | Sony IMX708, 12MP (4608 × 2592) |
| Sensor size | 1/2.43" |
| Pixel size | 1.4 µm |
| Lens | Fixed, 4.74 mm focal length |
| FoV (diagonal / horizontal / vertical) | 75° / 66° / 41° |
| Focus | **Autofocus** (PDAF), 10 cm to ∞ |
| Interface | MIPI CSI-2 (15-pin ribbon cable) |
| Dimensions | 25 × 24 × 11.5 mm |
| Price | **~$25–$28** |
| Suppliers | [Raspberry Pi Store](https://www.raspberrypi.com/products/camera-module-3/), [PiShop US](https://www.pishop.us/), [CanaKit](https://www.canakit.com/) |

**FOV calculation at 170 mm working distance:**
- Horizontal FOV = 2 × 170 × tan(66°/2) ≈ **221 mm** ✅ covers full plate (128 mm)
- Vertical FOV = 2 × 170 × tan(41°/2) ≈ **127 mm** ✅ covers full plate (86 mm)
- Pixels per well (96-well, full plate in frame): ~223 × 219 px/well → **~49k pixels/well** ✅

**Pros:** Cheapest option, autofocus (critical for hands-off operation), proven `picamera2` support, smallest form factor, direct drop-in for existing a1_cam codebase.
**Cons:** Fixed lens (no optical zoom), moderate resolution per well for 384-well plates.

---

### 2b. Raspberry Pi Camera Module 3 Wide

| Specification | Value |
|---------------|-------|
| Sensor | Sony IMX708, 12MP (4608 × 2592) |
| FoV (diagonal / horizontal / vertical) | 120° / 102° / 67° |
| Focus | **Autofocus** (PDAF), 5 cm to ∞ |
| Dimensions | 25 × 24 × 12.4 mm |
| Price | **~$35–$39** |
| Suppliers | Same as Camera Module 3 |

**FOV at 170 mm:**
- Horizontal FOV ≈ **420 mm** (much wider than plate — plate would occupy ~30% of the frame)
- Vertical FOV ≈ **225 mm**
- Pixels per well (96-well): ~117 × 124 px/well → **~15k pixels/well**

**Pros:** Closer minimum focus distance (5 cm), good if camera must be very close to the plate.
**Cons:** Excessive FOV at typical working distances means the plate is small in the frame, wasting resolution. Not recommended for overhead use unless the camera is positioned very close (~50–80 mm) to the plate.

---

### 2c. Raspberry Pi HQ Camera (C/CS-Mount or M12 Mount) ⭐ Best Image Quality

| Specification | Value |
|---------------|-------|
| Sensor | Sony IMX477, 12.3MP (4056 × 3040) |
| Sensor size | 1/2.3" (6.287 × 4.712 mm) |
| Pixel size | 1.55 µm |
| Lens | **Interchangeable** — C/CS-mount or M12 mount |
| FoV | Lens-dependent |
| Focus | **Manual** (lens-dependent) |
| Interface | MIPI CSI-2 (15-pin ribbon cable) |
| Dimensions | 38 × 38 × 18.4 mm (body only, plus lens) |
| Price (body only) | **~$50–$70** |
| Lens pricing | 6 mm CS-mount: ~$25; 16 mm C-mount: ~$50; M12 lenses: ~$12–$25 each |
| Suppliers | [Raspberry Pi Store](https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/), [Adafruit](https://www.adafruit.com/product/4561), [PiShop US](https://www.pishop.us/) |

**Lens selection for OT-2 overhead imaging (170 mm working distance, full 96-well plate):**

| Lens Focal Length | Horizontal FOV at 170 mm | Vertical FOV at 170 mm | Covers Full Plate? | Pixels/Well (96-well) |
|-------------------|-------------------------|------------------------|--------------------|----------------------|
| 6 mm | 178 mm | 134 mm | ✅ Yes | ~243 × 245 ≈ **60k** |
| 8 mm | 134 mm | 100 mm | ✅ Yes (tight) | ~324 × 326 ≈ **106k** |
| 12 mm | 89 mm | 67 mm | ❌ No (crops) | Higher per-well, but needs stitching |
| 16 mm | 67 mm | 50 mm | ❌ No (crops) | Very high per-well, needs stitching |

**Lens selection for flush mount on plexiglass lid (~386 mm / ~15" working distance, full 96-well plate):**

At ~386 mm, the max focal length that covers the full plate width is ~19 mm. A 16 mm lens is optimal.

| Lens Focal Length | Horizontal FOV at 386 mm | Vertical FOV at 386 mm | Covers Full Plate? | Pixels/Well (96-well) |
|-------------------|-------------------------|------------------------|--------------------|----------------------|
| 8 mm | 303 mm | 227 mm | ✅ Yes | ~143 × 144 ≈ **21k** |
| 12 mm | 202 mm | 152 mm | ✅ Yes | ~214 × 216 ≈ **46k** |
| 16 mm | 152 mm | 114 mm | ✅ Yes (84% × 76% fill) | ~285 × 287 ≈ **82k** |
| 25 mm | 97 mm | 73 mm | ❌ No (crops) | — |

**Lens selection for fixed overhead mount (~610 mm / 24" working distance, full 96-well plate):**

At 610 mm, the max focal length that still covers the full plate width (128 mm) is **~30 mm**. A 25 mm lens gives comfortable margin; 28 mm is near-optimal.

| Lens Focal Length | Horizontal FOV at 610 mm | Vertical FOV at 610 mm | Covers Full Plate? | Pixels/Well (96-well) |
|-------------------|-------------------------|------------------------|--------------------|----------------------|
| 16 mm | 240 mm | 180 mm | ✅ Yes | ~180 × 182 ≈ **33k** |
| 25 mm | 153 mm | 115 mm | ✅ Yes | ~282 × 284 ≈ **80k** |
| 28 mm | 137 mm | 103 mm | ✅ Yes (tight, 93% × 83% fill) | ~316 × 318 ≈ **101k** |
| 35 mm | 110 mm | 82 mm | ❌ No (crops width) | — |
| 50 mm | 77 mm | 58 mm | ❌ No (crops) | — |

> **Recommended lens for gantry-mount (170 mm):** **6 mm or 8 mm** CS-mount for full-plate imaging. The 8 mm lens provides a tighter framing with more pixels per well while still covering the plate footprint. For flush-mount on lid (~386 mm), use **12–16 mm**. For 24" overhead (~610 mm), use **25 mm** (see Section 5b).

**Pros:** Best image quality (larger pixels, better low-light), interchangeable lenses allow fine-tuning of FOV and working distance, flat-field optics reduce edge distortion, upgradeable for future needs (e.g., macro lens for individual wells).
**Cons:** Manual focus requires one-time physical adjustment (not autofocus), larger form factor, higher total cost (body + lens), lens protrudes and adds bulk to the "fake pipette" assembly.

---

### 2d. Arducam 64MP Hawk-eye ⭐ Highest Resolution

| Specification | Value |
|---------------|-------|
| Sensor | Sony IMX682 (via Arducam), **64MP** (9152 × 6944) |
| Sensor size | 1/1.7" (7.4 × 5.55 mm) |
| Pixel size | 0.8 µm |
| Lens | Fixed, 5.1 mm focal length |
| FoV (diagonal / horizontal / vertical) | 84° / ~72° / ~55° |
| Focus | **Autofocus** (PDAF + CDAF), 8 cm to ∞ |
| Interface | MIPI CSI-2 (22-pin to 15-pin adapter included) |
| Dimensions | 25 × 24 mm (same as Camera Module 3) |
| Price | **~$75–$110** |
| Suppliers | [Amazon](https://www.amazon.com/dp/B0B63PCZM9), [The Pi Hut](https://thepihut.com/products/64mp-hawk-eye-autofocus-camera-module-for-raspberry-pi), [SparkFun](https://www.sparkfun.com/arducam-64mp-autofocus-camera-module.html) |

**FOV at 170 mm:**
- Horizontal FOV = 2 × 170 × tan(72°/2) ≈ **247 mm** ✅ covers full plate (128 mm)
- Vertical FOV = 2 × 170 × tan(55°/2) ≈ **177 mm** ✅ covers full plate (86 mm)
- Pixels per well (96-well, full plate in frame): ~395 × 422 ≈ **167k pixels/well** ✅✅

**Pros:** Extremely high resolution (~3.4× more pixels per well than Camera Module 3), autofocus, same form factor as Camera Module 3, excellent for 384-well plates (still ~42k pixels/well).
**Cons:** More expensive, smaller pixel size means worse low-light performance, full 64MP capture requires RPi 4B or 5 (falls back to 16MP on Zero 2W), `libcamera` support is good but Arducam-specific drivers may require additional setup.

> **Important:** Full 64MP mode requires Raspberry Pi 4B or 5. On RPi Zero 2W, output is limited to 16MP (still 4× more than needed). If using RPi Zero 2W, this limitation should be verified.

---

### 2e. Raspberry Pi Global Shutter Camera

| Specification | Value |
|---------------|-------|
| Sensor | Sony IMX296, 1.58MP (1456 × 1088) |
| Price | ~$50 |

**Not recommended** for this application. The global shutter is designed for fast-moving subjects and machine vision; its 1.58MP resolution is far too low for well plate imaging. Included here only for completeness.

---

## 3. Camera Comparison Summary

| Feature | Camera Module 3 | Camera Module 3 Wide | HQ Camera (8 mm lens) | Arducam 64MP |
|---------|-----------------|---------------------|----------------------|--------------|
| Resolution | 12MP | 12MP | 12.3MP | 64MP |
| Autofocus | ✅ Yes | ✅ Yes | ❌ Manual | ✅ Yes |
| FOV at 170 mm (H × V) | 221 × 127 mm | 420 × 225 mm | 134 × 100 mm | 247 × 177 mm |
| Covers 96-well plate? | ✅ Yes | ✅ Yes (overkill) | ✅ Yes (tight fit) | ✅ Yes |
| Pixels per well (96-well) | ~49k | ~15k | ~106k | ~167k |
| Pixels per well (384-well) | ~12k | ~4k | ~27k | ~42k |
| Min focus distance | 10 cm | 5 cm | Lens-dependent | 8 cm |
| Form factor | 25 × 24 mm | 25 × 24 mm | 38 × 38 mm + lens | 25 × 24 mm |
| RPi Zero 2W compatible | ✅ Full | ✅ Full | ✅ Full | ⚠️ 16MP mode only |
| `picamera2` support | ✅ Native | ✅ Native | ✅ Native | ✅ (with Arducam driver) |
| Total cost (camera only) | **~$25** | **~$35** | **~$75–$95** (body + lens) | **~$75–$110** |
| a1_cam codebase compatible | ✅ Drop-in | ✅ Drop-in | ✅ Minor config changes | ✅ Minor config changes |

---

## 3b. Lighting & Low-Light Performance

The OT-2 interior has limited ambient lighting — the built-in LED ring provides some illumination, but depending on lid configuration and room lighting, the camera may need to perform well in moderate to low light. This matters especially for the fixed overhead approach where the camera is farther from the plate.

### Sensor Low-Light Comparison

| Camera | Sensor | Pixel Size | Lens Aperture | Relative Light per Pixel | Low-Light Rating | Notes |
|--------|--------|-----------|---------------|-------------------------|-----------------|-------|
| **HQ Camera** | IMX477 | **1.55 µm** | **F1.4** (C-mount lenses) | **Best** (baseline; 1.55² / 1.4² ≈ 1.23) | ⭐⭐⭐⭐⭐ | Largest pixels + fastest available aperture. Best choice for low light. |
| Camera Module 3 | IMX708 | 1.4 µm | F1.8 (fixed) | ~0.49× HQ | ⭐⭐⭐ | Good for moderate lighting. BSI sensor with Quad Bayer binning helps in low light. |
| Camera Module 3 Wide | IMX708 | 1.4 µm | F2.2 (fixed) | ~0.33× HQ | ⭐⭐ | Wider FOV and slower aperture reduce per-pixel light. |
| Arducam 64MP | IMX682 | **0.8 µm** | F1.8 (fixed) | ~0.16× HQ | ⭐⭐ | Tiny pixels collect much less light. Quad Bayer binning (to 16MP/1.6 µm effective) helps, but still noisier than HQ Camera. Indoor images can be dark without exposure adjustments. |

> **Relative light per pixel** is proportional to (pixel_size)² / (F-number)². The HQ Camera with an F1.4 lens collects roughly **2× more light per pixel** than Camera Module 3, and **~6× more** than the Arducam 64MP at native resolution.

### Practical Implications

- **HQ Camera + F1.4 C-mount lens** is the clear winner for low light. The 25 mm and 8–50 mm zoom lenses recommended for the overhead mount are both F1.4, maximizing light collection at the ~24" working distance.
- **Camera Module 3** performs well in moderate indoor lighting and can use longer exposure times (up to ~1 s with `picamera2`) to compensate. Since the plate and camera are stationary, motion blur is not a concern.
- **Arducam 64MP** is the most challenging in low light due to 0.8 µm pixels. It benefits from Quad Bayer pixel binning (grouping 4 pixels → effective 1.6 µm at 16MP), but still lags behind the HQ Camera. Best suited for well-lit conditions.
- **All cameras** support configurable exposure time, analog/digital gain, and white balance via `picamera2`. For a stationary well plate, exposures of 100–500 ms are practical and significantly improve low-light capture.

### Lighting Recommendations

| Scenario | Adequate? | Recommendation |
|----------|-----------|----------------|
| OT-2 LED ring on, room lights on | ✅ All cameras | Any camera works fine |
| OT-2 LED ring on, room lights off | ✅ HQ Camera, ⚠️ Camera Module 3, ⚠️ Arducam 64MP | HQ Camera is best; others need longer exposure or supplemental light |
| Lid closed, minimal ambient light | ⚠️ HQ Camera, ❌ Others without help | Add a small LED ring or strip near the camera/cutout (~$5–$15 for a USB-powered LED ring) |
| Through plexiglass cutout at 24" | ✅ HQ Camera (F1.4 lens) | The F1.4 aperture on the recommended lenses is excellent for this distance; the OT-2's internal LEDs may be sufficient |

> **Tip:** If lighting is insufficient, a USB-powered LED ring light (~$5–$15 on Amazon) can be mounted around the plexiglass cutout or on the camera bracket. This provides consistent, diffuse illumination and eliminates dependence on ambient light conditions. The `picamera2` library also supports auto-exposure and auto-white balance to adapt to varying lighting.

---

## 4. Compute Module Options

The camera requires a Raspberry Pi to drive it and handle MQTT/S3 communication.

| Board | Price | WiFi | Camera Interface | Notes |
|-------|-------|------|-----------------|-------|
| **RPi Zero 2W** (recommended) | ~$15 (MSRP), ~$20–$35 (street) | ✅ 2.4 GHz | Mini CSI (needs adapter cable) | Proven in a1_cam setup; compact; sufficient for image capture + upload |
| RPi 4B | ~$35–$55 | ✅ 2.4/5 GHz | Standard CSI | Required for full 64MP Arducam; overkill for Camera Module 3 |
| RPi 5 | ~$60–$80 | ✅ 2.4/5 GHz | Standard CSI (new connector) | Most powerful; unnecessary for point-and-shoot |

> **Recommendation:** RPi Zero 2W for Camera Module 3 or HQ Camera. RPi 4B if using Arducam 64MP at full resolution.

---

## 5. Mounting Approach — "Fake Pipette"

The team has decided on a "fake pipette" approach where the camera occupies the second pipette slot on the OT-2 gantry.

### Advantages
- Uses the existing linear actuator in the second pipette slot for z-axis movement
- Moves with the gantry in X-Y, allowing the camera to be positioned over any deck slot
- Does not require cutting holes in the plexiglass lid
- The gantry can be parked out of the way during liquid handling

### Mounting Considerations
1. **Press-fit adapter:** A 3D-printed adapter that fits into the pipette mount, similar to the [RAISE system (arXiv:2510.06546)](https://arxiv.org/abs/2510.06546) which uses a press-fit camera holder mimicking a pipette tip form factor
2. **Mounting screws:** The OT-2 pipette mount has existing mounting holes that can be used to attach a 3D-printed camera bracket
3. **Cable routing:** The MIPI CSI-2 ribbon cable from the camera needs to route back to the RPi, which can be mounted on the gantry frame or inside the OT-2 enclosure. Ribbon cable lengths up to 300 mm (or longer with extension cables) are available
4. **Power:** The RPi Zero 2W can be powered via USB from the OT-2's internal USB ports, or via a separate 5V supply routed along the gantry

### Software Integration
The camera can be treated as a "fake pipette" in the OT-2 protocol — moving the gantry to position the camera over a target well plate, lowering via the z-axis for optimal focus distance, capturing an image, and then parking the camera out of the way for pipetting operations.

For the capture workflow, the existing [a1_cam architecture](https://ac-training-lab.readthedocs.io/en/latest/devices/a1_cam.html) can be reused:
1. Orchestrator sends `{"command": "capture_image"}` via MQTT to the camera's read topic
2. RPi captures image using `picamera2` (with autofocus cycle if supported)
3. RPi uploads JPEG to AWS S3 via `boto3`
4. RPi publishes S3 URI back via MQTT on the camera's write topic
5. Orchestrator downloads/stores the image URI

---

## 5b. Alternative Mounting Approach — Fixed Overhead (Plexiglass Cutout)

An alternative to the "fake pipette" approach is mounting the camera **above the OT-2** on an external arm or bracket, looking down through a small cutout in the plexiglass lid. The gantry is moved out of the way before each image capture.

### Geometry

The camera-to-plate distance depends on where the camera is positioned:
- **Flush on plexiglass lid:** ~386 mm (~15 in) — the internal deck-to-lid clearance is ~400 mm, minus ~14 mm plate height
- **On arm/bracket above lid:** If mounted on an arm extending ~9" (224 mm) above the plexiglass top, the total distance from camera to plate surface is approximately **~610 mm (~24")**

> **Note:** If the camera is placed directly *on* the plexiglass (flush mount), the distance is ~386 mm (~15 in). At this distance, the HQ Camera with a **12 mm lens** covers the full plate at 63% fill (~46k px/well), or a **16 mm lens** at 84% fill (~82k px/well). This is a viable simpler option if 24" is not required.

### Why the HQ Camera + Telephoto Lens Is Required at 24"

Fixed-lens cameras (Camera Module 3, Arducam 64MP) have short focal lengths (4.7–5.1 mm), so at 610 mm the well plate occupies only ~15–18% of the frame. This wastes most of the sensor resolution:

| Camera | Focal Length | FOV at 610 mm (H × V) | Plate % of Frame | Pixels/Well (96) |
|--------|-------------|----------------------|-----------------|-----------------|
| Camera Module 3 | 4.74 mm | 716 × 403 mm | 18% × 21% | ~69 × 69 ≈ **5k** ❌ |
| Arducam 64MP | 5.1 mm | 885 × 664 mm | 14% × 13% | ~110 × 112 ≈ **12k** ⚠️ |
| **HQ Camera + 25 mm** | **25 mm** | **153 × 115 mm** | **83% × 75%** | **~282 × 284 ≈ 80k** ✅ |
| **HQ Camera + 28 mm** | **28 mm** | **137 × 103 mm** | **93% × 83%** | **~316 × 318 ≈ 101k** ✅✅ |

The RPi HQ Camera with a **25 mm C-mount telephoto lens** is the clear choice for this distance, delivering **80k pixels per well** — more than enough for precipitate detection and intensity measurement.

### Recommended Lens Options for 610 mm

| Lens | Focal Length | Type | Min Focus | Price | Supplier |
|------|-------------|------|-----------|-------|----------|
| **Waveshare 25 mm C-mount** (recommended — simple) | 25 mm fixed | C-mount, F1.4, manual focus/iris | ~20–30 cm | **~$34** | [Waveshare ($34)](https://www.waveshare.com/25mm-telephoto-lens-for-pi.htm), [Amazon ($34)](https://www.amazon.com/dp/B08BRRKDCH) |
| **Arducam 8–50 mm zoom** (recommended — versatile) | 8–50 mm varifocal | C-mount, F1.4, manual zoom/focus/iris | 50 cm (0.5 m) | **~$70–$80** | [Amazon ($75)](https://www.amazon.com/dp/B08PYMBX9T), [Welectron (€57)](https://www.welectron.com/Arducam-LN057-8-50mm-C-Mount-Zoom-Lens-for-IMX477-Raspberry-Pi-HQ-Camera_1) |
| Arducam/Waveshare 16 mm C-mount | 16 mm fixed | C-mount, manual | ~20 cm | ~$30–$50 | Amazon, Waveshare |

> **Best pick:** The **Arducam 8–50 mm zoom** (~$75) is the most versatile — dial it to ~25–28 mm to frame the full plate, or zoom further to inspect individual wells. Its 50 cm minimum focus distance is well within the 610 mm working distance. The **Waveshare 25 mm** (~$34) is the simpler/cheaper option if you don't need zoom.

### Advantages of Fixed Overhead Mount
- **No interference with gantry or pipettes** — camera is completely separate from the OT-2 mechanism
- **Simpler integration** — no "fake pipette" software complexity; just park the gantry, trigger MQTT, capture
- **Fixed focus** — once manually set, focus doesn't change (working distance is constant)
- **Accessible** — easy to adjust lens, clean, or replace without opening the OT-2
- **No ribbon cable routing inside the OT-2** — RPi sits outside, near the camera

### Disadvantages
- **Requires a small cutout** in the plexiglass lid (or removing the lid during imaging)
- **Fixed position** — cannot reposition over different deck slots without moving the entire camera mount (unless the camera covers the full deck, which would reduce per-well resolution)
- **External arm/bracket needed** — must be stable to avoid vibration/blur; 3D-printed or aluminum extrusion bracket recommended
- **Manual focus only** — HQ Camera lenses are all manual focus (not autofocus); however, focus only needs to be set once since the distance is fixed

---

## 6. Recommended Configurations

### 6a. Fake Pipette: Camera Module 3 + RPi Zero 2W

| Component | Part | Est. Cost |
|-----------|------|-----------|
| Camera | Raspberry Pi Camera Module 3 (Standard) | ~$25 |
| Compute | Raspberry Pi Zero 2W | ~$15–$20 |
| CSI cable | Mini-to-standard CSI adapter cable (for Zero) | ~$3–$5 |
| SD card | 16 GB+ microSD | ~$8–$10 |
| Power | USB micro cable (or tap OT-2 internal power) | ~$5 |
| Mount | 3D-printed press-fit adapter (in-house) | ~$2–$5 (filament) |
| **Total** | | **~$58–$65** |

**Rationale:** This matches the proven a1_cam setup (same camera, same compute, same software stack). Autofocus eliminates the need for manual focus adjustment when the z-distance varies. The compact form factor fits easily in the pipette slot. The existing `device.py` codebase from [ac-dev-lab](https://github.com/AccelerationConsortium/ac-dev-lab/tree/main/src/ac_training_lab/a1_cam) can be reused with minimal modification.

### 6b. Fake Pipette Upgrade: Arducam 64MP + RPi 4B

| Component | Part | Est. Cost |
|-----------|------|-----------|
| Camera | Arducam 64MP Hawk-eye | ~$75–$110 |
| Compute | Raspberry Pi 4B (2GB) | ~$35–$45 |
| CSI cable | Standard 15-pin CSI cable (included with Arducam) | ~$0 |
| SD card | 32 GB+ microSD | ~$10–$12 |
| Power | USB-C cable + 5V/3A supply | ~$10 |
| Mount | 3D-printed press-fit adapter (in-house) | ~$2–$5 (filament) |
| **Total** | | **~$132–$182** |

**Rationale:** If higher resolution is needed — especially for 384-well plates where wells are only 3.7 mm across — the 64MP sensor provides ~5× more pixels per well. The RPi 4B is required for full 64MP capture but also has 5 GHz WiFi for faster image uploads.

### 6c. Fake Pipette: HQ Camera (Maximum Optical Quality)

| Component | Part | Est. Cost |
|-----------|------|-----------|
| Camera | Raspberry Pi HQ Camera (CS-mount) | ~$50 |
| Lens | 8 mm CS-mount lens | ~$25–$50 |
| Compute | Raspberry Pi Zero 2W | ~$15–$20 |
| CSI cable | Mini-to-standard CSI adapter cable (for Zero) | ~$3–$5 |
| SD card | 16 GB+ microSD | ~$8–$10 |
| Power | USB micro cable | ~$5 |
| Mount | 3D-printed adapter (larger, for HQ Camera body + lens) | ~$3–$5 (filament) |
| **Total** | | **~$109–$145** |

**Rationale:** Best per-pixel image quality due to larger pixels (1.55 µm vs 1.4 µm) and interchangeable optics. The 8 mm lens provides a tight, well-framed view of the full plate. However, manual focus is a drawback — once set for a fixed working distance, it should remain in focus, but any change in z-height requires manual re-adjustment. Best suited if optical quality and upgradeability are priorities and the working distance will remain constant.

### 6d. Fixed Overhead Mount: HQ Camera + 25 mm Telephoto + RPi Zero 2W ⭐ Best for Fixed Position

| Component | Part | Est. Cost |
|-----------|------|-----------|
| Camera | Raspberry Pi HQ Camera (CS-mount) | ~$50–$70 |
| Lens (option A — simple) | Waveshare 25 mm C-mount telephoto | ~$34 |
| Lens (option B — versatile) | Arducam 8–50 mm C-mount zoom | ~$75 |
| Compute | Raspberry Pi Zero 2W | ~$15–$20 |
| CSI cable | Standard 15-pin or mini-to-standard adapter | ~$3–$5 |
| SD card | 16 GB+ microSD | ~$8–$10 |
| Power | USB micro cable + 5V supply | ~$5–$10 |
| Mount | Aluminum extrusion arm or 3D-printed bracket + plexiglass cutout | ~$15–$30 |
| **Total (25 mm lens)** | | **~$130–$179** |
| **Total (zoom lens)** | | **~$171–$220** |

**Performance at ~610 mm (24"):**
- **25 mm lens:** FOV 153 × 115 mm → full plate in frame → **~80k pixels/well** (96-well), ~20k (384-well)
- **Zoom at 28 mm:** FOV 137 × 103 mm → plate fills 93% of frame → **~101k pixels/well** (96-well), ~25k (384-well)

**Rationale:** This is the best approach for a fixed overhead camera at ~24" distance. The HQ Camera with a 25 mm telephoto provides excellent resolution (80k px/well) despite the large working distance — well above the ~10k minimum needed for intensity measurement (see Section 8 resolution requirements analysis). The zoom lens option adds ~$40 more but gives the flexibility to fine-tune framing or zoom into individual wells. Manual focus is set once and left alone since the working distance is fixed. The RPi Zero 2W sits outside the OT-2 enclosure (no cable routing inside the robot), making setup simpler. Total cost stays well under the $500 budget.

---

## 7. USB Microscope Alternatives

USB microscopes were discussed as alternatives for higher magnification per-well imaging. While not the primary recommendation (the team has decided on RPi cameras), they remain a viable option for future close-up inspection.

| Model | Resolution | Magnification | Working Distance | Focus | Price | Control |
|-------|-----------|---------------|-----------------|-------|-------|---------|
| Plugable USB2-MICRO-250X | 2MP | 10×–250× | 1–200 mm | Manual | ~$30–$40 | USB UVC, Python (OpenCV) |
| Dino-Lite AM7915MZT | 5MP | 10×–220× | 11–300+ mm | **Motorized** | ~$600–$900 | USB, DinoCapture SDK, Python API |
| Dino-Lite AM4113T | 1.3MP | 10×–50× | 5–300 mm | Manual | ~$300–$400 | USB, DinoCapture SDK |
| Amscope MU300 | 3MP | 40×–2000× (with objectives) | Objective-dependent | Manual | ~$200–$400 | USB, AmScope driver |

> **Note:** Dino-Lite models with programmable LED and motorized focus (e.g., AM7915MZT) offer the most control for automated imaging but are significantly more expensive. For basic well plate overview imaging, the RPi camera approach is far more cost-effective and integrates better with the existing MQTT/S3 stack.

---

## 8. Resolution Requirements Analysis

What resolution do we actually need per well?

| Target | Wells | Well Diameter | Min Useful Resolution/Well | Justification |
|--------|-------|---------------|---------------------------|---------------|
| Detect precipitate (yes/no) | 96 | 6.86 mm | ~50 × 50 px (2.5k) | Binary detection of turbidity |
| Measure precipitate intensity | 96 | 6.86 mm | ~100 × 100 px (10k) | Grayscale/color intensity quantification |
| Resolve precipitate morphology | 96 | 6.86 mm | ~200 × 200 px (40k) | Particle size estimation |
| Detect precipitate (384-well) | 384 | 3.7 mm | ~50 × 50 px (2.5k) | Binary detection |

All camera options above exceed the minimum useful resolution for precipitate detection and intensity measurement in 96-well plates. Even for 384-well plates, the Camera Module 3 provides ~12k pixels per well — sufficient for binary detection and basic intensity measurement. The HQ Camera and Arducam 64MP offer significantly more headroom for morphology analysis.

---

## 9. Next Steps

1. **Order Camera Module 3 + RPi Zero 2W** as the primary setup (lowest cost, fastest to deploy, reuses existing a1_cam software)
2. **Design and 3D-print** a press-fit camera mount for the second pipette slot — reference the [RAISE system design](https://arxiv.org/abs/2510.06546) for inspiration
3. **Adapt the a1_cam `device.py`** for the OT-2 overhead camera, modifying:
   - MQTT topics (e.g., `ot2/overhead-cam/request/{serial}` and `ot2/overhead-cam/response/{serial}`)
   - Camera orientation/transform settings (may need `vflip` and/or `hflip` depending on mount orientation)
   - Image quality/compression settings as needed
4. **Integrate with OT-2 protocol** — add commands to move the gantry to position the camera over the well plate, trigger a capture via MQTT, and wait for the image URI response
5. **Test and calibrate** — verify focus, FOV, and image quality at the actual working distance inside the OT-2
6. **Consider Arducam 64MP upgrade** later if higher resolution is needed for 384-well plate experiments or morphology analysis

---

## 10. References

- [Opentrons OT-2 Specifications](https://docs.opentrons.com/ot-2/system-description/specs/)
- [Opentrons OT-2 Hardware Files (GitHub)](https://github.com/Opentrons/ot2)
- [Raspberry Pi Camera Module 3 Product Page](https://www.raspberrypi.com/products/camera-module-3/)
- [Raspberry Pi HQ Camera Product Page](https://www.raspberrypi.com/products/raspberry-pi-high-quality-camera/)
- [Arducam 64MP Hawk-eye Wiki](https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/64MP-Hawkeye/)
- [a1_cam Documentation (AC Training Lab)](https://ac-training-lab.readthedocs.io/en/latest/devices/a1_cam.html)
- [a1_cam Source Code (ac-dev-lab)](https://github.com/AccelerationConsortium/ac-dev-lab/tree/main/src/ac_training_lab/a1_cam)
- [RAISE: Press-fit Camera for OT-2 (arXiv:2510.06546)](https://arxiv.org/abs/2510.06546)
- [RSC Digital Discovery Camera Tool](https://pubs.rsc.org/en/content/articlehtml/2025/dd/d4dd00334a)
- [Camera Positioning Guide (raspberrypi-guide.github.io)](https://raspberrypi-guide.github.io/electronics/camera-positioning)
- [Arducam Lens Guide for HQ Camera](https://blog.arducam.com/raspberry-pi-high-quality-camera-lens/)
- [Seeed Studio HQ Camera Lens Guide](https://www.seeedstudio.com/blog/2020/06/18/a-complete-guide-to-help-you-choose-lenses-for-your-raspberry-pi-high-quality-camera-m/)

---

## 11. Sourcing Guide — DigiKey BOM for Fixed Overhead (Plexiglass) Configuration

This bill of materials sources as much as possible from **DigiKey** for simplified procurement. The zoom lens is not available on DigiKey and must be ordered separately.

### Primary Components (DigiKey)

| # | Component | Mfr Part | DigiKey Part | Price (USD) | DigiKey Link |
|---|-----------|----------|-------------|-------------|--------------|
| 1 | **RPi HQ Camera** (IMX477, C-mount) | SC1220 | 2648-SC1220-ND | ~$50 | [DigiKey SC1220](https://www.digikey.com/en/products/detail/raspberry-pi/SC1220/12339164) |
| 2 | **Raspberry Pi 5** (4 GB) | SC1111 | 2648-SC1111-ND | ~$60 | [DigiKey SC1111](https://www.digikey.com/en/products/detail/raspberry-pi/SC1111/21658261) |
| 3 | **RPi 5 27W USB-C Power Supply** (US plug) | SC1153 | 2648-SC1153-ND | ~$12 | [DigiKey SC1153](https://www.digikey.com/en/products/detail/raspberry-pi/SC1153/21658276) |
| 4 | **RPi 5 Camera Cable** (22-pin → 15-pin, 200 mm) | SC1189 | 2648-SC1189-ND | ~$2 | [DigiKey SC1189](https://www.digikey.com/en/products/detail/raspberry-pi/SC1189/22113927) |
| 5 | **32 GB microSD** (Class A2, official RPi) | SC1628 | 2648-SC1628-ND | ~$12 | [DigiKey SC1628](https://www.digikey.com/en/products/detail/raspberry-pi/SC1628/24627139) |
| 6 | **RPi 5 Active Cooler** (heatsink + fan) | SC1148 | 2648-SC1148-ND | ~$5 | [DigiKey SC1148](https://www.digikey.com/en/products/detail/raspberry-pi/SC1148/21658255) |
| | **DigiKey subtotal** | | | **~$141** | |

> **Note on cable length:** The 200 mm cable (SC1189) works if the RPi 5 is mounted close to the camera on the external bracket. For longer runs, the 300 mm (SC1190) and 500 mm (SC1191) are also available on DigiKey. A 500 mm cable is recommended if the Pi is positioned on the table beside the OT-2.

### Zoom Lens (not available on DigiKey — order separately)

The 8–50 mm zoom lens is not stocked by DigiKey. Two sourcing options:

| # | Component | Manufacturer | Price (USD) | Supplier | Link |
|---|-----------|-------------|-------------|----------|------|
| 7a | **Waveshare 8–50 mm C-mount Zoom** (F1.4, includes C-CS adapter) | Waveshare | ~$35 | Waveshare direct | [Waveshare 8-50mm](https://www.waveshare.com/8-50mm-Zoom-Lens-for-Pi.htm) |
| 7b | **Arducam 8–50 mm C-mount Zoom** (F1.4, includes C-CS adapter) | Arducam (LN057) | ~$75 | Amazon | [Amazon LN057](https://www.amazon.com/dp/B08PYMBX9T) |

> The Waveshare lens (~$35) is the budget option; the Arducam LN057 (~$75) has better build quality and smoother zoom action. Both are optically similar (F1.4, 8–50 mm varifocal, C-mount). The Waveshare lens was specifically linked by the PI — it has a 0.20 m minimum focus distance, which comfortably covers the ~610 mm working distance.

### Optional Accessories

| # | Component | Price (USD) | Supplier | Notes |
|---|-----------|-------------|----------|-------|
| 8 | USB LED ring light (for supplemental illumination) | ~$8–$15 | Amazon | Mount around plexiglass cutout; powered from RPi USB |
| 9 | Mounting bracket (aluminum extrusion or 3D-printed) | ~$10–$30 | Amazon / in-house | 80/20 aluminum extrusion or 3D-printed arm to hold camera ~9" above lid |

### Total Cost Summary

| Configuration | DigiKey Total | Lens (separate) | Accessories | **Grand Total** |
|---------------|--------------|-----------------|-------------|----------------|
| With Waveshare 8–50 mm zoom | ~$141 | ~$35 | ~$18–$45 | **~$194–$221** |
| With Arducam 8–50 mm zoom | ~$141 | ~$75 | ~$18–$45 | **~$234–$261** |

Both configurations are well under the **$500 budget**. The RPi 5 provides 5 GHz WiFi (faster image uploads), dual CSI ports, and ample processing power for `picamera2` and any future image processing needs.

### Why Raspberry Pi 5 Instead of Zero 2W

For the fixed overhead configuration, the RPi 5 is recommended over the Zero 2W because:
- **Dual CSI camera ports** — could add a second camera in the future without additional hardware
- **5 GHz WiFi** — ~3–5× faster image uploads to S3 compared to Zero 2W's 2.4 GHz
- **USB 3.0 ports** — can power LED lighting or connect USB peripherals directly
- **More headroom** — can run on-device image processing (e.g., OpenCV well segmentation) if needed
- **Still modest cost** — only ~$40 more than Zero 2W at street pricing
- The RPi 5 sits outside the OT-2 on the bracket, so its larger size is not a constraint
