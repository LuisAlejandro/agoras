#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API guard-stack order verification (QA residual: positional stack ordering).

Machine-checks every decorated method in the ten platform api modules for
the guard-stack invariant: decorators are applied top-to-bottom as
outermost-to-innermost, and the error wrap must be INNERMOST (closest to
the method definition) so guard-phase errors — AuthenticationError from
the auth attempt/ensure, client-presence messages — always propagate
unwrapped. A transposed stack (error_wrap above a guard) would flatten
guard-phase errors into generic exceptions and change the CLI's
actionable auth branch.

Checked per module:
  1. For each method's decorator stack: if ``guard_error_wrap`` is
     present, it must be the final decorator before ``def``.
  2. If ``guard_rate_limit`` is present without ``guard_error_wrap``, it
     must be the final decorator.
  3. No guard decorator (auth_attempt / assert_auth / ensure_auth_manager
     / token_presence / client_presence) may appear below ``guard_error_wrap``
     or ``guard_rate_limit`` in the stack.

Exit code 0 when every module passes; 1 otherwise. Text-based and offline.
"""

import re
import sys

from verify_harness import report_self_test, run

GUARD_DECORATORS = (
    "guard_ensure_auth_manager",
    "guard_token_presence",
    "guard_client_presence",
)
WRAP_DECORATOR = "guard_error_wrap"
RATE_DECORATOR = "guard_rate_limit"


def check_api_source(name, src):
    """Check one api module's source text for the guard-stack invariant."""
    failures = []
    lines = src.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^    (async )?def ", line)
        if not m:
            i += 1
            continue

        # Collect the decorator stack immediately above this def
        stack = []
        j = i - 1
        while j >= 0:
            dm = re.match(r"^    @(guard_\w+)", lines[j])
            if not dm:
                break
            stack.append(dm.group(1))
            j -= 1
        stack.reverse()  # top-to-bottom order

        method = line.split("def ")[1].split("(")[0]
        if not stack:
            i += 1
            continue

        # Invariant checks
        if WRAP_DECORATOR in stack and stack[-1] != WRAP_DECORATOR:
            failures.append(f"{name}.{method}: {WRAP_DECORATOR} not innermost (stack: {stack})")
        if WRAP_DECORATOR not in stack and RATE_DECORATOR in stack and stack[-1] != RATE_DECORATOR:
            failures.append(f"{name}.{method}: {RATE_DECORATOR} not innermost (stack: {stack})")
        wrap_pos = stack.index(WRAP_DECORATOR) if WRAP_DECORATOR in stack else len(stack)
        rate_pos = stack.index(RATE_DECORATOR) if RATE_DECORATOR in stack else len(stack)
        innermost_pos = min(wrap_pos, rate_pos)
        for pos, deco in enumerate(stack):
            if deco in GUARD_DECORATORS and pos > innermost_pos:
                failures.append(f"{name}.{method}: guard {deco} below wrap/rate-limit (stack: {stack})")
        i += 1

    return failures


def self_test():
    """Negative self-test: a transposed stack must be flagged."""
    failures = []
    good = (
        "    @guard_ensure_auth_manager\n"
        "    @guard_client_presence\n"
        '    @guard_rate_limit("post", 1.0)\n'
        '    @guard_error_wrap("op")\n'
        "    async def post(self):\n"
        "        return 1\n"
    )
    bad = (
        "    @guard_ensure_auth_manager\n"
        '    @guard_error_wrap("op")\n'
        "    @guard_client_presence\n"
        "    async def post(self):\n"
        "        return 1\n"
    )
    if check_api_source("fake", good):
        failures.append("self-test: valid stack flagged")
    f = check_api_source("fake", bad)
    if not any("not innermost" in item for item in f):
        failures.append("self-test: transposed error_wrap not flagged")
    return report_self_test(failures, "Self-test passed: the gate catches transposed guard stacks.")


if __name__ == "__main__":
    sys.exit(
        run(
            description=__doc__,
            check=check_api_source,
            self_test=self_test,
            success_message="All api modules pass the guard-stack invariant.",
        )
    )
