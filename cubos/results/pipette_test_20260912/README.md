# pipette_test on the new CubXL Pi — 2026-09-12

Ben moved the CubXL onto a new Raspberry Pi 5 and attached two cameras, and
asked for the 2026-09-08 trio to be run through it with four frames from each
camera during the run.

**The run did not happen.** The new Pi is on the tailnet and online, but
Tailscale SSH from the CI runner is refused by the tailnet ACL. Everything
that does not require the Pi was done instead, so the run is one ACL rule away.

## The blocker

```
$ ssh <user>@rpi-5-des4
tailnet policy does not permit you to SSH to this node
```

Tags, read off `tailscale status --json` from the runner:

| node | tags | SSH from the runner |
| --- | --- | --- |
| the runner (ephemeral) | `tag:stream-cam-test` | — |
| `rpi-5-stream-cam-2wp0` (old CubOS Pi) | `tag:stream-cam-test`, `tag:tailscale-ssh` | works |
| **`rpi-5-des4`** (new CubXL Pi) | **`tag:pi-5-des4`** | **refused** |

The new Pi carries a tag of its own and no `tag:tailscale-ssh`, so any SSH rule
written against `tag:tailscale-ssh` does not cover it — the case CLAUDE.md
already warns about for this machine.

Five different login names were tried (`CUBXL_PI_USERNAME`,
`OT2_STREAM_CAM_USERNAME`, `pi`, `ubuntu`, `root`) and all were refused
identically. A `users`-field mismatch would reject some and accept others, so
this is a missing `dst`, not a wrong login.

The Tailscale API cannot be used to confirm or fix it from here: the OAuth
client is scoped to `tag:stream-cam-test`, and both
`GET /tailnet/<id>/acl` and `GET /tailnet/<id>/devices` return
`403 calling actor does not have enough permissions`. This is an admin change.

The rule that is missing, in the tailnet policy file:

```jsonc
"ssh": [
  {
    "action": "accept",                 // NOT "check" — the source is a tagged
    "src":    ["tag:stream-cam-test"],  // node, so there is nobody to reauth
    "dst":    ["tag:pi-5-des4"],
    "users":  ["<the Pi's login user>", "root"]
  }
]
```

## The CubXL really has moved

Confirmed on the old Pi, which is still reachable:

```
$ ls /dev/ttyUSB* /dev/ttyACM*     -> No such file or directory
$ lsusb                            -> only an RTL8153 Ethernet adapter
$ git -C ~/CubOS log --oneline -1  -> cbc33dc (+ all four local patches)
```

Neither the GRBL controller (CH340 `1a86:7523`) nor the capper/pipette Arduino
(`2341:0043`) is on the old Pi any more. So there is no fallback host — the run
has to happen on the new Pi.

## Offline gates — all four pass

Run against CubOS `cbc33dc` with all four of this repo's patches applied, i.e.
the exact software the old Pi runs and the new Pi will need:

```
validate_setup                PASS — 12 steps
run_protocol --mock           12/12
passive_shadow                0 interferences (28 poses, 36 obstacles)
passive_shadow --tip-stuck    0 interferences
```

The committed files were re-checked after editing, so what is on the branch is
what was validated, and all three parse identically to Ben's attachments.

## What changed in the trio, and why the new parks are safe

Only the park positions moved from the previous revision:

| | before | after |
| --- | --- | --- |
| capper `park_position` (gantry file) | `[236, 175]` | `[236, 25]` |
| protocol `pipette_park` | `[258, 182, 87]` | `[258, 25, 87]` |

Commanded gantry coordinates, from the trace:

```
Z  99.065  x15   capper transit / park        (safe_z 115 + depth -15.935)
Z 124.000  x3    tipped hover, CLAMPED        (hover-clamp patch; = z_max)
Z 122.000  x1    step 5 pipette_park          (travel_z 87 + tip 35)
Z 115.000  x1    bare-nozzle hover at safe_z
Z  99.065        capper park
Z  92.000  x1    drop_tip
Z  57.000  x1    pick_up_tip
Z  55.000  x2    aspirate / blowout           (tip end deck 20; height -35)
Z  54.065  x4    capper engage                (rim 55 + engage_depth 15)

X 154.000  x4    vial column, pipette frame
X 206.000  x16   capper over the vials, and pipette_park
X 236.000  x4    capper park
X 284.000  x4    tip rack — Ben's measured jog point, reproduced
```

