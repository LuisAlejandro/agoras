# API and Entry Points Inventory

This document catalogs all public APIs, entry points, and user-facing interfaces in the current Agoras codebase.

## Console Entry Points

### Main CLI Entry Point

Defined in `setup.py`:

```python
entry_points={
    'console_scripts': ('agoras = agoras.cli:main',),
}
```

**Command**: `agoras`
**Function**: `agoras.cli:main`
**Description**: Main command-line interface

## CLI Commands

### Platform Commands

All platform commands follow the pattern: `agoras <platform> <action> [options]`

#### Supported Platforms

1. **X (Twitter)**
   - Command: `agoras x <action>`
   - Alias: `agoras twitter <action>` (deprecated)
   - Parser: `agoras.cli.platforms.x.create_x_parser`
   - Actions: post, like, share, delete, video

2. **Facebook**
   - Command: `agoras facebook <action>`
   - Parser: `agoras.cli.platforms.facebook.create_facebook_parser`
   - Actions: post, like, share, delete, video

3. **Instagram**
   - Command: `agoras instagram <action>`
   - Parser: `agoras.cli.platforms.instagram.create_instagram_parser`
   - Actions: post, video

4. **LinkedIn**
   - Command: `agoras linkedin <action>`
   - Parser: `agoras.cli.platforms.linkedin.create_linkedin_parser`
   - Actions: post, like, share, delete

5. **Discord**
   - Command: `agoras discord <action>`
   - Parser: `agoras.cli.platforms.discord.create_discord_parser`
   - Actions: post, delete

6. **YouTube**
   - Command: `agoras youtube <action>`
   - Parser: `agoras.cli.platforms.youtube.create_youtube_parser`
   - Actions: video

7. **TikTok**
   - Command: `agoras tiktok <action>`
   - Parser: `agoras.cli.platforms.tiktok.create_tiktok_parser`
   - Actions: video

8. **Telegram** (New in v2.0)
   - Command: `agoras telegram <action>`
   - Parser: `agoras.cli.platforms.telegram.create_telegram_parser`
   - Actions: post, delete

9. **Threads** (New in v2.0)
   - Command: `agoras threads <action>`
   - Parser: `agoras.cli.platforms.threads.create_threads_parser`
   - Actions: post

10. **WhatsApp** (New in v2.0)
    - Command: `agoras whatsapp <action>`
    - Parser: `agoras.cli.platforms.whatsapp.create_whatsapp_parser`
    - Actions: post

### Utility Commands

1. **Feed Publishing**
   - Command: `agoras utils feed-publish`
   - Parser: `agoras.cli.utils.create_utils_parser`
   - Modes: last, random

2. **Schedule Management**
   - Command: `agoras utils schedule-run`
   - Parser: `agoras.cli.utils.create_utils_parser`
   - Description: Run scheduled posts from Google Sheets

### Legacy Commands (Deprecated)

1. **Publish Command**
   - Command: `agoras publish`
   - Parser: `agoras.cli.legacy.create_legacy_publish_parser`
   - Status: Deprecated, emits warnings
   - Will be removed in v3.0

## Public API Classes

### Platform Wrappers (SocialNetwork Implementations)

All platform classes implement the `SocialNetwork` interface and provide async methods.

#### Current Locations (v1.1.3 / v2.0 pre-split)

```python
from agoras.core.facebook import Facebook
from agoras.core.instagram import Instagram
from agoras.core.linkedin import LinkedIn
from agoras.core.discord import Discord
from agoras.core.youtube import YouTube
from agoras.core.tiktok import TikTok
from agoras.core.telegram import Telegram      # New in v2.0
from agoras.core.threads import Threads        # New in v2.0
from agoras.core.whatsapp import WhatsApp      # New in v2.0
from agoras.core.x import X                    # New in v2.0
```

#### Common Methods (All Platforms)

