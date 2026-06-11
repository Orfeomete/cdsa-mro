"""
LIME local interpretable model-agnostic explanations — NumPy reference
implementation (v2).

Reference: Ribeiro, Singh & Guestrin (2016), "Why Should I Trust You?",
ACM KDD.

Fits a locally weighted ridge-regression surrogate around a single input
by Gaussian perturbation, yielding per-feature local importance weights
for one action class. Used at feature granularity, complementing the
modality-level SHAP explainer.
"""

from __future__ import annotations

import numpy as np


class LIMEExplainer:
    """Local linear surrogate via perturbation + weighted ridge regression."""

    def __init__(self, predict_fn, n_samples: int = 512, sigma: float = 0.25,
                 ridge: float = 1e-3, seed: int = 42):
        self.predict_fn = predict_fn      # callable(x: (d,)) -> scores
        self.n_samples = int(n_samples)
        self.sigma = float(sigma)
        self.ridge = float(ridge)
        self.rng = np.random.default_rng(seed)

    def explain(self, x: np.ndarray, action: int | None = None) -> dict:
        x = np.asarray(x, dtype=float).ravel()
        d = x.shape[0]
        base_scores = np.asarray(self.predict_fn(x), dtype=float)
        a = int(np.argmax(base_scores)) if action is None else int(action)

        # 1) perturb around x
        Z = x + self.rng.normal(0.0, self.sigma, size=(self.n_samples, d))
        y = np.array([np.asarray(self.predict_fn(z), dtype=float)[a] for z in Z])

        # 2) locality kernel (RBF on input distance)
        dist2 = ((Z - x) ** 2).sum(axis=1)
        w = np.exp(-dist2 / (2.0 * (self.sigma * np.sqrt(d)) ** 2))

        # 3) weighted ridge regression (closed form) on centred data
        Zc = Z - x
        yc = y - y.mean()
        A = Zc.T @ (Zc * w[:, None]) + self.ridge * np.eye(d)
        b = Zc.T @ (w * yc)
        coefs = np.linalg.solve(A, b)

        order = np.argsort(-np.abs(coefs))
        return {
            "action": a,
            "coefficients": coefs.tolist(),
            "top_features": [{"index": int(i), "weight": float(coefs[i])}
                             for i in order[:10]],
            "intercept": float(y.mean()),
        }
