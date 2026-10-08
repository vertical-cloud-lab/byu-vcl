# Sliced for a Bambu Lab A1 mini, in PLA

[`piper_camera_mount_A1mini_PLA.3mf`](piper_camera_mount_A1mini_PLA.3mf) is a Bambu Studio project
with every printed part on **one plate**, already sliced: bracket, pod, carrier, the four Pi 5
spacers and both tag wedges. Open it in Bambu Studio or send it from Bambu Handy.
[`slice_a1mini.py`](slice_a1mini.py) makes it headless with the Bambu Studio **02.08.02.61**
command-line slicer, and writes the numbers to [`report.json`](report.json). It is the OT-2 lid
mount's script from [#234](https://github.com/vertical-cloud-lab/byu-vcl/pull/234)
(`ot2-overhead-camera/lid-mount/slice`, whose README covers the CLI's traps), by way of the Pi 5
dual-camera mount's in [#238](https://github.com/vertical-cloud-lab/byu-vcl/issues/238).

- **Parts** come from [`../exports`](../exports) as exported: in print orientation, centred on
  x = y = 0, standing on z = 0.
- **Positions** are `PRINT_LAYOUT` in [`../cad/render.py`](../cad/render.py), the centre of each
  part's footprint on the 180 × 180 mm bed. The script imports it, so a change there moves the part
  in both the slice and `renders/print_layout.png`.
- **Settings** are Bambu's system presets `Bambu Lab A1 mini 0.4 nozzle`, `0.20mm Standard @BBL A1M`
  and `Bambu PLA Basic @BBL A1M` (220 °C). On top go **3 walls and 25 % infill**, the **Textured PEI**
  plate at 65 °C, Auto circle contour-hole compensation **on** and supports **off**. The filament
  colour is black, which only changes the preview.

## Running it

From the repo root:

```bash
# Bambu Studio for Linux: the AppImage, extracted to ~/bambu/squashfs-root (needs no FUSE)
mkdir -p ~/bambu && curl -L -o ~/bambu/BambuStudio.AppImage \
  https://github.com/bambulab/BambuStudio/releases/download/v02.08.02.61/BambuStudio_ubuntu24.04-v02.08.02.61-20260820225108.AppImage
chmod +x ~/bambu/BambuStudio.AppImage && (cd ~/bambu && ./BambuStudio.AppImage --appimage-extract > /dev/null)
sudo apt-get install libwebkit2gtk-4.1-0 libgstreamer-plugins-base1.0-0 libwayland-server0

# optional, for the plate thumbnails the printer's screen shows: a headless Wayland display and OSMesa
sudo apt-get install weston libosmesa6 gcc
export XDG_RUNTIME_DIR=/tmp/xdg && mkdir -p -m 700 $XDG_RUNTIME_DIR
weston --backend=headless --socket=wayland-bambu --idle-time=0 &
export WAYLAND_DISPLAY=wayland-bambu

python piper-camera-mount/slice/slice_a1mini.py --bambu ~/bambu/squashfs-root   # -> .3mf, report.json (~10 s)
python piper-camera-mount/slice/overhangs.py                                    # -> overhangs.json (needs trimesh)
```

- **Re-run both** whenever `cad/piper_mount.py` re-exports the STLs. Each output records the first 12
  hex digits of every STL's SHA-256, so a stale one is easy to spot. The slice needs `cadquery` and
  `pyvista` only because it imports `render.py`.
- **Layout check.** Before slicing, each part's footprint (its STL's bounding box, centred on its
  `PRINT_LAYOUT` point) is checked against the bed and the other parts. Any clash is printed and
  recorded in `layout_warnings`; the fix is a new position in `PRINT_LAYOUT`. Bounding boxes are
  conservative, so a clash may be a near miss.
- **The two tag wedges** are two entries in the CLI's assemble list, so Studio names both
  `tag_wedge_1`. One entry with `"count": 2` would name them apart, but the CLI then adds the second
  position to the first.
