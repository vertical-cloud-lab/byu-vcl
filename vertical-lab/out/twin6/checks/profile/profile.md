# Round 6: where an automated-lab GP run spends its time

Made by `python out/twin6/checks/profile/summarize.py` from py-spy's raw samples of live timing runs (seed 0, the automated lab stocked). Share of samples in each function and everything it calls. Everything is simulated.

| | BOFN, 16x, day ~340 | pKGFN, 64x, day ~320 | BOFN, 16x, day ~390 |
|---|---|---|---|
| samples | 2,930 | 2,915 | 2,199 |
| proposing (all) (`Net3.propose`) | 93.6 % | 83.6 % | 94.5 % |
| valuing candidates (`Net3._candidates`) | 80.2 % | 74.9 % | 38.6 % |
| GP prediction (`Node.predict`) | 73.3 % | 58.7 % | 69.4 % |
| the atomize node's batched search (`_Six._p_powder`) | 51.4 % | 49.8 % | 30.6 % |
| GP draws through a network (`Node.sample`) | 30.2 % | 19.2 % | 46.5 % |
| copper's utility draws (`Net3._ucu`) | 10.4 % | 5.9 % | 32.9 % |
| aluminium's utility draws (`Net3.utility_samples_al`) | 20.3 % | 13.6 % | 13.8 % |
| refreshing the new designs' list (`Net3._refresh_new`) | 12.9 % | 7.2 % | 55.9 % |
| GP fitting (`Node.fit`) | 1.0 % | 5.1 % | 11.7 % |
| gpytorch's predictive covariance (`DefaultPredictionStrategy.exact_predictive_covar`) | 52.6 % | 38.1 % | 51.8 % |
| the HPC stream (`Twin6._stream_tick`) | 2.6 % | 13.9 % | 0.6 % |
