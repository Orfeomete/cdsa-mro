# CDSA-MRO — Synthetic Data Generation and Reinforcement Learning

**A Reinforcement-Learning and Data-Locality-Based Cyber-Safety Incident
Prediction Framework for Continuing Airworthiness in Aviation
Maintenance Organisations Using Synthetic Data.**

[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-orange.svg)](LICENSE-DATA)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org)
[![arXiv](https://img.shields.io/badge/arXiv-preprint-red.svg)](#)
[![DOI](https://img.shields.io/badge/DOI-pending-yellow.svg)](#)

---

## Overview

CDSA-MRO is an open-source framework that addresses a structural gap
in aviation maintenance cyber-safety research: real operational data
from Part-145 approved maintenance organisations is largely
inaccessible due to trade secret protection. CDSA-MRO overcomes this
gap through three coordinated components:

1. **Data-Locality Architecture** — no data is ever requested from
   maintenance organisations.
2. **Synthetic Data Generation Engine (CDSA-MRO-SDG)** — produces
   incident records aligned with the SHGM SHT-SIBER Annex 13
   standard format.
3. **Reinforcement Learning Early-Warning Model** — trained on the
   synthetic data. The principal policy network uses **Proximal
   Policy Optimization (PPO)**; three baselines (Q-Learning,
   REINFORCE, Actor-Critic) are evaluated under identical
   conditions for comparison. PPO-Lite attains 54.0% test accuracy,
   2.7× the random baseline.

The accompanying doctoral thesis (CDSA-MRO_Tez_v2, Istanbul Beykent
University, Department of Computer Engineering, May 2026) presents
the full framework in Turkish. The thesis positions the data-locality
regime as **v1 — pure locality** (the configuration in this
repository) with a roadmap to **v2 — federated extension** under
the TÜBİTAK 1001 ARDEB Project 3 application (September 2026).

The framework is released as open source to enable reproducibility,
comparison, and sectoral adoption.

---

## Paradigm Context — CDSA Scenario C (v2 update, 22 May 2026)

Following the **CDSA Methodological Unification Decision (Scenario C,
frozen status, 21 May 2026)**, this CDSA-MRO module is positioned
as the **maintenance safety pillar** of a three-pillar **Federated
Reinforcement Learning (FRL)** research programme:

| Pillar | Domain | Companion repo | Companion journal article |
|---|---|---|---|
| **CDSA-BB3** | Pilot biometrics | `Orfeomete/cdsa-bb3` | JATM v8 (Q2, in submission) |
| **CDSA-MRO** | Maintenance safety | `Orfeomete/cdsa-mro` | RESS v2 (Q1, in preparation) |
| **CDSA-ATM** | Air traffic management | `Orfeomete/cdsa-atm` | CEAS v2 (Q2, in preparation) |

This **CDSA-MRO** repository implements the maintenance safety
pillar with a **Multi-modal CNN + Transformer + LSTM** policy network operating
over **Engine + Cyber + Maintenance** modalities and a federated layer
designed for a MRO consortium (MRO-A, MRO-B, MRO-C (simulated three-MRO consortium)).
The sibling pillars are CDSA-BB3 (pilot biometrics, JATM Q2 v8 in submission) and the parallel ATM pillar; together they provide convergent
validation across three independent aviation domains.

A paradigm-defining umbrella article (Safety Science Q1, September 2026
submission target) positions the three pillars under a common
diagnostic-safety paradigm with quantitative convergent validation
evidence across the three domains.

The current `src/` layout retains the v1.0.0 modules and adds
**scaffolded FRL modules** for the paradigm extension. The v2 modules
are **scaffolds**: `__init__.py` + placeholder docstrings documenting
the planned interface. Full implementations are deferred to
**TÜBİTAK 1001 ARDEB Project 3** (September 2026 application cycle;
2027-2030 execution). Treat v2 modules as **architectural commitments**,
not as runnable code at this scaffold stage.

The four-component action space (or 4-class
for CDSA-MRO) is:
**no maintenance required, scheduled maintenance, urgent maintenance, fleet-wide alert**.

For the paradigm-defining argument, refer to:
- `docs/scenario_c_paradigm_context.md` (paradigm context summary)
- The CDSA Methodological Unification Decision document (internal,
  cited as `[Cantekin 2026, CDSA Scenario C]`)
- The Safety Science Q1 umbrella article (in preparation,
  September 2026)

---

---

## Quick Start

### Installation

```bash
git clone https://github.com/Orfeomete/cdsa-mro.git
cd cdsa-mro
pip install -r requirements.txt
```

### Reproduce the Synthetic Data Set (1000 records)

```bash
python src/synthetic_data_generation/generator.py 1000
```

Output: `data/synthetic_incidents_v1.json` (deterministic, seed = 42).

### Train PPO + 3 Baselines for Comparison

```bash
python src/training/train.py 300
```

Output: results, learning curves, confusion matrix in `results/`.

### Example — Inspect a Single Generated Scenario

```bash
python examples/quick_start.py
```

---

## Repository Structure

```
cdsa-mro/
├── README.md                       ← this file
├── LICENSE                          ← MIT (code)
├── LICENSE-DATA                     ← CC-BY 4.0 (synthetic data)
├── CITATION.cff                     ← academic citation
├── CHANGELOG.md
├── CONTRIBUTING.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── synthetic_data_generation/
│   │   └── generator.py             ← CDSA-MRO-SDG v2.0
│   ├── rl_environment/
│   │   └── cdsa_mro_env.py          ← Gymnasium-compatible env
│   ├── rl_agents/
│   │   └── agents.py                ← Q-Learning, REINFORCE, A2C, PPO-Lite
│   └── training/
│       └── train.py                 ← end-to-end training script
│
├── data/
│   ├── synthetic_incidents_v1.json  ← 1000 generated incidents (4.7 MB)
│   ├── synthetic_incidents_v1_summary.csv
│   ├── delphi_validation_20_samples.json
│   ├── schema.json                  ← JSON Schema specification
│   ├── training_results_v1.json     ← Trained RL model weights
│   ├── GENERATION_REPORT_v1.md
│   └── 5_ornek_senaryolar/          ← 5 hand-curated example scenarios (TR)
│
├── docs/
│   ├── INDEX.md
│   ├── synthetic_data_design.md
│   ├── rl_methodology.md
│   └── validation_protocol.md
│
├── examples/
│   ├── quick_start.py
│   └── reproduce_results.py
│
├── figures/
│   ├── Sekil_1_Egitim_Egrileri.png
│   ├── Sekil_2_Dogruluk_Egrileri.png
│   ├── Sekil_3_Karsilastirma.png
│   └── Sekil_4_Karisiklik_Matrisi.png
│
└── tests/
    └── test_environment.py
```

---

## Data Set

### Synthetic Incidents v1

- **Records:** 1000
- **Format:** JSON (full) + CSV (summary)
- **Generation method:** Template-based deterministic engine with parameter
  pools, aligned with SHT-SIBER Annex 13 (5-section incident report).
- **Random seed:** 42 (deterministic, reproducible).
- **Generation time:** ~1.2 seconds on commodity hardware.

### Scenario Coverage

15 incident types are included:

| ID | Type | Count | Mean Risk Severity |
|---|---|---|---|
| 1 | Phishing attack | 100 | High |
| 2 | Shadow IT | 96 | Moderate |
| 3 | OT system intrusion | 89 | Critical |
| 4 | USB malware | 84 | High |
| 5 | Configuration error | 83 | High |
| 6 | Inadequate access revocation | 74 | High |
| 7 | Account takeover | 71 | Critical |
| 8 | Social engineering | 59 | High |
| 9 | Work order forgery | 56 | Critical |
| 10 | Portal access breach | 55 | Critical |
| 11 | Ransomware | 51 | Critical |
| 12 | Supply chain contamination | 51 | Critical |
| 13 | Calibration integrity breach | 49 | Critical |
| 14 | DDoS attack | 45 | High |
| 15 | Training system manipulation | 37 | High |

### Regulatory Alignment

Each record is labelled with:

- **Risk severity** (1-4) per SHT-SIBER Annex 21
- **MITRE ATT&CK** tactic and technique
- **Annex 19 control point** references
- **KVKK Article 6** special-category data flag
- **SHY-145 Article 18** 72-hour notification compliance

### Privacy Guarantee

- No real person, organisation, or incident is referenced.
- Differential privacy parameter epsilon = 0.8 applied to numeric fields.
- Verified through automated schema validation and planned Modified
  Delphi expert validation (3-5 experts, 2-3 rounds).

---

## Reinforcement Learning Models

### Markov Decision Process Formulation

- **State space (S):** 10-dimensional continuous feature vector.
- **Action space (A):** 5 discrete actions
  (Wait, Low Alert, High Alert, Critical Alert, Escalate to CSIRT).
- **Reward function (R):** Regulation-aware. Correct prediction = +10
  (severity bonus), false alarm = -5, miss = -20 * (severity + 1),
  over/under-reaction = proportional penalty,
  72-hour notification compliance bonus = +2.
- **Discount factor (γ):** 0.99.

### Algorithms

| Algorithm | Test Accuracy | Test Reward | Training Time |
|---|---|---|---|
| Q-Learning | 47.7% | 654.8 | 0.5 s |
| REINFORCE | 43.3% | 528.2 | 1.7 s |
| Actor-Critic | 42.7% | 731.2 | 1.5 s |
| **PPO-Lite** | **54.0%** | **872.1** | **5.1 s** |

Compared to a random baseline (20% on 5-class problem), PPO-Lite
achieves a 2.7-fold improvement.

---

## How to Cite

If you use this framework, the data set, or the code in your research,
please cite:

```bibtex
@article{cantekin2026cdsamro,
  title   = {A Reinforcement-Learning and Data-Locality-Based Cyber-Safety
             Incident Prediction Framework for Continuing Airworthiness
             in Aviation Maintenance Organisations Using Synthetic Data},
  author  = {Cantekin, Mete},
  year    = {2026},
  journal = {arXiv preprint},
  note    = {Preprint v1, DOI pending}
}

@dataset{cantekin2026synthetic,
  title  = {CDSA-MRO Synthetic Cyber-Safety Incident Dataset v1.0},
  author = {Cantekin, Mete},
  year   = {2026},
  publisher = {Zenodo},
  doi    = {pending}
}
```

A machine-readable citation file is available at
[`CITATION.cff`](CITATION.cff).

---

## License

- **Code** (Python modules in `src/`, `examples/`, `tests/`):
  MIT License — see [LICENSE](LICENSE).
- **Data** (`data/synthetic_incidents_v1.json` and other JSON/CSV/MD
  files under `data/`):
  Creative Commons Attribution 4.0 International (CC BY 4.0) — see
  [LICENSE-DATA](LICENSE-DATA).
- **Documentation** (`docs/`): CC BY 4.0.

---

## Acknowledgements

The author thanks Assoc. Prof. Dr. İbrahim Furkan İNCE (Istanbul
Beykent University) for academic guidance during the doctoral
research. Acknowledgements to the modified Delphi panel members will
be added in v2.

This work is part of the doctoral thesis being prepared at Istanbul
Beykent University, Department of Computer Engineering, with planned
external funding through TÜBİTAK ARDEB 1001 (proposal in
preparation).

---

## AI Use Statement

Large language model assistance (Anthropic Claude) was used in the
preparation of source code scaffolding, documentation, and synthetic
scenario template drafting. All scientific contributions, experimental
design, validation decisions, and interpretation of results are the
author's own.

---

## Contact

- **Author:** Mete CANTEKİN
- **Affiliation:** Department of Computer Engineering, Istanbul Beykent
  University, Istanbul, Türkiye
- **ORCID:** [0009-0001-6990-6340](https://orcid.org/0009-0001-6990-6340)
- **E-mail:** metecantekin@gmail.com
- **Platform:** [cdsa.app](https://cdsa.app)

---

## Roadmap

| Version | Target Date | Features |
|---|---|---|
| v1.0 (this) | 15 May 2026 | Synthetic data + 4 RL algorithms |
| v1.1 | 30 Jun 2026 | Modified Delphi validation results (3-5 experts) |
| v2.0 | Q4 2026 | PyTorch deep policy, Stable-Baselines3 PPO, 1M timesteps |
| v2.1 | Q1 2027 | Federated learning extension, XAI integration |
| v3.0 | 2027 | Field deployment study (TÜBİTAK-funded) |

---

## Related Work — CDSA Framework Ecosystem

This repository is part of the CDSA framework ecosystem maintained under
[`Orfeomete`](https://github.com/Orfeomete):

| Repository | Role |
|---|---|
| [`cdsa-site`](https://github.com/Orfeomete/cdsa-site) | Public hub & landing page (cdsa.app) |
| [`cdsa-blackbox`](https://github.com/Orfeomete/cdsa-blackbox) | Investigation module — biometric synthetic data + cryptographic multi-signature |
| [`cdsa-mro`](https://github.com/Orfeomete/cdsa-mro) | **This repo** — Maintenance Organisation module (SDG + RL) |
| [`hipoksi-app-`](https://github.com/Orfeomete/hipoksi-app-) | PilotO2 hypoxia simulator |
| [`pilotguard-app-`](https://github.com/Orfeomete/pilotguard-app-) | Pre-flight readiness monitor |
| [`PilotReflect-new`](https://github.com/Orfeomete/PilotReflect-new) | Post-flight EFB debrief |
| [`pilotsense-auth`](https://github.com/Orfeomete/pilotsense-auth) | Cryptographic 2/3 signature demo |
| [`pilotsense-ops`](https://github.com/Orfeomete/pilotsense-ops) | Anonymized fleet monitoring |

- **arXiv preprint** — Cantekin (2026). See `docs/` for the rendered
  preprint once available.
- **Doctoral thesis** — In preparation, Istanbul Beykent University,
  Department of Computer Engineering, under the supervision of
  Assoc. Prof. Dr. Ibrahim Furkan INCE.
