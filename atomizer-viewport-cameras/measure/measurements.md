# rePowder viewing windows: dimensions from training-video frames

Machine coordinates as in `viz3d/model.py`: x to the right (operator facing the front), y away from the operator,
z up from the floor, furnace axis at x = y = 0, chamber front face at y ≈ −120.

**How the numbers were made.** All pixel spans were read off 720p and 1080p frames. Nothing was measured with a rule.
None of the documented sizes (HMI, KF50, feet) appears in the same plane as a window, so the absolute scale comes
from the furnace body Ø270. That number is the model's own estimate, scaled from the documented envelope. It was
re-checked here against the crucible bore: in `ref_58wJ_Khwgyk_7620.jpg` the body's sealing rim is about 3.7× the
crucible hole (Ø57.1), which gives a rim of about Ø210 and a body of about Ø250–270. Treat the body as Ø270 ± 10 %.

Every window sits nearer the camera than the body's silhouette, by 100–200 mm, so its pixels were corrected for
perspective. Camera distances came from the body's pixel width and an assumed horizontal field of view of 60–80°
(phone, collar and head cameras). That correction is 15–25 %, and it is the largest source of error. Each value
therefore has two or three independent estimates where possible: the body scale, ratios inside the part itself, and
hardware assumptions such as screw heads and star knobs. The ± figures span those estimates. Where a number rests on
one weak estimate it is marked *(weak)*.

## 1. Front view port (chamber front face, upper left, under the furnace)

| Dimension | Value | ± | Frame(s) | Reference | Notes |
|---|---|---|---|---|---|
| What the grey ring is | AMAZEMET LED illuminator cover | — | `58wJ_Khwgyk` 25:11, `FDRTt68Vfvo` 51:00, `1F9_4ccwhss` 7:49 | — | 3D-printed-looking matte dark-grey low-poly shell with 12-fold symmetry and "AMAZEMET" embossed on its rim. A white LED ring glows round the glass (bright ring in 25:11; the lit 12-gon seen from the inside at `DWH1CEygsTI` 34:28). It pushes on over the port nut and the operator pulls it off by hand (`1F9` 7:49), leaving the bare port (`1F9` 7:58). **Not a phone holder.** |
| Small faceted piece with black cable | LED/cable "pod" | ~90 × 55 × 45 mm, ±30 % | `FDRTt68Vfvo` 51:00, `58wJ_Khwgyk` 28:18 | hood width | Same low-poly style, fixed to the hood, with a cable gland on one end and one black round cable (≈Ø6–8) running down. At 3 o'clock on 29 Sep (gland pointing down), at 6 o'clock from 30 Sep to 6 Oct (gland pointing left). Hood and pod turn together, so the cover can sit at any angle on the port. |
| Clear glass diameter | 63 mm | ±12 | `FDRTt68Vfvo` 51:00, `58wJ_Khwgyk` 25:11, `1F9_4ccwhss` 7:58 | glass/hood 0.34 → 0.38 after depth correction; glass/nut 0.67 | Hardened glass (trainer, 25:10); blue gasket visible at its edge (`1F9` 7:58). |
| Threaded retaining nut OD (hook-wrench ring) | 95 mm | ±15 | `1F9_4ccwhss` 7:58 | glass/nut ratio; star knob in the same frame (if Ø40–50) | Polished round union nut on a short stub, chamfered front edge. Looks like a dairy-fitting (DIN 11851-style) sight glass; a DN50 nut is ≈Ø92. **Notch count not resolved:** the polished ring is too small in the frame. |
| Hood across corners (12-gon) | 168 mm | ±25 | `FDRTt68Vfvo` 51:00 (235 px), `2wMgeI-E7zw` 10:00 (200 px) | body Ø270, perspective-corrected (raw body-plane scale gives 201–205 mm, an upper bound) | Across flats ≈ 162 mm (×cos 15°). Model has 180. |
| Hood front opening (inner 12-gon at its front face) | 75 mm | ±15 | `58wJ_Khwgyk` 25:11 | 0.45 × hood | Inner faceted cone narrows toward the glass. |
| Hood front face, distance in front of chamber face | 75 mm | ±25 *(weak)* | `wRc8p2_FnJo` 35:10, `1F9_4ccwhss` 7:49 (side views) | hood OD | Stub + nut + hood overhang. Needs a tape. |
| Port centre: right of chamber's left face | 100 mm (x ≈ −15) | ±25 | `FDRTt68Vfvo` 51:00 | front-face scale | Hood centre is ~20 mm left of the furnace axis; its left edge is flush with the chamber's left edge. |
| Port centre: below chamber top | 95 mm | ±30 | `FDRTt68Vfvo` 51:00, `2wMgeI-E7zw` 10:00 | as above | The hood's top edge reaches about the top-plate level. |
| Port centre height above floor | 1035 mm | ±40 | as above | chamber top z = 1130 (model) | Model: 1030. |
| Axis tilt (down toward plate) | ~20° down | ±12 *(weak)* | `DWH1CEygsTI` 34:28 (view through the port: plate in the upper part, catch bowl at the bottom) | geometry: port → plate | The hood's foreshortening is not clean enough to measure. Measure with a phone inclinometer on the glass. |
| Clearance hood top → furnace foot bracket | ~20 mm | ±15 | `FDRTt68Vfvo` 51:00, `2wMgeI-E7zw` 9:29 | — | Projected gap. The furnace body itself is ~100+ mm behind the hood face. |
| Top-front star knob, left of hood's left edge | ~50 mm | ±20 | `FDRTt68Vfvo` 51:00, `58wJ_Khwgyk` 28:18 | — | At about hood mid-height, on a swing bolt from a bracket on the front face's left edge. |
| Lower-front star knob, below hood bottom | ~110 mm | ±30 | `FDRTt68Vfvo` 51:00 | — | Second swing bolt; a third is at the door's bottom. |

