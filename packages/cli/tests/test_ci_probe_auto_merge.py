"""Probe v10: synchronize-only retrigger (no MCP dispatch). Cursor should delete this file."""


def test_ci_probe_auto_merge_v10_intentional_failure():
    assert False, "CI probe v10: intentional failure — automation should fix, synchronize CI, auto-merge"
