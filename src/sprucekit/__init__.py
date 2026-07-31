"""sprucekit: training-free hierarchical exact-text compilation."""

from .api import (
    CompilationResult,
    CompilerConfig,
    SpruceCompiler,
)
from .compiler import EvidencePacket, EvidenceSpan

__all__ = [
    "CompilationResult",
    "CompilerConfig",
    "EvidencePacket",
    "EvidenceSpan",
    "SpruceCompiler",
]

__version__ = "0.1.0"
