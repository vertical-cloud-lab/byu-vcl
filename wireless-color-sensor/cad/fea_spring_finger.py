"""Lightweight CalculiX FEA of one PETG spring finger of the P20 socket.

Models a single finger (annular sector between two slits) as a cantilever
fixed at the solid base ring, with a prescribed 0.10 mm radial deflection
applied to the inner edge of the free (top) end — the worst-case interference
during nozzle insertion (design interference 0.05-0.15 mm shared across the
bore, so 0.10 mm per finger is conservative).

Checks that peak von Mises stress stays below PETG yield (~50 MPa) so the
fingers remain elastic over hundreds of insertion/removal cycles.

Requires: gmsh (pip), calculix-ccx (apt).  Run: python fea_spring_finger.py
"""

from __future__ import annotations

import math
import pathlib
import subprocess

import gmsh

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / "fea"

# geometry (matches cad_model.Params, mid-bore 3.55 mm)
R_IN = 3.55 / 2          # socket bore radius at mid-depth (mm)
R_OUT = 6.0 / 2          # socket OD radius (mm)
H = 6.0                  # slit depth = finger length (mm)
SLIT_W = 0.5             # slit width (mm)
N_FINGERS = 3

# PETG, typical datasheet values
E_MPA = 2100.0
NU = 0.38
YIELD_MPA = 50.0

DEFLECTION = 0.10        # prescribed radial deflection at finger tip (mm)


def build_mesh(msh_path: pathlib.Path) -> None:
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("finger")
    occ = gmsh.model.occ
    # annular sector: 120 deg minus the slit widths on each side
    half_gap = math.degrees((SLIT_W / 2) / ((R_IN + R_OUT) / 2))
    a0 = math.radians(half_gap)
    a1 = math.radians(360 / N_FINGERS - half_gap)
    outer = occ.addCylinder(0, 0, 0, 0, 0, H, R_OUT)
    inner = occ.addCylinder(0, 0, 0, 0, 0, H, R_IN)
    ring, _ = occ.cut([(3, outer)], [(3, inner)])
    # wedge to keep only the sector a0..a1
    pts = [occ.addPoint(0, 0, -1)]
    wedge = occ.addWedge(0, 0, 0, 1, 1, 1)  # placeholder, replaced below
    occ.remove([(3, wedge)], recursive=True)
    # build cutting box approach: rotate two half-space boxes
    big = 4 * R_OUT
    box1 = occ.addBox(0, -big, -1, big, big, H + 2)       # y < 0 half (x>0)
    occ.rotate([(3, box1)], 0, 0, 0, 0, 0, 1, a0)
    box2 = occ.addBox(0, 0, -1, big, big, H + 2)          # y > 0 half (x>0)
    occ.rotate([(3, box2)], 0, 0, 0, 0, 0, 1, a1)
    sector, _ = occ.cut(ring, [(3, box1), (3, box2)])
    occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", 0.35)
    gmsh.option.setNumber("Mesh.MeshSizeMin", 0.15)
    gmsh.option.setNumber("Mesh.ElementOrder", 2)
    gmsh.model.mesh.generate(3)
    gmsh.write(str(msh_path))
    gmsh.finalize()


def msh_to_ccx(msh_path: pathlib.Path, inp_path: pathlib.Path) -> None:
    """Convert gmsh .msh (v4 ASCII) tet10 mesh to a CalculiX input deck."""
    import numpy as np

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.open(str(msh_path))
    tags, coords, _ = gmsh.model.mesh.getNodes()
    coords = np.array(coords).reshape(-1, 3)
    nid = {int(t): coords[i] for i, t in enumerate(tags)}
    etypes, etags, enodes = gmsh.model.mesh.getElements(dim=3)
    gmsh.finalize()

    tet10 = None
    for et, tg, nd in zip(etypes, etags, enodes):
        if et == 11:  # 10-node tet
            tet10 = (tg, np.array(nd, dtype=int).reshape(-1, 10))
    assert tet10 is not None, "no tet10 elements"
    etags10, conn = tet10

    # gmsh tet10 -> CalculiX C3D10 node order (swap nodes 9 & 10)
    conn_ccx = conn[:, [0, 1, 2, 3, 4, 5, 6, 7, 9, 8]]

    base = [t for t, c in nid.items() if abs(c[2]) < 1e-6]
    # tip load band: inner surface nodes near the top
    tip = [t for t, c in nid.items()
           if c[2] > H - 0.75 and math.hypot(c[0], c[1]) < R_IN + 0.10]
    assert base and tip

    with open(inp_path, "w") as f:
        f.write("*NODE, NSET=NALL\n")
        for t in sorted(nid):
            x, y, z = nid[t]
            f.write(f"{t}, {x:.6f}, {y:.6f}, {z:.6f}\n")
        f.write("*ELEMENT, TYPE=C3D10, ELSET=EALL\n")
        for et, c in zip(etags10, conn_ccx):
            f.write(f"{int(et)}, " + ", ".join(str(int(n)) for n in c) + "\n")
        for name, nodes in (("BASE", base), ("TIP", tip)):
            f.write(f"*NSET, NSET={name}\n")
            for i in range(0, len(nodes), 10):
                f.write(", ".join(str(n) for n in nodes[i:i + 10]) + ",\n")
        f.write(f"*MATERIAL, NAME=PETG\n*ELASTIC\n{E_MPA}, {NU}\n")
        f.write("*SOLID SECTION, ELSET=EALL, MATERIAL=PETG\n")
        f.write("*BOUNDARY\nBASE, 1, 3, 0.0\n")
        f.write("*STEP\n*STATIC\n")
        # push the tip band radially outward: the finger is centered around
        # the bisector angle; apply displacement along that direction
        bis = math.radians(180 / N_FINGERS)
        ux, uy = DEFLECTION * math.cos(bis), DEFLECTION * math.sin(bis)
        f.write(f"*BOUNDARY\nTIP, 1, 1, {ux:.5f}\nTIP, 2, 2, {uy:.5f}\n")
        f.write("*EL PRINT, ELSET=EALL\nS\n")
        f.write("*NODE FILE\nU\n*EL FILE\nS\n*END STEP\n")


def run_ccx(inp_path: pathlib.Path) -> float:
    subprocess.run(["ccx", "-i", inp_path.stem], cwd=inp_path.parent,
                   check=True, capture_output=True, text=True)
    dat = inp_path.with_suffix(".dat").read_text()
    vmax = 0.0
    for line in dat.splitlines():
        parts = line.split()
        if len(parts) == 8 and "E" in parts[-1]:
            try:
                sxx, syy, szz, sxy, sxz, syz = (float(v) for v in parts[2:8])
            except ValueError:
                continue
            vm = math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 +
                                  (szz - sxx) ** 2) +
                           3 * (sxy ** 2 + sxz ** 2 + syz ** 2))
            vmax = max(vmax, vm)
    return vmax


if __name__ == "__main__":
    WORK.mkdir(exist_ok=True)
    msh = WORK / "finger.msh"
    inp = WORK / "finger.inp"
    build_mesh(msh)
    msh_to_ccx(msh, inp)
    vmax = run_ccx(inp)
    print(f"Finger: r_in={R_IN:.2f} r_out={R_OUT:.2f} H={H:.1f} mm, "
          f"deflection={DEFLECTION:.2f} mm")
    print(f"Peak von Mises stress: {vmax:.1f} MPa "
          f"(PETG yield ~{YIELD_MPA:.0f} MPa, "
          f"safety factor {YIELD_MPA / vmax:.2f})")
