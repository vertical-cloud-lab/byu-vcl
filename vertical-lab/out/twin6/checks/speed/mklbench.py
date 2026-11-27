import os, time, torch
torch.set_num_threads(1)
torch.manual_seed(0)
def bench():
    out = {}
    for n in (64, 200, 300):
        A = torch.randn(n, n, dtype=torch.double); S = A @ A.T + n * torch.eye(n, dtype=torch.double)
        B = torch.randn(n, 64, dtype=torch.double); X = torch.randn(1024, n, dtype=torch.double)
        t = time.perf_counter(); k = 0
        while time.perf_counter() - t < 0.4:
            L = torch.linalg.cholesky(S); torch.cholesky_solve(B, L); X @ S; torch.exp(X); k += 1
        out[n] = round((time.perf_counter() - t) / k * 1e3, 3)
    return out
print(os.environ.get("MKL_CBWR"), bench())
