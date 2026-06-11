"""
CDSA-MRO src.multimodal — Multi-modal Encoders + Cross-modal Attention
=============================================================================

Scaffold for parallel modality encoders and a cross-modal attention +
gating fusion layer that produces the fused representation consumed
by `src.rl_agents`.

Modalities (Engine + Cyber + Maintenance):
  EngineEncoder: 1D-CNN + LSTM over NASA C-MAPSS turbofan sensors
                 (21 sensor channels, FD001-FD004 sub-sets)
  CyberEncoder:  Transformer over SHT-SIBER Annex 13 15-class typology
  MaintEncoder:  LSTM over SHY-145 maintenance record sequences

Status: scaffolded (v2). Full implementation is planned under
TÜBİTAK 1001 ARDEB Project 3.
"""

from .encoders import EngineEncoder, CyberEncoder, MaintEncoder  # noqa: F401
from .fusion import CrossModalAttentionFusion  # noqa: F401

__all__ = ['EngineEncoder', 'CyberEncoder', 'MaintEncoder', "CrossModalAttentionFusion"]
