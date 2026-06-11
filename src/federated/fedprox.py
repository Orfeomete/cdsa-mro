"""
FedProx aggregator for CDSA-MRO — NumPy reference implementation (v2).

Reference: Li, T. et al. (2020). Federated Optimization in Heterogeneous
Networks. MLSys.

FedProx adds a proximal term mu/2 * ||w_local - w_global||^2 to the local
objective, stabilising client updates under statistically heterogeneous
(Non-IID) data distributions. Aggregation itself follows FedAvg.

Scope note (Faz A): compact CPU-scale reference implementation.
Framework-scale training is planned under TUBITAK 1001 ARDEB Project 3.
"""

from __future__ import annotations

from .fedavg import (FedAvgAggregator, _tree_add, _tree_map, _tree_scale,
                     _tree_sqnorm, _tree_sub)


class FedProxAggregator(FedAvgAggregator):
    """FedAvg with proximal regularisation utilities (mu >= 0)."""

    def __init__(self, mu: float = 0.01, dp_epsilon: float | None = None,
                 dp_sensitivity: float = 1.0, seed: int | None = None):
        super().__init__(dp_epsilon=dp_epsilon, dp_sensitivity=dp_sensitivity, seed=seed)
        if mu < 0:
            raise ValueError("mu must be >= 0")
        self.mu = float(mu)

    # -- proximal utilities used by client-side local training ----------
    def proximal_penalty(self, local_params: dict, global_params: dict) -> float:
        """mu/2 * ||w_local - w_global||^2 (added to the local loss)."""
        return 0.5 * self.mu * _tree_sqnorm(_tree_sub(local_params, global_params))

    def proximal_grad(self, local_params: dict, global_params: dict) -> dict:
        """Gradient of the proximal penalty: mu * (w_local - w_global)."""
        diff = _tree_sub(local_params, global_params)
        return _tree_map(lambda a: self.mu * a, diff)

    def apply_proximal_step(self, local_params: dict, global_params: dict,
                            lr: float = 1.0) -> dict:
        """One explicit proximal correction step on local parameters."""
        g = self.proximal_grad(local_params, global_params)
        return _tree_add(local_params, _tree_scale(g, -lr))
