# Real footage: a cut list for draft 5

Draft 4 of the [tutorials](README.md) cuts to the recordings only for Bartosz's explanations, and most of those show
him talking, or the touchscreen, rather than the work. This is the cut list for draft 5: after each step's 3D animation,
a few seconds of the real action from the tables below, then the explanation clip draft 4 already has. The picks go
through the clip path [`build_tutorials.py`](build_tutorials.py) already has: 720p windows fetched on the stream-cam Pi
with [`../tools/hls_sections.py`](../tools/hls_sections.py), two-pass `vidstab` zoomed in by at most 10 %, and the label
bar drawn after it.

**Built into draft 5** (2026-10-07): every first pick and the three "what goes wrong" picks, 70 in all, are `R(...)`
entries in `REAL` in [`scripts.py`](scripts.py), with a caption of at most six words each. The *(alt)* rows are not used.
A pick longer than 17 s plays its middle 14 s; the catch bowl plays 5:29–5:43, so that the bowl is in frame. See the
[README](README.md#how-each-tutorial-is-put-together).

## Reading the tables

- **Sub-steps** are the narration sentences in [`scripts.py`](scripts.py), one per sub-step of the animation (numbered
  from 0 where a step plays only part of one). The first pick of a sub-step is the one to use; *(alt)* rows are second
  choices.
- Every pick was checked against its rows in [`../timestamps.md`](../timestamps.md) (the longer windows around it are in
  [`../stitch/edl.md`](../stitch/edl.md)), the Whisper transcript, and the frames in
  [`../keyframes/`](../keyframes/README.md) or [`../runs/2026-10-06/review/`](../runs/2026-10-06/review/). In and out
  points are to the second; the build should trim on the words where there are any.
- **Stabilize**: *yes* where the camera moves with the person wearing or holding it, *light* where it rests on one view
  for the whole pick, so a smaller zoom will do. None of the recordings is on a tripod, so nothing is *no*.
- **What goes wrong** marks a pick shown as the mistake, not the method.

| Label | Recording | Camera |
| --- | --- | --- |
| T1–T9 | Training videos 1–9, Sep 29–30 | worn or held by a trainee, moving with them (T7 11:24 calls it head-mounted); T8 and T9 are portrait phone video |
| Comm. | `2wMgeI-E7zw`, the commissioning walk-around, Sep 28 (Sterling's phone) | hand-held phone |
| Brush | `Pk0K5sBz-sQ`, right after a pour, Sep 29 | hand-held |
| Cup | `TFpU4uqVF9c`, the first custom charge, Sep 30, Bartosz narrating | hand-held |
| POV | `u-KjR5TENN4`, the expert cleaning, Sep 30, no speech | body-worn, dim |
| Drill | `LSQmxwmlTkQ`, drilling a graphite nozzle, Sep 30 | hand-held |
| O2a, O2b | `qYyT39D5Yzo`, `of5-LhkX_VQ`, the first run on our own, Oct 2 | worn by the narrator, first person |
| V1–V3 | `VFycaxIq0Tc`, `dnPs56DPt6I`, `DWH1CEygsTI`, Gage's run, Oct 6 ([`../runs/2026-10-06.md`](../runs/2026-10-06.md)) | collar phone, first person |

## Tutorial 0 · The machine and how it works

**After the machine (`00_machine`).** The furnace, the chamber door, the stack and the container are left to tutorial
1's picks; the cutaway has no real counterpart.

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| The machine | V1 `VFycaxIq0Tc` | 2:30–2:50 | [V1 2:30](https://www.youtube.com/embed/VFycaxIq0Tc?start=150) | the whole machine from the front, camera at rest (chatter: mute) | light |
| Panels, touchscreen | Comm. `2wMgeI-E7zw` | 3:35–3:58 | [Comm. 3:35](https://www.youtube.com/embed/2wMgeI-E7zw?start=215) | the furnace panel and the touchscreen, what each one runs | yes |
| Utilities | Comm. `2wMgeI-E7zw` | 0:12–0:34 | [Comm. 0:12](https://www.youtube.com/embed/2wMgeI-E7zw?start=12) | the back: pump socket, exchanger port, argon tee, blue air line | yes |

**After how it makes powder (`06_pour`).** The same shots as in tutorials 1 and 2, as a preview. The argon push, the
turbo push and the powder falling into the container are not on camera.

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Coil heats crucible | Cup `TFpU4uqVF9c` | 15:57–16:20 | [Cup 15:57](https://www.youtube.com/embed/TFpU4uqVF9c?start=957) | the melt through the lid window; Bartosz on a leftover and the oxide | yes |
| Plate at 40 kHz | V2 `dnPs56DPt6I` | 16:20–16:35 | [V2 16:20](https://www.youtube.com/embed/dnPs56DPt6I?start=980) | water on the vibrating plate atomizes in straight lines (door open) | yes |
| Stream onto plate | T9 `9kn-HhXCr1o` | 20:12–20:32 | [T9 20:12](https://www.youtube.com/embed/9kn-HhXCr1o?start=1212) | through the view port: rod up, stream on the plate, first droplet lost | light |
| Droplets | T9 `9kn-HhXCr1o` | 21:02–21:11 | [T9 21:02](https://www.youtube.com/embed/9kn-HhXCr1o?start=1262) | through the view port: atomizing on the upper part of the plate | light |

**With the safety card.**

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Respirators | T5 `58wJ_Khwgyk` | 73:47–74:02 | [T5 73:47](https://www.youtube.com/embed/58wJ_Khwgyk?start=4427) | full-face respirators labelled with names at the bench | yes |

## Tutorial 1 · Before a run

### Step 1 · Utilities (`01_utilities`)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Breakers, main switch | Comm. `2wMgeI-E7zw` | 3:23–3:35 | [Comm. 3:23](https://www.youtube.com/embed/2wMgeI-E7zw?start=203) | the main switch on the blue frame: "you turn on the whole system" | yes |
| Chilled water | Comm. `2wMgeI-E7zw` | 1:04–1:18 | [Comm. 1:04](https://www.youtube.com/embed/2wMgeI-E7zw?start=64) | at the facility valves: open them "very, very little" | yes |
| Heat exchanger | Comm. `2wMgeI-E7zw` | 2:06–2:28 | [Comm. 2:06](https://www.youtube.com/embed/2wMgeI-E7zw?start=126) | the exchanger's own switch on; its pump and pressure come up | yes |
| Compressed air | O2a `qYyT39D5Yzo` | 0:44–0:58 | [O2a 0:44](https://www.youtube.com/embed/qYyT39D5Yzo?start=44) | first person at the wall: a fitting still leaking, then the air on | yes |
| Argon | V3 `DWH1CEygsTI` | 5:55–6:10 | [V3 5:55](https://www.youtube.com/embed/DWH1CEygsTI?start=355) | the argon regulator's two gauges on the wall (no speech) | yes |
| Checks | O2a `qYyT39D5Yzo` | 1:26–1:38 | [O2a 1:26](https://www.youtube.com/embed/qYyT39D5Yzo?start=86) | the startup checklist read off a phone: oil, water, argon, air | yes |
| Checks (alt) | Comm. `2wMgeI-E7zw` | 1:45–2:02 | [Comm. 1:45](https://www.youtube.com/embed/2wMgeI-E7zw?start=105) | the exchanger's tank and its level sensor | yes |

### Step 2 · The furnace (`03_furnace_load`)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Everything out | T1 `wRc8p2_FnJo` | 35:50–36:12 | [T1 35:50](https://www.youtube.com/embed/wRc8p2_FnJo?start=2150) | teardown starts with the thermocouple; its thin cover may crack | yes |
| Nozzle, holder | — | — | [T1 45:54](https://www.youtube.com/embed/wRc8p2_FnJo?start=2754) | draft 4's clip already shows it | — |
| Crucible into coil | V2 `dnPs56DPt6I` | 2:48–3:10 | [V2 2:48](https://www.youtube.com/embed/dnPs56DPt6I?start=168) | first person: the crucible lowered into the insulation (no speech) | yes |
| Nut from below | T8 `HTlUrAr5HVU` | 2:26–2:50 | [T8 2:26](https://www.youtube.com/embed/HTlUrAr5HVU?start=146) | the graphite nut started on the thread from below, through the door | yes |
| Nut from below (alt) | T8 `HTlUrAr5HVU` | 2:52–3:16 | [T8 2:52](https://www.youtube.com/embed/HTlUrAr5HVU?start=172) | tightened while the hole is turned for the thermocouple | yes |
| Insulation | T4 `1F9_4ccwhss` | 0:31–0:55 | [T4 0:31](https://www.youtube.com/embed/1F9_4ccwhss?start=31) | the insulation's hole lined up with the thermocouple port | light |
| Insulation (alt) | T4 `1F9_4ccwhss` | 0:59–1:18 | [T4 0:59](https://www.youtube.com/embed/1F9_4ccwhss?start=59) | the side insulation pressed in; it is dusty, so vacuum | light |
| Thermocouple | T8 `HTlUrAr5HVU` | 4:20–4:40 | [T8 4:20](https://www.youtube.com/embed/HTlUrAr5HVU?start=260) | the thermocouple pushed into its hole | yes |
| Thermocouple (alt) | V2 `dnPs56DPt6I` | 3:38–4:00 | [V2 3:38](https://www.youtube.com/embed/dnPs56DPt6I?start=218) | first person: the thermocouple in at the back | yes |
| Sealing rod | V2 `dnPs56DPt6I` | 4:00–4:25 | [V2 4:00](https://www.youtube.com/embed/dnPs56DPt6I?start=240) | first person: the rod in hand, then in the furnace under its lever | yes |
| Lever, pin, button | — | — | [T4 1:41](https://www.youtube.com/embed/1F9_4ccwhss?start=101) | draft 4's clip ends on it | — |
| The charge | V3 `DWH1CEygsTI` | 0:40–1:00 | [V3 0:40](https://www.youtube.com/embed/DWH1CEygsTI?start=40) | the charge wiped with IPA at the bench | yes |
| The charge (alt) | T4 `1F9_4ccwhss` | 4:31–4:50 | [T4 4:31](https://www.youtube.com/embed/1F9_4ccwhss?start=271) | "we always need to clean the feedstock"; rods stood in the crucible | yes |
| The charge (alt) | V3 `DWH1CEygsTI` | 4:28–4:50 | [V3 4:28](https://www.youtube.com/embed/DWH1CEygsTI?start=268) | first person: the charge in beside the sealing rod | yes |
| Lid, latch | T4 `1F9_4ccwhss` | 5:17–5:35 | [T4 5:17](https://www.youtube.com/embed/1F9_4ccwhss?start=317) | lid closed and latched; tighten the latch if it hisses | light |
| Lid, latch (alt) | T8 `HTlUrAr5HVU` | 9:05–9:20 | [T8 9:05](https://www.youtube.com/embed/HTlUrAr5HVU?start=545) | the latch tightened "to get a seal" | yes |

### Step 3 · The chamber (`03b_chamber`)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Splash disc | — | — | [T5 2:38](https://www.youtube.com/embed/58wJ_Khwgyk?start=158) | draft 4's clip shows it going in (2:47) | — |
| Container, clamp | T5 `58wJ_Khwgyk` | 4:46–4:58 | [T5 4:46](https://www.youtube.com/embed/58wJ_Khwgyk?start=286) | the container on the outlet, flange clamp finger-tight | yes |
| Catch bowl | T5 `58wJ_Khwgyk` | 5:21–5:43 | [T5 5:21](https://www.youtube.com/embed/58wJ_Khwgyk?start=321) | the gold-melting bowl in the chamber (in frame at 5:41) | yes |

### Step 4 · The ultrasonic stack (`02_stack`)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Transducer | T5 `58wJ_Khwgyk` | 6:37–6:58 | [T5 6:37](https://www.youtube.com/embed/58wJ_Khwgyk?start=397) | the transducer at the door: piezo stack, air, cable (runs into draft 4's 6:59 clip) | yes |
| Booster at 65 | T7 `FDRTt68Vfvo` | 37:56–38:20 | [T7 37:56](https://www.youtube.com/embed/FDRTt68Vfvo?start=2276) | 17 mm on the transducer, arrow checked, counter-held with a second wrench | yes |
| Booster at 65 (alt) | T5 `58wJ_Khwgyk` | 17:17–17:40 | [T5 17:17](https://www.youtube.com/embed/58wJ_Khwgyk?start=1037) | torque wrench pulled to the click at 65, then set to 60 | yes |
| Sonotrode at 60 | T7 `FDRTt68Vfvo` | 35:23–35:45 | [T7 35:23](https://www.youtube.com/embed/FDRTt68Vfvo?start=2123) | the prolonger sonotrode threaded on, M8 end up | yes |
| Sonotrode at 60 (alt) | T7 `FDRTt68Vfvo` | 40:06–40:25 | [T7 40:06](https://www.youtube.com/embed/FDRTt68Vfvo?start=2406) | tightened to the click (silent until "that click is how you know") | yes |
| Into the door | T5 `58wJ_Khwgyk` | 24:46–25:03 | [T5 24:46](https://www.youtube.com/embed/58wJ_Khwgyk?start=1486) | the stack pushed up into the housing, clamp over, final clamp | yes |
| Plate at 50 | T5 `58wJ_Khwgyk` | 25:55–26:15 | [T5 25:55](https://www.youtube.com/embed/58wJ_Khwgyk?start=1555) | plate on by hand, then the wrench to 50 with a counter-hold | yes |
| Plate at 50 (alt) | T7 `FDRTt68Vfvo` | 47:24–47:47 | [T7 47:24](https://www.youtube.com/embed/FDRTt68Vfvo?start=2844) | the plate wiggled fully onto the connector, then pushed home | yes |
| Plate at 50 (alt) | V2 `dnPs56DPt6I` | 15:20–15:42 | [V2 15:20](https://www.youtube.com/embed/dnPs56DPt6I?start=920) | first person: the torque wrench on the plate in the door | yes |
| Scan | V2 `dnPs56DPt6I` | 5:38–6:03 | [V2 5:38](https://www.youtube.com/embed/dnPs56DPt6I?start=338) | scan pressed on the touchscreen: "40,000 points" | yes |
| Water test | V2 `dnPs56DPt6I` | 16:20–16:35 | [V2 16:20](https://www.youtube.com/embed/dnPs56DPt6I?start=980) | water atomizes over the plate in straight lines | yes |
| Cover, cable, air | T7 `FDRTt68Vfvo` | 40:55–41:10 | [T7 40:55](https://www.youtube.com/embed/FDRTt68Vfvo?start=2455) | the cable connector locked; the stack carried by its housing | yes |
| Check, door shut | V2 `dnPs56DPt6I` | 10:02–10:15 | [V2 10:02](https://www.youtube.com/embed/dnPs56DPt6I?start=602) | the test after torquing: "40,200. Perfect" | yes |
| Bolts, star knobs | V2 `dnPs56DPt6I` | 17:20–17:45 | [V2 17:20](https://www.youtube.com/embed/dnPs56DPt6I?start=1040) | the door's star knobs tightened: "That's tight" | yes |

## Tutorial 2 · During a run

### Step 1 · Gas wash (`04_gas_wash`)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Pressure control off | T9 `9kn-HhXCr1o` | 3:04–3:25 | [T9 3:04](https://www.youtube.com/embed/9kn-HhXCr1o?start=184) | at the panels: pressure control off, then the vacuum pump | yes |
| Pressure control off (alt) | V3 `DWH1CEygsTI` | 5:17–5:32 | [V3 5:17](https://www.youtube.com/embed/DWH1CEygsTI?start=317) | first person: "pressure control, vacuum pump, gas wash" | yes |
| Furnace wash | T5 `58wJ_Khwgyk` | 33:50–34:12 | [T5 33:50](https://www.youtube.com/embed/58wJ_Khwgyk?start=2030) | vacuum pump on, gas wash pressed: five purges run by themselves | yes |
| Argon, repeat | T5 `58wJ_Khwgyk` | 37:35–37:53 | [T5 37:35](https://www.youtube.com/embed/58wJ_Khwgyk?start=2255) | the furnace display at −0.76 bar on the last cycle; melting pressure | light |
| Oxygen after fill | V3 `DWH1CEygsTI` | 20:55–21:08 | [V3 20:55](https://www.youtube.com/embed/DWH1CEygsTI?start=1255) | oxygen on the touchscreen after the argon fill: "19 parts per million" | yes |
| Chamber wash | T5 `58wJ_Khwgyk` | 38:13–38:32 | [T5 38:13](https://www.youtube.com/embed/58wJ_Khwgyk?start=2293) | furnace to overpressure, then the chamber pumped: pump on, valve open | yes |
| Generator, 250 °C | T9 `9kn-HhXCr1o` | 2:29–2:50 | [T9 2:29](https://www.youtube.com/embed/9kn-HhXCr1o?start=149) | generator start; setpoint from 800 down to 250 | yes |
| Generator, 250 °C (alt) | T9 `9kn-HhXCr1o` | 1:58–2:19 | [T9 1:58](https://www.youtube.com/embed/9kn-HhXCr1o?start=118) | heat exchanger on; waiting out the cooling-water alarm | yes |
| 500 °C | T9 `9kn-HhXCr1o` | 6:13–6:33 | [T9 6:13](https://www.youtube.com/embed/9kn-HhXCr1o?start=373) | washing at 250; at −850 mbar, set 500 | yes |
| Pressure control on | T9 `9kn-HhXCr1o` | 1:34–1:48 | [T9 1:34](https://www.youtube.com/embed/9kn-HhXCr1o?start=94) | pressure control pressed: the chamber back up to 150 mbar | yes |

### Step 2 · Heat and melt (`05_melt`)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Overshoot | T5 `58wJ_Khwgyk` | 52:50–53:06 | [T5 52:50](https://www.youtube.com/embed/58wJ_Khwgyk?start=3170) | "now we go up": well past 800 to drop the rods (hand at the panel) | yes |
| Overshoot (alt) | Cup `TFpU4uqVF9c` | 10:26–10:40 | [Cup 10:26](https://www.youtube.com/embed/TFpU4uqVF9c?start=626) | setpoint raised on the furnace panel for the cup charge | yes |
| Melt cues | V3 `DWH1CEygsTI` | 23:37–23:50 | [V3 23:37](https://www.youtube.com/embed/DWH1CEygsTI?start=1417) | through the lid window: the charge glowing in the crucible | yes |
| Melt cues (alt) | Cup `TFpU4uqVF9c` | 15:57–16:20 | [Cup 15:57](https://www.youtube.com/embed/TFpU4uqVF9c?start=957) | the pool through the window: a leftover and the oxide skin | yes |
| Setpoint down | T3 `txH397FGTAU` | 38:33–38:52 | [T3 38:33](https://www.youtube.com/embed/txH397FGTAU?start=2313) | setpoint lowered on the panel "as soon as it starts melting" | yes |
| Wait two minutes | V3 `DWH1CEygsTI` | 27:08–27:32 | [V3 27:08](https://www.youtube.com/embed/DWH1CEygsTI?start=1628) | through the lid window: the pool; "let that go for two minutes" | yes |
| Cooling, rescan | V3 `DWH1CEygsTI` | 28:30–28:53 | [V3 28:30](https://www.youtube.com/embed/DWH1CEygsTI?start=1710) | scan on the touchscreen, 40,185 Hz: "scanner is looking good" | yes |
| Cooling, rescan (alt) | T9 `9kn-HhXCr1o` | 19:35–19:53 | [T9 19:35](https://www.youtube.com/embed/9kn-HhXCr1o?start=1175) | transducer cooling on; the last scan's settings are kept | yes |

### Step 3 · The pour (`06_pour`)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| The sequence | T2 `naePD8o9_Gk` | 19:12–19:31 | [T2 19:12](https://www.youtube.com/embed/naePD8o9_Gk?start=1152) | at the touchscreen: ultrasonic start ("it vibrates"), then rod, pressure, turbo | yes |
| Vibration, ~90 % | O2b `of5-LhkX_VQ` | 25:00–25:22 | [O2b 25:00](https://www.youtube.com/embed/of5-LhkX_VQ?start=1500) | first person: amplitude set to "about 90" on an unmarked knob | yes |
| Draining pressure | — | — | — | pressed in the next pick | — |
| Rod up, first drops | T9 `9kn-HhXCr1o` | 20:12–20:32 | [T9 20:12](https://www.youtube.com/embed/9kn-HhXCr1o?start=1212) | through the view port: rod up, stream on the plate, first droplet lost | light |
| Turbo push | — | — | — | not on camera: the button is on the touchscreen, and no view-port shot catches its effect | — |
| Plate hot, steer | T9 `9kn-HhXCr1o` | 21:02–21:11 | [T9 21:02](https://www.youtube.com/embed/9kn-HhXCr1o?start=1262) | through the view port: atomizing on the upper part of the plate | light |
| Plate hot, steer | V3 `DWH1CEygsTI` | 30:33–30:48 | [V3 30:33](https://www.youtube.com/embed/DWH1CEygsTI?start=1833) | **What goes wrong:** stack too high, stream on the upper sonotrode; his hand pulls it back (mostly floor in frame) | yes |
| Plate hot, steer | V3 `DWH1CEygsTI` | 32:35–32:58 | [V3 32:35](https://www.youtube.com/embed/DWH1CEygsTI?start=1955) | **What goes wrong:** the same mistake explained at the chamber window | yes |
| Too thin, too high | T9 `9kn-HhXCr1o` | 21:11–21:20 | [T9 21:11](https://www.youtube.com/embed/9kn-HhXCr1o?start=1271) | through the view port: melt gathers at the bottom of the plate and drips | light |
| Too thin, too high | O2b `of5-LhkX_VQ` | 26:48–27:13 | [O2b 26:48](https://www.youtube.com/embed/of5-LhkX_VQ?start=1608) | **What goes wrong:** Oct 2's pressure too high: "most of it did not get atomized" (stream not in frame) | yes |
| At the window | T3 `txH397FGTAU` | 44:46–45:08 | [T3 44:46](https://www.youtube.com/embed/txH397FGTAU?start=2686) | Bartosz bent at the view port as the pour ends: "we are done" | yes |
| At the window (alt) | Cup `TFpU4uqVF9c` | 19:58–20:20 | [Cup 19:58](https://www.youtube.com/embed/TFpU4uqVF9c?start=1198) | mid-pour, a hand at the door beside the view port (no speech) | yes |
| At the window (alt) | T5 `58wJ_Khwgyk` | 29:12–29:31 | [T5 29:12](https://www.youtube.com/embed/58wJ_Khwgyk?start=1752) | how the plate holder moves: loosen, turn, twist for up and down | yes |
| Crucible empty | — | — | — | see step 4 | — |

### Step 4 · End the pour (`07_end_cooldown`, sub-steps 0–1)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Last turbo | T5 `58wJ_Khwgyk` | 62:12–62:24 | [T5 62:12](https://www.youtube.com/embed/58wJ_Khwgyk?start=3732) | at the touchscreen: turbo to clear the nozzle, then rod, pressure, generator, ultrasonics | yes |
| Stop within seconds | T9 `9kn-HhXCr1o` | 21:39–21:56 | [T9 21:39](https://www.youtube.com/embed/9kn-HhXCr1o?start=1299) | through the view port as it ends: "It's over… stop the vibrations…" | light |

## Tutorial 3 · After a run

### Step 1 · Shutdown (`07_end_cooldown`, sub-steps 0–1)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Turbo, then stop | Cup `TFpU4uqVF9c` | 20:28–20:42 | [Cup 20:28](https://www.youtube.com/embed/TFpU4uqVF9c?start=1228) | "It was fast. It was everything." Pressure, rod down, generator stopped | yes |
| Turbo, then stop (alt) | O2b `of5-LhkX_VQ` | 27:41–27:52 | [O2b 27:41](https://www.youtube.com/embed/of5-LhkX_VQ?start=1661) | first person after Oct 2's pour: rod, generator, ultrasonics, cooler | yes |

### Step 2 · Cool down and open (`07_end_cooldown`, sub-steps 2–5)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| 250 °C, wait for 400 | O2b `of5-LhkX_VQ` | 27:59–28:19 | [O2b 27:59](https://www.youtube.com/embed/of5-LhkX_VQ?start=1679) | setpoint down to 250 for next time; "we got some… a pile" | yes |
| Vent, masks | — | — | [T2 38:59](https://www.youtube.com/embed/naePD8o9_Gk?start=2339) | draft 4's clip shows the vent pressed | — |
| Door open, plate out | Brush `Pk0K5sBz-sQ` | 4:20–4:44 | [Brush 4:20](https://www.youtube.com/embed/Pk0K5sBz-sQ?start=260) | the door open with the plate on it: "the plate is okay" | yes |
| Brush down | T2 `naePD8o9_Gk` | 43:40–44:05 | [T2 43:40](https://www.youtube.com/embed/naePD8o9_Gk?start=2620) | paper under the opening; powder brushed off door and walls into the chamber | yes |
| Brush down (alt) | T4 `1F9_4ccwhss` | 8:47–9:10 | [T4 8:47](https://www.youtube.com/embed/1F9_4ccwhss?start=527) | the brush swept in a circle so the powder falls into the container | yes |

### Step 3 · Collect the powder (`07_end_cooldown`, sub-steps 6–7)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Valve, clamp, off | — | — | [T6 0:00](https://www.youtube.com/embed/tfb4fsVNIFI?start=0) | draft 4's clips show it, with [T2 53:39](https://www.youtube.com/embed/naePD8o9_Gk?start=3219) | — |
| Paper, chunks, sieve | T2 `naePD8o9_Gk` | 55:05–55:30 | [T2 55:05](https://www.youtube.com/embed/naePD8o9_Gk?start=3305) | the container on paper on the floor: valve open, powder brushed out | yes |
| Paper, chunks, sieve (alt) | V1 `VFycaxIq0Tc` | 5:58–6:18 | [V1 5:58](https://www.youtube.com/embed/VFycaxIq0Tc?start=358) | a jar of the last run's powder that "needs to be sifted" | yes |

### Step 4 · Clean and maintain (`08_clean`)

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Brush, vacuum, wipe | T4 `1F9_4ccwhss` | 6:52–7:16 | [T4 6:52](https://www.youtube.com/embed/1F9_4ccwhss?start=412) | door seal and chamber wiped with paper and alcohol; "vacuum it first" | yes |
| Brush, vacuum, wipe (alt) | POV `u-KjR5TENN4` | 6:00–6:20 | [POV 6:00](https://www.youtube.com/embed/u-KjR5TENN4?start=360) | first person: gloved hands inside the chamber, wiping (frames only, no speech) | yes |
| Plate off, scraper | — | — | — | no clear shot of a plate coming off its stud; draft 4's T7 17:51 clip covers "never clean a plate" | — |
| Sealing rod out | T1 `wRc8p2_FnJo` | 36:24–36:47 | [T1 36:24](https://www.youtube.com/embed/wRc8p2_FnJo?start=2184) | rod out after the safety pin; the top insulation lifted out | yes |
| Sealing rod out (alt) | T8 `HTlUrAr5HVU` | 6:05–6:25 | [T8 6:05](https://www.youtube.com/embed/HTlUrAr5HVU?start=365) | aluminum rubbed off the rod: "the tip needs to be good" | yes |
| Strip, nut, crucible | T1 `wRc8p2_FnJo` | 37:27–37:52 | [T1 37:27](https://www.youtube.com/embed/wRc8p2_FnJo?start=2247) | unscrew from below while holding the nut; the graphite nut and seal shown | yes |
| Nozzle | Drill `LSQmxwmlTkQ` | 0:00–0:20 | [Drill 0:00](https://www.youtube.com/embed/LSQmxwmlTkQ?start=0) | a graphite nozzle under the drill press, #70 bit (chatter: mute) | yes |
| Nozzle (alt) | O2a `qYyT39D5Yzo` | 10:08–10:28 | [O2a 10:08](https://www.youtube.com/embed/qYyT39D5Yzo?start=608) | "Check the nozzle… there's light coming through" (picture not checked) | yes |
| O-rings, HEPA | T7 `FDRTt68Vfvo` | 52:22–52:35 | [T7 52:22](https://www.youtube.com/embed/FDRTt68Vfvo?start=3142) | the O-ring seal wiped with isopropanol and paper | yes |
| O-rings, HEPA (alt) | T1 `wRc8p2_FnJo` | 8:33–8:50 | [T1 8:33](https://www.youtube.com/embed/wRc8p2_FnJo?start=513) | the HEPA unit: its two disconnect points and cover, pointed out | yes |

**With the closing card (lessons from Oct 2).**

| Sub-step | Source | In–out | Link | Shows | Stabilize |
| --- | --- | --- | --- | --- | --- |
| Label the plates | O2a `qYyT39D5Yzo` | 2:26–2:50 | [O2a 2:26](https://www.youtube.com/embed/qYyT39D5Yzo?start=146) | Oct 2: the plates on the bench, and nobody can tell which is which | yes |
| Pressure, plate, notes | O2b `of5-LhkX_VQ` | 27:24–27:40 | [O2b 27:24](https://www.youtube.com/embed/of5-LhkX_VQ?start=1644) | after Oct 2's pour: "definitely too high… plate a lot closer", noted on a phone | yes |

## Totals and gaps

| Tutorial | First picks | What goes wrong | Alternatives |
| --- | --- | --- | --- |
| 0 · The machine and how it works | 8, 2:27 | — | — |
| 1 · Before a run | 26, 8:15 | — | 11, 3:45 |
| 2 · During a run | 21, 6:13 | 3, 1:03 | 7, 2:12 |
| 3 · After a run | 12, 4:13 | — | 7, 2:11 |

- The first picks and the three mistakes add about 22 minutes to the four tutorials' 30:33 (22:11, before the 0.4 s
  crossfades). Cut to their central 10 s each, they would add about 12.
- The pour itself is in frame only in T9, the phone held to the view port from 20:12 to 21:56, a reverse-booster pour
  that partly dripped. The other pours were filmed from the panels, from behind the operator or at the floor (T2, T3,
  T5, Oct 2, Oct 6); the T5 frame at 59:51 is black. The cup charge's pour (Cup 19:58) was filmed at the door and may
  show the stream at 720p.
- Not on camera: the effect of a turbo push, and a plate coming off its stud.
- To build: one `hls_sections.py` job per pick (`video_id`, `start`, `end`, `name` = `<id>_<start>`), padded a few
  seconds either side, run on the Pi as in [`../stitch/README.md`](../stitch/README.md). Picks without useful speech
  need exact in and out points rather than [`clip_words.py`](clip_words.py)'s sentence snapping, which falls back to
  the nearest word, and their chatter muted. `SHORT` in `build_tutorials.py` has no labels yet for V1–V3 and the drill
  clip, so their label bar would fall back to the title in [`../videos.json`](../videos.json).
