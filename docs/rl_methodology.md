# Reinforcement Learning Methodology — CDSA-MRO

## Overview

The CDSA-MRO framework formulates the cyber-safety incident prediction
problem as a Markov Decision Process (MDP) and evaluates four
reinforcement learning algorithms on synthetic data.

## Markov Decision Process Formulation

`M = (S, A, P, R, gamma)` where:

### State Space S

A 10-dimensional continuous feature vector representing each incident:

| Feature | Encoding | Range |
|---|---|---|
| Incident type | 15 types → identifier / 14 | [0, 1] |
| MITRE ATT&CK tactic | 6 tactics → identifier / 5 | [0, 1] |
| Affected service count | count / 5 | [0, 1] |
| Downtime (minutes) | log(1+t) / log(2500) | [0, ~1] |
| Monetary loss (TL) | log(1+kayip) / log(500K) | [0, ~1] |
| KVKK special-data flag | binary | {0, 1} |
| 72-hour notification compliance flag | binary | {0, 1} |
| Annex 19 control reference count | count / 5 | [0, 1] |
| Swiss-cheese organisational layers | count / 6 | [0, 1] |
| Recommended action count | count / 5 | [0, 1] |

### Action Space A

Five discrete actions corresponding to escalating intervention levels:

| Action | Meaning |
|---|---|
| 0 — `wait` | No action; continue monitoring. |
| 1 — `low_alert` | Issue a low-severity alert. |
| 2 — `high_alert` | Issue a high-severity alert. |
| 3 — `critical_alert` | Issue a critical-severity alert. |
| 4 — `csirt_escalate` | Escalate to the Corporate Computer Emergency Response Team. |

This action set mirrors the operational decision hierarchy expected of
a Cyber-Safety Responsible Manager (SGSYY) under SHT-SIBER Article 12.

### Reward Function R

The reward function internalises regulatory priorities:

- **Correct prediction:** +10, plus severity bonus (+2 × severity for
  critical alerts).
- **False alarm** (action > 0 but ground truth = 0): -5.
- **Missed incident** (action = 0 but ground truth > 0): -20 × (severity + 1).
- **Over-reaction** (action > ground truth): -3 × magnitude gap.
- **Under-reaction** (0 < action < ground truth): -7 × magnitude gap.
- **72-hour compliance bonus:** +2 if the agent issues at least a
  high-severity alert in a scenario flagged as compliant with
  SHY-145 Article 18.

### Discount Factor

gamma = 0.99.

## Algorithms Evaluated

Four algorithms are implemented with linear function approximation in
NumPy. This linear-approximation version is the "lite" baseline; v2.0
will provide deep PyTorch implementations.

### 1. Q-Learning

Value-based method with linear function approximation:

`Q(s, a) = w_a · s`

- Learning rate alpha = 0.01
- Exploration: epsilon-greedy, epsilon decays from 1.0 to 0.05 with
  factor 0.9985 per episode.
- Update: standard TD(0) Q-learning step.

### 2. REINFORCE

Vanilla Monte Carlo policy gradient with softmax policy:

`pi(a | s) = softmax(W · s)`

- Learning rate alpha = 0.005
- Episode returns G_t computed via discounted reverse sum.
- Baseline normalisation (mean/std) applied for variance reduction.
- Gradient: `∇θ log π(a|s) · G_t` for each (state, action, return).

### 3. Actor-Critic (A2C analog)

Advantage actor-critic:

- Actor: softmax policy with weights `W_actor`.
- Critic: linear value function `V(s) = w_critic · s`.
- Advantage estimate: `A_t = r + gamma · V(s') - V(s)`.
- Actor learning rate alpha = 0.005, critic alpha = 0.01.

### 4. PPO-Lite (Clipped Policy Optimization)

Proximal policy optimisation with linear policy:

- Ratio `r_t(θ) = pi_θ(a|s) / pi_θ_old(a|s)`.
- Clipped surrogate loss `L^CLIP = E[min(r_t · A_t, clip(r_t, 1-ε, 1+ε) · A_t)]`.
- Clip epsilon = 0.2, PPO epochs = 4 per update.
- Actor lr 0.003, critic lr 0.01.

## Training Configuration

- **Episodes:** 300
- **Max steps per episode:** 100
- **Total training steps:** up to 30,000
- **Random seed:** 42 (deterministic across all algorithms)
- **Evaluation episodes:** 50 (deterministic / greedy action selection)
- **Hardware:** Single-CPU node, NumPy 1.26, Python 3.10
- **Total training time:** ~9 seconds for all 4 algorithms combined

## Evaluation Metrics

- **Mean episode reward** — aggregate reward across 50 test episodes.
- **Mean per-step accuracy** — fraction of correct action predictions.
- **Confusion matrix** — 5×5 predicted vs. true action.
- **Regulatory compliance rate** — fraction of compliant scenarios
  receiving at least a high-severity alert.

## Results Summary

| Algorithm | Reward | Accuracy | Training Time |
|---|---|---|---|
| Q-Learning | 654.8 | 47.7% | 0.5 s |
| REINFORCE | 528.2 | 43.3% | 1.7 s |
| Actor-Critic | 731.2 | 42.7% | 1.5 s |
| **PPO-Lite** | **872.1** | **54.0%** | **5.1 s** |

PPO-Lite achieves the highest performance on both reward and accuracy,
consistent with the broader RL literature on clipped policy gradient
stability.

## Comparison with Random Baseline

On a 5-class decision problem, the random baseline accuracy is 20%.
PPO-Lite achieves a **2.7-fold improvement** over random, while all
four algorithms exceed the baseline by significant margins.

## Limitations

- **Linear function approximation:** No deep neural network policy in
  v1.0. v2.0 will use PyTorch-based deep policies.
- **Short training:** 30K timesteps is short; v2.0 targets 1M+
  timesteps with hyperparameter search.
- **Single seed:** v2.0 will include 5-seed variance analysis.
- **No federated learning:** v2.1 will add federated learning extension
  to compare against the strict data-locality regime.

## Future Work

- **v2.0 PyTorch deep policy** — Stable-Baselines3 PPO with MLP/Conv
  policy networks.
- **v2.1 Federated learning** — Compare 5 simulated MROs federated vs.
  pure data-locality.
- **v2.2 Explainability** — SHAP and integrated gradients on the
  PyTorch policy.
- **v3.0 Real-world deployment** — Field study with a Turkish Part-145
  operator under TÜBİTAK funding.
