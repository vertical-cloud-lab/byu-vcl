# Presentation clips: making the Al cups and plugs

Slide versions of the three CAD clips from PR [#232](https://github.com/vertical-cloud-lab/byu-vcl/pull/232)
(`machining_cup.gif`, `machining_plug.gif`, `fill_and_vent.gif`), for
[#248](https://github.com/vertical-cloud-lab/byu-vcl/issues/248). Each clip comes as a looping GIF, which drops straight
into Google Slides, and as an H.264 MP4 for PowerPoint or Keynote.

| Clip | GIF | MP4 | Length | Captions, in order (seconds on screen) |
| --- | --- | --- | --- | --- |
| Cup | [cup.gif](out/cup.gif) | [cup.mp4](out/cup.mp4) | 26.6 s | Face the end flat (5.2) · Drill the pocket (5.2) · Ream it smooth (5.1) · Cut the cup off (5.4) · The finished cup (5.7) |
| Plug | [plug.gif](out/plug.gif) | [plug.mp4](out/plug.mp4) | 32.1 s | Turn it to fit its cup (5.2) · Taper the end that goes in (5.2) · Drill the air hole (5.7) · Chamfer the top edge (5.1) · Cut the plug off (5.2) · The finished plug (5.7) |
| Fill | [fill.gif](out/fill.gif) | [fill.mp4](out/fill.mp4) | 16.4 s | Fill with weighed powder (5.2) · Close it with its own plug (5.2) · Vacuum pulls air out the hole (6.0) |

## The rules they follow

- **Text in one place only.** One caption at a time, centred in a white band under the picture. The #232 clips also had
  a title, a step counter, an italic note, a caption line and leader-line callouts. All of those are gone.
- **Six words at most per caption, and no numbers** (the brief was 4–8 words). With no numbers on screen, nothing can
  disagree with the as-made sizes in #222.
- **Every caption stays up for at least 5 s.** `save()` refuses to write a clip that breaks this or the word limit.
- 1280×720 (16:9) on a pure white background, so the clips sit on a white slide without a visible box.

## What changed from the #232 clips

The motion is re-rendered from the same build123d model, using `machining.py`'s geometry and drawing helpers, rather
than stretched from the old GIFs. Most of #232's steps are on screen for one to three and a half seconds, at 5 fps.
These run at 10 fps, with about five seconds per step. To fill that time the tools approach and back off, the drill
and reamer come back out, the view cross-fades wherever it is cut in half or changes, the camera zooms in for the edge
chamfer (#232 used a note saying "close up"), and each finished part turns, then has its near half fade away. CAD
edges are drawn with a polygon offset, so circular edges come out solid rather than dashed.

The geometry is still the drawing's, from #232: a 2.5" cup with a 1.875" deep pocket and a 3/8" plug. The cups made so
far are 2.75" long with a 1/2" drill 2.25" deep, and their plugs are .5625" long (#222). The clips carry no numbers,
so the only difference is in proportions. "Ream it smooth" follows the drawing (31/64" drill, then ream to .500") and
the smooth hole asked for in #248 for the hydraulic-press versions. The first cups had the 1/2" drill only.

## Rebuilding

```bash
pip install build123d pyvista matplotlib pillow numpy imageio-ffmpeg
xvfb-run -a python clips.py              # all three -> out/{cup,plug,fill}.{gif,mp4}, about 8 minutes
xvfb-run -a python clips.py plug         # just one
xvfb-run -a python clips.py --preview    # two frames per move -> out/preview_<clip>.png, about a minute
```

Captions and their timing are in `clips.py`, next to the motion they label. `clips.py` reads `machining.py`,
`charge_cad.py` and `render.py` from `../cad/` once #232 is merged, and from its commit (`323adba`) until then. To
render several clips at once, give each its own X display (`xvfb-run -n 91`, `-n 92`, ...). Two `xvfb-run -a` calls
started together can pick the same one, and the second then fails with "Render window is not current".
