"""Faz E / E3.1 — aile bazli AYRIK degerlendirme (yalniz CDSA-MRO).

On kayit E3 (FAZ_E_ON_KAYIT_05092026.md, Ek 5 §4):
  "Bakim damarinda olay ve sablon ailesi bazinda ayrik test kumesi (%20, aile
   duzeyinde); ayni ailenin varyantlari egitim ve teste dagitilmaz. Her
   ozelligin bilinme zaman damgasi yazilir; kesinti suresi, maddi kayip, kok
   neden katman sayisi ve alinan aksiyon sayisi karar ani listesinden CIKARILIR."
  Kural E3.1: "Test sonucu egitim sonucundan 5 PUANDAN fazla duserse
   'genelleme acigi' yazilir; ana tabloya YALNIZ test kumesi girer."

BU BETIK SONUC GORULMEDEN SABITLENEN KURGUYU UYGULAR:
  * Ayrim faz_e_veri.e3_aile_ayrimi() ile uretilmis ve results/faz_e3_ayrim.json
    icinde DONDURULMUSTUR; bu betik ayrimi YENIDEN URETMEZ, dosyadan OKUR ve
    ayrimin yeniden uretilebilirligini dogrular.
  * Ozellikler: yalniz KARAR ANI listesi (6 ozellik, indeks 0,1,2,5,6,7).
    Cikarilan 4 karar SONRASI ozellik (3,4,8,9) sklearn kollarinda sutun olarak
    ALINMAZ; PPO kollarinda gozlem boyutu korunmak zorunda oldugu icin
    SIFIRLANIR (faz_e_veri.e3_ortamlari, karar_ani_maskesi=True).
  * On isleme (olcekleme) YALNIZ EGITIM kumesinden fit edilir (bkz. _olcekle);
    test kumesi yalnizca transform edilir. Maliyet matrisi K de yalniz egitim
    kayitlari uzerinde olculur.
  * Test kumesiyle hicbir ayar, esik secimi ya da erken durdurma yapilmaz;
    butun hiperparametreler mevcut kollarin (E2 / faz_e_kampanya) degerleridir.
  * Esik 5 puan (E3_ESIK_PUAN) sabittir.

Olcu: makro-F1 (faz_e_kayit.makro_f1 — E2 ile AYNI tanim, bes sinif uzerinden),
egitim kumesinde (in-sample) ve ayrik test kumesinde ayri ayri.

Cikti: results/faz_e3_ayrik_degerlendirme.json + her kol/kume/tohum icin E0 kaydi.
Kullanim: python3 faz_e3_ayrik_degerlendirme.py [--hizli]
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from faz_a_config import (PILLAR, make_env, N_ACTIONS, STATE_DIM, ACTION_LABELS,
                          NEW_STEP_API, INFO_TRUE_KEY, CRITICAL_ACTIONS, _DATA)
from faz_a_staged import new_agent, train_local, OUT, LOCAL_ROLLOUTS, ROLLOUT_LEN
from faz_e_kayit import KosuKaydi, makro_f1
import faz_e_veri as ev
from src.federated.fedavg import FedAvgAggregator

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

TOHUMLAR = [42, 43, 44, 45, 46]      # on kayit E7
TUR = 100                            # faz_e_kampanya.TUR_VARSAYILAN ile ayni butce
E3_ESIK_PUAN = 5.0                   # Kural E3.1 — SABIT, sonuc gorulmeden
AGAC_DERINLIK = 4                    # on kayit E2: derinligi <= 4 karar agaci
AGAC_RANDOM_STATE = 0                # E2 ile ayni
LOJISTIK_MAX_ITER = 2000             # E2 ile ayni
AYRIM_DOSYASI = OUT / "faz_e3_ayrim.json"


# =======================================================================
# Ayrim: DOSYADAN okunur (dondurulmus), yeniden uretilebilirligi dogrulanir
# =======================================================================
def ayrimi_oku():
    if not AYRIM_DOSYASI.exists():
        raise SystemExit(f"Ayrim dosyasi yok: {AYRIM_DOSYASI} "
                         f"(once: python3 faz_e_veri.py e3)")
    a = json.loads(AYRIM_DOSYASI.read_text(encoding="utf-8"))
    yeni = ev.e3_aile_ayrimi()          # ayni tohum/oran ile yeniden uretim
    ayni = (a["_egitim_idx"] == yeni["_egitim_idx"] and
            a["_test_idx"] == yeni["_test_idx"] and
            a["test_aileleri"] == yeni["test_aileleri"])
    return a, bool(ayni)


def _olcekle(Xtr, Xte):
    """ON ISLEME — YALNIZ EGITIM KUMESINDEN FIT EDILIR.

    fit yalnizca Xtr ile cagrilir; test kumesi SADECE transform edilir.
    Bu satirlar Ek 8'de sizinti kaniti olarak birebir alintilanmaktadir."""
    olcek = StandardScaler()
    olcek.fit(Xtr)                      # <-- fit YALNIZ egitim
    return olcek.transform(Xtr), olcek.transform(Xte), olcek


