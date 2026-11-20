# The real footage and photos in the long-form, and their credits

Round 13, run D (Sterling's notes on round 12's public video, PR #318, 2026-11-20). The excerpts live in
[`out/footage/`](../out/footage/), each with its source in [`out/footage/manifest.json`](../out/footage/manifest.json).
Chapter 2 cuts them in at its slots (`alloy_atomize.py`, `PLAN`, then `python3 alloy_atomize.py splice`); chapter 3
and the long-form's opening use the rest.

## What changed

| Video time (round 12) | What was there | Now | Why |
|---|---|---|---|
| 20:05, chapter 2's pour | `mst2026_stream.mp4`: a melt stream breaking up on the plate, cut from Sterling's MS&T 2026 talk ([YmvaeqOQAU4](https://youtu.be/YmvaeqOQAU4?t=298)) and badged as from his talk | **Out.** The pour beat is the lab's own Oct 27 bronze jet on the W-coated carbon-fibre plate, `nab_pour1.mp4` ([2brsz-90seg](https://youtu.be/2brsz-90seg), DAL #219), which already followed it | Sterling: "that's not my video. That's from AMAZEMET." The clip in the talk is AMAZEMET's footage, so the badge credited the wrong source, and the lab has its own equivalent |
| 20:26, chapter 2's powder | `al4047_oct22_c3k0n5_bag_and_jar.jpg`: a phone photo of a screen, a bag with a lump of splats beside a jar of lumps (c3k0n5, DAL #159) | `al_4yghtr_oct06_jar.jpg`: a jar of the lab's own atomized aluminium, lot 4yghtr, cropped from Ronnie Guymon's photo in [DAL #159](https://github.com/vertical-cloud-lab/digital-alloy-lab/issues/159#issuecomment-6353392867) | Sterling: "that's aluminum slag/scrap. You should be able to find a better jar photo for the Al atomizer runs." |

## Choosing the jar photo

Every photo of an aluminium run in DAL #157 and #159 was looked at:

| Lot, run | Photo | Verdict |
|---|---|---|
| jz31op, training days | the leftover metal from the chamber's crucible | slag |
| 8rthq2, last training run | a bag with one lump (the stream ran too fast and dripped) | slag |
| u23y78, Oct 2 | a bag of flakes and splats | slag |
| 4yghtr, Oct 6 run 1 | a bag of splats **and, beside it, a labelled jar of fine grey powder** | **used, cropped to the jar** |
| kj0461, Oct 8 | the plate and drips; "no atomization really happened" | no jar |
| k7m2qx, Oct 21 | a crucible of splats, a jar lying on its side behind it | jar out of focus |
| c3k0n5, Oct 22 | inside the collection funnel, dusted with powder; and the bag-and-jar photo above | no clear jar |

4yghtr's jar is clear glass with a black cap, the powder fine and grey with a few coarse drops, the label readable.
Its SEM images are in DAL #157 (Oct 29): particles in groups of about 40-60 µm and 90-110 µm, a few over 150 µm.
The run was a poor one (the upper sonotrode was in the nozzle's way for most of it; DAL #159, Oct 6), so the caption
says the splats went in a bag of their own rather than implying the jar is the whole yield. Its log says "180g of Al
6067"; the lab's rods then were 6063, so the caption says only "Al rod".

**Better, when it exists:** a photo of a jar from a good Al run (Al 4047 at 0.19 bar on the Mo plate, like c3k0n5),
taken straight on. Any later run's jar photo can replace this one: put it in `out/footage/` at 1600 px, add its entry
to the manifest, change the `powder` beat in `alloy_atomize.PLAN`, and run `python3 alloy_atomize.py splice`.

## For the chapter-2 re-render

`splice()` reads `out/footage/manifest.json` and skips any `PLAN` entry whose file isn't there, so a render started
before this change still leaves the AMAZEMET clip and the slag photo out once this commit is pulled. If chapter 2's raw
render (`out/clean/alloy_atomize.*`, git-ignored) is on hand, `python3 alloy_atomize.py splice` re-cuts the footage in
without re-rendering.
