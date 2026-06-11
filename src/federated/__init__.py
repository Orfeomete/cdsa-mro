"""
CDSA-MRO src.federated — FedAvg + FedProx Federated Aggregation Scaffold
================================================================================

Scaffold for Federated Averaging (FedAvg, McMahan et al. 2017) and
FedProx (Li et al. 2020, μ=0.01) aggregation for the
MRO consortium (MRO-A, MRO-B, MRO-C (simulated three-MRO consortium)).

Status: scaffolded (v2). Full implementation is planned under
TÜBİTAK 1001 ARDEB Project 3.
"""

from .fedavg import FedAvgAggregator  # noqa: F401
from .fedprox import FedProxAggregator  # noqa: F401

__all__ = ["FedAvgAggregator", "FedProxAggregator"]
