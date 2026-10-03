#!/usr/bin/env python3
"""Slice the lid mount for a Bambu Lab A1 mini in PLA with the Bambu Studio CLI.

    python slice_a1mini.py --bambu ~/bambu/squashfs-root   # an extracted Bambu Studio AppImage

Three plates, every part square to the bed:

    1  base            144 x 144 x 99.7 mm, centred
    2  deck + spacers  112 x 112 x 11 mm, 10 mm back from centre, spacers in front of it
    3  drill template  144 x 144 x 2 mm (optional; the paper PDF does the same job)
    4  fit coupon      a post top and a deck socket (optional; try the fits first)

Presets are Bambu's own system presets (machine "Bambu Lab A1 mini 0.4 nozzle",
process "0.20mm Standard @BBL A1M", filament "Bambu PLA Basic @BBL A1M"),
flattened by flatten_presets.py, with the README's print settings on top:
3 walls and 25 % infill (the stock preset has 2 walls and 15 %), and black
filament. The build plate is set explicitly to the Textured PEI plate the A1 mini
ships with: left alone, the CLI falls back to "Cool Plate" (which the A1 mini's
own profile lists as unsupported) and heats the bed to 35 °C instead of 65 °C,
without a warning. Writes lid_mount_A1mini_PLA.3mf and report.json here.

Plate thumbnails (the picture the printer's screen shows) and Bambu's own plate
renders need an OpenGL context. On Linux the CLI asks GLFW for an OSMesa context
on a Wayland display, and its GLX-only GLEW then refuses to start; glxshim.c
works around that. With WAYLAND_DISPLAY set (a headless Weston is enough) and
libOSMesa installed, the shim is compiled and preloaded automatically; without
them the slice still works, just with no thumbnails. See README.md here.
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

from flatten_presets import PRESETS, flatten

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
OUT_3MF = HERE / "lid_mount_A1mini_PLA.3mf"
OVERRIDES = {"wall-loops": "3", "sparse-infill-density": "25%", "curr-bed-type": "Textured PEI Plate"}
# Bambu's "Auto circle contour-hole compensation", off in the stock process preset. It resizes
# round holes and bosses by the error model in the PLA Basic filament preset, which otherwise
# prints an M3 clearance hole about 0.4 mm small (fit_sim.py). Set in the preset file because
# the CLI takes booleans only as bare flags.
PROCESS_SETTINGS = {"enable_circle_compensation": "1"}
OSMESA = Path("/usr/lib/x86_64-linux-gnu/libOSMesa.so.8")
FILAMENT_COLOUR = "#000000"

# (plate name, [(stl, x, y)]) -- x, y are where the STL origin lands on the 180 mm bed.
PLATES = [
    ("Base", [("base", 90, 90)]),
    ("Deck + spacers", [("deck", 90, 100), ("spacers", 69, 18)]),
    ("Drill template", [("drill_template", 90, 90)]),
    ("Fit coupon", [("fit_coupon", 80, 90)]),
]


def write_presets(resources: Path, build: Path) -> dict[str, Path]:
    paths = {}
    for kind, name in PRESETS.items():
        cfg = flatten(kind, name, resources / "profiles" / "BBL")
        if kind == "filament":
            cfg["filament_colour"] = [FILAMENT_COLOUR]
        if kind == "process":
            cfg.update(PROCESS_SETTINGS)
        paths[kind] = build / f"{kind}.json"
        paths[kind].write_text(json.dumps(cfg, indent=2) + "\n")
    return paths


def write_assemble_list(build: Path) -> Path:
    plates = [{"plate_name": name, "need_arrange": False,
               "objects": [{"path": str(EXPORTS / f"{stl}.stl"), "count": 1, "filaments": [1],
                            "pos_x": [x], "pos_y": [y], "pos_z": [0]} for stl, x, y in objs]}
              for name, objs in PLATES]
    path = build / "assemble.json"
    path.write_text(json.dumps({"plates": plates}, indent=1) + "\n")
    return path


def gl_env(build: Path) -> dict[str, str]:
    """Environment for the CLI, with the OSMesa shim preloaded when it can work."""
    env = os.environ.copy()
    if not (env.get("WAYLAND_DISPLAY") and OSMESA.exists() and shutil.which("gcc")):
        print("no Wayland display or libOSMesa: slicing without thumbnails")
        return env
    shim = build / "libglxshim.so"
    subprocess.run(["gcc", "-shared", "-fPIC", "-O2", "-o", str(shim), str(HERE / "glxshim.c"),
                    f"-l:{OSMESA.name}"], check=True)
    env["LD_PRELOAD"] = f"{shim}:{OSMESA}"
    return env


def run_cli(bambu: Path, presets: dict[str, Path], assemble: Path, build: Path, env: dict) -> str:
    cmd = [str(bambu / "AppRun"), "--debug", "3",
           "--load-settings", f"{presets['machine']};{presets['process']}",
           "--load-filaments", str(presets["filament"]),
           "--load-assemble-list", str(assemble)]
    for k, v in OVERRIDES.items():
        cmd += [f"--{k}", v]
    cmd += ["--slice", "0", "--outputdir", str(build), "--export-3mf", OUT_3MF.name]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    log = proc.stdout + proc.stderr
    (build / "cli.log").write_text(log)
    if proc.returncode != 0:
        raise SystemExit(f"Bambu Studio CLI exited {proc.returncode}; see {build / 'cli.log'}")
    return log


def export_png(bambu: Path, build: Path, env: dict) -> None:
    """Bambu's own iso render of every plate, for render_preview.py."""
    if "LD_PRELOAD" not in env:
        return
    (build / "png").mkdir()
    subprocess.run([str(bambu / "AppRun"), "--export-png", "0", "--camera-view", "0",
                    "--outputdir", str(build / "png"), str(build / OUT_3MF.name)],
                   capture_output=True, env=env, check=True)


