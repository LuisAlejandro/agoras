================
Maintainer Guide
================

Rosey maintainer workflow for Agoras. Each step is a skill invocation; details
live in the skill files under ``.cursor/skills/``.

Workflow overview
-----------------

For each feature:

1. ``rosey-lfg-code`` — brainstorm requirements, create a plan, implement on a
   feature branch (via ``rosey-brainstorm``, ``rosey-plan``, ``rosey-work``).
2. ``rosey-lfg-quality`` — QA review, lint/build after fixes, open or update PR
   (via ``rosey-qa``, ``rosey-pr``). PRs target ``develop``; CI auto-merges when
   configured.

Repeat 1–2 for every feature in the release.

When ``develop`` is ready to ship:

3. ``rosey-release`` — publish a **release** (patch, minor, or major). Five gates:
   (1) Docker preflight (``make lint``, ``make format``, ``make test``;
   on Python repos ``make test`` runs coverage),
   (2) ``release/<version>`` branch pushed,
   (3) ``push.yml`` CI on the release branch,
   (4) tag and GitHub release,
   (5) ``release.yml`` after publish
   (PyPI build and publish) —
   ``rosey-release`` confirms the workflow passed. Patch releases may attach a
   retroactive milestone. On failure, rolls back with
   ``VERSION=<version> make undo-release`` and halts. Optional post-bump hooks
   live in ``.bumpversion.cfg`` under ``[rosey-maintainer]``.

Skill reference
---------------

``rosey-lfg-code``
  Autonomous code stage: requirements → plan → implementation and lint/build.
  Emits ``ROSEY_LFG_QUALITY_HANDOFF`` for the quality stage.

``rosey-lfg-quality``
  Autonomous quality stage: QA autofix, post-review lint, PR create/update.
  Emits ``<promise>DONE</promise>`` when the PR is ready. Does not merge or
  publish releases.

``rosey-release``
  Release only: ``patch`` (default), ``minor``, or ``major``. Invoke from clean
  ``develop``. Arguments: ``[mode:interactive|mode:non-interactive] [patch|minor|major]``.

Prerequisites (checked by release script)
-------------------------------------------------

- ``git``, ``git flow``, ``docker`` (daemon running), ``make``, ``gh`` (authenticated),
  ``bumpversion``, ``gpg``
- ``user.signingkey`` configured with secret key available locally
- Clean working tree (no modified or untracked files)

GitHub branch protection (configure once)
-----------------------------------------

**``develop``** — require PR; status checks: Linting, Integration Tests, Unit
tests, Documentation, Finish.

**``master``** — restrict pushes; disallow force pushes.

**``release/*``** — Push workflow runs; script waits for
Release Gate before tagging.

**Version tags** — restrict creation to maintainers; prevent tag deletion except
by admins.