```python
class SocialNetwork:
    async def _initialize_client(self) -> None
    async def disconnect(self) -> None
    async def post(self, status_text: str, status_link: str,
                   status_image_url_1: str = None, ...) -> str
    async def like(self, post_id: str) -> str
    async def delete(self, post_id: str) -> str
    async def share(self, post_id: str) -> str
    async def video(self, status_text: str, video_url: str,
                    video_title: str) -> str
    async def execute_action(self, action: str) -> None
```

**Note**: Not all platforms support all methods. See platform-specific documentation.

### Base Classes and Interfaces

```python
from agoras.core.base import SocialNetwork          # Abstract base class
from agoras.core.api.base import BaseAPI            # API base class
from agoras.core.api.auth.base import BaseAuthManager  # Auth base class
```

### Media Processing

```python
from agoras.core.media import MediaFactory
from agoras.core.media.factory import MediaFactory
from agoras.core.media.image import Image
from agoras.core.media.video import Video
from agoras.core.media.base import BaseMedia
```

**Key Methods**:
- `MediaFactory.create_image(url: str) -> Image`
- `MediaFactory.create_video(url: str, platform: str) -> Video`
- `MediaFactory.download_images(urls: List[str]) -> List[Image]`
- `Image.download() -> None`
- `Video.download() -> None`
- `Media.cleanup() -> None`

### Feed Management

```python
from agoras.core.feed import Feed
from agoras.core.feed.feed import Feed
from agoras.core.feed.item import FeedItem
```

**Key Methods**:
- `Feed(url: str)`
- `Feed.download() -> Feed`
- `Feed.get_items_since(lookback_seconds: int) -> List[FeedItem]`
- `Feed.get_random_item(max_age_days: int) -> FeedItem`
- `Feed.get_latest_items(count: int) -> List[FeedItem]`

### Sheet Management

```python
from agoras.core.sheet import ScheduleSheet
from agoras.core.sheet.schedule import ScheduleSheet
```

**Key Methods**:
- `ScheduleSheet(sheet_id: str, client_email: str, private_key: str, worksheet_name: str)`
- `ScheduleSheet.authenticate() -> None`
- `ScheduleSheet.get_worksheet() -> None`
- `ScheduleSheet.process_scheduled_posts(max_count: int) -> List[Dict]`

### Utilities

```python
from agoras.core.utils import parse_metatags, add_url_timestamp
from agoras.core.logger import logger
```

**Functions**:
- `parse_metatags(url: str) -> Dict[str, str]`
- `add_url_timestamp(url: str, timestamp: str) -> str`

### Version and Metadata

```python
from agoras import __version__, __author__, __email__, __url__, __description__
```

**Attributes**:
- `__version__`: Current version string (e.g., "1.1.3")
- `__author__`: Author name
- `__email__`: Contact email
- `__url__`: Project URL
- `__description__`: Short description

## Authentication (v2.0 New)

### OAuth2 Callback Server

```python
from agoras.core.api.auth.callback_server import OAuthCallbackServer
```

**Key Methods**:
- `OAuthCallbackServer(expected_state: str = None)`
- `OAuthCallbackServer.start_and_wait(timeout: int = 300) -> str`
- `OAuthCallbackServer.get_redirect_uri() -> str`

### Token Storage

```python
from agoras.core.api.auth.storage import TokenStorage
```

**Key Methods**:
- `TokenStorage.save_tokens(user_id: str, tokens: Dict) -> None`
- `TokenStorage.load_tokens(user_id: str) -> Dict`
- `TokenStorage.delete_tokens(user_id: str) -> None`

### Auth Exceptions

```python
from agoras.core.api.auth.exceptions import AuthException
```

## CLI Utilities (Internal APIs)

These are typically not used directly by end users but are available for advanced use cases.

### Parameter Conversion

```python
from agoras.cli.converter import ParameterConverter
```

**Methods**:
- `ParameterConverter.convert_legacy_to_new(args_dict: Dict) -> Dict`

### Validation

