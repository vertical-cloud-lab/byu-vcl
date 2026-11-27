"""Item-level hashes of numpy's and scipy's BLAS/LAPACK results on fixed inputs (to find which routine and size
differs between CPU identities). Prints JSON {item: sha12}."""
import hashlib, json, sys
import numpy as np
import scipy.linalg, scipy.special, scipy.stats, scipy.spatial.distance, scipy.optimize
rng = np.random.default_rng(99)
out = {}
def put(name, a):
    out[name] = hashlib.sha256(np.ascontiguousarray(np.asarray(a, dtype="<f8")).tobytes()).hexdigest()[:12]
x = rng.normal(0, 2.0, 100000); p = np.abs(x) + 1e-3
for n in (2, 3, 4, 5, 7, 8, 12, 16, 30, 31, 32, 33, 64, 120, 300):
    A = rng.normal(size=(n, n)); B = rng.normal(size=(n, 7)); v = rng.normal(size=n); w = rng.normal(size=n)
    S = A @ A.T + n * np.eye(n)
    put(f"np.dot_vv{n}", [v @ w]); put(f"np.dot_vv_self{n}", [v @ v])
    put(f"np.mv{n}", A @ v); put(f"np.vm{n}", v @ A)
    put(f"np.matmul{n}", A @ B); put(f"np.matmul_sq{n}", A @ A); put(f"np.gram{n}", A @ A.T)
    put(f"np.einsum{n}", np.einsum("ij,jk->ik", A, B))
    put(f"np.outer{n}", np.outer(v, w))
    put(f"np.norm{n}", [np.linalg.norm(v), np.linalg.norm(A)])
    put(f"np.chol{n}", np.linalg.cholesky(S)); put(f"np.solve{n}", np.linalg.solve(S, B))
    put(f"np.eigvalsh{n}", np.linalg.eigvalsh(S)); put(f"np.inv{n}", np.linalg.inv(S))
    put(f"np.det{n}", [np.linalg.slogdet(S)[1]]); put(f"np.lstsq{n}", np.linalg.lstsq(A, B, rcond=None)[0])
    L = scipy.linalg.cholesky(S, lower=True)
    put(f"sp.chol{n}", L); put(f"sp.cho_solve{n}", scipy.linalg.cho_solve((L, True), B))
    put(f"sp.solve_triangular{n}", scipy.linalg.solve_triangular(L, B, lower=True))
    put(f"sp.cdist{n}", scipy.spatial.distance.cdist(A, A[: max(n // 2, 1)]))
    f = scipy.linalg.blas
    put(f"sp.ddot{n}", [f.ddot(v, w)]); put(f"sp.dnrm2{n}", [f.dnrm2(v)]); put(f"sp.daxpy{n}", f.daxpy(v, w.copy(), a=1.7))
    put(f"sp.dgemv{n}", f.dgemv(1.0, A, v)); put(f"sp.dgemm{n}", f.dgemm(1.0, A, B)); put(f"sp.dsyrk{n}", f.dsyrk(1.0, A))
    put(f"sp.dtrsm{n}", f.dtrsm(1.0, L, B, lower=1)); put(f"sp.dscal{n}", f.dscal(1.7, v.copy()))
for N in (10, 100, 1000, 100000):
    put(f"np.sum{N}", [x[:N].sum()]); put(f"np.dot_big{N}", [x[:N] @ p[:N]]); put(f"np.norm_big{N}", [np.linalg.norm(x[:N])])
    put(f"sp.ddot_big{N}", [scipy.linalg.blas.ddot(x[:N], p[:N])]); put(f"sp.dnrm2_big{N}", [scipy.linalg.blas.dnrm2(x[:N])])
    put(f"sp.dasum_big{N}", [scipy.linalg.blas.dasum(x[:N])])
put("sp.ndtr", scipy.special.ndtr(x)); put("sp.norm_cdf", scipy.stats.norm.cdf(x)); put("sp.norm_pdf", scipy.stats.norm.pdf(x))
put("sp.erf", scipy.special.erf(x)); put("sp.gammaln", scipy.special.gammaln(p)); put("sp.logsumexp", [scipy.special.logsumexp(x[:5000])])
put("sp.expit", scipy.special.expit(x)); put("sp.sobol", scipy.stats.qmc.Sobol(9, seed=3).random(256))
print(json.dumps(out))
