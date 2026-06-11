# CDSA Scenario C — Paradigm Context for MRO

**Document status:** Reference document supporting the CDSA-MRO v2 update.
**Source decision:** CDSA Methodological Unification Decision (Scenario C, frozen status), 21 May 2026.
**Audience:** Repository users (developers, reviewers, replicators) who need to understand the paradigm positioning of CDSA-MRO.

## 1. Why Scenario C exists

A senior aviation professional reviewing the CDSA-APP framework in May 2026 noted that the three pillars (BB3, MRO, ATM) were using heterogeneous methodologies. This feedback was accepted as academically valid, and on 21 May 2026 the author issued the Scenario C decision: all three CDSA pillars are unified under a Federated Reinforcement Learning (FRL) paradigm with pillar-specific policy network architectures. For CDSA-MRO this means extending the v1.0.0 supervised RL framework with a multi-modal FRL architecture (engine + cyber + maintenance fusion under FedPPO).

## 2. Three-pillar symmetry under FRL

| Dimension | CDSA-BB3 | CDSA-MRO | CDSA-ATM |
|---|---|---|---|
| Domain | Pilot biometrics | Maintenance safety | Air traffic management |
| Policy network | Bi-LSTM (multi-modal) | 1D-CNN + Transformer + LSTM | Multi-Agent PPO (multi-modal) |
| Modalities | PPG + ECG + EEG | Engine + Cyber + Maintenance | Trajectory + ATS + ANSP |
| Federated layer | Pilot consortium | MRO consortium | ANSP consortium |
| XAI | SHAP + counterfactual + LIME | (same) | (same) |
| Privacy | DP (ε ≤ 1.0) + Shamir (2,3) | (same) | (same) |
| Companion journal | JATM Q2 (v8) | RESS Q1 (v2) | CEAS Q2 (v2) |

The paradigm layer (FRL + FedAvg/FedProx), privacy layer (DP + Shamir)
and explainability layer (SHAP + counterfactual + LIME) are **constant
across all three pillars**. What varies is the policy network
architecture, the data modalities, and the federated consortium
structure.

## 3. What v2 changes in this repo

The v2 update is **additive only**. The v1.0.0 release tag remains
valid and reproducible — all v1.0.0 modules and the v1.0.0 reference
data are byte-identical.

The v2 additions are:
- Scaffolded `src/` modules for the FRL extension
  (multimodal, federated, xai)
- This paradigm-context document
- Updated README.md, CHANGELOG.md, CITATION.cff, `.zenodo.json`

The scaffolded modules raise `NotImplementedError` when instantiated;
their implementations are deferred to **TÜBİTAK 1001 ARDEB Project 3**
(September 2026 application cycle; 2027-2030 execution).

## 4. How to read this repo at v1.0.0 vs v2

If you are reading this repo to **reproduce the v1.0.0 results**: use
the v1.0.0 release tag and the existing modules. The scaffolded v2
modules can be ignored.

If you are reading this repo to **understand the paradigm context for
the RESS v2 (Reliability Engineering and System Safety, Q1, in preparation) manuscript or the Safety Science Q1
paradigm-defining article**: use the v2 update notes in README.md and
this paradigm context document.

## 5. Sibling repositories

| Repository | Pillar | Status |
|---|---|---|
| `Orfeomete/cdsa-bb3` | Pilot biometrics | v1.0.0 + v2 scaffold |
| `Orfeomete/cdsa-mro` | Maintenance safety | v1.0.0 + v2 scaffold |
| `Orfeomete/cdsa-atm` | Air traffic management | v1.0.0 + v2 scaffold |
| `Orfeomete/cdsa-site` | Public hub at cdsa.app | active |

## 6. Decision document

The CDSA Methodological Unification Decision (Scenario C) is an
internal frozen-status decision document of Istanbul Beykent
University, dated 21 May 2026. Citations to this document use:

```bibtex
@misc{cantekin2026cdsa_scenario_c,
  author = {Cantekin, Mete},
  title  = {CDSA Methodological Unification Decision (Scenario C, frozen status)},
  year   = 2026,
  month  = may,
  note   = {Internal frozen decision document, Istanbul Beykent University},
  url    = {https://github.com/Orfeomete/cdsa-mro/blob/main/docs/scenario_c_paradigm_context.md}
}
```

---

**Last updated:** 22 May 2026
**Maintainer:** Mete Cantekin (`metecantekin@gmail.com`, ORCID 0009-0001-6990-6340)
