"""Faz E / E2 — zorunlu karsilastiricilar, esdeger 1.800 karar protokolunde.

On kayit E2 (kol (a) secildi): "Karsilastiricilar (zorunlu): maliyet-duyarli
lojistik siniflandirici, derinligi <= 4 karar agaci, cogunluk sinifi sabit
politikasi, hep-kritik sabit politikasi ve sentetik etiket kuralinin kendisi
(ust sinir)."
Kural E2.1: "PPO, maliyet-duyarli siniflandiriciyi makro-F1'de bes tohum
ortalamasinda +0,05 gecmezse 'DRL yontem secimi bu gorevde gerekcelendirilemedi'
yazilir."
E7: tohumlar 42, 43, 44, 45, 46.

DEGERLENDIRME PROTOKOLU — faz_e0_esdeger_degerlendirme.py ile BIREBIR AYNI:
  3 tekrar x 600 karar = 1.800; rep r: env = make_env(42+900+r),
  reset(seed=2026+r) (NEW_STEP_API ise), deterministik karar, gozlem bozulmasi yok.
Degerlendirme kumesi TOHUMDAN BAGIMSIZDIR; tohum yalniz karsilastiricinin
EGITIM kumesini belirler (egitim tohumu s -> make_env(s)).

MALIYET-DUYARLI LOJISTIK — kosudan once sabitlenen tanim:
  1) Cok sinifli lojistik regresyon P(c|x) egitilir; ornek agirliklari
     w_c ∝ (c sinifini kacirmanin ortalama maliyeti) = mean_{a != c} K[a, c].
  2) Karar: a* = argmin_a  sum_c P(c|x) * K[a, c]   (beklenen maliyeti en azlayan).
  K maliyet matrisi ORTAMIN KENDI ODUL ISLEVINDEN okunur (K[a,c] = -R(a,c));
  elle yazilmaz, koddan ornekleme ile olculur.

KARAR AGACI: DecisionTreeClassifier(max_depth=4), ayni ornek agirliklari.

Cikti: results/faz_e2_karsilastiricilar.json + her kol/tohum icin E0 kaydi.
Kullanim: python3 faz_e2_karsilastiricilar.py
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
                          NEW_STEP_API, INFO_TRUE_KEY, CRITICAL_ACTIONS)
from faz_a_staged import env_reset, env_step, new_agent, _load, _j2p, OUT
from faz_e_kayit import KosuKaydi, makro_f1

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

SEED_PROTOKOL = 42
EVAL_STEPS, EVAL_REPS = 600, 3
TOHUMLAR = [42, 43, 44, 45, 46]        # on kayit E7
N_EGITIM = 3000                        # egitim kumesi buyuklugu (kosudan once sabit)


# --- degerlendirme kumesi (protokol) -----------------------------------
def degerlendirme_kumesi():
    """1.800 (gozlem, gercek etiket) cifti — faz_e0 protokolunun aynisi.

    Ortamlarin durum akisi eylemden bagimsiz uretildigi icin gozlem dizisi
    politikadan bagimsizdir; sabit eylem 0 ile akitilir."""
    X, y = [], []
    for rep in range(EVAL_REPS):
        env = make_env(SEED_PROTOKOL + 900 + rep)
        s = env_reset(env, seed=2026 + rep) if NEW_STEP_API else env_reset(env)
        for _ in range(EVAL_STEPS):
            X.append(np.asarray(s, dtype=float))
            s2, r, done, info = env_step(env, 0)
            y.append(int(info[INFO_TRUE_KEY]))
            s = env_reset(env) if done else s2
    return np.asarray(X), np.asarray(y, dtype=int)


def egitim_kumesi(tohum: int, n: int = N_EGITIM):
    env = make_env(tohum)
    s = env_reset(env, seed=tohum) if NEW_STEP_API else env_reset(env)
    X, y = [], []
    for _ in range(n):
        X.append(np.asarray(s, dtype=float))
        s2, r, done, info = env_step(env, 0)
        y.append(int(info[INFO_TRUE_KEY]))
        s = env_reset(env) if done else s2
    return np.asarray(X), np.asarray(y, dtype=int)


# --- maliyet matrisi ORTAMIN ODUL ISLEVINDEN ----------------------------
def maliyet_matrisi(tohum: int, n_ornek: int = 600):
    """K[a, c] = -ortalama R(a | gercek etiket c). Ortamin step()'i cagrilarak
    OLCULUR; odul kurali bu betikte yeniden yazilmaz."""
    env = make_env(tohum)
    s = env_reset(env, seed=tohum) if NEW_STEP_API else env_reset(env)
    top = np.zeros((N_ACTIONS, N_ACTIONS)); say = np.zeros((N_ACTIONS, N_ACTIONS))
    for _ in range(n_ornek):
        if PILLAR == "CDSA-MRO":
            idx = env.current_idx; c = int(env.labels[idx])
            for a in range(N_ACTIONS):
                env.current_idx = idx; env.current_step = 0
                _, r, _, _ = env.step(a)
                top[a, c] += r; say[a, c] += 1
            env.current_idx = int(env.rng.integers(0, len(env.features)))
        else:
            st = np.asarray(s, dtype=float).copy()
            c = int(env._appropriate_action(st))
            for a in range(N_ACTIONS):
                env._state = st.copy(); env._t = 0
                out = env.step(a)
                r = out[1]
                top[a, c] += r; say[a, c] += 1
            env._state = st.copy(); env._t = 0
            out = env.step(0)
            s = out[0]
    with np.errstate(invalid="ignore"):
        R = np.where(say > 0, top / np.maximum(say, 1), np.nan)
    K = -R
    # gorulmemis (a,c) hucreleri: en kotu gozlenen maliyetle doldurulur
    if np.isnan(K).any():
        K = np.where(np.isnan(K), np.nanmax(K), K)
    return K, say.astype(int)


def sinif_agirliklari(K):
    """w_c ∝ c'yi kacirmanin ortalama maliyeti = mean_{a != c} K[a, c]."""
    k = K.shape[0]
    w = np.array([np.mean([K[a, c] for a in range(k) if a != c]) for c in range(k)])
    w = w - w.min() + 1e-6 if w.min() <= 0 else w
    return w / w.mean()


