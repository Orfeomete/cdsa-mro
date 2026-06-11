"""
CDSA-MRO src.xai — Explainable AI Layer Scaffold
=======================================================

Three explainability techniques aligned with the EASA AI Roadmap
Level 2 AI/ML "Concepts of Design" explainability requirement:

  shap_explainer.py     — SHAP modality contribution analysis
  counterfactual.py     — Counterfactual reasoning
  lime_explainer.py     — LIME local interpretability

Outputs are JSON-serialised and dispatched to three stakeholder
interfaces (maintenance personnel, EASA Part-IS auditors, SHGM SHT-SIBER inspectors).

Status: scaffolded (v2). Full implementation is planned under
TÜBİTAK 1001 ARDEB Project 3.
"""

from .shap_explainer import SHAPModalityExplainer  # noqa: F401
from .counterfactual import CounterfactualExplainer  # noqa: F401
from .lime_explainer import LIMEExplainer  # noqa: F401

__all__ = ["SHAPModalityExplainer", "CounterfactualExplainer", "LIMEExplainer"]
