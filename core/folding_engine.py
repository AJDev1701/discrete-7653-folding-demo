"""
discrete-7653-folding-demo: Core Folding Engine

Deterministic permutation generator using the 7653 generator ratio (76/53).
Classification: STANDALONE_DETERMINISTIC_PERMUTATION
Solve claims: FALSE
"""

from __future__ import annotations

import math
from typing import List

# ── Engine constants ──────────────────────────────────────────────────────────
BLOCK_SIZE       = 97        # N
GENERATOR_NUM    = 76        # generator numerator
GENERATOR_DEN    = 53        # generator denominator
BASE_STEP        = GENERATOR_NUM // GENERATOR_DEN   # 1
REMAINDER_STEP   = GENERATOR_NUM % GENERATOR_DEN    # 23
HINGE_STEP       = 2         # stride on carry
COLLISION_STEP   = 7         # secondary probe (must be coprime with BLOCK_SIZE)


class FoldingEngineError(ValueError):
    """Raised on invalid engine configuration."""


def _validate_collision_step(n: int, step: int) -> None:
    """Reject collision steps that are not coprime with block size."""
    if math.gcd(step, n) != 1:
        raise FoldingEngineError(
            f"Collision step {step} is not coprime with block size {n} "
            f"(gcd={math.gcd(step, n)}). Probe would cycle and miss slots."
        )


def build_permutation(
    n: int           = BLOCK_SIZE,
    remainder_step:  int = REMAINDER_STEP,
    den:             int = GENERATOR_DEN,
    collision_step:  int = COLLISION_STEP,
) -> List[int]:
    """
    Construct the deterministic 7653 folding permutation for block size n.

    Recurrence:
        pointer      = n - 1
        accumulator  = 0
        For i in [0, n):
            acc_next = accumulator + remainder_step
            if acc_next >= den:
                stride      = HINGE_STEP
                accumulator = acc_next - den
            else:
                stride      = BASE_STEP
                accumulator = acc_next
            candidate = (pointer + stride) % n
            while occupied[candidate]:
                candidate = (candidate + collision_step) % n
            occupied[candidate] = True
            permutation[i]      = candidate
            pointer             = candidate

    Invariants enforced:
        - set(result) == set(range(n))          [bijectivity]
        - len(result) == n                       [completeness]
        - gcd(collision_step, n) == 1           [probe termination]
    """
    _validate_collision_step(n, collision_step)

    occupied:    List[bool] = [False] * n
    permutation: List[int]  = [0]    * n
    pointer:     int        = n - 1
    accumulator: int        = 0

    for i in range(n):
        acc_next = accumulator + remainder_step
        if acc_next >= den:
            stride      = HINGE_STEP
            accumulator = acc_next - den
        else:
            stride      = BASE_STEP
            accumulator = acc_next

        candidate = (pointer + stride) % n
        while occupied[candidate]:
            candidate = (candidate + collision_step) % n

        occupied[candidate]  = True
        permutation[i]       = candidate
        pointer              = candidate

    # Invariant check
    assert set(permutation) == set(range(n)), "Bijectivity violated"
    assert len(permutation) == n,             "Length invariant violated"

    return permutation


def build_inverse(permutation: List[int]) -> List[int]:
    """
    Derive the inverse mapping: inverse[permutation[source]] = source.

    invert_permute(permute(sequence)) == sequence for all sequences of len(permutation).
    """
    n       = len(permutation)
    inverse = [0] * n
    for source_index, target_index in enumerate(permutation):
        inverse[target_index] = source_index
    return inverse


def permute(sequence: List, permutation: List[int]) -> List:
    """
    Apply permutation to sequence: out[i] = sequence[permutation[i]].

    The permutation maps output-position i to the source-position permutation[i].
    """
    if len(sequence) != len(permutation):
        raise FoldingEngineError(
            f"Sequence length {len(sequence)} != permutation length {len(permutation)}"
        )
    return [sequence[permutation[i]] for i in range(len(permutation))]


def invert_permute(sequence: List, permutation: List[int]) -> List:
    """
    Invert a permuted sequence using the derived inverse map.

    Guarantees: invert_permute(permute(seq, pi), pi) == seq for all seq.
    """
    inv = build_inverse(permutation)
    return permute(sequence, inv)
