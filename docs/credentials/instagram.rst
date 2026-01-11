Instagram credentials
=====================

.. versionchanged:: 1.6
   Instagram now uses OAuth 2.0 authentication via Facebook Graph API. You no longer need to manually generate access tokens.

Agoras needs the following OAuth app credentials to access the Instagram Graph API:

- Client ID (Facebook App ID)
- Client Secret (Facebook App Secret)
- Object ID (Facebook User ID for Instagram business account)

Instagram uses Facebook OAuth, so you'll need a Facebook App. You also need to connect a Facebook page with the Instagram account that you wish to use.

Connect Facebook Page to Instagram Account
------------------------------------------

On Facebook, switch to the profile of the page that's going to manage the Instagram account, then click **Settings & privacy** > **Settings** > **Linked Accounts** and then click **Connect**.

.. image:: images/instagram-1.png

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
-------------------

1. In your Facebook App dashboard, go to **Settings** > **Basic**.
2. Note your **App ID** (this is your ``--client-id``).
3. Note your **App Secret** (click "Show" to reveal it - this is your ``--client-secret``).

Get Object ID (Facebook User ID)
--------------------------------

You need the Facebook user ID that has access to the Instagram business account. To find it:

1. Use the Graph API Explorer with a valid access token::

      https://developers.facebook.com/tools/explorer/?method=GET&path=me

2. The response will show your user ID::

      {
            "name": "Your Name",
            "id": "XXXXX"
      }

The ``id`` field is your ``--object-id``.

Alternatively, if you know the Facebook page ID linked to your Instagram account, you can get the user ID from the page's accounts endpoint.

Authorize Agoras
----------------

Once you have your app credentials, authorize Agoras to access your Instagram account::

    agoras instagram authorize \
      --client-id "${INSTAGRAM_CLIENT_ID}" \
      --client-secret "${INSTAGRAM_CLIENT_SECRET}" \
      --object-id "${INSTAGRAM_OBJECT_ID}"

This will:

1. Open your browser to Facebook's OAuth authorization page (Instagram uses Facebook OAuth)
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization
4. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can use Instagram actions without providing tokens. Credentials are automatically refreshed when needed.

CI/CD Setup (Headless Authorization)
-------------------------------------

For CI/CD environments where interactive browser authorization isn't possible:

1. Run ``agoras instagram authorize`` locally first to generate a refresh token.
2. Extract the refresh token from ``~/.agoras/tokens/instagram-{object_id}.token`` (decrypted).
3. Set environment variables in your CI/CD pipeline::

      export AGORAS_INSTAGRAM_REFRESH_TOKEN="your_refresh_token_here"
      export AGORAS_INSTAGRAM_HEADLESS=1

4. Agoras will automatically use the refresh token from the environment variable.

Agoras parameters
~~~~~~~~~~~~~~~~~

+------------------------------+--------------------------+
| Instagram credential         | Agoras parameter         |
+==============================+==========================+
| Client ID (Facebook App ID)  | --client-id              |
+------------------------------+--------------------------+
| Client Secret (App Secret)   | --client-secret          |
+------------------------------+--------------------------+
| Object ID (Facebook User ID)  | --object-id              |
+------------------------------+--------------------------+
