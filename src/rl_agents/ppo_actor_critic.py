"""
PPO Actor-Critic for CDSA-MRO — NumPy reference implementation (v2).

Reference: Schulman et al. (2017), Proximal Policy Optimization
Algorithms, arXiv:1707.06347.

Compact shared-trunk actor-critic:
  h      = tanh(W1 s + b1)
  logits = Wa h + ba          (actor: softmax over n_actions)
  value  = Wv h + bv          (critic: scalar)

Update: clipped surrogate objective (clip eps), GAE(lambda) advantages,
manual NumPy gradients, simple SGD. Parameters are exposed as a tree
(params/set_params) for FedAvg/FedProx exchange.

Scope note (Faz A): CPU-scale reference implementation used in the
three-MRO consortium simulation. Framework-scale training is planned
under TUBITAK 1001 ARDEB Project 3 (Faz B).
"""

from __future__ import annotations

import numpy as np


def _softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


class PPOActorCritic:
    """Discrete-action PPO agent over a fused state representation."""

    def __init__(self, fused_dim: int = 64, n_actions: int = 5,
                 hidden: int = 64, lr: float = 3e-4, gamma: float = 0.99,
                 gae_lambda: float = 0.95, clip_eps: float = 0.2,
                 reward_scale: float = 1.0, max_grad_norm: float = 10.0,
                 seed: int = 42):
        self.fused_dim, self.n_actions = fused_dim, n_actions
        self.lr, self.gamma = lr, gamma
        self.gae_lambda, self.clip_eps = gae_lambda, clip_eps
        self.reward_scale = float(reward_scale)
        self.max_grad_norm = float(max_grad_norm)
        rng = np.random.default_rng(seed)
        s1 = 1.0 / np.sqrt(fused_dim)
        sh = 1.0 / np.sqrt(hidden)
        self.W1 = rng.normal(0, s1, (hidden, fused_dim))
        self.b1 = np.zeros(hidden)
        self.Wa = rng.normal(0, sh, (n_actions, hidden))
        self.ba = np.zeros(n_actions)
        self.Wv = rng.normal(0, sh, (1, hidden))
        self.bv = np.zeros(1)
        self.rng = rng

    # -- forward ---------------------------------------------------------
    def _trunk(self, s):
        return np.tanh(self.W1 @ np.asarray(s, dtype=float) + self.b1)

    def policy(self, s):
        return _softmax(self.Wa @ self._trunk(s) + self.ba)

    def value(self, s) -> float:
        return float((self.Wv @ self._trunk(s) + self.bv)[0])

    def act(self, s, deterministic: bool = False):
        p = self.policy(s)
        a = int(np.argmax(p)) if deterministic else int(self.rng.choice(self.n_actions, p=p))
        return a, float(np.log(p[a] + 1e-12)), self.value(s)

    # -- GAE ---------------------------------------------------------------
    def compute_gae(self, rewards, values, dones, last_value: float = 0.0):
        rewards = [r * self.reward_scale for r in rewards]
        T = len(rewards)
        adv = np.zeros(T)
        gae = 0.0
        for t in reversed(range(T)):
            nxt = last_value if t == T - 1 else values[t + 1]
            nonterm = 0.0 if dones[t] else 1.0
            delta = rewards[t] + self.gamma * nxt * nonterm - values[t]
            gae = delta + self.gamma * self.gae_lambda * nonterm * gae
            adv[t] = gae
        returns = adv + np.asarray(values, dtype=float)
        return adv, returns

    # -- clipped-surrogate update ------------------------------------------
    def update(self, states, actions, old_logps, advantages, returns,
               epochs: int = 4):
        states = np.asarray(states, dtype=float)
        actions = np.asarray(actions, dtype=int)
        old_logps = np.asarray(old_logps, dtype=float)
        adv = np.asarray(advantages, dtype=float)
        adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        rets = np.asarray(returns, dtype=float)
        N = len(actions)
        last_loss = 0.0
        for _ in range(epochs):
            gW1 = np.zeros_like(self.W1); gb1 = np.zeros_like(self.b1)
            gWa = np.zeros_like(self.Wa); gba = np.zeros_like(self.ba)
            gWv = np.zeros_like(self.Wv); gbv = np.zeros_like(self.bv)
            last_loss = 0.0
            for i in range(N):
                s = states[i]
                h = self._trunk(s)
                logits = self.Wa @ h + self.ba
                p = _softmax(logits)
                a = actions[i]
                logp = np.log(p[a] + 1e-12)
                ratio = np.exp(logp - old_logps[i])
                clipped = np.clip(ratio, 1 - self.clip_eps, 1 + self.clip_eps)
                # policy gradient only flows through unclipped branch
                use_grad = (ratio * adv[i]) <= (clipped * adv[i])
                v = float((self.Wv @ h + self.bv)[0])
                v_err = v - rets[i]
                last_loss += -min(ratio * adv[i], clipped * adv[i]) + 0.5 * v_err ** 2
                # actor grads: dlogp/dlogits = onehot - p
                if use_grad:
                    dlogits = -(ratio * adv[i]) * (_onehot(a, self.n_actions) - p)
                    gWa += np.outer(dlogits, h); gba += dlogits
                    dh_a = self.Wa.T @ dlogits
                else:
                    dh_a = np.zeros_like(h)
                # critic grads
                dv = v_err
                gWv += dv * h[None, :]; gbv += np.array([dv])
                dh = dh_a + dv * self.Wv.ravel()
                dz = dh * (1 - h ** 2)
                gW1 += np.outer(dz, s); gb1 += dz
            grads = ((gW1, "W1"), (gb1, "b1"), (gWa, "Wa"),
                     (gba, "ba"), (gWv, "Wv"), (gbv, "bv"))
            gnorm = np.sqrt(sum(float((g * g).sum()) for g, _ in grads)) / N
            scale = (self.max_grad_norm / gnorm) if gnorm > self.max_grad_norm else 1.0
            for g, m in grads:
                setattr(self, m, getattr(self, m) - self.lr * scale * g / N)
        return last_loss / N

    # -- federated exchange --------------------------------------------------
    def params(self) -> dict:
        return {"W1": self.W1, "b1": self.b1, "Wa": self.Wa,
                "ba": self.ba, "Wv": self.Wv, "bv": self.bv}

    def set_params(self, p: dict) -> None:
        for n in ("W1", "b1", "Wa", "ba", "Wv", "bv"):
            setattr(self, n, np.asarray(p[n], dtype=float).copy())


def _onehot(a: int, n: int) -> np.ndarray:
    v = np.zeros(n)
    v[a] = 1.0
    return v
