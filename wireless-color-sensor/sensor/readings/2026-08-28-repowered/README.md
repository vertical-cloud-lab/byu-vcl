# 2026-08-28 — sensor back online, full S1–S9 run

First successful acquisition since **2026-08-10**. The Pico W had been silent
for 18 days; @timothy-commins identified the cause in
[PR #60](https://github.com/vertical-cloud-lab/byu-vcl/pull/60) —
*"it was connected to a computer and the computer turned off"* — and repowered
the host. The device answered on the first attempt afterwards, which retires
the flat-LiPo hypothesis the earlier run recorded.

Reproduce with:

```bash
export HIVEMQ_PASSWORD=...   # or fill in my_secrets.py
export MONGODB_URI=...
python read_and_upload.py --n 6 --period 3 \
    --label "seated in base, slot 8, bench ambient" \
    --out readings/2026-08-28-repowered/readings_2026-08-28.json --upload
```

## Result: every stage passes

```
S1 PASS tcp/8883 open                 S6 PASS #76FF20, dominant 550 nm
S2 PASS CONNACK=Success               S7 PASS wrote 6 documents
S3 PASS subscribed                    S8 PASS connected to MongoDB 7.0.40
S4 PASS reply in 1.4 s   (6/6)        S9 PASS 6x inserted, read-back verified
S5 PASS 8/8 channels, none saturated
```

`readings_2026-08-28.json` holds the six documents exactly as they were
uploaded. Re-running the same file with `--replay ... --upload` reports
`updated` rather than `inserted`, so a backfill is safe to repeat.

**The upload half ran against a local MongoDB 7.0.40, not Atlas** — this
repo's Actions workflow still has no `MONGODB_URI` (see the runbook's *Known
gaps*). The readings are committed here so they can be pushed to Atlas with
`--replay` the moment that secret exists; no data is stranded.

## Readings

Six consecutive readings, ~3 s apart, module seated in its base in slot 8
under bench ambient light. Round-trip latency was 1.4 s for all six.

| 410 | 440 | 470 | 510 | 550 | 583 | 620 | 670 | sRGB | dominant |
|---|---|---|---|---|---|---|---|---|---|
| 8 | 6–7 | 14 | 179–180 | 188 | 59 | 52 | 51 | `#76FF18`–`#77FF20` | 550 nm |

CIE xy ≈ (0.321, 0.577), CCT ≈ 5700 K. As always these are **relative** —
the AS7341 reports counts, not radiance, and eight samples is a coarse basis
for a 390–830 nm integral.

## What the numbers show

![repeatability](https://github.com/vertical-cloud-lab/byu-vcl/blob/c101030/wireless-color-sensor/sensor/readings/2026-08-28-repowered/repeatability.png?raw=true)

**1. The instrument is repeatable across an 18-day power outage.** Same pose,
same base, compared against the 2026-08-10 *reseated* reading:

| channel | 2026-08-28 mean (n=6) | 2026-08-10 reseated | Δ |
|---|---|---|---|
| 410 | 8.0 | 8 | 0.0 % |
| 440 | 6.3 | 6 | +5.6 % (±1 count on a 6-count channel) |
| 470 | 14.0 | 14 | 0.0 % |
| 510 | 179.8 | 175 | +2.8 % |
| 550 | 188.0 | 184 | +2.2 % |
| 583 | 59.0 | 58 | +1.7 % |
| 620 | 52.0 | 51 | +2.0 % |
| 670 | 51.0 | 50 | +2.0 % |

The 2–3 % on the well-populated channels is the honest repeatability figure,
and it is not separable from real changes in room lighting between the two
sessions — it is an upper bound on drift, not a measurement of it. Within
today's run the spread is **≤1 count on every channel**, so per-reading noise
is far below the session-to-session term.

**2. That difference is negligible next to a real one.** The left panel puts
the same data beside the 2026-08-10 mid-air reading: lifting the module out of
its base moves 620 nm from 51 to 1084 counts, a **21×** change. Pose still
dominates everything, which is the constraint any real colorimetric protocol
has to design around — fixed height, fixed illumination.

**3. The R/Y/B command still does nothing.** Commanding `255/0/0`, `0/255/0`
and `0/0/255` against a `0/0/0` baseline moved no channel by more than
**1 count**. This confirms on maximum contrast what 2026-08-10 saw at
`50/50/50`: the upstream firmware accepts the LED field and ignores it, so
every colour this device reports is ambient. Driving the illuminant is a
firmware change (see [README](../../README.md)), not a wiring problem.
