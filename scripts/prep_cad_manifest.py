"""Merge CAD inventory manifests and convert STEP files so scripts/render_cad.py can read them.

    python -I scripts/prep_cad_manifest.py merged.json a.json b.json \
        --cq-python /path/to/cadquery-env/bin/python --work /tmp/cad-render-input

For every design, `render_files` lists what the renderer should load: its mesh files as they
are, plus one STL per solid for each STEP file (made with scripts/step_to_stl.py in the
CadQuery environment). Designs are sorted by `first_seen`, then id.
"""

import argparse
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
MESH = {".stl", ".obj", ".ply", ".glb", ".gltf", ".3mf", ".off"}
STEP = {".step", ".stp"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("manifests", nargs="+")
    ap.add_argument("--cq-python", required=True)
    ap.add_argument("--work", default="/tmp/cad-render-input")
    args = ap.parse_args()

    designs, seen = [], set()
    for m in args.manifests:
        for d in json.loads(Path(m).read_text()):
            if d["id"] in seen:
                continue
            seen.add(d["id"])
            designs.append(d)

    for d in designs:
        files = [f for f in d.get("local_files", []) if Path(f).exists()]
        meshes = [f for f in files if Path(f).suffix.lower() in MESH]
        steps = [f for f in files if Path(f).suffix.lower() in STEP]
        render = list(meshes)
        # Prefer the mesh exports when a design ships both, unless only STEP holds the parts.
        if steps and (not meshes or (d.get("assembly") and len(meshes) < 2)):
            outdir = Path(args.work) / d["id"]
            r = subprocess.run([args.cq_python, "-I", str(HERE / "step_to_stl.py"), *steps, str(outdir)],
                               capture_output=True, text=True, timeout=900)
            if r.returncode == 0:
                render = json.loads(r.stdout.strip().splitlines()[-1])
            else:
                d.setdefault("notes", "")
                d["notes"] += f" STEP conversion failed: {r.stderr.strip().splitlines()[-1][:200] if r.stderr else '?'}"
        d["render_files"] = render
    designs.sort(key=lambda d: (str(d.get("first_seen") or "9999"), d["id"]))
    Path(args.out).write_text(json.dumps(designs, indent=1))
    print(json.dumps({"designs": len(designs), "renderable": sum(bool(d["render_files"]) for d in designs)}))


if __name__ == "__main__":
    main()
