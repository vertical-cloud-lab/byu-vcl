# Sliced for a Bambu Lab A1 mini, in PLA

[`lid_mount_A1mini_PLA.3mf`](lid_mount_A1mini_PLA.3mf) is a Bambu Studio project with every
printed part already sliced. Open it in Bambu Studio (or send it from Bambu Handy) and print
plate by plate. It was produced headless by the Bambu Studio **02.08.02.61** command-line
slicer, and [`report.json`](report.json) holds the numbers below.

| Plate | Parts | Time | PLA |
|---|---|---|---|
| 1 | Base | 2 h 29 min | 80.5 g (26.6 m) |
| 2 | Deck + 4 Pi 5 standoffs + 4 deck shims | 1 h 08 min | 43.4 g (14.3 m) |
| 3 | Drill template (optional; the paper PDF does the same job) | 52 min | 31.9 g (10.5 m) |
| | **Total** | **4 h 28 min** | **155.8 g** |

**Settings.** These are Bambu's own system presets: printer `Bambu Lab A1 mini 0.4 nozzle`,
process `0.20mm Standard @BBL A1M` and filament `Bambu PLA Basic @BBL A1M` (220 °C nozzle).
On top of them go the main README's print settings: **3 walls and 25 % infill**, where the
stock preset has 2 walls and 15 %. Two more settings:

- **Build plate: Textured PEI**, with the bed at 65 °C. This is the plate the A1 mini ships
  with.
- **Filament colour: black**, as the README recommends for blocking stray light. The colour
  only affects the preview and AMS slot matching; any PLA prints the same.

Supports are off, and every part stays in the orientation its STL was exported in.

![toolpaths](preview/toolpaths.png)

The picture above is read straight from the G-code inside the 3MF, in Bambu Studio's
Preview colours ([`render_preview.py`](render_preview.py)). Below are Bambu Studio's own
renders of the same plates (`bambu-studio --export-png`), which are also the thumbnails
embedded in the 3MF for the printer's screen:

![Bambu Studio plate renders](preview/bambu_plates.png)

## Warnings

| Check | Result |
|---|---|
| Slicer warnings (the CLI's `found … slicing warnings` log lines) | **None** on any plate |
| Bambu's support-necessity check (floating regions, floating cantilevers, large overhangs) | Ran on all 4 objects and flagged nothing. This agrees with the README's "none needs supports" |
| Toolpaths outside the 180 × 180 mm bed / G-code path conflicts | None / none |
| G-code warnings stored in the 3MF (`slice_info.config`) | `not_support_traditional_timelapse` on every plate, see below |

`not_support_traditional_timelapse` is the only warning, and every single-colour print on an
A1 or A1 mini carries it. It appears only if you send the job with timelapse switched on. The
text is *"Enabling traditional timelapse photography may cause surface imperfections. It is
recommended to change to smooth mode."* Leave timelapse off, or switch to smooth mode (that
needs a prime tower).

Two more points that aren't slicer warnings:

- **The four posts** on plate 1 are 10 × 10 mm and stand 94 mm above the plate. The A1 mini
  moves the bed in Y, so watch the last few centimetres for ringing.
- **The four camera nut traps** on the deck open onto the build plate. The preset's
  elephant-foot compensation is 0, so if an M2.5 nut is tight, the first layer is the reason.
  Chase the hex with a nut or a blade.

## Running it again

```bash
# Bambu Studio for Linux: the AppImage, extracted (needs no FUSE)
curl -LO https://github.com/bambulab/BambuStudio/releases/download/v02.08.02.61/BambuStudio_ubuntu24.04-v02.08.02.61-20260820225108.AppImage
chmod +x BambuStudio_*.AppImage && ./BambuStudio_*.AppImage --appimage-extract
sudo apt-get install libwebkit2gtk-4.1-0 libgstreamer-plugins-base1.0-0 libwayland-server0

# optional, for thumbnails and Bambu's own renders: a headless Wayland display and OSMesa
sudo apt-get install weston libosmesa6 gcc
export XDG_RUNTIME_DIR=/tmp/xdg && mkdir -p -m 700 $XDG_RUNTIME_DIR
weston --backend=headless --socket=wayland-bambu --idle-time=0 &
export WAYLAND_DISPLAY=wayland-bambu

pip install numpy matplotlib
python slice_a1mini.py --bambu squashfs-root   # -> lid_mount_A1mini_PLA.3mf, report.json
python render_preview.py                       # -> preview/*.png
```

The whole run takes about 10 s. Change `OVERRIDES`, `FILAMENT_COLOUR` or `PLATES` at the top
of [`slice_a1mini.py`](slice_a1mini.py) to reprint differently, and `PRESETS` in
[`flatten_presets.py`](flatten_presets.py) for another printer, process or filament.

### What the CLI does not tell you

Four behaviours of Bambu Studio's command line cost time here. Each one fails silently or
with a misleading message:

1. **Preset files must be complete.** `--load-settings` and `--load-filaments` read one JSON
   each and ignore `inherits` and `include`, so a system preset loaded straight from
   `resources/profiles/BBL/` quietly falls back to a built-in default for every key its
   parents set. [`flatten_presets.py`](flatten_presets.py) walks the chain and writes
   complete files.
2. **The build plate defaults to Cool Plate**, whatever the printer's profile says. The A1
   mini's profile names Textured PEI as its default and lists Cool Plate as unsupported. Left
   alone, the bed heats to 35 °C and the start G-code's Textured-PEI Z offset is skipped, with
   no warning. So `--curr-bed-type "Textured PEI Plate"` is passed explicitly. Command-line
   overrides use dashes (`--wall-loops 3`); underscores are rejected.
3. **Auto-arrange rotates parts.** With `need_arrange` it turned the 144 mm base and the
   template 22.5° on the bed. Positions are therefore fixed in the `--load-assemble-list`
   file, which is also how the CLI takes several plates in one project.
4. **Thumbnails need an OpenGL context, and the stock build can't get one headless.** On
   Linux the CLI asks GLFW for an OSMesa context. This GLFW build is Wayland-only (under
   Xvfb, `glfwInit` fails), and its statically linked GLEW is GLX-only, so under Wayland
   `glewInit` fails. Either way the 3MF comes out with no plate pictures. The slice itself is
   unaffected; only the pictures are missing. [`glxshim.c`](glxshim.c) (20 lines) fixes it
   when preloaded with `libOSMesa.so.8`: it answers GLEW's GLX probes and routes GL calls to
   OSMesa. `slice_a1mini.py` compiles and preloads it automatically when `WAYLAND_DISPLAY` is
   set.

The CLI also writes a garbage `first_layer_time` into `slice_info.config` for one plate. The
value changes from run to run, `7.2e31` for example. It is display-only metadata and doesn't
affect the G-code.
