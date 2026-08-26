# deck_tour on the CubXL — 2026-08-25 — NOT completed: controller reset mid-tour, 3/3 attempts

Three hardware attempts at `cubos/configs/protocol/vcl/deck_tour.yaml`
(gantry `cub_xl_ben_pipette_capper.yaml` + deck `sterling_6vials_tiprack.yaml`,
both byte-identical to the repo copies) against the lab CubXL, requested in
[issue #182](https://github.com/vertical-cloud-lab/byu-vcl/issues/182)
("run those protocols"). **Every attempt ended with the GRBL controller
spontaneously resetting mid-tour** — motion stops, position is lost, and the
controller answers normally again seconds later in Alarm state with a
boot-frame `WPos`. No software retry can get past this; it needs someone at
the machine.

A wrinkle for provenance: GitHub double-fired the trigger, so two agent
sessions ran concurrently (workflow runs 32911626052 and 32911747276). The
first session staged the configs and made the three attempts; the second
("watchdog") detected the duplication, kept off the hardware, and after the
third failure placed an exclusive kernel-level hold (`TIOCEXCL`) on the
gantry serial port to prevent further blind motion retries — that holder is
`WATCHDOG_PORT_INTERLOCK__see_STOP_DUPLICATE_RUN_README.py` (in this
directory, plus the `STOP_DUPLICATE_RUN_README.md` coordination note left on
the Pi). The holder doubled as a read-only status prober; its transcript is
`watchdog_interlock.log`.

## Timeline (all times UTC, 2026-08-25→26)

| time | event | evidence |
|---|---|---|
| 22:59:08 | gantry USB (CH340) **unplugged or powered off** at the machine | Pi `dmesg` |
| 23:17:24 | gantry USB back | Pi `dmesg` |
| 23:34:29 | quick disconnect/reconnect (0.4 s) — a control-box power-cycle or replug | Pi `dmesg` |
| 23:37:49 | @jarrettshupe: "run those protocols please" | issue #182 |
| 23:43–23:44 | configs staged on the Pi; `validate_setup` + `--mock` pass (campaign 14) | `campaign_14_*` |
| 23:47:10 | preflight connect: GRBL in Alarm, `WPos:389.333,235.000,125.000` (boot frame — machine was power-cycled, never homed) | `home_preflight.log` |
| 23:47:40–23:48:41 | **attempt 1** (campaign 15) — died mid corner circuit | `hardware_run.log` |
| 23:49:34–23:51:15 | **attempt 2** (campaign 16) — died approaching deck center | `hardware_run2.log` |
| 23:55:56–23:57:52 | **attempt 3** (campaign 17) — died at/after the vial_1 close approach | `hardware_run3.log` |
| 23:57:52 | watchdog takes the serial port; controller already answering again: `<Alarm|WPos:389.333,235.000,125.000|...>` | `watchdog_interlock.log` |
| 00:00:43 | interlock upgraded to kernel `TIOCEXCL` (any other `open()` → `EBUSY`); `$I`/`$$` captured read-only | `watchdog_interlock.log` |

## The three deaths

| attempt | died commanding | deck-frame target | GRBL evidence |
|---|---|---|---|
| 1 | `G01 X1.0 F2000` (corner_front_left, a ~384 mm X sweep) | (53, 13, 111) | status reply to the timed-out command was the **boot banner** `Grbl 1.1h ['$' for help]` — the MCU rebooted mid-move |
| 2 | `G01 X193.0 F2000` (deck_center diagonal) | (245, 128, 111) | **no status response at all** ("Failed to get status from the mill") |
| 3 | `G01 X135.0 F2000` (ascent from vial_1_close back to vial_1_hover) | (187, 26, 90) | **`error:9`** (G-code locked out — controller was already back in Alarm), i.e. the reset happened during the vial_1 descent/dwell |

Each attempt got farther than the last: attempt 3 completed the full corner
circuit, deck center, the vial_1 hover, and the close approach to Z 78 over
the capped vial before dying. In all three cases the **USB link never
dropped** (no `dmesg` events during the attempts — the CH340 is USB-powered,
so this only rules out cable/hub problems, not control-box power events), and
the controller was **alive and answering within seconds** of each failure.
All three campaign CSVs record `status=failed`.

## Controller state captured read-only after the failures

From `watchdog_interlock.log` (probes every 30 s; steady since 23:57:52):

```
<Alarm|WPos:389.333,235.000,125.000|FS:0,0>
[VER:1.1h.20190825:]  [OPT:V,15,128]
$0=10 $1=25 $2=0 $3=1 $4=0 $5=0 $6=0 $10=0 $11=0.010 $12=0.002 $13=0
$20=1 $21=0 $22=1 $23=0 $24=100.000 $25=1000.000 $26=250 $27=3.000
$30=10000 $31=0 $32=0
$100=400 $101=400 $102=400  $110=5000 $111=5000 $112=5000
$120=300 $121=300 $122=150  $130=389.333 $131=235.000 $132=125.000
```

Notable: **`$21=0` — hard limits are disabled**, exactly the condition the
issue-#182 E-stop investigation warned about (limit switches do nothing
outside homing). `$1=25` means steppers are commanded to de-energize 25 ms
after motion. `WPos` at the raw max-travel values is GRBL's power-on frame —
the signature of a freshly reset, unhomed controller.

