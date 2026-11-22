"""Fit the machining cell's machine models to footage of the real machines, by silhouette overlap (#367).

Sterling, on PR #373 (2026-11-22): "Your model of the machines probably need to be refined ... Estimating camera
intrinsics of a video that shows the same kind of machine in action, looking at keyframes of tutorial videos ... doing
model checks of volume overlap. Aiming for high perfection on the overlap between our model and the different images
considering those camera intrinsic corrections and maybe doing a background removal before doing that comparison."

    python3 machining_fit.py masks st10      # the machine cut out of each frame by SAM 2 -> .frames/masks/st10/
    python3 machining_fit.py fit st10        # cameras, then cameras and the model's free dimensions -> refs/st10/fit.json
    python3 machining_fit.py draw st10       # the overlap drawn on each frame -> out/register/st10/

For each view (``refs/<key>/<view>.json``, register.py's format, its frame fetched by frames.py):

1. **The camera from picks.** register.py's own solver (solvePnP over a range of focal lengths, then least squares):
   a pinhole with square pixels, its principal point at the centre, one radial lens term once there are 10 picks.
   The lens is an intrinsic, so views from one video share it. The picks are the model's named points
   (``machining_cell.st10_anchors``), read off gridded frames.
2. **The background removed.** SAM 2 (Meta's Segment Anything 2.1, ``sam2.1_l.pt`` through ultralytics, on the CPU),
   prompted with a box round the machine as the picks' camera sees the model, and points on its body. The prompt only
   says where the machine is; the outline is SAM's. A view's ``"ignore"`` polygons are left out of the comparison (a
   person in front, or a different bar feeder), and its ``"parts"`` list says which of the model's parts are in that
   machine (the showroom ST-10 has no bar feeder).
3. **The overlap.** The model's silhouette (every triangle of its closed outside, projected through the fitted camera,
   lens term and all, so the frame needn't be undistorted) against SAM's mask: IoU, and the mean distance between the
   two outlines in pixels.
4. **The refinement.** The cameras and the model's free dimensions (``FREE[key]``) are moved to raise the IoU, the
   picks kept within a few pixels, and each dimension pulled softly back to the drawing's value, so a dimension that no
   view sees stays as drawn. Cameras and dimensions alternate (Powell), three rounds.

``fit.json`` keeps every view's camera, lens, the IoU and outline distance before (the model as it was, at the picks'
camera), at the picks' camera with the new model, and after the refinement, and the fitted dimensions.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

import register as RG

HERE = Path(__file__).resolve().parent
REFS = HERE / "refs"
OUT = HERE / "out" / "register"
MASKS = HERE / ".frames" / "masks"
WORK_W = 640                                      # the comparison runs at this width (the frames are 1280)


def _st10():
    import machining_cell as M
    return dict(params=dict(M.ST10), anchors=M.st10_anchors,
                parts=lambda p, names=None: {k: v for k, v in M.st10_parts(p, inside=False).items()
                                             if names is None or any(k.startswith(n) for n in names)},
                free=["W", "H", "base_h", "base_x1", "pend_x0", "pend_x1", "pend_z0", "pend_z1", "pend_d",
                      "scr_x0", "scr_x1", "scr_z0", "scr_z1", "panel_x0", "win_x0", "win_w", "win_z0", "win_z1",
                      "lcov_w", "lcov_z0", "lcov_z1", "conv_x1", "conv_top", "conv_head", "conv_low",
                      "feed_z0", "feed_z1", "feed_lid", "feed_l"])


KEYS = {"st10": _st10}


# ============================================================================================ silhouettes
def silhouette(meshes: dict, cam, size) -> np.ndarray:
    """uint8 mask (h, w) of the union of every triangle of the meshes, through the camera (register.project)."""
    import cv2
    w, h = size
    m = np.zeros((h, w), np.uint8)
    for mesh, _c, _o in meshes.values():
        tri = mesh.triangulate()
        f = tri.faces.reshape(-1, 4)[:, 1:]
        uv = RG.project(cam, np.asarray(tri.points, float), size)
        if not np.all(np.isfinite(uv)):
            continue
        polys = np.round(uv[f] * 16).astype(np.int32)           # 4 fractional bits
        for tri_uv in polys:                                     # one at a time: fillPoly's even-odd rule would cut
            cv2.fillConvexPoly(m, tri_uv, 1, lineType=cv2.LINE_8, shift=4)   # a box's back faces out of its front
    return m


def overlap(model: np.ndarray, target: np.ndarray, keep: np.ndarray) -> tuple[float, float]:
    """(IoU, mean outline distance in px) of two masks over the pixels `keep`."""
    import cv2
    a, b = (model > 0) & keep, (target > 0) & keep
    union = np.count_nonzero(a | b)
    iou = np.count_nonzero(a & b) / union if union else 0.0
    ea = cv2.morphologyEx(a.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    eb = cv2.morphologyEx(b.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    if not ea.any() or not eb.any():
        return iou, 999.0
    da = cv2.distanceTransform((~ea).astype(np.uint8), cv2.DIST_L2, 3)
    db = cv2.distanceTransform((~eb).astype(np.uint8), cv2.DIST_L2, 3)
    return iou, float(0.5 * (db[ea & keep].mean() + da[eb & keep].mean()))


def _scaled(cam, s: float) -> np.ndarray:
    """The same camera for a frame scaled by s (focal length scales, the lens term doesn't)."""
    c = np.array(cam, float)
    c[6] += math.log(s)
    return c


# ============================================================================================ views and masks
def views(key: str) -> dict:
    from PIL import Image
    out = {}
    for p in sorted((REFS / key).glob("*.json")):
        if p.name == "fit.json":
            continue
        v = json.loads(p.read_text())
        v["frame"] = RG.frame_path(key, p.stem, v)
        v["size"] = Image.open(v["frame"]).size
        out[p.stem] = v
    return out


def keep_mask(v: dict) -> np.ndarray:
    """True where the view is compared: the whole frame less its "ignore" polygons."""
    import cv2
    w, h = v["size"]
    k = np.ones((h, w), np.uint8)
    for poly in v.get("ignore", []):
        cv2.fillPoly(k, [np.asarray(poly, np.int32)], 0)
    return k > 0


def look_at(C, target, f: float) -> np.ndarray:
    """register.py's camera vector for a camera at C (machine mm) looking at target, level, focal length f px."""
    import cv2
    C, target = np.asarray(C, float), np.asarray(target, float)
    zc = (target - C) / np.linalg.norm(target - C)
    xc = np.cross(zc, (0.0, 0.0, 1.0))
    xc /= np.linalg.norm(xc)
    yc = np.cross(zc, xc)
    Rm = np.array([xc, yc, zc])
    rv, _ = cv2.Rodrigues(Rm)
    return np.r_[rv.ravel(), -Rm @ C, math.log(f), 0.0]


def centre(cam) -> np.ndarray:
    Rm = RG.rodrigues(cam[:3])
    return -Rm.T @ np.asarray(cam[3:6], float)


def height_penalty(cam, lo=300.0, hi=4000.0) -> float:
    """Pixels of penalty for a camera below 0.3 m or above 4 m: the picks of a flat front can't tell a camera above
    the floor from its mirror image below it, and solvePnP sometimes takes the mirror."""
    z = centre(cam)[2]
    return 0.05 * (max(0.0, lo - z) + max(0.0, z - hi))


def pick_camera(key: str, v: dict, params: dict) -> np.ndarray:
    """The view's camera from its picks (register.py's residuals and priors), started from solvePnP and, when the view
    gives one, from a rough camera position "cam_hint" (machine mm) looking at "look_at"; the best camera above the
    floor wins."""
    from scipy.optimize import least_squares
    spec = KEYS[key]()
    A = spec["anchors"](params)
    size = v["size"]
    if v.get("init_points"):          # the picks the start trusts: outer corners, not features the fit may still move
        v = dict(v, points={k: v["points"][k] for k in v["init_points"]})
    npick = len(v.get("points", {}))
    zc = v.get("cam_z")               # a rough height of the camera, mm (say, the roof seen edge-on): a soft pull
    starts = []
    try:
        starts.append(RG.init_camera(A, v, size))
    except RuntimeError:
        pass
    if "cam_hint" in v:
        tgt = v.get("look_at", [params.get("W", 1000.0) / 2, 300.0, 1100.0])
        for f in (0.6, 0.9, 1.4, 2.0):
            starts.append(look_at(v["cam_hint"], tgt, f * size[0]))
    best = None
    for c0 in starts:
        def fn(c):
            c = np.r_[c, 0.0] if len(c) == 7 else c
            return np.r_[RG.residuals(c, A, v, size), RG.line_residuals(c, v, size), RG.priors(c, size),
                         height_penalty(c) * 20.0, 0.0 if zc is None else (centre(c)[2] - zc) / 30.0]
        x0 = c0 if npick >= 10 else c0[:7]
        if len(starts) > 1 and npick < 4:
            x0 = c0[:7]
        sol = least_squares(fn, x0, x_scale="jac", loss="soft_l1", f_scale=6.0, max_nfev=4000)
        c = sol.x if len(sol.x) == 8 else np.r_[sol.x, 0.0]
        cost = float(np.mean(RG.residuals(c, A, v, size) ** 2)) + height_penalty(c) * 1e3
        if best is None or cost < best[0]:
            best = (cost, c)
    return best[1]


def sam_mask(key: str, name: str, v: dict, cam, params: dict, model: str = "sam2.1_l.pt") -> np.ndarray:
    """The machine cut out of the frame by SAM 2: a box round where the camera sees the model, points on its body."""
    import cv2
    from ultralytics import SAM
    spec = KEYS[key]()
    sil = silhouette(spec["parts"](params, v.get("parts")), cam, v["size"])
    ys, xs = np.nonzero(sil)
    w, h = v["size"]
    pad = 0.04 * max(xs.max() - xs.min(), ys.max() - ys.min())
    box = [max(0, xs.min() - pad), max(0, ys.min() - pad), min(w - 1, xs.max() + pad), min(h - 1, ys.max() + pad)]
    inner = cv2.erode(sil, np.ones((25, 25), np.uint8))
    pts = []
    for nm in v.get("sam_points", []):                 # anchor names that sit on the body, projected
        uv = RG.project(cam, RG.sample(spec["anchors"](params)[nm]), v["size"])[0]
        pts.append([float(uv[0]), float(uv[1])])
    for k in v.get("sam_pixels", []):                  # or pixels given outright
        pts.append([float(k[0]), float(k[1])])
    if not pts and inner.any():
        iy, ix = np.nonzero(inner)
        i = np.argsort((ix - ix.mean()) ** 2 + (iy - iy.mean()) ** 2)[0]
        pts.append([float(ix[i]), float(iy[i])])
    import os
    sam = SAM(os.environ.get("SAM_WEIGHTS", model))     # e.g. /tmp/sam2.1_l.pt: keep the 428 MB file out of the repo
    res = sam.predict(str(v["frame"]), bboxes=[box], points=[pts], labels=[[1] * len(pts)], verbose=False)
    m = res[0].masks.data.cpu().numpy()
    m = (m.max(axis=0) > 0.5).astype(np.uint8)
    out = MASKS / key
    out.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out / f"{name}.png"), m * 255)
    (out / f"{name}.json").write_text(json.dumps({"box": [float(b) for b in box], "points": pts, "model": model}))
    return m


