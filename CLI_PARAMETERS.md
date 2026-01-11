# CLI Parameters Summary by Social Network

This document provides a comprehensive summary of all CLI parameters available for each social network platform in Agoras.

## X (formerly Twitter)

### Actions

- `authorize` - Authorize X account (OAuth 1.0a)
- `post` - Create a text/image post on X
- `video` - Upload a video to X
- `like` - Like a tweet
- `share` - Retweet/share a tweet
- `delete` - Delete a tweet

### Parameters

#### authorize

- `--consumer-key` (required) - X API consumer key
- `--consumer-secret` (required) - X API consumer secret

#### post

- `--consumer-key` (required) - X API consumer key
- `--consumer-secret` (required) - X API consumer secret
- `--oauth-token` (required) - X OAuth token
- `--oauth-secret` (required) - X OAuth secret
- `--text` - Text content of the post
- `--link` - URL to include in post
- `--image-1` - Image URL #1
- `--image-2` - Image URL #2
- `--image-3` - Image URL #3
- `--image-4` - Image URL #4

#### video

- `--consumer-key` (required) - X API consumer key
- `--consumer-secret` (required) - X API consumer secret
- `--oauth-token` (required) - X OAuth token
- `--oauth-secret` (required) - X OAuth secret
- `--video-url` (required) - URL of video file to upload
- `--video-title` - Video title/description
- `--text` - Text content
- `--link` - URL to include

#### like

- `--consumer-key` (required) - X API consumer key
- `--consumer-secret` (required) - X API consumer secret
- `--oauth-token` (required) - X OAuth token
- `--oauth-secret` (required) - X OAuth secret
- `--post-id` (required) - Tweet ID to interact with

#### share

- `--consumer-key` (required) - X API consumer key
- `--consumer-secret` (required) - X API consumer secret
- `--oauth-token` (required) - X OAuth token
- `--oauth-secret` (required) - X OAuth secret
- `--post-id` (required) - Tweet ID to interact with

#### delete

- `--consumer-key` (required) - X API consumer key
- `--consumer-secret` (required) - X API consumer secret
- `--oauth-token` (required) - X OAuth token
- `--oauth-secret` (required) - X OAuth secret
- `--post-id` (required) - Tweet ID to interact with

---

## Facebook

### Actions

- `authorize` - Authorize Facebook account (OAuth 2.0)
- `post` - Create a text/image post on Facebook
- `video` - Upload a video to Facebook
- `like` - Like a Facebook post
- `share` - Share a Facebook post
- `delete` - Delete a Facebook post

### Parameters

#### authorize

- `--client-id` (required) - Facebook App client ID
- `--client-secret` (required) - Facebook App client secret
- `--app-id` (required) - Facebook App ID
- `--object-id` (required) - Facebook user ID for authentication

#### post

- `--object-id` (required) - Facebook page or profile ID where post will be published
- `--text` - Text content of the post
- `--link` - URL to include in post
- `--image-1` - Image URL #1
- `--image-2` - Image URL #2
- `--image-3` - Image URL #3
- `--image-4` - Image URL #4

#### video

- `--object-id` (required) - Facebook page or profile ID where post will be published
- `--video-url` (required) - URL of video file to upload
- `--video-title` - Video title
- `--video-description` - Video description
- `--video-type` - Video type
- `--text` - Text content
- `--link` - URL to include

#### like

- `--post-id` (required) - Facebook post ID to interact with

#### share

- `--post-id` (required) - Facebook post ID to interact with
- `--profile-id` - Facebook profile ID where post will be shared

#### delete

- `--post-id` (required) - Facebook post ID to interact with

---

## Instagram

### Actions

- `authorize` - Authorize Instagram account (OAuth 2.0)
- `post` - Create a photo post on Instagram
- `video` - Upload a video to Instagram

### Parameters

#### authorize

- `--client-id` (required) - Facebook App client ID
- `--client-secret` (required) - Facebook App client secret
- `--object-id` (required) - Facebook user ID (for Instagram business account)

