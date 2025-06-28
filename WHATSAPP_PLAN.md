# WhatsApp Implementation Plan

## Overview

Add WhatsApp integration to agoras using the official Meta Graph API directly, following the exact patterns established by existing platform implementations while creating foundation for a shared Meta platform base class.

## Priority: MEDIUM (messaging platform, different from social media)

## Library Analysis

**pyfacebook GraphAPI Client Integration** provides:

- Official WhatsApp Business API via Meta Graph API endpoints
- Shared GraphAPI client with Facebook and Instagram implementations
- Rich media support (images, videos, documents, audio)
- Interactive messaging (buttons, lists, quick replies)
- Template message management and creation
- Business profile and phone number management
- Comprehensive error handling matching Meta standards
- Foundation for shared Meta platform base class

## Dependencies to Add

```
# No additional dependencies needed
# Will use existing pyfacebook.GraphAPI client
# Shared with Facebook and Instagram implementations
```

## Architecture Overview

Following the established 4-layer architecture:

1. **Auth Layer** (`agoras/core/api/auth/whatsapp.py`) - Meta Graph API token management
2. **Client Layer** (`agoras/core/api/clients/whatsapp.py`) - pyfacebook GraphAPI wrapper
3. **API Layer** (`agoras/core/api/whatsapp.py`) - Main integration class
4. **Core Layer** (`agoras/core/whatsapp.py`) - SocialNetwork implementation

## Detailed Implementation Plans

### 1. Authentication Manager (`agoras/core/api/auth/whatsapp.py`)

**Pattern**: Follow `agoras/core/api/auth/facebook.py` structure for shared Meta authentication

**Key Implementation Details**:

```python
class WhatsAppAuthManager(BaseAuthManager):
    def __init__(self, access_token: str, phone_number_id: str,
                 business_account_id: str = None):
        # Meta Graph API authentication
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.business_account_id = business_account_id
```

**Meta Graph API Authentication**:

- Use Meta Graph API access tokens (same as Facebook/Instagram)
- Support both temporary and permanent access tokens
- Validate token permissions and phone number access
- Handle token refresh for permanent tokens

**Key Methods to Implement**:

- `authenticate()` - Validate access token and phone number
- `validate_token()` - Check token permissions and validity
- `get_phone_info()` - Retrieve phone number details via Graph API
- `_validate_credentials()` - Ensure required credentials present

**Token Management Strategy**:

```python
def _validate_access_token(self) -> bool:
    """Validate access token and phone number access."""
    try:
        from pyfacebook import GraphAPI
        graph_api = GraphAPI(access_token=self.access_token, version="23.0")
        response = graph_api.get_object(self.phone_number_id)
        return bool(response and response.get("verified_name"))
    except Exception:
        return False
```

**Meta-Specific Considerations**:

- Handle Meta Graph API token format (same as Facebook/Instagram)
- Support business account verification requirements
- Handle phone number verification status
- Manage webhook token validation

### 2. API Client (`agoras/core/api/clients/whatsapp.py`)

**Pattern**: Follow `agoras/core/api/clients/facebook.py` structure

**WhatsApp Graph API Client**:

```python
class WhatsAppAPIClient:
    def __init__(self, access_token: str, phone_number_id: str):
        from pyfacebook import GraphAPI

        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.graph_api = GraphAPI(
            access_token=access_token,
            version="23.0"
        )
```

**Key Methods to Implement**:

- `send_message()` - Send text messages with formatting
- `send_image()` - Send images with captions
- `send_video()` - Send videos with captions
- `send_document()` - Send files and documents
- `send_audio()` - Send audio files
- `send_location()` - Send location data
- `send_contact()` - Send contact information
- `send_template()` - Send template messages

**Message Sending Pattern**:

```python
def send_message(self, to: str, text: str, buttons=None) -> Dict[str, Any]:
    """Send text message via pyfacebook GraphAPI."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    if buttons:
        payload["type"] = "interactive"
        payload["interactive"] = {
            "type": "button",
            "body": {"text": text},
            "action": {"buttons": buttons}
        }

    endpoint = f"{self.phone_number_id}/messages"
    response = self.graph_api.post_object(endpoint, payload)

    if response and response.get("messages"):
        return {"message_id": response["messages"][0]["id"], "status": "sent"}
    else:
        raise Exception(f"WhatsApp API error: {response}")
```

