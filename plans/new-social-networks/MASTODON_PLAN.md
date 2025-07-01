# Mastodon Implementation Plan

## Overview

Add Mastodon integration to agoras using OAuth 2.0 authentication and the Mastodon.py library, supporting multiple instances across the fediverse.

## Priority: MEDIUM (after Threads and Pinterest)

## Library Analysis

**Mastodon.py** provides:

- OAuth 2.0 authentication with multi-instance support
- Status creation (toots) with text, images, videos
- Boost (repost) and favorite functionality
- Reply and thread management
- Instance capability detection
- Media upload and alt-text support
- Automatic app registration per instance

## Dependencies to Add

```
Mastodon.py>=1.8.1
```

## Architecture Overview

Following the established 4-layer architecture:

1. **Auth Layer** (`agoras/core/api/auth/mastodon.py`) - OAuth 2.0 with instance support
2. **Client Layer** (`agoras/core/api/clients/mastodon.py`) - HTTP wrapper around Mastodon.py
3. **API Layer** (`agoras/core/api/mastodon.py`) - Main integration class
4. **Core Layer** (`agoras/core/mastodon.py`) - SocialNetwork implementation

## Detailed Implementation Plans

### 1. Authentication Manager (`agoras/core/api/auth/mastodon.py`)

**Pattern**: Follow `agoras/core/api/auth/tiktok.py` OAuth 2.0 pattern

**Key Implementation Details**:

```python
class MastodonAuthManager(BaseAuthManager):
    def __init__(self, instance_url: str, client_id: str = None,
                 client_secret: str = None, refresh_token: Optional[str] = None):
        # Multi-instance OAuth 2.0 configuration
```

**OAuth Flow Implementation**:

- Use Mastodon.py's `create_app()` for automatic app registration
- Handle instance-specific authorization URLs
- Support any Mastodon-compatible instance
- Instance-specific token caching

**Key Methods to Implement**:

- `authenticate()` - Check cached token, refresh if needed
- `authorize()` - Browser-based OAuth flow with instance support
- `_register_app()` - Automatic app registration per instance
- `_validate_credentials()` - Ensure instance URL is valid

**Token Caching Strategy**:

```python
def _get_cache_filename(self) -> str:
    instance_name = self.instance_url.replace('https://', '').replace('/', '-')
    return f'mastodon-{instance_name}.json'

def _save_refresh_token_to_cache(self, token: str):
    cache_file = self._get_cache_filename()
    self._save_token_to_cache(cache_file, 'mastodon_access_token', token)
```

### 2. API Client (`agoras/core/api/clients/mastodon.py`)

**Pattern**: Follow `agoras/core/api/clients/tiktok.py` structure

**Mastodon API Wrapper**:

```python
class MastodonAPIClient:
    def __init__(self, instance_url: str, access_token: str):
        from mastodon import Mastodon

        self.client = Mastodon(
            api_base_url=instance_url,
            access_token=access_token
        )
        self.instance_url = instance_url
```

**Key Methods to Implement**:

- `get_account_info()` - User profile information
- `create_status()` - Create toots with media
- `boost_status()` - Boost (repost) functionality
- `favourite_status()` - Favorite posts
- `reply_to_status()` - Reply functionality
- `delete_status()` - Delete posts
- `upload_media()` - Media upload with alt text

**Status Creation Pattern**:

```python
def create_status(self, text: str, media_files: List[Dict] = None,
                 reply_to_id: str = None, visibility: str = 'public',
                 spoiler_text: str = None) -> Dict[str, Any]:
    media_ids = []
    if media_files:
        for media in media_files:
            media_dict = self.client.media_post(
                media['file'],
                mime_type=media['mime_type'],
                description=media.get('alt_text')
            )
            media_ids.append(media_dict['id'])

    return self.client.status_post(
        status=text,
        media_ids=media_ids,
        in_reply_to_id=reply_to_id,
        visibility=visibility,
        spoiler_text=spoiler_text
    )
```

### 3. Main API Integration (`agoras/core/api/mastodon.py`)

**Pattern**: Follow `agoras/core/api/tiktok.py` structure

**Class Structure**:

```python
class MastodonAPI:
    def __init__(self, instance_url: str, client_id: str = None,
                 client_secret: str = None, refresh_token: Optional[str] = None):
        self.auth_manager = MastodonAuthManager(
            instance_url, client_id, client_secret, refresh_token
        )
        self.client = None
```

**Async Method Wrappers**:

