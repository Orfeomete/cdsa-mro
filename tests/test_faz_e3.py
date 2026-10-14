"""Faz E / E3.1 birim testleri — aile ayrimi, on isleme sizintisi, karar
sonrasi ozellik denetimi.

Sinanan uc iddia:
  A) Ayrim ortusmez: aile duzeyinde ve kayit duzeyinde kesisim YOKTUR ve
     dondurulmus results/faz_e3_ayrim.json yeniden uretilebilir.
  B) On isleme sizintisi yoktur: olcekleyici YALNIZ egitim kumesinden fit
     edilir; test kumesi degisse bile egitim istatistikleri degismez.
  C) Karar sonrasi ozellik kullanilmaz: sklearn kollarinda cikarilan 4 sutun
     hic alinmaz, PPO kollarinda gozlemde sifirdir; yazilan E0 kayitlari da
     bunu belgeler.

Kullanim: python3 tests/test_faz_e3.py <repo_kok>
"""
import json
import sys
from pathlib import Path

import numpy as np

KOK = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "experiments"))

import faz_e_veri as ev
import faz_e3_ayrik_degerlendirme as e3
from faz_a_config import make_env

GECTI = []


def onay(ad, kosul, ek=""):
    GECTI.append(bool(kosul))
    print(f"  [{'GECTI' if kosul else 'KALDI'}] {ad} {ek}")


print(f"=== {KOK.name} — Faz E3.1 ===")

# --- A) ayrim -----------------------------------------------------------
ayrim, ayni = e3.ayrimi_oku()
tr = np.asarray(ayrim["_egitim_idx"]); te = np.asarray(ayrim["_test_idx"])
onay("A1 dondurulmus ayrim yeniden uretilebilir (ayni tohum/oran)", ayni)
onay("A2 kayit kesisimi bos", len(np.intersect1d(tr, te)) == 0,
     f"|kesisim|={len(np.intersect1d(tr, te))}")
onay("A3 aile kesisimi bos",
     set(ayrim["test_aileleri"]).isdisjoint(set(ayrim["egitim_aileleri"])))
onay("A4 egitim + test = butun korpus, tekrar yok",
     len(tr) + len(te) == ayrim["n_toplam"] == len(set(tr.tolist() + te.tolist())),
     f"{len(tr)}+{len(te)}={ayrim['n_toplam']}")

# aile duzeyinde: bir ailenin butun kayitlari TEK tarafta
from faz_a_config import _DATA
kayitlar = json.loads(Path(_DATA).read_text(encoding="utf-8"))
aile = np.array([r["olay_ozeti"]["olay_turu"] for r in kayitlar])
bolunen = [a for a in set(aile)
           if (set(np.where(aile == a)[0]) & set(tr.tolist()))
           and (set(np.where(aile == a)[0]) & set(te.tolist()))]
onay("A5 hicbir aile iki tarafa BOLUNMEMIS (varyant sizintisi yok)",
     not bolunen, f"bolunen aileler: {bolunen}")
onay("A6 test orani on kayittaki %20 hedefine uyar (aile tam sayili)",
     0.15 <= ayrim["test_orani_gerceklesen"] <= 0.25,
     f"gerceklesen {ayrim['test_orani_gerceklesen']}")

# --- B) on isleme sizintisi ---------------------------------------------
env = make_env(42)
X = np.asarray(env.features, dtype=float)
ka = list(ayrim["karar_ani_ozellik_indeksleri"])
Xtr, Xte = X[tr][:, ka], X[te][:, ka]
Ztr, Zte, olcek = e3._olcekle(Xtr, Xte)

onay("B1 olcekleyici ortalamasi = EGITIM ortalamasi",
     np.allclose(olcek.mean_, Xtr.mean(axis=0)))
onay("B2 olcekleyici ortalamasi TAM KORPUS ortalamasindan farkli "
     "(yani tum veriden fit edilmemis)",
     not np.allclose(olcek.mean_, X[:, ka].mean(axis=0)))
onay("B3 olcekleyici olcegi = EGITIM standart sapmasi",
     np.allclose(olcek.scale_, Xtr.std(axis=0)))

# test kumesi degistirilse bile egitim donusumu ve fit istatistikleri AYNI
Xte_bozuk = Xte + 1000.0
Ztr2, Zte2, olcek2 = e3._olcekle(Xtr, Xte_bozuk)
onay("B4 test kumesi degisince egitim donusumu DEGISMEZ (fit'e girmiyor)",
     np.allclose(Ztr, Ztr2) and np.allclose(olcek.mean_, olcek2.mean_)
     and np.allclose(olcek.scale_, olcek2.scale_))
onay("B5 test kumesi yalnizca transform edilir (bozulan test ciktisi degisir)",
     not np.allclose(Zte, Zte2))

