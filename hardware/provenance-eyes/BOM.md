# Provenance Eyes: bill of materials and cost

Prices were checked on 2026-11-12, in USD. *Est.* marks a figure we estimated rather than read off
a listing. Masses are in [`cad/layout.py`](cad/layout.py).

## Default build: about $177

| # | Part | Qty | Unit | Line | Source and notes |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | Raspberry Pi Zero 2 W | 1 | $15.00 | $15.00 | [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) list price, unchanged through the 2025–26 memory-driven price rises ([news](https://www.raspberrypi.com/news/a-new-3gb-raspberry-pi-4-for-83-75-and-more-memory-driven-price-increases/)). It has the hardware H.264 encoder (1080p30, [product brief](https://pip-assets.raspberrypi.com/categories/584-raspberry-pi-zero-2-w/documents/RP-008359-DS-1-raspberry-pi-zero-2-w-product-brief.pdf)) and weighs 10 g ([Adafruit](https://www.adafruit.com/product/5291), $19.05, out of stock). Get it without headers and solder wires on directly; that is lighter. |
| 2 | Camera Module 3 **Wide** | 1 | $35.00 | $35.00 | 102° × 67° field of view, autofocus from about 5 cm, 4 g ([docs](https://www.raspberrypi.com/documentation/accessories/camera.html)). $35 is the [launch price](https://www.raspberrypi.com/news/new-autofocus-camera-modules/); the product page now says only "from $25", which is the standard version. |
| 3 | Camera cable, 22-pin to 15-pin ("Standard–Mini") | 1 | ~$3.00 | $3.00 | Fits the Zero ([raspberrypi.com](https://www.raspberrypi.com/products/camera-cable/), 200/300/500 mm). Adafruit sells the [300 mm for $3.16](https://www.adafruit.com/product/5819). The camera sits next to the Pi, so use the shortest you can get and fold the rest. |
| 4 | Adafruit I2S MEMS microphone, SPH0645LM4H | 2 | $6.95 | $13.90 | [Adafruit 3421](https://www.adafruit.com/product/3421), 0.4 g each. Two make a stereo pair: one SEL pin to ground, the other to 3.3 V. Adafruit has discontinued the ICS-43434 version and points to this one. |
| 5 | PiSugar 3, 1200 mAh | 1 | $39.99 | $39.99 | [PiSugar on Tindie](https://www.tindie.com/products/pisugar/pisugar-3-battery-for-raspberry-pi-zero/). Charger, real-time clock, a programmable button and a USB-C port on a Zero-sized board ([docs](https://docs.pisugar.com/docs/product-wiki/battery/pisugar3/pisugar-3-series)). The **PiSugar 3 Plus** (5000 mAh) is a 65 × 56 mm board for the Pi 3/4/5, not the Zero. |
| 6 | microSD, 64 GB, high endurance | 1 | ~$29.00 | $29.00 | SanDisk High Endurance; $29 is a [Staples](https://www.staples.com/sandisk-high-endurance-64gb-microsd-memory-card-with-adapter-class-10-uhs-i-v30-sdsqqnr-064g-gn6ia/product_IM1ZS3423) listing we didn't open. About 10 h of 1080p at 8 Mb/s. |
| 7 | Heatsink, 14 × 14 × 6 mm, adhesive | 1 | ~$1.50 | $1.50 | e.g. [The Pi Hut](https://thepihut.com/collections/raspberry-pi-cooling-heatsinks-fans/products/heatsink-for-raspberry-pi-zero-2) (£1). Avoid full-board Zero heatsinks: Waveshare's weighs 35 g. |
| 8 | 12 mm tactile push button | 1 | ~$1.00 | $1.00 | *Est.* The record button, in the right temple pod. |
| 9 | Coin vibration motor, 10 mm | 1 | ~$2.00 | $2.00 | *Est.* Buzzes on start, stop and bookmark. |
| 10 | NPN transistor, diode, resistors, red 3 mm LED | 1 set | ~$1.00 | $1.00 | *Est.* Motor driver and the recording light. |
| 11 | 4-core cable (1 m), 30 AWG silicone wire, heat shrink | 1 set | ~$8.00 | $8.00 | *Est.* 5 V, ground and I2C run to the battery pod; the mics and button run to the front. |
| 12 | M2 and M2.5 screws, heat-set inserts | 1 kit | ~$8.00 | $8.00 | *Est.* |
| 13 | **3M H8A ratchet headgear** (82501-00000) | 1 | $18.49 | $18.49 | [WebstaurantStore](https://argo.webstaurantstore.com/3m-82501-00000-h8a-blue-thermoplastic-ratchet-headgear/39982501.html). Runner-up: [Jackson Safety 370](https://www.dillonsupply.com/Product/05820696), $32.85. See the [README](README.md#the-headband). |
| 14 | PETG filament, about 70 g | — | ~$20/kg | $1.50 | *Est.* For the Pi enclosure, camera head, temple pods, battery pod and clips, printed on the lab's Bambu printers. |
| | **Total** | | | **$177.38** | Electronics (lines 1–10) $141.39; headgear $18.49; hardware and filament $17.50. |

## Options

| Option | Adds | Notes |
| --- | ---: | --- |
| Larger 1S LiPo, about 3000 mAh | ~$12–15 *(est.)* | About 3 times the run time. Adds about 30 g at the back, which moves the centre of mass 2 cm behind the ear line. Check that the PiSugar 3 charges a larger cell, and that its connector matches, before buying. |
| Pocket power bank and a 1.5 m USB-C cable | ~$30 *(est.)* | All-day running with no battery on the head. The front becomes heavy unless the Pi moves to the back of the band. |
| Spare headgear, for fitting trials | $18.49 | Lets two people try sizes and pod positions at once. |
| Pi 5 instead of the Zero 2 W | +$62.50 or more | Only if transcription has to run on the headset. 2 GB is now [$77.50](https://www.raspberrypi.com/news/price-increases-for-2gb-raspberry-pi-4-and-raspberry-pi-5/). It has **no hardware H.264 encoder**, uses 2.4–9 W ([measured](https://www.jeffgeerling.com/blog/2024/new-2gb-pi-5-has-33-smaller-die-30-idle-power-savings/)), and needs a fan and a bigger battery. Not recommended on the head. |

## Running costs

| Item | Cost | Notes |
| --- | --- | --- |
| YouTube uploads | free | `videos.insert` now has its own quota, 100 uploads a day by default ([quota](https://developers.google.com/youtube/v3/determine_quota_cost)). |
| Transcription | free | faster-whisper on a GitHub Actions runner. Private repos use the org's included Actions minutes; expect a few minutes of runner time per 10 minutes of audio. |
| Claude analysis | the lab's existing token, or about $0.25 per 30 min of video | With `anthropics/claude-code-action` and the `CLAUDE_CODE_OAUTH_TOKEN` the lab already uses, it costs nothing extra. On the API instead, with `claude-opus-5-5` at $4 in and $20 out per million tokens, a 30-minute recording is about 6k tokens of transcript plus 90 keyframes at 768 × 432 (about 440 tokens each), so roughly 48k tokens in and 3k out, or about $0.25. |
| Storage | free to low | Originals stay on the card until archived. The analysis bundle (audio and frames, a few MB) goes to a private GitHub repo as release assets. MongoDB gets metadata only, since the free tier is capped at 512 MB. |
