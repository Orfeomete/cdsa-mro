"""
Cross-modal attention + gating fusion for CDSA-MRO — NumPy reference
implementation (v2).

Reference: Vaswani et al. (2017), Attention Is All You Need, NeurIPS.

For each modality m with latent h_m:
  g_m       = sigmoid(w_g[m] . h_m + b_g[m])          # gating score
  h_m^attn  = scaled dot-product attention over the
              {h_engine, h_cyber, h_maint} token set
  h_fusion  = sum_m (g_m * h_m^attn)  ->  linear head -> fusion_dim

Output: ``fusion_dim`` (default 64) vector for the PPO Actor-Critic head,
plus the gating scores (used by the XAI layer and the platform panel).

Scope note (Faz A): compact CPU-scale forward implementation with seeded
weights; framework-scale training under TUBITAK 1001 ARDEB Project 3.
"""

from __future__ import annotations

import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))


class CrossModalAttentionFusion:
    """Gated cross-modal attention over a fixed set of modality latents."""

    MODALITIES = ("engine", "cyber", "maint")

    def __init__(self, latent_dim: int = 64, fusion_dim: int = 64,
                 seed: int = 42):
        self.latent_dim = latent_dim
        self.fusion_dim = fusion_dim
        rng = np.random.default_rng(seed)
        s = 1.0 / np.sqrt(latent_dim)
        self.Wq = rng.normal(0, s, (latent_dim, latent_dim))
        self.Wk = rng.normal(0, s, (latent_dim, latent_dim))
        self.Wv = rng.normal(0, s, (latent_dim, latent_dim))
        self.Wg = rng.normal(0, s, (len(self.MODALITIES), latent_dim))
        self.bg = np.zeros(len(self.MODALITIES))
        self.Wo = rng.normal(0, s, (fusion_dim, latent_dim))
        self.bo = np.zeros(fusion_dim)

    def forward(self, h_engine: np.ndarray, h_cyber: np.ndarray,
                h_maint: np.ndarray, return_gates: bool = False):
        H = np.stack([np.asarray(h, dtype=float)
                      for h in (h_engine, h_cyber, h_maint)])     # (3, L)
        if H.shape[1] != self.latent_dim:
            raise ValueError(f"expected latent_dim={self.latent_dim}")
        gates = _sigmoid(np.einsum("ml,ml->m", self.Wg, H) + self.bg)
        Q, K, V = H @ self.Wq.T, H @ self.Wk.T, H @ self.Wv.T
        A = Q @ K.T / np.sqrt(self.latent_dim)                    # (3, 3)
        A = np.exp(A - A.max(axis=1, keepdims=True))
        A = A / A.sum(axis=1, keepdims=True)
        H_attn = A @ V                                            # (3, L)
        h_fusion = self.Wo @ (gates[:, None] * H_attn).sum(axis=0) + self.bo
        if return_gates:
            return h_fusion, dict(zip(self.MODALITIES, gates.tolist()))
        return h_fusion

    def params(self) -> dict:
        return {"Wq": self.Wq, "Wk": self.Wk, "Wv": self.Wv,
                "Wg": self.Wg, "bg": self.bg, "Wo": self.Wo, "bo": self.bo}

    def set_params(self, p: dict) -> None:
        for n in ("Wq", "Wk", "Wv", "Wg", "bg", "Wo", "bo"):
            setattr(self, n, np.asarray(p[n], dtype=float))
