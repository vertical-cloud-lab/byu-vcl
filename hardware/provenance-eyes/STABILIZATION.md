# Head-camera jitter

Sterling, on [#342](https://github.com/vertical-cloud-lab/byu-vcl/issues/342) (2026-11-13):
"there's a lot more movement / jitter with a head camera (e.g., in context of training
material), but that it's obviously more faithful to what the user experiences." This page is
about what to do with that, for the Pi headset in this folder and for the commercial devices in
[`docs/provenance-eyes.md`](../../docs/provenance-eyes.md).

**Status: researched, not tried on a head.** The two ffmpeg commands below were run on a
synthetic shaky clip on 2026-11-28, only to check that they work. Nothing else here has run.
Sources were read on 2026-11-28.

## Short version

- **Keep two files, not one.** The shaky original stays the record: the hash covers it, and its
  motion shows where the wearer looked. People watch a **steadied copy**. Stabilizing crops and
  warps every frame, so the copy is derived from the record and never replaces it.
- **The steadied copy is closer to what the wearer saw.** Their eyes turned against each head
  movement to hold the picture still, so the room didn't shake for them. The camera can't do
  that. Stabilizing removes the shake and keeps the deliberate turns of the head.
- **For the Pi build, add a gyro.** A $12–20 IMU breakout in the camera head (Adafruit's
  LSM6DSOX weighs 1.7 g) lets [Gyroflow](https://github.com/gyroflow/gyroflow) steady the copy
  from the head's measured rotation, if the gyro is logged with every recording. That also fixes the
  rolling-shutter wobble that picture-only methods handle poorly. Without a gyro, ffmpeg's
  vid.stab works from the picture alone, and it is already in Ubuntu's and Debian's ffmpeg.
- **For training videos, film a steady second angle.** A chest camera (the pendant or a harness
  from [#290's page](../../docs/wearable-camera-mounts.md)) or a fixed camera at the bench gives
  the steady main shot. Cut to the head camera's steadied view where what the person looked at
  matters. A single action camera that stabilizes itself also works: on respirator days, that
  is the helmet GoPro in [`PPE.md`](PPE.md).
- **Capture settings help too:** a locked hinge, a short exposure so turns don't smear the
  frames, and a wide enough view to crop into.

## Why a head camera shakes more

- **It turns with every glance.** At a bench the head keeps moving between the hands, a label,
  a screen and the person next to you, and the camera turns with it each time. A chest camera
  turns only when the body does.
- **Small turns move the picture a lot.** At 1080p with the Camera Module 3 Wide (102° across),
  a 1° turn moves the middle of the picture by about 14 pixels, and a 5° glance by about 70.
  (That is 960 / tan 51° ≈ 777 px of focal length, times the tangent of the angle.)
- **The wearer doesn't see it.** "Visual acuity and motion perception are degraded during head
  movements unless the eyes counter-rotate so as to stabilize the line of sight and the retinal
  image" ([King and Shanidze 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC4049289/)). The
  vestibulo-ocular reflex plays a large part in that, along with eye movements that anticipate
  the head's. Watching the footage later, nothing cancels the motion, so it looks shakier than it
  felt.
- **Phones stabilize; the Pi doesn't.** Most phones and action cameras steady their video in
  the camera. The Pi's camera software doesn't: rpicam-apps' post-processing stages cover HDR,
  motion detection, object detection and similar, but nothing steadies the picture. So the Pi
  headset's raw footage will look shakier than a phone's, even from the same spot.
- **Rolling shutter.** The Camera Module 3 reads its rows top to bottom, so during a fast turn,
  upright lines lean and the picture wobbles. Methods that only look at the picture handle this
  poorly. Gyroflow corrects it from the gyro, given the sensor's readout time.

## At capture (the Pi build)

| What | Why | How |
| --- | --- | --- |
| Lock the camera hinge | A hinge that can move adds its own wobble to the head's | A friction hinge with a set screw or detent, set before recording and left alone during it |
| Ratchet headgear, not elastic | An elastic band lets the front pod bounce | Already the design ([README](README.md#the-headband)) |
| Short exposure | During a turn, a long exposure smears each frame. Stabilizing can't remove the smear, and in the steadied copy the frames go soft and sharp again. | `rpicam-vid --shutter` sets the exposure time in microseconds ([docs](https://www.raspberrypi.com/documentation/computers/camera_software.html)). Try `--shutter 8000` (1/125 s) and shorter in phase 0, and check the noise under the lab's lights. |
| Room to crop | Stabilizing crops the frame to hide the moving edges | The Wide's 102° leaves room. Record the full view and let the steadied copy crop it. |
| Log a gyro | Lets Gyroflow use the head's measured rotation | An IMU in the camera head, so it turns with the camera ("Mount the logger rigidly to the camera, ideally facing the same direction", [Gyroflow](https://docs.gyroflow.xyz/app/advanced-usage/using-external-gyro-source)). See [below](#from-a-gyro-gyroflow). |

## Making the steadied copy

Make it **off the headset**, on whatever lab machine archives the original (step 5 of
[`SOFTWARE.md` phase 2](SOFTWARE.md#phase-2-upload-when-the-clip-ends)). The Zero 2 W is busy
encoding, and it runs on battery. A GitHub runner could do it with vid.stab, but only if the
headset uploads the whole file: a 30-minute clip at 8 Mb/s is about 1.8 GB, under GitHub's
limit of 2 GiB per release file
([GitHub](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)),
but not by much.

### From the picture alone: ffmpeg's vid.stab

Two passes. The first measures the motion, and the second steadies and crops:

```bash
ffmpeg -i rec.mkv -vf vidstabdetect=shakiness=8:accuracy=15:result=rec.trf -f null -
ffmpeg -i rec.mkv -vf "vidstabtransform=input=rec.trf:smoothing=15,unsharp=5:5:0.8:3:3:0.4" \
  -c:v libx264 -crf 20 -preset veryfast -c:a copy rec-steady.mp4
```

- **`smoothing`** is how many frames on each side are averaged into the camera's path. 15 means
  31 frames, about 1 s at 30 fps; the default is 10, which means 21
  ([ffmpeg](https://ffmpeg.org/ffmpeg-filters.html#vidstabtransform)). A higher value is
  steadier, but deliberate turns lag behind.
- **`unsharp`** after the transform is what ffmpeg's docs call "always recommended".
- **Where it runs.** The filters need ffmpeg built with `--enable-libvidstab`. Ubuntu's is (ffmpeg
  8.0.1 on a GitHub runner, checked 2026-11-28), and so is Debian 13's: its `libavfilter10`
  depends on `libvidstab1.1` ([Debian](https://packages.debian.org/trixie/libavfilter10)).
  Raspberry Pi OS's own build wasn't checked.
- **Its weak spot.** It infers the camera's motion from the picture, so large hands moving close
  to the lens can be taken for camera motion. A gyro doesn't have that problem. ffmpeg's simpler
  `deshake` filter only fixes "small changes in horizontal and/or vertical shift".

### From a gyro: Gyroflow

[Gyroflow](https://github.com/gyroflow/gyroflow) is open source ("GPLv3 License with App Store
Exception"; the binary also links one closed-source library) and runs on Linux, Windows and
macOS. It steadies a video using motion logged alongside it.

- **The log.** Gyroflow reads its own CSV format,
  [GCSV](https://docs.gyroflow.xyz/app/technical-details/gcsv-format), and finds `rec.gcsv`
  next to `rec.mp4` by itself. The recorder writes a header and then one row per IMU sample:

  ```
  GYROFLOW IMU LOG
  version,1.3
  id,provenance-eyes
  orientation,<how the IMU's axes map to the camera's>
  frame_readout_time,<ms, once measured>
  tscale,0.000001
  gscale,<rad/s per raw count>
  ascale,<g per raw count>
  t,gx,gy,gz,ax,ay,az
  ```

  `tscale` times `t` gives seconds, here with `t` in microseconds. The spec asks for timestamps to
  1 ms or better. Take `gscale` and `ascale` from the IMU's datasheet for the ranges you set.
  The accelerometer columns are optional, but "Acceleration data is required for horizon lock".
- **Lining the log up with the video.** Gyroflow syncs them itself by optical flow: "When using
  external gyro data, the offset can be arbitrary"
  ([sync](https://docs.gyroflow.xyz/app/getting-started/basic-usage/synchronization)). So start
  the gyro log just before the camera. Still stamp the IMU samples from the same clock the
  camera uses, as the spec recommends, to prevent drift. Also save the frame times with
  `rpicam-vid --save-pts rec.pts`, which writes each frame's time in milliseconds from the
  first frame. They show any dropped frames.
- **A lens profile.** "Lens profile is very important as it's the base for the stabilization
  algorithm" ([Gyroflow](https://docs.gyroflow.xyz/app/getting-started/basic-usage)). Its
  [database](https://github.com/gyroflow/lens_profiles) has a community profile for a Camera
  Module 3 at 1080p. Its focal length works out to about 68° across, which is the standard
  module, not the Wide, so make our own. The calibrator wants about a minute of video of a
  chessboard on a flat monitor
  ([calibration](https://docs.gyroflow.xyz/app/getting-started/lens-calibration)).
- **Rolling shutter.** Gyroflow needs the "Frame readout time"
  ([stabilization](https://docs.gyroflow.xyz/app/getting-started/basic-usage/stabilization)),
  which isn't published for the IMX708. Raspberry Pi lists a 2304 × 1296 mode at up to 56 fps for
  both Camera Module 3 versions ([docs](https://www.raspberrypi.com/documentation/accessories/camera.html)),
  so a frame in that mode can't take longer than about 18 ms (1/56 s) to read out. Gyroflow's
  most accurate way to measure it films an LED that an Arduino blinks at a known rate
  ([rollingshutter](https://github.com/gyroflow/rollingshutter)).
- **Automation.** Gyroflow has a command line "for usage in scripts and automating workflows",
  for example `gyroflow rec.mp4 --preset headset.gyroflow`, and can watch a folder
  ([CLI](https://docs.gyroflow.xyz/app/advanced-usage/command-line-cli)). Whether it renders
  without a display or GPU wasn't confirmed, so plan on a lab PC rather than a runner.
- **Prior art.** Gyroflow points to external loggers such as ESP-gyrologger, and "any other
  logger that writes the GCSV format". No Raspberry Pi logger for it turned up, so the
  recorder would write the GCSV itself.

## Training videos: a second camera

- **Head camera alone:** use the steadied copy. Expect cropped edges, and the fastest glances
  to stay soft.
- **Head camera plus a steady angle:** a chest camera or a fixed camera at the bench records the
  same session. Edit with the steady angle as the main shot, and cut to the head camera for close
  work. Clap once with both cameras running, so the two line up. The recorder's bookmarks
  ([`SOFTWARE.md` phase 1](SOFTWARE.md#phase-1-the-recorder-service)) mark the moments to cut to.
- **One self-stabilizing camera:** see below.

## Commercial devices

- **Action cameras steady themselves.**
  - GoPro HERO13 Black: "HyperSmooth 6.0" ([GoPro](https://gopro.com/en/np/shop/cameras/buy/hero13black/CHDHX-131-master.html))
  - Insta360 GO Ultra: "FlowState Stabilization & 360 Horizon Lock" ([Insta360](https://www.insta360.com/product/insta360-go-ultra))
  - DJI Osmo Nano: "RockSteady 3.0, HorizonBalancing" ([DJI](https://www.dji.com/support/product/nano?set_region=US))

  Worn on a helmet over a respirator ([`PPE.md`](PPE.md)), or on a head strap on other days,
  they give steady head footage straight from the camera.
- **GoPro and Insta360 also record their own gyro, which Gyroflow reads.** Gyroflow supports the
  HERO13 Black and the GO Ultra without manual sync, and GoPro's from the HERO11 on carry their
  own lens calibration in every video
  ([GoPro](https://docs.gyroflow.xyz/app/getting-started/supported-cameras/gopro),
  [Insta360](https://docs.gyroflow.xyz/app/getting-started/supported-cameras/insta360)). So one
  camera can give both files: record with in-camera stabilization off for the record, and steady
  a copy in Gyroflow. On Insta360, "Some of the cameras require use of FreeFrame video mode, for
  motion data to be saved".
- **Glasses move with the head too,** so their footage shakes the same way. In
  [#290's table](../../docs/smart-safety-glasses.md), the HTC Vive Eagle, Rokid's Style Pack and
  a $140 budget pair list stabilized video. Check the others before buying.

## Changes to the plan

- **[`BOM.md`](BOM.md#options):** an optional IMU breakout for the camera head. Adafruit's
  LSM6DSOX is $11.95 and 1.7 g, with the gyro running at up to 6.7 kHz, but it was out of stock
  on 2026-11-28. The ISM330DHCX ($19.95) was in stock. With 3 g at the camera head, the add-on
  parts' centre of mass moves from 0.7 cm to about 0.4 cm behind the ear line. The IMU isn't in
  the 3D model.
- **[`SOFTWARE.md`](SOFTWARE.md):** phase 0 gets a jitter test (item 7). Phase 1 writes the gyro
  log and the frame times next to each clip. Phase 6 adds steadied copies for training videos.

## Still to check

- **How shaky it really is.** Record the same bench task with the headset and with the chest
  camera, and compare the raw footage, the vid.stab copy and the Gyroflow copy.
- **Exposure under the lab's lights.** How short the shutter can be before noise is worse than
  blur.
- **The IMU on the I2C bus.** It would share the bus with the PiSugar 3, so check that their
  addresses don't clash, and how fast the Zero can read it while it encodes.
- **Whether a training video needs the head camera at all,** or the steady angle with a few
  head-camera cuts is enough.
