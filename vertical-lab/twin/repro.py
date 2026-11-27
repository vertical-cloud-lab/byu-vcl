"""Round 3b: the numerical set-up a rerun needs to give a committed round-3 row bit for bit, and a check of it.

    python3 -m twin.repro env              # what this process runs on: versions, BLAS kernels, threads, pins
    python3 -m twin.repro check [DAYS]     # rerun BOFN seed 0 for DAYS simulated days (default 30) and compare its
                                           # bookings with the committed event log; exit 0 if identical, 1 if not,
                                           # 2 if this machine can't provide the pinned kernels
    python3 -m twin.repro row EXP POLICY SEED   # rerun one committed row of out/twin3/runs/EXP.jsonl and compare

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
  (``torch_rng_used`` in round 3b's rows says so run by run), so seeding it changes none of them;
* ``PYTHONHASHSEED=0``: Python hashes strings with a random key in every process, and ``Campaign`` builds a lot's true
  composition by iterating a set of element symbols (twin/campaign.py, the atomized lot and the top-up blend), so
  the order of the composition's keys, and with it the order of a later floating-point sum over them, changes from
  process to process. It moves the last bit of a value now and then: of round 3's first 60 reruns, one (the
  heuristic, seed 11) differs from its committed row by one unit in the last place of one alloy's true utility,
  and four hash seeds give two different values for it (twin/tests/test_round3b.py). No decision changed. The hash
  key can only be set when an interpreter starts, so ``apply()`` puts it in the environment for every process
  started from this one (the benchmark's workers), and the command-line tools re-execute themselves under it
  (``reexec_pinned``).

``TWIN_PIN=avx2`` pins the AVX2 kernels instead (``Haswell``, ``avx2``, ``AVX2``), which run on any x86-64 CPU from
2013 on, but give rows of their own, not round 3's; ``TWIN_PIN=off`` sets nothing (kernels, threads and hashing as
the libraries and the interpreter choose). A machine
without AVX-512 can't run the default pin (OpenBLAS would fault on the first AVX-512 instruction), so ``apply()`` then
leaves the kernels alone and ``check`` reports that this machine can't reproduce the committed rows.

**Round 6: what ``avx2`` misses, and ``TWIN_PIN=portable``.** Round 5's BOFN and pKGFN rows, made under ``avx2``,
reran bit for bit between AMD EPYC 9V45 and 9V74 runners and not on an EPYC 7763 or an Intel Xeon 6975P-C. Two
libraries still chose their code by the CPU (measured on an EPYC 9V74 and, for Intel CPUs, under Intel SDE's emulated
CPUIDs; out/twin6/checks/pin_search/README.md has the numbers):

* **numpy's own kernels.** numpy dispatches its float64 ``exp``, ``log``, ``power``, ``expm1``, ``log1p`` and others by
  CPU feature, apart from BLAS: AVX-512 kernels on a CPU that has them, libm on one that has only AVX2. They differ in
  the last bit (``exp`` on 4.6 % of inputs, ``power`` on 5.3 %). The network policies compute their utilities with them;
  the truth, the instruments, the heuristic and the funnel use Python's ``math`` (libm), which is why their rows never
  differed. ``NPY_DISABLE_CPU_FEATURES`` caps numpy at its AVX2 kernels (``X86_V3``).
* **MKL, inside torch.** ``MKL_ENABLE_INSTRUCTIONS=AVX2`` caps the instruction set on an Intel CPU, but MKL takes a
  different code branch on a non-Intel CPU whatever it is set to (its verbose header says "Intel(R) Architecture
  processors" on the EPYC and "Intel(R) AVX2 enabled processors" on an Intel CPUID), and the two branches differ in
  ``matmul``, ``cholesky``, the triangular solves and the vector math behind ``torch.exp``, ``erf`` and ``tanh``.
  MKL's conditional numerical reproducibility closes it: ``MKL_CBWR=COMPATIBLE`` is the one branch Intel documents for
  "all Intel or Intel compatible CPUs" (any other value falls back to ``AUTO`` on a non-Intel CPU, without a warning).

* **OpenBLAS's blocking, by the L2 cache it finds.** ``OPENBLAS_CORETYPE=Haswell`` fixes OpenBLAS's kernels but not
  its blocking: OpenBLAS reads the L2 cache's size from the CPU and, at exactly 1,024 KB (the EPYC 9V45 and 9V74),
  blocks its matrix products differently from every other size tried (128 KB to 4 MB, and the emulated Haswell and
  Granite Rapids). numpy's and scipy's products, Cholesky factors and solves then differ from size 257 or so on
  (measured at 300), and a (64 x 384) by (384 x 64) product crashes numpy's OpenBLAS outright on the EPYC 9V74
  under the Haswell kernels. ``OPENBLAS_L2_SIZE=256`` (Haswell's own L2) sets the size OpenBLAS uses on every CPU.

``portable`` is ``avx2`` plus those three, ``MKL_DYNAMIC`` and ``OMP_DYNAMIC`` off (Intel's conditions for
reproducibility) and oneDNN capped at AVX2 (a precaution; no float64 result here depends on it). It gives rows of
its own: not round 5's, and not round 3's. ``fingerprint()`` records what is in force (numpy's enabled kernels, MKL's
branch and CNR state as MKL itself reports them), ``problems6()`` lists what isn't, and ``python -m twin.gpcheck6``
(twin/gpcheck6.py) is the check a new runner runs first.
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
# Round 6: the AVX2 kernels as "avx2", numpy's own kernels capped at AVX2, and MKL's CPU-independent branch. The names
# in NPY_DISABLE_CPU_FEATURES are numpy 2.5's dispatch groups (out/twin5/requirements.txt pins numpy 2.5.5); a name
# that isn't one is ignored with an ImportWarning, so ``fingerprint()['numpy_simd']`` records what numpy really enabled.
NPY_AVX512_GROUPS = ("X86_V4", "AVX512_ICL", "AVX512_SPR")
PINS["portable"] = dict(PINS["avx2"], MKL_CBWR="COMPATIBLE", MKL_DYNAMIC="FALSE", OMP_DYNAMIC="FALSE",
                        NPY_DISABLE_CPU_FEATURES=",".join(NPY_AVX512_GROUPS), ONEDNN_MAX_CPU_ISA="AVX2",
                        OPENBLAS_L2_SIZE="256")
# variables a pin removes: numpy refuses to start with both NPY_ENABLE_ and NPY_DISABLE_CPU_FEATURES set
UNSET = {"portable": ("NPY_ENABLE_CPU_FEATURES",)}
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
    if want != "off":
        for k in THREADS:
            env[k] = "1"
        env["PYTHONHASHSEED"] = "0"
    STATE["late"] = any(m in sys.modules for m in ("numpy", "torch", "scipy"))
    for k, v in env.items():
        os.environ[k] = v
    for k in UNSET.get(want, ()):
        os.environ.pop(k, None)
    STATE.update(pin=want, applied=env)
    return STATE


def hash_pinned() -> bool:
    """Whether this interpreter hashes strings with the fixed key (PYTHONHASHSEED=0 when it started)."""
    return sys.flags.hash_randomization == 0


def reexec_pinned(module: str) -> None:
    """Re-execute ``python -m module args`` with PYTHONHASHSEED=0 unless this interpreter already runs with it (the
    command-line tools call this first; nothing has been simulated yet, so nothing is lost)."""
    if hash_pinned() or os.environ.get("TWIN_PIN", "avx512").lower() == "off":
        return
    os.environ["PYTHONHASHSEED"] = "0"
    sys.stdout.flush()
    os.execv(sys.executable, [sys.executable, "-m", module] + sys.argv[1:])


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
               pin_late=STATE["late"], hash_pinned=hash_pinned())
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
    # round 6: what the "portable" pin adds, as the libraries themselves report it
    out["cpu_vendor"] = cpu_vendor()
    out["glibc"] = "-".join(platform.libc_ver())
    out["numpy_simd"] = numpy_simd()
    out["pin_env"] = {k: os.environ.get(k) for k in sorted(set(PINS["portable"]) | set(THREADS) |
                                                           {"PYTHONHASHSEED", "NPY_ENABLE_CPU_FEATURES"})}
    out["mkl"] = mkl_state() if STATE["pin"] == "portable" else None
    return out


def cpu_vendor() -> str:
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("vendor_id"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return ""


def numpy_simd() -> dict | None:
    """The kernels numpy dispatches to in this process: its baseline, and the dispatch groups it enabled and left
    off (``NPY_DISABLE_CPU_FEATURES``, or a CPU without them)."""
    try:
        from numpy._core import _multiarray_umath as U
        feats = U.__cpu_features__
        return dict(baseline=list(U.__cpu_baseline__), enabled=[k for k in U.__cpu_dispatch__ if feats.get(k)],
                    off=[k for k in U.__cpu_dispatch__ if not feats.get(k)])
    except Exception:
        return None


def mkl_state() -> dict | None:
    """MKL's own account of itself inside torch: its version, the code branch its verbose header names (on an Intel
    CPU the instruction set, "Intel(R) Architecture processors" on any other) and its CNR state. Read once per
    process, by switching MKL's verbose mode on for one 4 x 4 product with the process's standard output pointed at
    a temporary file. Only called under the "portable" pin: without CNR an extra MKL call could, in principle, move
    a later result through its buffers' alignment."""
    if "mkl" in STATE:
        return STATE["mkl"]
    out = None
    try:
        import ctypes
        import re
        import tempfile

        import torch
        if torch.backends.mkl.is_available():
            libc = ctypes.CDLL(None)
            sys.stdout.flush()
            libc.fflush(None)
            saved = os.dup(1)
            text = ""
            with tempfile.TemporaryFile() as tmp:
                try:
                    os.dup2(tmp.fileno(), 1)
                    with torch.backends.mkl.verbose(torch.backends.mkl.VERBOSE_ON):
                        a = torch.ones(4, 4, dtype=torch.double)
                        torch.mm(a, a)
                    libc.fflush(None)
                finally:
                    os.dup2(saved, 1)
                    os.close(saved)
                tmp.seek(0)
                text = tmp.read().decode(errors="replace")
            head = re.search(r"MKL_VERBOSE (oneMKL .*?) for Intel\(R\) 64 architecture (.*?), Lnx", text)
            cnr = re.search(r"CNR:([A-Z0-9_,]+)", text)
            nthr = re.search(r"NThr:(\d+)", text)
            out = dict(version=head.group(1) if head else None, branch=head.group(2) if head else None,
                       cnr=cnr.group(1) if cnr else None, threads=int(nthr.group(1)) if nthr else None)
    except Exception as e:                                  # never let the record break a run
        out = dict(error=repr(e)[:200])
    STATE["mkl"] = out
    return out


