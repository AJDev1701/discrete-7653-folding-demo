"""
v0.1.2 parameterization tests.

- Regression lock: default arguments reproduce the frozen v0.1.1 permutation.
- Parameter grid: 48 (n, num, den, collision_step) cases; bijection, exact
  inversion, determinism and the closed-form hinge-tick count for each.
- Validation: invalid parameters raise FoldingEngineError.
- Deprecation shim for the v0.1.1 ``remainder_step=`` keyword.
"""

from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.folding_engine import (  # noqa: E402
    BASE_STEP,
    HINGE_STEP,
    REMAINDER_STEP,
    FoldingEngineError,
    build_permutation,
    derive_strides,
    expected_hinge_ticks,
    invert_permute,
    permute,
)

FIXTURE = ROOT / "tests" / "fixtures" / "v0_1_1_permutation.json"


# ── Regression lock ───────────────────────────────────────────────────────────
def test_default_matches_frozen_v0_1_1_permutation():
    frozen = json.loads(FIXTURE.read_text(encoding="utf-8"))["permutation"]
    assert build_permutation() == frozen


def test_explicit_defaults_match_frozen_permutation():
    frozen = json.loads(FIXTURE.read_text(encoding="utf-8"))["permutation"]
    assert build_permutation(n=97, num=76, den=53, collision_step=7) == frozen


def test_default_anchors():
    p = build_permutation()
    assert p[:3] == [0, 1, 3]
    assert sum(p) == 4656
    assert expected_hinge_ticks(97, 76, 53) == 42


def test_derived_constants_backward_compatible():
    assert (BASE_STEP, REMAINDER_STEP, HINGE_STEP) == (1, 23, 2)
    assert derive_strides(76, 53) == (1, 23, 2)
    assert derive_strides(130, 53) == (2, 24, 3)   # v0.1.1 would have used 1 / 2 here


# ── Parameter grid (48 cases) ─────────────────────────────────────────────────
_SIZES  = (97, 101, 64, 12)
_RATIOS = ((76, 53), (130, 53), (1, 1), (5, 3), (53, 76), (97, 2))
_PROBES = (1, 7)
GRID = [
    (n, num, den, probe)
    for n in _SIZES
    for (num, den) in _RATIOS
    for probe in _PROBES
    if math.gcd(probe, n) == 1
]
assert len(GRID) == 48, len(GRID)


@pytest.mark.parametrize("n,num,den,probe", GRID,
                         ids=[f"n{n}-{num}_{den}-p{p}" for n, num, den, p in GRID])
def test_parameter_grid(n, num, den, probe):
    perm = build_permutation(n=n, num=num, den=den, collision_step=probe)
    # bijection
    assert sorted(perm) == list(range(n))
    # determinism
    assert build_permutation(n=n, num=num, den=den, collision_step=probe) == perm
    # exact inversion
    seq = [f"s{i}" for i in range(n)]
    assert invert_permute(permute(seq, perm), perm) == seq
    # closed-form hinge ticks (recomputed independently of the engine)
    _, rem, _ = derive_strides(num, den)
    acc = ticks = 0
    for _ in range(n):
        acc += rem
        if acc >= den:
            acc -= den
            ticks += 1
    assert ticks == expected_hinge_ticks(n, num, den)


# ── Validation ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("kwargs", [
    {"n": 1},
    {"den": 0},
    {"num": 0},
    {"n": 64, "collision_step": 2},
    {"collision_step": 97},
    {"num": 76.0},
])
def test_invalid_parameters_rejected(kwargs):
    with pytest.raises(FoldingEngineError):
        build_permutation(**kwargs)


# ── Deprecation shim ──────────────────────────────────────────────────────────
def test_remainder_step_keyword_deprecated_but_equivalent():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        old = build_permutation(remainder_step=23, den=53)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
    assert old == build_permutation(num=76, den=53)