```python
async def create_status(self, text: str, media_files: List[Dict] = None,
                       visibility: str = 'public') -> str:
    def _sync_create():
        response = self.client.create_status(text, media_files, visibility=visibility)
        return response['id']  # Extract status ID

    return await asyncio.to_thread(_sync_create)
```

**Key Methods**:

- `authenticate()` - Initialize auth manager and client
- `create_status()` - Status creation with media
- `boost_status()` - Boost functionality
- `favourite_status()` - Favorite functionality
- `reply_to_status()` - Reply functionality
- `delete_status()` - Status deletion
- `disconnect()` - Cleanup resources

### 4. Core Platform Implementation (`agoras/core/mastodon.py`)

**Pattern**: Follow `agoras/core/tiktok.py` structure exactly

**Class Initialization**:

```python
class Mastodon(SocialNetwork):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Platform-specific configuration
        self.mastodon_instance_url = None
        self.mastodon_client_id = None
        self.mastodon_client_secret = None
        self.mastodon_access_token = None
        # Mastodon-specific settings
        self.mastodon_visibility = None
        self.mastodon_sensitive = None
        self.mastodon_spoiler_text = None
        self.mastodon_status_id = None
        self.api = None
```

**Client Initialization Pattern**:

```python
async def _initialize_client(self):
    # Get configuration using existing pattern
    self.mastodon_instance_url = self._get_config_value('mastodon_instance_url', 'MASTODON_INSTANCE_URL')
    self.mastodon_client_id = self._get_config_value('mastodon_client_id', 'MASTODON_CLIENT_ID')
    self.mastodon_client_secret = self._get_config_value('mastodon_client_secret', 'MASTODON_CLIENT_SECRET')

    # Optional configuration
    self.mastodon_visibility = self._get_config_value('mastodon_visibility', 'MASTODON_VISIBILITY') or 'public'
    self.mastodon_sensitive = self._get_config_value('mastodon_sensitive', 'MASTODON_SENSITIVE') or False
    self.mastodon_spoiler_text = self._get_config_value('mastodon_spoiler_text', 'MASTODON_SPOILER_TEXT')

    # Validation
    if not self.mastodon_instance_url:
        raise Exception('Mastodon instance URL is required.')

    # Initialize API (client_id/secret will be auto-generated if missing)
    self.api = MastodonAPI(
        self.mastodon_instance_url, self.mastodon_client_id,
        self.mastodon_client_secret, self.mastodon_access_token
    )
    await self.api.authenticate()
```

**SocialNetwork Interface Implementation**:

**post() Method Pattern**:

```python
async def post(self, status_text, status_link,
               status_image_url_1=None, status_image_url_2=None,
               status_image_url_3=None, status_image_url_4=None):
    if not self.api:
        raise Exception('Mastodon API not initialized')

    # Combine text and link
    post_text = f'{status_text} {status_link}'.strip()

    # Handle media files
    media_files = []
    image_urls = list(filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ]))

    if image_urls:
        images = await self.download_images(image_urls)
        try:
            for image in images:
                if image.content and image.file_type:
                    media_files.append({
                        'file': image.content,
                        'mime_type': image.file_type.mime,
                        'alt_text': f'Image from {image.url}'
                    })
                else:
                    raise Exception(f'Failed to validate image: {image.url}')
        finally:
            for image in images:
                image.cleanup()

    # Create status
    status_id = await self.api.create_status(
        text=post_text,
        media_files=media_files,
        visibility=self.mastodon_visibility
    )

    self._output_status(status_id)
    return status_id
```

**Mastodon-Specific Methods**:

```python
async def reply(self, reply_text: str, status_id: str):
    """Reply to a Mastodon status."""
    if not self.api:
        raise Exception('Mastodon API not initialized')

    if not status_id:
        status_id = self.mastodon_status_id

    if not status_id:
        raise Exception('Status ID is required for reply')

    reply_id = await self.api.reply_to_status(reply_text, status_id)
    self._output_status(reply_id)
    return reply_id

async def boost(self, status_id: str = None):
    """Boost a Mastodon status."""
    if not self.api:
        raise Exception('Mastodon API not initialized')

    status_id = status_id or self.mastodon_status_id
    if not status_id:
        raise Exception('Status ID is required for boost')

    boost_id = await self.api.boost_status(status_id)
    self._output_status(boost_id)
    return boost_id
```

## Configuration Variables

