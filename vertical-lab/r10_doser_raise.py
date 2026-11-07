"""Round 10, the doser: can the vessel be raised so the auger's outlet is closer? Measured on v5's own geometry.

Sterling on PR #318 (2026-11-07): "did you get latest multi-doser with the scale? Note the comment about raising the cup
on a platform of sorts so that the nozzle is closer, but we might end up needing to use a funnel anyway." His comment
on powder-doser PR #185 (2026-11-05 17:52): "if we have a shorter scale or want to get it closer to the dispense point,
we just raise the scale up on some kind of block (e.g., granite block)".

    python3 r10_doser_raise.py                     # measurements -> out/doser_raise.json, section -> out/doser_raise_section.png
    python3 r10_doser_raise.py sweep               # FCL: the shuttle with vessel and funnel along its travel and at the dose
    xvfb-run -a python3 r10_doser_raise.py stills  # 3D stills of the funnel option -> out/doser_raise_{cup,vial}.png

Everything is read from the copies of powder-doser's v5 at 353dae7 (``carousel.CL``/``CP``, the tessellated parts) and
from our own parts in ``carousel.py``. Rig frame: x along the augers (the balance's display at -x), y along the loop, z
up from the bench, mm.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import carousel as C        # noqa: E402

CL, CP = C.CL, C.CP
OUT = HERE / "out"
EXIT_Z = float(CL.exit_point(C.TILT)[2])          # 435.8: on the hinge axis, the same at every tilt
PX, PY = (float(v) for v in C.PAN_XY)
VIAL_MOUTH_D = 2 * (14.0 - 1.2)                   # props.VIAL_R - VIAL_WALL: the model vial's mouth, 25.6 mm
CUP_BORE = 12.7                                   # charge.CUP_BORE_D (1/2 in)
STREAM_D = 8.0                                    # v5's check_stream column
FUNNEL_CONE_D = 40.0                              # charge.FUNNEL cone_r 20
GAP_TARGET = 5.0                                  # "within a few mm" of the outlet


def placed(st, parts):
    """[(key, module, world points)] of every drawn instance in state `st`."""
    out = []
    for p in C.lowered(CL.placements(st)):
        if p.key in C.SKIP:
            continue
        out.append((p.key, p.module, parts[p.key].points @ p.M[:3, :3].T + p.M[:3, 3]))
    return out


def lowest_over(items, box, z_from=100.0, skip=("hr202i",)):
    """The lowest point of any part (not the balance) inside the plan box (x0, x1, y0, y1) above z_from."""
    x0, x1, y0, y1 = box
    best = (1e9, "", -1)
    for k, m, pts in items:
        if k.startswith(skip):
            continue
        sel = (pts[:, 0] > x0) & (pts[:, 0] < x1) & (pts[:, 1] > y0) & (pts[:, 1] < y1) & (pts[:, 2] > z_from)
        if sel.any():
            z = float(pts[sel, 2].min())
            if z < best[0]:
                best = (z, k, m)
    return best


def measure() -> dict:
    parts = C.part_meshes()
    parked = placed(CL.State(ext=0.0, beaker=False), parts)
    dose = placed(CL.State(ext=C.DOCK_EXT, tilt=C.TILT, top_door=C.TOP_OPEN, side_door=C.SIDE_OPEN, beaker=False), parts)
    bal = np.vstack([pts for k, _, pts in parked if k.startswith("hr202i")])
    blo, bhi = bal.min(0), bal.max(0)
    top_grip = float(bhi[2])
    plan = (blo[0], bhi[0], blo[1], bhi[1])
    z_park, k_park, _ = lowest_over(parked, plan)
    z_dose, k_dose, _ = lowest_over(dose, plan)
    # the column a vessel could rise into over the pan, at the dose and parked
    col = {}
    for name, items in (("parked", parked), ("dose", dose)):
        for r in (14.0, 20.0):
            z, k, _ = lowest_over(items, (PX - r, PX + r, PY - r, PY + r), z_from=200.0)
            col[f"{name}_r{int(r)}"] = dict(z=round(z, 1), part=k)
    chamber_ceiling = float(CP.HR2_PAN_TOP + CP.HR2_CH[2])
    door_top = C.DOOR_TOP_Z
    v = dict(vial=dict(h=C.VIAL_H, d=2 * C.VIAL_R, mouth_d=VIAL_MOUTH_D), cup=dict(h=C.CUP_L, d=C.CUP_D, mouth_d=CUP_BORE))
    as_built, funnel = {}, {}
    for kind, d in v.items():
        rim = C.SEAT_Z + d["h"]
        as_built[kind] = dict(rim_z=round(rim, 1), fall_mm=round(EXIT_Z - rim, 1), carried_rim_z=round(rim + C.SEAT_LIFT, 1),
                              under_door_top_mm=round(door_top - rim - C.SEAT_LIFT, 1),
                              stream_margin_each_side_mm=round((d["mouth_d"] - STREAM_D) / 2, 2),
                              block_for_rim_within_5mm=round(EXIT_Z - GAP_TARGET - rim, 1))
        rim_f = C.SEAT_Z_FUNNEL + d["h"]
        tip = float(C.funnel_tip_at(0.0, 1.0)[2])
        funnel[kind] = dict(seat_z=C.SEAT_Z_FUNNEL, rim_z=round(rim_f, 1), funnel_tip_over_rim_mm=round(tip - rim_f, 1),
                            funnel_rim_z=round(tip + C.FUNNEL_H, 1), fall_onto_cone_mm=round(EXIT_Z - tip - C.FUNNEL_H, 1),
                            carried_funnel_rim_z=round(float(C.funnel_tip_at(0.0, 0.0)[2]) + C.FUNNEL_H, 1),
                            cone_margin_each_side_mm=round((FUNNEL_CONE_D - STREAM_D) / 2, 1))
    # what a block of the height the cup needs would run into: the balance raised B mm, its outline vs the station at the dose
    B = as_built["cup"]["block_for_rim_within_5mm"]
    hits = sorted({k for k, m, pts in dose if not k.startswith("hr202i")
                   and ((pts[:, 0] > blo[0]) & (pts[:, 0] < bhi[0]) & (pts[:, 1] > blo[1]) & (pts[:, 1] < bhi[1])
                        & (pts[:, 2] < top_grip + B)).any()})
    import vlm
    rig_h = C.TOP_Z + 3.0                          # the top panel on the rails (lowered): 854
    out = dict(
        source="powder-doser chain-carousel-v5 at 353dae7 (PR #185 head on 2026-11-07), copied in multidoser/; "
               "our pedestal, shuttle and funnel option in carousel.py",
        exit_z=round(EXIT_Z, 1), exit_xy=[round(float(c), 1) for c in CL.exit_point(C.TILT)[:2]],
        pan_xy=[round(PX, 1), round(PY, 1)], pan_top_z=C.PAN_TOP,
        balance=dict(model="A&D HR-202i (220 g x 0.1 mg)", body_h=CP.HR2_H, overall_h=CP.HR2_H_ALL,
                     top_door_grip_z=round(top_grip, 1), chamber_inside_wdh=list(CP.HR2_CH),
                     chamber_ceiling_z=chamber_ceiling, side_door_opening_z=[C.DOOR_SILL_Z, door_top],
                     side_door_opening_x=[round(x, 1) for x in C.DOOR_X], top_door_opening_xy=list(CP.HR2_TOP_DOOR),
                     capacity_g=CP.HR2_CAP_G),
        over_the_balance=dict(parked=dict(z=round(z_park, 1), part=k_park), dose_30deg=dict(z=round(z_dose, 1), part=k_dose),
                              column_over_pan=col),
        block=dict(room_under_parked_ec_mm=round(z_park - top_grip, 1), v5_keeps_mm=CP.HR2_TOP_GAP,
                   max_block_mm=round(max(0.0, z_park - top_grip - CP.HR2_TOP_GAP), 1),
                   cup_needs_mm=B, balance_top_then_z=round(top_grip + B, 1), parts_in_the_way_at_the_dose=hits,
                   tray_b=dict(rig_h=rig_h, shuttle_goods_h=round(float(vlm.MAX_GOODS_H), 1),
                               room_to_raise_rig_mm=round(float(vlm.MAX_GOODS_H) - rig_h, 1))),
        as_built=as_built, funnel_option=funnel,
        pan_load_g=dict(cu_cup_topped_up=135.7, al_cup_topped_up=round(32.08 + 3.92 + 3.91, 2),
                        pedestal_as_built_est=27.0, pedestal_funnel_option_est=20.0,
                        note="cups: out/alloy_recipe.json and alloy_recipe_pressed.json (cup + both layers, no plug); "
                             "pedestals estimated from v5's riser (about 30 g at 194 mm, parts5.beaker_riser) by height"),
        stream=dict(column_d=STREAM_D, exit_to_pan_axis_mm=round(float(np.hypot(*(CL.exit_point(C.TILT)[:2] - C.PAN_XY))), 2),
                    note="v5's check_stream: an 8 mm column from the exit to the rim is clear at 45 deg, a 0.4 mm3 graze "
                         "of the module's own outlet face at 30 deg; strays over a ~150 mm fall are powder-doser's T8b"),
    )
    return out


# ------------------------------------------------------------------------------------------- the section (matplotlib)
def section(m: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pyvista as pv
    from matplotlib.patches import Rectangle, Polygon
    parts = C.part_meshes()
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 8.0), sharey=True)
    states = (("As built (rounds 9-10): the vessel on our pedestal, no funnel", None),
              ("The funnel option: the powder's funnel on the shuttle's upper tine", "funnel"))
    ink, rig_c, bal_c, ours_c = "#222222", "#6b6f76", "#9aa3ad", "#178c8c"
    for ax, (title, opt) in zip(axes, states):
        st = CL.State(ext=C.DOCK_EXT, tilt=C.TILT, top_door=C.TOP_OPEN, side_door=0.0, beaker=False)
        for k, mod, pts in []:
            pass
        for p in C.lowered(CL.placements(st)):
            if p.key in C.SKIP:
                continue
            mesh = parts[p.key].copy()
            mesh.points = mesh.points @ p.M[:3, :3].T + p.M[:3, 3]
            b = mesh.bounds
            if not (b[2] <= PY <= b[3]) or b[4] > 520 or b[1] < -160 or b[0] > 330:
                continue
            sl = mesh.slice(normal="y", origin=(0, PY, 0))
            if sl.n_points == 0:
                continue
            lines = sl.lines.reshape(-1, 3)[:, 1:] if sl.lines.size else np.zeros((0, 2), int)
            col = bal_c if p.key.startswith("hr202i") else rig_c
            lw = 0.6
            if p.key in ("sam_electronics_carriage", "nema11", "solenoid"):
                col, lw = "#c0392b", 0.8
            segs = sl.points[lines]
            for s in segs:
                ax.plot(s[:, 0], s[:, 2], color=col, lw=lw, solid_capstyle="round")
        # ours: pedestal, vessel, funnel
        sz = C.SEAT_Z if opt is None else C.SEAT_Z_FUNNEL
        ped = C.seat_mesh(seat_z=sz).slice(normal="y", origin=(0, PY, 0))
        for s in ped.points[ped.lines.reshape(-1, 3)[:, 1:]]:
            ax.plot(s[:, 0], s[:, 2], color=ours_c, lw=1.2)
        for kind, h, d, dx, ls in (("cup", C.CUP_L, C.CUP_D, 0.0, "-"),):
            ax.add_patch(Rectangle((PX - d / 2, sz), d, h, fill=False, ec="#b87333", lw=1.6, ls=ls))
            ax.add_patch(Rectangle((PX - CUP_BORE / 2, sz + h - 47.6), CUP_BORE, 47.6, fill=False, ec="#b87333", lw=0.8))
        if opt:
            tip = float(C.funnel_tip_at(0.0, 1.0)[2])
            f = C.FUNNEL_H
            poly = [(PX - 4.5, tip), (PX - 4.5, tip + 12), (PX - 14, tip + 12), (PX - 14, tip + 14), (PX - 21.4, tip + f - 6),
                    (PX - 21, tip + f), (PX + 21, tip + f), (PX + 21.4, tip + f - 6), (PX + 14, tip + 14), (PX + 14, tip + 12),
                    (PX + 4.5, tip + 12), (PX + 4.5, tip)]
            ax.add_patch(Polygon(poly, closed=True, fill=False, ec=ours_c, lw=1.6))
            # the shuttle stays in while it doses: the upper tine under the funnel's flange, the fork 4 mm under the
            # vessel's foot (both cut across here: each is two tines round a slot, running out along -y)
            for z1, slot in ((tip + 12, C.TINE_SLOT_W), (sz - (C.FORK_DROP - C.SEAT_LIFT), C.SLOT_W)):
                for sx in (-1, 1):
                    a, b = sorted((PX + sx * slot / 2, PX + sx * C.FORK_W / 2))
                    ax.add_patch(Rectangle((a, z1 - C.FORK_T), b - a, C.FORK_T, fc=ours_c, ec="none", alpha=0.8))
            ax.text(PX - 24, tip + 8, "upper tine", fontsize=7.5, color=ours_c, ha="right", va="center")
            ax.text(PX - 24, sz - 8, "fork, 4 mm under the foot", fontsize=7.5, color=ours_c, ha="right", va="center")
            land = tip + f
        else:
            land = sz + C.CUP_L
        # the stream
        ax.add_patch(Rectangle((PX - STREAM_D / 2, land), STREAM_D, EXIT_Z - land, fc="#d4a017", ec="none", alpha=0.45))
        ax.plot([PX], [EXIT_Z], marker="v", color="#d4a017", ms=9, mec=ink)
        # the gaps
        def dim(z0, z1, x, text, side=1):
            ax.annotate("", xy=(x, z0), xytext=(x, z1), arrowprops=dict(arrowstyle="<->", color=ink, lw=0.9))
            ax.text(x + side * 4, (z0 + z1) / 2, text, fontsize=8.5, ha="left" if side > 0 else "right", va="center",
                    color=ink)
        dim(land, EXIT_Z, PX - 70, f"{EXIT_Z - land:.0f} mm\nfall", side=-1)
        bt = m["balance"]["top_door_grip_z"]
        zp = m["over_the_balance"]["parked"]["z"]
        ax.axhline(C.DOOR_TOP_Z, color=bal_c, lw=0.8, ls="--")
        ax.text(-150, C.DOOR_TOP_Z + 2, f"side door opening's top {C.DOOR_TOP_Z:.0f}", fontsize=8, color="#555")
        ax.axhline(zp, color="#c0392b", lw=0.8, ls=":")
        ax.text(-150, zp + 2, f"EC parked: its underside {zp:.1f}, {zp - bt:.1f} mm over the balance's top ({bt:.0f})",
                fontsize=8, color="#c0392b")
        ax.text(-150, EXIT_Z + 50, f"auger exit {EXIT_Z:.1f}\n(on the hinge axis, every tilt);\nthe EC docked, 30° (red)",
                fontsize=8, color="#8a6d0b")
        if opt:
            tip = float(C.funnel_tip_at(0.0, 1.0)[2])
            ax.text(PX + 26, tip + 18, f"powder's own funnel\n(40 mm cone), stem\n{tip - (sz + C.CUP_L):.0f} mm over "
                                       f"the bore", fontsize=8, color=ours_c, va="center")
            ax.text(PX + 26, sz + 25, f"cup on a shorter\npedestal (top {sz:.1f})", fontsize=8, color="#b87333")
        else:
            ax.text(PX + 14, sz + 25, f"cup on our pedestal\n(top {sz:.0f}), rim {sz + C.CUP_L:.1f},\n12.7 mm bore",
                    fontsize=8, color="#b87333")
        ax.set_title(title, fontsize=10.5)
        ax.set_xlim(-160, 330)
        ax.set_ylim(0, 520)
        ax.set_aspect("equal")
        ax.set_xlabel("x along the augers, mm (rig frame; section through the pan's centre)")
        ax.grid(alpha=0.15)
    axes[0].set_ylabel("height over the bench, mm")
    fig.suptitle("Multi-doser v5 (powder-doser 353dae7) on the HR-202i at the 30° dose: why a block can't raise the cup, "
                 "and the funnel", fontsize=11.5)
    fig.text(0.5, 0.012, f"A block under the balance has {m['block']['room_under_parked_ec_mm']} mm before the "
             f"balance's top meets the parked EC (v5 keeps 10 mm; on tray B the rig is {m['block']['tray_b']['rig_h']:.0f} "
             f"of the Shuttle's {m['block']['tray_b']['shuttle_goods_h']} mm). Bringing the cup's rim within 5 mm of the "
             f"exit would take {m['block']['cup_needs_mm']} mm.", ha="center", fontsize=8.8)
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    fig.savefig(path, dpi=110)
    plt.close(fig)


# ------------------------------------------------------------------------------------------- the FCL sweep
def sweep() -> dict:
    import trimesh
    import pyvista as pv
    import charge
    parts = C.part_meshes()

    def tm(poly):
        p = poly.triangulate()
        return trimesh.Trimesh(p.points.copy(), p.faces.reshape(-1, 4)[:, 1:].copy(), process=False)

    def rig_manager(st, extra=()):
        cm = trimesh.collision.CollisionManager()
        for i, p in enumerate(C.lowered(CL.placements(st))):
            if p.key in C.SKIP or p.key.startswith("door_spring"):
                continue
            cm.add_object(f"{p.key}#{i}", tm(parts[p.key]), transform=p.M)
        for name, mesh in extra:
            cm.add_object(name, tm(mesh))
        return cm

    pm = C.pusher_meshes()
    sm = C.shuttle_meshes(C.SEAT_Z_FUNNEL, tine=True)
    fixed = [("seat", C.seat_mesh(seat_z=C.SEAT_Z_FUNNEL)), ("shuttle_rail", sm["fixed"]),
             ("side_rail", pm["side_rail"]), ("top_rail", pm["top_rail"])]
    fn = charge.funnel()["body"].translate(C.funnel_tip_at(), inplace=False)
    import props
    vessels = {"cup": tm(charge.cup()), "vial": tm(props.vial_glass())}
    moving = {"fork": tm(sm["moving"]), "tine": tm(sm["tine"]), "funnel": tm(fn)}
    res = {}
    # 1. along the travel, side door open, top door shut, EC parked (the shuttle runs only then)
    cm = rig_manager(CL.State(ext=0.0, side_door=C.SIDE_OPEN, beaker=False),
                     fixed + [("side_finger", pm["side_finger"].translate((C.SIDE_OPEN, 0, 0), inplace=False)),
                              ("top_finger", pm["top_finger"])])
    for kind in ("cup", "vial"):
        hits = set()
        for s in np.linspace(0.0, 1.0, 41):
            for fk in (0.0,) if s > 0 else (0.0, C.SEAT_LIFT / C.FORK_DROP, 1.0):
                M = np.eye(4)
                M[:3, 3] = (0.0, -C.TRAVEL * s, -C.FORK_DROP * fk)
                for name, mesh in moving.items():
                    hit, names = cm.in_collision_single(mesh, transform=M, return_names=True)
                    if hit:
                        hits |= {f"{name}:{n}" for n in names}
                Mv = np.eye(4)
                Mv[:3, 3] = C.vessel_at(kind, s, fk, C.SEAT_Z_FUNNEL)
                hit, names = cm.in_collision_single(vessels[kind], transform=Mv, return_names=True)
                if hit:
                    hits |= {f"{kind}:{n}" for n in names if not (n == "seat" and fk >= C.SEAT_LIFT / C.FORK_DROP - 1e-6)}
        res[f"travel_{kind}"] = sorted(hits)
    # 2. at the dose: EC docked and tilted 30 deg, top door open, side door open, the shuttle in and dropped
    cm = rig_manager(CL.State(ext=C.DOCK_EXT, tilt=C.TILT, top_door=C.TOP_OPEN, side_door=C.SIDE_OPEN, beaker=False),
                     fixed)
    for kind in ("cup", "vial"):
        hits = set()
        M = np.eye(4)
        M[:3, 3] = (0.0, 0.0, -C.FORK_DROP)
        for name, mesh in moving.items():
            hit, names = cm.in_collision_single(mesh, transform=M, return_names=True)
            if hit:
                hits |= {f"{name}:{n}" for n in names}
        Mv = np.eye(4)
        Mv[:3, 3] = C.vessel_at(kind, 0.0, 1.0, C.SEAT_Z_FUNNEL)
        hit, names = cm.in_collision_single(vessels[kind], transform=Mv, return_names=True)
        hits |= {f"{kind}:{n}" for n in names if n != "seat"} if hit else set()
        # the funnel, tine and fork against the vessel itself (they must not touch it)
        vm = trimesh.collision.CollisionManager()
        vm.add_object(kind, vessels[kind], transform=Mv)
        for name, mesh in moving.items():
            d = vm.min_distance_single(mesh, transform=M)
            res[f"dose_{kind}_{name}_to_vessel_mm"] = round(float(d), 2)
        res[f"dose_{kind}"] = sorted(hits)
    return res


# ------------------------------------------------------------------------------------------- 3D stills
def stills() -> list[str]:
    import pyvista as pv
    import charge
    import props
    from scene import Scene
    from PIL import Image, ImageDraw
    import scene
    made = []
    for kind in ("cup", "vial"):
        sc = Scene(f"doser_raise_{kind}", "", gif=False, mp4=False)
        car = C.Carousel(sc, "rig", highlight=None, funnel=charge.FUNNEL_LABEL["Ni"])
        m = 5
        car.set(shift=car.index_to(m), ext=C.DOCK_EXT, tilt=C.TILT, top_door=C.TOP_OPEN, side_door=C.SIDE_OPEN,
                shuttle=0.0, fork=1.0)
        base = C.vessel_at(kind, 0.0, 1.0, C.SEAT_Z_FUNNEL)
        if kind == "cup":
            sc.add("v/cup", charge.cup(cut=True).translate(base, inplace=False), (0.72, 0.45, 0.20), "rig", specular=0.7)
            top = base[2] + charge.FLOOR_Z + 4.0
        else:
            sc.add("v/vial", props.vial_glass().translate(base, inplace=False), (0.85, 0.92, 0.95), "rig", opacity=0.35)
            top = base[2] + 6.0
        tip = C.funnel_tip_at(0.0, 1.0)
        land = tip[2] + C.FUNNEL_H - 8.0
        ex = car.exit_point()
        pts = []
        rng = np.random.default_rng(3)
        for z in np.linspace(land, ex[2] - 1.5, 60):
            pts.append((ex[0] + rng.normal(0, 1.2), ex[1] + rng.normal(0, 1.2), z))
        for z in np.linspace(top, tip[2], 14):
            pts.append((tip[0] + rng.normal(0, 0.6), tip[1] + rng.normal(0, 0.6), z))
        cloud = pv.PolyData(np.array(pts))
        sc.add("v/stream", cloud, (0.55, 0.55, 0.58), "rig", render_points_as_spheres=True, point_size=4.0)
        for n in car.glass:
            sc.base_alpha[n] = min(sc.base_alpha[n], 0.18)
        c = np.array([PX, PY, 300.0])
        sc.cam = [tuple(c + (-330.0, -520.0, 140.0)), tuple(c + (0, 0, -20)), (0, 0, 1)]
        sc.view_angle = 30.0
        img = Image.fromarray(sc.render_base())
        d = ImageDraw.Draw(img)
        f = scene.font(17)
        txt = (f"The funnel option, {kind}: the Ni module's own funnel on our shuttle's upper tine, its stem "
               f"{C.FUNNEL_GAP if kind == 'cup' else C.FUNNEL_GAP + C.CUP_L - C.VIAL_H:.1f} mm over the "
               f"{'12.7 mm bore' if kind == 'cup' else 'vial'}; the stream falls "
               f"{EXIT_Z - tip[2] - C.FUNNEL_H:.0f} mm onto its 40 mm cone")
        d.rectangle((0, img.size[1] - 34, img.size[0], img.size[1]), fill=(255, 255, 255))
        d.text((12, img.size[1] - 28), txt, fill=(20, 20, 20), font=f)
        path = OUT / f"doser_raise_{kind}.png"
        img.save(path)
        made.append(str(path.relative_to(HERE)))
        sc.pl.close()
    return made


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "measure"
    js = OUT / "doser_raise.json"
    if what == "measure":
        m = measure()
        if js.exists():
            old = json.loads(js.read_text())
            for k in ("sweep", "stills"):
                if k in old:
                    m[k] = old[k]
        js.write_text(json.dumps(m, indent=1))
        section(m, OUT / "doser_raise_section.png")
        print(json.dumps({k: m[k] for k in ("exit_z", "block", "as_built", "funnel_option")}, indent=1))
    elif what == "sweep":
        r = sweep()
        m = json.loads(js.read_text())
        m["sweep"] = r
        js.write_text(json.dumps(m, indent=1))
        print(json.dumps(r, indent=1))
    elif what == "stills":
        made = stills()
        m = json.loads(js.read_text())
        m["stills"] = made
        js.write_text(json.dumps(m, indent=1))
        print(made)
