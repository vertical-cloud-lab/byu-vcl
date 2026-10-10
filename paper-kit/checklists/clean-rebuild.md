# Clean-environment rebuild, before internal review

Before **G4 (my review)**, prove that the figures in the PDF are exactly what
the committed data and scripts make, on a machine that has nothing else.
That catches a script that reads a file from outside `data/`, a package
missing from `requirements.txt`, a figure that was edited by hand, a stale
PNG, and a caption whose n no longer matches the data.

## Steps

1. Commit everything: `git status` shows nothing to commit.
2. Figures from a clean environment:
   ```bash
   make rebuild-check
   ```
   This copies only `vcl_style.py`, `requirements.txt`, `data/` and
   `figures/fig*.py` into an empty temporary folder, creates a new virtual
   environment from `requirements.txt` alone, runs every figure script with
   `VCL_STRICT_DATA=1` (any data file opened from outside `data/` is an
   error), and compares the result with `figures/out/`. It must end with
   `clean rebuild OK`.
3. The manuscript from a fresh clone, so nothing uncommitted can help:
   ```bash
   git clone <repository URL> /tmp/clean-clone
   cd /tmp/clean-clone/<path to the paper folder>
   make figures check pdf J=<journal>
   git status --short     # must print nothing: the figures rebuilt identically
   ```
4. Paste into the tracker's G4 update: the commit hash, the last line of
   `make rebuild-check`, and that `git status --short` was empty.

## If it fails

- `FAIL fig3_...py` with a `PermissionError`: the script opens a file outside
  `data/`. Take a snapshot (`python scripts/snapshot_data.py <file>`) and read
  that instead.
- `ModuleNotFoundError` in the clean environment: add the package, pinned, to
  `requirements.txt`.
- `% of pixels differ`: the committed figure is not what the code makes now.
  Rebuild with `make figures`, look at what changed, and commit; if fonts
  differ between machines (the PDF's fonts show it), build on the machine
  that made the committed figures, or commit figures from the clean build.
- Caption stub differs: a script's caption or the data changed after the last
  `make figures`. Rebuild and commit.
