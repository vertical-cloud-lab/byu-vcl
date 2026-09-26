#!/usr/bin/env python3
"""Write the 1:1 drill template for the lid as SVG, DXF and PDF (Letter).

The outline is read off the bottom face of the printed drill template, so the
paper, the DXF and the printed part cannot drift apart.

    python template.py              # writes ../exports/drill_template_1to1.{svg,dxf,pdf}
"""
from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import cadquery as cq
import ezdxf
import numpy as np
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.TopAbs import TopAbs_REVERSED

from lid_mount import EXPORTS, Params, corners, make_drill_template

PAGE_W, PAGE_H = 215.9, 279.4        # US Letter, mm
CX, CY = PAGE_W / 2, 112.0           # where the optical axis lands on the page
SCALE_BAR_COLOR = "#0050d0"           # checked in the PDF to prove the print scale


def wire_points(wire: cq.Wire, step: float = 0.5) -> list[tuple[float, float]]:
    """Ordered (x, y) points around a wire: exact line ends, sampled arcs.
    Each edge is flipped as needed so it starts where the previous one ended."""
    pts: list[tuple[float, float]] = []
    exp = BRepTools_WireExplorer(wire.wrapped)
    while exp.More():
        edge = cq.Edge(exp.Current())
        n = 2 if edge.geomType() == "LINE" else max(8, int(edge.Length() / step))
        seg = [(round(v.x, 4), round(v.y, 4)) for v in edge.positions(np.linspace(0.0, 1.0, n))]
        if pts:
            d_start = math.dist(pts[-1], seg[0])
            d_end = math.dist(pts[-1], seg[-1])
            if d_end < d_start:
                seg = seg[::-1]
        elif exp.Orientation() == TopAbs_REVERSED:
            seg = seg[::-1]
        for q in seg:
            if not pts or math.dist(pts[-1], q) > 1e-6:
                pts.append(q)
        exp.Next()
    if len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
        pts.pop()
    # The first edge may have gone the wrong way round; if so the chain is
    # still closed but starts backwards, which is harmless for drawing.
    return pts


def to_page(x: float, y: float) -> tuple[float, float]:
    return CX + x, CY - y


def outline(p: Params) -> list[tuple[float, float]]:
    face = make_drill_template(p).faces("<Z").val()
    return wire_points(face.outerWire())


