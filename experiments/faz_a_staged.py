"""Faz A / A6 — staged runner (her aşama < 40 sn, checkpoint'li).

Kullanım: python3 faz_a_staged.py [base|fedavg|fedprox|fedprox_dp|finalize]
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
from faz_a_config import (PILLAR, make_env, make_client_envs, N_ACTIONS,
                          STATE_DIM, MODALITY_GROUPS, ACTION_LABELS,
                          NEW_STEP_API, INFO_TRUE_KEY, CRITICAL_ACTIONS)
from src.rl_agents.ppo_actor_critic import PPOActorCritic
from src.federated.fedavg import FedAvgAggregator
from src.federated.fedprox import FedProxAggregator

ROUNDS, LOCAL_ROLLOUTS, ROLLOUT_LEN = 100, 6, 96
ROUNDS_FED, FED_CHUNK = 160, 80
PROBE_EVERY, PROBE_STEPS, EVAL_STEPS = 8, 300, 600
SEED = 42
OUT = HERE / "results"; OUT.mkdir(exist_ok=True)
RES_F, CURVE_F = OUT / "faz_a_results.json", OUT / "faz_a_curves.json"

def _load(f, d): return json.loads(f.read_text()) if f.exists() else d
def _save(f, obj): f.write_text(json.dumps(obj, indent=2))
def _p2j(p): return {k: (_p2j(v) if isinstance(v, dict) else np.asarray(v).tolist()) for k, v in p.items()}
def _j2p(p): return {k: (_j2p(v) if isinstance(v, dict) else np.asarray(v, dtype=float)) for k, v in p.items()}

def new_agent(seed): return PPOActorCritic(fused_dim=STATE_DIM, n_actions=N_ACTIONS,
                                           hidden=64, lr=0.05, reward_scale=0.05, seed=seed)

def env_reset(env, seed=None):
    out = env.reset(seed=seed) if NEW_STEP_API else env.reset()
    return out[0] if isinstance(out, tuple) else out

def env_step(env, a):
    out = env.step(a)
    if len(out) == 5:
        s, r, te, tr, info = out
        return s, r, te or tr, info
    return out

def train_local(env, ag):
    for _ in range(LOCAL_ROLLOUTS):
        s = env_reset(env)
        S, A, LP, R, V, D = [], [], [], [], [], []
        for _ in range(ROLLOUT_LEN):
            a, lp, v = ag.act(s)
            s2, r, done, _ = env_step(env, a)
            S.append(s); A.append(a); LP.append(lp); R.append(r); V.append(v); D.append(done)
            s = env_reset(env) if done else s2
        adv, ret = ag.compute_gae(R, V, D)
        ag.update(S, A, LP, adv, ret, epochs=2)

def evaluate(agent=None, steps=EVAL_STEPS, rng=None):
    env = make_env(SEED + 900); s = env_reset(env, seed=2026)
    tot = corr = known = ch = ct = 0
    for _ in range(steps):
        a = int(rng.integers(N_ACTIONS)) if agent is None else agent.act(s, deterministic=True)[0]
        s2, r, done, info = env_step(env, a)
        tot += r
        if isinstance(info, dict) and INFO_TRUE_KEY in info:
            known += 1; at = info[INFO_TRUE_KEY]; corr += int(a == at)
            if at in CRITICAL_ACTIONS: ct += 1; ch += int(a == at)
        s = env_reset(env) if done else s2
    return (round(tot / steps, 2),
            round(100 * corr / known, 1) if known else None,
            round(ch / ct, 3) if ct else None)

def pack(mr, acc, crit, curve=None):
    d = {"mean_reward": mr, "accuracy_pct": acc, "critical_recall": crit}
    if curve:
        tgt = 0.9 * curve[-1] if curve[-1] > 0 else curve[-1]
        d["convergence_round"] = next((i + 1 for i, v in enumerate(curve) if v >= tgt), None)
    return d

def run_fed(label):
    agg = {"fedavg": FedAvgAggregator(seed=SEED),
           "fedprox": FedProxAggregator(mu=0.01, seed=SEED),
           "fedprox_dp": FedProxAggregator(mu=0.01, dp_epsilon=1.0, dp_sensitivity=0.01, seed=SEED)}[label]
    envs = make_client_envs(SEED)
    cl = [new_agent(SEED + i) for i in range(len(envs))]
    ckpt_f = OUT / f"ckpt_{label}.json"
    ck = _load(ckpt_f, None)
    if ck:
        g, curve, start = _j2p(ck["g"]), ck["curve"], ck["round"]
    else:
        g, curve, start = cl[0].params(), [], 0
    use_prox = isinstance(agg, FedProxAggregator)
    end = min(start + FED_CHUNK, ROUNDS_FED)
    for rnd in range(start, end):
        for c in cl: c.set_params(g)
        for e, c in zip(envs, cl):
            train_local(e, c)
            if use_prox:
                c.set_params(agg.apply_proximal_step(c.params(), g, lr=1.0))
        g = agg.aggregate([c.params() for c in cl])
        if (rnd + 1) % PROBE_EVERY == 0:
            probe = new_agent(0); probe.set_params(g)
            curve.append(evaluate(probe, steps=PROBE_STEPS)[0])
    if end < ROUNDS_FED:
        _save(ckpt_f, {"round": end, "curve": curve, "g": _p2j(g)})
        print(label, f"PARTIAL {end}/{ROUNDS_FED} — tekrar çağır")
        return
    _save(ckpt_f, {"round": end, "curve": curve, "g": _p2j(g)})
    fin = new_agent(0); fin.set_params(g)
    res, cur = _load(RES_F, {}), _load(CURVE_F, {})
    mr, acc, crit = evaluate(fin)
    res[label] = pack(mr, acc, crit, curve); cur[label] = curve
    _save(RES_F, res); _save(CURVE_F, cur)
    _save(OUT / f"params_{label}.json", _p2j(g))
    print(label, "->", res[label])

def main(stage):
    t0 = time.time()
    if stage == "base":
        res = {}
        res.update({"pillar": PILLAR, "date": "2026-06-11", "seed": SEED,
                    "config": {"rounds": ROUNDS, "clients": 3, "local_rollouts": LOCAL_ROLLOUTS,
                               "rollout_len": ROLLOUT_LEN, "eval_steps": EVAL_STEPS,
                               "agent": {"hidden": 64, "lr": 0.05, "reward_scale": 0.05,
                                          "max_grad_norm": 10},
                               "fedprox_mu": 0.01,
                               "dp": {"epsilon": 1.0, "sensitivity": 0.01}}})
        rng = np.random.default_rng(SEED)
        mr, acc, crit = evaluate(None, rng=rng)
        res["random"] = pack(mr, acc, crit)
        central = new_agent(SEED); envs = make_client_envs(SEED); curve = []
        for rnd in range(ROUNDS):
            for e in envs: train_local(e, central)
            if (rnd + 1) % PROBE_EVERY == 0:
                curve.append(evaluate(central, steps=PROBE_STEPS)[0])
        mr, acc, crit = evaluate(central)
        res["central_ppo"] = pack(mr, acc, crit, curve)
        _save(CURVE_F, {"central_ppo": curve})
        _save(RES_F, res)
        print("base ->", {"random": res["random"], "central_ppo": res["central_ppo"]})
    elif stage in ("fedavg", "fedprox", "fedprox_dp"):
        run_fed(stage)
    elif stage == "finalize":
        res = _load(RES_F, {})
        if MODALITY_GROUPS:
            from itertools import combinations
            from math import factorial
            best = new_agent(0); best.set_params(_j2p(_load(OUT / "params_fedprox.json", {})))
            groups = list(MODALITY_GROUPS.items()); n = len(groups)
            def f(coal, state):
                s = np.zeros(STATE_DIM)
                for nm, idx in groups:
                    if nm in coal: s[idx] = state[idx]
                return best.policy(s)
            def shap(state):
                full = f(tuple(g[0] for g in groups), state); a = int(np.argmax(full)); phi = {}
                for nm, _ in groups:
                    others = [g[0] for g in groups if g[0] != nm]; val = 0.0
                    for k in range(n):
                        for S in combinations(others, k):
                            w = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                            val += w * (f(tuple(S) + (nm,), state)[a] - f(tuple(S), state)[a])
                    phi[nm] = val
                tot = sum(abs(v) for v in phi.values()) or 1.0
                return a, {m: round(100 * abs(v) / tot, 1) for m, v in phi.items()}
            envx = make_env(SEED + 902); agg_pct = {}
            for i in range(40):
                s = env_reset(envx, seed=1000 + i)
                a, pct = shap(s)
                agg_pct.setdefault(ACTION_LABELS[a], []).append(pct)
            res["xai"] = {"mean_pct_by_action": {
                act: {m: round(float(np.mean([p[m] for p in ps])), 1) for m in MODALITY_GROUPS}
                for act, ps in agg_pct.items()}}
            # karşıolgusal örnek
            rng = np.random.default_rng(7); cf = None
            for _ in range(500):
                s = env_reset(envx, seed=int(rng.integers(1e6)))
                a0 = int(np.argmax(best.policy(s)))
                if a0 == 0: continue
                for nm, idx in groups:
                    sc = s.copy(); sc[idx] = 0.0
                    a1 = int(np.argmax(best.policy(sc)))
                    if a1 != a0:
                        cf = {"modality_removed": nm, "original_action": ACTION_LABELS[a0],
                              "counterfactual_action": ACTION_LABELS[a1]}
                        break
                if cf: break
            res["xai"]["counterfactual"] = cf
        res["runtime_note"] = "staged runs, 11 Jun 2026"
        _save(RES_F, res)
        print("finalize ->", json.dumps(res.get("xai", {}), indent=1)[:400])
    print("süre:", round(time.time() - t0, 1), "sn")

if __name__ == "__main__":
    main(sys.argv[1])
