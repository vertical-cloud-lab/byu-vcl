"""Round 6's market summary: every station the twin builds has a row, and the values round 5's USED reads are sane."""
from twin import market6 as M
from twin import round4 as R4


def test_every_build_key_has_a_row():
    m = M.load()
    missing = [k for k in R4.BUILD if k not in m]
    assert not missing, missing


def test_used_params_in_range():
    m = M.load()
    for k in R4.BUILD:
        p = M.used_params(k, m)
        assert set(M.ROUND5_USED) <= set(p)
        assert 0.0 < p["price_frac"] < 2.0, (k, p["price_frac"])
        assert 0.0 < p["lead_w"] < 30.0, (k, p["lead_w"])
        assert 0.0 <= p["p_fault"] <= 1.0, (k, p["p_fault"])
        assert p["refurb_w"] > 0 and 0.0 <= p["refurb_frac"] < 1.0, k
        assert p["extra_com_w"] >= 0.0, k
        if p["ok"]:
            assert not p["fallback"], (k, p["fallback"])     # a station bought used has its own numbers
            assert p["price_frac"] < 1.0, k                     # and saves money


def test_used_ok_needs_a_real_market():
    m = M.load()
    for k, r in m.items():
        if r["used_ok"]:
            assert str(r["market"]).startswith("yes"), (k, r["market"])
