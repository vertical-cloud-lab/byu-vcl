"""The floor-space segment's layouts, story and script (twin/video/floorspace*.py): no VTK needed.

    cd vertical-lab && python -m pytest -q twin/tests/test_floorspace.py
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pytest

from twin.video import floorspace as FS
from twin.video import floorspace_story as FSS

HERE = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def built():
    return FS.build_all()


@pytest.fixture(scope="module")
def story():
    return FSS.Story()


def test_inventory_is_the_3d_labs(built):
    inv, _ = built
    tp = json.loads((HERE / "out" / "tray_plan.json").read_text())
    n_items = sum(1 for v in tp["trays"].values() for it in v["items"] if it["kind"] == "item")
    assert sum(1 for it in inv.values() if it.tray is not None) == n_items
    c = FS.counts(inv)
    assert (c["instruments"], c["benchtop"], c["floor"]) == (43, 31, 12)
    assert all(it.name in FS.ITEM_INFO for it in inv.values() if it.tray is not None)


def test_layouts_have_no_overlaps(built):
    inv, lays = built
    for lay in lays:
        assert FS.check(lay, inv) == [], lay.name


def test_every_item_is_placed_in_every_layout(built):
    inv, lays = built
    for lay in lays:
        assert set(inv) <= set(lay.places), lay.name


def test_areas(built):
    inv, (conv, flat, vert) = built
    assert flat.envelope == conv.envelope
    assert vert.area_m2 < conv.area_m2
    js = json.loads((HERE / "out" / "floorspace" / "layouts.json").read_text())
    rows = {r["name"]: r for r in js["summary"]["rows"]}
    assert rows["conventional"]["area_sqft"] == round(conv.area_sqft)
    assert rows["vertical"]["area_sqft"] == round(vert.area_sqft)
    for lay in (conv, vert):                          # the breakdown covers the floor (rasterized: within 1 %)
        b = FS.breakdown(lay, inv)
        assert abs(sum(b.values()) - lay.area_m2) / lay.area_m2 < 0.01


def test_rooms_follow_the_rules(built):
    inv, (conv, _, _) = built
    for r in conv.rooms:
        x0, y0, x1, y1 = r["rect"]
        assert x1 - x0 >= FS.ASSUME["module"] - 1, r["name"]
        assert x0 <= r["entry"][0] <= x1
    for b in conv.benches:                            # every bench item on its bench, inside its edges
        if b["kind"] != "bench":
            continue
        bx0, by0, bx1, by1 = b["rect"]
        for k in b["keys"]:
            r = conv.places[k].rect(inv[k])
            assert bx0 - 1 <= r[0] and r[2] <= bx1 + 1 and by0 - 1 <= r[1] and r[3] <= by1 + 1, k


def test_story_order(story):
    S = story
    assert max(a for a, _ in S.fly.values()) < FSS.PH["vert"] + 12.4   # every instrument is off its bench before
    assert S.fly_end <= FSS.PH["vert"] + 14.6 + 1e-6                    # the benches go, and on its tray before
    assert min(a for a, _ in S.move.values()) >= FSS.PH["vert"] + 14.6 - 1e-6     # the floor machines move
    assert S.move_end < FSS.PH["plans"]
    for k, (a, b) in S.fly.items():                      # each lands exactly on its tray's anchor
        x, y, z, th, where = S.item_pose(k, b + 0.01)
        assert where == "tray"
        sh, ys, zs = S.tray_of(S.inv[k])
        cx, cy, z0 = S.item_local(k)
        assert (x, y, z) == pytest.approx((FSS.SHUTTLE_X[sh] + cx, ys + cy, zs + z0))


def test_people_stay_in_the_building_until_they_leave(story):
    S = story
    x0, y0, x1, y1 = S.conv.envelope
    for nm, ag in S.people.items():
        if nm == "p7":
            continue
        for t in [i * 0.5 for i in range(int(min(ag.t_out, FSS.PH["vert"] + 12.0) * 2))]:
            st = ag.state(t)
            if st.get("alpha", 0) < 0.99:
                continue
            inside = x0 - 1 <= st["x"] <= x1 + 1 and y0 - 1 <= st["y"] <= y1 + 1
            leaving = S.cor[1] <= st["y"] <= S.cor[3] and t >= FSS.PH["flat"]    # out of a corridor door
            assert inside or leaving, (nm, t)


def test_narration_numbers_match_the_layouts():
    js = json.loads((HERE / "out" / "floorspace" / "layouts.json").read_text())
    rows = {r["name"]: r for r in js["summary"]["rows"]}
    sc = json.loads((HERE / "twin" / "video" / "narration_floorspace.json").read_text())
    lines = {ln["id"]: ln["text"] for ln in sc["lines"]}
    text = " ".join(lines.values())
    c, v, rb = rows["conventional"], rows["vertical"], rows["robots"]
    n_inst = js["summary"]["counts"]["instruments"]
    assert f"{c['area_sqft']:,}" in text and f"{v['area_sqft']:,}" in text
    assert "Forty-three instruments" in lines["f1"] and n_inst == 43
    assert "design layouts, not built labs" in lines["f1"]
    assert "9.15 meters" in text
    # the context line (f8): today's instruments, the layout for robots beside the conventional lab
    assert f"today's {n_inst} instruments" in lines["f8"]
    assert f"{rb['area_sqft']:,} square feet" in lines["f8"]
    assert abs(rb["area_sqft"] / c["area_sqft"] - 1) < 0.05              # "about what the conventional lab does"
    # the result (f11, f12): the same capacity, the Shuttles' trays laid out flat against the vertical lab
    cp = js["capacity"]
    tr, sc_, pc = cp["trays"], cp["same_capacity"], cp["percent"]
    assert f"only {tr['in_use']} of the Shuttles' {tr['trays']} trays" in lines["f11"]
    assert f"all {tr['trays']} need {sc_['flat']['area_sqft']:,} square feet" in lines["f11"]
    assert (f"holds them in {sc_['vertical']['area_sqft']:,}: {pc['vertical_vs_flat_capacity']} percent less floor"
            in lines["f12"])
    assert pc["vertical_vs_flat_capacity"] == round((1 - sc_["vertical"]["area_sqft"] / sc_["flat"]["area_sqft"]) * 100)
    assert (f"{sc_['vertical']['positions_per_1000_sqft']:.1f} tray positions per thousand square feet, against "
            f"{sc_['flat']['positions_per_1000_sqft']:.1f}") in lines["f12"]
    # the same-equipment percentages are context on screen (the plans' first row), never spoken
    for k in ("vertical_vs_conventional", "vertical_vs_robots"):
        assert f"{pc[k]} percent" not in text
    assert cp["machine_block"]["area_m2"] / rows["vertical"]["area_m2"] > 0.5      # f9: "most of the floor"
    say = sc["say"]
    for n in re.findall(r"\d[\d,]*\.\d+|\d{1,3}(?:,\d{3})+", text):              # every decimal and thousands respelled
        assert n in say, n
    rec = json.loads((HERE / "out" / "floorspace" / "narration" / "lines.json").read_text())["lines"]
    times = sorted((FSS.PH[ln["phase"]] + ln["at"], rec[ln["id"]]["seconds"], ln["id"]) for ln in sc["lines"])
    for (a, da, ia), (b, _, ib) in zip(times[:-1], times[1:]):
        assert a + da + 0.3 <= b, (ia, ib)
    assert times[-1][0] + times[-1][1] <= FSS.PH["end"]
    # context and the scale reference come before the result; what the result costs (a high bay) is said last
    order = [i for _, _, i in times]
    assert [i for i in order if i in ("f8", "f10", "f11", "f12", "f9")] == ["f8", "f10", "f11", "f12", "f9"]
    for ln in sc["lines"]:                               # a cue is a moment inside its line's recording
        assert rec[ln["id"]]["text"] == ln["text"], ln["id"]
        for k, at in ln.get("cues", {}).items():
            assert 0.0 <= at <= rec[ln["id"]]["seconds"], (ln["id"], k)


def test_segment_for_a_longer_cut():
    """What twin/video/cut5.py calls: the segment's length, its lines with their recordings, and a finished frame
    (a plans frame here: it needs no 3-D track)."""
    pytest.importorskip("PIL")
    from twin.video import floorspace_cut as FC
    assert FC.Cut.T == FSS.PH["end"] > FSS.T3D_END
    ls = FC.narration_lines()
    assert [ln["t"] for ln in ls] == sorted(ln["t"] for ln in ls) and len({ln["id"] for ln in ls}) == len(ls)
    assert all(ln["flac"].exists() and 0.0 <= ln["t"] and ln["t"] + ln["seconds"] <= FC.Cut.T for ln in ls)
    cut = FC.Cut()
    assert FSS.PH["plans"] < cut.cue("f12", "result") < cut.cue("f12", "positions") < cut.t0("f9")
    try:
        fr = FC.segment_frame(FC.Cut.T - 0.5)
    except OSError as e:                                 # no DejaVu fonts on this machine
        pytest.skip(str(e))
    assert fr.shape == (1080, 1920, 3) and fr.dtype.name == "uint8"


# ============================================================================================ the capacity comparison
def _vlm_constants() -> dict:
    """vlm.py's column constants, read from its source (vlm.py needs cadquery to import)."""
    src = (HERE / "vlm.py").read_text()

    def num(name):
        return float(re.search(rf"^{name} = ([0-9.]+)", src, re.M).group(1))
    unit_h, pitch, sill, open_h, z_low = (num(n) for n in ("UNIT_H", "PITCH", "Z_SILL", "OPEN_H", "Z_LOW"))
    assert re.search(r"^Z_TOP_IN = UNIT_H - 260\.0", src, re.M)
    assert re.search(r"^Z_FRONT_LOW_TOP = Z_SILL - 40\.0", src, re.M)
    assert re.search(r"^Z_FRONT_HI = PITCH \* -\(-\(Z_OPEN_TOP \+ 120\.0\) // PITCH\)", src, re.M)
    return dict(unit_h=unit_h, pitch=pitch, z_low=z_low, z_top=unit_h - 260.0, z_front_low_top=sill - 40.0,
                z_front_hi=pitch * math.ceil((sill + open_h + 120.0) / pitch))


