"""Faz C / C2 — entropi-hedefli kesif taramasi (FedProx, DP'siz).

Amac: cokusun (asiri-uyari / tek-eylem rejimi) entropi bonusuyla kirilip
kirilmadigini olcmek. Yayimlanmis ajan koduna DOKUNULMAZ; entropi bonusu bu
scriptteki alt-sinifta eklenir. ent_coef=0 tabani faz_a fedprox'tur.
REVIZYON KITI MALZEMESI - makale metnine otomatik ISLENMEZ.
Kullanim: python3 faz_c_entropy.py
Cikti: results/faz_c_entropy.json (+ params_fedprox_ent*.json)
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
from faz_a_config import PILLAR, make_client_envs, STATE_DIM, N_ACTIONS
from faz_a_staged import (train_local, evaluate, _save, _p2j, OUT,
                          ROUNDS_FED, PROBE_EVERY, PROBE_STEPS, SEED)
from faz_b_dynamic_reward import eval_final
from src.rl_agents.ppo_actor_critic import PPOActorCritic, _softmax, _onehot
from src.federated.fedprox import FedProxAggregator

ENT_VALUES = (0.01, 0.05)

class PPOWithEntropy(PPOActorCritic):
    """update() kopyasi + entropi bonusu. Orijinal sinif degistirilmez.
    Entropi terimi: loss -= ent_coef * H(p); dH/dlogits_j = -p_j(log p_j + H)."""
    def __init__(self, *a, ent_coef=0.01, **kw):
        super().__init__(*a, **kw)
        self.ent_coef = float(ent_coef)
    def update(self, states, actions, old_logps, advantages, returns, epochs=4):
        states = np.asarray(states, dtype=float)
        actions = np.asarray(actions, dtype=int)
        old_logps = np.asarray(old_logps, dtype=float)
        adv = np.asarray(advantages, dtype=float)
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        rets = np.asarray(returns, dtype=float)
        N = len(actions); last_loss = 0.0
        for _ in range(epochs):
            gW1 = np.zeros_like(self.W1); gb1 = np.zeros_like(self.b1)
            gWa = np.zeros_like(self.Wa); gba = np.zeros_like(self.ba)
            gWv = np.zeros_like(self.Wv); gbv = np.zeros_like(self.bv)
            last_loss = 0.0
            for i in range(N):
                s = states[i]
                h = self._trunk(s)
                logits = self.Wa @ h + self.ba
                p = _softmax(logits)
                a = actions[i]
                logp = np.log(p[a] + 1e-12)
                ratio = np.exp(logp - old_logps[i])
                clipped = np.clip(ratio, 1 - self.clip_eps, 1 + self.clip_eps)
                use_grad = (ratio * adv[i]) <= (clipped * adv[i])
                v = float((self.Wv @ h + self.bv)[0])
                v_err = v - rets[i]
                logp_all = np.log(p + 1e-12)
                H = float(-(p * logp_all).sum())
                last_loss += (-min(ratio * adv[i], clipped * adv[i])
                              + 0.5 * v_err ** 2 - self.ent_coef * H)
                dlogits = np.zeros(self.n_actions)
                if use_grad:
                    dlogits += -(ratio * adv[i]) * (_onehot(a, self.n_actions) - p)
                # entropi bonusunun loss'a gradyani: d(-c*H)/dz = c * p * (log p + H)
                dlogits += self.ent_coef * p * (logp_all + H)
                gWa += np.outer(dlogits, h); gba += dlogits
                dh_a = self.Wa.T @ dlogits
                dv = v_err
                gWv += dv * h[None, :]; gbv += np.array([dv])
                dh = dh_a + dv * self.Wv.ravel()
                dz = dh * (1 - h ** 2)
                gW1 += np.outer(dz, s); gb1 += dz
            grads = ((gW1, "W1"), (gb1, "b1"), (gWa, "Wa"),
                     (gba, "ba"), (gWv, "Wv"), (gbv, "bv"))
            gnorm = np.sqrt(sum(float((g * g).sum()) for g, _ in grads)) / N
            scale = (self.max_grad_norm / gnorm) if gnorm > self.max_grad_norm else 1.0
            for g, m in grads:
                setattr(self, m, getattr(self, m) - self.lr * scale * g / N)
        return last_loss / N

def new_ent_agent(seed, ent):
    return PPOWithEntropy(fused_dim=STATE_DIM, n_actions=N_ACTIONS, hidden=64,
                          lr=0.05, reward_scale=0.05, seed=seed, ent_coef=ent)

def train_ent(ent):
    agg = FedProxAggregator(mu=0.01, seed=SEED)
    envs = make_client_envs(SEED)
    cl = [new_ent_agent(SEED + i, ent) for i in range(len(envs))]
    g, curve = cl[0].params(), []
    for rnd in range(ROUNDS_FED):
        for c in cl: c.set_params(g)
        for e, c in zip(envs, cl):
            train_local(e, c)
            c.set_params(agg.apply_proximal_step(c.params(), g, lr=1.0))
        g = agg.aggregate([c.params() for c in cl])
        if (rnd + 1) % PROBE_EVERY == 0:
            probe = new_ent_agent(0, ent); probe.set_params(g)
            curve.append(evaluate(probe, steps=PROBE_STEPS)[0])
    fin = new_ent_agent(0, ent); fin.set_params(g)
    _save(OUT / f"params_fedprox_ent{str(ent).replace('.','_')}.json", _p2j(g))
    return {"final": eval_final(fin), "curve": curve}

def main():
    t0 = time.time()
    import datetime
    res = {"pillar": PILLAR, "date": datetime.date.today().isoformat(), "seed": SEED,
           "design": {"agg": "fedprox mu=0.01, DP yok", "rounds": ROUNDS_FED,
                      "ent_values": list(ENT_VALUES),
                      "note": "entropi bonusu alt-sinifta; ent=0 tabani "
                              "faz_a_results.json fedprox; degerlendirme statik "
                              "ortam, faz_b protokolu (3 seed)"}}
    for ent in ENT_VALUES:
        t1 = time.time()
        res[f"ent_{ent}"] = train_ent(ent)
        print(PILLAR, f"ent={ent} bitti", round(time.time()-t1,1), "sn ->",
              {k: v for k, v in res[f"ent_{ent}"]["final"].items()
               if k in ("accuracy_pct","critical_recall","distinct_actions_used")})
    _save(OUT / "faz_c_entropy.json", res)
    print(PILLAR, "faz_c_entropy TAMAM", round(time.time()-t0,1), "sn")

if __name__ == "__main__":
    main()
