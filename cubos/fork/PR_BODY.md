This is the CubOS that the lab's CubXL actually runs: upstream `496819c` plus four local patches. Until now the patches lived as files in [`byu-vcl/cubos/patches`](https://github.com/vertical-cloud-lab/byu-vcl/tree/a88bce8/cubos/patches) and were applied by hand to an uncommitted working tree on the Pi. This branch puts them under version control, one commit each. The Pi can then check out a real branch, and each change can be reviewed, ported or sent upstream on its own.

**This branch matches the Pi's code exactly.** On 2026-11-10 the Pi's `~/CubOS` was detached at `496819c` with 11 files modified (+261/−44). `git diff 496819c` of this branch is identical to that working tree, apart from `index` lines. Nothing on the Pi was changed to prepare this. The 2026-11-05 run log on the Pi names the same four patches.

| | Commit | What it does | Where it should go |
|---|---|---|---|
| 1 | Clamp a tipped pipette's hover to the reachable ceiling | With a 35 mm tip on, engage commands need carriage Z of `safe_z + tip`. That is 149 on a machine that tops out at 122, so every tipped pipette step failed validation. The pipette now hovers at the highest reachable plane and logs a WARNING. The validators and the offline `Gantry` model the same plane, so dry runs match the hardware. | Upstream candidate. `main` still rejects these steps: both tests fail on `b4f18ec`. |
| 2 | Use Opentrons' P20 GEN2 plunger planes and pass microlitres through | Every value in `p20_single_gen2` was a placeholder. Volumes were converted twice, once in CubOS and again in the firmware, and prime, blowout and drop-tip pointed at the wrong absolute planes. The new values come from Opentrons' own pipette definition. | Upstream candidate. These are the P20 GEN2 model's constants, so they hold on any machine. |
| 3 | Connect with an unreferenced plunger when homing fails | Works around this machine's plunger limit switch, which never triggered in September. Connect now warns and continues instead of refusing. Volumes are not real while this is in. | **VCL only, not for upstream.** Revert it soon: it has not been triggered since 2026-09-18, and on 2026-11-05 the connect-time `HOME` reported "Pipette homed" in 12.7 s. |
| 4 | Send `?` before reading GRBL status | Backport of draft Ursa-Laboratories/CubOS#351. It removes a ~2 s serial timeout from every status read, which was ~73 s of one 238 s campaign. | Already on `main` as `e1b8327`, and its six tests pass on unpatched `b4f18ec`. It drops out in a port. |

### Tests

On this branch, `packages/core` gives **2550 passed, 17 skipped, 0 failed** (Python 3.14, run with `pytest -o addopts=""`).

### Merging into `main`

This branch is based on `496819c`, which is 213 commits behind `main` (`b4f18ec`), so GitHub reports conflicts. That is expected: this PR records what is deployed, and porting it to `main` is the next step. Here is how each commit fares on `b4f18ec`:

- Commits 2 and 3 apply cleanly, and the full suite stays at 3695 passed, 0 failed, the same as unpatched `main`.
- Commit 4 conflicts in `driver.py`, but `e1b8327` already covers it, so its code can be dropped.
- Commit 1 conflicts in `bounds.py` (3 hunks), `protocol_semantics.py` (3) and `instrument_loader.py` (1). The clashes are with upstream's collision-aware routing (`71e7d08`) and 16 later commits to the validators. Porting it means rewriting safety-critical validation code, so it should be its own change. The lab's protocols should go through `validate_setup` and `--mock` before and after the port, and the planes should be compared.

Porting to `main` also upgrades the CubOS on the Pi. That upgrade should go through the usual dry-run gates and a bare-deck rehearsal before any labware run.

Refs vertical-cloud-lab/byu-vcl#133

🤖 Generated with [Claude Code](https://claude.com/claude-code)
