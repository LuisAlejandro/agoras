"""Intentional lint failure for CI auto-merge probe. Remove when probe completes."""

# flake8 E501: line too long
ci_probe_line = "this line intentionally exceeds the configured max line length of one hundred twenty characters for the agoras flake8 probe"