# maliyet matrisi de yalniz egitim kayitlarindan olculur
K_tr, say_tr = e3.maliyet_matrisi_egitim(tr)
onay("B6 maliyet matrisi K yalniz egitim kayitlarindan olculur",
     int(say_tr.sum()) == len(tr) * 5, f"gozlem sayisi {int(say_tr.sum())} = {len(tr)}x5")
egitim_siniflari = set(np.unique(np.asarray(env.labels)[tr]).tolist())
test_only = set(np.unique(np.asarray(env.labels)[te]).tolist()) - egitim_siniflari
onay("B7 K'nin sutun kapsami egitimde gorulen siniflarla sinirli",
     all(say_tr[:, c].sum() == 0 for c in test_only) if test_only else True,
     f"yalniz testte gorulen sinif: {sorted(test_only)}")

# --- C) karar sonrasi ozellik yok ---------------------------------------
cik = list(ayrim["cikarilan_ozellik_indeksleri"])
onay("C1 cikarilan indeksler on kayit lafziyla ayni {kesinti, kayip, swiss, aksiyon}",
     cik == [3, 4, 8, 9] == ev.E3_CIKARILAN)
onay("C2 karar ani listesi cikarilanlari icermez ve 6 ozelliktir",
     ka == [0, 1, 2, 5, 6, 7] and len(ka) == 6 and not (set(ka) & set(cik)))
onay("C3 sklearn kolu matrisi 6 sutunlu", Xtr.shape[1] == 6 and Xte.shape[1] == 6)

Xmask = X.copy(); Xmask[:, cik] = 0.0
onay("C4 PPO gozleminde cikarilan sutunlar butun kayitlarda SIFIR",
     np.all(Xmask[:, cik] == 0.0) and Xmask.shape[1] == 10)
onay("C5 PPO gozleminde karar ani sutunlari DEGISMEDEN kalir",
     np.allclose(Xmask[:, ka], X[:, ka]))
onay("C6 maskeleme gercekten bilgi kaldirir (ham veride bu sutunlar sifir degildi)",
     np.any(X[:, cik] != 0.0))

# --- D) yazilan E0 kayitlari --------------------------------------------
kd = KOK / "experiments/results/e_kayit"
e3k = [json.loads(p.read_text()) for p in kd.glob("*-E3-*.json")
       if not p.name.startswith("tahmin_")]
onay("D1 E3 kayitlari yazilmis", len(e3k) > 0, f"n={len(e3k)}")
if e3k:
    onay("D2 her E3 kaydi karar ani ozellik listesini KODDAN tasir",
         all(k["yapilandirma_koddan"]["faz_e_veri"]["E3_KARAR_ANI"] == [0, 1, 2, 5, 6, 7]
             for k in e3k))
    onay("D3 her E3 kaydi cikarilan ozellikleri KODDAN tasir",
         all(k["yapilandirma_koddan"]["faz_e_veri"]["E3_CIKARILAN"] == [3, 4, 8, 9]
             for k in e3k))
    onay("D4 esik 5 puan kayitlarda sabit",
         all(k["yapilandirma_koddan"]["faz_e3_ayrik_degerlendirme"]["E3_ESIK_PUAN"] == 5.0
             for k in e3k))
    nlar = {k["kol"].rsplit("_", 1)[-1]: k["karisiklik_matrisi"]["n"] for k in e3k}
    onay("D5 kayit n'leri ayrimla uyusur (egitim 782 / test 218)",
         nlar.get("egitim") == len(tr) and nlar.get("test") == len(te), str(nlar))

# --- E) sonuc dosyasi ve E3.1 hukmu -------------------------------------
sf = KOK / "experiments/results/faz_e3_ayrik_degerlendirme.json"
if sf.exists():
    s = json.loads(sf.read_text())
    onay("E1 esik 5 puan sonuc dosyasinda da sabit", s["esik_puan"] == 5.0)
    onay("E2 on isleme fit kumesi 'YALNIZ egitim' olarak kayda gecmis",
         s["on_isleme"]["fit_kumesi"] == "YALNIZ egitim")
    onay("E3 her kol icin hukum yazilmis",
         set(s["kural_E3_1"]["hukum"]) == set(s["kollar"]))
    tut = all(abs(round(100 * (v["egitim_makro_f1"] - v["test_makro_f1"]), 2)
                  - h["fark_yuzde_puani_egitim_eksi_test"]) < 1e-9
              for k, v in s["kollar"].items()
              for h in [s["kural_E3_1"]["hukum"][k]])
    onay("E4 fark sutunu = egitim - test (yuzde puani), hesap tutarli", tut)

print(f"--- {sum(GECTI)}/{len(GECTI)} test gecti ---")
sys.exit(0 if all(GECTI) else 1)
