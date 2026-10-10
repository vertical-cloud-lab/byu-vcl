# data/: the only thing figures read

Every number in a figure comes from a file in this folder. A figure script
reads nothing else: no paths into the rest of the repository, no network,
no database. When the lab's record changes, a paper does not change with it
until someone takes a new snapshot here, on purpose, and says so in the
snapshot's README.

## One README per data file

`foo.csv` is described by `foo.README.md`, next to it. `vcl_style.read_csv()`
refuses a file without one, and `make check` lists any that are missing a
field. The README states three things, as bullets that start with these
bold words (or as `##` headings):

- **Units:** every column, with its unit in brackets, and what the codes in
  any text column mean.
- **n:** how many rows, and what one row is (a dose, a specimen, a scan);
  how many independent samples that is, and whether any rows are technical
  replicates of each other. The caption's n comes from here.
- **Provenance:** where the file came from: repository, path, commit (short
  hash), branch, the date the snapshot was taken, the SHA-256 of the source
  file, and exactly what was done to it (columns kept, renames, filters). If
  it came from an instrument rather than a repository, the instrument, its
  serial or asset tag, the software version, and the date.

`python scripts/snapshot_data.py <source file>` copies a file in, counts its
rows, and writes the README with the provenance it can find (git remote,
commit, branch, SHA-256, date); you fill in units and what a row is.

## Rules

- Snapshots are copies, never links: a symlink or a path outside this folder
  defeats the point.
- Change a snapshot only by taking a new one and editing its README's
  provenance; never edit numbers by hand.
- Prefer CSV. Keep raw units (mg, s, mm) in the file and convert in the
  figure script, so the README stays true.
- At G2 (results freeze) the files here are the record the paper reports.
  A late measurement means a new snapshot and a line in the tracker.
