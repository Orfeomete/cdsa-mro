# Contributing to CDSA-MRO

Thank you for considering a contribution. This document outlines how
to participate constructively in the project.

## Types of Contributions Welcome

1. **Bug reports** for code or documentation.
2. **Scenario contributions** — new incident-type templates aligned
   with SHT-SIBER Annex 13. See `data/5_ornek_senaryolar/` for format.
3. **Algorithm extensions** — additional reinforcement learning
   algorithms compatible with the CDSA-MRO environment interface.
4. **Validation studies** — independent expert validation runs in
   different domains (healthcare, finance, defence, etc.).
5. **Documentation improvements** — translations, clarifications,
   examples.
6. **Reproducibility verifications** — running the framework on your
   hardware and reporting variance.

## Code Style

- Python 3.10+ syntax.
- PEP 8 with 4-space indentation.
- Docstrings for all public functions (Google or NumPy style).
- Type hints encouraged but not mandatory.

## Submitting Changes

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-improvement`).
3. Make changes; ensure existing tests pass (`python -m pytest tests/`).
4. Commit with a clear message.
5. Push your branch and open a pull request.
6. Include a brief description of the motivation and impact.

## Data Contributions

For synthetic scenario contributions, ensure:

- Compliance with the JSON Schema in `data/schema.json`.
- No references to real persons, organisations, or incidents.
- Alignment with the 15-type incident taxonomy in
  `docs/synthetic_data_design.md`.
- Submission via pull request with a short rationale.

## Academic Use and Citation

If you use CDSA-MRO in published research, please cite the framework
per `CITATION.cff`. If your work extends or significantly modifies the
framework, consider opening an issue to discuss potential collaboration.

## Code of Conduct

This project follows the Contributor Covenant Code of Conduct. Be
respectful, constructive, and inclusive. Report any concerns to the
maintainer (see README).

## Maintainer

- **Mete CANTEKİN** — author and primary maintainer
- E-mail: metecantekin@gmail.com
- ORCID: 0009-0001-6990-6340
