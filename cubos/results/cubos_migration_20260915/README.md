# CubOS migration on `rpi-5-des4` — `cbc33dc` → `main` (`496819c`) — 2026-09-15

Requested by Ben: *"reinstall the updated CubOS on the Pi and include the two
patches mentioned above."* This is that migration, executed against the recipe
verified in [the audit](../cubos_update_audit_20260915/README.md) earlier the
same day.

**No protocol was run and no motion was commanded.** Both serial ports were
opened read-only, to read settings and sensors; the electromagnet was
explicitly de-energized afterwards. Per the standing rule, a hardware run needs
an explicit ask.

---

## Result

| | before | after |
|---|---|---|
| `~/CubOS` HEAD | `cbc33dc` | **`496819c`** (detached; `== origin/main`) |
| patches applied | 4 (`*.patch`) | **2** (`*-main.patch`) |
| local diff | 9 files, 173 insertions | **8 files, 125 insertions** |
| `validate_setup` | PASS | **PASS** |
| `run_protocol --mock` | 12/12 | **12/12** |
| `passive_shadow` | 0 interferences, 28 poses | **0 interferences, 22 poses** |
| `passive_shadow --tip-stuck` | 0 interferences | **0 interferences** |
| `pytest packages/core/tests` | 2020 passed, **3 failed** | **2544 passed, 0 failed** |

`origin/main` was still exactly `496819c` at migration time — zero drift from
the audited commit — so the verified recipe applied verbatim and both ported
patches went on clean with no conflict resolution.

## What is installed

```
HEAD        : 496819cec06a83fb97ef75734249809c16dc6fa9  (detached)
HEAD subject: Merge pull request #339 from Ursa-Laboratories/feat/potentiostat-rinse
patches     : tipped-hover-clamp-main.patch
              pipette-connect-tolerate-failed-home-main.patch
```

The other four are gone, and two of them for good: `cap-release-confirm-after-retract`
and `pawduino-connect-boot-banner` are **fixed upstream**, better than ours.
`tipped-hover-clamp-and-ceiling-travel` split — upstream took the ceiling-travel
half, we re-ported the clamp. `pipette-connect-tolerate-failed-home` is the same
workaround as before and is still the one patch here that is not a bug fix;
revert it the moment the plunger limit switch works.

## The one behaviour that had to be verified on hardware, not in the abstract

Dropping `pawduino-connect-boot-banner` means the Arduino handshake is now
upstream's `PawduinoLink` — `_ARDUINO_SETTLE_TIME 2.0` + a quiet-period drain,
then a `CMD_HELLO` round-trip with `expect="Hello"` that skips stale lines. Our
patch existed because this board's boot banner lands at **3.76 s**, well past
that 2 s settle, and the old code ate the banner as the reply to the first real
command:

```
ERROR during execution: Arduino did not respond after connect:
  No 'value1' field in line-break sensor response 'OK:Ready'.
```

Tested directly against the board on the migrated tree (`hwcheck.log`):

```
=== Pawduino /dev/ttyACM0 via upstream PawduinoLink ===
  connect() with CMD_HELLO handshake: 3.77 s -> OK
  cmd 7  capper line-break sensor   -> OK:{"value1":0}
  cmd 14 pipette STATUS             -> OK:{"homed":0,"pos":0.00,"max_vol":300.00}
  cmd 6  electromagnet OFF          -> OK:{"msg":"Electromagnet off"}
```

The resync handles it. A longer sleep was never the right fix and upstream did
not use one.

## The run will connect

All ten settings in `Gantry._validate_grbl_settings`' critical set — unchanged
at `496819c` — match the gantry file. Read live, read-only:

| | config expects | controller reports |
|---|---|---|
| `$3` dir_invert_mask | 1 | 1 |
| `$20` soft_limits | true | 1 |
| `$22` homing_enable | true | 1 |
| `$23` homing_dir_mask | 0 | 0 |
| `$100` / `$101` / `$102` | 400.0 | 400.000 |
| `$130` / `$131` / `$132` | 409 / 309 / 124.0 | 409.000 / 309.000 / 124.000 |

```
<Alarm|WPos:409.000,309.000,124.000|FS:0,0|WCO:-409.000,-309.000,-124.000>
```

`Alarm` is normal — the board resets when the port opens. Re-home first.

## The commanded geometry is byte-identical to the audit

`trace_installed.log` diffs **empty** against the audit's `trace_main_patched.log`.
22 commanded poses, down from 28 at `cbc33dc`: six removed, nothing added,
nothing moved.

The six are the capper's park legs, which upstream `b39988b` deleted. They are
not simply absent — the work they used to do now happens higher. A cap gripped
after `decap` used to be carried on the park leg at carriage Z 99.065; it is now
carried on the *next* command's ceiling travel at carriage Z **124**, about 9 mm
higher. That is a direct improvement on the symptom Ben filmed on 2026-08-31
(caps sliding off the magnet while passing neighbouring caps).

