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
    text = " ".join(ln["text"] for ln in sc["lines"])
    c, v = rows["conventional"], rows["vertical"]
    assert f"{c['area_sqft']:,}" in text and f"{v['area_sqft']:,}" in text
    assert f"{(1 - v['area_sqft'] / c['area_sqft']) * 100:.0f} percent" in text
    assert f"{v['per_1000_sqft']:.1f}" in text and f"{c['per_1000_sqft']:.1f}" in text
    assert "Forty-three instruments" in text and js["summary"]["counts"]["instruments"] == 43
    assert "9.15 meters" in text
    rec = json.loads((HERE / "out" / "floorspace" / "narration" / "lines.json").read_text())["lines"]
    times = sorted((FSS.PH[ln["phase"]] + ln["at"], rec[ln["id"]]["seconds"], ln["id"]) for ln in sc["lines"])
    for (a, da, ia), (b, _, ib) in zip(times[:-1], times[1:]):
        assert a + da + 0.3 <= b, (ia, ib)
    assert times[-1][0] + times[-1][1] <= FSS.PH["end"]
