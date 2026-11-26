"""Round 3b: the numerical set-up a rerun needs to give a committed round-3 row bit for bit, and a check of it.

    python3 -m twin.repro env              # what this process runs on: versions, BLAS kernels, threads, pins
    python3 -m twin.repro check [DAYS]     # rerun BOFN seed 0 for DAYS simulated days (default 30) and compare its
                                           # bookings with the committed event log; exit 0 if identical, 1 if not,
                                           # 2 if this machine can't provide the pinned kernels

**Why round 3's BOFN and pKGFN rows did not reproduce.** The libraries pick their floating-point kernels for the CPU
they find. numpy's OpenBLAS (built with DYNAMIC_ARCH) uses its ``SkylakeX`` kernels on a CPU with AVX-512 and its
``Haswell`` or ``Zen`` kernels without; torch dispatches its own kernels and MKL's by the same test. The kernels sum in
different orders, so results differ in the last bits, and a near-tie in a policy's ranking can go either way. Round 3
ran on an AVX-512 runner. On this runner (Xeon 6975P-C, AVX-512), a rerun of BOFN seed 0 matches the committed
event log, and full-year reruns match the committed rows exactly. With the AVX2 kernels forced on the same machine
(``OPENBLAS_CORETYPE=Haswell``, or torch's ``ATEN_CPU_CAPABILITY=avx2`` with ``MKL_ENABLE_INSTRUCTIONS=AVX2``, either
alone), the log is identical for 1,010 bookings, to day 24.9, and then copper's ranking puts a different action
first: exactly what the round-3 video run reported from its own runner. The thread count, the history of earlier runs
in the same worker and BoTorch's fit retries were ruled out (notes/twin_round3b.md).

**The pin** (``PINS``), applied by ``apply()`` when the ``twin`` package is imported, before numpy or torch load:

* one thread for OpenMP, OpenBLAS and MKL (a multithreaded reduction can also change the summation order);
* the AVX-512 kernels round 3 used: ``OPENBLAS_CORETYPE=SkylakeX``, ``ATEN_CPU_CAPABILITY=avx512``,
  ``MKL_ENABLE_INSTRUCTIONS=AVX512``, so that any AVX-512 machine runs the same kernels as round 3's runner (a newer
  CPU would otherwise get newer kernels);
* ``seed_globals(seed)`` at the start of every run: Python's, numpy's and torch's global generators. torch 2.15 seeds
  its global generator at random in every process, so a draw from it (BoTorch's fit retries resample the
  hyperparameters from their priors with it) would not repeat. No committed round-3 run drew from it
  (``torch_rng_used`` in round 3b's rows says so run by run), so seeding it changes none of them.

``TWIN_PIN=avx2`` pins the AVX2 kernels instead (``Haswell``, ``avx2``, ``AVX2``), which run on any x86-64 CPU from
2013 on, but give rows of their own, not round 3's; ``TWIN_PIN=off`` leaves the libraries to choose. A machine
without AVX-512 can't run the default pin (OpenBLAS would fault on the first AVX-512 instruction), so ``apply()`` then
leaves the kernels alone and ``check`` reports that this machine can't reproduce the committed rows.
"""
from __future__ import annotations

import json
import os
import platform
import sys

PINS = {
    "avx512": {"OPENBLAS_CORETYPE": "SkylakeX", "ATEN_CPU_CAPABILITY": "avx512", "MKL_ENABLE_INSTRUCTIONS": "AVX512"},
    "avx2": {"OPENBLAS_CORETYPE": "Haswell", "ATEN_CPU_CAPABILITY": "avx2", "MKL_ENABLE_INSTRUCTIONS": "AVX2"},
    "off": {},
}
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
STATE = {"pin": None, "late": False, "applied": {}}


def cpu_flags() -> set:
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("flags"):
                    return set(line.split(":", 1)[1].split())
    except OSError:
        pass
    return set()


def cpu_model() -> str:
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def has_avx512() -> bool:
    f = cpu_flags()
    return {"avx512f", "avx512dq", "avx512bw", "avx512vl"} <= f


def apply() -> dict:
    """Set the pinned environment. Call before numpy and torch are imported (twin/__init__.py does)."""
    if STATE["pin"] is not None:
        return STATE
    want = os.environ.get("TWIN_PIN", "avx512").lower()
    if want not in PINS:
        want = "avx512"
    if want == "avx512" and not has_avx512():
        want = "unpinned (no AVX-512)"
        env = {}
    else:
        env = dict(PINS[want])
    for k in THREADS:
        env[k] = "1"
    STATE["late"] = any(m in sys.modules for m in ("numpy", "torch", "scipy"))
    for k, v in env.items():
        os.environ[k] = v
    STATE.update(pin=want, applied=env)
    return STATE


def seed_globals(seed: int) -> None:
    """Seed Python's, numpy's and torch's global generators (the twin's own draws use their own seeded generators)."""
    import random

    import numpy as np
    random.seed(seed)
    np.random.seed(seed % (2 ** 32))
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass


def torch_rng_state():
    try:
        import torch
        return torch.get_rng_state().clone()
    except ImportError:
        return None


def torch_rng_used(before) -> bool | None:
    if before is None:
        return None
    import torch
    return not torch.equal(before, torch.get_rng_state())


