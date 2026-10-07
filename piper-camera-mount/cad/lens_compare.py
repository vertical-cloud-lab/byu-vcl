#!/usr/bin/env python3
"""6 mm wide-angle or 16 mm telephoto on the HQ Camera? The numbers and pictures behind the choice.

Both official lenses go on the same camera, in the same place on the pod: the camera doesn't move,
only what is screwed into its CS mount changes. For each lens this works out

  - optics at the distances this mount works at (the finger tags 85-91 mm from the lens, a target
    30-120 mm past the fingertips): field of view, what it covers, pixels on a tag, how far the
    lens must move out to focus, and how sharp the near and far ends can be at once (depth of
    field, with diffraction);
  - fit: the lens against the printed parts, the gripper and the Wide's picture;
  - the HQ picture through it, with the same AprilTags and detector as fiducials.py.

    xvfb-run -a -s "-screen 0 1920x1080x24" python lens_compare.py
        # -> ../exports/lens_compare.json, ../renders/lens_compare.png
"""
from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

import cadquery as cq
import cv2
import numpy as np
import pyvista as pv

import reference
from fiducials import TARGET_ID, Scene, annotate, detect, detector, relative_error
from lenses import LENSES, lens_body_local, lens_screws_local, screw_sweep_local
from piper_mount import (CM3W_FOV, COLORS, FINGERTIP_Y, Params, build, gap, hq_fov, hq_place, in_view,
                         optical_axes, overlap, station_vec, tag_poses, view_pyramid)
from render import add_gripper, add_parts, mesh

HERE = Path(__file__).resolve().parent
EXPORTS = HERE.parent / "exports"
RENDERS = HERE.parent / "renders"

PIXEL = 1.55e-3                 # mm, IMX477
BINNED = 2 * PIXEL              # 2028 x 1520, the mode fiducials.py renders and a stream would use
WAVELENGTH = 0.55e-3            # mm, green
HQ_BACK_FOCUS = (12.5, 22.4)    # mm of lens back focus the CS-mount HQ takes (product brief)
TARGETS = (30, 60, 120)         # mm past the fingertips, as fiducials.py
F_NUMBERS = (2.8, 4.0, 5.6, 8.0, 11.0, 16.0)
VIEW = (40, 60)                 # opening, target past the tips: the pose of the pictures


def lens_params(p6: Params, key: str) -> Params:
    """Params with another lens on the same camera: the lens front moves, the camera doesn't."""
    lens = LENSES[key]
    front = station_vec(p6, 0, -(p6.hq_cs_seat + lens.front_s), 0)
    return dataclasses.replace(p6, lens=key, hq_front_x=front.x, hq_front_y=front.y)


def lens_parts(p: Params, parts6: dict) -> dict:
    """The 6 mm build with the lens (and its thumbscrews) swapped for p's."""
    out = dict(parts6)
    seat = -p.hq_cs_seat
    out["hq_lens"] = hq_place(p)(lens_body_local(p.lens_spec, seat))
    out["hq_lens_screws"] = hq_place(p)(lens_screws_local(p.lens_spec, seat, p.lens_screw_deg))
    return out


def depth(p: Params, pt: cq.Vector) -> float:
    """Distance from the lens front to a point, along the optical axis."""
    o, d, _ = optical_axes(p)["hq"]
    return (pt - o).dot(d)


def thin_lens_v(f: float, u: float) -> float:
    return 1.0 / (1.0 / f - 1.0 / u)


def blur_um(f: float, n: float, u_near: float, u_far: float) -> dict:
    """Focused where the near and far ends are equally soft: the defocus blur at either end, the
    diffraction spot at the working f-number, and the two combined, in um."""
    v1, v2 = thin_lens_v(f, u_near), thin_lens_v(f, u_far)
    vm = 2 * v1 * v2 / (v1 + v2)                     # equal blur both sides
    defocus = (f / n) * abs(v1 - vm) / v1
    airy = 2.44 * WAVELENGTH * n * vm / f
    return {"defocus": defocus * 1e3, "diffraction": airy * 1e3, "total": math.hypot(defocus, airy) * 1e3,
            "focus_at_mm": 1.0 / (1.0 / f - 1.0 / vm)}


