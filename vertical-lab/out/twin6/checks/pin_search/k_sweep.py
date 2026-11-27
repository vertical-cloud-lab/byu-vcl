import sys, numpy as np, faulthandler
faulthandler.enable()
for K in [int(a) for a in sys.argv[1:]]:
    for M, N in ((64, 64), (8, 8), (300, 300), (16, 400), (400, 16)):
        A = np.random.default_rng(K).normal(size=(M, K)); B = np.random.default_rng(K+1).normal(size=(K, N))
        print("K", K, "M", M, "N", N, end=" ", flush=True)
        C = A @ B
        print("ok", flush=True)
