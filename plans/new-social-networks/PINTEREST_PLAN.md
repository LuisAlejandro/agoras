# Pinterest Implementation Plan

## Overview

Add Pinterest integration to agoras using OAuth 2.0 authentication and the official Pinterest Python API client, following the exact patterns established by TikTok and Instagram implementations.

## Priority: HIGH (user specified)

## Library Analysis

**pinterest-python-generated-api-client** provides:

- OAuth 2.0 authentication flow with Pinterest's API
- Pin creation with images and videos
- Board management and organization
- Pin analytics and insights
- Account and user profile management
- Comprehensive error handling and rate limiting

## Dependencies to Add

```
pinterest-python-generated-api-client>=0.5.0
```

## Architecture Overview

Following the established 4-layer architecture:

1. **Auth Layer** (`agoras/core/api/auth/pinterest.py`) - OAuth 2.0 management
2. **Client Layer** (`agoras/core/api/clients/pinterest.py`) - HTTP wrapper around Pinterest API
3. **API Layer** (`agoras/core/api/pinterest.py`) - Main integration class
4. **Core Layer** (`agoras/core/pinterest.py`) - SocialNetwork implementation

## Detailed Implementation Plans

### 1. Authentication Manager (`agoras/core/api/auth/pinterest.py`)

**Pattern**: Follow `agoras/core/api/auth/tiktok.py` OAuth 2.0 pattern

**Key Implementation Details**:

```python
class PinterestAuthManager(BaseAuthManager):
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str,
                 refresh_token: Optional[str] = None):
        # OAuth 2.0 configuration for Pinterest
```

**OAuth Flow Implementation**:

- Use Pinterest's OAuth 2.0 authorization URL with appropriate scopes
- Handle authorization code exchange for access tokens
- Implement refresh token logic (Pinterest tokens last 1 year)
- Support PKCE for enhanced security

**Key Scopes Required**:

- `pins:read` - Read pin data
- `pins:write` - Create and modify pins
- `boards:read` - Read board information
- `boards:write` - Create and modify boards
- `user_accounts:read` - Read user profile information

**Key Methods to Implement**:

- `authenticate()` - Check cached token, refresh if needed
- `authorize()` - Browser-based OAuth flow
- `_refresh_access_token()` - Handle Pinterest's token refresh
- `_validate_credentials()` - Ensure required credentials present

**Token Caching Strategy**:

```python
def _get_cache_filename(self) -> str:
    return f'pinterest-{self.app_id}.json'  # Follow established pattern

def _save_refresh_token_to_cache(self, token: str):
    cache_file = self._get_cache_filename()
    self._save_token_to_cache(cache_file, 'pinterest_refresh_token', token)
```

**Pinterest-Specific Considerations**:

- Handle Pinterest's longer token expiration (1 year)
- Support Pinterest's specific OAuth error codes
- Handle rate limiting (200 requests per hour per user)

### 2. API Client (`agoras/core/api/clients/pinterest.py`)

**Pattern**: Follow `agoras/core/api/clients/tiktok.py` structure

**Pinterest API Wrapper**:

```python
class PinterestAPIClient:
    def __init__(self, access_token: str):
        import openapi_generated.pinterest_client as pinterest

        self.client = pinterest.ApiClient()
        self.client.default_headers['Authorization'] = f'Bearer {access_token}'

        # Initialize API endpoints
        self.pins_api = pinterest.PinsApi(self.client)
        self.boards_api = pinterest.BoardsApi(self.client)
        self.user_api = pinterest.UserAccountApi(self.client)
```

**Key Methods to Implement**:

- `get_user_account()` - User profile information
- `create_pin()` - Create pin with media and metadata
- `get_boards()` - List user's boards
- `create_board()` - Create new board
- `get_pin()` - Get pin details
- `get_pin_analytics()` - Pin performance data
- `update_pin()` - Modify existing pin
- `delete_pin()` - Remove pin

**Pin Creation Pattern**:

