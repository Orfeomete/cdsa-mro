# Changelog

## [2.2.0-dev] — 2026-07-03 (unreleased)

### Added (Faz B/C/D revision-preparation experiments; seeded, CPU-scale)
- Faz B: inference-time robustness + confusion-matrix evaluation and a
  tempo-aware-reward retraining experiment — `experiments/faz_b_robustness.py`,
  `experiments/faz_b_dynamic_reward.py` + seeded output JSONs under
  `experiments/results/`.
- Faz C: differential-privacy ε sweep (ε = 0.5 / 2.0) and entropy-targeted
  exploration (coef 0.01 / 0.05), each a separate 160-round FedProx
  retraining — `experiments/faz_c_dp_sweep.py`, `experiments/faz_c_entropy.py`
  + output JSONs.
- Faz D: decoy-signal (group-Shapley) attribution test and
  recall-floor-gated exploration — `experiments/faz_d_decoy.py`,
  `experiments/faz_d_gated_entropy.py` + output JSONs.
- Per-phase result panels with honesty bands at https://cdsa.app/mro/.

### Findings (honest summary — numbers verbatim from `experiments/results/*.json`)
- All Faz B robustness conditions and the tempo-aware-reward retraining
  reproduce the constant-action policy (accuracy 42.7%, critical recall
  0.494, one of five actions used) — Faz A rows should not be read as
  evidence of task mastery.
- Faz C: the ε conditions and 0.01 entropy leave the policy unchanged;
  a 0.05 entropy bonus breaks the single-action collapse for the first
  time (two of five actions, accuracy 53.0%, critical recall 0.613) —
  a partial but real improvement.
- Faz D: the exploration gate never opens (gate_on ratio 0.0 — the 0.90
  critical-recall floor is never reached); decoy attribution is 11.1%,
  to be read over near-constant outputs.

### Unchanged
- Published core code, environments and Faz A outputs — no behavioural
  changes.
- The v2.1.0 release and its Zenodo DOI remain valid; no new release or
  DOI is cut for this section (deferred to the acceptance/revision stage).

## [2.0.0-scaffold] — 2026-05-22

### Added (Scenario C paradigm alignment, additive only)
- README.md: new "Paradigm Context — CDSA Scenario C" section
  positioning CDSA-MRO as the maintenance safety pillar of the
  three-pillar Federated Reinforcement Learning (FRL) research
  programme.
- `src/multimodal/` (scaffold)
- `src/federated/` (scaffold)
- `src/xai/` (scaffold)
- `docs/scenario_c_paradigm_context.md` — full paradigm context
  reference document.
- `CITATION.cff`: added FRL/multi-modal/XAI/CDSA-paradigm keywords,
  Scenario C decision reference, sibling article references.
- `.zenodo.json`: added paradigm keywords and related-identifier
  entries for the three-pillar sibling repos.

### Not Changed
- v1.0.0 modules byte-identical to the v1.0.0 release. The v1.0.0
  release tag remains valid and reproducible.
- Reference data unchanged.
- Existing tests pass.
- Authorship policy (single-author per the CDSA Authorship Rule)
  unchanged.

### Notes
- The v2 scaffolded modules raise `NotImplementedError` when
  instantiated. Treat them as **architectural commitments**, not
  as runnable code at v2-scaffold stage.
- Full implementations of the scaffolded modules are deferred to
  TÜBİTAK 1001 ARDEB Project 3 (Sept 2026 application cycle;
  2027-2030 execution).
- The v2.0.0 final release is planned for Q4 2026 following
  TÜBİTAK project acceptance.

## [1.0.0] — 2026-05-15

### Initial Release
- CDSA-MRO Synthetic Data Generation Engine (CDSA-MRO-SDG v2.0)
- 1000-record synthetic incident dataset (deterministic, seed=42)
- Gymnasium-compatible CDSA-MRO environment
- Four reinforcement learning agents: Q-Learning, REINFORCE,
  Actor-Critic, PPO-Lite
- Modified Delphi validation protocol (20 stratified samples)
- 15 incident scenario types aligned with SHT-SIBER Annex 13
- Regulatory alignment metadata: Annex 19, Annex 21, MITRE ATT&CK,
  KVKK Article 6, SHY-145 Article 18
- Differential privacy guarantee (epsilon = 0.8)
- Full open-source release under MIT (code) and CC BY 4.0 (data)

### Documentation
- README with quick start
- Synthetic data design document
- RL methodology document
- Validation protocol document
- Example scripts (quick_start.py, reproduce_results.py)

### Known Limitations
- Linear function approximation; deep neural policy in v2.0
- 30K training timesteps; v2.0 targets 1M+ timesteps
- Single random seed; v2.0 will include 5-seed variance analysis
- Delphi panel: 3-5 experts; v2.0 will report results

## [Roadmap]

### [1.1.0] — Target 2026-06-30
- Modified Delphi panel completion (3 rounds)
- Aggregate scores and consensus analysis
- Updated arXiv preprint v2

_(Roadmap renumbered 2026-06-12: the CPU-scale reference implementation of the planned 2.1.0 federated/XAI items shipped early as the actual 2.1.0 release below; framework-scale items move to 2.2.0/2.3.0.)_

### [2.2.0] — Target 2026-Q4 (framework-scale)
- PyTorch deep policy networks
- Stable-Baselines3 PPO integration
- 1M+ training timesteps
- Hyperparameter search (Optuna)

### [2.3.0] — Target 2027-Q1 (federated extension at scale)
- Federated learning extension (5 simulated MROs)
- SHAP-based explainability layer
- Integrated gradients

### [3.0.0] — Target 2027
- Field deployment study with a Turkish Part-145 operator
- TÜBİTAK-funded validation
- Anonymised production data integration

## [2.1.0] — 2026-06-12 (Faz A implementation)
### Added
- `src/federated/`: FedAvgAggregator + FedProxAggregator NumPy reference
  implementations (data-weighted aggregation, Laplace DP hook, proximal
  penalty/grad utilities). Replaces v2.0.0-scaffold stubs.
- `src/multimodal/`: EngineEncoder (1D-CNN+LSTM), CyberEncoder
  (self-attention), MaintEncoder (LSTM) + CrossModalAttentionFusion
  (gating + scaled dot-product attention) — CPU-scale NumPy forward
  implementations with federated param get/set.
- `src/xai/`: SHAPModalityExplainer (exact 2^3-coalition Shapley),
  CounterfactualExplainer (modality ablation, auditor JSON),
  LIMEExplainer (weighted ridge surrogate).
- `tests/test_v2_modules.py`: 9 unit tests covering all v2 modules.
### Notes
- Faz A scope: CPU-scale reference implementations (zero server cost).
  Framework-scale training remains under TUBITAK 1001 Project 3 (Faz B).

### Changed (11 Jun 2026, A6 runs)
- PPOActorCritic: reward_scale + global gradient-norm clipping.
- experiments/: faz_a_staged.py + faz_a_config.py + results/ (seeded,
  checkpointed CPU-scale federated runs; see CDSA_FazA_A6 report).
