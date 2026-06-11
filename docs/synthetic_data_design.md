# Synthetic Data Design — CDSA-MRO-SDG v2.0

This document describes the design and implementation of the synthetic
data generation engine.

## Motivation

Operational data from Part-145 approved maintenance organisations is
considered a trade secret and is therefore inaccessible to academic
research. This barrier prevents the development of empirical
AI-supported cyber-safety models for this sector.

CDSA-MRO-SDG addresses the barrier by generating regulation-aligned
synthetic incident records that:

1. Follow the SHGM SHT-SIBER Annex 13 standard 5-section format
   (Summary, Process, Root Cause, Actions, Project Planning).
2. Map to the MITRE ATT&CK threat framework.
3. Carry KVKK Article 6 special-category flags.
4. Cover 15 representative incident types.
5. Guarantee differential privacy with epsilon = 0.8.

## Data Schema

See [`data/schema.json`](../data/schema.json) for the formal JSON
Schema. Top-level structure:

```
{
  "olay_id":             "CDSA-MRO-SDG-NNNNNN",
  "olay_tarihi":         "ISO 8601 timestamp",
  "firma_anonim_id":     "MRO-TR-NNN",
  "olay_ozeti": {
      "olay_turu":             "phishing_attack | ...",
      "saat_araligi":          { "baslangic": ..., "bitis": ... },
      "olay_aciklama":         "Turkish prose",
      "kesinti_suresi_dakika": int,
      "etkilenen_hizmetler":   [string, ...],
      "tahmini_maddi_kayip_TL": int
  },
  "olay_sureci":          "Turkish prose, multi-paragraph",
  "kok_neden_analizi": {
      "temel_neden":               "Turkish prose",
      "katkida_bulunan_etmenler":  [string, ...],
      "swiss_cheese_katmanlari":   [{ "katman": ..., "delik_aciklamasi": ... }]
  },
  "aksiyonlar":           [{ "aksiyon_no", "aciklama", "sorumlu_rol", "oncelik" }],
  "projelendirme":        [{ "proje_no", "duzeltici_faaliyet", "baslama_tarihi", "bitis_tarihi" }],
  "etiketler": {
      "risk_seviyesi":                int 1-4,
      "mitre_attack":                 { "tactic", "technique", "subtechnique" },
      "shtsiber_ek19_kontrol_atfi":   [string, ...],
      "kvkk_ozel_veri_iceriyor":      bool,
      "shy145_madde18_72saat_uygunluk": bool
  },
  "metaveri": { "uretim_tarihi", "uretim_motor_versiyonu",
                "sentetik_garanti": {...}, "delphi_dogrulama": {...} }
}
```

## Incident Type Taxonomy

15 incident types are catalogued. Each type has:

- Typical risk severity (1-4) per SHT-SIBER Annex 21
- MITRE ATT&CK tactic and technique identifiers
- Control point references to SHT-SIBER Annex 19 (173-point matrix
  for Group-2 organisations)
- Pool of natural-language summary templates (5 variants per type)
- Pool of detailed process narratives (3 variants per type)
- Pool of root cause statements (3 variants per type)
- Pool of recommended actions (4-6 actions per type)

| ID | Type Code | Typical Severity |
|---|---|---|
| 1 | `oltalama_saldirisi` | High |
| 2 | `hesap_ele_gecirme` | Critical |
| 3 | `ot_sistem_sizmasi` | Critical |
| 4 | `fidye_yazilimi` | Critical |
| 5 | `ddos_saldirisi` | High |
| 6 | `tedarik_zinciri_kontaminasyonu` | Critical |
| 7 | `usb_zararli_yazilim` | High |
| 8 | `shadow_it` | Moderate |
| 9 | `konfigurasyon_hatasi` | High |
| 10 | `yetki_iptal_eksikligi` | High |
| 11 | `egitim_sistem_manipulasyonu` | High |
| 12 | `kalibrasyon_butunluk_ihlali` | Critical |
| 13 | `portal_erisim_ihlali` | Critical |
| 14 | `sosyal_muhendislik` | High |
| 15 | `is_emri_sahteciligi` | Critical |

## Generation Algorithm

The generation algorithm is deterministic given the random seed
(default: 42). For each record:

1. **Type selection** — weighted sampling according to incident type
   distribution.
2. **Severity adjustment** — base severity from type, with ±1
   variation in 20% of cases.
3. **Date sampling** — uniform random within an 18-month window
   starting 1 January 2025.
4. **Parameter sampling** — facility, personnel role, system identifier
   drawn from labelled pools.
5. **Template instantiation** — narrative templates filled with sampled
   parameters via Python `.format()`.
6. **Root cause and action generation** — drawn from type-specific
   pools.
7. **Project planning** — generated with 14/30/60/90/180-day duration
   options.
8. **Label assignment** — severity, MITRE tactic/technique, Annex 19
   control references, KVKK flag, 72-hour compliance flag.
9. **Differential privacy** — Laplace noise (epsilon = 0.8) applied to
   `kesinti_suresi_dakika` and `tahmini_maddi_kayip_TL`.
10. **Metadata** — generation timestamp, motor version, synthetic
    guarantees, Delphi placeholder.

## Privacy Guarantees

- **No real reference:** All identifiers are synthetic; no real persons,
  organisations, or incidents are referenced.
- **Differential privacy:** Numeric fields perturbed with Laplace
  mechanism, epsilon = 0.8.
- **Sentence-level non-reproducibility:** Template instantiation with
  parameter sampling ensures no two records share identical narratives,
  while no record matches any single real-world template verbatim.
- **Verification:** Metadata field `metaveri.sentetik_garanti` declares
  the absence of real-world references for each record.

## Performance

On commodity hardware (CPU only, Python 3.10, NumPy 1.26):

- 1000 records generated in ~1.2 seconds.
- Memory footprint: < 100 MB.
- Output file size: ~4.7 MB (JSON, indented).
- CSV summary size: ~120 KB.

## Reproducibility

Set `SEED = 42` in `src/synthetic_data_generation/generator.py` and run:

```bash
python src/synthetic_data_generation/generator.py 1000
```

Output is byte-identical across runs on the same hardware. The released
v1 dataset was produced with this exact procedure.

## Comparison with Related Approaches

- **CTGAN / TVAE / Diffusion (tabular synthetic AI):** Statistical
  fidelity to real distributions; requires access to a real reference
  dataset, which is precisely what is unavailable in our setting.
- **LLM-generated synthetic incidents:** Higher narrative diversity but
  expensive to generate at scale, non-deterministic, and requires
  prompt engineering quality assurance.
- **CDSA-MRO-SDG (this approach):** Template-based, deterministic,
  regulation-aligned, no LLM API dependency, suitable for academic
  reproducibility.

## Future Extensions

- **v2.0 LLM hybrid:** Integrate LLM expansion for narrative diversity
  while retaining template-level deterministic seeds.
- **v2.1 Multi-language:** English translation pipeline for
  international audiences.
- **v2.2 Cross-sector:** Adaptation to healthcare, finance, defence
  cyber-safety incident reporting.
