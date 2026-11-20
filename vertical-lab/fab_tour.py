"""Renders of the fabrication tools, one at a time, each doing what it does, as ``tour.py`` does for the instruments
(#303): the compact metal printers (``fab_metal.py``), the resin printers with their wash and cure (``fab_resin.py``),
and the PCB line, a stencil printer and an open-source pick-and-place (``fab_pcb.py``).

    xvfb-run -a python3 fab_tour.py                  # every model -> out/fabrication/<key>.gif, .png; out/mp4/fabrication/
    xvfb-run -a python3 fab_tour.py form4 lumenpnp   # just these
    xvfb-run -a python3 fab_tour.py still form4      # the closed state and the end of every action -> /tmp/still_form4.png
    python3 fab_tour.py gallery join table           # out/fabrication_gallery.png, out/mp4/fabrication_tour.mp4,
                                                     # out/fabrication.json

Same pipeline as ``tour.py`` (its ``Rig``, studio and camera), with the models' own materials merged in. Each model's
meshes are cached in ``.cache/`` on the hash of its own file, so editing one family does not rebuild the others.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import pickle
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import tour
from scene import OUT, Scene, font

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
FAMILIES = ("fab_metal", "fab_resin", "fab_pcb")
DIR = "fabrication"


def registry() -> dict:
    """{key: (family module, builder)}, in the order the families list them. A family not written yet is skipped."""
    out = {}
    for name in FAMILIES:
        try:
            mod = importlib.import_module(name)
        except ModuleNotFoundError as e:
            if e.name != name:
                raise
            continue
        tour.MATS.update(getattr(mod, "MATERIALS", {}))
        tour.GLOWY.update(m for m in getattr(mod, "MATERIALS", {}) if "glow" in m)    # fab_resin's uv_glow
        for key, build in mod.REGISTRY.items():
            out[key] = (mod, build)
    return out


def load(keys=None, rebuild=False) -> dict:
    """{key: (Instrument, {piece: [entry]})}, cached per model on its family's source."""
    CACHE.mkdir(exist_ok=True)
    data = {}
    shared = b"".join((HERE / f).read_bytes() for f in ("instruments.py", "lab_models/common.py", "lab.py"))
    for key, (mod, build) in registry().items():
        if keys is not None and key not in keys:
            continue
        h = hashlib.sha256(shared + Path(mod.__file__).read_bytes() + key.encode()).hexdigest()[:12]
        path = CACHE / f"fab_{key}_{h}.pkl"
        if path.exists() and not rebuild:
            data[key] = pickle.loads(path.read_bytes())
            continue
        print(f"  building {key}", flush=True)
        inst = build()
        data[key] = (inst, tour.piece_entries(inst))
        path.write_bytes(pickle.dumps(data[key]))
    return data


def tour_one(inst, entries: dict) -> str:
    """tour.tour_one, writing to out/fabrication/ and out/mp4/fabrication/."""
    (OUT / DIR).mkdir(parents=True, exist_ok=True)
    (OUT / "mp4" / DIR).mkdir(parents=True, exist_ok=True)
    sc = Scene(f"{DIR}/{inst.key}", f"{inst.title}: {inst.model}")
    sc.intro = 0.6
    tour.studio(sc, shadow_of=inst.bbox())
    rig = tour.Rig(sc, inst, entries, f"{inst.key}:")
    bb = inst.bbox()
    tall = (bb[5] - bb[4]) > 1.3 * max(bb[1] - bb[0], bb[3] - bb[2])
    pad, look_z = inst.framing or ((1.0, 0.5) if tall else (0.85, 0.42))
    sc.cam = tour.frame_cam(bb, inst.cam, pad=pad, look_z=look_z)
    n = len([a for a in inst.actions if a[0]])
    whole = sc.cam
    for i, (cap, secs, targets) in enumerate(inst.actions):
        z = getattr(inst, "zoom", {}).get(i)               # close-ups, as tour.tour_one does them
        cam_to = None if z is None else whole if z == "out" else tour.close_cam(*z, direction=inst.cam)
        sc.step(f"{min(i + 1, n)}/{n}", cap, secs, rig.move(targets), hold=0.5, labels=list(inst.labels),
                cam_to=cam_to)
    # the hero still for the gallery: closed, the load in place, nothing see-through, no text
    rig.move({k: (None, 1.0 if k in inst.props else j.v0) for k, j in inst.joints.items()})(1.0)
    rig.move({f"~{k}": (None, 0.0) for k in entries})(1.0)
    Image.fromarray(sc.render_base()).save(OUT / DIR / f"{inst.key}.png", optimize=True)
    return sc.save()


