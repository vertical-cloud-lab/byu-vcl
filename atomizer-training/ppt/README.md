# Slide clips of the 3D animations

The 3D animations from [`../viz3d/`](../viz3d/README.md), cut for a PowerPoint slide. Each clip shows one short caption
at a time and speaks one short line per caption. The summary is the whole run in one condensed take, with the fasteners
sped up. The other two clips are single steps at the animation's own speed, the same as in the GIFs and the tutorials.

| Clip | Narrated, unlisted (draft 1) | File | Length |
| --- | --- | --- | --- |
| **The whole run** (`summary`), condensed. Furnace (about 14 s): crucible into the coil, nut, insulation, sealing rod, charge, lid. Stack (6 s): built, into the door, door shut. Run (13 s): argon and the melt, the pour onto the plate (zoomed in), powder into the container | https://www.youtube.com/watch?v=qwopusVSwf4 | [`videos/summary.mp4`](videos/summary.mp4) | 0:33 |
| Loading the furnace (`03_furnace_load`): lid and lever, crucible into the coil, the graphite nut from below, insulation, thermocouple, sealing rod, charge, lid | https://www.youtube.com/watch?v=86K-EHhtPp8 | [`videos/03_furnace_load.mp4`](videos/03_furnace_load.mp4) | 1:04 |
| The ultrasonic stack and the door (`02_stack`): transducer, booster, sonotrode, into the door, plate, scan, wet test, cover, door shut and bolted | https://www.youtube.com/watch?v=8lBR11fgznI | [`videos/02_stack.mp4`](videos/02_stack.mp4) | 0:47 |

[`script.md`](script.md) lists every caption with when it is up, its spoken line and how long that line takes, with a
frame from each. The upload log, with the commit each description links to, is [`uploads.json`](uploads.json).

## The rules

They live in [`captions.py`](captions.py), and `build_ppt.py` refuses to build if any is broken:

- **At most 6 words on screen at a time.** A number and its unit ("65 N·m") count as two.
- **Each caption stays up at least 4 s.** The two clips' captions are up 4.2–7.7 s each. One caption per sub-step of the
  animation; the long nut sub-step (2a.4) carries two, the door and nut, then how tight.
- **Each line is spoken while its caption is up.** It starts 0.25 s after the caption appears and ends at least 0.3 s
  before the next.
- **No other text.** The GIFs' title, step label, leader labels, gauges and long captions are all off.
- **The single-step clips keep the animation's speed.** Nothing is slowed down or held to fit the voice, except that the
  last frame is held for 1 s. The voice is the tutorials' `en-US-AndrewMultilingualNeural` at 1×.
- **The summary is condensed, and captions only the steps an audience needs.** It is its own animation
  (`anim_summary` in [`../viz3d/steps.py`](../viz3d/steps.py)): the same parts on the same paths, in the same order, as
  the furnace, stack, melt and pour animations.
  - Sped up: the holder (4 turns in about a second), the nut (5 turns in about one), the thermocouple, the lever, the
    booster, sonotrode and plate, the cover and the three bolts.
  - Left out: the scan, the wet test, the gas washes and every hold.
  - Its 7 captions name the key steps only, so the fasteners pass without one. Its last frame is held 0.7 s.
  - [`../viz3d/out/collisions_summary.md`](../viz3d/out/collisions_summary.md) is its interference check.

## How they differ from the GIFs

- 1920 × 1080 at 30 fps. The GIFs are 800 × 450 at 10 fps, and the tutorials' animations 1280 × 720 at 15 fps. Every
  move lasts as many seconds as before.
- Rendered with no text at all (`VIZ3D_CLEAN=1` in [`../viz3d/scene.py`](../viz3d/scene.py)), then captioned here: white
  bold text on a navy pill, centred near the bottom, switched between frames with no fade.

## In PowerPoint

Insert → Video → This Device, and pick the MP4. Under Playback, set Start to Automatically or When Clicked. The narration
is in the file. To talk over it instead, set the clip's Volume to Mute; the captions are burned in either way.

## Rebuilding

```bash
export PIP_TIMEOUT=600 PIP_RETRIES=2
pip install cadquery pyvista edge-tts               # plus: apt-get install xvfb libgl1-mesa-dri ffmpeg
cd ../viz3d
VIZ3D_CLEAN=1 VIZ3D_SIZE=1920x1080 VIZ3D_FPS=30 xvfb-run -a -s "-screen 0 1920x1080x24" python steps.py 03_furnace_load 02_stack summary
cd ../ppt
python build_ppt.py --check                         # the rules and timing (uses the 15 fps timing if nothing is rendered)
python build_ppt.py                                 # videos/*.mp4, script.md, *_sheet.jpg (or name one: summary)
python build_ppt.py upload --ref <pushed sha>       # unlisted, upload-only token; ids into uploads.json
```

The clean renders took 13 minutes for the two single steps, run side by side on four cores, and 7 minutes for the
summary. To change the wording, edit `captions.py` and rerun
`build_ppt.py`; the renders are reused. A caption's time is given as an offset into one of the animation's sub-steps
(their frames are in `../viz3d/out/clean/<name>.json`). Moving one means changing that offset, or the motion in
`../viz3d/steps.py`.

The uploads are not in the [playlist](https://www.youtube.com/playlist?list=PLB8wxmcPAjLM), and
[`../playlist/sync.py`](../playlist/sync.py) does not touch them, since they are not in its catalog.
