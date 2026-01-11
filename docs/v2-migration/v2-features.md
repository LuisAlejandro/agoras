# Agoras v2.0 Features

This document lists all new features and changes implemented in v2.0 (develop branch) before the package split.

## New Features in v2.0

### 1. OAuth2 Authentication Infrastructure

**New in v2.0**: Complete OAuth2 authentication system with automatic callback handling.

#### OAuth Callback Server (`agoras/core/api/auth/callback_server.py`)
- Local HTTP server for OAuth callbacks
- Eliminates manual copy-paste of callback URLs
- Automatic authorization code capture
- CSRF protection via state parameter validation
- Beautiful HTML success/error pages
- Timeout handling (300 seconds default)
- Port auto-detection for callback URL

#### Enhanced Auth Managers
- `BaseAuthManager` (`agoras/core/api/auth/base.py`): Abstract base for all auth implementations
- Platform-specific auth managers for each social network
- Token storage system (`agoras/core/api/auth/storage.py`)
- Custom exceptions (`agoras/core/api/auth/exceptions.py`)

**Platforms with OAuth2 support**:
- Facebook (`agoras/core/api/auth/facebook.py`)
- Instagram (`agoras/core/api/auth/instagram.py`)
- LinkedIn (`agoras/core/api/auth/linkedin.py`)
- TikTok (`agoras/core/api/auth/tiktok.py`)
- YouTube (`agoras/core/api/auth/youtube.py`)
- Discord (`agoras/core/api/auth/discord.py`)
- X/Twitter (`agoras/core/api/auth/x.py`)
- Telegram (`agoras/core/api/auth/telegram.py`)
- Threads (`agoras/core/api/auth/threads.py`)
- WhatsApp (`agoras/core/api/auth/whatsapp.py`)

### 2. New Social Network Platforms

**Added in v2.0**: Support for 4 additional social networks.

#### Telegram Support
- Files: `agoras/core/telegram.py`, `agoras/core/api/telegram.py`, `agoras/core/api/clients/telegram.py`
- CLI: `agoras/cli/platforms/telegram.py`
- Full async/await implementation
- Bot API integration

#### WhatsApp Support
- Files: `agoras/core/whatsapp.py`, `agoras/core/api/whatsapp.py`, `agoras/core/api/clients/whatsapp.py`
- CLI: `agoras/cli/platforms/whatsapp.py`
- WhatsApp Business API integration
- Media sharing capabilities

#### Threads Support
- Files: `agoras/core/threads.py`, `agoras/core/api/threads.py`, `agoras/core/api/clients/threads.py`
- CLI: `agoras/cli/platforms/threads.py`
- Meta's Threads platform integration
- Compatible with Instagram Graph API

#### X (Twitter Rebrand)
- Files: `agoras/core/x.py`, `agoras/core/api/x.py`, `agoras/core/api/clients/x.py`
- CLI: `agoras/cli/platforms/x.py`
- Updated for X platform (formerly Twitter)
- Maintains backward compatibility with Twitter API

### 3. Unified API Architecture

**New in v2.0**: Consistent three-layer architecture for all platforms.

#### Three-Layer Structure
1. **Wrapper Layer** (`agoras/core/<platform>.py`): High-level `SocialNetwork` interface
2. **API Manager Layer** (`agoras/core/api/<platform>.py`): Business logic and rate limiting
3. **Client Layer** (`agoras/core/api/clients/<platform>.py`): Low-level HTTP/API calls

**Benefits**:
- Cleaner separation of concerns
- Easier to test and maintain
- Consistent error handling
- Rate limiting at API layer

### 4. CLI Migration Utilities

**New in v2.0**: Tools to help users migrate from legacy CLI commands.

#### Migration Module (`agoras/cli/migration.py`)
- `suggest_new_command()`: Converts legacy publish commands to new syntax
- `migrate_feed_command()`: Migrates feed-based commands
- `migrate_schedule_command()`: Migrates schedule commands
- `migrate_basic_action()`: Migrates post/like/share/delete commands

#### CLI Improvements
- Platform-specific command parsers
- Parameter validation and conversion
- Better error messages
- Deprecation warnings for legacy commands

### 5. Enhanced CLI Structure

**New in v2.0**: Reorganized CLI for better maintainability.