# =======================================================================
# Maliyet matrisi — YALNIZ EGITIM kayitlarindan olculur
# =======================================================================
def maliyet_matrisi_egitim(egitim_idx, tohum: int = 42):
    """K[a, c] = -ortalama R(a | gercek etiket c); ortamin kendi step()'i
    cagrilarak olculur ve YALNIZ egitim kayitlari uzerinden gecilir."""
    env = make_env(tohum)
    top = np.zeros((N_ACTIONS, N_ACTIONS)); say = np.zeros((N_ACTIONS, N_ACTIONS))
    for idx in egitim_idx:
        c = int(env.labels[idx])
        for a in range(N_ACTIONS):
            env.current_idx = int(idx); env.current_step = 0
            _, r, _, _ = env.step(a)
            top[a, c] += r; say[a, c] += 1
    with np.errstate(invalid="ignore"):
        R = np.where(say > 0, top / np.maximum(say, 1), np.nan)
    K = -R
    if np.isnan(K).any():
        K = np.where(np.isnan(K), np.nanmax(K), K)
    return K, say.astype(int)


def sinif_agirliklari(K):
    k = K.shape[0]
    w = np.array([np.mean([K[a, c] for a in range(k) if a != c]) for c in range(k)])
    w = w - w.min() + 1e-6 if w.min() <= 0 else w
    return w / w.mean()


# =======================================================================
# PPO kollari — E3 egitim ortamlarinda yeniden egitim
# =======================================================================
def _e3_istemci_ortamlari(egitim_idx, X_maskeli, tohum, n_istemci=3):
    """faz_a_config.make_client_envs ile ayni heterojenlik kurgusu (ayni
    korpus, farkli tohum => farkli kayit sirasi), fakat korpus YALNIZ
    egitim ailelerinin kayitlaridir."""
    Sinif = ev._kayit_ortami_sinifi()

    class E3Ortami(Sinif):
        def __init__(self, pay, **kw):
            super().__init__(X_maskeli, pay, dataset_path=_DATA, **kw)
            self.features = X_maskeli

    return [E3Ortami(np.asarray(egitim_idx), seed=tohum + 17 * i, max_steps=10_000)
            for i in range(n_istemci)]


def ppo_kos(kol, egitim_idx, X_maskeli, tohum, tur=TUR):
    envs = _e3_istemci_ortamlari(egitim_idx, X_maskeli, tohum)
    gecis = 0
    if kol == "merkezi":
        ag = new_agent(tohum)
        for _ in range(tur):
            for e in envs:
                train_local(e, ag)
                gecis += LOCAL_ROLLOUTS * ROLLOUT_LEN
        son = ag
    else:                                   # fedavg
        agg = FedAvgAggregator(seed=tohum)
        cl = [new_agent(tohum + i) for i in range(len(envs))]
        g = cl[0].params()
        for _ in range(tur):
            for c in cl:
                c.set_params(g)
            for e, c in zip(envs, cl):
                train_local(e, c)
                gecis += LOCAL_ROLLOUTS * ROLLOUT_LEN
            g = agg.aggregate([c.params() for c in cl])
        son = new_agent(0); son.set_params(g)
    return son, gecis


def ppo_tahmin(ajan, X):
    return np.array([ajan.act(x, deterministic=True)[0] for x in X], dtype=int)


