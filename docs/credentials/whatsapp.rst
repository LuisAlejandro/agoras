WhatsApp credentials
====================

Agoras needs the following information from WhatsApp Business API to be able to access its API:

- Meta Graph API Access Token
- WhatsApp Business Phone Number ID
- Target Recipient Phone Number (E.164 format)
- Business Account ID (optional)

For that, we'll need to create a Meta Developer Account, set up a WhatsApp Business Account, and obtain the necessary credentials from Meta Business Manager.

**Important**: WhatsApp Business API requires business verification for production use. For development and testing, you can use test phone numbers and temporary access tokens. Make sure your WhatsApp Business Account has the necessary permissions for the actions you want to perform.

---

Meta Developer Account Setup
----------------------------

WhatsApp Business API is part of Meta's platform, so you'll need a Meta Developer Account (shared with Facebook and Instagram).

1. Go to `Meta for Developers <https://developers.facebook.com/>`_
2. Click **"Get Started"** or **"My Apps"** if you already have an account
3. Create a new app or select an existing app
4. Add the **WhatsApp** product to your app

**Note**: If you already have a Meta Developer Account for Facebook or Instagram, you can use the same account and add WhatsApp to an existing app.

Create a Meta App
~~~~~~~~~~~~~~~~~

1. In Meta for Developers, click **"Create App"**
2. Select **"Business"** as the app type
3. Fill in your app details:
   - App name
   - App contact email
   - Business account (if applicable)
4. Click **"Create App"**

Add WhatsApp Product
~~~~~~~~~~~~~~~~~~~~~

1. In your app dashboard, find **"Add Product"** or go to **"Products"**
2. Find **"WhatsApp"** and click **"Set Up"**
3. Follow the setup wizard to configure WhatsApp Business API

WhatsApp Business Account Setup
--------------------------------

After adding WhatsApp to your app, you need to set up a WhatsApp Business Account.

1. In your app dashboard, go to **"WhatsApp"** > **"Getting Started"**
2. Click **"Create Business Account"** or link an existing WhatsApp Business Account
3. Complete the business account setup:
   - Business name
   - Business category
   - Business description
   - Contact information

**Important**: For production use, you'll need to complete business verification. This process can take several days and requires business documentation.

Phone Number Registration
--------------------------

You need to register a phone number with your WhatsApp Business Account.

1. In your app dashboard, go to **"WhatsApp"** > **"Phone Numbers"**
2. Click **"Add Phone Number"**
3. Select your country and enter your phone number
4. Choose verification method (SMS or Voice call)
5. Enter the verification code you receive
6. Complete the phone number setup

**Development Mode**: For testing, you can use test phone numbers provided by Meta. These don't require phone number verification but have limitations.

Get Phone Number ID
~~~~~~~~~~~~~~~~~~~~

After registering your phone number:

1. Go to **"WhatsApp"** > **"Phone Numbers"** in your app dashboard
2. Click on your phone number
3. Find the **"Phone number ID"** (it's a long numeric ID)
4. Copy this ID - you'll need it for Agoras

**Example**: Phone number ID looks like: ``123456789012345``

Access Token Generation
------------------------

WhatsApp Business API uses Meta Graph API access tokens. You can generate temporary tokens for development or permanent tokens for production.

Generate Temporary Access Token (Development)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. In your app dashboard, go to **"WhatsApp"** > **"API Setup"**
2. Find the **"Temporary access token"** section
3. Click **"Generate Token"**
4. Copy the token - it expires in 24 hours

**Note**: Temporary tokens are for development and testing only. They have limited rate limits and expire quickly.

Generate Permanent Access Token (Production)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For production use, you need a permanent access token:

1. Go to **"WhatsApp"** > **"API Setup"** in your app dashboard
2. Scroll to **"Permanent access token"** section
3. Click **"Generate Token"**
4. Select the appropriate permissions/scopes:
   - ``whatsapp_business_messaging``
   - ``whatsapp_business_management``
5. Copy the token - this token doesn't expire (unless revoked)

**Important**: Store permanent tokens securely. They provide full access to your WhatsApp Business Account.

Token Permissions and Scopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WhatsApp Business API requires the following permissions:

- **whatsapp_business_messaging**: Send and receive messages
- **whatsapp_business_management**: Manage business profile and settings

Make sure your access token has these permissions when generating it.

Token Management
~~~~~~~~~~~~~~~~~

- **Token Expiration**: Temporary tokens expire in 24 hours. Permanent tokens don't expire unless revoked.
- **Token Refresh**: For temporary tokens, generate a new token before expiration. Permanent tokens don't need refresh.
- **Token Revocation**: You can revoke tokens in Meta Business Manager if compromised.
- **Security**: Never share your access tokens publicly. Store them in environment variables or secure secret managers.

Business Account ID (Optional)
--------------------------------

The Business Account ID is optional but may be required for some operations.

Find Business Account ID
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to `Meta Business Manager <https://business.facebook.com/>`_
2. Select your business account
3. Go to **"Business Settings"** > **"Business Info"**
4. Find the **"Business ID"** - this is your Business Account ID

**Note**: The Business Account ID is different from the Phone Number ID. You typically only need the Phone Number ID for basic messaging operations.

When It's Required
~~~~~~~~~~~~~~~~~~~

- Business profile management
- Advanced analytics
- Multi-phone number management
- Some enterprise features

For basic message sending, the Business Account ID is usually not required.

Recipient Phone Number
-----------------------

WhatsApp Business API sends messages to individual recipients. You need to specify the recipient phone number in E.164 format.

E.164 Format Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~

Phone numbers must be in E.164 international format:

- Start with a **+** sign
- Followed by country code (1-3 digits)
- Followed by the phone number (without leading zeros)

**Examples**:
- US: ``+1234567890``
- UK: ``+441234567890``
- Mexico: ``+521234567890``

Test Phone Numbers (Development)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For development and testing, you can use test phone numbers:

1. In your app dashboard, go to **"WhatsApp"** > **"API Setup"**
2. Find **"To"** field in the test section
3. Add test phone numbers (numbers you want to send test messages to)
4. These numbers must be verified in your Meta account

**Note**: Test phone numbers have limitations:
- Can only send to verified test numbers
- Limited rate limits
- Messages are marked as test messages

Production Recipient Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

For production:

1. Recipients must opt-in to receive messages from your business
2. You can only send to numbers that have initiated contact with you (for 24-hour window)
3. For messages outside the 24-hour window, you must use approved message templates
4. Recipients can opt-out at any time

Recipient Verification
~~~~~~~~~~~~~~~~~~~~~~~

Before sending messages to production recipients:

1. Ensure recipients have opted in to receive messages
2. Verify recipient phone numbers are in E.164 format
3. Test with a small group before sending to all recipients
4. Monitor delivery rates and recipient feedback

Rate Limiting and Compliance
------------------------------

WhatsApp Business API has rate limits to prevent abuse and ensure quality.

Free Tier Limits
~~~~~~~~~~~~~~~~~

- **1,000 messages per day** (free tier)
- Rate limits apply per recipient
- Limits reset daily

**Note**: These limits are for unverified businesses. Business verification increases limits significantly.

Business Verification Benefits
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After business verification:

- Higher message limits (varies by business tier)
- Access to advanced features
- Better delivery rates
- Priority support

Compliance Guidelines
~~~~~~~~~~~~~~~~~~~~~

- **WhatsApp Business Policy**: Follow Meta's WhatsApp Business Policy
- **Message Templates**: Pre-approved templates required for notifications
- **Opt-in Requirements**: Recipients must opt-in to receive messages
- **Data Privacy**: Comply with GDPR and local data protection laws
- **Content Guidelines**: Follow WhatsApp's content and spam policies

Best Practices
~~~~~~~~~~~~~~

- Start with test phone numbers during development
- Monitor rate limits and plan message sending accordingly
- Use message templates for notifications
- Respect recipient opt-outs immediately
- Keep access tokens secure and rotate them periodically
- Monitor delivery rates and adjust messaging strategy

Troubleshooting
---------------

Common Setup Issues
~~~~~~~~~~~~~~~~~~~

**Issue**: "Invalid access token"
- **Solution**: Generate a new access token. Temporary tokens expire in 24 hours.

**Issue**: "Phone number not verified"
- **Solution**: Complete phone number verification in Meta Business Manager.

**Issue**: "Invalid phone number ID"
- **Solution**: Verify you're using the correct Phone Number ID from your app dashboard.

**Issue**: "Recipient phone number invalid"
- **Solution**: Ensure phone number is in E.164 format (starts with +, includes country code).

Token Expiration Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Temporary tokens**: Generate new token before expiration (every 24 hours)
- **Permanent tokens**: Should not expire unless revoked
- **Token refresh**: Not supported for WhatsApp (unlike OAuth refresh tokens)
- **Error handling**: Agoras will show clear error messages if token is invalid

Phone Number Verification Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **SMS not received**: Try voice call verification instead
- **Verification code expired**: Request a new verification code
- **Wrong phone number**: Ensure you're using the correct number format
- **Already verified**: Check if number is already linked to another account

Business Verification Delays
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Processing time**: Business verification can take 3-7 business days
- **Documentation**: Ensure all required documents are submitted
- **Status check**: Monitor verification status in Meta Business Manager
- **Support**: Contact Meta support if verification is delayed beyond expected time

Test your setup
---------------

You can test if your WhatsApp Business API is properly configured:

1. Make sure you have your access token and phone number ID
2. First, authorize your WhatsApp credentials:

   ::

         agoras whatsapp authorize \
               --access-token "your_access_token_here" \
               --phone-number-id "your_phone_number_id_here"

3. Then send a test message (credentials are now stored):

   ::

         agoras whatsapp post \
               --recipient "+1234567890" \
               --text "Hello from Agoras!"

4. Check if the message appears in WhatsApp

CI/CD Setup (Unattended Execution)
-----------------------------------

For CI/CD environments where interactive authorization isn't possible, you can skip the ``authorize`` step entirely and provide all required credentials via environment variables.

1. Run ``agoras whatsapp authorize`` locally first to store credentials (optional, for local development)
2. Extract stored credentials using the tokens utility command (if you need to retrieve them)::

      # First, list tokens to find the identifier (phone_number_id)
      agoras utils tokens list --platform whatsapp

      # Then view all stored credentials
      agoras utils tokens show --platform whatsapp --identifier {identifier}

3. For CI/CD, set all required environment variables in your CI/CD pipeline::

      export WHATSAPP_ACCESS_TOKEN="your_access_token_here"
      export WHATSAPP_PHONE_NUMBER_ID="your_phone_number_id_here"
      export WHATSAPP_BUSINESS_ACCOUNT_ID="your_business_account_id_here"  # Optional
      export WHATSAPP_RECIPIENT="+1234567890"  # Required for all messaging actions

4. Run Agoras actions directly without running ``authorize``. All credentials will be loaded from environment variables.

**Note**: For unattended execution, you must provide all required credentials (access token, phone number ID, and recipient) as shown in the :doc:`../reference/platform-arguments-envvars` documentation. The recipient phone number must be provided with each messaging action as it varies per message.

Agoras parameters
-----------------

+------------------------+---------------------------+--------------------------------+
| WhatsApp credential    | Agoras parameter          | Required for                   |
+========================+===========================+================================+
| Access Token           | --access-token            | authorize (required)           |
|                        |                           | post/video/etc (optional)      |
+------------------------+---------------------------+--------------------------------+
| Phone Number ID        | --phone-number-id         | authorize (required)           |
|                        |                           | post/video/etc (optional)      |
+------------------------+---------------------------+--------------------------------+
| Business Account ID    | --business-account-id     | authorize (optional)           |
+------------------------+---------------------------+--------------------------------+
| Recipient Number       | --recipient               | All messaging actions          |
+------------------------+---------------------------+--------------------------------+

**Important**: Run ``agoras whatsapp authorize`` first to store your credentials securely. After authorization, you can use post, video, and template actions without providing access token and phone number ID each time.

**Note**: The recipient phone number must be provided with each message action as it varies per message. It is not stored during authorization.

Security Best Practices
-----------------------

- **Never commit tokens to version control**: Use `.gitignore` for credential files
- **Use environment variables**: Store credentials in environment variables, not in code
- **Rotate tokens periodically**: Generate new tokens and revoke old ones
- **Use secrets managers**: For production, use AWS Secrets Manager, HashiCorp Vault, etc.
- **Limit token permissions**: Only grant necessary permissions
- **Monitor token usage**: Regularly check for unauthorized access
- **Revoke compromised tokens**: Immediately revoke any tokens that may be compromised

Additional Resources
--------------------

- `WhatsApp Business API Documentation <https://developers.facebook.com/docs/whatsapp>`_
- `Meta for Developers <https://developers.facebook.com/>`_
- `WhatsApp Business Policy <https://www.whatsapp.com/legal/business-policy>`_
- `Graph API Reference <https://developers.facebook.com/docs/graph-api>`_
