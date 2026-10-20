# pipette_test_20261020: 12/12 on the CubXL, a repeat of 10-07 to the hundredth of a second

Run requested by Ben on #171 (*"run pipette test protocol on the CubXL"*).

| | |
|---|---|
| campaign | **139**, `2026-10-20T22:10:48Z` → `22:13:04Z` (lab 16:10:48 → 16:13:04), status **`completed`** |
| result | ✅ **12/12 steps**, no capper retries, no alarms, 0 USB events in the kernel log |
| wall | **135 s** (steps 114 s), against 137 s for the baseline `pipette_test_20261007` |
| plunger | every command executed; post-run `HOME` check **+0.00 mm**, so no steps were lost |
| trio | `cub_xl_ben_3_instrument.yaml` + `ben_2vials_tiprack.yaml` + `pipette_test.yaml`, from [#269](https://github.com/vertical-cloud-lab/byu-vcl/pull/269) at `ed84bba` (copies in [`configs/`](configs/)) |
| code | CubOS `496819c` + `grbl-prompt-status-polling`, `p20-gen2-plunger-constants`, `pipette-connect-tolerate-failed-home-main`, `tipped-hover-clamp-main` |
| plunger driver | the TMC2209 (Adafruit 6121) on the 10-07 spreadCycle firmware, so `--no-tic` |
| runner | `cubos/tools/cubxl_run.py` on #269's branch, which wrote [`SUMMARY.md`](SUMMARY.md) |

## Which trio, and why not this branch's

This branch's `pipette_test` trio (`cub_xl_ben_pipette_capper.yaml` +
`ben_6vials_tiprack.yaml`) was last run on 2026-09-18 (campaign 54). It no
longer describes the machine. The controller was recalibrated in late September
(and restored to that calibration after a factory reset found on 09-30), and Ben
re-measured the gantry and deck files on 10-02:

| | this branch's gantry file | the controller today |
|---|---|---|
| `$130/$131/$132` | 409 / 309 / 124 | **364 / 281 / 125** |
| `$21` (hard limits) | — | **1** (it was 0 in September) |

Since 10-02 every run on the CubXL has used Ben's 10-02 gantry and deck files
from #269, where the pipette work moved on 2026-09-21. So this run used those, and
the files are byte-identical (sha256) to the ones that ran before:

| file | identical to what ran in |
|---|---|
| `cub_xl_ben_3_instrument.yaml` | `pipette_test_20261007`, `pipette_test_stir_20261012` |
| `ben_2vials_tiprack.yaml` | `pipette_test_20261007`, `pipette_test_stir_20261012` |
| `pipette_test.yaml` | `pipette_test_20261006`, `pipette_test_20261007` |

This branch's trio isn't dangerous to leave in place. `$130/$131/$132` are in
CubOS's critical-settings check, so `run_protocol` would refuse it at connect
before any motion. But it isn't the trio to run.

## Checks before motion

[`checks_20261020/`](checks_20261020/) is a `--checks-only` pass run a minute
before the run. The run repeated the same checks itself:

- **GRBL:** `$20=1 $21=1`, travel `[364, 281, 125]`, `G54 = −travel`, feed F3000 within `$110–$112`.
- **Arduino:** connected in 3.77 s; `STATUS` `{"homed":0,"pos":0.00,"max_vol":20.00}`, cap sensor clear, magnet off.
- **Ports:** `/dev/ttyUSB0` (gantry) and `/dev/ttyACM0` (capper and pipette), neither held open.
- **Gates:** `validate_setup`, `run_protocol --mock`, `passive_shadow` and `passive_shadow --tip-stuck` all PASS.

The Pi's `~/CubOS` was compared file by file against a fresh `496819c` with those
four patches applied: all 11 changed files are byte-identical, so nothing else
is on the tree. The Pi had booted at about 21:28Z, and the gantry's CH340 came
up at 22:00Z, about three minutes before this session started.

## The run against its baseline

The 45 `G01`s in [`gantry_command.log`](gantry_command.log) are the same
sequence, line for line, as `pipette_test_20261007`'s. The step and plunger
timings match as well:

| step | command | today (s) | 10-07 (s) |
|---:|---|---:|---:|
| 0 | home | 7.9 | 7.9 |
| 1 | move | 9.5 | 9.5 |
| 2 | decap vial_1 | 7.3 | 7.3 |
| 3 | pick_up_tip A1 | 8.4 | 8.4 |
| 4 | aspirate vial_1 | 12.8 | 12.8 |
| 5 | move pipette_park | 5.0 | 5.0 |
| 6 | cap vial_1 | 7.0 | 7.0 |
| 7 | decap vial_2 | 5.9 | 5.9 |
| 8 | blowout vial_2 | 7.2 | 7.2 |
| 9 | drop_tip A1 | 12.8 | 12.8 |
| 10 | cap vial_2 | 7.4 | 7.4 |
| 11 | home | 22.3 | 22.3 |

