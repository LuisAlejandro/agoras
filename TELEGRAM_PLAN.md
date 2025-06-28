# Telegram Implementation Plan

## Overview

Add Telegram integration to agoras using Bot API and the python-telegram-bot library, following the exact patterns established by existing platform implementations.

## Priority: MEDIUM (messaging platform, different from social media)

## Library Analysis

**python-telegram-bot** provides:

- Async-first architecture with comprehensive Bot API support
- Rich message types (text, media, polls, games, stickers)
- Inline keyboards and callback query handling
- Bot commands and conversation handlers
- File upload/download with automatic media handling
- Webhook and polling support for updates
- Comprehensive error handling and rate limiting

## Dependencies to Add

```
python-telegram-bot>=22.1
```

## Architecture Overview

Following the established 4-layer architecture:

1. **Auth Layer** (`agoras/core/api/auth/telegram.py`) - Bot token management
2. **Client Layer** (`agoras/core/api/clients/telegram.py`) - HTTP wrapper around python-telegram-bot
3. **API Layer** (`agoras/core/api/telegram.py`) - Main integration class
4. **Core Layer** (`agoras/core/telegram.py`) - SocialNetwork implementation

## Detailed Implementation Plans

### 1. Authentication Manager (`agoras/core/api/auth/telegram.py`)

**Pattern**: Follow `agoras/core/api/auth/tiktok.py` structure but simplified for bot tokens

**Key Implementation Details**:

```python
class TelegramAuthManager(BaseAuthManager):
    def __init__(self, bot_token: str, chat_id: str = None):
        # Bot token authentication (no OAuth needed)
        self.bot_token = bot_token
        self.chat_id = chat_id  # Target chat/channel ID
```

**Bot Token Authentication**:

- Use Telegram Bot API tokens (obtained from @BotFather)
- No OAuth 2.0 flow needed - tokens are permanent
- Support both private chats and channels/groups
- Validate token format and bot permissions

**Key Methods to Implement**:

- `authenticate()` - Validate bot token and get bot info
- `validate_bot_token()` - Check token format and validity
- `get_bot_info()` - Retrieve bot details from Telegram
- `_validate_credentials()` - Ensure bot token is present

**Token Management Strategy**:

```python
def _validate_bot_token(self) -> bool:
    """Validate bot token format and API access."""
    if not self.bot_token or not self.bot_token.startswith('bot'):
        return False

    try:
        # Test token by getting bot info
        bot_info = self._get_bot_info()
        return bool(bot_info.get('ok'))
    except Exception:
        return False
```

**Telegram-Specific Considerations**:

- Handle bot token format validation
- Support both private and group/channel messaging
- Handle bot permissions and admin requirements
- No token refresh needed (tokens are permanent)

### 2. API Client (`agoras/core/api/clients/telegram.py`)

**Pattern**: Follow `agoras/core/api/clients/tiktok.py` structure

**Telegram API Wrapper**:

```python
class TelegramAPIClient:
    def __init__(self, bot_token: str):
        from telegram import Bot
        from telegram.constants import ParseMode

        self.bot = Bot(token=bot_token)
        self.default_parse_mode = ParseMode.HTML
```

**Key Methods to Implement**:

- `get_me()` - Bot information
- `send_message()` - Send text messages with formatting
- `send_photo()` - Send images with captions
- `send_video()` - Send videos with captions
- `send_document()` - Send files and documents
- `send_audio()` - Send audio files
- `edit_message_text()` - Edit sent messages
- `delete_message()` - Delete messages
- `get_file()` - Get file information for downloads

**Message Sending Pattern**:

```python
def send_message(self, chat_id: str, text: str,
                parse_mode: str = None, reply_markup=None) -> Dict[str, Any]:
    """Send text message with optional formatting and keyboards."""
    try:
        message = self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode or self.default_parse_mode,
            reply_markup=reply_markup
        )
        return message.to_dict()
    except TelegramError as e:
        raise Exception(f"Failed to send message: {e}")
```

**Media Handling Pattern**:

```python
def send_photo(self, chat_id: str, photo, caption: str = None) -> Dict[str, Any]:
    """Send photo with optional caption."""
    message = self.bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        parse_mode=self.default_parse_mode
    )
    return message.to_dict()
```

**Error Handling Pattern**:

- Wrap python-telegram-bot exceptions into agoras-standard exceptions
- Handle Telegram-specific error codes (rate limits, permissions, etc.)
- Implement retry logic for temporary failures

### 3. Main API Integration (`agoras/core/api/telegram.py`)

**Pattern**: Follow `agoras/core/api/tiktok.py` structure

**Class Structure**:

```python
class TelegramAPI:
    def __init__(self, bot_token: str, chat_id: str = None):
        self.auth_manager = TelegramAuthManager(bot_token, chat_id)
        self.client = None
```

