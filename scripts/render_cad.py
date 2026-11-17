"""Render CAD designs as turntable GIFs, plus exploded views for assemblies.

Reads a manifest (a JSON list of designs, see docs/talks/2026-11-17-research-lunch-and-learn/cad/)
and writes, for each design:

    <out>/<id>.gif                 turntable, assembled
    <out>/<id>-exploded.gif        assemblies only: rotates while the parts move apart and back
    <out>/<id>-exploded.png        assemblies only: still of the fully exploded state
    <out>/<id>.png                 still of the assembled state (used for the contact sheet)

Meshes (STL, OBJ, PLY, GLB, 3MF, OFF) are read with trimesh. STEP files must be converted to
STL first with scripts/step_to_stl.py, which needs CadQuery; CadQuery's OCP wheel bundles an
older VTK that breaks PyVista, so the two run in separate environments.

Run under a virtual display on a headless machine:

    xvfb-run -a -s "-screen 0 1600x1200x24" python -I scripts/render_cad.py manifest.json out/

Each design is one parts list. A part is one file, or, when the design is an assembly that
ships as a single file, one connected body of it (capped at --max-bodies). The exploded view
moves every part away from the assembly's centre along the line from that centre to the
part's own centre, so a part that sits in the middle stays put.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pyvista as pv
import trimesh
from PIL import Image, ImageDraw, ImageFont

pv.OFF_SCREEN = True

# Muted, print-friendly colours; parts cycle through them.
PALETTE = [
    "#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2", "#EECA3B",
    "#B279A2", "#FF9DA6", "#9D755D", "#BAB0AC", "#2F6B9A", "#D67195",
]
MESH_EXT = {".stl", ".obj", ".ply", ".glb", ".gltf", ".3mf", ".off"}


def load_parts(files: list[str], assembly: bool, max_bodies: int, max_faces: int):
    """Return a list of (name, pv.PolyData)."""
    parts = []
    for f in files:
        p = Path(f)
        if p.suffix.lower() not in MESH_EXT:
            continue
        loaded = trimesh.load(str(p), force=None)
        if isinstance(loaded, trimesh.Scene):
            geoms = []
            for node in loaded.graph.nodes_geometry:
                transform, gname = loaded.graph[node]
                g = loaded.geometry[gname].copy()
                if not isinstance(g, trimesh.Trimesh) or len(g.faces) == 0:
                    continue
                g.apply_transform(transform)
                geoms.append((f"{p.stem}:{gname}", g))
        else:
            geoms = [(p.stem, loaded)] if len(getattr(loaded, "faces", [])) else []
        for name, g in geoms:
            parts.append((name, g))

    # A single-file assembly: split it into its connected bodies, if there is a sensible number.
    if assembly and len(parts) == 1:
        name, g = parts[0]
        try:
            bodies = g.split(only_watertight=False)
        except Exception:
            bodies = [g]
        bodies = [b for b in bodies if len(b.faces) >= 12]
        if 2 <= len(bodies) <= max_bodies:
            parts = [(f"{name}#{i}", b) for i, b in enumerate(bodies)]

    out = []
    for name, g in parts:
        faces = np.hstack([np.full((len(g.faces), 1), 3), g.faces]).astype(np.int64)
        m = pv.PolyData(np.asarray(g.vertices, dtype=float), faces)
        if m.n_cells > max_faces:
            m = m.triangulate().decimate(1.0 - max_faces / m.n_cells)
        out.append((name, m))
    return out


def up_axis_for(files: list[str]) -> np.ndarray:
    # glTF is Y-up by specification; everything the lab exports from CAD is Z-up.
    if any(Path(f).suffix.lower() in {".glb", ".gltf"} for f in files):
        return np.array([0.0, 1.0, 0.0])
    return np.array([0.0, 0.0, 1.0])


def explode_offsets(parts, factor: float, up=np.array([0.0, 0.0, 1.0])):
    centers = np.array([m.center for _, m in parts])
    lo = np.min([m.bounds[::2] for _, m in parts], axis=0)
    hi = np.max([m.bounds[1::2] for _, m in parts], axis=0)
    c = (lo + hi) / 2
    diag = float(np.linalg.norm(hi - lo)) or 1.0
    vecs = centers - c
    # Parts whose centres coincide with the assembly centre do not move radially.
    vecs[np.linalg.norm(vecs, axis=1) < 1e-3 * diag] = 0.0
    # Radial moves cannot separate parts that share a centre (a ring on a shaft), so also
    # spread every part along the vertical by its rank in height.
    n = len(parts)
    rank = np.empty(n)
    rank[np.argsort(centers @ up, kind="stable")] = np.arange(n)
    lift = (rank - (n - 1) / 2) * (0.3 * diag / max(n - 1, 1))
    return vecs * factor + np.outer(lift, up / np.linalg.norm(up))


def view_frame(up, azim_deg: float, elev_deg: float):
    """Unit vectors (toward camera, right, screen-up) for a camera orbiting `up`."""
    up = up / np.linalg.norm(up)
    ref = np.array([1.0, 0.0, 0.0]) if abs(up[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = ref - up * np.dot(ref, up)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(up, e1)
    a, e = math.radians(azim_deg), math.radians(elev_deg)
    d = math.cos(e) * (math.cos(a) * e1 + math.sin(a) * e2) + math.sin(e) * up
    right = np.cross(up, d)
    right /= np.linalg.norm(right)
    screen_up = np.cross(d, right)
    return d, right, screen_up


def camera_for(bounds_list, up, elev_deg: float, aspect: float = 4 / 3, margin: float = 1.06,
               azims=range(0, 360, 10)):
    """Centre and distance that keep every box corner in view at every azimuth of the turn.

    Fitting the corners rather than a bounding sphere frames flat or long parts much more
    tightly. The top band is kept clear for the caption.
    """
    corners = []
    for b in bounds_list:
        for x in (b[0], b[1]):
            for y in (b[2], b[3]):
                for z in (b[4], b[5]):
                    corners.append((x, y, z))
    corners = np.array(corners, dtype=float)
    lo, hi = corners.min(axis=0), corners.max(axis=0)
    center = (lo + hi) / 2
    rel = corners - center
    tv = math.tan(math.radians(30.0) / 2)
    th = tv * aspect
    need = 1e-9
    for az in azims:
        d, right, sup = view_frame(up, az, elev_deg)
        f = rel @ d
        r = np.abs(rel @ right)
        u = rel @ sup
        # Caption band: allow the top 12 % less room than the bottom.
        need = max(need, float(np.max(f + r / th)), float(np.max(f + u / (tv * 0.88))),
                   float(np.max(f + (-u) / tv)))
    return center, need * margin


def place_camera(pl: pv.Plotter, center, dist, up, azim_deg: float, elev_deg: float):
    d, _, _ = view_frame(up, azim_deg, elev_deg)
    pl.camera.position = tuple(center + dist * d)
    pl.camera.focal_point = tuple(center)
    pl.camera.up = tuple(up / np.linalg.norm(up))
    pl.camera.view_angle = 30.0
    pl.reset_camera_clipping_range()


def caption(img: Image.Image, text: str, sub: str | None) -> Image.Image:
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 15)
        small = ImageFont.truetype("DejaVuSans.ttf", 12)
    except OSError:
        font = small = ImageFont.load_default()
    draw.text((10, 8), text, fill=(30, 30, 30), font=font)
    if sub:
        draw.text((10, 28), sub, fill=(90, 90, 90), font=small)
    return img


def render_frames(parts, up, size, n_frames, elev, explode=None, start_azim=30.0):
    """explode: None for assembled, else (offsets, schedule) where schedule(t) in [0, 1]."""
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    actors, bases = [], []
    for i, (_, m) in enumerate(parts):
        mm = m.copy()
        try:
            mm = mm.compute_normals(split_vertices=True, feature_angle=35.0, auto_orient_normals=False)
        except Exception:
            pass
        actors.append(pl.add_mesh(mm, color=PALETTE[i % len(PALETTE)], smooth_shading=True,
                                  specular=0.25, specular_power=20, ambient=0.18, diffuse=0.85))
        bases.append(mm)
    # Frame the camera on the largest extent the animation reaches, so nothing leaves the view.
    if explode is not None:
        offsets, _ = explode
        bounds = [np.array(m.bounds) + np.repeat(o, 2) for (_, m), o in zip(parts, offsets)]
        bounds += [np.array(m.bounds) for _, m in parts]
    else:
        bounds = [np.array(m.bounds) for _, m in parts]
    center, dist = camera_for(bounds, up, elev, aspect=size[0] / size[1],
                              azims=[start_azim + 360.0 * k / n_frames for k in range(n_frames)])
    frames = []
    for k in range(n_frames):
        t = k / n_frames
        if explode is not None:
            offsets, schedule = explode
            s = schedule(t)
            for a, o in zip(actors, offsets):
                a.position = tuple(o * s)
        place_camera(pl, center, dist, up, start_azim + 360.0 * t, elev)
        pl.render()
        frames.append(Image.fromarray(pl.screenshot(return_img=True)))
    pl.close()
    return frames


def still(parts, up, size, elev, azim=30.0, offsets=None):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    bounds = []
    for i, (_, m) in enumerate(parts):
        mm = m.copy()
        if offsets is not None:
            mm = mm.translate(offsets[i], inplace=False)
        try:
            mm = mm.compute_normals(split_vertices=True, feature_angle=35.0, auto_orient_normals=False)
        except Exception:
            pass
        pl.add_mesh(mm, color=PALETTE[i % len(PALETTE)], smooth_shading=True,
                    specular=0.25, specular_power=20, ambient=0.18, diffuse=0.85)
        bounds.append(np.array(mm.bounds))
    center, dist = camera_for(bounds, up, elev, aspect=size[0] / size[1], azims=[azim])
    place_camera(pl, center, dist, up, azim, elev)
    pl.render()
    img = Image.fromarray(pl.screenshot(return_img=True))
    pl.close()
    return img


def save_gif(frames, path: Path, ms: int, title: str, sub: str | None):
    frames = [caption(f.convert("RGB"), title, sub) for f in frames]
    # One shared palette keeps the colours steady from frame to frame and the file small.
    sample = Image.new("RGB", (frames[0].width, frames[0].height * 4))
    for j, f in enumerate(frames[:: max(1, len(frames) // 4)][:4]):
        sample.paste(f, (0, frames[0].height * j))
    pal = sample.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True, disposal=1)
    try:
        subprocess.run(["gifsicle", "-O3", "--lossy=40", "-b", str(path)], check=True,
                       capture_output=True, timeout=300)
    except Exception:
        pass


def trapezoid(t: float) -> float:
    """0 -> 1 over the first 30 % of the loop, hold, 1 -> 0 over the last 30 %."""
    if t < 0.3:
        x = t / 0.3
    elif t < 0.7:
        x = 1.0
    else:
        x = (1.0 - t) / 0.3
    return x * x * (3 - 2 * x)  # smoothstep


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("out")
    ap.add_argument("--only", nargs="*", help="render just these ids")
    ap.add_argument("--size", default="480x360")
    ap.add_argument("--frames", type=int, default=36)
    ap.add_argument("--ms", type=int, default=90, help="milliseconds per frame")
    ap.add_argument("--elev", type=float, default=25.0)
    ap.add_argument("--explode", type=float, default=0.9, help="explode factor")
    ap.add_argument("--max-bodies", type=int, default=40)
    ap.add_argument("--max-faces", type=int, default=150_000)
    ap.add_argument("--force", action="store_true", help="re-render designs that already have a GIF")
    args = ap.parse_args()

    w, h = (int(x) for x in args.size.split("x"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    designs = json.loads(Path(args.manifest).read_text())
    report = []
    for d in designs:
        did = d["id"]
        if args.only and did not in args.only:
            continue
        if d.get("skip_render"):
            continue
        gif = out / f"{did}.gif"
        if gif.exists() and not args.force:
            report.append({"id": did, "status": "exists"})
            continue
        t0 = time.time()
        try:
            files = d.get("render_files") or d.get("local_files") or []
            parts = load_parts(files, bool(d.get("assembly")), args.max_bodies, args.max_faces)
            if not parts:
                raise RuntimeError("no renderable mesh among " + ", ".join(Path(f).name for f in files))
            up = np.array(d["up"], dtype=float) if d.get("up") else up_axis_for(files)
            title = d.get("title", did)
            sub = f'{d.get("repo", "").split("/")[-1]} · {d.get("first_seen", "")}'.strip(" ·")
            frames = render_frames(parts, up, (w, h), args.frames, args.elev)
            save_gif(frames, gif, args.ms, title, sub)
            caption(frames[0].convert("RGB"), title, sub).save(out / f"{did}.png", optimize=True)
            entry = {"id": did, "status": "ok", "parts": len(parts), "faces": int(sum(m.n_cells for _, m in parts))}
            if len(parts) > 1 and d.get("assembly"):
                offs = explode_offsets(parts, args.explode, up)
                if np.any(np.linalg.norm(offs, axis=1) > 0):
                    ex = render_frames(parts, up, (w, h), int(args.frames * 1.4), args.elev,
                                       explode=(offs, trapezoid))
                    save_gif(ex, out / f"{did}-exploded.gif", args.ms, title + " (exploded)", sub)
                    img = still(parts, up, (2 * w, 2 * h), args.elev, offsets=offs)
                    caption(img, title + " (exploded)", sub).save(out / f"{did}-exploded.png", optimize=True)
                    entry["exploded"] = True
            entry["seconds"] = round(time.time() - t0, 1)
            report.append(entry)
            print(json.dumps(entry), flush=True)
        except Exception as exc:  # keep going; report the failure
            report.append({"id": did, "status": "error", "error": f"{type(exc).__name__}: {exc}"[:300]})
            print(json.dumps(report[-1]), flush=True)
    rp = out / "_render_report.json"
    old = json.loads(rp.read_text()) if rp.exists() else []
    merged = {r["id"]: r for r in old}
    merged.update({r["id"]: r for r in report if r["status"] != "exists"})
    rp.write_text(json.dumps(list(merged.values()), indent=1))


if __name__ == "__main__":
    sys.exit(main())
