"""All the PNGs in ../renders: a contact sheet per group, the sandbox scene, and the room."""
from __future__ import annotations

import math

import numpy as np
import pyvista as pv

import sandbox
import vendor
from common import MATERIALS, RENDERS, Model
from piper_pose import Piper
from render import BG, add_floor, add_model, caption, contact_sheet, plotter, render, view

TILES = RENDERS / "tiles"


def _grams(m: Model) -> str:
    bb = m.bbox()
    return f"{bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm"


SHEETS = {
    "labware_tier1": (("tier1",), 5, "Sandbox objects: Tier 1 core set (docs/sandbox-object-set.md)"),
    "labware_tier2": (("tier2", "extra"), 6, "Sandbox objects: Tier 2 and common extras"),
    "sandbox_stations": (("station",), 4, "Sandbox stations and printed holders"),
}


def labware_sheet(cat: dict[str, Model]) -> None:
    for name, (groups, cols, title) in SHEETS.items():
        tiles = []
        for key, m in cat.items():
            if m.notes.get("group") not in groups:
                continue
            out = render([m], TILES / f"{key}.png", size=(700, 560), zoom=1.05)
            src = "lab CAD" if "lab CAD" in m.source else "ours" if "our design" in m.source else "assumed" if \
                "assumed" in m.source else "from specs"
            tiles.append((out, m.title if len(m.title) < 44 else key, f"{_grams(m)}  ·  {src}"))
        contact_sheet(tiles, RENDERS / f"{name}.png", cols=cols, tile_w=420, title=title,
                      sub="Overall size W x D x H. 'from specs' = datasheet dims; 'lab CAD' = the #222 / PR #232 STEP; "
                          "'ours' = printed holders designed here; 'assumed' = rough")


def equipment_sheet(eq: dict[str, Model]) -> dict[str, Model]:
    allm = dict(eq)
    for f in (vendor.ot2, vendor.piper):
        m = f()
        allm[m.key] = m
    order = ["bambu_a1_mini", "bambu_h2d", "opentrons_ot2", "agilex_piper", "cubxl", "lansmont_m23_drop_tower",
             "amazemet_repowder", "labconco_glovebox", "mse_pro_glovebox", "aconity_midi"]
    views = {"aconity_midi": (-0.8, -1.2, 0.55)}      # from the left, where its filter unit stands
    tiles = []
    for key in order:
        if key not in allm:
            continue
        m = allm[key]
        d = views.get(key, (0.75, -1.25, 0.6))
        out = render([m], TILES / f"{key}.png", size=(900, 900), direction=d)
        render([m], RENDERS / f"{key}.png", size=(1400, 1200), direction=d, title=m.title)
        src = "vendor STEP" if "STEP" in m.source and "lab" not in m.source else "rough, from specs"
        tiles.append((out, m.title, f"{_grams(m)}  ·  {src}"))
    contact_sheet(tiles, RENDERS / "equipment_sheet.png", cols=4, tile_w=480, title="Lab equipment",
                  sub="Vendor STEP where it exists (OT-2: Opentrons; PiPER: AgileX); the rest modelled from specs, drawings and photos")
    return allm


def _piper_actor(pl: pv.Plotter, q, grip: float) -> None:
    arm = Piper()
    base = np.eye(4)
    base[2, 3] = 12.0            # on the 12 mm arm plate
    for mesh, mat in arm.meshes(q, grip, base):
        r, g, b, a, spec = MATERIALS[mat]
        pl.add_mesh(mesh, color=(r, g, b), specular=spec, specular_power=30, smooth_shading=True,
                    split_sharp_edges=True)