def problems6(fp: dict | None = None) -> list:
    """Why this process is not under round 6's "portable" pin (empty if it is, as far as the set-up goes)."""
    fp = fp or fingerprint()
    out = []
    if fp["pin"] != "portable":
        out.append(f"the pin is {fp['pin']!r}, not 'portable'")
    if not fp.get("hash_pinned"):
        out.append("this interpreter hashes strings with a random key (start it with PYTHONHASHSEED=0)")
    if fp["pin_late"]:
        out.append("numpy, scipy or torch was imported before the twin package, so the pins may not have applied")
    ns = fp.get("numpy_simd")
    if ns is None:
        out.append("numpy's enabled kernels can't be read")
    else:
        on = [k for k in ns["enabled"] if k != "X86_V3"]
        if on:
            out.append(f"numpy dispatches to {', '.join(on)} kernels (NPY_DISABLE_CPU_FEATURES did not take)")
        if "X86_V3" not in ns["enabled"]:
            out.append("numpy's AVX2 kernels (X86_V3) are off: this CPU has no AVX2, or this numpy names them otherwise")
    mk = fp.get("mkl")
    if mk is None or mk.get("error"):
        out.append("MKL's state inside torch can't be read")
    else:
        if mk.get("cnr") != "COMPATIBLE":
            out.append(f"MKL's CNR state is {mk.get('cnr')!r}, not 'COMPATIBLE'")
        if mk.get("threads") not in (1, None):
            out.append(f"MKL runs {mk['threads']} threads, not 1")
    pe = fp.get("pin_env") or {}
    for k, v in PINS["portable"].items():
        if pe.get(k) != v:
            out.append(f"{k} is {pe.get(k)!r}, not {v!r}")
    for d in fp.get("blas") or []:
        if d["api"] == "openblas" and d["arch"] != "Haswell":
            out.append(f"OpenBLAS runs its {d['arch']} kernels, not Haswell")
        if d["api"] in ("openblas", "mkl", "openmp") and d["threads"] not in (1, None):
            out.append(f"{d['api']} runs {d['threads']} threads, not 1")
    if fp.get("torch_cpu") not in (None, "AVX2"):
        out.append(f"torch dispatches its {fp['torch_cpu']} kernels, not AVX2")
    if fp.get("torch_threads") not in (None, 1):
        out.append(f"torch runs {fp['torch_threads']} threads, not 1")
    return out