## Interpretation — three candidate causes, indistinguishable remotely

1. **A person at the machine stopping it** (E-stop / Reset / power blip).
   Matches every signature: on this controller class an E-stop/Reset press
   produces exactly a mid-motion MCU reset (boot banner) with USB intact,
   released again moments later. Also matches the human timeline: someone was
   physically working on the machine 22:59–23:34, immediately before the run
   request, and the stops came as the head got progressively closer to the
   labware (full-speed cross-deck sweep → deck center → descending over
   vial_1). If this is what happened: **please say so in the issue** — and
   note it would double as a real E-stop data point for #182 (it stopped
   free motion every time, Reset-class behavior).
2. **Collision-stall brownout.** Attempt 3 died exactly at the tour's
   documented worst-case passive-capper corridor (capper tool end at deck
   Z ≈ 62 over the x ≈ 135 strip during the vial_1 close approach — the
   clearance the protocol header says must be eyeballed). A stalled
   closed-loop stepper pulls maximum current and can dip the supply enough
   to reset the MCU. Attempts 1–2 don't have an obvious obstacle, though a
   deck rearranged during the 22:59–23:34 session could put something tall
   in the swept corridors. **Check the deck and the capper/nozzle for
   contact marks.**
3. **Electrical: supply sag or EMI under sustained motion.** Long full-speed
   sweeps resetting an 8-bit controller via logic-rail dip or noise is a
   known CNC failure mode — but earlier long-move protocols (2026-07-27
   vial scan, 2026-08-03 capper runs) completed clean, so if this is it,
   something changed at the machine today (loose supply terminal, pinched
   wire, half-seated connector from the afternoon's physical work).

## CubOS bugs surfaced (upstream-worthy, @alexc2684)

- **Failure-path safety retract is broken**: on any protocol failure the
  driver attempts a retract to `safe_z` using the instrument *class* name
  (`OpentronsPipette`) instead of the config key (`pipette`), raises
  `KeyError: "Unknown instrument 'OpentronsPipette'. Available: pipette,
  vial_capper_decapper"`, and the retract never happens ("manual hardware
  check required"). All three logs show it.
- **"0 steps executed before exit" is wrong** — attempts that demonstrably
  completed home + several moves still report 0 steps.
- Pre-existing (from the #182 research): the driver clears a pre-run alarm by
  *unlocking* (`$X`) rather than homing; safe here only because the machine
  happened to be parked at the home corner.

## Machine state as left + interlock release

- Controller: powered, responsive, **Alarm state, unhomed** (position lost).
  Alarm actually blocks G-code, so this is a safe parked state.
- The head is physically somewhere near **vial_1 at roughly Z 78–90** (it
  died right after the close approach). Before homing, visually confirm the
  head/capper are clear — homing lifts Z first (`$23=0`, home to max), which
  should be safe.
- Electromagnet/capper: never commanded (motion-only protocol).
- The serial-port interlock **auto-expires 90 min after 00:00:43 UTC
  (~01:30 UTC)**, or release it early with:
  `touch /home/vcl/run_20260825_deck_tour/RELEASE_INTERLOCK` on the Pi.
  After release, the port is free for the Operator UI / CLI as usual.

## Suggested at-bench checklist before the next attempt

1. If you stopped the machine on purpose — no fault found; just rerun when
   the deck/observer situation allows, ideally at a lower feed (protocol
   moves use F2000; drop to F800 for a first supervised pass).
2. Otherwise: check the swept corridors for obstacles/contact marks
   (especially x ≈ 118–135 strip and the front edge), reseat the control
   box's power terminals and motor/limit connectors (the afternoon's
   physical work is the prime suspect for a marginal connection), and watch
   a supervised slow run for where/whether it resets.
3. While there for issue #182: consider `$21=1` (hard limits) per the earlier
   investigation, and run its E-stop test matrix — this session confirmed
   `$21=0` is still live.
