"""DAL #256's schedule (facility dal256), the campaign trace and the common seed set (round 2, resumed)."""
from __future__ import annotations

import collections
import json

import pytest

from twin import bench2 as B
from twin import campaign as C
from twin import facility as F
from twin import seeding as SD
from twin import trace as TR
from twin.opt import policies2 as P2


def _twin(fac="dal256", stock="lean", policy="heuristic", seeding=None, trace=False):
    specs = {k: C.Spec(k, B.BUDGET[k], B.WIP[k], 0, 1.0, stock=stock) for k in B.BUDGET}
    pols = {k: P2.make(policy, k, 0, seeding=seeding) for k in specs}
    tw = C.Twin(specs, pols, facility=fac, seed=0, horizon_days=365, trace=trace)
    tw.run()
    return tw


@pytest.fixture(scope="module")
def tw256():
    return _twin()


def test_proposed_unchanged_by_the_new_fields():
    st = F.facility("proposed")
    assert all(s.weekdays is None and s.adjust is None and s.campaign_weekdays is None for s in st.values())
    fac = F.Facility("proposed", 0, 8760.0)
    assert fac.adjust("atomizer", 2.5, "atomize", "flaime_al") == 2.5


def test_dal256_atomizer_calendar(tw256):
    fac = next(iter(tw256.facilities.values()))
    runs = [j for j in fac.res["atomizer"].jobs if j[3] == "atomize"]
    assert runs
    for t0, t1, camp, what, tag in runs:
        day, hod = int(t0 // 24), t0 % 24
        assert abs(hod - 8.0) < 1e-6, "one run a day, starting at 08:00"
        assert (day % 7 == 4) == (camp == "onr_cu"), "copper on Fridays, aluminium Mon-Thu"
        assert t1 - t0 >= 5.0, "a run plus about 3 h to cool, clean and rebuild"
    per_day = collections.Counter(int(j[0] // 24) for j in runs)
    assert max(per_day.values()) == 1


def test_dal256_weekly_sessions(tw256):
    fac = next(iter(tw256.facilities.values()))
    assert {int(j[0] // 24) % 7 for j in fac.res["byu_sem"].jobs} == {3}          # Thursdays
    assert {int(j[0] // 24) % 7 for j in fac.res["tensile"].jobs} <= {3}
    assert {int(j[0] // 24) % 7 for j in fac.res["utah_midi"].jobs} <= {1, 2}     # Tue-Wed sessions


def test_dal275_seed_set():
    al = SD.seeds("dal275", "flaime_al")
    assert [lab.split()[0] for lab, _ in al] == ["D1", "D2", "B30", "B15", "S1", "S2", "S3"]
    assert len(SD.seeds("dal275", "onr_cu")) == 5


def test_trace_schema_and_annotations(tmp_path):
    tw = _twin(policy="heuristic", seeding="dal275", trace=True)
    cfg = B._cfg("heuristic", 0, facility="dal256", stock="lean", seeding="dal275", trace=True)
    T = TR.build(tw, cfg, "test", {})
    p = tmp_path / "t.json"
    p.write_text(json.dumps(B._jsonable(T)))
    assert TR.check(p) == []
    ev = T["events"]
    atom = [e for e in ev if e["station"] == "atomizer" and e["what"] == "atomize"]
    assert atom and all(e["dal211"] == "p3" for e in atom)
    assert {e["outcome"] for e in ev} <= set(TR.OUTCOMES)
    lit = T["literature"]
    assert lit and all(L["reused"] and L["edison"].startswith("https://github.com/vertical-cloud-lab/"
                                                                "digital-alloy-lab/blob/") for L in lit)
    assert "weeks_below_3" in T["weekly"]


def test_saas_nuts_refit_schedule(monkeypatch):
    """Fresh NUTS chains only when the data have grown by refit_every and by nuts_growth; reuse in between."""
    import numpy as np
    from twin.opt import gp as G
    calls = []

    def fake_fit(m, warmup_steps, num_samples, thinning, disable_progbar, seed):
        calls.append(len(m.train_inputs[0]) if m.train_inputs[0].dim() == 2 else None)
        import torch
        s = {"mean": torch.zeros(2, dtype=torch.double), "outputscale": torch.ones(2, dtype=torch.double),
             "noise": torch.full((2,), 1e-3, dtype=torch.double),
             "lengthscale": torch.ones(2, m.train_inputs[0].shape[-1], dtype=torch.double)}
        m.load_mcmc_samples(s)
        m.eval()

    import botorch.fit
    monkeypatch.setattr(botorch.fit, "fit_fully_bayesian_model_nuts", fake_fit)
    rng = np.random.default_rng(0)
    X, y = rng.random((30, 4)), rng.random(30)
    nd = G.Node("saas_nuts", refit_every=4, seed=0)
    for n in range(3, 31):
        nd.fit(X[:n], y[:n])
        mu, sd = nd.predict(X[:2])
        assert np.all(np.isfinite(mu)) and np.all(sd > 0)
    assert calls == [3, 7, 11, 17, 26]
