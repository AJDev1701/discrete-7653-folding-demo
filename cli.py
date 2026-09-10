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
"""

from __future__ import annotations

import argparse
import sys

from core.folding_engine import (
    BLOCK_SIZE,
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
                        help=f"Input string of exactly {BLOCK_SIZE} characters. "
                             f"If omitted, reads from stdin.")

    args = parser.parse_args()

    # Read input
    if args.input is not None:
        raw = args.input
    else:
        raw = sys.stdin.read()

    # Strip single trailing newline if present (shell piping artefact)
    if raw.endswith("\n"):
        raw = raw[:-1]

    if len(raw) != BLOCK_SIZE:
        print(
            f"ERROR: Input must be exactly {BLOCK_SIZE} characters, "
            f"got {len(raw)}.",
            file=sys.stderr,
        )
        return 1

    try:
        pi   = build_permutation()
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
