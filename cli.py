#!/usr/bin/env python3
"""
discrete-7653-folding-demo CLI

Applies or inverts the 7653 deterministic folding permutation to text input.
Operates entirely offline via standard I/O. No network dependencies.

Usage:
    echo "YOURINPUTSTRING..." | python cli.py --permute
    echo "YOURINPUTSTRING..." | python cli.py --invert
    python cli.py --permute --input "YOURINPUTSTRING..."
    python cli.py --invert  --input "YOURINPUTSTRING..."
    python cli.py --permute --n 101 --num 130 --den 53 --probe 7 --input "..."
"""

from __future__ import annotations

import argparse
import sys

from core.folding_engine import (
    BLOCK_SIZE,
    COLLISION_STEP,
    GENERATOR_DEN,
    GENERATOR_NUM,
    FoldingEngineError,
    build_permutation,
    invert_permute,
    permute,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="7653 Deterministic Folding Permutation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--permute", action="store_true",
                      help="Apply the 7653 folding permutation to input.")
    mode.add_argument("--invert", action="store_true",
                      help="Invert the 7653 folding permutation on input.")
    parser.add_argument("--input", "-i", type=str, default=None,
                        help="Input string of exactly N characters (default N=97). "
                             "If omitted, reads from stdin.")
    parser.add_argument("--n", type=int, default=BLOCK_SIZE,
                        help=f"Block size N (default {BLOCK_SIZE}).")
    parser.add_argument("--num", type=int, default=GENERATOR_NUM,
                        help=f"Generator numerator (default {GENERATOR_NUM}).")
    parser.add_argument("--den", type=int, default=GENERATOR_DEN,
                        help=f"Generator denominator (default {GENERATOR_DEN}).")
    parser.add_argument("--probe", type=int, default=COLLISION_STEP,
                        help=f"Collision probe step, coprime with N (default {COLLISION_STEP}).")

    args = parser.parse_args()

    # Read input
    if args.input is not None:
        raw = args.input
    else:
        raw = sys.stdin.read()

    # Strip one trailing line ending if present (shell piping artefact).
    # Handles both POSIX "\n" and Windows "\r\n".
    if raw.endswith("\r\n"):
        raw = raw[:-2]
    elif raw.endswith("\n"):
        raw = raw[:-1]

    if len(raw) != args.n:
        print(
            f"ERROR: Input must be exactly {args.n} characters, "
            f"got {len(raw)}.",
            file=sys.stderr,
        )
        return 1

    try:
        pi   = build_permutation(n=args.n, num=args.num, den=args.den,
                                 collision_step=args.probe)
        seq  = list(raw)

        if args.permute:
            result = permute(seq, pi)
        else:
            result = invert_permute(seq, pi)

        print("".join(result))
        return 0

    except FoldingEngineError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
