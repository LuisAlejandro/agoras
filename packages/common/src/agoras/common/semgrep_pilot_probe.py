# Semgrep pilot probe — delete after criterion 2 verification.

import subprocess


def insecure_probe(user_input: str) -> None:
    subprocess.call(user_input, shell=True)
