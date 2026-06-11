"""
Modality-specific encoders for CDSA-MRO — NumPy reference implementation (v2).

  EngineEncoder: 1D-CNN + LSTM over NASA C-MAPSS turbofan sensors
                 (21 sensor channels, FD001-FD004 sub-sets)
  CyberEncoder:  scaled dot-product self-attention over the SHT-SIBER
                 Annex 13 15-class incident typology sequence
  MaintEncoder:  LSTM over SHY-145 maintenance record sequences

Each encoder projects its hidden state to a ``latent_dim`` (default 64)
representation: h_m for the engine, h_c for cyber, h_b for maintenance.

Scope note (Faz A): compact CPU-scale NumPy forward implementations with
seeded weights and get/set parameter trees for federated exchange.
Gradient-based end-to-end encoder training at framework scale is planned
under TUBITAK 1001 ARDEB Project 3 (Faz B).
"""

from __future__ import annotations

import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60, 60)))


class _LSTMCore:
    """Minimal NumPy LSTM (single layer) returning the last hidden state."""

    def __init__(self, input_dim: int, hidden_dim: int, rng: np.random.Generator):
        s = 1.0 / np.sqrt(max(input_dim + hidden_dim, 1))
        self.W = rng.normal(0, s, (4 * hidden_dim, input_dim + hidden_dim))
        self.b = np.zeros(4 * hidden_dim)
        self.hidden_dim = hidden_dim

    def forward(self, x: np.ndarray) -> np.ndarray:
        """x: (T, input_dim) -> h_T: (hidden_dim,)"""
        H = self.hidden_dim
        h = np.zeros(H)
        c = np.zeros(H)
        for t in range(x.shape[0]):
            z = self.W @ np.concatenate([x[t], h]) + self.b
            i, f, g, o = z[:H], z[H:2 * H], z[2 * H:3 * H], z[3 * H:]
            c = _sigmoid(f) * c + _sigmoid(i) * np.tanh(g)
            h = _sigmoid(o) * np.tanh(c)
        return h

    def params(self) -> dict:
        return {"W": self.W, "b": self.b}

    def set_params(self, p: dict) -> None:
        self.W = np.asarray(p["W"], dtype=float)
        self.b = np.asarray(p["b"], dtype=float)


class _ModalityEncoder:
    """Base encoder: domain core -> linear projection to latent_dim."""

    def __init__(self, latent_dim: int = 64, seed: int = 42):
        self.latent_dim = latent_dim
        self.rng = np.random.default_rng(seed)

    def _init_projection(self, core_dim: int) -> None:
        s = 1.0 / np.sqrt(core_dim)
        self.P = self.rng.normal(0, s, (self.latent_dim, core_dim))
        self.pb = np.zeros(self.latent_dim)

    def _project(self, h: np.ndarray) -> np.ndarray:
        return self.P @ h + self.pb

    def params(self) -> dict:
        return {"P": self.P, "pb": self.pb}

    def set_params(self, p: dict) -> None:
        self.P = np.asarray(p["P"], dtype=float)
        self.pb = np.asarray(p["pb"], dtype=float)


class EngineEncoder(_ModalityEncoder):
    """1D-CNN (kernel=3, ReLU) + LSTM over multivariate engine series.

    Input  x: (T, n_sensors)  — e.g. C-MAPSS windows, n_sensors=21
    Output h_m: (latent_dim,)
    """

    def __init__(self, n_sensors: int = 21, n_filters: int = 16,
                 lstm_hidden: int = 32, latent_dim: int = 64, seed: int = 42):
        super().__init__(latent_dim=latent_dim, seed=seed)
        s = 1.0 / np.sqrt(3 * n_sensors)
        self.K = self.rng.normal(0, s, (n_filters, 3, n_sensors))  # (F, k, C)
        self.kb = np.zeros(n_filters)
        self.lstm = _LSTMCore(n_filters, lstm_hidden, self.rng)
        self._init_projection(lstm_hidden)
        self.n_sensors = n_sensors

    def forward(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        if x.ndim != 2 or x.shape[0] < 3:
            raise ValueError("EngineEncoder expects (T>=3, n_sensors)")
        T = x.shape[0]
        feat = np.empty((T - 2, self.K.shape[0]))
        for t in range(T - 2):
            win = x[t:t + 3]                                      # (3, C)
            feat[t] = np.maximum(
                np.einsum("fkc,kc->f", self.K, win) + self.kb, 0.0)
        return self._project(self.lstm.forward(feat))

    def params(self) -> dict:
        return {"K": self.K, "kb": self.kb, "lstm": self.lstm.params(),
                **super().params()}

    def set_params(self, p: dict) -> None:
        self.K = np.asarray(p["K"], dtype=float)
        self.kb = np.asarray(p["kb"], dtype=float)
        self.lstm.set_params(p["lstm"])
        super().set_params(p)


class CyberEncoder(_ModalityEncoder):
    """Self-attention over an incident-event sequence, mean-pooled.

    Input  x: (T, event_dim)  — e.g. one-hot(15) + severity/meta features
    Output h_c: (latent_dim,)
    """

    def __init__(self, event_dim: int = 18, d_model: int = 32,
                 latent_dim: int = 64, seed: int = 42):
        super().__init__(latent_dim=latent_dim, seed=seed)
        s = 1.0 / np.sqrt(event_dim)
        self.We = self.rng.normal(0, s, (d_model, event_dim))
        sq = 1.0 / np.sqrt(d_model)
        self.Wq = self.rng.normal(0, sq, (d_model, d_model))
        self.Wk = self.rng.normal(0, sq, (d_model, d_model))
        self.Wv = self.rng.normal(0, sq, (d_model, d_model))
        self._init_projection(d_model)
        self.d_model = d_model

    def forward(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        if x.ndim != 2:
            raise ValueError("CyberEncoder expects (T, event_dim)")
        E = x @ self.We.T                                         # (T, d)
        Q, K, V = E @ self.Wq.T, E @ self.Wk.T, E @ self.Wv.T
        A = Q @ K.T / np.sqrt(self.d_model)
        A = np.exp(A - A.max(axis=1, keepdims=True))
        A = A / A.sum(axis=1, keepdims=True)
        return self._project((A @ V).mean(axis=0))

    def params(self) -> dict:
        return {"We": self.We, "Wq": self.Wq, "Wk": self.Wk, "Wv": self.Wv,
                **super().params()}

    def set_params(self, p: dict) -> None:
        for n in ("We", "Wq", "Wk", "Wv"):
            setattr(self, n, np.asarray(p[n], dtype=float))
        super().set_params(p)


class MaintEncoder(_ModalityEncoder):
    """LSTM over maintenance-record sequences (action one-hot + outcome).

    Input  x: (T, record_dim)
    Output h_b: (latent_dim,)
    """

    def __init__(self, record_dim: int = 8, lstm_hidden: int = 24,
                 latent_dim: int = 64, seed: int = 42):
        super().__init__(latent_dim=latent_dim, seed=seed)
        self.lstm = _LSTMCore(record_dim, lstm_hidden, self.rng)
        self._init_projection(lstm_hidden)

    def forward(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        if x.ndim != 2:
            raise ValueError("MaintEncoder expects (T, record_dim)")
        return self._project(self.lstm.forward(x))

    def params(self) -> dict:
        return {"lstm": self.lstm.params(), **super().params()}

    def set_params(self, p: dict) -> None:
        self.lstm.set_params(p["lstm"])
        super().set_params(p)
