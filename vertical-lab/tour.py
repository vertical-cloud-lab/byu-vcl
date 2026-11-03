"""Renders of the instruments in ``instruments.py``, one at a time, each doing what it does: the XRD's chamber opens and
closes, a sample goes onto the PIP's anvil, the SEM's drawer comes out for a stub, and so on (#303).

    xvfb-run -a python3 tour.py                 # every instrument -> out/instruments/<key>.gif, .png; out/mp4/...
    xvfb-run -a python3 tour.py xrd pip         # just these
    python3 tour.py gallery                     # out/instruments_gallery.png from the stills
    python3 tour.py join                        # out/mp4/instruments_tour.mp4, every instrument's MP4 in turn

Same pipeline as ``animate.py`` (``scene.py``): CadQuery tessellated into PyVista, rendered off-screen, text drawn
with PIL. The meshes are cached in ``.cache/`` on the sources' hash.
"""
from __future__ import annotations

import hashlib
import json
import pickle
import subprocess
import sys
from pathlib import Path

import numpy as np
import pyvista as pv
from PIL import Image, ImageDraw

import instruments as I
import lab
import scene
from scene import FPS, OUT, Scene, T, font

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
MATS = dict(lab.MATS)
MATS.update(I.MATERIALS)
GLOWY = {"glow", "laser", "screen_on", "vlm_led"}
scene.GIF_SIZE = (640, 360)          # one GIF per instrument: smaller than the chapters'
FIT = dict(W=2450.0 - 24, D=864.0 - 24, H=727.5)     # inside a tray's rim; Kardex's product height


# ================================================================================================= meshes
def piece_entries(inst: I.Instrument) -> dict:
    """{piece: [entry]} with one merged mesh per material, as lab.py does for the equipment."""
    out = {}
    for name, model in inst.pieces.items():
        by = {}
        for p in model.parts:
            by.setdefault(p.material, []).append(lab.to_mesh(p.shape, 0.5))
        out[name] = []
        for mat, ms in by.items():
            r, g, b, a, spec = MATS[mat]
            out[name].append(dict(mesh=lab._merge(ms), color=(r, g, b), opacity=a, specular=spec, material=mat))
    for name, parts in inst.meshes.items():
        out.setdefault(name, [])
        for mesh, col, op in parts:
            out[name].append(dict(mesh=mesh, color=col, opacity=op, specular=0.25, material="mesh"))
    return out


def _sources() -> list[Path]:
    return [HERE / "instruments.py", HERE / "openflexure.py", HERE / "lab_models" / "common.py",
            *sorted((HERE / "openflexure").glob("*.json"))]


def load(keys=None, rebuild=False) -> dict:
    """{key: (Instrument, {piece: [entry]})}, every instrument, cached on the sources."""
    CACHE.mkdir(exist_ok=True)
    h = hashlib.sha256()
    for f in _sources():
        if f.exists():
            h.update(f.read_bytes())
    path = CACHE / f"instruments_{h.hexdigest()[:12]}.pkl"
    if path.exists() and not rebuild:
        data = pickle.loads(path.read_bytes())
    else:
        data = {}
        for key, build in I.REGISTRY.items():
            print(f"  building {key}", flush=True)
            inst = build()
            data[key] = (inst, piece_entries(inst))
        path.write_bytes(pickle.dumps(data))
    return {k: v for k, v in data.items() if keys is None or k in keys}


def fit_report(inst: I.Instrument) -> dict:
    x0, x1, y0, y1, z0, z1 = inst.bbox()
    w, d, h = x1 - x0, y1 - y0, z1 - z0
    fits = w <= FIT["W"] and d <= FIT["D"] and h <= FIT["H"]
    return dict(model_mm=[round(w), round(d), round(h)], published_mm=list(inst.size), fits_tray=bool(fits),
                floor=inst.floor)


