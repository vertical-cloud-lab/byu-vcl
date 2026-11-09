#!/usr/bin/env python3
"""Slice the stub holder's two trial Bottoms (Ø3.3 and Ø3.4 mm pin holes) onto one A1 mini
plate in black PLA, with the Bambu Studio CLI.

    python slice_a1mini.py --bambu ~/bambu/squashfs-root   # extracted Bambu Studio 02.08.02.61 AppImage

Writes stub_holder_bottoms_A1mini_blackPLA.gcode.3mf and report.json here.

This is digital-alloy-lab's stub-holder/slice_a1mini.py (PR 174, commit 9566ee1), which made the
2026-11-02 plate (Top + Bottom with Ø3.5 mm holes), with only the parts and their places changed.
The settings are the same, so the hole diameter in Onshape is the only thing that differs
from that print:
- Bambu's own system presets: machine "Bambu Lab A1 mini 0.4 nozzle", process
  "0.20mm Standard @BBL A1M", filament "Bambu PLA Basic @BBL A1M", flattened, because the
  CLI follows neither `inherits` nor `include`.
- On top of them: the filament colour (black), the build plate (Textured PEI) and Bambu's
  "Auto circle contour-hole compensation" (on, as on 2026-11-02). --stock leaves the
  compensation off, for a stock slice to compare.
- Both parts stand as designed, holes up, at pinned positions: Ø3.3 mm at the FRONT of the
  bed (low Y), Ø3.4 mm at the BACK. Once off the plate they look the same, so mark them as
  they come off.
- The CLI reads the printer's model id ("N1") from profiles/BBL/machine_full/, a folder the
  AppImage doesn't ship. It is created here from the stock model file.
- Plate thumbnails need an OpenGL context: run a headless Wayland display first
  (`weston --backend=headless --socket=wayland-bambu &`, then
  `export WAYLAND_DISPLAY=wayland-bambu`) with libOSMesa and gcc installed. Without them the
  slice is the same, but has no pictures.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRESETS = {
    "machine": "Bambu Lab A1 mini 0.4 nozzle",
    "process": "0.20mm Standard @BBL A1M",
    "filament": "Bambu PLA Basic @BBL A1M",
}
FILAMENT_COLOUR = "#000000"
BED = "Textured PEI Plate"
# Set in the preset file, because the CLI takes booleans only as bare flags.
PROCESS_SETTINGS = {"enable_circle_compensation": "1"}
# (STL, x, y): where each STL's origin, the middle of its 70 x 35 mm footprint, lands on the
# 180 mm bed. Both centred on X, 10 mm apart in Y, the pair centred on the bed.
# Y grows from the front of the bed to the back.
PARTS = [("stub_holder_bottom_3.3", 90.0, 67.5), ("stub_holder_bottom_3.4", 90.0, 112.5)]
OUT_STEM = "stub_holder_bottoms_A1mini_blackPLA"
OSMESA = Path("/usr/lib/x86_64-linux-gnu/libOSMesa.so.8")
# byu-vcl's glxshim.c. The CLI asks GLFW (Wayland-only in this build) for an OSMesa context,
# and its statically linked GLEW only knows GLX. This answers GLEW's GLX probes and routes
# gl* calls to OSMesa.
GLXSHIM = r"""
#include <string.h>
typedef void (*fp)(void);
extern fp OSMesaGetProcAddress(const char *name);
static char fake_display[4096];
static void *get_current_display(void) { return fake_display; }
fp glXGetProcAddressARB(const unsigned char *name)
{
    if (!strcmp((const char *)name, "glXGetCurrentDisplay"))
        return (fp)get_current_display;
    return OSMesaGetProcAddress((const char *)name);
}
fp glXGetProcAddress(const unsigned char *name) { return glXGetProcAddressARB(name); }
int glXQueryVersion(void *dpy, int *major, int *minor)
{
    (void)dpy;
    if (major) *major = 1;
    if (minor) *minor = 4;
    return 1;
}
const char *glXGetClientString(void *dpy, int name) { (void)dpy; (void)name; return ""; }
"""


def flatten(kind: str, name: str, profiles: Path) -> dict:
    """The preset with its parents first, then its included G-code templates, then its own keys."""
    files = {}
    for f in (profiles / kind).glob("*.json"):
        n = json.loads(f.read_text()).get("name")
        if n:
            files[n] = f

    def resolve(n: str) -> dict:
        own = json.loads(files[n].read_text())
        merged = resolve(own["inherits"]) if own.get("inherits") else {}
        for inc in own.get("include", []):
            merged.update({k: v for k, v in resolve(inc).items() if k not in ("name", "instantiation")})
        merged.update(own)
        return merged

    cfg = resolve(name)
    for k in ("inherits", "include", "instantiation"):
        cfg.pop(k, None)
    cfg.update({"name": name, "from": "system", "type": kind})
    return cfg


def write_presets(profiles: Path, build: Path, process_settings: dict) -> dict[str, Path]:
    paths = {}
    for kind, name in PRESETS.items():
        cfg = flatten(kind, name, profiles)
        if kind == "filament":
            cfg["filament_colour"] = [FILAMENT_COLOUR]
        if kind == "process":
            cfg.update(process_settings)
        paths[kind] = build / f"{kind}.json"
        paths[kind].write_text(json.dumps(cfg, indent=2) + "\n")
    return paths


def ensure_model_id(profiles: Path) -> None:
    model = json.loads((profiles / "machine" / f"{PRESETS['machine']}.json").read_text())["printer_model"]
    full = profiles / "machine_full" / f"{model}.json"
    if not full.exists():
        full.parent.mkdir(exist_ok=True)
        shutil.copy(profiles / "machine" / f"{model}.json", full)


def write_assemble_list(build: Path) -> Path:
    plate = {"plate_name": "Bottom 3.3 (front) + Bottom 3.4 (back)", "need_arrange": False,
             "objects": [{"path": str(HERE / f"{stl}.stl"), "count": 1, "filaments": [1],
                          "pos_x": [x], "pos_y": [y], "pos_z": [0]} for stl, x, y in PARTS]}
    path = build / "assemble.json"
    path.write_text(json.dumps({"plates": [plate]}, indent=1) + "\n")
    return path


def gl_env(build: Path) -> dict[str, str]:
    env = os.environ.copy()
    if not (env.get("WAYLAND_DISPLAY") and OSMESA.exists() and shutil.which("gcc")):
        print("no Wayland display or libOSMesa: slicing without thumbnails")
        return env
    (build / "glxshim.c").write_text(GLXSHIM)
    shim = build / "libglxshim.so"
    subprocess.run(["gcc", "-shared", "-fPIC", "-O2", "-o", str(shim), str(build / "glxshim.c"),
                    f"-l:{OSMESA.name}"], check=True)
    env["LD_PRELOAD"] = f"{shim}:{OSMESA}"
    return env


def report(build: Path, out_name: str, log: str, process_settings: dict) -> dict:
    result = json.loads((build / "result.json").read_text())
    sliced = result["sliced_plates"][0]
    with zipfile.ZipFile(build / out_name) as z:
        info = ET.fromstring(z.read("Metadata/slice_info.config")).find("plate")
        gcode = z.read("Metadata/plate_1.gcode").decode()
        names = z.namelist()
    meta = {m.get("key"): m.get("value") for m in info.findall("metadata")}
    fil = info.find("filament")
    head = dict(re.findall(r"^; (model printing time|total estimated time|total layer number|max_z_height): (.*?)\s*$",
                           gcode, re.M))
    times = re.search(r"model printing time: (.*?); total estimated time: (.*)$", gcode, re.M)
    return {
        "bambu_studio": (re.search(r"Current BambuStudio Version (\S+)", log) or [None, None])[1],
        "presets": PRESETS,
        "set_on_top_of_presets": {"filament_colour": FILAMENT_COLOUR, "curr_bed_type": BED, **process_settings},
        "return_code": result["return_code"], "error_string": result["error_string"],
        "printer_model_id": meta.get("printer_model_id"),
        "objects": [{"name": o["name"], "bbox_on_bed_mm": {k: round(o["bbox"][k], 3) for k in ("x", "y", "width", "depth", "height")}}
                    for o in sliced["objects"]],
        "estimate": {"model_printing_time": times.group(1), "total_estimated_time": times.group(2),
                     "prediction_s": int(meta["prediction"])},
        "layers": int(head["total layer number"]), "max_z_mm": float(head["max_z_height"]),
        "filament": {"type": fil.get("type"), "colour": fil.get("color"), "tray_info_idx": fil.get("tray_info_idx"),
                     "used_g": float(fil.get("used_g")), "used_m": float(fil.get("used_m"))},
        "bed_type": re.search(r"^; curr_bed_type = (.*)$", gcode, re.M).group(1),
        "bed_temp_c": [int(t) for t in re.findall(r"^M1[49]0 S(\d+)", gcode, re.M)],
        "nozzle_temp_c": re.search(r"^; nozzle_temperature = (.*)$", gcode, re.M).group(1),
        "toolpath_outside_bed": meta.get("outside") == "true",
        "support_used": meta.get("support_used") == "true",
        "slicer_warnings": re.findall(r"found (?:NON_CRITICAL )?slicing warnings: (.*)", log),
        "gcode_warnings": [w.get("msg") for w in info.findall("warning")],
        "thumbnails": sorted(n for n in names if n.endswith(".png")),
        "feature_time_s": {k: round(v) for k, v in sorted(sliced.get("feature_type_times", {}).items())},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bambu", type=Path, required=True, help="extracted AppImage (squashfs-root)")
    ap.add_argument("--build", type=Path, default=HERE / "build")
    ap.add_argument("--stock", action="store_true", help="no circle compensation; writes a *_stock file and report")
    args = ap.parse_args()
    process_settings = {} if args.stock else PROCESS_SETTINGS
    suffix = "_stock" if args.stock else ""
    out_name = f"{OUT_STEM}{suffix}.gcode.3mf"
    shutil.rmtree(args.build, ignore_errors=True)
    args.build.mkdir(parents=True)
    profiles = args.bambu / "resources" / "profiles" / "BBL"
    presets = write_presets(profiles, args.build, process_settings)
    ensure_model_id(profiles)
    env = gl_env(args.build)
    cmd = [str(args.bambu / "AppRun"), "--debug", "3",
           "--load-settings", f"{presets['machine']};{presets['process']}",
           "--load-filaments", str(presets["filament"]),
           "--load-assemble-list", str(write_assemble_list(args.build)),
           "--curr-bed-type", BED,
           "--slice", "0", "--outputdir", str(args.build), "--export-3mf", out_name]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    log = proc.stdout + proc.stderr
    (args.build / "cli.log").write_text(log)
    if proc.returncode != 0:
        raise SystemExit(f"Bambu Studio CLI exited {proc.returncode}; see {args.build / 'cli.log'}")
    rep = report(args.build, out_name, log, process_settings)
    shutil.copy(args.build / out_name, HERE / out_name)
    (HERE / f"report{suffix}.json").write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
