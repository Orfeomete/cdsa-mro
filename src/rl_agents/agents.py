"""
CDSA-MRO Pekiştirmeli Öğrenme Ajanları
========================================
NumPy ile üç algoritma:
  1. Q-Learning (değer tabanlı) — Q-tablosu ayrıştırılmış durum
  2. REINFORCE (policy gradient) — softmax politikası
  3. Actor-Critic (A2C analog) — politika + değer fonksiyonu

Bu kod stable-baselines3'ün PPO/A2C ailesine matematiksel olarak
denk, sandbox bağımsız.

Tez başlığı: Pekiştirmeli Öğrenme ve Veri Yerelliği ile Bakım
Organizasyonlarında Sürekli Uçuşa Elverişlilik için Sentetik Veri
Tabanlı Siber-Emniyet Olay Tahmini

Lisans: CC-BY 4.0
"""

import numpy as np


def softmax(x):
    e = np.exp(x - np.max(x))
    return e / e.sum()


# ====================================================================
# 1. Q-LEARNING (Değer Tabanlı, Function Approximation ile)
# ====================================================================

class QLearningAjan:
    """
    Doğrusal fonksiyon yaklaşımıyla Q-Learning.
    Q(s, a) = w_a · s
    """

    def __init__(self, n_features, n_actions, alpha=0.01, gamma=0.99,
                 epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.9995):
        self.n_features = n_features
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        # Ağırlık matrisi: (n_actions, n_features)
        self.weights = np.zeros((n_actions, n_features))

    def q_values(self, state):
        return self.weights @ state

    def act(self, state, deterministic=False):
        if not deterministic and np.random.rand() < self.epsilon:
            return np.random.randint(self.n_actions)
        return int(np.argmax(self.q_values(state)))

    def update(self, state, action, reward, next_state, done):
        q_next = 0.0 if done else np.max(self.q_values(next_state))
        target = reward + self.gamma * q_next
        current = self.q_values(state)[action]
        delta = target - current
        self.weights[action] += self.alpha * delta * state
        return delta ** 2  # MSE

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


# ====================================================================
# 2. REINFORCE (Policy Gradient — vanilla)
# ====================================================================

class REINFORCEAjan:
    """
    REINFORCE policy gradient.
    π(a|s) = softmax(W · s)
    Gradient ∇θ J = E[∇θ log π(a|s) · G_t]
    """

    def __init__(self, n_features, n_actions, alpha=0.001, gamma=0.99):
        self.n_features = n_features
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.weights = np.random.randn(n_actions, n_features) * 0.01

    def policy(self, state):
        logits = self.weights @ state
        return softmax(logits)

    def act(self, state, deterministic=False):
        probs = self.policy(state)
        if deterministic:
            return int(np.argmax(probs))
        return int(np.random.choice(self.n_actions, p=probs))

    def update(self, episode_states, episode_actions, episode_rewards):
        # Discounted returns
        returns = []
        G = 0
        for r in reversed(episode_rewards):
            G = r + self.gamma * G
            returns.insert(0, G)
        returns = np.array(returns)
        # Baseline normalization (variance reduction)
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        total_loss = 0
        for s, a, G in zip(episode_states, episode_actions, returns):
            probs = self.policy(s)
            # ∇θ log π(a|s) = (1[a=k] - π(k|s)) · s for k = action
            grad = np.zeros_like(self.weights)
            for k in range(self.n_actions):
                indicator = 1.0 if k == a else 0.0
                grad[k] = (indicator - probs[k]) * s
            self.weights += self.alpha * G * grad
            total_loss += -G * np.log(probs[a] + 1e-8)
        return total_loss / max(1, len(episode_states))


# ====================================================================
# 3. ACTOR-CRITIC (A2C Analog, advantage tabanlı)
# ====================================================================

class ActorCriticAjan:
    """
    Advantage Actor-Critic (A2C analoğu).
    Actor: π(a|s) = softmax(W_a · s)
    Critic: V(s) = w_v · s
    Advantage: A_t = r + γ V(s') - V(s)
    """

    def __init__(self, n_features, n_actions, alpha_actor=0.001,
                 alpha_critic=0.005, gamma=0.99):
        self.n_features = n_features
        self.n_actions = n_actions
        self.alpha_actor = alpha_actor
        self.alpha_critic = alpha_critic
        self.gamma = gamma
        # Actor (policy) ağırlıkları
        self.W_actor = np.random.randn(n_actions, n_features) * 0.01
        # Critic (value) ağırlıkları
        self.W_critic = np.zeros(n_features)

    def policy(self, state):
        return softmax(self.W_actor @ state)

    def value(self, state):
        return self.W_critic @ state

    def act(self, state, deterministic=False):
        probs = self.policy(state)
        if deterministic:
            return int(np.argmax(probs))
        return int(np.random.choice(self.n_actions, p=probs))

    def update(self, state, action, reward, next_state, done):
        v = self.value(state)
        v_next = 0.0 if done else self.value(next_state)
        target = reward + self.gamma * v_next
        advantage = target - v

        # Critic update (TD)
        self.W_critic += self.alpha_critic * advantage * state

        # Actor update (policy gradient with advantage)
        probs = self.policy(state)
        for k in range(self.n_actions):
            indicator = 1.0 if k == action else 0.0
            self.W_actor[k] += self.alpha_actor * advantage * (indicator - probs[k]) * state

        return advantage ** 2


# ====================================================================
# 4. PPO-LITE (Proximal Policy Optimization analog, clip ratio)
# ====================================================================