```python
def create_pin(self, board_id: str, title: str, description: str = None,
               media_source_url: str = None, destination_url: str = None,
               alt_text: str = None) -> Dict[str, Any]:
    pin_create = {
        'board_id': board_id,
        'title': title,
        'description': description,
        'media_source': {
            'source_type': 'image_url',  # or 'video_url'
            'url': media_source_url
        },
        'link': destination_url,
        'alt_text': alt_text
    }

    return self.pins_api.pins_create(pin_create=pin_create)
```

**Board Management Pattern**:

```python
def get_boards(self, bookmark: str = None, page_size: int = 25):
    return self.boards_api.boards_list(
        bookmark=bookmark,
        page_size=page_size
    )

def create_board(self, name: str, description: str = None,
                privacy: str = 'PUBLIC'):
    board_create = {
        'name': name,
        'description': description,
        'privacy': privacy
    }
    return self.boards_api.boards_create(board_request=board_create)
```

**Error Handling Pattern**:

- Wrap Pinterest API exceptions into agoras-standard exceptions
- Handle Pinterest's specific error codes (rate limiting, permissions, etc.)
- Implement exponential backoff for rate limiting

### 3. Main API Integration (`agoras/core/api/pinterest.py`)

**Pattern**: Follow `agoras/core/api/tiktok.py` structure

**Class Structure**:

```python
class PinterestAPI:
    def __init__(self, app_id: str, app_secret: str, redirect_uri: str,
                 refresh_token: Optional[str] = None):
        self.auth_manager = PinterestAuthManager(
            app_id, app_secret, redirect_uri, refresh_token
        )
        self.client = None
```

**Async Method Wrappers**:

```python
async def create_pin(self, board_id: str, title: str, description: str,
                    media_url: str, destination_url: str = None) -> str:
    def _sync_create():
        response = self.client.create_pin(
            board_id, title, description, media_url, destination_url
        )
        return response.id  # Extract pin ID

    return await asyncio.to_thread(_sync_create)
```

**Key Methods**:

- `authenticate()` - Initialize auth manager and client
- `create_pin()` - Pin creation with media
- `get_boards()` - Board management
- `create_board()` - Board creation
- `get_pin_analytics()` - Analytics data
- `update_pin()` - Pin modification
- `delete_pin()` - Pin removal
- `disconnect()` - Cleanup resources

**Board Selection Logic**:

```python
async def get_default_board(self) -> str:
    """Get the first available board or create a default one."""
    def _sync_get_board():
        boards = self.client.get_boards(page_size=1)
        if boards.items:
            return boards.items[0].id
        else:
            # Create default board if none exist
            default_board = self.client.create_board(
                name="Agoras Posts",
                description="Posts created via Agoras"
            )
            return default_board.id

    return await asyncio.to_thread(_sync_get_board)
```

### 4. Core Platform Implementation (`agoras/core/pinterest.py`)

**Pattern**: Follow `agoras/core/tiktok.py` structure exactly

**Class Initialization**:

```python
class Pinterest(SocialNetwork):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Platform-specific configuration attributes
        self.pinterest_app_id = None
        self.pinterest_app_secret = None
        self.pinterest_redirect_uri = None
        self.pinterest_refresh_token = None
        # Pinterest-specific settings
        self.pinterest_board_id = None
        self.pinterest_board_name = None
        self.pinterest_pin_id = None
        self.pinterest_privacy = None
        self.api = None
```

**Client Initialization Pattern**:

```python
async def _initialize_client(self):
    # Get configuration using existing pattern
    self.pinterest_app_id = self._get_config_value('pinterest_app_id', 'PINTEREST_APP_ID')
    self.pinterest_app_secret = self._get_config_value('pinterest_app_secret', 'PINTEREST_APP_SECRET')
    self.pinterest_redirect_uri = self._get_config_value('pinterest_redirect_uri', 'PINTEREST_REDIRECT_URI')

    # Optional configuration
    self.pinterest_board_id = self._get_config_value('pinterest_board_id', 'PINTEREST_BOARD_ID')
    self.pinterest_board_name = self._get_config_value('pinterest_board_name', 'PINTEREST_BOARD_NAME')
    self.pinterest_privacy = self._get_config_value('pinterest_privacy', 'PINTEREST_PRIVACY') or 'PUBLIC'

    # Validation
    if not all([self.pinterest_app_id, self.pinterest_app_secret, self.pinterest_redirect_uri]):
        raise Exception('Pinterest app ID, app secret, and redirect URI are required.')

    # Initialize API
    self.api = PinterestAPI(
        self.pinterest_app_id, self.pinterest_app_secret,
        self.pinterest_redirect_uri, self.pinterest_refresh_token
    )
    await self.api.authenticate()
```

