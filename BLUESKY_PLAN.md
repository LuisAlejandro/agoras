# Bluesky Implementation Plan

## Overview

Add Bluesky integration to agoras using AT Protocol authentication and the atproto Python library.

## Priority: MEDIUM (after Threads and Pinterest)

## Library Analysis

**atproto** provides:

- AT Protocol authentication with OAuth 2.0 support
- Post creation with text, images, and links
- Reply and quote functionality
- Follow/unfollow capabilities
- Feed and notification management
- Rich text and embed support

## Dependencies to Add

```
atproto>=0.0.46
```

## Architecture Overview

Following the established 4-layer architecture:

1. **Auth Layer** (`agoras/core/api/auth/bluesky.py`) - AT Protocol OAuth 2.0
2. **Client Layer** (`agoras/core/api/clients/bluesky.py`) - HTTP wrapper around atproto
3. **API Layer** (`agoras/core/api/bluesky.py`) - Main integration class
4. **Core Layer** (`agoras/core/bluesky.py`) - SocialNetwork implementation

## Detailed Implementation Plans

### 1. Authentication Manager (`agoras/core/api/auth/bluesky.py`)

**Pattern**: Follow `agoras/core/api/auth/tiktok.py` OAuth 2.0 pattern

**Key Implementation Details**:

```python
class BlueskyAuthManager(BaseAuthManager):
    def __init__(self, identifier: str, password: str = None,
                 oauth_client_id: str = None, oauth_client_secret: str = None,
                 refresh_token: Optional[str] = None):
        # Support both password and OAuth authentication
```

**Authentication Options**:

- **Password Authentication**: Simple username/password (easier for personal use)
- **OAuth 2.0**: Full OAuth flow for production applications
- **App Passwords**: Bluesky-specific app password system

**Key Methods to Implement**:

- `authenticate()` - Check cached token, refresh if needed
- `authorize()` - OAuth flow or password authentication
- `_refresh_access_token()` - Handle AT Protocol token refresh
- `_validate_credentials()` - Ensure required credentials present

**Token Caching Strategy**:

```python
def _get_cache_filename(self) -> str:
    return f'bluesky-{self.identifier}.json'

def _save_refresh_token_to_cache(self, token: str):
    cache_file = self._get_cache_filename()
    self._save_token_to_cache(cache_file, 'bluesky_refresh_token', token)
```

**AT Protocol Considerations**:

- Handle DID (Decentralized Identifier) resolution
- Support custom PDS (Personal Data Server) endpoints
- Handle AT Protocol session management

### 2. API Client (`agoras/core/api/clients/bluesky.py`)

**Pattern**: Follow `agoras/core/api/clients/tiktok.py` structure

**Bluesky API Wrapper**:

```python
class BlueskyAPIClient:
    def __init__(self, session):
        from atproto import Client
        self.client = Client()
        self.client.configure(session)
```

**Key Methods to Implement**:

- `get_profile()` - User profile information
- `create_post()` - Post with text, images, embeds
- `create_reply()` - Reply to specific posts
- `like_post()` - Like functionality
- `repost()` - Repost with optional quote
- `delete_post()` - Delete posts
- `upload_blob()` - Media upload

**Post Creation Pattern**:

```python
def create_post(self, text: str, images: List[bytes] = None,
               embed_url: str = None, reply_to: str = None):
    # Handle rich text, mentions, hashtags
    # Upload images as blobs
    # Create embeds for links
    # Support reply threading
    return self.client.send_post(
        text=text,
        images=images,
        embed=embed_url,
        reply_to=reply_to
    )
```

**Media Handling Pattern**:

```python
def upload_image(self, image_bytes: bytes, mime_type: str) -> str:
    blob = self.client.upload_blob(image_bytes)
    return blob.blob
```

### 3. Main API Integration (`agoras/core/api/bluesky.py`)

**Pattern**: Follow `agoras/core/api/tiktok.py` structure

**Class Structure**:

```python
class BlueskyAPI:
    def __init__(self, identifier: str, password: str = None,
                 oauth_client_id: str = None, oauth_client_secret: str = None,
                 refresh_token: Optional[str] = None):
        self.auth_manager = BlueskyAuthManager(
            identifier, password, oauth_client_id, oauth_client_secret, refresh_token
        )
```

**Async Method Wrappers**:

```python
async def create_post(self, text: str, images: List[bytes] = None,
                     embed_url: str = None) -> str:
    def _sync_post():
        response = self.client.create_post(text, images, embed_url)
        return response.uri  # AT Protocol URI

    return await asyncio.to_thread(_sync_post)
```

