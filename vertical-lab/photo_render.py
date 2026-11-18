"""org_photo.py's record, path-traced with Blender's Cycles (bpy, CPU): the org GIF's scene rebuilt in Blender, each
snap rendered to REC/png/<snap>.png (RGBA, the background left transparent for compose to put on white).

Run with a Python that has ``bpy`` (5.3 here; ``pip install bpy`` wants Python 3.13), not the lab's venv:

    python photo_render.py [REC]        # every snap not yet rendered, in order
    PHOTO_SNAPS=0,120,400 ...           # only these snaps (also a:b, a:b:step)
    PHOTO_ORDER=coarse ...              # every 8th snap first, then every 4th, 2nd, the rest: a partial run is a
                                        # whole loop at a lower frame rate
    PHOTO_SAMPLES=16 PHOTO_SIZE=1280x720 PHOTO_THREADS=0

The scene, in Blender's units (m; the lab's mm x 0.001):
- every VTK actor is an object holding its mesh in mm under a world matrix of 0.001 x the actor's own. Shading is
  smooth with edges sharp past 35 deg (scene.FEATURE_ANGLE). Point actors (the melt's droplets) are spheres;
- materials come from the actor's colour (sRGB -> linear), its opacity and its 0-1 shininess (the specular that
  scene.surface_style set): 0.65 and up is metal, roughness falls from 0.75 to 0.15 with it; an ambient over 0.35
  glows (the melt, the hot cup). Colour, opacity and glow are per object (Object Info, an object property), so a fade
  changes no shader. The floor is polished concrete;
- light: a large soft panel overhead, a sun low enough to throw shadows across the floor, and a pale grey sky for
  the bounce; AgX tone mapping.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

REC = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else Path("/tmp/org_photo")
SAMPLES = int(os.environ.get("PHOTO_SAMPLES", "16"))
W, H = (int(v) for v in os.environ.get("PHOTO_SIZE", "1280x720").split("x"))
THREADS = int(os.environ.get("PHOTO_THREADS", "0"))
FEATURE_ANGLE = 35.0
MM = 0.001
GHOST = float(os.environ.get("PHOTO_GHOST", "0.6"))     # a see-through part's opacity, against the VTK clip's
OUTDIR = Path(os.environ.get("PHOTO_OUT", str(REC / "png")))


def srgb_to_lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


# ============================================================================================ the Blender scene
def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = SAMPLES
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = float(os.environ.get("PHOTO_NOISE", "0.03"))
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    try:
        cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
        cy.denoising_prefilter = "ACCURATE"
    except Exception:
        pass
    cy.max_bounces = 4
    cy.diffuse_bounces = 2
    cy.glossy_bounces = 2
    cy.transmission_bounces = 2
    cy.transparent_max_bounces = 16
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.sample_clamp_indirect = 3.0
    cy.use_animated_seed = False
    cy.seed = 7
    sc.render.use_persistent_data = True
    sc.render.film_transparent = False
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.compression = 15
    if THREADS:
        sc.render.threads_mode = "FIXED"
        sc.render.threads = THREADS
    sc.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast", "AgX - Base Contrast", "None"):
        try:
            sc.view_settings.look = look
            break
        except (TypeError, ValueError):
            continue
    print("photo: view", sc.view_settings.view_transform, sc.view_settings.look, flush=True)
    sc.view_settings.exposure = float(os.environ.get("PHOTO_EXPOSURE", "-1.7"))
    # sky: pale grey, for the bounce and the reflections in the metal
    world = bpy.data.worlds.new("lab")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes.get("Background") or nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.78, 0.80, 0.84, 1.0)
    bg.inputs["Strength"].default_value = float(os.environ.get("PHOTO_SKY", "0.35"))
    # the backdrop the camera sees is plain white, as the org page is (and as the VTK clip's was). It is drawn, not
    # left transparent: Cycles denoises the colour but not the alpha, so a see-through panel in front of an empty
    # background came out speckled where the PNG was put on white
    white = nt.nodes.new("ShaderNodeBackground")
    white.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    white.inputs["Strength"].default_value = 40.0 * 2.0 ** -float(os.environ.get("PHOTO_EXPOSURE", "-1.7"))
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(bg.outputs["Background"], mix.inputs[1])
    nt.links.new(white.outputs["Background"], mix.inputs[2])
    out = nt.nodes.get("World Output") or nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    # a camera
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.sensor_fit = "VERTICAL"
    cam.data.clip_start = 0.02
    cam.data.clip_end = 300.0
    return sc, cam


def add_lights(sc, centre, span):
    """A soft panel over the lab and a sun from the front left, in the lab's frame (x east, y north, z up)."""
    cx, cy_, cz = centre
    panel = bpy.data.lights.new("panel", "AREA")
    panel.shape = "RECTANGLE"
    panel.size, panel.size_y = span[0] * 0.8, span[1] * 0.8
    panel.energy = float(os.environ.get("PHOTO_PANEL", "1.2")) * panel.size * panel.size_y     # W/m2 under it
    ob = bpy.data.objects.new("panel", panel)
    ob.location = (cx, cy_, 5.2)
    sc.collection.objects.link(ob)
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = float(os.environ.get("PHOTO_SUN", "1.6"))
    sun.angle = math.radians(12.0)
    ob = bpy.data.objects.new("sun", sun)
    # from the south west (the camera's side), 50 deg up
    el, az = math.radians(50.0), math.radians(-35.0)
    d = np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)])   # towards the sun
    z = d / np.linalg.norm(d)
    x = np.cross((0, 0, 1), z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    ob.matrix_world = Matrix([[x[0], y[0], z[0], 0], [x[1], y[1], z[1], 0], [x[2], y[2], z[2], 0], [0, 0, 0, 1]])
    sc.collection.objects.link(ob)


_MATS: dict = {}


def material(kind: str, shine: float, vcol: bool = False):
    """One material per (kind, shininess bucket): colour and opacity from Object Info, glow from obj["emit"]."""
    b = round(min(max(shine, 0.0), 1.0) * 10) / 10
    key = (kind, b, vcol)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(f"{kind}_{b:.1f}{'_v' if vcol else ''}")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    info = nt.nodes.new("ShaderNodeObjectInfo")
    emit = nt.nodes.new("ShaderNodeAttribute")
    emit.attribute_type = "OBJECT"
    emit.attribute_name = "emit"
    col = info.outputs["Color"]
    if vcol:
        va = nt.nodes.new("ShaderNodeVertexColor")
        va.layer_name = "rgb"
        col = va.outputs["Color"]
    metal = kind == "metal"
    rough = 0.75 - 0.6 * b
    if kind == "floor":
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (0.004, 0.004, 0.004)       # mm in the object's frame
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 3.0
        nz.inputs["Detail"].default_value = 8.0
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.inputs["To Min"].default_value = 0.66      # concrete: darker than the VTK floor's colour, so the
        ramp.inputs["To Max"].default_value = 0.80      # tape on it reads
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], ramp.inputs["Value"])
        nt.links.new(col, mix.inputs[6])
        nt.links.new(ramp.outputs["Result"], mix.inputs[7])
        col = mix.outputs[2]
        rough = 0.42
    nt.links.new(col, bsdf.inputs["Base Color"])
    nt.links.new(info.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Metallic"].default_value = 1.0 if metal else 0.0
    bsdf.inputs["Roughness"].default_value = max(0.12, rough)
    if metal:
        bsdf.inputs["Roughness"].default_value = max(0.22, rough)
    nt.links.new(info.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(emit.outputs["Fac"], bsdf.inputs["Emission Strength"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    _MATS[key] = m
    return m


_PTS_NG = None


def points_group():
    """Geometry nodes: a mesh's vertices -> points of radius `r` (Cycles draws them as spheres)."""
    global _PTS_NG
    if _PTS_NG is not None:
        return _PTS_NG
    ng = bpy.data.node_groups.new("to_points", "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Radius", in_out="INPUT", socket_type="NodeSocketFloat")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi = ng.nodes.new("NodeGroupInput")
    go = ng.nodes.new("NodeGroupOutput")
    mp = ng.nodes.new("GeometryNodeMeshToPoints")
    ng.links.new(gi.outputs[0], mp.inputs["Mesh"])
    ng.links.new(gi.outputs[1], mp.inputs["Radius"])
    ng.links.new(mp.outputs["Points"], go.inputs[0])
    _PTS_NG = ng
    return ng


_MESHES: dict = {}


def load_mesh(key: str, points_only: bool):
    me = _MESHES.get(key)
    if me is not None:
        return me
    d = np.load(REC / "meshes" / f"{key}.npz")
    pts = d["points"].astype(np.float32)
    tris = d["tris"].astype(np.int32)
    me = bpy.data.meshes.new(key)
    if len(pts):
        me.vertices.add(len(pts))
        me.vertices.foreach_set("co", pts.ravel())
    if len(tris) and not points_only:
        me.loops.add(len(tris) * 3)
        me.loops.foreach_set("vertex_index", tris.ravel())
        me.polygons.add(len(tris))
        me.polygons.foreach_set("loop_start", np.arange(0, len(tris) * 3, 3, dtype=np.int32))
    me.update(calc_edges=True)
    if len(tris) and not points_only:
        try:
            me.set_sharp_from_angle(angle=math.radians(FEATURE_ANGLE))
        except Exception:
            pass
        me.shade_smooth()
        if "rgb" in d.files:
            rgb = srgb_to_lin(d["rgb"].astype(np.float32) / 255.0)
            ca = me.color_attributes.new("rgb", "FLOAT_COLOR", "POINT")
            ca.data.foreach_set("color", np.c_[rgb, np.ones(len(rgb))].astype(np.float32).ravel())
    _MESHES[key] = me
    return me


# ============================================================================================ the record
def record_done() -> bool:
    log = REC / "record.log"
    return (REC / "done").exists() or (log.exists() and "RECORD EXIT" in log.read_text()[-4000:])


def stream():
    """The record's snaps, as org_photo.py record appends them (it may still be running): each with `rep`, the first
    snap of the run of identical snaps it belongs to (nothing changed, the camera the same), whose PNG it shares."""
    fh = open(REC / "snaps.jsonl")
    prev_key, rep, buf = None, None, ""
    while True:
        line = fh.readline()
        if line:
            buf += line
            if not buf.endswith("\n"):
                continue
            s = json.loads(buf)
            buf = ""
            key = (json.dumps(s["cam"]), s["va"])
            if s["ch"] or key != prev_key or rep is None:
                rep = s["s"]
            prev_key = key
            s["rep"] = rep
            yield s
            continue
        if record_done():
            line = fh.readline()
            if not line:
                return
            buf += line
            continue
        time.sleep(2.0)


def wanted(s: int, pass_i: int) -> bool:
    sel = os.environ.get("PHOTO_SNAPS")
    if sel:
        if pass_i:
            return False
        for part in sel.split(","):
            if ":" in part:
                a = [int(v) if v else None for v in part.split(":")]
                lo, hi, st = (a + [None, None, None])[:3]
                if (lo or 0) <= s < (hi if hi is not None else 10 ** 9) and (s - (lo or 0)) % (st or 1) == 0:
                    return True
            elif int(part) == s:
                return True
        return False
    stride = int(os.environ.get("PHOTO_STRIDE", "2"))     # pass 0: every `stride`-th snap; pass 1: the rest
    return (s % stride == 0) if pass_i == 0 else (s % stride != 0)


class Lab:
    """The Blender side of the scene: one object per actor, updated from the record's deltas."""

    def __init__(self, sc, cam):
        self.sc, self.cam = sc, cam
        self.objs: dict[int, bpy.types.Object] = {}
        self.applied: dict[int, dict] = {}
        self.info: list = []
        self.kind: dict[int, tuple] = {}
        self.lit = False

    def actor(self, k):
        for _ in range(30):
            if k < len(self.info):
                return self.info[k]
            self.info = json.loads((REC / "actors.json").read_text())
            if k < len(self.info):
                return self.info[k]
            time.sleep(1.0)
        raise RuntimeError(f"actor {k} isn't in actors.json")

    def lights(self, st0):
        lo, hi = np.array([-6.0, -6.0, 0.0]), np.array([6.0, 6.0, 0.0])
        pts = []
        for k, c in st0.items():
            if "floor" in self.actor(k)["name"] and c.get("mesh") and c.get("v"):
                p = np.load(REC / "meshes" / f"{c['mesh']}.npz")["points"]
                if len(p):
                    m = np.array(c["m"], float).reshape(4, 4)
                    pts.append((np.c_[p, np.ones(len(p))] @ m.T)[:, :3] * MM)
        if pts:
            q = np.vstack(pts)
            lo, hi = q.min(0), q.max(0)
        add_lights(self.sc, ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0.0),
                   (max(hi[0] - lo[0], 4.0), max(hi[1] - lo[1], 4.0)))
        self.lit = True

    def push(self, target: dict, s: dict):
        sc, S = self.sc, Matrix.Scale(MM, 4)
        if not self.lit:
            self.lights(target)
        for k, ob in self.objs.items():            # an actor that doesn't exist yet at this snap (a later pass, rewound)
            if k not in target and not ob.hide_render:
                ob.hide_render = True
                self.applied[k] = {}
        for k, st in target.items():
            prev = self.applied.setdefault(k, {})
            if prev == st:
                continue
            a = self.actor(k)
            vis = st.get("v", False) and st.get("mesh") is not None and (st.get("o", 1.0) > 0.01)
            ob = self.objs.get(k)
            if vis and ob is None:
                me = load_mesh(st["mesh"], a["points"])
                ob = self.objs[k] = bpy.data.objects.new(f"a{k:05d}", me)
                sc.collection.objects.link(ob)
                kind = "metal" if a["shine"] >= 0.65 else "dielectric"
                if "floor" in a["name"]:
                    kind = "floor"
                vcol = "rgb" in np.load(REC / "meshes" / f"{st['mesh']}.npz").files
                mat = material(kind, a["shine"], vcol=vcol)
                if not me.materials:
                    me.materials.append(mat)
                ob["emit"] = 0.0
                self.kind[k] = (kind, a["shine"], vcol)
                if a["points"]:
                    mod = ob.modifiers.new("pts", "NODES")
                    mod.node_group = points_group()
                prev = self.applied[k] = {"mesh": st["mesh"]}
            if ob is None:
                self.applied[k] = dict(st)
                continue
            if not vis:
                if not ob.hide_render:
                    ob.hide_render = True
                self.applied[k] = dict(st)
                continue
            if ob.hide_render:
                ob.hide_render = False
            if st.get("mesh") != prev.get("mesh"):
                me = load_mesh(st["mesh"], a["points"])
                if not me.materials:
                    kind, shine, vcol = self.kind[k]
                    me.materials.append(material(kind, shine, vcol=bool(vcol)))
                ob.data = me
            if st.get("m") != prev.get("m") and st.get("m"):
                m = st["m"]
                ob.matrix_world = S @ Matrix([m[0:4], m[4:8], m[8:12], m[12:16]])
            if st.get("c") != prev.get("c") or st.get("o") != prev.get("o"):
                r, g, b = srgb_to_lin(st.get("c", (0.8, 0.8, 0.8)))
                o = float(min(1.0, st.get("o", 1.0)))
                # see-through parts (the VLM's cladding, ghosted shells) are glass: they cast no shadow, so what is
                # behind them is lit as in the VTK clip, and their veil is thinner (with every layer of the cladding
                # lit, the trays behind it read through a white haze)
                ghost = o < 0.5
                if ob.visible_shadow == ghost:
                    ob.visible_shadow = not ghost
                ob.color = (float(r), float(g), float(b), o * GHOST if ghost else o)
            if st.get("a") != prev.get("a"):
                amb = st.get("a", 0.22)
                e = 0.0 if amb <= 0.35 else (amb - 0.35) / 0.65 * 6.0
                if a["diffuse"] <= 0.05:
                    e = max(e, 4.0)
                ob["emit"] = float(e)
                ob.update_tag()
            self.applied[k] = dict(st)
        # points: the radius VTK drew them at on screen, at the camera's distance
        pos = np.array(s["cam"][0], float)
        fh = 2.0 * math.tan(math.radians(s["va"]) / 2.0) / H * (H / 720.0)
        for k, ob in self.objs.items():
            if self.actor(k)["points"] and not ob.hide_render:
                c = np.array(ob.matrix_world.translation) / MM
                r = max(0.4, 0.5 * self.actor(k)["point_size"] * fh * np.linalg.norm(pos - c))      # mm
                mod = ob.modifiers["pts"]
                ident = [it.identifier for it in mod.node_group.interface.items_tree
                         if getattr(it, "in_out", "") == "INPUT" and it.name == "Radius"][0]
                if mod.get(ident) != r:
                    mod[ident] = float(r)
                    ob.update_tag()
        # the camera
        p = np.array(s["cam"][0], float) * MM
        f = np.array(s["cam"][1], float) * MM
        up = np.array(s["cam"][2], float)
        fwd = (f - p) / np.linalg.norm(f - p)
        right = np.cross(fwd, up)
        right /= np.linalg.norm(right)
        upp = np.cross(right, fwd)
        self.cam.matrix_world = Matrix([[right[0], upp[0], -fwd[0], p[0]], [right[1], upp[1], -fwd[1], p[1]],
                                        [right[2], upp[2], -fwd[2], p[2]], [0, 0, 0, 1]])
        self.cam.data.angle = math.radians(s["va"])


def main():
    sc, cam = setup()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    lab = Lab(sc, cam)
    t_start, n_done = time.time(), 0
    deadline = float(os.environ.get("PHOTO_DEADLINE", "0"))      # unix time: stop starting new renders after it
    sel = os.environ.get("PHOTO_SNAPS")
    sel_max = max(int(v) for v in sel.replace(":", ",").split(",") if v) if sel else None
    for pass_i in range(1 if sel else 2):
        target: dict[int, dict] = {}
        for s in stream():
            for k, d in s["ch"].items():
                target.setdefault(int(k), {}).update(d)
            if not wanted(s["s"], pass_i):
                if sel_max is not None and s["s"] >= sel_max:
                    break
                continue
            png = OUTDIR / f"{s['rep']:05d}.png"
            if png.exists():
                continue
            if deadline and time.time() > deadline:
                print(f"render: deadline reached; {n_done} snaps in {time.time() - t_start:.0f} s", flush=True)
                return
            t0 = time.time()
            lab.push(target, s)
            sc.render.filepath = str(png)
            bpy.ops.render.render(write_still=True)
            n_done += 1
            el = time.time() - t_start
            print(f"render: pass {pass_i}, snap {s['s']} as {s['rep']} (frame {s['n0']}), {time.time() - t0:.1f} s; "
                  f"{n_done} done, {el / n_done:.1f} s each", flush=True)
    print(f"render: {n_done} snaps in {time.time() - t_start:.0f} s", flush=True)


if __name__ == "__main__":
    main()
