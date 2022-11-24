Twitter credentials
===================

Agoras needs the following credentials from twitter to be able to access its API.

- API key
- API secret key
- Access token
- Access token secret

For that, we'll need to create a Twitter App.

Create a twitter app
~~~~~~~~~~~~~~~~~~~~

You can create a twitter app for your twitter account at https://developer.twitter.com/en/apps.

.. image:: images/twitter-1.png

If you haven't yet, you will be asked to apply for a Twitter developer account. See my answers below for reference. If you've done that before, skip the next section and continue at `Create an app <create-an-app_>`_.

Apply for a developer account
-----------------------------

.. image:: images/twitter-2.png
.. _email settings: https://twitter.com/settings/email

You might be asked to add a phone number to your twitter account before proceeding. If the phone number is used in another account, it won't let you use it again. But you can remove the phone number from the other account. You can change it back once your developer account was approved.

Your twitter account will also need to be associated with an email address. If it isn't yet, set the email address in your twitter account `email settings`_.

.. image:: images/twitter-3.png

Answer the following questions:

- What country are you based in?

Just put the country where you live in. Be aware that if you live in a US-sanctioned country you might be subject to rejections or limitations to your account.

- What's your use case?

Select Building customized solutions in-house or Making a bot.

- Will you make Twitter content or derived information available to a government entity or a government affiliated enitity?

Answer no.

.. image:: images/twitter-4.png

Now accept the terms and conditions.

What to do if you dont qualify
------------------------------

.. image:: images/twitter-5.png

If you dont qualify for a developer account, you'll be asked to fill a more detailed application to request "Elevated access" to APIs. It consists of 4 pages, the first asking some basic information about you.

.. image:: images/twitter-6.png

### Describe in your own words what you are building

1. In your words

This app will be used to publish tweets using the [twitter-together](https://github.com/gr2m/twitter-together/) GitHub Action. It allows to use a GitHub repository and pull request reviews as a workflow to collaboratively tweet from a shared twitter account.

2. Are you planning to analyze Twitter data?

No

3. Will your app use Tweet, Retweet, like, follow, or Direct Message functionality?

Yes. This app will be used to publish tweets for this account. It might be used for retweeting in future. There are no plans for liking.

4. Do you plan to display Tweets or aggregate data about Twitter content outside of Twitter?

No twitter data will be displayed. The `twitter-together` GitHub action shows a preview of the tweet before it is published and becomes twitter data.

5. Will your product, service, or analysis make Twitter content or derived information available to a government entity?

No

---

You will receive an email to verify your developer account. After that you can create an app at https://developer.twitter.com/en/portal/apps/new.

.. _create-an-app:

## Create an app

.. image:: twitter-03-create-app.png

Only 4 questions are required. Here are my answers for reference

### App name (required)

`<your twitter account name>-twitter-together`, e.g. `probot-twitter-together`

### Application description (required)

Collaboratively tweet using GitHub’s pull request review process by utilizing the twitter-together GitHub Action.

### Website URL (required)

https://github.com/gr2m/twitter-together

### Tell us how this app will be used (required)

This app will be used to create tweets that have previously been reviewed and accepted on our GitHub repository. It allows everyone to submit a tweet draft that we can discuss prior publishing.

## Save credentials

"read and write" permissions are required. When you have created your app, open `app settings` and set app permissions to "Read & Write". If you change the permission you must re-generate tokens for the change to take effect.

Open your app’s "Keys and tokens" tab. In the "Access token & access token secret" section, press the "Create" button. After that you will see all four credentials required for `twitter-together`.

.. image:: twitter-04-keys-and-tokens.png

Now save the credentials into your repository’s "Secrets" settings as follows

| Twitter Credential name | GitHub Secret name            |
| ----------------------- | ----------------------------- |
| API key                 | `TWITTER_API_KEY`             |
| API secret key          | `TWITTER_API_SECRET_KEY`      |
| Access token            | `TWITTER_ACCESS_TOKEN`        |
| Access token secret     | `TWITTER_ACCESS_TOKEN_SECRET` |

.. image:: twitter-05-repository-secrets.png

---

next: [Create a `.github/workflows/twitter-together.yml` file](02-create-twitter-together-workflow.md)