def test_shuttle_columns_are_vlms():
    v = _vlm_constants()
    for k, val in v.items():
        assert FS.SHUTTLE[k] == val, k
    tp = json.loads((HERE / "out" / "tray_plan.json").read_text())
    rear = [s for k, s in tp["slots"].items() if k != "open" and s["y"] > 0]
    front = [s for k, s in tp["slots"].items() if k != "open" and s["y"] < 0]
    assert min(s["z"] for s in rear) == v["z_low"]
    assert min(s["z"] for s in front if s["z"] > v["z_front_low_top"]) == v["z_front_hi"]
    assert max(s["z"] + s["span"] for s in front if s["z"] < v["z_front_low_top"]) <= v["z_front_low_top"]


def test_tray_capacity():
    c = FS.tray_capacity()
    assert (c["in_use"], c["in_use_instrument_trays"], c["in_use_stores"]) == (18, 12, 6)
    assert c["span_mm"] == 750.0 and min(c["instrument_tray_spans_mm"]) == 625.0
    free = {(col["shuttle"], col["column"]): col["free_mm"] for col in c["columns"]}
    # notes/tray_plan.md: "5140 mm in Shuttle 1's rear column, 5465 in its front column, 5265 and 5490 in Shuttle 2's"
    assert (free[1, "rear"], free[1, "front"], free[2, "rear"], free[2, "front"]) == (5140, 5465, 5265, 5490)
    assert c["trays"] == c["in_use"] + sum(col["added"] for col in c["columns"]) == 45
    assert c["empty_unit"]["instrument_trays"] == 20 < FS.PR344["trays_per_unit"]
    assert c["surface_m2"] == pytest.approx(45 * 2.45 * 0.864, abs=0.05)


