"""
CDSA-MRO Quick Start Example
==============================
Load the synthetic dataset, inspect a single record, and print basic
statistics.

Usage:
    python examples/quick_start.py
"""

import json
import sys
from collections import Counter
from pathlib import Path

# Resolve dataset path relative to repository root
ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "synthetic_incidents_v1.json"


def main():
    print("CDSA-MRO Quick Start")
    print(f"Loading dataset from: {DATA_PATH}")
    if not DATA_PATH.exists():
        print(f"Dataset not found. Generate it first:")
        print(f"  python src/synthetic_data_generation/generator.py 1000")
        sys.exit(1)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"\nTotal records: {len(records)}")
    print()

    # Inspect a single record
    print("Sample record (first 5 fields):")
    print("-" * 60)
    first = records[0]
    print(f"  olay_id        : {first['olay_id']}")
    print(f"  olay_tarihi    : {first['olay_tarihi']}")
    print(f"  firma_anonim_id: {first['firma_anonim_id']}")
    print(f"  olay_turu      : {first['olay_ozeti']['olay_turu']}")
    print(f"  risk_seviyesi  : {first['etiketler']['risk_seviyesi']}")
    print(f"  MITRE tactic   : {first['etiketler']['mitre_attack']['tactic']}")
    print()
    print("  Description (first 200 chars):")
    print(f"    {first['olay_ozeti']['olay_aciklama'][:200]}...")
    print()

    # Aggregate statistics
    print("Statistics across all records:")
    print("-" * 60)

    type_counts = Counter(r["olay_ozeti"]["olay_turu"] for r in records)
    severity_counts = Counter(r["etiketler"]["risk_seviyesi"] for r in records)
    kvkk_count = sum(1 for r in records if r["etiketler"]["kvkk_ozel_veri_iceriyor"])
    compliance_count = sum(1 for r in records if r["etiketler"]["shy145_madde18_72saat_uygunluk"])

    print("\n  Incident Type Distribution (top 5):")
    for t, c in type_counts.most_common(5):
        print(f"    {t:40s} {c:>4} ({c/len(records)*100:>4.1f}%)")

    print("\n  Severity Distribution:")
    severity_labels = {1: "Low", 2: "Moderate", 3: "High", 4: "Critical"}
    for s in [4, 3, 2, 1]:
        c = severity_counts.get(s, 0)
        print(f"    {s} ({severity_labels[s]:>8s}) {c:>4} ({c/len(records)*100:>4.1f}%)")

    print(f"\n  KVKK special-data flagged : {kvkk_count} ({kvkk_count/len(records)*100:.1f}%)")
    print(f"  72-hour notification compliant: {compliance_count} ({compliance_count/len(records)*100:.1f}%)")

    print("\nQuick start complete.")


if __name__ == "__main__":
    main()
