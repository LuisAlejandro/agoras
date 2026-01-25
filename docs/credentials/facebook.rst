Facebook credentials
====================

.. versionchanged:: 2.0
   Facebook now uses OAuth 2.0 authentication. You no longer need to manually generate access tokens.

Agoras needs the following OAuth app credentials from Facebook to access its API:

- Client ID (App ID)
- Client Secret (App Secret)
- App ID
- Object ID (User/Page ID)

Create a Facebook App
---------------------

.. _My Apps: https://developers.facebook.com/apps/

**If you already have a Facebook App**, skip to "Get App Credentials".

.. image:: images/facebook-1.png

1. Go to `My Apps`_.
2. Click "Create App".
3. Select app type (choose "Business" or "Other").
4. Fill in the app name and contact email.

.. image:: images/facebook-2.png

.. image:: images/facebook-3.png

Get App Credentials
------------------

1. In your Facebook App dashboard, go to **Settings** > **Basic**.
2. Note your **App ID** (this is your ``--app-id``).
3. Note your **App Secret** (click "Show" to reveal it - this is your ``--client-secret``).
4. The **App ID** is also your **Client ID** (this is your ``--client-id``).

Get Object ID (User/Page ID)
----------------------------

You need the ID of the Facebook page or profile you want to post to. To find your Page ID:

1. Go to your Facebook page.
2. Note the page name from the URL (e.g., ``LuisDevelops`` from ``https://www.facebook.com/LuisDevelops``).
3. Use the Graph API Explorer to get the ID (replace ``{page_name}`` with the page name)::

      https://developers.facebook.com/tools/explorer/?method=GET&path={page_name}

4. Click "Submit" and you'll see a response like::

      {
            "name": "Luis Develops",
            "id": "ZZZZZZZ"
      }

The ``id`` field is your ``--object-id``.

.. image:: images/facebook-6.png

Authorize Agoras
----------------

Once you have your app credentials, authorize Agoras to access your Facebook account::

    agoras facebook authorize \
      --client-id "${FACEBOOK_CLIENT_ID}" \
      --client-secret "${FACEBOOK_CLIENT_SECRET}" \
      --app-id "${FACEBOOK_APP_ID}" \
      --object-id "${FACEBOOK_OBJECT_ID}"

This will:

1. Open your browser to Facebook's OAuth authorization page
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization
4. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can use Facebook actions without providing tokens. Credentials are automatically refreshed when needed.

CI/CD Setup (Unattended Execution)
-----------------------------------

For CI/CD environments where interactive browser authorization isn't possible, you can skip the ``authorize`` step entirely and provide all required credentials via environment variables.

1. Run ``agoras facebook authorize`` locally first to generate a refresh token (one-time setup)
2. Extract the refresh token using the tokens utility command::

      # First, list tokens to find the identifier (if you don't know it)
      agoras utils tokens list --platform facebook

      # Then view all stored credentials
      agoras utils tokens show --platform facebook --identifier {identifier}

3. Set all required environment variables in your CI/CD pipeline::

      export FACEBOOK_OBJECT_ID="your_object_id"
      export FACEBOOK_CLIENT_ID="your_client_id"
      export FACEBOOK_CLIENT_SECRET="your_client_secret"
      export FACEBOOK_REFRESH_TOKEN="your_refresh_token_here"

4. Run Agoras actions directly without running ``authorize``. All credentials will be loaded from environment variables.

**Note**: For unattended execution, you must provide all required credentials. The refresh token alone is not sufficient - you also need client ID, client secret, and object ID as shown in the :doc:`../reference/platform-arguments-envvars` documentation.

Agoras parameters
~~~~~~~~~~~~~~~~~

+------------------------------+--------------------------+
| Facebook credential          | Agoras parameter         |
+==============================+==========================+
| Client ID (App ID)           | --client-id              |
+------------------------------+--------------------------+
| Client Secret (App Secret)   | --client-secret          |
+------------------------------+--------------------------+
| App ID                       | --app-id                 |
+------------------------------+--------------------------+
| Object ID (User/Page ID)     | --object-id              |
+------------------------------+--------------------------+