def sandbox_scene(cat: dict[str, Model]) -> None:
    import cadquery as cq
    scene = sandbox.layout(cat, with_vendor=False)
    tabletop = Model("t", "t")
    tabletop.parts = [p for p in scene.parts if not p.name.startswith("table - leg")]
    arm = Piper()
    # the arm has the first charge cup (holder at (0, -400), cup at (-48, +18) in it) between its fingers
    target = (-48.0, -382.0, 60.0)
    q, err = arm.ik_down(target, yaw=math.pi / 2)
    bb = cq.Compound.makeCompound([p.shape for p in tabletop.parts]).BoundingBox()
    for name, direction, zoom, size, up in (("sandbox_scene", (0.9, -1.25, 0.95), 1.5, (1800, 1250), (0, 0, 1)),
                                            ("sandbox_top", (0.0, 0.0, 1.0), 1.25, (1500, 1500), (0, 1, 0))):
        pl = plotter(size)
        add_model(pl, tabletop)
        _piper_actor(pl, q, 0.0115)
        if name == "sandbox_top":      # fingertip reach (0.77 m, #229) and the J1 dead zone on the -x side
            ring = pv.Disc(center=(0, 0, 1.0), inner=765, outer=775, c_res=180)
            pl.add_mesh(ring, color=(0.2, 0.45, 0.85), lighting=False)
            angs = np.radians(np.linspace(150, 210, 40))
            pts = np.vstack([[0, 0, 1.2]] + [[770 * math.cos(a), 770 * math.sin(a), 1.2] for a in angs])
            wedge = pv.PolyData(pts, faces=np.hstack([[3, 0, i, i + 1] for i in range(1, len(pts) - 1)]))
            pl.add_mesh(wedge, color=(0.90, 0.45, 0.25), opacity=0.35, lighting=False)
            pl.enable_parallel_projection()
        add_floor(pl, bb, z=-26.0)
        s = max(bb.xlen, bb.ylen)
        pl.enable_ssao(radius=s / 60, bias=0.5, kernel_size=64)
        pl.enable_anti_aliasing("ssaa")
        view(pl, bb, direction, zoom, up=up)
        out = RENDERS / f"{name}.png"
        pl.screenshot(str(out))
        pl.close()
        caption(out, "PiPER sandbox on spot D (1.29 x 1.36 m)" if name == "sandbox_scene" else "Sandbox, top view",
                f"Arm posed by IK over the first charge cup (fingertip error {err:.1f} mm). Holders printed in PETG, "
                "A1 mini bed run forward" if name == "sandbox_scene" else
                "Blue ring: 0.77 m fingertip reach (#229). Orange wedge: J1 stops at +-150 deg, so nothing sits there")


def glovebox_fit(gb: Model, hr: Model) -> None:
    """The HR-100A on the glove box floor, with the shell drawn clear, to see the room left for the doser."""
    from common import Part
    x, y, z = gb.notes["floor_centre_mm"]
    clear = {"body": "acrylic", "control column": "acrylic", "window frame": "acrylic"}
    box_ = Model("glovebox_fit", gb.title)
    box_.parts = [Part(p.name, p.shape, clear.get(p.name, p.material)) for p in gb.parts
                  if not p.name.startswith(("glove 1", "glove 2", "stand", "caster", "vacuum pump"))]
    bal = hr.moved(x, y + 60.0, z)
    out = render([box_, bal], RENDERS / "glovebox_fit.png", size=(1500, 1150), direction=(0.3, -1.0, 1.1),
                 bounds_of=[box_])
    caption(out, "HR-100A on the Labconco glove box floor (shell drawn clear)", gb.notes.get("fit_note", ""))


def balance_lids(hr: Model) -> None:
    """The HR-100A twice: with the AutoTrickler V4 lid the doser runs, and with A&D's own lid."""
    import labware
    stock = labware.balance("stock")
    gap = 300.0
    out = render([hr.moved(-gap / 2), stock.moved(gap / 2)], RENDERS / "balance_hr100a_lids.png", size=(1600, 1000),
                 direction=(0.35, -1.3, 0.9), zoom=1.05)
    caption(out, "HR-100A breeze break lids: AutoTrickler V4 (left, as the doser runs it) and A&D's own (right)",
            "Both sit on the same four FXi-10 posts, so they swap. The panel's 46 mm hole is 24 mm behind the pan centre, "
            "under the doser's outlet; A&D's lid has a 28 mm centre opening.")


def mse_fit(gb: Model, hr: Model) -> None:
    """The HR-100A on the MSE box's floor, gone in through the 400 mm side door."""
    x, y, z = gb.notes["floor_centre_mm"]
    bal = hr.moved(x - 150.0, y, z)
    out = render([gb, bal], RENDERS / "mse_glovebox_fit.png", size=(1500, 1100), direction=(0.45, -1.0, 0.75),
                 bounds_of=[gb])
    caption(out, "HR-100A inside the MSE PRO acrylic box", gb.notes.get("fit_note", ""))


def all_renders(cat: dict[str, Model], eq: dict[str, Model], room_model: Model | None = None) -> None:
    RENDERS.mkdir(exist_ok=True)
    labware_sheet(cat)
    render([cat["holder_charge"]], RENDERS / "holder_charge.png", size=(1400, 1000), title=cat["holder_charge"].title)
    render([cat["holder_vial_20ml"]], RENDERS / "holder_vial_20ml.png", size=(1400, 1000), title=cat["holder_vial_20ml"].title)
    hr = cat["balance_hr100a"]
    render([hr], RENDERS / "balance_hr100a.png", size=(1400, 1200), direction=(0.8, -1.3, 0.75), title=hr.title)
    balance_lids(hr)
    if "labconco_glovebox" in eq:
        glovebox_fit(eq["labconco_glovebox"], hr)
    if "mse_pro_glovebox" in eq:
        mse_fit(eq["mse_pro_glovebox"], hr)
    equipment_sheet(eq)
    sandbox_scene(cat)
    if room_model is not None:
        import room
        room.render_room(room_model)
