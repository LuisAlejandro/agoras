#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared driver for the platform-parity verify gates.

Carries the parts every gate repeats — the platform list, the per-platform
source loader, argv parsing with ``--self-test``, and the PASS/FAIL loop.
Each gate keeps its own invariants, fixtures, and expectation tables.
"""

import argparse
from pathlib import Path

PLATFORM_DIR = Path("packages/platforms/src/agoras/platforms")

PLATFORMS = [
    "x",
    "discord",
    "telegram",
    "threads",
    "facebook",
    "instagram",
    "linkedin",
    "youtube",
    "tiktok",
    "whatsapp",
]


def load_source(platform, filename="api.py"):
    """Read one platform module's source text."""
    return (PLATFORM_DIR / platform / filename).read_text()


def run(
    *,
    description,
    check,
    self_test,
    success_message,
    platforms=None,
    filename="api.py",
    add_arguments=None,
    on_args=None,
    format_failure=None,
):
    """
    Parse argv, dispatch ``--self-test``, then run ``check`` per platform.

    ``check(name, src)`` returns a list of failure strings; ``format_failure``
    renders each one for output (default: unchanged).
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--self-test", action="store_true", help="run negative self-tests and exit")
    if add_arguments:
        add_arguments(parser)
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if on_args:
        on_args(args)

    names = getattr(args, "platforms", None) or list(platforms or PLATFORMS)
    render = format_failure or (lambda name, failure: failure)

    all_failures = []
    for name in names:
        failures = check(name, load_source(name, filename))
        if failures:
            for failure in failures:
                print(f"[FAIL] {render(name, failure)}")
                all_failures.append(failure)
        else:
            print(f"[PASS] {name}")

    if all_failures:
        print(f"\n{len(all_failures)} failure(s)")
        return 1
    print(f"\n{success_message}")
    return 0


def report_self_test(failures, success_message):
    """Print the shared self-test verdict and return its exit code."""
    if not failures:
        print(success_message)
        return 0
    for item in failures:
        print(f"[FAIL] {item}")
    return 1
