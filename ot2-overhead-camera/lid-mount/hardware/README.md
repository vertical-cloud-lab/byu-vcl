# Fasteners: McMaster-Carr models and the nylon kit

Since 2026-10-03 the renders and GIFs show the fasteners the lab is actually using:

- **Steel:** the stainless Phillips pan heads and nuts from the ME Prototyping Lab's drawer
  ([`../shopping-list.md`](../shopping-list.md)). These are drawn from McMaster-Carr's own 3-D
  STEP models of the same parts, with modelled threads.
- **Nylon:** every M2.5 part is black nylon from the lab's COMRUN kit
  ([`amazon/README.md`](amazon/README.md)). COMRUN publishes no CAD, so `cad/hardware.py` and
  `cad/lid_mount.py` draw those from nominal sizes.

`cad/hardware.py` loads the McMaster files from `mcmaster/<PN>.step`, and falls back to ISO
nominal shapes if a file is missing.

**The STEP files aren't committed.** McMaster's CAD comes with no licence to redistribute it,
and this repo is public, so they are handled like Opentrons' STEP in `cad/ot2_context.py`:
fetch them, don't commit them (`.gitignore` has `hardware/mcmaster/*.step`). They were in
commit `e9b1911` briefly. If the lab decides committing them is fine, restore them with
`git checkout e9b1911 -- hardware/mcmaster/` and drop the ignore line.

| Qty | Role | McMaster PN | Part |
|---|---|---|---|
| 4 | base → lid, phase 2 | [92000A227](https://www.mcmaster.com/92000A227/) | 18-8 stainless Phillips pan head screw, M4 × 0.7, 18 mm: the drawer's M4 × 18 (fetched 2026-10-03) |
| 4 | in the base's traps | [91828A231](https://www.mcmaster.com/91828A231/) | 18-8 stainless hex nut, M4 × 0.7 |
| 4 | under the M4 heads | [95610A550](https://www.mcmaster.com/95610A550/) | nylon washer, M4, 4.3 mm ID × 9 mm OD (0.8 mm thick in the model) |
| 4 | deck → posts | [92000A120](https://www.mcmaster.com/92000A120/) | 18-8 stainless Phillips pan head screw, M3 × 0.5, 10 mm: the drawer's M3 × 10 (fetched 2026-10-03) |
| 4 | in the posts' side slots | [91828A211](https://www.mcmaster.com/91828A211/) | 18-8 stainless hex nut, M3 × 0.5 (fetched 2026-09-26, when the posts gained nut slots) |

The first design used button and socket heads, and steel M2.5:
[92095A194](https://www.mcmaster.com/92095A194/) and [92095A192](https://www.mcmaster.com/92095A192/)
(M4 × 16 and × 12 button heads), [92095A184](https://www.mcmaster.com/92095A184/) (M3 × 16 button
head), [91292A018](https://www.mcmaster.com/91292A018/) (M2.5 × 16 socket head) and
[91828A113](https://www.mcmaster.com/91828A113/) (M2.5 nut). They all still fit, as the shopping
list's [other lengths and heads](../shopping-list.md#other-lengths-and-heads) explains, but the
renders no longer draw them.

[`mcmaster/parts.json`](mcmaster/parts.json) records each file's page title, download URL,
size and SHA-256, and whether the renders use it. McMaster sells in packs, so one pack of each
covers the build.

## How they were fetched

McMaster's CAD files return 403 to plain `curl`, even from a Pi. So the files were fetched
by headless Chromium on the CubOS Pi 5 (`RPI_STREAM_CAM_HOSTNAME`), with no McMaster
login. [`mcmaster/fetch/`](mcmaster/fetch/) has the two scripts,
which also live on that Pi in `~/mcm/lid`:

```bash
# on the Pi, in ~/mcm/lid
bash run.sh title 92095A194                # print the product page's title (checks the PN)
bash run.sh step  92000A227 91828A231      # download <PN>.step (+ <PN>.meta.json) for each PN

# then, from the runner or a laptop on the tailnet, one file at a time (scp's SFTP mode
# doesn't expand braces on the far side)
u=RPI_STREAM_CAM_USERNAME; h=RPI_STREAM_CAM_HOSTNAME
for pn in 92000A227 91828A231 95610A550 92000A120 91828A211; do
  scp "${!u}@${!h}:mcm/lid/$pn.step" hardware/mcmaster/
done
```

Each file's SHA-256 is in `parts.json`, so a fresh download can be checked against the one
the renders used.

`run.sh` starts Chromium (niced, DevTools on loopback only) and always kills it on exit.
`cdp.js` runs under the Pi's Node 20 with `--experimental-websocket`, so nothing had to be
installed. For each part it opens `https://www.mcmaster.com/<PN>/` and clicks the CAD format
button. It then reads the file path from the "3-D STEP" entry of the dropdown and downloads it
from inside the page, which sends the site's cookies.

- **The path can't be guessed.** Each option is
  `<li value="/mvC/Library/CAD2/<date>/<hash>/<PN>_<family>.STEP">`, and the hash differs
  per format. A path copied from the SLDPRT entry, with the extension changed, does not work.
- **A 403 means "not a browser session".** `curl` gets 403 on real paths too.
- **Other formats in the menu:** STEP without threads (much smaller files), Parasolid, SAT,
  IGES, and 2-D DXF/DWG/PDF.
- **A nonexistent PN** loads a page titled just "McMaster-Carr".
