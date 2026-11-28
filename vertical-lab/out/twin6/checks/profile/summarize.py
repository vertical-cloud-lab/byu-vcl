"""Round 6: where a live automated-lab GP run spends its time (py-spy sampling profiles, raw collapsed stacks).

    python out/twin6/checks/profile/summarize.py           # writes profile.md beside this file

Taken with ``py-spy record --pid <worker> --duration 90-120 --rate 25 --nonblocking --format raw`` on the second
job's timing runs (checks/timing6.py, seed 0 of the automated lab stocked), which kept running while sampled.
"""
import collections
import lzma
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = [("BOFN, 16x, day ~340", "bofn3_16x_day340.raw.xz"), ("pKGFN, 64x, day ~320", "pkgfn3_64x_day320.raw.xz"),
        ("BOFN, 16x, day ~390", "bofn3_16x_day390.raw.xz")]
KEYS = [("Net3.propose (net3.py)", "proposing (all)"), ("Net3._candidates (net3.py)", "valuing candidates"),
        ("Node.predict (gp.py)", "GP prediction"), ("_Six._p_powder (net6.py)", "the atomize node's batched search"),
        ("Node.sample (gp.py)", "GP draws through a network"), ("Net3._ucu (net3.py)", "copper's utility draws"),
        ("Net3.utility_samples_al (net3.py)", "aluminium's utility draws"),
        ("Net3._refresh_new (net3.py)", "refreshing the new designs' list"), ("Node.fit (gp.py)", "GP fitting"),
        ("DefaultPredictionStrategy.exact_predictive_covar (exact_prediction_strategies.py)",
         "gpytorch's predictive covariance"),
        ("Twin6._stream_tick (round6.py)", "the HPC stream")]


def load(f):
    tot, incl = 0, collections.Counter()
    for line in lzma.decompress((HERE / f).read_bytes()).decode().splitlines():
        if not line.strip():
            continue
        stack, n = line.rsplit(" ", 1)
        n = int(n)
        tot += n
        names = set()
        for fr in stack.split(";"):
            m = re.match(r"(.+?) \((.+?):\d+\)", fr)
            names.add(f"{m.group(1)} ({m.group(2).split('/')[-1]})" if m else fr)
        for nm in names:
            incl[nm] += n
    return tot, incl


def main():
    data = [(lab, *load(f)) for lab, f in RUNS]
    L = ["# Round 6: where an automated-lab GP run spends its time", "",
         "Made by `python out/twin6/checks/profile/summarize.py` from py-spy's raw samples of live timing runs "
         "(seed 0, the automated lab stocked). Share of samples in each function and everything it calls. "
         "Everything is simulated.", "",
         "| | " + " | ".join(lab for lab, _, _ in data) + " |", "|---|" + "---|" * len(data),
         "| samples | " + " | ".join(f"{t:,}" for _, t, _ in data) + " |"]
    for k, what in KEYS:
        L.append(f"| {what} (`{k.split(' (')[0]}`) | " + " | ".join(f"{100 * c[k] / t:.1f} %" for _, t, c in data) + " |")
    (HERE / "profile.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