def load_mask(key: str, name: str):
    import cv2
    p = MASKS / key / f"{name}.png"
    return (cv2.imread(str(p), cv2.IMREAD_GRAYSCALE) > 127).astype(np.uint8) if p.exists() else None


# ============================================================================================ the fit
def fit(key: str, rounds: int = 3, only=None) -> dict:
    import cv2
    from scipy.optimize import minimize
    spec = KEYS[key]()
    p0 = dict(spec["params"])
    free = list(spec["free"])
    V = views(key)
    if only:
        V = {k: v for k, v in V.items() if k in only}
    data = {}
    for n, v in V.items():
        cam = pick_camera(key, v, p0)
        tgt = load_mask(key, n)
        if tgt is None:
            tgt = sam_mask(key, n, v, cam, p0)
        s = WORK_W / v["size"][0]
        size = (WORK_W, int(round(v["size"][1] * s)))
        data[n] = dict(v=v, cam=cam, s=s, size=size,
                       tgt=cv2.resize(tgt, size, interpolation=cv2.INTER_NEAREST),
                       keep=cv2.resize(keep_mask(v).astype(np.uint8), size, interpolation=cv2.INTER_NEAREST) > 0)

    def score(n, cam, params):
        d = data[n]
        sil = silhouette(spec["parts"](params, d["v"].get("parts")), _scaled(cam, d["s"]), d["size"])
        return overlap(sil, d["tgt"], d["keep"])

    def picks_rms(n, cam, params):
        d = data[n]
        return RG.rms(RG.residuals(cam, spec["anchors"](params), d["v"], d["v"]["size"]))

    # the model as it was before this fit: the cell's previous box (machining_cell's old LATHE) is another model, so
    # "before" here is the drawing's model at the picks' camera, and fit.json says so
    before = {n: score(n, d["cam"], p0) for n, d in data.items()}
    params = dict(p0)
    scale = {k: max(abs(p0[k]), 50.0) for k in free}
    groups = {}
    for n, d in data.items():
        groups.setdefault(RG.group(d["v"]), []).append(n)

    def cam_loss(x, n, params):
        cam = np.r_[x[:7], data[n]["cam"][7]]
        iou, dist = score(n, cam, params)
        return (1 - iou) * 100 + 0.3 * dist + 0.05 * picks_rms(n, cam, params) ** 2 / 25.0 + height_penalty(cam)

    def par_loss(x):
        q = dict(params)
        q.update({k: p0[k] + x[i] * scale[k] for i, k in enumerate(free)})
        tot = 0.0
        for n, d in data.items():
            iou, dist = score(n, d["cam"], q)
            tot += (1 - iou) * 100 + 0.3 * dist + 0.05 * picks_rms(n, d["cam"], q) ** 2 / 25.0
        return tot / len(data) + 4.0 * float(np.sum(np.asarray(x) ** 2) / 0.01)   # 10 % off costs 4

    log = []
    for r in range(rounds):
        for n, d in data.items():
            sol = minimize(cam_loss, d["cam"][:7], args=(n, params), method="Powell",
                           options=dict(xtol=1e-3, ftol=1e-3, maxfev=1500))
            d["cam"] = np.r_[sol.x, d["cam"][7]]
        x0 = np.array([(params[k] - p0[k]) / scale[k] for k in free])
        sol = minimize(par_loss, x0, method="Powell", options=dict(xtol=1e-3, ftol=1e-4, maxfev=4000))
        params.update({k: p0[k] + sol.x[i] * scale[k] for i, k in enumerate(free)})
        it = {n: score(n, d["cam"], params) for n, d in data.items()}
        log.append({n: [round(a, 4), round(b, 2)] for n, (a, b) in it.items()})
        print(f"round {r + 1}: " + ", ".join(f"{n} IoU {a:.3f} ({b:.1f} px)" for n, (a, b) in it.items()), flush=True)
    after = {n: score(n, d["cam"], params) for n, d in data.items()}
    out = {"key": key, "work_width_px": WORK_W, "free": free,
           "params": {k: round(float(params[k]), 1) for k in free}, "start": {k: p0[k] for k in free},
           "changed_mm": {k: round(float(params[k] - p0[k]), 1) for k in free if abs(params[k] - p0[k]) >= 5.0},
           "rounds": log, "views": {}}
    for n, d in data.items():
        v = d["v"]
        c = d["cam"]
        out["views"][n] = {
            "source": v.get("source", ""), "size": list(v["size"]), "camera": [float(t) for t in c],
            "focal_px": round(math.exp(c[6]), 1), "k1": round(float(c[7]), 4),
            "hfov_deg": round(math.degrees(2 * math.atan(v["size"][0] / 2 / math.exp(c[6]))), 1),
            "picks_rms_px": round(picks_rms(n, c, params), 2),
            "iou_drawing_model_at_pick_camera": round(before[n][0], 4),
            "outline_px_drawing_model_at_pick_camera": round(before[n][1] / d["s"], 2),
            "iou_fitted": round(after[n][0], 4), "outline_px_fitted": round(after[n][1] / d["s"], 2),
            "parts": v.get("parts", "all")}
    (REFS / key / "fit.json").write_text(json.dumps(out, indent=1))
    return out


