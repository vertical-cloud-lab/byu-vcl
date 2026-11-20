"""The OT-2's deck as tray A carries it in the lab scenes (#303, PR #318, round 14).

Sterling, PR #318, 2026-11-20, of round 12's video: "The OT-2 is empty". Every scene that builds the lab
(animate.Lab, so the set-up movie, the services, hookups and bay-camera clips, the chapters' VLMs) drew Opentrons'
reference STEP with a bare deck; only the OT-2's own clip (ot2_corrosion.py) set out labware. This module puts that
clip's labware on the deck, at rest and without its moves, in the STEP's own frame, so animate.Lab can add it to the
OT-2's group with the same placement as the machine:

* slot 1: Opentrons 300 uL tips (the P300's, on the right mount), a full rack;
* slot 2: the printed tube block (ours) with the night's nine 0.5 mL PP tubes and two 1.5 mL tubes: the 10 mg/L
  sulfide stock and the 1 mg/L ICP-MS standard;
* slot 3: a 96-well 2 mL deep-well plate, where the OT-2 makes the 0.1 mg/L sulfide working stock and the 10x
  dilutions;
* slot 4: Opentrons 20 uL tips (the P20's, on the left mount);
* slot 5: a NEST 12-well 15 mL reservoir: 2 % HNO3, seawater (ASTM D1141 without the heavy metals) and the blank
  matrix, at the volumes the clip starts with (12, 12 and 10 mL).

Slots 6-11 stay free and 12 is the fixed trash, as in ot2_corrosion.py. Where each piece and volume comes from is in
that module's docstring (DAL alloy-corrosion/copper/protocol.md at aeda51a; digital-wetlab PR #83, direction 5). The
meshes are cached in .cache/ on this file, ot2_corrosion.py and lab_models/labware.py.

    python3 ot2_deck.py          # build (or load) the deck and print what is on it
"""
from __future__ import annotations

import hashlib
import pickle
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
sys.path.insert(0, str(HERE / "lab_models"))


def _shapes() -> list:
    """[(name, CadQuery shape, material)] of the labware on the deck, the OT-2 STEP's frame."""
    import cadquery as cq
    import labware
    import ot2_corrosion as OC
    dz = OC.OT2["deck_z"]
    out = []
    for slot, kind in ((1, "300ul"), (4, "20ul")):
        rack = OC._ot2_seat(labware.tiprack(kind), slot)
        out.append((f"{kind} tip rack (slot {slot})", rack.parts[0].shape, "pp_black"))
        out.append((f"{kind} tips", rack.parts[1].shape, "oc_tip"))
    s2x, s2y = OC._ot2_slot(2)
    blk, holes, ((sfx, sfy), (stx, sty)) = OC._block(s2x + labware.SBS_W / 2, s2y + labware.SBS_D / 2, dz)
    out.append(("tube block (slot 2)", blk, "pla_white"))
    tz = dz + 1.0
    tubes = [OC._tube05(hx, hy, tz) for hx, hy in holes]
    out.append(("0.5 mL tubes", cq.Workplane().add([t.val() for t in tubes]), "oc_tube"))
    mt = labware.microtube().parts[0].shape
    out.append(("1.5 mL tubes", cq.Workplane().add([mt.moved(cq.Location(cq.Vector(x, y, tz)))
                                                    for x, y in ((sfx, sfy), (stx, sty))]), "oc_tube"))
    out.append(("10 mg/L sulfide stock", OC._tube15_liquid(sfx, sfy, tz, OC.TUBE15_UL), "oc_sulf"))
    out.append(("1 mg/L standard", OC._tube15_liquid(stx, sty, tz, OC.TUBE15_UL), "oc_std"))
    out.append(("deep-well plate (slot 3)", OC._ot2_seat(labware.plate("96_deep"), 3).parts[0].shape, "polystyrene"))
    s5x, s5y = OC._ot2_slot(5)
    res, troughs, r_bot = OC._reservoir(s5x + labware.SBS_W / 2, s5y + labware.SBS_D / 2, dz)
    out.append(("12-well reservoir (slot 5)", res, "polypropylene"))
    r = OC.RES
    area = (r["w"] - 0.1) * (r["l"] - 0.1)
    for i, (ml, mat) in enumerate(((r["ml"], "oc_diluent"), (r["ml"], "oc_asw"), (r["ml3"], "oc_blank"))):
        x, y = troughs[i]
        h = ml * 1000.0 / area
        out.append((f"trough {i + 1}", cq.Workplane().box(r["w"] - 0.1, r["l"] - 0.1, h, centered=(True, True, False))
                    .translate((x, y, r_bot + 0.05)), mat))
    return out


def _key() -> str:
    h = hashlib.sha256()
    for f in (HERE / "ot2_deck.py", HERE / "ot2_corrosion.py", HERE / "lab_models" / "labware.py"):
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def entries(tol: float = 0.3) -> dict:
    """{name: dict(mesh, color, opacity)} of the deck's labware, the STEP's frame, one mesh per material."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"ot2_deck_{_key()}.pkl"
    if path.exists():
        try:
            return pickle.loads(path.read_bytes())
        except Exception:                            # noqa: BLE001  (a cache being written: build it here)
            pass
    import lab
    import ot2_corrosion as OC
    mats = dict(lab.MATS)
    mats.update(OC.MATERIALS)
    by: dict = {}
    for name, shape, mat in _shapes():
        if hasattr(shape, "vals"):
            vals = shape.vals()
            import cadquery as cq
            shape = vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
        # the 192 tips are small and many: a coarser chord keeps them about 30k triangles, not 260k
        by.setdefault(mat, []).append(lab.to_mesh(shape, 1.2, 0.8) if mat == "oc_tip" else lab.to_mesh(shape, tol))
    out = {}
    for mat, ms in by.items():
        r, g, b, a, _spec = mats[mat]
        out[f"deck {mat}"] = dict(mesh=lab._merge(ms), color=(r, g, b), opacity=a)
    path.write_bytes(pickle.dumps(out))
    return out


if __name__ == "__main__":
    for n, e in entries().items():
        print(f"{n}: {e['mesh'].n_cells} triangles, opacity {e['opacity']}")
