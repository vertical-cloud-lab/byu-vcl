"""Check EZstat-Pro runs of the corrosion checks C1-C3 (README section 7).

Splits an EZware CSV export into stretches with the cell off and with it on.
While the cell is off (open-circuit monitoring), EZware writes a current of
exactly 0 A. Then reports:

- OCP, for each cell-off stretch: mean, standard deviation, and drift in
  mV per 10 min from a straight-line fit (C3: two references within 5 mV,
  drifting under 1 mV in 10 min);
- LPR, for each cell-on stretch that sweeps the potential: a straight-line
  fit I = (E - E_mid)/Rp + I_mid, giving Rp (C1: within 3 % of the resistor)
  and the current where the sweep crosses its middle;
- hold, for each cell-on stretch at one potential: the mean current, its
  standard deviation and the charge passed (C1: 4.00 uA and 2.40 mC at
  +40 mV for 10 min on 10.00 kOhm).

With the leads open, as in the 2026-10-24 dummy runs, an LPR measures no
resistance at all. Its current is the instrument's offset and noise floor
on that range, which is what C2 needs to know, so those are reported too.

    python check_corrosion_runs.py ../results/20261024_dummy-runs/20261024-D2.csv
    python check_corrosion_runs.py C1.csv --r-ohm 10000 --tol 3

Columns are found as in check_dummy_runs.py, which this reuses; the time
column is required. Writes <csv>.check.png and <csv>.check.json next to the
CSV and prints a summary.
"""

import argparse
import json
from pathlib import Path

import numpy as np

from check_dummy_runs import load, plt

# A cell-on stretch whose potential spans less than this is a hold, not a sweep.
SWEEP_MIN_SPAN_V = 2e-3


def stretches(on):
    """(start, stop) index pairs of the runs of equal values in a bool array."""
    edges = np.flatnonzero(np.diff(on.astype(int))) + 1
    bounds = np.concatenate([[0], edges, [len(on)]])
    return [(int(a), int(b)) for a, b in zip(bounds[:-1], bounds[1:]) if b > a]


def line(x, y):
    A = np.column_stack([x, np.ones_like(x)])
    (slope, icept), *_ = np.linalg.lstsq(A, y, rcond=None)
    return slope, icept


def check_ocp(t, V):
    res = {"t_start_s": float(t[0]), "t_end_s": float(t[-1]), "points": int(len(t)),
           "E_mean_V": float(np.mean(V)), "E_sd_V": float(np.std(V)),
           "E_first_V": float(V[0]), "E_last_V": float(V[-1])}
    if len(t) >= 3 and t[-1] > t[0]:
        slope, _ = line(t, V)
        res["drift_mV_per_10min"] = float(slope * 600 * 1e3)
    return res


def check_lpr(t, V, I, r_ohm, tol):
    e_mid = 0.5 * (V.min() + V.max())
    g, i_mid = line(V - e_mid, I)
    resid = I - (g * (V - e_mid) + i_mid)
    res = {"t_start_s": float(t[0]), "t_end_s": float(t[-1]), "points": int(len(t)),
           "E_from_V": float(V[0]), "E_to_V": float(V[-1]), "E_mid_V": float(e_mid),
           "I_at_mid_A": float(i_mid), "I_mean_A": float(np.mean(I)), "I_sd_A": float(np.std(I)),
           "I_range_A": [float(I.min()), float(I.max())],
           "slope_S": float(g), "Rp_ohm": float(1 / g) if g else float("inf"),
           "residual_sd_A": float(np.std(resid))}
    # Rp is meaningful only if the sweep moved the current by more than its noise.
    span_i = abs(g) * (V.max() - V.min())
    res["Rp_resolved"] = bool(span_i > 10 * res["residual_sd_A"])
    if r_ohm:
        res["R_ohm"] = r_ohm
        res["deviation_pct"] = 100 * (res["Rp_ohm"] - r_ohm) / r_ohm
        res["pass"] = bool(res["Rp_resolved"] and abs(res["deviation_pct"]) <= tol)
    return res


def check_hold(t, V, I, r_ohm, tol):
    q = float(np.sum(0.5 * (I[1:] + I[:-1]) * np.diff(t)))  # trapezoids
    res = {"t_start_s": float(t[0]), "t_end_s": float(t[-1]), "points": int(len(t)),
           "E_mean_V": float(np.mean(V)), "I_mean_A": float(np.mean(I)),
           "I_sd_A": float(np.std(I)), "charge_C": q}
    if r_ohm:
        expect = res["E_mean_V"] / r_ohm
        res["I_expected_A"] = expect
        res["deviation_pct"] = 100 * (res["I_mean_A"] - expect) / expect if expect else None
        res["pass"] = bool(res["deviation_pct"] is not None and abs(res["deviation_pct"]) <= tol)
    return res


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("csv")
    p.add_argument("--r-ohm", type=float,
                   help="the resistor's meter reading, for C1: Rp and the hold current are checked against it")
    p.add_argument("--tol", type=float, default=3.0, help="pass tolerance in percent (default 3)")
    p.add_argument("--t-col")
    p.add_argument("--v-col")
    p.add_argument("--i-col")
    p.add_argument("--i-unit", choices=["A", "mA", "uA", "µA", "nA"])
    args = p.parse_args()

    d = load(args.csv, args, need_time=True)
    t, V, I = d["t"], d["V"], d["I"]
    on = I != 0.0
    out = {"csv": str(args.csv), "columns": d["columns"], "units": d["units"], "points": int(len(t)),
           "sample_interval_s": float(np.median(np.diff(t))) if len(t) > 1 else None,
           "ocp": [], "lpr": [], "hold": []}
    for a, b in stretches(on):
        sl = slice(a, b)
        if not on[a]:
            out["ocp"].append(check_ocp(t[sl], V[sl]))
        elif b - a >= 3 and np.ptp(V[sl]) >= SWEEP_MIN_SPAN_V:
            out["lpr"].append(check_lpr(t[sl], V[sl], I[sl], args.r_ohm, args.tol))
        else:
            out["hold"].append(check_hold(t[sl], V[sl], I[sl], args.r_ohm, args.tol))
    checks = [r["pass"] for k in ("lpr", "hold") for r in out[k] if "pass" in r]
    if checks:
        out["pass"] = bool(all(checks))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5.5), sharex=True)
    ax1.plot(t, V * 1e3, ".", ms=2)
    ax1.set_ylabel("potential (mV)")
    ax2.plot(t[on], I[on] * 1e9, ".", ms=2, color="C1", label="cell on")
    ax2.set_ylabel("current (nA)")
    ax2.set_xlabel("time (s)")
    for k, color in (("ocp", "0.85"), ("lpr", "#cfe3f5"), ("hold", "#f5e3cf")):
        for r in out[k]:
            for ax in (ax1, ax2):
                ax.axvspan(r["t_start_s"], r["t_end_s"], color=color, lw=0, zorder=0)
    ax2.legend(fontsize=8)
    fig.suptitle(f"{Path(args.csv).name}: grey cell off (OCP), blue LPR, orange hold", fontsize=9)
    fig.tight_layout()
    stem = Path(args.csv).with_suffix("")
    fig.savefig(f"{stem}.check.png", dpi=150)
    Path(f"{stem}.check.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()
