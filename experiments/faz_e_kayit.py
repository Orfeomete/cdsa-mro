"""Faz E — E0 kayit disiplini modulu (uc damarda ORTAK; birebir kopya).

On kayit: FAZ_E_ON_KAYIT_05092026.md, bolum E0.
  "Her kosu; kosu kimligi, tohum, kod surumu (git ozeti), yapilandirmanin
   KODDAN OKUNAN hali (sabit degil), veri dosyasinin SHA-256 ozeti, tahmin
   dosyasi ve karisiklik matrisini yazar. Bir tabloya giren her sayi bu
   alanlardan turetilir; turetilemeyen sayi tabloya girmez."

Kullanim (kutuphane):
    from faz_e_kayit import KosuKaydi
    k = KosuKaydi(deney="E2", kol="lojistik_maliyet_duyarli", tohum=42)
    k.yapilandirma_koddan("faz_a_config", ["N_ACTIONS", "STATE_DIM", ...])
    k.veri_dosyasi(path)                  # SHA-256 hesaplar
    k.tahminler(y_true, y_pred)           # tahmin dosyasi + karisiklik matrisi
    k.yaz()                               # results/e_kayit/<kosu_kimligi>.json

Kullanim (CLI):
    python3 faz_e_kayit.py dogrula <kayit.json> [...]   # eksik alan -> hata
    python3 faz_e_kayit.py dogrula-dizin <dizin>
    python3 faz_e_kayit.py smoke                        # duman testi

Bu modul hicbir mevcut dosyayi degistirmez ve mevcut Faz A davranisina
dokunmaz. 05.09.2026.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
KAYIT_DIZINI = HERE / "results" / "e_kayit"

SEMA_SURUM = "faz_e_kayit/1.0"

# --- E0 zorunlu alanlar -------------------------------------------------
ZORUNLU = [
    "sema_surum",
    "kosu_kimligi",
    "damar",
    "deney",
    "kol",
    "tohum",
    "tarih_utc",
    "kod_surumu",          # git ozeti (yoksa dosya ozetleri)
    "yapilandirma_koddan",  # koddan okunmus; sabit degil
    "veri",                 # {yol, sha256, n_kayit}
    "tahmin_dosyasi",
    "karisiklik_matrisi",
    "ortam",
]

SEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "CDSA Faz E kosu kaydi semasi",
    "version": SEMA_SURUM,
    "type": "object",
    "required": ZORUNLU,
    "properties": {
        "sema_surum": {"type": "string"},
        "kosu_kimligi": {"type": "string",
                         "description": "damar-deney-kol-tohum-zaman damgasi"},
        "damar": {"type": "string", "enum": ["CDSA-BB3", "CDSA-MRO", "CDSA-ATM"]},
        "deney": {"type": "string", "description": "E1..E9"},
        "kol": {"type": "string"},
        "tohum": {"type": "integer"},
        "tarih_utc": {"type": "string"},
        "kod_surumu": {
            "type": "object",
            "required": ["yontem"],
            "properties": {
                "yontem": {"type": "string", "enum": ["git", "dosya_ozetleri"]},
                "git_head": {"type": ["string", "null"]},
                "kirli": {"type": ["boolean", "null"]},
                "dosya_ozetleri": {"type": ["object", "null"]},
                "kod_agac_ozeti": {"type": "string"},
            },
        },
        "yapilandirma_koddan": {
            "type": "object",
            "description": "Degerler ilgili modullerden calisma aninda OKUNUR; "
                           "belgeye elle yazilan sabit kabul edilmez.",
        },
        "veri": {
            "type": "object",
            "required": ["yol", "sha256"],
            "properties": {"yol": {"type": ["string", "null"]},
                           "sha256": {"type": ["string", "null"]},
                           "n_kayit": {"type": ["integer", "null"]},
                           "not": {"type": ["string", "null"]}},
        },
        "tahmin_dosyasi": {"type": ["string", "null"]},
        "karisiklik_matrisi": {
            "type": "object",
            "required": ["duzen", "matris", "n"],
            "properties": {"duzen": {"type": "string", "enum": ["[true][pred]"]},
                           "matris": {"type": "array"},
                           "n": {"type": "integer"},
                           "etiketler": {"type": "array"}},
        },
        "metrikler": {"type": "object"},
        "ortam": {"type": "object"},
        "sure_sn": {"type": "number"},
        "notlar": {"type": "object"},
    },
}


# --- yardimcilar --------------------------------------------------------
def sha256_dosya(yol) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def sha256_metin(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def git_ozeti(repo: Path = REPO) -> dict:
    """Git ozeti; git yoksa/basarisizsa kaynak dosya SHA-256 ozetleri."""
    try:
        ortak = ["git", "-c", f"safe.directory={repo}", "-C", str(repo)]
        head = subprocess.run(ortak + ["rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=20)
        if head.returncode == 0:
            durum = subprocess.run(ortak + ["status", "--porcelain"],
                                   capture_output=True, text=True, timeout=20)
            return {"yontem": "git",
                    "git_head": head.stdout.strip(),
                    "kirli": bool(durum.stdout.strip()),
                    "dosya_ozetleri": None,
                    "kod_agac_ozeti": _kod_agac_ozeti(repo)[1]}
    except Exception:
        pass
    ozetler, agac = _kod_agac_ozeti(repo)
    return {"yontem": "dosya_ozetleri", "git_head": None, "kirli": None,
            "dosya_ozetleri": ozetler, "kod_agac_ozeti": agac}


def _kod_agac_ozeti(repo: Path):
    """src/ ve experiments/ altindaki .py dosyalarinin ozetleri + toplu ozet."""
    ozetler = {}
    for alt in ("src", "experiments"):
        kok = repo / alt
        if not kok.exists():
            continue
        for p in sorted(kok.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            ozetler[str(p.relative_to(repo))] = sha256_dosya(p)
    agac = sha256_metin("\n".join(f"{k} {v}" for k, v in sorted(ozetler.items())))
    return ozetler, agac


def ortam_ozeti() -> dict:
    return {"python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "makine": platform.machine()}


def karisiklik_matrisi(y_true, y_pred, n_sinif: int) -> np.ndarray:
    """[true][pred] duzeninde karisiklik matrisi."""
    cm = np.zeros((n_sinif, n_sinif), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[int(t), int(p)] += 1
    return cm


def makro_f1(cm: np.ndarray):
    """Karisiklik matrisinden sinif bazli F1 ve makro-F1 (E0: her sayi
    karisiklik matrisinden turetilir)."""
    cm = np.asarray(cm, dtype=float)
    k = cm.shape[0]
    f1 = np.zeros(k)
    kesinlik = np.zeros(k)
    duyarlilik = np.zeros(k)
    for c in range(k):
        tp = cm[c, c]
        fp = cm[:, c].sum() - tp
        fn = cm[c, :].sum() - tp
        kesinlik[c] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        duyarlilik[c] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1[c] = (2 * kesinlik[c] * duyarlilik[c] / (kesinlik[c] + duyarlilik[c])
                 if (kesinlik[c] + duyarlilik[c]) > 0 else 0.0)
    return {"sinif_f1": [round(float(x), 4) for x in f1],
            "sinif_kesinlik": [round(float(x), 4) for x in kesinlik],
            "sinif_duyarlilik": [round(float(x), 4) for x in duyarlilik],
            "makro_f1": round(float(f1.mean()), 4),
            "dogruluk": round(float(np.trace(cm) / cm.sum()), 4) if cm.sum() else None}


# --- kayit nesnesi ------------------------------------------------------
class KosuKaydi:
    def __init__(self, damar: str, deney: str, kol: str, tohum: int,
                 kayit_dizini: Path = None, repo: Path = None):
        self.repo = Path(repo) if repo else REPO
        self._t0 = time.time()
        zd = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.d = {
            "sema_surum": SEMA_SURUM,
            "kosu_kimligi": f"{damar}-{deney}-{kol}-t{tohum}-{zd}",
            "damar": damar, "deney": deney, "kol": kol, "tohum": int(tohum),
            "tarih_utc": datetime.now(timezone.utc).isoformat(),
            "kod_surumu": git_ozeti(self.repo),
            "yapilandirma_koddan": {},
            "veri": {"yol": None, "sha256": None, "n_kayit": None, "not": None},
            "tahmin_dosyasi": None,
            "karisiklik_matrisi": None,
            "metrikler": {},
            "ortam": ortam_ozeti(),
            "notlar": {},
        }
        self.kayit_dizini = Path(kayit_dizini) if kayit_dizini else (
            self.repo / "experiments" / "results" / "e_kayit")

    # -- yapilandirma KODDAN --------------------------------------------
    def yapilandirma_koddan(self, modul_adi: str, alanlar, takma: str = None):
        """Modulu ice aktarip alanlari CALISMA ANINDA okur (E0 gereği:
        belgede yazan sabit degil, kodun kendisi)."""
        m = importlib.import_module(modul_adi)
        blok = {}
        for a in alanlar:
            v = getattr(m, a, "<YOK>")
            blok[a] = _jsonlastir(v)
        blok["_modul_dosyasi"] = getattr(m, "__file__", None)
        if blok["_modul_dosyasi"] and Path(blok["_modul_dosyasi"]).exists():
            blok["_modul_sha256"] = sha256_dosya(blok["_modul_dosyasi"])
        self.d["yapilandirma_koddan"][takma or modul_adi] = blok
        return blok

    def yapilandirma_ekle(self, ad: str, sozluk: dict):
        """Kod icinde hesaplanmis (turetilmis) yapilandirma degerleri."""
        self.d["yapilandirma_koddan"][ad] = _jsonlastir(sozluk)

    # -- veri -------------------------------------------------------------
    def veri_dosyasi(self, yol, n_kayit: int = None, not_: str = None):
        yol = Path(yol)
        self.d["veri"] = {"yol": str(yol), "sha256": sha256_dosya(yol),
                          "n_kayit": n_kayit, "not": not_}

    def veri_uretilmis(self, tanim: str, n_kayit: int = None):
        """Veri dosyasi yok; ortam tohumdan uretiyor. Uretim tanimi ozetlenir."""
        self.d["veri"] = {"yol": None, "sha256": sha256_metin(tanim),
                          "n_kayit": n_kayit,
                          "not": "uretilmis ortam; sha256 = uretim tanimi ozeti: " + tanim}

    # -- tahminler --------------------------------------------------------
    def tahminler(self, y_true, y_pred, n_sinif: int, etiketler=None,
                  dosya_adi: str = None):
        y_true = [int(x) for x in y_true]
        y_pred = [int(x) for x in y_pred]
        cm = karisiklik_matrisi(y_true, y_pred, n_sinif)
        self.d["karisiklik_matrisi"] = {"duzen": "[true][pred]",
                                        "matris": cm.tolist(),
                                        "n": int(cm.sum()),
                                        "etiketler": list(etiketler or [])}
        self.d["metrikler"].update(makro_f1(cm))
        self.kayit_dizini.mkdir(parents=True, exist_ok=True)
        ad = dosya_adi or f"tahmin_{self.d['kosu_kimligi']}.json"
        tp = self.kayit_dizini / ad
        tp.write_text(json.dumps({"kosu_kimligi": self.d["kosu_kimligi"],
                                  "y_true": y_true, "y_pred": y_pred},
                                 separators=(",", ":")))
        self.d["tahmin_dosyasi"] = str(tp)
        return cm

    def metrik(self, **kw):
        self.d["metrikler"].update(_jsonlastir(kw))

    def not_(self, **kw):
        self.d["notlar"].update(_jsonlastir(kw))

    # -- yazim ------------------------------------------------------------
    def yaz(self, dosya_adi: str = None) -> Path:
        self.d["sure_sn"] = round(time.time() - self._t0, 3)
        dogrula(self.d)
        self.kayit_dizini.mkdir(parents=True, exist_ok=True)
        p = self.kayit_dizini / (dosya_adi or f"{self.d['kosu_kimligi']}.json")
        p.write_text(json.dumps(self.d, indent=1, ensure_ascii=False))
        return p


class KayitHatasi(ValueError):
    pass


def dogrula(kayit: dict) -> None:
    """Eksik/ bos zorunlu alan -> KayitHatasi."""
    eksik = [a for a in ZORUNLU if a not in kayit or kayit[a] in (None, {}, "")]
    if eksik:
        raise KayitHatasi(f"E0 zorunlu alan eksik/bos: {eksik}")
    ks = kayit["kod_surumu"]
    if ks.get("yontem") not in ("git", "dosya_ozetleri"):
        raise KayitHatasi("kod_surumu.yontem git ya da dosya_ozetleri olmali")
    if ks["yontem"] == "git" and not ks.get("git_head"):
        raise KayitHatasi("kod_surumu.yontem=git ama git_head bos")
    if ks["yontem"] == "dosya_ozetleri" and not ks.get("dosya_ozetleri"):
        raise KayitHatasi("kod_surumu.yontem=dosya_ozetleri ama ozet yok")
    v = kayit["veri"]
    if not v.get("sha256"):
        raise KayitHatasi("veri.sha256 zorunlu (dosya ozeti ya da uretim tanimi ozeti)")
    cm = kayit["karisiklik_matrisi"]
    if cm.get("duzen") != "[true][pred]":
        raise KayitHatasi("karisiklik_matrisi.duzen '[true][pred]' olmali")
    m = np.asarray(cm.get("matris", []))
    if m.ndim != 2 or m.shape[0] != m.shape[1] or m.size == 0:
        raise KayitHatasi("karisiklik_matrisi.matris kare ve bos olmayan olmali")
    if int(m.sum()) != int(cm.get("n", -1)):
        raise KayitHatasi("karisiklik_matrisi.n matris toplamiyla uyusmuyor")
    if not kayit.get("tahmin_dosyasi"):
        raise KayitHatasi("tahmin_dosyasi zorunlu")
    if not Path(kayit["tahmin_dosyasi"]).exists():
        raise KayitHatasi(f"tahmin dosyasi bulunamadi: {kayit['tahmin_dosyasi']}")
    yk = kayit["yapilandirma_koddan"]
    if not isinstance(yk, dict) or not yk:
        raise KayitHatasi("yapilandirma_koddan bos olamaz (koddan okunmali)")


def _jsonlastir(v):
    if isinstance(v, dict):
        return {str(k): _jsonlastir(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set, frozenset)):
        return [_jsonlastir(x) for x in sorted(v) if True] if isinstance(v, (set, frozenset)) \
            else [_jsonlastir(x) for x in v]
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return repr(v)


# --- CLI ----------------------------------------------------------------
def _cli_dogrula(yollar):
    kotu = 0
    for y in yollar:
        try:
            dogrula(json.loads(Path(y).read_text()))
            print(f"TAMAM   {y}")
        except Exception as e:
            kotu += 1
            print(f"HATA    {y}: {e}")
    if kotu:
        print(f"{kotu} kayit gecersiz")
        sys.exit(1)
    print(f"{len(yollar)} kayit gecerli")


def _smoke():
    """Duman testi: eksiksiz kayit gecer, her zorunlu alanin dusurulmesi hata verir."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        k = KosuKaydi(damar="CDSA-BB3", deney="E0", kol="smoke", tohum=42,
                      kayit_dizini=td)
        k.yapilandirma_koddan("faz_e_kayit", ["SEMA_SURUM", "ZORUNLU"])
        k.veri_uretilmis("smoke-uretici(tohum=42, n=6)", n_kayit=6)
        k.tahminler([0, 0, 1, 1, 2, 2], [0, 1, 1, 1, 2, 0], n_sinif=3)
        p = k.yaz()
        kayit = json.loads(p.read_text())
        assert kayit["metrikler"]["dogruluk"] == round(4 / 6, 4), kayit["metrikler"]
        dogrula(kayit)
        print("  1) eksiksiz kayit dogrulandi:", p.name)
        print("     makro_f1 =", kayit["metrikler"]["makro_f1"],
              " dogruluk =", kayit["metrikler"]["dogruluk"])
        yakalanan = 0
        for alan in ZORUNLU:
            bozuk = json.loads(json.dumps(kayit))
            bozuk.pop(alan)
            try:
                dogrula(bozuk)
                print(f"  ! {alan} dusuruldu ama hata VERMEDI")
            except KayitHatasi:
                yakalanan += 1
        print(f"  2) {yakalanan}/{len(ZORUNLU)} zorunlu alan dusurulunce hata verdi")
        assert yakalanan == len(ZORUNLU)
        # bozuk matris toplami
        bozuk = json.loads(json.dumps(kayit))
        bozuk["karisiklik_matrisi"]["n"] += 1
        try:
            dogrula(bozuk); print("  ! n uyusmazligi yakalanmadi"); sys.exit(1)
        except KayitHatasi:
            print("  3) karisiklik matrisi n uyusmazligi yakalandi")
        # tahmin dosyasi silinince
        bozuk = json.loads(json.dumps(kayit))
        bozuk["tahmin_dosyasi"] = str(td / "yok.json")
        try:
            dogrula(bozuk); print("  ! kayip tahmin dosyasi yakalanmadi"); sys.exit(1)
        except KayitHatasi:
            print("  4) kayip tahmin dosyasi yakalandi")
        ks = kayit["kod_surumu"]
        print(f"  5) kod surumu yontemi = {ks['yontem']}"
              f" head={ks.get('git_head')} agac={ks['kod_agac_ozeti'][:12]}")
    print("SMOKE TAMAM")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    komut = sys.argv[1]
    if komut == "smoke":
        _smoke()
    elif komut == "dogrula":
        _cli_dogrula(sys.argv[2:])
    elif komut == "dogrula-dizin":
        d = Path(sys.argv[2])
        _cli_dogrula([str(p) for p in sorted(d.glob("*.json"))
                      if not p.name.startswith("tahmin_")])
    elif komut == "sema":
        print(json.dumps(SEMA, indent=2, ensure_ascii=False))
    else:
        print("bilinmeyen komut:", komut); sys.exit(2)