**Media Handling Pattern**:

```python
def send_image(self, to: str, image_url: str, caption: str = None) -> Dict[str, Any]:
    """Send image message via pyfacebook GraphAPI."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": image_url}
    }

    if caption:
        payload["image"]["caption"] = caption

    endpoint = f"{self.phone_number_id}/messages"
    response = self.graph_api.post_object(endpoint, payload)

    if response and response.get("messages"):
        return {"message_id": response["messages"][0]["id"], "status": "sent"}
    else:
        raise Exception(f"WhatsApp API error: {response}")
```

**Error Handling Pattern**:

- Use pyfacebook GraphAPI error handling mechanisms
- Parse WhatsApp-specific error codes from Graph API responses
- Implement retry logic for rate limits and temporary failures
- Match error handling patterns with Facebook/Instagram implementations

### 3. Main API Integration (`agoras/core/api/whatsapp.py`)

**Pattern**: Follow `agoras/core/api/facebook.py` structure

**Class Structure**:

```python
class WhatsAppAPI:
    def __init__(self, access_token: str, phone_number_id: str,
                 business_account_id: str = None):
        self.auth_manager = WhatsAppAuthManager(
            access_token, phone_number_id, business_account_id
        )
        self.client = None
```

**Async Method Wrappers**:

```python
async def send_message(self, to: str, text: str, buttons=None) -> str:
    def _sync_send():
        response = self.client.send_message(to, text, buttons=buttons)
        return response['message_id']

    return await asyncio.to_thread(_sync_send)
```

**Key Methods**:

- `authenticate()` - Initialize auth manager and client
- `send_message()` - Text message sending
- `send_image()` - Image message sending
- `send_video()` - Video message sending
- `send_document()` - Document sending
- `send_template()` - Template message sending
- `get_business_profile()` - Business profile information
- `disconnect()` - Cleanup resources

**Business Profile Management**:

```python
async def get_business_profile(self) -> Dict[str, Any]:
    """Get WhatsApp Business profile via pyfacebook GraphAPI."""
    def _sync_get_profile():
        endpoint = f"{self.client.phone_number_id}/whatsapp_business_profile"
        response = self.client.graph_api.get_object(endpoint)
        if response and response.get("data"):
            return response["data"][0]
        else:
            raise Exception(f"Failed to get business profile: {response}")

    return await asyncio.to_thread(_sync_get_profile)
```

### 4. Core Platform Implementation (`agoras/core/whatsapp.py`)

**Pattern**: Follow `agoras/core/facebook.py` structure exactly

**Class Initialization**:

```python
class WhatsApp(SocialNetwork):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Platform-specific configuration attributes
        self.whatsapp_access_token = None
        self.whatsapp_phone_number_id = None
        self.whatsapp_business_account_id = None
        # WhatsApp-specific settings
        self.whatsapp_recipient = None
        self.whatsapp_message_id = None
        self.api = None
```

**Client Initialization Pattern**:

```python
async def _initialize_client(self):
    # Get configuration using existing pattern
    self.whatsapp_access_token = self._get_config_value('whatsapp_access_token', 'WHATSAPP_ACCESS_TOKEN')
    self.whatsapp_phone_number_id = self._get_config_value('whatsapp_phone_number_id', 'WHATSAPP_PHONE_NUMBER_ID')
    self.whatsapp_business_account_id = self._get_config_value('whatsapp_business_account_id', 'WHATSAPP_BUSINESS_ACCOUNT_ID')

    # Required recipient for messaging
    self.whatsapp_recipient = self._get_config_value('whatsapp_recipient', 'WHATSAPP_RECIPIENT')

    # Validation
    if not all([self.whatsapp_access_token, self.whatsapp_phone_number_id]):
        raise Exception('WhatsApp access token and phone number ID are required.')

    if not self.whatsapp_recipient:
        raise Exception('WhatsApp recipient phone number is required.')

    # Initialize API
    self.api = WhatsAppAPI(
        self.whatsapp_access_token,
        self.whatsapp_phone_number_id,
        self.whatsapp_business_account_id
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
        raise Exception('WhatsApp API not initialized')

    # Combine text and link
    message_text = f'{status_text}\n{status_link}'.strip() if status_link else status_text

    # Handle images
    image_urls = list(filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ]))

    if image_urls:
        # WhatsApp supports multiple media in sequence
        message_ids = []
        images = await self.download_images(image_urls)

        try:
            for i, image in enumerate(images):
                if image.content and image.file_type:
                    # First image gets the full caption, others get minimal caption
                    caption = message_text if i == 0 else f"Image {i+1}"

                    message_id = await self.api.send_image(
                        to=self.whatsapp_recipient,
                        image_url=image.url,
                        caption=caption
                    )
                    message_ids.append(message_id)
                else:
                    raise Exception(f'Failed to validate image: {image.url}')
        finally:
            for image in images:
                image.cleanup()

        # Return first message ID for consistency
        primary_message_id = message_ids[0] if message_ids else None
    else:
        # Text-only message
        primary_message_id = await self.api.send_message(
            to=self.whatsapp_recipient,
            text=message_text
        )

    self._output_status(primary_message_id)
    return primary_message_id
```

