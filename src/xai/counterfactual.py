"""
Counterfactual reasoning explainer — NumPy reference implementation (v2).

Reference: Wachter, Mittelstadt & Russell (2017), Counterfactual
Explanations Without Opening the Black Box, Harvard JLT.

Modality-level counterfactuals answer the auditor question used across
the CDSA framework: "What would the agent have decided if this modality
signal had not been present?" — e.g. removing an active USB-malware
cyber event and observing the decision revert from Urgent to Scheduled
maintenance.
"""

from __future__ import annotations

import numpy as np

MODALITIES = ("engine", "cyber", "maint")


class CounterfactualExplainer:
    """Ablation-style modality counterfactuals over a prediction head."""

    def __init__(self, predict_fn, baselines: dict | None = None,
                 action_labels: list[str] | None = None):
        self.predict_fn = predict_fn
        self.baselines = baselines or {}
        self.action_labels = action_labels

    def _label(self, a: int) -> str:
        if self.action_labels and 0 <= a < len(self.action_labels):
            return self.action_labels[a]
        return f"action_{a}"

    def _predict(self, latents: dict):
        scores = np.asarray(
            self.predict_fn(*[np.asarray(latents[m], dtype=float)
                              for m in MODALITIES]), dtype=float)
        return int(np.argmax(scores)), scores

    def counterfactual(self, latents: dict, modality: str) -> dict:
        """Replace one modality by its baseline and report the decision flip."""
        if modality not in MODALITIES:
            raise ValueError(f"modality must be one of {MODALITIES}")
        a0, s0 = self._predict(latents)
        cf = dict(latents)
        base = self.baselines.get(modality)
        cf[modality] = (np.zeros_like(np.asarray(latents[modality], dtype=float))
                        if base is None else np.asarray(base, dtype=float))
        a1, s1 = self._predict(cf)
        return {
            "modality_removed": modality,
            "original_action": self._label(a0),
            "counterfactual_action": self._label(a1),
            "decision_changed": bool(a0 != a1),
            "original_scores": s0.tolist(),
            "counterfactual_scores": s1.tolist(),
            "statement": (
                f"Without the '{modality}' signal the agent decides "
                f"'{self._label(a1)}' instead of '{self._label(a0)}'."
                if a0 != a1 else
                f"The decision '{self._label(a0)}' is robust to removing "
                f"the '{modality}' signal."),
        }

    def report(self, latents: dict) -> list:
        """Counterfactual sweep over all modalities (auditor JSON format)."""
        return [self.counterfactual(latents, m) for m in MODALITIES]