- `MASTODON_INSTANCE_URL` - Instance URL (e.g., <https://mastodon.social>)
- `MASTODON_CLIENT_ID` - OAuth client ID (auto-generated if missing)
- `MASTODON_CLIENT_SECRET` - OAuth client secret (auto-generated if missing)
- `MASTODON_ACCESS_TOKEN` - User access token
- `MASTODON_VISIBILITY` - Post visibility (public, unlisted, private, direct)
- `MASTODON_SENSITIVE` - Mark media as sensitive
- `MASTODON_SPOILER_TEXT` - Content warning text

## CLI Integration

**Usage Examples**:

```bash
# Create status (toot)
agoras publish --network mastodon --action post \
  --status-text "Hello Mastodon!" \
  --status-link "https://example.com"

# Post with images and alt text
agoras publish --network mastodon --action post \
  --status-text "Check this out!" \
  --status-image-url-1 "https://example.com/image1.jpg" \
  --mastodon-visibility "public"

# Reply to status
agoras publish --network mastodon --action reply \
  --mastodon-reply-text "Great post!" \
  --mastodon-status-id "status_id_here"

# Boost status
agoras publish --network mastodon --action boost \
  --mastodon-status-id "status_id_here"

# Favorite status
agoras publish --network mastodon --action like \
  --mastodon-status-id "status_id_here"

# Post with content warning
agoras publish --network mastodon --action post \
  --status-text "Sensitive content" \
  --mastodon-spoiler-text "Content Warning" \
  --mastodon-sensitive true
```

**New Actions to Support**:

- `reply` - Reply to statuses
- `boost` - Boost statuses (same as share)
- Standard actions: `post`, `video`, `like`, `share`, `delete`

## Package Updates Required

**Import Additions**:

```python
# agoras/core/api/__init__.py
from .mastodon import MastodonAPI

# agoras/core/api/auth/__init__.py
from .mastodon import MastodonAuthManager

# agoras/core/api/clients/__init__.py
from .mastodon import MastodonAPIClient

# agoras/core/__init__.py
from .mastodon import Mastodon
```

## Documentation Requirements

### Credential Setup Guide (`docs/credentials/mastodon.rst`)

**Content Outline**:

1. Instance selection and account creation
2. Automatic app registration process
3. OAuth flow for multiple instances
4. Instance-specific considerations
5. Character limits and capabilities per instance

### Usage Documentation (`docs/mastodon.rst`)

**Content Outline**:

1. Multi-instance authentication setup
2. Basic posting (tooting) examples
3. Reply and boost functionality
4. Visibility controls and content warnings
5. Alt text and accessibility features
6. RSS feed integration for automatic posting
7. Troubleshooting multi-instance issues

## Mastodon Requirements

**Prerequisites**:

- Account on any Mastodon instance
- Instance-specific app registration (automatic)

**Development vs. Production**:

- Development: Test with personal instance account
- Production: Multi-instance support with automatic app registration

## Implementation Phases

### Phase 1: Core Authentication (Week 1)

1. Create `MastodonAuthManager` with multi-instance support
2. Implement automatic app registration per instance
3. Create basic `MastodonAPIClient` wrapper around Mastodon.py
4. Test authentication across different instances

### Phase 2: Basic Status Creation (Week 1-2)

1. Create `MastodonAPI` main integration class
2. Implement basic status (toot) creation
3. Add media handling with alt text support
4. Test posting across instances with different capabilities

### Phase 3: SocialNetwork Interface (Week 2)

1. Create `Mastodon` core class extending SocialNetwork
2. Implement all required interface methods
3. Add Media system integration for images and videos
4. Test interface compliance and configuration management

### Phase 4: Platform-Specific Features (Week 2-3)

1. Implement reply functionality with threading
2. Add boost (repost) functionality
3. Add favorite functionality
4. Implement visibility controls and content warnings
5. Test federated features across instances

### Phase 5: Integration & Documentation (Week 3)

1. Add CLI action handlers for new actions
2. Test RSS feed integration and scheduling
3. Test multi-instance capabilities
4. Write comprehensive documentation with instance-specific guides

## Mastodon-Specific Considerations

- Variable character limits per instance (500-5000+)
- Automatic app registration per instance
- Federation and instance policies
- Privacy and visibility controls
- Content warnings and sensitive media
- Alt text support for accessibility

## Success Criteria

- [ ] Multi-instance support working
- [ ] Automatic app registration
- [ ] All SocialNetwork interface methods implemented
- [ ] Character limit detection per instance
- [ ] Media posting with alt text
- [ ] Reply, boost, and favorite functionality
- [ ] Privacy controls working
- [ ] RSS and scheduling integration
- [ ] Complete multi-instance documentation
