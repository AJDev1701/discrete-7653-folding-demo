# Changelog

## 0.1.2
- `build_permutation(n, num, den, collision_step)`: the generator ratio is now a parameter. Defaults (97, 76, 53, 7) reproduce the 0.1.1 permutation exactly (locked by `tests/fixtures/v0_1_1_permutation.json`).
- Fixed: strides are derived from num/den (`base = num // den`, `hinge = base + 1`). 0.1.1 used fixed strides 1/2, which were wrong for any ratio with `num // den != 1`.
- New invariant: hinge ticks = `floor(n * (num % den) / den)`, checked on every build.
- Input validation for `n`, `num`, `den` and the collision probe.
- CLI: `--n`, `--num`, `--den`, `--probe`.
- Deprecated: the `remainder_step=` keyword (maps to `num = den + remainder_step`). Note: the second positional argument is now `num` (was `remainder_step`).
- Tests: 1,012 -> 1,071.

## 0.1.1
- README sanitized, packaging fixed, CRLF-tolerant CLI, headless verifier, CI install check.
