# Live E2E integration tests

Manual smoke tests against real platform APIs. Not run in CI by default.

## Prerequisites

- `virtualenv/bin/agoras` installed (`make virtualenv` — uses `--copies`)
- `jq` on PATH
- `authorize.env` and/or `unattended.env` at repo root (never commit)
- `export AGORAS_STORAGE_DIR=/tmp/agoras-test-e2e` (must **not** be `~/.agoras`)

Use dedicated test platform accounts. Do not pipe logs to shared systems. Do not run `agoras utils tokens show` or `agoras utils tokens unattended-format` in scripted output. To build `unattended.env` from authorize storage, run `agoras utils tokens unattended-format` locally and redirect to a file.

## Authorize-path run

1. Fill `authorize.env` with `AGORAS_STORAGE_DIR` and platform OAuth creds for `authorize-platforms.sh`, plus any test-time vars (`FACEBOOK_OBJECT_ID` for facebook share tests, `WHATSAPP_RECIPIENT` for whatsapp tests).
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

Preflight fails fast if stored tokens are missing (`utils tokens list` per platform, before post tests). Post tests use stored credentials; OAuth app secrets are not re-checked here.

## Unattended-path run

1. Export `AGORAS_STORAGE_DIR`
2. Fill `unattended.env` (including test-only `FEED_URL` and Google Sheets fixtures)
3. Run:

```bash
tests/test-unattended.sh all
# or: tests/test-unattended.sh x
```

Clears storage at start, seeds from env vars, runs utils (feed last/random, schedule-run) at end.

On exit, refresh-capable OAuth credentials are refreshed noninteractively, then rotated `*_REFRESH_TOKEN` values in `unattended.env` are patched from tokens saved during the run. Manual re-export still required if env was stale before any successful auth: `agoras utils tokens unattended-format`.

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

Clears storage at start, runs per-platform post/video cases via `agoras publish`, then legacy feed (`last-from-feed`, `random-from-feed`) and schedule actions. Does not run tokens-list smoke. Patches `*_REFRESH_TOKEN` lines in `unattended.env` on exit (same as unattended suite).

## CI guard

Scripts exit when `CI` or `GITHUB_ACTIONS` is set.

## MVP checklist highlights

| Area | Authorize | Unattended |
| ------ | ----------- | ------------ |
| x post/like/share/delete | yes | yes |
| threads share | yes | yes |
| discord video | yes | yes |
| tiktok post (slideshow) | skip if unavailable | skip if unavailable |
| utils feed/schedule | no | yes |
| legacy publish feed/schedule | no | yes (legacy suite only) |
| utils tokens list (preflight) | yes | no (env vars only; storage cleared at start) |

## Skip policy

Unsupported or blocked actions print `SKIP: <reason>` and return success for that case. Suite continues. See `tests/skip-registry.md`.

## Phase 2 actions (included)

- **x**, **threads**, **instagram**, **linkedin**, **telegram**, **whatsapp** video
- **whatsapp template** (requires `WHATSAPP_TEMPLATE_NAME` in env; optional `WHATSAPP_TEMPLATE_LANGUAGE`, default `en`)
- **feed-publish** and **schedule-run** on one network (`UTILS_TEST_NETWORK`, default `x`); posts are deleted after each utils run

## Optional env vars

| Variable | Purpose |
| ---------- | --------- |
| `UTILS_TEST_NETWORK` | Network for utils feed/schedule tests (default `x`) |
| `WHATSAPP_TEMPLATE_NAME` | Pre-approved template for whatsapp template test |
| `WHATSAPP_TEMPLATE_LANGUAGE` | Template language code (default `en`) |
