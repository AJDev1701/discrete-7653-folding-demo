"""Reference values for the default permutation (v0.1.3)."""

import hashlib
import json

from core.folding_engine import build_permutation

EXPECT_SHA256 = "a01406b0c6e3444818942e6c215b24e301e1360abc78a22b3166bd68dcd8f1f7"


def test_permutation_sha256():
    p = build_permutation()
    digest = hashlib.sha256(json.dumps(p, separators=(",", ":")).encode()).hexdigest()
    assert digest == EXPECT_SHA256


def test_order_sensitive_sum():
    p = build_permutation()
    assert sum(i * x for i, x in enumerate(p)) % 97 == 73
