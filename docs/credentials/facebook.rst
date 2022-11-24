Facebook credentials
===================


👥 How to get a Facebook permanent access token
-----------------------------------------------

.. _extending page tokens documentation: https://developers.facebook.com/docs/facebook-login/access-tokens#extendingpagetokens
.. _Graph API Explorer: https://developers.facebook.com/tools/explorer

Following the instructions laid out in Facebook's `extending page tokens documentation`_ I was able to get a page access token that does not expire.

I suggest using the `Graph API Explorer`_ for all of these steps except where otherwise stated.

0. Create Facebook App
-----------------------------------

.. _My Apps: https://developers.facebook.com/apps/

**If you already have an app**, skip to step 1.

1. Go to `My Apps`_.
2. Click "+ Add a New App".
3. Setup a website app.

You don't need to change its permissions or anything. You just need an app that wont go away before you're done with your access token.

1. Get User Short-Lived Access Token
-----------------------------------

.. _Graph API Explorer: https://developers.facebook.com/tools/explorer

1. Go to the `Graph API Explorer`_.
2. Select the application you want to get the access token for (in the "Facebook App" drop-down menu, not the "My Apps" menu).
3. In the "Add a Permission" drop-down, search and check "pages_manage_posts" and "pages_read_engagement".
4. Click "Generate Access Token".
5. Grant access from a Facebook account that has access to manage the target page. Note that if this user loses access the final, never-expiring access token will likely stop working.

The token that appears in the "Access Token" field is your short-lived access token.

2. Generate Long-Lived Access Token
-----------------------------------

.. _these instructions: https://developers.facebook.com/docs/facebook-login/access-tokens#extending
.. _Access Token Debugger: https://developers.facebook.com/tools/debug/accesstoken

Following `these instructions`_ from the Facebook docs, make a GET request to

> https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_lived_token}

entering in your app's ID and secret and the short-lived token generated in the previous step.

You **cannot use the Graph API Explorer**. For some reason it gets stuck on this request. I think it's because the response isn't JSON, but a query string. Since it's a GET request, you can just go to the URL in your browser.

The response should look like this::

      {"access_token":"**ABC123**","token_type":"bearer","expires_in":5183791}

"ABC123" will be your long-lived access token. You can put it into the `Access Token Debugger`_ to verify. Under "Expires" it should have something like "2 months".

3. Get User ID
-----------------------------------

Using the long-lived access token, make a GET request to::

      https://graph.facebook.com/me?access_token={long_lived_access_token}

The `id` field is your account ID. You'll need it for the next step.

4. Get Permanent Page Access Token
-----------------------------------

.. _Access Token Debugger: https://developers.facebook.com/tools/debug/accesstoken

Make a GET request to::

      https://graph.facebook.com/{account_id}/accounts?access_token={long_lived_access_token}

The JSON response should have a `data` field under which is an array of items the user has access to. Find the item for the page you want the permanent access token from. The `access_token` field should have your permanent access token. Copy it and test it in the `Access Token Debugger`_. Under "Expires" it should say "Never".

👥 How to get a Facebook page ID
-----------------------------------------------

To find your Page ID:

1. From News Feed, click Pages in the left side menu.
2. Click your Page name to go to your Page.
3. Click About in the left column. If you don't see About in the left column, click See More.
4. Scroll down to find your Page ID below More Info.