# ============================================================================================ drawing
def draw(key: str, old_box: bool = True) -> list[Path]:
    """Each frame with SAM's mask (blue tint), the fitted model's outline (yellow) and, for the record, the outline of
    the model the cell had before (the 3437 x 1596 x 2167 box, red) at the same camera."""
    import cv2
    spec = KEYS[key]()
    fit_ = json.loads((REFS / key / "fit.json").read_text())
    params = dict(spec["params"])
    params.update(fit_["params"])
    OUT.joinpath(key).mkdir(parents=True, exist_ok=True)
    paths = []
    for n, v in views(key).items():
        if n not in fit_["views"]:
            continue
        cam = np.array(fit_["views"][n]["camera"])
        img = cv2.imread(str(v["frame"]))
        tgt = load_mask(key, n)
        if tgt is not None:
            tint = img.copy()
            tint[tgt > 0] = (0.55 * tint[tgt > 0] + 0.45 * np.array([255, 120, 40])).astype(np.uint8)
            img = tint
        sil = silhouette(spec["parts"](params, v.get("parts")), cam, v["size"])
        cnts, _ = cv2.findContours(sil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(img, cnts, -1, (0, 230, 255), 2, cv2.LINE_AA)
        if old_box and key == "st10":
            ob = old_box_meshes()
            osil = silhouette(ob, cam, v["size"])
            cnts, _ = cv2.findContours(osil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(img, cnts, -1, (40, 40, 230), 2, cv2.LINE_AA)
        for poly in v.get("ignore", []):
            cv2.polylines(img, [np.asarray(poly, np.int32)], True, (160, 160, 160), 1, cv2.LINE_AA)
        fv = fit_["views"][n]
        txt = f"IoU {fv['iou_fitted']:.3f}, outline {fv['outline_px_fitted']:.1f} px (drawing's model: " \
              f"{fv['iou_drawing_model_at_pick_camera']:.3f})"
        cv2.rectangle(img, (0, 0), (img.shape[1], 30), (0, 0, 0), -1)
        cv2.putText(img, f"{n}: {txt}", (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        p = OUT / key / f"{n}.jpg"
        cv2.imwrite(str(p), img, [cv2.IMWRITE_JPEG_QUALITY, 88])
        paths.append(p)
        print(p)
    return paths


def old_box_meshes() -> dict:
    """The lathe as the cell drew it before this round, in the ST-10's frame: the installed envelope as one
    3437 x 1596 x 2167 mm box from the conveyor's end, with the 2104 x 1283 x 1000 mm loader beside it (PR #373 at
    5b41a36, lathe_parts()). Placed by its spindle nose, as the cell placed both."""
    import machining_cell as M
    # old cell frame: body x -1937..1500, y -2396..-800, z 0..2167; nose at x 198 (+ 64 to the collet nose), axis at
    # y -1270, z 1050. In the ST-10's frame x = X_HEAD - x_cell and y = Y_FRONT - y_cell, both models' noses at x 860
    xh, yf = M.X_HEAD, M.Y_FRONT
    body = M._box(xh - 1500, xh + 1937, yf + 800, yf + 2396, 0, 2167)
    loader = M._box(xh - 1500 - 2104, xh - 1500, yf + 1270 - 641.5, yf + 1270 + 641.5, 90, 1000)
    return {"body": (body, None, 1.0), "loader": (loader, None, 1.0)}


if __name__ == "__main__":
    cmd, key = sys.argv[1], sys.argv[2]
    rest = sys.argv[3:]
    if cmd == "masks":
        spec = KEYS[key]()
        for n, v in views(key).items():
            if rest and n not in rest:
                continue
            cam = pick_camera(key, v, spec["params"])
            m = sam_mask(key, n, v, cam, spec["params"])
            print(n, "mask", int(m.sum()), "px")
    elif cmd == "fit":
        print(json.dumps(fit(key, only=rest or None)["views"], indent=1))
    elif cmd == "draw":
        draw(key)
    else:
        sys.exit(__doc__)
