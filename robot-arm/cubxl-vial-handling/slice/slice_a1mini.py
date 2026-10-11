#!/usr/bin/env python3
"""Slice the mock-up v2 parts for a Bambu Lab A1 mini in PLA, supports off, with the Bambu Studio CLI.

    python slice/slice_a1mini.py --bambu ~/bambu/squashfs-root   # an extracted Bambu Studio AppImage

Adapted from piper-camera-mount/slice/slice_a1mini.py on #245 (itself from #238 and #234), with the
same settings: Bambu's system presets "Bambu Lab A1 mini 0.4 nozzle", "0.20mm Standard @BBL A1M" and
"Bambu PLA Basic @BBL A1M", flattened by flatten_presets.py, then 3 walls, 25 % infill, the Textured PEI
plate, Bambu's circle compensation, and supports off.

Two projects, both from the STLs in ../exports as exported (print orientation, standing on z = 0):
- mockup_v2_A1mini_PLA.3mf: the print job, every part on 180 x 180 mm beds. Each offset plate is
  printed twice, one for each dock block, so a whole test set is on the beds.
- per-part run (build/, not kept): one part per bed, so each part's mass and time come from its own
  G-code. Those numbers go into report.json, which is what the payload uses.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np

from flatten_presets import PRESETS, flatten

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
OUT_3MF = HERE / "mockup_v2_A1mini_PLA.3mf"
OVERRIDES = {"wall-loops": "3", "sparse-infill-density": "25%", "curr-bed-type": "Textured PEI Plate"}
PROCESS_SETTINGS = {"enable_circle_compensation": "1", "enable_support": "0"}
OSMESA = Path("/usr/lib/x86_64-linux-gnu/libOSMesa.so.8")
FILAMENT_COLOUR = "#f2a900"
BED = 180.0

PLATE_DESIGNS = ["plate_0", "plate_x+1mm", "plate_x+2mm", "plate_x+3mm", "plate_x+4mm", "plate_y+1mm",
                 "plate_y+2mm", "plate_y+3mm", "plate_y+4mm", "plate_yaw+2deg", "plate_yaw-2deg",
                 "plate_yaw+4deg", "plate_yaw-4deg"]
GRID6 = [(30, 50), (90, 50), (150, 50), (30, 130), (90, 130), (150, 130)]


def _plates_beds():
    each = [p for p in PLATE_DESIGNS for _ in (0, 1)]
    beds = []
    for k in range(0, len(each), 6):
        chunk = each[k:k + 6]
        seen = {}
        objs = []
        for part, (x, y) in zip(chunk, GRID6):
            seen[part] = seen.get(part, 0) + 1
            objs.append((f"{part}#{seen[part]}", x, y))
        beds.append((f"Offset plates {k // 6 + 1}", objs))
    return beds


# (bed name, [(part, x, y)]): x, y is where the centre of the part's footprint lands on the bed
JOB = [
    ("Carrier", [("carrier_half_a", 40, 90), ("carrier_half_b", 88, 90), ("handle_post", 142, 90)]),
    ("Dock and finger inserts", [("dock_block#1", 35, 55), ("dock_block#2", 100, 55),
                                 ("finger_insert_upper", 44, 142), ("finger_insert_lower", 134, 142)]),
] + _plates_beds()
PER_PART = [(p, [(p, 90, 90)]) for p in ["carrier_half_a", "carrier_half_b", "handle_post", "dock_block",
                                         "finger_insert_upper", "finger_insert_lower"] + PLATE_DESIGNS]


def stl_bounds(path: Path) -> np.ndarray:
    data = path.read_bytes()
    n = int.from_bytes(data[80:84], "little")
    if len(data) != 84 + 50 * n:
        raise SystemExit(f"{path} is not a binary STL")
    tri = np.dtype([("normal", "<f4", 3), ("v", "<f4", (3, 3)), ("attr", "<u2")])
    v = np.frombuffer(data, tri, count=n, offset=84)["v"].reshape(-1, 3)
    return np.array([v.min(0), v.max(0)])


def layout(beds):
    placed, warnings = [], []
    for _, objs in beds:
        parts = []
        for part, x, y in objs:
            stl = EXPORTS / f"{part.split('#')[0]}.stl"
            (x0, y0, z0), (x1, y1, z1) = stl_bounds(stl)
            box = [x - (x1 - x0) / 2, y - (y1 - y0) / 2, x + (x1 - x0) / 2, y + (y1 - y0) / 2]
            parts.append({"part": part, "stl": stl.name, "sha256": hashlib.sha256(stl.read_bytes()).hexdigest()[:12],
                          "centre": [x, y], "footprint": [round(float(c), 2) for c in box],
                          "height": round(float(z1 - z0), 2),
                          "pos": [float(x - (x0 + x1) / 2), float(y - (y0 + y1) / 2)]})
            if min(box) < 0 or max(box) > BED:
                warnings.append(f"{part} leaves the {BED:g} mm bed: x {box[0]:.1f}..{box[2]:.1f}, y {box[1]:.1f}..{box[3]:.1f}")
        for a, b in itertools.combinations(parts, 2):
            fa, fb = a["footprint"], b["footprint"]
            ox, oy = min(fa[2], fb[2]) - max(fa[0], fb[0]), min(fa[3], fb[3]) - max(fa[1], fb[1])
            if ox > 0 and oy > 0:
                warnings.append(f"{a['part']} and {b['part']} overlap by {ox:.1f} x {oy:.1f} mm (bounding boxes)")
        placed.append(parts)
    return placed, warnings


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


def write_assemble_list(build: Path, beds, placed) -> Path:
    plates = [{"plate_name": name, "need_arrange": False,
               "objects": [{"path": str(EXPORTS / p["stl"]), "count": 1, "filaments": [1],
                            "pos_x": [p["pos"][0]], "pos_y": [p["pos"][1]], "pos_z": [0]} for p in parts]}
              for (name, _), parts in zip(beds, placed)]
    path = build / "assemble.json"
    path.write_text(json.dumps({"plates": plates}, indent=1) + "\n")
    return path


def gl_env(build: Path) -> dict[str, str]:
    env = os.environ.copy()
    if not (env.get("WAYLAND_DISPLAY") and OSMESA.exists() and shutil.which("gcc")):
        print("no Wayland display or libOSMesa: slicing without thumbnails")
        return env
    shim = build / "libglxshim.so"
    subprocess.run(["gcc", "-shared", "-fPIC", "-O2", "-o", str(shim), str(HERE / "glxshim.c"),
                    f"-l:{OSMESA.name}"], check=True)
    env["LD_PRELOAD"] = f"{shim}:{OSMESA}"
    return env


def run_cli(bambu: Path, presets, assemble: Path, build: Path, env, name: str) -> str:
    cmd = [str(bambu / "AppRun"), "--debug", "3",
           "--load-settings", f"{presets['machine']};{presets['process']}",
           "--load-filaments", str(presets["filament"]),
           "--load-assemble-list", str(assemble)]
    for k, v in OVERRIDES.items():
        cmd += [f"--{k}", v]
    cmd += ["--slice", "0", "--outputdir", str(build), "--export-3mf", name]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    log = proc.stdout + proc.stderr
    (build / f"{Path(name).stem}.cli.log").write_text(log)
    if proc.returncode != 0:
        raise SystemExit(f"Bambu Studio CLI exited {proc.returncode}; see {build}")
    return log


def report(build: Path, log: str, name: str, beds, placed, layout_warnings) -> dict:
    result = json.loads((build / "result.json").read_text())
    with zipfile.ZipFile(build / name) as z:
        info = ET.fromstring(z.read("Metadata/slice_info.config"))
        names = z.namelist()
        gcode = {n: z.read(f"Metadata/plate_{n}.gcode").decode() for n in range(1, len(beds) + 1)}
    version = re.search(r"Current BambuStudio Version (\S+)", log)
    slicing_warnings = re.findall(r"plate (\d+): found (?:NON_CRITICAL )?slicing warnings: (.*)", log)
    support_checks = len(re.findall(r"is_support_necessary takes", log))
    support_flags = [{"plate": int(p), "object": m.group(1), "reason": m.group(2)} for p, w in slicing_warnings
                     if (m := re.search(r"It seems object (.+?) has (.+?)\. Please re-orient", w))]
    out = []
    for sliced, (bname, _), xml, parts in zip(result["sliced_plates"], beds, info.findall("plate"), placed):
        meta = {m.get("key"): m.get("value") for m in xml.findall("metadata")}
        fil = xml.find("filament")
        g = gcode[sliced["id"]]
        out.append({
            "plate": sliced["id"], "name": bname, "objects": [o["name"] for o in sliced["objects"]],
            "parts": [p["part"] for p in parts],
            "print_time_s": round(sliced["total_predication"]),
            "filament_g": float(fil.get("used_g")), "filament_m": float(fil.get("used_m")),
            "layers": int(re.findall(r"^; total layer number: (\d+)", g, re.M)[0])
            if re.search(r"^; total layer number: (\d+)", g, re.M) else None,
            "bed_type": re.search(r"^; curr_bed_type = (.*)$", g, re.M).group(1),
            "toolpath_outside_bed": meta.get("outside") == "true",
            "support_used": meta.get("support_used") == "true",
            "support_extrusion_in_gcode": bool(re.search(r"^; FEATURE: Support", g, re.M)),
            "slicer_warnings": [w for p, w in slicing_warnings if int(p) == sliced["id"]],
            "gcode_warnings": [{"msg": w.get("msg"), "level": int(w.get("level")), "code": w.get("error_code")}
                               for w in xml.findall("warning")],
        })
    return {
        "bambu_studio": version.group(1) if version else None,
        "presets": PRESETS, "overrides": {**{k.replace("-", "_"): v for k, v in OVERRIDES.items()}, **PROCESS_SETTINGS},
        "return_code": result["return_code"], "error_string": result["error_string"],
        "support_necessity_checks_run": support_checks, "support_necessity_flags": support_flags,
        "layout": [{k: v for k, v in p.items() if k != "pos"} for parts in placed for p in parts],
        "layout_warnings": layout_warnings,
        "thumbnails_embedded": sorted(n for n in names if n.endswith(".png")),
        "plates": out,
        "total_print_time_s": sum(p["print_time_s"] for p in out),
        "total_filament_g": round(sum(p["filament_g"] for p in out), 2),
    }


def run(bambu: Path, build: Path, beds, name: str, env) -> dict:
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir(parents=True)
    placed, warnings = layout(beds)
    for w in warnings:
        print(f"LAYOUT WARNING: {w}", file=sys.stderr)
    presets = write_presets(bambu / "resources", build)
    env = gl_env(build) if env is None else env
    log = run_cli(bambu, presets, write_assemble_list(build, beds, placed), build, env, name)
    return report(build, log, name, beds, placed, warnings)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bambu", type=lambda s: Path(s).expanduser().resolve(), required=True)
    ap.add_argument("--build", type=Path, default=HERE / "build")
    args = ap.parse_args()
    job = run(args.bambu, args.build / "job", JOB, OUT_3MF.name, None)
    shutil.copy(args.build / "job" / OUT_3MF.name, OUT_3MF)
    each = run(args.bambu, args.build / "per_part", PER_PART, "per_part.3mf", None)
    per_part = {p["parts"][0]: {k: p[k] for k in ("print_time_s", "filament_g", "filament_m", "support_used",
                                                   "support_extrusion_in_gcode", "slicer_warnings")}
                for p in each["plates"]}
    rep = dict(job=job, per_part=per_part, per_part_support_flags=each["support_necessity_flags"],
               per_part_support_checks_run=each["support_necessity_checks_run"])
    (HERE / "report.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps({"job": {k: job[k] for k in ("bambu_studio", "return_code", "support_necessity_flags",
                                                   "layout_warnings", "total_print_time_s", "total_filament_g")},
                      "per_part": per_part}, indent=1))


if __name__ == "__main__":
    main()
