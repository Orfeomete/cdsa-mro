"""Faz D / D2 — recall-tabani korumali kisitli kesif (gated entropy).

SS tur-1 elestirisinin 'sert kisit esigi' onerisinin uygulanabilir ilk
versiyonu (SS v27 5.6): entropi bonusu (0.05) YALNIZ kritik-recall probe'u
taban esiginin (FLOOR=0.90) uzerindeyken aktif; probe tabanin altina
dustugunde bonus kapatilir, ustune cikinca yeniden acilir. Karsilastirma
tabanlari: faz_a fedprox (statik) ve faz_c ent=0.05 (kisitsiz kesif).
Kullanim: python faz_d_gated_entropy.py           (tam kosu, 160 round)
          python faz_d_gated_entropy.py --smoke   (6 round dogrulama)
Cikti: results/faz_d_gated_entropy.json (+ params_fedprox_gatedent.json)
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
from faz_a_config import PILLAR, make_client_envs
from faz_a_staged import (train_local, evaluate, _save, _p2j, OUT,
                          ROUNDS_FED, PROBE_EVERY, PROBE_STEPS, SEED)
from faz_b_dynamic_reward import eval_final
from faz_c_entropy import PPOWithEntropy, new_ent_agent
from src.federated.fedprox import FedProxAggregator

ENT, FLOOR = 0.05, 0.90

def probe_recall(g):
    probe = new_ent_agent(0, 0.0); probe.set_params(g)
    _, _, crit = evaluate(probe, steps=PROBE_STEPS)
    return crit if crit is not None else 0.0

def main(smoke=False):
    t0 = time.time()
    rounds = 6 if smoke else ROUNDS_FED
    agg = FedProxAggregator(mu=0.01, seed=SEED)
    envs = make_client_envs(SEED)
    cl = [new_ent_agent(SEED + i, ENT) for i in range(len(envs))]
    g = cl[0].params()
    gate_on, gate_log = True, []
    for rnd in range(rounds):
        for c in cl:
            c.set_params(g)
            c.ent_coef = ENT if gate_on else 0.0
        for e, c in zip(envs, cl):
            train_local(e, c)
            c.set_params(agg.apply_proximal_step(c.params(), g, lr=1.0))
        g = agg.aggregate([c.params() for c in cl])
        if (rnd + 1) % (2 if smoke else PROBE_EVERY) == 0:
            rec = probe_recall(g)
            gate_on = rec >= FLOOR
            gate_log.append({"round": rnd + 1, "probe_recall": round(float(rec), 3),
                             "gate_on_next": bool(gate_on)})
    fin = new_ent_agent(0, 0.0); fin.set_params(g)
    import datetime
    res = {"pillar": PILLAR, "date": datetime.date.today().isoformat(), "seed": SEED,
           "design": {"ent_coef": ENT, "recall_floor": FLOOR, "rounds": rounds,
                      "smoke": smoke,
                      "note": "entropi bonusu yalniz probe kritik-recall >= FLOOR iken "
                              "aktif; probe her PROBE_EVERY roundda, greedy politika ile"},
           "gate_log": gate_log,
           "gate_on_ratio": round(sum(1 for x in gate_log if x["gate_on_next"]) / max(len(gate_log), 1), 2),
           "final": eval_final(fin)}
    if not smoke:
        _save(OUT / "faz_d_gated_entropy.json", res)
        _save(OUT / "params_fedprox_gatedent.json", _p2j(g))
    print(PILLAR, "faz_d_gated_entropy", "SMOKE" if smoke else "TAMAM",
          round(time.time()-t0, 1), "sn | gate_on orani:", res["gate_on_ratio"],
          "| final:", {k: res["final"][k] for k in ("accuracy_pct","critical_recall","distinct_actions_used")})

if __name__ == "__main__":
    main(smoke="--smoke" in sys.argv)