Two things worth recording about the new parks:

* **The capper park is now off the vial column in X.** Vials span deck x
  192–220; the park is at x 236. Every decap/cap leg therefore holds the
  passive nozzle at deck x ≥ 258 — at least 38 mm clear of the column — so no
  leg carries the nozzle over a cap. That is what keeps `--tip-stuck` at zero.
* **`pipette_park` puts the capper's tool point at deck (206, 13)**, which is
  the edge of vial_1's footprint (y 13–41) in plan. It clears because the move
  travels at gantry 122, putting the capper tool point at deck ~138 and the
  cap it is holding at ~123 — far above the cap tops at deck 70.

The hover-clamp patch fires three times, as designed: a 35 mm tip cannot reach
`safe_z` 115 (that would need gantry 150 against a 124 ceiling), so the tipped
hover clamps to gantry 124 / tip end deck 89.

## Still true from the last run, and unchanged by any of this

The pipette limit switch reads asserted (Arduino D9 HIGH), so
`stepMotor()` aborts every retract after one step. `pick_up_tip`, `blowout` and
both `drop_tip` legs will again return OK in ~0.11 s having emitted no steps;
only the forward `prime` and `aspirate` will move. That is one input pin, not
anything a config can reach. See `cubos/docs/opentrons-pipette-wiring.md`.

## The camera harness

`cubos/tools/run_with_camera_capture.py` wraps `run_protocol` and grabs frames
at **step boundaries**, where the gantry is stationary and its pose is known.
A frame named `step04_aspirate` is evidence about the aspirate; a frame named
`t+38s` is not.

Two properties were tested rather than asserted:

* With two cameras stubbed to fail (missing binary, missing device), the
  protocol still completed 12/12 and returned 0. A camera cannot abort a run.
* The default capture points for this 12-step protocol come out as
  **steps 2, 4, 7, 9** — `decap vial_1`, `aspirate`, `decap vial_2`,
  `drop_tip`. Those are exactly the four open questions on this branch: did
  the cap come off, did the tip seat and enter the vial, did the second cap
  come off, and where did the tip go.

Backends are detected, not assumed: CSI cameras via `rpicam-still` /
`libcamera-still --list-cameras`, USB UVC via `ffmpeg` on `/dev/videoN` nodes
that `v4l2-ctl` confirms support capture.

## Recipe, once the ACL is fixed

The new Pi will also need CubOS at `cbc33dc` plus this repo's four patches,
and its serial ports confirmed (they are named `/dev/ttyUSB0` and
`/dev/ttyACM0` in the gantry file; on a different Pi they may enumerate
differently — prefer the `by-id` paths).

```bash
# 0. cameras first, with nothing moving
python cubos/tools/run_with_camera_capture.py --list
python cubos/tools/run_with_camera_capture.py --test-shot --outdir /tmp/camtest

# 1. offline gates
C=~/byu-vcl/cubos/configs
~/CubOS/.venv/bin/python -m cubos.tools.validate_setup \
    $C/gantry/cub_xl_ben_pipette_capper.yaml \
    $C/deck/ben_6vials_tiprack.yaml \
    $C/protocol/vcl/pipette_test.yaml

# 2. the run, 4 frames per camera
~/CubOS/.venv/bin/python cubos/tools/run_with_camera_capture.py \
    --outdir /tmp/run_frames -- \
    $C/gantry/cub_xl_ben_pipette_capper.yaml \
    $C/deck/ben_6vials_tiprack.yaml \
    $C/protocol/vcl/pipette_test.yaml
```

## Files

| file | what it is |
| --- | --- |
| `validate_setup.log` | bounds + semantics, PASS, 12 steps |
| `mock.log` | offline execution, 12/12 |
| `shadow_nominal.log` | passive-instrument sweep, 0 |
| `shadow_tipstuck.log` | same with the tip modeled as never released, 0 |
| `trace.log` | full DEBUG coordinate trace the tables above come from |
