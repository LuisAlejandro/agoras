# File Migration Mapping Reference

**Date**: 2026-01-11
**Purpose**: Complete reference of old → new file mappings for the package split migration

This document serves as a reference for finding where old monolithic code has been migrated.

## Quick Reference

| Old Package | New Package | Description |
|:------------|:------------|:------------|
| `agoras/core/` (base, interfaces) | `packages/core/` | Core abstractions and business logic |
| `agoras/core/` (platform wrappers) | `packages/platforms/` | Platform implementations |
| `agoras/core/api/` (managers) | `packages/platforms/` | Platform API managers |
| `agoras/core/api/clients/` | `packages/platforms/` | HTTP clients |
| `agoras/core/api/auth/` (platform) | `packages/platforms/` | Platform auth managers |
| `agoras/core/api/auth/` (base) | `packages/core/` | Auth infrastructure |
| `agoras/core/media/` | `packages/media/` | Image/video processing |
| `agoras/core/feed/` | `packages/core/` | Feed parsing |
| `agoras/core/sheet/` | `packages/core/` | Google Sheets |
| `agoras/core/logger.py` | `packages/common/` | Logging |
| `agoras/core/utils.py` | `packages/common/` | Utilities |
| `agoras/cli/` | `packages/cli/` | CLI interface |
| `agoras/commands/` | `packages/cli/commands/` | Commands |
| `agoras/cli.py` | `packages/cli/src/agoras/cli/main.py` | Entry point |

## Detailed Mappings

### Core Platform Wrappers (10 files)

agoras/core/ → packages/platforms/src/agoras/platforms/

```
agoras/core/facebook.py    → packages/platforms/src/agoras/platforms/facebook/wrapper.py
agoras/core/instagram.py   → packages/platforms/src/agoras/platforms/instagram/wrapper.py
agoras/core/linkedin.py    → packages/platforms/src/agoras/platforms/linkedin/wrapper.py
agoras/core/discord.py     → packages/platforms/src/agoras/platforms/discord/wrapper.py
agoras/core/telegram.py    → packages/platforms/src/agoras/platforms/telegram/wrapper.py
agoras/core/threads.py     → packages/platforms/src/agoras/platforms/threads/wrapper.py
agoras/core/tiktok.py      → packages/platforms/src/agoras/platforms/tiktok/wrapper.py
agoras/core/whatsapp.py    → packages/platforms/src/agoras/platforms/whatsapp/wrapper.py
agoras/core/x.py           → packages/platforms/src/agoras/platforms/x/wrapper.py
agoras/core/youtube.py     → packages/platforms/src/agoras/platforms/youtube/wrapper.py
```

### API Managers (10 files)

agoras/core/api/ → packages/platforms/src/agoras/platforms/

```
agoras/core/api/facebook.py    → packages/platforms/src/agoras/platforms/facebook/api.py
agoras/core/api/instagram.py   → packages/platforms/src/agoras/platforms/instagram/api.py
agoras/core/api/linkedin.py    → packages/platforms/src/agoras/platforms/linkedin/api.py
agoras/core/api/discord.py     → packages/platforms/src/agoras/platforms/discord/api.py
agoras/core/api/telegram.py    → packages/platforms/src/agoras/platforms/telegram/api.py
agoras/core/api/threads.py     → packages/platforms/src/agoras/platforms/threads/api.py
agoras/core/api/tiktok.py      → packages/platforms/src/agoras/platforms/tiktok/api.py
agoras/core/api/whatsapp.py    → packages/platforms/src/agoras/platforms/whatsapp/api.py
agoras/core/api/x.py           → packages/platforms/src/agoras/platforms/x/api.py
agoras/core/api/youtube.py     → packages/platforms/src/agoras/platforms/youtube/api.py
```

### API Clients (10 files)

agoras/core/api/clients/ → packages/platforms/src/agoras/platforms/

