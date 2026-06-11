"""
Basic tests for the CDSA-MRO Gymnasium-compatible environment.
"""

import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "rl_environment"))


def test_environment_loads():
    """Environment can be instantiated."""
    from cdsa_mro_env import CDSAMROEnv
    env = CDSAMROEnv(
        str(REPO_ROOT / "data" / "synthetic_incidents_v1.json"),
        seed=42,
        max_steps=10
    )
    assert env.n_features == 10
    assert env.n_actions == 5
    assert len(env.dataset) == 1000
    print("test_environment_loads — PASS")


def test_reset_returns_state():
    """env.reset() returns a 10-dim state vector."""
    from cdsa_mro_env import CDSAMROEnv
    env = CDSAMROEnv(
        str(REPO_ROOT / "data" / "synthetic_incidents_v1.json"),
        seed=42,
        max_steps=10
    )
    state = env.reset()
    assert state.shape == (10,)
    assert 0 <= state.min() <= state.max() <= 1.01
    print("test_reset_returns_state — PASS")


def test_step_returns_tuple():
    """env.step(action) returns (state, reward, done, info)."""
    from cdsa_mro_env import CDSAMROEnv
    env = CDSAMROEnv(
        str(REPO_ROOT / "data" / "synthetic_incidents_v1.json"),
        seed=42,
        max_steps=5
    )
    env.reset()
    state, reward, done, info = env.step(2)
    assert state.shape == (10,)
    assert isinstance(reward, float)
    assert isinstance(done, bool)
    assert "true_action" in info
    assert "episode_accuracy" in info
    print("test_step_returns_tuple — PASS")


def test_episode_terminates():
    """Episode terminates after max_steps."""
    from cdsa_mro_env import CDSAMROEnv
    env = CDSAMROEnv(
        str(REPO_ROOT / "data" / "synthetic_incidents_v1.json"),
        seed=42,
        max_steps=3
    )
    env.reset()
    for _ in range(3):
        _, _, done, _ = env.step(0)
    assert done is True
    print("test_episode_terminates — PASS")


def test_deterministic_reset():
    """Same seed gives same first observation."""
    from cdsa_mro_env import CDSAMROEnv
    env1 = CDSAMROEnv(
        str(REPO_ROOT / "data" / "synthetic_incidents_v1.json"),
        seed=42, max_steps=5
    )
    env2 = CDSAMROEnv(
        str(REPO_ROOT / "data" / "synthetic_incidents_v1.json"),
        seed=42, max_steps=5
    )
    s1 = env1.reset()
    s2 = env2.reset()
    import numpy as np
    assert np.allclose(s1, s2)
    print("test_deterministic_reset — PASS")


if __name__ == "__main__":
    test_environment_loads()
    test_reset_returns_state()
    test_step_returns_tuple()
    test_episode_terminates()
    test_deterministic_reset()
    print("\nAll tests passed.")
