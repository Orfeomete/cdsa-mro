"""Faz A / A6 run configuration — CDSA-MRO pillar (siber-emniyet karar gorevi).

Not: Bu kosu v1 tek-modlu siber-emniyet karar gorevinin FEDERE halidir.
Cok-modlu C-MAPSS kurgusu gercek motor verisi gerektirir ve Faz B'dedir
(TUBITAK Proje 3). Non-IID heterojenlik: istemciler ayni sentetik korpusu
farkli kayit sirasi/baslangiciyla gorur (veri-sirasi heterojenligi).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "rl_environment"))
from cdsa_mro_env import CDSAMROEnv

PILLAR = "CDSA-MRO"
N_ACTIONS = 5
STATE_DIM = 10
NEW_STEP_API = False
INFO_TRUE_KEY = "true_action"
ACTION_LABELS = ["izleme_devam", "uyari_olustur", "ic_sorusturma",
                 "some_mudahale", "shgm_72saat_bildirim"]
MODALITY_GROUPS = {}   # tek-modlu gorev — grup-Shapley Faz B'de

_DATA = str(Path(__file__).parent.parent / "data" / "synthetic_incidents_v1.json")


def make_env(seed: int):
    return CDSAMROEnv(_DATA, seed=seed, max_steps=10_000)


def make_client_envs(seed: int):
    return [CDSAMROEnv(_DATA, seed=seed + 17 * i, max_steps=10_000)
            for i in range(3)]

CRITICAL_ACTIONS = set((3, 4))
