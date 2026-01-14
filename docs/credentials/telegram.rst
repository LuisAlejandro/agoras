Telegram credentials
====================

Agoras needs the following information from Telegram to be able to access its API:

- Bot Token
- Chat ID (user, group, or channel)

For that, we'll need to create a Telegram bot using @BotFather and obtain the bot token. We'll also need to find the chat ID for the target chat (user, group, or channel).

**Important**: Telegram bots require appropriate permissions to function. Make sure your bot has the necessary permissions for the actions you want to perform (send messages, send media, delete messages, send polls).

---

You can create a Telegram bot by talking to @BotFather on Telegram.

Create a Telegram bot
---------------------

1. Open Telegram and search for **@BotFather**
2. Start a conversation with @BotFather
3. Send the command ``/newbot``
4. Follow the prompts:
   - Enter a name for your bot (e.g., "My Agoras Bot")
   - Enter a username for your bot (must end with "bot", e.g., "my_agoras_bot")
5. @BotFather will reply with your bot token

**Example conversation**:

::

    You: /newbot
    BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.
    You: My Agoras Bot
    BotFather: Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
    You: my_agoras_bot
    BotFather: Done! Congratulations on your new bot. You will find it at t.me/my_agoras_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands.

    Use this token to access the HTTP API:
    123456789:ABCdefGHIjklMNOpqrsTUVwxyz

    For a description of the Bot API, see this page: https://core.telegram.org/bots/api

Get your bot token
------------------

The bot token is provided by @BotFather when you create your bot. It looks like this:

::

    123456789:ABCdefGHIjklMNOpqrsTUVwxyz

**Important**:
- **Copy and save this token securely** - you'll need it for Agoras
- **Never share this token publicly** - treat it like a password
- **If your token is ever compromised**, use @BotFather's ``/revoke`` command to regenerate it

**Security best practices**:
- Store the token in environment variables, not in code
- Use a secrets manager for production deployments
- Never commit tokens to version control
- Regenerate tokens periodically for security

Configure bot settings
----------------------

You can configure your bot using @BotFather commands:

- ``/setdescription`` - Set bot description
- ``/setabouttext`` - Set about text
- ``/setuserpic`` - Set bot profile picture
- ``/setcommands`` - Set bot commands menu
- ``/setname`` - Change bot name
- ``/setdescription`` - Change bot description

**Note**: These settings are optional but recommended for a better user experience.

Find your Chat ID
-----------------

The chat ID is a unique identifier for the chat where you want to send messages. The method to find it depends on the chat type.

For Private Chats (Direct Messages)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Method 1: Using @userinfobot**

1. Start a conversation with **@userinfobot**
2. Send any message to the bot
3. The bot will reply with your user ID
4. Use this ID as ``--chat-id``

**Method 2: Using @getidsbot**

1. Start a conversation with **@getidsbot**
2. Forward any message from the chat you want to use
3. The bot will reply with the chat ID
4. Use this ID as ``--chat-id``

**Note**: For private chats, the chat ID is the same as your user ID (a positive number).

For Groups
~~~~~~~~~~

**Method 1: Using @getidsbot**

1. Add **@getidsbot** to your group
2. Send any message in the group
3. The bot will reply with the group ID
4. Use this ID as ``--chat-id``

**Method 2: Using Telegram Web/Desktop**

1. Open your group in Telegram Web (web.telegram.org)
2. Look at the URL - it will contain the group ID
3. Group IDs are negative numbers (e.g., ``-1001234567890``)

**Note**:
- Group IDs are negative numbers
- Supergroups have IDs starting with ``-100``
- Regular groups have IDs starting with ``-``

For Channels
~~~~~~~~~~~~

**Method 1: Using @getidsbot**

1. Add **@getidsbot** to your channel as an administrator
2. Post any message in the channel
3. The bot will reply with the channel ID
4. Use this ID as ``--chat-id``

**Method 2: Using Telegram Web/Desktop**

1. Open your channel in Telegram Web (web.telegram.org)
2. Look at the URL - it will contain the channel ID
3. Channel IDs are negative numbers starting with ``-100`` (e.g., ``-1001234567890``)

**Note**:
- Channel IDs are negative numbers starting with ``-100``
- The bot must be added to the channel as an administrator
- The bot must have permission to post messages

Set up bot permissions
-----------------------

For your bot to function properly, it needs appropriate permissions in groups and channels.

**For Groups**:

1. Add your bot to the group
2. Make the bot an administrator (optional but recommended)
3. Grant the following permissions:
   - ✅ **Send Messages** - Required for all posting actions
   - ✅ **Send Media** - Required for photos, videos, documents, audio
   - ✅ **Delete Messages** - Required for delete action
   - ✅ **Send Polls** - Required for poll action

**For Channels**:

1. Add your bot to the channel as an administrator
2. Grant the following permissions:
   - ✅ **Post Messages** - Required for all posting actions
   - ✅ **Edit Messages** - Required for edit action
   - ✅ **Delete Messages** - Required for delete action

