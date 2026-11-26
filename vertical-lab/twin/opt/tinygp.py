"""A fitted node's Gaussian process in numpy, for round 3's acquisitions (twin/opt/policies3.py).

BoTorch fits each node (``twin.opt.gp.Node``: ``SingleTaskGP``, an ARD RBF kernel with unit variance, a constant
mean, Gaussian noise and a ``Standardize`` outcome transform on targets the Node has already standardized). Round 3
needs the same posterior many times a decision, with extra rows that the fit never saw, so ``TinyGP`` copies the
fitted hyperparameters and training data into numpy and does the algebra itself:

* ``predict`` and ``cov`` (posterior mean, variance, and covariance with a point), equal to ``Node.predict`` to
  rounding (checked in twin/tests/test_round3.py);
* ``with_rows``: the same GP conditioned on extra (pseudo-)observations at fixed hyperparameters. With the posterior
  mean as the value this is the kriging believer (Ginsbourger et al. 2010) for evaluations still in flight; with a
  sampled value, a Monte Carlo fantasy.
"""
from __future__ import annotations

import numpy as np


class TinyGP:
    def __init__(self, node):
        m = node.model
        self.X = m.train_inputs[0].detach().numpy().astype(float)
        self.Yt = m.train_targets.detach().numpy().astype(float).reshape(-1)
        self.ls = m.covar_module.lengthscale.detach().numpy().reshape(-1).astype(float)
        self.noise = float(m.likelihood.noise.detach().numpy().reshape(-1)[0])
        self.c = float(m.mean_module.constant.detach().numpy().reshape(-1)[0])
        ot = getattr(m, "outcome_transform", None)
        self.m_ot = float(ot.means.detach().numpy().reshape(-1)[0]) if ot is not None else 0.0
        self.s_ot = float(ot.stdvs.detach().numpy().reshape(-1)[0]) if ot is not None else 1.0
        self.ymean, self.ystd = float(node.ymean), float(node.ystd)
        self._factor()

    # -------------------------------------------------------------------------------------------- algebra
    def _k(self, A, B):
        A = np.asarray(A, float) / self.ls
        B = np.asarray(B, float) / self.ls
        d2 = (A * A).sum(-1)[..., :, None] + (B * B).sum(-1)[..., None, :] - 2.0 * A @ np.swapaxes(B, -1, -2)
        return np.exp(-0.5 * np.maximum(d2, 0.0))

    def _factor(self):
        K = self._k(self.X, self.X) + (self.noise + 1e-8) * np.eye(len(self.X))
        self.L = np.linalg.cholesky(K)
        self.alpha = np.linalg.solve(self.L.T, np.linalg.solve(self.L, self.Yt - self.c))

    def to_t(self, y):
        return ((np.asarray(y, float) - self.ymean) / self.ystd - self.m_ot) / self.s_ot

    def from_t(self, mu_t, var_t):
        sc = self.s_ot * self.ystd
        return (mu_t * self.s_ot + self.m_ot) * self.ystd + self.ymean, np.sqrt(np.maximum(var_t, 1e-12)) * sc

    def _post_t(self, U):
        U = np.asarray(U, float)
        sh = U.shape[:-1]
        U2 = U.reshape(-1, U.shape[-1])
        Ks = self._k(U2, self.X)
        mu = self.c + Ks @ self.alpha
        V = np.linalg.solve(self.L, Ks.T)
        var = 1.0 - (V * V).sum(0)
        return mu.reshape(sh), var.reshape(sh), V

    # -------------------------------------------------------------------------------------------- public
    def predict(self, U):
        """Posterior mean and standard deviation (original units) at U (..., d)."""
        mu, var, _ = self._post_t(U)
        return self.from_t(mu, var)

    def sample(self, U, S, rng):
        """S independent marginal draws, like Node.sample: (M, d) -> (S, M); (S, M, d) -> (S, M)."""
        U = np.asarray(U, float)
        mu, sd = self.predict(U)
        z = rng.standard_normal((S,) + mu.shape[-1:]) if U.ndim == 2 else rng.standard_normal(mu.shape)
        return mu + sd * z

    def cov_with(self, U, z):
        """Posterior covariance (original units squared) between each row of U (M, d) and one point z (d,), and the
        point's variance including noise: what a fantasy observation at z does to the posterior at U."""
        U = np.asarray(U, float).reshape(-1, len(self.ls))
        z = np.asarray(z, float).reshape(1, -1)
        _, _, Vu = self._post_t(U)
        _, var_z, Vz = self._post_t(z)
        c = self._k(U, z)[:, 0] - (Vu * Vz).sum(0)
        sc2 = (self.s_ot * self.ystd) ** 2
        return c * sc2, (float(var_z[0]) + self.noise) * sc2

    def with_rows(self, Xn, yn):
        """A copy conditioned on extra observations (original units), hyperparameters fixed."""
        g = object.__new__(TinyGP)
        g.__dict__.update(self.__dict__)
        Xn = np.asarray(Xn, float).reshape(-1, self.X.shape[1])
        if len(Xn) == 0:
            return g
        g.X = np.vstack([self.X, Xn])
        g.Yt = np.concatenate([self.Yt, self.to_t(np.asarray(yn, float).reshape(-1))])
        g._factor()
        return g