```
agoras/core/api/clients/facebook.py    → packages/platforms/src/agoras/platforms/facebook/client.py
agoras/core/api/clients/instagram.py   → packages/platforms/src/agoras/platforms/instagram/client.py
agoras/core/api/clients/linkedin.py    → packages/platforms/src/agoras/platforms/linkedin/client.py
agoras/core/api/clients/discord.py     → packages/platforms/src/agoras/platforms/discord/client.py
agoras/core/api/clients/telegram.py    → packages/platforms/src/agoras/platforms/telegram/client.py
agoras/core/api/clients/threads.py     → packages/platforms/src/agoras/platforms/threads/client.py
agoras/core/api/clients/tiktok.py      → packages/platforms/src/agoras/platforms/tiktok/client.py
agoras/core/api/clients/whatsapp.py    → packages/platforms/src/agoras/platforms/whatsapp/client.py
agoras/core/api/clients/x.py           → packages/platforms/src/agoras/platforms/x/client.py
agoras/core/api/clients/youtube.py     → packages/platforms/src/agoras/platforms/youtube/client.py
```

### Auth Managers (10 files)

agoras/core/api/auth/ (platform-specific) → packages/platforms/src/agoras/platforms/

```
agoras/core/api/auth/facebook.py    → packages/platforms/src/agoras/platforms/facebook/auth.py
agoras/core/api/auth/instagram.py   → packages/platforms/src/agoras/platforms/instagram/auth.py
agoras/core/api/auth/linkedin.py    → packages/platforms/src/agoras/platforms/linkedin/auth.py
agoras/core/api/auth/discord.py     → packages/platforms/src/agoras/platforms/discord/auth.py
agoras/core/api/auth/telegram.py    → packages/platforms/src/agoras/platforms/telegram/auth.py
agoras/core/api/auth/threads.py     → packages/platforms/src/agoras/platforms/threads/auth.py
agoras/core/api/auth/tiktok.py      → packages/platforms/src/agoras/platforms/tiktok/auth.py
agoras/core/api/auth/whatsapp.py    → packages/platforms/src/agoras/platforms/whatsapp/auth.py
agoras/core/api/auth/x.py           → packages/platforms/src/agoras/platforms/x/auth.py
agoras/core/api/auth/youtube.py     → packages/platforms/src/agoras/platforms/youtube/auth.py
```

### Core Infrastructure (6 files)

agoras/core/ → packages/core/src/agoras/core/

```
agoras/core/base.py                      → packages/core/src/agoras/core/interfaces.py
agoras/core/api/base.py                  → packages/core/src/agoras/core/api_base.py
agoras/core/api/auth/base.py             → packages/core/src/agoras/core/auth/base.py
agoras/core/api/auth/storage.py          → packages/core/src/agoras/core/auth/storage.py
agoras/core/api/auth/exceptions.py       → packages/core/src/agoras/core/auth/exceptions.py
agoras/core/api/auth/callback_server.py  → packages/core/src/agoras/core/auth/callback_server.py
```

### Feed System (4 files)

agoras/core/feed/ → packages/core/src/agoras/core/feed/

```
agoras/core/feed/__init__.py    → packages/core/src/agoras/core/feed/__init__.py
agoras/core/feed/feed.py        → packages/core/src/agoras/core/feed/feed.py
agoras/core/feed/item.py        → packages/core/src/agoras/core/feed/item.py
agoras/core/feed/manager.py     → packages/core/src/agoras/core/feed/manager.py
```

### Sheet System (5 files)

agoras/core/sheet/ → packages/core/src/agoras/core/sheet/

```
agoras/core/sheet/__init__.py    → packages/core/src/agoras/core/sheet/__init__.py
agoras/core/sheet/sheet.py       → packages/core/src/agoras/core/sheet/sheet.py
agoras/core/sheet/manager.py     → packages/core/src/agoras/core/sheet/manager.py
agoras/core/sheet/row.py         → packages/core/src/agoras/core/sheet/row.py
agoras/core/sheet/schedule.py    → packages/core/src/agoras/core/sheet/schedule.py
```

### Media System (5 files)

agoras/core/media/ → packages/media/src/agoras/media/

