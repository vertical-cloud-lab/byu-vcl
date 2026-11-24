# Higgsfield: what it takes, and how this render is prepared for it


Web research only. Most figures come from Higgsfield's own pages, which change month to month and
sometimes contradict each other (noted inline). **n/p** = not published by Higgsfield.
**unconf.** = could not be confirmed. Credits are converted to dollars at about $0.049/credit,
Higgsfield's own blog convention (Plus plan). [n] = Sources list.

## 1. Features that take an existing video

| Feature (date) | Model | Input | Input limits | Output | Audio |
|---|---|---|---|---|---|
| **Editing Room** (20 Nov 2026) [1,2] | Higgsfield's own (model n/p) | Your clip. You select a moment, then swap a person, change the angle or location, move the camera, relight (presets, custom lights, or text), or brush-edit. Edits apply only to that moment and stack. | n/p (unconf.) | n/p | n/p |
| **Kling 4.0 "Edit video"** (21 Oct 2026) [1,3] | Kling 4.0 | 1 main clip + up to 4 more + prompt; references up to 15 (≤10 images, ≤5 videos totalling ≤30 s); prompt ≤8,000 tokens. Changes character, product, background, camera angle or style. | Each clip 3–30 s, combined ≤30 s. Resolution, fps and file size n/p. | 3–30 s, 720p/1080p, aspect Auto/21:9/16:9/9:16/1:1, fps n/p | Generates stereo; whether source audio is kept is n/p |
| Kling 4.0 Flash (4 Nov 2026) [1] | Kling 4.0 Flash | Same modes as 4.0; start frame only | – | 3–20 s, 720p only | – |
| **Kling 3.0 Omni Edit** (4 Feb 2026); Kling O1 Video Edit (Nov 2025) [1,4,5] | Kling 3.0 Omni / O1 | Clip + prompt + ≤4 reference images (O1) | **3–10 s.** Third-party API figures for the same model: .mp4/.mov, ≤200 MB, 720–2160 px (fal); 700–4553 px, 24–60 fps (Atlas) [20,21] | Max 1080p; length matches input (API) | API flag `keep_original_sound`/`keep_audio` (default differs by host) |
| **Seedance 2.5 Edit** (Aug 2026) [5,6] | ByteDance Seedance 2.5 | Clip + prompt; region edit / Draw to Edit; references ≤50 (30 images, 10 videos, 10 audio) | Up to 30 s [6] | 480p–720p, length matches source [5] (an older blog says up to 1080p [6]) | Edits audio too |
| **Genjutsu** (Restyle 30 Sep; Motion Transfer and Object Swap 1 Sep 2026) [1,8,9] | Higgsfield's own | One video + ≤30 reference images + optional prompt. Restyle = Style block inside Motion Transfer: 20+ styles or a custom style from your images. Keeps motion, timing and camera. | **4–30 s** | 480p/720p/1080p | n/p |
| Genjutsu Lite (19 Oct 2026) [1,9] | Higgsfield's own | ≤10 reference images, **no Restyle** | 4–15 s (changelog) / 4–30 s (help) | 720p/1080p | n/p |
| **FLUX 3 Video Edit** [10,11,22] | Black Forest Labs (BFL) | Clip + prompt; no references or masks | Higgsfield's limits n/p. BFL's own API: mp4, ≤50 MiB, ≤15 s, **>720p downscaled to 720p, normalized to 24 fps** | Length, aspect and camera follow the source | Source audio carried through |
| Cinema Studio 4.0 Edit Video / Extend (Aug 2026) [12] | Mixed | Uploaded video | ≤30 s | n/p | n/p |
| Gemini Omni Flash 1.2 (5 Nov 2026) [1] | Google | Text, images or video. ≤6 images + ≤3 short videos (appearance only); start frame required, end frame optional | – | 3–15 s, 360p–4K; extend 3–10 s per step, ≤30 s total | Ignores the reference video's audio |

