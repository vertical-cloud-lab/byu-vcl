# Fasteners: McMaster-Carr models

The screws, nuts and washers in the renders and GIFs are McMaster-Carr's own 3-D STEP
models (with modelled threads). They were downloaded on 2026-09-26. `cad/hardware.py` loads
them from `mcmaster/`, and falls back to ISO nominal shapes if a file is missing.

| Qty | Role | McMaster PN | Part |
|---|---|---|---|
| 4 | base → lid, phase 2 | [92095A194](https://www.mcmaster.com/92095A194/) | 18-8 stainless button head hex-drive screw, M4 × 0.7, 16 mm (ISO 7380) |
| – | shorter option | [92095A192](https://www.mcmaster.com/92095A192/) | the same, 12 mm |
| 4 | in the base's traps | [91828A231](https://www.mcmaster.com/91828A231/) | 18-8 stainless hex nut, M4 × 0.7 |
| 4 | under the M4 heads | [95610A550](https://www.mcmaster.com/95610A550/) | nylon washer, M4, 4.3 mm ID × 9 mm OD (0.8 mm thick in the model) |
| 8 | camera → deck, Pi 5 → deck | [91292A018](https://www.mcmaster.com/91292A018/) | 18-8 stainless socket head screw, M2.5 × 0.45, 16 mm |
| 8 | in the deck's traps | [91828A113](https://www.mcmaster.com/91828A113/) | 18-8 stainless hex nut, M2.5 × 0.45 |
| 4 | deck → posts | [92095A184](https://www.mcmaster.com/92095A184/) | 18-8 stainless button head hex-drive screw, M3 × 0.5, 16 mm |

[`mcmaster/parts.json`](mcmaster/parts.json) records each file's page title, download URL,
size and SHA-256. McMaster sells in packs, so one pack of each covers the build.

## How they were fetched

McMaster's CAD files return 403 to plain `curl`, even from a Pi. So the files were fetched
by headless Chromium on the CubOS Pi 5 (`RPI_STREAM_CAM_HOSTNAME`), with no McMaster
login. [`mcmaster/fetch/`](mcmaster/fetch/) has the two scripts,
which also live on that Pi in `~/mcm/lid`:

```bash
bash run.sh title 92095A194          # print the product page's title (checks the PN)
bash run.sh step  92095A194 91828A231  # download the 3-D STEP for each PN into dl/
```

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
