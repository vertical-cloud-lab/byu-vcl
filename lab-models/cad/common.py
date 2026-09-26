"""Shared helpers: materials, assemblies of named parts, and STEP/STL export.

Every model in this folder is a `Model`: a list of named solids, each with a material. The
same list feeds the STEP export (names and colours survive into Onshape), the STL export
and the PyVista renders, so there is one source of geometry for all three.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXPORTS = ROOT / "exports"
RENDERS = ROOT / "renders"
CACHE = HERE / ".cache"          # vendor CAD, fetched at run time and never committed

# name: (r, g, b, opacity, specular). Opacity only affects renders; STEP carries the colour.
MATERIALS = {
    "glass":        (0.80, 0.90, 0.95, 0.30, 0.9),
    "polystyrene":  (0.86, 0.89, 0.93, 0.55, 0.6),
    "polypropylene": (0.93, 0.93, 0.90, 1.00, 0.2),
    "pp_blue":      (0.16, 0.42, 0.80, 1.00, 0.3),
    "pp_black":     (0.09, 0.09, 0.10, 1.00, 0.3),
    "pp_white":     (0.95, 0.95, 0.93, 1.00, 0.2),
    "pp_yellow":    (0.97, 0.80, 0.20, 1.00, 0.2),
    "rubber":       (0.55, 0.12, 0.10, 1.00, 0.1),
    "aluminium":    (0.78, 0.79, 0.81, 1.00, 0.7),
    "steel":        (0.62, 0.63, 0.66, 1.00, 0.7),
    "brass":        (0.80, 0.65, 0.30, 1.00, 0.6),
    "graphite":     (0.20, 0.20, 0.21, 1.00, 0.2),
    "powder_al":    (0.58, 0.59, 0.61, 1.00, 0.05),
    "powder_si":    (0.36, 0.37, 0.42, 1.00, 0.05),
    "liquid":       (0.25, 0.55, 0.92, 0.75, 0.6),
    "pla_orange":   (0.95, 0.52, 0.13, 1.00, 0.2),
    "pla_grey":     (0.45, 0.47, 0.50, 1.00, 0.2),
    "pla_white":    (0.92, 0.92, 0.90, 1.00, 0.2),
    "petg_teal":    (0.10, 0.55, 0.55, 1.00, 0.3),
    "pei":          (0.72, 0.55, 0.25, 1.00, 0.4),
    "resin":        (0.12, 0.12, 0.13, 1.00, 0.3),
    "printer_grey": (0.30, 0.31, 0.33, 1.00, 0.3),
    "printer_white": (0.88, 0.88, 0.86, 1.00, 0.3),
    "printer_black": (0.13, 0.13, 0.14, 1.00, 0.3),
    "extrusion":    (0.70, 0.71, 0.73, 1.00, 0.5),
    "acrylic":      (0.85, 0.92, 0.95, 0.25, 0.9),
    "tinted":       (0.35, 0.33, 0.25, 0.35, 0.9),
    "paint_blue":   (0.12, 0.30, 0.62, 1.00, 0.3),
    "paint_red":    (0.72, 0.13, 0.12, 1.00, 0.3),
    "paint_white":  (0.93, 0.93, 0.92, 1.00, 0.2),
    "paint_grey":   (0.55, 0.56, 0.58, 1.00, 0.3),
    "wood":         (0.78, 0.64, 0.45, 1.00, 0.1),
    "benchtop":     (0.18, 0.18, 0.19, 1.00, 0.3),
    "wall":         (0.90, 0.89, 0.86, 1.00, 0.0),
    "floor":        (0.74, 0.73, 0.70, 1.00, 0.1),
    "door":         (0.62, 0.48, 0.33, 1.00, 0.2),
    "screen":       (0.05, 0.06, 0.08, 1.00, 0.8),
    "pcb":          (0.10, 0.40, 0.20, 1.00, 0.3),
    "copper":       (0.80, 0.45, 0.25, 1.00, 0.6),
}


@dataclass
class Part:
    name: str
    shape: cq.Shape
    material: str


@dataclass
class Model:
    """A named group of parts, in millimetres, with z = 0 on the surface it stands on."""
    key: str
    title: str
    parts: list[Part] = field(default_factory=list)
    source: str = ""          # "modelled from specs", "vendor STEP", ...
    notes: dict = field(default_factory=dict)

    def add(self, name: str, shape, material: str) -> "Model":
        if isinstance(shape, cq.Workplane):
            shape = shape.val() if len(shape.vals()) == 1 else cq.Compound.makeCompound(shape.vals())
        self.parts.append(Part(name, shape, material))
        return self

    def moved(self, x=0.0, y=0.0, z=0.0, rz=0.0, key: str | None = None) -> "Model":
        """A copy rotated by rz degrees about Z (through the origin), then translated."""
        loc = cq.Location(cq.Vector(x, y, z)) * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), rz)
        m = Model(key or self.key, self.title, source=self.source, notes=dict(self.notes))
        m.parts = [Part(p.name, p.shape.moved(loc), p.material) for p in self.parts]
        return m

    def bbox(self) -> cq.BoundBox:
        return cq.Compound.makeCompound([p.shape for p in self.parts]).BoundingBox()

    def assembly(self, prefix: str = "") -> cq.Assembly:
        asm = cq.Assembly(name=self.key)
        seen: dict[str, int] = {self.key: 1}        # the root's own name is taken
        for p in self.parts:
            r, g, b, _, _ = MATERIALS[p.material]
            n = prefix + p.name
            seen[n] = seen.get(n, 0) + 1
            if seen[n] > 1:
                n = f"{n} {seen[n]}"
            asm.add(p.shape, name=n, color=cq.Color(r, g, b))
        return asm


PRINTED = ("holder", "nest", "rack")      # part names that are ours to print


def export(model: Model, folder: Path = EXPORTS, stl: bool = False) -> dict:
    """STEP (named, coloured parts), plus with stl=True an STL of just the printed part
    (the holder, not the vials standing in it); returns size facts."""
    folder.mkdir(parents=True, exist_ok=True)
    model.assembly().export(str(folder / f"{model.key}.step"))
    if stl:
        printed = [p.shape for p in model.parts if p.name in PRINTED]
        cq.exporters.export(cq.Compound.makeCompound(printed), str(folder / f"{model.key}.stl"),
                            tolerance=0.05, angularTolerance=0.2)
    bb = model.bbox()
    return {"title": model.title, "source": model.source, "parts": len(model.parts),
            "bbox_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)], **model.notes}


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


# ---- small geometry helpers ----------------------------------------------------------------

def cyl(d: float, h: float, x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z))


def tube(od: float, idia: float, h: float, x=0.0, y=0.0, z=0.0) -> cq.Workplane:
    return cq.Workplane("XY").circle(od / 2).circle(idia / 2).extrude(h).translate((x, y, z))


def rbox(w: float, d: float, h: float, r: float = 0.0, x=0.0, y=0.0, z=0.0, centred=True) -> cq.Workplane:
    """Box standing on z, rounded vertical edges; centred on (x, y) or with its corner there."""
    wp = cq.Workplane("XY").rect(w, d).extrude(h) if r <= 0 else \
        cq.Workplane("XY").sketch().rect(w, d).vertices().fillet(r).finalize().extrude(h)
    if not centred:
        wp = wp.translate((w / 2, d / 2, 0))
    return wp.translate((x, y, z))


def box(x0, y0, z0, x1, y1, z1) -> cq.Workplane:
    """Axis-aligned box between two corners."""
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