**Utilities:**
- **Video Relight** (21 Aug 2026): presets Practicals, Silhouette, Contre-jour, Soft Cross, Window, Overhead Fall, plus Auto; up to 2 custom lights. **Color Palette**: 50+ grades. [1,13]
- **Upscale** [1,14]:
  - FLUX.3 Upscale: 1080p/2K/4K, Precise or Creative mode, audio kept.
  - ByteDance Upscale: 1080p–8K at 30 or 60 fps.
  - Topaz Video: ≤4K, ≤120 fps.
- **Reframe** (30 May 2026): 16:9, 9:16, 4:3, 3:4, 21:9, 1:1. It generates the missing area instead of cropping. [1]
- **Also listed**: Deflicker, FPS Boost, SDR→HDR, Depth Map. [10,15]

**Not relevant to us (person-centric):** Recast (character swap), Wan 2.2 Animate Replace (Sep 2025),
Lipsync. **Runway Aleph is not offered** on Higgsfield; I found no mention in llms.txt or the changelog [1,2].

**Reference modes do not carry geometry over.** Kling references and Creative Recreation
[3], Seedance `@motion` [5] and the 3D Jutsu previz render [16] use a reference to guide camera
path, motion and composition, but they regenerate the scene. The 3D Jutsu example prompt says
*"Nothing else from the previz (its grey materials, proxy geometry or lighting) is inherited"* [16]. To keep our layout, upload the render as the **source** of an Edit or Restyle
mode, not as a reference.

## 2. Image-to-video from start/end keyframes (our PNG frames)

| Model | Frames | Duration | Resolution | Aspect / fps |
|---|---|---|---|---|
| Kling 4.0 [3] | Up to **10 keyframes**, including first and last | 3–30 s | 720p/1080p | 21:9–9:16; fps n/p |
| Kling 3.0 [5,17] | Start, end, or both | 3–15 s | 720p/1080p/4K | 16:9, 9:16, 1:1 |
| Seedance 2.5 [1,5,7] | First + last | 4–30 s | 480p/720p/1080p. 4K, Flash and (reportedly) Draft Mode are **not available in the US** | 9:16–21:9; about 24 fps (third-party, unconf.) |
| Veo 3.1 [18] | Start + end | 4/6/8 s | 720p/1080p/4K | 16:9, 9:16; **24 fps**; ≤3 reference images |
| Wan 2.7 [1] | First + last; instruction edits | ≤15 s | 1080p | n/p |
| FLUX 3 Video [11] | Start + end; ≤10 reference frames | 5–20 s | 720p/1080p | n/p |
| DoP [19] | Start image required (PNG/JPG), plus an optional prompt | 3 or 5 s | n/p | n/p |

Image-upload size limits are n/p for every model. Output fps is n/p for Kling and Seedance.
In-between motion is invented: only the keyframes themselves are faithful.

## 3. Camera-control presets

**DoP** is Higgsfield's own image-to-video model [19]:
- **Input:** a start image plus an optional prompt, with an "Enhance" option.
- **Presets** come in categories (Basic Camera Control, Epic Camera Control, Effects, and others). **Mix** combines presets in one generation.
- **Camera names** on the Motion library page [23]:
  - Static, Handheld
  - Dolly In/Out/Left/Right, Super Dolly In/Out, Double Dolly
  - Dolly Zoom In/Out, Zoom In/Out, Crash Zoom In/Out, YoYo Zoom
  - Crane Up/Down, Crane Over The Head, Jib Up/Down, Tilt Up/Down
  - Arc Left/Right, 360 Orbit, Lazy Susan, Robo Arm, FPV Drone, Overhead
  - Hyperlapse, Timelapse Landscape, Whip Pan, Dutch Angle, Bullet Time, Focus Change
  - Through Object In/Out, Object POV, Push To Glass, Fisheye, Low Shutter, Snorricam
  - The WAN 2.5 group adds Pan Left/Right.

