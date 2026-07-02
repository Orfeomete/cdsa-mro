"""Faz C / C1 — diferansiyel mahremiyet epsilon taramasi (FedProx + Laplace DP).

Amac: eps=1.0'daki bilinen davranisin (faz_a) iki yanini olcmek. eps=0.5 (siki
butce) ve eps=2.0 (gevsek butce) icin ayni seed protokoluyle 160 round FedProx
egitimi. Degerlendirme statik ortamda, faz_b eval protokoluyle (3 seed).
REVIZYON KITI MALZEMESI - makale metnine otomatik ISLENMEZ.
Kullanim: python3 faz_c_dp_sweep.py
Cikti: results/faz_c_dp_sweep.json (+ params_fedprox_dp_eps*.json)
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
from faz_a_config import PILLAR, make_client_envs
from faz_a_staged import (new_agent, train_local, evaluate, _load, _save,
                          _p2j, _j2p, OUT, ROUNDS_FED, PROBE_EVERY,
                          PROBE_STEPS, SEED)
from faz_b_dynamic_reward import eval_final
from src.federated.fedprox import FedProxAggregator

EPS_VALUES = (0.5, 2.0)   # eps=1.0 zaten faz_a'da mevcut

def train_dp(eps):
    agg = FedProxAggregator(mu=0.01, dp_epsilon=eps, dp_sensitivity=0.01, seed=SEED)
    envs = make_client_envs(SEED)
    cl = [new_agent(SEED + i) for i in range(len(envs))]
    g, curve = cl[0].params(), []
    for rnd in range(ROUNDS_FED):
        for c in cl: c.set_params(g)
        for e, c in zip(envs, cl):
            train_local(e, c)
            c.set_params(agg.apply_proximal_step(c.params(), g, lr=1.0))
        g = agg.aggregate([c.params() for c in cl])
        if (rnd + 1) % PROBE_EVERY == 0:
            probe = new_agent(0); probe.set_params(g)
            curve.append(evaluate(probe, steps=PROBE_STEPS)[0])
    fin = new_agent(0); fin.set_params(g)
    _save(OUT / f"params_fedprox_dp_eps{str(eps).replace('.','_')}.json", _p2j(g))
    return {"final": eval_final(fin), "curve": curve}

def main():
    t0 = time.time()
    res = {"pillar": PILLAR, "date": None, "seed": SEED,
           "design": {"agg": "fedprox mu=0.01 + Laplace DP, sensitivity=0.01",
                      "rounds": ROUNDS_FED, "eps_values": list(EPS_VALUES),
                      "note": "eps=1.0 referansi faz_a_results.json'da; "
                              "degerlendirme statik ortam, faz_b protokolu (3 seed)"}}
    import datetime
    res["date"] = datetime.date.today().isoformat()
    for eps in EPS_VALUES:
        t1 = time.time()
        res[f"eps_{eps}"] = train_dp(eps)
        print(PILLAR, f"eps={eps} bitti", round(time.time()-t1,1), "sn ->",
              {k: v for k, v in res[f"eps_{eps}"]["final"].items()
               if k in ("accuracy_pct","critical_recall","distinct_actions_used")})
    _save(OUT / "faz_c_dp_sweep.json", res)
    print(PILLAR, "faz_c_dp_sweep TAMAM", round(time.time()-t0,1), "sn")

if __name__ == "__main__":
    main()