# ================================================================================================= staging
class Rig:
    """An instrument in a scene: its pieces as groups, placed at `at` (a 4x4), with joint values."""

    def __init__(self, sc: Scene, inst: I.Instrument, entries: dict, prefix: str, at=np.eye(4), parent=None):
        self.sc, self.inst, self.prefix = sc, inst, prefix
        self.base = at
        self.v = {k: j.v0 for k, j in inst.joints.items()}
        self.v.update({f"~{k}": 0.0 for k in entries})              # see-through amount of each piece
        self.names: dict[str, list[str]] = {}
        root = f"{prefix}body"
        for piece, ents in entries.items():
            g = f"{prefix}{piece}"
            self.names[piece] = []
            for i, e in enumerate(ents):
                if not e["mesh"].n_points:
                    continue
                kw = dict(specular=e["specular"])
                if e["material"] in GLOWY:
                    kw.update(ambient=0.9, diffuse=0.25)
                n = f"{g}/{e['material']}{i}"
                sc.add(n, e["mesh"], e["color"], g, opacity=e["opacity"], **kw)
                self.names[piece].append(n)
            if piece != "body":
                j = inst.joints.get(piece)
                sc.parent[g] = f"{prefix}{j.parent}" if j is not None and j.parent else root
        sc.gmat[root] = at
        if parent is not None:
            sc.parent[root] = parent
        self.apply()

    def apply(self):
        for piece, j in self.inst.joints.items():
            g = f"{self.prefix}{piece}"
            self.sc.gmat[g] = j.matrix(self.v[piece])
            if j.kind == "fade":
                for n in self.names.get(piece, []):
                    self.sc.alpha[n] = self.v[piece]
        for piece, ns in self.names.items():
            g = self.v.get(f"~{piece}", 0.0)
            if g > 0 or piece not in self.inst.joints or self.inst.joints[piece].kind != "fade":
                for n in ns:
                    self.sc.alpha[n] = 1.0 - 0.82 * g

    def move(self, targets: dict):
        """An update(u) for Scene.step: each piece from its current value to its target."""
        start = {k: self.v[k] for k in targets}

        def up(u):
            for k, (a, b) in targets.items():
                a = start[k] if a is None else a
                self.v[k] = a + (b - a) * u
            self.apply()
        return up

    def all_names(self):
        return [n for ns in self.names.values() for n in ns]


def studio(sc: Scene, size=6000.0, at=(0, 0)):
    floor = pv.Plane(center=(at[0], at[1], -0.5), direction=(0, 0, 1), i_size=size, j_size=size)
    sc.add("floor", floor, (0.965, 0.965, 0.96), "floor", ambient=1.0, diffuse=0.0, specular=0.0,
           smooth_shading=False)


def frame_cam(bb, direction=(1.0, -1.6, 0.9), pad=0.85, look_z=0.42):
    x0, x1, y0, y1, z0, z1 = bb
    c = np.array([(x0 + x1) / 2, (y0 + y1) / 2, z0 + (z1 - z0) * look_z])
    r = 0.5 * np.linalg.norm([x1 - x0, y1 - y0, z1 - z0])
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    dist = pad * r / np.tan(np.radians(15.0)) * 1.05
    return [tuple(c + d * dist), tuple(c), (0, 0, 1)]


def tour_one(inst: I.Instrument, entries: dict) -> str:
    ents = entries
    out = OUT / "instruments"
    out.mkdir(parents=True, exist_ok=True)
    (OUT / "mp4" / "instruments").mkdir(parents=True, exist_ok=True)
    sc = Scene(f"instruments/{inst.key}", f"{inst.title}: {inst.model}")
    sc.intro = 0.6
    studio(sc)
    rig = Rig(sc, inst, entries, f"{inst.key}:")
    bb = inst.bbox()
    tall = (bb[5] - bb[4]) > 1.3 * max(bb[1] - bb[0], bb[3] - bb[2])
    pad, look_z = inst.framing or ((1.0, 0.5) if tall else (0.85, 0.42))
    sc.cam = frame_cam(bb, inst.cam, pad=pad, look_z=look_z)
    labels = [(t, xyz, at) for t, xyz, at in inst.labels]
    if inst.key == "rail":                 # the arm it would carry: a UR10e on the carriage, folded
        import animate
        import robot
        top = I.RAIL["top"]
        robot.Robot(sc, "ur10e", f"{inst.key}:carriage", T((0, 0, top)), q0=animate.PARK_DEG, prefix="railarm")
        sc.cam = frame_cam(inst.bbox(), inst.cam, pad=0.75, look_z=0.9)
    n = len([a for a in inst.actions if a[0]])
    for i, (cap, secs, targets) in enumerate(inst.actions):
        sc.step(f"{min(i + 1, n)}/{n}", cap, secs, rig.move(targets), hold=0.5, labels=labels)
    # the hero still for the gallery: closed, the sample in place, no text
    rig.move({k: (None, 1.0 if k in inst.props else j.v0) for k, j in inst.joints.items()})(1.0)
    rig.move({f"~{k}": (None, 0.0) for k in ents})(1.0)
    img = sc.render_base()
    Image.fromarray(img).save(out / f"{inst.key}.png", optimize=True)
    return sc.save()