def optics(p: Params) -> dict:
    lens = p.lens_spec
    f = lens.f
    hf, vf = hq_fov(p)
    pts = {}
    for opening in (0.0, 60.0):
        for t in tag_poses(p, opening):
            pts[f"{t['name']} finger tag, {opening:.0f} mm open"] = t["centre"]
    for tgt in TARGETS:
        pts[f"target {tgt} mm past the fingertips"] = cq.Vector(p.ax_x, FINGERTIP_Y - tgt, p.ax_z)
    u = {k: depth(p, v) for k, v in pts.items()}
    tag_u = [v for k, v in u.items() if "finger tag" in k]
    near = min(tag_u)
    rows = {}
    for k, v in pts.items():
        size = p.tag_size if "finger tag" in k else 20.0
        rows[k] = {
            "distance along the axis (mm)": round(u[k], 1),
            "in view": in_view(p, v)[0],
            "picture covers (mm, across x up)": [round(2 * u[k] * math.tan(math.radians(a / 2)), 1) for a in (hf, vf)],
            "px per mm (2028 x 1520)": round(f / BINNED / u[k], 1),
            f"tag edge, {size:g} mm tag (px, 2028 x 1520, face-on)": round(size * f / BINNED / u[k]),
        }
    e = {k: thin_lens_v(f, v) - f for k, v in u.items()}
    e_mod = thin_lens_v(f, lens.mod_m * 1000) - f
    dof = {}
    for label, far_key in (("finger tags + target 60 mm past the tips", "target 60 mm past the fingertips"),
                           ("finger tags + target 120 mm past the tips", "target 120 mm past the fingertips")):
        far = u[far_key]
        by_n = {f"f/{n:g}": {k: round(v, 1) for k, v in blur_um(f, n, near, far).items()} for n in F_NUMBERS}
        best = min(by_n, key=lambda k: by_n[k]["total"])
        dof[label] = {"near, far (mm)": [round(near, 1), round(far, 1)], "by f-number (um)": by_n,
                      "sharpest": best, "blur at the sharpest (px, 2028 x 1520)": round(by_n[best]["total"] / 1e3 / BINNED, 1)}
    cg = (p.hq_cs_seat - p.hq_standoff - p.pod_t) + lens.front_s / 2      # from the pod's front face
    return {
        "lens": dataclasses.asdict(lens),
        "field of view (deg, across x up), pinhole from the sensor": [round(hf, 1), round(vf, 1)],
        "field of view (deg, across x up x diagonal), Raspberry Pi's figure": list(lens.fov_hq_deg),
        "points": rows,
        "focus": {
            "lens moved out from infinity focus, to the nearest finger tag (mm)": round(max(e.values()), 3),
            "lens moved out from infinity focus, to the farthest target (mm)": round(min(e.values()), 3),
            "the lens's own focus range reaches (mm out, at its 0.2 m MOD)": round(e_mod, 3),
            "back-focus ring has to add (mm)": round(max(0.0, max(e.values()) - e_mod), 3),
        },
        "depth of field": dof,
        "load": {"mass (g)": lens.mass_g, "centre of mass in front of the pod's face (mm, approx.)": round(cg, 1),
                 "moment about the pod's face (g mm)": round(lens.mass_g * cg)},
    }


def fit(p: Params, parts: dict) -> dict:
    """The lens (thumbscrews wherever they can point) against everything else."""
    sweep = hq_place(p)(screw_sweep_local(p.lens_spec, -p.hq_cs_seat))
    lens_all = parts["hq_lens"].union(sweep)
    g = reference.gripper()
    res = {"overlap_mm3": {}, "gap_mm": {}}
    for n in ("bracket", "pod", "cm_pcb", "cm_module"):
        res["overlap_mm3"][f"lens + thumbscrew circles vs {n}"] = round(overlap(lens_all, parts[n]), 1)
    res["overlap_mm3"]["lens + thumbscrew circles vs gripper body"] = round(overlap(lens_all, g["body"]), 1)
    for opening, tag in ((0.0, "closed"), (100.0, "fully open")):
        res["overlap_mm3"][f"lens + thumbscrew circles vs fingers ({tag})"] = round(
            overlap(lens_all, reference.gripper(opening)["fingers"]), 1)
    o, d, up = optical_axes(p)["cm3w"]
    res["overlap_mm3"]["lens inside the Wide's view (250 mm deep)"] = round(
        overlap(view_pyramid(o, d, up, *CM3W_FOV, 250.0, aperture=1.5), parts["hq_lens"].union(parts["hq_lens_screws"])), 1)
    res["gap_mm"]["lens to the bracket"] = round(gap(parts["hq_lens"], parts["bracket"]), 2)
    res["gap_mm"]["lens to the finger plate"] = round(gap(parts["hq_lens"], g["body"]), 2)
    res["gap_mm"]["thumbscrew circles to the finger plate"] = round(gap(sweep, g["body"]), 2)
    o_hq = optical_axes(p)["hq"][0]
    res["lens front behind the finger plate's front face (mm)"] = round(o_hq.y - (-4.52), 1)
    res["lens front behind the fingertips (mm)"] = round(o_hq.y - FINGERTIP_Y, 1)
    res["clash"] = {k: v for k, v in res["overlap_mm3"].items() if v > 1e-3}
    return res, lens_all


