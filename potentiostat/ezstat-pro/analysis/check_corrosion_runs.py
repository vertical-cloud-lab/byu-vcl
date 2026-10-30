"""Check EZstat-Pro runs of the corrosion checks C1-C3 (README section 7).

Reads an EZware CSV export or EZware's own .nuvdt file, and splits it into
stretches with the cell off and with it on. While the cell is off
(open-circuit monitoring), EZware writes a current of exactly 0 A to the CSV
and NaN to the .nuvdt. Then reports:

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

    python check_corrosion_runs.py ../results/20261024_dummy-runs/20261024-D2.nuvdt
    python check_corrosion_runs.py C1.csv --r-ohm 10000 --tol 3

A CSV's columns are found as in check_dummy_runs.py, which this reuses; the
time column is required. The .nuvdt layout was read from EZware 7.1's files
(2026-10-24) and checked against R2's CSV export, which it matches exactly:
a text header in the first 512 bytes, then from byte 536 one 32-byte
big-endian record per point, a LabVIEW timestamp (i64 seconds since
1904-01-01 UTC, u64 fraction of a second), the current in A and the
potential in V. Writes <file>.check.png and <file>.check.json next to the
input (<file>.nuvdt.check.* for a .nuvdt) and prints a summary.
"""

import argparse
import json
from pathlib import Path

import numpy as np

from check_dummy_runs import load, plt

# A cell-on stretch whose potential spans less than this is a hold, not a sweep.
SWEEP_MIN_SPAN_V = 2e-3

NUVDT_DATA_START = 536
NUVDT_RECORD = np.dtype([("s", ">i8"), ("frac", ">u8"), ("I", ">f8"), ("V", ">f8")])


def read_nuvdt(path):
    """Header text, and t (s from the first point), I (A, NaN with the cell off), V (V)."""
    b = Path(path).read_bytes()
    header = b[:512].decode("latin-1").replace("\r", "").rstrip(" \x00")
    n = (len(b) - NUVDT_DATA_START) // NUVDT_RECORD.itemsize
    rec = np.frombuffer(b, NUVDT_RECORD, count=n, offset=NUVDT_DATA_START)
    t = rec["s"].astype(float) + rec["frac"].astype(float) / 2.0 ** 64
    return header, {"t": t - t[0], "I": rec["I"].astype(float), "V": rec["V"].astype(float),
                    "t0_labview_s": float(t[0]) if n else None}


def stretches(on, t):
    """(start, stop) index pairs of the runs of equal values in a bool array,
    also split where the time between points jumps: a .nuvdt from the
    Corrosion Inhibition Test keeps only the open-circuit points, so each LPR
    shows up as a gap."""
    dt = np.diff(t)
    gap = dt > 5 * np.median(dt) if len(dt) else dt.astype(bool)
    edges = np.flatnonzero((np.diff(on.astype(int)) != 0) | gap) + 1
    bounds = np.concatenate([[0], edges, [len(on)]])
    return [(int(a), int(b)) for a, b in zip(bounds[:-1], bounds[1:]) if b > a]


def is_sweep(t, V):
    """A steady ramp (LPR) rather than one or more potential steps."""
    if len(V) < 3 or np.ptp(V) < SWEEP_MIN_SPAN_V:
        return False
    return abs(np.corrcoef(t, V)[0, 1]) > 0.98


def steps(V, jump=0.01):
    """Split a cell-on stretch at potential steps larger than `jump` (V).

    Works on medians of short blocks, so a noise spike doesn't split it.
    """
    n = len(V)
    k = max(1, n // 400)
    starts, level = [0], np.median(V[:k])
    for j in range(1, n // k):
        m = np.median(V[j * k:(j + 1) * k])
        if abs(m - level) > jump:
            starts.append(j * k)
            level = m
    return [(a, b) for a, b in zip(starts, starts[1:] + [n]) if b - a >= 3]


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

    if args.csv.lower().endswith(".nuvdt"):
        header, d = read_nuvdt(args.csv)
        t, V, I = d["t"], d["V"], d["I"]
        on = np.isfinite(I)
        I = np.where(on, I, 0.0)
        meta = {"nuvdt_header": header.splitlines()}
    else:
        d = load(args.csv, args, need_time=True)
        t, V, I = d["t"], d["V"], d["I"]
        on = I != 0.0
        meta = {"columns": d["columns"], "units": d["units"]}
    out = {"file": str(args.csv), **meta, "points": int(len(t)),
           "sample_interval_s": float(np.median(np.diff(t))) if len(t) > 1 else None,
           "ocp": [], "lpr": [], "hold": []}
    for a, b in stretches(on, t):
        sl = slice(a, b)
        if not on[a]:
            out["ocp"].append(check_ocp(t[sl], V[sl]))
        elif is_sweep(t[sl], V[sl]):
            out["lpr"].append(check_lpr(t[sl], V[sl], I[sl], args.r_ohm, args.tol))
        else:
            for c, e in steps(V[sl]):
                ss = slice(a + c, a + e)
                out["hold"].append(check_hold(t[ss], V[ss], I[ss], args.r_ohm, args.tol))
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
    # A .nuvdt and its CSV export can sit side by side, so a .nuvdt keeps its
    # suffix in the output names.
    stem = args.csv if args.csv.lower().endswith(".nuvdt") else Path(args.csv).with_suffix("")
    fig.savefig(f"{stem}.check.png", dpi=150)
    Path(f"{stem}.check.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()
