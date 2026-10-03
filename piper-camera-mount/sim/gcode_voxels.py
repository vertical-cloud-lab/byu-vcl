#!/usr/bin/env python3
"""From a part's sliced G-code to the material inside it: what was extruded where, in which direction.

- parse(): every extruding G1/G2/G3 move as a straight segment (arcs cut into chords of at most 5 deg),
  with its layer (from Bambu's '; Z_HEIGHT' comments), '; LINE_WIDTH' and '; FEATURE'. A layer's height
  is its Z_HEIGHT step: Bambu also writes '; LAYER_HEIGHT' mid-layer for its thick bridges (one nozzle
  diameter), which is the bridge bead's height, not the layer's. Coordinates are moved into the STL's
  print frame by the placement the slicer used.
- Raster: per layer, a fine pixel grid (a quarter of a line width) in the print frame. Each pixel gets
  the feature of the bead covering it (0 = no bead) and that bead's direction (degrees, 0-179). A bead
  covers the pixels within half its line width of its centreline. Dense features (walls, skins, solid
  infill, bridges, gap fill) win over sparse infill where they overlap. A third array marks pixels
  inside the STL's cross-section at mid-layer, so that "inside the part but no bead" (the space
  between sparse infill lines) is known too.
- Checks: the rastered bead volume against the G-code's own extruded volume.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numba import njit

FEATURES = {"Outer wall": 1, "Inner wall": 2, "Overhang wall": 3, "Sparse infill": 4, "Internal solid infill": 5,
            "Top surface": 6, "Bottom surface": 7, "Bridge": 8, "Gap infill": 9, "Floating vertical shell": 10}
NAMES = {v: k for k, v in FEATURES.items()}
SPARSE = 4
WALLS = (1, 2, 3, 10)


@dataclass
class Toolpath:
    seg: np.ndarray          # (n, 4) x0 y0 x1 y1, print frame
    layer: np.ndarray        # (n,) layer index
    width: np.ndarray        # (n,) line width
    feat: np.ndarray         # (n,) FEATURES code
    evol: np.ndarray         # (n,) filament volume pushed, mm^3
    z_top: np.ndarray        # (L,) top of each layer
    h: np.ndarray            # (L,) layer height


def parse(text: str, offset_xy=(0.0, 0.0), filament_d: float = 1.75) -> Toolpath:
    area = math.pi * filament_d ** 2 / 4
    x = y = 0.0
    absolute = True
    feat, width = 0, 0.4
    z_tops = []
    segs, lay, wid, fts, ev = [], [], [], [], []
    num = re.compile(r"([XYZEIJF])(-?\d*\.?\d+)")
    for line in text.splitlines():
        if not line:
            continue
        c = line[0]
        if c == ";":
            if line.startswith("; Z_HEIGHT:"):
                z = float(line[11:])
                if not z_tops or abs(z - z_tops[-1]) > 1e-6:
                    z_tops.append(z)
            elif line.startswith("; FEATURE:"):
                feat = FEATURES.get(line[10:].strip(), 0)
            elif line.startswith("; LINE_WIDTH:"):
                width = float(line[13:])
            continue
        if c == "G":
            head = line.split(";")[0].split()
            if not head:
                continue
            g = head[0]
            if g == "G90":
                absolute = True
                continue
            if g == "G91":
                absolute = False
                continue
            if g not in ("G0", "G1", "G2", "G3"):
                continue
            vals = {k: float(v) for k, v in num.findall(" ".join(head[1:]))}
            if not absolute:
                x += vals.get("X", 0.0)
                y += vals.get("Y", 0.0)
                continue
            nx, ny = vals.get("X", x), vals.get("Y", y)
            e = vals.get("E", 0.0)
            if e > 0 and feat and z_tops and (nx != x or ny != y):
                L = len(z_tops) - 1
                if g in ("G2", "G3"):
                    cx, cy = x + vals.get("I", 0.0), y + vals.get("J", 0.0)
                    a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
                    r = math.hypot(x - cx, y - cy)
                    if g == "G3" and a1 <= a0:
                        a1 += 2 * math.pi
                    if g == "G2" and a1 >= a0:
                        a1 -= 2 * math.pi
                    n = max(1, int(math.ceil(abs(a1 - a0) / math.radians(5))))
                    aa = np.linspace(a0, a1, n + 1)
                    px, py = cx + r * np.cos(aa), cy + r * np.sin(aa)
                    px[-1], py[-1] = nx, ny
                    for k in range(n):
                        segs.append((px[k], py[k], px[k + 1], py[k + 1]))
                        lay.append(L)
                        wid.append(width)
                        fts.append(feat)
                        ev.append(e * area / n)
                else:
                    segs.append((x, y, nx, ny))
                    lay.append(L)
                    wid.append(width)
                    fts.append(feat)
                    ev.append(e * area)
            x, y = nx, ny
    seg = np.array(segs, float)
    seg[:, [0, 2]] -= offset_xy[0]
    seg[:, [1, 3]] -= offset_xy[1]
    z_top = np.array(z_tops)
    return Toolpath(seg, np.array(lay), np.array(wid), np.array(fts, np.uint8), np.array(ev),
                    z_top, np.diff(np.r_[0.0, z_top]).round(6))


@njit(cache=True)
def _raster(cls, ang, seg, layer, width, feat, angle, ox, oy, dp, sparse):
    L, ny, nx = cls.shape
    for s in range(seg.shape[0]):
        x0, y0, x1, y1 = seg[s, 0], seg[s, 1], seg[s, 2], seg[s, 3]
        hw = width[s] / 2
        f = feat[s]
        k = layer[s]
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        i0 = max(0, int((min(x0, x1) - hw - ox) / dp))
        i1 = min(nx - 1, int((max(x0, x1) + hw - ox) / dp) + 1)
        j0 = max(0, int((min(y0, y1) - hw - oy) / dp))
        j1 = min(ny - 1, int((max(y0, y1) + hw - oy) / dp) + 1)
        for j in range(j0, j1 + 1):
            py = oy + (j + 0.5) * dp
            for i in range(i0, i1 + 1):
                px = ox + (i + 0.5) * dp
                t = 0.0
                if L2 > 0:
                    t = ((px - x0) * dx + (py - y0) * dy) / L2
                    t = min(1.0, max(0.0, t))
                qx, qy = x0 + t * dx - px, y0 + t * dy - py
                if qx * qx + qy * qy <= hw * hw:
                    old = cls[k, j, i]
                    if f == sparse and old != 0 and old != sparse:
                        continue
                    cls[k, j, i] = f
                    ang[k, j, i] = angle[s]


@dataclass
class Raster:
    cls: np.ndarray       # (L, ny, nx) uint8 feature code
    ang: np.ndarray       # (L, ny, nx) uint8 bead direction, degrees 0-179
    inside: np.ndarray    # (L, ny, nx) bool, inside the STL cross-section at mid-layer
    origin: np.ndarray    # (ox, oy)
    dp: float
    z_top: np.ndarray
    h: np.ndarray

    def lookup(self, p: np.ndarray):
        """cls, ang, inside at print-frame points p (n, 3); outside the raster -> 0, 0, False."""
        i = np.floor((p[:, 0] - self.origin[0]) / self.dp).astype(np.int64)
        j = np.floor((p[:, 1] - self.origin[1]) / self.dp).astype(np.int64)
        k = np.searchsorted(self.z_top, p[:, 2] - 1e-9)
        L, ny, nx = self.cls.shape
        ok = (i >= 0) & (i < nx) & (j >= 0) & (j < ny) & (k < L) & (p[:, 2] > 0)
        c = np.zeros(len(p), np.uint8)
        a = np.zeros(len(p), np.uint8)
        ins = np.zeros(len(p), bool)
        c[ok] = self.cls[k[ok], j[ok], i[ok]]
        a[ok] = self.ang[k[ok], j[ok], i[ok]]
        ins[ok] = self.inside[k[ok], j[ok], i[ok]]
        return c, a, ins


def rasterize(tp: Toolpath, stl: Path, dp: float, margin: float = 1.0) -> Raster:
    import cv2
    import trimesh

    mesh = trimesh.load_mesh(stl)
    lo, hi = mesh.bounds
    ox, oy = lo[0] - margin, lo[1] - margin
    nx, ny = int(math.ceil((hi[0] - lo[0] + 2 * margin) / dp)), int(math.ceil((hi[1] - lo[1] + 2 * margin) / dp))
    L = len(tp.z_top)
    cls = np.zeros((L, ny, nx), np.uint8)
    ang = np.zeros((L, ny, nx), np.uint8)
    d = tp.seg[:, 2:] - tp.seg[:, :2]
    angle = (np.degrees(np.arctan2(d[:, 1], d[:, 0])) % 180).round().astype(np.int64) % 180
    _raster(cls, ang, tp.seg, tp.layer.astype(np.int64), tp.width, tp.feat, angle.astype(np.uint8), ox, oy, dp, SPARSE)
    inside = np.zeros((L, ny, nx), bool)
    zmid = tp.z_top - tp.h / 2
    sections = mesh.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zmid))
    shift = 4
    for k, sec in enumerate(sections):
        if sec is None:
            continue
        img = np.zeros((ny, nx), np.uint8)
        for poly in sec.polygons_full:
            ext = np.asarray(poly.exterior.coords)
            pts = [((ext - [ox, oy]) / dp - 0.5) * (1 << shift)]
            cv2.fillPoly(img, [np.round(pts[0]).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=shift)
            for hole in poly.interiors:
                hp = ((np.asarray(hole.coords) - [ox, oy]) / dp - 0.5) * (1 << shift)
                cv2.fillPoly(img, [np.round(hp).astype(np.int32)], 0, lineType=cv2.LINE_8, shift=shift)
        inside[k] = img.astype(bool)
    return Raster(cls, ang, inside, np.array([ox, oy]), dp, tp.z_top, tp.h)


def volume_check(tp: Toolpath, r: Raster) -> dict:
    """Rastered bead volume vs the filament the G-code pushed, per feature and in total."""
    vol_px = r.dp ** 2 * r.h[:, None, None]
    out = {}
    for code, name in NAMES.items():
        ras = float(((r.cls == code) * vol_px).sum())
        gc = float(tp.evol[tp.feat == code].sum())
        if gc > 0 or ras > 0:
            out[name] = {"raster_mm3": round(ras, 1), "gcode_mm3": round(gc, 1)}
    tot_r = float(((r.cls > 0) * vol_px).sum())
    tot_g = float(tp.evol.sum())
    inside = float((r.inside * vol_px).sum())
    out["total"] = {"raster_mm3": round(tot_r, 1), "gcode_mm3": round(tot_g, 1),
                    "raster / gcode": round(tot_r / tot_g, 4), "stl_cross_sections_mm3": round(inside, 1),
                    "beads outside the STL section (% of raster)": round(100 * float(((r.cls > 0) & ~r.inside).sum()
                                                                             * 1.0 / max(1, (r.cls > 0).sum())), 2)}
    return out