| plunger command | where | today (s) | 10-07 (s) |
|---|---|---:|---:|
| `HOME` | connect | 0.95 | 0.94 |
| `MOVE_TO 28.0` | connect, prime | 2.56 | 2.56 |
| `MOVE_TO 0.0` | `pick_up_tip` | 2.56 | 2.56 |
| `ASPIRATE 20.0` → `[20.00, 1.20]` | `aspirate` | 5.00 | 5.00 |
| `MOVE_TO 32.5` | `blowout` | 2.86 | 2.86 |
| `MOVE_TO 46.5` | `drop_tip` | 4.65 | 4.65 |
| `MOVE_TO 28.0` | `drop_tip` | 1.70 | 1.70 |
| post-run `HOME` from 28.0 | `--home-check` | 12.681 ⇒ **+0.00 mm** | 12.698 ⇒ +0.04 mm |

The plunger moves both ways, and nothing is lost over a run: the post-run `HOME`
from the firmware's 28.0 mm took exactly the time 28.0 mm takes.

## What the frames show, and what they don't

Ten frames, all captured, 0.6 s each. `cam1_csi1` rides on the head next to the
capper and looks down. `cam0_csi0` looks down over the front of the deck.

- **Step 2, `decap vial_1`:** vial_1, the front vial, is open
  ([cam1](frames/step02_decap__cam1_csi1.jpg)).
- **Step 9, `drop_tip`:** vial_1 is capped again and vial_2 is open, with the red
  paint visible ([cam1](frames/step09_drop_tip__cam1_csi1.jpg),
  [cam0](frames/step09_drop_tip__cam0_csi0.jpg)). That is the protocol's state
  between steps 7 and 10, so both caps came off and the first went back on.
- **Neither camera sees the nozzle.** So there is no frame of the tip seated,
  of liquid in it, or of where the dropped tip went. The plunger table shows that
  every command ran with no lost steps. Whether liquid moved needs eyes.

The [pre-run overhead frame](frames/pre_run_2209Z__deckcam.jpg) (from the Pi's
`deckcam` service) shows **six vials in the holder**: vial_1 and vial_2 at the
front, and four more behind them that `ben_2vials_tiprack.yaml` doesn't have.
That was fine for this protocol. Every descent is over vial_1, vial_2 or the tip
rack, and with a tip on, every XY move in the G-code is at gantry Z 121–122,
which puts the tip end at deck 86 or above, against cap tops near 71. But
`passive_shadow` only checks labware that is in the deck file, so it can't see
those four vials. A protocol that moves low behind vial_2 needs them added to the
deck first.

**`cam0_csi0` frames are cropped** to the deck. Below the front rail that camera
sees the floor, and at step 2 someone's knee. This repo is public. `cam1_csi1`
frames and the deckcam frame are as captured.

## Machine state after the run

| | |
|---|---|
| protocol | completed, with `home` as the final step |
| electromagnet | off: `EMAG_OFF` → `OK:{"msg":"Electromagnet off"}` |
| cap sensor | `OK:{"value1":0}`, nothing held at the head |
| caps | both back on vials 1 and 2, from the protocol's own `cap` steps |
| plunger | homed at the limit switch by the post-run `HOME` check |
| GRBL | `Alarm`, because the board resets when the port reopens. `$20=1 $21=1`, travel 364/281/125. Re-home before the next run. |
| ports | both free, no CubOS process left running |

## How it was run

On the Pi, from the #269 worktree at `~/byu-vcl-pipette`, which was at `f4ef516`
and was fast-forwarded to `ed84bba`. That changed nothing the run uses, only the
stirrer files:

```bash
cd ~/byu-vcl-pipette && C=cubos/configs
setsid nohup ~/CubOS/.venv/bin/python cubos/tools/cubxl_run.py \
    --name pipette_test_20261020 \
    --gantry $C/gantry/cub_xl_ben_3_instrument.yaml \
    --deck $C/deck/ben_2vials_tiprack.yaml \
    --protocol $C/protocol/vcl/pipette_test.yaml \
    --no-tic --home-check --frames-at 2,3,4,8,9 \
    --baseline ~/cubxl_runs/pipette_test_20261007 \
    > ~/cubxl_runs/pipette_test_20261020.console 2>&1 < /dev/null &
```

The worktree has no upstream configured, so the status map's
`git -C ~/byu-vcl-pipette pull --ff-only` fails with *"Diverging branches"* (it
pulls the wrong branch). Use
`git fetch origin claude/issue-169-20261009-2151 && git merge --ff-only FETCH_HEAD`.

## Files

| file | what |
|---|---|
| `SUMMARY.md`, `summary.json` | the runner's own one-screen summary |
| `runner.log`, `console.log` | everything the runner printed |
| `checks.json`, `grbl_before.json`, `arduino_*.log` | the pre- and post-run reads |
| `gate_*.log` | the four offline gates |
| `run_hardware.log` | CubOS's log of the run |
| `step_trace.json`, `plunger_trace.json` | each step and each plunger command, timed |
| `gantry_command.log`, `gantry_mill_control.log` | the G-code, and the timestamped GRBL exchange |
| `kernel_during_run.log` | the kernel log during the run: camera link messages only, no USB events |
| `campaign_139_20261020_221049/` | campaign CSVs |
| `configs/` | the three files that ran |
| `checks_20261020/` | the `--checks-only` pass a minute before |
| `frames/` | 10 in-run frames and the pre-run overhead frame |