**Cinema Studio 4.0** [1,12,24]:
- 30+ camera presets, including POV, Robot Arm and Helicopter Shot.
- Moves are written as `#tags` and stack in order.
- Camera bodies: 35mm Film, 8mm Film, DV Camcorder. Up to 50 references.

**Kling and Seedance** take camera moves as prompt text ("dolly in", "arc right") [5].

**Prompt + reference image/video** is supported by Kling 4.0, Seedance 2.5, Gemini Omni,
Genjutsu (images only), Kling Omni/O1 Edit (≤4 images) and Veo 3.1 (≤3 images). DoP takes an
image + prompt only.

**Caveat:** every preset *generates a new camera move*. None of them follows our rendered camera path.

## 4. Pricing (checked 2026-11-24)

**Plans** [25] (a Black-Friday promo ends 25 Nov):

| Plan | Price | Credits / month | Notes |
|---|---|---|---|
| Free | $0 | 0 | Watermarked; few models |
| Starter | $19/mo | 270 | No Seedance 2.5 |
| Plus | $59/mo | 1,200 | All models; 6 parallel videos |
| Ultra | $129 / $250 / $375 per mo | 3,000 / 6,000 / 9,000 | |
| Team | $55 per seat | 1,000 per seat | |
| Scale | $119.99 per seat | 2,500 per seat | |
| Enterprise | Custom | Custom | |

- Credits do not roll over. "Unlimited" models apply only on higgsfield.ai. [26]
- Paid plans are watermark-free. You own your outputs. Commercial use is not tied to a plan. [27]
- The **API** is billed separately: prepaid USD, priced per output second, 20 concurrent requests. [28]

**Published credit examples** (they vary; the Generate button shows the real price):

| Feature | Published cost | Per second at 1080p |
|---|---|---|
| Genjutsu Restyle / Motion Transfer [8] | 15 s = 45 / 105 / 300 cr at 480p / 720p / 1080p | ≈20 cr ≈ **$0.98** |
| Genjutsu Lite [8] | 15 s at 1080p = 192 cr | – |
| Kling 4.0 [3,29] | 5 s at 1080p = 18.75–37.5 cr (sources disagree) | ≈3.75–7.5 cr ≈ **$0.18–0.37** |
| Seedance 2.5 [7] | 10 s = 30 / 70 / 160 / 280 cr at 480p / 720p / 1080p / 4K | – |
| Seedance 2.5 Edit [6] | 10 s at 1080p = 90 cr | – |
| FLUX 3 Video [11] | 5 s = 45 cr; 20 s = 180 cr | 9 cr |
| Kling 3.0 Omni Edit | n/p on Higgsfield; third-party APIs $0.14–0.17/s [20,21] | – |

Cheap utilities, per 15 s at 720p [15]: FLUX.3 Upscale ≈14 cr, Reframe 71 cr, FPS Boost 58 cr,
Relight 42 cr (an Aug 2026 post gave 135 cr [13]).

**Budget:** one 1080p pass over 120 s costs about 2,400 cr with Genjutsu, or about 450–900 cr with
Kling 4.0. Allow 3–4 takes per shot. That means the Ultra 6,000 or 9,000 tier, or top-ups.

## 5. Guidance on geometry-faithful results (sources say)

- **Edit, don't regenerate.** Full regeneration shifts camera, pacing and details. Name only what
  changes and lock the rest: camera, lighting, timing, positions [6,15].
  BFL: *"Everything it doesn't mention stays as filmed."*
- **For blockouts and previz,** "name what each box becomes and what stays the same" [22]. For example:
  *"…the pillars become ruined highway columns… Same weave lines, same speeds, same camera
  overtake."*