**Note**: For private chats, no special permissions are needed - the bot can send messages directly.

Bot Commands (Optional)
-----------------------

You can set up bot commands using @BotFather:

1. Send ``/setcommands`` to @BotFather
2. Select your bot
3. Send a list of commands in this format:

::

    start - Start the bot
    help - Get help
    status - Check bot status

**Note**: Bot commands are optional and not required for Agoras functionality.

Test your bot
------------

You can test if your bot is properly configured:

1. Make sure you have your bot token from @BotFather
2. Find your chat ID using @userinfobot or @getidsbot
3. First, authorize your bot credentials:

   ::

         agoras telegram authorize \
               --bot-token "your_bot_token_here" \
               --chat-id "your_chat_id_here"

4. Then try a simple post command (credentials are now stored):

   ::

         agoras telegram post \
               --text "Hello, Telegram!"

5. Check if the message appears in your Telegram chat

CI/CD Setup
-----------

For CI/CD environments where you need to use Telegram credentials:

1. Set environment variables in your CI/CD pipeline::

      export TELEGRAM_BOT_TOKEN="your_bot_token_here"
      export TELEGRAM_CHAT_ID="your_chat_id_here"

2. Agoras will automatically use these environment variables when credentials are not provided via command-line parameters.

3. You can also authorize once locally and the credentials will be stored securely in ``~/.agoras/tokens/``, which can be used in CI/CD if the token storage is accessible.

**Security Best Practices for CI/CD**:
- Store credentials in your CI/CD platform's secret management system (GitHub Secrets, GitLab CI/CD Variables, etc.)
- Never commit tokens to version control
- Use different bot tokens for different environments (dev, staging, production)
- Rotate tokens periodically using @BotFather's ``/revoke`` command
- Limit bot permissions to only what's required

Security Best Practices
-----------------------

**Token Security**:

- Store tokens in environment variables:

  ::

      export TELEGRAM_BOT_TOKEN="your_token_here"

- Use secrets managers for production (AWS Secrets Manager, HashiCorp Vault, etc.)
- Never commit tokens to version control
- Use different tokens for development and production
- Rotate tokens periodically

**Chat ID Management**:

- Store chat IDs in environment variables or configuration files
- Use different chat IDs for different environments (dev, staging, production)
- Document which chat IDs correspond to which chats
- Keep a backup of important chat IDs

**Access Control**:

- Only add the bot to groups/channels where it's needed
- Limit bot permissions to only what's required
- Regularly review bot access and permissions
- Remove bot access from unused chats

**Rate Limiting**:

- Be aware of Telegram's rate limits:
  - 30 messages per second to different chats
  - 1 message per second to the same chat
- Agoras handles rate limiting automatically
- Avoid sending too many messages in a short time

Agoras parameters
-----------------

+------------------------+---------------------------+--------------------------------+
| Telegram credential    | Agoras parameter          | Required for                   |
+========================+===========================+================================+
| Bot Token              | --bot-token               | authorize (required)           |
|                        |                           | post/video/delete (optional)   |
+------------------------+---------------------------+--------------------------------+
| Chat ID                | --chat-id                 | authorize (required)           |
|                        |                           | post/video/delete (optional)   |
+------------------------+---------------------------+--------------------------------+
| Message ID             | --post-id                 | delete/edit actions only       |
+------------------------+---------------------------+--------------------------------+

**Important**: Run ``agoras telegram authorize`` first to store your credentials securely. After authorization, you can use post, video, delete, and other actions without providing credentials each time.

**Note**: Message ID is only needed for delete and edit actions. Parse mode and other optional parameters are still accepted but not stored.

Troubleshooting
---------------

**Bot token not working**:

- Verify the token is correct (no extra spaces or characters)
- Check if the token was revoked using @BotFather's ``/revoke`` command
- Generate a new token if needed

**Chat ID not working**:

- Verify the chat ID is correct (negative for groups/channels, positive for users)
- Ensure the bot is added to the group/channel
- Check that the bot has permission to send messages
- Try using @getidsbot to verify the chat ID

**Bot can't send messages**:

- Check bot permissions in the group/channel
- Verify the bot is an administrator (for channels)
- Ensure the bot hasn't been blocked or removed
- Check rate limiting (may need to wait between messages)

**Bot can't delete messages**:

- Verify the bot has "Delete Messages" permission
- Check that the message ID is correct
- Ensure the message is in the specified chat
- Verify the bot sent the message (bots can only delete their own messages in some cases)

Additional Resources
--------------------

- `Telegram Bot API Documentation <https://core.telegram.org/bots/api>`_
- `python-telegram-bot Documentation <https://python-telegram-bot.org/>`_
- `@BotFather <https://t.me/botfather>`_ - Official bot for creating Telegram bots
- `@userinfobot <https://t.me/userinfobot>`_ - Get your user ID
- `@getidsbot <https://t.me/getidsbot>`_ - Get chat and message IDs
