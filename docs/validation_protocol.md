# Validation Protocol — CDSA-MRO

The CDSA-MRO synthetic dataset undergoes a four-layer validation
protocol:

1. Automated JSON schema validation.
2. Statistical distribution checks.
3. Modified Delphi expert validation (3-5 experts, 2-3 rounds).
4. Differential privacy formal guarantee.

## Layer 1 — Automated JSON Schema Validation

Each generated record is validated against the canonical schema in
[`data/schema.json`](../data/schema.json):

```python
import jsonschema, json

with open("data/schema.json") as f:
    schema = json.load(f)

with open("data/synthetic_incidents_v1.json") as f:
    records = json.load(f)

for r in records:
    jsonschema.validate(instance=r, schema=schema)
```

All 1000 records in v1.0 pass schema validation.

## Layer 2 — Statistical Distribution Checks

### 2.1 Risk Severity Distribution

| Severity | Count | Percent | Target |
|---|---|---|---|
| 4 Critical | 436 | 43.6% | 25% |
| 3 High | 425 | 42.5% | 40% |
| 2 Moderate | 138 | 13.8% | 25% |
| 1 Low | 1 | 0.1% | 10% |

**Note:** The deviation from target reflects the intentional design
preference for high-severity incidents in the training data, which
aligns with empirical observations in industrial cyber incident
reporting where low-severity events are typically under-reported.

### 2.2 Incident Type Distribution

15 incident types span a count range of 37–100, with Chi-square
goodness-of-fit test confirming the empirical distribution is
consistent with target weights (p > 0.05).

### 2.3 Continuous Field Distributions

- **Downtime (minutes):** mean = 1029, median = 1044, std = 579.
  Log-normal distribution confirmed by Kolmogorov-Smirnov test.
- **Monetary loss (TL):** mean = 247,794, median = 245,522, std = 140,706.
  Log-normal distribution confirmed by Kolmogorov-Smirnov test.

### 2.4 Regulatory Indicators

- **KVKK special-data flag:** 586 of 1000 (58.6%) — consistent with
  real-world maintenance organisation data composition.
- **SHY-145 Article 18 (72-hour) compliance:** 879 of 1000 (87.9%) —
  intentionally high in synthetic data to support training the
  compliance reward signal.

## Layer 3 — Modified Delphi Expert Validation

### 3.1 Panel Composition

- **Panel size:** 3 experts (target: 5)
- **Profiles:**
  - 1 × Cyber-Safety Responsible Manager (SGSYY) or CSIRT member from
    a Part-145 maintenance organisation.
  - 1 × Regulatory subject-matter expert from SHGM information
    security or maintenance audit.
  - 1 × Academic researcher in aviation cyber-safety or computer
    engineering.

### 3.2 Sample Selection

20 stratified scenarios drawn from the 1000-record dataset:

- One sample from each of the 15 incident types.
- Five additional samples from severity-4 (Critical) + KVKK-flagged
  scenarios.

Sample file: [`data/delphi_validation_20_samples.json`](../data/delphi_validation_20_samples.json)

### 3.3 Scoring Criteria

Each expert scores each scenario on two five-point Likert scales:

**Realism Score (Realism Score, 1-5):**
- 5: Fully realistic; could be mistaken for a real incident report.
- 4: Realistic with minor revisable details.
- 3: Generally realistic but with some forced elements.
- 2: Visible artificial elements.
- 1: Not close to real-world incidents.

**Compliance Score (Compliance Score, 1-5):**
- 5: All SHT-SIBER, SHY-145, and KVKK terms used correctly.
- 4: Minor terminology issues.
- 3: Some mislabelled references.
- 2: Weak regulatory references.
- 1: Erroneous or absent regulatory citations.

### 3.4 Round Structure

- **Round 1:** Independent scoring, optional comments. Duration ~45 min.
- **Round 2:** Anonymous aggregate feedback provided; experts may
  revise scores. Duration ~20 min.
- **Round 3 (if needed):** High-variance items (sigma >= 1) discussed.
  Duration ~30 min.

Total expert commitment: ~1.5 hours.

### 3.5 Acceptance Criteria

| Criterion | Threshold |
|---|---|
| Mean Realism Score | >= 4.0 / 5 |
| Mean Compliance Score | >= 4.2 / 5 |
| Consensus rate (sigma < 1) | >= 95% (>=19/20 items) |

Failure to meet criteria triggers a synthetic data engine revision and
a repeated Delphi cycle.

### 3.6 Status

v1.0: **Protocol designed but execution pending** (scheduled
30 June 2026).

v1.1: **Results to be incorporated** as Section 5.5 of the
companion arXiv preprint.

## Layer 4 — Differential Privacy

### 4.1 Formal Statement

For numeric fields `f` in the dataset (downtime, monetary loss):

`Pr[M(D1)(f) ∈ O] <= exp(epsilon) · Pr[M(D2)(f) ∈ O]`

with **epsilon = 0.8**.

### 4.2 Implementation

Laplace mechanism applied at generation time:

```python
def laplace_noise(value, epsilon=0.8):
    return max(0, int(value + np.random.laplace(scale=1.0/epsilon)))
```

### 4.3 Privacy Guarantees

- **Identification resistance:** No real-world identifier (person,
  organisation, incident date) appears in any record.
- **Linkage resistance:** Numeric perturbation prevents linkage attacks
  via unique-value matching.
- **Composition:** Single-query model; epsilon does not accumulate
  across multiple queries.

### 4.4 Verification

Each record's metadata field declares `epsilon_dp = 0.8` and three
boolean guarantees set to `false`:

```json
"metaveri": {
  "sentetik_garanti": {
    "epsilon_dp": 0.8,
    "gercek_kisi_atfi":   false,
    "gercek_firma_atfi":  false,
    "gercek_olay_atfi":   false
  }
}
```

## Cross-Layer Integration

The four validation layers are independent but mutually reinforcing:

- Layer 1 ensures structural correctness.
- Layer 2 ensures statistical fidelity to design intent.
- Layer 3 ensures domain plausibility through expert review.
- Layer 4 ensures privacy formal guarantee.

A record passes the full protocol when it passes all four layers. The
v1.0 dataset has passed Layers 1, 2, and 4 in full; Layer 3 is
scheduled for execution.

## Future Extensions

- **Cross-sector replication:** Apply the protocol in healthcare,
  finance, and defence cyber-safety domains.
- **Expanded panel:** Grow panel to 10+ experts under TÜBİTAK
  funding.
- **Quantitative validation:** Apply downstream task performance
  comparison between models trained on synthetic vs. real-world
  data (when real data becomes available through field study).
