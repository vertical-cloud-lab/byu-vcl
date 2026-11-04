# The polisher, refined against the lab's SOP videos (#303, PR #318)

Sterling asked for the polishing clip to follow the lab's SOP videos, and for the models to be registered to real
frames. Those videos show the polisher is not the Buehler EcoMet 30 the model was. It is a **LECO PX500**, with
"PX500" printed above the touchscreen. Next to it on the bench is a manual LECO PX300.

## Sources

The lab's own videos, on the BYU Vertical Cloud Lab channel:

| Video | What it shows |
|---|---|
| [Alumina polish part 1](https://www.youtube.com/watch?v=JmXvH10X9sI) (14:47) | A new white cloth onto the platen (0:04–0:34); the screen reading head 75 rpm, force 5, platen 150 rpm, 0:30 ([1:14](https://youtu.be/JmXvH10X9sI?t=74)); the head and spigot from the left ([1:34](https://youtu.be/JmXvH10X9sI?t=94)) |
| [Alumina polish part 2](https://www.youtube.com/watch?v=nfnl0aPJPZc) (57:07) | The whole machine from the front ([3:00](https://youtu.be/nfnl0aPJPZc?t=180)) and front right ([3:39](https://youtu.be/nfnl0aPJPZc?t=219)); the screen reading 35 / 3 / 150 and 3:00; alumina squeezed from a bottle onto the cloth ([5:48](https://youtu.be/nfnl0aPJPZc?t=348)); polishing with the head down, seen from the left ([6:28](https://youtu.be/nfnl0aPJPZc?t=388)) |
| [Alumina polish part 3](https://www.youtube.com/watch?v=eLrJxxBAcnE) (17:10) | Polishing with the head down from the front; alumina squeezed onto the cloth (1:39–2:28); rinsing the mounts at the sink, then ethanol and drying (3:47–7:45) |
| [320-1200 Polishing + Alumina on pad](https://www.youtube.com/watch?v=Vf_VRmOZlMY) (25:37) | SiC papers from LECO boxes; the screen at head 35 rpm, force 30, platen 150 rpm, 0:30 per grit ([5:37](https://youtu.be/Vf_VRmOZlMY?t=337)); the 6-position holder ([2:28](https://youtu.be/Vf_VRmOZlMY?t=148)); a maroon Bakelite mount ([4:27](https://youtu.be/Vf_VRmOZlMY?t=267)) |
| [Making Bakelite Polishing Puck](https://www.youtube.com/watch?v=9m_hdgmu2Jw) (7:09) | The mounts |

LECO's [PX400/PX500 brochure](https://www.leco.com/wp-content/uploads/documents/brochures/209-254-PX-series.pdf)
(form 209-254, 2020) gives the features:
- wheels up to 12 in (300 mm);
- a motorized head for fixed and individual holders;
- up to five metered dispensers and a 5-position bottle holder;
- a 7 in multi-touch screen with the emergency stop under it;
- a spiral bowl with automatic bowl wash;
- a detachable water spigot;
- an LED work light.

LECO publishes no dimensions. 533 W × 711 D × 635 H mm (21 × 28 × 25 in) is a reseller's figure for the PX400/PX500
series (IndiaMART). The brochure came through the Pi, because leco.com sits behind Cloudflare and refuses the runner.

## The fit

[`register.py`](../register.py) fits the model to two frames of part 2, 3:00 and 3:39, which share one lens. The fit
uses about 40 picks: the screen's four corners, the e-stop, the deck's front-right corner, and the platen, lip and
head outlines. Depth is fixed at 711 mm. The 7 in screen (155 × 87 mm active) sets the scale; the 12 in platen
(305 mm) is fixed.

| | Before (first guess) | Fitted |
|---|---|---|
| Width without the bottle holder | 600 | 558 |
| Deck height | 300 | 312 |
| Drum radius (round front left) | 205 | 226 |
| Head housing W × H | 350 × 285 | 281 × 253 |
| Housing underside above the deck, head up | 175 | 112 |
| Overall height, head up | 760 | 677 |

| View | RMS before the fit | RMS fitted | Focal length (shared) |
|---|---|---|---|
| Front, 3:00 | 24.6 px | 8.6 px | 1108 px |
| Front right, 3:39 | 30.6 px | 4.5 px | 1108 px |
| **Check, held out of the fit:** part 3, 0:00, head down, another phone | 22.9 px (starting model) | 11.8 px (camera fitted to the fitted model) | 1021 px |

The held-out frame tests the fitted model on a view it never saw: a different video and phone, close up, with the
head down. Its worst picks are on the platen's right edge, where glare from the work light blurs the cloth's edge
(20–27 px). The housing's right edge was not picked there: the spigot's hose runs down over it.

- **The platen size was checked by freeing it.** The fit settled at 323 mm. That is the 12 in (305 mm) wheel, not
  the 10 in (254 mm).
- **Three picks were dropped:**
  - the block's bottom-right corner in the front view, which may have been a foot;
  - the housing's front-bottom edge, which its dark skirt hides;
  - one point on the lip's front, which was more likely the drum's top edge.
- **Overall height, 677 mm with the head up:** 6 % over the reseller's 635 and under the tray's 727.5. The polisher
  still fits tray F.

## What changed in the clip

The old clip only lowered a head onto a cloth. The new one follows the SOP:
1. A 320-grit SiC paper goes on the platen.
2. The head comes down with water on, at the SOP's grinding settings from the screen: head 35 rpm, force 30,
   platen 150 rpm, 30 s.
3. The head lifts, and the 400, 600, 800 and 1200 papers follow.
4. A white cloth goes on.
5. The head comes down again with alumina, at force 3–5, 150 rpm, 3 min. In the SOP the alumina is squeezed from a
   bottle by hand. Here it comes from one of the PX500's own dispensers, since that is how it would run unattended.
6. The mounts are rinsed and dried, as in part 3.

The camera moves in on the holder for both head-down steps.

## Still uncertain

- **Units of the force setting.** The screen shows 30 and 3–5 but not the unit.
- **Head travel.** The 87 mm drop is set by the mounts reaching the paper, not measured.
- **The holder.** Part 2 at 6:28 shows an individual-force holder with pistons. Other frames show the 6-position
  fixed holder, which is what is modelled.
- **Not modelled:** the logo, the vents and the bowl's spiral.
- **Power rating.** LECO publishes none, so `services.py` uses the EcoMet 30's 740 W, marked as an estimate.