def report(build: Path, log: str) -> dict:
    result = json.loads((build / "result.json").read_text())
    with zipfile.ZipFile(build / OUT_3MF.name) as z:
        info = ET.fromstring(z.read("Metadata/slice_info.config"))
        names = z.namelist()
        gcode = {n: z.read(f"Metadata/plate_{n}.gcode").decode() for n in range(1, len(PLATES) + 1)}
    version = re.search(r"Current BambuStudio Version (\S+)", log)
    slicing_warnings = re.findall(r"plate (\d+): found (?:NON_CRITICAL )?slicing warnings: (.*)", log)
    support_checks = len(re.findall(r"is_support_necessary takes", log))
    plates = []
    for sliced, (name, _), xml in zip(result["sliced_plates"], PLATES, info.findall("plate")):
        meta = {m.get("key"): m.get("value") for m in xml.findall("metadata")}
        fil = xml.find("filament")
        plates.append({
            "plate": sliced["id"], "name": name,
            "objects": [o["name"] for o in sliced["objects"]],
            "print_time_s": round(sliced["total_predication"]),
            "filament_g": float(fil.get("used_g")), "filament_m": float(fil.get("used_m")),
            "bed_type": re.search(r"^; curr_bed_type = (.*)$", gcode[sliced["id"]], re.M).group(1),
            "bed_temp_c": [int(t) for t in re.findall(r"^M1[49]0 S(\d+)", gcode[sliced["id"]], re.M)],
            "toolpath_outside_bed": meta.get("outside") == "true",
            "support_used": meta.get("support_used") == "true",
            "slicer_warnings": [w for p, w in slicing_warnings if int(p) == sliced["id"]],
            "gcode_warnings": [{"msg": w.get("msg"), "level": int(w.get("level")), "code": w.get("error_code")}
                               for w in xml.findall("warning")],
            "feature_time_s": {k: round(v) for k, v in sorted(sliced.get("feature_type_times", {}).items())},
        })
    return {
        "bambu_studio": version.group(1) if version else None,
        "presets": PRESETS, "overrides": {**{k.replace("-", "_"): v for k, v in OVERRIDES.items()}, **PROCESS_SETTINGS},
        "filament_colour": FILAMENT_COLOUR,
        "return_code": result["return_code"], "error_string": result["error_string"],
        "support_necessity_checks_run": support_checks,
        "thumbnails_embedded": sorted(n for n in names if n.endswith(".png")),
        "plates": plates,
        "total_print_time_s": sum(p["print_time_s"] for p in plates),
        "total_filament_g": round(sum(p["filament_g"] for p in plates), 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bambu", type=Path, required=True, help="extracted AppImage (squashfs-root)")
    ap.add_argument("--build", type=Path, default=HERE / "build")
    args = ap.parse_args()
    shutil.rmtree(args.build, ignore_errors=True)
    args.build.mkdir(parents=True)
    presets = write_presets(args.bambu / "resources", args.build)
    env = gl_env(args.build)
    log = run_cli(args.bambu, presets, write_assemble_list(args.build), args.build, env)
    rep = report(args.build, log)
    export_png(args.bambu, args.build, env)
    shutil.copy(args.build / OUT_3MF.name, OUT_3MF)
    (HERE / "report.json").write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