- **Restyles:** describe **materials and light**, not a style label alone [22].
- **One change per iteration** [5,15,30].
- **Draft first.** Test at 720p on short clips, then render at 1080p with the same prompt [5]. Upscale last [15].
- **Text.** Higgsfield's own prompt examples use *"NO on-screen text, NO subtitles… No readable text
  anywhere"* [30]. Enhancement "may reconstruct faces, text, and textures inaccurately" [15].
  Keep negative lists short: "Say what you want, not what you don't" [30].
- **Source footage.** Use one continuous shot with no cuts, stable lighting and camera, and room around
  the subject. Avoid tight, cluttered shots: "vague prompts and cramped source footage invite the model to
  remake the scene" [31]. Genjutsu: "the cleaner the movement, the better" [9]. Keep reference
  images close to the source framing [9].
- **3D-render pipeline (fal, Jul 2026)** [32]:
  - Use flat grey simple geometry with "no small clutter that could be misread by an AI restyler".
  - Every key element must be **visible in the first frame**, or the model invents content mid-shot.
  - Crop references to the film's exact aspect ratio, or the model recomposes the shot.
  - Check alignment by overlaying output and source at 50%. They rendered at 24 fps.
- **Known failures:**
  - Excess style or lighting changes, and edge flicker [31].
  - Drift of product or shape details, especially in fast motion or when objects cross [15].
  - Replacing an object with one of very different size or shape breaks its motion [6].
  - Wrong depth placement [31].
  - Recentering or zooming out [32].
  - Fixes: run Deflicker [10]; if areas meant to stay the same change, retry from the original clip [15].
- **Continuity across shots:** use the last frame of one clip as the start frame of the next [5,30].

## 6. Recommendation: what to hand to Higgsfield

1. **Package.** Two cuts plus support files:
   - (a) A **clean plate**, delivered per shot.
   - (b) The captioned cut, as a reference only.
   - (c) A shot list (CSV/JSON): shot ID, source in/out timecode, frames, camera move, the objects in frame, and a prompt.
   - Captions, narration, music and logos go back on in the editor after Higgsfield. Deliver silent plates.
2. **Shot length.** One continuous camera move per clip, no internal cuts.
   - Aim for **5–10 s, never under 4 s**. Genjutsu and Seedance need ≥4 s, Kling ≥3 s.
   - ≤10 s keeps every edit model available, including Kling 3.0 Omni Edit (3–10 s) and FLUX (≤15 s).
   - Only Kling 4.0, Genjutsu and Seedance accept up to 30 s, and long retries are expensive.
   - Add 12 frames of head and tail handles, for dissolves between separately restyled shots.
   - At ≤2 min, that is about 12–20 shots.
3. **Format.** 1920×1080, 16:9, full frame (no letterbox).
   - **24 fps constant.** BFL normalizes to 24 and Veo and Grok output 24. A 30 fps plate gets resampled. If the final cut must be 30 fps, use FPS Boost or upscale-to-30 afterwards.
   - H.264 High 4:2:0 MP4, Rec.709, `+faststart`, no audio track, **<50 MB per clip**.
   - Most edit outputs top out at 1080p, and some at 720p, so a 4K plate buys nothing.
4. **Keyframes.** Lossless PNGs, exactly frame 0 and the last frame of each clip, plus one every ~5 s for long shots (Kling 4.0 takes 10).
   - Optionally restyle 1–2 hero stills per shot in an image model. Feed them as appearance references (Genjutsu ≤30, Kling ≤10 images).
   - Use start/end-frame image-to-video **only** for inserts and transitions, since its motion is invented.
5. **Remove from the render** (judgment, guided by [15,31,32]):
   - All on-screen text, labels, callouts, scale bars, timestamps and logos.
   - Transparency, ghosting, cutaway or x-ray views, and section planes.
   - Wireframes, grid lines, path lines and bounding boxes.
   - Sub-pixel members: thin railings, mesh, grating and perforated sheet cause moiré and flicker. Thicken them to ≥3 px, or simplify.
   - Aliasing: turn on SSAA.
   - Z-fighting and shadow-map shimmer.
   - Objects that pop in or teleport.
   - Whip pans and very fast arm moves.
   - Empty black voids. Close the building, because the model fills emptiness.
   - False-colour status coding, which the model will treat as paint.
