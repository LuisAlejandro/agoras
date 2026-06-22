"""Probe v9: repeat validation after v8 success. Cursor should delete this file."""


def test_ci_probe_auto_merge_v9_intentional_failure():
    assert False, "CI probe v9: intentional failure — automation should fix, dispatch, auto-merge"
