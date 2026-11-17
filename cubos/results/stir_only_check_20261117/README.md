# stir_only_check_20261117: the CubOS `stir` command on the CubXL, 0 rpm

The first run of the stirrer through CubOS itself (approach 1 of
[#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133),
[`stirrer-approach-1.patch`](../../patches/stirrer-approach-1.patch)), on PR #348. It was
run before the 5× transfer protocol ([`stir_transfer_5x_20261117`](../stir_transfer_5x_20261117/))
while vial 1's position on the deck was unconfirmed. The head only homed, and was already in
its homed corner, so nothing went near a vial.

- Protocol: [`stir_only_check.yaml`](../../configs/protocol/vcl/stir_only_check.yaml):
  home; `stir` 600 rpm for 20 s (blocking); `stir` 600 rpm, 60 s limit, `wait: false`;
  `pause` 15 s; `stir` rpm 0
- Gantry: [`cub_xl_ben_3_instrument_stirrer.yaml`](../../configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml),
  deck: [`stir_module_trial_stirrer.yaml`](../../configs/deck/stir_module_trial_stirrer.yaml)
- Code: byu-vcl `650f68c`, CubOS `496819c` + the four earlier patches + `stirrer-approach-1`
  (first version; the fix in `06ab340` only stops the double status reads seen below)
- Record: [`run/`](run/) from `cubxl_run.py` ([`SUMMARY.md`](run/SUMMARY.md),
  [`stir_trace.json`](run/stir_trace.json): every `30`/`31` command and reply)

## Result

**CubOS: 5/5 steps, 22:42:32 → 22:43:22 UTC.** Stage 1 checks and all four gates passed
first, and the Uno answered `31`, so the stirrer firmware is still the 11-03 image. CubOS
connected the stirrer on the shared link (`30,0`, then `31`), sent every command, polled
`31` once a second while it ran, and the run's teardown sent `30,0` again. No alarms, 0 USB
kernel lines.

**The stirrer: never turned.**

| stir | started (UTC) | stopped by | s | `31` reads | rpm max | stalled |
|---:|---|---|---:|---:|---:|---|
| 1, step 1 (20 s, blocking) | 22:42:53.324 | firmware (stall) | 12.1 | 24 | 0 | yes |
| 2, step 2 (60 s limit, no wait) | 22:43:05.485 | firmware (stall) | 12.1 | 12 | 0 | yes |

The setpoint ramped 100 → 600 rpm on schedule, and the duty crept 0.300 → 0.315, which is
the firmware's stall branch (`duty × 1.01` per 2 s update, with a 0.75 s pause and a 0.5 s
full-power kick each time). After five updates with no Hall pulse it stopped the fan and set
`stalled`. So step 1 returned after 12.2 s instead of 20, with the warning
`stir: stirrer_1 stalled during the stir and stopped itself.`

Not one pulse was counted, even during the full-power kicks. On 11-05, the same firmware and
stack read 240 rpm two seconds after a start
([`trial_stir.jsonl`](../stir_module_trial_20261105/stir/trial_stir.jsonl)). So either
the fan doesn't turn (no power at the fan, or the magnet carrier binding) or the Hall signal
doesn't reach D2. The deck camera suggests the module was moved by one plate slot since
11-05 ([frames](../stir_transfer_5x_20261117/frames/)), and its leads may have come off then.
That needs someone at the machine.

Two things the run showed about the code, both fixed in `06ab340`:

- During the blocking stir, `31` was read twice a second, because both the status poller and
  the step's own wait loop polled. The wait now stops the poller and logs each read itself.
- The summary's stir table only ended a window on a `30,0`. It now also ends one when the
  firmware stops the stirrer itself. The table above is the corrected one. The window 2 row in
  [`run/SUMMARY.md`](run/SUMMARY.md) attributes its start to step 3, because this trace
  stamped each command when it returned; it was sent in step 2.

`*.log` files are committed as `*.log.txt`, because the repo ignores `*.log`.