6. **Keep in the render:**
   - Plausible materials (grey powder-coated steel, polished concrete, stainless).
   - One consistent key-light direction and white balance across all shots, with soft shadows and AO, so Relight and restyle can read form.
   - Slow, simple moves (dolly, truck, crane, orbit).
   - Every machine in the shot visible from frame 0.
7. **Model order to try.** Test one 5 s shot at 720p in each, then keep the best:
   1. Kling 4.0 Edit, or Kling 3.0 Omni Edit for ≤10 s.
   2. Genjutsu Restyle with a custom style from a restyled keyframe.
   3. FLUX Video Edit (720p cap).

   Fix local problems in Editing Room or with Seedance region edit, then Deflicker if needed, then
   upscale last (FLUX.3, Precise mode). QC each shot by overlaying it on the plate at 50%: counts of
   VLMs, atomizers and robots, arm poses, platform stairs.
8. **Prompt template** (English; generic nouns, since brand names may invite fake logos, which is our judgment):
   > Restyle this 3D render as photoreal footage of an automated metal-powder materials lab in a
   > high-bay steel-frame industrial hall. The tall grey towers are 10.7 m vertical-lift storage
   > modules with powder-coated steel panels and a lit access opening; the small wheeled carts are
   > autonomous mobile robots carrying six-axis collaborative arms; the rows of small boxes are
   > benchtop ultrasonic powder atomizers; the large vessels on steel platforms with stairs are gas
   > atomizers; the enclosed cabinets are metal 3D printers. Keep every object's position, size,
   > count and motion, and the camera path, framing and timing, exactly as in the source.
   > Cool-white LED high-bay light, polished concrete floor. No people, no text, no new objects.

   Then add the shot-specific mapping and move ("slow dolly in along the VLM row").

**Open (unconfirmed):**
- Editing Room input limits.
- Whether Kling 4.0, Genjutsu and Higgsfield's FLUX keep source audio.
- Output fps for Kling and Seedance.
- Whether base Seedance 2.5 is available in the US. BYU is in the US. 4K, Flash and Draft Mode are flagged as not available there.
- Kling 3.0 Omni Edit credit price.

## Sources (accessed 2026-11-24)

