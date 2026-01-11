# Import Path Mapping: v1.1.3 → v2.0.0

This document maps all import paths from the monolithic v1.1.3 package to the new modular v2.0.0 package structure.

## Package Organization

v2.0.0 splits the monolithic `agoras` package into 5 sub-packages:

- **agoras-common**: Utilities, logging, version info
- **agoras-media**: Image and video processing
- **agoras-core**: Interfaces, Feed, Sheet, Base API/Auth
- **agoras-platforms**: Platform-specific implementations
- **agoras** (CLI): Command-line interface

## Public API Import Changes

### Core Package Metadata

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras import __version__` | `from agoras.common import __version__` | Version info moved to common |
| `from agoras import __author__` | `from agoras.common import __author__` | Metadata moved to common |
| `from agoras import __email__` | `from agoras.common import __email__` | Metadata moved to common |
| `from agoras import __url__` | `from agoras.common import __url__` | Metadata moved to common |
| `from agoras import __description__` | `from agoras.common import __description__` | Metadata moved to common |

### Platform Classes (Social Network Wrappers)

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras.core.facebook import Facebook` | `from agoras.platforms.facebook import Facebook` | Platform wrapper moved |
| `from agoras.core.instagram import Instagram` | `from agoras.platforms.instagram import Instagram` | Platform wrapper moved |
| `from agoras.core.linkedin import LinkedIn` | `from agoras.platforms.linkedin import LinkedIn` | Platform wrapper moved |
| `from agoras.core.discord import Discord` | `from agoras.platforms.discord import Discord` | Platform wrapper moved |
| `from agoras.core.youtube import YouTube` | `from agoras.platforms.youtube import YouTube` | Platform wrapper moved |
| `from agoras.core.tiktok import TikTok` | `from agoras.platforms.tiktok import TikTok` | Platform wrapper moved |
| `from agoras.core.telegram import Telegram` | `from agoras.platforms.telegram import Telegram` | Platform wrapper moved (v2.0 new) |
| `from agoras.core.threads import Threads` | `from agoras.platforms.threads import Threads` | Platform wrapper moved (v2.0 new) |
| `from agoras.core.whatsapp import WhatsApp` | `from agoras.platforms.whatsapp import WhatsApp` | Platform wrapper moved (v2.0 new) |
| `from agoras.core.x import X` | `from agoras.platforms.x import X` | Platform wrapper moved (v2.0 new, Twitter rebrand) |

### Base Classes and Interfaces

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras.core.base import SocialNetwork` | `from agoras.core.interfaces import SocialNetwork` | Interface renamed for clarity |
| `from agoras.core.api.base import BaseAPI` | `from agoras.core.api_base import BaseAPI` | Flattened structure |

### Media Processing

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras.core.media import MediaFactory` | `from agoras.media import MediaFactory` | Media is now separate package |
| `from agoras.core.media.factory import MediaFactory` | `from agoras.media.factory import MediaFactory` | Media is now separate package |
| `from agoras.core.media.image import Image` | `from agoras.media.image import Image` | Media is now separate package |
| `from agoras.core.media.video import Video` | `from agoras.media.video import Video` | Media is now separate package |
| `from agoras.core.media.base import BaseMedia` | `from agoras.media.base import BaseMedia` | Media is now separate package |

### Feed Management

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras.core.feed import Feed` | `from agoras.core.feed import Feed` | **No change** - stays in core |
| `from agoras.core.feed.feed import Feed` | `from agoras.core.feed.feed import Feed` | **No change** - stays in core |
| `from agoras.core.feed.item import FeedItem` | `from agoras.core.feed.item import FeedItem` | **No change** - stays in core |

### Sheet Management

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras.core.sheet import ScheduleSheet` | `from agoras.core.sheet import ScheduleSheet` | **No change** - stays in core |
| `from agoras.core.sheet.sheet import Sheet` | `from agoras.core.sheet.sheet import Sheet` | **No change** - stays in core |
| `from agoras.core.sheet.schedule import ScheduleSheet` | `from agoras.core.sheet.schedule import ScheduleSheet` | **No change** - stays in core |

