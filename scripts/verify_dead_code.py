#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dead-code gate: fail the build on unused code.

Runs vulture over the five ``packages/*/src/agoras`` trees with the
repo's allowlist and ``--min-confidence 90``. The allowlist
(``scripts/vulture-allowlist.txt``) is bounded: entries need a one-line
reason (framework protocol, dynamic dispatch). New dead code must be
removed or added to the allowlist with justification — the gate never
grows silently.

Exit code 0 when the tree is clean (vulture reports only allowlisted
names); 1 otherwise. Text-based and offline (after install).
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TREES = [
    "packages/common/src/agoras",
    "packages/media/src/agoras",
    "packages/core/src/agoras",
    "packages/platforms/src/agoras",
    "packages/cli/src/agoras",
]
ALLOWLIST = ROOT / "scripts" / "vulture-allowlist.txt"


def _allowed_names():
    """Parse bare names from the allowlist file (skip comments/blanks)."""
    names = set()
    for line in ALLOWLIST.read_text().splitlines():
        name = line.split("#", 1)[0].strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name or ""):
            names.add(name)
    return names


def run_gate():
    """Run vulture and filter allowlisted names; return the offending lines.

    Fails closed: a missing vulture install or a scanner error is a gate
    failure, never a pass.
    """
    import importlib.util

    if importlib.util.find_spec("vulture") is None:
        return ["[FAIL] vulture is not installed -- run pip install -r requirements-dev.txt"]
    proc = subprocess.run(
        [sys.executable, "-m", "vulture", *TREES, str(ALLOWLIST), "--min-confidence", "90"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 and not proc.stdout.strip():
        return [f"[FAIL] vulture scanner error (exit {proc.returncode}): {proc.stderr.strip()[:200]}"]
    allowed = _allowed_names()
    failures = []
    for line in proc.stdout.splitlines():
        m = re.search(r"unused (?:variable|function|class|attribute|import|property) '([A-Za-z_][A-Za-z0-9_]*)'", line)
        if m and m.group(1) not in allowed:
            failures.append(f"[FAIL] {line}")
    return failures


def self_test():
    """Negative self-test: run the real gate against a dirty temp tree."""
    failures = []
    import tempfile

    # Unused imports report at 100% confidence — inside the enforced
    # --min-confidence 90 threshold (bare functions report at 60%).
    with tempfile.TemporaryDirectory() as tmp:
        dirty = Path(tmp) / "dirty_mod.py"
        dirty.write_text("import verifydeadcodeunusedprobe\n")
        proc = subprocess.run(
            [sys.executable, "-m", "vulture", str(dirty), "--min-confidence", "90"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if "verifydeadcodeunusedprobe" not in proc.stdout:
            failures.append("self-test: unused-symbol fixture not flagged by vulture")

    # The gate itself must flag the probe through its own filter path.
    global TREES
    saved = TREES
    try:
        with tempfile.TemporaryDirectory() as tmp:
            dirty = Path(tmp) / "dirty_mod.py"
            dirty.write_text("import verifydeadcodeunusedprobe\n")
            TREES = [str(dirty.relative_to(ROOT)) if str(dirty).startswith(str(ROOT)) else str(dirty)]
            gate_failures = run_gate()
            if not any("verifydeadcodeunusedprobe" in f for f in gate_failures):
                failures.append("self-test: run_gate filter path drops the probe")
    finally:
        TREES = saved
    if not failures:
        print("Self-test passed: the gate catches unused code.")
        return 0
    for item in failures:
        print(f"[FAIL] {item}")
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run negative self-tests and exit")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    failures = run_gate()
    if failures:
        for f in failures:
            print(f)
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("No unlisted dead code found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