#### post

- `--object-id` (required) - Instagram business account ID
- `--text` - Text content of the post
- `--link` - URL to include in post
- `--image-1` - Image URL #1

#### video

- `--object-id` (required) - Instagram business account ID
- `--video-url` (required) - URL of video file to upload
- `--video-caption` - Video caption
- `--video-type` - Video type (e.g., REELS, STORIES)

---

## LinkedIn

### Actions

- `authorize` - Authorize LinkedIn account (OAuth 2.0)
- `post` - Create a post on LinkedIn
- `video` - Upload a video to LinkedIn
- `like` - Like a LinkedIn post
- `share` - Share a LinkedIn post
- `delete` - Delete a LinkedIn post

### Parameters

#### authorize

- `--client-id` (required) - LinkedIn App client ID
- `--client-secret` (required) - LinkedIn App client secret
- `--object-id` (required) - LinkedIn user/organization ID

#### post

- `--text` - Text content of the post
- `--link` - URL to include in post
- `--image-1` - Image URL #1

#### video

- `--video-url` (required) - URL of video file to upload
- `--video-title` - Video title

#### like

- `--post-id` (required) - LinkedIn post ID to interact with

#### share

- `--post-id` (required) - LinkedIn post ID to interact with

#### delete

- `--post-id` (required) - LinkedIn post ID to interact with

---

## Discord

### Actions

- `authorize` - Set up Discord bot token
- `post` - Send a message to Discord channel
- `video` - Send a video to Discord channel
- `delete` - Delete a Discord message

### Parameters

#### authorize

- `--bot-token` (required) - Discord bot token
- `--server-name` (required) - Discord server (guild) name
- `--channel-name` (required) - Discord channel name

#### post

- `--bot-token` (required) - Discord bot token
- `--server-name` (required) - Discord server (guild) name
- `--channel-name` (required) - Discord channel name
- `--text` - Text content of the message
- `--link` - URL to include in message
- `--image-1` - Image URL #1
- `--image-2` - Image URL #2
- `--image-3` - Image URL #3
- `--image-4` - Image URL #4

#### video

- `--bot-token` (required) - Discord bot token
- `--server-name` (required) - Discord server (guild) name
- `--channel-name` (required) - Discord channel name
- `--video-url` (required) - URL of video file to send
- `--video-title` - Video title/description

#### delete

- `--bot-token` (required) - Discord bot token
- `--server-name` (required) - Discord server (guild) name
- `--channel-name` (required) - Discord channel name
- `--post-id` (required) - Discord message ID to delete

---

## YouTube

### Actions

- `authorize` - Authorize YouTube account (OAuth 2.0)
- `video` - Upload a video to YouTube
- `like` - Like a YouTube video
- `delete` - Delete a YouTube video

### Parameters

#### authorize

- `--client-id` (required) - YouTube (Google) OAuth client ID
- `--client-secret` (required) - YouTube (Google) OAuth client secret

#### video

- `--video-url` (required) - URL of video file to upload
- `--title` - Video title
- `--description` - Video description
- `--category-id` - YouTube category ID
- `--privacy` - Video privacy status (default: private) - Choices: public, private, unlisted
- `--keywords` - Video keywords separated by comma

#### like

- `--video-id` (required) - YouTube video ID to interact with

#### delete

- `--video-id` (required) - YouTube video ID to interact with

---

## TikTok

### Actions

- `authorize` - Authorize TikTok account (OAuth 2.0)
- `video` - Upload a video to TikTok

### Parameters

#### authorize

- `--client-key` (required) - TikTok App client key
- `--client-secret` (required) - TikTok App client secret
- `--username` (required) - TikTok username for authentication

#### video

- `--video-url` (required) - URL of video file to upload
- `--title` - Video title/caption
- `--privacy` - Video privacy status (default: SELF_ONLY) - Choices: PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, FOLLOWER_OF_CREATOR, SELF_ONLY

