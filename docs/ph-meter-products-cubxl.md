# pH meter products to buy for the Cub XL

Concrete, purchasable options with **live prices** for adding pH (and optionally ionic
conductivity + temperature) sensing to the Cub XL.

> **Scope note.** Follow-up to
> [issue #148](https://github.com/vertical-cloud-lab/byu-vcl/issues/148) — @sgbaird asked for
> "several different products (4 to 8) that we could buy … include prices." Earlier comments on
> that issue cover the *research* side (probe chemistry, ISFET vs. glass, and a literature survey
> of automated pH systems). This doc is the **shopping list**.
>
> **How prices were obtained.** Several of these vendors (Atlas Scientific in particular) return
> HTTP 403 to the GitHub Actions runner. Prices below were fetched over **Tailscale SSH from a lab
> Raspberry Pi** (`vcl@rpi-5-stream-cam-2wp0`), which gets HTTP 200, and were read out of each
> page's `schema.org` `offers.price` JSON-LD plus the rendered "Add to cart" price. Dimensions come
> from the vendors' own datasheet PDFs, downloaded and parsed the same way.
> **Prices captured 2026-07-31, USD unless noted. Atlas lists a two-week lead time on the mini probes.**

## The governing constraint

A standard **20 mL scintillation vial** is 28 × 61 mm with a 22-400 neck → **~15 mm mouth opening**.
Anything **≤ 12 mm OD** drops in. Depth matters too: the probe must reach the liquid *and* the
system has to be able to lift it clear, so shorter is better.

Second constraint, from the issue title discussion: **glass pH probes must be stored wet.** Two ways
out — (a) buy a solid-state **ISFET** probe that stores dry (expensive, drifts), or (b) keep a glass
probe and **park it in a capped storage-solution vial** using the capper/decapper between runs
(cheap, and the storage vial is just another vial in the rack).

---

## Summary table

| # | Product | Part # | Price | OD × length | Storage | Interface |
|:-:|---|---|---:|---|---|---|
| 1 | **Atlas Mini Lab Grade pH Probe** + EZO™ pH Circuit | ENV-20-pH + EZO-pH | **$99.99 + $45.99 = $145.98** | 12 mm × 107 mm | wet (3 mL soaker) | I²C / UART → Pi |
| 2 | **Atlas EZO-Complete pH Kit** w/ Mini pH probe | KIT-106P | **$244.99** ($194.99 + $50) | same probe | wet | **USB**, plug-and-play |
| 3 | **Atlas Micro pH Kit** (half-cell) | KIT-104P | **$299.99** (probe alone $237.99) | ~3 mm tip | wet | I²C / UART |
| 4 | **DFRobot Gravity Lab-Grade Analog pH Kit** | SEN0161-V2 | **$39.50** | 12 mm (E-201-C) | wet | analog → ADC |
| 5 | **DFRobot Gravity Industrial pH Meter Pro Kit V2** | SEN0169-V2 | **$64.90** | 12 mm, IP68 | wet, continuous-immersion rated | analog → ADC |
| 6 | **Hanna HI1083B micro-bulb pH electrode** | HI1083B | **$469.99** | 12 → 5 → **3 mm** tip, 120 mm | wet | BNC (needs amp) |
| 7 | **Vernier Go Direct pH Sensor** | GDX-PH | **$119.00** | 12 mm | wet | **USB/BLE**, `godirect` Python |
| 8 | **Sentron wireless ISFET pH/T meter** (+ MicroFET probe) | LanceFET / MicroFET | **€920 + €115 = €1,035** | **3 mm** × 110 mm (MicroFET) | **DRY** ✅ | BLE + app (no official Python API) |
| — | *Add-on:* Atlas Mini EC K1.0 + EZO-EC + PT-1000 | ENV-20-EC-K1.0 / EZO-EC / ENV-TMP | **$109.99 + $67.99 + $23.99 = $201.97** | 12 mm × 84 mm (EC) | **dry** ✅ (EC) | same I²C bus |

---

## 1. Atlas Scientific Mini Lab Grade pH Probe + EZO™ pH Circuit — $145.98 · *recommended starting point*

- [Mini Lab Grade pH Probe, ENV-20-pH — **$99.99**](https://atlas-scientific.com/probes/mini-ph-probe/)
  ([datasheet PDF](https://files.atlas-scientific.com/Mini_pH_probe.pdf))
- [EZO™ pH Circuit, EZO-pH — **$45.99**](https://atlas-scientific.com/embedded-solutions/ezo-ph-circuit/)

From the datasheet: **Ø 12 mm, 107 mm overall**, minimum immersion **16 mm**, ships with a **3 mL
soaker bottle**. Range 0–14, resolution ±0.001, accuracy ±0.002, response 95 % in 1 s, −5 to 99 °C,
male SMA connector, 1 m cable. Recalibrate ~1 year; working life ~2 years (5 years on the shelf).

**Why it's first:** it is the smallest *robust* probe that clears the vial mouth, the EZO circuit
speaks I²C/UART straight to a Raspberry Pi with
[Atlas's own Pi sample code](https://github.com/AtlasScientific/Raspberry-Pi-sample-code), and the
whole stack is already de-risked elsewhere in our group. Quantity breaks: $94.99 at 4+, $92.50 at
10+, $89.99 at 25+.

**Catch:** wet storage. That's what the capped parking-vial idea in this issue solves — and the
3 mL soaker bottle it ships with is roughly the volume of storage solution a 20 mL vial would hold.

## 2. Atlas EZO-Complete pH Kit (KIT-106P) — $244.99 · *no electronics work*

[Product page](https://atlas-scientific.com/kits/ezo-complete-ph-kit/) — base **$194.99**, plus
**$50** for the Mini Lab Grade probe option (the same ENV-20-pH as above). Optional certificate of
calibration +$55.

Same probe, but the EZO-Complete module is **USB** — plug into a PC or Pi, install Atlas Desktop,
done. Pay ~$99 over option 1 to skip carrier-board wiring and level shifting. Good choice if we want
pH working this semester and would rather spend the integration time on the capper/decapper.

## 3. Atlas Micro pH Kit (KIT-104P) — $299.99 · *smallest Atlas option, but read the caveats*

[Micro pH Kit — **$299.99**](https://atlas-scientific.com/kits/micro-ph-kit/) ·
[Micro pH Probe alone, ENV-10-pH — **$237.99**](https://atlas-scientific.com/probes/micro-ph-probe/)
([datasheet](https://files.atlas-scientific.com/Micro-pH-probe.pdf))

Designed for microfluidics. Because it's so small it is a **half-cell** design: you get a separate
micro pH probe *and* a micro reference probe (both must go in the sample), plus an optional
half-cell SMA adapter (+$5.99) and pH flow cell (+$74.99).

**Caveats straight from Atlas's datasheet, and they are serious for a walk-away system:**
**recalibrate ~every month**, life expectancy **~6–24 months**, and *"do not pull on the probe or
twist the cable … best suited for scientific research, not intended to be used in a commercial
product."* Two probes to park and clean instead of one. Only worth it if we go to sub-mL volumes.

## 4. DFRobot Gravity Lab-Grade Analog pH Kit (SEN0161-V2) — $39.50 · *cheap spare / test rig*

[Product page](https://www.dfrobot.com/product-1782.html) — ships with calibration solutions. Uses a
standard 12 mm E-201-C lab probe and an analog signal board (needs an ADC on the Pi, e.g. ADS1115).
Accuracy ~±0.1 pH — an order of magnitude worse than the Atlas mini, but at $39.50 it's the right
thing to break while developing the parking-vial/capper motion, and a fine backup probe.

## 5. DFRobot Gravity 7/24 Industrial Analog pH Meter Pro Kit V2 (SEN0169-V2) — $64.90

[Product page](https://www.dfrobot.com/product-2069.html) — IP68 industrial probe rated for
**continuous immersion** (the "7/24" in the name), ±0.1 pH. Interesting precisely because it is
*designed to live in liquid*: if we end up with a permanently-submerged reference/monitoring channel
rather than a dip-and-park channel, this is the cheap way to do it.

## 6. Hanna HI1083B micro-bulb pH electrode — $469.99 · *smallest glass tip*

[Hanna product page](https://hannainst.com/hi1083b-combination-ph-electrode-with-micro-bulb.html)
(BNC) · [HI1083P](https://hannainst.com/micro-ph-electrode-hi1083p.html) (BNC + pin)

120 mm glass body stepping **12 mm → 5 mm → 3 mm** at the tip; measures samples as small as
**100 µL**; open junction with viscolene gel electrolyte (no refilling); 0–50 °C. Sold for 96-well
plates and precious samples.

It's a bare electrode — no electronics. Pair it with the **EZO-pH circuit ($45.99)** plus a
[female BNC → male SMA adapter, 5-pack, **$11.99**](https://atlas-scientific.com/connectors/female-bnc-to-male-sma-connectors/),
giving a ~$528 small-tip glass channel on the same I²C stack as option 1.

## 7. Vernier Go Direct pH Sensor (GDX-PH) — $119.00 · *easiest software path*

[Product page](https://www.vernier.com/product/go-direct-ph-sensor/) — $119.00 single sensor
(a $1,029 8-pack + charge station also exists). USB **and** Bluetooth, with an official Python
package (`godirect`). Standard 12 mm glass probe, wet storage, education-grade accuracy.

Worth listing because it is the lowest-effort *software* integration of the bunch — but note
Vernier's pricing is "valid only for U.S. educators," which we are, and it's still a wet-storage
glass bulb.

## 8. Sentron wireless ISFET pH/T meter + MicroFET probe — €920 + €115 ≈ €1,035 · *the only true dry-storage option*

[ESTEDE Scientific listing](https://en.estede-scientific.com/Sentron-ISFET-wireless-pH-Meters)
(**€920,00** per unit, MicroFET probe option **+€115,00**) ·
[Sysmatec MicroFET page](https://sysmatec.ch/en/product/isfet-micro-ph-probe-sentron-microfet/) ·
[Millar/Sentron probes](https://www.millar.com/our-expertise/off-the-shelf-products/probes)

Solid-state ISFET instead of a glass bulb: **stores dry**, so the parking vial, the storage solution
and the capper/decapper choreography all go away. The **MicroFET** body is **3 mm × 110 mm** — it
drops into a 20 mL vial with room to spare — and it reads **pH + temperature** in one probe. Choice
of ConeFET / LanceFET / CupFET / MicroFET tips on the same meter.

**Two real drawbacks.** (a) ~7× the cost of option 1. (b) It's a Bluetooth meter with a phone/tablet
app and **no official Python API**, so headless integration is a reverse-engineering project. ISFETs
also **drift** (~0.003 pH/h even compensated, worse at high pH and temperature), so budget for an
automated recalibration step — which is very nearly the same automation effort as the parking vial.

> Link note: `sentron.nl` product deep-links now **404** (the brand moved under millar.com); the
> ESTEDE and Sysmatec pages are live and are where the pricing above comes from.

---

## Add-on: ionic conductivity + temperature on the same bus — $201.97

@sgbaird's preference was "technically I'd rather have an ionic conductivity meter or a joint
ionic conductivity + pH + temperature meter." **No single small probe does all three off the
shelf** — but the Atlas modular stack does it on one I²C bus:

| Part | Price | Notes |
|---|---:|---|
| [Mini Conductivity Probe K 1.0, ENV-20-EC-K1.0](https://atlas-scientific.com/probes/mini-e-c-probe-k-1-0/) | **$109.99** | **Ø 12 mm × 84 mm**, min. immersion 15.5 mm, 5–200,000 µS/cm, ±2 %, 1–110 °C ([datasheet](https://files.atlas-scientific.com/Mini_EC_K_1.0_probe.pdf)) |
| [EZO™ Conductivity Circuit, EZO-EC](https://atlas-scientific.com/embedded-solutions/ezo-conductivity-circuit/) | **$67.99** | I²C / UART |
| [PT-1000 Temperature Probe](https://atlas-scientific.com/probes/pt-1000-temperature-probe/) | **$23.99** | +$2 for the optional BNC→SMA adapter |

The headline benefit: the graphite EC probe is **dry-storable and needs recalibration only ~every
10 years** (life expectancy also ~10 years). So if we build the parking vial, **only the pH probe
needs it** — EC and temperature can sit in air indefinitely.

There is also a [Mini Conductivity K 1.0 **Kit** (M-EC-KIT-1.0) at **$199.99**](https://atlas-scientific.com/kits/mini-conductivity-k-1-0-kit/)
bundling probe + circuit + calibration solutions, which is ~$22 cheaper than buying the probe and
circuit separately once you count calibration solution.

---

## Recommendation

1. **Buy option 1 now** (Atlas Mini pH + EZO-pH, **$145.98**) and build the capped parking-vial
   routine on the capper/decapper. Add option 4 (**$39.50**) as the sacrificial probe for motion
   testing — total **$185.48**.
2. **Add the EC + temperature stack** (**$201.97**) once pH works; it rides the same I²C bus and
   needs no wet storage, so it costs almost nothing in extra automation.
3. **Only escalate to option 8** (Sentron ISFET, ~€1,035) if the parking-vial approach proves
   unreliable in practice. Its dry storage is real, but the drift-driven recalibration it forces is
   about as much automation work as the thing it replaces.

**Total for the recommended path: ~$387 for pH + conductivity + temperature.**

## Link validation

All URLs cited above were fetched from the lab Pi on 2026-07-31 and returned **HTTP 200**, with
prices read from live page content:

| Domain | Result |
|---|---|
| `atlas-scientific.com` (9 product pages) | 200 — note `/circuits/ezo-ph-circuit/` → `/embedded-solutions/ezo-ph-circuit/` and `/connectors/female-bnc-to-male-sma/` → `…-connectors/` (both harmless redirects) |
| `files.atlas-scientific.com` (3 datasheet PDFs) | 200, parsed for the dimensions quoted above |
| `hannainst.com` (HI1083B, HI1083P) | 200, price in `product:price:amount` meta tag |
| `dfrobot.com` (3 products) | 200, price in JSON-LD |
| `vernier.com` (GDX-PH) | 200, price in rendered options |
| `en.estede-scientific.com` (Sentron) | 200, €920 + €115 option |
| `sysmatec.ch` (MicroFET) | 200 — descriptive only, **no public price** |
| `millar.com` | 200 (redirect from `millar.com` → `www.millar.com`) |
| `sentron.nl/product/si-serie-microfet-probe/` | **404 — dead**, do not cite |

From the GitHub Actions runner itself, `atlas-scientific.com` returns 403; every price here required
the Pi. Sysmatec and the US distributors (Instrumentors Supply, Exceltec) are **quote-only** for
Sentron, so the ESTEDE euro pricing is the only public figure.
