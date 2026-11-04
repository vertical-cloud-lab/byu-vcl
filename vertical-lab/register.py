"""Register an instrument model to photos or video frames of the real machine, to check and refine its geometry (#303).

    python3 register.py solve polisher              # fit the cameras, and the model's free dimensions, to every view
    xvfb-run -a python3 register.py draw polisher   # draw the model over each frame -> out/register/polisher/*.jpg

A view is ``refs/<key>/<name>.json`` next to its frame ``refs/<key>/<name>.jpg``::

    {"source": "https://youtu.be/nfnl0aPJPZc?t=219",      # where the frame comes from
     "video": "nfnl0aPJPZc", "t": 219,                    # optional: lets a missing frame be fetched (frames.py)
     "pose": {"head": 0.0},                               # joint values of the model in that frame (Instrument.joints)
     "points": {"screen tl": [771, 548], ...},            # a point of the model at pixel (u, v)
     "curves": {"platen edge": [[402, 455], ...], ...},   # pixels anywhere along a circle or a line of the model
     "holdout": false}                                    # true: a check, left out of the fit of the model's dimensions

Frames from the lab's own videos are committed; frames from makers' and others' videos are not (refs/.gitignore),
as vendor CAD is not: give their "video" and "t" and the frame is fetched through the Pi when it is missing.

The names are anchors: the model publishes them (``ANCHORS[key] = (params, anchors(params))`` in the instrument's
module), as points ``(x, y, z)``, circles ``("circle", centre, radius)`` (horizontal) and lines ``("line", p0, p1)``,
all in the model's frame (mm; x right, y away from the front, z up). They are computed from the same parameters that
build the model, so a dimension fitted here is a dimension of the model.

The camera of each view is a pinhole with square pixels, its principal point at the centre and one radial lens term
(phone and action cameras bend straight edges noticeably). ``solve`` first finds each camera alone (solvePnP over a
range of focal lengths, then least squares over the pose, focal length, distortion and the curve picks), then, if the
model lists free parameters (``FREE[key]``), fits those and every camera together, with a soft pull back to the
starting values so a dimension no view sees stays where it was. Writes ``refs/<key>/fit.json``: the cameras, the
fitted parameters and the residual of every pick.

``draw`` renders the model with each fitted camera at the frame's size and draws it over the undistorted frame: the
silhouette in yellow, the creases in cyan, the picks as green dots and where the fitted model puts them as red
crosses. A gap between yellow and the machine's outline is a place the model is wrong.
"""
from __future__ import annotations

import importlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REFS = HERE / "refs"
OUT = HERE / "out" / "register"
MODULES = ["instruments", "instruments_char", "instruments_lab", "services", "fab_metal", "fab_resin", "fab_pcb"]


# ============================================================================================ anchors and cameras
def anchor_sets(key: str):
    """(params, anchors_fn, free) for an instrument that publishes anchors."""
    for name in MODULES:
        if not (HERE / f"{name}.py").exists():
            continue
        mod = importlib.import_module(name)
        a = getattr(mod, "ANCHORS", {})
        if key in a:
            params, fn = a[key]
            return dict(params), fn, list(getattr(mod, "FREE", {}).get(key, []))
    raise KeyError(f"no anchors for {key!r}: add ANCHORS[{key!r}] = (params, fn) to its module")


def anchor_checks(key: str):
    """The module's CHECKS[key](params) -> numbers that must stay >= 0 for the model to make sense, if any."""
    for name in MODULES:
        if (HERE / f"{name}.py").exists():
            mod = importlib.import_module(name)
            if key in getattr(mod, "ANCHORS", {}):
                return getattr(mod, "CHECKS", {}).get(key)
    return None


def sample(anchor, n=360) -> np.ndarray:
    """Points along a circle or line anchor, or the point itself."""
    if isinstance(anchor, tuple) and anchor and anchor[0] == "circle":
        _, c, r = anchor
        t = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return np.stack([c[0] + r * np.cos(t), c[1] + r * np.sin(t), np.full(n, c[2])], axis=1)
    if isinstance(anchor, tuple) and anchor and anchor[0] == "line":
        _, p0, p1 = anchor
        s = np.linspace(0, 1, n)[:, None]
        return np.asarray(p0, float) * (1 - s) + np.asarray(p1, float) * s
    return np.asarray(anchor, float)[None, :]