**Key Methods**:

- `authenticate()` - Initialize auth manager and client
- `create_post()` - Post creation with media and embeds
- `create_reply()` - Reply functionality
- `like_post()` - Like functionality
- `repost()` - Repost/quote functionality
- `delete_post()` - Post deletion
- `disconnect()` - Session cleanup

### 4. Core Platform Implementation (`agoras/core/bluesky.py`)

**Pattern**: Follow `agoras/core/tiktok.py` structure exactly

**Class Initialization**:

```python
class Bluesky(SocialNetwork):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Platform-specific configuration
        self.bluesky_identifier = None
        self.bluesky_password = None
        self.bluesky_oauth_client_id = None
        self.bluesky_oauth_client_secret = None
        self.bluesky_refresh_token = None
        # Action-specific attributes
        self.bluesky_post_id = None
        self.bluesky_reply_to_uri = None
        self.api = None
```

**Client Initialization Pattern**:

```python
async def _initialize_client(self):
    self.bluesky_identifier = self._get_config_value('bluesky_identifier', 'BLUESKY_IDENTIFIER')
    self.bluesky_password = self._get_config_value('bluesky_password', 'BLUESKY_PASSWORD')

    # OAuth support
    self.bluesky_oauth_client_id = self._get_config_value('bluesky_oauth_client_id', 'BLUESKY_OAUTH_CLIENT_ID')
    self.bluesky_oauth_client_secret = self._get_config_value('bluesky_oauth_client_secret', 'BLUESKY_OAUTH_CLIENT_SECRET')

    if not self.bluesky_identifier:
        raise Exception('Bluesky identifier (username/DID) is required.')

    if not self.bluesky_password and not all([self.bluesky_oauth_client_id, self.bluesky_oauth_client_secret]):
        raise Exception('Either password or OAuth credentials are required.')

    self.api = BlueskyAPI(
        self.bluesky_identifier, self.bluesky_password,
        self.bluesky_oauth_client_id, self.bluesky_oauth_client_secret,
        self.bluesky_refresh_token
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
        raise Exception('Bluesky API not initialized')

    # Combine text and link
    post_text = f'{status_text} {status_link}'.strip()

    # Handle images
    image_blobs = []
    image_urls = list(filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ]))

    if image_urls:
        images = await self.download_images(image_urls)
        try:
            for image in images:
                if image.content and image.file_type:
                    # Convert to format expected by atproto
                    blob = await self.api.upload_image(image.content, image.file_type.mime)
                    image_blobs.append(blob)
                else:
                    raise Exception(f'Failed to validate image: {image.url}')
        finally:
            for image in images:
                image.cleanup()

    # Create post
    post_uri = await self.api.create_post(
        text=post_text,
        images=image_blobs,
        embed_url=status_link if status_link else None
    )

    self._output_status(post_uri)
    return post_uri
```

**Bluesky-Specific Methods**:

```python
async def reply(self, reply_text: str, reply_to_uri: str):
    """Reply to a Bluesky post."""
    if not self.api:
        raise Exception('Bluesky API not initialized')

    if not reply_to_uri:
        reply_to_uri = self.bluesky_reply_to_uri

    if not reply_to_uri:
        raise Exception('Reply to URI is required')

    reply_uri = await self.api.create_reply(reply_text, reply_to_uri)
    self._output_status(reply_uri)
    return reply_uri

async def quote_post(self, quote_text: str, post_uri: str):
    """Quote a Bluesky post."""
    if not self.api:
        raise Exception('Bluesky API not initialized')

    quote_uri = await self.api.repost(post_uri, quote_text)
    self._output_status(quote_uri)
    return quote_uri
```

## Configuration System

**Required Configuration Variables**:

- `BLUESKY_IDENTIFIER` - Username, email, or DID

**Authentication Options** (choose one):

- `BLUESKY_PASSWORD` - Account password or app password
- `BLUESKY_OAUTH_CLIENT_ID` + `BLUESKY_OAUTH_CLIENT_SECRET` - OAuth credentials

**Optional Configuration Variables**:

- `BLUESKY_REFRESH_TOKEN` - Cached refresh token
- `BLUESKY_POST_ID` - For like/delete actions
- `BLUESKY_REPLY_TO_URI` - For reply actions
- `BLUESKY_SERVER` - Custom PDS server (defaults to bsky.social)

## CLI Integration

**Usage Examples**:

