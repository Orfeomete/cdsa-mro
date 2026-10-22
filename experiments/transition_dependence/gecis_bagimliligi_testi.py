#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gecis fonksiyonu eylem bagimliligi testi — A makalesi icin arac.

A makalesinin merkezi bulgusu su: yayimlanmis uc ortamda sonraki durum,
ajanin sectigi eylemden bagimsiz cekilmektedir, yani P(s' | s, a) = P(s').
Bu bulgu su ana kadar ORTAM KODU OKUNARAK ileri surulmustu. Bu betik onu
OLCUME cevirir.

NEDEN YENI VERI GEREKMIYOR. Ortamlar kendi verilerini kendileri uretir.
Test ortami kosturur, dis bir veri kumesi istemez.

IKI AYRI SORU, IKI AYRI SINAMA

  S1  UYGULAMA DUZEYI. Sonraki durumu hesaplayan kod eylemi OKUYOR mu?
      Ayni rastgele akis paylasildiginda, eylem okunmuyorsa butun eylemler
      BIT DUZEYINDE AYNI sonraki durumu vermek zorundadir. Tek bir bit
      farki, kodun eylemi okudugunu gosterir.
      Bu sinama uygulamayi sinar, dagilimi sinamaz.

  S2  DAGILIM DUZEYI. Makalenin savi budur. Bagimsiz akislarla her eylem
      icin M sonraki durum ornekleyip, durum vektorunun her boyutu icin
      eylemler arasi dagilim karsilastirilir (Kruskal-Wallis, nominal
      anlamlilik 0,01, boyut sayisina gore Bonferroni).

DENETIMLER ZORUNLU. Iki referans ortam kurulur:
  NegatifDenetim  sonraki durum eylemden bagimsiz  -> gecmeli
  PozitifDenetim  sonraki durum eyleme gore kayar  -> gecmemeli
Pozitif denetim kaymayi saptamazsa test kordur ve hicbir sonuc raporlanmaz.
Kayma buyuklugu taranarak testin DUYARLILIGI da olculur, boylece okur
"bu test ne kadarlik bir etkiyi yakalar" sorusunun yanitini bilir.

Bu bir on kayitli deney DEGILDIR. Var olan bir savi denetlenebilir kilan bir
olcumdur ve makalede boyle sunulur.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

UP = Path('/mnt/user-data/uploads/KARAKUTU3.0')
ALFA = 0.01
M = 400          # eylem basina ornek
K = 20           # sabit tutulan durum sayisi


# =====================================================================
# denetim ortamlari
# =====================================================================
class NegatifDenetim:
    """Sonraki durum eylemden bagimsiz. Test GECMELI."""
    N_ACTIONS, STATE_DIM = 4, 6

    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)
        self._s = self.rng.uniform(0, 1, self.STATE_DIM)

    def durum_ata(self, s):
        self._s = np.asarray(s, dtype=float).copy()

    def step(self, a):
        self._s = self.rng.uniform(0, 1, self.STATE_DIM)
        return self._s.copy(), 0.0, False, False, {}


class PozitifDenetim(NegatifDenetim):
    """Sonraki durum eyleme gore kayar. Test GECMEMELI."""

    def __init__(self, seed=0, kayma=0.10):
        super().__init__(seed)
        self.kayma = float(kayma)

    def step(self, a):
        temel = self.rng.uniform(0, 1, self.STATE_DIM)
        self._s = np.clip(temel + self.kayma * a, 0, 1)
        return self._s.copy(), 0.0, False, False, {}


# =====================================================================
# sinamalar
# =====================================================================
def s1_bit_ayniligi(kur, durumlar, n_eylem):
    """Ayni akis paylasildiginda eylemler bit duzeyinde ayni s' veriyor mu."""
    fark = 0
    karsilastirma = 0
    for i, s in enumerate(durumlar):
        sonraki = []
        for a in range(n_eylem):
            e = kur(seed=10_000 + i)          # her eylem icin AYNI akis
            e.durum_ata(s)
            sp, *_ = e.step(a)
            sonraki.append(np.asarray(sp, dtype=float))
        for a in range(1, n_eylem):
            karsilastirma += 1
            if not np.array_equal(sonraki[0], sonraki[a]):
                fark += 1
    return {'karsilastirma': karsilastirma, 'farkli': fark,
            'bit_ayni': fark == 0}


