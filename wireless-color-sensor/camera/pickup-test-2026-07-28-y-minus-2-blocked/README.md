# Y −2 mm re-run — BLOCKED: P20 replaced by a P300 on the left mount (2026-07-28)

Requested by @timothy-commins in PR #60: *"great job. the pick up spot is
close but not perfect. try the same test again but -2mm in the y direction"* —
i.e. re-run the raised-heights full cycle with the pickup/eject XY moved from
(171.05, **227.0**) to (171.05, **225.0**).

## Why no press-fit was attempted

On connecting (runner → Tailscale → RPi-5 → USB-Ethernet → OT-2 HTTP API) the
robot reported the left mount holds a **P300 single GEN2**
(`p300_single_v2.1`, serial `P3HSV212021083111`), right mount **empty**. Every
prior pickup session used the **P20 single GEN2**, and the module's crown
socket is the P20 geometry (3.40 mm bore). `loadPipette p20_single_gen2`
fails with *"p20_single_gen2 was requested but p300_single_v2.1 is present"*.

The P300 GEN2 nozzle is far larger than the 3.40 mm bore, so pressing it
7 mm into the crown (the recipe's mouth − 7 grip press) would not insert — it
would ram the module down and likely crack the printed crown. **No contact
was made.**

## What was done instead — no-contact Y-alignment hover

The P300 was loaded (it is what's physically attached) and hovered over the
crown at both Y values, closest approach z=102 (crown mouth is at 98.7 →
3.3 mm clearance), with a camera frame at each stop:

| frame | position |
|---|---|
| `00_baseline.jpg` | module seated in slot 8, crown up, nozzle parked |
| `01…z130 / 02…z110 / 03…z105` | approach ladder at the old y=227.0 |
| `04…z105 / 05…z102` | shifted to the requested **y=225.0** |
| `06…z102` | back at y=227.0, same height, for direct comparison |
| `07_final_homed.jpg` | gantry homed, module untouched |

The 05 vs 06 pair is the useful evidence: same x/z, y differs by exactly
2 mm. (Note the camera is still mis-aimed from the 2026-07-28 bump and views
the deck nearly side-on, so a 2 mm Y shift reads as a small lateral offset —
good enough to confirm both positions are over the crown, not enough to judge
sub-mm centering.)

## Robot end state

Clean: gantry homed, maintenance run deleted, module seated on its base in
slot 8, nozzle bare, deck untouched. Status written to
`/tmp/OT2_STATUS_READ_ME_FIRST.txt` on the RPi-5.

## To unblock

Reattach the **P20 single GEN2** to the left mount (or confirm the module has
been switched to a P300-bore crown, in which case the recipe needs re-probing
from scratch — mouth Z, entry depth, and press depth all change). Once the
P20 is back, the queued recipe is the raised-heights full cycle with the −2 mm
shift applied throughout:

- entry (171.05, **225.0**), mouth Z 98.7, entry z=95, press to z=91.5
  (mouth − 7, required for the mid-air eject)
- lift test z=110, high carry z=170
- carry x 171→205→171 at 10 mm/s in 8.5 mm segments
- mid-air eject at z=101.5 (foot ~10 mm above seat), same XY as pickup
