"""Faz E / E3.1 TANISAL analiz birim testleri.

Sinanan iddialar:
  A) Ham sonuc DEGISMEDI: faz_e3_ayrik_degerlendirme.json'un "_duzeltme_*"
     bloklari disindaki cekirdegi, tanisal JSON'da kayitli md5 ile birebir ayni;
     kollar/kural_E3_1 sayilari ve esik yerinde.
  B) Tanisal olculer karisiklik matrislerinden yeniden uretilebilir; on kayitli
     (bes sinif) makro-F1 ham JSON ile ayni.
  C) Ortak sinif hesabi dogru: ortak kume = {2, 3, 4}; etiket kurali icin ortak
     sinif farki = 0 puan (destek etkisi), ogrenen kollarda ortak siniflarda da
     kayip var.
  D) Ayristirma toplanir: on kayitli fark = ortak sinif farki + sinif dagilimi payi.

Kullanim: python3 tests/test_faz_e3_tanisal.py <repo_kok>
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

KOK = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(KOK))
sys.path.insert(0, str(KOK / "experiments"))

import faz_e3_tanisal as tn

GECTI = []


def onay(ad, kosul, ek=""):
    GECTI.append(bool(kosul))
    print(f"  [{'GECTI' if kosul else 'KALDI'}] {ad} {ek}")


print(f"=== {KOK.name} — Faz E3.1 tanisal ===")

ham_yol = KOK / "experiments/results/faz_e3_ayrik_degerlendirme.json"
tan_yol = KOK / "experiments/results/faz_e3_tanisal.json"
ham = json.loads(ham_yol.read_text(encoding="utf-8"))
tan = json.loads(tan_yol.read_text(encoding="utf-8"))

# --- A) ham sonuc degismedi ---------------------------------------------
cekirdek = {k: v for k, v in ham.items() if not k.startswith("_duzeltme")}
md5 = hashlib.md5(json.dumps(cekirdek, indent=1, ensure_ascii=False).encode("utf-8")).hexdigest()
onay("A1 ham cekirdek md5 tanisal JSON'daki degerle ayni",
     md5 == tan["kaynak"]["ham_cekirdek_md5"], md5)
onay("A2 ham cekirdek md5 duzeltme blogundaki degerle ayni",
     md5 == ham["_duzeltme_06092026"]["ham_cekirdek_md5"])
onay("A3 esik 5 puan degismedi", ham["esik_puan"] == 5.0)
onay("A4 on kayitli olcu tanimi degismedi (bes sinif)",
     "bes sinif" in ham["olcu"])
onay("A5 kural_E3_1 hukumleri yerinde ve butun kollari kapsiyor",
     set(ham["kural_E3_1"]["hukum"]) == set(ham["kollar"]))
onay("A6 etiket kuralinin ham sayilari degismedi (0,80 / 0,60)",
     ham["kollar"]["etiket_kurali_ust_sinir"]["egitim_makro_f1"] == 0.8 and
     ham["kollar"]["etiket_kurali_ust_sinir"]["test_makro_f1"] == 0.6)
onay("A7 tanisal analiz yeni egitim yapmadigini beyan eder",
     tan["yeni_egitim_yapildi_mi"] is False and
     "YERINE GECMEZ" in tan["on_kayitli_sonucun_yerine_gecmez"])

# --- B) yeniden uretim ---------------------------------------------------
veri, dosyalar, atlanan = tn.kayitlari_oku()
onay("B1 gecersiz (--hizli) kayitlar atlanmis", len(atlanan) > 0 and
     all("gecersiz" not in a for a in []), f"atlanan n={len(atlanan)}")
onay("B2 her kol icin egitim ve test kaydi var",
     all({"egitim", "test"} <= set(veri[k]) for k in veri), f"n_kol={len(veri)}")
onay("B3 on kayitli makro-F1 ham JSON ile ayni (butun kollar)",
     tan["dogrulama"]["hepsi_tutarli"] is True)

cm = veri["etiket_kurali_ust_sinir"]["test"][42]
kes, duy, f1, dst = tn.sinif_bazli(cm)
onay("B4 etiket kurali test karisiklik matrisi kosegen (dogruluk 1,0)",
     np.allclose(cm, np.diag(np.diag(cm))))
onay("B5 test destegi [0, 0, 23, 127, 68]", dst.tolist() == [0, 0, 23, 127, 68],
     str(dst.tolist()))
cm_e = veri["etiket_kurali_ust_sinir"]["egitim"][42]
onay("B6 egitim destegi dort sinifli [0, 1, 115, 298, 368]",
     tn.sinif_bazli(cm_e)[3].tolist() == [0, 1, 115, 298, 368])
onay("B7 desteksiz sinifin F1'i 0 sayilir (olcunun destek duyarliligi)",
     f1[0] == 0.0 and f1[1] == 0.0 and float(np.mean(f1)) == 0.6)
onay("B8 destegi olan uc sinif uzerinde makro-F1 = 1,0",
     tn.makro_alt_kume(f1, [2, 3, 4]) == 1.0)

# --- C) ortak sinif hesabi ----------------------------------------------
onay("C1 ortak sinif kumesi {2, 3, 4}", tan["ortak_siniflar_genel"] == [2, 3, 4])
onay("C2 ortak kume = egitimde VE testte destegi olan siniflar",
     all(v["ortak_siniflar"] ==
         sorted(set(v["egitim"]["destegi_olan_siniflar"]) &
                set(v["test"]["destegi_olan_siniflar"]))
         for v in tan["kollar"].values()))
ek = tan["kollar"]["etiket_kurali_ust_sinir"]
onay("C3 ETIKET KURALI ortak sinif farki = 0 puan (genelleme acigi degil)",
     ek["ayristirma"]["ortak_sinif_farki_puan"] == 0.0 and
     ek["makro_f1_ortak_egitim"] == ek["makro_f1_ortak_test"] == 1.0)
onay("C4 etiket kuralinda esik yine de tetiklenmis (mekanik sonuc korunur)",
     ek["ayristirma"]["esik_tetiklendi_mi"] is True and
     ek["ayristirma"]["on_kayitli_fark_puan"] == 20.0)
onay("C5 etiket kuralinin dususu tumuyle sinif dagilimi payindan",
     ek["ayristirma"]["sinif_dagilimi_payi_puan"] == 20.0)
for kol in ("karar_agaci_d4", "maliyet_lojistik", "ppo_merkezi", "ppo_fedavg"):
    v = tan["kollar"][kol]
    onay(f"C6 {kol}: ortak siniflarda da kayip var (> 0 puan)",
         v["ayristirma"]["ortak_sinif_farki_puan"] > 0,
         f"{v['ayristirma']['ortak_sinif_farki_puan']:+.2f} pp")
onay("C7 sabit politikalarda genelleme acigi okumasi 'uygulanmaz'",
     all(tan["kollar"][k]["ayristirma"]["genelleme_acigi"].startswith("uygulanmaz")
         for k in tan["kollar"] if k.startswith("sabit_")))

# --- D) ayristirma tutarli ----------------------------------------------
tut = all(abs(v["ayristirma"]["on_kayitli_fark_puan"]
              - (v["ayristirma"]["ortak_sinif_farki_puan"]
                 + v["ayristirma"]["sinif_dagilimi_payi_puan"])) < 1e-9
          for v in tan["kollar"].values())
onay("D1 on kayitli fark = ortak sinif farki + sinif dagilimi payi", tut)
onay("D2 on kayitli fark ham JSON'un fark sutunuyla ayni",
     all(abs(v["ayristirma"]["on_kayitli_fark_puan"]
             - ham["kural_E3_1"]["hukum"][k]["fark_yuzde_puani_egitim_eksi_test"]) < 1e-9
         for k, v in tan["kollar"].items()))
onay("D3 esik tetiklenen kollar ham hukumle ayni",
     sorted(tan["ozet_hukum"]["esik_tetiklendi"]) ==
     sorted(k for k, h in ham["kural_E3_1"]["hukum"].items()
            if h["hukum"].startswith("genelleme acigi (")))

# --- E) tanisal E0 kayitlari --------------------------------------------
kd = KOK / "experiments/results/e_kayit_tanisal"
tk = [json.loads(p.read_text()) for p in kd.glob("*e3tani_*.json")
      if not p.name.startswith("tahmin_")]
onay("E0 tanisal kayitlar AYRI dizinde (on kayitli E3.1 kayitlarina karismaz)",
     not list((KOK / "experiments/results/e_kayit").glob("*e3tani_*")))
onay("E1 tanisal E0 kayitlari yazilmis", len(tk) == 2 * len(tan["kollar"]),
     f"n={len(tk)}")
onay("E2 her tanisal kayit 'tanisal' turunu ve yerine gecmez notunu tasir",
     all(k["notlar"]["tur"] == "tanisal" and
         "YERINE GECMEZ" in k["notlar"]["on_kayitli_sonucun_yerine_gecmez"]
         for k in tk))
onay("E3 tanisal kayitlar deney='E3' altinda (damar tablosuna karismaz)",
     all(k["deney"] == "E3" for k in tk))

print(f"--- {sum(GECTI)}/{len(GECTI)} test gecti ---")
sys.exit(0 if all(GECTI) else 1)
