#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Faz E10 (cok-tohum) ve E11 (Tablo 9 / Tablo 10) kosucusu.

On kayit: FAZ_E10_E11_ON_KAYIT_09092026.md (kosudan ONCE donduruldu).

Depodaki ortam kodu, ajan kodu, federe agregasyon kodu ve degerlendirme
sozlesmesi DEGISTIRILMEZ; buradan yalniz cagrilir.

Kullanim:
  python3 e10_e11_kosu.py <damar> <kol> <tohum>
    damar: mro | bb3 | atm
    kol  : fedavg | fedprox | central | tekmod:<grup>
    tohum: tam sayi
Cikti: cikti/<damar>_<kol>_<tohum>.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

KOK = Path('/home/claude/kosu')
CIKTI = KOK / 'cikti'
CIKTI.mkdir(exist_ok=True)


def yukle(damar):
    """Damarin config + staged modullerini yalitilmis sekilde yukler."""
    for m in list(sys.modules):
        if m in ('faz_a_config', 'faz_a_staged') or m.startswith('src'):
            del sys.modules[m]
    d = KOK / damar
    for p in (str(d), str(d / 'experiments')):
        while p in sys.path:
            sys.path.remove(p)
        sys.path.insert(0, p)
    import faz_a_config as C
    import faz_a_staged as S
    return C, S


# ---- makro-F1: depodaki tanimin birebir kopyasi (faz_e_kayit.makro_f1) ----
def makro_f1(cm):
    cm = np.asarray(cm, dtype=float)
    k = cm.shape[0]
    f1 = np.zeros(k); kes = np.zeros(k); duy = np.zeros(k)
    for c in range(k):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        kes[c] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        duy[c] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1[c] = (2 * kes[c] * duy[c] / (kes[c] + duy[c])
                 if (kes[c] + duy[c]) > 0 else 0.0)
    return {'sinif_f1': [round(float(x), 4) for x in f1],
            'makro_f1': round(float(f1.mean()), 4),
            'dogruluk': round(float(np.trace(cm) / cm.sum()), 4) if cm.sum() else None}


# ---- E0 degerlendirme sozlesmesi: 3 x 600, tohumlar sabit ----
EVAL_STEPS, EVAL_REPS, EVAL_SEED = 600, 3, 42


def degerlendir(C, S, karar, maske=None):
    """karar(s) -> eylem. maske verilirse gozlem maskelenir (tek-modlu kol).

    Dondurur: (pooled_cm, ort_odul, true_seq_listesi)
    """
    cm = np.zeros((C.N_ACTIONS, C.N_ACTIONS), dtype=int)
    oduller, true_reps = [], []
    for rep in range(EVAL_REPS):
        env = C.make_env(EVAL_SEED + 900 + rep)
        s = (S.env_reset(env, seed=2026 + rep) if C.NEW_STEP_API
             else S.env_reset(env))
        tot = 0.0
        tseq = []
        for _ in range(EVAL_STEPS):
            obs = s if maske is None else s * maske
            a = int(karar(obs))
            s2, r, done, info = S.env_step(env, a)
            tot += r
            if isinstance(info, dict) and C.INFO_TRUE_KEY in info:
                at = int(info[C.INFO_TRUE_KEY])
                cm[at, a] += 1
                tseq.append(at)
            s = S.env_reset(env) if done else s2
        oduller.append(tot / EVAL_STEPS)
        true_reps.append(tseq)
    return cm, float(np.mean(oduller)), true_reps


def egit_federe(C, S, tohum, tur_sayisi, prox, maske=None):
    """Parcasiz (tek seferde) federe egitim. Depodaki run_fed ile ayni akis,
    ancak checkpoint yok -> istemci RNG durumu sifirlanmaz."""
    from src.federated.fedavg import FedAvgAggregator
    from src.federated.fedprox import FedProxAggregator
    agg = (FedProxAggregator(mu=0.01, seed=tohum) if prox
           else FedAvgAggregator(seed=tohum))
    envs = C.make_client_envs(tohum)
    cl = [S.new_agent(tohum + i) for i in range(len(envs))]
    g = cl[0].params()
    for _ in range(tur_sayisi):
        for c in cl:
            c.set_params(g)
        for e, c in zip(envs, cl):
            egit_yerel(S, e, c, maske)
            if prox:
                c.set_params(agg.apply_proximal_step(c.params(), g, lr=1.0))
        g = agg.aggregate([c.params() for c in cl])
    return g


