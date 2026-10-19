# Seeing what the lid camera sees

The camera is the HQ Camera (IMX477) with the 8–50 mm zoom, on the Pi 5 that sits on the
mount's deck. On the tailnet it is the Pi behind `RPI_STREAM_CAM_HOSTNAME`, which also runs
CubOS and reaches the OT-2 over its wired link. Only one program can hold the camera at a time,
so stop the stream (`sudo systemctl stop device.service`) before a preview or a still, and start
it again afterwards; see [`stream/README.md`](stream/README.md).

| Way | Needs | Good for |
|---|---|---|
| **Live, anywhere: the YouTube stream** in the [OT2 overhead Livestreams Playlist](https://www.youtube.com/playlist?list=PLM4VC4X_7XKQ) (public, since 2026-10-18; its own playlist since 2026-10-19; see [`stream/`](stream/README.md)) | Nothing | Watching the deck from anywhere, with YouTube's 5–20 s of delay. Full 4:3 field at 1920 × 1440, 3 fps, timestamp top left |
| **Live, in a browser:** [`preview_server.py`](preview_server.py) on the Pi, then open the address it prints | The viewing device on the lab's tailnet, and someone with SSH to the Pi to start it (or a comment asking `@claude` to start it) | Positioning and focusing the mount |
| **Live, on a monitor at the robot:** `rpicam-hello -t 0 --viewfinder-mode 2028:1520:12:P` | A monitor on the Pi's micro-HDMI port, plus a keyboard or an SSH session to start it | Positioning while standing at the OT-2, with no network in the loop |
| **One full-resolution still:** a comment asking `@claude` for a still from the lid camera | Nothing | Checking the result. Measurements should come from these: 4056 × 3040 px |

```bash
# on the Pi
python3 preview_server.py                      # prints http://<tailnet address>:8000; stops after 30 min
python3 preview_server.py --minutes 90
rpicam-still -n -t 3000 -o still.jpg           # full resolution
```

`preview_server.py` listens on the Pi's tailnet address only, not on the campus Wi-Fi. The
tailnet policy lets people reach any port on a device, so anyone on the tailnet can open it.

## Use the whole sensor

The live view must cover the same field as a still, or the slots at the edges look cut off when
they aren't. [PR #84's `preview_server.py`](https://github.com/vertical-cloud-lab/byu-vcl/blob/84b8c0b/ot2-overhead-camera/preview_server.py)
asks for a 1536 × 864 stream. For that, libcamera picks the IMX477's 16:9 mode,
`ScalerCrop (108, 440, 3840, 2160)`: 95 % of the sensor's width and 71 % of its height. At 8 mm
from the middle of the deck it hides the front 52 mm of slots 1–3 and the back 52 mm of
slots 10–12 ([figure](../renders/wide_view_8mm.png)). The version here forces the 2028 × 1520
binned mode, `ScalerCrop (2, 0, 4052, 3040)`, and streams 1352 × 1014. Both crops were read
from the camera on 2026-10-15, and this script was run there end to end: 4:3 frames, the page,
the tailnet-only listener, and the stop after `--minutes`.

The live view is a third of full resolution: about 2.8 px/mm at 8 mm, or 19 px across a well.
That's enough to position and focus by, not to measure.

## 2026-10-15, 17:39 UTC: the camera saw nothing of the deck

![Three frames from the lid camera on 2026-10-15](frames/2026-10-15/lid_camera_blocked.jpg)

At 17:39–17:42 UTC the frame was black. Turning the OT-2's rail lights on (17:42:04–17:42:08,
no run active, then back off) changed nothing: the same auto exposure, 67 ms at gain 7.9,
and Lux 0.172 against 0.173. So the lens wasn't looking at the deck. A 2.5 s exposure shows
light only in the corners, and very blurred, which points at something close to the lens.
Check, in this order:

1. the lens cap;
2. the blackout paper on the lid, which needs a hole at least as big as the base's 46 mm
   aperture under the lens;
3. that the mount is over the window;
4. that the iris ring isn't closed.

The numbers are in [`frames/2026-10-15/frames.json`](frames/2026-10-15/frames.json).

## 2026-10-15, 22:04 UTC: the deck is in view, out of focus

![Two lid-camera frames and the OT-2's own camera, 2026-10-15 22:04-22:08 UTC](frames/2026-10-15/lid_camera_in_view_defocused.jpg)

Whatever blocked the lens has gone. Turning the rail lights on for 5 s (22:07, no run active,
then back off) raised the camera's Lux reading from 4.6 to 136, and labware shows. But the
frame is badly out of focus.

The zoom already looks at or near the wide end. The dark labware at the top of the frame spans
1,130 of the still's 4,056 px. A 128 mm labware footprint would span 1,086 px at 8 mm,
1,358 at 10 mm and 1,629 at 12 mm. The corners are also dark, at 20–27 % of the centre's
brightness, as expected below about 9 mm. The blur and the labware's height make this good
to about a millimetre.

Zoom, focus and iris are manual rings, each locked by its own thumbscrew, so they can only be
set at the robot:

![Which ring is which](frames/2026-10-15/lens_rings.jpg)

1. Turn the zoom ring toward WIDE until it stops: that is 8 mm.
2. Open the iris fully, which makes the sharpest point easiest to find.
3. Turn the focus ring until the labware edges are sharp. The lens is varifocal: changing the
   zoom moves the focus, so refocus after every zoom change.
4. Tighten the three thumbscrews. Closing the iris a little afterwards adds depth of field.

If no position of the focus ring gives a sharp picture, check the C–CS adapter: exactly one
ring between the lens and the camera, as in step 6 of [the assembly](../README.md#2-assemble).
In July a misplaced adapter ring is why the camera wouldn't focus (#84). The numbers are in
[`frames/2026-10-15/frames_2204Z.json`](frames/2026-10-15/frames_2204Z.json).

## 2026-10-18: streaming to YouTube

The camera now streams around the clock as `device.service` on the Pi, public. Until
2026-10-19 16:24 UTC it went into the
[OT-2 Livestreams Playlist](https://www.youtube.com/playlist?list=PLdKz1vXA-rfQ); since then it has
its own, [OT2 overhead Livestreams Playlist](https://www.youtube.com/playlist?list=PLM4VC4X_7XKQ),
at 1920 × 1440 and 3 fps. The newest video in the playlist is the live one. That is the way to watch the feed while positioning,
zooming or focusing the mount: YouTube adds 5–20 s of delay, so move, wait, look. The set-up,
settings and how to operate it are in [`stream/README.md`](stream/README.md). The stream holds
the camera, so `preview_server.py` and `rpicam-still` need it stopped first.

**First frames, 04:34–04:38 UTC: black.** Frames were pulled from the live stream on the Pi
(`yt-dlp -g` for the HLS address, then `ffmpeg -frames:v 1`) with the OT-2's rail lights
switched on for 20–40 s at a time (no run active, lights off again afterwards). The robot's own
camera saw a lit deck in the same seconds (mean luma 111 of 255,
[picture](frames/2026-10-18/ot2_camera_0438Z_lights_on.jpg)); the stream frame was black
(mean luma 1.1, [frame](frames/2026-10-18/stream_frame_0438Z_lights_on.jpg)), with and without
the lights. That is the 15 Oct 17:39 UTC situation again: the lens is capped, the iris is closed,
or the blackout cover is over it. Check those at the robot. The stream shows the deck the moment
the lens is clear; nothing needs restarting. The orientation (`CAMERA_VFLIP`/`HFLIP`) could not be
judged for the same reason and is still at the default.
