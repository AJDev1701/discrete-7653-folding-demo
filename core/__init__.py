# core/__init__.py
from .folding_engine import (
    build_permutation,
    build_inverse,
    permute,
    invert_permute,
    FoldingEngineError,
    BLOCK_SIZE,
)

__all__ = [
    "build_permutation",
    "build_inverse",
    "permute",
    "invert_permute",
    "FoldingEngineError",
    "BLOCK_SIZE",
]
