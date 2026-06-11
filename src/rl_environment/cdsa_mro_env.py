"""
CDSA-MRO Pekiştirmeli Öğrenme Ortamı
=====================================
Gymnasium-uyumlu interface ile sentetik veri seti üzerinde
siber-emniyet olay tahmin ortamı.

Tez başlığı: Pekiştirmeli Öğrenme ve Veri Yerelliği ile Bakım
Organizasyonlarında Sürekli Uçuşa Elverişlilik için Sentetik Veri
Tabanlı Siber-Emniyet Olay Tahmini

Markov Decision Process formülasyonu:
  S (State)  : Olay özellik vektörü (10 boyutlu)
  A (Action) : 5 eylem (bekle, düşük uyarı, yüksek uyarı, kritik, eskale)
  R (Reward) : Risk seviyesi ile orantılı, yanlış alarm ve kaçırma cezaları
  γ (Gamma)  : 0.99 (uzun vadeli ödül indirimi)

Lisans: CC-BY 4.0
"""

import json
import random
import numpy as np
from pathlib import Path

# Eylemler
ACTIONS = {
    0: "bekle",
    1: "dusuk_uyari",
    2: "yuksek_uyari",
    3: "kritik_uyari",
    4: "kurumsal_some_eskale",
}

# Olay türü ID haritası (15 tür)
OLAY_TURU_IDS = {
    "oltalama_saldirisi": 0,
    "hesap_ele_gecirme": 1,
    "ot_sistem_sizmasi": 2,
    "fidye_yazilimi": 3,
    "ddos_saldirisi": 4,
    "tedarik_zinciri_kontaminasyonu": 5,
    "usb_zararli_yazilim": 6,
    "shadow_it": 7,
    "konfigurasyon_hatasi": 8,
    "yetki_iptal_eksikligi": 9,
    "egitim_sistem_manipulasyonu": 10,
    "kalibrasyon_butunluk_ihlali": 11,
    "portal_erisim_ihlali": 12,
    "sosyal_muhendislik": 13,
    "is_emri_sahteciligi": 14,
}

# MITRE tactic ID haritası (6 tactic)
MITRE_IDS = {
    "TA0001": 0,  # Initial Access
    "TA0006": 1,  # Credential Access
    "TA0040": 2,  # Impact
    "TA0009": 3,  # Collection
    "TA0007": 4,  # Discovery
    "TA0010": 5,  # Exfiltration
}


