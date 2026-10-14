"""Faz E kampanya kosucusu — tek is calistirir, E0 kaydi yazar.

Kollar (on kayittan; kosudan once sabitlenmis):
  merkezi            E6/E7  merkezi PPO
  fedavg             E6/E7  FedAvg
  fedprox_yakinlik   E5     mevcut tek adimli yakinlik duzeltmesi (Faz A kolu)
  fedprox_gercek     E5     OZGUN FedProx: yerel kayba mu/2||w-w_g||^2 (Alg. 2)
  dp_eps10 / dp_eps1 E8     FedAvg + L1 kirpma (dondurulmus C) + Laplace
  e4_ayrik_fedavg    E4     istemci basina AYRIK kayit
  e4_heteroj_fedavg  E4     ayrik kayit + bir istemcide kritik pay 2x
  e1_cokmodlu        E1     tam gozlem
  e1_tekmodlu        E1     yalniz BIRINCIL modalite (kod sirasinda ILK
                            MODALITY_GROUPS grubu; MRO'da grup yok -> kosulamaz)

Butun kollar AYNI bütçe ile kosar (varsayilan 100 tur), E8 haric: E8 on kayit
Ek 2 madde 3 geregi T = 160 turdur (eps_toplam = T*eps_tur).

Degerlendirme: faz_e0 esdeger 1.800 karar protokolu (faz_e2 ile ayni kume).

Kullanim: python3 faz_e_kampanya.py <kol> <tohum> [tur]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from faz_a_config import (PILLAR, make_env, make_client_envs, N_ACTIONS, STATE_DIM,
                          MODALITY_GROUPS, ACTION_LABELS, NEW_STEP_API,
                          INFO_TRUE_KEY, CRITICAL_ACTIONS)
from faz_a_staged import (new_agent, train_local, env_reset, env_step, OUT,
                          _p2j, LOCAL_ROLLOUTS, ROLLOUT_LEN)
from src.federated.fedavg import FedAvgAggregator
from src.federated.fedprox import FedProxAggregator
from src.rl_agents.ppo_actor_critic import PPOActorCritic
from faz_e_kayit import KosuKaydi, makro_f1
import faz_e2_karsilastiricilar as e2
import faz_e_veri as ev

TUR_VARSAYILAN = 100
E8_TUR = 160                      # on kayit Ek 2 md 3
E8_EPS = {"dp_eps10": 10.0 / 160, "dp_eps1": 1.0 / 160}
E1_BIRINCIL = (list(MODALITY_GROUPS)[0] if MODALITY_GROUPS else None)


def _maske(kol):
    """E1 tek-modlu kol icin gozlem maskesi (birincil modalite disi sifirlanir)."""
    if kol != "e1_tekmodlu" or not MODALITY_GROUPS:
        return None
    m = np.zeros(STATE_DIM)
    m[np.asarray(MODALITY_GROUPS[E1_BIRINCIL])] = 1.0
    return m


def _degerlendir(ajan, maske=None):
    """1.800 karar; (y_true, y_pred) dondurur."""
    Xte, yte = e2.degerlendirme_kumesi()
    if maske is not None:
        Xte = Xte * maske
    yp = np.array([ajan.act(x, deterministic=True)[0] for x in Xte], dtype=int)
    return yte, yp


class _MaskeliOrtam:
    """Gozlemi maskeleyen ince sarmalayici (E1 tek-modlu kol)."""

    def __init__(self, env, maske):
        self.env, self.m = env, maske

    def reset(self, seed=None):
        out = self.env.reset(seed=seed) if NEW_STEP_API else self.env.reset()
        if isinstance(out, tuple):
            return (np.asarray(out[0]) * self.m,) + out[1:]
        return np.asarray(out) * self.m

    def step(self, a):
        out = self.env.step(a)
        return (np.asarray(out[0]) * self.m,) + tuple(out[1:])


def _istemci_ortamlari(kol, tohum):
    if kol == "e4_ayrik_fedavg":
        envs, meta = ev.e4_istemci_ortamlari(seed=tohum, heterojen=False)
        return envs, meta
    if kol == "e4_heteroj_fedavg":
        envs, meta = ev.e4_istemci_ortamlari(seed=tohum, heterojen=True)
        return envs, meta
    return make_client_envs(tohum), {"kaynak": "faz_a_config.make_client_envs (Faz A kurulumu)"}


def _param_bayt(p) -> int:
    return int(sum(np.asarray(v, dtype=float).nbytes for v in p.values()))


def kos(kol: str, tohum: int, tur: int):
    t0 = time.time()
    if kol == "e1_tekmodlu" and not MODALITY_GROUPS:
        return {"durum": "kosulamadi",
                "gerekce": (f"{PILLAR} tek-modlu bir gorevdir; faz_a_config.MODALITY_GROUPS "
                            "bostur. E1 cok-modlu/tek-modlu basligi bu damarda "
                            "UYGULANMAMISTIR.")}
    if kol in E8_EPS:
        tur = E8_TUR
    maske = _maske(kol)
    gecis = 0
    iletisim_bayt = 0

    if kol == "merkezi":
        envs = make_client_envs(tohum)
        if maske is not None:
            envs = [_MaskeliOrtam(e, maske) for e in envs]
        ag = new_agent(tohum)
        for _ in range(tur):
            for e in envs:
                train_local(e, ag)
                gecis += LOCAL_ROLLOUTS * ROLLOUT_LEN
        son = ag
        meta = {"kaynak": "faz_a_config.make_client_envs (havuzlanmis)"}
    else:
        envs, meta = _istemci_ortamlari(kol, tohum)
        if maske is not None:
            envs = [_MaskeliOrtam(e, maske) for e in envs]
        n = len(envs)
        C = None
        if kol in E8_EPS:
            C = json.loads((OUT / "faz_e8_C.json").read_text())["C_dondurulmus"]
            agg = FedAvgAggregator(seed=tohum, dp_mode="clip_l1", dp_clip_c=C,
                                   dp_epsilon=E8_EPS[kol], dp_rounds=E8_TUR)
        elif kol.startswith("fedprox"):
            agg = FedProxAggregator(mu=0.01, seed=tohum)
        else:
            agg = FedAvgAggregator(seed=tohum)
        cl = [new_agent(tohum + i) for i in range(n)]
        g = cl[0].params()
        for _ in range(tur):
            for c in cl:
                c.set_params(g)
            iletisim_bayt += n * _param_bayt(g)                 # indirme
            for e, c in zip(envs, cl):
                if kol == "fedprox_gercek":
                    _egit_proksimal(e, c, g, mu=0.01)
                else:
                    train_local(e, c)
                gecis += LOCAL_ROLLOUTS * ROLLOUT_LEN
                if kol == "fedprox_yakinlik":
                    c.set_params(agg.apply_proximal_step(c.params(), g, lr=1.0))
            iletisim_bayt += sum(_param_bayt(c.params()) for c in cl)   # yukleme
            if kol in E8_EPS:
                g = agg.aggregate([c.params() for c in cl], global_params=g)
            else:
                g = agg.aggregate([c.params() for c in cl])
        son = new_agent(0); son.set_params(g)
        meta["n_istemci"] = n
        if kol in E8_EPS:
            meta["dp_defteri"] = agg.privacy_defteri()

    yte, yp = _degerlendir(son, maske)
    sure = time.time() - t0

    k = KosuKaydi(damar=PILLAR, deney=_deney(kol), kol=kol, tohum=tohum)
    k.yapilandirma_koddan("faz_a_config",
                          ["PILLAR", "N_ACTIONS", "STATE_DIM", "NEW_STEP_API",
                           "INFO_TRUE_KEY", "ACTION_LABELS", "CRITICAL_ACTIONS",
                           "MODALITY_GROUPS"])
    k.yapilandirma_koddan("faz_a_staged",
                          ["LOCAL_ROLLOUTS", "ROLLOUT_LEN", "PROBE_STEPS", "EVAL_STEPS"])
    k.yapilandirma_koddan("faz_e_kampanya",
                          ["TUR_VARSAYILAN", "E8_TUR", "E8_EPS", "E1_BIRINCIL"])
    k.yapilandirma_ekle("kosu", {"kol": kol, "tur_koddan": tur, "tohum": tohum,
                                 "cevre_gecisi": gecis,
                                 "iletisim_bayt": iletisim_bayt,
                                 "istemci_kurulumu": meta,
                                 "e1_birincil_modalite": E1_BIRINCIL if maske is not None else None})
    k.veri_uretilmis(f"{PILLAR} {kol} tohum={tohum} tur={tur}; "
                     f"degerlendirme: {e2.EVAL_REPS}x{e2.EVAL_STEPS} esdeger protokol",
                     n_kayit=int(len(yte)))
    cm = k.tahminler(yte, yp, n_sinif=N_ACTIONS, etiketler=list(ACTION_LABELS))
    m = makro_f1(cm)
    k.metrik(duvar_saati_sn=round(sure, 2), cevre_gecisi=gecis,
             iletisim_bayt=iletisim_bayt,
             kritik_sinif_duyarlilik=[m["sinif_duyarlilik"][c] for c in sorted(CRITICAL_ACTIONS)])
    kp = k.yaz()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"params_e7_{kol}_t{tohum}.json").write_text(json.dumps(_p2j(son.params())))
    return {"durum": "tamam", "damar": PILLAR, "kol": kol, "tohum": tohum, "tur": tur,
            "makro_f1": m["makro_f1"], "dogruluk": m["dogruluk"],
            "duvar_saati_sn": round(sure, 2), "cevre_gecisi": gecis,
            "iletisim_bayt": iletisim_bayt, "kayit": str(kp)}


def _egit_proksimal(env, ajan, g, mu=0.01):
    """E5 — OZGUN FedProx: yerel PPO kaybina mu/2*||w - w_g||^2 eklenir."""
    for _ in range(LOCAL_ROLLOUTS):
        s = env_reset(env)
        S, A, LP, R, V, D = [], [], [], [], [], []
        for _ in range(ROLLOUT_LEN):
            a, lp, v = ajan.act(s)
            s2, r, done, _ = env_step(env, a)
            S.append(s); A.append(a); LP.append(lp); R.append(r); V.append(v); D.append(done)
            s = env_reset(env) if done else s2
        adv, ret = ajan.compute_gae(R, V, D)
        ajan.update(S, A, LP, adv, ret, epochs=2, prox_ref=g, prox_mu=mu)


def _deney(kol):
    if kol in E8_EPS: return "E8"
    if kol.startswith("e4_"): return "E4"
    if kol.startswith("e1_"): return "E1"
    if kol.startswith("fedprox"): return "E5"
    return "E6"


if __name__ == "__main__":
    kol = sys.argv[1]; tohum = int(sys.argv[2])
    tur = int(sys.argv[3]) if len(sys.argv) > 3 else TUR_VARSAYILAN
    print(json.dumps(kos(kol, tohum, tur), ensure_ascii=False))
