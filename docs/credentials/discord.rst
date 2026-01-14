Discord credentials
===================

Agoras needs the following information from Discord to be able to access its API:

- Bot Token
- Discord Server Name
- Discord Channel Name

For that, we'll need to create a Discord application, set up a bot, and invite it to your server with appropriate permissions.

**Important**: Discord bots require specific permissions to function. Make sure your bot has the necessary permissions for the actions you want to perform (send messages, embed links, attach files, add reactions, manage messages).

---

You can create a Discord application at https://discord.com/developers/applications.

.. image:: images/discord-1.png

Create a Discord application
---------------------------

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Enter an application name (e.g., "My-Bot-Agoras")
4. Accept Discord's Terms of Service and Developer Policy
5. Click "Create"

.. image:: images/discord-2.png

Create a bot user
----------------

After creating your application:

1. Navigate to the "Bot" section in the left sidebar
2. Click "Add Bot" or "Create Bot User"
3. Confirm by clicking "Yes, do it!"
4. Your bot is now created

.. image:: images/discord-3.png

Configure bot settings
---------------------

Configure your bot's basic settings:

1. **Username**: Set a recognizable name for your bot
2. **Avatar**: Upload an avatar image (optional)
3. **Public Bot**: Disable this if you only want to use the bot on your own servers
4. **Require OAuth2 Code Grant**: Keep this disabled for Agoras usage
5. **Presence Intent**: Enable if you need presence information
6. **Server Members Intent**: Enable if you need member information
7. **Message Content Intent**: **Enable this** - required for message processing

.. image:: images/discord-4.png

**Important**: Make sure to enable "Message Content Intent" as it's required for bots to read message content.

Get your bot token
-----------------

1. In the "Bot" section, find the "Token" area
2. Click "Reset Token" or "Copy" if the token is already visible
3. **Copy and save this token securely** - you'll need it for Agoras
4. **Never share this token publicly** - treat it like a password

.. image:: images/discord-5.png

**Security note**: If your token is ever compromised, return to this page and regenerate it immediately.

Set up bot permissions
---------------------

Configure the permissions your bot will need:

1. Go to the "OAuth2" section in the left sidebar
2. Select "URL Generator"
3. In "Scopes", check **"bot"**
4. In "Bot Permissions", select the permissions you need:

**Required permissions for Agoras**:
- ✅ **Send Messages** - To post content
- ✅ **Embed Links** - To create rich embeds
- ✅ **Attach Files** - To upload videos and images
- ✅ **Read Message History** - To access existing messages
- ✅ **Add Reactions** - To like messages (for like action)
- ✅ **Manage Messages** - To delete messages (for delete action)

**Optional but recommended**:
- ✅ **Use External Emojis** - For custom emoji reactions
- ✅ **Mention Everyone** - If you need to mention @everyone or @here

.. image:: images/discord-6.png

Invite bot to your server
------------------------

1. Copy the generated OAuth2 URL from the URL Generator
2. Open the URL in your browser
3. Select the Discord server where you want to add the bot
4. Verify the permissions are correct
5. Click "Authorize"
6. Complete any required captcha verification

.. image:: images/discord-7.png

**Note**: You must have "Manage Server" permission on the Discord server to invite bots.

Get server and channel information
---------------------------------

**Server Name**:
1. Open Discord and navigate to your server
2. The server name is displayed at the top-left of the Discord interface
3. Use this exact name (case-sensitive) for ``--discord-server-name``

**Channel Name**:
1. Navigate to the text channel where you want the bot to post
2. The channel name is displayed without the # symbol
3. Use this exact name (case-sensitive) for ``--discord-channel-name``

For example:
- If you see "My Awesome Server" at the top, use ``My Awesome Server``
- If you see "#general" in the channel list, use ``general``

.. image:: images/discord-8.png

Test your bot
------------

You can test if your bot is properly configured:

1. Make sure the bot is online (green status) in your server member list
2. First, authorize your bot credentials:

   ::

         agoras discord authorize \
               --bot-token "your_bot_token_here" \
               --server-name "Your Server Name" \
               --channel-name "general"

3. Then try a simple post command (credentials are now stored):

   ::

         agoras discord post \
               --text "Hello, Discord!"

4. Check if the message appears in your Discord channel

Enable Developer Mode (for message IDs)
---------------------------------------

To get message IDs for like and delete actions:

1. Open Discord user settings (gear icon)
2. Go to "Advanced" in the left sidebar
3. Enable "Developer Mode"
4. Now you can right-click any message and select "Copy Message ID"

.. image:: images/discord-9.png

CI/CD Setup
-----------

For CI/CD environments where you need to use Discord credentials:

1. Set environment variables in your CI/CD pipeline::

      export DISCORD_BOT_TOKEN="your_bot_token_here"
      export DISCORD_SERVER_NAME="Your Server Name"
      export DISCORD_CHANNEL_NAME="general"

2. Agoras will automatically use these environment variables when credentials are not provided via command-line parameters.

3. You can also authorize once locally and the credentials will be stored securely in ``~/.agoras/tokens/``, which can be used in CI/CD if the token storage is accessible.

**Security Best Practices for CI/CD**:
- Store credentials in your CI/CD platform's secret management system (GitHub Secrets, GitLab CI/CD Variables, etc.)
- Never commit tokens to version control
- Use different bot tokens for different environments (dev, staging, production)
- Rotate tokens periodically
- Limit bot permissions to only what's required

Agoras parameters
-----------------

+------------------------+---------------------------+--------------------------------+
| Discord credential     | Agoras parameter          | Required for                   |
+========================+===========================+================================+
| Bot Token              | --bot-token               | authorize (required)           |
|                        |                           | post/video/delete (optional)   |
+------------------------+---------------------------+--------------------------------+
| Server Name            | --server-name             | authorize (required)           |
|                        |                           | post/video/delete (optional)   |
+------------------------+---------------------------+--------------------------------+
| Channel Name           | --channel-name           | authorize (required)           |
|                        |                           | post/video/delete (optional)   |
+------------------------+---------------------------+--------------------------------+
| Message ID             | --post-id                 | delete action only             |
+------------------------+---------------------------+--------------------------------+

**Important**: Run ``agoras discord authorize`` first to store your credentials securely. After authorization, you can use post, video, and delete actions without providing credentials each time.

**Note**: Message ID is only needed for delete actions. You can get message IDs by enabling Developer Mode in Discord settings.

Troubleshooting
---------------

**"Bot is not in the server" error**:
- Make sure you've invited the bot to your server using the OAuth2 URL
- Check that the bot appears in the server member list
- Verify the server name matches exactly (case-sensitive)

**"Missing permissions" error**:
- Check that your bot has the required permissions in the server
- Make sure the bot can see and send messages in the target channel
- Verify channel permissions aren't overriding server permissions

**"Channel not found" error**:
- Double-check the channel name is correct (without # symbol)
- Ensure the bot has permission to view the channel
- Verify the channel exists in the specified server

**"Invalid token" error**:
- Check that you've copied the bot token correctly
- Make sure you're using the bot token, not a user token
- Regenerate the token if it might be compromised

**"Message Content Intent" error**:
- Go to your bot settings and enable "Message Content Intent"
- This is required for Discord bots to process message content

**File upload fails**:
- Check that the file URL is publicly accessible
- Verify the file format is supported
- Ensure the file size doesn't exceed Discord's limits (8MB/50MB)

For more help, consult the `Discord Developer Documentation <https://discord.com/developers/docs>`_.
