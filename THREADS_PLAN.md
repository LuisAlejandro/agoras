# Threads Implementation Plan

## Overview

Add Meta Threads integration to agoras using OAuth 2.0 authentication and the threadspipepy library, following the exact patterns established by TikTok and Instagram implementations.

## Priority: HIGH (user specified)

## Library Analysis

**threadspipepy** provides:

- OAuth 2.0 authentication with Meta's authorization server
- Post creation (text, images, videos, carousels)
- Repost functionality
- Reply system with threading
- Analytics and insights data
- Reply moderation (hide/unhide)
- Built-in rate limiting and error handling

## Dependencies to Add

```
threadspipepy>=0.4.5
```

## Architecture Overview

Following the established 4-layer architecture:

1. **Auth Layer** (`agoras/core/api/auth/threads.py`) - OAuth 2.0 management
2. **Client Layer** (`agoras/core/api/clients/threads.py`) - HTTP wrapper around threadspipepy
3. **API Layer** (`agoras/core/api/threads.py`) - Main integration class
4. **Core Layer** (`agoras/core/threads.py`) - SocialNetwork implementation

## Detailed Implementation Plans

### 1. Authentication Manager (`agoras/core/api/auth/threads.py`)

**Pattern**: Follow `agoras/core/api/auth/tiktok.py` exactly

**Key Implementation Details**:

```python
class ThreadsAuthManager(BaseAuthManager):
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str,
                 refresh_token: Optional[str] = None):
        # Similar to TikTok pattern but with Meta-specific parameters
```

**OAuth Flow Implementation**:

- Use threadspipepy's `get_auth_token()` for authorization URL generation
- Handle Meta's authorization response format
- Use `get_access_tokens()` for code-to-token exchange
- Cache long-lived tokens as refresh tokens (Meta tokens last 60 days)

**Key Methods to Implement**:

- `authenticate()` - Check cached token, refresh if needed
- `authorize()` - Browser-based OAuth flow using threadspipepy
- `_refresh_or_get_token()` - Handle Meta's token refresh pattern
- `_validate_credentials()` - Ensure app_id, app_secret, redirect_uri present

**Token Caching Strategy**:

```python
def _get_cache_filename(self) -> str:
    return f'threads-{self.app_id}.json'  # Follow TikTok pattern

def _save_refresh_token_to_cache(self, token: str):
    # Use existing base class token caching
    cache_file = self._get_cache_filename()
    self._save_token_to_cache(cache_file, 'threads_refresh_token', token)
```

**Meta-Specific Considerations**:

- Handle long-lived token format (60-day expiration)
- Extract user_id from profile response
- Support Meta's scope system ('threads_basic', 'threads_content_publish', etc.)

### 2. API Client (`agoras/core/api/clients/threads.py`)

**Pattern**: Follow `agoras/core/api/clients/tiktok.py` structure

**ThreadsPipe Wrapper**:

```python
class ThreadsAPIClient:
    def __init__(self, access_token: str, user_id: str):
        self.api = ThreadsPipe(
            access_token=access_token,
            user_id=user_id,
            handle_hashtags=True,  # Automatic hashtag processing
            auto_handle_hashtags=False  # Manual control
        )
```

**Key Methods to Implement**:

- `get_profile()` - User profile information
- `create_post()` - Text/media posts with reply controls
- `create_reply()` - Reply to specific posts
- `repost_post()` - Repost existing content
- `get_posts()` - User's post history
- `get_post_insights()` - Analytics data
- `hide_reply()` - Moderation functionality

**Media Handling**:

```python
def create_post(self, post_text: str, files: List[str] = None,
               file_captions: List[str] = None,
               who_can_reply: str = "everyone"):
    # ThreadsPipe handles file upload automatically
    return self.api.pipe(
        post=post_text,
        files=files or [],
        file_captions=file_captions or [],
        who_can_reply=who_can_reply
    )
```

**Error Handling Pattern**:

- Wrap threadspipepy exceptions into agoras-standard exceptions
- Handle Meta's specific error codes
- Implement retry logic for rate limiting

### 3. Main API Integration (`agoras/core/api/threads.py`)

**Pattern**: Follow `agoras/core/api/tiktok.py` structure

**Class Structure**:

```python
class ThreadsAPI:
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str,
                 refresh_token: Optional[str] = None):
        self.auth_manager = ThreadsAuthManager(
            app_id, app_secret, redirect_uri, refresh_token
        )
```

**Async Method Wrappers**:

```python
async def create_post(self, post_text: str, files: List[str] = None,
                     who_can_reply: str = "everyone") -> str:
    def _sync_post():
        response = self.client.create_post(post_text, files, who_can_reply)
        return response.get('id')  # Extract post ID

    return await asyncio.to_thread(_sync_post)
```

**Key Methods**:

- `authenticate()` - Initialize auth manager and client
- `create_post()` - Post creation with media support
- `create_reply()` - Reply functionality
- `repost()` - Share/repost functionality
- `get_post_insights()` - Analytics data
- `disconnect()` - Cleanup (threadspipepy handles internally)

### 4. Core Platform Implementation (`agoras/core/threads.py`)

**Pattern**: Follow `agoras/core/tiktok.py` structure exactly

**Class Initialization**:

```python
class Threads(SocialNetwork):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Platform-specific configuration attributes
        self.threads_app_id = None
        self.threads_app_secret = None
        self.threads_redirect_uri = None
        self.threads_refresh_token = None
        self.threads_who_can_reply = None
        # Action-specific attributes
        self.threads_post_id = None
        self.threads_reply_to_id = None
        self.api = None
```

