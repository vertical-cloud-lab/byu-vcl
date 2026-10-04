#!/usr/bin/env python3
"""Slice the PiPER camera mount three ways, each part on its own plate too, for mass and for the FEA.

    python slice_configs.py --bambu ~/bambu/squashfs-root [--config h2d_pahtcf_06 ...]

slice_a1mini.py makes the one-plate job for the A1 mini in PLA. This does the same for the
configurations the material question is about, and adds one plate per part, so that each part's
mass and its own G-code (in its own print frame) come out separately:

  h2d_pahtcf_04   H2D, 0.4 mm hardened steel (fitted now), Bambu PAHT-CF, 0.20mm Standard
  h2d_pahtcf_06   H2D, 0.6 mm hardened steel (Bambu's recommendation for PAHT-CF), 0.30mm Standard
  a1m_pla_04      A1 mini, 0.4 mm, Bambu PLA Basic, 0.20mm Standard (the README's PLA print)

Every configuration uses Bambu's own system presets with the README's overrides on top: 3 walls,
25 % grid infill, circle compensation on, supports off, Textured PEI. Plate 1 is the whole job
(PRINT_LAYOUT from ../cad/render.py); plates 2-6 are bracket, pod, carrier, spacers and one
tag_wedge alone, centred on the bed. Writes build_<config>/<config>.3mf (ignored by git) and
slice_configs.json here: per plate the slicer's time and filament, and per part the mass from the
G-code itself, split by feature (outer wall, sparse infill, ...).
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from flatten_presets import flatten
from slice_a1mini import gl_env, stl_bounds

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
sys.path.insert(0, str(HERE.parent / "cad"))
from render import PRINT_LAYOUT  # noqa: E402

CONFIGS = {
    "h2d_pahtcf_04": {"machine": "Bambu Lab H2D 0.4 nozzle", "process": "0.20mm Standard @BBL H2D",
                      "filament": "Bambu PAHT-CF @BBL H2D", "bed": (350.0, 320.0)},
    "h2d_pahtcf_06": {"machine": "Bambu Lab H2D 0.6 nozzle", "process": "0.30mm Standard @BBL H2D 0.6 nozzle",
                      "filament": "Bambu PAHT-CF @BBL H2D 0.6 nozzle", "bed": (350.0, 320.0)},
    "a1m_pla_04": {"machine": "Bambu Lab A1 mini 0.4 nozzle", "process": "0.20mm Standard @BBL A1M",
                   "filament": "Bambu PLA Basic @BBL A1M", "bed": (180.0, 180.0)},
}
OVERRIDES = {"wall-loops": "3", "sparse-infill-density": "25%", "curr-bed-type": "Textured PEI Plate"}
PROCESS_SETTINGS = {"enable_circle_compensation": "1", "enable_support": "0"}
SINGLE = ["bracket", "pod", "carrier", "spacers", "tag_wedge"]


def plates_for(bed: tuple[float, float]) -> list[tuple[str, list[tuple[str, float, float]]]]:
    job = [(part, x, y) for part, (x, y) in PRINT_LAYOUT.items()]
    return [("job", job)] + [(part, [(part, bed[0] / 2, bed[1] / 2)]) for part in SINGLE]


def assemble(plates, build: Path) -> Path:
    out = []
    for name, objs in plates:
        objects = []
        for part, x, y in objs:
            stl = EXPORTS / f"{part.split('#')[0]}.stl"
            (x0, y0, _), (x1, y1, _) = stl_bounds(stl)
            objects.append({"path": str(stl), "count": 1, "filaments": [1],
                            "pos_x": [float(x - (x0 + x1) / 2)], "pos_y": [float(y - (y0 + y1) / 2)], "pos_z": [0]})
        out.append({"plate_name": name, "need_arrange": False, "objects": objects})
    path = build / "assemble.json"
    path.write_text(json.dumps({"plates": out}, indent=1) + "\n")
    return path


def gcode_mass(gcode: str, filament_d: float, density: float) -> dict:
    """Filament pushed per feature, from the G-code: relative E (M83) summed per '; FEATURE:' block,
    retractions and their re-primes cancelling. Grams, at the filament preset's density."""
    area = 3.141592653589793 * (filament_d / 2) ** 2
    feat, per = "start", {}
    relative = True
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line[10:].strip()
        elif line.startswith("M83"):
            relative = True
        elif line.startswith("M82"):
            relative = False
        elif line.startswith(("G1 ", "G0 ", "G2 ", "G3 ")) and " E" in line and relative:
            m = re.search(r" E(-?[\d.]+)", line)
            if m:
                per[feat] = per.get(feat, 0.0) + float(m.group(1))
    grams = {k: round(v * area * density / 1000.0, 3) for k, v in per.items()}
    return grams


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bambu", type=lambda s: Path(s).expanduser().resolve(), required=True)
    ap.add_argument("--config", nargs="*", default=list(CONFIGS))
    args = ap.parse_args()
    out_json = HERE / "slice_configs.json"
    report = json.loads(out_json.read_text()) if out_json.exists() else {}
    for cfg_name in args.config:
        cfg = CONFIGS[cfg_name]
        build = HERE / f"build_{cfg_name}"
        shutil.rmtree(build, ignore_errors=True)
        build.mkdir(parents=True)
        presets = {}
        for kind in ("machine", "process", "filament"):
            c = flatten(kind, cfg[kind], args.bambu / "resources" / "profiles" / "BBL")
            if kind == "process":
                c.update(PROCESS_SETTINGS)
            presets[kind] = build / f"{kind}.json"
            presets[kind].write_text(json.dumps(c, indent=2) + "\n")
        fil = json.loads(presets["filament"].read_text())
        density = float(fil["filament_density"][0])
        diameter = float(fil.get("filament_diameter", ["1.75"])[0])
        proc = json.loads(presets["process"].read_text())
        plates = plates_for(cfg["bed"])
        cmd = [str(args.bambu / "AppRun"), "--debug", "3",
               "--load-settings", f"{presets['machine']};{presets['process']}",
               "--load-filaments", str(presets["filament"]),
               "--load-assemble-list", str(assemble(plates, build))]
        for k, v in OVERRIDES.items():
            cmd += [f"--{k}", v]
        cmd += ["--slice", "0", "--outputdir", str(build), "--export-3mf", f"{cfg_name}.3mf"]
        proc_run = subprocess.run(cmd, capture_output=True, text=True, env=gl_env(build))
        (build / "cli.log").write_text(proc_run.stdout + proc_run.stderr)
        if proc_run.returncode != 0:
            raise SystemExit(f"{cfg_name}: CLI exited {proc_run.returncode}; see {build / 'cli.log'}")
        result = json.loads((build / "result.json").read_text())
        rep = {"presets": {k: cfg[k] for k in ("machine", "process", "filament")},
               "overrides": {**{k.replace("-", "_"): v for k, v in OVERRIDES.items()}, **PROCESS_SETTINGS},
               "layer_height_mm": float(proc["layer_height"]),
               "line_width_mm": {k: float(proc[k]) for k in ("outer_wall_line_width", "inner_wall_line_width",
                                                              "sparse_infill_line_width",
                                                              "internal_solid_infill_line_width",
                                                              "top_surface_line_width")},
               "sparse_infill_pattern": proc["sparse_infill_pattern"],
               "filament_density_g_cm3": density, "plates": []}
        with zipfile.ZipFile(build / f"{cfg_name}.3mf") as z:
            info = ET.fromstring(z.read("Metadata/slice_info.config"))
            for sliced, (name, objs), xml in zip(result["sliced_plates"], plates, info.findall("plate")):
                g = z.read(f"Metadata/plate_{sliced['id']}.gcode").decode()
                (build / f"plate_{sliced['id']}_{name}.gcode").write_text(g)
                f = xml.find("filament")
                feats = gcode_mass(g, diameter, density)
                part_g = round(sum(v for k, v in feats.items() if k not in ("start", "Custom", "Prime tower")), 2)
                rep["plates"].append({
                    "plate": sliced["id"], "name": name, "objects": [o["name"] for o in sliced["objects"]],
                    "stl_sha256": {p.split('#')[0]: hashlib.sha256((EXPORTS / f"{p.split('#')[0]}.stl").read_bytes())
                                   .hexdigest()[:12] for p, _, _ in objs},
                    "print_time_s": round(sliced["total_predication"]),
                    "slicer_filament_g": float(f.get("used_g")), "slicer_filament_m": float(f.get("used_m")),
                    "gcode_g_by_feature": feats, "part_g_from_gcode": part_g})
        rep["bambu_studio"] = (re.search(r"Current BambuStudio Version (\S+)", proc_run.stdout + proc_run.stderr)
                               or [None, None])[1]
        report[cfg_name] = rep
        print(cfg_name, json.dumps([{k: p[k] for k in ("name", "print_time_s", "slicer_filament_g",
                                                         "part_g_from_gcode")} for p in rep["plates"]], indent=0))
    out_json.write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