def s2_dagilim(kur, durumlar, n_eylem, boyut):
    """Bagimsiz akislarla, boyut boyut Kruskal-Wallis."""
    esik = ALFA / (len(durumlar) * boyut)      # Bonferroni
    reddedilen = []
    p_min = 1.0
    for i, s in enumerate(durumlar):
        ornek = [[] for _ in range(n_eylem)]
        for a in range(n_eylem):
            for m in range(M):
                e = kur(seed=(i + 1) * 1_000_003 + a * 7919 + m)
                e.durum_ata(s)
                sp, *_ = e.step(a)
                ornek[a].append(np.asarray(sp, dtype=float))
        A = [np.array(x) for x in ornek]
        for d in range(boyut):
            kolon = [x[:, d] for x in A]
            if all(np.ptp(k) == 0 for k in kolon):
                continue                        # sabit boyut, sinanamaz
            try:
                _, p = stats.kruskal(*kolon)
            except ValueError:
                continue
            p_min = min(p_min, p)
            if p < esik:
                reddedilen.append({'durum': i, 'boyut': d, 'p': float(p)})
    return {'bonferroni_esik': esik, 'en_kucuk_p': float(p_min),
            'reddedilen': reddedilen, 'bagimsiz_kalir': not reddedilen}


def kos(ad, kur, n_eylem, boyut, tohum=7):
    rng = np.random.default_rng(tohum)
    durumlar = [rng.uniform(0, 1, boyut) for _ in range(K)]
    s1 = s1_bit_ayniligi(kur, durumlar, n_eylem)
    s2 = s2_dagilim(kur, durumlar, n_eylem, boyut)
    print('  %-22s S1 bit aynı %-5s (%d/%d fark)  S2 bağımsız %-5s '
          '(en küçük p %.3g, eşik %.2g)'
          % (ad, s1['bit_ayni'], s1['farkli'], s1['karsilastirma'],
             s2['bagimsiz_kalir'], s2['en_kucuk_p'], s2['bonferroni_esik']))
    return {'ortam': ad, 'n_eylem': n_eylem, 'boyut': boyut,
            'K': K, 'M': M, 's1': s1, 's2': s2}


