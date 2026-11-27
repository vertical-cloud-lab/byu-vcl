"""Round 6: the GP determinism check. A runner runs it before it makes BOFN or pKGFN rows.

    python -m twin.gpcheck6                 # run it under the "portable" pin and compare with the committed reference
                                            # (out/twin6/checks/gpcheck.json): one JSON line; exit 0 if identical,
                                            # 1 if anything differs, 2 if the pin is not in force on this machine
    python -m twin.gpcheck6 --out FILE      # the same, and the full record written to FILE (a slice commits it)
    python -m twin.gpcheck6 write           # run it and write the reference
    python -m twin.gpcheck6 probe           # the kernel probe only (seconds), compared with the reference
    python -m twin.gpcheck6 show            # the committed reference
    TWIN_GPCHECK_WRAP="sde64 -gnr --" python -m twin.gpcheck6 probe     # under an emulated CPU (Intel SDE, QEMU)

Round 5's BOFN and pKGFN rows differed between CPU models under ``TWIN_PIN=avx2`` because numpy's own float64 kernels
and MKL's code branch inside torch still followed the CPU (twin/repro.py, "Round 6"). ``TWIN_PIN=portable`` pins both.
This check is how a machine shows that it computes what the reference machine computed, in two parts:

* **The kernel probe**: every numerical building block the network policies use, on fixed inputs, hashed bit for bit
  in groups: numpy's float64 math, its reductions and BLAS, scipy's (its own OpenBLAS, L-BFGS-B, special functions),
  torch's math functions (MKL's vector math and ATen's kernels), torch's BLAS and LAPACK (MKL) at the sizes a GP fit
  uses, and whole GP fits (BoTorch's ``SingleTaskGP``: the marginal likelihood, its gradient, the fitted
  hyperparameters, the posterior). A group that differs names the library that still follows the CPU.
* **Short BOFN and pKGFN runs** on the round's engine (``twin.bench6`` when it imports, else ``twin.bench5``),
  each in a fresh interpreter: the row (apart from timing and provenance), the event log, and **the GP state**: every
  node's fitted hyperparameters and scaling and the policy's last posterior means, as exact floats. The GP state is
  the sensitive part. In a 150-day run a last-bit difference in a fit changes the GP state at once and no decision
  yet (measured: the row and log hashes of four settings were equal while their GP states all differed), so a check
  of the row and log alone would pass on a machine whose two-year rows then differ.

Every part runs in a fresh interpreter started with the pin's environment and nothing else that could steer the
libraries (``MKL_*``, ``OPENBLAS_*``, ``NPY_*``, ``ATEN_*``, ``ONEDNN_*``, ``OMP_*`` and similar are dropped first).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "out" / "twin6" / "checks" / "gpcheck.json"
PIN = "portable"
# (name, lab, plan, policy, stock, seed, simulated days). Both campaigns fit GPs in each (the reference records how
# many nodes; ``write`` refuses a run where a campaign fitted none). The conventional lab's runs are the cheapest that
# fit GPs; the automated lab's adds the in-house routes and the reorder-point stock.
RUNS = (
    ("conventional_bofn3", "conventional", "external", "bofn3", "lean", 0, 220),
    ("conventional_pkgfn3", "conventional", "external", "pkgfn3", "lean", 0, 220),
    ("automated_bofn3", "vertical", "parallel", "bofn3", "reorder", 0, 200),
)
# The simulated candidates at 4 x round 5's (a pool of 512), whatever the grid's main scale: more than the 384 the
# network values in one decision, so BOFN's and pKGFN's cut of the pool (twin/opt/net6.py) runs in the check too.
SCALE = 4
NOT_IN_ROW = ("seconds", "timing", "gp", "env", "code", "events_file")       # timing and provenance, as round 5's comparisons
STEERING = ("MKL_", "OPENBLAS_", "NPY_", "ATEN_", "ONEDNN_", "DNNL_", "OMP_", "KMP_", "GOMP_", "BLIS_", "NUMEXPR_",
            "VECLIB_", "TORCH_", "GLIBC_TUNABLES", "LD_PRELOAD")


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------- the kernel probe
def probe() -> dict:
    """Fixed inputs through every numerical building block, hashed per group (run in a pinned child)."""
    import numpy as np
    import scipy.linalg
    import scipy.optimize
    import scipy.spatial.distance
    import scipy.special
    import scipy.stats
    import torch
    torch.set_num_threads(1)
    groups = {}

    def put(group, name, a):
        a = np.ascontiguousarray(np.asarray(a, dtype="<f8"))
        groups.setdefault(group, hashlib.sha256()).update(name.encode() + a.tobytes())

    rng = np.random.default_rng(20261127)
    N = 200_000
    x = rng.normal(0, 2.0, N)
    p = np.abs(x) + 1e-3
    u = rng.uniform(-1, 1, N)
    y = rng.uniform(0.1, 3.0, N)
    # numpy's own float64 kernels (dispatched by CPU feature unless capped)
    for name, f, a in [("exp", np.exp, x), ("expm1", np.expm1, x), ("exp2", np.exp2, x), ("log", np.log, p),
                       ("log2", np.log2, p), ("log10", np.log10, p), ("log1p", np.log1p, p), ("sqrt", np.sqrt, p),
                       ("cbrt", np.cbrt, x), ("sin", np.sin, x), ("cos", np.cos, x), ("tan", np.tan, x),
                       ("arcsin", np.arcsin, u), ("arccos", np.arccos, u), ("arctan", np.arctan, x),
                       ("sinh", np.sinh, x), ("cosh", np.cosh, x), ("tanh", np.tanh, x), ("arcsinh", np.arcsinh, x),
                       ("arctanh", np.arctanh, u * 0.999), ("square", np.square, x),
                       ("reciprocal", np.reciprocal, p)]:
        put("numpy_math", name, f(a))
    put("numpy_math", "power", np.power(p, y))
    put("numpy_math", "power10", 10.0 ** x)
    put("numpy_math", "arctan2", np.arctan2(x, y))
    put("numpy_math", "hypot", np.hypot(x, y))
    put("numpy_math", "scalar_exp", [float(np.exp(v)) for v in x[:2000]])
    put("numpy_math", "scalar_log", [float(np.log(v)) for v in p[:2000]])
    put("numpy_reduce", "sums", [x.sum(), (x * y).sum(), np.add.reduce(x[:1001]), x.mean(), x.std(), x.var(),
                                 np.linalg.norm(x), np.prod(1.0 + 1e-6 * x)])
    put("numpy_reduce", "cumsum", np.cumsum(x))
    put("numpy_reduce", "sort", np.sort(x))
    put("numpy_reduce", "argsort", np.argsort(x).astype(float))
    put("numpy_reduce", "norm_axis", np.linalg.norm(x.reshape(-1, 8), axis=1))
    put("numpy_reduce", "percentile", np.percentile(x, [5, 50, 90]))
    for n in (8, 30, 120, 300):
        A = rng.normal(size=(n, n))
        B = rng.normal(size=(n, 7))
        v = rng.normal(size=n)
        S = A @ A.T + n * np.eye(n)
        put("numpy_blas", f"matmul{n}", A @ B)
        put("numpy_blas", f"gram{n}", S)
        put("numpy_blas", f"mv{n}", A @ v)
        put("numpy_blas", f"dot{n}", [v @ v, np.dot(v, A[0])])
        put("numpy_blas", f"einsum{n}", np.einsum("ij,jk->ik", A, B))
        put("numpy_blas", f"chol{n}", np.linalg.cholesky(S))
        put("numpy_blas", f"solve{n}", np.linalg.solve(S, B))
        put("numpy_blas", f"eigh{n}", np.linalg.eigvalsh(S))
        # scipy's own BLAS and LAPACK (a second OpenBLAS)
        L = scipy.linalg.cholesky(S, lower=True)
        put("scipy", f"chol{n}", L)
        put("scipy", f"cho_solve{n}", scipy.linalg.cho_solve((L, True), B))
        put("scipy", f"solve_triangular{n}", scipy.linalg.solve_triangular(L, B, lower=True))
        put("scipy", f"cdist{n}", scipy.spatial.distance.cdist(A, A[: n // 2]))
    put("scipy", "ndtr", scipy.special.ndtr(x))
    put("scipy", "norm_cdf", scipy.stats.norm.cdf(x))
    put("scipy", "norm_pdf", scipy.stats.norm.pdf(x))
    put("scipy", "erf", scipy.special.erf(x))
    put("scipy", "gammaln", scipy.special.gammaln(p))
    put("scipy", "logsumexp", [scipy.special.logsumexp(x[:5000])])
    put("scipy", "expit", scipy.special.expit(x))
    put("scipy", "sobol", scipy.stats.qmc.Sobol(9, seed=3).random(256))
    Q = rng.normal(size=(12, 12))
    Q = Q @ Q.T + 12 * np.eye(12)
    b = rng.normal(size=12)

    def fun(z):                                             # a smooth non-quadratic objective, as an MLL is
        return float(0.5 * z @ Q @ z - b @ z + np.sum(np.log1p(np.exp(z)))), Q @ z - b + scipy.special.expit(z)
    r = scipy.optimize.minimize(fun, np.zeros(12), jac=True, method="L-BFGS-B", bounds=[(-2.0, 2.0)] * 12)
    put("scipy", "lbfgsb", list(r.x) + [r.fun, float(r.nit), float(r.nfev)])
    # torch: MKL's vector math and ATen's kernels
    tx, tp, tu = torch.tensor(x), torch.tensor(p), torch.tensor(u)
    for name, f, a in [("exp", torch.exp, tx), ("expm1", torch.expm1, tx), ("log", torch.log, tp),
                       ("log1p", torch.log1p, tp), ("log10", torch.log10, tp), ("sqrt", torch.sqrt, tp),
                       ("rsqrt", torch.rsqrt, tp), ("erf", torch.erf, tx), ("erfc", torch.erfc, tx),
                       ("erfinv", torch.erfinv, tu * 0.999), ("tanh", torch.tanh, tx), ("sigmoid", torch.sigmoid, tx),
                       ("sin", torch.sin, tx), ("cos", torch.cos, tx), ("atan", torch.atan, tx),
                       ("lgamma", torch.lgamma, tp), ("softplus", torch.nn.functional.softplus, tx),
                       ("logsigmoid", torch.nn.functional.logsigmoid, tx)]:
        put("torch_math", name, f(a).numpy())
    put("torch_math", "pow", torch.pow(tp, 1.7).numpy())
    put("torch_math", "pow_t", torch.pow(tp, torch.tensor(y)).numpy())
    put("torch_math", "strided_exp", torch.exp(tx[::3]).numpy())
    put("torch_math", "sums", [tx.sum().item(), (tx * tp).sum().item(), tx.mean().item(), tx.std().item(),
                               tx.norm().item(), torch.logsumexp(tx[:5000], 0).item()])
    put("torch_math", "cumsum", torch.cumsum(tx, 0).numpy())
    # torch: MKL's BLAS and LAPACK at the sizes a GP fit uses
    for n in (8, 30, 120, 300):
        A = torch.tensor(rng.normal(size=(n, n)))
        B = torch.tensor(rng.normal(size=(n, 7)))
        v = torch.tensor(rng.normal(size=n))
        S = A @ A.T + n * torch.eye(n, dtype=torch.double)
        put("torch_blas", f"matmul{n}", (A @ B).numpy())
        put("torch_blas", f"gram{n}", S.numpy())
        put("torch_blas", f"mv{n}", (A @ v).numpy())
        put("torch_blas", f"dot{n}", [(v @ v).item(), torch.dot(v, A[0]).item()])
        L = torch.linalg.cholesky(S)
        put("torch_blas", f"chol{n}", L.numpy())
        put("torch_blas", f"trsm{n}", torch.linalg.solve_triangular(L, B, upper=False).numpy())
        put("torch_blas", f"cholsolve{n}", torch.cholesky_solve(B, L).numpy())
        put("torch_blas", f"logdet{n}", [torch.logdet(S).item(), 2 * L.diagonal().log().sum().item()])
        put("torch_blas", f"cdist{n}", torch.cdist(A, A[: n // 2]).numpy())
        put("torch_blas", f"eigh{n}", torch.linalg.eigvalsh(S).numpy())
        put("torch_blas", f"einsum{n}", torch.einsum("ij,ij->i", A, A).numpy())
        put("torch_blas", f"baddbmm{n}", torch.baddbmm(torch.zeros(2, n, 7, dtype=torch.double),
                                                       torch.stack([A, A.T]), torch.stack([B, B])).numpy())
    # whole GP fits, as twin/opt/gp.py makes them (two sizes: a young node and a node at its 300-row cap)
    from botorch.fit import fit_gpytorch_mll
    from botorch.models import SingleTaskGP
    from gpytorch.mlls import ExactMarginalLogLikelihood
    for n, d in ((40, 9), (300, 24)):
        X = torch.tensor(rng.uniform(size=(n, d)))
        w = rng.normal(size=d) * (rng.uniform(size=d) < 0.4)
        Y = torch.tensor((np.sin(3.0 * X.numpy() @ w) + 0.1 * rng.normal(size=n)).reshape(-1, 1))
        Y = (Y - Y.mean()) / Y.std()
        m = SingleTaskGP(X, Y)
        mll = ExactMarginalLogLikelihood(m.likelihood, m)
        m.train()
        loss = -mll(m(X), m.train_targets)
        loss.backward()
        put("gp_fit", f"mll{n}", [loss.item()])
        put("gp_fit", f"grad{n}", np.concatenate([q.grad.reshape(-1).numpy() for q in m.parameters()
                                                  if q.grad is not None]))
        fit_gpytorch_mll(mll)
        m.eval()
        Xs = torch.tensor(rng.uniform(size=(400, d)))
        with torch.no_grad():
            post = m.posterior(Xs)
            put("gp_fit", f"mean{n}", post.mean.reshape(-1).numpy())
            put("gp_fit", f"var{n}", post.variance.reshape(-1).numpy())
        put("gp_fit", f"hyper{n}", np.concatenate([q.detach().reshape(-1).numpy() for q in m.parameters()]))
    return {g: h.hexdigest() for g, h in sorted(groups.items())}


# ------------------------------------------------------------------------------------------------- the short runs
def _bench():
    """The round's engine: twin.bench6 when it imports, else round 5's (the interface is the same).
    ``TWIN_GPCHECK_ENGINE=bench5`` (or ``bench6``) names one."""
    want = os.environ.get("TWIN_GPCHECK_ENGINE", "")
    if want != "bench5":
        try:
            from twin import bench6 as B
            return B, "twin.bench6"
        except ImportError:
            if want == "bench6":
                raise
    from twin import bench5 as B
    return B, "twin.bench5"


def gp_state(tw) -> dict:
    """Every GP node's fitted hyperparameters and scaling, and the policy's last posterior means, as exact floats."""
    st = {}
    for k, c in tw.campaigns.items():
        pol = c.policy
        d = {}
        for name, nodes in sorted((getattr(pol, "nodes", None) or {}).items()):
            for j, nd in enumerate(nodes):
                hyp = {kk: [float(v).hex() for v in vv.detach().reshape(-1).double().tolist()]
                       for kk, vv in sorted((nd.state or {}).items())}
                d[f"{name}/{j}"] = dict(n=nd.n, n_fit=nd.n_fit, ymean=float(nd.ymean).hex(),
                                        ystd=float(nd.ystd).hex(), hyper=hyp)
        d["_mus"] = [float(v).hex() for v in (getattr(pol, "_mus", None) or [])]
        d["_best_kb"] = float(getattr(pol, "_best_kb", 0.0) or 0.0).hex()
        st[k] = d
    return st


def run(name: str) -> dict:
    """One short run in this (pinned, fresh) interpreter: hashes of its row, event log and GP state."""
    _, lab, plan, policy, stock, seed, days = next(r for r in RUNS if r[0] == name)
    os.environ["TWIN6_DAYS"] = os.environ["TWIN5_DAYS"] = str(days)
    B, engine = _bench()
    from twin import bench2 as B2
    t0 = time.time()
    cfg = B._cfg(lab, plan, policy, stock, seed, **({"hpc": dict(scale=SCALE)} if engine == "twin.bench6" else {}))
    out, tw = B.simulate(cfg)
    row = json.loads(json.dumps(B2._jsonable(out)))
    if engine == "twin.bench6":                             # the log a grid row's event file holds, named after
        log = B.event_log(tw, cfg)                          # the check's run (not the grid's run id, which names
        log["meta"]["run_id"] = name                        # the scale relative to the grid's main one)
    else:                                                   # as bench5.run_one builds it
        log = tw.event_log(meta=dict(cfg=cfg, run_id=B.run_id(cfg)))
        log["round5"] = dict(stock={k: dict(use=c.use_log, orders=c.stock_orders, stockouts=c.stockouts)
                                    for k, c in tw.campaigns.items()}, held=tw.held_log, daily=dict(tw.daily))
    log = json.loads(json.dumps(B2._jsonable(log)))
    gps = gp_state(tw)
    return dict(run_id=B.run_id(cfg), days=days, engine=engine,
                row=_sha({k: v for k, v in row.items() if k not in NOT_IN_ROW}), log=_sha(log), gp=_sha(gps),
                gp_nodes_fitted={k: sum(1 for v in d.values() if isinstance(v, dict) and v["n_fit"] > 0)
                                 for k, d in gps.items()},
                gp_fits=row.get("gp", {}).get("fits"), n_bookings=len(log["events"]), n_results=len(log["results"]),
                torch_rng_used=row.get("torch_rng_used"), seconds=round(time.time() - t0, 1))


# ------------------------------------------------------------------------------------------------- the driver
def _env() -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(STEERING)}
    env.update(TWIN_PIN=PIN, PYTHONHASHSEED="0")
    return env


def _child(what: str, name: str = "") -> dict:
    # TWIN_GPCHECK_WRAP runs each part under an emulator that presents another CPU to the libraries, for example
    # "/path/to/sde64 -gnr --" (Intel SDE, an Intel Granite Rapids CPUID) or "qemu-x86_64 -cpu EPYC-Milan"
    wrap = os.environ.get("TWIN_GPCHECK_WRAP", "").split()
    p = subprocess.run(wrap + [sys.executable, "-m", "twin.gpcheck6", "_child", what, name], cwd=HERE.parent,
                       env=_env(), capture_output=True, text=True)
    lines = [ln for ln in p.stdout.splitlines() if ln.startswith("{")]
    if p.returncode != 0 or not lines:
        return dict(error=(p.stderr or p.stdout)[-1500:])
    return json.loads(lines[-1])


def measure(runs=True) -> dict:
    """The probe and (unless ``runs`` is False) the short runs, each in its own pinned interpreter."""
    t0 = time.time()
    jobs = [("probe", "")] + ([("run", r[0]) for r in RUNS] if runs else [])
    with ThreadPoolExecutor(max(1, int(os.environ.get("TWIN_WORKERS", "1")))) as ex:
        res = list(ex.map(lambda j: _child(*j), jobs))
    pr = res[0]
    out = dict(what="twin/gpcheck6.py: the kernel probe and short BOFN and pKGFN runs under TWIN_PIN=portable; "
                    "sha256 of each probe group, and of each run's row, event log and GP state",
               pin=PIN, env=pr.get("env"), problems=pr.get("problems"), code=pr.get("code"),
               probe=pr.get("probe"), probe_seconds=pr.get("seconds"), errors={})
    if os.environ.get("TWIN_GPCHECK_WRAP"):
        out["wrap"] = os.environ["TWIN_GPCHECK_WRAP"]
    if "error" in pr:
        out["errors"]["probe"] = pr["error"]
    if runs:
        out["runs"] = {}
        for (_, name), r in zip(jobs[1:], res[1:]):
            if "error" in r:
                out["errors"][name] = r["error"]
            else:
                out["runs"][name] = r
        engines = {r["engine"] for r in out["runs"].values()}
        out["engine"] = engines.pop() if len(engines) == 1 else None
    out["seconds"] = round(time.time() - t0, 1)
    return out


VERSION_KEYS = ("python", "numpy", "scipy", "torch", "botorch", "gpytorch", "linear_operator")


def compare(got: dict, ref: dict) -> dict:
    """What matches the reference: each probe group, and each run's row, log and GP state."""
    out = dict(probe={g: got["probe"].get(g) == h for g, h in ref["probe"].items()} if got.get("probe") else None)
    if "runs" in got:
        out["runs"] = {}
        for name, r in ref["runs"].items():
            g = got["runs"].get(name)
            out["runs"][name] = None if g is None else {k: g[k] == r[k] for k in ("row", "log", "gp")}
        out["engine_same"] = got.get("engine") == ref.get("engine")
    ge, re_ = got.get("env") or {}, ref.get("env") or {}
    out["versions_differ"] = {k: [ge.get(k), re_.get(k)] for k in VERSION_KEYS if ge.get(k) != re_.get(k)}
    ok = bool(out["probe"]) and all(out["probe"].values())
    if "runs" in out:
        ok = ok and out["engine_same"] and all(v is not None and all(v.values()) for v in out["runs"].values())
    out["match"] = bool(ok) and not got.get("errors")
    return out


