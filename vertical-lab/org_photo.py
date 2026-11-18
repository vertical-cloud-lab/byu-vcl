"""The org page's GIF (org_gif.py), path-traced: the same scene, moves, camera and labels, rendered with Blender's Cycles
instead of VTK (PR #329, Sterling, 2026-11-18: "somewhat related to #351, attempt making a more photorealistic version
of this").

Three passes, so the slow one can run on its own and be resumed:

1. ``record`` (the lab's venv): org_gif.movie() runs as it does for the GIF, but each frame's draw is replaced by a
   record of the scene: every actor's mesh (once per version), its world matrix, visibility, opacity, colour and glow;
   the camera; the leader labels. Nothing is rendered. -> REC/meshes/*.npz, REC/actors.json, REC/snaps.jsonl, and
   out/<ORG_NAME>.json (the phases the header band reads). A frame drawn once and held (a hold) is one snap.
2. ``render`` (a venv with ``bpy``): photo_render.py rebuilds the scene in Blender and path-traces each snap with Cycles
   -> REC/png/<snap>.png, every 4th snap across the loop first, then every 2nd, then the rest (``PHOTO_STRIDES``);
   ``PHOTO_SNAPS`` picks snaps, ``PHOTO_RANGE`` a second worker's share. Snaps already rendered are skipped, so it
   resumes.
3. ``compose`` (the lab's venv): each snap's PNG under its leader labels, held for its frames -> out/mp4/<NAME>.mp4;
   then ``org_gif.py gif`` makes the GIF and the README MP4 as for the VTK clip. A snap not rendered yet is an
   in-between made by optical flow from the rendered snaps on either side, within a camera shot (Filler), so a
   partial render, every 4th or 2nd snap, still makes the whole loop at full frame rate.

    ORG_NAME=org_vertical_lab_photo VIZ3D_FPS=12 xvfb-run -a python3 org_photo.py record
    /path/to/bpy-venv/bin/python photo_render.py [REC]              # Cycles, CPU; PHOTO_SAMPLES, PHOTO_SIZE, ...
    ORG_NAME=org_vertical_lab_photo python3 org_photo.py compose
    ORG_NAME=org_vertical_lab_photo python3 org_gif.py gif 880 0 256
    python3 org_photo.py sheet 0 160 ...                           # round 9 beside the path-traced frames
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REC = Path(os.environ.get("PHOTO_REC", "/tmp/org_photo"))


# ============================================================================================ 1. record
class Recorder:
    """Scene.snap's stand-in: the scene's state, as a delta against the last snap, one JSON line per snap."""

    def __init__(self, sc, rec: Path = REC):
        import vtk
        self.vtk = vtk
        self.sc = sc
        self.rec = rec
        (rec / "meshes").mkdir(parents=True, exist_ok=True)
        (rec / "png").mkdir(parents=True, exist_ok=True)
        self.fh = open(rec / "snaps.jsonl", "w")
        self.idx: dict[str, int] = {}          # actor name -> index
        self.info: list[dict] = []             # per actor, static: name, shininess, kind
        self.last: dict[int, dict] = {}        # per actor index, the last recorded state
        self.mesh_key: dict[tuple, str] = {}   # (the polydata's C++ address, MTime) -> mesh file key
        self.n_mesh = 0
        self.n_snap = 0
        self.n_info = 0
        self.t0 = time.time()

    def _actor(self, name, actor):
        k = self.idx.get(name)
        if k is not None:
            return k
        k = self.idx[name] = len(self.info)
        prop = actor.GetProperty()
        spec = prop.GetSpecular()
        shine = float(np.sqrt(max(spec, 0.0) / 0.30)) if spec > 0 else 0.0
        rep = prop.GetRepresentation()          # 0 points, 1 wireframe, 2 surface
        self.info.append(dict(name=name, group=self.sc.group_of.get(name, ""), shine=round(min(shine, 1.0), 3),
                              points=bool(rep == 0), point_size=float(prop.GetPointSize()),
                              diffuse=round(prop.GetDiffuse(), 3), lines=bool(rep == 1)))
        return k

    def _mesh(self, actor) -> str | None:
        poly = actor.GetMapper().GetInput()
        if poly is None:
            return None
        key = (poly.__this__, poly.GetMTime())     # the C++ object (a Python wrapper's id() isn't stable)
        mk = self.mesh_key.get(key)
        if mk is not None:
            return mk
        vtk = self.vtk
        from vtk.util.numpy_support import vtk_to_numpy
        mk = f"m{self.n_mesh:06d}"
        self.n_mesh += 1
        npts = poly.GetNumberOfPoints()
        data = {}
        if npts:
            pts = vtk_to_numpy(poly.GetPoints().GetData()).astype(np.float32)
        else:
            pts = np.zeros((0, 3), np.float32)
        data["points"] = pts
        tris = np.zeros((0, 3), np.int32)
        if poly.GetNumberOfPolys() or poly.GetNumberOfStrips():
            tf = vtk.vtkTriangleFilter()
            tf.SetInputData(poly)
            tf.PassVertsOff()
            tf.PassLinesOff()
            tf.Update()
            out = tf.GetOutput()
            if out.GetNumberOfPolys():
                cells = vtk_to_numpy(out.GetPolys().GetConnectivityArray()).astype(np.int32)
                tris = cells.reshape(-1, 3)
                if out.GetNumberOfPoints() != npts:       # the filter keeps the points; if not, take its own
                    data["points"] = vtk_to_numpy(out.GetPoints().GetData()).astype(np.float32)
        data["tris"] = tris
        # per-point colours, where the mapper draws scalars (RGB(A) uint8)
        mapper = actor.GetMapper()
        if mapper.GetScalarVisibility():
            arr = poly.GetPointData().GetScalars()
            if arr is not None and arr.GetDataType() == vtk.VTK_UNSIGNED_CHAR and arr.GetNumberOfComponents() in (3, 4):
                data["rgb"] = vtk_to_numpy(arr)[:, :3].astype(np.uint8)
        np.savez(self.rec / "meshes" / f"{mk}.npz", **data)
        self.mesh_key[key] = mk
        return mk

    def snap(self, n=1):
        sc = self.sc
        sc.apply()
        cam = sc.pl.renderer.GetActiveCamera()      # for project(): the camera set without a render
        cam.SetPosition(*map(float, sc.cam[0]))
        cam.SetFocalPoint(*map(float, sc.cam[1]))
        cam.SetViewUp(*map(float, sc.cam[2]))
        cam.SetViewAngle(float(sc.view_angle))
        ch = {}
        for name, actor in sc.actors.items():
            k = self._actor(name, actor)
            vis = bool(actor.GetVisibility())
            last = self.last.setdefault(k, {})
            st = {"v": vis}
            if vis:
                prop = actor.GetProperty()
                m = actor.GetMatrix()
                st["m"] = [round(m.GetElement(i, j), 4) for i in range(4) for j in range(4)]
                st["o"] = round(prop.GetOpacity(), 4)
                st["c"] = [round(x, 4) for x in prop.GetColor()]
                st["a"] = round(prop.GetAmbient(), 3)
                st["mesh"] = self._mesh(actor)
            d = {kk: vv for kk, vv in st.items() if last.get(kk) != vv}
            if d:
                ch[k] = d
                last.update(d)
        anchors = [sc.project(xyz) for _, xyz, _, _ in sc.labels]
        rec = dict(s=self.n_snap, n0=sc.n, n=n, cam=[list(map(float, v)) for v in sc.cam[:3]],
                   va=float(sc.view_angle), ch=ch,
                   ov=dict(title=sc.title, label=sc.label, caption=sc.caption,
                           gauges=[list(g) for g in sc.gauges],
                           labels=[[t, list(map(float, xyz)), list(map(float, f)), float(a)]
                                   for t, xyz, f, a in sc.labels],
                           anchors=[list(map(float, p)) for p in anchors], scale=float(sc.text_scale)))
        self.fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
        self.fh.flush()
        if len(self.info) != self.n_info:           # new actors: actors.json as it stands, so render can start early
            self.n_info = len(self.info)
            (self.rec / "actors.json").write_text(json.dumps(self.info, indent=0) + "\n")
        if self.n_snap % 50 == 0:
            print(f"record: snap {self.n_snap}, frame {sc.n}, {self.n_mesh} meshes, {time.time() - self.t0:.0f} s",
                  flush=True)
        self.n_snap += 1
        sc.n += n
        return None

    def close(self):
        self.fh.close()
        (self.rec / "actors.json").write_text(json.dumps(self.info, indent=0) + "\n")
        (self.rec / "done").write_text(f"{self.n_snap} snaps\n")
        print(f"record: {self.n_snap} snaps, {len(self.info)} actors, {self.n_mesh} meshes", flush=True)


def record():
    import org_gif as OG
    import scene as SC
    rec = {}
    orig_build = OG.build

    def build(data, mp4=True):
        sc, L, K, fx = orig_build(data, mp4=False)        # no encoder: this pass writes no MP4
        r = rec["r"] = Recorder(sc)
        sc.snap = r.snap
        return sc, L, K, fx
    OG.build = build
    meta_written = {}
    orig_save = SC.Scene.save

    def save(self):
        r = rec.get("r")
        if r is not None:
            r.close()
        self.mp4 = None
        meta = dict(name=self.name, fps=SC.FPS, n_frames=self.n, size=list(self.size), substeps=self.substeps)
        SC.OUT.joinpath(f"{self.name}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
        meta_written["ok"] = True
        self.pl.close()
        return f"{self.name}: {self.n} frames recorded"
    SC.Scene.save = save
    OG.movie()


# ============================================================================================ 3. compose
CUT_MM = 400.0       # the camera moving more than this (position + focal point) between two snaps is a cut


class Filler:
    """Each snap's picture: its own PNG, or the PNG of the run of identical snaps it belongs to (photo_render.py
    renders such a run once), or, for a snap not rendered yet, an in-between made by optical flow (OpenCV's DIS) from
    the nearest rendered snaps before and after it with no camera cut between (PHOTO_FILL=flow, the default), or the
    one before held (PHOTO_FILL=hold). A partial render, every 2nd or 4th snap, then still makes the whole loop at
    full frame rate. On round 9's frames 40-152, in-betweens from every 4th snap against the snap rendered in the
    middle: 24-37 dB PSNR, where holding the one before gave 15-36 (a camera move: 23.9 against 14.7)."""

    def __init__(self, snaps, png_dir: Path):
        from PIL import Image
        self.Image = Image
        self.png_dir = png_dir
        self.mode = os.environ.get("PHOTO_FILL", "flow")
        self.rep, self.reps, prev_key, rep = {}, [], None, None
        for s in snaps:
            key = (json.dumps(s["cam"]), s["va"])
            if s["ch"] or key != prev_key or rep is None:
                rep = s["s"]
                self.reps.append(s)
            prev_key = key
            self.rep[s["s"]] = rep
        self.seg, seg, last = {}, 0, None       # camera segments: a cut starts a new one
        for s in self.reps:
            if last is not None:
                d = (np.linalg.norm(np.subtract(s["cam"][0], last["cam"][0])) +
                     np.linalg.norm(np.subtract(s["cam"][1], last["cam"][1])))
                if d > CUT_MM or abs(s["va"] - last["va"]) > 2.0:
                    seg += 1
            self.seg[s["s"]] = seg
            last = s
        self.t = {s["s"]: s["n0"] for s in self.reps}
        self.have = [s["s"] for s in self.reps if self._load(s["s"]) is not None]
        self.cache: dict = {}
        self.flows: dict = {}
        self.n_flow = self.n_hold = 0

    def _load(self, r):
        p = self.png_dir / f"{r:05d}.png"
        if not p.exists():
            return None
        try:
            return np.asarray(self.Image.open(p).convert("RGB"))
        except OSError:
            return None

    def _flow(self, a, b):
        import cv2
        if not hasattr(self, "dis"):
            self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        return self.dis.calc(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY), cv2.cvtColor(b, cv2.COLOR_RGB2GRAY), None)

    def image(self, s_no):
        import bisect
        r = self.rep[s_no]
        if r in self.cache:
            return self.cache[r]
        im = self._load(r)
        if im is None:
            k = bisect.bisect_left(self.have, r)
            A = self.have[k - 1] if k > 0 and self.seg[self.have[k - 1]] == self.seg[r] else None
            B = self.have[k] if k < len(self.have) and self.seg[self.have[k]] == self.seg[r] else None
            if A is not None and B is not None and self.mode == "flow":
                import cv2
                a, b = self.image(A), self.image(B)
                if (A, B) not in self.flows:
                    self.flows = {(A, B): (self._flow(a, b), self._flow(b, a))}      # one pair at a time
                fab, fba = self.flows[(A, B)]
                t = (self.t[r] - self.t[A]) / max(1, self.t[B] - self.t[A])
                h, w = a.shape[:2]
                gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
                wa = cv2.remap(a, gx - t * fab[..., 0], gy - t * fab[..., 1], cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REPLICATE)
                wb = cv2.remap(b, gx - (1 - t) * fba[..., 0], gy - (1 - t) * fba[..., 1], cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REPLICATE)
                im = ((1 - t) * wa.astype(np.float32) + t * wb.astype(np.float32)).clip(0, 255).astype(np.uint8)
                self.n_flow += 1
            else:
                near = A if A is not None else B
                if near is None:
                    near = self.have[max(0, k - 1)]
                im = self.image(near)
                self.n_hold += 1
        if len(self.cache) > 64:
            self.cache.pop(next(iter(self.cache)))
        self.cache[r] = im
        return im


def compose():
    """Each snap's picture (Filler) under its leader labels, held for the snap's frames -> out/mp4/<NAME>.mp4 at the
    PNGs' size, and out/<NAME>.json's size set to match (gif() and video() read both)."""
    from types import SimpleNamespace

    from PIL import Image

    import org_gif as OG
    import scene as SC
    snaps = [json.loads(line) for line in open(REC / "snaps.jsonl")]
    meta_path = SC.OUT / f"{OG.NAME}.json"
    meta = json.loads(meta_path.read_text())
    fill = Filler(snaps, REC / "png")
    size = Image.open(REC / "png" / f"{fill.have[0]:05d}.png").size
    k = size[0] / meta["size"][0]          # the labels: drawn at the PNG's size as they were at the scene's
    path = SC.OUT / "mp4" / f"{OG.NAME}.mp4"
    enc = SC.encoder(path, size, crf=int(os.environ.get("PHOTO_CRF", "18")))
    for s in snaps:
        base = Image.fromarray(fill.image(s["s"]))
        if base.size != size:
            base = base.resize(size, Image.LANCZOS)
        ov = s["ov"]
        fake = SimpleNamespace(title=ov["title"], label=ov["label"], caption=ov["caption"],
                               gauges=[tuple(g) for g in ov["gauges"]],
                               labels=[(t, tuple(xyz), tuple(f), a) for t, xyz, f, a in ov["labels"]])
        hi = SC.Scene.overlay(fake, base, ov["scale"] * k, [tuple(a) for a in ov["anchors"]])
        buf = np.asarray(hi.convert("RGB")).tobytes()
        for _ in range(s["n"]):
            enc.stdin.write(buf)
    enc.stdin.close()
    enc.wait()
    n = sum(s["n"] for s in snaps)
    st = dict(snaps=len(snaps), distinct=len(fill.reps), rendered=len(fill.have), in_between=fill.n_flow,
              held=fill.n_hold, cuts=max(fill.seg.values()), frames=n)
    meta.update(size=list(size), photo=st)
    meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(f"{path.name}: {n} frames; {st}", flush=True)


def sheet(*snaps_, out="org_vertical_lab_photo_vs_r9.jpg"):
    """Round 9's VTK frames (out/mp4/org_vertical_lab.mp4) beside the path-traced ones, for the given snaps, each with
    its leader labels -> out/<out>."""
    import subprocess
    import tempfile
    from types import SimpleNamespace

    from PIL import Image, ImageDraw

    import scene as SC
    want = [int(v) for v in snaps_]
    recs = {}
    for line in open(REC / "snaps.jsonl"):
        r = json.loads(line)
        if r["s"] in want:
            recs[r["s"]] = r
    rows = []
    for sn in want:
        r = recs[sn]
        ph = Image.open(REC / "png" / f"{sn:05d}.png").convert("RGB")
        W, H = ph.size
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(SC.OUT / "mp4" / "org_vertical_lab.mp4"),
                            "-vf", f"select=eq(n\\,{r['n0']}),scale={W}:{H}:flags=lanczos", "-vframes", "1",
                            f"{tmp}/v.png"], check=True)
            old = Image.open(f"{tmp}/v.png").convert("RGB")
        ov = r["ov"]
        fake = SimpleNamespace(title="", label="", caption="", gauges=[],
                               labels=[(t, tuple(xyz), tuple(f), a) for t, xyz, f, a in ov["labels"]])
        ph = SC.Scene.overlay(fake, ph, ov["scale"] * W / 1280, [tuple(a) for a in ov["anchors"]])
        row = Image.new("RGB", (2 * W + 12, H + 30), "white")
        d = ImageDraw.Draw(row)
        f = SC.font(17)
        d.text((4, 5), f"Round 9 (VTK), frame {r['n0']}", font=f, fill=(20, 20, 24))
        d.text((W + 16, 5), f"Path-traced (Blender Cycles), frame {r['n0']}", font=f, fill=(20, 20, 24))
        row.paste(old, (0, 30))
        row.paste(ph, (W + 12, 30))
        rows.append(row)
    sh = Image.new("RGB", (rows[0].width, sum(r.height + 10 for r in rows)), "white")
    y = 0
    for r in rows:
        sh.paste(r, (0, y))
        y += r.height + 10
    sh.save(SC.OUT / out, quality=88)
    print(f"{out}: {len(rows)} rows", flush=True)


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    {"record": record, "compose": compose, "sheet": sheet}[sys.argv[1]](*sys.argv[2:])