# ================================================================================================= gallery
def gallery(data: dict, cols=4) -> Path:
    tiles = []
    for key, (inst, _) in data.items():
        p = OUT / "instruments" / f"{key}.png"
        if p.exists():
            tiles.append((inst, Image.open(p).convert("RGB")))
    tw, th, cap = 480, 270, 58
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, (th + cap) * rows), "white")
    d = ImageDraw.Draw(sheet)
    f1, f2 = font(15, bold=True), font(13)
    for i, (inst, im) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + cap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        fr = fit_report(inst)
        where = "beside the VLM" if inst.floor or not fr["fits_tray"] else "on a VLM tray"
        d.text((x + 10, y + th + 4), inst.model, font=f1, fill=(20, 20, 24))
        w, dd, h = inst.size
        d.text((x + 10, y + th + 24), f"{inst.title}", font=f2, fill=(70, 72, 78))
        d.text((x + 10, y + th + 40), f"{w:.0f} x {dd:.0f} x {h:.0f} mm, {where}", font=f2, fill=(70, 72, 78))
    path = OUT / "instruments_gallery.png"
    sheet.save(path, optimize=True)
    return path


def join(keys) -> str:
    parts = [OUT / "mp4" / "instruments" / f"{k}.mp4" for k in keys]
    parts = [p for p in parts if p.exists()]
    lst = OUT / "mp4" / "instruments" / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    dst = OUT / "mp4" / "instruments_tour.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(dst)], check=True)
    lst.unlink()
    return f"instruments_tour: {len(parts)} clips, {dst.stat().st_size / 1e6:.1f} MB"


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "still":          # quick look: the closed state and the end of every action, to /tmp
        for key, (inst, ents) in load(args[1:] or None).items():
            sc = Scene(f"still_{key}", inst.model, gif=False, mp4=False)
            studio(sc)
            rig = Rig(sc, inst, ents, f"{key}:")
            sc.cam = frame_cam(inst.bbox(), inst.cam)
            shots = [sc.render_base()]
            for cap, secs, targets in inst.actions:
                rig.move(targets)(1.0)
                shots.append(sc.render_base())
            sc.pl.close()
            w, h = 640, 360
            sheet = Image.new("RGB", (w * len(shots), h), "white")
            for i, im in enumerate(shots):
                sheet.paste(Image.fromarray(im).resize((w, h)), (i * w, 0))
            sheet.save(f"/tmp/still_{key}.png")
            print(key, fit_report(inst), f"/tmp/still_{key}.png", flush=True)
    elif args and set(args) <= {"gallery", "join", "table"}:
        for word in args:
            if word == "table":                 # out/instruments.json: what each model is, its size, where it goes
                rows = {}
                for key, (inst, _) in load().items():
                    fr = fit_report(inst)
                    rows[key] = dict(title=inst.title, model=inst.model, source=inst.source, **fr,
                                     where="beside the VLM" if inst.floor or not fr["fits_tray"] else "on a tray")
                (OUT / "instruments.json").write_text(json.dumps(rows, indent=1) + "\n")
                for k, r in rows.items():
                    print(f"{k:18s} {r['model']:36s} {r['published_mm']} model {r['model_mm']} {r['where']}")
            elif word == "gallery":
                print(gallery(load()))
            else:
                print(join(list(I.REGISTRY)))
    else:
        data = load(args or None, rebuild="--rebuild" in args)
        for key, (inst, ents) in data.items():
            print(key, fit_report(inst), flush=True)
            print(tour_one(inst, ents), flush=True)
