# 2026-10-24: dummy runs of the corrosion checks, leads open

Sterling asked for "whatever you can on the ezstat in current config", as dummy runs of the tests
to come ([PR #291](https://github.com/vertical-cloud-lab/byu-vcl/pull/291)). A Claude session ran
EZware over Remote Desktop from des4, 05:43–06:20 UTC (23:43–00:20 MDT). Nobody was in the lab.

| | |
|---|---|
| Instrument | NuVant EZstat-Pro, serial `EZST15073101 V2`, metal case. Board NI USB-6221 (OEM) "Dev1" |
| PC | Windows 7 Professional SP1, EZware 7.1.16.1025, LabVIEW Run-Time 2011 SP1, NI-DAQmx 9.7.0. Ours was the only Windows session; EZware wasn't running when we logged in |
| Leads | **Open.** The 10 kΩ from R2 has been taken off. The white clip (reference, counter stacked on it) and the black clip (working, working sense) are hooked onto each other, but don't conduct: the cell-off reading was 10.3 V, as with nothing connected, and D1 measured no slope (below) ([photo](20261024-leads-0539.jpg)) |

## What ran

| Run | Stands in for | Technique and settings | Result |
|---|---|---|---|
| D1 | C2's low-current range | Linear Sweep Voltammetry, −10 → +10 mV absolute at 0.167 mV/s, after 5 s at −10 mV. **10 nA–1 µA range**, fixed (only the 1uA auto-range box ticked). Cell ON After Measurement unticked | Ran and exported. With the leads open, the current is the floor: **−0.555 nA mean, 0.020 nA SD**, no slope (fit 0.53 GΩ, unresolved). **Only 9 points**, one per 2 mV (every 12 s), and the last two (+9, +10 mV) are missing from the export |
