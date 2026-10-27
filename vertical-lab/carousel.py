"""The lab's latest multi-doser, the **chain carousel v2** (powder-doser PR #185, issue #128), as animated meshes.

Thirteen powder modules (Sam's mounting plate with the lab's threaded auger) ride two vertical #35 chains; the station
on the bottom run docks one module, tilts it 30° and doses into a 20 mL vial on a 100 g load cell. Nothing here is
re-modelled: ``multidoser/{params,parts,layout,kinematics}.py`` are verbatim copies of powder-doser's
``cad/chain-carousel-v2/`` at ``1c135e0`` (PR #185's head, 2026-10-19), and ``layout.placements(State(...))`` gives
every one of the rig's 701 part instances for a chain shift, a station tilt, an actuator extension, an auger turn and a
solenoid tap, so the carousel indexes, docks, tilts and doses with its own kinematics. Its three reference STEPs (Sam's
plate and electronics carriage, the auger, the cap) are fetched at that commit and hash-checked.

Frame of the rig (its own): x along the augers (outlet end, where the vial is, at -x), y along the loop, z up from the
feet. Millimetres.
"""
from __future__ import annotations

import hashlib
import pickle
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pyvista as pv

HERE = Path(__file__).resolve().parent
MD = HERE / "multidoser"
sys.path.insert(0, str(MD))

SHA = "1c135e040a4eec28ddbbf5d121f05b0f592e6e05"       # powder-doser PR #185 head (claude/issue-128-20261013-2050)
REF_URL = "https://raw.githubusercontent.com/vertical-cloud-lab/powder-doser/{sha}/cad/chain-carousel-v2/reference/{name}"
REFERENCE = {
    "sam-oct13-mounting-plate-and-carriage.step": "dae4b71975c2fb5f2442df2ee457c811909d9ae343cb31b6850e905f8256b81a",
    "auger-threaded-storage.step": "3008ccbea47bae590934fcef5106a5a904a1ab069ed188480a760ff2e13ce6ff",
    "auger-cap-threaded.step": "2a2e8eda516330268003ad40faeb1b4339300c8f2d00e928ec4c8550259e6b82",
}
SKIP = {"vial"}                  # the animation's own vial (the arm carries it) stands in for the rig's
HIGHLIGHT = (0.10, 0.65, 0.35)   # powder-doser's render.py marks a module this green
HL_KEYS = {"carriage", "sam_mounting_plate", "auger_cap", "armature_tab"}
FINE = ("sprocket", "pinion")
COARSE = ("chain", "clevis", "stub", "loc_pin", "magnet", "insert", "eclip", "hall", "m3", "m5", "nut", "tnut", "bolt")
BUDGET = {"auger": 4000, "auger_cap": 1500, "chain_outer": 240, "chain_inner": 200, "chain_a1": 400}   # triangles per part


def fetch_reference() -> None:
    (MD / "reference").mkdir(exist_ok=True)
    for name, digest in REFERENCE.items():
        path = MD / "reference" / name
        if not path.exists():
            req = urllib.request.Request(REF_URL.format(sha=SHA, name=name), headers={"User-Agent": "Mozilla/5.0"})
            path.write_bytes(urllib.request.urlopen(req, timeout=300).read())
        d = hashlib.sha256(path.read_bytes()).hexdigest()
        if d != digest:
            raise RuntimeError(f"{name}: sha256 {d}, expected {digest} (powder-doser {SHA[:7]})")


fetch_reference()
import layout as CL      # noqa: E402  (the carousel's own layout, verbatim)
import params as CP      # noqa: E402

N_MODULES = CP.N_MODULES
MODULE_LINKS = CP.MODULE_LINKS
DIRN = CP.RUN_DIRECTION
DOCK_EXT = CP.DOCK_EXT
TILT = CL.frame_dose_tilt(CP.TILT_DOSE_WORLD)
VIAL_XY = np.array(CL.VIAL_XY, float)
VIAL_Z = float(CL.VIAL_Z)                          # vial base, in the rig's frame
VIAL_H, VIAL_R = 61.0, 14.0                        # the rig's 20 mL vial (28 mm across, 61 mm tall)


def _sources_hash() -> str:
    h = hashlib.sha256()
    for f in sorted(MD.glob("*.py")) + [Path(__file__)]:
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def _tess(shape, tol: float) -> pv.PolyData:
    verts, tris = shape.tessellate(tol, 0.35)
    if not tris:
        return pv.PolyData()
    pts = np.array([(v.x, v.y, v.z) for v in verts], float)
    faces = np.hstack([[3, *t] for t in tris])
    return pv.PolyData(pts, faces).clean()


def part_meshes() -> dict[str, pv.PolyData]:
    """Every unique part, tessellated once in its own frame and cached."""
    cache = HERE / ".cache" / f"carousel_{_sources_hash()}.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    cache.parent.mkdir(exist_ok=True)
    out = {}
    for key in sorted({p.key for p in CL.placements()} - SKIP):
        tol = 0.15 if key.startswith(FINE) else 0.8 if key.startswith(COARSE) else 0.4
        m = _tess(CL.shape(key), tol)
        n = BUDGET.get(key)
        if n and m.n_cells > n:              # threads and chain links: far more triangles than show at this scale
            m = m.triangulate().decimate_pro(1 - n / m.n_cells, preserve_topology=False).clean()
        out[key] = m
    cache.write_bytes(pickle.dumps(out))
    return out


