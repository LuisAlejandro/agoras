================
Maintainer Guide
================

Quick reminders for Agoras.

Feature work
------------

1. Plan and implement on a feature branch (``feature/*`` → ``develop``).
2. Run QA, lint/build, open or update a PR to ``develop``.

Repeat until ready to ship.

Commit messages
---------------

Subjects feed ``HISTORY.rst`` via gitchangelog, then GitHub release notes on ``make release-*``.

- ``[ADD]`` — Added (new user-facing capability)
- ``[FIX]`` — Fixed (bug or broken behavior)
- ``[REF]`` — Changed (behavior change that is not a new feature)
- ``[DEL]`` — Removed

Format: ``[TAG] Imperative user-facing summary.`` Non-user-facing work (deps, lint, sync, CI): append ``!cosmetic`` / ``!refactor`` / ``!wip``, or use a ``CI:`` prefix, so it is omitted from HISTORY. PR titles may stay Conventional-style; only commit subjects use these tags.

Release
-------



From **clean** ``develop``:

- **Preflight** — ``make release-preflight``.
- **Publish** — ``make release-patch`` (or ``release-minor`` / ``release-major``).
- **Rollback** — ``VERSION=<version> make undo-release``.

Preflight: ``make image``, ``make dependencies``, ``make build``, ``make format``, ``make lint``, ``make test`` (``test`` = coverage).
Release flow: ``scripts/release.sh`` (via Makefile ``release-*`` targets).
Post-bump hooks: ``.bumpversion.cfg`` → ``[maintainer-tools]``.

PR CI (pointers)
----------------

- **Pull Request** — ``.github/workflows/pr.yml`` on PRs to ``develop``.

Before ``make release-*``
-------------------------

- Tools: ``git``, git-flow, Docker (running), ``make``, ``gh``, bumpversion, GPG (``user.signingkey``).
- Clean working tree (release stops if format mutates files).

One-time GitHub setup
---------------------

- ``develop`` — PR + checks from ``pr.yml``.
- ``master`` — restrict pushes.
- ``release/*`` — ``push.yml`` lists ``release/**``; release tooling waits for the whole **Push** workflow at the exact branch SHA.
- Tags — restrict creation to maintainers.

For Tetra cutovers, run ``rosey-maintain protect-github --repo <repo> --trust-preflight``,
open the check window with ``--window open --apply``, then close it after a probe with
one ``--observed-check <context>`` per live check-run name. Rollback cancels matching
Push, Publish Release, and Artifacts runs, waits for terminal state, then deletes refs.