def rodrigues(r) -> np.ndarray:
    r = np.asarray(r, float)
    t = np.linalg.norm(r)
    if t < 1e-12:
        return np.eye(3)
    k = r / t
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def project(cam, X, size) -> np.ndarray:
    """cam = [rx, ry, rz, tx, ty, tz, log f, k1]; X (n, 3) model mm -> (n, 2) pixels, with the radial term."""
    R = rodrigues(cam[:3])
    Xc = np.asarray(X, float) @ R.T + np.asarray(cam[3:6])
    z = np.maximum(Xc[:, 2], 1e-6)
    x, y = Xc[:, 0] / z, Xc[:, 1] / z
    k1 = cam[7] if len(cam) > 7 else 0.0
    d = 1 + k1 * (x * x + y * y)
    f = math.exp(cam[6])
    return np.stack([size[0] / 2 + f * x * d, size[1] / 2 + f * y * d], axis=1)


def residuals(cam, anchors, view, size) -> np.ndarray:
    out = []
    for name, uv in view.get("points", {}).items():
        out.append(project(cam, sample(anchors[name]), size)[0] - np.asarray(uv, float))
    for name, uvs in view.get("curves", {}).items():
        P = project(cam, sample(anchors[name], 720), size)
        for uv in uvs:
            d = P - np.asarray(uv, float)
            out.append(d[np.argmin((d * d).sum(1))])
    return np.concatenate(out) if out else np.zeros(0)


def init_camera(anchors, view, size):
    """The best of solvePnP over a range of focal lengths, from the point picks (four or more)."""
    import cv2
    names = [n for n in view.get("points", {}) if n in anchors]
    X = np.array([sample(anchors[n])[0] for n in names], np.float64)
    U = np.array([view["points"][n] for n in names], np.float64)
    best = None
    for f in np.geomspace(0.35 * size[0], 5.0 * size[0], 60):
        K = np.array([[f, 0, size[0] / 2], [0, f, size[1] / 2], [0, 0, 1]])
        for flag in (cv2.SOLVEPNP_SQPNP, cv2.SOLVEPNP_ITERATIVE):
            try:
                ok, rv, tv = cv2.solvePnP(X, U, K, None, flags=flag)
            except cv2.error:
                continue
            if not ok or tv[2, 0] <= 0:
                continue
            cam = np.r_[rv.ravel(), tv.ravel(), math.log(f), 0.0]
            e = float(np.mean(residuals(cam, anchors, view, size) ** 2)) + float(np.sum(priors(cam, size) ** 2))
            if best is None or e < best[0]:
                best = (e, cam)
    if best is None:
        raise RuntimeError("solvePnP found no camera: pick at least four points")
    return best[1]


F0 = 0.8                    # a phone or action camera at 16:9: focal length about 0.8 of the frame's width (HFOV ~ 64 deg)


def priors(cam, size) -> np.ndarray:
    """Soft pulls: the focal length towards F0 * width (a factor of e away costs about 25 px), the lens term to 0."""
    return np.r_[25.0 * (cam[6] - math.log(F0 * size[0])), 400.0 * (cam[7] if len(cam) > 7 else 0.0)]


def fit_camera(anchors, view, size, k1=True):
    from scipy.optimize import least_squares
    cam = init_camera(anchors, view, size)
    npick = len(view.get("points", {})) + sum(len(v) for v in view.get("curves", {}).values())

    def f(c):
        c = np.r_[c, 0.0] if len(c) == 7 else c
        return np.r_[residuals(c, anchors, view, size), priors(c, size)]
    x0 = cam if (k1 and npick >= 10) else cam[:7]
    sol = least_squares(f, x0, x_scale="jac", loss="soft_l1", f_scale=6.0, max_nfev=4000)
    c = sol.x if len(sol.x) == 8 else np.r_[sol.x, 0.0]
    return c


