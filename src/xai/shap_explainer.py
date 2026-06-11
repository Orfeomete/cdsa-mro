"""
SHAP modality contribution explainer — NumPy reference implementation (v2).

Reference: Lundberg & Lee (2017), A Unified Approach to Interpreting
Model Predictions, NeurIPS.

For the three CDSA-MRO modalities the Shapley value is computed EXACTLY
by enumerating all 2^3 coalitions (no sampling approximation needed at
modality granularity). A modality "absent" from a coalition is replaced
by its baseline latent (default: zero vector, i.e. uninformative input).

Output: per-modality contribution to the model output for a chosen
action class, plus normalised percentage shares as reported on the
platform FRL Agent Panel and in the manuscripts.
"""

from __future__ import annotations

from itertools import combinations
from math import factorial

import numpy as np

MODALITIES = ("engine", "cyber", "maint")


class SHAPModalityExplainer:
    """Exact Shapley values over modality groups.

    Parameters
    ----------
    predict_fn : callable(h_engine, h_cyber, h_maint) -> np.ndarray
        Model head returning action scores/probabilities.
    baselines : dict | None
        Optional per-modality baseline latents (default: zeros).
    """

    def __init__(self, predict_fn, baselines: dict | None = None):
        self.predict_fn = predict_fn
        self.baselines = baselines or {}

    def _eval(self, latents: dict, coalition: tuple) -> np.ndarray:
        args = []
        for m in MODALITIES:
            if m in coalition:
                args.append(np.asarray(latents[m], dtype=float))
            else:
                base = self.baselines.get(m)
                args.append(np.zeros_like(np.asarray(latents[m], dtype=float))
                            if base is None else np.asarray(base, dtype=float))
        return np.asarray(self.predict_fn(*args), dtype=float)

    def shap_values(self, latents: dict, action: int | None = None) -> dict:
        """Exact Shapley contribution of each modality.

        If ``action`` is given, contributions are w.r.t. that action's
        score; otherwise w.r.t. the argmax action of the full input.
        """
        full = self._eval(latents, MODALITIES)
        a = int(np.argmax(full)) if action is None else int(action)
        n = len(MODALITIES)
        values = {}
        for m in MODALITIES:
            others = [x for x in MODALITIES if x != m]
            phi = 0.0
            for k in range(n):
                for S in combinations(others, k):
                    wgt = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                    with_m = self._eval(latents, tuple(S) + (m,))[a]
                    without = self._eval(latents, tuple(S))[a]
                    phi += wgt * (with_m - without)
            values[m] = float(phi)
        return values

    def contribution_percentages(self, latents: dict,
                                 action: int | None = None) -> dict:
        """Absolute-share percentages (sum to ~100), panel/manuscript format."""
        phi = self.shap_values(latents, action=action)
        total = sum(abs(v) for v in phi.values())
        if total == 0:
            return {m: 0.0 for m in MODALITIES}
        return {m: round(100.0 * abs(v) / total, 1) for m, v in phi.items()}
