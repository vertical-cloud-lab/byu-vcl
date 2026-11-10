# The lab's CubOS fork: staged PR

[`vertical-cloud-lab/CubOS`](https://github.com/vertical-cloud-lab/CubOS) is the lab's fork of
[`Ursa-Laboratories/CubOS`](https://github.com/Ursa-Laboratories/CubOS), created 2026-11-10.
This directory holds its first PR, ready to push. It could not be pushed when it was prepared:
see [Why it isn't open yet](#why-it-isnt-open-yet).

| file | what it is |
|---|---|
| [`vcl-cubxl-local-patches/`](vcl-cubxl-local-patches/) | `git format-patch` series: four commits on upstream `496819c` |
| [`PR_BODY.md`](PR_BODY.md) | the PR description |
| [`open_pr.sh`](open_pr.sh) | rebuilds the branch, checks it, pushes it, opens the draft PR |

## What the PR is

Branch `vcl/cubxl-local-patches` is the CubOS that the CubXL Pi runs: upstream `496819c` plus the
four patches in [`../patches/`](../patches/), one commit each:

1. `tipped-hover-clamp-main.patch`
2. `p20-gen2-plunger-constants.patch`
3. `pipette-connect-tolerate-failed-home-main.patch`
4. `grbl-prompt-status-polling.patch`

The other three `.patch` files in `../patches/` are not in the branch. Two are the older `cbc33dc`
forms, kept for rollback, and `tmc2209-softwareserial-read.patch` patches an Arduino library,
not CubOS.

How this was checked on 2026-11-10:

- **It matches the Pi.** A read-only `git diff` of the Pi's `~/CubOS` (detached at `496819c`, 11
  files, +261/−44) is identical to `git diff 496819c` of this branch, apart from `index` lines.
- **Tests pass.** On the branch, `packages/core` gives 2550 passed, 17 skipped, 0 failed.
- **It rebuilds exactly.** `open_pr.sh` reproduces the same commit hashes, ending at `a5fbfb7`
  with tree `5cca000`, and refuses to push if the tree differs.

The PR body explains how each commit fares on the fork's current `main` (`b4f18ec`, 213 commits
ahead). In short: commits 2 and 3 apply cleanly, `main` already covers commit 4, and commit 1
needs a real port.

## Why it isn't open yet

The PAT for the fork never reached the Claude session. No new variable was in its environment,
and `.github/workflows/claude.yml` passes no CubOS PAT in its `env:` block. A repo secret
reaches `@claude` runs only through that block, and the Claude GitHub App cannot edit
`.github/workflows/`. The App's own token has `push: false` on the fork, because it is scoped to
this repo.

To fix it, a person adds one line to the `env:` block of `claude.yml`, with the secret's
actual name on the right:

```yaml
      CUBOS_FORK_PAT: ${{ secrets.CUBOS_FORK_PAT }}
```

The PAT should be fine-grained, with repository access to `vertical-cloud-lab/CubOS` only:
Contents read/write and Pull requests read/write. Metadata read is added automatically.
Then any `@claude` run can open the PR with:

```bash
bash cubos/fork/open_pr.sh
```

Anyone whose own `git` and `gh` can already push to the fork can run the same command locally
without the PAT. Use `--dry-run` to build and verify without pushing.

Once the PR exists, the branch on the fork is the source of truth for these four changes, and
this directory can be deleted.
