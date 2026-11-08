"""Draw a rePowder model over a frame of the lab's footage, with a pinhole camera fitted to the frame (round 7 of PR #329).

    xvfb-run -a python3 repowder/overlay.py fit  refs/repowder_r7/t1_2640_lid_open.json OUT.jpg [MODEL_DIR] [lid latch bolt]
    xvfb-run -a python3 repowder/overlay.py draw OUT.jpg.cam.json FRAME.jpg OUT2.jpg MODEL_DIR [lid latch bolt]

``fit`` reads a view's picks (``refs/repowder_r7/<view>.json``: model points in mm, the pixels they are at) and its frame
(``<view>.jpg`` beside it), fits the camera (solvePnP over a range of focal lengths, square pixels, the principal point
at the centre, no lens term), renders the model with it and writes the frame with the model's silhouette (yellow), its
creases (cyan), the picks (green) and where the camera puts them (red), beside the frame and the render blended. The
camera goes to OUT.jpg.cam.json. ``draw`` renders another model (round 6's, say) with that same camera, so the two can be
compared on the same frame (out/org_vertical_lab_r7.jpg). Joint values: the lid, latch and bolt, 0..1 of their travel.
The picks are by eye on a 40 px grid; the fits are good to 20-30 px, enough to see a lid on the wrong side, not to
measure millimetres (register.py does that).
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def load_model(mdir):
    spec = importlib.util.spec_from_file_location("rp_overlay_model", Path(mdir) / "model.py")
    M = importlib.util.module_from_spec(spec)
    sys.modules["rp_overlay_model"] = M
    spec.loader.exec_module(M)
    return M


def fit(view: dict, W: int, H: int) -> dict:
    import cv2
    X = np.array([p["model"] for p in view["points"]], float)
    U = np.array([p["pixel"] for p in view["points"]], float)
    best = None
    for f in np.linspace(400, 2200, 181):
        K = np.array([[f, 0, W / 2], [0, f, H / 2], [0, 0, 1.0]])
        ok, rv, tv = cv2.solvePnP(X, U, K, None, flags=cv2.SOLVEPNP_SQPNP)
        if not ok:
            continue
        pr, _ = cv2.projectPoints(X, rv, tv, K, None)
        e = float(np.sqrt(((pr[:, 0] - U) ** 2).sum(1).mean()))
        if best is None or e < best[0]:
            best = (e, f, rv, tv)
    e, f, rv, tv = best
    R, _ = cv2.Rodrigues(rv)
    C = -R.T @ tv.ravel()
    return dict(rms=e, f=float(f), C=C.tolist(), fwd=(R.T @ [0, 0, 1.0]).tolist(), up=(-(R.T @ [0, 1.0, 0])).tolist(),
                W=W, H=H)


def render(M, cam: dict, joints=(1.0, 0.0, 0.0)) -> np.ndarray:
    import pyvista as pv
    lid, latch, bolt = joints
    of = {n: "lid" for n in M.LID_PARTS}
    of.update(latch_lever="latch", latch_loop="latch", latch_bolt="bolt")
    pl = pv.Plotter(off_screen=True, window_size=(cam["W"], cam["H"]))
    pl.set_background("black")
    for n, d in M.meshes().items():
        if d["whole"] is None or n == "floor" or d["group"] == "utilities":
            continue
        m = d["whole"]
        if n in of:
            m = m.transform(M.joint_matrix(of[n], dict(lid=lid, latch=latch, bolt=bolt)[of[n]]), inplace=False)
        pl.add_mesh(m, color=d["color"], smooth_shading=True)
    C, fwd = np.array(cam["C"]), np.array(cam["fwd"])
    pl.camera.position, pl.camera.focal_point, pl.camera.up = tuple(C), tuple(C + fwd * 1000), tuple(cam["up"])
    pl.camera.view_angle = math.degrees(2 * math.atan(cam["H"] / 2 / cam["f"]))
    img = pl.screenshot(return_img=True)
    pl.close()
    return img


def draw(frame: np.ndarray, ren: np.ndarray, cam: dict, view: dict | None = None) -> np.ndarray:
    import cv2
    ov = frame.copy()
    blend = (0.55 * frame + 0.45 * ren).astype(np.uint8)
    mask = (ren.sum(2) > 0).astype(np.uint8)
    cont, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(ov, cont, -1, (255, 230, 0), 2)
    ov[cv2.Canny(ren.mean(2).astype(np.uint8), 20, 60) > 0] = (0, 220, 255)
    if view:
        C, fwd, up = (np.array(cam[k]) for k in ("C", "fwd", "up"))
        right = np.cross(fwd, up)
        for p in view["points"]:
            d = np.array(p["model"], float) - C
            u = (cam["W"] / 2 + cam["f"] * d @ right / (d @ fwd), cam["H"] / 2 - cam["f"] * d @ up / (d @ fwd))
            cv2.circle(ov, tuple(int(v) for v in p["pixel"]), 4, (0, 255, 0), -1)
            cv2.drawMarker(ov, tuple(int(v) for v in u), (255, 0, 0), cv2.MARKER_CROSS, 10, 2)
    return np.concatenate([ov, blend], 1)


if __name__ == "__main__":
    from PIL import Image
    cmd = sys.argv[1]
    if cmd == "fit":
        vpath, out = Path(sys.argv[2]), sys.argv[3]
        mdir = sys.argv[4] if len(sys.argv) > 4 else HERE
        joints = tuple(float(v) for v in sys.argv[5:8]) if len(sys.argv) > 7 else (1.0, 0.0, 0.0)
        view = json.loads(vpath.read_text())
        frame = np.array(Image.open(vpath.with_suffix(".jpg")).convert("RGB"))
        cam = fit(view, frame.shape[1], frame.shape[0])
        print(f"{vpath.stem}: rms {cam['rms']:.1f} px, f {cam['f']:.0f} px")
        Image.fromarray(draw(frame, render(load_model(mdir), cam, joints), cam, view)).save(out, quality=90)
        Path(out + ".cam.json").write_text(json.dumps(cam))
    elif cmd == "draw":
        cam = json.loads(Path(sys.argv[2]).read_text())
        frame = np.array(Image.open(sys.argv[3]).convert("RGB"))
        joints = tuple(float(v) for v in sys.argv[6:9]) if len(sys.argv) > 8 else (1.0, 0.0, 0.0)
        Image.fromarray(draw(frame, render(load_model(sys.argv[5]), cam, joints), cam)).save(sys.argv[4], quality=90)
    print("done")