def _line(got: dict, cmp_: dict | None) -> dict:
    env = got.get("env") or {}
    line = dict(check="gpcheck6", match=None if cmp_ is None else cmp_["match"], pin=got["pin"],
                engine=got.get("engine"), cpu=env.get("cpu"), cpu_vendor=env.get("cpu_vendor"),
                problems=got.get("problems"), seconds=got["seconds"])
    if got.get("wrap"):
        line["wrap"] = got["wrap"]                          # the CPU the libraries saw is the emulator's, not ``cpu``
    if cmp_ is not None:
        line.update(probe=cmp_["probe"], runs=cmp_.get("runs"))
        if cmp_["versions_differ"]:
            line["versions_differ"] = cmp_["versions_differ"]
        if cmp_.get("engine_same") is False:
            line["engine_same"] = False
    line["hashes"] = dict(probe={g: h[:16] for g, h in (got.get("probe") or {}).items()},
                          runs={n: {k: r[k][:16] for k in ("row", "log", "gp")}
                                for n, r in (got.get("runs") or {}).items()})
    if got.get("errors"):
        line["errors"] = {k: v[-300:] for k, v in got["errors"].items()}
    return line


def main(argv) -> int:
    if argv[:1] == ["_child"]:                              # a pinned child: one part, one JSON line
        from twin import repro as R
        t0 = time.time()
        if argv[1] == "probe":
            pr = probe()
            fp = R.fingerprint()
            try:
                B, _ = _bench()
                code = B._code()
            except Exception:
                code = None
            print(json.dumps(dict(probe=pr, env=fp, problems=R.problems6(fp), code=code,
                                  seconds=round(time.time() - t0, 1))))
        else:
            print(json.dumps(run(argv[2])))
        return 0
    out_file = None
    if "--out" in argv:
        i = argv.index("--out")
        out_file = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    cmd = argv[0] if argv else "check"
    if cmd == "show":
        print(REF.read_text())
        return 0
    if cmd not in ("check", "write", "probe"):
        raise SystemExit(__doc__)
    got = measure(runs=cmd != "probe")
    if cmd == "write":
        if got["errors"] or got["problems"]:
            print(json.dumps(_line(got, None)))
            raise SystemExit("not written: " + json.dumps(got["errors"] or got["problems"])[:2000])
        vac = [n for n, r in got["runs"].items() if min(r["gp_nodes_fitted"].values()) < 1]
        if vac:
            raise SystemExit(f"not written: a campaign fitted no GP node in {vac}; lengthen the run (RUNS)")
        REF.parent.mkdir(parents=True, exist_ok=True)
        REF.write_text(json.dumps(got, indent=1) + "\n")
        print(json.dumps(_line(got, None)))
        return 0
    ref = json.loads(REF.read_text()) if REF.exists() else None
    cmp_ = compare(got, ref) if ref is not None and got.get("probe") else None
    if out_file is not None:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(dict(got, compared_with=str(REF.relative_to(HERE.parent)),
                                            comparison=cmp_), indent=1) + "\n")
    line = _line(got, cmp_)
    if ref is None:
        line["note"] = f"no reference at {REF.relative_to(HERE.parent)}: run 'python -m twin.gpcheck6 write'"
    print(json.dumps(line))
    if got.get("problems") or (got.get("errors") and not got.get("probe")):
        return 2
    return 0 if (cmp_ is not None and cmp_["match"]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
