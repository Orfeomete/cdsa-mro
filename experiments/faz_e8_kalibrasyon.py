"""Faz E / E8 — C kirpma esiginin KALIBRASYONLA belirlenmesi (on kayit Ek 4).

Ek 4 madde 2 uyarinca C, korunacak istemci guncellemelerinden DEGIL, korunacak
veriden bagimsiz ayri bir kalibrasyon kaynagindan belirlenir:

  * ayni sentetik uretici/ortam, KALIBRASYON TOHUMU ile ayri bir kalibrasyon
    kumesi uretir (BB3: 9042, MRO: 9044, ATM: 9043 — Ek 4 md 2);
  * bu kumede kisa bir yerel egitim kosusu yapilir (3 kalibrasyon istemcisi
    x K tur), her turda her istemcinin guncellemesi u = w_yerel - w_kuresel
    icin ||u||_1 olculur;
  * C = bu normlarin MEDYANI, iki anlamli basamaga yuvarlanir ve DONDURULUR.

Kalibrasyon kumesi hicbir istemcinin verisi degildir, ana kosulara girmez ve
C disinda hicbir ciktisi kullanilmaz. Kalibrasyon tohumlari egitim (42-46) ve
degerlendirme (942-944 / reset 2026-2028) tohumlariyla cakismaz.

Kullanim: python3 faz_e8_kalibrasyon.py [K_tur]
Cikti   : results/e_kayit/<...>.json (E0 kaydi) + results/faz_e8_C.json
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

from faz_a_config import PILLAR, make_client_envs, N_ACTIONS, STATE_DIM
from faz_a_staged import new_agent, train_local, OUT
from src.federated.fedavg import FedAvgAggregator, tree_l1, _tree_sub
from faz_e_kayit import KosuKaydi

# Ek 4 madde 2 — kalibrasyon tohumlari (ana kosu tohumlariyla cakismaz)
KALIBRASYON_TOHUMU = {"CDSA-BB3": 9042, "CDSA-ATM": 9043, "CDSA-MRO": 9044}
K_TUR = 5                      # kisa kalibrasyon kosusu
EGITIM_TOHUMLARI = [42, 43, 44, 45, 46]
DEGERLENDIRME_TOHUMLARI = [942, 943, 944]


def main(k_tur: int = K_TUR):
    t0 = time.time()
    tohum = KALIBRASYON_TOHUMU[PILLAR]
    assert tohum not in EGITIM_TOHUMLARI and tohum not in DEGERLENDIRME_TOHUMLARI

    # Kalibrasyon KUMESI: ayni uretici, AYRI tohum. Ana kosularda kullanilmaz.
    envs = make_client_envs(tohum)
    istemciler = [new_agent(tohum + i) for i in range(len(envs))]
    g = istemciler[0].params()
    agg = FedAvgAggregator(seed=tohum)

    normlar = []
    tur_kayit = []
    for tur in range(k_tur):
        for c in istemciler:
            c.set_params(g)
        tur_n = []
        for e, c in zip(envs, istemciler):
            train_local(e, c)
            tur_n.append(tree_l1(_tree_sub(c.params(), g)))
        normlar.extend(tur_n)
        tur_kayit.append([round(x, 6) for x in tur_n])
        g = agg.aggregate([c.params() for c in istemciler])

    medyan = float(np.median(normlar))
    C = float(f"{medyan:.2g}")            # iki anlamli basamak -> dondurulur
    n = len(envs)
    ozet = {
        "damar": PILLAR,
        "kaynak": "kalibrasyon kumesi (Ek 4 md 2) — korunacak veriden bagimsiz",
        "kalibrasyon_tohumu": tohum,
        "kalibrasyon_istemci_sayisi": n,
        "kalibrasyon_tur_sayisi": k_tur,
        "olculen_norm_sayisi": len(normlar),
        "L1_norm_medyani": round(medyan, 6),
        "L1_norm_min": round(float(np.min(normlar)), 6),
        "L1_norm_maks": round(float(np.max(normlar)), 6),
        "C_dondurulmus": C,
        "yuvarlama": "iki anlamli basamak",
        "n_ana_kosu_istemci": n,
        "delta1_2C_over_n": 2 * C / n,
        "T_tur": 160,
        "calisma_noktalari": {
            "eps_toplam_10": {"eps_tur": 10 / 160, "laplace_olcek": (2 * C / n) / (10 / 160)},
            "eps_toplam_1": {"eps_tur": 1 / 160, "laplace_olcek": (2 * C / n) / (1 / 160)},
        },
        "tur_bazinda_normlar": tur_kayit,
        "kanit_cumlesi": ("Gurultu eklenmesi tek basina DP kaniti degildir; kanit = "
                          "kirpma + turetilmis duyarlilik (2C/n) + kayitli eps_toplam."),
        "uyari": "Bu kosu bir DENEY degildir; yalniz C'yi kalibre eder ve ana kosulara girmez.",
    }

    # E0 kaydi
    k = KosuKaydi(damar=PILLAR, deney="E8", kol="kalibrasyon_C", tohum=tohum)
    k.yapilandirma_koddan("faz_a_config",
                          ["PILLAR", "N_ACTIONS", "STATE_DIM", "NEW_STEP_API",
                           "INFO_TRUE_KEY", "ACTION_LABELS", "CRITICAL_ACTIONS"])
    k.yapilandirma_koddan("faz_a_staged",
                          ["ROUNDS", "LOCAL_ROLLOUTS", "ROLLOUT_LEN", "ROUNDS_FED",
                           "PROBE_EVERY", "PROBE_STEPS", "EVAL_STEPS", "SEED"])
    k.yapilandirma_ekle("kalibrasyon", ozet)
    k.veri_uretilmis(f"{PILLAR} kalibrasyon kumesi: make_client_envs(seed={tohum}), "
                     f"{k_tur} tur x {n} istemci yerel egitim",
                     n_kayit=len(normlar))
    # E0: karisiklik matrisi zorunlu; kalibrasyon bir karar kosusu degildir,
    # bu yuzden dejenere (tek hucreli) matris yazilir ve notta aciklanir.
    k.tahminler([0] * len(normlar), [0] * len(normlar), n_sinif=N_ACTIONS)
    k.not_(kalibrasyon_kosusu=True,
           karisiklik_matrisi_notu=("kalibrasyon kosusunda karar verilmez; matris "
                                    "dejenere yazildi, hicbir tabloya girmez"),
           ek4_uyum="C korunacak istemci guncellemelerinden DEGIL kalibrasyon kumesinden")
    k.metrik(C_dondurulmus=C, L1_medyan=round(medyan, 6))
    kp = k.yaz()

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "faz_e8_C.json").write_text(json.dumps(ozet, indent=1, ensure_ascii=False))
    ozet["e0_kayit"] = str(kp)
    ozet["sure_sn"] = round(time.time() - t0, 1)
    print(json.dumps({kk: ozet[kk] for kk in
                      ("damar", "kalibrasyon_tohumu", "olculen_norm_sayisi",
                       "L1_norm_medyani", "C_dondurulmus", "delta1_2C_over_n",
                       "sure_sn")}, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else K_TUR)
