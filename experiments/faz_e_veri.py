"""Faz E — veri ayrimlari (E3 ayrik test, E4 gercek istemci ayrimi).

On kayit:
  E3: "Bakim damarinda olay ve sablon ailesi bazinda ayrik test kumesi (%20,
      aile duzeyinde); ayni ailenin varyantlari egitim ve teste dagitilmaz.
      Her ozelligin bilinme zaman damgasi yazilir; kesinti suresi, maddi kayip,
      kok neden katman sayisi ve alinan aksiyon sayisi karar ani listesinden
      CIKARILIR."
  E4: "Uc damarda istemci basina AYRIK kayit; sinif ve ozellik dagilimlari
      istemci basina olculup raporlanir (JS uzakligi >= 0,1 olmayan istemci
      cifti 'benzesik' damgasi alir). Acik heterojenlik senaryosu: bir
      istemcide kritik sinif payi iki kat."

TASARIM ILKESI: butun degisiklikler BAYRAK/ARGUMAN arkasindadir. Bu modul
faz_a_config'i ve mevcut ortamlari DEGISTIRMEZ; yalniz alt sinif uretir.
Mevcut Faz A komutlari (faz_a_run.py, faz_a_staged.py) varsayilan davranisi
birebir korur.

Kullanim:
  python3 faz_e_veri.py rapor          # E4 istemci ayrimi + JS raporu
  python3 faz_e_veri.py rapor-heteroj  # acik heterojenlik senaryosu
  python3 faz_e_veri.py e3             # (yalniz MRO) aile bazli ayrik test
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from faz_a_config import (PILLAR, make_env, N_ACTIONS, STATE_DIM,
                          NEW_STEP_API, INFO_TRUE_KEY, CRITICAL_ACTIONS)

OUT = HERE / "results"

# --- sabitler (on kayittan; sonuc gorulmeden) ---------------------------
HAVUZ_TOHUMU = 7042          # kayit havuzu uretim tohumu (ana tohumlarla cakismaz)
HAVUZ_N = 3000               # BB3/ATM: uretilen kayit sayisi
E3_TEST_ORANI = 0.20         # on kayit E3: %20
E3_AYRIM_TOHUMU = 7003
E4_AYRIM_TOHUMU = 7004
JS_ESIGI = 0.10              # on kayit E4: JS < 0,1 -> "benzesik"
HETEROJ_ISTEMCI = 0          # acik heterojenlik senaryosunda kritik payi 2x olan istemci


# =======================================================================
# Jensen-Shannon
# =======================================================================
def js_uzakligi(p, q, taban: int = 2) -> float:
    """Jensen-Shannon UZAKLIGI (= sqrt(JS diverjansi), taban-2 log ile [0,1])."""
    p = np.asarray(p, dtype=float); q = np.asarray(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)

    def kl(a, b):
        msk = a > 0
        return float(np.sum(a[msk] * (np.log(a[msk] / b[msk]) / np.log(taban))))
    jsd = 0.5 * kl(p, m) + 0.5 * kl(q, m)
    return float(np.sqrt(max(jsd, 0.0)))


def sinif_dagilimi(etiketler, k: int) -> np.ndarray:
    c = np.bincount(np.asarray(etiketler, dtype=int), minlength=k).astype(float)
    return c / c.sum() if c.sum() else c


def ozellik_js(Xa, Xb, kutu: int = 10) -> list:
    """Ozellik basina JS uzakligi (ortak [0,1] araliginda kutu histogrami)."""
    Xa = np.asarray(Xa, dtype=float); Xb = np.asarray(Xb, dtype=float)
    out = []
    for j in range(Xa.shape[1]):
        lo = min(Xa[:, j].min(), Xb[:, j].min())
        hi = max(Xa[:, j].max(), Xb[:, j].max())
        if hi <= lo:
            out.append(0.0); continue
        ha, _ = np.histogram(Xa[:, j], bins=kutu, range=(lo, hi))
        hb, _ = np.histogram(Xb[:, j], bins=kutu, range=(lo, hi))
        out.append(js_uzakligi(ha + 1e-12, hb + 1e-12))
    return [round(x, 4) for x in out]


# =======================================================================
# E4 — istemci basina AYRIK kayit
# =======================================================================
def kayit_havuzu(n: int = HAVUZ_N, tohum: int = HAVUZ_TOHUMU):
    """Damara gore sabit kayit havuzu: (X, y, kaynak_tanimi).

    BB3/ATM : ortam tohumlu uretir; her kayit bir (durum, dogru eylem) cifti.
    MRO     : veri kumesinin kendisi kayit havuzudur (1000 sentetik olay).
    """
    if PILLAR == "CDSA-MRO":
        env = make_env(tohum)
        X = np.asarray(env.features, dtype=float)
        y = np.asarray(env.labels, dtype=int)
        return X, y, f"{PILLAR}: synthetic_incidents_v1.json kayitlari (n={len(y)})"
    env = make_env(tohum)
    X, y = [], []
    env.reset(seed=tohum)
    for _ in range(n):
        s = env._sample_state()
        X.append(s)
        y.append(env._appropriate_action(s))
    return (np.asarray(X, dtype=float), np.asarray(y, dtype=int),
            f"{PILLAR}: make_env(seed={tohum})._sample_state() ile uretilmis "
            f"sabit kayit havuzu (n={n})")


def istemci_ayrimi(y, n_istemci: int = 3, tohum: int = E4_AYRIM_TOHUMU):
    """Kayitlari istemcilere AYRIK (kesisimsiz, ortusmez) dagitir."""
    rng = np.random.default_rng(tohum)
    idx = rng.permutation(len(y))
    paylar = np.array_split(idx, n_istemci)
    return [np.sort(p) for p in paylar]


def heterojen_agirliklar(y, pay, kat: float = 2.0):
    """Istemcinin KENDI ayrik kayitlari icinde kritik sinif payini 'kat' katina
    cikaran ornekleme agirliklari. Kayitlar ayrik kalir (baska istemciden kayit
    odunc alinmaz); yalniz istemcinin kendi kayitlari yeniden agirliklandirilir."""
    yy = y[pay]
    krit = np.isin(yy, sorted(CRITICAL_ACTIONS))
    p0 = krit.mean()
    hedef = min(kat * p0, 0.95)
    w = np.ones(len(yy), dtype=float)
    if 0 < p0 < 1:
        w[krit] = hedef / p0
        w[~krit] = (1 - hedef) / (1 - p0)
    return w / w.sum(), float(p0), float(hedef)


def _kayit_ortami_sinifi():
    """Damarin kendi ortam sinifindan tureyen 'kayit oynatan' ortam.

    Odul islevi, etiket kurali ve API (NEW_STEP_API) ust siniftan AYNEN
    devralinir; yalniz durum ornekleyici istemcinin AYRIK kayit alt kumesine
    kisitlanir. Odul islevi ve etiket kurali degistirilmez (on kayit ilkesi)."""
    if PILLAR == "CDSA-BB3":
        from src.rl_environment.pilot_state_env import PilotStateEnv as Taban
    elif PILLAR == "CDSA-ATM":
        from src.rl_environment.env import ATMFlowEnv as Taban
    else:
        from cdsa_mro_env import CDSAMROEnv as Taban

    class KayitOrtami(Taban):
        """Yalniz verilen kayit alt kumesinden ornekleyen ortam (E4)."""

        def __init__(self, X, pay, agirlik=None, seed=42, max_steps=10_000, **kw):
            if PILLAR == "CDSA-MRO":
                super().__init__(kw.pop("dataset_path"), seed=seed, max_steps=max_steps)
            else:
                super().__init__(seed=seed, max_steps=max_steps, **kw)
            self._X = np.asarray(X, dtype=float)
            self._pay = np.asarray(pay, dtype=int)
            self._w = None if agirlik is None else np.asarray(agirlik, dtype=float)
            self._ornek_rng = np.random.default_rng(seed)

        def _sec(self):
            if self._w is None:
                return int(self._ornek_rng.choice(self._pay))
            return int(self._ornek_rng.choice(self._pay, p=self._w))

        # BB3 / ATM yolu
        def _sample_state(self):
            return self._X[self._sec()].copy()

        # MRO yolu (indeks tabanli)
        def reset(self, seed=None):                         # noqa: D102
            if PILLAR != "CDSA-MRO":
                return super().reset(seed=seed) if seed is not None else super().reset()
            self.current_step = 0
            self.current_idx = self._sec()
            self.episode_rewards = []; self.episode_correct = 0; self.episode_total = 0
            return self.features[self.current_idx].copy()

        def step(self, action):                             # noqa: D102
            out = super().step(action)
            if PILLAR == "CDSA-MRO":
                self.current_idx = self._sec()
                s = self.features[self.current_idx].copy()
                return (s,) + tuple(out[1:])
            return out

    return KayitOrtami


def e4_istemci_ortamlari(seed: int = 42, heterojen: bool = False, n_istemci: int = 3):
    """E4 kolu: istemci basina AYRIK kayit alt kumesi olan ortamlar.

    heterojen=True -> HETEROJ_ISTEMCI'nin kritik sinif payi 2 kat (kendi
    ayrik kayitlari icinde yeniden agirliklandirma)."""
    X, y, kaynak = kayit_havuzu()
    paylar = istemci_ayrimi(y, n_istemci)
    Sinif = _kayit_ortami_sinifi()
    kw = {}
    if PILLAR == "CDSA-MRO":
        from faz_a_config import _DATA
        kw["dataset_path"] = _DATA
    ortamlar, meta = [], []
    for i, pay in enumerate(paylar):
        w = None; p0 = hedef = None
        if heterojen and i == HETEROJ_ISTEMCI:
            w, p0, hedef = heterojen_agirliklar(y, pay)
        ortamlar.append(Sinif(X, pay, agirlik=w, seed=seed + i, max_steps=10_000, **kw))
        meta.append({"istemci": i, "n_kayit": int(len(pay)),
                     "kritik_pay_ham": round(float(np.isin(y[pay], sorted(CRITICAL_ACTIONS)).mean()), 4),
                     "heterojen_agirlikli": bool(w is not None),
                     "kritik_pay_hedef": None if hedef is None else round(hedef, 4)})
    return ortamlar, {"kaynak": kaynak, "istemciler": meta,
                      "ayrik": True, "ayrim_tohumu": E4_AYRIM_TOHUMU}


def e4_rapor(heterojen: bool = False) -> dict:
    X, y, kaynak = kayit_havuzu()
    paylar = istemci_ayrimi(y)
    kesisim = []
    for i in range(len(paylar)):
        for j in range(i + 1, len(paylar)):
            kesisim.append(int(len(np.intersect1d(paylar[i], paylar[j]))))
    dag, Xs = [], []
    for i, pay in enumerate(paylar):
        yy = y[pay].copy()
        Xi = X[pay]
        if heterojen and i == HETEROJ_ISTEMCI:
            w, p0, hedef = heterojen_agirliklar(y, pay)
            # agirlikli sinif dagilimi (ortamda gorulen dagilim)
            d = np.zeros(N_ACTIONS)
            for c in range(N_ACTIONS):
                d[c] = w[yy == c].sum()
            dag.append(d)
        else:
            dag.append(sinif_dagilimi(yy, N_ACTIONS))
        Xs.append(Xi)
    ciftler = {}
    for i in range(len(paylar)):
        for j in range(i + 1, len(paylar)):
            s_js = js_uzakligi(dag[i], dag[j])
            o_js = ozellik_js(Xs[i], Xs[j])
            ciftler[f"{i}-{j}"] = {
                "sinif_js": round(s_js, 4),
                "ozellik_js_ortalama": round(float(np.mean(o_js)), 4),
                "ozellik_js_maks": round(float(np.max(o_js)), 4),
                "ozellik_js": o_js,
                "damga": ("non-IID (olculmus fark)" if s_js >= JS_ESIGI
                          else "benzesik (JS < 0,10)"),
            }
    return {
        "damar": PILLAR, "deney": "E4",
        "senaryo": "acik_heterojenlik_kritik_pay_2x" if heterojen else "temel_ayrik_kayit",
        "kaynak": kaynak,
        "n_istemci": len(paylar),
        "istemci_kayit_sayilari": [int(len(p)) for p in paylar],
        "istemci_kayitlari_ayrik_mi": all(k == 0 for k in kesisim),
        "cift_kesisim_buyuklukleri": kesisim,
        "sinif_dagilimlari": [[round(float(x), 4) for x in d] for d in dag],
        "kritik_sinif_paylari": [round(float(sum(d[c] for c in sorted(CRITICAL_ACTIONS))), 4)
                                 for d in dag],
        "js_esigi": JS_ESIGI,
        "cift_js": ciftler,
        "kural_E4_1": ("'Non-IID' sozcugu yalniz JS >= 0,10 olculmus cifti olan "
                       "kurulumlar icin kullanilir."),
        "ayrim_tohumu": E4_AYRIM_TOHUMU, "havuz_tohumu": HAVUZ_TOHUMU,
    }


# =======================================================================
# E3 — aile bazli ayrik test (yalniz CDSA-MRO)
# =======================================================================
# Karar ANI ozellik listesi. cdsa_mro_env._olaydan_ozellik'in dondurdugu
# 10 boyutlu vektorun indeksleri:
E3_OZELLIK_ADLARI = ["olay_turu_id", "mitre_tactic", "etkilenen_hizmet_sayisi",
                     "kesinti_suresi_dk", "tahmini_maddi_kayip_TL",
                     "kvkk_ozel_veri", "shy145_72saat_uygunluk",
                     "ek19_kontrol_atfi_sayisi", "swiss_cheese_katman_sayisi",
                     "aksiyon_sayisi"]
# On kayit E3: bu dordu karar ani listesinden CIKARILIR
E3_CIKARILAN = [3, 4, 8, 9]     # kesinti, maddi kayip, kok neden katman, aksiyon
E3_KARAR_ANI = [i for i in range(10) if i not in E3_CIKARILAN]

E3_BILINME_ZAMANI = {
    "olay_turu_id": "tespit ani (siniflandirma ilk triyajda yapilir)",
    "mitre_tactic": "tespit ani (ilk gostergelerden esleme)",
    "etkilenen_hizmet_sayisi": "tespit ani (etkilenen hizmet listesi ilk triyajda)",
    "kesinti_suresi_dk": "OLAY KAPANDIKTAN SONRA — karar aninda bilinmez, CIKARILDI",
    "tahmini_maddi_kayip_TL": "olay sonrasi maliyet degerlendirmesi — CIKARILDI",
    "kvkk_ozel_veri": "tespit ani (etkilenen veri sinifi ilk triyajda)",
    "shy145_72saat_uygunluk": "tespit ani (bildirim penceresi tespit anindan islar)",
    "ek19_kontrol_atfi_sayisi": "tespit ani (ihlal edilen kontrol atfi triyajda)",
    "swiss_cheese_katman_sayisi": "KOK NEDEN ANALIZI SONRASI — CIKARILDI",
    "aksiyon_sayisi": "AKSIYON PLANI YAZILDIKTAN SONRA — CIKARILDI",
}


def e3_aile_alani():
    """Aile kimliginin veride nasil bulundugunu tespit eder."""
    from faz_a_config import _DATA
    kayitlar = json.loads(Path(_DATA).read_text(encoding="utf-8"))
    ornek = kayitlar[0]
    acik = [k for k in ("sablon_ailesi", "sablon_id", "template_family", "aile_id")
            if k in ornek or k in ornek.get("metaveri", {})]
    return {
        "acik_aile_alani": acik or None,
        "bulgu": ("Veride ve schema.json'da ACIK bir 'sablon ailesi' alani YOKTUR. "
                  "Uretici (src/synthetic_data_generation/generator.py) sablon "
                  "havuzlarini OZET_SABLONLAR / SUREC_SABLONLAR / KOKNEDEN_SABLONLAR "
                  "sozluklerinde 'olay_turu' anahtariyla tutar; bir kaydin sablon "
                  "ailesi bu nedenle olay_ozeti.olay_turu alanindan tam olarak "
                  "belirlenir."),
        "kullanilan_aile_alani": "olay_ozeti.olay_turu",
        "aile_alani_turetilmis_mi": True,
        "yedek_ayrim": ("olay_kimligi_bazli_ayrim (olay_id) — aile alani "
                        "turetilebildigi icin BU TURDA KULLANILMADI"),
    }, kayitlar


def e3_aile_ayrimi(oran: float = E3_TEST_ORANI, tohum: int = E3_AYRIM_TOHUMU):
    """Aile duzeyinde %20 ayrik test kumesi: ayni ailenin hicbir varyanti
    egitim ve teste birlikte dagitilmaz."""
    bilgi, kayitlar = e3_aile_alani()
    aileler = {}
    for i, r in enumerate(kayitlar):
        aileler.setdefault(r["olay_ozeti"]["olay_turu"], []).append(i)
    adlar = sorted(aileler)
    rng = np.random.default_rng(tohum)
    rng.shuffle(adlar)
    n = len(kayitlar); hedef = oran * n
    test_aile, test_n = [], 0
    for ad in adlar:
        if test_n >= hedef:
            break
        test_aile.append(ad); test_n += len(aileler[ad])
    egitim_aile = [a for a in adlar if a not in test_aile]
    test_idx = np.sort(np.concatenate([aileler[a] for a in test_aile]))
    egitim_idx = np.sort(np.concatenate([aileler[a] for a in egitim_aile]))
    yedek = {  # ADIYLA kayda gecen yedek yordam (bu turda kullanilmadi)
        "ad": "olay_kimligi_bazli_ayrim",
        "kullanildi": False,
        "gerekce": "aile kimligi olay_ozeti.olay_turu'ndan turetilebildi",
    }
    return {
        "damar": PILLAR, "deney": "E3",
        "aile_alani": bilgi,
        "aile_sayisi": len(adlar),
        "test_aileleri": sorted(test_aile),
        "egitim_aileleri": sorted(egitim_aile),
        "n_toplam": n, "n_test": int(len(test_idx)), "n_egitim": int(len(egitim_idx)),
        "test_orani_gerceklesen": round(len(test_idx) / n, 4),
        "aile_ortusmesi_yok": bool(set(test_aile).isdisjoint(set(egitim_aile))),
        "kayit_ortusmesi_yok": bool(len(np.intersect1d(test_idx, egitim_idx)) == 0),
        "karar_ani_ozellik_indeksleri": E3_KARAR_ANI,
        "karar_ani_ozellik_adlari": [E3_OZELLIK_ADLARI[i] for i in E3_KARAR_ANI],
        "cikarilan_ozellik_indeksleri": E3_CIKARILAN,
        "cikarilan_ozellik_adlari": [E3_OZELLIK_ADLARI[i] for i in E3_CIKARILAN],
        "bilinme_zaman_damgalari": E3_BILINME_ZAMANI,
        "yedek_ayrim": yedek,
        "ayrim_tohumu": tohum,
        "_test_idx": test_idx.tolist(), "_egitim_idx": egitim_idx.tolist(),
    }


def e3_ortamlari(seed: int = 42, karar_ani_maskesi: bool = True):
    """E3 kolu: aile bazli ayrik egitim/test ortamlari + karar ani maskesi.

    karar_ani_maskesi=True -> cikarilan 4 ozellik SIFIRLANIR (gozlem boyutu
    korunur ki mevcut ajan/protokol degismesin; bilgi icerigi kaldirilir)."""
    if PILLAR != "CDSA-MRO":
        raise RuntimeError("E3 yalniz CDSA-MRO damarinda tanimlidir")
    from faz_a_config import _DATA
    ayrim = e3_aile_ayrimi()
    env0 = make_env(seed)
    X = np.asarray(env0.features, dtype=float)
    if karar_ani_maskesi:
        X = X.copy()
        X[:, E3_CIKARILAN] = 0.0
    Sinif = _kayit_ortami_sinifi()

    class E3Ortami(Sinif):
        def __init__(self, pay, **kw):
            super().__init__(X, pay, dataset_path=_DATA, **kw)
            self.features = X          # maskelenmis gozlem

    egitim = E3Ortami(np.asarray(ayrim["_egitim_idx"]), seed=seed, max_steps=10_000)
    test = E3Ortami(np.asarray(ayrim["_test_idx"]), seed=seed + 900, max_steps=10_000)
    return egitim, test, ayrim


# =======================================================================
def main(komut):
    OUT.mkdir(parents=True, exist_ok=True)
    if komut in ("rapor", "rapor-heteroj"):
        het = komut.endswith("heteroj")
        r = e4_rapor(heterojen=het)
        ad = "faz_e4_istemci_ayrimi_heteroj.json" if het else "faz_e4_istemci_ayrimi.json"
        (OUT / ad).write_text(json.dumps(r, indent=1, ensure_ascii=False))
        print(json.dumps({k: r[k] for k in
                          ("damar", "senaryo", "istemci_kayit_sayilari",
                           "istemci_kayitlari_ayrik_mi", "kritik_sinif_paylari")},
                         indent=1, ensure_ascii=False))
        for c, v in r["cift_js"].items():
            print(f"  cift {c}: sinif_JS={v['sinif_js']:.4f} "
                  f"ozellik_JS_ort={v['ozellik_js_ortalama']:.4f} -> {v['damga']}")
    elif komut == "e3":
        a = e3_aile_ayrimi()
        yaz = {k: v for k, v in a.items() if not k.startswith("_")}
        (OUT / "faz_e3_ayrim.json").write_text(
            json.dumps(a, indent=1, ensure_ascii=False))
        print(json.dumps(yaz, indent=1, ensure_ascii=False))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
