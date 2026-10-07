#!/usr/bin/env python3
"""Slice the PiPER camera mount for a Bambu Lab A1 mini in PLA with the Bambu Studio CLI.

    python slice_a1mini.py --bambu ~/bambu/squashfs-root   # an extracted Bambu Studio AppImage

Adapted from the Pi 5 dual-camera mount's slicer script (#238), itself from the OT-2 lid
mount's (#234, ot2-overhead-camera/lid-mount/slice), with the same settings: Bambu's own
system presets (machine "Bambu Lab A1 mini 0.4 nozzle", process "0.20mm Standard @BBL A1M",
filament "Bambu PLA Basic @BBL A1M"), flattened by flatten_presets.py, then 3 walls, 25 %
infill, black filament, the Textured PEI plate (left alone the CLI picks "Cool Plate" and a
35 C bed), Bambu's circle compensation, and supports off.

One plate: every printed part in ../exports (bracket, pod, carrier, spacers, 2 x tag_wedge),
each STL in the print orientation it was exported in. The positions are PRINT_LAYOUT in
../cad/render.py, the centre of each part's footprint on the 180 x 180 mm bed, so a layout
change there flows through here. A footprint that leaves the bed or overlaps another is
reported as a layout warning. Writes piper_camera_mount_A1mini_PLA.3mf and report.json here.
Thumbnails need an OpenGL context. With WAYLAND_DISPLAY set (a headless Weston is enough) and
libOSMesa installed, glxshim.c is compiled and preloaded for it; see README.md here. Without
one the slice is the same, only without plate pictures.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # importing ../cad/render.py leaves no __pycache__ in cad/

import argparse
import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np

from flatten_presets import PRESETS, flatten

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
sys.path.insert(0, str(HERE.parent / "cad"))
from render import PRINT_LAYOUT  # noqa: E402  (imports cadquery and pyvista, like render.py itself)

OUT_3MF = HERE / "piper_camera_mount_A1mini_PLA.3mf"
OVERRIDES = {"wall-loops": "3", "sparse-infill-density": "25%", "curr-bed-type": "Textured PEI Plate"}
# Bambu's "Auto circle contour-hole compensation", off in the stock process preset. It resizes
# round holes and bosses by the error model in the PLA Basic filament preset, which otherwise
# prints an M3 clearance hole about 0.4 mm small (#234's fit_sim.py). Support is already off in
# the stock preset; it is pinned here so the report says so. Both are set in the preset file
# because the CLI takes booleans only as bare flags.
PROCESS_SETTINGS = {"enable_circle_compensation": "1", "enable_support": "0"}
OSMESA = Path("/usr/lib/x86_64-linux-gnu/libOSMesa.so.8")
FILAMENT_COLOUR = "#000000"
BED = 180.0

# (plate name, [(part, x, y)]) -- x, y is where the centre of the part's footprint lands on the
# bed; "tag_wedge#2" is a second copy of tag_wedge.stl.
PLATES = [
    ("PiPER camera mount", [(part, x, y) for part, (x, y) in PRINT_LAYOUT.items()]),
]


def stl_bounds(path: Path) -> np.ndarray:
    """[[xmin, ymin, zmin], [xmax, ymax, zmax]] of a binary STL, which is what cadquery writes."""
    data = path.read_bytes()
    n = int.from_bytes(data[80:84], "little")
    if len(data) != 84 + 50 * n:
        raise SystemExit(f"{path} is not a binary STL")
    tri = np.dtype([("normal", "<f4", 3), ("v", "<f4", (3, 3)), ("attr", "<u2")])
    v = np.frombuffer(data, tri, count=n, offset=84)["v"].reshape(-1, 3)
    return np.array([v.min(0), v.max(0)])


def layout() -> tuple[list[list[dict]], list[str]]:
    """Each part's footprint on the bed from its STL's bounding box, per plate, and warnings for any
    that leave the bed or overlap. Bounding boxes only, so an overlap may still be a near miss."""
    plates, warnings = [], []
    for _, objs in PLATES:
        parts = []
        for part, x, y in objs:
            stl = EXPORTS / f"{part.split('#')[0]}.stl"
            (x0, y0, z0), (x1, y1, z1) = stl_bounds(stl)
            box = [x - (x1 - x0) / 2, y - (y1 - y0) / 2, x + (x1 - x0) / 2, y + (y1 - y0) / 2]
            parts.append({"part": part, "stl": stl.name, "sha256": hashlib.sha256(stl.read_bytes()).hexdigest()[:12],
                          "centre": [x, y], "footprint": [round(float(c), 2) for c in box],
                          "height": round(float(z1 - z0), 2),
                          # the CLI puts the STL's origin at pos, so offset by the box centre
                          "pos": [float(x - (x0 + x1) / 2), float(y - (y0 + y1) / 2)]})
            if min(box) < 0 or max(box) > BED:
                warnings.append(f"{part} leaves the {BED:g} mm bed: footprint x {box[0]:.1f}..{box[2]:.1f}, "
                                f"y {box[1]:.1f}..{box[3]:.1f}")
        for a, b in itertools.combinations(parts, 2):
            fa, fb = a["footprint"], b["footprint"]
            ox, oy = min(fa[2], fb[2]) - max(fa[0], fb[0]), min(fa[3], fb[3]) - max(fa[1], fb[1])
            if ox > 0 and oy > 0:
                warnings.append(f"{a['part']} and {b['part']} overlap by {ox:.1f} x {oy:.1f} mm (bounding boxes)")
        plates.append(parts)
    return plates, warnings


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


def write_assemble_list(build: Path, placed: list[list[dict]]) -> Path:
    # One entry per copy. With "count": 2 the CLI adds the second position to the first
    # (pos_x [70, 85] puts the copy at x 155). The cost is that both copies are named "tag_wedge_1".
    plates = [{"plate_name": name, "need_arrange": False,
               "objects": [{"path": str(EXPORTS / p["stl"]), "count": 1, "filaments": [1],
                            "pos_x": [p["pos"][0]], "pos_y": [p["pos"][1]], "pos_z": [0]} for p in parts]}
              for (name, _), parts in zip(PLATES, placed)]
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


def report(build: Path, log: str, placed: list[list[dict]], layout_warnings: list[str]) -> dict:
    result = json.loads((build / "result.json").read_text())
    with zipfile.ZipFile(build / OUT_3MF.name) as z:
        info = ET.fromstring(z.read("Metadata/slice_info.config"))
        names = z.namelist()
        gcode = {n: z.read(f"Metadata/plate_{n}.gcode").decode() for n in range(1, len(PLATES) + 1)}
    version = re.search(r"Current BambuStudio Version (\S+)", log)
    slicing_warnings = re.findall(r"plate (\d+): found (?:NON_CRITICAL )?slicing warnings: (.*)", log)
    # PrintObject::generate_support_material runs this check on every object when support is off,
    # and raises "It seems object X has floating regions / floating cantilever / large overhangs".
    support_checks = len(re.findall(r"is_support_necessary takes", log))
    support_flags = [{"plate": int(p), "object": m.group(1), "reason": m.group(2)} for p, w in slicing_warnings
                     if (m := re.search(r"It seems object (.+?) has (.+?)\. Please re-orient", w))]
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
        "support_necessity_flags": support_flags,
        "layout": [{k: v for k, v in p.items() if k != "pos"} for parts in placed for p in parts],
        "layout_warnings": layout_warnings,
        "thumbnails_embedded": sorted(n for n in names if n.endswith(".png")),
        "plates": plates,
        "total_print_time_s": sum(p["print_time_s"] for p in plates),
        "total_filament_g": round(sum(p["filament_g"] for p in plates), 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bambu", type=lambda s: Path(s).expanduser().resolve(), required=True,
                    help="extracted AppImage (squashfs-root)")
    ap.add_argument("--build", type=Path, default=HERE / "build")
    args = ap.parse_args()
    shutil.rmtree(args.build, ignore_errors=True)
    args.build.mkdir(parents=True)
    placed, layout_warnings = layout()
    for w in layout_warnings:
        print(f"LAYOUT WARNING: {w}", file=sys.stderr)
    presets = write_presets(args.bambu / "resources", args.build)
    env = gl_env(args.build)
    log = run_cli(args.bambu, presets, write_assemble_list(args.build, placed), args.build, env)
    rep = report(args.build, log, placed, layout_warnings)
    shutil.copy(args.build / OUT_3MF.name, OUT_3MF)
    (HERE / "report.json").write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
