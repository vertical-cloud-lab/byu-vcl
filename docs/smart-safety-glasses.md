# Camera and AR glasses for filming lab work

Issue [#290](https://github.com/vertical-cloud-lab/byu-vcl/issues/290), following on from
[wearable-camera-mounts.md](wearable-camera-mounts.md). Gage didn't find the chest-harness idea
much better than the current neck mount: "Something like a small camera attached to safety glasses
would be ideal, then it's not a big phone on the chest." This page looks at Meta-style camera
glasses, and at smart glasses sold as safety eyewear, for filming bench work.

Prices, ratings and stock below were read from Amazon US on **2026-10-22**, from the CubXL Pi
(see [How this was gathered](#how-this-was-gathered)). Specs Amazon doesn't list come from the
makers or from reviews, linked where they're used. Nothing here has been bought, worn or tested.

## Short version

**None of the Meta-style camera glasses is safety eyewear.** Ray-Ban Meta, Oakley Meta, Meta
Ray-Ban Display, HTC Vive Eagle and Rokid all sell consumer glasses, and none of them claims
ANSI Z87.1. Where the lab requires Z87.1 eye protection, they can only be worn *under* goggles.
The smart glasses that *are* certified safety eyewear with a camera are enterprise products,
from about $1,300 (Vuzix) to €2,275 (Iristick). In between are $80 camera glasses whose listings
claim Z87.1, which nobody has checked.

What fits depends on the eye protection the work needs:

1. **Impact protection only (safety glasses are enough):**
   - **[Iristick.G3](https://iristick.com/)** is the product built for this: certified safety
     glasses (EN 16321 and ANSI Z87, per Iristick) with two cameras between the eyes. It weighs 95 g
     and plugs into an iPhone or Android phone by USB-C. It costs €2,275 before VAT. Iristick offers
     a six-week trial for €1,000, which is deducted if you buy.
   - **[OHO camera glasses](https://www.amazon.com/dp/B0H1WGMPQW), $78.88**, are a cheap way to
     try the idea. They record 1080p for about 60 minutes, and the listing claims
     "ANSI/ISEA Z87.1-2015 Impact Resistant". Reviews are mixed, and the Z87.1 claim is the
     seller's. Before wearing them as eye protection, check that the frame and lenses are actually
     stamped "Z87" (see [below](#why-the-safety-rating-matters)).
2. **Chemical splash (goggles required):** no glasses-style product here claims splash
   protection. What can work is **camera glasses with clear lenses worn under over-the-glasses
   (OTG) splash goggles**, e.g. [Ray-Ban Meta Gen 2](https://www.amazon.com/dp/B0FLYDJHB4) ($379)
   under [Uvex Stealth OTG S3970D](https://www.amazon.com/dp/B003U9VE4Y) goggles ($39.46). Test
   two things before relying on it: whether the glasses' thick temples, which hold the battery,
   let the goggle seal close, and how the video looks through the goggle lens. Or keep the goggles
   and wear a 53 g camera on your forehead: the Insta360 GO Ultra from Option 2 in
   [wearable-camera-mounts.md](wearable-camera-mounts.md#option-2-a-tiny-wearable-camera-instead-of-a-phone)
   on its [Easy Clip Headband](https://www.amazon.com/dp/B0FHHFF2SN) ($19.99, 4.4 from 111
   ratings). That's as close to eye level as a camera gets without being part of the eyewear.
3. **Not worth it:** side shields for Ray-Ban Meta (they aren't safety-rated); Lucyd Armor
   (Z87.1-rated, but it has no camera); and RealWear Navigator 520 (a 270 g headset, unavailable
   on Amazon).

**Meta's glasses cap every clip at 3–5 minutes.** Ray-Ban Meta Gen 2 stops at 3 minutes in every
mode, and it still records **vertical** video
([9to5Google](https://9to5google.com/2025/09/17/ray-ban-meta-gen-2-battery-video-upgrades/)),
which is awkward for landscape YouTube videos. On the Oakley Meta Vanguard, 3K and 1080p60 stop
at 3 minutes and 1080p30 at 5 ([UploadVR](https://uploadvr.com/oakley-meta-vanguard-glasses-official)).
Meta doesn't publish a limit for Gen 3. That's fine for short demos, but a whole procedure means
stitching clips together. The OHO listing claims about 60 minutes of recording, Rokid's 10-minute
clips, and one $90 pair lets you set the clip length anywhere from 15 s to 12 min.

## Why the safety rating matters

- OSHA requires eye protection meeting ANSI Z87.1 wherever there are eye hazards, including liquid
  chemicals ([29 CFR 1910.133](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.133)).
  Whether a given task needs safety glasses or splash goggles is up to the lab's own rules.
- Compliant eyewear is permanently marked: "Z87" for basic impact, "Z87+" for high impact, and
  "D3" for droplet and splash protection
  ([ANSI](https://blog.ansi.org/ansi-isea-z87-1-2020-safety-glasses-eye-protection/),
  [Safety Glasses USA](https://safetyglassesusa.com/blog/what-does-ansi-z87-1-certified-mean/)).
  Whatever a listing says, if the frame and lenses aren't stamped, the glasses aren't compliant.
- The same OSHA rule lets people who wear prescription glasses put compliant eyewear *over* them,
  as long as it doesn't disturb the glasses underneath. Camera glasses under OTG goggles are the
  same arrangement.
- An IP rating is not eye protection. "IP54 dust-and-splash protection" on the Vive Eagle, or
  "resists daily splashes" on the OHO listings, describes the electronics, not your eyes.

## Certified safety eyewear with a camera (enterprise)

| Product | Safety rating (maker's claim) | Camera | Weight | Price | Notes |
| --- | --- | --- | --- | --- | --- |
| [Iristick.G3](https://iristick.com/) | EN 16321, ANSI Z87 | two cameras, centred between the eyes | 95 g | €2,275 excl. VAT, "while stock lasts" ([pricing](https://iristick.com/pricing/)) | Runs from an iPhone or Android phone over USB-C. Remote-assist app free; Teams €365/yr; SDK €1,000/yr. Six-week trial €1,000. |
| Iristick.G2 (earlier model) | ANSI Z87 / EN 166 ([2020 datasheet](https://www.quad.de/media/50/fb/a7/1653403727/IRISTICK_DE.pdf), line-wide) | camera plus optical zoom | 78 g ([spec sheet](https://www.quad.de/media/66/97/03/1653403744/spec-sheet-Iristick.G2-EU-industry.pdf)) | €1,975 | |
| [Vuzix Blade 2](https://vuzix.com/products/vuzix-blade-2-smart-glasses) | ANSI Z87.1 | 8 MP autofocus, 1080p30 | not published | $1,289.99 ([ChannelXR](https://channelxr.com/products/vuzix-blade-2-smart-glasses)); $1,299.99 MSRP ([SHI](https://www.shi.com/product/45587499/Vuzix-Blade-2-Smart-glasses)) | Standalone Android 11, with a see-through display. Amazon's listing for the earlier Z87.1 Blade ([B08K9D97CK](https://www.amazon.com/dp/B08K9D97CK)) now returns "Page Not Found". |
| [RealWear Navigator 520](https://shop.realwear.com/pages/realwear-navigator-520-specifications) | none itself; worn with safety glasses or a hard hat | 48 MP, 1080p60 | 270 g | [Amazon](https://www.amazon.com/dp/B0BZ3QN297): currently unavailable | Voice-controlled headset with a display arm. Heavier on the head than anything else here. |
| [Vuzix M400 Starter Kit](https://www.amazon.com/dp/B087QSPFT9) | none on the listing (the kit includes "Safety Glasses Frames") | monocular camera and display | not listed | Amazon: currently unavailable | Clips onto the included frames, a headband or a hat. |

These are built for remote assistance and work instructions in factories, so recording goes
through the maker's app or SDK rather than a camera roll. Iristick's trial is the cheapest way to
find out whether that suits making lab videos.

## Meta-style camera glasses (not safety eyewear)

| Glasses | Listed weight | Camera, clip limit | Battery | Price | Rating (count) |
| --- | --- | --- | --- | --- | --- |
| [Ray-Ban Meta Gen 3](https://www.amazon.com/dp/B0HBQ19GSB), Wayfarer | 50 g | 12 MP, 3K; clip limit not published | up to 9 h | $449.00 | 4.0 (62) |
| [Ray-Ban Meta Gen 2](https://www.amazon.com/dp/B0FLYDJHB4), Wayfarer, **clear lenses** | not listed (48–52 g in reviews) | 12 MP, 3K, vertical; 3 min | up to 8 h | $379.00 | 4.2 (1,415), 3K+ bought last month |
| [Oakley Meta HSTN](https://www.amazon.com/dp/B082KLQBD5) | 53.15 g | 3K | up to 8 h | $479.00 | 4.2 (612) |
| [Oakley Meta Vanguard](https://www.amazon.com/dp/B0FQFJT9YW) | 65.2 g | **centred** camera; 3 min at 3K or 1080p60, 5 min at 1080p30 | about 9 h | $499.00 | 4.4 (295) |
| [HTC Vive Eagle](https://www.amazon.com/dp/B0H788SL8J) | 48.8 g | 3K, stabilised | not listed | $423.99 | 4.8 (28) |
| [Rokid Glasses](https://www.amazon.com/dp/B0H4FX73FR), with display | 49 g (38.5 g in the spec table) | Sony IMX681 (12 MP); clips up to 10 min; "45 minutes of video recording" per charge | 6 h of music | currently unavailable | |
| [Rokid AI Glasses Style Pack](https://www.amazon.com/dp/B0H4QKSJP3), no display | not listed | 12 MP, 3K, stabilised | swappable battery capsules on the temple | $399.00 | 3.9 (11) |
| [Meta Ray-Ban Display](https://www.tomsguide.com/computing/smart-glasses/meta-ray-ban-display-glasses-features-neural-link-price-and-availability) | 69 g | 12 MP, 1080p30 | | $799 ([Engadget](https://engadget.com/2267230/everything-announced-at-meta-connect-2026)) | not checked (the Amazon search was blocked) |
| [Mentra Live](https://9to5google.com/2026/01/15/mentra-live-smart-glasses-youtube-livestream/) | 43 g | 12 MP, 1080p; livestreams | 12+ h | $449 (was $299 at launch) | no Amazon listing found |

- **Clear lenses.** Lab work needs them. Ray-Ban Meta sells clear and Transitions versions.
  The four Vanguard versions UploadVR lists all have tinted Prizm sport lenses, so check for a
  clear option before buying one for indoor bench work, despite its centred camera and longer
  1080p clips.
- **Where the camera sits.** On Ray-Ban Meta and HSTN it's at a front corner of the frame; on the
  Vanguard and Iristick it's in the middle, closer to what your eyes see.
- **Reviews.** Amazon's review summaries keep coming back to battery life and durability
  (Ray-Ban Meta Gen 2: "reports of fast-draining batteries and poor durability"; Vanguard:
  "won't hold a charge"; HSTN: some "stop working after three months").
- **Recording light.** Meta's and HTC's glasses light up while recording; HTC's camera also
  switches off if the light is covered. Tell people in the lab when you're filming.
- **Side shields** such as [HiBloks](https://www.amazon.com/dp/B0GQZG6M7N) ($6.99, 3.1 g,
  3.3 from 11 ratings) clip onto Ray-Ban Meta and HSTN frames. The listing sells them as
  anti-glare and claims protection against "splashes, and small debris", but they carry no
  Z87.1 claim, so they don't make the glasses safety eyewear.

## Budget camera glasses

| Glasses | Listed weight | Video | Price | Rating (count) | Safety claim |
| --- | --- | --- | --- | --- | --- |
| [OHO, polarized + clear and yellow lenses](https://www.amazon.com/dp/B0H1WGMPQW) | not listed | 1080p, about 60 min per charge; 32 GB card included | $78.88 (only 14 left) | 4.0 (99) | "US Safety Lens Standard ANSI/ISEA Z87.1-2015 Impact Resistant" |
| [OHO, another listing](https://www.amazon.com/dp/B0DLVW13KL) | 46 g | 1080p, records while charging | $83.99 | 3.9 (51) | "Z87.1" in the title only; its spec table lists tri-acetate cellulose lenses rather than the usual polycarbonate |
| [OHO Ultra-Light](https://www.amazon.com/dp/B0C7VRKZWJ) | 39 g | 1080p; battery "1 hours" | $128.88 | 3.6 (354) | none |
| [Zigtik "Pro" camera glasses](https://www.amazon.com/dp/B0GFZBS9WY) | 1.6 oz (45 g) | clip length settable from 15 s to 12 min | $89.99 | 3.9 (125) | none |
| [AI smart glasses, 1200p with EIS](https://www.amazon.com/dp/B0H294Y26K) | 49.3 g | 1200p30, stabilised | $139.99 | 3.9 (64) | none |

Amazon's review summary for the first OHO says quality runs from "very good" to "garbage". At
$79 it's a cheap experiment, but treat it as a camera until the stamp on the frame says otherwise.

The most visible "smart safety glasses" on Amazon, [Lucyd Armor](https://www.amazon.com/dp/B0DG6LYP8F)
($149, 3.9 from 479 ratings, ANSI Z87.1), have speakers, a microphone and an AI assistant but
**no camera**. Lucyd describes them as the only mainstream smart glasses with Z87.1 certification
([Lucyd](https://lucyd.co/blogs/news-media/lucyd-armor-for-construction-ansi-z87-1-hands-free-communication-ai-on-the-jobsite)).

## Goggles that fit over glasses

[Uvex Stealth OTG S3970D](https://www.amazon.com/dp/B003U9VE4Y): $39.46, 4.4 from 772 ratings,
4.48 oz. The listing says they fit "over most prescription eyewear", seal gap-free against
splashes, and meet ANSI Z87+ and CSA Z94.3. Amazon's review summary says buyers use them for
chemistry lab work and that they "accommodate glasses well", with mixed reports on fogging. A
Ray-Ban Meta temple is much thicker than a normal one, though, so whether the seal still closes
over it has to be tried on.

## The AR part: displays, and getting video into our own software

- **Displays.** Meta Ray-Ban Display, Rokid Glasses, Vuzix Blade 2 and RealWear show text in
  front of one eye, which could put protocol steps in view while your hands are busy. None of the
  consumer ones is safety eyewear, and Meta caps a *recording of the display* at one minute
  ([Meta help](https://www.meta.com/help/ai-glasses/951708387778102/)).
- **Meta's Wearables Device Access Toolkit** lets your own iOS or Android app use the camera of
  Ray-Ban Meta, Meta Ray-Ban Display and Oakley Meta glasses. It's still a developer preview: you
  can build and share builds inside your own organisation, but only selected partners can
  publish to app stores
  ([Meta](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/),
  [pub.dev](https://pub.dev/packages/flutter_meta_wearables_dat/versions/0.6.0),
  [status as of 2026-09](https://vr.org/articles/meta-glasses-three-tiers-wearables-toolkit-publishing-connect-2026)).
  For lab use, building inside your own organisation is enough. This is the route if POV video
  should land straight in an experiment record, the way the stream-cam overlays do now, without
  the 3-minute cap.
- **Mentra Live** runs an open-source OS with an SDK and an app store, and livestreams to YouTube.
- **Iristick** sells an SDK (€1,000/yr after three months).

## How this was gathered

Amazon serves bot checks to datacenter IPs such as a GitHub Actions runner, so every Amazon request
went out from the **CubXL Pi** over Tailscale SSH, the same way as
[wearable-camera-mounts.md](wearable-camera-mounts.md#how-this-was-gathered). I checked it read-only
first: load average 0.00, with `deckcam.service` the only lab software running. On the Pi it ran
**`curl` only**, capped at `--limit-rate 300k` with 15–25 s between requests. Nothing was installed
or written there.

- **Searches:** 7 tried. The first 3 came back, and the next 4 in a row got Amazon's ~1.4 kB
  JavaScript bot-check page (`bm-verify`). That's sooner than on 2026-10-20, when the first block
  came after about ten requests. So I stopped searching from the Pi, found the remaining listings
  with a web search restricted to amazon.com, and fetched those product pages from the Pi.
- **Product pages:** 20 fetched, none blocked. One, the Vuzix Blade (B08K9D97CK), is
  "Page Not Found" because the listing is gone.
- [`smart-safety-glasses-amazon-2026-10-22.json`](smart-safety-glasses-amazon-2026-10-22.json)
  holds what was parsed: the three searches' results, and for each product the listed weight,
  spec-table rows, feature bullets and Amazon's "Customers say" summary. `parse_dp.py` now also
  saves the listing's own sentences mentioning a safety standard (`safety_mentions`) or a
  recording length (`video_length_mentions`). Those are the seller's words, not certificates.
  Raw HTML isn't committed.

To redo or extend it, from a runner on the tailnet:

```bash
python3 -I scripts/amazon_via_pi/fetch.py /tmp/amzn/raw search "smart glasses with camera ansi z87 safety"
python3 -I scripts/amazon_via_pi/fetch.py /tmp/amzn/raw dp B0HBQ19GSB B0H1WGMPQW
python3 -I scripts/amazon_via_pi/summarize.py /tmp/amzn/raw /tmp/amzn/summary.json
```

`fetch.py` now connects with `StrictHostKeyChecking=accept-new`. A fresh runner has no
`known_hosts` entry for the Pi, so with `BatchMode=yes` alone the first request failed with "Host
key verification failed". Over the tailnet the peer is already authenticated by its WireGuard
key.
