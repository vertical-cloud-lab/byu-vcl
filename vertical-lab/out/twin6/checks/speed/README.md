# Round 6: two speed measurements (simulated runs; timings on this job's AMD EPYC 9V74, other runs going at once)

* **The atomize node's search** (`twin/opt/net6.py`): round 5's search (one GP prediction per candidate, features
  rebuilt from the whole design) against round 6's (features built once per composition, 16 candidates' trials
  predicted per call), the same automated-lab BOFN run (stocked, seed 0, 1x, 200 days), run side by side:
  233.7 s against 218.7 s, 6 % faster, with the same results (the same demonstrations at the same hours, the same lots)
  ([`search_round5.json`](search_round5.json), [`search_round6.json`](search_round6.json), [`speed_test.py`](speed_test.py)).
  The search's share of a run grows once the atomize node has data, so the gain grows over two years, but it is
  modest.
* **MKL's conditional numerical reproducibility** (`MKL_CBWR=COMPATIBLE`, part of the `portable` pin): the same
  conventional-lab BOFN run (stocked, seed 0, 1x, 220 days) with it and without it, side by side: 90.5 s against
  85.5 s, 6 % slower, with the same demonstrations ([`mkl_cnr_compatible.json`](mkl_cnr_compatible.json),
  [`mkl_cnr_off.json`](mkl_cnr_off.json), [`cbwr_test.py`](cbwr_test.py)). Alone, MKL's Cholesky, solve and
  products at a GP's sizes take 2-4 times as long under it ([`mklbench.py`](mklbench.py)); they are a small part of a
  run.