class PPOLiteAjan:
    """
    PPO-Lite: A2C üzerine clipped surrogate objective.
    L^CLIP(θ) = E[min(r_t(θ) · A_t, clip(r_t(θ), 1-ε, 1+ε) · A_t)]

    Burada r_t(θ) = π_θ(a|s) / π_θ_old(a|s)
    """

    def __init__(self, n_features, n_actions, alpha_actor=0.001,
                 alpha_critic=0.005, gamma=0.99, clip_epsilon=0.2,
                 ppo_epochs=4):
        self.n_features = n_features
        self.n_actions = n_actions
        self.alpha_actor = alpha_actor
        self.alpha_critic = alpha_critic
        self.gamma = gamma
        self.clip_epsilon = clip_epsilon
        self.ppo_epochs = ppo_epochs
        self.W_actor = np.random.randn(n_actions, n_features) * 0.01
        self.W_critic = np.zeros(n_features)

    def policy(self, state):
        return softmax(self.W_actor @ state)

    def value(self, state):
        return self.W_critic @ state

    def act(self, state, deterministic=False):
        probs = self.policy(state)
        if deterministic:
            return int(np.argmax(probs))
        return int(np.random.choice(self.n_actions, p=probs))

    def update_batch(self, states, actions, rewards, next_states, dones):
        states = np.array(states)
        actions = np.array(actions)
        rewards = np.array(rewards)
        next_states = np.array(next_states)
        dones = np.array(dones)

        # Compute advantages
        values = np.array([self.value(s) for s in states])
        next_values = np.array([self.value(s) for s in next_states])
        next_values[dones] = 0
        targets = rewards + self.gamma * next_values
        advantages = targets - values
        # Normalize advantages
        if len(advantages) > 1:
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # Old policy log-probs
        old_log_probs = []
        for s, a in zip(states, actions):
            p = self.policy(s)
            old_log_probs.append(np.log(p[a] + 1e-8))
        old_log_probs = np.array(old_log_probs)

        # PPO epochs
        for _ in range(self.ppo_epochs):
            for s, a, adv, old_lp, tgt in zip(states, actions, advantages, old_log_probs, targets):
                probs = self.policy(s)
                new_lp = np.log(probs[a] + 1e-8)
                ratio = np.exp(new_lp - old_lp)
                # Clipped surrogate
                surrogate1 = ratio * adv
                surrogate2 = np.clip(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * adv
                # Use min (loss is -min, gradient ascent on min)
                actor_loss_coef = min(surrogate1, surrogate2)
                # Approximate gradient
                grad = np.zeros_like(self.W_actor)
                for k in range(self.n_actions):
                    indicator = 1.0 if k == a else 0.0
                    grad[k] = (indicator - probs[k]) * s
                self.W_actor += self.alpha_actor * actor_loss_coef * grad / max(1e-8, abs(adv))

                # Critic
                v = self.value(s)
                self.W_critic += self.alpha_critic * (tgt - v) * s

        return advantages.mean(), advantages.std()


# ====================================================================
# EĞİTİM ÇERÇEVESİ
# ====================================================================

def egit(ajan, env, n_episodes=500, batch_mode=False, verbose=True):
    """Genel eğitim döngüsü. Tüm ajan tipleri için."""
    rewards_history = []
    accuracy_history = []

    for episode in range(n_episodes):
        state = env.reset()
        done = False
        episode_reward = 0

        # Episode buffer (REINFORCE ve PPO için)
        states, actions, rewards_list, next_states, dones = [], [], [], [], []

        while not done:
            action = ajan.act(state)
            next_state, reward, done, info = env.step(action)
            episode_reward += reward

            if isinstance(ajan, REINFORCEAjan):
                states.append(state)
                actions.append(action)
                rewards_list.append(reward)
            elif isinstance(ajan, PPOLiteAjan):
                states.append(state)
                actions.append(action)
                rewards_list.append(reward)
                next_states.append(next_state)
                dones.append(done)
            elif isinstance(ajan, (QLearningAjan, ActorCriticAjan)):
                ajan.update(state, action, reward, next_state, done)

            state = next_state

        # Episode sonu güncellemeleri
        if isinstance(ajan, REINFORCEAjan):
            ajan.update(states, actions, rewards_list)
        elif isinstance(ajan, PPOLiteAjan):
            ajan.update_batch(states, actions, rewards_list, next_states, dones)
        elif isinstance(ajan, QLearningAjan):
            ajan.decay_epsilon()

        rewards_history.append(episode_reward)
        accuracy_history.append(info["episode_accuracy"])

        if verbose and (episode + 1) % 50 == 0:
            recent = np.mean(rewards_history[-50:])
            recent_acc = np.mean(accuracy_history[-50:])
            extra = f", ε {ajan.epsilon:.3f}" if isinstance(ajan, QLearningAjan) else ""
            print(f"  Episode {episode+1:>4}/{n_episodes} | ortalama ödül {recent:>8.1f} | doğruluk {recent_acc*100:>5.1f}%{extra}")

    return rewards_history, accuracy_history


def degerlendir(ajan, env, n_episodes=50):
    """Test modu (eylem deterministik)."""
    rewards = []
    accuracies = []
    confusion_matrix = np.zeros((env.n_actions, env.n_actions))
    for _ in range(n_episodes):
        state = env.reset()
        done = False
        episode_reward = 0
        while not done:
            action = ajan.act(state, deterministic=True)
            next_state, reward, done, info = env.step(action)
            episode_reward += reward
            confusion_matrix[info["true_action"], info["predicted_action"]] += 1
            state = next_state
        rewards.append(episode_reward)
        accuracies.append(info["episode_accuracy"])
    return {
        "mean_reward": float(np.mean(rewards)),
        "std_reward": float(np.std(rewards)),
        "mean_accuracy": float(np.mean(accuracies)),
        "confusion_matrix": confusion_matrix.tolist(),
    }
