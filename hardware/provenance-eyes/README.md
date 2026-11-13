# Provenance Eyes: a Raspberry Pi head camera

A head-worn recorder that sees what the wearer sees and hears what they hear. One button starts a
recording; pressing it again stops it, and the clip goes to YouTube on its own. The transcript, an
analysis of the video and its conclusions then land on GitHub. Asked for by @gage-erickson on
[#342](https://github.com/vertical-cloud-lab/byu-vcl/issues/342), as a replacement for the chest
camera. The first part of that issue, a survey of commercial smart glasses, is
[`docs/provenance-eyes.md`](../../docs/provenance-eyes.md). Its closest off-the-shelf match to
this build is Mentra Live ($449), though, like all glasses, it can't be worn with a full-face
respirator ([`PPE.md`](PPE.md)).

**Status: designed, not built.** The model below is a concept: parts are placed at their real
sizes and weights, but the printed enclosures are envelopes, not print-ready parts. Nothing has
been bought, printed, wired or worn. Prices were checked on 2026-11-12.

**v2 (2026-11-13): worn like a cap, so it fits over a full-face respirator.** Sterling pointed out
that people sometimes wear full-face respirators and take lab coats on and off. The first layout
(v1) ran its band across the forehead, which is where a full-face facepiece seals. v2 uses the
same parts at the same cost, but the band sits at the hairline, so the headset goes on over the
respirator's straps and never touches the facepiece. Nothing hangs below the back of the head
and nothing is cabled to the body, so lab coats go on and off freely. The checks, the wearing
order and the commercial options under both conditions are in [`PPE.md`](PPE.md).

| | |
| --- | --- |
| ![Front left](img/headset-front-left.png) | ![Rear right](img/headset-rear-right.png) |
| **Front.** The camera head (Camera Module 3 Wide) hinges off the Pi enclosure at the hairline and looks 30° down, at the hands. The red LED shows when it is recording. | **Back.** The battery pod rides high on the back of the head, above the ratchet knob, as the counterweight. |
| ![X-ray front](img/headset-xray-front.png) | ![X-ray rear](img/headset-xray-rear.png) |
| **Inside the front.** Pi Zero 2 W with its heatsink under the vents, camera board in the head. Right temple: the record button (orange), a mic and a vibration motor. | **Inside the back.** PiSugar 3 board and its 1200 mAh cell, in a pod curved to the head. |
| ![Over a full-face respirator](img/respirator-front-left.png) | ![The camera's view](img/camera-view.png) |
| **With a full-face respirator.** The band rides above the facepiece and over its straps (generic respirator, not a specific model). | **What the camera sees** at a bench, head bowed 25°, respirator on: no part of the respirator is in frame. |

The model is [`cad/build_headset.py`](cad/build_headset.py) (Blender, run headless). The whole
device without the head is [`stl/headset-assembly.stl`](stl/headset-assembly.stl), which GitHub
shows in a 3D viewer you can turn.

## The layout: a headlamp worn like a cap

The device is laid out like a headlamp with its battery at the back (Petzl's NAO RL is 145 g, with
an 80 g battery behind the head
([retailer](https://www.bergzeit.co.uk/p/petzl-r1-battery-nao-rl-headlamp/5049366))). In v2 the
band is tilted like the band of a cap: high at the front, low at the back, where it hooks under
the bulge of the back of the head.

| Where | What | Why there |
| --- | --- | --- |
| Front, at the hairline | Pi Zero 2 W, and a hinged camera head with a Camera Module 3 Wide and a red recording LED | Above the top edge of a full-face facepiece, so the same headset works with and without one. The camera sits about 9 cm above the eyes and 3 cm in front of them; tilted 30° down, it frames hands on a bench. A Pi beside the camera needs only a short camera cable, so no 50 cm ribbon runs round the head. |
| Sides, above and in front of the ears | One I2S MEMS microphone each side, wired as a stereo pair. The right pod also has the **record button** and a coin vibration motor. | The mics are about 15 cm apart near the ears, so the recording hears roughly what the wearer hears, in stereo. A full-face respirator leaves the ears uncovered, so that holds with one on. The button is where a gloved hand finds it without looking. The motor buzzes to confirm start, stop and bookmarks, since the wearer can't see the LED. |
| Back of the head, high | PiSugar 3: a 1200 mAh LiPo, its charger, a real-time clock and a USB-C charge port, in a pod curved to the head | It is the heaviest part and the counterweight to the front. It stands 10 mm off the head so it can ride over a respirator's harness pad, and it is about 11 cm above a lab coat's collar. The clock keeps timestamps right when there is no Wi-Fi. |
| Along the band | One 4-wire cable round the left side (5 V, ground and I2C), and short mic and button runs from the temples to the front | Cable clips hold the runs to the band. Nothing runs off the head, so there is nothing to thread through a lab coat. |

### Balance

Weights and positions come from [`cad/layout.py`](cad/layout.py). The renders use the same file,
and [`cad/mass_budget.py`](cad/mass_budget.py) prints the full table. The centre of mass is
measured from the **ear line**, the line through both ear canals (the tragion).

| Build (v2) | Add-on parts | Their centre of mass | With the headgear |
| --- | ---: | --- | --- |
| **PiSugar 3, 1200 mAh (default)** | **108 g** | **0.7 cm behind the ear line**, centred left to right | 254 g, 2.0 cm behind |
| Larger 3000 mAh cell | 140 g | 2.8 cm behind | 284 g, 2.9 cm behind |
| Battery in a pocket, cable down the neck (not with lab coats) | 66 g | 5.2 cm in front (no counterweight) | 212 g, 0.4 cm behind |

v1, with the band across the forehead, had the same 108 g with its centre of mass 0.4 cm *in
front* of the ear line. Moving the band up to the hairline also moved the front pod up and back.

![Side view with the centre of mass](img/headset-side-balance.png)

*Side view. Grey line: the ear line. Magenta: the add-on parts' centre of mass. Purple: with the
headgear. Both are drawn just outside the head, as projections.*

- **Why this is the target.** Ito et al. tested VR headsets of 470–670 g and found that "if the
  COM lies within 2 cm in front of the tragion notch, the physical load remains almost constant",
  whatever the weight. From 2 to 4 cm in front, the load climbs fast
  ([Applied Sciences 11:6802, 2021](https://doi.org/10.3390/app11156802)). The default build's
  add-on parts sit 0.7 cm behind the ear line, so the front is never the heavy end. A slightly
  rear-heavy headset rests on the ratchet cradle under the back of the head. With a full-face
  respirator on, the facepiece and filters add their own weight in front of the face, and the
  headset offsets a little of it.
- **Left to right**, the right temple pod is 3.5 g heavier, because it carries the button and
  motor. The power cable runs down the left side to even that out.
- **The headgear's own centre of mass is a guess.** The table splits its 145 g as 80 g band, 20 g
  crown strap and 45 g ratchet, which puts its centre of mass behind the ear line. A front-heavy
  headgear such as the 3M H8A would bring the total forward. Weigh the real one.
- **This much mass barely loads the neck.** 254 g on a 4.5 kg head moves the combined centre of
  mass by under 0.1 cm. Balance matters most for keeping the band from rotating and slipping, and
  the crown strap carries the vertical load.
- **Battery trade-off.** The 1200 mAh cell gives roughly 2 h of recording (4.4 Wh at about 2 W;
  measure it). A 3000 mAh cell gives about 2.5 times that, but pulls the centre of mass 2 cm
  further back. For a full day, swap in a second charged headset or battery pod rather than
  using a pocket power bank: its cable would run from the head to under the lab coat, and
  would have to be unplugged or rethreaded every time the coat goes on or off.

## The headband

Build on **ratchet suspension headgear**, the kind sold as a replacement for face shields and
welding helmets. It adjusts with a knob, has a crown strap to carry weight, is made to be worn for
whole shifts, and costs under $35. Elastic straps hold by squeezing, which gets uncomfortable over
hours, and pods on them creep.

| Headband | Price (2026-11-12) | Weight | Notes |
| --- | --- | --- | --- |
| **[3M H8A ratchet headgear](https://argo.webstaurantstore.com/3m-82501-00000-h8a-blue-thermoplastic-ratchet-headgear/39982501.html)** (82501-00000) **(pick)** | $18.49 (WebstaurantStore) | not published | Ratchet and a "five position crown strap" ([datasheet](https://media.digikey.com/pdf/Data%20Sheets/3M%20PDFs/82501-00000_Ds.pdf)). The rigid front piece has face-shield attachment points, a stiff place to mount the front pod. Cheap enough to buy two for fitting. Bulky at the front. |
| [Jackson Safety 370 ratchet headgear](https://www.dillonsupply.com/Product/05820696) (20696), runner-up | $32.85 (Dillon Supply) | about 145 g (reseller) | Ratchet, crown strap, and a pivoting rear cradle that resists creep. Lower profile, but the front pod needs its own printed bracket, and the side pivot hubs may sit where the mic pods go. |
| [Lincoln Electric KP4100-1](https://weldingmart.com/products/lincoln-electric-ratchet-style-headgear-w-sweatband-kp4100-1) | $33.88 (WeldingMart) | not found | Ratchet headgear with a sweatband, much like the 370. |
| [GoPro Head Strap 2.0](https://www.bestbuy.com/site/6545389.p) (ACHOM-002), soft option | $26.99 (Best Buy) | 97–135 g (listings disagree) | Elastic, with a top strap. Light and easy to clip onto, but pods can creep and rotate. |

The render shows a generic ratchet headgear of this type, not any one product. Weigh the one you
buy and update `HEADGEAR_G` in `layout.py`.

## Cost

About **$177 for the default build**: about $141 of electronics, $18.49 for the headgear, and
about $17.50 for screws, wire and filament.
The line items, links and options are in [`BOM.md`](BOM.md).
Running costs are close to nothing: YouTube uploads are free, transcription runs on a GitHub
runner, and the Claude analysis uses the lab's existing Claude Code token.

## Software

Press → record → stop → YouTube → transcript, analysis and conclusions on GitHub. The build-out
path, in six phases with the commands for each, is in [`SOFTWARE.md`](SOFTWARE.md). In short:

1. **On the headset:** a `systemd` service watches the button and runs `rpicam-vid` with the
   stereo mics, using the Zero 2 W's hardware H.264 encoder. It writes a crash-safe MKV and a JSON
   sidecar with UTC times, bookmarks and logs.
2. **When the clip ends:** the headset uploads it to YouTube with the lab's upload-only token
   ([`youtube/yt_service.py`](../../youtube/yt_service.py)). It then sends the audio and keyframes,
   a few MB, to a private GitHub repo as a release.
3. **On GitHub Actions:** faster-whisper transcribes the audio and Claude writes the analysis and
   conclusions from the transcript and frames. The workflow commits all of it, with timestamped
   YouTube links, and comments on any issue the wearer names.

## Files

| Path | What |
| --- | --- |
| [`PPE.md`](PPE.md) | Full-face respirators and lab coats: what they rule out, the v2 checks, how to wear it |
| [`cad/layout.py`](cad/layout.py) | Head form, band geometry, pod positions and part masses (plain Python); `use("v1")` or `use("v2")` |
| [`cad/build_headset.py`](cad/build_headset.py) | Builds the scene in Blender, with a generic full-face respirator, lab coat and bench for context; renders `img/`, exports `stl/` |
| [`cad/respirator_check.md`](cad/respirator_check.md) | Written by the build: gaps to the facepiece and the coat collar, and how much of the camera's view the respirator blocks |
| [`cad/mass_budget.py`](cad/mass_budget.py) | Mass table and centre of mass for each battery option |
| [`img/`](img) | The renders |
| [`stl/headset-assembly.stl`](stl/headset-assembly.stl) | Device without the head, in mm, for viewing (not a print file) |
| [`BOM.md`](BOM.md) | Parts, prices, links |
| [`SOFTWARE.md`](SOFTWARE.md) | Software build-out path |

To regenerate (Blender 5.0, about 10 minutes on 4 cores; `--quick` for low-resolution test renders):

```bash
cd hardware/provenance-eyes/cad
blender -b --factory-startup -P build_headset.py --              # v2: all views, STL, respirator_check.md
blender -b --factory-startup -P build_headset.py -- --layout v1  # the v1 conflict view
python3 mass_budget.py                                            # balance tables (v2)
```

## Still to check

- **With a full-face respirator:** fit testing with the headset on, the lab's own respirator
  models, speech through the facepiece, and EHS sign-off. See [`PPE.md`](PPE.md#still-to-check).
- **Weights we estimated:** the PiSugar 3 and its cell, the printed pods and the headgear. None of
  them is published.
- **Heat:** the Zero 2 W sits at the hairline and dissipates about 2 W while encoding, roughly a
  headlamp's worth. Check the enclosure's temperature against the skin during a 30-minute
  recording, and move the Pi to the back if it is uncomfortable. A respirator adds its own heat,
  so test with one on as well.
- **The band at the hairline.** Ratchet headgear is made to sit across the forehead. Check on a
  real head that v2 stays at the hairline through a shift, with the crown strap shortened; if it
  creeps, see the fallbacks in [`PPE.md`](PPE.md#what-that-leaves-for-a-head-camera).
- **Separating the PiSugar 3 from the Pi.** It normally mounts under the Pi on pogo pins. Here
  it powers the Pi over a cable (5 V and ground, with I2C for the clock, the battery gauge and its
  button). Confirm the board supports this, and a larger cell, before relying on either.
- **Privacy.** The headset records people as well as procedures. Keep the LED visible, upload as
  unlisted or private, keep transcripts in a private repo (this one is public), and ask BYU's IRB
  before using recordings as research data about people.