**WhatsApp-Specific Methods**:

```python
async def send_contact(self, contact_name: str, phone_number: str) -> str:
    """Send a contact card."""
    if not self.api:
        raise Exception('WhatsApp API not initialized')

    message_id = await self.api.send_contact(
        to=self.whatsapp_recipient,
        name=contact_name,
        phone=phone_number
    )
    self._output_status(message_id)
    return message_id

async def send_location(self, latitude: float, longitude: float,
                       name: str = None) -> str:
    """Send a location message."""
    if not self.api:
        raise Exception('WhatsApp API not initialized')

    message_id = await self.api.send_location(
        to=self.whatsapp_recipient,
        latitude=latitude,
        longitude=longitude,
        name=name
    )
    self._output_status(message_id)
    return message_id
```

## Configuration System

**Required Configuration Variables**:

- `WHATSAPP_ACCESS_TOKEN` - Meta Graph API access token
- `WHATSAPP_PHONE_NUMBER_ID` - WhatsApp Business phone number ID
- `WHATSAPP_RECIPIENT` - Target recipient phone number

**Optional Configuration Variables**:

- `WHATSAPP_BUSINESS_ACCOUNT_ID` - WhatsApp Business Account ID
- `WHATSAPP_MESSAGE_ID` - For status/tracking actions
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN` - For webhook verification

## CLI Integration

**Usage Examples**:

```bash
# Send text message
agoras publish --network whatsapp --action post \
  --status-text "Hello from agoras!" \
  --status-link "https://example.com"

# Send message with image
agoras publish --network whatsapp --action post \
  --status-text "Check this out!" \
  --status-image-url-1 "https://example.com/image.jpg"

# Send video
agoras publish --network whatsapp --action video \
  --video-url "https://example.com/video.mp4" \
  --video-title "My Video"

# Send contact
agoras publish --network whatsapp --action contact \
  --whatsapp-contact-name "John Doe" \
  --whatsapp-contact-phone "+1234567890"

# Send location
agoras publish --network whatsapp --action location \
  --whatsapp-latitude "37.7749" \
  --whatsapp-longitude "-122.4194" \
  --whatsapp-location-name "San Francisco"
```

**New Actions to Support**:

- `contact` - Send contact information
- `location` - Send location data
- `template` - Send template messages
- Standard actions: `post`, `video`, `delete`

## Package Updates Required

**Import Additions**:

```python
# agoras/core/api/__init__.py
from .whatsapp import WhatsAppAPI

# agoras/core/api/auth/__init__.py
from .whatsapp import WhatsAppAuthManager

# agoras/core/api/clients/__init__.py
from .whatsapp import WhatsAppAPIClient

# agoras/core/__init__.py
from .whatsapp import WhatsApp
```

## Future Meta Platform Base Class

**Shared Meta Platform Foundation**:
The WhatsApp implementation creates the foundation for a shared Meta platform base class that can be used by WhatsApp, Facebook, and Instagram:

```python
# Future: agoras/core/api/auth/meta_base.py
class MetaAuthManager(BaseAuthManager):
    """Shared authentication for Meta platforms (WhatsApp, Facebook, Instagram)"""

# Future: agoras/core/api/clients/meta_base.py
class MetaAPIClient:
    """Shared Graph API client for Meta platforms"""

