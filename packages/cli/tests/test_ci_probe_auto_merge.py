"""Probe v12: Cursor fix + synchronize retrigger + auto-merge. Cursor should delete this file."""


def test_ci_probe_auto_merge_v12_intentional_failure():
    assert False, "CI probe v12: intentional failure — automation should fix, synchronize, auto-merge"