- **Run to run**, Bambu's time estimate moves by up to about 0.4 % and the G-code's travel order
  changes. Filament use doesn't.

## report.json

| Key | What it is |
|---|---|
| `plates[].print_time_s`, `filament_g`, `filament_m` | Bambu's estimate for the plate, and the PLA it takes |
| `plates[].feature_time_s` | Bambu's time per feature. `Travel` is also counted inside the others: leave it out and the rest add up to `print_time_s` |
| `plates[].toolpath_outside_bed` | Whether any part's toolpath leaves the 180 × 180 mm bed (Bambu's own `outside` flag) |
| `plates[].support_used` | Whether supports were generated. False, since they're off |
| `support_necessity_checks_run`, `support_necessity_flags` | With supports off, Bambu checks every object for floating regions and cantilevers over 6 mm, and warns *"It seems object X has … Please re-orient the object or enable support generation."* The flags are those warnings; empty means nothing was flagged. In 02.08.02.61 the check ignores ordinary overhangs and bridges, hence `overhangs.py` |
| `plates[].slicer_warnings` | Every `found … slicing warnings` line the CLI logged for the plate |
| `plates[].gcode_warnings` | Warnings stored in the 3MF. `not_support_traditional_timelapse` is on every single-colour A1 mini print, and only matters if the job is sent with timelapse on |
| `layout`, `layout_warnings` | Each part's footprint on the bed and its height, and any part that leaves the bed or overlaps another |

## overhangs.json

[`overhangs.py`](overhangs.py) works on the STLs alone, without the slicer. For each part, in print
orientation, it adds up the downward-facing triangles more than 45° from vertical, leaving out the
faces on the bed, and finds the largest edge-connected patch of them. It reports that patch's area,
its flattest face (90° is a flat ceiling) and its bounding box in the STL's own frame. Faces drawn at
exactly 45°, like the carrier's gussets, are counted separately as `at_limit_mm2`. Hole tops,
nut-slot roofs and counterbore roofs all show up: they print as short bridges.

## Three setups, each part alone (`slice_configs.py`)

[`slice_configs.py`](slice_configs.py) slices the mount for the material question, with the same CLI
and the same overrides (3 walls, 25 % grid infill, supports off):

| Setup | Printer and nozzle | Process | Filament |
|---|---|---|---|
| `h2d_pahtcf_06` | H2D, 0.6 mm hardened steel (Bambu's recommendation for PAHT-CF) | 0.30mm Standard | Bambu PAHT-CF |
| `h2d_pahtcf_04` | H2D, 0.4 mm hardened steel (fitted now) | 0.20mm Standard | Bambu PAHT-CF |
| `a1m_pla_04` | A1 mini, 0.4 mm | 0.20mm Standard | Bambu PLA Basic |

Plate 1 is the whole job, and plates 2 to 6 hold one part each, centred on the bed. So each part's
mass comes from its own G-code, split by feature, in
[`slice_configs.json`](slice_configs.json). Each part's G-code also goes to `build_<setup>/` (ignored
by git), where [`../sim/sliced_fea.py`](../sim/sliced_fea.py) reads it to model the part as printed.

## Has it been printed? (`print_2026-10-08/`, `a1mini_history/`)

**The PLA set went to the A1 mini on 2026-10-08.** It was sent at 12:39 UTC from Bambu Studio on a
CI runner, as one plate, in black PLA Basic on Textured PEI. The record is in
[`print_2026-10-08/`](print_2026-10-08/README.md): pre-flights, the file Studio sent, `print.json`
and camera frames.

Before that, nothing of the mount had been printed. [`a1mini_history/`](a1mini_history/README.md)
lists everything the A1 mini printed from July to the morning of 2026-10-08, from Bambu's cloud and
the printer's own SD card, with the two read-only scripts that fetch it.