class CDSAMROEnv:
    """
    CDSA-MRO Siber-Emniyet Olay Tahmin Ortamı.

    Gymnasium-uyumlu interface (reset/step) ama kendi başına
    NumPy üzerinde çalışır.
    """

    def __init__(self, dataset_path: str, seed: int = 42, max_steps: int = 200):
        self.rng = np.random.default_rng(seed)
        random.seed(seed)
        self.max_steps = max_steps

        # Veri setini yükle
        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)

        # Olay özellik vektörlerini önişle
        self.features = []
        self.labels = []
        for olay in self.dataset:
            self.features.append(self._olaydan_ozellik(olay))
            # Etiket: doğru eylem (risk seviyesi 1-4'ten)
            risk = olay["etiketler"]["risk_seviyesi"]
            self.labels.append(self._risk_to_optimal_action(risk))

        self.features = np.array(self.features, dtype=np.float32)
        self.labels = np.array(self.labels, dtype=np.int64)
        self.n_features = self.features.shape[1]
        self.n_actions = len(ACTIONS)

        # Episode durumu
        self.current_step = 0
        self.current_idx = 0
        self.episode_rewards = []
        self.episode_correct = 0
        self.episode_total = 0

    def _olaydan_ozellik(self, olay: dict) -> list:
        """Bir sentetik olaydan 10 boyutlu özellik vektörü çıkarır."""
        e = olay["etiketler"]
        o = olay["olay_ozeti"]

        # 1-2: Olay türü (15 sınıf → 4 bit one-hot-ish)
        olay_id = OLAY_TURU_IDS.get(o["olay_turu"], 0) / 14.0

        # 3: MITRE tactic
        mitre_id = MITRE_IDS.get(e["mitre_attack"]["tactic"], 0) / 5.0

        # 4: Risk seviyesi - bu hedef etikete sızdırılmaması için kullanılmaz!
        # Yerine: olay belirtilerinden çıkarılacak proxy

        # 5: Etkilenen hizmet sayısı (normalize)
        etkilenen = len(o["etkilenen_hizmetler"]) / 5.0

        # 6: Kesinti süresi (log normalize)
        kesinti = np.log1p(o["kesinti_suresi_dakika"]) / np.log(2500)

        # 7: Maddi kayıp (log normalize)
        kayip = np.log1p(o["tahmini_maddi_kayip_TL"]) / np.log(500000)

        # 8: KVKK özel veri
        kvkk = 1.0 if e["kvkk_ozel_veri_iceriyor"] else 0.0

        # 9: 72 saat bildirim uyumu
        bildirim = 1.0 if e["shy145_madde18_72saat_uygunluk"] else 0.0

        # 10: Ek-19 kontrol noktası sayısı (normalize)
        ek19_n = len(e["shtsiber_ek19_kontrol_atfi"]) / 5.0

        # 11: Swiss cheese katman sayısı (normalize)
        swiss = len(olay["kok_neden_analizi"]["swiss_cheese_katmanlari"]) / 6.0

        # 12: Aksiyon sayısı (normalize)
        aksiyon = len(olay["aksiyonlar"]) / 5.0

        return [olay_id, mitre_id, etkilenen, kesinti, kayip, kvkk,
                bildirim, ek19_n, swiss, aksiyon]

    def _risk_to_optimal_action(self, risk: int) -> int:
        """Risk seviyesinden 'optimal' eylem haritası."""
        return {1: 1, 2: 2, 3: 3, 4: 4}.get(risk, 0)

    def reset(self):
        """Yeni episode başlat. İlk gözlemi döndür."""
        self.current_step = 0
        self.current_idx = int(self.rng.integers(0, len(self.features)))
        self.episode_rewards = []
        self.episode_correct = 0
        self.episode_total = 0
        return self.features[self.current_idx].copy()

    def step(self, action: int):
        """
        Eylem uygula, ödül hesapla, sonraki durumu döndür.

        Returns:
          (next_state, reward, done, info)
        """
        true_action = self.labels[self.current_idx]

        # ÖDÜL fonksiyonu
        reward = 0.0

        if action == true_action:
            # Doğru tahmin
            reward = 10.0 + true_action * 2  # Kritik seviyede daha yüksek ödül
            self.episode_correct += 1
        elif action == 0 and true_action != 0:
            # Olay var, bekledi (kaçırma)
            reward = -20.0 * (true_action + 1)
        elif action != 0 and true_action == 0:
            # Olay yok, yanlış alarm
            reward = -5.0
        elif action > true_action:
            # Aşırı tepki (false positive ama hafif)
            reward = -3.0 * (action - true_action)
        else:
            # Yetersiz tepki
            reward = -7.0 * (true_action - action)

        # SHY-145 Madde 18 72 saat bonus
        olay = self.dataset[self.current_idx]
        if olay["etiketler"]["shy145_madde18_72saat_uygunluk"] and action >= 2:
            reward += 2.0

        self.episode_total += 1
        self.episode_rewards.append(reward)
        self.current_step += 1

        # Sonraki olay
        self.current_idx = int(self.rng.integers(0, len(self.features)))
        next_state = self.features[self.current_idx].copy()

        done = self.current_step >= self.max_steps
        info = {
            "true_action": int(true_action),
            "predicted_action": int(action),
            "correct": int(action == true_action),
            "episode_accuracy": self.episode_correct / max(1, self.episode_total),
        }
        return next_state, reward, done, info

    def render(self):
        """Mevcut durumu yazdır."""
        olay = self.dataset[self.current_idx]
        print(f"  Olay {olay['olay_id']} | tür {olay['olay_ozeti']['olay_turu']} | risk {olay['etiketler']['risk_seviyesi']}")


if __name__ == "__main__":
    env = CDSAMROEnv("data/synthetic_incidents_v1.json")
    print(f"Ortam yüklendi.")
    print(f"  Veri seti boyutu: {len(env.dataset)}")
    print(f"  Özellik boyutu: {env.n_features}")
    print(f"  Eylem sayısı: {env.n_actions}")
    print(f"  İlk özellik vektörü: {env.features[0]}")
    print(f"  İlk etiket: {env.labels[0]}")

    # Test episode
    state = env.reset()
    total_reward = 0
    for i in range(10):
        action = int(env.rng.integers(0, env.n_actions))
        state, reward, done, info = env.step(action)
        total_reward += reward
        if done:
            break
    print(f"\n10 rastgele adım sonucu: toplam ödül {total_reward:.2f}, doğruluk {info['episode_accuracy']*100:.1f}%")
