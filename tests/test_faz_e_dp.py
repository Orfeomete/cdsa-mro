"""Faz E / E8 birim testleri — L1 kirpma, duyarlilik 2C/n, Laplace olcegi,
ve Faz A geriye-donuk uyum (regresyon).

Kullanim: python3 test_faz_e_dp.py <repo_kok>
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

KOK = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(KOK))
from src.federated.fedavg import (FedAvgAggregator, clip_l1, tree_l1,
                                  _tree_sub, _tree_add, _tree_scale)
from src.federated.fedprox import FedProxAggregator
from src.rl_agents.ppo_actor_critic import PPOActorCritic

GECTI = []


def onay(ad, kosul, ek=""):
    GECTI.append(bool(kosul))
    print(f"  [{'GECTI' if kosul else 'KALDI'}] {ad} {ek}")


def agac(rng, sekil=((4, 3), (4,), (2, 4))):
    return {"W1": rng.normal(size=sekil[0]), "b1": rng.normal(size=sekil[1]),
            "Wa": rng.normal(size=sekil[2])}


def h(t):
    if isinstance(t, dict):
        return hashlib.sha256("|".join(k + h(v) for k, v in sorted(t.items())).encode()).hexdigest()
    return hashlib.sha256(np.asarray(t, dtype=float).round(12).tobytes()).hexdigest()


print(f"=== {KOK.name} ===")

# --- T1: kirpma normu <= C ------------------------------------------------
rng = np.random.default_rng(1)
tamam = True
for C in (0.05, 0.5, 5.0, 50.0):
    for _ in range(50):
        u = agac(rng)
        k = clip_l1(u, C)
        if tree_l1(k) > C + 1e-9:
            tamam = False
        # yon korunur: norm <= C ise degismez
        if tree_l1(u) <= C and h(k) != h({kk: np.array(v, float) for kk, v in u.items()}):
            tamam = False
onay("T1 kirpma normu <= C (200 rastgele agac, 4 C degeri)", tamam)

# --- T2: deneysel duyarlilik <= 2C/n --------------------------------------
# f(D) = w_g + (1/n) sum clip_L1(w_i - w_g, C); komsuluk: TEK istemci degisir
for n in (3, 5):
    C = 0.7
    enb = 0.0
    rng = np.random.default_rng(2)
    for _ in range(400):
        wg = agac(rng)
        istemci = [_tree_add(wg, _tree_scale(agac(rng), 3.0)) for _ in range(n)]
        j = int(rng.integers(n))
        komsu = list(istemci)
        komsu[j] = _tree_add(wg, _tree_scale(agac(rng), 3.0))
        a1 = FedAvgAggregator(dp_mode="clip_l1", dp_clip_c=C, dp_epsilon=1e12, seed=0)
        a2 = FedAvgAggregator(dp_mode="clip_l1", dp_clip_c=C, dp_epsilon=1e12, seed=0)
        # gurultusuz f: eps devasa -> olcek ~0
        f1 = a1.aggregate_dp_l1(istemci, wg)
        f2 = a2.aggregate_dp_l1(komsu, wg)
        enb = max(enb, tree_l1(_tree_sub(f1, f2)))
    sinir = 2.0 * C / n
    onay(f"T2 deneysel duyarlilik <= 2C/n (n={n})", enb <= sinir + 1e-6,
         f"olculen max={enb:.6f} sinir={sinir:.6f} doluluk={100*enb/sinir:.1f}%")

# --- T2b: 2C/n SIKI sinirdir (zit yonde kirpilmis iki guncelleme) ---------
n, C = 3, 0.7
wg = {"W1": np.zeros((4, 3)), "b1": np.zeros(4), "Wa": np.zeros((2, 4))}
buyuk = {"W1": np.ones((4, 3)) * 10, "b1": np.ones(4) * 10, "Wa": np.ones((2, 4)) * 10}
u_arti = buyuk
u_eksi = _tree_scale(buyuk, -1.0)
D = [u_arti, agac(np.random.default_rng(9)), agac(np.random.default_rng(10))]
Dp = [u_eksi] + D[1:]
f1 = FedAvgAggregator(dp_mode="clip_l1", dp_clip_c=C, dp_epsilon=1e12, seed=0).aggregate_dp_l1(D, wg)
f2 = FedAvgAggregator(dp_mode="clip_l1", dp_clip_c=C, dp_epsilon=1e12, seed=0).aggregate_dp_l1(Dp, wg)
fark = tree_l1(_tree_sub(f1, f2))
onay("T2b 2C/n siniri siki (u=+C, u'=-C karsi ornegi)",
     abs(fark - 2 * C / n) < 1e-6, f"fark={fark:.6f} 2C/n={2*C/n:.6f}")

# --- T3: Laplace olcegi dogru (Delta1/eps_tur) ----------------------------
n, C, eps = 3, 0.4, 0.0625
bek = (2.0 * C / n) / eps
a = FedAvgAggregator(dp_mode="clip_l1", dp_clip_c=C, dp_epsilon=eps,
                     dp_rounds=160, seed=5)
rng = np.random.default_rng(3)
wg = agac(rng)
cl = [_tree_add(wg, _tree_scale(agac(rng), 3.0)) for _ in range(n)]
g2 = a.aggregate_dp_l1(cl, wg)
d = a.privacy_defteri()
onay("T3a defter: Delta1 = 2C/n", abs(d["delta1_2C_over_n"] - 2 * C / n) < 1e-12)
onay("T3b defter: laplace_olcek = Delta1/eps_tur", abs(d["laplace_olcek"] - bek) < 1e-12,
     f"olcek={d['laplace_olcek']:.6f}")
onay("T3c defter: eps_toplam = T*eps_tur", abs(d["eps_toplam"] - 160 * eps) < 1e-12,
     f"eps_toplam={d['eps_toplam']}")
onay("T3d kirpik norm max <= C", d["kirpik_norm_max"] <= C + 1e-9)

# ampirik olcek: cok sayida tur, gurultu ortalama mutlak sapmasi = olcek
ornek = []
for t in range(300):
    aa = FedAvgAggregator(dp_mode="clip_l1", dp_clip_c=C, dp_epsilon=eps, seed=1000 + t)
    gg = aa.aggregate_dp_l1(cl, wg)
    temiz = FedAvgAggregator(dp_mode="clip_l1", dp_clip_c=C, dp_epsilon=1e12,
                             seed=0).aggregate_dp_l1(cl, wg)
    ornek.append(np.abs(np.asarray(gg["W1"]) - np.asarray(temiz["W1"])).ravel())
oms = float(np.mean(np.concatenate(ornek)))     # E|Lap(b)| = b
onay("T3e ampirik E|gurultu| ~ olcek (%10 tolerans)",
     abs(oms - bek) / bek < 0.10, f"ampirik={oms:.5f} beklenen={bek:.5f}")

# --- T4: eksik parametrelerde hata ---------------------------------------
try:
    FedAvgAggregator(dp_mode="clip_l1", dp_clip_c=1.0, dp_epsilon=1.0).aggregate([{"a": np.ones(2)}])
    ok = False
except ValueError:
    ok = True
onay("T4a global_params yoksa ValueError", ok)
try:
    FedAvgAggregator(dp_mode="clip_l1", dp_epsilon=1.0).aggregate_dp_l1([{"a": np.ones(2)}], {"a": np.zeros(2)})
    ok = False
except ValueError:
    ok = True
onay("T4b C yoksa ValueError", ok)

# --- T5: REGRESYON — legacy kip bit-birebir korunuyor ---------------------
ref = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else None
rng = np.random.default_rng(7)
cp = [agac(rng) for _ in range(3)]
cur = {}
cur['fedavg'] = h(FedAvgAggregator(seed=42).aggregate([{k: v.copy() for k, v in p.items()} for p in cp]))
cur['fedavg_dp'] = h(FedAvgAggregator(dp_epsilon=1.0, dp_sensitivity=0.01, seed=42)
                     .aggregate([{k: v.copy() for k, v in p.items()} for p in cp]))
ap = FedProxAggregator(mu=0.01, dp_epsilon=1.0, dp_sensitivity=0.01, seed=42)
cur['fedprox_dp'] = h(ap.aggregate([{k: v.copy() for k, v in p.items()} for p in cp]))
cur['prox_step'] = h(ap.apply_proximal_step(cp[0], cp[1], lr=1.0))
if ref:
    onay("T5 legacy toplama bit-birebir (yama oncesi ozetlerle)", cur == ref,
         "" if cur == ref else json.dumps({k: (ref[k][:8], cur[k][:8]) for k in ref if ref[k] != cur[k]}))
else:
    print("  [ATLANDI] T5 referans ozet verilmedi;", json.dumps(cur, indent=1)[:200])

# --- T6: REGRESYON — PPO update varsayilani bit-birebir -------------------
def egit(prox=None, mu=0.0):
    ag = PPOActorCritic(fused_dim=6, n_actions=3, hidden=8, lr=0.05, seed=11)
    r = np.random.default_rng(4)
    S = r.uniform(0, 1, (32, 6)); A = r.integers(0, 3, 32)
    LP = np.log(np.ones(32) / 3); adv = r.normal(size=32); ret = r.normal(size=32)
    ag.update(S, A, LP, adv, ret, epochs=2, prox_ref=prox, prox_mu=mu)
    return ag.params()
p0 = egit()
p_none = egit(prox=None, mu=0.5)
onay("T6a prox_ref=None -> Faz A davranisi bit-birebir", h(p0) == h(p_none))
ref_w = PPOActorCritic(fused_dim=6, n_actions=3, hidden=8, lr=0.05, seed=11).params()
p_prox = egit(prox=ref_w, mu=0.5)
onay("T6b prox_ref verilince cikti DEGISIR (proksimal terim etkili)", h(p0) != h(p_prox))
# prox terimi w'yi referansa yaklastirir mi (mu buyukken)
uzak = {k: v + 5.0 for k, v in ref_w.items()}
ag = PPOActorCritic(fused_dim=6, n_actions=3, hidden=8, lr=0.05, seed=11)
ag.set_params(uzak)
r = np.random.default_rng(4)
S = r.uniform(0, 1, (32, 6)); A = r.integers(0, 3, 32)
LP = np.log(np.ones(32) / 3); adv = r.normal(size=32); ret = r.normal(size=32)
d0 = tree_l1(_tree_sub(ag.params(), ref_w))
ag.update(S, A, LP, adv, ret, epochs=1, prox_ref=ref_w, prox_mu=1.0)
d1 = tree_l1(_tree_sub(ag.params(), ref_w))
onay("T6c proksimal terim yerel agirligi w_g'ye yaklastirir", d1 < d0,
     f"||w-w_g||_1: {d0:.3f} -> {d1:.3f}")

print(f"--- {sum(GECTI)}/{len(GECTI)} test gecti ---")
sys.exit(0 if all(GECTI) else 1)