def still(keys) -> None:
    for key, (inst, ents) in load(keys or None).items():
        sc = Scene(f"still_{key}", inst.model, gif=False, mp4=False)
        tour.studio(sc, shadow_of=inst.bbox())
        rig = tour.Rig(sc, inst, ents, f"{key}:")
        sc.cam = tour.frame_cam(inst.bbox(), inst.cam, *(inst.framing or ()))
        shots = [sc.render_base()]
        for _, _, targets in inst.actions:
            rig.move(targets)(1.0)
            shots.append(sc.render_base())
        sc.pl.close()
        w, h = 640, 360
        sheet = Image.new("RGB", (w * len(shots), h), "white")
        for i, im in enumerate(shots):
            sheet.paste(Image.fromarray(im).resize((w, h)), (i * w, 0))
        sheet.save(f"/tmp/still_{key}.png")
        print(key, tour.fit_report(inst), f"/tmp/still_{key}.png", flush=True)


def where(inst) -> str:
    """On a tray if it goes through the opening as it stands or turned 90 degrees, else beside the VLM."""
    w, d, h = tour.fit_report(inst)["model_mm"]
    F = tour.FIT
    if inst.floor or h > F["H"]:
        return "beside the VLM"
    if w <= F["W"] and d <= F["D"]:
        return "on a VLM tray"
    return "on a VLM tray, turned 90 deg" if d <= F["W"] and w <= F["D"] else "beside the VLM"


def gallery(data: dict, cols=4) -> Path:
    tiles = [(inst, Image.open(OUT / DIR / f"{k}.png").convert("RGB")) for k, (inst, _) in data.items()
             if (OUT / DIR / f"{k}.png").exists()]
    tw, th, cap = 480, 270, 58
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, (th + cap) * rows), "white")
    d = ImageDraw.Draw(sheet)
    f1, f2 = font(15, bold=True), font(13)
    for i, (inst, im) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + cap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        w, dd, h = inst.size
        d.text((x + 10, y + th + 4), inst.model, font=f1, fill=(20, 20, 24))
        d.text((x + 10, y + th + 24), inst.title, font=f2, fill=(70, 72, 78))
        d.text((x + 10, y + th + 40), f"{w:.0f} x {dd:.0f} x {h:.0f} mm, {where(inst)}", font=f2, fill=(70, 72, 78))
    path = OUT / "fabrication_gallery.png"
    sheet.save(path, optimize=True)
    return path


def join(keys) -> str:
    parts = [p for p in (OUT / "mp4" / DIR / f"{k}.mp4" for k in keys) if p.exists()]
    lst = OUT / "mp4" / DIR / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    dst = OUT / "mp4" / "fabrication_tour.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(dst)], check=True)
    lst.unlink()
    return f"fabrication_tour: {len(parts)} clips, {dst.stat().st_size / 1e6:.1f} MB"


def table(data: dict) -> dict:
    rows = {}
    for key, (inst, _) in data.items():
        fr = tour.fit_report(inst)
        rows[key] = dict(title=inst.title, model=inst.model, source=inst.source, **fr, where=where(inst),
                         over_opening_mm=round(max(0.0, fr["model_mm"][2] - tour.FIT["H"]), 1), notes=inst.notes)
    (OUT / "fabrication.json").write_text(json.dumps(rows, indent=1) + "\n")
    for k, r in rows.items():
        print(f"{k:14s} {r['model']:34s} {r['published_mm']} model {r['model_mm']} {r['where']}")
    return rows


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args and args[0] == "still":
        still(args[1:])
    elif args and set(args) <= {"gallery", "join", "table"}:
        data = load()
        for word in args:
            print(table(data) and "out/fabrication.json" if word == "table" else
                  gallery(data) if word == "gallery" else join(list(data)))
    else:
        for key, (inst, ents) in load(args or None, rebuild="--rebuild" in sys.argv).items():
            print(key, tour.fit_report(inst), flush=True)
            print(tour_one(inst, ents), flush=True)
