# Filming lab work from the wearer's point of view

Start here. Two issues worked on replacing the phone on a neck mount that many of the lab's videos
were shot with:

- [#290](https://github.com/vertical-cloud-lab/byu-vcl/issues/290), October 2026: something more
  comfortable. It was closed on 2026-11-28 as a duplicate of #342.
- [#342](https://github.com/vertical-cloud-lab/byu-vcl/issues/342), "Provenance Eyes", from
  November 2026: a head-worn camera and mic whose recordings upload themselves, with logs we can read.

As of 2026-11-28, nothing on these pages has been bought, built or worn.

| Question | Page | Short answer |
| --- | --- | --- |
| Is there a more comfortable phone mount? | [`wearable-camera-mounts.md`](wearable-camera-mounts.md) (#290) | No neck mount is lighter: they are 190–310 g before the phone goes on. Move the weight instead: a chest harness (about $25), or a 52–53 g camera on a magnetic pendant ($389–450). |
| Can we use a small camera on safety glasses? | [`smart-safety-glasses.md`](smart-safety-glasses.md) (#290) | None of the Meta-style glasses is safety eyewear. Certified glasses with a camera are enterprise products, such as the Iristick.G3 (€2,275). |
| Which devices let us read logs and automate uploads? | [`provenance-eyes.md`](provenance-eyes.md) (#342) | Over $500: Iristick.G3, RealWear Arc 3 and Pupil Labs Neon. Under: Mentra Live ($449). Meta's glasses give no logs. |
| Could we build one ourselves? | [`hardware/provenance-eyes/`](../hardware/provenance-eyes/README.md) (#342) | Yes: a Pi Zero 2 W head camera on $18.49 ratchet headgear, about $177 and 108 g of add-on parts. A button records; the clip goes to YouTube, and the transcript and analysis go to GitHub ([`SOFTWARE.md`](../hardware/provenance-eyes/SOFTWARE.md)). |
| What about full-face respirators and lab coats? | [`PPE.md`](../hardware/provenance-eyes/PPE.md) (#342) | No glasses can be worn with a full-face respirator. The Pi headset (v2) is worn like a cap, over the respirator's straps, with nothing cabled to the body. |
| Head-camera footage is shaky. | [`STABILIZATION.md`](../hardware/provenance-eyes/STABILIZATION.md) (#342) | Keep the shaky original as the record and make a steadied copy to watch. For training videos, add a steady second camera. |

## Which to use when

- **Training videos:** steadiness matters most. Use a chest camera, such as the pendant or a harness
  from [`wearable-camera-mounts.md`](wearable-camera-mounts.md), or a fixed camera at the bench.
  Add head-camera footage, steadied, for the moments when what the person looked at matters.
- **A record of what happened:** use a head camera. It shows what the wearer looked at, and the Pi
  headset uploads and logs everything without anyone touching a computer.
- **Days with a full-face respirator:** only something worn over the straps works, either the Pi
  headset v2 or a camera on a helmet ([`PPE.md`](../hardware/provenance-eyes/PPE.md#the-commercial-options-under-the-same-two-conditions)).