def egit_yerel(S, env, ag, maske):
    """S.train_local'in maskeli hali; maske yoksa birebir ayni akis."""
    for _ in range(S.LOCAL_ROLLOUTS):
        s = S.env_reset(env)
        SS, A, LP, R, V, D = [], [], [], [], [], []
        for _ in range(S.ROLLOUT_LEN):
            obs = s if maske is None else s * maske
            a, lp, v = ag.act(obs)
            s2, r, done, _ = S.env_step(env, a)
            SS.append(obs); A.append(a); LP.append(lp)
            R.append(r); V.append(v); D.append(done)
            s = S.env_reset(env) if done else s2
        adv, ret = ag.compute_gae(R, V, D)
        ag.update(SS, A, LP, adv, ret, epochs=2)


def egit_merkezi(C, S, tohum, tur_sayisi, maske=None):
    """faz_a_staged.main('base') icindeki central_ppo akisiyla ayni."""
    ag = S.new_agent(tohum)
    envs = C.make_client_envs(tohum)
    for _ in range(tur_sayisi):
        for e in envs:
            egit_yerel(S, e, ag, maske)
    return ag.params()


def main():
    damar, kol, tohum = sys.argv[1], sys.argv[2], int(sys.argv[3])
    hedef = CIKTI / f'{damar}_{kol.replace(":", "_")}_{tohum}.json'
    if hedef.exists():
        print('ATLANDI (var):', hedef.name)
        return
    t0 = time.time()
    C, S = yukle(damar)

    maske = None
    grup = None
    if kol.startswith('tekmod:'):
        grup = kol.split(':', 1)[1]
        if grup not in C.MODALITY_GROUPS:
            raise SystemExit(f'{damar}: {grup} modalite grubu yok')
        maske = np.zeros(C.STATE_DIM)
        maske[C.MODALITY_GROUPS[grup]] = 1.0

    if kol == 'central':
        g = egit_merkezi(C, S, tohum, S.ROUNDS)          # 100 tur
        tur = S.ROUNDS
    elif kol == 'fedavg':
        g = egit_federe(C, S, tohum, S.ROUNDS_FED, prox=False)
        tur = S.ROUNDS_FED
    elif kol in ('fedprox',) or kol.startswith('tekmod:'):
        g = egit_federe(C, S, tohum, S.ROUNDS_FED, prox=True, maske=maske)
        tur = S.ROUNDS_FED
    else:
        raise SystemExit('bilinmeyen kol: ' + kol)

    ajan = S.new_agent(0)
    ajan.set_params(g)
    cm, odul, true_reps = degerlendir(
        C, S, lambda s: ajan.act(s, deterministic=True)[0], maske=maske)
    m = makro_f1(cm)
    kayit = {'damar': C.PILLAR, 'kol': kol, 'tohum': tohum,
             'egitim_turu': tur, 'maske_grubu': grup,
             'pooled_cm': cm.tolist(), 'ortalama_odul': round(odul, 4),
             'toplam_karar': int(cm.sum()),
             'protokol': {'eval_steps': EVAL_STEPS, 'eval_reps': EVAL_REPS,
                          'env_seeds': [EVAL_SEED + 900 + r for r in range(EVAL_REPS)],
                          'reset_seeds': ([2026 + r for r in range(EVAL_REPS)]
                                          if C.NEW_STEP_API else None),
                          'karar_kurali': 'deterministik argmax',
                          'maskeleme': ('degerlendirmede de uygulandi'
                                        if maske is not None else 'yok')},
             'sure_sn': round(time.time() - t0, 1)}
    kayit.update(m)
    hedef.write_text(json.dumps(kayit, indent=1), encoding='utf-8')
    print(f'{damar:4s} {kol:18s} tohum {tohum:3d} | makro-F1 {m["makro_f1"]:.4f} '
          f'| dogruluk {m["dogruluk"]:.4f} | odul {odul:7.2f} '
          f'| {kayit["sure_sn"]:.0f} sn')


if __name__ == '__main__':
    main()
