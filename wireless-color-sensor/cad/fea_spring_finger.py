"""CalculiX FEA of one PETG spring finger of the P20 socket.

Models a single finger (annular sector between two slits) as a cantilever
fixed at the solid base ring, with a prescribed radial deflection applied to
the inner edge of the free (top) end -- the interference during nozzle
insertion.  Returns both the peak von Mises stress (durability) and the
radial reaction force at the tip (the inward grip the finger provides, which
sets how much package weight the press-fit can hold).

This module is parametric and importable; ``fea_fit_study.py`` calls
``run_case`` to sweep every bore size in the test array.  Running this file
directly reproduces the original single conservative case (mid-bore 3.55 mm,
0.10 mm deflection).

Requires: gmsh (pip), calculix-ccx (apt).  Run: python fea_spring_finger.py
"""

from __future__ import annotations

import math
import pathlib
import subprocess
from dataclasses import dataclass

import gmsh

HERE = pathlib.Path(__file__).resolve().parent
WORK = HERE / "fea"

# socket geometry (matches cad_model.Params)
R_OUT = 6.0 / 2          # socket OD radius (mm)
H = 6.0                  # slit depth = finger length (mm)
SLIT_W = 0.5             # slit width (mm)
N_FINGERS = 3

# PETG, typical printed-part datasheet values
E_MPA = 2100.0
NU = 0.38
YIELD_MPA = 50.0
# Fatigue: printed PETG endurance ~50 % of yield for the released (R=0) cycle
# seen here (finger goes 0 -> delta -> 0 each pick/place).  Below this the
# finger should survive effectively unlimited insertion/removal cycles.
ENDURANCE_MPA = 25.0


@dataclass
class CaseResult:
    bore_id: float
    deflection: float        # radial interference per side (mm)
    vmax_mpa: float          # peak von Mises stress
    grip_force_n: float      # total inward radial force from all fingers


def build_mesh(msh_path: pathlib.Path, r_in: float) -> None:
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("finger")
    occ = gmsh.model.occ
    half_gap = math.degrees((SLIT_W / 2) / ((r_in + R_OUT) / 2))
    a0 = math.radians(half_gap)
    a1 = math.radians(360 / N_FINGERS - half_gap)
    outer = occ.addCylinder(0, 0, 0, 0, 0, H, R_OUT)
    inner = occ.addCylinder(0, 0, 0, 0, 0, H, r_in)
    ring, _ = occ.cut([(3, outer)], [(3, inner)])
    big = 4 * R_OUT
    box1 = occ.addBox(0, -big, -1, big, big, H + 2)
    occ.rotate([(3, box1)], 0, 0, 0, 0, 0, 1, a0)
    box2 = occ.addBox(0, 0, -1, big, big, H + 2)
    occ.rotate([(3, box2)], 0, 0, 0, 0, 0, 1, a1)
    sector, _ = occ.cut(ring, [(3, box1), (3, box2)])
    occ.synchronize()
    gmsh.option.setNumber("Mesh.MeshSizeMax", 0.35)
    gmsh.option.setNumber("Mesh.MeshSizeMin", 0.15)
    gmsh.option.setNumber("Mesh.ElementOrder", 2)
    gmsh.model.mesh.generate(3)
    gmsh.write(str(msh_path))
    gmsh.finalize()


def msh_to_ccx(msh_path: pathlib.Path, inp_path: pathlib.Path,
               r_in: float, deflection: float) -> None:
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
    tip = [t for t, c in nid.items()
           if c[2] > H - 0.75 and math.hypot(c[0], c[1]) < r_in + 0.10]
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
        # push the tip band radially outward along the finger bisector
        bis = math.radians(180 / N_FINGERS)
        ux, uy = deflection * math.cos(bis), deflection * math.sin(bis)
        f.write(f"*BOUNDARY\nTIP, 1, 1, {ux:.5f}\nTIP, 2, 2, {uy:.5f}\n")
        f.write("*EL PRINT, ELSET=EALL\nS\n")
        f.write("*NODE PRINT, NSET=TIP\nRF\n")
        f.write("*NODE FILE\nU\n*EL FILE\nS\n*END STEP\n")


def _parse_results(dat: str) -> tuple[float, float]:
    """Return (peak von Mises MPa, radial reaction magnitude N) from a .dat."""
    vmax = 0.0
    rf_sum = [0.0, 0.0, 0.0]
    section = None
    for line in dat.splitlines():
        low = line.lower()
        if "stress" in low:
            section = "S"
            continue
        if "force" in low:
            section = "RF"
            continue
        parts = line.split()
        if section == "S" and len(parts) == 8 and "E" in parts[-1]:
            try:
                sxx, syy, szz, sxy, sxz, syz = (float(v) for v in parts[2:8])
            except ValueError:
                continue
            vm = math.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 +
                                  (szz - sxx) ** 2) +
                           3 * (sxy ** 2 + sxz ** 2 + syz ** 2))
            vmax = max(vmax, vm)
        elif section == "RF" and len(parts) == 4:
            try:
                fx, fy, fz = (float(v) for v in parts[1:4])
            except ValueError:
                continue
            rf_sum[0] += fx
            rf_sum[1] += fy
            rf_sum[2] += fz
    # the reaction opposes the imposed outward push; its radial (xy) magnitude
    # is the inward grip this finger exerts on the nozzle.
    grip_one = math.hypot(rf_sum[0], rf_sum[1])
    return vmax, grip_one


def run_ccx(inp_path: pathlib.Path) -> tuple[float, float]:
    subprocess.run(["ccx", "-i", inp_path.stem], cwd=inp_path.parent,
                   check=True, capture_output=True, text=True)
    dat = inp_path.with_suffix(".dat").read_text()
    return _parse_results(dat)


def run_case(bore_id: float, deflection: float, r_in: float | None = None,
             tag: str | None = None) -> CaseResult:
    """Mesh + solve one finger at the given interference deflection.

    ``r_in`` defaults to the mid-depth bore radius for ``bore_id``; the inward
    grip force is reported for all ``N_FINGERS`` fingers combined.
    """
    WORK.mkdir(exist_ok=True)
    r_in = (bore_id / 2) if r_in is None else r_in
    tag = tag or f"{round(bore_id * 100):03d}"
    msh = WORK / f"finger_{tag}.msh"
    inp = WORK / f"finger_{tag}.inp"
    build_mesh(msh, r_in)
    msh_to_ccx(msh, inp, r_in, deflection)
    vmax, grip_one = run_ccx(inp)
    return CaseResult(bore_id, deflection, vmax, grip_one * N_FINGERS)


if __name__ == "__main__":
    res = run_case(3.55, 0.10)
    print(f"Finger: r_in={res.bore_id / 2:.2f} r_out={R_OUT:.2f} "
          f"H={H:.1f} mm, deflection={res.deflection:.2f} mm")
    print(f"Peak von Mises stress: {res.vmax_mpa:.1f} MPa "
          f"(PETG yield ~{YIELD_MPA:.0f} MPa, "
          f"safety factor {YIELD_MPA / res.vmax_mpa:.2f})")
    print(f"Total inward grip (3 fingers): {res.grip_force_n:.2f} N")
