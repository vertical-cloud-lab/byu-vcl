# Tutorial outline diagrams

Each tutorial opens on a draw.io outline of its major steps. The same outline then comes back as a section divider,
with the current step in full colour and a bold border and the other steps dimmed. All PNGs are 1280×720, the frame
size of the tutorial videos.

| Files | What it is |
| --- | --- |
| `00-overview.drawio` / `.png` | One run, start to finish: nine numbered phases in three lanes, one lane per tutorial |
| `00-overview_tutorial1.png` … `_tutorial3.png` | The overview with one tutorial's lane highlighted, a "you are here" for the start of tutorials 1–3 |
| `01-before`, `02-during`, `03-after` `.drawio` / `.png` | The opening outline of each tutorial: four steps with their key numbers |
| `01-before_step1.png` … `03-after_step4.png` | Section dividers: step *k* highlighted, the others dimmed |

Colours: teal for before, burnt orange for during, violet for after. The three pass the colour-blind separation checks.
White bold labels on them are at least 4.3:1, and text on the light tints at least 13:1. Wording and numbers follow
[`../../sop.md`](../../sop.md) as of 2026-10-03; when the SOP changes, change `SPECS` in
[`make_diagrams.py`](make_diagrams.py) to match.

## Regenerate

Needs draw.io desktop, Pillow, and `xvfb-run` on a machine with no display:

```bash
gh api repos/jgraph/drawio-desktop/releases/latest --jq '.assets[].browser_download_url' | grep 'amd64-.*\.deb$'
curl -LO <that url>
sudo apt-get install -y ./drawio-amd64-*.deb xvfb
python make_diagrams.py                # .drawio files from SPECS, then every PNG
python make_diagrams.py 02-during      # one tutorial and its variants
```

It takes about 45 s for all 19 PNGs on a CI runner, in a single draw.io launch. draw.io exports at 2× and Pillow
downsamples to exactly 1280×720. On macOS, point `DRAWIO` at `/Applications/draw.io.app/Contents/MacOS/draw.io`.

## Edit

- **Words and numbers:** edit `SPECS` in `make_diagrams.py` and run it. Key numbers go through `b()`, which makes
  them bold and stops them breaking at a space, dash or hyphen. `nb()` keeps any other phrase on one line. The script
  warns when an overview caption line is too wide for its box. Running it rewrites the `.drawio` files.
- **Layout or styling by hand:** open the `.drawio` file in [diagrams.net](https://app.diagrams.net) or the desktop
  app, edit and save (compressed or not), then run `python make_diagrams.py --export-only`. That re-exports every PNG,
  highlight variants included, from your edited file. A later run without `--export-only` overwrites hand edits, so
  carry anything that should last back into `make_diagrams.py`.
- **Keep the cell ids** (shown under Edit → Edit Data, Ctrl+M). The highlight variants find steps by id:
  - `s<k>_box` and `s<k>_panel` are step *k*.
  - `s<k>_lane` and the cells inside it are overview lane *k*.
  - `a<k>` is the arrow after step *k*.
  - A new cell whose id does not start with `s<k>_` is never dimmed.
- **Leave the background in place.** The white page-sized rectangle on the locked "Background" layer keeps every export
  at exactly 16:9. Keep all shapes inside the page.

Text is draw.io's default Helvetica. On Linux that resolves to Liberation Sans, which has the same metrics as
Arial/Helvetica, so lines wrap the same way in diagrams.net on other systems.
