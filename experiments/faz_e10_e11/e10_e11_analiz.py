#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E10/E11 analizi. On kayit: FAZ_E10_E11_ON_KAYIT_09092026.md (kosudan once).

Karar kurallari E10.1, E10.2, E10.3, E11a.1, E11b.1 oradan aynen uygulanir.
"""
import glob
import json
from collections import defaultdict

import numpy as np

TOHUMLAR = list(range(42, 52))
T95 = 2.262157  # t(0.975, sd=9)


def ga(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    m = x.mean()
    s = x.std(ddof=1)
    h = T95 * s / np.sqrt(n)
    return m, s, m - h, m + h


kayit = defaultdict(dict)
for f in glob.glob('cikti/*.json'):
    d = json.load(open(f, encoding='utf-8'))
    if d['tohum'] not in TOHUMLAR:
        continue            # tohum 999 muhendislik denemesi, analize girmez
    kayit[(d['damar'], d['kol'])][d['tohum']] = d

print('=' * 78)
print('E10 — COK-TOHUM (n=10, tohumlar 42-51)')
print('=' * 78)
ozet = {}
for damar in ('CDSA-MRO', 'CDSA-BB3', 'CDSA-ATM'):
    print(f'\n--- {damar} ---')
    for kol in ('fedavg', 'fedprox', 'central'):
        r = kayit.get((damar, kol))
        if not r or len(r) != 10:
            print(f'  {kol}: eksik ({len(r) if r else 0}/10)')
            continue
        v = [r[t]['makro_f1'] for t in TOHUMLAR]
        m, s, lo, hi = ga(v)
        ozet[(damar, kol)] = dict(deger=v, ort=m, sd=s, alt=lo, ust=hi)
        d42 = r[42]['makro_f1']
        disarida = not (lo <= d42 <= hi)
        # dejenere kosu sayisi: tek eylemde toplanmis tahmin
        dej = sum(1 for t in TOHUMLAR
                  if (np.array(r[t]['pooled_cm']).sum(axis=0) > 0).sum() == 1)
        print(f'  {kol:8s} ort {m:.4f}  sd {s:.4f}  GA[{lo:.4f}, {hi:.4f}]  '
              f'min {min(v):.4f} maks {max(v):.4f}  '
              f'tohum42 {d42:.4f}{"  <-- GA DISINDA" if disarida else ""}  '
              f'dejenere {dej}/10')

print('\n' + '=' * 78)
print('E10.1 — TEK TOHUMUN TEMSIL GUCU')
print('=' * 78)
for (damar, kol), o in ozet.items():
    d42 = kayit[(damar, kol)][42]['makro_f1']
    if not (o['alt'] <= d42 <= o['ust']):
        print(f'  {damar} {kol}: tohum 42 = {d42:.4f}, GA = '
              f'[{o["alt"]:.4f}, {o["ust"]:.4f}] -> DISINDA')

print('\n' + '=' * 78)
print('E10.3 — DEGISKENLIGIN BUYUKLUGU')
print('=' * 78)
for damar in ('CDSA-MRO', 'CDSA-BB3', 'CDSA-ATM'):
    kols = [(k, ozet[(damar, k)]) for k in ('fedavg', 'fedprox', 'central')
            if (damar, k) in ozet]
    if len(kols) < 2:
        continue
    ortalamalar = [o['ort'] for _, o in kols]
    kol_farki = max(ortalamalar) - min(ortalamalar)
    en_buyuk_sd = max(o['sd'] for _, o in kols)
    print(f'  {damar}: kollar arasi en buyuk fark {kol_farki:.4f} | '
          f'en buyuk tohum sd {en_buyuk_sd:.4f} -> '
          f'{"SD BUYUK: kollar tek tohumla ayrilamaz" if en_buyuk_sd > kol_farki else "fark sd den buyuk"}')

print('\n' + '=' * 78)
print('E11a.1 — TABLO 10: MERKEZI <-> BIRLESIK')
print('=' * 78)
print('  NOT: merkezi 100 tur, federe 160 tur — butceler esit DEGIL.')
for damar in ('CDSA-MRO', 'CDSA-BB3', 'CDSA-ATM'):
    if (damar, 'central') not in ozet or (damar, 'fedprox') not in ozet:
        continue
    c, f = ozet[(damar, 'central')], ozet[(damar, 'fedprox')]
    ortusme = not (c['ust'] < f['alt'] or f['ust'] < c['alt'])
    if ortusme:
        h = 'GA ORTUSUYOR -> bu kurguda ve bu butcede fark olculemedi'
    elif f['ort'] < c['ort']:
        h = f'birlesik ALTTA -> veri yerelliginin bedeli {c["ort"]-f["ort"]:.4f}'
    else:
        h = (f'birlesik USTTE ({f["ort"]-c["ort"]:.4f}) -> butce esitsizligi '
             f'(160/100) nedeniyle ustunluk kaniti sayilamaz')
    print(f'  {damar}: merkezi {c["ort"]:.4f} GA[{c["alt"]:.4f},{c["ust"]:.4f}] | '
          f'birlesik {f["ort"]:.4f} GA[{f["alt"]:.4f},{f["ust"]:.4f}]')
    print(f'      -> {h}')

print('\n' + '=' * 78)
print('E11b.1 — TABLO 9: COK-MODLU <-> TEK-MODLU')
print('=' * 78)
GRUPLAR = {'CDSA-BB3': ('ppg', 'ecg', 'eeg'),
           'CDSA-ATM': ('trajectory', 'ats', 'coord')}
for damar, gruplar in GRUPLAR.items():
    cok = ozet.get((damar, 'fedprox'))
    if not cok:
        continue
    print(f'\n  {damar}')
    print(f'    cok-modlu (fedprox, tam gozlem): {cok["ort"]:.4f} '
          f'GA[{cok["alt"]:.4f}, {cok["ust"]:.4f}]  sd {cok["sd"]:.4f}')
    en_iyi = None
    for g in gruplar:
        r = kayit.get((damar, f'tekmod:{g}'))
        if not r or len(r) != 10:
            print(f'    tekmod:{g}: eksik')
            continue
        v = [r[t]['makro_f1'] for t in TOHUMLAR]
        m, s, lo, hi = ga(v)
        ozet[(damar, f'tekmod:{g}')] = dict(deger=v, ort=m, sd=s, alt=lo, ust=hi)
        print(f'    tek-modlu {g:11s}: {m:.4f} GA[{lo:.4f}, {hi:.4f}]  sd {s:.4f}')
        if en_iyi is None or m > en_iyi[1]:
            en_iyi = (g, m, lo, hi)
    g, m, lo, hi = en_iyi
    ortusme = not (cok['ust'] < lo or hi < cok['alt'])
    if ortusme:
        h = ('GA ORTUSUYOR -> cok-modlu fuzyonun kazanci bu damarda '
             'GOSTERILEMEDI')
    elif m > cok['ort']:
        h = (f'EN IYI TEK-MODLU ({g}) COK-MODLUYU GECIYOR ({m-cok["ort"]:+.4f}) '
             f'-> kazanc yok, TERSI yonde fark var')
    else:
        h = f'cok-modlu ustte ({cok["ort"]-m:+.4f}) -> kazanc gosterildi'
    print(f'    en iyi tek-modlu: {g} ({m:.4f})')
    print(f'    -> {h}')
print('\n  CDSA-MRO: TANIMSIZ — gorev tek-modlu (MODALITY_GROUPS bos, '
      'faz_a_config.py). Kol imal edilmedi.')

print('\n' + '=' * 78)
print('E10.2 — SABIT POLITIKA KARSILASTIRICISI (mevcut faz_e0 kaydindan)')
print('=' * 78)
YOL = {'CDSA-MRO': 'mro', 'CDSA-BB3': 'bb3', 'CDSA-ATM': 'atm'}


def makro(cm):
    cm = np.asarray(cm, float)
    k = cm.shape[0]
    f1 = np.zeros(k)
    for c in range(k):
        tp = cm[c, c]
        p = tp / cm[:, c].sum() if cm[:, c].sum() else 0.0
        d = tp / cm[c, :].sum() if cm[c, :].sum() else 0.0
        f1[c] = 2 * p * d / (p + d) if (p + d) else 0.0
    return float(f1.mean())


for damar, kisa in YOL.items():
    try:
        e0 = json.load(open(f'{kisa}/experiments/results/faz_e0_esdeger.json'))
    except FileNotFoundError:
        print(f'  {damar}: faz_e0 kaydi yok, atlandi')
        continue
    sabit = {k: makro(v['pooled']) for k, v in e0['policies'].items()
             if v.get('kind') in ('fixed', 'simulated_random')}
    if not sabit:
        continue
    en_iyi_ad = max(sabit, key=sabit.get)
    en_iyi = sabit[en_iyi_ad]
    o = ozet.get((damar, 'fedprox'))
    if not o:
        continue
    icinde = o['alt'] <= en_iyi <= o['ust']
    altinda = o['ust'] < en_iyi
    if altinda:
        h = 'SABIT POLITIKA OGRENILMISIN GA UST SINIRINDAN DA YUKSEK'
    elif icinde:
        h = 'GA sabit politikayi ICERIYOR -> gectigi iddia edilemez'
    else:
        h = 'ogrenilmis politika sabit politikanin uzerinde'
    print(f'  {damar}: en iyi sabit "{en_iyi_ad}" = {en_iyi:.4f} | '
          f'fedprox GA[{o["alt"]:.4f}, {o["ust"]:.4f}] -> {h}')

json.dump({f'{d}|{k}': {kk: (vv.tolist() if hasattr(vv, 'tolist') else vv)
                        for kk, vv in o.items()}
           for (d, k), o in ozet.items()},
          open('e10_e11_ozet.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\nozet -> e10_e11_ozet.json')
