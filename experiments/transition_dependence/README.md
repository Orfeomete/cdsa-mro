# Transition-dependence test

`gecis_bagimliligi_testi.py` asks whether the next state of an environment depends on the action taken at a fixed state. Stage S1 shares one random stream across actions, so an implementation that ignores the action must return a bit-identical next state for every action. Stage S2 draws 400 next states per action at each of 20 fixed states and compares the actions dimension by dimension with a Kruskal–Wallis test at a nominal level of 0.01, Bonferroni-corrected. A reference environment whose next state ignores the action and one shifted by 0.10 per action index serve as controls, and a sweep of the shift measures the sensitivity of the test.

`gecis_bagimliligi_sonuc.json` is the result for the three published environments (BB3, MRO and ATM). All three pass both stages, the action-independent control passes, the shifted control fails, and the sensitivity sweep detects a shift of 0.02 but not 0.01 in the normalised state space. This calibration does not guarantee detection of every dependence of that magnitude.

| File | SHA-256 |
|---|---|
| `gecis_bagimliligi_testi.py` | `b3bc5b7633a9f5f1230596af30cff37c6fce5ccec9c65c1da2ecc0bc6205e64d` |
| `gecis_bagimliligi_sonuc.json` | `d09a453c634624a97ef46f3d2843f0016c9351b3600e850575b11a2951f2244d` |

The script digest is the one recorded by the E12 positive control (`experiments/e12_positive_control/sonuclar/` in cdsa-atm) and the E13 external test (`experiments/e13_external_envs/e13_sonuc.json` in cdsa-atm), which import this test as their precondition check. The script is published exactly as it was run, so its paths (`UP`, `/tmp` and the output path in `main()`) point to the author's working environment, where the three repositories sat under `CDSA-BB3/12_GitHub_Repo/cdsa-bb3`, `CDSA-MRO/12_GitHub_Repo/cdsa-mro` and `CDSA-ATM/12_GitHub_Repo/cdsa-atm`. To rerun it, set `UP` to a folder with that layout and change the output path. The same two files are included in cdsa-bb3, cdsa-mro and cdsa-atm from release v2.4.0.
