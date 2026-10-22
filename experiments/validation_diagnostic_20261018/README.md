# Validation diagnostic study (18 October 2026)

`CDSA_VALIDATION_DIAGNOSTIC_20261018_R1.zip` is the complete package of the diagnostic study dated 18 October 2026 that the preregistered evaluation manuscript reports alongside its preregistered results. Thirty models were trained over the three tasks, two PPO arms (centralised and FedAvg) and five model seeds for 32 fixed rounds, and the 270 checkpoints were frozen before any test forward pass. Validation loss is the unweighted reference-action negative log probability, not the PPO optimisation objective, and the final mean validation loss exceeds its initial value in all six task and arm combinations.

| File | Size | SHA-256 |
|---|---|---|
| `CDSA_VALIDATION_DIAGNOSTIC_20261018_R1.zip` | 6,645,190 bytes | `278448ee4fe747f2c501f2f11e1bc6cbf8008ed13b25c933843985075b375445` |

The archive holds the frozen protocol, input and source snapshots, data splits, run folders with checkpoints, training traces and post-training test scores, TensorBoard event files, figures and the analysis scripts. Its `STUDY_README.txt` describes the contents and the limits of reproduction. That file was written before this deposit and therefore still says that no public release contains the package, which release v2.4.0 changes.

The study is diagnostic. It does not change any preregistered decision rule, does not reconstruct the historical loss logs and makes no claim of operational validity. The MRO test pool has no class-0 support and one class-1 record unseen in training, so its supported-class AUC is not an external-validation result. The same archive is included in cdsa-bb3, cdsa-mro and cdsa-atm from release v2.4.0.
