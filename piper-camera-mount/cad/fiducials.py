#!/usr/bin/env python3
"""Can the HQ Camera see the gripper and a target in the same picture? A rendered check.

Renders what the HQ Camera sees (pinhole at the lens front, 2028 x 1520, its binned mode) with:

  - AprilTag 36h11 #1 and #2, 5 mm, on the printed wedges on the upper and lower finger,
  - AprilTag 36h11 #10, 20 mm, on a card square to the approach axis, 30, 60 or 120 mm past
    the fingertips (the "object" fiducial),

at finger openings from 0 to 100 mm. Each picture goes through OpenCV's AprilTag detector and
solvePnP (IPPE_SQUARE); the recovered poses are compared with the true ones. Also writes a
printable sheet of the tags at exact size.

    xvfb-run -a -s "-screen 0 1920x1080x24" python fiducials.py     # -> ../exports/fiducials/*, ../renders/*

The pictures are ideal: no blur, noise or lens distortion, and the lens is in focus everywhere.
They show geometry (what is in view, at what angle and how many pixels), not a real camera's
accuracy.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
import cv2
import numpy as np
import pyvista as pv

import reference
from piper_mount import (ASSEMBLY, COLORS, FINGERTIP_Y, Params, build, hq_fov, optical_axes, place_tag_wedges,
                         tag_poses)
from render import add_gripper, mesh

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "exports" / "fiducials"
RENDERS = HERE.parent / "renders"
SIZE = (2028, 1520)
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
FINGER_IDS = {"upper": 1, "lower": 2}
TARGET_ID, TARGET_SIZE = 10, 20.0
OPENINGS = (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
TARGETS = (30, 60, 120)


def detector() -> cv2.aruco.ArucoDetector:
    prm = cv2.aruco.DetectorParameters()
    prm.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    return cv2.aruco.ArucoDetector(DICT, prm)


def tag_image(tag_id: int, cell: int = 24) -> np.ndarray:
    """The tag with one white cell of border all round (10 x 10 cells), RGB."""
    img = cv2.aruco.generateImageMarker(DICT, tag_id, 8 * cell)
    full = np.full((10 * cell, 10 * cell), 255, np.uint8)
    full[cell:9 * cell, cell:9 * cell] = img
    return np.dstack([full] * 3)


def tag_quad(centre, right, up, size) -> pv.PolyData:
    """A textured square: the tag (black edge `size`) and its white border."""
    s = size * 10 / 8
    c, r, u = (np.asarray(v, float) for v in (centre, right, up))
    pts = np.array([c - r * s / 2 - u * s / 2, c + r * s / 2 - u * s / 2, c + r * s / 2 + u * s / 2,
                    c - r * s / 2 + u * s / 2])
    quad = pv.PolyData(pts, np.array([4, 0, 1, 2, 3]))
    quad.active_texture_coordinates = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
    return quad


def vec(v) -> np.ndarray:
    return np.array(v.toTuple() if hasattr(v, "toTuple") else v, float)


def scene_tags(p: Params, opening: float, target: float | None) -> list[dict]:
    tags = []
    for t in tag_poses(p, opening):
        tags.append({"id": FINGER_IDS[t["name"]], "name": f"{t['name']} finger", "size": p.tag_size,
                     "centre": vec(t["centre"]) + vec(t["normal"]) * 0.05, "right": vec(t["right"]),
                     "up": vec(t["up"]), "normal": vec(t["normal"])})
    if target is not None:
        tags.append({"id": TARGET_ID, "name": "target", "size": TARGET_SIZE,
                     "centre": np.array([p.ax_x, FINGERTIP_Y - target, p.ax_z]),
                     "right": np.array([-1.0, 0, 0]), "up": np.array([0, 0, 1.0]), "normal": np.array([0, 1.0, 0])})
    return tags


class Scene:
    """The gripper, the mount and the tags, reused across renders (only the fingers move)."""

    def __init__(self, p: Params, parts: dict, with_mount: bool = True):
        self.p, self.parts, self.with_mount = p, parts, with_mount
        self.textures = {i: pv.numpy_to_texture(tag_image(i)) for i in (*FINGER_IDS.values(), TARGET_ID)}

    def render(self, opening: float, target: float | None, which: str = "hq", size=SIZE,
               annotate: bool = False) -> tuple[np.ndarray, list[dict]]:
        p = self.p
        pl = pv.Plotter(off_screen=True, window_size=size)
        pl.set_background((0.93, 0.93, 0.90))
        add_gripper(pl, opening=opening)
        if self.with_mount:                       # the mount itself, in case it gets in the way
            for name in ASSEMBLY:
                pl.add_mesh(mesh(self.parts[name]), color=COLORS[name], smooth_shading=False)
            pl.add_mesh(mesh(place_tag_wedges(p, opening)), color=COLORS["tag_wedge"], smooth_shading=False)
        tags = scene_tags(p, opening, target)
        if target is not None:
            card = pv.Plane(center=(p.ax_x, FINGERTIP_Y - target - 0.2, p.ax_z), direction=(0, 1, 0),
                            i_size=600, j_size=600)
            pl.add_mesh(card, color=(0.62, 0.66, 0.70))
        for t in tags:
            pl.add_mesh(tag_quad(t["centre"], t["right"], t["up"], t["size"]), texture=self.textures[t["id"]],
                        lighting=False)
        o, d, up = (vec(v) for v in optical_axes(p)[which])
        up = up - d * up.dot(d)
        up /= np.linalg.norm(up)
        vfov = hq_fov(p)[1] if which == "hq" else 67.0
        pl.camera.position = tuple(o)
        pl.camera.focal_point = tuple(o + d * 200)
        pl.camera.up = tuple(up)
        pl.camera.view_angle = vfov
        pl.camera.clipping_range = (1.0, 3000.0)
        img = pl.screenshot(return_img=True)
        pl.close()
        return img, [dict(t, cam=(o, d, up, vfov)) for t in tags]


def detect(img: np.ndarray, tags: list[dict], det: cv2.aruco.ArucoDetector) -> dict[int, dict | None]:
    h, w = img.shape[:2]
    o, d, up, vfov = tags[0]["cam"]
    f = (h / 2) / math.tan(math.radians(vfov / 2))
    K = np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1]])
    Rwc = np.vstack([np.cross(d, up), -up, d])          # world -> OpenCV camera (x right, y down, z ahead)
    corners, ids, _ = det.detectMarkers(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
    found = {} if ids is None else {int(i): c.reshape(4, 2) for i, c in zip(ids.ravel(), corners)}
    out = {}
    for t in tags:
        R_true = Rwc @ np.column_stack([t["right"], t["up"], t["normal"]])
        t_true = Rwc @ (t["centre"] - o)
        off_normal = math.degrees(math.acos(abs(float(np.dot(t["normal"], (o - t["centre"]) /
                                                             np.linalg.norm(o - t["centre"]))))))
        if t["id"] not in found:
            out[t["id"]] = None
            continue
        s = t["size"]
        obj = np.array([[-s / 2, s / 2, 0], [s / 2, s / 2, 0], [s / 2, -s / 2, 0], [-s / 2, -s / 2, 0]])
        _, rv, tv = cv2.solvePnP(obj, found[t["id"]], K, None, flags=cv2.SOLVEPNP_IPPE_SQUARE)
        R_est, _ = cv2.Rodrigues(rv)
        rot = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R_est.T @ R_true) - 1) / 2))))
        out[t["id"]] = {"position_error_mm": round(float(np.linalg.norm(tv.ravel() - t_true)), 2),
                        "rotation_error_deg": round(rot, 2), "view_angle_off_normal_deg": round(off_normal, 1),
                        "tag_edge_px": round(float(np.linalg.norm(found[t["id"]][0] - found[t["id"]][1])), 1),
                        "distance_mm": round(float(np.linalg.norm(t_true)), 1),
                        "corners": found[t["id"]].tolist(), "t_est": tv.ravel().tolist(), "t_true": t_true.tolist()}
    return out


def relative_error(res: dict) -> float | None:
    """Target position measured from the upper finger's tag: estimated vs true, mm."""
    a, b = res.get(FINGER_IDS["upper"]), res.get(TARGET_ID)
    if not a or not b:
        return None
    est = np.array(b["t_est"]) - np.array(a["t_est"])
    true = np.array(b["t_true"]) - np.array(a["t_true"])
    return round(float(np.linalg.norm(est - true)), 2)