# --- karsilastiricilar --------------------------------------------------
def kol_maliyet_lojistik(Xtr, ytr, Xte, K, w):
    sw = w[ytr]
    m = LogisticRegression(max_iter=2000)
    m.fit(Xtr, ytr, sample_weight=sw)
    P = np.zeros((len(Xte), K.shape[0]))
    P[:, m.classes_] = m.predict_proba(Xte)
    beklenen = P @ K.T                     # [n_ornek, n_eylem]
    return np.argmin(beklenen, axis=1)


def kol_agac(Xtr, ytr, Xte, w, derinlik=4):
    m = DecisionTreeClassifier(max_depth=derinlik, random_state=0)
    m.fit(Xtr, ytr, sample_weight=w[ytr])
    return m.predict(Xte)


def kol_cogunluk(ytr, Xte):
    c = int(np.bincount(ytr, minlength=N_ACTIONS).argmax())
    return np.full(len(Xte), c, dtype=int), c


def kol_hep_kritik(Xte, a):
    return np.full(len(Xte), a, dtype=int)


# --- PPO kontrol noktalari (varsa) --------------------------------------
def ppo_kontrol_noktalari():
    """results/ altindaki E7 cok tohumlu kontrol noktalari:
    params_e7_<kol>_t<tohum>.json. Yoksa bos donulur (kampanya henuz bitmedi)."""
    out = {}
    for p in sorted(OUT.glob("params_e7_*_t*.json")):
        ad = p.stem[len("params_e7_"):]
        kol, _, t = ad.rpartition("_t")
        out.setdefault(kol, {})[int(t)] = p
    return out


def ppo_tahmin(pfile, Xte):
    ag = new_agent(0)
    ag.set_params(_j2p(_load(pfile, {})))
    return np.array([ag.act(x, deterministic=True)[0] for x in Xte], dtype=int)