def problems(fp: dict | None = None) -> list:
    """Why this process can't reproduce round 3's rows (empty if it can, as far as the set-up goes)."""
    fp = fp or fingerprint()
    out = []
    if not fp["avx512"]:
        out.append(f"the CPU ({fp['cpu']}) has no AVX-512; round 3's rows were made with AVX-512 kernels")
    if fp["pin"] != "avx512":
        out.append(f"the pin is {fp['pin']!r}, not 'avx512'")
    if not fp.get("hash_pinned"):
        out.append("this interpreter hashes strings with a random key (start it with PYTHONHASHSEED=0)")
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


def row(experiment: str, policy: str, seed: int) -> dict:
    """Rerun one committed row of round 3 (out/twin3/runs/<experiment>.jsonl) for its whole horizon and compare."""
    from twin import bench3 as B3
    from twin import bench3b as B3b
    ref = next(r for r in B3b.committed_rows(experiment).values()
               if r["cfg"]["policy"] == policy and r["cfg"]["seed"] == seed)
    out, _ = B3.simulate(dict(ref["cfg"], events=False))
    out = json.loads(json.dumps(B3.B2._jsonable(out)))
    d = B3b.first_diff(out, ref)
    return dict(experiment=experiment, policy=policy, seed=seed, identical=d is None,
                first_diff=None if d is None else [d[0], str(d[1])[:120], str(d[2])[:120]],
                torch_rng_used=out["torch_rng_used"])


def main(argv):
    from twin import repro as R             # the package's module (python -m runs this file as __main__ as well)
    R.reexec_pinned("twin.repro")
    R.apply()
    if not argv or argv[0] == "env":
        fp = R.fingerprint()
        print(json.dumps(dict(fp, problems=R.problems(fp), problems6=R.problems6(fp)), indent=1))
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
    if argv[0] == "row":
        why = R.problems()
        if why:
            print("can't reproduce round 3's rows bit for bit on this machine:\n  " + "\n  ".join(why))
            return 2
        r = R.row(argv[1], argv[2], int(argv[3]))
        print(json.dumps(r))
        return 0 if r["identical"] else 1
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