def annotate(img: np.ndarray, res: dict) -> np.ndarray:
    out = img.copy()
    for tid, r in res.items():
        if not r:
            continue
        c = np.array(r["corners"], np.int32)
        cv2.polylines(out, [c], True, (230, 30, 30), 3, cv2.LINE_AA)
        x, y = c[:, 0].min(), c[:, 1].min() - 10
        label = f"#{tid}"
        cv2.putText(out, label, (int(x), int(max(y, 20))), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (230, 30, 30), 2, cv2.LINE_AA)
    return out


def tag_sheet(p: Params, path: Path) -> None:
    """Printable A4 sheet: finger tags at 5 mm (with 2 spares each) and target tags at 20 and 30 mm.
    Print at 100 % scale; each tag's black square is its nominal size."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 210)
    ax.set_ylim(0, 297)
    ax.axis("off")

    def put(tid, size, x, y, label=True):
        img = cv2.aruco.generateImageMarker(DICT, tid, 8 * 20)
        ax.imshow(img, cmap="gray", extent=(x, x + size, y, y + size), interpolation="nearest", vmin=0, vmax=255)
        if label:
            ax.text(x + size / 2, y - 1.5, f"36h11 #{tid}, {size:g} mm", ha="center", va="top", fontsize=5)

    ax.text(15, 282, "PiPER wrist camera mount: AprilTag 36h11 (print at 100 %, no scaling)", fontsize=9)
    ax.text(15, 276, "Finger tags #1 (upper) and #2 (lower): 5 mm, glue onto the printed wedges. "
                     "Target tags #10-#13: 20 and 30 mm.", fontsize=6)
    ax.plot([15, 65], [268, 268], color="black", lw=0.6)
    ax.text(40, 266, "50 mm scale check", ha="center", va="top", fontsize=5)
    x0, y = 15.0, 245.0
    for k, tid in enumerate((1, 1, 1, 2, 2, 2)):
        put(tid, p.tag_size, x0 + k * 20, y)
    for k, tid in enumerate((10, 11, 12, 13)):
        put(tid, TARGET_SIZE, x0 + k * 30, 205)
    for k, tid in enumerate((10, 11, 12, 13)):
        put(tid, 30.0, x0 + k * 45, 150)
    fig.savefig(path)
    fig.savefig(path.with_suffix(".svg"))
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RENDERS.mkdir(parents=True, exist_ok=True)
    p = Params()
    parts = build(p)
    scene = Scene(p, parts)
    det = detector()
    table = []
    for opening in OPENINGS:
        for target in TARGETS:
            img, tags = scene.render(opening, target)
            res = detect(img, tags, det)
            row = {"opening_mm": opening, "target_past_fingertips_mm": target,
                   "relative_error_mm (target from upper finger tag)": relative_error(res)}
            for tid, r in res.items():
                row[f"tag {tid}"] = None if r is None else {k: v for k, v in r.items()
                                                             if k not in ("corners", "t_est", "t_true")}
            table.append(row)
            if (opening, target) in ((40, 60),):
                cv2.imwrite(str(RENDERS / "view_hq.png"), cv2.cvtColor(annotate(img, res), cv2.COLOR_RGB2BGR))
            if (opening, target) in ((10, 30), (40, 60), (60, 120)):
                cv2.imwrite(str(OUT / f"hq_open{opening}_target{target}.png"),
                            cv2.cvtColor(annotate(img, res), cv2.COLOR_RGB2BGR))
            print(opening, target, {k: (None if v is None else (v["position_error_mm"], v["view_angle_off_normal_deg"],
                                                              v["tag_edge_px"])) for k, v in res.items()})
    # The Wide's view, for the stream.
    img, tags = scene.render(40, 60, which="cm3w", size=(1600, 900))
    cv2.imwrite(str(RENDERS / "view_cm3w.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    def seen(tid, target=None):
        return [o for o in OPENINGS if any(r["opening_mm"] == o and r[f"tag {tid}"] is not None and
                                           (target is None or r["target_past_fingertips_mm"] == target)
                                           for r in table)]
    summary = {
        "finger tags detected at openings (mm)": {"upper #1": seen(1), "lower #2": seen(2)},
        "target tag detected at openings (mm), by distance past the fingertips":
            {f"{t} mm": seen(TARGET_ID, t) for t in TARGETS},
        "worst position error, any detected tag (mm)": max(
            r[f"tag {tid}"]["position_error_mm"] for r in table for tid in (1, 2, 10) if r[f"tag {tid}"]),
        "worst rotation error, any detected tag (deg)": max(
            r[f"tag {tid}"]["rotation_error_deg"] for r in table for tid in (1, 2, 10) if r[f"tag {tid}"]),
        "finger tag view angle off its normal (deg)": [
            min(r[f"tag {tid}"]["view_angle_off_normal_deg"] for r in table for tid in (1, 2) if r[f"tag {tid}"]),
            max(r[f"tag {tid}"]["view_angle_off_normal_deg"] for r in table for tid in (1, 2) if r[f"tag {tid}"])],
        "finger tag edge (px, in the 2028 x 1520 picture)": [
            min(r[f"tag {tid}"]["tag_edge_px"] for r in table for tid in (1, 2) if r[f"tag {tid}"]),
            max(r[f"tag {tid}"]["tag_edge_px"] for r in table for tid in (1, 2) if r[f"tag {tid}"])],
        "worst target-from-finger-tag error (mm)": max(
            r["relative_error_mm (target from upper finger tag)"] for r in table
            if r["relative_error_mm (target from upper finger tag)"] is not None),
    }
    (OUT / "fiducials.json").write_text(json.dumps({"summary": summary, "cases": table}, indent=1) + "\n")
    tag_sheet(p, OUT / "tags.pdf")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