**SocialNetwork Interface Implementation**:

**post() Method Pattern** (Pinterest creates Pins, not posts):

```python
async def post(self, status_text, status_link,
               status_image_url_1=None, status_image_url_2=None,
               status_image_url_3=None, status_image_url_4=None):
    if not self.api:
        raise Exception('Pinterest API not initialized')

    # Pinterest requires at least one image
    image_urls = list(filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ]))

    if not image_urls:
        raise Exception('Pinterest requires at least one image for pin creation')

    # Get or create board
    board_id = await self._get_target_board()

    # Create pins for each image
    pin_ids = []
    images = await self.download_images(image_urls)

    try:
        for i, image in enumerate(images):
            if not image.content or not image.file_type:
                image.cleanup()
                raise Exception(f'Failed to validate image: {image.url}')

            # Pinterest prefers JPEG and PNG
            if image.file_type.mime not in ['image/jpeg', 'image/png', 'image/jpg']:
                image.cleanup()
                raise Exception(f'Invalid image type "{image.file_type.mime}" for Pinterest')

            # Create pin with title and description
            pin_title = f"{status_text} ({i+1})" if len(images) > 1 else status_text
            pin_id = await self.api.create_pin(
                board_id=board_id,
                title=pin_title[:100],  # Pinterest title limit
                description=status_text[:500],  # Pinterest description limit
                media_url=image.url,
                destination_url=status_link
            )
            pin_ids.append(pin_id)

    finally:
        # Cleanup all images
        for image in images:
            image.cleanup()

    # Return first pin ID for consistency
    primary_pin_id = pin_ids[0] if pin_ids else None
    self._output_status(primary_pin_id)
    return primary_pin_id
```

**Board Management Methods**:

```python
async def _get_target_board(self) -> str:
    """Get target board ID for pin creation."""
    if self.pinterest_board_id:
        return self.pinterest_board_id

    if self.pinterest_board_name:
        # Find board by name
        boards = await self.api.get_boards()
        for board in boards:
            if board.name == self.pinterest_board_name:
                return board.id

        # Create board if not found
        board_id = await self.api.create_board(
            name=self.pinterest_board_name,
            privacy=self.pinterest_privacy
        )
        return board_id

    # Use default board
    return await self.api.get_default_board()
```

**Pinterest-Specific Methods**:

```python
async def create_board(self, board_name: str, description: str = None):
    """Create a new Pinterest board."""
    if not self.api:
        raise Exception('Pinterest API not initialized')

    board_id = await self.api.create_board(
        name=board_name,
        description=description,
        privacy=self.pinterest_privacy
    )
    self._output_status(board_id)
    return board_id

async def get_pin_analytics(self, pin_id: str = None):
    """Get analytics for a pin."""
    if not self.api:
        raise Exception('Pinterest API not initialized')

    pin_id = pin_id or self.pinterest_pin_id
    if not pin_id:
        raise Exception('Pin ID is required for analytics')

    analytics = await self.api.get_pin_analytics(pin_id)
    return analytics
```

## Configuration System

**Required Configuration Variables**:

- `PINTEREST_APP_ID` - Pinterest Developer App ID
- `PINTEREST_APP_SECRET` - Pinterest Developer App Secret
- `PINTEREST_REDIRECT_URI` - OAuth callback URL

**Optional Configuration Variables**:

- `PINTEREST_REFRESH_TOKEN` - Cached refresh token
- `PINTEREST_BOARD_ID` - Specific board ID for pins
- `PINTEREST_BOARD_NAME` - Board name (will create if doesn't exist)
- `PINTEREST_PRIVACY` - Board privacy (PUBLIC, PROTECTED, SECRET)
- `PINTEREST_PIN_ID` - For analytics/delete actions

## CLI Integration

**Usage Examples**:

```bash
# Create pin with image
agoras publish --network pinterest --action post \
  --status-text "Beautiful sunset" \
  --status-link "https://example.com" \
  --status-image-url-1 "https://example.com/sunset.jpg"

# Create multiple pins
agoras publish --network pinterest --action post \
  --status-text "Photo collection" \
  --status-image-url-1 "https://example.com/photo1.jpg" \
  --status-image-url-2 "https://example.com/photo2.jpg" \
  --pinterest-board-name "My Collection"

# Video pin
agoras publish --network pinterest --action video \
  --video-url "https://example.com/video.mp4" \
  --video-title "My Video" --status-text "Check out this video!"

# Create board
agoras publish --network pinterest --action create-board \
  --pinterest-board-name "New Board" \
  --pinterest-board-description "Description here"

# Get pin analytics
agoras publish --network pinterest --action analytics \
  --pinterest-pin-id "pin_id_here"
```

**New Actions to Support**:

- `create-board` - Create new Pinterest board
- `analytics` - Get pin performance data
- Standard actions: `post`, `video`, `delete`

## Package Updates Required

**Import Additions**:

```python
# agoras/core/api/__init__.py
from .pinterest import PinterestAPI

# agoras/core/api/auth/__init__.py
from .pinterest import PinterestAuthManager

# agoras/core/api/clients/__init__.py
from .pinterest import PinterestAPIClient

# agoras/core/__init__.py
from .pinterest import Pinterest
```

## Documentation Requirements

### Credential Setup Guide (`docs/credentials/pinterest.rst`)

**Content Outline**:

1. Pinterest Developer Portal setup
2. App creation and configuration
3. OAuth redirect URI configuration
4. Scope selection and permissions
5. App verification process (if required)
6. Rate limiting considerations

### Usage Documentation (`docs/pinterest.rst`)

**Content Outline**:

1. Initial authentication setup
2. Pin creation examples
3. Board management
4. Video pin creation
5. Analytics usage
6. RSS feed integration for automatic pinning
7. Troubleshooting guide

## Pinterest Requirements

**Prerequisites**:

- Pinterest Developer account
- Standard app review process
- Compliance with Pinterest platform policies

**Development vs. Production**:

- Development: Test with personal account
- Production: Standard app review required

## Implementation Phases

### Phase 1: Core Authentication (Week 1)

1. Create `PinterestAuthManager` with OAuth 2.0 flow
2. Implement token caching system
3. Create basic `PinterestAPIClient` wrapper
4. Test authentication flow

### Phase 2: Basic Pin Creation (Week 1-2)

1. Create `PinterestAPI` main integration class
2. Implement basic pin creation with images
3. Add board management functionality
4. Test pin creation flow

### Phase 3: SocialNetwork Interface (Week 2)

1. Create `Pinterest` core class extending SocialNetwork
2. Implement all required interface methods
3. Add Media system integration
4. Test interface compliance

### Phase 4: Advanced Features (Week 2-3)

1. Add video pin support
2. Implement analytics functionality
3. Add board creation/management
4. Add bulk pin creation for multiple images

### Phase 5: Integration & Documentation (Week 3)

1. Add CLI action handlers
2. Test RSS feed integration
3. Test Google Sheets scheduling
4. Write comprehensive documentation

## Success Criteria

- [ ] Full OAuth 2.0 authentication flow working
- [ ] Pin creation with images and videos
- [ ] Board management (create, select, manage)
- [ ] Analytics integration working
- [ ] Multiple image handling (create separate pins)
- [ ] RSS feed integration for automatic pinning
- [ ] Google Sheets scheduling integration
- [ ] Complete documentation with setup guides
- [ ] Comprehensive error handling