1. Higgsfield changelog + RSS, dated entries: Kling 3.0/Omni Edit 4 Feb, Wan 2.7 6 Apr, Reframe 30 May, Seedance 2.5 6 Aug, Cinema Studio 4.0 12 Aug, Relight 21 Aug, FLUX 3 Upscaler 27 Aug, Genjutsu 1 Sep, Genjutsu Restyle 30 Sep, Genjutsu Lite 19 Oct, Kling 4.0 21 Oct, Kling 4.0 Flash 4 Nov, Gemini Omni Flash 1.2 5 Nov, Seedance 2.5 4K 11 Nov, Seedance 2.5 Flash 12 Nov, Editing Room 20 Nov 2026. https://higgsfield.ai/creator-hub/changelog · https://higgsfield.ai/creator-hub/changelog/rss.xml
2. Higgsfield homepage, Editing Room tagline, and llms.txt site index (both undated). https://higgsfield.ai/ · https://higgsfield.ai/llms.txt
3. Kling 4.0 on Higgsfield (20 Oct 2026). https://higgsfield.ai/blog/kling-4-0-on-higgsfield
4. Kling O1 guide (30 Nov 2025). https://higgsfield.ai/blog/Kling-01-is-Here-A-Complete-Guide-to-Video-Model
5. Help: How do I use Kling? / Seedance? (both modified 17 Nov 2026). https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-kling · …/how-do-i-use-seedance
6. Edit AI video without regenerating (16 Sep, updated 20 Oct 2026). https://higgsfield.ai/blog/edit-ai-video-without-regenerating
7. Seedance 2.5 on Higgsfield (6 Aug, modified 10 Nov 2026). https://higgsfield.ai/blog/seedance-2-5-on-higgsfield-2026
8. Genjutsu blog (31 Aug, updated 2 Nov 2026). https://higgsfield.ai/blog/higgsfield-genjutsu
9. Help: How do I use Genjutsu? (26 Oct 2026). https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-genjutsu
10. Video to video page (undated). https://higgsfield.ai/video-to-video
11. FLUX 3 on Higgsfield (16 Aug 2026). https://higgsfield.ai/blog/flux-3-higgsfield; AI video editor page (undated). https://higgsfield.ai/ai-video-editor
12. Help: How do I use Cinema Studio? (modified 19 Nov 2026). https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-cinema-studio
13. Video Relight and Color Palette (20 Aug 2026). https://higgsfield.ai/blog/video-relight-color-palette-higgsfield
14. Help: How do I use Upscale? (modified 18 Nov 2026). https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-upscale
15. How to edit videos with AI (24 Oct 2026). https://higgsfield.ai/blog/how-to-edit-videos-with-ai
16. 3D Jutsu (5 Sep 2026). https://higgsfield.ai/blog/higgsfield-3d-jutsu
17. Kling 3.0 user guide (2026, undated). https://higgsfield.ai/blog/Kling-3.0-is-on-Higgsfield-User-Guide-AI-Video-Generation
18. Veo 3.1 page (undated). https://higgsfield.ai/veo3.1
19. Help: How do I use DoP? (2 Aug, modified 12 Sep 2026). https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-dop
20. fal, Kling O1 video edit (undated). https://fal.ai/models/fal-ai/kling-video/o1/video-to-video/edit; Replicate, Kling v3 Omni (undated). https://replicate.com/kwaivgi/kling-v3-omni-video/readme
21. Atlas Cloud, Kling O3 Pro video edit (undated). https://www.atlascloud.ai/models/kwaivgi/kling-video-o3-pro/video-edit
22. BFL FLUX Video Edit limits and editing prompt guide (undated). https://docs.bfl.ai/flux_tools/flux_video_edit.md · https://docs.bfl.ai/guides/prompting_video_editing.md
23. Higgsfield Motion library (preset list; uploads dated 2025-09-18 to 2026-11-24). https://higgsfield.ai/motion
24. Cinema Studio page (undated). https://higgsfield.ai/cinematic-video-generator
25. Pricing (updated 2026-11-24). https://higgsfield.ai/pricing.md
26. Help: plans (modified 11 Nov 2026); what uses my credits (modified 28 Aug 2026). https://higgsfield.ai/creator-hub/help-center/plans/how-do-higgsfield-plans-work
27. Help: ownership and commercial use (modified 12 Sep 2026). https://higgsfield.ai/creator-hub/help-center/account/who-owns-my-generations-and-can-i-use-them-commercially
28. Help: Higgsfield API (16 Sep 2026). https://higgsfield.ai/creator-hub/help-center/integrations/what-is-the-higgsfield-api
29. Independent review, verified 22 Nov 2026. https://omidsaffari.com/blog/higgsfield-ai-review
30. Help: How do I write a good prompt? (modified 14 Sep 2026). https://higgsfield.ai/creator-hub/help-center/getting-started/how-do-i-write-a-good-prompt
31. The Rundown, "Add CGI to any video with Higgsfield" (updated 23 Jul 2026). https://app.therundown.ai/guides/add-cgi-to-any-video-with-higgsfield
32. fal blog, "From clay 3D render to a real action short" (13 Jul 2026). https://blog.fal.ai/from-clay-3d-render-to-a-real-action-short-a-3d-to-ai-pipeline-with-total-control/
