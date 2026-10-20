"""Check EZstat-Pro dummy-load runs R1-R3 against the runbook's pass criteria.

R1, R2: a CV on a resistor. Fits I = V/R + I0 and compares R with the
multimeter reading (pass: within 1 %).

R3: step impedance on the dummy cell, 1 kOhm in series with (10 kOhm in
parallel with 1 uF). Fits each current pulse with V = a + b(1 - exp(-t/tau)):
Rs = a/dI, Rct = b/dI, Cdl = tau/Rct (pass: each within 5 % of the parts'
values). Rs needs a sampling interval much shorter than tau = 10 ms; see
check_sis.

The column layout of an EZware CSV export depends on what was ticked under
Tools > File Export > Data Configuration, so columns are found by name
("time", "potential"/"voltage", "current") and units read from the header,
e.g. "Current (mA)". Override with --t-col/--v-col/--i-col (0-based index or
exact header text) and --i-unit if the guess is wrong.

    python check_dummy_runs.py R1 ../results/20261021_dummy-loads/20261021-R1.csv --r-ohm 998.7
    python check_dummy_runs.py R3 ../results/20261021_dummy-loads/20261021-R3.csv

Writes <csv>.check.png and <csv>.check.json next to the CSV and prints a summary.
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

UNIT_SCALE = {"a": 1.0, "ma": 1e-3, "ua": 1e-6, "na": 1e-9,
              "v": 1.0, "mv": 1e-3, "s": 1.0, "ms": 1e-3}


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def read_table(path):
    """Return (header, rows) from the first row followed by numeric rows."""
    text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
    dialect = csv.excel_tab if text.count("\t") > text.count(",") else csv.excel
    lines = [r for r in csv.reader(text.splitlines(), dialect) if any(c.strip() for c in r)]
    for k in range(len(lines) - 2):
        head = [c.strip() for c in lines[k]]
        nxt = lines[k + 1:k + 3]
        if (sum(not _is_number(c) for c in head if c) >= 2
                and all(len(r) >= 2 and all(_is_number(c) for c in r if c.strip()) for r in nxt)):
            rows = []
            for r in lines[k + 1:]:
                cells = [c.strip() for c in r]
                if cells and all(_is_number(c) for c in cells if c):
                    rows.append([float(c) if c else np.nan for c in cells])
            width = max(len(r) for r in rows)
            data = np.full((len(rows), width), np.nan)
            for i, r in enumerate(rows):
                data[i, :len(r)] = r
            return head, data
    sys.exit(f"{path}: found no header row followed by numeric rows")


def find_column(header, override, patterns, what):
    if override is not None:
        if override.isdigit():
            return int(override)
        if override in header:
            return header.index(override)
        sys.exit(f"--{what}-col {override!r} is not a column index or header: {header}")
    for pat in patterns:
        for i, h in enumerate(header):
            if re.search(pat, h, re.IGNORECASE):
                return i
    sys.exit(f"no {what} column found in {header}; pass --{what}-col")


def unit_of(name, default):
    """SI scale from a unit in brackets, e.g. 'Current (mA)' -> (1e-3, 'ma')."""
    m = re.search(r"[\(\[]\s*([^\)\]]+?)\s*[\)\]]", name)
    unit = (m.group(1) if m else default).strip().lower()
    unit = unit.replace("\u00b5", "u").replace("\u03bc", "u")
    return UNIT_SCALE.get(unit), unit


def load(path, args, need_time):
    header, data = read_table(path)
    # Prefer measured over applied columns, and skip "current range".
    iv = find_column(header, args.v_col, [r"meas\w*.*(potential|voltage)", r"(potential|voltage).*meas",
                                          r"potential", r"voltage", r"\bewe\b", r"^e\b", r"^v\b"], "v")
    ii = find_column(header, args.i_col, [r"meas\w*.*current", r"current.*meas",
                                          r"current(?!\s*range)", r"^i\b"], "i")
    v_scale, v_unit = unit_of(header[iv], "v")
    i_scale, i_unit = unit_of(header[ii], "a")
    if args.i_unit:
        i_scale, i_unit = unit_of(f"({args.i_unit})", "a")
    if v_scale is None or i_scale is None:
        sys.exit(f"unknown unit in {header[iv]!r} or {header[ii]!r}; pass --i-unit")
    out = {"header": header, "V": data[:, iv] * v_scale, "I": data[:, ii] * i_scale,
           "columns": {"V": header[iv], "I": header[ii]}, "units": {"V": v_unit, "I": i_unit}}
    if need_time:
        it = find_column(header, args.t_col, [r"time", r"^t\b"], "t")
        t_scale, t_unit = unit_of(header[it], "s")
        out["t"] = data[:, it] * (t_scale or 1.0)
        out["columns"]["t"], out["units"]["t"] = header[it], t_unit
    ok = np.isfinite(out["V"]) & np.isfinite(out["I"])
    for k in ("V", "I", "t"):
        if k in out:
            out[k] = out[k][ok]
    return out


def check_resistor(d, r_ohm, tol):
    V, I = d["V"], d["I"]
    A = np.column_stack([V, np.ones_like(V)])
    (g, i0), *_ = np.linalg.lstsq(A, I, rcond=None)
    resid = I - (g * V + i0)
    r_fit = 1.0 / g
    res = {"R_fit_ohm": r_fit, "offset_A": i0,
           "r_squared": 1 - np.sum(resid ** 2) / np.sum((I - I.mean()) ** 2),
           "max_residual_A": float(np.max(np.abs(resid))),
           "I_range_A": [float(I.min()), float(I.max())], "points": int(len(V))}
    if r_ohm:
        res["R_meter_ohm"] = r_ohm
        res["deviation_pct"] = 100 * (r_fit - r_ohm) / r_ohm
        res["pass"] = bool(abs(res["deviation_pct"]) <= tol)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6), sharex=True,
                                   gridspec_kw={"height_ratios": [3, 1]})
    ax1.plot(V, I * 1e3, ".", ms=2, label="data")
    vv = np.linspace(V.min(), V.max(), 2)
    ax1.plot(vv, (g * vv + i0) * 1e3, "-", lw=1, label=f"fit: R = {r_fit:.1f} Ω")
    ax1.set_ylabel("current (mA)")
    ax1.legend()
    ax2.plot(V, resid * 1e6, ".", ms=2)
    ax2.set_ylabel("residual (µA)")
    ax2.set_xlabel("potential (V)")
    return res, fig


def fit_pulse(t, v):
    """Least squares for v = a + b(1 - exp(-t/tau)).

    For a fixed tau the model is linear in a and b, so search tau on a coarse
    log grid, then on a fine grid around the best value.
    """
    def sse_at(tau):
        A = np.column_stack([np.ones_like(t), 1 - np.exp(-t / tau)])
        coef, *_ = np.linalg.lstsq(A, v, rcond=None)
        return float(np.sum((A @ coef - v) ** 2)), coef[0], coef[1], tau

    span = max(t[-1] - t[0], 1e-6)
    best = min((sse_at(tau) for tau in np.geomspace(span / 1e4, span, 400)), key=lambda r: r[0])
    fine = np.linspace(best[3] / 1.03, best[3] * 1.03, 301)
    best = min((sse_at(tau) for tau in fine), key=lambda r: r[0])
    return best[1:]


def check_sis(d, nominal, tol):
    """Fit each current pulse; Rs needs the step time, Rct and tau do not.

    The step falls somewhere between the last sample before the pulse and the
    first sample in it, so time is counted from their midpoint. That leaves an
    uncertainty in Rs of about Rct * (half a sample) / tau, reported as
    Rs_uncertainty_ohm. The plateau (Rs + Rct) and tau don't depend on the
    step time, so they are always checked. Rs, Rct and Cdl are checked only
    when that uncertainty is within the tolerance, since splitting the
    plateau into Rs and Rct needs the step time.
    """
    t, V, I = d["t"], d["V"], d["I"]
    base = np.median(I)  # most samples sit at the initial current
    amp = I[np.argmax(np.abs(I - base))] - base
    on = np.abs(I - base) > 0.5 * abs(amp)
    change = np.diff(on.astype(int))
    starts = np.flatnonzero(change == 1) + 1
    ends = np.flatnonzero(change == -1) + 1
    results = []
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(t, V * 1e3, ".", ms=2, label="data")
    prev_end = 0
    for s0 in starts:
        later = ends[ends > s0]
        e0 = later[0] if len(later) else len(t)
        if s0 - prev_end < 3 or e0 - s0 < 10:
            prev_end = e0
            continue
        pre = slice(max(prev_end, s0 - 20), s0)
        v0, i0 = np.mean(V[pre]), np.mean(I[pre])
        seg = slice(s0, e0)
        dI = np.mean(I[seg]) - i0
        t_step = 0.5 * (t[s0 - 1] + t[s0])
        half = 0.5 * (t[s0] - t[s0 - 1])
        tt = t[seg] - t_step
        a, b, tau = fit_pulse(tt, V[seg] - v0)
        rs, rct = a / dI, b / dI
        cdl = tau / rct if rct else float("nan")
        rs_err = abs(rct) * (1 - np.exp(-half / tau)) if tau > 0 else float("inf")
        rs_resolved = bool(rs_err <= tol / 100 * nominal["Rs"])

        def within(x, n):
            return abs(x / n - 1) * 100 <= tol

        checks = {"Rs+Rct": within(rs + rct, nominal["Rs"] + nominal["Rct"]),
                  "tau": within(tau, nominal["Rct"] * nominal["Cdl"])}
        if rs_resolved:
            checks.update(Rs=within(rs, nominal["Rs"]), Rct=within(rct, nominal["Rct"]),
                          Cdl=within(cdl, nominal["Cdl"]))
        results.append({"pulse_start_s": float(t_step), "dI_A": float(dI), "Rs_ohm": rs,
                        "Rs_uncertainty_ohm": rs_err, "Rs_resolved": rs_resolved,
                        "Rct_ohm": rct, "Cdl_F": cdl, "tau_s": tau,
                        "sample_interval_s": 2 * half, "points": int(e0 - s0),
                        "checks": {k: bool(v) for k, v in checks.items()},
                        "pass": bool(all(checks.values()))})
        tf = np.linspace(0, tt[-1], 300)
        ax.plot(t_step + tf, (v0 + a + b * (1 - np.exp(-tf / tau))) * 1e3, "-", lw=1,
                label=f"fit: Rs {rs:.0f} \u00b1 {rs_err:.0f} \u03a9, Rct {rct:.0f} \u03a9, "
                      f"Cdl {cdl * 1e6:.2f} \u00b5F")
        prev_end = e0
    if not results:
        sys.exit("no usable current pulse found in the current column")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("potential (mV)")
    ax.legend(fontsize=8)
    return {"pulses": results, "nominal": nominal, "tolerance_pct": tol,
            "pass": bool(all(r["pass"] for r in results))}, fig


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("run", choices=["R1", "R2", "R3"])
    p.add_argument("csv")
    p.add_argument("--r-ohm", type=float, help="multimeter reading of the resistor (R1, R2)")
    p.add_argument("--rs", type=float, default=1000.0, help="R3 series resistor, ohm")
    p.add_argument("--rct", type=float, default=10000.0, help="R3 parallel resistor, ohm")
    p.add_argument("--cdl", type=float, default=1e-6, help="R3 capacitor, F")
    p.add_argument("--tol", type=float, help="pass tolerance in percent (default 1 for R1/R2, 5 for R3)")
    p.add_argument("--t-col")
    p.add_argument("--v-col")
    p.add_argument("--i-col")
    p.add_argument("--i-unit", choices=["A", "mA", "uA", "µA", "nA"])
    args = p.parse_args()

    d = load(args.csv, args, need_time=args.run == "R3")
    if args.run == "R3":
        res, fig = check_sis(d, {"Rs": args.rs, "Rct": args.rct, "Cdl": args.cdl},
                             args.tol if args.tol is not None else 5.0)
    else:
        res, fig = check_resistor(d, args.r_ohm, args.tol if args.tol is not None else 1.0)
    res = {"run": args.run, "csv": str(args.csv), "columns": d["columns"], "units": d["units"], **res}
    fig.suptitle(f"{Path(args.csv).name}: {args.run}")
    fig.tight_layout()
    stem = Path(args.csv).with_suffix("")
    fig.savefig(f"{stem}.check.png", dpi=150)
    Path(f"{stem}.check.json").write_text(json.dumps(res, indent=2, default=float) + "\n")
    print(json.dumps(res, indent=2, default=float))


if __name__ == "__main__":
    main()
