"""
Unit tests for the CDSA-MRO v2 modules (Faz A implementation):
federated (FedAvg/FedProx), multimodal (encoders + fusion), xai
(SHAP modality / counterfactual / LIME).
"""

import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.federated.fedavg import FedAvgAggregator
from src.federated.fedprox import FedProxAggregator
from src.multimodal.encoders import EngineEncoder, CyberEncoder, MaintEncoder
from src.multimodal.fusion import CrossModalAttentionFusion
from src.xai.shap_explainer import SHAPModalityExplainer
from src.xai.counterfactual import CounterfactualExplainer
from src.xai.lime_explainer import LIMEExplainer

RNG = np.random.default_rng(42)
L = 64  # latent dim


def _toy_params(scale):
    return {"layer": {"W": np.full((2, 2), scale), "b": np.full(2, scale)}}


# ---------------- federated ----------------

def test_fedavg_weighted_average():
    agg = FedAvgAggregator()
    out = agg.aggregate([_toy_params(0.0), _toy_params(1.0)], [1, 3])
    assert np.allclose(out["layer"]["W"], 0.75)
    assert np.allclose(out["layer"]["b"], 0.75)
    assert agg.round == 1


def test_fedavg_dp_noise_changes_params_but_preserves_mean():
    agg = FedAvgAggregator(dp_epsilon=1.0, seed=0)
    clean = _toy_params(1.0)
    noisy = agg.privatize(clean)
    assert not np.allclose(noisy["layer"]["W"], clean["layer"]["W"])
    # many-sample mean approaches the clean value (Laplace is zero-mean)
    samples = [agg.privatize(clean)["layer"]["W"] for _ in range(3000)]
    assert abs(np.mean(samples) - 1.0) < 0.1


def test_fedprox_penalty_and_grad():
    agg = FedProxAggregator(mu=0.5)
    local, glob = _toy_params(2.0), _toy_params(0.0)
    # ||diff||^2 = 6 entries * 4 = 24 -> penalty = 0.5*0.5*24 = 6
    assert np.isclose(agg.proximal_penalty(local, glob), 6.0)
    g = agg.proximal_grad(local, glob)
    assert np.allclose(g["layer"]["W"], 1.0)
    stepped = agg.apply_proximal_step(local, glob, lr=1.0)
    assert np.allclose(stepped["layer"]["W"], 1.0)


# ---------------- multimodal ----------------

def test_encoders_output_latent_dim_and_determinism():
    eng = EngineEncoder(seed=7)
    cyb = CyberEncoder(seed=7)
    mnt = MaintEncoder(seed=7)
    x_e = RNG.normal(size=(30, 21))
    x_c = RNG.normal(size=(12, 18))
    x_b = RNG.normal(size=(10, 8))
    h_e, h_c, h_b = eng.forward(x_e), cyb.forward(x_c), mnt.forward(x_b)
    for h in (h_e, h_c, h_b):
        assert h.shape == (L,)
        assert np.all(np.isfinite(h))
    assert np.allclose(h_e, EngineEncoder(seed=7).forward(x_e))  # seeded determinism


def test_encoder_param_roundtrip():
    enc = EngineEncoder(seed=1)
    x = RNG.normal(size=(20, 21))
    h1 = enc.forward(x)
    p = enc.params()
    enc2 = EngineEncoder(seed=99)
    enc2.set_params(p)
    assert np.allclose(h1, enc2.forward(x))


def test_fusion_shapes_and_gates():
    fus = CrossModalAttentionFusion(latent_dim=L, fusion_dim=L, seed=3)
    h = [RNG.normal(size=L) for _ in range(3)]
    out, gates = fus.forward(*h, return_gates=True)
    assert out.shape == (L,)
    assert set(gates) == {"engine", "cyber", "maint"}
    assert all(0.0 <= g <= 1.0 for g in gates.values())


# ---------------- xai ----------------

def _linear_head():
    """Toy 4-action head: action k score depends on distinct modalities."""
    W = np.zeros((4, 3))
    W[0] = [0.1, 0.1, 1.0]   # action0: maint-driven
    W[1] = [1.0, 0.1, 0.4]   # action1: engine-driven
    W[2] = [1.2, 0.6, 0.1]   # action2: engine+cyber
    W[3] = [0.2, 1.5, 0.1]   # action3: cyber-driven

    def f(h_e, h_c, h_b):
        feats = np.array([h_e.mean(), h_c.mean(), h_b.mean()])
        return W @ feats
    return f


def test_shap_exact_and_percentages():
    f = _linear_head()
    lat = {"engine": np.full(L, 2.0), "cyber": np.full(L, 1.0),
           "maint": np.full(L, 0.5)}
    ex = SHAPModalityExplainer(f)
    phi = ex.shap_values(lat, action=3)         # cyber-driven action
    assert max(phi, key=lambda m: abs(phi[m])) == "cyber"
    # linearity -> Shapley sums to f(full) - f(empty)
    full = f(lat["engine"], lat["cyber"], lat["maint"])[3]
    empty = f(np.zeros(L), np.zeros(L), np.zeros(L))[3]
    assert np.isclose(sum(phi.values()), full - empty)
    pct = ex.contribution_percentages(lat, action=3)
    assert np.isclose(sum(pct.values()), 100.0, atol=0.5)


def test_counterfactual_flip():
    f = _linear_head()
    lat = {"engine": np.full(L, 0.4), "cyber": np.full(L, 2.0),
           "maint": np.full(L, 0.3)}
    cf = CounterfactualExplainer(
        f, action_labels=["no_maint", "scheduled", "urgent", "fleet_alert"])
    res = cf.counterfactual(lat, "cyber")
    assert res["original_action"] == "fleet_alert"
    assert res["decision_changed"] is True
    report = cf.report(lat)
    assert len(report) == 3


def test_lime_recovers_dominant_feature():
    def f(x):
        return np.array([3.0 * x[0] + 0.1 * x[1], 0.0])
    lime = LIMEExplainer(f, n_samples=400, seed=5)
    res = lime.explain(np.array([1.0, 1.0, 1.0]), action=0)
    assert res["top_features"][0]["index"] == 0
    assert res["top_features"][0]["weight"] > 1.0