def solve(key: str) -> dict:
    """Fit every view's camera, then the free parameters and the cameras together. Writes refs/<key>/fit.json."""
    from PIL import Image
    from scipy.optimize import least_squares
    params, fn, free = anchor_sets(key)
    checks = anchor_checks(key)
    views = {}
    for p in sorted((REFS / key).glob("*.json")):
        if p.name == "fit.json":
            continue
        v = json.loads(p.read_text())
        v["size"] = Image.open(frame_path(key, p.stem, v)).size
        views[p.stem] = v
    cams = {name: fit_camera(fn(params, v.get("pose", {})), v, v["size"]) for name, v in views.items()}
    before = {n: rms(residuals(cams[n], fn(params, v.get("pose", {})), v, v["size"])) for n, v in views.items()}
    held = {n: v for n, v in views.items() if v.get("holdout")}
    views = {n: v for n, v in views.items() if not v.get("holdout")}
    fitted = dict(params)
    if free or len(set(group(v) for v in views.values())) < len(views):
        # views from the same video share the lens: one focal length and one radial term per video
        x0 = np.r_[[params[k] for k in free]]
        scale = np.maximum(np.abs(x0), 10.0)
        order = list(views)
        groups = sorted(set(group(v) for v in views.values()))
        gi = {n: groups.index(group(views[n])) for n in order}
        nf, nv = len(free), 6 * len(order)

        def unpack(x):
            q = dict(params)
            q.update({k: float(x[i]) for i, k in enumerate(free)})
            cs = {}
            for i, n in enumerate(order):
                g0 = nf + nv + 2 * gi[n]
                cs[n] = np.r_[x[nf + 6 * i: nf + 6 * i + 6], x[g0:g0 + 2]]
            return q, cs

        def f(x):
            q, cs = unpack(x)
            r = [residuals(cs[n], fn(q, views[n].get("pose", {})), views[n], views[n]["size"]) for n in order]
            r += [priors(cs[n], views[n]["size"]) for n in order]
            r.append(5.0 * (x[:len(free)] - x0) / scale * 10.0)       # 10 % off its start costs about 5 px
            if checks is not None:                                     # the model must stay buildable
                r.append(50.0 * np.minimum(np.asarray(checks(q), float), 0.0))
            return np.concatenate(r)
        lens = [np.median([cams[n][6:8] for n in order if gi[n] == k], axis=0) for k in range(len(groups))]
        x = np.r_[x0, *[cams[n][:6] for n in order], *lens]
        lo = np.r_[x0 - 0.4 * scale, np.full(len(x) - len(free), -np.inf)]
        hi = np.r_[x0 + 0.4 * scale, np.full(len(x) - len(free), np.inf)]
        sol = least_squares(f, np.clip(x, lo + 1e-9, hi - 1e-9), bounds=(lo, hi), x_scale="jac", loss="soft_l1",
                            f_scale=6.0, max_nfev=20000)
        fitted, cams = unpack(sol.x)
    for n, v in held.items():                       # the checks: only their own camera is fitted, to the result
        cams[n] = fit_camera(fn(fitted, v.get("pose", {})), v, v["size"])
    views.update(held)
    out = {"key": key, "free": free, "params": {k: round(float(fitted[k]), 1) for k in free},
           "start": {k: params[k] for k in free}, "views": {}}
    for name, v in views.items():
        c = cams[name]
        r = residuals(c, fn(fitted, v.get("pose", {})), v, v["size"]).reshape(-1, 2)
        names = list(v.get("points", {})) + [f"{n} ({i + 1})" for n, uvs in v.get("curves", {}).items()
                                             for i in range(len(uvs))]
        out["views"][name] = {"source": v.get("source", ""), "size": list(v["size"]), "holdout": bool(v.get("holdout")),
                              "camera": [float(t) for t in c], "focal_px": round(math.exp(c[6]), 1),
                              "k1": round(float(c[7]), 4), "rms_px_camera_only": round(before[name], 2),
                              "rms_px": round(rms(r), 2),
                              "residual_px": {n: round(float(np.hypot(*e)), 1) for n, e in zip(names, r)}}
    (REFS / key / "fit.json").write_text(json.dumps(out, indent=1))
    return out


def group(view) -> str:
    """The camera a view was taken with: its "camera" field, else the YouTube id in its source."""
    import re
    if view.get("camera"):
        return view["camera"]
    m = re.search(r"(?:youtu\.be/|v=)([\w-]{11})", view.get("source", ""))
    return m.group(1) if m else view.get("source", "")