def fingerprint() -> dict:
    """Versions, the BLAS kernels and threads actually in use, the CPU, and the pin: recorded in every round-3b row."""
    out = dict(python=platform.python_version(), cpu=cpu_model(), avx512=has_avx512(), pin=STATE["pin"],
               pin_late=STATE["late"])
    import numpy
    out["numpy"] = numpy.__version__
    for mod in ("scipy", "torch", "botorch", "gpytorch", "linear_operator"):
        try:
            out[mod] = __import__(mod).__version__
        except Exception:
            out[mod] = None
    try:
        import threadpoolctl
        libs = threadpoolctl.threadpool_info()
        out["blas"] = [dict(api=d.get("internal_api"), version=d.get("version"), arch=d.get("architecture"),
                            threads=d.get("num_threads")) for d in libs]
    except Exception:
        out["blas"] = None
    try:
        import torch
        out["torch_cpu"] = torch.backends.cpu.get_cpu_capability()
        out["torch_threads"] = torch.get_num_threads()
    except Exception:
        pass
    return out


def problems(fp: dict | None = None) -> list:
    """Why this process can't reproduce round 3's rows (empty if it can, as far as the set-up goes)."""
    fp = fp or fingerprint()
    out = []
    if not fp["avx512"]:
        out.append(f"the CPU ({fp['cpu']}) has no AVX-512; round 3's rows were made with AVX-512 kernels")
    if fp["pin"] != "avx512":
        out.append(f"the pin is {fp['pin']!r}, not 'avx512'")
    if fp["pin_late"]:
        out.append("numpy, scipy or torch was imported before the twin package, so the pins may not have applied")
    for d in fp.get("blas") or []:
        if d["api"] == "openblas" and d["arch"] != "SkylakeX":
            out.append(f"OpenBLAS runs its {d['arch']} kernels, not SkylakeX")
        if d["api"] in ("openblas", "mkl") and d["threads"] not in (1, None):
            out.append(f"{d['api']} runs {d['threads']} threads, not 1")
    if fp.get("torch_cpu") not in (None, "AVX512"):
        out.append(f"torch dispatches its {fp['torch_cpu']} kernels, not AVX512")
    return out


# ------------------------------------------------------------------------------------------------------ the check
def _key(e, lim):
    return (e["t0_h"], e["station"], e["campaign"], e["what"], e.get("design"), e.get("node"),
            e["t1_h"] if e["t1_h"] < lim else None)


def check(days: float = 30.0, policy: str = "bofn3", seed: int = 0) -> dict:
    """Rerun a committed seed of round 3's main benchmark for ``days`` simulated days (the horizon, the spending plan
    and everything else as in the full year) and compare its bookings and results before ``days - 2`` with the
    committed event log. 30 days takes about half a minute; it reaches past day 24.9, where an AVX2 rerun of BOFN
    seed 0 first departs from the committed log."""
    from pathlib import Path

    from twin import bench2 as B2
    from twin import bench3 as B3
    from twin import campaign as C
    from twin.opt import policies3 as P3
    root = Path(__file__).resolve().parent.parent
    ref = json.loads((root / "out" / "twin3" / "events" / f"r3_vertical_lab_{policy}_s{seed}.json").read_text())
    seed_globals(seed)
    specs = {k: C.Spec(k, B3.BUDGET[k], B2.WIP[k], seed, 1.0, crucible_cm3=225, reuse=True, stock="stocked",
                       cu_hidden=0.0, fidelity="fast") for k in ("flaime_al", "onr_cu")}
    pols = {k: P3.make3(policy, k, seed, None) for k in specs}
    tw = C.Twin(specs, pols, scenario="historical", facility="vertical_lab", seed=seed, horizon_days=365,
                mode="async")
    tw.stop_h = days * 24.0
    tw.run()
    log = tw.event_log()
    lim = (days - 2.0) * 24.0
    a = sorted(_key(e, lim) for e in log["events"] if e["t0_h"] < lim)
    b = sorted(_key(e, lim) for e in ref["events"] if e["t0_h"] < lim)
    first = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
    if first is None and len(a) != len(b):
        first = min(len(a), len(b))
    ra = [(r["t_h"], r["campaign"], r["type"], r["design"]) for r in log["results"] if r["t_h"] < lim]
    rb = [(r["t_h"], r["campaign"], r["type"], r["design"]) for r in ref["results"] if r["t_h"] < lim]
    return dict(policy=policy, seed=seed, days=days, n_bookings=len(a), n_bookings_ref=len(b), first_diff=first,
                first_diff_at_day=(round(min(a[first][0], b[first][0]) / 24.0, 2) if first is not None
                                   and first < min(len(a), len(b)) else None),
                results_identical=ra == rb, identical=first is None and ra == rb)


def main(argv):
    from twin import repro as R             # the package's module (python -m runs this file as __main__ as well)
    R.apply()
    if not argv or argv[0] == "env":
        fp = R.fingerprint()
        print(json.dumps(dict(fp, problems=R.problems(fp)), indent=1))
        return 0
    if argv[0] == "check":
        days = float(argv[1]) if len(argv) > 1 else 30.0
        fp = R.fingerprint()
        why = R.problems(fp)
        if why:
            print("can't reproduce round 3's rows bit for bit on this machine:\n  " + "\n  ".join(why))
            return 2
        r = R.check(days)
        print(json.dumps(r))
        return 0 if r["identical"] else 1
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