def svg(p: Params, pts: list[tuple[float, float]]) -> str:
    path = "M " + " L ".join(f"{a:.3f},{b:.3f}" for a, b in (to_page(x, y) for x, y in pts)) + " Z"
    reach = p.base_size / 2 + p.tab_len + 4
    el = []
    add = el.append
    add(f'<path d="{path}" fill="none" stroke="#000" stroke-width="0.3"/>')
    # Axis lines through the tab notches.
    for a, b in (((-reach, 0), (reach, 0)), ((0, -reach), (0, reach))):
        (x1, y1), (x2, y2) = to_page(*a), to_page(*b)
        add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#666" '
            f'stroke-width="0.15" stroke-dasharray="6 1.5 1 1.5"/>')
    # Lens cutout.
    cx, cy = to_page(0, 0)
    add(f'<circle cx="{cx}" cy="{cy}" r="{p.cutout_d / 2}" fill="none" stroke="#c00000" '
        f'stroke-width="0.35" stroke-dasharray="3 1.5"/>')
    add(f'<circle cx="{cx}" cy="{cy}" r="0.8" fill="#c00000"/>')
    # Bolt holes: final size in the acrylic, with a centre-punch cross.
    for x, y in corners(p.bolt_xy):
        hx, hy = to_page(x, y)
        add(f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r="{p.lid_bolt_d / 2}" fill="none" stroke="#000" stroke-width="0.3"/>')
        add(f'<path d="M {hx - 4:.2f},{hy:.2f} H {hx + 4:.2f} M {hx:.2f},{hy - 4:.2f} V {hy + 4:.2f}" '
            f'stroke="#000" stroke-width="0.15"/>')
    # Cable-side arrow, as engraved on the base.
    ax, ay = to_page(0, -34)
    add(f'<path d="M {ax - 5:.2f},{ay:.2f} L {ax + 5:.2f},{ay:.2f} L {ax:.2f},{ay + 10:.2f} Z" '
        f'fill="none" stroke="#000" stroke-width="0.25"/>')

    def text(x, y, s, size=3.2, anchor="start", weight="normal", fill="#000"):
        add(f'<text x="{x:.2f}" y="{y:.2f}" font-family="Helvetica, Arial, sans-serif" font-size="{size}" '
            f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">{s}</text>')

    text(PAGE_W / 2, 14, "OT-2 lid camera mount — drill template, ACTUAL SIZE", 5.0, "middle", "bold")
    text(PAGE_W / 2, 20.5, "Print at 100% / “Actual size”, then check both scale bars below before drilling.",
         3.2, "middle")
    half, tip = p.base_size / 2, p.base_size / 2 + p.tab_len
    lx, ly = to_page(-half, tip - 5)
    text(lx, ly, "lens cutout (red):", 2.8, fill="#c00000")
    text(lx, ly + 4, f"Ø{p.cutout_d:.1f} mm = 2 in hole saw", 2.8, fill="#c00000")
    rx, ry = to_page(half, tip - 5)
    text(rx, ry, f"4 × Ø{p.lid_bolt_d:.1f} mm bolt holes", 2.8, "end")
    text(rx, ry + 4, "for M4 screws + nylon washers", 2.8, "end")
    bx, by = to_page(half, -tip + 9)
    text(bx, by, "X axis → plate columns 1–12", 2.8, "end")
    text(bx, by + 4, "(sensor long axis)", 2.8, "end")
    qx, qy = to_page(-half, -tip + 9)
    text(qx, qy, "▽ = cable side (−Y),", 2.8)
    text(qx, qy + 4, "matches the arrow on the base", 2.8)
    text(cx + 2, cy + 4.2, "pilot / centre punch", 2.4, fill="#c00000")

    # Scale bars: 50 mm and 2 in.
    y0 = 196.0
    x0 = 30.0
    add(f'<line x1="{x0}" y1="{y0}" x2="{x0 + 50}" y2="{y0}" stroke="{SCALE_BAR_COLOR}" stroke-width="0.6"/>')
    for t in range(0, 51, 10):
        add(f'<line x1="{x0 + t}" y1="{y0 - 2}" x2="{x0 + t}" y2="{y0 + 2}" stroke="{SCALE_BAR_COLOR}" stroke-width="0.3"/>')
    text(x0, y0 + 6, "50 mm", 3.0, fill=SCALE_BAR_COLOR)
    x1 = 110.0
    add(f'<line x1="{x1}" y1="{y0}" x2="{x1 + 50.8}" y2="{y0}" stroke="{SCALE_BAR_COLOR}" stroke-width="0.6"/>')
    for t in range(0, 9):
        add(f'<line x1="{x1 + t * 6.35:.3f}" y1="{y0 - (2 if t % 4 == 0 else 1)}" x2="{x1 + t * 6.35:.3f}" '
            f'y2="{y0 + (2 if t % 4 == 0 else 1)}" stroke="{SCALE_BAR_COLOR}" stroke-width="0.3"/>')
    text(x1, y0 + 6, "2 in", 3.0, fill=SCALE_BAR_COLOR)

    notes = [
        "1. Tape the mount down first and position it with the live preview (preview_server.py) until the plate is",
        "    centred and square. Trace the base outline and the four tab notches onto the lid with a fine marker.",
        "2. Line this sheet (or the printed drill template) up with the tracing and centre-punch the five marks.",
        "3. Take the window off (4 screws, slide, lift). Clamp it over a wooden backer board, keep any film on, and",
        "    use a sharp plastic or step drill at low speed with light pressure; ease off before breaking through.",
        f"4. Cut the lens hole with a {p.cutout_d:.1f} mm (2 in) hole saw at low speed; deburr every edge.",
        "5. Bolt with M4 button-head screws from inside the robot into the nuts trapped in the base,",
        "    with a nylon washer under each head: the pipette head passes ~9 mm below the window.",
        "    Snug only: acrylic cracks from over-tightening and from holes drilled near an edge.",
    ]
    for i, line in enumerate(notes):                 # SVG collapses leading spaces, so indent by x
        text(18 if not line.startswith(" ") else 23, 212 + i * 5.4, line.strip(), 2.9)
    text(PAGE_W / 2, PAGE_H - 10, "vertical-cloud-lab/byu-vcl · ot2-overhead-camera/lid-mount · generated by cad/template.py",
         2.4, "middle", fill="#666")
    body = "\n  ".join(el)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}mm" height="{PAGE_H}mm" '
            f'viewBox="0 0 {PAGE_W} {PAGE_H}">\n  {body}\n</svg>\n')


