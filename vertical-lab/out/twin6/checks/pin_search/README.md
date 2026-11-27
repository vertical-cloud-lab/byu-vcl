# Round 6: what round 5's pin missed, and what closes it

Round 5's BOFN and pKGFN rows, made under `TWIN_PIN=avx2`, reran bit for bit between AMD EPYC 9V45 and 9V74 runners
and not on an EPYC 7763 or an Intel Xeon 6975P-C (round 5's notes, "Reproducibility"). The heuristic's and the
funnel's rows reran on every CPU tried. This folder holds what was measured to find the difference. Everything was
measured on this job's runner (AMD EPYC 9V74, Zen 4, AVX-512, 1 MB of L2 a core) and, for Intel CPUs, under Intel's
Software Development Emulator (SDE 9.58), which runs the same binaries while presenting an emulated CPU's CPUID and
instruction set: `-hsw` (Haswell: AVX2, no AVX-512, 256 KB of L2) and `-gnr` (Granite Rapids, the Xeon 6975P-C's
family: AVX-512, 2 MB of L2). numpy 2.5.5 (scipy-openblas 0.3.34), scipy's own OpenBLAS, torch 2.15.0 (oneMKL 2024.0
Update 2), as `out/twin5/requirements.txt` pins them.

## Three libraries still chose their arithmetic by the CPU

1. **numpy's own float64 kernels** (not BLAS). numpy dispatches `exp`, `log`, `power`, `expm1`, `log1p` and others
   to AVX-512 code on a CPU that has it and to AVX2 code otherwise. On a million fixed inputs, the two differ in the
   last bit for 4.6 % of `exp`'s results, 5.3 % of `power`'s, 10.1 % of `expm1`'s, 8.8 % of `log1p`'s and 0.26 % of
   `log`'s; `sin`, `tanh`, `sqrt`, products and Cholesky factors agree. The network policies compute utilities with
   these. The heuristic, the funnel, the truth and the instruments use Python's `math` (libm), which is why their rows
   never differed. Fix: `NPY_DISABLE_CPU_FEATURES=X86_V4,AVX512_ICL,AVX512_SPR` (numpy's AVX2 kernels, `X86_V3`, on
   every CPU).
2. **MKL inside torch.** `MKL_ENABLE_INSTRUCTIONS=AVX2` caps the instruction set on an Intel CPU, but on a non-Intel
   CPU MKL takes another code branch whatever it is set to. Its verbose header says "Intel(R) Architecture
   processors" on the EPYC and "Intel(R) AVX2 enabled processors" under an Intel CPUID. The two branches differ in
   `matmul`, `cholesky`, the triangular solves and the vector math behind `torch.exp`, `erf` and `tanh`. Fix: MKL's
   conditional numerical reproducibility, `MKL_CBWR=COMPATIBLE` (the one branch Intel documents for "all Intel or
   Intel compatible CPUs"), with `MKL_DYNAMIC=FALSE` and `OMP_DYNAMIC=FALSE`.
3. **OpenBLAS's blocking** (numpy's and scipy's). `OPENBLAS_CORETYPE=Haswell` fixes OpenBLAS's kernels, not how it
   blocks a product: it reads the L2 cache's size from the CPU. At exactly 1,024 KB (the EPYC 9V45 and 9V74) it
   blocks differently from every other size tried (`OPENBLAS_L2_SIZE` = 128, 256, 512, 1000, 1023, 1025, 2048 and
   4096, and the emulated Haswell and Granite Rapids all agree). Products, Cholesky factors and solves of size 300
   then differ ([`blas300.py`](blas300.py); [`bi_native.json`](bi_native.json) against [`bi_hsw.json`](bi_hsw.json):
   440 of 452 items agree, and the 12 that don't are all of size 300). Under the Haswell kernels with that blocking,
   a (64 x 384) by (384 x 64) product crashes numpy with a segmentation fault on the 9V74
   ([`k_sweep.py`](k_sweep.py)). Fix: `OPENBLAS_L2_SIZE=256` (Haswell's own L2).

`TWIN_PIN=portable` (`twin/repro.py`) is round 5's `avx2` plus all three, and oneDNN capped at AVX2 as a precaution.

## What the fix does

* **150-day automated-lab BOFN runs, before the OpenBLAS fix** ([`native150.jsonl`](native150.jsonl),
  [`sde150.jsonl`](sde150.jsonl)): every setting gave the same row and event log hashes, because no decision had
  changed yet, but the GP state (every node's fitted hyperparameters and the policy's last posterior means, as exact
  floats) told them apart. Under `avx2` the GP state differed between the native EPYC (`24a04029`), emulated Haswell
  (`a816b7c7`) and emulated Granite Rapids (`22499e98`). With numpy's kernels and MKL's branch pinned it was the same
  on all three (`b5f6a93b`).
* **The kernel probe** (`twin/gpcheck6.py`: numpy's math, reductions and BLAS, scipy, torch's math and BLAS, whole
  GP fits). Before the OpenBLAS fix, emulated Haswell and Granite Rapids agreed with each other and differed from
  the native EPYC in numpy's BLAS and in scipy ([`probe_sde_hsw_before_l2.line`](probe_sde_hsw_before_l2.line),
  [`probe_sde_gnr_before_l2.line`](probe_sde_gnr_before_l2.line)). With it, the native EPYC's probe
  ([`../gpcheck.json`](../gpcheck.json)) matches both emulated CPUs in all seven groups.
* **The whole GP check under emulated Granite Rapids**, including its short BOFN and pKGFN runs:
  [`../gpcheck_sde_gnr.json`](../gpcheck_sde_gnr.json).

The emulator presents another CPU's identity and instruction set to the same binaries, not another CPU's cache
timings or microarchitecture. A real Intel runner and a real EPYC 7763 are the test that counts. Each compute slice
runs `python -m twin.gpcheck6` before its rows, so the slices' mix of CPUs is that test.
