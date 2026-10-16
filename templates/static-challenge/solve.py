#!/usr/bin/env python3
"""solve.py -- the reference solver.

It PROVES the challenge is solvable from the shipped artifact alone and that the
flag it yields matches meta.yml byte for byte. Run it in one command:

    python3 -I solve.py

Keep it stdlib-only where you can (or pin any extra dependency in a comment at
the top), so a reviewer can run it without setup. A static challenge that has no
runnable reference solver is unproven: do not ship one.
"""
from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACT = os.path.join(HERE, "files", "sample.bin")


def solve() -> str:
    with open(ARTIFACT, "rb") as fh:
        blob = fh.read()
    # Single-byte XOR: the key is the one byte whose decode is all printable.
    for key in range(256):
        cand = bytes(b ^ key for b in blob)
        if all(c == 0x09 or c == 0x0a or 0x20 <= c <= 0x7e for c in cand):
            m = re.search(rb"TOKEN=([A-Za-z0-9_]+)", cand)
            if m:
                return "ESPILON{%s}" % m.group(1).decode("ascii")
    raise SystemExit("solve failed: no printable single-byte XOR carried a TOKEN marker")


def _expected_flag() -> str:
    """Read the flag from meta.yml without a yaml dependency, so the solver's
    own answer is checked against the shipped flag on every run."""
    with open(os.path.join(HERE, "meta.yml"), encoding="utf-8") as fh:
        meta = fh.read()
    m = re.search(r"^flag:\s*(ESPILON\{[^{}]+\})\s*$", meta, re.MULTILINE)
    return m.group(1) if m else ""


if __name__ == "__main__":
    flag = solve()
    print(flag)
    expected = _expected_flag()
    assert flag == expected, "solver flag %r != meta.yml flag %r" % (flag, expected)
    print("OK: solver output matches meta.yml flag")
