"""
discrete-7653-folding-demo: Core Folding Engine

Deterministic permutation generator driven by a rational generator ratio num/den.
The default generator is 76/53 over a 97-position block (the v0.1.1 permutation,
reproduced bit-for-bit). Any positive num/den and any block size n >= 2 with a
coprime collision probe are supported.

Classification: STANDALONE_DETERMINISTIC_PERMUTATION
Solve claims: FALSE
"""

from __future__ import annotations

import math
import warnings
from typing import List, Optional, Tuple

# ── Default parameters ────────────────────────────────────────────────────────
BLOCK_SIZE       = 97        # N (default block size; prime)
GENERATOR_NUM    = 76        # default generator numerator
GENERATOR_DEN    = 53        # default generator denominator
COLLISION_STEP   = 7         # default secondary probe (coprime with BLOCK_SIZE)

# Derived defaults (kept as module constants for backward compatibility)
BASE_STEP        = GENERATOR_NUM // GENERATOR_DEN   # 1
REMAINDER_STEP   = GENERATOR_NUM % GENERATOR_DEN    # 23
HINGE_STEP       = BASE_STEP + 1                    # 2


class FoldingEngineError(ValueError):
    """Raised on invalid engine configuration."""


def derive_strides(num: int, den: int) -> Tuple[int, int, int]:
    """Return (base, remainder, hinge) for generator num/den.

    base  = num // den   stride when the accumulator does not carry
    rem   = num %  den   accumulator increment per step
    hinge = base + 1     stride when the accumulator carries
    """
    return num // den, num % den, num // den + 1


def expected_hinge_ticks(n: int, num: int, den: int) -> int:
    """Closed-form count of carry (hinge) steps in n iterations from acc = 0.

    The accumulator gains (num % den) per step and loses den on each carry while
    staying in [0, den), so carries = floor(n * (num % den) / den).
    """
    return (n * (num % den)) // den


def _validate(n: int, num: int, den: int, collision_step: int) -> None:
    for name, value in (("n", n), ("num", num), ("den", den), ("collision_step", collision_step)):
        if not isinstance(value, int) or isinstance(value, bool):
            raise FoldingEngineError(f"{name} must be an int, got {type(value).__name__}")
    if n < 2:
        raise FoldingEngineError(f"Block size n must be >= 2, got {n}.")
    if den < 1:
        raise FoldingEngineError(f"Generator denominator must be >= 1, got {den}.")
    if num < 1:
        raise FoldingEngineError(f"Generator numerator must be >= 1, got {num}.")
    if math.gcd(collision_step, n) != 1:
        raise FoldingEngineError(
            f"Collision step {collision_step} is not coprime with block size {n} "
            f"(gcd={math.gcd(collision_step, n)}). Probe would cycle and miss slots."
        )


def build_permutation(
    n:              int = BLOCK_SIZE,
    num:            int = GENERATOR_NUM,
    den:            int = GENERATOR_DEN,
    collision_step: int = COLLISION_STEP,
    *,
    remainder_step: Optional[int] = None,
) -> List[int]:
    """
    Construct the deterministic folding permutation for block size n and
    generator num/den.

    Recurrence (base, rem, hinge = derive_strides(num, den)):
        pointer      = n - 1
        accumulator  = 0
        For i in [0, n):
            accumulator += rem
            if accumulator >= den:
                accumulator -= den
                stride = hinge
            else:
                stride = base
            candidate = (pointer + stride) % n
            while occupied[candidate]:
                candidate = (candidate + collision_step) % n
            occupied[candidate] = True
            permutation[i]      = candidate
            pointer             = candidate

    Invariants enforced (raise FoldingEngineError on violation):
        - set(result) == set(range(n)), len(result) == n   [bijectivity]
        - gcd(collision_step, n) == 1                       [probe termination]
        - hinge ticks == floor(n * rem / den)               [stride distribution]

    Deprecated: ``remainder_step=`` (v0.1.1 keyword). It maps to
    num = den + remainder_step, which is the generator v0.1.1 implied, since its
    base stride was fixed at 1.
    """
    if remainder_step is not None:
        warnings.warn(
            "build_permutation(remainder_step=...) is deprecated; pass num= and den= instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        num = den + remainder_step

    _validate(n, num, den, collision_step)
    base, rem, hinge = derive_strides(num, den)

    occupied:    List[bool] = [False] * n
    permutation: List[int]  = [0]    * n
    pointer:     int        = n - 1
    accumulator: int        = 0
    hinge_ticks: int        = 0

    for i in range(n):
        accumulator += rem
        if accumulator >= den:
            accumulator -= den
            stride = hinge
            hinge_ticks += 1
        else:
            stride = base

        candidate = (pointer + stride) % n
        while occupied[candidate]:
            candidate = (candidate + collision_step) % n

        occupied[candidate]  = True
        permutation[i]       = candidate
        pointer              = candidate

    if len(permutation) != n or set(permutation) != set(range(n)):
        raise FoldingEngineError("Bijectivity/length invariant violated")
    if hinge_ticks != expected_hinge_ticks(n, num, den):
        raise FoldingEngineError(
            f"Stride distribution invariant violated: {hinge_ticks} hinge ticks, "
            f"expected {expected_hinge_ticks(n, num, den)}"
        )

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
