#!/usr/bin/env python3
"""Slice the Christmas toy drive shortlist (toys.json) for the lab's A1 mini in PLA Basic, one
toy per plate, with the Bambu Studio CLI, and table grams, cost and time.

    python slice_toys.py --bambu ~/bambu/squashfs-root            # every toy in toys.json
    python slice_toys.py --bambu ~/bambu/squashfs-root --only worry-stone

Needs trimesh (``pip install trimesh numpy lxml networkx``) and the extracted Bambu Studio
02.08.02.61 AppImage (``bambu/studio/setup_runner.sh`` downloads and checks it). Writes, next to
this file:

- ``3mf/<slug>_A1mini_PLA.gcode.3mf``: the sliced plate, ready to send
- ``thumbs/<slug>.png``: the plate thumbnail Studio renders into the 3MF
- ``report.json``: per toy, the slicer's grams, time, layers and bounding box, and the cost

How each toy is handled:

- The model file comes straight from Printables (the file id in toys.json) and is checked
  against the sha256 recorded there, so a designer's later update can't change a toy silently.
- The mesh is only moved so that its footprint is centred on the 180 x 180 mm bed. Two toys are
  also turned, both under licenses that allow it: the octopus 59 degrees about Z so its legs fit
  the bed, the phone stand onto its side, as its designer advises. Nothing is scaled.
- Bambu's own system presets, flattened because the CLI follows neither ``inherits`` nor
  ``include``: machine "Bambu Lab A1 mini 0.4 nozzle", filament "Bambu PLA Basic @BBL A1M",
  process "0.20mm Standard @BBL A1M" unless toys.json names another (the shark uses 0.16 mm,
  as its designer recommends). On top: no brim (a brim can fuse print-in-place joints), the
  Textured PEI plate, and any per-toy settings in toys.json (the marble maze's 0.5 mm lines).
- Cost is grams x the price per kg given with --usd-per-kg (default 18.99, Bambu's typical
  price for a 1 kg PLA Basic refill on its US store, read 2026-11-26).
- Plate thumbnails need an OpenGL context: run a headless Wayland display first
  (``weston --backend=headless --socket=wayland-bambu &``, then
  ``export WAYLAND_DISPLAY=wayland-bambu``) with libOSMesa and gcc installed. Without them the
  slice is the same, but has no pictures. The GL shim is byu-vcl's (see
  bambu/evidence/2026-11-09/stub-holder-bottoms/slice_a1mini.py on PR 257's branch, which this
  script follows).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MACHINE = "Bambu Lab A1 mini 0.4 nozzle"
FILAMENT = "Bambu PLA Basic @BBL A1M"
BED = "Textured PEI Plate"
BED_CENTRE = (90.0, 90.0)  # the A1 mini's bed is 180 x 180 mm
FILAMENT_COLOUR = "#0A2989"  # the dark blue PLA Basic in the A1 mini's AMS Lite slot A1 on 2026-11-26
ALWAYS = {"brim_type": "no_brim"}
LIMITS = {"grams": 250, "usd": 4.00, "hours": 8}
PRINTABLES = "https://api.printables.com/graphql/"
OSMESA = Path("/usr/lib/x86_64-linux-gnu/libOSMesa.so.8")
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


# ----------------------------------------------------------------------------- model files


def fetch(toy: dict, cache: Path) -> Path:
    """The toy's file from Printables, in its own folder, checked against toys.json's sha256."""
    folder = cache / toy["slug"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / toy["file_name"]
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != toy["sha256"]:
        query = ("mutation($id: ID!, $printId: ID!) { getDownloadLink(id: $id, printId: $printId, "
                 "fileType: stl, source: model_detail) { ok output { link } } }")
        body = json.dumps({"query": query, "variables": {"id": toy["printables_file_id"],
                                                         "printId": toy["printables_model_id"]}}).encode()
        req = urllib.request.Request(PRINTABLES, data=body, headers={"content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            link = json.load(r)["data"]["getDownloadLink"]["output"]["link"]
        with urllib.request.urlopen(urllib.request.Request(link, headers={"user-agent": "Mozilla/5.0"}),
                                    timeout=600) as r:
            path.write_bytes(r.read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != toy["sha256"]:
        raise SystemExit(f"{toy['slug']}: sha256 {digest} is not the {toy['sha256']} in toys.json; "
                         "the designer may have updated the file, so check it before slicing")
    return path


def prepare_mesh(toy: dict, src: Path, build: Path) -> tuple[Path, list[float]]:
    """Turn the mesh if toys.json says to, centre its footprint on the origin, rest it on z = 0."""
    import numpy as np
    import trimesh

    mesh = trimesh.load(src, force="mesh")
    for axis, key in (([0, 1, 0], "rotate_y_deg"), ([0, 0, 1], "rotate_z_deg")):
        deg = (toy.get("transform") or {}).get(key)
        if deg:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(deg), axis))
    lo, hi = mesh.bounds
    mesh.apply_translation([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    out = build / f"{toy['slug']}.stl"
    mesh.export(out)
    return out, [round(float(v), 1) for v in mesh.extents]


# ----------------------------------------------------------------------------- presets


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


def write_presets(toy: dict, profiles: Path, build: Path) -> dict[str, Path]:
    process = flatten("process", toy["process"], profiles)
    process.update(ALWAYS)
    process.update(toy.get("process_settings") or {})
    filament = flatten("filament", FILAMENT, profiles)
    filament["filament_colour"] = [FILAMENT_COLOUR]
    paths = {}
    for kind, cfg in (("machine", flatten("machine", MACHINE, profiles)), ("process", process),
                      ("filament", filament)):
        paths[kind] = build / f"{kind}.json"
        paths[kind].write_text(json.dumps(cfg, indent=2) + "\n")
    return paths


def ensure_model_id(profiles: Path) -> None:
    """The CLI reads the printer's model id from machine_full/, which the AppImage doesn't ship."""
    model = json.loads((profiles / "machine" / f"{MACHINE}.json").read_text())["printer_model"]
    full = profiles / "machine_full" / f"{model}.json"
    if not full.exists():
        full.parent.mkdir(exist_ok=True)
        shutil.copy(profiles / "machine" / f"{model}.json", full)


def gl_env(build: Path) -> dict[str, str]:
    env = os.environ.copy()
    if not (env.get("WAYLAND_DISPLAY") and OSMESA.exists() and shutil.which("gcc")):
        print("no Wayland display or libOSMesa: slicing without thumbnails")
        return env
    shim = build.parent / "libglxshim.so"
    if not shim.exists():
        (build.parent / "glxshim.c").write_text(GLXSHIM)
        subprocess.run(["gcc", "-shared", "-fPIC", "-O2", "-o", str(shim), str(build.parent / "glxshim.c"),
                        f"-l:{OSMESA.name}"], check=True)
    env["LD_PRELOAD"] = f"{shim}:{OSMESA}"
    return env


# ----------------------------------------------------------------------------- slice


def hms(seconds: int) -> str:
    h, rem = divmod(int(seconds), 3600)
    return f"{h} h {rem // 60:02d} min"


def slice_toy(toy: dict, args) -> dict:
    build = args.build / toy["slug"]
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir(parents=True)
    profiles = args.bambu / "resources" / "profiles" / "BBL"
    ensure_model_id(profiles)
    stl, extents = prepare_mesh(toy, fetch(toy, args.cache), build)
    presets = write_presets(toy, profiles, build)
    plate = {"plate_name": toy["slug"], "need_arrange": False,
             "objects": [{"path": str(stl), "count": 1, "filaments": [1],
                          "pos_x": [BED_CENTRE[0]], "pos_y": [BED_CENTRE[1]], "pos_z": [0]}]}
    (build / "assemble.json").write_text(json.dumps({"plates": [plate]}, indent=1) + "\n")
    out_name = f"{toy['slug']}_A1mini_PLA.gcode.3mf"
    cmd = [str(args.bambu / "AppRun"), "--debug", "3",
           "--load-settings", f"{presets['machine']};{presets['process']}",
           "--load-filaments", str(presets["filament"]),
           "--load-assemble-list", str(build / "assemble.json"),
           "--curr-bed-type", BED,
           "--slice", "0", "--outputdir", str(build), "--export-3mf", out_name]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=gl_env(build))
    log = proc.stdout + proc.stderr
    (build / "cli.log").write_text(log)
    if proc.returncode != 0:
        return {"slug": toy["slug"], "error": f"Bambu Studio CLI exited {proc.returncode}; see {build / 'cli.log'}"}

    result = json.loads((build / "result.json").read_text())
    sliced = result["sliced_plates"][0]
    with zipfile.ZipFile(build / out_name) as z:
        info = ET.fromstring(z.read("Metadata/slice_info.config")).find("plate")
        gcode = z.read("Metadata/plate_1.gcode").decode()
        thumb = z.read("Metadata/plate_1.png") if "Metadata/plate_1.png" in z.namelist() else None
    meta = {m.get("key"): m.get("value") for m in info.findall("metadata")}
    fil = info.find("filament")
    grams = float(fil.get("used_g"))
    seconds = int(meta["prediction"])
    usd = round(grams * args.usd_per_kg / 1000, 2)
    over = [k for k, ok in (("grams", grams <= LIMITS["grams"]), ("usd", usd <= LIMITS["usd"]),
                            ("hours", seconds <= LIMITS["hours"] * 3600)) if not ok]
    (args.out / "3mf").mkdir(exist_ok=True)
    shutil.copy(build / out_name, args.out / "3mf" / out_name)
    if thumb:
        (args.out / "thumbs").mkdir(exist_ok=True)
        (args.out / "thumbs" / f"{toy['slug']}.png").write_bytes(thumb)
    return {
        "slug": toy["slug"], "file": f"3mf/{out_name}",
        "presets": {"machine": MACHINE, "process": toy["process"], "filament": FILAMENT},
        "set_on_top_of_presets": {"curr_bed_type": BED, "filament_colour": FILAMENT_COLOUR, **ALWAYS,
                                  **(toy.get("process_settings") or {})},
        "transform": toy.get("transform"), "extents_on_bed_mm": extents,
        "return_code": result["return_code"], "error_string": result["error_string"],
        "filament_g": round(grams, 1), "filament_m": round(float(fil.get("used_m")), 2),
        "cost_usd": usd, "usd_per_kg": args.usd_per_kg,
        "prediction_s": seconds, "print_time": hms(seconds),
        "plates": 1,
        "layers": int(re.search(r"^; total layer number: (\d+)", gcode, re.M).group(1)),
        "max_z_mm": float(re.search(r"^; max_z_height: ([\d.]+)", gcode, re.M).group(1)),
        "toolpath_outside_bed": meta.get("outside") == "true",
        "support_used": meta.get("support_used") == "true",
        "slicer_warnings": re.findall(r"found (?:NON_CRITICAL )?slicing warnings: (.*)", log),
        "gcode_warnings": [w.get("msg") for w in info.findall("warning")],
        "thumbnail": f"thumbs/{toy['slug']}.png" if thumb else None,
        "over_limits": over,
        "bambu_studio": (re.search(r"Current BambuStudio Version (\S+)", log) or [None, None])[1],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bambu", type=Path, required=True, help="extracted AppImage (squashfs-root)")
    ap.add_argument("--toys", type=Path, default=HERE / "toys.json")
    ap.add_argument("--only", nargs="*", help="slugs to slice (default: all)")
    ap.add_argument("--usd-per-kg", type=float, default=18.99)
    ap.add_argument("--cache", type=Path, default=Path("/tmp/toy-models"), help="where model files are kept")
    ap.add_argument("--build", type=Path, default=Path("/tmp/toy-build"))
    ap.add_argument("--out", type=Path, default=HERE)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    toys = json.loads(args.toys.read_text())
    if args.only:
        toys = [t for t in toys if t["slug"] in args.only]
    report_path = args.out / "report.json"
    report = {r["slug"]: r for r in json.loads(report_path.read_text())} if report_path.exists() else {}
    for toy in toys:
        r = slice_toy(toy, args)
        report[toy["slug"]] = r
        print(json.dumps({k: r.get(k) for k in ("slug", "filament_g", "cost_usd", "print_time", "layers",
                                                "extents_on_bed_mm", "over_limits", "error",
                                                "slicer_warnings", "gcode_warnings")}))
    order = [t["slug"] for t in json.loads(args.toys.read_text())]
    rows = sorted(report.values(), key=lambda r: order.index(r["slug"]) if r["slug"] in order else 99)
    report_path.write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    main()
