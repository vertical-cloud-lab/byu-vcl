"""Round 6: checkpoints, so that one run can span several jobs and end exactly as an unbroken run does.

A two-year run of the automated lab with BOFN or pKGFN costs several CPU-hours (out/twin6/checks/grid_hours.md), more
than a GitHub-hosted job's six hours allow with set-up. ``bench6`` stops such a run at a simulated day's boundary
when its job is about to end, saves it here, and the next job that is given the same run id carries on from that day.

A checkpoint holds everything the rest of the run depends on:

* the twin itself (``round6.Twin6``: its campaigns, policies and their GP nodes, the facility, the market, the HPC
  stream, every generator the twin draws from) and the state of its loop (``Twin6._loop``: the event queue, the
  bookings that end, results held for a person, the hour and the step), pickled with cloudpickle, which also takes
  the lambdas and closures the twin keeps; ``itertools.count``, which Python 3.14 no longer pickles, is saved as its
  next value;
* the state of Python's, numpy's and torch's global generators (BoTorch's fitting can draw from torch's);
* what the row reports and isn't in the twin: the torch generator's state at the start (``torch_rng_used``), the GP
  fits so far, the commit and ``twin/`` tree the run started from, and each job's share of the run (its CPU, CPU
  seconds and simulated days).

Whether a resumed run is the same run is tested, not assumed: ``python -m twin.gpcheck6 resume`` runs each of the GP
check's three runs in two fresh interpreters, stopped and saved at a day in the first and carried on in the second,
and compares the row, the event log and the GP state with the reference made by unbroken runs.
"""
from __future__ import annotations

import io
import itertools
import lzma
import os
import pickle
import random
import re
from pathlib import Path

import numpy as np

FORMAT = 1


def _count(start, step):
    return itertools.count(start, step)


def _pickler(f):
    import cloudpickle

    class P(cloudpickle.Pickler):
        def reducer_override(self, obj):
            if type(obj) is itertools.count:                  # count(5) or count(5, 2): its next value, unconsumed
                m = re.fullmatch(r"count\((.+?)(?:, (.+))?\)", repr(obj))
                return _count, (eval(m.group(1), {}), eval(m.group(2), {}) if m.group(2) else 1)
            return super().reducer_override(obj)

    return P(f, protocol=5)


def dumps(obj) -> bytes:
    f = io.BytesIO()
    _pickler(f).dump(obj)
    return f.getvalue()


def globals_state() -> dict:
    import torch
    return dict(random=random.getstate(), numpy=np.random.get_state(), torch=torch.get_rng_state().clone())


def set_globals_state(st: dict) -> None:
    import torch
    random.setstate(st["random"])
    np.random.set_state(st["numpy"])
    torch.set_rng_state(st["torch"])


def save(path, state: dict) -> int:
    """Write ``state`` (a dict holding the twin and the rest) to ``path``, xz-compressed, atomically; returns bytes."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = lzma.compress(dumps(dict(state, format=FORMAT)), preset=1)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    return len(data)


def load(path) -> dict:
    st = pickle.loads(lzma.decompress(Path(path).read_bytes()))
    if st.get("format") != FORMAT:
        raise ValueError(f"{path}: checkpoint format {st.get('format')}, this engine reads {FORMAT}")
    return st