# Future: agoras/core/api/meta_base.py
class MetaAPI:
    """Shared API integration for Meta platforms"""
```

**Benefits**:

- Consistent authentication across Meta platforms
- Shared error handling and rate limiting
- Unified configuration patterns
- Reduced code duplication

## Documentation Requirements

### Credential Setup Guide (`docs/credentials/whatsapp.rst`)

**Content Outline**:

1. Meta Developer Account setup (shared with Facebook/Instagram)
2. WhatsApp Business API application creation
3. Phone number registration and verification
4. Access token generation and management
5. Business verification requirements
6. Webhook configuration for production
7. Rate limiting and compliance guidelines

### Usage Documentation (`docs/whatsapp.rst`)

**Content Outline**:

1. Initial API setup and authentication
2. Sending messages to individual recipients
3. Media posting (images, videos, documents)
4. Interactive messaging (buttons, lists)
5. Template message creation and sending
6. Business profile management
7. RSS feed integration for automatic messaging
8. Troubleshooting business verification and permissions

## WhatsApp Requirements

**Prerequisites**:

- Meta Developer Account (shared with Facebook/Instagram)
- WhatsApp Business Account
- Phone number verification
- Business verification (for production)

**Development vs. Production**:

- Development: Use test phone numbers and temporary tokens
- Production: Complete business verification and use permanent tokens

## Implementation Phases

### Phase 1: Core Authentication (Week 1)

1. Create `WhatsAppAuthManager` with Graph API token validation
2. Implement phone number verification via Graph API
3. Create basic `WhatsAppAPIClient` for Graph API calls
4. Test authentication and basic API connectivity

### Phase 2: Basic Message Sending (Week 1-2)

1. Create `WhatsAppAPI` main integration class
2. Implement basic text message sending via Graph API
3. Add Media system integration for images and videos
4. Test message sending to verified recipients

### Phase 3: SocialNetwork Interface (Week 2)

1. Create `WhatsApp` core class extending SocialNetwork
2. Implement all required interface methods
3. Add configuration management and validation
4. Test interface compliance and media handling

### Phase 4: Advanced Features (Week 2-3)

1. Implement contact and location sharing via Graph API
2. Add document and audio file support
3. Add template message functionality
4. Test business features and profile management

### Phase 5: Integration & Documentation (Week 3)

1. Add CLI action handlers for new actions
2. Test RSS feed integration and scheduling
3. Test business verification requirements
4. Write comprehensive documentation with setup guides

## Success Criteria

- [ ] WhatsApp Business API authentication via Graph API working
- [ ] Message sending to verified recipients
- [ ] Media posting (images, videos, documents, audio)
- [ ] Contact and location sharing functionality
- [ ] Template message creation and sending
- [ ] Business profile management
- [ ] RSS feed integration for automatic messaging
- [ ] Google Sheets scheduling integration
- [ ] Complete documentation with business setup guides
- [ ] Foundation for shared Meta platform base class
- [ ] Comprehensive error handling matching Meta standards

## WhatsApp-Specific Considerations

**Graph API Features**:

- Rich media support (images, videos, documents, audio)
- Interactive messaging (buttons, lists, quick replies)
- Template messages for notifications
- Contact and location sharing
- Business profile management
- Message status tracking (sent, delivered, read)

**Rate Limiting**:

- Standard Meta Graph API rate limits
- 1000 messages per day (free tier)
- Higher limits with business verification
- Rate limits per recipient per time period
- Automatic retry with exponential backoff

**Business Requirements**:

- Meta business verification for production
- Phone number ownership verification
- Compliance with WhatsApp Business Policy
- Message template approval process

**Message Types**:

- Text messages with formatting
- Media messages (image, video, document, audio)
- Interactive messages (buttons, lists)
- Template messages (notifications)
- Location and contact sharing

## Risk Assessment

**Medium Risk**:

- Business verification requirements for production
- Strict compliance with WhatsApp policies
- Rate limiting for unverified businesses

**Low Risk**:

- Official Meta Graph API with comprehensive documentation
- Shared authentication patterns with Facebook/Instagram
- Clear business guidelines and support
- Foundation for shared Meta platform base class

**Considerations**:

- Business verification process timing
- Message template approval delays
- Recipient opt-in requirements
- Cost implications for high-volume messaging
- Maintaining consistency with Facebook/Instagram implementations