def disk(d: float) -> np.ndarray:
    r = d / 2
    n = int(math.ceil(r))
    y, x = np.mgrid[-n:n + 1, -n:n + 1]
    k = (x * x + y * y <= r * r + 0.25).astype(np.float32)
    return k / k.sum()


def defocus(img: np.ndarray, z: np.ndarray, f: float, n: float, focus_mm: float) -> np.ndarray:
    """The ideal picture as the lens would take it focused at focus_mm and f/n: each pixel blurred by
    the disk its distance gives (geometric defocus, thin lens), then the whole picture by diffraction
    (Gaussian, sigma = 0.42 lambda N at the working f-number). Pixels are gathered from a stack of
    uniformly blurred copies, which is rough at depth edges but fine on flat tags."""
    zz = np.where(np.isfinite(z), z, 1000.0)
    zz = np.clip(zz, f * 1.5, None)
    v = 1.0 / (1.0 / f - 1.0 / zz)
    vm = thin_lens_v(f, focus_mm)
    b = (f / n) * np.abs(v - vm) / v / BINNED                    # blur disk diameter, px
    levels = [0.0, 1.5, 2.5, 4.0, 6.0, 8.0, 11.0, 16.0, 22.0, 32.0, 45.0, 64.0, 90.0]
    src = img.astype(np.float32)
    out = np.zeros_like(src)
    prev = src
    for lo, hi in zip(levels[:-1], levels[1:]):
        nxt = cv2.filter2D(src, -1, disk(hi), borderType=cv2.BORDER_REPLICATE)
        w = np.clip((b - lo) / (hi - lo), 0.0, 1.0)[..., None]
        m = ((b >= lo) & (b < hi))[..., None]
        out = np.where(m, prev * (1 - w) + nxt * w, out)
        prev = nxt
    out = np.where((b >= levels[-1])[..., None], prev, out)
    sigma = 0.42 * WAVELENGTH * n * (vm / f) / BINNED
    out = cv2.GaussianBlur(out, (0, 0), sigma)
    return np.clip(out, 0, 255).astype(np.uint8)


def views(p: Params, parts: dict, det, n: float, focus_mm: float) -> tuple[np.ndarray, dict]:
    """What the detector finds at every opening and target, in the ideal picture and focused at
    focus_mm and f/n; and the picture at VIEW as the lens would take it, annotated."""
    scene = Scene(p, parts)
    found, pictured = {}, None
    for opening in (0, 20, 40, 60, 80, 100):
        for target in TARGETS:
            im, tg, z = scene.render(opening, target, depth=True)
            soft = defocus(im, z, p.lens_f, n, focus_mm)
            row = {}
            for label, picture in (("ideal", im), (f"f/{n:g}, focused at {focus_mm:.0f} mm", soft)):
                r = detect(picture, tg, det)
                row[label] = {"finger tags": [tid for tid in (1, 2) if r.get(tid)], "target": bool(r.get(TARGET_ID)),
                              "target from finger tag error (mm)": relative_error(r),
                              "worst position error (mm)": max((v["position_error_mm"] for v in r.values() if v),
                                                               default=None)}
                if (opening, target) == VIEW and picture is soft:
                    pictured = (annotate(soft, r), r)
            found[f"{opening} mm open, target {target} mm past"] = row
    summary = {}
    for label in next(iter(found.values())):
        cases = [v[label] for v in found.values()]
        summary[label] = {
            "openings with both finger tags detected": sorted({int(k.split()[0]) for k, v in found.items()
                                                              if len(v[label]["finger tags"]) == 2}),
            "target detected (cases of 18)": sum(c["target"] for c in cases),
            "finger tag and target in the same picture (cases of 18)": sum(
                bool(c["finger tags"]) and c["target"] for c in cases),
            "worst target-from-finger-tag error (mm)": max((c["target from finger tag error (mm)"] for c in cases
                                                           if c["target from finger tag error (mm)"] is not None),
                                                          default=None),
        }
    img, r = pictured
    summary["at the pictured pose"] = {str(k): (None if v is None else {"edge px": v["tag_edge_px"],
                                                                        "position error mm": v["position_error_mm"]})
                                       for k, v in r.items()}
    return img, {"summary": summary, "cases": found}


