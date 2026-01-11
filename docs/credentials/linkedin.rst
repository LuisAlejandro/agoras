LinkedIn credentials
====================

.. versionchanged:: 1.6
   LinkedIn now uses OAuth 2.0 authentication. You no longer need to manually generate access tokens.

Agoras needs the following OAuth app credentials from LinkedIn to access its API:

- Client ID
- Client Secret
- Object ID (User/Organization ID)

Create a LinkedIn App
---------------------

1. Sign in to the `LinkedIn developer portal <https://www.linkedin.com/developers/apps>`_.

.. image:: images/linkedin-1.png

2. Click "Create app" to create a new app.

3. Enter basic details such as the app's name and logo.

.. image:: images/linkedin-2.png

4. You will need to associate your app with a LinkedIn page. If you don't have any pages, `create one <https://www.linkedin.com/company/setup/new/>`_.

5. Request App Verification From the Company Page: go to the Settings tab and press the "Verify" button to receive a verification link. Open this link and confirm responsibility for the app.

.. image:: images/linkedin-3.png

.. image:: images/linkedin-4.png

Request Access to Products
--------------------------

1. Go to Products tab, and request access to "Share on LinkedIn" and "Sign In with LinkedIn using OpenID Connect".

.. image:: images/linkedin-5.png

2. Once approved (usually instantly), go to the **Auth** tab in your app settings to find your **Client ID** and **Client Secret**.

Get App Credentials
-------------------

1. In your LinkedIn App dashboard, go to the **Auth** tab.
2. Note your **Client ID** (this is your ``--client-id``).
3. Note your **Client Secret** (this is your ``--client-secret``).

Get Object ID (User/Organization ID)
-------------------------------------

You need the LinkedIn user or organization ID you want to post as. To find it:

1. Go to your LinkedIn profile or company page.
2. The ID can be found in the URL or by using the LinkedIn API.
3. For organizations, you can find it in the company page settings.

Alternatively, after authorizing, Agoras will automatically detect and use the correct ID.

Authorize Agoras
----------------

Once you have your app credentials, authorize Agoras to access your LinkedIn account::

    agoras linkedin authorize \
      --client-id "${LINKEDIN_CLIENT_ID}" \
      --client-secret "${LINKEDIN_CLIENT_SECRET}" \
      --object-id "${LINKEDIN_OBJECT_ID}"

This will:

1. Open your browser to LinkedIn's OAuth authorization page
2. Prompt you to grant permissions to Agoras
3. Automatically capture the authorization
4. Store encrypted credentials in ``~/.agoras/tokens/``

After authorization, you can use LinkedIn actions without providing tokens. Credentials are automatically refreshed when needed.

CI/CD Setup (Headless Authorization)
------------------------------------

For CI/CD environments where interactive browser authorization isn't possible:

1. Run ``agoras linkedin authorize`` locally first to generate a refresh token.
2. Extract the refresh token from ``~/.agoras/tokens/linkedin-{object_id}.token`` (decrypted).
3. Set environment variables in your CI/CD pipeline::

      export AGORAS_LINKEDIN_REFRESH_TOKEN="your_refresh_token_here"
      export AGORAS_LINKEDIN_HEADLESS=1

4. Agoras will automatically use the refresh token from the environment variable.

Agoras parameters
~~~~~~~~~~~~~~~~~

+------------------------------+--------------------------+
| LinkedIn credential          | Agoras parameter         |
+==============================+==========================+
| Client ID                    | --client-id              |
+------------------------------+--------------------------+
| Client Secret                | --client-secret          |
+------------------------------+--------------------------+
| Object ID (User/Org ID)      | --object-id              |
+------------------------------+--------------------------+