def dxf(p: Params, pts: list[tuple[float, float]], path: Path) -> None:
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4       # millimetres
    msp = doc.modelspace()
    for name, color in (("OUTLINE", 7), ("DRILL", 5), ("CUTOUT", 1), ("AXES", 8)):
        doc.layers.add(name, color=color)
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "OUTLINE"})
    msp.add_circle((0, 0), p.cutout_d / 2, dxfattribs={"layer": "CUTOUT"})
    msp.add_circle((0, 0), p.template_center_d / 2, dxfattribs={"layer": "DRILL"})
    for x, y in corners(p.bolt_xy):
        msp.add_circle((x, y), p.lid_bolt_d / 2, dxfattribs={"layer": "DRILL"})
    reach = p.base_size / 2 + p.tab_len
    msp.add_line((-reach, 0), (reach, 0), dxfattribs={"layer": "AXES"})
    msp.add_line((0, -reach), (0, reach), dxfattribs={"layer": "AXES"})
    doc.saveas(path)


def pdf(svg_path: Path, pdf_path: Path) -> None:
    chrome = next((c for c in ("google-chrome", "chromium", "chromium-browser") if shutil.which(c)), None)
    if chrome is None:
        print("no Chrome/Chromium found; skipping the PDF")
        return
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "t.html"
        html.write_text(
            "<!doctype html><html><head><style>@page{size:8.5in 11in;margin:0}"
            "html,body{margin:0;padding:0}svg{display:block}</style></head><body>"
            + svg_path.read_text() + "</body></html>")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path}", html.as_uri()],
                       check=True, capture_output=True, timeout=120)


def check_pdf_scale(pdf_path: Path) -> list[float]:
    """Lengths (mm) of the two scale bars as drawn in the PDF."""
    import pymupdf
    page = pymupdf.open(pdf_path)[0]
    target = tuple(int(SCALE_BAR_COLOR[i:i + 2], 16) / 255 for i in (1, 3, 5))
    bars = []
    for d in page.get_drawings():
        if d.get("color") and all(abs(a - b) < 0.02 for a, b in zip(d["color"], target)) and d.get("width", 0) > 1.5:
            for item in d["items"]:
                if item[0] == "l":
                    bars.append(abs(item[2].x - item[1].x) / 72 * 25.4)
    return sorted(bars)


def main() -> None:
    p = Params()
    EXPORTS.mkdir(parents=True, exist_ok=True)
    pts = outline(p)
    svg_path = EXPORTS / "drill_template_1to1.svg"
    svg_path.write_text(svg(p, pts))
    dxf(p, pts, EXPORTS / "drill_template_1to1.dxf")
    pdf_path = EXPORTS / "drill_template_1to1.pdf"
    pdf(svg_path, pdf_path)
    if pdf_path.exists():
        print("scale bars in the PDF (mm):", [round(v, 2) for v in check_pdf_scale(pdf_path)], "expected [50.0, 50.8]")
    print(f"wrote {svg_path.name}, drill_template_1to1.dxf, {pdf_path.name} to {EXPORTS}")


if __name__ == "__main__":
    main()