def closeup(p: Params, parts: dict, clash: cq.Workplane | None, path: Path) -> None:
    """The pod on its seat, from outside and in front, the lens and what it hits."""
    pl = pv.Plotter(off_screen=True, window_size=(1100, 900))
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    add_gripper(pl, opening=40.0, opacity=0.35)
    names = ("pod", "carrier", "hq_pcb", "hq_mount", "hq_lens", "hq_lens_screws", "cm_pcb", "cm_module")
    add_parts(pl, parts, names=names)
    pl.add_mesh(mesh(parts["bracket"]), color=COLORS["bracket"], opacity=0.55, smooth_shading=False)
    if clash is not None and clash.val().isValid() and clash.val().Volume() > 1e-3:
        pl.add_mesh(mesh(clash), color=(0.9, 0.05, 0.05))
    o, d, _ = (np.array(v.toTuple()) for v in optical_axes(lens_params(p, "6mm"))["hq"])
    focal = o + d * 5.0
    pl.camera_position = [tuple(focal + np.array([-150.0, -150.0, 95.0])), tuple(focal), (0, 0, 1)]
    pl.camera.zoom(1.25)
    pl.screenshot(path)
    pl.close()


def figure(panels: list[tuple[Path, str]], out: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(16, 13), gridspec_kw={"height_ratios": [1.0, 0.93]})
    for ax, (img, text) in zip(axs.ravel(), panels):
        ax.imshow(cv2.cvtColor(cv2.imread(str(img)), cv2.COLOR_BGR2RGB))
        ax.set_title(text, fontsize=12, loc="left")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out, dpi=90)
    plt.close(fig)


def main() -> None:
    p6 = Params()
    assert p6.lens == "6mm"
    parts6 = build(p6)
    det = detector()
    out = {}
    tmp = RENDERS / "_lens_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    for key in ("6mm", "16mm"):
        p = lens_params(p6, key)
        parts = lens_parts(p, parts6) if key != "6mm" else parts6
        res_fit, lens_all = fit(p, parts)
        clash = None
        if res_fit["clash"]:
            clash = lens_all.intersect(parts["bracket"])
        opt = optics(p)
        dof = opt["depth of field"]["finger tags + target 60 mm past the tips"]
        n = float(dof["sharpest"][2:])
        focus = dof["by f-number (um)"][dof["sharpest"]]["focus_at_mm"]
        img, res_view = views(p, parts, det, n, focus)
        cv2.imwrite(str(tmp / f"view_{key}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        closeup(p, parts, clash, tmp / f"pod_{key}.png")
        out[key] = {"optics": opt, "fit": res_fit, "rendered views": res_view,
                    "pictures taken at": {"f-number": n, "focus (mm from the lens front)": round(focus, 1)}}
        print(key, json.dumps({"fit": res_fit["clash"], "views": res_view["summary"]}, indent=1))
    o6, o16 = out["6mm"], out["16mm"]
    hf6, vf6 = o6["optics"]["field of view (deg, across x up), pinhole from the sensor"]
    hf16, vf16 = o16["optics"]["field of view (deg, across x up), pinhole from the sensor"]
    def caption(key, hf, vf):
        o = out[key]
        at = o["pictures taken at"]
        label = f"f/{at['f-number']:g}, focused at {at['focus (mm from the lens front)']:.0f} mm"
        both = o["rendered views"]["summary"][label]["finger tag and target in the same picture (cases of 18)"]
        return (f"HQ through the {key[:-2]} mm ({hf:.0f} x {vf:.0f} deg), {label}:\n"
                f"a finger tag and the target detected together in {both} of 18 poses")
    figure([
        (tmp / "pod_6mm.png", "6 mm wide-angle (CS mount): O30 x 34 mm, 53 g.\n"
                              "Fits the seat; its two thumbscrews clear at any angle"),
        (tmp / "pod_16mm.png", "16 mm telephoto (C mount, on the C-CS adapter): O39 x 50 mm, 134 g.\n"
                               "Red: where it would cut into the seat"),
        (tmp / "view_6mm.png", caption("6mm", hf6, vf6)),
        (tmp / "view_16mm.png", caption("16mm", hf16, vf16)),
    ], RENDERS / "lens_compare.png")
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    (EXPORTS / "lens_compare.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: {"optics": {kk: v["optics"][kk] for kk in ("points", "focus", "load")},
                          "depth of field": {kk: {x: vv[x] for x in ("near, far (mm)", "sharpest",
                                                                      "blur at the sharpest (px, 2028 x 1520)")}
                                             for kk, vv in v["optics"]["depth of field"].items()}}
                      for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
