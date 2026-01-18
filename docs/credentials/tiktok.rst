TikTok credentials
==================

Agoras needs the following credentials from TikTok to be able to access its API:

- Client Key (App ID)
- Client Secret
- TikTok Username

For that, we'll need to create a TikTok for Developers app and get it approved for production use.

**Important**: TikTok requires app review and approval before you can use the API in production. The approval process can take several weeks. Additionally, TikTok's API does not support like, share, or delete actions.

---

You can create a TikTok for Developers app at https://developers.tiktok.com/.

.. image:: images/tiktok-1.png

If you haven't yet, you will need to apply for a TikTok for Developers account and create an application.

Apply for a TikTok for Developers account
-----------------------------------------

1. Go to https://developers.tiktok.com/ and click "Get Started"
2. Sign in with your TikTok account (the same account you want to post to)
3. Complete the developer registration form:

   - **Account Type**: Select "Individual" unless you're representing a company
   - **Use Case**: Select "Content Publishing" or "Marketing"
   - **Contact Information**: Provide accurate contact details
   - **Company Information**: Fill this if you selected "Company" as account type

.. image:: images/tiktok-2.png

Create an app
-------------

After your developer account is approved:

1. Go to your TikTok for Developers dashboard
2. Click "Create an app" or "Add app"
3. Fill out the application form:

   - **App Name**: Choose a descriptive name like "My-App-Agoras"
   - **App Description**: Describe your use case for content publishing
   - **Category**: Select "Productivity" or "Social Media"
   - **Platform**: Select "Web"

.. image:: images/tiktok-3.png

Configure app permissions
------------------------

After creating your app:

1. Go to your app's dashboard
2. Navigate to "Products" or "Add Products"
3. Add the following products to your app:

   - **Login Kit**: For user authentication
   - **Content Posting API**: For publishing videos and photos

4. Configure the required scopes:

   - ``user.info.basic``: To get user profile information
   - ``video.upload``: To upload video content
   - ``video.publish``: To publish video content

.. image:: images/tiktok-4.png

Set up OAuth redirect URI
-------------------------

1. In your app dashboard, go to "Login Kit" settings
2. Add a redirect URI: ``http://127.0.0.1:3456/callback/``
3. Make sure this exact URL is added to your app configuration

.. image:: images/tiktok-5.png

Submit for app review
---------------------

**Important**: TikTok requires app review for production use.

1. Complete all required app information
2. Provide detailed use case description
3. Submit privacy policy and terms of service URLs (if required)
4. Submit your app for review

The review process typically takes 2-4 weeks. During this time, you can use your app in development mode with limited functionality.

.. image:: images/tiktok-6.png

Get your credentials
-------------------

Once your app is created (and optionally approved):

1. Go to your app dashboard
2. Navigate to "Basic Information" or "App Details"
3. Copy the following credentials:

   - **Client Key**: Your app's unique identifier
   - **Client Secret**: Your app's secret key (keep this secure!)

.. image:: images/tiktok-7.png

Get your TikTok username
------------------------

You'll also need your TikTok username (the handle you want to post to):

1. Go to your TikTok profile
2. Your username is displayed as @username
3. Use just the username part (without the @)

For example, if your profile shows @myawesomehandle, use ``myawesomehandle``

Authorize Agoras
----------------

.. versionchanged:: 2.0
   TikTok now uses OAuth 2.0 "authorize first" workflow.

Before you can post content, you need to authorize Agoras to access your TikTok account::

    agoras tiktok authorize \
      --client-key "${TIKTOK_CLIENT_KEY}" \
      --client-secret "${TIKTOK_CLIENT_SECRET}" \
      --username "${TIKTOK_USERNAME}"

This will:

1. Open your browser to TikTok's OAuth authorization page
2. Prompt you to log in to TikTok and approve the app permissions
3. Automatically capture the authorization code
4. Store encrypted credentials in ``~/.agoras/tokens/``

This is a one-time process. The refresh token will be stored securely and used for subsequent requests. Credentials are automatically refreshed when needed.

CI/CD Setup (Unattended Execution)
-----------------------------------

For CI/CD environments where interactive browser authorization isn't possible, you can skip the ``authorize`` step entirely and provide all required credentials via environment variables.

1. Run ``agoras tiktok authorize`` locally first to generate a refresh token (one-time setup)
2. Extract the refresh token using the tokens utility command::

      # First, list tokens to find the identifier (if you don't know it)
      agoras utils tokens list --platform tiktok

      # Then view all stored credentials
      agoras utils tokens show --platform tiktok --identifier {identifier}

3. Set all required environment variables in your CI/CD pipeline::

      export TIKTOK_USERNAME="your_username"
      export TIKTOK_CLIENT_KEY="your_client_key"
      export TIKTOK_CLIENT_SECRET="your_client_secret"
      export TIKTOK_REFRESH_TOKEN="your_refresh_token_here"

4. Run Agoras actions directly without running ``authorize``. All credentials will be loaded from environment variables.

**Note**: For unattended execution, you must provide all required credentials. The refresh token alone is not sufficient - you also need username, client key, and client secret as shown in the :doc:`../reference/platform-arguments-envvars` documentation.

Development vs Production
------------------------

**Development Mode**:
- Available immediately after app creation
- Limited to your own account
- May have posting restrictions
- Good for testing integration

**Production Mode**:
- Requires app review and approval
- Can post to any authorized account
- Full API functionality
- Required for live usage

Agoras parameters
-----------------

+------------------------+---------------------------+
| TikTok credential      | Agoras parameter          |
+========================+===========================+
| Client Key             | --client-key              |
+------------------------+---------------------------+
| Client Secret          | --client-secret            |
+------------------------+---------------------------+
| Username               | --username                |
+------------------------+---------------------------+

**Note**: After authorization, refresh tokens are managed automatically by Agoras. You no longer need to provide tokens for actions.

Troubleshooting
---------------

**"App not approved" error**:
- Make sure your app has been submitted for review
- Check if you're trying to use production features in development mode
- Verify all required app information is complete

**"Invalid credentials" error**:
- Double-check your Client Key and Client Secret
- Make sure you're using the correct TikTok username
- Verify your app's redirect URI is set to ``http://127.0.0.1:3456/callback/``

**"Authorization failed" error**:
- Make sure you're logged into the correct TikTok account
- Check that your app has the required scopes enabled
- Try the authorization process again

**"Video upload failed" error**:
- Verify your video format is supported (MP4, MOV, WebM)
- Check that your video duration doesn't exceed account limits
- Make sure your video file is accessible from the provided URL

For more help, consult the `TikTok for Developers documentation <https://developers.tiktok.com/doc/>`_.