```bash
# Text post
agoras publish --network bluesky --action post \
  --status-text "Hello Bluesky!" --status-link "https://example.com"

# Post with images
agoras publish --network bluesky --action post \
  --status-text "Check this out!" \
  --status-image-url-1 "https://example.com/image1.jpg" \
  --status-image-url-2 "https://example.com/image2.jpg"

# Reply to post
agoras publish --network bluesky --action reply \
  --bluesky-reply-text "Great post!" \
  --bluesky-reply-to-uri "at://did:plc:example/app.bsky.feed.post/rkey"

# Like post
agoras publish --network bluesky --action like \
  --bluesky-post-id "at://did:plc:example/app.bsky.feed.post/rkey"

# Quote post
agoras publish --network bluesky --action quote \
  --bluesky-quote-text "Interesting point!" \
  --bluesky-post-uri "at://did:plc:example/app.bsky.feed.post/rkey"
```

**New Actions to Support**:

- `reply` - Reply to posts
- `quote` - Quote posts
- Standard actions: `post`, `like`, `share`, `delete`

## Package Updates Required

**Import Additions**:

```python
# agoras/core/api/__init__.py
from .bluesky import BlueskyAPI

# agoras/core/api/auth/__init__.py
from .bluesky import BlueskyAuthManager

# agoras/core/api/clients/__init__.py
from .bluesky import BlueskyAPIClient

# agoras/core/__init__.py
from .bluesky import Bluesky
```

## Documentation Requirements

### Credential Setup Guide (`docs/credentials/bluesky.rst`)

**Content Outline**:

1. Bluesky account creation
2. App password generation for personal use
3. OAuth app setup for production applications
4. AT Protocol concepts and terminology
5. Custom PDS server configuration
6. DID resolution and identity management

### Usage Documentation (`docs/bluesky.rst`)

**Content Outline**:

1. Authentication setup (password vs OAuth)
2. Basic posting examples with character limits
3. Reply and quote functionality
4. Image posting with blob handling
5. Custom server usage
6. RSS feed integration for automatic posting
7. Troubleshooting AT Protocol issues

## Bluesky Requirements

**Prerequisites**:

- Bluesky account or compatible AT Protocol account
- For OAuth: Developer account with Bluesky (when available)

**Development vs. Production**:

- Development: Use app passwords for simplicity
- Production: Implement full OAuth flow for user authentication

## Implementation Phases

### Phase 1: Core Authentication (Week 1)

1. Create `BlueskyAuthManager` with dual authentication support
2. Implement session management and token caching
3. Create basic `BlueskyAPIClient` wrapper around atproto
4. Test both password and OAuth authentication flows

### Phase 2: Basic Posting (Week 1-2)

1. Create `BlueskyAPI` main integration class
2. Implement basic post creation with text
3. Add image handling using existing Media system
4. Test post creation and media upload

### Phase 3: SocialNetwork Interface (Week 2)

1. Create `Bluesky` core class extending SocialNetwork
2. Implement all required interface methods
3. Add Media system integration for images
4. Test interface compliance and configuration management

### Phase 4: Platform-Specific Features (Week 2-3)

1. Implement reply functionality with threading
2. Add quote post functionality
3. Add like/unlike functionality
4. Add delete functionality
5. Test AT Protocol specific features

### Phase 5: Integration & Documentation (Week 3)

1. Add CLI action handlers for new actions
2. Test RSS feed integration and scheduling
3. Test custom PDS server support
4. Write comprehensive documentation with setup guides

## Bluesky-Specific Considerations

**AT Protocol Features**:

- Decentralized architecture support
- DID-based identity system
- Custom PDS server support
- Rich text and facet handling

**Authentication Flexibility**:

- Simple password authentication for personal use
- OAuth 2.0 for production applications
- App password system for security

**Content Limitations**:

- 300 character limit for posts
- 4 images maximum per post
- Rich text support with mentions and links
- Thread/reply structure

**Rate Limiting**:

- Server-dependent rate limits
- Implement exponential backoff
- Handle AT Protocol error codes

## Success Criteria

- [ ] Both password and OAuth authentication working
- [ ] All SocialNetwork interface methods implemented
- [ ] Reply and quote functionality working
- [ ] Image posting with proper blob handling
- [ ] Like and delete functionality
- [ ] RSS feed and scheduling integration
- [ ] Custom server support
- [ ] Complete documentation

## Risk Assessment

**Medium Risk**:

- AT Protocol still evolving
- Limited third-party server adoption
- Authentication complexity

**Low Risk**:

- Active library maintenance (atproto)
- Strong community support
- Clear API documentation
