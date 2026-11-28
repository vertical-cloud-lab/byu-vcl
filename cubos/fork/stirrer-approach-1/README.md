# The stirrer PR for the lab's CubOS fork (staged)

This is the stir module's first CubOS PR, ready to open against
[`vertical-cloud-lab/CubOS`](https://github.com/vertical-cloud-lab/CubOS) as
@alexc2684 asked on 2026-11-23 ([#133](https://github.com/vertical-cloud-lab/byu-vcl/issues/133#issuecomment-7108487964):
"Go through the fork"). It is not open yet, for the same reason as the 11-10 fork PR: no token
that can write to the fork reaches `@claude` runs. See [To open it](#to-open-it).

| file | what it is |
|---|---|
| [`patches/`](patches/) | `git format-patch` series: two commits on upstream `main` `6e5cffe` (2026-11-22) |
| [`PR_BODY.md`](PR_BODY.md) | the PR description, including how each of Alex's five answers is reflected |
| [`open_pr.sh`](open_pr.sh) | rebuilds the branch, checks its tree, syncs the fork's `main` if it is behind, pushes, opens a draft PR |
| [`checks/`](checks/) | test summaries and `validate_setup` / `run_protocol --mock` logs |

## What changed since the 11-17 patch

[`../../patches/stirrer-approach-1.patch`](../../patches/stirrer-approach-1.patch) is what the
CubXL Pi runs (on `496819c` + 4 local patches). The fork series is that change with Alex's
answers applied, ported to current upstream `main`:

- **Answer 4: the high-level calls.** `StirrerInstrument.set_speed(rpm, seconds)` is now
  `set_stirrer_params(rpm, seconds)`, which sends firmware command `30`. `status()` is now
  `get_stirrer_params()`, which sends `31`. `stop()` stays, as `set_stirrer_params(0)`, and the
  vendors no longer implement it themselves. `validate_speed` is now `validate_stirrer_params`.
- **Answers 1–3** needed no code change. `mount: deck` stays on the registry type, the command
  stays `stir`, and there is no tip interlock.
- **The upstream port.** Upstream `main` is 241 commits past `496819c`. It has three
  head-geometry paths that `496819c` didn't: the motion planner's tool envelopes
  (`routing._build_scene_from_context`), offset calibration
  (`gantry/offset_calibration.py`), and `motion_envelope` in the gantry YAML. Commit 2 makes
  all three skip or refuse deck-mounted instruments. One import in `validation/bounds.py`
  needed a hand merge. Nothing else conflicted.

The protocol YAML is unchanged (`stir` with `rpm`, `seconds`, `wait`). So every config in
[`../../configs/`](../../configs/) that uses the stirrer works on either form.

For the Pi, [`../../patches/stirrer-approach-1-rename.patch`](../../patches/stirrer-approach-1-rename.patch)
applies the rename on top of the 11-17 patch. Commit 2 has no counterpart there, because its
code doesn't exist on `496819c`. With both patches applied, the tree is `a966957`, and that is
the tree tested below. **It is not applied on the Pi.** The Pi's behaviour would be identical,
since only method names change.

## How it was checked (2026-11-26, GitHub runner, Python 3.13)

[`checks/tests.txt`](checks/tests.txt):

| tree | suite | result |
|---|---|---|
| upstream `main` `6e5cffe` | `packages/core` | 3779 passed, 34 skipped |
| fork series, commit 1 only | `packages/core` | 3814 passed |
| fork series (`12ece77`, tree `7409d6d`) | `packages/core` | **3818 passed**, 34 skipped (39 new) |
| fork series | `services/api` / `services/sila` | 371 / 84 passed |
| Pi base + 11-17 patch + rename (tree `a966957`) | `packages/core` | 2585 passed, 17 skipped (the 11-17 Pi run had 2581) |

The machine's own stirrer configs, run offline with
[`cub_xl_ben_3_instrument_stirrer.yaml`](../../configs/gantry/cub_xl_ben_3_instrument_stirrer.yaml)
and [`stir_module_trial_stirrer.yaml`](../../configs/deck/stir_module_trial_stirrer.yaml):

| protocol | fork series (upstream base) | Pi base + rename |
|---|---|---|
| [`stir_only_check.yaml`](../../configs/protocol/vcl/stir_only_check.yaml) | validate PASS, mock 5 steps | validate PASS, mock 5 steps |
| [`stir_transfer_5x.yaml`](../../configs/protocol/vcl/stir_transfer_5x.yaml) | 22 violations, all the tipped-pipette hover at gantry Z 150 > `z_max` 122. Upstream still lacks the clamp in the first fork PR, and none of the violations involves the stirrer. | validate PASS, mock **45 steps** |

Two CubOS CI jobs weren't run here: the docs build and the web app's lint, test and build. No
docs or web files change.

`open_pr.sh --dry-run` rebuilds the series from these patch files to the same commit, `12ece77`,
with tree `7409d6d`. It refuses to push any other tree.

## To open it

Exactly as for the [11-10 fork PR](https://github.com/vertical-cloud-lab/byu-vcl/tree/claude/issue-133-20261110-0309/cubos/fork):
someone has to give the session a way to write to the fork. Either:

1. **Pass a fork token to Claude.** Add one line to the `env:` block of
   `.github/workflows/claude.yml` (the Claude App can't edit workflows):
   ```yaml
         CUBOS_FORK_PAT: ${{ secrets.CUBOS_FORK_PAT }}
   ```
   Make it a fine-grained PAT with access to `vertical-cloud-lab/CubOS` only: Contents
   read/write and Pull requests read/write. Then comment
   `@claude run cubos/fork/stirrer-approach-1/open_pr.sh`.
2. **Or run it yourself**, with your own `git` and `gh` logins, which can push to the fork:
   ```bash
   git clone -q --depth 1 --filter=blob:none --sparse -b claude/issue-133-20261116-2143 https://github.com/vertical-cloud-lab/byu-vcl.git vcl-stirrer-pr
   cd vcl-stirrer-pr && git sparse-checkout set cubos/fork/stirrer-approach-1 && bash cubos/fork/stirrer-approach-1/open_pr.sh
   ```

The fork's `main` was upstream `b4f18ec` (2026-11-08), 28 commits behind the series' base.
So the script first fast-forwards it to upstream `main` with `gh repo sync`, which is what
GitHub's *Sync fork* button does, and then the PR shows only the two stirrer commits. That
sync refuses anything but a fast-forward. The script stops instead if the fork's `main` has
commits of its own. `--no-sync` makes it stop rather than sync.

Once the PR exists, the fork branch `vcl/stirrer-approach-1` is the source of truth, and this
directory can go.