```
agoras/core/media/__init__.py    → packages/media/src/agoras/media/__init__.py
agoras/core/media/base.py        → packages/media/src/agoras/media/base.py
agoras/core/media/factory.py     → packages/media/src/agoras/media/factory.py
agoras/core/media/image.py       → packages/media/src/agoras/media/image.py
agoras/core/media/video.py       → packages/media/src/agoras/media/video.py
```

### Common Utilities (2 files)

agoras/core/ → packages/common/src/agoras/common/

```
agoras/core/logger.py    → packages/common/src/agoras/common/logger.py
agoras/core/utils.py     → packages/common/src/agoras/common/utils.py
```

### CLI Core Modules (7 files)

agoras/cli/ → packages/cli/src/agoras/cli/

```
agoras/cli/__init__.py      → packages/cli/src/agoras/cli/__init__.py (restructured)
agoras/cli/base.py          → packages/cli/src/agoras/cli/base.py
agoras/cli/converter.py     → packages/cli/src/agoras/cli/converter.py
agoras/cli/validator.py     → packages/cli/src/agoras/cli/validator.py
agoras/cli/registry.py      → packages/cli/src/agoras/cli/registry.py
agoras/cli/legacy.py        → packages/cli/src/agoras/cli/legacy.py
agoras/cli/migration.py     → packages/cli/src/agoras/cli/migration.py
```

### CLI Platform Parsers (11 files)

agoras/cli/platforms/ → packages/cli/src/agoras/cli/platforms/

```
agoras/cli/platforms/__init__.py      → packages/cli/src/agoras/cli/platforms/__init__.py
agoras/cli/platforms/facebook.py      → packages/cli/src/agoras/cli/platforms/facebook.py
agoras/cli/platforms/instagram.py     → packages/cli/src/agoras/cli/platforms/instagram.py
agoras/cli/platforms/linkedin.py      → packages/cli/src/agoras/cli/platforms/linkedin.py
agoras/cli/platforms/discord.py       → packages/cli/src/agoras/cli/platforms/discord.py
agoras/cli/platforms/telegram.py      → packages/cli/src/agoras/cli/platforms/telegram.py
agoras/cli/platforms/threads.py       → packages/cli/src/agoras/cli/platforms/threads.py
agoras/cli/platforms/tiktok.py        → packages/cli/src/agoras/cli/platforms/tiktok.py
agoras/cli/platforms/whatsapp.py      → packages/cli/src/agoras/cli/platforms/whatsapp.py
agoras/cli/platforms/x.py             → packages/cli/src/agoras/cli/platforms/x.py
agoras/cli/platforms/youtube.py       → packages/cli/src/agoras/cli/platforms/youtube.py
```

### CLI Utilities (3 files)

agoras/cli/utils/ → packages/cli/src/agoras/cli/utils/

```
agoras/cli/utils/__init__.py     → packages/cli/src/agoras/cli/utils/__init__.py
agoras/cli/utils/feed.py         → packages/cli/src/agoras/cli/utils/feed.py
agoras/cli/utils/schedule.py     → packages/cli/src/agoras/cli/utils/schedule.py
```

### Commands (2 files)

agoras/commands/ → packages/cli/src/agoras/cli/commands/

```
agoras/commands/__init__.py    → packages/cli/src/agoras/cli/commands/__init__.py
agoras/commands/publish.py     → packages/cli/src/agoras/cli/commands/publish.py
```

### Entry Point (1 file)

```
agoras/cli.py    → packages/cli/src/agoras/cli/main.py
```

### Test Files (13 files)

#### CLI Tests

tests/cli/ → packages/cli/tests/

```
tests/cli/__init__.py                             → packages/cli/tests/__init__.py
tests/cli/test_base.py                            → packages/cli/tests/test_base.py
tests/cli/test_converter.py                       → packages/cli/tests/test_converter.py
tests/cli/test_validator.py                       → packages/cli/tests/test_validator.py
tests/cli/test_registry.py                        → packages/cli/tests/test_registry.py
tests/cli/test_migration.py                       → packages/cli/tests/test_migration.py
tests/cli/test_integration.py                     → packages/cli/tests/test_integration.py
tests/cli/platforms/__init__.py                   → packages/cli/tests/platforms/__init__.py
tests/cli/platforms/test_facebook.py              → packages/cli/tests/platforms/test_facebook.py
tests/cli/platforms/test_x.py                     → packages/cli/tests/platforms/test_x.py
tests/cli/platforms/test_remaining_platforms.py   → packages/cli/tests/platforms/test_remaining_platforms.py
```

