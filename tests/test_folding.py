"""
Test suite for discrete-7653-folding-demo core engine.

Covers:
  - Bijectivity and length invariants
  - Exact round-trip inversion (1000 randomised ASCII sequences)
  - Non-coprime collision step rejection
  - Determinism across repeated calls
  - Edge: single-char and boundary sequences
"""

from __future__ import annotations

import math
import random
import string
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.folding_engine import (
    BLOCK_SIZE,
    COLLISION_STEP,
    FoldingEngineError,
    build_inverse,
    build_permutation,
    invert_permute,
    permute,
)

SEED = 1701


# ── Fixture ───────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def canonical_perm():
    return build_permutation()


# ── T1: Bijectivity ───────────────────────────────────────────────────────────
def test_bijectivity(canonical_perm):
    assert set(canonical_perm) == set(range(BLOCK_SIZE))


def test_length(canonical_perm):
    assert len(canonical_perm) == BLOCK_SIZE


# ── T2: Determinism ───────────────────────────────────────────────────────────
def test_determinism(canonical_perm):
    second = build_permutation()
    assert canonical_perm == second


# ── T3: Inverse correctness ───────────────────────────────────────────────────
def test_inverse_composition(canonical_perm):
    inv = build_inverse(canonical_perm)
    # permutation composed with its inverse should give identity
    identity = permute(list(range(BLOCK_SIZE)), inv)
    identity2 = permute(identity, canonical_perm)
    # Actually verify forward->inverse == original
    seq = list(range(BLOCK_SIZE))
    permuted   = permute(seq, canonical_perm)
    recovered  = invert_permute(permuted, canonical_perm)
    assert recovered == seq


# ── T4: 1000 randomised ASCII round-trip assertions ──────────────────────────
@pytest.mark.parametrize("trial", range(1000))
def test_random_roundtrip(trial, canonical_perm):
    rng = random.Random(SEED + trial)
    seq = [rng.choice(string.printable) for _ in range(BLOCK_SIZE)]
    recovered = invert_permute(permute(seq, canonical_perm), canonical_perm)
    assert recovered == seq


# ── T5: Non-coprime collision step rejection ──────────────────────────────────
@pytest.mark.parametrize("bad_step", [97, 194, 0])
def test_non_coprime_step_rejected(bad_step):
    with pytest.raises(FoldingEngineError):
        build_permutation(collision_step=bad_step)


def test_coprime_step_accepted():
    # Step 7 is coprime with 97 (97 is prime, 7 < 97)
    assert math.gcd(COLLISION_STEP, BLOCK_SIZE) == 1
    perm = build_permutation(collision_step=COLLISION_STEP)
    assert len(perm) == BLOCK_SIZE


# ── T6: Length mismatch rejection ────────────────────────────────────────────
def test_permute_length_mismatch(canonical_perm):
    with pytest.raises(FoldingEngineError):
        permute(["x"] * (BLOCK_SIZE - 1), canonical_perm)


# ── T7: Mathematical invariants from spec ─────────────────────────────────────
def test_generator_ratio():
    from core.folding_engine import GENERATOR_DEN, GENERATOR_NUM, REMAINDER_STEP
    assert GENERATOR_NUM // GENERATOR_DEN == 1
    assert GENERATOR_NUM % GENERATOR_DEN  == 23
    assert REMAINDER_STEP                 == 23


def test_gcd_collision_step():
    assert math.gcd(COLLISION_STEP, BLOCK_SIZE) == 1


# ── T8: Stride count verification (55 single, 42 hinge) ──────────────────────
def test_stride_counts(canonical_perm):
    from core.folding_engine import GENERATOR_DEN, REMAINDER_STEP, HINGE_STEP, BASE_STEP
    acc = 0
    single_count = 0
    hinge_count  = 0
    for _ in range(BLOCK_SIZE):
        acc_next = acc + REMAINDER_STEP
        if acc_next >= GENERATOR_DEN:
            hinge_count += 1
            acc = acc_next - GENERATOR_DEN
        else:
            single_count += 1
            acc = acc_next
    assert single_count == 55, f"Expected 55 single steps, got {single_count}"
    assert hinge_count  == 42, f"Expected 42 hinge steps, got {hinge_count}"
    assert single_count + hinge_count == BLOCK_SIZE