**What a mount must clear.** The port sits in the top-left corner of the front face. The hood's left edge is flush with
the chamber's left edge, and its top reaches the top-plate level, ~20 mm under the furnace's front-left foot bracket.
About 50 mm to its left, at mid-height, is the top door clamp. That is a swing bolt with a black star knob, pivoting on
a bracket on the front face's left edge; it swings forward and left to release the door. Directly below is the LED pod
with its cable, which on the current setup hangs at 6 o'clock. About 110 mm below the hood is the second swing bolt
and knob. The front face to the right is clear for ~250 mm (vertical slots and the aus500 label only). The furnace body
is ~100 mm behind the hood face, above it. A camera can either replace the AMAZEMET cover or clip onto its 12-sided
rim. The rim is the easier datum: it is removable by hand, rotatable, and keeps the LED. A mount must leave the
top-left swing bolt free to swing and must not load the glass nut (hook-wrench removable).

**Phone holder.** None was found on this port in the cached frames from 2 Oct (`qYyT39D5Yzo`, `of5-LhkX_VQ`) or 6 Oct
(`VFycaxIq0Tc`, `dnPs56DPt6I`, `DWH1CEygsTI`, including a newly fetched 34:05–34:45 window). The recording phone was a
collar camera (VFyc 1:28), and the checklist phone lay on the chamber deck (`DWH1` 28:50, `of5` 27:20). The trainer only
says "I saw some people putting like a phone holder here" (`58wJ` 28:29–28:32).

## 2. Left-side port (small sight glass on the door)

| Dimension | Value | ± | Frame(s) | Reference | Notes |
|---|---|---|---|---|---|
| Visible glass diameter | 45 mm | ±12 | `58wJ_Khwgyk` 77:25 (70 px vertical), `9kn-HhXCr1o` 25:06 | hood OD in the same frame, depth-corrected; ring/glass 0.74 | Seen almost edge-on in every frame. No frame looks straight at the left face. |
| Ring/nut OD | 65 mm | ±15 | as above | as above | Polished round ring with a nut-like edge. Can't tell from the frames whether it is an ISO-KF clamp flange. If KF, KF40 (OD 55; clamp ≈70) fits better than KF50 (75). It could equally be a small threaded (DIN 11851-style) sight glass like the front one. Check for wrench notches versus a wing-nut clamp. |
| Protrusion from door outer face | 30 mm | ±10 | `9kn-HhXCr1o` 25:06 (profile, 32 px) | ring OD | |
| Centre height above floor | 1015 mm | ±50 | `9kn-HhXCr1o` 25:06 | ring OD; door bottom z ≈ 775 (model) | ~130 mm above the stack's entry on the door, ~75–100 mm below the door top. Model: 1060. |
| Fore-aft (y) | ≈ +20 mm | ±50 *(weak)* | `58wJ_Khwgyk` 77:00, 77:25 | — | Upper part of the door, above the stack entry, between the door's middle and its back (hinge) edge. Model puts it at y = −45. |
| Door hinge | back edge (+y) | — | `58wJ_Khwgyk` 24:54, `1F9_4ccwhss` 7:49, `FDRTt68Vfvo` 51:00, `58wJ` 77:25 | — | All three swing bolts anchor on the front face's left edge (two) or under the door, and the open door stands out from the opening's back edge with its inner face toward the operator. The model hinges it at the front edge, which looks reversed. |

**Room for a camera and small display.** Probably yes, above the stack. The stack leaves the door ~130 mm below the
glass and runs outward and down at 40°, so clearance grows with distance from the door. Its KF clamp carries a black
wing knob ~100–150 mm out and below. The top door clamp is at the front edge at about the glass's height, so its
swing must stay free. The door swings forward on a back-edge hinge, so anything on it moves with it, and the glass near
the hinge sweeps a small arc. A camera body ≤ 60–80 mm outboard of the glass, plus a display ≤ ~100 mm, looks
feasible without blocking the opening or the stack. Confirm with a tape: the blue frame side panel is just behind the
door's back edge (`58wJ` 77:25), which limits anything that overhangs the hinge.