```python
from agoras.cli.validator import ActionValidator
```

**Methods**:
- `ActionValidator.validate_action(platform: str, action: str) -> bool`

### Platform Registry

```python
from agoras.cli.registry import PlatformRegistry
```

**Methods**:
- `PlatformRegistry.get_platform(name: str) -> Type[SocialNetwork]`
- `PlatformRegistry.list_platforms() -> List[str]`

### Migration Utilities

```python
from agoras.cli.migration import suggest_new_command, migrate_*
```

**Functions**:
- `suggest_new_command(network: str, action: str, args_dict: Dict) -> str`
- `migrate_feed_command(args_dict: Dict) -> str`
- `migrate_schedule_command(args_dict: Dict) -> str`

## Breaking Changes in v2.0 (Package Split)

### Entry Point Changes

**No changes** - Entry point remains: `agoras = agoras.cli:main`

### Import Path Changes

All import paths will change. See [import-mapping.md](import-mapping.md) for complete mapping.

**Most Common Changes**:
- Platform classes: `agoras.core.<platform>` → `agoras.platforms.<platform>`
- Media: `agoras.core.media` → `agoras.media`
- Utils: `agoras.core.utils` → `agoras.common.utils`
- Logger: `agoras.core.logger` → `agoras.common.logger`
- Metadata: `agoras` → `agoras.common`

### Method Signature Changes

**No changes** - All method signatures remain the same

### CLI Command Changes

**Recommended but not required**:
- Old: `agoras publish --network facebook --action post ...`
- New: `agoras facebook post ...`

Legacy commands still work with deprecation warnings.

## Usage Examples

### CLI Usage

```bash
# Post to Facebook
agoras facebook post \
    --facebook-access-token "$TOKEN" \
    --status-text "Hello World" \
    --status-link "https://example.com"

# Post to multiple platforms (script)
for platform in facebook twitter linkedin; do
    agoras $platform post --status-text "Hello" --status-link "https://example.com"
done
```

### Programmatic Usage (Current)

```python
import asyncio
from agoras.core.facebook import Facebook

async def post_to_facebook():
    fb = Facebook(facebook_access_token='...')
    await fb._initialize_client()
    try:
        post_id = await fb.post(
            status_text='Hello World',
            status_link='https://example.com'
        )
        print(f'Posted: {post_id}')
    finally:
        await fb.disconnect()

asyncio.run(post_to_facebook())
```

### Programmatic Usage (After Package Split)

```python
import asyncio
from agoras.platforms.facebook import Facebook  # Changed import

async def post_to_facebook():
    fb = Facebook(facebook_access_token='...')
    await fb._initialize_client()
    try:
        post_id = await fb.post(
            status_text='Hello World',
            status_link='https://example.com'
        )
        print(f'Posted: {post_id}')
    finally:
        await fb.disconnect()

asyncio.run(post_to_facebook())
```

## Summary

### User-Facing APIs

- **CLI Commands**: 10 platform commands + 2 utility commands + 1 legacy command
- **Platform Classes**: 10 classes (Facebook, Instagram, LinkedIn, Discord, YouTube, TikTok, Telegram, Threads, WhatsApp, X)
- **Utility Classes**: MediaFactory, Feed, ScheduleSheet
- **Entry Point**: `agoras` command

### Internal APIs

- **Base Classes**: SocialNetwork, BaseAPI, BaseAuthManager
- **CLI Utilities**: ParameterConverter, ActionValidator, PlatformRegistry
- **Auth Infrastructure**: OAuthCallbackServer, TokenStorage (v2.0)

### Stability Guarantees

- ✅ **CLI commands**: Backward compatible (legacy commands deprecated but functional)
- ❌ **Import paths**: Breaking changes in v2.0 (package split)
- ✅ **Method signatures**: No changes
- ✅ **Configuration**: No changes (same env vars and config files)

For migration guidance, see [MIGRATION.md](../../MIGRATION.md).
