"""Probe v3 re-run: intentional failure for Cursor automation → auto-merge test."""


def test_ci_probe_auto_merge_v3_intentional_failure():
    assert False, "CI probe v3 re-run: Cursor should fix and trigger auto-merge"
