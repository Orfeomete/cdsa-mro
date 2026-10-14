"""
FedAvg aggregator for CDSA-MRO — NumPy reference implementation (v2).

Reference: McMahan, B. et al. (2017). Communication-Efficient Learning
of Deep Networks from Decentralized Data. AISTATS.

Implements data-weighted Federated Averaging over parameter dictionaries,
with an optional Laplace differential-privacy hook applied to client
updates before aggregation.

Scope note (Faz A): compact CPU-scale reference implementation used by the
three-client consortium simulation. Framework-scale training is planned
under TUBITAK 1001 ARDEB Project 3 (Faz B).
"""

from __future__ import annotations

import numpy as np


class FedAvgAggregator:
    """Data-weighted Federated Averaging over nested parameter dicts.

    Parameters are dictionaries mapping names to ``np.ndarray`` (or nested
    dicts thereof). All clients must share an identical structure.
    """

    def __init__(self, dp_epsilon: float | None = None, dp_sensitivity: float = 1.0,
                 seed: int | None = None, dp_mode: str = "legacy",
                 dp_clip_c: float | None = None, dp_rounds: int | None = None):
        """dp_mode:
          "legacy"  — Faz A/C davranisi (VARSAYILAN, degismedi): kirpma yok,
                      gurultu dogrudan parametrelere, olcek = dp_sensitivity/eps.
                      Bu kip icin mahremiyet iddiasi YOKTUR.
          "clip_l1" — Faz E / E8 (a): istemci GUNCELLEMESI u_i = w_i - w_g
                      L1 normunda C'ye kirpilir, ortalama alinir, uzerine
                      Lap(Delta1/eps_tur) eklenir; Delta1 = 2C/n (on kayit Ek 2),
                      degistirme komsulugu, sabit n. eps_toplam = T*eps_tur
                      (temel bilesim, saf eps-DP; on kayit Ek 3).
        """
        self.dp_epsilon = dp_epsilon
        self.dp_sensitivity = dp_sensitivity
        self.rng = np.random.default_rng(seed)
        self.round = 0
        if dp_mode not in ("legacy", "clip_l1"):
            raise ValueError("dp_mode 'legacy' ya da 'clip_l1' olmali")
        self.dp_mode = dp_mode
        self.dp_clip_c = None if dp_clip_c is None else float(dp_clip_c)
        self.dp_rounds = None if dp_rounds is None else int(dp_rounds)
        self._defter = None

    # -- differential privacy hook -------------------------------------
    def _laplace(self, arr: np.ndarray) -> np.ndarray:
        scale = self.dp_sensitivity / float(self.dp_epsilon)
        return arr + self.rng.laplace(0.0, scale, size=arr.shape)

    def privatize(self, params: dict) -> dict:
        """Apply Laplace noise (if dp_epsilon is set) to a client update."""
        if self.dp_epsilon is None:
            return params
        return _tree_map(self._laplace, params)

    # -- aggregation ----------------------------------------------------
    def aggregate(self, client_params: list[dict],
                  client_weights: list[float] | None = None,
                  global_params: dict | None = None) -> dict:
        """Weighted average of client parameter trees (weights proportional to data size).

        dp_mode="clip_l1" ise cagri aggregate_dp_l1'e yonlendirilir (global_params
        zorunlu). Varsayilan "legacy" kipinde davranis Faz A ile birebir aynidir.
        """
        if not client_params:
            raise ValueError("client_params must be non-empty")
        if self.dp_mode == "clip_l1":
            return self.aggregate_dp_l1(client_params, global_params)
        n = len(client_params)
        if client_weights is None:
            client_weights = [1.0] * n
        w = np.asarray(client_weights, dtype=float)
        if w.sum() <= 0:
            raise ValueError("client_weights must sum to a positive value")
        w = w / w.sum()

        noisy = [self.privatize(p) for p in client_params]
        out = _tree_zeros_like(noisy[0])
        for wi, pi in zip(w, noisy):
            out = _tree_add(out, _tree_scale(pi, float(wi)))
        self.round += 1
        return out

    # -- Faz E / E8 (a): L1 kirpma + Laplace, Delta1 = 2C/n -----------------
    def aggregate_dp_l1(self, client_params: list[dict],
                        global_params: dict | None) -> dict:
        """Saf eps-DP toplama (on kayit E8 (a), Ek 2, Ek 3, Ek 4).

        f(D) = w_g + (1/n) * sum_i clip_L1(w_i - w_g, C)
        Degistirme komsulugu (n sabit): Delta1 = max ||f(D)-f(D')||_1 <= 2C/n.
        Her koordinata bagimsiz Lap(Delta1/eps_tur) -> tur basina eps_tur-DP.
        T tur icin temel bilesim: eps_toplam = T*eps_tur.
        """
        if global_params is None:
            raise ValueError("dp_mode='clip_l1' icin global_params zorunludur "
                             "(guncelleme u_i = w_i - w_g uzerinden tanimlidir)")
        if self.dp_clip_c is None or self.dp_clip_c <= 0:
            raise ValueError("dp_clip_c > 0 olmali (kalibrasyonla dondurulmus C)")
        if not self.dp_epsilon or self.dp_epsilon <= 0:
            raise ValueError("dp_epsilon (eps_tur) > 0 olmali")
        n = len(client_params)
        C = float(self.dp_clip_c)
        kirpik = [clip_l1(_tree_sub(p, global_params), C) for p in client_params]
        ort = _tree_zeros_like(kirpik[0])
        for u in kirpik:
            ort = _tree_add(ort, _tree_scale(u, 1.0 / n))
        delta1 = 2.0 * C / n
        olcek = delta1 / float(self.dp_epsilon)
        gurultulu = _tree_map(
            lambda a: a + self.rng.laplace(0.0, olcek, size=np.shape(a)), ort)
        self.round += 1
        T = self.dp_rounds if self.dp_rounds is not None else self.round
        self._defter = {
            "mekanizma": "Laplace, saf eps-DP",
            "korunacak_birim": "istemci guncellemesi",
            "komsuluk": "degistirme (n sabit)",
            "n": n, "C": C, "delta1_2C_over_n": delta1,
            "eps_tur": float(self.dp_epsilon),
            "T_tur": int(T),
            "eps_toplam": float(self.dp_epsilon) * int(T),
            "laplace_olcek": olcek,
            "bilesim": "temel ardisik (saf DP; on kayit Ek 3 madde 3)",
            "kirpik_norm_max": max(tree_l1(u) for u in kirpik),
            "kirpilmamis_norm": [tree_l1(_tree_sub(p, global_params))
                                 for p in client_params],
        }
        return _tree_add(global_params, gurultulu)

    def privacy_defteri(self) -> dict | None:
        """Son aggregate_dp_l1 cagrisinin mahremiyet defteri (E0 kaydina girer).

        Uyari: gurultu eklenmis olmasi tek basina DP kanmiti degildir; kanit =
        kirpma + turetilmis duyarlilik (2C/n) + kayitli eps_toplam (Ek 4 md 5).
        """
        return self._defter