### Utilities and Logging

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras.core.utils import parse_metatags` | `from agoras.common.utils import parse_metatags` | Utilities moved to common |
| `from agoras.core.utils import add_url_timestamp` | `from agoras.common.utils import add_url_timestamp` | Utilities moved to common |
| `from agoras.core.logger import logger` | `from agoras.common.logger import logger` | Logger moved to common |

### Authentication (v2.0 new features)

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| N/A | `from agoras.core.auth.base import BaseAuthManager` | New in v2.0 |
| N/A | `from agoras.core.auth.storage import TokenStorage` | New in v2.0 |
| N/A | `from agoras.core.auth.callback_server import OAuthCallbackServer` | New in v2.0 |
| N/A | `from agoras.core.auth.exceptions import AuthException` | New in v2.0 |

### API Clients (Internal - typically not imported directly by users)

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras.core.api import FacebookAPI` | `from agoras.platforms.facebook.api import FacebookAPI` | API moved to platforms |
| `from agoras.core.api import InstagramAPI` | `from agoras.platforms.instagram.api import InstagramAPI` | API moved to platforms |
| `from agoras.core.api import LinkedInAPI` | `from agoras.platforms.linkedin.api import LinkedInAPI` | API moved to platforms |
| `from agoras.core.api import DiscordAPI` | `from agoras.platforms.discord.api import DiscordAPI` | API moved to platforms |
| `from agoras.core.api import YouTubeAPI` | `from agoras.platforms.youtube.api import YouTubeAPI` | API moved to platforms |
| `from agoras.core.api import XAPI` | `from agoras.platforms.x.api import XAPI` | API moved to platforms |
| `from agoras.core.api.tiktok import TikTokAPI` | `from agoras.platforms.tiktok.api import TikTokAPI` | API moved to platforms |
| `from agoras.core.api.telegram import TelegramAPI` | `from agoras.platforms.telegram.api import TelegramAPI` | API moved to platforms |
| `from agoras.core.api.threads import ThreadsAPI` | `from agoras.platforms.threads.api import ThreadsAPI` | API moved to platforms |
| `from agoras.core.api import WhatsAppAPI` | `from agoras.platforms.whatsapp.api import WhatsAppAPI` | API moved to platforms |

### CLI Modules (typically not imported by end users)

| v1.1.3 | v2.0.0 | Notes |
|--------|--------|-------|
| `from agoras.cli import commandline` | `from agoras.cli import commandline` | **No change** - stays in CLI |
| `from agoras.cli.registry import PlatformRegistry` | `from agoras.cli.registry import PlatformRegistry` | **No change** - stays in CLI |
| `from agoras.cli.validator import ActionValidator` | `from agoras.cli.validator import ActionValidator` | **No change** - stays in CLI |
| `from agoras.cli.converter import ParameterConverter` | `from agoras.cli.converter import ParameterConverter` | **No change** - stays in CLI |
| `from agoras.cli.migration import migrate_*` | `from agoras.cli.migration import migrate_*` | **No change** - stays in CLI |

## Migration Strategy

### For Library Users

If you're using Agoras as a library (importing classes programmatically):

1. **Find and replace** imports in your code using the table above
2. Most common change: `from agoras.core.facebook import Facebook` → `from agoras.platforms.facebook import Facebook`
3. Update utility imports: `from agoras.core.utils` → `from agoras.common.utils`

### For CLI Users

If you only use the `agoras` command-line tool:

- **No import changes needed** - just upgrade the package
- All CLI commands remain the same
- Configuration file formats unchanged

## Breaking Changes Summary

### High Impact (Most Common User-Facing Imports)

1. **Platform classes**: All moved from `agoras.core.<platform>` to `agoras.platforms.<platform>`
2. **MediaFactory**: Moved from `agoras.core.media` to `agoras.media`
3. **Utilities**: Moved from `agoras.core.utils` to `agoras.common.utils`
4. **Logger**: Moved from `agoras.core.logger` to `agoras.common.logger`
5. **Metadata**: Moved from `agoras` to `agoras.common`

### Low Impact (Internal APIs)

- API client classes reorganized but rarely imported directly by users
- Base classes renamed for clarity (`base.py` → `interfaces.py`)
- CLI modules remain unchanged

## Backward Compatibility

**No backward compatibility layer is provided.** Users must update their imports when upgrading to v2.0.0.

For a step-by-step migration guide, see [MIGRATION.md](../../MIGRATION.md).
