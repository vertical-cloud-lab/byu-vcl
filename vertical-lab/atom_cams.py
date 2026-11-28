"""The rePowder's melt-chamber and melt-stream cameras (DAL PR 189) on this repo's model, for PR #353 (#303).

Three Raspberry Pi 5 camera units, each with its own small display beside the operator, as designed in
digital-alloy-lab PR 189 (``atomizer-viewport-cameras/``, README "Design"; Onshape document "rePowder viewport cameras
(byu-vcl #198)"):

- **front**: a 12-sided socket pushed onto AMAZEMET's LED illuminator cover on the chamber's round view port, an HQ
  Camera (M12) with a 16 mm M12 lens and a Camera Module 3 Wide side by side, a Pi 5, and a 5 in HDMI display (Elecrow,
  800 x 480) facing out along the port's axis, ~20 deg up to a standing operator. HDMI because both MIPI ports carry
  cameras.
- **left**: a split collar on the door's sight-glass ring, a Camera Module 3 Wide on its axis, a Pi 5 and a 5 in Touch
  Display 2. It rides on the door (its group's parent is the door's), so it swings when the door opens.
- **top**: a switchable magnetic base and 5/8 in post on the blue frame's top, a printed hub on a detent collar (dimples
  "working" and "parked", 90 deg apart), a 2020 extrusion out over the furnace, a camera pod (HQ Camera, 16 mm C lens,
  hot mirror, variable ND) on the ~66 deg line through the lid window to the melt, and a display box (2.8 in DSI)
  tilted 30 deg down at the arm's tip.

Every part is DAL's own geometry: the Onshape Part Studio's STEP export (``exports/onshape_partstudio.step``, read
with its part names: the printed parts, the bought parts as Onshape drew them, and the machine parts round the
windows), tessellated once by ``python3 atom_cams.py --extract`` into ``out/atom/cams_dal189_parts.npz`` so that the
clip does not need the DAL clone. The STEP is in the Onshape model's frame, which shares this model's axes and origin
(x right, y back, z up, the furnace axis at x = y = 0; the blue frame's numbers are identical). Each unit is then moved
as DAL's ``cad/units.py`` moved it onto a model whose windows differ:

- front: rigidly, from the Onshape port (x -15, z 1035 on the face, axis 20 deg up, not turned) onto this model's
  ``M.VIEWPORT``/``M.VIEWPORT_N`` (21.6 deg up, 8.5 deg to the left): the minimal rotation between the axes about the
  point where each leaves the face. The model's own port flange and glass are hidden; DAL's port nut, glass, LED cover
  and cable pod are drawn in their place (DAL's renders did the same).
- left: (-10, -65, +45) mm, units.py's move from the Onshape sight glass (y +20, z 1015, ring 30 proud) onto this
  model's (y -45, z 1060, ring 22 proud), then parented to the door. DAL's ring is drawn over the model's.
- top: not moved. The Onshape arm aims at (0, 0, 1240), the crucible datum (``M.Z_CR`` 1219.2) plus ~20 mm of melt,
  which is DAL's aim on this model too.

The lid window: #327's model had a 26 x 84 slot on the lid's left facet; DAL measured a 60 x 64 mm glass-ceramic
window in a polished 8-screw plate on the lid's FRONT facet. The frames favour DAL, and so does the lid's swing (hinged
at the back, #327's lid ran into the blue cabinet), so the model's lid was turned 90 deg in commit e3b1428 (hinge on
the left, DAL's window and plate on the front facet, at this top camera's line). ``add_units`` therefore uses the
model's lid and window as they are; ``window=True`` (DAL's pane re-fitted onto the old lid, ``lid_mesh``) is kept only
for the old model and is off by default.

API (importable without side effects; nothing is read until called):

    import atom_base as AB, atom_cams as CAMS
    sc, ma, mb = AB.build(...)
    CAMS.add_units(sc)                 # all three units, the lid window; the top arm in its working dimple
    CAMS.set_top_arm(sc, 1.0)          # 0 = working, 1 = parked (90 deg about the post, DAL's park angle)
    CAMS.unit_poses()                  # each camera's pose (model frame) and field of view
    fd = CAMS.Feeds(sc)                # the four cameras rendered live, onto the displays and as panels
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NPZ = HERE / "out" / "atom" / "cams_dal189_parts.npz"
DAL_REPO = Path("/tmp/dal")              # a clone of vertical-cloud-lab/digital-alloy-lab with PR 189 fetched as "pr189"
DAL_REF = "pr189"                        # PR 189's head when read: c4827e9
DAL_STEP = "atomizer-viewport-cameras/exports/onshape_partstudio.step"

# ------------------------------------------------------------------------------------------- DAL's numbers
DAL_PORT = np.array([-15.0, -120.0, 1035.0])          # Onshape: where the front port's axis leaves the chamber face
DAL_PORT_TILT = 20.0                                   # deg up, not turned (placement.json)
LEFT_MOVE = np.array([-10.0, -65.0, 45.0])            # units.py: Onshape sight glass -> the CadQuery model's (= ours)
POST_XY = np.array([-90.0, 195.0])                     # the 5/8 in post's axis (the STEP's post rod, its bbox centre)
PARK_DEG = 90.0                                        # viewport_mounts.fs: park = +90 deg about the post (z up)
DAL_WINDOW_C = np.array([0.0, -93.9, 1455.0])          # Onshape lid window centre (placement.json)
AIM = np.array([0.0, 0.0, 1240.0])                     # the top camera's aim: crucible datum + ~20 mm of melt (README)
# fields of view. HQ Camera (IMX477, 6.287 x 4.712 mm active) behind a 16 mm lens: 2 atan(3.14 / 16) = 22.2 deg by
# 16.8 deg. Camera Module 3 Wide: 102 x 67 deg (Raspberry Pi's product brief).
FOV = {"hq16": (22.2, 16.8), "wide": (102.0, 67.0)}

GROUPS = dict(front="cams:front", left="cams:left", post="cams:top_post", arm="cams:top_arm", window="cams:lid_window")

# ------------------------------------------------------------------------------------------- colours
PETG = (0.10, 0.10, 0.11)        # black PETG: front and left units (DAL README "Printed part" table)
ASA = (0.20, 0.20, 0.21)         # ASA above the furnace: the top pod and display box
PCB = (0.10, 0.40, 0.20)
COOLER = (0.52, 0.53, 0.56)
BEZEL = (0.05, 0.05, 0.06)
SCREEN = (0.02, 0.03, 0.05)
LENS = (0.07, 0.07, 0.08)
ALU = (0.78, 0.79, 0.81)
STEEL = (0.70, 0.71, 0.73)
POLISH = (0.84, 0.85, 0.87)
LEDCOV = (0.26, 0.27, 0.29)
GLASS = (0.72, 0.86, 0.96)
CERAMIC = (0.30, 0.24, 0.20)     # the lid's glass-ceramic pane: tinted brown (frames: 58wJ 58:06)


def _git_show(path: str, dal: Path = DAL_REPO, ref: str = DAL_REF) -> bytes:
    return subprocess.run(["git", "-C", str(dal), "show", f"{ref}:{path}"], check=True, capture_output=True).stdout


def extract(dal: Path = DAL_REPO, ref: str = DAL_REF, out: Path = NPZ, tol: float = 0.25) -> Path:
    """Read DAL PR 189's STEP with Onshape's part names (as DAL's cad/check.py does) and save each solid's
    tessellation (Onshape frame, mm) to `out`. Needs the DAL clone; the clip only needs the .npz."""
    import tempfile

    import cadquery as cq
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TDF import TDF_Label, TDF_LabelSequence
    from OCP.TDocStd import TDocStd_Document
    from OCP.TopLoc import TopLoc_Location
    from OCP.XCAFDoc import XCAFDoc_DocumentTool

    with tempfile.TemporaryDirectory() as td:
        step = Path(td) / "partstudio.step"
        step.write_bytes(_git_show(DAL_STEP, dal, ref))
        doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
        reader = STEPCAFControl_Reader()
        reader.SetNameMode(True)
        if reader.ReadFile(str(step)) != IFSelect_RetDone:
            raise SystemExit("cannot read the STEP")
        reader.Transfer(doc)
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    found = []

    def name_of(label) -> str:
        attr = TDataStd_Name()
        return attr.Get().ToExtString() if label.FindAttribute(TDataStd_Name.GetID_s(), attr) else ""

    def walk(label, loc):
        if not tool.IsAssembly_s(label):
            found.append((name_of(label), cq.Shape.cast(tool.GetShape_s(label).Moved(loc))))
            return
        comps = TDF_LabelSequence()
        tool.GetComponents_s(label, comps)
        for i in range(1, comps.Length() + 1):
            c = comps.Value(i)
            ref_ = TDF_Label()
            tool.GetReferredShape_s(c, ref_)
            cl = loc.Multiplied(tool.GetLocation_s(c))
            if tool.IsAssembly_s(ref_):
                walk(ref_, cl)
            else:
                found.append((name_of(c) or name_of(ref_), cq.Shape.cast(tool.GetShape_s(ref_).Moved(cl))))

    free = TDF_LabelSequence()
    tool.GetFreeShapes(free)
    for i in range(1, free.Length() + 1):
        walk(free.Value(i), TopLoc_Location())
    keys, arrays = [], {}
    for nm, sh in found:
        vs, fs = sh.tessellate(tol, 0.35)
        k, j = nm, 1
        while k in keys:
            j += 1
            k = f"{nm} #{j}"
        arrays[f"v{len(keys)}"] = np.array([(p.x, p.y, p.z) for p in vs], np.float32)
        arrays[f"f{len(keys)}"] = np.array(fs, np.int32)
        keys.append(k)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, names=np.array(keys), **arrays)
    return out


_PARTS: dict | None = None


def dal_parts() -> dict:
    """{name: pv.PolyData} in the Onshape (= model) frame, from the cached tessellation."""
    global _PARTS
    if _PARTS is None:
        import pyvista as pv
        z = np.load(NPZ)
        _PARTS = {}
        for i, nm in enumerate(z["names"]):
            v, f = z[f"v{i}"].astype(float), z[f"f{i}"]
            faces = np.hstack([np.full((len(f), 1), 3, np.int64), f.astype(np.int64)]).ravel()
            _PARTS[str(nm)] = pv.PolyData(v, faces).clean()
    return _PARTS


def _centre(m) -> np.ndarray:
    b = m.bounds
    return np.array([(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2])


def unit_of(name: str, m) -> str | None:
    """Which unit a STEP part belongs to (by its name and where it is), or None for the Onshape model's rough machine
    parts, which this model replaces (the frame, chamber, door, furnace body and lid, the stack, the open-lid ghosts)."""
    c = _centre(m)
    b = m.bounds
    if name.startswith(("(machine) blue frame", "(machine) atomization chamber", "(machine) chamber door",
                        "(machine) furnace body", "(machine) ultrasonic stack", "(machine) lid window, open",
                        "(machine) furnace lid, open")):
        return None
    if name.startswith("(machine) furnace lid"):
        return "window" if b[1] - b[0] < 130 else None          # the window's plate, not the rough lid
    if name.startswith("(machine) lid window"):
        return "window"
    if c[2] > 1600:
        return "post" if name.startswith(("(bought) switchable magnetic base", "(bought) post rod",
                                          "TOP detent collar")) else "arm"
    if c[0] < -130 and c[2] > 940:
        return "left"
    if c[1] < -130 and c[2] > 900:
        return "front"
    return None


def colour_of(name: str):
    n = name.lower()
    if "screen" in n:
        return SCREEN, 1.0
    if "display" in n:
        return BEZEL, 1.0
    if "glass" in n and "ring" not in n:
        return GLASS, 0.35
    if "lid window" in n:
        return CERAMIC, 0.55
    if "furnace lid" in n:                     # the window's polished plate
        return POLISH, 1.0
    if "led cover" in n:
        return LEDCOV, 1.0
    if "port nut" in n or "ring" in n:
        return POLISH, 1.0
    if "cooler" in n:
        return COOLER, 1.0
    if "raspberry pi 5" in n or "camera module" in n or ("hq camera" in n and "mount" not in n):
        return PCB, 1.0
    if "lens" in n:
        return LENS, 1.0
    if "extrusion" in n:
        return ALU, 1.0
    if "post rod" in n:
        return STEEL, 1.0
    if "magnetic base" in n:
        return (0.16, 0.16, 0.17), 1.0
    if n.startswith("top"):
        return ASA, 1.0
    return PETG, 1.0


# ------------------------------------------------------------------------------------------- the moves
def _M():
    sys.path.insert(0, str(HERE))
    import repowder.model as M      # noqa: E402
    return M


def _rot_between(a, b) -> np.ndarray:
    a = np.asarray(a, float) / np.linalg.norm(a)
    b = np.asarray(b, float) / np.linalg.norm(b)
    v, c = np.cross(a, b), float(np.dot(a, b))
    if np.linalg.norm(v) < 1e-12:
        return np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * (1.0 / (1.0 + c))


def _T(p) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = p
    return m


def port_axis() -> tuple[np.ndarray, np.ndarray]:
    """This model's front port: (where its axis leaves the chamber face, the outward axis)."""
    M = _M()
    n = np.asarray(M.VIEWPORT_N, float)
    n = n / np.linalg.norm(n)
    t = (M.CH_Y[0] - M.VIEWPORT[1]) / n[1]
    return np.asarray(M.VIEWPORT, float) + t * n, n


def front_move() -> np.ndarray:
    """4x4: DAL's front unit from the Onshape port onto this model's (rigid, about where the axes leave the face)."""
    a_dal = np.array([0.0, -math.cos(math.radians(DAL_PORT_TILT)), math.sin(math.radians(DAL_PORT_TILT))])
    p, n = port_axis()
    Rm = np.eye(4)
    Rm[:3, :3] = _rot_between(a_dal, n)
    return _T(p) @ Rm @ _T(-DAL_PORT)


def left_move() -> np.ndarray:
    return _T(LEFT_MOVE)


def front_facet() -> tuple[np.ndarray, np.ndarray]:
    """This model's lid front facet: (a point on it, its outward normal), shut."""
    M = _M()
    o, n = M.facet_plane(M.lid_params(), "front", 0.5)
    return np.asarray(o, float), np.asarray(n, float) / np.linalg.norm(n)


def window_move(parts: dict | None = None) -> np.ndarray:
    """4x4: DAL's lid-window plate and pane from the Onshape lid's front facet (~50 deg) onto this model's (53 deg),
    centred where the top camera's line (Onshape pod -> AIM through DAL's window centre) crosses this facet, the
    plate's back on the facet."""
    parts = parts or dal_parts()
    plate = next(m for k, m in parts.items() if k.startswith("(machine) furnace lid") and m.bounds[1] - m.bounds[0] < 130)
    m = plate.compute_normals(cell_normals=True, point_normals=False)
    cn = m.cell_data["Normals"]
    area = m.compute_cell_sizes(length=False, volume=False).cell_data["Area"]
    sel = (cn[:, 1] < -0.4) & (cn[:, 2] > 0.4)
    n_dal = (cn[sel] * area[sel, None]).sum(0)
    n_dal /= np.linalg.norm(n_dal)
    o_f, n_f = front_facet()
    # the line: from DAL's window centre towards the aim, extended back to this facet
    d = AIM - DAL_WINDOW_C
    d /= np.linalg.norm(d)
    t = float(np.dot(o_f - DAL_WINDOW_C, n_f) / np.dot(d, n_f))
    hit = DAL_WINDOW_C + t * d
    Rm = np.eye(4)
    Rm[:3, :3] = _rot_between(n_dal, n_f)
    pts = (Rm[:3, :3] @ (plate.points - DAL_WINDOW_C).T).T
    back = float(np.min(pts @ n_f))             # the plate's back face, along the normal, from the centre
    return _T(hit - n_f * back) @ Rm @ _T(-DAL_WINDOW_C), dict(n_dal=n_dal, n_model=n_f, centre=hit, back=back)


def window_pose() -> dict:
    """The lid window as placed: centre (on the facet), normal, and the 60 x 64 opening's in-plane axes."""
    Mw, info = window_move()
    n = info["n_model"]
    xa = np.array([1.0, 0.0, 0.0])
    ya = np.cross(n, xa)
    return dict(centre=info["centre"], normal=n, x=xa, y=ya, w=60.0, h=64.0, matrix=Mw)


def top_arm_matrix(v: float) -> np.ndarray:
    """The top arm (hub and what it carries) at v of its swing: 0 = working dimple, 1 = parked (+90 deg about the post,
    seen from above anticlockwise: the arm then lies over the blue frame's top, clear of the lid and the furnace)."""
    a = math.radians(PARK_DEG * float(v))
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    m[:2, :2] = [[c, -s], [s, c]]
    m[:2, 3] = POST_XY - m[:2, :2] @ POST_XY
    return m


# ------------------------------------------------------------------------------------------- the lid, re-cut
def lid_mesh():
    """This model's lid shell (repowder/model.py hood_parts, the same calls) with DAL's 60 x 64 window opening cut in
    its front facet instead of the left-facet slot: for this scene only."""
    import cadquery as cq
    M = _M()
    p = M.lid_params()
    r, r1, h1, h2, ext, w = p["r"], p["r1"], p["h1"], p["h2"], p["ext"], p["wall"]
    taper = math.degrees(math.atan2(r - r1, h2))
    outer = M._prism(r, ext, M.BODY_TOP, h1).fuse(M._prism(r, ext, M.BODY_TOP + h1, h2, taper=taper))
    inner = M._prism(r - w, ext - w, M.BODY_TOP - 1, h1 + 1).fuse(
        M._prism(r - w, ext - w, M.BODY_TOP + h1, h2 - w, taper=taper))
    hood = outer.cut(inner).clean()
    wp = window_pose()
    c, n = wp["centre"], wp["normal"]
    pl = cq.Plane(origin=cq.Vector(*(c - n * 12.0)), xDir=cq.Vector(1, 0, 0), normal=cq.Vector(*n))
    hood = hood.cut(cq.Workplane(pl).rect(wp["w"], wp["h"]).extrude(24.0).val())
    return M.tess(hood, 0.4) if hasattr(M, "tess") else None


# ------------------------------------------------------------------------------------------- the cameras
# lens part (its STEP name and the unit), the field of view, the display it feeds and the Pi
CAMERAS = {
    "top_hq": dict(unit="arm", lens="(bought) lens", near=(0.0, -204.0, 1707.0), fov="hq16",
                   label="TOP: HQ + 16 mm, through the lid window",
                   pi="top unit's Pi 5 (CSI0)", display="top 2.8 in DSI (Waveshare, 480 x 640)"),
    "front_hq": dict(unit="front", lens="(bought) lens", near=(-30.0, -178.0, 1056.0), fov="hq16",
                     label="FRONT: HQ + 16 mm M12",
                     pi="front unit's Pi 5 (CSI0)", display="front 5 in HDMI (Elecrow, 800 x 480), left half"),
    "front_wide": dict(unit="front", lens="(bought) Camera Module 3 lens", near=(3.5, -186.0, 1058.0), fov="wide",
                       label="FRONT: Camera Module 3 Wide",
                       pi="front unit's Pi 5 (CSI1)", display="front 5 in HDMI, right half"),
    "left_wide": dict(unit="left", lens="(bought) Camera Module 3 lens", near=(-158.0, 20.0, 1015.0), fov="wide",
                      label="LEFT: Camera Module 3 Wide, side on",
                      pi="left unit's Pi 5 (CSI0)", display="left 5 in Touch Display 2 (DSI)"),
}


def _lens_part(parts: dict, cam: dict) -> tuple[str, object]:
    """The STEP part that is this camera's lens: the one of that name nearest the given Onshape point."""
    best = None
    for k, m in parts.items():
        if not k.startswith(cam["lens"]):
            continue
        d = float(np.linalg.norm(_centre(m) - np.asarray(cam["near"])))
        if best is None or d < best[0]:
            best = (d, k, m)
    return best[1], best[2]


def _camera_onshape(key: str, parts: dict | None = None) -> dict:
    """A camera's lens front and view direction in the Onshape frame (before the unit's move)."""
    parts = parts or dal_parts()
    cam = CAMERAS[key]
    k, m = _lens_part(parts, cam)
    near = [mm for kk, mm in parts.items() if kk.startswith(cam["lens"])
            and np.linalg.norm(_centre(mm) - _centre(m)) < 15.0]           # a lens drawn as two solids: both
    pts = np.vstack([np.asarray(mm.points) for mm in near])
    c = np.asarray(m.points).mean(0)
    if key == "top_hq":
        d = AIM - c
    elif key.startswith("front"):
        d = -np.array([0.0, -math.cos(math.radians(DAL_PORT_TILT)), math.sin(math.radians(DAL_PORT_TILT))])
    else:
        d = np.array([1.0, 0.0, 0.0])
    d = d / np.linalg.norm(d)
    front = c + d * (float(np.max((pts - c) @ d)) + 0.5)       # just in front of the lens's front face
    return dict(part=k, eye=front, dir=d)


def _unit_matrix(unit: str, v_top: float = 0.0, door: float = 0.0) -> np.ndarray:
    M = _M()
    if unit == "front":
        return front_move()
    if unit == "left":
        return M.joint_matrix("door", door) @ left_move()
    if unit == "arm":
        return top_arm_matrix(v_top)
    return np.eye(4)


def unit_poses(v_top: float = 0.0, door: float = 0.0) -> dict:
    """Each camera's pose and field of view in the model frame: {name: dict(eye, dir, up, hfov, vfov, unit, pi,
    display, label, matrix (4x4: camera frame, z = the view direction))}, with the top arm at v_top (0 working,
    1 parked) and the door at `door` (0..1 of its swing)."""
    out = {}
    for key, cam in CAMERAS.items():
        c = _camera_onshape(key)
        Mx = _unit_matrix(cam["unit"], v_top, door)
        eye = (Mx @ np.r_[c["eye"], 1.0])[:3]
        d = Mx[:3, :3] @ c["dir"]
        up0 = np.array([0.0, 0.0, 1.0])
        x = np.cross(d, up0)
        x /= np.linalg.norm(x)
        up = np.cross(x, d)
        F = np.eye(4)
        F[:3, 0], F[:3, 1], F[:3, 2], F[:3, 3] = x, -up, d, eye
        hf, vf = FOV[cam["fov"]]
        out[key] = dict(eye=eye, dir=d, up=up, hfov=hf, vfov=vf, unit=cam["unit"], pi=cam["pi"],
                        display=cam["display"], label=cam["label"], matrix=F)
    return out


PORT_GLASS_R = 31.5                  # the front port's glass, Ø63 (DAL measurements: ±12): the clear bore given to the nut
SIGHT_YZ, SIGHT_R = (-45.0, 1060.0), 22.0   # this model's door sight glass (repowder/model.py: the ring's bore, r 22)


def bore(mesh, p, n, r: float):
    """The mesh with everything within r of the axis (p, n) clipped away: a see-through bore (no bore wall)."""
    n = np.asarray(n, float) / np.linalg.norm(n)
    # long edges first cut to <= 4 mm, so that no triangle spans the bore with all its corners outside it (an end cap)
    m = mesh.triangulate().clean().subdivide_adaptive(max_edge_len=4.0)
    rel = np.asarray(m.points) - np.asarray(p, float)
    m.point_data["_bore"] = np.linalg.norm(rel - np.outer(rel @ n, n), axis=1) - r
    out = m.clip_scalar(scalars="_bore", value=0.0, invert=False).extract_surface(algorithm="dataset_surface")
    for key in list(out.point_data.keys()):
        if key == "_bore":
            del out.point_data[key]
    return out


def window_hole(mesh, c, n, xa, w: float, h: float, depth: float = 20.0):
    """The mesh with a w x h rectangle clipped through it (centre c, normal n, x axis xa, +-depth along n)."""
    n = np.asarray(n, float) / np.linalg.norm(n)
    xa = np.asarray(xa, float) - n * float(np.dot(xa, n))
    xa /= np.linalg.norm(xa)
    ya = np.cross(n, xa)
    m = mesh.triangulate().clean().subdivide_adaptive(max_edge_len=4.0)
    rel = np.asarray(m.points) - np.asarray(c, float)
    m.point_data["_hole"] = np.maximum.reduce([np.abs(rel @ xa) - w / 2, np.abs(rel @ ya) - h / 2,
                                                np.abs(rel @ n) - depth])
    out = m.clip_scalar(scalars="_hole", value=0.0, invert=False).extract_surface(algorithm="dataset_surface")
    if "_hole" in out.point_data:
        del out.point_data["_hole"]
    return out


def model_window() -> dict | None:
    """The model's own lid window (commit e3b1428): centre on the front facet, normal, axes, size; None before it."""
    M = _M()
    lw = getattr(M, "LID_WINDOW", None)
    if lw is None:
        return None
    # the window is on the lid's own "left" facet (repowder/model.py hood_parts); turned=True (the default) puts it in
    # the machine's frame, where the turn has brought that facet to the front
    o, n = M.facet_plane(M.lid_params(), "left", lw["s"])
    n = np.asarray(n, float) / np.linalg.norm(n)
    xa = np.cross([0.0, 0.0, 1.0], n)
    return dict(centre=np.asarray(o, float), normal=n, x=xa / np.linalg.norm(xa), w=float(lw["w"]), h=float(lw["h"]))


# ------------------------------------------------------------------------------------------- into a scene
def add_units(sc, window: bool = False, hide_model_port: bool = True, sight: bool = True,
              see_window: bool = True) -> dict:
    """Add the three units to a Scene built by atom_base.build: the front unit on the chamber, the left unit on the
    door's group (it swings with the door), the top post fixed on the blue frame's top and its arm in its own group
    (``set_top_arm``). The model's own lid window is used (commit e3b1428); window=True re-fits DAL's pane onto the
    pre-e3b1428 lid instead (legacy). sight=True cuts the 44 mm hole behind the door's sight glass in this scene's door
    mesh (the model's glass is a disc on the plate); see_window=True opens the model's lid window through (it is a
    2 mm pocket in the 4 mm wall), so the top camera can see in; DAL's port nut is bored to the glass. Returns
    {unit: [names]}."""
    import atom_base as AB
    import pyvista as pv
    parts = dal_parts()
    moves = dict(front=front_move(), left=left_move(), post=np.eye(4), arm=np.eye(4))
    if window:
        moves["window"] = window_move(parts)[0]
    names: dict[str, list] = {k: [] for k in GROUPS}
    for k, m in parts.items():
        u = unit_of(k, m)
        if u is None or u not in moves:
            continue
        col, op = colour_of(k)
        nm = f"cams {u}: {k}"
        mesh = m.transform(moves[u], inplace=False)
        if k.startswith("(machine) front port nut"):       # DAL drew the nut solid: give it the glass's bore
            pp, nn = port_axis()
            mesh = bore(mesh, pp, nn, PORT_GLASS_R)
        kw = dict(specular=0.6) if col in (POLISH, ALU, STEEL) else {}
        if "screen" in k.lower():
            kw = dict(ambient=0.35, specular=0.9)
        sc.add(nm, mesh, col, GROUPS[u], opacity=op, **kw)
        names[u].append(nm)
    sc.parent[GROUPS["front"]] = "rp"
    sc.parent[GROUPS["left"]] = AB.g("door")
    sc.parent[GROUPS["post"]] = "rp"
    sc.parent[GROUPS["arm"]] = "rp"
    for gk in ("front", "left", "post", "arm"):
        sc.gmat.setdefault(GROUPS[gk], np.eye(4))
    if window:
        sc.parent[GROUPS["window"]] = AB.g("hood")
        sc.gmat.setdefault(GROUPS["window"], np.eye(4))
        lm = lid_mesh()
        for nm in ("hood", "w:hood"):
            if nm in sc.actors and lm is not None:
                sc.set_mesh(nm, lm)
        for nm in ("hood_window", "w:hood_window"):
            if nm in sc.actors:
                sc.show([nm], 0.0)
                sc.base_alpha[nm] = 0.0
    mw = model_window() if not window else None
    if mw is not None and see_window:       # the model cuts its window as a 2 mm pocket in a 4 mm wall: open it through
        for nm in ("hood", "w:hood"):
            if nm in sc.actors:
                m0 = pv.wrap(sc.actors[nm].GetMapper().GetInput())
                sc.set_mesh(nm, window_hole(m0, mw["centre"], mw["normal"], mw["x"], mw["w"], mw["h"]))
    if sight:                               # this model's door has no hole behind its sight glass: cut one here
        M = _M()
        for nm in ("door", "w:door"):
            if nm in sc.actors:
                m0 = pv.wrap(sc.actors[nm].GetMapper().GetInput())
                sc.set_mesh(nm, bore(m0, np.array([M.CH_X[0], SIGHT_YZ[0], SIGHT_YZ[1]]), np.array([1.0, 0, 0]),
                                     SIGHT_R))
    if hide_model_port:                     # DAL's port nut, glass and LED cover replace the model's flange and glass
        for nm in ("viewport_flange", "viewport_glass", "w:viewport_flange", "w:viewport_glass"):
            if nm in sc.actors:
                sc.show([nm], 0.0)
                sc.base_alpha[nm] = 0.0
    set_top_arm(sc, 0.0)
    sc.cams_names = names
    return names


def set_top_arm(sc, v: float):
    """The top arm at v of its swing about the post: 0 = the working dimple, 1 = the parked one (90 deg)."""
    sc.gmat[GROUPS["arm"]] = top_arm_matrix(v)
    sc.cams_top = float(v)


def top_arm_value(sc) -> float:
    return float(getattr(sc, "cams_top", 0.0))


def extrusion_point(s: float, v: float = 0.0, side: float = 0.0) -> np.ndarray:
    """A point on the 2020 extrusion's centre line, s mm out from the post's axis, with the arm at v; side > 0 moves
    it that far off the line horizontally, towards the side the arm turns to when it parks (its leading face)."""
    c, d = extrusion_axis()
    lead = np.array([-d[1], d[0], 0.0])           # +90 deg: where the arm goes when it parks
    # s from the post's axis, measured along the extrusion's own centre line
    foot = c + d * float(np.dot(np.r_[POST_XY, c[2]] - c, d))
    q = foot + d * s + lead * side
    return (top_arm_matrix(v) @ np.r_[q, 1.0])[:3]


def extrusion_axis() -> tuple[np.ndarray, np.ndarray]:
    """The 2020 extrusion's centre line in the working position: (its centroid, its unit direction out to the tip)."""
    ex = next(m for k, m in dal_parts().items() if k.startswith("(bought) 2020 extrusion"))
    pts = np.asarray(ex.points)
    c = 0.5 * (pts.min(0) + pts.max(0))
    _, _, vt = np.linalg.svd(pts - pts.mean(0))
    d = vt[0] * (1 if vt[0][1] < 0 else -1)
    d[2] = 0.0
    return c, d / np.linalg.norm(d)


# ------------------------------------------------------------------------------------------- the live feeds
class Feeds:
    """The four cameras rendered from their own poses and lenses, every `every` frames, in a strip under the frame
    (the render window grows by `strip` px; the clip only sees the top 1280 x 720), and put (1) on each unit's display
    as a texture and (2) as picture-in-picture panels with the camera's name (``pip``). Extra vtkRenderers in the same
    window share the scene's actors, so the cost is the extra draws only. The glass panes are left out of the feeds
    (the cameras see through them), and so is each unit's own housing."""

    ORDER = ("top_hq", "front_hq", "front_wide", "left_wide")

    def __init__(self, sc, every: int = 2, slot=(320, 240), light: dict | None = None):
        import vtk
        from scene import AUDIT, PREVIEW
        self.sc, self.every, self.slot = sc, max(1, int(every)), slot
        self.off = AUDIT
        self.preview = PREVIEW
        self.crops: dict[str, np.ndarray] = {}
        self.panels: list[str] = []
        self.panel_alpha = 0.0
        self.on = True
        self.tex_actors: dict[str, object] = {}
        self.last = -10**9
        self.light = dict(top_hq=0.35, front_hq=1.0, front_wide=1.0, left_wide=0.55, **(light or {}))
        if self.off:
            return
        W, H = sc.size
        self.H0 = H
        self.strip = slot[1]
        sc.pl.window_size = (W, H + self.strip)
        sc.pl.renderer.SetViewport(0.0, self.strip / (H + self.strip), 1.0, 1.0)
        self.rens = {}
        for i, key in enumerate(self.ORDER):
            ren = vtk.vtkRenderer()
            hf, vf = FOV[CAMERAS[key]["fov"]]
            aspect = math.tan(math.radians(hf / 2)) / math.tan(math.radians(vf / 2))
            h = min(slot[1], int(round(slot[0] / aspect)))
            Ht = H + self.strip
            ren.SetViewport(i * slot[0] / W, 0.0, (i + 1) * slot[0] / W, h / Ht)
            ren.SetBackground(0.03, 0.03, 0.035)
            ren.AutomaticLightCreationOff()
            lt = vtk.vtkLight()
            lt.SetLightTypeToHeadlight()
            lt.SetIntensity(self.light[key])
            ren.AddLight(lt)
            ren.GetActiveCamera().SetViewAngle(vf)
            ren.SetNearClippingPlaneTolerance(0.0005)
            sc.pl.ren_win.AddRenderer(ren)
            self.rens[key] = (ren, h)
        self.sync()
        orig_render, orig_project, orig_overlay = sc.render_base, sc.project, sc.overlay
        feeds = self

        def render_base():
            draw = feeds.on and (sc.n - feeds.last >= feeds.every or feeds.preview)
            for key, (ren, _) in feeds.rens.items():
                ren.SetDraw(bool(draw))
            if draw:
                feeds._cams()
            img = orig_render()
            if draw:
                feeds.last = sc.n
                feeds._grab(img)
            return img[:feeds.H0]

        def project(xyz):
            ren = sc.pl.renderer
            ren.SetWorldPoint(float(xyz[0]), float(xyz[1]), float(xyz[2]), 1.0)
            ren.WorldToDisplay()
            dx, dy, _ = ren.GetDisplayPoint()
            return dx / sc.size[0], (feeds.H0 + feeds.strip - dy) / feeds.H0

        def overlay(img, scale, anchors):
            img = orig_overlay(img, scale, anchors)
            return feeds._pip(img, scale)

        sc.render_base, sc.project, sc.overlay = render_base, project, overlay

    # the scene's actors, less the glass and each unit's own housing
    def sync(self):
        if self.off:
            return
        skip_all = {n for n in self.sc.actors if ("glass" in n.lower() and "ring" not in n.lower())
                    or "lid window" in n.lower() or n.split(":")[-1] == "hood_window"
                    or n.startswith(("cams los", "cams lid ghost"))}
        own = {"top_hq": ("cams arm:",), "front_hq": ("cams front: front", "cams front: (bought)"),
               "front_wide": ("cams front: front", "cams front: (bought)"), "left_wide": ("cams left:",)}
        for key, (ren, _) in self.rens.items():
            have = {id(a) for a in _actors(ren)}
            for n, a in self.sc.actors.items():
                if n in skip_all or any(n.lower().startswith(o.lower()) for o in own[key]) or n.startswith("feedtex"):
                    continue
                if id(a) not in have:
                    ren.AddActor(a)

    def _cams(self):
        sc = self.sc
        sc.apply()
        import atom_base as AB
        door = float(getattr(sc, "joint_vals", {}).get("door", 0.0))
        poses = unit_poses(top_arm_value(sc), door)
        for key, (ren, _) in self.rens.items():
            p = poses[key]
            cam = ren.GetActiveCamera()
            eye = AB.W(p["eye"])
            cam.SetPosition(*eye)
            cam.SetFocalPoint(*(eye + p["dir"] * 200.0))
            cam.SetViewUp(*p["up"])
            cam.SetViewAngle(p["vfov"])
            ren.ResetCameraClippingRange()
            near, far = cam.GetClippingRange()
            cam.SetClippingRange(2.0, max(far, 4000.0))

    def _grab(self, img: np.ndarray):

        for i, key in enumerate(self.ORDER):
            ren, h = self.rens[key]
            x0 = i * self.slot[0]
            y1 = img.shape[0]
            self.crops[key] = img[y1 - h:y1, x0:x0 + self.slot[0]].copy()
        self._textures()

    def _textures(self):
        import pyvista as pv
        for key, act in self.tex_actors.items():
            src = self._display_image(key)
            if src is not None:
                act.SetTexture(pv.Texture(src))

    def _display_image(self, disp: str):
        c = self.crops
        if disp == "front" and "front_hq" in c and "front_wide" in c:
            a, b = c["front_hq"], c["front_wide"]
            h = 240
            pa = _resize(a, (int(round(a.shape[1] * h / a.shape[0])), h))
            pb = _resize(b, (int(round(b.shape[1] * h / b.shape[0])), h))
            img = np.zeros((h * 480 // 800 * 800 // 480, 800, 3), np.uint8)    # 800 x 480 panel, 5:3
            img = np.zeros((480, 800, 3), np.uint8)
            wa = 400
            ha = int(round(pa.shape[0] * wa / pa.shape[1]))
            hb = int(round(pb.shape[0] * wa / pb.shape[1]))
            img[(480 - ha) // 2:(480 - ha) // 2 + ha, :wa] = _resize(pa, (wa, ha))
            img[(480 - hb) // 2:(480 - hb) // 2 + hb, wa:] = _resize(pb, (400, hb))
            return img
        if disp == "left" and "left_wide" in c:
            a = c["left_wide"]
            img = np.zeros((720, 1280, 3), np.uint8)                          # 1280 x 720 as mounted (landscape)
            h = int(round(a.shape[0] * 1280 / a.shape[1]))
            img[(720 - h) // 2:(720 - h) // 2 + h] = _resize(a, (1280, h))
            return img
        if disp == "top" and "top_hq" in c:
            a = c["top_hq"]
            img = np.zeros((640, 480, 3), np.uint8)                            # 480 x 640 portrait: letterboxed
            h = int(round(a.shape[0] * 480 / a.shape[1]))
            img[(640 - h) // 2:(640 - h) // 2 + h] = _resize(a, (480, h))
            return img
        return None

    def add_display_textures(self):
        """A textured quad on each display's screen, riding its unit, showing that unit's feed."""
        import pyvista as pv
        sc = self.sc
        parts = dal_parts()
        spec = dict(front=("(bought) 5 in HDMI display screen", "front", (0, -1, 0)),
                    left=("(bought) DSI display screen", "left", (-1, 0, 0)),
                    top=("(bought) small DSI display screen", "arm", (0, -1, 0.2)))
        moves = dict(front=front_move(), left=left_move(), arm=np.eye(4))
        for disp, (pname, unit, toward) in spec.items():
            m = parts[pname].transform(moves[unit], inplace=False)
            pts = np.asarray(m.points)
            c = pts.mean(0)
            u_, s_, vt = np.linalg.svd(pts - c)
            n = vt[2] * (1 if np.dot(vt[2], toward) > 0 else -1)
            up = np.array([0, 0, 1.0]) - n * n[2]
            up /= np.linalg.norm(up)
            rt = np.cross(up, n)
            hw = float(np.max(np.abs((pts - c) @ rt)))
            hh = float(np.max(np.abs((pts - c) @ up)))
            front = float(np.max((pts - c) @ n)) + 0.4
            c0 = c + n * front
            quad = pv.PolyData(np.array([c0 - rt * hw - up * hh, c0 + rt * hw - up * hh, c0 + rt * hw + up * hh,
                                         c0 - rt * hw + up * hh]), np.array([4, 0, 1, 2, 3]))
            quad.active_texture_coordinates = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
            nm = f"feedtex {disp}"
            sc.add(nm, quad, (1.0, 1.0, 1.0), GROUPS[unit], ambient=1.0, diffuse=0.0, specular=0.0, smooth_shading=False)
            img = np.zeros((32, 32, 3), np.uint8)
            sc.actors[nm].SetTexture(pv.Texture(img))
            self.tex_actors[disp] = sc.actors[nm]

    def pip(self, keys=None, alpha=1.0):
        """Show these feeds as panels (None: none)."""
        self.panels = list(keys or [])
        self.panel_alpha = alpha if keys else 0.0

    def _pip(self, img, scale):
        if not self.panels or self.panel_alpha <= 0.02:
            return img
        from PIL import Image, ImageDraw
        from scene import font
        W, H = img.size
        s = W / 1280.0
        pw = int(300 * s)
        d = ImageDraw.Draw(img, "RGBA")
        x0 = W - pw - int(12 * s)
        y = int(52 * s)
        for key in self.panels:
            a = self.crops.get(key)
            if a is None:
                continue
            ph = int(round(a.shape[0] * pw / a.shape[1]))
            tile = Image.fromarray(a).resize((pw, ph), Image.LANCZOS)
            if self.panel_alpha < 0.98:
                tile.putalpha(int(255 * self.panel_alpha))
                img.paste(tile, (x0, y), tile)
            else:
                img.paste(tile, (x0, y))
            d.rectangle((x0 - 1, y - 1, x0 + pw, y + ph), outline=(30, 60, 140, 255), width=max(1, int(2 * s)))
            ft = font(12.5 * max(s, 0.8))
            lab = CAMERAS[key]["label"]
            tw = d.textlength(lab, font=ft)
            d.rectangle((x0, y + ph - int(19 * s), x0 + min(pw, tw + 10 * s), y + ph), fill=(0, 0, 0, 170))
            d.text((x0 + 5 * s, y + ph - int(18 * s)), lab, font=ft, fill=(255, 255, 255, 255))
            y += ph + int(8 * s)
        return img


def _actors(ren):
    col = ren.GetActors()
    col.InitTraversal()
    out = []
    for _ in range(col.GetNumberOfItems()):
        out.append(col.GetNextActor())
    return out


def _resize(a: np.ndarray, size) -> np.ndarray:
    from PIL import Image
    return np.asarray(Image.fromarray(a).resize((max(1, int(size[0])), max(1, int(size[1]))), Image.BILINEAR))


if __name__ == "__main__":
    if "--extract" in sys.argv:
        print("wrote", extract())
    else:
        wp = window_pose()
        print("window centre", wp["centre"].round(1), "normal", wp["normal"].round(3))
        for k, p in unit_poses().items():
            print(k, "eye", p["eye"].round(1), "dir", p["dir"].round(3), "fov", p["hfov"], p["vfov"])
