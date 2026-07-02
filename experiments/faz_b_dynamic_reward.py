"""Faz B / B3 — operasyonel-tempo-duyarli odul (FedProx yeniden egitim).

Onaylanan tasarim (02.07.2026): son T=32 adimdaki kritik-olay yogunlugu
tempo katsayisini verir. Kacirilan-kritik cezasi x(1+kappa*tempo),
sahte-kritik cezasi x(1+kappa*(1-tempo)); kappa=1.0. Dogru eylem ve diger
durumlar degismez. Egitim: FedProx mu=0.01, 160 round (chunk'li), statik-odul
Faz A ile ayni seed protokolu. DEGERLENDIRME statik-odul ortaminda yapilir
(karsilastirilabilirlik); accuracy/recall odulden bagimsizdir.
Kullanim: python3 faz_b_dynamic_reward.py run   (checkpoint'li, tekrar cagir)
Cikti: results/faz_b_dynamic_reward.json
"""
from __future__ import annotations
import json, sys, time
from collections import deque
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
from faz_a_config import (PILLAR, make_client_envs, N_ACTIONS, STATE_DIM,
                          ACTION_LABELS, NEW_STEP_API, INFO_TRUE_KEY,
                          CRITICAL_ACTIONS)
from faz_a_staged import (new_agent, env_reset, env_step, train_local,
                          evaluate, _load, _save, _p2j, _j2p, OUT,
                          ROUNDS_FED, FED_CHUNK, PROBE_EVERY, PROBE_STEPS, SEED)
from src.federated.fedprox import FedProxAggregator

KAPPA, WINDOW = 1.0, 32
CKPT = OUT / "ckpt_fedprox_dynrew.json"
RES_F = OUT / "faz_b_dynamic_reward.json"

class TempoRewardWrapper:
    """Odul olceklemesi; gozlem/gecisler degismez."""
    def __init__(self, env):
        self._env = env
        self._win = deque(maxlen=WINDOW)
    def reset(self, **kw):
        self._win.clear()
        return self._env.reset(**kw)
    def step(self, action):
        out = self._env.step(action)
        if len(out) == 5: s, r, te, tr, info = out
        else: (s, r, done, info), te, tr = out, None, None
        a_true = info.get(INFO_TRUE_KEY) if isinstance(info, dict) else None
        if a_true is not None:
            tempo = (sum(self._win) / len(self._win)) if self._win else 0.0
            self._win.append(1 if a_true in CRITICAL_ACTIONS else 0)
            if action != a_true:
                if a_true in CRITICAL_ACTIONS and action not in CRITICAL_ACTIONS:
                    r = r * (1.0 + KAPPA * tempo)            # kacirilan kritik
                elif action in CRITICAL_ACTIONS and a_true not in CRITICAL_ACTIONS:
                    r = r * (1.0 + KAPPA * (1.0 - tempo))    # sahte kritik
        return (s, r, te, tr, info) if len(out) == 5 else (s, r, done, info)
    def __getattr__(self, k):
        return getattr(self._env, k)

def eval_final(agent, reps=3, steps=600):
    """Statik ortamda per-sinif recall + confusion (3 tekrar toplami)."""
    from faz_a_config import make_env
    cm = np.zeros((N_ACTIONS, N_ACTIONS), dtype=int)
    trip = []
    for rep in range(reps):
        env = make_env(SEED + 900 + rep)
        s = env_reset(env, seed=2026 + rep) if NEW_STEP_API else env_reset(env)
        tot = corr = known = ch = ct = 0
        for _ in range(steps):
            a = agent.act(s, deterministic=True)[0]
            s2, r, done, info = env_step(env, int(a))
            tot += r
            if isinstance(info, dict) and INFO_TRUE_KEY in info:
                at = int(info[INFO_TRUE_KEY]); known += 1
                corr += int(a == at); cm[at, int(a)] += 1
                if at in CRITICAL_ACTIONS: ct += 1; ch += int(a == at)
            s = env_reset(env) if done else s2
        trip.append((tot/steps, 100*corr/known if known else None, ch/ct if ct else None))
    mr = round(float(np.mean([t[0] for t in trip])), 2)
    acc = round(float(np.mean([t[1] for t in trip])), 1)
    crit = round(float(np.mean([t[2] for t in trip])), 3)
    rec = {ACTION_LABELS[i]: (round(cm[i, i] / cm[i].sum(), 3) if cm[i].sum() else None)
           for i in range(N_ACTIONS)}
    n_pred = int((cm.sum(axis=0) > 0).sum())
    return {"mean_reward": mr, "accuracy_pct": acc, "critical_recall": crit,
            "per_class_recall": rec, "distinct_actions_used": n_pred,
            "confusion_sum": cm.tolist()}

def main():
    t0 = time.time()
    agg = FedProxAggregator(mu=0.01, seed=SEED)
    envs = [TempoRewardWrapper(e) for e in make_client_envs(SEED)]
    cl = [new_agent(SEED + i) for i in range(len(envs))]
    ck = _load(CKPT, None)
    if ck: g, curve, start = _j2p(ck["g"]), ck["curve"], ck["round"]
    else: g, curve, start = cl[0].params(), [], 0
    end = min(start + FED_CHUNK, ROUNDS_FED)
    for rnd in range(start, end):
        for c in cl: c.set_params(g)
        for e, c in zip(envs, cl):
            train_local(e, c)
            c.set_params(agg.apply_proximal_step(c.params(), g, lr=1.0))
        g = agg.aggregate([c.params() for c in cl])
        if (rnd + 1) % PROBE_EVERY == 0:
            probe = new_agent(0); probe.set_params(g)
            curve.append(evaluate(probe, steps=PROBE_STEPS)[0])
    _save(CKPT, {"round": end, "curve": curve, "g": _p2j(g)})
    if end < ROUNDS_FED:
        print(PILLAR, f"dynrew PARTIAL {end}/{ROUNDS_FED} — tekrar çağır,",
              round(time.time()-t0,1), "sn"); return
    fin = new_agent(0); fin.set_params(g)
    res = {"pillar": PILLAR, "date": "2026-07-02", "seed": SEED,
           "design": {"kappa": KAPPA, "window": WINDOW, "agg": "fedprox mu=0.01",
                      "rounds": ROUNDS_FED,
                      "note": "tempo=son 32 adimdaki kritik-olay orani; kacirilan-kritik "
                              "cezasi x(1+k*tempo), sahte-kritik x(1+k*(1-tempo)); "
                              "degerlendirme statik-odul ortaminda"},
           "dynrew_fedprox": eval_final(fin), "curve": curve}
    base = new_agent(0); base.set_params(_j2p(_load(OUT / "params_fedprox.json", {})))
    res["static_fedprox_baseline"] = eval_final(base)
    _save(RES_F, res)
    _save(OUT / "params_fedprox_dynrew.json", _p2j(g))
    d, b = res["dynrew_fedprox"], res["static_fedprox_baseline"]
    print(PILLAR, "dynrew TAMAM", round(time.time()-t0,1), "sn")
    print("  statik :", b["accuracy_pct"], b["critical_recall"], b["per_class_recall"])
    print("  dinamik:", d["accuracy_pct"], d["critical_recall"], d["per_class_recall"])

if __name__ == "__main__":
    main()
