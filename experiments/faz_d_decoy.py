"""Faz D / D1 — yem-sinyal (decoy) atif testi.

SS tur-1 elestirisinin onerdigi XAI yanlislarma enstrumani (SS v27 5.4):
gozleme anlamsal olarak ALAKASIZ K=2 kanal eklenir, FedProx ayni protokolle
yeniden egitilir ve grup-Shapley'nin decoy grubuna verdigi atif olculur.
BEKLENTI decoy atifinin sifira yakin kalmasidir; sonuc NE CIKARSA raporlanir.
Kullanim: python faz_d_decoy.py            (tam kosu, 160 round)
          python faz_d_decoy.py --smoke    (yalniz hizli dogrulama, 6 round)
Cikti: results/faz_d_decoy.json (+ params_fedprox_decoy.json)
"""
from __future__ import annotations
import json, sys, time
from itertools import combinations
from math import factorial
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
from faz_a_config import (PILLAR, make_client_envs, make_env, STATE_DIM,
                          N_ACTIONS, MODALITY_GROUPS, ACTION_LABELS,
                          NEW_STEP_API, INFO_TRUE_KEY, CRITICAL_ACTIONS)
from faz_a_staged import (train_local, evaluate, _save, _p2j, OUT,
                          ROUNDS_FED, PROBE_EVERY, PROBE_STEPS, SEED)
from src.rl_agents.ppo_actor_critic import PPOActorCritic
from src.federated.fedprox import FedProxAggregator

K_DECOY = 2
DIM = STATE_DIM + K_DECOY
GROUPS = {**{k: np.asarray(v) for k, v in MODALITY_GROUPS.items()},
          "decoy": np.arange(STATE_DIM, DIM)}
if len(GROUPS) == 1:   # tek-modlu (MRO): gercek blok + decoy
    GROUPS = {"real": np.arange(STATE_DIM), "decoy": np.arange(STATE_DIM, DIM)}

class DecoyEnv:
    """Gozleme iid U(0,1) decoy kanallari ekler; odul/gecis DEGISMEZ."""
    def __init__(self, env, seed):
        self._env = env
        self._rng = np.random.default_rng(77_000 + seed)
    def _aug(self, s):
        return np.concatenate([np.asarray(s, dtype=float),
                               self._rng.uniform(0, 1, K_DECOY)])
    def reset(self, **kw):
        out = self._env.reset(**kw)
        if isinstance(out, tuple): return self._aug(out[0]), *out[1:]
        return self._aug(out)
    def step(self, a):
        out = self._env.step(a)
        return (self._aug(out[0]),) + tuple(out[1:])
    def __getattr__(self, k): return getattr(self._env, k)

def new_agent(seed):
    return PPOActorCritic(fused_dim=DIM, n_actions=N_ACTIONS, hidden=64,
                          lr=0.05, reward_scale=0.05, seed=seed)

def env_reset(env, seed=None):
    out = env.reset(seed=seed) if (NEW_STEP_API and seed is not None) else env.reset()
    return out[0] if isinstance(out, tuple) else out

def env_step(env, a):
    out = env.step(a)
    if len(out) == 5:
        s, r, te, tr, info = out
        return s, r, te or tr, info
    return out

def eval_decoy(agent, reps=3, steps=600):
    cm = np.zeros((N_ACTIONS, N_ACTIONS), dtype=int); trip = []
    for rep in range(reps):
        env = DecoyEnv(make_env(SEED + 900 + rep), 500 + rep)
        s = env_reset(env, seed=2026 + rep)
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
    return {"mean_reward": round(float(np.mean([t[0] for t in trip])), 2),
            "accuracy_pct": round(float(np.mean([t[1] for t in trip])), 1),
            "critical_recall": round(float(np.mean([t[2] for t in trip])), 3),
            "distinct_actions_used": int((cm.sum(axis=0) > 0).sum())}

def group_shapley(agent, n_states=40):
    names = list(GROUPS); n = len(names)
    def f(coal, state):
        s = np.zeros(DIM)
        for nm in coal: s[GROUPS[nm]] = state[GROUPS[nm]]
        return agent.policy(s)
    agg = {}
    envx = DecoyEnv(make_env(SEED + 902), 901)
    for i in range(n_states):
        st = env_reset(envx, seed=1000 + i)
        full = f(tuple(names), st); a = int(np.argmax(full)); phi = {}
        for nm in names:
            others = [x for x in names if x != nm]; val = 0.0
            for k in range(n):
                for S in combinations(others, k):
                    w = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                    val += w * (f(tuple(S) + (nm,), st)[a] - f(tuple(S), st)[a])
            phi[nm] = val
        tot = sum(abs(v) for v in phi.values()) or 1.0
        agg.setdefault(ACTION_LABELS[a], []).append(
            {m: 100 * abs(v) / tot for m, v in phi.items()})
    return {act: {m: round(float(np.mean([p[m] for p in ps])), 1) for m in GROUPS}
            for act, ps in agg.items()}

def main(smoke=False):
    t0 = time.time()
    rounds = 6 if smoke else ROUNDS_FED
    agg = FedProxAggregator(mu=0.01, seed=SEED)
    envs = [DecoyEnv(e, i) for i, e in enumerate(make_client_envs(SEED))]
    cl = [new_agent(SEED + i) for i in range(len(envs))]
    g = cl[0].params()
    for rnd in range(rounds):
        for c in cl: c.set_params(g)
        for e, c in zip(envs, cl):
            train_local(e, c)
            c.set_params(agg.apply_proximal_step(c.params(), g, lr=1.0))
        g = agg.aggregate([c.params() for c in cl])
    fin = new_agent(0); fin.set_params(g)
    import datetime
    shap = group_shapley(fin, n_states=8 if smoke else 40)
    decoy_by_action = {a: v.get("decoy") for a, v in shap.items()}
    vals = [v for v in decoy_by_action.values() if v is not None]
    res = {"pillar": PILLAR, "date": datetime.date.today().isoformat(), "seed": SEED,
           "design": {"k_decoy": K_DECOY, "groups": {k: v.tolist() for k, v in GROUPS.items()},
                      "rounds": rounds, "smoke": smoke,
                      "note": "decoy = iid U(0,1), odulle/gecisle iliskisiz; beklenti "
                              "grup-Shapley decoy atifi ~0; sonuc ne cikarsa raporlanir"},
           "final_eval": eval_decoy(fin, reps=1 if smoke else 3, steps=200 if smoke else 600),
           "shapley_pct_by_action": shap,
           "decoy_attribution_pct": {"by_action": decoy_by_action,
                                     "mean": round(float(np.mean(vals)), 2) if vals else None,
                                     "max": round(float(np.max(vals)), 2) if vals else None}}
    if not smoke:
        _save(OUT / "faz_d_decoy.json", res)
        _save(OUT / "params_fedprox_decoy.json", _p2j(g))
    print(PILLAR, "faz_d_decoy", "SMOKE" if smoke else "TAMAM",
          round(time.time()-t0, 1), "sn | decoy atif ort/max:",
          res["decoy_attribution_pct"]["mean"], "/", res["decoy_attribution_pct"]["max"],
          "| eval:", res["final_eval"])

if __name__ == "__main__":
    main(smoke="--smoke" in sys.argv)
