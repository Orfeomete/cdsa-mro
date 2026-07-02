"""Faz B / B1+B2 — bozulmus-girdi dayaniklilik + confusion matrix (egitimsiz).

Egitilmis FedProx/FedAvg global parametreleriyle, gozlem bozulmalari altinda
yeniden degerlendirme. Ortam ic durumu TEMIZ kalir; bozulma yalniz ajanin
gordugu gozleme uygulanir (sensor/link degradasyonu modeli).
Kosullar: clean · gauss(sigma=0.05/0.10/0.20) · drop(p=0.05/0.10, zero-fill)
· moddrop(tam modalite dususu, modalite gruplari varsa).
Cikti: results/faz_b_robustness.json + results/faz_b_confusion.json
Kullanim: python3 faz_b_robustness.py
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
from faz_a_config import (PILLAR, make_env, N_ACTIONS, STATE_DIM,
                          MODALITY_GROUPS, ACTION_LABELS, NEW_STEP_API,
                          INFO_TRUE_KEY, CRITICAL_ACTIONS)
from faz_a_staged import new_agent, env_reset, env_step, _load, _j2p, OUT

SEED = 42
EVAL_STEPS = 600
EVAL_REPS = 3          # farkli seed'le tekrar -> ortalama ± std
# paket/zaman-damgasi kaybi hangi bilesenlere uygulanir:
# ATM'de ATS loglari (makale metniyle birebir), digerlerinde tum gozlem
DROP_IDX = (np.asarray(MODALITY_GROUPS["ats"])
            if "ats" in MODALITY_GROUPS else np.arange(STATE_DIM))

def conditions():
    conds = [("clean", "none", None)]
    for s in (0.05, 0.10, 0.20):
        conds.append((f"gauss_{s:.2f}", "gauss", s))
    for p in (0.05, 0.10):
        conds.append((f"drop_{p:.2f}", "drop", p))
    for name in MODALITY_GROUPS:
        conds.append((f"moddrop_{name}", "moddrop", name))
    return conds

def perturb(s, kind, param, rng):
    s = np.asarray(s, dtype=float)
    if kind == "none":
        return s
    if kind == "gauss":
        return np.clip(s + rng.normal(0.0, param, s.shape), 0.0, 1.0)
    if kind == "drop":
        out = s.copy()
        mask = rng.random(DROP_IDX.size) < param
        out[DROP_IDX[mask]] = 0.0
        return out
    if kind == "moddrop":
        out = s.copy()
        out[np.asarray(MODALITY_GROUPS[param])] = 0.0
        return out
    raise ValueError(kind)

def eval_cond(agent, kind, param, rep):
    env = make_env(SEED + 900 + rep)
    s = env_reset(env, seed=2026 + rep) if NEW_STEP_API else env_reset(env)
    rng = np.random.default_rng(10_000 + rep)
    cm = np.zeros((N_ACTIONS, N_ACTIONS), dtype=int)   # [true, pred]
    tot = corr = known = ch = ct = 0
    for _ in range(EVAL_STEPS):
        obs = perturb(s, kind, param, rng)
        a = agent.act(obs, deterministic=True)[0]
        s2, r, done, info = env_step(env, int(a))
        tot += r
        if isinstance(info, dict) and INFO_TRUE_KEY in info:
            at = int(info[INFO_TRUE_KEY]); known += 1
            corr += int(a == at); cm[at, int(a)] += 1
            if at in CRITICAL_ACTIONS:
                ct += 1; ch += int(a == at)
        s = env_reset(env) if done else s2
    # turetilmis oranlar
    crit = sorted(CRITICAL_ACTIONS)
    ncrit = [i for i in range(N_ACTIONS) if i not in CRITICAL_ACTIONS]
    benign_n = cm[ncrit, :].sum()
    false_crit = cm[np.ix_(ncrit, crit)].sum()          # benign -> kritik uyari
    crit_n = cm[crit, :].sum()
    missed_crit = crit_n - cm[np.ix_(crit, crit)].sum() # kritik kacirildi (baska sinifa)
    return {"mean_reward": tot / EVAL_STEPS,
            "accuracy_pct": 100 * corr / known if known else None,
            "critical_recall": ch / ct if ct else None,
            "false_critical_rate": float(false_crit / benign_n) if benign_n else None,
            "missed_critical_rate": float(missed_crit / crit_n) if crit_n else None,
            "confusion": cm.tolist()}

def agg(reps):
    keys = ["mean_reward", "accuracy_pct", "critical_recall",
            "false_critical_rate", "missed_critical_rate"]
    out = {}
    for k in keys:
        vals = [r[k] for r in reps if r[k] is not None]
        out[k] = {"mean": round(float(np.mean(vals)), 3),
                  "std": round(float(np.std(vals)), 3)} if vals else None
    out["confusion_sum"] = np.sum([np.array(r["confusion"]) for r in reps], axis=0).tolist()
    return out

def main():
    t0 = time.time()
    res, conf = {"pillar": PILLAR, "date": "2026-07-02", "seed": SEED,
                 "eval_steps": EVAL_STEPS, "eval_reps": EVAL_REPS,
                 "drop_idx": DROP_IDX.tolist(),
                 "note": "B1+B2 inference-time robustness; egitilmis parametrelerle, "
                         "yeniden egitim YOK; bozulma yalniz gozleme uygulanir",
                 "action_labels": list(ACTION_LABELS), "models": {}}, {}
    for label in ("fedprox", "fedavg"):
        pf = OUT / f"params_{label}.json"
        if not pf.exists():
            continue
        ag_ = new_agent(0); ag_.set_params(_j2p(_load(pf, {})))
        res["models"][label] = {}
        conf[label] = {}
        for cname, kind, param in conditions():
            reps = [eval_cond(ag_, kind, param, rep) for rep in range(EVAL_REPS)]
            a = agg(reps)
            conf[label][cname] = a.pop("confusion_sum")
            res["models"][label][cname] = a
    (OUT / "faz_b_robustness.json").write_text(json.dumps(res, indent=1))
    (OUT / "faz_b_confusion.json").write_text(json.dumps(
        {"pillar": PILLAR, "action_labels": list(ACTION_LABELS),
         "layout": "[true][pred], EVAL_REPS toplami", "matrices": conf}, indent=1))
    print(PILLAR, "faz_b tamam,", round(time.time() - t0, 1), "sn")
    for m, conds in res["models"].items():
        for c, v in conds.items():
            print(f"  {m:8s} {c:14s} acc={v['accuracy_pct']['mean']:5.1f} "
                  f"critRec={v['critical_recall']['mean']:.3f} "
                  f"falseCrit={v['false_critical_rate']['mean']:.3f}")

if __name__ == "__main__":
    main()
