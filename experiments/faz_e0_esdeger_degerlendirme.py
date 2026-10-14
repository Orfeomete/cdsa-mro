"""Faz E0 — esdeger degerlendirme protokolu (1.800 karar).

Amac: Tez Tablo 12/13 ve makale Tablo 3/5/6 icin karsilastirilan butun
politikalari TEK bir degerlendirme protokolunde toplamak.

Protokol sozlesmesi (faz_b_robustness.py 'clean' kosulu ile birebir ayni):
  SEED = 42, EVAL_STEPS = 600, EVAL_REPS = 3  -> 3 x 600 = 1.800 karar
  rep r icin: env = make_env(SEED + 900 + r)
              baslangic gozlemi = env.reset(seed=2026 + r)  (NEW_STEP_API ise)
                                  env.reset()               (degilse)
  gozlem bozulmasi YOK ('clean'), karar deterministik (argmax).

Ortamlarin durum akisi eylemden bagimsiz uretildigi icin butun politikalar
ayni 1.800 gozlemi ayni sirada gorur; degerlendirme kumesi, tohum listesi ve
butce butun politikalarda ozdestir.

Degerlendirilenler:
  - results/params_*.json altindaki BUTUN kontrol noktalari
  - sabit politikalar: cogunluk sinifi, her kritik eylem icin hep-kritik
  - rastgele politika: ayni protokolde tohumlu simulasyon (analitik beklenti
    ayrica v11_protokol_hesap.py icinde kapali formulle hesaplanir)

Cikti: results/faz_e0_esdeger.json
  her politika icin  per_rep: 3 adet 600'luk [true][pred] matris
                     pooled : 1.800'luk toplam matris
  ayrica true_labels_per_rep (protokol ozdesligi denetimi icin)

Kullanim: python3 faz_e0_esdeger_degerlendirme.py
Not: mevcut hicbir dosya degistirilmez; bu betik yalniz degerlendirir.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from faz_a_config import (PILLAR, make_env, N_ACTIONS, STATE_DIM,
                          ACTION_LABELS, NEW_STEP_API, INFO_TRUE_KEY,
                          CRITICAL_ACTIONS)
from faz_a_staged import new_agent, env_reset, env_step, _load, _j2p, OUT

SEED = 42
EVAL_STEPS = 600
EVAL_REPS = 3
RANDOM_RNG_BASE = 10_000   # faz_b'deki bozulma rng tohumu ile ayni taban


def _policies():
    """Kontrol noktasi dosyalarini duzenli sirayla dondur."""
    tercih = ["params_fedavg.json", "params_fedprox.json",
              "params_fedprox_dp.json", "params_fedprox_dp_eps0_5.json",
              "params_fedprox_dp_eps2_0.json", "params_fedprox_dynrew.json",
              "params_fedprox_ent0_01.json", "params_fedprox_ent0_05.json",
              "params_fedprox_gatedent.json", "params_fedprox_decoy.json"]
    var = sorted(p.name for p in OUT.glob("params_*.json"))
    sirali = [n for n in tercih if n in var] + [n for n in var if n not in tercih]
    return [(n[len("params_"):-len(".json")], OUT / n) for n in sirali]


def _run_rep(rep, decide):
    """Tek tekrar: 600 karar. decide(obs) -> eylem. Dondurur: (cm, true_seq)."""
    env = make_env(SEED + 900 + rep)
    s = env_reset(env, seed=2026 + rep) if NEW_STEP_API else env_reset(env)
    cm = np.zeros((N_ACTIONS, N_ACTIONS), dtype=int)   # [true, pred]
    true_seq = []
    tot = 0.0
    for _ in range(EVAL_STEPS):
        a = int(decide(s))
        s2, r, done, info = env_step(env, a)
        tot += r
        if isinstance(info, dict) and INFO_TRUE_KEY in info:
            at = int(info[INFO_TRUE_KEY])
            cm[at, a] += 1
            true_seq.append(at)
        s = env_reset(env) if done else s2
    return cm, true_seq, tot / EVAL_STEPS


def _eval_policy(decide_factory):
    """decide_factory(rep) -> decide. Dondurur: politika kaydi."""
    per_rep, true_reps, rewards = [], [], []
    for rep in range(EVAL_REPS):
        cm, tseq, mr = _run_rep(rep, decide_factory(rep))
        per_rep.append(cm)
        true_reps.append(tseq)
        rewards.append(mr)
    pooled = np.sum(per_rep, axis=0)
    return {"per_rep": [m.tolist() for m in per_rep],
            "pooled": pooled.tolist(),
            "mean_reward_per_rep": [round(float(x), 4) for x in rewards]}, true_reps


def main():
    t0 = time.time()
    out = {"pillar": PILLAR,
           "protocol": {"name": "1800-karar esdeger degerlendirme",
                        "seed": SEED, "eval_steps": EVAL_STEPS,
                        "eval_reps": EVAL_REPS,
                        "total_decisions": EVAL_STEPS * EVAL_REPS,
                        "env_seeds": [SEED + 900 + r for r in range(EVAL_REPS)],
                        "reset_seeds": ([2026 + r for r in range(EVAL_REPS)]
                                        if NEW_STEP_API else None),
                        "condition": "clean (gozlem bozulmasi yok)",
                        "decision_rule": "deterministik argmax",
                        "source_contract": "faz_b_robustness.py clean kosulu"},
           "n_actions": N_ACTIONS, "state_dim": STATE_DIM,
           "action_labels": list(ACTION_LABELS),
           "critical_actions": sorted(CRITICAL_ACTIONS),
           "layout": "[true][pred]",
           "policies": {}}

    ref_true = None
    out["skipped"] = {}

    # 1) ogrenilmis kontrol noktalari
    for label, pf in _policies():
        raw = _j2p(_load(pf, {}))
        w1 = np.asarray(raw.get("W1"))
        if w1.ndim != 2 or w1.shape[1] != STATE_DIM:
            # farkli gozlem uzayinda egitilmis kontrol noktasi (or. decoy
            # kanali eklenmis gozlem) — bu protokolde degerlendirilemez
            out["skipped"][label] = {
                "reason": "gozlem boyutu uyusmuyor",
                "checkpoint_state_dim": int(w1.shape[1]) if w1.ndim == 2 else None,
                "protocol_state_dim": STATE_DIM, "source": pf.name}
            continue
        ag = new_agent(0)
        ag.set_params(raw)
        rec, tr = _eval_policy(lambda rep, ag=ag: (lambda s: ag.act(s, deterministic=True)[0]))
        rec["kind"] = "checkpoint"
        rec["source"] = pf.name
        out["policies"][label] = rec
        if ref_true is None:
            ref_true = tr
            out["true_labels_per_rep"] = tr
        rec["eval_set_identical"] = bool(tr == ref_true)

    # 2) sabit politikalar — cogunluk sinifi (havuzlanmis gercek etikete gore)
    if ref_true is not None:
        flat = [x for seq in ref_true for x in seq]
        counts = np.bincount(flat, minlength=N_ACTIONS)
        majority = int(np.argmax(counts))
        out["true_label_counts_pooled"] = counts.tolist()
        rec, tr = _eval_policy(lambda rep, m=majority: (lambda s: m))
        rec.update({"kind": "fixed", "constant_action": majority,
                    "eval_set_identical": bool(tr == ref_true)})
        out["policies"][f"sabit_cogunluk_a{majority}"] = rec

        # 3) hep-kritik (her kritik eylem icin ayri)
        for c in sorted(CRITICAL_ACTIONS):
            rec, tr = _eval_policy(lambda rep, c=c: (lambda s: c))
            rec.update({"kind": "fixed", "constant_action": int(c),
                        "eval_set_identical": bool(tr == ref_true)})
            out["policies"][f"sabit_hep_kritik_a{c}"] = rec

        # 4) rastgele — ayni protokolde tohumlu simulasyon
        def rnd_factory(rep):
            rng = np.random.default_rng(RANDOM_RNG_BASE + rep)
            return lambda s: int(rng.integers(N_ACTIONS))
        rec, tr = _eval_policy(rnd_factory)
        rec.update({"kind": "simulated_random",
                    "rng_seeds": [RANDOM_RNG_BASE + r for r in range(EVAL_REPS)],
                    "eval_set_identical": bool(tr == ref_true)})
        out["policies"]["rastgele_simule"] = rec

    # 5) faz_b_confusion.json 'clean' matrisleriyle regresyon denetimi
    cf = OUT / "faz_b_confusion.json"
    reg = {}
    if cf.exists():
        mats = json.loads(cf.read_text()).get("matrices", {})
        for m, conds in mats.items():
            if "clean" in conds and m in out["policies"]:
                reg[m] = {"faz_b_clean": conds["clean"],
                          "e0_pooled": out["policies"][m]["pooled"],
                          "match": conds["clean"] == out["policies"][m]["pooled"]}
    out["regression_vs_faz_b_confusion"] = reg

    (OUT / "faz_e0_esdeger.json").write_text(json.dumps(out, indent=1))
    print(PILLAR, "faz_e0 tamam,", round(time.time() - t0, 1), "sn")
    for m, v in reg.items():
        print(f"  regresyon {m}: {'ESLESTI' if v['match'] else 'ESLESMEDI'}")
    for k, v in out["policies"].items():
        p = np.array(v["pooled"])
        n = p.sum()
        acc = 100 * np.trace(p) / n if n else float("nan")
        print(f"  {k:26s} n={n} acc={acc:5.2f}")


if __name__ == "__main__":
    main()
