# Provenance Eyes: head-worn cameras we can script

Issue [#342](https://github.com/vertical-cloud-lab/byu-vcl/issues/342). We want something that
replaces the chest camera for recording lab procedures, with three hard requirements:

1. A **camera and a microphone** that record what the wearer sees and hears.
2. **"Backdoor" (developer) access**: we can read the device's logs, and get the video and audio
   into our own code without going through a vendor's app by hand.
3. **Automated upload** to our database (MongoDB `digital-wetlab`) and to YouTube.

This follows [#290](https://github.com/vertical-cloud-lab/byu-vcl/issues/290). There,
[`smart-safety-glasses.md`](https://github.com/vertical-cloud-lab/byu-vcl/blob/aa9ff51/docs/smart-safety-glasses.md)
(on an unmerged branch) compared safety ratings, weights and Amazon prices. This page asks the
question that doc didn't: **which devices let us get at the data?**

Researched on **2026-11-12** from makers' pages, developer docs and press. Nothing has been bought,
worn or tested. See [How this was gathered](#how-this-was-gathered) for which facts were
re-checked on the maker's own page.

> **Price.** The issue says ">$500". Read literally, that means over $500, and the three picks below
> are all over $500. If it meant *under* $500, see [Under $500](#under-500-mentra-live-and-the-meta-glasses).
> Nothing under $500 is safety eyewear.

## Short version

**Meta's glasses fail the "logs" requirement.** Meta documents no ADB, shell or log access to its
glasses and offers no device management. Its new developer toolkit streams at most 720p into an
app of our own. The glasses' own recordings stop at 3–5 minutes and only reach us through the
Meta AI app. And Meta says they "must not be used as safety glasses". Details are
[below](#idea-1-meta-glasses).

**The three that meet all three requirements, over $500:**

| | [Iristick.G3](https://iristick.com/tools/Iristick.G3/) | [RealWear Arc 3](https://support.realwear.com/knowledge/arc3/specifications) | [Pupil Labs Neon](https://pupil-labs.com/products/neon), "Safety on" frame |
| --- | --- | --- | --- |
| What it is | Safety glasses with two cameras, plugged into a phone | An Android computer worn on the head with a camera arm, worn **over** your own safety glasses | A research eye tracker with a scene camera, plugged into a phone |
| Price | €2,275 excl. VAT (about $2,550), **plus** the SDK: €1,137.50, then €1,000 a year | about $2,950 (CDW lists $2,931.99; reseller prices, not re-checked) | €6,460 (about $7,250, before US tariffs) |
| Eye protection | **EN 16321 / ANSI Z87 / IP54** (maker's claim) | none of its own; "compatible with prescription/safety glasses" | built on Z87.1+ rated Revision Sawfly lenses; whether the assembled frame keeps the rating isn't stated |
| Camera | two 16 MP cameras between the eyes: 115°×77° wide and 44°×36° zoom, streaming at 1080p | 48 MP (82°) plus 8 MP wide (120°), 1080p60 | 1600×1200 at 30 Hz, 103°×77°, **plus where you were looking** (gaze at 200 Hz) |
| Microphones | 2, beamforming | 4, active noise cancellation (voice recognition up to 100 dBA) | stereo, recorded into the video; **off by default** |
| Logs | our app's `adb logcat` on the phone | `adb logcat` and `adb bugreport` on the device; **ADB is on by default** | REST `/api/status`, a WebSocket feed, and `android.log.zip` in each recording |
| Getting files | our app writes them on the phone, then uploads them or `adb pull` | `adb pull` from the device's storage | export in the app, then USB; or the optional Pupil Cloud API |
| Live video | SDK "direct streaming to your own … server", then RTMP to YouTube | any Android RTMP app or library (untested) | RTSP on the local network, then `ffmpeg` to YouTube RTMP |
| Weight | 95 g | 179 g | not checked |
| The catch | the camera is only reachable through an SDK under NDA, so **we write an Android app** | it isn't glasses, and it's the heaviest of the three | price; full-quality files need a manual export; live audio is 8 kHz |

Which one fits:

- **Iristick.G3** fits the issue's second idea best ("safety glasses built like Meta glasses for
  manufacturing and laboratory spaces"). It is the only shipping product found that is itself
  certified eye protection with a camera and microphones. Backdoor access costs money and code:
  the glasses are "inert without a phone running a licensed app"
  ([Iristick](https://docs.iristick.com/introduction/device-management/)).
- **RealWear Arc 3** has the most backdoor for the least effort. It is a full Android 13 device,
  so any recorder or uploader app can be installed on it, and ADB comes switched on. It's the safe
  pick if the requirement is "we can see everything it does".
- **Pupil Labs Neon** is the provenance-grade option. It has a documented local API with start
  and stop, event markers, and clock sync to the phone at the millisecond level, and it records
  where the wearer was looking. It costs the most.

## What "backdoor access" has to mean

For each candidate, five checks:

| Check | Why it matters for provenance |
| --- | --- |
| **Logs** we can read (`adb logcat`, a status API) | to tell a failed recording from a missing one, and to keep battery, temperature and errors with the clip |
| **Files** we can pull without a vendor cloud | the original file, and its hash, is the record |
| **Live audio and video** into our code (RTMP, RTSP, SDK frames) | to livestream to YouTube as the stream cams do |
| **Our own code** controls start and stop | to tag each clip with an experiment ID, possibly by MQTT like the rest of the lab |
| **No mandatory cloud account** | so data reaches us first, and the device keeps working if the vendor changes plans |

Three kinds of device turned up:

- **Standalone Android** (RealWear, Vuzix, RayNeo X3 Pro): passes all five out of the box. ADB
  gives logs, files and app install.
- **Tethered to a phone** (Iristick, Pupil Labs Neon): the phone is an ordinary Android phone with
  ADB. How much we can reach on the glasses depends on the vendor's SDK or API.
- **Consumer glasses with a phone companion app** (Meta, Mentra Live, Android XR): our code runs on
  the phone and sees what the SDK hands it. Meta exposes the least; Mentra, being open source,
  exposes the most.

## 1. Iristick.G3: safety glasses with cameras

- **Hardware** ([Iristick](https://iristick.com/tools/Iristick.G3/)): EN 16321 / ANSI Z87 / IP54,
  95 g, two 16 MP cameras centred between the eyes (wide 115°×77°, zoom 44°×36°), streaming at
  1080p, dual beamforming microphones and a speaker. It has no battery: it runs from the phone over
  USB-C (Android 8+ or iOS 15+). Iristick doesn't say which Z87.1 edition, or whether it has the
  "+" high-impact mark, so check the stamp on the frame. A prescription insert is reportedly
  available on request.
- **SDK** ([developers page](https://iristick.com/developers/)): native Android and iOS SDKs with
  "live preview, frame grabbing, and direct streaming to your own AI stack, server, or storage".
  They also cover the heads-up display, offline voice commands, the IMU and buttons. Access needs an
  NDA. The **Developer Package** is €1,137.50 one-time, and includes three months of SDK access and
  a development unit at 50% off. After that, an **SDK Licence for internal apps** is €1,000 a year.
- **How the pipeline would work:** our Android app on the phone records video and audio from the
  glasses, tags each clip with the experiment ID, and uploads it (see [Wiring](#wiring-it-into-what-we-already-have)).
  Logs come from `adb logcat` on the phone. The glasses "hold no captured data", so nothing is
  stranded on them.
- **Unknowns to ask Iristick:** whether the SDK records the mic together with the camera stream,
  or we have to mux them ourselves; and whether the glasses show up as a standard USB (UVC)
  camera, which would let an existing streaming app use them without the SDK. Neither is documented.
- **Trying it:** #290's doc found a six-week trial for €1,000, which is deducted if you buy.
- **Older model:** the Iristick.G2 (€1,975, with 6x optical zoom and a hot-swap battery) is "no
  longer made, while stock lasts".

## 2. RealWear Arc 3: the most open

- **Hardware** ([specs](https://support.realwear.com/knowledge/arc3/specifications)): Ari OS 2.0
  (Android 13), a 48 MP main camera (82°) and an 8 MP wide camera (120°), 1080p60, four
  microphones with active noise cancellation, 179 g, a 2,000 mAh battery, IP54. "Compatible with
  prescription/safety glasses" and with hearing protection. It's driven by voice, so it works with
  gloves on.
- **Backdoor:** RealWear devices "ship by default with ADB enabled"
  ([ARI OS docs](https://developer.ari-os.com/device_docs/docs/Basics/enabling-developer-tools.md)),
  and capturing a bug report is a documented support step
  ([RealWear](https://support.realwear.com/knowledge/enabling-developer-options-and-capturing-a-bug-report-on-realwear-devices)).
  Over USB or Wi-Fi ADB:

  ```bash
  adb devices                          # the headset
  adb logcat -v time > session.log     # live logs
  adb shell ls /sdcard/DCIM/Camera     # recordings (path to confirm on a real unit)
  adb pull /sdcard/DCIM/Camera/<clip>.mp4 .
  adb bugreport bugreport.zip          # full diagnostics
  ```

  Any Android app can be installed with `adb install`, including a recorder of our own that talks
  to MQTT and uploads. RealWear documents no RTMP app, but standard Android streaming apps and
  libraries should work (untested). RealWear Cloud and the developer programme are optional.
- **Longevity:** RealWear is private, with a new CEO since January 2025. Current devices are
  supported to at least 2029–2030 and are due to move to Android 16
  ([policy](https://support.realwear.com/knowledge/realwear-firmware-update-and-support-policy)).
- **Sibling:** the **Navigator 520** (about $2,700–3,150) is the older 270 g boom headset, with a
  48 MP 1080p60 camera, a hot-swap battery and IP66. The Arc 3 is lighter and works over glasses,
  so it fits a lab better.

## 3. Pupil Labs Neon: provenance-grade

- **Hardware** ([specs](https://pupil-labs.com/products/neon/specs)): a scene camera at 1600×1200,
  30 Hz, 103°×77°; two eye cameras at 200 Hz; an IMU; stereo microphones recorded into the scene
  video. **Audio is off by default**, so switch it on in the Companion app
  ([docs](https://docs.pupil-labs.com/neon/data-collection/data-streams)). About 4 h of recording
  per charge. It runs from a supplied Android phone (Galaxy S25 or Moto Edge 40 Pro).
- **Frames and prices** ([shop](https://pupil-labs.com/products/neon/shop), EUR only): *Safety on*
  €6,460, *All clear* €6,510, *The goggles, they do everything* €6,405, *Better safe than sorry*
  €6,460, *Bare metal* €6,090 (the module alone, to build into our own eyewear). The shop page
  claims no safety rating. Per Pupil Labs'
  [frame guide](https://pupil-labs.com/blog/a-guide-to-neon-frames), *Safety on* uses Revision
  Sawfly lenses (rated Z87.1+ by Revision) and *All clear* uses ESS Profile NVG goggles (Z87.1-2015
  and EN 166 per a reseller). Ask Pupil Labs, and BYU's safety office, whether the assembled frame
  counts as eye protection. Pupil Labs offers academic pricing.
- **Backdoor** ([Realtime API](https://pupil-labs.github.io/pl-realtime-api/dev/guides/under-the-hood)):
  REST at `http://neon.local:8080/api`. It provides:
  - `GET /api/status` for battery, storage and sensors
  - `POST /api/recording:start` and `stop_and_save`
  - `POST /api/event` for event markers with nanosecond timestamps
  - a WebSocket status feed
  - RTSP for scene video, gaze, IMU and audio

  The Python package is `pupil-labs-realtime-api`. Everything works offline on a local network.
  Campus Wi-Fi may block the mDNS and UDP traffic it needs; a lab router or phone hotspot avoids
  that. Clock offset to a host computer is measured to the millisecond
  ([time sync](https://docs.pupil-labs.com/neon/data-collection/time-synchronization/)), which is
  the best timestamping of anything here.
- **Gaps:** full-quality recordings have to be exported in the app and copied over USB.
  Pupil Labs said in March 2026 that there is no API for exporting from the phone. The optional
  Pupil Cloud has a REST API, which would automate that step through their cloud. Live audio
  over RTSP is mono at 8 kHz, so use the exported file for anything archival.

## Under $500: Mentra Live (and the Meta glasses)

### Mentra Live ($449): the Meta-style glasses with a real backdoor

[Mentra Live](https://mentraglass.com/live) is camera-and-mic glasses in a normal frame (43 g,
1080p video, 3 mics). It costs $449 (it launched at $299 in January 2026) and ships in 2–5 business
days. Its OS, MentraOS, is open source under
[Apache-2.0](https://github.com/Mentra-Community/MentraOS). Its Bluetooth SDK
([camera and streaming docs](https://docs.mentraglass.com/bluetooth-sdk/camera-streaming.md)) can:

- stream to **our own ingest URL**, over `rtmp://`, `rtmps://`, `srt://` or WHIP. That covers
  YouTube's RTMP ingest and the stream cams' Lambda-issued URLs.
- upload photos and videos to **our own server** by webhook (multipart `video` + `requestId`)
- record until our app stops it. There's no length cap unless we set one.
- serve the gallery over the glasses' own Wi-Fi hotspot (`/api/gallery`)

The examples run video at 1280×720 and 30 fps. Mentra's docs also describe installing software
with ADB. The catches: about **1 h of recording per charge**, no safety rating, no prescription
option, and a small startup vendor. It's the cheapest way to prove the whole pipeline. Worn under
over-the-glasses goggles, it covers splash work too (see #290's doc).

### Idea 1: Meta glasses

| Model | Price | Native video | Works with the toolkit |
| --- | --- | --- | --- |
| Ray-Ban Meta Gen 2 | $379 | 3K30 or 1080p60, **3 min clips** | yes |
| Ray-Ban Meta Gen 3 | $449 | 12 MP, 3K; clip limit not stated | **not yet listed** |
| Oakley Meta HSTN | $399–479 | 3K30 or 1080p60, 3 min | yes |
| Oakley Meta Vanguard | $499 | centred camera, **5 min** at 1080p30 | yes |
| Meta Ray-Ban Display + Neural Band | $799 (the only one over $500) | 1080p30 (press reports) | yes |

- **Meta Wearables Device Access Toolkit** reached 1.0 on 2026-09-24
  ([changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)).
  - **What it gives us:**
    - our own iOS or Android app receives a live camera stream of **at most 720×1280**, at 2–30
      fps, "constrained by the Bluetooth Classic connection"
      ([docs](https://wearables.developer.meta.com/docs/develop/dat/streaming/))
    - photos
    - the mic over Bluetooth hands-free profile (about 8 kHz, per
      [MIXED](https://mixed-news.com/en/meta-dat-camera-720x1280-lower-resolution-higher-quality/))
    - battery and thermal state
  - **Who can install our app:** it can't go on the App Store yet, but invite-only test groups
    are allowed, which is enough for a lab app.
  - **What it can't do:** reach the native 3K recordings or the glasses' storage. It also sends
    usage telemetry to Meta unless we opt out.
- **No logs, no device management.** Meta documents no ADB or shell. Its FAQ says the glasses "are
  currently consumer devices and do not offer MDM support"
  ([Meta](https://www.meta.com/legal/ai-glasses/impact-grants-faq/)).
- **Files** leave the glasses only when the Meta AI app imports them into the phone's photo
  library. Auto-import is on by default. A script on an Android phone could pick them up from
  there, one 3–5 minute clip at a time.
- **No native livestream to YouTube.** Native livestreaming (Facebook and Instagram only) "was
  removed in the Gen 2 glasses"
  ([Meta community manager](https://communityforums.atmeta.com/discussions/ai-troubleshooting/instagram-live/1357087)).
  Custom RTMP goes only through a toolkit app, at 720p.
- **Not eye protection.** Meta says they "must not be used as safety glasses or protection
  against mechanical impact" ([Meta](https://www.meta.com/legal/ai-glasses/health-and-safety-warnings/meta-glasses/)).
- A researcher has run her own code on the glasses by bypassing Meta's signature check
  ([Malwarebytes, 2026-11-10](https://malwarebytes.com/blog/news/2026/11/researcher-bypassed-meta-smart-glasses-safeguards-to-run-her-own-code)).
  That is an exploit, not a supported backdoor, so don't build on it.

**Verdict:** best picture and comfort, but the least access. Good for short clips, not as a
provenance record.

## Everything else considered

| Device | Price | Safety | Backdoor | Verdict |
| --- | --- | --- | --- | --- |
| [Vuzix M400](https://www.vuzix.com/collections/smart-glasses) | $1,499.99 | none; Vuzix's $29.99 safety-frame kit has no Z87.1 statement found | Android 13, ADB (off by default, [switch on](https://support.vuzix.com/docs/enable-adb-debugging-on-the-vuzix-m400-m4000)), standard camera APIs | cheapest open Android with 4K autofocus and 3 noise-cancelling mics. Monocular display arm. Vuzix had $17.3M cash against a $7.7M quarterly loss ([Q2 2026](https://www.sec.gov/Archives/edgar/data/0001463972/000110465926097887/tm2623396d1_ex99-1.htm)) |
| Vuzix LX1 | $2,199.99, sold out | none | Android 15, ADB | as M400, 10 h battery |
| Vuzix Shield / Blade 2 | about $2,500 / about $1,300 | ANSI Z87.1 | Android 11 | Shield's 2026 availability unverified. **Blade 2 was listed discontinued by CDW in July 2024**, so treat #290's reseller price as old stock |
| RealWear Navigator 520 | about $2,700–3,150 | none | as Arc 3 | heavier boom headset; Arc 3 is the better fit |
| [RayNeo X3 Pro](https://rayneo.gitbook.io/rayneo-devdoc/chang-jian-wen-ti/adb-tiao-shi/adb-lian-jie-ji-tou-ping) | $1,299 | none | Android, ADB switch | only about 30–36 min of video per charge |
| [Viture Helix](https://www.prnewswire.com/news-releases/viture-unveils-helix-the-first-ai-safety-glasses-built-on-nvidias-xr-ai-solution-at-awe-2026-302802005.html) | from $600 | "engineered to ANSI Z87.1-2025", certification pending | no SDK; streams to a hosted AI service | **watch**: aimed at wet labs, pilots at Stanford and Princeton, ships Q1 2027 |
| [Viewpointsystem VPS Next](https://www.viewpointsystem.com/vps-produkte/vps-next/) | from $5,040 | SAFETY variant to EN ISO 16321 | "standardized API", undocumented publicly | ask for API docs and a trial |
| [Tobii Pro Glasses 3](https://www.tobii.com/products/eye-trackers/wearables/tobii-pro-glasses-3) | quote only (likely over $10k) | none | free REST, WebSocket and RTSP API, SD card | open, but mono mic, 105 min batteries, price |
| Tobii Glasses X | quote | none | data goes to Tobii's cloud and needs a subscription | fails the backdoor requirement |
| Meta Aria Gen 2 | not for sale | none | excellent ([client SDK](https://facebookresearch.github.io/projectaria_tools/gen2/ark/client-sdk/cli-reference)) | research partners only, by application |
| [Android XR glasses](https://www.androidpolice.com/samsung-android-xr-glasses-pre-order-start/) (Samsung/Google; Warby Parker and Gentle Monster frames) | $395–489 | none | standard Android camera APIs from a phone app; SDK in developer preview | **watch**: preorders opened 2026-11-12, ship 2026-12-10 |
| Rokid AI Glasses Style / Rokid Glasses | $299 / $699 | none | camera access in its SDK unconfirmed | 10 min clips |
| HTC Vive Eagle | $499 | none | no SDK found | |
| Solos AirGo V2 | $299 | none | SDK costs $1,999, features unpublished | |
| Snap Specs | $2,195, preorder | none | Lens Studio camera API, not built for recording | |
| Brilliant Labs Halo | $299–399 | none | open source | camera is a low-power AI sensor, not for video |
| Lucyd Armor | $149 | ANSI Z87.1 | — | no camera |
| HoloLens 2, Magic Leap 2, ThinkReality A3, Epson Moverio | — | — | — | discontinued |

## Wiring it into what we already have

Whichever device wins, most of the lab end of the pipeline is already built. Only the first hop
changes from device to device.

```
 glasses ──(adb pull / our SDK app / phone gallery)──► lab PC or Pi ──► sha256 + ffprobe
    │                                                       │
    │                                                       ├─► youtube/yt_service.py upload  (private, upload-only token)
    │                                                       │        └─ returns video_id ─┐
    │                                                       └─► MongoDB digital-wetlab ◄──┘  one metadata document per clip
    │
    └──(live) RTMP ──► YouTube Live, as the stream cams do (streamingLambda creates the broadcast)
```

- **YouTube, recorded.** [`youtube/yt_service.py`](../youtube/yt_service.py) already does
  resumable uploads to the lab channel with the upload-only token, for example
  `python youtube/yt_service.py upload clip.mp4 --title "..."`. Uploads land as private, which
  is the right default for footage of people at work.
- **YouTube, live.** The stream cams get a broadcast and an RTMP ingest URL from
  [streamingLambda](https://github.com/vertical-cloud-lab/streamingLambda) and push to it with
  ffmpeg ([`stream-cams.md`](stream-cams.md)). Any device above that accepts a custom RTMP URL
  can be given the same URL: Mentra natively, RealWear and Vuzix through an Android app, Neon
  through an `ffmpeg` relay of its RTSP stream. The Lambda files broadcasts into playlists by
  substring match on the workflow name, so pick a name that matches nothing else
  ([Renaming the workflow](stream-cams.md#renaming-the-workflow)).
- **MongoDB holds metadata, not video.** `digital-wetlab` is on Atlas's free tier, which has a
  hard limit of **512 MB** of data plus indexes, and 10 GB of transfer each way per rolling week
  ([MongoDB](https://www.mongodb.com/docs/atlas/reference/free-shared-limitations/)). One 1080p
  clip can be larger than the whole quota. So store one small document per clip:
  - experiment ID, wearer, device
  - start and end in UTC
  - the file's SHA-256 and size
  - the YouTube video ID
  - the session's device log lines or status snapshots

  Follow the `sensor-data` convention: `timestamp` is when it was recorded, `stored_at` when it
  was written.
- **Keep the original file.** YouTube re-encodes everything it receives, so a hash only proves
  something while the original exists. Keep originals on lab storage (OneDrive, Box), or deposit
  them with a dataset on Zenodo, and record in the MongoDB document where they are.
- **Clocks.** Stamp the clip with UTC from whatever starts the recording, and check it against
  the lab clock. Neon measures the offset for you. The stream cams burn lab local time into the
  frame for exactly this reason.

## Before buying

1. **Decide who answers on eye protection.** Ask BYU's safety office (EHS) whether a given
   combination counts as eye protection for the tasks being filmed. The combinations are:
   - Iristick's own certification
   - Arc 3 over the lab's own Z87.1 glasses
   - Neon in a frame built on rated eyewear
   - any glasses under over-the-glasses goggles

   Splash work needs goggles whatever is chosen.
2. **Try before buying.** Iristick's six-week trial (€1,000, deducted if you buy) can run alongside
   its SDK Developer Package. Ask RealWear and Pupil Labs for a demo or evaluation unit. A $449
   Mentra Live is cheap enough to prove the upload pipeline end to end first.
3. **Recording people.** Every device here has a recording light. Tell people in the room when
   you're recording, keep uploads private, and check BYU's policy on recording audio.

## How this was gathered

Web research on 2026-11-12, run as three parallel searches: consumer glasses, safety-rated
industrial glasses, and research eye trackers. Each search was told to cite a source for each
claim and to flag what it couldn't verify. The following were then **re-checked on the maker's own
page** the same day:

- Iristick.G3's certifications, cameras, microphones, weight, phone requirements and price
- the Iristick SDK's features, prices and licence terms
- RealWear Arc 3's specs and its compatibility with safety glasses
- Pupil Labs Neon frame prices
- Mentra's custom-ingest streaming and server upload
- Meta's 720×1280 streaming limit
- MongoDB's free-tier limits

Everything else is as reported by the linked source. vuzix.com and shop.realwear.com refused
most automated requests, so their prices come from resellers or search-engine copies.
USD conversions use 1.1222 USD/EUR (9 Nov 2026) and leave out VAT and US tariffs.