#### Core Tests

tests/ → packages/common/tests/

```
tests/test_core_logger.py    → packages/common/tests/test_logger.py
tests/test_core_utils.py     → packages/common/tests/test_utils.py
```

## Import Path Changes

### Platform Classes

**Old**:

```python
from agoras.core.facebook import Facebook
from agoras.core.x import X
```

**New**:

```python
from agoras.platforms.facebook import Facebook
from agoras.platforms.x import X
```

### Core Interfaces

**Old**:

```python
from agoras.core.base import SocialNetwork
```

**New**:

```python
from agoras.core.interfaces import SocialNetwork
```

### Common Utilities

**Old**:

```python
from agoras.core.logger import logger
from agoras.core.utils import sanitize_text
```

**New**:

```python
from agoras.common.logger import logger
from agoras.common.utils import sanitize_text
```

### Media

**Old**:

```python
from agoras.core.media import MediaFactory
from agoras.core.media.image import Image
```

**New**:

```python
from agoras.media import MediaFactory
from agoras.media.image import Image
```

### CLI Entry Point

**Old**:

```python
from agoras.cli import main, commandline
```

**New**:

```python
from agoras.cli.main import main, commandline
```

## Files Not Migrated (Will Remove)

### Initialization Files (Obsolete)

```
agoras/core/__init__.py                → Obsolete (functionality split)
agoras/core/api/__init__.py            → Obsolete
agoras/core/api/clients/__init__.py    → Obsolete
agoras/cli/__init__.py                 → Replaced with new structure
```

These files were organization/import helpers in the monolithic structure. In the new package structure, they're either obsolete or replaced with proper namespace packages.

## Package Structure Comparison

### Old Monolithic Structure

```
agoras/
├── __init__.py
├── cli.py (entry point)
├── cli/
│   ├── platforms/
│   └── utils/
├── commands/
└── core/
    ├── api/
    │   ├── auth/
    │   └── clients/
    ├── feed/
    ├── media/
    └── sheet/
```

### New Modular Structure

```
packages/
├── common/src/agoras/common/
├── media/src/agoras/media/
├── core/src/agoras/core/
│   ├── auth/
│   ├── feed/
│   └── sheet/
├── platforms/src/agoras/platforms/
│   ├── facebook/
│   ├── instagram/
│   └── ... (10 platforms)
└── cli/src/agoras/cli/
    ├── commands/
    ├── platforms/
    └── utils/
```

## Usage Examples

### Finding Migrated Code

If you need to find where old code went:

1. **Platform wrapper**: `agoras/core/facebook.py` → Check `packages/platforms/src/agoras/platforms/facebook/wrapper.py`
2. **API manager**: `agoras/core/api/facebook.py` → Check `packages/platforms/src/agoras/platforms/facebook/api.py`
3. **Auth**: `agoras/core/api/auth/facebook.py` → Check `packages/platforms/src/agoras/platforms/facebook/auth.py`
4. **CLI parser**: `agoras/cli/platforms/facebook.py` → Check `packages/cli/src/agoras/cli/platforms/facebook.py`

### Updating Import Statements

Use this mapping to update any remaining import statements:

**Pattern**:

- `agoras.core.<platform>` → `agoras.platforms.<platform>`
- `agoras.core.base` → `agoras.core.interfaces`
- `agoras.core.logger` → `agoras.common.logger`
- `agoras.core.utils` → `agoras.common.utils`
- `agoras.core.media` → `agoras.media`

## Verification

All files listed above have been:

- ✓ Migrated to new package structure
- ✓ Tested in new location (Week 3, Day 3: 151 tests passing)
- ✓ Manually verified (Week 3, Days 4-5: 70 tests passing)
- ✓ Integration verified (all packages work together)

**Conclusion**: Old files are redundant and safe to remove.
