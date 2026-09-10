# discrete-7653-folding-demo

Deterministic permutation engine using the **7653 generator ratio** (76 / 53).

> **Classification:** `STANDALONE_DETERMINISTIC_PERMUTATION`
> **Solve claims:** `FALSE`
> **External dependencies:** Zero

---

## What It Does

Generates a unique, reproducible 97-position permutation driven by the 7653 recurrence:

| Parameter | Value |
|---|---|
| Block size N | 97 |
| Generator ratio | 76 / 53 |
| Base step | 1 (76 // 53) |
| Remainder step | 23 (76 % 53) |
| Hinge step | 2 (on carry) |
| Collision probe step | 7 (coprime with 97) |
| Single-step ticks | 55 |
| Hinge-step ticks | 42 |
| Total pointer shift | 55(1) + 42(2) = 139 |

## Guaranteed Invariants

- **Bijectivity:** `set(permutation) == {0..96}`, `len == 97`
- **Exact inversion:** `invert_permute(permute(seq)) == seq` for all length-97 sequences
- **Coprimality guard:** Collision step is rejected if `gcd(step, N) != 1`
- **Determinism:** Identical output on every call with default parameters

## Usage

```bash
# Apply permutation
echo "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR" | python cli.py --permute

# Invert permutation
python cli.py --invert --input "..."
```

## Testing

```bash
pip install pytest
pytest
```

1 008 test cases: 1 000 randomised ASCII round-trips + 8 structural invariant assertions.

## Scope Boundary

This repository implements and verifies the folding permutation only.
It contains no substitution cipher, no crib alignment tests, and makes
no claims regarding Kryptos K4 or any cryptographic solution.

---

*MIT License | 2026 Alex J. Dalhaus (AJDev1701)*