def frame_path(key: str, name: str, view: dict) -> Path:
    """refs/<key>/<name>.jpg, fetched through the Pi from the view's "video" and "t" if it isn't there."""
    p = REFS / key / f"{name}.jpg"
    if not p.exists() and view.get("video") is not None:
        import shutil
        import frames
        shutil.copy(frames.grab(view["video"], [float(view["t"])])[0], p)
    return p


def rms(r) -> float:
    r = np.asarray(r, float).reshape(-1, 2)
    return float(np.sqrt(np.mean((r * r).sum(1)))) if len(r) else 0.0


# ================================================================================================= drawing
def _undistort(img: np.ndarray, cam, size) -> np.ndarray:
    import cv2
    f = math.exp(cam[6])
    K = np.array([[f, 0, size[0] / 2], [0, f, size[1] / 2], [0, 0, 1]])
    return cv2.undistort(img, K, np.array([cam[7], 0, 0, 0, 0], float)) if abs(cam[7]) > 1e-4 else img


_BUILT: dict = {}


def build(key: str, params: dict | None = None):
    """(Instrument, entries) of any model in MODULES, built afresh with the given parameters (the fitted ones) put in
    its parameter dict for the duration, and tessellated as tour.py does, with its module's materials."""
    import tour
    tag = (key, json.dumps(params, sort_keys=True))
    if tag in _BUILT:
        return _BUILT[tag]
    for name in MODULES:
        if not (HERE / f"{name}.py").exists():
            continue
        mod = importlib.import_module(name)
        if key not in getattr(mod, "REGISTRY", {}):
            continue
        tour.MATS.update(getattr(mod, "MATERIALS", {}))
        live = getattr(mod, "ANCHORS", {}).get(key, (None,))[0] if params else None
        saved = dict(live) if live is not None else None
        if live is not None:
            live.update(params)
        try:
            inst = mod.REGISTRY[key]()
        finally:
            if live is not None:
                live.clear()
                live.update(saved)
        _BUILT[tag] = (inst, tour.piece_entries(inst))
        return _BUILT[tag]
    raise KeyError(f"{key!r} is in no module's REGISTRY ({', '.join(MODULES)})")


def render(key: str, cam, size, pose: dict, params: dict | None = None):
    """(rgb, mask) of the model alone, seen by the fitted camera (pinhole: the lens term is taken out of the frame)."""
    import pyvista as pv
    import scene
    inst, entries = build(key, params)
    v = {k: j.v0 for k, j in inst.joints.items()}
    v.update(pose or {})
    world = {}

    def mat(piece):
        if piece in world:
            return world[piece]
        j = inst.joints.get(piece)
        if j is None:
            m = np.eye(4)
        else:
            m = j.matrix(v.get(piece, 0.0))
            if j.parent:
                m = mat(j.parent) @ m
        world[piece] = m
        return m
    pl = pv.Plotter(off_screen=True, window_size=list(size), lighting="none")
    scene.light_kit(pl.renderer)
    pl.set_background("black")
    for piece, ents in entries.items():
        j = inst.joints.get(piece)
        if j is not None and j.kind == "fade" and v.get(piece, 0.0) < 0.5:
            continue
        m = mat(piece)
        for e in ents:
            if not e["mesh"].n_points:
                continue
            pl.add_mesh(e["mesh"].transform(m, inplace=False), color=e["color"], opacity=max(e["opacity"], 0.6),
                        smooth_shading=True, split_sharp_edges=True, feature_angle=scene.FEATURE_ANGLE,
                        ambient=0.25, diffuse=0.8, **scene.surface_style(e["specular"]))
    R = rodrigues(cam[:3])
    C = -R.T @ np.asarray(cam[3:6])
    fwd = R.T @ np.array([0, 0, 1.0])
    up = -(R.T @ np.array([0, 1.0, 0]))
    f = math.exp(cam[6])
    pl.camera.position = tuple(C)
    pl.camera.focal_point = tuple(C + fwd * 1000.0)
    pl.camera.up = tuple(up)
    pl.camera.view_angle = math.degrees(2 * math.atan(size[1] / 2 / f))
    pl.renderer.ResetCameraClippingRange()
    rgb = pl.screenshot(return_img=True)[:, :, :3]
    depth = pl.get_image_depth(fill_value=np.nan)
    pl.close()
    return rgb, ~np.isnan(depth)


