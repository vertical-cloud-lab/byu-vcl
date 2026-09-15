# CubOS `main` update audit — 2026-09-15

Prompted by [Alex Chen's note on #200][alex]: CubOS `main` now moves the CubXL
faster, and the Operator UI carries an **Update** button that pulls the latest
CubOS for you.

This is the offline audit of what taking that update would do to *this* machine.
**Nothing was changed on the Pi and nothing was run on the CubXL.** Both serial
ports were left untouched; the only Pi access was a read-only status query.

[alex]: https://github.com/vertical-cloud-lab/byu-vcl/issues/200#issuecomment-5666131265

---

## Verdict

**Ready, but not taken.** The migration is prepared, verified and reversible —
two ported patches in `cubos/patches/*-main.patch`, zero test regressions,
byte-identical commanded geometry. It should be applied as a *deliberate* step
with someone at the machine, not folded into an unrelated run, because:

1. Ben and Jarrett are mid-debug on the plunger. That fault is entirely below
   CubOS (Arduino → TMC2209 → motor; see `cubos/docs/opentrons-pipette-wiring.md`),
   so the update buys nothing for it and only adds a variable.
2. Ben's outstanding ask from 2026-09-12 — run the trio on the new Pi and
   capture 8 camera frames — was validated against `cbc33dc`. Do that on the
   known-good tree first.
3. The update is a real motion change: the capper's park leg is gone and the
   default feed rate goes 2000 → 3000 mm/min. Both are improvements; neither
   should arrive as a surprise mid-run.

---

## Revisions

| | |
|---|---|
| Pi (`rpi-5-des4`), `~/CubOS` | `cbc33dc` + 4 local patches (9 files, 173 insertions) |
| CubOS `main` at audit time | `496819c` |
| Commits in between | **226** |

## What the update actually gives us

### 1. Feed rate 2000 → 3000 mm/min — the "moves faster" part

`7ff4d7f` (merged `5b3376c`, 2026-08-25) adds `cnc.default_feed_rate_mm_min` and
raises the module default from 2000 to 3000. Every `G01` previously hardcoded
`F2000` regardless of `$110/$111/$112`, so raising the GRBL max rates never did
anything. Alex's bench figure: an X-axis full-travel round trip went 24.9 s →
16.7 s, position readback exact.

`31fd169` pinned **every upstream config** to an explicit `3000.0`.
`cub_xl_ben_pipette_capper.yaml` is ours, so it carries no such field and would
silently inherit the module default:

```
cnc.default_feed_rate_mm_min in Ben's gantry file : None
module DEFAULT_FEED_RATE on upstream main         : 3000
=> effective feed rate at main                    : 3000
```

A 1.5× speed increase is not free on this machine. Caps are held by an
electromagnet with clearances that Ben has already seen fail once, and the
run this trio does is the first end-to-end capper sequence. **Pin it
explicitly** — `cnc.default_feed_rate_mm_min: 2000.0` — so the speed change is
its own validated step.

> ⚠️ That pin must land **with** the update, never before it. `CncYaml` at
> `cbc33dc` is `ConfigDict(extra="forbid")`, so adding the field today makes the
> gantry file fail to load on the Pi as it stands.

### 2. The capper park leg is gone — and that helps the cap-clearance problem

`b39988b` (2026-09-02) makes `InstrumentedGantry.move()` lift to
`multi_tool_safe_travel_z` before **any** XY change that has no explicit
`travel_z`, and drops `decap`/`cap`'s trailing park move entirely.
`park_position` is removed from the capper interface; a config that still
carries it loads with a warning:

```
Instrument 'vial_capper_decapper' (capper): YAML field 'park_position' is no
longer used and was ignored (decap/cap no longer park; delete this key).
```

This is the same defect this branch diagnosed from the other end on 2026-08-28.
Concretely for us: a cap gripped after `decap` used to be carried on the park
leg at carriage Z 99.065; now it is carried on the *next* command's ceiling
travel at carriage Z **124** — the held cap rides ~9 mm higher. That is a direct
improvement on the symptom Ben filmed on 2026-08-31 (caps sliding off the
magnet when passing neighbouring caps).

### 3. Two of our four patches are fixed upstream, better than ours

| our patch | upstream | verdict |
|---|---|---|
| `cap-release-confirm-after-retract` | `3a7f4ab` (2026-08-28) | **drop ours.** Upstream re-engages on each retry; ours did not. |
| `pawduino-connect-boot-banner` | `88bf226` `PawduinoLink` (2026-08-20) | **drop ours.** Upstream drains, then does a `CMD_HELLO` round-trip with `expect="Hello"` that skips stale lines — a resync, not a longer sleep. Verified `CMD_HELLO = 0` exists in the firmware we run (`PANDA_Arduino`, `src/Interface.cpp:143` → `"Hello from Pawduino!"`). |
| `tipped-hover-clamp-and-ceiling-travel` | ceiling-travel half only (`0cc5028`/`b39988b`) | **re-port the clamp.** See below. |
| `pipette-connect-tolerate-failed-home` | not upstreamed (it is a workaround, not a fix) | **re-port** while the limit switch is broken. |

`PawduinoLink` also fixes the unarbitrated shared `/dev/ttyACM0` flagged on
2026-08-26: capper and pipette now share one refcounted, lock-serialized link
instead of opening the port twice.

### 4. Smaller things that land with it

- `5b005f4` — the built-in Cub XL right X-max rail drops from Z 100 to its real
  80 mm. Relaxes a constraint that shaped a lot of the early `safe_z` work here.
- `8c92a72` — a pipette never expels held liquid when a run aborts.
- `219f622` — serial auto-reconnect when the controller drops off USB.
- `2f087be` — `$21=1` enforced for the calibration window only; no effect on runs.
- The connect-time critical GRBL set (`$3 $20 $22 $23 $100-102 $130-132`) is
  **unchanged**, and the controller matched Ben's gantry file on 2026-09-14,
  so a run at `main` would connect.

---

## 🔴 What breaks, and the one thing that must be re-ported

Ben's committed trio — the one campaign 83 ran — **fails on `main` as-is**:

```
RESULT: FAIL - 6 violation(s) found
- pipette -> vial_1.location.safe_z:    gantry (154.0, 15.0, 150.0) violates z_max=124.0
- pipette -> vial_2.location.safe_z:    gantry (154.0, 48.0, 150.0) violates z_max=124.0
- pipette -> tip_rack.A1.safe_z:        gantry (284.0, 25.5, 150.0) violates z_max=124.0
- step 4 (aspirate): safe_z gantry z=150.0 outside working volume [0.0, 124.0]
- step 8 (blowout):  safe_z gantry z=150.0 outside working volume [0.0, 124.0]
- step 9 (drop_tip): safe_z gantry z=150.0 outside working volume [0.0, 124.0]
```

(`validate_main_unpatched.log`.) Upstream took the ceiling-travel half of our
patch but not the **hover clamp**: `move_to_labware` still ends at `safe_z` in
the tool frame, so a 35 mm tip needs carriage `115 + 35 = 150` on a machine
whose Z tops out at 124. `multi_tool_safe_travel_z` cannot rescue it — it is a
`max()`, so it never clamps downward.

Re-ported as **`cubos/patches/tipped-hover-clamp-main.patch`**. Much smaller
than the original, because upstream already has `_gantry_z_ceiling()` and the
ceiling travel: it adds `GantryConfig.hover_z()`, clamps the hover target in
`move_to_labware`, mirrors that in both offline validators, and seeds the mock
controller's working volume so dry runs plan the same motion as hardware.

**`cubos/patches/pipette-connect-tolerate-failed-home-main.patch`** is the same
escape hatch as before, rebased onto the `PawduinoLink` connect path
(`self._release_link()` replaced `self._close_serial()`). Still the one patch
here that is not a bug fix — revert it the moment the plunger limit switch works.

## Verification

All against `496819c` + both `-main.patch` files, on Ben's committed trio
(`cub_xl_ben_pipette_capper.yaml` / `ben_6vials_tiprack.yaml` / `pipette_test.yaml`):

| gate | unpatched `main` | `main` + both ports |
|---|---|---|
| `validate_setup` | **FAIL, 6 violations** | **PASS** |
| `run_protocol --mock` | aborts | **12/12** |
| `passive_shadow` | — | **0 interferences** |
| `passive_shadow --tip-stuck` | — | **0 interferences** |
| `pytest packages/core/tests` | 2544 passed | **2544 passed, 0 failed** |

The test result is the one worth dwelling on: the port causes **zero**
regressions. Pristine `main` and patched `main` both report `2544 passed, 17
skipped, 14 subtests passed`; the three tests our patches change are rewritten
in the patches themselves, so the suite stays honest rather than red.
(`pytest_main_pristine.log`, `pytest_main_patched.log`.)

`pipette_test_partA.yaml` and the `_tipsafe` gantry variant also validate PASS.
Our own tools (`passive_shadow`, `run_with_camera_capture`,
`run_with_plunger_trace`, `pipette_driver_probe`, `pipette_bench_check`,
`probe_cap_plane`) all still import and run; `OpentronsPipette._send_command`,
which the plunger tracer hooks, still exists.

### The commanded geometry does not move

Diffing the commanded poses between `cbc33dc + 4 patches` and
`main + 2 ports`, on the same trio (`trace_diff.log`):

```
- Moving PawduinoCapper to (236.000, 25.000, 115.000) -> gantry (236.000, 25.000, 99.065)   x4
- Moving PawduinoCapper to (206.000, y,      115.000) -> gantry (206.000, y,      99.065)   x2
```

Six removed poses, nothing added, nothing moved. The four are the capper park
legs; the two are now-redundant retracts. Every remaining pose is identical —
`Z 99.065` capper transit, `Z 124` tipped hover, `Z 54.065` engage, `Z 55`
aspirate/blowout, `Z 57` `pick_up_tip`, `Z 92` `drop_tip`, `Z 122`
`pipette_park`, `Z 115` bare-nozzle hover. Same X column set (154 / 206 / 284).

The clamp warns on each tipped hover, as designed:

```
OpentronsPipette cannot reach safe_z 115.000 (tool point rides 35.000 below the
carriage; ceiling 124.000). Hovering/traveling at 89.000 instead - confirm this
plane clears all deck contents.
```

---

## 🔴 The Update button cannot work on this Pi as provisioned

Four independent reasons, all measured on `rpi-5-des4` today:

| precondition | on our Pi |
|---|---|
| `cubos_api` installed (the button lives in the Operator UI) | ❌ `ModuleNotFoundError: No module named 'cubos_api'` — we installed `packages/core` only |
| API server listening | ❌ only `sshd` on a tailnet-facing address; nothing on `:8742` |
| a `cubos` systemd service for `update.sh`'s `systemctl restart` | ❌ none |
| `npm`/`node` for the frontend rebuild | ❌ absent |

And even with all of that, `deploy/pi/update.sh` runs `git checkout --detach
<target>` against the live tree, which our four applied patches block outright
(`update_button_checkout_refusal.txt`):

```
error: Your local changes to the following files would be overwritten by checkout:
        packages/core/src/cubos/gantry/gantry_config.py
        ... 8 more ...
Aborting
```

It fails *before* `ROLLBACK_READY=1`, so the abort is clean and the machine
stays at `cbc33dc` — but the button would never succeed while any local patch
is applied. (Its default `CUBOS_REPO=/home/cub/CubOS` also does not match our
`/home/vcl/CubOS`.)

This is worth saying plainly to Ursa: **a gitops updater and a locally patched
appliance are mutually exclusive.** The durable fix is upstreaming the clamp so
we carry no patches; until then, updates here are the manual recipe below.

---

## Migration recipe, when someone wants it

Read-only until the last two steps; reversible throughout.

```bash
cd ~/CubOS
git stash                                  # or: git checkout -- . after noting the patches
git fetch origin && git checkout --detach origin/main
git apply ~/byu-vcl/cubos/patches/tipped-hover-clamp-main.patch
git apply ~/byu-vcl/cubos/patches/pipette-connect-tolerate-failed-home-main.patch
.venv/bin/pip install -e packages/core

# gates, nothing moves, no port opened
C=~/byu-vcl/cubos/configs; PY=~/CubOS/.venv/bin/python
G=$C/gantry/cub_xl_ben_pipette_capper.yaml
D=$C/deck/ben_6vials_tiprack.yaml
P=$C/protocol/vcl/pipette_test.yaml
$PY -m cubos.tools.validate_setup      $G $D $P     # expect PASS
$PY -m cubos.tools.run_protocol --mock $G $D $P     # expect 12/12
$PY ~/byu-vcl/cubos/tools/passive_shadow.py $G $D $P
$PY ~/byu-vcl/cubos/tools/passive_shadow.py $G $D $P --tip-stuck
```

Then, as two separate decisions:

1. Delete the now-dead `park_position` key from the capper block in
   `cub_xl_ben_pipette_capper.yaml` (it is ignored with a warning either way).
2. Decide the feed rate. Add `cnc.default_feed_rate_mm_min: 2000.0` to keep
   today's speed, or leave the field out to take 3000 — but take the speed
   change as its own watched run, not bundled with everything above.

To go back: `git checkout --detach cbc33dc` and re-apply the four original
patches, then `pip install -e packages/core`.

## Worth sending upstream

- **The tipped-hover clamp.** It is not a byu-vcl quirk: any machine whose Z
  travel cannot lift a tipped tool point to `safe_z` hits it, and upstream's own
  `cub_xl_sterling`-shaped test geometry (`safe_z 85`, `depth -17`, 59.3 mm tip,
  `z_max 127`) is exactly that case. Two ports now exist, tested against `main`
  with no regressions.
- **The `P20_config.json` `mm_to_ul`** finding from 2026-09-09 (a p20 whose
  full-scale volume would use 6.8% of the plunger travel), which belongs with
  machineagency/science-jubilee.
- **The Cubware pin-diagram shift** (`cubos/docs/opentrons-pipette-wiring.md` §2).

## Files here

| file | what |
|---|---|
| `validate_main_unpatched.log` | the 6 violations on pristine `main` |
| `validate_main_patched.log` | PASS with both ports |
| `mock_main_patched.log` | 12/12 mock run |
| `shadow_nominal.log`, `shadow_tipstuck.log` | 0 interferences both ways |
| `pytest_main_pristine.log`, `pytest_main_patched.log` | 2544 passed in both |
| `trace_cbc33dc_patched.log`, `trace_main_patched.log`, `trace_diff.log` | the commanded-pose comparison |
| `update_button_checkout_refusal.txt` | the simulated Update-button checkout |

## Machine state — untouched

| | |
|---|---|
| Motion | **none commanded** — no homing, no G-code, no port opened |
| `~/CubOS` on the Pi | still `cbc33dc` + the original four patches |
| Serial devices | `/dev/ttyUSB0` and `/dev/ttyACM0` present, **both free** |
| Last campaign on the Pi | `campaign_9`, 2026-09-14 17:52 — the provisioning gates, i.e. nobody has run the machine since |
| Config files | unchanged |