**Client Initialization Pattern**:

```python
async def _initialize_client(self):
    # Get configuration using existing pattern
    self.threads_app_id = self._get_config_value('threads_app_id', 'THREADS_APP_ID')
    self.threads_app_secret = self._get_config_value('threads_app_secret', 'THREADS_APP_SECRET')

    # Validation
    if not all([self.threads_app_id, self.threads_app_secret, self.threads_redirect_uri]):
        raise Exception('Threads app ID, app secret, and redirect URI are required.')

    # Initialize API
    self.api = ThreadsAPI(
        self.threads_app_id, self.threads_app_secret,
        self.threads_redirect_uri, self.threads_refresh_token
    )
    await self.api.authenticate()
```

**SocialNetwork Interface Implementation**:

**post() Method Pattern**:

```python
async def post(self, status_text, status_link,
               status_image_url_1=None, status_image_url_2=None,
               status_image_url_3=None, status_image_url_4=None):
    # Combine text and link like other platforms
    post_text = f'{status_text} {status_link}'.strip()

    # Collect media files
    files = list(filter(None, [status_image_url_1, status_image_url_2,
                              status_image_url_3, status_image_url_4]))

    # Use Media system for download/validation
    if files:
        images = await self.download_images(files)
        try:
            validated_files = []
            for image in images:
                if image.content and image.file_type:
                    validated_files.append(image.url)
                else:
                    raise Exception(f'Failed to validate image: {image.url}')

            post_id = await self.api.create_post(
                post_text, validated_files, self.threads_who_can_reply
            )
        finally:
            # Cleanup following established pattern
            for image in images:
                image.cleanup()
```

**Platform-Specific Methods**:

```python
async def reply(self, reply_text, reply_to_id):
    # New method for Threads-specific reply functionality
    if not reply_to_id:
        reply_to_id = self.threads_reply_to_id

    if not reply_to_id:
        raise Exception('Reply to ID is required')

    reply_id = await self.api.create_reply(reply_text, reply_to_id)
    self._output_status(reply_id)
    return reply_id
```

## Configuration System

**Required Configuration Variables**:

- `THREADS_APP_ID` - Meta Developer App ID
- `THREADS_APP_SECRET` - Meta Developer App Secret
- `THREADS_REDIRECT_URI` - OAuth callback URL

**Optional Configuration Variables**:

- `THREADS_REFRESH_TOKEN` - Cached long-lived token
- `THREADS_WHO_CAN_REPLY` - Reply control setting
- `THREADS_POST_ID` - For share actions
- `THREADS_REPLY_TO_ID` - For reply actions
- `THREADS_REPLY_TEXT` - Reply content

## CLI Integration

**New Action Support**:
Add 'reply' action alongside existing actions

**Usage Examples**:

```bash
# Text post
agoras publish --network threads --action post \
  --status-text "Hello Threads!"

# Post with images
agoras publish --network threads --action post \
  --status-text "Check this out!" \
  --status-image-url-1 "https://example.com/image1.jpg"

# Reply to post
agoras publish --network threads --action reply \
  --threads-reply-text "Great post!" \
  --threads-reply-to-id "post_id_here"

# Repost
agoras publish --network threads --action share \
  --threads-post-id "post_id_to_repost"
```

## Package Updates Required

**Import Additions**:

```python
# agoras/core/api/__init__.py
from .threads import ThreadsAPI

# agoras/core/api/auth/__init__.py
from .threads import ThreadsAuthManager

# agoras/core/api/clients/__init__.py
from .threads import ThreadsAPIClient

# agoras/core/__init__.py
from .threads import Threads
```

## Documentation Requirements

### Credential Setup Guide (`docs/credentials/threads.rst`)

- Meta Developer Console setup
- App creation and configuration
- OAuth redirect URI setup
- Business account verification process
- App review requirements

### Usage Documentation (`docs/threads.rst`)

- Initial authentication setup
- Basic posting examples
- Media posting (images/videos)
- Reply functionality usage
- RSS feed integration
- Troubleshooting common issues

## Business Account Requirements

**Prerequisites**:

- Meta business account (similar to Instagram requirement)
- App verification through Meta's review process
- Compliance with Meta's platform policies

## Implementation Phases

### Phase 1: Core Authentication (Week 1)

1. Create `ThreadsAuthManager` with OAuth 2.0 flow
2. Implement token caching system
3. Create basic `ThreadsAPIClient` wrapper

### Phase 2: API Integration (Week 1-2)

1. Create `ThreadsAPI` main integration class
2. Implement basic post creation
3. Add media handling using existing Media system

### Phase 3: SocialNetwork Interface (Week 2)

1. Create `Threads` core class extending SocialNetwork
2. Implement all required interface methods
3. Add configuration management

### Phase 4: Platform-Specific Features (Week 2-3)

1. Implement reply functionality
2. Add repost/share functionality
3. Add analytics/insights

### Phase 5: Integration & Documentation (Week 3-4)

1. Add CLI action handlers
2. Test RSS feed integration
3. Write comprehensive documentation
4. Validate business account requirements

## Success Criteria

- [ ] Full OAuth 2.0 authentication flow working
- [ ] All SocialNetwork interface methods implemented
- [ ] Media system integration working
- [ ] Reply and repost functionality working
- [ ] RSS feed and scheduling integration working
- [ ] Complete documentation with credential setup
- [ ] Comprehensive error handling
