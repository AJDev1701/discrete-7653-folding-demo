# discrete-7653-folding-demo

A deterministic permutation engine stepped by a rational generator ratio num/den. The default example is 76/53 over a 97-position block.

> **Classification:** `STANDALONE_DETERMINISTIC_PERMUTATION`
> **Cryptographic claims:** None
> **External dependencies:** Zero

---

## What It Does

It builds a single reproducible permutation of 97 positions from an integer-only stepping recurrence.

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

### Why N = 97

97 is prime, so every nonzero probe step is coprime with the block size and the collision probe is guaranteed to visit every slot. It is also the smallest prime at which the 76/53 accumulator completes 42 full carries, which gives a non-trivial mix of single and hinge steps.

## Choosing Parameters (v0.1.2)

`build_permutation(n=97, num=76, den=53, collision_step=7)`. All four are optional, and the defaults reproduce the v0.1.1 permutation exactly.

- Strides come from the ratio: `base = num // den`, `rem = num % den`, `hinge = base + 1`.
- Valid inputs: `n >= 2`, `den >= 1`, `num >= 1`, and `gcd(collision_step, n) == 1`. Anything else raises `FoldingEngineError`.
- `n` does not have to be prime. A coprime probe is enough to reach every slot. Prime `n` simply makes every nonzero probe valid.
- Hinge (carry) steps over one pass: `floor(n * rem / den)`. The default gives floor(97 * 23 / 53) = 42.

```bash
echo "$INPUT" | python cli.py --permute --n 97 --num 76 --den 53 --probe 7
```

## Guaranteed Invariants

- **Bijectivity:** `set(permutation) == {0..96}`, `len == 97`
- **Exact inversion:** `invert_permute(permute(seq)) == seq` for every length-97 sequence
- **Coprimality guard:** a collision step is rejected if `gcd(step, N) != 1`
- **Determinism:** identical output on every call with default parameters
- **Integer-only:** no floating-point arithmetic anywhere in the engine

## Reference Values

With default parameters, any correct build produces exactly these values. `python verify_z97_headless.py` rebuilds the permutation with the standard library only and checks all of them.

| Check | Value |
|---|---|
| First three entries | `[0, 1, 3]` |
| Cycle type | `[38, 35, 18, 3, 1, 1, 1]` |
| Permutation order (lcm of cycle lengths) | 11,970 |
| SHA-256 of the permutation as compact JSON | `a01406b0c6e3444818942e6c215b24e301e1360abc78a22b3166bd68dcd8f1f7` |
| Order-sensitive sum, `sum(i * P[i]) mod 97` | 73 |
| Plain sum (sanity only) | 4,656 |

The plain sum is the same for every permutation of 97 positions, so it cannot detect a wrong ordering. Use the SHA-256 for that. An order of 11,970 is a property of the cycle structure, not a security parameter.

## Usage

```bash
# Build a neutral 97-character test string
INPUT=$(python -c "print(('ABCDEFGHIJKLMNOPQRSTUVWXYZ'*4)[:97])")

# Apply the permutation
echo "$INPUT" | python cli.py --permute

# Round-trip: permute, then invert, and get the original back
echo "$INPUT" | python cli.py --permute | python cli.py --invert
```

After `pip install .`, the same commands work through the `fold` entry point:

```bash
echo "$INPUT" | fold --permute
```

## Testing

```bash
pip install pytest
pytest
```

The suite runs **1,073 test cases**:

- 1,000 randomized printable-ASCII round-trips (seeded, reproducible)
- 3 non-coprime collision-step rejections (steps 97, 194, 0)
- 9 structural checks: bijectivity, length, determinism, inverse composition, coprime acceptance, length-mismatch rejection, generator ratio, probe coprimality, and stride counts (55 / 42)
- 59 parameterization tests (v0.1.2): frozen v0.1.1 regression lock, a 48-case parameter grid, 6 invalid-parameter rejections, and the deprecation shim
- 2 reference-value tests (v0.1.3): permutation SHA-256 and the order-sensitive sum

## Scope Boundary

This repository implements and verifies one integer permutation and its inverse, and nothing more. There is no substitution layer and no keying, and it makes no claim to encrypt, decrypt, or solve anything. It is a teaching artifact for finite-ring stepping, rational pacing, and exact invertibility.

---

*MIT License | 2026 Alex J. Dalhaus (AJDev1701)*
