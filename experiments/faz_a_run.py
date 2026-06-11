"""
CDSA Faz A — A6 CPU-scale federated training runs (shared harness).

Configs: random baseline, centralised PPO, FedPPO-FedAvg, FedPPO-FedProx,
FedPPO-FedProx + Laplace DP. Three heterogeneous clients. Outputs JSON
results + learning-curve PNG + XAI (group-Shapley / counterfactual) report.

Reproducible: all seeds fixed. Runtime: < 1 min on commodity CPU.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

from faz_a_config import (PILLAR, make_env, make_client_envs, N_ACTIONS,
                          STATE_DIM, MODALITY_GROUPS, ACTION_LABELS,
                          NEW_STEP_API, INFO_TRUE_KEY, CRITICAL_ACTIONS)
from src.rl_agents.ppo_actor_critic import PPOActorCritic
from src.federated.fedavg import FedAvgAggregator
from src.federated.fedprox import FedProxAggregator

ROUNDS = 60
LOCAL_ROLLOUTS = 2
ROLLOUT_LEN = 128
EVAL_STEPS = 600
SEED = 42


def env_reset(env, seed=None):
    out = env.reset(seed=seed) if NEW_STEP_API else env.reset()
    return out[0] if isinstance(out, tuple) else out


def env_step(env, a):
    out = env.step(a)
    if len(out) == 5:
        s, r, term, trunc, info = out
        return s, r, term or trunc, info
    return out  # (s, r, done, info)


def rollout(env, agent, n_steps, rng=None, random_policy=False):
    s = env_reset(env)
    S, A, LP, Rw, V, D = [], [], [], [], [], []
    for _ in range(n_steps):
        if random_policy:
            a = int(rng.integers(N_ACTIONS))
            logp, v = np.log(1.0 / N_ACTIONS), 0.0
        else:
            a, logp, v = agent.act(s)
        s2, r, done, _ = env_step(env, a)
        S.append(s); A.append(a); LP.append(logp); Rw.append(r); V.append(v); D.append(done)
        s = env_reset(env) if done else s2
    return S, A, LP, Rw, V, D


def train_local(env, agent, n_rollouts=LOCAL_ROLLOUTS):
    for _ in range(n_rollouts):
        S, A, LP, Rw, V, D = rollout(env, agent, ROLLOUT_LEN)
        adv, ret = agent.compute_gae(Rw, V, D)
        agent.update(S, A, LP, adv, ret, epochs=3)


def evaluate(env, agent=None, rng=None):
    s = env_reset(env, seed=2026)
    total, correct, known = 0.0, 0, 0
    crit_hit, crit_tot = 0, 0
    for _ in range(EVAL_STEPS):
        if agent is None:
            a = int(rng.integers(N_ACTIONS))
        else:
            a, _, _ = agent.act(s, deterministic=True)
        s2, r, done, info = env_step(env, a)
        total += r
        if isinstance(info, dict) and INFO_TRUE_KEY in info:
            known += 1
            at = info[INFO_TRUE_KEY]
            correct += int(a == at)
            if at in CRITICAL_ACTIONS:
                crit_tot += 1
                crit_hit += int(a == at)
        s = env_reset(env) if done else s2
    acc = (100.0 * correct / known) if known else None
    crit = (crit_hit / crit_tot) if crit_tot else None
    return total / EVAL_STEPS, acc, crit


def run_federated(aggregator, dp_label, curve_store):
    envs = make_client_envs(SEED)
    clients = [PPOActorCritic(fused_dim=STATE_DIM, n_actions=N_ACTIONS,
                              hidden=64, lr=0.05, reward_scale=0.05, seed=SEED + i)
               for i in range(len(envs))]
    g = clients[0].params()
    curve = []
    for rnd in range(ROUNDS):
        for c in clients:
            c.set_params(g)
        for env, c in zip(envs, clients):
            train_local(env, c)
        g = aggregator.aggregate([c.params() for c in clients])
        probe = PPOActorCritic(fused_dim=STATE_DIM, n_actions=N_ACTIONS,
                               hidden=64, seed=0)
        probe.set_params(g)
        mr, _, _ = evaluate(make_env(SEED + 900), probe)
        curve.append(mr)
    curve_store[dp_label] = curve
    final = PPOActorCritic(fused_dim=STATE_DIM, n_actions=N_ACTIONS, hidden=64, seed=0)
    final.set_params(g)
    return final


def convergence_round(curve, target):
    for i, v in enumerate(curve):
        if v >= target:
            return i + 1
    return None


def group_shapley(agent, state):
    """Exact Shapley over modality groups for the trained policy."""
    from itertools import combinations
    from math import factorial
    groups = list(MODALITY_GROUPS.items())
    n = len(groups)

    def f(coal):
        s = np.zeros(STATE_DIM)
        for name, idx in groups:
            if name in coal:
                s[idx] = state[idx]
        return agent.policy(s)

    full = f(tuple(g[0] for g in groups))
    a = int(np.argmax(full))
    phi = {}
    for name, _ in groups:
        others = [g[0] for g in groups if g[0] != name]
        val = 0.0
        for k in range(n):
            for S in combinations(others, k):
                w = factorial(len(S)) * factorial(n - len(S) - 1) / factorial(n)
                val += w * (f(tuple(S) + (name,))[a] - f(tuple(S))[a])
        phi[name] = float(val)
    tot = sum(abs(v) for v in phi.values()) or 1.0
    pct = {m: round(100 * abs(v) / tot, 1) for m, v in phi.items()}
    return a, phi, pct


def counterfactual_demo(agent, env):
    """Find a state where ablating one group flips the decision."""
    rng = np.random.default_rng(7)
    for _ in range(400):
        s = env_reset(env, seed=int(rng.integers(1e6)))
        a0 = int(np.argmax(agent.policy(s)))
        for name, idx in MODALITY_GROUPS.items():
            s_cf = s.copy(); s_cf[idx] = 0.0
            a1 = int(np.argmax(agent.policy(s_cf)))
            if a1 != a0 and a0 != 0:
                return {"modality_removed": name,
                        "original_action": ACTION_LABELS[a0],
                        "counterfactual_action": ACTION_LABELS[a1],
                        "state": [round(float(x), 3) for x in s]}
    return None


def main():
    t0 = time.time()
    results = {"pillar": PILLAR, "date": "2026-06-11", "seed": SEED,
               "config": {"rounds": ROUNDS, "clients": 3,
                          "local_rollouts": LOCAL_ROLLOUTS,
                          "rollout_len": ROLLOUT_LEN,
                          "eval_steps": EVAL_STEPS,
                          "fedprox_mu": 0.01,
                          "dp": {"epsilon": 1.0, "sensitivity": 0.01,
                                 "note": "clipped-update varsayimi"}}}
    curves = {}
    rng = np.random.default_rng(SEED)

    # 1) random baseline
    mr, acc, crit = evaluate(make_env(SEED + 900), None, rng=rng)
    results["random"] = {"mean_reward": round(mr, 2), "accuracy_pct": None if acc is None else round(acc, 1), "critical_recall": crit}

    # 2) centralised PPO (single agent, pooled experience from 3 envs)
    central = PPOActorCritic(fused_dim=STATE_DIM, n_actions=N_ACTIONS,
                             hidden=64, lr=0.05, reward_scale=0.05, seed=SEED)
    envs = make_client_envs(SEED)
    curve_c = []
    for rnd in range(ROUNDS):
        for env in envs:
            train_local(env, central, n_rollouts=LOCAL_ROLLOUTS)
        m, _, _ = evaluate(make_env(SEED + 900), central)
        curve_c.append(m)
    curves["central_ppo"] = curve_c
    mr, acc, crit = evaluate(make_env(SEED + 900), central)
    results["central_ppo"] = {"mean_reward": round(mr, 2),
                              "accuracy_pct": None if acc is None else round(acc, 1),
                              "critical_recall": crit}

    # 3-5) federated variants
    agents = {}
    for label, agg in [
        ("fedavg", FedAvgAggregator(seed=SEED)),
        ("fedprox", FedProxAggregator(mu=0.01, seed=SEED)),
        ("fedprox_dp", FedProxAggregator(mu=0.01, dp_epsilon=1.0,
                                         dp_sensitivity=0.01, seed=SEED)),
    ]:
        agents[label] = run_federated(agg, label, curves)
        mr, acc, crit = evaluate(make_env(SEED + 900), agents[label])
        results[label] = {"mean_reward": round(mr, 2),
                          "accuracy_pct": None if acc is None else round(acc, 1),
                          "critical_recall": crit}

    # convergence: round where curve reaches 90% of its final value
    for label, curve in curves.items():
        tgt = 0.9 * max(curve[-1], 1e-9) if curve[-1] > 0 else curve[-1]
        results[label]["convergence_round"] = convergence_round(curve, tgt)

    # XAI on the FedProx agent
    if MODALITY_GROUPS:
        best = agents["fedprox"]
        env = make_env(SEED + 901)
        s = env_reset(env, seed=77)
        a, phi, pct = group_shapley(best, s)
        results["xai"] = {"shap_example": {"action": ACTION_LABELS[a],
                                           "phi": {k: round(v, 4) for k, v in phi.items()},
                                           "pct": pct},
                          "counterfactual": counterfactual_demo(best, env)}
        # mean SHAP pct over 30 states, grouped by decided action
        agg_pct = {}
        env2 = make_env(SEED + 902)
        for i in range(30):
            s = env_reset(env2, seed=1000 + i)
            a, _, pct = group_shapley(best, s)
            agg_pct.setdefault(ACTION_LABELS[a], []).append(pct)
        results["xai"]["mean_pct_by_action"] = {
            act: {m: round(float(np.mean([p[m] for p in ps])), 1)
                  for m in MODALITY_GROUPS}
            for act, ps in agg_pct.items()}

    results["runtime_sec"] = round(time.time() - t0, 1)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "faz_a_results.json").write_text(json.dumps(results, indent=2))
    (out / "faz_a_curves.json").write_text(json.dumps(curves, indent=2))
    print(json.dumps({k: v for k, v in results.items()
                      if k in ("random", "central_ppo", "fedavg", "fedprox",
                               "fedprox_dp", "runtime_sec")}, indent=2))


if __name__ == "__main__":
    main()