@pytest.fixture(scope="module")
def four():
    return FS.build_four()


def test_flat_layouts_for_robots(four):
    inv, (conv, _, rob, ver), cap, lays = four
    R = FS.TRAY_BENCH
    mb = FS.machine_block(inv)
    for lay in (rob, lays["capacity"], lays["robots_2way"], lays["capacity_2way"]):
        assert FS.check(lay, inv) == [], lay.name
        assert set(inv) <= set(lay.places), lay.name                   # every item, bench or floor, has a place
        benches = [b for b in lay.benches if b["kind"] == "bench"]
        assert len(benches) == lay.meta["positions"]
        docks = {(round(d["x"]), round(d["y"])) for d in lay.docks}
        for b in benches:                                             # each position: tray-sized, with its dock
            x0, y0, x1, y1 = b["rect"]
            assert (x1 - x0, y1 - y0) == pytest.approx((R["w"], R["d"]))
            assert any(abs(dx - (x0 + x1) / 2) < 1 for dx, _ in docks)
            for k in b["keys"]:                                       # its items inside it, as on the tray
                r = lay.places[k].rect(inv[k])
                assert x0 - 1 <= r[0] and r[2] <= x1 + 1 and y0 - 1 <= r[1] and r[3] <= y1 + 1, k
        # the floor machines stand as in the machine block (shifted by nothing: the bench block is added west)
        for k, p in mb.places.items():
            assert (lay.places[k].x, lay.places[k].y) == (p.x, p.y), k
        # facing rows: a dock lane each side of a MiR aisle as wide as the rule; cross-aisles as wide
        aisle = R["two_way"] if lay.meta["two_way"] else R["one_way"]
        assert lay.meta["aisle_mm"] == aisle
        kind = "mir" if lay.meta["two_way"] else "mir1"
        new = [a["rect"] for a in lay.aisles if a not in mb.aisles]
        assert all(round(r[3] - r[1]) == R["dock"] for r, a in zip(new, [a for a in lay.aisles if a not in mb.aisles])
                   if a["kind"] == "dock")
        assert sum(1 for a in lay.aisles if a not in mb.aisles and a["kind"] == kind) == 2 + lay.meta["modules"]
        assert all(round(min(a["rect"][2] - a["rect"][0], a["rect"][3] - a["rect"][1])) == aisle
                   for a in lay.aisles if a not in mb.aisles and a["kind"] == kind)
    assert rob.meta["used"] == 18 and lays["capacity"].meta["positions"] == cap["trays"]["trays"]
    assert rob.meta["north_row"] == 2                                 # where the Shuttles stood


def test_capacity_in_layouts_json(four):
    inv, (conv, _, rob, ver), cap, lays = four
    js = json.loads((HERE / "out" / "floorspace" / "layouts.json").read_text())
    c = js["capacity"]
    assert c["trays"]["trays"] == cap["trays"]["trays"] == 45
    assert c["same_capacity"]["flat"]["area_sqft"] == round(lays["capacity"].area_sqft)
    assert c["same_equipment"]["robots"]["area_sqft"] == round(rob.area_sqft)
    assert c["machine_block"]["area_m2"] == round(FS.machine_block(inv).area_m2, 1)
    rows = {r["name"]: r for r in js["summary"]["rows"]}
    assert list(rows) == ["conventional", "flat", "robots", "vertical"]
    assert rows["vertical"]["positions"] == 45 and rows["robots"]["positions"] == 18
    # the vertical lab and both flat automated layouts share the machine block; the rest is the benchtop part
    for k in ("robots", "vertical"):
        assert rows[k]["benchtop_m2"] == pytest.approx(rows[k]["area_m2"] - c["machine_block"]["area_m2"], abs=0.11)
    assert lays["capacity"].area_m2 > rob.area_m2 > ver.area_m2