#### New CLI Modules
- `agoras/cli/base.py`: Base CLI utilities
- `agoras/cli/converter.py`: Parameter conversion utilities
- `agoras/cli/validator.py`: Action and parameter validation
- `agoras/cli/registry.py`: Platform registry for dynamic loading
- `agoras/cli/migration.py`: Migration helpers
- `agoras/cli/legacy.py`: Legacy command compatibility layer

#### Platform-Specific Parsers
Each platform now has its own CLI parser module:
- `agoras/cli/platforms/facebook.py`
- `agoras/cli/platforms/instagram.py`
- `agoras/cli/platforms/linkedin.py`
- `agoras/cli/platforms/discord.py`
- `agoras/cli/platforms/youtube.py`
- `agoras/cli/platforms/tiktok.py`
- `agoras/cli/platforms/telegram.py`
- `agoras/cli/platforms/threads.py`
- `agoras/cli/platforms/whatsapp.py`
- `agoras/cli/platforms/x.py`

### 6. Improved Testing Infrastructure

**New in v2.0**: Comprehensive test coverage for new features.

#### New Test Files
- `tests/cli/test_base.py`: Base CLI functionality tests
- `tests/cli/test_converter.py`: Parameter converter tests
- `tests/cli/test_validator.py`: Validation logic tests
- `tests/cli/test_registry.py`: Platform registry tests
- `tests/cli/test_migration.py`: Migration utilities tests
- `tests/cli/test_integration.py`: Integration tests
- `tests/cli/platforms/test_facebook.py`: Facebook CLI tests
- `tests/cli/platforms/test_x.py`: X/Twitter CLI tests
- `tests/cli/platforms/test_remaining_platforms.py`: Other platforms

### 7. API Client Separation

**New in v2.0**: Low-level API clients extracted into separate modules.

#### Client Directory (`agoras/core/api/clients/`)
- `facebook.py`: Facebook Graph API client
- `instagram.py`: Instagram Graph API client
- `linkedin.py`: LinkedIn API client
- `tiktok.py`: TikTok API client
- `telegram.py`: Telegram Bot API client
- `youtube.py`: YouTube Data API client
- `discord.py`: Discord API client
- `whatsapp.py`: WhatsApp Business API client
- `threads.py`: Threads API client
- `x.py`: X (Twitter) API v2 client

**Benefits**:
- Clear separation between business logic (API managers) and HTTP calls (clients)
- Easier to mock for testing
- Reusable across different authentication methods

## Breaking Changes Introduced in v2.0

### API Changes (Non-Package Split)
1. **Async/Await Throughout**: All platform methods now use async/await
2. **Authentication Flow**: OAuth2 with callback server (some platforms)
3. **Client Initialization**: New pattern with auth managers

### CLI Changes (Non-Package Split)
1. **Command Structure**: Platform-specific commands (e.g., `agoras facebook post` instead of `agoras publish --network facebook`)
2. **Parameter Names**: Some parameter names changed for consistency
3. **Legacy Commands**: Still supported but with deprecation warnings

## Features NOT Included in v2.0

The following will be added in the package split (final v2.0 feature):

1. **Package Split**: Separation into 5 PyPI packages
2. **Import Path Changes**: New namespace structure
3. **Monorepo Structure**: `packages/` directory organization

## Upgrade Path

### From v1.1.3 to v2.0 (pre-split)

If v2.0 were released before the package split, users would need to:

1. Update code to use async/await
2. Update CLI commands to new structure
3. Update authentication configuration for OAuth2

### From v1.1.3 to v2.0 (with package split)

When v2.0 is released with the package split, users will also need to:

4. Update all import paths (see [import-mapping.md](import-mapping.md))
5. Install the new `agoras` package (which pulls in 4 sub-packages)

## Summary

v2.0 (develop branch) includes significant improvements:

- **4 new platforms**: Telegram, WhatsApp, Threads, X
- **OAuth2 infrastructure**: Automatic callback server, token management
- **Unified architecture**: Three-layer structure for all platforms
- **Better CLI**: Platform-specific commands, migration utilities
- **Enhanced testing**: Comprehensive test coverage
- **Client separation**: Low-level HTTP clients isolated

The **package split** is the final architectural change before v2.0 release, and it will reorganize all this code into 5 separate, distributable packages.
