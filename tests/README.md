# Live E2E integration tests

Manual smoke tests against real platform APIs. Not run in CI by default.

## Prerequisites

- `virtualenv/bin/agoras` installed (`make virtualenv` — uses `--copies`)
- `jq` on PATH
- `authorize.env` and/or `unattended.env` at repo root (never commit)
- `export AGORAS_STORAGE_DIR=/tmp/agoras-test-e2e` (must **not** be `~/.agoras`)

Use dedicated test platform accounts. Do not pipe logs to shared systems. Do not run `agoras utils tokens show` or `agoras utils tokens unattended-format` in scripted output. To build `unattended.env` from authorize storage, run `agoras utils tokens unattended-format` locally and redirect to a file.

## Authorize-path run

1. Fill `authorize.env` (include `export AGORAS_STORAGE_DIR=...`)
2. Authorize platforms:

```bash
tests/authorize-platforms.sh          # all platforms
tests/authorize-platforms.sh facebook   # one platform
```

1. Run:

```bash
tests/test-authorize.sh all
# or: tests/test-authorize.sh facebook
```

Preflight fails fast if stored tokens are missing.

## Unattended-path run

1. Export `AGORAS_STORAGE_DIR`
2. Fill `unattended.env` (including test-only `FEED_URL` and Google Sheets fixtures)
3. Run:

```bash
tests/test-unattended.sh all
# or: tests/test-unattended.sh x
```

Clears storage at start, seeds from env vars, runs utils (feed last/random, schedule-run) at end.

## Legacy publish-path run

Same `unattended.env` and CI guard as the unattended suite, but exercises the deprecated `agoras publish` command instead of platform subcommands.

1. Export `AGORAS_STORAGE_DIR`
2. Fill `unattended.env`
3. Run:

```bash
tests/test-legacy-unattended.sh all
# or: tests/test-legacy-unattended.sh x
# or: tests/test-legacy-unattended.sh twitter   # alias for x
```

Clears storage at start, runs per-platform post/video cases via `agoras publish`, then legacy feed (`last-from-feed`, `random-from-feed`) and schedule actions. Does not run tokens-list smoke.

## CI guard

Scripts exit when `CI` or `GITHUB_ACTIONS` is set unless `AGORAS_LIVE_E2E=1`.

## MVP checklist highlights

| Area | Authorize | Unattended |
|------|-----------|------------|
| x post/like/share/delete | yes | yes |
| threads share | yes | yes |
| discord video | yes | yes |
| tiktok post (slideshow) | skip if unavailable | skip if unavailable |
| utils feed/schedule | no | yes |
| legacy publish feed/schedule | no | yes (legacy suite only) |
| utils tokens list | yes | storage platforms only |

## Skip policy

Unsupported or blocked actions print `SKIP: <reason>` and return success for that case. Suite continues. See `tests/skip-registry.md`.

## Phase 2 actions (included)

- **x**, **threads**, **instagram**, **linkedin**, **telegram**, **whatsapp** video
- **whatsapp template** (requires `WHATSAPP_TEMPLATE_NAME` in env; optional `WHATSAPP_TEMPLATE_LANGUAGE`, default `en`)
- **feed-publish** and **schedule-run** on one network (`UTILS_TEST_NETWORK`, default `x`); posts are deleted after each utils run

## Optional env vars

| Variable | Purpose |
|----------|---------|
| `UTILS_TEST_NETWORK` | Network for utils feed/schedule tests (default `x`) |
| `WHATSAPP_TEMPLATE_NAME` | Pre-approved template for whatsapp template test |
| `WHATSAPP_TEMPLATE_LANGUAGE` | Template language code (default `en`) |
| `AGORAS_LIVE_E2E=1` | Override CI guard |
