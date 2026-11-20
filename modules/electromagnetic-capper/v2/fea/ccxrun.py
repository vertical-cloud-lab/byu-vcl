"""Minimal CadQuery-STEP -> gmsh tet10 -> CalculiX static linear-elastic runner.

run(step, name, fixed_box, load_box, disp=None, force=None, E=..., nu=...)
  fixed_box / load_box: (xmin,ymin,zmin,xmax,ymax,zmax) in mm; nodes inside are selected.
  disp: (ux,uy,uz) prescribed displacement on load nodes (None components left free)
  force: (Fx,Fy,Fz) total force spread evenly over load nodes
Returns dict with reaction force on load nodes (for disp) or max displacement (for force),
max von Mises stress and max principal strain (mm/mm), plus the node coords of the max.
Units: mm, N, MPa.
"""
import os, subprocess, re, numpy as np, gmsh

def mesh(step, msh, size=0.6, order=2):
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("m"); gmsh.model.occ.importShapes(step); gmsh.model.occ.synchronize()
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", size)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", size/4)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
    gmsh.option.setNumber("Mesh.ElementOrder", order)
    gmsh.option.setNumber("Mesh.SecondOrderLinear", 0)
    gmsh.model.mesh.generate(3)
    nt, xyz, _ = gmsh.model.mesh.getNodes()
    xyz = xyz.reshape(-1, 3)
    et, etags, enodes = gmsh.model.mesh.getElements(3)
    gmsh.finalize()
    i = list(et).index(11) if 11 in et else list(et).index(4)
    typ = et[i]; conn = np.array(enodes[i]).reshape(-1, 10 if typ == 11 else 4)
    return np.array(nt, dtype=int), xyz, conn, typ

def inbox(xyz, b):
    return np.where((xyz[:,0]>=b[0])&(xyz[:,1]>=b[1])&(xyz[:,2]>=b[2])&(xyz[:,0]<=b[3])&(xyz[:,1]<=b[4])&(xyz[:,2]<=b[5]))[0]

def run(step, name, fixed_box, load_box, disp=None, force=None, E=2300.0, nu=0.35, size=0.6, workdir="/tmp/cad/fea/runs", extra_fixed=None, cyl_axis=None, load_filter=None, fixed_filter=None, local_size=None):
    os.makedirs(workdir, exist_ok=True)
    tags, xyz, conn, typ = mesh(step, None, size=size)
    fi = inbox(xyz, fixed_box) if not callable(fixed_box) else np.where([fixed_box(p) for p in xyz])[0]
    li = inbox(xyz, load_box) if not callable(load_box) else np.where([load_box(p) for p in xyz])[0]
    fixed = tags[fi]; load = tags[li]
    assert len(fixed) and len(load), (len(fixed), len(load))
    inp = os.path.join(workdir, name + ".inp")
    with open(inp, "w") as f:
        f.write("*NODE\n")
        for t, p in zip(tags, xyz): f.write(f"{t},{p[0]:.6f},{p[1]:.6f},{p[2]:.6f}\n")
        # gmsh tet10 node order -> ccx C3D10: gmsh 0..9 = corners 0-3, edges (0-1,1-2,2-0,0-3,2-3,1-3); ccx wants (0-1,1-2,2-0,0-3,1-3,2-3)
        f.write("*ELEMENT, TYPE=C3D10, ELSET=EALL\n" if typ == 11 else "*ELEMENT, TYPE=C3D4, ELSET=EALL\n")
        for k, c in enumerate(conn, 1):
            if typ == 11: c = [c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],c[9],c[8]]
            f.write(f"{k}," + ",".join(str(int(v)) for v in c) + "\n")
        f.write("*NSET, NSET=NFIX\n" + "\n".join(str(int(t)) for t in fixed) + "\n")
        f.write("*NSET, NSET=NLOAD\n" + "\n".join(str(int(t)) for t in load) + "\n")
        if extra_fixed:
            for j,(b,dofs) in enumerate(extra_fixed):
                ns = tags[inbox(xyz, b)]
                f.write(f"*NSET, NSET=NFX{j}\n" + "\n".join(str(int(t)) for t in ns) + "\n")
        if cyl_axis is not None:
            a, b = cyl_axis
            f.write(f"*TRANSFORM, NSET=NLOAD, TYPE=C\n{a[0]},{a[1]},{a[2]},{b[0]},{b[1]},{b[2]}\n")
        f.write(f"*MATERIAL, NAME=MAT\n*ELASTIC\n{E},{nu}\n*SOLID SECTION, ELSET=EALL, MATERIAL=MAT\n")
        f.write("*STEP\n*STATIC\n*BOUNDARY\nNFIX,1,3,0.\n")
        if extra_fixed:
            for j,(b,dofs) in enumerate(extra_fixed):
                for d in dofs: f.write(f"NFX{j},{d},{d},0.\n")
        if disp is not None:
            for d, v in enumerate(disp, 1):
                if v is not None: f.write(f"NLOAD,{d},{d},{v}\n")
        if force is not None:
            f.write("*CLOAD\n")
            n = len(load)
            for d, v in enumerate(force, 1):
                if v: 
                    for t in load: f.write(f"{int(t)},{d},{v/n:.8e}\n")
        f.write("*NODE PRINT, NSET=NLOAD, TOTALS=ONLY, GLOBAL=YES\nRF\n*NODE FILE\nU\n*EL FILE\nS,E\n*END STEP\n")
    r = subprocess.run(["ccx", "-i", name], cwd=workdir, capture_output=True, text=True)
    if "Job finished" not in r.stdout:
        raise RuntimeError(r.stdout[-2000:] + r.stderr[-2000:])
    return parse(workdir, name, xyz, tags) | {"n_nodes": len(tags), "n_elems": len(conn), "n_fixed": len(fixed), "n_load": len(load)}