Everything else is unchanged: `Z 99.065` capper transit, `Z 124` tipped hover,
`Z 54.065` engage, `Z 55` aspirate/blowout, `Z 57` `pick_up_tip`, `Z 92`
`drop_tip`, `Z 122` `pipette_park`, `Z 115` bare-nozzle hover; X column set
154 / 206 / 236 / 284.

The clamp warns on each tipped hover, as designed:

```
OpentronsPipette cannot reach safe_z 115.000 (tool point rides 35.000 below the
carriage; ceiling 124.000). Hovering/traveling at 89.000 instead - confirm this
plane clears all deck contents.
```

## Two config decisions that came with the migration

### 1. `cnc.default_feed_rate_mm_min: 2000.0` — added

Upstream `7ff4d7f` made the feed rate configurable and raised the **module
default** from 2000 to 3000 mm/min; before it, every `G01` hardcoded `F2000`
regardless of `$110`–`$112`. `cub_xl_ben_pipette_capper.yaml` is ours and
carried no such field, so the migration would silently have made every move 1.5×
faster:

```
raw cnc.default_feed_rate_mm_min in Ben's file : None
  cbc33dc  driver DEFAULT_FEED_RATE = 2000
  496819c  driver DEFAULT_FEED_RATE = 3000
```

Pinned to `2000.0` so the migrated tree reproduces campaign 83's motion exactly
and the next hardware run differs from it in one intended way (the removed park
legs), not two. **To take the speed: change that one line to `3000.0`, or delete
it.** Upstream pins `3000.0` in all of its own configs. Worth doing as its own
watched run rather than bundled with everything here.

> The field does not exist at `cbc33dc` — `CncYaml` there is `extra="forbid"` —
> so this line must be removed before any rollback.

### 2. `park_position` on the capper — kept, annotated, **not** deleted

`b39988b` removed it from the capper interface. It now loads with a warning and
has no effect:

```
Instrument 'vial_capper_decapper' (capper): YAML field 'park_position' is no
longer used and was ignored (decap/cap no longer park; delete this key).
```

Upstream says delete it. Not deleted here, because `PawduinoCapper.__init__` at
`cbc33dc` takes `park_position` as a **required** argument — removing it breaks
a rollback, and the importer's fallback is the placeholder `[-10, -10]`, which
is outside the working volume and alarms GRBL on every `decap`/`cap`. Delete it
once rollback is off the table.

⚠️ This is the **capper instrument's** park. It is *not* the protocol's
`positions: park_position:` in `pipette_test.yaml` — that one is a named
protocol position, is still used, and step 1 still moves to it. A blind
find-and-delete would break the protocol.

## Rollback

```bash
cd ~/CubOS
git checkout -- .
git checkout --detach cbc33dc
for p in pawduino-connect-boot-banner cap-release-confirm-after-retract \
         tipped-hover-clamp-and-ceiling-travel pipette-connect-tolerate-failed-home; do
  git apply ~/byu-vcl/cubos/patches/$p.patch
done
.venv/bin/pip install -e packages/core
```

…and remove the `default_feed_rate_mm_min` line from the gantry file first, or
it will fail to load.

## Machine state — no motion commanded

| | |
|---|---|
| Motion | **none** — no homing, no G-code, no protocol |
| GRBL | `Alarm` (the board resets when the port opens). Re-home before the next run. |
| `$20` soft limits | `1` |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Plunger | `OK:{"homed":0,"pos":0.00,"max_vol":300.00}` — untouched, **not** actuated |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |
| Listening on the tailnet | `sshd` only — matches the `tcp:22`-only grant |
| Campaigns | `campaign_10`/`campaign_11` are this session's mock runs (mock writes campaign rows too) |

Address the boards by their stable paths, not `ttyUSB0`/`ttyACM0`:

```
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0                               # gantry
/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_03535343335351018130-if00  # capper + pipette
```

## Unchanged by any of this

The plunger still will not actuate the pipette. That fault is entirely below
CubOS — Arduino → TMC2209 → motor; see
[`cubos/docs/opentrons-pipette-wiring.md`](../../docs/opentrons-pipette-wiring.md).
The limit switch read asserted as of campaign 83, so `pick_up_tip`, `blowout`
and both `drop_tip` legs will again return `OK` in ~0.11 s having emitted no
steps. Nothing in this migration touches that.

## Files here

| file | what |
|---|---|
| `pre_state.txt` | `cbc33dc` + the four old patches, before anything changed |
| `checkout.txt` | the revert / detach / apply transcript |
| `post_state.txt` | `496819c` + the two ports, venv, devices, listening sockets |
| `validate_setup.log` | PASS |
| `mock.log` | 12/12 |
| `shadow_nominal.log`, `shadow_tipstuck.log` | 0 interferences both ways |
| `pytest.log` | 2544 passed, 0 failed |
| `trace_installed.log` | the 22 commanded poses; diffs empty against the audit |
| `hwcheck.log`, `hwcheck.json` | the read-only GRBL + `PawduinoLink` check |