# =====================================================================
# gercek ortamlar icin sarmalayicilar
# =====================================================================
def modul_yukle(yol: Path, ad: str):
    """Dosya yolundan modul yukler. Paket adlari uc depoda ayni oldugu icin
    normal import ilkini onbellekten dondururdu."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(ad, yol)
    m = importlib.util.module_from_spec(spec)
    sys.modules[ad] = m
    spec.loader.exec_module(m)
    return m


def ortam_sinifi(m):
    return next(v for v in vars(m).values()
                if isinstance(v, type) and hasattr(v, 'step')
                and hasattr(v, 'reset') and v.__module__ == m.__name__)


def bb3_kur():
    m = modul_yukle(UP / 'CDSA-BB3/12_GitHub_Repo/cdsa-bb3/src/rl_environment'
                    '/pilot_state_env.py', 'bb3_env')
    sinif = ortam_sinifi(m)

    class Sarmal(sinif):
        def durum_ata(self, s):
            self._state = np.asarray(s, dtype=float).copy()
    return Sarmal, sinif


def atm_kur():
    m = modul_yukle(UP / 'CDSA-ATM/12_GitHub_Repo/cdsa-atm/src/rl_environment'
                    '/env.py', 'atm_env')
    sinif = ortam_sinifi(m)

    class Sarmal(sinif):
        def durum_ata(self, s):
            self._state = np.asarray(s, dtype=float).copy()
    return Sarmal, sinif


def mro_veri(yol: Path, n=60, tohum=3):
    """MRO ortami bir veri kumesi istiyor. Gecis MEKANIZMASI veri icerigine
    bagli olmadigi icin sema uyumlu kucuk bir kume uretilir; bu, ortamin
    gercek sinifinin kosulabilmesi icindir ve bir bulgu uretmez."""
    rng = np.random.default_rng(tohum)
    turler = ['Oltalama saldırısı', 'Fidye yazılımı', 'USB zararlı yazılımı']
    tactics = ['Initial Access', 'Impact', 'Exfiltration']
    kume = []
    for i in range(n):
        kume.append({
            'olay_id': 'S%03d' % i,
            'olay_ozeti': {
                'olay_turu': turler[i % len(turler)],
                'etkilenen_hizmetler': ['h'] * int(rng.integers(1, 5)),
                'kesinti_suresi_dakika': int(rng.integers(1, 2000)),
                'tahmini_maddi_kayip_TL': int(rng.integers(1000, 400000))},
            'etiketler': {
                'risk_seviyesi': int(rng.integers(1, 5)),
                'mitre_attack': {'tactic': tactics[i % len(tactics)]},
                'kvkk_ozel_veri_iceriyor': bool(rng.integers(0, 2)),
                'shy145_madde18_72saat_uygunluk': bool(rng.integers(0, 2)),
                'shtsiber_ek19_kontrol_atfi': ['k'] * int(rng.integers(1, 5))},
            'kok_neden_analizi': {
                'swiss_cheese_katmanlari': ['s'] * int(rng.integers(1, 6))},
            'aksiyonlar': ['a'] * int(rng.integers(1, 5)),
        })
    yol.write_text(json.dumps(kume, ensure_ascii=False))
    return yol


def mro_kur():
    m = modul_yukle(UP / 'CDSA-MRO/12_GitHub_Repo/cdsa-mro/src/rl_environment'
                    '/cdsa_mro_env.py', 'mro_env')
    sinif = ortam_sinifi(m)
    veri = mro_veri(Path('/tmp/mro_sema_uyumlu.json'))

    class Sarmal(sinif):
        def __init__(self, seed=42):
            super().__init__(dataset_path=str(veri), seed=seed)

        def durum_ata(self, s):
            pass      # MRO durumu veri kumesi indisinden okur

        def step(self, a):
            ns, r, d, info = super().step(a)
            return ns, r, d, False, info
    return Sarmal, sinif


# =====================================================================
def main():
    print('GEÇİŞ FONKSİYONU EYLEM BAĞIMLILIĞI TESTİ')
    print('K=%d durum, eylem başına M=%d örnek, alfa=%.2g Bonferroni'
          % (K, M, ALFA))
    sonuc = {'K': K, 'M': M, 'alfa': ALFA, 'denetimler': [], 'ortamlar': [],
             'duyarlilik': []}

    print('\nDENETİMLER')
    neg = kos('negatif denetim', lambda seed=0: NegatifDenetim(seed), 4, 6)
    poz = kos('pozitif denetim 0,10',
              lambda seed=0: PozitifDenetim(seed, 0.10), 4, 6)
    sonuc['denetimler'] = [neg, poz]
    assert neg['s1']['bit_ayni'] and neg['s2']['bagimsiz_kalir'], \
        'negatif denetim geçmedi, test hatalı'
    assert not poz['s1']['bit_ayni'] and not poz['s2']['bagimsiz_kalir'], \
        'POZİTİF DENETİM BAĞIMLILIĞI SAPTAMADI — TEST KÖR, sonuç raporlanmaz'
    print('  -> pozitif denetim bağımlılığı saptadı, test kör değil')

    print('\nDUYARLILIK (kayma taraması, S2)')
    for kayma in (0.001, 0.002, 0.005, 0.01, 0.02, 0.05):
        r = s2_dagilim(lambda seed=0, k=kayma: PozitifDenetim(seed, k),
                       [np.random.default_rng(7).uniform(0, 1, 6)
                        for _ in range(K)], 4, 6)
        print('  kayma %-6.3f saptandı mı: %-5s (en küçük p %.3g)'
              % (kayma, not r['bagimsiz_kalir'], r['en_kucuk_p']))
        sonuc['duyarlilik'].append({'kayma': kayma,
                                    'saptandi': not r['bagimsiz_kalir'],
                                    'en_kucuk_p': r['en_kucuk_p']})

    print('\nYAYIMLANMIŞ ÜÇ ORTAM')
    B, Bsinif = bb3_kur()
    sonuc['ortamlar'].append(kos('CDSA-BB3 %s' % Bsinif.__name__,
                                 lambda seed=42: B(seed=seed),
                                 Bsinif.N_ACTIONS, Bsinif.STATE_DIM))
    A, Asinif = atm_kur()
    n_a = getattr(Asinif, 'N_ACTIONS', 5)
    d_a = getattr(Asinif, 'STATE_DIM', 12)
    sonuc['ortamlar'].append(kos('CDSA-ATM %s' % Asinif.__name__,
                                 lambda seed=42: A(seed=seed), n_a, d_a))
    Mr, Msinif = mro_kur()
    ornek = Mr(seed=42)
    d_m = int(ornek.n_features)
    n_m = int(ornek.n_actions)
    sonuc['ortamlar'].append(kos('CDSA-MRO %s' % Msinif.__name__,
                                 lambda seed=42: Mr(seed=seed), n_m, d_m))

    hepsi = all(o['s1']['bit_ayni'] and o['s2']['bagimsiz_kalir']
                for o in sonuc['ortamlar'])
    print('\n' + '=' * 66)
    print('ÜÇ ORTAMIN HEPSİNDE SONRAKİ DURUM EYLEMDEN BAĞIMSIZ: %s' % hepsi)
    if not hepsi:
        print('DİKKAT: en az bir ortamda bağımlılık saptandı, A makalesinin '
              'Bölüm 5.8.2 savı bu haliyle doğru değil.')
    sonuc['uc_ortamda_bagimsiz'] = hepsi
    Path('/home/claude/kkt/gecis_bagimliligi_sonuc.json').write_text(
        json.dumps(sonuc, indent=1, ensure_ascii=False))
    print('-> gecis_bagimliligi_sonuc.json')


if __name__ == '__main__':
    main()