---

## Threads

### Actions

- `authorize` - Authorize Threads account (OAuth 2.0)
- `post` - Create a post on Threads
- `video` - Upload a video to Threads
- `share` - Share/repost a Threads post

### Parameters

#### authorize

- `--app-id` (required) - Threads (Meta) App ID
- `--app-secret` (required) - Threads (Meta) App secret
- `--redirect-uri` (required) - OAuth redirect URI (e.g., <http://localhost:3456/callback>)

#### post

- `--text` - Text content of the post
- `--link` - URL to include in post
- `--image-1` - Image URL #1
- `--image-2` - Image URL #2
- `--image-3` - Image URL #3
- `--image-4` - Image URL #4

#### video

- `--video-url` (required) - URL of video file to upload
- `--video-title` - Video caption/description

#### share

- `--post-id` (required) - Threads post ID to share

---

## Telegram

### Actions

- `authorize` - Set up Telegram bot token
- `post` - Send a message to Telegram chat
- `video` - Send a video to Telegram chat
- `edit` - Edit an existing Telegram message
- `poll` - Send a poll to Telegram chat
- `document` - Send a document file to Telegram chat
- `audio` - Send an audio file to Telegram chat
- `delete` - Delete a Telegram message

### Parameters

#### authorize

- `--bot-token` (required) - Telegram bot token from @BotFather
- `--chat-id` (required) - Target chat ID (user, group, or channel)
- `--parse-mode` - Message parse mode (default: HTML) - Choices: HTML, Markdown, MarkdownV2, None

#### post

- `--bot-token` (required) - Telegram bot token from @BotFather
- `--chat-id` (required) - Target chat ID (user, group, or channel)
- `--parse-mode` - Message parse mode (default: HTML)
- `--text` - Text content of the message
- `--link` - URL to include in message
- `--image-1` - Image URL #1
- `--image-2` - Image URL #2
- `--image-3` - Image URL #3
- `--image-4` - Image URL #4

#### video

- `--bot-token` (required) - Telegram bot token from @BotFather
- `--chat-id` (required) - Target chat ID (user, group, or channel)
- `--parse-mode` - Message parse mode (default: HTML)
- `--video-url` (required) - URL of video file to upload
- `--video-title` - Video title/description

#### edit

- `--bot-token` (required) - Telegram bot token from @BotFather
- `--chat-id` (required) - Target chat ID (user, group, or channel)
- `--parse-mode` - Message parse mode (default: HTML)
- `--message-id` (required) - ID of the message to edit
- `--text` (required) - New message text

#### poll

- `--bot-token` (required) - Telegram bot token from @BotFather
- `--chat-id` (required) - Target chat ID (user, group, or channel)
- `--parse-mode` - Message parse mode (default: HTML)
- `--question` (required) - Poll question (up to 300 characters)
- `--options` (required) - Comma-separated list of poll options (2-10 options)
- `--anonymous` - Make poll anonymous (default: True)

#### document

- `--bot-token` (required) - Telegram bot token from @BotFather
- `--chat-id` (required) - Target chat ID (user, group, or channel)
- `--parse-mode` - Message parse mode (default: HTML)
- `--document-url` (required) - URL of document file to send
- `--caption` - Document caption

#### audio

- `--bot-token` (required) - Telegram bot token from @BotFather
- `--chat-id` (required) - Target chat ID (user, group, or channel)
- `--parse-mode` - Message parse mode (default: HTML)
- `--audio-url` (required) - URL of audio file to send
- `--caption` - Audio caption
- `--duration` - Audio duration in seconds
- `--performer` - Performer name
- `--title` - Track title

#### delete

- `--bot-token` (required) - Telegram bot token from @BotFather
- `--chat-id` (required) - Target chat ID (user, group, or channel)
- `--parse-mode` - Message parse mode (default: HTML)
- `--post-id` (required) - Telegram message ID to delete

---

## WhatsApp

### Actions

- `post` - Send a text/image message via WhatsApp
- `video` - Send a video message via WhatsApp
- `contact` - Send a contact card via WhatsApp
- `location` - Send a location message via WhatsApp
- `document` - Send a document file via WhatsApp
- `audio` - Send an audio file via WhatsApp
- `template` - Send a template message via WhatsApp

### Parameters

#### post

- `--access-token` (required) - Meta Graph API access token
- `--phone-number-id` (required) - WhatsApp Business phone number ID
- `--business-account-id` - WhatsApp Business Account ID (optional)
- `--recipient` (required) - Target recipient phone number (E.164 format, e.g., +1234567890)
- `--text` - Text content of the message
- `--link` - URL to include in message
- `--image-1` - Image URL #1
- `--image-2` - Image URL #2
- `--image-3` - Image URL #3
- `--image-4` - Image URL #4

#### video

- `--access-token` (required) - Meta Graph API access token
- `--phone-number-id` (required) - WhatsApp Business phone number ID
- `--business-account-id` - WhatsApp Business Account ID (optional)
- `--recipient` (required) - Target recipient phone number (E.164 format)
- `--video-url` (required) - URL of video file to upload
- `--video-title` - Video title/description

#### contact

- `--access-token` (required) - Meta Graph API access token
- `--phone-number-id` (required) - WhatsApp Business phone number ID
- `--business-account-id` - WhatsApp Business Account ID (optional)
- `--recipient` (required) - Target recipient phone number (E.164 format)
- `--contact-name` (required) - Name of the contact to send
- `--contact-phone` (required) - Phone number of the contact (E.164 format)

#### location

- `--access-token` (required) - Meta Graph API access token
- `--phone-number-id` (required) - WhatsApp Business phone number ID
- `--business-account-id` - WhatsApp Business Account ID (optional)
- `--recipient` (required) - Target recipient phone number (E.164 format)
- `--latitude` (required) - Latitude coordinate (-90 to 90)
- `--longitude` (required) - Longitude coordinate (-180 to 180)
- `--location-name` - Location name (optional)

#### document

- `--access-token` (required) - Meta Graph API access token
- `--phone-number-id` (required) - WhatsApp Business phone number ID
- `--business-account-id` - WhatsApp Business Account ID (optional)
- `--recipient` (required) - Target recipient phone number (E.164 format)
- `--document-url` (required) - Publicly accessible HTTPS URL of the document
- `--caption` - Document caption (optional)
- `--filename` - Document filename (optional)

#### audio

- `--access-token` (required) - Meta Graph API access token
- `--phone-number-id` (required) - WhatsApp Business phone number ID
- `--business-account-id` - WhatsApp Business Account ID (optional)
- `--recipient` (required) - Target recipient phone number (E.164 format)
- `--audio-url` (required) - Publicly accessible HTTPS URL of the audio file

#### template

- `--access-token` (required) - Meta Graph API access token
- `--phone-number-id` (required) - WhatsApp Business phone number ID
- `--business-account-id` - WhatsApp Business Account ID (optional)
- `--recipient` (required) - Target recipient phone number (E.164 format)
- `--template-name` (required) - Name of the pre-approved template
- `--language-code` - Language code (ISO 639-1 format, default: en)
- `--template-components` - Template components as JSON string (optional)

---

## Common Parameters

### Content Options (available for most post actions)

- `--text` - Text content of the post/message
- `--link` - URL to include in post/message
- `--image-1` through `--image-4` - Image URLs (number of images supported varies by platform)

### Video Options (available for video actions)

- `--video-url` (required) - URL of video file to upload
- `--video-title` / `--title` - Video title/description/caption (varies by platform)

### Feed Options (if supported)

- `--feed-url` (required) - URL of RSS/Atom feed
- `--max-count` - Maximum posts to publish at once
- `--post-lookback` - Only posts within last N seconds
- `--max-post-age` - Maximum post age in days
