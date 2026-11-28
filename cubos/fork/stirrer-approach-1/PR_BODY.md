Adds the CubXL's magnetic stir module to CubOS as a **deck-mounted instrument** with a **`stir`** protocol command. This is approach 1 from [vertical-cloud-lab/byu-vcl#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133), shaped by @alexc2684's [answers of 2026-11-23](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-7108487964). Alex plans to build the full deck-instrument design on top of it.

### How it looks in the YAML

```yaml
# gantry.yaml, under instruments:
  stirrer_1:
    type: stirrer        # registry.yaml: mount: deck, so no offsets, depth, envelope or calibration
    vendor: pawduino     # the PANDA Arduino, over the shared PawduinoLink
    port: /dev/ttyACM0   # exactly the same string as the capper's and the pipette's
    status_poll_s: 1.0   # optional: log firmware status this often while it stirs

# protocol.yaml
  - stir:
      instrument: stirrer_1
      rpm: 600           # 0 stops
      seconds: 120       # optional: the stirrer stops itself after this long
      wait: false        # optional: defaults to true when seconds is given
```

The deck file can give the module's body as a `wall`, as an obstacle. Nothing in this PR ties a vial to a stirrer.

### Alex's five answers, and where they are

| # | question | answer | in this PR |
|---|---|---|---|
| 1 | Is `mount: deck` on the registry type the right hook? | yes | `registry.yaml` `stirrer: mount: deck`. `registry.py` validates `mount` (`head`, the default, or `deck`) and adds `get_mount()` and `is_deck_mounted()`. `base_instrument.is_deck_mounted_instrument()` is the one check that head geometry uses. |
| 2 | Command name? | `stir` | `protocol_engine/commands/stir.py` |
| 3 | Refuse a tip in a vial that is being stirred, in this PR? | no | No interlock. The step names the stirrer, not the vial. |
| 4 | Where do firmware commands `30`/`31` go? | high-level `set_stirrer_params` and `get_stirrer_params`, which call 30 and 31 on the Arduino | `StirrerInstrument.set_stirrer_params(rpm, seconds=None)` and `get_stirrer_params()`. In the `pawduino` vendor they send `30,<rpm>[,<seconds>]` and `31`. `stop()` is `set_stirrer_params(0)`. |
| 5 | Upstream directly or through the fork? | through the fork | this PR |

### What's in it

**Commit 1: the stirrer type and the `stir` command**
- `instruments/stirrer/`: the interface, a status model, exceptions, and two vendors:
  - `pawduino`: the real module. `connect()` checks that the firmware answers `30`/`31`.
  - `mock`: models the firmware's ramp, for `--mock` runs and tests.
- `disconnect_instruments()` stops every stirrer first, as it already turns lights off. So an aborted run never leaves one spinning.
- The gantry loader refuses non-zero `offset_x`, `offset_y` or `depth` on a deck-mounted entry.
- These skip deck-mounted instruments: bounds, home poses, the setup summary, both calibration CLIs, and head moves. `_resolve_instrument` refuses a deck-mounted one, and `InstrumentedGantry.head_instruments` lists the others.

**Commit 2: three head-geometry paths that came after `496819c`**, the CubOS the CubXL runs:
- The motion planner's tool envelopes.
- Offset calibration.
- The loader now refuses a `motion_envelope` on a deck-mounted entry.

### Checked

- `packages/core`: **3818 passed**, 34 skipped. That's upstream `6e5cffe`'s 3779 plus 39 new. Commit 1 alone gives 3814.
- `services/api`: 371 passed. `services/sila`: 84 passed.
- On this branch, the CubXL's stir-only protocol passes `validate_setup`, and `run_protocol --mock` runs all 5 steps. Its 45-step transfer protocol fails only on the tipped-pipette hover limit (gantry Z 150 > 122), which `main` has without this PR. None of the failures involves the stirrer.
- On the Pi's CubOS (`496819c` + 4 local patches), the same code minus commit 2 gives 2585 passed. There, the 45-step protocol passes `validate_setup` and `--mock` runs all 45 steps.
- On hardware, the same code with the old method names (`set_speed`/`status`) ran on the CubXL on 2026-11-17, -18, -19 and -24:
  - The 45-step protocol ran 45/45 twice. It stirs vial 1 while vial 2 is uncapped, aspirated from and recapped, and stops the stirrer before vial 1 is opened.
  - CubOS sent every start and stop, and the run teardown stopped the stirrer.
  - The module didn't always turn. It had wiring faults and a weak start from rest, now being fixed in the hardware.
  - Records: byu-vcl `cubos/results/stir_*`.

The logs are in byu-vcl `cubos/fork/stirrer-approach-1/checks/`.

### Not in it

- **Operator UI.** The calibration wizard, the offset-calibration modal and `calibrationMath.ts` still skip only `lighting`. So a gantry with a stirrer can't be calibrated from the UI yet. The CLI and core paths do skip it.
- **The vial–stirrer binding and interlocks.** These belong to the deck-instrument design.
- **Several stirrers per Arduino.** The firmware drives one.
- **The firmware.** `30`/`31` live only in byu-vcl's `cubos/firmware/panda-arduino-stirrer.patch`.

### Open points for review

1. Answer 2 named the command but didn't say whether a timed `stir` should block by default. Here it does when `seconds` is given, and `wait: false` overrides that.
2. `get_stirrer_params()` returns a `StirrerStatus`: target, setpoint, measured rpm, duty, stall flag, time left. Rename it to `StirrerParams` if you prefer.
3. `PawduinoLink.acquire()` keys on the exact port string. A `by-id` path for one instrument and `/dev/ttyACM0` for another would open the Uno twice, and the second open resets it. Normalising with `os.path.realpath` would remove that trap. It isn't in this PR.

Refs vertical-cloud-lab/byu-vcl#133

🤖 Generated with [Claude Code](https://claude.com/claude-code)