# -- small parameter-tree helpers (shared with FedProx) -----------------

def _tree_map(fn, tree):
    if isinstance(tree, dict):
        return {k: _tree_map(fn, v) for k, v in tree.items()}
    return fn(np.asarray(tree, dtype=float))


def _tree_zeros_like(tree):
    return _tree_map(np.zeros_like, tree)


def _tree_scale(tree, s: float):
    return _tree_map(lambda a: a * s, tree)


def _tree_add(t1, t2):
    if isinstance(t1, dict):
        return {k: _tree_add(t1[k], t2[k]) for k in t1}
    return np.asarray(t1) + np.asarray(t2)


def _tree_sub(t1, t2):
    if isinstance(t1, dict):
        return {k: _tree_sub(t1[k], t2[k]) for k in t1}
    return np.asarray(t1) - np.asarray(t2)


def _tree_sqnorm(tree) -> float:
    if isinstance(tree, dict):
        return float(sum(_tree_sqnorm(v) for v in tree.values()))
    a = np.asarray(tree, dtype=float)
    return float((a * a).sum())


def tree_l1(tree) -> float:
    """Parametre agacinin TAMAMI icin L1 norm (koordinat basina degil)."""
    if isinstance(tree, dict):
        return float(sum(tree_l1(v) for v in tree.values()))
    return float(np.abs(np.asarray(tree, dtype=float)).sum())


def clip_l1(tree, C: float):
    """L1 kirpma: ||clip_L1(u,C)||_1 <= C, yon korunur (on kayit E8 (a))."""
    C = float(C)
    nrm = tree_l1(tree)
    if nrm <= C or nrm == 0.0:
        return _tree_map(lambda a: np.array(a, dtype=float), tree)
    return _tree_scale(tree, C / nrm)