**Async Method Wrappers**:

```python
async def send_message(self, chat_id: str, text: str,
                      reply_markup=None) -> str:
    def _sync_send():
        response = self.client.send_message(chat_id, text, reply_markup=reply_markup)
        return str(response['message_id'])  # Return message ID

    return await asyncio.to_thread(_sync_send)
```

**Key Methods**:

- `authenticate()` - Initialize auth manager and client
- `send_message()` - Text message sending
- `send_photo()` - Image message sending
- `send_video()` - Video message sending
- `send_document()` - Document sending
- `edit_message()` - Message editing
- `delete_message()` - Message deletion
- `get_file_url()` - File URL retrieval
- `disconnect()` - Cleanup resources

**Bot Information Retrieval**:

```python
async def get_bot_info(self) -> Dict[str, Any]:
    """Get information about the bot."""
    def _sync_get_info():
        return self.client.get_me()

    return await asyncio.to_thread(_sync_get_info)
```

### 4. Core Platform Implementation (`agoras/core/telegram.py`)

**Pattern**: Follow `agoras/core/tiktok.py` structure exactly

**Class Initialization**:

```python
class Telegram(SocialNetwork):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Platform-specific configuration attributes
        self.telegram_bot_token = None
        self.telegram_chat_id = None
        self.telegram_parse_mode = None
        # Action-specific attributes
        self.telegram_message_id = None
        self.telegram_reply_to_message_id = None
        self.api = None
```

**Client Initialization Pattern**:

```python
async def _initialize_client(self):
    # Get configuration using existing pattern
    self.telegram_bot_token = self._get_config_value('telegram_bot_token', 'TELEGRAM_BOT_TOKEN')
    self.telegram_chat_id = self._get_config_value('telegram_chat_id', 'TELEGRAM_CHAT_ID')

    # Optional configuration
    self.telegram_parse_mode = self._get_config_value('telegram_parse_mode', 'TELEGRAM_PARSE_MODE') or 'HTML'
    self.telegram_reply_to_message_id = self._get_config_value('telegram_reply_to_message_id', 'TELEGRAM_REPLY_TO_MESSAGE_ID')

    # Validation
    if not self.telegram_bot_token:
        raise Exception('Telegram bot token is required.')

    if not self.telegram_chat_id:
        raise Exception('Telegram chat ID is required.')

    # Initialize API
    self.api = TelegramAPI(self.telegram_bot_token, self.telegram_chat_id)
    await self.api.authenticate()
```

**SocialNetwork Interface Implementation**:

**post() Method Pattern**:

```python
async def post(self, status_text, status_link,
               status_image_url_1=None, status_image_url_2=None,
               status_image_url_3=None, status_image_url_4=None):
    if not self.api:
        raise Exception('Telegram API not initialized')

    # Combine text and link
    message_text = f'{status_text}\n{status_link}'.strip() if status_link else status_text

    # Handle images
    image_urls = list(filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ]))

    if image_urls:
        # For multiple images, create a media group
        if len(image_urls) > 1:
            message_id = await self._send_media_group(image_urls, message_text)
        else:
            # Single image
            images = await self.download_images(image_urls)
            try:
                image = images[0]
                if image.content and image.file_type:
                    message_id = await self.api.send_photo(
                        chat_id=self.telegram_chat_id,
                        photo=image.content,
                        caption=message_text
                    )
                else:
                    raise Exception(f'Failed to validate image: {image.url}')
            finally:
                for image in images:
                    image.cleanup()
    else:
        # Text-only message
        message_id = await self.api.send_message(
            chat_id=self.telegram_chat_id,
            text=message_text
        )

    self._output_status(message_id)
    return message_id
```

**Telegram-Specific Methods**:

```python
async def send_poll(self, question: str, options: List[str],
                   is_anonymous: bool = True) -> str:
    """Send a poll to the chat."""
    if not self.api:
        raise Exception('Telegram API not initialized')

    message_id = await self.api.send_poll(
        chat_id=self.telegram_chat_id,
        question=question,
        options=options,
        is_anonymous=is_anonymous
    )
    self._output_status(message_id)
    return message_id

async def edit_message(self, message_id: str, new_text: str) -> str:
    """Edit a previously sent message."""
    if not self.api:
        raise Exception('Telegram API not initialized')

    await self.api.edit_message(
        chat_id=self.telegram_chat_id,
        message_id=message_id,
        text=new_text
    )
    return message_id
```

## Configuration System

**Required Configuration Variables**:

- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `TELEGRAM_CHAT_ID` - Target chat ID (user, group, or channel)

**Optional Configuration Variables**:

- `TELEGRAM_PARSE_MODE` - Message formatting (HTML, Markdown, None)
- `TELEGRAM_MESSAGE_ID` - For edit/delete actions
- `TELEGRAM_REPLY_TO_MESSAGE_ID` - For reply functionality

