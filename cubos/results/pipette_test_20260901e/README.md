# pipette_test on the CubXL — campaign 77, 2026-09-01 (rev 3, after Ben's 4th rewiring pass)

**Result: 12/12 steps, `completed`, 19:50:49 → 19:54:52 UTC (4m 3s).** No capper
retries, no alarms, no warnings other than the routine "GRBL is in Alarm state
after connect" and the expected hover-clamp notices.

Trio as run — all three files exactly as committed:

| | |
|---|---|
| gantry | `cubos/configs/gantry/cub_xl_ben_pipette_capper.yaml` (unchanged) |
| deck | `cubos/configs/deck/ben_6vials_tiprack.yaml` (unchanged) |
| protocol | `cubos/configs/protocol/vcl/pipette_test.yaml` (Ben's 2026-09-01 rev 3) |

Ben's two changes vs. campaign 73: `positions.park_position`
`[206, 100, 100] → [206, 25, 115]`, and step 1's `travel_z` `100 → 115`.

---

## The headline: the limit switch is the single variable, and it is back to ASSERTED

This supersedes the "direction fault / DIR line" framing used in the
2026-08-31 and 2026-09-01 (b, c) write-ups. **There is no direction fault.**
Both of the symptoms we have been chasing come from one reading of one pin,
and the firmware source says so explicitly.

`BU-KABlab/PANDA_Arduino`, `src/Pipette.cpp` — `stepMotor()`:

```c
// Check for limit switch when moving UP (DIR_PIN is LOW for UP)
if (digitalRead(PIPETTE_LIMIT_PIN) == HIGH && digitalRead(DIR_PIN) == LOW)
{
    delay(DEBOUNCE_TIME);
    if (digitalRead(PIPETTE_LIMIT_PIN) == HIGH)
    {
        errorOccurred = true;
        break;
    }
}
```

and `homePipette()`, which checks the switch *before* its first step:

```c
digitalWrite(DIR_PIN, LOW);            // seek upward
while (!homingSuccessful && ...) {
    if (digitalRead(PIPETTE_LIMIT_PIN) == HIGH) {
        delay(DEBOUNCE_TIME);
        if (digitalRead(PIPETTE_LIMIT_PIN) == HIGH) { homingSuccessful = true; break; }
    }
    ... step ...
    if (stepsCount > 50000) return false;    // ~26 s of seek
}
// then: 796 back-off steps at 510 us == 0.406 s
```

`PIPETTE_LIMIT_PIN` is D9, `INPUT_PULLUP`, and **HIGH means "at the limit"** —
so an open switch circuit reads asserted.

| D9 reads | `HOME` | UP / retract moves | DOWN / forward moves |
|---|---|---|---|
| **HIGH (asserted)** | "success" in **0.52 s** — only the 796-step back-off, no seek | aborted after 1 step + 100 ms debounce → **~0.11 s** | unaffected |
| **LOW (clear)** | full 50000-step budget then `false` → **26.35 s** ERR | normal, scales with distance | unaffected |

Both constants are exact, not approximate: 796 × 510 µs = 0.406 s + the 100 ms
debounce = **0.506 s** vs. 0.52 s measured; 1 step + `DEBOUNCE_TIME 100` =
**~0.1 s** vs. 0.11 s measured.

Every session's data falls out of that one table:

| session | `HOME` | backward | ⇒ D9 |
|---|---|---|---|
| 2026-08-31 (before any rewiring) | 0.52 s | refused | HIGH |
| 2026-09-01 18:33 (rewire #1) | 26.35 s ERR | moves | LOW |
| 2026-09-01 18:56 (rewire #2) | 26.35 s ERR | moves | LOW |
| 2026-09-01 19:13 (rewire #3) | 26.35 s ERR | moves | LOW |
| **2026-09-01 19:46 (rewire #4, this session)** | **0.52 s** | **refused** | **HIGH** |

So the "your rewiring fixed the direction fault" reported on 2026-09-01 at
18:33 was wrong. What changed was the switch reading, which un-gated the
retract direction as a side effect. The correction is recorded here and in
`cubos/docs/opentrons-pipette-wiring.md`.

**What to check:** pipette **pin 6 → Arduino GND** (the switch return — the
Cubware diagram labels it but draws no wire), then pin 7 → D9, then that the
contact is normally *closed* (LOW at rest, opening at the limit).

## Plunger trace from the run (`plunger_trace.json`)

Motion costs ~0.673 s/mm, so a round trip that does not scale with the
commanded distance emitted no steps.

| step | command | dt | firmware stepped? |
|---|---|---|---|
| `connect()` | `STATUS` | 0.007 s | — (`homed:0, pos:0.00, max_vol:300.00`) |
| `connect()` | `HOME` | **0.520 s** | back-off only — switch asserted |
| `connect()` prime | `MOVE_TO 5.0` (down) | **3.354 s** | **yes** — 5 mm |
| `pick_up_tip` | `MOVE_TO 0.0` (up, from 5.0) | 0.107 s | **no — refused** |
| `aspirate` | `ASPIRATE 0.5` (down) | **5.962 s** | **yes** → firmware pos 36.00 |
| `blowout` | `MOVE_TO 7.0` (up, from 36) | 0.108 s | **no — refused** |
| `drop_tip` | `MOVE_TO 10.0` (up, from 36) | 0.109 s | **no — refused** |
| `drop_tip` | `MOVE_TO 5.0` (up) | 0.107 s | **no — refused** |

`ASPIRATE 0.5` → 36.00 is fully explained: the firmware's `aspirate()` clamps
to `MIN_VOLUME 5.0` µL and always primes to `PRIME_POSITION 36.0` first, so it
targets `36.0 − 5 × UL_TO_MM 0.1098 = 35.451`, reported rounded.

**A round trip that scales only proves the Arduino toggled STEP.** Whether the
motor turned needs eyes on the plunger — the two forward moves above are the
ones to watch.

## Gantry — Ben's `travel_z` change did exactly what he wanted

This run's G-code (`gantry_command_thisrun.log`), first three moves:

```
G01 Z99.065 F2000
G01 X206.0  F2000
G01 Y25.0   F2000
```

`travel_z: 115` names the capper (`depth: -15.935`) → gantry 99.065, the same
plane as every other capper leg. The old `travel_z: 100` gave 84.065.

Distinct planes commanded:

```
  9 x  Z99.065    capper transit / park     (safe_z 115 + depth -15.935)
  8 x  Z124.0     tipped hover, CLAMPED by the hover-clamp patch
  4 x  Z54.065    capper engage             (rim 55 + engage_depth 15)
  2 x  Z55.0      aspirate / blowout        (tip end deck 20, nozzle at rim)
  1 x  Z115.0     bare-nozzle hover at safe_z
  1 x  Z122.0     step 5, pipette_park at travel_z 87
  1 x  Z92.0      drop_tip
  1 x  Z57.0      pick_up_tip
```

Distinct X: 154.0 (vial column in the pipette frame), 206.0 (capper over the
vials), 236.0 (capper park), 284.0 (tip rack — Ben's measured jog point,
reproduced to the millimetre for the third run running).

Controller read live before the run: `$130/$131/$132` = 409.000 / 309.000 /
124.000, matching the gantry file exactly; `$20=1 $21=0 $22=1 $23=0`.

## Offline gates (Pi's exact CubOS: `cbc33dc` + all four local patches)

```
validate_setup                PASS — 12 steps
run_protocol --mock           12/12
passive_shadow                0 interferences   (28 poses, 36 obstacles)
passive_shadow --tip-stuck    0 interferences
```

The tip-stuck column is the real case, not the hypothetical one: `drop_tip`'s
plunger command was refused *and* it releases 35 mm above the slot, so the tip
is almost certainly still on the nozzle.

## Machine state, left clean

| | |
|---|---|
| Protocol | completed, `home` as the final step |
| Electromagnet | off — `CMD_EMAG_OFF`, `OK:{"msg":"Electromagnet off"}` |
| Cap sensor | `OK:{"value1":0}` — nothing held at the head |
| Caps | both returned to vials 1–2 by the protocol's own `cap` steps |
| GRBL | `Alarm` — normal, the board resets when the port closes. Re-home before the next run. |
| Plunger | counter reset by the port-open board reset; physical position unknown |
| Ports | `/dev/ttyUSB0` · `/dev/ttyACM0` — both free |
| `~/CubOS` | `cbc33dc` + all four patches |

## Plunger travel commanded this session

Retraction is refused, so nothing came back:

| pass | mm forward commanded |
|---|---|
| bench test (first) | +6.0 |
| the protocol run (prime 5 + aspirate ~9) | +13.9 |
| bench test (re-run of the corrected tool) | +6.0 |

≈ **26 mm**, all one way. Commanded, not necessarily physical — if the motor
still is not turning this is counter-only. Worth an eyeball at the plunger and
its coupling either way.

## Note on the connect patch

`pipette-connect-tolerate-failed-home.patch` is still applied but **never fired
this session** — with the switch asserted, `home()` returns OK and `connect()`
succeeds on its own. It is inert whenever homing "succeeds". Revert with:

```bash
cd ~/CubOS && git apply -R ~/byu-vcl/cubos/patches/pipette-connect-tolerate-failed-home.patch
```

## Files

- `run_hardware.log` — the full hardware run
- `plunger_trace.json` — every plunger command with timing
- `gantry_command_thisrun.log` — this run's G-code only (the Pi's `command.log` is cumulative)
- `bench_move.log` — the plunger bench check (corrected tool)
- `validate.log`, `mock.log`, `shadow_nominal.log`, `shadow_tipstuck.log` — offline gates
- campaign CSVs in `../campaign_77_20260901_195049/`
