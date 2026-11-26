"""Round 3b: round 3's committed runs reproduce under the pinned set-up (twin/repro.py).

The reruns go in a subprocess started with the pinned environment, because string hashing can only be pinned when an
interpreter starts. They need a CPU with AVX-512, which round 3's rows were made on; elsewhere they skip and say why
(on an AVX2-only runner a rerun of BOFN seed 0 departs from the committed log at day 24.9, so they would only fail).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from twin import repro as R

ROOT = Path(__file__).resolve().parents[2]


def _pinned_env(**extra):
    env = dict(os.environ)
    env.update(PYTHONHASHSEED="0")
    env.update(extra)
    return env


def _run(args, **extra):
    p = subprocess.run([sys.executable, "-m", "twin.repro"] + args, cwd=ROOT, env=_pinned_env(**extra),
                       capture_output=True, text=True, timeout=1800)
    if p.returncode == 2:
        pytest.skip(p.stdout.strip())
    return p.returncode, p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-2000:]


def test_the_pin_is_applied_before_numpy():
    assert R.STATE["pin"] is not None
    assert not R.STATE["late"], "numpy, scipy or torch was imported before the twin package"
    for k in R.THREADS:
        assert os.environ[k] == "1"
    assert os.environ["PYTHONHASHSEED"] == "0"        # for every process started from this one


def test_a_short_rerun_of_bofn_seed_0_matches_the_committed_log():
    """BOFN seed 0 of round 3's main benchmark for its first 30 simulated days (about half a minute): every booking and
    result before day 28 as in the committed event log. Day 24.9 is where an AVX2 rerun departs from it."""
    rc, out = _run(["check", "30"])
    assert rc == 0, out
    r = json.loads(out)
    assert r["identical"] and r["n_bookings"] > 1000


@pytest.mark.parametrize("policy", ["heuristic", "gpbo"])
def test_a_full_rerun_gives_the_committed_row(policy):
    """Seed 0 of round 3's main benchmark, the whole year: the committed row exactly (GP-BO fits BoTorch GPs, so it
    goes through the same BLAS kernels as BOFN and pKGFN)."""
    rc, out = _run(["row", "main", policy, "0"])
    assert rc == 0, out
    r = json.loads(out)
    assert r["identical"] and r["torch_rng_used"] is False


def test_string_hashing_moves_a_last_bit():
    """Why PYTHONHASHSEED is part of the pin: round 3's heuristic, seed 11, under hash seeds 0 and 2. The two give one
    alloy's true utility one unit apart in the last place; hash seed 0 gives the committed value."""
    why = [w for w in R.problems() if "hashes strings" not in w]     # the subprocesses set their own hash seed
    if why:
        pytest.skip("; ".join(why))
    code = ("import json, sys; from twin import bench3 as B3; "
            "c = next(c for c in B3.EXPERIMENTS['main'] if c['policy'] == 'heuristic' and c['seed'] == 11); "
            "o, _ = B3.simulate(dict(c, events=False)); print(repr(o['campaigns']['flaime_al']['curve'][6][2]))")
    vals = {}
    for h in ("0", "2"):
        p = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=_pinned_env(PYTHONHASHSEED=h),
                           capture_output=True, text=True, timeout=600)
        vals[h] = float(p.stdout.strip().splitlines()[-1])
    ref = next(json.loads(l) for l in (ROOT / "out/twin3/runs/main.jsonl").read_text().splitlines()
               if json.loads(l)["cfg"]["policy"] == "heuristic" and json.loads(l)["cfg"]["seed"] == 11)
    assert vals["0"] == ref["campaigns"]["flaime_al"]["curve"][6][2]
    assert vals["2"] != vals["0"] and abs(vals["2"] - vals["0"]) < 1e-15


def test_reruns_in_round_3b_match_their_committed_rows():
    """Every rerun round 3b committed (out/twin3b/runs/re_*.jsonl) matches its committed round-3 row: exactly, or with
    only true utilities a few units apart in the last place (the hash key of the process that made the committed row
    was random and is not recorded) and everything else identical. No run drew from torch's global generator, and
    every run was made under the pin."""
    from twin import bench3b as B3b
    rows, bad = [], []
    for name, src in B3b.RERUN_OF.items():
        refs = B3b.committed_rows(src)
        for r in B3b.load(name):
            kind, info = B3b.match_kind(r, refs[B3b.run_id(r["cfg"])])
            if kind not in ("exact", "last bit"):
                bad.append((B3b.run_id(r["cfg"]), info))
            rows.append(r)
    if not rows:
        pytest.skip("no round-3b reruns committed")
    assert not bad, bad
    every = []
    for p in sorted((ROOT / "out" / "twin3b" / "runs").glob("*.jsonl")):
        every += [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    assert not [r for r in every if r.get("torch_rng_used")]
    assert all(r["env"]["hash_pinned"] and r["env"]["pin"] == "avx512" for r in every)


def test_rerun_logs_equal_round_3s_committed_logs():
    """Round 3 kept seed 0's event logs (out/twin3/events/*.json). Each rerun's log (out/twin3b/events/*.json.xz) is the
    same, booking for booking: the logs of the other seeds are the logs those committed runs would have written."""
    from twin import bench3b as B3b
    n = 0
    for p in sorted((ROOT / "out" / "twin3" / "events").glob("*.json")):
        q = ROOT / "out" / "twin3b" / "events" / f"{p.stem}.json.xz"
        if not q.exists():
            continue
        a, b = B3b.read_events(q), json.loads(p.read_text())
        for k in ("stations", "events", "designs", "results", "curves"):
            assert a[k] == b[k], (p.stem, k)
        n += 1
    if not n:
        pytest.skip("no rerun logs committed")