## CLI Integration

**Usage Examples**:

```bash
# Send text message
agoras publish --network telegram --action post \
  --status-text "Hello from agoras!" \
  --status-link "https://example.com"

# Send message with image
agoras publish --network telegram --action post \
  --status-text "Check this out!" \
  --status-image-url-1 "https://example.com/image.jpg"

# Send video
agoras publish --network telegram --action video \
  --video-url "https://example.com/video.mp4" \
  --video-title "My Video"

# Edit message
agoras publish --network telegram --action edit \
  --telegram-message-id "123" \
  --status-text "Updated message text"

# Send poll
agoras publish --network telegram --action poll \
  --telegram-poll-question "What's your favorite color?" \
  --telegram-poll-options "Red,Blue,Green,Yellow"
```

**New Actions to Support**:

- `edit` - Edit existing messages
- `poll` - Send polls to chats
- Standard actions: `post`, `video`, `delete`

## Package Updates Required

**Import Additions**:

```python
# agoras/core/api/__init__.py
from .telegram import TelegramAPI

# agoras/core/api/auth/__init__.py
from .telegram import TelegramAuthManager

# agoras/core/api/clients/__init__.py
from .telegram import TelegramAPIClient

# agoras/core/__init__.py
from .telegram import Telegram
```

## Documentation Requirements

### Credential Setup Guide (`docs/credentials/telegram.rst`)

**Content Outline**:

1. Creating a Telegram bot with @BotFather
2. Obtaining and securing the bot token
3. Finding chat IDs for users, groups, and channels
4. Setting up bot permissions and admin rights
5. Bot commands and interaction setup

### Usage Documentation (`docs/telegram.rst`)

**Content Outline**:

1. Initial bot setup and authentication
2. Sending messages to users and groups
3. Media posting (images, videos, documents)
4. Interactive features (polls, keyboards)
5. Message editing and deletion
6. RSS feed integration for automatic posting
7. Troubleshooting bot permissions and chat access

## Telegram Requirements

**Prerequisites**:

- Telegram account for creating bots
- Bot creation via @BotFather
- Target chat/channel setup with appropriate permissions

**Development vs. Production**:

- Development: Test with personal chats and private channels
- Production: Ensure proper bot permissions and rate limiting

## Implementation Phases

### Phase 1: Core Authentication (Week 1)

1. Create `TelegramAuthManager` with bot token validation
2. Implement bot information retrieval
3. Create basic `TelegramAPIClient` wrapper around python-telegram-bot
4. Test bot authentication and basic connectivity

### Phase 2: Basic Message Sending (Week 1-2)

1. Create `TelegramAPI` main integration class
2. Implement basic text message sending
3. Add Media system integration for images and videos
4. Test message sending to different chat types

### Phase 3: SocialNetwork Interface (Week 2)

1. Create `Telegram` core class extending SocialNetwork
2. Implement all required interface methods
3. Add configuration management and validation
4. Test interface compliance and media handling

### Phase 4: Platform-Specific Features (Week 2-3)

1. Implement message editing functionality
2. Add poll creation and sending
3. Add document and audio file support
4. Test advanced messaging features

### Phase 5: Integration & Documentation (Week 3)

1. Add CLI action handlers for new actions
2. Test RSS feed integration and scheduling
3. Test various chat types (private, groups, channels)
4. Write comprehensive documentation with bot setup guides

## Success Criteria

- [ ] Bot token authentication working
- [ ] Message sending to users, groups, and channels
- [ ] Media posting (images, videos, documents)
- [ ] Message editing and deletion functionality
- [ ] Poll creation and sending
- [ ] RSS feed integration for automatic posting
- [ ] Google Sheets scheduling integration
- [ ] Complete documentation with bot setup guides
- [ ] Comprehensive error handling and rate limiting

## Telegram-Specific Considerations

**Bot API Features**:

- Rich message formatting (HTML, Markdown)
- Inline keyboards and callback queries
- File uploads up to 50MB
- Message editing and deletion
- Poll creation and management
- Group and channel administration

**Rate Limiting**:

- 30 messages per second to different chats
- 1 message per second to the same chat
- Automatic retry with exponential backoff

**Chat Types**:

- Private chats (direct messages)
- Groups (up to 200,000 members)
- Channels (unlimited subscribers)
- Supergroups with advanced features

**Permissions**:

- Bot admin rights for groups/channels
- Message deletion permissions
- File sending permissions
- Poll creation permissions

## Risk Assessment

**Low Risk**:

- Mature and stable python-telegram-bot library
- Official Telegram Bot API with excellent documentation
- Active community support and regular updates
- No business verification requirements

**Considerations**:

- Bot token security (permanent tokens)
- Chat ID management for different environments
- Rate limiting compliance
- Permission management for groups/channels

```