# =======================================================================
def main():
    t0 = time.time()
    Xte, yte = degerlendirme_kumesi()
    assert len(yte) == EVAL_STEPS * EVAL_REPS
    sonuc = {
        "damar": PILLAR, "deney": "E2", "kol_secimi": "(a) baglamsal bant",
        "protokol": {"ad": "1.800 karar esdeger degerlendirme (faz_e0 ile birebir)",
                     "eval_steps": EVAL_STEPS, "eval_reps": EVAL_REPS,
                     "n_karar": int(len(yte)),
                     "env_tohumlari": [SEED_PROTOKOL + 900 + r for r in range(EVAL_REPS)],
                     "reset_tohumlari": ([2026 + r for r in range(EVAL_REPS)]
                                         if NEW_STEP_API else None)},
        "tohumlar": TOHUMLAR, "n_egitim": N_EGITIM,
        "maliyet_lojistik_tanimi": ("cok sinifli lojistik + beklenen maliyeti "
                                    "enazlayan karar; K ortamin odul islevinden olculdu"),
        "kollar": {}, "gercek_etiket_dagilimi":
            np.bincount(yte, minlength=N_ACTIONS).tolist(),
    }

    kol_tahminleri = {}      # kol -> {tohum: y_pred}
    for tohum in TOHUMLAR:
        Xtr, ytr = egitim_kumesi(tohum)
        K, say = maliyet_matrisi(tohum)
        w = sinif_agirliklari(K)
        if tohum == TOHUMLAR[0]:
            sonuc["maliyet_matrisi_K"] = [[round(float(x), 3) for x in r] for r in K]
            sonuc["sinif_agirliklari"] = [round(float(x), 4) for x in w]
            sonuc["egitim_etiket_dagilimi"] = np.bincount(ytr, minlength=N_ACTIONS).tolist()
        kol_tahminleri.setdefault("maliyet_lojistik", {})[tohum] = \
            kol_maliyet_lojistik(Xtr, ytr, Xte, K, w)
        kol_tahminleri.setdefault("karar_agaci_d4", {})[tohum] = kol_agac(Xtr, ytr, Xte, w)
        cog, c = kol_cogunluk(ytr, Xte)
        kol_tahminleri.setdefault(f"sabit_cogunluk_a{c}", {})[tohum] = cog
        for kr in sorted(CRITICAL_ACTIONS):
            kol_tahminleri.setdefault(f"sabit_hep_kritik_a{kr}", {})[tohum] = \
                kol_hep_kritik(Xte, kr)
        kol_tahminleri.setdefault("etiket_kurali_ust_sinir", {})[tohum] = yte.copy()

    # PPO kontrol noktalari (kampanya urettiyse)
    for kol, dosyalar in ppo_kontrol_noktalari().items():
        for t, p in dosyalar.items():
            kol_tahminleri.setdefault("ppo_" + kol, {})[t] = ppo_tahmin(p, Xte)

    # --- degerlendir + E0 kaydi ----------------------------------------
    for kol, per_tohum in kol_tahminleri.items():
        f1ler, dogruluklar, krit_duy = [], [], []
        for tohum, yp in sorted(per_tohum.items()):
            k = KosuKaydi(damar=PILLAR, deney="E2", kol=kol, tohum=tohum)
            k.yapilandirma_koddan("faz_a_config",
                                  ["PILLAR", "N_ACTIONS", "STATE_DIM", "NEW_STEP_API",
                                   "INFO_TRUE_KEY", "ACTION_LABELS", "CRITICAL_ACTIONS"])
            k.yapilandirma_koddan("faz_e2_karsilastiricilar",
                                  ["SEED_PROTOKOL", "EVAL_STEPS", "EVAL_REPS",
                                   "TOHUMLAR", "N_EGITIM"])
            k.veri_uretilmis(sonuc["protokol"]["ad"] + f" | egitim: make_env({tohum}), "
                             f"n={N_EGITIM}", n_kayit=int(len(yte)))
            cm = k.tahminler(yte, yp, n_sinif=N_ACTIONS, etiketler=list(ACTION_LABELS))
            m = makro_f1(cm)
            kd = [m["sinif_duyarlilik"][c] for c in sorted(CRITICAL_ACTIONS)]
            k.metrik(kritik_sinif_duyarlilik=kd)
            k.yaz()
            f1ler.append(m["makro_f1"]); dogruluklar.append(m["dogruluk"])
            krit_duy.append(float(np.mean(kd)))
        sonuc["kollar"][kol] = {
            "n_tohum": len(f1ler),
            "makro_f1_tohumlar": f1ler,
            "makro_f1_ort": round(float(np.mean(f1ler)), 4),
            "makro_f1_ss": round(float(np.std(f1ler, ddof=1)) if len(f1ler) > 1 else 0.0, 4),
            "dogruluk_ort": round(float(np.mean(dogruluklar)), 4),
            "kritik_duyarlilik_ort": round(float(np.mean(krit_duy)), 4),
        }

    # --- Kural E2.1 -----------------------------------------------------
    ref = sonuc["kollar"].get("maliyet_lojistik", {}).get("makro_f1_ort")
    e21 = {"esik": 0.05, "referans_maliyet_lojistik_makro_f1_ort": ref, "hukum": {}}
    ppo_kollari = [k for k in sonuc["kollar"] if k.startswith("ppo_")]
    if not ppo_kollari:
        e21["hukum"]["_durum"] = ("PPO kollari bu kosuda YOK (E7 cok tohumlu kontrol "
                                  "noktalari henuz uretilmedi) — E2.1 hukmu VERILMEDI")
    for k in ppo_kollari:
        v = sonuc["kollar"][k]
        if v["n_tohum"] < 5:
            e21["hukum"][k] = {"fark": None,
                               "hukum": f"bes tohum tamamlanmadi (n={v['n_tohum']}) — hukum verilmedi"}
            continue
        fark = round(v["makro_f1_ort"] - ref, 4)
        e21["hukum"][k] = {
            "fark_makro_f1": fark,
            "hukum": ("PPO maliyet-duyarli siniflandiriciyi +0,05 GECTI"
                      if fark > 0.05 else
                      "DRL yontem secimi bu gorevde gerekcelendirilemedi")}
    sonuc["kural_E2_1"] = e21
    sonuc["sure_sn"] = round(time.time() - t0, 1)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "faz_e2_karsilastiricilar.json").write_text(
        json.dumps(sonuc, indent=1, ensure_ascii=False))
    print(f"== {PILLAR} E2 ({sonuc['sure_sn']} sn) ==")
    for kol, v in sorted(sonuc["kollar"].items(), key=lambda x: -x[1]["makro_f1_ort"]):
        print(f"  {kol:28s} makro-F1 {v['makro_f1_ort']:.4f} ± {v['makro_f1_ss']:.4f}"
              f"  dogruluk {v['dogruluk_ort']:.4f}  kritik-duy {v['kritik_duyarlilik_ort']:.4f}"
              f"  (n={v['n_tohum']})")
    print("  E2.1:", json.dumps(e21["hukum"], ensure_ascii=False))


if __name__ == "__main__":
    main()
