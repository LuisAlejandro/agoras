# agoras (CLI)

Command-line interface for managing social network posts.

## Installation

```bash
pip install agoras
```

This automatically installs all dependencies:
- agoras-common
- agoras-media
- agoras-core
- agoras-platforms

## Usage

```bash
# Post to Facebook
agoras facebook post \
    --facebook-access-token "$TOKEN" \
    --status-text "Hello World" \
    --status-link "https://example.com"

# Post to X (Twitter)
agoras x post \
    --x-api-key "$KEY" \
    --x-api-secret "$SECRET" \
    --x-access-token "$TOKEN" \
    --x-access-token-secret "$TOKEN_SECRET" \
    --status-text "Hello X!"

# See all commands
agoras --help
```

## Dependencies

- agoras-platforms (and all its dependencies)
