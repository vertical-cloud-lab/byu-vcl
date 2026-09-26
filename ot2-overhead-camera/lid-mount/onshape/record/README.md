# Screen-recording the Onshape UI build for YouTube

`record_ui_build.py` runs `onshape_ui.py`'s steps unchanged and records the whole screen
while they run. It then adds a title card and chapters, and can upload the result to the BYU
Vertical Cloud Lab channel with the upload-only token.

```bash
cd ot2-overhead-camera/lid-mount/onshape/record
./rig.sh start      # Xvfb :99 at 1920x1080, headed Chrome, SOCKS tunnel out through the CubXL Pi
./rig.sh check      # the tunnel's exit network (ASN and org only) and a screenshot of the display
python record_ui_build.py \
    --folder-url 'https://cad.onshape.com/documents?nodeId=591b857bfa1a8f40e6455c90&resourceType=folder' \
    --upload --privacy unlisted
./rig.sh stop       # stops all three and deletes the browser profile
```

Needs `ffmpeg`, `Xvfb`, Google Chrome, `playwright`, `cadquery` (for `lid_mount.Params`), and
`youtube/requirements.txt`; the script imports `youtube/yt_service.py` from the repo root. The folder URL is **vcl-shared › OT-2 Overhead Camera**.

- **The login never appears on screen.** The script signs in before `ffmpeg` starts, and the
  browser profile never saves the password.
- **What's drawn over the page.** Playwright sends its input through DevTools, so the X cursor
  never moves and a raw recording would show no pointer. [`overlay.js`](overlay.js) draws one
  from the page's own events, along with click ripples, key badges for shortcuts, and a caption
  for each step. Every part of it is `pointer-events: none` and its listeners are passive, so
  Onshape receives exactly the same input either way.
- **Chapters.** The first caption of each feature becomes a YouTube chapter. Each chapter is at
  least 10 s long, which is YouTube's rule.
- **The volume is checked before upload.** Onshape's figure drifts by a few hundredths of a
  mm³ between runs (108,840.264 vs 108,840.279), while the smallest feature, one bolt hole, is
  95 mm³. So the tolerance is 1 mm³.

## 2026-09-26

It took three takes; [`../evidence/recording-2026-09-26.json`](../evidence/recording-2026-09-26.json)
has the details of each.

1. **Take 1** built all 14 features, but Mirror 1 and Mirror 3 had nothing to mirror, and the
   volume came out at 90,299 mm³. From a runner, a feature-list pick takes more than a second to
   reach a dialog's field. The script had already moved on to the mirror-plane field, so those
   picks were lost. `Ui.pick_into` in `onshape_ui.py` now waits for each pick to show up in the
   field.
2. **Take 2** built the right part, but a 0.01 mm³ tolerance was tighter than Onshape's own noise.
3. **Take 3** is on YouTube (unlisted). It has **no pointer or captions**. Run as an init script,
   `overlay.js` threw before the page had any elements, so the overlay vanished at the new
   document's full page load. That is fixed now. The video's description still says the overlay
   is there, and the upload-only token can't edit it.

**Unlisted uploads stay unlisted.** The upload-only token requested `unlisted`, and the video
came back unlisted, with no unaudited-project lock. That answers the open question in #236.

**Where the traffic goes.** The tunnel relays everything the browser loads, not just Onshape. A
PAC file that sends only `*.onshape.com` through the Pi would narrow that; see the security note
on PR #234.
