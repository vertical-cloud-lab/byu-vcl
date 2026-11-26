"""Gaussian-process helpers on BoTorch, sized for a 4-core runner running three twins at once.

* ``Node``: one output of a function-network node, or a plain objective: an ARD GP (BoTorch's ``SingleTaskGP``
  defaults: an RBF kernel with dimension-scaled log-normal lengthscale priors, Hvarfner et al. 2024), a MAP SAAS
  GP (``get_map_saas_model``: half-Cauchy shrinkage on the inverse lengthscales, Eriksson & Jankowiak 2021, fit to the
  MAP point), or a fully Bayesian SAAS GP (``SaasFullyBayesianSingleTaskGP`` with NUTS). Hyperparameters are refit
  when the data have grown enough (``refit_every``); in between the model is rebuilt on the new data with the
  previous hyperparameters, which costs milliseconds.
* ``sample``: independent marginal posterior draws at a batch of inputs (``(..., d)`` -> ``(S, ...)``), which is all an
  expected-improvement estimate over many candidates needs.
"""
from __future__ import annotations

import math
import time
import warnings

import numpy as np
import torch

warnings.filterwarnings("ignore")
torch.set_num_threads(1)
DT = torch.double
STATS = {"fits": 0, "fit_s": 0.0, "nuts": 0, "nuts_s": 0.0}


def _hyper(state: dict) -> dict:
    return {k: v for k, v in state.items() if "outcome_transform" not in k and "train" not in k
            and "input_transform" not in k}


class Node:
    def __init__(self, kind: str = "gp", refit_every: int = 8, max_n: int = 600, nuts=(128, 128, 8), seed=0,
                 nuts_growth: float = 1.5):
        self.kind, self.refit_every, self.max_n, self.nuts, self.seed = kind, refit_every, max_n, nuts, seed
        self.nuts_growth = nuts_growth
        self.model, self.state, self.n_fit, self.n = None, None, 0, 0
        self.mcmc = None                 # saas_nuts: the last NUTS run's thinned hyperparameter samples
        self.ymean, self.ystd = 0.0, 1.0
        self.growth = 1.0                # round 3: also wait for the data to grow by this factor before a refit

    def ready(self) -> bool:
        return self.model is not None

    def fit(self, X, y, rng=None):
        X = np.asarray(X, float)
        y = np.asarray(y, float).reshape(-1)
        ok = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
        X, y = X[ok], y[ok]
        if len(y) < 3:
            self.model = None
            return
        if len(y) > self.max_n:                       # keep the newest half and a random half of the rest
            keep_new = np.arange(len(y) - self.max_n // 2, len(y))
            r = np.random.default_rng(len(y))
            old = r.choice(len(y) - self.max_n // 2, self.max_n - self.max_n // 2, replace=False)
            idx = np.concatenate([old, keep_new])
            X, y = X[idx], y[idx]
        if self.model is not None and len(y) == self.n:
            return
        self.ymean, self.ystd = float(y.mean()), float(y.std() + 1e-6)
        Xt = torch.tensor(X, dtype=DT)
        Yt = torch.tensor(((y - self.ymean) / self.ystd).reshape(-1, 1), dtype=DT)
        need_fit = self.state is None or len(y) >= max(self.n_fit + self.refit_every, math.ceil(self.n_fit * self.growth))
        t0 = time.time()
        if self.kind == "saas_nuts":
            # NUTS on a geometric schedule: a fresh chain when the data have grown by refit_every points and by the
            # factor nuts_growth since the last one (n = 3, 7, 11, 17, 26, 39, 59, 89, 134, ... at 4 and 1.5); in
            # between, the model is rebuilt on the new data with the last chain's hyperparameter samples (the same
            # reuse the MAP GPs get). A chain at every new point cost 25-170 s at n = 30-140 on the runner, about
            # 33 CPU-hours for 12 SAASBO seeds.
            from botorch.fit import fit_fully_bayesian_model_nuts
            from botorch.models.fully_bayesian import SaasFullyBayesianSingleTaskGP
            m = SaasFullyBayesianSingleTaskGP(Xt, Yt)
            due = self.mcmc is None or len(y) >= max(self.n_fit + self.refit_every,
                                                     math.ceil(self.n_fit * self.nuts_growth))
            if due:
                cap = {}
                orig = m.load_mcmc_samples

                def _capture(samples, _orig=orig):
                    cap["s"] = {kk: vv.detach().clone() for kk, vv in samples.items()}
                    return _orig(samples)

                m.load_mcmc_samples = _capture
                w, ns, th = self.nuts
                fit_fully_bayesian_model_nuts(m, warmup_steps=w, num_samples=ns, thinning=th, disable_progbar=True,
                                              seed=self.seed + len(y))
                self.mcmc, self.n_fit = cap.get("s"), len(y)
                STATS["nuts"] += 1
                STATS["nuts_s"] += time.time() - t0
            else:
                m.load_mcmc_samples(self.mcmc)
                m.eval()
            self.model, self.n = m, len(y)
            return
        if self.kind == "saas_map":
            from botorch.models.map_saas import get_map_saas_model
            m = get_map_saas_model(Xt, Yt)
            if isinstance(m, tuple):
                m = m[0]
        else:
            from botorch.models import SingleTaskGP
            m = SingleTaskGP(Xt, Yt)
        if need_fit:
            from botorch.fit import fit_gpytorch_mll
            from gpytorch.mlls import ExactMarginalLogLikelihood
            try:
                fit_gpytorch_mll(ExactMarginalLogLikelihood(m.likelihood, m))
            except Exception:
                pass
            self.state = _hyper(m.state_dict())
            self.n_fit = len(y)
            STATS["fits"] += 1
            STATS["fit_s"] += time.time() - t0
        else:
            try:
                m.load_state_dict(self.state, strict=False)
            except Exception:
                pass
        m.eval()
        self.model, self.n = m, len(y)

    def predict(self, X):
        """Posterior mean and standard deviation (original units) at X (..., d)."""
        Xt = torch.as_tensor(np.asarray(X, float), dtype=DT)
        with torch.no_grad():
            post = self.model.posterior(Xt)
            mu = post.mean.squeeze(-1)
            var = post.variance.squeeze(-1)
            if self.kind == "saas_nuts":           # mixture over the MCMC samples: (s, ..., )
                m = mu.mean(0)
                v = (var + mu ** 2).mean(0) - m ** 2
                mu, var = m, v
        return mu.numpy() * self.ystd + self.ymean, np.sqrt(np.clip(var.numpy(), 1e-12, None)) * self.ystd

    def sample(self, X, S, rng):
        """S independent marginal draws at each input: X (M, d) -> (S, M); X (S, M, d) -> (S, M)."""
        X = np.asarray(X, float)
        mu, sd = self.predict(X)
        z = rng.standard_normal((S,) + mu.shape[-1:]) if X.ndim == 2 else rng.standard_normal(mu.shape)
        return mu + sd * z


def expected_improvement(samples_u: np.ndarray, best: float) -> np.ndarray:
    """MC expected improvement over ``best`` from utility samples (S, M)."""
    return np.maximum(samples_u - best, 0.0).mean(axis=0)
