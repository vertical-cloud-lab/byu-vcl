# Getting the stir module into CubOS

This is where we discuss how the CubXL's magnetic stir module becomes part of CubOS
([#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133)). It answers
@alexc2684's [questions of 2026-11-10](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-6779212147):

1. How is the stirrer implemented in the fork today? ([§1](#1-how-the-stirrer-runs-today))
2. With approach 1, what would the gantry, deck and protocol YAML look like?
   ([§2](#2-approach-1-as-files), files in [`approach-1/`](approach-1/))
3. What are the tradeoffs between "an instrument in the gantry file plus a position in
   the deck file, for now" and "full support for deck-based instruments that a protocol
   can run"? ([§3](#3-tradeoffs-for-now-vs-full-deck-instrument-support))

Alex has said he would like us to open the first CubOS PR, and he will then do more design
work for on-deck instruments. [§4](#4-what-the-first-cubos-pr-would-contain) lists what
that PR would contain, and [§5](#5-questions-for-alex) lists the decisions we need from him
first.

This directory holds the example configs, a script that checks them offline, and its logs.

### Update, 2026-11-17: approach 1 is implemented, as a patch

At Ben's request on PR #348, approach 1 now exists as CubOS code, as
[`../patches/stirrer-approach-1.patch`](../patches/stirrer-approach-1.patch), on top of the
CubXL's `496819c` and its four patches (the fork still can't be pushed to from `@claude`
runs). It follows §2 and §4: a `stirrer` type whose registry entry says `mount: deck`;
`pawduino` (commands `30`/`31` over the shared link, optional `status_poll_s`) and `mock`
vendors; a `stir` command with `rpm`, `seconds` and `wait`; a stop for every stirrer at run
teardown; and deck-mounted types skipped by bounds, home pose, the setup summary,
calibration and head moves. The loader refuses `offset_x`/`offset_y`/`depth` on a
deck-mounted entry. The check is `mount == "deck"` exactly, so mocks in the tests still count
as head-mounted. With it, CubOS's own tests pass on the Pi: 2581, the 4-patch base's 2550 plus
31 new. The Operator UI changes in §4 are not in it.

The patch is applied to `~/CubOS` on the CubXL Pi. A stir-only CubOS run there completed 5/5
steps, but the stirrer read 0 rpm and stalled
([`stir_only_check_20261117`](../results/stir_only_check_20261117/)). The 5× transfer protocol
Ben asked for then ran 45/45 with vial 1 at its new x 151, but the stirrer stalled at 0 rpm in
all five stir windows ([`stir_transfer_5x_20261117`](../results/stir_transfer_5x_20261117/)).

What changed on the Pi (none of it is in a repo there):

- `~/CubOS`: `stirrer-approach-1.patch` applied (new files under `instruments/stirrer/`,
  `protocol_engine/commands/stir.py`, `tests/instruments/stirrer/`). The working-tree diff
  before it is saved in `~/stirrer_approach1_20261117/CubOS_before_stirrer.diff`. To undo it,
  run `git -C ~/CubOS apply -R ~/byu-vcl-stir5x/cubos/patches/stirrer-approach-1.patch`.
- `~/byu-vcl-stir5x`: a shallow, sparse checkout of this branch (`cubos/configs`,
  `cubos/tools`, `cubos/patches`, `cubos/docs/tic_p20.txt`, about 1 MB).
- `~/stirrer_approach1_20261117`: scratch space for the offline checks (an exported, patched
  CubOS tree run with `PYTHONPATH`, test logs and gate logs).
- `~/cubxl_runs/stir_transfer_5x_20261117_checks`, `~/cubxl_runs/stir_only_check_20261117`.

The examples in [`approach-1/`](approach-1/) and the checks below predate the patch. The
committed configs that use it are
[`cub_xl_ben_3_instrument_stirrer.yaml`](../configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml),
[`stir_module_trial_stirrer.yaml`](../configs/deck/stir_module_trial_stirrer.yaml),
[`stir_transfer_5x.yaml`](../configs/protocol/vcl/stir_transfer_5x.yaml) and
[`stir_only_check.yaml`](../configs/protocol/vcl/stir_only_check.yaml).

CubOS links point at upstream `main` @ [`d136340`](https://github.com/Ursa-Laboratories/CubOS/tree/d136340)
(2026-11-16). The CubXL Pi runs `496819c` plus four local patches
([`../patches/`](../patches/)).

## 1. How the stirrer runs today

**The stirrer isn't in the fork.** [`vertical-cloud-lab/CubOS`](https://github.com/vertical-cloud-lab/CubOS)
has had no pushes since it was forked on 2026-11-10. Its `main` is upstream `b4f18ec`, its
270 branches are all upstream's, and it has no pull requests. The first fork PR (the Pi's
four patches) is staged on branch
[`claude/issue-133-20261110-0309`](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-133-20261110-0309/cubos/fork),
but it is blocked: no PAT for the fork reaches `@claude` runs yet.

The stirrer runs **outside CubOS**, in three pieces:

| piece | what it is |
|---|---|
| Firmware | [`../firmware/panda-arduino-stirrer.patch`](../firmware/panda-arduino-stirrer.patch) adds two commands to the PANDA Arduino firmware on the CubXL's Uno, the same board that runs the capper and the pipette. `30,<rpm>[,<seconds>]` sets a speed, which the firmware clamps to 100-2000 rpm. With `seconds`, it stops itself after that long. `30,0` stops it. `31` returns `OK:{"target","setpoint","rpm","duty","stalled","left_s"}`. Control is closed-loop on a Hall latch (one pulse per turn), after the Pioreactor: the setpoint ramps at 100 rpm/s, and there is a full-power kick from rest and a stall recovery. The fan PWM is on D10 (Timer1, 200 Hz) and the Hall sensor on D2 (INT0). The image was flashed on 2026-11-03 ([`../firmware/README.md`](../firmware/README.md)) |
| Deck | The deck file only moves `vial_1` up onto the module (x 126, z 66: [`../configs/deck/stir_module_trial.yaml`](../configs/deck/stir_module_trial.yaml)). Nothing in any CubOS config says there is a stirrer |
| Host | [`stir_trial.py`](../results/stir_module_trial_20261105/stir/stir_trial.py) runs **after** the CubOS run has finished. It already talks through CubOS's own `PawduinoLink`: it sends `30,600,60` and polls `31` once a second |

It has to run after the protocol, because CubOS holds the Uno's port for the whole run, and
opening the port again resets the Uno, which stops everything on that board. So today a
protocol can't stir between steps, and the stir isn't in the run's record.
On 2026-11-05 ([run record](../results/stir_module_trial_20261105/README.md)) the protocol
ran 11/11 and then the script stirred vial 1 for 60 s. It reached 540 rpm and then
turned in bursts. Before the protocol, the same stack had held 600 rpm. What changed in
between isn't known; the decap and recap of vial 1 may have shifted it on its spacer.

## 2. Approach 1, as files

Approach 1 ([proposed on 2026-11-10](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-6758266781))
declares the stirrer under `instruments:` like any other device, and adds a registry flag
that marks its type as deck-mounted. Each example file is the file the 11-05 run used,
plus the stirrer:

| file | starts from | what's added |
|---|---|---|
| [`approach-1/gantry.yaml`](approach-1/gantry.yaml) | [`cub_xl_ben_3_instrument.yaml`](../configs/gantry/cub_xl_ben_3_instrument.yaml) | a `stirrer_1` instrument entry |
| [`approach-1/deck.yaml`](approach-1/deck.yaml) | [`stir_module_trial.yaml`](../configs/deck/stir_module_trial.yaml) (deck) | a `stirrer_1` `wall` for the module's body |
| [`approach-1/protocol.yaml`](approach-1/protocol.yaml) | [`stir_module_trial.yaml`](../configs/protocol/vcl/stir_module_trial.yaml) (protocol) | a `stir` step after vial 1 is recapped |

The gantry file declares the driver and the port, and nothing about position:

```yaml
instruments:
  # ...vial_capper_decapper, pipette, camera_3 unchanged...
  stirrer_1:
    type: stirrer        # registry.yaml marks this type `mount: deck`
    vendor: pawduino     # shares the Uno's PawduinoLink with the capper and pipette
    port: /dev/ttyACM0   # exactly the same string as theirs (see below)
```

`mount: deck` goes on the **type**, in `registry.yaml`, not on each YAML entry. That makes
it one predicate (say `is_deck_mounted(type)`) that every head-geometry loop can ask.
Lighting today is skipped by matching the string `"lighting"`, in seven lines across
`offset_calibration.py` and three Operator UI files (all listed in
[§4](#4-what-the-first-cubos-pr-would-contain)), and each new non-head device would add
more. A deck-mounted entry
has no `offset_x`/`offset_y`/`depth`/`motion_envelope`. The loader should reject them if
they are given, rather than ignore them.

The deck file gives the module's **body** as an obstacle, using the existing `wall` type:

```yaml
  stirrer_1:            # same key as the instrument, by convention only
    type: wall
    name: stirrer_1
    corner_1: {x: 98.0, y: 17.0, z: -16.0}    # 56 x 56 mm around vial_1's axis;
    corner_2: {x: 154.0, y: 73.0, z: 26.0}    # Z derived, not measured
```

The protocol runs the stirrer by name. The step is modelled on `set_lights`:

```yaml
  - cap:
      instrument: vial_capper_decapper
      vial: vial_1
  - stir:
      instrument: stirrer_1
      rpm: 600        # 0 stops; the firmware clamps to 100-2000
      seconds: 60     # optional; without it, runs until stopped or the run ends
                      # wait: blocks by default when seconds is given, polling 31
  - drop_tip:
      position: tip_rack.A1
```

The step stops with `rpm: 0` rather than `off: true`, because YAML reads a bare `off` as a
boolean. That's the same reason `set_lights` has `all_off`. Run teardown stops every
stirrer, in the same way
[`disconnect_instruments`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/gantry/instrument_mount.py#L318-L336)
already turns every light off, so an aborted run never leaves a stirrer spinning.

**One trap: the port string.** `PawduinoLink.acquire()` keys its shared link on the exact
port string, with no `realpath`
([`pawduino.py`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/instruments/controllers/pawduino.py#L62-L79)).
If the stirrer used `/dev/serial/by-id/...` while the capper and pipette used
`/dev/ttyACM0`, CubOS would open the Uno twice, and the second open resets it mid-run.
It's worth moving all three to the `by-id` path, but together. Normalising the key in
`acquire()` would remove the trap altogether.

### Checked offline

[`check_examples.py`](check_examples.py) runs CubOS's `validate_setup` and
`run_protocol --mock` (which never opens a port) on three sets of files. Logs are in
[`checks/`](checks/). It ran on a GitHub runner on 2026-11-16, under two CubOS builds:
upstream `main`, and `496819c` with the four patches the 11-05 run lists
([`summary.json`](../results/stir_module_trial_20261105/run/summary.json)) applied from
[`../patches/`](../patches/). To rerun it, `pip install -e packages/core` in a CubOS checkout,
then `python cubos/stirrer-integration/check_examples.py <label>`.

| files | Pi's CubOS (`496819c` + 4 patches) | upstream `main` (`d136340`) |
|---|---|---|
| the examples as they are | stops at `ValueError: Unknown instrument type 'stirrer'` | same |
| the examples without `stirrer_1` and the `stir` step (deck unchanged, wall included) | validate **PASS**; mock **11 steps executed** | 6 violations: tipped pipette hover at gantry Z 150 > `z_max` 122 |
| the 11-05 originals | validate **PASS**; mock **11 steps executed**, the same step list | the same 6 violations |

So, on the CubOS the CubXL runs, the stirrer is the only thing in these files that
CubOS doesn't already accept. The extra wall doesn't change any result. On `main`,
both sets fail only on the tipped-hover clamp, which `main` still lacks
([`../patches/tipped-hover-clamp-main.patch`](../patches/tipped-hover-clamp-main.patch)).
That issue is separate from the stirrer.

## 3. Tradeoffs: "for now" vs full deck-instrument support

"For now" is approach 1 above: the driver goes in the gantry file and the position in the
deck file, joined only by a name. Full support would make a deck device a first-class
fixture. It would have a footprint, the labware seated in it, and a driver, and protocols
and validation could reason about all three. One possible shape:

```yaml
# deck.yaml, full support (sketch only: no such type exists yet)
labware:
  stir_plate_1:
    type: stir_plate            # new fixture type, like vial_holder
    name: stir_plate_1
    instrument: stirrer_1       # driver and port stay in the machine (gantry) file
    location: {x: 126, y: 45, z: -16}
    length: 56
    width: 56
    height: 42
    vials:
      vial_1: {...}             # nested, as in vial_holder: the plate knows what's on it

# protocol.yaml
  - stir:
      vial: stir_plate_1.vial_1 # CubOS finds the stirrer under it
      rpm: 600
      seconds: 60
```

| | for now (approach 1) | full deck-instrument support |
|---|---|---|
| Size of the CubOS change | Small. A new instrument type with `pawduino` and `mock` vendors, a `stir` command, a stop at teardown, and the `mount: deck` check in the nine places in §4 | Large. A new deck schema type, the loader and `Deck` model, validation, the motion planner, protocol target resolution, and the Operator UI's deck editor |
| Which vial is being stirred | CubOS doesn't know. The step names a stirrer, and the protocol author has to know what's on it | CubOS knows. The step can name the vial, and run data can record it |
| Interlocks | Only what the protocol author writes | CubOS can enforce rules such as: no tip descending into a vial that is being stirred (the bar is on the floor and the vortex lowers the surface; [`vial-mixing.md`](../docs/vial-mixing.md) says to stop stirring while pipetting); no decap or recap of a vial while it spins; stop before anything moves the vial |
| Keeping files consistent | Two files joined by a name, and nothing checks it. Moving `vial_1` off the module would still validate | One source. The vial is nested in the plate, so moving it means editing the plate entry |
| Head geometry | Every loop that assumes "every instrument is on the head" has to ask `is_deck_mounted`, including future loops. Missing one is a quiet bug: the stirrer gets bounds-checked as if it were a tool, or motion planning refuses to run without an envelope for it | Those loops never see it, because it is not in the head's instrument list |
| Operator UI | The gantry editor shows the stirrer under instruments, and needs a "deck-mounted: no offsets or calibration" form. The calibration screens must skip it. The deck editor needs no change (a wall) | The deck editor needs the new fixture type. When Ben last tried (2026-10-02), it couldn't edit vial holders or tip racks either ([#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133), [CubOS#270](https://github.com/Ursa-Laboratories/CubOS/issues/270)) |
| Several stirrers | `stirrer_1`…`stirrer_4` on the same port with a `channel` field | One plate per position, each with its channel. Either way the firmware needs the [four-stirrer change](../../hardware/vial-stirrer-cubxl/README.md#four-stirrers-on-one-uno) first, which isn't written yet |
| Upgrade path | Forward-compatible. Full support can add the deck type that references the same instrument entry, and protocols that name the instrument keep working | n/a |
| Time to first use | As soon as the PR merges: the 11-05 protocol needs one added step | After the design work |

**Our suggestion:** do approach 1 as the first PR, with `mount: deck` as a registry
property so there is one predicate to check. Then build full deck-instrument support on
top of it as the follow-up Alex proposed. Approach 1 isn't throwaway: the driver entry and
the protocol step that names an instrument both stay. Full support adds the fixture type,
the vial binding and the interlocks. The interlocks are the strongest argument for full
support, and the first one worth having is "no tip in a vial that is being stirred".

## 4. What the first CubOS PR would contain

CubOS side, against `main`:

- `instruments/stirrer/`: `interface.py` (`StirrerInstrument`: `set_speed(rpm, seconds=None)`,
  `stop()`, `status()`), `models.py`, `exceptions.py`, and `vendors/pawduino.py`, which
  sends `30`/`31` over the shared link, like
  [`PawduinoLighting`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/instruments/lighting/vendors/pawduino.py).
  `vendors/mock.py` simulates the firmware's ramp, so `--mock` and tests have something to poll.
- `registry.yaml` gets the `stirrer` entry with `mount: deck`. `registry.py` validates
  `mount` (`head`|`deck`, default `head`) and exposes `is_deck_mounted()`.
- `protocol_engine/commands/stir.py` adds the `stir` command, with a summary in
  `_summaries.py`.
- [`instrument_mount.py` `disconnect_instruments`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/gantry/instrument_mount.py#L318-L336):
  stop every stirrer, best-effort, before disconnecting (as for lights).
- Skip deck-mounted types in the places that assume an instrument is on the head:
  - calibration CLI, [`multi_instrument_calibration.py`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/tools/calibration/multi_instrument_calibration.py#L284-L298)
  - [`offset_calibration.py`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/gantry/offset_calibration.py#L37-L39) (and L76)
  - motion-envelope planning, [`routing.py`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/protocol_engine/routing.py#L992-L998)
  - bounds, [`bounds.py`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/validation/bounds.py#L911)
  - home pose, [`protocol_semantics.py`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/packages/core/src/cubos/validation/protocol_semantics.py#L310)
  - Operator UI: [`CalibrationWizard.tsx`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/apps/operator-web/src/components/gantry/CalibrationWizard.tsx#L54),
    [`InstrumentOffsetCalibrationModal.tsx`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/apps/operator-web/src/components/gantry/InstrumentOffsetCalibrationModal.tsx#L25),
    [`calibrationMath.ts`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/apps/operator-web/src/components/gantry/calibrationMath.ts#L224) (and L258)
  - the gantry loader: reject offsets, depth or an envelope on a deck-mounted entry
- Optional: manual stir controls in the API and UI, alongside the lights
  ([`routers/instruments.py`](https://github.com/Ursa-Laboratories/CubOS/blob/d136340/services/api/src/cubos_api/routers/instruments.py#L187)).
- Optional: `PawduinoLink.acquire()` keys on `os.path.realpath(port)`.
- Tests: the mock vendor, `stir` in a mock run, the teardown stop, calibration and planning
  skipping the stirrer, and the loader rejecting offsets on it.

Firmware side: commands `30` and `31` exist only in our patch. They need to go wherever
Ursa keeps the PANDA firmware it ships
([BU-KABlab/PANDA_Arduino](https://github.com/BU-KABlab/PANDA_Arduino) or Ursa's own
copy), so the numbers don't collide with someone else's.

## 5. Questions for Alex

1. Is `mount: deck` on the registry type the right hook? Another option would be a
   `calibration_mode` value, but that only covers calibration, not planning or validation.
2. Should the command be `stir` or `set_stirrer` (like `set_lights`)? Should it block by default when
   `seconds` is given?
3. Should the first PR already refuse a tip descent into a vial on a running stirrer? With
   approach 1, CubOS can only do that if the step also names the vial, which is half of
   full support. Or should that wait for your deck-instrument design?
4. Where should firmware commands `30`/`31` live upstream?
5. Should the PR go straight to `Ursa-Laboratories/CubOS` (Sterling has write access) or
   through our fork?
