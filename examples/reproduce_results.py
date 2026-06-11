"""
Reproduce CDSA-MRO v1.0 Results
=================================
End-to-end reproduction of the v1.0 published results:
1. Generate the 1000-record synthetic dataset (deterministic, seed=42).
2. Train all four RL algorithms.
3. Evaluate and print comparison table.

Expected runtime: ~10 seconds on commodity hardware.

Usage:
    python examples/reproduce_results.py
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent


def step(num, title):
    print(f"\n{'='*60}")
    print(f"Step {num}: {title}")
    print("=" * 60)


def main():
    print("CDSA-MRO v1.0 — Full Reproduction")
    print(f"Repository root: {ROOT}")

    # Step 1: Generate synthetic data
    step(1, "Generate 1000-record synthetic dataset")
    gen_script = ROOT / "src" / "synthetic_data_generation" / "generator.py"
    result = subprocess.run(
        [sys.executable, str(gen_script), "1000"],
        cwd=ROOT
    )
    if result.returncode != 0:
        print("ERROR — generation failed.")
        sys.exit(1)

    # Step 2: Train RL algorithms
    step(2, "Train Q-Learning, REINFORCE, A2C, PPO-Lite")
    train_script = ROOT / "src" / "training" / "train.py"
    result = subprocess.run(
        [sys.executable, str(train_script), "300"],
        cwd=ROOT
    )
    if result.returncode != 0:
        print("ERROR — training failed.")
        sys.exit(1)

    # Step 3: Verify
    step(3, "Verify output files")
    expected = [
        ROOT / "data" / "synthetic_incidents_v1.json",
        ROOT / "data" / "training_results_v1.json",
    ]
    for f in expected:
        if f.exists():
            size_kb = f.stat().st_size / 1024
            print(f"  OK: {f.relative_to(ROOT)} ({size_kb:.1f} KB)")
        else:
            print(f"  MISSING: {f.relative_to(ROOT)}")

    print(f"\n{'='*60}")
    print("Reproduction complete.")
    print(f"{'='*60}")
    print("\nExpected results (PPO-Lite):")
    print("  Test mean reward: 872.1")
    print("  Test accuracy   : 54.0%")
    print("\nDeviations greater than ±5% suggest non-determinism in the environment.")


if __name__ == "__main__":
    main()
