import hashlib, os, numpy as np, scipy.linalg
rng = np.random.default_rng(99)
out = {}
def put(name, a):
    out[name] = hashlib.sha256(np.ascontiguousarray(np.asarray(a, dtype="<f8")).tobytes()).hexdigest()[:12]
x = rng.normal(0, 2.0, 100000)
for n in (2, 3, 4, 5, 7, 8, 12, 16, 30, 31, 32, 33, 64, 120, 300):
    A = rng.normal(size=(n, n)); B = rng.normal(size=(n, 7)); v = rng.normal(size=n); w = rng.normal(size=n)
    S = A @ A.T + n * np.eye(n)
    if n == 300:
        put("matmul300", A @ B); put("matmul_sq300", A @ A); put("gram300", A @ A.T)
        put("chol300", np.linalg.cholesky(S))
        L = scipy.linalg.cholesky(S, lower=True); put("sp.chol300", L)
# K-sweep: where does a GEMM's K start to matter
for K in (128, 192, 200, 224, 240, 256, 257, 300, 384, 400, 512, 640):
    A = np.random.default_rng(K).normal(size=(64, K)); B = np.random.default_rng(K+1).normal(size=(K, 64))
    put(f"K{K}", A @ B)
print(os.environ.get("OPENBLAS_L2_SIZE"), out)