def draw(key: str, names=None, rebuild=False) -> list[Path]:
    import cv2
    from PIL import Image
    fit = json.loads((REFS / key / "fit.json").read_text())
    params, fn, free = anchor_sets(key)
    params.update(fit.get("params", {}))
    OUT.joinpath(key).mkdir(parents=True, exist_ok=True)
    paths = []
    for name, fv in fit["views"].items():
        if names and name not in names:
            continue
        view = json.loads((REFS / key / f"{name}.json").read_text())
        anchors = fn(params, view.get("pose", {}))
        size = tuple(fv["size"])
        cam = np.asarray(fv["camera"])
        frame = np.asarray(Image.open(frame_path(key, name, view)).convert("RGB"))
        und = _undistort(frame, cam, size)
        rgb, mask = render(key, cam, size, view.get("pose", {}), fit.get("params") or None)
        pin = np.r_[cam[:7], 0.0]                        # the undistorted frame is a pinhole image
        base = (0.55 * und + 0.45 * np.where(mask[..., None], rgb, und)).astype(np.uint8)
        over = und.copy()
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        creases = cv2.Canny(gray, 40, 110) > 0
        creases &= cv2.erode(mask.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        lw = max(2, round(size[0] / 640))
        for img in (over, base):
            img[creases] = (0, 230, 255)
            cv2.drawContours(img, cnts, -1, (255, 225, 0), lw)
        for img in (over, base):
            for n, uv in view.get("points", {}).items():
                p = project(pin, sample(anchors[n]), size)[0]
                q = _undistort_pt(uv, cam, size)
                cv2.circle(img, tuple(int(round(t)) for t in q), 5 * lw // 2, (40, 220, 60), -1)
                cv2.drawMarker(img, tuple(int(round(t)) for t in p), (235, 40, 40), cv2.MARKER_CROSS, 7 * lw, lw)
            for n, uvs in view.get("curves", {}).items():
                for uv in uvs:
                    q = _undistort_pt(uv, cam, size)
                    cv2.circle(img, tuple(int(round(t)) for t in q), 2 * lw, (40, 220, 60), -1)
        sheet = np.concatenate([over, base], axis=1)
        h = 540
        im = Image.fromarray(sheet).resize((int(sheet.shape[1] * h / sheet.shape[0]), h), Image.LANCZOS)
        _caption(im, f"{key} / {name}: {fit['views'][name]['source']}   rms {fv['rms_px']} px, "
                     f"f {fv['focal_px']} px, k1 {fv['k1']}")
        path = OUT / key / f"{name}.jpg"
        im.save(path, quality=88)
        paths.append(path)
        print(path)
    return paths


def _undistort_pt(uv, cam, size):
    import cv2
    f = math.exp(cam[6])
    K = np.array([[f, 0, size[0] / 2], [0, f, size[1] / 2], [0, 0, 1]])
    if abs(cam[7]) <= 1e-4:
        return np.asarray(uv, float)
    p = cv2.undistortPoints(np.array([[uv]], np.float64), K, np.array([cam[7], 0, 0, 0, 0], float), P=K)
    return p[0, 0]


def _caption(im, text):
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    d.rectangle((0, 0, im.width, 22), fill=(0, 0, 0))
    d.text((6, 3), text, fill=(255, 255, 255), font=f)


if __name__ == "__main__":
    cmd, key = sys.argv[1], sys.argv[2]
    if cmd == "solve":
        res = solve(key)
        print(json.dumps({k: res[k] for k in ("free", "start", "params")}, indent=1))
        for n, v in res["views"].items():
            tag = " (held out of the fit)" if v.get("holdout") else ""
            print(f"{n}{tag}: rms {v['rms_px_camera_only']} -> {v['rms_px']} px, f {v['focal_px']}, k1 {v['k1']}")
            worst = sorted(v["residual_px"].items(), key=lambda kv: -kv[1])[:6]
            print("   worst:", ", ".join(f"{a} {b}" for a, b in worst))
    elif cmd == "draw":
        draw(key, [a for a in sys.argv[3:] if not a.startswith("--")] or None, rebuild="--rebuild" in sys.argv)