# =======================================================================
def _kaydet(kol, kume, tohum, y_true, y_pred, ek_yapilandirma, veri_tanimi,
            ek_metrik=None):
    k = KosuKaydi(damar=PILLAR, deney="E3", kol=f"e3_{kol}_{kume}", tohum=tohum)
    k.yapilandirma_koddan("faz_a_config",
                          ["PILLAR", "N_ACTIONS", "STATE_DIM", "NEW_STEP_API",
                           "INFO_TRUE_KEY", "ACTION_LABELS", "CRITICAL_ACTIONS"])
    k.yapilandirma_koddan("faz_e3_ayrik_degerlendirme",
                          ["TOHUMLAR", "TUR", "E3_ESIK_PUAN", "AGAC_DERINLIK",
                           "AGAC_RANDOM_STATE", "LOJISTIK_MAX_ITER"])
    k.yapilandirma_koddan("faz_e_veri",
                          ["E3_TEST_ORANI", "E3_AYRIM_TOHUMU", "E3_KARAR_ANI",
                           "E3_CIKARILAN", "E3_OZELLIK_ADLARI"])
    k.yapilandirma_ekle("e3_kosu", ek_yapilandirma)
    k.veri_dosyasi(_DATA, n_kayit=int(len(y_true)),
                   not_=veri_tanimi)
    cm = k.tahminler(y_true, y_pred, n_sinif=N_ACTIONS, etiketler=list(ACTION_LABELS))
    m = makro_f1(cm)
    kd = [m["sinif_duyarlilik"][c] for c in sorted(CRITICAL_ACTIONS)]
    k.metrik(kritik_sinif_duyarlilik=kd, **(ek_metrik or {}))
    k.yaz()
    return m


