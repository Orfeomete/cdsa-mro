"""
CDSA-MRO RL Eğitim Çalıştırıcı
================================
Tüm dört ajanı (Q-Learning, REINFORCE, A2C, PPO-Lite) sentetik veri
seti üzerinde eğitir ve sonuçları karşılaştırır.

Kullanım:
  python3 03_Egitim_Calistir.py [n_episodes]
"""

import sys
import json
import os
import time
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util

def yukle_modul(yol, ad):
    spec = importlib.util.spec_from_file_location(ad, yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

base_dir = os.path.dirname(os.path.abspath(__file__))
ortam_m = yukle_modul(os.path.join(base_dir, "01_Ortam.py"), "ortam")
ajan_m = yukle_modul(os.path.join(base_dir, "02_RL_Ajanlari.py"), "ajanlar")

CDSAMROEnv = ortam_m.CDSAMROEnv
QLearningAjan = ajan_m.QLearningAjan
REINFORCEAjan = ajan_m.REINFORCEAjan
ActorCriticAjan = ajan_m.ActorCriticAjan
PPOLiteAjan = ajan_m.PPOLiteAjan
egit = ajan_m.egit
degerlendir = ajan_m.degerlendir

DATASET_PATH = "data/synthetic_incidents_v1.json"
CIKTI_DIR = "results"


def main(n_episodes=500):
    print(f"CDSA-MRO RL Eğitim Çerçevesi")
    print(f"  Veri seti: {DATASET_PATH}")
    print(f"  Episode sayısı: {n_episodes}")
    print(f"  Episode başına max adım: 100")
    print()

    sonuclar = {}

    # ---- 1. Q-LEARNING ----
    print("=" * 60)
    print("1/4 — Q-Learning (Değer Tabanlı)")
    print("=" * 60)
    env = CDSAMROEnv(DATASET_PATH, seed=42, max_steps=100)
    np.random.seed(42)
    ajan = QLearningAjan(env.n_features, env.n_actions,
                          alpha=0.01, gamma=0.99, epsilon=1.0,
                          epsilon_min=0.05, epsilon_decay=0.9985)
    t0 = time.time()
    rh, ah = egit(ajan, env, n_episodes=n_episodes, verbose=True)
    sure = time.time() - t0
    print(f"\n  Test değerlendirme...")
    test = degerlendir(ajan, env, n_episodes=50)
    sonuclar["q_learning"] = {
        "egitim_suresi_sn": sure,
        "rewards_history": rh,
        "accuracy_history": ah,
        "test": test,
        "weights": ajan.weights.tolist(),
    }
    print(f"  Eğitim süresi: {sure:.1f} sn")
    print(f"  Test ortalama ödül: {test['mean_reward']:.1f}")
    print(f"  Test doğruluk: {test['mean_accuracy']*100:.1f}%")
    print()

    # ---- 2. REINFORCE ----
    print("=" * 60)
    print("2/4 — REINFORCE (Policy Gradient)")
    print("=" * 60)
    env = CDSAMROEnv(DATASET_PATH, seed=42, max_steps=100)
    np.random.seed(42)
    ajan = REINFORCEAjan(env.n_features, env.n_actions,
                          alpha=0.005, gamma=0.99)
    t0 = time.time()
    rh, ah = egit(ajan, env, n_episodes=n_episodes, verbose=True)
    sure = time.time() - t0
    print(f"\n  Test değerlendirme...")
    test = degerlendir(ajan, env, n_episodes=50)
    sonuclar["reinforce"] = {
        "egitim_suresi_sn": sure,
        "rewards_history": rh,
        "accuracy_history": ah,
        "test": test,
        "weights": ajan.weights.tolist(),
    }
    print(f"  Eğitim süresi: {sure:.1f} sn")
    print(f"  Test ortalama ödül: {test['mean_reward']:.1f}")
    print(f"  Test doğruluk: {test['mean_accuracy']*100:.1f}%")
    print()

    # ---- 3. ACTOR-CRITIC (A2C analog) ----
    print("=" * 60)
    print("3/4 — Actor-Critic (A2C analog)")
    print("=" * 60)
    env = CDSAMROEnv(DATASET_PATH, seed=42, max_steps=100)
    np.random.seed(42)
    ajan = ActorCriticAjan(env.n_features, env.n_actions,
                           alpha_actor=0.005, alpha_critic=0.01, gamma=0.99)
    t0 = time.time()
    rh, ah = egit(ajan, env, n_episodes=n_episodes, verbose=True)
    sure = time.time() - t0
    print(f"\n  Test değerlendirme...")
    test = degerlendir(ajan, env, n_episodes=50)
    sonuclar["a2c"] = {
        "egitim_suresi_sn": sure,
        "rewards_history": rh,
        "accuracy_history": ah,
        "test": test,
        "actor_weights": ajan.W_actor.tolist(),
        "critic_weights": ajan.W_critic.tolist(),
    }
    print(f"  Eğitim süresi: {sure:.1f} sn")
    print(f"  Test ortalama ödül: {test['mean_reward']:.1f}")
    print(f"  Test doğruluk: {test['mean_accuracy']*100:.1f}%")
    print()

    # ---- 4. PPO-LITE ----
    print("=" * 60)
    print("4/4 — PPO-Lite (Clipped Policy)")
    print("=" * 60)
    env = CDSAMROEnv(DATASET_PATH, seed=42, max_steps=100)
    np.random.seed(42)
    ajan = PPOLiteAjan(env.n_features, env.n_actions,
                       alpha_actor=0.003, alpha_critic=0.01,
                       gamma=0.99, clip_epsilon=0.2, ppo_epochs=4)
    t0 = time.time()
    rh, ah = egit(ajan, env, n_episodes=n_episodes, verbose=True)
    sure = time.time() - t0
    print(f"\n  Test değerlendirme...")
    test = degerlendir(ajan, env, n_episodes=50)
    sonuclar["ppo_lite"] = {
        "egitim_suresi_sn": sure,
        "rewards_history": rh,
        "accuracy_history": ah,
        "test": test,
        "actor_weights": ajan.W_actor.tolist(),
        "critic_weights": ajan.W_critic.tolist(),
    }
    print(f"  Eğitim süresi: {sure:.1f} sn")
    print(f"  Test ortalama ödül: {test['mean_reward']:.1f}")
    print(f"  Test doğruluk: {test['mean_accuracy']*100:.1f}%")
    print()

    # Sonuçları kaydet
    Path(CIKTI_DIR).mkdir(parents=True, exist_ok=True)
    out_path = os.path.join(CIKTI_DIR, "egitim_sonuclari.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sonuclar, f, ensure_ascii=False, indent=2)
    print(f"Sonuçlar kaydedildi: {out_path}")

    # Özet tablo
    print()
    print("=" * 60)
    print("KARŞILAŞTIRMA ÖZETİ")
    print("=" * 60)
    print(f"{'Algoritma':<20} {'Süre':>8} {'Ortalama Ödül':>15} {'Doğruluk':>10}")
    print("-" * 60)
    for ad, s in sonuclar.items():
        print(f"{ad:<20} {s['egitim_suresi_sn']:>6.1f}sn {s['test']['mean_reward']:>15.1f} {s['test']['mean_accuracy']*100:>9.1f}%")

    return sonuclar


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    main(n_episodes=n)