## 3. Top window (furnace lid / "bell")

| Dimension | Value | ± | Frame(s) | Reference | Notes |
|---|---|---|---|---|---|
| Window shape | rectangle, small corner radii (~5 mm) | — | `58wJ_Khwgyk` 58:06, `DWH1CEygsTI` 25:40, `of5-LhkX_VQ` 24:18 | — | Glass-ceramic (trainer, 25:22). A "⚠HOT⚠" print runs along its lower edge. Indutherm parts C015/C016 (frame/glass). |
| Clear opening W × H (H along the slope) | 60 × 64 mm | ±12 each | `58wJ` 58:06 (face-on, 440 × 465 px), `DWH1` 25:40 (208 × 208 px), `1F9` 5:05 (from inside) | lid skirt Ø275 depth-corrected (52); screw heads M5–M6 (49–62); open-lid rim (66) | Model: 70 × 54. |
| Frame plate | ~112 mm wide at top screw row, flaring to a ~140 mm arc at the bottom; ~105 mm along slope | ±20 | `58wJ` 58:06, `DWH1` 25:40, `of5` 24:18 | window size | Polished stainless plate on the front facet. Its bottom edge follows the round shoulder of the lid. |
| Fasteners | 8 hex-socket screws (3 top, 2 sides, 3 bottom), likely M5 | — | `DWH1` 25:40, `58wJ` 58:06 | — | Top-row pitch ≈ 48 mm (±10). |
| Glass recess / plate height | glass ~4 mm below plate face; plate ~4 mm proud of facet | ±2 each | `DWH1` 25:40, `of5` 24:18 | — | A bevelled step round the opening. Not flush. |
| Facet orientation | faces front (−y), inclined ~50° from horizontal | ±15° *(weak)* | `9kn` 20:04, `DWH1` 25:40, `wRc8p2` 35:10, `58wJ` 58:06 | — | Operator at the front-left looks down through it at the crucible. |
| Lid lower part | round skirt, Ø ≈ 275 mm (≈ body Ø) | ±25 | `DWH1` 25:40, `wRc8p2` 35:10 | body | Round, not hexagonal as in the model. Upper part is a ~6-facet pyramidal frustum with a small flat top. |
| Lid height above body top | ~150 mm | ±30 | `wRc8p2` 35:10, `1F9` 5:16 | body | |
| Lid top above floor | ~1500 mm | ±60 | as above | body top z = 1345 (model) | |
| Window centre | z ≈ 1455, y ≈ −95 | ±60, ±25 | as above | | |
| Hinge | left side (x ≈ −160), pin axis along y, at about the lid/body joint (z ≈ 1345) | ±20, ±30 | `DWH1` 25:40, `1F9` 5:05, `2wMgeI` 10:00 | — | Over-centre draw latch on the right/front-right of the body. Black ball knob (≈Ø25–30) on a stem on the lid's right side. |
| Opening swing | up and over to the left, ~105° (stands just past vertical) | ±10° | `1F9` 5:05, `2wMgeI` 10:00 | body Ø270 | Open lid occupies x ≈ −310…−135 and reaches z ≈ 1610 (±50). Anything mounted on the lid must clear that arc, and the cables and blue frame on the left. |

**Around the lid.** Behind it is the blue cabinet face, close behind the furnace. The Indutherm GU 500 AMA keypad
panel is on that face to the right and behind, at about lid height. The Weintek HMI hangs on its arm further right and
forward. The sealing-rod lever post is on the deck to the right (+x), under the lid, and the coil leads and cables
leave the furnace on the left. Nothing is directly above the lid, but anything mounted on the lid swings with it to the
left when it opens. A fixed camera looking down at this window has to sit in front of and above it, along the facet's
normal. That point is at about z 1.55–1.65 m and y −250 to −350, from where the operator also looks. It must also clear
the lid's opening arc on the left.

## Still unknown: measure with a tape

1. Front port: glass clear Ø, nut OD and notch count, how far the hood face stands off the chamber face, the port
   axis's tilt (inclinometer on the glass), and the hood's inner bore where it grips the nut.
2. Hood: true across-flats and across-corners, depth, the pod's size and position, and the LED cable route and plug.
3. Front port position: centre height above the floor, and distance from the chamber's left edge and top.
4. Left sight glass: glass Ø, ring OD, its type (KF clamp or threaded nut), protrusion, centre height, and distance
   from the door's back edge.
5. Door: hinge side (back edge, per the frames above; the model says front), its opening angle, and the swing
   envelope of the three star-knob bolts.
6. Top window: opening W × H, frame-plate outline and screw positions, facet angle, and window centre height.
7. Lid: skirt Ø, total height, hinge-pin position, opening angle and swept envelope.
8. Global scale: the furnace body Ø (assumed 270) and the chamber top height (assumed 1130). Every absolute number
   above scales with these.