def main(hizli=False):
    t0 = time.time()
    ayrim, ayrim_ayni = ayrimi_oku()
    egitim_idx = np.asarray(ayrim["_egitim_idx"], dtype=int)
    test_idx = np.asarray(ayrim["_test_idx"], dtype=int)
    assert len(np.intersect1d(egitim_idx, test_idx)) == 0
    karar_ani = list(ayrim["karar_ani_ozellik_indeksleri"])
    cikarilan = list(ayrim["cikarilan_ozellik_indeksleri"])

    env0 = make_env(42)
    Xtam = np.asarray(env0.features, dtype=float)
    y = np.asarray(env0.labels, dtype=int)

    # sklearn kollari: karar ani SUTUNLARI (cikarilanlar hic alinmaz)
    Xtr_ham, Xte_ham = Xtam[egitim_idx][:, karar_ani], Xtam[test_idx][:, karar_ani]
    ytr, yte = y[egitim_idx], y[test_idx]
    Xtr, Xte, olcek = _olcekle(Xtr_ham, Xte_ham)

    # PPO kollari: gozlem boyutu 10; cikarilan 4 sutun SIFIRLANIR
    Xmask = Xtam.copy(); Xmask[:, cikarilan] = 0.0

    tohumlar = TOHUMLAR[:1] if hizli else TOHUMLAR
    K, say = maliyet_matrisi_egitim(egitim_idx)
    w = sinif_agirliklari(K)
    cog = int(np.bincount(ytr, minlength=N_ACTIONS).argmax())

    sonuc = {
        "damar": PILLAR, "deney": "E3.1",
        "baslik": "aile bazli ayrik degerlendirme (karar ani ozellikleri)",
        "ayrim_kaynagi": str(AYRIM_DOSYASI),
        "ayrim_dondurulmus_ve_yeniden_uretilebilir": ayrim_ayni,
        "ayrim": {k: ayrim[k] for k in ("aile_sayisi", "test_aileleri", "egitim_aileleri",
                                        "n_toplam", "n_egitim", "n_test",
                                        "test_orani_gerceklesen", "aile_ortusmesi_yok",
                                        "kayit_ortusmesi_yok", "ayrim_tohumu")},
        "ozellikler": {
            "karar_ani_indeksleri": karar_ani,
            "karar_ani_adlari": ayrim["karar_ani_ozellik_adlari"],
            "cikarilan_indeksler": cikarilan,
            "cikarilan_adlar": ayrim["cikarilan_ozellik_adlari"],
            "sklearn_kollarinda": "cikarilan sutunlar ALINMAZ (6 sutun)",
            "ppo_kollarinda": ("gozlem boyutu 10 korunur, cikarilan 4 sutun "
                               "SIFIRLANIR (faz_e_veri.e3_ortamlari ile ayni kural)"),
        },
        "on_isleme": {
            "yontem": "StandardScaler",
            "fit_kumesi": "YALNIZ egitim",
            "kod_satiri": "olcek.fit(Xtr)  # <-- fit YALNIZ egitim  (faz_e3_ayrik_degerlendirme._olcekle)",
            "test_kumesi_islemi": "yalnizca transform",
            "egitim_ortalamalari": [round(float(x), 6) for x in olcek.mean_],
            "egitim_olcekleri": [round(float(x), 6) for x in olcek.scale_],
            "ortam_ici_normalizasyon": ("cdsa_mro_env._olaydan_ozellik icindeki "
                                        "bolenler (14.0, 5.0, log(2500), log(500000), 6.0) "
                                        "KOD SABITIDIR; veriden fit EDILMEZ, bu nedenle "
                                        "test kumesinden bilgi tasimaz"),
        },
        "maliyet_matrisi_K": [[round(float(x), 3) for x in r] for r in K],
        "maliyet_matrisi_kaynagi": "yalniz egitim kayitlari (n=%d) uzerinde olculdu" % len(egitim_idx),
        "sinif_agirliklari": [round(float(x), 4) for x in w],
        "egitim_etiket_dagilimi": np.bincount(ytr, minlength=N_ACTIONS).tolist(),
        "test_etiket_dagilimi": np.bincount(yte, minlength=N_ACTIONS).tolist(),
        "olcu": "makro-F1 (faz_e_kayit.makro_f1; bes sinif uzerinden, E2 ile ayni tanim)",
        "esik_puan": E3_ESIK_PUAN,
        "tohumlar": tohumlar, "tur": TUR,
        "kollar": {},
    }

    # --- sklearn + sabit kollar (egitim kumesi ayrimla SABIT; tohumdan
    #     bagimsiz oldugu icin tek kez kosulur) ---------------------------
    tahminler = {}
    m = LogisticRegression(max_iter=LOJISTIK_MAX_ITER)
    m.fit(Xtr, ytr, sample_weight=w[ytr])

    def _lojistik(Xa):
        P = np.zeros((len(Xa), N_ACTIONS))
        P[:, m.classes_] = m.predict_proba(Xa)
        return np.argmin(P @ K.T, axis=1)

    tahminler["maliyet_lojistik"] = (_lojistik(Xtr), _lojistik(Xte), 42)

    ag = DecisionTreeClassifier(max_depth=AGAC_DERINLIK, random_state=AGAC_RANDOM_STATE)
    ag.fit(Xtr, ytr, sample_weight=w[ytr])
    tahminler["karar_agaci_d4"] = (ag.predict(Xtr), ag.predict(Xte), 42)

    tahminler[f"sabit_cogunluk_a{cog}"] = (np.full(len(ytr), cog), np.full(len(yte), cog), 42)
    for kr in sorted(CRITICAL_ACTIONS):
        tahminler[f"sabit_hep_kritik_a{kr}"] = (np.full(len(ytr), kr),
                                                np.full(len(yte), kr), 42)
    tahminler["etiket_kurali_ust_sinir"] = (ytr.copy(), yte.copy(), 42)

    for kol, (ptr, pte, tohum) in tahminler.items():
        yap = {"kol_turu": "sklearn/sabit", "egitim_kumesi_tohumdan_bagimsiz": True,
               "on_isleme_fit_kumesi": "egitim", "ozellik_sayisi": len(karar_ani)}
        me = _kaydet(kol, "egitim", tohum, ytr, ptr, yap,
                     "E3 aile ayrimi — EGITIM kaydi alt kumesi (in-sample)")
        mt = _kaydet(kol, "test", tohum, yte, pte, yap,
                     "E3 aile ayrimi — AYRIK TEST kaydi alt kumesi")
        sonuc["kollar"][kol] = {
            "tur": "sklearn/sabit", "n_tohum": 1,
            "egitim_makro_f1": me["makro_f1"], "test_makro_f1": mt["makro_f1"],
            "egitim_dogruluk": me["dogruluk"], "test_dogruluk": mt["dogruluk"],
        }

    # --- PPO kollari (5 tohum) ------------------------------------------
    for kol in ("ppo_merkezi", "ppo_fedavg"):
        etr, ete, sureler, gecisler = [], [], [], []
        for tohum in tohumlar:
            ts = time.time()
            ajan, gecis = ppo_kos(kol.replace("ppo_", ""), egitim_idx, Xmask, tohum)
            sure = time.time() - ts
            ptr = ppo_tahmin(ajan, Xmask[egitim_idx])
            pte = ppo_tahmin(ajan, Xmask[test_idx])
            yap = {"kol_turu": "PPO", "tur": TUR, "cevre_gecisi": gecis,
                   "gozlem": "10 boyut; cikarilan 4 sutun sifirlanmis",
                   "n_istemci": 3, "egitim_korpusu": "yalniz E3 egitim aileleri"}
            me = _kaydet(kol, "egitim", tohum, ytr, ptr, yap,
                         "E3 aile ayrimi — EGITIM kaydi alt kumesi (in-sample)",
                         {"duvar_saati_sn": round(sure, 2), "cevre_gecisi": gecis})
            mt = _kaydet(kol, "test", tohum, yte, pte, yap,
                         "E3 aile ayrimi — AYRIK TEST kaydi alt kumesi",
                         {"duvar_saati_sn": round(sure, 2), "cevre_gecisi": gecis})
            etr.append(me["makro_f1"]); ete.append(mt["makro_f1"])
            sureler.append(round(sure, 2)); gecisler.append(gecis)
            print(f"  {kol} t{tohum}: egitim {me['makro_f1']:.4f} "
                  f"test {mt['makro_f1']:.4f} ({sure:.1f} sn)", flush=True)
        sonuc["kollar"][kol] = {
            "tur": "PPO", "n_tohum": len(etr), "tohumlar": tohumlar,
            "egitim_makro_f1_tohumlar": etr, "test_makro_f1_tohumlar": ete,
            "egitim_makro_f1": round(float(np.mean(etr)), 4),
            "test_makro_f1": round(float(np.mean(ete)), 4),
            "egitim_makro_f1_ss": round(float(np.std(etr, ddof=1)) if len(etr) > 1 else 0.0, 4),
            "test_makro_f1_ss": round(float(np.std(ete, ddof=1)) if len(ete) > 1 else 0.0, 4),
            "duvar_saati_sn": sureler, "cevre_gecisi": gecisler,
        }

    # --- Kural E3.1 hukmu (kol kol) -------------------------------------
    hukumler = {}
    for kol, v in sonuc["kollar"].items():
        fark_puan = round(100 * (v["egitim_makro_f1"] - v["test_makro_f1"]), 2)
        hukumler[kol] = {
            "egitim_makro_f1": v["egitim_makro_f1"],
            "test_makro_f1": v["test_makro_f1"],
            "fark_yuzde_puani_egitim_eksi_test": fark_puan,
            "hukum": ("genelleme acigi (fark > 5 puan)" if fark_puan > E3_ESIK_PUAN
                      else "genelleme acigi yazilmaz (fark <= 5 puan)"),
        }
    sonuc["kural_E3_1"] = {
        "lafiz": ("test sonucu egitim sonucundan 5 PUANDAN fazla duserse "
                  "'genelleme acigi' yazilir; ana tabloya YALNIZ test kumesi girer"),
        "esik_puan": E3_ESIK_PUAN,
        "olcu": "makro-F1, yuzde puani",
        "ana_tabloya_giren": "test kumesi sutunu",
        "hukum": hukumler,
    }
    sonuc["sure_sn"] = round(time.time() - t0, 1)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "faz_e3_ayrik_degerlendirme.json").write_text(
        json.dumps(sonuc, indent=1, ensure_ascii=False))
    print(f"== {PILLAR} E3.1 ({sonuc['sure_sn']} sn) ==")
    for kol, v in sonuc["kural_E3_1"]["hukum"].items():
        print(f"  {kol:28s} egitim {v['egitim_makro_f1']:.4f}  "
              f"test {v['test_makro_f1']:.4f}  fark {v['fark_yuzde_puani_egitim_eksi_test']:+.2f} pp"
              f"  -> {v['hukum']}")
    return sonuc


if __name__ == "__main__":
    main(hizli=("--hizli" in sys.argv))
