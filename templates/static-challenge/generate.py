#!/usr/bin/env python3
"""generate.py -- build this challenge's player-facing artifact(s).

Run it from anywhere (it resolves paths relative to this file):

    python3 -I generate.py

It writes into files/ next to this script. Rerunning is idempotent: the bytes
are fully determined by the constants below, so the artifact never drifts. A
drifting artifact breaks artifact pinning the moment a course pins it by
sha256, and silently invalidates any fact the lessons bake about it.

Replace the body with your own build. The contract this template demonstrates:
  * the artifact ENCODES the answer; it never stores the flag string itself;
  * the build is deterministic, so solve.py and any sha256 pin stay valid;
  * nothing here is player-facing, so it may use any dependency you like, as
    long as the OUTPUT in files/ is what the player gets.
"""
from __future__ import annotations

import os

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(HERE, "files")

# The token the player must recover. meta.yml's flag is ESPILON{<TOKEN>}.
# Keep this and the flag in meta.yml in step; solve.py checks they agree.
TOKEN = "xor_k3y_rec0very"
XOR_KEY = 0x5A


def build() -> None:
    os.makedirs(FILES, exist_ok=True)
    plaintext = (
        "depot log 2026-03-04\n"
        "note: recovered marker TOKEN=%s\n"
        "end of record\n" % TOKEN
    ).encode("utf-8")
    blob = bytes(b ^ XOR_KEY for b in plaintext)
    out = os.path.join(FILES, "sample.bin")
    with open(out, "wb") as fh:
        fh.write(blob)
    print("wrote %s (%d bytes)" % (out, len(blob)))


if __name__ == "__main__":
    build()
