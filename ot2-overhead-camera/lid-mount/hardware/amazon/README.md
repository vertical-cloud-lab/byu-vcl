# The nylon M2.5 kit: what's in it and what the mount uses

Every M2.5 part on the mount is **black nylon** from COMRUN's 350-piece M2.5 standoff kit,
[Amazon B0CKBWQSNY](https://www.amazon.com/dp/B0CKBWQSNY/) (part number SO350NYM25, $9.99 on
2026-10-03). The lab has two of them, plus one of the M2 version,
[B0BXT4FG1T](https://www.amazon.com/dp/B0BXT4FG1T/) (SO350NYM2), which this mount doesn't use
([sgbaird](https://github.com/vertical-cloud-lab/byu-vcl/pull/234)). The listings were read on
2026-10-03; [`kits.json`](kits.json) has the details.

### What the M2.5 kit holds

| Part | Sizes | Each |
|---|---|---|
| Male–female hex standoffs (hex body + 6 mm stud) | 6, 10, 15 and 20 mm bodies | 25 |
| Female–female hex standoffs | 6, 10, 15 and 20 mm | 25 |
| Phillips pan-head screws ("PM") | 6, 8 and 12 mm | 20 |
| Hex nuts | | 50 |
| Washers | | 40 |

The M2 kit has the same layout in M2, with the same quantities.

The page's text gives only the total of 350, so the contents come from the chart in its
"From the manufacturer" section. The M2 page lists the same layout in text. COMRUN gives no
dimensions for the M2.5 parts. The model uses 5 mm across the flats for the standoffs and a
5.0 × 2.0 mm pan head, which is usual for M2.5 nylon. **The kit has no screw longer than 12 mm.**

### What the mount takes from it

| Joint | From the kit | Qty | Fit ([`cad/fastener_fit.py`](../../cad/fastener_fit.py)) |
|---|---|---|---|
| Camera → deck | **PM M2.5 × 12**, up through the camera's corner holes and the deck's bosses | 4 | The longest in the kit, and just long enough. Through the 1.4 mm board, the 6 mm boss and the 5 mm deck, its tip ends 0.1 mm below the top of a full 2.0 mm nut, about 4 threads in. The camera and lens weigh about 0.2 kg, or 0.5 N per screw. |
| | **M2.5 nut**, in the traps on the deck top | 4 | |
| Pi 5 → deck | **M2.5 6 + 6 male–female standoff**: the stud goes down through the deck | 4 | The 6 mm stud reaches 1.3 mm past the nut and ends 1.0 mm below the deck, where nothing is in the way |
| | **M2.5 nut**, in the traps in the deck's underside, onto each stud | 4 | |
| | **PM M2.5 × 6**, down through the Pi 5 into the standoffs | 4 | 4.4 mm of thread in each standoff. An 8 mm would need a hole deeper than the 6 mm body |
| **Total** | 4 × PM 12, 4 × PM 6, 4 × 6 + 6 male–female standoffs, 8 nuts | | All of them are well within one kit |

The standoffs take the place of the four printed 5 mm spacers, and lift the Pi 5 by 1 mm, to
6 mm above the deck. They also make the Pi easier to handle:

- **Removing the Pi 5:** the standoffs stay screwed to the deck, so the nuts can't drop out of
  the traps in its underside.
- **Fitting it:** the four screws go into fixed threads. You don't have to hold loose spacers
  and nuts in line.

The printed spacers (plate 2) are the fallback: 4 × PM M2.5 × 12 down through the Pi 5 and
the spacers into nuts in the same traps, 0.7 mm past the nut.

**Nylon notes:**

- **Tightening:** turn the screws until they're snug and stop. Small nylon Phillips heads strip
  easily.
- **If a Pi screw stops short:** COMRUN gives no thread depth for the standoffs. If an M2.5 × 6
  stops before it pulls the Pi 5 down, put one of the kit's washers under its head.
- **Assembly:** [`cad/animate.py`](../../cad/animate.py) draws these parts in black, and step 4 of
  the [assembly GIF](../../renders/assembly_steps.gif) puts the standoffs in before the camera.

### How the listings were read

Amazon is better read from a home IP than from a datacenter runner, so
[`fetch/`](fetch/) runs headless Chromium on the CubOS Pi 5 (`RPI_STREAM_CAM_HOSTNAME`),
the same way the McMaster models were fetched ([`../README.md`](../README.md)):

```bash
# on the Pi, with run.sh and amz.js in ~/amz
bash run.sh B0CKBWQSNY B0BXT4FG1T     # writes out/<ASIN>.json, .html and .png
```

`run.sh` runs Chromium niced, with DevTools on loopback only, and kills it and deletes its
profile on exit. `amz.js` saves each listing's title, bullets, specs, the A+ ("From the
manufacturer") text and the image URLs. The pages loaded on the first try, with no CAPTCHA or
"Continue shopping" check. The listing images aren't committed, because they are Amazon's and
COMRUN's to publish, not ours.

Two things to know about the pages:

- **The M2, M2.5, M3 and M4 kits share one set of pictures.** The M2.5 page's main picture
  shows the M4 kit. Read the contents from the chart labelled M2.5, not from the first picture.
- **The M2.5 contents are only in a picture.** That page's A+ section has no text.