def parse(workdir, name, xyz, tags):
    dat = open(os.path.join(workdir, name + ".dat")).read()
    rf = None
    m = re.findall(r"total force.*?\n\s*\n\s*([-\d.E+]+)\s+([-\d.E+]+)\s+([-\d.E+]+)", dat, re.S)
    if m: rf = [float(v) for v in m[-1]]
    frd = open(os.path.join(workdir, name + ".frd")).read().splitlines()
    blocks = {}; cur = None
    for line in frd:
        if line.startswith(" -4"):
            cur = line.split()[1]; blocks[cur] = {}
        elif line.startswith(" -1") and cur:
            nid = int(line[3:13]); vals = [float(line[13+12*i:25+12*i]) for i in range((len(line)-13)//12)]
            blocks[cur][nid] = vals
        elif line.startswith(" -3"): cur = None
    U = blocks.get("DISP", {}); S = blocks.get("STRESS", {}); Ee = blocks.get("TOSTRAIN", {})
    pos = dict(zip(tags, xyz))
    def vm(s):
        sx,sy,sz,sxy,syz,szx = s[:6]
        return np.sqrt(0.5*((sx-sy)**2+(sy-sz)**2+(sz-sx)**2)+3*(sxy**2+syz**2+szx**2))
    def p1(e):
        ex,ey,ez,exy,eyz,ezx = e[:6]
        T = np.array([[ex,exy,ezx],[exy,ey,eyz],[ezx,eyz,ez]])  # ccx writes tensor shear strains
        return np.linalg.eigvalsh(T)[-1]
    def s1(s):
        sx,sy,sz,sxy,syz,szx = s[:6]
        return np.linalg.eigvalsh(np.array([[sx,sxy,szx],[sxy,sy,syz],[szx,syz,sz]]))[-1]
    vms = {k: vm(v) for k, v in S.items()}
    kmax = max(vms, key=vms.get)
    e1 = {k: p1(v) for k, v in Ee.items()}; ke = max(e1, key=e1.get)
    sp = {k: s1(v) for k, v in S.items()}; ks = max(sp, key=sp.get)
    umax = max(np.linalg.norm(v[:3]) for v in U.values())
    # robust: 99.5th percentile too (singular corners)
    vmv = np.array(list(vms.values())); e1v = np.array(list(e1.values()))
    return {"RF": rf, "vm_max": float(vms[kmax]), "vm_max_at": pos[kmax].round(2).tolist(),
            "vm_p995": float(np.percentile(vmv, 99.5)), "e1_max": float(e1[ke]), "e1_max_at": pos[ke].round(2).tolist(),
            "e1_p995": float(np.percentile(e1v, 99.5)), "s1_max": float(sp[ks]), "s1_max_at": pos[ks].round(2).tolist(), "u_max": float(umax)}
