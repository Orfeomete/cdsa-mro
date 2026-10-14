"""Faz E / E3.1 — TANISAL analiz (sonradan yapilan cozumleme, YENI EGITIM YOK).

NE DEGILDIR
-----------
Bu betik on kayitli E3.1 sonucunun YERINE GECMEZ. On kayitli olcu (makro-F1,
bes sinif uzerinden), 5 puanlik esik ve ham sonuclar
(results/faz_e3_ayrik_degerlendirme.json) DEGISMEZ. Burada yeni model
egitilmez, yeni tohum kosulmaz, yeni veri uretilmez.

NE YAPAR
--------
E3.1 kosusunda YAZILMIS E0 kayitlarindaki karisiklik matrislerini
(results/e_kayit/CDSA-MRO-E3-*.json; notlar.gecersiz=True olanlar ATLANIR)
yeniden okur ve her kol x {egitim, test} icin sunlari hesaplar:

  (a) ON KAYITLI makro-F1  : bes sinif uzerinden ortalama (desteksiz siniflar
      F1 = 0 olarak ortalamaya girer) — faz_e_kayit.makro_f1 ile ayni; DOKUNULMAZ,
      yalniz dogrulama amaciyla yeniden uretilir.
  (b) DESTEKLI makro-F1    : yalniz o kumede destegi (gercek ornegi) olan
      siniflar uzerinden ortalama.
  (c) ORTAK SINIF makro-F1 : egitim VE testte destegi olan siniflar kumesi
      uzerinde, HER IKI kumede yeniden hesaplanan makro-F1.
      -> "ortak sinif farki" = egitim(c) - test(c), yuzde puani.
  (d) AYRISTIRMA           : on kayitli fark (a) = ortak sinif kaybi (c)
      + sinif dagilimi etkisi (kalan). Sinif dagilimi etkisi, egitimde destegi
      olup testte destegi olmayan siniflarin bes sinifli ortalamaya sifir
      olarak girmesinden dogar.

Kesinlik/duyarlilik her zaman TAM 5x5 matristen hesaplanir (baska siniflara
yapilan tahminler ilgili sinif icin yanlis pozitif/negatif olarak sayilmaya
devam eder); (b) ve (c) yalniz ORTALAMANIN alindigi sinif kumesini daraltir.

Cikti: results/faz_e3_tanisal.json + her kol/kume icin E0 kaydi
       (results/e_kayit_tanisal/, kol = "e3tani_...", notlar.tur = "tanisal";
        on kayitli E3.1 kayitlarinin dizinine KARISTIRILMAZ).
Kullanim: python3 faz_e3_tanisal.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from faz_a_config import PILLAR, N_ACTIONS, ACTION_LABELS, CRITICAL_ACTIONS, _DATA
from faz_a_staged import OUT
from faz_e_kayit import KosuKaydi, makro_f1

KAYIT_DIZINI = OUT / "e_kayit"
KAYIT_TANISAL = OUT / "e_kayit_tanisal"      # tanisal kayitlar AYRI dizinde:
# on kayitli E3.1 kayitlarinin (e_kayit/) arasina karismaz, faz_e_ozet ve
# test_faz_e3.py'nin saydigi kume degismez.
HAM_SONUC = OUT / "faz_e3_ayrik_degerlendirme.json"
CIKTI = OUT / "faz_e3_tanisal.json"

YERINE_GECMEZ = ("Tanisal analiz: on kayitli E3.1 sonucunun YERINE GECMEZ. "
                 "On kayitli olcu (bes sinif uzerinden makro-F1), 5 puanlik "
                 "esik ve ham sonuclar degismemistir; bu blok sonradan yapilan "
                 "cozumlemedir (06.09.2026).")


# =======================================================================
# karisiklik matrisinden turetilen olculer
# =======================================================================
def sinif_bazli(cm):
    """Tam 5x5 matristen sinif bazli kesinlik/duyarlilik/F1/destek."""
    cm = np.asarray(cm, dtype=float)
    k = cm.shape[0]
    kes = np.zeros(k); duy = np.zeros(k); f1 = np.zeros(k)
    destek = cm.sum(axis=1)
    for c in range(k):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        kes[c] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        duy[c] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1[c] = (2 * kes[c] * duy[c] / (kes[c] + duy[c])
                 if (kes[c] + duy[c]) > 0 else 0.0)
    return kes, duy, f1, destek.astype(int)


def makro_alt_kume(f1, siniflar):
    """Verilen sinif alt kumesi uzerinde makro-F1 (bos kume -> None)."""
    siniflar = sorted(siniflar)
    if not siniflar:
        return None
    return float(np.mean([f1[c] for c in siniflar]))


# =======================================================================
# E0 kayitlarini oku (YENI KOSU YOK)
# =======================================================================
def kayitlari_oku():
    """E3.1 kayitlari: kol -> kume -> tohum -> karisiklik matrisi.
    notlar.gecersiz=True olan (--hizli on kosu) kayitlar ATLANIR."""
    veri = defaultdict(lambda: defaultdict(dict))
    dosyalar = defaultdict(list)
    atlanan = []
    for p in sorted(KAYIT_DIZINI.glob("CDSA-MRO-E3-*.json")):
        if p.name.startswith("tahmin_"):
            continue
        k = json.loads(p.read_text(encoding="utf-8"))
        if k.get("deney") != "E3" or not k.get("kol", "").startswith("e3_"):
            continue                     # tanisal kayitlar (e3tani_) dahil degil
        if k.get("notlar", {}).get("gecersiz") is True:
            atlanan.append(p.name)
            continue
        kol_kume = k["kol"][len("e3_"):]
        kol, kume = kol_kume.rsplit("_", 1)
        if kume not in ("egitim", "test"):
            continue
        veri[kol][kume][int(k["tohum"])] = np.asarray(
            k["karisiklik_matrisi"]["matris"], dtype=float)
        dosyalar[kol].append(p.name)
    return veri, dosyalar, atlanan


def _ort(liste):
    return round(float(np.mean(liste)), 4)


def kol_cozumle(kume_kayitlari):
    """Bir kol x kume icin tohumlar uzerinde ortalanmis tanisal olculer."""
    tohumlar = sorted(kume_kayitlari)
    kesL, duyL, f1L, aL, bL = [], [], [], [], []
    destek = None
    for t in tohumlar:
        kes, duy, f1, dst = sinif_bazli(kume_kayitlari[t])
        kesL.append(kes); duyL.append(duy); f1L.append(f1)
        destek = dst if destek is None else destek
        if not np.array_equal(destek, dst):
            raise SystemExit("Ayni kume icinde farkli destek dagilimi — beklenmez")
        destekli = [c for c in range(N_ACTIONS) if dst[c] > 0]
        aL.append(float(np.mean(f1)))
        bL.append(makro_alt_kume(f1, destekli))
    return {
        "tohumlar": tohumlar,
        "sinif_destek": destek.tolist(),
        "destegi_olan_siniflar": [c for c in range(N_ACTIONS) if destek[c] > 0],
        "sinif_kesinlik": [round(float(x), 4) for x in np.mean(kesL, axis=0)],
        "sinif_duyarlilik": [round(float(x), 4) for x in np.mean(duyL, axis=0)],
        "sinif_f1": [round(float(x), 4) for x in np.mean(f1L, axis=0)],
        "_f1_tohum_matrisi": np.asarray(f1L),
        "makro_f1_on_kayitli_5sinif": _ort(aL),
        "makro_f1_destekli_siniflar": _ort(bL),
    }


def main():
    t0 = time.time()
    if not HAM_SONUC.exists():
        raise SystemExit(f"Ham sonuc yok: {HAM_SONUC}")
    ham_metin = HAM_SONUC.read_bytes()
    ham = json.loads(ham_metin.decode("utf-8"))
    # HAM CEKIRDEK = dosyanin "_duzeltme_*" bloklari DISINDAKI butun alanlari.
    # Ozet, ham sayilarin degismedigini bu cekirdek uzerinden kanitlar; sonradan
    # eklenen tarihli duzeltme bloklari ozeti bozmaz.
    cekirdek = {k: v for k, v in ham.items() if not k.startswith("_duzeltme")}
    cekirdek_metin = json.dumps(cekirdek, indent=1, ensure_ascii=False).encode("utf-8")
    veri, dosyalar, atlanan = kayitlari_oku()
    if not veri:
        raise SystemExit("E3 kaydi bulunamadi")

    sonuc = {
        "damar": PILLAR, "deney": "E3.1-tanisal",
        "baslik": "E3.1 sonucunun sinif destegine duyarliligi — tanisal cozumleme",
        "on_kayitli_sonucun_yerine_gecmez": YERINE_GECMEZ,
        "tur": "tanisal",
        "tarih": "06.09.2026",
        "yeni_egitim_yapildi_mi": False,
        "kaynak": {
            "ham_sonuc_dosyasi": str(HAM_SONUC),
            "ham_cekirdek_md5": hashlib.md5(cekirdek_metin).hexdigest(),
            "ham_cekirdek_sha256": hashlib.sha256(cekirdek_metin).hexdigest(),
            "ham_cekirdek_tanimi": ("dosyanin '_duzeltme_*' bloklari disindaki "
                                    "butun alanlari, json.dumps(indent=1, "
                                    "ensure_ascii=False) ile serilestirilmis"),
            "ham_dosya_md5_su_an": hashlib.md5(ham_metin).hexdigest(),
            "kayit_dizini": str(KAYIT_DIZINI),
            "kullanilan_kayit_sayisi": sum(len(dosyalar[k]) for k in dosyalar),
            "atlanan_gecersiz_kayitlar": atlanan,
            "yontem": ("her sayi, E3.1 kosusunda yazilmis E0 kayitlarindaki "
                       "karisiklik matrislerinden turetilmistir; model yeniden "
                       "egitilmemis, tahminler yeniden uretilmemistir"),
        },
        "olcu_tanimlari": {
            "a_on_kayitli": ("makro-F1, BES sinif uzerinden ortalama; destegi "
                             "olmayan sinif F1 = 0 olarak ortalamaya girer "
                             "(faz_e_kayit.makro_f1 — E2 ile ayni tanim)"),
            "b_destekli": "makro-F1, yalniz o kumede destegi olan siniflar uzerinden",
            "c_ortak": ("makro-F1, egitim VE testte destegi olan siniflar uzerinde "
                        "her iki kumede yeniden hesaplanmis"),
            "kesinlik_duyarlilik": ("her zaman TAM 5x5 matristen; alt kume yalniz "
                                    "ORTALAMANIN alindigi sinif kumesini daraltir"),
            "d_ayristirma": ("on kayitli fark (a) = ortak sinif kaybi (c) + sinif "
                             "dagilimi etkisi; sinif dagilimi etkisi, egitimde "
                             "destegi olup testte destegi olmayan siniflarin bes "
                             "sinifli ortalamaya sifir girmesinden dogar"),
        },
        "sinif_etiketleri": list(ACTION_LABELS),
        "kritik_siniflar": sorted(CRITICAL_ACTIONS),
        "kollar": {},
    }

    ortak_kume_genel = None
    tutarlilik = {"ham_json_ile_ayni_makro_f1": {}, "hepsi_tutarli": True}

    for kol in sorted(veri):
        if not {"egitim", "test"} <= set(veri[kol]):
            continue
        ce = kol_cozumle(veri[kol]["egitim"])
        ct = kol_cozumle(veri[kol]["test"])
        ortak = sorted(set(ce["destegi_olan_siniflar"]) & set(ct["destegi_olan_siniflar"]))
        ortak_kume_genel = ortak if ortak_kume_genel is None else ortak_kume_genel

        c_eg = _ort([makro_alt_kume(f1, ortak) for f1 in ce["_f1_tohum_matrisi"]])
        c_te = _ort([makro_alt_kume(f1, ortak) for f1 in ct["_f1_tohum_matrisi"]])
        b_eg, b_te = ce["makro_f1_destekli_siniflar"], ct["makro_f1_destekli_siniflar"]
        a_eg, a_te = ce["makro_f1_on_kayitli_5sinif"], ct["makro_f1_on_kayitli_5sinif"]

        on_fark = round(100 * (a_eg - a_te), 2)
        ortak_fark = round(100 * (c_eg - c_te), 2)
        dagilim_payi = round(on_fark - ortak_fark, 2)
        pay_orani = (round(dagilim_payi / on_fark, 4) if abs(on_fark) > 1e-9 else None)

        kol_turu = ("etiket_kurali" if kol == "etiket_kurali_ust_sinir"
                    else "sabit_politika" if kol.startswith("sabit_")
                    else "ogrenen")
        if kol_turu == "sabit_politika":
            genelleme = ("uygulanmaz — sabit politika ogrenmez; egitim/test farki "
                         "yalnizca iki kumenin sinif bilesiminden dogar")
        elif abs(ortak_fark) <= 0.5:
            genelleme = "kanitli degil — ortak siniflarda kayip yok (destek etkisi)"
        elif abs(dagilim_payi) > abs(ortak_fark):
            genelleme = "destek etkisi baskin — ortak sinif kaybi daha kucuk"
        elif ortak_fark > 0:
            genelleme = "kanitli — ortak siniflarda da kayip var"
        else:
            genelleme = "kanitli degil — ortak siniflarda test egitimden dusuk degil"

        ham_kol = ham["kollar"].get(kol, {})
        for kume, deger, tanisal in (("egitim", ham_kol.get("egitim_makro_f1"), a_eg),
                                     ("test", ham_kol.get("test_makro_f1"), a_te)):
            ayni = deger is not None and abs(deger - tanisal) < 5e-4
            tutarlilik["ham_json_ile_ayni_makro_f1"][f"{kol}_{kume}"] = {
                "ham": deger, "tanisal_yeniden_uretim": tanisal, "ayni": bool(ayni)}
            tutarlilik["hepsi_tutarli"] &= bool(ayni)

        sonuc["kollar"][kol] = {
            "kol_turu": kol_turu,
            "n_tohum": len(ce["tohumlar"]),
            "tohumlar": ce["tohumlar"],
            "egitim": {k: v for k, v in ce.items() if not k.startswith("_")},
            "test": {k: v for k, v in ct.items() if not k.startswith("_")},
            "ortak_siniflar": ortak,
            "ortak_sinif_adlari": [ACTION_LABELS[c] for c in ortak],
            "makro_f1_ortak_egitim": c_eg,
            "makro_f1_ortak_test": c_te,
            "makro_f1_destekli_egitim": b_eg,
            "makro_f1_destekli_test": b_te,
            "ayristirma": {
                "on_kayitli_fark_puan": on_fark,
                "ortak_sinif_farki_puan": ortak_fark,
                "sinif_dagilimi_payi_puan": dagilim_payi,
                "sinif_dagilimi_payi_orani": pay_orani,
                "esik_tetiklendi_mi": bool(on_fark > ham["esik_puan"]),
                "genelleme_acigi": genelleme,
            },
        }

    sonuc["ortak_siniflar_genel"] = ortak_kume_genel
    sonuc["egitim_etiket_dagilimi"] = ham["egitim_etiket_dagilimi"]
    sonuc["test_etiket_dagilimi"] = ham["test_etiket_dagilimi"]
    sonuc["dogrulama"] = tutarlilik

    ek = sonuc["kollar"].get("etiket_kurali_ust_sinir", {})
    sonuc["etiket_kurali_okumasi"] = {
        "egitim_dogruluk": ham["kollar"]["etiket_kurali_ust_sinir"]["egitim_dogruluk"],
        "test_dogruluk": ham["kollar"]["etiket_kurali_ust_sinir"]["test_dogruluk"],
        "ortak_sinif_farki_puan": ek.get("ayristirma", {}).get("ortak_sinif_farki_puan"),
        "on_kayitli_fark_puan": ek.get("ayristirma", {}).get("on_kayitli_fark_puan"),
        "okuma": ("Etiket kurali egitimde ve testte %100 dogrudur; ortak siniflarda "
                  "F1 farki 0 puandir. On kayitli 20 puanlik dusus, egitimde dort "
                  "testte uc sinif bulunmasindan ve bulunmayan siniflarin bes "
                  "sinifli ortalamaya sifir girmesinden dogar: bu bir genelleme "
                  "basarisizligi degil, olcunun sinif destegine duyarliligidir."),
    }
    sonuc["ozet_hukum"] = {
        "esik_tetiklendi": [k for k, v in sonuc["kollar"].items()
                            if v["ayristirma"]["esik_tetiklendi_mi"]],
        "ortak_siniflarda_kayip_kanitli": [
            k for k, v in sonuc["kollar"].items()
            if v["ayristirma"]["genelleme_acigi"].startswith("kanitli —")],
        "not": ("'esik tetiklendi' Kural E3.1'in mekanik sonucudur; 'genelleme "
                "acigi kanitli' ayri bir okumadir ve ortak sinif farkina dayanir."),
    }
    sonuc["sure_sn"] = round(time.time() - t0, 2)

    CIKTI.write_text(json.dumps(sonuc, indent=1, ensure_ascii=False))

    # --- E0 kayitlari (tanisal) ----------------------------------------
    for kol, v in sonuc["kollar"].items():
        for kume in ("egitim", "test"):
            k = KosuKaydi(damar=PILLAR, deney="E3", kol=f"e3tani_{kol}_{kume}",
                          tohum=v["tohumlar"][0], kayit_dizini=KAYIT_TANISAL)
            ad = f"{PILLAR}-E3-tanisal-e3tani_{kol}_{kume}"
            k.yapilandirma_ekle("e3_tanisal", {
                "tur": "tanisal",
                "kaynak_kayitlar": "CDSA-MRO-E3-e3_%s_%s-*" % (kol, kume),
                "n_tohum": v["n_tohum"], "tohumlar": v["tohumlar"],
                "ortak_siniflar": v["ortak_siniflar"],
                "yeni_egitim_yapildi_mi": False,
            })
            cmler = [veri[kol][kume][t] for t in v["tohumlar"]]
            cm_top = np.sum(cmler, axis=0)
            y_true, y_pred = [], []
            for i in range(N_ACTIONS):
                for j in range(N_ACTIONS):
                    y_true += [i] * int(cm_top[i, j])
                    y_pred += [j] * int(cm_top[i, j])
            k.veri_dosyasi(_DATA, n_kayit=int(cm_top.sum()),
                           not_=("E3.1 tanisal: kol kayitlarinin karisiklik "
                                 "matrisleri toplanmistir (tohumlar birlestirilmis); "
                                 "yeni tahmin URETILMEMISTIR"))
            k.yapilandirma_koddan("faz_e_veri",
                                  ["E3_TEST_ORANI", "E3_AYRIM_TOHUMU",
                                   "E3_KARAR_ANI", "E3_CIKARILAN",
                                   "E3_OZELLIK_ADLARI"])
            k.yapilandirma_koddan("faz_e3_ayrik_degerlendirme",
                                  ["TOHUMLAR", "TUR", "E3_ESIK_PUAN"])
            k.tahminler(y_true, y_pred, n_sinif=N_ACTIONS,
                        etiketler=list(ACTION_LABELS),
                        dosya_adi=f"tahmin_{ad}.json")
            k.metrik(makro_f1_on_kayitli_5sinif=v[kume]["makro_f1_on_kayitli_5sinif"],
                     makro_f1_destekli_siniflar=v[kume]["makro_f1_destekli_siniflar"],
                     makro_f1_ortak_siniflar=v["makro_f1_ortak_%s" % kume],
                     sinif_destek=v[kume]["sinif_destek"])
            k.not_(tur="tanisal",
                   on_kayitli_sonucun_yerine_gecmez=YERINE_GECMEZ,
                   ayristirma=v["ayristirma"])
            k.yaz(dosya_adi=f"{ad}.json")   # sabit ad: yeniden kosuda birikmez

    print(f"== {PILLAR} E3.1 tanisal ({sonuc['sure_sn']} sn) ==")
    print(f"  ortak siniflar: {ortak_kume_genel}  "
          f"(egitim destek {sonuc['egitim_etiket_dagilimi']}, "
          f"test destek {sonuc['test_etiket_dagilimi']})")
    bas = f"  {'kol':28s} {'on kayitli':>11s} {'ortak':>8s} {'dagilim':>8s}  hukum"
    print(bas)
    for kol, v in sonuc["kollar"].items():
        a = v["ayristirma"]
        print(f"  {kol:28s} {a['on_kayitli_fark_puan']:+11.2f} "
              f"{a['ortak_sinif_farki_puan']:+8.2f} {a['sinif_dagilimi_payi_puan']:+8.2f}  "
              f"{'esik tetiklendi' if a['esik_tetiklendi_mi'] else 'esik altinda'}; "
              f"genelleme acigi: {a['genelleme_acigi']}")
    print(f"  ham JSON ile makro-F1 tutarliligi: {sonuc['dogrulama']['hepsi_tutarli']}")
    return sonuc


if __name__ == "__main__":
    main()
