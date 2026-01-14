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
3. Use the Graph API Explorer to get the ID::

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

CI/CD Setup (Headless Authorization)
------------------------------------

For CI/CD environments where interactive browser authorization isn't possible:

1. Run ``agoras facebook authorize`` locally first to generate a refresh token.
2. Extract the refresh token from ``~/.agoras/tokens/facebook-{object_id}.token`` (decrypted).
3. Set environment variables in your CI/CD pipeline::

      export AGORAS_FACEBOOK_REFRESH_TOKEN="your_refresh_token_here"
      export AGORAS_FACEBOOK_HEADLESS=1

4. Agoras will automatically use the refresh token from the environment variable.

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
