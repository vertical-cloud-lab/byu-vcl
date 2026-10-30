# 2026-10-26: C1, DAL's corrosion sequence on the 10.00 kΩ

C1 of [§7 of the runbook](../../README.md#c1-dals-sequence-on-the-1000-kω-no-chemistry), for
[#231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231). Ben Whitney clipped R2's 10 kΩ back
on and asked for C1 ([PR #291](https://github.com/vertical-cloud-lab/byu-vcl/pull/291)). A Claude
session ran EZware over Remote Desktop from des4, 19:51–20:54 UTC (13:51–14:54 MDT). Nobody was at
the PC; the PC's own screen was at its login prompt throughout.

| | |
|---|---|
| Instrument | NuVant EZstat-Pro, metal case. Board NI USB-6221 (OEM) "Dev1" |
| PC | Windows 7 Professional SP1, EZware 7.1.16.1025, LabVIEW Run-Time 2011 SP1, NI-DAQmx 9.7.0. Ours was the only Windows session, and EZware wasn't running when we logged in |
| Load | R2's 10 kΩ resistor, wired as for R2: white clip (reference, counter stacked on it) on one end, black clip (working, working sense) on the other, on paper on the EZstat's top ([photo](20261026-C1-wiring.jpg), camera 0 at 19:49 UTC) |
| Meter | Neoteck NT8233D Pro: **10.00 kΩ** on its 20 kΩ range (2026-10-22), ±1.0 % per listings of the same meter |
| Range | Fixed 1 µA–100 µA (General Method Settings: only the 100uA auto-range box ticked). Electrode area 1 cm² |

## Result: C1 passes, once the range's offset is taken off the hold

| Check | Limit (§7) | Result |
|---|---|---|
| Wiring, cell off | about 0 V | −30 to −56 µV (open leads read 10.3 V on 2026-10-24) |
| OCP | within ±1 mV of 0 | **−42 µV**, SD 13 µV, no drift (+0.001 mV per 10 min over 20 min) |
| Rp, C1's LPR | within 3 % of 10.00 kΩ | **10,000 Ω**, +0.004 % ✅ |
| Rp, the repeat | the same | **9,991 Ω**, −0.09 % ✅. EZware's own figure: 9,990.6 Ω |
| Hold current at +39.94 mV | V/R = 3.994 µA, within 3 % | **3.856 µA** as measured, −3.5 % ❌. With the range's offset taken off, **3.9995 µA**, +0.13 % ✅ |
| Hold charge, 600.4 s | 2.40 mC, within 3 % | 2.315 mC as measured. **2.401 mC** with the offset taken off ✅ |
| Runs over Remote Desktop and ends with Cell OFF | | Yes, every run. EZware was closed with File → Exit at the end, and `tasklist` confirmed it |

![C1: the 20 min OCP, the two LPRs, and the 10 min hold](20261026-C1-summary.png)

- **The offset is steady, so subtracting a same-day value works.** On the 1 µA–100 µA range it was
  −0.1437 µA where C1's LPR line crosses 0 V, −0.1430 µA in the repeat, and −0.146 µA with the
  leads open on 2026-10-24 (D3). The hold's noise was 2.0 nA SD.
- **Don't read 10,000 Ω as 0.004 % accuracy.** It agrees with the meter within the meter's own
  ±1.0 %. R2 found two errors of about 1 % that pull opposite ways in a ±10 mV LPR: on the ±10 V
  potential range, resistance read 1.08 % high, and the ±50 mV potential range reads 0.94 % low.
  C1's LPR stays inside ±50 mV, so they nearly cancel. R2 fitted on its ±50 mV points alone gave
  9,989 Ω, within 0.1 % of today's two.

## EZware reports its own Rp, in a CSV it writes by itself

The Corrosion Inhibition Test writes `<run name>.csv` next to the `.nuvdt` when the run starts, and
adds a row for the LPR, presumably one per LPR (every run so far had one):

```
"Inhibitor","Relative time [s]","Corrosion Potential","Corrosion Resistance"
0 ,1.9E+2 ,0.001429 ,9990.6
```

That's the repeat ([`20261026-C1-lpr2.csv`](20261026-C1-lpr2.csv)). Both numbers are a straight
line through the 9 exported points:
- **Corrosion Resistance** is 1/slope. `check_corrosion_runs.py` gets 9,990.64 Ω from the same
  points.
- **Corrosion Potential** is where the line crosses zero current, +1.429 mV. **It isn't the OCP**
  (−47 µV just before). It's shifted by the range's current offset times Rp:
  −0.143 µA × 10 kΩ = 1.43 mV. On a 2.3 kΩ bench cell that's 0.3 mV, but take E_corr from the
  OCP logged before the LPR, not from this column.
- **Relative time** is about the end of the LPR, 190 s after Start.

**C1's own results file was lost, which is why the repeat was run.** For C1's main run EZware wrote
`20261026-C1-lpr.csv`. The session then exported the LPR from Display Cell Data with the same name,
and copied that into the same folder with `copy /y`, which overwrote EZware's file without asking.
**Export LPRs under a different name from the run's**, as the repeat's
`20261026-C1-lpr2-export.csv` is. The 2026-10-24 dummy run D2 exported under its run's name as well,
so its results file was probably overwritten the same way.

## What ran

| Run | UTC | Technique and settings | What happened |
|---|---|---|---|
| `20261026-C1-lpr` | 19:56:29–20:18:46 | Corrosion Studies → Corrosion Inhibition Tests: open-circuit monitoring, log 1 s, **monitoring time 20 min, measurement interval 20 min**; ±10 mV at 10 mV/min; Account for Rs unticked | OCP 20 min (1,154 points, one every 1.04 s), then one LPR, 9 points from −8.81 to +7.07 mV, one every 12 s. The first LPR point came 18 s after the last OCP point. Cell OFF at the end |
| `20261026-C1-hold` | 20:25:05 | Time Base Techniques → Extended Time Base, potentiostat: 5 s at 0 V, then +0.04 V for 10 min, log 1 s, **Cutoff Current Limit 1E-5 A** | **Stopped after 1 point** ("Scan Ended", Cell OFF), at 3.857 µA. See below |
| `20261026-C1-hold2` | 20:27:02–20:37:02 | The same, with Cutoff Current Limit **1E-7 A** | Ran the full 10 min: 633 points, one every 0.95 s, +39.94 mV and 3.856 µA throughout. The 0 V pretreatment isn't in the file. Cell OFF at the end |
| `20261026-C1-ocp` | 20:38:38–20:45:05 | Corrosion Inhibition Test, monitoring time **5 min**, interval 20 min | **Didn't end at 5 min**: still monitoring at 6 min, so stopped with the Stop button (cell off throughout). **Stopping saved nothing**: the `.nuvdt` and the results CSV hold only their headers |
| `20261026-C1-lpr2` | 20:47:54–20:51:11 | Corrosion Inhibition Test, monitoring time **1 min**, interval **1 min** | OCP 1 min (58 points), then one LPR, the same 9 points as C1's. EZware's results CSV kept |

**EZware details found on the way** (now in the runbook):
- **The measurement interval tops out at 20 min.** 30 was coerced to 20 with no message, so the
  Corrosion Inhibition Test can't do DAL's 30 min of OCP before a single LPR.
- **Extended Time Base opens in galvanostat mode, applying 0.1 A**, with a 1.5 V cutoff. Pick
  Potentiostat in Source Mode first: the fields become Pretreatment Potential, Applied Potential
  and Cutoff Current Limit. Its default 1 A cutoff is "out of range" on the 100 µA range.
- **In potentiostat mode, its Cutoff Current Limit ends the hold once the current is *below* it,**
  like the end of a battery charger's constant-voltage stage. 1E-5 A ended a 3.86 µA hold at once.
  Set it well below the current you expect.
- **Its potentials are absolute.** There's no "vs OCP" option, so a hold at E_corr + 50 mV needs
  the OCP read off and typed in.
- **The export's time columns were off.** Tools → File Export → Data Configuration had only Voltage
  and Current ticked, though D2's export on 2026-10-24 had time. Check it before every export.
- **The file prompt takes `%USERPROFILE%\Documents\EZware_user_Files\<name>`,** which keeps a run's
  file on the PC even when the prompt opens in `\\tsclient\ez`.

## Files

| File | What it is |
|---|---|
| [`20261026-C1-lpr.nuvdt`](20261026-C1-lpr.nuvdt) | C1's 20 min OCP, 1,154 points; current NaN (cell off) |
| [`20261026-C1-lpr.csv`](20261026-C1-lpr.csv) | C1's LPR, exported from Display Cell Data with all five columns. Not EZware's results file, which this overwrote on the PC |
| [`20261026-C1-hold.nuvdt`](20261026-C1-hold.nuvdt) | The hold that stopped at its cutoff: 1 point |
| [`20261026-C1-hold2.nuvdt`](20261026-C1-hold2.nuvdt) | The 10 min hold, 633 points. No CSV export: the `.nuvdt` has the same data |
| [`20261026-C1-ocp.nuvdt`](20261026-C1-ocp.nuvdt), [`.csv`](20261026-C1-ocp.csv) | The stopped OCP: headers only |
| [`20261026-C1-lpr2.nuvdt`](20261026-C1-lpr2.nuvdt) | The repeat's 1 min OCP, 58 points |
| [`20261026-C1-lpr2.csv`](20261026-C1-lpr2.csv) | **EZware's own results** for the repeat: Rp and the zero-current potential |
| [`20261026-C1-lpr2-export.csv`](20261026-C1-lpr2-export.csv) | The repeat's LPR, exported from Display Cell Data |
| `*.check.json`, `*.check.png` | [`check_corrosion_runs.py`](../../analysis/check_corrosion_runs.py)'s output, with `--r-ohm 10000 --tol 3` for the LPRs and the hold |
| [`20261026-C1-summary.png`](20261026-C1-summary.png), [`plot_c1_summary.py`](plot_c1_summary.py) | The figure above, and the script that draws it |
| [`20261026-C1-wiring.jpg`](20261026-C1-wiring.jpg) | Camera 0 at 19:49 UTC, cropped to the clips |

The hold's offset correction, by hand:

```
python analysis/check_corrosion_runs.py results/20261026_c1-10k/20261026-C1-hold2.nuvdt --r-ohm 10000 --tol 3
# I_mean 3.8558 uA; V/R 3.9945 uA; offset -0.1437 uA (C1's LPR at 0 V)
# 3.8558 + 0.1437 = 3.9995 uA, +0.13 %; charge 2.3152 mC + 0.1437 uA x 600.4 s = 2.4014 mC
```
