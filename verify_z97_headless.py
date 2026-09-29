#!/usr/bin/env python3
"""
verify_z97_headless.py: zero-dependency verification harness.

Rebuilds the 97-position permutation from first principles (stdlib only;
this file does not import the package) and checks it against fixed anchors.
If the repo's core package can be imported, it also checks that core
produces the identical permutation.

Anchor values are the ones the engine at 1e5908a actually produces.
Exit status: 0 = all checks pass, 1 = any failure.
"""

import math
import sys
import time

N, NUM, DEN, HINGE, PROBE = 97, 76, 53, 2, 7
BASE, REM = NUM // DEN, NUM % DEN  # 1, 23

# Anchors (computed from the engine, integer-only)
EXPECT_HEAD = [0, 1, 3]
EXPECT_SUM = N * (N - 1) // 2          # 4656
EXPECT_TICKS = (55, 42)                # (base, hinge)
EXPECT_CYCLES = [38, 35, 18, 3, 1, 1, 1]
EXPECT_ORDER = 11970                   # lcm of the cycle lengths


def build():
    occ, perm, ptr, acc = [False] * N, [0] * N, N - 1, 0
    base = hinge = 0
    for i in range(N):
        a = acc + REM
        if a >= DEN:
            step, acc, hinge = HINGE, a - DEN, hinge + 1
        else:
            step, acc, base = BASE, a, base + 1
        c = (ptr + step) % N
        while occ[c]:
            c = (c + PROBE) % N
        occ[c], perm[i], ptr = True, c, c
    return perm, (base, hinge)


def cycles(p):
    seen, out = [False] * len(p), []
    for i in range(len(p)):
        if not seen[i]:
            n, j = 0, i
            while not seen[j]:
                seen[j], j, n = True, p[j], n + 1
            out.append(n)
    return sorted(out, reverse=True)


def main():
    t0 = time.perf_counter()
    P, ticks = build()
    inv = [0] * N
    for i, t in enumerate(P):
        inv[t] = i
    cyc = cycles(P)
    order = 1
    for c in cyc:
        order = order * c // math.gcd(order, c)

    checks = [
        ("Field bound", len(P) == N and all(0 <= x < N for x in P)),
        ("Stride ticks 55/42", ticks == EXPECT_TICKS),
        ("Canonical head", P[:3] == EXPECT_HEAD),
        ("Bijective inversion", all(P[inv[k]] == k for k in range(N))
                                and sorted(P) == list(range(N))),
        ("Conserved sum", sum(P) == EXPECT_SUM),
        ("Cycle spectrum", cyc == EXPECT_CYCLES and sum(cyc) == N),
        ("Group order", order == EXPECT_ORDER),
        ("Probe coprimality", math.gcd(PROBE, N) == 1),
    ]
    try:
        from core.folding_engine import build_permutation
        checks.append(("Matches core package", build_permutation() == P))
    except ImportError:
        pass

    ms = (time.perf_counter() - t0) * 1000
    ok = all(r for _, r in checks)
    for name, r in checks:
        print(f"[{'PASS' if r else 'FAIL'}] {name}")
    print(f"head={P[:3]} sum={sum(P)} cycles={cyc} order={order}")
    print(f"{'ALL PASS' if ok else 'FAILURE'} in {ms:.2f} ms")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
