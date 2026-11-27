"""The digital twin of the vertical lab (twin/README.md).

Importing the package pins the numerical set-up first (twin/repro.py: one BLAS thread, and the AVX-512 kernels
round 3's rows were made with), before any submodule loads numpy or torch. ``TWIN_PIN=avx2`` or ``TWIN_PIN=off``
changes it; see twin/repro.py for why it matters.
"""
from twin import repro as _repro

_repro.apply()