def board_move(pl) -> np.ndarray:
    """The rig's electronics board stands beside its frame in powder-doser; on a tray it goes alongside the frame,
    turned 90°, so the rig and its board share the tray's depth."""
    pts = np.array([p.M[:3, 3] for p in pl if p.group == "elec"])
    c = (pts.min(0) + pts.max(0)) / 2
    target = np.array([170.0, -127.0 - 30.0 - 175.0, 0.0])
    Rz = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], float)
    M = np.eye(4)
    M[:3, :3] = Rz
    M[:3, 3] = target - Rz @ np.array([c[0], c[1], 0.0])
    return M


class Carousel:
    """The rig as a handful of actors (one per colour) in Scene group `group`; ``set(**state)`` re-poses all 701
    instances from ``layout.placements`` and rewrites the actors' points."""

    def __init__(self, sc, group: str, prefix: str = "md", highlight: int | None = None, **state):
        """`highlight`: a module (0-based) whose plate and cap are drawn green, as powder-doser's own movie marks one."""
        self.sc, self.group = sc, group
        self.parts = part_meshes()
        self.state = dict(shift=0.0, ext=0.0, tilt=0.0, spin=0.0, tap=0.0, magnet_on=False)
        self.state.update(state)
        pl = CL.placements(CL.State(**self.state))
        self.keys = [p.key for p in pl]
        self.board = board_move(pl)
        # one actor per (colour, the highlighted module or not, riding a carriage or fixed): the others' modules and
        # carriages can then be ghosted to show the docked one, which rides inside the loop, boxed in by the rest
        groups: dict[tuple, list[int]] = {}
        for i, p in enumerate(pl):
            if p.key in SKIP:
                continue
            hl = highlight is not None and p.module == highlight
            col = HIGHLIGHT if (hl and p.key in HL_KEYS) else p.color
            groups.setdefault((tuple(round(c, 3) for c in col), hl, p.module >= 0), []).append(i)
        self.actors = []
        self.others = []                 # actors of the modules and carriages other than the highlighted one
        for j, ((col, hl, rides), idx) in enumerate(sorted(groups.items())):
            if rides and not hl and highlight is not None:
                self.others.append(f"{prefix}/c{j}")
            polys, n0, slices = [], 0, []
            for i in idx:
                m = self.parts[pl[i].key]
                slices.append((i, n0, n0 + m.n_points))
                polys.append(m)
                n0 += m.n_points
            mesh = pv.merge(polys, merge_points=False) if len(polys) > 1 else polys[0].copy()
            name = f"{prefix}/c{j}"
            spec = 0.6 if col in ((0.62, 0.64, 0.67), (0.8, 0.82, 0.85)) else 0.3
            sc.add(name, mesh, col, group, specular=spec)
            self.actors.append((name, mesh, slices))
        self.set()

    def set(self, **kw):
        self.state.update(kw)
        pl = CL.placements(CL.State(**self.state))
        assert [p.key for p in pl] == self.keys, "the rig's instance list changed with its state"
        for name, mesh, slices in self.actors:
            pts = np.empty((mesh.n_points, 3))
            for i, a, b in slices:
                M = pl[i].M if pl[i].group != "elec" else self.board @ pl[i].M
                local = self.parts[pl[i].key].points
                pts[a:b] = local @ M[:3, :3].T + M[:3, 3]
            mesh.points = pts
            self.sc.set_mesh(name, mesh)

    # --------------------------------------------------------------------------------------- moves
    def ghost(self, a1: float):
        """An update(u) that fades the other modules and their carriages to opacity a1 (1: solid)."""
        a0 = {n: self.sc.base_alpha[n] for n in self.others}

        def up(u):
            for n in self.others:
                self.sc.base_alpha[n] = a0[n] + (a1 - a0[n]) * u
        return up

    def to(self, **target):
        """An update(u) that eases the state from now to `target` (numbers only; flags switch at the start)."""
        start = {k: self.state[k] for k in target}

        def up(u):
            kw = {}
            for k, v in target.items():
                kw[k] = v if isinstance(v, bool) else start[k] + (v - start[k]) * u
            self.set(**kw)
        return up

    def index_to(self, module: int):
        """Chain shift that brings `module` (0-based) to the station, the way the rig runs, from the current shift."""
        cur, n_links = self.state["shift"], CP.N_LINKS
        # carriage k sits at the station when MODULE_LINKS * k + shift = 0 (mod N_LINKS): shift 0 has carriage 1 there
        if DIRN < 0:
            return cur - (MODULE_LINKS * module + cur) % n_links
        return cur + (-MODULE_LINKS * module - cur) % n_links

    def exit_point(self) -> np.ndarray:
        """Auger outlet at the station, rig frame, at the current tilt."""
        return np.asarray(CL.exit_point(self.state["tilt"]), float)


def vial_seat() -> np.ndarray:
    """Base centre of the vial in its cup at the station, rig frame."""
    return np.array([VIAL_XY[0], VIAL_XY[1], VIAL_Z])


def funnel_top() -> float:
    return float(CL.FUNNEL_TOP)


if __name__ == "__main__":
    import time
    t0 = time.time()
    m = part_meshes()
    print(len(m), "parts,", sum(x.n_cells for x in m.values()), "triangles, %.1f s" % (time.time() - t0))
    pl = CL.placements()
    print(sum(m[p.key].n_cells for p in pl if p.key not in SKIP), "triangles placed")
    print("station module after index_to(5) from 0:", Carousel.index_to.__doc__ is not None)
